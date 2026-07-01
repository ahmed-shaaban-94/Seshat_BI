---
description: "Task list for feature 061-wiring-meta-gate"
---

# Tasks: 5-Place Wiring Meta-Gate / Registry Lockstep Self-Check

**Input**: Design documents from `specs/061-wiring-meta-gate/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/meta-gate-contract.md

**Tests**: This feature IS a test. TDD applies at the meta level -- each check
is written to fail first against a deliberately-broken planted representation,
then made to pass, then the known-good repo state confirms no false failure.

**Organization**: Grouped by the three user stories from spec.md. The single
deliverable is `tests/unit/test_wiring_meta_gate.py`. No `src/` change, no new
golden file, no new `@register` rule, no new `EXPECTED_RULE_ID`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable (independent helper, no ordering dependency)
- **[Story]**: US1 / US2 / US3 (maps to spec.md user stories)

## Path Conventions

Single project. New file: `tests/unit/test_wiring_meta_gate.py`. Read-only
imports from `src/retail/` and reads of `docs/rules/*.json`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the test module and its shared read-only helpers.

- [ ] T001 Create `tests/unit/test_wiring_meta_gate.py` with the `pytest`
  import, `pytestmark = pytest.mark.unit`, an ASCII-only module docstring stating
  the meta-gate is test-only, stdlib-only, adds no rule/id/golden-file, and cites
  Principles I/VII/VIII/IX.
- [ ] T002 Add a shared helper in the module that returns the deterministic
  live-registry snapshot by clearing the registry and reloading every rules
  submodule via package introspection (reuse the exact technique in
  `tests/unit/test_rules_wiring.py::test_registered_rule_ids_match_expected_set`),
  returning both the id set and the `{id: title}` map.
- [ ] T003 [P] Add a shared helper that resolves the repo root from the installed
  package location and reads a golden JSON file (`docs/rules/rules-manifest.json`,
  `docs/rules/severity-posture.json`) as UTF-8 without BOM via stdlib `json`,
  MAX_PATH-safe, returning parsed content only.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Constants and discovery helpers every check depends on.

- [ ] T004 Add the discovery helper that computes the on-disk rules-submodule set
  via `pkgutil.iter_modules` over the rules package path (excluding the package
  initializer), and reads the package `__all__` attribute and the imported
  submodule attribute set from the imported package object -- all as plain sets.
- [ ] T005 Add the explicit ADR-0007 non-registered-surface exemption constant
  (a frozenset containing exactly the one known L3 verdict-to-finding surface key
  as recorded in `docs/rules/severity-posture.json`), with an ASCII comment
  citing ADR-0007 and stating a new surface must be added deliberately.

---

## Phase 3: User Story 1 -- Un-guarded package-symmetry seam (Priority: P1)

**Goal**: Prove import list == `__all__` == on-disk submodule set; fail closed on
any asymmetry or orphan.

**Independent test**: Diverge a planted representation of the three sets; the
check fails naming the offending symbol; equal sets pass.

- [ ] T006 [US1] Write a failing test that feeds three deliberately-unequal
  planted sets (a name missing from `__all__`) to the C1 comparison helper and
  asserts it raises/fails naming the `__all__` omission (RED).
- [ ] T007 [US1] Implement the C1 comparison helper (pure function over three
  sets) that fails closed with a message naming any symbol present in one set but
  not the others and which list it is missing from; make T006 pass (GREEN).
- [ ] T008 [US1] Add `test_package_symmetry_live` asserting the C1 helper passes
  over the REAL discovered sets (import list, `__all__`, on-disk) from Phase 2 --
  the known-good assertion for US1.
- [ ] T009 [P] [US1] Add `test_orphan_submodule_detected` that plants an on-disk
  name absent from both lists into a copied set and asserts C1 fails naming the
  orphan.

---

## Phase 4: User Story 2 -- Five places in mutual lockstep (Priority: P1)

**Goal**: Prove live registry ids reconcile with the expected-id set, the golden
manifest, and the golden posture record; fail closed naming the disagreeing place.

**Independent test**: Alter a planted copy of each place one at a time; the check
fails naming that place; consistent places pass.

- [ ] T010 [US2] Write a failing test for C2 (id source of truth): remove one id
  from a copied expected-id set and assert the reconciler fails with `missing=`
  naming that id (this is the G6 omission-symmetry class) (RED).
- [ ] T011 [US2] Implement the C2 reconciler comparing the live id set to the
  imported `EXPECTED_RULE_IDS` from `tests/unit/test_rules_wiring.py`, failing
  closed with `missing=`/`unexpected=`; make T010 pass (GREEN).
- [ ] T012 [US2] Add `test_ids_match_expected_live` asserting C2 passes over the
  real live ids vs the real `EXPECTED_RULE_IDS` (known-good).
- [ ] T013 [P] [US2] Write and satisfy C3: `test_manifest_matches_live` compares
  the golden manifest `{id,title}` set to the live `{id,title}` map, failing
  closed naming any added/removed/retitled id and the `manifest` place; include a
  planted-drift RED case.
- [ ] T014 [P] [US2] Write and satisfy C4: `test_posture_covers_live` asserts
  every live id appears in the golden posture `registered` section, failing closed
  naming absent ids and the `posture` place; include a planted-drift RED case.
- [ ] T015 [US2] Add `test_no_duplicate_registration` (C7): assert
  `len(all_rules()) == len(live_ids)` on the deterministic snapshot, failing
  closed naming any duplicated id.
- [ ] T016 [US2] Add `test_registry_not_vacuous` (C6): assert the on-disk
  submodule count and the live rule count are both > 0, failing closed naming
  whichever is zero.

---

## Phase 5: User Story 3 -- Non-registered-surface exemption (Priority: P2)

**Goal**: Honor the ADR-0007 exception without a false failure, but fail closed on
a new, un-exempted non-registered surface.

**Independent test**: Known-good state passes; a planted new non-registered
surface key not on the exemption list fails.

- [ ] T017 [US3] Write a failing test for C5 that plants a new non-registered
  surface key (not on the exemption list) into a copied posture-surface set and
  asserts the exemption check fails naming the un-exempted key (RED).
- [ ] T018 [US3] Implement the C5 exemption check: every non-registered posture
  surface key must be in the exemption constant; make T017 pass (GREEN).
- [ ] T019 [US3] Add `test_adr0007_surface_exempted_live` asserting C5 passes over
  the REAL posture golden surfaces (the one L3 surface is exempted, no rule id
  demanded) -- the known-good assertion for US3.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T020 [P] Add `test_meta_gate_all_green` as an end-to-end known-good sweep
  that runs C1-C7 over the real repo state and asserts a clean pass (SC-003),
  documenting the single-pass lockstep contract.
- [ ] T021 [P] Verify the module is ASCII-only, stdlib-only (no third-party
  import), imports no DB/network/Power BI/subprocess surface, and adds no
  `@register`/`EXPECTED_RULE_ID`; run `ruff` and `pytest -m unit
  tests/unit/test_wiring_meta_gate.py` and confirm green.
- [ ] T022 Run the full existing wiring/snapshot suite
  (`test_rules_wiring.py`, `test_rules_manifest_snapshot.py`,
  `test_severity_posture.py`) to confirm the ADD (not REPLACE) decision held --
  no existing test was modified or removed.

---

## Dependencies

- Phase 1 (T001-T003) -> Phase 2 (T004-T005) -> Phases 3/4/5 -> Phase 6.
- US1 (Phase 3), US2 (Phase 4), US3 (Phase 5) are independently testable once
  Phases 1-2 exist; within each, RED precedes GREEN precedes known-good.
- T020-T022 require all checks implemented.

## Parallel Opportunities

- T003 parallel with T002 (independent helpers).
- Within US1: T009 parallel after T007.
- Within US2: T013 and T014 parallel after T011.
- Polish: T020 and T021 parallel.

## Implementation Strategy

MVP = User Story 1 (the genuinely-new package-symmetry coverage) plus the C2
G6-class check from US2; these alone close the documented blind spot. US2's
manifest/posture cross-checks and US3's exemption guard complete the lockstep.
All work lands in one test module; no source or golden-file change.
