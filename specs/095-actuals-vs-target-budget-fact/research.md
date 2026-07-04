# Research: Actuals-vs-Target (Budget) Fact + Variance Readiness

**Feature**: `specs/095-actuals-vs-target-budget-fact/` | **Phase**: 0 (research)

This is documentation research, not code research: what already-shipped
artifacts this feature must reuse, what it must stay distinct from, and what
capabilities are explicitly NOT assumed. Every claim below cites the artifact
it rests on (real repo paths).

## 1. Precedent survey -- what SHIPPED artifacts this feature reuses

| Shipped artifact | Real repo path | What this feature reuses from it |
|---|---|---|
| The domain-knowledge doc that names the gap | `skills/retail-kpi-knowledge/domains/targets-and-budgets.md` | The decision question ("Are we hitting our sales target?"), the KPI name ("Net Sales vs Target %"), its `Planned (needs target fact)` status, and the four named ambiguities (grain match, calendar alignment, missing targets, filter-scope parity). This feature CITES these verbatim; it does not re-derive or restate them as new invented guidance (FR-003, FR-005). |
| The metric-contract mechanism (F009) | `templates/metric-contract.yaml` | The exact field set (`name`, `grain`, `formula_intent`, `owner`, `binds_to.{gold_table, columns, pii_sensitive}`, `readiness.{status, evidence, blocking_reasons}`, `ambiguities[]`) that the variance contract shape must match with zero new/renamed fields (FR-006, SC-005). Also reuses its stop-and-ask triggers list (business rollup, grain ambiguity, PII) verbatim as the pattern for a fourth trigger this feature documents (missing-target). |
| The first, and so far only, worked example | `docs/worked-examples/retail-store-sales.md` | Its section-structure convention ("copy this section structure... fill each section's Evidence from that table's own artifacts") is the template the second worked-example narrative follows, per Principle VII's own guidance that there is no separate blank worked-example template file (precedent already established by `specs/084-worked-example-factory/data-model.md` item 13). This feature also reuses its Readiness-at-a-glance table shape (`status` + one-line evidence) for the second narrative's honest `not_started` framing. |
| The committed gold star this feature grounds its second example in | `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` | The exact, committed conformed-dimension names (`dim_customer_rss`, `dim_product_rss`, `dim_payment_method_rss`, `dim_location_rss`, `dim_date_rss`) and the fact table name (`gold.fct_sales_rss`) that the second worked example cites verbatim (FR-011, SC-006) -- never invents a dimension name. |
| The RC14 conformed-dimension discipline | `docs/decisions/0002-retail-cleaning-defaults.md` (RC14 -- "Gold is a Kimball star: one fact at the silver grain + conformed dims") | The pattern document's core structural claim (FR-001): a target/budget fact MUST reuse the SAME dimension keys as the actuals star it compares against, rather than growing a parallel, non-conformed dimension set. |
| The Constitution's stop-and-ask discipline | `.specify/memory/constitution.md` Principle V | The obligation that grain, RAG thresholds, and versioning stay owner-supplied and are recorded as `[NEEDS CLARIFICATION]` rather than resolved by this feature (FR-002, FR-009, FR-019). |
| The four-status readiness vocabulary | `.specify/memory/constitution.md` "Readiness System" section; `templates/readiness-status.yaml` | The exact four statuses (`not_started \| blocked \| warning \| pass`) used honestly in the second worked example's framing (FR-016) -- no numeric score anywhere (hard rule #9). |
| A recent same-shape docs-only plan (style + Constitution Check table precedent) | `specs/084-worked-example-factory/plan.md`, `research.md`, `data-model.md` | The table-format Constitution Check, the ASCII-tree Project Structure convention, and the "this is documentation research, not code research" framing this research.md follows. |

## 2. Precedent survey -- what this feature must stay DISTINCT from (boundary)

Per the spec's own "Boundary against neighbouring shipped work" section, three
shipped surfaces are cited, read, and extended ALONGSIDE, never edited:

| Surface | Path | Why it stays untouched |
|---|---|---|
| The first worked example | `docs/worked-examples/retail-store-sales.md` | It already traverses the full seven-stage spine for the ACTUALS star; this feature adds a genuinely SECOND, separate narrative file rather than re-narrating or appending to this one (FR-011, FR-015). |
| The metric-contract template | `templates/metric-contract.yaml` | It already defines the contract mechanism generically; this feature authors a FILLED PATTERN of it as a new, separate file, never forking or adding a field to the template itself (FR-006, FR-015). |
| The targets/budgets domain doc | `skills/retail-kpi-knowledge/domains/targets-and-budgets.md` | Flipping its `Planned` marker is reserved for whoever ships the first REAL target-fact table -- out of scope here per the collision-avoidance allocation (FR-015). |

No other shipped surface is at risk of collision: a repo-wide search for
existing "target" or "budget" fact patterns (`docs/patterns/`, `templates/`)
confirms `docs/patterns/target-budget-fact.md` and
`templates/metric-contract-shape.variance-vs-target.yaml` do not yet exist --
this feature is additive only, no overwrite.

## 3. Input-source confirmation

The feature's only inputs are already-committed repository text, confirmed
present and read during this research pass:

- `skills/retail-kpi-knowledge/domains/targets-and-budgets.md` -- exists, read
  in full (Overview, KPI table, ambiguities, notes).
- `templates/metric-contract.yaml` -- exists, read in full (every field, every
  authoring-notes block, the optional `definition` block).
- `docs/worked-examples/retail-store-sales.md` -- exists, read (header,
  "Readiness at a glance" table, Sec 1-2 structure).
- `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` -- exists,
  read in full; the five conformed dimension names and the fact table name are
  copied verbatim from this file, not from memory or inference.
- `docs/decisions/0002-retail-cleaning-defaults.md` -- exists; RC14 confirmed
  present ("Gold is a Kimball star: one fact at the silver grain + conformed
  dims").
- `.specify/memory/constitution.md` -- exists at version 1.7.0; Principles
  I, III, IV, V, VI, VII, VIII, IX and the Readiness System section confirmed
  present and read in full.

No external (non-repo) source is consulted. No target/budget data file, no
finance-supplied plan, and no live database connection is available or sought
-- confirmed absent by design (spec.md Assumptions): "No live database,
target-data file, or real budget figure is available or will be sought during
this feature."

## 4. Deferred capabilities NOT assumed

This feature explicitly does NOT assume the following exist or are reachable,
and authors nothing that depends on them:

- **F016 (Power BI execution adapter)** does not exist and is not assumed
  reachable. No dashboard, publish-layer, or RAG-visualization consequence of
  a variance metric is addressed here -- RAG *visualization* is a later,
  separate dashboard-design concern (spec.md Assumptions; Constitution
  Principle II: the adapter is execution-only and gated on Semantic Model
  Ready, which this feature does not advance for any real table).
- **No live database connection.** Per Constitution Principle VIII
  (static-first, live-deferred), this feature authors zero SQL, zero
  migration, zero `retail validate` run, and zero live profiling. Unlike a
  feature that touches a live surface and marks its unmeasured numbers
  `[PENDING LIVE PROFILE]`, this feature has NO live surface to defer at all --
  there is nothing to mark pending because nothing here connects to, queries,
  or assumes a database exists. The only deferred markers this feature uses
  are the Principle-V `[NEEDS CLARIFICATION]` markers (grain, RAG thresholds,
  versioning), which are business-policy deferrals, not live-data deferrals.
- **No new readiness stage, four-status gate, or `retail check` rule.** This
  feature rides the EXISTING seven-stage spine and the EXISTING F009 contract
  mechanism only (collision-avoidance allocation, FR-014). No file under
  `src/retail/rules/` is added or edited; `docs/rules/rules-manifest.json` is
  unaffected.
- **No real target/budget table build.** No `mappings/<table>/` directory, no
  `warehouse/migrations/*.sql` for a target fact, no `readiness-status.yaml`
  entry, and no `powerbi/*.SemanticModel/` change is authored for
  `retail_store_sales` or any other table. A real per-table target/budget-fact
  build is a separate, later feature that would walk the existing
  `source-mapping` -> `retail-build-warehouse` -> `retail-validate` sequence
  (spec.md Assumptions).
- **No target VALUE, variance percentage, or RAG threshold anywhere.**
  Every such number is owner-supplied (Principle V) and, until supplied, is
  represented only as an explicit `[NEEDS CLARIFICATION]` marker -- never
  estimated, defaulted, or placeholder-filled (FR-010, SC-002).

## 5. The `binds_to` two-table tension (the delicate design point)

`templates/metric-contract.yaml`'s `binds_to` block is a single scalar
`gold_table:` plus a `columns:` list -- designed for a metric that reads ONE
gold table. A variance metric structurally reads TWO gold tables (the actuals
fact and the target fact) at their comparison grain.

**Resolution adopted (per FR-006/FR-007 and SC-005's "0 new/renamed fields"
bar):** the contract shape does NOT add a field, does NOT turn `gold_table`
into a list, and does NOT fork the template. Instead it:

1. Fills `binds_to.gold_table` with the PRIMARY (actuals) gold table, exactly
   as the template's existing single-table shape expects.
2. Records the target gold table's identity in `formula_intent` (plain
   language: "compares gold.<actuals_fact> against gold.<target_fact> at the
   comparison grain") -- intent, not a new structured field.
3. Adds an inline `#` comment at the `binds_to` block (per the Clarifications'
   resolved file-format decision) that explicitly flags the two-table need as
   an OPEN NOTE for human/F009-owner review, rather than silently forcing a
   fit or inventing a second `gold_table` key.

This keeps SC-005 mechanically checkable (a diff of the shape's top-level and
nested keys against `metric-contract.yaml`'s keys shows zero additions) while
still surfacing the real structural gap for a human to decide whether F009
itself needs a future multi-table `binds_to` shape -- a decision this feature
explicitly does NOT make (FR-007: "flag... as an open note for human/F009-owner
review, rather than silently forcing a fit").

## Sources cited in this research

- `skills/retail-kpi-knowledge/domains/targets-and-budgets.md`
- `templates/metric-contract.yaml`
- `docs/worked-examples/retail-store-sales.md`
- `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`
- `docs/decisions/0002-retail-cleaning-defaults.md` (RC14)
- `.specify/memory/constitution.md` (Principles I, III, IV, V, VI, VII, VIII,
  IX; Readiness System section)
- `specs/084-worked-example-factory/plan.md`, `research.md`, `data-model.md`
  (style + structure precedent for a docs-only feature)
- `specs/095-actuals-vs-target-budget-fact/spec.md` (this feature's own,
  now-clarified spec)
