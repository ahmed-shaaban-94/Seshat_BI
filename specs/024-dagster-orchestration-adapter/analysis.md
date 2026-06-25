# Specification Analysis Report -- Dagster Orchestration Adapter (F030 / spec 024)

Read-only cross-artifact consistency pass over spec.md + plan.md + tasks.md, validated against
the constitution (v1.6.0). No artifact was modified by this analysis. This file is the captured
report (repo convention).

Run date: 2026-06-26. Scope: planning-only slice (five Spec-Kit files; no Dagster code).

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Coverage Gap | MEDIUM | spec.md FR-013; tasks.md Phase 5/8 | FR-013 (a halted/fail-closed run MUST terminate with a non-zero/failed run status) was added by the 2026-06-25 clarify pass AFTER tasks.md was authored; no task names FR-013 explicitly. | Add a one-line US1/US3 sub-task (or extend T008/T013) to author the failed-run-status signal; non-blocking -- it refines existing fail-closed stories, does not contradict them. |
| C2 | Coverage Gap | LOW | spec.md Edge Cases (F016 parked); tasks.md T017 | The new "F016 parked / not yet built" edge case is adjacent to T017 (publish-trigger-only) but not explicitly enumerated as a task line. | Optionally extend T017 to author the F016-absent fail-closed edge; the spec already states it, so coverage is satisfied at the spec level. |
| I1 | Inconsistency (terminology) | LOW | plan.md L169-173, L134-139 vs spec.md FR-007/Key Entities | Plan still names the run-evidence record `templates/dagster-run-evidence.md` and `dagster-run-evidence.md`; spec now fixes the per-run home at `orchestration/dagster/run-evidence/<run-id>.md` (the template under `templates/` remains the generic shape). | Harmonize on next plan touch: `templates/dagster-run-evidence.md` = the generic template; `orchestration/dagster/run-evidence/<run-id>.md` = the per-run instance. Not contradictory (template vs instance); cosmetic drift only. |
| U1 | Underspecification | LOW | spec.md FR-007 / readiness `evidence[]` | The clarify answer routes measured results into the affected table's readiness `evidence[]`; the exact write mechanism (Core Authority process vs adapter proposing the entry) is left to the implementation slice. | Acceptable: the spec is explicit that Core Authority records any `pass`; the `evidence[]` surfacing mechanism is correctly deferred (Principle VIII, roadmap rule #8). No action this slice. |
| N1 | Note (scope) | INFO | tasks.md header (FR-001..FR-012) | tasks.md enumerates FR-001..FR-012; FR-013 is the only requirement added post-tasks. | Recorded for the ledger; the plan/tasks remain valid (FR-013 is a derived-signal refinement of US1/US3, not a new capability that reshapes the asset graph). |

## Coverage Summary

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| FR-001 (five files only; no Dagster file) | Yes | T026, T029 | Five-files-only + no-Dagster-file verification. |
| FR-002 (asset graph gate semantics) | Yes | T004, T009 | STOP / HUMAN-SEAM edge classification. |
| FR-003 (closed allowed RUN list) | Yes | T005 | Allowed-vs-forbidden fixed. |
| FR-004 (forbidden ops enumerated) | Yes | T005, T016 | No-self-approval + forbidden list. |
| FR-005 (fail-closed propagation) | Yes | T007, T008 | US1 MVP. |
| FR-006 (human-seam reads committed approval) | Yes | T010, T011 | US2. |
| FR-007 (derived run-evidence; no truth-write; run-evidence path + evidence[]) | Yes | T013, T014, T015 | US3; run-evidence path refined by clarify, template enumerated. |
| FR-008 (F005 reconciliation) | Yes | T021 | Conductor sibling. |
| FR-009 (auto-update posture; defer to F031/F033) | Yes | T022 | Pin-together, PR-only, smoke. |
| FR-010 (generic; C086 cited not inlined) | Yes | T028 | Leak grep. |
| FR-011 (ASCII / UTF-8 no BOM) | Yes | T027 | Non-ASCII grep. |
| FR-012 (all stages sequenced, none decided) | Yes | T004, T016 | Authority boundary. |
| FR-013 (halted/fail-closed run -> non-zero run status) | No (implicit) | (T008/T013 adjacent) | C1 -- added post-tasks; refine a task line. |
| SC-001..SC-007 | Yes | T024-T029 | Checklists + whole-feature gates. |

Requirements with >=1 explicit task: 12 of 13 (FR-013 implicit). Coverage = 92% explicit,
100% at the spec level (FR-013 is authored in the spec and enforced by US1/US3 verification).

## Constitution Alignment

No constitution MUST violation found. The spec actively reinforces:

- Principle I (Agent-First, Gate-Enforced): asset success means "command ran, returned this
  exit," never "stage passed"; gate exit code stays the authority. FR-012, US4.
- Principle II (Depend, Never Fork): planned Dagster project is a separate upgradeable
  dependency; publish wall holds even when F016 is parked (clarify Q1, new edge case). FR-002.
- Principle IV (Source Mapping Before Silver): `silver_tables` is a HUMAN-SEAM/STOP edge,
  blocked until the mapping is CLEARED; never self-granted. FR-006, US2.
- Principle V (Agent Stops at Judgment Calls): every grain/PII/rollup/segment/sentinel call
  HALTS the asset and escalates; the orchestrator resolves none. FR-004, US4. (The clarify pass
  correctly REFUSED to auto-answer any Principle-V item; all three clarified questions were
  execution-posture, not judgment calls.)
- Principle VIII (Static-First, Live Deferred): no Dagster code, no new rule this slice;
  `retail validate` stays gated on creds; a deferred-boundary result never fabricates a pass.
- Principle IX (Secrets & Reproducibility): no score in run evidence (clarify reaffirms the
  failed-run-status is a derived signal, not a score); ASCII + UTF-8 no BOM. FR-007, FR-011, FR-013.

## Unmapped Tasks

None. Every task (T001-T029) maps to a requirement, a user story, or a constitution-mandated
gate (verification/checklist tasks T024-T029 map to SC-001..SC-007 + Principles VIII/IX).

## Metrics

- Total Requirements: 13 FR + 7 SC = 20.
- Total Tasks: 29 (T001-T029).
- Coverage: 12/13 FR have an explicit task (92%); 100% at spec level.
- Ambiguity Count: 0 unresolved (3 resolved by the 2026-06-25 clarify session).
- Duplication Count: 0.
- Inconsistencies: 1 LOW (I1, template-vs-instance naming drift in plan.md).
- Critical Issues: 0.
- High Issues: 0.

## Verdict

CLEAN: 0 CRITICAL, 0 HIGH. The chain is internally consistent and constitution-aligned. The
only follow-ups are LOW/MEDIUM polish: thread FR-013 into an explicit task line (C1) and
harmonize the run-evidence template-vs-instance naming in plan.md on its next touch (I1).
Neither blocks the planning slice; both are recorded for the ledger.

## Next Actions

- Proceed: the planning slice is complete and consistent; no CRITICAL/HIGH blocks.
- On the next plan/tasks touch (not required this slice): add a task line for FR-013 (C1) and
  harmonize the run-evidence naming (I1).
- No constitution amendment required.
