---
description: "Task list for 104-rename-impact-refactor-guard (Rename/Impact Refactor-Safety Static Rule, HR9)"
---

# Tasks: Rename/Impact Refactor-Safety Static Rule (HR9)

**Input**: Design documents from `specs/104-rename-impact-refactor-guard/`
(spec.md, plan.md, research.md, data-model.md)

**Tests**: Included -- this is a fail-closed governance rule; plan.md's
Testing section requires a golden-fixture pair (clean + planted-orphan)
mirroring the D1-D11/SF1/HR1 mutation-verified discipline.

**Manifest-less by design**: unlike SF1 (spec 086) / HR1 (spec 087), HR9
introduces **no hand-curated manifest YAML** (research.md Sec 2.1; SCOPE
GUARD "no shared-schema addition"). There is therefore **no Phase 0
manifest-authoring owner seam** in this task list -- the ONLY owner seam is
Q-APPROVAL-SEAM (FR-016), which stays OPEN and is never answered by any task
below.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3), or
  `SETUP`/`FOUND`/`POLISH` for cross-cutting phases
- Every task names an exact repo-relative file path

## Path Conventions

Single project (`src/retail/`, `tests/`, `docs/`) at repository root, per
plan.md "Structure Decision". No new project/service/top-level directory, no
new manifest schema.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Docs-first (hard rule #8). HR9 has no manifest/template to
author (manifest-less by design), so "docs before automation" here means:
land the two GATE-DOC narrative edits (which are inert prose until HR9
exists, and depend on nothing HR9's code produces) before any rule-wiring
task touches the registry/manifest/wiring-lockstep surfaces in Phase 2.

- [ ] **T001** `[SETUP]` Confirm the reserved static-rule id is **HR9**
  (collision-avoidance allocation, spec.md header) and that no other
  in-flight feature has claimed it in `src/retail/rules/__init__.py` or
  `docs/rules/rules-manifest.json` as of this branch's base. Plain
  confirmation (grep), not an owner ruling -- HR9's id is already reserved
  in the spec, this only guards against a same-day collision. _Satisfies:
  collision-avoidance allocation._
- [ ] **T002** `[SETUP]` Edit `docs/readiness/semantic-model-ready.md`:
  add an HR9 line to the "Blocking reasons" section/table, mirroring the
  existing "A `retail check` D1-D11 DAX/TMDL finding" bullet's shape (for
  example: "A `retail check` HR9 finding -- a metric-contract or DAX
  cross-reference to a gold column/measure name that does not resolve
  against the model's current committed TMDL"). _Satisfies: FR-011, FR-014
  (semantic-model-ready.md half), SC-007._
- [ ] **T003** `[SETUP]` Edit `docs/readiness/dashboard-ready.md`: add an
  HR9 line to the "Blocking reasons" section, scoped explicitly to the
  binding-map-orphan case only (a `semantic_model_field(s)` cell reference
  that does not resolve), distinguishing it from the semantic-model-ready.md
  line's broader scope (contract + DAX + binding-map). _Satisfies: FR-011,
  FR-014 (dashboard-ready.md half), SC-007._

**Checkpoint**: the gate docs already describe HR9's vocabulary before any
code exists, so `blocking_reasons[]` and the gate doc stay in agreement
(FR-014) the moment HR9's stub registers in Phase 2.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Reserve the rule id across every wiring surface, produce a
stub module, and build the SHARED read-only helpers (truth-set derivation,
the dual-form qualifier normalizer, the DAX-safe stripper) that US1 and US2
both depend on -- mirroring the SF1/AP1/HR1 wiring discipline but WITHOUT a
manifest-authoring step (none exists for HR9).

**CRITICAL**: No user story (Phase 3+) can be implemented until this phase
is complete: HR9 must exist as a registered (even if empty-bodied) rule
before its Finding-emitting logic can be tested via `retail check`, and the
wiring-lockstep surfaces (manifest, severity-posture, EXPECTED_RULE_IDS)
must land together with the stub so the meta-gate (manifest ids == registry
ids) never goes red mid-feature.

- [ ] **T004** `[FOUND]` Create the stub rule module
  `src/retail/rules/rename_impact_guard.py` with `RULE_ID = "HR9"`, a module
  docstring describing what HR9 does and never does (static-only, no auto-
  rename, no fuzzy matching, generic -- no worked-example name), and a
  `@register(RULE_ID, "rename/impact refactor-safety: gold column and
  measure reference resolution")`-decorated `check_hr9(ctx: RuleContext) ->
  Iterable[Finding]` that returns `[]` (stub body; Phase 3+ fills it in).
  _Satisfies: FR-001, FR-002, FR-009, FR-010, FR-013._
- [ ] **T005** `[FOUND]` Edit `src/retail/rules/__init__.py`: add
  `rename_impact_guard` to the side-effecting import tuple (alphabetical
  slot) AND to `__all__` in the same commit -- the ONLY discovery step (no
  autodiscovery). _Satisfies: FR-015 (wiring surface 1)._
- [ ] **T006** `[P]` `[FOUND]` Edit `tests/unit/test_rules_wiring.py`: add
  `"HR9"` to `EXPECTED_RULE_IDS` (alphabetical/grouped placement near the
  other reconcile-family ids, e.g. beside `SF1`/`DR1`). The set's `len()`
  drives the count check -- no bare literal is edited anywhere else for
  this. _Satisfies: FR-015 (wiring surface 2)._
- [ ] **T007** `[P]` `[FOUND]` Regenerate `docs/rules/rules-manifest.json`
  (via the repo's manifest-generation entrypoint, e.g. `retail manifest`, or
  by hand-adding `{"id": "HR9", "title": "rename/impact refactor-safety:
  gold column and measure reference resolution"}` in id order if no
  generator command exists) so it includes HR9 -- never hand-edited out of
  step with the live registry. _Satisfies: FR-015 (wiring surface 3)._
- [ ] **T008** `[P]` `[FOUND]` Edit `docs/rules/severity-posture.json`: add
  `"HR9": ["error"]` under the registered section -- HR9 has NO warning
  tier (data-model.md Entity 5: a reference either resolves or it is a
  genuine orphan, binary per hard rule #9). Do not copy HR1's
  `["error", "warning"]` shape. _Satisfies: FR-012, FR-015 (wiring surface
  4)._
- [ ] **T009** `[FOUND]` Edit `docs/glossary.md`: add the `HR9` row to the
  rules table (same family letter as any other already-registered `HR*`
  rule, or a new family entry if none has landed yet on this branch's base)
  describing the reconcile-and-fail-closed posture in the same style as the
  `SF`/`DF` rows; bump the "Currently N rules in M families" anchor to
  reflect **the live registered count plus HR9**, reconciled against
  `len(EXPECTED_RULE_IDS)` at the time this task is executed -- never a
  hardcoded `55 -> 56`-style guess, since other in-flight features may land
  first. _Satisfies: FR-015 (wiring surface 5)._
- [ ] **T010** `[FOUND]` Edit `docs/quality/rule-count-claims.yaml`: bump
  `claimed-count` for the `glossary-rule-count` entry to match T009's
  updated anchor text exactly (byte-consistent), computed the same
  reconciled way (live count, not a hardcoded literal). _Satisfies: FR-015
  (wiring surface 6)._
- [ ] **T011** `[FOUND]` In `rename_impact_guard.py`: implement
  `_governing_model_files(ctx)` / truth-set derivation -- for every file
  yielded by `tmdl.iter_model_files(ctx, ".tmdl")`, call `tmdl.parse_tmdl`
  and build a `TruthSet` per data-model.md Entity 1 (lowercased `columns`
  keyed by table name; lowercased `measures` unioned per `*.SemanticModel/`
  model folder). Depends on T004. Shared by US1 and US2; built once here to
  keep both stories independently testable without duplicating traversal
  logic. _Satisfies: FR-002, FR-006, FR-007 (a table with zero TMDL files
  contributes no TruthSet entry)._
- [ ] **T012** `[FOUND]` In `rename_impact_guard.py`: implement
  `normalize_qualifier(qualifier, tmdl_table_names)` per data-model.md
  Entity 4 -- try the dotted `schema.table` -> `schema table` exact-match
  form FIRST, then fall back to stripping each candidate `TmdlTable.name`'s
  leading `<schema> ` word and comparing the remainder against a bare
  qualifier (e.g. `dim_product_rss` matching `gold dim_product_rss`). Both
  forms are required -- data-model.md Entity 4 warns that omitting the bare
  form false-positives on every dim-column reference in the currently
  committed, already-approved binding map, breaking the green-baseline
  expectation (SC-005 sibling spirit). No hardcoded schema word (Principle
  VII) -- the leading word is read from whatever `TmdlTable.name` actually
  carries. Depends on T011. _Satisfies: FR-006, data-model.md Entity 4._
- [ ] **T013** `[FOUND]` In `rename_impact_guard.py`: implement a NEW
  sibling DAX comment/string stripper (e.g. `_strip_dax_comments_and_dquotes`)
  that strips `//` / `/* */` comments and double-quoted string literals
  ONLY -- explicitly NOT reusing `dax.py`'s `_strip_dax_comments_and_strings`,
  which also strips single-quoted `'Table Name'` tokens HR9 needs to keep
  (research.md Sec 1.2 caveat). Depends on T004. _Satisfies: FR-004
  (extraction correctness), research.md Sec 1.2._
- [ ] **T014** `[FOUND]` Run
  `pytest -m unit tests/unit/test_wiring_meta_gate.py
  tests/unit/test_rules_wiring.py tests/unit/test_rule_count_claims.py` and
  confirm all green with the HR9 stub registered at the live count.
  _Satisfies: SC-008 (wiring + rule-count lockstep stays green)._

**Checkpoint**: `HR9` is a real, registered, discoverable rule (currently a
no-op), the shared truth-set/normalization/stripper helpers exist, and every
wiring-lockstep meta-gate is green. User story implementation can now begin.

---

## Phase 3: User Story 1 - A renamed gold column orphans a metric contract reference (Priority: P1) MVP

**Goal**: Given a metric contract's `binds_to.columns` naming a column that
no longer exists in the cited gold table's current committed TMDL, HR9 fails
closed with one ERROR finding naming the contract file, the stale column
name, and the TMDL table it was checked against -- independent of the
contract's own `readiness.status` (FR-008).

**Independent Test**: rename a column in a committed TMDL table without
updating a metric contract's `binds_to.columns` that names the old value;
`retail check` produces exactly one HR9 finding naming the contract file and
the orphaned column name, present in `blocking_reasons[]` for that table's
Semantic Model Ready status.

### Tests for User Story 1

> Write these tests FIRST; they FAIL against the Phase 2 stub before Phase 3
> implementation lands (RED), then PASS after (GREEN).

- [ ] **T015** `[P]` `[US1]` Fixture pair
  `tests/fixtures/rename_impact_guard/contract_column_orphan/` -- a
  generic (non-worked-example, Principle VII) committed TMDL table plus a
  metric contract whose `binds_to.columns` names a column absent from that
  table's current TMDL. _Satisfies: US1 Acceptance Scenario 1, FR-003._
- [ ] **T016** `[P]` `[US1]` Fixture
  `tests/fixtures/rename_impact_guard/contract_column_clean/` -- the same
  shape with the contract corrected to name a column that DOES exist --
  used to assert the no-Finding path. _Satisfies: US1 Acceptance Scenario
  2._
- [ ] **T017** `[P]` `[US1]` Fixture
  `tests/fixtures/rename_impact_guard/contract_unapproved_orphan/` -- an
  orphaned `binds_to.columns` reference inside a metric contract whose
  `readiness.status` is explicitly NOT `pass` (e.g. `draft`) -- used to
  assert HR9 still fires regardless of approval state. _Satisfies: FR-008._
- [ ] **T018** `[US1]` `tests/unit/test_rename_impact_guard.py`: write the
  RED tests against T015/T016/T017 fixtures asserting exact
  `Severity.ERROR` count, message content (contract file + stale column
  name + TMDL table), and locator shape; confirm FAIL against the Phase 2
  stub. _Satisfies: US1 Independent Test._

### Implementation for User Story 1

- [ ] **T019** `[US1]` In `rename_impact_guard.py`: implement
  `_collect_contract_references(ctx)` -- glob
  `mappings/[^/]+/metrics/[^/]+\.ya?ml` (AL2's `_METRICS_RE` convention,
  research.md Sec 1.3), excluding `templates/metric-contract.yaml` and
  `tests/` paths (`is_test_path`); lazy `import yaml` inside this function
  only (Principle VIII / B1 / B3). For each contract, if `binds_to` is a
  mapping with a non-placeholder `gold_table`, emit one `Reference(kind=
  "contract-column", ...)` per entry in `binds_to.columns` per data-model.md
  Entity 2a; a malformed/placeholder `binds_to`/`gold_table` yields no
  reference (not itself an HR9 finding). Depends on T004. _Satisfies:
  FR-003, FR-008 (extraction ignores `readiness.status`)._
- [ ] **T020** `[US1]` In `rename_impact_guard.py`: implement the
  contract-column resolution path -- resolve each `contract-column`
  Reference's `qualifier` (the contract's `gold_table`) via
  `normalize_qualifier` (T012) against the TMDL tables in that table's own
  `*.SemanticModel/` model folder (data-model.md Entity 3, step 0 + step 2
  form (a)); case-fold and look up `token` in the resolved table's
  `TruthSet.columns` ONLY. No match on the qualifier -> orphan naming the
  qualifier; no match on the column -> orphan naming the column. Depends on
  T011, T012, T019. _Satisfies: FR-003, FR-006._
- [ ] **T021** `[US1]` In `rename_impact_guard.py`: wire the orphan ->
  `Finding(HR9, ERROR, ...)` emission per data-model.md Entity 3's message
  shape, naming the contract file, the stale column name, and the table
  checked against; append to `check_hr9`'s return list. Depends on T020.
  _Satisfies: FR-003, FR-009 (names the break, suggests no fix), FR-012
  (binary, no score)._
- [ ] **T022** `[US1]` Run `tests/unit/test_rename_impact_guard.py` (T018)
  against the Phase 3 implementation and confirm GREEN (mutation-verified:
  correct the fixture's column name back and re-confirm the Finding
  disappears). _Satisfies: US1 Independent Test, SC-001._

**Checkpoint**: HR9 correctly fails closed on an orphaned metric-contract
column reference, independent of approval state, and passes silently when
the reference resolves. This is the MVP slice -- independently testable and
deployable.

---

## Phase 4: User Story 2 - A renamed measure orphans a DAX reference and a dashboard binding (Priority: P1)

**Goal**: Given a TMDL measure's own DAX expression referencing another
measure or table-qualified column that no longer exists, AND/OR a dashboard
binding-map cell referencing a measure/`dim[column]` that no longer exists,
HR9 fails closed with one ERROR finding per orphaned reference, naming the
referencing measure/visual row, the artifact, and the stale token.

**Independent Test**: rename a TMDL measure without updating a second
measure's DAX expression that references it by name, and without updating
the binding map; `retail check` produces one HR9 finding for the DAX
cross-reference and one for the binding-map reference, each naming the
stale measure name and the citing artifact.

### Tests for User Story 2

- [ ] **T023** `[P]` `[US2]` Fixture
  `tests/fixtures/rename_impact_guard/dax_measure_orphan/` -- a TMDL model
  with two measures, where one's DAX expression references
  `[OtherMeasure]` and no measure by that name currently exists in the same
  model. _Satisfies: US2 Acceptance Scenario 1, FR-004._
- [ ] **T024** `[P]` `[US2]` Fixture
  `tests/fixtures/rename_impact_guard/dax_column_orphan/` -- a TMDL measure
  whose DAX expression references `'table'[column]` where `column` no
  longer exists on that table. _Satisfies: FR-004 (column-token limb),
  FR-006 (table-qualified resolution)._
- [ ] **T025** `[P]` `[US2]` Fixture
  `tests/fixtures/rename_impact_guard/dax_cross_model_isolation/` -- two
  different `*.SemanticModel/` folders each defining a measure with the
  SAME name, where one model's DAX references it; used to assert HR9
  resolves against the REFERENCING model's own folder only, never the
  other model's. _Satisfies: Edge Cases "two model folders share a measure
  name", FR-006._
- [ ] **T026** `[P]` `[US2]` Fixture
  `tests/fixtures/rename_impact_guard/binding_map_orphan/` -- a committed
  visual-contract binding map whose `semantic_model_field(s)` cell names a
  `[Measure]` or `dim[column]` token absent from the current committed
  model, mixed with prose/qualifiers (`by`, `(Top N)`, `(month)`) per
  Q-BINDING-CELL-PARSE, to confirm only the bracket token is extracted.
  _Satisfies: US2 Acceptance Scenario 2, FR-005._
- [ ] **T027** `[P]` `[US2]` Fixture
  `tests/fixtures/rename_impact_guard/binding_map_dim_own_table/` -- a
  binding-map cell naming `dim[column]` where the DIMENSION's own TMDL (not
  the fact table's) is the one missing the column -- used to confirm HR9
  resolves against the named dimension's own TMDL, not the fact table's.
  _Satisfies: Edge Cases "dim's own TMDL renamed the column"._
- [ ] **T028** `[P]` `[US2]` Fixture
  `tests/fixtures/rename_impact_guard/case_insensitive_match/` -- a DAX
  expression referencing `[totalsales]` where the committed measure is
  named `TotalSales` -- used to assert this is NOT an orphan
  (Q-CASE-SENSITIVITY). _Satisfies: Edge Cases "case-insensitive
  resolution", FR-004._
- [ ] **T029** `[US2]` Extend `tests/unit/test_rename_impact_guard.py` with
  RED tests over T023-T028 asserting exact ERROR counts/messages for the
  orphan fixtures, exact no-Finding assertions for the isolation/dim-own-
  table/case-insensitive fixtures, and that a corrected DAX expression AND
  binding map together clear both findings (US2 Acceptance Scenario 3);
  confirm FAIL against the Phase 3-only implementation (US1 code has no
  DAX/binding-map branches yet). _Satisfies: US2 Independent Test._

### Implementation for User Story 2

- [ ] **T030** `[US2]` In `rename_impact_guard.py`: implement
  `_collect_dax_references(ctx)` -- for every `TmdlMeasure.expression` from
  every parsed TMDL table in scope (reusing T011's traversal), strip via
  T013's stripper, then extract `[MeasureName]` (unqualified,
  `is_bracket_measure=True`) and `'Table Name'[ColumnName]` (qualified,
  `is_bracket_measure=False`) tokens per data-model.md Entity 2b, tagging
  `locator_detail` with the REFERENCING measure's name. Depends on T011,
  T013. _Satisfies: FR-004._
- [ ] **T031** `[US2]` In `rename_impact_guard.py`: implement the
  DAX-cross-reference resolution path -- for an unqualified `[Measure]`
  token, case-fold and resolve against the UNION of `TruthSet.measures`
  across every TMDL table file inside the SAME `*.SemanticModel/` model
  folder as the referencing TMDL file (data-model.md Entity 3 step 1, FR-006
  cross-model isolation); for a qualified `'table'[column]` token, resolve
  `qualifier` via `normalize_qualifier` (T012) within that same model
  folder, then case-fold-match `token` against that table's own
  `TruthSet.columns` ONLY (Entity 3 step 2). No match -> orphan `Finding
  (HR9, ERROR, ...)` naming the referencing measure, the TMDL file, and the
  stale token. Depends on T012, T030. _Satisfies: FR-004, FR-006._
- [ ] **T032** `[US2]` In `rename_impact_guard.py`: implement
  `_collect_binding_map_references(ctx)` -- read the committed dashboard
  visual-contract binding map(s) (e.g.
  `mappings/<table>/design/visual-contract-binding-map.md`), locate the
  `semantic_model_field(s)` column, and for each cell extract ONLY
  bracket-delimited `[Measure]` / `dim[column]` tokens (regex-based,
  ignoring "by", parenthetical qualifiers, and all other prose) per
  data-model.md Entity 2c / Q-BINDING-CELL-PARSE; resolve the binding map's
  governing model via its own committed pointer (e.g. `governed_model:
  ../../../powerbi/<Model>.SemanticModel`, data-model.md Entity 3 step 0).
  `locator_detail` names the visual row. Depends on T011. _Satisfies:
  FR-005._
- [ ] **T033** `[US2]` In `rename_impact_guard.py`: implement the
  binding-map resolution path -- same step-1/step-2 resolution logic as
  T031 (unqualified `[Measure]` against the governing model's measure
  union; `dim[column]` qualifier resolved via `normalize_qualifier` against
  the governing model's TMDL tables, then column looked up on that table
  only). No match -> orphan `Finding(HR9, ERROR, ...)` naming the
  binding-map file, the visual row, and the stale reference. Depends on
  T012, T032. _Satisfies: FR-005, FR-006._
- [ ] **T034** `[US2]` Run the extended
  `tests/unit/test_rename_impact_guard.py` (T029) against T030-T033 and
  confirm GREEN, including the mutation-verify direction (correct the DAX
  expression and the binding-map cell, re-confirm both findings clear).
  _Satisfies: US2 Independent Test, SC-002, SC-003._

**Checkpoint**: HR9 now fails closed on a DAX measure-to-measure orphan, a
DAX measure-to-column orphan, and a binding-map orphan, all case-insensitive
and cross-model-isolated, while a dimension's own TMDL and a same-model
case-variant resolve correctly. US1 and US2 together deliver the feature's
full P1 scope.

---

## Phase 5: User Story 3 - A table with no model surface yet is a clean no-op (Priority: P2)

**Goal**: A table with metric contracts (and, hypothetically, a binding map)
but no committed TMDL file produces zero HR9 findings; once a TMDL file is
later committed for that table, HR9 begins checking its references.

**Independent Test**: run `retail check` against a table with metric
contracts but no committed TMDL table file; confirm zero HR9 findings for
that table; add a TMDL file for it; confirm HR9 now checks its references.

### Tests for User Story 3

- [ ] **T035** `[P]` `[US3]` Fixture
  `tests/fixtures/rename_impact_guard/no_tmdl_yet/` -- a metric contract
  (with a `binds_to.columns` reference that would otherwise be an orphan)
  for a table with NO committed TMDL file under
  `powerbi/*.SemanticModel/definition/tables/` -- used to assert zero
  findings. _Satisfies: US3 Acceptance Scenario 1, FR-007._
- [ ] **T036** `[US3]` Extend `tests/unit/test_rename_impact_guard.py` with
  a RED test over T035 asserting `len(findings) == 0` for that table, then a
  second phase of the same test that adds a TMDL file lacking the
  contract's referenced column and confirms the orphan finding NOW appears
  (US3 Acceptance Scenario 2); confirm the first assertion would FAIL if
  T011's traversal is not already scoped per-table-with-TMDL. _Satisfies:
  US3 Independent Test._

### Implementation for User Story 3

- [ ] **T037** `[US3]` In `rename_impact_guard.py`: confirm/harden that
  `_collect_contract_references` (T019) and the resolution paths (T020,
  T031, T033) never fabricate a `TruthSet` entry for a table with zero
  committed TMDL files -- a contract-column reference whose `gold_table`
  does not resolve to ANY TMDL table anywhere in the tree is reported as an
  unresolved QUALIFIER orphan only if TMDL model surfaces exist elsewhere in
  the tree (per data-model.md Entity 3 step 2's "qualifier itself
  unresolved" branch does NOT apply when there is no TMDL surface at all
  for that table's model); when the table has genuinely no TMDL file
  anywhere, no `Reference` from that table is resolved and no Finding is
  produced -- add the explicit early-continue for this case if T020 does
  not already guarantee it. Depends on T011, T020. _Satisfies: FR-007._
- [ ] **T038** `[US3]` Run the extended
  `tests/unit/test_rename_impact_guard.py` (T036) and confirm GREEN for
  both the zero-TMDL no-op and the TMDL-added engagement transition.
  _Satisfies: US3 Independent Test, SC-005._

**Checkpoint**: All three user stories are independently functional. HR9
does not fire prematurely on a table with no model surface, and engages
correctly the moment one is committed.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Mechanical verification of the spec's global guarantees
(read-only, no worked-example hardcode, no numeric score, wiring lockstep)
and the final gate/documentation sign-off. These are cross-cutting because
they verify properties of the WHOLE rule rather than adding a new trigger
condition.

- [ ] **T039** `[P]` `[POLISH]` Add a source-inspection test to
  `tests/unit/test_rename_impact_guard.py` asserting `rename_impact_guard.py`'s
  source contains no file-write/open-for-write call anywhere (mirrors SF1's
  `SPINE_REL`-write-absence test) -- HR9 is read-only by construction.
  _Satisfies: FR-010, SC-006._
- [ ] **T040** `[P]` `[POLISH]` Extend the same test file with an assertion
  that no emitted `Finding.message` contains a numeric percentage, ratio, or
  "N of M" style confidence/health/maturity/completeness phrasing (hard rule
  #9). _Satisfies: FR-012._
- [ ] **T041** `[P]` `[POLISH]` Grep `src/retail/rules/rename_impact_guard.py`
  for any C086/pharmacy/`retail_store_sales`-specific table, column, or
  measure name; confirm none appears as a required literal in the rule's
  logic (worked-example names may appear only in research.md/plan.md/
  data-model.md as CITED, inspected examples, never in the rule source
  itself). _Satisfies: FR-013, SC-004._
- [ ] **T042** `[P]` `[POLISH]` Grep test fixture names/contents under
  `tests/fixtures/rename_impact_guard/` to confirm they use generic
  placeholder table/column/measure names, not `retail_store_sales`/C086
  specifics (Principle VII). _Satisfies: FR-013 (fixture hygiene)._
- [ ] **T043** `[POLISH]` Run the full local gate:
  `ruff format --check src/ tests/`, `ruff check src/ tests/`,
  `pytest -m unit -x -q`, then `retail check` and `retail kit-lint` --
  confirm GREEN on the current committed tree (the committed
  `retail_store_sales` metric contracts, TMDL, and binding map produce ZERO
  HR9 findings, per Entity 4's dual-form normalization keeping the existing
  bare-qualifier dim references resolvable). _Satisfies: SC-005 (as a
  real-tree check, not just fixtures), plan.md local-verification
  requirement._
- [ ] **T044** `[POLISH]` Confirm `tests/unit/test_wiring_meta_gate.py` and
  `tests/unit/test_rule_count_claims.py` still pass at the live count and
  that `all_rules()` (not just `EXPECTED_RULE_IDS`) contains `"HR9"`.
  _Satisfies: SC-008._
- [ ] **T045** `[POLISH]` [OWNER SEAM -- OPEN, do not answer] Record
  Q-APPROVAL-SEAM (FR-016) as still OPEN in the feature's closing state --
  no new `approvals[]` shape is added, no `readiness-status.yaml` key is
  touched, and HR9 records no new approval requirement anywhere; this task
  is a checklist confirmation, not a resolution. The RECORDED PENDING
  DEFAULT (MECHANICAL, no new approval seam) stays pending, not promoted to
  adopted, by this task. _Satisfies: FR-016 PENDING DEFAULT posture,
  Principle V guard._
- [ ] **T046** `[POLISH]` Re-read `docs/readiness/semantic-model-ready.md`
  (T002) and `docs/readiness/dashboard-ready.md` (T003) once Phase 3-5 land;
  confirm the gate-doc wording matches the FINAL Finding taxonomy (contract-
  column / DAX-cross-ref / binding-map orphan, all ERROR-only, no WARNING
  tier) so the doc and the code do not drift. _Satisfies: FR-014
  consistency, SC-007._

**Checkpoint**: Feature complete, gate green, no numeric score anywhere, no
domain-specific name baked into the rule or its fixtures, wiring lockstep
intact, HR9 verifiably read-only, and the one genuinely open governance
question (FR-016) is left open rather than silently decided.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies; the two gate-doc edits (T002, T003)
  are inert prose that can land before any code exists (docs-first, hard
  rule #8) since HR9 has no manifest/template to author first.
- **Foundational (Phase 2)**: depends on Setup only loosely (T001's
  collision check gates nothing else); BLOCKS all user stories. T005
  depends on T004; T006-T008 are parallel edits once T004 exists; T009
  depends on T004 (needs the final rule title) and reads the live registry
  state, not a hardcoded number; T010 depends on T009 (count/anchor must
  match); T011-T013 depend on T004 and on each other only where noted; T014
  depends on T005-T010 all landing.
- **User Stories (Phase 3-5)**: all depend on Foundational (Phase 2)
  completion (HR9 must be a registered, importable rule, and the shared
  `_governing_model_files`/`normalize_qualifier`/stripper helpers must
  exist, before any story's body can be tested). US1 (Phase 3) has no
  dependency on US2/US3. US2 (Phase 4) reuses US1's contract-collection
  pattern only as a sibling (its own `_collect_dax_references` /
  `_collect_binding_map_references` are new) -- implement after US1 lands
  so the shared Phase 2 helpers are proven, though the underlying rule
  logic is a single `check_hr9` function, not separable services. US3
  (Phase 5) depends on US1's T020 (contract resolution path) to harden
  against the zero-TMDL case.
- **Polish (Phase 6)**: depends on US1 + US2 + US3 all landing (the
  source-inspection and green-baseline tasks verify the FINAL rule body).

### Within Each User Story

- Fixtures before tests-that-use-them; tests written and RED before the
  matching implementation task; implementation before the GREEN re-run task.
- `_governing_model_files` / `normalize_qualifier` / the DAX-safe stripper
  (T011-T013) are shared read-only helpers built once in Phase 2 and reused
  (not reimplemented) by Phase 3/4/5.

### Parallel Opportunities

- T006, T007, T008 (three different wiring-surface files) can run in
  parallel once T004/T005 exist.
- Within Phase 3/4/5/6, all `[P]`-marked fixture-authoring tasks (T015-T017,
  T023-T028, T035, T039-T042) touch different files and can run in parallel
  with each other (not with the shared-helper or resolution-path
  implementation tasks they feed into).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup, gate docs) + Phase 2 (Foundational) -- HR9
   registered as a no-op, wiring green, shared helpers in place.
2. Complete Phase 3 (US1) -- an orphaned metric-contract column reference
   fails closed regardless of approval state; a resolved reference passes
   silently.
3. **STOP and VALIDATE**: run T022's mutation-verified fixtures
   independently.
4. This is the MVP: the exact gap the feature exists to close (spec.md US1
   rationale).

### Incremental Delivery

1. Setup + Foundational -> HR9 registered, no-op, gate green, gate docs
   already describe the vocabulary.
2. Add US1 -> MVP -- the metric-contract column-orphan gate.
3. Add US2 -> the DAX cross-reference and binding-map orphan gates (both
   P1, co-equal with US1 per spec.md's stated highest-risk framing).
4. Add US3 -> confirms no premature engagement on a table with no model
   surface yet (adoptability requirement, P2).
5. Polish -> read-only/no-hardcode/no-score mechanical verification, final
   six-surface wiring gate confirmation, gate-doc consistency re-check.

### Requirement Coverage Check (every FR maps to >=1 task)

- FR-001 -> T004
- FR-002 -> T004, T011
- FR-003 -> T019, T020, T021
- FR-004 -> T030, T031
- FR-005 -> T032, T033
- FR-006 -> T012, T020, T031, T033
- FR-007 -> T037, T038
- FR-008 -> T017, T019
- FR-009 -> T021 (names the break, never edits/suggests)
- FR-010 -> T004, T039
- FR-011 -> T002, T003, T046 (gate-doc listing + finding stream; no
  `readiness_status.py` code change -- research.md Sec 4 confirms RS1 is
  unchanged)
- FR-012 -> T008, T021, T040
- FR-013 -> T004, T041, T042
- FR-014 -> T002, T003, T046
- FR-015 -> T005, T006, T007, T008, T009, T010
- FR-016 -> T045 (recorded OPEN, not answered)
