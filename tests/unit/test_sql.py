from pathlib import Path

import pytest

from retail.core import RuleContext, Severity
from retail.rules.sql import s1_snake_case_identifiers, s2_medallion_schemas

pytestmark = pytest.mark.unit

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sql"


def _ctx(*rel: str) -> RuleContext:
    return RuleContext(repo_root=FIXTURES, tracked_files=tuple(rel))


def test_s1_passes_snake_case() -> None:
    ctx = _ctx("warehouse/pass_s1_s2.sql")
    # fixture lives flat; map the warehouse-relative name to the file
    (FIXTURES / "warehouse").mkdir(exist_ok=True)
    (FIXTURES / "warehouse" / "pass_s1_s2.sql").write_text(
        (FIXTURES / "pass_s1_s2.sql").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    assert list(s1_snake_case_identifiers(ctx)) == []


def test_s1_flags_quoted_caps() -> None:
    (FIXTURES / "warehouse").mkdir(exist_ok=True)
    (FIXTURES / "warehouse" / "fail_s1_quoted_caps.sql").write_text(
        (FIXTURES / "fail_s1_quoted_caps.sql").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    ctx = _ctx("warehouse/fail_s1_quoted_caps.sql")
    findings = list(s1_snake_case_identifiers(ctx))
    assert findings
    assert all(f.rule_id == "S1" for f in findings)
    assert all(f.severity is Severity.ERROR for f in findings)


def test_s2_passes_raw_amount_column() -> None:
    ctx = _ctx("warehouse/pass_s1_s2.sql")
    assert list(s2_medallion_schemas(ctx)) == []


def test_s2_flags_create_schema_raw() -> None:
    (FIXTURES / "warehouse").mkdir(exist_ok=True)
    (FIXTURES / "warehouse" / "fail_s2_create_schema_raw.sql").write_text(
        (FIXTURES / "fail_s2_create_schema_raw.sql").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    ctx = _ctx("warehouse/fail_s2_create_schema_raw.sql")
    findings = list(s2_medallion_schemas(ctx))
    assert len(findings) >= 1
    assert any("raw" in f.message for f in findings)
    assert all(f.rule_id == "S2" for f in findings)
    assert all(f.severity is Severity.ERROR for f in findings)


def test_s2_exempts_warehouse_readme() -> None:
    ctx = _ctx("warehouse/README.md")  # not a .sql -> never scanned
    assert list(s2_medallion_schemas(ctx)) == []


from retail.rules.sql import s3_vw_prefix


def _stage(name: str) -> str:
    (FIXTURES / "warehouse").mkdir(exist_ok=True)
    (FIXTURES / "warehouse" / name).write_text(
        (FIXTURES / name).read_text(encoding="utf-8"), encoding="utf-8"
    )
    return f"warehouse/{name}"


def test_s3_passes_prefixed_views() -> None:
    ctx = _ctx(_stage("pass_s3_vw.sql"))
    assert list(s3_vw_prefix(ctx)) == []


def test_s3_flags_unprefixed_view() -> None:
    ctx = _ctx(_stage("fail_s3_no_prefix.sql"))
    findings = list(s3_vw_prefix(ctx))
    assert len(findings) == 1
    assert findings[0].rule_id == "S3"
    assert findings[0].severity is Severity.ERROR
    assert findings[0].locator == "warehouse/fail_s3_no_prefix.sql:1"
