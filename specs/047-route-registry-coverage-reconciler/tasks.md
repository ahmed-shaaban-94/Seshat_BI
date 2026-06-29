# Tasks: Route-Registry Coverage Reconciler (A3)

**Input**: Design documents from `specs/047-route-registry-coverage-reconciler/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/a3-rule-contract.md, quickstart.md

**Tests**: TDD is REQUESTED (spec User Stories 1-2 are acceptance-scenario-driven;
quickstart pins a RED->GREEN order). Test tasks are included and come first.

**Organization**: Tasks are grouped by the three user stories from spec.md. US1
(drift fails the gate) is the MVP. All paths are repository-relative.

## Path Conventions

Single project: `src/retail/`, `tests/unit/` at repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the build surface; no new infrastructure is needed.

- [ ] T001 Read `src/retail/rules/routes.py` and `tests/unit/test_routes.py` to confirm the A1 shape A3 will mirror (register decorator, ERROR severity, lazy `import yaml`, fail-loud inputs, live guard). No file change.
- [ ] T002 Confirm `tests/unit/test_rules_wiring.py` `EXPECTED_RULE_IDS` holds 33 ids today and that "A3" is absent. No file change.

**Checkpoint**: Build surface understood; baseline rule count = 33.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None beyond the existing rule contract. `src/retail/core.py`
(Finding/Severity/RuleContext) and `src/retail/registry.py` (`@register`,
`all_rules()`) are already shipped and reused UNCHANGED.

(No foundational tasks -- the rule contract and registry already exist.)

**Checkpoint**: Foundation is the existing core; user-story work can begin.

---

## Phase 3: User Story 1 - Drift between map and manifest fails the gate (Priority: P1) MVP

**Goal**: A3 reports an ERROR naming the exact id when the map id set and the
manifest id set differ in either direction, and zero findings when they match.

**Independent Test**: Stage a synthetic context where map ids and manifest ids
differ by one id (each direction); assert exactly one ERROR naming that id and the
direction. Stage equal sets; assert `[]`.

### Tests (write first -- RED)

- [ ] T003 [P] [US1] In NEW `tests/unit/test_routes_coverage.py`, add a `_stage` helper (mirroring `test_routes.py::_stage`) that writes a synthetic `docs/knowledge-map.md` (a "Route by task" table) and a synthetic `docs/routing/routes.yaml` under `tmp_path` and returns a `RuleContext` tracking both. Use only generic ids ("1", "2", "99").
- [ ] T004 [P] [US1] In `tests/unit/test_routes_coverage.py`, add `test_bijection_holds_yields_no_findings` (equal id sets -> `[]`).
- [ ] T005 [P] [US1] In `tests/unit/test_routes_coverage.py`, add `test_map_id_missing_from_manifest_fails` (map has an id the manifest lacks -> 1 ERROR naming the id; message states map-has / manifest-lacks).
- [ ] T006 [P] [US1] In `tests/unit/test_routes_coverage.py`, add `test_manifest_id_missing_from_map_fails` (manifest has an id the map lacks -> 1 ERROR naming the id; message states manifest-has / map-lacks).
- [ ] T007 [P] [US1] In `tests/unit/test_routes_coverage.py`, add `test_sublettered_ids_compare_exactly` (an id like "12a" present on both sides matches; "12a" vs "12" does NOT match) so the extractor does not normalize sub-letters.

### Implementation (make GREEN)

- [ ] T008 [US1] Create NEW `src/retail/rules/routes_coverage.py`: module docstring (names A1 as the sibling, states stdlib-only / read-only / fail-loud); constants for `_MANIFEST = "docs/routing/routes.yaml"` and `_MAP = "docs/knowledge-map.md"`; an `_finding(message, locator)` helper emitting `Finding(rule_id="A3", severity=Severity.ERROR, ...)`.
- [ ] T009 [US1] In `routes_coverage.py`, implement a hand-rolled stdlib extractor `_map_ids(text) -> set[str] | None` that locates the `## Route by task` section, reads its pipe-table data rows (skipping the header + `|---|` separator), takes each row's first-cell leading token with a trailing period stripped (preserving sub-letters), and stops at the next `## ` heading. Returns `None` if the section is not locatable.
- [ ] T010 [US1] In `routes_coverage.py`, implement `_manifest_ids(ctx) -> set[str] | list[Finding]` reusing A1's lazy `import yaml` + `safe_load` + `{routes:[...]}` shape guard, collecting each route `id` as a str.
- [ ] T011 [US1] In `routes_coverage.py`, implement `@register("A3", "Knowledge-map route ids and the routing manifest ids are in bijection")` on `check_route_coverage(ctx) -> Iterable[Finding]`: read both id sets, compute `map_only` and `manifest_only`, emit one ERROR per drifting id (generic message naming the id + direction + responsible locator), return `[]` when both empty.

**Checkpoint**: US1 tests pass (RED->GREEN). A3 detects drift in both directions.

---

## Phase 4: User Story 2 - Malformed or missing inputs fail loud (Priority: P1)

**Goal**: A3 emits an ERROR (never `[]`) when either source is missing, untracked,
unparseable, wrong-shape, or the map's "Route by task" table cannot be located.

**Independent Test**: Stage contexts with (a) no manifest tracked, (b) a non-routes
manifest, (c) malformed YAML, (d) a map whose "Route by task" table is absent; assert
each yields an ERROR describing the unreadable input.

### Tests (write first -- RED)

- [ ] T012 [P] [US2] In `tests/unit/test_routes_coverage.py`, add `test_missing_manifest_fails_loud` (manifest untracked -> ERROR naming the manifest).
- [ ] T013 [P] [US2] In `tests/unit/test_routes_coverage.py`, add `test_manifest_not_routes_mapping_fails` and `test_malformed_yaml_fails_loud` (-> ERROR each).
- [ ] T014 [P] [US2] In `tests/unit/test_routes_coverage.py`, add `test_map_table_not_locatable_fails_loud` (map text has no "Route by task" section -> ERROR naming the map source; assert it is NOT a vacuous `[]`).

### Implementation (make GREEN)

- [ ] T015 [US2] In `routes_coverage.py` `check_route_coverage`, add the fail-loud branches BEFORE the set comparison: manifest missing/untracked -> ERROR; manifest parse/shape errors -> ERROR (propagate `_manifest_ids` findings); map file untracked or `_map_ids` returns `None` -> ERROR naming the map source. Never fall through to an empty-set comparison.

**Checkpoint**: US2 tests pass. No unreadable input can produce a vacuous green.

---

## Phase 5: User Story 3 - The rule is discoverable and counted in the gate (Priority: P2)

**Goal**: A3 self-registers on import and is counted in the wiring drift guard
(33 -> 34); the wiring test would catch A3's removal.

**Independent Test**: Run the wiring test; assert the registered set contains "A3"
and totals 34.

### Implementation + wiring tests

- [ ] T016 [US3] Edit `src/retail/rules/__init__.py`: add `routes_coverage` to the side-effecting import tuple and to `__all__` (keep alphabetical/grouped ordering consistent with the file).
- [ ] T017 [US3] Edit `tests/unit/test_rules_wiring.py`: add `"A3"` to `EXPECTED_RULE_IDS` with a short comment (route registry coverage: map ids == manifest ids bijection). This moves the keyed count 33 -> 34.
- [ ] T018 [US3] Run `pytest -m unit tests/unit/test_rules_wiring.py` and confirm `test_registered_rule_ids_match_expected_set` passes (A3 present, count 34, no drift).

**Checkpoint**: US3 passes. A3 is wired, discoverable, and drift-guarded.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T019 [US1] In `tests/unit/test_routes_coverage.py`, add `test_live_map_and_manifest_in_bijection_against_real_repo` mirroring `test_routes.py::test_live_manifest_resolves_against_real_repo`: `@pytest.mark.skipif(shutil.which("git") is None)`, shell `git ls-files`, build a real `RuleContext` over the repo root, run `check_route_coverage`, assert `[]`. This is the production guard proving the shipped map+manifest are in bijection.
- [ ] T020 Add a ledger row to `docs/roadmap/roadmap.md` in the idea-bank execution sequence section recording A3 shipped and the rule count 33 -> 34. Generic wording; no C086 specifics.
- [ ] T021 Run the full gate set and confirm green: `ruff check .`, `pytest -m unit`, `retail check` (exit 0, 34 rules), `retail semantic-check`.
- [ ] T022 Final generic-leak sweep: grep `routes_coverage.py` and `test_routes_coverage.py` for any pharmacy/C086/billing/segment/PII token; confirm all ids and messages are abstract.

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** -> **Phase 3 (US1)** is the critical path. US1 delivers the MVP.
- **Phase 4 (US2)** depends on T008/T011 existing (it adds fail-loud branches to the
  same handler), so US2 implementation (T015) follows US1 implementation.
- **Phase 5 (US3)** wiring (T016/T017) can be done any time after T008 creates the
  module, but T018 needs the module importable; recommended after US1+US2 so the
  rule is fully implemented when first counted.
- **Phase 6 (Polish)**: T019 needs the full rule (post US1+US2); T020-T022 are last.

### Parallel opportunities

- T003-T007 (US1 tests) are `[P]` -- all in the one new test file but independent
  cases; write together.
- T012-T014 (US2 tests) are `[P]`.
- T016 and T017 touch different files and can proceed in parallel once the module
  exists.

## Implementation Strategy

MVP = US1 (drift detection both directions + clean-on-equal). US2 hardens against
vacuous green; US3 wires and counts the rule; Polish adds the live guard, the
roadmap ledger row, and the full gate run. The bijection holds on main, so the
live guard and `retail check` are expected GREEN at exit.

## Reserved for human ratification (do NOT self-decide)

Per spec ## Clarifications, build on these reversible advisor defaults unless a
human ruling changes them: severity = ERROR both directions; bijection scope =
"Route by task" table only (no COMPASS); roadmap stage = none (routing-integrity
rule like A1/B1). If the human flips the severity posture, only the `_finding`
severity and the affected test assertions change.
