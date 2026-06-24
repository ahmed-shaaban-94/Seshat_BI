# Cross-Artifact Analysis: BI Handoff Pack (014)

**Date**: 2026-06-24 | **Branch**: `014-bi-handoff-pack` | **Roadmap**: F013
(Layer 6 -> Publish Ready, stage 7).

Scope of this analysis: spec.md, plan.md, tasks.md for feature 014, checked for
internal consistency and against the constitution (v1.6.0), the roadmap hard
rules, and the readiness spine docs (`readiness-model.md`, `publish-ready.md`,
`dashboard-ready.md`).

## Method

Read the four upstream authorities (constitution, roadmap, publish-ready.md,
readiness-model.md) and the inherited templates the pack composes
(reconciliation-report, readiness-scorecard, data-issues, blocking-reasons,
readiness-status). Cross-checked each spec requirement -> plan gate -> task, and
each hard rule -> artifact treatment. Findings are graded
CRITICAL / HIGH / MEDIUM / LOW.

## Coverage matrix (requirement -> task)

| FR | Requirement (short) | Task(s) | Covered |
|----|---------------------|---------|---------|
| FR-001 | Generic copy-per-table pack template, composes existing artifacts | T004 | yes |
| FR-002 | Handoff-review checklist as docs, not code | T006 | yes |
| FR-003 | Six required sections each -> existing artifact | T003, T004, T007, T008, T010 | yes |
| FR-004 | Four mandatory caveats (PII/returns/gaps/out-of-scope) | T008, T009 | yes |
| FR-005 | Publish approval recorded in approvals[]; no self-grant | T007 | yes |
| FR-006 | No pass while a prior stage / caveats / recon / approval missing | T006, T007, T016 | yes |
| FR-007 | warning does not auto-promote to pass | T005, T016 | yes |
| FR-008 | No publish / pbi-cli / Fabric | T005, T016 | yes |
| FR-009 | Generic; no worked-example specifics | T015 | yes |
| FR-010 | No fabricated confidence number | T005, T016 | yes |
| FR-011 | Data dictionary matches DEPLOYED schema | T010, T011 | yes |
| FR-012 | ASCII, UTF-8 no BOM, short paths | T015 | yes |
| FR-013 | Wire pack into publish-ready.md + readiness-model.md | T012, T013, T014 | yes |

All thirteen functional requirements map to at least one task. All four user
stories (US1-US4) have implementation tasks and an independent test.

## Success-criteria -> verification mapping

| SC | Verified by |
|----|-------------|
| SC-001 (analyst assembles from existing evidence only) | T016 checklist walk |
| SC-002 (100% sections resolve to an artifact or recorded gap) | T014 cross-link check + T016 |
| SC-003 (checklist FAILS on any missing mandatory item) | T009, T011, T016 |
| SC-004 (no pass without prior stages + approval) | T007, T016 |
| SC-005 (generic + docs conventions) | T015 |
| SC-006 (no publish/pbi-cli/Fabric introduced) | T016 |

## Constitution & hard-rule alignment

| Authority | Verdict | Note |
|-----------|---------|------|
| Principle I (Agent-First, Gate-Enforced) | ALIGNED | Pack is the gate's deliverable; authority stays the existing checks + human approval. |
| Principle II (Depend, Never Fork) | ALIGNED | No pbi-cli touch; F016 stays the later gated adapter. |
| Principle III (Gold-Only) | ALIGNED | Data dictionary keyed to deployed gold only. |
| Principle IV (Mapping Before Silver) | ALIGNED (untouched) | Stage 7 is downstream; pack only references mapping artifacts. |
| Principle V (Agent Stops at Judgment Calls) | ALIGNED | Approval is named human sign-off; PII/rollup/grain/identity recorded, not decided -- see open-for-human. |
| Principle VI (Defaults Then Deviations) | ALIGNED | Caveats compose assumptions.md; no re-derivation. |
| Principle VII (C086 is an example) | ALIGNED | Generic; worked example cited by reference; T015 scans for leakage. |
| Principle VIII (Static-First, Live Deferred) | ALIGNED | Docs-only; recon evidence is referenced retail validate output, no new validator. |
| Principle IX (Secrets & Reproducibility) | ALIGNED | No secrets; ASCII/UTF-8 no BOM; short paths (FR-012). |
| Rule #6 (no pbi-cli before F016) | ALIGNED | FR-008 + agent-must-not block + T016 negative check. |
| Rule #7 (C086 not the schema) | ALIGNED | FR-009 + T015. |
| Rule #8 (docs/templates first) | ALIGNED | Whole slice is docs + checklist. |
| Rule #9 (no fake confidence) | ALIGNED | FR-010 + four explicit statuses. |
| Readiness spine | ALIGNED | Pack = Publish Ready artifact; entered only at dashboard_ready: pass; statuses match readiness-model.md. |

No CRITICAL or HIGH findings. The slice introduces no new gate, no code, and no
publish path; it is consistent with the constitution and every hard rule.

## Findings

### F1 -- Roadmap number vs spec-dir number (LOW, resolved-by-design)

The roadmap lists this as F013 "BI Handoff Pack"; the spec dir is
014-bi-handoff-pack (assigned by the orchestrator to avoid parallel-worktree
collisions). Both refer to the same feature. Every artifact states the mapping
("Roadmap: F013 ... spec dir 014") so a reader is not misled. No change needed;
recorded so a future reconciliation of roadmap numbers vs spec-dir numbers is
deliberate, not an error.

### F2 -- Metric contracts (stage 5) are a forward dependency (LOW, by-design)

The pack's "Metric contracts" required section depends on F009/F010 (Metric
Contract Store), which are not yet built. The spec/plan/tasks handle this
correctly: the section is REFERENCED as an input, and an absent contract store
is recorded as a blocking gap rather than invented (FR-003 + T014 marks it
PLANNED/F009-F010). No fabricated content. Acceptable for a Publish Ready
template that, by definition, is only assembled after stage 5 has passed.

### F3 -- No quickstart.md / data-model.md (LOW, intentional)

The plan omits the optional Phase-0/1 design docs because this is a docs slice
with no code/data model. Consistent with how the other spec-only features in this
repo (002-006) are structured. Not a gap.

### F4 -- Per-table FILLED instance not produced (LOW, intentional)

Only the generic blanks are delivered (Principle VII). A filled instance would be
produced when a real table is handed off. Correctly out of scope.

### F5 -- Same-file task contention flagged (LOW, mitigated)

bi-handoff-pack.md is edited by T004/T005/T007/T008/T010 and the checklist by
T006/T009/T011. The tasks file explicitly marks these SEQUENTIAL (not [P]),
preventing a parallel-edit conflict. Correctly handled.

## Auto-decisions made during the chain (recommended defaults)

1. Pack home = templates/handoff/ (beside other readiness templates).
   Reversible-easy.
2. Pack = docs + checklist, not code (rule #8 / Principle VIII).
   Reversible-easy (a later feature may automate after the artifact proves
   useful).
3. Metric contracts referenced as an input, not built here (stage 5 / F009-
   F010). Reversible-easy.
4. Publish approval recorded in existing readiness-status.yaml approvals[]
   (no new approval store). Reversible-easy.
5. Reconciliation evidence = the existing reconciliation-report.md (no
   re-run). Reversible-easy.

## Open for human (Principle V -- NOT auto-answered)

These are recorded by the pack but MUST be decided by a named human; the chain
deliberately did NOT invent answers:

1. PII publish-safety -- which columns are safe to ship to the consumer (the
   default is drop; governance signs off). The pack records the decision and the
   sign-off; it does not determine safety.
2. Business-rollup / segment mappings -- any value->group rollup surfaced in
   the pack must come from an analyst-supplied mapping, never invented at handoff.
3. Product / grain identity -- the grain and identifying keys the consumer
   relies on are carried from the mapping artifacts and the human decisions
   behind them, not re-decided in the pack.
4. The publish authorization itself -- the data-owner/governance sign-off in
   approvals[] is a human action the agent cannot self-grant.

## Verdict

Status: consistent and ready. All four chain artifacts exist, every FR maps
to a task, every hard rule is satisfied, and the only open items are the
Principle-V human decisions the pack is explicitly designed to record rather than
answer. No CRITICAL/HIGH findings; five LOW findings, all by-design or mitigated.
