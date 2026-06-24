# Tasks: BI Handoff Pack

**Input**: Design documents from `specs/014-bi-handoff-pack/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Roadmap**: F013 (Layer 6). Advances **Publish Ready** (stage 7).

**Tests**: This is a docs/templates slice -- it ships NO code, so there are no
unit/integration test tasks. "Verification" tasks below are documentation
checks (cross-links, ASCII/UTF-8 no BOM, generic-only, checklist walk).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US4)
- All paths are repo-relative from the repository root.

## Path Conventions

- New templates: `templates/handoff/`
- Edited stage docs: `docs/readiness/`
- Spec chain: `specs/014-bi-handoff-pack/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the pack's home directory and confirm the inherited
artifacts the pack will reference.

- [ ] T001 Create `templates/handoff/` directory.
- [ ] T002 [P] Inventory the inherited artifacts the pack composes and confirm
  each exists: `templates/readiness-scorecard.md`, `templates/data-issues.md`,
  `templates/blocking-reasons.md`, `templates/readiness-status.yaml`,
  `templates/assumptions.md`, `templates/source-map.yaml`,
  `templates/reconciliation-report.md`, `docs/readiness/publish-ready.md`,
  `docs/readiness/readiness-model.md`. Record any missing input as a gap (do not
  create it here).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the pack's required-section contract that both the
template and the checklist must agree on. MUST complete before US1-US4.

**CRITICAL**: The required-section list is the single source both files key off.

- [ ] T003 Define the pack's REQUIRED-SECTIONS contract (the six required
  sections from FR-003: metric contracts, readiness scorecard, reconciliation
  evidence, known data issues/caveats, data dictionary, publish approval) as a
  short ordered list in the plan's terms. Both T004 and T006 use this exact list
  and order.

**Checkpoint**: Required-section contract fixed; pack template + checklist can be
authored against it.

---

## Phase 3: User Story 1 - Assemble a complete pack from existing evidence (Priority: P1) MVP

**Goal**: A copy-per-table pack template whose every required section points at
an existing committed artifact -- composes, invents nothing.

**Independent Test**: Copy the template for a generic `<schema>.<table>`, fill
each index row with a path to an existing artifact, walk it end to end; every
required item resolves to a committed file or is recorded as an explicit gap.

### Implementation for User Story 1

- [ ] T004 [US1] Author `templates/handoff/bi-handoff-pack.md`: header
  (generic-template banner + table identity placeholders `<schema>.<table>`,
  `<source_system>`, mapping version, deployed gold objects), and the
  **required-sections index** table (one row per T003 section: Section | Points
  at (existing artifact path) | Status (pass/warning/blocked) | Evidence/notes).
  Every row's "Points at" MUST be an existing-artifact path placeholder, never a
  new-content slot. Cite `docs/readiness/publish-ready.md` as the gate.
- [ ] T005 [US1] In the same file, add the **"Composes, never invents"** rule
  block + a "What this pack is NOT" block (not a publish action, not pbi-cli, not
  Fabric, not a confidence score) -- mirrors FR-008/FR-010 and publish-ready.md
  "What the agent must NOT do".

**Checkpoint**: A generic pack can be assembled from existing evidence; MVP
viable.

---

## Phase 4: User Story 2 - Record the publish approval (Priority: P1)

**Goal**: The pack carries the named, dated human publish approval and forbids
agent self-grant.

**Independent Test**: Walk the approval section: it provides the exact
`approvals[]` shape, forbids self-grant, and treats an absent approval as a
blocking reason (not auto-`pass`).

### Implementation for User Story 2

- [ ] T006 [US2] Author `templates/handoff/handoff-review-checklist.md`: one
  checklist line per required section (T003 order), each resolvable to
  "satisfied (evidence path)" OR "gap (recorded)"; plus the gate rule that ANY
  unsatisfied-and-unrecorded item = pack incomplete = `publish_ready` blocked.
  Reference `docs/readiness/publish-ready.md` blocking reasons verbatim.
- [ ] T007 [US2] Add the **Publish Approval** section to
  `templates/handoff/bi-handoff-pack.md`: the exact `readiness-status.yaml`
  `approvals[]` shape `{stage: publish_ready, owner: <data_owner|governance>,
  at: <YYYY-MM-DD>}`, the rule that the AGENT MUST NOT self-grant it (Principle
  V), and that an absent approval -> `publish_ready: blocked` (never auto-`pass`).

**Checkpoint**: Approval is a named human action; checklist enforces presence.

---

## Phase 5: User Story 3 - Honest caveats (Priority: P2)

**Goal**: Mandatory, honest caveats (PII / returns / known-gaps / out-of-scope)
sourced from existing artifacts.

**Independent Test**: The template's caveats section requires all four
statements; the checklist FAILS the pack if any is missing.

### Implementation for User Story 3

- [ ] T008 [US3] Add the **Known data issues / caveats** section to
  `templates/handoff/bi-handoff-pack.md` requiring four explicit statements: (a)
  PII exclusion, (b) returns/refunds handling, (c) known gaps sourced from
  `templates/data-issues.md` (with measured counts, never adjectives), (d)
  out-of-scope items. Each cites its source artifact (`data-issues.md`,
  `assumptions.md`).
- [ ] T009 [US3] Add the four caveats as FAIL conditions in
  `templates/handoff/handoff-review-checklist.md` (a missing caveat = pack
  incomplete), citing publish-ready.md blocking reasons. Mark PII-safety /
  returns-handling as HUMAN-decided inputs the pack records, not decides
  (Principle V).

**Checkpoint**: Caveats are mandatory and honest; gaps cannot be hidden.

---

## Phase 6: User Story 4 - Data dictionary against the deployed schema (Priority: P3)

**Goal**: Column-by-column dictionary keyed to the DEPLOYED `gold` schema.

**Independent Test**: The dictionary table lists every deployed column once and
no non-deployed column; the checklist requires it to match the deployed schema.

### Implementation for User Story 4

- [ ] T010 [US4] Add the **Data dictionary** section to
  `templates/handoff/bi-handoff-pack.md`: a column table keyed to deployed
  `<schema>.<table>` with columns Name | Type | Grain role (fact measure /
  dimension attribute / degenerate dim) | Business meaning (carried from
  `templates/source-map.yaml`). Gold-only (Principle III).
- [ ] T011 [US4] Add the "dictionary matches deployed schema" item to
  `templates/handoff/handoff-review-checklist.md` (every deployed column once;
  no non-deployed column), citing publish-ready.md blocking reason.

**Checkpoint**: Consumer has a deployed-schema-accurate dictionary.

---

## Phase 7: Spine wiring + verification (Cross-Cutting)

**Purpose**: Wire the pack into the readiness spine and verify the docs slice.

- [ ] T012 [P] Edit `docs/readiness/publish-ready.md`: in "Required artifacts"
  and "See also", reference the concrete pack template path
  `templates/handoff/bi-handoff-pack.md` + the checklist
  `templates/handoff/handoff-review-checklist.md` (FR-013).
- [ ] T013 [P] Edit `docs/readiness/readiness-model.md` "See also" / templates
  list to include the handoff pack template (spine consistency, FR-013).
- [ ] T014 Verify cross-links: every path referenced by the two new templates
  and the two edited docs resolves to an existing file (or, for stage-5 metric
  contracts not yet built, is explicitly marked PLANNED/F009-F010).
- [ ] T015 [P] Verify all delivered/edited artifacts are ASCII + UTF-8 without
  BOM and contain NO worked-example (C086/pharmacy) specifics (Principle VII,
  FR-009, FR-012).
- [ ] T016 Walk the handoff-review checklist against a generic placeholder table
  end to end; confirm SC-002/SC-003/SC-004 hold (every section resolves or is a
  recorded gap; missing caveat/reconciliation/dictionary/approval FAILS; no
  `pass` without prior stages + approval). Confirm SC-006: no publish/pbi-cli/
  Fabric step exists anywhere in the pack.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2 / T003)**: depends on Setup; BLOCKS US1-US4 (both
  files key off the required-sections contract).
- **US1 (Phase 3)**: depends on T003. The MVP.
- **US2 (Phase 4)**: depends on T003; T006 creates the checklist file that
  US3/US4 then extend; T007 extends the pack file from US1.
- **US3 (Phase 5)**, **US4 (Phase 6)**: depend on US1 (pack file) + US2
  (checklist file); independent of each other.
- **Phase 7**: depends on the template + checklist existing (US1/US2) and
  ideally all sections (US3/US4) for the final walk (T016).

### Within the slice (file-contention note)

- `templates/handoff/bi-handoff-pack.md` is touched by T004, T005, T007, T008,
  T010 -- these are SEQUENTIAL (same file), not `[P]`.
- `templates/handoff/handoff-review-checklist.md` is touched by T006, T009, T011
  -- also SEQUENTIAL.
- T012, T013, T015 act on different files and are `[P]`.

### Parallel Opportunities

- T002 (inventory) is `[P]` during Setup.
- After the two template files exist, the two stage-doc edits (T012, T013) and
  the encoding/generic scan (T015) can run in parallel.

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Phase 1 Setup -> Phase 2 contract (T003).
2. US1 (T004, T005): the pack index that composes existing evidence.
3. US2 (T006, T007): the checklist + the publish approval slot.
4. **STOP and VALIDATE**: a generic pack can be assembled, every section
   resolves to an existing artifact, and approval is a named human action.

### Incremental Delivery

1. MVP (US1+US2) -> a usable, gated handoff bundle.
2. + US3 (caveats hardened) -> honest, no hidden gaps.
3. + US4 (data dictionary) -> deployed-schema-accurate consumer doc.
4. + Phase 7 -> spine-wired and verified.

---

## Notes

- [P] = different files, no dependencies. Same-file tasks are sequential.
- This slice ships NO code: no validator, no pbi-cli, no publish path (rules #6,
  #8). All "tests" are docs checks.
- The pack COMPOSES existing readiness evidence; it never invents data, metrics,
  or a confidence number (rule #9, FR-010).
- PII-safety, business-rollup mappings, and grain/identity are HUMAN decisions
  the pack records, never auto-answers (Principle V).
- Keep every artifact generic; cite the worked example by reference only
  (Principle VII).
