"""US2 tests: first run / unreadable prior snapshot (spec 131, T017).

No prior snapshot (and a corrupt/unreadable prior snapshot) -> every
condition ``current_condition_no_baseline``, explicitly NOT ``new``, with a
stated "no baseline available" note (FR-009, SNAP-3, the ``observed=None``
honesty).
"""

from __future__ import annotations

import json
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


def _build_repo_with_one_condition(root: Path) -> None:
    write_readiness_status(
        root,
        "scope_alpha",
        current_stage="mapping_ready",
        stage_status={"source_ready": "pass", "mapping_ready": "blocked"},
        stage_blocking_reasons={"mapping_ready": ["mapping_ready approval is missing"]},
        top_blocking_reasons=["mapping_ready approval is missing"],
    )
    write_source_profile(root, "scope_alpha")
    write_json_artifact(
        root,
        "scope_alpha",
        "drift-findings.json",
        drift_artifact(
            class_="column_added",
            items=[{"class": "column_added", "subject_locator": "new_col"}],
        ),
    )


def test_first_run_marks_every_condition_no_baseline_not_new(tmp_path: Path) -> None:
    assert pw.read_prior_snapshot(tmp_path) is None
    _build_repo_with_one_condition(tmp_path)

    result = pw.run_portfolio_watch(tmp_path)

    assert result["baseline"]["used"] is False
    assert "no prior snapshot" in result["baseline"]["note"].lower()
    all_labels = {
        change["label"]
        for scope in result["scopes"]
        for change in scope["change_labels"]
    }
    assert all_labels == {pw.LABEL_NO_BASELINE}
    assert pw.LABEL_NEW not in all_labels

    snapshot_path = tmp_path / ".seshat" / "watch" / "snapshot.json"
    assert snapshot_path.is_file()


def test_corrupt_prior_snapshot_degrades_to_no_baseline(tmp_path: Path) -> None:
    _build_repo_with_one_condition(tmp_path)
    snapshot_path = tmp_path / ".seshat" / "watch" / "snapshot.json"
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text("{not valid json", encoding="utf-8")

    assert pw.read_prior_snapshot(tmp_path) is None

    result = pw.run_portfolio_watch(tmp_path)

    assert result["baseline"]["used"] is False
    all_labels = {
        change["label"]
        for scope in result["scopes"]
        for change in scope["change_labels"]
    }
    assert all_labels == {pw.LABEL_NO_BASELINE}


def test_prior_snapshot_with_unknown_schema_version_degrades_to_no_baseline(
    tmp_path: Path,
) -> None:
    _build_repo_with_one_condition(tmp_path)
    snapshot_path = tmp_path / ".seshat" / "watch" / "snapshot.json"
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(
        json.dumps({"schema_version": "99.0", "conditions": [], "scope_set": []}),
        encoding="utf-8",
    )

    assert pw.read_prior_snapshot(tmp_path) is None
