# Data Model: Promotion/Markdown Fact and Factless-Fact Coverage Pattern

**Feature**: `specs/097-promotion-markdown-factless/` | **Phase**: 1 (design)

This feature introduces no database schema and no application data model. Per
Principle VII, everything below is a GENERIC artifact SHAPE (the illustrative
Markdown/YAML structure the pattern doc and template will show at implement
stage) -- never a concrete table's grain, column set, or value. No entity
here is a row in a real database; each is a documented PATTERN a future
adopting table fills in through the unchanged source-mapping gate.

## Entity 1: Promotion/markdown fact (pattern)

A documented, measure-bearing Kimball fact shape (FR-005), distinct from the
factless coverage fact (Entity 2) so the two are never conflated.

**Shape (illustrative `gold_star.fact` block, mirroring `templates/
source-map.yaml`'s convention):**

```yaml
gold_star:
  fact:
    name: "fct_<promotion_grain>"          # placeholder; adopting table names its own
    grain: "<= meta.grain>"                # e.g. "one row per promotion line per store per day" -- adopter decides
    measures:                              # RC9: independent additive measures
      - "<markdown_amount>"                # e.g. a markdown-amount-shaped measure
      - "<promoted_units>"                 # e.g. a promoted-units-shaped measure
      # - "<promotion_line_count>"         # optional; a promotion-count measure
  dimensions:
    - name: "dim_product"                  # CONFORMED -- reused, not re-created (FR-006)
    - name: "dim_store"                    # CONFORMED
    - name: "dim_date"                     # CONFORMED
```

**Fields / attributes**:
- `grain` -- a placeholder-only candidate (e.g. "one row per promotion line
  per day per store"); the actual grain is an adopting-table mapping-gate
  decision (Principle V), never fixed by this feature (FR-005, FR-009).
- `measures[]` -- at least one additive measure placeholder is REQUIRED for
  this shape (this is what distinguishes it from Entity 2); concrete measure
  names, units, and formulas are an adopter decision.
- `dimensions[]` -- MUST name product, store/location, and date as CONFORMED
  (reused from an existing sales star, never re-minted); cites spec 087 /
  HR1 as the pending mechanism that would eventually verify that conformance
  (FR-006), without this feature adding or wiring that mechanism.

**Relationships**: joins to the same conformed `dim_product` / `dim_store` /
`dim_date` an existing sales star already carries. Does not require the
factless coverage fact to exist, and vice versa (Edge Cases: the two patterns
are independently adoptable).

## Entity 2: Factless coverage fact (pattern)

A documented Kimball fact shape recording that a (product, store, day,
promotion) COMBINATION held true, independent of whether a sale happened --
carrying NO required additive measure (FR-004). This is the feature's central
new concept: still a valid Kimball star (fact + conformed dimensions,
Principle III) because it retains the fact-plus-conformed-dims shape; what it
lacks is a measure, not a dimension.

**Shape (illustrative `gold_star.fact` block -- the defining structural
difference from every other fact template in the repo):**

```yaml
gold_star:
  fact:
    name: "fct_<coverage_grain>"           # placeholder
    grain: "<= meta.grain>"                # e.g. "one row per product per store per day that was on promotion" -- adopter decides
    measures: []                           # DEFERRED -- see Clarification Q2. Empty by design.
    # Authoring note: COUNT(*) over this fact's rows is a valid read
    # ("how many combinations were on promotion") without being a stored
    # measure column. Do NOT add a fabricated "coverage_count" column here
    # (see Edge Cases in spec.md) -- that would misrepresent the fact's
    # nature by inventing a quantity the source does not provide.
  dimensions:
    - name: "dim_product"                  # CONFORMED -- same instance the sales star uses
    - name: "dim_store"                    # CONFORMED
    - name: "dim_date"                     # CONFORMED
  degenerate_dimensions:
    - "<promotion_id>"                     # if the source has a promotion/markdown identifier with no attributes
```

**Fields / attributes**:
- `measures: []` -- MUST be empty (Clarification Q2 resolution: the shipped
  template shows `measures: []`, not a documented-degenerate marker column,
  so SC-002's "zero required entries" is unambiguous to verify by inspection).
- `grain` -- a placeholder-only candidate combination (product x store x day
  x promotion); overlap-handling (more than one promotion active on the same
  combination, or a partial-day promotion) is an adopting-table mapping
  decision this pattern flags, not answers (Edge Cases).
- `dimensions[]` -- the SAME conformed product/store/date dimensions the
  promotion/markdown fact (Entity 1) and an existing sales star already use.

**Relationships**: this is the entity that Entity 3 (the anti-join
mechanism) operates against. It exists independently of whether a matching
sales-fact row exists -- that independence is the entire reason it is needed
(FR-003).

## Entity 3: Anti-join mechanism (pattern)

The documented LEFT ANTI JOIN (or equivalent set-difference) between the
factless coverage fact (Entity 2) and an existing sales fact, on their shared
conformed dimensions, that answers "on promotion but did not sell." A
described TECHNIQUE, not an executed query (FR-003, Clarification Q3).

**Shape (illustrative, non-executable SQL sketch -- placeholder names only,
never run or proposed as a migration; FR-011)**:

```sql
-- ILLUSTRATION ONLY -- not a proposed or runnable migration (Principle VIII, FR-011).
-- Generic placeholder names throughout; no real table/column/promotion name.
SELECT
    coverage_fact.product_sk,
    coverage_fact.store_sk,
    coverage_fact.date_sk
FROM coverage_fact
LEFT JOIN sales_fact
    ON  sales_fact.product_sk = coverage_fact.product_sk
    AND sales_fact.store_sk   = coverage_fact.store_sk
    AND sales_fact.date_sk    = coverage_fact.date_sk
WHERE sales_fact.product_sk IS NULL;   -- equivalent to a LEFT ANTI JOIN
```

**Preconditions this pattern names explicitly**:
- The two facts MUST share a conformed, grain-compatible key on every joined
  dimension. When they do not (e.g. the promotion source only has a category,
  not a product key), the pattern names this as a blocking mapping-gate
  question for the adopting table to resolve -- never an invented crosswalk
  (Edge Cases).
- "Did not sell" is illustrated as "zero recorded sale rows for that
  combination" (a plain anti-join). A "sold below baseline" definition is the
  same baseline-rule gap the Promotion Uplift % KPI is already Planned
  pending, and stays a future, separate decision (Edge Cases, spec.md
  Assumptions).

**Relationships**: reads Entity 2 (factless coverage fact) and an EXISTING
sales fact (e.g., illustratively, the shape `docs/worked-examples/
retail-store-sales.md` demonstrates -- cited once, never restated with real
names) on their shared conformed dimensions (Entity 1's `dimensions[]` list
is the same set).

## Entity 4: Factless-fact template (artifact)

The new copy-me file this feature adds under `templates/` (authored at
implement stage; this plan stage documents its intended shape only). Mirrors
`templates/source-map.yaml`'s authoring-notes convention (a commented header
explaining WHAT the file is and WHICH sections of this pattern doc it
formalizes) and its `gold_star`-shaped body, adapted for the no-measure case.

**Structure** (top-level keys, matching `source-map.yaml`'s section set so a
reader already familiar with that file recognizes the pattern immediately):

| Section | Same as `source-map.yaml`? | Notes for the factless case |
|---|---|---|
| Header comment block | Yes (same convention) | Explains this is the factless-fact variant; cross-references `docs/patterns/promotion-markdown-factless.md`. |
| `meta:` (table_id, source_system, profiled_from, grain, primary_key, reviewed_by, reviewed_on) | Yes, unchanged shape | `grain` here is the coverage combination (product x store x day x promotion); `primary_key` is the composite of the conformed dimension keys plus the promotion identifier. |
| `defaults:` (adopted / deviations) | Yes, unchanged shape | An adopting table still records only its RC deviations here, exactly as any other table. |
| `columns:` | Yes, unchanged shape | Every source column still gets an entry (keep/drop/derive); a factless source typically has NO money/quantity column to keep as `fact_measure` -- if one exists, the authoring note flags that its presence may mean this is actually a measure-bearing promotion fact (Entity 1), not a factless fact. |
| `gold_star.fact.measures` | **Different**: `[]` (empty), never populated | This is the one structural difference this template exists to show (FR-004, SC-002). |
| `gold_star.dimensions` | Yes, unchanged shape | MUST list the same conformed dimensions (product/store/date) an existing sales star uses -- an authoring note reminds the filler to reuse names, not re-mint them. |
| `derived_columns:` | Yes, unchanged shape | Unused in the common case (a factless fact rarely derives a new column); left as an empty/commented section. |

**Validation rule this template's own authoring note states** (not a
`retail check` rule -- a documented convention only, FR-007): `measures: []`
must stay empty; a `COUNT(*)` over the fact's rows is the valid substitute
read, documented inline as a comment, never materialized as a stored column
(Clarification Q2).

## Non-entities (explicitly out of scope for this data model)

- No real table's grain, primary key, or column list (FR-009).
- No promotion mechanics taxonomy (discount type, funding source, campaign
  hierarchy) beyond the generic placeholders shown above (FR-008).
- No metric contract, KPI formula, or status change for Discount Amount /
  Discount Rate % / Promotion Uplift % (FR-010).
- No `readiness-status.yaml` key, no `retail check` rule id, no rule-registry
  entry (FR-007).
- No numeric confidence/health/maturity score or completeness count anywhere
  in this data model or its downstream artifacts (FR-014, hard rule #9).
