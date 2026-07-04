---
description: "Task list for the promotion/markdown fact + factless-fact coverage pattern"
---

# Tasks: Promotion/Markdown Fact and Factless-Fact Coverage Pattern

**Input**: Design documents from `specs/097-promotion-markdown-factless/`

**Prerequisites**: `plan.md`, `spec.md` (clarified, 16 FRs, Q1-Q3 RESOLVED),
`research.md`, `data-model.md`, `quickstart.md` (all present, Phase 0/1
complete).

**Tests**: This is a documentation feature (SCOPE GUARD: pattern +
worked-example shape only, no live execution). "Tests" below means
inspection/verification tasks against spec.md's Success Criteria (SC-001
through SC-006) and a read-only `retail check` run -- never unit/integration
test code, never a numeric score.

**Organization**: Tasks are grouped by user story (spec.md US1 P1, US2 P2, US3
P3). Per plan.md's Structure Decision, this feature creates **exactly two**
repo deliverable files, both OUTSIDE `specs/097-promotion-markdown-factless/`:

- `docs/patterns/promotion-markdown-factless.md` (FR-001; new `docs/patterns/`
  subdirectory)
- `templates/factless-fact.yaml` (FR-002; flat under `templates/`)

Both files already exist as *targets* only -- neither is created before this
tasks.md is executed (plan.md: "authored at implement stage"). Most content
tasks below therefore land in ONE of these two files, not in a new file per
task; do not split the pattern doc into artificial extra files merely to earn
a `[P]` marker.

**Hard boundary repeated here for execution safety**: no task creates a
`mappings/<table>/` directory, a migration, a PBIP model, a new `retail check`
rule, a new readiness-status.yaml key, or edits `templates/source-map.yaml` or
`skills/retail-kpi-knowledge/domains/discounts-and-promotions.md` (FR-007,
FR-010; SC-004, SC-006). No task runs `git add -A` (stage exact paths only, if
a human later commits this work). No task commits, pushes, opens a PR, or
merges.

**Docs-first note (hard rule #8)**: this feature adds NO static-rule wiring
task at all (FR-007 forbids it) -- there is nothing for a doc/template task to
precede in a wiring sense. The ordering requirement is satisfied vacuously:
Setup/Foundational (read + skeleton) precedes content authoring, which
precedes verification, and no automation phase exists by design.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to, or `SETUP`/`XCUT` for
  shared/cross-cutting work
- Every task cites the exact FR-### / SC-### it satisfies, so FR-to-task
  coverage is auditable in place (per the analyze stage's coverage check)

---

## Phase 1: Setup

**Purpose**: Confirm inputs and target locations before any content task
begins. No file is written in this phase except (optionally) empty parent
directories.

- [ ] T001 [SETUP] Confirm the spec chain is complete and self-consistent:
      re-read `specs/097-promotion-markdown-factless/spec.md`,
      `plan.md`, `research.md`, `data-model.md`, `quickstart.md` in this
      worktree; confirm zero unresolved `[NEEDS CLARIFICATION]` markers remain
      (Q1-Q3 all RESOLVED). No FR.
- [ ] T002 [SETUP] Confirm `docs/patterns/` does not yet exist as a
      subdirectory and `templates/factless-fact.yaml` does not yet exist,
      matching research.md Sec 2's repo-wide directory check; re-verify with a
      fresh listing immediately before authoring (avoids acting on a stale
      research-stage snapshot). Supports FR-016 (exact target paths).
- [ ] T003 [SETUP] Create the `docs/patterns/` directory (new `docs/<topic>/`
      subdirectory, matching the convention of `docs/worked-examples/`,
      `docs/architecture/`, `docs/decisions/`). Creates no file yet. FR-016.

**Checkpoint**: Target locations confirmed and ready; no existing repo file
touched yet.

---

## Phase 2: Foundational (blocking prerequisites)

**Purpose**: Lock the shared placeholder vocabulary and file skeletons every
user story's content tasks build on, so US1/US2/US3 never invent conflicting
generic names or duplicate a header. No user-story content task may begin
before this phase completes.

**CRITICAL**: Both deliverable files are authored incrementally across
Phases 2-5 (they are single files each); this phase creates the skeleton
(header + section stubs) only, not the load-bearing content.

- [ ] T004 [XCUT] Re-read the four cited source artifacts in full so every
      later citation is accurate, not assumed: `templates/source-map.yaml`
      (the `gold_star` shape + authoring-notes header convention),
      `skills/retail-kpi-knowledge/domains/discounts-and-promotions.md` (the
      named gap; Discount Amount/Discount Rate % Seeded, Promotion Uplift %
      Planned), `docs/worked-examples/retail-store-sales.md` (the one
      measure-bearing fact to be cited, never restated),
      `docs/decisions/0002-retail-cleaning-defaults.md` (RC14, RC9). Supports
      FR-001, FR-002, FR-004, FR-005, FR-010, FR-012.
- [ ] T005 [XCUT] Lock the shared generic-placeholder vocabulary used by BOTH
      deliverable files, per research.md Sec 5: `sales_fact`, `coverage_fact`,
      `promotion_fact`, `dim_product`, `dim_store`, `dim_date`,
      `promotion_id`, `markdown_amount`, `promoted_units`. Record this list as
      a short internal note (not a new repo file) so Phase 3-5 tasks reuse it
      verbatim instead of drifting to synonyms. Supports FR-012, SC-003.
- [ ] T006 [XCUT] Write the skeleton of
      `docs/patterns/promotion-markdown-factless.md`: title, a short
      "what this is / what it is not" framing paragraph (cross-referencing
      the Boundary section of spec.md: does not redefine KPIs, does not edit
      `source-map.yaml`, does not edit the worked example, adds no static
      rule), and empty headed sections for: (1) why a measure-bearing fact
      alone cannot answer "discounted but did not sell", (2) the factless
      coverage fact shape, (3) the anti-join mechanism, (4) the
      promotion/markdown fact shape, (5) conformed dimensions, (6) edge
      cases, (7) references. FR-001.
- [ ] T007 [XCUT] Write the skeleton of `templates/factless-fact.yaml`: a
      commented header block mirroring `templates/source-map.yaml`'s
      convention exactly (WHAT THIS IS / WHICH PLAYBOOK PHASES / WHICH ADR-0002
      DEFAULTS / a "this is a filled EXAMPLE, never the schema"-style
      reminder / SISTER ARTIFACTS pointer to
      `docs/patterns/promotion-markdown-factless.md`), followed by empty
      top-level key stubs matching data-model.md Entity 4's section table:
      `meta:`, `defaults:`, `columns:`, `gold_star:` (`fact:`, `dimensions:`),
      `derived_columns:`. Depends on T004 (must mirror the real file, not a
      guess). FR-002, FR-016.

**Checkpoint**: Both deliverable files exist on disk with header + section
skeletons only; the shared placeholder vocabulary is fixed. User-story content
tasks may begin.

---

## Phase 3: User Story 1 - Answer "what did we discount that did not sell?" with a factless coverage fact (Priority: P1) 🎯 MVP

**Goal**: Make the pattern doc and template teach the factless-coverage-fact
concept and the anti-join mechanism completely enough that a reader with no
prior exposure can restate why a measure-bearing fact alone cannot answer the
question, and correctly describe the anti-join.

**Independent Test** (spec.md US1): given only the pattern doc and the
factless-fact template, an analyst can (a) state why a measure-bearing
promotion fact alone cannot answer "discounted but did not sell", (b)
identify the coverage row (product x store x day x promotion) as the
factless fact's grain, and (c) describe the anti-join against the sales fact
on conformed dimensions -- without inventing promo mechanics.

### Implementation for User Story 1

- [ ] T008 [US1] In `docs/patterns/promotion-markdown-factless.md` section
      (1), write the explanation of WHY a measure-bearing promotion fact
      alone cannot answer "on promo but did not sell" (no row exists for a
      promotion that sold zero units), and state this as the reason a
      factless fact is needed at all. Depends on T006. FR-003; Acceptance
      Scenario US1-1; SC-001.
- [ ] T009 [US1] In `docs/patterns/promotion-markdown-factless.md` section
      (2), write the factless coverage fact shape per data-model.md Entity 2:
      the illustrative `gold_star.fact` block with `measures: []` (empty,
      per Clarification Q2 -- not a documented-degenerate marker column), the
      `dim_product` / `dim_store` / `dim_date` conformed dimension list, and
      the authoring note that `COUNT(*)` over the fact's rows is a valid read
      without being a stored measure column. State explicitly that this is
      the defining structural difference from every other fact template in
      the repo (Principle III: still a valid Kimball star despite no additive
      measure). Depends on T008 (same section flow). FR-004; Acceptance
      Scenario US1-2; SC-002.
- [ ] T010 [US1] In `templates/factless-fact.yaml`, fill `gold_star.fact` with
      `measures: []` and the inline comment distinguishing `COUNT(*)` (a valid
      read) from a fabricated stored `coverage_count` column (discouraged, per
      spec.md Edge Cases); fill `gold_star.dimensions` with the same
      `dim_product` / `dim_store` / `dim_date` placeholder list as T009's doc
      section (must match verbatim, per T005's locked vocabulary). Depends on
      T007, T009. FR-002, FR-004; SC-002.
- [ ] T011 [US1] In `templates/factless-fact.yaml`, fill `meta:` (grain,
      primary_key placeholders per data-model.md Entity 4: grain = the
      coverage combination product x store x day x promotion; primary_key =
      the composite of conformed dimension keys plus the promotion
      identifier), `defaults:` (adopted/deviations, unchanged shape from
      `source-map.yaml`), `columns:` (with the authoring note that a real
      money/quantity column showing up here may mean the real shape needed is
      the measure-bearing promotion fact, not a factless fact), and
      `derived_columns:` (left empty/commented, per data-model.md Entity 4).
      Depends on T007. FR-002.
- [ ] T012 [US1] In `docs/patterns/promotion-markdown-factless.md` section
      (3), write the anti-join mechanism: name the LEFT ANTI JOIN (or
      equivalent set-difference) between the factless coverage fact and the
      sales fact, on their shared conformed dimensions, as the mechanism that
      answers the question; include the one placeholder-only, non-executable
      SQL sketch from data-model.md Entity 3 (`coverage_fact` LEFT JOIN
      `sales_fact` ... WHERE `sales_fact.<key> IS NULL`), explicitly labeled
      as an illustration, never a proposed or runnable migration. Depends on
      T009. FR-003, FR-011 (illustration only, not execution); Clarification
      Q3; Acceptance Scenario US1-1; SC-001.
- [ ] T013 [US1] In `docs/patterns/promotion-markdown-factless.md` section
      (6), write the first two Edge Cases from spec.md verbatim in substance:
      (a) the dimension-mismatch precondition for the anti-join (when the two
      facts do not share a conformed grain-compatible key, name this as a
      blocking mapping-gate question for the adopting table, never an invented
      crosswalk), and (b) the partial-day / overlapping-promotion grain
      ambiguity (an adopting-table mapping decision the template's grain field
      flags, not answers). Depends on T009, T012. FR-013 (edge cases 1-2 of
      4).
- [ ] T014 [US1] In `docs/patterns/promotion-markdown-factless.md` section
      (7), add the one citation to `docs/worked-examples/retail-store-sales.md`
      as "an existing measure-bearing fact to anti-join against" -- a "see"
      pointer only, never restated with invented promotion data. Depends on
      T012. FR-012; Acceptance Scenario US3-3; SC-003.

**Checkpoint**: A reader of the pattern doc + template alone (US1's
Independent Test) can restate why a factless fact is required and describe
the anti-join, satisfying SC-001 and SC-002. User Story 1 is independently
reviewable now.

---

## Phase 4: User Story 2 - Model the promotion/markdown fact itself (Priority: P2)

**Goal**: Document the measure-bearing promotion/markdown fact shape as a
distinct entity from the factless coverage fact, sharing the same conformed
dimensions, with spec 087 cited (not implemented) as the future conformance
check.

**Independent Test** (spec.md US2): given the pattern doc's promotion/markdown
fact section alone, an analyst can state its candidate grain in placeholder
terms, name at least one additive measure, and identify which conformed
dimensions it reuses -- all marked as an adopting-table decision.

### Implementation for User Story 2

- [ ] T015 [US2] In `docs/patterns/promotion-markdown-factless.md` section
      (4), write the promotion/markdown fact shape per data-model.md
      Entity 1: the illustrative `gold_star.fact` block with a placeholder
      grain (e.g. "one row per promotion line per store per day", explicitly
      marked as an adopting-table decision, not a value this feature
      supplies) and at least one additive measure placeholder
      (`markdown_amount`, `promoted_units`), distinct from the factless
      coverage fact so the two are never conflated. Depends on T009 (must
      reference the already-written factless shape for contrast). FR-005;
      Acceptance Scenario US2-1; SC-002 (contrast case).
- [ ] T016 [US2] In `docs/patterns/promotion-markdown-factless.md` section
      (5), write the conformed-dimensions statement: both the
      promotion/markdown fact (section 4) and the factless coverage fact
      (section 2) are expected to reuse the SAME `dim_product` / `dim_store`
      (`dim_location`) / `dim_date` dimensions an existing sales star already
      carries, never mint their own copy; cite spec 087 (cross-star
      conformed-dimension readiness, reserved rule id HR1, Draft/not yet
      ratified) as the pending mechanism that would eventually verify this,
      without this feature adding, wiring, or duplicating that mechanism.
      Depends on T015. FR-006; Acceptance Scenario US2-2.
- [ ] T017 [US2] Verify (do not restate) that section (4)'s text does not
      alter the Discount Amount / Discount Rate % KPI contracts and does not
      assert a value or status for Promotion Uplift % -- cross-check against
      `skills/retail-kpi-knowledge/domains/discounts-and-promotions.md` as
      read in T004. Depends on T015. FR-010; Acceptance Scenario US2-3;
      SC-006.
- [ ] T018 [US2] In `docs/patterns/promotion-markdown-factless.md` section
      (6), add the third Edge Case: the "did not sell" (zero recorded sale
      rows) vs. "sold below baseline" distinction, stating this is the same
      baseline-rule gap the Promotion Uplift % KPI is already Planned
      pending, and that this feature's factless fact enables a zero-units
      anti-join today without resolving the baseline rule. Depends on T013,
      T016. FR-013 (edge case 3 of 4).

**Checkpoint**: Both fact shapes (measure-bearing and factless) are now
documented, clearly distinguished, and both cite the same conformed
dimensions and the pending 087 mechanism. Satisfies US2's Independent Test
without touching the KPI domain doc.

---

## Phase 5: User Story 3 - The pattern is generic and reusable across tables (Priority: P3)

**Goal**: Verify (and where needed, tighten) that neither deliverable file
inlines any real worked-example or table-specific name, so the pattern is
provably reusable rather than a one-off write-up.

**Independent Test** (spec.md US3): grep the pattern doc and template for any
worked-example (C086/pharmacy, `retail_store_sales`) or real table's specific
name; confirm none appear except as an explicitly cited external reference.

### Implementation for User Story 3

- [ ] T019 [US3] In `docs/patterns/promotion-markdown-factless.md`
      section (6), add the fourth Edge Case: adding a fabricated
      "coverage_count" measure to the factless fact is explicitly
      discouraged (a `COUNT(*)` over the coverage fact's rows is a valid
      read, but a stored additive measure column would misrepresent the
      fact's nature); and add the fifth edge-case note that the two patterns
      (promotion fact, factless fact) are independently adoptable -- a table
      needing only one may adopt only that section. Depends on T009, T015.
      FR-013 (edge case 4 of 4, plus the independent-adoptability note from
      spec.md Edge Cases).
- [ ] T020 [P] [US3] Grep `docs/patterns/promotion-markdown-factless.md` and
      `templates/factless-fact.yaml` for `retail_store_sales`, `fct_sales_rss`,
      `C086`, `pharmacy`, `el ezaby`/`El Ezaby`, or any other worked-example
      or real-table-specific noun; confirm every hit is a citation ("see ...")
      never inlined content, and confirm only the T005-locked generic
      placeholder vocabulary appears elsewhere. Depends on T014, T015, T016,
      T018, T019 (all content must exist first). FR-012; Acceptance Scenario
      US3-1 and US3-3; SC-003.
- [ ] T021 [P] [US3] Compare `templates/factless-fact.yaml`'s top-level
      section set and placeholder style (angle-bracket `<placeholder>` names)
      against `templates/source-map.yaml`'s own convention; confirm the same
      section set and authoring-notes header pattern is used WITHOUT copying
      `source-map.yaml`'s own specific example values (e.g. no C086/pharmacy
      column names). Depends on T007, T010, T011. FR-002; Acceptance Scenario
      US3-2.

**Checkpoint**: Both deliverable files are confirmed generic by inspection
(SC-003); the template is confirmed to follow the existing convention without
copying its specific values. All three user stories are now independently
satisfied.

---

## Phase 6: Polish & Cross-Cutting Guards

**Purpose**: Close out the MUST-NOT requirements that are not owned by any
single user story (they are guard conditions on the whole feature), plus the
final coverage sweep and validation run.

- [ ] T022 [P] [XCUT] Confirm no `retail check` static rule id was added,
      modified, or reserved: `git status --short` shows no change under
      `src/retail/rules/`, no change to `EXPECTED_RULE_IDS`, the glossary
      rules table, `docs/rules/rules-manifest.json`, or the severity-posture
      record; confirm no `mappings/<table>/readiness-status.yaml` gained a new
      key and no new readiness stage was added anywhere. FR-007; SC-004.
- [ ] T023 [P] [XCUT] Confirm neither deliverable file connects to a database,
      proposes/executes migration SQL (beyond T012's labeled illustration), or
      references the Power BI execution adapter (F016). FR-011.
- [ ] T024 [P] [XCUT] Confirm neither deliverable file invents promotion
      mechanics beyond generic placeholders (no discount-type taxonomy, promo
      funding source, or promo hierarchy/campaign structure introduced as if
      fixed), and confirm no real table's grain, primary key, or column set
      was picked; every such call is stated as an adopting-table decision.
      FR-008, FR-009.
- [ ] T025 [P] [XCUT] Confirm zero numeric confidence/health/maturity score or
      completeness count appears anywhere in either deliverable file (hard
      rule #9). FR-014; SC-005.
- [ ] T026 [P] [XCUT] Confirm both deliverable files are ASCII, UTF-8 without
      BOM (`--` and `->` only, no em-dashes/curly quotes/Unicode glyphs), and
      that both paths stay short and well within the Windows 260-char budget.
      FR-015.
- [ ] T027 [XCUT] Validate `templates/factless-fact.yaml` parses as valid YAML
      (per `templates/source-map.yaml`'s own "keep this YAML valid" authoring
      note). Depends on T010, T011. Supports FR-002.
- [ ] T028 [XCUT] Run a read-only `retail check` from the repo root over the
      full tree including the two new files; record the exact exit code
      verbatim. Expect exit 0 with no new rule firing (none was added by this
      feature) -- this run only confirms the new files trip no EXISTING rule
      (e.g. a secret-pattern scan, an encoding check). If the command is
      unavailable in this worktree, record the exact skip reason -- do not
      claim a result that was not observed. Depends on T006-T021 (all content
      must exist first). Supports FR-007 (evidence), plan.md's "compliance is
      demonstrable by running `retail check`."
- [ ] T029 [XCUT] FR-to-task coverage sweep: re-read spec.md's Functional
      Requirements FR-001 through FR-016 one by one and confirm each is cited
      by at least one task above (T001-T028); if any FR is uncited, add the
      missing task before considering this tasks.md complete. This task IS
      the coverage check the analyze stage will independently re-run, not a
      duplicate of it.
- [ ] T030 [XCUT] Run `git -C "<worktree>" status --short` and confirm the
      only new/modified paths are `docs/patterns/promotion-markdown-factless.md`,
      `templates/factless-fact.yaml`, and (if a directory was newly created)
      `docs/patterns/` itself -- no other file under `src/`, `mappings/`,
      `warehouse/`, `powerbi/`, or any existing template changed. No FR (repo
      hygiene / scope guard confirmation).

**Checkpoint**: All FR-001 through FR-016 are covered by name; both
deliverable files exist, are generic, ASCII/UTF-8-no-BOM, contain no
fabricated score, add no rule, and pass a read-only `retail check`.

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2)**: depends on Setup; BLOCKS all user stories --
  the shared placeholder vocabulary (T005) and both file skeletons (T006,
  T007) must exist before any section is filled in Phases 3-5.
- **User Story 1 (Phase 3, P1)**: depends on Foundational only. Delivers the
  MVP slice (the factless-fact concept + anti-join), matching spec.md's own
  P1 priority rationale (the previously-impossible capability).
- **User Story 2 (Phase 4, P2)**: depends on Foundational; T015 depends on
  T009 (US1) because it contrasts against the already-written factless shape,
  and T018 depends on T013 (US1) because it extends the same Edge Cases
  section. US2 is independently REVIEWABLE per its own Independent Test, but
  its authoring is sequenced after US1 within the shared file.
- **User Story 3 (Phase 5, P3)**: depends on Foundational; T019 depends on
  US1 (T009) and US2 (T015) content existing; T020-T021 are verification
  tasks that depend on ALL prior content tasks (T014-T018) being complete,
  since they grep/compare the finished files.
- **Polish (Phase 6)**: depends on Phases 3-5 all being complete (the guard
  checks and `retail check` run need every section written first).

### Within-file sequencing (both deliverables are single files)

- `docs/patterns/promotion-markdown-factless.md`: T006 -> T008 -> T009 ->
  T012 -> T013 -> T014 (Phase 3) -> T015 -> T016 -> T018 (Phase 4) -> T019
  (Phase 5). These are SEQUENTIAL (same file, same document flow) -- none are
  `[P]` against each other.
- `templates/factless-fact.yaml`: T007 -> T010 -> T011 (Phase 3) -> T021 read
  (Phase 5, read-only). Sequential within the file for the same reason.
- The two files ARE `[P]`-eligible against EACH OTHER where no content
  dependency exists (e.g. T007 could run alongside T008), but this tasks.md
  does not mark either as `[P]` because in practice the shared placeholder
  vocabulary (T005) and cross-references between the two files (the template
  cites the pattern doc; T010's dimension list must match T009's verbatim)
  make writing them in lock-step safer than genuinely parallel authoring.

### Parallel opportunities

- T020, T021 [P] -- T020 and T021 read different files (the pattern doc and
  the template, respectively) and only compare against already-written
  content, so they can run in the same pass once T019 and the earlier content
  tasks (T009, T013-T018) are complete. T019 itself is NOT `[P]`: it is a
  content-authoring edit to the single shared pattern-doc file (same
  same-file-is-sequential rule as every other doc-authoring task in this
  file), and T020 explicitly depends on it completing first.
- T022, T023, T024, T025, T026 [P] -- five independent guard checks, each
  reading (not writing) the two deliverable files plus `git status`; no
  shared state, no ordering constraint among them.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational).
2. Complete Phase 3 (User Story 1) -- the factless-coverage-fact concept and
   the anti-join mechanism, the reason the gap was opened.
3. **STOP and VALIDATE**: confirm US1's Independent Test against the doc +
   template alone (SC-001, SC-002).
4. This alone already closes the structurally-impossible half of the gap;
   US2 and US3 extend and verify it but are not required to answer the P1
   business question.

### Incremental delivery

1. Setup + Foundational -> skeleton ready.
2. Add US1 -> validate independently (factless fact + anti-join documented).
3. Add US2 -> validate independently (measure-bearing fact documented,
   distinguished from US1, KPI doc untouched).
4. Add US3 -> validate independently (genericity confirmed by grep).
5. Polish -> FR coverage sweep + `retail check` run -> done.

## Notes

- Only two repo files are ever created by this feature:
  `docs/patterns/promotion-markdown-factless.md` and
  `templates/factless-fact.yaml` (plus the `docs/patterns/` directory itself).
  This `tasks.md` (and any bookkeeping under
  `specs/097-promotion-markdown-factless/`) is spec-chain hygiene, not a
  runtime deliverable.
- No task in this file stages or commits anything; staging/committing is out
  of scope for this task list. `git add -A` is FORBIDDEN for any future
  commit of this work -- stage the exact two deliverable paths only.
- No task creates a `mappings/<table>/` directory, a migration file, a PBIP
  model change, a new `retail check` rule, or a new readiness-status.yaml key
  -- these are explicitly out of scope (FR-007, FR-009, FR-011, spec.md
  Assumptions).
- `[P]` marks are limited to genuinely independent read/verify tasks (Phase 5
  and Phase 6); content-authoring tasks inside either single-file deliverable
  are sequential by construction and are not marked `[P]` even where the
  underlying content is logically independent, because both files are one
  document each.
