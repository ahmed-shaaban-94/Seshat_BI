# Specification Analysis Report: Stale-Marker Sweep / Status-Claim Reconciler (SC1)

**Scope**: Cross-artifact consistency over spec.md, plan.md, tasks.md (with
research.md, data-model.md, contracts/sc1-rule-contract.md, quickstart.md) against
the constitution. READ-ONLY pass. Generated 2026-06-30 (stage 5, /speckit-analyze).

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Constitution Alignment | LOW | spec/plan/tasks | SC1 reads committed text (manifest + each claiming doc) + the tracked-files set, executes nothing, opens no connection, stdlib-only core import path (lazy yaml, stdlib substring anchor check). Aligns with Principle VIII + never-execute invariant. | None -- compliant. |
| C2 | Constitution Alignment | LOW | spec FR-016, plan Constitution Check, tasks T020 | Generic-only mandate (Principle VII) stated in all three artifacts and enforced by a final leak-sweep task. Seed entry uses generic repo-infrastructure paths, not a worked-example value. | None -- compliant. |
| C3 | Constitution Alignment | LOW | spec FR-012, data-model invariant 3, plan Hard-rule-9 line | No-fake-confidence (Hard rule 9): SC1 is strictly categorical; data-model and plan both forbid any numeric value; SC-004 verifies it. | None -- compliant. |
| F1 | Inconsistency | LOW | spec FR-003 vs research D4 | Spec FR-003 names the per-record fields; research D4 fixes the top-level key as `claims`. Consistent and more specific; contract + data-model agree. | None. |
| F2 | Inconsistency | LOW | spec FR-011 vs contract message strings | Spec leaves messages descriptive ("human-readable"); the contract pins concrete wording. Consistent (contract is the more specific binding). | None. |
| U1 | Underspecification | LOW | spec edge case "anchor matches more than once" | Multiple anchor matches treated as present (presence-only). Deliberately under-pinned (no positional matcher, by design -- research D2). | Acceptable; narrows false-positive surface. |
| U2 | Underspecification | LOW | spec Out of Scope (completeness) | Manifest-completeness drift gap is named and ACCEPTED (Q2), no coverage rule built. Mirrors A1-before-A3. | Acceptable; future sibling idea may add coverage. |
| M1 | Coverage | LOW | FR-001..FR-018, SC-001..SC-005 | Every buildable FR and SC maps to >=1 task (see Coverage Summary). | None. |
| B1 | Baseline consistency | INFO | spec FR-015/SC-003, plan Scale, tasks T002/T013, research | All artifacts agree the live EXPECTED_RULE_IDS baseline is 35 ids -> 36 with SC1, and explicitly CORRECT the idea-bank's stale "33/34" baseline. Verified against the live wiring test (35 ids today). | None -- internally consistent, ground-truth-correct. |
| V1 | Principle V | INFO | spec ## Clarifications "Deferred to human ruling" | SC1 surfaces NO grain/PII/rollup/identity question; the section is explicitly empty. Three build-relevant ambiguities were advisor-resolved on reversible defaults, none a Principle-V ruling. | Confirm at ratify; not a build blocker. |
| S1 | Seed-defect reality | INFO | spec FR-017, tasks T015/T016 | The one seed defect is verified real: net-sales trace is tracked + shipped (roadmap stage 2, PR #72) while capability-state doc calls it "(planned)". Plan fixes the prose in the same change so SC1 ships GREEN. | None -- grounded. |

## Coverage Summary

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| FR-001 (registered enforced ERROR rule) | Yes | T006, T007, T012, T013 | |
| FR-002 (fixed manifest path, lazy parse) | Yes | T007 | lazy yaml |
| FR-003 (manifest schema: claims + 5 fields) | Yes | T003, T007, T015 | |
| FR-004 (manifest missing/untracked -> ERROR) | Yes | T009, T007 | |
| FR-005 (malformed/wrong-shape -> ERROR) | Yes | T009, T011 | |
| FR-006 (doc untracked -> ERROR) | Yes | T010, T011 | |
| FR-007 (anchor presence via repo_root) | Yes | T010, T011 | substring |
| FR-008 (built + missing artifact -> ERROR) | Yes | T008, T011 | |
| FR-009 (planned + present -> ERROR; absent -> none) | Yes | T004, T005, T007 | MVP |
| FR-010 (invalid/missing field -> ERROR) | Yes | T010, T011 | |
| FR-011 (finding shape SC1/ERROR/msg/locator) | Yes | T006, T007, T011 | |
| FR-012 (strictly categorical, no number) | Yes | T006, T020 | |
| FR-013 (no module-scope DB/net; lazy yaml) | Yes | T006, T007, T020 | |
| FR-014 (self-register via decorator) | Yes | T006, T012 | |
| FR-015 (EXPECTED_RULE_IDS 35->36 same change) | Yes | T013, T014 | |
| FR-016 (generic, no C086 in rule/seed) | Yes | T015, T020 | leak sweep |
| FR-017 (seed defect + fix prose same change) | Yes | T015, T016 | |
| FR-018 (unit tests cover 8 enumerated cases) | Yes | T004-T005, T008-T010 | |
| SC-001 (seeded stale-planned -> non-zero + names doc/artifact) | Yes | T004, T015, T019 | |
| SC-002 (all contradiction classes ERROR; honest -> zero) | Yes | T004-T011 | 8 cases |
| SC-003 (wiring test passes; set has SC1; count 36) | Yes | T013, T014 | |
| SC-004 (zero numeric values in findings) | Yes | T020 | |
| SC-005 (no DB/network/PowerBI access) | Yes | T006, T017, T019 | |

Coverage: 23/23 requirement+SC keys have >=1 task (100%).

## Constitution Alignment Issues

None. Principles I, V (carve-out empty -- no Principle-V question arises), VII,
VIII, IX, and Hard rule 9 are each addressed by the plan's Constitution Check and
reflected in tasks. The seed-fix ship-green discipline avoids landing an enforced
ERROR rule RED on main.

## Unmapped Tasks

None lacking purpose. T001/T002 are read-only setup (by design); T003 is the US1
test harness; T016 is the in-same-change prose fix paired with seed T015; T017 is
the live guard; T018 the roadmap ledger row; T019 the gate run; T020 the leak sweep.

## Metrics

- Total Functional Requirements: 18 (FR-001..FR-018)
- Total Success Criteria (buildable): 5 (SC-001..SC-005)
- Total Tasks: 20 (T001..T020)
- Coverage: 100% (every FR and SC has >=1 task)
- Ambiguity Count: 0 open [NEEDS CLARIFICATION] markers (3 resolved; 0 Principle-V deferrals)
- Duplication Count: 0
- Critical Issues Count: 0
- High Issues Count: 0

## Verdict

No CRITICAL and no HIGH findings. All findings are LOW/INFO and compliant. Artifacts
are internally consistent; the 35->36 baseline is ground-truth correct (and corrects
the idea-bank's stale 33/34 assumption); the single seed defect is verified real and
is fixed in the same change so SC1 ships GREEN. No Principle-V question arises. Ready
for the adversarial plan-review stage, then the human ratify gate.

## Next Actions

- No remediation required before ratification.
- At ratify, a human may flip any of the three reversible Clarifications defaults
  (Q1 seed-fix sequencing, Q2 completeness-gap acceptance, Q3 off-spine placement);
  each is recorded and changes are localized.
