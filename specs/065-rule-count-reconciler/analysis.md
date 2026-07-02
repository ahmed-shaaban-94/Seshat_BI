# Cross-Artifact Analysis: Rule-Count Claim Reconciler (SC2)

**Stage**: 5 (/speckit-analyze) -- READ-ONLY consistency pass over spec.md,
plan.md, tasks.md (+ research.md, data-model.md, contracts/, quickstart.md).

**Date**: 2026-07-02

**Scope**: This pass checks internal consistency (requirement -> task coverage,
terminology, count arithmetic, principle alignment, duplication, ambiguity). It
does not build anything and edits no artifact except this file (repo convention).

## Inventory

- Functional requirements: FR-001 .. FR-019 (19).
- Success criteria: SC-001 .. SC-006 (6).
- User stories: US1 (P1, stale count), US2 (P1, per-entry fail-loud), US3 (P2, bad
  manifest/count source + wiring).
- Tasks: T001 .. T024 (24), grouped into 6 phases and mapped to US1/US2/US3.
- Live base rule count N = 43 (confirmed: docs/rules/rules-manifest.json has 43
  entries; EXPECTED_RULE_IDS matches). Post-SC2 count = 44. Spec/plan/tasks refer
  to the count as N / N+1 abstractly and never hardcode 43/44 -- consistent with
  SC2's own anti-drift charter.

## Requirement -> task coverage

| Requirement | Covered by | Status |
|-------------|-----------|--------|
| FR-001 (registered SC2, ERROR, enforced) | T006, T007, T016, T023 | covered |
| FR-002 (manifest path, parse-on-run) | T006, T007 | covered |
| FR-003 (manifest shape + record fields) | T003 (fixture), T007, data-model | covered |
| FR-004 (missing/untracked manifest -> ERROR) | T012, T007 | covered |
| FR-005 (malformed/wrong-shape manifest -> ERROR) | T012, T007 | covered |
| FR-006 (count source via stdlib json; fail loud; no rules-package import) | T007, T013, plan | covered |
| FR-007 (untracked doc -> ERROR) | T010, T011 | covered |
| FR-008 (absent anchor -> ERROR) | T008, T011 | covered |
| FR-009 (malformed/missing claimed-count -> ERROR) | T009, T011 | covered |
| FR-010 (mismatch -> ERROR naming both integers; match -> none) | T004, T005, T007 | covered |
| FR-011 (missing field -> ERROR) | T010, T011 | covered |
| FR-012 (finding shape: id/ERROR/message/locator) | T006, contract | covered |
| FR-013 (strictly categorical, no score) | T006, contract INV-2, T024 | covered |
| FR-014 (no module-scope DB/network/rules import; lazy yaml; stdlib json) | T006, T014, INV-3, SC-005 | covered |
| FR-015 (5-place wiring; N->N+1) | T014, T015, T016, T020 | covered |
| FR-016 (generic-only) | T003, T019, T024 | covered |
| FR-017 (live-state-only; dated snapshots excluded) | T019, research D4 | covered |
| FR-018 (seed defect + same-change glossary fix to N+1) | T017, T018, T019 | covered |
| FR-019 (unit tests across all fault classes) | T003-T013, T021 | covered |

Every FR maps to at least one task. Every SC maps to a task or gate step
(SC-001->T004; SC-002->T004-T013; SC-003->T016/T020; SC-004->T024/INV-2;
SC-005->T024 + never-execute rule; SC-006->T017-T021/T023).

## Consistency checks

- **Count arithmetic**: spec FR-018, plan, research D3/D5, quickstart step 7, and
  tasks T017-T019 all agree the seed target is the POST-SC2 count (N+1), justified
  by SC2 itself incrementing the registry. No artifact hardcodes 43 or 44.
  CONSISTENT.
- **Count source**: spec FR-006/FR-014, plan, research D1, data-model, contract
  INV-3, quickstart all agree on docs/rules/rules-manifest.json + stdlib json, no
  rules-package import. CONSISTENT (no contradicting alternative left live).
- **Anchor semantics**: spec (edge cases, Out of Scope), data-model, contract
  INV-5, research D2 all agree the reconciled integer is the manifest claimed-count
  and the anchor is a presence check only. CONSISTENT.
- **Terminology**: "authoritative count", "claimed-count", "anchor", "manifest",
  "live-state" used uniformly. Rule id "SC2" + title match across plan, contract,
  quickstart, tasks T007/T015.
- **Off-spine placement**: spec Q5 + Assumptions, plan Constitution Check, research
  D6, tasks T022 all record SC2 off-spine with no self-assigned F-number/stage.
  CONSISTENT and Principle-V-safe.
- **Fail-loud coverage**: contract steps 1-4 enumerate every bad-input class; each
  has a test task (T008-T013) and an implementation task (T007/T011). No class can
  return a vacuous [].

## Duplication / over-scope check

- No duplicated requirement. FR-004/FR-005 (manifest guards) vs FR-006 (count-source
  guard) are distinct sources; not redundant.
- No task builds a deferred capability (no DB, no F016 adapter, no F031-F033
  runtime). No task adds a family-count check or a coverage rule -- both explicitly
  out of scope. No over-scope detected.

## Ambiguities / residual notes (non-blocking)

- **A-1 (low)**: The exact glossary anchor sentence is chosen at implement time
  (T018 -> T019). Intentional (the anchor must be byte-identical to the corrected
  wording), not an unresolved ambiguity; the tasks pin the dependency order so the
  manifest anchor cannot drift from the doc.
- **A-2 (low)**: docs/rules/rules-manifest.json is both the golden snapshot
  regenerated in T020 AND SC2's count source. Ordering (regen T020, live guard T021)
  is correct: the count source must contain SC2 (length N+1) before the live guard
  runs, else the seed claimed-count: N+1 would not reconcile. Tasks make the
  dependency explicit; noted so the implementer does not reorder.
- **A-3 (low)**: Base count N is stated as 43 here for narrative, but the authored
  spec/plan/tasks keep it symbolic. This is a feature, not an inconsistency -- it
  prevents the plan from becoming a stale-count claim.

## Verdict

- **Critical findings**: 0
- **High findings**: 0
- **Low/advisory notes**: 3 (A-1, A-2, A-3), all intentional and non-blocking.

All 19 FRs and 6 SCs are task-covered; the count arithmetic, count-source, and
anchor-semantics decisions are internally consistent across all artifacts; no
deferred capability is assumed; no C086 leak; no fabricated confidence. Result:
CLEAN (0 critical / 0 high).
