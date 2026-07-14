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
- Option B (ratified 2026-07-07): honored as the recommended default (skill,
  not verb). The peer `explorer`/`passport` CLI verbs were added by spec 120
  (created 2026-07-11, AFTER the ratification), so they are NOT a grandfathered
  pre-ratification exception -- they are a live post-ratification verb-parity
  precedent for the nearest sibling surfaces. Because the verb-vs-skill choice is
  a product-identity call the Option B doc itself reserves for the owner, this
  spec routes it to the ratifier (see Section D item 1 and the spec's
  "Open for human" note) rather than presenting it as auto-cleared.

## D. Ambiguities / underspecification (resolved by auto-answer, recorded)

1. Verb vs skill -> RECLASSIFIED to open_for_human (see Section E). Skill
   (Option B) is the recommended default, but the choice is a product-identity
   call reserved for the owner, not an auto-cleared decision.
2. Redact vs block on live findings -> block fail-closed; redacted =
   portability normalization. Recorded.
3. "valid comparable snapshots" -> same schema+scope, differing revision.
   Recorded.
4. Producing the bundle != publish sign-off. Recorded (Principle-V-adjacent,
   auto-answered NO because the bundle is local; NOT a publish decision).

No open [NEEDS CLARIFICATION] markers remain in spec.md.

## E. Open for human (ratifier) + open questions carried to implementation

**Open for human (Principle-V-adjacent, ratifier decides at the ratify seam):**

- **Skill vs `seshat showcase build` CLI verb (product identity).** The
  recommended default is a read-only skill over a reusable library function,
  applying the ratified Option B policy (`cli-verbs-vs-skill-driven.md`,
  2026-07-07). This is NOT auto-cleared: (1) the choice is reversible-but-costly;
  (2) the nearest sibling surfaces `explorer`/`passport` are shipped CLI verbs
  added by spec 120 AFTER the Option B ratification -- a live verb-parity
  counter-argument; (3) the Option B doc states the verb-vs-skill choice "is a
  genuine change to the product's stated identity ... an owner decision." The
  ratifier may confirm the skill default or override to verb-parity. FR-005
  encodes the recommended default and must be re-confirmed (or amended) at
  ratification.

**Open questions carried to plan/implementation (not blocking the spec):**

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
artifacts; all cited reused symbols exist; constitution and Option-B aligned.
One product-identity choice (skill vs CLI verb) is routed to the ratifier as an
open_for_human item (Section E) with skill as the recommended default -- it is
NOT auto-cleared. One implementation-phase seam (private-URL scanner extension)
is explicitly deferred with a fail-closed fallback. Ready for the ratify seam
(human).

## H. Post-review correction (advisor pass, 2026-07-14)

An adversarial review pass found one BLOCKER that section A's FR->task mapping
structurally could not catch (it verified coverage, not whether the reused
mechanism delivers the FR), plus one unverified claim. Both are now fixed in the
artifacts and re-committed:

1. **BLOCKER (fixed): disclosure scan scanned the wrong body.** As first drafted,
   `disclosure` was "carried through from the Explorer projection." But
   `build_explorer_projection` sets `disclosure = base["disclosure"]`
   (explorer/build.py:183), which is scanned on the BASE projection BEFORE
   `_lineage` (metric names/paths) and `_approval_receipts` (owner names) enrich
   the tables, and before any before/after content exists. The killer case is
   US4: user-supplied Passport snapshot content would flow into the bundle
   UNSCANNED, so a "disclosure-safe proof" would gate on a result that never saw
   its own rendered content. FIX: `build_showcase_bundle` now runs
   `scan_disclosure` over the FULL composed body (tables + enriched lineage +
   approvals + badge + manifest + comparison), MERGED with the base projection's
   invariant findings (pass-without-evidence / blocked-without-reason, which live
   only in `build_readiness_projection`). Order pinned: compose -> normalize/redact
   -> scan full body -> fail-closed. This also reconciles FR-010 (abs-path blocks)
   with FR-019 (abs-path -> repo-relative, redacted): normalization runs before the
   scan, so only a residual path blocks. Touched: spec FR-009/FR-010 + clarification
   + reuse-map row 7, data-model disclosure row + INV-4, contract behavior, research
   R2, plan R2, tasks T004/T006a/T020.

2. **Unverified claim (fixed): "explorer/passport verbs predate Option B, so
   grandfathered."** Verified FALSE -- spec 120 (which added those verbs) was
   created 2026-07-11, AFTER the 2026-07-07 Option B ratification. The decision
   (skill, not verb) is unchanged and correct (the ratified policy governs new
   capabilities), but the justification now rests on applying the policy, and the
   sibling-verb tension is surfaced explicitly for the ratifier as a possible
   verb-parity override rather than buried under a false "grandfathered" claim.
   Touched: spec clarification + assumptions, research R1, plan R1.

3. **Verified (no change needed):** `.seshat-output/` IS git-ignored (.gitignore:96),
   so the quickstart claim holds; the containment guard remains the real control.
   All cited reused symbols exist as named (re-confirmed).

Revised verdict: CONSISTENT after the fixes. The disclosure mechanism now
matches FR-009; the Option-B justification is factually grounded. A later
correction (2026-07-14, second advisor pass) additionally RECLASSIFIED the
verb-vs-skill choice from an auto-cleared decision to an open_for_human ratifier
call (Section E), because it is a reversible-but-costly product-identity decision
with a live post-ratification sibling-verb precedent (`explorer`/`passport`, spec
120); skill remains the recommended default. No PII/grain/rollup decision arises
in a local rendering layer. Ready for the ratify seam (human).
