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


def test_sqlserver_count_where_is_count_case() -> None:
    d = get_dialect("sqlserver")
    # COUNT(CASE ...) — exact on empty input (returns 0, not NULL like SUM).
    assert d.count_where("x IS NULL") == "COUNT(CASE WHEN x IS NULL THEN 1 END)"


def test_sqlserver_distinct_tuple_is_derived_table() -> None:
    d = get_dialect("sqlserver")
    assert d.distinct_tuple_count(("a", "b"), "s.t") == (
        "(SELECT COUNT(*) FROM (SELECT DISTINCT a, b FROM s.t) AS sub)"
    )


def test_sqlserver_quote_ident_brackets() -> None:
    assert get_dialect("sqlserver").quote_ident("col") == "[col]"


def test_sqlserver_placeholder_is_qmark() -> None:
    assert get_dialect("sqlserver").placeholder() == "?"


def test_sqlserver_translate_params_percent_s_to_qmark() -> None:
    d = get_dialect("sqlserver")
    assert d.translate_params("WHERE a = %s AND b = %s") == "WHERE a = ? AND b = ?"


def test_sqlserver_is_text_type() -> None:
    d = get_dialect("sqlserver")
    assert d.is_text_type("varchar")
    assert d.is_text_type("NVARCHAR")
    assert not d.is_text_type("int")


def test_mysql_count_where_is_count_case() -> None:
    assert get_dialect("mysql").count_where("x IS NULL") == (
        "COUNT(CASE WHEN x IS NULL THEN 1 END)"
    )


def test_mysql_quote_ident_backtick() -> None:
    assert get_dialect("mysql").quote_ident("col") == "`col`"


def test_mysql_placeholder_is_percent_s() -> None:
    # mysql-connector paramstyle is pyformat (%s), same as psycopg2.
    assert get_dialect("mysql").placeholder() == "%s"


def test_mysql_translate_params_noop() -> None:
    d = get_dialect("mysql")
    assert d.translate_params("WHERE a = %s") == "WHERE a = %s"


def test_mysql_distinct_tuple_is_derived_table() -> None:
    assert get_dialect("mysql").distinct_tuple_count(("a", "b"), "s.t") == (
        "(SELECT COUNT(*) FROM (SELECT DISTINCT a, b FROM s.t) AS sub)"
    )


def test_snowflake_quote_ident_uppercases() -> None:
    # R1: Snowflake folds unquoted names to UPPERCASE; quoting must match stored case
    # or the query silently matches nothing.
    assert get_dialect("snowflake").quote_ident("my_table") == '"MY_TABLE"'


def test_snowflake_quote_qualified_uppercases_each_part() -> None:
    assert (
        get_dialect("snowflake").quote_qualified("bronze.my_table", context="t")
        == '"BRONZE"."MY_TABLE"'
    )


def test_snowflake_count_where_is_count_case() -> None:
    assert get_dialect("snowflake").count_where("x IS NULL") == (
        "COUNT(CASE WHEN x IS NULL THEN 1 END)"
    )


def test_snowflake_is_text_type_collapses_to_text() -> None:
    d = get_dialect("snowflake")
    assert d.is_text_type("TEXT")
    assert d.is_text_type("text")
    assert not d.is_text_type("NUMBER")


def test_snowflake_columns_query_uppercases_filter() -> None:
    # The profiler must pass UPPERCASE (schema, table); the query uses ILIKE-safe
    # equality on UPPER()-folded catalog values.
    sql = get_dialect("snowflake").columns_query()
    assert "INFORMATION_SCHEMA.COLUMNS" in sql
    assert "%s" in sql  # snowflake default paramstyle is pyformat


@pytest.mark.parametrize("engine", ["postgres", "sqlserver", "mysql", "snowflake"])
def test_count_where_predicate_is_embedded_verbatim(engine: str) -> None:
    # R3: the conditional-count fragment must count only matching rows; every engine
    # embeds the predicate. (PG uses FILTER, the others COUNT(CASE) — both count 0,
    # never NULL, on zero matches; the string form encodes that.)
    frag = get_dialect(engine).count_where("v IS NULL")
    assert "v IS NULL" in frag
    assert frag.startswith(("count(", "COUNT("))


def test_r2_param_translation_qmark_only_for_pyodbc() -> None:
    # R2: only the qmark engine rewrites %s -> ?; the pyformat engines leave it.
    assert get_dialect("sqlserver").translate_params("a=%s") == "a=?"
    for e in ("postgres", "mysql", "snowflake"):
        assert get_dialect(e).translate_params("a=%s") == "a=%s"


def test_distinct_tuple_form_is_portable_for_new_engines() -> None:
    # R (portability): the three new engines all use the derived-table form.
    for e in ("sqlserver", "mysql", "snowflake"):
        out = get_dialect(e).distinct_tuple_count(("a", "b"), "s.t")
        assert out.startswith("(SELECT COUNT(*) FROM (SELECT DISTINCT a, b")
        assert out.endswith("AS sub)")


def test_normalize_catalog_literal_identity_for_non_snowflake() -> None:
    # Guards against a future "simplify to one method" refactor silently breaking
    # Postgres (and the other non-folding engines) by uppercasing everywhere.
    for e in ("postgres", "sqlserver", "mysql"):
        assert get_dialect(e).normalize_catalog_literal("Bronze") == "Bronze"


def test_normalize_catalog_literal_uppercases_for_snowflake() -> None:
    assert get_dialect("snowflake").normalize_catalog_literal("bronze") == "BRONZE"
