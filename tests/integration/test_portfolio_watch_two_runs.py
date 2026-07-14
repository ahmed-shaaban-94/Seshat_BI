"""Integration test: two runs, quickstart Steps 1-3 (spec 131, T022).

First run writes a baseline (0 ``new``). Between runs: resolve one blocker,
introduce a new one, leave one standing, and nudge a magnitude on the
standing one. Second run: the resolved condition is ``resolved``, the new one
is ``new``, the standing one is ``unchanged`` exactly once (duplicate
suppression, SC-005), and running the same state twice yields byte-identical
change labels (determinism, SC-006).
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

pytestmark = pytest.mark.integration


def _repo_state_one(root: Path) -> None:
    """Two standing conditions: one that will be resolved, one that stays."""
    write_readiness_status(
        root,
        "scope_alpha",
        current_stage="source_ready",
        stage_status={"source_ready": "pass"},
    )
    write_source_profile(root, "scope_alpha")
    write_json_artifact(
        root,
        "scope_alpha",
        "drift-findings.json",
        drift_artifact(
            class_="missingness_shift",
            items=[
                {
                    "class": "column_removed",
                    "subject_locator": "to_be_resolved",
                    "measured": "present -> absent",
                },
                {
                    "class": "missingness_shift",
                    "subject_locator": "standing_col",
                    "measured": "3.1% -> 11.7%",
                },
            ],
        ),
    )


def _repo_state_two(root: Path) -> None:
    """Resolve to_be_resolved, nudge standing_col's magnitude, add a new one."""
    write_json_artifact(
        root,
        "scope_alpha",
        "drift-findings.json",
        drift_artifact(
            class_="missingness_shift",
            items=[
                {
                    "class": "missingness_shift",
                    "subject_locator": "standing_col",
                    "measured": "3.1% -> 42.0%",
                },
                {
                    "class": "column_added",
                    "subject_locator": "brand_new_col",
                    "measured": "absent -> present",
                },
            ],
        ),
    )


def test_first_run_has_zero_new_and_writes_a_baseline(tmp_path: Path) -> None:
    _repo_state_one(tmp_path)

    first = pw.run_portfolio_watch(tmp_path)

    all_labels = [
        c["label"] for scope in first["scopes"] for c in scope["change_labels"]
    ]
    assert pw.LABEL_NEW not in all_labels
    assert all(label == pw.LABEL_NO_BASELINE for label in all_labels)
    assert (tmp_path / ".seshat" / "watch" / "snapshot.json").is_file()


def test_second_run_labels_new_resolved_unchanged_correctly(tmp_path: Path) -> None:
    _repo_state_one(tmp_path)
    pw.run_portfolio_watch(tmp_path)

    _repo_state_two(tmp_path)
    second = pw.run_portfolio_watch(tmp_path)

    scope = next(s for s in second["scopes"] if s["scope_id"] == "scope_alpha")
    by_locator = {c["subject_locator"]: c["label"] for c in scope["change_labels"]}

    assert by_locator["to_be_resolved"] == pw.LABEL_RESOLVED
    assert by_locator["brand_new_col"] == pw.LABEL_NEW
    assert by_locator["standing_col"] == pw.LABEL_UNCHANGED
    # Duplicate suppression: the standing condition appears exactly once.
    standing_entries = [
        c for c in scope["change_labels"] if c["subject_locator"] == "standing_col"
    ]
    assert len(standing_entries) == 1


def test_running_the_same_state_twice_is_byte_identical(tmp_path: Path) -> None:
    """SC-006: identical current evidence + identical prior snapshot yields
    identical labels. Isolated from run_portfolio_watch's own snapshot
    write (which would otherwise make the SECOND call's prior differ from the
    first call's prior) by fixing one prior snapshot and diffing the same
    current state against it twice."""
    _repo_state_one(tmp_path)
    pw.run_portfolio_watch(tmp_path)
    _repo_state_two(tmp_path)

    prior = pw.read_prior_snapshot(tmp_path)
    summary = pw.build_portfolio_watch_summary(tmp_path)
    current_keys = pw.condition_keys_from_summary(summary)
    current_scopes = frozenset(s["scope_id"] for s in summary["scopes"])

    run_a = pw.classify_changes(current_keys, current_scopes, prior)
    run_b = pw.classify_changes(current_keys, current_scopes, prior)

    assert run_a == run_b

    # And the summary itself (no snapshot/diff involved) is a deterministic
    # function of the same committed state.
    assert pw.build_portfolio_watch_summary(
        tmp_path
    ) == pw.build_portfolio_watch_summary(tmp_path)
