# Specification Analysis Report -- 018-companion-tools-architecture (F024)

**Date**: 2026-06-26  **Mode**: read-only cross-artifact consistency pass
**Artifacts**: spec.md (clarified 2026-06-25), plan.md, tasks.md
**Constitution**: `.specify/memory/constitution.md` v1.6.0

> Note: `.specify/scripts/powershell/check-prerequisites.ps1` aborts on this
> isolated worktree because the branch (`worktree-wf_4cefe1c4-0a1-1`) is not
> feature-numbered. `.specify/feature.json` resolves correctly to
> `specs/018-companion-tools-architecture`; all three artifacts were loaded
> directly. This does not affect the analysis.

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| N1 | Inconsistency | MEDIUM | plan.md:L112; tasks.md:L138,L162 vs spec.md:FR-009/Architecture | ADR-number drift: the clarify session moved the enumerated ADR from `0006` to `0008` (0006/0007 already shipped). spec.md updated; plan.md and tasks.md still name `0008-core-authority-vs-product-modules.md`. | Update plan.md L112 and tasks.md L138/L162 to `0008-...`. Flagged for the ledger; NOT auto-edited (plan/tasks are out of the clarify write-scope). |
| I1 | Inconsistency | LOW | spec.md (roadmap citation) vs docs/roadmap/roadmap.md | The roadmap ledger (2026-06-25) lists F005-F015 shipped + F016 only; it does not yet carry the F024-F033 tier the spec declares against. | Resolved in-spec by the new Dependencies "Sequence authority" note: `specs/` is authoritative for the batch; roadmap reconciliation is a deferred docs follow-up. No artifact change needed this slice. |
| C1 | Coverage | LOW | tasks.md Phase 7 (T019-T024) | The five enumerated FUTURE deliverables are carried as tasks in the SAME tasks.md as the current slice. | Acceptable: Phase 7 is explicitly labelled FUTURE / next-slice and the dependency section states this slice authors none of them. No action. |
| A1 | Ambiguity | LOW | spec.md edge case "highest authority capability" | "classify by its HIGHEST authority capability used" relies on an implicit ordering of the Module sub-axis. | Minor: the tie-break prose ("most restrictive matching sub-axis") covers it. Optional: state the read-only < artifact-writing < execution-capable ordering explicitly in the future `product-modules.md`. |

## Coverage Summary (Functional Requirements -> Tasks)

| Requirement | Has Task? | Task IDs | Notes |
|-------------|-----------|----------|-------|
| FR-001 (five categories, closed set) | yes | T003 | |
| FR-002 (authority matrix; only Core creates truth/approves) | yes | T004, T013 | |
| FR-003 (Module capability sub-axis) | yes | T005 | |
| FR-004 (Adapter connectivity sub-axis) | yes | T005 | |
| FR-005 (module-vs-adapter seam) | yes | T006, T010 | |
| FR-006 (Maintenance Automation; Principle V pin) | yes | T006, T012 | clarify-added Principle-V clause covered by T012 intent |
| FR-007 (orthogonal to Six layers) | yes | T008 | |
| FR-008 (operate from committed/approved evidence only) | yes | T004, T013 | |
| FR-009 (enumerate five future deliverables) | yes | T014 | ADR slot now 0008 in spec; see N1 |
| FR-010 (no code/rule/stage; retail check exit 0) | yes | T016 | |
| FR-011 (no numeric/maturity score) | yes | T015 | |
| FR-012 (conformance check deferred/enumerated) | yes | T014, T024 | |
| FR-013 (generic; no C086 specifics) | yes | T017 | |
| FR-014 (classify shipped surfaces) | yes | T007 | |

All 14 FRs map to >=1 task. SC-001..SC-007 each trace to US1/US2/US3 acceptance + Phase 6 gates.

## Constitution Alignment

No MUST violations. Spot checks:

- Principle I (agent-first, gate-enforced): contract adds no gate; agent classifies, gate disposes. PASS.
- Principle V (agent stops at judgment calls): clarify-added FR-006 clause explicitly states Maintenance Automation does NOT relax the named-human approval boundary. Strengthens alignment. PASS.
- Principle VII (C086 is an example): FR-013/SC-004 keep artifacts generic. PASS.
- Principle VIII (static-first, live deferred): FR-010/FR-012 add no rule/checker/stage; conformance check enumerated + deferred. PASS.
- Principle IX (reproducibility / ASCII no-BOM): all three artifacts verified pure-ASCII, no BOM. No numeric/maturity score (FR-011). PASS.

## Unmapped Tasks

None. T001-T002 (setup reads), T018 (encoding/header gate) are process tasks; all other tasks map to an FR or US.

## Metrics

- Total Functional Requirements: 14
- Total Success Criteria: 7
- Total Tasks: 24 (T001-T018 this slice; T019-T024 FUTURE)
- Requirement coverage: 14/14 = 100%
- Ambiguity findings: 1 (LOW)
- Duplication findings: 0
- Inconsistency findings: 2 (1 MEDIUM, 1 LOW)
- CRITICAL issues: 0
- HIGH issues: 0

## Verdict

**CLEAN of CRITICAL/HIGH.** 0 CRITICAL, 0 HIGH. One MEDIUM (N1: ADR-number
drift between the clarified spec and plan/tasks) and minor LOW items remain.

## Next Actions

- Proceed allowed: no CRITICAL/HIGH blockers.
- MEDIUM N1 should be fixed before implementation: align plan.md L112 and
  tasks.md L138/L162 from `0006` to `0008`. Recorded for the chain ledger;
  not auto-applied here (analyze is read-only; plan/tasks are outside the
  clarify write-scope this run).
