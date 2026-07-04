---
description: "Task list for 089-readiness-decay-demotion (Readiness Decay -- Drift Raises a Stale-Pass Demotion Blocker)"
---

# Tasks: Readiness Decay -- Drift Raises a Stale-Pass Demotion Blocker

**Input**: Design documents from `specs/089-readiness-decay-demotion/`
(spec.md, plan.md, research.md, data-model.md, quickstart.md)

**Tests**: Included -- plan.md's Testing section requires mutation-verified
fixtures (RS1/SF1/AP1/HR1 discipline) plus a controlled-commit-date fixture
repo for the git-history comparisons; this is a fail-closed governance rule,
not optional coverage.

**Status carried from plan.md**: DRAFT. This task list authors the design;
it does not itself constitute ratification. One item stays explicitly OPEN
per plan.md's "Open item carried to implement-stage" -- whether a
`stale_review` entry may also clear a drift-triggered (FR-002) finding. No
task below answers it; Phase 6 records it as a PENDING DEFAULT only.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3), or
  `SETUP`/`FOUND`/`POLISH` for cross-cutting phases
- Every task names an exact repo-relative file path

## Path Conventions

Single project (`src/retail/`, `tests/`, `docs/`, `templates/`) at repository
root, per plan.md "Structure Decision". No new project/service/top-level
directory. HR3 lands as `src/retail/rules/rule_hr3.py`, mirroring the shipped
`rule_sf1.py`/`rule_ap1.py` and the (design-stage) `rule_hr1.py` convention.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Reserve the rule id and the new schema key, then author the
docs/template surfaces BEFORE any rule code exists -- hard rule #8 (docs/
templates/checklists before automation). Nothing in this phase writes
`src/retail/rules/rule_hr3.py`.

- [ ] **T001** `[SETUP]` [OWNER SEAM] Confirm/ratify that the reserved
  static-rule id is **HR3** and the new `readiness-status.yaml` top-level key
  is **`stale_review`** (collision-avoidance allocation, per the feature's
  own header). No task below may rename either. Also re-verify the LIVE rule
  count against `docs/quality/rule-count-claims.yaml` /
  `docs/rules/rules-manifest.json` at this moment -- plan.md records 55 as of
  its own writing but flags this as a serialization point across ~19
  parallel in-flight features (including HR1/spec 087, itself still
  design-stage); do not assume any specific number without re-reading the
  live files in T014. _Satisfies: spec.md collision allocation; FR-001,
  FR-006._
- [ ] **T002** `[SETUP]` Author the `stale_review` shape into
  `templates/readiness-status.yaml`: a commented-out, additive example block
  (`stage`, `evidence`, `reviewer`, `at`, optional `note`) matching
  data-model.md entity 2's generic shape verbatim (illustrative field names
  only -- no domain specifics, Principle VII). A `readiness-status.yaml`
  scaffolded from this template with the block still commented out remains
  valid and unaffected (FR-006 back-compat). ASCII, UTF-8 without BOM
  (Principle IX). _Satisfies: FR-006, FR-016, data-model.md entity 2._
- [ ] **T003** `[SETUP]` Record, as a checklist item (not a code change) in
  this feature's own docs -- e.g. a short note appended to research.md's
  existing "Honesty limitation" section, or a new adjacent note if that
  section is treated as frozen -- the coverage-boundary the design already
  traced (research.md "Honesty limitation," lines ~229-260): an HR3-clean
  `retail check` run does NOT prove "this stage's evidence is fresh" for a
  stage whose `pass` cites evidence ONLY via a directory-shaped token (case
  (b) in data-model.md's extraction algorithm), because HR3 can only
  date-compare an evidence token that resolves to an exact tracked FILE.
  This note must exist before T017's docstring is written (T017 restates it
  in the shipped module) so the limitation is documented at the design layer
  first, not invented ad hoc in code comments. _Satisfies: hard rule #9
  (no false assurance dressed as a score), Principle V (agent does not imply
  a guarantee it cannot back)._
- [ ] **T004** `[SETUP]` Confirm (checklist task, no file edit beyond T002)
  that HR3 stays orthogonal to every neighbouring shipped surface named in
  spec.md's "Boundary against neighbouring shipped work": `docs/readiness/
  source-drift.md` is REFERENCE ONLY (not edited), RS1
  (`src/retail/rules/readiness_status.py`) is READ-ONLY reference (not
  edited), and no `.claude/skills/approval-console/`,
  `.claude/skills/evidence-pack-generator/`,
  `.claude/skills/approval-evidence-pack/`, `.claude/skills/
  readiness-viewer/`, `.claude/skills/retail-control-room/`, or
  `.claude/skills/run-next-readiness/` file is in this feature's footprint.
  _Satisfies: spec.md Boundary section, plan.md file-footprint fidelity._

**Checkpoint**: the `stale_review` schema shape is authored into the
template (human-readable, additive, back-compatible) and the feature's
boundary/limitation notes exist before any rule code is written.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Reserve the rule id across every wiring surface and produce a
stub module, mirroring the RS1/SF1/AP1/HR1 six-surface wiring discipline.
**No Finding-emitting logic is implemented yet in this phase** -- only the
scaffold that makes `@register("HR3", ...)` compile and be discoverable.
The new git-commit-date helper is deliberately NOT added here (US1 does not
need it -- see Phase 3); it is added at the head of Phase 4 (US2) so US1
stays a truly independent, git-free MVP slice.

**CRITICAL**: No user story (Phase 3+) can be implemented until this phase
is complete, because HR3 must exist as a registered (even if empty-bodied)
rule before its Finding-emitting logic can be tested via `retail check`.

- [ ] **T005** `[FOUND]` Create the stub rule module
  `src/retail/rules/rule_hr3.py` with `RULE_ID = "HR3"`, the module docstring
  (mirrors `rule_sf1.py`'s / RS1's shape: what HR3 does, what it never does --
  never writes any file, never auto-clears a `stale_review`, restates the
  T003 coverage-boundary limitation -- static-only, lazy `import yaml`
  inside the function body), and a
  `@register(RULE_ID, "readiness decay: stale_pass demotion blocker")`
  -decorated `check_hr3(ctx: RuleContext) -> Iterable[Finding]` that returns
  `[]` (stub body; Phase 3+ fills it in). Import and reuse RS1's
  `_owner_is_valid`, `_OWNER_SHAPE_RE`, `_AUTHORITY_CLASSES`,
  `_APPROVAL_REQUIRED`, and `_STAGE_ORDER` from
  `src/retail/rules/readiness_status.py` rather than redefining a second
  copy (research.md "REUSE, verbatim in shape"). _Satisfies: FR-001, FR-011,
  FR-015, data-model.md entity 1._
- [ ] **T006** `[FOUND]` Edit `src/retail/rules/__init__.py`: add `rule_hr3`
  to the side-effecting import tuple (alphabetical/id-ordered slot,
  consistent with wherever `rule_hr1` lands if it has already landed; re-verify
  order at implement time per T001) AND to `__all__` in the same commit --
  the ONLY discovery step (no autodiscovery). _Satisfies: FR-001 (wiring
  surface 1)._
- [ ] **T007** `[P]` `[FOUND]` Edit `tests/unit/test_rules_wiring.py`: add
  `"HR3"` to `EXPECTED_RULE_IDS`. _Satisfies: FR-001 (wiring surface 2)._
- [ ] **T008** `[P]` `[FOUND]` Edit `docs/rules/rules-manifest.json`: add
  `{"id": "HR3", "title": "readiness decay: stale_pass demotion blocker"}`
  in id order (re-verify current entries at implement time per T001 --
  do not assume HR1 has or has not already landed). _Satisfies: FR-001
  (wiring surface 3)._
- [ ] **T009** `[P]` `[FOUND]` Edit `docs/rules/severity-posture.json`: add
  `"HR3": ["error"]` under the registered section -- ERROR only. Every HR3
  finding (drift-triggered, approval-lag, unresolvable citation, unparseable
  approval date, invalid `stale_review` reviewer) is `Severity.ERROR`; there
  is no WARNING-only HR3 finding (data-model.md entity 1: "there is no
  WARNING-only HR3 finding for staleness itself"). _Satisfies: FR-001, FR-012
  (wiring surface 4)._
- [ ] **T010** `[FOUND]` Edit `docs/glossary.md`: add the `HR3` row to the
  rules table (reuse the `HR` family letter if HR1/spec 087 has already
  introduced it; otherwise this is the first `HR`-family row -- confirm
  against the live doc at implement time, do not assume either state)
  describing the stale-pass fail-closed posture in the same style as the
  `RS`/`SF` rows; bump the "Currently N rules" anchor by exactly one from
  whatever the live count is at implement time (re-verify per T001; do not
  hardcode a number here). _Satisfies: FR-001 (wiring surface 5)._
- [ ] **T011** `[FOUND]` Edit `docs/quality/rule-count-claims.yaml`: bump
  `claimed-count` for the `glossary-rule-count` entry by exactly one, kept
  byte-consistent with T010's anchor text. _Satisfies: FR-001 (wiring surface
  6)._
- [ ] **T012** `[FOUND]` Run `pytest -m unit tests/unit/test_wiring_meta_gate.py
  tests/unit/test_rules_wiring.py tests/unit/test_rule_count_claims.py` and
  confirm all green with the HR3 stub registered at the bumped count.
  _Satisfies: wiring + rule-count lockstep stays green._

**Checkpoint**: `HR3` is a real, registered, discoverable rule (currently a
no-op) and every meta-gate lockstep is green. User story implementation can
now begin.

---

## Phase 3: User Story 1 - Drift at Source Ready blocks every downstream `pass` from staying silently green (Priority: P1) MVP

**Goal**: When `stages.source_ready.status` is `warning` or `blocked`, HR3
emits one `stale_pass` ERROR finding per downstream stage recorded `pass`,
naming that stage and citing the drift signal -- or no finding when
`source_ready` is `pass`/`not_started`. This story reads only
`readiness-status.yaml`'s already-parsed YAML; it requires NO git-history
read at all, keeping it a self-contained, independently testable MVP slice.

**Independent Test**: set `stages.source_ready.status` to `warning` in a
table's `readiness-status.yaml` while `stages.mapping_ready.status` is
`pass`; run `retail check`; confirm it fails with an HR3 `stale_pass` finding
naming `mapping_ready`, and confirm the YAML file is byte-for-byte unchanged
after the run.

### Tests for User Story 1

> Write these tests FIRST; they FAIL against the Phase 2 stub before Phase 3
> implementation lands (RED), then PASS after (GREEN).

- [ ] **T013** `[P]` `[US1]` Fixture
  `tests/fixtures/stale_pass/drift_no_downstream_pass/readiness-status.yaml`
  -- `source_ready.status: pass`, every downstream stage `not_started` --
  used to assert zero findings. _Satisfies: US1 Acceptance Scenario 1._
- [ ] **T014** `[P]` `[US1]` Fixture
  `tests/fixtures/stale_pass/drift_single_downstream_pass/readiness-status.yaml`
  -- `source_ready.status: warning`, `mapping_ready.status: pass` (with
  evidence + a shape-valid approval so RS1-adjacent fields do not
  cross-contaminate the assertion). _Satisfies: US1 Acceptance Scenario 2._
- [ ] **T015** `[P]` `[US1]` Fixture
  `tests/fixtures/stale_pass/drift_multi_downstream_pass/readiness-status.yaml`
  -- `source_ready.status: blocked`, `mapping_ready`, `silver_ready`,
  `gold_ready` all `pass` -- used to assert exactly three findings, each
  naming its own stage. _Satisfies: US1 Acceptance Scenario 3._
- [ ] **T016** `[P]` `[US1]` Fixture
  `tests/fixtures/stale_pass/drift_not_started_no_finding/readiness-status.yaml`
  -- `source_ready.status: not_started` with a downstream `pass` -- used to
  assert HR3's drift check does NOT fire (that is an RS1-adjacent
  stage-order oddity, not a drift signal; FR-002 applies only to
  `warning`/`blocked`). _Satisfies: Edge Cases "not_started" bullet._
- [ ] **T017** `[P]` `[US1]` Fixture
  `tests/fixtures/stale_pass/drift_mechanical_stage_pass/readiness-status.yaml`
  -- `source_ready.status: warning`, `silver_ready.status: pass` (a
  mechanical stage with no `approvals[]` concept) -- used to assert the
  drift-triggered finding STILL fires for a mechanical stage (FR-011: the
  approval-lag check does not apply to mechanical stages, but the
  drift-triggered check does). _Satisfies: Edge Cases "mechanical stage with
  drift" bullet._
- [ ] **T018** `[US1]` `tests/unit/test_rule_hr3.py`: write the RED tests
  against T013-T017 fixtures asserting exact `Severity.ERROR` finding
  counts, message content (stage name + drifted `source_ready` status as the
  cited reason), and the `"<rel>:stages.<stage_name>"` locator shape; confirm
  they FAIL against the Phase 2 stub. Also assert, for T014/T015, that
  reading the fixture file's bytes before and after invoking `check_hr3`
  yields an identical result (no write occurred) -- the first instance of
  the SC-003 no-write assertion this feature repeats at every phase.
  _Satisfies: US1 Independent Test._

### Implementation for User Story 1

- [ ] **T019** `[US1]` In `rule_hr3.py`: implement `_iter_status_files(ctx)`
  reusing RS1's `_INSTANCE_RE` glob over `mappings/<table>/
  readiness-status.yaml` verbatim (same pattern, not a second regex).
  Depends on T005. _Satisfies: research.md input-source confirmation
  (per-table state file)._
- [ ] **T020** `[US1]` In `rule_hr3.py`: implement the drift-triggered check
  -- for each status file, parse (lazy `import yaml`), read
  `stages.source_ready.status`; when it is `warning` or `blocked`, iterate
  every OTHER stage in `_STAGE_ORDER` and, for each one recorded `pass`,
  emit `Finding(HR3, ERROR, "stage {stage!r} is pass but
  stages.source_ready.status is {drift_status!r} (drift signal,
  docs/readiness/source-drift.md); the human must re-confirm or demote this
  stage", "{rel}:stages.{stage_name}")`. One finding per stale stage, never
  rolled up (FR-002, hard rule #9). When `source_ready.status` is
  `not_started` or `pass`, this branch emits nothing. Depends on T019.
  _Satisfies: FR-002, FR-010, data-model.md message shape 1, US1 all
  Acceptance Scenarios._
- [ ] **T021** `[US1]` Run `tests/unit/test_rule_hr3.py` (T018) against the
  Phase 3 implementation and confirm GREEN (mutation-verified: flip
  `source_ready.status` back to `pass` in each fixture and re-confirm the
  finding disappears). _Satisfies: US1 Independent Test, SC-001, SC-003
  (first pass)._

**Checkpoint**: HR3 correctly fails closed on drift-triggered staleness for
both approval-bearing and mechanical downstream stages, is silent when
`source_ready` is clean or not-yet-profiled, and writes nothing. This is the
MVP slice -- independently testable and deployable without any git-history
dependency.

---

## Phase 4: User Story 2 - An approval-bearing `pass` whose evidence changed after sign-off must show a re-review (Priority: P1)

**Goal**: For an approval-bearing `pass` stage, HR3 compares each cited
evidence path's git AUTHOR commit date against the stage's latest
`approvals[].at` date and emits a `stale_pass` finding when the evidence is
strictly newer (day granularity); a distinct finding for an evidence token
that looks like a citation but does not resolve to a tracked file; and a
distinct finding for an unparseable/missing `approvals[].at`. This story
introduces the one new mechanical capability this feature requires: a
git-commit-date-of-a-path helper.

**Independent Test**: commit a change to an evidence path cited by an
already-`pass`, already-approved stage, with the new commit dated after the
recorded `approvals[].at`; run `retail check`; confirm an HR3 `stale_pass`
finding fires naming the stage, the changed evidence path, and both dates.

### `gitutil.py` helper (shared prerequisite for this story only)

- [ ] **T022** `[US2]` Edit `src/retail/gitutil.py`: add
  `git_last_commit_date(repo_root: Path, path: str) -> str | None` running
  `git log -1 --format=%aI -- <path>` via the existing `git_output` helper
  (AUTHOR date, per FR-004 -- NEVER `%cI` committer date, since a rebase or
  cherry-pick can rewrite committer date long after the content was actually
  written), using the `--` pathspec separator for the same option-injection
  safety `validate_commit_range` already gives ranges. Returns `None` when
  the path has no commit history (git exits 0 with empty stdout) --
  HR3 treats `None` the same as an unresolvable citation (FR-013's sibling
  case), never crashing and never silently skipping. _Satisfies: FR-004,
  data-model.md entity 6._
- [ ] **T023** `[P]` `[US2]` `tests/unit/test_gitutil.py` (new if it does not
  yet exist): build a small, controlled, throwaway fixture git repo per test
  (temp dir, `git init`, one commit with `GIT_AUTHOR_DATE` and
  `GIT_COMMITTER_DATE` env vars set explicitly) -- never read this repo's own
  live history for date assertions (plan.md Testing section: determinism,
  independent of when the fixture happens to be committed to `Seshat_BI`
  itself). Cover: (a) a normal commit where author date and committer date
  match -- helper returns that ISO date; (b) a path with zero commit history
  -- helper returns `None`; (c) **the author-vs-committer discriminator
  fixture required by plan.md's Testing section**: `GIT_AUTHOR_DATE` set
  BEFORE a reference approval date and `GIT_COMMITTER_DATE` set AFTER it
  (simulating a rebase/cherry-pick), asserting the helper returns the AUTHOR
  date -- this is the one fixture that actually pins FR-004's
  author-vs-committer discipline, since a fixture where both dates match
  cannot prove which field the helper reads. _Satisfies: FR-004 (the
  Testing-section-mandated straddling fixture)._

### Tests for User Story 2

> Write these tests FIRST; they FAIL against the Phase 3 implementation
> before Phase 4 lands (RED), then PASS after (GREEN). Fixtures use the
> same controlled-commit-repo technique as T023 (a throwaway git repo built
> inside the test, not this repo's live history), except where noted.

- [ ] **T024** `[P]` `[US2]` Fixture case
  `tests/fixtures/stale_pass/approval_lag_evidence_predates_approval/` --
  approval-bearing stage `pass`, cited evidence path's last AUTHOR commit
  predates the `approvals[].at` date -- used to assert zero findings.
  _Satisfies: US2 Acceptance Scenario 1._
- [ ] **T025** `[P]` `[US2]` Fixture case
  `tests/fixtures/stale_pass/approval_lag_evidence_after_approval/` -- same
  stage, cited evidence path's last AUTHOR commit is strictly LATER than the
  `approvals[].at` date -- used to assert exactly one `stale_pass` finding
  naming the stage, the evidence path, and both dates. _Satisfies: US2
  Acceptance Scenario 2._
- [ ] **T026** `[P]` `[US2]` Fixture case
  `tests/fixtures/stale_pass/approval_lag_same_day_not_stale/` -- evidence's
  commit AUTHOR date and `approvals[].at` fall on the exact same calendar
  date (day-granularity tie) -- used to assert zero findings (the confirmed
  "strictly later" / "same-day is not stale" default). _Satisfies: Edge
  Cases "same calendar date" bullet, Clarifications same-day default._
- [ ] **T027** `[P]` `[US2]` Fixture case
  `tests/fixtures/stale_pass/approval_lag_reapproval_clears/` -- starting
  from T025's stale state, add a SECOND, later-dated `approvals[]` entry for
  the same stage (on/after the evidence commit date) -- used to assert the
  finding no longer fires because HR3 compares against the LATEST
  `approvals[].at`, not the earliest. _Satisfies: US2 Acceptance Scenario 3,
  Clarifications "latest approvals[] entry wins" default._
- [ ] **T028** `[P]` `[US2]` Fixture case
  `tests/fixtures/stale_pass/approval_lag_malformed_approval_date/` -- two
  variants: (a) `approvals[].at` missing entirely; (b) `approvals[].at` an
  unparseable string (e.g. `"sometime in June"`) -- used to assert a
  DISTINCT `stale_pass`-family finding (message shape 4, FR-014) naming the
  parse failure, never a silently skipped stage and never a guessed date.
  _Satisfies: US2 Acceptance Scenario 4, FR-014._
- [ ] **T029** `[P]` `[US2]` Fixture case
  `tests/fixtures/stale_pass/multiple_evidence_one_changed/` -- an
  approval-bearing `pass` stage citing TWO resolving file evidence paths,
  only one of which has a post-approval commit -- used to assert exactly one
  finding fires (one changed citation is enough; not every cited path must
  have moved). _Satisfies: Edge Cases "multiple evidence paths" bullet,
  FR-003._
- [ ] **T030** `[P]` `[US2]` Fixture case
  `tests/fixtures/stale_pass/unresolvable_citation/` -- an evidence entry
  containing a path token whose PARENT directory is a real tracked
  directory (case (b) confirmed via a prefix test) but the named file itself
  does not exist there (data-model.md case (d)) -- used to assert a DISTINCT
  `stale_pass`-family finding (message shape 3, FR-013) naming the
  unresolvable citation. _Satisfies: FR-013, US2's sibling edge case "cited
  evidence path does not exist."_
- [ ] **T031** `[P]` `[US2]` Fixture case
  `tests/fixtures/stale_pass/prose_directory_token_no_finding/` -- an
  evidence entry naming a real tracked-directory prefix with no exact file
  match (e.g. a `metrics/`-shaped token, data-model.md case (b)) -- used to
  assert ZERO findings under both FR-003 and FR-013 (a bare directory
  reference is prose, not a citation). _Satisfies: research.md canary rows
  for `semantic_model_ready`/`dashboard_ready`-shaped directory tokens,
  SC-006 near-miss class 1._
- [ ] **T032** `[P]` `[US2]` Fixture case
  `tests/fixtures/stale_pass/prose_ruleid_range_token_no_finding/` -- an
  evidence entry containing a slash-bearing token whose PARENT path is NOT a
  real tracked directory at all (the exact `D1-D8/C1/R1/G6`-class near-miss
  research.md traced) -- used to assert ZERO findings (case (c): prose, not
  an unresolvable citation). Pin this so it cannot regress. _Satisfies:
  research.md "corrected resolution" case (c), SC-006 near-miss class 2._
- [ ] **T033** `[P]` `[US2]` Fixture case
  `tests/fixtures/stale_pass/prose_formatted_decimal_mechanical_stage/` -- a
  MECHANICAL stage (`gold_ready`) `pass` with an evidence entry containing a
  formatted-decimal token that punctuation-splits into something
  extension-shaped (e.g. `"1,552,071.00"` -> `"071.00"`, the exact
  research.md near-miss) -- used to assert ZERO findings, doubly: the token
  fails the step-2 candidate filter (no `/`, no exact tracked-file match)
  AND `gold_ready` is outside FR-013's approval-bearing scope entirely.
  _Satisfies: research.md "corrected resolution" adversarial case 2, SC-006
  near-miss class 3, FR-011 (FR-013 scoped away from mechanical stages)._
- [ ] **T034** `[P]` `[US2]` Fixture case
  `tests/fixtures/stale_pass/prose_bare_colisted_filenames_no_finding/` -- an
  approval-bearing `pass` stage (`dashboard_ready`-shaped) whose evidence
  lists a directory token alongside BARE co-listed filenames that do not
  themselves exactly match any `ctx.tracked_files` entry (the third
  adversarial case research.md traced: `"design authored: <dir>/
  (a.md, b.md, c.md)"` where the tracked files are the fully-qualified
  `<dir>/a.md` etc.) -- used to assert ZERO findings (the bare names are
  discarded as prose at the step-2 candidate filter, never reaching
  resolution). _Satisfies: research.md third adversarial case, SC-006 near-
  miss class 4._
- [ ] **T034a** `[P]` `[US2]` Fixture case
  `tests/fixtures/stale_pass/drift_and_approval_lag_same_stage/` -- a SINGLE
  stage that is simultaneously drift-stale (`stages.source_ready.status:
  warning`) AND approval-lag-stale (its own cited evidence path's commit
  date is strictly later than its latest `approvals[].at`) -- used to
  assert EXACTLY TWO findings for that stage, one of message shape 1
  (drift-triggered) and one of message shape 2 (approval-lag), with NO
  deduplication or merging into a single finding. This is the literal
  Clarifications MUST ("both findings fire independently... because each
  names a different root cause"), not a restatement of T020's per-stage
  no-rollup. _Satisfies: FR-002's combined-condition clause,
  Clarifications "both findings fire independently" default._
- [ ] **T034b** `[P]` `[US2]` Fixture case
  `tests/fixtures/stale_pass/approval_lag_two_evidence_both_changed/` --
  an approval-bearing `pass` stage citing TWO resolving file evidence
  paths, BOTH with a post-approval commit date -- used to assert exactly
  TWO findings (one per changed evidence path), not one rolled-up finding.
  Companion to T029 (which covers only one-of-two changed); together they
  pin FR-003's "no dedup, no rollup" across multiple evidence paths on the
  same stage. _Satisfies: FR-003 multi-evidence clause, T038's own
  "no dedup, no rollup" implementation note._
- [ ] **T035** `[US2]` `tests/unit/test_rule_hr3.py`: extend with RED tests
  over T024-T034b asserting exact finding counts, message content (stage +
  evidence path + both dates for the approval-lag case; the parse-failure
  text for T028; the unresolvable-citation text for T030), the
  two-distinct-message-shapes assertion for T034a, the two-findings
  assertion for T034b, and the no-write guarantee (repeat the SC-003
  byte-comparison assertion from T018 for every fixture in this batch);
  confirm FAIL against the Phase 3 implementation (which has no evidence/
  git-date branches yet). _Satisfies: US2 Independent Test._

### Implementation for User Story 2

- [ ] **T036** `[US2]` In `rule_hr3.py`: implement the cited-evidence-path
  extraction algorithm exactly as data-model.md entity 5 specifies --
  tokenize on whitespace and `()[]{}"';,`; step-2 candidate filter (a token
  is a candidate only if it contains `/` or exactly matches a tracked file);
  step-3 resolution against `ctx.tracked_files` in order: (a) exact file
  match -> cited evidence path; (b) real-directory-prefix with no exact
  match -> prose, no finding of either kind; (c) slash-bearing token whose
  PARENT path is not a real tracked directory -> prose, no finding; (d)
  parent path IS a real tracked directory but the full token does not
  resolve -> FR-013 unresolvable-citation finding. Scope this ENTIRE
  extraction call to the approval-bearing stage set (`_APPROVAL_REQUIRED`
  plus file-source `source_ready`, reused from RS1 per T005) -- a mechanical
  stage's `evidence[]` is never passed to this function at all (FR-011).
  Depends on T005, T019. _Satisfies: FR-003, FR-011, FR-013, data-model.md
  entity 5 (the exact algorithm), all of T030-T034's fixtures._
- [ ] **T037** `[US2]` In `rule_hr3.py`: implement the latest-`approvals[]`-
  entry selector -- for a given stage, among all `approvals[]` entries whose
  `stage` field matches, select the one with the latest parseable `at` date;
  if the ONLY entries present have an unparseable/missing `at`, emit the
  FR-014 finding (message shape 4) instead of silently skipping or
  defaulting the stage. Depends on T005. _Satisfies: FR-003 (latest-entry
  clause), FR-014, Clarifications "latest approvals[] entry wins."_
- [ ] **T038** `[US2]` In `rule_hr3.py`: implement the approval-lag
  comparison -- for each approval-bearing stage recorded `pass`: resolve its
  matching `approvals[].at` via T037; for each cited evidence path resolved
  via T036's case (a), call `gitutil.git_last_commit_date` (T022); truncate
  both dates to their calendar-date component and compare STRICTLY LATER
  (day granularity; same-day is NOT stale, per the Clarifications default);
  when the evidence's `None` commit-date result occurs, treat it the same as
  an unresolvable citation (FR-013's sibling case) rather than crashing;
  emit `Finding(HR3, ERROR, ...)` (message shape 2) naming the stage, the
  evidence path, the approval date, and the evidence's later commit date for
  each evidence path (not stage) that outruns the approval -- one changed
  citation is enough to fire, and multiple changed citations on the same
  stage each produce their own finding (no dedup, no rollup). Depends on
  T022, T036, T037. _Satisfies: FR-003, FR-004, hard rule #9 (no rolled-up
  finding), US2 Acceptance Scenarios 1-3, T024-T027/T029's fixtures._
- [ ] **T039** `[US2]` Run `tests/unit/test_rule_hr3.py` (T035) and
  `tests/unit/test_gitutil.py` (T023) against T022/T036-T038 and confirm
  GREEN, including the mutation-verify direction (edit a fixture's evidence
  commit date back to predate the approval and re-confirm the finding
  disappears) and the author-vs-committer discriminator (T023c) still
  passing. _Satisfies: US2 Independent Test, SC-002, SC-006 (near-miss
  fixtures all clean)._

**Checkpoint**: HR3 now fails closed on approval-lag staleness for a
resolving-file citation, distinguishes prose from citations exactly as the
canary requires, surfaces unresolvable citations and unparseable approval
dates as their own distinct findings, and still writes nothing. US1 and US2
together are the load-bearing pair the spec calls "equally load-bearing."

---

## Phase 5: User Story 3 - A human reaffirms a stale pass without re-running the whole approval, and the reaffirmation traces to a named person (Priority: P2)

**Goal**: A shape-valid, correctly-dated `stale_review` entry clears the
matching FR-003 approval-lag finding for its specific (stage, evidence)
pair. An invalid-shaped `reviewer` does not clear anything and raises its
own distinct finding. A backdated `stale_review` does not clear the
finding it targets. This story depends on US2 existing (there is nothing to
reaffirm against otherwise).

**Independent Test**: starting from the stale state in User Story 2's
"evidence after approval" fixture, add a `stale_review` entry naming a valid
`Person Name (authority_class)` reviewer dated on or after the evidence's
commit date; run `retail check`; confirm the HR3 finding for that
stage/evidence pair no longer appears, and confirm no other file was
modified.

### Tests for User Story 3

- [ ] **T040** `[P]` `[US3]` Fixture case
  `tests/fixtures/stale_pass/stale_review_clears_finding/` -- built on
  T025's stale state, add a `stale_review` entry naming `stage`, the exact
  triggering `evidence` path, a shape-valid `reviewer` ("Person Name
  (authority_class)"), and an `at` date ON or AFTER the evidence's commit
  date -- used to assert the FR-003 finding for that pair no longer fires.
  _Satisfies: US3 Acceptance Scenario 1._
- [ ] **T041** `[P]` `[US3]` Fixture case
  `tests/fixtures/stale_pass/stale_review_invalid_reviewer_shape/` -- same
  base, but `reviewer` is a bare role token (e.g. `"data_owner"`) with no
  name/class shape -- used to assert (a) the original FR-003 finding STILL
  fires (the invalid entry does not count), AND (b) a distinct FR-008
  invalid-reviewer finding (message shape 5) also fires. _Satisfies: US3
  Acceptance Scenario 2, FR-008._
- [ ] **T042** `[P]` `[US3]` Fixture case
  `tests/fixtures/stale_pass/stale_review_backdated/` -- same base, but
  `stale_review.at` is a date STRICTLY BEFORE the evidence's triggering
  commit date -- used to assert the original FR-003 finding STILL fires (a
  reaffirmation cannot predate the thing it reaffirms). _Satisfies: US3
  Acceptance Scenario 3, FR-007b._
- [ ] **T043** `[P]` `[US3]` Fixture case
  `tests/fixtures/stale_pass/stale_review_wrong_evidence_pair/` -- a
  `stale_review` entry naming the correct `stage` but a DIFFERENT evidence
  path than the one that triggered the finding -- used to assert the
  original finding STILL fires (an entry clears its own named (stage,
  evidence) pair only, never a whole stage's findings; hard rule #9's
  "no rolled-up clearing" per data-model.md field semantics). _Satisfies:
  data-model.md entity 2 field semantics ("never a whole stage's ... worth
  of findings at once")._
- [ ] **T044** `[US3]` `tests/unit/test_rule_hr3.py`: write RED tests over
  T040-T043 asserting exact clear/no-clear outcomes and, for T041, that BOTH
  findings (the original stale_pass AND the new invalid-reviewer finding)
  are present simultaneously; confirm FAIL against the Phase 4
  implementation (no `stale_review`-reading branch exists yet). _Satisfies:
  US3 Independent Test._

### Implementation for User Story 3

- [ ] **T045** `[US3]` In `rule_hr3.py`: implement `_stale_review_entries(data)`
  -- read the top-level `stale_review` list (absent/empty is valid, FR-006
  back-compat), returning each entry's `stage`, `evidence`, `reviewer`,
  `at`, optional `note` fields defensively (never crash on a malformed
  entry shape; a non-dict entry or missing required field is handled by the
  validity check in T046, not by crashing here). Depends on T005.
  _Satisfies: FR-006, data-model.md entity 2._
- [ ] **T046** `[US3]` In `rule_hr3.py`: implement the `stale_review`
  validity + clearing logic -- for each FR-003 approval-lag finding
  candidate (stage, evidence path, evidence commit date) computed in T038,
  look for a matching `stale_review` entry with the SAME `stage` AND the
  SAME `evidence` path; if found and (a) `reviewer` passes RS1's
  `_owner_is_valid` (reused, not redefined, per T005) AND (b) `at` parses
  and is on-or-after the evidence's commit date (day granularity, matching
  T038's truncation convention) -> suppress that specific FR-003 finding; if
  a matching entry exists but `reviewer` is NOT shape-valid -> do NOT
  suppress the finding AND additionally emit the FR-008 finding (message
  shape 5) naming the stage and the invalid reviewer value; if a matching
  entry exists but `at` predates the evidence's commit date -> do NOT
  suppress the finding (no additional finding needed -- FR-007's condition
  (b) failure is silent-non-clear, not a second error class). A
  `stale_review` entry naming a different `evidence` path than the one that
  triggered a given finding has no effect on that finding. Depends on T038,
  T045. _Satisfies: FR-007, FR-008, US3 all Acceptance Scenarios._
- [ ] **T047** `[US3]` Run `tests/unit/test_rule_hr3.py` (T044) against
  T045-T046 and confirm GREEN, including the mutation-verify direction
  (remove the `stale_review` entry from T040's fixture and confirm the
  finding reappears). _Satisfies: US3 Independent Test, SC-005._

**Checkpoint**: All three user stories are independently functional. A
human can reaffirm a specific stale approval-lag finding without a full
re-approval, an invalid reviewer shape never silently counts, and a
backdated reaffirmation never clears the thing it predates.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: The feature-wide guarantees that cut across all three stories
(no write, no score, canary clean, agent-behavior boundary, the OPEN
governance item) plus final gate/documentation sign-off.

- [ ] **T048** `[P]` `[POLISH]` Add a source-inspection test to
  `tests/unit/test_rule_hr3.py` asserting `rule_hr3.py`'s source contains no
  write/open-for-write call of any kind against a `readiness-status.yaml`
  path or any other tracked path (mirrors SF1/HR1's write-absence source
  test) -- and asserting no numeric percentage/ratio/decay/staleness/
  confidence/"N of M" formatting appears in any emitted message string
  across all five message shapes. _Satisfies: FR-005, FR-012, SC-003,
  SC-004 (mechanically verified, not just reviewed)._
- [ ] **T049** `[P]` `[POLISH]` Add an integration-style test (or extend
  `tests/unit/test_rule_hr3.py`) that runs `check_hr3` against
  `mappings/retail_store_sales/readiness-status.yaml` AS COMMITTED TODAY
  (the real file, not a fixture copy) and asserts ZERO HR3 findings --
  the literal SC-006 canary, re-verified at implement time (research.md's
  measured table may have shifted if the file was touched again since this
  plan was written; re-run `git log -1 --format=%aI -- <path>` for every
  cited evidence path at implement time rather than trusting the recorded
  dates verbatim). _Satisfies: SC-006._
- [ ] **T050** `[P]` `[POLISH]` Grep `src/retail/rules/rule_hr3.py`,
  `src/retail/gitutil.py`'s new helper, and `templates/readiness-status.yaml`'s
  new comment block for any C086/pharmacy/retail-domain-specific column,
  table, or metric name; confirm any illustrative name (e.g. the worked
  example in data-model.md) appears only in comments/docstrings, never as a
  required literal in rule logic. _Satisfies: Principle VII._
- [ ] **T051** `[POLISH]` Confirm (checklist task, no rule-code change) that
  FR-009 ("the agent MAY draft `stage`/`evidence`/`note` but MUST leave
  `reviewer` for a human to supply and MUST NOT commit a `stale_review`
  entry without a human-supplied reviewer name") is satisfied at the AGENT-
  BEHAVIOR layer, not the rule layer -- `rule_hr3.py` contains no
  entry-drafting or auto-fill logic of any kind (it is read-only, exactly
  like every other branch of this rule); any future skill-level tooling
  that drafts a `stale_review` entry (e.g. an Approval-Console-style
  surface) is OUT OF SCOPE for this feature and must itself honor FR-009
  when it is built. Record this boundary in `rule_hr3.py`'s module
  docstring (T005) if not already present. _Satisfies: FR-009, Principle V,
  data-model.md validation-rules-summary row ("agent behavior, out of rule
  scope")._
- [ ] **T052** `[POLISH]` [OWNER SEAM -- OPEN, do not answer] Record, as a
  checklist confirmation only (no code or schema change), that the question
  "does a `stale_review` entry also clear a drift-triggered (FR-002)
  finding?" remains OPEN per spec.md's Clarifications and plan.md's "Open
  item carried to implement-stage" -- this feature ships implementing
  FR-007 exactly as worded (clears FR-003 approval-lag findings for a named
  (stage, evidence) pair only; an FR-002 drift-triggered finding clears
  exclusively via a human edit to `stages.source_ready.status` or the stale
  stage's own status). No task in this list broadens that scope. _Satisfies:
  FR-007 PENDING DEFAULT posture, Principle V guard._
- [ ] **T053** `[POLISH]` Run the full local gate:
  `ruff format --check src/ tests/`, `ruff check src/ tests/`,
  `pytest -m unit -x -q`, then `retail check` and `retail kit-lint` --
  confirm GREEN on the current tree (T049's canary confirms zero new HR3
  findings against the real committed state). _Satisfies: SC-001 through
  SC-006 collectively, plan.md local-verification requirement._
- [ ] **T054** `[POLISH]` Confirm `tests/unit/test_wiring_meta_gate.py` and
  the rule-count test still pass at the bumped count from T011, and that
  `all_rules()` (not just `EXPECTED_RULE_IDS`) contains `"HR3"`.
  _Satisfies: wiring lockstep integrity._
- [ ] **T055** `[P]` `[POLISH]` Update `docs/glossary.md`'s `HR3` row (T010)
  if needed, and confirm `docs/readiness/source-drift.md` still reads
  correctly as the FIRST HALF of the sentence HR3 now enforces (this feature
  does not edit that file's text, per the Boundary section, but T055
  confirms no cross-reference update was missed elsewhere, e.g. a
  `docs/rules/rules-manifest.json` title mismatch against the final rule
  docstring). _Satisfies: documentation consistency, FR-001._

**Checkpoint**: Feature complete, gate green, no numeric score anywhere, no
domain-specific name baked into generic artifacts, wiring lockstep intact,
the canary stays clean, the agent-behavior boundary (FR-009) is recorded
where it belongs, and the one genuinely open governance question (FR-007
scope) is left open rather than silently decided.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies; T002-T004 require T001's owner-seam
  confirmation (id + key names) before authoring anything that names them.
- **Foundational (Phase 2)**: depends on Setup (the template shape from T002
  should exist so the stub module's docstring can reference the final
  `stale_review` shape) -- BLOCKS all user stories. T006 depends on T005;
  T007-T009 are parallel edits once T005 exists; T010 depends on T005 (needs
  the final rule title); T011 depends on T010 (count must match anchor);
  T012 depends on T006-T011 all landing.
- **User Stories (Phase 3-5)**: all depend on Foundational (Phase 2)
  completion (HR3 must be a registered, importable rule before its body can
  be tested). US1 (Phase 3) has NO dependency on git history and NO
  dependency on US2/US3 -- it is a pure YAML-read MVP. US2 (Phase 4) adds
  the `gitutil` helper (T022) as its own prerequisite, not a Foundational
  one, because US1 does not need it. US3 (Phase 5) depends on US2's T038
  (the approval-lag finding-candidate computation) -- a `stale_review` entry
  has nothing to clear until US2 exists.
- **Polish (Phase 6)**: depends on US1 + US2 + US3 all landing (T048's
  write-absence test and T049's canary run exercise all three stories'
  code paths together).

### Within Each User Story

- Fixtures before tests-that-use-them; tests written and RED before the
  matching implementation task; implementation before the GREEN re-run task.
- `_iter_status_files` (T019) is a shared read-only helper built once in
  Phase 3 and reused (not reimplemented) by Phase 4/5.
- The cited-evidence-path extraction algorithm (T036) and the latest-
  approval selector (T037) are built once in Phase 4 and reused by Phase 5's
  clearing logic (T046) via T038's finding-candidate list -- not
  reimplemented.

### Parallel Opportunities

- T007, T008, T009 (three different wiring-surface files) can run in
  parallel once T005/T006 exist.
- Within Phase 3, T013-T017 (five independent fixture files) can run in
  parallel.
- Within Phase 4, T023-T034 (twelve independent fixture/helper-test files)
  can run in parallel with each other (not with T022, which they depend on
  for T023, or with the implementation tasks T036-T038 they feed into).
- Within Phase 5, T040-T043 (four independent fixture files) can run in
  parallel.
- Within Phase 6, T048, T049, T050, T055 (independent files/checks) can run
  in parallel.

---

## Parallel Example: User Story 2

```bash
# Launch all independent US2 fixture-authoring tasks together:
Task: "Fixture case tests/fixtures/stale_pass/approval_lag_evidence_predates_approval/"
Task: "Fixture case tests/fixtures/stale_pass/approval_lag_evidence_after_approval/"
Task: "Fixture case tests/fixtures/stale_pass/approval_lag_same_day_not_stale/"
Task: "Fixture case tests/fixtures/stale_pass/prose_ruleid_range_token_no_finding/"
Task: "Fixture case tests/fixtures/stale_pass/prose_formatted_decimal_mechanical_stage/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational) -- HR3 registered as a
   no-op, wiring green.
2. Complete Phase 3 (US1) -- drift-triggered staleness fails closed for
   every downstream `pass` stage; a clean/not-yet-profiled `source_ready`
   stays silent. No git dependency at all.
3. **STOP and VALIDATE**: run T021's mutation-verified fixtures
   independently.
4. This is the MVP: the literal gap named in the feature description
   ("raise a stale_pass BLOCKER on every downstream stage built on the old
   profile").

### Incremental Delivery

1. Setup + Foundational -> HR3 registered, no-op, gate green.
2. Add US1 -> MVP -- drift-triggered downstream staleness.
3. Add US2 -> approval-lag staleness via git-commit-date comparison, plus
   the canary-verified prose/citation discrimination (co-equal load-bearing
   requirement per spec.md).
4. Add US3 -> the day-to-day `stale_review` reaffirmation escape hatch
   (P2, depends on US2).
5. Polish -> no-write/no-score mechanical verification, SC-006 canary
   re-check, agent-behavior boundary (FR-009) documented, FR-007 scope
   recorded OPEN, final six-surface gate confirmation.

### Requirement Coverage Check (every FR maps to >=1 task)

- FR-001 -> T005, T006, T018, T020
- FR-002 -> T020, T013-T017 tests, T034a (combined-condition no-dedup clause)
- FR-003 -> T036, T037, T038, T024-T027/T029/T034b tests
- FR-004 -> T022, T023(c), T038
- FR-005 -> T038/T046 (no write path exists), T048 (mechanically verified)
- FR-006 -> T002, T045
- FR-007 -> T046, T040/T042/T043 tests, T052 (scope recorded OPEN)
- FR-008 -> T046, T041 tests
- FR-009 -> T051 (agent-behavior boundary, not rule code)
- FR-010 -> T020 (no live runtime invoked)
- FR-011 -> T036 (scope to approval-bearing stages), T017/T033 tests
- FR-012 -> T009 (ERROR-only posture), T048 (mechanically verified)
- FR-013 -> T036, T030/T032/T033/T034 tests
- FR-014 -> T037, T028 tests
- FR-015 -> T004 (RS1 untouched), T005 (reuses RS1 helpers, no redefinition)
- FR-016 -> T002 (ASCII/UTF-8/no-BOM), applies to every new file this
  feature authors
- FR-017 -> T004 (no new stage, no `retail validate` check, no
  executor/adapter in this feature's footprint)
