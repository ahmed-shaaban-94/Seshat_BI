# Tasks: Stale-Marker Sweep / Status-Claim Reconciler (SC1)

**Input**: Design documents from `specs/050-stale-marker-sweep/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/sc1-rule-contract.md, quickstart.md

**Tests**: TDD is REQUESTED (spec User Stories 1-3 are acceptance-scenario-driven;
quickstart pins a RED->GREEN order). Test tasks are included and come first.

**Organization**: Tasks are grouped by the three user stories from spec.md. US1
(stale planned marker fails the gate) is the MVP. All paths are repository-relative.

## Path Conventions

Single project: `src/retail/`, `tests/unit/` at repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the build surface; no new infrastructure is needed.

- [ ] T001 Read `src/retail/rules/routes.py` and `tests/unit/test_routes.py` to confirm the A1 shape SC1 mirrors (register decorator, ERROR severity, lazy `import yaml`, fail-loud inputs, `_finding` helper, live guard). No file change.
- [ ] T002 Confirm `tests/unit/test_rules_wiring.py` `EXPECTED_RULE_IDS` holds 35 ids today and that "SC1" is absent. No file change.

**Checkpoint**: Build surface understood; baseline rule count = 35.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None beyond the existing rule contract. `src/retail/core.py`
(Finding/Severity/RuleContext) and `src/retail/registry.py` (`@register`,
`all_rules()`) and `src/retail/runner.py` (`tracked_files`) are already shipped and
reused UNCHANGED.

(No foundational tasks -- the rule contract, registry, and context already exist.)

**Checkpoint**: Foundation is the existing core; user-story work can begin.

---

## Phase 3: User Story 1 - Catch a stale "planned" claim about a shipped artifact (Priority: P1) MVP

**Goal**: SC1 reports an ERROR when a manifest entry marks an artifact `planned`
but the artifact is a tracked file, and zero findings when a `planned` claim's
artifact is honestly absent. (Symmetric `built` cases land in US2.)

**Independent Test**: Stage a synthetic context with a `planned` entry whose anchor
is present and whose artifact IS tracked -> assert one ERROR naming that entry.
Stage the same entry with the artifact ABSENT -> assert `[]`.

### Tests (write first -- RED)

- [ ] T003 [P] [US1] In NEW `tests/unit/test_status_claims.py`, add a `_stage(tmp_path, manifest_claims, docs, artifacts)` helper (mirroring `test_routes.py::_stage`) that writes a synthetic `docs/quality/status-claims.yaml`, the named claiming docs (containing their anchor text), and the named artifact files under `tmp_path`, and returns a `RuleContext(repo_root=tmp_path, tracked_files=tuple(...))`. Use only GENERIC synthetic paths/anchors (`docs/x.md`, anchor "feature X is planned", artifact `src/x.py`).
- [ ] T004 [P] [US1] In `tests/unit/test_status_claims.py`, add `test_stale_planned_marker_fails` (planned + artifact tracked + anchor present -> 1 ERROR; message names the claim id + artifact + states the artifact now exists).
- [ ] T005 [P] [US1] In `tests/unit/test_status_claims.py`, add `test_honest_planned_yields_no_findings` (planned + artifact NOT tracked + anchor present -> `[]`).

### Implementation (make GREEN)

- [ ] T006 [US1] Create NEW `src/retail/rules/status_claims.py`: module docstring (names A1 as the sibling; states stdlib-only / read-only / fail-loud / categorical-only); constants `_MANIFEST = "docs/quality/status-claims.yaml"` and `_VALID_STATUS = frozenset({"built", "planned"})`; an `_finding(message, locator)` helper emitting `Finding(rule_id="SC1", severity=Severity.ERROR, ...)`.
- [ ] T007 [US1] In `status_claims.py`, implement `@register("SC1", "Prose status claims reconcile with tracked-file evidence")` on `check_status_claims(ctx) -> Iterable[Finding]`: manifest-in-tracked_files guard (fail loud), lazy `import yaml` + `safe_load`, `{claims:[...]}` shape guard, then per entry compute the `planned` branches from the truth table (planned + resolved -> ERROR stale marker; planned + not resolved -> no finding). Anchor/doc/built branches are added in US2/US3 phases. Return accumulated findings.

**Checkpoint**: US1 tests pass (RED->GREEN). SC1 detects the stale-planned defect.

---

## Phase 4: User Story 2 - Catch a false "built" claim, and fail loud on bad input (Priority: P1)

**Goal**: SC1 emits an ERROR (never `[]`) for: a `built` claim whose artifact is
missing; a missing/untracked manifest; malformed YAML; a wrong-shape manifest; an
entry with an invalid/missing field; an untracked claiming `doc`; and an anchor
absent from the claiming doc. Honest `built` (artifact tracked) -> no finding.

**Independent Test**: Stage each bad-input/contradiction case; assert each yields an
ERROR describing the cause and is NOT a vacuous `[]`. Stage honest built; assert `[]`.

### Tests (write first -- RED)

- [ ] T008 [P] [US2] In `tests/unit/test_status_claims.py`, add `test_honest_built_yields_no_findings` (built + artifact tracked + anchor present -> `[]`) and `test_false_built_fails` (built + artifact NOT tracked + anchor present -> 1 ERROR).
- [ ] T009 [P] [US2] In `tests/unit/test_status_claims.py`, add `test_missing_manifest_fails_loud` (manifest untracked -> 1 ERROR) and `test_malformed_yaml_fails_loud` (manifest not valid YAML -> 1 ERROR) and `test_wrong_shape_fails_loud` (no `claims` list -> 1 ERROR).
- [ ] T010 [P] [US2] In `tests/unit/test_status_claims.py`, add `test_invalid_status_fails` (`claimed-status: shipped` -> 1 ERROR), `test_missing_field_fails` (entry missing `claimed-artifact` -> 1 ERROR), `test_untracked_doc_fails` (`doc` not tracked -> 1 ERROR), and `test_absent_anchor_fails_loud` (anchor NOT in doc text -> 1 ERROR stating stale/misplaced).

### Implementation (make GREEN)

- [ ] T011 [US2] In `status_claims.py` `check_status_claims`, complete the ordered contract: BEFORE the truth-table resolution add the fail-loud branches -- entry-not-mapping -> ERROR; missing required field (`id`/`doc`/`anchor`/`claimed-artifact`/`claimed-status`) -> ERROR; `claimed-status` not in `_VALID_STATUS` -> ERROR; `doc` not tracked -> ERROR; `anchor` not a substring of `(ctx.repo_root / doc).read_text("utf-8")` -> ERROR (stale/misplaced). Add the `built` resolution branch (built + not resolved -> ERROR false-built; built + resolved -> no finding). Never fall through to a vacuous empty result on bad input.

**Checkpoint**: US2 tests pass. Both contradiction directions + every fail-loud
input are covered. No unreadable input produces a vacuous green.

---

## Phase 5: User Story 3 - The rule is discoverable and counted in the gate (Priority: P2)

**Goal**: SC1 self-registers on import and is counted in the wiring drift guard
(35 -> 36); the wiring test would catch SC1's removal.

**Independent Test**: Run the wiring test; assert the registered set contains "SC1"
and totals 36.

### Implementation + wiring tests

- [ ] T012 [US3] Edit `src/retail/rules/__init__.py`: add `status_claims` to the side-effecting import tuple and to `__all__` (keep the grouping/ordering consistent with the file).
- [ ] T013 [US3] Edit `tests/unit/test_rules_wiring.py`: add `"SC1"` to `EXPECTED_RULE_IDS` with a short comment (status-claim reconciler: prose claim matches tracked-file evidence). This moves the keyed count 35 -> 36.
- [ ] T014 [US3] Run `pytest -m unit tests/unit/test_rules_wiring.py` and confirm `test_registered_rule_ids_match_expected_set` passes (SC1 present, count 36, no drift).

**Checkpoint**: US3 passes. SC1 is wired, discoverable, and drift-guarded.

---

## Phase 6: Seed the manifest, fix the seeded prose, and harden

**Purpose**: Author the real manifest with the one confirmed generic seed defect,
correct that defect's stale prose in the SAME change so SC1 ships GREEN, then add
the live guard, the roadmap ledger row, and the full gate run.

- [ ] T015 [US1] Author NEW `docs/quality/status-claims.yaml` with the single confirmed seed entry: the capability-state governance doc's claim about the shipped Net Sales end-to-end trace. Fields: `id` (stable handle), `doc: docs/quality/post-idea-bank-capability-state.md`, `anchor` (the exact corrected wording -- see T016), `claimed-artifact: docs/demo/net-sales-end-to-end-readiness-trace.md`, `claimed-status: built`. Generic repo-infrastructure paths only; no pharmacy/C086 token. Include a header comment explaining the manifest contract (mirroring `routes.yaml`'s header).
- [ ] T016 Correct the stale wording in `docs/quality/post-idea-bank-capability-state.md` (the "(planned)" reference to the shipped Net Sales end-to-end trace, around the "Recommended next proof" section) so it no longer calls the shipped, tracked trace planned. Choose the corrected wording, set the T015 `anchor` to that exact text, and `claimed-status: built` so the seed entry resolves clean (trace is tracked -> built honest). Net effect: the manifest ends GREEN.
- [ ] T017 [P] In `tests/unit/test_status_claims.py`, add `test_live_manifest_resolves_against_real_repo` mirroring `test_routes.py::test_live_manifest_resolves_against_real_repo`: `@pytest.mark.skipif(shutil.which("git") is None)`, shell `git ls-files`, build a real `RuleContext` over the repo root, run `check_status_claims`, assert `[]`. This is the production guard proving the shipped manifest + corrected prose reconcile clean.
- [ ] T018 Add a ledger row to `docs/roadmap/roadmap.md` in the idea-bank execution sequence section recording SC1 shipped and the rule count 35 -> 36. Generic wording; no C086 specifics.
- [ ] T019 Run the full gate set and confirm green: `ruff check .`, `pytest -m unit`, `retail check` (exit 0, 36 rules), `retail semantic-check`.
- [ ] T020 Final generic-leak sweep: grep `status_claims.py`, `test_status_claims.py`, and `status-claims.yaml` for any pharmacy/C086/billing/segment/PII token; confirm all ids, paths, anchors, and messages are abstract/generic.

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** -> **Phase 3 (US1)** is the critical path. US1 delivers the MVP
  (the stale-planned-marker detection, the named seed-defect shape).
- **Phase 4 (US2)** depends on T006/T007 existing (it completes the same handler:
  adds the fail-loud branches and the `built` resolution), so US2 implementation
  (T011) follows US1 implementation (T007).
- **Phase 5 (US3)** wiring (T012/T013) can be done any time after T006 creates the
  module, but T014 needs the rule fully implemented; do it after US1+US2.
- **Phase 6**: T015/T016 must land together (seed + prose fix) so the gate is GREEN;
  T017 (live guard) needs the full rule + seeded-and-fixed manifest; T018-T020 last.

### Parallel opportunities

- T004-T005 (US1 tests) are `[P]` -- independent cases in the one new test file.
- T008-T010 (US2 tests) are `[P]`.
- T012 and T013 touch different files and can proceed in parallel once the module exists.
- T017 is `[P]` (a distinct test case) but depends on the rule + seeded manifest.

## Implementation Strategy

MVP = US1 (stale-planned detection + honest-planned clean). US2 hardens against
vacuous green and adds the symmetric false-built case + every fail-loud input. US3
wires and counts the rule. Phase 6 seeds the real manifest, corrects the seeded
stale prose in the same change, adds the live guard + roadmap ledger row, and runs
the full gate. Because the seed prose is fixed in the same change, the live guard
and `retail check` are expected GREEN at exit (36 rules).

## Reserved for human ratification (do NOT self-decide)

Per spec ## Clarifications, build on these reversible advisor defaults unless a
human ruling changes them: (Q1) the seed prose is corrected in the same change so
the gate ships GREEN; (Q2) the manifest-completeness drift gap is accepted for this
first step (no coverage rule, mirroring A1-before-A3); (Q3) SC1 is recorded OUTSIDE
the seven-stage readiness spine as an idea-bank integrity rule (sibling A1/A3/B1).
None is a Principle-V ruling; all are reversible with localized changes.
