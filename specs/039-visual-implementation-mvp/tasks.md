---
description: "Task list for Visual Implementation MVP (F034)"
---

# Tasks: Visual Implementation MVP (F034)

**Feature**: F034 (roadmap F-number -- authoritative) | **Spec directory**:
`039-visual-implementation-mvp` (next free on-disk slot -- the script numbers from the current
max `038`, not the first gap; the roadmap F-number is authoritative -- see
`docs/roadmap/roadmap.md` numbering note)

**Input**: Design documents from `specs/039-visual-implementation-mvp/`

**Prerequisites**: spec.md (required for user stories); plan.md (required) -- if plan.md is not
yet on disk, T002 pins the reference shapes that stand in for it before any artifact is authored.

**Tests**: This is a docs/templates/skill-only authoring slice (roadmap rule 8) -- no runtime
code, so there are no unit tests. Verification tasks (gate fixture, no-automation/no-publish
grep, ASCII/no-BOM sweep, C086-leakage grep, 1:1 trace check, discount-framing check,
`retail check` R1 green with rule count unchanged) stand in for tests and are included
explicitly.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1 build+trace / US2 gate / US3 boundary)
  or SETUP / FOUND (foundational) / POLISH
- All paths are repo-relative from the worktree root

## Path Conventions

Docs/templates/skill authoring slice -- no `src/`/`tests/`. Homes reused from F011A (017):
the new workflow goes under `.claude/skills/powerbi-dashboard-design/workflows/` (alongside
`powerbi-handoff.md`, per O-1 below); the generic trace template under `templates/`; an EVIDENCE
ITEM edit (not a gate) in `docs/readiness/dashboard-ready.md`. The worked-example page is built
by a HUMAN in Power BI Desktop and committed under
`powerbi/RetailStoreSales.Report/definition/pages/<id>/`; its filled trace lands under
`mappings/retail_store_sales/design/`. (Skill under `.claude/skills/`, NOT top-level `skills/`
-- the F011A Structure Decision the foundation already set.)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Pin the reference shapes to reuse and confirm the upstream gate is satisfied for
the worked example before any build is contemplated.

- [ ] T001 [P] [SETUP] Re-read the reference shapes to match house style EXACTLY: the input
      contract this slice consumes (`.claude/skills/powerbi-dashboard-design/workflows/powerbi-handoff.md`
      -- surface 4 build order + its Stop-and-ask / no-data-edit boundary); the stage doc whose
      EVIDENCE ITEM this slice adds (`docs/readiness/dashboard-ready.md` -- the gate + owner to
      inherit VERBATIM); the readiness vocabulary (`docs/readiness/readiness-model.md` -- four
      statuses + `evidence[]` + `blocking_reasons[]`, no score); a workflow header idiom
      (`workflows/powerbi-handoff.md`) and a template header idiom (`templates/visual-spec.yaml`).
      Capture the header/status/boundary idioms to reuse.
- [ ] T002 [P] [SETUP] Confirm the worked example's upstream inputs EXIST and the gate is
      cleared (read-only, no edit): the approved binding map
      (`mappings/retail_store_sales/design/visual-contract-binding-map.md` -- 10 visuals, all
      bound 1:1, design-review `approved` 2026-06-25), the visual list + layout
      (`visual-list.md`, `dashboard-layout.md`), and `semantic_model_ready: pass`
      (`mappings/retail_store_sales/readiness-status.yaml`). Note the empty target page
      (`powerbi/RetailStoreSales.Report/definition/pages/a1b2c3d4e5f600112233/page.json` -- zero
      visual containers today) and that `definition.pbir` already references the model by the
      RELATIVE path `../RetailStoreSales.SemanticModel` (R1 baseline). [FR-006, FR-007]

**Checkpoint**: house style for the workflow/template headers, the status vocabulary, and the
inherited boundary is pinned; the worked example's gate (contracts + sign-off + `pass`) is
confirmed cleared, so a build is legitimate to specify.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Fix the boundary facts that ALL generic artifacts (the workflow, the trace
template, the Dashboard Ready edit) reuse VERBATIM. Get these wrong and the artifacts drift
into a second gate, a new readiness stage, an automation step, or a re-design.

**CRITICAL**: No US1/US2/US3 artifact may be authored until these facts are fixed in one place.
They are the load -- the same four statements are copied identically into every artifact.

- [ ] T003 [FOUND] Resolve and RECORD Open Decision O-1 in `specs/039-visual-implementation-mvp/`
      (a short decision note in spec.md / plan.md): the implementation verification lives as a
      NEW WORKFLOW alongside `powerbi-handoff.md` (`workflows/visual-implementation-review.md`),
      NOT a standalone verb skill -- the reversible default, because the build is the natural
      continuation of surface 4 and reuses its inputs. State that a standalone verb skill is a
      later, separate decision if review prefers it (same posture F011A used for its
      router-vs-verb O-1). This task is closed only when O-1's resolution is written down. [FR-001]
- [ ] T004 [FOUND] Write the INHERITED-GATE statement (single source of truth, reused in the
      workflow + the trace template + the Dashboard Ready edit): no implemented-page evidence is
      recorded before the subject area's `semantic_model_ready` is `pass` AND the design-review
      sign-off is recorded (rule 5); this slice DEFINES NO new gate and is NOT a second source of
      truth -- the gate + design-review + `dashboard_ready: pass` stay owned by
      `docs/readiness/dashboard-ready.md` + F011/012. [FR-004, FR-005, FR-006]
- [ ] T005 [FOUND] Write the 1:1-TRACE rule VERBATIM: every measure-bearing visual on the built
      page maps to exactly ONE approved metric contract by name AND to a field present in the
      governed semantic model; a visual NOT in the approved binding map is an "orphan visual: not
      in approved binding map" and forces `trace: blocked`; a field absent from the model is
      "unmapped field" and forces `blocked`; filter-rail slicers are dimension controls, not
      trace rows (measure-bearing visuals only). [FR-003]
- [ ] T006 [FOUND] Write the NO-AUTOMATION / NO-PUBLISH boundary statement: this slice generates
      no PBIR, writes no DAX, changes no SQL, edits no semantic-model file, runs no
      pbi-cli / Power BI MCP command, and publishes nothing; the ONLY PBIR change is the human's
      Desktop save committed as plain text; any generation/publish request STOPS and names F016
      as the owner (rule 6). State VERBATIM that F034 is INDEPENDENT of F016, not blocked by it
      (rule 6 gates the automation, not the manual build). [FR-008, FR-009]
- [ ] T007 [FOUND] Fix the readiness vocabulary + Principle-V stop list for this slice: exactly
      four statuses (`not_started`/`blocked`/`warning`/`pass`) + `evidence[]` +
      `blocking_reasons[]`, NO score; the implemented-page result is an `evidence[]` item, never
      a new status; STOP triggers = a layout deviation discovered during the build, whether the
      sign-off covers the built page, whether a page faithfully realizes the design -- surfaced
      to the BI owner, never self-answered, never a self-granted `dashboard_ready: pass`.
      [FR-011, FR-012]

**Checkpoint**: O-1 is resolved on paper; the inherited-gate text, the 1:1-trace rule, the
no-automation/no-publish boundary, and the four-status/no-score/stop-list are fixed -- ready to
drop into every artifact identically.

---

## Phase 3: User Story 1 - Build the approved blueprint as a real PBIR page, reviewed in git (Priority: P1) -- MVP

**Goal**: Ship the generic implementation-review workflow + the generic trace template so an
agent can (a) restate the build order from the handoff notes, (b) define the git-diff review
checklist on the committed PBIR, and (c) define + emit the 1:1 trace -- verifying a
human-built page without ever authoring or publishing it.

**Independent Test**: against a subject area with an approved binding map, a human-built page,
and `semantic_model_ready: pass`, the agent produces a filled trace whose every row maps a built
measure-bearing visual to exactly one approved contract + a mapped field, the page diff is
plain-text reviewable, and R1 still passes (relative model path). [SC-001, SC-002]

- [ ] T008 [US1] Author `.claude/skills/powerbi-dashboard-design/workflows/visual-implementation-review.md`
      (surface 4 continuation, per O-1): front-matter consistent with `powerbi-handoff.md`; body =
      (1) Scope -- this workflow VERIFIES a human-built committed page, it authors no PBIR and
      publishes nothing; (2) Inputs consumed -- the approved binding map + visual list + layout +
      the `powerbi-handoff.md` build notes (referenced by name, never re-derived); (3) RESTATE the
      build order from the handoff notes (theme -> background -> visuals -> slicers/interactions
      -> mobile -> QA) -- restated, not re-derived (T004 input contract); (4) the GIT-DIFF REVIEW
      CHECKLIST a reviewer runs on the committed `definition/` (plain text only, no opaque
      `.pbix`; one visual container per approved measure-bearing visual; relative model path / R1;
      no hand-edited `report.json`/`diagramLayout.json`); (5) the 1:1 TRACE CHECK (T005); (6) the
      inherited gate (T004), the no-automation/no-publish boundary + F016 ownership (T006), and
      the Principle-V stop list (T007) embedded VERBATIM. Generic -- placeholders only, no
      subject-area values. [FR-001, FR-002, FR-003, FR-006, FR-008, FR-009, FR-011, FR-012]
- [ ] T009 [US1] Author `templates/visual-implementation-trace.md` (generic copy-me blank): a
      header idiom matching `templates/visual-spec.yaml`; a status line using the four statuses +
      `evidence[]`/`blocking_reasons[]` (no score); a one-row-per-built-measure-bearing-visual
      table with columns `visual_id | visual_type | bound_contract (approved, by name) |
      mapped_field(s) | PASS / blocking-reason`; an explicit "orphan visual / unmapped field ->
      blocked" rule (T005); a "filter-rail slicers are dimension controls, not trace rows" note;
      a "caveat carried to the page" slot (generic, e.g. `<rate>` / `<excluded>` / `<floor>`); and
      the inherited gate + no-publish boundary (T004, T006). Placeholders only -- no C086, no
      retail_store_sales values. [FR-003, FR-005, FR-010, FR-014]

**Checkpoint**: the generic workflow + trace template exist; an agent can verify any
human-built page against its approved binding map and emit a reviewable trace. MVP done.

---

## Phase 4: User Story 2 - Refuse to build (or bless) when the design is not approved (Priority: P1)

**Goal**: Make the gate + the orphan/unmapped failure modes load-bearing in the Dashboard Ready
doc and prove they fire -- recording the implemented-page EVIDENCE ITEM under the existing owner
WITHOUT adding a new stage, status, gate, or `retail check` rule.

**Independent Test**: for each non-`pass` `semantic_model_ready` status and for a
`pass`-but-no-sign-off fixture, an "implement the page" request yields 0 implemented-page
evidence + the matching blocking reason; a built page carrying a visual absent from the approved
binding map yields `trace: blocked` with "orphan visual: not in approved binding map". [SC-002, SC-003]

- [ ] T010 [US2] Edit `docs/readiness/dashboard-ready.md`: add the implemented-page result as an
      EVIDENCE ITEM under the EXISTING owner -- distinguish "design approved" (the existing `pass`
      basis) from "page implemented" as evidence a `pass` MAY record
      (`evidence: built-page traces to the approved binding map; R1 passes`). Make NO change to
      the gate, the four statuses' meaning, the blocking reasons, the required checks, the owner,
      or the design-review responsibility; add NO new status and NO new `retail check` rule. Add a
      pointer to `workflows/visual-implementation-review.md` + `templates/visual-implementation-trace.md`
      as the procedure + evidence artifact. The edit is additive (one evidence-item note + one
      pointer), verifiable by diff. [FR-005, FR-006]
- [ ] T011 [US2] Verify (read-only, against the spec) that the workflow + template encode the
      REFUSAL paths from US2: (a) `semantic_model_ready` not `pass` -> 0 evidence + "no approved
      contracts -- Dashboard Ready gate, rule 5", point upstream; (b) `pass` but no recorded
      design-review sign-off -> bless no built page + "design-review sign-off not recorded";
      (c) an orphan visual -> `trace: blocked` + "orphan visual: not in approved binding map";
      (d) an unmapped field -> `trace: blocked` + "unmapped field". Confirm each refusal text is
      present VERBATIM and the building/blessing is what is refused, not the design approval
      itself (building never DOWNGRADES a legitimately-approved design). [FR-003, FR-006, FR-011]

**Checkpoint**: the gate + orphan/unmapped failure modes are present in the doc + the
artifacts; the Dashboard Ready edit added only an evidence item + a pointer (no new
stage/status/gate/rule).

---

## Phase 5: User Story 3 - Build the retail_store_sales worked example and stay inside the manual / no-publish boundary (Priority: P1)

**Goal**: Realize the approved 10-visual page for `retail_store_sales` as a HUMAN Desktop build
committed as plain-text PBIR, produce the filled trace, and prove the slice crossed no
automation/publish boundary.

**Independent Test**: an auditor confirms the committed
`powerbi/RetailStoreSales.Report/definition/pages/<id>/` contains one visual container per
approved measure-bearing visual, each trace row maps a built visual to exactly one approved
contract + a mapped field, the diff is plain text (0 opaque `.pbix`), the discount visual shows
50.37% with caveats, R1 passes, and the slice emitted 0 generation/publish/DAX/SQL/model edits. [SC-001, SC-004, SC-007]

- [ ] T012 [US3] **HUMAN Desktop action (the agent VERIFIES, does NOT author).** A human opens
      `powerbi/RetailStoreSales.Report` in Power BI Desktop, builds the approved 10 visuals
      (v01-v10 from `visual-contract-binding-map.md`) onto the page following
      `workflows/visual-implementation-review.md`'s restated build order, selecting the EXISTING
      approved measures (writing no DAX), keeps the model reference relative, saves as plain-text
      PBIR (PBIP), and commits `definition/`. The agent does NOT generate PBIR, does NOT
      hand-edit `report.json`/`diagramLayout.json` or visual-container JSON, and does NOT publish
      -- it confirms a real Desktop save produced the diff. [FR-002, FR-009, FR-008]
- [ ] T013 [US3] Produce the filled trace
      `mappings/retail_store_sales/design/visual-implementation-trace.md` from the committed page:
      one row per built measure-bearing visual (v01-v10) -> its one approved contract by name
      (TotalSales / TransactionCount / AvgTransactionValue / DiscountedTransactionRate /
      TotalQuantity) -> the mapped field(s) from the binding map -> PASS; status `pass` only if
      all 10 rows trace cleanly; the filter-rail slicers (date/category/location/payment_method)
      are NOT trace rows. Record the build-page evidence as the Dashboard Ready `evidence[]` item
      ("built-page traces to approved binding map; R1 passes") -- recorded, never a self-granted
      `pass`. [FR-003, FR-005, FR-012, FR-013]
- [ ] T014 [US3] In the built v04 discount card AND its trace row, frame
      `DiscountedTransactionRate` as the APPROVED 50.37% (discounted / known-status) WITH the
      contract caveats (33.39% unknown status excluded; 33.55% floor if unknowns were treated as
      not-discounted), sourced from `mappings/retail_store_sales/metrics/DiscountedTransactionRate.yaml`
      -- never the retracted/stale figure. [FR-013, SC-007]

**Checkpoint**: the worked example is a committed, reviewable PBIR page with a filled
1:1 trace at `pass`, the discount visual carries the corrected 50.37% framing, and no
automation/publish/data-edit was performed.

---

## Phase 6: Polish & Cross-Cutting Verification

**Purpose**: Whole-feature gates spanning all three stories. These stand in for tests.

- [ ] T015 [POLISH] Gate fixture: for each non-`pass` `semantic_model_ready` status on an
      "implement the page" request, and for a `pass`-but-no-sign-off fixture, confirm 0
      implemented-page evidence + the matching blocking reason; confirm an orphan visual yields
      `trace: blocked` ("orphan visual: not in approved binding map") and an unmapped field yields
      `blocked` ("unmapped field"). [SC-002, SC-003]
- [ ] T016 [P] [POLISH] No-automation / no-publish grep across all new/edited files: 0 generated
      PBIR, 0 pbi-cli / Power BI MCP commands, 0 publish actions, 0 DAX, 0 SQL changes, 0
      semantic-model edits; confirm the only PBIR change is the human-built page committed as
      plain text (a Desktop save, by diff), and F016 is named as the owner of any
      generation/publish. [SC-004, FR-008]
- [ ] T017 [P] [POLISH] 1:1 trace check on the worked example: the committed
      `definition/pages/<id>/` contains one visual container per approved measure-bearing visual
      (v01-v10), each maps to exactly one approved contract + a mapped field, 0 orphans, 0
      unmapped fields, 0 opaque `.pbix` committed; the diff is plain-text reviewable. [SC-001, SC-002]
- [ ] T018 [P] [POLISH] Discount-framing check: grep the built v04 card + the filled trace for
      `50.37%` WITH its caveats (33.39% unknown excluded; 33.55% floor) and confirm 0 occurrences
      of the retracted/stale rate anywhere in the built page or the trace. [SC-007]
- [ ] T019 [P] [POLISH] C086/pharmacy-leakage grep across every GENERIC artifact (the workflow,
      the trace template, the Dashboard Ready edit) -- expect zero subject-area specifics; a
      reviewer scanning every generic file finds only placeholders. Worked values appear ONLY in
      the per-subject-area instance. [SC-006, FR-010]
- [ ] T020 [P] [POLISH] No-new-stage / no-new-gate proof (by diff): confirm 0 new readiness
      stages, 0 new readiness statuses, 0 new `retail check` rules; the implemented-page result
      is recorded ONLY as an `evidence[]` item under the existing Dashboard Ready owner; the
      `dashboard-ready.md` edit altered only an additive evidence-item note + a pointer (gate,
      owner, statuses, blocking reasons, required checks unchanged); 0 self-granted
      `dashboard_ready: pass`. [SC-005, SC-008, FR-005]
- [ ] T021 [POLISH] Run `retail check` over the repo: exit 0, R1 passes (PBIR references the
      model by the relative path `../RetailStoreSales.SemanticModel`), and the rule count is
      UNCHANGED. Confirm all new/edited files are ASCII + UTF-8 no BOM (no em-dash, smart quote,
      arrow, or emoji), repo-relative paths `<= 200` chars, the PBIR page folders stay under the
      Windows 260-char limit, and 0 real hosts/secrets appear in any committed file. [SC-005, SC-009, FR-014]

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies -- start immediately. T001 and T002 are parallel
  (different reads).
- **Foundational (Phase 2)**: depends on Setup; BLOCKS all user stories. It resolves O-1 and
  fixes the inherited-gate text, the 1:1-trace rule, the no-automation/no-publish boundary, and
  the four-status/no-score/stop-list every artifact reuses verbatim.
- **User Stories (Phase 3-5)**: all depend on Foundational. US1 (the generic workflow + template)
  is the MVP and goes first -- the trace template + workflow are what US2's doc edit points at and
  what US3's worked example fills. US2 (the Dashboard Ready evidence-item edit + refusal-path
  verification) and US3 (the human build + filled trace) follow US1; US3's T012 is a HUMAN action
  the agent only verifies.
- **Polish (Phase 6)**: depends on all three stories complete.

### User Story Dependencies

- **US1 (P1)**: independent after Foundational -- the MVP. T008 (workflow) and T009 (template)
  are the generic substrate everything else consumes.
- **US2 (P1)**: needs US1's workflow + template to point at (T010) and to check the refusal paths
  against (T011).
- **US3 (P1)**: needs US1's workflow (the build order it restates) + US1's template (the blank it
  fills); T012 (human build) precedes T013/T014 (the agent's verification + trace).

### Parallel Opportunities

- T001 || T002 (Setup -- independent reads).
- Within Phase 2, T004-T007 each write one boundary fact -- author in one pass as a shared
  "boundary facts" note the artifacts copy from; T003 (O-1) is recorded alongside.
- Phase 6: T016 / T017 / T018 / T019 / T020 are independent greps/diffs -- parallel; T021
  (`retail check` + ASCII sweep) runs last.

## Parallel Example: Phase 6 verification sweep

```
# Independent greps/diffs -- run together:
T016 no-automation/no-publish grep
T017 1:1 trace check (worked example)
T018 discount-framing check (50.37% + caveats)
T019 C086/pharmacy-leakage grep (generic artifacts)
T020 no-new-stage / no-new-gate diff proof
# then T021 retail check + ASCII/no-BOM sweep last
```

## Implementation Strategy

**MVP first**: Setup -> Foundational -> US1 = the generic implementation-review workflow + the
generic trace template (an agent can verify any human-built page against its approved binding map
and emit a reviewable trace). Ship/commit there if needed. Then US2 (the Dashboard Ready
evidence-item edit + refusal-path verification) and US3 (the retail_store_sales human build +
filled trace + corrected discount framing), then the Phase 6 whole-feature gates.

**Boundary discipline (the load)**: every generic artifact carries the same verbatim
inherited-gate text (T004), 1:1-trace rule (T005), and no-automation/no-publish boundary (T006).
Phase 6 (T015-T021) proves the ways this feature could fail its own scope: a build blessed before
its design is approved, an orphan/unmapped visual passed, an automation/publish step crossed, a
new stage/status/gate/rule added, a C086 leak, a stale discount number, or a non-ASCII/BOM file.
The only PBIR change in the entire slice is the human's Desktop save of the worked-example page.

## Readiness for the next gate

When Phase 6 is green (gate fixture holds; no automation/publish/data-edit; 1:1 trace at `pass`;
50.37% framing correct; no new stage/status/gate/rule; `retail check` exit 0 with rule count
unchanged; ASCII + UTF-8 no BOM), this tasks.md is ready for `/speckit-analyze` (cross-artifact
consistency across spec.md / plan.md / tasks.md) or `/speckit-plan-next`, per house convention.
