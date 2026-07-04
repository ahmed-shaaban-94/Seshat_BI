---

description: "Task list for Consumer-Facing Generated Data Dictionary"
---

# Tasks: Consumer-Facing Generated Data Dictionary

**Input**: Design documents from `specs/101-consumer-data-dictionary/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md (all present)

**Deliverable shape**: docs/skill/template Product Module -- NO runtime code, NO
`retail check` rule, NO rule-id (FR-017, Collision-Avoidance Allocation). Verification is
`retail check` staying green with an UNCHANGED rule count, plus doc-level demonstration of
the acceptance scenarios against the already-authored `quickstart.md` (F028/F035/F039
precedent). No pytest module is added; no `src/` or `tests/` change.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency)
- **[Story]**: US1 / US2 / US3 (from spec.md), or SETUP / POLISH

## Phase 1: Setup

- [ ] T001 [SETUP] Confirm the three read-source artifact families this module composes
  from exist and are readable for the cited illustrative table, per research.md section 2:
  `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`,
  `mappings/retail_store_sales/source-map.yaml`, and
  `mappings/retail_store_sales/metrics/*.yaml` (5 files). Record any absent source as a
  plan risk before authoring. No file is written in this task. (FR-002, FR-003, FR-004)

## Phase 2: Foundational (blocking prerequisites)

**Purpose**: the generic template and the embedded module-contract block that both US1 and
US2's SKILL.md sections reference. Both authored files are touched here, so later
per-story tasks that add SKILL.md sections are sequential against each other (same file),
never `[P]`.

- [ ] T002 Author the generic copy-me template `templates/consumer-data-dictionary.md`
  with the fixed, ordered section shape from data-model.md: document header
  (`table_id`, `generated_on`, `gold_source`, `source_map_source`,
  `metrics_source_dir`), a Gold Column Entries section (one entry per Entity 2 field:
  `column_name`, `gold_table`, `meaning_state`, `meaning_text`/`meaning_source_path` or
  `gap`, `drift_note`), a Metric Entries section (Entity 3 fields:
  `metric_name`, `formula_intent`, `readiness_status`, `approved`, `source_path`, `gap`),
  and a Document-Level Gaps section. Placeholders only -- NO C086/`retail_store_sales`
  column name, grain key, or metric name baked into a fixed label (FR-015); NO score
  field and NO completeness-count field anywhere (FR-013). ASCII, UTF-8 without BOM,
  `--`/`->` only, short repo-relative path (FR-016). (FR-001, FR-007, FR-013, FR-015,
  FR-018)
- [ ] T003 In the same template, encode the Clarification Q2 ordering rules as fixed
  structural rules, not prose suggestions: gold column entries in the committed gold
  migration SQL's `CREATE TABLE` column-definition order; metric entries in the lexical
  (alphabetical) filename order of `mappings/<table>/metrics/*.yaml`. (FR-001,
  data-model.md "Ordering rules")
- [ ] T004 In the same template, encode the Clarification Q3 gap-marker minimum shape as a
  fixed structure: the greppable label `GAP:`, the `subject` (column/metric/`"document"`),
  the closed `reason_code` enum (`no_source_map_entry`, `no_reason_recorded`,
  `contract_missing_or_unreadable`, `no_gold_migration_found`, `source_disagreement`), and
  a non-empty `checked_paths[]` list. (FR-008, FR-014, FR-019, data-model.md Entity 4)
- [ ] T005 Author `.claude/skills/consumer-data-dictionary/SKILL.md` skeleton: purpose,
  the Module Contract block (Product Module; capability level `artifact-writing` per
  research.md section 1.3; Core Authority READ list = the three artifact families;
  derived artifact WRITTEN = `mappings/<table>/consumer-data-dictionary.md`; EXECUTES
  none; no DB/PBIP/F016/F031-33 connection), reusing the F035/F039
  module-contract-embedded-in-SKILL.md shape verbatim in spirit. This task establishes
  the file; later US tasks add its numbered-steps and forbidden-ops content (sequential,
  same file). (FR-002, FR-017, plan.md Design/Structure Decision)

**Checkpoint**: template + module-contract skeleton exist -- user story sections can now be
added to SKILL.md.

---

## Phase 3: User Story 1 -- one plain-language reference per table (Priority: P1) MVP

**Goal**: an analyst gets one ordered document listing every deployed gold column and
every metric contract for one table, each entry traceable to a committed source path, with
no invented prose and no write-back to any upstream artifact.

**Independent Test**: for a table with a committed gold migration SQL and at least one
metric contract, generating the dictionary produces one document listing every deployed
gold column and every metric contract file, each entry citing a committed source path.

- [ ] T006 [US1] In `.claude/skills/consumer-data-dictionary/SKILL.md`, specify Compose
  Step 1: resolve the table's committed gold migration SQL
  (`warehouse/migrations/*_create_gold_<table>*.sql`) and enumerate every column declared
  in its `CREATE TABLE` statement(s), in file-definition order, as the `column_entries[]`
  source. (FR-001, FR-003)
- [ ] T007 [US1] In the same file, specify Compose Step 2: resolve
  `mappings/<table>/source-map.yaml` and, for each gold column from Step 1, look up the
  matching `columns[]` entry's `reason` text; when found, cite it VERBATIM with its exact
  source-map location -- never paraphrased or simplified. (FR-005)
- [ ] T008 [US1] In the same file, specify Compose Step 3: resolve every file under
  `mappings/<table>/metrics/*.yaml` in lexical filename order; for each, carry forward its
  `formula_intent` text VERBATIM and surface its recorded `readiness.status` as-is; list
  approved and pending contracts alike, each clearly marked with its own status (never
  presenting a non-`pass` contract as approved). (FR-004, FR-006, Clarification Q4)
- [ ] T009 [US1] In the same file, specify the citation discipline binding every entry
  (column and metric alike) to at least one repo-relative committed source path it was
  composed from, matching the template's field shape from T002. (FR-007)
- [ ] T010 [US1] In the same file, specify the single-write discipline and forbidden-
  operations list: the module's ONLY write is
  `mappings/<table>/consumer-data-dictionary.md`; it MUST NOT write to, modify, or append
  to `source-map.yaml`, any `metrics/*.yaml` contract, the gold migration SQL,
  `readiness-status.yaml`, `unresolved-questions.md`, or the handoff pack; it MUST NOT add
  a `blocking_reasons[]` or `approvals[]` entry or move any readiness stage; it MUST NOT
  define, approve, revise, or resolve any metric's formula, grain, or business meaning, or
  resolve any open mapping question. (FR-009, FR-011, FR-012)
- [ ] T011 [US1] In the same file, specify the no-score / no-count rule: the generated
  document MUST NOT contain a numeric confidence/health/maturity score or a completeness
  count/"N of M" tally anywhere -- gaps are named markers only (hard rule #9). (FR-013)
- [ ] T012 [US1] In the same file, specify the fixed output path rule:
  `mappings/<table>/consumer-data-dictionary.md`, table-co-located under the table's
  mappings folder, distinct from the handoff pack's item (e) and any F028 evidence-pack
  filename; regenerating overwrites only this module's own output path. (FR-018)

**Checkpoint**: User Story 1 is fully specified and independently demonstrable via
quickstart.md Scenario A.

---

## Phase 4: User Story 2 -- no invented meaning; explicit gaps (Priority: P1)

**Goal**: a column or metric with no committed consumer-legible meaning gets a named gap
marker, never invented prose; the module's integrity guarantee.

**Independent Test**: generate the dictionary for a table with a gold column whose only
committed source is a technical source-map `reason` (or no source-map entry at all, or an
unreadable metric contract); confirm the entry is a verbatim citation or an explicit `GAP:`
marker, never a paraphrase or a silent drop.

- [ ] T013 [US2] In `.claude/skills/consumer-data-dictionary/SKILL.md`, specify the FR-008
  branch: when a gold column has NO corresponding `source-map.yaml` column entry, or an
  entry with no `reason` recorded, emit a `GAP:` marker (reason_code
  `no_source_map_entry` or `no_reason_recorded`) naming the column and the path checked --
  and explicitly state the module MUST NOT generate, infer, or paraphrase a plausible
  business definition to fill the gap. Apply the verbatim-cite-or-gap default (never a
  generated gloss) pending the OPEN FR-008/Q1 owner ruling (see Principle-V carve-out
  below -- this task does not resolve Q1). (FR-008)
- [ ] T014 [US2] In the same file, specify the FR-010 branch: the dictionary describes the
  DEPLOYED gold star only -- a column marked `pii: true` and dropped in `source-map.yaml`,
  or otherwise never materialized to gold, MUST NOT appear in the dictionary at all (not
  even as a gap). (FR-010)
- [ ] T015 [US2] In the same file, specify the FR-014 branch: when no committed gold
  migration SQL is found for the table at all (table has not reached Gold Ready), record
  ONE document-level `GAP:` marker (reason_code `no_gold_migration_found`) and MUST NOT
  fabricate a column list from a design or profiling document instead. (FR-014)
- [ ] T016 [US2] In the same file, specify the FR-019 branch: when the gold migration SQL
  and `source-map.yaml` disagree on a column's presence or name, record a `drift_note` /
  `GAP:` marker (reason_code `source_disagreement`) naming both paths checked -- never
  silently prefer one source as authoritative; live-schema reconciliation against the
  actually-deployed database stays out of scope (Principle VIII, PENDING). (FR-019)
- [ ] T017 [US2] In the same file, specify the metric-contract-unreadable branch (User
  Story 2 Acceptance Scenario 3): when a metric contract file referenced under
  `mappings/<table>/metrics/` is missing or unreadable, record a `GAP:` marker
  (reason_code `contract_missing_or_unreadable`) citing the attempted path -- never a
  silent drop of that metric from the listing. (FR-008 discipline extended to metrics,
  User Story 2 Acceptance Scenario 3)

**Checkpoint**: User Stories 1 AND 2 are both independently specified and demonstrable
(quickstart.md Scenario B; SC-002, SC-007).

---

## Phase 5: User Story 3 -- the same generator serves any mapped, gold-built table (Priority: P2)

**Goal**: genericity across tables (Principle VII) -- the same skill and template, with
only the table identifier changed, produce a correct dictionary for any table, with no
C086/`retail_store_sales` specifics baked into a fixed section label.

**Independent Test**: generate the dictionary for two different tables; each output
resolves its own gold migration SQL and its own metrics folder; the template's fixed
section labels contain no domain-specific column name, grain key, or metric name.

- [ ] T018 [US3] In `.claude/skills/consumer-data-dictionary/SKILL.md`, specify the
  generic path-resolution rule: given only a table identifier, resolve
  `warehouse/migrations/*_create_gold_<table>*.sql`,
  `mappings/<table>/source-map.yaml`, and `mappings/<table>/metrics/*.yaml` generically --
  no hardcoded table name anywhere in the resolution logic. (FR-015)
- [ ] T019 [US3] Add the generic-only guard to the template (`templates/consumer-data-
  dictionary.md`) and to SKILL.md: audit both for any C086/`retail_store_sales`-specific
  column name, grain key, or metric name in a FIXED section label or placeholder, and
  confirm `retail_store_sales` appears only as a cited, filled illustrative instance in
  prose examples (SKILL.md walkthrough text), never inlined into the template body or a
  fixed label. This is a read/audit pass over both already-authored files, so it depends
  on T002-T018 being complete and is NOT `[P]` (it audits the finished artifacts, not
  independent unwritten ones). (FR-015, SC-006)

**Checkpoint**: All three user stories are independently specified and demonstrable
(quickstart.md Scenario C; SC-005, SC-006).

---

## Phase 6: Polish

- [ ] T020 [POLISH] Validate the fully-authored SKILL.md + template against every scenario
  already written in `quickstart.md` (Scenarios A, B, C, and the five "Edge cases to
  exercise" and five "What this feature does NOT let you do" items) -- confirm no
  quickstart step describes a behavior the authored SKILL.md does not actually specify,
  and no quickstart step is left unaddressed. Do not re-author quickstart.md; it already
  exists and is complete for this feature. (SC-001 through SC-007)
- [ ] T021 [POLISH] ASCII/UTF-8-no-BOM + short-repo-relative-path sweep of the two new
  artifacts (`templates/consumer-data-dictionary.md`,
  `.claude/skills/consumer-data-dictionary/SKILL.md`): confirm `--`/`->` only, no glyphs,
  no BOM, and both paths respect the Windows 260-char budget. (FR-016)
- [ ] T022 [POLISH] Verify `retail check` passes and the rule count is UNCHANGED (this
  feature adds no rule and claims no rule-id); confirm no `src/retail/rules/` entry and no
  `tests/` change was introduced anywhere in the diff. (FR-017)
- [ ] T023 [POLISH] Confirm the composes-only guarantee by diffing the feature's file
  changes against the "Real repo paths this feature EDITS: (none)" list in plan.md's
  Project Structure section -- the diff must show only the two new authored files (T002,
  T005) plus this `specs/101-consumer-data-dictionary/` documentation set; no existing
  shipped file (`source-map.yaml`, any `metrics/*.yaml`, gold migration SQL,
  `readiness-status.yaml`, the handoff pack, `docs/roadmap/roadmap.md`) is modified.
  (FR-011, SC-004)
- [ ] T024 [POLISH] Record, in a plan/PR note only (not a roadmap-ledger edit), that the
  F040 roadmap-ledger row proposed in research.md section 1.4 remains an INTEGRATION-TIME
  edit to `docs/roadmap/roadmap.md`, deliberately deferred past this task list to avoid
  colliding with other in-flight features touching that shared file (plan.md Project
  Structure "Real repo paths this feature EDITS: none"; research.md section 1.4). This
  task authors no edit to `docs/roadmap/roadmap.md`.

## Dependencies

- T001 (Setup) has no dependency and can start immediately.
- T002-T005 (Foundational: template + module-contract skeleton) depend on T001 and BLOCK
  all of Phase 3-5 -- every US task edits either the template or SKILL.md that T002-T005
  establish.
- T002, T003, T004 all edit `templates/consumer-data-dictionary.md` -- sequential, not
  `[P]`, against each other. T005 edits a different file (`SKILL.md`) and could in
  principle run alongside T002-T004, but is listed sequentially here since it is small and
  the two files share the same field vocabulary from data-model.md.
- T006-T012 (US1) all edit the same `SKILL.md` file established by T005 -- sequential, not
  `[P]`, against each other or against T013-T019.
- T013-T017 (US2) all edit the same `SKILL.md` file -- sequential against each other and
  against US1/US3's SKILL.md edits. US2 is the MVP's integrity companion to US1; both are
  P1 and should ship together before US3.
- T018 (US3) edits `SKILL.md`; T019 audits both authored files and depends on T002-T018
  being complete (it is a finished-artifact audit, not `[P]`).
- T020-T024 (Polish) depend on all of T002-T019 being complete.

## Parallel Example

```bash
# T001 (Setup) has no dependency and can run alone first.

# Within Foundational, T002-T004 (same file: templates/consumer-data-dictionary.md)
# must run sequentially. T005 (different file: SKILL.md) could start once data-model.md's
# field vocabulary is fixed, but is sequenced here for simplicity.

# US1 and US2 tasks (T006-T017) all edit the same SKILL.md file and must be applied
# sequentially, in the order listed, even though they are grouped under different
# priorities.

# T019 runs last among the authoring tasks: it audits the two already-authored files
# for genericity, so it depends on T002-T018 rather than racing them.
```

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

Both US1 and US2 are Priority P1: US1 delivers the dictionary's entire value (a composed,
cited reference); US2 delivers the module's integrity guarantee (no invented meaning, ever
an explicit gap instead). Neither is a viable MVP without the other, per spec.md's own P1
pairing (User Story 2's "Why this priority" ties it to day-one integrity, matching the 063
precedent's own no-fabrication User Story 2). Complete Setup -> Foundational -> US1 -> US2,
then STOP and VALIDATE against quickstart.md Scenarios A and B before starting US3.

### Incremental Delivery

1. Setup + Foundational -> template and module-contract skeleton exist.
2. US1 -> a table with clean, fully-cited inputs produces a correct dictionary.
3. US2 -> the same module handles missing/unreadable/drifted inputs safely (no invented
   prose).
4. US3 -> the same module is proven generic across a second table.
5. Polish -> ASCII/path sweep, `retail check` rule-count-unchanged proof, composes-only
   diff proof, and the deferred-roadmap-edit note.

## Principle-V carve-out (do NOT implement a resolution)

- **FR-008 / Clarification Q1** (may the module GENERATE a simplified, consumer-plain
  paraphrase of a column's existing TECHNICAL source-map `reason`, or must it always fall
  back to verbatim-cite-or-gap) stays OPEN. T013 references it as an input constraint; NO
  task in this list resolves it. The template and SKILL.md ship the verbatim-cite-or-gap
  fail-safe default only, regardless of the eventual ruling. Owner: retail-kpi /
  data-owner (named human TBD at plan/approval time) -- not decided by this task list.
