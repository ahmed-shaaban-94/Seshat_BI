"""Unit tests: the dashboard pattern library never fabricates (spec 123, US3).

FR-013 requires every Dashboard Pattern doc (`docs/patterns/dashboard/*.md`) to
stay GENERIC guidance -- suitable audiences, intended purpose, common question
families, metric ROLES (outcome/driver/guardrail), common page structure,
recommended visual roles, expected action paths, and common design risks --
and to NEVER fabricate a concrete named KPI, a DAX/formula expression, or
tenant-specific business logic.

The oracle sits on the actual fabrication mode: a bare DAX/formula token
(``=``, ``:=``, ``SUM(``, ``CALCULATE(``, ``DIVIDE(``, a ``[Table]`` bracket
reference) or a concrete, named retail KPI drawn from this repo's own
`skills/retail-kpi-knowledge` vocabulary (Net Sales, Gross Margin, GMROI,
Sell-through, Days of Supply, AOV, Basket Size, and their common spelling
variants). Detecting "this string is a KPI name" in full generality is not
mechanically decidable; this test uses a representative denylist of the
concrete metrics this repo's own KPI-knowledge skill names, which is exactly
the fabrication mode FR-013 is written to forbid in a GENERIC pattern doc.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.unit._dashboard_pattern_scan import find_fabrications

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).parent.parent.parent
PATTERNS_DIR = REPO_ROOT / "docs" / "patterns" / "dashboard"


# --- RED-first: the detector itself, proven on a fabrication fixture ---------


def test_detects_dax_formula_token() -> None:
    text = "Net Sales = SUM(Sales[Amount])"
    findings = find_fabrications(text)
    assert findings
    assert any("SUM(" in f or "formula" in f.lower() for f in findings)


def test_detects_walrus_style_dax_assignment() -> None:
    text = "Gross Margin % := DIVIDE([Gross Margin], [Net Sales])"
    findings = find_fabrications(text)
    assert findings


def test_detects_named_kpi_from_denylist() -> None:
    text = "This page shows GMROI and Sell-through prominently."
    findings = find_fabrications(text)
    assert findings
    joined = " ".join(findings).lower()
    assert "gmroi" in joined or "sell-through" in joined


def test_clean_role_level_text_has_zero_findings() -> None:
    text = (
        "An outcome role showing the primary performance result, paired with "
        "a guardrail role that must not slip while the outcome improves."
    )
    assert find_fabrications(text) == []


# --- Applied to the real committed pattern docs ------------------------------


def _pattern_docs() -> list[Path]:
    return sorted(PATTERNS_DIR.glob("*.md"))


def test_ten_pattern_families_exist() -> None:
    docs = _pattern_docs()
    assert len(docs) == 10, f"expected 10 pattern docs, found {[d.name for d in docs]}"


@pytest.mark.parametrize("doc_path", _pattern_docs(), ids=lambda p: p.name)
def test_pattern_doc_never_fabricates(doc_path: Path) -> None:
    text = doc_path.read_text(encoding="utf-8")
    findings = find_fabrications(text)
    assert findings == [], f"{doc_path.name} fabricates: {findings}"


@pytest.mark.parametrize("doc_path", _pattern_docs(), ids=lambda p: p.name)
def test_pattern_doc_has_all_eight_guidance_fields(doc_path: Path) -> None:
    """Each pattern doc provides GUIDANCE ONLY across the eight FR-012 fields
    (data-model.md's Dashboard Pattern entity): suitable_audiences,
    intended_purpose, common_question_families, metric_roles (outcome/driver/
    guardrail), common_page_structure, recommended_visual_roles,
    expected_action_paths, common_design_risks."""
    text = doc_path.read_text(encoding="utf-8").lower()
    required_headings = [
        "suitable audiences",
        "intended purpose",
        "common question families",
        "metric roles",
        "common page structure",
        "recommended visual roles",
        "expected action paths",
        "common design risks",
    ]
    missing = [h for h in required_headings if h not in text]
    assert missing == [], f"{doc_path.name} missing sections: {missing}"


def test_no_pattern_doc_is_empty() -> None:
    for doc_path in _pattern_docs():
        assert doc_path.stat().st_size > 200, f"{doc_path.name} looks empty/stub"


# --- The pattern-recommendation workflow (FR-013/FR-014) ---------------------

WORKFLOW_PATH = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "powerbi-dashboard-design"
    / "workflows"
    / "pattern-recommendation.md"
)


def test_workflow_never_fabricates() -> None:
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert find_fabrications(text) == []


def test_workflow_cites_gap_detector_never_recomputes() -> None:
    """FR-013: an unavailable requirement is surfaced as a gap via the shipped
    `retail dashboard-gaps` -- this workflow must route to it, not reimplement
    gap detection itself."""
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "retail dashboard-gaps" in text
    assert "gap_detector.py" in text


def test_workflow_maps_every_pattern_family_reachable() -> None:
    """FR-014 / no-orphan-doc: every one of the 10 family docs must be named
    somewhere in the workflow's purpose -> candidate map."""
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    for doc_path in _pattern_docs():
        assert doc_path.name in text, (
            f"{doc_path.name} is unreachable from the workflow"
        )


def test_workflow_never_auto_picks_when_multiple_fit() -> None:
    """FR-014: when multiple patterns fit, present candidates for human choice
    -- never silently pick one."""
    text = WORKFLOW_PATH.read_text(encoding="utf-8").lower()
    assert "never auto-pick" in text or "never silently pick" in text
