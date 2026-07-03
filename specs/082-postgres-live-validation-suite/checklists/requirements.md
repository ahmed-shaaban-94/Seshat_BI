# Specification Quality Checklist: Postgres live-validation suite (local, ephemeral, honest)

**Purpose**: Validate `spec.md` for completeness, testability, honesty of live-DB claims, and
correct separation of repo-only vs live-DB checks before proceeding to `plan.md`.
**Created**: 2026-07-03
**Feature**: `specs/082-postgres-live-validation-suite/spec.md`

## Content Quality

- [x] CHK001 No implementation detail (language, library, container-tool name) is stated as a
  decision in `spec.md` itself -- Docker/testcontainers/`psycopg2` appear only as the
  user-supplied framing and as Assumptions marked "deferred to plan/research", never as a
  committed choice.
- [x] CHK002 Focused on user (contributor) value and observable outcomes, not on internal code
  structure.
- [x] CHK003 Written for a reviewer who is not the implementer -- each user story states the
  "why this priority" in outcome terms.
- [x] CHK004 All mandatory sections present: User Scenarios, Requirements, Success Criteria,
  Non-Goals, Human-Approval Boundaries, Safety Constraints, Stop Conditions, Assumptions.

## Requirement Completeness

- [x] CHK005 No unresolved `[NEEDS CLARIFICATION]` marker exceeds the 3-marker cap; each has a
  named working default so the chain is not blocked.
- [x] CHK006 Every functional requirement (FR-001..FR-014) is independently testable (each names
  a concrete, checkable condition, not a vague aspiration).
- [x] CHK007 Success criteria (SC-001..SC-007) are technology-agnostic in their outcome framing
  (e.g. "zero ERROR findings", "SKIPPED not PASSED") even though the underlying mechanism is a
  Python/pytest suite -- the measurable claim itself does not require reading source to verify.
- [x] CHK008 Success criteria are measurable (each has a concrete pass/fail condition or a
  named artifact to inspect).
- [x] CHK009 Every acceptance scenario across all 4 user stories follows Given/When/Then and
  names a concrete, checkable outcome.
- [x] CHK010 Edge cases identified: driver-missing-but-Docker-present, stale port conflict,
  re-run idempotency, Windows Docker Desktop startup behavior, partial mid-run failure, external
  DSN substitution attempt, local-credential redaction.
- [x] CHK011 Scope is clearly bounded: Non-Goals section explicitly excludes CI wiring, cloud
  DBs, new manifest dependencies, new `retail check` rules, golden-file regen, and modification
  of `validate.py`/`value_proxy.py`/`readiness_evidence.py`.
- [x] CHK012 Dependencies/assumptions identified: reuse of the existing `db` extra, a
  new-but-only-described `livetest`-working-name extra, Docker as the containerization mechanism,
  a new pytest marker for structural separation.

## Feature Readiness

- [x] CHK013 Every FR maps to at least one acceptance scenario or success criterion (traceable:
  e.g. FR-001..FR-002 -> SC-001/US1 Scenario 1; FR-005 -> SC-002/US2; FR-007 -> US1 Scenario 2;
  FR-009 -> SC-004/US4 all scenarios; FR-010/FR-011 -> SC-005; FR-012 -> the "no stage-pass"
  Non-Goal + FR text itself, verifiable by code review of any future implementation, not by a
  runtime assertion this chain can make).
- [x] CHK014 User stories are prioritized (P1/P1/P2/P1) and each is independently testable per
  its own "Independent Test" clause.
- [x] CHK015 No implementation detail leaks into requirement language that would constrain the
  plan phase's tool choice unnecessarily (FRs speak of "a container-based mechanism", "the real
  `psycopg2`-backed `QueryRunner`" -- the latter is a REUSE of an already-shipped, named seam,
  not a new implementation choice, so naming it is not a premature decision).

## Honest Live-Validation Discipline (feature-specific gate)

- [x] CHK016 **No Hidden Live Pass** is stated as an explicit requirement (FR-009), an explicit
  success criterion (SC-004), an explicit edge case (stale container / partial mid-run failure),
  and an explicit contract obligation (deferred to `plan.md`/`contracts/`) -- appearing in all
  four places the task instructions require.
- [x] CHK017 Every unavailability precondition named in the task (Docker down, container fail,
  port conflict, seed fail) has a corresponding edge case and/or User Story 4 acceptance
  scenario -- plus driver-missing, which the task's phrasing implies but does not name verbatim.
- [x] CHK018 Repo-only vs live-DB separation is stated as its own functional requirement
  (FR-010) with a structural (not conventional) enforcement mechanism named (a distinct pytest
  marker/directory), and as its own success criterion (SC-005).
- [x] CHK019 The spec explicitly forbids the suite from granting any readiness stage's `pass`
  (FR-012, Non-Goals) and explicitly distinguishes this feature (the harness) from the checks it
  runs (`validate.py`/`value_proxy.py`) and from the recorder it feeds (057) in the Overview.
- [x] CHK020 No real credential, DSN, or hostname (real or example-realistic) appears anywhere
  in `spec.md`; all connection references use `<placeholder>` forms or reference existing code by
  file/function name only.

## Notes

- Self-validated by the authoring agent (no human reviewer in this spec-only chain). All 20
  items pass on inspection; none required a spec revision (this is the reviewed/final `spec.md`,
  not an earlier draft this checklist rejected).
- If a future human reviewer disagrees with a working default recorded under a
  `[NEEDS CLARIFICATION]` marker (see `spec.md` end), that disagreement should be resolved by
  amending `spec.md` before `plan.md` is treated as final, not by silently overriding it in
  `plan.md`.
