# Tasks: Rule-Count Claim Reconciler (SC2)

**Input**: Design documents from `specs/065-rule-count-reconciler/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/sc2-rule-contract.md, quickstart.md

**Tests**: TDD is REQUESTED (spec User Stories 1-3 are acceptance-scenario-driven;
quickstart pins a RED->GREEN order). Test tasks are included and come first.

**Organization**: Tasks are grouped by the three user stories from spec.md. US1
(a stale count claim fails the gate) is the MVP. All paths are repository-relative.

## Path Conventions

Single project: `src/retail/`, `tests/unit/` at repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the build surface; no new infrastructure is needed.

- [ ] T001 Read `src/retail/rules/status_claims.py` and `tests/unit/test_status_claims.py` to confirm the SC1 shape SC2 mirrors (register decorator, ERROR severity, lazy `import yaml`, fail-loud inputs, `_finding` helper, anchor-presence check, live guard). No file change.
- [ ] T002 Confirm the base rule count: record `N = len(EXPECTED_RULE_IDS)` in `tests/unit/test_rules_wiring.py` and confirm "SC2" is absent, and confirm `docs/rules/rules-manifest.json` has N entries. No file change. (N is read live; do NOT hardcode it -- a hardcoded count is the drift SC2 governs.)

**Checkpoint**: Build surface understood; baseline rule count = N.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None beyond the existing rule contract. `src/retail/core.py`
(Finding/Severity/RuleContext), `src/retail/registry.py` (`@register`,
`all_rules()`), and `src/retail/runner.py` (`tracked_files`) are already shipped and
reused UNCHANGED. The authoritative count source `docs/rules/rules-manifest.json`
already exists and is golden-tested.

(No foundational tasks -- the rule contract, registry, context, and count source
already exist.)

**Checkpoint**: Foundation is the existing core; user-story work can begin.

---

## Phase 3: User Story 1 - Catch a stale rule-count claim (Priority: P1) MVP

**Goal**: SC2 reports an ERROR when a manifest entry's `claimed-count` differs from
the authoritative count (anchor present), and zero findings when the claimed count
matches. Fail-loud branches and wiring land in US2/US3.

**Independent Test**: Stage a synthetic context with an entry whose anchor is
present and whose `claimed-count` differs from a synthetic count source -> assert
one ERROR naming both integers. Stage the same entry with a matching count ->
assert `[]`.

### Tests (write first -- RED)

- [ ] T003 [P] [US1] In NEW `tests/unit/test_rule_count_claims.py`, add a `_stage(tmp_path, manifest_claims, docs, count_source_len)` helper (mirroring `test_status_claims.py::_stage`) that writes a synthetic `docs/quality/rule-count-claims.yaml`, the named claiming docs (containing their anchor text), and a synthetic `docs/rules/rules-manifest.json` with `count_source_len` list entries, and returns a `RuleContext(repo_root=tmp_path, tracked_files=tuple(...))`. Use only GENERIC synthetic paths/anchors (`docs/x.md`, anchor "Currently 7 rules", count source of length 7).
- [ ] T004 [P] [US1] In `tests/unit/test_rule_count_claims.py`, add `test_stale_count_fails` (claimed-count != source length, anchor present -> 1 ERROR; message names the claim id, the doc, the claimed integer, and the authoritative count).
- [ ] T005 [P] [US1] In `tests/unit/test_rule_count_claims.py`, add `test_accurate_count_yields_no_findings` (claimed-count == source length, anchor present -> `[]`).

### Implementation (make GREEN)

- [ ] T006 [US1] Create NEW `src/retail/rules/rule_count_claims.py`: module docstring (names SC1 as the sibling; states stdlib-only / read-only / fail-loud / categorical-only / manifest-only / live-state-only, and that the count comes from the committed rule-count JSON via stdlib `json`, never from importing the rules package); constants `_MANIFEST = "docs/quality/rule-count-claims.yaml"` and `_COUNT_SOURCE = "docs/rules/rules-manifest.json"`; an `_finding(message, locator)` helper emitting `Finding(rule_id="SC2", severity=Severity.ERROR, ...)`.
- [ ] T007 [US1] In `rule_count_claims.py`, implement `@register("SC2", "Prose rule-count claims reconcile with the authoritative count")` on `check_rule_count_claims(ctx) -> Iterable[Finding]`: manifest-in-tracked_files guard (fail loud), lazy `import yaml` + `safe_load`, `{claims:[...]}` shape guard, count-source guard (tracked + stdlib `json` parse -> `authoritative_count = len(parsed)`, else ERROR), then per entry the mismatch comparison (claimed != authoritative -> ERROR naming both; equal -> no finding). Fail-loud field/doc/count/anchor branches are added in US2. Return accumulated findings.

**Checkpoint**: US1 tests pass (RED->GREEN). SC2 detects the stale-count defect.

---

## Phase 4: User Story 2 - Fail loud on a moved anchor or malformed entry (Priority: P1)

**Goal**: SC2 emits an ERROR (never `[]`) for: an absent anchor; a malformed/missing
`claimed-count` (non-integer / negative / missing); a missing required field; and an
untracked claiming `doc`. Honest entries still reconcile clean.

**Independent Test**: Stage each bad-entry case; assert each yields an ERROR
describing the cause and is NOT a vacuous `[]`.

### Tests (write first -- RED)

- [ ] T008 [P] [US2] In `tests/unit/test_rule_count_claims.py`, add `test_absent_anchor_fails_loud` (anchor NOT in doc text -> 1 ERROR stating stale/misplaced).
- [ ] T009 [P] [US2] In `tests/unit/test_rule_count_claims.py`, add `test_malformed_count_fails` covering missing `claimed-count`, a non-integer value, and a negative value (each -> 1 ERROR stating the count is malformed).
- [ ] T010 [P] [US2] In `tests/unit/test_rule_count_claims.py`, add `test_untracked_doc_fails` (`doc` not tracked -> 1 ERROR) and `test_missing_field_fails` (entry missing `anchor` -> 1 ERROR).

### Implementation (make GREEN)

- [ ] T011 [US2] In `rule_count_claims.py` `check_rule_count_claims`, complete the ordered contract (steps 4a-4d) BEFORE the comparison: entry-not-mapping -> ERROR; missing required field (`id`/`doc`/`anchor`/`claimed-count`) -> ERROR; `doc` not tracked -> ERROR; `claimed-count` not a non-negative integer -> ERROR (malformed); `anchor` not a substring of `(ctx.repo_root / doc).read_text("utf-8")` -> ERROR (stale/misplaced). Only a well-formed, tracked-doc, present-anchor, valid-integer entry reaches the comparison (step 4e). Never fall through to a vacuous empty result on bad input.

**Checkpoint**: US2 tests pass. Every per-entry fault is covered; no bad entry
produces a vacuous green.

---

## Phase 5: User Story 3 - Fail loud on a bad manifest / count source; rule is discoverable and counted (Priority: P2)

**Goal**: SC2 fails loud on a missing/malformed manifest and an unreadable
authoritative count source; and SC2 self-registers on import and is counted in the
wiring drift guard (N -> N+1) and the two golden snapshots.

**Independent Test**: (a) stage each bad manifest / count-source case -> ERROR; (b)
run the wiring test -> registered set contains "SC2" and totals N+1.

### Tests (write first -- RED)

- [ ] T012 [P] [US3] In `tests/unit/test_rule_count_claims.py`, add `test_missing_manifest_fails_loud` (manifest untracked -> 1 ERROR), `test_malformed_yaml_fails_loud` (manifest not valid YAML -> 1 ERROR), and `test_wrong_shape_fails_loud` (no `claims` list -> 1 ERROR).
- [ ] T013 [P] [US3] In `tests/unit/test_rule_count_claims.py`, add `test_missing_count_source_fails_loud` (count source untracked -> 1 ERROR) and `test_unparseable_count_source_fails_loud` (count source not valid JSON / not a list -> 1 ERROR). Confirm the T007 count-source guard covers both.

### Implementation + wiring tests

- [ ] T014 [US3] Edit `src/retail/rules/__init__.py`: add `rule_count_claims` to the side-effecting import tuple and to `__all__` (keep grouping/ordering consistent with the file).
- [ ] T015 [US3] Edit `tests/unit/test_rules_wiring.py`: add `"SC2"` to `EXPECTED_RULE_IDS` with a short comment (rule-count reconciler: prose count matches the authoritative count). This moves the keyed count N -> N+1.
- [ ] T016 [US3] Run `pytest -m unit tests/unit/test_rules_wiring.py` and confirm `test_registered_rule_ids_match_expected_set` passes (SC2 present, count N+1, no drift).

**Checkpoint**: US3 passes. SC2 is wired, discoverable, drift-guarded, and fails
loud on every unreadable input.

---

## Phase 6: Seed the manifest, fix the seeded prose, regen goldens, and harden

**Purpose**: Author the real manifest with the one confirmed generic seed defect
(the glossary stale count), correct that glossary prose to the POST-SC2 count in the
SAME change so SC2 ships GREEN, regenerate the two golden snapshots, then add the
live guard, the roadmap ledger row, and the full gate run.

- [ ] T017 Determine the POST-SC2 count: after T014/T015, it is N+1 (the base count plus SC2). Read it live from `len(EXPECTED_RULE_IDS)` / the regenerated `docs/rules/rules-manifest.json` -- do NOT hardcode.
- [ ] T018 Correct the stale rule-count wording in `docs/glossary.md` (the "Currently N rules in ... families" line near the static-check-rules catalog) so its integer equals the POST-SC2 count (N+1). Choose the exact corrected sentence wording; this becomes the T019 `anchor`. (Correct ONLY the rule-count integer; do not alter the family-count claim -- family counts are out of scope for SC2.)
- [ ] T019 Author NEW `docs/quality/rule-count-claims.yaml` with the single confirmed seed entry: `id` (stable handle, e.g. `glossary-rule-count`), `doc: docs/glossary.md`, `anchor` (the EXACT corrected sentence from T018), `claimed-count: <N+1>`. Include a header comment explaining the manifest contract and the live-state-only scope (mirroring `status-claims.yaml`'s header). Generic governance paths only; no pharmacy/C086 token; no dated snapshot listed.
- [ ] T020 Regenerate the two golden snapshots in this change: run `retail manifest` (writes `docs/rules/rules-manifest.json` now containing SC2, length N+1) and `retail severity-posture` (writes `docs/rules/severity-posture.json` now containing SC2). Commit both regenerated files.
- [ ] T021 [P] In `tests/unit/test_rule_count_claims.py`, add `test_live_manifest_reconciles_against_real_repo` mirroring `test_status_claims.py`'s live guard: `@pytest.mark.skipif(shutil.which("git") is None)`, shell `git ls-files`, build a real `RuleContext` over the repo root, run `check_rule_count_claims`, assert `[]`. This is the production guard proving the shipped manifest + corrected glossary reconcile clean (all three integers equal N+1).
- [ ] T022 Add a ledger row to `docs/roadmap/roadmap.md` in the idea-bank execution sequence section recording SC2 shipped and the rule count N -> N+1, and update the "Effect on the static gate" running tally sentence to include SC2. Generic wording; no C086 specifics; off-spine (no F-number/stage self-assigned).
- [ ] T023 Run the full gate set and confirm green: `ruff check .`, `pytest -m unit`, `retail check` (exit 0, N+1 rules), `retail semantic-check`.
- [ ] T024 Final generic-leak sweep: grep `rule_count_claims.py`, `test_rule_count_claims.py`, and `rule-count-claims.yaml` for any pharmacy/C086/billing/segment/PII token; confirm all ids, paths, anchors, and messages are abstract/generic.

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** -> **Phase 3 (US1)** is the critical path. US1 delivers the MVP
  (the stale-count detection, the named seed-defect shape).
- **Phase 4 (US2)** depends on T006/T007 existing (it completes the same handler:
  adds the per-entry fail-loud branches), so US2 implementation (T011) follows US1
  implementation (T007).
- **Phase 5 (US3)** manifest/count-source fail-loud tests (T012/T013) exercise the
  T007 guards; the wiring edits (T014/T015) can be done any time after T006 creates
  the module, but T016 needs the rule fully implemented; do it after US1+US2.
- **Phase 6**: T018/T019 must land together with T014/T015 (seed + prose fix +
  wiring) so the gate is GREEN at the POST-SC2 count; T020 (regen) needs the wiring;
  T021 (live guard) needs the full rule + seeded-and-fixed manifest + regenerated
  count source; T022-T024 last.

### Parallel opportunities

- T004-T005 (US1 tests) are `[P]` -- independent cases in the one new test file.
- T008-T010 (US2 tests) are `[P]`; T012-T013 (US3 tests) are `[P]`.
- T014 and T015 touch different files and can proceed in parallel once the module exists.
- T021 is `[P]` (a distinct test case) but depends on the rule + seeded manifest + regen.

## Implementation Strategy

MVP = US1 (stale-count detection + accurate-count clean). US2 hardens against
vacuous green with the per-entry fail-loud branches. US3 fails loud on a bad
manifest / unreadable count source and wires + counts the rule. Phase 6 seeds the
real manifest, corrects the seeded stale glossary count to the POST-SC2 count in the
same change, regenerates the two golden snapshots, adds the live guard + roadmap
ledger row, and runs the full gate. Because the seed prose is fixed to N+1 in the
same change, the live guard and `retail check` are expected GREEN at exit (N+1
rules).

## Reserved for human ratification (do NOT self-decide)

Per spec ## Clarifications, build on these documented advisor defaults unless a
human ruling changes them: (Q1) the count source is the committed rule-count JSON
read with stdlib `json`, never a rules-package import; (Q2) the seed glossary prose
is corrected to the POST-SC2 count in the same change so the gate ships GREEN; (Q3)
only the integer rule count is reconciled (family counts out of scope for v1); (Q4)
the manifest-completeness drift gap is accepted for this first step (no coverage
rule); (Q5) SC2 is recorded OUTSIDE the seven-stage readiness spine as an idea-bank
integrity rule (sibling SC1/DF1). None is a Principle-V ruling; all are reversible.
The roadmap readiness STAGE and the roadmap F-number/spec-number remain a human's to
assign at ratify time -- this workflow records them for the human and does not
self-assign them.
