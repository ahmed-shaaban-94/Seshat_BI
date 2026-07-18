"""Static contract for the governed shadow dbt project and worked star."""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DBT = ROOT / "dbt"
TABLE_ID = "retail_store_sales"
SELECTOR = f"seshat_table_{TABLE_ID}"
SOURCE_MAP = f"mappings/{TABLE_ID}/source-map.yaml"
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
# Per governed table, the exact model set that table's worked star must contain.
# The project hosts several tables side by side (spec 133 VII: models isolated
# under the worked selector); each table still owns EXACTLY its own models -- no
# stray, no missing. Add a table's entry here when its worked example is added.
EXPECTED_MODELS_BY_TABLE = {
    "retail_store_sales": EXPECTED_MODELS,
    "sales_c086_raw": {
        "stg_sales_c086_raw",
        "dim_product_c086",
        "dim_billing_type_c086",
        "dim_customer_c086",
        "dim_staff_c086",
        "dim_date_c086",
        "fct_sales_c086",
        "audit_sales_c086_raw_parity",
    },
}
# The exact migration_gold source tables each governed table reconciles against.
EXPECTED_MIGRATION_GOLD_BY_TABLE = {
    "retail_store_sales": [
        "fct_sales_rss",
        "dim_customer_rss",
        "dim_product_rss",
        "dim_payment_method_rss",
        "dim_location_rss",
        "dim_date_rss",
    ],
    "sales_c086_raw": [
        "fct_sales_c086",
        "dim_product_c086",
        "dim_billing_type_c086",
        "dim_customer_c086",
        "dim_staff_c086",
        "dim_date_c086",
    ],
}
ALLOWED_DERIVATIONS = {
    "surrogate_key",
    "date_spine",
    "unknown_member",
    "parity_measure",
}


def _governed_tables() -> set[str]:
    """Table ids with a committed mapping working set (dir + source map + readiness).

    Note: a mapping working set does NOT imply a dbt worked example. Some tables
    (e.g. status-surface demo fixtures) have a mapping but no dbt models. Tables
    that have a dbt star are the keys of EXPECTED_MODELS_BY_TABLE, always a subset
    of this set -- see _tables_with_models().
    """
    mappings = ROOT / "mappings"
    return {
        child.name
        for child in mappings.iterdir()
        if child.is_dir()
        and (child / "source-map.yaml").is_file()
        and (child / "readiness-status.yaml").is_file()
    }


def _tables_with_models() -> set[str]:
    """Governed tables that ship a dbt worked star (subset of _governed_tables)."""
    return set(EXPECTED_MODELS_BY_TABLE)


def _yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _model_rows() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for path in (DBT / "models").rglob("*.yml"):
        document = _yaml(path)
        for row in document.get("models", []):
            rows[row["name"]] = row
    return rows


def _map_revision(table_id: str = TABLE_ID) -> str:
    result = subprocess.run(
        ["git", "rev-parse", f"HEAD:mappings/{table_id}/source-map.yaml"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        shell=False,
    )
    return result.stdout.strip()


def test_worked_project_has_complete_star() -> None:
    sql_names = {path.stem for path in (DBT / "models").rglob("*.sql")}
    rows = _model_rows()

    # Every table that ships a dbt star must be a real governed table, contribute
    # EXACTLY its worked-star model set -- no stray model, none missing -- and the
    # project's models are precisely the union of those stars (no orphan model
    # belonging to nothing). Tables with a mapping but no dbt models (demo
    # fixtures) legitimately contribute none.
    governed = _governed_tables()
    tables_with_models = _tables_with_models()
    assert tables_with_models <= governed, (
        "a table with dbt models has no committed mapping working set",
        tables_with_models - governed,
    )
    expected_union: set[str] = set()
    for table_id in tables_with_models:
        expected = EXPECTED_MODELS_BY_TABLE[table_id]
        assert expected <= sql_names, (table_id, expected - sql_names)
        expected_union |= expected
    assert set(rows) == expected_union


def test_project_uses_only_target_prefixed_shadow_layers() -> None:
    project = _yaml(DBT / "dbt_project.yml")
    models = project["models"]["seshat_bi"]

    assert project["name"] == "seshat_bi"
    assert project["profile"] == "seshat_bi_warehouse"
    assert models["staging"]["+schema"] == "silver"
    assert models["marts"]["+schema"] == "gold"
    assert models["audit"]["+schema"] == "audit"
    assert {models[layer]["+schema"] for layer in models} == {
        "silver",
        "gold",
        "audit",
    }

    macro = (DBT / "macros" / "generate_schema_name.sql").read_text(encoding="utf-8")
    for layer in ("silver", "gold", "audit"):
        assert f"'{layer}'" in macro
    for protected in ("bronze", "public"):
        assert f"'{protected}'" not in macro
    assert "target.schema" in macro
    assert "raise_compiler_error" in macro


def test_schema_macro_routes_dbt_test_nodes_to_shadow_test_schema() -> None:
    macro = (DBT / "macros" / "generate_schema_name.sql").read_text(encoding="utf-8")

    assert "node.resource_type == 'test'" in macro
    assert "requested_schema == 'dbt_test__audit'" in macro
    assert "target.schema" in macro


def test_generic_project_and_macro_contain_no_worked_example_answers() -> None:
    generic = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in (
            DBT / "dbt_project.yml",
            DBT / "macros" / "generate_schema_name.sql",
        )
    )

    for token in ("retail_store_sales", "c086", "pharmacy", "billing_code"):
        assert token not in generic


def test_selector_and_source_are_exact() -> None:
    selectors = _yaml(DBT / "selectors.yml")["selectors"]
    sources = _yaml(DBT / "models" / "sources" / "_sources.yml")["sources"]
    by_name = {source["name"]: source for source in sources}
    tables_with_models = _tables_with_models()

    # Each table with a dbt star declares exactly one tag selector of the fixed shape.
    for table_id in tables_with_models:
        selector = f"seshat_table_{table_id}"
        match = [row for row in selectors if row["name"] == selector]
        assert len(match) == 1, (table_id, "exactly one selector expected")
        assert match[0]["definition"] == {"method": "tag", "value": selector}

    # bronze source carries exactly one landing table per table with a dbt star.
    assert by_name["bronze"]["schema"] == "bronze"
    assert {t["name"] for t in by_name["bronze"]["tables"]} == tables_with_models

    # migration_gold carries exactly each such table's oracle tables -- the union,
    # nothing stray.
    expected_gold: set[str] = set()
    for table_id in tables_with_models:
        expected_gold |= set(EXPECTED_MIGRATION_GOLD_BY_TABLE[table_id])
    assert by_name["migration_gold"]["schema"] == "gold"
    assert {t["name"] for t in by_name["migration_gold"]["tables"]} == expected_gold


def test_every_model_and_output_column_has_current_governed_citation() -> None:
    governed = _governed_tables()
    # Cache each governed table's committed source-map revision once.
    revision_by_table = {tid: _map_revision(tid) for tid in governed}

    for name, row in _model_rows().items():
        contract = row["meta"]["seshat"]
        tid = contract["table_id"]
        # Every model must be attributed to a REAL governed table -- a model citing
        # a table with no committed mapping working set is an orphan and fails here
        # (the contract-test twin of the DBT_MODEL_ORPHANED validator guard).
        assert tid in governed, (name, "table_id is not a governed table", tid)
        # ...and it must cite ITS OWN table: the matching selector tag, its own
        # source map, and that map's own committed revision. A model that carried
        # another table's revision (e.g. a c086 model citing the rss hash) fails
        # here -- the citation cannot silently belong to the wrong table.
        assert f"seshat_table_{tid}" in row["config"]["tags"], (name, tid)
        assert contract["source_map"] == f"mappings/{tid}/source-map.yaml"
        assert contract["source_map_revision"] == revision_by_table[tid], (name, tid)
        assert contract["authority"] == "derived"
        assert contract["grain"]
        assert contract["business_key"]
        assert row["columns"], name
        for column in row["columns"]:
            citation = column["meta"]["seshat"]
            sources = citation.get("source_columns", [])
            derivation = citation.get("derivation")
            assert sources or derivation in ALLOWED_DERIVATIONS, (
                name,
                column["name"],
            )


def test_staging_reproduces_approved_cleaning_without_sentinel_update() -> None:
    sql = (
        (DBT / "models" / "staging" / TABLE_ID / "stg_retail_store_sales.sql")
        .read_text(encoding="utf-8")
        .lower()
    )

    assert "source('bronze', 'retail_store_sales')" in sql
    for column in (
        "transaction_id",
        "customer_id",
        "category",
        "item",
        "price_per_unit",
        "quantity",
        "total_spent",
        "payment_method",
        "location",
        "transaction_date",
        "discount_applied",
    ):
        assert f"trim({column})" in sql
    assert "::numeric(12, 2)" in sql
    assert "::date" in sql
    assert "case lower(nullif(discount_applied, ''))" in sql
    assert "when 'true' then true" in sql
    assert "when 'false' then false" in sql
    assert "update " not in sql
    assert "sentinel" not in sql


def test_dimensions_use_deterministic_keys_and_governed_unknown_members() -> None:
    marts = DBT / "models" / "marts" / TABLE_ID
    entity_models = {
        "dim_customer_rss.sql": "customer_id",
        "dim_product_rss.sql": "item",
        "dim_payment_method_rss.sql": "payment_method",
        "dim_location_rss.sql": "location",
    }
    for filename, natural_key in entity_models.items():
        sql = (marts / filename).read_text(encoding="utf-8").lower()
        assert "-1::integer" in sql
        assert "unknown" in sql
        assert f"row_number() over (order by {natural_key})" in sql
        assert "union all" in sql

    date_sql = (marts / "dim_date_rss.sql").read_text(encoding="utf-8").lower()
    assert "generate_series(" in date_sql
    assert "date '2022-01-01'" in date_sql
    assert "date '2025-01-18'" in date_sql
    assert "'yyyymmdd'" in date_sql
    assert "-1::integer" not in date_sql


def test_fact_coalesces_only_entity_keys_and_leaves_date_fail_loud() -> None:
    sql = (
        (DBT / "models" / "marts" / TABLE_ID / "fct_sales_rss.sql")
        .read_text(encoding="utf-8")
        .lower()
    )

    for alias in ("dc", "dp", "dpm", "dl"):
        assert f"coalesce({alias}." in sql
    assert "coalesce(dd.date_sk" not in sql
    assert "dd.date_sk" in sql
    assert "row_number() over (order by s.transaction_id)" in sql
    for model in (
        "stg_retail_store_sales",
        "dim_customer_rss",
        "dim_product_rss",
        "dim_payment_method_rss",
        "dim_location_rss",
        "dim_date_rss",
    ):
        assert f"ref('{model}')" in sql


def _data_test(row: dict, column_name: str, test_name: str) -> dict:
    column = next(item for item in row["columns"] if item["name"] == column_name)
    for item in column.get("data_tests", []):
        if isinstance(item, dict) and test_name in item:
            value = item[test_name]
            return value if isinstance(value, dict) else {}
    raise AssertionError(f"missing {test_name} test on {row['name']}.{column_name}")


def test_fact_business_key_and_relationship_tests_are_governed() -> None:
    fact = _model_rows()["fct_sales_rss"]
    for test_name in ("unique", "not_null"):
        config = _data_test(fact, "transaction_id", test_name)["config"]
        assert SELECTOR in config["tags"]

    relationships = {
        "customer_sk": ("dim_customer_rss", "customer_sk"),
        "product_sk": ("dim_product_rss", "product_sk"),
        "payment_method_sk": (
            "dim_payment_method_rss",
            "payment_method_sk",
        ),
        "location_sk": ("dim_location_rss", "location_sk"),
        "date_sk": ("dim_date_rss", "date_sk"),
    }
    for column, (model, field) in relationships.items():
        test = _data_test(fact, column, "relationships")
        assert test["arguments"] == {
            "to": f"{{{{ ref('{model}') }}}}",
            "field": field,
        }
        assert SELECTOR in test["config"]["tags"]


def test_dimension_surrogate_keys_are_unique_and_not_null() -> None:
    dimensions = {
        "dim_customer_rss": "customer_sk",
        "dim_product_rss": "product_sk",
        "dim_payment_method_rss": "payment_method_sk",
        "dim_location_rss": "location_sk",
        "dim_date_rss": "date_sk",
    }
    for model, key in dimensions.items():
        row = _model_rows()[model]
        for test_name in ("unique", "not_null"):
            config = _data_test(row, key, test_name)["config"]
            assert SELECTOR in config["tags"]


def test_audit_model_emits_exact_normalized_parity_contract() -> None:
    sql = (
        (DBT / "models" / "audit" / TABLE_ID / "audit_retail_store_sales_parity.sql")
        .read_text(encoding="utf-8")
        .lower()
    )
    assertion_ids = {
        "fact_row_count",
        "fact_distinct_transaction_id",
        "fact_total_spent_sum",
        "dim_customer_member_count",
        "dim_product_member_count",
        "dim_payment_method_member_count",
        "dim_location_member_count",
        "dim_date_member_count",
    }

    for assertion_id in assertion_ids:
        assert f"'{assertion_id}'" in sql
    for output in (
        "assertion_id",
        "assertion_class",
        "subject",
        "expected",
        "actual",
        "delta",
        "tolerance",
        "passed",
    ):
        assert f" as {output}" in sql
    assert sql.count("union all") == 7
    assert "source('migration_gold', 'fct_sales_rss')" in sql
    assert "ref('fct_sales_rss')" in sql
