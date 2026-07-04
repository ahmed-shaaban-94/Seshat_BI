# Phase 1 Data Model: Consumer-Facing Generated Data Dictionary

**Feature**: `101-consumer-data-dictionary` | **Date**: 2026-07-04

Generic entity/artifact shapes this feature introduces (Principle VII: no
C086/`retail_store_sales` specifics baked into a fixed field or label -- any
concrete value below is a cited, filled illustration only).

## Entity 1 -- Consumer Data Dictionary (the document)

The per-table, plain-language document this module writes. One per table per
run, at a fixed path.

| Field | Type | Description |
|---|---|---|
| `table_id` | string | The target table identifier (e.g. `<schema>.<table>` or the mapping-folder name), resolved generically per FR-015. |
| `generated_on` | date | The date this run produced the document (informational only; not a readiness timestamp, not a score). |
| `gold_source` | repo-relative path | The committed gold migration SQL file this run resolved (FR-003), or an explicit gap if none exists (FR-014). |
| `source_map_source` | repo-relative path | The committed `mappings/<table>/source-map.yaml` this run resolved. |
| `metrics_source_dir` | repo-relative path | The committed `mappings/<table>/metrics/` folder this run resolved. |
| `column_entries[]` | list of **Gold Column Entry** | One per deployed gold-star column, in gold-migration-SQL column definition order (FR-001, Clarification Q2). |
| `metric_entries[]` | list of **Metric Entry** | One per metric contract file found, in lexical filename order (FR-001, Clarification Q2). |
| `document_level_gaps[]` | list of **Gap Marker** | Table-wide gaps that are not specific to one column or metric (e.g. "no gold migration SQL found for this table" -- FR-014). |

**Invariants** (checkable, no exceptions):

- Exactly one document per table per run; regenerating overwrites only this
  module's own output path (FR-018; spec edge case "regenerated dictionary").
- Every `column_entries[]` row and every `metric_entries[]` row cites at least
  one repo-relative source path (FR-007).
- Contains NO numeric confidence/health/maturity score and NO completeness
  count or "N of M" tally anywhere (FR-013, hard rule #9).
- Contains NO sentence describing a column's or metric's meaning that does not
  trace to a committed source (SC-002).
- Never lists a gold column that source-map.yaml marks `pii: true` and dropped,
  or any other column never materialized to gold (FR-010).

## Entity 2 -- Gold Column Entry

One row per deployed gold-star column (as declared in the committed gold
migration SQL's `CREATE TABLE` statements).

| Field | Type | Description |
|---|---|---|
| `column_name` | string | The gold column's name, exactly as declared in the gold migration SQL. |
| `gold_table` | string | The gold table/dim/fact this column belongs to (e.g. `gold.<fact_or_dim_name>`). |
| `definition_order` | integer | This column's position in the gold migration SQL's `CREATE TABLE` statement (drives Entity 1's `column_entries[]` ordering -- FR-001/Q2). |
| `meaning_state` | enum: `cited` \| `gap` | Whether a committed consumer-facing or mapping-rationale meaning was found (FR-005/FR-008). |
| `meaning_text` | string or null | When `meaning_state = cited`: the source-map `reason` text quoted VERBATIM (FR-005) -- never paraphrased, never simplified, never generated (pending FR-008/Q1's OPEN owner ruling). Null when `meaning_state = gap`. |
| `meaning_source_path` | repo-relative path or null | The exact `mappings/<table>/source-map.yaml` location the `meaning_text` was quoted from (FR-007). Null when `meaning_state = gap`. |
| `gap` | **Gap Marker** or null | Present only when `meaning_state = gap` (FR-008: no source-map column entry at all, or a source-map entry with no `reason` recorded). |
| `drift_note` | string or null | Present only when the gold migration SQL and `source-map.yaml` disagree on this column's presence or name (FR-019) -- records the discrepancy; never silently resolves it by preferring one source. |

**Invariants**:

- Every gold-star column that is actually deployed appears EXACTLY ONCE
  (FR-001 Acceptance Scenario 1); no column is silently omitted because it
  lacks a committed meaning (User Story 2 Acceptance Scenario 2 -- a missing
  meaning is a gap entry, not an omission).
- **Join basis (FR-005, Clarification Q5), fixed and non-negotiable**: a gold
  column is matched to its `source-map.yaml` entry ONLY by the source-map's
  own recorded `source_name` (fact / degenerate-dim columns), or by the
  `gold_star` dimension's listed attribute name (dimension attributes) --
  NEVER by position (e.g. "3rd column in the CREATE TABLE") and NEVER by
  fuzzy/approximate string matching on the column name. A gold column with no
  such matching record -- a surrogate key generated only in the gold
  migration, or an RC15 calendar-derived `dim_date` attribute such as
  `month_name` / `day_name` / `is_weekend` -- has no candidate join at all and
  falls straight through to `meaning_state = gap` (FR-008); it MUST NOT be
  matched positionally to the "nearest" source-map entry as a fallback.
- `meaning_state = cited` implies `meaning_text` and `meaning_source_path` are
  both non-null; `meaning_state = gap` implies `meaning_text` and
  `meaning_source_path` are both null and `gap` is non-null.
- `meaning_text`, when present, is a substring/verbatim quote of the committed
  `reason` field -- never a rephrasing (FR-005, FR-008 verbatim-cite-or-gap
  default).

## Entity 3 -- Metric Entry

One row per metric contract file found under `mappings/<table>/metrics/`.

| Field | Type | Description |
|---|---|---|
| `metric_name` | string | The contract's `name` field. |
| `file_order` | integer | This file's position in the lexical (filename) ordering of `mappings/<table>/metrics/*.yaml` (drives Entity 1's `metric_entries[]` ordering -- FR-001/Q2). |
| `formula_intent` | string or null | The contract's `formula_intent` text, carried forward VERBATIM (FR-006). Null only when the contract is unreadable (see `gap` below). |
| `readiness_status` | string or null | The contract's own recorded `readiness.status` value (e.g. `pass`, `not_started`), surfaced as-is (FR-006). Null only when the contract is unreadable. |
| `approved` | boolean | Derived display flag: `true` when `readiness_status == "pass"`, else `false` -- drives the "clearly marked as not yet approved" requirement (FR-006); never itself a numeric score. |
| `source_path` | repo-relative path | The exact `mappings/<table>/metrics/<Metric>.yaml` path (FR-007). Present even when the file is unreadable (the path that was attempted). |
| `gap` | **Gap Marker** or null | Present only when the metric contract file referenced is missing or unreadable (User Story 2 Acceptance Scenario 3, FR-008-style discipline extended to metrics). |

**Invariants**:

- Every metric contract file found under `mappings/<table>/metrics/*.yaml` is
  listed exactly once, approved and pending alike -- never filtered to
  `pass`-only (FR-004, FR-006, Clarification Q4).
- A metric whose `readiness_status` is not `pass` is never rendered in a way
  that implies it is approved (FR-006, `approved = false` in that case).
- An unreadable/missing contract file still produces a row (with `gap` set),
  never a silent drop (User Story 2 Acceptance Scenario 3).

## Entity 4 -- Gap Marker

An explicit, named record that a column or metric (or the document as a
whole) has no committed consumer-facing meaning available, or that a
committed source disagrees with another, or is missing/unreadable. Never
filled with invented prose (Clarification Q3 -- the minimum shape every gap
must carry).

| Field | Type | Description |
|---|---|---|
| `label` | constant string `"GAP:"` | The fixed, greppable prefix every gap marker starts with (Clarification Q3; enables `grep -n "GAP:"` verification, per `quickstart.md`). |
| `subject` | string | The column name, metric name, or `"document"` (for a table-wide gap) this gap concerns. |
| `reason_code` | enum: `no_source_map_entry` \| `no_reason_recorded` \| `contract_missing_or_unreadable` \| `no_gold_migration_found` \| `source_disagreement` | A closed set naming WHY the gap exists -- never a free-text guess standing in for one of these. |
| `checked_paths[]` | list of repo-relative paths | The path(s) that were checked and found missing, empty, unreadable, or disagreeing (FR-007, FR-008, FR-019; Clarification Q3). |

**Invariants**:

- `reason_code` is always one of the closed enum values above -- a sixth,
  ad hoc reason would itself be a template drift and is out of scope for this
  version (Principle VI: extend deliberately, not silently).
- `checked_paths[]` is never empty -- a gap always names what was looked for
  and where (SC-002's "0 entries state a meaning ... not present in a
  committed source" extends symmetrically: a gap never omits its own
  evidence trail either).
- A gap marker NEVER contains a percentage, a count, or any numeric
  confidence/health/maturity value (hard rule #9, FR-013).

## Ordering rules (Clarification Q2, fixed by this data model)

1. `column_entries[]`: gold-migration-SQL column DEFINITION order (the order
   columns appear inside each table's `CREATE TABLE` statement, table-by-table
   in the migration file's own top-to-bottom order). Deterministic and
   byte-stable for a fixed source state (no invented business-relevance
   ranking).
2. `metric_entries[]`: lexical (alphabetical) order of
   `mappings/<table>/metrics/*.yaml` filenames.

## What this data model deliberately does NOT include

- No `confidence`, `health`, `maturity`, `completeness_pct`, or any numeric
  field of that shape anywhere (hard rule #9).
- No `approved_by` / `approval` field -- this module records a metric
  contract's OWN recorded `readiness.status`; it never grants or witnesses an
  approval itself (FR-009, FR-012).
- No `blocking_reasons[]` or `next_action` field -- those belong to
  `readiness-status.yaml` (Core Authority), not this optional companion
  document (FR-012).
- No live-schema field (e.g. `actually_deployed: true/false` from a database
  catalog read) -- live reconciliation is explicitly out of scope/PENDING
  (Principle VIII; `research.md` section 3).
