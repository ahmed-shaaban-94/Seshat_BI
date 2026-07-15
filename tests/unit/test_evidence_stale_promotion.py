from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from seshat.decision_gate import _evidence_stale, evidence_stale

pytestmark = pytest.mark.unit


def _approval(path: Path) -> dict[str, object]:
    return {
        "evidence": ["evidence.md"],
        "evidence_identity": {
            "evidence.md": hashlib.sha256(path.read_bytes()).hexdigest()
        },
    }


def test_promoted_helper_matches_original_seam_for_fresh_and_stale(
    tmp_path: Path,
) -> None:
    evidence = tmp_path / "evidence.md"
    evidence.write_text("fresh\n", encoding="utf-8")
    approval = _approval(evidence)

    assert evidence_stale(tmp_path, approval) == []
    assert evidence_stale(tmp_path, approval) == _evidence_stale(tmp_path, approval)

    evidence.write_text("changed\n", encoding="utf-8")
    assert evidence_stale(tmp_path, approval) == ["evidence.md"]
    assert evidence_stale(tmp_path, approval) == _evidence_stale(tmp_path, approval)
