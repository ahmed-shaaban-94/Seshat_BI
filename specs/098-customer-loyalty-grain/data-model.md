# Data Model: Customer / Loyalty Grain + Dimension Pattern

Phase 1 output. Defines the artifact SHAPES this feature introduces (markdown
structures, not database tables -- this feature writes no SQL and touches no
schema). Generic (Principle VII): every field value shown below is an
ILLUSTRATION of a SLOT, never a filled answer. No C086/`retail_store_sales`
column name, table name, or ruling (e.g. `customer_id`, "keep, no raw PII") is
used as an example value anywhere in this document -- see research.md's
precedent survey for why that specific substitution is the trap this feature
exists to avoid.

## The canonical unresolved-ruling marker

Every entity below that carries an unresolved slot uses exactly one marker
string (spec.md Clarify Q1, FR-002):

```text
[NEEDS CLARIFICATION: <slot-specific reason> -- owner ruling]
```

One spelling across all three authored artifacts (the two pattern docs plus
the template) so a reviewer can `grep` one pattern rather than reconcile two
marker spellings. `<slot-specific reason>` is replaced per slot (e.g.
`identity key not ruled`, `PII publish-safety not ruled`,
`SCD/historization type not ruled`); the surrounding `[NEEDS CLARIFICATION: ...
-- owner ruling]` shape does not vary.

## Entities (from spec.md Key Entities)

### CustomerDimensionPattern

The new `docs/patterns/customer-dimension-pattern.md` document. A conformed
Kimball dimension SHAPE (Principle III), not a filled table.

| Slot | Filled or unresolved? | Content |
|---|---|---|
| Surrogate key | FILLED (structural convention, not a business ruling) | `customer_sk`, an integer identity/generated key, RC14 convention -- the same mechanic `gold.dim_customer_rss` already uses. |
| Natural/identity-key slot | UNRESOLVED | `[NEEDS CLARIFICATION: identity key not ruled -- owner ruling]`. Never a named field (not `customer_id`, not `email`, not `loyalty_id`, not `phone`) -- the pattern names the SLOT, never a candidate value. |
| PII-publish-safety slot | UNRESOLVED | `[NEEDS CLARIFICATION: PII publish-safety not ruled -- owner ruling]`. Carries neither "keep" nor "drop" as a shipped default (FR-002); the doc states explicitly that no default is implied and that a cited filled example's answer applies to that source only (Edge Cases). |
| SCD/historization-type slot | UNRESOLVED | `[NEEDS CLARIFICATION: SCD/historization type not ruled -- owner ruling]`. Names Type 1 ("overwrite") and Type 2 ("track history") as the two options; decides neither (Clarify Q4). |
| Unknown-member row | FILLED (structural convention, RC14) | A row at `customer_sk = -1` representing an unresolved/unknown member, joinable via FK `COALESCE` -- the same convention `gold.dim_customer_rss` already uses and every other shipped dim in the star. |
| Identity-resolution cross-reference | FILLED (a pointer, not a mechanism) | States that resolving multiple raw ids to one `customer_sk` is a reserved owner ruling and links to `domains/customer.md`'s identity/grain stop (FR-005, User Story 3). Proposes no merge rule, matching heuristic, or precedence order. |

**Non-goal**: this entity is a DOCUMENT, not a database object. It produces no
DDL and is not itself consumed by `retail check`.

### CustomerDimensionTemplate

The new `templates/customer-dimension.md` copy-me artifact. Instantiates
`CustomerDimensionPattern`'s shape for a future table's mapping to adopt
(FR-001, FR-014). Same four slots as `CustomerDimensionPattern` above
(surrogate key, identity-key, PII-publish, SCD/historization), authored as a
fillable worksheet rather than expository prose.

| Field | Type | Notes |
|---|---|---|
| `customer_sk` | structural convention (filled) | RC14 surrogate key; a future table's map records the concrete generated-key mechanics in its own `source-map.yaml`, not here. |
| Identity-key slot | unresolved marker (to be filled by a future table's owner) | Copy-me placeholder; this template itself never fills it. |
| PII-publish slot | unresolved marker (to be filled by a future table's owner) | Copy-me placeholder; this template itself never fills it. |
| SCD/historization slot | unresolved marker (to be filled by a future table's owner) | Copy-me placeholder; this template itself never fills it. |
| Unknown-member row | structural convention (filled) | `-1` / `UNKNOWN`, RC14. |

**Citable, not merely descriptive (FR-014)**: this template is structured so a
future table's `source-map.yaml` `gold_star.dimensions[]` entry can reference
it BY NAME (e.g. a dimension entry citing "see
`templates/customer-dimension.md`" in an authoring comment) without copying
the template's prose into the map. It maps onto the EXISTING
`gold_star.dimensions[].name` / `.surrogate_key` / `.has_unknown_member` /
`.attributes[]` fields already defined in `templates/source-map.yaml` --
this feature adds no new key to that schema.

### CustomerGrainPattern

The new `docs/patterns/customer-grain-pattern.md` document. DOC-ONLY (Clarify
Q3: no copy-me grain template ships, because a template would instantiate a
CHOSEN grain, and which grain a table adopts is itself part of the reserved
rulings this feature must not make).

One entry per Planned customer KPI named in `domains/customer.md` (FR-003;
SC-002 requires exactly four, 0 decided):

| KPI (cited from `domains/customer.md`) | Candidate grain (OPTION, not a shipped default) | Structural FK join (FILLED, RC14) | Unresolved value (marker) |
|---|---|---|---|
| Customer Retention Rate | A periodic-snapshot grain: one row per customer per calendar period. | Keys to the customer dimension via `customer_sk`, COALESCE'd to `-1` for an unresolved/unknown member. | `[NEEDS CLARIFICATION: retention window not ruled -- owner ruling]` (the period length itself). |
| Purchase Frequency | The same periodic-snapshot grain family as retention (one row per customer per calendar period). | Keys to `customer_sk`, COALESCE'd to `-1`. | `[NEEDS CLARIFICATION: retention window not ruled -- owner ruling]` (frequency shares the same period-length ambiguity retention does; the doc states this rather than inventing a second period). |
| Customer Lifetime Value (CLV) | A customer-to-date grain: one row per customer, lifetime-to-date (not periodic). | Keys to `customer_sk`, COALESCE'd to `-1`. | `[NEEDS CLARIFICATION: CLV horizon not ruled -- owner ruling]` (horizon length and discounting choice). |
| New-vs-Returning Customer split | Depends on the first-purchase anchor: a periodic-snapshot grain classifying each period's customers against their anchor date. | Keys to `customer_sk`, COALESCE'd to `-1`. | `[NEEDS CLARIFICATION: anchor not ruled -- owner ruling]` (the first-purchase anchor rule itself). |

**Structural join fixed, semantic grain open (Clarify Q2, FR-003)**: every row
above fixes ONLY the join surface (a conformed dimension needs a documented
join, Principle III) -- it decides no period length, horizon, discount rate,
or anchor value. This is why the join column is marked FILLED while the grain
parameter itself carries the marker.

### IdentityKeySlot

A named-but-unfilled placeholder (appears in both `CustomerDimensionPattern`
and `CustomerDimensionTemplate`) marking where a table's confirmed customer
identity field goes once an owner rules it. The pattern and template never
name a candidate field. Filling this slot for a REAL table is that table's own
`mappings/<table>/unresolved-questions.md` decision, recorded there -- not in
these generic artifacts.

### PIIPublishSlot

A named-but-unfilled placeholder marking where a table's governance
publish-safety ruling goes. Default is neither "keep" nor "drop" at the
PATTERN level (each table's owner rules its own case, as
`retail_store_sales`'s Q1 did for itself -- see research.md). Filling this
slot for a real table is likewise that table's own mapping-gate decision.

### SCDHistorizationTypeSlot

A named-but-unfilled placeholder marking where a table's owner rules whether
the customer dimension is Type 1 (overwrite) or Type 2 (track history). The
pattern names both options and decides neither (Clarify Q4).

### IdentityResolutionStop

A documented cross-reference (not a mechanism) inside `CustomerDimensionPattern`
pointing a reader from the pattern to `domains/customer.md`'s reserved
identity/grain ruling. Not a new entity with its own file -- a section within
the dimension pattern document.

## Relationships

```text
skills/retail-kpi-knowledge/domains/customer.md   (SHIPPED, spec 042 -- READ-ONLY, cited)
        |
        |  cites 4 Planned KPIs + 4 Principle-V stops
        v
docs/patterns/customer-grain-pattern.md  (NEW, doc-only)      docs/patterns/customer-dimension-pattern.md  (NEW)
        |  one candidate-grain row per KPI                              |  surrogate key + 3 unresolved slots
        |  FK join fixed -> customer_sk, COALESCE -1                    |  + -1 unknown member + identity-resolution
        |                                                                |    cross-reference
        `------------------------------- both cite RC14/RC15 -----------'
                                          |
                                          v
                          templates/customer-dimension.md  (NEW, copy-me)
                                          |
                                          |  citable by name (FR-014), no new source-map.yaml key
                                          v
                     a FUTURE table's mappings/<table>/source-map.yaml
                     gold_star.dimensions[] entry (existing shape, unchanged schema)
                                          |
                                          |  that table's OWN owner fills the 4 slots
                                          |  (identity key, PII, SCD, + grain-pattern's
                                          |   retention/CLV/anchor values)
                                          v
                     that table's OWN mappings/<table>/unresolved-questions.md
                     records the filled decisions -- NOT this feature's artifacts
```

## Non-goals for this data model (YAGNI, matches spec.md Assumptions)

- No database table, column, or SQL DDL anywhere in this data model -- every
  shape above is a markdown/prose structure a human or agent reads.
- No numeric field, percentage, ratio, or "N of 4 KPIs covered" score anywhere
  (hard rule #9, FR-010, SC-004). Coverage is expressed only as "which slots
  are filled (generic, structural) vs. which remain an explicit owner ruling."
- No new key added to `templates/source-map.yaml`'s schema (FR-014's
  citability is achieved by naming convention, not a schema change).
- No `contracts/` file, no metric-contract shape, no `approvals[]` entry, and
  no `readiness-status.yaml` key (FR-009, FR-015). This data model produces
  nothing that changes what a stage's `pass` requires.
- No identity-resolution algorithm, matching heuristic, or precedence-order
  data structure (FR-005) -- `IdentityResolutionStop` is a cross-reference,
  not a resolvable ruleset.
