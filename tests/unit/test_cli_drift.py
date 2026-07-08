# tests/unit/test_cli_drift.py
import pytest

from retail.cli import main

pytestmark = pytest.mark.unit


def test_drift_without_dsn_is_deferred(capsys):
    rc = main(["drift", "--baseline", "mappings/retail_store_sales/source-profile.md"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "PENDING LIVE RE-PROFILE" in err or "deferred" in err.lower()


def test_drift_nonconformant_baseline_reports_uncomparable(capsys):
    rc = main(["drift", "--baseline", "mappings/demo_sample_orders/source-profile.md"])
    out = capsys.readouterr()
    assert rc == 1
    assert (
        "uncomparable" in (out.out + out.err).lower()
        or "non-conformant" in (out.out + out.err).lower()
    )


_CONFORMANT = "mappings/retail_store_sales/source-profile.md"


def test_drift_live_missing_driver_is_actionable(capsys, monkeypatch):
    # --dsn given but the optional DB driver is absent: gate like validate does
    # -- an actionable "pip install 'retail[db]'" message + rc 1, never a raw
    # ModuleNotFoundError traceback.
    from retail import cli

    monkeypatch.setattr(cli, "_ensure_driver", lambda: False)
    rc = main(["drift", "--baseline", _CONFORMANT, "--dsn", "postgresql://x@h/db"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "retail[db]" in err


def test_drift_live_db_error_is_scrubbed_not_leaked(capsys, monkeypatch):
    # A DB-boundary failure must NOT leak the DSN (user/host/password) verbatim.
    # Mirror validate.py: the exception is caught and run through the dialect
    # redactor before printing. The DSN embeds a password that must not appear.
    from retail import cli

    secret = "postgresql://admin:s3cr3t_pw@db.internal:5432/prod"

    monkeypatch.setattr(cli, "_ensure_driver", lambda: True)

    def _boom(config):
        raise RuntimeError(f"connection failed for {config}")

    monkeypatch.setattr(cli, "_make_runner", _boom)
    rc = main(["drift", "--baseline", _CONFORMANT, "--dsn", secret])
    out = capsys.readouterr()
    combined = out.out + out.err
    assert rc == 1
    assert "s3cr3t_pw" not in combined
    assert "connection failed" not in combined or "s3cr3t_pw" not in combined
