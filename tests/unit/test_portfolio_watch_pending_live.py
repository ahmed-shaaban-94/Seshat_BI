"""US3 tests: [PENDING LIVE] truthful degradation (spec 131, T023, FR-013).

A dimension whose evidence needs a live re-profile with no DSN configured ->
``[PENDING LIVE]``, never a fabricated comparison, consistent with
``docs/readiness/source-drift.md``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat import portfolio_watch as pw
from tests.fixtures.portfolio_watch.builders import (
    drift_artifact,
    write_json_artifact,
    write_readiness_status,
    write_source_profile,
)

pytestmark = pytest.mark.unit


def _dim(summary: dict, dimension: str) -> dict:
    return next(
        d for d in summary["scopes"][0]["dimensions"] if d["dimension"] == dimension
    )


def test_baseline_recorded_but_no_reprofile_yet_is_pending_live(tmp_path: Path) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")
    write_source_profile(tmp_path, "scope_alpha")
    # Deliberately no drift-findings.json artifact.

    summary = pw.build_portfolio_watch_summary(tmp_path)

    assert _dim(summary, "source_drift")["state"] == pw.STATE_PENDING_LIVE


def test_artifact_declaring_the_live_leg_unavailable_is_pending_live(
    tmp_path: Path,
) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")
    write_source_profile(tmp_path, "scope_alpha")
    write_json_artifact(
        tmp_path,
        "scope_alpha",
        "drift-findings.json",
        drift_artifact(live_leg_available=False),
    )

    summary = pw.build_portfolio_watch_summary(tmp_path)

    assert _dim(summary, "source_drift")["state"] == pw.STATE_PENDING_LIVE


def test_pending_live_is_never_upgraded_to_covered(tmp_path: Path) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")
    write_source_profile(tmp_path, "scope_alpha")

    summary = pw.build_portfolio_watch_summary(tmp_path)
    finding = _dim(summary, "source_drift")

    assert finding["state"] != pw.STATE_COVERED
    assert finding["class"] is None
