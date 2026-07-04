# Adversarial Plan-Review: Golden/Regression Tests for Generated DAX & SQL (100)

**Date**: 2026-07-04 | **Branch**: `100-generated-artifact-golden-tests`
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports fixes, never edits).
**Scope**: spec.md, plan.md, tasks.md, analysis.md across five axes
(hidden-principle-violation, assumes-deferred-capability, c086-leak, fabricated-confidence,
over-scope).

**Inputs reviewed**: spec.md (present, Clarifications session recorded 2026-07-04), plan.md
(present, with research.md/data-model.md/quickstart.md as its Phase 0/1 siblings), tasks.md
(present, 27 tasks across 6 phases). **analysis.md is ABSENT.** This is called out up front
because it is verdict-determining -- see Axis 1, Finding R1.

## Precedent check: is a missing analysis.md normal at this point in the chain, or anomalous?

Before scoring axis 1, I checked whether "no analysis.md" is common among features that already
have a plan-review.md (i.e., features that reached this same stage). Every plan-reviewed feature
from 041 through 068 (28 consecutive features: 041, 042, 043, 044 x2, 045, 046, 047, 048, 049,
050, 051, 052, 053, 054, 055, 056, 057, 058, 059, 060, 061, 062, 063, 064, 065, 066, 067 x2, 068)
carries an analysis.md. The gap only starts appearing from 069 onward (069, 070, 087, 094, 095
lack it), which reads as a LATER change in chain practice, not a signal that analysis.md was ever
optional for features shaped like this one. Feature 100's own task instructions (the brief this
review was commissioned under) explicitly list analysis.md as a required read alongside spec/plan/
tasks -- i.e., the chain that produced this review expects it to exist. Its absence here means the
`/speckit-analyze` stage was never run for this feature, not that it was judged unnecessary.

This matters concretely, not just procedurally: analysis.md is the stage that checks
spec-vs-plan-vs-tasks CONSISTENCY (duplicate/conflicting requirements, terminology drift, FR/task
coverage gaps) as an artifact separate from either document alone -- exactly the kind of thing
precedent 043's own plan-review found analyze-clean but STILL WRONG (R1 in that review: analyze
returned clean but missed a spec self-contradiction). This review cannot substitute for that stage;
it reviews the same three documents from a different angle (principles, not internal consistency),
and grounded-checked several claims directly against source in the process (see below), but it does
not replace a coverage-matrix pass over spec.md's FRs against tasks.md's task list as a dedicated
artifact would.

## Axis 1 -- hidden-principle-violation

### Finding R1 (HIGH, blocking): analyze stage was never run -- analysis.md is absent

Per the precedent survey above, every comparable plan-reviewed feature in this chain's dense
041-068 run produced an analysis.md before reaching plan-review. Feature 100 has research.md,
data-model.md, and quickstart.md (the `/speckit-plan` Phase 0/1 outputs) but no analysis.md (the
`/speckit-analyze` output). This is not itself a principle the spec violates in its own text --
but the review's own task brief requires analysis.md as an input, and the 046 review (the nearest
sibling in this same golden-file-lock family) states explicitly: "A draft missing analyze or tasks
would be automatic BLOCKED." Tasks.md is present here; analysis.md is not. Under that same
standard, this is a blocking gap, not a style note: it means the cross-artifact consistency check
(FR-to-task coverage, terminology drift, duplicate/conflicting requirements) that stage performs
has not been run for this feature, even though the tasks.md FR Coverage Map at the bottom of
tasks.md reads as if it substitutes for one (it does not -- it is authored by the same pass that
wrote the tasks, not an independent check).

FIX: Run `/speckit-analyze` (or the equivalent analysis stage) for this feature and produce
`specs/100-generated-artifact-golden-tests/analysis.md` before this feature proceeds past plan
review. Given the grounding performed below found no contradiction between spec/plan/tasks, this
is very likely to return clean -- but "very likely clean" is exactly the posture Principle I
(demonstrable, not asserted) forbids substituting for the actual run.

### Content-level check (assuming R1 is resolved): no self-grant, no Principle-V resolution, no advise-instead-of-block

Independent of R1, I looked for the substantive version of this axis -- does the spec/plan/tasks
content itself quietly resolve a judgment call or self-grant a readiness pass? It does not:

- The spec's own Assumptions section states plainly that this feature "requires no named-human
  approval and raises no Principle-V judgment call," and I could not find a grain/PII/business-
  policy/approval question anywhere in spec.md, plan.md, or tasks.md that the text then quietly
  answers itself. There is no readiness-stage transition anywhere in this feature's surface (it
  writes no `readiness-status.yaml` entry, requests no approval).
- The tests this feature adds are themselves fail-closed by construction: FR-007 and its mirrored
  tasks (T009, T014) require an explicit failure naming the missing/unreadable path, never a
  `pytest.skip`, on a missing golden. This is "block," not "advise" -- consistent with Principle I's
  fail-closed requirement, even though (correctly, per FR-001) it is scoped to pytest, not to
  `retail check` itself. The plan's Constitution Check states this distinction precisely rather than
  overclaiming: "Demonstrability here means 'run `pytest -m unit`,' not 'run `retail check`.'" That
  precision is itself evidence against a hidden violation -- an over-reaching spec would have
  blurred this line to claim `retail check` coverage it does not have.
- I verified the one FR that could plausibly hide a scope creep into "the tests decide something
  new": FR-002's exact call shape. Read directly from `src/retail/cli.py::_run_generate` (lines
  1036-1040 in the current worktree), the call is:
  `generate_measure(contract.get("definition") or {}, name=name, doc_intent=contract.get("formula_intent"))`
  with `name = contract.get("name")` -- this matches FR-002's stated call shape verbatim, including
  the `or {}` fallback the spec text does not literally reproduce but the plan's data-model.md does
  (`contract.get("definition") or {}`). No drift between claimed and actual CLI behavior.

PASS on the content-level check; the blocking issue is procedural (R1), not a hidden resolution
inside the text itself.

## Axis 2 -- assumes-deferred-capability

PASS. Grounded, not just asserted:

- Read `src/retail/dax_gen.py` directly: `GenResult` (dataclass, lines ~20-31) exposes `ok`, `dax`,
  `tmdl_block`, `reason`, `warnings` exactly as the spec/plan/data-model describe -- no import of any
  live adapter, DB driver, or Power BI surface anywhere in the module (confirmed by the plan's own
  research.md, cross-checked against the file directly).
- The two exemplar migration files
  (`warehouse/migrations/0003_create_silver_retail_store_sales.sql`,
  `0004_create_gold_retail_store_sales_star.sql`) exist on disk exactly where FR-004 says; they are
  read as TEXT, never executed, never connected to.
- FR-005 explicitly forbids any DB connection, live Power BI/PBIP surface, F016 (execution adapter),
  or F031-F033 (spec-only runtimes); SC-003 requires the full suite to pass with no DB connection
  available and no environment variable set. research.md's dedicated "Deferred capabilities NOT
  assumed" section names F016, live Postgres, F031-F033, and the `retail-build-warehouse` skill's
  EXECUTION explicitly and states each is untouched. Nothing in tasks.md contradicts this (T015
  explicitly asserts the SQL regression test opens no DB connection and invokes no skill/CLI step).

No deferred capability is assumed anywhere in this chain.

## Axis 3 -- c086-leak

PASS, with one honest residual noted (same shape as 046's own residual, not a new problem).

- FR-010 explicitly and correctly invokes Principle VII's own mechanism: reusing the existing,
  already-approved `retail_store_sales` (C086) contracts and migrations as "a cited filled
  instance, not a template default" is exactly what Principle VII authorizes -- it is not a leak to
  cite an approved instance by name when the spec says it is doing exactly that, and the plan's
  Constitution Check for Principle VII repeats this reasoning without overclaiming.
- The two TEST MODULES this feature adds (`test_dax_golden.py`, `test_warehouse_sql_golden.py`) are
  themselves fully generic per the plan's own claim -- I checked this claim against the tasks that
  build them (T007, T008, T013) and found no domain-specific branching logic described (they iterate
  a fixture-stem list and a filename-pair list; nothing about "sales," "discount," or "retail" is
  hardcoded into the COMPARISON LOGIC itself, only into the fixture DATA and file names, which is
  the citation FR-010 authorizes).
- RESIDUAL (LOW, non-blocking, same shape as the 046 review's own axis-3 residual): the golden
  `.txt`/`.sql` fixture CONTENTS will unavoidably contain C086-specific identifiers
  (`total_spent`, `fct_sales_rss`, `discount_applied`, the `0003`/`0004` filenames) because they are
  verbatim generator output for a cited C086 instance. No success criterion in the spec scans the
  fixture CONTENTS for domain leakage the way SC-006 scans for fabricated scores -- but this is
  correct and expected here, not a gap: FR-010 explicitly says these ARE the cited filled instance,
  not a genericity target. Recorded as a note, not a finding, because the alternative (inventing a
  synthetic non-C086 fixture set) is explicitly rejected by the spec's own Assumptions ("no new
  synthetic-only domain is required").

## Axis 4 -- fabricated-confidence

PASS. Structurally, not just by assertion:

- Every comparison this feature performs is a binary string-equality check (FR-002, FR-003, FR-004,
  FR-006) -- pass or fail with a text diff, never a score, percentage, or partial-credit value.
- FR-012 and SC-006 explicitly forbid any numeric confidence/health/maturity score or "N of M"
  completeness tally anywhere in the tests, fixtures, or docs this feature adds; T025 is a dedicated
  polish task that greps every added file for exactly this pattern before the feature is considered
  done.
- The Success Criteria that DO use numbers (SC-003 "100% of golden/regression tests... pass," SC-004
  "0... tests flake," SC-005 "byte-identical," SC-006 "0 numeric... scores") are counts/binaries
  about the TEST SUITE's own behavior, not a fabricated readiness/maturity score about the feature
  or the codebase -- this is the same SC style the 046 review examined and explicitly blessed
  ("SC values are counts... not invented percentages"). No instance of a readiness stage being
  marked `pass`/advanced by this feature exists anywhere in the chain; this feature touches no
  `readiness-status.yaml`.

## Axis 5 -- over-scope

PASS. Grounded against the actual file footprint, not just the plan's claim:

- The plan's Project Structure section lists exactly two new test modules
  (`tests/unit/test_dax_golden.py`, `tests/unit/test_warehouse_sql_golden.py`), a new
  `tests/fixtures/golden/` subtree (dax/ + sql/), and one optional standalone script. I found no
  task instructing an edit to `src/retail/dax_gen.py`, `src/retail/metric_drift.py`,
  `.claude/skills/retail-build-warehouse/SKILL.md`, `docs/rules/rules-manifest.json`,
  `docs/rules/severity-posture.json`, or any existing test file -- FR-009 forbids all of these and
  T022/T023/T024 are dedicated polish tasks that verify each stays byte-identical.
- No `retail check` rule or rule-id is added anywhere (FR-001; collision-avoidance allocation
  explicitly honored); T024 checks the manifest/severity-posture files are unchanged.
- The one mutation vector this feature introduces -- the optional regeneration script (FR-008,
  T019) -- is tightly bounded: T020 requires confirming by reading the finished script that it is
  not pytest-collected, not wired into the `retail` CLI or `retail check`, not referenced by any CI
  workflow, and contains no `git commit`/`git add` call. This is the correct shape for a
  human-reviewed convenience tool, not a new runtime authority.
- research.md's "Alternatives considered and rejected" section explicitly rejected two scope-
  expanding options (a new `retail check` rule for the SQL lock; a `retail` CLI subcommand for the
  regeneration helper) for the same collision-avoidance reason the spec's SCOPE GUARD states,
  showing scope discipline was actively exercised, not merely claimed after the fact.

No task or requirement reaches into another feature's declared territory (043's manifest, 046's
severity posture, the `retail-build-warehouse` skill's own authoring logic, or any of F016/F023/
F024's adapter surfaces).

## Minor notes (non-blocking; the build should honor these)

- **N1**: T021 proves the regeneration script is idempotent against the CURRENT generator output,
  but nothing in the task list re-runs that idempotency check after T010/T011 are (re)committed if
  their content changes for any reason before merge. Low risk given the ordering (T019-T021 run
  after T010-T011 per the Dependencies section), but worth a final sanity pass at PR time.
- **N2**: FR-006's normalization is implemented "inline... a small private helper function per
  module" (T006) rather than a single shared helper. This is a deliberate, stated choice (avoiding a
  new shared `src/retail/` utility for a test-only concern) and is acceptable, but the two inline
  implementations must be verified byte-identical in behavior at review time -- a divergence between
  the two modules' normalization helpers would be a subtle, hard-to-notice bug this test suite
  itself would not catch (neither module tests the other's normalization).
- **N3**: Resolve R1 (run `/speckit-analyze`, commit `analysis.md`) before this feature proceeds
  to implementation sign-off, per the same standard the 046 review applied to itself.

## Verdict

Verdict: FAIL

**FAIL**, solely on the missing analyze-stage artifact (R1). Every content axis (2 through 5, and
the content-level portion of axis 1) is a clean, well-grounded PASS -- the spec/plan/tasks chain is
internally careful, cites its precedents accurately, verifies its own call-shape claims against
source, and stays inside its collision-avoidance allocation with no hidden principle violation, no
deferred-capability assumption, no disqualifying C086 leak, and no fabricated score. But this same
review family's own precedent (046) states that a draft missing the analyze stage is an automatic
block, and feature 100 is missing it where every comparable feature in the dense 041-068 run of
this chain has one. Re-run `/speckit-analyze` to produce `analysis.md`, then re-submit for review;
given the clean content-level findings above, that follow-up review is expected to convert directly
to PASS-WITH-NOTES (folding in N1-N3) rather than surfacing new content problems.
