"""US3 tests: 'not_applicable_with_reason' truthful degradation (spec 131,
T025, FR-015).

No shipped producer for a scope, or no evidence produced yet -> a named
reason, never counted as covered/clean.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat import portfolio_watch as pw
from tests.fixtures.portfolio_watch.builders import write_readiness_status

pytestmark = pytest.mark.unit


def test_no_baseline_source_profile_is_not_applicable(tmp_path: Path) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")
    # No source-profile.md and no drift-findings.json at all.

    summary = pw.build_portfolio_watch_summary(tmp_path)
    finding = next(
        d
        for d in summary["scopes"][0]["dimensions"]
        if d["dimension"] == "source_drift"
    )

    assert finding["state"] == pw.STATE_NOT_APPLICABLE
    assert finding["measured"]
    assert finding["class"] is None


@pytest.mark.parametrize(
    "dimension",
    ["contract_metric_drift", "dashboard_intent_divergence", "review"],
)
def test_no_evidence_produced_yet_is_not_applicable(
    tmp_path: Path, dimension: str
) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")

    summary = pw.build_portfolio_watch_summary(tmp_path)
    finding = next(
        d for d in summary["scopes"][0]["dimensions"] if d["dimension"] == dimension
    )

    assert finding["state"] == pw.STATE_NOT_APPLICABLE
    assert finding["state"] != pw.STATE_COVERED


def test_not_applicable_scopes_are_listed_in_scopes_with_no_evidence(
    tmp_path: Path,
) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")

    summary = pw.build_portfolio_watch_summary(tmp_path)

    assert "scope_alpha" in summary["portfolio"]["scopes_with_no_evidence"]
