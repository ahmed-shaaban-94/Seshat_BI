# Feature Specification: Actuals-vs-Target (Budget) Fact + Variance Readiness

**Feature Branch**: `095-actuals-vs-target-budget-fact`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Gap #18 -- Actuals-vs-target (budget) fact + variance readiness. Serves
Stages 2-5 (new fact family). Lens/justification: retail-kpi domains/targets-and-budgets.md. What it
is: a worked pattern + contract shape for a target/budget fact and actual-vs-plan variance (RAG). The
domain is taught as knowledge but no target fact exists in the spine, so RAG-vs-plan -- a core retail
exec view -- is unmodellable."

## Overview

`skills/retail-kpi-knowledge/domains/targets-and-budgets.md` already teaches the targets/budgets
domain: it names the decision question ("Are we hitting our sales target?"), the KPI it would answer
(Net Sales vs Target %), and four key ambiguities (grain match, calendar alignment, missing targets,
filter-scope parity). But the domain doc's own KPI table records that KPI's status as **Planned
(needs target fact)** -- because no target/budget fact has ever been modelled anywhere in the spine.
Every worked example, every mapping artifact, and every gold star built so far is an ACTUALS-only
star (one fact at the transaction/line grain, conformed dims, no plan-side counterpart). Without a
target/budget fact conformed to the same dimensions as actuals, a Kimball star has nothing to join a
plan number against, and RAG-vs-plan ("are we red, amber, or green against target") -- one of the most
common retail executive views -- is structurally unmodellable in this kit today.

This feature closes that gap as a PATTERN, not a shipped table. It authors: (1) a worked MODELLING
PATTERN for a target/budget fact that conforms to the same dimension set as an existing actuals star
(grain, conformance, and the non-additive variance-percentage calculation pattern already flagged in
the domain doc); (2) a CONTRACT SHAPE for the actual-vs-plan variance metric that plugs into the
existing F009 `templates/metric-contract.yaml` mechanism without redefining it; and (3) a SECOND
worked-example narrative section (Principle VII genericity proof) that walks the pattern against a
hypothetical target/budget fact conformed to the `retail_store_sales` actuals star -- without
inventing a single target VALUE. Every target number, every RAG threshold, and the target fact's
exact grain are owner-supplied business inputs (Principle V); this feature supplies the shape they
would be poured into, and leaves each one an explicit, named, unresolved question.

## Boundary against neighbouring shipped work (read first)

This feature is a genuine EXTENSION of already-shipped surfaces, not a restatement of any of them.
Three shipped neighbours must stay distinct, untouched, and un-duplicated:

- **`docs/worked-examples/retail-store-sales.md`** (the kit's first, and so far ONLY, worked
  example) traverses the full seven-stage spine for the `retail_store_sales` ACTUALS star. This
  feature does not edit that file and does not re-narrate its seven stages. It adds a genuinely
  SECOND worked-example narrative -- new content, in a new location -- that walks the
  target/budget-fact pattern conformed to that same actuals star's dimensions. Per Principle VII,
  a single worked example cannot prove genericity; this is the second data point, and it MUST stay
  a pattern/shape walkthrough (no live target rows), never a restatement of the first example's
  answers.
- **`templates/metric-contract.yaml`** (F009, the metric-contract mechanism) already defines how
  ANY metric -- including a ratio/variance metric -- is captured as intent + grain + `binds_to` +
  the ambiguity ledger. This feature does not redefine, fork, or replace that template. It authors
  a CONTRACT SHAPE (a filled-out pattern of that same template applied to a variance metric, plus
  notes on the fields a variance/RAG contract stresses that a simple sum does not) as its own new
  artifact; it does not add a second contract format.
- **`skills/retail-kpi-knowledge/domains/targets-and-budgets.md`** (the existing domain-knowledge
  doc) already teaches the domain, the KPI, and the four key ambiguities and marks the KPI
  `Planned (needs target fact)`. This feature does not edit that file -- flipping its `Planned`
  marker or rewriting its ambiguities is a shared-surface edit reserved for whoever ships the first
  REAL target-fact table (out of scope here, per the collision-avoidance allocation). This feature
  only CITES it as the domain justification and closes the gap it names.

This feature adds NO new readiness stage, NO new four-status gate, and NO new `retail check` rule
(collision-avoidance allocation, non-negotiable). It rides the EXISTING seven-stage spine and the
EXISTING F009 contract mechanism; it is a pattern + contract-shape + worked-example-section
docs/templates change only, confined to new files under `docs/`, `templates/`, and a new
worked-example directory.

**File locations (resolved 2026-07-04, see Clarifications):** the modelling pattern document is
authored at `docs/patterns/target-budget-fact.md`; the variance contract shape is authored at
`templates/metric-contract-shape.variance-vs-target.yaml` (a filled-pattern instance living
alongside, never inside, `templates/metric-contract.yaml`); the second worked-example narrative is
authored at `docs/worked-examples/target-budget-pattern-retail-store-sales.md` (a new file, distinct
from and never editing `docs/worked-examples/retail-store-sales.md`). The contract shape is authored
as a `.yaml` instance (mirroring `metric-contract.yaml`'s own format exactly, per FR-006/SC-005's
mechanically-checkable field-set match) with inline `#` comments carrying the authoring notes the
boundary section calls for, rather than a separate prose `.md` companion.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An analyst models a target/budget fact conformed to an existing actuals star (Priority: P1)

An analyst has an actuals star already at Gold Ready (or later) and now has a real target/budget
source (a finance-supplied plan file, a budget spreadsheet, whatever the owner actually hands over).
They need to know: what grain should the target fact be built at, which dimensions must it conform
to, how does a target fact's structure differ from an actuals fact's structure (no transaction rows,
typically pre-aggregated to a period/dimension-combination grain), and how does the eventual variance
calculation stay correct (aggregate each side separately, then compute the percentage -- never
average two already-computed percentages). They follow the worked pattern doc and produce their own
table's target-fact mapping and gold migration, the same way a new actuals table today copies
`retail-store-sales.md`.

**Why this priority**: Without a concrete modelling pattern, every future target/budget table
reinvents grain and conformance decisions from scratch, and the domain doc's flagged ambiguities
(grain match, calendar alignment) are exactly the kind of thing that gets silently gotten wrong
without a worked reference. This is the pattern the whole gap is about; without it nothing else in
this feature has anything to attach to.

**Independent Test**: Given the new pattern doc alone (no other artifact from this feature), an
analyst can state, for a hypothetical target/budget source, what grain decision they must make, which
existing conformed dimensions the target fact must reuse, and what the variance-calculation
non-additivity rule requires -- entirely from the doc, with zero external lookups beyond ADR 0002 and
the existing actuals-star pattern it already cites.

**Acceptance Scenarios**:

1. **Given** the target/budget fact pattern doc, **When** an analyst reads it, **Then** it states the
   target fact MUST conform to the SAME dimension keys as the actuals star it is compared against
   (RC14 conformed-dims discipline), citing `docs/decisions/0002-retail-cleaning-defaults.md`.
2. **Given** the pattern doc, **When** an analyst looks for the target fact's grain, **Then** the doc
   states that the target fact's grain is an OWNER-SUPPLIED business decision (commonly coarser than
   the actuals grain -- e.g. month x store x category rather than transaction) and marks the specific
   grain as `[NEEDS CLARIFICATION]` rather than asserting a grain.
3. **Given** the pattern doc, **When** an analyst looks for how variance is computed, **Then** the doc
   states the non-additive rule already named in `targets-and-budgets.md` (aggregate actuals and
   targets separately at the comparison grain, then recompute the percentage -- never average
   pre-computed ratios) and cites that domain doc rather than restating it as new invented guidance.
4. **Given** the pattern doc, **When** an analyst checks scope, **Then** the doc states plainly that
   it contains NO target VALUES, NO RAG thresholds, and NO specific table's grain decision --
   these are owner-supplied per Principle V and must be recorded in that table's own
   `unresolved-questions.md` when a real target table is onboarded.

---

### User Story 2 - An analyst authors an actual-vs-plan variance metric contract from the contract shape (Priority: P1)

Once a target/budget fact and an actuals fact both exist at a comparable grain for a table, an
analyst needs to define the variance metric ("Net Sales vs Target %") as a proper F009 metric
contract so it can eventually bind into a semantic model. They use the variance contract SHAPE this
feature provides -- a filled-out example of `templates/metric-contract.yaml`'s fields as they apply
to a ratio-of-two-facts metric -- to see how `binds_to`, `grain`, and the ambiguity ledger get filled
for a variance metric specifically (two gold tables, a non-additive ratio, a missing-target case that
must be flagged rather than defaulted to 0%).

**Why this priority**: The contract shape is what turns the modelling pattern into something an
analyst can actually file into the existing Semantic Model Ready machinery; without it the pattern is
architecture-only and never reaches a contract a model can bind to. Tied with User Story 1 as the
core deliverable.

**Independent Test**: Given the variance contract shape alone, an analyst can identify which
`metric-contract.yaml` fields a variance metric must fill differently from a simple additive-sum
metric (two-table `binds_to`, a `grain` that names the comparison rollup, and an `ambiguities[]` entry
for the missing-target case) without needing to read the F009 template's authoring notes from
scratch.

**Acceptance Scenarios**:

1. **Given** the variance contract shape, **When** an analyst compares it against
   `templates/metric-contract.yaml`, **Then** every field name in the shape matches the existing F009
   template exactly (no new field, no forked template) -- the shape is a filled pattern OF that
   template, not a competing one.
2. **Given** the variance contract shape, **When** an analyst looks at `binds_to`, **Then** the shape
   shows a variance metric reading from TWO gold tables (the actuals fact and the target fact) with a
   worked note on how a single-table `binds_to` block accommodates that (or where the shape flags this
   as a current template limitation for human review).
3. **Given** the variance contract shape, **When** an analyst looks for the missing-target case named
   in `targets-and-budgets.md` ("missing targets must be flagged, not shown as 0%"), **Then** the
   shape shows that case recorded as a required `ambiguities[]` / `blocking_reasons[]` entry, never as
   a silent default value.
4. **Given** the variance contract shape, **When** an analyst looks for a RAG (red/amber/green)
   threshold, **Then** the shape contains NO numeric threshold -- RAG banding is marked
   `[NEEDS CLARIFICATION: RAG thresholds are owner-supplied business policy]` and the shape shows
   only WHERE such a threshold would be recorded once an owner supplies it (as evidence on the
   filled contract, not invented by the pattern).

---

### User Story 3 - A second worked-example narrative proves the pattern is generic, not C086/retail_store_sales-specific (Priority: P2)

A reviewer checking Principle VII compliance (genericity: the questions and checks generalize, the
answers are per-table) reads a second worked-example narrative section that walks the target/budget
pattern against the `retail_store_sales` actuals star's existing conformed dimensions -- WITHOUT
inventing any target row, target value, or RAG threshold for that table. The section demonstrates the
pattern is reusable pattern-and-shape, and explicitly marks every place a REAL target-fact build for
`retail_store_sales` would need owner-supplied input before it could proceed past Mapping Ready.

**Why this priority**: A single example (the pattern doc itself, in the abstract) does not meet the
kit's own two-example genericity bar the way `retail-store-sales.md` set the precedent for the first
domain area; but the core deliverable (the pattern + contract shape) is already usable without this
narrative, so it is P2, not P1.

**Independent Test**: Given only the second worked-example section, a reader can see the pattern
applied to a NAMED existing star (`retail_store_sales`) with concrete conformed-dimension names drawn
from that star's own committed gold migration, while confirming zero fabricated target figures appear
anywhere in the section.

**Acceptance Scenarios**:

1. **Given** the second worked-example section, **When** a reviewer inspects it, **Then** every
   dimension name it references (`dim_customer_rss`, `dim_product_rss`, `dim_payment_method_rss`,
   `dim_location_rss`, `dim_date_rss`) is copied verbatim from the committed
   `0004_create_gold_retail_store_sales_star.sql` migration and `retail-store-sales.md`, never
   invented.
2. **Given** the second worked-example section, **When** a reviewer searches it for a numeric target
   value, a variance percentage, or a RAG color assignment, **Then** none exists anywhere in the
   section -- every such value is marked as an owner-supplied gap, not filled with a plausible number.
3. **Given** the second worked-example section, **When** a reviewer checks its readiness framing,
   **Then** it states plainly that `retail_store_sales` has NO target/budget fact today and that
   building one would restart at Mapping Ready for a NEW source (the target file/system), never
   implying the existing Gold Ready/Dashboard Ready status of the actuals star extends to an
   unbuilt target fact.

---

### Edge Cases

- What happens when a table's actuals star and its prospective target source have DIFFERENT native
  grains (e.g. actuals at transaction grain, targets supplied only at month x category)? The pattern
  states this is the expected, common case (targets are almost always coarser) and that the
  COMPARISON must happen at the coarser (target) grain -- actuals must be rolled up to match, never
  targets disaggregated to match actuals -- but the exact rollup dimensions for any real table remain
  an owner-supplied `[NEEDS CLARIFICATION]` per table, never asserted generically.
- What happens when a dimension member exists in the actuals star but has no corresponding target
  (e.g. a store opened mid-year with no budget yet, or a new product with no target)? Per the domain
  doc's own flagged ambiguity, the pattern requires this be surfaced as an explicit missing-target
  case (a flag, not a 0% or blank variance) -- the pattern names this requirement but does not decide
  how a specific table's dashboard should visually represent it (that is a dashboard-design decision,
  out of scope here).
- What happens when the target source itself changes mid-period (a budget revision/reforecast)? The
  pattern flags that a target fact may need a version/as-of dimension to avoid silently overwriting a
  prior plan, but whether any given table needs this is an owner-supplied judgment
  (`[NEEDS CLARIFICATION]`) -- this feature does not mandate a specific versioning scheme.
- What happens if someone tries to use this feature's second worked-example section as if it were a
  real, buildable table (i.e., tries to run `retail-onboard-table` against it)? The section is
  explicit that no bronze/silver/gold object, mapping artifact, or readiness-status.yaml exists for a
  `retail_store_sales` target fact; it is a narrative pattern illustration only, and MUST NOT be
  treated as evidence of any readiness stage for a target fact.
- What happens when an analyst wants a RAG threshold today, before an owner has supplied one? The
  contract shape and pattern doc both refuse to supply a default threshold (unlike additive
  cleaning-default RC rules, RAG bands are pure business policy with no safe generic default) --
  the metric contract's `readiness.status` stays `blocked` with a named `blocking_reasons[]` entry
  until an owner records one.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST author a target/budget fact MODELLING PATTERN document that states the
  target fact conforms to the SAME dimension keys as the actuals star it will be compared against
  (RC14 conformed-dimension discipline), citing `docs/decisions/0002-retail-cleaning-defaults.md`.
- **FR-002**: The pattern document MUST NOT assert a specific grain for any table's target/budget
  fact. It MUST state that target-fact grain is an owner-supplied business decision and MUST mark it
  `[NEEDS CLARIFICATION: target-fact grain is owner-supplied per table]` wherever the pattern would
  otherwise need a concrete grain to proceed.
- **FR-003**: The pattern document MUST state the non-additive variance-calculation rule already
  named in `skills/retail-kpi-knowledge/domains/targets-and-budgets.md` (aggregate actuals and
  targets separately at the comparison grain, then recompute the percentage) by CITING that domain
  doc, not by restating it as independently-invented guidance.
- **FR-004**: The pattern document MUST state that when actuals and target grains differ, the
  comparison happens at the COARSER (typically target) grain, and MUST NOT assert which specific
  dimensions any given real table's comparison rollup uses.
- **FR-005**: The pattern document MUST state the missing-target handling rule from the domain doc
  (a dimension member with no corresponding target MUST be flagged, never defaulted to 0% or silently
  dropped) as a structural requirement on any target-fact build, without asserting how a specific
  table's dashboard visualizes that flag (dashboard-design is out of scope here).
- **FR-006**: The feature MUST author a CONTRACT SHAPE for an actual-vs-plan variance metric that
  uses the EXACT field set of the existing `templates/metric-contract.yaml` (F009) -- it MUST NOT
  introduce a new template, a new field name, or a competing contract format.
- **FR-007**: The contract shape MUST show how a variance metric's `binds_to` references BOTH the
  actuals gold table and the target gold table, and MUST flag any place this exceeds what a
  single-table `binds_to` block was designed for as an open note for human/F009-owner review, rather
  than silently forcing a fit.
- **FR-008**: The contract shape MUST record the missing-target case as a required
  `ambiguities[]`/`blocking_reasons[]` entry pattern (per FR-005), never as a silently-defaulted
  value in a filled contract.
- **FR-009**: The contract shape MUST NOT specify a RAG (red/amber/green) numeric threshold anywhere.
  Any RAG banding reference MUST be marked
  `[NEEDS CLARIFICATION: RAG thresholds are owner-supplied business policy, not a kit default]` and
  MUST show only WHERE a threshold would be recorded (as owner-supplied evidence on a filled
  contract) once one exists.
- **FR-010**: The feature MUST NOT invent, estimate, or place any target/budget VALUE, variance
  percentage, or RAG color assignment anywhere in any authored artifact (Principle V; SCOPE GUARD).
  Every such value is owner-supplied and, until supplied, is represented only as an explicit
  unresolved question or a `[NEEDS CLARIFICATION]` marker -- never a placeholder number that could be
  mistaken for a real one.
- **FR-011**: The feature MUST author a SECOND worked-example narrative section (Principle VII
  genericity proof) that applies the pattern to the `retail_store_sales` actuals star's EXISTING,
  committed conformed dimensions (read from `0004_create_gold_retail_store_sales_star.sql` and
  `docs/worked-examples/retail-store-sales.md`), without editing either of those files.
- **FR-012**: The second worked-example section MUST NOT contain any fabricated target value,
  variance figure, or RAG assignment for `retail_store_sales`, and MUST state explicitly that no
  target/budget fact, mapping artifact, or readiness-status record exists yet for that table.
- **FR-013**: The second worked-example section MUST state that building a real target/budget fact
  for `retail_store_sales` (or any table) restarts the mapping gate at Mapping Ready for the NEW
  target source -- it MUST NOT imply the actuals star's existing Gold Ready / Dashboard Ready status
  extends to an unbuilt target fact.
- **FR-014**: All authored artifacts MUST NOT add a new readiness stage, a new four-status gate, or a
  new `retail check` rule ID -- this feature rides the existing seven-stage spine and the existing
  F009 contract mechanism only (collision-avoidance allocation).
- **FR-015**: All authored artifacts MUST NOT edit `docs/worked-examples/retail-store-sales.md`,
  `templates/metric-contract.yaml`, or
  `skills/retail-kpi-knowledge/domains/targets-and-budgets.md` -- they are cited, read, and extended
  alongside, never modified (collision-avoidance allocation; boundary section).
- **FR-016**: All authored artifacts MUST emit NO numeric confidence, health, maturity, or
  completeness score (hard rule #9). Any readiness framing used in the second worked-example section
  MUST use only the four explicit statuses (`not_started | blocked | warning | pass`) applied
  honestly (in this case, `not_started`, since no target fact exists) -- never a fabricated status
  implying progress that has not happened.
- **FR-017**: All authored artifacts MUST be ASCII, UTF-8 without BOM (use `--` and `->`, no glyphs),
  and MUST use short repo-relative paths respecting the Windows 260-character path budget (rule IX).
- **FR-018**: This feature MUST NOT author any live database connection, migration SQL, or execution
  code for any target/budget fact. Per Principle VIII (static-first, live-deferred), it is a static
  pattern + contract-shape + narrative doc set only; any eventual live target-fact build is a
  separate, later, per-table feature that walks the existing `source-mapping` -> `retail-build-warehouse`
  -> `retail-validate` sequence.
- **FR-019**: The pattern document and the contract shape MUST each explicitly list which of their
  own open items are Principle-V judgment calls (grain, RAG thresholds, versioning/reforecast
  handling, missing-target visualization) versus which are already-resolved structural defaults
  (conformed dims, non-additive variance calculation, missing-target-must-flag) -- so a future
  reader does not have to re-derive which parts are safe defaults and which require a named human.

### Key Entities

- **Target/budget fact (pattern only)**: a hypothetical second Kimball fact, conformed to the SAME
  dimension keys as an existing actuals star, at an OWNER-SUPPLIED grain (commonly coarser than
  actuals), carrying planned/budgeted measure values. No real instance is built by this feature.
- **Variance metric (contract shape only)**: the actual-vs-plan comparison (e.g. "Net Sales vs Target
  %"), computed non-additively (aggregate each side separately, then recompute the ratio), reading
  from both the actuals fact and the target fact at their comparison grain. Its RAG banding is
  owner-supplied and absent from any artifact this feature authors.
- **Comparison grain**: the (typically coarser, target-side) grain at which actuals are rolled up to
  meet targets for a valid comparison; a per-table owner decision, never asserted generically.
- **Missing-target case**: a dimension member present in actuals with no corresponding target row;
  MUST be flagged per the domain doc's existing ambiguity, never defaulted to 0%.
- **Second worked-example section**: the new narrative content (Principle VII genericity proof)
  applying the pattern to `retail_store_sales`'s existing conformed dimensions, with zero fabricated
  target data and an honest `not_started` framing for any target-fact build on that table.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An analyst onboarding a real target/budget source can identify, from the pattern
  document alone, every structural decision the pattern already makes for them (conformance,
  non-additive variance calculation, missing-target-must-flag) versus every decision that remains
  theirs to supply (grain, RAG thresholds, versioning) -- with zero ambiguity about which category
  each item falls into.
- **SC-002**: 0 authored artifacts in this feature contain a fabricated target value, variance
  percentage, or RAG color/threshold.
- **SC-003**: 0 authored artifacts in this feature add a new readiness-stage name, a new four-status
  gate, or a new `retail check` rule ID.
- **SC-004**: 0 authored artifacts in this feature modify `docs/worked-examples/retail-store-sales.md`,
  `templates/metric-contract.yaml`, or `skills/retail-kpi-knowledge/domains/targets-and-budgets.md`.
- **SC-005**: The variance contract shape's field set matches `templates/metric-contract.yaml`'s
  field set with 0 new/renamed fields.
- **SC-006**: The second worked-example section references only dimension/table names already
  present in `0004_create_gold_retail_store_sales_star.sql` or `retail-store-sales.md` -- 0 invented
  names.
- **SC-007**: A reader can locate, in under one pass of the pattern document and the contract shape,
  every `[NEEDS CLARIFICATION]` marker this feature leaves open (grain, RAG thresholds, versioning),
  with each one naming exactly what a future owner must supply.

## Assumptions

- `docs/worked-examples/retail-store-sales.md` and its `0004_create_gold_retail_store_sales_star.sql`
  migration are the only committed actuals star available to ground the second worked-example
  section; a future second REAL table is out of scope here.
- `templates/metric-contract.yaml` (F009) is the sole contract mechanism this feature builds a shape
  for; no alternative contract format is introduced.
- `skills/retail-kpi-knowledge/domains/targets-and-budgets.md`'s four key ambiguities (grain match,
  calendar alignment, missing targets, filter-scope parity) are treated as the authoritative starting
  list of open questions the pattern must acknowledge; this feature does not discover new ambiguities
  beyond what that doc already names, beyond the versioning/reforecast edge case surfaced during
  authoring.
- No live database, target-data file, or real budget figure is available or will be sought during
  this feature; Principle VIII (static-first, live-deferred) applies in full -- there is nothing to
  mark `[PENDING LIVE PROFILE]` because no live surface is touched at all.
- A real per-table target/budget fact build (source-mapping through gold + contracts) is a separate,
  later feature that consumes this pattern; it is not scheduled or numbered by this spec.
- The F016 Power BI execution adapter does not exist and is not assumed reachable; no dashboard or
  publish-layer consequence of a variance metric is addressed here (RAG *visualization* is
  dashboard-design's later concern, not this feature's).

## Clarifications

### Session 2026-07-04

- **Q: Where do the three authored deliverables (pattern document, contract shape, second
  worked-example) live -- the spec named the sanctioned directories (`docs/`, `templates/`, a
  worked-example dir) but never a concrete path or filename?**
  **A (Default adopted, Principle VI):** `docs/patterns/target-budget-fact.md` for the pattern
  document; `templates/metric-contract-shape.variance-vs-target.yaml` for the contract shape
  (co-located alongside, never merged into, `templates/metric-contract.yaml`); and
  `docs/worked-examples/target-budget-pattern-retail-store-sales.md` for the second worked-example
  narrative (a new file, distinct from `docs/worked-examples/retail-store-sales.md`). These paths
  stay inside the collision-avoidance allocation's sanctioned surfaces and touch no shared schema.
  Touches: Overview / boundary section (paths recorded above), FR-001, FR-006, FR-011.

- **Q: What FILE FORMAT should the contract shape take -- FR-006/SC-005 require its field set to
  match `templates/metric-contract.yaml` exactly (implying a `.yaml` instance), while the boundary
  section also asks for "notes on the fields a variance/RAG contract stresses" (which reads like
  prose)?**
  **A (Default adopted, Principle VI):** author it as a single `.yaml` file in the exact shape of
  `metric-contract.yaml`, with the stress-point notes carried as inline `#` comments rather than a
  separate prose companion document. This keeps SC-005's "0 new/renamed fields" check mechanical
  (diff the key set against the template) instead of requiring a second artifact to reconcile.
  Touches: FR-006, FR-007, FR-008, FR-009, SC-005.

- **Q: What is the target/budget fact's GRAIN for any real table (transaction-matched, month x
  store x category, or something else)?**
  **A (OPEN owner ruling -- Principle V, business-policy/grain judgment call; NOT answered here).**
  The spec already correctly refuses to assert this generically and keeps the inline
  `[NEEDS CLARIFICATION: target-fact grain is owner-supplied per table]` marker as required
  DELIVERABLE CONTENT of the pattern document itself (FR-002) -- this clarify pass does not resolve
  it, and the marker stays in place unchanged. Any real table's grain decision is recorded in that
  table's own `unresolved-questions.md` when a target fact is actually onboarded, per Acceptance
  Scenario 4 of User Story 1.
  Touches: FR-002, FR-004 (comparison-grain corollary), Key Entity "Comparison grain".

- **Q: What are the RAG (red/amber/green) numeric thresholds for any variance metric?**
  **A (OPEN owner ruling -- Principle V, business-policy judgment call; NOT answered here).** The
  spec already correctly refuses a default (RAG bands have no safe generic default, unlike additive
  RC cleaning defaults) and keeps the inline
  `[NEEDS CLARIFICATION: RAG thresholds are owner-supplied business policy, not a kit default]`
  marker as required deliverable content of the contract shape (FR-009). This clarify pass does not
  resolve it; the marker stays in place unchanged. A filled contract's `readiness.status` remains
  `blocked` with a named `blocking_reasons[]` entry until a named owner supplies a threshold.
  Touches: FR-009, Edge Case "What happens when an analyst wants a RAG threshold today".

- **Q: Does a target/budget fact need a version/as-of dimension to handle mid-period budget
  revisions or reforecasts, and if so what versioning scheme?**
  **A (OPEN owner ruling -- Principle V, business-policy judgment call; NOT answered here).** The
  spec already correctly frames this as a per-table owner decision ("whether any given table needs
  this is an owner-supplied judgment") rather than mandating a scheme. This clarify pass does not
  resolve it and introduces no versioning default; the pattern document (FR-002/FR-019) must list
  this as an open Principle-V item alongside grain and RAG thresholds, not as a resolved structural
  default.
  Touches: FR-002, FR-019, Edge Case "What happens when the target source itself changes
  mid-period".
