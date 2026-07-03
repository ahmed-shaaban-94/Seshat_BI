# Cross-Artifact Analysis Report: Postgres live-validation suite

**Feature**: `specs/082-postgres-live-validation-suite`
**Date**: 2026-07-03
**Method**: The `speckit-analyze` skill WAS invoked (read-only) as Step 4 of this chain. Its
prerequisite script (`.specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks
-IncludeTasks`) initially errored because the worktree branch is `spec/postgres-live-validation-
suite` rather than the `082-...` naming pattern the script validates; re-running it with the
sanctioned `SPECIFY_FEATURE=082-postgres-live-validation-suite` override (the script's documented
env-var escape, which also reads the `.specify/feature.json` pointer this chain set) resolved the
feature dir correctly and confirmed all required docs present (`research.md`, `data-model.md`,
`contracts/`, `quickstart.md`, `tasks.md`). The skill's `before_analyze` / `after_analyze`
extension hooks are both `git.commit` (`optional: true`) and were deliberately NOT executed, per
this chain's no-commit/no-push/no-PR boundary. This document is the report produced by running
the skill's detection passes (duplication, ambiguity, underspecification, constitution alignment,
coverage gaps, inconsistency) over `spec.md`, `plan.md`, `tasks.md`, `research.md`,
`data-model.md`, `contracts/live-pass-contract.md`, and the constitution -- augmented with the
overlap/unsafe-claim/fake-confidence/live-validation-claim/over-governance analysis this feature
specifically required. (The skill is a read-only analysis pass that writes no files; this report
is authored to the spec dir as the durable record of that pass.)

## Summary verdict

**Ready for human review.** No CRITICAL or HIGH finding. The feature is internally consistent,
its requirements are covered by tasks, its central discipline (no hidden live pass) is expressed
redundantly across FR/SC/contract/edge-case, and its overlap with adjacent shipped work
(`validate.py`, `value_proxy.py`, `057-live-validation-evidence-recorder`) is explicitly argued
as additive, not duplicative. Findings below are LOW/MEDIUM notes for the reviewer, not blockers.

## 1. Consistency (spec <-> plan <-> tasks <-> contracts)

| Dimension | Finding |
|---|---|
| User stories -> tasks | All four user stories (US1-US4) map to dedicated task phases (Phase 3-6). US1->T012-T015; US2->T016-T023; US3->T024-T026; US4->T027-T035. Consistent. |
| FRs -> tasks | FR-001/002 (ephemeral local container, no external DSN) -> T009/T011. FR-003 (no real creds, redaction) -> T009/T011 + Safety Constraints. FR-004 (generic seed) -> T007/T012/T016-T019/T024. FR-005 (clean+defect per check) -> T012 + T016-T023. FR-006 (real psycopg2 runner) -> T013/T020-T023/T025-T026. FR-007 (feed 057 recorder) -> T014. FR-008/FR-009 (three-outcome / no hidden pass) -> Phase 2 checkpoint + T027-T032 + T034 + contract. FR-010 (structural separation) -> T006 + T033 + T035. FR-011 (no module-scope import in src) -> T040. FR-012 (no stage pass) -> T014 assertion + contract disclaimer. FR-013 (local, no CI) -> whole plan; Non-Goals. FR-014 (readable mode report) -> T015. All 14 FRs traced. |
| SCs -> tasks/tests | SC-001->T013; SC-002->T020-T023; SC-003->T025-T026; SC-004->T027-T032; SC-005->T035/T039; SC-006->redaction (T009/T011) + text-scan intent; SC-007->T038 timing. All 7 SCs traced. |
| Terminology | `run_mode`/`mode` used consistently (matches 057's `build_gold_ready_block(run_mode=...)` signature, confirmed against `src/retail/readiness_evidence.py`). Reason strings (`"docker not available"` etc.) are identical between `spec.md` edge cases, `contracts/live-pass-contract.md`, `data-model.md` section 3, and `tasks.md`. No drift. |
| Marker name | `@pytest.mark.live_db` used consistently in `research.md`, `plan.md`, `quickstart.md`, `tasks.md`. Not yet registered (correctly flagged as a manifest edit deferred to T005). |

**Consistency verdict: PASS.** One MEDIUM note: `tasks.md` T013 says "Must FAIL first" but this
suite's tests are fixture-dependent rather than TDD-red-then-green in the classic sense; the
task text already qualifies this ("confirm it fails for the RIGHT reason"), so it is not a
contradiction, but a reviewer should read it as "verify the test genuinely exercises the
container, don't accept a vacuous pass" rather than strict RED-first TDD.

## 2. Coverage gaps

- **No gap in FR/SC coverage** -- every requirement traces to at least one task (table above).
- **Edge cases -> tasks**: driver-missing (T028), port conflict (T030), re-run idempotency
  (implied by T009's fresh-container/reset design + T035; not its own dedicated test -- LOW note:
  a reviewer may want an explicit "run twice, second run's clean scenario unaffected by first
  run's defect seed" test added at implementation time; currently covered structurally by
  isolated per-scenario containers but not by a dedicated regression test). **LOW.**
- **Windows Docker Desktop edge case** -> T003 (measure real timing) + `research.md` Decision 5.
  Covered as an operational note, not a dedicated test (appropriate -- it's an environment risk,
  not a code path).
- **Partial mid-run failure edge case** -> covered by `contracts/live-pass-contract.md`
  precondition #5 ("live check raised an unexpected error" -> skip) and the `ScenarioOutcome`
  invariant in `data-model.md` section 3; no dedicated task test for a container killed
  mid-suite (hard to simulate deterministically). **LOW note** for the reviewer.

## 3. Ambiguity / approval-boundary clarity

- **Human-approval boundaries** (`spec.md`) are explicit and correct: ratification is a named-
  human action; no self-approval; future manifest/CI/`src` touches go through normal review.
  Matches the repo's `Ratify seam not auto-cleared` memory lesson.
- **Three `[NEEDS CLARIFICATION]` markers**, all scope-forking, all with a stated working
  default (opt-in marker; CI-as-risk-only; sum-not-ratio for L4). None left dangling. Within the
  ≤3 cap. **PASS.**
- One additional `[NEEDS-HUMAN-CONFIRM]` appears in `tasks.md` T036 (docs-placement of the
  gold-ready cross-reference). This is deliberately NOT counted against the spec's 3-marker
  budget because it is a docs-nicety scope call at implementation time, not a spec-level scope
  fork. **LOW note**: a strict reviewer might prefer it folded into the spec's markers; the
  author's judgment is that it does not rise to spec-level. Flagged for the reviewer to accept or
  reject.

## 4. Hidden implementation scope (spec-only chain discipline)

- No artifact in this chain edits `src/**`, any manifest, any CI file, or any golden file --
  verified: `plan.md` and `tasks.md` both flag T004/T005 (manifest) as explicitly out of scope
  for the authoring chain, and mark zero `src/retail/` edits.
- `.specify/feature.json` was repointed to `082-...` -- this is the one sanctioned file outside
  the spec dir, authorized by the task ("set `.specify/feature.json` in your worktree").
- **No hidden scope.** PASS.

## 5. OVERLAP analysis (the required, highest-scrutiny section)

The three adjacent shipped surfaces and why 082 is distinct, not duplicative:

| Adjacent shipped work | What it owns | What 082 does differently |
|---|---|---|
| `src/retail/validate.py` (`004-retail-validate`) | The four live-check ALGORITHMS (V-RC2/V-RC15/V-RC16) over a driver-free `QueryRunner` Protocol, plus the lazy `make_psycopg2_runner`. Fixture-tested against FAKE runners. | 082 does NOT re-implement any check. It provides the real DATABASE + SEED + HARNESS those checks need to run against real materialized rows for the first time (they have only ever run against fakes). 082 calls `run_live_checks`/`make_psycopg2_runner` unmodified. |
| `src/retail/value_proxy.py` (L4) | The L4 value-drift check ALGORITHM (`check_expected_value`). Fixture-tested against fakes. | 082 calls it unmodified against a real seeded gold measure; adds no L4 logic. |
| `057-live-validation-evidence-recorder` (`src/retail/readiness_evidence.py`) | Turning a `Finding[]` list into a proposed `gold_ready` readiness block. A PURE serializer; FR-012 "never sets pass"; FR-013 "emit-only". | 082 FEEDS it one real live run's output to prove the seam end-to-end; it does not modify the recorder, its status rules, or its emit-only posture. `contracts/live-pass-contract.md` explicitly restates that 057's rules are unchanged. |

**Overlap verdict: DISTINCT, additive.** 082's unique, nowhere-else-in-repo contribution is the
**local ephemeral Postgres substrate + generic seed + honest-skip harness** -- the concrete,
credential-free instantiation of Principle VIII's "live run deferred" step. The keep-separate
recommendation (below) is to keep 082 as its own feature, not to fold it into 004/057.

No overlap found with `044-live-surface-protocol`, `048-live-surface-import-boundary-guard`
(082 must KEEP that guard green, FR-011/T040 -- a dependency, not an overlap), or the readiness
docs (082 references `gold-ready.md`, doesn't redefine it).

## 6. Unsafe-claim scan (feature-critical)

- **LIVE-VALIDATION-CLAIM risk (highest priority for this feature)**: The chain makes NO claim
  that any live validation has passed. Every artifact frames the live run as a FUTURE capability
  the harness ENABLES; `spec.md`/`plan.md`/`tasks.md` all state no code is executed by this
  chain. The `contracts/live-pass-contract.md` is entirely devoted to forbidding the hidden-pass
  shape. **No unsafe live claim present. PASS.**
- **FAKE-CONFIDENCE risk**: No numeric confidence/score appears anywhere; `data-model.md` section
  4 explicitly excludes a score field from `ScenarioOutcome`; FR-014 / SC framing uses the
  four-status vocabulary, never a number. **PASS.**
- **Secret-leak risk**: No DSN literal, hostname, or credential appears in any artifact. All
  connection references use `<placeholder>` or name existing code by file/function. The one place
  a full DSN shape could tempt (research/quickstart) deliberately uses `pip install
  'retail[db]'`-style commands and `<placeholder>` forms only, avoiding the
  scheme-userinfo-at-host shape that `validate.py` itself breaks up to satisfy the C2 scanner.
  **PASS.**
- **Over-governance risk**: 082 adds NO new `retail check` rule, NO new gate, NO new approval
  seam. It is evidentiary tooling only. The two static wiring tests it proposes (T033/T034) are
  test-side guards on 082's OWN test directory, not new repo-wide governance rules. **PASS --
  appropriately narrow.**

## 7. Dependency-conflict / optional-extra boundary

- The `db` extra (`psycopg2-binary`) is reused as-is -- no conflict.
- The would-be `livetest` extra is DESCRIBED only, kept disjoint from `dev` (so CI installs no
  Docker-orchestration dependency) and from `db`. Not added to any manifest by this chain.
- No conflict with the static core's `dependencies = []` invariant: FR-011 + T040 guard it; the
  harness is entirely test-side. **PASS.**

## 8. Recommendation

**KEEP AS A SEPARATE FEATURE, appropriately narrow, ready for human review.**

- Do not fold 082 into `004-retail-validate` or `057-live-validation-evidence-recorder`: it has a
  distinct concern (the local DB substrate/harness) and folding it would blur the clean
  algorithm-vs-substrate separation those features rely on.
- The three `[NEEDS CLARIFICATION]` markers (opt-in vs default collection; CI-as-risk-only;
  sum-vs-ratio L4) are the reviewer's to rule on; the working defaults are safe to proceed under
  if the reviewer does not object.
- LOW notes for the implementer (not blockers): add a dedicated re-run-idempotency test and a
  best-effort mid-run-failure test at implementation time; decide the T036 docs-placement call.

**No CI/Actions were run or claimed. No live validation was run or claimed. No secret was
printed. No file outside `specs/082-postgres-live-validation-suite/` was created (the sole
sanctioned exception being the authorized `.specify/feature.json` repoint).**
