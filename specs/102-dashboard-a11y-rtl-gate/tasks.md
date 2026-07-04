---

description: "Task list for Dashboard Accessibility + RTL/Arabic Readiness Checklist (102-dashboard-a11y-rtl-gate)"
---

# Tasks: Dashboard Accessibility + RTL/Arabic Readiness Checklist

**Input**: Design documents from `specs/102-dashboard-a11y-rtl-gate/`
(spec.md, plan.md, research.md, data-model.md, quickstart.md)

**Tests**: Not requested. This is a docs/template-only feature (no `src/`
change, no pytest surface); "tests" are the deterministic grep/verification
tasks in Polish, matching the F034 precedent's testing posture.

**Organization**: Tasks are grouped by user story (US1/US2/US3) per
spec.md's priorities (US1: P1, US2: P1, US3: P2). Every FR-xxx from spec.md
is tagged inline on at least one task below.

## SCOPE GUARD (read before touching any task)

This feature touches exactly FOUR repo paths. If a task would edit anything
under `src/retail/rules/`, `docs/rules/rules-manifest.json`,
`tests/unit/test_rules_wiring.py`, or `docs/roadmap/roadmap.md` -- STOP,
that is out of scope (no new `retail check` rule id; FR-008; SCOPE GUARD).

1. `templates/a11y-rtl-readiness-checklist.md` (NEW)
2. `docs/powerbi/visual-design-system.md` (EDIT, additive)
3. `docs/readiness/dashboard-ready.md` (EDIT, additive)
4. `mappings/retail_store_sales/design/a11y-rtl-readiness-checklist.md` (NEW, worked instance)

## Path Conventions

Docs/template feature -- no `src/`/`tests/` project layout applies. All
paths below are exact repo-relative paths from the constitution/plan/
data-model. No path is invented.

---

## Phase 1: Setup

**Purpose**: Confirm the prerequisite files this feature reads/cites are
present and confirm the toolchain this feature depends on (never
re-implements) actually runs, before any authoring begins.

- [ ] T001 Confirm all Phase-0 input files exist on disk (re-verify
  research.md R6): `design/tokens/tower-retail-design-tokens.yaml`,
  `themes/tower-retail.theme.json`, `src/retail/rules/design_contrast.py`,
  `docs/readiness/dashboard-ready.md`, `templates/visual-implementation-trace.md`,
  `mappings/retail_store_sales/design/dashboard-layout.md`,
  `mappings/retail_store_sales/design/visual-contract-binding-map.md`,
  `mappings/retail_store_sales/design/visual-list.md`,
  `docs/powerbi/visual-design-system.md`. Record a NO-GO if any are missing
  (none expected; research.md already confirmed presence).
- [ ] T002 Run `retail check` once, before any authoring, and record the
  full current rule-id set + pass/fail output to a scratch note (used later
  by T014's before/after diff for FR-008/SC-005, and by T011 to read CT1's
  CURRENT finding for `design/tokens/tower-retail-design-tokens.yaml`
  rather than assuming a clean result).

**Checkpoint**: Prerequisite files confirmed present; baseline `retail
check` output captured.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Fix the shared contract every later phase depends on --
the four target file paths, the stable heading-anchor names the
generic template (US1) will cite and User Story 3 will later fill in
under those same anchors, and the readiness-status header shape (four
statuses + `evidence[]` + `blocking_reasons[]`) reused verbatim from
`templates/visual-implementation-trace.md`. Fixing anchor names here
(rather than in US3) avoids a backwards dependency where US1's template
would otherwise have to wait on US3's prose section to exist first.

**CRITICAL**: No user-story authoring may begin until this phase is
complete.

- [ ] T003 Read `templates/visual-implementation-trace.md` in full and
  extract its exact readiness-status header shape (four statuses +
  `evidence[]` + `blocking_reasons[]` fields, FORBIDDEN OPERATIONS
  section, stop-and-ask section, `templates/module-contract.md`
  authority-matrix boundary language) as the literal shape to reuse for
  the new checklist template (FR-001; research.md R2).
- [ ] T004 Decide and record the two stable heading anchors that will live
  in `docs/powerbi/visual-design-system.md` and be cited by every filled
  checklist's `criteria_ref` field (data-model.md): `#colorblind-safe-palette-separation`
  and `#rtl-arabic-layout-readiness`. These exact anchor strings are the
  shared contract between the Foundational phase and both US1 (template
  cites them) and US3 (prose is authored under them) (FR-005, FR-006,
  FR-009).
- [ ] T005 [P] Confirm the exact insertion point in
  `docs/powerbi/visual-design-system.md` (the existing "Accessible
  contrast" paragraph, ~line 90 per research.md R6) where the two new
  criteria subsections (T004's anchors) will be appended, without altering
  any existing section's meaning (FR-009; Assumptions).
- [ ] T006 [P] Confirm the exact insertion point in
  `docs/readiness/dashboard-ready.md` (after the existing "Evidence item:
  'design approved' vs 'page implemented'" F034 subsection) where the new
  "Evidence item: a11y/RTL readiness checklist" subsection will be
  appended, without altering the gate, statuses, owner, or blocking-reasons
  shape above it (FR-008).

**Checkpoint**: Anchor names, header shape, and both insertion points are
fixed. User story authoring (Phase 3+) can now begin in priority order.

---

## Phase 3: User Story 1 - A dashboard cannot reach Dashboard Ready without a filled a11y/RTL checklist (Priority: P1) MVP

**Goal**: Define the generic checklist template (three required dimensions,
readiness-status header, forbidden-operations section) and wire it into
`dashboard-ready.md` as a REQUIRED `evidence[]` item whose absence or
partial fill is a recorded blocker.

**Independent Test**: For a page whose design-review is otherwise
complete, confirm `dashboard-ready.md` names the checklist as required
`evidence[]`, and confirm the template's own header makes clear an absent
or `<placeholder>`-containing checklist is a `blocking_reasons[]` entry.

### Implementation for User Story 1

- [ ] T007 [US1] Author `templates/a11y-rtl-readiness-checklist.md`: the
  generic copy-me template with the readiness-status header (four statuses
  + `evidence[]` + `blocking_reasons[]`, per T003's extracted shape),
  header fields `subject_area` / `page_id` / `filled_by` / `filled_at`
  (data-model.md), and three dimension placeholders (`contrast`,
  `colorblind_safe`, `rtl_arabic_layout`) each with a `disposition` field
  (`reviewed-clean` \| `not-applicable-with-reason` \| `blocked`) that is
  NEVER left blank (FR-001, FR-002, FR-007, FR-012).
- [ ] T008 [US1] In `templates/a11y-rtl-readiness-checklist.md`, add a
  FORBIDDEN OPERATIONS section (matching `visual-implementation-trace.md`'s
  shape from T003) explicitly naming: no render/open/publish/connect to
  Power BI Desktop, a live semantic model, or F016 (gated, does not exist)
  (FR-002, Principle VIII).
- [ ] T009 [US1] In `templates/a11y-rtl-readiness-checklist.md`, add a
  stop-and-ask section carrying forward BOTH open Principle-V questions
  verbatim (never answered by the template itself): Q-FR014-SCOPE
  (RTL-dimension applicability default) and Q-FR014-SEVERITY
  (block-vs-warning pass-bar) (FR-014).
- [ ] T010 [US1] Edit `docs/readiness/dashboard-ready.md` at T006's
  insertion point: add the "Evidence item: a11y/RTL readiness checklist"
  subsection stating the checklist is a REQUIRED `evidence[]` item before
  `dashboard_ready` may record `pass` for every page; an absent, missing,
  or partially-unfilled checklist (any dimension still carrying a
  `<placeholder>`) is a recorded `blocking_reasons[]` entry; NO new status,
  NO new gate, NO new `retail check` rule id, NO change to the existing
  owner/required-checks/blocking-reasons shape above it (FR-007, FR-008).
- [ ] T011 [US1] In the same `docs/readiness/dashboard-ready.md`
  subsection from T010, record the interim severity floor from
  Q-FR014-SEVERITY: an open finding in any dimension is recorded as AT
  LEAST a `warning`-class finding cited in `blocking_reasons[]` (or an
  equivalent warning-evidence entry); escalation to `blocked` is UNDECIDED
  pending the named-human ruling -- do not resolve it here (FR-011,
  FR-014).

**Checkpoint**: The template exists with all three dimension placeholders
and both required guard sections; `dashboard-ready.md` names the checklist
as required evidence with the interim severity floor recorded. User Story
1 is independently verifiable: a page missing the checklist is a named
blocker, per the stage-doc text alone.

---

## Phase 4: User Story 2 - The checklist cites CT1 rather than re-deriving contrast (Priority: P1)

**Goal**: Make the contrast dimension's shape and fill-procedure a pure
citation of CT1's registered result -- never an independently computed
ratio -- and fix the token-file resolution mechanic.

**Independent Test**: Fill the contrast dimension for a page whose token
file currently fails CT1 (or passes cleanly, per T002's captured baseline)
and confirm the dimension's disposition is a pure function of the CT1
result, never asserted independently.

### Implementation for User Story 2

- [ ] T012 [US2] In `templates/a11y-rtl-readiness-checklist.md`'s
  `contrast` dimension block (from T007), add the `token_file` and
  `ct1_result` fields and the derivation rule: `ct1_result: clean` ->
  `disposition: reviewed-clean`; `ct1_result: open-error \| parse-failure \|
  file-not-found` -> `disposition: blocked` (never `reviewed-clean` while
  CT1 reports an open finding) (FR-003, FR-004).
- [ ] T013 [US2] In `templates/a11y-rtl-readiness-checklist.md`'s
  `contrast` dimension block, document the `token_file` resolution
  mechanic: the SAME co-location convention `visual-implementation-trace.md`
  already uses -- the `*-design-tokens.yaml` file already associated with
  the page's design mapping under `mappings/<subject>/design/`. No new
  lookup mechanism, index, or naming convention is introduced (FR-015;
  Clarifications C1; research.md R5).
- [ ] T014 [US2] Add an explicit invariant note beside the `contrast`
  dimension block in `templates/a11y-rtl-readiness-checklist.md`:
  `disposition: reviewed-clean` implies `ct1_result: clean` and these two
  fields must never disagree -- the contrast dimension never re-derives a
  ratio that could contradict CT1's registered finding (FR-003; US2;
  SC-002).

**Checkpoint**: The contrast dimension's shape makes it structurally
impossible to mark `reviewed-clean` while citing an open CT1 finding.
User Stories 1 and 2 together are independently verifiable: the template
has all three dimension placeholders, the required guard sections, and a
citation-only contrast mechanic.

---

## Phase 5: User Story 3 - Colorblind-safe and RTL/Arabic dimensions are reviewed against committed, generic criteria (Priority: P2)

**Goal**: Document the fixed, generic colorblind-safe and RTL/Arabic
review criteria ONCE (under the anchors fixed in T004), wire the
template's two remaining dimensions to cite them, and produce the one
worked instance proving every citation resolves to a real path.

**Independent Test**: Fill the checklist for two different pages using the
same generic template; confirm both cite the identical criteria anchors
and neither the template nor the criteria doc contains a C086/pharmacy
domain noun or a literal Arabic string.

### Implementation for User Story 3

- [ ] T015 [US3] Edit `docs/powerbi/visual-design-system.md` at T005's
  insertion point: add the "Colorblind-safe palette separation" subsection
  (anchor `#colorblind-safe-palette-separation` from T004) documenting the
  fixed, generic criteria (do not rely on hue alone for adjacent series;
  pair color with a second encoding -- pattern, label, position -- for
  distinctions that matter; avoid red/green as the only distinguishing
  pair for pass/fail or good/bad) -- generic, no C086 color literal
  (FR-005, FR-009).
- [ ] T016 [US3] Edit `docs/powerbi/visual-design-system.md` immediately
  after T015's subsection (same file, same edit pass): add the "RTL/Arabic
  layout readiness" subsection
  (anchor `#rtl-arabic-layout-readiness` from T004) documenting the fixed,
  generic criteria (text direction / right-to-left reading order; mirrored
  visual/axis alignment where direction carries meaning, e.g. a trend's
  implied time direction; Arabic numeral/date formatting expectations) --
  generic, no literal Arabic string, no C086 specific (FR-006, FR-009,
  FR-013).
- [ ] T017 [US3] In `templates/a11y-rtl-readiness-checklist.md`'s
  `colorblind_safe` dimension block, add the `palette_source` and
  `criteria_ref` fields (`criteria_ref` pointing at T015's anchor) and the
  three dispositions (`reviewed-clean`, `not-applicable-with-reason` with
  `reason` when no multi-series palette is declared, `blocked` with
  `finding_detail` naming the defect and proposing the accessible
  alternative) (FR-005, FR-011; Edge Cases).
- [ ] T018 [US3] In `templates/a11y-rtl-readiness-checklist.md`'s
  `rtl_arabic_layout` dimension block, add the `layout_source` and
  `criteria_ref` fields (`criteria_ref` pointing at T016's anchor), the
  three dispositions, and the REQUIRED `scope_ruling_citation` field that
  is mandatory whenever `disposition: not-applicable-with-reason` is used
  -- an assumed default alone is NOT a valid citation; it must name an
  explicit human LTR-only ruling for that specific page (FR-006, FR-011,
  FR-014; Q-FR014-SCOPE interim floor).
- [ ] T019 [US3] In `templates/a11y-rtl-readiness-checklist.md`, add the
  staleness note (no automated detector; a human review-discipline
  obligation checked at the next design-review sign-off, per Clarifications
  C2): when the cited token/theme/layout file changes after a checklist is
  filled, the checklist is STALE and must be re-filled before the next
  `dashboard_ready: pass` claim relies on it (FR-010).
- [ ] T020 [US3] Read `retail check`'s CURRENT finding for
  `design/tokens/tower-retail-design-tokens.yaml` from T002's captured
  baseline (do not assume a clean result). Using that real finding, author
  the worked instance `mappings/retail_store_sales/design/a11y-rtl-readiness-checklist.md`:
  fill `subject_area: retail_store_sales`, a real `page_id` matching
  `mappings/retail_store_sales/design/visual-list.md`, and the `contrast`
  dimension citing `design/tokens/tower-retail-design-tokens.yaml` with
  the disposition that actually follows from T002's finding (`blocked` if
  CT1 reports an open error; `reviewed-clean` only if CT1 is clean)
  (FR-003, FR-004, FR-015; SC-002; SC-006).
- [ ] T021 [US3] In the same worked instance from T020, fill the
  `colorblind_safe` dimension citing `themes/tower-retail.theme.json`'s
  declared `dataColors` reviewed against T015's criteria, and the
  `rtl_arabic_layout` dimension citing
  `mappings/retail_store_sales/design/dashboard-layout.md` reviewed
  against T016's criteria -- real values only, no invented citation, no
  `not-applicable-with-reason` on the RTL dimension without an actual
  named-human LTR-only ruling for this page (none exists yet, so this
  dimension must be filled as actively reviewed, not exempted) (FR-005,
  FR-006, FR-009, FR-014; SC-006).
- [ ] T022 [US3] In the worked instance from T020/T021, set
  `overall_status` to the worst of the three filled dimension dispositions
  and populate `evidence[]` / `blocking_reasons[]` accordingly (never a
  numeric score) (FR-012; data-model.md roll-up rule).

**Checkpoint**: All three dimensions are fully specified in the generic
template, both criteria subsections exist under their fixed anchors, and
the worked instance proves every citation traces to a real, confirmed
repo-relative path with a real (not assumed) CT1 result.

---

## Phase 6: Polish & Cross-Cutting Verification

**Purpose**: Deterministic checks proving the feature's constraints hold
across all four authored/edited files (matches quickstart.md's
"Deterministic checks" section; no pytest suite for a docs-only feature).

- [ ] T023 [P] Grep `templates/a11y-rtl-readiness-checklist.md` and the two
  new subsections in `docs/powerbi/visual-design-system.md` for any
  `retail_store_sales`/C086/pharmacy-specific noun, color literal, or
  grain key. Expect zero matches (FR-009, SC-004).
- [ ] T024 [P] Grep `templates/a11y-rtl-readiness-checklist.md` for
  non-ASCII bytes (no literal Arabic string in the generic template).
  Expect zero matches (FR-013).
- [ ] T025 [P] Grep all four target files
  (`templates/a11y-rtl-readiness-checklist.md`,
  `docs/powerbi/visual-design-system.md`'s new subsections,
  `docs/readiness/dashboard-ready.md`'s new subsection, and the worked
  instance) for `score`/`confidence`/`health`/`maturity`/`completeness`
  used as a numeric field. Expect zero matches (FR-012, SC-003, hard
  rule #9).
- [ ] T026 Run `retail check` again and diff its rule-id set against
  T002's captured baseline. Confirm the registered rule-id set and rule
  count are IDENTICAL before/after (FR-008, SC-005).
- [ ] T027 Confirm every citation in the worked instance
  (`mappings/retail_store_sales/design/a11y-rtl-readiness-checklist.md`)
  resolves to a real file on disk
  (`design/tokens/tower-retail-design-tokens.yaml`,
  `themes/tower-retail.theme.json`,
  `mappings/retail_store_sales/design/dashboard-layout.md`) and that the
  cited CT1 result matches what `retail check` actually reports for that
  token file at authoring time (SC-006).
- [ ] T028 [P] Verify ASCII + UTF-8-without-BOM encoding on all four
  authored/edited files (Principle IX, FR-013).
- [ ] T029 Confirm both OPEN Principle-V questions (Q-FR014-SCOPE,
  Q-FR014-SEVERITY) remain unresolved -- carried forward verbatim, not
  defaulted -- in every authored artifact from this feature (template,
  criteria-doc extension, stage-doc edit, worked instance) (FR-014;
  Principle V; plan.md Post-Design Constitution Re-Check).
- [ ] T030 Run through `quickstart.md`'s per-page fill procedure end to
  end using the worked instance as the walkthrough example, confirming
  each numbered step in quickstart.md matches what the authored template
  actually requires.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies -- can start immediately.
- **Foundational (Phase 2)**: Depends on Setup (T001-T002) completion --
  BLOCKS all user stories (T004's anchor names are the shared contract
  US1's template and US3's prose both depend on).
- **User Story 1 (Phase 3)**: Depends on Foundational. No dependency on
  US2/US3.
- **User Story 2 (Phase 4)**: Depends on Foundational AND on US1's T007
  (the `contrast` dimension block T012-T014 extend must already exist as
  a placeholder). Independently testable per its own Independent Test.
- **User Story 3 (Phase 5)**: Depends on Foundational (T004's anchors) AND
  on US1's T007 (the `colorblind_safe`/`rtl_arabic_layout` placeholder
  blocks T017-T018 extend). T020-T022 (the worked instance) additionally
  depend on T012-T014 (US2's contrast mechanic) being authored first,
  since the worked instance fills all three dimensions together.
- **Polish (Phase 6)**: Depends on all three user stories being complete.

### Within Each User Story

- T007 (template skeleton with three placeholder blocks) precedes
  T008-T009 (same file, sequential -- not [P]).
  T010 precedes T011 (same file, sequential -- not [P]).
- T012-T014 are sequential (same `contrast` dimension block, same file).
- T015 and T016 are sequential (both edit `docs/powerbi/visual-design-system.md`
  at the same insertion point -- same-file edits are never [P] regardless
  of staffing).
- T017-T019 are sequential (same file, same template, different dimension
  blocks that must not collide).
- T020-T022 are sequential (building up the one worked-instance file).

### Parallel Opportunities

- T005 and T006 [P] -- different files (`visual-design-system.md` vs
  `dashboard-ready.md` insertion-point confirmation only, no content yet).
- T023, T024, T025, T028 [P] -- independent grep/verification passes over
  already-authored files, no mutation, no shared state.

---

## Requirement Coverage Map (FR-001 .. FR-015)

| Requirement | Task(s) |
|---|---|
| FR-001 (generic template shape, 3 dimensions) | T003, T007 |
| FR-002 (static; no render/open/publish/connect) | T007, T008 |
| FR-003 (contrast cites CT1, never re-derives) | T012, T013, T014, T020 |
| FR-004 (open CT1 error/parse-failure -> blocked, never reviewed-clean) | T012, T020 |
| FR-005 (colorblind-safe fixed generic criteria) | T015, T017, T021 |
| FR-006 (RTL/Arabic fixed generic criteria) | T016, T018, T021 |
| FR-007 (checklist required in `evidence[]`; absent/unfilled = blocker) | T007, T010 |
| FR-008 (no new status/stage/rule id; additive only) | T010, T011, T026 |
| FR-009 (generic; no C086 specifics; per-page path via design mapping) | T005, T015, T016, T023 |
| FR-010 (staleness = review-discipline, not mechanical detector) | T019 |
| FR-011 (defect -> warning/blocked finding with proposed alternative) | T011, T017, T018 |
| FR-012 (no numeric score/confidence/health/completeness) | T007, T022, T025 |
| FR-013 (ASCII/UTF-8-no-BOM; no literal Arabic in template; short paths) | T016, T024, T028 |
| FR-014 (two OPEN Principle-V questions carried forward, not defaulted) | T009, T011, T018, T029 |
| FR-015 (token-file resolution via existing co-location convention) | T013, T020 |

All 15 functional requirements map to at least one task. No task edits
`src/retail/rules/`, `docs/rules/rules-manifest.json`,
`tests/unit/test_rules_wiring.py`, or `docs/roadmap/roadmap.md`.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002).
2. Complete Phase 2: Foundational (T003-T006) -- fixes anchor names and
   insertion points so later phases never need to backtrack.
3. Complete Phase 3: User Story 1 (T007-T011) -- the template skeleton
   plus the stage-doc wiring that makes an absent checklist a blocker.
4. **STOP and VALIDATE**: Confirm `dashboard-ready.md` names the checklist
   as required evidence and the template's placeholder dimensions can
   never be left blank.

### Incremental Delivery

1. Setup + Foundational -> shared contract ready (anchors, header shape,
   insertion points).
2. Add User Story 1 -> template + stage-doc wiring exist -> MVP: a
   missing/unfilled checklist is now a named blocker.
3. Add User Story 2 -> contrast dimension is a pure CT1 citation,
   structurally unable to contradict the mechanical result.
4. Add User Story 3 -> criteria documented once, all three dimensions
   fully specified, worked instance proves real-path citations.
5. Polish -> deterministic verification (genericity, no score, rule-count
   unchanged, real citations, ASCII/no-BOM, both OPEN questions still
   open).

---

## Notes

- [P] tasks = different files (or independently-authorable content) with
  no dependency between them.
- [Story] label maps each task to its user story for traceability; every
  FR-xxx tag above is a literal substring match against spec.md, verified
  in the Requirement Coverage Map.
- This feature adds NO test suite (docs/template only); Polish tasks
  T023-T030 are the verification equivalent, matching F034's own
  docs-slice testing posture.
- Two Principle-V questions (Q-FR014-SCOPE, Q-FR014-SEVERITY) remain OPEN
  throughout every phase; no task may resolve them -- T009, T011, T018,
  and T029 exist specifically to keep them visibly carried-forward, not to
  close them.
- Stop at any checkpoint to validate a story independently before moving
  to the next priority.
