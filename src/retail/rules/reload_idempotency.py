"""HR7 -- reload-strategy declaration for gold loads (anti-double-count).

What HR7 does (STATIC, fail-closed):
  Scans committed ``warehouse/migrations/*.sql`` files. For every migration that
  targets a ``gold.<table>``, it classifies each target's load pattern:

  - FULL_DROP_AND_REBUILD -- a ``DROP TABLE IF EXISTS gold.<t>`` (or a
    whole-table, unqualified ``TRUNCATE``/``DELETE FROM`` with no ``WHERE``)
    followed by a clean ``INSERT ... SELECT`` with no ``ON CONFLICT``. This is
    idempotency-safe by construction -- a rerun replaces rather than doubles --
    so it needs NO declaration and emits no Finding.
  - DEVIATION -- a bare append ``INSERT`` with no prior whole-table clear, an
    ``ON CONFLICT`` upsert, or a partial ``DELETE ... WHERE``/named-partition
    overwrite. A rerun of a DEVIATION *can* double-count unless the load key is
    known, so HR7 requires the load to DECLARE its dedup/overwrite key. An
    in-SQL key (``ON CONFLICT (...)`` or a named partition/date-range boundary)
    counts as a declaration; otherwise a ``-- reload-strategy: <key>`` marker in
    the migration header (or a matching ``warehouse/load-policy.md`` entry) is
    required. An undeclared DEVIATION emits exactly one ``Severity.ERROR``.

What HR7 NEVER does:
  - It never opens a database connection, executes, or simulates a reload
    (Principle VIII -- static only). A passing HR7 does NOT prove a live rerun is
    duplicate-free; that proof stays with RC2 (PK/grain uniqueness) and RC16
    (penny-exact reconciliation) under ``retail validate``.
  - It never re-derives a table's grain or primary key, never reads
    ``source-map.yaml`` (collision-free with the mapping rules), and emits no
    numeric score or count (hard rule #9).

Mirrors the S6/S8 gold-migration scan discipline: reads noise-stripped raw text
so a ``-- reload-strategy:`` marker in a comment survives (the token lexer would
discard it), and skips ``tests/`` fixtures.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from ..core import Finding, RuleContext, Severity, is_test_path
from ..registry import register
from ..sql import iter_sql_files

RULE_ID = "HR7"

# --- patterns (operate on noise-stripped raw text; case-insensitive) ---
_TARGETS_GOLD = re.compile(r"\bgold\.\w+", re.IGNORECASE)
_INSERT_INTO_GOLD = re.compile(r"\bINSERT\s+INTO\s+gold\.(\w+)", re.IGNORECASE)
_DROP_GOLD = re.compile(
    r"\bDROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?gold\.(\w+)", re.IGNORECASE
)
# whole-table clear (no WHERE, no named boundary) -- idempotency-equivalent to DROP
_TRUNCATE_GOLD = re.compile(r"\bTRUNCATE\s+(?:TABLE\s+)?gold\.(\w+)", re.IGNORECASE)
_DELETE_GOLD = re.compile(
    r"\bDELETE\s+FROM\s+gold\.(\w+)\s*(?P<where>WHERE\b)?", re.IGNORECASE
)
_ON_CONFLICT = re.compile(r"\bON\s+CONFLICT\b", re.IGNORECASE)
# a reload-strategy declaration in a SQL "-- ..." header comment
_RELOAD_MARKER = re.compile(r"--\s*reload-strategy:\s*(?P<keys>[^\n]+)", re.IGNORECASE)
# the same declaration inside warehouse/load-policy.md (markdown, no "--" prefix)
_RELOAD_MARKER_MD = re.compile(r"reload-strategy:\s*(?P<keys>[^\n|]+)", re.IGNORECASE)


def _read(ctx: RuleContext, rel: str) -> str:
    return (ctx.repo_root / rel).read_text(encoding="utf-8")


def _strip_comments_keep_markers(text: str) -> str:
    """Collapse string literals and block comments, but KEEP ``--`` line comments.

    HR7 must see ``-- reload-strategy:`` markers, so unlike the token lexer we
    preserve single-line comments; block comments and string literals are blanked
    so a ``gold.x`` mentioned inside them never triggers classification.
    """
    # blank /* ... */ block comments
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    # blank single-quoted string literals (keep the quotes' newlines out)
    text = re.sub(r"'(?:[^']|'')*'", "''", text)
    return text


def _has_gold_target(clean: str) -> bool:
    return _TARGETS_GOLD.search(clean) is not None


def _declared_in_header(raw_text: str) -> bool:
    """True if a ``-- reload-strategy:`` marker appears anywhere in the file."""
    return _RELOAD_MARKER.search(raw_text) is not None


def _load_policy_declares(ctx: RuleContext, migration_rel: str, table: str) -> bool:
    """True if a tracked ``warehouse/load-policy.md`` names this migration+table
    with a reload-strategy marker. Absent/untracked file -> False (never an ERROR
    on its own)."""
    rel = "warehouse/load-policy.md"
    if rel not in ctx.tracked_files:
        return False
    try:
        text = _read(ctx, rel)
    except OSError:
        return False
    # a policy entry naming both the migration filename and the table, with a marker
    name = migration_rel.rsplit("/", 1)[-1]
    if name not in text or table not in text:
        return False
    return _RELOAD_MARKER_MD.search(text) is not None


def _classify_and_check(ctx: RuleContext, rel: str, raw_text: str) -> list[Finding]:
    clean = _strip_comments_keep_markers(raw_text)
    if not _has_gold_target(clean):
        return []

    dropped = {m.group(1).lower() for m in _DROP_GOLD.finditer(clean)}
    truncated = {m.group(1).lower() for m in _TRUNCATE_GOLD.finditer(clean)}
    # a DELETE FROM gold.x with NO WHERE is a whole-table clear (drop-equivalent)
    whole_table_deleted = {
        m.group(1).lower()
        for m in _DELETE_GOLD.finditer(clean)
        if m.group("where") is None
    }
    cleared = dropped | truncated | whole_table_deleted

    has_conflict = _ON_CONFLICT.search(clean) is not None
    header_declared = _declared_in_header(raw_text)

    findings: list[Finding] = []
    seen: set[str] = set()
    for m in _INSERT_INTO_GOLD.finditer(clean):
        table = m.group(1).lower()
        if table in seen:
            continue
        seen.add(table)
        # FULL_DROP_AND_REBUILD: this target was whole-table cleared before insert
        if table in cleared:
            continue
        # in-SQL key (ON CONFLICT upsert) is a valid declaration
        if has_conflict:
            continue
        # otherwise it is a DEVIATION -- require a declaration
        if header_declared or _load_policy_declares(ctx, rel, table):
            continue
        line = clean.count("\n", 0, m.start()) + 1
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=Severity.ERROR,
                message=(
                    f"gold.{table} load in {rel} is a deviation "
                    "(append/upsert/partial-overwrite) with no reload-strategy "
                    "declaration; add an in-SQL key, a '-- reload-strategy: <key>' "
                    "header marker, or a warehouse/load-policy.md entry"
                ),
                locator=f"{rel}:{line}",
            )
        )
    return findings


@register(RULE_ID, "reload-strategy declaration for gold loads")
def check_hr7(ctx: RuleContext) -> Iterable[Finding]:
    findings: list[Finding] = []
    for rel in iter_sql_files(ctx):
        if is_test_path(rel):
            continue
        if not rel.startswith("warehouse/migrations/"):
            continue
        try:
            raw = _read(ctx, rel)
        except OSError:
            continue
        findings.extend(_classify_and_check(ctx, rel, raw))
    return findings
