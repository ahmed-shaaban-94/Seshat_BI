# Feature Specification: Cross-Star Conformed-Dimension Readiness Gate

**Feature Branch**: `087-conformed-dimension-readiness`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Cross-star conformed-dimension readiness gate (gap #1). A model-level readiness tier above the per-table spine: when more than one fact exists, a reviewable conformance map plus a static `retail check` rule assert that the shared dimensions (dim_product / dim_store / dim_date, illustratively) match on grain + key + type across stars. Enforces Principle III (gold IS a Kimball star with CONFORMED dims), which today has no cross-table gate."

## Overview

Constitution Principle III says `gold` MUST be a Kimball star -- "fact + conformed
dimensions". "Conformed" is load-bearing: when a warehouse holds more than one fact
table (more than one star), a dimension shared across them (a `dim_product`, a
`dim_store`, a `dim_date`) MUST be the SAME dimension in every star -- same grain,
same natural key, same attribute types -- so a measure from one star and a measure
from another can be sliced by that one shared dimension and reconcile. A drifted
"conformed" dimension (two stars whose `dim_product` disagree on grain, on the natural
key column, or on an attribute's silver type) silently produces wrong cross-star
answers in Power BI, and nothing catches it today.

The existing gates are all PER-TABLE. Gold Ready (Stage 4) live-validates ONE star:
PK/grain uniqueness, date coverage, zero orphan FKs, penny-exact silver<->gold
reconciliation. But conformance is a CROSS-STAR property no single table's Gold Ready
can see: whether two independently-built stars agree on their shared dimensions is
invisible to each table's own gate. So Principle III's "conformed" clause -- the one
word that makes the collection of stars a single coherent model rather than a pile of
disconnected tables -- has, today, NO enforced gate.

This feature adds that missing gate as a MODEL-LEVEL readiness tier that sits ABOVE the
per-table Gold Ready spine and is ORTHOGONAL to the seven-stage per-table pipeline (it
is NOT an eighth stage and NOT a key in any `mappings/<table>/readiness-status.yaml`;
the constitution's spine adds no new stage). It has two parts, mirroring the shipped
SF1 fork-detector pattern (spec 086):

1. A NEW human-authored declaration file, `docs/quality/conformed-dimension-map.yaml`,
   in which a named human declares which dimension names are MEANT to be one conformed
   dimension across which stars (and, where appropriate, which same-named dims are
   intentionally NOT conformed). Deciding that two stars' `dim_product` are the same
   business dimension is a Principle-V modelling judgment; a human authors it, the rule
   only READS it.

2. A NEW static `retail check` rule, reserved id **HR1**, that reads each star's shape
   from its per-table `source-map.yaml` (`gold_star.dimensions[]` + the `columns[]`
   silver types), and for every declared-conformed dimension verifies it matches on
   grain + key + type across the stars that carry it. HR1 fails CLOSED (ERROR,
   Principle I) on a declared-conformed dimension that diverges, and on an UNDECLARED
   shared dimension (the same dim name in 2+ stars with no map entry -- coincidence
   cannot be told from intent, so a human declaration is demanded). It surfaces a
   status + the diverging dimension + WHAT diverged -- never a numeric conformance
   score, never a "% conformed" or "N of M" tally (hard rule #9).

HR1 is static-only (Principle VIII): it reads committed text (the per-table
`source-map.yaml` files and the map), opens no database, reads no live Power BI/PBIP
surface. It never auto-merges two dimensions, never authors or rewrites the map, and
never self-grants the model-level pass (SCOPE GUARD; Principle V).

## Boundary against neighbouring shipped work (read first)

This feature is a genuine NEW gate for a cross-star property nothing checks today, not
a restatement of an existing gate. Three shipped neighbours must stay distinct:

- **Gold Ready (Stage 4)** (`docs/readiness/gold-ready.md`, spec 006 warehouse-builder +
  spec 004 retail-validate) validates ONE star: static S6/S7 (unknown member, contiguous
  date dim) plus live RC2/RC15/RC16 (PK uniqueness, date coverage, orphan FKs,
  penny-exact reconciliation) over that table's own gold. It is PER-TABLE and cannot see
  another star. This feature validates that shared dimensions agree ACROSS two or more
  stars -- a property that only exists when more than one Gold-Ready star exists. HR1 does
  not re-run any Gold Ready check, does not touch `retail validate`, and adds no per-table
  gate; it composes ABOVE Gold Ready.
- **SF1 shared-checklist fork detector** (`src/retail/rules/rule_sf1.py`, spec 086) is the
  DESIGN PRECEDENT this feature reuses -- a human-authored `docs/quality/*.yaml` manifest
  declaring shared-vs-distinct intent, a static rule that only READS the manifest and fails
  closed on an UNDECLARED collision. SF1 reconciles same-basename CHECKLIST files under
  `skills/**/checklists/`; HR1 reconciles same-named GOLD DIMENSIONS across `source-map.yaml`
  stars. Different subject, different manifest (`shared-spine.yaml` vs
  `conformed-dimension-map.yaml`), different rule id (SF1 vs HR1). HR1 does NOT edit SF1,
  does NOT read `shared-spine.yaml`, and reuses only SF1's declaration-then-enforce shape.
- **The source-mapping gate / `source-map.yaml`** (Principle IV, spec 001; templates
  `templates/source-map.yaml`) is the PER-TABLE artifact HR1 READS -- each table's
  `gold_star.dimensions[]` (name, `surrogate_key`, `has_unknown_member`, `attributes[]`)
  and its `columns[].silver_type` / `gold_placement`. HR1 adds NO new key to
  `source-map.yaml` (that would collide with the source-mapping gate's owned schema); the
  cross-star declaration lives in the NEW, separate `conformed-dimension-map.yaml`. HR1
  never rewrites a `source-map.yaml` and never re-decides a table's own grain/PK/placement
  (those are that table's Mapping Ready judgments, already reviewed).

This feature adds a NEW `retail check` rule (id HR1) -- unlike the F024 Product Modules
(F027/F028) which add no gate. It follows the SF1/AP1 rule-adding shape: one registered
static rule, its wiring across the meta-gate surfaces, and its fixtures. It adds NO new
per-table readiness stage; the model-level tier is orthogonal to the seven-stage spine
and is not written into any `mappings/<table>/readiness-status.yaml`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fail closed when a declared-conformed dimension diverges across stars (Priority: P1)

As the `retail check` gate, when the human-authored `conformed-dimension-map.yaml`
declares that a dimension (illustratively `dim_product`) is conformed across two or more
stars, I read each star's `gold_star.dimensions[]` and `columns[].silver_type` from its
`source-map.yaml` and verify the shared dimension matches on grain (its natural-key
attribute), on key (its surrogate key), and on type (the silver type of each shared
attribute) across those stars -- and I emit a fail-closed ERROR if any star disagrees, so
a drifted "conformed" dimension can never pass unnoticed.

**Why this priority**: This is the whole point of the feature and the MVP -- it is the
enforcement that gives Principle III's "conformed" clause a gate. A cross-star mismatch is
a PROVEN modelling defect (two stars claim the same dimension but disagree on its shape),
so it blocks. Without this, the feature delivers nothing.

**Independent Test**: With a map declaring `dim_product` conformed across two fixture
stars whose `source-map.yaml` files disagree on the dimension's natural-key column (or its
surrogate key, or a shared attribute's silver type), the rule emits exactly one ERROR that
names the dimension, the two stars, and WHAT diverged (which of grain / key / type, and the
disagreeing values). With the two stars made to agree, the rule emits no Finding.

**Acceptance Scenarios**:

1. **Given** the map declares `dim_product` conformed across stars A and B, and A's
   `source-map.yaml` gives its `dim_product` surrogate key `product_sk` while B's gives
   `prod_key`, **When** the rule runs, **Then** it emits one ERROR naming `dim_product`,
   both stars, and the divergent surrogate-key values.
2. **Given** the same declaration, and A's `dim_product` natural-key attribute is
   `product_id` (type `text`) while B's shared attribute is typed `integer`, **When** the
   rule runs, **Then** it emits one ERROR naming the attribute and the two silver types.
3. **Given** a declared-conformed dimension whose stars agree on grain, key, and every
   shared attribute type, **When** the rule runs, **Then** it emits no Finding for that
   dimension.

---

### User Story 2 - Fail closed on an UNDECLARED shared dimension (Priority: P1)

As the gate, when the same dimension NAME appears in two or more stars' `source-map.yaml`
files but is NOT declared in `conformed-dimension-map.yaml` (neither as conformed nor as
intentionally-distinct), I emit a fail-closed ERROR -- because a shared name across stars
could be an intended conformed dimension OR a coincidental name clash, and only a named
human may rule which. The rule cannot tell intent from coincidence, so it demands the
human declaration (the SF1 undeclared-collision discipline).

**Why this priority**: Without this, a new star could introduce a second `dim_store` that
silently diverges from the first and slip through simply by never being declared. Forcing
every cross-star name collision to be a DECLARED decision is what keeps the map honest as
the model grows; it is co-equal with US1 as the integrity floor.

**Independent Test**: Provide two fixture stars that both carry a `dim_store` with no
`dim_store` entry in the map; assert one ERROR naming `dim_store` and both stars. Add a map
entry (conformed or distinct) and assert the undeclared ERROR clears.

**Acceptance Scenarios**:

1. **Given** `dim_store` present in 2+ stars with no map entry, **When** the rule runs,
   **Then** one ERROR names `dim_store` and every star carrying it, and instructs the human
   to declare it conformed or distinct.
2. **Given** a dimension name that appears in exactly ONE star, **When** the rule runs,
   **Then** no Finding (a single-star dimension is not a cross-star collision).
3. **Given** the map declares that same-named dimension `distinct` (intentionally not one
   conformed dimension), **When** the rule runs, **Then** no ERROR (a distinct declaration
   is a legitimate human ruling; the copies may differ).

---

### User Story 3 - Do not fire spuriously below the multi-fact trigger (Priority: P2)

As the gate, when the model has zero or exactly one star (one or no fact table), I treat
HR1 as a no-op and emit no Finding, and when the map is empty on a single-star model I do
not demand declarations -- because conformance is only meaningful across TWO or more stars.
The tier is a MODEL-LEVEL gate that engages only once the multi-fact condition (more than
one fact) that Principle III's "conformed dimensions" clause presupposes is actually met.

**Why this priority**: A gate that fired on a one-table repo would block every early-stage
model before a second star ever exists and would contradict the feature's own trigger
("when more than one fact exists"). Correct non-firing is required for the rule to be
adoptable, but a single working multi-star case (US1/US2) is already the viable slice, so
this is P2.

**Independent Test**: With a fixture repo containing zero stars, then one star, assert the
rule emits no Finding in either case; with a second star added that shares a dimension name,
assert US2's undeclared ERROR now fires (the trigger has engaged).

**Acceptance Scenarios**:

1. **Given** a repo with no `source-map.yaml` gold star at all, **When** the rule runs,
   **Then** no Finding.
2. **Given** exactly one star, **When** the rule runs, **Then** no Finding regardless of the
   map's contents.
3. **Given** a second star is added that carries a dimension name the first star also
   carries, **When** the rule runs, **Then** the cross-star checks (US1/US2) engage.

---

### Edge Cases

- **A declared-conformed dimension that no longer appears in 2+ stars** (a star was removed
  or its dimension renamed, leaving the map entry naming a dimension now present in one or
  zero stars): the map entry is STALE -> WARNING (surface it so the map cannot rot silently),
  never a silent pass and never an ERROR that blocks unrelated work.
- **A `distinct` declaration whose stars have in fact become identical in shape** (grain +
  key + type all now match): the distinct declaration is arguably moot -> WARNING (surface for
  review: the human may want to promote it to conformed), consistent with SF1's moot-distinct
  posture. It does NOT auto-promote or auto-merge.
- **The `conformed-dimension-map.yaml` is missing or unparseable** while 2+ stars exist: ERROR
  (fail-closed -- with more than one star the gate has a contract it must check and cannot
  verify without the map). If zero/one star exists, a missing map is not an error (US3).
- **A malformed map entry** (a declared value that is neither `conformed` nor `distinct`, or a
  named star whose `source-map.yaml` cannot be found/parsed): ERROR naming the offending entry
  -- an unrecognized declaration MUST NOT be treated as a valid ruling (the SF1 bad-value
  posture).
- **A degenerate dimension** (a transaction id carried ON the fact per RC14, not a shared
  lookup dimension): degenerate dims are per-star by definition and are NOT cross-star
  conformable; the rule considers only entries under `gold_star.dimensions[]`, not
  `gold_star.degenerate_dimensions[]`, so a degenerate id shared by name across stars is out
  of HR1's scope. RESOLVED (Clarifications 2026-07-04, Default adopted): degenerate dimensions
  are EXCLUDED from conformance -- HR1's conformance set is the star's LOOKUP dimensions
  (entries under `gold_star.dimensions[]` PLUS a `gold_star.date_dimension` block where present,
  per FR-004 and the `dim_date` note below), and it ignores `gold_star.degenerate_dimensions[]`.
  This confirms the existing YAGNI scope (Assumptions "Out of scope: conformance of degenerate
  dims"); widening HR1 to declare same-named degenerate dims is a future spec.
- **`dim_date`** is typically the most-shared conformed dimension; because RC15 already forces
  a contiguous `generate_series` date dim per star, HR1's date-dim conformance reduces to grain
  (the date grain / key column) + type agreement across stars, not a re-check of RC15's
  contiguity (that is Gold Ready's job per star).
- **A `conformed`/`distinct` entry names a star whose `source-map.yaml` parses fine but does not
  actually carry that dimension name** (distinct from the malformed case above, where the star
  file itself cannot be found or parsed): RESOLVED (Clarifications 2026-07-04, Default adopted)
  -- this is STALE -> WARNING (the same posture as a map entry naming fewer than 2 surviving
  stars), not a malformed-entry ERROR; the named star is a valid, readable star, it simply no
  longer (or does not yet) carry the declared dimension, which is a map-drift condition, not a
  broken reference. Touches FR-009/FR-010.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST add a NEW model-level tier that is ORTHOGONAL to the
  seven-stage per-table readiness spine -- NOT an eighth stage, NOT a key in any
  `mappings/<table>/readiness-status.yaml`. The constitution's spine adds no new stage
  (Principle III readiness-spine section); this tier composes above per-table Gold Ready.
- **FR-002**: The feature MUST introduce a NEW human-authored declaration file at
  `docs/quality/conformed-dimension-map.yaml`, separate from every `source-map.yaml`, in
  which a named human declares, per shared dimension name, whether it is `conformed` across a
  listed set of stars or `distinct` (intentionally not one dimension). The rule NEVER writes
  or generates this file (Principle V); the human authors its CONTENT. RESOLVED
  (Clarifications 2026-07-04, Default adopted): the file mirrors the SF1 `shared-spine.yaml`
  shape -- a single top-level `dimensions:` mapping whose keys are gold dimension names and
  whose value per entry carries `status: conformed|distinct` plus a `stars: [<table_id>, ...]`
  list of the tables the ruling covers. This reuses SF1's declaration-then-enforce structure
  (top-level mapping + enum value + fail-closed on an unrecognized value) and adds no
  domain-specific key; the exact field names are confirmable at plan/template time.
- **FR-003**: The feature MUST add exactly ONE `@register`ed static `retail check` rule with
  reserved id **HR1**, reading only committed files (the per-table `source-map.yaml` set and
  `docs/quality/conformed-dimension-map.yaml`); it MUST NOT connect to a database, read a live
  Power BI/PBIP surface, or invoke any deferred execution adapter (F016) (Principle VIII).
- **FR-004**: HR1 MUST discover each star's lookup dimensions by reading, per table, that
  table's `source-map.yaml` `gold_star.dimensions[]` (each dimension's `name`, `surrogate_key`,
  `has_unknown_member`, `attributes[]`) PLUS the `gold_star.date_dimension` block where a table
  records the date dim separately (the committed instances use BOTH forms -- a `dim_date` entry
  inside `dimensions[]`, or a standalone `date_dimension:` block; HR1 MUST recognize a date dim
  in either form), and the corresponding `columns[].silver_type` / `gold_placement` -- the
  already-committed source-mapping-gate artifact. HR1 MUST NOT include
  `gold_star.degenerate_dimensions[]` (C1) and MUST NOT add any new key to `source-map.yaml`.
- **FR-005**: For a dimension the map declares `conformed` across 2+ stars, HR1 MUST verify it
  matches across those stars on: grain (its natural-key attribute), key (its surrogate key),
  and type (the silver type of each shared attribute); a divergence on any of these MUST be a
  fail-closed ERROR (Principle I) that names the dimension, the disagreeing stars, and WHAT
  diverged (which of grain / key / type, and the conflicting values) (US1).
  DEFERRED TO PLAN (Clarifications 2026-07-04, schema/mechanics gap -- natural-key
  identification): the grain limb of this requirement is NOT mechanically implementable as
  written. The current `gold_star.dimensions[]` schema carries NO machine-readable natural-key
  marker, and no reliable signal can be inferred from the committed instances: first-position
  fails (`demo_sample_orders` `dim_product` lists `product_name` first, a descriptive
  attribute, not a key), and an `_id`-suffix heuristic fails (`retail_store_sales`
  `dim_product` natural key is `item`, no suffix). A fail-closed ERROR rule (Principle I) MUST
  NOT rest on an unenforced authoring convention. PLAN MUST specify the natural-key SIGNAL
  before the grain check is implemented; leading candidate: an explicit natural-key marker
  owned by the source-mapping-gate schema that HR1 READS (never writes -- FR-004). This is a
  schema/mechanics question, not a Principle-V grain ruling -- HR1 re-decides no table's grain;
  it only reads the already-recorded shape. The key limb (surrogate_key) and type limb (below)
  are unaffected.
  RESOLVED (Clarifications 2026-07-04, Default adopted -- shared-attribute set): the "shared
  attributes" whose silver types HR1 compares are the INTERSECTION of the attribute-NAME sets
  across the conformed stars (Kimball conformed-subset). A type disagreement on an
  intersection attribute is an ERROR; a differing attribute SET alone (one star carries an
  extra attribute the other lacks) is NOT itself an ERROR under this feature.
- **FR-006**: When the SAME dimension name appears under `gold_star.dimensions[]` in 2+ stars
  and is NOT declared in the map (neither `conformed` nor `distinct`), HR1 MUST emit a
  fail-closed ERROR naming the dimension and every star carrying it, instructing a human to
  declare it -- because intent cannot be inferred from a shared name (US2).
- **FR-007**: HR1 MUST engage only when MORE THAN ONE star exists. With zero or one star it
  MUST be a no-op (no Finding), and it MUST NOT demand any declaration on a single-star model
  (US3).
- **FR-008**: A dimension name declared `distinct` MUST be allowed to differ in shape across
  stars with no ERROR (an intentional human ruling that two same-named dims are NOT one
  conformed dimension) (US2/US3).
- **FR-009**: A stale map entry (a declared dimension no longer present in 2+ stars) MUST be a
  WARNING, and a `distinct` entry whose stars have become identical in shape MUST be a WARNING
  (moot declaration) -- surfaced, never a silent pass, never a blocking ERROR. RESOLVED
  (Clarifications 2026-07-04, Default adopted): a listed star that PARSES but does not carry the
  declared dimension name is also this STALE/WARNING case (map drift), distinct from FR-010's
  malformed case (the star file itself missing/unparseable).
- **FR-010**: A missing or unparseable `conformed-dimension-map.yaml` MUST be a fail-closed
  ERROR WHEN 2+ stars exist (no contract, no pass); with zero or one star it MUST NOT error
  (consistent with FR-007). A malformed entry -- a declared value that is neither `conformed`
  nor `distinct`, or a named star whose `source-map.yaml` is missing/unparseable -- MUST be an
  ERROR naming the offending entry; an unrecognized declaration MUST NOT count as a valid
  ruling. A named star that parses fine but simply lacks the declared dimension is NOT this
  malformed case (see FR-009).
- **FR-011**: HR1 MUST NOT auto-merge, rewrite, or reconcile any dimension or any
  `source-map.yaml`; MUST NOT author or edit `conformed-dimension-map.yaml`; and MUST NOT
  self-grant, record, or move the model-level pass. On a breach it STOPS at the finding and a
  human must fix the divergence or declare the dims distinct (SCOPE GUARD; Principle V).
- **FR-012**: HR1 MUST NOT emit any numeric confidence / health / maturity / conformance score
  and MUST NOT emit a completeness count or "N of M" / "% conformed" tally (hard rule #9);
  output is categorical Findings only -- a status plus, per finding, the diverging dimension
  and what diverged.
- **FR-013**: The rule and the `conformed-dimension-map.yaml` template MUST stay generic
  (Principle VII): `dim_product` / `dim_store` / `dim_date` are ILLUSTRATIVE only and MUST NOT
  be baked into the rule logic or the template as required names; no C086 / worked-example dim
  names, grain keys, or column names may be inlined. HR1 resolves generic
  `mappings/<table>/source-map.yaml` paths.
- **FR-014**: The rule MUST be wired across every meta-gate surface so `@register` fires and
  the wiring/count locks stay green: the module added to `src/retail/rules/__init__.py`, the
  `EXPECTED_RULE_IDS` membership, the glossary rules-table row, `docs/rules/rules-manifest.json`,
  the severity-posture record, and the rule-count claim in the SAME commit (the SF1/AP1
  wiring-meta-gate discipline). (Wiring is an implementation-stage concern; recorded here so the
  plan does not miss it.)
- **FR-015**: All authored artifacts MUST be ASCII, UTF-8 without BOM (use `--` and `->`, no
  glyphs), and MUST use short repo-relative paths (Windows 260-char budget) (Principle IX).
- **FR-016**: OPEN (owner ruling required -- Principle V; see Clarifications 2026-07-04).
  Whether the model-level conformed tier requires a NAMED-HUMAN approval seam on top of the
  mechanical HR1 gate, or is purely mechanical like Silver Ready and Gold Ready (a clean HR1
  run IS the sign-off, no `approvals[]` entry), is a governance-shape decision the agent MUST
  NOT settle alone: adding a new named-human-approval tier joins the constitution's
  approval-bearing set and is a Principle-V who-approves ruling. PENDING DEFAULT the owner may
  ratify: MECHANICAL -- HR1 is a static objective check like S6/S7, the scope guard already
  forbids the agent self-granting the pass, and no new approval seam is invented until the
  owner rules one in. Until the owner rules, HR1 emits Findings only and records no
  model-level pass anywhere (consistent with FR-011 and Assumptions "where the model-level
  pass is recorded is a plan-time decision").

### Key Entities *(include if feature involves data)*

- **Star**: one fact + its dimensions as recorded in a single table's
  `mappings/<table>/source-map.yaml` `gold_star` block (`fact`, `dimensions[]`). Only tables
  with a `gold_star.fact` are stars; the model has more than one star when 2+ such tables
  exist.
- **GoldDimension**: a `gold_star.dimensions[]` entry -- `name`, `surrogate_key`,
  `has_unknown_member`, `attributes[]` -- plus each attribute's `silver_type` from the same
  file's `columns[]`. The unit HR1 compares across stars.
- **ConformedDeclaration**: a `docs/quality/conformed-dimension-map.yaml` entry mapping a
  dimension name to `conformed` (across a listed set of stars) or `distinct` -- HUMAN-AUTHORED;
  the contract HR1 enforces; it holds the Principle-V modelling judgment (which same-named dims
  are one dimension).
- **ConformanceFinding**: a `Finding(HR1, severity, message, locator)` for a declared-conformed
  divergence (ERROR), an undeclared cross-star collision (ERROR), a missing/malformed map
  (ERROR), or a stale/moot declaration (WARNING). Categorical only; carries no score.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Once a human authors `docs/quality/conformed-dimension-map.yaml` covering every
  dimension name shared across 2+ stars (each ruled `conformed` or `distinct`), and the
  conformed dims genuinely agree, HR1 produces ZERO ERROR Findings on the tree.
- **SC-002**: Introducing a second star whose shared dimension diverges from the first on
  grain, key, or a shared attribute's type causes HR1 to ERROR (mutation-verified), naming the
  dimension and what diverged.
- **SC-003**: Adding a same-named dimension in a second star WITHOUT a map declaration causes
  HR1 to ERROR; declaring it `distinct` clears the ERROR and lets the shapes differ.
- **SC-004**: On a model with zero or one star, HR1 emits no Finding regardless of the map's
  contents (no spurious firing below the multi-fact trigger).
- **SC-005**: HR1 adds no numeric score and never writes any `source-map.yaml`, the
  `conformed-dimension-map.yaml`, or any dimension (verified by test + review).
- **SC-006**: 0 generic artifacts (the rule logic, the map template) contain a
  worked-example (C086 / pharmacy) dim name, grain key, or column name; `dim_product` /
  `dim_store` / `dim_date` appear only as illustrations.
- **SC-007**: The wiring + rule-count lockstep stays green after HR1 lands (the wiring-meta-gate
  and rule-count-claim tests pass; the registered rule set contains `HR1`).

## Assumptions

- **`source-map.yaml` is the authoritative per-star shape source.** HR1 reads each table's
  committed `gold_star.dimensions[]` and `columns[].silver_type` rather than a live DB or PBIP
  model; it assumes those maps are the reviewed output of each table's Mapping Ready gate
  (Principle IV) and does not re-decide any table's own grain/PK/placement.
- **The human authors the conformance map (BLOCKING, Principle V).**
  `docs/quality/conformed-dimension-map.yaml` and every conformed-vs-distinct ruling are HUMAN
  work -- deciding two stars' same-named dims are one business dimension is a modelling
  judgment the rule exists to enforce, not one the agent may make. The agent supplies the map
  SHAPE / an empty scaffold only at the owner's instruction; it never rules an existing
  collision.
- **The tier is model-level and orthogonal to the seven-stage spine** -- it is not written
  into any `mappings/<table>/readiness-status.yaml` and adds no per-table stage. Where the
  model-level pass is recorded (if anywhere) is a plan-time decision; the spec does not invent
  a new readiness-status shape.
- **Static-only, live deferred (Principle VIII).** HR1 checks the committed maps' declared
  shapes; whether the MATERIALIZED dimensions actually match across stars at the data level is
  a LIVE cross-star reconciliation that belongs to the `retail validate` surface and is
  DEFERRED, not in this feature. HR1 proves the DECLARED shapes agree; a live check would prove
  the DATA agrees.
- **Reused mechanism.** `@register` / `RuleContext` / `Finding` from `src/retail/core.py` +
  `src/retail/registry.py`, the human-authored-manifest + read-only-rule pattern from SF1
  (`src/retail/rules/rule_sf1.py`), and the fixture + wiring-meta-gate discipline from the
  SF1/AP1 slices. Nothing new at the mechanism layer; `yaml` is imported LAZILY (kept out of
  the `retail check` static-core chain, mirroring SF1).
- **Severity posture.** Divergence of a declared-conformed dim, an undeclared cross-star
  collision, and a missing/malformed map (with 2+ stars) are ERROR (proven breaches of a human
  declaration -- unlike the RC "override-when" defaults, so ERROR not WARN is consistent with
  Principle VIII's suspect-WARN / proven-ERROR asymmetry); stale and moot-distinct entries are
  WARNING.
- **Out of scope for this feature (YAGNI):** live cross-star data reconciliation; conformance of
  degenerate dims; any auto-merge / auto-fix of a divergence; a numeric conformance score; and
  any new per-table readiness stage. Extending scope is a future spec.
- **Ratification pending.** This spec is a DRAFT; it DEFINES the tier, the map shape, and the
  HR1 rule but is not approved or implemented here. The reserved rule id is HR1 and the new
  artifact is `docs/quality/conformed-dimension-map.yaml` (collision-avoidance allocation);
  neither is renamed or reused.

## Clarifications

<!-- Principle-V carve-out questions are recorded under their own subsection for a human
     ruling; the workflow is forbidden to answer these. Non-Principle-V ambiguities resolved
     with reasonable constitution-safe defaults (Principle VI) are recorded under the dated
     session subsection. -->

### Session 2026-07-04

Non-Principle-V ambiguities resolved against the constitution, the SF1 precedent (spec 086),
and the committed `source-map.yaml` template + filled instances (`retail_store_sales`,
`demo_sample_orders`). Most are reversible docs/plan choices that confirm a shape the spec
already implies; one (C3) turned out NOT to be mechanically implementable as written and is
DEFERRED to plan rather than defaulted.

- **C1 (degenerate vs date dims -- Edge Cases / FR-004) -- Default adopted.** Q: Which of a
  star's dimension records are in scope for cross-star conformance? A: HR1's conformance set is
  the star's LOOKUP dimensions -- entries under `gold_star.dimensions[]` PLUS a
  `gold_star.date_dimension` block where a table records the date dim separately -- and it
  EXCLUDES `gold_star.degenerate_dimensions[]`. Reasoning: degenerate dims are per-star
  transaction ids on the fact (RC14), not shared lookup dims, and the spec already lists
  "conformance of degenerate dims" as future scope; but the date dim IS a shared lookup dim and
  the spec's own `dim_date` Edge Case note requires HR1 to check its grain+type conformance, so
  it must be included. The committed instances record the date dim in BOTH forms (inside
  `dimensions[]` with `built_from`, or a standalone `date_dimension:` block), so HR1 must
  recognize either. Reconciles the C1 exclusion with the pre-existing `dim_date` note.
  Reversible: easy. Touches: Edge Cases (degenerate-dim + dim_date bullets), FR-004.

- **C2 (conformed-dimension-map shape -- FR-002) -- Default adopted.** Q: What is the
  top-level structure of `docs/quality/conformed-dimension-map.yaml`? A: mirror SF1's
  `shared-spine.yaml` -- one top-level `dimensions:` mapping (keys = gold dimension names),
  each entry carrying `status: conformed|distinct` plus a `stars: [<table_id>, ...]` list.
  Reasoning: SF1 is the named design precedent (top-level mapping + enum value + fail-closed on
  an unrecognized value); reusing its shape adds no new mechanism and no domain-specific key.
  Exact field names are confirmable at plan/template time. Reversible: easy. Touches: FR-002.

- **C3 (natural-key identification -- FR-005/FR-004) -- DEFERRED to plan (schema/mechanics
  gap; not Principle-V).** Q: The grain check compares "the natural-key attribute", but
  `gold_star.dimensions[]` carries no machine-readable natural-key marker (only an authoring
  comment). How does HR1 identify it without adding a `source-map.yaml` key (FR-004 forbids
  that)? A: it CANNOT, as the schema stands -- so the grain limb of FR-005 is NOT mechanically
  implementable as written and is deferred to plan. No reliable signal exists in the committed
  tree: first-position fails (`demo_sample_orders` `dim_product` lists the descriptive
  `product_name` first, not a key) and an `_id`-suffix heuristic fails (`retail_store_sales`
  `dim_product` natural key is `item`, no suffix). A fail-closed ERROR rule (Principle I) must
  not rest on an unenforced authoring convention, so no first-attribute default is adopted.
  PLAN MUST specify the natural-key signal before the grain check is built; leading candidate
  is an explicit marker owned by the source-mapping-gate schema that HR1 READS (never writes,
  FR-004). This is a schema/mechanics question (HR1 only reads a shape decided at Mapping
  Ready), NOT a Principle-V grain ruling. The key limb (surrogate_key) and type limb (C4) are
  unaffected. Touches: FR-005, FR-004.

- **C4 (shared-attribute compare set -- FR-005) -- Default adopted.** Q: FR-005 compares "the
  silver type of each shared attribute" -- which attributes count as shared across stars? A:
  the INTERSECTION of the attribute-NAME sets across the conformed stars (Kimball
  conformed-subset); a type disagreement on an intersection attribute is an ERROR, but a
  differing attribute SET alone (one star has an extra attribute) is NOT an ERROR in this
  feature. Reasoning: the conformed-subset is the standard Kimball notion and the narrowest
  reading that still catches type drift on genuinely shared attributes. Reversible: easy (a
  future spec may add attribute-set-mismatch enforcement). Touches: FR-005.

- **C5 (named star present but dimension absent -- FR-009/FR-010/Edge Cases) -- Default
  adopted.** Q: A map entry names a star whose `source-map.yaml` parses fine, but that star's
  `gold_star.dimensions[]` (+ `date_dimension`) does not actually contain the declared dimension
  name -- is that FR-009's stale/WARNING case or FR-010's malformed/ERROR case? A: STALE ->
  WARNING, same posture as a map entry whose declared dimension now survives in fewer than 2
  stars. Reasoning: FR-010's malformed/ERROR case is reserved for a star reference that cannot be
  resolved or parsed at all (a broken reference); a star that resolves and parses but simply no
  longer (or not yet) carries the named dimension is map drift, not a broken contract, and the
  SF1 precedent treats a listed-but-absent member as stale rather than a hard error. Reversible:
  easy. Touches: FR-009, FR-010, Edge Cases.

### Principle-V carve-out (OPEN -- owner ruling required; the workflow is forbidden to answer)

- **Q-APPROVAL-SEAM (FR-016) -- OPEN owner ruling.** Q: Does the model-level conformed tier
  require a NAMED-HUMAN approval seam on top of the mechanical HR1 gate, or is it purely
  mechanical like Silver Ready / Gold Ready (a clean HR1 run IS the sign-off, no `approvals[]`
  entry)? This is a who-approves / governance-shape decision (Principle V): adding a new
  named-human-approval tier joins the constitution's approval-bearing set, which the agent MUST
  NOT settle alone. RECORDED PENDING DEFAULT the owner may ratify: MECHANICAL (HR1 is a static
  objective check like S6/S7; the scope guard already forbids the agent self-granting the pass;
  no approval seam is invented until an owner rules one in). Until the owner rules, HR1 emits
  Findings only and records no model-level pass anywhere. Touches: FR-016 (and interacts with
  FR-011 and the "where the pass is recorded" plan-time assumption).
