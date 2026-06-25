# Specification Analysis Report -- Evidence Pack Generator (F028)

**Feature dir**: `specs/022-evidence-pack-generator/`  **Date**: 2026-06-26
**Artifacts analyzed**: spec.md, plan.md, tasks.md  **Authority**: constitution v1.6.0 (Principles I-IX), roadmap (hard rules 1-9)
**Mode**: read-only cross-artifact consistency pass. No spec.md / plan.md / tasks.md modified.

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Inconsistency | MEDIUM | plan.md "Structure Decision" (L134-139) vs spec.md Clarifications + Assumptions | Plan still calls per-table FILLED pack placement "a deferred decision (cheaply reversible)"; the 2026-06-25 clarify RESOLVED it to `mappings/<table>/`. Plan text is now mildly stale, not contradictory (plan defers; spec resolves). | At the next plan touch, update the Structure Decision sentence to cite the resolved `mappings/<table>/` placement. Not a blocker -- spec is authoritative and the resolution is reversible-easy. |
| I1 | Inconsistency | LOW | tasks.md (no task references storage-path / export-format / tally decisions) | The three clarified decisions (no tally, `mappings/<table>/`, markdown-only) are not yet reflected as explicit tasks; they were deferred when tasks.md was authored. | Optional: add a one-line note in T020 (template enumeration) that filled packs land under `mappings/<table>/` and export is markdown-only. Low impact -- build-slice details; tasks.md is planning-only here. |
| A1 | Coverage | LOW | spec.md SC-002 / tasks.md T021 | SC-002 ("100% of sections resolve to a committed source OR a recorded blocker") is verified via the acceptance checklist (T021) rather than a dedicated task. | Acceptable for a planning-only slice; the checklist is the standin-for-tests verification per tasks.md preamble. No action required. |

No CRITICAL or HIGH findings. No constitution MUST violations. No duplicate or conflicting requirements. No unmapped tasks. No terminology drift across the three artifacts (four-status vocabulary, "compose not invent", F013 one-directional delta, surface-not-assert are used identically in all three).

## Coverage Summary (Functional Requirements -> Tasks)

| Requirement | Has Task? | Task IDs | Notes |
|-------------|-----------|----------|-------|
| FR-001 (10 fixed ordered sections) | yes | T003, T007, T008, T009 | section contract fixed in FOUND, authored in US1 |
| FR-002 (compose + link each section) | yes | T003, T007, T008, T009 | |
| FR-003 (missing -> blocker, never fabricate) | yes | T004, T010, T011 | integrity guarantee (US2) |
| FR-004 (embed F013; never re-author) | yes | T005, T023 | one-directional delta verified in Polish |
| FR-005 (surface publish_ready; no write/move/edit) | yes | T006, T013, T014, T015 | |
| FR-006 (no claim without pass + named approval) | yes | T006, T013, T014, T017, T024 | guardrail; reinforced by in-progress check T017 |
| FR-007 (four statuses; no score; no tally in base) | yes | T004, T009, T010, T011 | tally clarification (2026-06-25) consistent with hard rule #9 |
| FR-008 (in-progress composition) | yes | T016, T017 | US4 |
| FR-009 (surface disagreement as warning) | yes | T012, T015 | Principle V stop-and-ask |
| FR-010 (read committed only; no live/exec) | yes | T018, T026 | |
| FR-011 (generic; no C086 specifics) | yes | T025 | leakage grep |
| FR-012 (ASCII/UTF-8 no BOM/short paths) | yes | T027 | |
| FR-013 (no new rule/stage/gate) | yes | T026 | |

| Success Criterion | Has Task? | Task IDs | Notes |
|-------------------|-----------|----------|-------|
| SC-001 (one traceable 10-section pack) | yes | T021 + T007-T009 | |
| SC-002 (100% sections -> source or blocker) | yes | T021 | checklist verification |
| SC-003 (missing -> blocked, not fabricated) | yes | T021 + T010/T011 | |
| SC-004 (claim only on pass + approval) | yes | T021 + T024 | |
| SC-005 (writes only derived pack) | yes | T021 + T026 | |
| SC-006 (generic; no rule; no live read; conventions) | yes | T021 + T025/T026/T027 | |

## Constitution Alignment

No conflicts. Plan's Constitution Check table maps all nine principles to PASS; this analysis confirms each holds after the 2026-06-25 clarifications:
- **Principle V** (stop at judgment calls): the clarify pass correctly REFUSED to auto-answer any Principle-V carve-out (grain/uniqueness, PII publish-safety, business rollup/segment, product identity). The three resolved decisions (tally, storage path, export format) are module-shape choices, not human judgment calls. PASS preserved.
- **Hard rule #9** (no fake confidence): the no-tally-in-base-contract clarification strengthens, not weakens, distance from a fabricated confidence number. PASS.
- **Principle IX / hard rule #8**: markdown-only export + `mappings/<table>/` placement (an established home, ADR 0003) keep paths short and add no new top-level dir. PASS.

## Unmapped Tasks

None. T001-T002 (setup), T018-T020 (future-deliverable enumeration), T021-T027 (whole-feature gates) all trace to a phase purpose and the FR/SC set above.

## Metrics

- Total Functional Requirements: 13 (FR-001..FR-013)
- Total Success Criteria: 6 (SC-001..SC-006)
- Total Tasks: 27 (T001..T027)
- Requirement coverage: 100% (13/13 FRs and 6/6 SCs have >= 1 task)
- Ambiguity count: 0 (post-clarify; 3 deferred decisions resolved this session)
- Duplication count: 0
- Conflict count: 0
- CRITICAL issues: 0
- HIGH issues: 0

## Verdict

**CLEAN** -- 0 CRITICAL, 0 HIGH. Three low/medium consistency notes (C1, I1, A1) are non-blocking staleness/where-verified observations, not defects. The spec is internally consistent, fully task-covered, and constitution-aligned. Safe to proceed; address C1 opportunistically at the next plan edit.

## Next Actions

- No blocker before a future `/speckit-implement` slice. This is a planning-only feature; the deliverable is the spec-kit files.
- Opportunistic: refresh plan.md Structure Decision (C1) to cite the now-resolved `mappings/<table>/` placement.
