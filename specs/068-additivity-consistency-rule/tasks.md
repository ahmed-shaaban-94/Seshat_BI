---

description: "Task list for the Additivity-Consistency Lineage Rule"
---

# Tasks: Additivity-Consistency Lineage Rule

**Input**: Design documents from `specs/067-additivity-consistency-rule/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test tasks ARE included -- the spec's success criteria (SC-001..SC-005) require
fixture-driven behavior tests and the wiring golden test. TDD order: write the failing test
before the implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency)
- **[Story]**: US1 / US2 / US3 (from spec.md) or SETUP / POLISH

## Phase 1: Setup

- **T001** [SETUP] Read and confirm the clone-target scaffold in
  `src/retail/rules/assumptions.py` (AL1) and the rule context surface in
  `src/retail/rules/core.py` / `src/retail/rules/registry.py`; confirm the current
  authoritative rule count in `docs/rules/rules-manifest.json` and the expected-rule-id set
  in `tests/unit/test_rules_wiring.py` so the target count is "current + 1". No file change.

- **T002** [SETUP] Choose the new rule id (a short unique id in the existing convention,
  not colliding with any id in the expected set) and record it in this tasks file before
  wiring. No behavior yet.

## Phase 2: US1 -- Illegal composition surfaced as ERROR (Priority: P1)

- **T003** [US1] Write FAILING unit test `tests/unit/test_additivity_consistency.py`: a
  fixture pair of define-layer contracts where a fully-additive parent composes a
  non-additive (ratio) child by direct SUM -> assert exactly one ERROR finding naming the
  metric; a repaired base-over-base fixture -> assert zero findings. Add the semi-additive-
  into-plain-SUM illegal case and its ERROR assertion. (Acceptance US1.1-US1.3; SC-002.)

- **T004** [US1] Implement `src/retail/rules/additivity_consistency.py`: clone the AL1
  scaffold -- `@register(<id>, <desc>)`, lazy parser import inside the handler, generic glob
  over the define-layer prose corpus, template + `is_test_path` exemption, fail-loud on
  unreadable. Parse the closed additivity vocabulary and the committed derivation edges into
  the data-model shapes; apply the closed legality table; return ERROR-only findings for
  illegal compositions. Make T003 pass. (FR-001, FR-002, FR-003, FR-005, FR-006, FR-009.)

## Phase 3: US2 -- Absent/ambiguous class refused, never inferred (Priority: P1)

- **T005** [US2] Extend `tests/unit/test_additivity_consistency.py` with a FAILING case: a
  metric on a derivation edge with a missing additivity heading -> assert an ERROR that the
  class is absent (not a composition verdict); a metric with an out-of-vocabulary word ->
  assert an ERROR that the class is ambiguous. Assert NO inferred class is produced.
  (Acceptance US2.1-US2.2; SC-003; FR-004.)

- **T006** [US2] In `additivity_consistency.py`, implement the absent/ambiguous branch:
  classify only on exact closed words; emit an ERROR (never a default class) when a metric
  on an edge is absent/ambiguous; never infer. Make T005 pass. (FR-004, FR-005.)

## Phase 4: US3 -- Wired in and counted (Priority: P2)

- **T007** [US3] Edit `src/retail/rules/__init__.py`: add the new module to the side-
  effecting import block AND to `__all__` (2 of the 5 wiring points).

- **T008** [US3] Edit `tests/unit/test_rules_wiring.py`: add the new rule id to the
  expected-rule-id set (count -> current + 1).

- **T009** [US3] Regenerate `docs/rules/rules-manifest.json` via the repo's manifest
  generator so it includes the new rule and its authoritative count is current + 1.

- **T010** [US3] Regenerate the severity-posture manifest / golden fixture so the new rule's
  ERROR posture is present (the 5th wiring point).

- **T011** [US3] Run `tests/unit/test_rules_wiring.py`: confirm actual registered ids ==
  expected set and manifest count == len(expected). (SC-004.)

## Phase 5: Polish / Verification

- **T012** [POLISH] Run the full unit suite (`pytest -m unit`) and the retail governance
  check on the current committed corpus: confirm zero findings from the new rule on `main`'s
  corpus (SC-001) and that the check still passes.

- **T013** [POLISH] Verify invariants by inspection: no numeric score/confidence/threshold
  in any finding; no DAX/connection/visual; core module still imports with stdlib only at
  module scope; no worked-example metric name/id/path is baked into the rule or table
  (SC-005, FR-002, FR-003, FR-006 generality). Confirm ASCII/UTF-8-no-BOM in the new files.

## Dependencies / order

- T001, T002 (setup) before all.
- US1 (T003->T004) before US2 (T005->T006) sharing the same rule module and test file, so
  they are SEQUENTIAL, not parallel.
- US3 wiring (T007-T011) after the rule id exists (T002) and the module exists (T004); T007,
  T008 touch different files and may be [P], but T009/T010 regeneration must follow the
  module + expected-set edits and T011 runs last of the phase.
- Polish (T012-T013) last.

## Out of scope (YAGNI -- do NOT do)

- Do NOT add a structured `additivity` or `derives_from` field to any metric contract.
- Do NOT build a cross-corpus id join (FR-011 is OPEN, human ruling).
- Do NOT self-ratify the legality matrix (FR-012 is OPEN, human ruling).
- Do NOT assume any deferred runtime/adapter; the rule is a static text read only.
