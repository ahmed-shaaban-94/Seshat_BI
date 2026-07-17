"""Optional real-Postgres proof for the governed dbt shadow adapter."""

from __future__ import annotations

import pytest

PENDING = "[PENDING LIVE PROFILE]"

pytest.importorskip(
    "testcontainers.postgres",
    reason=f"{PENDING}: install the livetest extra and start Docker",
)
pytest.importorskip(
    "psycopg2",
    reason=f"{PENDING}: install the db extra",
)

pytestmark = pytest.mark.live_db


def test_migration_and_shadow_outputs_have_complete_parity(
    live_dbt_project,
) -> None:
    evidence = live_dbt_project.build("retail_store_sales")

    assert evidence.outcome == "pass"
    assert len(evidence.parity) == 8
    assert all(row.passed for row in evidence.parity)


@pytest.mark.parametrize(
    "mutation,assertion_id",
    [
        ("delete_fact", "fact_row_count"),
        ("duplicate_business_key", "fact_distinct_transaction_id"),
        ("change_money", "fact_total_spent_sum"),
        ("remove_unknown_member", "dim_product_member_count"),
    ],
)
def test_each_parity_class_blocks(
    live_dbt_project,
    mutation: str,
    assertion_id: str,
) -> None:
    evidence = live_dbt_project.build_with_mutation(mutation)

    assert evidence.outcome == "blocked"
    assert assertion_id in {
        blocker.assertion_id for blocker in evidence.blocking_reasons
    }
