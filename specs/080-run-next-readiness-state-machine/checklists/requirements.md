# Specification Quality Checklist: Run-Next Readiness State Machine

**Purpose**: Validate that `spec.md` is complete, unambiguous, and ready for
planning (`/speckit-plan`).
**Created**: 2026-07-03
**Feature**: [spec.md](../spec.md)

**Note**: This checklist is generated per the `/speckit-checklist` convention
(business-focused: content-quality + completeness gates before planning begins).

## Content Quality

- [x] CHK001 No implementation details (languages, frameworks, APIs) leak into
      requirements -- FR-001..FR-016 describe WHAT the surface reads/returns/never
      does, not HOW (no file format, no code structure, no CLI flag names).
- [x] CHK002 Focused on user/agent value and business rules (stage-order
      enforcement, no self-approval, no fake confidence), not on a technology
      stack.
- [x] CHK003 Written for a non-implementer stakeholder: every requirement reads
      as an English behavioral rule; no code or pseudo-code appears in spec.md.
- [x] CHK004 All mandatory sections present: User Scenarios & Testing,
      Requirements, Success Criteria, Assumptions (plus the task-mandated
      Non-Goals, Human-Approval Boundaries, Safety Constraints, Stop Conditions,
      Evidence Requirements sections, which this spec adds as first-class
      sections per the assignment brief).

## Requirement Completeness

- [x] CHK005 At most one `[NEEDS CLARIFICATION]` marker remains, and it is
      scope-changing (grain/KPI-approval reading), not a lazy stand-in for an
      easy default -- confirmed: exactly 1 marker used, budget was up to 3.
- [x] CHK006 Every functional requirement (FR-001..FR-016) is testable: each
      names an observable input shape and an observable, checkable output
      (a returned action, a flag, a STOP, or an absence of a file write).
- [x] CHK007 Success criteria (SC-001..SC-005) are measurable and
      technology-agnostic (percentages/counts over fixtures, `git status`
      cleanliness, presence/absence of a numeric score) -- none names a
      language, library, or internal function.
- [x] CHK008 Every user story carries an independent acceptance test that does
      not depend on another story's implementation existing first (each is a
      single-fixture-in, single-response-out check).
- [x] CHK009 Edge cases enumerated (8 distinct edge cases: missing file,
      malformed file, `current_stage` disagreement, all-pass terminal state,
      invalid status string, `warning` non-blocking, dual-blocked stages,
      file-source approval sub-case) and each has a stated resolution, not just
      a question.
- [x] CHK010 Scope is explicitly bounded: 10 Non-Goals (NG-001..NG-010) each
      name a capability this feature does NOT have, addressing execution,
      approval-granting, cross-table aggregation, RS1 duplication,
      orchestrator changes, persisted state, new stages, live DB, scoring, and
      doc mutation.
- [x] CHK011 Dependencies and assumptions are identified: 8 assumptions
      (A1..A8) each name the existing artifact/feature relied upon
      (readiness-status.yaml, RS1, retail-orchestrate, readiness-viewer,
      the stage docs) and the relationship (reads, does not replace, matches
      shape rule, etc.).

## Feature Readiness

- [x] CHK012 Every functional requirement maps to at least one acceptance
      scenario or edge case: FR-002/FR-004 <- Edge Case "current_stage
      disagrees"; FR-005/FR-015 <- User Story 2 scenarios 1-2; FR-009 <- User
      Story 3 scenario 2; FR-010 <- User Story 3 scenario 1; FR-011/FR-012 <-
      Edge Cases "missing file"/"malformed"; FR-013 <- Non-Goal NG-003.
- [x] CHK013 User stories are prioritized (P1, P1, P2) and each is
      independently testable/deliverable -- User Story 1 alone is a viable MVP
      (the basic next-action computation); User Story 2 adds the approval-stop
      safety property; User Story 3 adds the honesty/evidence-gap layer on top.
- [x] CHK014 Success criteria are measurable without reference to any specific
      internal implementation (no function name, no file path referenced as
      "the code path" -- only observable repo state and response content).
- [x] CHK015 No contradiction between the Non-Goals and the Functional
      Requirements (cross-checked: NG-001/FR-008 agree on no-execution;
      NG-002/FR-005/FR-015 agree on no-self-approval; NG-006/A6 agree on no
      persisted state).

## Overlap / Duplication Self-Check (repo-specific gate)

- [x] CHK016 The spec names its delta against `retail-orchestrate` explicitly
      (Assumption A3, Non-Goal NG-005): 080 is the extracted READ half of
      orchestrate's existing inline next-phase table; it does not touch
      orchestrate's execution/self-heal loop.
- [x] CHK017 The spec names its delta against `readiness-viewer`/F026 and F012
      explicitly (Assumption A1, A2, Non-Goal NG-003): those RENDER the stored
      `next_action` verbatim across many tables; 080 COMPUTES a fresh next
      action for one table and flags disagreement with the stored field rather
      than rendering it as-is.
- [x] CHK018 The spec names its relationship to RS1 explicitly (Assumption A4,
      Non-Goal NG-004): 080 consumes the same approval-shape rule RS1 enforces
      but does not re-implement RS1's linting and adds no new `retail check`
      rule ID.
- [x] CHK019 The spec does not invent new readiness stages or new approval
      gates beyond the four the spine already defines (Assumption A5, Non-Goal
      NG-007); "grain approval" and "KPI approval" are explicitly mapped onto
      existing stages, with the residual ambiguity called out as the single
      NEEDS CLARIFICATION marker rather than silently resolved.

## Validation Log

- **Pass 1** (initial draft): all items above authored against the completed
  spec.md sections; no gaps found requiring a second pass.
- **Pass 2** (self-review against overlap risk): confirmed CHK016-CHK019 each
  cite a specific spec.md section (not just "it's fine") -- re-read
  `retail-orchestrate` and `readiness-viewer` SKILL.md content to verify the
  named deltas are accurate, not asserted. No corrections needed.
- **Pass 3** (safety-boundary re-check): re-verified FR-005/FR-015/NG-002 and
  the Human-Approval Boundaries section jointly cover all 4 named-human seams
  plus the Source Ready file-source special case (5 total, matching RS1's
  `_APPROVAL_REQUIRED` set plus its file-source branch) -- no seam omitted, no
  extra seam invented. Checklist PASSES; spec is ready for `/speckit-plan`.
- **Pass 4** (post-analyze correction pass, after the Step-4 analysis and an
  adversarial review): the analysis surfaced one real defect the first three
  passes MISSED -- FR-005's original wording was internally contradictory
  ("earliest non-`pass` stage ... and status is `pass`", logically
  impossible). CHK006 ("every FR is testable") is only truly satisfied AFTER
  this fix: FR-005 was reworded to fire on the walk's pass-branch and a new
  FR-005a was added reconciling the two approval-need paths (see
  analysis/analyze-report.md finding F10, and spec.md FR-005/FR-005a). Also
  fixed the plan.md/tasks.md fixtures-directory inconsistency (finding F5).
  Recording this honestly: the earlier "no corrections needed" notes reflected
  those passes' scope; the contradiction was a genuine miss caught only on the
  adversarial pass, now corrected. Checklist PASSES as of this pass.
