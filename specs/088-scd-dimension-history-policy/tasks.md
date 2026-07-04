---
description: "Task list for 088-scd-dimension-history-policy (Dimension History / SCD Policy Readiness)"
---

# Tasks: Dimension History / SCD Policy Readiness

**Input**: Design documents from `specs/088-scd-dimension-history-policy/`
(spec.md, plan.md, data-model.md)

**Tests**: Included -- the plan's Testing section requires mutation-verified
fixtures (SF1/AP1/HR1 discipline); this is a fail-closed governance rule, not
optional coverage.

**Status carried from plan.md**: Draft. This task list authors the design; it
does not itself constitute ratification. Phase 1 contains an OWNER SEAM
(the reserved id + schema key) and FR-017 (Q-APPROVAL-SEAM) stays OPEN for the
owner -- no task below answers it.

**Landing-precondition warning (carried from plan.md, do not "fix" it)**: once
HR2 lands, `retail check` goes RED on the current committed tree -- both
`mappings/retail_store_sales/source-map.yaml` and
`mappings/demo_sample_orders/source-map.yaml` have `gold_star.dimensions[]`
entries with no `scd_type` key, and FR-005 grants no grandfather exemption.
This is the DELIBERATE, already-recorded severity posture (spec.md
Assumptions: "Severity posture"), not a bug for any task here to paper over.
**No task in this file may add a real `scd_type` value to either committed
map** -- filling in `type_1`/`type_2` on a human's behalf is the exact
Principle-V act this feature exists to forbid (plan.md Summary: "The agent
does not, and must not, green this by filling in a placeholder `scd_type`
value on a human's behalf"). The Polish gate task (T041) asserts the NEW
tests are green and the wiring lockstep is green -- it explicitly does NOT
assert a clean `retail check` run on the live tree.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3), or
  `SETUP`/`FOUND`/`POLISH` for cross-cutting phases
- Every task names an exact repo-relative file path

## Path Conventions

Single project (`src/retail/`, `tests/`, `docs/`, `templates/`) at repository
root, per plan.md "Structure Decision". No new project/service/top-level
directory.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Reserve the rule id and the schema key, then author the
docs-first schema-template edit BEFORE any static-rule wiring task (hard
rule #8: docs/templates/checklists before automation).

- [ ] **T001** `[SETUP]` [OWNER SEAM] Confirm/ratify that the reserved
  static-rule id is **HR2** and the new schema key is exactly
  `gold_star.dimensions[].scd_type` (collision-avoidance allocation, spec.md
  "Ratification pending"). No task below may rename either, add a new
  top-level `source-map.yaml` key, or add any sibling key on the dimension
  entry beyond `scd_type`. _Satisfies: spec.md collision allocation; FR-001._
- [ ] **T002** `[SETUP]` Re-verify the current live registered-rule count by
  reading `docs/rules/rules-manifest.json` directly (do not trust plan.md's
  recorded count of 55) -- 087/HR1 is an in-flight parallel rule-adder
  claiming the SAME 55->56 slot (plan.md "Scale/Scope"); record whichever
  count is actually live at this moment so T028/T029 bump from the CORRECT
  base, not a stale plan-time snapshot. _Satisfies: plan.md serialization-point
  caveat; SC-008._
- [ ] **T003** `[SETUP]` Edit `templates/source-map.yaml`: add
  `scd_type: "type_1"` as a new nested key on the illustrative
  `gold_star.dimensions[]` entry, alongside `surrogate_key` /
  `has_unknown_member` / `attributes[]` (data-model.md "SCD declaration"
  shape). This is the feature's ENTIRE schema footprint -- no new top-level
  key, no other sibling key on the entry. Generic placeholder value only
  (Principle VII); this is a TEMPLATE edit, not a real map, so it is not a
  Principle-V act. Depends on T001. _Satisfies: FR-001, FR-002, FR-015,
  Principle VII; docs-first ordering (hard rule #8)._
- [ ] **T004** `[SETUP]` Confirm (checklist task, no file edit outside T003)
  that `docs/readiness/mapping-ready.md` and `docs/readiness/gold-ready.md`
  stay REFERENCE-ONLY per plan.md's Project Structure -- neither file is
  edited unless it enumerates per-dimension fields or per-rule static-check
  ids by name; `scd_type` is declared at Stage 2 (Mapping Ready) and HR2 runs
  on the existing Stage 4 (Gold Ready) static surface, adding no new
  readiness stage. _Satisfies: plan.md file-footprint fidelity; spec.md
  Boundary section ("adds NO new readiness stage")._

**Checkpoint**: the schema key exists in the template (generic, no committed
map touched) and the rule id is reserved before any code is written.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Reserve HR2 across every wiring surface and produce a stub
module, mirroring the SF1/AP1/HR1 six-surface wiring discipline (FR-014).
**No user-story Finding logic is implemented yet in this phase** -- only the
scaffold that makes `@register("HR2", ...)` compile and be discoverable.

**CRITICAL**: No user story (Phase 3+) can be implemented until this phase is
complete, because HR2 must exist as a registered (even if empty-bodied) rule
before its Finding-emitting logic can be tested via `retail check`.

- [ ] **T005** `[FOUND]` Create the stub rule module
  `src/retail/rules/rule_hr2.py` with `RULE_ID = "HR2"`, the module docstring
  (mirrors `rule_sf1.py`'s shape: what HR2 does, what it never does,
  static-only, lazy `import yaml`), and a
  `@register(RULE_ID, "dimension history / SCD policy readiness gate")`
  -decorated `check_hr2(ctx: RuleContext) -> Iterable[Finding]` that returns
  `[]` (stub body; Phase 3+ fills it in). _Satisfies: FR-004, FR-013._
- [ ] **T006** `[FOUND]` Edit `src/retail/rules/__init__.py`: add `rule_hr2`
  to the side-effecting import tuple (alphabetical slot, immediately after
  `rule_count_claims` and before `rule_sf1`, per existing `rule_ap1` /
  `rule_count_claims` / `rule_sf1` ordering) AND to `__all__` in the same
  commit -- the ONLY discovery step (no autodiscovery). Depends on T005.
  _Satisfies: FR-014 (wiring surface 1)._
- [ ] **T007** `[P]` `[FOUND]` Edit `tests/unit/test_rules_wiring.py`: add
  `"HR2"` to `EXPECTED_RULE_IDS`. Depends on T005. _Satisfies: FR-014
  (wiring surface 2)._
- [ ] **T008** `[P]` `[FOUND]` Edit `docs/rules/rules-manifest.json`: add
  `{"id": "HR2", "title": "dimension history / SCD policy readiness gate"}`
  in id order (after the `HR1` entry if 087 has landed in this tree by
  implement time; otherwise after the nearest alphabetically-preceding `H*`
  entry -- verify live per T002). Depends on T005. _Satisfies: FR-014
  (wiring surface 3)._
- [ ] **T009** `[P]` `[FOUND]` Edit `docs/rules/severity-posture.json`: add
  `"HR2": ["error"]` under the registered section -- ERROR ONLY, no
  WARNING-only case exists for HR2 (data-model.md: "there is no WARNING-only
  HR2 case"; every emitting branch -- undeclared, invalid value, proven
  drop-and-rebuild mismatch -- is `Severity.ERROR`). Depends on T005.
  _Satisfies: FR-014 (wiring surface 4)._
- [ ] **T010** `[FOUND]` Edit `docs/glossary.md`: add the `HR2` row to the
  rules table. If 087/HR1 has already landed in this tree (verify per T002),
  HR2 joins the EXISTING `HR` family row-set (rule count bumps, family count
  UNCHANGED); if HR1 has not landed, this task also introduces the `HR`
  family for the first time (rule count bumps AND family count bumps by one,
  matching HR1's own T010 in spec 087) -- confirm which case applies live,
  do not assume. Bump the "Currently N rules in M families" anchor text to
  match whichever case applies. _Satisfies: FR-014 (wiring surface 5)._
- [ ] **T011** `[FOUND]` Edit `docs/quality/rule-count-claims.yaml`: bump
  `claimed-count` for the `glossary-rule-count` entry to match T010's new
  anchor text exactly (byte-consistent; SC2 reconciles the two). Use the
  LIVE count confirmed in T002, not a hard-coded 56 -- 087/HR1 may have
  already consumed that slot. Depends on T010. _Satisfies: FR-014 (wiring
  surface 6), SC-008._
- [ ] **T012** `[FOUND]` Run
  `pytest -m unit tests/unit/test_wiring_meta_gate.py
  tests/unit/test_rules_wiring.py tests/unit/test_rule_count_claims.py` and
  confirm all green with the HR2 stub registered at the live count.
  _Satisfies: SC-008 (wiring + rule-count lockstep stays green)._

**Checkpoint**: `HR2` is a real, registered, discoverable rule (currently a
no-op) and every meta-gate lockstep is green. User story implementation can
now begin.

---

## Phase 3: User Story 1 - A human declares each dimension's history policy at Mapping Ready (Priority: P1)

**Goal**: Given a `source-map.yaml` whose every `gold_star.dimensions[]`
entry carries a valid `scd_type` (`type_1` or `type_2`), HR2 reports no
missing-declaration finding; given an entry with an unrecognized value,
HR2 emits a fail-closed ERROR naming the dimension and the invalid value.
This phase builds the shared declaration-reading helper that US2/US3 reuse.

**Independent Test**: fixture `source-map.yaml` with `scd_type: "type_2"` on
one dimension and `scd_type: "type_1"` on another -> both parse as valid, no
missing-declaration finding for either. A fixture with `scd_type: "bogus"`
-> one ERROR naming the dimension and the invalid value.

### Tests for User Story 1

> Write these tests FIRST; they FAIL against the Phase 2 stub before Phase 3
> implementation lands (RED), then PASS after (GREEN) -- SF1/AP1/HR1
> mutation discipline.

- [ ] **T013** `[P]` `[US1]` Fixture
  `tests/fixtures/scd_history/source-map-declared.yaml` -- a minimal
  `source-map.yaml` stand-in whose `gold_star.dimensions[]` has one entry
  `scd_type: "type_1"` and one entry `scd_type: "type_2"` (both valid).
  _Satisfies: US1 Acceptance Scenario 1, FR-002, FR-003._
- [ ] **T014** `[P]` `[US1]` Fixture
  `tests/fixtures/scd_history/source-map-invalid-value.yaml` -- a
  `gold_star.dimensions[]` entry with `scd_type: "quarterly"` (neither
  `type_1` nor `type_2`). _Satisfies: US1 Acceptance Scenario 3, FR-006._
- [ ] **T015** `[US1]` `tests/unit/test_rule_hr2.py`: write the RED tests
  against T013/T014 fixtures asserting (a) zero findings for every valid
  declaration in T013, (b) exactly one `Severity.ERROR` finding for T014
  naming the dimension and the literal invalid value seen, and (c) the
  `locator` shape `mappings/<table>/source-map.yaml:<dimension_name>` for the
  invalid-value finding (data-model.md "HR2 Finding" locator convention);
  confirm FAIL against the Phase 2 stub. _Satisfies: US1 Independent Test._

### Implementation for User Story 1

- [ ] **T016** `[US1]` In `rule_hr2.py`: implement `_load_source_map(ctx, rel)`
  -- read one `mappings/<table>/source-map.yaml` path (lazy `import yaml`),
  return the parsed dict or `None` on missing/unparseable (never raise);
  this is the shared read-only helper US2/US3 reuse. Depends on T005.
  _Satisfies: FR-003, data-model.md "SCD declaration" (Read by: HR2 only)._
- [ ] **T017** `[US1]` In `rule_hr2.py`: implement
  `_iter_declared_dimensions(source_map)` -- yield each
  `gold_star.dimensions[]` entry's `(name, scd_type_or_missing)` pair, NEVER
  reading `gold_star.degenerate_dimensions[]` or `gold_star.date_dimension`
  (FR-010, Edge Cases). Depends on T016. _Satisfies: FR-010._
- [ ] **T018** `[US1]` In `rule_hr2.py`: implement the invalid-value branch --
  for each dimension whose `scd_type` is present but not exactly `type_1` or
  `type_2`, emit `Finding(HR2, ERROR, ...)` naming the dimension and the
  literal value seen, locator `mappings/<table>/source-map.yaml:<dim_name>`.
  A dimension with a VALID value or a MISSING key produces no finding from
  this branch (missing is US3's job, Phase 5). Depends on T017. _Satisfies:
  FR-002, FR-006, US1 Acceptance Scenario 3._
- [ ] **T019** `[US1]` Wire `check_hr2` in `rule_hr2.py` to glob
  `mappings/*/source-map.yaml` from `ctx.tracked_files`, call
  `_load_source_map` + `_iter_declared_dimensions` + the T018 invalid-value
  branch per table, and collect findings. Depends on T016, T017, T018.
  _Satisfies: FR-004 (input source: `ctx.tracked_files` only)._
- [ ] **T020** `[US1]` Run `tests/unit/test_rule_hr2.py` (T015) against the
  Phase 3 implementation and confirm GREEN (mutation-verified: change the
  invalid value in T014's fixture to `type_1`/`type_2` and re-confirm the
  finding disappears). _Satisfies: US1 Independent Test, SC-001 (partial:
  valid-declaration zero-finding case)._

**Checkpoint**: HR2 correctly validates a declared `scd_type` value (valid ->
silent, invalid -> fail-closed ERROR) and never touches
`degenerate_dimensions[]`/`date_dimension`. The shared declaration-reading
helpers are in place for US2/US3 to build on.

---

## Phase 4: User Story 2 - Fail closed when a Type-2 dimension is built by drop-and-rebuild (Priority: P1) MVP

**Goal**: When a dimension is declared `scd_type: "type_2"` but its table's
gold migration SQL builds that dimension's own gold table by
drop-and-rebuild (batched `DROP TABLE IF EXISTS` + same-file `CREATE TABLE`,
in either CTAS or DDL-plus-`INSERT` form, not required to be textually
adjacent -- Clarification C5), HR2 emits a fail-closed ERROR naming the
dimension and the migration file. A `type_1` dimension never fires
regardless of build shape. A `type_2` dimension with no gold migration yet
fires nothing (not-yet-buildable).

**Why this is the MVP**: this is the enforcement half that makes the silent
implicit-Type-1 gap visible and blocking (spec.md: "This is the feature's
whole point").

**Independent Test**: fixture `source-map.yaml` declaring one dimension
`type_2` and a fixture gold migration SQL file containing, for that
dimension's own gold table, a batched `DROP TABLE IF EXISTS <dim_table>`
paired (non-adjacent) with `CREATE TABLE <dim_table> (...)` + `INSERT INTO
<dim_table> ...` -> exactly one fail-closed ERROR naming the dimension and
the migration file. Same fixture with the dimension changed to `type_1` ->
no finding for that table.

### Tests for User Story 2

- [ ] **T021** `[P]` `[US2]` Fixture
  `tests/fixtures/scd_history/gold-ddl-insert-drop-rebuild.sql` -- the
  PRIMARY/committed-tooling shape: a batched `DROP TABLE IF EXISTS
  <schema>.<dim_table>` (not textually adjacent to its recreation, mirroring
  the committed `0004_create_gold_retail_store_sales_star.sql` layout) plus,
  further down the same file, `CREATE TABLE <schema>.<dim_table> (...)`
  followed by one or more `INSERT INTO <schema>.<dim_table> ...` statements.
  Illustrative table/column names only (Principle VII). _Satisfies: US2
  Acceptance Scenario 1, FR-007, Clarification C5 (primary authored form)._
- [ ] **T022** `[P]` `[US2]` Fixture
  `tests/fixtures/scd_history/gold-ctas-drop-rebuild.sql` -- the ADDITIONAL
  authored-form case: the same batched `DROP TABLE IF EXISTS
  <schema>.<dim_table>` paired with `CREATE TABLE <schema>.<dim_table> AS
  SELECT ...` (CTAS). _Satisfies: US2 Acceptance Scenario 1, FR-007,
  Clarification C5 (CTAS form, "MUST also be covered")._
- [ ] **T023** `[P]` `[US2]` Fixture
  `tests/fixtures/scd_history/gold-type1-drop-rebuild.sql` -- a `type_1`
  dimension's own gold table built by the identical drop-and-rebuild
  construct (either form) -- used to assert NO finding (FR-009). _Satisfies:
  US2 Acceptance Scenario 2, FR-009._
- [ ] **T024** `[P]` `[US2]` Fixture
  `tests/fixtures/scd_history/source-map-type2-single-dim.yaml` -- a
  `source-map.yaml` stand-in declaring exactly one `gold_star.dimensions[]`
  entry `scd_type: "type_2"` with a schema-qualified `name` (e.g.
  `gold.dim_<entity_a>`), paired against T021/T022; and a second variant
  declaring `scd_type: "type_1"` for the same dimension name, paired against
  T023. _Satisfies: US2 all three Acceptance Scenarios, Clarification C4
  (schema-qualified `name` resolution)._
- [ ] **T025** `[US2]` `tests/unit/test_rule_hr2.py`: extend with RED tests
  over T021-T024 asserting (a) exactly one `Severity.ERROR` finding naming
  the dimension AND the migration file path for the `type_2` + drop-rebuild
  pairing (both CTAS and DDL+INSERT forms), (b) zero findings for the
  `type_1` + drop-rebuild pairing (T023), and (c) zero findings when the
  `type_2` dimension's migration file is simply absent from
  `ctx.tracked_files` (US2 Acceptance Scenario 3, FR-008 -- no fixture file
  needed for this case, just omit one from the context); confirm FAIL
  against the Phase 3 implementation (no FR-007 branch exists yet). Depends
  on T016, T017, T019. _Satisfies: US2 Independent Test._

### Implementation for User Story 2

- [ ] **T026** `[US2]` In `rule_hr2.py`: implement
  `_resolve_bare_table(name: str) -> str` -- strip an optional leading
  `<schema>.` prefix from a dimension's declared `gold_star.dimensions[].name`
  (Clarification C4). Depends on T005. _Satisfies: FR-007 (name resolution),
  Clarification C4._
- [ ] **T027** `[US2]` In `rule_hr2.py`: implement
  `_find_gold_migration(ctx, table_id) -> str | None` -- resolve
  `warehouse/migrations/*create_gold_<table_id>_star.sql` from
  `ctx.tracked_files` (glob-style match on the documented naming
  convention); return `None` when no such file is tracked (FR-008 -- this
  return value is the not-yet-buildable signal, never itself a finding).
  Depends on T005. _Satisfies: FR-004 (input source), FR-008._
- [ ] **T028** `[US2]` In `rule_hr2.py`: implement
  `_has_drop_and_rebuild(sql_text: str, bare_table: str) -> bool` -- a scoped
  regex/text match (no SQL AST parser, per plan.md Primary Dependencies) that
  finds, for `bare_table` specifically (with an optional `<schema>.` prefix
  stripped from the matched `DROP`/`CREATE` token before comparing against
  `bare_table`, Clarification C4): a `DROP TABLE IF EXISTS <tok>` for that
  table AND a same-file `CREATE TABLE <tok>` for the same table, in EITHER
  form -- `CREATE TABLE <tok> AS SELECT` (CTAS) OR `CREATE TABLE <tok> (...)`
  followed by at least one `INSERT INTO <tok> ...` -- WITHOUT requiring
  textual adjacency between the `DROP` and the `CREATE` (Clarification C5).
  Depends on T026. _Satisfies: FR-007 (construct detection), Clarification
  C4, Clarification C5._
- [ ] **T029** `[US2]` In `rule_hr2.py`: add a code comment (not a Finding) at
  the `_has_drop_and_rebuild` call site marking the POSITIVE-recognition gap
  as `# [FUTURE SCOPE -- see spec.md Clarification C3] no positive signal for
  a valid, correctly-authored Type-2 construct exists yet; only the negative
  drop-and-rebuild signal is implemented` so the deferred limb is visibly
  authored-pending rather than silently absent (Principle VIII). Depends on
  T028. _Satisfies: FR-007 deferred-positive-signal note, Clarification C3._
- [ ] **T030** `[US2]` In `rule_hr2.py`: wire the `type_2`-declared branch
  into `check_hr2` -- for each dimension with a VALID `scd_type ==
  "type_2"` (invalid values already handled by T018; this branch never
  double-fires on an invalid value), resolve its migration via T027; if
  `None`, emit no finding (FR-008); if present, read the migration file text
  and call `_has_drop_and_rebuild` scoped to that dimension's own
  `_resolve_bare_table(name)`; if `True`, emit
  `Finding(HR2, ERROR, ...)` naming the dimension AND the migration file
  path (locator = the migration file path, per data-model.md "HR2 Finding"
  build-mismatch locator convention). A `type_1` dimension is NEVER passed
  into this branch (FR-009 -- enforced structurally, not by an extra check).
  Depends on T019, T027, T028, T029. _Satisfies: FR-007, FR-008, FR-009, US2
  all three Acceptance Scenarios._
- [ ] **T031** `[US2]` Run the extended `tests/unit/test_rule_hr2.py` (T025)
  against T026-T030 and confirm GREEN, including the mutation-verify
  direction (change T024's `type_2` fixture map to `type_1` and re-confirm
  the finding disappears; per SC-002/SC-004). _Satisfies: US2 Independent
  Test, SC-002, SC-004, SC-005._

**Checkpoint**: HR2 now fails closed on the ONE proven mechanical
contradiction (declared Type-2, built by drop-and-rebuild) and stays silent
for Type-1 and not-yet-buildable dimensions. This is the feature's MVP slice
-- independently testable and deployable, and it is the concrete signal that
makes today's silent gap visible.

---

## Phase 5: User Story 3 - A dimension's history policy is undeclared (Priority: P2)

**Goal**: A `gold_star.dimensions[]` entry with no `scd_type` key at all is
treated as a blocking Needs-decision, never a silent default to `type_1`.
Each undeclared dimension gets its own individually-traceable finding (not
one table-wide flag).

**Independent Test**: fixture `source-map.yaml` with one
`gold_star.dimensions[]` entry that has no `scd_type` key at all -> exactly
one Needs-decision finding naming that dimension, no other finding
fabricated in its place. A table with two such entries -> two findings, one
per dimension.

### Tests for User Story 3

- [ ] **T032** `[P]` `[US3]` Fixture
  `tests/fixtures/scd_history/source-map-undeclared.yaml` -- two variants in
  one fixture set: (a) a single `gold_star.dimensions[]` entry with no
  `scd_type` key; (b) a table with TWO such entries missing `scd_type`, both
  otherwise valid dimension entries. _Satisfies: US3 Acceptance Scenarios 1
  and 2, FR-005._
- [ ] **T033** `[US3]` `tests/unit/test_rule_hr2.py`: extend with RED tests
  over T032 asserting (a) exactly one `Severity.ERROR` Needs-decision finding
  naming the dimension for variant (a), with a message instructing a human
  to declare `type_1` or `type_2` (never inferring one), (b) exactly TWO
  findings for variant (b) -- one per undeclared dimension, not a single
  table-wide flag -- and (c) that adding a valid `scd_type` to the fixture
  clears that dimension's finding on a re-run (Acceptance Scenario 3);
  confirm FAIL against the Phase 4 implementation (no missing-key branch
  exists yet). Depends on T015, T025. _Satisfies: US3 Independent Test._

### Implementation for User Story 3

- [ ] **T034** `[US3]` In `rule_hr2.py`: implement the missing-key branch --
  for each `gold_star.dimensions[]` entry with NO `scd_type` key at all
  (distinct from an entry with an invalid non-empty value, T018's branch),
  emit `Finding(HR2, ERROR, ...)` naming the dimension and instructing a
  human to declare `type_1` or `type_2`; NEVER infer or silently default to
  `type_1` (FR-005). This fires for EVERY table's map, including one whose
  Mapping Ready approval predates this feature -- there is no
  already-approved-map grandfather clause (FR-005, Principle I). Depends on
  T017. _Satisfies: FR-005, US3 Acceptance Scenarios 1 and 2._
- [ ] **T035** `[US3]` Wire T034's missing-key branch into `check_hr2`
  alongside T018's invalid-value branch and T030's type_2-build branch, so
  all three branches run per dimension without overlapping (a dimension is
  in exactly one of: missing-key / invalid-value / valid-type_1 /
  valid-type_2, never more than one branch firing for the same dimension).
  Depends on T019, T030, T034. _Satisfies: FR-005, FR-006, FR-013
  (categorical, one concern per finding)._
- [ ] **T036** `[US3]` Run the extended `tests/unit/test_rule_hr2.py` (T033)
  against T034-T035 and confirm GREEN, including the mutation-verify
  direction (add `scd_type: "type_1"` to T032's fixture and confirm that
  dimension's Needs-decision finding clears while a sibling still-undeclared
  dimension's finding remains). _Satisfies: US3 Independent Test, SC-003._

**Checkpoint**: All three user stories are independently functional. HR2
never silently defaults an undeclared dimension, validates declared values,
and fails closed on the one proven Type-2/drop-and-rebuild mismatch. Every
`gold_star.dimensions[]` entry across the repo now produces at most one
finding, and that finding names exactly what is wrong.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: The remaining cross-cutting FRs (no numeric score, no SQL
execution, no Principle-V decision-making, generic-only artifacts, ASCII/
UTF-8 hygiene) plus final gate/documentation sign-off. These touch findings
and invariants across every branch built in Phases 3-5 rather than adding a
new trigger condition.

- [ ] **T037** `[P]` `[POLISH]` Add a source-inspection test to
  `tests/unit/test_rule_hr2.py` asserting `rule_hr2.py`'s source contains no
  write/open-for-write against any `source-map.yaml` or migration `.sql`
  path (mirrors SF1's write-absence test) -- and asserting no numeric
  percentage/ratio/"N of M" formatting appears in any emitted message
  string. _Satisfies: FR-011, FR-012, FR-013, SC-006 (mechanically verified,
  not just reviewed)._
- [ ] **T038** `[P]` `[POLISH]` Add a test to `tests/unit/test_rule_hr2.py`
  asserting `rule_hr2.py` never opens a database connection or invokes any
  execution-adapter import (grep-style assertion over the module source, no
  `psycopg`/`sqlalchemy`/live-connection import anywhere). _Satisfies:
  FR-004, FR-012, Principle VIII._
- [ ] **T039** `[P]` `[POLISH]` Grep `src/retail/rules/rule_hr2.py`,
  `templates/source-map.yaml`'s new `scd_type` line, and every fixture under
  `tests/fixtures/scd_history/` for any C086/pharmacy-specific dimension
  name, grain key, or column name; confirm every table/dimension/column name
  used is illustrative only (`dim_<entity_a>`-style or an equally generic
  stand-in), never a required literal in rule logic. _Satisfies: FR-015,
  SC-007._
- [ ] **T040** `[P]` `[POLISH]` Confirm every file this feature authors or
  edits (`rule_hr2.py`, the `templates/source-map.yaml` edit,
  `test_rule_hr2.py`, every `tests/fixtures/scd_history/*` file, and every
  doc edit in Phase 2) is ASCII, UTF-8 without BOM, using `--`/`->` instead
  of glyphs, and that every new path stays well under the Windows 260-char
  budget. _Satisfies: FR-016, Principle IX._
- [ ] **T041** `[POLISH]` Run the local unit-test + wiring gate:
  `ruff format --check src/ tests/`, `ruff check src/ tests/`,
  `pytest -m unit -x -q`, then `pytest -m unit
  tests/unit/test_wiring_meta_gate.py tests/unit/test_rules_wiring.py
  tests/unit/test_rule_count_claims.py tests/unit/test_rule_hr2.py` -- confirm
  ALL GREEN at the live rule count (re-verified per T002). Do **NOT** assert
  a clean full-repo `retail check` run: the current committed
  `retail_store_sales`/`demo_sample_orders` maps have undeclared
  `scd_type` entries by design (see the Landing-precondition warning at the
  top of this file) and MUST continue to fail HR2's FR-005 branch until a
  human declares real values -- that RED is the intended, deliberate outcome
  of this feature landing, not a defect to fix here. _Satisfies: SC-001
  (mechanism proven via fixtures), SC-008, plan.md local-verification
  requirement, plan.md "Landing precondition."_
- [ ] **T042** `[POLISH]` Confirm `tests/unit/test_wiring_meta_gate.py` and
  `tests/unit/test_rule_count_claims.py` still pass at the live count and
  that `all_rules()` (not just `EXPECTED_RULE_IDS`) contains `"HR2"`.
  _Satisfies: SC-008._
- [ ] **T043** `[POLISH]` Update `docs/glossary.md`'s `HR2` row (T010) and any
  cross-reference noted in T004 to reflect the FINAL Finding taxonomy
  (undeclared -> ERROR Needs-decision; invalid value -> ERROR; declared
  `type_2` + drop-and-rebuild -> ERROR; declared `type_1` -> no finding;
  `type_2` with no migration yet -> no finding) once Phases 3-5 land, so the
  doc and the code do not drift. _Satisfies: consistency with data-model.md
  Finding taxonomy._
- [ ] **T044** `[POLISH]` [OWNER SEAM -- OPEN, do not answer]
  Record Q-APPROVAL-SEAM (FR-017) as still OPEN in the feature's closing
  state -- no new `approvals[]` shape or `readiness-status.yaml` key is
  added anywhere; `scd_type` review continues to happen inside the existing
  Mapping Ready approval under the PENDING DEFAULT (folds in) until an owner
  rules otherwise. This task is a checklist confirmation, not a resolution.
  _Satisfies: FR-017 PENDING DEFAULT posture, Principle V guard._

**Checkpoint**: Feature complete, HR2's own tests + wiring lockstep green, no
numeric score anywhere, no domain-specific name baked into generic
artifacts, no SQL executed or database opened, and the one genuinely open
governance question (FR-017) is left open rather than silently decided. The
live tree's committed maps are EXPECTED to fail HR2's FR-005 branch until a
human declares real `scd_type` values -- that is the feature working as
designed, not a follow-up bug.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies; T003 (the template edit) requires
  T001's owner-seam confirmation. Docs-first: T003 lands before any Phase 2
  wiring task (hard rule #8).
- **Foundational (Phase 2)**: depends on Setup -- BLOCKS all user stories.
  T006 depends on T005; T007-T009 are parallel edits once T005 exists; T010
  depends on T005 (needs the final rule title) and on T002's live-count
  check (to know whether HR1 already claimed the family); T011 depends on
  T010 (count must match anchor); T012 depends on T006-T011 all landing.
- **User Stories (Phase 3-5)**: all depend on Foundational (Phase 2)
  completion (HR2 must be a registered, importable rule before its body can
  be tested). US1 (Phase 3) has no dependency on US2/US3 and builds the
  shared `_load_source_map` / `_iter_declared_dimensions` helpers. US2
  (Phase 4) reuses those helpers but is otherwise independent of US1's
  invalid-value branch -- implement after US1 lands so the helpers exist.
  US3 (Phase 5) reuses the same helpers and slots its missing-key branch
  alongside US1's invalid-value branch and US2's type_2-build branch
  (T035) -- implement after both US1 and US2 land so all three branches can
  be wired together without overlap.
- **Polish (Phase 6)**: depends on US1 + US2 + US3 all landing (the
  source-inspection and taxonomy-consistency tasks read the FINAL branch
  set).

### Within Each User Story

- Fixtures before tests-that-use-them; tests written and RED before the
  matching implementation task; implementation before the GREEN re-run task.
- `_load_source_map` / `_iter_declared_dimensions` (T016-T017) are shared
  read-only helpers built once in Phase 3 and reused (not reimplemented) by
  Phase 4/5.
- `_resolve_bare_table` / `_find_gold_migration` / `_has_drop_and_rebuild`
  (T026-T028) are Phase 4-only helpers, used solely by the `type_2`-build
  branch (T030); US1 and US3 never call them.

### Parallel Opportunities

- T007, T008, T009 (three different wiring-surface files) can run in
  parallel once T005/T006 exist.
- Within Phase 3/4/5/6, all `[P]`-marked fixture-authoring tasks (T013-T014,
  T021-T024, T032, T037-T040) touch different files and can run in parallel
  with each other (not with the shared-helper implementation tasks they feed
  into).

---

## Parallel Example: User Story 2 (the MVP)

```bash
# Launch all fixtures for User Story 2 together:
Task: "Fixture gold-ddl-insert-drop-rebuild.sql in tests/fixtures/scd_history/"
Task: "Fixture gold-ctas-drop-rebuild.sql in tests/fixtures/scd_history/"
Task: "Fixture gold-type1-drop-rebuild.sql in tests/fixtures/scd_history/"
Task: "Fixture source-map-type2-single-dim.yaml in tests/fixtures/scd_history/"
```

---

## Implementation Strategy

### MVP First (User Story 2 is the enforcement MVP; User Story 1 is its prerequisite)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational) -- HR2 registered as a
   no-op, wiring green, schema key present in the template.
2. Complete Phase 3 (US1) -- a valid/invalid `scd_type` declaration is
   recognized; this is the prerequisite the enforcement check reads.
3. Complete Phase 4 (US2) -- a `type_2`-declared dimension built by
   drop-and-rebuild fails closed; a `type_1` dimension never fires. This IS
   the feature's stated "whole point" (spec.md US2 rationale).
4. **STOP and VALIDATE**: run T031's mutation-verified fixtures
   independently.

### Incremental Delivery

1. Setup + Foundational -> HR2 registered, no-op, gate green, schema key in
   the template.
2. Add US1 -> declared-value validation (valid -> silent; invalid -> ERROR).
3. Add US2 -> MVP -- the build-honors-declaration enforcement gate.
4. Add US3 -> the undeclared-dimension Needs-decision floor, closing the
   adoption path for maps authored before this feature shipped (P2).
5. Polish -> SC-006/SC-007 mechanical verification, ASCII/UTF-8 hygiene,
   final six-surface gate confirmation, FR-017 left OPEN.

### Requirement Coverage Check (every FR maps to >=1 task)

- FR-001 -> T001, T003
- FR-002 -> T003, T013, T018
- FR-003 -> T003, T016
- FR-004 -> T005, T019, T027, T038
- FR-005 -> T032, T033, T034, T035
- FR-006 -> T014, T015, T018
- FR-007 -> T021, T022, T024, T026, T027, T028, T029, T030
- FR-008 -> T025, T027, T030
- FR-009 -> T023, T024, T030, T031
- FR-010 -> T017
- FR-011 -> T037
- FR-012 -> T037, T038
- FR-013 -> T005, T035, T037
- FR-014 -> T006-T012
- FR-015 -> T003, T039
- FR-016 -> T040
- FR-017 -> T044 (recorded OPEN, not answered)
