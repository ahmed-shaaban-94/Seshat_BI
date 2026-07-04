# Phase 0 Research: Cross-Table Column-Level Lineage / Impact Analysis

**Feature**: `099-cross-table-lineage-impact` | **Date**: 2026-07-04

## Purpose

Ground the design in what already SHIPPED (reuse, do not re-derive) and what is
DEFERRED (do not assume). Every claim below cites a real repo path.

## 1. Precedent survey -- what ships today and what this feature reuses

### 1.1 The hand-authored proof this feature generalizes

- `docs/demo/net-sales-end-to-end-readiness-trace.md` (shipped). A human-written,
  single-KPI trace through business question -> contract -> required fields ->
  source coverage -> blockers -> SQL/gold -> DAX -> dashboard -> readiness gates,
  each step tagged with one of three evidence tiers ("Proven (artifact present)",
  "Documented (not runtime-enforced)", "Needs real data / live run"). This
  feature's evidence-state vocabulary (PROVEN / UNRESOLVED / GAP, FR-016) is a
  direct structural descendant of this trace's tiering, narrowed to the
  cross-artifact chain the trace itself calls "Steps 2/6/7/8" (contract -> gold
  table/SQL -> DAX measure -> dashboard usage). The trace is NOT retro-edited or
  superseded (spec boundary section, Assumptions).

### 1.2 The four/five upstream-to-final artifact families (read-only inputs)

- `mappings/<table>/source-map.yaml` -- shipped mapping-gate artifact (F006/F007,
  `specs/007-table-onboarding-wizard/`, `specs/008-business-meaning-registry/`).
  Filled instance: `mappings/retail_store_sales/source-map.yaml`.
- `warehouse/migrations/*.sql` -- shipped silver/gold SQL authored by
  `retail-build-warehouse` (spec `006-warehouse-builder`). Filled instance:
  `warehouse/migrations/0003_create_silver_retail_store_sales.sql` and
  `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`.
- `mappings/<table>/metrics/*.yaml` -- shipped metric-contract store (F009, spec
  `010-metric-contract-store`). Filled instances:
  `mappings/retail_store_sales/metrics/TotalSales.yaml`,
  `AvgTransactionValue.yaml`, `DiscountedTransactionRate.yaml`,
  `TotalQuantity.yaml`, `TransactionCount.yaml`.
- `powerbi/*.SemanticModel/definition/tables/*.tmdl` -- shipped, committed TMDL
  under Semantic Model Ready (F010, spec `011-semantic-model-readiness`). Filled
  instance: `powerbi/RetailStoreSales.SemanticModel/definition/tables/gold
  fct_sales_rss.tmdl`.
- `templates/visual-contract-binding-map.md` -- the dashboard-design skill's
  binding map (F011/F012, `specs/012-dashboard-design-skill/`,
  `specs/013-data-quality-control-room/`) recording `visual_id -> bound_contract
  (approved) -> semantic_model_field(s)`. This is the fifth and final hop this
  feature reads WHEN a table has reached Dashboard Ready; earlier tables record
  this hop as a GAP, not an error (spec Assumptions, edge cases).

### 1.3 Close neighbours to stay distinct from (spec boundary section, restated for the plan)

| Neighbour | Shipped at | What it does | Why this feature is not a restatement |
|---|---|---|---|
| Spec 044 KPI Derivation-Lineage | `specs/044-kpi-derivation-lineage/` (ratified, no runtime code) | Authors a `Derives from` PROSE section inside a metric contract: METRIC-TO-METRIC conceptual derivation (e.g. Net Sales derives from Gross Sales + Discount Amount) | This feature derives a PHYSICAL cross-ARTIFACT chain (column -> SQL -> contract -> measure -> visual) from structural references in committed files, generated not authored; it cites a 044 edge at the contract hop when present but never edits/re-derives it |
| F014 Source Drift Detector | spec `015-source-drift-detector` (shipped) | DETECTS that one source's shape/semantics drifted from its recorded profile; turns that into Source Ready evidence/blockers | This feature does not detect drift or compare to a baseline; it is the DOWNSTREAM-SCOPING half -- given a column F014 flagged, shows what sits downstream so a reviewer knows what to re-check |
| F012 Data Quality Control Room | spec `013-data-quality-control-room` (shipped), credited in `docs/decisions/0004-readiness-status-location.md` for the cross-table roll-up role | Cross-table, read-only aggregator of DATA-QUALITY findings/blockers ("worst first" triage) | This feature aggregates LINEAGE EDGES, a different evidence category; it does not read Control Room's findings and Control Room gains no lineage view from this feature |
| Net-Sales trace | `docs/demo/net-sales-end-to-end-readiness-trace.md` (shipped) | The single hand-authored proof for exactly one KPI | This feature generalizes the trace's SHAPE into a regeneratable template for any column/KPI; supersedes nothing, retro-edits nothing |
| OpenLineage | Evaluated in `docs/decisions/0013-bi-tool-adapter-shortlist.md` (line 41: "column-level lineage ... transform provenance ... borderline ... client + external backend ... **DEFER** (emitter, not a gated reader; external-service boundary; duplicates F014)") | External lineage-emitter service/client | This feature is not a revival: it is a static reader over already-committed repo text (Principle VIII), never a running emitter, never an external-service client, adds no new dependency |

### 1.4 The Product Module precedent this feature's shape follows

- `.claude/skills/approval-evidence-pack/SKILL.md` (F035, spec
  `063-approval-evidence-pack`, docs-only skill + `templates/approval-evidence-
  pack.md`) is the most recent read-only-input / single-artifact-output Product
  Module: it declares a filled `Module Contract` block (per
  `templates/module-contract.md`) embedded directly in `SKILL.md` rather than as
  a separate file, states its authority category (`Product Module`) and
  capability level (`artifact-writing`), enumerates Core Authority it reads,
  forbidden operations, and an honest-state table mapping each missing-input
  situation to its handling. This feature's `SKILL.md` follows that exact shape,
  including declaring the same `artifact-writing` capability level (see the
  Capability-level note immediately below for why).
- `docs/architecture/product-modules.md` (F024) is the normative five-category /
  three-capability-level contract this feature's module declares against.
  **Capability-level note**: the F024 contract's three levels are `read-only |
  artifact-writing | execution-capable`. The shipped Product Modules that write
  anything (F027, F028, F035) all declare `artifact-writing`, because "MAY write
  derived evidence" is precisely what `artifact-writing` means. This feature
  also writes one derived artifact per run
  (`mappings/<table>/lineage-column-<column>.md` /
  `lineage-metric-<Metric>.md`, FR-014) and reads only Core Authority -- so per
  the F024 matrix it is `artifact-writing`, matching F027/F028/F035, not
  `read-only` (which would forbid writing anything at all, including its own
  output). The spec's characterization of this feature as a "read-only
  aggregator" (feature framing / SCOPE GUARD) describes its INPUT discipline
  (reads only, invents no truth) and is preserved verbatim in that sense; the
  F024 CAPABILITY LEVEL field is the separate, precise vocabulary and is
  `artifact-writing` (see Constitution Check in plan.md).

### 1.5 Roadmap F-number -- plan-time proposal, not a roadmap-ledger edit

- Highest confirmed SHIPPED Product Module: **F035** (Approval Evidence Pack,
  `docs/roadmap/roadmap.md` line ~195, "Authored 2026-07-02").
- Highest confirmed SHIPPED F-number of any category: **F038** (Tabular Editor
  BPA spike, an Execution Adapter, `docs/roadmap/roadmap.md` line 40, "SHIPPED
  (six-gate PASS)").
- `grep -n "F036\|F037\|F039" docs/roadmap/roadmap.md specs/*/spec.md` returns no
  hits: F036 and F037 are not accounted for in the committed roadmap ledger, and
  F039 is unclaimed.
- Per the spec's own instruction ("the exact number is a roadmap-ledger edit
  recorded at plan time, not invented here, matching the spec 044 / spec 063
  precedent of not self-assigning a number"), this research/plan PROPOSES
  **F039** as the next free Product Module slot but does NOT edit
  `docs/roadmap/roadmap.md` in this stage -- that file is a shared surface 19
  parallel in-flight features touch, and editing it here risks a collision this
  spec's own collision-avoidance allocation exists to prevent. The roadmap-row
  reconciliation (confirming F039, or resolving what F036/F037 were, and adding
  the F035-style row) is an INTEGRATION-TIME edit for whoever merges this
  feature, not a Plan-stage deliverable.

## 2. Input-source confirmation

The five artifact families this module reads are confirmed to exist, on-disk,
with real filled instances, as of this research:

| # | Artifact family | Confirmed present (filled instance) |
|---|---|---|
| 1 | `mappings/<table>/source-map.yaml` | `mappings/retail_store_sales/source-map.yaml` |
| 2 | `warehouse/migrations/*.sql` | `warehouse/migrations/0003_create_silver_retail_store_sales.sql`, `0004_create_gold_retail_store_sales_star.sql` |
| 3 | `mappings/<table>/metrics/*.yaml` | `mappings/retail_store_sales/metrics/TotalSales.yaml` (+ 4 siblings) |
| 4 | `powerbi/*.SemanticModel/definition/tables/*.tmdl` | `powerbi/RetailStoreSales.SemanticModel/definition/tables/gold fct_sales_rss.tmdl` |
| 5 | Dashboard visual-to-contract binding | `templates/visual-contract-binding-map.md` (generic template exists; a filled per-subject-area copy is produced by the dashboard-design skill once a table reaches Dashboard Ready -- for `retail_store_sales` this hop is expected to be a recorded GAP today, since a filled binding map for that table was not found on disk at research time; the module records that as a gap, never an error, per spec Assumptions) |

No sixth artifact family is introduced. No new file format is invented; the
module is a reader over these five existing shapes plus the spec-044 contract
`Derives from` prose (cited, never re-derived, section 1.3).

## 3. Deferred capabilities NOT assumed (explicit non-goals for this design)

- **F016 (Power BI execution adapter)** does not exist and is not invoked. No
  live PBIP read, no Power BI Desktop automation, no DAX execution.
- **F031-F033 (adapter maintenance automation)** are spec-only with no consumer
  (`docs/roadmap/roadmap.md` Tier 5 rows for F031/F032/F033: "no consumer yet").
  This feature does not invoke or depend on them.
- **No live database connection.** `retail validate` (DB-connected, needs the
  `db` extra + a DSN) is out of scope; the module reads committed repo text only
  (Principle VIII, static-first). Any live-DB surface this feature might one day
  want (e.g. confirming a column exists in a real source) is explicitly deferred
  and, if ever added, would be a separate PENDING-marked surface, not assumed
  here.
- **No new `retail check` rule / rule-id / gate.** Per the collision-avoidance
  allocation and FR-013, this feature claims no `src/retail/rules/` entry and
  adds no static-check rule. `retail check` is unaffected by this feature.
- **No graphical/visual rendering of the lineage graph.** Output is a markdown
  artifact (ordered hop list), not a diagram, graph database, or UI (spec
  Assumptions: "a graphical/visual rendering of the lineage graph ... [is] OUT
  OF SCOPE").
- **No reverse (upstream-only) lineage query.** Only the fixed forward order
  (source-map -> SQL -> contract -> measure -> visual) is in scope (spec
  Assumptions).
- **No name-similarity auto-resolution.** FR-010 is an OPEN Principle-V owner
  ruling; until ruled, every contract<->gold-column or measure<->contract link
  without an explicit machine-readable cross-reference is UNRESOLVED/candidate
  only, never promoted to proven by any heuristic this design introduces.
- **No score, count, or health value of any kind** (hard rule #9): no blast
  radius number, no "N artifacts affected" count, no confidence/maturity value.

## 4. Design conclusion feeding Phase 1

The module is a **read-only-input, single-derived-artifact-output** Product
Module (F024 capability level `artifact-writing`), implemented as a
`.claude/skills/` skill plus one generic `templates/` file -- no runtime
executor, no rule-id, no schema/DB touch. It reuses the Net-Sales trace's
evidence-tier vocabulary (renamed PROVEN/UNRESOLVED/GAP per FR-016), reuses the
F035 module-contract-embedded-in-SKILL.md shape, and reads the five artifact
families already confirmed present above. Phase 1 (`data-model.md`,
`quickstart.md`, `plan.md`) proceeds on this basis.
