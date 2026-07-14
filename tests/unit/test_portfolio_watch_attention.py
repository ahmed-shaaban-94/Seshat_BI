"""US1 tests: requires_human_attention (spec 131, T010, FR-006).

A scope with an unmet/invalid approval OR a relayed Principle-V drift blocker
sets ``requires_human_attention=true`` and names an ``owner`` -- independently
of the scope's category rank (a buried PII blocker still sets it). A
fully-clean scope is NOT flagged and its next action is its own terminal/
next-stage action (US1 #4).
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


def test_missing_approval_sets_attention_and_names_owner(tmp_path: Path) -> None:
    write_readiness_status(
        tmp_path,
        "scope_alpha",
        current_stage="mapping_ready",
        stage_status={"source_ready": "pass", "mapping_ready": "blocked"},
        stage_blocking_reasons={"mapping_ready": ["mapping_ready approval is missing"]},
        top_blocking_reasons=["mapping_ready approval is missing"],
    )
    # Emulate approval_inbox seeing an unmet approval: a pass-with-no-approval
    # stage is what the shipped approval_inbox surfaces; simplest fixture here
    # is a stage recorded pass with no approvals[] entries.
    write_readiness_status(
        tmp_path,
        "scope_needs_approval",
        current_stage="mapping_ready",
        stage_status={"source_ready": "pass", "mapping_ready": "pass"},
    )

    summary = pw.build_portfolio_watch_summary(tmp_path)
    by_scope = {s["scope_id"]: s for s in summary["scopes"]}

    flagged = by_scope["scope_needs_approval"]
    assert flagged["requires_human_attention"] is True
    assert flagged["owner"]


def test_pii_drift_blocker_sets_attention_independent_of_rank(tmp_path: Path) -> None:
    """The shipped readiness_classify rank has NO pii bucket -- a pii_surface_
    drift item must still set requires_human_attention even though the
    scope's ranked category (e.g. 'artifact', the lowest bucket that matches)
    would otherwise bury it (spec 131 analysis.md C2)."""
    write_readiness_status(
        tmp_path,
        "scope_alpha",
        current_stage="source_ready",
        stage_status={"source_ready": "pass", "mapping_ready": "blocked"},
        stage_blocking_reasons={"mapping_ready": ["a required artifact is missing"]},
        top_blocking_reasons=["a required artifact is missing"],
    )
    write_source_profile(tmp_path, "scope_alpha")
    write_json_artifact(
        tmp_path,
        "scope_alpha",
        "drift-findings.json",
        drift_artifact(
            class_="pii_surface_drift",
            measured="1 finding",
            owner="governance",
            items=[
                {
                    "class": "pii_surface_drift",
                    "subject_locator": "customer_email",
                    "measured": "reappeared",
                    "owner": "governance",
                    "principle_v": True,
                }
            ],
        ),
    )

    summary = pw.build_portfolio_watch_summary(tmp_path)
    scope = summary["scopes"][0]

    # The ranked category is NOT approval/grain (no PII bucket exists there).
    assert scope["prioritized_next_action"]["category"] == "artifact"
    # Yet the attention flag fires anyway, independent of that rank.
    assert scope["requires_human_attention"] is True
    assert scope["owner"] == "governance"


def test_fully_clean_scope_is_not_flagged(tmp_path: Path) -> None:
    write_readiness_status(
        tmp_path,
        "scope_alpha",
        current_stage="publish_ready",
        stage_status={
            "source_ready": "pass",
            "mapping_ready": "pass",
            "silver_ready": "pass",
            "gold_ready": "pass",
            "semantic_model_ready": "pass",
            "dashboard_ready": "pass",
            "publish_ready": "pass",
        },
        approvals=[
            {"stage": "mapping_ready", "owner": "Test Owner (analyst)"},
            {"stage": "semantic_model_ready", "owner": "Test Owner (metric_owner)"},
            {"stage": "dashboard_ready", "owner": "Test Owner (governance)"},
            {"stage": "publish_ready", "owner": "Test Owner (data_owner)"},
        ],
    )

    summary = pw.build_portfolio_watch_summary(tmp_path)
    scope = summary["scopes"][0]

    assert scope["requires_human_attention"] is False
    assert scope["owner"] is None
    assert scope["prioritized_next_action"]["category"] == "readiness"
