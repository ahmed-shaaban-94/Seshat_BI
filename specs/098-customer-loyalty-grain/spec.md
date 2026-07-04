# Feature Specification: Customer / Loyalty Grain + Dimension Pattern

**Feature Branch**: `098-customer-loyalty-grain`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Gap #19 -- Customer / loyalty grain + dimension pattern: a
customer dimension + customer-grain pattern (identity resolution, RFM/retention/CLV grain)
so customer analytics is structurally possible. Customer is the heaviest KPI knowledge
domain yet has no dimension or customer-grain fact in the spine."

## Overview

`skills/retail-kpi-knowledge/domains/customer.md` is the heaviest KPI knowledge domain in
the repo -- four candidate KPIs (Customer Retention Rate, Purchase Frequency, Customer
Lifetime Value, New-vs-Returning split), each explicitly `Planned`, each blocked on the
same unmade ruling: no confirmed customer identity key, no confirmed retention/CLV/segment
grain. That domain file correctly states the stops and decides none of them (Principle V);
what it does NOT have is a companion STRUCTURAL pattern an analyst can pick up once an
owner finally makes those rulings for a real source.

The gap is precise, not absolute. A single-source, already-ruled customer dimension DOES
exist today: `gold.dim_customer_rss` (warehouse/migrations/0004, mirrored in the
RetailStoreSales PBIP model) is a FILLED INSTANCE for the retail_store_sales worked
example, built on a table-scoped Q1 ruling ("keep `customer_id`, pseudonymous, no raw PII"
-- `mappings/retail_store_sales/unresolved-questions.md`). That ruling is real, but it is
narrow: one source, one already-resolved identity question, a bare two-column dimension
with no retention/RFM/CLV grain and no identity-resolution shape (one row already equals
one already-trusted natural key; nothing here resolves the same person appearing under
multiple ids). There is no GENERIC, reusable pattern in `templates/` or `docs/` that a
future table's analyst and owner could apply to reach a conformed customer dimension or a
customer-grain fact for retention/frequency/CLV -- only one filled, source-specific answer
and one knowledge-layer list of the open questions.

This feature closes that structural gap: a generic customer dimension shape (conformed
Kimball dimension, Principle III) plus a generic customer-grain fact/snapshot pattern
(the grain a retention, frequency, or CLV metric would need), each carrying explicit
PLACEHOLDER slots for the identity key, the PII publish-safety decision, and the
retention/CLV/segment grain -- never a default answer to any of them. It serves Stage 2
(Mapping Ready: a table's map can now cite a pattern for its grain/PK/dimension shape
instead of inventing one from scratch) and Stage 5 (Semantic Model Ready: a future
customer metric contract, F009, has a conformed dimension + grain to bind to). It adds no
identity-resolution algorithm, no PII ruling, and no seeded metric -- it makes customer
analytics STRUCTURALLY POSSIBLE for the first table an owner rules on, without deciding
that ruling itself.

## Boundary against neighbouring shipped work (read first)

This feature is a genuine EXTENSION of the customer-domain gap, not a restatement of
either shipped neighbour. Two shipped neighbours must stay distinct:

- **`gold.dim_customer_rss` + `gold.fct_sales_rss`** (warehouse/migrations/0004_create_
  gold_retail_store_sales_star.sql; mirrored in
  `powerbi/RetailStoreSales.SemanticModel/definition/tables/gold dim_customer_rss.tmdl`)
  is a FILLED, table-scoped instance for ONE source (retail_store_sales / C086), built on
  an ALREADY-ANSWERED Q1 PII ruling for that table only. This feature does NOT edit that
  migration, does NOT edit that TMDL, does NOT re-open or re-litigate Q1, and does NOT
  generalize Q1's answer ("keep, no raw PII") into a repo-wide default -- a different
  source's identity/PII ruling may come out differently. This feature produces a
  GENERIC, copy-me pattern (docs + template) that a NEW table's mapping could choose to
  apply; it is not itself a second filled instance and it touches no existing gold table.
- **`skills/retail-kpi-knowledge/domains/customer.md`** (spec 042) is the KNOWLEDGE-LAYER
  overview: it lists the four Planned customer KPIs and STATES the four Principle-V stops
  (identity/grain, PII publish-safety, segment rollups, product identity) verbatim,
  deciding none of them. This feature is the STRUCTURE-LAYER companion: a dimension +
  grain PATTERN a table could adopt once those same stops are eventually ruled by their
  owner. It does not edit `domains/customer.md`'s KPI table or Planned statuses, does not
  seed a metric contract, and does not answer any of the four stops that file already
  carries -- it cites that file's stops rather than restating or resolving them.

This feature adds NO new readiness stage and NO new `retail check` rule (the
collision-avoidance allocation for this parallel-build round): it is docs + a copy-me
template only, touching no shared gold schema and no existing table's migration, mapping,
or PBIP model.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An analyst has a generic conformed customer dimension shape to start from (Priority: P1)

An analyst onboarding a NEW source that carries some notion of "customer" (loyalty id,
account, member number, phone) wants to know what a conformed customer dimension should
look like before they map it. Today they have only the domain-knowledge list of open
questions and one already-answered, source-specific filled example to reverse-engineer
from. After this feature, they can read a generic customer-dimension pattern doc plus a
copy-me dimension template: a surrogate key (`customer_sk`), an explicit PLACEHOLDER
natural/identity-key slot (not a prescribed field), an explicit PLACEHOLDER PII-publish
slot (default undecided, never default-keep or default-drop), and the -1 unknown-member
convention already used elsewhere in the star (RC14).

**Why this priority**: Without a generic dimension shape, every future table reinvents the
customer dimension from the one filled C086 instance, risking a silently copied PII
ruling that was never re-examined for the new source. This is the structural core of the
gap.

**Independent Test**: Read `docs/patterns/customer-dimension-pattern.md` and
`templates/customer-dimension.md` in isolation (no other feature); confirm the dimension
shape names a surrogate key, an explicit unresolved identity-key slot, an explicit
unresolved PII-publish slot, and the -1 unknown-member row, and confirm neither file
answers either slot or names a specific field.

**Acceptance Scenarios**:

1. **Given** the new pattern doc and template, **When** an analyst reads them for a
   source that is not retail_store_sales, **Then** they find a generic surrogate-key +
   natural-key-slot + PII-slot shape with no C086 column name, table name, or ruling
   baked in.
2. **Given** the template's identity-key slot, **When** an analyst inspects it, **Then**
   it is marked with the canonical unresolved-ruling marker (FR-002:
   `[NEEDS CLARIFICATION: identity key not ruled -- owner ruling]`) rather than defaulted
   to any specific field (email, phone, loyalty id, or `customer_id`).
3. **Given** the template's PII-publish slot, **When** an analyst inspects it, **Then**
   it is marked as an unresolved owner/governance ruling and carries neither "keep" nor
   "drop" as a shipped default value.

---

### User Story 2 - An analyst has a generic customer-grain pattern for retention/frequency/CLV facts (Priority: P1)

The same analyst, once a customer dimension exists, wants to know at what GRAIN a
retention, purchase-frequency, or CLV metric should be computed -- one row per customer
per period? One row per customer lifetime-to-date? Today `domains/customer.md` names the
ambiguity (retention window, CLV horizon, first-purchase anchor) but offers no candidate
grain shape to reason from. After this feature, a generic customer-grain fact/snapshot
pattern doc names the CANDIDATE grains those KPI families need (a periodic snapshot grain
for retention/frequency; a customer-to-date grain for CLV) as OPTIONS to be ruled on, not
a shipped answer, each explicitly tied back to the same open ambiguities
`domains/customer.md` already carries.

**Why this priority**: The dimension alone (User Story 1) does not make retention/
frequency/CLV computable; those KPIs are grain-dependent facts, and the domain file
already says so. This is the second half of "structurally possible."

**Independent Test**: Read `docs/patterns/customer-grain-pattern.md` in isolation; confirm
it names candidate grains for the four Planned customer KPIs, cites `domains/customer.md`
for the underlying ambiguity, and asserts none of retention-window, CLV-horizon, or
new-vs-returning anchor as a decided value.

**Acceptance Scenarios**:

1. **Given** the customer-grain pattern doc, **When** an analyst reads the retention/
   frequency section, **Then** it names a periodic-snapshot candidate grain (e.g.
   "one row per customer per calendar period") as an OPTION and marks the period length
   itself `[NEEDS CLARIFICATION: retention window not ruled -- owner ruling]`.
2. **Given** the same doc, **When** an analyst reads the CLV section, **Then** it names a
   customer-to-date candidate grain as an OPTION and marks the horizon/discounting
   question `[NEEDS CLARIFICATION: CLV horizon not ruled -- owner ruling]`.
3. **Given** the same doc, **When** an analyst reads the new-vs-returning section,
   **Then** it marks the first-purchase anchor
   `[NEEDS CLARIFICATION: anchor not ruled -- owner ruling]` and does not silently pick a
   first-transaction-date default.

---

### User Story 3 - The pattern names identity resolution as a stop, without deciding it (Priority: P2)

An analyst mapping a source where the same customer may appear under more than one raw
id (a loyalty card AND a phone number, for example) wants to know where identity
resolution fits in the pattern, without the pattern silently picking a resolution
strategy for them. After this feature, the dimension pattern doc names identity
resolution as a distinct, explicitly out-of-scope decision point (one raw source id vs.
multiple ids merged into one customer_sk) and points at the reserved ruling already
recorded in `domains/customer.md`, rather than proposing a merge algorithm.

**Why this priority**: This is the sharpest Principle-V edge in the whole feature (the
scope guard names it explicitly) but it is a documentation cross-reference, not new
structure -- P2 relative to the two grain/dimension deliverables above, which are usable
even before any multi-id source appears.

**Independent Test**: Read the pattern doc's identity-resolution section in isolation;
confirm it states the multi-id problem, cites `domains/customer.md`'s identity/grain stop,
and proposes no merge rule, matching heuristic, or precedence order between competing raw
ids.

**Acceptance Scenarios**:

1. **Given** the pattern doc, **When** an analyst reads the identity-resolution section,
   **Then** it states that resolving multiple raw ids to one customer is a reserved
   owner ruling and links to `domains/customer.md`'s identity/grain stop.
2. **Given** the same section, **When** an analyst looks for a merge rule (e.g. "prefer
   loyalty id over phone"), **Then** none exists -- the section proposes no precedence
   or matching heuristic.

---

### Edge Cases

- What happens when a table has only ONE customer-identifying column and no multi-id
  ambiguity (the retail_store_sales case)? The pattern still applies (a single-id source
  is the simplest case of the same slot), but this feature does not retrofit
  `dim_customer_rss` to the pattern's shape -- that migration is out of scope (see
  Boundary section).
- What happens when an analyst tries to use the pattern to seed a customer metric
  contract directly? The pattern is a dimension/grain SHAPE, not a metric contract; F009's
  contract-template + review process still applies, and this feature seeds none.
- What happens when the pattern's PII-publish slot is read as an implicit recommendation
  (e.g. "the C086 example kept it, so keep is the default")? The pattern MUST state
  explicitly that no default is implied and that C086's Q1 answer applies to that source
  only.
- What happens when a reader wants the retention window, CLV horizon, or new-vs-returning
  anchor decided so they can build now? They cannot get that from this feature by design;
  each stays `[NEEDS CLARIFICATION]` until the named owner rules (Principle V), and this
  feature's Success Criteria measure that the pattern still functions (is legible and
  applicable) with all three left open.
- What happens if a future table's source-map wants to CITE this pattern? The pattern
  docs use a generic `<table>` placeholder path so any table's mapping can reference them
  without the pattern being edited per table (Principle VII).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST add exactly two new pattern documents under `docs/patterns/`
  -- a customer-dimension pattern and a customer-grain pattern -- plus a copy-me dimension
  template under `templates/`. The customer-grain pattern stays DOC-ONLY (no copy-me grain
  template): a template implies an instantiable, chosen grain, and which grain a table
  adopts is itself part of the reserved retention/CLV/anchor rulings this feature must not
  make (Principle V). It MUST NOT add a runtime executor, a CLI command, or a
  `src/retail/rules/` entry (collision-avoidance allocation: adds no static rule).
- **FR-002**: The customer-dimension pattern MUST define a conformed Kimball dimension
  shape (Principle III) with: a surrogate key (`*_sk` convention, RC14), an explicit
  natural/identity-key slot marked as an unresolved ruling (not a named field), an
  explicit PII-publish-safety slot marked as an unresolved ruling (not defaulted to keep
  or drop), an explicit SCD/historization-type slot marked as an unresolved ruling (naming
  Type 1 "overwrite" vs. Type 2 "track history" as the two options, deciding neither), and
  the -1 unknown-member row convention already used by the shipped star (RC14). Every
  unresolved-ruling slot in both new documents and the new template MUST use one canonical
  marker string, `[NEEDS CLARIFICATION: <slot-specific reason> -- owner ruling]`, so a
  reader can grep one pattern across both documents rather than reconcile two marker
  spellings.
- **FR-003**: The customer-grain pattern MUST name CANDIDATE grains for each of the four
  Planned customer KPIs listed in `skills/retail-kpi-knowledge/domains/customer.md`
  (Customer Retention Rate, Purchase Frequency, Customer Lifetime Value, New-vs-Returning
  split) as options to be ruled on, not as a shipped default grain. Every candidate grain
  MUST state that it keys to the customer dimension's surrogate key (`customer_sk`) as a
  foreign key, with COALESCE-to-`-1` for an unresolved/unknown member (RC14), consistent
  with Principle III's conformed-dimension requirement -- this fixes the STRUCTURAL join
  shape only and decides no grain, period, horizon, or anchor value.
- **FR-004**: The customer-grain pattern MUST leave the retention window, the CLV horizon/
  discounting choice, and the new-vs-returning first-purchase anchor as
  `[NEEDS CLARIFICATION: ...]` markers; it MUST NOT pick a period length, a horizon, a
  discount rate, or an anchor rule (Principle V -- these are the same reserved rulings
  `domains/customer.md` already carries).
- **FR-005**: The customer-dimension pattern MUST name identity resolution (multiple raw
  ids mapping to one customer) as an explicit, reserved owner ruling; it MUST NOT propose
  a matching heuristic, a merge algorithm, or a precedence order between competing raw
  identifiers (Scope Guard).
- **FR-006**: Neither new pattern document MUST decide, recommend, or imply a default
  answer to any of the four Principle-V stops already recorded in
  `skills/retail-kpi-knowledge/domains/customer.md` (identity/grain, PII publish-safety,
  business-segment rollups, product identity). Each MUST be cross-referenced to that file
  rather than restated in different words that could read as a fresh ruling.
- **FR-007**: The feature MUST NOT edit, generalize, or extend the ALREADY-RULED,
  table-scoped `gold.dim_customer_rss` / `gold.fct_sales_rss` objects
  (warehouse/migrations/0004) or their PBIP mirror. It MUST NOT restate C086's Q1 PII
  answer ("keep `customer_id`, no raw PII") as a repo-wide or pattern-level default.
- **FR-008**: The feature MUST NOT edit `skills/retail-kpi-knowledge/domains/customer.md`
  (its KPI table, decision-questions table, and Principle-V stop section stay exactly as
  spec 042 shipped them); this feature only CITES that file.
- **FR-009**: The feature MUST NOT seed, author, or modify any file under `contracts/`
  (metric contracts remain F009's gated process) and MUST NOT advance or self-grant any
  readiness stage for any table.
- **FR-010**: The feature MUST NOT emit any numeric confidence, health, maturity, or
  completeness score (hard rule #9). Readiness/applicability of the pattern is expressed
  only as which slots are filled (generic) vs. which remain an explicit owner ruling --
  never a percentage or count framed as a health signal.
- **FR-011**: Both new pattern documents and the new template MUST stay generic
  (Principle VII): no C086/retail_store_sales column name, table name, or specific
  ruling may be inlined as a default; the worked example may be cited only as "see
  `mappings/retail_store_sales/...` for one filled, source-specific answer."
- **FR-012**: All authored artifacts MUST be ASCII, UTF-8 without BOM (`--` and `->`, no
  Unicode glyphs), and MUST use short repo-relative paths within the Windows 260-char
  path budget (Principle IX).
- **FR-013**: The feature MUST NOT connect to a live database, MUST NOT invoke the
  deferred Power BI execution adapter (F016), and MUST NOT assume any live-profile result
  -- pattern authorship is static-only (Principle VIII); any live application of the
  pattern to a real table is a future table's own Stage 1/2 profiling work, out of scope
  here.
- **FR-014**: The dimension template MUST be structured so a future table's source-map
  (`templates/source-map.yaml` shape) can reference it by name in a `gold_star.dims`
  entry without copying pattern text into the map -- i.e., the template is citable, not
  merely descriptive prose.
- **FR-015**: The feature MUST NOT widen or narrow which readiness stages carry a
  named-human `approvals[]` requirement, and MUST NOT introduce a new `retail check`
  rule id (collision-avoidance allocation, non-negotiable for this parallel-build round).

### Key Entities

- **Customer dimension pattern**: the new `docs/patterns/customer-dimension-pattern.md`
  doc -- a generic conformed-dimension shape (surrogate key, identity-key slot, PII-publish
  slot, unknown-member row) with no source-specific answer filled in.
- **Customer dimension template**: the new `templates/customer-dimension.md` copy-me
  artifact instantiating the pattern's shape for a future table's mapping to adopt.
- **Customer-grain pattern**: the new `docs/patterns/customer-grain-pattern.md` doc --
  candidate grains for retention/frequency/CLV/new-vs-returning KPIs, each tied to an
  explicit `[NEEDS CLARIFICATION]` ruling rather than a decided period/horizon/anchor.
- **Identity-key slot**: a named-but-unfilled placeholder in the pattern/template marking
  where a table's confirmed customer identity field goes once an owner rules it; the
  pattern itself never names a candidate field.
- **PII-publish slot**: a named-but-unfilled placeholder marking where a table's
  governance publish-safety ruling goes; default is neither "keep" nor "drop" at the
  pattern level (each table's owner rules its own case, as C086's Q1 did for itself).
- **SCD/historization-type slot**: a named-but-unfilled placeholder marking where a
  table's owner rules whether the customer dimension is Type 1 (overwrite) or Type 2
  (track history); the pattern names both options and decides neither.
- **Identity-resolution stop**: a documented cross-reference (not a mechanism) pointing
  a reader from the pattern to `domains/customer.md`'s reserved identity/grain ruling.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A future table's analyst can locate a generic customer dimension shape and
  a generic customer-grain pattern in one hop from `docs/patterns/`, without reverse-
  engineering the single filled C086 instance.
- **SC-002**: 100% of the four Planned customer KPIs named in `domains/customer.md` have a
  corresponding candidate-grain entry in the new grain pattern doc; 0 of the four have a
  decided period length, horizon, discount rate, or anchor value.
- **SC-003**: 0 new pattern/template files contain a C086/retail_store_sales-specific
  column name, table name, or ruling presented as a default (generic-retail scan passes).
- **SC-004**: 0 new pattern/template files contain a numeric confidence, health, maturity,
  or completeness score (hard rule #9 scan passes).
- **SC-005**: 0 edits land in `warehouse/migrations/0004_create_gold_retail_store_sales_
  star.sql`, its PBIP TMDL mirror, or `skills/retail-kpi-knowledge/domains/customer.md`
  (the two shipped neighbours stay byte-identical).
- **SC-006**: The `retail check` static gate exits 0 over the changed tree with the same
  rule count as before this feature (no new rule id introduced).
- **SC-007**: 0 files under `contracts/` are created or modified by this feature.

## Assumptions

- "Loyalty" in this feature's name refers to loyalty as one CANDIDATE customer-identity
  signal (a loyalty id, card, account, or member number is one of several possible raw
  identifiers the identity-key slot might eventually hold) and to loyalty-adjacent KPIs
  (retention, frequency) already named in `domains/customer.md` -- it does NOT introduce a
  separate loyalty-program dimension, tier table, or points/rewards structure. Any loyalty
  tier or cohort is itself a business-segment rollup and stays a reserved owner ruling
  (Principle V), out of scope to author here.
- `skills/retail-kpi-knowledge/domains/customer.md` (spec 042) remains the authoritative
  knowledge-layer statement of the four Principle-V customer stops; this feature reads and
  cites it rather than re-deriving or re-stating those stops in its own words.
- `gold.dim_customer_rss` / `gold.fct_sales_rss` (warehouse/migrations/0004) remain the
  one shipped, table-scoped filled instance; this feature treats it as a citable example
  of "one source's answer," never as the generic schema (Principle VII), and does not
  retrofit it to the new pattern's shape.
- RC14 (surrogate keys, -1 unknown member, FK COALESCE) from
  `docs/decisions/0002-retail-cleaning-defaults.md` is the correct existing convention to
  reuse for the dimension pattern's structural mechanics; this feature does not invent a
  new key convention.
- Identity resolution across multiple raw ids, the PII publish-safety ruling, the
  retention window, the CLV horizon, and the new-vs-returning anchor are ALL reserved
  human/governance rulings (Principle V) and are explicitly OUT OF SCOPE to decide in this
  feature; they are named as open slots, not resolved.
- No live database connection, no F016 Power BI execution adapter, and no F031-F033
  spec-only runtimes are assumed to exist or are touched (static-first, Principle VIII).
- This feature does not require a new roadmap F-number allocation decision to be made in
  this spec; if one is needed it is a plan-time roadmap-ledger edit, not invented here.
- The two new pattern docs are read-only reference material for a HUMAN analyst and the
  agent to consult during a future table's Stage 1/2 onboarding; they are not themselves
  executed by any tool and add no new `retail check` rule (collision-avoidance
  allocation).

## Clarifications

### Session 2026-07-04

- **Q1: The spec's own illustrative markers use two different spellings --
  `[NEEDS CLARIFICATION / owner ruling]` (User Story 1) vs.
  `[NEEDS CLARIFICATION: retention window not ruled]` (User Story 2, FR-004). Should the
  two authored pattern documents and the template standardize on one marker string, or is
  spelling-per-slot acceptable?**
  Resolution: Default adopted (Principle VI). One canonical marker string is now
  required: `[NEEDS CLARIFICATION: <slot-specific reason> -- owner ruling]`. This is a
  pure authoring-consistency default (grep-one-pattern legibility for SC-001); it decides
  no domain question and defaults no PII/identity/grain ruling. Touches: FR-002 (new
  sentence), User Story 1 Acceptance Scenario 2 (illustrative text aligned).
- **Q2: FR-003 names candidate grains for the four Planned customer KPIs but never states
  how a candidate grain's fact/snapshot row joins back to the customer dimension. Is a
  structural FK-to-`customer_sk` join implied, or does the grain pattern stay silent on
  joinability?**
  Resolution: Default adopted (Principle VI, reusing RC14). Every candidate grain in the
  customer-grain pattern MUST state it keys to the customer dimension via `customer_sk`
  as a foreign key, COALESCE'd to `-1` for an unresolved/unknown member -- the same
  convention the shipped star already uses. This fixes only the STRUCTURAL join shape
  (a conformed dimension needs a documented join surface, Principle III); it decides no
  grain, period, horizon, or anchor value. Touches: FR-003 (new sentence).
- **Q3: FR-001 mandates a copy-me template only for the customer DIMENSION. Should the
  customer-GRAIN pattern also ship a copy-me template, or stay doc-only?**
  Resolution: Default adopted (Principle VI, reinforcing Principle V). The grain pattern
  stays DOC-ONLY; no copy-me grain template ships. A template would instantiate a chosen
  grain (period length, horizon, anchor), and which grain a table adopts is itself part
  of the reserved rulings this feature must not make. Touches: FR-001 (new sentence),
  FR-003 (clarifying comment).
- **Q4: The dimension pattern's shape (FR-002) enumerates a surrogate key, an
  identity-key slot, and a PII-publish slot, but says nothing about SCD/historization
  (Type 1 overwrite vs. Type 2 track-history) -- is that omission intentional, or is it a
  fourth slot the "conformed dimension shape" (Principle III) should also name?**
  Resolution: Default adopted (Principle VI). A conformed Kimball dimension shape is
  incomplete without naming its historization behavior, so the dimension pattern now
  names an explicit SCD/historization-type slot alongside the identity-key and
  PII-publish slots -- stating Type 1 and Type 2 as the two named options and deciding
  neither (the choice is itself a per-table governance/business ruling, Principle V).
  Touches: FR-002 (new slot), Key Entities (new "SCD/historization-type slot" entity).
- **Q5: The spec already names five reserved Principle-V rulings scattered across FR-004,
  FR-005, FR-006, and the Assumptions (identity resolution across multiple raw ids, the
  PII publish-safety ruling, the retention window, the CLV horizon/discounting choice, and
  the new-vs-returning first-purchase anchor). Should any of these be decided here so the
  pattern ships more "complete," or does each stay an explicitly open owner ruling?**
  Resolution: OPEN owner ruling -- NOT decided in this spec or by this feature. Each of
  the five stays exactly as `domains/customer.md` (spec 042) and this spec's FR-004/
  FR-005/FR-006 already frame it: an explicit, reserved judgment call for the table's
  named business/governance owner at the time a real source is mapped (Principle V). This
  agent does not pick a value, does not imply a default, and does not self-grant a
  resolution. No spec text changed for this item -- the existing `[NEEDS CLARIFICATION]`
  markers and FR-004/FR-005/FR-006 language are affirmed as correct and are left in place
  (only their marker SPELLING is standardized per Q1). Touches: FR-004, FR-005, FR-006.
