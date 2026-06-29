# Specification Analysis Report: Live-Surface Import Boundary Guard (B3)

Cross-artifact consistency pass over spec.md, plan.md, tasks.md (and the
supporting research.md, data-model.md, contracts/rule-contract.md, quickstart.md)
on branch `048-live-surface-import-boundary-guard`. READ-ONLY; no files modified
by this pass.

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Inconsistency | LOW | plan.md code-block trees | Directory-tree blocks use box-drawing glyphs (the only non-ASCII in any artifact). | Matches shipped sibling 044/047 plans (repo precedent for fenced tree blocks); prose uses `--`/`->`. Acceptable; no prose glyphs. |
| U1 | Underspecification | LOW | spec.md FR-007, tasks.md T005 | Final live-surface set membership is a candidate, not closed (`metric_drift.py` deliberately excluded for now). | Intended: membership is a [HUMAN RATIFY] item; tasks pick a working set and leave the question open. No action. |
| U2 | Underspecification | LOW | spec.md Clarifications, tasks.md T001/T014 | The registry rule id is a placeholder pending ratification. | Intended: tasks use a non-colliding working id and record the open question. No action. |
| A1 | Ambiguity | LOW | research.md R2 | Two acceptable rule placements (new sibling module vs. second @register in never_execute.py). | tasks.md commits to the sibling module as primary; contract is identical either way. No action. |
| O1 | Over-scope check | INFO | tasks.md scope guard | Verified tasks add only one rule + tests + id update + manifest; no scanned-module behavior change, no new dep/executor/severity. | None. |

No CRITICAL or HIGH findings.

## Coverage Summary

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| FR-001 (one registered rule) | Yes | T005 | |
| FR-002 (reuse helper, no fork) | Yes | T001, T005 | |
| FR-003 (parse-not-import) | Yes | T005 | |
| FR-004 (lazy/TYPE_CHECKING ok) | Yes | T003 | |
| FR-005 (try/if flagged) | Yes | T004 | |
| FR-006 (unparseable fail loud) | Yes | T004 | |
| FR-007 (explicit, disjoint, generic set) | Yes | T005, T011, T012 | |
| FR-008 (wiring + manifest, no baseline) | Yes | T007, T008, T009 | |
| FR-009 (firing test, not just listed) | Yes | T003, T010 | closes wiring-latent-gap |
| FR-010 (immutable Finding, no mutation) | Yes | T005 | |
| FR-011 (ERROR uniform) | Yes | T005 | clarified 2026-06-30 |
| SC-001 (regression caught) | Yes | T006 | |
| SC-002 (no false positive on lazy) | Yes | T003 | |
| SC-003 (registry==manifest==wiring) | Yes | T009 | |
| SC-004 (rule exercised firing) | Yes | T010 | |
| SC-005 (no domain artifact) | Yes | T012 | |
| SC-006 (no new dep/network/DB) | Yes | T013 | |

Coverage: 11/11 FR + 6/6 buildable SC = 100% have >=1 task.

## Constitution Alignment Issues

None. The plan's Constitution Check addresses Principle II (Depend Never Fork --
reuse the helper), Principle VIII (static-first, parse-not-import; severity ERROR
matching B1 recorded as a judgment), Principle VII (generic, no C086), Principle
IX (ASCII/Windows-safe), anti-fabricated-confidence (Findings only, no readiness
number), and rule-registry integrity (043 snapshot + wiring + firing test). The
three [HUMAN RATIFY] items (set membership, registry id, readiness stage) are
correctly left to a named human (Principle V) and are not self-granted.

## Unmapped Tasks

None that lack a requirement link. T001/T002 are setup/foundational
(reuse-surface confirmation, wiring-mechanism confirmation). T014 is a
governance-discipline guard (keeps the [HUMAN RATIFY] items unanswered). T013 is
cross-cutting polish (SC-006). All trace to the spec's intent.

## Metrics

- Total Requirements: 11 FR + 6 buildable SC = 17
- Total Tasks: 14
- Coverage: 100% (every FR and buildable SC has >=1 task)
- Ambiguity Count: 1 (LOW, resolved-by-decision in research.md)
- Duplication Count: 0
- Critical Issues Count: 0
- High Issues Count: 0

## Next Actions

No CRITICAL or HIGH issues. The draft is internally consistent and constitution-
aligned. The remaining open items are deliberate human-ratification decisions
recorded in spec.md ## Clarifications, not defects. Proceed to the adversarial
plan-review gate; ratification (and any change to set membership / registry id /
readiness stage) remains a human action this workflow does not perform.
