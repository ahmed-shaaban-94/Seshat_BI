# Feature Specification: Dimension History / SCD Policy Readiness

**Feature Branch**: `088-scd-dimension-history-policy`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Dimension history / SCD policy readiness (gap #8).
Declare an explicit SCD type (Type-1 overwrite vs Type-2 historized) per dimension in the
source-map, and a static check that the gold star honors it. Today gold is
drop-and-rebuild = implicit Type-1; past facts silently re-point to today's attributes."

## Overview

Constitution Principle III requires gold to be a Kimball star -- fact + conformed
dimensions. Kimball dimensional modelling recognizes that a dimension's ATTRIBUTES
change over time (a store changes region, a product changes category), and that
whether a change OVERWRITES history (SCD Type-1) or PRESERVES it (SCD Type-2, a new
dated row) is a modelling decision with real consequences: under Type-1, a fact from
last year silently re-points to this year's attribute value when the dimension is
rebuilt, corrupting historical analysis with no error and no warning.

Today this decision is never made explicitly. `retail-build-warehouse`
(`.claude/skills/retail-build-warehouse/SKILL.md`) authors every gold dimension the
same way: every `DROP TABLE IF EXISTS` batched up front, then each dimension
recreated by explicit column DDL plus `INSERT` (the documented gold shape; silver
alone uses a `CREATE TABLE ... AS SELECT` CTAS form -- see Clarifications 2026-07-04,
C5) inside one transaction (a bare drop-and-rebuild either way, "S4b layer-aware"
allows this for derived silver/gold). This is, in effect, SCD Type-1 for every
dimension in every star,
chosen by omission rather than by a recorded decision. `gold_star.dimensions[]`
(`templates/source-map.yaml`) carries no field that says whether a given dimension
was MEANT to overwrite or to preserve history, so a table's own Mapping Ready review
cannot see the gap, and Gold Ready's static checks (S6 unknown-member, S7 contiguous
date dim) do not look for it either. A dimension that a human intends to historize
(Type-2) can pass every existing gate while its migration silently drop-and-rebuilds
it -- an unnoticed policy violation, not a data-quality bug any current check catches.

This feature closes that gap for the STATIC layer only: (1) a new per-dimension field,
`gold_star.dimensions[].scd_type`, in which a human declares `type_1` or `type_2` for
each gold dimension at Mapping Ready, and (2) a new static `retail check` rule,
reserved id **HR2**, that reads the declared `scd_type` alongside the table's gold
migration SQL and fails closed when a dimension declared `type_2` is built by a
mechanism that cannot preserve history (drop-and-rebuild is the only mechanism this
repo's tooling currently authors). The feature does NOT choose a dimension's SCD type
-- that is an owner/analyst ruling, exactly like grain or PII handling (Principle V) --
and it does NOT execute any SQL; it is a static declaration plus a static check.

## Boundary against neighbouring shipped work (read first)

This feature is a genuine NEW readiness signal for an axis (dimension history) no
existing gate names, not a restatement of an existing check. It shares the
`gold_star.dimensions[]` surface with shipped and coordinated-but-unshipped work and
must stay narrowly on its own sub-key. Shipped neighbours that must stay distinct:

- **The source-mapping gate / `source-map.yaml`** (Principle IV, spec 001;
  `templates/source-map.yaml`) already owns `gold_star.dimensions[]` (`name`,
  `surrogate_key`, `has_unknown_member`, `attributes[]`) and RC14 (the `_sk` / unknown
  member / FK COALESCE / degenerate-dim defaults, `docs/decisions/0002-retail-cleaning-defaults.md`).
  This feature ADDS exactly one new nested key, `scd_type`, under each existing
  dimension entry -- it does not touch `surrogate_key`, `has_unknown_member`, or
  `attributes[]`, and it does not re-decide any table's grain, PK, or placement
  (those are that table's already-reviewed Mapping Ready judgments).
- **Gold Ready (Stage 4)** (`docs/readiness/gold-ready.md`, spec 006
  warehouse-builder + spec 004 retail-validate) already runs static S6 (`-1` unknown
  member present) and S7 (contiguous `generate_series` date dim), plus live RC2 / RC15
  / RC16. HR2 is a NEW static check added to that same Gold Ready static surface -- it
  does not re-implement S6/S7, does not touch `retail validate`, and does not change
  any existing Gold Ready status meaning; a table can still reach `pass` on S6/S7/live
  validate while HR2 reports its own finding.
- **`retail-build-warehouse`** (spec 006) is the skill whose documented pattern (bare
  `DROP TABLE IF EXISTS ... CREATE TABLE ... AS ...` for gold, "S4b layer-aware")
  creates the very drop-and-rebuild gap this feature names. HR2 reads that pattern's
  known shape to detect the mismatch; it does NOT rewrite the skill's authored SQL and
  does NOT add an SCD-2 (dated-row / merge) authoring mode to it -- teaching the
  builder to author Type-2 SQL is explicitly out of scope (Assumptions).
- **HR1 cross-star conformed-dimension gate** (spec 087, reserved id HR1, DRAFT) also
  reads `gold_star.dimensions[]` across stars, but on an ORTHOGONAL axis: HR1 checks
  that a shared dimension NAME agrees on grain/key/type ACROSS two or more stars; HR2
  checks that ONE dimension's declared HISTORY POLICY is honored by its OWN star's
  build. HR1 adds no new `source-map.yaml` key by its own rule (its declaration lives
  in a separate `conformed-dimension-map.yaml`); HR2 is the one that adds the new
  `scd_type` key. The two rule ids and the two concerns do not overlap and neither
  reads the other's artifact.
- **SF1 shared-checklist fork detector** (`src/retail/rules/rule_sf1.py`, spec 086)
  and **AP1** (`src/retail/rules/rule_ap1.py`, spec 085) are the DESIGN and WIRING
  precedent this feature follows for how a new rule id is registered, wired across the
  five meta-gate surfaces, and fixture-tested. HR2 does not edit either rule.

This feature is coordinated, NOT collision-tested, against three OTHER in-flight
`source-map.yaml` adders that touch the same `gold_star` block from different
sub-keys: 090 (freshness), 103 (currency/unit), 105 (data-contract). None of those
directories exist yet in this tree; per the collision-avoidance allocation, this
feature's ENTIRE schema footprint is the single nested key
`gold_star.dimensions[].scd_type` -- no top-level key, no sibling key on the
dimension entry beyond that one addition.

This feature adds a NEW `retail check` rule (id HR2) -- unlike a Product Module
(F027/F028), which adds no gate. It follows the SF1/AP1/HR1 rule-adding shape: one
registered static rule, its wiring across the meta-gate surfaces, and its fixtures.
It adds NO new readiness stage; `scd_type` is recorded inside the existing Mapping
Ready artifact and HR2 runs on the existing Gold Ready static surface.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A human declares each dimension's history policy at Mapping Ready (Priority: P1)

An analyst reviewing a table's `source-map.yaml` at Mapping Ready reaches the
`gold_star.dimensions[]` block and, for each dimension, records whether it is
`type_1` (overwrite -- the default, matching today's drop-and-rebuild behavior) or
`type_2` (historized -- changes must be preserved as dated rows). This is recorded
once per dimension, next to the dimension's other Mapping Ready-owned fields, so the
decision travels with the map a reviewer already reads and approves.

**Why this priority**: Without an explicit field to declare intent, there is nothing
for HR2 to check and no artifact for a human to review -- this is the foundation the
rest of the feature rests on.

**Independent Test**: Add `scd_type: "type_2"` to one dimension entry and
`scd_type: "type_1"` to another in a fixture `source-map.yaml`; confirm both parse
as valid declared values and that a `retail check` run over that table reports no
missing-declaration finding for either dimension.

**Acceptance Scenarios**:

1. **Given** a `source-map.yaml` whose every `gold_star.dimensions[]` entry carries a
   valid `scd_type` (`type_1` or `type_2`), **When** `retail check` runs, **Then** HR2
   reports no missing-declaration finding for that table.
2. **Given** a dimension entry with `scd_type: "type_2"`, **When** the map is read,
   **Then** the value is recorded as a human declaration next to the dimension's
   `surrogate_key` / `attributes[]`, not inferred or defaulted by tooling.
3. **Given** a dimension entry with an unrecognized `scd_type` value (neither `type_1`
   nor `type_2`), **When** `retail check` runs, **Then** HR2 emits a fail-closed
   finding naming the dimension and the invalid value.

---

### User Story 2 - Fail closed when a Type-2 dimension is built by drop-and-rebuild (Priority: P1)

As the `retail check` gate, when a dimension is declared `scd_type: "type_2"` but its
table's gold migration SQL builds every dimension by drop-and-rebuild (the only
mechanism this repo's tooling currently authors -- a `DROP TABLE IF EXISTS` for that
dimension's table paired, same file, with a `CREATE TABLE` that recreates it, whether
authored as CTAS or as column DDL plus `INSERT` (both are drop-and-rebuild; see
Clarifications 2026-07-04, C5), with no dated-row / effective-period preservation
either way), I emit a fail-closed finding: the declared policy
(preserve history) cannot be honored by the build regime that exists, so past facts
would silently re-point to today's attributes the moment that migration re-runs. This
is the feature's whole point -- it is the ONE new signal that makes today's silent gap
visible and blocking wherever a human has declared they need history.

**Why this priority**: This is the enforcement half of the feature; without it,
`scd_type` is a comment nobody checks, and the gap the feature exists to close
(silent implicit Type-1) remains silent. It is the MVP.

**Independent Test**: With a fixture `source-map.yaml` declaring one dimension
`type_2` and a fixture gold migration SQL file containing, for that dimension's own
gold table, a `DROP TABLE IF EXISTS <dim_table>` paired, in the same file, with a
`CREATE TABLE <dim_table>` that recreates it (the documented `retail-build-warehouse`
GOLD pattern: batched drops up front, then per-dimension explicit-column DDL plus
`INSERT` -- see Clarifications 2026-07-04, C5; a CTAS-form fixture MUST also be
covered since either authored form is in scope), assert HR2 emits exactly one
fail-closed (ERROR) finding naming the dimension and the migration file. With the
dimension changed to `type_1`, assert HR2 emits no finding for that table
(drop-and-rebuild honors a Type-1 declaration by construction). This IS implementable
today: the detection is a scoped text match against the one documented,
currently-authored construct, not a deferred capability.

**Acceptance Scenarios**:

1. **Given** a dimension declared `type_2` and its gold migration file containing,
   scoped to that dimension's own gold table, a `DROP TABLE IF EXISTS <dim_table>`
   paired, in the same file, with a `CREATE TABLE <dim_table>` that recreates it (the
   `retail-build-warehouse` drop-and-rebuild pattern, in either its CTAS or its
   DDL-plus-`INSERT` authored form, and regardless of whether the `DROP` and
   `CREATE` are textually adjacent -- Clarifications 2026-07-04, C5), **When**
   `retail check` runs, **Then** HR2 emits one fail-closed ERROR finding naming the
   dimension, the migration file, and the drop-and-rebuild construct it found.
2. **Given** the same table with every dimension declared `type_1`, **When**
   `retail check` runs, **Then** HR2 emits no finding for that table (drop-and-rebuild
   is the correct, honored build for an overwrite policy).
3. **Given** a dimension declared `type_2` whose gold migration file cannot be found
   (no `warehouse/migrations/*create_gold_<table>_star.sql` exists yet), **When**
   `retail check` runs, **Then** HR2 records this as a not-yet-buildable state (no
   finding fabricated about a migration that does not exist) -- the check only fires
   once a gold migration is present to inspect.

---

### User Story 3 - A dimension's history policy is undeclared (Priority: P2)

A table's `source-map.yaml` was authored before this feature existed, or a new
dimension was added to `gold_star.dimensions[]` without a reviewer setting its
`scd_type`. HR2 treats a missing `scd_type` on any dimension as a blocking
Needs-decision, not a silent default to `type_1` -- because silently assuming Type-1
would reproduce the exact silent gap this feature exists to end, only one layer
higher (an undeclared field instead of an unenforced convention).

**Why this priority**: This closes the migration/adoption path for the many tables
mapped before this feature shipped; it is essential for the feature to be adoptable
without instantly blocking every existing map, but the core enforcement (US1/US2) is
already a viable slice without it, so it is P2.

**Independent Test**: Take a fixture `source-map.yaml` with one `gold_star.dimensions[]`
entry that has no `scd_type` key at all; assert HR2 emits exactly one Needs-decision
finding naming that dimension and no other finding is fabricated in its place.

**Acceptance Scenarios**:

1. **Given** a dimension entry with no `scd_type` key, **When** `retail check` runs,
   **Then** HR2 emits one Needs-decision finding naming the dimension and instructing
   a human to declare `type_1` or `type_2`; it never infers or silently defaults the
   value.
2. **Given** a table with multiple dimensions missing `scd_type`, **When**
   `retail check` runs, **Then** HR2 emits one finding per undeclared dimension (not
   a single table-wide flag), so each is individually traceable and resolvable.
3. **Given** a Needs-decision finding is later resolved by a human adding
   `scd_type: "type_1"` (or `"type_2"`) to the map, **When** `retail check` runs
   again, **Then** that dimension's Needs-decision finding clears (and, for
   `type_2`, US2's build check now applies).

---

### Edge Cases

- **A dimension with `has_unknown_member: true` and no other history-relevant
  attribute** (the common case): `has_unknown_member` (RC14, the `-1` sentinel row) is
  an ORTHOGONAL concern to `scd_type` (history-over-time) -- HR2 does not read or alter
  `has_unknown_member`, and a dimension may carry both an unknown member and a
  Type-2 policy.
- **A degenerate dimension** (`gold_star.degenerate_dimensions[]`, a transaction id
  carried on the fact per RC14): degenerate dims have no separate dimension table to
  rebuild or historize, so they are OUT OF SCOPE for `scd_type` -- HR2 only reads
  `gold_star.dimensions[]` entries, never `degenerate_dimensions[]`.
- **The date dimension** (`gold_star.date_dimension`): a generated, append-only
  calendar has no "changing attribute" to historize in the SCD sense -- HR2 does not
  require or read an `scd_type` on the `date_dimension` block; the block is out of
  HR2's declaration and enforcement scope.
- **A table with no gold migration yet** (pre-Gold-Ready, e.g. still at Mapping
  Ready): HR2's US1 (declaration presence/validity) can and should run at Mapping
  Ready time; US2 (build-honors-declaration) cannot fire without a gold migration to
  inspect and MUST NOT fabricate a pass or a fail about SQL that does not exist yet
  (see User Story 2, Acceptance Scenario 3).
- **A migration file that contains something other than a bare drop-and-rebuild for
  a Type-2 dimension** (a hand-authored upsert / dated-row / merge pattern): this
  feature does not author or validate the CORRECTNESS of any history-preservation
  SQL -- it only detects the ABSENCE of any recognizable non-destructive construct
  for a declared Type-2 dimension. Whether a given hand-written pattern actually,
  correctly preserves history is a live-data question and is explicitly deferred
  (Assumptions; Principle VIII).
- **A dimension changes from `type_1` to `type_2` (or vice versa) after gold already
  exists**: this is a Mapping Ready map edit like any other and re-triggers HR2 on
  the next `retail check`; this feature does not add a migration/backfill mechanism
  for the transition itself (out of scope; a future spec).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST add exactly one new nested field,
  `gold_star.dimensions[].scd_type`, to the `source-map.yaml` schema
  (`templates/source-map.yaml`), nested under each existing dimension entry. It MUST
  NOT add any new top-level key and MUST NOT add, rename, or remove any other field
  on the dimension entry (`name`, `surrogate_key`, `has_unknown_member`,
  `attributes[]` stay exactly as they are).
- **FR-002**: The permitted values of `scd_type` MUST be exactly `type_1` (overwrite;
  matches today's drop-and-rebuild default) and `type_2` (historized; changes must be
  preserved as dated rows). Any other value MUST be treated as invalid and MUST
  produce a fail-closed finding (User Story 1, Acceptance Scenario 3).
- **FR-003**: `scd_type` MUST be a human-authored declaration made at Mapping Ready
  time, recorded in the same reviewed `source-map.yaml` a human already approves
  (Principle IV) -- it is not inferred, defaulted, or auto-filled by any tool.
- **FR-004**: The feature MUST add exactly one `@register`ed static `retail check`
  rule with reserved id **HR2**, reading only committed files (the table's
  `source-map.yaml` and, when present, its `warehouse/migrations/*create_gold_<table>_star.sql`
  file, where `<table>` is that map's own mapping-directory name, i.e. the source
  table identifier from `mappings/<table>/source-map.yaml`, and the glob's leading
  `*` absorbs the migration's arbitrary numeric filename prefix -- Clarifications
  2026-07-04, C7). It MUST NOT connect to a database, read a live Power BI/PBIP
  surface, or invoke any deferred execution adapter (F016) (Principle VIII).
- **FR-005**: HR2 MUST emit a fail-closed ERROR finding when a `gold_star.dimensions[]`
  entry has no `scd_type` key at all, OR the key is present but holds an empty or
  placeholder value (`""`, `null`, or a case-insensitive `"tbd"` -- Clarifications
  2026-07-04, C6) (Needs-decision; User Story 3) -- it MUST NOT silently default an
  undeclared dimension to `type_1`, because that would reproduce the exact
  silent-Type-1-by-omission gap this feature exists to close. This ERROR applies to
  every table's map, INCLUDING one whose Mapping Ready approval predates this feature
  (Principle I fails closed by design; there is no already-approved-map grandfather
  clause -- adopting this feature means every existing map must gain an explicit
  `scd_type` per dimension before HR2 is clean).
- **FR-006**: HR2 MUST emit a fail-closed ERROR finding when a `scd_type` value is
  present, non-empty, and not one of the two permitted values (FR-002) and not one of
  the placeholder forms routed to FR-005 (Clarifications 2026-07-04, C6), naming the
  dimension and the invalid value.
- **FR-007**: When a table's gold migration file (per FR-004) exists and is
  readable, HR2 MUST inspect it, scoped to each dimension declared `scd_type:
  "type_2"` and that dimension's own gold table, for the documented
  `retail-build-warehouse` GOLD drop-and-rebuild construct: a `DROP TABLE IF
  EXISTS <dim_table>` for that dimension's table PLUS a same-file `CREATE TABLE
  <dim_table>` for the same table, in EITHER authored form -- `CREATE TABLE
  <dim_table> AS SELECT ...` (CTAS) OR explicit column DDL
  (`CREATE TABLE <dim_table> (...)`) followed by one or more `INSERT INTO
  <dim_table> ...` statements -- and WITHOUT requiring the `DROP` and `CREATE` to
  be textually adjacent (the documented gold pattern batches every `DROP TABLE IF
  EXISTS` up front, then recreates each table further down; see Clarifications
  2026-07-04, C5). `<dim_table>` MUST be resolved from the
  dimension entry's OWN `gold_star.dimensions[].name`, stripping an optional
  leading `<schema>.` prefix (e.g. `gold.`) from both the declared `name` and the
  `DROP`/`CREATE` token before comparing the bare table identifier (Clarifications
  2026-07-04, C4) -- this is what SCOPES the match to that one dimension's own
  table, so a `type_1` dimension's drop-and-rebuild elsewhere in the same
  migration file never fires a finding against a different, `type_2`-declared
  dimension. When that construct is found for a
  `type_2`-declared dimension, HR2 MUST emit a fail-closed ERROR finding naming the
  dimension and the migration file -- because that construct discards prior
  attribute values on every re-run, which cannot honor a Type-2 declaration
  (User Story 2). This detection is IMPLEMENTABLE NOW: it is a scoped text match
  against the one construct this repo's tooling currently authors for every gold
  dimension (`.claude/skills/retail-build-warehouse/SKILL.md`), not a deferred
  capability -- it is the feature's P1 MVP enforcement.
  DEFERRED TO PLAN, FUTURE SCOPE ONLY (mechanics gap, not a Principle-V ruling, and
  NOT required for this feature's MVP): once a builder can author a genuine
  history-preserving Type-2 migration (a future feature; see Assumptions), HR2 will
  need a POSITIVE recognition signal for a valid construct so it does not
  false-positive against a correctly hand-authored Type-2 migration. No such
  construct exists in any authored migration today (drop-and-rebuild is the only
  mechanism this repo's tooling produces, per the Overview), so there is nothing to
  false-positive against yet, and this positive-recognition signal is explicitly
  OUT OF SCOPE for this feature's implementation. A future plan decides it when
  Type-2 authoring ships, mirroring HR1's genuinely-blocking C3 deferral (spec 087)
  only in shape, not in urgency.
- **FR-008**: HR2 MUST NOT emit a finding under FR-007 for a dimension not yet backed
  by any gold migration file -- absence of a migration is a not-yet-buildable state,
  never a fabricated pass or fail about SQL that does not exist (User Story 2,
  Acceptance Scenario 3). If the `warehouse/migrations/*create_gold_<table>_star.sql`
  glob (FR-004) matches MORE than one file for that table, HR2 MUST treat this as an
  ambiguous-migration state and emit a single fail-closed ERROR finding naming the
  table and the matched filenames, rather than inspecting any of them or guessing
  which is current (Clarifications 2026-07-04, C7) -- this mirrors FR-008's
  no-fabrication stance for the zero-match case.
- **FR-009**: A dimension declared `type_1` MUST produce no HR2 finding regardless of
  whether its migration uses drop-and-rebuild -- drop-and-rebuild is the correct,
  honored mechanism for an overwrite policy (User Story 2, Acceptance Scenario 2).
- **FR-010**: HR2 MUST NOT read or evaluate `gold_star.degenerate_dimensions[]` or
  `gold_star.date_dimension` -- `scd_type` applies only to `gold_star.dimensions[]`
  entries (Edge Cases).
- **FR-011**: HR2 MUST NOT decide, recommend, or default any dimension's `scd_type`
  value on a human's behalf. On a missing or invalid declaration it records the
  Needs-decision finding (FR-005/FR-006) and STOPS; a human resolves it by editing
  `source-map.yaml` (SCOPE GUARD; Principle V, same seam as grain/PII/business
  rollup at Mapping Ready).
- **FR-012**: HR2 MUST NOT execute any SQL, connect to a database, or apply any
  migration. It reads migration files as committed TEXT only (Principle VIII;
  SCOPE GUARD).
- **FR-013**: HR2 MUST NOT emit any numeric confidence / health / maturity /
  completeness score and MUST NOT emit a completeness count or "N of M" tally
  (hard rule #9); output is categorical findings only -- per finding, the dimension,
  the table, and what is wrong (undeclared, invalid value, or declared-but-not-honored).
- **FR-014**: HR2 MUST be wired across every meta-gate surface so `@register` fires
  and the wiring/count locks stay green: the module added to
  `src/retail/rules/__init__.py`, the `EXPECTED_RULE_IDS` membership, the glossary
  rules-table row, `docs/rules/rules-manifest.json`, the severity-posture record, and
  the rule-count claim in the SAME commit (the SF1/AP1/HR1 wiring-meta-gate
  discipline). (Wiring is an implementation-stage concern; recorded here so the plan
  does not miss it.)
- **FR-015**: The rule and the `source-map.yaml` template's `scd_type` example MUST
  stay generic (Principle VII): no C086 / worked-example dimension name, grain key,
  or column name may be inlined as a required value; HR2 resolves generic
  `mappings/<table>/source-map.yaml` paths.
- **FR-016**: All authored artifacts MUST be ASCII, UTF-8 without BOM (use `--` and
  `->`, no glyphs), and MUST use short repo-relative paths (Windows 260-char budget)
  (Principle IX).
- **FR-017**: OPEN (owner ruling required -- Principle V; see Clarifications
  2026-07-04). Whether a dimension's `scd_type` declaration requires its OWN
  named-human approval seam distinct from Mapping Ready's existing `approvals[]`
  entry, or folds into that same existing Mapping Ready sign-off (no new approval
  record introduced), is a governance-shape decision the agent MUST NOT settle
  alone: adding a new approval-bearing seam joins the constitution's
  approval-bearing set, a who-approves ruling. PENDING DEFAULT the owner may ratify:
  FOLDS IN -- `scd_type` is one more field inside the same `source-map.yaml` a human
  already reviews and approves at Mapping Ready (same seam as grain/PK/PII), and no
  second approval record is invented until the owner rules one in. Until the owner
  rules, `scd_type` review happens inside the existing Mapping Ready approval and no
  new `approvals[]` stage key is added anywhere.

### Key Entities *(include if feature involves data)*

- **SCD declaration**: the `gold_star.dimensions[].scd_type` field -- `type_1` or
  `type_2` -- a human-authored Mapping Ready judgment recording whether a dimension's
  attribute changes should overwrite (Type-1) or be historized (Type-2). Read-only to
  HR2; never inferred.
- **Gold migration construct**: the drop-and-rebuild SQL pattern -- a `DROP TABLE IF
  EXISTS <dim_table>` paired, same file, with a `CREATE TABLE <dim_table>` that
  recreates it, in either authored form (CTAS, or explicit column DDL plus
  `INSERT`), not required to be textually adjacent (Clarifications 2026-07-04, C5)
  -- found in a table's `warehouse/migrations/*create_gold_<table>_star.sql`
  file, scoped to one declared-`type_2` dimension's own gold table -- `<dim_table>`
  resolved from that dimension's own `gold_star.dimensions[].name` with an optional
  `<schema>.` prefix stripped before comparison (Clarifications 2026-07-04, C4).
  HR2's detection signal for the MVP (FR-007) is this one construct; a positive
  signal for a valid history-preserving construct is future scope once such
  authoring exists.
- **HR2 Finding**: a `Finding(HR2, severity, message, locator)` for an undeclared
  `scd_type` (Needs-decision), an invalid `scd_type` value, or a `type_2` declaration
  the migration's construct cannot honor. Categorical only; carries no score.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Once a human declares `scd_type` (`type_1` or `type_2`) on every
  `gold_star.dimensions[]` entry of a table, and no `type_2` dimension's gold
  migration contains the drop-and-rebuild construct (or no `type_2` dimension
  exists), HR2 produces ZERO findings for that table.
- **SC-002**: A dimension declared `type_2` whose gold migration builds it by the
  documented drop-and-rebuild construct causes HR2 to emit an ERROR
  (mutation-verified), naming the dimension and the migration file.
- **SC-003**: A dimension with no `scd_type` key causes HR2 to emit exactly one
  Needs-decision finding naming that dimension; adding a valid `scd_type` value
  clears it.
- **SC-004**: A dimension declared `type_1` never causes an HR2 finding regardless
  of its migration's construct (0 false positives against the overwrite default).
- **SC-005**: HR2 never fires on a table with no gold migration yet for the
  build-honors-declaration limb (FR-007/FR-008) -- 0 fabricated findings about SQL
  that does not exist.
- **SC-006**: HR2 adds no numeric score and never writes any `source-map.yaml`,
  migration file, or `scd_type` value (verified by test + review).
- **SC-007**: 0 generic artifacts (the rule logic, the template's `scd_type`
  example) contain a worked-example (C086 / pharmacy) dimension name, grain key, or
  column name.
- **SC-008**: The wiring + rule-count lockstep stays green after HR2 lands (the
  wiring-meta-gate and rule-count-claim tests pass; the registered rule set contains
  `HR2`).

## Assumptions

- **`source-map.yaml` is the single authoritative place `scd_type` is declared.**
  HR2 reads the committed map rather than any live DB or PBIP model; it assumes the
  map is the reviewed output of that table's Mapping Ready gate (Principle IV) and
  does not re-decide any other field on the dimension entry.
- **The human authors the `scd_type` value (BLOCKING, Principle V).** Deciding
  whether a given dimension's history matters enough to preserve is a business
  judgment (like grain or PII) the rule exists to enforce, not one the agent may
  make. The agent may scaffold the field as an empty/placeholder value at the
  owner's instruction; it never fills in `type_1` or `type_2` as a ruling.
- **The MVP detection signal is implementable now; a positive signal is future
  scope (not Principle V).** FR-007's negative signal -- the documented
  drop-and-rebuild construct, scoped to the declared-`type_2` dimension's own gold
  table -- is directly gleaned from the currently-authored `retail-build-warehouse`
  pattern and needs no deferral. A POSITIVE recognition signal for a valid
  history-preserving construct is deferred to whichever future feature adds Type-2
  authoring, since no such construct exists in any migration today (C3).
- **Static-only, live deferred (Principle VIII).** HR2 checks the DECLARED policy
  against the AUTHORED migration text; whether a materialized Type-2 dimension's
  DATA actually preserves history correctly at the row level (an SCD-2 audit: no
  duplicate current rows, `effective_to` gaps, correct `is_current` flags) is a LIVE
  check that belongs to a future `retail validate` extension and is explicitly
  DEFERRED, not in this feature.
- **This feature does not teach `retail-build-warehouse` to author Type-2 SQL.**
  Building a correct SCD-2 upsert/merge migration is a substantial authoring feature
  in its own right; this spec only adds the DECLARATION and the STATIC DETECTION of
  the mismatch. Authoring support is future scope (YAGNI).
- **Reused mechanism.** `@register` / `RuleContext` / `Finding` from
  `src/retail/core.py` + `src/retail/registry.py`, and the fixture + wiring-meta-gate
  discipline from the SF1/AP1/HR1 slices. Nothing new at the mechanism layer; any
  YAML/SQL text parsing is imported LAZILY (kept out of the `retail check`
  static-core chain, mirroring SF1/HR1).
- **Severity posture.** An undeclared `scd_type` (FR-005), an invalid `scd_type`
  value (FR-006), and a proven Type-2-declared-but-drop-and-rebuilt mismatch
  (FR-007) are all ERROR, not WARNING -- consistent with Principle VIII's
  suspect-WARN / proven-ERROR asymmetry: each is either a required-and-absent human
  decision or a proven mechanical contradiction, never a mere suspicion. This is a
  deliberate choice to force the decision rather than let an undeclared dimension
  pass quietly; it accepts an adoption cliff for maps approved before this feature
  shipped (FR-005) as the cost of closing the silent-Type-1-by-omission gap for
  good, rather than reproducing it one layer higher with a WARNING nobody must act
  on.
- **Two-stage ownership.** `scd_type` is DECLARED at Mapping Ready (Stage 2) --
  its absence is a Mapping Ready blocker like an unresolved grain/PII question. HR2's
  build-honors-declaration check (FR-007) fires on the Gold Ready (Stage 4) static
  surface, alongside S6/S7, once a gold migration exists -- it does not duplicate or
  alter S6/S7's own meaning.
- **Sub-key discipline with coordinated in-flight work.** Three other features (090
  freshness, 103 currency/unit, 105 data-contract) are allocated their own,
  different `source-map.yaml` sub-keys; none of their directories exist yet in this
  tree. This feature's schema footprint is exactly
  `gold_star.dimensions[].scd_type` and nothing else, so it cannot collide with
  their allocations regardless of build order.
- **Out of scope for this feature (YAGNI):** live SCD-2 data-correctness auditing;
  authoring Type-2 build SQL; any SCD Type-0/3/4/6 variant (only the two-value
  `type_1`/`type_2` enum is in scope); any migration/backfill mechanism for a
  dimension changing declared type after gold already exists; any new readiness
  stage. Extending scope is a future spec.
- **Ratification pending.** This spec is a DRAFT; it DEFINES the `scd_type` field,
  its permitted values, and the HR2 rule but is not approved or implemented here.
  The reserved rule id is HR2 and the new schema key is
  `gold_star.dimensions[].scd_type` (collision-avoidance allocation); neither is
  renamed or reused.

## Clarifications

<!-- Principle-V carve-out questions are recorded under their own subsection for a
     human ruling; the workflow is forbidden to answer these. Non-Principle-V
     ambiguities resolved with reasonable constitution-safe defaults (Principle VI)
     are recorded under the dated session subsection. -->

### Session 2026-07-04

Non-Principle-V ambiguities resolved against the constitution, the HR1/SF1
precedent (specs 087/086), the committed `source-map.yaml` template and filled
instances (`retail_store_sales`, `demo_sample_orders`), and skill docs
(`retail-build-warehouse/SKILL.md`, `docs/decisions/0002-retail-cleaning-defaults.md`).

- **C1 (schema shape -- FR-001) -- Default adopted.** Q: Does `scd_type` live on the
  dimension entry, or as a separate top-level list/map? A: nested directly under each
  existing `gold_star.dimensions[]` entry, alongside `surrogate_key` /
  `has_unknown_member` / `attributes[]`. Reasoning: the collision-avoidance
  allocation names this exact key; nesting it on the entry (rather than a parallel
  top-level list keyed by dimension name) keeps one dimension's full declaration in
  one place, matching how `surrogate_key` and `has_unknown_member` are already
  authored. Reversible: easy (a template/schema choice, no data). Touches: FR-001.
- **C2 (enum scope -- FR-002) -- Default adopted.** Q: Does the enum need to support
  the fuller SCD taxonomy (Type-0/3/4/6)? A: no -- exactly two values, `type_1` and
  `type_2`, matching the feature description's own framing ("Type-1 overwrite vs
  Type-2 historized"). Reasoning: Principle VI (defaults-then-deviations) plus YAGNI;
  no committed table or worked example needs a hybrid/mini-dimension variant today,
  and a narrower enum is easy to widen later without breaking existing declarations.
  Reversible: easy. Touches: FR-002, Assumptions.
- **C3 (build-honors-declaration detection signal -- FR-007) -- Default adopted for
  the MVP; a NARROWER future-scope item deferred (schema/mechanics gap; not
  Principle-V).** Q: How does HR2 mechanically tell whether a `type_2` dimension's
  migration honors its declaration? A: for THIS feature, the negative signal alone
  is sufficient and implementable today -- detect the one documented
  drop-and-rebuild construct (`retail-build-warehouse/SKILL.md`) scoped to the
  declared-`type_2` dimension's own gold table; its presence IS the fail-closed
  ERROR (FR-007). Unlike HR1's C3 (spec 087), which found NO usable signal at all
  for its check (both candidate heuristics demonstrably failed on committed
  fixtures), this feature's negative signal is directly grepable against the one
  construct this repo's tooling currently authors for every gold dimension -- so
  the MVP does not defer. What DOES remain future scope (not MVP-blocking): once a
  builder can author a genuine history-preserving Type-2 migration, HR2 will need a
  POSITIVE recognition signal for that valid construct to avoid a false positive;
  no such construct exists today, so that positive signal is out of scope for this
  feature and left to the future feature that adds Type-2 authoring. Touches:
  FR-007, Key Entities ("Gold migration construct"), Assumptions.
- **C4 (name-to-physical-table resolution for the FR-007 scope match -- FR-007) --
  Default adopted.** Q: FR-007's drop-and-rebuild grep must be SCOPED to one
  declared-`type_2` dimension's own gold table (`<dim_table>`), never the whole
  migration file -- otherwise a `type_1` dimension's ordinary, correct
  drop-and-rebuild in the same file would false-positive against an unrelated
  `type_2` dimension. But `gold_star.dimensions[].name` is the only machine-readable
  handle a dimension entry carries, and the two committed instances disagree on its
  shape: `mappings/retail_store_sales/source-map.yaml` fully schema-qualifies it
  (`name: "gold.dim_customer_rss"`, matching `DROP TABLE IF EXISTS
  gold.dim_customer_rss` / `CREATE TABLE gold.dim_customer_rss` in
  `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` verbatim),
  while `mappings/demo_sample_orders/source-map.yaml` and the canonical
  `templates/source-map.yaml` placeholder both leave it bare (`name: "dim_product"`,
  `name: "dim_<entity_a>"`, no schema prefix) -- and the authored migration SQL
  always schema-qualifies the physical `CREATE`/`DROP` token with `gold.` regardless
  of how the map spells `name`. A: HR2 resolves `<dim_table>` by stripping an
  optional leading `<schema>.` prefix from BOTH the declared `name` and the
  `DROP`/`CREATE` token, then comparing the remaining bare identifier -- this is a
  reliable normalization confirmed against the one committed instance that has a
  gold migration to check (`retail_store_sales`, exact match once the shared
  `gold.` prefix is disregarded), and it degrades safely for `demo_sample_orders`
  (bare `name`, no gold migration yet -- FR-008's not-yet-buildable path applies,
  not a false comparison). Unlike HR1's C3 (spec 087), which found NO reliable
  signal at all in the committed tree (both candidate heuristics failed outright),
  this feature's normalization holds on every committed data point available, so a
  default is adopted rather than a defer-to-plan. Reversible: easy (a parsing rule,
  no data or schema change; a future multi-schema-per-star case, if it ever arises,
  would refine the strip rule without touching `scd_type` itself). Touches: FR-007,
  Key Entities ("Gold migration construct").
- **C5 (the actual shape of the GOLD drop-and-rebuild construct -- FR-007, Overview,
  US2, Key Entities) -- Default adopted (correction).** Q: FR-007/US2, as first
  drafted, named the target construct as `DROP TABLE IF EXISTS <dim_table>`
  IMMEDIATELY FOLLOWED BY `CREATE TABLE <dim_table> AS SELECT ...` (CTAS,
  adjacent). Does the committed gold-migration tooling actually author that shape? A:
  NO -- checked directly against both authoritative sources and they agree with each
  other but disagree with the as-drafted FR-007 text. `.claude/skills/
  retail-build-warehouse/SKILL.md` documents `CREATE TABLE ... AS SELECT` (CTAS) ONLY
  for SILVER (its Silver section, "Wrap:" line); its separate Gold section
  ("Gold: the Kimball star") instead documents explicit column DDL
  (`CREATE TABLE <dim> (...)`) followed by `INSERT` statements, one dim at a time,
  with "drop fact before dims (FK order), recreate all in one txn" -- i.e. every
  `DROP TABLE IF EXISTS` batched up front, NOT adjacent to its matching `CREATE`.
  The one committed gold migration, `warehouse/migrations/
  0004_create_gold_retail_store_sales_star.sql`, matches the SKILL.md Gold
  description exactly: six `DROP TABLE IF EXISTS` batched at lines 22-27, then each
  dim recreated far below via `CREATE TABLE gold.dim_customer_rss (customer_sk INT
  ..., customer_id TEXT);` plus `INSERT INTO ...` -- zero occurrences of
  `CREATE TABLE ... AS SELECT` anywhere in the file. A rule implemented literally to
  the as-drafted FR-007 wording would match NOTHING in this repo's actual gold
  output, so a `type_2` dimension genuinely built by drop-and-rebuild would pass HR2
  clean -- a fail-OPEN outcome that violates Principle I and defeats the feature's
  entire MVP purpose (User Story 2). This is a mechanics/drafting correction (what
  construct exists in the tooling), not a Principle-V ruling. Corrected default: HR2
  detects a `DROP TABLE IF EXISTS <dim_table>` for that dimension's table PLUS a
  same-file `CREATE TABLE <dim_table>` that recreates it, in EITHER authored form
  (CTAS or DDL-plus-`INSERT`), WITHOUT requiring textual adjacency between the two
  statements. Both SC-002's mutation-verified fixture and the negative-construct
  fixture in User Story 2's Independent Test MUST use the DDL-plus-`INSERT`,
  batched-drop shape (the form the repo's tooling actually authors for gold), with a
  CTAS-form fixture covered as an additional case, not the primary one. Reversible:
  easy (a text-match rule, no data or schema change). Touches: FR-007, Overview,
  User Story 2 (description, Independent Test, Acceptance Scenario 1), Key Entities
  ("Gold migration construct").
- **C6 (empty/placeholder `scd_type` value routes to Needs-decision, not
  invalid-value -- FR-005/FR-006) -- Default adopted.** Q: The Assumptions permit the
  agent to "scaffold the field as an empty/placeholder value" while never ruling on
  `type_1`/`type_2` itself. FR-005 (as first drafted) covered only "no `scd_type` key
  at all" and FR-006 covered "present but not one of the two permitted values" -- so a
  scaffolded placeholder (`scd_type: ""`, `scd_type: null`, or `scd_type: "TBD"`) fell
  through the crack: it is technically present (FR-006's condition) but semantically
  an undeclared decision (FR-005's condition), and the two findings carry different
  messages (Needs-decision vs invalid-value-named). Both are already fail-closed
  ERROR, so the choice does not change enforcement posture; it changes only which
  finding message a reviewer sees. A: an empty string, `null`, or a case-insensitive
  `"tbd"` value routes to FR-005's Needs-decision finding (same message and remedy as
  a wholly-missing key: "declare `type_1` or `type_2`"), not FR-006's
  invalid-value finding -- because a placeholder is semantically an undeclared
  decision, and grouping it with the missing-key case gives a reviewer the one
  correct next action instead of a confusing "invalid value: ''" message. FR-006
  remains for a value that is present, non-empty, and not a recognized placeholder
  (e.g. a typo like `"type1"` or an out-of-scope taxonomy value like `"type_3"`).
  Reversible: easy (a routing rule inside HR2's own value-classification, no schema or
  data change). Touches: FR-005, FR-006.
- **C7 (mapping-directory-to-migration-file resolution and multi-match handling for
  the FR-004/FR-007 glob -- FR-004, FR-008) -- Default adopted.** Q: FR-004/FR-007
  name the migration file pattern as
  `warehouse/migrations/*create_gold_<table>_star.sql` but never state, the way C4
  states the dimension-name-to-physical-table rule, what `<table>` resolves FROM, nor
  what HR2 does if the glob matches more than one file. A, resolution rule: `<table>`
  is that map's own mapping-directory name -- the source table identifier from
  `mappings/<table>/source-map.yaml` -- and the leading `*` in the glob absorbs the
  migration's arbitrary numeric filename prefix; confirmed against the one committed
  instance with both a map and a gold migration
  (`mappings/retail_store_sales/source-map.yaml` pairs with
  `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`, prefix `0004_`
  absorbed by the glob, `<table>` = `retail_store_sales` matching the mapping
  directory exactly). A, multi-match rule: if the glob matches more than one file for
  a table, HR2 emits a single fail-closed ERROR naming the table and every matched
  filename, rather than inspecting any one of them or guessing which is current
  (FR-008) -- an ambiguous migration set is itself a fail-closed condition, not a
  silent pick-the-first. Reasoning: both are mechanical resolution rules (Principle
  VI), not business judgments -- no committed table has more than one matching
  migration today, so the multi-match default has nothing to contradict it, and it is
  easy to widen later (e.g. "most recent by filename ordinal") without breaking any
  existing finding. Reversible: easy (a file-resolution rule, no schema or data
  change). Touches: FR-004, FR-008.

### Principle-V carve-out (OPEN -- owner ruling required; the workflow is forbidden to answer)

- **Q-APPROVAL-SEAM (FR-017) -- OPEN owner ruling.** Q: Does declaring a dimension's
  `scd_type` require its OWN named-human approval seam distinct from Mapping Ready's
  existing `approvals[]` entry, or does it fold into that same existing sign-off (no
  new approval record)? This is a who-approves / governance-shape decision
  (Principle V): adding a new approval-bearing seam joins the constitution's
  approval-bearing set, which the agent MUST NOT settle alone. RECORDED PENDING
  DEFAULT the owner may ratify: FOLDS IN (one more field inside the same
  `source-map.yaml` a human already reviews and approves at Mapping Ready; no second
  approval record is invented until an owner rules one in). Until the owner rules,
  `scd_type` review happens inside the existing Mapping Ready approval and HR2 adds
  no new `approvals[]` stage key anywhere. Touches: FR-017.
