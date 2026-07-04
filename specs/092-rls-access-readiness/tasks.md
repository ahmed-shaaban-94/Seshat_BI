---

description: "Task list for 092-rls-access-readiness"
---

# Tasks: Row-Level Security as a Semantic-Model-Ready Dimension

**Input**: Design documents from `specs/092-rls-access-readiness/`
**Prerequisites**: plan.md, spec.md, data-model.md

**Tests**: Included. `plan.md` names `tests/unit/test_hr6.py` as a required
deliverable (Project Structure) and every user story's Independent Test is
"run `retail check`, inspect findings" -- unit tests are the mechanical
encoding of that check, matching the shipped `test_g6.py` / `test_readiness_status.py`
convention.

**Organization**: Tasks are grouped by user story (US1/US2/US3). Because HR6's
scaffold (module + registration + gold-SQL reader) is shared by all three
stories inside ONE file (`src/retail/rules/hr6.py`) and ONE test file
(`tests/unit/test_hr6.py`), tasks that touch either file are **sequential**,
never `[P]`, even within a story -- `[P]` is reserved for genuinely
independent files (fixtures, docs, the template). Per repo hard rule #8
(docs-first), the template and gate-doc land in Setup/Foundational, before any
static-rule wiring task.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3), or
  `Setup`/`Foundational`/`Polish`
- **FR**: functional requirement id(s) this task satisfies, from `spec.md`
- Every task names an exact repo-relative file path

## Path Conventions

Single project (existing `src/retail/` governance checker + `templates/` +
`docs/` + `mappings/` + `tests/` layout, per plan.md "Project Structure").

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Test fixtures and directories the rule and its tests will read.
No rule code yet (docs-first, hard rule #8).

- [ ] T001 [P] [Setup] Create fixture directory
  `tests/fixtures/rls_roles/` (sibling of `tests/fixtures/pbip_params/`,
  `tests/fixtures/sql/`) to hold HR6 test fixtures. FR: (supports FR-004..FR-009 tests)

- [ ] T002 [P] [Setup] Author a fixture gold migration,
  `tests/fixtures/rls_roles/warehouse/migrations/0001_fixture_gold_star.sql`,
  declaring one generic `CREATE TABLE gold.dim_<placeholder>` (with at least
  two columns) and one generic `CREATE TABLE gold.fct_<placeholder>` (per
  `docs/conventions.md` `dim_`/`fct_` prefixes), modeled on the shape of
  `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` but with
  wholly generic names (no `_rss`/C086 tokens -- Principle VII, FR-015). This
  is the static "committed gold schema" HR6's tests will check role contracts
  against. FR-006, FR-007, FR-005 (fact-vs-dim), FR-015

- [ ] T003 [P] [Setup] Author well-formed and defective
  `rls-role-contract.yaml` fixture instances under
  `tests/fixtures/rls_roles/mappings/<fixture_table>/roles/`: one clean
  contract (`Clean.yaml`, binds to the fixture `gold.dim_*` column, `status:
  pass` with non-empty `evidence[]`); one with `filter.column: ""` (blank);
  one with `filter.column` naming a column absent from the fixture dim table;
  one with `filter.gold_table` pointing at `silver.*`; one with
  `filter.gold_table` pointing at a `gold` table absent from the fixture
  migration entirely; one with `filter.gold_table` pointing at the fixture's
  `gold.fct_*` table (fact, not dim); one `pass`-with-empty-`evidence: []`;
  two contracts sharing the same `name` (duplicate). FR-005, FR-006, FR-007,
  FR-008, FR-009

**Checkpoint**: Fixtures exist; no production code changed yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The docs-first artifacts (template + gate-doc) and the HR6
module scaffold every user story builds on. Per hard rule #8, the template
and doc-listing land BEFORE the rule is wired to run.

**CRITICAL**: No user-story finding-trigger work (Phase 3+) may start until
T004-T009 are complete.

- [ ] T004 [Foundational] Author the generic template
  `templates/rls-role-contract.yaml`, mirroring the declare/bind/readiness
  shape of `templates/metric-contract.yaml` (data-model.md Entity 1): `name`
  (stable, unique), `filter: {gold_table, column}` (gold-dimension-only per
  Principle III), `readiness: {status, evidence, blocking_reasons}` using
  exactly the four explicit statuses. Every value is an obvious placeholder
  (`<RoleName>`, `<dim_table>`, `<column>`) -- no C086/retail_store_sales
  token. Header comments cite `docs/metrics/metric-contract-store.md`'s
  precedent and state the collision-avoidance boundary (separate file; no key
  added to `metric-contract.yaml`/`kpi-pack.yaml`). FR-001, FR-002, FR-003,
  FR-013, FR-014, FR-015, FR-016

- [ ] T005 [Foundational] Edit `docs/readiness/semantic-model-ready.md`:
  add HR6 to the "Required checks" table row (alongside D1-D11/C1/R1/G6) and
  add an HR6 bullet to "Blocking reasons" (a role contract's filter binding
  is empty/unresolvable/fact-bound/duplicate-named, or claims `pass` with no
  evidence) -- doc-listing only, no rewrite of the stage's existing meaning
  (mirrors how G6 is already listed there). Also add one sentence noting the
  zero-role-contract case is an open Principle-V question (Q-ZERO-ROLES, not
  resolved by this stage's doc) so a reader does not infer either "required"
  or "optional" from silence. FR-017, FR-010

- [ ] T006 [Foundational] Create `src/retail/rules/hr6.py` scaffold: module
  docstring citing `docs/readiness/semantic-model-ready.md` and
  `templates/rls-role-contract.yaml` (mirrors `g6.py`'s docstring style);
  `@register("HR6", "RLS role contract filter binding is well-formed and
  approved")`; a pure `check_rls_role_bindings(ctx: RuleContext) ->
  Iterable[Finding]` function (empty findings list for now); a private
  `_iter_role_contract_files(ctx)` helper that globs
  `ctx.tracked_files` for `mappings/*/roles/*.yaml` and excludes
  `is_test_path()` fixtures (mirrors `g6.py`'s `_iter_param_files`); lazy
  `import yaml` INSIDE the check function body only (never at module scope --
  mirrors `readiness_status.py`/RS1's `import yaml  # lazy` comment).
  FR-004, FR-012

- [ ] T007 [Foundational] In `src/retail/rules/hr6.py`, add a private
  `_read_gold_schema(ctx)` helper that scans `warehouse/migrations/*.sql`
  (via the existing `iter_sql_files`/regex-family helpers in
  `src/retail/sql.py`, reused rather than reinvented -- research P5) and
  returns a static structure mapping `gold.<table_name> ->
  {columns: set[str], is_fact: bool}`, where `is_fact` is decided by the
  `fct_`/`dim_` table-name prefix convention already fixed in
  `docs/conventions.md` (Clarification C3) -- no live database connection
  (Principle VIII). FR-006, FR-007, FR-012

- [ ] T008 [Foundational] Wire the new module into
  `src/retail/rules/__init__.py`: add `hr6` to both the side-effecting
  import list and `__all__` (alphabetically placed, matching the existing
  ordering) so `@register("HR6", ...)` fires when `retail check` starts --
  this is the "only wiring step" the module's own docstring requires. FR-004

- [ ] T009 [Foundational] Create empty test scaffold
  `tests/unit/test_hr6.py` with the module docstring, `pytestmark =
  pytest.mark.unit`, a `_ctx(...)` fixture-context helper pointed at
  `tests/fixtures/rls_roles/` (mirrors `test_g6.py`'s `_ctx()` helper), and
  one smoke test asserting `check_rls_role_bindings` returns `[]` findings
  against a repo root with no `mappings/*/roles/*.yaml` files at all (the
  zero-contract case, T003's fixtures not yet referenced) -- this smoke test
  is also the FIRST enforcement point for Q-ZERO-ROLES: it MUST NOT assert
  or encode a "pass" or "block" outcome for the zero-contract case, only that
  no finding is fabricated where none is declared. FR-010

**Checkpoint**: Template exists and is documented in the gate doc; the HR6
module registers and is wired into `retail check`'s rule set (returning zero
findings so far); test scaffold exists. User story work can now begin.

---

## Phase 3: User Story 1 - A declared role with no real filter binding fails the gate (Priority: P1) - MVP

**Goal**: HR6 fails closed (Severity.ERROR) on every structurally broken
role-contract binding, and that finding surfaces in the table's Semantic
Model Ready `blocking_reasons[]`.

**Independent Test**: Author one `rls-role-contract.yaml` with a filter
expression naming a non-existent gold column (or an empty filter column),
run `retail check`, confirm an HR6 finding names the role and the unresolved
column and blocks the stage.

### Tests for User Story 1

- [ ] T010 [US1] In `tests/unit/test_hr6.py`, add
  `test_blank_filter_column_fails()` using T003's blank-column fixture --
  assert exactly one `Finding(rule_id="HR6", severity=Severity.ERROR, ...)`
  whose message names the role and states the filter column is missing/blank.
  FR-005

- [ ] T011 [US1] In `tests/unit/test_hr6.py`, add
  `test_nonexistent_gold_column_fails()` using T003's unresolvable-column
  fixture against T002's fixture gold migration -- assert an HR6 ERROR
  finding naming the role, the referenced gold table, and the unresolved
  column. FR-006

- [ ] T012 [US1] In `tests/unit/test_hr6.py`, add
  `test_silver_or_bronze_binding_fails()` and
  `test_gold_table_absent_from_migrations_fails()` using T003's
  silver-binding and absent-gold-table fixtures -- assert an HR6 ERROR
  finding for each (Principle III boundary). FR-007

- [ ] T013 [US1] In `tests/unit/test_hr6.py`, add
  `test_fact_table_binding_hard_fails()` using T003's `gold.fct_*` fixture --
  assert `Severity.ERROR` (never `Severity.WARNING`, per spec Clarification
  C1) with a message stating the binding must target a dimension, not a
  fact, table. FR-005, Clarification C1

- [ ] T014 [P] [US1] Add `tests/unit/test_readiness_status.py`-style
  integration coverage in `tests/unit/test_hr6.py` (or a focused new test
  function in the same file, added sequentially after T010-T013) confirming
  that when a repo's `mappings/<table>/readiness-status.yaml` is present
  alongside a broken role contract, the existing `retail-semantic-check`
  gate-blocking path (RS1 / `semantic_model_ready.blocking_reasons[]`)
  is the one that surfaces the HR6 finding -- i.e. this test documents/
  confirms the WIRING contract (an ERROR-severity `Finding` blocks the
  stage via the existing exit-code path), it does NOT add new computation to
  `readiness_status.py`. FR-011

  (Note: not `[P]` in practice once sequenced after T010-T013 in the same
  file; marked here only to flag it as conceptually independent of the
  specific defect-trigger tests above. Implement it after T010-T013 land.)

### Implementation for User Story 1

- [ ] T015 [US1] In `src/retail/rules/hr6.py`,
  `check_rls_role_bindings()`: for each committed role-contract file
  (via `_iter_role_contract_files`), parse the YAML (lazy `import yaml`),
  and emit `Finding(rule_id="HR6", severity=Severity.ERROR, ...)` when
  `filter.column` is missing, empty, or blank (whitespace-only). Locator is
  the repo-relative contract file path (mirrors `g6.py`'s `locator=rel`
  style). FR-005

- [ ] T016 [US1] In `src/retail/rules/hr6.py`, extend
  `check_rls_role_bindings()` to resolve `filter.gold_table` +
  `filter.column` against `_read_gold_schema(ctx)` (T007): emit an ERROR
  finding when the table is `silver.*`/`bronze.*`, when the table is
  `gold.*` but absent from the committed migrations, or when the table
  exists but the named column is not in its column set. Message names the
  role, the table, and the column (SC-002). FR-006, FR-007

- [ ] T017 [US1] In `src/retail/rules/hr6.py`, extend
  `check_rls_role_bindings()` to emit an ERROR finding (never WARNING) when
  the resolved `gold_table` is fact-classified (`is_fact: true` from T007's
  prefix check) rather than dimension-classified -- Clarification C1's hard
  fail. FR-005, Clarification C1

- [ ] T018 [US1] Run `pytest tests/unit/test_hr6.py -m unit -x -q` and
  confirm T010-T014 all pass; fix `hr6.py` (not the tests) on any mismatch,
  per repo testing rule "fix implementation, not tests." (verification step,
  no FR of its own -- confirms FR-005, FR-006, FR-007, FR-011, Clarification C1)

**Checkpoint**: HR6 fails closed on every structural-defect trigger in scope
for US1; a broken role contract now blocks Semantic Model Ready the same way
a D1-D11/G6 finding already does.

---

## Phase 4: User Story 2 - A well-formed role contract binds cleanly and clears HR6 (Priority: P1)

**Goal**: A correctly filled role contract produces zero HR6 findings, so
the gate is reachable, not just failable.

**Independent Test**: Point a contract's `filter.column` at a column
confirmed present on the bound `gold` dimension table, re-run `retail
check`, confirm no HR6 finding is emitted for that role.

### Tests for User Story 2

- [ ] T019 [US2] In `tests/unit/test_hr6.py`, add
  `test_well_formed_binding_produces_no_finding()` using T003's `Clean.yaml`
  fixture (real gold dim column, unique name, `status: pass` +
  non-empty `evidence[]`) -- assert `check_rls_role_bindings()` returns `[]`
  for that fixture. FR-003 (implicitly, via a passing gold-dim binding),
  SC-003

- [ ] T020 [US2] In `tests/unit/test_hr6.py`, add
  `test_hr6_findings_never_carry_a_numeric_score()` -- for every `Finding`
  produced across ALL of T010-T013's defect fixtures, assert
  `finding.message` contains no numeric confidence/health/maturity token and
  the `Finding` dataclass carries no such field (grep-style substring
  assertions, mirroring how other rule test suites guard hard rule #9).
  FR-014, SC-004

### Implementation for User Story 2

- [ ] T021 [US2] Run `pytest tests/unit/test_hr6.py -m unit -x -q` and
  confirm T019-T020 pass without further `hr6.py` changes -- if a change IS
  needed (e.g. the well-formed fixture unexpectedly trips a T015-T017
  check), fix `src/retail/rules/hr6.py`'s check logic, not the fixture or
  the test, per repo testing rule. No new finding-trigger code is expected
  in this story; it is primarily a confirmation slice on top of US1's
  triggers (per plan.md, HR6 has one shared implementation surface). FR-003,
  SC-003, FR-014, SC-004

**Checkpoint**: HR6 both fails on defects (US1) and passes cleanly on a
correctly filled contract (US2) -- the gate is usable, not just punitive.

---

## Phase 5: User Story 3 - HR6 flags a role contract that is present but never reviewed/approved (Priority: P2)

**Goal**: A structurally-valid-looking contract that was never actually
reviewed (`status: pass` with no evidence, or an unaddressed
`not_started`/`blocked`) is still caught -- HR6 does not treat "well-formed"
as a substitute for "approved."

**Independent Test**: Author a role contract with a well-formed filter
binding but `readiness.status: pass` and empty `evidence[]`; run `retail
check`; confirm HR6 flags the missing evidence rather than accepting the
unearned pass.

### Tests for User Story 3

- [ ] T022 [US3] In `tests/unit/test_hr6.py`, add
  `test_pass_with_empty_evidence_fails()` using T003's
  pass-with-empty-evidence fixture -- assert an HR6 ERROR finding stating a
  `pass` status requires non-empty evidence. FR-008

- [ ] T023 [US3] In `tests/unit/test_hr6.py`, add
  `test_duplicate_role_name_fails()` using T003's two same-`name` fixtures
  -- assert an HR6 ERROR finding identifying the duplicate name and both
  contract file locators. FR-009

- [ ] T024 [US3] In `tests/unit/test_hr6.py`, add
  `test_not_started_and_blocked_are_surfaced_not_silently_passed()`: for a
  `status: not_started` fixture, assert HR6 does not emit a "pass" signal
  for that role (i.e. no finding suppresses/overrides the fact that
  Semantic Model Ready must not treat this role as cleared); for a `status:
  blocked` fixture with a non-empty `blocking_reasons[]`, assert HR6 does
  not re-decide or discard the recorded reason (structural check only, per
  FR-012). This test documents behavior rather than asserting a specific
  new `Finding` -- HR6's role is to not launder an unreviewed contract into
  a false pass, not to invent new severities for lifecycle states already
  self-declared. FR-008 (evidence-shape boundary), Principle VIII

### Implementation for User Story 3

- [ ] T025 [US3] In `src/retail/rules/hr6.py`, extend
  `check_rls_role_bindings()` to emit an ERROR finding when
  `readiness.status == "pass"` and `readiness.evidence` is empty (mirrors
  the metric-contract precedent cited in FR-008). FR-008

- [ ] T026 [US3] In `src/retail/rules/hr6.py`, extend
  `check_rls_role_bindings()` to detect two or more committed role contracts
  sharing the same `name` (case-sensitive exact match, consistent with the
  template's "MUST be UNIQUE" note) and emit one ERROR finding identifying
  both contract file locators. FR-009

- [ ] T027 [US3] Run `pytest tests/unit/test_hr6.py -m unit -x -q` and
  confirm T022-T024 pass; fix `hr6.py` on any mismatch. FR-008, FR-009

**Checkpoint**: All three user stories are independently satisfied; HR6 now
covers every FR-005..FR-009 trigger in `data-model.md`'s Entity 3 table.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Registry/manifest regeneration, MUST-NOT verifications, and the
full-suite check. Depends on all three user stories being complete.

- [ ] T028 [Polish] Regenerate `docs/rules/rules-manifest.json` by running
  the existing `retail manifest` CLI command (per `src/retail/manifest.py`)
  now that HR6 is registered -- confirm the new `{"id": "HR6", "title": "..."}`
  entry appears alongside `G6` in the golden inventory (the manifest-snapshot
  test fails closed on a stale manifest, per plan.md). Must run AFTER T008
  (registration) and cannot be `[P]` with any `hr6.py` edit. FR-004

- [ ] T029 [Polish] Regenerate `docs/rules/severity-posture.json` by
  running the existing `retail severity-posture` CLI command (per
  `src/retail/severity_posture.py`) so the posture snapshot records HR6 as
  an `ERROR`-severity rule (never `WARNING`, per Clarification C1) -- confirm
  the golden record's `test_scaffold.py`-style byte comparison stays green.
  FR-005 (severity posture), Clarification C1

- [ ] T030 [P] [Polish] Grep-verify the collision-avoidance allocation held:
  `git diff` (or a targeted `grep -n` ) confirms 0 lines changed in
  `templates/metric-contract.yaml` and `templates/kpi-pack.yaml` by this
  feature's commits. FR-002, SC-005

- [ ] T031 [P] [Polish] Grep-verify genericity: confirm
  `templates/rls-role-contract.yaml` and `src/retail/rules/hr6.py` contain
  no `retail_store_sales`, `_rss`, or other C086-specific token (a
  case-insensitive grep for the known C086 table/column names used
  elsewhere in the repo, e.g. `dim_location_rss`, `dim_customer_rss`,
  `fct_sales_rss`). FR-015, SC-007

- [ ] T032 [P] [Polish] Grep-verify hard rule #9: confirm neither
  `templates/rls-role-contract.yaml` nor `src/retail/rules/hr6.py` nor
  `tests/unit/test_hr6.py` contains a numeric confidence/health/maturity
  field name or an "N of M" completeness phrasing. FR-014, SC-004

- [ ] T033 [Polish] Confirm `docs/readiness/semantic-model-ready.md`'s
  "Required checks" and "Blocking reasons" tables list HR6 (re-check T005's
  edit landed and matches the shipped rule's actual behavior after
  T015-T026). FR-017, SC-006

- [ ] T033b [P] [Polish] Confirm `templates/rls-role-contract.yaml`,
  `src/retail/rules/hr6.py`, and `tests/unit/test_hr6.py` are all ASCII,
  UTF-8 without BOM, and that every new repo-relative path introduced by
  this feature (`mappings/<table>/roles/<RoleName>.yaml`,
  `tests/fixtures/rls_roles/...`) stays comfortably under the Windows
  260-char budget (spot-check the longest fixture path). FR-016

- [ ] T034 [Polish] Run the full verification sequence required before any
  commit in this repo: `ruff format --check src/ tests/`, `ruff check src/
  tests/`, `pytest -m unit -x -q` (full suite, not just `test_hr6.py`, to
  catch any cross-rule regression e.g. in the rules-manifest snapshot test
  or the severity-posture snapshot test), then `retail check` against the
  live repo tree to confirm HR6 registers and runs cleanly with zero
  committed `rls-role-contract.yaml` files present (the real,
  not-yet-owner-filled state) -- confirm this zero-contract run does NOT
  itself fail the build and does NOT itself claim any stage `pass` (Q-ZERO-
  ROLES non-negotiable constraint from plan.md's Constitution Check).
  FR-010, FR-012, FR-018

**Checkpoint**: HR6 is registered, documented, tested, generic, and
non-fabricating; the manifest and posture snapshots are current; the
zero-contract state is neither a fabricated pass nor an unauthorized block.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies -- can start immediately. T001-T003
  are `[P]` (distinct fixture files).
- **Foundational (Phase 2)**: Depends on Setup (tests reference Setup's
  fixtures). T004 and T005 are independent files and could run in parallel
  with each other, but NOT with T006-T009 (T006 depends on nothing from
  T004/T005 directly, but is sequenced after per hard rule #8: doc/template
  before rule-wiring). T006 -> T007 -> T008 -> T009 are sequential (same
  file `hr6.py`, then its registration, then its test scaffold). BLOCKS all
  user stories.
- **User Stories (Phase 3-5)**: All depend on Foundational (Phase 2)
  completion. Because they share `hr6.py` and `test_hr6.py`, US1 -> US2 ->
  US3 is the SAFE sequential order (US2's "does the well-formed case still
  pass" test is most meaningful once US1's triggers exist; US3 extends the
  same file further). Attempting true parallel multi-developer work across
  US1/US2/US3 would collide on both shared files -- this is called out
  explicitly, unlike the template's default parallel-story assumption.
- **Polish (Phase 6)**: Depends on all three user stories being complete.
  T028/T029 depend on T008's registration and on all finding-trigger code
  (T015-T017, T025-T026) being final, since both regenerate goldens FROM the
  live rule behavior. T030-T032 are `[P]` (independent grep/diff checks,
  read-only, no shared file writes).

### Within Each User Story

- Tests are written first (T010-T014, T019-T020, T022-T024) and must FAIL
  before the corresponding implementation task (T015-T017, T021, T025-T026)
  makes them pass -- TDD RED -> GREEN, per repo testing rule.
- Within `hr6.py`, each implementation task ADDS to the same
  `check_rls_role_bindings()` function body -- strictly sequential, never
  `[P]`, regardless of story boundary.

### Parallel Opportunities

- T001, T002, T003 (Setup: distinct fixture files) -- run together.
- T004 (template) and T005 (doc edit) touch different files and have no
  data dependency on each other -- may run together, both before T006.
- T030, T031, T032 (Polish: independent read-only verification checks) --
  run together.
- No task inside `src/retail/rules/hr6.py` or `tests/unit/test_hr6.py` is
  ever `[P]` with another task touching the same file -- this is a
  deliberate departure from the template's default (see Organization note
  above).

---

## FR Coverage Map (verification aid for the analyze stage)

| FR | Covered by |
|---|---|
| FR-001 | T004 |
| FR-002 | T004, T030 |
| FR-003 | T004, T019, T021 |
| FR-004 | T006, T008, T028 |
| FR-005 | T003, T010, T013, T015, T017, T018, T029 |
| FR-006 | T002, T003, T007, T011, T016, T018 |
| FR-007 | T002, T003, T007, T012, T016, T018 |
| FR-008 | T003, T022, T024, T025, T027 |
| FR-009 | T003, T023, T026, T027 |
| FR-010 | T005, T009, T034 (recorded open + non-default enforced; NOT resolved) |
| FR-011 | T014, T018 |
| FR-012 | T006, T007, T024, T034 |
| FR-013 | T004 |
| FR-014 | T004, T020, T032 |
| FR-015 | T002, T004, T031 |
| FR-016 | T004, T033b |
| FR-017 | T005, T033 |
| FR-018 | T034 |

Every FR-001..FR-018 maps to at least one task. FR-010 and FR-013 (the
Principle-V MUST-NOTs) are covered by record-and-enforce tasks, never by a
task that resolves the underlying who-sees-what question -- that ruling
stays with a named human, outside this tasks.md, per the spec's Scope Guard.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational).
2. Complete Phase 3 (US1) -- HR6 fails closed on every structural defect.
3. **STOP and VALIDATE**: run `pytest tests/unit/test_hr6.py -m unit -x -q`
   and `retail check` against a repo tree seeded with T003's defect
   fixtures; confirm HR6 findings appear and block.
4. This is already a coherent, demoable slice (a broken role contract now
   fails the gate) even before US2/US3 land.

### Incremental Delivery

1. Setup + Foundational -> template exists, doc lists HR6, module registers.
2. Add US1 -> HR6 fails on defects (MVP).
3. Add US2 -> HR6 passes cleanly on a correct contract (gate is usable, not
   just punitive).
4. Add US3 -> HR6 also catches the unearned-pass and duplicate-name
   loopholes (hardening).
5. Polish -> manifest/posture regenerated, genericity and hard-rule-#9
   verified, full suite green.

### Sequencing Reality (not a parallel-team feature)

Unlike the template's default multi-developer parallel-story assumption,
this feature's entire implementation surface is TWO files
(`src/retail/rules/hr6.py`, `tests/unit/test_hr6.py`) plus a handful of
docs/fixtures. One implementer works US1 -> US2 -> US3 -> Polish in that
order; the only genuine parallelism is within Setup (T001-T003), within
Foundational's doc/template pair (T004-T005), and within Polish's read-only
verification checks (T030-T032).
