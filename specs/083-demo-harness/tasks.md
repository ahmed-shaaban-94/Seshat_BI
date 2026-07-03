---
description: "Dependency-ordered implementation tasks for the local demo harness (083). SPEC WORK ONLY produced this file -- no task below has been executed."
---

# Tasks: Local Demo Harness

**Input**: Design documents from `specs/083-demo-harness/` (spec.md, plan.md,
research.md, data-model.md, quickstart.md, contracts/)

**Tests**: Explicitly requested by `plan.md` ("Tests and validation" section)
-- test tasks ARE included below, separated from implementation tasks per
user story.

**Organization**: Tasks are grouped by user story (P1/P2/P3) so each can be
implemented and demoed independently, per the spec's "Independent Test"
sections.

**STOP CONDITION (binding on whoever executes this file)**: This tasks.md
describes future implementation work. Executing it means writing to
`src/**`, `mappings/**`, `tests/**`, and `docs/**` -- files explicitly
OUT OF SCOPE for the spec-work phase that produced this document. Do **not**
commit, push, open a PR, or merge as part of executing these tasks without a
separate, explicit human authorization to implement feature 083. Never use
`git add -A` or `git add .` when staging -- add exact paths only, so an
unrelated dirty-tree file is never swept into a demo-harness commit.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependencies)
- **[Story]**: US1 / US2 / US3, or `Setup`/`Foundational`/`Polish`

## Phase 1: Setup

- [ ] T001 Confirm the final naming choices this plan left TBD before writing
      any code: the sample table's committed name (plan.md suggests
      `demo_sample_orders`), the demo-scoped DB object marker (research.md R4
      suggests a `demo_` prefix or `_seshat_demo` suffix), and the git-ignored
      working directory path (data-model.md suggests `.demo-work/`). Record
      the final choices in a short note at the top of the new
      `src/retail/demo/__init__.py` docstring (see T004) so they are pinned
      once, not re-decided per file.
- [ ] T002 Add the chosen working-directory path to `.gitignore` (a single
      new line; do not touch unrelated `.gitignore` entries).
- [ ] T003 [P] Confirm `ruff`/`pytest` config already covers a new
      `src/retail/demo/` package and `tests/unit/test_demo_*.py` naming
      (it should, since both match existing glob patterns) -- no config
      change expected; this task is a verification, not an edit.

**Checkpoint**: Naming is pinned; no implementation started yet.

---

## Phase 2: Foundational (blocks all user stories)

**Purpose**: The sample dataset and its mapping-gate fixtures must exist
before any CLI verb can be meaningfully tested end-to-end.

- [ ] T004 Author the invented sample CSV (or equivalent flat file) at the
      path chosen in T001, per the column shape in `data-model.md` ("Bronze
      shape" table). Target well under 1,000 rows (FR-009). Run the
      C086/`retail_store_sales` term-list review (SC-006) on the finished
      file before treating it as done.
- [ ] T005 Author `mappings/<sample-name>/source-profile.md`,
      `source-map.yaml`, `assumptions.md`, `unresolved-questions.md` as
      pre-filled, pre-reviewed fixtures (Constitution Check row "IV" in
      plan.md) -- grain ratio measured (target 1.00), RC defaults recorded as
      adopted-as-is (Principle VI), Gate status CLEARED. This is a
      human-reviewed authoring act, not something a later CLI verb infers.
- [ ] T006 [P] Author `mappings/<sample-name>/readiness-status.yaml`, seeded
      at `source_ready: pass` / `mapping_ready: pass` / `silver_ready: pass`,
      all later stages `not_started`/`blocked`, in the shape of
      `mappings/retail_store_sales/readiness-status.yaml`. Because the sample
      is a CSV file source: set `source_kind: csv` in the `source_ready` block
      and ship BOTH mandatory illustrative approvals in `approvals[]` (FR-017,
      FR-016) -- a `{stage: source_ready}` encoding-confirmation approval (RS1
      requires it for a file source's `source_ready: pass`) and a
      `{stage: mapping_ready}` gate approval -- each with a fictional named
      owner + authority class (e.g. "Jordan Rivera (analyst)") and a comment
      labeling it illustrative. NOTE: `retail check`'s RS1 rule
      (`src/retail/rules/readiness_status.py`) WILL fail on this fixture if
      `source_kind: csv` is set without the matching source_ready approval --
      T037 verifies this stays green.
- [ ] T007 [P] (Optional, User Story 3) Author the ADDITIONAL illustrative
      approval fixture for `semantic_model_ready`, clearly labeled per FR-016,
      inside `readiness-status.yaml`'s `approvals[]` (fictional named owner +
      authority class, e.g. "Jordan Rivera (metric_owner)"). This is on top of
      the two mandatory approvals in T006.
- [ ] T008 Author the silver migration `.sql` as a COMMITTED Foundational
      fixture (moved here from US2, because Silver Ready's gate is static
      "authoring only" per `docs/readiness/silver-ready.md`, so `silver_ready`
      must be able to reach `pass` OFFLINE in User Story 1). Mirror
      `warehouse/migrations/0003_*` naming/structure at the next available
      migration number -- confirm the number by checking the latest committed
      migration first. Do NOT apply it to a database here (that is the deferred
      DB-write seam, US2). Also DESCRIBE (do not author yet) the gold migration
      shape -- the gold `.sql` is authored in T027 because Gold Ready needs the
      live leg regardless.

**Checkpoint**: Fixtures exist and are reviewable independent of any CLI code.
Run `retail check` over the new `mappings/<sample-name>/` fixtures NOW (before
any CLI code) to confirm RS1 is satisfied (`source_kind: csv` + the
source_ready approval) and S1-S7 pass on the silver migration fixture -- so a
later RS1/S-rule failure is caught here, not at T037.

---

## Phase 3: User Story 1 - Evaluator proves the spine offline (P1) MVP

**Goal**: `retail demo init/load/run/report` complete a full offline cycle
with zero network access, ending in an honest report.

### Tests for User Story 1

- [ ] T009 [P] [US1] Unit test: CLI wiring for the four `demo` subparsers in
      `tests/unit/test_demo_cli.py` (argparse registration + `--help` text
      present), following the existing subparser test pattern for
      `check`/`validate`.
- [ ] T010 [P] [US1] Unit test: `demo init` materializes fixtures into the
      working directory and is idempotent without `--force`, in
      `tests/unit/test_demo_init.py`.
- [ ] T011 [P] [US1] Unit test: `demo load` with no DSN reports the skip
      reason and exits 0, in `tests/unit/test_demo_load.py` (no real network
      call -- assert via a monkeypatched/absent DSN, not a live attempt).
- [ ] T012 [P] [US1] Unit test: `demo run` offline computation reports
      `source_ready`/`mapping_ready`/`silver_ready` as `pass` with evidence
      (Source/Mapping citing the shipped labeled approval fixtures, Silver
      citing static `retail check`), and `gold_ready` onward as
      `blocked`/`not_started` -- never `pass` offline -- in
      `tests/unit/test_demo_run.py`. Gold Ready is the honest offline ceiling
      because its gate is the live `retail validate`.
- [ ] T013 [P] [US1] Unit test: `demo report` never emits a numeric score and
      always names a `next_action`, for both `--format text` and `--format
      json`, in `tests/unit/test_demo_report.py`.

### Implementation for User Story 1

- [ ] T014 [US1] Add the `demo` subparser group to `src/retail/cli.py`
      (`init`, `load`, `run`, `report` subcommands), following the existing
      `add_parser` pattern; lazy-import the actual handlers so the stdlib-only
      `retail check` chain is unaffected (depends on T004-T008).
- [ ] T015 [US1] Implement `src/retail/demo/fixtures.py`: read the committed
      sample fixtures, materialize into the working directory (per
      `contracts/demo-init-contract.md`).
- [ ] T016 [US1] Implement `src/retail/demo/init.py` (the `init` handler),
      depends on T015.
- [ ] T017 [US1] Implement `src/retail/demo/load.py`'s OFFLINE path only
      (per `contracts/demo-load-contract.md`'s offline case) -- the live path
      is US2's task.
- [ ] T018 [US1] Implement `src/retail/demo/run.py`'s OFFLINE computation
      (per `contracts/demo-run-contract.md`): read fixtures + invoke `retail
      check`, compute the four-value status per stage, write the snapshot to
      the working directory.
- [ ] T019 [US1] Implement `src/retail/demo/report.py` (per
      `contracts/demo-report-contract.md`): render the snapshot (or compute
      inline on cold start) in `text` and `json` formats.
- [ ] T020 [US1] Wire `init`/`load`/`run`/`report` handlers into the
      `cli.py` subparsers from T014 (depends on T016-T019).

**Checkpoint**: User Story 1 is independently completable, testable, and
demoable -- the offline four-verb sequence works end to end with zero network
access.

---

## Phase 4: User Story 2 - Evaluator with a local Postgres (P2)

**Goal**: The live leg (via an already-reachable local/disposable Postgres)
lets `gold_ready` honestly reach `pass`.

### Tests for User Story 2

- [ ] T021 [P] [US2] Integration test (opt-in / auto-skipped without a DSN):
      `demo load` + `demo run` against a real or fixture-`QueryRunner`-backed
      Postgres reach `gold_ready == pass` with live evidence, in
      `tests/unit/test_demo_live_leg.py` (reuse the fixture `QueryRunner`
      pattern from `tests/unit/` covering `validate.py`, so CI needs no real
      DB).
- [ ] T022 [P] [US2] Unit test: `demo load`'s live path refuses to write when
      the target schema/table names lack the demo-scoped marker (FR-011), in
      `tests/unit/test_demo_load.py`.
- [ ] T023 [P] [US2] Unit test: `demo load` re-run against the same target
      converges to the same row count (idempotent, FR-004).
- [ ] T024 [P] [US2] Unit test: `demo run` reports `gold_ready` as `pending`
      with the concrete reason when a DSN is set but no successful `load`
      preceded it (Edge Cases in spec.md).

### Implementation for User Story 2

- [ ] T025 [US2] Implement `demo load`'s LIVE path in
      `src/retail/demo/load.py`: resolve DSN via the same
      `resolve_dsn`/precedence as `retail validate`; verify demo-scoped
      naming before any write; lazy-import the DB driver; idempotent
      upsert (depends on T017, T008).
- [ ] T026 [US2] Implement `demo run`'s LIVE leg in `src/retail/demo/run.py`:
      call the existing `run_live_checks`/`QueryRunner` machinery from
      `src/retail/validate.py` (reused, not modified) against the demo-scoped
      objects (depends on T018, T025).
- [ ] T027 [US2] Author the GOLD migration `.sql` from T008's described shape
      (`warehouse/migrations/<next-number>_create_gold_<sample>_star.sql`) and
      apply BOTH the silver (T008 fixture) and gold migrations to the
      demo-scoped objects in the connected DB. The silver `.sql` itself is
      already committed (T008); this task authors gold and performs the live
      apply -- the deferred DB-write seam that Gold Ready's live gate needs.

**Checkpoint**: User Stories 1 AND 2 both work independently; the live leg
never runs unless a DSN is actually reachable.

---

## Phase 5: User Story 3 - Illustrative approval fixture (P3)

**Goal**: The report clearly labels the pre-committed illustrative approval,
never presenting it as something the run produced.

### Tests for User Story 3

- [ ] T028 [P] [US3] Unit test: when the illustrative approval fixture
      (T007) is present, `demo report` labels `semantic_model_ready` with
      the exact "illustrative fixture... not produced by this run" text
      (FR-016), in `tests/unit/test_demo_report.py`.
- [ ] T029 [P] [US3] Unit test: no demo verb writes to
      `mappings/<sample-name>/readiness-status.yaml` (the TRACKED fixture) --
      diff the file before/after a full run sequence and assert byte-identical.

### Implementation for User Story 3

- [ ] T030 [US3] Extend `src/retail/demo/report.py` to detect and label an
      illustrative `approvals[]` entry when rendering `semantic_model_ready`
      (depends on T019, T007).

**Checkpoint**: All three user stories independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T031 [P] Author `docs/demo/demo-harness.md` (short doc, FR-015):
      cross-link to `docs/worked-examples/retail-store-sales.md` and
      `docs/demo/retail-store-sales-demo.md` rather than duplicating them.
- [ ] T032 [P] Update `RELEASE_NOTES.md` (a new dated entry, additive only,
      not touching prior entries) once the feature ships, describing what
      became possible -- following the existing entry format (see the
      2026-07-03 "Design-layer governance wave" entry for the shape).
- [ ] T033 Run the full validation task from `quickstart.md` Path A end to
      end on a clean checkout; confirm `git status` stays clean throughout
      (FR-010, SC-004).
- [ ] T034 Run `quickstart.md` Path B end to end against a real
      local/disposable Postgres; confirm demo-scoped naming and idempotency
      (FR-011, FR-004).
- [ ] T035 Run `quickstart.md` Path C (cold start) and confirm no error.
- [ ] T036 [P] Run `ruff format --check`, `ruff check`, and `pytest -m unit`
      over the new files, per the repo's mandatory local verification
      (`~/.claude/rules/common/common.md` dev workflow).
- [ ] T037 Run `retail check` and `retail semantic-check --repo .` and
      confirm neither newly fails because of the added fixtures/files (in
      particular: RS1 passes on the CSV `readiness-status.yaml` fixture, and
      S1-S7 pass on the silver migration fixture). Additionally: (a) run a
      secret-pattern scan over the new fixtures/docs to confirm no real host or
      credential was introduced (FR-014, folds in analyze-report G1); and (b)
      run `retail manifest` (or diff `docs/rules/rules-manifest.json`) to
      confirm NO new rule ID appeared -- this feature adds no `retail check`
      rule (folds in analyze-report G2).

**STOP before commit/push/PR**: after T037 passes, STOP. Do not commit, push,
open a PR, or merge. Report the diff for human review first. This tasks.md's
completion is not authorization to land the change.

---

## Dependencies & Execution Order

- Setup (Phase 1) has no dependencies.
- Foundational (Phase 2) depends on Setup; BLOCKS all user stories (the
  fixtures must exist before any verb can be meaningfully tested).
- User Story 1 (Phase 3) depends on Foundational only -- no dependency on
  US2/US3.
- User Story 2 (Phase 4) depends on Foundational AND on US1's offline `load`/
  `run` skeleton existing (T017, T018) to extend, but does not require US1's
  tests to be "done" first if worked in parallel by different people --
  the live-path functions are additive to the same files.
- User Story 3 (Phase 5) depends on Foundational (T007) and on US1's `report`
  skeleton (T019) to extend.
- Polish (Phase 6) depends on all desired user stories being complete.

## Parallel Opportunities

- T003, T006, T007 can run in parallel (different files).
- All US1 test tasks (T009-T013) can run in parallel (different test files).
- All US2 test tasks (T021-T024) can run in parallel.
- T028/T029 (US3 tests) can run in parallel.
- T031/T032/T036 (Polish, non-sequential) can run in parallel.

## Forbidden in execution (restated)

- No `git add -A` / `git add .`.
- No new `retail check` rule ID.
- No edit to `retail_store_sales`'s own artifacts.
- No C086 term, field, or value anywhere in T004-T008's authored fixtures.
- No commit/push/PR/merge without separate explicit human authorization.
