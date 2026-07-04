# Data Model: Date-Spine Completeness Static Gate (HR8)

Phase 1 -- the entities/artifact shapes this feature introduces or reads. All
shapes are GENERIC (Principle VII): no worked-example table, dimension, or
column name is a required literal anywhere below; `dim_date`,
`retail_store_sales`, and `2022-01-01` appear only as illustrative examples.

HR8 introduces NO new persisted file format and NO new declaration/manifest
schema (FR-010) -- unlike a Product Module (F024 shape) or 087/HR1 (which adds
`conformed-dimension-map.yaml`), this feature's only new "entity" is the
in-memory classification logic inside one rule function, expressed here as
plain Python shapes for clarity. Everything below either (a) is read from an
EXISTING file format unchanged, or (b) is an in-process value never persisted
to disk.

## 1. Date-spine build statement (read, not persisted)

The SQL statement HR8 inspects. Identical to what S7 already discovers --
HR8 adds no new discovery criterion, it only inspects deeper into a statement
S7 has already located.

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `file` | `str` (repo-relative path) | `iter_sql_files(ctx)` | e.g. `warehouse/migrations/NNNN_create_gold_<table>_star.sql`; illustrative only |
| `start_line` / `end_line` | `int` (1-based) | `tokenize_sql` token `.line` values across the statement's token span (INSERT token through the next `;` token) | the same span S7 walks; HR8 re-derives it independently rather than sharing mutable state with `s7_contiguous_date_dim` (FR-010: S7's function body is untouched) |
| `target_name` | `str` | first token in the span whose lowercased text starts with `dim_date` | generic prefix match, same as S7/S8; NOT a hardcoded full name (Principle VII) |
| `has_generate_series` | `bool` | any token in the span whose lowercased text equals `generate_series` | HR8's own precondition -- a statement without this token is not HR8's concern (S7 already flags it via the DISTINCT-vs-generate_series check, unrelated to HR8) |

A statement failing `has_generate_series` (uses `SELECT DISTINCT` instead, or
neither) produces NO HR8 Finding of any kind -- that is exclusively S7's
concern (Boundary section; FR-002).

## 2. `generate_series` call arguments (read, not persisted)

For each qualifying statement (has both a `dim_date`-prefixed target and a
`generate_series` token), the call's three arguments, read from the
`strip_sql_comments`-stripped RAW TEXT over the statement's line span (NOT
from `tokenize_sql`, which blanks literal contents -- Clarifications
2026-07-04).

| Field | Type | Notes |
|-------|------|-------|
| `start_arg_text` | `str` (raw source text, trimmed) | 1st positional argument's literal source text, e.g. `DATE '2022-01-01'` or `(SELECT min(sale_date) FROM silver.orders)` |
| `end_arg_text` | `str` (raw source text, trimmed) | 2nd positional argument, same shape as `start_arg_text` |
| `step_arg_text` | `str` (raw source text, trimmed) | 3rd positional argument, e.g. `INTERVAL '1 day'` or `INTERVAL '1 month'` |
| `call_line` | `int` (1-based) | the line the `generate_series(` token begins on, for the Finding locator |

Argument-splitting is a balanced-parenthesis top-level comma split (a bound MAY
itself contain a parenthesized subquery per Edge Cases: `(SELECT max(d) FROM
...)`), not a naive `str.split(",")`.

## 3. Step classification (in-process value, never persisted)

| Value | Meaning | Outcome |
|-------|---------|---------|
| `daily` | `step_arg_text` matches a literal `INTERVAL` expression textually equal to `INTERVAL '1 day'`, whitespace-insensitive | passes -- no ERROR (FR-003) |
| `non_daily_literal` | `step_arg_text` matches a literal `INTERVAL` expression of any OTHER span (e.g. `INTERVAL '1 month'`, `INTERVAL '7 days'`) | fail-closed ERROR naming the file, line, and the offending literal step text (FR-003; US1) |
| `unclassifiable` | `step_arg_text` is present but is NOT a literal `INTERVAL` expression (a bare identifier, a computed expression, a non-`INTERVAL` literal) | fail-closed ERROR naming the file, line, and the literal text found, wording DISTINCT from `non_daily_literal`'s message (FR-004; Edge Cases) |

Exactly one of these three values is assigned per qualifying `generate_series`
call; there is no fourth "unknown/skip" outcome for the step (Principle I: a
fail-closed rule must not let an unclassifiable step pass by default).

## 4. Bounds-order check (in-process value, never persisted)

| Field | Type | Notes |
|-------|------|-------|
| `both_literal` | `bool` | true only when BOTH `start_arg_text` and `end_arg_text` are literal date values (any dialect spelling of a bare date literal) |
| `order_violation` | `bool \| None` | `None` when `both_literal` is `False` (check does not fire -- FR-005, US2 Acceptance Scenario 3); otherwise `True` when the parsed `start` date is chronologically AFTER the parsed `end` date, else `False` |

When `order_violation` is `True`: fail-closed ERROR naming the file, line, and
BOTH literal values in the order given (start, then end) (FR-005; US2). When
`both_literal` is `False`, this check contributes no Finding either way -- a
non-literal bound is not statically comparable and is never treated as a
violation by default (Edge Cases).

## 5. Pending-live coverage record (a `Finding`, `Severity.INFO`)

Emitted once per qualifying `generate_series` call that CLEARS the step check
(daily) and the bounds-order check where it applies (not reversed, or not
applicable because a bound is non-literal) -- FR-007.

| Field | Value |
|-------|-------|
| `rule_id` | `"HR8"` |
| `severity` | `Severity.INFO` |
| `message` | States that live date-coverage against the fact's actual span is PENDING `retail validate` (V-RC15); explicitly asserts no coverage fact. MUST NOT contain "covers", "complete", "gap-free", or equivalent coverage-proof language (FR-007; FR-008; SC-004) |
| `locator` | `f"{file}:{call_line}"` |

This record is emitted REGARDLESS of whether the bounds are literal or
fact-derived (US3 Acceptance Scenario 3) -- a fact-derived bound narrows drift
RISK but is never treated as a coverage PROOF.

## 6. HR8 Finding (the only output shape; reuses the existing `Finding` dataclass)

All HR8 output is an instance of the ALREADY-EXISTING, UNCHANGED
`Finding(rule_id, severity, message, locator)` dataclass
(`src/retail/core.py`). No new dataclass, TypedDict, or serialization shape is
introduced by this feature.

| `rule_id` | `severity` | Fires when | FR |
|---|---|---|---|
| `HR8` | `ERROR` | step is a literal `INTERVAL` other than `'1 day'` | FR-003 |
| `HR8` | `ERROR` | step is present but not a classifiable literal `INTERVAL` | FR-004 |
| `HR8` | `ERROR` | both bounds are literal dates and start is after end | FR-005 |
| `HR8` | `INFO` | the call cleared all applicable ERROR checks above | FR-007 |

A single qualifying `generate_series` call MAY produce more than one Finding
in the same run (e.g. an unclassifiable step AND, independently, nothing to
say about bounds since one side wasn't literal -- in that case just the one
ERROR); the INFO record (row 4) is emitted ONLY when no ERROR fired for that
call, since FR-007 explicitly scopes to calls that "pass" the earlier checks.

## Explicitly NOT modeled (Principle VIII deferral; hard rule #9)

- **No live coverage entity.** There is no "fact min/max date" field, no
  "matched/unmatched days" count, and no comparison to any live database value
  anywhere in this data model -- that is `V-RC15`'s (`src/retail/validate.py`)
  exclusive domain, unchanged by this feature (FR-006).
- **No score, ratio, or tally field.** No entity above carries a percentage,
  confidence, health, or completeness number (hard rule #9; FR-008).
- **No new manifest/declaration file schema.** Unlike 087/HR1's
  `conformed-dimension-map.yaml`, HR8 reads and writes nothing outside the
  already-committed `warehouse/migrations/*.sql` text it inspects (FR-010).
