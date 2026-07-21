"""CLI-level tests for `seshat profile` (#400).

The mechanical profiler is exercised in ``test_profile.py``; these tests cover
the CLI seam only -- flag parsing, config/driver resolution, the markdown/JSON
render, and the fail-closed messages -- with the DB seams monkeypatched so no
real database is touched (the same posture as ``test_cli_context.py``'s
validate tests).
"""

from __future__ import annotations

import json

import pytest

from seshat.cli import _build_parser
from seshat.cli import main as main_under_test

pytestmark = pytest.mark.unit


class _FakeRunner:
    """Scripts the FIFO query order of ``seshat.profile.profile``:

    discover columns -> row count -> per-column (missingness, distinct) -> PK.
    """

    def run(self, sql, params=()):
        if "information_schema" in sql:
            return [("a", "text"), ("amount", "numeric")]
        if sql.strip().lower().startswith("select count(*) from") and (
            "DISTINCT" not in sql
        ):
            return [(3,)]
        if "DISTINCT (a)" in sql or "DISTINCT (a, " in sql:
            # PK proof row: (total, distinct_pk, null_pk) -> unique, no nulls
            return [(3, 3, 0)]
        # per-column (missing, distinct)
        return [(0, 3)]


def _args_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h:5432/db")
    monkeypatch.setattr("seshat.cli._ensure_driver", lambda: True)
    monkeypatch.setattr("seshat.cli._make_runner", lambda dsn: _FakeRunner())


def test_parser_profile_flags() -> None:
    ns = _build_parser().parse_args(
        ["profile", "--table", "bronze.t", "--pk", "a,b", "--format", "json"]
    )
    assert ns.command == "profile"
    assert ns.table == "bronze.t"
    assert ns.pk == "a,b"
    assert ns.output_format == "json"


def test_profile_markdown_render(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _args_ok(monkeypatch)
    rc = main_under_test(["profile", "--table", "bronze.t", "--pk", "a"])
    out = capsys.readouterr().out
    assert rc == 0
    # The mechanical blocks the blank source-profile.md asks for:
    assert "## Shape" in out
    assert "## Per-column profile" in out
    assert "COUNT(DISTINCT pk)" in out
    assert "candidate PK holds" in out


def test_profile_json_render(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _args_ok(monkeypatch)
    rc = main_under_test(
        ["profile", "--table", "bronze.t", "--pk", "a", "--format", "json"]
    )
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert payload["table"] == "bronze.t"
    assert payload["row_count"] == 3
    assert payload["pk"]["is_unique"] is True
    assert [c["name"] for c in payload["columns"]] == ["a", "amount"]


def test_profile_no_creds_errors_clearly(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    for var in ("DATABASE_URL", "ANALYTICS_DB_HOST"):
        monkeypatch.delenv(var, raising=False)

    def _boom(dsn):  # pragma: no cover - must never be called without creds
        raise AssertionError("must not build a runner without creds")

    monkeypatch.setattr("seshat.cli._make_runner", _boom)
    rc = main_under_test(["profile", "--table", "bronze.t", "--pk", "a"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "no database connection" in err.lower()


def test_profile_empty_pk_is_refused(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _args_ok(monkeypatch)
    rc = main_under_test(["profile", "--table", "bronze.t", "--pk", " , "])
    err = capsys.readouterr().err
    assert rc == 1
    assert "--pk must name at least one column" in err


def test_profile_missing_driver_errors_clearly(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h:5432/db")
    monkeypatch.setattr("seshat.cli._ensure_driver", lambda: False)
    rc = main_under_test(["profile", "--table", "bronze.t", "--pk", "a"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "optional DB driver" in err
    assert "Traceback" not in err


def test_profile_db_boundary_error_is_clean(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h:5432/db")
    monkeypatch.setattr("seshat.cli._ensure_driver", lambda: True)

    class _Boom:
        def run(self, sql, params=()):
            raise RuntimeError("relation does not exist")

    monkeypatch.setattr("seshat.cli._make_runner", lambda dsn: _Boom())
    rc = main_under_test(["profile", "--table", "bronze.t", "--pk", "a"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "profiling failed at the DB boundary" in err
    assert "Traceback" not in err
