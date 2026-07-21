"""End-to-end proof: `dbt init` + scaffold produces a project that validates.

Materializes a fresh governed workspace (``governed_projects.dbt_init``),
commits an approved mapping working set, runs ``scaffold_models``, then runs the
REAL ``validate_project`` on the result. A scaffold that trips any static gate
blocker (contract/authority/citation/orphan/selector) fails here. Driver-free:
no dbt, no live database -- only git + the static validators.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

ROOT = Path(__file__).resolve().parents[2]
TABLE_ID = "retail_store_sales"
EXPECTED_MODELS = {
    "stg_retail_store_sales",
    "dim_customer_rss",
    "dim_product_rss",
    "dim_payment_method_rss",
    "dim_location_rss",
    "dim_date_rss",
    "fct_sales_rss",
    "audit_retail_store_sales_parity",
}


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def _seed_workspace(tmp_path: Path) -> Path:
    from seshat.governed_projects import dbt_init

    dbt_init(tmp_path)
    (tmp_path / "schemas").mkdir(exist_ok=True)
    shutil.copy2(
        ROOT / "schemas" / "dbt-run-evidence.schema.json",
        tmp_path / "schemas" / "dbt-run-evidence.schema.json",
    )
    mapping = tmp_path / "mappings" / TABLE_ID
    mapping.mkdir(parents=True)
    for name in ("source-map.yaml", "readiness-status.yaml", "unresolved-questions.md"):
        shutil.copy2(ROOT / "mappings" / TABLE_ID / name, mapping / name)
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "seed approved mapping")
    return tmp_path


def test_scaffold_output_passes_static_validation(tmp_path: Path) -> None:
    from seshat.dbt.gate import resolve_working_set
    from seshat.dbt.project import validate_project
    from seshat.dbt.scaffold import scaffold_models

    root = _seed_workspace(tmp_path)
    report = scaffold_models(root, TABLE_ID)

    sql_names = {path.stem for path in (root / "dbt/models").rglob("*.sql")}
    assert EXPECTED_MODELS <= sql_names
    assert "dbt/selectors.yml" in report.merged
    assert "dbt/models/sources/_sources.yml" in report.merged

    working_set = resolve_working_set(root, TABLE_ID)
    result = validate_project(root, working_set, target_schema="seshat_dbt_shadow")

    assert result.valid, [b.code for b in result.blocking_reasons]
    assert {c.name for c in result.model_contracts} == EXPECTED_MODELS


def test_scaffold_is_non_destructive_on_rerun(tmp_path: Path) -> None:
    from seshat.dbt.scaffold import scaffold_models

    root = _seed_workspace(tmp_path)
    scaffold_models(root, TABLE_ID)
    second = scaffold_models(root, TABLE_ID)

    assert second.written == ()  # every model file already exists -> all kept
    assert second.merged == ()  # selector + sources already present
    assert second.kept
