"""Integration tests for the PBIR-vs-blueprint validator (spec 123, US8, T046).

Extends (not replaces) the shipped Visual Implementation Review: given a committed
PBIR report tree (compiler- or human-produced) and the approved design artifacts
(page blueprint + visual-contract binding map), the validator reports
expected-vs-actual conformity and flags deviations. It NEVER grants
``dashboard_ready: pass`` -- it records evidence/deviations only (FR-031).

Both scenarios sit the oracle ON the real risk (repo lesson
``verifier-must-sit-on-the-risk``): a REAL committed PBIR tree (copied from the
same Desktop-authored fixtures the compiler unit tests use --
``tests/fixtures/pbir/page_shell.Report`` + ``visual_fmt.Report``), with a REAL
injected deviation, never a mock:

* T046a: a manually-added visual with no entry on the approved binding map is
  FLAGGED as an unapproved addition (never silently passed).
* T046b: a visual whose PBIR type diverges from the approved blueprint's declared
  type (an approved-design-vs-PBIR divergence -- the compiler's lineChart binding
  reappearing as a ``barChart`` in the committed report) is FLAGGED.
* The validator's overall result is `blocked` in both cases and it never emits
  ``dashboard_ready: pass`` -- there is no code path in the module that can.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from seshat.pbir_validate_blueprint import validate_blueprint

pytestmark = pytest.mark.integration

_FIXTURES = Path(__file__).parent.parent / "fixtures" / "pbir"
_PAGE_SHELL_SAMPLE = _FIXTURES / "page_shell.Report"
_LINECHART_SAMPLE = _FIXTURES / "visual_fmt.Report"

_PAGE_NAME = "a1b2c3d4e5f600112233"

_BLUEPRINT_YAML = """\
page_name: branch_perf
audience: branch_manager
business_question: "How is the branch performing this period vs last?"
visuals:
  - visual_id: "v05"
    spec_ref: "design/visuals/v05.yaml"
    section: "main_insight"
    binds_contract: "TotalSales"
readiness:
  status: "warning"
  evidence: ["design review pending"]
  blocking_reasons: []
"""

_BINDING_MAP_MD = """\
# Visual -> contract binding map -- retail_store_sales

## Binding map (every visual -> exactly one APPROVED contract)

| visual_id | visual_type | business_question | bound_contract (approved) | field |
|-----------|-------------|-------------------|---------------------------|-------|
| `v05` | `lineChart` | `How is branch perf?` | `TotalSales` | `sales.total` |
"""


def _sample_visual_json(sample: Path) -> Path:
    return sample / "definition" / "pages" / "pg" / "visuals" / "v1" / "visual.json"


def _committed_visual_json(report_dir: Path, visual_id: str) -> Path:
    pages = report_dir / "definition" / "pages"
    return pages / _PAGE_NAME / "visuals" / visual_id / "visual.json"


def _report_tree(tmp_path: Path, *, report_name: str = "RSS.Report") -> Path:
    """A REAL committed PBIR tree: the verified page-shell sample plus one built
    visual copied from the verified lineChart sample -- grounded in the same
    Desktop-authored fixtures the compiler unit tests use, not a hand-typed mock."""
    dst = tmp_path / report_name
    shutil.copytree(_PAGE_SHELL_SAMPLE, dst)
    visual_src = _sample_visual_json(_LINECHART_SAMPLE)
    visual_dst = _committed_visual_json(dst, "v05")
    visual_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(visual_src, visual_dst)
    return dst


def _write_design(tmp_path: Path) -> tuple[Path, Path]:
    design_dir = tmp_path / "mappings" / "retail_store_sales" / "design"
    design_dir.mkdir(parents=True, exist_ok=True)
    blueprint = design_dir / "dashboard-page-blueprint.branch_perf.yaml"
    blueprint.write_text(_BLUEPRINT_YAML, encoding="utf-8")
    binding_map = design_dir / "visual-contract-binding-map.md"
    binding_map.write_text(_BINDING_MAP_MD, encoding="utf-8")
    return blueprint, binding_map


# --------------------------------------------------------------------------- #
# Conforming baseline: proves the validator can report `pass`-shaped conformity
# on a page with no injected deviation (the shape T046 needs to prove FLAGGING
# actually distinguishes bad from good, not merely emitting a fixed result).
# --------------------------------------------------------------------------- #
def test_conforming_page_reports_no_deviations(tmp_path: Path):
    blueprint, binding_map = _write_design(tmp_path)
    report_dir = _report_tree(tmp_path)

    result = validate_blueprint(
        report_dir=report_dir,
        blueprint_path=blueprint,
        binding_map_path=binding_map,
    )

    assert result.deviations == ()
    assert result.unapproved_additions == ()
    assert result.missing_elements == ()
    assert result.status == "pass"
    assert result.grants_approval is False


# --------------------------------------------------------------------------- #
# T046a: a manually-added unapproved visual is flagged
# --------------------------------------------------------------------------- #
def test_manually_added_unapproved_visual_is_flagged(tmp_path: Path):
    blueprint, binding_map = _write_design(tmp_path)
    report_dir = _report_tree(tmp_path)

    # Inject a SECOND visual with no binding-map entry -- a human hand-added it in
    # Desktop (or a rogue script did) after the design review. Grounded in the same
    # real lineChart sample shape, just under an id absent from the approved map.
    orphan_src = _sample_visual_json(_LINECHART_SAMPLE)
    orphan_dst = _committed_visual_json(report_dir, "v99")
    orphan_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(orphan_src, orphan_dst)

    result = validate_blueprint(
        report_dir=report_dir,
        blueprint_path=blueprint,
        binding_map_path=binding_map,
    )

    assert any("v99" in d.locator for d in result.unapproved_additions)
    assert result.status == "blocked"
    assert result.grants_approval is False


# --------------------------------------------------------------------------- #
# T046b: a blueprint<->PBIR divergence (visual type) is flagged
# --------------------------------------------------------------------------- #
def test_blueprint_pbir_type_divergence_is_flagged(tmp_path: Path):
    blueprint, binding_map = _write_design(tmp_path)
    report_dir = _report_tree(tmp_path)

    # Mutate the committed visual's type so it diverges from the binding map's
    # declared `lineChart` -- e.g. the compiler ran once, a human then hand-edited
    # the visual in Desktop to a barChart without re-approving the design.
    visual_path = _committed_visual_json(report_dir, "v05")
    doc = json.loads(visual_path.read_text(encoding="utf-8-sig"))
    doc["visual"]["visualType"] = "barChart"
    text = json.dumps(doc, indent=2, sort_keys=True) + "\n"
    visual_path.write_text(text, encoding="utf-8")

    result = validate_blueprint(
        report_dir=report_dir,
        blueprint_path=blueprint,
        binding_map_path=binding_map,
    )

    assert any(
        "v05" in d.locator and "lineChart" in d.message and "barChart" in d.message
        for d in result.deviations
    )
    assert result.status == "blocked"
    assert result.grants_approval is False


# --------------------------------------------------------------------------- #
# FR-031: the validator records evidence/deviations only -- it can NEVER grant
# `dashboard_ready: pass`. This is a structural guarantee, not a per-call flag:
# assert the returned result object carries no path to self-grant.
# --------------------------------------------------------------------------- #
def test_validator_never_grants_approval_field_is_always_false(tmp_path: Path):
    blueprint, binding_map = _write_design(tmp_path)
    report_dir = _report_tree(tmp_path)

    result = validate_blueprint(
        report_dir=report_dir,
        blueprint_path=blueprint,
        binding_map_path=binding_map,
    )
    assert result.grants_approval is False
    # No writable "approve" mutation exists on the result shape.
    assert not hasattr(result, "approve")
    assert not hasattr(result, "grant_approval")


def test_validator_is_read_only_no_files_written(tmp_path: Path):
    blueprint, binding_map = _write_design(tmp_path)
    report_dir = _report_tree(tmp_path)
    before = {
        str(p.relative_to(report_dir)): p.stat().st_mtime_ns
        for p in report_dir.rglob("*")
        if p.is_file()
    }

    validate_blueprint(
        report_dir=report_dir,
        blueprint_path=blueprint,
        binding_map_path=binding_map,
    )

    after = {
        str(p.relative_to(report_dir)): p.stat().st_mtime_ns
        for p in report_dir.rglob("*")
        if p.is_file()
    }
    assert before == after  # not one byte written -- validation is read-only
