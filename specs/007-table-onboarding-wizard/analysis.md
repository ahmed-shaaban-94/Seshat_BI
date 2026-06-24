# Cross-Artifact Analysis: 007-table-onboarding-wizard

**Date**: 2026-06-24 | **Scope**: spec.md + plan.md + tasks.md vs the constitution,
the readiness spine, the roadmap (F006), and the existing skills (`source-mapping`,
`retail-orchestrate`, `retail-build-warehouse`).

**Method**: a `/speckit-analyze`-style cross-artifact pass -- coverage (every
requirement traces to a task and to a success criterion), consistency (no artifact
contradicts another or the constitution), terminology, scope leakage, and the
mapping-mandatory / stop-and-ask gates.

## Verdict

**PASS -- ready to draft as final.** No CRITICAL or HIGH findings. All eleven
functional requirements trace to tasks and to success criteria; no constitution
principle is violated or weakened; no C086/pharmacy leakage; the Source -> Mapping
stage boundary and the four Principle-V human seams are consistently encoded across
all three artifacts. The minor items below are LOW (recorded, not blocking).

## Coverage matrix (FR -> tasks -> success criterion)

| FR | Requirement (short) | Tasks | Success criterion |
|----|---------------------|-------|-------------------|
| FR-001 | wizard SKILL.md, no Python/CLI/codegen | T001, T004, T005 | SC-001, SC-002 |
| FR-002 | committed onboarding checklist | T002, T011, T015, T019 | SC-001 |
| FR-003 | run-state from disk; resume; no run-state file | T006, T016 | SC-003 |
| FR-004 | Stage 1 profile (read-only; ''OR NULL; PK proof; returns) | T007 | SC-003 |
| FR-005 | Stage 2 delegate to source-mapping; RC defaults | T008 | SC-003 |
| FR-006 | seed readiness-status; evidence/blockers; no confidence | T009, T013 | SC-003 |
| FR-007 | four human-seam HARD-STOPs | T012, T013, T014 | SC-004 |
| FR-008 | hard-stop at Mapping Ready; no silver; no self-grant | T010, T017 | SC-005 |
| FR-009 | generic only (no C086 specifics) | T022, T023 | SC-001 |
| FR-010 | Orchestration pointer + reciprocal conductor edit | T020, T021 | (integration) |
| FR-011 | deferred-boundary honesty ([PENDING LIVE PROFILE], warning) | T018 | SC-003 |

Every FR maps to >=1 task and >=1 success criterion. Every success criterion
(SC-001..SC-005) is exercised by >=1 task. Verification tasks T024-T027 close the
gate (SC-002) and the dry-run acceptance (SC-003/4/5). No orphan requirements,
no untraceable tasks.

## Constitution alignment (re-checked against plan.md's gate table)

- Principle I (Agent-First): PASS -- skill, not CLI; gates are CALLED. No artifact
  proposes a `retail onboard` subcommand (the spec records "any CLI subcommand" as
  NOT built).
- Principle IV (Source Mapping Before Silver): PASS, load-bearing -- the terminal
  state is Mapping Ready; FR-008 + T010/T017 forbid silver and self-granting the gate.
  Consistent with mapping-ready.md (approval is a human approvals[] action).
- Principle V (Stops at Judgment Calls): PASS, load-bearing -- the four seams
  (grain, PII, business rollup, product identity) are HARD-STOPs (FR-007, T012-T014),
  and are recorded as open_for_human, NOT auto-answered.
- Principle VII (C086 is an example): PASS -- FR-009 + T023 leakage sweep; SC-001
  asserts zero specifics.
- Principle VIII (Static-first / no fake confidence): PASS -- four explicit statuses +
  evidence + blockers; no numeric score (FR-006); deferred mode records warning,
  never a fabricated pass (FR-011).
- Principle IX (Secrets / ASCII / paths): PASS -- enable steps printed, no DSN
  committed; ASCII + UTF-8 no BOM asserted (T026, SC-001).

## Consistency checks

- Stage boundary is identical across artifacts: spec ("ENTERS Source Ready, EXITS
  Mapping Ready"), plan (Constitution Check IV row), tasks (T010/T017 terminal,
  no-silver invariant in Notes). No drift.
- Delegation, not duplication: spec FR-005 + plan Structure Decision + tasks T008 all
  state the wizard CALLS source-mapping and does not re-implement it.
- Relationship to the conductor: spec's "Where this sits" table, plan's reused/edited
  list, and tasks T020/T021 agree -- the wizard is the Source->Mapping LEG; the
  self-heal loop stays in retail-orchestrate. Matches readiness-pipeline.md.
- Roadmap reconciliation: the roadmap lists this as F006; the spec dir is numbered 007
  (parallel-worktree numbering). Both numbers are stated in spec.md + plan.md. (LOW-1.)
- Readiness-status reuse: spec/plan/tasks all treat templates/readiness-status.yaml as
  the SEED (used, not redefined). Consistent with readiness-model.md.

## Terminology

- "Source Ready" / "Mapping Ready" / the four statuses (not_started / blocked /
  warning / pass) are used exactly as defined in readiness-model.md. No synonym drift.
- "Gate status: CLEARED" is used only as the HUMAN-set field the wizard READS, never
  one it writes -- consistent across all three artifacts and with the orchestrate skill.

## Scope-leakage scan

- No C086/pharmacy specifics in any artifact (T023 enforces it at build time).
  Placeholders <schema>.<table>, <wizard-skill-name> used throughout.
- No out-of-stage work: no silver SQL, no gold star, no PBIP, no pbi-cli, no live
  retail validate run is required by any task -- all correctly deferred.

## Findings (all LOW -- recorded, not blocking)

- LOW-1 (roadmap number vs spec number): roadmap says F006; spec dir is 007. Both
  artifacts state both numbers, so this is parallel-numbering labeling, not a
  contradiction. Action: none required.
- LOW-2 (three auto-defaulted names): skill name (retail-onboard-table), checklist
  home (docs/readiness/onboarding-checklist.md), and readiness-status file home
  (mappings/<table>/readiness-status.yaml) are defaulted in plan.md Phase 0. All
  reversible. Recorded as auto_decisions. Action: confirm at implementation time.
- LOW-3 (rule count not pinned): SC-002 says retail check stays exit 0 at the
  "current rule count" without naming the number, because the constitution carries a
  known stale-count caveat (26 vs 27, G6). Intentional; avoids baking a drifting
  number. Action: none.

## Open for human (NOT auto-answered -- Principle V seams)

Surfaced by the wizard at RUN time, per table; NOT decisions this spec chain makes:

1. Grain -- the correct row level / candidate PK for the onboarded table.
2. PII publish-safety -- which columns are PII and whether dropping is the right
   handling (governance sign-off).
3. Business rollup / segment mapping -- the analyst-supplied value->group table.
4. Product identity -- which column authoritatively identifies the entity.

## Conclusion

The four artifacts are internally consistent, fully traceable, constitution-aligned,
generic, and correctly bounded to the Source -> Mapping readiness transition. No
CRITICAL/HIGH issues. Status: drafted.
