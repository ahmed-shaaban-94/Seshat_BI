---
description: "Task list for 087-conformed-dimension-readiness (Cross-Star Conformed-Dimension Readiness Gate)"
---

# Tasks: Cross-Star Conformed-Dimension Readiness Gate

**Input**: Design documents from `specs/087-conformed-dimension-readiness/`
(spec.md, plan.md, research.md, data-model.md)

**Tests**: Included -- the plan's Testing section requires mutation-verified
fixtures (SF1/AP1 discipline); this is a fail-closed governance rule, not
optional coverage.

**Status carried from plan.md**: DRAFT. This task list authors the design;
it does not itself constitute ratification. Phase 0 contains an OWNER SEAM
that gates a green landing (mirrors 086/SF1's Phase 0 pattern) and FR-016
(Q-APPROVAL-SEAM) stays OPEN for the owner -- no task below answers it.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3), or
  `SETUP`/`FOUND`/`POLISH` for cross-cutting phases
- Every task names an exact repo-relative file path

## Path Conventions

Single project (`src/retail/`, `tests/`, `docs/`) at repository root, per
plan.md "Structure Decision". No new project/service/top-level directory.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the landing precondition and reserve the rule id before
any code is written. Docs-first per hard rule #8: the human-authored manifest
and its shape are authored before the static-rule wiring task.

- [ ] **T001** `[SETUP]` [OWNER SEAM] Confirm/ratify that the reserved static-rule
  id is **HR1** and the new artifact path is `docs/quality/conformed-dimension-map.yaml`
  (collision-avoidance allocation, spec.md Assumptions "Ratification pending").
  No code or doc task below may rename either. _Satisfies: spec.md collision
  allocation; FR-002, FR-003._
- [ ] **T002** `[SETUP]` Confirm the current tree's landing precondition
  (research.md "Landing precondition") is satisfied by an EMPTY-BUT-PRESENT
  manifest (`dimensions: {}`): the two committed stars (`retail_store_sales`,
  `demo_sample_orders`) share NO dimension name today, so there is nothing to
  adjudicate `conformed` vs `distinct`, and authoring the empty shape is NOT a
  Principle-V act (research.md is explicit: no collision exists to rule on).
  Plain confirmation, not an owner ruling -- clears the way for T003.
  _Satisfies: research.md Landing precondition; Principle V guard._
- [ ] **T003** `[SETUP]` Author `docs/quality/conformed-dimension-map.yaml` with the
  empty-but-present shape (`dimensions: {}` plus the authoring-comment header
  documenting the `status: conformed|distinct` / `stars: [...]` entry shape from
  data-model.md "ConformedDeclaration"). ASCII, UTF-8 no BOM (Principle IX).
  Depends on T002 (owner authorization for the empty scaffold). _Satisfies: FR-002,
  FR-013 (generic, illustrative names only), Principle IX._
- [ ] **T004** `[SETUP]` Confirm (checklist task, no file edit outside T003) that
  the model-level tier stays orthogonal per FR-001: no eighth readiness stage is
  introduced, no `mappings/<table>/readiness-status.yaml` gains a new key, and
  `docs/readiness/readiness-model.md` / `docs/readiness/gold-ready.md` remain
  UNEDITED reference-only per plan.md's Project Structure (neither file is in
  this feature's file footprint). T003's manifest header is the one place this
  feature documents the tier's relationship to Gold Ready. _Satisfies: FR-001
  (orthogonal tier), spec.md Boundary section, plan.md file-footprint fidelity._

**Checkpoint**: the manifest exists (empty, human-authorized) and the tier's
doc boundary is recorded before any rule code is written.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Reserve the rule id across every wiring surface and produce a
stub module, mirroring the SF1/AP1 six-surface wiring discipline (FR-014).
**No user-story Finding logic is implemented yet in this phase** -- only the
scaffold that makes `@register("HR1", ...)` compile and be discoverable.

**CRITICAL**: No user story (Phase 3+) can be implemented until this phase
is complete, because HR1 must exist as a registered (even if empty-bodied)
rule before its Finding-emitting logic can be tested via `retail check`.

- [ ] **T005** `[FOUND]` Create the stub rule module `src/retail/rules/rule_hr1.py`
  with `RULE_ID = "HR1"`, the module docstring (mirrors rule_sf1.py's shape:
  what HR1 does, what it never does, static-only, lazy `import yaml`), and a
  `@register(RULE_ID, "cross-star conformed-dimension readiness gate")`-decorated
  `check_hr1(ctx: RuleContext) -> Iterable[Finding]` that returns `[]` (stub
  body; Phase 3+ fills it in). _Satisfies: FR-003, FR-013._
- [ ] **T006** `[FOUND]` Edit `src/retail/rules/__init__.py`: add `rule_hr1` to
  the side-effecting import tuple (alphabetical slot, before `rule_sf1`,
  after `rule_count_claims`) AND to `__all__` in the same commit -- the ONLY
  discovery step (no autodiscovery). _Satisfies: FR-014 (wiring surface 1)._
- [ ] **T007** `[P]` `[FOUND]` Edit `tests/unit/test_rules_wiring.py`: add
  `"HR1"` to `EXPECTED_RULE_IDS`. _Satisfies: FR-014 (wiring surface 2)._
- [ ] **T008** `[P]` `[FOUND]` Edit `docs/rules/rules-manifest.json`: add
  `{"id": "HR1", "title": "cross-star conformed-dimension readiness gate"}`
  in id order after the `SF1` entry. _Satisfies: FR-014 (wiring surface 3)._
- [ ] **T009** `[P]` `[FOUND]` Edit `docs/rules/severity-posture.json`: add
  `"HR1": ["error", "warning"]` under the registered section (HR1 emits both
  severities per data-model.md's Finding taxonomy). _Satisfies: FR-014
  (wiring surface 4)._
- [ ] **T010** `[FOUND]` Edit `docs/glossary.md`: add the `HR1` row to the
  rules table (new family letter, e.g. `HR` -- confirm no collision with an
  existing family letter) describing the map + fail-closed/warn posture in
  the same style as the `SF` row; bump the "Currently 55 rules in 21
  families" anchor to **56 rules in 22 families** (append `HR` to the family
  list). _Satisfies: FR-014 (wiring surface 5)._
- [ ] **T011** `[FOUND]` Edit `docs/quality/rule-count-claims.yaml`: bump
  `claimed-count` from `55` to `56` for the `glossary-rule-count` entry, kept
  byte-consistent with T010's anchor text (SC2 reconciles the two).
  _Satisfies: FR-014 (wiring surface 6), SC-007._
- [ ] **T012** `[FOUND]` Run `pytest -m unit tests/unit/test_wiring_meta_gate.py
  tests/unit/test_rules_wiring.py tests/unit/test_rule_count_claims.py` and
  confirm all green with the HR1 stub registered at count 56. _Satisfies:
  SC-007 (wiring + rule-count lockstep stays green)._

**Checkpoint**: `HR1` is a real, registered, discoverable rule (currently a
no-op) and every meta-gate lockstep is green. User story implementation can
now begin.

---

## Phase 3: User Story 1 - Fail closed when a declared-conformed dimension diverges (Priority: P1) MVP

**Goal**: Given a map declaring a dimension `conformed` across 2+ stars, HR1
reads each star's `gold_star.dimensions[]` + `columns[].silver_type` from its
`source-map.yaml` and emits one fail-closed ERROR naming the dimension, the
disagreeing stars, and WHAT diverged (key or type; grain is
`[PENDING SCHEMA PREREQUISITE]` per C3/research.md) -- or no Finding when the
stars agree.

**Independent Test**: fixture map declares `dim_product` conformed across
stars A and B whose `source-map.yaml` disagree on `surrogate_key` (or a
shared attribute's `silver_type`) -> exactly one ERROR naming the dimension,
both stars, and the divergent values; made to agree -> no Finding.

### Tests for User Story 1

> Write these tests FIRST; they FAIL against the Phase 2 stub before Phase 3
> implementation lands (RED), then PASS after (GREEN) -- SF1/AP1 mutation
> discipline.

- [ ] **T013** `[P]` `[US1]` Fixture pair
  `tests/fixtures/conformed_dimension/key_divergence/` -- two minimal
  `source-map.yaml` stand-ins (or a fixture `RuleContext` per SF1's
  `ctx.tracked_files` pattern) whose declared-conformed dimension disagrees
  on `surrogate_key`, plus a `conformed-dimension-map.yaml` fixture declaring
  it `conformed`. _Satisfies: US1 Acceptance Scenario 1, FR-005 (key limb)._
- [ ] **T014** `[P]` `[US1]` Fixture pair
  `tests/fixtures/conformed_dimension/type_divergence/` -- same shape, but the
  stars agree on `surrogate_key` and disagree on a shared (intersection)
  attribute's `silver_type`. _Satisfies: US1 Acceptance Scenario 2, FR-005
  (type limb), C4 (intersection-only compare)._
- [ ] **T015** `[P]` `[US1]` Fixture pair
  `tests/fixtures/conformed_dimension/agree/` -- stars agree on grain-adjacent
  key + every shared attribute type; used to assert the NO-Finding path.
  _Satisfies: US1 Acceptance Scenario 3._
- [ ] **T016** `[US1]` `tests/unit/test_rule_hr1.py`: write the RED tests
  against T013/T014/T015 fixtures asserting exact `Severity.ERROR` count,
  message content (dimension name + both star ids + diverging values), and
  locator shape, plus the zero-Finding case for T015 -- run and confirm they
  FAIL against the Phase 2 stub. _Satisfies: US1 Independent Test._

### Implementation for User Story 1

- [ ] **T017** `[US1]` In `src/retail/rules/rule_hr1.py`: implement
  `_discover_stars(ctx)` -- glob `mappings/*/source-map.yaml` from
  `ctx.tracked_files`, parse each (lazy `import yaml`), and keep only tables
  whose parsed content carries `gold_star.fact` (rich or compact form) per
  data-model.md "Star / Is-a-star test". Depends on T005. _Satisfies:
  data-model.md Star entity, FR-004 (input source)._
- [ ] **T018** `[US1]` In `rule_hr1.py`: implement `_gold_dimensions(star)` --
  extract each star's `GoldDimension` list from `gold_star.dimensions[]`
  (name, `surrogate_key` if present, `attributes[]`) PLUS a synthesized entry
  for a standalone `gold_star.date_dimension` block when present (C1/FR-004);
  explicitly skip `gold_star.degenerate_dimensions[]` (never traversed).
  Depends on T017. _Satisfies: FR-004, C1, data-model.md GoldDimension +
  date-dimension recognition._
- [ ] **T019** `[US1]` In `rule_hr1.py`: implement
  `_attribute_silver_type(star, dim_name, attr)` -- resolve via the star's
  `columns[]` entries whose `gold_placement == f"dim:{dim_name}.{attr}"`,
  returning `None` (never raising) when the join is unavailable (compact-form
  degradation per data-model.md "Graceful degradation rule"). Depends on
  T017. _Satisfies: FR-004, FR-005 (type limb), research.md "type limb is
  mechanically implementable"._
- [ ] **T020** `[US1]` In `rule_hr1.py`: implement `_load_map(ctx)` -- read
  `docs/quality/conformed-dimension-map.yaml` (lazy yaml), return the parsed
  `dimensions:` mapping; this task only wires the READ path used by US1 (the
  missing/malformed-map ERROR paths belong to US2/edge-case tasks below, not
  duplicated here). Depends on T005. _Satisfies: FR-002 (read-only), C2 shape._
- [ ] **T021** `[US1]` In `rule_hr1.py`: implement the `conformed`-branch
  comparison -- for each dimension declared `status: conformed` with `stars:`
  naming 2+ resolvable stars that all carry that dimension: (a) compare
  `surrogate_key` across all named stars, comparing ONLY fields present on
  both sides of each pair (never crash on an absent field, data-model.md
  graceful-degradation rule); (b) compute the Kimball conformed-subset
  (intersection of `attributes[]` name sets) and compare each intersection
  attribute's resolved silver type across stars; emit ONE
  `Finding(HR1, ERROR, ...)` per diverging dimension naming the dimension,
  the disagreeing stars, and WHAT diverged (key values or the attribute +
  conflicting types); emit no Finding when all present fields agree. Grain
  comparison is explicitly OUT for this feature -- see T022. Depends on
  T018, T019, T020. _Satisfies: FR-005 (key + type limbs), C4, US1 all three
  Acceptance Scenarios._
- [ ] **T022** `[US1]` In `rule_hr1.py`: add a code comment (not a Finding)
  at the grain-comparison call site marking it
  `# [PENDING SCHEMA PREREQUISITE] -- see research.md C3; no natural-key
  marker exists in gold_star.dimensions[].attributes[] yet` so the deferred
  limb is visibly authored-pending rather than silently absent (Principle
  VIII: author static structure, mark live/pending explicitly). Depends on
  T021. _Satisfies: FR-005 grain-limb deferral, C3, plan.md Summary._
- [ ] **T023** `[US1]` Run `tests/unit/test_rule_hr1.py` (T016) against the
  Phase 3 implementation and confirm GREEN (mutation-verified: flip each
  fixture's divergent field back to agreement and re-confirm the Finding
  disappears). _Satisfies: US1 Independent Test, SC-002._

**Checkpoint**: HR1 correctly fails closed on a declared-conformed
key/type divergence and passes silently when stars agree. This is the MVP
slice -- independently testable and deployable.

---

## Phase 4: User Story 2 - Fail closed on an UNDECLARED shared dimension (Priority: P1)

**Goal**: When the same dimension name appears in 2+ stars with no map entry
(neither `conformed` nor `distinct`), HR1 emits a fail-closed ERROR naming
the dimension and every carrying star. A `distinct` declaration clears the
ERROR and permits divergence. A missing/unparseable map with 2+ stars is
also a fail-closed ERROR (FR-010); a malformed entry (bad enum value or an
unresolvable named star) is likewise an ERROR (FR-010).

**Independent Test**: two fixture stars both carry `dim_store` with no map
entry -> one ERROR naming `dim_store` and both stars; add a `conformed` or
`distinct` entry -> the undeclared ERROR clears.

### Tests for User Story 2

- [ ] **T024** `[P]` `[US2]` Fixture pair
  `tests/fixtures/conformed_dimension/undeclared_collision/` -- two stars
  both carrying a same-named dimension, with a
  `conformed-dimension-map.yaml` fixture that has NO entry for that name.
  _Satisfies: US2 Acceptance Scenario 1, FR-006._
- [ ] **T025** `[P]` `[US2]` Fixture
  `tests/fixtures/conformed_dimension/single_star_no_collision/` -- a
  dimension name present in exactly one star -- used to assert no Finding.
  _Satisfies: US2 Acceptance Scenario 2._
- [ ] **T026** `[P]` `[US2]` Fixture
  `tests/fixtures/conformed_dimension/distinct_declared/` -- two stars with a
  same-named dimension that genuinely differs in shape, declared `distinct`
  in the map -- used to assert no ERROR. _Satisfies: US2 Acceptance Scenario
  3, FR-008._
- [ ] **T027** `[P]` `[US2]` Fixture
  `tests/fixtures/conformed_dimension/missing_manifest/` -- 2+ stars present,
  `conformed-dimension-map.yaml` absent from `ctx.tracked_files` -- used to
  assert the FR-010 missing-manifest ERROR. _Satisfies: FR-010 (missing
  case)._
- [ ] **T028** `[P]` `[US2]` Fixture
  `tests/fixtures/conformed_dimension/malformed_entry/` -- two variants: (a)
  a `status:` value that is neither `conformed` nor `distinct`; (b) a
  `stars:` entry naming a table id whose `source-map.yaml` cannot be
  found/parsed -- used to assert the FR-010 malformed-entry ERROR naming the
  offending entry. _Satisfies: FR-010 (malformed case)._
- [ ] **T029** `[US2]` Extend `tests/unit/test_rule_hr1.py` with RED tests
  over T024-T028 asserting exact ERROR/no-Finding outcomes and message
  content (dimension name + every carrying star for the collision case; the
  offending entry name for the malformed case); confirm FAIL against the
  Phase 3 implementation (US1 code has no undeclared/missing/malformed
  branches yet). _Satisfies: US2 Independent Test._

### Implementation for User Story 2

- [ ] **T030** `[US2]` In `rule_hr1.py`: implement the missing/unparseable
  manifest check -- when `docs/quality/conformed-dimension-map.yaml` is
  absent from `ctx.tracked_files`, or fails to parse, AND 2+ stars exist
  (per T017's `_discover_stars`), return a single
  `Finding(HR1, ERROR, ...)` naming the manifest path; when 0 or 1 star
  exists, this check MUST NOT fire (defer to Phase 5 / FR-007, but implement
  the 2+-star gate here so US2's own fixtures pass in isolation). Depends on
  T017, T020. _Satisfies: FR-010 (missing case), US3 boundary._
- [ ] **T031** `[US2]` In `rule_hr1.py`: implement malformed-entry detection
  -- a `status` value not exactly `conformed`/`distinct`, or a `stars:`
  entry naming a table id not resolvable in `_discover_stars`'s parse
  results (missing/unparseable `source-map.yaml`) -- each emits
  `Finding(HR1, ERROR, ...)` naming the offending map entry; an entry with a
  bad status is NOT treated as a valid ruling for the collision-grouping
  step below (T032). Depends on T017, T020. _Satisfies: FR-010 (malformed
  case)._
- [ ] **T032** `[US2]` In `rule_hr1.py`: implement cross-star name-collision
  grouping -- group all discovered `GoldDimension`s by `name` across all
  stars; for each name-group with 2+ entries: if undeclared (no valid map
  entry) -> `Finding(HR1, ERROR, ...)` naming the dimension and every
  carrying star (FR-006); if declared `distinct` -> no ERROR regardless of
  shape (FR-008), route to the moot-`distinct` WARNING check (Phase 5); if
  declared `conformed` -> route to US1's T021 comparison. A name in exactly
  one star produces no Finding. Depends on T018, T031. _Satisfies: FR-006,
  FR-008, US2 all three Acceptance Scenarios._
- [ ] **T033** `[US2]` Run the extended `tests/unit/test_rule_hr1.py`
  (T029) against T030-T032 and confirm GREEN, including the
  mutation-verify direction (remove the `distinct` entry and confirm the
  undeclared ERROR reappears). _Satisfies: US2 Independent Test, SC-003._

**Checkpoint**: HR1 now fails closed on an undeclared cross-star collision,
a missing/malformed manifest, and a malformed entry, while a `distinct`
declaration legitimately clears divergence. US1 and US2 together are the
integrity floor (spec.md: "co-equal with US1").

---

## Phase 5: User Story 3 - Do not fire spuriously below the multi-fact trigger (Priority: P2)

**Goal**: With zero or exactly one star, HR1 is a no-op regardless of the
map's contents (including a missing map). Adding a second star that shares a
dimension name engages the US1/US2 checks.

**Independent Test**: fixture repo with zero stars, then one star -> no
Finding either way; add a second star sharing a dimension name -> US2's
undeclared ERROR now fires.

### Tests for User Story 3

- [ ] **T034** `[P]` `[US3]` Fixture
  `tests/fixtures/conformed_dimension/zero_stars/` -- no `source-map.yaml`
  carries `gold_star.fact` at all (and no manifest, or an arbitrary
  manifest) -- used to assert no Finding. _Satisfies: US3 Acceptance
  Scenario 1, FR-007._
- [ ] **T035** `[P]` `[US3]` Fixture
  `tests/fixtures/conformed_dimension/one_star/` -- exactly one star, and a
  manifest that is EITHER absent OR contains an arbitrary entry -- used to
  assert no Finding regardless of manifest contents. _Satisfies: US3
  Acceptance Scenario 2, FR-007._
- [ ] **T036** `[US3]` Extend `tests/unit/test_rule_hr1.py` with RED tests
  over T034/T035 asserting `len(findings) == 0` in both cases, including
  when the manifest is entirely missing (distinguishing this from FR-010's
  2+-star missing-manifest ERROR); confirm these FAIL if the Phase 4
  missing-manifest check (T030) does not already gate on the 2+-star
  condition. _Satisfies: US3 Independent Test._

### Implementation for User Story 3

- [ ] **T037** `[US3]` In `rule_hr1.py`: add the top-of-function short-circuit
  in `check_hr1` -- if `len(_discover_stars(ctx)) < 2`, return `[]`
  immediately (no manifest read attempted, no collision grouping, no
  missing-manifest check) -- confirms T030's gate is not just conditionally
  silent but that the whole rule body is skipped below the trigger. Depends
  on T017, T030. _Satisfies: FR-007, US3 Acceptance Scenario 1 & 2._
- [ ] **T038** `[US3]` Run the extended `tests/unit/test_rule_hr1.py`
  (T036) and confirm GREEN; then re-run T024's undeclared-collision fixture
  with a second star added (simulating US3 Acceptance Scenario 3) and
  confirm the US2 ERROR now fires once the trigger engages. _Satisfies: US3
  Independent Test, SC-004._

**Checkpoint**: All three user stories are independently functional. HR1
does not fire below the multi-fact trigger and correctly engages once it is
met.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: The remaining edge cases from spec.md (stale/moot WARNING
posture), the SC-005/SC-006 verification tests, and final gate/documentation
sign-off. These are cross-cutting because they touch Findings emitted across
US1/US2's branches rather than adding a new trigger condition.

- [ ] **T039** `[P]` `[POLISH]` Fixture
  `tests/fixtures/conformed_dimension/stale_entry/` -- a map entry naming a
  dimension that now survives in fewer than 2 stars (or names a star that
  parses but no longer carries the dimension, per C5) -- used to assert
  `Severity.WARNING`, never ERROR and never silent. _Satisfies: FR-009, C5,
  Edge Cases "stale map entry"._
- [ ] **T040** `[P]` `[POLISH]` Fixture
  `tests/fixtures/conformed_dimension/moot_distinct/` -- a `distinct` entry
  whose stars have become identical in key+type shape -- used to assert
  `Severity.WARNING` (moot), never auto-promotion. _Satisfies: FR-009, Edge
  Cases "moot distinct declaration"._
- [ ] **T041** `[POLISH]` In `rule_hr1.py`: implement the stale-entry WARNING
  (a declared dimension whose named stars no longer number >= 2 with that
  dimension present, OR a listed star that parses but lacks the dimension)
  and the moot-`distinct` WARNING (a `distinct` pair whose present fields now
  all agree) -- both append to `findings`, neither blocks. Depends on T021,
  T032. _Satisfies: FR-009, C5, data-model.md Finding taxonomy (stale +
  moot rows)._
- [ ] **T042** `[POLISH]` Extend `tests/unit/test_rule_hr1.py` with T039/T040
  RED-then-GREEN tests for both WARNING cases; assert `Severity.WARNING`
  specifically (not ERROR, not silent). _Satisfies: FR-009 verification._
- [ ] **T043** `[P]` `[POLISH]` Add a source-inspection test to
  `tests/unit/test_rule_hr1.py` asserting `rule_hr1.py`'s source contains no
  write/open-for-write against `SPINE-equivalent` map path or any
  `source-map.yaml` path (mirrors SF1's `SC_REL`-write-absence test) --
  and asserting no numeric percentage/ratio/"N of M" formatting appears in
  any emitted message string. _Satisfies: FR-011, FR-012, SC-005 (mechanically
  verified, not just reviewed)._
- [ ] **T044** `[P]` `[POLISH]` Grep `src/retail/rules/rule_hr1.py`,
  `docs/quality/conformed-dimension-map.yaml`, and its authoring comments for
  any C086/pharmacy-specific dim name, grain key, or column name; confirm
  `dim_product`/`dim_store`/`dim_date` (or any name) appears only in
  illustrative comments, never as a required literal in rule logic.
  _Satisfies: FR-013, SC-006._
- [ ] **T045** `[POLISH]` Update `docs/glossary.md`'s `HR` row (T010) and any
  cross-reference in `docs/readiness/gold-ready.md` / the Boundary doc from
  T004 to reflect the FINAL Finding taxonomy (key + type ERROR; grain
  pending; undeclared-collision ERROR; missing/malformed-manifest ERROR;
  stale/moot WARNING) once Phase 3-6 land, so the doc and the code do not
  drift. _Satisfies: consistency with data-model.md Finding taxonomy._
- [ ] **T046** `[POLISH]` Run the full local gate:
  `ruff format --check src/ tests/`, `ruff check src/ tests/`,
  `pytest -m unit -x -q`, then `retail check` and `retail kit-lint` --
  confirm GREEN on the current tree (the empty-but-present manifest from
  T003 satisfies FR-010 since the two committed stars share no dimension
  name today). _Satisfies: SC-001, SC-007, plan.md local-verification
  requirement._
- [ ] **T047** `[POLISH]` Confirm `tests/unit/test_wiring_meta_gate.py` and
  `tests/unit/test_rule_count_claims.py` still pass at count 56 and that
  `all_rules()` (not just `EXPECTED_RULE_IDS`) contains `"HR1"`.
  _Satisfies: SC-007._
- [ ] **T048** `[POLISH]` [OWNER SEAM -- OPEN, do not answer] Record
  Q-APPROVAL-SEAM (FR-016) as still OPEN in the feature's closing state --
  no `approvals[]` shape is added, no `readiness-status.yaml` key is
  touched, and HR1 records no model-level pass anywhere; this task is a
  checklist confirmation, not a resolution. _Satisfies: FR-016 PENDING
  DEFAULT posture, Principle V guard._

**Checkpoint**: Feature complete, gate green, no numeric score anywhere, no
domain-specific name baked into generic artifacts, wiring lockstep intact,
and the one genuinely open governance question (FR-016) is left open rather
than silently decided.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies; T002/T003 require the owner-seam
  authorization (T001, T002) before the manifest scaffold is written.
- **Foundational (Phase 2)**: depends on Setup (the manifest must exist so
  Phase 6's final gate run has something non-empty to read) -- BLOCKS all
  user stories. T006 depends on T005; T007-T009 are parallel edits once T005
  exists; T010 depends on T005 (needs the final rule title); T011 depends on
  T010 (count must match anchor); T012 depends on T006-T011 all landing.
- **User Stories (Phase 3-5)**: all depend on Foundational (Phase 2)
  completion (HR1 must be a registered, importable rule before its body can
  be tested). US1 (Phase 3) has no dependency on US2/US3. US2 (Phase 4)
  reuses US1's `_discover_stars`/`_gold_dimensions`/`_load_map` helpers
  (T017/T018/T020) but adds its own branches -- implement after US1 lands so
  those helpers exist, though the underlying rule logic is a single
  `check_hr1` function, not separable services. US3 (Phase 5) depends on
  US2's T030 (the missing-manifest 2+-star gate) for T037's short-circuit
  to be meaningful.
- **Polish (Phase 6)**: depends on US1 + US2 + US3 all landing (the
  stale/moot WARNING logic in T041 reuses T021's comparison and T032's
  grouping).

### Within Each User Story

- Fixtures before tests-that-use-them; tests written and RED before the
  matching implementation task; implementation before the GREEN re-run task.
- `_discover_stars` / `_gold_dimensions` / `_attribute_silver_type` /
  `_load_map` (T017-T020) are shared read-only helpers built once in Phase 3
  and reused (not reimplemented) by Phase 4/5/6.

### Parallel Opportunities

- T007, T008, T009 (three different wiring-surface files) can run in
  parallel once T005/T006 exist.
- Within Phase 3/4/5/6, all `[P]`-marked fixture-authoring tasks (T013-T015,
  T024-T028, T034-T035, T039-T040, T043-T044) touch different files and can
  run in parallel with each other (not with the shared-helper implementation
  tasks they feed into).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational) -- HR1 registered as a
   no-op, wiring green.
2. Complete Phase 3 (US1) -- declared-conformed key/type divergence fails
   closed; agreement passes silently.
3. **STOP and VALIDATE**: run T023's mutation-verified fixtures independently.
4. This is the MVP: the feature's stated "whole point" (spec.md US1 rationale).

### Incremental Delivery

1. Setup + Foundational -> HR1 registered, no-op, gate green.
2. Add US1 -> MVP -- the declared-conformed divergence gate.
3. Add US2 -> the undeclared-collision + missing/malformed-manifest floor
   (co-equal integrity requirement per spec.md).
4. Add US3 -> confirms no spurious firing below the multi-fact trigger
   (adoptability requirement, P2).
5. Polish -> stale/moot WARNING posture, SC-005/SC-006 mechanical
   verification, final six-surface gate confirmation.

### Requirement Coverage Check (every FR maps to >=1 task)

- FR-001 -> T004
- FR-002 -> T003, T020
- FR-003 -> T001, T005
- FR-004 -> T017, T018, T019
- FR-005 -> T021, T022 (grain deferred), T014/T013 tests
- FR-006 -> T032, T024 tests
- FR-007 -> T030, T037
- FR-008 -> T032, T026 tests
- FR-009 -> T041, T039/T040 tests
- FR-010 -> T030, T031, T027/T028 tests
- FR-011 -> T043
- FR-012 -> T043
- FR-013 -> T003, T044
- FR-014 -> T006-T012
- FR-015 -> T003 (ASCII/UTF-8/no-BOM), applies to every new file this
  feature authors
- FR-016 -> T048 (recorded OPEN, not answered)
