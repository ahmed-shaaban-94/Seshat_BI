# Tasks: Golden/Regression Tests for Generated DAX & SQL

**Input**: Design documents from `specs/100-generated-artifact-golden-tests/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md,
data-model.md, quickstart.md

**Tests**: This feature IS tests -- two new pytest modules under `tests/unit/` plus committed
golden fixture files under `tests/fixtures/golden/`. There is no separate "implementation" to
build behind the tests: the golden files ARE the implementation artifact. Tests are authored
test-first per user story (RED against a missing golden -> GREEN once the golden is committed),
matching the repo's nearest sibling (`043-rule-registry-snapshot-manifest-golden`).

**Organization**: Tasks are grouped by user story (US1 = DAX/TMDL/refusal golden pin, priority
P1; US2 = warehouse SQL regression lock, priority P2; US3 = optional regeneration helper,
priority P3). No `retail check` rule, no rule-id, no manifest/severity-posture entry, no CLI
subcommand, and no `.gitattributes` entry are added anywhere in this task list -- see "Out of
Scope" at the end; those exclusions are load-bearing, not oversights.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3), or omitted for
  Setup/Foundational/Polish tasks that serve all stories
- Exact repo-relative file paths are included in every task
- `[FR-0xx]` tags map each task to the functional requirement(s) it satisfies (spec.md)

## Path Conventions

Single project (existing `src/retail` + `tests/unit` + `tests/fixtures`). This feature is
purely additive under `tests/`: two new test modules in `tests/unit/`, a new `tests/fixtures/golden/`
subtree, and one optional standalone script inside that subtree. No file under `src/retail/`,
`.claude/skills/`, `docs/rules/`, or `warehouse/migrations/` is created or edited.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the exact seams this feature's tests depend on before authoring anything,
so the tests are written against confirmed reality, not assumption.

- [ ] T001 Confirm `generate_measure`, `load_contract`, and `GenResult` are importable from
  `src/retail/dax_gen.py` exactly as `tests/unit/test_dax_gen.py` already imports them (read-only;
  no new import surface added). [FR-009]
- [ ] T002 Confirm the exact `_run_generate` call shape by reading `src/retail/cli.py` directly:
  `generate_measure(contract.get("definition") or {}, name=contract.get("name"),
  doc_intent=contract.get("formula_intent"))`, no `format_string`/`display_folder` override. This
  is the call shape both US1's test and its golden-generation step must reproduce verbatim.
  (read-only) [FR-002]
- [ ] T003 [P] Confirm the fixed fixture corpus on disk: `tests/fixtures/contracts/base_revenue.yaml`
  (success), `tests/fixtures/contracts/ratio_disc.yaml` (success), `tests/fixtures/contracts/refuse_no_column.yaml`
  (refusal) -- read each and note its `definition.kind`. (read-only; no fixture is added, renamed,
  or edited) [FR-010]
- [ ] T004 [P] Confirm the two exemplar migration files exist and are read-only INPUT:
  `warehouse/migrations/0003_create_silver_retail_store_sales.sql` and
  `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`. (read-only) [FR-004]

**Checkpoint**: Every seam this feature's tests call is confirmed present and stable; no source
file has been touched.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the ONE shared contract both user stories' tests depend on -- the FR-006
text-normalization behavior -- and create the fixture directory tree before any golden file is
written into it. Nothing in Phase 3+ can be authored correctly without this.

- [ ] T005 Create the new, currently-nonexistent directories `tests/fixtures/golden/dax/` and
  `tests/fixtures/golden/sql/` (empty; no content yet). [FR-001]
- [ ] T006 Define the FR-006 normalization behavior identically everywhere it is used: replace
  every `\r\n` with `\n` in both the actual and the golden text, then strip at most one trailing
  `\n` from each side, before exact string-equality comparison. Implement this INLINE in each of
  the two test modules created in Phases 3-4 (a small private helper function per module is
  acceptable; no new shared `src/retail/` utility module is introduced -- this stays a test-only
  concern per the plan's file footprint). Document the algorithm once, in a module docstring, in
  each test module that uses it. [FR-006]

**Checkpoint**: Fixture tree exists; the normalization contract is defined and ready to be used
identically by both US1 and US2 tests. User story work can now begin.

---

## Phase 3: User Story 1 - The DAX generator's output is pinned for a fixed contract (Priority: P1) 🎯 MVP

**Goal**: A golden test that fails closed when `generate_measure`'s emitted `dax` / `tmdl_block`
(success cases) or `reason` (refusal case) text drifts from a committed golden file, for the
fixed three-fixture corpus.

**Independent Test**: Run the golden test suite unchanged against the current `dax_gen.py`; it
passes today. Hand-edit one character of the emitted DAX logic locally (uncommitted) and re-run;
the golden test fails with a diff, while `test_dax_gen.py`'s existing round-trip test still
passes (SC-001).

### Tests for User Story 1 (test-first; RED before goldens exist)

- [ ] T007 [US1] Author `tests/unit/test_dax_golden.py` (marked `@pytest.mark.unit`), test-first:
  for each of `base_revenue` and `ratio_disc`, load the contract via `load_contract(...)`, call
  `generate_measure(...)` using the exact FR-002/T002 call shape, assert `result.ok is True`, then
  read `tests/fixtures/golden/dax/<stem>.dax.txt` and `tests/fixtures/golden/dax/<stem>.tmdl.txt`,
  normalize both actual and golden text per T006, and assert exact equality with a diff on
  mismatch. At this point the golden files do not exist yet, so this test module intentionally
  fails RED. [FR-002, FR-006]
- [ ] T008 [US1] In the same module, add the refusal-case test for `refuse_no_column`: same call
  shape, assert `result.ok is False`, `result.dax is None`, `result.tmdl_block is None`, then read
  `tests/fixtures/golden/dax/refuse_no_column.reason.txt`, normalize per T006, and assert exact
  equality of `result.reason` against it -- RED until the golden reason file exists. [FR-003, FR-006]
- [ ] T009 [US1] In the same module, add an explicit-failure assertion for FR-007: when a golden
  file path referenced by a test is missing or unreadable, the test fails with a message naming
  the missing/unreadable path -- never a silent `pytest.skip`, never a pass-by-default. Verify this
  behavior is what T007/T008 currently exhibit before the goldens are created (their present RED
  failures ARE this behavior; add a small dedicated assertion/comment confirming intent so a future
  reader does not "fix" it into a skip). [FR-007]

### Golden fixture generation for User Story 1 (turns T007-T008 GREEN)

- [ ] T010 [US1] Generate and commit the golden fixture files for the two success-case fixtures by
  running `generate_measure(...)` (the T002 call shape) against `base_revenue.yaml` and
  `ratio_disc.yaml` and writing the resulting `result.dax` / `result.tmdl_block` strings verbatim
  (UTF-8, no BOM, single trailing newline) to `tests/fixtures/golden/dax/base_revenue.dax.txt`,
  `tests/fixtures/golden/dax/base_revenue.tmdl.txt`, `tests/fixtures/golden/dax/ratio_disc.dax.txt`,
  `tests/fixtures/golden/dax/ratio_disc.tmdl.txt`. These files are PRODUCED by running the
  generator, never hand-typed, so they exactly match what T007 will compare against. [FR-002, FR-011]
- [ ] T011 [US1] Generate and commit the golden refusal-reason file the same way: run
  `generate_measure(...)` against `refuse_no_column.yaml`, capture `result.reason`, and write it
  verbatim to `tests/fixtures/golden/dax/refuse_no_column.reason.txt` (UTF-8, no BOM, single
  trailing newline). [FR-003, FR-011]
- [ ] T012 [US1] Run `pytest -m unit tests/unit/test_dax_golden.py -v` and confirm all tests now
  pass GREEN with the goldens from T010-T011 in place. [FR-002, FR-003]

**Checkpoint**: User Story 1 is fully functional and independently testable -- a one-character
change to `dax_gen.py`'s emission logic now fails a test with a visible diff (SC-001), verifiable
by the quickstart.md step 2 procedure.

---

## Phase 4: User Story 2 - The committed exemplar warehouse SQL is locked against silent drift (Priority: P2)

**Goal**: A regression test that fails closed when either committed exemplar migration file's
text drifts from a committed golden copy, with no database connection and no invocation of the
`retail-build-warehouse` skill.

**Independent Test**: Run the regression test suite unchanged against the current
`warehouse/migrations/000{3,4}_*.sql`; it passes today. Hand-edit one line of either file locally
(uncommitted) and re-run; the test fails and names the file and differing content (SC-002).

### Tests for User Story 2 (test-first; RED before golden copies exist)

- [ ] T013 [US2] Author `tests/unit/test_warehouse_sql_golden.py` (marked `@pytest.mark.unit`),
  test-first: for each of the two pairs
  (`warehouse/migrations/0003_create_silver_retail_store_sales.sql`,
  `tests/fixtures/golden/sql/0003_create_silver_retail_store_sales.sql`) and
  (`warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`,
  `tests/fixtures/golden/sql/0004_create_gold_retail_store_sales_star.sql`), read both files as
  UTF-8 text, normalize each per T006, and assert exact equality, reporting which file and which
  normalized lines differ on mismatch. At this point the golden copies do not exist yet, so this
  test module intentionally fails RED. [FR-004, FR-006]
- [ ] T014 [US2] In the same module, add the FR-007 explicit-failure assertion/comment (mirroring
  T009) confirming a missing/unreadable golden copy fails with a message naming the path, never a
  silent skip. [FR-007]
- [ ] T015 [US2] In the same module, assert (via the test's own construction -- no live call made
  anywhere in the file) that the test opens no database connection and invokes no CLI/skill step,
  reading only the two already-committed migration files and their golden copies. This is a
  structural property of the test as written, confirmed by code review of the module, not a
  runtime assertion. [FR-004, FR-005]

### Golden fixture generation for User Story 2 (turns T013 GREEN)

- [ ] T016 [P] [US2] Create `tests/fixtures/golden/sql/0003_create_silver_retail_store_sales.sql`
  as a verbatim copy of the current committed
  `warehouse/migrations/0003_create_silver_retail_store_sales.sql` (same content, same filename,
  new directory). [FR-004, FR-011]
- [ ] T017 [P] [US2] Create `tests/fixtures/golden/sql/0004_create_gold_retail_store_sales_star.sql`
  as a verbatim copy of the current committed
  `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`. [FR-004, FR-011]
- [ ] T018 [US2] Run `pytest -m unit tests/unit/test_warehouse_sql_golden.py -v` and confirm all
  tests now pass GREEN with the golden copies from T016-T017 in place. [FR-004]

**Checkpoint**: User Stories 1 AND 2 both work independently -- a one-line hand-edit to either
exemplar migration file now fails a test with a diff (SC-002), verifiable by quickstart.md step 3.

---

## Phase 5: User Story 3 - Golden fixtures are refreshed through one explicit, reviewable command (Priority: P3)

**Goal**: An optional, human-run, non-CI regeneration script that overwrites only the DAX/TMDL/
reason golden files with fresh generator output, for review via `git diff` before committing.

**Independent Test**: Run the regeneration script after an intentional `dax_gen.py` change;
confirm only the golden DAX/TMDL/reason fixture files under `tests/fixtures/golden/dax/` are
rewritten, `git diff` shows exactly the expected textual change, and the User Story 1 golden
tests pass again with the refreshed fixtures.

### Implementation for User Story 3

- [ ] T019 [US3] Author `tests/fixtures/golden/regenerate_dax_golden.py` as a standalone script
  (stdlib + `retail.dax_gen` imports only): for each of `base_revenue` and `ratio_disc`, run the
  exact T002 call shape and overwrite `tests/fixtures/golden/dax/<stem>.dax.txt` and
  `<stem>.tmdl.txt`; for `refuse_no_column`, overwrite `<stem>.reason.txt`. It writes ONLY these
  five files under `tests/fixtures/golden/dax/` -- never a contract fixture, never a golden SQL
  file, never any file under `src/` or `warehouse/`. [FR-008]
- [ ] T020 [US3] Confirm by reading the finished script (T019) that it: (a) is invoked only
  manually (`python tests/fixtures/golden/regenerate_dax_golden.py`), (b) is not collected by
  pytest (no `test_` prefix, no `pytest` import, no fixture/test function inside it), (c) is not
  wired into any `retail` CLI subcommand or `retail check` rule, (d) is not referenced by any CI
  workflow file, and (e) contains no `git commit`/`git add` invocation -- it asserts nothing and
  returns no pass/fail signal; the contributor reviews `git diff` themselves. [FR-008, FR-009]
- [ ] T021 [US3] Manually run the script once (`python tests/fixtures/golden/regenerate_dax_golden.py`)
  against the CURRENT, unmodified `dax_gen.py` and confirm via `git diff tests/fixtures/golden/dax/`
  that it produces NO diff (the goldens from T010-T011 already match current generator output) --
  this proves the script's output shape matches the test's expectation shape exactly. [FR-008]

**Checkpoint**: All three user stories are independently functional. The optional regeneration
helper exists and is proven idempotent against the current, unmodified generator.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the constraints that span all three user stories and are not naturally
exercised by any single story's own tests -- the negative/scope-guard requirements.

- [ ] T022 [P] Run `pytest -m unit tests/unit/test_dax_gen.py tests/unit/test_sql.py tests/unit/test_dax.py -v`
  and confirm all three EXISTING test files still pass unchanged, and diff each against the
  worktree's pre-feature state to confirm none was edited by this feature. [FR-009]
- [ ] T023 [P] Confirm `src/retail/dax_gen.py`, `src/retail/metric_drift.py`, and
  `.claude/skills/retail-build-warehouse/SKILL.md` are byte-identical to their pre-feature state
  (`git diff` shows no change to any of the three). [FR-009]
- [ ] T024 [P] Run `retail check` (or, if unavailable in this environment, inspect
  `docs/rules/rules-manifest.json` and `docs/rules/severity-posture.json` directly) and confirm
  both files are byte-identical before and after this feature -- 0 new rule-ids, no registry
  change. [FR-001, SC-005]
- [ ] T025 [P] Grep every file this feature added
  (`tests/unit/test_dax_golden.py`, `tests/unit/test_warehouse_sql_golden.py`,
  `tests/fixtures/golden/**`) for any numeric confidence/health/maturity score or "N of M"
  completeness tally; confirm none exists (hard rule #9). [FR-012, SC-006]
- [ ] T026 [P] Confirm every file this feature added is ASCII, UTF-8 without BOM, and every path
  stays well under the Windows `MAX_PATH` budget (longest path:
  `tests/fixtures/golden/dax/refuse_no_column.reason.txt`, ~50 repo-relative characters). [FR-011]
- [ ] T027 Run the full quickstart.md validation end-to-end: steps 1 (baseline pass), 2 (US1 drift
  caught), 3 (US2 drift caught), 4 (missing-golden fails closed), 5 (US3 regeneration + diff
  review), 6 (no manifest/severity-posture change), 7 (no DB/env var required). Confirm every step
  behaves exactly as documented. [SC-001, SC-002, SC-003, SC-004, SC-005, SC-006]

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies -- read-only confirmation, can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 confirmations. BLOCKS all user stories (both the
  fixture directories and the shared normalization contract must exist before any golden test or
  golden file is authored).
- **User Story 1 (Phase 3)**: Depends on Foundational. Independent of US2 and US3 -- can be
  delivered alone as the MVP slice.
- **User Story 2 (Phase 4)**: Depends on Foundational only. Does NOT depend on US1 (different
  files, different subject: SQL text vs. DAX text) -- can proceed in parallel with Phase 3 if
  staffed.
- **User Story 3 (Phase 5)**: Depends on Foundational AND on US1's golden files existing (T010-T011)
  -- the regeneration script's correctness is verified (T021) against the goldens US1 already
  committed. Does not depend on US2.
- **Polish (Phase 6)**: Depends on all three user stories being complete.

### Within Each User Story

- Tests authored first (RED): T007-T009 (US1), T013-T015 (US2).
- Golden fixtures generated/copied second, turning tests GREEN: T010-T012 (US1), T016-T018 (US2).
- US3 (T019-T021) is additive tooling layered on top of US1's already-GREEN goldens.

### Parallel Opportunities

- T003 and T004 (Setup, read-only confirmations of independent fixture sets) can run in parallel.
- T016 and T017 (US2 golden SQL copies, different destination files) can run in parallel.
- Phase 3 (US1) and Phase 4 (US2) can be worked in parallel once Phase 2 (Foundational) is
  complete -- they touch entirely disjoint files (`test_dax_golden.py` + `golden/dax/*` vs.
  `test_warehouse_sql_golden.py` + `golden/sql/*`).
- T022-T026 (Polish verification tasks) can all run in parallel -- each reads a disjoint set of
  files and asserts a disjoint negative property.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (confirm seams).
2. Complete Phase 2: Foundational (fixture tree + normalization contract).
3. Complete Phase 3: User Story 1 (DAX/TMDL/refusal golden pin) -- T007-T012.
4. **STOP and VALIDATE**: `pytest -m unit tests/unit/test_dax_golden.py -v` passes; quickstart.md
   step 2's drift-detection procedure confirms SC-001.
5. This alone delivers the core value named in the spec ("catch silent generator drift... with
   the least architectural risk").

### Incremental Delivery

1. Setup + Foundational -> fixture tree and normalization contract ready.
2. Add User Story 1 -> test independently -> MVP delivered (P1, the deterministic generator half).
3. Add User Story 2 -> test independently -> the agent-authored-artifact regression lock (P2).
4. Add User Story 3 -> test independently -> the optional regeneration convenience (P3).
5. Polish -> confirm every negative/scope-guard requirement (FR-005, FR-009, FR-011, FR-012, and
   the MUST-NOT half of FR-001) that no single user story's own tests naturally exercise.

---

## Out of Scope (YAGNI / SCOPE GUARD -- do not add these tasks)

- **No `retail check` rule, no rule-id, no `docs/rules/rules-manifest.json` or
  `docs/rules/severity-posture.json` entry** -- this feature is pytest tests over committed
  fixtures only (collision-avoidance allocation; T024 verifies this stays true).
- **No `.gitattributes` entry** -- unlike feature 043's `text eol=lf` pin, this feature's FR-006
  normalization is done explicitly inside each test (T006), which research.md records as the
  deliberate, sufficient mechanism; no defense-in-depth `.gitattributes` line is added.
- **No `retail` CLI subcommand** for the regeneration helper -- FR-008's script (T019) stays a
  standalone script under `tests/fixtures/golden/`, never wired into `src/retail/cli.py`'s
  argparse surface, unlike 043's `retail manifest`.
- **No edit to `src/retail/dax_gen.py`, `src/retail/metric_drift.py`,
  `.claude/skills/retail-build-warehouse/SKILL.md`, or any existing test file** (FR-009; verified
  by T023 and the first half of T022).
- **No live database connection, no Power BI/PBIP surface, no F016 execution adapter, no
  F031-F033 spec-only runtime** -- every test added reads only committed files and calls a pure
  Python function (FR-005; SC-003).
- **No new metric contract `kind`, no new table, no expanded fixture corpus** -- the fixture
  corpus is fixed at what already exists on disk as of this spec (Assumptions section); expanding
  it is a follow-on feature, not this one.
- **No named-human approval request and no `unresolved-questions.md` entry** -- this feature
  raises no Principle-V judgment call (spec's Assumptions section; re-confirmed in plan.md's
  Constitution Check).

## FR Coverage Map (for the analyze stage)

| FR | Covered by |
|---|---|
| FR-001 | T005, T024 |
| FR-002 | T002, T007, T010, T012 |
| FR-003 | T008, T011, T012 |
| FR-004 | T004, T013, T016, T017, T018 |
| FR-005 | T015 |
| FR-006 | T006, T007, T008, T013 |
| FR-007 | T009, T014 |
| FR-008 | T019, T020, T021 |
| FR-009 | T001, T020, T022, T023 |
| FR-010 | T003 |
| FR-011 | T010, T011, T016, T017, T026 |
| FR-012 | T025 |
