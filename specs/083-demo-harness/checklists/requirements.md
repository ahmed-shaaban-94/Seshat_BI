# Requirements Checklist: Local Demo Harness

**Purpose**: Self-validation of `spec.md` against Spec-Kit quality bar and the
repo's constitution/readiness-spine constraints, before handing off to `plan.md`.
**Created**: 2026-07-03
**Feature**: `specs/083-demo-harness/spec.md`

## Content quality

- [x] CHK001 No implementation detail leaks into requirements (FR-001..016
      describe CLI verb *behavior/contracts*, not internal module names or
      function signatures)
- [x] CHK002 Every user story has a priority (P1/P2/P3) and an independently
      testable acceptance path
- [x] CHK003 Edge cases cover: wrong invocation order, re-run/idempotency, DB
      extra without DSN, unrelated dirty tree, accidental prod-DSN pointing,
      cold-start report
- [x] CHK004 Non-Goals section explicitly rules out one-click dashboard
      generation (the task's named hard constraint), live-DB provisioning, and
      C086 reintroduction
- [x] CHK005 Assumptions section states the invented-dataset choice and the
      rejected alternative (reusing `retail_store_sales`), so a reviewer can
      override it without re-deriving the reasoning

## Constitution / readiness-spine alignment

- [x] CHK006 FR-005 explicitly forbids a separate run-state engine, matching
      AGENTS.md ("there is no separate run-state engine") and the
      readiness-viewer/first-hour-compass "renders, never re-derives" posture
- [x] CHK007 FR-006 restricts status vocabulary to the four defined values and
      forbids a numeric confidence score (Principle V / hard rule #9;
      `docs/readiness/readiness-model.md` "No fake confidence")
- [x] CHK008 FR-007/FR-008/FR-016/FR-017 + the Human-Approval Boundaries
      section keep every approval a named-human action the demo cannot
      self-grant (Principle V), including the two MANDATORY pre-committed
      approvals the offline `pass` states rest on (`source_ready`, required by
      rule RS1 for a CSV source; and `mapping_ready`)
- [x] CHK008b The offline honest ceiling is drawn CONSISTENTLY across spec
      SC-002, US1's independent test, `contracts/demo-run-contract.md`,
      `contracts/demo-report-contract.md`, and `quickstart.md`:
      Source/Mapping/Silver reach `pass` offline (Silver via
      `silver-ready.md`'s static "authoring only" gate), Gold Ready and later
      are `blocked`/`not_started` because Gold's gate is the live
      `retail validate` (`gold-ready.md`) -- no branch permits a fake offline
      `pass` past the ceiling
- [x] CHK008c `contracts/demo-report-contract.md` requires EVERY shipped
      illustrative approval to be labeled inline (not just the optional US3
      one) -- so the primary offline path's `source_ready`/`mapping_ready`
      `pass` states can never render as earned passes (the fake-pass the
      feature exists to prevent), in the most safety-critical surface
- [x] CHK009 FR-003/FR-012 + User Story 1's acceptance scenarios require
      graceful degrade-to-pending when no DB/extra is present, never a
      traceback or a faked pass (AGENTS.md "Live DB steps -- graceful
      deferred mode")
- [x] CHK010 FR-011 requires demo-scoped DB object naming so a live leg cannot
      collide with real schema objects (parallels the worked example's `_rss`
      suffix convention)
- [x] CHK011 FR-014 + Safety Constraints keep secrets exclusively in the
      git-ignored `.env` convention (Principle IX)
- [x] CHK012 FR-013 + the dashboard-generation Non-Goal keep `demo report` a
      status/evidence/blockers artifact, never a rendered visual (release-notes
      non-goal, Principle II adapter-is-later)

## Differentiation / overlap discipline

- [x] CHK013 Explicitly distinguishes this feature from
      `docs/demo/retail-store-sales-demo.md` (reading tour vs. runnable
      harness) with a stated non-duplication requirement (FR-015)
- [x] CHK014 Explicitly distinguishes this feature from
      `docs/worked-examples/retail-store-sales.md` (full narrative on real
      Kaggle data vs. small invented sample)
- [x] CHK015 States the dependency direction with `082-postgres-live-validation-suite`
      (083 depends optionally on 082; 082 has no dependency on 083) and the
      graceful-absent behavior
- [x] CHK016 States the relationship to `084-worked-example-factory` without
      inventing that sibling's contents (083 runs a sample; 084 would define
      how samples are authored)

## Testability / measurability

- [x] CHK017 Every SC-xxx is a binary or percentage measurement an
      independent reviewer could check without reading this spec's prose
      (e.g. SC-002/SC-004/SC-005 as "100% of runs")
- [x] CHK018 SC-004 and the Evidence Requirements section together make
      "no tracked-file writes, no fabricated approval" independently
      verifiable via `git status` and a diff, not just an assertion

## Clarification discipline

- [x] CHK019 No more than 3 [NEEDS CLARIFICATION] markers are used; this spec
      uses 0, with build-guiding choices recorded as Assumptions instead,
      because none of them are scope-changing unknowns

## Self-validation notes (informal, not a formal pass count)

Pass 1: drafted against the spec-template shape; checked FR/SC numbering is
sequential and every FR is independently testable.

Pass 2: cross-checked against `.specify/memory/constitution.md` Principles I,
II, IV, V, VII, VIII, IX and `docs/readiness/readiness-model.md`; tightened
FR-005/FR-006/FR-007 wording to quote the exact "no separate run-state engine"
/ "no fake confidence" language rather than paraphrase it loosely.

Pass 3: cross-checked against the four neighbor artifacts
(`docs/demo/retail-store-sales-demo.md`, the worked example, and the two named
sibling specs) to make sure the differentiation section names each one with a
concrete non-overlap claim rather than a generic "this is different" assertion.
