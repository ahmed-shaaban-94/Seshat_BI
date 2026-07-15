from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from seshat.impact_map import build_impact_map, render_impact_map

pytestmark = pytest.mark.unit

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "impact_map"
_WORKED_EXAMPLE_TOKENS = (
    "c086",
    "retail_store_sales",
    "total_spent",
    "billing_code",
    "insurance_policy",
    "pharmacy",
    "ahmed shaaban",
)


@pytest.mark.parametrize(
    "family,preview",
    [
        ("direct", False),
        ("transitive", False),
        ("stale_evidence", False),
        ("missing_ref", False),
        ("incomplete_lineage", False),
        ("dangling_pointer", False),
        ("preview", True),
        ("non_approved_subject", False),
    ],
)
def test_generic_projection_leaks_no_worked_example_defaults(
    tmp_path: Path, family: str, preview: bool
) -> None:
    shutil.copytree(_FIXTURES / "_base", tmp_path, dirs_exist_ok=True)
    shutil.copytree(_FIXTURES / family, tmp_path, dirs_exist_ok=True)
    projection = build_impact_map(
        tmp_path,
        "naming.metric_alpha",
        preview=preview,
        generated_at="2026-07-15T00:00:00Z",
    )
    rendered = (json.dumps(projection) + render_impact_map(projection)).lower()
    assert all(token not in rendered for token in _WORKED_EXAMPLE_TOKENS)
