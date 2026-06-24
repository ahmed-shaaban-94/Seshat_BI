# Tasks: dashboard design skill -- design a report FROM approved metric contracts

**Input**: Design documents from `specs/012-dashboard-design-skill/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: This is a docs/skill-first feature (roadmap rule 8). There is no code surface;
"tests" are fixture/audit reviews of the authored skill + a generic binding-map fixture.
No unit-test framework tasks are included.

**Organization**: Tasks are grouped by user story so each story is independently
authorable and reviewable. US1 (design from contracts) and US2 (refuse when gate not
pass) are both P1 and together form the MVP -- the gate AND the binding are the feature.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency)
- **[Story]**: US1 / US2 / US3 (or SETUP / POLISH)
- Paths are repo-relative and exact.

## Path Conventions

- Skill: `.claude/skills/dashboard-design/SKILL.md`
- Optional generic scaffolds: `templates/dashboard-layout.md`,
  `templates/visual-contract-binding-map.md`
- Stage doc (authoritative, already exists): `docs/readiness/dashboard-ready.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: create the skill skeleton and confirm the upstream gate inputs it reads.

- [ ] T001 [SETUP] Create `.claude/skills/dashboard-design/` and an empty `SKILL.md` with
      valid front-matter: `name: dashboard-design` and a `description` that says it
      designs a dashboard FROM approved metric contracts, is gated on `semantic_model_ready
      : pass`, authors guidance only, and never publishes / never calls pbi-cli/PBIP
      (so the agent auto-selects it for the right request and only then).
- [ ] T002 [SETUP] In `SKILL.md`, add the cross-references it depends on:
      `docs/readiness/dashboard-ready.md` (the stage contract),
      `docs/readiness/semantic-model-ready.md` (the prior stage / gate),
      `docs/readiness/readiness-model.md` (status + evidence + blockers),
      `docs/roadmap/roadmap.md` (hard rules 5/6/7/8), and `retail check` rule R1
      (relative model reference). No content authored yet -- just the See-also spine.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: author the two load-bearing boundary sections every user story relies on --
the hard gate and the author/publish boundary. Nothing else can be correct without these.

- [ ] T003 [US2] Author the **Hard gate** section in `SKILL.md` (rule 5): the skill MUST
      read the subject area's readiness status and verify `semantic_model_ready: pass`
      (approved contracts exist per F009 + the governed model binds to them per F010)
      BEFORE authoring any design; otherwise record `dashboard_ready: not_started` and
      STOP. State that `not_started` / `blocked` / `warning` of the prior stage all fail
      the gate (only `pass` authorizes design). [FR-001, FR-003]
- [ ] T004 [US3] Author the **Author vs publish boundary** section in `SKILL.md` (rule 6):
      authoring design text (layout plan, visual list, binding map, optional blank PBIR
      scaffold) is in-scope; EXECUTING -- generating/publishing the PBIR, opening
      DB/Desktop, calling pbi-cli/PBIP authoring automation -- is the deferred F016 seam.
      The skill authors, runs static `retail check`, and STOPS; name F016 as the owner of
      publishing. [FR-004]

**Checkpoint**: the gate and the boundary are written -- the two refusals the feature
exists to enforce are now expressible.

---

## Phase 3: User Story 1 - Design a dashboard from approved contracts (Priority: P1)

**Goal**: from `semantic_model_ready: pass`, author a layout plan + visual list + a
visual->contract binding map where every visual binds to one approved contract.

**Independent Test**: a generic fixture subject area with N approved contracts -> the
skill's binding map cites exactly its listed visuals, each -> one approved contract; an
auditor finds 0 orphan visuals and 0 silently dropped contracts.

- [ ] T005 [US1] Author the **Preconditions (STOP unless all hold)** list in `SKILL.md`:
      (1) `semantic_model_ready: pass`; (2) approved metric contracts (F009) are readable
      and each carries a recorded approval; (3) the governed PBIP model (F010) is present
      and binds measures to those contracts; (4) the analyst has supplied the business
      questions the page must answer (a Principle V input -- ask if missing). [FR-001,
      FR-008]
- [ ] T006 [US1] Author the **Procedure** in `SKILL.md` as a numbered, non-reorderable
      sequence: (a) read approved contracts + the business questions; (b) author the
      layout plan (page/section structure, reading order, one question per region);
      (c) author the visual list (per visual: type, the question it answers, the one
      approved contract it binds to -- visual type chosen to fit the contract's grain);
      (d) author the visual->contract binding map (the artifact the review signs off);
      (e) record `dashboard_ready: warning` + evidence + `next_action`; (f) STOP. [FR-002,
      FR-006, FR-010]
- [ ] T007 [P] [US1] (Optional, generic) Author `templates/dashboard-layout.md` and
      `templates/visual-contract-binding-map.md` as blank scaffolds (ASCII, UTF-8 no BOM,
      no C086/pharmacy values) the skill copies into a per-subject-area working set. If
      kept inline in the skill body instead, mark this task N/A in the analyze pass.
      [FR-009, FR-012]
- [ ] T008 [US1] Author the **R1 / relative-reference** note in `SKILL.md`: when a
      committed PBIR exists for the subject area, confirm `retail check` (R1) stays exit 0
      (model referenced by relative path, not absolute/remote); on failure record
      `dashboard_ready: blocked` with the reason and STOP. [FR-005]

**Checkpoint**: the happy path is authorable -- a reviewable design where every visual
maps to an approved contract.

---

## Phase 4: User Story 2 - Refuse to design when the gate is not pass (Priority: P1)

**Goal**: when `semantic_model_ready` is not `pass`, author NO design and record the
matching blocking reason. (The gate section, T003, is the spine; this phase makes the
refusal explicit and exhaustive.)

**Independent Test**: fixtures with `semantic_model_ready` in `not_started`/`blocked`/
`warning` each -> 0 design artifacts written + the matching blocking reason recorded.

- [ ] T009 [US2] Author the **Blocking reasons** section in `SKILL.md`, mirroring
      `docs/readiness/dashboard-ready.md`: prior stage not `pass`; orphan visual (no
      approved contract for a question); metric invented at design time; PBIR references
      the model by absolute/remote path (R1 fails). Each maps to a STOP. [FR-002, FR-003,
      FR-006]
- [ ] T010 [US2] Author the **No-invented-metrics** rule explicitly in `SKILL.md`: the
      skill binds ONLY to existing approved contracts; it never defines/alters a metric
      (that is F009). An unapproved-but-present contract is not a valid target -> orphan ->
      STOP. [FR-003]

**Checkpoint**: both P1 stories are authorable -- the MVP (gate + binding) is complete.

---

## Phase 5: User Story 3 - Stop at the design review and the publish boundary (Priority: P2)

**Goal**: the skill records `warning` (not `pass`), surfaces the design-review sign-off as
the next action, and never crosses into publishing/automation.

**Independent Test**: across runs the skill writes 0 `dashboard_ready: pass` without an
`approvals[]` entry, emits 0 publish/PBIP commands, opens 0 DB/Desktop connections.

- [ ] T011 [US3] Author the **No self-granted pass** rule in `SKILL.md`: the skill never
      writes `dashboard_ready: pass`; the highest it records is `warning` with
      `next_action: "get the design review (visual->contract binding) signed off by the BI
      report owner"`. A `pass` requires an `approvals[]` entry written by the reviewer,
      not the skill. [FR-007]
- [ ] T012 [US3] Author the **What the agent must NOT do** section in `SKILL.md`, mirroring
      the stage doc: do NOT invent metrics; do NOT design before contracts exist (rule 5);
      do NOT call pbi-cli/PBIP authoring automation or publish (rule 6, F016); do NOT
      open a DB/Desktop connection; do NOT self-grant `pass`. [FR-004, FR-007, FR-008]
- [ ] T013 [US3] Author the **Edge cases** handling in `SKILL.md`: more approved contracts
      than visuals (record a drop reason -- no silent omission); grain mismatch (record a
      `warning`-class note + propose the grain-appropriate visual); multi-table subject
      area (bind only within `pass` models); no questions supplied (ask, do not invent).
      [FR-008, FR-011]

**Checkpoint**: all three stories authorable; the publish boundary and the review boundary
are explicit.

---

## Phase 6: Polish & Cross-Cutting

**Purpose**: enforce the generic/encoding/secret invariants and verify consistency.

- [ ] T014 [P] [POLISH] Scan `SKILL.md` + any `templates/*` for C086/pharmacy specifics,
      real connection hosts/secrets, and non-ASCII/BOM; fix to generic placeholders, ASCII,
      UTF-8 no BOM. [FR-009, FR-012, SC-006]
- [ ] T015 [P] [POLISH] Verify the skill body satisfies every Success Criterion SC-001..
      SC-007 (binding 100%, gate holds, 0 publish commands, R1 exit 0, 0 self-granted pass,
      0 C086 specifics, 0 silent drops) and that each FR-001..FR-012 has a home in the
      skill text; record any gap for the analyze pass.
- [ ] T016 [POLISH] Confirm no new `retail check` rule and no `src/` change were introduced
      (reuse R1 only), and that the skill dir/name stays short for the Windows 260-char
      path limit (`dashboard-design`).

---

## Dependencies & Execution Order

- **Setup (T001-T002)** before everything.
- **Foundational (T003-T004)** -- the gate + the publish boundary -- block all user
  stories; do them right after setup.
- **US1 (T005-T008)** and **US2 (T009-T010)** are both P1 and together are the MVP. US2's
  refusal builds on the gate (T003); US1's happy path builds on preconditions (T005). They
  touch the same `SKILL.md`, so author US2's gate-facing sections and US1's procedure in
  sequence (one file), not in parallel.
- **US3 (T011-T013)** is P2; depends on US1's procedure existing (it constrains its tail).
- **Polish (T014-T016)** last.
- **[P] tasks** (T007 template scaffolds, T014/T015 scans) touch separate files / are
  read-only audits and may run in parallel with each other.

## Implementation Strategy

- **MVP = Setup + Foundational + US1 + US2.** That delivers the gate (refuse without
  contracts) AND the binding (design from contracts) -- the whole point of Stage 6.
- **US3 + Polish** harden the publish/review boundaries and the generic/encoding
  invariants.
- Single-file feature: most tasks edit `.claude/skills/dashboard-design/SKILL.md`; batch
  the edits to minimize rounds. The only separate files are the optional `templates/*`
  scaffolds.
