---
description: "Task list for Power BI Visual Foundation (F011A)"
---

# Tasks: Power BI Visual Foundation (F011A)

**Input**: Design documents from `specs/017-powerbi-visual-foundation/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: This is a docs/templates/skill-only feature (no runtime code) -- there are no unit
tests. Verification tasks (router fixture, gate fixture, YAML/JSON-valid, ASCII/no-BOM,
C086-leakage grep, no-data-edit grep, `retail check` green) stand in for tests and are
included explicitly.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1 route / US2 gate / US3 separation)
  or SETUP / FOUND (foundational) / POLISH
- All paths are repo-relative from the worktree root

## Path Conventions

Docs/templates/skill feature -- no `src/`/`tests/`. New homes: `.claude/skills/powerbi-dashboard-design/`,
`docs/powerbi/`, `templates/`, `design/`, `themes/`, `reports/blueprints/`, plus a pointer
edit in `docs/readiness/dashboard-ready.md`. (Skill under `.claude/skills/`, NOT top-level
`skills/` -- see plan.md Structure Decision.)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the new homes and pin the reference shapes to reuse.

- [ ] T001 [P] Create the new directories: `.claude/skills/powerbi-dashboard-design/workflows/`,
      `docs/powerbi/`, `design/tokens/`, `design/grids/`, `design/backgrounds/`, `themes/`,
      `reports/blueprints/`. (`templates/` already exists.)
- [ ] T002 [P] Re-read the reference shapes to match house style EXACTLY: an existing skill
      (`.claude/skills/dashboard-design/SKILL.md` -- the F011/012 verb this foundation routes
      to, + `.claude/skills/retail-orchestrate/SKILL.md` for the router idiom); the readiness
      vocabulary (`docs/readiness/readiness-model.md` + `templates/readiness-status.yaml` --
      four statuses, no score); the stage doc (`docs/readiness/dashboard-ready.md` -- the gate
      to inherit verbatim); a template header idiom (`templates/source-map.yaml`). Capture the
      header/status/router idioms to reuse.

**Checkpoint**: homes exist; house style for skill front-matter, router tables, status
vocabulary, and template headers is pinned.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Fix the boundary facts that ALL artifacts reuse verbatim. These are the load --
get them wrong and the artifacts drift into a second gate, a blended surface, or an invented
metric.

**CRITICAL**: No US1/US2/US3 artifact may be authored until these facts are fixed in one
place, or they will be re-worded inconsistently across ~30 files.

- [ ] T003 [FOUND] Write the canonical FOUR-SURFACE table (request -> surface -> workflow ->
      the rule that keeps it clean), verbatim source for the router skill and
      `docs/powerbi/visual-design-system.md`: (1) report visuals; (2) external
      background/canvas; (3) theme JSON; (4) implementation handoff. [FR-001, FR-011]
- [ ] T004 [FOUND] Write the INHERITED-GATE statement (single source of truth, reused in the
      router + every data-bound artifact): no data-bound dashboard design before the subject
      area's `semantic_model_ready` is `pass` (rule 5); this feature DEFINES NO new gate and
      is NOT a second source of truth -- the gate + design-review + `dashboard_ready: pass` are
      owned by `docs/readiness/dashboard-ready.md` + F011/012. [FR-004, FR-010]
- [ ] T005 [FOUND] Write the TWO surface-purity rules verbatim: "background is STATIC
      STRUCTURE, never data -- no KPI value or dynamic title baked into a static image"
      (surface 2) and "theme JSON controls DEFAULTS, never business meaning -- no DAX, metric,
      relationship, source-mapping, storytelling, or validation" (surface 3). [FR-005, FR-006]
- [ ] T006 [FOUND] Write the NO-DATA-EDIT / handoff-boundary statement: this slice edits no
      PBIP/PBIR, generates no DAX, changes no SQL, edits no semantic-model file, adds no
      pbi-cli automation; the handoff stops at NOTES and names F016 as the owner of execution
      (rule 6). [FR-007]
- [ ] T007 [FOUND] Fix the readiness vocabulary + Principle-V stop list for this surface:
      exactly four statuses (`not_started`/`blocked`/`warning`/`pass`) + `evidence[]` +
      `blocking_reasons[]`, NO score; STOP triggers = ambiguous surface, business-question
      choice, readability/grain deviation, design-review sign-off. [FR-009, FR-010]

**Checkpoint**: the four-surface table, the inherited-gate text, the two purity rules, the
no-data-edit statement, and the four-status/no-score/stop-list are fixed -- ready to drop into
every artifact identically.

---

## Phase 3: User Story 1 - Route a request to exactly one of four surfaces (Priority: P1) -- MVP

**Goal**: Ship the router skill + the eight workflows + the reference docs so an agent
classifies any request into one surface and opens the right workflow.

**Independent Test**: feed the ~10-request router fixture; the agent names surface + intent +
workflow file for each, exactly one surface each, ambiguous ones asked-not-guessed, zero
blends. [SC-001]

- [ ] T008 [US1] Author `.claude/skills/powerbi-dashboard-design/SKILL.md`: front-matter
      (`name`, `description`); body = the four-surface ROUTER table (T003) as the front door;
      the request->workflow router (new page/page design -> `page-blueprint.md`; screenshot
      critique -> `screenshot-review.md`; background/canvas -> `background-asset-design.md`;
      colors/fonts/defaults -> `theme-json-design.md`; chart/card/slicer arrangement ->
      `visual-design-system.md` + `page-blueprint.md`; final review -> `dashboard-qa.md`;
      mobile -> `mobile-layout.md`; build/implement -> `powerbi-handoff.md`); the HARD RULES
      block (metrics from contracts only; visuals map to semantic-model fields; background =
      structure not data; theme = defaults not meaning; PBIP/pbi-cli later unless scoped; STOP
      before editing PBIP/PBIR); and an explicit "this routes to the F011/012 `dashboard-design`
      verb for the gated contract-binding design" note (O-1 alongside). [FR-001, FR-003, FR-004, FR-011, FR-007]
- [ ] T009 [P] [US1] Author `workflows/visual-design-system.md` (surface 1): the report-visual
      objects (cards, charts, slicers, tables/matrices, tooltips, bookmarks, titles,
      interactions) and chart-selection guidance by question/grain; every data-bound visual
      cites a contract + a mapped field. [FR-002, FR-012]
- [ ] T010 [P] [US1] Author `workflows/page-blueprint.md` (surface 1): page = one business
      question; the section vocabulary (header / KPI strip / main insight / diagnostic /
      exception-detail / filter rail / footer-status); how to fill
      `templates/dashboard-page-blueprint.yaml`. [FR-012]
- [ ] T011 [P] [US1] Author `workflows/background-asset-design.md` (surface 2): design outside
      Power BI (Figma/Canva/PowerPoint/Illustrator), export PNG/SVG/JPG, import as page
      background/image layer, keep visuals editable above it, safe zones, static containers
      only; embed the surface-2 purity rule (T005). [FR-005]
- [ ] T012 [P] [US1] Author `workflows/theme-json-design.md` (surface 3): what to set
      (palette/fonts/visual+page/wallpaper/filter-pane defaults/sentiment colors) and the
      must-NOT list (T005); points at `templates/theme-json-spec.md` + `themes/`. [FR-006]
- [ ] T013 [P] [US1] Author `workflows/mobile-layout.md` (surface 1): phone-layout guidance;
      reference `design/grids/mobile-grid.yaml`; what survives to mobile (KPI strip, top
      insight) vs. desktop-only detail. [FR-012]
- [ ] T014 [P] [US1] Author `docs/powerbi/visual-design-system.md`: distinguish design tokens
      vs theme JSON vs background assets vs page blueprint vs visual specs vs Power BI
      implementation (the four surfaces, T003); the Power BI design principles list (every
      page answers a business question; every KPI has comparison/context; executive pages use
      fewer visuals; slicers don't dominate; tables for detail not executive insight;
      consistent number formats; colors carry meaning; accessible contrast; consistent
      branch/category colors where applicable; a Data Quality & Controls page for serious
      dashboards). [FR-012]
- [ ] T015 [P] [US1] Author `docs/powerbi/background-assets.md`: the external-background
      workflow + background rules (structure not data; no KPI/dynamic title in image; avoid
      dark behind dense charts; preserve whitespace; consistent 16:9; document canvas size +
      safe zones). [FR-005]
- [ ] T016 [P] [US1] Author `docs/powerbi/theme-json.md`: what theme JSON controls + what it
      must NOT control (T005), with the do/don't framing. [FR-006]
- [ ] T017 [P] [US1] Author `docs/powerbi/dashboard-blueprints.md`: how a page blueprint is
      read, the section vocabulary, and an index of the four starter blueprints in
      `reports/blueprints/`. [FR-012]
- [ ] T017a [P] [US1] Author `docs/powerbi/visual-qa.md`: the PROSE home of the visual-QA
      anti-pattern reference (the readable explanations of each anti-pattern + the design
      principle it violates). This is the reference doc; the `workflows/dashboard-qa.md`
      procedure (T018) USES it -- the doc/skill split of plan.md Structure Decision #4. Keep
      the two in sync: prose here, procedure there. [FR-013] (closes the "5 reference docs"
      count in plan.md Scale/Scope)

**Checkpoint**: a request can be routed to exactly one surface + the right workflow, and the
prose reference for each surface (5 docs/powerbi files) exists. MVP done.

---

## Phase 4: User Story 2 - Refuse to design before contracts exist (Priority: P1)

**Goal**: Ship the gate-bearing artifacts -- the QA reference, the screenshot-review and
handoff workflows, and the generic templates that all carry the inherited gate + the
contract/field requirement.

**Independent Test**: run the gate fixture (each non-`pass` `semantic_model_ready` status on a
data-bound request -> 0 designs + blocking reason; a pure-styling request -> allowed). [SC-002, SC-004]

- [ ] T018 [US2] Author `workflows/dashboard-qa.md` (surface 1): the visual anti-pattern
      reference (too many visuals; KPI without comparison; unclear date context; wrong number
      formats; slicers dominating; table as main executive visual; no hierarchy; inconsistent
      branch/category colors; no tooltip explanation; visual using a metric with NO contract;
      visual using an UNMAPPED field; background containing dynamic values; theme colors
      overridden randomly per visual). Each anti-pattern names the rule it violates. [FR-013, FR-002]
- [ ] T019 [US2] Author `workflows/screenshot-review.md` (surface 1): the critique procedure
      whose output is page purpose / visual-hierarchy score / readability / spacing+alignment
      / color+contrast / chart-choice / slicer+filter / KPI-context / background+canvas issues
      / recommended fixes / FORBIDDEN changes. It may FLAG an uncontracted/unmapped metric but
      MUST NOT redefine it (points upstream). [FR-013, FR-009]
- [ ] T020 [US2] Author `workflows/powerbi-handoff.md` (surface 4): consumes metric contracts +
      semantic model contract + page blueprint + theme JSON + background specs + visual specs +
      QA checklist; OUTPUTS implementation notes for Power BI Desktop + optional future
      PBIP/pbi-cli adapter NOTES + known limitations. Embeds the no-data-edit/handoff-boundary
      statement (T006) -- no automation. [FR-007]
- [ ] T021 [P] [US2] Author `templates/visual-spec.yaml`: visual id / type / business question /
      metric contract (REFERENCE by name) / semantic-model fields (mapped) / position /
      formatting rules / interactions / tooltip behavior / sorting / number format /
      anti-pattern checks. Carry the contract+field requirement (T004) + a generic placeholder
      note. [FR-002, FR-008]
- [ ] T022 [P] [US2] Author `templates/screenshot-review.md`: the critique-output template
      (same section shape as the workflow), generic. [FR-013]

**Checkpoint**: the gate + contract/field requirement are present in the QA, review, handoff,
and visual-spec artifacts; a data-bound design refuses without contracts, a styling request
proceeds.

---

## Phase 5: User Story 3 - Keep the four surfaces and their artifacts separated (Priority: P1)

**Goal**: Ship the templates, tokens, theme, and starter blueprints, each belonging to one
surface and encoding its purity rule (reference-don't-embed; forbidden-dynamic-content;
must-NOT-control).

**Independent Test**: read each artifact -- the page blueprint references (not embeds)
contracts/theme/background; the background spec has a "forbidden dynamic content" section; the
theme-JSON spec has a "must NOT control" section; no C086 specifics anywhere. [SC-005, SC-006, SC-007]

- [ ] T023 [P] [US3] Author `templates/dashboard-page-blueprint.yaml`: page name / audience /
      business question / readiness dependencies / required metric contracts (REFERENCE) /
      required semantic model contract (REFERENCE) / background asset (path) / theme JSON
      (path) / canvas size / grid / sections (header, KPI strip, main insight, diagnostic,
      exception-detail, filter rail, footer-status) / visuals / slicers / tooltips / mobile
      notes / QA rules. References never inline metric formulas or DAX. [FR-002, FR-008]
- [ ] T024 [P] [US3] Author `templates/background-spec.yaml`: page / canvas size / asset path /
      export format / safe zones / static regions / FORBIDDEN dynamic content (explicit
      section banning KPI values + dynamic titles) / import instructions / QA checklist. [FR-005, FR-008]
- [ ] T025 [P] [US3] Author `templates/theme-json-spec.md` (human-readable): palette /
      typography / sentiment colors / data colors / visual defaults / filter-pane defaults /
      page background / accessibility checks / JSON-validation reminder / and the explicit
      "must NOT control" list (T005). [FR-006, FR-008]
- [ ] T026 [P] [US3] Author `design/tokens/tower-retail-design-tokens.yaml`: conservative
      executive retail seed -- primary/secondary colors, background, surface, text colors,
      success/warning/danger (sentiment), neutrals, font family, spacing units, KPI-card
      rules, max-visuals-per-executive-page, number-format defaults. No extreme gradients / no
      overdesigned SaaS styling. Generic. [FR-012, FR-008]
- [ ] T027 [P] [US3] Author `design/grids/16x9-grid.yaml` + `design/grids/mobile-grid.yaml`:
      canvas dimensions, columns/rows, gutters, safe zones for desktop 16:9 and phone. [FR-005]
- [ ] T028 [P] [US3] Author `design/backgrounds/README.md`: where exported background assets
      live, naming convention, export formats, and the structure-not-data rule (T005). [FR-005]
- [ ] T029 [P] [US3] Author `themes/tower-retail.theme.json`: minimal CONSERVATIVE starter --
      `name`, `dataColors` (from tokens), `background`, `foreground`, `tableAccent`, and safe
      `visualStyles` defaults only. + `themes/README.md` stating it is a STARTER requiring
      validation in Power BI Desktop and that the exact theme schema is treated as uncertain.
      No business logic, no connection string. [FR-006, FR-014]
- [ ] T030 [P] [US3] Author the four `reports/blueprints/*.yaml` (executive-summary,
      branch-performance, product-mix, data-quality-control-room): each states audience +
      business question + required metric contracts (placeholders) + required semantic-model
      dependencies (placeholders) + layout sections + candidate visuals + QA rules; invents NO
      concrete business metric beyond a named placeholder. [FR-002, FR-008, FR-012]
- [ ] T031 [US3] Edit `docs/readiness/dashboard-ready.md`: add a "design foundation that backs
      this stage" pointer row -> the `powerbi-dashboard-design` skill + `docs/powerbi/` +
      `templates/` + `design/` + `themes/` + `reports/blueprints/`, WITHOUT changing any gate,
      status, blocking reason, or the F011/012 design-review responsibility. [FR-004]
- [ ] T031a [US3] Register F011A in `docs/roadmap/roadmap.md`: add an F011A row (Layer 6,
      advances Dashboard Ready, "the design FOUNDATION the F011 verb reasons with") near the
      F011 row, and add the spec-dir->F-number mapping note (017 = F011A) consistent with the
      existing numbering note. Make the spec header's "F011A (roadmap F-number)" claim true.
      Change no hard rule, no other feature row, no ordering. [roadmap-consistency acceptance criterion]

**Checkpoint**: every template/token/theme/blueprint belongs to one surface and encodes its
purity rule; the stage doc + roadmap point at the foundation without altering any gate or
ordering.

---

## Phase 6: Polish & Cross-Cutting Verification

**Purpose**: Whole-feature gates that span all three stories. These stand in for tests.

- [ ] T032 [POLISH] Router fixture: write/execute ~10 generic requests (>=2 per surface +
      ambiguous), confirm each resolves to exactly one surface + intent + workflow, ambiguous
      asked-not-guessed, zero blends. [SC-001]
- [ ] T033 [POLISH] Gate fixture: for each non-`pass` `semantic_model_ready` status, a
      data-bound request yields 0 designs + the blocking reason; a pure-styling request is
      allowed. [SC-002, SC-004]
- [ ] T034 [P] [POLISH] Validate every YAML (`templates/*.yaml`, `design/**/*.yaml`,
      `reports/blueprints/*.yaml`) parses, and `themes/tower-retail.theme.json` is valid JSON. [SC-008]
- [ ] T035 [P] [POLISH] Grep all new/edited files for C086/pharmacy leakage (billing codes,
      segment rollups, insurance/PII columns, pharmacy grain keys) -- expect zero. [SC-007]
- [ ] T036 [P] [POLISH] Grep proving the no-data-edit boundary: 0 PBIP/PBIR edits, 0 DAX, 0
      SQL changes, 0 semantic-model edits, 0 pbi-cli commands across all deliverables; confirm
      no new `retail check` rule and no `src/` change. [SC-003]
- [ ] T037 [P] [POLISH] Confirm the surface-purity proofs: every background template/spec has a
      "forbidden dynamic content" section; the theme spec has a "must NOT control" section; no
      artifact places a dynamic value in a static background or business logic in a theme. [SC-005, SC-006]
- [ ] T038 [POLISH] Run `retail check` over the repo: exit 0 and rule count UNCHANGED. Confirm
      all new files are ASCII + UTF-8 no BOM, paths `<= 200` chars, no real host/secret. [SC-008, FR-014]
- [ ] T039 [POLISH] Re-run the plan.md Constitution Check (Post-Design Re-Check): confirm still
      PASS (9/9 + spine + roadmap rules) -- no new gate, no divergent source of truth, no data
      edit. Confirm the `dashboard-ready.md` edit altered only the pointer row, and the
      `roadmap.md` edit added only the F011A row + numbering note (no hard-rule/ordering change)
      -- by diff. [SC-009]

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies -- start immediately. T001 and T002 are parallel.
- **Foundational (Phase 2)**: depends on Setup; BLOCKS all user stories. It fixes the
  four-surface table, the inherited-gate text, the two purity rules, the no-data-edit
  statement, and the four-status/no-score/stop-list that every artifact reuses verbatim.
- **User Stories (Phase 3-5)**: all depend on Foundational. US1 (route) is the MVP and goes
  first -- the router skill (T008) is the front door the rest references. US2 (gate) and US3
  (separation) author mostly DIFFERENT files and can proceed in parallel after US1's skill +
  the four-surface table exist; the few cross-references (the QA list lives both in the
  `dashboard-qa.md` workflow and `docs/powerbi/visual-qa.md`; templates are referenced by the
  workflows) are name-level, not blocking.
- **Polish (Phase 6)**: depends on all three stories complete.

### User Story Dependencies

- **US1 (P1)**: independent after Foundational -- the MVP. T008 (the skill) is authored first;
  T009-T017 are parallel workflow/doc files.
- **US2 (P1)**: needs US1's skill (it is the surface that the QA/review/handoff workflows hang
  off) + the four-surface table; the templates (T021/T022) are independent files.
- **US3 (P1)**: needs the four-surface table + the purity rules; its templates/tokens/theme/
  blueprints are independent files. T031 (the stage-doc pointer) and T031a (the roadmap
  registration) should be last in US3 so they point at artifacts that exist.

### Parallel Opportunities

- T001 || T002 (Setup).
- Within Phase 2, T003-T007 each write one boundary fact -- author in one pass (they become a
  shared "boundary facts" note the artifacts copy from), then proceed.
- Phase 3: T008 first; then T009-T017 are all [P] (different files).
- Phase 4 and Phase 5 author different files -- run together after US1's skill exists.
- Phase 6: T034/T035/T036/T037 are independent greps/validators -- parallel.

## Parallel Example: after US1's skill (T008) ships

```
# US2 and US3 touch different files -- run together:
US2: workflows/dashboard-qa.md + screenshot-review.md + powerbi-handoff.md + templates/visual-spec.yaml + templates/screenshot-review.md
US3: templates/dashboard-page-blueprint.yaml + background-spec.yaml + theme-json-spec.md
     + design/** + themes/** + reports/blueprints/*.yaml  (then T031 stage-doc pointer last)
```

## Implementation Strategy

**MVP first**: Setup -> Foundational -> US1 = a usable router + per-surface workflows + the
reference docs (an agent can classify any request and open the right workflow). Ship/commit
there if needed. Then US2 (gate-bearing QA/review/handoff/visual-spec) + US3 (templates/
tokens/theme/blueprints + stage pointer) in parallel, then the Phase 6 whole-feature gates.

**Boundary discipline (the load)**: every artifact carries the same verbatim four-surface
table (T003), inherited-gate text (T004), purity rules (T005), and no-data-edit statement
(T006). Phase 6 (T032-T039) proves the four ways this feature could fail its own scope: a
blended surface, a design before contracts, a data edit, or a C086 leak.
