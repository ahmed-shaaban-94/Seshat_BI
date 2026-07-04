---
description: "Task list for 090-source-freshness-gate (Source Freshness / Staleness Declaration and Static Presence Check)"
---

# Tasks: Source Freshness / Staleness Declaration and Static Presence Check

**Input**: Design documents from `specs/090-source-freshness-gate/`
(spec.md, plan.md, research.md, data-model.md, quickstart.md)

**Tests**: Included -- plan.md's Testing section requires mutation-verified
fixtures (`tests/fixtures/<rule>/` good/bad corpora, SF1/HR1 discipline); this
is a fail-closed governance rule, not optional coverage.

**Status carried from plan.md**: DRAFT. This task list authors the design; it
does not itself constitute ratification. Q-FR014-SCOPE (FR-014) stays OPEN
for a named-human owner ruling -- no task below answers it, and no task makes
outright ABSENCE of `meta.freshness` an ERROR (that would silently pre-empt
the open ruling; see plan.md "Landing precondition" and research.md).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3), or
  `SETUP`/`FOUND`/`POLISH` for cross-cutting phases
- Every task names an exact repo-relative file path

## Path Conventions

Single project (`src/retail/`, `tests/`, `docs/`, `templates/`) at repository
root, per plan.md "Structure Decision". No new project/service/top-level
directory; no new manifest file (unlike HR1/087 -- HR4 adds no cross-table
YAML, only the `meta.freshness` key on the existing `source-map.yaml` schema).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the reserved allocation and the presence-gated landing
precondition, then author the SCHEMA edit before any rule code is written
(hard rule #8: docs/templates/checklists before automation).

- [ ] **T001** `[SETUP]` Confirm the reserved static-rule id is **HR4** and
  the reserved schema key is `meta.freshness` (`expected_cadence` +
  `max_staleness`), nested under the existing `meta:` block of
  `templates/source-map.yaml` and every `mappings/<table>/source-map.yaml`
  -- collision-avoidance allocation (spec.md Overview, plan.md Summary). No
  other top-level or `meta`-level key is touched; no new artifact file is
  introduced (unlike HR1's `conformed-dimension-map.yaml`). _Satisfies:
  FR-001, FR-003._
- [ ] **T002** `[SETUP]` Confirm the presence-gated landing precondition
  (research.md "Landing precondition"; plan.md Summary): HR4 will fail
  closed ONLY on a `meta.freshness` block that IS PRESENT but
  missing/blank/unparseable on `expected_cadence` or `max_staleness`; it
  MUST NOT fire on outright ABSENCE of the block on a filled map (that is
  Q-FR014-SCOPE, FR-014, an OPEN owner ruling -- Principle V). Confirm
  neither committed filled map
  (`mappings/retail_store_sales/source-map.yaml`,
  `mappings/demo_sample_orders/source-map.yaml`) carries a `freshness` key
  today, so this design lands GREEN on the current tree (SC-001/SC-003 hold
  trivially). Plain confirmation, not an owner ruling -- clears the way for
  T003. _Satisfies: plan.md Landing precondition; Principle V guard;
  SC-001, SC-003._
- [ ] **T003** `[SETUP]` Confirm the token grammar (Clarification C1/C2,
  resolved in plan.md Technical Context + data-model.md "Token grammar") is
  the one to implement: `expected_cadence` a closed enum
  (`daily|weekly|monthly|quarterly|annual` with `annually`/`yearly` as
  synonyms of `annual`, plus `one_time` with `static` as a synonym);
  `max_staleness` the regex
  `^\s*\d+\s*(hour|day|week|month|quarter|year)s?\s*$` (case-insensitive) OR
  the literal sentinel `n/a` (case-insensitive); both trimmed of surrounding
  whitespace before matching. No C086/`retail_store_sales` value is used in
  the grammar (FR-011). Plain confirmation (grammar is a mechanical
  vocabulary choice per C1, not a business-SLA judgment) -- no file edit.
  _Satisfies: FR-002, FR-011, C1, C2._
- [ ] **T004** `[SETUP]` Edit `templates/source-map.yaml`: add a
  `freshness:` block as a sibling of the existing `meta.grain` /
  `meta.primary_key` / `meta.reviewed_by` / `meta.reviewed_on` keys, with
  generic placeholder values and an authoring comment citing the recognized
  vocabulary (e.g.
  `expected_cadence: "<cadence: daily|weekly|monthly|quarterly|annual|one_time>"`,
  `max_staleness: "<duration: e.g. 2 days | 1 week -- or 'n/a' if one_time>"`)
  and a one-line note that this key is OPTIONAL today pending an owner
  ruling (FR-014) and is never auto-filled by automation (FR-002, FR-008).
  No other key in the template is added, renamed, or removed. ASCII, UTF-8
  without BOM (Principle IX). Depends on T001, T003. _Satisfies: FR-001,
  FR-002, FR-007 (illustrative duration is a declared input, not a score),
  FR-013, Clarification C3 (this is schema documentation the rule will
  never evaluate)._
- [ ] **T005** `[SETUP]` Confirm (checklist task, no file edit) that
  `mappings/retail_store_sales/source-map.yaml` and
  `mappings/demo_sample_orders/source-map.yaml` remain UNCHANGED and
  READ-ONLY by this feature -- no real `expected_cadence`/`max_staleness`
  value is fabricated on either table's behalf (hard rule #9, FR-002); the
  agent does not decide FR-014's scope by populating them. _Satisfies:
  FR-002, FR-008, FR-014 guard; plan.md Project Structure "UNCHANGED,
  READ-ONLY."_

**Checkpoint**: the schema documentation exists (generic, ASCII, no
domain-specific value), the grammar is fixed, and the presence-gated shape
is confirmed as the design to implement, before any rule code is written.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Reserve HR4 across every wiring surface and produce a stub
module, mirroring the SF1/AP1/HR1 six-surface wiring discipline (FR-012).
**No user-story Finding logic is implemented yet in this phase** -- only the
scaffold that makes `@register("HR4", ...)` compile and be discoverable.

**CRITICAL**: No user story (Phase 3+) can be implemented until this phase
is complete, because HR4 must exist as a registered (even if empty-bodied)
rule before its Finding-emitting logic can be tested via `retail check`.

- [ ] **T006** `[FOUND]` Create the stub rule module
  `src/retail/rules/rule_hr4.py` with `RULE_ID = "HR4"`, the module
  docstring (mirrors `rule_sf1.py`'s shape: what HR4 does, what it never
  does -- static-only, presence-gated, no live comparison, no numeric score
  -- and a LAZY `import yaml` note), and a
  `@register(RULE_ID, "source freshness declaration presence/well-formedness gate")`-decorated
  `check_hr4(ctx: RuleContext) -> Iterable[Finding]` that returns `[]` (stub
  body; Phase 3+ fills it in). Depends on T004. _Satisfies: FR-003, FR-013._
- [ ] **T007** `[FOUND]` Edit `src/retail/rules/__init__.py`: add `rule_hr4`
  to the side-effecting import tuple (alphabetical slot, after `rule_count_claims`,
  before `rule_sf1`) AND to `__all__` in the same commit -- the ONLY
  discovery step (no autodiscovery). Depends on T006. _Satisfies: FR-012
  (wiring surface 1)._
- [ ] **T008** `[P]` `[FOUND]` Edit `tests/unit/test_rules_wiring.py`: add
  `"HR4"` to `EXPECTED_RULE_IDS`. Depends on T006. _Satisfies: FR-012
  (wiring surface 2)._
- [ ] **T009** `[P]` `[FOUND]` Edit `docs/rules/rules-manifest.json`: add
  `{"id": "HR4", "title": "source freshness declaration presence/well-formedness gate"}`
  in id order (the file is id-sorted; `HR4` sorts after the `G*` rules and
  before the `P*`/`S*` block -- re-verify the exact insertion point against
  the live file at implement time rather than trusting this description).
  Depends on T006. _Satisfies: FR-012 (wiring surface 3)._
- [ ] **T010** `[P]` `[FOUND]` Edit `docs/rules/severity-posture.json`: add
  `"HR4": ["error"]` under the `"registered"` section -- ERROR-only, no
  WARNING case (data-model.md Finding taxonomy: HR4 has no WARNING branch,
  unlike SF1/HR1, because there is no cross-file manifest that can go
  stale). Depends on T006. _Satisfies: FR-012 (wiring surface 4)._
- [ ] **T011** `[FOUND]` Edit `docs/glossary.md`: add an `HR4` row to the
  rules table (new family `HR`, if not already present from a
  concurrently-landing sibling feature -- re-verify at implement time
  before appending a duplicate family token) describing the presence-gated
  well-formedness check in the same style as the `SF` row; bump the
  "Currently 55 rules in 21 families" anchor to **"Currently 56 rules in 22
  families"** (append `HR` to the family list) -- re-verify the live count
  against `docs/rules/rules-manifest.json` at implement time rather than
  trusting this number, exactly as 087's own plan cautions for itself (a
  sibling in-flight feature, HR1/087, may land first and already claim
  count 56 and family `HR`, in which case HR4 becomes 57 without adding a
  duplicate family). Depends on T009. _Satisfies: FR-012 (wiring surface
  5)._
- [ ] **T012** `[FOUND]` Edit `docs/quality/rule-count-claims.yaml`: bump
  `claimed-count` for the `glossary-rule-count` entry to match T011's final
  anchor number exactly, and confirm the `anchor:` text stays
  byte-identical to the glossary sentence from T011 (SC2 reconciles the
  two). Depends on T011 (must match its final wording/number, not run in
  parallel with it). _Satisfies: FR-012 (wiring surface 6), SC-006._
- [ ] **T013** `[FOUND]` Run
  `pytest -m unit tests/unit/test_wiring_meta_gate.py tests/unit/test_rules_wiring.py tests/unit/test_rule_count_claims.py`
  and confirm all green with the HR4 stub registered at the current live
  count. Depends on T007, T008, T009, T010, T011, T012. _Satisfies: SC-006
  (wiring + rule-count lockstep stays green)._

**Checkpoint**: `HR4` is a real, registered, discoverable rule (currently a
no-op) and every meta-gate lockstep is green. User story implementation can
now begin.

---

## Phase 3: User Story 1 - A data owner declares an expected cadence and max staleness (Priority: P1)

**Goal**: A `meta.freshness` block with both sub-keys well-formed can be
added to a table's `source-map.yaml` without disturbing any other mapping-gate
requirement (grain, PK, reviewed_by) and without HR4 raising any Finding for
it.

**Independent Test**: Add a `meta.freshness` block with both sub-keys filled
to a fixture `source-map.yaml`; confirm no other key is touched and HR4
emits zero Findings.

### Tests for User Story 1

> Write these tests FIRST; they exercise the Phase 2 stub (trivially GREEN,
> since the stub returns `[]`) and then continue to pass unchanged once
> Phase 4 (US2) implements real logic -- this is the "well-formed input never
> regresses" regression guard for the malformed-input work that follows.

- [ ] **T014** `[P]` `[US1]` Fixture
  `tests/fixtures/source_freshness/well_formed/source-map.yaml` -- a minimal
  `source-map.yaml` stand-in carrying the existing `meta.grain` /
  `meta.primary_key` / `meta.reviewed_by` keys UNCHANGED plus a
  `meta.freshness` block with both `expected_cadence` and `max_staleness`
  well-formed (e.g. `weekly` / `"3 days"`, illustrative only per Principle
  VII). _Satisfies: US1 Acceptance Scenario 1 & 2, SC-001._
- [ ] **T015** `[P]` `[US1]` Fixture
  `tests/fixtures/source_freshness/one_time_valid/source-map.yaml` -- the
  reserved `one_time` (or `static`) cadence paired with `max_staleness:
  "n/a"` (Clarification C2) -- used to assert this pairing is well-formed at
  the grammar level. _Satisfies: data-model.md Token grammar sentinel row,
  quickstart.md step 4._
- [ ] **T016** `[US1]` `tests/unit/test_rule_hr4.py`: write the tests
  against T014/T015 fixtures asserting `check_hr4` returns `[]` for both,
  and a separate assertion (by reading the fixture YAML directly, not via
  HR4) that the fixture's `meta.grain`/`meta.primary_key`/`meta.reviewed_by`
  keys are present and unchanged alongside the new `freshness` key --
  confirming FR-001's "no other key touched" claim is fixture-verifiable,
  not just asserted in prose. Depends on T006 (stub must exist to import).
  _Satisfies: US1 Independent Test._

### Implementation for User Story 1

- [ ] **T017** `[US1]` In `src/retail/rules/rule_hr4.py`: implement
  `_iter_filled_maps(ctx)` -- from `ctx.tracked_files`, match paths against
  `mappings/<name>/source-map.yaml` (a generic path pattern, no hardcoded
  table name, per FR-011), EXCLUDING `templates/source-map.yaml` explicitly
  by path (Clarification C3) and excluding any path where `is_test_path`
  is true (fixture exemption); parse each candidate as YAML (lazy `import
  yaml`) and yield `(table_id, parsed)` only for files that parse and carry
  a top-level `meta:` mapping -- anything else (missing file, unparseable
  YAML, no `meta:` mapping) is silently excluded from HR4's scope entirely
  (FR-005; a different rule's concern, not HR4's). Depends on T006.
  _Satisfies: FR-005, FR-011, data-model.md "Is-in-scope-to-parse test"._
- [ ] **T018** `[US1]` In `rule_hr4.py`: implement `_cadence_ok(value)` and
  `_staleness_ok(value)` per T003's confirmed grammar (closed enum with
  `annually`/`yearly` synonyms of `annual` and `static` synonym of
  `one_time`; the duration regex or the `n/a` sentinel), both
  case-insensitive and both trimming surrounding whitespace before
  matching, both returning a plain boolean (no side effect, no score).
  Depends on T006. _Satisfies: FR-002, C1, C2, data-model.md Token
  grammar._
- [ ] **T019** `[US1]` In `check_hr4`: for each table from T017, when
  `meta.freshness` is present as a mapping and BOTH `_cadence_ok` and
  `_staleness_ok` return true on its two sub-keys, emit no Finding for that
  table. Depends on T017, T018. _Satisfies: US1 Acceptance Scenario 1 & 2,
  SC-001._
- [ ] **T020** `[US1]` Run `tests/unit/test_rule_hr4.py` (T016) against the
  Phase 3 implementation and confirm GREEN for the well-formed and
  one_time/n/a fixtures. _Satisfies: US1 Independent Test._

**Checkpoint**: A well-formed `meta.freshness` block (including the
one_time/n/a sentinel pairing) validates cleanly with zero Findings, and no
other `meta` key is disturbed. This is the MVP slice -- independently
testable.

---

## Phase 4: User Story 2 - A missing or malformed freshness declaration is surfaced as a blocker (Priority: P1)

**Goal**: When a filled `source-map.yaml`'s `meta.freshness` block IS
PRESENT but `expected_cadence` and/or `max_staleness` is missing, blank, or
unparseable, HR4 fails closed with an ERROR Finding naming the table and the
specific offending field(s). Outright ABSENCE of the whole block on a filled
map produces NO Finding (presence-gated; Q-FR014-SCOPE stays open, T002).

**Independent Test**: Run `check_hr4` against a fixture with the `freshness`
block entirely absent -> zero Findings (presence-gated negative). Run it
against a fixture with the block present but a sub-key blank/unparseable ->
exactly one ERROR naming the table and the sub-key; fixing the value clears
the Finding.

### Tests for User Story 2

> Write these tests FIRST; they FAIL against the Phase 3 implementation
> (T019 has no malformed/absent branches yet) -- RED -- then PASS after this
> phase's implementation lands -- GREEN (SF1/HR1 mutation discipline).

- [ ] **T021** `[P]` `[US2]` Fixture
  `tests/fixtures/source_freshness/absent_block/source-map.yaml` -- a
  filled map with the existing `meta` keys but NO `freshness` key at all --
  used to assert the presence-gated NO-Finding path (the negative fixture
  plan.md's Project Structure names explicitly). _Satisfies: FR-014 (OPEN
  scope, presence-gated default), Edge Cases (retroactive-map bullet),
  SC-003 boundary reasoning applied to a filled (not pre-Stage-2) map._
- [ ] **T022** `[P]` `[US2]` Fixture
  `tests/fixtures/source_freshness/blank_cadence/source-map.yaml` -- block
  present, `expected_cadence` blank/whitespace-only (or the key present
  with an empty string), `max_staleness` well-formed. _Satisfies: US2
  Acceptance Scenario 2 (symmetric case), FR-004(b)._
- [ ] **T023** `[P]` `[US2]` Fixture
  `tests/fixtures/source_freshness/missing_staleness/source-map.yaml` --
  block present, `expected_cadence` well-formed, `max_staleness` key absent
  entirely. _Satisfies: US2 Acceptance Scenario 2, FR-004(b)._
- [ ] **T024** `[P]` `[US2]` Fixture
  `tests/fixtures/source_freshness/unparseable_cadence/source-map.yaml` --
  block present, `expected_cadence` a non-empty string not in the closed
  enum (e.g. an illustrative typo/free-text phrase, never a C086 value),
  `max_staleness` well-formed. _Satisfies: US2 Acceptance Scenario 1 is
  NOT this (that scenario is absence, T021) -- this covers FR-004(b) and
  Edge Cases "a cadence string the rule cannot classify"._
- [ ] **T025** `[P]` `[US2]` Fixture
  `tests/fixtures/source_freshness/unparseable_staleness/source-map.yaml`
  -- block present, `expected_cadence` well-formed, `max_staleness` a
  non-empty string matching neither the duration regex nor `n/a` (e.g. a
  bare number with no unit, or free text). _Satisfies: FR-004(b), Edge
  Cases "unparseable form."_
- [ ] **T026** `[P]` `[US2]` Fixture
  `tests/fixtures/source_freshness/block_not_mapping/source-map.yaml` --
  `meta.freshness` present but is a bare string/list, not a YAML mapping.
  _Satisfies: FR-004(b) "malformed," data-model.md Finding taxonomy
  "Block present but not a mapping" row._
- [ ] **T027** `[P]` `[US2]` Fixture
  `tests/fixtures/source_freshness/pre_stage2_no_map/` -- a scenario
  directory with NO `mappings/<table>/source-map.yaml` at all (Stage 1,
  pre-mapping) -- used to assert HR4 never fires ahead of Stage 2 even
  though the scenario directory exists. _Satisfies: FR-005, US2 Acceptance
  Scenario boundary, SC-003._
- [ ] **T028** `[US2]` `tests/unit/test_rule_hr4.py`: extend with RED tests
  over T021-T027 asserting: T021 -> `len(findings) == 0`; T022/T023 ->
  exactly one `Severity.ERROR` Finding naming the table and the specific
  missing/blank sub-key (`expected_cadence` for T022, `max_staleness` for
  T023); T024/T025 -> exactly one ERROR naming the table, the offending
  sub-key, and the offending raw value; T026 -> exactly one ERROR with the
  whole-block locator (`meta.freshness`, not a sub-key); T027 -> `len(findings)
  == 0`. Confirm all FAIL against the Phase 3 implementation before
  proceeding. Depends on T016 (extends the same test module). _Satisfies:
  US2 Independent Test._

### Implementation for User Story 2

- [ ] **T029** `[US2]` In `check_hr4`: for each table from T017 where
  `meta.freshness` key is present, branch on its type -- if not a mapping,
  emit one `Finding(HR4, ERROR, ...)` with locator
  `mappings/<table>/source-map.yaml:meta.freshness` naming the table and
  stating the block is not a mapping; STOP further per-field checks for
  that table (nothing to inspect). Depends on T017, T018, T019. _Satisfies:
  FR-004(b) "malformed," data-model.md "Block present but not a mapping"
  row._
- [ ] **T030** `[US2]` In `check_hr4`: when `meta.freshness` is a mapping,
  evaluate `expected_cadence` via `_cadence_ok` -- if the key is absent,
  `None`, or blank/whitespace-only after trim, or non-empty but
  `_cadence_ok` returns false, emit one `Finding(HR4, ERROR, ...)` with
  locator `mappings/<table>/source-map.yaml:meta.freshness.expected_cadence`
  naming the table, the field, and the offending raw value (when present).
  Depends on T018, T029. _Satisfies: FR-004(b), US2 Acceptance Scenario 1's
  malformed-value half, Edge Cases "unparseable form."_
- [ ] **T031** `[US2]` In `check_hr4`: symmetrically evaluate
  `max_staleness` via `_staleness_ok` with the same
  absent/blank/unparseable -> ERROR rule, locator
  `mappings/<table>/source-map.yaml:meta.freshness.max_staleness`. Depends
  on T018, T029. _Satisfies: FR-004(b), US2 Acceptance Scenario 2._
- [ ] **T032** `[US2]` In `check_hr4`: confirm (by construction, not a new
  branch) that a table whose `meta.freshness` key is entirely ABSENT
  produces no call into T029/T030/T031 at all -- the presence-gated
  short-circuit lives at the top of the per-table loop from T019/T029 ("key
  absent -> continue, no Finding"). Add a code comment at that short-circuit
  citing Q-FR014-SCOPE (FR-014) so the deferred ruling is visibly authored,
  not silently absent (Principle VIII/V discipline, mirrors HR1's
  `[PENDING SCHEMA PREREQUISITE]` comment convention). Depends on T029.
  _Satisfies: FR-014 (presence-gated default), plan.md "Landing
  precondition," Principle V guard._
- [ ] **T033** `[US2]` Run the extended `tests/unit/test_rule_hr4.py`
  (T028) against T029-T032 and confirm GREEN, including the
  mutation-verify direction (take a passing fixture, blank one sub-key, and
  reconfirm the ERROR appears; then restore it and reconfirm the ERROR
  clears). _Satisfies: US2 Independent Test, SC-002._

**Checkpoint**: HR4 now fails closed on every present-but-malformed
`meta.freshness` shape (missing/blank/unparseable sub-key, non-mapping
block) while remaining silent on outright absence and on pre-Stage-2 tables.
US1 and US2 together deliver the full P1 scope.

---

## Phase 5: User Story 3 - The live arrival-time comparison is marked pending, never fabricated (Priority: P2)

**Goal**: Confirm by construction and by test that HR4 computes, queries, or
asserts nothing about ACTUAL arrival time, elapsed staleness, or a live
pass/fail verdict -- and that this feature introduces no live-reporting
surface of its own (Clarification C4); the `[PENDING LIVE FRESHNESS CHECK]`
marker is recorded as a future contract only.

**Independent Test**: Static source-inspection test confirms `rule_hr4.py`
opens no database/network handle and contains no `MAX(` /
elapsed-time/score computation; running `check_hr4` requires no live DSN and
no `db` extra.

### Tests for User Story 3

- [ ] **T034** `[US3]` `tests/unit/test_rule_hr4.py`: add a source-inspection
  test asserting `rule_hr4.py`'s source contains no database/connection API
  call (e.g. no `psycopg`, `sqlalchemy`, `connect(`, `MAX(` SQL fragment),
  no `import socket`/`requests`/`urllib` network call, no numeric
  percentage/ratio/"N of M" formatting in any emitted message string, AND
  (mirroring 087's T043 / SF1's `SC_REL`-write-absence test pattern
  mechanically, not just by comment) no write/open-for-write call (e.g. no
  `open(..., "w")`, `write_text(`, `.write(`) against any
  `source-map.yaml`, `readiness-status.yaml`, or `approvals` path anywhere
  in `rule_hr4.py`'s source. Depends on T006 (stub must exist to
  import/inspect). _Satisfies: US3 Independent Test, FR-006, FR-007,
  FR-008 (mechanically verified write-absence), SC-004, SC-005._
- [ ] **T035** `[US3]` `tests/unit/test_rule_hr4.py`: add a test that
  `check_hr4` runs to completion and returns without requiring any live
  fixture/DSN/environment variable -- i.e. calling it against T014/T021's
  fixtures needs nothing beyond the fixture files on disk. Depends on T016,
  T028. _Satisfies: SC-004._

### Implementation for User Story 3

- [ ] **T036** `[US3]` Confirm (by construction, no new code path) that
  `rule_hr4.py` never emits the `[PENDING LIVE FRESHNESS CHECK]` string --
  HR4 never reports on live state at all, so the marker has no call site
  in this feature (Clarification C4). Add a docstring/comment in
  `rule_hr4.py` naming `[PENDING LIVE FRESHNESS CHECK]` as the CONTRACT a
  future live surface (most likely `retail validate`, spec 082) must honor
  when it is eventually built, so the seam is visibly recorded rather than
  silently absent. Depends on T006. _Satisfies: FR-006, Clarification C4._
- [ ] **T037** `[US3]` Run T034/T035 and confirm GREEN. _Satisfies: US3
  Independent Test, SC-004, SC-005._

**Checkpoint**: HR4 is verifiably 100% static -- no live surface, no
fabricated freshness verdict, no numeric score -- and the deferred live-check
contract is named without being implemented or simulated.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Genericity verification (no C086 value leaked into a generic
artifact), the final six-surface gate confirmation, the FR-coverage check,
and recording the one genuinely open governance question (FR-014) as still
open rather than silently decided.

- [ ] **T038** `[P]` `[POLISH]` Grep `src/retail/rules/rule_hr4.py`,
  `templates/source-map.yaml`'s new `freshness` block, and
  `tests/fixtures/source_freshness/**` authoring comments for any
  C086/`retail_store_sales`/pharmacy-specific cadence value, column name,
  or table name; confirm any such reference appears ONLY as a cited filled
  instance (e.g. in a comment pointing to the worked example), never as a
  required literal in rule logic or the schema template. _Satisfies:
  FR-011, SC-007._
- [ ] **T039** `[P]` `[POLISH]` Grep `docs/readiness/source-drift.md` and
  confirm it is UNEDITED by this feature (no taxonomy/template/key touched)
  -- diff against the pre-feature commit to confirm zero changes.
  _Satisfies: FR-009._
- [ ] **T040** `[P]` `[POLISH]` Confirm no missing-segment / date-spine
  completeness check was added anywhere in `rule_hr4.py` or its fixtures --
  a checklist re-read of the implementation against FR-010, not a new file.
  _Satisfies: FR-010._
- [ ] **T041** `[POLISH]` Run the full local gate:
  `ruff format --check src/ tests/`, `ruff check src/ tests/`,
  `pytest -m unit -x -q`, then `retail check` and `retail kit-lint` --
  confirm GREEN on the current tree (the presence-gated design from T002
  means neither committed filled map produces a Finding). _Satisfies:
  SC-001, SC-003, SC-004, plan.md local-verification requirement._
- [ ] **T042** `[POLISH]` Confirm `tests/unit/test_wiring_meta_gate.py` and
  `tests/unit/test_rule_count_claims.py` still pass at the final live rule
  count and that `registry.all_rules()` (not just `EXPECTED_RULE_IDS`)
  contains `"HR4"`. _Satisfies: SC-006._
- [ ] **T043** `[POLISH]` [OWNER SEAM -- OPEN, do not answer] Record
  Q-FR014-SCOPE (FR-014) as still OPEN in the feature's closing state -- no
  task in this file makes `meta.freshness` mandatory, retroactive, or
  exempted for any table; no `readiness-status.yaml` key or `approvals[]`
  entry is added or touched by HR4; the RECORDED PENDING DEFAULT
  (going-forward-only, existing maps grandfathered, `one_time`/`static`
  token reserved but not mandated) remains a default a named human may
  ratify, not a ruling this task list adopts. Checklist confirmation only,
  no file edit beyond this task's own checkbox. _Satisfies: FR-014 OPEN
  posture, Principle V guard._
- [ ] **T044** `[POLISH]` Confirm the Requirement Coverage Check below is
  accurate against the final landed task numbers (re-map if any task was
  renumbered during implementation). _Satisfies: speckit-analyze
  cross-artifact consistency (every FR maps to >=1 task)._

**Checkpoint**: Feature complete, gate green, no numeric score anywhere, no
domain-specific value baked into a generic artifact, wiring lockstep intact,
and Q-FR014-SCOPE left open rather than silently decided.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies; T004 (the schema edit) depends on
  T001 + T003 (id/allocation and grammar must be confirmed before the
  placeholder text is written) and must land BEFORE any Foundational wiring
  task (hard rule #8: docs/templates before automation) -- T006 depends on
  T004.
- **Foundational (Phase 2)**: depends on Setup -- BLOCKS all user stories.
  T007-T010 are parallel edits once T006 exists; T011 depends on T009
  (needs the manifest entry to exist / count to be re-verified); T012
  depends on T011 (count/anchor must match byte-for-byte); T013 depends on
  T007-T012 all landing.
- **User Stories (Phase 3-5)**: all depend on Foundational (Phase 2)
  completion (HR4 must be a registered, importable rule before its body can
  be tested). US1 (Phase 3) has no dependency on US2/US3. US2 (Phase 4)
  reuses US1's `_iter_filled_maps`/`_cadence_ok`/`_staleness_ok` helpers
  (T017/T018) but adds its own ERROR branches -- implement after US1 lands
  so those helpers exist, though the underlying rule logic is a single
  `check_hr4` function, not separable services. US3 (Phase 5) is
  independent of US1/US2's Finding logic (it inspects source code and
  requires-no-DSN behavior) but depends on the stub existing (T006) and
  benefits from T016/T028's fixtures already being callable (T035).
- **Polish (Phase 6)**: depends on US1 + US2 + US3 all landing.

### Within Each User Story

- Fixtures before tests-that-use-them; tests written and RED (US2) or
  trivially-green-then-reconfirmed (US1, since the stub already returns
  `[]`) before the matching implementation task; implementation before the
  GREEN re-run task.
- `_iter_filled_maps` / `_cadence_ok` / `_staleness_ok` (T017-T018) are
  shared read-only helpers built once in Phase 3 and reused (not
  reimplemented) by Phase 4.

### Parallel Opportunities

- T008, T009, T010 (three different wiring-surface files) can run in
  parallel once T006/T007 exist.
- Within Phase 3/4, all `[P]`-marked fixture-authoring tasks (T014-T015,
  T021-T027) touch different files and can run in parallel with each other
  (not with the shared-helper implementation tasks they feed into).
- T038, T039, T040 (Polish genericity/boundary checks) touch no shared file
  and can run in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational) -- HR4 registered as a
   no-op, wiring green, schema documented.
2. Complete Phase 3 (US1) -- a well-formed `meta.freshness` block (including
   the `one_time`/`n/a` sentinel pairing) validates cleanly.
3. **STOP and VALIDATE**: run T020's fixtures independently.
4. This is the MVP: the feature's declaration half (spec.md US1 rationale
   -- "the foundation the rest of the feature depends on").

### Incremental Delivery

1. Setup + Foundational -> HR4 registered, no-op, gate green, schema
   documented.
2. Add US1 -> the declaration validates; no other mapping-gate key
   disturbed.
3. Add US2 -> the fail-closed enforcement half (co-equal P1 requirement per
   spec.md -- "without it, the declaration in User Story 1 is optional
   prose that nothing checks").
4. Add US3 -> confirms no live surface is touched and no fabricated
   verdict is possible (P2 scope fence).
5. Polish -> genericity verification, final six-surface gate confirmation,
   FR-coverage reconciliation, Q-FR014-SCOPE recorded OPEN.

### Requirement Coverage Check (every FR maps to >=1 task)

- FR-001 -> T004, T016
- FR-002 -> T004, T018, T030, T031
- FR-003 -> T001, T006
- FR-004 -> T029, T030, T031 (T021-T027 fixtures)
- FR-005 -> T017, T027
- FR-006 -> T034, T036
- FR-007 -> T034, T004 (illustrative duration is a declared input, not a
  score)
- FR-008 -> T005, T032, T034 (T034 mechanically verifies write-absence;
  T005/T032 confirm no auto-fill / no self-granted pass)
- FR-009 -> T039
- FR-010 -> T040
- FR-011 -> T017, T018, T038
- FR-012 -> T007-T013
- FR-013 -> T004, T006, T038 (ASCII/UTF-8/no-BOM, short paths)
- FR-014 -> T002, T032, T043 (recorded OPEN, not answered)
