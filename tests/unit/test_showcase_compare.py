"""Before/after comparability unit coverage (spec 127, US4). Never a
fabricated delta; graceful omission when snapshots are not comparable."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from seshat.showcase.compare import build_comparison

pytestmark = pytest.mark.unit

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures/showcase/snapshots"
_BEFORE = _FIXTURES / "comparable_before.json"
_AFTER = _FIXTURES / "comparable_after.json"
_MISMATCHED_SCOPE = _FIXTURES / "mismatched_scope.json"
_MALFORMED_READINESS = _FIXTURES / "malformed_readiness_after.json"
_MISSING_READINESS_KEY = _FIXTURES / "missing_readiness_key_after.json"


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

    verdicts = {item["path"]: item["verdict"] for item in result["evidence_verdicts"]}
    assert verdicts["mappings/orders/source-profile.md"] == "verified"
    assert verdicts["mappings/orders/readiness-status.yaml"] == "changed"
    assert verdicts["mappings/orders/source-map.yaml"] == "unavailable"


def test_evidence_verdicts_diff_the_snapshots_not_the_live_workspace(
    tmp_path: Path,
) -> None:
    """Regression: evidence_verdicts must compare `before` vs `after`
    directly, never `after` vs the live workspace -- an empty/unrelated
    tmp_path (no files on disk at all) must still yield real verdicts."""
    result = build_comparison(tmp_path, (_BEFORE, _AFTER))
    assert result["comparable"] is True
    verdicts = {item["path"]: item["verdict"] for item in result["evidence_verdicts"]}
    assert verdicts["mappings/orders/readiness-status.yaml"] == "changed"


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


def test_missing_readiness_key_is_malformed_not_an_empty_valid_delta(
    tmp_path: Path,
) -> None:
    """A snapshot that omits the ``readiness`` key entirely must NOT be read
    the same as an explicit ``readiness: []`` -- a valid Passport document
    always carries the key. Silently defaulting a missing key to `[]` would
    make this comparable with a fabricated empty delta instead of omitting
    with a truthful note."""
    result = build_comparison(tmp_path, (_BEFORE, _MISSING_READINESS_KEY))
    assert result["comparable"] is False
    assert "readiness" in result["omitted_reason"]
    assert result["stage_transitions"] == []
    assert result["evidence_verdicts"] == []


def test_removed_artifact_reports_a_missing_evidence_verdict(
    tmp_path: Path,
) -> None:
    """An artifact recorded in `before` but absent from `after` (the
    evidence reference was removed) must appear as its own `missing`
    verdict -- not be silently omitted just because only `after`'s own
    artifact list is walked."""

    def _snapshot(revision: str, artifacts: list[dict]) -> dict:
        return {
            "schema_version": "1.0",
            "source_revision": revision,
            "scope": ["orders"],
            "readiness": [],
            "artifacts": artifacts,
            "approvals": [],
            "validation_boundary": {
                "static": "x",
                "live": "unavailable",
                "unavailable_checks": [],
            },
            "authority_disclaimer": "test",
            "passport_id": "passport-a",
            "generated_at": "2026-07-01T00:00:00+00:00",
        }

    before_path = tmp_path / "before.json"
    after_path = tmp_path / "after.json"
    before_path.write_text(
        json.dumps(
            _snapshot(
                "1111111111111111111111111111111111111111",
                [
                    {
                        "artifact_id": "evidence:removed",
                        "path": "mappings/orders/removed.md",
                        "sha256": "a" * 64,
                    }
                ],
            )
        ),
        encoding="utf-8",
    )
    after_path.write_text(
        json.dumps(_snapshot("2222222222222222222222222222222222222222", [])),
        encoding="utf-8",
    )

    result = build_comparison(tmp_path, (before_path, after_path))
    assert result["comparable"] is True
    verdicts = {item["path"]: item["verdict"] for item in result["evidence_verdicts"]}
    assert verdicts["mappings/orders/removed.md"] == "missing"
