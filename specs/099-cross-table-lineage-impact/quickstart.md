# Quickstart: Cross-Table Column-Level Lineage / Impact Analysis

**Feature**: `099-cross-table-lineage-impact` | **Date**: 2026-07-04

How an agent or developer exercises this feature once built (`.claude/skills/
cross-table-lineage/SKILL.md` + `templates/lineage-trace.md`). This walkthrough
uses `retail_store_sales` only as a cited, already-committed illustrative
instance (Principle VII) -- the skill itself resolves any generic starting
point.

## Prerequisites

- The repo working tree is checked out locally (no DB, no live Power BI, no
  network -- Principle VIII).
- The starting point already exists as either:
  - a row in a committed `mappings/<table>/source-map.yaml` (column-rooted), or
  - a committed `mappings/<table>/metrics/<Metric>.yaml` file (metric-rooted).
- Nothing else needs to be "ready" -- a table mid-journey through the seven
  readiness stages is the NORMAL case; partial chains are expected, not an
  error (spec Overview).

## Scenario A -- trace one column's downstream reach (User Story 1)

1. Ask the agent: "generate the lineage/impact artifact for
   `retail_store_sales`'s `net_amount` column" (or any real
   `schema.table.column`).
2. The agent invokes the `cross-table-lineage` skill with the `column` starting
   point.
3. The skill:
   a. Resolves the column against `mappings/retail_store_sales/source-map.yaml`.
      If not found, it records a top-level blocker and STOPS (FR-015) -- no
      fabricated chain.
   b. Walks the fixed forward order: source-map -> migration SQL
      (`warehouse/migrations/*.sql`) -> metric contract
      (`mappings/retail_store_sales/metrics/*.yaml`) -> TMDL measure
      (`powerbi/RetailStoreSales.SemanticModel/definition/tables/*.tmdl`) ->
      dashboard visual binding (a filled `visual-contract-binding-map.md` copy,
      if one exists for this table).
   c. For each hop, records `proven` (explicit committed reference cited),
      `unresolved` (both sides exist, no explicit link -- FR-010's fail-safe),
      or `gap` (no committed artifact yet -- FR-008), never inventing a fourth
      state.
   d. Writes exactly one file:
      `mappings/retail_store_sales/lineage-column-net_amount.md`.
   e. STOPS. It edits nothing else.
4. **Verify** (mirrors the F028/F035 "composes-only" check):
   ```
   git status
   ```
   Expect exactly one new/untracked file:
   `mappings/retail_store_sales/lineage-column-net_amount.md`. No existing
   artifact (source-map, migration SQL, metric contract, TMDL, readiness-
   status.yaml) shows as modified.
5. **Inspect the output** for the SC-002/SC-003/SC-004 negative checks:
   - Every hop marked `proven` cites a real repo-relative path that exists on
     disk (SC-002).
   - No numeric blast-radius score, no "N artifacts affected" count, no
     confidence/health/maturity value anywhere in the file (SC-003).
   - No verb of obligation ("must", "should", "needs to") applied to any
     downstream item (SC-004).

## Scenario B -- trace one KPI's full chain (User Story 2)

1. Ask the agent: "generate the lineage artifact for the
   `TotalSales` metric contract" (or any other committed
   `mappings/<table>/metrics/<Metric>.yaml`).
2. The agent invokes the same skill with the `metric` starting point.
3. The chain starts at hop 3 (metric contract) since a metric-rooted run has no
   natural upstream source-map/SQL entry point of its own to start from; the
   module still records the upstream (source-map, migration SQL) side as
   PROVEN/UNRESOLVED/GAP by tracing backward-then-forward only far enough to
   cite the contract's own required-field origin -- it does NOT run a full
   reverse-lineage query (that is out of scope; see spec Assumptions).
4. Output: `mappings/<table>/lineage-metric-TotalSales.md`.
5. **Special check when the starting contract is Net Sales** (SC-006): if a
   table in the repo has a Net Sales-equivalent contract, generate its lineage
   artifact and compare its cited hops against
   `docs/demo/net-sales-end-to-end-readiness-trace.md`. The generated artifact
   must not CONTRADICT the hand-authored trace's cited evidence (e.g. it must
   not claim a different gold table or a different TMDL measure than the trace
   already cites). It is fine -- expected, even -- for the generated artifact
   to have LESS narrative color than the hand-authored trace; it must not
   assert something the trace's citations disagree with.

## Scenario C -- scope "what to re-review" without deciding it (User Story 3)

1. After Scenario A or B produces an artifact with a non-trivial
   `downstream_set` (see `data-model.md` Entity 4), a reviewer reads that list
   as the CANDIDATE set.
2. The reviewer (a human) or a separate F014 drift-detector run decides,
   OUTSIDE this artifact, what actually needs re-work.
3. **Verify** the artifact itself carries no recommendation: grep the
   generated file for obligation verbs ("must", "should", "needs to",
   "requires re-review") applied to any downstream item -- there should be
   zero matches (SC-004). The artifact says "is downstream of" / "cites",
   never "must be re-reviewed."

## Edge cases to exercise once built

- **Unresolved starting point**: ask for the lineage of a column that does not
  appear in any committed `source-map.yaml`. Expect a top-level blocker naming
  the missing row, and NO downstream chain (FR-015).
- **Name-mismatch hop**: a metric contract whose required-field name does not
  textually match its gold column name. Expect `evidence_state: unresolved`
  with a `note` explaining the mismatch -- never silently promoted to `proven`
  (FR-005/FR-010, the OPEN owner ruling's fail-safe default).
- **Two measures, one column**: two TMDL measures in different
  `*.SemanticModel/` folders both reference the same gold column. Expect BOTH
  surfaced as separate hops -- the module does not arbitrarily pick one (spec
  edge cases).
- **Pre-Dashboard-Ready table**: a table with contracts and a TMDL measure but
  no filled `visual-contract-binding-map.md` copy yet. Expect hop 5
  (`dashboard_visual`) recorded as `gap`, not an error, not a fabricated
  visual reference (Acceptance Scenario 2, User Story 1).
- **Regeneration**: run the same lineage query twice, after renaming a TMDL
  measure in between. Expect the second run to reflect only the CURRENT
  committed state -- it carries no memory of the prior run's hop content and
  makes no "this changed" claim (that comparison is F014's job, spec edge
  case).

## What this feature does NOT let you do (do not attempt to force these)

- It will not connect to a database or run SQL/DAX to confirm a hop is
  reconciled -- that is `retail validate` (DB-connected, live) or `retail
  value-check` territory, out of scope here (FR-002).
- It will not tell you a downstream item "must" be re-reviewed, "is broken," or
  "is at risk" -- only that it is reachable, with its citation (FR-007, User
  Story 3).
- It will not auto-promote a name-similarity match to a proven hop -- FR-010 is
  an OPEN owner ruling; until answered, every such link stays candidate-only
  (fail-safe, not a temporary gap in the build).
- It will not move any readiness stage, grant any approval, or edit any
  artifact besides its own generated lineage file (FR-009).
- It will not emit a blast-radius score, a completeness count, or a
  confidence/health/maturity value under any circumstance (hard rule #9,
  FR-006).
