---

description: "Task list for 103-currency-unit-contract"
---

# Tasks: Currency / Unit-of-Measure Contract

**Input**: Design documents from `specs/103-currency-unit-contract/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md, quickstart.md

**Tests**: Included. `plan.md`'s Project Structure names `tests/unit/test_hr11.py`
as a required deliverable, and every user story's Independent Test is "author
fixtures, run `retail check`, inspect findings" -- unit tests are the
mechanical encoding of that check, matching the shipped `test_g6.py` /
`test_additivity_consistency.py` convention.

**Organization**: Tasks are grouped by user story (US1/US2/US3), following the
shape `specs/092-rls-access-readiness/tasks.md` (HR6) already demonstrates for
folding one new single-purpose static rule into the EXISTING Semantic Model
Ready gate. Because HR11's scaffold, its finding-trigger logic, and its tests
all live in ONE rule file (`src/retail/rules/hr11.py`) and ONE test file
(`tests/unit/test_hr11.py`), every task touching either file is **sequential**,
never `[P]`, even across story boundaries -- `[P]` is reserved for genuinely
independent files (fixtures, the two template edits, docs, read-only greps).
Per repo hard rule #8 (docs-first), the two template edits and the gate-doc
edit land in Foundational, BEFORE any HR11 rule-wiring task.

**Unlike 092**: 092 added a wholly NEW template file and its Polish check was
"confirm 0 lines changed in `metric-contract.yaml`." This feature is the
opposite shape -- it EDITS two already-shipped templates in place
(`templates/source-map.yaml` gains `columns[].unit` + `columns[].currency`;
`templates/metric-contract.yaml` gains ONLY the top-level `unit` key). The
Polish verification here therefore confirms the diffs LANDED, additively, and
carry no forbidden key -- never that a diff is empty (research.md P1).

**FR-013 / FR-014 / Q2a stay OPEN.** Per plan.md's Constitution Check
("Two open questions carried forward -- explicitly NOT decided here"), no task
below may pick either FR-013 detection-scope extreme, and no task below may
adopt a settled block/warn/no-op answer for FR-014's undeclared-value posture.
US1/US2/US3 fixtures are authored on the UNAMBIGUOUS-SUM shape (2+
`binds_to.columns[]` entries WITH an explicit `definition.aggregation: sum`
block) -- a shape that is in-scope for HR11 under *either* candidate FR-013
reading, so the unit/currency comparison can be tested without the tasks
silently resolving FR-013. The disputed shapes (a no-`definition` metric, a
`[numerator, denominator]` ratio pair, a null-vs-non-null pairing) are
explicitly DEFERRED, not fixture-encoded as pass or fail.

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

**Purpose**: Fixture directories and fixture files the rule and its tests
will read. No rule code yet (docs-first, hard rule #8).

- [ ] T001 [P] [Setup] Create fixture directory
  `tests/fixtures/currency_unit_contract/` (sibling of `tests/fixtures/rls_roles/`,
  `tests/fixtures/contracts/`) to hold HR11 test fixtures. FR: (supports
  FR-004..FR-011 tests)

- [ ] T002 [P] [Setup] Author a fixture source-map,
  `tests/fixtures/currency_unit_contract/mappings/fixture_table/source-map.yaml`,
  with `columns[]` entries covering every join/comparison case HR11 must
  handle: two quantity columns declaring different `unit` values (e.g.
  `rename_to: weight_kg` / `unit: "kg"` and `rename_to: unit_count` /
  `unit: "each"`); two quantity columns declaring the SAME `unit` (e.g.
  `rename_to: secondary_weight_kg` / `unit: "kg"`); two money columns
  declaring different `currency` values (e.g. `rename_to: revenue_egp` /
  `currency: "EGP"` and `rename_to: revenue_usd` / `currency: "USD"`); two
  money columns declaring the SAME `currency`; and one column with
  `unit: null` / `currency: null` (undeclared, for the FR-010/derived-column
  path only -- NOT wired into any FR-014 pass/fail assertion). Wholly generic
  names (no `_rss`/C086 token -- Principle VII, FR-016). FR-001, FR-004,
  FR-005, FR-006, FR-007

- [ ] T003 [P] [Setup] Author well-formed and defective metric-contract
  fixture instances under
  `tests/fixtures/currency_unit_contract/mappings/fixture_table/metrics/`,
  each with an explicit `definition: {aggregation: sum, ...}` block (the
  unambiguous-sum shape both FR-013 candidate readings agree is in-scope):
  `ClashingUnit.yaml` (`binds_to.columns: [weight_kg, unit_count]`);
  `CleanUnit.yaml` (`binds_to.columns: [weight_kg, secondary_weight_kg]`,
  both `unit: "kg"`); `ClashingCurrency.yaml`
  (`binds_to.columns: [revenue_egp, revenue_usd]`); `CleanCurrency.yaml`
  (both same `currency`); `SingleColumn.yaml`
  (`binds_to.columns: [weight_kg]`, one entry only -- FR-011 no-op case);
  `UnresolvableColumn.yaml` (`binds_to.columns` names a column absent from
  T002's `columns[].rename_to` list, e.g. a `derived_columns`-only name).
  FR-003, FR-005, FR-006, FR-010, FR-011

- [ ] T004 [P] [Setup] Author one metric-contract fixture,
  `tests/fixtures/currency_unit_contract/mappings/fixture_table_missing_map/metrics/OrphanMetric.yaml`,
  whose `binds_to.columns[]` lists two or more columns, but WITHOUT a sibling
  `mappings/fixture_table_missing_map/source-map.yaml` file at all (the
  missing/unreadable source-map path). FR-010

**Checkpoint**: Fixtures exist; no production code changed yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The docs-first artifacts (the two template edits + the gate-doc
edit) and the HR11 module scaffold every user story builds on. Per hard rule
#8, the templates and the doc-listing land BEFORE the rule is wired to run.

**CRITICAL**: No user-story finding-trigger work (Phase 3+) may start until
T005-T010 are complete.

- [ ] T005 [P] [Foundational] Edit `templates/source-map.yaml`: inside the
  existing `columns[]` entry shape (data-model.md Entity 1), add exactly two
  new OPTIONAL per-column keys, `unit: null` and `currency: null`, each with
  an inline comment stating it is free-text, human-authored, and
  `null` means "not yet declared" (distinct from an explicit "n/a" string).
  Add the two keys to ALL FOUR placeholder `columns[]` examples already in
  the file (measure, dimension attribute, dropped column, PII column) so the
  template stays internally consistent. Do NOT touch `decision`,
  `silver_type`, `missing_policy`, `pii`, `gold_placement`, `derived_columns`,
  or `gold_star` -- additive only. No C086/retail_store_sales-specific unit
  label or currency code is inlined (Principle VII). FR-001, FR-016, FR-017

- [ ] T006 [P] [Foundational] Edit `templates/metric-contract.yaml`: add
  exactly one new OPTIONAL top-level key, `unit: null`, sibling to `grain`
  and `binds_to` (data-model.md Entity 2), with an inline comment stating it
  is DOCUMENTARY ONLY (Clarification Q3) -- HR11 never cross-checks it
  against `binds_to.columns[]`'s own declared units. Do NOT add a `currency`
  key to this file, and do NOT touch `name`, `grain`, `formula_intent`,
  `owner`, `binds_to`, `readiness`, or `ambiguities[]` (Scope Guard,
  collision-avoidance allocation). No C086-specific value is inlined
  (Principle VII). FR-002, FR-016, FR-017

- [ ] T007 [Foundational] Edit `docs/readiness/semantic-model-ready.md`: add
  HR11 to the existing "Required checks" table row (alongside D1-D11/C1/R1/G6
  and any already-listed HR-family entry) and add an HR11 bullet to "Blocking
  reasons" (a multi-column-bound metric's resolved columns disagree on
  declared unit, disagree on declared currency, or a bound column/source-map
  cannot be resolved) -- doc-listing only, no rewrite of the stage's existing
  meaning (mirrors how G6, and HR6, are/would be listed there). FR-018

- [ ] T008 [Foundational] Create `src/retail/rules/hr11.py` scaffold: module
  docstring citing `docs/readiness/semantic-model-ready.md`,
  `templates/source-map.yaml`, and `templates/metric-contract.yaml` (mirrors
  `g6.py`'s docstring style), explicitly stating the FR-013/FR-014 open
  questions are NOT resolved by this module and MUST NOT be defaulted in
  code; `@register("HR11", "Summed metric's bound columns agree on declared
  unit and currency")`; a pure `check_unit_currency_agreement(ctx:
  RuleContext) -> Iterable[Finding]` function (empty findings list for now);
  a private `_iter_metric_contract_files(ctx)` helper that globs
  `ctx.tracked_files` for `mappings/*/metrics/*.yaml` and excludes
  `is_test_path()` fixtures (mirrors `assumptions.py`/AL1's path regex);
  lazy `import yaml` INSIDE the check function body only (never at module
  scope -- mirrors `readiness_status.py`/RS1 and `assumptions.py`/AL1).
  FR-003, FR-009

- [ ] T009 [Foundational] In `src/retail/rules/hr11.py`, add a private
  `_read_source_map_columns(ctx, table)` helper that reads
  `mappings/<table>/source-map.yaml` (via `ctx.repo_root / rel`,
  `read_text(encoding="utf-8-sig")`, lazy `import yaml`, `safe_load`) and
  returns a static mapping `rename_to -> {unit, currency}` for every entry in
  `columns[]` (Clarification Q4 join key: `columns[].rename_to`, per
  research.md P6) -- catching `OSError`/`UnicodeDecodeError`/`yaml.YAMLError`
  and returning a sentinel meaning "unreadable" rather than raising (so the
  caller can emit an FR-010 finding instead of crashing the whole gate). No
  live database connection (Principle VIII). FR-004, FR-009, FR-010

- [ ] T010 [Foundational] Wire the new module into
  `src/retail/rules/__init__.py`: add `hr11` to both the side-effecting
  import tuple and `__all__`, alphabetically placed immediately after
  `git_meta` (matching the existing ordering) so `@register("HR11", ...)`
  fires when `retail check` starts -- this is the "only wiring step" the
  module's own docstring requires. FR-003

- [ ] T011 [Foundational] Create empty test scaffold
  `tests/unit/test_hr11.py` with the module docstring, `pytestmark =
  pytest.mark.unit`, a `_ctx(...)` fixture-context helper pointed at
  `tests/fixtures/currency_unit_contract/` (mirrors `test_g6.py`'s `_ctx()`
  helper), and one smoke test asserting `check_unit_currency_agreement`
  returns `[]` findings against a repo root with no
  `mappings/*/metrics/*.yaml` files at all (the zero-contract case).
  FR: (scaffold only, no FR of its own)

**Checkpoint**: Both templates carry their new optional fields and the gate
doc lists HR11; the HR11 module registers and is wired into `retail check`'s
rule set (returning zero findings so far); test scaffold exists. User story
work can now begin.

---

## Phase 3: User Story 1 - A summed metric with clashing units fails closed (Priority: P1) 🎯 MVP

**Goal**: HR11 fails closed (Severity.ERROR) when a metric contract's two or
more resolved bound columns declare a different, non-null `unit`, and that
finding surfaces in the table's Semantic Model Ready `blocking_reasons[]`.

**Independent Test**: Author a source-map with two columns declaring
different `columns[].unit` values, author a metric contract whose
`binds_to.columns[]` names both, run `retail check`, confirm an HR11 finding
names the metric and the two clashing columns/units.

### Tests for User Story 1

- [ ] T012 [US1] In `tests/unit/test_hr11.py`, add
  `test_clashing_unit_fails()` using T002/T003's `ClashingUnit.yaml` fixture
  -- assert exactly one `Finding(rule_id="HR11", severity=Severity.ERROR,
  ...)` whose message names the metric (`ClashingUnit`), both column names
  (`weight_kg`, `unit_count`), and both declared unit values (`kg`, `each`)
  verbatim. FR-005

- [ ] T013 [US1] In `tests/unit/test_hr11.py`, add
  `test_hr11_finding_never_carries_a_conversion_hint()` -- for the
  `ClashingUnit.yaml` finding from T012, assert `finding.message` contains no
  numeric conversion factor/rate token and no case-insensitive substring
  match on `"rate"`/`"factor"`/`"convert"` (Scope Guard, SC-003). FR-008

- [ ] T014 [US1] In `tests/unit/test_hr11.py`, add
  `test_unresolvable_bound_column_fails()` using T003's
  `UnresolvableColumn.yaml` fixture against T002's source-map -- assert an
  HR11 ERROR finding naming the metric and the unresolved column name
  (mirrors HR6's "unresolvable column" treatment). FR-010

- [ ] T015 [US1] In `tests/unit/test_hr11.py`, add
  `test_missing_source_map_fails()` using T004's `OrphanMetric.yaml` fixture
  (no sibling `source-map.yaml` at all) -- assert an HR11 ERROR finding
  naming the missing/unreadable `source-map.yaml` path, not a silent skip.
  FR-010

- [ ] T016 [US1] In `tests/unit/test_hr11.py`, add
  `test_hr11_blocks_semantic_model_ready_blocking_reasons()`: confirm that
  when a repo's `mappings/<table>/readiness-status.yaml` is present alongside
  the `ClashingUnit.yaml` fixture, the existing `retail-semantic-check`
  gate-blocking path (`semantic_model_ready.blocking_reasons[]`) is the one
  that surfaces the HR11 finding -- this test documents/confirms the WIRING
  contract (an ERROR-severity `Finding` blocks the stage via the existing
  exit-code path), it does NOT add new computation to `readiness_status.py`.
  FR-012

### Implementation for User Story 1

- [ ] T017 [US1] In `src/retail/rules/hr11.py`,
  `check_unit_currency_agreement()`: for each committed metric-contract file
  (via `_iter_metric_contract_files`), parse the YAML (lazy `import yaml`),
  skip any contract whose `binds_to.columns[]` lists fewer than two entries
  (FR-011 no-op), and resolve the table name from the contract's own path
  (`mappings/<table>/metrics/...`, mirrors AL1's path regex / HR6's
  table-scoped join per research.md P5). FR-003, FR-011

- [ ] T018 [US1] In `src/retail/rules/hr11.py`, extend
  `check_unit_currency_agreement()` to call `_read_source_map_columns` (T009)
  for the resolved table and, for each `binds_to.columns[]` entry, look it up
  by `rename_to`; emit an ERROR finding naming the metric and the unresolved
  column when a bound column is not found among the source-map's `columns[]`
  entries, and an ERROR finding naming the metric and the missing/unreadable
  path when the source-map itself could not be read (T009's sentinel).
  FR-004, FR-010

- [ ] T019 [US1] In `src/retail/rules/hr11.py`, extend
  `check_unit_currency_agreement()` to compare, pairwise, the resolved
  `unit` value of every bound column that DOES resolve; emit exactly one
  ERROR finding per metric when two or more of them declare a different,
  non-null `unit` value, naming the metric, the clashing column names, and
  their declared unit values verbatim -- an exact, case-sensitive string
  comparison only, no normalization/alias/fuzzy-match (FR-007). FR-005,
  FR-007

- [ ] T020 [US1] Run `pytest tests/unit/test_hr11.py -m unit -x -q` and
  confirm T012-T016 all pass; fix `hr11.py` (not the tests) on any mismatch,
  per repo testing rule "fix implementation, not tests." (verification step;
  confirms FR-004, FR-005, FR-007, FR-008, FR-010, FR-011, FR-012)

**Checkpoint**: HR11 fails closed on a clashing-unit sum, an unresolvable
bound column, and a missing source-map; a broken multi-column bind now blocks
Semantic Model Ready the same way a D1-D11/G6 finding already does.

---

## Phase 4: User Story 2 - A same-unit summed metric binds cleanly and clears HR11 (Priority: P1)

**Goal**: A metric contract whose bound columns all agree on declared unit
and currency produces zero HR11 findings, so the gate is reachable, not just
failable.

**Independent Test**: Point a metric contract's `binds_to.columns[]` at two
columns whose source-map entries declare the same `unit` (or the same
`currency`), re-run `retail check`, confirm no HR11 finding is emitted for
that metric.

### Tests for User Story 2

- [ ] T021 [US2] In `tests/unit/test_hr11.py`, add
  `test_same_unit_produces_no_finding()` using T002/T003's `CleanUnit.yaml`
  fixture (`weight_kg` + `secondary_weight_kg`, both `unit: "kg"`) -- assert
  `check_unit_currency_agreement()` returns `[]` findings for that metric.
  FR-005 (negative case), SC-004

- [ ] T022 [US2] In `tests/unit/test_hr11.py`, add
  `test_same_currency_produces_no_finding()` using T003's `CleanCurrency.yaml`
  fixture (both bound columns declare the same `currency`) -- assert
  `check_unit_currency_agreement()` returns `[]` findings for that metric.
  FR-006 (negative case), SC-004

- [ ] T023 [US2] In `tests/unit/test_hr11.py`, add
  `test_single_bound_column_never_fires()` using T003's `SingleColumn.yaml`
  fixture (`binds_to.columns` lists exactly one entry) -- assert
  `check_unit_currency_agreement()` returns `[]` findings (FR-011: nothing to
  compare, HR11 MUST NOT fire). FR-011

- [ ] T024 [US2] In `tests/unit/test_hr11.py`, add
  `test_hr11_findings_never_carry_a_numeric_score()` -- for every `Finding`
  produced across ALL of T012/T014/T015's defect fixtures, assert
  `finding.message` contains no numeric confidence/health/maturity token and
  the `Finding` dataclass carries no such field (grep-style substring
  assertions, mirroring how `test_hr6.py` guards hard rule #9). FR-015,
  SC-005

### Implementation for User Story 2

- [ ] T025 [US2] Run `pytest tests/unit/test_hr11.py -m unit -x -q` and
  confirm T021-T024 pass without further `hr11.py` changes -- if a change IS
  needed (e.g. the clean fixtures unexpectedly trip a T017-T019 check), fix
  `src/retail/rules/hr11.py`'s check logic, not the fixture or the test, per
  repo testing rule. No new finding-trigger code is expected in this story;
  it is primarily a confirmation slice on top of US1's triggers (HR11 has one
  shared implementation surface, mirrors 092/HR6's US2). FR-005, FR-006,
  FR-011, FR-015, SC-004, SC-005

**Checkpoint**: HR11 both fails on a genuine unit clash (US1) and passes
cleanly on a correctly declared, correctly bound metric (US2) -- the gate is
usable, not just punitive.

---

## Phase 5: User Story 3 - A currency mismatch across summed money columns is caught the same way (Priority: P2)

**Goal**: HR11 catches a currency clash on summed money columns using the
exact same mechanism as a unit clash -- currency is not a second-class case.

**Independent Test**: Author a source-map with two money columns declaring
different `columns[].currency` values, author a metric contract summing
both, run `retail check`, confirm an HR11 finding names the metric and the
two clashing column/currency pairs.

### Tests for User Story 3

- [ ] T026 [US3] In `tests/unit/test_hr11.py`, add
  `test_clashing_currency_fails()` using T002/T003's `ClashingCurrency.yaml`
  fixture (`revenue_egp` / `EGP` vs `revenue_usd` / `USD`) -- assert exactly
  one `Finding(rule_id="HR11", severity=Severity.ERROR, ...)` whose message
  names the metric, both column names, and both declared currency values
  verbatim. FR-006

- [ ] T027 [US3] In `tests/unit/test_hr11.py`, add
  `test_currency_finding_never_carries_a_conversion_hint()` -- for the
  `ClashingCurrency.yaml` finding from T026, assert `finding.message`
  contains no exchange-rate token and no case-insensitive substring match on
  `"rate"`/`"factor"`/`"convert"` (Scope Guard, SC-003). FR-008

- [ ] T028 [US3] In `tests/unit/test_hr11.py`, add
  `test_unit_and_currency_clash_are_independent_findings()`: author (in this
  test, inline or as a small additional fixture) a metric contract whose
  bound columns clash on BOTH unit and currency, and assert HR11 reports
  both the unit-clash condition and the currency-clash condition (FR-006's
  "independent of FR-005" clause) rather than only the first one found.
  FR-005, FR-006

### Implementation for User Story 3

- [ ] T029 [US3] In `src/retail/rules/hr11.py`, extend
  `check_unit_currency_agreement()` to compare, pairwise, the resolved
  `currency` value of every bound column that resolves, using the SAME
  exact-string-equality mechanism as T019's unit comparison; emit an ERROR
  finding when two or more resolved bound columns declare a different,
  non-null `currency` value, naming the metric, the clashing column names,
  and their declared currency values verbatim. This check runs independently
  of the unit comparison (a metric may clash on unit, currency, both, or
  neither -- FR-006). FR-006, FR-007

- [ ] T030 [US3] Run `pytest tests/unit/test_hr11.py -m unit -x -q` and
  confirm T026-T028 all pass; fix `hr11.py` (not the tests) on any mismatch.
  FR-006, FR-007, FR-008

**Checkpoint**: All three user stories are independently satisfied; HR11 now
covers every FR-004..FR-011 trigger in `data-model.md`'s Entity 3 table, on
both the unit axis and the currency axis.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Registry/manifest regeneration, MUST-NOT verifications
(Scope Guard, collision-avoidance, genericity, hard rule #9), the two OPEN
questions' record-and-don't-resolve check, and the full-suite gate. Depends
on all three user stories being complete.

- [ ] T031 [Polish] Regenerate `docs/rules/rules-manifest.json` by running
  the existing `retail manifest` CLI command (per `src/retail/manifest.py`)
  now that HR11 is registered -- confirm the new
  `{"id": "HR11", "title": "..."}` entry appears alongside the existing rule
  ids in the golden inventory. Must run AFTER T010 (registration) and cannot
  be `[P]` with any `hr11.py` edit. FR-003

- [ ] T032 [Polish] Regenerate `docs/rules/severity-posture.json` by running
  the existing `retail severity-posture` CLI command (per
  `src/retail/severity_posture.py`) so the posture snapshot records HR11 as
  an `ERROR`-severity rule (never `WARNING`, per Principle I / data-model.md
  Entity 3's "all four triggers are Severity.ERROR") -- confirm the golden
  record's snapshot test stays green. FR-003, FR-005, FR-006, FR-010

- [ ] T033 [P] [Polish] Grep-verify the collision-avoidance key allocation
  held: `git diff templates/metric-contract.yaml` shows an ADDED `unit:`
  line and NO added `currency:` line (case-insensitive) at any level;
  `git diff templates/source-map.yaml` shows ADDED `unit:` and `currency:`
  lines inside `columns[]` and no other key touched; neither diff introduces
  `uom`, `unit_of_measure`, `measure_unit`, or `binds_to.currency` (Scope
  Guard, FR-002, quickstart.md Step 7). FR-001, FR-002, SC-006

- [ ] T034 [P] [Polish] Grep-verify Scope Guard / SC-003: `git diff
  templates/source-map.yaml templates/metric-contract.yaml
  src/retail/rules/hr11.py` contains no case-insensitive match on
  `"rate"`/`"factor"`/`"convert"` in an added line (a targeted
  `Select-String -Pattern "^\+.*"` filter, per quickstart.md Step 7) --
  0 conversion rate, conversion factor, or converted value anywhere in the
  template fields or the rule's own source. FR-008, SC-003

- [ ] T035 [P] [Polish] Grep-verify genericity: confirm
  `templates/source-map.yaml`, `templates/metric-contract.yaml`, and
  `src/retail/rules/hr11.py` contain no `retail_store_sales`, `_rss`, or
  other C086-specific token (a case-insensitive grep for the known C086
  table/column names used elsewhere in the repo). FR-016, SC-006

- [ ] T036 [P] [Polish] Grep-verify hard rule #9: confirm neither
  `templates/source-map.yaml`, `templates/metric-contract.yaml`,
  `src/retail/rules/hr11.py`, nor `tests/unit/test_hr11.py` contains a
  numeric confidence/health/maturity field name or an "N of M" completeness
  phrasing. FR-015, SC-005

- [ ] T037 [P] [Polish] Grep/read-verify FR-013 and FR-014 stay OPEN and
  unresolved in code: confirm `src/retail/rules/hr11.py` contains no logic
  that (a) scopes itself ONLY to `definition.aggregation == "sum"` while
  silently exempting every no-`definition` contract, or the inverse of
  unconditionally treating any 2+-column bind as a sum with no
  `definition.aggregation` gate at all being asserted as "settled"; and (b)
  no logic that treats a null-vs-non-null unit/currency pairing as a
  hardcoded "matches" or "blocks" outcome. Confirm the module's docstring
  (T008) still states both items as open. This is a record-and-verify task,
  not a resolution task -- it MUST NOT itself pick an answer. FR-013, FR-014

- [ ] T038 [Polish] Confirm `docs/readiness/semantic-model-ready.md`'s
  "Required checks" and "Blocking reasons" tables list HR11 (re-check T007's
  edit landed and matches the shipped rule's actual behavior after
  T017-T029). FR-018

- [ ] T039 [Polish] Run the full verification sequence required before any
  commit in this repo: `ruff format --check src/ tests/`, `ruff check src/
  tests/`, `pytest -m unit -x -q` (full suite, not just `test_hr11.py`, to
  catch any cross-rule regression e.g. in the rules-manifest snapshot test or
  the severity-posture snapshot test), then `retail check` against the live
  repo tree to confirm HR11 registers and runs cleanly with the repo's real,
  currently-committed metric contracts and source-maps (none of which yet
  declare `unit`/`currency`, so this run must not fabricate a finding on an
  all-undeclared table -- confirms T037's FR-014 non-default holds in
  practice, not just in fixtures). FR-009, FR-012, FR-019, FR-020

**Checkpoint**: HR11 is registered, documented, tested, generic, and
non-fabricating; the manifest and posture snapshots are current; FR-013 and
FR-014 remain visibly open in both code and docs; the two template diffs are
additive-only and free of any conversion concept.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies -- can start immediately. T001-T004
  are `[P]` (distinct fixture files/directories).
- **Foundational (Phase 2)**: Depends on Setup (tests reference Setup's
  fixtures). T005 (source-map template) and T006 (metric-contract template)
  are independent files and may run in parallel with each other and with T007
  (doc edit) -- all three are docs-first per hard rule #8, and land BEFORE
  T008-T011 (the rule module, its helper, its wiring, its test scaffold),
  which are sequential (same file `hr11.py`, then its registration, then its
  test scaffold). BLOCKS all user stories.
- **User Stories (Phase 3-5)**: All depend on Foundational (Phase 2)
  completion. Because they share `hr11.py` and `test_hr11.py`, US1 -> US2 ->
  US3 is the SAFE sequential order (US2's "does the clean case still pass"
  test is most meaningful once US1's triggers exist; US3 extends the same
  file with the currency axis). True parallel multi-developer work across
  US1/US2/US3 would collide on both shared files -- called out explicitly,
  unlike the template's default parallel-story assumption (mirrors
  092/HR6's tasks.md).
- **Polish (Phase 6)**: Depends on all three user stories being complete.
  T031/T032 depend on T010's registration and on all finding-trigger code
  (T017-T019, T029) being final, since both regenerate goldens FROM the live
  rule behavior. T033-T037 are `[P]` (independent grep/read-only checks, no
  shared file writes).

### Within Each User Story

- Tests are written first (T012-T016, T021-T024, T026-T028) and must FAIL
  before the corresponding implementation task (T017-T019, T025, T029) makes
  them pass -- TDD RED -> GREEN, per repo testing rule.
- Within `hr11.py`, each implementation task ADDS to the same
  `check_unit_currency_agreement()` function body -- strictly sequential,
  never `[P]`, regardless of story boundary.

### Parallel Opportunities

- T001, T002, T003, T004 (Setup: distinct fixture files/directories) -- run
  together.
- T005 (source-map template), T006 (metric-contract template), T007 (doc
  edit) touch different files and have no data dependency on each other --
  may run together, all before T008.
- T033, T034, T035, T036, T037 (Polish: independent read-only verification
  checks) -- run together.
- No task inside `src/retail/rules/hr11.py` or `tests/unit/test_hr11.py` is
  ever `[P]` with another task touching the same file -- a deliberate
  departure from the template's default (mirrors 092/HR6's tasks.md).

---

## Parallel Example: Setup + Foundational docs-first slice

```bash
# Launch all Setup fixture tasks together:
Task: "Create fixture directory tests/fixtures/currency_unit_contract/"
Task: "Author fixture source-map tests/fixtures/currency_unit_contract/mappings/fixture_table/source-map.yaml"
Task: "Author metric-contract fixtures under .../fixture_table/metrics/"
Task: "Author OrphanMetric.yaml fixture with no sibling source-map.yaml"

# Launch the docs-first template + doc edits together (before any hr11.py code):
Task: "Edit templates/source-map.yaml to add columns[].unit / columns[].currency"
Task: "Edit templates/metric-contract.yaml to add top-level unit"
Task: "Edit docs/readiness/semantic-model-ready.md to list HR11"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational) -- both templates carry
   their new fields, the gate doc lists HR11, the module registers.
2. Complete Phase 3 (US1) -- HR11 fails closed on a unit clash, an
   unresolvable bound column, and a missing source-map.
3. **STOP and VALIDATE**: run `pytest tests/unit/test_hr11.py -m unit -x -q`
   and `retail check` against a repo tree seeded with T002-T004's defect
   fixtures; confirm HR11 findings appear and block.
4. This is already a coherent, demoable slice (the exact "12 kg + 3 each"
   failure mode from the gap description now fails the gate) even before
   US2/US3 land.

### Incremental Delivery

1. Setup + Foundational -> both templates carry the new fields, doc lists
   HR11, module registers with zero findings.
2. Add US1 -> HR11 fails on a unit clash (MVP; the gap's exact failure mode).
3. Add US2 -> HR11 passes cleanly on a correctly declared, correctly bound
   metric (gate is usable, not just punitive).
4. Add US3 -> HR11 also catches the currency-clash half of the gap
   description, independently of the unit check.
5. Polish -> manifest/posture regenerated, Scope Guard / collision-avoidance
   / genericity / hard-rule-#9 / FR-013-FR-014-still-open all verified, full
   suite green.

### Sequencing Reality (not a parallel-team feature)

Unlike the template's default multi-developer parallel-story assumption,
this feature's entire rule-code implementation surface is TWO files
(`src/retail/rules/hr11.py`, `tests/unit/test_hr11.py`) plus two small
template edits, one doc edit, and a handful of fixtures. One implementer
works US1 -> US2 -> US3 -> Polish in that order; the only genuine
parallelism is within Setup (T001-T004), within Foundational's
template/doc trio (T005-T007), and within Polish's read-only verification
checks (T033-T037).

---

## FR Coverage Map (verification aid for the analyze stage)

| FR | Covered by |
|---|---|
| FR-001 | T002, T005, T033 |
| FR-002 | T006, T033 |
| FR-003 | T003, T008, T010, T017, T031, T032 |
| FR-004 | T002, T009, T018 |
| FR-005 | T003, T012, T019, T020, T021, T025, T028, T032 |
| FR-006 | T002, T003, T026, T028, T029, T030, T032 |
| FR-007 | T019, T029, T030 |
| FR-008 | T013, T027, T030, T034 |
| FR-009 | T008, T009, T039 |
| FR-010 | T003, T004, T014, T015, T018, T020, T032 |
| FR-011 | T003, T017, T020, T023, T025 |
| FR-012 | T016, T020, T039 |
| FR-013 | T008, T037 (recorded open + non-default enforced; NOT resolved) |
| FR-014 | T008, T037, T039 (recorded open + non-default enforced; NOT resolved) |
| FR-015 | T024, T036 |
| FR-016 | T002, T035 |
| FR-017 | T005, T006 |
| FR-018 | T007, T038 |
| FR-019 | T039 (no live-DB check exists to test; verified by absence) |
| FR-020 | T039 (agent never auto-fills unit/currency; the rule only reads human-authored declarations -- no code path in hr11.py writes to either template or mapping file) |

Every FR-001..FR-020 maps to at least one task. FR-013 and FR-014 (the
Principle-V/VI MUST-NOTs) are covered by record-and-enforce tasks, never by a
task that resolves the underlying detection-scope or enforcement-posture
question -- that ruling stays with implementation planning / a named human,
outside this tasks.md, per the spec's own routing.
