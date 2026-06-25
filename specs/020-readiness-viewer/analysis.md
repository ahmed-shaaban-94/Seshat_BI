# Specification Analysis Report -- Readiness Viewer (F026, spec-dir 020)

**Date**: 2026-06-26  **Mode**: read-only cross-artifact consistency pass
**Artifacts**: spec.md, plan.md, tasks.md  **Constitution**:
`.specify/memory/constitution.md` (Principles I-IX)

This is the `/speckit-analyze` capture for the post-clarify state of F026. The spec was
clarified on 2026-06-25 (Session 2026-06-25: three rendering-rule clarifications --
required-approval source, item discovery, evidence verbatim form). plan.md and tasks.md
pre-existed and were verified, not rewritten.

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Coverage | LOW | tasks.md T019 / spec Non-goals | The optional deferred CLI `src/retail/tools/readiness_viewer.py` is enumerated as future-only in both spec and T019; it has no implementing task by design. | None -- intentional non-goal; T019 correctly enumerates-but-does-not-build. |
| I1 | Inconsistency | LOW | spec FR-006/Allowed-ops vs plan.md L29-32 / tasks T002 | Post-clarify, FR-006 reads the "Required owner / approval" field of `docs/readiness/<stage>-ready.md` to decide when to flag a missing approval. plan.md Primary Dependencies and T002 list `readiness-status.yaml` + readiness-model.md but do not explicitly name the per-stage `<stage>-ready.md` docs as a read input. | Non-blocking. T014 already flags a `pass` gate whose required approval is absent; the stage-doc read is the mechanical source the clarification pins. Ledger note; optional one-line add to plan Primary Dependencies + T002/T014 in the implementation slice. |
| A1 | Ambiguity | LOW | spec FR-005 / edge cases | "line/section where recorded" -- clarified (Session 2026-06-25) to mean "rendered verbatim if the entry carries an anchor; never synthesized". | Resolved by clarification; no action. |
| D1 | Duplication | LOW | spec scope-wall vs Forbidden operations | The no-create-truth / no-fake-confidence / generic constraints recur in the scope wall, the F012-delta section, Forbidden operations, and the governance checklist. | Intentional redundancy (load-bearing boundary restated for the reader); not a defect. Keep. |
| U1 | Underspecification | LOW | spec US1 / FR-004 | Matrix ROW ORDER across items is not specified (spec deliberately leaves sort order open; F012 owns worst-first severity sort). | Acceptable -- row order is not load-bearing for a stage-lens; leaving it open avoids re-speccing F012's sort. No action. |

No CRITICAL or HIGH findings. No constitution MUST is violated. No requirement has zero
task coverage. No task is unmapped.

## Coverage Summary

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| FR-001 skill/mode home | yes | T003, T007 | shape (a)/(b) resolved in T003 (plan Phase 0) |
| FR-002 generic template | yes | T006, T010, T013 | one template, three blocks |
| FR-003 read-only inputs + discovery | yes | T002, T007 | reuses F012 `mappings/<table>/` fan-out (clarified) |
| FR-004 seven-stage matrix | yes | T006, T007 | the MVP delta |
| FR-005 evidence as references | yes | T010, T011, T012 | verbatim; no synthesized anchor (clarified) |
| FR-006 approvals timeline | yes | T013, T014, T015 | required-approval source = stage doc (clarified) |
| FR-007 read-only | yes | T005, T007, T022 | git-status-clean proof |
| FR-008 no fake confidence | yes | T016 | rule #9 |
| FR-009 missing/partial input | yes | T008 | "no readiness file" / "incomplete" |
| FR-010 conflict surfacing | yes | T011, T014 | surface, never resolve (Principle V) |
| FR-011 F012 relationship | yes | T004, T007, T017, T024 | delta statement single-sourced |
| FR-012 orchestration pointer | yes | T018 | retail-orchestrate READ |
| SC-001 files exist + generic | yes | T009, T021, T023 | ASCII/no-BOM + generic grep |
| SC-002 retail check exit 0, no rule | yes | T020 | no validator added |
| SC-003 matrix cells = recorded | yes | T009 | read-only proven |
| SC-004 evidence references | yes | T012 | missing/not-found flags |
| SC-005 approvals verbatim | yes | T015 | no approval added |
| SC-006 F012 delta holds | yes | T022, T024 | three deltas only |
| SC-007 score declined | yes | T016 | four statuses returned |

## Constitution Alignment

No issues. Spot-check of the load-bearing principles for a read-only Product Module:

- **I (Agent-First, Gate-Enforced)**: viewer adds no gate, is not the authority on
  pass/fail; `retail check` stays the gate (SC-002, T020). Aligned.
- **II (Depend, Never Fork)**: reuses F012's shipped aggregation; no fork (FR-003, T003).
  Aligned.
- **V (Agent Stops at Judgment Calls)**: conflicts and missing approvals/evidence are
  SURFACED as flags, never auto-resolved (FR-010, T011/T014); no-self-approval is a
  Forbidden op (FR-006). The clarify pass explicitly REFUSED to auto-answer any grain /
  PII / business-rollup / product-identity question -- none arose, and none was invented.
  Aligned.
- **VII (C086 Is An Example)**: skill + template generic; C086 cited only (SC-001, T021).
  Aligned.
- **VIII (Static-First, Live Deferred)**: no Python, no rule, no CLI, no DB read this
  slice; optional CLI enumerated + deferred (Non-goals, T019). Aligned.
- **IX (Secrets & Reproducibility / no fake confidence)**: no secrets/DSNs; ASCII + no
  BOM (T023); no numeric confidence score (FR-008, T016). Aligned.

## Unmapped Tasks

None. Every task T001-T024 maps to a requirement, a success criterion, a setup/foundation
step, or an explicit polish/verification gate. Setup (T001-T002) and Foundational
(T003-T005) are prerequisite tasks; Polish (T016-T024) are whole-feature verification
gates. All trace to an FR/SC or to a constitution principle.

## Metrics

- Total Functional Requirements: 12 (FR-001..FR-012)
- Total Success Criteria: 7 (SC-001..SC-007)
- Total Tasks: 24 (T001..T024)
- Requirement coverage: 100% (19/19 FR+SC have >= 1 task)
- Ambiguity count: 1 (A1, LOW -- resolved by the 2026-06-25 clarification)
- Duplication count: 1 (D1, LOW -- intentional boundary restatement)
- Inconsistency count: 1 (I1, LOW -- stage-doc read input not yet named in plan/T002)
- Critical issues: 0
- High issues: 0

## Verdict

**CLEAN** -- 0 CRITICAL, 0 HIGH. The five findings are all LOW and are either intentional
(C1, D1, U1) or already resolved by the clarification (A1), with one non-blocking note for
the implementation slice (I1: name `docs/readiness/<stage>-ready.md` as a read input in
plan Primary Dependencies and T002/T014 when authoring the skill). The feature may proceed
to `/speckit-implement` for the authoring slice. No constitution principle requires
adjustment.

## Next Actions

- No CRITICAL/HIGH blockers. Proceed to the implementation (authoring) slice when ready.
- Optional, non-blocking (I1): in the implementation slice, add `docs/readiness/<stage>-ready.md`
  ("Required owner / approval") to plan.md Primary Dependencies and to T002/T014 so the
  approval-requirement read input is named where the artifacts are authored. This is a
  refinement of existing tasks, not a new task.
