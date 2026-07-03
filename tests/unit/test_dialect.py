from __future__ import annotations

import pytest

from retail.dialect import get_dialect

pytestmark = pytest.mark.unit


def test_postgres_count_where_is_filter() -> None:
    pg = get_dialect("postgres")
    # Postgres KEEPS the native FILTER form (byte-identical to today's SQL).
    assert pg.count_where("x IS NULL") == "count(*) FILTER (WHERE x IS NULL)"


def test_postgres_quote_ident_double_quote() -> None:
    pg = get_dialect("postgres")
    assert pg.quote_ident("invoice_no") == '"invoice_no"'


def test_postgres_placeholder_is_percent_s() -> None:
    assert get_dialect("postgres").placeholder() == "%s"


def test_get_dialect_unknown_raises() -> None:
    with pytest.raises(ValueError):
        get_dialect("oracle")


def test_postgres_distinct_tuple_count_row_value() -> None:
    pg = get_dialect("postgres")
    assert pg.distinct_tuple_count(("invoice_no", "line_no"), "silver.t") == (
        "count(DISTINCT (invoice_no, line_no))"
    )


def test_postgres_columns_query_is_information_schema() -> None:
    pg = get_dialect("postgres")
    sql = pg.columns_query()
    assert "information_schema.columns" in sql
    assert "table_schema = %s" in sql
    assert "table_name = %s" in sql
    assert "ORDER BY ordinal_position" in sql
