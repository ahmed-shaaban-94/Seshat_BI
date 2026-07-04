# Phase 0 Research: Returns/Refunds Fact Worked Example

**Feature**: `specs/096-returns-refunds-fact-example/` | **Date**: 2026-07-04

**Input**: `specs/096-returns-refunds-fact-example/spec.md` (Clarifications session
2026-07-04, Q1-Q5 resolved)

---

## 1. Precedent survey -- what SHIPPED artifacts this feature reuses

Every artifact below is real and already committed on `main` as of this feature's
authoring. This feature reuses their SHAPE and their governing prose; it does not
re-derive any of it.

| # | Shipped artifact (real repo path) | What this feature reuses from it |
|---|-----|-----|
| 1 | `specs/084-worked-example-factory/contracts/worked-example-completeness.md` | The Tier-1 (repo-only) completeness checklist (sections A-H, items C-A1..C-H5) this example's build must satisfy, cited by path (FR-016, Clarification Q4). Confirmed committed as of this spec's Clarifications; the fallback to `retail_store_sales`'s own artifact set (below) is a contingency only. |
| 2 | `docs/worked-examples/retail-store-sales.md` | The narrative doc's SECTION STRUCTURE (Readiness-at-a-glance table; one section per stage reached: Source Ready -> Mapping Ready -> Silver Ready -> Gold Ready -> Semantic Model Ready -> Dashboard Ready -> Publish Ready; "See also"). This feature copies the structure, not the content, name, table, or recorded figures/approvals (spec.md Boundary section). |
| 3 | `mappings/retail_store_sales/` (source-profile.md, source-map.yaml, assumptions.md, unresolved-questions.md, reconciliation-report.md, metrics/, design/, handoff/, readiness-status.yaml) | The full per-table artifact SET and each file's internal shape (e.g. `source-map.yaml`'s `meta` / `defaults.adopted` / `defaults.deviations` / `columns[]` / `gold_star` / `derived_columns` structure; `readiness-status.yaml`'s `stages:` + `approvals:` + `next_action` shape). This feature's `mappings/<returns-example>/` mirrors this shape exactly, filled for a different domain. |
| 4 | `templates/metric-contract.yaml` | The metric-contract SHAPE (`name` / `grain` / `formula_intent` / `owner` / `binds_to` / `readiness` / `ambiguities`). Confirmed: this template has **no additivity field** -- additivity is stated only in the contract author's prose plus the `**Additivity**` heading convention `returns-rate-value.md` already uses. This feature's two new contracts (Return Value, Return Rate %) follow this exact shape; neither adds a new YAML key (FR-005). |
| 5 | `docs/decisions/0002-retail-cleaning-defaults.md` (RC8, line ~56) | RC8's exact rule text: "Keep returns, and derive an `is_return` boolean from the authoritative column (billing/transaction type), never from the measure sign." This is the one RC default `retail_store_sales` recorded `N/A` for and this feature is built to exercise as an ADOPTED default (not a deviation) for the first time. |
| 6 | `skills/retail-kpi-knowledge/domains/returns.md` + `skills/retail-kpi-knowledge/contracts/returns-rate-value.md` (KPI-MC-08) | The seeded business definition, additivity statement ("Return value is additive; the rate is non-additive and must be recomputed per level"), and the two open ambiguities this feature must not resolve: A2 (returns as negative sales vs. separate fact -- resolved by RC8/this feature's own modelling, not a new ruling) and A3 (sale date vs. return date -- explicitly left open, see Sec 3 below). |
| 7 | `src/retail/rules/additivity_consistency.py` (rule AD1, spec 068) | The closed additivity vocabulary this feature's contracts must use verbatim in prose ("Fully additive" / "Semi-additive" / "Non-additive") and the composition-legality table (no direct SUM of a non-additive/semi-additive metric). **Read path confirmed**: AD1's corpus regex (`_CORPUS_RE`) matches ONLY `skills/retail-kpi-knowledge/contracts/*.md` -- it does NOT read `mappings/<table>/metrics/*.yaml`. This feature's new contract YAML files are therefore outside AD1's static-check surface entirely; AD1's zero-new-ERROR guarantee (FR-006/SC-002) holds by construction because this feature edits nothing under the AD1 corpus glob. |
| 8 | `docs/worked-examples/README.md` | The "examples" index table row format and the "How to reuse it" 4-step recipe this feature's build-time doc update follows (C-H4 in the completeness contract). |

## 2. Precedent survey -- what to stay DISTINCT from (real repo paths, confirmed)

| # | Neighbour (real repo path) | Why this feature must not touch/restate it |
|---|-----|-----|
| 1 | `docs/worked-examples/retail-store-sales.md` (line ~116, RC8 = N/A) | This is the confirmed GAP this feature fills. This feature does not edit this file, does not reuse its table name (`retail_store_sales`) or figures, and does not retroactively add a return to that table's source (its source genuinely has none). |
| 2 | `specs/084-worked-example-factory/` (FR-011: 084 explicitly forbids itself from authoring or scaffolding an instance) | 084 owns the PROCESS and the completeness bar; this feature is 084's first real CONSUMER. This feature does not touch `specs/084-.../*` and does not invent its own completeness bar (Sec 1 row 1). |
| 3 | `src/retail/rules/additivity_consistency.py` (rule AD1, spec 068) | AD1 owns the additivity vocabulary and the composition-legality check. This feature consumes the vocabulary in prose; it does not modify `additivity_consistency.py`, does not add a field AD1 would need to read, and does not touch the `_CORPUS_RE` glob's target files beyond the two contracts this feature naturally authors under that path. |
| 4 | `specs/087-conformed-dimension-readiness/` (rule id reserved: HR1) | **Confirmed not yet implemented**: `src/retail/rules/` contains no HR1 rule file (searched, zero matches), and `docs/quality/conformed-dimension-map.yaml` does not exist in the repo yet. 087 is spec-only (spec.md + research.md only, no plan/tasks/contracts). This feature's design MUST NOT assume HR1's rule or the conformed-dimension-map file exist or will run; if this example's dimensions share a name with `retail_store_sales`'s or `demo_sample_orders`'s dimensions, the feature only NOTES the question in prose (FR-012) -- it cannot invoke a gate that is not built. |
| 5 | `docs/quality/conformed-dimension-map.yaml` | Does not exist yet (087 is spec-only). This feature never authors or edits it (FR-012, SC-007). |

## 3. Input-source confirmation

Per Clarification Q5 (spec.md, resolved), the example's source data is a **small,
hand-authored, GENERIC synthetic dataset**, committed under
`mappings/<returns-example>/`, in the same posture `retail_store_sales` used for its
own Kaggle-derived source (a committed, profileable artifact -- not a live-fetched or
third-party feed reached at build time). No live database connection and no external
API/service call is used to produce or validate this data.

Minimum content the dataset MUST carry to exercise the spec's acceptance scenarios
(FR-003, FR-004, US1/US2/US3):

- At least one return/refund transaction row whose quantity and/or amount carries a
  sign or flag distinguishing it from a normal sale (FR-003).
- An authoritative transaction-type/reason column, independent of measure sign, from
  which `is_return` is derived per RC8 (FR-004).
- At least one row where the transaction-type column and the measure's sign
  DISAGREE, to exercise the discrepancy-surfacing check (FR-004, US2 Acceptance
  Scenario 2) -- this row is a deliberately planted data-quality case, not a defect
  in the synthetic data; it must be documented in the mapping's assumptions or
  unresolved-questions artifact when built, never silently coerced.
- At least one cross-period return: a return transaction dated in a later reporting
  period than its paired original sale's date, sized only as large as needed to
  produce one clean worked reconciliation figure (FR-007, SC-003).
- No client-specific fact, billing code, or C086-archived specific (Principle VII,
  FR-014).

This dataset does not exist yet; it is authored during the implementation stage
(Stage 2, Source Ready / Mapping Ready), not during this planning stage.

## 4. Deferred capabilities NOT assumed

This design assumes NONE of the following are available, and every artifact this
feature's build later produces must reflect that honestly (Principle VIII;
FR-009/FR-011):

- **F016 (the Power BI execution adapter) does not exist.** No PBIP model authored
  under this feature is opened in Power BI Desktop or connected live. The governed
  TMDL model is authored and statically checkable only.
- **No live database connection is available.** Every live-gated check (Gold
  Ready's live PK/grain uniqueness, orphan-FK, penny-exact reconciliation; any live
  semantic-model connection; `retail validate` itself) is recorded `blocked` with a
  `blocking_reasons[]` entry, or `[PENDING LIVE PROFILE]` in a reconciliation
  report's numeric cells -- never a fabricated `pass`.
- **Rule HR1 / `docs/quality/conformed-dimension-map.yaml` (spec 087) is not
  implemented.** This feature's design does not depend on HR1 running or on that
  file existing; it only notes the cross-star conformance question in prose where
  relevant (FR-012).
- **No new `retail check` rule, RC cleaning default, or readiness stage is added by
  this feature** (collision-avoidance allocation; FR-002). The example is expressible
  entirely with the currently-shipped rule set and RC1-RC16.
- **No numeric confidence/health/maturity score or "N of M" completeness tally is
  produced anywhere** (hard rule #9; FR-011). Readiness is expressed only via the
  four-status model (`not_started` / `blocked` / `warning` / `pass`) plus
  `evidence[]` plus `blocking_reasons[]`.
- **No named-human approval is self-granted.** Every approval seam this example
  reaches (at minimum Mapping Ready and Semantic Model Ready) starts and stays with
  an empty `approvals[]` entry until a real named human signs it (Principle V;
  FR-010).

## 5. Decisions this research confirms (no open items block Phase 1)

- The completeness bar is `specs/084-worked-example-factory/contracts/worked-example-completeness.md`,
  cited by path (Clarification Q4).
- The source data is hand-authored synthetic, committed, not live (Clarification Q5).
- The additivity vocabulary is consumed, not redefined; AD1's static-check surface
  (`skills/retail-kpi-knowledge/contracts/*.md`) does not include this feature's
  `mappings/<returns-example>/metrics/*.yaml` files, so SC-002's "zero new AD1 ERROR
  findings" holds by construction once this feature edits nothing else under that
  glob.
- HR1/087 is confirmed spec-only (no rule file, no map file) -- this feature's
  design notes the conformance question without invoking a gate that does not
  exist.
- The reversible worked-example date-axis default (return date = the fact's own
  transaction date; original sale date carried as a reference attribute) governs
  ONLY this example's synthetic worked figures; the operative business reporting
  axis (A3) and VAT/tax treatment of refunds (Q2) remain OPEN owner rulings recorded
  in the example's own `unresolved-questions.md` at build time -- Phase 1 design
  must preserve, not resolve, these two open items.
