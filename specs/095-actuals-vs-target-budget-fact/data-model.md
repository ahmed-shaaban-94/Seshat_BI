# Data Model: Actuals-vs-Target (Budget) Fact + Variance Readiness

**Feature**: `specs/095-actuals-vs-target-budget-fact/` | **Phase**: 1 (design)

This is a documentation/pattern feature; there is no database schema or API
payload owned by this spec chain. "Data model" here means the **artifact
shapes** (Markdown/YAML structures) this feature introduces, and the
**hypothetical entities** the pattern document reasons about. Every shape
stays generic (Principle VII) -- no table-specific grain, value, or threshold
is baked into any of them.

## Entity: Target/Budget Fact (pattern only -- no real instance)

A hypothetical second Kimball fact, described by the pattern document but not
built by this feature.

| Field (conceptual, not a literal column list) | Meaning | Resolved-vs-open |
|---|---|---|
| Conformed dimension keys | The SAME dimension keys as the actuals star it will be compared against (RC14 discipline) | **Resolved structural default** -- stated as a MUST in the pattern doc, citing `docs/decisions/0002-retail-cleaning-defaults.md` |
| Grain | Commonly coarser than the actuals grain (e.g. month x store x category vs. transaction) | **OPEN, owner-supplied per table** -- pattern doc marks this `[NEEDS CLARIFICATION: target-fact grain is owner-supplied per table]`, never asserts a concrete grain |
| Measures | Planned/budgeted values at the target grain | **OPEN** -- no value, no column name is invented; the pattern only states measures exist, never their identity or magnitude |
| Version/as-of dimension | Whether a target fact needs one, to avoid silently overwriting a prior plan on a mid-period revision/reforecast | **OPEN, owner-supplied per table** -- the pattern flags the NEED to consider this; it does not mandate a scheme |

No real instance of this entity exists anywhere in the repo. This feature
authors zero SQL, zero migration, and zero mapping artifact for it (FR-018).

## Entity: Variance Metric (contract shape only -- no filled real contract)

The actual-vs-plan comparison (e.g. "Net Sales vs Target %"), described by a
FILLED PATTERN of the existing `templates/metric-contract.yaml` field set.
The shape below lists every field the F009 template already defines --
**zero new, zero renamed** (SC-005) -- annotated with how a variance metric
fills each one differently from a simple additive-sum metric.

| `metric-contract.yaml` field | How the variance-vs-target SHAPE fills it | Resolved-vs-open |
|---|---|---|
| `name` | A placeholder variance-metric name (e.g. `<VarianceMetricName>`, PascalCase, matching the template's own placeholder convention) | Placeholder (Principle VII) |
| `grain` | States the COMPARISON grain -- the (typically coarser, target-side) grain at which actuals are rolled up to meet targets -- as a description, not a concrete per-table value | **Resolved structural default**: comparison happens at the coarser grain (FR-004). **Open**: which specific dimensions any real table's rollup uses |
| `formula_intent` | Plain-language statement of the non-additive rule: aggregate actuals and targets SEPARATELY at the comparison grain, then recompute the ratio -- never average two pre-computed percentages. ALSO carries, in plain language, which second gold table (the target fact) this metric compares against, since `binds_to` only names one table (see the two-table note below) | **Resolved structural default**, citing `targets-and-budgets.md` (FR-003) |
| `owner` | A placeholder owner role (e.g. `<named metric owner>`, matching the template's own placeholder) | Placeholder (Principle VII) |
| `binds_to.gold_table` | The PRIMARY (actuals) gold table only -- the template's existing single-table shape is used as-is, never forked into a list | **Resolved-by-fit**; the SECOND (target) table's identity is carried in `formula_intent` and flagged via an inline `#` comment as an open note for human/F009-owner review (FR-007; research.md Sec 5) -- not a silent fit |
| `binds_to.columns` | The actuals-side measure column(s) this metric reads | Placeholder, matching template convention |
| `binds_to.pii_sensitive` | `false` by default (a variance-of-sales-totals metric is not typically PII-derived), same as the template's own default | Resolved-by-fit; a real table's actual PII status is that table's own determination |
| `readiness.status` | `blocked`, because a filled real contract cannot resolve to `pass` while RAG thresholds and grain remain unset | **Resolved structural consequence** of the two OPEN items below -- not itself an open item |
| `readiness.blocking_reasons` | A REQUIRED entry naming the missing-target case (FR-008) AND a REQUIRED entry naming the missing RAG threshold (FR-009) -- both explicit, both non-empty, never silently defaulted | **Resolved structural default**: these MUST be present whenever they apply, per the pattern; their content stays a marker, not a value |
| `ambiguities[]` | An entry pattern for the missing-target case (a dimension member with no corresponding target row MUST be flagged, never defaulted to 0%), following the EXISTING `id / decision_status / ruling / evidence / number_moving` shape the template already defines -- no new ambiguity-ledger field | **Resolved structural default** (FR-005, FR-008), citing `targets-and-budgets.md`'s own named ambiguity |
| (no field for RAG threshold) | The template has no dedicated RAG field; a RAG threshold, if ever recorded, would live as `evidence[]` on a filled contract once an owner supplies it -- the shape shows WHERE, not a value | **OPEN, owner-supplied business policy** -- marked `[NEEDS CLARIFICATION: RAG thresholds are owner-supplied business policy, not a kit default]` (FR-009) |

### The two-table `binds_to` tension (see research.md Sec 5 for the full resolution)

`metric-contract.yaml`'s `binds_to` block is scalar-shaped for ONE gold
table. A variance metric structurally needs two (the actuals fact and the
target fact) at their comparison grain. The shape resolves this WITHOUT
adding a field: it fills `binds_to.gold_table` with the actuals table (fitting
the existing shape), names the target table in `formula_intent`, and adds an
inline `#` comment flagging this as an open note for human/F009-owner review.
This feature does NOT decide whether F009 should someday grow a multi-table
`binds_to` shape -- that decision, if ever made, belongs to a future F009
amendment, not to this pattern-and-shape feature.

## Entity: Comparison Grain

The (typically coarser, target-side) grain at which actuals are rolled up to
meet targets for a valid comparison.

| Aspect | Statement | Resolved-vs-open |
|---|---|---|
| Direction of rollup | Actuals are rolled up to match the target grain; targets are NEVER disaggregated to match actuals | **Resolved structural default** (FR-004; Edge Cases) |
| Specific dimensions used | Which dimensions a real table's comparison rollup actually uses (e.g. month x store, or month x store x category) | **OPEN, owner-supplied per table** -- never asserted generically |

## Entity: Missing-Target Case

A dimension member present in the actuals star with no corresponding target
row (e.g. a store opened mid-year with no budget yet, or a new product with no
target).

| Aspect | Statement | Resolved-vs-open |
|---|---|---|
| Required handling | MUST be surfaced as an explicit flag -- never a silent 0% or blank variance | **Resolved structural default**, citing `targets-and-budgets.md`'s own named ambiguity (FR-005, FR-008) |
| Dashboard visualization of the flag | How a specific table's dashboard should visually represent the flag | **Out of scope here** -- a dashboard-design decision, not this feature's (Edge Cases) |

## Entity: Second Worked-Example Section

The new narrative content (Principle VII genericity proof) applying the
pattern to `retail_store_sales`'s existing conformed dimensions.

| Field | Content | Source of truth (verbatim, never invented) |
|---|---|---|
| Referenced actuals fact | `gold.fct_sales_rss` | `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` |
| Referenced conformed dimensions | `dim_customer_rss`, `dim_product_rss`, `dim_payment_method_rss`, `dim_location_rss`, `dim_date_rss` | `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` (copied verbatim; SC-006) |
| Readiness framing for a `retail_store_sales` target fact | `not_started` -- no target fact, no mapping artifact, no readiness-status record exists yet for this table | Honest statement per FR-016; hard rule #9 (no fabricated score) |
| Fabricated content | NONE -- zero target values, zero variance figures, zero RAG assignments anywhere in the section | FR-012; SC-002 |
| Restart framing | Building a real target fact for `retail_store_sales` restarts the mapping gate at Mapping Ready for the NEW target source; the existing actuals star's Gold Ready / Dashboard Ready status does NOT extend to an unbuilt target fact | FR-013 |

## Entity: Open Principle-V Item (the ledger FR-019 requires)

A tracked list, appearing in BOTH the pattern document and the contract
shape, separating already-resolved structural defaults from open judgment
calls a future owner must supply. This is not a new template -- it is a
content requirement (FR-019) on the two artifacts above.

| Item | Category | Where it appears |
|---|---|---|
| Conformed dimension keys (RC14 reuse) | Resolved structural default | Pattern document |
| Non-additive variance calculation | Resolved structural default (cites `targets-and-budgets.md`) | Pattern document |
| Comparison happens at coarser grain | Resolved structural default | Pattern document |
| Missing-target must be flagged, never defaulted | Resolved structural default (cites `targets-and-budgets.md`) | Pattern document + contract shape |
| Target-fact grain | **OPEN**, owner-supplied per table | Pattern document (`[NEEDS CLARIFICATION: target-fact grain is owner-supplied per table]`) |
| RAG (red/amber/green) numeric thresholds | **OPEN**, owner-supplied business policy | Contract shape (`[NEEDS CLARIFICATION: RAG thresholds are owner-supplied business policy, not a kit default]`) |
| Version/as-of dimension for reforecasts | **OPEN**, owner-supplied per table | Pattern document |

## Relationships

```text
Domain doc (targets-and-budgets.md, Planned/needs-target-fact)
  --(names the gap)-->  Target/Budget Fact (pattern only)
  --(names the gap)-->  Variance Metric (contract shape only)

Target/Budget Fact (pattern)  --(conforms to)-->  SAME dims as an existing actuals star
  (e.g. dim_customer_rss, dim_product_rss, ... from 0004_*.sql, in the 2nd worked example)

Variance Metric (contract shape)
  --(reads, per the two-table tension)-->  Actuals gold fact (binds_to.gold_table)
  --(reads, named in formula_intent + flagged)-->  Target gold fact (NOT a binds_to field)
  --(compared at)-->  Comparison Grain (coarser, target-side)
  --(must flag)-->  Missing-Target Case (never defaulted to 0%)
  --(defers)-->  RAG threshold (owner-supplied; blocked until supplied)

Second Worked-Example Section
  --(applies pattern + shape to)-->  retail_store_sales' EXISTING conformed dims
  --(states honestly)-->  not_started (no target fact exists for this table today)
```

No entity in this feature is mutable state this spec chain writes to. The
pattern document, the contract shape, and the second worked-example section
are the only artifacts this feature's IMPLEMENT stage produces; a REAL
target/budget fact for any table is a separate, later, unnumbered feature
(spec.md Assumptions).
