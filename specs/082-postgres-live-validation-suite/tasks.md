# Tasks: Postgres live-validation suite (local, ephemeral, honest)

**Input**: `specs/082-postgres-live-validation-suite/plan.md`, `spec.md`, `research.md`,
`data-model.md`, `contracts/live-pass-contract.md`, `quickstart.md`

**IMPORTANT -- this is a task LIST for a future implementer, not an execution log.** No task
below has been executed by this spec-only chain. This chain stops before Phase 1 (Setup); it
produces the ordered plan an implementer would follow, per the task's boundaries (spec work
only, no `src/**` edits, no manifest edits, no CI edits, no commit/push/PR).

**STOP CONDITION (restated, load-bearing)**: after `tasks.md` is written, this chain proceeds
only to Step 4 (analyze). It performs no `git add`, no `git commit`, no push, no PR, and grants
no self-approval. `git add -A` is FORBIDDEN for this feature at implementation time too (see
Phase 6 note) -- every future commit must stage named files only.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on another unfinished task).
- **[Story]**: which user story (US1-US4) this task belongs to, or `Setup`/`Foundation`/`Polish`.

## Phase 1: Setup

- [ ] T001 Confirm the exact Python floor and existing `db`/`dev` extras in `pyproject.toml`
  (read-only check; no edit) to size the `livetest` extra's Python-version compatibility
  requirement before it is proposed for addition.
- [ ] T002 [P] Select and pin the specific Docker-orchestration library version
  (`research.md` Decision 1 recommends `testcontainers[postgres]`) and record the chosen
  version string in a short addendum note in `research.md` (a doc edit, not a manifest edit).
- [ ] T003 [P] Confirm Docker Desktop / Docker Engine is installed on the implementer's own
  machine and record its version, to ground the timeout budget in `quickstart.md`'s
  "Operational timing expectation" with a real measurement rather than an estimate.

**Checkpoint**: tooling choice confirmed; no code written yet.

---

## Phase 2: Foundational (blocking prerequisites for every user story)

**⚠️ CRITICAL**: no user-story task may start until this phase is complete.

- [ ] T004 Add the `livetest` optional extra to `pyproject.toml`
  `[project.optional-dependencies]` (bundling the library pinned in T002), keeping it disjoint
  from `dev` (CI continues to install no Docker-orchestration dependency) and from `db` (the
  driver extra stays driver-only). **Manifest edit -- explicitly out of scope for the spec-only
  chain that authored this task list; this is the first task a human-approved implementation
  PR would perform.**
- [ ] T005 Register the `live_db` marker in `pyproject.toml`'s `[tool.pytest.ini_options]
  markers` list, alongside the existing `unit` / `integration` entries (a one-line addition to
  the same list read in `plan.md`'s Technical Context). **Manifest edit; same out-of-scope note
  as T004.**
- [ ] T006 Create `tests/live_db/__init__.py` (empty, matching the existing `tests/unit/`
  package-marker convention) and `tests/live_db/seeds/` as a plain data directory (no `__init__`
  needed -- SQL files, not importable Python).
- [ ] T007 Write `tests/live_db/seeds/schema.sql` -- the shared DDL from `data-model.md`
  section 1 (`silver.stg_order_line`, `gold.dim_date`, `gold.dim_product`,
  `gold.fct_order_line`), including the `-1` unknown-member row in `gold.dim_product` and a
  `generate_series`-built `gold.dim_date` covering a small fixed date range.
- [ ] T008 Write `tests/live_db/conftest.py`'s Docker-availability probe function in isolation
  first (a small pure function returning `(available: bool, reason: str | None)`), before
  wiring it into a pytest fixture -- this is the function T017's precondition tests exercise
  directly, without needing a real Docker daemon in the *unit* test that tests the probe's logic
  against a mocked failure.
- [ ] T009 [P] Write `tests/live_db/conftest.py`'s container lifecycle fixture (session- or
  function-scoped, per `research.md` Decision 3): start the chosen library's Postgres container,
  wait for readiness within a bounded timeout (T003's measured value plus margin), yield a
  `ContainerHandle`-shaped object (`data-model.md` section 3), and guarantee teardown in a
  `finally`/fixture-teardown block even on a mid-test failure.
- [ ] T010 [P] Write the seed-execution helper (`tests/live_db/conftest.py` or a small
  `tests/live_db/_seed.py` module) that runs `schema.sql` plus a named scenario `.sql` file
  against a `ContainerHandle`'s DSN via `psycopg2`, raising a distinguishable exception on SQL
  error so the fixture can map it to the `"seed failed"` skip reason.
- [ ] T011 Wire T008-T010 together into the top-level `live_db_container` fixture: probe Docker
  (T008) -> skip with `"docker not available"` if absent -> check driver import -> skip with
  `"driver not installed"` if absent -> start container (T009) -> skip with `"container failed
  to start"` / `"port conflict"` on timeout -> seed (T010) -> skip with `"seed failed"` on error
  -> yield the ready, seeded `ContainerHandle`. This is the single fixture every US1-US3 test
  depends on; implements the full precondition chain in `contracts/live-pass-contract.md`.

**Checkpoint**: the fixture exists and, on a Docker-less machine, every test depending on it
skips honestly with a correct reason -- verify this manually before starting US1-US4 tasks (this
IS the FR-009 discipline; get it right once, here, rather than per-scenario).

---

## Phase 3: User Story 1 - Prove the four live checks against real materialized rows (P1) 🎯 MVP

**Goal**: one clean seeded run, all four checks executed live, zero ERROR findings, fed through
the 057 recorder once.

**Independent Test**: `pytest -m live_db tests/live_db/test_live_validate_clean.py -x -q` on a
Docker-available machine.

### Tests for User Story 1

- [ ] T012 [US1] Write `tests/live_db/seeds/seed_clean.sql` (`data-model.md` section 2 clean
  scenario: N order lines, all dates/products present, silver/gold sums equal to the penny).
- [ ] T013 [US1] Write `tests/live_db/test_live_validate_clean.py::test_clean_run_all_checks_pass`
  -- depends on `live_db_container` fixture seeded with `seed_clean.sql`; builds the four
  `PkTarget`/`DateCoverageTarget`/`OrphanTarget`/`ReconcileTarget` dataclasses pointed at the
  seeded table names; calls `validate.make_psycopg2_runner(handle.dsn)` and
  `validate.run_live_checks`; asserts the returned `Finding` list is empty. **Must FAIL first**
  (no fixture wired yet) before T007-T011 make it pass -- if written after Phase 2 is complete,
  confirm it fails for the RIGHT reason (assertion, not fixture-missing) before considering
  Phase 2 done.
- [ ] T014 [US1] Write
  `tests/live_db/test_live_validate_clean.py::test_clean_run_feeds_evidence_recorder` -- takes
  T013's real `Finding` list (empty) and calls
  `readiness_evidence.build_gold_ready_block(findings, table_identity="<generic
  table>", run_mode="live")`; asserts `status == "warning"` (never `"pass"` -- FR-012), asserts
  `evidence` is non-empty, asserts no field is a numeric score.

### Implementation for User Story 1

*(No `src/retail/` implementation -- User Story 1 is entirely test/fixture code per the
Constitution Check's "additive, test-side only" finding. "Implementation" here means the test
and fixture code itself.)*

- [ ] T015 [US1] Add a short human-readable print/log line per FR-014 in
  `test_live_validate_clean.py` (or a shared helper used by all US1-US3 tests) stating the run
  mode (`live`) and the table identity, so a contributor reading terminal output (not just the
  pytest PASS/FAIL) sees the mode explicitly.

**Checkpoint**: User Story 1 is independently testable and, on a Docker-available machine,
demonstrates the full happy path end-to-end including the 057 seam.

---

## Phase 4: User Story 2 - Prove each check catches its seeded defect (P1)

**Goal**: four isolated defect scenarios, each yielding exactly its expected ERROR finding and
no other.

**Independent Test**: `pytest -m live_db tests/live_db/test_live_validate_defects.py -x -q`.

### Tests for User Story 2

- [ ] T016 [P] [US2] Write `tests/live_db/seeds/seed_defect_pk_duplicate.sql`
  (`data-model.md` section 2).
- [ ] T017 [P] [US2] Write `tests/live_db/seeds/seed_defect_date_gap.sql`.
- [ ] T018 [P] [US2] Write `tests/live_db/seeds/seed_defect_orphan_fk.sql`.
- [ ] T019 [P] [US2] Write `tests/live_db/seeds/seed_defect_reconciliation_mismatch.sql`.
- [ ] T020 [US2] Write
  `tests/live_db/test_live_validate_defects.py::test_pk_duplicate_yields_v_rc2` -- seeds
  T016's scenario in its own container/schema instance, runs only `check_pk_uniqueness`
  (and, to prove isolation, the other three checks too), asserts exactly one `V-RC2` ERROR and
  zero ERRORs from the other three checks (depends on T016).
- [ ] T021 [US2] Write
  `tests/live_db/test_live_validate_defects.py::test_date_gap_yields_v_rc15` -- mirrors T020 for
  T017's scenario, asserting exactly one `V-RC15` ERROR and no cross-contamination (depends on
  T017).
- [ ] T022 [US2] Write
  `tests/live_db/test_live_validate_defects.py::test_orphan_fk_yields_v_rc16` -- mirrors T020
  for T018's scenario, asserting exactly one `V-RC16` orphan ERROR (depends on T018).
- [ ] T023 [US2] Write
  `tests/live_db/test_live_validate_defects.py::test_reconciliation_mismatch_yields_v_rc16` --
  mirrors T020 for T019's scenario, asserting exactly one `V-RC16` reconciliation ERROR naming
  the one-cent gap (depends on T019).

**Checkpoint**: all four RC checks are proven, live, to both pass on clean data (US1) and fail
correctly on their own defect (US2), each in isolation.

---

## Phase 5: User Story 3 - Prove the L4 value-check path live (P2)

**Goal**: one seeded gold measure, proven live-matching and live-mismatching.

**Independent Test**: `pytest -m live_db tests/live_db/test_live_value_check.py -x -q`.

### Tests for User Story 3

- [ ] T024 [US3] Write `tests/live_db/seeds/seed_value_check.sql` (`data-model.md` section 2).
- [ ] T025 [US3] Write
  `tests/live_db/test_live_value_check.py::test_matching_expected_value_no_finding` -- seeds
  T024's scenario, builds a `value_proxy.ExpectedValue` matching the seeded `sum(net_amount)`
  total exactly, runs `value_proxy.check_expected_value` via the real `QueryRunner`, asserts no
  finding (depends on T024, and on Phase 2's fixture).
- [ ] T026 [US3] Write
  `tests/live_db/test_live_value_check.py::test_mismatched_expected_value_yields_v_l4` -- same
  seed, an `ExpectedValue` perturbed beyond tolerance, asserts exactly one `V-L4` ERROR naming
  observed vs. expected (depends on T024).

**Checkpoint**: the L4 surface is proven live in both directions, completing all three
"prove an existing live surface actually runs against real data" stories.

---

## Phase 6: User Story 4 - Honest pending/skipped reporting (P1)

**Goal**: every named precondition failure resolves to an honest `SKIPPED` outcome with the
correct named reason, and repo-only checks stay completely unaffected.

**Independent Test**:
`pytest -m live_db tests/live_db/test_live_db_unavailable.py -x -q` (this test file itself does
NOT require Docker to be absent -- it mocks each precondition, so it is runnable and meaningful
on any machine, Docker or not).

### Tests for User Story 4

- [ ] T027 [P] [US4] Write
  `tests/live_db/test_live_db_unavailable.py::test_docker_absent_skips_with_reason` -- mocks
  T008's probe function to return `(False, "docker not available")`, invokes the fixture chain,
  asserts a `pytest.skip` is raised with that exact reason string (not a raw exception, not a
  silent pass).
- [ ] T028 [P] [US4] Write
  `tests/live_db/test_live_db_unavailable.py::test_driver_missing_skips_with_reason` -- mocks
  the `psycopg2` import check to fail, asserts skip reason `"driver not installed"`, and asserts
  this is a DIFFERENT string from T027's (distinct precondition, per `spec.md` edge cases).
- [ ] T029 [P] [US4] Write
  `tests/live_db/test_live_db_unavailable.py::test_container_start_timeout_skips_with_reason` --
  mocks T009's container-start wait to exceed the bounded timeout, asserts skip reason
  `"container failed to start"`.
- [ ] T030 [P] [US4] Write
  `tests/live_db/test_live_db_unavailable.py::test_port_conflict_skips_with_reason` -- mocks a
  port-bind failure distinct from a generic startup timeout, asserts skip reason
  `"port conflict"` (distinct string from T029's).
- [ ] T031 [P] [US4] Write
  `tests/live_db/test_live_db_unavailable.py::test_seed_failure_skips_with_reason` -- mocks
  T010's seed-execution helper to raise, asserts skip reason `"seed failed"`, and asserts NO
  `Finding`/check result is reported for that scenario (per `contracts/live-pass-contract.md`'s
  "no field combination can represent a hidden pass" invariant).
- [ ] T032 [US4] Write
  `tests/live_db/test_live_db_unavailable.py::test_all_five_reasons_are_distinct_strings` --
  asserts the five reason strings collected from T027-T031 (plus the harness-level-error case)
  are pairwise distinct (contract's "mutually distinguishable" verification requirement).
- [ ] T033 [US4] Write `tests/live_db/test_live_db_wiring.py::test_every_live_db_test_is_marked`
  -- scans `tests/live_db/*.py` (excluding `conftest.py` and this wiring test itself) and
  asserts every test function/class carries `@pytest.mark.live_db`, mirroring the existing
  `tests/unit/test_rules_wiring.py` pattern named in `research.md` Decision 3.
- [ ] T034 [US4] Write
  `tests/live_db/test_live_db_wiring.py::test_no_silent_exception_swallow_around_docker_calls`
  -- a static source scan (AST-based, mirroring `src/retail/rules/never_execute.py`'s approach
  referenced in `live_surface_boundary.py`) over `tests/live_db/**/*.py` asserting no bare
  `except Exception: pass` (or equivalent) wraps a call into the Docker-orchestration library or
  a `psycopg2.connect` call -- the static half of `contracts/live-pass-contract.md`'s
  verification approach.
- [ ] T035 [US4] Manually verify (documented as a task, not automatable in this list): on a
  machine with Docker genuinely stopped, run `pytest -m unit -x -q` and `retail check` and
  confirm both succeed identically to a Docker-running machine -- the concrete demonstration of
  SC-005.

**Checkpoint**: the honest-pending discipline is proven both by runtime tests (T027-T032) and by
static wiring guards (T033-T034), and the repo-only/live-DB independence is confirmed manually
(T035).

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T036 [P] Update `docs/readiness/gold-ready.md`'s "Required checks" table with a
  cross-reference note pointing to this feature as "the local, credential-free way to exercise
  this stage's live gate for development/review purposes" (a docs-only addition; does not
  change the stage's actual required-artifacts/required-checks contract).
  **[NEEDS-HUMAN-CONFIRM]**: whether this cross-reference belongs in `gold-ready.md` itself or
  only in this feature's own docs -- a small scope call for the implementer/reviewer, not
  resolved by this spec chain (kept out of `spec.md`'s 3-marker budget since it is a docs-
  placement nicety, not a scope fork).
- [ ] T037 [P] Add a short section to this repo's local-verification doc
  (`docs/quality/local-verification.md`, confirmed to exist per the earlier grep) documenting
  the opt-in `pytest -m live_db` command and its Docker prerequisite, consistent with
  `quickstart.md`.
- [ ] T038 Run the full `quickstart.md` walkthrough once, end to end, on the implementer's own
  Docker-available machine, and record the actual measured timing (replacing `quickstart.md`'s
  estimate with a real number).
- [ ] T039 Run `ruff format --check`, `ruff check`, and `pytest -m unit -x -q` (repo-only,
  mandatory local verification per this repo's rules) to confirm zero regression to the
  existing suite from this feature's additions.
- [ ] T040 Run `retail check` and confirm the rule count and exit code are unchanged from before
  this feature's tasks began (no new rule, no B3 regression -- the concrete check for FR-011).

---

## Dependencies & Execution Order

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2)**: depends on Setup; BLOCKS every user story (T011's fixture is the
  shared dependency of US1, US2, and US3's tests; US4's tests mock pieces of Phase 2's own code,
  so US4 also depends on Phase 2 existing, though not on it being run against a real Docker
  daemon).
- **User Story 1 (P1)**: depends on Phase 2. No dependency on US2/US3/US4.
- **User Story 2 (P1)**: depends on Phase 2. Independent of US1/US3 (different seed files,
  different test module) but conventionally sequenced after US1 since both are P1 and US1 is
  the smaller proof to land first.
- **User Story 3 (P2)**: depends on Phase 2. Independent of US1/US2.
- **User Story 4 (P1)**: depends on Phase 2 (mocks its internals). Independent of US1/US2/US3's
  seed files, but most valuable to land AFTER Phase 2's fixture exists (so there is a real
  fixture chain to mock against) -- can be developed in parallel with US1-US3 by a different
  contributor since it touches different files (`test_live_db_unavailable.py`,
  `test_live_db_wiring.py`) with no shared state.
- **Polish (Phase 7)**: depends on all four user stories being complete.

### Parallel opportunities

- T002 and T003 (Phase 1) are independent lookups, `[P]`.
- T009 and T010 (Phase 2) touch different concerns (container lifecycle vs. seed execution) and
  can be developed in parallel once T008 exists, `[P]`.
- T016-T019 (Phase 4, four seed `.sql` files) are fully independent files, `[P]`.
- T027-T031 (Phase 6, five independent precondition-mock tests) are fully independent, `[P]`.
- Once Phase 2 is complete, US1, US2, US3, and US4 can be staffed in parallel by up to four
  contributors with no file overlap (each owns its own test module and seed files).

---

## Implementation strategy

### MVP first

1. Phase 1 (Setup) -> Phase 2 (Foundational, the honest-skip fixture chain) -> Phase 3 (US1).
2. **STOP and manually verify**: on a Docker-available machine, US1's two tests pass and
   demonstrably hit a real container (e.g. temporarily break the seed on purpose and confirm the
   test fails, proving it isn't vacuously passing).
3. This MVP alone already demonstrates the feature's core claim (a real live run against real
   data) -- Phase 4-6 add breadth (defect detection, L4, honest-skip breadth) but Phase 3 is the
   smallest slice that is not a no-op.

### Incremental delivery

Phase 1+2 -> Phase 3 (US1, MVP) -> Phase 4 (US2) -> Phase 5 (US3) -> Phase 6 (US4) -> Phase 7
(Polish). Each phase's checkpoint is independently demonstrable before starting the next.

## Notes

- No task in this list has been executed. This is a plan for a future, separately-approved
  implementation effort.
- **`git add -A` is FORBIDDEN** for any future commit implementing these tasks -- stage named
  files only, consistent with this repo's git-safety rules and this feature's own "no hidden
  scope creep" discipline (an accidental `git add -A` could stage an in-progress Docker
  container's leftover file, a local `.env`, or an unrelated change).
- Any task touching `pyproject.toml` (T004, T005) or any file under `src/retail/` (none in this
  list -- confirmed zero) MUST pass through this repo's normal PR review + `retail check` +
  B3-guard gate before merge; none of that happens as part of writing this task list.
- Tests are included throughout (not optional) because `spec.md`'s acceptance scenarios and
  success criteria are themselves the tests -- there is no meaningful implementation of this
  feature that is not, itself, test/fixture code.
