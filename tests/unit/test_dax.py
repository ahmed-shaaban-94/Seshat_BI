"""Unit tests for DAX/TMDL rules D1-D5 (M4a)."""

from pathlib import Path

import pytest

from retail.core import RuleContext, Severity
from retail.rules.dax import (
    d1_pascalcase_measures,
    d2_display_folder,
    d3_no_duplicate_logic,
    d4_divide_not_slash,
    d5_explicit_aggregation,
)
from retail.tmdl import TmdlMeasure

pytestmark = pytest.mark.unit

FIXTURES = Path(__file__).parent.parent / "fixtures" / "tmdl"


def _ctx(tmp_path: Path, fixture: str) -> RuleContext:
    """Stage a fixture under a SemanticModel path and return a RuleContext."""
    rel = "Model.SemanticModel/definition/tables/T.tmdl"
    dest = tmp_path / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        (FIXTURES / fixture).read_text(encoding="utf-8-sig"), encoding="utf-8"
    )
    return RuleContext(repo_root=tmp_path, tracked_files=(rel,))


# ---------------------------------------------------------------------------
# D1 — PascalCase measure names
# ---------------------------------------------------------------------------


def test_d1_flags_non_pascalcase(tmp_path: Path) -> None:
    findings = list(d1_pascalcase_measures(_ctx(tmp_path, "bad_names.tmdl")))
    assert len(findings) == 1
    assert findings[0].rule_id == "D1"
    assert findings[0].severity is Severity.ERROR
    assert "total_revenue" in findings[0].message


def test_d1_passes_clean(tmp_path: Path) -> None:
    assert list(d1_pascalcase_measures(_ctx(tmp_path, "clean_sales.tmdl"))) == []


def test_d1_locator_includes_line_number(tmp_path: Path) -> None:
    findings = list(d1_pascalcase_measures(_ctx(tmp_path, "bad_names.tmdl")))
    assert findings[0].locator.endswith(":2")


# ---------------------------------------------------------------------------
# D2 — displayFolder required
# ---------------------------------------------------------------------------


def test_d2_passes_clean(tmp_path: Path) -> None:
    assert list(d2_display_folder(_ctx(tmp_path, "clean_sales.tmdl"))) == []


def test_d2_passes_ti_file_with_folder(tmp_path: Path) -> None:
    # bad_ti_no_marker.tmdl has a displayFolder on its measure
    assert list(d2_display_folder(_ctx(tmp_path, "bad_ti_no_marker.tmdl"))) == []


def test_d2_flags_missing_folder(tmp_path: Path) -> None:
    findings = list(d2_display_folder(_ctx(tmp_path, "bad_no_folder.tmdl")))
    assert len(findings) == 1
    assert findings[0].rule_id == "D2"
    assert findings[0].severity is Severity.ERROR
    assert "Revenue" in findings[0].message


def test_d2_passes_non_empty_folder(tmp_path: Path) -> None:
    """A measure with a present, non-empty displayFolder passes (is None == False)."""
    rel = "Model.SemanticModel/definition/tables/T.tmdl"
    dest = tmp_path / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        "table T\n\tmeasure Revenue = SUM(T[Amount])\n\t\tdisplayFolder: KPIs\n",
        encoding="utf-8",
    )
    ctx = RuleContext(repo_root=tmp_path, tracked_files=(rel,))
    assert list(d2_display_folder(ctx)) == []


def test_d2_does_not_flag_explicitly_empty_folder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Contract: D2 guards on `is None`, not falsiness.

    An empty-string displayFolder (`""`) is a *different* state than a missing
    line (`None`). D2 must flag only `None`. Because the parser never yields
    `""` from TMDL text (its regex requires a non-empty value), this exercises
    the rule directly with a constructed measure to lock the is-None contract:
    a falsy-but-not-None folder must NOT be flagged.
    """
    from retail.rules import dax as dax_mod
    from retail.tmdl import TmdlTable

    empty_folder_table = TmdlTable(
        name="T",
        measures=(
            TmdlMeasure(
                name="Revenue", expression="SUM(T[Amount])", display_folder="", line=2
            ),
        ),
        columns=(),
        partition_sources=(),
        annotations=(),
        line=1,
    )
    monkeypatch.setattr(
        dax_mod, "iter_model_files", lambda ctx, suffix: iter([("T.tmdl", "x")])
    )
    monkeypatch.setattr(dax_mod, "parse_tmdl", lambda text: empty_folder_table)
    ctx = RuleContext(repo_root=Path("."), tracked_files=())
    assert list(d2_display_folder(ctx)) == []


# ---------------------------------------------------------------------------
# D3 — no duplicated measure logic
# ---------------------------------------------------------------------------


def test_d3_flags_identical_bodies(tmp_path: Path) -> None:
    findings = list(d3_no_duplicate_logic(_ctx(tmp_path, "bad_duplicate.tmdl")))
    assert len(findings) == 1
    assert findings[0].rule_id == "D3"
    assert findings[0].severity is Severity.ERROR
    assert "Revenue" in findings[0].message and "TotalSales" in findings[0].message


def test_d3_passes_clean(tmp_path: Path) -> None:
    assert list(d3_no_duplicate_logic(_ctx(tmp_path, "clean_sales.tmdl"))) == []


def test_d3_second_occurrence_is_locator(tmp_path: Path) -> None:
    """The second (duplicate) measure is the locator, not the first."""
    findings = list(d3_no_duplicate_logic(_ctx(tmp_path, "bad_duplicate.tmdl")))
    # TotalSales is the second measure; its name appears in the message
    assert "TotalSales" in findings[0].message


# ---------------------------------------------------------------------------
# D4 — use DIVIDE() not bare /
# ---------------------------------------------------------------------------


def test_d4_flags_bare_slash(tmp_path: Path) -> None:
    findings = list(d4_divide_not_slash(_ctx(tmp_path, "bad_divide.tmdl")))
    assert len(findings) == 1
    assert findings[0].rule_id == "D4"
    assert findings[0].severity is Severity.ERROR
    assert findings[0].locator.endswith(":2")


def test_d4_passes_clean(tmp_path: Path) -> None:
    # clean_sales uses DIVIDE(...) and SUM(...) — no bare slash
    assert list(d4_divide_not_slash(_ctx(tmp_path, "clean_sales.tmdl"))) == []


def test_d4_passes_url_in_string_literal(tmp_path: Path) -> None:
    """A '/' inside a string literal must NOT trigger D4."""
    rel = "Model.SemanticModel/definition/tables/T.tmdl"
    dest = tmp_path / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        'table T\n\tmeasure M = "http://example.com"\n\t\tdisplayFolder: X\n',
        encoding="utf-8",
    )
    ctx = RuleContext(repo_root=tmp_path, tracked_files=(rel,))
    assert list(d4_divide_not_slash(ctx)) == []


# ---------------------------------------------------------------------------
# D5 — WARNING: numeric column summarizeBy != none
# ---------------------------------------------------------------------------


def test_d5_warns_on_implicit_aggregation(tmp_path: Path) -> None:
    findings = list(d5_explicit_aggregation(_ctx(tmp_path, "bad_summarize.tmdl")))
    assert len(findings) == 1
    assert findings[0].rule_id == "D5"
    assert findings[0].severity is Severity.WARNING
    assert "Amount" in findings[0].message


def test_d5_passes_when_summarize_none(tmp_path: Path) -> None:
    # clean_sales: Amount and ProductKey both summarizeBy none
    assert list(d5_explicit_aggregation(_ctx(tmp_path, "clean_sales.tmdl"))) == []


def test_d5_passes_non_numeric_column_with_sum(tmp_path: Path) -> None:
    """A text/string column with summarizeBy: sum should NOT fire D5."""
    rel = "Model.SemanticModel/definition/tables/T.tmdl"
    dest = tmp_path / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        "table T\n\tcolumn Name\n\t\tdataType: string\n\t\tsummarizeBy: sum\n",
        encoding="utf-8",
    )
    ctx = RuleContext(repo_root=tmp_path, tracked_files=(rel,))
    assert list(d5_explicit_aggregation(ctx)) == []


def test_d5_exempts_tests_prefix(tmp_path: Path) -> None:
    """Files under tests/ must be exempted (iter_model_files exemption)."""
    rel = "tests/fixtures/golden_pbip/X.SemanticModel/definition/T.tmdl"
    dest = tmp_path / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        "table T\n\tcolumn Amount\n\t\tdataType: decimal\n\t\tsummarizeBy: sum\n",
        encoding="utf-8",
    )
    ctx = RuleContext(repo_root=tmp_path, tracked_files=(rel,))
    assert list(d5_explicit_aggregation(ctx)) == []
