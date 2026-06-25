# Specification Analysis Report -- F029 dbt Transformation Adapter

**Artifacts**: `spec.md`, `plan.md`, `tasks.md` (+ constitution v1.6.0)
**Mode**: read-only cross-artifact consistency pass (post-clarify, Session 2026-06-25)
**Scope note**: planning-only slice -- "tasks" are author/confirm/enumerate verbs over the
five spec-kit files, NOT buildable runtime code (FR-011, SC-005). Coverage maps to spec
sections, not source files.

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| I1 | Inconsistency | MEDIUM | tasks.md:T005,T013,T136-137 vs spec.md FR-007/SC-002/US4 | tasks.md says "three parity assertions (row count, transaction_id distinct, additive sum within tolerance)"; the clarified spec now states FOUR (adds per-dimension distinct row counts) and exact-to-the-cent tolerance (`<= 0.01`). | Refresh tasks.md T005/T013/T015 wording to "four assertions" + the cent tolerance on a follow-up edit; flagged for ledger -- not rewritten in this read-only pass. |
| I2 | Inconsistency | MEDIUM | tasks.md:T015 vs spec.md Deferred decisions | T015 says the tolerance is "listed under Deferred decisions for human confirmation"; the spec moved it to Resolved (clarified 2026-06-25, still owner-confirmable). | Update T015 to "confirm tolerance is recorded as a resolved default (cent-level), still owner-confirmable" on follow-up. |
| C1 | Coverage Gap | MEDIUM | plan.md Phase 1 + tasks.md US4 | The clarified FR-006 adds two new rules -- migration files RETAINED as parity oracle/rollback after a switch, and parity RE-RUNS on every dbt build while the oracle is retained. plan.md Phase 1 design + tasks T013/T014 do not yet enumerate either. | Add a one-line plan.md note (ADR records retain-not-delete + re-run cadence) and a tasks confirm-line; flagged for ledger. Spec is internally complete (FR-006, US4 sc.3/sc.4, Forbidden ops, Human approval boundary all cover it). |
| D1 | Pre-existing tension (noted, not introduced) | LOW | plan.md:151-160; migration 0004 line ~89 | dim_date_rss carries a -1 member that S8 flags; F029 reproduces committed gold as-is. New per-dimension-count parity assertion (FR-007) will COUNT that -1 date member -- consistent with "reproduce as committed". | None. Correctly scoped out (16110d8 split-brain); if S8 is later fixed, the dbt mart follows the migration and the parity count follows with it. |

## Coverage Summary (requirement -> task)

| Requirement | Has Task? | Task IDs | Notes |
|-------------|-----------|----------|-------|
| FR-001 entry gate | Yes | T003, T006, T007 | Mapping Ready=pass refusal pinned + confirmed in spec/plan. |
| FR-002 map citation | Yes | T008, T009 | Per-model source-map citation; planned model-contract template. |
| FR-003 no Principle V auto-resolve | Yes | T010, T012 | Stop-and-ask list + forbidden ops. |
| FR-004 evidence-not-approval | Yes | T004, T010, T011 | Governance hinge pinned verbatim. |
| FR-005 first-MVP model+tests | Yes | T014 | One staging + one mart + basic tests enumerated. |
| FR-006 optional-alt + parity + RETAIN + re-run | Partial | T005, T013 | Optional-alt/parity covered; NEW retain + re-run rules not yet in tasks (C1). |
| FR-007 parity assertions (now four) | Partial | T005, T013, T015 | Tasks still say three assertions / tolerance-deferred (I1, I2). |
| FR-008 no secrets | Yes | T018 | Only profiles.example.yml committed. |
| FR-009 DB-connected, not publish | Yes | T010, T012 | Stops at gold; F016 disjoint. |
| FR-010 auto-update policy | Yes | T011, T019 | Pin dbt-core+dbt-postgres; no automerge minor/major. |
| FR-011 zero dbt files this slice | Yes | T016 | Diff check. |
| FR-012 generic artifacts | Yes | T017 | Zero retail_store_sales leak into generic templates. |
| SC-001 entry-gate unambiguous | Yes | T006 | -- |
| SC-002 parity concrete (now four) | Partial | T013, T015 | Tasks count drift (I1). |
| SC-003 no green-test self-pass | Yes | T010, T012 | -- |
| SC-004 zero C086 leak | Yes | T017 | -- |
| SC-005 zero dbt/runtime files | Yes | T016 | -- |
| SC-006 no-secrets reviewable | Yes | T018 | -- |
| SC-007 auto-update explicit | Yes | T019 | -- |

## Constitution Alignment

No constitution MUST is violated. Principle IV (entry gate), V (stop-and-ask, no
auto-resolve), VI (defaults-then-deviations -- migrations default; retain-on-switch
strengthens this), VII (generic), VIII (planning-only), IX (no secrets, ASCII/no-BOM) all
hold. The clarifications strengthen VI (retain the migration oracle, re-run parity) rather
than weaken any gate. No CRITICAL, no HIGH.

## Unmapped Tasks

None. Verification tasks (T016-T021) map to SC-004/005/006/007 + Principle IX. Setup tasks
(T001-T002) are reference-reads supporting the parity target + house style.

## Metrics

- Total Requirements: 19 (FR-001..FR-012 = 12; SC-001..SC-007 = 7)
- Total Tasks: 21 (T001-T021)
- Coverage (requirements with >=1 task): 19/19 = 100% (3 of them Partial pending the I1/I2/C1 refresh)
- Ambiguity Count: 0 (the three material ambiguities were resolved in clarify Session 2026-06-25)
- Duplication Count: 0
- Critical Issues: 0
- High Issues: 0

## Verdict

**findings** -- 0 CRITICAL, 0 HIGH; 3 MEDIUM + 1 LOW. All MEDIUMs are expected
post-clarify refinement drift between the now-sharper spec (four parity assertions, cent
tolerance, migration retention, re-run cadence) and the unchanged plan/tasks. They are
flagged for the ledger, NOT auto-fixed (plan/tasks rewrite is out of scope for this
read-only pass and for an idempotent finish that must not silently rewrite approved
artifacts).

## Next Actions

- No CRITICAL/HIGH: the chain may proceed; `/speckit-implement` is not in scope (this is a
  planning-only slice that ships no code).
- Recommended follow-up (separate, explicit edit -- not this read-only pass): refresh
  tasks.md T005/T013/T015 to "four parity assertions + cent tolerance (resolved default)"
  and add a plan.md/tasks line for the migration-retention + parity-re-run rules (I1, I2,
  C1).
