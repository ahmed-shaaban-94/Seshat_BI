# Tasks: 088-drill-nav-periods

Dependency-ordered. DEFINE-only. Each cites its FR/SC. STOPS at ratify.

## Phase 0 -- Owner seams (confirmed at ratify; do not self-clear)

- [ ] **T000a [OWNER SEAM, BLOCKING]** Owner confirms C1: #5 = growth-contract
  STRUCTURE only; owner rules the comparison-baseline (uncoded) + A11 (same-store) later. Agent writes
  NO baseline/comparable-store definition. _clarify C1, FR-007._
- [ ] **T000b [OWNER SEAM]** Owner confirms C2: add `report-composition.yaml` (A) vs
  defer US2 (B). _clarify C2._
- [ ] **T000c** Owner knowingly ratifies across two feature areas (F011A #4 + F009
  #5), two risk stories. _clarify C4._

## Phase 1 -- US1: drill/nav INTENT on visual-spec (P1)

- [ ] **T101** Add `drill_through` block to `templates/visual-spec.yaml`:
  `offers`, `target_page` (by name), `carried_filters` (by name). Intent only.
  _FR-001._
- [ ] **T102** Add `drill_down` block: `hierarchy` (ordered mapped-field dimension
  levels). Intent only. _FR-002._
- [ ] **T103** Comment on both blocks: reference-by-name; INTENT not execution
  (F016 renders); no inlined DAX/SQL/query. _FR-003._

## Phase 2 -- US3: period-over-period contract STRUCTURE (P1)

- [ ] **T201** Author `net-sales-growth.md`: existing contract markdown format;
  `**Additivity** Non-additive`; `**Derives from**` = base-over-base ratio of
  NetSales[period] vs NetSales[baseline] (AD1-LEGAL, never a direct sum); comparison-baseline (uncoded) flagged
  OPEN with a recommended option; `Status` structure-only. _FR-005/006/007._
- [ ] **T202** Author `same-store-sales-growth.md`: Non-additive, base-over-base; comparison-baseline (uncoded) + A11
  AND A11 flagged OPEN; comparable-store definition owner-pending (agent writes
  none). _FR-005/006/007._
- [ ] **T203** Author `ytd.md`: Non-additive/period-accumulation; comparison-baseline / partial-period (uncoded)
  normalization flagged OPEN. _FR-005/006/007._
- [ ] **T204** Annotate the `<period-comparison-contract>` placeholder in
  `reports/blueprints/executive-summary.yaml` (comment) to note the now-authored
  growth-contract structure it can reference; keep it a placeholder. _FR-008._

## Phase 3 -- US2: report-composition (P2, gated on C2=A)

- [ ] **T301** Add `templates/report-composition.yaml` (NEW): `pages[]` (blueprint
  refs), `landing_page`, `navigation[]` (incl. footer DQ-control-room link),
  `cross_page_filters[]`; orphan page ref = blocking; references pages, never
  inlines. _FR-004._

## Phase 4 -- boundary + AD1 correctness checks (no @register rule)

- [ ] **T401** YAML/markdown validity of every edited/new file. _FR-009._
- [ ] **T402** AD1 correctness: `retail check` (AD1 reads the 3 new contracts) GREEN;
  spot-run `test_additivity_consistency`. Confirms Non-additive + base-over-base is
  AD1-legal. _FR-006, SC-003/005._
- [ ] **T403** Boundary grep: drill/nav blocks contain no execution/runtime token;
  growth contracts contain NO agent-written baseline/comparable-store definition
  (comparison-baseline + A11 marked open). _FR-003/007, SC-001/003._
- [ ] **T404** Generic placeholders only, ASCII + UTF-8 no BOM. _FR-009._
- [ ] **T405** `retail check` EXIT 0 + ruff format --check/check + full unit suite
  green. _FR-010, SC-005._

## Phase 5 -- explicitly OUT of scope (guard against creep)

- [ ] **T501 (NOT DONE HERE)** Ruling the comparison-baseline (uncoded) + A11; filling real drill/nav/growth values.
  Owner-gated. _FR-011, C1._
- [ ] **T502 (NOT DONE HERE)** Optional enforcement rule (drill target_page resolves
  to a composition page). Separate future spec. _FR-010._

## STOP -- ratify ledger

Ratification (owner confirms C1/C2/C4, signs the spec) is a human edit the workflow
is forbidden to make (Principle V). See `ratify-ledger.md`.
