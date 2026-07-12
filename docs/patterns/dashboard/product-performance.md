# Dashboard Pattern: Product Performance

**Status of this document**: a GENERIC dashboard-design pattern (spec 123, US3).
It supplies design GUIDANCE ONLY -- suitable audiences, intended purpose, common
question families, metric ROLES (not named metrics), a common page structure,
recommended visual roles, expected action paths, and common design risks. It
defines NO KPI, NO formula, NO DAX, and NO tenant-specific business logic. A
report that adopts this pattern still authors its own Report Intent
(`templates/report-intent.yaml`), page blueprints, and visual specs, and still
resolves every metric role to an APPROVED metric contract (F009) by name --
never invents one (FR-003/FR-013).

**How this is used**: the pattern-recommendation workflow
(`.claude/skills/powerbi-dashboard-design/workflows/pattern-recommendation.md`)
proposes this pattern (alongside any other fitting pattern) when a committed
Report Intent's `purpose` matches. The human accepts, adapts, or rejects it
(FR-014); nothing here is auto-applied.

## Suitable audiences

- Category / product manager (the primary reader).
- Merchandising or assortment planning analyst.
- Executive interested in product-mix contribution as a secondary reader.

## Intended purpose

`analytical_exploration` (primary) with a `diagnostic` component -- explores
performance across the product hierarchy (category/sub-category/item) to
understand which products contribute, and why.

## Common question families

- "Which products/categories are the top and bottom contributors to the
  outcome?"
- "How is the product mix shifting over time?"
- "Which products are growing/declining fastest, and is that broad or
  concentrated?"
- "Which products should get more/less shelf, marketing, or buying
  attention?"

## Metric roles (roles, not named metrics)

- **Outcome role(s)**: a contribution/performance outcome per product
  (e.g. "the per-product performance outcome").
- **Driver role(s)**: metrics explaining a product's movement (e.g. a
  volume driver, a price/mix driver, a distribution/availability driver).
- **Guardrail role**: optional; a metric that should not be sacrificed while
  optimizing product mix (e.g. a margin guardrail alongside a volume-outcome
  focus).

## Common page structure

1. `header` -- title + period context + product-hierarchy level selector
   (category/sub-category/item).
2. `kpi_strip` (light) -- headline mix/contribution outcome metrics.
3. `main_insight` -- a ranked or hierarchical visual (e.g. a Top/Bottom-N or
   treemap-style role) showing product contribution.
4. `diagnostic` -- trend-over-time and mix-shift breakdowns supporting the
   main insight.
5. `exception_detail` -- row-level product detail for drill-down.
6. `filter_rail` -- category/sub-category/product slicers.
7. `footer_status` -- data-as-of / refresh note.

## Recommended visual roles

- A ranked bar/column or hierarchical (treemap/matrix) role for product
  contribution.
- A trend-line role for mix-shift-over-time.
- A detail-table role for item-level drill-down (kept in `exception_detail`).
- Hierarchy-aware slicer roles (category/sub-category/item), contained in
  `filter_rail`.

## Expected action paths

- Drill from category to sub-category to item (a natural hierarchy
  drill-through), matching the product hierarchy the semantic model exposes.
- A callout naming the top gaining/declining product(s) (`key_exception`),
  human-supplied.
- A recommended-action narrative slot for merchandising decisions (e.g. "give
  attention to X"), human-supplied -- never an auto-generated business
  recommendation.

## Common design risks

- **Flat list instead of ranked/hierarchical view**: an unranked, unsliced
  product list defeats the "which products matter" question; prefer a
  ranked or hierarchical presentation.
- **Mix shift without a driver**: showing that mix changed without any
  driver-role breakdown explaining why is an `incomplete` finding when this
  pattern also carries a diagnostic component.
- **Too granular a default view**: opening at item level for a large catalog
  overwhelms the reader; default to a higher hierarchy level with drill-down
  available, not the reverse.
- **Unavailable product hierarchy level**: if the subject area's semantic
  model lacks a hierarchy level the pattern assumes (e.g. no sub-category
  attribute), surface the gap via `retail dashboard-gaps` -- never
  approximate a hierarchy level that isn't mapped.
