"""The live-database boundary (research D5).

DSN resolution reuses the main package's ``seshat.validate.resolve_dsn`` (one
resolution path: ``DATABASE_URL`` or the ``ANALYTICS_DB_*`` set from the
git-ignored ``.env``). psycopg2 is imported LAZILY inside the helpers so the
definitions-load smoke and every fixture test run without a driver.

A missing DSN is a DEFERRED BOUNDARY: callers record it as a concrete
blocking reason -- never a fabricated success (Principle VIII).
"""

from __future__ import annotations

import csv
import os
import re
from dataclasses import dataclass
from pathlib import Path

_IDENT_RE = re.compile(r"[^a-z0-9_]")

DEFERRED_BOUNDARY = "no database credentials (deferred boundary)"


def resolve_dsn() -> str | None:
    from seshat.validate import resolve_dsn as _resolve

    return _resolve(dict(os.environ))


def _connect(dsn: str):
    import psycopg2  # lazy: only a live run needs the driver

    return psycopg2.connect(dsn)


def _ident(name: str) -> str:
    cleaned = _IDENT_RE.sub("_", name.strip().lower()) or "col"
    return cleaned if not cleaned[0].isdigit() else f"c_{cleaned}"


def apply_sql_file(dsn: str, sql_path: Path) -> None:
    """Apply one committed idempotent migration file."""
    sql_text = Path(sql_path).read_text(encoding="utf-8")
    with _connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_text)


def load_csv(dsn: str, table: str, csv_path: Path) -> int:
    """Land a raw CSV into ``bronze.<table>`` (all TEXT columns; idempotent
    drop-and-reload of the raw landing). Returns rows loaded."""
    csv_path = Path(csv_path)
    with csv_path.open(encoding="utf-8", newline="") as handle:
        header = next(csv.reader(handle))
    columns = ", ".join(f"{_ident(col)} TEXT" for col in header)
    target = f"bronze.{_ident(table)}"
    with _connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS bronze")
            cur.execute(f"DROP TABLE IF EXISTS {target}")
            cur.execute(f"CREATE TABLE {target} ({columns})")
            with csv_path.open(encoding="utf-8") as data:
                cur.copy_expert(
                    f"COPY {target} FROM STDIN WITH (FORMAT csv, HEADER true)", data
                )
            cur.execute(f"SELECT COUNT(*) FROM {target}")
            return int(cur.fetchone()[0])


@dataclass(frozen=True)
class BronzeRelation:
    """A read-only snapshot of an existing ``bronze.<table>`` relation.

    ``exists`` is False when the relation is absent; ``columns`` and ``rows``
    are only meaningful when it exists. Immutable: the DB-first ingest head
    reads this and NEVER writes back."""

    exists: bool
    columns: tuple[str, ...] = ()
    rows: int = 0


def inspect_bronze(dsn: str, table: str) -> BronzeRelation:
    """Inspect ``bronze.<table>`` READ-ONLY: existence, columns, row count.

    Issues ONLY ``information_schema`` lookups and a single ``SELECT count(*)``
    -- never ``DROP``, ``TRUNCATE``, ``CREATE``, ``INSERT``, ``COPY``, or any
    other DDL/DML (issue #405: existing-Bronze mode performs zero Bronze
    writes). An absent relation returns ``exists=False`` so the caller can fail
    closed with a named blocker rather than fabricating a success.
    """
    relation = _ident(table)
    with _connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = 'bronze' AND table_name = %s "
                "ORDER BY ordinal_position",
                (relation,),
            )
            columns = tuple(str(row[0]) for row in cur.fetchall())
            if not columns:
                return BronzeRelation(exists=False)
            # Safe: `relation` is _ident-sanitized to [a-z0-9_]; the count is a
            # read-only probe, never a write.
            cur.execute(f"SELECT COUNT(*) FROM bronze.{relation}")
            rows = int(cur.fetchone()[0])
    return BronzeRelation(exists=True, columns=columns, rows=rows)
