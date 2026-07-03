"""Per-engine SQL dialect seam for the read-only profile + validate surface.

The QueryRunner Protocol answers "how do I execute"; a Dialect answers "how do I
phrase it" -- identifier quoting, param placeholder, and the handful of SQL
fragments the profile/validate/value_proxy modules build. Adding an engine means
adding a Dialect, not editing the check logic.

PostgresDialect emits BYTE-IDENTICAL SQL to the repo's original hardcoded strings
(FILTER, row-value DISTINCT) so the existing suite stays a true regression oracle;
the three new dialects use portable/native forms verified per engine.

DRIVER-FREE: every concrete connect() lazy-imports its driver INSIDE the method,
never at module scope, so importing this module opens nothing (B3 enforces it).
"""

from __future__ import annotations

from typing import Protocol

from .identifiers import validate_identifier, validate_qualified_identifier


class Dialect(Protocol):
    name: str

    def quote_ident(self, name: str, *, context: str = "identifier") -> str: ...
    def quote_qualified(
        self, name: str, *, context: str, min_parts: int = 1, max_parts: int = 2
    ) -> str: ...
    def count_where(self, predicate: str) -> str: ...
    def distinct_tuple_count(
        self, cols: tuple[str, ...], table: str, where: str | None = None
    ) -> str: ...
    def is_text_type(self, data_type: str) -> bool: ...
    def placeholder(self) -> str: ...
    def translate_params(self, sql: str) -> str: ...


# Postgres text types (information_schema.data_type), from profile.py today.
_PG_TEXT_TYPES = frozenset(
    {"text", "character varying", "varchar", "character", "char", "name", '"char"'}
)


class PostgresDialect:
    name = "postgres"

    def quote_ident(self, name: str, *, context: str = "identifier") -> str:
        return f'"{validate_identifier(name, context=context)}"'

    def quote_qualified(
        self, name: str, *, context: str, min_parts: int = 1, max_parts: int = 2
    ) -> str:
        validated = validate_qualified_identifier(
            name, context=context, min_parts=min_parts, max_parts=max_parts
        )
        return ".".join(f'"{p}"' for p in validated.split("."))

    def count_where(self, predicate: str) -> str:
        return f"count(*) FILTER (WHERE {predicate})"

    def distinct_tuple_count(
        self, cols: tuple[str, ...], table: str, where: str | None = None
    ) -> str:
        # Postgres keeps its native row-value form (byte-identical to today).
        joined = ", ".join(cols)
        return f"count(DISTINCT ({joined}))"

    def is_text_type(self, data_type: str) -> bool:
        return data_type.lower() in _PG_TEXT_TYPES

    def placeholder(self) -> str:
        return "%s"

    def translate_params(self, sql: str) -> str:
        return sql  # canonical style IS %s; no rewrite for Postgres


_DIALECTS: dict[str, type] = {"postgres": PostgresDialect}


def get_dialect(name: str) -> Dialect:
    """Return the Dialect for ``name`` (postgres|sqlserver|mysql|snowflake)."""
    try:
        return _DIALECTS[name]()
    except KeyError:
        raise ValueError(
            f"unknown DB engine {name!r}; expected one of {sorted(_DIALECTS)}"
        ) from None
