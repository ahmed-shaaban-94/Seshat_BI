"""Unit tests for the fail-closed Decision Store loader (spec 121, T007/T017)."""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.decision_store import (
    CRITICAL_DECISION_TYPES,
    STATUS_VALUES,
    STORE_PATHS,
    approval_is_valid,
    is_critical,
    is_open_status,
    load_store,
    load_store_file,
    store_files,
)

pytestmark = pytest.mark.unit

_SEMANTIC = ".seshat/semantic-decisions.yaml"

_VALID = """\
decisions:
  - id: table_grain.fct_sales
    decision_type: table_grain
    statement: "One row of fct_sales is one sale line."
    scope:
      tables: ["fct_sales"]
    status: proposed
    confidence: high
    evidence: ["mappings/fct_sales/source-profile.md"]
    proposed_by: "agent"
    proposed_at: "2026-01-01"
batches: []
"""


def _write(tmp_path: Path, rel: str, body: str) -> Path:
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


# --- store_files selector -------------------------------------------------


def test_store_files_selects_only_canonical_seshat_paths() -> None:
    tracked = (
        _SEMANTIC,
        ".seshat/kpi-contracts.yaml",
        "templates/semantic-decisions.yaml",  # blank template must NOT match
        "docs/whatever.yaml",
    )
    assert store_files(tracked) == [
        ".seshat/kpi-contracts.yaml",
        _SEMANTIC,
    ]


def test_store_files_absent_returns_empty() -> None:
    # Absent store => empty list => callers pass-silent (fail-closed contract 4a).
    assert store_files(("docs/x.md", "templates/kpi-contracts.yaml")) == []


# --- happy path -----------------------------------------------------------


def test_load_valid_store_roundtrips_one_decision(tmp_path: Path) -> None:
    _write(tmp_path, _SEMANTIC, _VALID)
    store = load_store(tmp_path, (_SEMANTIC,))
    assert store.present
    assert store.problems == ()
    decisions = store.decisions()
    assert len(decisions) == 1
    assert decisions[0]["id"] == "table_grain.fct_sales"


def test_empty_file_is_a_legitimate_empty_store(tmp_path: Path) -> None:
    _write(tmp_path, _SEMANTIC, "")
    loaded = load_store_file(tmp_path, _SEMANTIC)
    assert loaded.present
    assert loaded.ok
    assert loaded.decisions == ()


# --- fail-closed conditions ----------------------------------------------


def test_invalid_yaml_fails_closed_not_raise(tmp_path: Path) -> None:
    _write(tmp_path, _SEMANTIC, "decisions: [\n  unterminated")
    loaded = load_store_file(tmp_path, _SEMANTIC)
    assert not loaded.ok
    assert any("not valid YAML" in p.message for p in loaded.problems)


def test_non_mapping_top_level_fails_closed(tmp_path: Path) -> None:
    _write(tmp_path, _SEMANTIC, "- just\n- a\n- list\n")
    loaded = load_store_file(tmp_path, _SEMANTIC)
    assert not loaded.ok
    assert any("must be a mapping" in p.message for p in loaded.problems)


def test_unknown_top_level_key_fails_closed(tmp_path: Path) -> None:
    _write(tmp_path, _SEMANTIC, "decisions: []\ngremlins: []\n")
    loaded = load_store_file(tmp_path, _SEMANTIC)
    assert not loaded.ok
    assert any("unknown top-level key" in p.message for p in loaded.problems)


def test_decisions_not_a_list_fails_closed(tmp_path: Path) -> None:
    _write(tmp_path, _SEMANTIC, "decisions: {not: a list}\n")
    loaded = load_store_file(tmp_path, _SEMANTIC)
    assert not loaded.ok
    assert any("'decisions' must be a list" in p.message for p in loaded.problems)


def test_non_dict_decision_member_fails_closed(tmp_path: Path) -> None:
    _write(tmp_path, _SEMANTIC, "decisions:\n  - just a string\n")
    loaded = load_store_file(tmp_path, _SEMANTIC)
    assert not loaded.ok
    assert any("must be a mapping" in p.message for p in loaded.problems)


def test_unreadable_file_fails_closed(tmp_path: Path) -> None:
    # Point at a path that does not exist on disk though "tracked".
    loaded = load_store_file(tmp_path, _SEMANTIC)
    assert not loaded.ok
    assert any("could not read" in p.message for p in loaded.problems)


# --- vocabulary helpers ---------------------------------------------------


def test_status_vocabulary_is_the_nine_lifecycle_values() -> None:
    assert STATUS_VALUES == {
        "proposed",
        "approved",
        "rejected",
        "pending",
        "needs_user_input",
        "needs_sample",
        "blocked",
        "deferred",
        "superseded",
    }


def test_critical_types_are_the_eleven_named() -> None:
    assert len(CRITICAL_DECISION_TYPES) == 11
    assert "policy_ruling" in CRITICAL_DECISION_TYPES
    assert "report_intent_approval" in CRITICAL_DECISION_TYPES
    assert is_critical("kpi_definition")
    assert is_critical("report_intent_approval")
    assert not is_critical("naming")


def test_open_status_excludes_approved_and_superseded() -> None:
    assert is_open_status("pending")
    assert not is_open_status("approved")
    assert not is_open_status("superseded")


def test_store_paths_are_the_three_seshat_files() -> None:
    assert STORE_PATHS == (
        ".seshat/semantic-decisions.yaml",
        ".seshat/kpi-contracts.yaml",
        ".seshat/cleaning-rules.yaml",
    )


# --- report_intent_approval validity (spec 123, T007) ----------------------
#
# report_intent_approval is now a critical decision type. A report_owner-authored
# record must pass approval_is_valid; an agent identity must never satisfy it
# (Principle V -- no self-grant).

_REPORT_INTENT_AUTHORITY: dict[str, frozenset[str]] = {
    "report_intent_approval": frozenset({"report_owner"}),
}


def _report_intent_decision(approved_by: str) -> dict:
    return {
        "id": "report_intent_approval.branch_perf",
        "decision_type": "report_intent_approval",
        "status": "approved",
        "approval": {
            "approved_by": approved_by,
            "approved_at": "2026-01-02",
            "source": "interview",
            "evidence": ["ev.md"],
            "evidence_identity": {"ev.md": "abc123"},
            "reviewed_scope": {"artifacts": ["report_intent.branch_perf"]},
        },
    }


def test_report_owner_approval_is_valid_for_report_intent_approval() -> None:
    decision = _report_intent_decision("R. Owner (report_owner)")
    valid, reason = approval_is_valid(decision, _REPORT_INTENT_AUTHORITY)
    assert valid, reason


def test_agent_identity_is_rejected_for_report_intent_approval() -> None:
    # An agent identity is not a "Name (class)" shape at all -- and even if it
    # were shaped as an agent role, no self-grant is permitted (Principle V).
    decision = _report_intent_decision("agent")
    valid, reason = approval_is_valid(decision, _REPORT_INTENT_AUTHORITY)
    assert not valid
    assert "invalid approved_by" in reason


def test_ineligible_class_is_rejected_for_report_intent_approval() -> None:
    # A shape-valid owner whose class is not eligible for report_intent_approval
    # (e.g. metric_owner, not report_owner) must also fail closed.
    decision = _report_intent_decision("A. Owner (metric_owner)")
    valid, reason = approval_is_valid(decision, _REPORT_INTENT_AUTHORITY)
    assert not valid
    assert "ineligible" in reason
