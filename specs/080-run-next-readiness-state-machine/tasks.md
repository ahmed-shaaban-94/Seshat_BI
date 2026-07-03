---
description: "Task list for the Run-Next Readiness State Machine (specs/080-run-next-readiness-state-machine/)"
---

# Tasks: Run-Next Readiness State Machine

**Input**: Design documents from `specs/080-run-next-readiness-state-machine/`
(spec.md, plan.md, research.md, data-model.md, quickstart.md,
contracts/run-next-response.md)

**Prerequisites**: spec.md, plan.md, research.md, data-model.md, quickstart.md,
contracts/run-next-response.md (all present, all done as of this chain).

**Tests**: This feature is spec-only through this chain. The tasks below are
for a FUTURE implementation slice and are written now so that slice has an
unambiguous, dependency-ordered checklist. Tests are explicitly requested here
(fixture-based, per quickstart.md's 15 cases) because FR-006/NG-002/NG-009 are
safety properties that MUST be test-proven, not asserted.

**Organization**: Tasks are grouped by the plan's Product-Module shape: a
skill (agent procedure) is the primary deliverable; an optional Python helper
is a stretch deliverable clearly separated and marked optional.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on another
  unfinished task in this list).
- **[Story]**: Which user story (US1/US2/US3) or cross-cutting (X) the task
  serves.
- Exact file paths are given wherever the file is known from plan.md.

---

## STOP CONDITION -- READ BEFORE STARTING ANY TASK BELOW

This tasks.md is a planning artifact produced by the spec/plan/tasks/analyze
chain. **Do not commit, push, open a PR, or merge as part of executing this
chain.** A human reviews this spec dir first (see the ratify step this
workflow stops at). When a future session DOES implement these tasks:

- **STOP before any `git commit` / `git push` / PR creation** once the tasks
  below are complete, and hand back to the human for review -- do not
  self-merge.
- **NEVER run `git add -A` or `git add .`** at any point. Stage files
  individually by exact path (e.g. `git add .claude/skills/run-next-readiness/SKILL.md`)
  so an accidental unrelated change (a stray local artifact, a secret-bearing
  `.env`, an unrelated in-progress edit) cannot be swept into the commit.
- Do not skip hooks (`--no-verify`), do not force-push, do not touch
  `src/retail/rules/*.py` (no new rule ID), do not touch CI config, do not add
  a dependency.

---

## Phase 1: Setup

**Purpose**: Confirm the ground this implementation slice stands on before
writing anything.

- [ ] T001 Re-read `specs/080-run-next-readiness-state-machine/spec.md` in
      full and confirm no repo change since this chain was authored has
      altered `templates/readiness-status.yaml`, RS1
      (`src/retail/rules/readiness_status.py`), `retail-orchestrate`
      SKILL.md, or `readiness-viewer` SKILL.md in a way that invalidates an
      Assumption (A1-A8) or a boundary-gate claim in plan.md. If any drift is
      found, STOP and re-run `speckit-analyze` before continuing.
- [ ] T002 Confirm the feature branch is `080-run-next-readiness-state-machine`
      (or the equivalent working branch for the implementation slice) and
      that no unrelated changes are staged (`git status --short` clean or
      containing only expected in-progress files).

**Checkpoint**: Ground confirmed unchanged; safe to design the deliverable.

---

## Phase 2: Foundational (blocking prerequisites for every user story)

**Purpose**: Establish the one shared artifact every user story's behavior
depends on: the skill doc's scope-boundary and stage-order-walk sections. No
user-story-specific behavior can be written before this exists, because every
outcome type shares the same walk.

- [ ] T003 Create `.claude/skills/run-next-readiness/SKILL.md` with
      frontmatter (name: `run-next-readiness`; a description that triggers on
      "what's the next allowed action", "is this table blocked", "can I
      proceed to X yet", following the frontmatter style of
      `.claude/skills/readiness-viewer/SKILL.md`).
- [ ] T004 In that file, author the "Scope boundary" section: read-only;
      computes no truth; grants no approval; no fake confidence; generic (no
      C086/retail_store_sales specifics baked in); ASCII + UTF-8 no BOM.
      Mirror the phrasing discipline of `readiness-viewer`'s own scope-boundary
      section (do not merely copy it -- restate it for THIS feature's
      compute-vs-render distinction).
- [ ] T005 In that file, author the "Relationship to retail-orchestrate /
      readiness-viewer / RS1" section, restating the three boundary-gate
      deltas from `plan.md` verbatim (or near-verbatim) so a future reader
      does not need to cross-reference the spec dir to understand why a
      fourth reader of `readiness-status.yaml` exists.
- [ ] T006 In that file, author the stage-order-walk procedure section,
      transcribing the pseudocode in `data-model.md` "State Transitions" into
      agent-followable prose steps (the seven stages in fixed order; the
      five stop conditions; the approval-shape check citing RS1's
      `_owner_is_valid` by name).

**Checkpoint**: The skill's spine exists; every user-story task below adds a
section to this same file (or a fixture file), never restructures the spine.

---

## Phase 3: User Story 1 - "What is the one next allowed action?" (Priority: P1) -- MVP

**Goal**: The skill can answer the basic case: given an unblocked,
un-approval-gated table, return the correct single next action.

**Independent Test**: Fixture #1 from `quickstart.md` (source_ready pass,
rest not_started) produces `outcome: next_action, stage: mapping_ready`.

### Tests for User Story 1

- [ ] T007 [P] [US1] Write fixture #1 (unblocked forward case) as a minimal
      `readiness-status.yaml` excerpt under
      `tests/fixtures/readiness/run_next/us1_forward_action.yaml` (new
      directory; confirm no existing fixture dir should be reused first by
      checking `tests/fixtures/` for a `readiness` convention already in use).
- [ ] T008 [P] [US1] Write fixture #2 (blocked stage, matches quickstart.md
      row 2) under `tests/fixtures/readiness/run_next/us1_blocked.yaml`.
- [ ] T009 [P] [US1] Write fixture #3 variant (chain pass through
      dashboard_ready, publish_ready not_started, with the approval-timing
      ambiguity from quickstart.md resolved per its documented note) under
      `tests/fixtures/readiness/run_next/us1_publish_next.yaml`.

### Implementation for User Story 1

- [ ] T010 [US1] Author the "Forward action" response section of
      `.claude/skills/run-next-readiness/SKILL.md`: when the earliest
      non-`pass` stage is `not_started`, return `outcome: next_action` with
      `action_text` drawn from that stage's `docs/readiness/<stage>-ready.md`
      "Next allowed action" text (depends on T006).
- [ ] T011 [US1] Author the "Missing file" response section (fixture #8):
      when no `readiness-status.yaml` exists, return `next_action` @
      `source_ready` per `contracts/run-next-response.md` Example E.
- [ ] T012 [US1] Manually walk fixtures T007-T009 against the authored
      sections; record the result inline in a short "Verified fixtures"
      subsection of the SKILL.md (or a sibling `VERIFICATION.md` if preferred)
      so a reviewer can see the fixture-to-behavior trace without re-deriving
      it.

**Checkpoint**: User Story 1 is independently demonstrable -- the skill
answers the basic forward-action question correctly and traceably.

---

## Phase 4: User Story 2 - Stop at a named human-approval seam (Priority: P1)

**Goal**: The skill never recommends stepping past an ungranted or
shape-invalid approval.

**Independent Test**: Fixture #4 (bare-role owner on a `pass` `mapping_ready`)
produces `outcome: approval_required, stage: mapping_ready`, never
`next_action` past it.

### Tests for User Story 2

- [ ] T013 [P] [US2] Write fixture #4 (shape-invalid owner) under
      `tests/fixtures/readiness/run_next/us2_approval_invalid_owner.yaml`.
- [ ] T014 [P] [US2] Write fixture #5 (fully-approved chain through
      dashboard_ready) under
      `tests/fixtures/readiness/run_next/us2_approved_chain.yaml`.
- [ ] T015 [P] [US2] Write fixture #15 (file-source `source_ready` special
      case, source_kind: csv, pass, no source_ready approval) under
      `tests/fixtures/readiness/run_next/us2_file_source_approval.yaml`.

### Implementation for User Story 2

- [ ] T016 [US2] Author the "Approval required" response section of the
      SKILL.md: for each of the five approval-required cases (mapping,
      semantic_model, dashboard, publish, file-source-only source_ready),
      check `approvals[]` for a shape-valid entry using RS1's exact rule
      (cite `src/retail/rules/readiness_status.py::_owner_is_valid` by name
      and restate its shape requirement: `Person Name (authority_class)` with
      `authority_class` in `{analyst, governance, data_owner, metric_owner}`).
      Depends on T010 (shares the same walk structure).
- [ ] T017 [US2] Verify fixtures T013-T015 manually against T016; append to
      the "Verified fixtures" subsection from T012.
- [ ] T018 [US2] Cross-check T016's shape rule word-for-word against the
      CURRENT `_owner_is_valid`/`_OWNER_SHAPE_RE`/`_AUTHORITY_CLASSES`/
      `_ROLE_TOKENS` definitions in `src/retail/rules/readiness_status.py` at
      implementation time (not just at spec time) -- RS1 may have changed
      since this spec was authored (2026-07-03); if it has, update T016's
      restatement to match, per plan.md's "Operational Risks" drift warning.

**Checkpoint**: User Stories 1 AND 2 both work independently; the safety
property (never step past an ungranted approval) is fixture-proven.

---

## Phase 5: User Story 3 - Surface evidence gaps and disagreement (Priority: P2)

**Goal**: The skill never hides a `pass`-without-evidence stage or a
stored-vs-computed `next_action` disagreement.

**Independent Test**: Fixture #6 (gold_ready pass, empty evidence) produces a
`pass_without_evidence` caveat regardless of what the primary outcome is.

### Tests for User Story 3

- [ ] T019 [P] [US3] Write fixture #6 (pass without evidence) under
      `tests/fixtures/readiness/run_next/us3_pass_without_evidence.yaml`.
- [ ] T020 [P] [US3] Write fixture #7 (stored/computed next_action
      disagreement) under
      `tests/fixtures/readiness/run_next/us3_next_action_disagreement.yaml`.
- [ ] T021 [P] [US3] Write fixture #9 (malformed YAML), fixture #10
      (current_stage disagreement), fixture #12 (invalid status string) under
      `tests/fixtures/readiness/run_next/us3_input_defects.yaml` (may combine
      as three documented cases in one file with clear separators, or three
      files -- implementer's choice, but each case must remain independently
      referenceable).

### Implementation for User Story 3

- [ ] T022 [US3] Author the "Caveats" response section of the SKILL.md:
      `pass_without_evidence` (FR-009), `next_action_disagreement` (FR-010),
      `warning_carried_forward` (fixture #13), `dual_blocked` (fixture #14).
      Each caveat's `kind` and `detail` shape must match
      `contracts/run-next-response.md` exactly.
- [ ] T023 [US3] Author the "Input defect handling" section of the SKILL.md:
      missing file (already T011), malformed YAML, missing `stages` key,
      unrecognized stage-status value -- each returns `outcome: input_defect`
      per `contracts/run-next-response.md`, never a guessed default (FR-012).
- [ ] T024 [US3] Verify fixtures T019-T021 manually against T022/T023; append
      to "Verified fixtures."
- [ ] T025 [P] [US3] Write fixture #11 (all-pass terminal) and fixture #14
      dual-blocked case under
      `tests/fixtures/readiness/run_next/us3_terminal_and_dual_blocked.yaml`
      and #13 (warning carried forward) under
      `tests/fixtures/readiness/run_next/us3_warning_forward.yaml`; verify
      against T022.

**Checkpoint**: All three user stories are independently functional and
fixture-verified; the full 15-row quickstart.md table is covered.

---

## Phase 6: Optional Stretch -- Python Helper (DEFERRED unless explicitly requested)

**Purpose**: Only if a future reviewer decides the walk logic needs to be
guaranteed identical across every invocation via code rather than
agent-followed prose (see plan.md "Repository artifacts this feature PLANS").
**Do not build this phase unless a human explicitly asks for it** -- the
default delivery shape is the skill alone (Assumption A7).

- [ ] T026 [P] [X] (OPTIONAL) Create `src/retail/tools/run_next_readiness.py`
      -- stdlib-only, read-only, takes a parsed readiness-status mapping (not
      a file path, to keep I/O separate from logic) and returns a plain-data
      response matching `contracts/run-next-response.md`. MUST NOT import
      from `src/retail/rules/` (no rule-registry coupling) and MUST NOT
      register a rule ID via `@register`.
- [ ] T027 [X] (OPTIONAL) Add `tests/unit/test_run_next_readiness.py` covering
      all 15 quickstart.md fixture rows as parametrized pytest cases, marked
      `@pytest.mark.unit`.
- [ ] T028 [X] (OPTIONAL) Run `ruff format --check`, `ruff check`, and
      `pytest -m unit -x -q` restricted to the new file; confirm the existing
      suite's rule/test counts otherwise unchanged (no new `retail check`
      rule ID introduced by this file).

---

## Phase 7: Polish & Cross-Cutting

**Purpose**: Documentation, validation, and the safety-property proof that
applies across all three user stories.

- [ ] T029 [P] [X] Create `docs/tools/run-next-readiness.md` (usage + boundary
      doc, parallel to `docs/tools/readiness-viewer.md` if it exists, else
      parallel to a `docs/readiness/` sibling): what it is, when to use it
      vs. `retail-orchestrate`/`readiness-viewer`, the read-only contract, and
      a pointer to `contracts/run-next-response.md` for the exact shape.
- [ ] T030 [X] Run `retail check` and confirm exit 0 with the SAME rule count
      as immediately before this implementation slice began (zero new rule
      IDs). Record the exact before/after rule count.
- [ ] T031 [X] Run the read-only proof: after exercising every fixture
      (manually or via T027's pytest run, if built), run
      `git status --short` and confirm it shows ONLY the new files this slice
      intentionally added (SKILL.md, docs page, fixtures, optional helper +
      test) -- zero modified `mappings/**/readiness-status.yaml` or any other
      pre-existing tracked file.
- [ ] T032 [P] [X] Scan every new file for a numeric-score pattern (`%`,
      `score:`, `confidence`) appearing outside a comment/prose explanation of
      why it is deliberately absent; confirm zero live occurrences (SC-004).
- [ ] T033 [X] Update `specs/080-run-next-readiness-state-machine/quickstart.md`'s
      fixture table with the FINAL resolution of the T009/fixture-#3 and
      T014/fixture-#5 approval-timing ambiguity, once T016/T018 settle it
      against RS1's actual current behavior -- close the open note rather
      than leaving it open post-implementation.

**Checkpoint**: Feature is documentation-complete, gate-clean, and read-only
-proven.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies; run first.
- **Foundational (Phase 2)**: depends on Phase 1; BLOCKS all user stories
  (every story adds a section to the same SKILL.md spine T003-T006 create).
- **User Story 1 (Phase 3)**: depends on Phase 2. No dependency on US2/US3.
- **User Story 2 (Phase 4)**: depends on Phase 2 AND on T010 (shares the walk
  structure) -- but its fixtures (T013-T015) can be written in parallel with
  Phase 3's fixtures.
- **User Story 3 (Phase 5)**: depends on Phase 2 AND on T010/T016 (its
  caveats attach to outcomes those sections produce).
- **Phase 6 (Optional)**: depends on Phases 3-5 being complete (the Python
  helper must match already-verified agent-procedure behavior, not invent its
  own).
- **Phase 7 (Polish)**: depends on Phases 3-5 (documents/validates what
  exists); T033 depends specifically on T016/T018.

### Parallel Opportunities

- T007, T008, T009 (US1 fixtures) in parallel with each other.
- T013, T014, T015 (US2 fixtures) in parallel with each other, and with
  T007-T009 once Phase 2 is done.
- T019, T020, T021, T025 (US3 fixtures) in parallel with each other and with
  the US1/US2 fixtures.
- T029 (docs) and T032 (score scan) can run in parallel with each other and
  with Phase 6 if that phase is undertaken.

## Non-Goals Preserved (do not let implementation drift add these back)

- No task above writes to `mappings/**/readiness-status.yaml` -- every
  "write" task targets either the skill doc, a NEW test fixture file, docs,
  or an optional new Python module. If a future task seems to require editing
  an existing table's readiness status, that is scope creep -- stop and
  re-check against spec.md Non-Goals.
- No task adds a `src/retail/rules/*.py` file or an `@register` call.
- No task modifies `.claude/skills/retail-orchestrate/SKILL.md`,
  `.claude/skills/readiness-viewer/SKILL.md`, or
  `src/retail/rules/readiness_status.py` -- this feature is additive-only
  next to those three.
- No task adds a dependency to `pyproject.toml` or any lockfile.
- No task touches CI configuration.

## STOP before commit/push/PR (repeated, load-bearing)

Once every checked box above is complete for the scope a given implementation
session was asked to cover: **STOP.** Report what was completed, run the
validation commands in Phase 7, and hand back to a human for review before any
`git add` / `git commit` / `git push` / PR is created. Do not use
`git add -A` or `git add .` at any point -- stage the exact files this
feature touched, by name.
