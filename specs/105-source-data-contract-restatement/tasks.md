---

description: "Task list for Source Data-Contract -- Forward Schema + Arrival + Restatement Policy (HR12)"
---

# Tasks: Source Data-Contract -- Forward Schema + Arrival + Restatement Policy

**Input**: Design documents from `specs/105-source-data-contract-restatement/`
(spec.md, plan.md, research.md, data-model.md, quickstart.md)

**Prerequisites**: plan.md (required), spec.md (required for user stories),
research.md, data-model.md

**Tests**: Test tasks ARE included -- plan.md's Testing section explicitly
requires new fixture-driven unit tests for the rule module (`test_source_data_contract.py`)
plus edits to the three existing wiring-lockstep tests. All fixtures live under a
test-fixture root recognized by `is_test_path()`; no real table's contract is ever
authored (Principle V).

**Organization**: Tasks are grouped by user story (US1/US2/US3 from spec.md), in
priority order (P1, P1, P2). Per repo hard rule #8 (docs-first), the generic
template (FR-001) is authored and reviewable BEFORE any rule-wiring code exists, so
US1's doc/template tasks precede its rule-registration tasks.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, or SETUP/FOUND/POLISH)
- Every task names an exact repo-relative file path

## Path Conventions

Single project (Option 1 shape, per plan.md's Project Structure): `src/retail/rules/`,
`tests/unit/`, `templates/`, `mappings/<table>/`, `docs/` at repository root. No
frontend/backend split; no new top-level directory.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the live registration surfaces this feature must extend, before
authoring anything, so no task below hardcodes a stale count or a colliding id.

- [ ] T001 Re-read the live rule count and confirm no `HR12` entry already exists:
  `docs/rules/rules-manifest.json` (currently 55 entries at spec-authoring time --
  re-read live, do not trust the cached number) and `docs/rules/severity-posture.json`'s
  `registered` map. Confirm `HR12` is still a free id (not claimed by a
  concurrently-merged 089/090/093 draft) before proceeding.
- [ ] T002 [P] Confirm zero `mappings/**/source-data-contract.yaml` files exist on
  the tree yet (`mappings/retail_store_sales/`, `mappings/demo_sample_orders/`),
  confirming the green-landing posture from research.md -- no existing table
  artifact needs editing for this feature to land.
- [ ] T003 [P] Read `src/retail/rules/rule_sf1.py` and `src/retail/rules/assumption_coherence.py`
  in full as the two direct structural precedents (malformed-YAML handling shape
  and lazy-yaml-import + path-regex + template-exclusion + `is_test_path` shape,
  respectively) that Phase 3 (US1) implementation will mirror.

**Checkpoint**: Free id confirmed, precedents read, zero pre-existing contract files
to account for. Documentation authoring (Phase 3) can begin.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None required beyond Setup. This feature adds one independent static
rule with no shared new infrastructure (no new base model, no new stage, no new
directory) -- per plan.md's Complexity Tracking, HR12 reuses the existing
`@register` / `RuleContext` / `Finding` / `Severity` / `is_test_path` mechanism
unchanged. There is no blocking cross-story scaffolding to build.

**Checkpoint**: Foundation is the existing `retail.core` / `retail.registry`
mechanism (unchanged) -- proceed directly to User Story 1.

---

## Phase 3: User Story 1 - An analyst declares the forward contract before onboarding a table (Priority: P1) 🎯 MVP

**Goal**: A NEW generic template (`templates/source-data-contract.yaml`) exists with
its three required sections (schema, arrival, restatement), each pre-filled with a
distinctive sentinel placeholder; a NEW static rule HR12 verifies a table's filled
copy at `mappings/<table>/source-data-contract.yaml` is present and every section is
non-placeholder, citing the file as passing evidence; the contract's absence is
never penalized (opt-in).

**Note on registry wiring**: `src/retail/rules/__init__.py`'s side-effecting import
block is what makes `@register("HR12", ...)` populate the LIVE rule registry. The
seven wiring surfaces (research.md) -- including `__init__.py`, the manifest, the
severity posture, and `EXPECTED_RULE_IDS` -- MUST move together in one atomic group
(Phase 6), never split across phases: if `__init__.py` wired HR12 into the registry
here while the manifest/posture/`EXPECTED_RULE_IDS` still lacked it,
`test_wiring_meta_gate.py` / `test_rules_wiring.py` would go RED on any full
`pytest -m unit` run between this phase and Phase 6. Therefore User Story 1's tests
call the rule function DIRECTLY against a constructed `RuleContext` (module-level
import of `source_data_contract.py`, not a `retail check` / registry round-trip) --
this validates the rule's behavior fully before it is wired into the registry in
Phase 6.

**Independent Test**: Author a fixture `source-data-contract.yaml` with all three
sections filled with real (non-sentinel) values; calling
`source_data_contract`'s rule function directly against a `RuleContext` built over
that fixture returns zero Findings, with the contract's path citable as evidence.
The same direct call against a fixture table directory with no contract file
returns zero Findings (not-applicable). (Confirming this also holds end-to-end via
`retail check` happens once registry wiring lands in Phase 6, T023.)

### Docs/template authoring for User Story 1 (docs-first, hard rule #8 -- precedes rule code)

- [ ] T004 [US1] Author the NEW generic template `templates/source-data-contract.yaml`
  per data-model.md's exact shape: a header comment block naming this as a
  copy-me, per-table, forward-looking supplier agreement distinct from
  `source-map.yaml`'s descriptive map; a `schema` list with one illustrative entry
  carrying `name: "REPLACE_ME_COLUMN_NAME"` and `type: "REPLACE_ME_COLUMN_TYPE"`;
  an `arrival.cadence` field set to `"REPLACE_ME_ARRIVAL_CADENCE"`; a
  `restatement.policy` field set to `"REPLACE_ME_RESTATEMENT_POLICY"` with a
  comment pointing to 093/HR7's `load-policy.md` by reference (FR-012). No
  worked-example (C086/retail_store_sales) specifics anywhere in the file
  (Principle VII, FR-007). ASCII, UTF-8 without BOM (FR-011).
- [ ] T005 [P] [US1] Edit `docs/readiness/source-ready.md`: add one new row/sentence
  under an "Optional strengthening checks" heading (create the heading if absent)
  describing HR12 as an opt-in, evidence-only static check that does not change the
  stage's Required-artifacts table or its human-review gate procedure (research.md's
  Source Ready precedent note).

### Tests for User Story 1 (write FIRST, confirm they FAIL before implementation)

- [ ] T006 [P] [US1] Create the fixture-and-test file `tests/unit/test_source_data_contract.py`
  with fixtures under a test-fixture root recognized by `is_test_path()` (never a
  real table path). Import the rule's checking function DIRECTLY from
  `retail.rules.source_data_contract` (not via the registry/`retail check`, per the
  Note above) and call it against a constructed `RuleContext`. Initial US1 cases
  (expected to fail/error until T007 lands, since the rule module does not exist
  yet):
  - a fully-filled fixture contract (`schema` with a real name+type entry,
    `arrival.cadence` filled, `restatement.policy` filled) -> asserts **zero**
    Findings from the direct call, with the contract's path citable as evidence.
  - a fixture table directory with NO `source-data-contract.yaml` at all -> asserts
    **zero** Findings (not-applicable, opt-in per FR-002/SC-003).
  - the shipped `templates/source-data-contract.yaml` itself, scanned directly ->
    asserts it is EXCLUDED from evaluation (never self-flagged as an incomplete
    "table" contract) via the `_TEMPLATE_PATH` exclusion constant.

### Rule implementation for User Story 1

- [ ] T007 [US1] Create the NEW rule module `src/retail/rules/source_data_contract.py`:
  a compiled path regex `^mappings/[^/]+/source-data-contract\.ya?ml$` scanning
  `ctx.tracked_files`; a `_TEMPLATE_PATH = "templates/source-data-contract.yaml"`
  exclusion constant; an `is_test_path(rel)` exclusion (mirrors AL2); a lazy
  `import yaml` INSIDE the rule handler function only (never at module/package
  import time, per AL2's precedent and the constitution's stdlib-only-at-import
  wording). Define the checking function and decorate it with
  `@register("HR12", ...)` using a fixed, generic (no worked-example)
  title/description -- but do NOT touch `src/retail/rules/__init__.py` yet (that is
  T017, deferred to the atomic Phase 6 wiring group per the Note above; the module
  exists and is directly importable/callable for T006's tests without being
  registry-live). For each matched, non-excluded path: load the YAML, and for a
  structurally complete document (schema non-empty with every entry carrying both
  non-placeholder `name` and `type`; `arrival.cadence` non-blank and non-sentinel;
  `restatement.policy` non-blank and non-sentinel) emit NO Finding (pass-eligible,
  evidence = the file path per SC-001). (Malformed and incomplete branches are
  completed in Phase 4/US2 tasks T011-T012, since they are that story's own
  acceptance scenarios -- this task delivers only the pass/not-applicable happy
  path needed for US1's Independent Test.)
- [ ] T009 [US1] Confirm T006's US1 fixture tests (fully-filled fixture -> zero
  Findings; no-file fixture -> zero Findings; template-path exclusion) now PASS
  against the T007 implementation, calling the rule function directly. Run
  `pytest -m unit tests/unit/test_source_data_contract.py -q`. (Full `retail check`
  / registry-level confirmation happens once Phase 6 wires `__init__.py` -- see
  T023.)

**Checkpoint**: A table that fills the contract passes HR12 citing its path as
evidence; a table with no contract is not penalized. User Story 1 is independently
functional and testable (SC-001, SC-003 covered).

---

## Phase 4: User Story 2 - A declared-but-incomplete contract fails closed (Priority: P1)

**Goal**: HR12 fails CLOSED, naming the specific incomplete section (`schema`,
`arrival`, or `restatement`) or the file itself (on a YAML parse error), for any
present-but-incomplete or malformed contract -- never a silent pass, never an
undifferentiated failure message, never an unhandled exception.

**Independent Test**: Author a fixture contract with the `restatement` section left
as the template's sentinel token (all else filled); running `retail check` reports
HR12 failing for that fixture, naming `restatement` specifically. Repeat per
acceptance scenario for `arrival`, an empty `schema` list, a `schema` entry with a
`name` but no `type`, and a YAML parse error.

### Tests for User Story 2 (write FIRST, confirm they FAIL before implementation completes each branch)

- [ ] T010 [P] [US2] Extend `tests/unit/test_source_data_contract.py` with new
  fixture-driven cases (fixtures under the same test-fixture root as T006, never a
  real table):
  - `restatement.policy` left as the sentinel token, all else filled -> exactly one
    `Severity.ERROR` Finding naming `restatement` (spec Acceptance Scenario 1, US2).
  - `arrival.cadence` blank/missing, all else filled -> exactly one `ERROR` Finding
    naming `arrival` (spec Acceptance Scenario 2, US2).
  - `schema` is an empty list, all else filled -> exactly one `ERROR` Finding
    naming `schema` (spec Acceptance Scenario 3, US2).
  - a `schema` entry with a `name` but no `type`, all else filled -> exactly one
    `ERROR` Finding naming `schema` (spec Clarifications Q3).
  - a fixture file present but not valid YAML at all (a syntax error) -> exactly
    one `ERROR` Finding naming the FIXTURE FILE ITSELF (not a section), and no
    unhandled exception escapes the rule handler (spec Clarifications Q6, mirrors
    `rule_sf1.py`'s `except (OSError, yaml.YAMLError)` branch).
  - multiple sections incomplete at once (e.g. both `arrival` blank AND `schema`
    empty) -> Findings name EACH incomplete section individually, never a single
    undifferentiated "contract incomplete" message (FR-006).

### Rule implementation for User Story 2

- [ ] T011 [US2] Extend `src/retail/rules/source_data_contract.py` (from T007) with
  the per-section fail-closed branches: define the `SentinelToken` constants (one
  literal string per section family, matching the exact tokens shipped in
  `templates/source-data-contract.yaml`'s T004 content); implement the exact,
  case-sensitive, whitespace-normalized substring/equality check per data-model.md's
  `SentinelToken` entity (never a regex heuristic, never semantic judgment); for
  `schema`, fail closed when the list is empty OR any entry is missing `name`,
  missing `type`, or either field still holds its sentinel verbatim; for `arrival`
  and `restatement`, fail closed when the single free-text field is absent, blank,
  or still holds its sentinel verbatim; emit ONE `Severity.ERROR` Finding PER
  incomplete section (never a combined undifferentiated message), each `locator`
  set to the contract's repo-relative path.
- [ ] T012 [US2] Extend `src/retail/rules/source_data_contract.py` with the
  malformed-YAML branch: wrap the `yaml.safe_load` (and file read) in
  `except (OSError, yaml.YAMLError) as exc`, mirroring `rule_sf1.py`'s exact
  precedent shape, emitting exactly ONE `Severity.ERROR` Finding naming the FILE
  ITSELF (never a section, since none could be parsed), `locator` = the contract's
  path. Confirm no exception escapes the rule handler under this branch.
- [ ] T013 [US2] Confirm T010's US2 fixture tests now PASS against the T011/T012
  implementation. Run `pytest -m unit tests/unit/test_source_data_contract.py -q`
  and confirm every US1 case from T009 still passes (no regression).

**Checkpoint**: Both User Story 1 AND User Story 2 pass independently -- a filled
contract passes citing evidence, an incomplete or malformed one fails closed naming
the specific section or file (SC-001, SC-002, SC-003 all covered).

---

## Phase 5: User Story 3 - The contract stays a static, forward artifact with no live enforcement (Priority: P2)

**Goal**: Confirm (by inspection and by test) that HR12 never opens a database
connection, never compares a declared cadence or schema against any live signal,
and never detects a live restatement event -- it is a pure static file check, fully
evaluable with no DSN configured and no live database reachable.

**Independent Test**: Run `retail check` (or the unit suite) with no DSN configured
and no live database reachable; HR12 still evaluates fully and produces a
pass/fail/not-applicable result based solely on committed files.

### Tests for User Story 3

- [ ] T014 [P] [US3] Extend `tests/unit/test_source_data_contract.py` with a static-only
  confirmation case: run HR12 against the full T006/T010 fixture set with any
  environment DSN variable unset/cleared for that test (e.g. via `monkeypatch.delenv`
  on whatever env var the repo's DB layer reads), asserting identical Findings to
  the DSN-present case -- proving no live signal path is consulted (SC-004).
- [ ] T015 [P] [US3] Add a static source-inspection test (or extend T014) asserting
  `src/retail/rules/source_data_contract.py` contains no import of a database
  driver module and no reference to a DSN/connection-string constant or the repo's
  `db` extra -- a lightweight structural guard against future scope creep into a
  live check, not a substitute for T014's behavioral proof.

### Documentation confirmation for User Story 3

- [ ] T016 [US3] Confirm (no code change expected) that `specs/105-source-data-contract-restatement/quickstart.md`'s
  "Confirm HR12 stays static-only" section and spec.md's User Story 3 Acceptance
  Scenario 3 already state plainly that live arrival-time comparison and live
  restatement-event detection are deferred to a future `retail validate` extension;
  if HR12's Finding/pass message text (T007/T011) does not already avoid implying a
  live guarantee, edit `src/retail/rules/source_data_contract.py`'s message strings
  so they never state or imply that a passing HR12 result proves a live arrival
  match or that no restatement will ever occur (FR-003 wording check).

**Checkpoint**: All three user stories are independently functional. HR12 is
confirmed static-only with no live dependency (SC-004 covered); the full spec's
acceptance scenarios (US1, US2, US3) are covered by committed tests.

---

## Phase 6: Polish & Cross-Cutting Concerns (wiring lockstep + glossary + count reconciliation)

**Purpose**: Complete the seven-surface wiring discipline (research.md) so HR12 is
a fully registered, lockstep-consistent rule -- required for `retail check` itself
to recognize HR12 as real, and for the existing meta-gate tests to keep passing.
**All seven surfaces below (T008, T017-T020) move together as ONE ATOMIC GROUP**:
`__init__.py`'s side-effecting import is what makes `@register("HR12", ...)`
populate the LIVE rule registry, so it must land in the SAME commit as the
manifest/posture/`EXPECTED_RULE_IDS`/glossary updates -- never split across phases
(research.md's lockstep requirement; confirmed necessary by the wiring-flow review
of this task list).

- [ ] T008 [P] Wire `src/retail/rules/source_data_contract.py` into
  `src/retail/rules/__init__.py`: add the module to the existing side-effecting
  import block AND to `__all__` (package-symmetry, mirrors every other rule's
  wiring). This is the task that makes HR12 registry-live -- land it together with
  T017-T020, never earlier.
- [ ] T017 [P] Edit `tests/unit/test_rules_wiring.py`: add `"HR12"` to
  `EXPECTED_RULE_IDS`.
- [ ] T018 [P] Edit `docs/rules/rules-manifest.json`: append one new entry
  `{"id": "HR12", "title": "..."}` (generic title, no worked-example specifics,
  Principle VII) using the live-reconciled count from T001 (do not hardcode "56th"
  without re-confirming no sibling draft claimed it first).
- [ ] T019 [P] Edit `docs/rules/severity-posture.json`: append `HR12` under
  `registered` with its severity (`ERROR`, per data-model.md's `HR12Finding`
  entity -- the failure-mode severity; HR12 itself never emits a Finding on the
  pass/not-applicable paths).
- [ ] T020 [P] Edit `docs/glossary.md`: add an `HR12` row to the "Static check
  rules" table (rule id, one-line generic description, file/section it reads);
  bump any "Currently N rules in M families" prose to the live-reconciled count
  from T001, and append the `HR` family token to the family list ONLY IF no
  sibling HR-rule (HR3/HR4/HR7) has already added it in a merged commit by
  implement time (re-verify live, per research.md's caveat).
- [ ] T021 Edit `docs/quality/rule-count-claims.yaml`: reconcile the glossary-rule-count
  entry (and any other prose "N rules" claim this file tracks) to the new
  live-reconciled count from T001/T018. Depends on T018 landing first (needs the
  reconciled count).
- [ ] T022 Run `pytest -m unit tests/unit/test_wiring_meta_gate.py tests/unit/test_glossary_rule_table.py tests/unit/test_rules_wiring.py -q`
  and confirm all three lockstep tests pass with HR12 registered (no duplicate id,
  package symmetry intact, glossary/manifest/posture all agree). This is the FIRST
  point in the task sequence where a full `pytest -m unit` run is expected to be
  green with HR12 present in the registry.
- [ ] T023 [P] Run the full quickstart.md validation checklist end-to-end: `retail check`
  on the committed tree (zero Findings from HR12, since no real table has a
  contract yet); grep the rule module to confirm it never reads/writes
  `source-map.yaml`, `meta.freshness`, or `readiness-status.yaml`, and never raises
  a `stale_pass` blocker (FR-004, collision-avoidance allocation); confirm
  `templates/source-data-contract.yaml` was never merged into
  `templates/source-map.yaml`'s sister-artifact list (FR-010, SC-006).
- [ ] T025 [P] Verify SC-005: grep every artifact this feature authored or edited
  (`templates/source-data-contract.yaml`, `src/retail/rules/source_data_contract.py`,
  `docs/rules/rules-manifest.json`, `docs/rules/severity-posture.json`,
  `docs/glossary.md`) for a numeric confidence/health/maturity score or an "N of M"
  completeness-count pattern; confirm zero matches (hard rule #9).
- [ ] T026 [P] Verify SC-007: grep `templates/source-data-contract.yaml` and
  `src/retail/rules/source_data_contract.py`'s fixed Finding/message strings for
  any worked-example domain specific (`retail_store_sales`, `demo_sample_orders`,
  or any C086/pharmacy-specific column/table name); confirm zero matches
  (Principle VII).
- [ ] T024 Run the full unit suite once more (`pytest -m unit -q`) plus
  `ruff format --check src/ tests/` and `ruff check src/ tests/` for a final
  no-regression pass across the whole feature.

**Checkpoint**: HR12 is fully wired, lockstep-consistent, static-only, and every
spec.md Functional Requirement (FR-001 through FR-012; FR-013 remains an
intentionally OPEN Clarifications item this feature does not resolve, per Principle
V) is covered by at least one task above.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies -- can start immediately.
- **Foundational (Phase 2)**: Trivial/no-op for this feature (no shared scaffolding
  beyond the existing rule mechanism) -- does not block Phase 3.
- **User Story 1 (Phase 3)**: Depends on Setup (T001-T003) only. MVP slice. Tests
  call the rule function directly (not via the registry), so US1 does not depend on
  Phase 6's `__init__.py` wiring.
- **User Story 2 (Phase 4)**: Depends on User Story 1's rule module existing (T007)
  -- extends the SAME file (`source_data_contract.py`) rather than creating a new
  one, so it is sequential-on-file, not parallel, with US1's implementation tasks
  (T011/T012 both edit the file T007 created). Also does not depend on registry
  wiring.
- **User Story 3 (Phase 5)**: Depends on User Story 1 + 2's rule module being
  complete (T013) so its static-only tests have real Findings to compare against
  the DSN-absent case; can otherwise run independently of any new rule logic
  (Phase 5 adds no new branch to the rule itself, only confirmation tests plus an
  optional message-wording edit in T016).
- **Polish (Phase 6)**: Depends on all three user stories' rule logic being final
  (T007-T016) -- the wiring surfaces (T008 `__init__.py`, T017-T020 manifest/
  posture/wiring-test/glossary) must describe the FINISHED rule, not a partial one,
  and must all land in the SAME atomic group so the registry, manifest, posture,
  and `EXPECTED_RULE_IDS` never disagree at any commit boundary (see Phase 6's
  purpose note).

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other stories. Independently testable
  (fully-filled fixture -> pass; no-file fixture -> not-applicable).
- **User Story 2 (P1)**: Extends US1's rule module file; independently testable via
  its own fixtures once US1's module exists, but not parallel-safe against US1's
  own implementation tasks (same file).
- **User Story 3 (P2)**: Extends/confirms US1+US2's rule module; independently
  testable (no DSN configured, Findings unchanged) once US1+US2 land.

### Within Each User Story

- Docs/template tasks precede test tasks precede implementation tasks (docs-first,
  hard rule #8) -- T004/T005 before T006 before T007-T009.
- Tests are written FIRST and confirmed to fail (or be inapplicable) before the
  corresponding implementation task closes them out (T006 before T007-T009; T010
  before T011-T013; T014-T015 alongside T016).
- Each story's checkpoint task re-runs the full fixture suite to confirm no
  regression against prior stories.

### Parallel Opportunities

- T002 and T003 (Setup) can run in parallel with each other (and after T001).
- T005 (doc edit) can run in parallel with T006 (test authoring) -- different
  files, no dependency.
- T010, T014, T015 are additive test-file edits that can be drafted in parallel by
  different contributors before their corresponding implementation tasks close
  them out, though they land in the same physical test file
  (`tests/unit/test_source_data_contract.py`) so merge carefully if truly
  parallelized.
- T008, T017, T018, T019, T020 (the five independent wiring-surface file edits) can
  all run in parallel -- five different files, no dependencies among them (they
  must still all be committed together as one atomic group; "parallel to author,"
  not "safe to land separately"). T021 depends on T018's reconciled count. T025 and
  T026 (SC verification greps) can run in parallel with each other and with T023.

---

## Parallel Example: Phase 6 wiring surfaces

```bash
# Launch all five independent wiring-surface edits together (land as one atomic commit):
Task: "Wire source_data_contract into src/retail/rules/__init__.py (import block + __all__)"
Task: "Add HR12 to EXPECTED_RULE_IDS in tests/unit/test_rules_wiring.py"
Task: "Append HR12 entry to docs/rules/rules-manifest.json"
Task: "Append HR12 under registered in docs/rules/severity-posture.json"
Task: "Add HR12 row to docs/glossary.md's Static check rules table"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (confirm free id, zero pre-existing contract files).
2. Skip Phase 2 (no-op for this feature).
3. Complete Phase 3: User Story 1 (template + doc row + happy-path rule, tested by
   calling the rule function directly -- NOT yet wired into `__init__.py`).
4. **STOP and VALIDATE**: `pytest -m unit tests/unit/test_source_data_contract.py -q`
   passes for the fully-filled and no-file fixture cases.
5. Note: HR12 is NOT yet registry-live at this point -- `__init__.py` wiring (T008)
   is deliberately deferred to Phase 6's atomic wiring group, alongside the
   manifest/posture/glossary/wiring-test lockstep, so no full `pytest -m unit` run
   ever sees a partially-registered rule. `retail check` will not recognize HR12 as
   a live rule until Phase 6 completes. Treat Phase 3 alone as a
   code-complete-but-not-yet-wired MVP checkpoint, not a shippable end state.

### Incremental Delivery

1. Setup -> User Story 1 (template + happy-path rule) -> validate independently.
2. Add User Story 2 (fail-closed branches, same rule file) -> validate independently
   (all US1 cases still pass, all new US2 cases pass).
3. Add User Story 3 (static-only confirmation, no new rule branch) -> validate
   independently (DSN-absent run identical to DSN-present run).
4. Phase 6: wire all seven surfaces in one atomic commit (`__init__.py`, manifest,
   posture, glossary, `EXPECTED_RULE_IDS`, count-claims all move together, per the
   lockstep discipline) -> this is the FIRST point HR12 is registry-live and
   `retail check`-visible -> full suite green -> feature complete.

### Requirement Coverage Map (FR -> task, for the analyze stage)

- FR-001 (template, 3 sections) -> T004
- FR-002 (HR12 reserved, opt-in, fail-closed-when-present, malformed-YAML-is-malformed) -> T007, T011, T012
- FR-003 (no live DB/cadence/restatement detection) -> T007 (no live code path ever added), T014, T015, T016
- FR-004 (no source-map.yaml / meta.freshness / readiness-status.yaml read-or-write) -> T007, T023
- FR-005 (agent never invents values; template + check only) -> T004 (template ships sentinels only), T002 (no fabricated fixture-as-real-table)
- FR-006 (sentinel-token structural detection, per-section named failure) -> T011
- FR-007 (generic, no C086 specifics) -> T004, T018 (manifest title), T020 (glossary row)
- FR-008 (contract lives at `mappings/<table>/source-data-contract.yaml`, not merged into source-map.yaml) -> T004, T023
- FR-009 (no numeric score/completeness count) -> T007, T011, T012 (categorical Findings only)
- FR-010 (no new stage, no 6th mapping-gate artifact) -> T005, T023
- FR-011 (ASCII/UTF-8-no-BOM, short paths) -> T004 and every authored file
- FR-012 (restatement section references 093/HR7 by name, does not restate it) -> T004
- FR-013 (OPEN -- owner ruling required) -> intentionally NOT assigned an implementation task; T016 confirms the interim non-blocking stance is reflected in message wording only, without resolving the open question itself

---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps task to specific user story for traceability.
- Tests are included per plan.md's explicit Testing section; write them first per
  story and confirm they fail/are inapplicable before the implementation task that
  closes them out.
- No fixture is ever authored as a real table's committed contract
  (`mappings/retail_store_sales/` or `mappings/demo_sample_orders/`) -- Principle V
  forbids inventing owner-supplied facts about a real upstream system. All US1-US3
  coverage lives under a test-fixture root recognized by `is_test_path()`.
- FR-013's enforcement-strength question stays genuinely open; no task in this file
  resolves it, wires HR12 into `blocking_reasons[]`, or self-grants any stage a
  `pass`.
- Commit after each task or logical group; stop at any checkpoint to validate a
  story independently before proceeding to the next.
