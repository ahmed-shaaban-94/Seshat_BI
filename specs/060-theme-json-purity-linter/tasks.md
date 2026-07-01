# Tasks: Theme JSON Purity Linter

**Input**: Design documents from `specs/060-theme-json-purity-linter/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/rule-contract.md, quickstart.md

**Tests**: Included -- the spec's user stories are defined in test terms and the
project is a governance-rule codebase where TDD (RED->GREEN) is the norm.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 / US2 / US3, or SETUP / WIRING / POLISH

## GATING NOTE (Principle V -- read before Phase WIRING)

The exact literal forbidden-key vocabulary and any REQUIRED-key assertion are an
OPEN human ruling (spec ## Clarifications). Phases SETUP/US1/US2/US3 build the
generic seam and can proceed on the working assumption (MUST-NOT-only scan,
vocabulary derived from the generic contract categories). Phase WIRING FREEZES the
golden records and MUST NOT be committed until the human ruling on the literal
vocabulary is recorded; wiring an unratified literal list would encode a Principle-V
judgment the workflow is forbidden to make.

---

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 [SETUP] Confirm the live registry state on this branch: enumerate the
  actually-registered rule ids (import `retail.rules`; call `registry.all_rules()`)
  and reconcile against `EXPECTED_RULE_IDS` in
  `tests/unit/test_rules_wiring.py`. Record the TRUE set and confirm the intended
  fresh, non-colliding, design/theme-namespaced rule id is free. (Do not trust a
  count claim; reconcile against the real set.)
- [ ] T002 [SETUP] Create the fixture directory under the test-fixture exemption
  path (mirroring the pbir fixtures location convention) for the theme-purity
  fixtures. ASCII, UTF-8 no BOM.

---

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T003 [SETUP] Author the generic forbidden-key vocabulary seam in a single
  place (a named module-level constant) DERIVED from the MUST-NOT categories in
  `docs/powerbi/theme-json.md` (DAX/measures/calculated*/metric-definition/
  relationship/source-mapping/sentiment-threshold-or-rule/data-validation), with a
  code comment citing the contract and marking the literal membership as pending the
  human ruling. No tenant/example/brand literal (Principle VII).

---

## Phase 3: User Story 1 -- Contaminated theme file fails (Priority: P1)

**Goal**: A forbidden business-logic key in a committed theme file is an ERROR
finding with a precise locator, and the check exits non-zero.

- [ ] T004 [P] [US1] Add fixture: a theme file with exactly one forbidden key
  (under the exemption path).
- [ ] T005 [P] [US1] Add fixture: a theme file with a forbidden key nested inside a
  deeper object.
- [ ] T006 [P] [US1] Add fixture: a theme file with two distinct forbidden keys.
- [ ] T007 [US1] Write failing unit tests in `tests/unit/test_design_theme.py` for
  contract rows C1 (one ERROR + locator + non-zero), C2 (nested locator path),
  C3 (two findings, no masking). RED.
- [ ] T008 [US1] Implement `src/retail/rules/design_theme.py`: a
  `@register`-decorated function that discovers theme files generically, parses
  each with the pbir.py pattern, recursively walks KEY names against the forbidden
  vocabulary, and emits one `Severity.ERROR` Finding per occurrence with a
  `file#/pointer` locator. Make C1-C3 GREEN.

**Checkpoint**: US1 is an independently demonstrable MVP -- a contaminated fixture
fails the rule with a precise finding.

---

## Phase 4: User Story 2 -- Clean allowed file passes (Priority: P1)

**Goal**: Legitimate styling-only files (including a sentiment COLOR) produce zero
findings; the current committed starter theme stays green.

- [ ] T009 [P] [US2] Add fixture: an allowed-only theme file (palette/fonts/visual
  defaults/filter-pane/page defaults).
- [ ] T010 [P] [US2] Add fixture: a theme file with a sentiment COLOR but no
  threshold/rule.
- [ ] T011 [P] [US2] Add fixture: a theme file whose VALUE string equals a
  forbidden word (not a key).
- [ ] T012 [US2] Write failing unit tests for contract rows C4 (allowed-only zero),
  C5 (sentiment color allowed), C6 (current committed starter theme zero findings),
  C7 (value not scanned). RED where behavior is missing.
- [ ] T013 [US2] Refine `design_theme.py` so the scan inspects KEY names /
  structural positions only (not free-text values) and treats the allowed
  vocabulary as never-flagged. Make C4-C7 GREEN. Verify against the real
  `themes/tower-retail.theme.json` (C6).

**Checkpoint**: US1 + US2 together define the correctness boundary (no false
positives, no false negatives on the fixtures + live corpus).

---

## Phase 5: User Story 3 -- Generic and self-registering (Priority: P2)

**Goal**: The rule scans any committed theme file generically, handles edge cases,
and is verifiably present in governance records.

- [ ] T014 [P] [US3] Add fixture: a malformed (invalid JSON) theme file.
- [ ] T015 [P] [US3] Add fixture: a second, differently-named theme file to prove
  generic discovery (distinct from the starter).
- [ ] T016 [US3] Write failing unit tests for contract rows C8 (malformed ->
  finding, no crash, not silently passed), C9 (no theme files -> zero, no error),
  C10 (fixture-exemption path excluded from live scan), C11 (two files both
  scanned, no code change). RED.
- [ ] T017 [US3] Implement malformed-JSON handling (emit a finding, do not raise;
  FR-009) and confirm generic discovery + fixture exemption. Make C8-C11 GREEN.

**Checkpoint**: All contract rows C1-C11 GREEN; the rule is generic and robust.

---

## Phase 6: Wiring (Golden-Record Freeze -- GATED on human ruling)

**BLOCKED until the Principle-V human ruling on the literal forbidden-key
vocabulary (and required-key scope) is recorded in spec ## Clarifications.**

- [ ] T018 [WIRING] Add `design_theme` to the side-effecting import tuple AND
  `__all__` in `src/retail/rules/__init__.py`.
- [ ] T019 [WIRING] Add the fresh rule id to `EXPECTED_RULE_IDS` in
  `tests/unit/test_rules_wiring.py`.
- [ ] T020 [WIRING] Regenerate `docs/rules/rules-manifest.json` via the existing
  `retail manifest` command (adds the new id + title).
- [ ] T021 [WIRING] Regenerate `docs/rules/severity-posture.json` (the new id's
  OBSERVED severity; do not hand-declare a governed table -- ratified 044).

---

## Phase 7: Polish & Gate

- [ ] T022 [POLISH] Run `pytest -m unit` -- all C1-C11 tests plus the wiring test
  pass.
- [ ] T023 [POLISH] Run `retail check` (full governance gate) -- green; the new
  rule produces zero findings on the live corpus and the wiring/golden-record tests
  pass.
- [ ] T024 [POLISH] Confirm all authored files are ASCII / UTF-8-no-BOM / short
  paths (Principle IX) and no tenant/example literal appears in the rule
  (Principle VII).

---

## Dependencies & Ordering

- Setup (T001-T002) before everything.
- Foundational vocabulary seam (T003) before US1 implementation (T008).
- Within each story: fixtures + failing tests before implementation (TDD).
- US1 (P1) and US2 (P1) are the MVP; US3 (P2) hardens.
- Phase 6 (WIRING) is GATED on the human ruling and comes after all rule behavior
  is GREEN.
- Phase 7 (gate) is last.

## Parallel opportunities

- Fixture-authoring tasks marked [P] (T004-T006, T009-T011, T014-T015) touch
  distinct files and can be authored together.
- The two P1 stories can be built in sequence or interleaved; both must be GREEN
  before wiring.

## MVP scope

US1 + US2 (both P1) = the minimum viable rule: catches contamination, never flags
legitimate styling. US3 + wiring make it durable and governed.
