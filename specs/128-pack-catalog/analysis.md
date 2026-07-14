# Cross-Artifact Analysis: Public Extension-Pack Catalog (128)

**Date**: 2026-07-14 | **Artifacts**: spec.md, plan.md, tasks.md | **Mode**: non-destructive cross-artifact consistency (speckit-analyze)

This is the fourth required Spec-Kit chain artifact (specify -> plan -> tasks -> analyze). It records the cross-artifact consistency pass so the downstream implement workflow's handoff preflight finds it.

**Scope**: Consistency, coverage, and constitution alignment across the three authored artifacts, cross-checked against the SHIPPED extension-pack system (src/seshat/packs/, schemas/seshat-extension-pack.schema.json, the pack CLI verb group) and .specify/memory/constitution.md v1.7.0.

## Summary

The three artifacts are internally consistent and align with the shipped code and the constitution. Two MEDIUM coverage gaps were found during the pass (FR-018 and SC-009 had no tagged task) and were remediated in place by extending task T022 and adding task T037. No CRITICAL or HIGH finding remains. The feature is correctly scoped as the discovery/retrieval layer spec 120 US5 explicitly deferred, and it does not step on the shipped "no install/activate verb by design" posture.

## Coverage matrix (post-remediation)

Every functional, reuse, and success item maps to at least one task.

| Item | Task(s) | Status |
|------|---------|--------|
| FR-001 static git registry | T003, T007, T032 | covered |
| FR-002 required record fields | T001, T005 | covered |
| FR-003 new index schema, not a rival pack format | T001, T007 | covered |
| FR-004 search reads metadata only | T009, T010 | covered |
| FR-005 search display fields | T009, T010 | covered |
| FR-006 inspect full record | T014, T015, T017 | covered |
| FR-007 strict flow order | T007, T023, T029 | covered |
| FR-008 hash verify before add | T019, T024, T031 | covered |
| FR-009 reuse existing validation | T021, T025 | covered |
| FR-010 fail closed on every class | T020, T023, T025, T029 | covered |
| FR-011 no auto-activation | T022, T026 | covered |
| FR-012 no hidden global state | T004, T022, T026 | covered |
| FR-013 no readiness/approval grant | T022, T026, T027 | covered |
| FR-014 declarative only, enforced by reused validation | T020, T025 | covered |
| FR-015 categorical verification state, no score | T005, T027, T033 | covered |
| FR-016 no runtime self-grant of review state | T027 | covered |
| FR-017 preserve attribution, distinct from owner | T012, T017, T034 | covered |
| FR-018 read-only except explicit local add | T022, T037 | covered (remediated) |
| FR-019 disclosure-safe findings | T006, T020, T029 | covered |
| FR-020 duplicate record = defect | T005, T008 | covered |
| FR-021 empty/absent registry works | T006, T021 | covered |
| FR-022 no silent overwrite | T020, T026 | covered |
| RR-001 reuse single+selection validation | T021, T025 | covered |
| RR-002 reuse pack content schema | T025 | covered |
| RR-003 reuse containment guard | T023 | covered |
| RR-004 reuse disclosure scan | T021, T025 | covered |
| RR-005 reuse JSON-contract validator on new index | T002, T007 | covered |
| RR-006 extend pack verb group, not a parallel surface | T011, T016, T028, T036 | covered |
| SC-001 search shows fields, fetches nothing | T013 | covered |
| SC-002 inspect full record | T018 | covered |
| SC-003 tamper refused 100% | T030, T031 | covered |
| SC-004 incompatible/missing/etc refused 100% | T031 | covered |
| SC-005 verdict from existing validator | T021 | covered |
| SC-006 no side effect after add | T022, T030 | covered |
| SC-007 attribution intact | T034 | covered |
| SC-008 no numeric state anywhere | T033 | covered |
| SC-009 fully offline | T037 | covered (remediated) |

Every user story (US1 search, US2 inspect, US3 fetch/verify/add) has both acceptance scenarios in spec.md and a dedicated task phase (Phases 3, 4, 5) with tests preceding implementation.

## Findings

| ID | Severity | Location | Finding | Disposition |
|----|----------|----------|---------|-------------|
| A1 | MEDIUM | tasks.md | FR-018 (read-only w.r.t. external systems; only the explicit add writes, and only local content) had no tagged task; the no-side-effect test T022 covered activation/readiness but not the DB/publish/PBI-write dimension. | REMEDIATED: T022 extended to assert no database write, Power BI modification, or publish; the only write is local workspace content. |
| A2 | MEDIUM | tasks.md | SC-009 (the catalog is fully exercisable offline against a checked-out static registry) was asserted in the plan's testing note but had no dedicated task. | REMEDIATED: added T037, an offline-guarantee integration test (no socket, no driver import) covering FR-001, FR-018, SC-009. |
| A3 | LOW (resolved by design) | spec.md vs shipped code | The shipped pack system states "no install/activate verb by design" (parser_ecosystem.py) and "constructing a selection installs nothing and persists nothing" (model.py); this feature adds an add verb and a registry. Potential contradiction. | NOT A DEFECT: reconciled in spec Clarification 2 and FR-011/FR-012 -- add fetches verified content into the workspace as a reviewable committed change; it writes NO activation state and promotes NO readiness. Verified the spec's add description does not read as an install/activate lifecycle. |
| A4 | LOW (resolved by design) | plan.md vs anti-reinvent rule | The plan introduces a NEW schema (seshat-pack-registry.schema.json). Risk of being read as a second pack format. | NOT A DEFECT: FR-003 + RR-002 + Complexity Tracking state explicitly that the index schema is metadata ABOUT packs and that pack CONTENT continues to use the unchanged seshat-extension-pack.schema.json with the unchanged validators. Required because Requirement-2 fields (source, hash, verification_state, author) do not exist on PackManifest. |

## Consistency checks

- **Terminology**: verification_state (registry field), verification state (prose), owner (pack content author on the manifest) vs author (registry contributor) are used consistently and kept distinct in all three artifacts (FR-017). No drift.
- **Flow order**: The search -> inspect -> fetch -> verify hash -> verify schema -> existing validation -> explicit add sequence in FR-007 matches the plan's fail-closed chain (Phase 0 decision 4) and the task order (Phases 3 to 5 and T023 to T024 to T025 to T026). Consistent.
- **Fail-closed mapping**: Every refusal class in FR-010 maps to a reused component in the plan and to a test in T020. No refusal class is unmapped.
- **No-score / no-self-grant**: FR-015/FR-016 (verification state categorical + human-authored) are consistent with the hard-stops and with T027/T033. No numeric score appears anywhere.
- **Anti-reinvent**: No task modifies model.py, loader.py, validator.py, scaffold.py, or the pack content schema (stated explicitly in the tasks' Dependencies note). Consistent with RR-001..RR-006 and Principle II.

## Constitution alignment (v1.7.0)

Re-confirmed the plan's Constitution Check table. No principle is violated: Principle II (reuse, no fork) and Principle VIII (static-first: a reviewed git registry, offline, no hosted service) are actively reinforced; Principle V and the two hard-stops are honored by keeping verification state human-authored and readiness untouched. No Complexity Tracking entry is required.

## Human-owned decisions (Principle V)

None. This is a distribution/tooling feature; none of the genuine Principle V categories arise:

- **Grain / PII publish-safety / business-rollup / product-identity**: not touched -- the catalog moves declarative pack metadata and content, not source data or business mappings.
- **author / attribution**: software authorship of a pack, NOT data-domain product-identity; auto-decided (registry contributor preserved alongside the manifest owner).
- **Who grants reviewed state**: dictated by the hard-stop never_self_grant_approval (a named human commits it to the registry; the tool never grants it) -- an auto-decision citing the hard-stop, not an open question.

open_for_human is therefore empty for this feature.

## Result

PASS. All four chain artifacts (spec, plan, tasks, this analysis) exist and are consistent. Two MEDIUM coverage gaps found and remediated in place. Chain is spec-only; the implement step remains owner-gated.