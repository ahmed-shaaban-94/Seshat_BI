"""The generated dbt model set must pass the gate's OWN validators, offline.

These tests feed the scaffold output straight through ``project`` (model
contracts) and ``evidence`` (parity coverage) -- the same functions the real
gate runs -- so a scaffold that would trip DBT_MODEL_CONTRACT_MISSING,
DBT_MODEL_AUTHORITY_INVALID, DBT_COLUMN_CITATION_MISSING, DBT_MODEL_ORPHANED, or
DBT_ARTIFACT_INTEGRITY (parity) fails here. Driver-free: no live DB, no dbt.
"""

from __future__ import annotations

import pytest
import yaml

from seshat.dbt.contracts import FactBinding
from seshat.dbt.scaffold import model_plan, sql_render, yaml_render

pytestmark = pytest.mark.unit

TABLE_ID = "retail_store_sales"
REVISION = "d" * 40
SELECTOR = f"seshat_table_{TABLE_ID}"
SOURCE_MAP = f"mappings/{TABLE_ID}/source-map.yaml"

# A committed-map-shaped gold_star: schema-qualified relation names (the
# fact_semantics normalization strips the `gold.` qualifier), one money measure,
# a date dimension. Mirrors mappings/retail_store_sales/source-map.yaml's shape.
_MAP = {
    "meta": {"table_id": TABLE_ID, "grain": "one row = one retail transaction"},
    "columns": [
        {
            "source_name": "transaction_id",
            "decision": "keep",
            "rename_to": "transaction_id",
            "silver_type": "text",
        },
        {
            "source_name": "customer_id",
            "decision": "keep",
            "rename_to": "customer_id",
            "silver_type": "text",
        },
        {
            "source_name": "total_spent",
            "decision": "keep",
            "rename_to": "total_spent",
            "silver_type": "numeric(12,2)",
        },
        {
            "source_name": "transaction_date",
            "decision": "keep",
            "rename_to": "transaction_date",
            "silver_type": "date",
        },
        {"source_name": "legacy_flag", "decision": "drop"},
    ],
    "gold_star": {
        "fact": {
            "name": "gold.fct_sales_rss",
            "grain": "one row = one retail transaction",
            "business_key": "transaction_id",
            "measures": ["total_spent"],
            "additive_money_measures": ["total_spent"],
        },
        "dimensions": [
            {
                "name": "gold.dim_customer_rss",
                "surrogate_key": "customer_sk",
                "has_unknown_member": True,
                "attributes": ["customer_id"],
            },
        ],
        "date_dimension": {
            "name": "gold.dim_date_rss",
            "surrogate_key": "date_sk",
            "method": "generate_series",
        },
    },
}

_FACT = FactBinding(
    name="fct_sales_rss",
    business_key=("transaction_id",),
    additive_money_measures=("total_spent",),
)


def _source(document: dict) -> model_plan.MapSource:
    return model_plan.MapSource(
        document=document, source_map=SOURCE_MAP, source_map_revision=REVISION
    )


def _plan() -> model_plan.ScaffoldPlan:
    return model_plan.build_scaffold_plan(_source(_MAP), TABLE_ID, _FACT)


def _all_models(plan: model_plan.ScaffoldPlan):
    return (plan.staging, *plan.dimensions, plan.fact_model, plan.audit)


# --------------------------------------------------------------------------- #
# Model-plan derivation
# --------------------------------------------------------------------------- #
def test_plan_derives_the_full_star_with_normalized_names() -> None:
    plan = _plan()

    assert plan.staging.name == "stg_retail_store_sales"
    assert plan.fact_model.name == "fct_sales_rss"  # gold. qualifier stripped
    dim_names = {dim.name for dim in plan.dimensions}
    assert dim_names == {"dim_customer_rss", "dim_date_rss"}
    assert plan.audit.name == "audit_retail_store_sales_parity"


def test_exactly_one_model_is_the_fact_by_exclusion() -> None:
    """evidence._selected_fact_model finds the fact by EXCLUSION of dim_/stg_/audit_."""
    names = [model.name for model in _all_models(_plan())]
    facts = [name for name in names if not name.startswith(("dim_", "stg_", "audit_"))]
    assert facts == ["fct_sales_rss"]


# --------------------------------------------------------------------------- #
# The generated _models.yml passes project._model_contract with zero blockers
# --------------------------------------------------------------------------- #
def _context() -> object:
    from seshat.dbt.project import _ContractContext

    return _ContractContext(
        selector_name=SELECTOR,
        table_id=TABLE_ID,
        source_map=SOURCE_MAP,
        source_map_revision=REVISION,
    )


def test_generated_contracts_pass_the_model_validator() -> None:
    from seshat.dbt.project import _model_contract

    plan = _plan()
    context = _context()
    for model in _all_models(plan):
        document = yaml_render.render_models_document((model,), plan, SELECTOR)
        row = document["models"][0]
        blockers: list = []
        contract = _model_contract(context, row, blockers)
        assert blockers == [], (model.name, [b.code for b in blockers])
        assert contract is not None
        assert contract.authority == "derived"
        assert contract.business_key
        assert contract.columns


def test_every_column_cites_source_or_governed_derivation() -> None:
    plan = _plan()
    allowed = {"surrogate_key", "date_spine", "unknown_member", "parity_measure"}
    for model in _all_models(plan):
        for column in model.columns:
            assert column.source_columns or column.derivation in allowed, (
                model.name,
                column.name,
            )


def test_advisory_data_types_are_emitted_without_an_enforced_contract() -> None:
    """data_type surfaces the intended type (issue #406 item 3) but the contract is
    NOT enforced: the parity-proven worked example ships no enforced contract, and
    an enforced type guess would reject the human's correctly-typed completed SQL
    (e.g. an integer surrogate key vs a `text` guess). Advisory only."""
    plan = _plan()
    document = yaml_render.render_models_document(
        (plan.staging, plan.fact_model), plan, SELECTOR
    )
    staging = document["models"][0]
    fact = document["models"][1]

    assert "contract" not in staging["config"]
    total = next(c for c in staging["columns"] if c["name"] == "total_spent")
    assert total["data_type"] == "numeric(12,2)"
    # A derived column (the fact surrogate key) carries NO guessed data_type.
    sk = next(c for c in fact["columns"] if c["name"] == "fct_sales_rss_sk")
    assert "data_type" not in sk
    assert sk["meta"]["seshat"]["derivation"] == "surrogate_key"


# --------------------------------------------------------------------------- #
# The generated parity set passes evidence._validate_parity_set exactly
# --------------------------------------------------------------------------- #
def _parity_assertions(plan: model_plan.ScaffoldPlan):
    from seshat.dbt.contracts import ParityAssertion

    return tuple(
        ParityAssertion(
            assertion_id=row.assertion_id,
            assertion_class=row.assertion_class,
            subject=row.subject,
            expected="1",
            actual="1",
            delta="0",
            tolerance=row.tolerance,
            passed=True,
        )
        for row in plan.parity
    )


def _selected_unique_ids(plan: model_plan.ScaffoldPlan) -> tuple[str, ...]:
    names = [model.name for model in _all_models(plan)]
    return tuple(sorted(f"model.seshat_bi.{name}" for name in names))


def test_generated_parity_set_matches_the_built_graph_exactly() -> None:
    from seshat.dbt.evidence import _validate_parity_set

    plan = _plan()
    _validate_parity_set(
        _parity_assertions(plan),
        _selected_unique_ids(plan),
        plan.fact,
    )  # must not raise


def test_parity_subjects_have_the_governed_shape() -> None:
    plan = _plan()
    by_class: dict[str, list[str]] = {}
    for row in plan.parity:
        by_class.setdefault(row.assertion_class, []).append(row.subject)

    assert by_class["fact_row_count"] == ["fct_sales_rss"]
    assert by_class["business_key_count"] == ["fct_sales_rss.transaction_id"]
    assert by_class["additive_money_total"] == ["fct_sales_rss.total_spent"]
    assert set(by_class["dimension_member_count"]) == {
        "dim_customer_rss",
        "dim_date_rss",
    }


def test_parity_assertion_ids_are_safe_and_unique() -> None:
    import re

    plan = _plan()
    ids = [row.assertion_id for row in plan.parity]
    assert len(ids) == len(set(ids))
    for assertion_id in ids:
        assert re.fullmatch(r"[a-z][a-z0-9_]*", assertion_id), assertion_id


# --------------------------------------------------------------------------- #
# The generated audit SQL is gate-shaped (parse-able by evidence.parse_parity_rows)
# --------------------------------------------------------------------------- #
def test_audit_sql_emits_every_assertion_and_the_output_columns() -> None:
    plan = _plan()
    sql = sql_render.render_audit_sql(plan).lower()

    for row in plan.parity:
        assert f"'{row.assertion_id}'" in sql
        assert f"'{row.subject}'" in sql
    for output in ("assertion_id", "assertion_class", "subject", "passed"):
        assert f" as {output}" in sql
    assert "source('migration_gold', 'fct_sales_rss')" in sql
    assert "ref('fct_sales_rss')" in sql


def test_skeleton_sql_selects_exactly_the_contract_columns() -> None:
    plan = _plan()
    staging_sql = sql_render.render_staging_sql(plan)

    for column in plan.staging.columns:
        assert f"as {column.name}" in staging_sql
    assert "TODO" in staging_sql


def test_factless_fact_needs_no_money_assertions() -> None:
    factless_map = {
        **_MAP,
        "gold_star": {
            **_MAP["gold_star"],
            "fact": {
                **_MAP["gold_star"]["fact"],
                "measures": [],
                "additive_money_measures": [],
            },
        },
    }
    fact = FactBinding(
        name="fct_sales_rss",
        business_key=("transaction_id",),
        additive_money_measures=(),
    )
    plan = model_plan.build_scaffold_plan(_source(factless_map), TABLE_ID, fact)

    money = [r for r in plan.parity if r.assertion_class == "additive_money_total"]
    assert money == []


def test_scaffold_error_on_missing_gold_star() -> None:
    with pytest.raises(model_plan.ScaffoldError):
        model_plan.build_scaffold_plan(
            _source({"meta": {"table_id": TABLE_ID}}), TABLE_ID, _FACT
        )


def test_rendered_models_document_is_valid_yaml() -> None:
    plan = _plan()
    document = yaml_render.render_models_document(plan.dimensions, plan, SELECTOR)
    round_trip = yaml.safe_load(yaml.safe_dump(document))

    assert round_trip["version"] == 2
    assert len(round_trip["models"]) == len(plan.dimensions)


# --------------------------------------------------------------------------- #
# BLOCKER 2 regression -- provenance is never fabricated
# --------------------------------------------------------------------------- #
# A map whose gold columns are RENAMED from their bronze source_name, so a
# citation to the silver name (the bug) is a bronze column that does not exist.
_RENAMED_MAP = {
    "meta": {"table_id": TABLE_ID, "grain": "one row = one txn"},
    "columns": [
        {"source_name": "TxnId", "decision": "keep", "rename_to": "transaction_id"},
        {"source_name": "CustId", "decision": "keep", "rename_to": "customer_id"},
        {
            "source_name": "TotalSpent",
            "decision": "keep",
            "rename_to": "total_spent",
            "silver_type": "numeric(12,2)",
        },
        {"source_name": "TxnDate", "decision": "keep", "rename_to": "transaction_date"},
    ],
    "gold_star": {
        "fact": {
            "name": "gold.fct_sales_rss",
            "business_key": "transaction_id",
            "measures": ["total_spent"],
            "additive_money_measures": ["total_spent"],
        },
        "dimensions": [
            {
                "name": "gold.dim_customer_rss",
                "surrogate_key": "customer_sk",
                "attributes": ["customer_id"],
            },
        ],
        "date_dimension": {"name": "gold.dim_date_rss", "surrogate_key": "date_sk"},
    },
}


def _renamed_plan() -> model_plan.ScaffoldPlan:
    return model_plan.build_scaffold_plan(_source(_RENAMED_MAP), TABLE_ID, _FACT)


def test_fact_cites_the_real_bronze_source_name_not_the_renamed_name() -> None:
    plan = _renamed_plan()
    bk = next(c for c in plan.fact_model.columns if c.name == "transaction_id")
    money = next(c for c in plan.fact_model.columns if c.name == "total_spent")

    assert bk.source_columns == (f"bronze.{TABLE_ID}.TxnId",)
    assert money.source_columns == (f"bronze.{TABLE_ID}.TotalSpent",)


def test_dim_attribute_cites_the_real_bronze_source_name() -> None:
    plan = _renamed_plan()
    dim = next(d for d in plan.dimensions if d.name == "dim_customer_rss")
    attr = next(c for c in dim.columns if c.name == "customer_id")

    assert attr.source_columns == (f"bronze.{TABLE_ID}.CustId",)


def test_fact_and_dim_surrogate_keys_are_derivations_not_fabricated_citations() -> None:
    plan = _renamed_plan()
    fact_sk = next(c for c in plan.fact_model.columns if c.name == "fct_sales_rss_sk")
    customer_fk = next(c for c in plan.fact_model.columns if c.name == "customer_sk")
    date_fk = next(c for c in plan.fact_model.columns if c.name == "date_sk")

    for column in (fact_sk, customer_fk, date_fk):
        assert column.derivation == "surrogate_key", column.name
        assert column.source_columns == ()  # no fabricated bronze citation


def test_gold_star_reference_to_unstaged_column_fails_closed() -> None:
    broken = {
        **_RENAMED_MAP,
        "columns": [
            c for c in _RENAMED_MAP["columns"] if c["rename_to"] != "total_spent"
        ],
    }
    # total_spent is still an additive_money_measure but no longer staged.
    with pytest.raises(model_plan.ScaffoldError, match="total_spent"):
        model_plan.build_scaffold_plan(_source(broken), TABLE_ID, _FACT)


# --------------------------------------------------------------------------- #
# Item 3 regression -- key tests target the correct column
# --------------------------------------------------------------------------- #
def test_staging_key_tests_target_the_grain_key_not_the_first_map_column() -> None:
    """The grain key is NOT first in map order (transaction_id is column 3 here),
    so keying tests on columns[0] would assert uniqueness on the wrong column."""
    reordered = {
        **_MAP,
        "columns": [
            {
                "source_name": "customer_id",
                "decision": "keep",
                "rename_to": "customer_id",
            },
            {
                "source_name": "total_spent",
                "decision": "keep",
                "rename_to": "total_spent",
            },
            {
                "source_name": "transaction_id",
                "decision": "keep",
                "rename_to": "transaction_id",
            },
        ],
    }
    plan = model_plan.build_scaffold_plan(_source(reordered), TABLE_ID, _FACT)
    doc = yaml_render.render_models_document((plan.staging,), plan, SELECTOR)
    columns = doc["models"][0]["columns"]

    tested = [c["name"] for c in columns if "data_tests" in c]
    assert tested == ["transaction_id"]  # the grain key, not customer_id (col 0)


def test_dimension_key_tests_target_the_surrogate_not_the_natural_key() -> None:
    """A dim's -1 unknown-member row has a NULL natural key, so not_null must sit
    on the surrogate key, never the natural business key."""
    plan = _plan()
    dim = next(d for d in plan.dimensions if d.name == "dim_customer_rss")
    doc = yaml_render.render_models_document((dim,), plan, SELECTOR)
    columns = doc["models"][0]["columns"]

    tested = [c["name"] for c in columns if "data_tests" in c]
    assert tested == ["customer_sk"]  # the surrogate, not customer_id


# --------------------------------------------------------------------------- #
# Items 6 & 7 regression -- fail closed on unbuildable star shapes
# --------------------------------------------------------------------------- #
def test_non_dim_prefixed_dimension_fails_closed() -> None:
    bad = {
        **_MAP,
        "gold_star": {
            **_MAP["gold_star"],
            "dimensions": [
                {
                    "name": "gold.customer",
                    "surrogate_key": "customer_sk",
                    "attributes": ["customer_id"],
                },
            ],
        },
    }
    with pytest.raises(model_plan.ScaffoldError, match="dim_"):
        model_plan.build_scaffold_plan(_source(bad), TABLE_ID, _FACT)


def test_non_identifier_dimension_attribute_fails_closed() -> None:
    bad = {
        **_MAP,
        "gold_star": {
            **_MAP["gold_star"],
            "dimensions": [
                {
                    "name": "gold.dim_customer_rss",
                    "surrogate_key": "customer_sk",
                    "attributes": ["Bad Name"],
                },
            ],
        },
    }
    with pytest.raises(model_plan.ScaffoldError, match="attribute"):
        model_plan.build_scaffold_plan(_source(bad), TABLE_ID, _FACT)


def test_fact_named_with_reserved_prefix_fails_closed() -> None:
    fact = FactBinding(
        name="dim_sales",  # would be misclassified as a dimension by evidence
        business_key=("transaction_id",),
        additive_money_measures=("total_spent",),
    )
    with pytest.raises(model_plan.ScaffoldError, match="dim_/stg_/audit_"):
        model_plan.build_scaffold_plan(_source(_MAP), TABLE_ID, fact)
