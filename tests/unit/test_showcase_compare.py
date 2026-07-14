"""Before/after comparability unit coverage (spec 127, US4). Never a
fabricated delta; graceful omission when snapshots are not comparable."""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.showcase.compare import build_comparison

pytestmark = pytest.mark.unit

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures/showcase/snapshots"
_BEFORE = _FIXTURES / "comparable_before.json"
_AFTER = _FIXTURES / "comparable_after.json"
_MISMATCHED_SCOPE = _FIXTURES / "mismatched_scope.json"
_MALFORMED_READINESS = _FIXTURES / "malformed_readiness_after.json"


def test_comparable_pair_yields_real_stage_transitions_and_verdicts(
    tmp_path: Path,
) -> None:
    result = build_comparison(tmp_path, (_BEFORE, _AFTER))
    assert result["comparable"] is True
    assert result["omitted_reason"] is None
    assert result["before_revision"] == "1111111111111111111111111111111111111111"
    assert result["after_revision"] == "2222222222222222222222222222222222222222"
    transitions = result["stage_transitions"]
    assert {
        "table_id": "orders",
        "stage": "mapping_ready",
        "before_status": "blocked",
        "after_status": "pass",
    } in transitions
    assert isinstance(result["evidence_verdicts"], list)


def test_mismatched_scope_is_not_comparable_with_a_truthful_reason(
    tmp_path: Path,
) -> None:
    result = build_comparison(tmp_path, (_BEFORE, _MISMATCHED_SCOPE))
    assert result["comparable"] is False
    assert result["omitted_reason"]
    assert "scope" in result["omitted_reason"]
    assert result["stage_transitions"] == []
    assert result["evidence_verdicts"] == []


def test_mismatched_schema_is_not_comparable(tmp_path: Path) -> None:
    forged = tmp_path / "forged_schema.json"
    forged.write_text(
        _AFTER.read_text(encoding="utf-8").replace('"1.0"', '"2.0"'),
        encoding="utf-8",
    )
    result = build_comparison(tmp_path, (_BEFORE, forged))
    assert result["comparable"] is False
    assert "schema" in result["omitted_reason"]


def test_single_snapshot_is_not_comparable(tmp_path: Path) -> None:
    result = build_comparison(tmp_path, (_BEFORE, None))
    assert result["comparable"] is False
    assert "one snapshot" in result["omitted_reason"]
    assert result["stage_transitions"] == []


def test_no_snapshots_is_not_comparable(tmp_path: Path) -> None:
    result = build_comparison(tmp_path, None)
    assert result["comparable"] is False
    assert result["omitted_reason"]
    assert result["stage_transitions"] == []
    assert result["evidence_verdicts"] == []


def test_same_source_revision_is_not_comparable(tmp_path: Path) -> None:
    result = build_comparison(tmp_path, (_BEFORE, _BEFORE))
    assert result["comparable"] is False
    assert "same source_revision" in result["omitted_reason"]


def test_unreadable_snapshot_file_is_not_comparable(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.json"
    result = build_comparison(tmp_path, (_BEFORE, missing))
    assert result["comparable"] is False
    assert result["omitted_reason"]


def test_malformed_readiness_member_is_omitted_gracefully_not_a_crash(
    tmp_path: Path,
) -> None:
    """Same schema_version/scope, differing source_revision, but one
    snapshot's ``readiness`` member is a dict instead of the Passport list --
    this must be omitted with a truthful note, never raise and never
    fabricate a delta from a shape it cannot read."""
    result = build_comparison(tmp_path, (_BEFORE, _MALFORMED_READINESS))
    assert result["comparable"] is False
    assert "readiness" in result["omitted_reason"]
    assert result["stage_transitions"] == []
    assert result["evidence_verdicts"] == []
