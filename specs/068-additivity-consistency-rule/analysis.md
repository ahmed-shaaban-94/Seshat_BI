# Cross-Artifact Analysis: Additivity-Consistency Lineage Rule

**Scope**: read-only consistency pass over spec.md, plan.md, tasks.md (and the Phase 0/1
design artifacts). No artifact was modified by this analysis.

## A. Requirement -> Task -> Success-Criterion coverage

| Requirement | Covered by task(s) | Success criterion |
|-------------|--------------------|-------------------|
| FR-001 clone AL1 scaffold, generic glob, lazy import, exemptions, fail-loud | T001, T004 | SC-005 |
| FR-002 categorical ERROR only, no score | T004, T013 | SC-005 |
| FR-003 no execution (no DAX/connection/visual) | T004, T013 | SC-005 |
| FR-004 exact closed words; absent/ambiguous ERRORs, never infer | T005, T006 | SC-003 |
| FR-005 surface only; never resolve/invent/re-classify | T004, T006, T013 | SC-003, SC-005 |
| FR-006 closed generic legality table; no worked-example names/ids/paths | T004, T013 | SC-002, SC-005 |
| FR-007 off-spine; advances no stage | plan Constitution Check; no task claims a stage | (no stage SC by design) |
| FR-008 five-place wiring; count +1 | T007, T008, T009, T010, T011 | SC-004 |
| FR-009 read the define-layer prose corpus; assume no machine-readable field | T004 | SC-001, SC-002 |
| FR-010 empty/edge corpus -> zero findings, no error | T012 (baseline); edge cases in spec | SC-001 |
| FR-011 (OPEN, Principle V) metric identity across corpora | tasks Out-of-scope | n/a (left open) |
| FR-012 (OPEN, Principle V) legality matrix ratification | tasks Out-of-scope | n/a (left open) |

Result: every buildable FR (001-010) maps to at least one task AND one success criterion.
FR-011/FR-012 are intentionally OPEN and are explicitly excluded in tasks Out-of-scope --
consistent, not a gap.

## B. User-story -> task coverage

- US1 (illegal composition ERROR, P1) -> T003, T004. Acceptance US1.1-US1.3 all asserted in
  T003. COVERED.
- US2 (absent/ambiguous refused, P1) -> T005, T006. Acceptance US2.1-US2.2 asserted in T005.
  COVERED.
- US3 (wired + counted, P2) -> T007-T011. Acceptance US3.1 asserted in T011. COVERED.

No user story lacks a task; no task is orphaned from a story/requirement.

## C. Consistency / contradiction checks

- Corpus decision is consistent across spec (Clarifications Q2, FR-009), plan (Summary,
  Scope), research (R2), data-model, contract, and tasks (T004): all say READ the define-
  layer prose corpus via a generic glob; none reads the deployable per-table YAML for
  additivity. No contradiction.
- Count target is consistently "current + 1" and explicitly NOT hardcoded (research R4,
  tasks T001/T009). Spec/plan note the count stands at 44 at spec time -> 45, but the build
  reads the live count. Consistent.
- Principle-V stance is consistent everywhere: surface-only, never resolve/infer/re-classify
  (spec FR-004/FR-005, plan Constitution Check, data-model invariants, contract invariants,
  tasks T006/T013). No artifact asks the rule to make an owner ruling.
- Off-spine / no-stage is consistent (spec FR-007, plan, Clarifications Q3). No artifact
  claims a readiness-stage advance or self-grants approval.

## D. Constitution / rules pass (informational, cross-checked)

- Static-First + never-execute: asserted FR-003, plan gate, contract invariant, T013 check.
- No-Fake-Confidence: asserted FR-002, T013.
- C086-Is-An-Example: generic glob + generic table, no worked-example names/ids/paths;
  asserted FR-006, plan gate, T013.
- ASCII/UTF-8-no-BOM: authored artifacts use -- and ->; T013 verifies new source files.

## E. Findings

- CRITICAL: 0
- HIGH: 0
- MEDIUM: 0
- LOW: 2 (informational)
  - L1: The exact rule id is deferred to T002 rather than fixed in the spec. Intentional
    (avoids colliding with any rule that lands first) and does not block; noted for
    transparency.
  - L2: FR-011 (cross-corpus identity) is OPEN but the chosen single-corpus scope (Q2) means
    the rule does not need it on day one; it becomes load-bearing only if a future change
    asks the rule to reconcile the two corpora. Consistent, but a human should note it when
    ratifying so a later scope creep does not silently depend on an unresolved ruling.

## Verdict

analyze_verdict: clean (0 critical, 0 high). The two LOW items are informational and do not
require a spec change before ratification.
