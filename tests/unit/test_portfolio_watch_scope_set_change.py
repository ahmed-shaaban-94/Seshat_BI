"""US2 tests: scope added/removed between runs (spec 131, T018, FR-011).

A scope present in only one of the two runs is reported as a scope-level
``scope_added``/``scope_removed`` change, not misattributed to condition
changes inside a missing scope.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat import portfolio_watch as pw
from tests.fixtures.portfolio_watch.builders import write_readiness_status

pytestmark = pytest.mark.unit


def test_a_new_scope_is_a_scope_level_change_not_a_condition_change(
    tmp_path: Path,
) -> None:
    write_readiness_status(
        tmp_path,
        "scope_alpha",
        current_stage="mapping_ready",
        stage_status={"source_ready": "pass", "mapping_ready": "blocked"},
        stage_blocking_reasons={"mapping_ready": ["mapping_ready approval is missing"]},
        top_blocking_reasons=["mapping_ready approval is missing"],
    )
    first = pw.run_portfolio_watch(tmp_path)
    assert first["scope_changes"] == []

    write_readiness_status(
        tmp_path,
        "scope_beta",
        current_stage="mapping_ready",
        stage_status={"source_ready": "pass", "mapping_ready": "blocked"},
        stage_blocking_reasons={"mapping_ready": ["a required artifact is missing"]},
        top_blocking_reasons=["a required artifact is missing"],
    )
    second = pw.run_portfolio_watch(tmp_path)

    assert {"scope_id": "scope_beta", "change": "scope_added"} in second[
        "scope_changes"
    ]
    beta_labels = next(
        s["change_labels"] for s in second["scopes"] if s["scope_id"] == "scope_beta"
    )
    # scope_beta's own conditions are NOT misattributed as 'new' condition
    # changes -- they are absent from the second run's snapshot diff entirely
    # (the scope-level change already reports the addition).
    assert all(c["label"] != pw.LABEL_NEW for c in beta_labels)


def test_a_removed_scope_is_a_scope_level_change(tmp_path: Path) -> None:
    write_readiness_status(
        tmp_path,
        "scope_alpha",
        current_stage="mapping_ready",
        stage_status={"source_ready": "pass", "mapping_ready": "blocked"},
        stage_blocking_reasons={"mapping_ready": ["mapping_ready approval is missing"]},
        top_blocking_reasons=["mapping_ready approval is missing"],
    )
    write_readiness_status(
        tmp_path,
        "scope_beta",
        current_stage="mapping_ready",
        stage_status={"source_ready": "pass", "mapping_ready": "blocked"},
        stage_blocking_reasons={"mapping_ready": ["a required artifact is missing"]},
        top_blocking_reasons=["a required artifact is missing"],
    )
    pw.run_portfolio_watch(tmp_path)

    (tmp_path / "mappings" / "scope_beta" / "readiness-status.yaml").unlink()

    second = pw.run_portfolio_watch(tmp_path)

    assert {
        "scope_id": "scope_beta",
        "change": "scope_removed",
    } in second["scope_changes"]
    assert not any(s["scope_id"] == "scope_beta" for s in second["scopes"])
    # scope_alpha's own standing condition is unaffected by the sibling
    # scope's removal.
    alpha_labels = next(
        s["change_labels"] for s in second["scopes"] if s["scope_id"] == "scope_alpha"
    )
    assert all(c["label"] == pw.LABEL_UNCHANGED for c in alpha_labels)
