# Phase 0 Research: Consumer-Facing Generated Data Dictionary

**Feature**: `101-consumer-data-dictionary` | **Date**: 2026-07-04

## Purpose

Ground the design in what already SHIPPED (reuse, do not re-derive) and what is
DEFERRED (do not assume). Every claim below cites a real repo path.

## 1. Precedent survey -- what ships today and what this feature reuses

### 1.1 The three artifact families this module composes from (read-only inputs)

- `warehouse/migrations/*_create_gold_<table>*.sql` -- shipped gold Kimball-star
  DDL authored by `retail-build-warehouse` (spec `006-warehouse-builder`).
  Filled instance: `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`
  (one fact `gold.fct_sales_rss` + four conformed dims + `gold.dim_date_rss`,
  columns declared in a fixed `CREATE TABLE` order). This is the authoritative,
  static source of a table's DEPLOYED gold columns (Principle VIII) -- never a
  live catalog read.
- `mappings/<table>/source-map.yaml` -- shipped mapping-gate artifact (F006/F007,
  `specs/007-table-onboarding-wizard/`, `specs/008-business-meaning-registry/`).
  Filled instance: `mappings/retail_store_sales/source-map.yaml`. Each column
  entry carries a `reason` string written for the mapping-gate reviewer (e.g.
  line 56: `"the grain key; unique on the data -> degenerate dim on the fact
  (RC14)"` for `transaction_id`) -- a technical mapping rationale, not
  consumer-facing prose. This module reads it read-only and never re-decides a
  mapping.
- `mappings/<table>/metrics/*.yaml` -- shipped metric-contract store (F009, spec
  `010-metric-contract-store`). Filled instances:
  `mappings/retail_store_sales/metrics/TotalSales.yaml` (+ `AvgTransactionValue`,
  `DiscountedTransactionRate`, `TotalQuantity`, `TransactionCount`). Each
  contract carries `formula_intent` (already consumer-legible prose, e.g.
  TotalSales.yaml line 7: "The total money taken across all retail
  transactions...") and a `readiness.status` field (`pass` / `not_started` /
  other). This module carries `formula_intent` forward VERBATIM and surfaces
  the recorded status -- it never defines, approves, or revises a metric.

### 1.2 Close neighbours to stay distinct from (spec boundary section, restated for the plan)

| Neighbour | Shipped at | What it does | Why this feature is not a restatement |
|---|---|---|---|
| F013 BI Handoff Pack, item (e) "Data dictionary" | `templates/handoff/bi-handoff-pack.md` (shipped, spec `014-bi-handoff-pack` per roadmap Tier naming) | A REQUIRED Publish Ready (Stage 7) gate section; audience is the data-owner/governance reviewer deciding whether to authorize release; a mismatch against the deployed schema FAILS the checklist (`publish-ready.md`) | This feature's dictionary is an OPTIONAL companion consumed AFTER publish, by the analyst querying self-serve; it adds NO gate, NO blocking reason, and NO required section to Publish Ready. It follows the `answerability-summary.md` precedent ("NOT a required Stage 7 artifact, not a gate") rather than extending the handoff pack. Composes from the SAME upstream truth but does not edit, re-render, or duplicate-govern F013's item (e). |
| F028 Evidence Pack Generator | `.claude/skills/evidence-pack-generator/` (shipped, spec `022-evidence-pack-generator`) | Composes a late-stage, 10-section READINESS evidence bundle (blockers, scorecards, approvals) for the Semantic Model -> Dashboard -> Publish window, written to `mappings/<table>/evidence-pack-index.md` / `evidence-pack-summary.md` | This feature composes a MEANING reference (what a column/measure means), not a readiness bundle; it carries no blocker list, no stage status, no approval slot, and is not part of any stage's `evidence[]` by default. Different output filename (FR-018), no collision. |
| `power-bi-docs` skill family | Referenced in this repo's Power BI CLI router (`~/.claude/CLAUDE.md` skill index) | Generates model documentation FROM A LIVE, CONNECTED semantic model (`pbi connect` required) | This feature is Principle-VIII static-first: it reads only committed, on-disk artifacts (gold migration SQL, metric-contract YAML, source-map YAML) and never opens a live Power BI or database connection; any live-schema drift against the deployed model is marked PENDING, never silently assumed reconciled. |

### 1.3 The Product Module precedent this feature's shape follows

- `.claude/skills/approval-evidence-pack/SKILL.md` (F035, spec
  `063-approval-evidence-pack`, docs-only skill + `templates/approval-evidence-
  pack.md`) is the most recent read-only-input / single-artifact-output Product
  Module: it declares a filled `Module Contract` block (per
  `templates/module-contract.md`) embedded directly in `SKILL.md`, states its
  authority category (`Product Module`) and capability level
  (`artifact-writing`), enumerates Core Authority it reads, forbidden
  operations, and an honest-state table mapping each missing-input situation to
  its handling. This feature's `SKILL.md` follows that exact shape.
- `.claude/skills/cross-table-lineage/` design intent (F039 proposal, spec
  `099-cross-table-lineage-impact`, plan authored the same day as this feature)
  is the closest sibling in this very batch: also a read-committed-artifacts,
  write-one-derived-markdown-file Product Module with an evidence-tier /
  gap-marker vocabulary and a "composes-only" `git status` verification pattern.
  This feature reuses that shape (module-contract-embedded-in-SKILL.md, no
  `contracts/` directory, gap markers instead of a graph). It does NOT reuse
  099's five-artifact-family input list (no TMDL, no dashboard visual-binding
  map here -- see section 2) and does NOT reuse 099's OPEN Principle-V question
  (that is FR-010 there; this feature's OPEN item is FR-008/Q1, an unrelated
  question about paraphrase-authoring latitude).
- **Capability-level note** (same reconciliation 099's research section 1.4
  already made, restated for this feature): the SCOPE GUARD text calls this a
  "read-only skill/template," describing its INPUT discipline (composes from
  committed artifacts only; never writes back to source-map, metrics, gold SQL,
  readiness-status, or the handoff pack -- FR-011). But FR-018 requires the
  module to WRITE its own generated file
  (`mappings/<table>/consumer-data-dictionary.md`). Per
  `docs/architecture/product-modules.md`'s three-level vocabulary, "MAY write
  derived evidence" is precisely `artifact-writing`, matching F027/F028/F035
  (and 099's F039 proposal). Declaring `read-only` at the F024 capability level
  would forbid writing any file at all, including this module's own output,
  contradicting FR-018. This plan's Module Contract therefore declares
  **capability level `artifact-writing`**, while the SCOPE GUARD's "read-only"
  language is preserved verbatim as the correct description of input
  discipline, not the F024 capability-level field.

### 1.4 Roadmap F-number -- plan-time proposal, not a roadmap-ledger edit

- Highest confirmed SHIPPED Product Module: **F035** (Approval Evidence Pack,
  `docs/roadmap/roadmap.md` line ~195, "Authored 2026-07-02").
- Highest confirmed SHIPPED F-number of any category: **F038** (Tabular Editor
  BPA spike, an Execution Adapter, `docs/roadmap/roadmap.md` line 40, "SHIPPED
  (six-gate PASS)").
- `grep -rn "F036\|F037\|F039\|F040" docs/roadmap/roadmap.md specs/*/spec.md
  specs/*/plan.md specs/*/research.md` (run at this research pass) shows: F036
  and F037 remain unaccounted for in the committed ledger; **F039 is already
  PROPOSED (not shipped, not ledger-edited) by the sibling in-flight feature
  `specs/099-cross-table-lineage-impact/research.md` section 1.5**, authored the
  same day; F040 has zero hits anywhere in the tree.
- To avoid proposing the SAME number as an in-flight sibling (both plans would
  otherwise race to claim F039 at integration time -- exactly the 19-parallel-
  feature collision this spec's own Collision-Avoidance Allocation exists to
  prevent), this research PROPOSES **F040** as this feature's next free Product
  Module slot. This is a PROPOSAL recorded here at plan time, not a
  roadmap-ledger edit; `docs/roadmap/roadmap.md` is a shared surface many
  parallel in-flight features touch, and editing it in this stage risks a
  collision. The actual roadmap row (confirming F040, or reconciling against
  whatever F036/F037/F039 turn out to be by the time this feature integrates) is
  left to integration time, matching the spec 044 / spec 063 / spec 099
  precedent of not self-assigning a ledger row.

## 2. Input-source confirmation

The three artifact families this module reads are confirmed to exist, on-disk,
with real filled instances, as of this research:

| # | Artifact family | Confirmed present (filled instance) |
|---|---|---|
| 1 | `warehouse/migrations/*_create_gold_<table>*.sql` | `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` (fact `gold.fct_sales_rss` + 4 dims + `gold.dim_date_rss`) |
| 2 | `mappings/<table>/source-map.yaml` (`columns[].reason`) | `mappings/retail_store_sales/source-map.yaml` (11 column entries, each with a `reason` string) |
| 3 | `mappings/<table>/metrics/*.yaml` (`formula_intent`, `readiness.status`) | `mappings/retail_store_sales/metrics/TotalSales.yaml` (+ 4 siblings: `AvgTransactionValue.yaml`, `DiscountedTransactionRate.yaml`, `TotalQuantity.yaml`, `TransactionCount.yaml`) |

No fourth artifact family is introduced. No new file format is invented; the
module is a reader over these three existing shapes. Unlike 099's five-hop
lineage chain, this feature does NOT read TMDL
(`powerbi/*.SemanticModel/definition/tables/*.tmdl`) and does NOT read the
dashboard visual-contract binding map -- neither is part of "what a column or
measure means," which is this feature's sole subject (spec Overview).

## 3. Deferred capabilities NOT assumed (explicit non-goals for this design)

- **F016 (Power BI execution adapter)** does not exist and is not invoked. No
  live PBIP read, no Power BI Desktop automation, no DAX execution, no `pbi
  connect` (FR-002).
- **No live database connection.** `retail validate` (DB-connected, needs the
  `db` extra + a DSN) is out of scope; the module reads committed repo text
  only (Principle VIII, static-first).
- **Static drift IS in scope; LIVE reconciliation is the deferred, PENDING
  half** (this is the one place this feature is NOT purely static, unlike
  099): when the committed gold migration SQL and the committed
  `source-map.yaml` disagree on a column's presence or name, that is a STATIC
  disagreement between two already-committed files -- the module DETECTS and
  RECORDS it as an explicit gap (FR-019; in scope, no live surface needed).
  What remains genuinely DEFERRED is reconciling the dictionary's column list
  against the ACTUALLY-DEPLOYED database schema (a live catalog read) -- that
  is explicitly out of scope per the spec's Assumptions ("deferred until a
  live-capable adapter such as F016/dashboard-design's live checks is invoked
  separately") and is never silently assumed reconciled just because the two
  static files happen to agree.
- **No new `retail check` rule / rule-id / gate.** Per the Collision-Avoidance
  Allocation and FR-017, this feature claims no `src/retail/rules/` entry and
  adds no static-check rule. `retail check` is unaffected by this feature.
- **No F031-F033 (adapter maintenance automation) dependency.** Spec-only, no
  consumer (`docs/roadmap/roadmap.md` Tier 5); this feature does not invoke or
  depend on them.
- **No generated business-meaning paraphrase (FR-008/Q1), pending an owner
  ruling.** Whether the module may ever generate a simplified, consumer-plain
  paraphrase of a column's existing technical source-map `reason` is an OPEN
  Principle-V question (Clarifications 2026-07-04 Q1). This design does NOT
  assume an answer and does NOT build a paraphrase-generation capability; until
  a named human (retail-kpi / data-owner) rules, the module applies the
  verbatim-cite-or-gap behavior only (FR-008, as amended).
- **No score, count, or health value of any kind** (hard rule #9): no
  completeness percentage, no "N of M" tally, no confidence/health/maturity
  value (FR-013).
- **No new readiness stage, no `blocking_reasons[]` entry, no `approvals[]`
  entry.** The dictionary is an optional companion; its absence is never a
  gate requirement for any of the seven stages (FR-012).

## 4. Design conclusion feeding Phase 1

The module is a **read-committed-input, single-derived-artifact-output**
Product Module (F024 capability level `artifact-writing`), implemented as a
`.claude/skills/` skill plus one generic `templates/` file -- no runtime
executor, no rule-id, no schema/DB touch. It reuses the F035/F039
module-contract-embedded-in-SKILL.md shape, reads the three artifact families
confirmed present above (gold migration SQL, source-map.yaml, metric-contract
YAML), applies the spec's four resolved Clarifications (Q2 ordering, Q3 gap-
marker shape, Q4 metric-inclusion scope) as fixed template rules, and carries
FR-008/Q1 forward as a genuinely OPEN Principle-V question rather than
resolving it. Phase 1 (`data-model.md`, `quickstart.md`, `plan.md`) proceeds on
this basis.
