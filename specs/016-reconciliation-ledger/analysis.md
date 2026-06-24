# Cross-Artifact Analysis: Reconciliation Ledger (016)

**Date**: 2026-06-24 | **Scope**: spec.md, plan.md, tasks.md for feature 016-reconciliation-ledger
| **Method**: consistency / coverage / constitution-alignment / scope-discipline pass.

## Verdict

**PASS -- no blocking findings.** The three artifacts are internally consistent, every functional
requirement is traced to at least one task, the constitution gates are respected, scope discipline
(Later tier, docs/templates-only) holds, and all cross-referenced files exist. Two items are
deliberately left OPEN for a human (Principle V) and several are explicitly DEFERRED -- both are
recorded, not defects.

## Deterministic checks

| Check | Result |
|-------|--------|
| ASCII-only (no bytes > 127) in spec/plan/tasks | PASS (0 non-ASCII bytes in all three) |
| UTF-8 without BOM | PASS (no BOM in any file) |
| FR coverage: every FR-001..FR-012 cited in tasks | PASS (all 12 mapped) |
| SC present and addressed: SC-001..SC-008 | PASS (all 8 in spec; SC-007/SC-008 enforced by T021/Deferred) |
| Cross-referenced files exist | PASS -- reconciliation-report.md, gold-ready.md, readiness-model.md, readiness-status.yaml, validate.py, roadmap.md, ADR 0002, ADR 0003, c086 worked example all present |
| Spec User Stories (US1/US2/US3) each have task phases | PASS (Phase 3/4/5) |

## Requirement -> task traceability (spot map)

| FR | Covered by |
|----|-----------|
| FR-001 (generic template, ASCII/no-BOM) | T001, T004, T018, T020 |
| FR-002 (entry fields: provenance/per-measure/row-count/verdict) | T004, T005, T006, T007 |
| FR-003 (measured numbers only, no score) | T006, T019 |
| FR-004 (append-only + correction protocol) | T008 |
| FR-005 (fail records measured delta + layer pair; NULL=defect) | T010 |
| FR-006 (pass/fail vocabulary, no warning/score middle) | T007 |
| FR-007 (placement decision, ADR 0003-aligned, concrete path deferred) | T003 |
| FR-008 (history layer; no new validator/gate) | T016 |
| FR-009 (temporal complement; worked example cited not copied) | T016, T017, T018 |
| FR-010 (citable as Gold Ready evidence; gate unchanged) | T013, T014, T015 |
| FR-011 (Later tier: design/template only, no runtime) | enforced by T021 + plan + Deferred |
| FR-012 (no entry when validate did not run) | T012 |

No orphan FRs; no task without a spec anchor.

## Consistency findings (non-blocking)

1. **F015 vs directory 016 (naming).** The roadmap entry for the Reconciliation Ledger is F015;
   this feature's spec directory is 016-reconciliation-ledger (per the assigned feature number).
   The spec states this explicitly ("Roadmap F015 ... Feature Branch 016") and See-also points to
   roadmap F015. Intentional and disclosed -- NOT a contradiction.
2. **F016 (pbi-cli / PBIP Adapter) exclusion.** The task brief deliberately EXCLUDES F016 (hard
   rule #6, gated + last). The spec records the exclusion in See-also. No F016 work appears anywhere.
3. **No research.md / data-model.md / contracts/.** plan.md justifies their omission (no API, no
   schema, no external research for a docs/templates slice). Consistent with scope discipline.
4. **Template filename not yet a created file.** templates/reconciliation-ledger-entry.md is the
   named deliverable of the (future) implement step, not created in this spec/plan/tasks slice.
   Correct: this batch drafts spec+plan+tasks+analysis only.
5. **pass/fail (entry) vs pass/blocked/warning (readiness stage).** The entry verdict is binary by
   design (penny-exact = pass; any cent = fail, #9 + Gold Ready). The readiness STAGE keeps its
   four-value vocabulary; a fail entry maps to a gold_ready blocking reason, a pass entry to
   evidence (FR-006, FR-010). Consistent, not a clash.

## Constitution / hard-rule alignment

- **Principle VIII (static-first, live deferred):** PASS. Adds no validator; records the existing
  retail validate reconciliation result; honors the deferred boundary (no entry when validate did
  not run -- FR-012).
- **Hard rule #4 (no gold -> Power BI before validation):** PASS. The ledger records that
  validation's result durably; it does not weaken or bypass the gate.
- **Hard rule #7 (generic):** PASS. Template is placeholders; C086 cited as filled-instance source,
  never copied (T018, FR-001/FR-009). 0 non-ASCII / pharmacy specifics confirmed.
- **Hard rule #8 (docs/templates first):** PASS. Design + template + examples this slice; runtime
  deferred (FR-011, plan, tasks notes).
- **Hard rule #9 (no fake confidence):** PASS. Every field measured; no score; cent recorded on the
  fail example (FR-003, T019, SC-003).
- **Principle V (agent stops at judgment calls):** RESPECTED. The ledger grain is left OPEN for a
  human; the working default is stated but NOT finalized.

## Open for human (Principle V -- NOT auto-answered)

- **Ledger grain / identity.** Is an entry one-row-per-reconciliation-run (working default) or
  one-row-per-measure-per-run? Is a ledger strictly one-per-table or can tables share one? This is a
  grain/identity decision reserved for a human; the spec adopts one-entry-per-run-per-table only as
  a non-binding working default and flags it as the human decision.

## Deferred (recorded, not built)

- Ledger storage runtime / store (gold table or append-only file + writer).
- retail validate -> ledger auto-append wiring.
- Ledger query / history (drift-over-time) surface.
- Concrete entry storage path + format under mappings/<table>/ (ADR 0003) -- a reversible
  plan/implement-phase decision, flagged for resolution then.

## Auto-decisions made during drafting (recommended defaults)

1. Template-first, runtime deferred (vs build the store now) -- recommended default for a Later-tier
   feature (hard rule #8). Reversible: easy.
2. Template filename templates/reconciliation-ledger-entry.md, sibling of reconciliation-report.md.
   Reversible: easy.
3. Examples inline in the template (vs separate example files). Reversible: easy.
4. Per-table placement under mappings/<table>/ (ADR 0003) for the eventual store; concrete
   path/format deferred. Reversible: easy.
5. Binary pass/fail for the reconciliation number (penny-exact = pass) -- consistent with #9 and the
   Gold Ready gate. Reversible: costly (load-bearing but aligned with an existing gate).
6. No constitution amendment assumed required -- the ledger adds no gate/principle; raised in
   implement if warranted. Reversible: easy.

## Recommendation

Proceed to the implement step (author templates/reconciliation-ledger-entry.md + two example
entries + the gold-ready.md evidence note per tasks.md). Carry the one OPEN human decision (ledger
grain) into that step as a stop-and-ask, and keep the changed-file set docs/templates-only (SC-007).
