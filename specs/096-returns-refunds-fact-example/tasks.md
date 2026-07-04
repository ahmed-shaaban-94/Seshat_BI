---

description: "Task list for Returns/Refunds Fact Worked Example (Negative-Quantity Additivity)"
---

# Tasks: Returns/Refunds Fact Worked Example (Negative-Quantity Additivity)

**Input**: Design documents from `specs/096-returns-refunds-fact-example/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md.
No `research.md` is cited beyond what plan.md already folded in; no `contracts/` directory
exists for this feature by design (FR-016: it CITES spec 084's completeness contract,
`specs/084-worked-example-factory/contracts/worked-example-completeness.md`, by path rather
than defining a new one).

**Deliverable shape**: a second worked example -- ONE new narrative doc
(`docs/worked-examples/<returns-example>.md`), ONE edited README index row, and ONE new
`mappings/<returns-example>/` directory carrying the full artifact set (source-profile,
source-map, assumptions, unresolved-questions, reconciliation-report, the hand-authored
synthetic dataset, two metric contracts, `design/`, `handoff/`, `readiness-status.yaml`),
plus the silver+gold migration SQL and a governed TMDL model. NO new `retail check` rule, NO
new RC default, NO new readiness stage, NO edit to `retail-store-sales.md` or
`mappings/retail_store_sales/*`, NO edit to `docs/quality/conformed-dimension-map.yaml`
(collision-avoidance allocation). Verification is `retail check` staying green with an
UNCHANGED rule count, plus the 084 completeness-contract checklist applied item-by-item. No
new pytest module is added (docs/governance feature, not application code).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency)
- **[Story]**: US1 / US2 / US3 (from spec.md), or SETUP / FOUND / POLISH
- Every task cites the FR-id(s) it satisfies in parentheses. All of FR-001..FR-016 must be
  covered by at least one task (checked by the analyze stage).

## Table-name placeholder

Every task below uses `<rr>` as the placeholder for the chosen short table name (Assumptions:
"table name is chosen at build time," Windows 260-char budget, FR-015). Whoever executes T001
fixes the concrete name once and every later task/path uses that same fixed name.

## Scope guard (read first)

- **Docs-first ordering (hard rule #8)**: doc/template-shaped artifacts (profile, map,
  assumptions, unresolved-questions, contracts, narrative doc) are authored before any SQL
  migration or wiring task -- reflected in the phase order below (US2's mapping phase
  precedes US1's build phase), not just within a phase.
- **Principle IV (source-mapping-before-silver) is a hard cross-story ordering constraint,
  not a per-story one.** US2's `source-map.yaml` (Stage 2, Mapping Ready) MUST exist and be
  internally coherent before ANY silver/gold migration task from US1 is started. This is why
  the phase order below is US2 (mapping) -> US1 (build + contracts) -> US3 (readiness
  honesty), even though the spec numbers them US1/US2/US3 by narrative priority. Both US1 and
  US2 are P1; the spine forces map-before-build regardless of narrative order.
- Do NOT add a file under `src/retail/rules/` or edit `src/retail/rules/additivity_
  consistency.py` -- no new `retail check` rule (FR-002).
- Do NOT add or edit an entry in `docs/decisions/0002-retail-cleaning-defaults.md` -- no new
  RC default (FR-002).
- Do NOT add a key to `docs/readiness/readiness-model.md` -- no new readiness stage
  (FR-002).
- Do NOT author, edit, or pre-fill `docs/quality/conformed-dimension-map.yaml` -- declaring
  cross-star conformed dimensions is a human judgment under spec 087/HR1 (FR-012).
- Do NOT edit `docs/worked-examples/retail-store-sales.md` or any file under
  `mappings/retail_store_sales/` (Boundary section).
- Do NOT resolve the two genuine open owner rulings: VAT/tax treatment of a refund (FR-008,
  Clarification Q2) and the operative reporting date axis, sale-date vs. return-date
  (FR-013, Clarification Q1b, KPI ambiguity A3). See "Principle-V carve-out" at the end of
  this file.
- Do NOT fabricate a numeric confidence/health/maturity score or an "N of M" / percentage
  completeness tally anywhere (FR-011, hard rule #9).
- Do NOT connect to a live database or open Power BI Desktop / invoke the deferred Power BI
  execution adapter (F016) -- every live-gated check stays `blocked` / `[PENDING LIVE
  PROFILE]` (FR-009, Principle VIII).

---

## Phase 1: Setup

- [ ] T001 [SETUP] Choose the short, generic `<rr>` table name (Principle VII: no
  client-specific token; distinct from `retail_store_sales` and `demo_sample_orders`; short
  enough for the Windows 260-char path budget per FR-015) and record it in a one-line note at
  the top of the (to-be-created) `mappings/<rr>/source-profile.md` in T004. Confirm the
  chosen name does not collide with any existing `mappings/*` directory or
  `docs/worked-examples/*.md` file. (FR-001, FR-014, FR-015)
- [ ] T002 [P] [SETUP] Confirm the four read-only reference artifacts this feature consumes
  by citation exist and are readable: `skills/retail-kpi-knowledge/domains/returns.md`,
  `skills/retail-kpi-knowledge/contracts/returns-rate-value.md` (KPI-MC-08),
  `specs/084-worked-example-factory/contracts/worked-example-completeness.md`, and
  `templates/metric-contract.yaml` (AD1's closed additivity vocabulary and the contract
  shape). Record any unexpectedly missing file as a blocker before Phase 2 begins. (FR-005,
  FR-016)
- [ ] T003 [P] [SETUP] Confirm `docs/worked-examples/retail-store-sales.md` and
  `mappings/retail_store_sales/readiness-status.yaml` are readable as the section-structure
  and artifact-shape precedent this feature mirrors (per `docs/worked-examples/README.md`'s
  "How to reuse it"), without editing either file. (FR-001)

---

## Phase 2: Foundational (blocking prerequisites)

**Purpose**: create the new directories and the minimum shared scaffolding (synthetic
dataset, source profile, readiness-status skeleton) that both US2's mapping phase and US1's
build phase read from. Does NOT include the source-map itself -- that is US2's own
deliverable, not a foundational hand-off (keeping US2 a real, non-hollowed-out story).

**CRITICAL**: No user-story phase (US2/US1/US3) may begin until this phase is complete.

- [ ] T004 [FOUND] Create `mappings/<rr>/source-profile.md` from `templates/source-profile.md`,
  filled with real profiled numbers against the Phase-2 synthetic dataset (T005): grain
  candidate, candidate PK, column list and types, missingness measured as `'' OR NULL`, and
  the row count. No `<placeholder>` left unfilled (per the template's own Exit Gate
  checklist and completeness-contract item C-B1). (FR-001, FR-003)
- [ ] T005 [FOUND] Author the hand-authored GENERIC synthetic dataset file(s) under
  `mappings/<rr>/` (Clarification Q5; FR-003), containing at minimum the four required-row
  shapes from data-model.md Sec 6: (a) a normal sale (`is_return=false`, positive
  quantity/amount, period P1); (b) a same-period return (`is_return=true` per the
  authoritative column, non-positive quantity/amount, period P1); (c) a cross-period return
  (`is_return=true`, non-positive quantity/amount, period P2 > P1, carrying a reference to
  the paired original sale for lineage only); (d) a sign/type discrepancy row (the
  authoritative transaction-type column and the measure's sign disagree). No exchange-case
  row is included unless later found necessary (Clarification Q3). Data is committed,
  ASCII, UTF-8 without BOM, no client-specific fact (Principle VII). (FR-003, FR-004,
  FR-007, FR-008, FR-014, FR-015)
- [ ] T006 [FOUND] Create `mappings/<rr>/readiness-status.yaml` from
  `templates/readiness-status.yaml`, seeded with all seven stage keys
  (`source_ready`..`publish_ready`) at `status: "not_started"`, an empty top-level
  `approvals: []`, and no `score`/`confidence`/`health`/`maturity`/"N of M" field anywhere in
  the shape (FR-011). This is the skeleton every later phase updates in place as its own
  stage's artifacts land -- it is never advanced to `pass` by the authoring agent without
  cited evidence (FR-009, FR-010). (FR-009, FR-010, FR-011)
- [ ] T007 [P] [FOUND] Create the empty target directories `mappings/<rr>/design/` and
  `mappings/<rr>/handoff/` (no content yet -- populated in the US1/US3 phases) so the full
  084-completeness-contract artifact set (data-model.md Sec 7) has its final shape visible
  from the start. (FR-001)

**Checkpoint**: synthetic dataset + source-profile + readiness-status skeleton + directory
shape exist -- US2's mapping phase may now begin.

---

## Phase 3: User Story 2 - Negative quantities are sign-managed, never assumed from measure
sign alone (Priority: P1)

**Goal**: the returns fact's grain and `is_return` classification are mapped from an
authoritative transaction-type column (RC8), never from measure sign, with any sign/column
disagreement surfaced as a data-quality finding -- the Stage-2 Mapping Ready deliverable that
Principle IV requires to exist before any silver SQL is written.

**Independent Test**: inspect `mappings/<rr>/source-map.yaml`; confirm `is_return` (or its
mapped equivalent) is derived from a transaction-type/reason column, confirm the
reconciliation report documents a non-positive-quantity check for return lines, and confirm
`assumptions.md`/`unresolved-questions.md` record the sign-vs-transaction-type discrepancy
row (T005d) as a surfaced anomaly, never silently resolved.

**Ordering note**: this phase MUST complete (source-map authored + internally coherent, per
completeness-contract items C-C1..C-C4) before any task in Phase 4 (US1's silver/gold
migrations) is started -- Principle IV.

- [ ] T008 [US2] Author `mappings/<rr>/source-map.yaml` from `templates/source-map.yaml`:
  decide grain and primary key FIRST (`meta.grain`, `meta.primary_key`, RC1/RC2), then one
  `columns[]` entry per source column from T004's profile, including the `is_return`
  classification column mapped per RC8 -- `derivation` states it is computed from the
  authoritative transaction-type/reason column, `never_derived_from` explicitly names measure
  sign (data-model.md Sec 2 shape). Record RC8 under `defaults.adopted`, NOT
  `defaults.deviations` -- the first worked example to adopt it rather than mark it N/A.
  (FR-004, SC-004)
- [ ] T009 [US2] In `mappings/<rr>/source-map.yaml`'s `gold_star` section, declare the
  returns fact (`gold.<rr-fact-name>`, grain = one row per transaction line, matching T008's
  `meta.grain`), its conformed dimensions with `-1` unknown members (RC14), any degenerate
  dimensions, and a contiguous `generate_series` date dimension (RC15) -- same shape
  `retail_store_sales/source-map.yaml`'s `gold_star` block uses, table/dimension names
  distinct from every `_rss`-suffixed object to avoid a physical name collision in the shared
  `gold` schema (plan.md Project Structure). (FR-002)
- [ ] T010 [US2] Author `mappings/<rr>/assumptions.md` from `templates/assumptions.md`: the
  16-row RC1-RC16 adopted/deviated table filled, with RC8 marked adopted (not deviated,
  contra `retail_store_sales`) and every other RC row citing a real fact from T004's profile
  or T005's dataset -- no fabricated example (completeness-contract C-C2/C-C4). (FR-002,
  FR-004)
- [ ] T011 [US2] Author `mappings/<rr>/unresolved-questions.md` from
  `templates/unresolved-questions.md`, recording: (a) the T005d sign-vs-transaction-type
  discrepancy row as a data-quality finding with `Status: open` or `answered` depending on
  whether the synthetic dataset's own design already resolves it as an intentional test case
  (never silently coerced to agree); (b) an orphaned-return finding slot (Edge Cases: a return
  referencing an original sale outside the captured date range), populated only if T005's
  dataset contains such a row; (c) the two genuine OPEN owner rulings carried forward per the
  Principle-V carve-out below -- VAT/tax treatment of refunds (FR-008/Q2) and the operative
  reporting date axis (FR-013/Q1b) -- each with `Status: open`, no invented `Resolution`.
  (FR-004, FR-008, FR-013)
- [ ] T012 [US2] Author `mappings/<rr>/reconciliation-report.md` from
  `templates/reconciliation-report.md`, including an explicit non-positive-quantity/amount
  check for every row where `is_return=true` (per the authoritative column) -- numeric cells
  computed from T005's committed synthetic dataset where determinable without a live DB;
  every cell that would require a live connection stays an unfilled `<placeholder>` or
  `[PENDING LIVE PROFILE]`, never a fabricated number (completeness-contract C-D4). (FR-009)
- [ ] T013 [US2] Update `mappings/<rr>/readiness-status.yaml`: set `source_ready` and
  `mapping_ready` stage evidence citing T004/T008/T010/T011 by path; leave both stages'
  `status` at `not_started` or advance to a status no higher than the artifacts + a NAMED
  human approval justify -- `mapping_ready` MUST NOT be set to `pass` here (no approval exists
  yet; FR-010). Leave `approvals: []` empty. (FR-009, FR-010)

**Checkpoint**: the returns fact's source-map is authored and internally coherent (Mapping
Ready artifacts complete, approval pending) -- US1's build phase may now begin.

---

## Phase 4: User Story 1 - An author walks a returns fact through Stages 2-6 without breaking
additivity (Priority: P1)

**Goal**: build the silver+gold layers from US2's approved-shape map, then author the
Return Value (additive) and Return Rate % (non-additive) metric contracts and a governed TMDL
model, with a worked cross-period reconciliation figure proving period totals do not silently
misstate.

**Independent Test**: confirm the Return Value contract states additivity "Fully additive"
and the Return Rate % contract states "Non-additive" (matching `returns-rate-value.md`
verbatim); confirm no derivation edge composes the rate by direct SUM; confirm the narrative
doc states which date axis is primary and shows a worked figure that a cross-period return
does not double-count or drop value under that choice; confirm `retail check`'s AD1 rule
emits zero new ERROR findings attributable to this example.

- [ ] T014 [US1] Author `warehouse/migrations/NNNN_create_silver_<rr>.sql` (idempotent,
  numbered per the next available migration number): builds the silver table at the grain
  T008 declared, applying T010's adopted RC defaults (type casts, missing-value policy,
  `is_return` derivation from the authoritative column per RC8). Depends on T008-T010 (US2)
  being complete. (FR-002, FR-004)
- [ ] T015 [US1] Author `warehouse/migrations/NNNN_create_gold_<rr>_star.sql` (next numbered
  migration): builds the Kimball star T009 declared -- fact + conformed dims with `-1`
  unknown members, FK `COALESCE` (RC14), degenerate dims, and a contiguous
  `generate_series` date dimension (RC15) -- table/object names distinct from every
  `_rss`-suffixed object (no physical collision in the shared `gold` schema). Depends on
  T014. (FR-002)
- [ ] T016 [US1] Update `mappings/<rr>/readiness-status.yaml`: record `silver_ready` and
  `gold_ready` evidence citing T014/T015 by path; per completeness-contract C-D3, these
  stages are recorded `pass` ONLY if backed by a real `retail check`/`retail validate` exit-0
  run -- since no live DB is available at authoring time (Principle VIII), both stay
  `blocked` with a `blocking_reasons[]` entry naming the missing live surface (e.g. "no live
  Postgres connection available to run `retail check`/`retail validate` against the
  migrations"). Never a fabricated `pass`. (FR-009)
- [ ] T017 [US1] Author `mappings/<rr>/metrics/ReturnValue.yaml` from
  `templates/metric-contract.yaml` exactly (no new field): `formula_intent` states the sum of
  returned money value across kept return lines; `binds_to.gold_table` points at
  T015's gold fact table; a prose comment/narrative line states `Additivity: Fully additive
  (summable across any dimension)`, matching `returns-rate-value.md`'s own statement
  verbatim; `readiness.status: "not_started"`, `owner` left as a placeholder for a named
  human, never the authoring agent. (FR-005, SC-001)
- [ ] T018 [US1] Author `mappings/<rr>/metrics/ReturnRatePercent.yaml` from
  `templates/metric-contract.yaml` exactly (no new field): `formula_intent` states Return
  Value divided by Net Sales for the same period as a ratio, explicitly "recomputed at each
  reporting level; never summed directly from a finer level's rate"; a prose comment/
  narrative line states `Additivity: Non-additive (must be recomputed per level, never summed
  directly)`, matching `returns-rate-value.md` verbatim; if a derivation-lineage field cites
  Return Value and a sales-value contract as parents, it MUST NOT compose the rate by direct
  SUM of those parents (AD1-legal ratio composition only). (FR-005, FR-006, SC-001, SC-002)
- [ ] T019 [US1] Author the governed TMDL model under
  `powerbi/<ReturnsExample>.SemanticModel/` (PascalCase name derived from `<rr>`): the
  returns-fact table plus conformed dims per T009/T015, a marked date table, a parameterized
  connection (no baked-in host or DSN per Principle IX/CLAUDE.md), and the two measures from
  T017/T018 each binding 1:1 to its metric contract. NOT opened in Power BI Desktop, NOT
  connected live -- authored and statically checkable only (F016 deferred).
  (FR-002, FR-009)
- [ ] T020 [US1] Author the narrative doc `docs/worked-examples/<rr>.md`, mirroring
  `retail-store-sales.md`'s section structure (readiness-at-a-glance table, one section per
  stage reached, "copy / watch" notes, "See also"). Include: (a) a stated primary date axis
  for worked period-total figures -- the reversible FR-013 default (return date = the fact's
  own transaction date; original sale date carried as a reference attribute only) -- with an
  explicit caveat that this default settles NOTHING about the business's operative reporting
  axis (A3 stays OPEN, see Principle-V carve-out); (b) at least one worked reconciliation
  figure, sourced from T005's committed synthetic dataset, showing the P1/P2 period totals
  under the chosen axis and stating in prose that the cross-period return's value is neither
  dropped nor double-counted; (c) the gross-minus-return-value-equals-net arithmetic
  relationship with a real evidence figure from the committed dataset; (d) a note on the
  potential cross-star conformed-dimension question (FR-012) pointing to spec 087/HR1 without
  answering it; (e) an explicit statement that exchange handling is out of scope for this
  instance if T005's dataset contains no exchange row (Clarification Q3). (FR-001, FR-003,
  FR-007, FR-012, FR-014, SC-003)
- [ ] T021 [P] [US1] Edit `docs/worked-examples/README.md`: add one new row to "The examples"
  table for `<rr>.md` (domain, spine depth, "best read for"), matching the existing
  `retail-store-sales.md` row's format. No other edit to this file. (FR-001, C-H4)
- [ ] T022 [US1] Update `mappings/<rr>/readiness-status.yaml`: record `semantic_model_ready`
  evidence citing T017/T018/T019 by path; status stays `blocked` or `not_started` pending a
  named human's approval (`approvals: []` stays empty -- FR-010); note that the AD1 legality
  check (T017/T018's non-SUM composition) is satisfied by construction, to be confirmed by the
  Polish phase's `retail check` run. (FR-009, FR-010)

**Checkpoint**: silver+gold migrations, both metric contracts, the governed TMDL model, and
the narrative doc all exist and are internally consistent -- US3's readiness-honesty phase may
now begin (it audits, rather than authors, most of what US2/US1 already produced).

---

## Phase 5: User Story 3 - The example stops honestly at what a repo-only, no-live-DB build
can prove (Priority: P2)

**Goal**: confirm every live-gated check is recorded `blocked`/`[PENDING LIVE PROFILE]`, every
approval seam stays empty, and no numeric score appears anywhere -- then close out the
remaining artifact-only stages (Dashboard Ready design, Publish Ready handoff pack) that the
084 completeness contract's Tier 1 still requires.

**Independent Test**: read `mappings/<rr>/readiness-status.yaml`; confirm every stage whose
evidence would require a live DB connection or F016 shows `blocked` with a
`blocking_reasons[]` entry naming the missing live surface, and confirm no stage shows `pass`
without a cited committed-artifact evidence line.

- [ ] T023 [US3] Author `mappings/<rr>/design/` (layout, visual list, binding map) from
  `templates/dashboard-layout.md` / `templates/visual-contract-binding-map.md`, following
  `retail_store_sales/design/`'s shape: every measure-bearing visual binds to exactly one of
  T017/T018's approved-shape contracts (zero orphan visuals per completeness-contract C-F1);
  record explicitly what is out of answerable scope (e.g. no margin metric if no cost data
  exists) rather than inventing a metric to fill a visual (C-F2). (FR-001)
- [ ] T024 [US3] Author `mappings/<rr>/handoff/` (a filled handoff pack + review checklist)
  per `templates/handoff/`'s shape, citing T014-T022's artifacts as the pack's evidence base
  (completeness-contract C-G1). (FR-001)
- [ ] T025 [US3] Update `mappings/<rr>/readiness-status.yaml`'s `dashboard_ready` and
  `publish_ready` stages: evidence cites T023/T024 by path; both stay `blocked` (or
  `not_started`) because no named human approval exists yet (FR-010) and, for `publish_ready`
  specifically, live publish itself depends on the deferred F016 adapter (FR-009). Confirm
  `approvals: []` remains empty across ALL seven stages -- the agent authoring this example
  never self-grants any approval. (FR-009, FR-010, SC-006)
- [ ] T026 [US3] Sweep every stage in `mappings/<rr>/readiness-status.yaml` (all seven) and
  confirm: (a) every live-gated check (Gold Ready's live PK/grain/orphan-FK/penny-exact
  reconciliation; any live semantic-model connection) is `blocked` with a
  `blocking_reasons[]` entry naming the missing live surface -- never a fabricated `pass`;
  (b) no `score`/`confidence`/`health`/`maturity` field or "N of M"/percentage tally appears
  anywhere in the file. (FR-009, FR-011, SC-005)
- [ ] T027 [US3] Confirm `mappings/<rr>/unresolved-questions.md` (authored in T011) still
  carries the two OPEN owner rulings -- VAT/tax treatment of refunds and the operative
  reporting date axis -- forward as `open`, not resolved by anything T014-T026 produced; the
  FR-013 worked-figure default (T020) is NOT cited anywhere as having settled the date-axis
  question. (FR-008, FR-013)

**Checkpoint**: all three user stories complete; every stage in `readiness-status.yaml` is
honestly `blocked`/`not_started`/`warning` with cited evidence, no stage is a fabricated
`pass`, and the two genuine open owner rulings remain open.

---

## Phase 6: Polish + verification

- [ ] T028 [POLISH] Run `retail check` (scoped to the new paths, or repo-wide) and confirm it
  exits 0 with the `retail check` RULE COUNT UNCHANGED from before this feature (no new rule,
  no new rule-id introduced anywhere in `src/retail/rules/`) -- report the exact command and
  exit code, never claimed without having been run (completeness-contract C-H5). (FR-002,
  SC-002)
- [ ] T029 [POLISH] Confirm `retail check`'s AD1 rule specifically emits zero new ERROR
  findings attributable to `mappings/<rr>/metrics/ReturnValue.yaml` and
  `ReturnRatePercent.yaml` -- reconcile against the fact that AD1's read glob is
  `skills/retail-kpi-knowledge/contracts/*.md`, not `mappings/*/metrics/*.yaml` (data-model.md
  Sec 3), so this check is a manual composition-legality review against the AD1 legality
  table, not an automatic parse. (FR-006, SC-002)
- [ ] T030 [P] [POLISH] No-score scan: grep every file under `mappings/<rr>/` and
  `docs/worked-examples/<rr>.md` for `score`, `confidence`, `health`, `maturity`, and
  N-of-M/percentage-completeness patterns; confirm ZERO matches (FR-011, hard rule #9). (SC-005)
- [ ] T031 [P] [POLISH] Generic-token scan (Principle VII): grep the same file set for
  C086/client-specific tokens (billing codes, segment rollups, insurance/PII columns specific
  to a real client) outside a clearly-marked cited-instance reference to
  `skills/retail-kpi-knowledge/*`; confirm ZERO hits (FR-014, SC-007).
- [ ] T032 [P] [POLISH] Encoding + path-budget sweep: confirm every new file is ASCII, UTF-8
  without BOM, uses `--`/`->` in place of glyphs, and that every path under `mappings/<rr>/`,
  `docs/worked-examples/<rr>.md`, `warehouse/migrations/*<rr>*.sql`, and
  `powerbi/<ReturnsExample>.SemanticModel/` stays within the Windows 260-character budget.
  (FR-015)
- [ ] T033 [P] [POLISH] Boundary scan: confirm `git status`/`git diff` shows NO modification
  to `docs/worked-examples/retail-store-sales.md`, any file under
  `mappings/retail_store_sales/`, `src/retail/rules/additivity_consistency.py`,
  `docs/decisions/0002-retail-cleaning-defaults.md`, `docs/readiness/readiness-model.md`, or
  `docs/quality/conformed-dimension-map.yaml` -- only new files under `mappings/<rr>/`,
  `docs/worked-examples/<rr>.md`, one edited row in `docs/worked-examples/README.md`, the two
  new migration files, and the new TMDL model directory. (SC-007, Boundary section)
- [ ] T034 [POLISH] Apply spec 084's completeness contract
  (`specs/084-worked-example-factory/contracts/worked-example-completeness.md`) item-by-item
  against this feature's artifact set: confirm every Tier-1 item (C-A1..C-H5) is checked with
  a cited real file/run, and confirm every Tier-2 item (C-T2-*) is explicitly left as a gap
  (no approval exists) rather than simulated -- report the specific unmet item(s), never a
  percentage or "N of M" tally (per the contract's own Verdict rule). (FR-016)
- [ ] T035 [POLISH] FR-coverage self-check: grep this tasks.md for `FR-001` through `FR-016`
  and confirm every id appears at least once across T001-T034; record the result for the
  analyze stage. (traceability gate)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies -- can start immediately.
- **Foundational (Phase 2)**: depends on Setup (needs the chosen `<rr>` name from T001);
  BLOCKS all user-story phases.
- **User Story 2 / Phase 3 (P1, Mapping)**: depends on Foundational only. MUST complete
  before Phase 4 starts (Principle IV: no silver SQL before the map is authored).
- **User Story 1 / Phase 4 (P1, Build + Contracts)**: depends on Phase 3 (US2) completing --
  T014's silver migration reads T008-T010's source-map decisions directly.
- **User Story 3 / Phase 5 (P2, Readiness honesty)**: depends on Phase 4 (US1) -- it audits
  and closes out the readiness-status stages that US1's artifacts feed, and authors the
  remaining design/handoff artifacts the 084 completeness contract's Tier 1 requires.
- **Polish (Phase 6)**: depends on Phases 2-5 all being complete.

### User Story Dependencies

- US2 (P1, Mapping): no dependency on US1/US3's *artifacts*, but is architecturally FIRST in
  the medallion spine -- Principle IV makes it a hard prerequisite for US1's build tasks,
  despite spec.md numbering it second by narrative priority. Independently testable via its
  own Independent Test (inspect `source-map.yaml`) without US1/US3 existing.
- US1 (P1, Build + Contracts): depends on US2's source-map existing and being internally
  coherent (T008-T010); does not depend on US3. Independently testable via its own
  Independent Test (contract additivity statements, AD1 zero-new-ERROR, narrative worked
  figure) once US2 is done.
- US3 (P2, Readiness honesty): depends on US1's contracts/migrations/narrative existing
  (T014-T022) to audit and to cite as evidence; not independently meaningful without US1, but
  does not require any NEW artifact from US2 beyond what US2 already produced.

### Within Each Phase

- T001 (Setup) is not `[P]` -- it fixes the `<rr>` name every later task's paths depend on.
  T002/T003 are `[P]` (independent read-only confirmations, no shared state with T001 or each
  other).
- T004-T007 (Foundational): T004 depends on T005 existing conceptually (the profile is filled
  against the dataset) but both can be drafted together since the dataset shape is fixed by
  data-model.md Sec 6 in advance; T006 is independent of T004/T005 (a skeleton, not filled
  from them); T007 is `[P]` (directory creation only, no content dependency).
- T008-T013 (US2) are sequential: grain/PK decided first (T008), then the gold star shape
  (T009) which depends on T008's grain, then assumptions (T010) and unresolved-questions
  (T011) which cite T008/T009's decisions, then reconciliation (T012) which needs the map's
  columns defined, then the readiness-status update (T013) last.
- T014-T022 (US1) are sequential: silver (T014) depends on the completed T008-T010; gold
  (T015) depends on T014; the readiness update (T016) depends on T014/T015; the two metric
  contracts (T017/T018) depend on T015's gold table existing to cite in `binds_to`; the TMDL
  model (T019) depends on T017/T018's contracts; the narrative doc (T020) depends on
  everything above being authored so it can cite real evidence; T021 (README edit) is `[P]`
  (different file, no dependency on T020's content beyond the chosen name); T022 (readiness
  update) runs last, after T017-T019 exist to cite.
- T023-T027 (US3) are mostly sequential (design before handoff before the readiness sweep
  before the final unresolved-questions confirmation), since each later task audits what the
  prior task in this phase produced.
- T028-T035 (Polish): T028-T029 (the `retail check`/AD1 runs) come first so later scans
  operate on a confirmed-green baseline; T030-T033 are `[P]` (independent read-only scans,
  different concerns, no mutation); T034 depends on T030-T033 having found no violations to
  re-litigate; T035 runs last.

### Parallel Opportunities

- T002 and T003 may run in parallel (Setup).
- T007 may run in parallel with T004-T006 (different files/dirs, no content dependency).
- T021 may run in parallel with T020 (different file).
- T030, T031, T032, T033 may run in parallel with each other (independent scans, no
  mutation).

---

## Implementation Strategy

### MVP First (User Stories 2 + 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational).
2. Complete Phase 3 (User Story 2) -- the source-map, RC8 adoption, and discrepancy
   surfacing are the Mapping Ready prerequisite every later stage needs.
3. Complete Phase 4 (User Story 1) -- silver/gold, the two additivity-correct metric
   contracts, the governed model, and the worked cross-period figure are the feature's core
   proof point.
4. **STOP and VALIDATE**: confirm US1's Independent Test (contract additivity statements
   match `returns-rate-value.md`; AD1 zero-new-ERROR; narrative worked figure present).
5. Ship/demo if ready; User Story 3 (Phase 5) and Polish (Phase 6) close out honesty and
   verification.

### Incremental Delivery

1. Setup + Foundational -> synthetic dataset + profile + readiness skeleton ready.
2. Add US2 (mapping) -> validate independently (source-map inspection).
3. Add US1 (build + contracts) -> validate independently (additivity + AD1 + worked figure).
4. Add US3 (readiness honesty) -> validate independently (readiness-status blocked/empty
   approvals sweep).
5. Polish (Phase 6) closes the loop: `retail check` green with unchanged rule count, AD1
   zero-new-ERROR, no-score/generic-token/encoding/boundary scans, 084 completeness-contract
   checklist applied item-by-item, FR-coverage self-check.

---

## Principle-V carve-out (do NOT implement a resolution)

- **VAT/tax treatment of refunds (FR-008, Clarification Q2)** is and stays a genuine OPEN
  owner ruling. No task in this file authorizes adopting "pre-tax" or any other treatment on
  this feature's own authority. T005/T011/T020 either cite tax handling already explicit in
  the committed synthetic dataset, or raise the gap in `unresolved-questions.md` -- never
  silently assume an answer. `returns-rate-value.md`'s "pre-tax unless policy differs" is
  knowledge-layer framing, not a ruling this feature may treat as settled.
- **The operative reporting date axis (FR-013, Clarification Q1b, KPI ambiguity A3)** is and
  stays a genuine OPEN owner ruling. T020's worked reconciliation figure uses the reversible
  Principle-VI default (return date = the fact's own transaction date) for its OWN synthetic
  arithmetic only; no task here, including T020, may cite that default as having resolved
  which axis is the business's actual operative reporting axis. T027 explicitly re-confirms
  this stays open in `unresolved-questions.md` after all other tasks complete.
- **Exchange-handling policy (FR-008, Clarification Q3)** gets a Default-adopted resolution
  only for SCOPE (out of scope for this instance if no exchange row exists in T005's
  dataset) -- the underlying business definition (return + new sale vs. netted) is NOT
  answered by any task here even if a source exchange case is later found.
- **Cross-star conformed-dimension declaration (FR-012, spec 087/HR1)** is NOT resolved by
  any task in this file. T020/T033 confirm the question is noted in prose and that
  `docs/quality/conformed-dimension-map.yaml` is never touched.
