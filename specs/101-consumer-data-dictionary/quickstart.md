# Quickstart: Consumer-Facing Generated Data Dictionary

**Feature**: `101-consumer-data-dictionary` | **Date**: 2026-07-04

How an agent or developer exercises this feature once built
(`.claude/skills/consumer-data-dictionary/SKILL.md` +
`templates/consumer-data-dictionary.md`). This walkthrough uses
`retail_store_sales` only as a cited, already-committed illustrative instance
(Principle VII) -- the skill itself resolves any generic table identifier.

## Prerequisites

- The repo working tree is checked out locally (no DB, no live Power BI, no
  network -- Principle VIII).
- The target table has reached Gold Ready: a committed gold migration SQL
  file exists (`warehouse/migrations/*_create_gold_<table>*.sql`). If it does
  not, the module still runs -- it records a document-level gap rather than
  refusing outright (FR-014) -- but the output will be mostly gaps.
- The table's `mappings/<table>/source-map.yaml` and
  `mappings/<table>/metrics/*.yaml` exist (they normally do once a table has
  cleared Mapping Ready; a metric folder with zero files is valid and simply
  yields zero metric entries).

## Scenario A -- generate the dictionary for a fully mapped, gold-built table (User Story 1)

1. Ask the agent: "generate the consumer data dictionary for
   `retail_store_sales`" (or any real table identifier).
2. The agent invokes the `consumer-data-dictionary` skill with the table
   identifier.
3. The skill:
   a. Resolves `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`
      and reads every `CREATE TABLE` statement's column list, in file order
      (FR-003).
   b. Resolves `mappings/retail_store_sales/source-map.yaml` and, for each
      gold column, looks up the matching `columns[]` entry's `reason`
      (FR-005).
   c. Resolves `mappings/retail_store_sales/metrics/*.yaml` (all five files:
      `AvgTransactionValue.yaml`, `DiscountedTransactionRate.yaml`,
      `TotalQuantity.yaml`, `TotalSales.yaml`, `TransactionCount.yaml`) in
      lexical filename order, carrying forward each contract's
      `formula_intent` verbatim and its `readiness.status` (FR-004, FR-006).
   d. For each gold column with a `reason` on file, cites it verbatim with
      its source path. For any gold column with NO source-map entry or an
      entry with no `reason` (e.g. a surrogate key generated only in the gold
      migration itself), records a `GAP:` marker naming the column and the
      path checked (FR-008, User Story 2).
   e. Writes exactly one file:
      `mappings/retail_store_sales/consumer-data-dictionary.md`.
   f. STOPS. It edits nothing else.
4. **Verify** (mirrors the F028/F035/F039 "composes-only" check):
   ```
   git status
   ```
   Expect exactly one new/untracked file:
   `mappings/retail_store_sales/consumer-data-dictionary.md`. No existing
   artifact (`source-map.yaml`, any `metrics/*.yaml`, the gold migration SQL,
   `readiness-status.yaml`, the handoff pack) shows as modified (FR-011, SC-004).
5. **Inspect the output** for the SC-002/SC-003 negative checks:
   - Every entry cites a real repo-relative path that exists on disk (SC-002).
   - No sentence states a meaning, status, or value not present in a
     committed source (SC-002).
   - No numeric confidence/health/maturity score and no "N of M" completeness
     count anywhere in the file (SC-003).

## Scenario B -- a column has no committed consumer-legible meaning (User Story 2)

1. Pick a gold column whose only committed meaning is a technical
   source-map `reason` written for the mapping-gate reviewer -- e.g.
   `transaction_id` in `mappings/retail_store_sales/source-map.yaml`, whose
   `reason` reads `"the grain key; unique on the data -> degenerate dim on
   the fact (RC14)"`.
2. Generate the dictionary (Scenario A steps).
3. **Verify** the `transaction_id` entry:
   - It quotes the `reason` VERBATIM, with the source-map path cited -- it
     does NOT contain a rewritten/simplified sentence like "a unique
     identifier for each transaction" that is not itself the quoted `reason`
     (FR-008's verbatim-cite-or-gap default; FR-008/Q1 remains an OPEN
     Principle-V question this build does not resolve).
4. Pick (or construct, for a test fixture) a gold column with NO
   corresponding `source-map.yaml` entry at all (e.g. a surrogate `_sk`
   column generated only inside the gold migration SQL).
5. **Verify** that column's entry is a `GAP:` marker naming the column and
   the source-map path that was checked and found to have no matching entry
   -- it is not silently omitted, and it does not contain any invented
   business definition (FR-008 Acceptance Scenario 2).
6. Pick (or construct) a metric contract file referenced by the table that is
   missing or unreadable (e.g. rename a `.yaml` file so the resolver's
   expected path 404s).
7. **Verify** that metric's entry is a `GAP:` marker citing the unreadable
   path, not a silent drop (User Story 2 Acceptance Scenario 3).

## Scenario C -- the same generator serves a second, differently-shaped table (User Story 3)

1. Generate the dictionary for `retail_store_sales` (Scenario A).
2. Generate the dictionary for a second, differently-mapped table that has
   also reached Gold Ready (any other committed
   `warehouse/migrations/*_create_gold_*.sql` + its own
   `mappings/<table>/metrics/*.yaml`).
3. **Verify**:
   - Each output resolves its OWN gold migration SQL and its OWN metrics
     folder -- the second table's dictionary contains none of the first
     table's column names, grain key, or metric names (SC-005).
   - The skill file and the generic template
     (`templates/consumer-data-dictionary.md`) contain no C086/
     `retail_store_sales`-specific column name, grain key, or metric name in
     any FIXED section label (SC-006) -- only this quickstart's own worked
     walkthrough (a doc, not the template) names `retail_store_sales` as a
     cited instance.

## Edge cases to exercise once built

- **Pre-Gold-Ready table**: ask for the dictionary of a table with no
  committed gold migration SQL yet. Expect a document-level `GAP:` marker
  naming the missing migration file, and NO fabricated column list drawn from
  a design or profiling document instead (FR-014).
- **Gold-SQL-vs-source-map disagreement**: a gold column present in the
  migration SQL with no textually matching `source-map.yaml` column name (or
  vice versa). Expect a `drift_note` / `GAP:` marker recording the
  disagreement -- never a silent pick of one source as authoritative
  (FR-019).
- **PII-dropped column**: a column marked `pii: true` and `decision: drop` in
  `source-map.yaml` (never reaches gold). Expect it to NOT appear in the
  dictionary at all -- the dictionary describes the DEPLOYED gold star only
  (FR-010).
- **Non-`pass` metric contract**: a metric contract whose `readiness.status`
  is `not_started` or another non-`pass` value. Expect it listed alongside
  approved metrics, but clearly marked as not yet approved -- never rendered
  as if it were approved (FR-006, Clarification Q4).
- **Regeneration**: run the same dictionary generation twice for the same
  table, after a metric contract's `formula_intent` changes in between.
  Expect the second run to overwrite only
  `mappings/<table>/consumer-data-dictionary.md` with the current committed
  state -- no other file is touched (spec edge case, FR-011).

## What this feature does NOT let you do (do not attempt to force these)

- It will not connect to a database or open a live Power BI/PBIP session to
  confirm a column's meaning or reconcile schema drift -- that is deferred
  (Principle VIII; a live-capable adapter such as F016 territory, invoked
  separately, not by this module) (FR-002).
- It will not generate, infer, or paraphrase a plausible business definition
  for a column whose only committed source is a technical mapping `reason` --
  FR-008/Q1 is an OPEN owner ruling; until answered, every such case falls
  back to verbatim-cite-or-gap (fail-safe, not a temporary gap in the build).
- It will not define, approve, revise, or resolve any metric's formula,
  grain, or business meaning, and will not resolve any open mapping question
  (FR-009).
- It will not write to, modify, or append to `source-map.yaml`, any
  `metrics/*.yaml` contract, the gold migration SQL, `readiness-status.yaml`,
  `unresolved-questions.md`, or the handoff pack -- its only write is its own
  generated dictionary file (FR-011).
- It will not move any readiness stage, add any `blocking_reasons[]` or
  `approvals[]` entry, or treat its own existence/absence as a gate
  requirement for any of the seven readiness stages (FR-012).
- It will not emit a numeric confidence/health/maturity score or a
  completeness count/percentage under any circumstance (hard rule #9,
  FR-013).
