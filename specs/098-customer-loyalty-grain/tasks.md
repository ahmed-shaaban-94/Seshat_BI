---
description: "Task list for 098-customer-loyalty-grain (Customer / Loyalty Grain + Dimension Pattern)"
---

# Tasks: Customer / Loyalty Grain + Dimension Pattern

**Input**: Design documents from `specs/098-customer-loyalty-grain/`
(spec.md, plan.md, research.md, data-model.md, quickstart.md)

**Tests**: NOT included. This feature authors markdown documentation and a
markdown template only -- plan.md's Testing section is explicit that "no
automated test suite is added (there is no code to unit-test)." Verification
is the set of static/textual checks quickstart.md already enumerates (grep +
diff + `retail check` exit code), reused below as Polish tasks.

**No static-rule wiring phase**: unlike a rule-adding feature (e.g. spec
087's HR1), this feature adds NO `src/retail/rules/` entry, no
`@register(...)` call, and touches none of the six rule-wiring surfaces
(`rules/__init__.py`, `test_rules_wiring.py`, `rules-manifest.json`,
`severity-posture.json`, `glossary.md`, `rule-count-claims.yaml`). The
collision-avoidance allocation for this parallel-build round is explicit:
"Adds NO static rule." Docs-first ordering (hard rule #8) is honored by
having no automation task at all, not by sequencing one after the docs.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3), or
  `SETUP`/`FOUND`/`POLISH` for cross-cutting phases
- Every task names an exact repo-relative file path

## Path Conventions

Single project, additive-only, docs + one template (plan.md "Structure
Decision"). Exactly three new files, one new directory
(`docs/patterns/`). No existing file is edited by any task below.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the pre-feature tree matches plan.md's stated
precondition before any content is authored, and create the one new
directory.

- [ ] **T001** `[SETUP]` Confirm `docs/patterns/` does not yet exist and that
  none of `docs/patterns/customer-dimension-pattern.md`,
  `docs/patterns/customer-grain-pattern.md`, or
  `templates/customer-dimension.md` is present in the current tree (plan.md
  "Status: Draft... none is authored by this planning stage"). Plain
  confirmation, not a judgment call. _Satisfies: plan.md precondition._
- [ ] **T002** `[SETUP]` Create the `docs/patterns/` directory (empty, ready
  to receive T004/T005 below). _Satisfies: plan.md Project Structure ("NEW
  directory, confirmed absent pre-feature")._

**Checkpoint**: the target directory exists and no target file is present --
safe to author.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Fix the ONE shared convention every subsequent authoring task
must reuse verbatim, so the three artifacts do not drift into two marker
spellings or two different RC14 restatements. No content file is written
yet in this phase.

**CRITICAL**: Phase 3+ tasks that author `[NEEDS CLARIFICATION: ...]` slots
MUST use exactly the string fixed in T003; Phase 3+ tasks that author the
surrogate-key / unknown-member mechanic MUST use exactly the RC14 shape
fixed in T004.

- [ ] **T003** `[FOUND]` Fix the canonical unresolved-ruling marker string
  used byte-identically across all three authored artifacts (data-model.md
  "The canonical unresolved-ruling marker"; spec.md Clarify Q1, FR-002):
  `[NEEDS CLARIFICATION: <slot-specific reason> -- owner ruling]`. This is a
  planning note for the tasks below, not a file write. _Satisfies: FR-002
  (one canonical marker)._
- [ ] **T004** `[FOUND]` Fix the RC14 structural mechanic every authoring
  task reuses: `customer_sk` (`*_sk` surrogate-key convention), the `-1`
  unknown-member row, and FK `COALESCE`-to-`-1` for joins
  (`docs/decisions/0002-retail-cleaning-defaults.md`). No new key convention
  is invented (spec.md Assumptions). Planning note, not a file write.
  _Satisfies: FR-002 (surrogate key + unknown-member row), FR-003
  (structural FK join), Constitution Principle VI._

**Checkpoint**: the marker spelling and the RC14 mechanic are fixed; every
authoring task in Phase 3-5 cites T003/T004 rather than inventing its own
wording.

---

## Phase 3: User Story 1 - An analyst has a generic conformed customer dimension shape to start from (Priority: P1) MVP

**Goal**: `docs/patterns/customer-dimension-pattern.md` and
`templates/customer-dimension.md` exist, each naming a surrogate key, an
explicit unresolved identity-key slot, an explicit unresolved PII-publish
slot, an explicit unresolved SCD/historization-type slot, and the `-1`
unknown-member row -- with no C086 column/table name or ruling baked in as a
default.

**Independent Test**: Read `docs/patterns/customer-dimension-pattern.md` and
`templates/customer-dimension.md` in isolation; confirm the dimension shape
names a surrogate key, an explicit unresolved identity-key slot, an explicit
unresolved PII-publish slot, and the -1 unknown-member row, and confirm
neither file answers either slot or names a specific field.

### Implementation for User Story 1

- [ ] **T005** `[US1]` Author
  `docs/patterns/customer-dimension-pattern.md` with: (a) a surrogate key
  section (`customer_sk`, RC14, FILLED per T004); (b) an explicit
  natural/identity-key slot using T003's marker verbatim
  (`[NEEDS CLARIFICATION: identity key not ruled -- owner ruling]`), never a
  named field (not `customer_id`, `email`, `loyalty_id`, or `phone`); (c) an
  explicit PII-publish-safety slot using T003's marker
  (`[NEEDS CLARIFICATION: PII publish-safety not ruled -- owner ruling]`),
  stating explicitly that no default ("keep" or "drop") is implied; (d) an
  explicit SCD/historization-type slot using T003's marker
  (`[NEEDS CLARIFICATION: SCD/historization type not ruled -- owner
  ruling]`), naming Type 1 ("overwrite") and Type 2 ("track history") as the
  two options and deciding neither; (e) the `-1` unknown-member row
  convention (RC14, FILLED). Cite `mappings/retail_store_sales/...` only in
  prose as "one filled, source-specific answer," never as a default value.
  Depends on T002, T003, T004. _Satisfies: FR-002, FR-006, FR-007 (no
  restated Q1 default), FR-011, Key Entities "Customer dimension pattern",
  "Identity-key slot", "PII-publish slot", "SCD/historization-type slot"._
- [ ] **T006** `[P]` `[US1]` Author `templates/customer-dimension.md` as a
  fillable worksheet (not expository prose) instantiating the same four
  slots as T005: `customer_sk` (structural convention, FILLED), an
  identity-key slot (unresolved marker, to be filled by a future table's
  owner), a PII-publish slot (unresolved marker), an SCD/historization slot
  (unresolved marker), and the `-1` unknown-member row (FILLED). Structure
  it so a future `source-map.yaml` `gold_star.dimensions[]` entry can cite it
  BY NAME without copying its prose inline -- maps onto the EXISTING
  `.name` / `.surrogate_key` / `.has_unknown_member` / `.attributes[]` keys
  already in `templates/source-map.yaml` (no new schema key added). Depends
  on T002, T003, T004. _Satisfies: FR-001 (copy-me dimension template),
  FR-014, FR-011, Key Entities "Customer dimension template"._

**Checkpoint**: the dimension pattern and its copy-me template both exist
and are independently readable per User Story 1's Independent Test. This is
the MVP slice.

---

## Phase 4: User Story 2 - An analyst has a generic customer-grain pattern for retention/frequency/CLV facts (Priority: P1)

**Goal**: `docs/patterns/customer-grain-pattern.md` exists (doc-only, no
template -- Clarify Q3), naming one candidate-grain entry for each of the
four Planned customer KPIs in `domains/customer.md`, each keyed to
`customer_sk` via FK COALESCE-to-`-1`, with the retention window, CLV
horizon, and new-vs-returning anchor left as unresolved markers.

**Independent Test**: Read `docs/patterns/customer-grain-pattern.md` in
isolation; confirm it names candidate grains for the four Planned customer
KPIs, cites `domains/customer.md` for the underlying ambiguity, and asserts
none of retention-window, CLV-horizon, or new-vs-returning anchor as a
decided value.

### Implementation for User Story 2

- [ ] **T007** `[US2]` Author `docs/patterns/customer-grain-pattern.md` with
  one row per Planned customer KPI cited from
  `skills/retail-kpi-knowledge/domains/customer.md` (data-model.md
  "CustomerGrainPattern" table; SC-002 requires exactly four, 0 decided):
  (a) Customer Retention Rate -- a periodic-snapshot candidate grain ("one
  row per customer per calendar period") as an OPTION, period length marked
  `[NEEDS CLARIFICATION: retention window not ruled -- owner ruling]`; (b)
  Purchase Frequency -- the same periodic-snapshot grain family, sharing the
  same retention-window marker rather than inventing a second period; (c)
  Customer Lifetime Value (CLV) -- a customer-to-date candidate grain ("one
  row per customer, lifetime-to-date") as an OPTION, horizon/discounting
  marked `[NEEDS CLARIFICATION: CLV horizon not ruled -- owner ruling]`; (d)
  New-vs-Returning Customer split -- a periodic-snapshot grain classifying
  each period's customers against a first-purchase anchor, anchor marked
  `[NEEDS CLARIFICATION: anchor not ruled -- owner ruling]`. Every row states
  the structural FK join fixed by T004 (`customer_sk`, COALESCE'd to `-1`).
  Cross-reference `domains/customer.md` for the underlying ambiguity rather
  than restating its stops in different words. Depends on T002, T003, T004.
  _Satisfies: FR-003, FR-004, FR-006, FR-011, Key Entities
  "Customer-grain pattern", data-model.md "CustomerGrainPattern" table._

**Checkpoint**: the grain pattern doc exists, names all four candidate
grains with the structural join fixed and the semantic parameters left open,
per User Story 2's Independent Test.

---

## Phase 5: User Story 3 - The pattern names identity resolution as a stop, without deciding it (Priority: P2)

**Goal**: `docs/patterns/customer-dimension-pattern.md` (from Phase 3)
gains an identity-resolution section stating that resolving multiple raw ids
to one `customer_sk` is a reserved owner ruling, cross-referencing
`domains/customer.md`'s identity/grain stop, and proposing no merge rule,
matching heuristic, or precedence order.

**Independent Test**: Read the pattern doc's identity-resolution section in
isolation; confirm it states the multi-id problem, cites
`domains/customer.md`'s identity/grain stop, and proposes no merge rule,
matching heuristic, or precedence order between competing raw ids.

**Note on file overlap**: `IdentityResolutionStop` is a section WITHIN
`docs/patterns/customer-dimension-pattern.md` (data-model.md: "Not a new
entity with its own file"), not a separate file. This task therefore
extends the SAME file T005 authors and must run AFTER T005, not in
parallel with it.

### Implementation for User Story 3

- [ ] **T008** `[US3]` Extend `docs/patterns/customer-dimension-pattern.md`
  (authored in T005) with an identity-resolution section: state that
  resolving multiple raw ids (e.g. a loyalty card AND a phone number) to one
  `customer_sk` is a reserved owner ruling; cross-reference
  `skills/retail-kpi-knowledge/domains/customer.md`'s identity/grain
  Principle-V stop by path; propose NO merge rule, matching heuristic, or
  precedence order (e.g. no "prefer loyalty id over phone" language)
  anywhere in the section. Depends on T005. _Satisfies: FR-005, FR-006, Key
  Entities "Identity-resolution stop", data-model.md
  "IdentityResolutionStop"._

**Checkpoint**: all three user stories are independently satisfied. The
dimension pattern (with its identity-resolution section), its template, and
the grain pattern all exist, are internally consistent on the T003 marker
and T004 RC14 mechanic, and decide none of the reserved Principle-V rulings.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: The mechanical verification checks quickstart.md already
enumerates (SC-003 through SC-007, FR-007 through FR-013, FR-015) -- run
once, after all three artifacts exist, because each check spans more than
one authored file or compares against the pre-existing tree.

- [ ] **T009** `[P]` `[POLISH]` Diff
  `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`,
  `powerbi/RetailStoreSales.SemanticModel/definition/tables/gold
  dim_customer_rss.tmdl`, and
  `skills/retail-kpi-knowledge/domains/customer.md` against the pre-feature
  tree and confirm all three are byte-identical (no edit landed in any of
  them). _Satisfies: FR-007, FR-008, SC-005, quickstart.md step 6._
- [ ] **T010** `[P]` `[POLISH]` Grep
  `docs/patterns/customer-dimension-pattern.md`,
  `docs/patterns/customer-grain-pattern.md`, and
  `templates/customer-dimension.md` for `retail_store_sales`, `customer_id`,
  and "keep"/"drop" presented as a default PII answer; confirm none appears
  as a filled value (the worked example may be cited only in prose as "see
  `mappings/retail_store_sales/...` for one filled, source-specific
  answer"). _Satisfies: FR-011, SC-003, quickstart.md step 7._
- [ ] **T011** `[P]` `[POLISH]` Grep the same three files for a percentage,
  a health/maturity/confidence number, or an "N of M" completeness count;
  confirm none appears anywhere (hard rule #9). _Satisfies: FR-010, SC-004,
  quickstart.md step 8._
- [ ] **T012** `[P]` `[POLISH]` Grep the same three files for the T003
  marker string and confirm every unresolved slot (identity-key,
  PII-publish, SCD/historization, retention window, CLV horizon,
  new-vs-returning anchor) uses the identical spelling -- no second marker
  variant (e.g. `[NEEDS CLARIFICATION / owner ruling]`) survived from the
  spec's own illustrative inconsistency (Clarify Q1). _Satisfies: FR-002
  (one canonical marker across all three artifacts)._
- [ ] **T013** `[P]` `[POLISH]` Confirm all three authored files are ASCII,
  UTF-8 without BOM (`--` and `->`, no Unicode glyphs), and that their repo-
  relative paths stay well under the Windows 260-char budget. _Satisfies:
  FR-012, Constitution Principle IX._
- [ ] **T014** `[POLISH]` Run `retail check` over the changed tree and
  confirm it exits 0 with the SAME registered-rule count as before this
  feature (no new rule id introduced -- this feature added none). _Satisfies:
  FR-015, SC-006, quickstart.md step 9._
- [ ] **T015** `[P]` `[POLISH]` Confirm zero files were created or modified
  under `contracts/` by this feature. _Satisfies: FR-009, SC-007,
  quickstart.md step 10._
- [ ] **T016** `[P]` `[POLISH]` Confirm no task above opened a live database
  connection, invoked the deferred Power BI execution adapter (F016), or
  assumed any live-profile result -- all three artifacts are static,
  offline-readable text. _Satisfies: FR-013, Constitution Principle VIII,
  quickstart.md step 11._
- [ ] **T017** `[POLISH]` Confirm `templates/customer-dimension.md` maps
  onto the EXISTING `gold_star.dimensions[].name` / `.surrogate_key` /
  `.has_unknown_member` / `.attributes[]` fields already defined in
  `templates/source-map.yaml`, and that no new key was added to that
  schema. _Satisfies: FR-014, data-model.md "Citable, not merely
  descriptive"._

**Checkpoint**: Feature complete. Exactly three new files exist under
`docs/patterns/` and `templates/`; no existing file is edited; no numeric
score, no C086-specific default, and no undecided Principle-V ruling was
smuggled in as a default anywhere; `retail check` is unaffected.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies -- confirms the precondition and
  creates the one new directory.
- **Foundational (Phase 2)**: depends on Setup (T002's directory must exist
  before any file is written into it); fixes the marker string (T003) and
  the RC14 mechanic (T004) that every authoring task below reuses verbatim.
  BLOCKS all user stories.
- **User Stories (Phase 3-5)**: all depend on Foundational (Phase 2)
  completion. US1 (Phase 3) and US2 (Phase 4) touch disjoint files
  (`customer-dimension-pattern.md` + `customer-dimension.md` vs.
  `customer-grain-pattern.md`) and can proceed in parallel. US3 (Phase 5)
  extends the SAME file US1's T005 authors
  (`docs/patterns/customer-dimension-pattern.md`) and MUST run after T005 --
  it is not parallel with US1, despite being a separate user story.
- **Polish (Phase 6)**: depends on all three files existing (T005, T006,
  T007, T008) -- every Polish task reads/greps/diffs across the full set of
  authored artifacts plus the pre-existing tree.

### Within Each User Story

- US1: T006 (template) may run in parallel with T005 (pattern doc) -- both
  depend only on Phase 2, not on each other, since neither's content
  requires the other to already exist (both instantiate the same slots
  independently per data-model.md, and cross-linking prose can be added by
  either without blocking).
- US3: T008 depends on T005 (same-file extension, sequential).

### Parallel Opportunities

- T005 and T006 (US1: different files) can run in parallel.
- T005/T006 (US1) and T007 (US2) can run in parallel (disjoint files).
- T008 (US3) cannot start until T005 completes (same-file dependency).
- All Polish tasks T009-T013, T015, T016 are read-only checks over
  different concerns and can run in parallel with each other; T014 (`retail
  check`) and T017 (schema cross-check) are best run after T009-T013 confirm
  content correctness, though nothing technically blocks them.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational).
2. Complete Phase 3 (US1) -- the dimension pattern doc and its copy-me
   template both exist with all four slots correctly marked.
3. **STOP and VALIDATE**: read both files per US1's Independent Test.
4. This is the MVP: a future analyst already has a generic dimension shape
   to start from, even before the grain pattern or the identity-resolution
   section land.

### Incremental Delivery

1. Setup + Foundational -> marker string and RC14 mechanic fixed.
2. Add US1 -> MVP -- generic dimension pattern + copy-me template.
3. Add US2 -> generic grain pattern for retention/frequency/CLV/
   new-vs-returning (independently useful once a dimension exists).
4. Add US3 -> identity-resolution section extends US1's file, closing the
   sharpest Principle-V edge the scope guard names.
5. Polish -> mechanical verification (byte-identical neighbours, no
   C086 default, no numeric score, one marker spelling, ASCII/UTF-8,
   `retail check` unaffected, `contracts/` untouched, no live surface,
   template-schema cross-check).

### Requirement Coverage Check (every FR maps to >=1 task)

- FR-001 -> T005, T006, T007 (two pattern docs + one template; grain stays
  doc-only, no template task exists for it)
- FR-002 -> T003, T005, T012
- FR-003 -> T004, T007
- FR-004 -> T007
- FR-005 -> T008
- FR-006 -> T005, T007, T008
- FR-007 -> T005, T009
- FR-008 -> T009
- FR-009 -> T015
- FR-010 -> T011
- FR-011 -> T005, T006, T007, T010
- FR-012 -> T013
- FR-013 -> T016
- FR-014 -> T006, T017
- FR-015 -> T014
