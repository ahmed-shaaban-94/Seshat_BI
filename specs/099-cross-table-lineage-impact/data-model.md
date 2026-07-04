# Phase 1 Data Model: Cross-Table Column-Level Lineage / Impact Analysis

**Feature**: `099-cross-table-lineage-impact` | **Date**: 2026-07-04

Generic entity/artifact shapes only (Principle VII) -- no C086 / retail_store_sales
value is embedded here as anything other than a cited illustrative example.

## Entity 1 -- Starting point

The anchor the whole artifact is generated for. Exactly one of two shapes:

| Field | Type | Notes |
|---|---|---|
| `kind` | enum: `column` \| `metric` | which of the two starting-point identifiers this is (FR-001) |
| `identifier` | string | `column` kind: `<schema>.<table>.<column>` (e.g. cited instance: `bronze.pos.retail_store_sales.net_amount`, illustrative only). `metric` kind: `mappings/<table>/metrics/<Metric>.yaml` repo-relative path |
| `resolved` | boolean | whether the identifier was found in a committed source-map row (`column`) or exists as a committed contract file (`metric`) -- FR-015 |
| `resolution_blocker` | string \| null | when `resolved: false`, names the missing source-map row or contract path; null when resolved |

**Rule**: if `resolved: false`, the module records `resolution_blocker` as a
top-level blocker and produces NO downstream chain from this starting point
(FR-015). This is the only field that can short-circuit the rest of the shape.

## Entity 2 -- Hop

One stage in the fixed forward chain. The chain always has exactly five
possible hop slots, in this fixed order (FR-003); a given run may start
partway through the chain (a `metric`-kind starting point begins at hop 3, not
hop 1) and always proceeds forward, never backward (Assumptions: reverse
lineage is out of scope).

| Field | Type | Notes |
|---|---|---|
| `hop_index` | integer 1-5 | fixed order: 1 = source-map entry, 2 = migration SQL reference, 3 = metric contract, 4 = TMDL measure, 5 = dashboard visual binding |
| `hop_name` | enum | `source_map` \| `migration_sql` \| `metric_contract` \| `tmdl_measure` \| `dashboard_visual` |
| `evidence_state` | enum: `proven` \| `unresolved` \| `gap` | FR-016's three-tier vocabulary (mirrors the Net-Sales trace's tiers, renamed for this artifact) |
| `citation` | object \| null | present only when `evidence_state: proven` or `unresolved` (both sides exist); see Entity 3 |
| `note` | string | required when `evidence_state: gap` -- names what is missing (FR-008); optional free text otherwise (e.g. why a link is `unresolved`, FR-005/FR-010) |

**Evidence-state definitions (exact, non-overlapping)**:

- **`proven`** -- a committed artifact contains an EXPLICIT, machine-readable
  reference connecting this hop to the previous one (e.g. the migration SQL
  literally selects the source-map's column name; the TMDL measure's DAX
  literally sums the gold column the contract's `Required fields` names).
  `citation` is populated; `note` may add color but is not required to explain
  an absence.
- **`unresolved`** (candidate) -- committed artifacts exist on BOTH sides of
  the hop, but the link between them is not an explicit machine-readable
  reference (e.g. a contract's business-friendly field name does not textually
  match the gold column name, and FR-010 has not authorized any promotion
  method). `citation` MAY point at both candidate artifacts; `note` MUST say
  why the module did not promote this to `proven` (never silently promoted,
  FR-005/FR-010).
- **`gap`** -- no committed artifact exists yet at this hop (e.g. a table with
  metric contracts but no TMDL measure). `citation` is null; `note` names the
  missing artifact family and, where knowable, why it does not exist yet (e.g.
  "table has not reached Semantic Model Ready").

## Entity 3 -- Citation

The exact source pointer a `proven` or `unresolved` hop is grounded in
(FR-004). Every `citation` object cites a real, currently-committed path --
never a path that does not exist at generation time.

| Field | Type | Notes |
|---|---|---|
| `path` | string | repo-relative path (Windows 260-char budget, Principle IX) |
| `anchor` | string \| null | a YAML key, SQL identifier, or TMDL object name identifying WHERE in the file the reference lives, when the format supports it (FR-004: "where the source format supports it, an anchor/line or YAML key") |
| `quoted_reference` | string \| null | the literal snippet (column name, measure name, contract title) the module matched between this hop and its neighbor -- present for `proven`; MAY be present for `unresolved` to show what was compared and why it did not qualify |

## Entity 4 -- Lineage/Impact Artifact (the top-level generated document)

The one file the module writes per invocation (FR-001, FR-014).

| Field | Type | Notes |
|---|---|---|
| `starting_point` | Entity 1 | the anchor |
| `generated_note` | string | states this is a GENERATED artifact reflecting current committed state, carries no memory of prior runs, and makes no drift/change claim (spec edge case: regeneration after a cited artifact changes) |
| `hops` | ordered list of Entity 2 | 1 to 5 entries, always in fixed forward order starting at or after `starting_point`'s natural entry hop |
| `downstream_set` | list of references into `hops` | the candidate re-review list (User Story 3) -- a plain restatement of which `hops` entries are `proven`/`unresolved` downstream of the starting point, with NO obligation verb attached (FR-007) |
| `net_sales_consistency_note` | string \| null | present ONLY when the starting point resolves to the Net Sales contract (SC-006): a statement that the generated hops do not contradict `docs/demo/net-sales-end-to-end-readiness-trace.md`'s cited evidence -- never a restatement replacing that trace |
| `boundary_footer` | string | fixed text reiterating: no score, no obligation verb, no readiness-stage change, no approval, read-only apart from this file (mirrors F035's "Composes-only proof" section) |

**Forbidden fields (explicitly absent from this shape, hard rule #9 / FR-006 /
FR-007)**: no `blast_radius_score`, no `confidence`, no `health`, no
`maturity`, no `artifacts_affected_count`, no `priority`, no `risk_level`, no
`recommended_action`. If a future edit to this shape is proposed that adds any
such field, it violates FR-006/FR-007 and must be rejected.

## Filename convention (FR-014, confirmed default -- see plan.md Constitution Check, Principle VI)

| Starting-point kind | Output path pattern | Collision-avoidance mechanism |
|---|---|---|
| `column` | `mappings/<table>/lineage-column-<column>.md` | the literal token `column` in the filename |
| `metric` | `mappings/<table>/lineage-metric-<Metric>.md` | the literal token `metric` in the filename |

The `column`/`metric` root-type token is load-bearing (spec FR-014): it is what
prevents a column and a metric contract that happen to share a name (e.g. a
column `total_sales` and a contract `TotalSales.yaml`) from writing to the same
path. Both live under the table's existing `mappings/<table>/` folder alongside
`reconciliation-report.md` and `unresolved-questions.md` -- no new top-level
`docs/lineage/` index is introduced.

## Illustrative cited instance (Principle VII -- example only, never inlined into the template)

Using the confirmed-present artifacts from `research.md` section 2, a
column-rooted run for `retail_store_sales` would (illustratively) produce hops
resembling:

1. `source_map` -- `proven`, citing `mappings/retail_store_sales/source-map.yaml`.
2. `migration_sql` -- `proven`, citing `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`.
3. `metric_contract` -- `proven` or `unresolved` depending on whether the
   contract's required-field name textually matches the gold column, citing
   e.g. `mappings/retail_store_sales/metrics/TotalSales.yaml`.
4. `tmdl_measure` -- `proven` or `unresolved`, citing
   `powerbi/RetailStoreSales.SemanticModel/definition/tables/gold fct_sales_rss.tmdl`.
5. `dashboard_visual` -- `gap` if no filled `visual-contract-binding-map.md`
   copy exists yet for this table (confirmed absent at research time),
   otherwise `proven`/`unresolved` citing that filled binding map.

This paragraph is the ONLY place in the Phase-1 design set where
`retail_store_sales` specifics appear as content; the template
(`templates/lineage-trace.md`) and the skill's fixed section labels use only
`<schema.table.column>` / `<Metric>` placeholders (SC-007).
