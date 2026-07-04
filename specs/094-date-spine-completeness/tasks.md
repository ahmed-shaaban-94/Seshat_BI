---
description: "Task list for 094-date-spine-completeness (Date-Spine Completeness Static Gate, HR8)"
---

# Tasks: Date-Spine Completeness Static Gate (HR8)

**Input**: Design documents from `specs/094-date-spine-completeness/`
(spec.md, plan.md, research.md, data-model.md, quickstart.md)

**Tests**: Included -- plan.md's Testing section requires mutation-verified
fixtures (S5/S6/S7/S8 tmp_path-inline convention in
`tests/unit/test_rc_defaults.py`), and SC-001/SC-002/SC-003/SC-004 are each
explicitly "mutation-verified" success criteria in spec.md.

**Status carried from plan.md**: DRAFT. This task list authors the design; it
does not itself constitute ratification. No Principle-V question is open for
this feature (spec.md Clarifications: both candidate ambiguities resolve
against already-settled repo conventions) -- unlike 087/HR1, no task below
needs an owner-seam ruling before work starts.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3), or
  `SETUP`/`FOUND`/`POLISH` for cross-cutting phases
- Every task names an exact repo-relative file path

## Path Conventions

Single project (`src/retail/`, `tests/`, `docs/`) at repository root, per
plan.md "Structure Decision". No new project/service/top-level directory, no
new rule module (HR8 lands inside the EXISTING `src/retail/rules/sql.py`,
unlike 087/HR1's new `rule_hr1.py`).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Docs-first per hard rule #8 -- confirm the landing precondition
and update the human-facing stage doc's prose BEFORE any rule code or
wiring-surface edit, so the documented boundary (what HR8 proves vs what
V-RC15 still must prove) exists before the mechanism that enforces it.

- [ ] **T001** `[SETUP]` Confirm the reserved static-rule id is **HR8** and that
  no new declaration/manifest file is introduced (collision-avoidance
  allocation, spec.md Overview + FR-010): grep
  `tests/unit/test_rules_wiring.py` for `"HR8"` and confirm no match yet (the
  precondition every later task assumes). No file edit in this task -- a
  confirmation checklist only. _Satisfies: spec.md collision allocation;
  FR-010._
- [ ] **T002** `[SETUP]` Re-read the live wiring-surface state at
  `docs/quality/rule-count-claims.yaml` and `docs/glossary.md`'s "Currently N
  rules in M families" anchor, and confirm whether the "HR" family already
  exists (i.e. whether 087/HR1 has landed first in this worktree per the
  Parallel-landing serialization note in plan.md/research.md). Record the
  live N/M as of this task's run so Phase 2 edits the actual current numbers,
  not the stale 55/21 figures baked into spec.md/plan.md/research.md drafts.
  No file edit -- a confirmation checklist only. _Satisfies: plan.md
  Technical Context "Parallel-landing serialization note"._
- [ ] **T003** `[SETUP]` Edit `docs/readiness/gold-ready.md`: update the
  "Required checks" table's static `retail check` row to name **HR8**
  alongside S6/S7 (daily-step + literal-bounds-order structural soundness),
  and state in the same row/note that live coverage against the fact's real
  min/max remains `V-RC15`'s job, unchanged. This is a DOC-FIRST prose edit,
  authored before HR8's code exists, per hard rule #8 and FR-012. _Satisfies:
  FR-012._

**Checkpoint**: the stage doc already states the boundary HR8 will enforce,
and the live wiring-surface numbers are confirmed, before any code lands.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Reserve the rule id across every wiring surface (FR-011) with a
stub registration, mirroring the S7/S8/HR1 wiring discipline -- but LIGHTER
than HR1's, because `sql.py` is already imported by
`src/retail/rules/__init__.py` (no `__init__.py` edit needed at all).

**CRITICAL**: No user story (Phase 3+) can be implemented until this phase is
complete, because HR8 must exist as a registered (even if empty-bodied) rule
before its Finding-emitting logic can be tested via `retail check`.

- [ ] **T004** `[FOUND]` In `src/retail/rules/sql.py`: add the stub function
  `hr8_date_spine_step_and_bounds(ctx: RuleContext) -> list[Finding]`
  decorated `@register("HR8", "date-spine generate_series step + literal
  bounds-order soundness")`, placed alongside `s7_contiguous_date_dim` /
  `s8_date_dim_no_unknown_member` (same file, same neighbourhood per
  research.md precedent), with a docstring stating what HR8 does and does
  NOT do (does not re-flag S7's DISTINCT-vs-generate_series choice; does not
  prove live coverage) and returning `[]` (stub body; Phase 3+ fills it in).
  Does NOT edit `s7_contiguous_date_dim`'s or `s8_date_dim_no_unknown_member`'s
  bodies (FR-010). _Satisfies: FR-001, FR-002 (precondition), FR-010._
- [ ] **T005** `[P]` `[FOUND]` Edit `tests/unit/test_rules_wiring.py`: add
  `"HR8"` to `EXPECTED_RULE_IDS`. No `src/retail/rules/__init__.py` edit is
  needed (`sql.py` is already in the side-effecting import list). _Satisfies:
  FR-011 (wiring surface 1)._
- [ ] **T006** `[P]` `[FOUND]` Edit `docs/rules/rules-manifest.json`: add
  `{"id": "HR8", "title": "date-spine generate_series step + literal
  bounds-order soundness"}` in id order (after the last "S"-family entry,
  or after "HR1" if T002 confirmed 087/HR1 already landed first).
  _Satisfies: FR-011 (wiring surface 2)._
- [ ] **T007** `[P]` `[FOUND]` In `src/retail/severity_posture.py`'s
  `_observe_rule` dispatch table: add an `elif rule_id == "HR8":` branch that
  plants a MINIMAL synthetic fixture forcing BOTH HR8 severities observed at
  once (mirrors the two-severity "S4b" precedent plan.md names): TWO separate
  `dim_date` `generate_series` builds in the same planted file -- one call
  with a non-daily literal step (forces `Severity.ERROR`, FR-003) and one
  call with a daily step and chronological (or non-literal) bounds (forces
  no ERROR, so FR-007's `Severity.INFO` pending-live record fires for that
  second call) -- planted under a non-`tests/`-exempt path such as
  `warehouse/migrations/a.sql`, mirroring the existing S7/S8 branches
  immediately above it. A single-call fixture (bad step only) would force
  only `["error"]`, not the `["error", "info"]` set plan.md's severity-posture
  note requires -- the second, clean call is REQUIRED for the observed
  golden to match FR-007's design (data-model.md: the INFO record fires only
  when NO ERROR fired for that call, so the ERROR-producing and
  INFO-producing calls must be two distinct `generate_series` calls, not
  one). This is a REQUIRED code edit, not just a JSON regeneration -- the
  harness's `_observe_rule` function is a hand-authored `elif` dispatch keyed
  by rule id with no default fixture, so an unrecognized id silently falls
  to the `else` branch (`tracked = []`, `NO_FINDING_MARKER`) rather than
  exercising HR8 at all. Do NOT hand-edit `docs/rules/severity-posture.json`
  directly; it is produced by T037a's regeneration (Phase 6) once this
  branch and HR8's real logic both exist. Depends on T004 (HR8 must exist to
  import). _Satisfies: FR-011 (wiring surface 3)._
- [ ] **T008** `[FOUND]` Edit `docs/glossary.md`: add the `HR8` row to the
  rules table. If T002 found the "HR" family does not yet exist in this
  worktree, this task ALSO adds the new "HR" family (HR8 becomes its first
  member, code living in `sql.py` but family identity "HR" per plan.md's
  Project Structure note); if "HR" already exists (087/HR1 landed first),
  this task adds HR8's row under the EXISTING HR family without re-adding
  "HR" to the family-letter list. Bump the "Currently N rules in M families"
  anchor using the LIVE numbers confirmed in T002 (re-read at task time, do
  not assume 55/21 or 56/22). Depends on T002, T004. _Satisfies: FR-011
  (wiring surface 4)._
- [ ] **T009** `[FOUND]` Edit `docs/quality/rule-count-claims.yaml`: bump the
  `claimed-count` for the `glossary-rule-count` entry to match T008's
  anchor text exactly (byte-consistent). Depends on T008. _Satisfies: FR-011
  (wiring surface 5)._
- [ ] **T010** `[FOUND]` Run `pytest -m unit tests/unit/test_wiring_meta_gate.py
  tests/unit/test_rules_wiring.py tests/unit/test_rule_count_claims.py`
  (NOTE: NOT `test_severity_posture.py` yet -- see below) and confirm GREEN
  with the HR8 stub registered at the new live count. Depends on T004, T005,
  T006, T008, T009. _Satisfies: FR-011 lockstep (manifest/count/glossary),
  SC-006 partial._
- [ ] **T010a** `[FOUND]` Run `pytest tests/unit/test_severity_posture.py -m
  unit` against the Phase 2 stub (T004 returns `[]`, T007's forced
  two-call fixture now exists) and confirm it FAILS RED with a drift message
  naming HR8 -- this is EXPECTED at this checkpoint (the stub cannot yet
  emit the real `["error", "info"]` set the fixture is designed to force),
  and the regeneration in T007's comment explicitly defers writing
  `docs/rules/severity-posture.json` until HR8's real logic lands (Phase 6,
  **T037a**). Confirms T007's fixture branch is wired to something (not a
  silent no-op) without prematurely committing a golden that Phase 3-5 will
  invalidate. Depends on T007, T004. _Satisfies: FR-011 wiring-surface-3
  precondition; avoids a stale golden._

**Checkpoint**: `HR8` is a real, registered, discoverable rule (currently a
no-op returning `[]`); the manifest/count/glossary wiring surfaces are
green. `severity-posture.json` intentionally stays UNREGENERATED (and its
golden test stays RED) until HR8's real Finding logic exists in Phase 6 --
regenerating now would bake in an empty/no-finding entry that Phase 3-5
would immediately invalidate. User story implementation can now begin.

---

## Phase 3: User Story 1 - Fail closed on a non-daily generate_series step (Priority: P1) MVP

**Goal**: Given a `dim_date` `INSERT` statement whose `generate_series(start,
end, step)` call has a `step` argument that is a literal `INTERVAL` other
than `'1 day'` (or an unclassifiable step expression), HR8 emits a
fail-closed ERROR naming the file, line, and the offending step text.

**Independent Test**: fixture gold migration with
`generate_series(DATE '2022-01-01', DATE '2025-01-18', INTERVAL '1 month')`
-> exactly one ERROR naming file:line and `INTERVAL '1 month'`; changing the
step to `INTERVAL '1 day'` clears the ERROR with bounds unchanged.

### Tests for User Story 1

> Write these tests FIRST; they FAIL against the Phase 2 stub before Phase 3
> implementation lands (RED), then PASS after (GREEN) -- S5/S6/S7/S8
> mutation-verify discipline.

- [ ] **T011** `[US1]` In `tests/unit/test_rc_defaults.py`: add inline
  `tmp_path`-built SQL fixture text (following the existing S7/S8 test
  convention in this same file, NOT a new `tests/fixtures/` corpus
  directory per plan.md's Testing note) for a `dim_date` `INSERT` whose
  `generate_series` step is `INTERVAL '1 month'`; assert HR8 emits exactly
  one `Severity.ERROR` Finding naming the file, line, and the literal text
  `INTERVAL '1 month'`; confirm this test FAILS against the Phase 2 stub
  (which returns `[]`). _Satisfies: US1 Acceptance Scenario 1, FR-003._
- [ ] **T012** `[P]` `[US1]` In `tests/unit/test_rc_defaults.py`: add a
  second inline fixture identical to T011 but with the step corrected to
  `INTERVAL '1 day'`; assert HR8 emits NO ERROR for that statement (the
  mutation-reverse direction for SC-002). _Satisfies: US1 Acceptance
  Scenario 2, SC-002._
- [ ] **T013** `[P]` `[US1]` In `tests/unit/test_rc_defaults.py`: add a test
  that runs HR8 against the actual committed
  `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` file
  (read via the real `RuleContext`/`ctx.tracked_files`, not a synthetic
  fixture) and assert ZERO HR8 ERROR findings -- the already-shipped tree
  must stay green. _Satisfies: US1 Acceptance Scenario 3, SC-001._
- [ ] **T014** `[US1]` In `tests/unit/test_rc_defaults.py`: add an inline
  fixture whose `generate_series` step argument is unclassifiable (a bare
  identifier such as `some_step_variable`, or a non-`INTERVAL` literal);
  assert HR8 emits exactly one `Severity.ERROR` whose message text is
  DISTINCT from T011's non-daily-step message (Edge Cases: "unreadable/
  unclassifiable step" vs "wrong step"); confirm this test FAILS against
  the Phase 2 stub. _Satisfies: FR-004, Edge Cases "step argument not a
  literal INTERVAL"._

### Implementation for User Story 1

- [ ] **T015** `[US1]` In `src/retail/rules/sql.py`: implement the
  statement-DISCOVERY loop inside `hr8_date_spine_step_and_bounds` --
  re-derive (independently of `s7_contiguous_date_dim`, per FR-010's "does
  not edit S7's body") the same `tokenize_sql`-based token span for an
  `INSERT INTO ... dim_date...` statement containing a `generate_series`
  token, yielding `(rel, start_line, end_line)` per qualifying statement.
  Depends on T004. _Satisfies: FR-002, data-model.md "Date-spine build
  statement"._
- [ ] **T016** `[US1]` In `src/retail/rules/sql.py`: implement the
  literal-preserving SLICE + argument-split helper -- run
  `strip_sql_comments` (NOT `tokenize_sql`) over the file text, select the
  `[start_line, end_line]` block found in T015, and extract the
  `generate_series(...)` call's three top-level comma-separated arguments
  via a balanced-parenthesis-aware split (a bound MAY itself be a
  parenthesized subquery per Edge Cases) into `start_arg_text`,
  `end_arg_text`, `step_arg_text`, plus the call's `call_line`. Depends on
  T015. _Satisfies: FR-003/FR-005 mechanism precondition, Clarifications
  2026-07-04 Q1, data-model.md "generate_series call arguments"._
- [ ] **T017** `[US1]` In `src/retail/rules/sql.py`: implement step
  classification over `step_arg_text` -- `daily` (literal `INTERVAL`
  textually equal to `INTERVAL '1 day'`, whitespace-insensitive) passes;
  `non_daily_literal` (a literal `INTERVAL` of any other span) emits
  `Finding("HR8", Severity.ERROR, ...)` naming the file, line, and the
  offending literal step text. Depends on T016. _Satisfies: FR-003, US1
  Acceptance Scenarios 1-2._
- [ ] **T018** `[US1]` In `src/retail/rules/sql.py`: implement the
  `unclassifiable` step branch -- when `step_arg_text` is present but is
  NOT a literal `INTERVAL` expression (bare identifier, computed
  expression, non-`INTERVAL` literal), emit `Finding("HR8", Severity.ERROR,
  ...)` naming the file, line, and the literal text found, with message
  wording DISTINCT from T017's non-daily-step message. Depends on T016.
  _Satisfies: FR-004, Edge Cases "unclassifiable step"._
- [ ] **T019** `[US1]` Run `pytest tests/unit/test_rc_defaults.py -k hr8 -m
  unit` (T011-T014) against the Phase 3 implementation and confirm GREEN,
  including the mutation-reverse check (T012's corrected-step fixture stays
  clear). _Satisfies: US1 Independent Test, SC-001, SC-002._

**Checkpoint**: HR8 correctly fails closed on a non-daily or unclassifiable
`generate_series` step, passes a daily step, and the shipped worked-example
migration stays green. This is the MVP slice -- independently testable and
deployable.

---

## Phase 4: User Story 2 - Fail closed on literal bounds that are already inverted (Priority: P1)

**Goal**: When a qualifying `generate_series` call's `start` and `end`
arguments are BOTH literal date values and `start` is chronologically after
`end`, HR8 emits a fail-closed ERROR naming the file, line, and both literal
values. A non-literal bound on either side skips this check entirely (no
Finding either way from this check).

**Independent Test**: fixture with
`generate_series(DATE '2025-01-18', DATE '2022-01-01', INTERVAL '1 day')`
(bounds reversed) -> exactly one ERROR naming both literal dates; swapping
back to chronological order clears the ERROR; a non-literal bound (e.g.
`(SELECT min(transaction_date) FROM silver.orders)`) skips the comparison.

### Tests for User Story 2

- [ ] **T020** `[US2]` In `tests/unit/test_rc_defaults.py`: add an inline
  fixture with `generate_series(DATE '2025-01-18', DATE '2022-01-01',
  INTERVAL '1 day')` (reversed literal bounds, daily step); assert HR8
  emits exactly one `Severity.ERROR` naming the file:line and BOTH literal
  values (`'2025-01-18'`, `'2022-01-01'`) in the order given; confirm this
  test FAILS against the Phase 3 implementation (no bounds-order branch
  exists yet). _Satisfies: US2 Acceptance Scenario 1, FR-005._
- [ ] **T021** `[P]` `[US2]` In `tests/unit/test_rc_defaults.py`: add a
  second inline fixture identical to T020 but with the bounds corrected to
  chronological order (`DATE '2022-01-01'`, `DATE '2025-01-18'`); assert HR8
  emits NO bounds-order ERROR for that statement (mutation-reverse
  direction for SC-003). _Satisfies: US2 Acceptance Scenario 2, SC-003._
- [ ] **T022** `[P]` `[US2]` In `tests/unit/test_rc_defaults.py`: add an
  inline fixture whose `generate_series` start argument is a non-literal
  expression (e.g. `(SELECT min(transaction_date) FROM silver.orders)`) and
  whose end argument is a literal date, daily step; assert HR8 does NOT
  emit a bounds-order ERROR for that statement (the check does not fire
  when either bound is non-literal). _Satisfies: US2 Acceptance Scenario 3,
  FR-005 non-literal-skip clause, Edge Cases "one bound literal, other an
  expression"._

### Implementation for User Story 2

- [ ] **T023** `[US2]` In `src/retail/rules/sql.py`: implement
  literal-date-shape detection over `start_arg_text` / `end_arg_text` (a
  bare date literal, any dialect spelling per data-model.md, e.g. `DATE
  'YYYY-MM-DD'`), setting `both_literal` true only when BOTH sides match.
  Depends on T016. _Satisfies: FR-005 precondition, data-model.md
  "Bounds-order check"._
- [ ] **T024** `[US2]` In `src/retail/rules/sql.py`: when `both_literal` is
  true, parse both literal dates and compare chronologically; if `start` is
  after `end`, emit `Finding("HR8", Severity.ERROR, ...)` naming the file,
  line, and BOTH literal values in the order given (start, then end); when
  `both_literal` is false, this check contributes NO Finding either way (a
  non-literal bound is never treated as a violation by default). Depends on
  T023. _Satisfies: FR-005, US2 all three Acceptance Scenarios._
- [ ] **T025** `[US2]` Run `pytest tests/unit/test_rc_defaults.py -k hr8 -m
  unit` (T020-T022, plus re-run T011-T014/T019 for regression) against the
  Phase 4 implementation and confirm GREEN, including the mutation-reverse
  check (T021's corrected-bounds fixture stays clear) and the non-literal
  skip (T022 emits no bounds-order ERROR). _Satisfies: US2 Independent Test,
  SC-003._

**Checkpoint**: HR8 now fails closed on both halves of the "structurally
incapable of covering the fact" defect class this feature targets (non-daily
step from US1, reversed literal bounds from US2), and correctly does not
over-fire on a non-literal bound. US1 and US2 together are the "co-equal"
integrity floor spec.md describes.

---

## Phase 5: User Story 3 - Record live coverage as pending, never as a fabricated pass (Priority: P2)

**Goal**: For every qualifying `generate_series` call that clears the US1
step check and the US2 bounds-order check (where applicable), HR8 emits
exactly one `Severity.INFO` record stating live coverage against the fact's
actual span is PENDING `retail validate` (V-RC15), using no coverage-proof
language ("covers", "complete", "gap-free", or equivalent) -- including when
a bound is fact-derived rather than literal.

**Independent Test**: run HR8 against the shipped worked-example migration
(literal bounds, daily step) -- zero ERROR/WARNING findings, exactly one
INFO record whose text contains no coverage-proof language; a fact-derived
bound (subquery) still gets the same INFO record.

### Tests for User Story 3

- [ ] **T026** `[US3]` In `tests/unit/test_rc_defaults.py`: extend the T013
  test (shipped worked-example migration) to also assert exactly one
  `Severity.INFO` HR8 record is present, at the migration's actual
  `generate_series` call line; confirm this assertion FAILS against the
  Phase 4 implementation (no INFO-emission branch exists yet). _Satisfies:
  US3 Independent Test, SC-001, SC-006._
- [ ] **T027** `[P]` `[US3]` In `tests/unit/test_rc_defaults.py`: add a
  text-content assertion (per SC-004) that scans every HR8 INFO message
  string produced across all fixtures in this test module and asserts none
  contains the substrings "covers", "complete", or "gap-free" (case
  -insensitive) or any equivalent coverage-proof phrase. _Satisfies: US3
  Acceptance Scenario 2, FR-007, FR-008, SC-004._
- [ ] **T028** `[P]` `[US3]` In `tests/unit/test_rc_defaults.py`: add an
  inline fixture whose `generate_series` bounds are fact-derived (e.g. a
  `min()`/`max()` subquery on both sides, or one side literal and one side
  a subquery) with a daily step; assert HR8 still emits exactly one
  `Severity.INFO` pending-live record for that call (a fact-derived bound
  narrows drift risk but is not itself a coverage proof). _Satisfies: US3
  Acceptance Scenario 3._

### Implementation for User Story 3

- [ ] **T029** `[US3]` In `src/retail/rules/sql.py`: after the T017/T018 step
  checks and the T024 bounds-order check run for a qualifying
  `generate_series` call, if NO ERROR fired for that call, emit exactly one
  `Finding("HR8", Severity.INFO, ...)` at `f"{rel}:{call_line}"` whose
  message states live date-coverage against the fact's actual span is
  PENDING `retail validate` (V-RC15) and explicitly asserts no coverage
  fact -- wording MUST NOT contain "covers", "complete", "gap-free", or
  equivalent. This record is emitted REGARDLESS of whether the bounds are
  literal or fact-derived. Depends on T017, T018, T024. _Satisfies: FR-007,
  FR-008, data-model.md "Pending-live coverage record"._
- [ ] **T030** `[US3]` Run `pytest tests/unit/test_rc_defaults.py -k hr8 -m
  unit` (T026-T028, plus full regression of T011-T025) against the Phase 5
  implementation and confirm GREEN. _Satisfies: US3 Independent Test,
  SC-004, SC-006._

**Checkpoint**: All three user stories are independently functional. HR8
fails closed on a non-daily step (US1) and on reversed literal bounds (US2),
and never overclaims coverage it cannot statically prove (US3) -- the
no-fabrication discipline (hard rule #9; Principle VIII) that keeps HR8
honest about its own limits.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: The remaining edge cases from spec.md (no `dim_date` INSERT
found; multiple builds in one file; fires order-blind to readiness stage),
the SC-005/SC-007 mechanical-verification tests, and final gate/documentation
sign-off. Cross-cutting because they touch behavior across all three user
stories' branches rather than adding a new trigger condition.

- [ ] **T031** `[P]` `[POLISH]` In `tests/unit/test_rc_defaults.py`: add a
  fixture with NO `dim_date`-targeted `INSERT` statement at all (a table
  with no gold star yet); assert HR8 emits zero findings for that file --
  a no-op, consistent with S7's own precondition. _Satisfies: Edge Cases
  "No dim_date INSERT statement found"._
- [ ] **T032** `[P]` `[POLISH]` In `tests/unit/test_rc_defaults.py`: add a
  fixture with a `generate_series` call embedded inside a SQL comment (not
  inside an actual `INSERT ... dim_date` statement token span); assert HR8
  emits zero findings for it (out of scope per Edge Cases, since HR8
  operates on comment-stripped, statement-scoped tokens like S7). _Satisfies:
  Edge Cases "generate_series call inside a comment or non-INSERT
  statement"._
- [ ] **T033** `[P]` `[POLISH]` In `tests/unit/test_rc_defaults.py`: add a
  fixture with TWO separate `dim_date` `generate_series` builds in the SAME
  migration file (one with a bad step, one clean); assert HR8 evaluates
  each qualifying `INSERT` statement independently and emits findings with
  distinct file:line locators for each. _Satisfies: Edge Cases "Multiple
  dim_date builds in the same migration file"._
- [ ] **T034** `[P]` `[POLISH]` In `tests/unit/test_rc_defaults.py`: add a
  source-inspection test asserting `hr8_date_spine_step_and_bounds`'s
  function body contains no database-connection call, no import of
  `src/retail/validate.py` / `check_date_coverage`, and no numeric
  percentage/ratio/"N of M" formatting in any emitted message string
  (mirrors the SF1/HR1 write-absence discipline, adapted to HR8's
  no-live-connection / no-fabricated-score guarantees). _Satisfies: FR-001,
  FR-006, FR-008, SC-005 (mechanically verified, not just reviewed)._
- [ ] **T035** `[P]` `[POLISH]` Grep `src/retail/rules/sql.py`'s HR8 function
  and its new test fixtures in `tests/unit/test_rc_defaults.py` for any
  C086/pharmacy-specific or worked-example-specific identifier (a literal
  `retail_store_sales` or `demo_sample_orders` table/column name required
  for matching logic to fire); confirm any such name appears only in
  illustrative fixture SQL, never as a required literal in the rule's
  matching/classification code. _Satisfies: FR-014, SC-007._
- [ ] **T036** `[POLISH]` In `tests/unit/test_rc_defaults.py`: add a test
  that HR8 fires on a fixture SQL file regardless of any
  `readiness-status.yaml` stage recorded for its table (order-blind static
  rule, per S1-S7's own framing) -- construct a minimal `RuleContext` with
  no accompanying readiness-status fixture at all and confirm HR8 still
  evaluates the SQL text. _Satisfies: Edge Cases "fires on tables whose
  Gold Ready is otherwise not yet reached"._
- [ ] **T037** `[POLISH]` Update `docs/glossary.md`'s `HR8` row (T008) and
  `docs/readiness/gold-ready.md` (T003) if the FINAL Finding-message wording
  from Phase 3-5 differs from the draft language used when those docs were
  first edited, so the doc and the code do not drift. Depends on T003, T008,
  T017, T018, T024, T029. _Satisfies: consistency with data-model.md Finding
  taxonomy, FR-012._
- [ ] **T037a** `[POLISH]` Regenerate `docs/rules/severity-posture.json`: run
  the severity-posture generator/golden test
  (`pytest tests/unit/test_severity_posture.py -m unit`, per
  `src/retail/severity_posture.py`'s own generator/observation mechanism)
  now that HR8's real Finding logic exists (Phase 3-5 landed) and T007's
  two-call fixture is wired; confirm the regenerated JSON records
  `"HR8": ["error", "info"]` (the two-severity shape T007's fixture forces
  and plan.md's Project Structure note names, matching the existing "S4b"
  precedent) and that the golden test goes GREEN (no longer RED as T010a
  left it). Do NOT hand-edit the JSON file. Depends on T007, T010a, T017,
  T018, T024, T029 (HR8's full Finding logic, all three user stories, must
  be in place first). _Satisfies: FR-011 (wiring surface 3, completes
  T010a's deferred regeneration); plan.md Project Structure
  "severity-posture.json" REGENERATE note._
- [ ] **T038** `[POLISH]` Run the full local gate: `ruff format --check src/
  tests/`, `ruff check src/ tests/`, `pytest -m unit -x -q`, then `retail
  check` and `retail kit-lint` -- confirm GREEN on the current tree,
  including zero HR8 ERROR findings against
  `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`
  (SC-001) and the wiring/rule-count lockstep (SC-006). This is the first
  full-gate run where `pytest -m unit -x -q` (which includes
  `test_severity_posture.py`) can pass GREEN, since T037a's regeneration
  must land first (T010a deliberately left that golden RED). Depends on
  T037a. _Satisfies: SC-001, SC-005, SC-006, SC-007, plan.md
  local-verification requirement._
- [ ] **T039** `[POLISH]` Confirm `tests/unit/test_wiring_meta_gate.py` and
  the rule-count-claims test still pass at the new live count and that
  `registry.all_rules()` (not just `EXPECTED_RULE_IDS`) contains `"HR8"`;
  re-confirm against T002's live-state note whether 087/HR1 landed first or
  second relative to this feature and that neither feature's family-letter
  edit collided. _Satisfies: SC-006, FR-011._

**Checkpoint**: Feature complete, gate green, no numeric score anywhere
(hard rule #9), no coverage-proof language in any INFO message, no
domain-specific name required in generic rule logic, wiring lockstep intact,
S7/V-RC15 both byte-unchanged.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies; T003 (doc-first prose edit) has no
  code dependency and can be authored before any rule code exists, per hard
  rule #8. T002 informs T008/T009's exact numbers but does not block T003.
- **Foundational (Phase 2)**: depends on Setup (T003's doc boundary should
  exist before the mechanism it describes is registered, though this is a
  sequencing preference, not a hard technical dependency) -- BLOCKS all user
  stories. T005-T007 are parallel edits once T004 exists; T008 depends on
  T002 (live numbers) and T004 (final rule title); T009 depends on T008
  (count must match anchor); T010 depends on T004-T009 all landing.
- **User Stories (Phase 3-5)**: all depend on Foundational (Phase 2)
  completion (HR8 must be a registered, importable rule before its body can
  be tested). US1 (Phase 3) has no dependency on US2/US3 and is the MVP.
  US2 (Phase 4) reuses US1's discovery/slice helpers (T015/T016) but adds
  its own bounds-order branch -- implement after US1 lands so those helpers
  exist. US3 (Phase 5) depends on US1's step checks (T017/T018) and US2's
  bounds-order check (T024) to know when NO ERROR fired for a call (the
  precondition for emitting the INFO record).
- **Polish (Phase 6)**: depends on US1 + US2 + US3 all landing (T034/T035
  inspect the FINAL function body; T037 reconciles doc wording against the
  final implementation; T037a regenerates the severity-posture golden now
  that HR8's real logic exists, completing T010a's deferred step; T038/T039
  are the final full-gate run, and T038 depends on T037a so
  `test_severity_posture.py` is GREEN, not left RED, by the time the full
  `pytest -m unit -x -q` sweep runs).

### Within Each User Story

- Tests written and RED before the matching implementation task; fixtures
  before the tests that use them (T011/T012/T013/T014 before their
  assertions run); implementation before the GREEN re-run task.
- The discovery/slice helpers (T015, T016) are shared, built once in Phase 3
  and reused (not reimplemented) by Phase 4/5.

### Parallel Opportunities

- T005, T006, T007 (three different wiring-surface files/artifacts) can run
  in parallel once T004 exists.
- Within Phase 3/4/5, fixture-authoring test tasks marked `[P]` (T012, T013 --
  note T011 is not marked P since T012/T013 are independent additions but
  T011 is the first RED test establishing the pattern; T021, T022; T027,
  T028) touch the same test file but assert independent, non-overlapping
  fixtures and can be authored in parallel by different contributors before
  being merged into the single `test_rc_defaults.py` file.
- All Phase 6 `[P]` tasks (T031-T035) touch different fixtures/assertions
  and can run in parallel with each other.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational) -- HR8 registered as a
   no-op, wiring green, stage doc already names it.
2. Complete Phase 3 (US1) -- non-daily/unclassifiable step fails closed; a
   daily step and the shipped worked-example migration pass silently (no
   ERROR).
3. **STOP and VALIDATE**: run T019's mutation-verified fixtures
   independently.
4. This is the MVP: the feature's stated "whole point" (spec.md US1
   rationale -- "the feature delivers nothing without it").

### Incremental Delivery

1. Setup + Foundational -> HR8 registered, no-op, gate green, doc boundary
   recorded.
2. Add US1 -> MVP -- the non-daily/unclassifiable step gate.
3. Add US2 -> the reversed-literal-bounds gate (co-equal integrity
   requirement per spec.md).
4. Add US3 -> the no-fabrication pending-live INFO marker (P2, but the
   check's integrity guarantee).
5. Polish -> edge cases (no-op paths, multiple builds per file,
   order-blind firing), SC-005/SC-007 mechanical verification, final gate.

### Requirement Coverage Check (every FR maps to >=1 task)

- FR-001 -> T004, T034
- FR-002 -> T004, T015
- FR-003 -> T016, T017, T011, T012
- FR-004 -> T016, T018, T014
- FR-005 -> T016, T023, T024, T020, T021, T022
- FR-006 -> T034 (source-inspection: no validate.py import, no DB call)
- FR-007 -> T029, T026, T027, T028
- FR-008 -> T029, T027, T034
- FR-009 -> T034 (no migration-file write anywhere in HR8's body)
- FR-010 -> T001, T004 (does not edit S7/S8 bodies)
- FR-011 -> T005, T006, T007, T008, T009, T010, T010a, T037a, T039
- FR-012 -> T003, T037
- FR-013 -> applies to every new file/edit this feature authors (T003-T038;
  ASCII, UTF-8 no BOM, short repo-relative paths)
- FR-014 -> T035
