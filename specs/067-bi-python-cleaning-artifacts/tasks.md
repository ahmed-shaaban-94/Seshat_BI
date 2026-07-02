# Tasks: Land bi-python's Planned Cleaning Artifacts

**Input**: Design documents from `specs/067-bi-python-cleaning-artifacts/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: No automated tests apply -- this is a docs-only knowledge-skill change
with no runtime code and no new retail check rule. Verification is grep +
read-through against the spec's Success Criteria (SC-001..SC-006).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 (route ends on a real artifact), US2 (router honestly reflects
  the flip), US3 (fork boundaries stay intact)

## Path Conventions

All paths are under `skills/bi-python-knowledge/`. No new directories.

---

## Phase 1: Setup

- [ ] T001 Confirm working state: on branch `067-bi-python-cleaning-artifacts`,
  `checklists/` and `patterns/` dirs exist, and the four source files are present
  (`knowledge/cleaning-and-standardization.md`,
  `checklists/aggregation-grain-checklist.md`,
  `references/id-conventions.md`, `references/retail-dataframe-schema.md`).
  No files created in this phase.

---

## Phase 2: Foundational (Blocking Prerequisite)

**Purpose**: The new checklist file must exist before any route can point at it as
live. This is the single blocking artifact for the whole feature.

- [ ] T002 [US1] Author
  `skills/bi-python-knowledge/checklists/cleaning-review-checklist.md`,
  mirroring the SHAPE of `checklists/aggregation-grain-checklist.md`:
  a one-line purpose header naming it the cleaning-route terminal artifact;
  lettered sections of checkbox items; a Verdict block; an "Attach:" line.
  (FR-001, FR-002)

**Checkpoint**: After T002 the file exists; US1's acceptance scenario 1 can pass
even before the route flip. US2/US3 tasks depend on this file.

---

## Phase 3: User Story 1 -- Cleaning route ends on a real artifact (P1)

**Goal**: The checklist's CONTENT covers every cleaning concern the knowledge file
raises, cites only existing IDs, keeps human decisions human, and ends on a
categorical verdict + row-count ledger.

- [ ] T003 [US1] In the new checklist, add a section enforcing PY-BP-005 (clean
  only what profiling flagged) and covering string standardization (PY-CN-031) and
  category convergence to a known domain (PY-CN-032). (FR-003)
- [ ] T004 [US1] Add a section covering currency / numeric-as-text coercion with
  coerced-null counting (PY-CN-033) and invalid / out-of-range / sentinel handling
  (PY-CN-034); phrase sentinel-meaning and out-of-range keep-vs-flag as "recorded
  by a human" checkboxes. (FR-003, FR-007)
- [ ] T005 [US1] Add a deduplication section: declare the uniqueness key first,
  measure duplicates, and record the keep-policy as a human decision (PY-CN-035,
  guarding PY-AP-001). (FR-003, FR-007)
- [ ] T006 [US1] Add a grain / row-count accountability section (PY-CN-036) and a
  source-value traceability item (PY-CN-037); make the row-count ledger
  (rows in -> altered -> coerced-null -> dropped -> out) the "Attach:" evidence.
  (FR-003, FR-005)
- [ ] T007 [US1] Add the Verdict block as a small set of CATEGORICAL statuses
  (mirroring the aggregation checklist's four-state shape) with an explicit
  "[verdict vocabulary + pass criteria reserved for human ratification -- see
  spec ## Clarifications]" note; emit NO numeric score. (FR-006)
- [ ] T008 [US1] Audit every checklist item: each cites ONLY an ID that already
  exists in the cleaning content or `references/id-conventions.md`; NO new IDs
  minted. (FR-004, SC-004)

**Checkpoint**: US1 fully deliverable -- an agent can walk the checklist to a
verdict; the route (once flipped in US2) resolves to real content.

---

## Phase 4: User Story 2 -- Router honestly reflects the flip (P1)

**Goal**: Every "planned" reference to the cleaning-review checklist flips to live;
no unrelated sibling is flipped.

- [ ] T009 [US2] Edit `skills/bi-python-knowledge/INDEX.md`: remove the
  "Cleaning review checklist" row from the Planned-routes table; point the live
  cleaning task route AND the relevant symptom routes at
  `checklists/cleaning-review-checklist.md`; rewrite the "Cleaning route endpoint"
  note so it no longer says the checklist is planned; add the checklist under the
  shipped `checklists/` line in the File map. (FR-008)
- [ ] T010 [US2] Edit
  `skills/bi-python-knowledge/knowledge/cleaning-and-standardization.md`: rewrite
  the "Ends on" block and the PY-CN-033 / PY-CN-036 inline phrasing so the
  cleaning-review checklist is described as live (not "planned / not yet
  implemented"); leave the OTHER "planned" inline notes (profiling, dtypes,
  validation) untouched. (FR-009, FR-011)
- [ ] T011 [US2] [P] Edit `skills/bi-python-knowledge/README.md`: update the
  coverage claim so the cleaning route's endpoint is no longer listed among
  not-yet-built items, without claiming any other planned slice is complete.
  (FR-010, FR-011)

**Checkpoint**: US2 deliverable -- router + notes + README consistently show the
checklist as live; both US2 acceptance scenarios pass.

---

## Phase 5: User Story 3 -- Fork boundaries stay intact (P2)

**Goal**: The checklist references, rather than re-owns, the aggregation-grain and
single-node boundaries.

- [ ] T012 [US3] In the new checklist, ensure any groupby / grain / additivity
  concern is a ONE-LINE reference to `checklists/aggregation-grain-checklist.md`
  (owner), not a restated section. (FR-012, US3 scenario 1)
- [ ] T013 [US3] In the new checklist, ensure any large-data / distributed concern
  is a ONE-LINE handoff to `skills/bi-bigdata-knowledge/`, not an absorbed section.
  (FR-013, US3 scenario 2)

**Checkpoint**: US3 deliverable -- no duplicated ownership.

---

## Phase 6: Polish & Cross-Cutting Verification

- [ ] T014 [P] Verify all touched/new files are UTF-8 without BOM, ASCII-only
  (`--`, `->`, no glyphs), short repo-relative paths. (FR-015)
- [ ] T015 [P] Verify no inline C086 / pharmacy specifics in the checklist;
  examples use only `references/retail-dataframe-schema.md`. (FR-014, SC-006)
- [ ] T016 Final grep sweep: zero surviving references call the cleaning-review
  checklist "planned / not yet implemented" (SC-002); the set of remaining planned
  routes shrank by EXACTLY one (SC-005); the cleaning route + "Ends on" pointer
  resolve to an existing file (SC-001). Confirm FR-016 respected -- no roadmap
  F-row / readiness stage self-assigned anywhere.

---

## Dependencies

- T002 (Foundational) blocks everything else -- the file must exist first.
- Phase 3 (US1 content) and Phase 5 (US3 boundaries) both edit the NEW file, so
  they are sequential with each other on that file (not [P] among themselves).
- Phase 4 (US2) edits three OTHER files; T011 (README) is [P] vs T009/T010.
- Phase 6 verification runs last.

## Implementation Strategy

MVP = T002 + Phase 3 (US1) + Phase 4 (US2): the file exists, is correct, and the
route honestly points at it -- the dead-end is closed. US3 (fork boundaries) and
Phase 6 (constraints) harden it. All within the single-route scope; no pattern
files, no unrelated route flips (Clarification C1).
