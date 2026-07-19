"""`.env` loading for live DB connection resolution (issue #340).

`validate`/`drift`/`value-check` resolved the DB connection from
`dict(os.environ)` only, so a user who put `ANALYTICS_DB_*` in the gitignored
`.env` (exactly as the error text, `.env.example`, and README instruct) still
got "no database connection configured". `connection_environment` merges `.env`
into a COPY of the process env -- real environment variables win over `.env`,
and the process is never mutated.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def test_connection_environment_merges_dotenv_analytics_keys(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from seshat.connection_env import connection_environment

    monkeypatch.setenv("PATH", "keep-me")
    (tmp_path / ".env").write_text(
        "ANALYTICS_DB_HOST=db.example\n"
        "ANALYTICS_DB_NAME=warehouse\n"
        "ANALYTICS_DB_USER=reader\n"
        "ANALYTICS_DB_PASSWORD='s3cret'\n",
        encoding="utf-8",
    )

    env = connection_environment(tmp_path)

    assert env["ANALYTICS_DB_HOST"] == "db.example"
    assert env["ANALYTICS_DB_PASSWORD"] == "s3cret"
    assert env["PATH"] == "keep-me"  # process env preserved


def test_connection_environment_real_env_wins_over_dotenv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An explicitly exported variable overrides the .env value (least surprise:
    the shell wins over the file)."""
    from seshat.connection_env import connection_environment

    monkeypatch.setenv("ANALYTICS_DB_HOST", "exported-wins")
    (tmp_path / ".env").write_text("ANALYTICS_DB_HOST=dotenv-loses\n", encoding="utf-8")

    env = connection_environment(tmp_path)

    assert env["ANALYTICS_DB_HOST"] == "exported-wins"


def test_connection_environment_does_not_mutate_process_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from seshat.connection_env import connection_environment

    monkeypatch.setenv("PATH", "keep-me")
    (tmp_path / ".env").write_text("ANALYTICS_DB_HOST=db.example\n", encoding="utf-8")
    before = dict(os.environ)

    connection_environment(tmp_path)

    assert dict(os.environ) == before
    assert "ANALYTICS_DB_HOST" not in os.environ


def test_connection_environment_no_dotenv_returns_process_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from seshat.connection_env import connection_environment

    monkeypatch.setenv("ANALYTICS_DB_HOST", "only-from-process")
    assert not (tmp_path / ".env").exists()

    env = connection_environment(tmp_path)

    assert env["ANALYTICS_DB_HOST"] == "only-from-process"


def test_validate_resolves_dsn_from_dotenv_end_to_end(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The #340 repro: a populated .env (no exported vars) must let `resolve_dsn`
    build a DSN via `connection_environment`, instead of returning None."""
    from seshat.connection_env import connection_environment
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

    dsn = resolve_dsn(connection_environment(tmp_path))

    assert dsn is not None
    assert "@db.example" in dsn and "/warehouse" in dsn
