# Cross-Artifact Analysis: 127-showcase-build

**Date**: 2026-07-14 | **Scope**: spec.md, plan.md, tasks.md, research.md, data-model.md, contracts/showcase-contract.md

Non-destructive /speckit-analyze-style consistency pass. No artifact was
rewritten by this analysis; findings below are advisory and, where actioned, the
action is noted.

## A. Requirement -> Task coverage

Every functional requirement maps to at least one task; every user story has a
test-first task set. Verified mapping:

| FR | Covered by | Notes |
|----|-----------|-------|
| FR-001 (read projection, no recompute) | T004, T011 | Reuse-only. |
| FR-002 (no new engine/schema) | T004, T021, T026 (all reuse) | Enforced by the Reuse Map. |
| FR-003 (missing/defect/deferred, no false pass) | T009, T011 | INV-1. |
| FR-004 (read-only) | T004, T010 | INV-6. |
| FR-005 (skill, no CLI verb) | T002, T007, T034 | T007 guard test. |
| FR-006 (contained local output) | T006 | resolve_local_output. |
| FR-007/008 (offline/self-contained) | T005, T008 | |
| FR-009/010 (fail-closed disclosure) | T006, T020 | INV-4. |
| FR-011 (no approval/publish) | T006, T034 | |
| FR-012/013/015 (truthful badge) | T013, T014, T016 | INV-2. |
| FR-014 (offline badge) | T015, T016 | |
| FR-016/017/018 (four-category manifest) | T018, T021, T023 | INV-3. |
| FR-019 (path/URL normalization -> redacted) | T019, T022 | |
| FR-020/021 (before/after only when comparable) | T024, T025, T026, T027 | INV-5. |
| FR-022 (spec-102 a11y) | T028, T031 | |
| FR-023/024 (responsive/RTL) | T029, T031, T032 | |
| FR-025 (explorer assets untouched) | T010, T030, T031 | INV-6. |
| FR-026/027 (no fabricated fact; local-snapshot note) | T012, T033 | |

Every SC (SC-001..008) has a corresponding test task (T008-T010, T013-T015,
T018-T020, T024-T025, T028-T030). No orphan FR; no orphan task.

## B. Consistency (spec <-> plan <-> tasks)

- Delivery shape consistent across all three: skill over a library function, no
  CLI verb (spec FR-005 / clarification, plan Technical Context + Structure
  Decision, tasks T002/T007). No contradiction.
- Fail-closed vs redacted consistent: spec clarification + FR-009/010/016/019,
  plan R2, research R2, tasks T020/T022. "Redacted" = portability normalization
  only; live findings block. No contradiction.
- Reused symbols all verified to exist as named: build_explorer_projection,
  render_explorer_html, build_passport, verify_passport (with
  schema_version/source_revision/scope), resolve_local_output, scan_disclosure,
  blocker_explainer.py, approval_inbox.py, rules/design_contrast.py,
  rules/design_categorical_distinctness.py. Option-B claim verified: _DISPATCH
  has no "showcase" key.
- Entity vocabulary consistent between data-model.md and spec Key Entities
  (ShowcaseBundle, Badge, DisclosureManifest, Comparison, TableView). Contract
  signatures match plan Phase 1 and data-model.

## C. Constitution alignment

- Principle V (judgment/approval/PII/publish): the one seam that could look like
  a Principle-V decision -- "does producing the bundle grant publish/PII
  sign-off?" -- is answered NO and recorded (bundle is local; sharing is a
  separate human action). No grain/rollup/identity decision arises in a pure
  rendering layer. Nothing auto-cleared that should be human-owned.
- Readiness spine "never a fabricated confidence number": badge is a stage
  summary, not a score (FR-013, INV-2, T013). Aligned.
- Principle VIII (static-first, live deferred): deferred live checks render as
  unavailable (FR-003); no live DB added. Aligned.
- Principle IX + hard rules: fail-closed disclosure, ASCII/UTF-8-no-BOM,
  contained local output, short paths. Aligned.
- Option B (ratified 2026-07-07): honored; the pre-ratification
  explorer/passport verbs are grandfathered, not precedent for a new verb.

## D. Ambiguities / underspecification (resolved by auto-answer, recorded)

1. Verb vs skill -> skill (Option B). Recorded as auto_decision.
2. Redact vs block on live findings -> block fail-closed; redacted =
   portability normalization. Recorded.
3. "valid comparable snapshots" -> same schema+scope, differing revision.
   Recorded.
4. Producing the bundle != publish sign-off. Recorded (Principle-V-adjacent,
   auto-answered NO because the bundle is local; NOT a publish decision).

No open [NEEDS CLARIFICATION] markers remain in spec.md.

## E. Open questions carried to plan/implementation (not blocking the spec)

- Private-URL scanner coverage (FR-019 / research R3): preferred = extend the
  shared disclosure.py with a private-URL rule (central, testable); fallback =
  composer-local stripping listed under redacted. Decision is deliberately left
  to the plan/implement phase because it touches a shared surface
  (Explorer/Passport also consume scan_disclosure); either path keeps
  secrets/abs-paths fail-closed. This is an implementation seam, not a spec
  ambiguity.

## F. Genericity / leakage check

- No C086 / pharmacy specifics baked into spec, plan, or tasks. The worked
  example is cited as a fixture only (Principle VII). ASCII-clean, UTF-8 no BOM
  across all six artifacts.

## G. Verdict

CONSISTENT. All FRs and SCs are task-covered; no contradictions across
artifacts; all cited reused symbols exist; constitution and Option-B aligned; no
Principle-V human seam was auto-cleared improperly. One implementation-phase seam
(private-URL scanner extension) is explicitly deferred with a fail-closed
fallback. Ready for the ratify seam (human).
