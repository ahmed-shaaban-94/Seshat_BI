---
description: "Task list for Cross-Table Column-Level Lineage / Impact Analysis"
---

# Tasks: Cross-Table Column-Level Lineage / Impact Analysis

**Input**: Design documents from `specs/099-cross-table-lineage-impact/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md,
data-model.md, quickstart.md. No `contracts/` directory exists by design (no API/service
contract; output shape lives in data-model.md, matching the F035 precedent).

**Deliverable shape**: docs/skill/template Product Module -- NO runtime executor code, NO
`src/retail/rules/` entry, NO new `retail check` rule-id (FR-013). Verification is `retail
check` staying green with an UNCHANGED rule count, plus the doc-level "composes-only" `git
status` proof and content/provenance scans (F028/F035 precedent). No pytest module is added.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency)
- **[Story]**: US1 / US2 / US3 (from spec.md), or SETUP / FOUND / POLISH
- Every task cites the FR-id(s) it satisfies in parentheses. All of FR-001..FR-016 must be
  covered by at least one task (checked by the analyze stage).

## Scope guard (read first)

- The unit of work is: ONE skill file `.claude/skills/cross-table-lineage/SKILL.md`, ONE
  generic template `templates/lineage-trace.md`. Nothing else is created.
- DO NOT add a `docs/roadmap/roadmap.md` edit in this build. research.md section 1.5 and
  plan.md's Project Structure explicitly DEFER the F039 roadmap-ledger row to
  INTEGRATION-TIME (whoever merges this feature), specifically to avoid colliding with 18
  other in-flight features on that shared file. No FR requires a roadmap edit here.
- DO NOT add a `src/retail/rules/` entry, a Python module, a `tests/` file, or any executor
  code (FR-013). The agent, following SKILL.md's numbered steps, is the runtime.
- DO NOT resolve FR-010 (the name-similarity resolution-method ruling). It is a genuine OPEN
  Principle-V owner ruling; ship only its fail-safe default (candidate-only, never proven,
  never silently auto-accepted). See "Principle-V carve-out" at the end of this file.
- DO NOT connect to a database, execute SQL, run DAX, or invoke F016 / F031-F033 (FR-002).
- DO NOT inline C086/`retail_store_sales`/pharmacy specifics into the template body or a
  fixed section label (FR-011); cite them only as illustrative filled instances in SKILL.md
  prose (matching data-model.md's own single-paragraph precedent).
- DO NOT compute or emit any blast-radius score, completeness count, or confidence/health/
  maturity value anywhere (hard rule #9, FR-006).

---

## Phase 1: Setup

- [ ] T001 [SETUP] Confirm the five read-source artifact families this module depends on
  exist and are readable, using research.md section 2's confirmed instances as the check
  list: `mappings/retail_store_sales/source-map.yaml`; `warehouse/migrations/0003_create_
  silver_retail_store_sales.sql` + `0004_create_gold_retail_store_sales_star.sql`;
  `mappings/retail_store_sales/metrics/*.yaml` (5 files); `powerbi/RetailStoreSales.
  SemanticModel/definition/tables/gold fct_sales_rss.tmdl`; `templates/visual-contract-
  binding-map.md` (generic template only -- record that no filled per-table copy exists yet
  for `retail_store_sales`, which is the expected hop-5 GAP case). Record any unexpectedly
  absent source as a plan risk before Phase 2 begins. (research.md section 2)

---

## Phase 2: Foundational (blocking prerequisites)

**Purpose**: the generic template and the embedded module-contract block that every user
story's SKILL.md sections build on top of.

**CRITICAL**: No user-story phase (US1/US2/US3) may begin until this phase is complete --
the template's hop/evidence-state vocabulary and the module contract's forbidden-operations
list are referenced, not re-derived, by every later phase.

- [ ] T002 [FOUND] Author the generic copy-me template `templates/lineage-trace.md` covering
  BOTH starting-point shapes (column-rooted and metric-rooted) per data-model.md: a header
  naming the starting point (`kind` + `identifier`, Entity 1) and its `resolved` /
  `resolution_blocker` fields; a fixed 5-slot hop section in order (source-map entry,
  migration SQL reference, metric contract, TMDL measure, dashboard visual binding, Entity
  2) with placeholders for `hop_name`, `evidence_state` (`proven`/`unresolved`/`gap`),
  `citation` (`path`/`anchor`/`quoted_reference`, Entity 3), and `note`; a `downstream_set`
  section restating which hops are proven/unresolved downstream with NO obligation verb; a
  `generated_note` stating the artifact reflects current committed state and carries no
  memory of prior runs; an OPTIONAL `net_sales_consistency_note` slot (populated only when
  the starting point resolves to a Net-Sales-equivalent contract); and a fixed
  `boundary_footer` reiterating no score/no obligation verb/no stage change/no approval/
  read-only-apart-from-this-file. Placeholders only -- generic `<schema.table.column>` /
  `<Metric>` tokens, no C086/retail_store_sales specifics. ASCII, UTF-8 no BOM, short
  filename/paths. NO score field, NO count field anywhere in the shape. (FR-006, FR-011,
  FR-012, FR-014, FR-016; data-model.md Entities 1-4)
- [ ] T003 [FOUND] In `templates/lineage-trace.md`, add the explicit "Forbidden fields" note
  transcribed from data-model.md (no `blast_radius_score`, no `confidence`, no `health`, no
  `maturity`, no `artifacts_affected_count`, no `priority`, no `risk_level`, no
  `recommended_action`) so a future filled copy cannot silently reintroduce one. (FR-006,
  hard rule #9)
- [ ] T004 [FOUND] Embed the F024 Module Contract block (per `templates/module-contract.md`,
  the F035 `SKILL.md`-embedded shape) at the top of `.claude/skills/cross-table-lineage/
  SKILL.md`: Authority category `Product Module`; Capability level `artifact-writing` (per
  research.md section 1.4 -- this module writes one derived artifact per run and reads only
  Core Authority, matching F027/F028/F035, not `read-only`); Product layer `6`; Core
  Authority READ list (the five artifact families, cited by path pattern); the ONE derived
  artifact WRITTEN (`mappings/<table>/lineage-column-<column>.md` or `lineage-metric-
  <Metric>.md`); EXECUTES: none; forbidden operations (no DB/PBIP/F016/F031-F033 connection
  or execution; no readiness-stage move; no approval grant; no business-meaning definition;
  no write-back to any artifact this module reads; no score/count/health/maturity value; no
  obligation verb applied to a downstream item). (FR-002, FR-006, FR-007, FR-009, FR-013)

**Checkpoint**: Foundational template + module contract exist -- user-story phases may now
begin.

---

## Phase 3: User Story 1 - A reader traces one column's downstream reach (Priority: P1) MVP

**Goal**: given a `schema.table.column` starting point, produce one ordered artifact listing
every hop (proven/unresolved/gap) forward from that column, each citing its committed path.

**Independent Test**: for a column referenced in a committed source-map, a migration file, a
metric contract, and a TMDL measure, generating the lineage artifact produces an ordered
chain whose every hop cites a committed repo-relative path, with no hop asserting a link no
cited artifact contains.

- [ ] T005 [US1] Author `.claude/skills/cross-table-lineage/SKILL.md` purpose section and the
  input contract: accepts a `schema.table.column` OR a `mappings/<table>/metrics/<Metric>.
  yaml` starting point (FR-001) and reads only already-committed artifacts -- no DB
  connection, no SQL execution, no DAX run, no live Power BI/PBIP surface, no F016/F031-F033
  invocation (FR-002). (FR-001, FR-002)
- [ ] T006 [US1] In SKILL.md, specify the fixed forward hop order and per-hop resolution
  steps for a column-rooted run: (1) resolve the column against the table's committed
  `source-map.yaml`; (2) find the `warehouse/migrations/*.sql` reference to the resulting
  silver/gold column; (3) find the metric contract(s) under `mappings/<table>/metrics/*.yaml`
  that consume that gold column; (4) find the TMDL measure(s) under `powerbi/*.SemanticModel/
  definition/tables/*.tmdl` that reference that contract; (5) find the dashboard visual
  binding, if any, from a filled `visual-contract-binding-map.md` copy. Each hop that has a
  committed artifact is surfaced; each hop that does not is recorded as a GAP, never a stop.
  (FR-003)
- [ ] T007 [US1] In SKILL.md, specify the citation discipline: every hop reported as part of
  the chain MUST cite the exact committed repo-relative path (and, where the format supports
  it, a YAML key / SQL identifier / TMDL object name as an anchor) it was read from; the
  skill MUST NOT assert a hop for which no committed artifact is cited. (FR-004)
- [ ] T008 [US1] In SKILL.md, specify the three-state evidence vocabulary per data-model.md
  Entity 2's exact, non-overlapping definitions -- `proven` (explicit machine-readable
  reference connecting the hop to its neighbor), `unresolved`/candidate (artifacts exist on
  both sides, no explicit link, and FR-010 has not authorized any promotion method -- `note`
  MUST say why it was not promoted), `gap` (no committed artifact exists yet at that hop --
  `note` names the missing family) -- and that the module MUST NOT create, infer-and-assert,
  or silently invent a lineage edge no committed artifact already records. (FR-005, FR-016)
- [ ] T009 [US1] In SKILL.md, specify the missing/unreadable-artifact handling distinct from
  an UNRESOLVED candidate link: when a required upstream or downstream artifact is missing,
  unreadable, or a blank template, record it as an explicit GAP naming the missing/unreadable
  path -- never fabricate content to fill it. (FR-008)
- [ ] T010 [US1] In SKILL.md, specify the unresolved-starting-point branch: when the
  requested `schema.table.column` does not appear in any committed `source-map.yaml`, record
  a top-level blocker naming the missing source-map row (Entity 1's `resolution_blocker`) and
  produce NO downstream chain from it. (FR-015)
- [ ] T011 [US1] In SKILL.md, specify the output-path rule and write step for the
  column-rooted case: write exactly one file, `mappings/<table>/lineage-column-<column>.md`,
  populated from `templates/lineage-trace.md`; the `column` root-type token is load-bearing
  collision-avoidance (a column and a same-named metric contract must never collide on one
  path). (FR-014)
- [ ] T012 [P] [US1] Add to `quickstart.md`'s existing Scenario A a confirmation checklist
  cross-reference (no new file -- quickstart.md already exists from Phase 1 planning; this
  task verifies SKILL.md's T005-T011 steps produce exactly the walkthrough quickstart.md
  Scenario A already describes, and flags any drift between the two for correction in T005-
  T011 rather than editing quickstart.md's already-approved content). (SC-001, SC-002)

**Checkpoint**: User Story 1 is fully specified and independently exercisable via
quickstart.md Scenario A.

---

## Phase 4: User Story 2 - A reader traces one KPI's full chain, mirroring the Net-Sales
precedent (Priority: P1)

**Goal**: given a metric-contract starting point, produce an artifact structured like the
Net-Sales trace (evidence-tiered, hop-by-hop cited) but generated from current committed
state.

**Independent Test**: generate the lineage artifact for a metric contract other than Net
Sales that has at least a committed contract and a TMDL measure; the artifact cites both hops
from committed paths and requires no hand-authored prose file to exist.

- [ ] T013 [US2] In SKILL.md, specify the metric-rooted entry point: a run starting from
  `mappings/<table>/metrics/<Metric>.yaml` begins at hop 3 (metric contract), not hop 1, per
  data-model.md Entity 2's "a given run may start partway through the chain" rule; it does
  NOT run a full reverse-lineage query (out of scope, spec Assumptions) but does trace
  backward only far enough to cite the contract's own required-field origin against the
  source-map/migration-SQL side as proven/unresolved/gap. (FR-001, FR-003)
- [ ] T014 [US2] In SKILL.md, specify that when the metric contract's upstream committed
  migration-SQL reference cannot be resolved from the source-map, the upstream hop is
  recorded as a GAP naming what is missing (the specific source-map row or SQL reference),
  never silently omitted. (FR-008)
- [ ] T015 [US2] In SKILL.md, specify the forward continuation from hop 3: find the TMDL
  measure(s) referencing the contract (hop 4) and the dashboard visual binding, if any (hop
  5), using the same evidence-state vocabulary and citation discipline as T007/T008. (FR-003,
  FR-004, FR-005, FR-016)
- [ ] T016 [US2] In SKILL.md, specify the `net_sales_consistency_note` behavior (data-model.md
  Entity 4): populate this optional field ONLY when the starting contract resolves to a
  Net-Sales-equivalent contract, stating the generated hops do not CONTRADICT `docs/demo/
  net-sales-end-to-end-readiness-trace.md`'s cited evidence -- never restating or replacing
  that trace, and never claiming a different gold table or TMDL measure than the trace
  already cites. (SC-006)
- [ ] T017 [US2] In SKILL.md, specify the output-path rule for the metric-rooted case: write
  exactly one file, `mappings/<table>/lineage-metric-<Metric>.md`; the `metric` root-type
  token is the same load-bearing collision-avoidance mechanism as T011. (FR-014)

**Checkpoint**: User Stories 1 AND 2 both independently specified and exercisable (quickstart
Scenarios A and B).

---

## Phase 5: User Story 3 - The same module scopes "what to re-review" without deciding it
(Priority: P2)

**Goal**: the downstream set is a candidate list only -- no obligation, priority, or risk
language attached to any item.

**Independent Test**: generate a lineage artifact for a column with three downstream hops;
the artifact's downstream set names exactly those three items with citations, and no
accompanying recommendation, priority, or risk label is present anywhere in the output.

- [ ] T018 [US3] In SKILL.md, specify the `downstream_set` composition rule (data-model.md
  Entity 4): a plain restatement of which `hops` entries are `proven`/`unresolved` downstream
  of the starting point, using only "is downstream of" / "cites" language -- MUST NOT contain
  a verb of obligation ("must", "should", "needs to", "requires re-review") applied to any
  downstream item. (FR-007)
- [ ] T019 [US3] In SKILL.md, add an explicit closing note (mirrored in the template's
  `boundary_footer`, T003) stating that deciding what to re-review is a human/reviewer action
  -- or a separate F014 drift-detector run -- taken OUTSIDE the artifact; the module supplies
  the candidate set only and never states an item "must be re-reviewed," "is broken," or "is
  at risk." (FR-007, FR-009)

**Checkpoint**: All three user stories independently specified and exercisable.

---

## Phase 6: Polish + verification

- [ ] T020 [POLISH] Composes-only proof: exercise quickstart.md Scenario A once against the
  `retail_store_sales` illustrative instance (or confirm by inspection of SKILL.md's steps
  against research.md section 2's confirmed inputs) and confirm `git status` would show
  exactly one new file (`mappings/retail_store_sales/lineage-column-<column>.md`) with no
  existing artifact (source-map, migration SQL, metric contract, TMDL, readiness-status.yaml)
  modified. (SC-005, FR-009)
- [ ] T021 [POLISH] Run `retail check` and confirm it exits green with the rule count
  UNCHANGED (this feature adds no rule, no rule-id, no `src/retail/rules/` entry); confirm no
  `src/` or `tests/` change was introduced anywhere in the diff. (FR-013)
- [ ] T022 [P] [POLISH] No-score / no-obligation-verb scan: grep `templates/lineage-trace.md`
  and `.claude/skills/cross-table-lineage/SKILL.md` for score/count/health/maturity tokens
  (`blast_radius`, `confidence`, `health`, `maturity`, `artifacts_affected`, `priority`,
  `risk_level`, `recommended_action`) and obligation verbs applied to a downstream item
  ("must", "should", "needs to", "requires re-review") -- confirm ZERO matches in the
  downstream-item context. (FR-006, FR-007, SC-003, SC-004, hard rule #9)
- [ ] T023 [P] [POLISH] Generic-token scan (Principle VII): grep the new template and SKILL.md
  for worked-example domain specifics (C086/pharmacy tokens: patient, insurance, payer,
  prescription, dispense, NDC, billing-code; and retail_store_sales-specific column/table
  names) outside a clearly-marked cited-instance example paragraph -- confirm ZERO hits in
  the template body and in SKILL.md's fixed section labels. (FR-011, SC-007)
- [ ] T024 [P] [POLISH] Encoding + path-budget sweep: confirm both new files are ASCII,
  UTF-8 without BOM, using `--`/`->` in place of glyphs, and that every path referenced stays
  within the Windows 260-char budget. (FR-012)
- [ ] T025 [POLISH] Citation-provenance spot-check: for the `retail_store_sales` illustrative
  instance, confirm each of the five hop citations SKILL.md's worked example (or data-
  model.md's own illustrative section) names a path that exists in research.md section 2's
  confirmed list, and confirm hop 5 (dashboard visual) is correctly described as a GAP for
  this table (no filled binding map confirmed present at research time). (FR-004, FR-005,
  SC-002)
- [ ] T026 [POLISH] FR-coverage self-check: grep this tasks.md for `FR-001` through `FR-016`
  and confirm every id appears at least once across T001-T025; record the result in the PR/
  review notes for the analyze stage. (traceability gate)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies -- can start immediately.
- **Foundational (Phase 2)**: depends on Setup; BLOCKS all user-story phases (the template
  and module-contract block are referenced, not re-derived, by every later phase).
- **User Story 1 (Phase 3, P1)**: depends on Foundational only.
- **User Story 2 (Phase 4, P1)**: depends on Foundational; reuses US1's hop-vocabulary/
  citation-discipline steps (T007/T008) by reference rather than duplicating them, so in
  practice authoring US1's SKILL.md sections first is the natural order, but the two phases
  edit disjoint SKILL.md sections and could be drafted in either order.
- **User Story 3 (Phase 5, P2)**: depends on Foundational; consumes the `hops` list T006/T013
  populate, so is naturally authored after US1/US2's hop-walk sections exist in SKILL.md.
- **Polish (Phase 6)**: depends on Phases 2-5 all being complete.

### User Story Dependencies

- US1 (P1): no dependency on US2/US3; independently testable via quickstart Scenario A.
- US2 (P1): no dependency on US1's *output*, but shares SKILL.md structure/vocabulary from
  Foundational; independently testable via quickstart Scenario B.
- US3 (P2): builds on the `hops`/`downstream_set` shape both US1 and US2 populate; not
  independently meaningful without at least one of US1/US2 existing, but does not require
  both.

### Within Each Phase

- T005-T011 (US1) are sequential: they edit the same file (`SKILL.md`) in an order that
  builds the input contract before the hop walk before the citation rule before the
  evidence-state vocabulary before the missing-artifact/blocker branches before the write
  step -- each later step assumes the vocabulary the earlier step defined. T012 is `[P]`
  because it only cross-checks the already-existing `quickstart.md`, a different file.
- T013-T017 (US2) are likewise sequential edits to the same `SKILL.md` file.
- T018-T019 (US3) are sequential edits to the same file.
- T020-T021 (Polish) run before the `[P]` scans (T022-T024) so a green `retail check` and a
  clean composes-only diff are confirmed before the content scans are trusted as final;
  T022-T024 are `[P]` (independent read-only scans over the same two files, no mutation);
  T025 depends on T022-T024 having found no violations to re-litigate; T026 runs last.

### Parallel Opportunities

- T012 may run in parallel with any of T005-T011 (different file).
- T022, T023, T024 may run in parallel with each other (independent scans, no file mutation).
- Nothing in Phase 2 (Foundational) is `[P]` against the other -- T002-T003 edit the same new
  template file sequentially; T004 is a different file (`SKILL.md`) and could in principle run
  alongside T002-T003, but is listed sequentially since the SKILL.md steps in later phases
  reference field names T002 defines.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational).
2. Complete Phase 3 (User Story 1) -- the column-rooted trace is the feature's whole reason
   to exist per spec.md's own "Why this priority" note.
3. **STOP and VALIDATE**: exercise quickstart.md Scenario A end-to-end against
   `retail_store_sales`.
4. Ship/demo if ready; User Stories 2 and 3 extend the same SKILL.md incrementally.

### Incremental Delivery

1. Setup + Foundational -> foundation ready (template + module contract exist).
2. Add US1 -> validate independently via quickstart Scenario A (MVP).
3. Add US2 -> validate independently via quickstart Scenario B (including the Net-Sales
   consistency check, SC-006).
4. Add US3 -> validate independently via quickstart Scenario C (obligation-verb grep).
5. Polish (Phase 6) closes the loop: composes-only proof, `retail check` green, no-score/no-
   obligation scans, generic-token scan, encoding sweep, FR-coverage self-check.

---

## Principle-V carve-out (do NOT implement a resolution)

- FR-010 (the contract<->gold-column and TMDL-measure<->contract name-resolution method) is
  and stays OPEN. No task in this file authorizes, implements, or even sketches a
  name-similarity heuristic that would promote a candidate link to `proven`. T008, T013, and
  T015 reference FR-010 only to specify the fail-safe default that ships regardless of the
  eventual ruling: every such link is recorded `unresolved`/candidate, never `proven`, never
  silently auto-accepted. The `[NEEDS CLARIFICATION]` marker in spec.md's FR-010 is preserved
  as-is; no task here closes it.
- The `docs/roadmap/roadmap.md` F039 ledger row (plan.md Project Structure, research.md
  section 1.5) is likewise NOT a task in this file -- it is explicitly INTEGRATION-TIME work
  for whoever merges this feature, deferred to avoid colliding with 18 other in-flight
  features on that shared file. If a future stage adds it, it is a separate, later edit, not
  part of this build.
