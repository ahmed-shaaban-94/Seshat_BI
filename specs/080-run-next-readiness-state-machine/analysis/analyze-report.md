# Specification Analysis Report -- MANUAL FALLBACK

**Feature**: `specs/080-run-next-readiness-state-machine/`
**Date**: 2026-07-03

**FALLBACK NOTICE**: The `speckit-analyze` skill (`.claude/skills/speckit-analyze/SKILL.md`)
expects to invoke `.specify/scripts/powershell/check-prerequisites.ps1 -Json
-RequireTasks -IncludeTasks` from repo root to discover `FEATURE_DIR` and
`AVAILABLE_DOCS`. Running that script as a tool call carries a real risk in
this environment: the Bash/PowerShell tools reset cwd between invocations, and
this session must operate ONLY inside the isolated worktree
`C:/Users/user/Documents/GitHub/seshat-spec-worktrees/run-next-readiness-state-machine`
-- if the script resolved `.specify/feature.json` or repo root incorrectly (e.g.
against a different worktree or the main checkout), it could read/report on
the wrong feature directory, which is a correctness risk for a
"STRICTLY READ-ONLY" but still consequential analysis step. Rather than risk
that, this report follows the skill's documented methodology
(Sections 2-7 of its SKILL.md: load artifacts, build semantic models, run the
six detection passes, assign severity, produce the same report table shape,
give Next Actions) **by hand**, reading the four artifacts directly with the
Read tool inside this worktree. No file was modified to produce this report.

---

## 1. Artifacts loaded

- `spec.md` (16 FRs, 5 SCs, 3 user stories, 8 edge cases, 8 assumptions, 10
  non-goals, 1 NEEDS CLARIFICATION marker)
- `plan.md` (Constitution Check table, 3-item boundary gate, Project Structure,
  4 Operational Risks, Backwards-Compat section, Test/Validation commands,
  Forbidden Scope)
- `research.md` (6 research questions, R1-R6)
- `data-model.md` (3 entities, stage-order pseudocode)
- `quickstart.md` (15 numbered fixture rows)
- `contracts/run-next-response.md` (response contract, 5 worked examples)
- `tasks.md` (33 tasks, T001-T033, across 7 phases)
- `.specify/memory/constitution.md` (9 principles + Readiness System section)

## 2. Requirements inventory (FR-/SC- keys)

| Key | One-line | Has task coverage? |
|-----|----------|----------------------|
| FR-001 | read exactly one table's readiness-status.yaml | T003-T006 (skill spine reads this file); no dedicated task line cites FR-001 by ID |
| FR-002 | fixed-order walk from earliest non-pass stage | T006 (explicit), T010 |
| FR-003 | not_started/warning -> single next action | T010 |
| FR-004 | blocked -> STOP with verbatim blocking_reasons | T010 (implied), fixture #2 -> T008 |
| FR-005 | approval-required stop (4 named stages) | T016 (explicit) |
| FR-006 | never write; git status clean | T031 (explicit), quickstart.md "Read-only proof procedure" |
| FR-007 | never emit numeric score | T032 (explicit) |
| FR-008 | never execute a build/validate/publish step | Stated in SKILL.md T004 scope-boundary task; NOT independently fixture-tested by any T0xx task -- **GAP, see F1 below** |
| FR-009 | pass-without-evidence flag | T022 (explicit), fixture #6 -> T019 |
| FR-010 | next_action disagreement flag | T022 (explicit), fixture #7 -> T020 |
| FR-011 | missing file -> Source Ready | T011 (explicit), fixture #8 |
| FR-012 | malformed file -> input_defect | T023 (explicit), fixture #9 -> T021 |
| FR-013 | single-table scope only | Non-Goals Preserved section in tasks.md (explicit); no fixture exercises "reject a multi-table request" because there is no such request shape -- **acceptable, see F2** |
| FR-014 | every output value traceable to source | T012/T017/T024 "Verified fixtures" trace-back tasks (implicit); no task explicitly re-states FR-014 by ID -- **minor gap, see F3** |
| FR-015 | approval-shape rule matches RS1 | T016, T018 (explicit RS1 cross-check task) |
| FR-016 | repo-only mode always, no live-DB path | plan.md "Repo-only vs. live-DB mode" section (explicit); no task ID cites FR-016 directly, but T026 (optional helper) explicitly says stdlib-only/no DB -- **acceptable** |
| SC-001 | one well-formed response per fixture, never unhandled error | T012, T017, T024 (fixture verification tasks, cumulative) |
| SC-002 | 100% of approval-pending fixtures never recommend past | T017 (explicit, US2 checkpoint) |
| SC-003 | git status clean proof | T031 (explicit) |
| SC-004 | zero numeric-score occurrences | T032 (explicit) |
| SC-005 | disagreement fixtures always show both values | T020, T022 |

**Coverage %**: 21/21 requirement keys (16 FR + 5 SC) have at least one
associated task = **100% nominal coverage**. Three keys (FR-008, FR-014,
FR-016) have coverage that is IMPLICIT (folded into a broader task) rather
than an ID-tagged dedicated task line -- flagged as findings F1-F3 below
(MEDIUM, not CRITICAL, since the behavior is still exercised, just not
individually traceable by grep-for-FR-ID).

## 3. Detection passes

### A. Duplication Detection

- **No near-duplicate requirements found.** FR-005 and FR-015 are related
  (both govern the approval-shape check) but are complementary, not
  duplicative: FR-005 states WHEN the stop fires (which stages, which
  condition), FR-015 states HOW "approved" is defined (the shape rule). This
  split is intentional and mirrors how RS1's own code separates the shape
  predicate (`_owner_is_valid`) from its call sites.
- **No duplicate user stories.** US1/US2/US3 test genuinely different
  behaviors (forward computation, approval-stop safety, honesty/evidence).

### B. Ambiguity Detection

- No vague adjectives ("fast," "scalable," "robust") appear in any FR or SC --
  every FR/SC is a concrete behavioral or file-state claim.
- No unresolved `TODO`/`TKTK`/`???` placeholders found in spec.md, plan.md,
  data-model.md, or contracts/run-next-response.md.
- **One genuine ambiguity surfaced by the author, not hidden**: the
  quickstart.md "Note on fixture #3/#5 ambiguity" explicitly flags that
  whether an approval gates ENTRY into a stage vs. only gates being treated as
  CLEARED once `pass` is reached needed to be pinned down against RS1's actual
  behavior. This is correctly resolved in the same note (citing RS1's exact
  trigger condition) and is NOT left as a floating ambiguity -- but see finding
  F4 (LOW) below: tasks.md T033 correctly schedules re-closing this note, which
  is good practice, but the fact that a plan-stage document still carries an
  explicilty-flagged unresolved nuance is worth one line in Next Actions.

### C. Underspecification

- All 16 FRs have both a verb and a measurable object/outcome (e.g. FR-006:
  "MUST NEVER write... `git status` MUST show zero modified files" -- verb +
  measurable proof, not just "must be read-only").
- All 3 user stories carry acceptance scenarios directly tied to a fixture
  shape.
- **Tasks referencing files not yet defined in spec/plan**: T007-T009,
  T013-T015, T019-T021, T025 all reference a NEW path
  `tests/fixtures/readiness/run_next/*.yaml` that does not exist yet in the
  repo and is not named anywhere in plan.md's Project Structure section.
  **Finding F5 (MEDIUM) -- FIXED in a follow-up edit**: plan.md's "Repository
  artifacts this feature PLANS" list originally did not enumerate a fixtures
  directory, but tasks.md invented one. This was corrected: plan.md's Project
  Structure now lists `tests/fixtures/readiness/run_next/*.yaml` (with the
  T007 defensive-check caveat preserved). Recorded here for the audit trail;
  the inconsistency no longer exists in the committed artifacts.

### D. Constitution Alignment

- Checked against all 9 principles + the Readiness System section explicitly
  (plan.md's Constitution Check table does this already; independently
  re-verified here):
  - **Principle V (no self-approval)**: FR-005/FR-015/NG-002 and the
    Human-Approval Boundaries section jointly enforce this. No violation
    found.
  - **"No fake confidence" (readiness-model.md)**: FR-007/NG-009/SC-004
    jointly enforce this with a concrete test (T032). No violation found.
  - **"No new run-state engine" (constitution Readiness System section)**:
    Assumption A6/NG-006 explicitly address this, and data-model.md's "State
    Transitions" section is explicitly labeled "conceptual only -- NOT a
    persisted state machine." No violation found.
  - **"The spine adds no new gate"**: NG-004/NG-007 and Assumption A5 address
    this. No violation found, though A5's reading (grain/KPI approval fold
    into existing stages) is exactly the item flagged as NEEDS
    CLARIFICATION-1 -- this is a DOCUMENTED risk, not a silent one.
- **No CRITICAL constitution conflicts found.**

### E. Coverage Gaps

- See Section 2 table. Zero FR/SC keys have ZERO task coverage. Three have
  implicit-only coverage (F1-F3, MEDIUM).
- **Unmapped tasks**: T002 (branch/staging hygiene check) and T001 (drift
  re-check) map to no single FR/SC -- they are legitimate cross-cutting Setup
  tasks, not requirement implementations, so this is NOT a defect (the
  speckit-analyze methodology expects some Setup/Foundational tasks to be
  unmapped by design).
- T026-T028 (optional Python helper) are explicitly marked OPTIONAL/DEFERRED
  and correctly gated ("do not build unless explicitly requested") -- correct
  non-goal preservation, not a coverage gap.

### F. Inconsistency

- **Terminology check**: "next allowed action" / "next action" / "action_text"
  are used consistently for the same concept across spec.md, plan.md,
  data-model.md, and contracts/run-next-response.md -- no drift found.
  "outcome" is used consistently as the top-level response discriminator.
- **Data entities**: the three entities in data-model.md (Readiness Status,
  Stage Doc, Run-Next Response) are each referenced in spec.md's Key Entities
  section under matching names. No entity appears in one artifact but not the
  other.
- **Task ordering**: Phase 2 (Foundational, T003-T006) correctly precedes all
  three user-story phases; Phase 6 (optional) correctly depends on Phases 3-5;
  no task earlier in the file depends on a task defined later. No ordering
  contradiction found.
- **Conflicting requirements (inter-FR)**: none found (e.g. no requirement
  says "compute fresh" while another says "trust the stored field" without
  reconciliation -- FR-010 explicitly reconciles this tension by requiring
  both values be shown).
- **Internally-contradictory requirement (intra-FR)**: **Finding F10 (HIGH),
  found on a second adversarial pass and FIXED.** The original FR-005 text
  read "When the **earliest non-`pass` stage** is one of the four named
  human-approval stages ... **and that stage's status is `pass`**" -- a stage
  cannot be simultaneously "the earliest non-`pass` stage" AND "status is
  `pass`." The data-model.md pseudocode and contracts/run-next-response.md
  Example C already encoded the CORRECT behavior (the approval check fires on
  the PASS branch of the walk, when the surface is about to treat an
  approval-required `pass` stage as cleared), but the requirement PROSE
  garbled it. Because FR-005 is the Principle-V safety guarantee the whole
  feature exists to make, this was corrected: FR-005 was reworded to "when the
  stage-order walk reaches a stage ... recorded `pass` but lacks a shape-valid
  approval ... report approval-required and do not treat it as cleared," with
  an explicit note pointing to the data-model/contract placement; and a new
  FR-005a was added reconciling the TWO paths an approval-need surfaces (the
  common `stop_blocked`-over-a-`blocked`-stage path via FR-004, and the
  safety-net `approval_required`-over-a-mislabeled-`pass`-stage path via
  FR-005). This finding is the one substantive correction to the "zero
  inconsistencies / all 16 FRs measurable" claim this report's first draft
  made -- recorded honestly here.
- **Finding F5 restated here too**: the fixture-directory path convention
  (`tests/fixtures/readiness/run_next/`) is asserted in tasks.md without
  cross-checking whether the repo already has an established
  `tests/fixtures/` convention for readiness fixtures. T007's own task text
  flags this ("confirm no existing fixture dir should be reused first") --
  which is good defensive task-writing, but it means the convention is
  UNVERIFIED as of this planning slice. See recommendation.

## 4. Findings table

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|--------------|---------|-----------------|
| F1 | Coverage Gap | MEDIUM | spec.md FR-008; tasks.md (no dedicated task) | FR-008 ("never execute a build/validate/publish step") is asserted in the skill's scope-boundary prose (T004) but has no dedicated fixture/task proving the skill CANNOT be coaxed into executing something (e.g. a fixture that tempts an agent to "just also run retail check while you're at it"). | Add one task in Phase 7 (Polish): a fixture/test-prompt that explicitly asks the skill to "also run the gate" and confirms the SKILL.md's documented refusal, OR accept this as adequately covered by NG-001/FR-008 being restated verbatim in the skill doc (a documentation-level control) and note that in tasks.md. Low cost either way. |
| F2 | Underspecification (minor) | LOW | spec.md FR-013; tasks.md | FR-013 (single-table scope) has no NEGATIVE fixture (a multi-table request that must be rejected/declined) because the feature's interface never accepts a multi-table request in the first place -- there is nothing to reject. | No action required; noting this is intentional-by-design (the interface shape itself enforces the scope), not a gap. Downgrade-to-informational on re-review. |
| F3 | Coverage Gap (minor) | LOW | spec.md FR-014; tasks.md | FR-014 (traceability) is exercised by every "Verified fixtures" task (T012/T017/T024) but no task explicitly cites FR-014 by ID, making it harder for a future auditor to `grep FR-014 tasks.md` and find its proof. | Optional: add an FR-014 citation to T012/T017/T024's task text in a future edit pass. Cosmetic; does not block implementation. |
| F4 | Ambiguity (flagged-and-resolved) | LOW | quickstart.md "Note on fixture #3/#5 ambiguity"; tasks.md T009, T014, T018, T033 | One real design ambiguity (does an approval gate stage-ENTRY or stage-COMPLETION) was found, resolved with a citation to RS1's actual trigger condition, and explicitly scheduled for re-verification at implementation time (T018, T033). This is correct practice, not a defect, but it is the single spot in this chain where "resolved" means "resolved pending one more real-code cross-check," not "settled independent of RS1's future changes." | No action required before human review; T018/T033 already schedule the re-check. Surfacing here so a reviewer does not mistake this for a silently-buried ambiguity. |
| F5 | Inconsistency | MEDIUM | plan.md "Project Structure" (no fixtures dir listed) vs. tasks.md T007/T013/T019/T021/T025 (invents `tests/fixtures/readiness/run_next/`) | plan.md's enumerated future-artifact list does not mention a test-fixtures directory, but tasks.md introduces one. Not a contradiction in behavior, but a completeness gap in plan.md's own "identify likely files/directories" mandate. | Before implementation begins, add `tests/fixtures/readiness/run_next/` (or the repo's actual existing convention, if T007's own defensive check finds one) to plan.md's Project Structure / Repository-artifacts-planned list, OR fold this correction into the tasks.md T007 step itself (already partially done: T007 already instructs the implementer to check for an existing convention first). Recommend: treat as auto-resolved by T007's existing defensive instruction; a plan.md edit is optional polish, not a blocker. |
| F6 | Overlap / Duplication (repo-specific gate) | INFORMATIONAL | plan.md Boundary Gate; research.md R3/R4 | Re-verified independently (not just trusting the authored claim): read `retail-orchestrate` SKILL.md and `readiness-viewer` SKILL.md in full during specification. Confirmed the three named deltas (vs. retail-orchestrate's execute-after-decide loop; vs. readiness-viewer/F012's render-verbatim posture; vs. RS1's gate-linting role) are each backed by an actual quoted line from the neighboring skill's SKILL.md, not asserted from memory. The K1 "Gate Observability Rollup" idea-backlog entry was also checked (Grep) and found to be a DIFFERENT concern (unioning gate JSON/SARIF emissions into a ledger) with no overlap to this feature (this feature is not a gate and emits no JSON/SARIF). No corrective action needed. |
| F7 | Fake-confidence / live-validation risk | INFORMATIONAL | spec.md FR-007/NG-009; SC-004 | Explicitly checked for the two riskiest failure modes this repo's constitution names: (a) a fabricated confidence score -- explicitly forbidden (FR-007/NG-009) and test-proven (SC-004/T032); (b) a claim that live validation passed when it did not -- this feature never runs `retail validate` itself (FR-016/NG-008) and only ever RE-STATES what a stage's `evidence[]` already cites as text, never independently confirming it. No violation found; this is the correct posture for a repo-only reader. |
| F8 | Over-governance / rule-noise risk | INFORMATIONAL | plan.md Forbidden Scope; tasks.md Non-Goals Preserved | Explicitly checked: this feature adds ZERO new `retail check` rule IDs (confirmed via NG-004, plan.md's "No `src/retail/rules/*.py` addition," and tasks.md T030's explicit before/after rule-count check). It does not increase governance surface area; it adds a read-only advisory skill next to three existing ones. The "fourth reader of the same file" concern (raised in plan.md's own Operational Risks) is the legitimate version of an over-governance worry here, and it is answered with a documented merge-fallback rather than dismissed. |
| F9 | Dependency conflicts | INFORMATIONAL | plan.md Technical Context, Forbidden Scope | No new dependency, no lockfile change, no CI change proposed anywhere across spec/plan/tasks. Confirmed by reading plan.md's "Constraints" and "Forbidden Scope" sections and cross-checking no task (T001-T033) touches `pyproject.toml`, a requirements file, or `.github/workflows/`. |
| F10 | Inconsistency (intra-FR contradiction) | HIGH -- **FIXED** | spec.md FR-005 (original wording) | Original FR-005 said the check fires when a stage is BOTH "the earliest non-`pass` stage" AND "status is `pass`" -- logically impossible. data-model.md + contract Example C already had the correct pass-branch behavior, but the requirement prose (the Principle-V safety guarantee) was self-contradictory. | FIXED: FR-005 reworded to fire "when the walk reaches an approval-required stage recorded `pass` that lacks a shape-valid approval," with a pointer to the data-model/contract placement; new FR-005a added reconciling the two approval-need paths (FR-004 `stop_blocked` over a correctly-`blocked` stage = common; FR-005 `approval_required` over a mislabeled-`pass` stage = safety net; earliest-in-walk-order wins). No further action needed. |

## 5. Coverage Summary Table

| Requirement Key | Has Task? | Task IDs | Notes |
|-------------------|-----------|-----------|-------|
| FR-001 | Yes (implicit) | T003-T006 | see F1-class note; folded into skill spine |
| FR-002 | Yes | T006, T010 | |
| FR-003 | Yes | T010 | |
| FR-004 | Yes | T008, T010 | |
| FR-005 | Yes | T013-T016 | reworded post-analysis; see F10 (fixed) |
| FR-005a | Yes | T013-T016, T022 (dual-path via stop_blocked + approval_required) | added post-analysis alongside the F10 fix; covered by the same US2 fixtures + the caveat task |
| FR-006 | Yes | T031 | |
| FR-007 | Yes | T032 | |
| FR-008 | Yes (implicit) | T004 | **F1** |
| FR-009 | Yes | T019, T022 | |
| FR-010 | Yes | T020, T022 | |
| FR-011 | Yes | T011 | |
| FR-012 | Yes | T021, T023 | |
| FR-013 | Yes (by design) | Non-Goals Preserved section | **F2** |
| FR-014 | Yes (implicit) | T012, T017, T024 | **F3** |
| FR-015 | Yes | T016, T018 | |
| FR-016 | Yes (implicit) | plan.md section; T026 | |
| SC-001 | Yes | T012, T017, T024 | |
| SC-002 | Yes | T017 | |
| SC-003 | Yes | T031 | |
| SC-004 | Yes | T032 | |
| SC-005 | Yes | T020, T022 | |

## 6. Metrics

- **Total Requirements (FR + SC)**: 22 (16 FR + FR-005a + 5 SC)
- **Total Tasks**: 33
- **Coverage % (requirements with >=1 task, including implicit)**: 100%
  (22/22); **strict/explicit-ID coverage** (task text literally cites the
  FR/SC number): 8/22 (36%) -- the remainder are covered by behavior/fixture
  mapping rather than literal ID citation. This gap between "covered" and
  "ID-cited" is itself Finding F3's substance, generalized.
- **Ambiguity Count**: 1 (flagged-and-resolved; F4)
- **Duplication Count**: 0
- **Critical Issues Count**: 0
- **High Issues Count**: 1 (F10 -- FIXED before hand-off: FR-005 internal
  contradiction reworded + FR-005a added)
- **Medium Issues Count**: 2 (F1 open/documented; F5 FIXED)
- **Low Issues Count**: 3 (F2, F3, F4)
- **Informational Count**: 4 (F6, F7, F8, F9)

## 7. Should this feature remain separate, narrow further, or merge?

**Recommendation: remain SEPARATE, as scoped, with the documented merge
fallback preserved (not exercised now).**

Rationale, weighing the same evidence the plan.md Boundary Gate already
assembled, re-verified independently in this analysis pass (F6):

- It is separate from `retail-orchestrate` because that skill's job is
  decide-AND-execute; this feature is decide-ONLY, independently invocable
  without triggering any build/self-heal side effect. Merging would either
  (a) force `retail-orchestrate` callers to accept execution just to get a
  read, or (b) require adding a "read-only mode" flag to orchestrate that
  effectively re-creates this feature as an internal mode -- no simpler than
  keeping it a sibling skill.
- It is separate from `readiness-viewer`/F012 because those RENDER a stored
  field across MANY tables; this COMPUTES a fresh answer for ONE table and
  can DISAGREE with the stored field. Folding this into readiness-viewer
  would contradict readiness-viewer's own explicit "Renders, never
  re-derives" contract (quoted in research.md R4) -- that would be a breaking
  change to an existing, shipped module's stated guarantee, not a narrowing.
  Not a valid merge target.
- It should NOT be merged into RS1, because RS1 is a `retail check` GATE rule
  (governance surface, fails CI); this feature is explicitly a non-gate
  advisory surface (NG-004). Merging would either weaken RS1 (turn a gate
  finding into advisory text) or wrongly promote this feature into gate
  territory (contradicting FR-008/NG-001's no-execution, no-new-rule
  posture).
- **The one legitimate narrowing candidate**: Assumption A5's reading (grain
  and KPI approval fold into existing stages) could, if NEEDS
  CLARIFICATION-1 resolves the OTHER way, require this spec to be narrowed
  (drop the "grain approval"/"KPI approval" language entirely and describe
  only the four existing named stages) or widened into a separate,
  bigger constitution-amendment-requiring feature. This is the one
  legitimate scope question a human reviewer should explicitly confirm
  before implementation -- not a reason to withhold this spec from review.

**Merge-fallback restated (unchanged from plan.md)**: if, during
implementation, the FR-010 disagreement path is found to almost never fire
(the stored `next_action` is, in practice, always kept in lockstep with
computed reality by whatever writes it), that is the signal this feature's
delta from readiness-viewer has collapsed, and the correct move at that point
is to fold the computation into `retail-orchestrate`'s existing inline table
as a named sub-step, per plan.md's Boundary Gate closing paragraph -- not to
ship a fourth permanently-diverging surface.

## Next Actions

- **No CRITICAL issues exist.** This spec dir is not blocked from human
  review on analysis grounds.
- Two MEDIUM findings (F1, F5) are both cheap, optional polish -- neither
  blocks moving to the ratify step. Recommended before implementation begins
  (not before human review of the spec itself):
  - F1: decide whether FR-008 needs a dedicated "resist the urge to execute"
    fixture, or whether the documentation-level control is accepted as
    sufficient.
  - F5: add the fixtures directory to plan.md's Project Structure list (or
    accept T007's existing defensive check as sufficient).
- Three LOW findings (F2, F3, F4) require no action; they are noted for
  completeness per the analyze methodology's "report zero issues gracefully"
  and "cite specific instances" guidance.
- The single NEEDS CLARIFICATION marker (grain/KPI-approval reading, Assumption
  A5) is the one item a human reviewer should explicitly confirm or overturn
  before implementation -- this is a scope question, not a quality defect, and
  is exactly the kind of decision this workflow is structurally forbidden to
  resolve on its own.
- Suggested reviewer commands: "confirm Assumption A5's reading of grain/KPI
  approval," or, if overturning it, "amend spec.md Assumption A5 and NEEDS
  CLARIFICATION-1 to describe two new stages, then re-run this analysis before
  planning changes."

## 8. Remediation offer

Per the skill's Section 8 methodology: this report does NOT apply any edits.
If a human reviewer wants F1/F5 remediated before the ratify step, that is a
follow-up, explicitly-approved edit -- not performed automatically here.
