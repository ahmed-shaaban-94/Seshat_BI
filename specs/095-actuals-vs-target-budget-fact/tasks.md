---
description: "Task list for the actuals-vs-target (budget) fact pattern + variance-contract-shape + second worked-example documentation feature"
---

# Tasks: Actuals-vs-Target (Budget) Fact + Variance Readiness

**Input**: Design documents from `specs/095-actuals-vs-target-budget-fact/`

**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`,
`quickstart.md` (all present, Phase 0/1 complete).

**Tests**: This is a documentation/template feature (Principle VIII,
static-first); there is no application code, so "tests" below are
verification/consistency checks (field-set diffs, verbatim name-checks,
fabricated-value greps, a read-only `retail check` dry run) rather than
unit/integration test code. They are NOT optional -- spec.md's Success
Criteria (SC-001..SC-007) depend on them and are executed as Polish-phase
tasks.

**Organization**: Tasks are grouped by user story (spec.md US1/US2 at P1,
US3 at P2). Each user story authors exactly ONE new deliverable file, at the
path spec.md's Clarifications already fixed. No task edits
`docs/worked-examples/retail-store-sales.md`, `templates/metric-contract.yaml`,
or `skills/retail-kpi-knowledge/domains/targets-and-budgets.md` (FR-015) --
those three are read-only citation sources throughout.

**FR coverage note (read before executing)**: Every one of spec.md's 19
functional requirements maps to at least one task below. FR-001..FR-005 and
the pattern-doc half of FR-019 are authored in Phase 3 (US1). FR-006..FR-009
and the contract-shape half of FR-019 are authored in Phase 4 (US2).
FR-011..FR-013 are authored in Phase 5 (US3). FR-010, FR-014, FR-015, FR-016,
FR-017, and FR-018 are PROHIBITIONS with no single "author X" home -- each is
verified by a dedicated Polish-phase task (Phase 6) rather than skipped.
Because every static default this feature could need already exists
(RC14, the four-status vocabulary, the F009 field set) and FR-014 forbids
adding a new `retail check` rule, this feature has NO static-rule-wiring
task; the docs-before-automation ordering (hard rule #8) is satisfied
vacuously and is called out explicitly in Phase 6 rather than left silent.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`US1`/`US2`/`US3`), or
  `SETUP`/`FOUND`/`POLISH` for shared/cross-cutting work
- Every task names the exact repo-relative file path it reads or writes, and
  the FR(s)/SC(s) it satisfies

---

## Phase 1: Setup

**Purpose**: Confirm the worktree and directory shape before any content
task begins. No deliverable file is created in this phase.

- [ ] T001 [SETUP] Confirm the worktree is on branch
      `095-actuals-vs-target-budget-fact` at
      `C:/Users/user/Documents/GitHub/Seshat_BI/.claude/worktrees/HERA`, and
      that `specs/095-actuals-vs-target-budget-fact/{spec.md,plan.md,
      research.md,data-model.md,quickstart.md}` all exist (via `git status`
      / `git branch --show-current` / directory listing).
- [ ] T002 [SETUP] Confirm the three IMPLEMENT-stage target directories exist
      or can be created without collision: `docs/patterns/` (may not exist
      yet), `templates/` (exists -- holds `metric-contract.yaml`),
      `docs/worked-examples/` (exists -- holds `retail-store-sales.md`).
      Confirm none of the three new target files
      (`docs/patterns/target-budget-fact.md`,
      `templates/metric-contract-shape.variance-vs-target.yaml`,
      `docs/worked-examples/target-budget-pattern-retail-store-sales.md`)
      already exists (per research.md Sec 2 -- additive only, no overwrite).

**Checkpoint**: Directory structure confirmed; safe to author content.

---

## Phase 2: Foundational (blocking prerequisite reading)

**Purpose**: Pin, verbatim, every source fact the three deliverables cite.
This phase is genuinely BLOCKING: SC-005 (exact field-set match) and SC-006
(verbatim dimension names) fail if authoring starts before these sources are
read in full. No user-story task may cite a fact not confirmed here.

- [ ] T003 [FOUND] Read `templates/metric-contract.yaml` in full and record
      its exact top-level and nested field set (`name`, `grain`,
      `formula_intent`, `owner`, `binds_to.gold_table`, `binds_to.columns`,
      `binds_to.pii_sensitive`, `readiness.status`, `readiness.evidence`,
      `readiness.blocking_reasons`, `ambiguities[]` with its
      `id/decision_status/ruling/evidence/number_moving` shape) -- this is
      the field-set baseline US2 and the SC-005 check both diff against.
- [ ] T004 [FOUND] Read `skills/retail-kpi-knowledge/domains/
      targets-and-budgets.md` in full and record verbatim: the decision
      question, the KPI name ("Net Sales vs Target %"), its
      `Planned (needs target fact)` status, and the four named ambiguities
      (grain match, calendar alignment, missing targets, filter-scope
      parity) -- the citation source for FR-003 and FR-005.
- [ ] T005 [FOUND] Read `docs/decisions/0002-retail-cleaning-defaults.md` and
      confirm RC14's exact wording ("Gold is a Kimball star: one fact at the
      silver grain + conformed dims") -- the citation source for FR-001.
- [ ] T006 [FOUND] Read `warehouse/migrations/
      0004_create_gold_retail_store_sales_star.sql` in full and record
      verbatim the fact table name (`gold.fct_sales_rss`) and the five
      conformed dimension names (`dim_customer_rss`, `dim_product_rss`,
      `dim_payment_method_rss`, `dim_location_rss`, `dim_date_rss`) -- the
      verbatim-name source for FR-011/SC-006.
- [ ] T007 [FOUND] Read `docs/worked-examples/retail-store-sales.md` in full
      (header, "Readiness at a glance" table shape, section structure) --
      the structural template US3's narrative section follows (per
      research.md Sec 1, no separate blank worked-example template file
      exists; this doc's own section structure is reused, never copied
      verbatim as content).
- [ ] T008 [FOUND] Read `.specify/memory/constitution.md` Principles I, III,
      IV, V, VI, VII, VIII, IX and the Readiness System section (four-status
      vocabulary: `not_started | blocked | warning | pass`) -- the
      compliance baseline every deliverable's Constitution-facing language
      (FR-014, FR-016) must match exactly.

**Checkpoint**: All source facts pinned verbatim. User-story authoring may
begin.

---

## Phase 3: User Story 1 - An analyst models a target/budget fact conformed to an existing actuals star (Priority: P1)

**Goal**: Author the modelling pattern document so a future analyst can
state, from the doc alone, every structural default it makes for them
(conformance, non-additive variance calculation, missing-target-must-flag,
comparison-at-coarser-grain) versus every decision left theirs (grain,
versioning).

**Independent Test** (from spec.md): Given the pattern doc alone, an analyst
can state, for a hypothetical target/budget source, the grain decision they
must make, which conformed dimensions the target fact must reuse, and what
the variance-calculation non-additivity rule requires -- entirely from the
doc, with zero external lookups beyond ADR 0002 and the existing actuals-star
pattern it cites.

### Implementation for User Story 1

All tasks in this phase write to the SAME single file,
`docs/patterns/target-budget-fact.md` -- none are marked `[P]` against each
other (same-file edits are sequential, per the template's own [P] rule).

- [ ] T009 [US1] Write `docs/patterns/target-budget-fact.md` opening/overview
      section plus the conformed-dimension-keys requirement: the target
      fact MUST conform to the SAME dimension keys as the actuals star it is
      compared against (RC14), citing
      `docs/decisions/0002-retail-cleaning-defaults.md` by name (depends on
      T003, T005). Satisfies **FR-001**; Acceptance Scenario 1 (US1).
- [ ] T010 [US1] Add the grain section to `docs/patterns/
      target-budget-fact.md`: state that target-fact grain is an
      OWNER-SUPPLIED business decision (commonly coarser than the actuals
      grain, e.g. month x store x category vs. transaction) and mark it
      `[NEEDS CLARIFICATION: target-fact grain is owner-supplied per table]`
      wherever the pattern would otherwise need a concrete grain (depends on
      T009). Satisfies **FR-002**; Acceptance Scenario 2 (US1).
- [ ] T011 [US1] Add the non-additive variance-calculation section to
      `docs/patterns/target-budget-fact.md`: state the rule already named in
      `targets-and-budgets.md` (aggregate actuals and targets SEPARATELY at
      the comparison grain, then recompute the percentage -- never average
      pre-computed ratios) by CITING that domain doc, not restating it as
      independently-invented guidance (depends on T004, T009). Satisfies
      **FR-003**; Acceptance Scenario 3 (US1).
- [ ] T012 [US1] Add the comparison-grain section to `docs/patterns/
      target-budget-fact.md`: state that when actuals and target grains
      differ, the comparison happens at the COARSER (typically target)
      grain -- actuals rolled up, never targets disaggregated -- without
      asserting which specific dimensions any given real table's rollup
      uses (depends on T010). Satisfies **FR-004**; Edge Case ("different
      native grains").
- [ ] T013 [US1] Add the missing-target-handling section to
      `docs/patterns/target-budget-fact.md`: state the rule from
      `targets-and-budgets.md` (a dimension member with no corresponding
      target MUST be flagged, never defaulted to 0% or silently dropped) as
      a structural requirement, without asserting how any specific table's
      dashboard visualizes the flag (dashboard-design is out of scope)
      (depends on T004, T009). Satisfies **FR-005**; Edge Case ("dimension
      member ... no corresponding target").
- [ ] T014 [US1] Add the versioning/reforecast edge-case note to
      `docs/patterns/target-budget-fact.md`: flag that a target fact MAY
      need a version/as-of dimension to avoid silently overwriting a prior
      plan on a mid-period revision, but that whether any given table needs
      this is an OPEN, owner-supplied judgment -- no scheme mandated
      (depends on T010). Satisfies Edge Case ("target source itself changes
      mid-period"); feeds FR-019's open-item ledger (T015).
- [ ] T015 [US1] Add the "Resolved defaults vs. open Principle-V items"
      ledger section to `docs/patterns/target-budget-fact.md`, explicitly
      separating: (resolved) conformed dimension keys, non-additive variance
      calculation, comparison-at-coarser-grain, missing-target-must-flag;
      from (open, owner-supplied) target-fact grain, RAG thresholds
      (cross-referenced to the contract shape, not restated here), and
      version/as-of dimension for reforecasts -- so a future reader does not
      have to re-derive which is which (depends on T009-T014). Satisfies
      **FR-019** (pattern-document half); SC-001; SC-007 (pattern-doc
      portion).
- [ ] T016 [US1] Add the explicit scope-boundary statement to
      `docs/patterns/target-budget-fact.md`: the document contains NO target
      VALUES, NO RAG thresholds, and NO specific table's grain decision --
      these are owner-supplied per Principle V and belong in that table's
      own `unresolved-questions.md` once a real target table is onboarded
      (depends on T009-T015). Satisfies **FR-010** (pattern-doc portion);
      Acceptance Scenario 4 (US1).

**Checkpoint**: `docs/patterns/target-budget-fact.md` exists and, read
alone, lets an analyst answer all four quickstart.md Step 1 questions with
zero external lookups beyond ADR 0002 and the actuals-star pattern it cites.

---

## Phase 4: User Story 2 - An analyst authors an actual-vs-plan variance metric contract from the contract shape (Priority: P1)

**Goal**: Author the variance contract SHAPE -- a filled pattern of
`templates/metric-contract.yaml`'s EXACT field set applied to a
ratio-of-two-facts metric -- so an analyst can see how `binds_to`, `grain`,
and the ambiguity ledger get filled for a variance metric specifically.

**Independent Test** (from spec.md): Given the variance contract shape
alone, an analyst can identify which `metric-contract.yaml` fields a
variance metric must fill differently from a simple additive-sum metric
(two-table `binds_to` tension, a comparison-rollup `grain`, and a
missing-target `ambiguities[]` entry) without reading the F009 template's
authoring notes from scratch.

### Implementation for User Story 2

All tasks in this phase write to the SAME single file,
`templates/metric-contract-shape.variance-vs-target.yaml` -- none are
marked `[P]` against each other.

- [ ] T017 [US2] Create `templates/metric-contract-shape.variance-vs-target.yaml`
      using the EXACT field set read in T003 (`name`, `grain`,
      `formula_intent`, `owner`, `binds_to.{gold_table, columns,
      pii_sensitive}`, `readiness.{status, evidence, blocking_reasons}`,
      `ambiguities[]`) -- zero new fields, zero renamed fields, zero forked
      template -- with a placeholder `name` (e.g. `<VarianceMetricName>`)
      and placeholder `owner` matching the template's own placeholder
      convention (depends on T003). Satisfies **FR-006**; Acceptance
      Scenario 1 (US2); SC-005.
- [ ] T018 [US2] Fill the `grain` field in
      `templates/metric-contract-shape.variance-vs-target.yaml`: describe
      the COMPARISON grain (the typically-coarser, target-side grain at
      which actuals are rolled up to meet targets) as a description, not a
      concrete per-table value (depends on T017). Satisfies the `grain`
      portion of **FR-006**/data-model.md's Variance Metric entity.
- [ ] T019 [US2] Fill the `formula_intent` field in
      `templates/metric-contract-shape.variance-vs-target.yaml`: state the
      non-additive rule (aggregate actuals and targets SEPARATELY at the
      comparison grain, then recompute the ratio) AND name, in plain
      language, the second (target) gold table this metric compares against
      -- since `binds_to` names only one table (depends on T004, T017, and
      research.md Sec 5's resolution). Satisfies the `formula_intent`
      portion of **FR-006**.
- [ ] T020 [US2] Fill `binds_to.gold_table` in
      `templates/metric-contract-shape.variance-vs-target.yaml` with the
      PRIMARY (actuals) gold table placeholder only (the template's existing
      single-table shape, used as-is), and add an inline `#` comment at the
      `binds_to` block flagging the two-table need as an OPEN NOTE for
      human/F009-owner review -- never a silently forced fit and never a
      second `gold_table` key (depends on T017, T019, research.md Sec 5).
      Satisfies **FR-007**; Acceptance Scenario 2 (US2).
- [ ] T021 [US2] Fill `binds_to.columns` (placeholder actuals-side measure
      column(s)) and `binds_to.pii_sensitive: false` (matching the
      template's own default) in `templates/
      metric-contract-shape.variance-vs-target.yaml` (depends on T020).
- [ ] T022 [US2] Fill `readiness.status: blocked` and add the two REQUIRED
      `readiness.blocking_reasons[]` entries in
      `templates/metric-contract-shape.variance-vs-target.yaml`: one naming
      the missing-target case, one naming the missing RAG threshold -- both
      explicit, both non-empty, never silently defaulted (depends on T017).
      Satisfies **FR-008** (blocking_reasons portion).
- [ ] T023 [US2] Add the `ambiguities[]` entry pattern for the missing-target
      case to `templates/metric-contract-shape.variance-vs-target.yaml`,
      following the EXISTING `id / decision_status / ruling / evidence /
      number_moving` shape (no new ambiguity-ledger field), citing
      `targets-and-budgets.md`'s own named ambiguity (depends on T004,
      T017, T022). Satisfies **FR-008** (ambiguities portion); Acceptance
      Scenario 3 (US2).
- [ ] T024 [US2] Add the RAG-threshold refusal to `templates/
      metric-contract-shape.variance-vs-target.yaml`: since the template has
      no dedicated RAG field, add an inline `#` comment showing WHERE a RAG
      threshold would be recorded (as `evidence[]` on a filled contract,
      once an owner supplies it) marked
      `[NEEDS CLARIFICATION: RAG thresholds are owner-supplied business
      policy, not a kit default]` -- no numeric threshold anywhere (depends
      on T017, T022). Satisfies **FR-009**; Acceptance Scenario 4 (US2).
- [ ] T025 [US2] Add the "Resolved defaults vs. open Principle-V items"
      inline-comment ledger to `templates/
      metric-contract-shape.variance-vs-target.yaml` (mirroring T015's
      pattern-doc ledger, but scoped to this file's own fields): resolved
      (readiness.status=blocked as a structural consequence,
      missing-target-must-flag) vs. open (RAG thresholds) (depends on
      T017-T024). Satisfies **FR-019** (contract-shape half); SC-007
      (contract-shape portion).

**Checkpoint**: `templates/metric-contract-shape.variance-vs-target.yaml`
exists; its field set is a mechanical, zero-diff match against
`templates/metric-contract.yaml`'s field set (verified in Phase 6, T031).

---

## Phase 5: User Story 3 - A second worked-example narrative proves the pattern is generic (Priority: P2)

**Goal**: Author the second worked-example narrative section (Principle VII
genericity proof) applying the pattern to `retail_store_sales`'s existing,
committed conformed dimensions -- without inventing any target row, value,
or RAG threshold.

**Independent Test** (from spec.md): Given only this section, a reader can
see the pattern applied to a NAMED existing star with concrete conformed-
dimension names drawn from that star's own committed gold migration, while
confirming zero fabricated target figures appear anywhere in the section.

### Implementation for User Story 3

All tasks in this phase write to the SAME single file,
`docs/worked-examples/target-budget-pattern-retail-store-sales.md` -- none
are marked `[P]` against each other. This phase depends on Phase 3 and
Phase 4 being complete (the narrative applies the pattern doc and contract
shape both authored above), in addition to Phase 2's foundational reads.

- [ ] T026 [US3] Create `docs/worked-examples/
      target-budget-pattern-retail-store-sales.md`, opening with an explicit
      statement that this is a NEW file, distinct from and never editing
      `docs/worked-examples/retail-store-sales.md`, following that file's
      own section-structure convention (per T007) rather than restating its
      content (depends on T007, T009-T016, T017-T025).
- [ ] T027 [US3] Add the conformed-dimensions section to
      `docs/worked-examples/target-budget-pattern-retail-store-sales.md`,
      naming the actuals fact (`gold.fct_sales_rss`) and the five conformed
      dimensions (`dim_customer_rss`, `dim_product_rss`,
      `dim_payment_method_rss`, `dim_location_rss`, `dim_date_rss`) copied
      VERBATIM from `warehouse/migrations/
      0004_create_gold_retail_store_sales_star.sql` (per T006) and from
      `docs/worked-examples/retail-store-sales.md`, applying the pattern
      doc's conformance requirement (T009) to this named star (depends on
      T006, T009, T026). Satisfies **FR-011**; Acceptance Scenario 1 (US3);
      SC-006.
- [ ] T028 [US3] Add the "no target fact exists" honesty section to
      `docs/worked-examples/target-budget-pattern-retail-store-sales.md`:
      state explicitly that no bronze/silver/gold object, mapping artifact,
      or `readiness-status.yaml` record exists yet for a
      `retail_store_sales` target fact, and frame its readiness as
      `not_started` (the only honest status, per hard rule #9 and the
      four-status vocabulary read in T008) -- zero fabricated target value,
      variance figure, or RAG assignment anywhere in the section (depends on
      T008, T026, T027). Satisfies **FR-012**, **FR-016** (worked-example
      portion); Acceptance Scenario 2 and 3 (US3); Edge Case ("tries to use
      this feature's second worked-example section as if it were a real,
      buildable table").
- [ ] T029 [US3] Add the "restart at Mapping Ready" statement to
      `docs/worked-examples/target-budget-pattern-retail-store-sales.md`:
      state that building a real target/budget fact for
      `retail_store_sales` (or any table) restarts the mapping gate at
      Mapping Ready for the NEW target source, and that this MUST NOT imply
      the actuals star's existing Gold Ready / Dashboard Ready status
      extends to an unbuilt target fact (depends on T028). Satisfies
      **FR-013**; Acceptance Scenario 3 (US3).

**Checkpoint**: `docs/worked-examples/
target-budget-pattern-retail-store-sales.md` exists; every dimension name in
it traces verbatim to the 0004 migration; zero numeric target/variance/RAG
content appears anywhere in it.

---

## Phase 6: Polish & Cross-Cutting Verification

**Purpose**: Verify the PROHIBITION-shaped FRs (FR-010, FR-014, FR-015,
FR-016, FR-017, FR-018) that have no natural "author X" task home in
Phases 3-5, and close out spec.md's Success Criteria mechanically. No task
in this phase adds new prose content to any of the three deliverables
(content is frozen after Phase 5); each task is a check, with its exact
finding recorded.

- [ ] T030 [POLISH] Grep all three authored files
      (`docs/patterns/target-budget-fact.md`,
      `templates/metric-contract-shape.variance-vs-target.yaml`,
      `docs/worked-examples/target-budget-pattern-retail-store-sales.md`)
      for any numeric target value, variance percentage, or RAG color/word
      (red/amber/green) that is NOT inside a `[NEEDS CLARIFICATION: ...]`
      marker or a citation of `targets-and-budgets.md`'s own text. Record 0
      matches found. Satisfies **FR-010**; SC-002.
- [ ] T031 [POLISH] Diff the field set of
      `templates/metric-contract-shape.variance-vs-target.yaml` against
      `templates/metric-contract.yaml` (T003's baseline) key-by-key
      (top-level and nested). Record 0 new/renamed keys. Satisfies
      **FR-006** (mechanical check); SC-005.
- [ ] T032 [POLISH] Diff every dimension/table name referenced in
      `docs/worked-examples/target-budget-pattern-retail-store-sales.md`
      against the names read in T006 from
      `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`
      and against `docs/worked-examples/retail-store-sales.md`. Record 0
      invented names. Satisfies **FR-011**; SC-006.
- [ ] T033 [POLISH] Run `git status --short` (or `git diff --stat` against
      the branch base) and confirm the ONLY files created or modified by
      this feature's implementation are the three deliverables above plus
      this `specs/095-actuals-vs-target-budget-fact/` chain -- and
      explicitly confirm `docs/worked-examples/retail-store-sales.md`,
      `templates/metric-contract.yaml`, and
      `skills/retail-kpi-knowledge/domains/targets-and-budgets.md` show
      ZERO diff. Satisfies **FR-015**; SC-004.
- [ ] T034 [POLISH] Confirm, by inspection of the three authored files, that
      (a) no new readiness-stage name, four-status gate, or `retail check`
      rule ID appears anywhere (no file under `src/retail/rules/` touched,
      `docs/rules/rules-manifest.json` unchanged), and (b) no SQL file, no
      `warehouse/migrations/*.sql`, no live-DB connection string, and no
      execution code was authored. Record both findings explicitly. Note:
      because FR-014 forbids a new rule, this feature has NO
      static-rule-wiring task by design (see the FR-coverage note above) --
      this task confirms that absence is correct, not an omission.
      Satisfies **FR-014**, **FR-018**; SC-003.
- [ ] T035 [POLISH] Confirm, by inspection, that every readiness-status
      reference in `docs/worked-examples/
      target-budget-pattern-retail-store-sales.md` uses only the four
      explicit statuses (`not_started | blocked | warning | pass`) and that
      the status used for the `retail_store_sales` target fact is honestly
      `not_started` -- and confirm no numeric confidence/health/maturity/
      completeness score appears in any of the three authored files
      (hard rule #9). Satisfies **FR-016**.
- [ ] T036 [POLISH] Confirm all three authored files are ASCII, UTF-8
      without BOM (`--` and `->` only, no glyphs, no smart quotes/em-dashes)
      and that every path referenced/created stays comfortably under the
      Windows 260-character path budget. Satisfies **FR-017**.
- [ ] T037 [POLISH] Confirm every `[NEEDS CLARIFICATION]` marker left open
      by this feature (target-fact grain, RAG thresholds, version/as-of
      dimension for reforecasts) is locatable in a single pass of
      `docs/patterns/target-budget-fact.md` and
      `templates/metric-contract-shape.variance-vs-target.yaml`, and that
      each one names exactly what a future owner must supply. Satisfies
      SC-007.
- [ ] T038 [POLISH] Run a read-only `retail check` dry run over the three
      newly authored files from the worktree root (ASCII/UTF-8-no-BOM,
      secret-pattern, YAML-validity checks only -- ASCII/UTF-8-no-BOM,
      secret-pattern, YAML-validity checks). Record the exact exit code and
      any output verbatim. If `retail check` is unavailable in this worktree
      (no editable install) or would require installing dependencies,
      record that as the exact skip reason -- do not claim a result that was
      not observed. Cross-checks Constitution Principle I ("compliance
      remains demonstrable by running `retail check`").
- [ ] T039 [POLISH] Compose the final FR-coverage self-audit: list FR-001
      through FR-019 in order and, for each, name the task ID(s) above that
      satisfy it, confirming all 19 are covered (per the FR-coverage note at
      the top of this file). Attach this list to the closing report for the
      `speckit-analyze` stage to consume.

**Checkpoint**: All three deliverables exist, are internally consistent with
data-model.md's entity shapes, and every spec.md Success Criterion
(SC-001..SC-007) and every FR (FR-001..FR-019) has a recorded, verified
task outcome.

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2)**: depends on Setup; BLOCKS all user stories --
  no authoring task may cite a fact not pinned verbatim in T003-T008.
- **User Story 1 (Phase 3)**: depends on Foundational (specifically T003,
  T004, T005). Independent of US2 and US3 -- can be authored first, in
  parallel intent, or interleaved with US2.
- **User Story 2 (Phase 4)**: depends on Foundational (specifically T003,
  T004). Independent of US1 in file terms (different deliverable file), but
  T019 (formula_intent) is easier to write consistently with US1's variance
  section (T011) authored first -- recommended order is US1 then US2, not a
  hard blocking dependency.
- **User Story 3 (Phase 5)**: depends on Foundational AND on User Story 1
  (T009-T016) AND User Story 2 (T017-T025) both being complete -- the
  narrative applies both the pattern doc and the contract shape to a named
  star, so it cannot be written before either exists.
- **Polish (Phase 6)**: depends on Phases 3, 4, and 5 all being complete
  (every verification task reads all three finished deliverables).

### User Story dependencies

- **User Story 1 (P1)**: Can start after Foundational -- no dependency on
  US2 or US3.
- **User Story 2 (P1)**: Can start after Foundational -- no hard dependency
  on US1, though shares citation sources (T003, T004) and benefits from
  US1's variance-rule wording (T011) existing first for consistency.
- **User Story 3 (P2)**: MUST start after BOTH US1 and US2 are complete --
  this is the one genuine cross-story dependency in this feature, because
  the second worked example demonstrates the pattern AND the contract shape
  together against a named star.

### Within each user story

- All tasks within Phase 3 write the same file (`docs/patterns/
  target-budget-fact.md`) and are sequential, not `[P]`.
- All tasks within Phase 4 write the same file
  (`templates/metric-contract-shape.variance-vs-target.yaml`) and are
  sequential, not `[P]`.
- All tasks within Phase 5 write the same file
  (`docs/worked-examples/target-budget-pattern-retail-store-sales.md`) and
  are sequential, not `[P]`.
- No task in this feature is marked `[P]` against another task in the SAME
  phase, because every phase's tasks target one shared file (per the
  template's own rule: `[P]` = different files, no dependencies). The only
  file-level parallelism available is ACROSS Phase 3 and Phase 4 (US1 vs
  US2 -- different files, both depend only on Foundational).

### Parallel opportunities

- Phase 3 (US1) and Phase 4 (US2) target different files and share no
  content dependency beyond Foundational -- they MAY be worked in parallel
  by two people/sessions once Phase 2 is complete.
- No task within any single phase is parallelizable against another task in
  that same phase (same-file constraint, see above) -- this feature
  deliberately has no `[P]` tags on individual tasks, only phase-level
  parallel opportunity (US1 vs US2).

---

## Implementation Strategy

### Documentation-only MVP

Since every deliverable here is a single new file with no independently
deployable runtime slice, "MVP" means: Phase 1 + Phase 2 + Phase 3 (US1)
alone already delivers a usable, standalone modelling pattern (spec.md's own
priority ordering: US1 is P1 and its Independent Test requires nothing from
US2 or US3). Phase 4 (US2) is the second P1 and is tied with US1 as the core
deliverable per spec.md's own framing ("Tied with User Story 1 as the core
deliverable"). Phase 5 (US3) is P2 and is the last increment, since it is
the only phase with a hard cross-story dependency.

### Incremental delivery

1. Complete Setup + Foundational -> sources pinned.
2. Add User Story 1 (pattern doc) -> independently testable per
   quickstart.md Step 1.
3. Add User Story 2 (contract shape) -> independently testable per
   quickstart.md Step 2.
4. Add User Story 3 (second worked example) -> requires 2 and 3 both done;
   testable per quickstart.md Step 3.
5. Polish (Phase 6) closes out every SC and every prohibition-shaped FR.

### What this tasks.md does NOT schedule

Per FR-018 and Constitution Principle VIII, a REAL per-table target/budget
fact build (source-mapping -> retail-build-warehouse -> retail-validate,
listed for orientation only in plan.md's "Files/dirs a FUTURE real
target-fact build would touch" section) is explicitly NOT a task in this
file -- it is a separate, later, unnumbered feature that would consume
these three deliverables, not build them further.

## Notes

- No task in this file creates a `mappings/<table>/` directory, a
  migration, a PBIP model, or edits any file outside
  `docs/patterns/`, `templates/`, `docs/worked-examples/`, and this
  feature's own `specs/095-actuals-vs-target-budget-fact/` chain.
- No task edits `docs/worked-examples/retail-store-sales.md`,
  `templates/metric-contract.yaml`, or
  `skills/retail-kpi-knowledge/domains/targets-and-budgets.md` (FR-015) --
  T033 verifies this with zero diff.
- No task invents a target value, variance percentage, or RAG threshold
  (FR-010) -- T030 verifies this with a grep pass.
- No task runs `git add -A`; if/when a human later commits this work, stage
  exact paths only.
- No task commits, pushes, opens a PR, or merges.
