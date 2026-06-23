from __future__ import annotations

from pathlib import Path

import pytest

from retail.core import RuleContext, Severity
from retail.rules.pbir import check_pbir_relative_reference

FIXTURES = Path(__file__).parent.parent / "fixtures" / "pbir"


def _ctx(report_dir: str) -> RuleContext:
    return RuleContext(
        repo_root=FIXTURES,
        tracked_files=(f"{report_dir}/definition.pbir",),
    )


@pytest.mark.unit
def test_relative_path_passes() -> None:
    findings = list(check_pbir_relative_reference(_ctx("relative.Report")))
    assert findings == []


@pytest.mark.unit
def test_absolute_path_fails() -> None:
    findings = list(check_pbir_relative_reference(_ctx("absolute.Report")))
    assert len(findings) == 1
    f = findings[0]
    assert f.rule_id == "R1"
    assert f.severity is Severity.ERROR
    assert f.locator == "absolute.Report/definition.pbir#/datasetReference/byPath/path"
    assert "absolute" in f.message.lower()


@pytest.mark.unit
def test_byconnection_fails() -> None:
    findings = list(check_pbir_relative_reference(_ctx("byconn.Report")))
    assert len(findings) == 1
    f = findings[0]
    assert f.rule_id == "R1"
    assert f.severity is Severity.ERROR
    assert f.locator == "byconn.Report/definition.pbir#/datasetReference/byConnection"
    assert "byconnection" in f.message.lower()


@pytest.mark.unit
def test_no_pbir_files_is_silent() -> None:
    ctx = RuleContext(repo_root=FIXTURES, tracked_files=("warehouse/x.sql",))
    assert list(check_pbir_relative_reference(ctx)) == []
