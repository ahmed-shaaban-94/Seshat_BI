"""`.env` loading for live DB connection resolution (issue #340).

`validate`/`drift`/`value-check` resolved the connection AND the engine from
`os.environ` only, so a user who put `ANALYTICS_DB_*` (incl.
`ANALYTICS_DB_ENGINE`) in the gitignored `.env` -- exactly as the error text,
`.env.example`, and README instruct -- got "no database connection configured"
or the wrong engine. `applied_dotenv(root)` is a context manager that fills the
process env from `root/.env` for the duration of the command body (so every
`os.environ` read -- engine selection, driver choice, config resolution -- sees
it), with real environment variables winning over `.env`, and restores
`os.environ` exactly on exit.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def test_applied_dotenv_fills_analytics_keys_within_the_block(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from seshat.connection_env import applied_dotenv

    monkeypatch.delenv("ANALYTICS_DB_HOST", raising=False)
    (tmp_path / ".env").write_text(
        "ANALYTICS_DB_HOST=db.example\nANALYTICS_DB_PASSWORD='s3cret'\n",
        encoding="utf-8",
    )

    with applied_dotenv(tmp_path):
        assert os.environ["ANALYTICS_DB_HOST"] == "db.example"
        assert os.environ["ANALYTICS_DB_PASSWORD"] == "s3cret"


def test_applied_dotenv_real_env_wins_over_dotenv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An explicitly exported variable overrides the .env value (the shell wins
    over the file)."""
    from seshat.connection_env import applied_dotenv

    monkeypatch.setenv("ANALYTICS_DB_HOST", "exported-wins")
    (tmp_path / ".env").write_text("ANALYTICS_DB_HOST=dotenv-loses\n", encoding="utf-8")

    with applied_dotenv(tmp_path):
        assert os.environ["ANALYTICS_DB_HOST"] == "exported-wins"


@pytest.mark.parametrize("raise_inside", [False, True])
def test_applied_dotenv_restores_environ_on_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, raise_inside: bool
) -> None:
    """os.environ is restored exactly on exit -- whether the block returns
    normally or raises (the mutation is scoped to the command body)."""
    from seshat.connection_env import applied_dotenv

    monkeypatch.delenv("ANALYTICS_DB_HOST", raising=False)
    (tmp_path / ".env").write_text("ANALYTICS_DB_HOST=db.example\n", encoding="utf-8")
    before = dict(os.environ)

    def _run() -> None:
        with applied_dotenv(tmp_path):
            if raise_inside:
                raise RuntimeError("boom")

    if raise_inside:
        with pytest.raises(RuntimeError):
            _run()
    else:
        _run()

    assert dict(os.environ) == before
    assert "ANALYTICS_DB_HOST" not in os.environ


def test_applied_dotenv_no_file_is_a_noop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from seshat.connection_env import applied_dotenv

    monkeypatch.setenv("ANALYTICS_DB_HOST", "only-from-process")
    assert not (tmp_path / ".env").exists()

    with applied_dotenv(tmp_path):
        assert os.environ["ANALYTICS_DB_HOST"] == "only-from-process"


def test_applied_dotenv_malformed_raises_environment_config_error(
    tmp_path: Path,
) -> None:
    """A malformed .env surfaces the governed EnvironmentConfigError so the CLI
    boundary can convert it to a clean exit-1 (no traceback)."""
    from seshat.connection_env import applied_dotenv
    from seshat.dbt.redaction import EnvironmentConfigError

    (tmp_path / ".env").write_text(
        "ANALYTICS_DB_HOST=a\nANALYTICS_DB_HOST=b\n", encoding="utf-8"
    )  # duplicate key

    with pytest.raises(EnvironmentConfigError):
        with applied_dotenv(tmp_path):
            pass


def test_engine_selected_from_dotenv_within_block(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`ANALYTICS_DB_ENGINE` in .env drives engine selection (P1): inside the
    block, `_current_engine` reads the .env value, not the postgres default."""
    from seshat import cli
    from seshat.connection_env import applied_dotenv

    monkeypatch.delenv("ANALYTICS_DB_ENGINE", raising=False)
    (tmp_path / ".env").write_text("ANALYTICS_DB_ENGINE=mysql\n", encoding="utf-8")

    assert cli._current_engine() == "postgres"  # default outside the block
    with applied_dotenv(tmp_path):
        assert cli._current_engine() == "mysql"  # .env-selected inside


def test_validate_resolves_dsn_from_dotenv_end_to_end(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The #340 repro: a populated .env (no exported vars) lets `resolve_dsn`
    build a DSN inside the block, instead of returning None."""
    from seshat.connection_env import applied_dotenv
    from seshat.validate import resolve_dsn

    for key in (
        "DATABASE_URL",
        "ANALYTICS_DB_HOST",
        "ANALYTICS_DB_NAME",
        "ANALYTICS_DB_USER",
    ):
        monkeypatch.delenv(key, raising=False)
    (tmp_path / ".env").write_text(
        "ANALYTICS_DB_HOST=db.example\n"
        "ANALYTICS_DB_NAME=warehouse\n"
        "ANALYTICS_DB_USER=reader\n",
        encoding="utf-8",
    )

    with applied_dotenv(tmp_path):
        dsn = resolve_dsn(dict(os.environ))

    assert dsn is not None
    assert "@db.example" in dsn and "/warehouse" in dsn
