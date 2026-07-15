from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from seshat.impact_map import build_impact_map
from tests.unit.test_impact_map import _fixture

pytestmark = pytest.mark.unit

_FORBIDDEN_KEYS = {
    "score",
    "confidence",
    "risk",
    "risk_score",
    "trust",
    "completeness",
    "blast_radius",
    "weight",
}


def _keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {key for child in value.values() for key in _keys(child)}
    if isinstance(value, list):
        return {key for child in value for key in _keys(child)}
    return set()


def test_projection_contains_no_numeric_impact_score(tmp_path: Path) -> None:
    projection = build_impact_map(
        _fixture(tmp_path, "direct"),
        "naming.metric_alpha",
        generated_at="2026-07-15T00:00:00Z",
    )
    assert not (_keys(projection) & _FORBIDDEN_KEYS)
    assert re.search(r"\d%", json.dumps(projection)) is None
