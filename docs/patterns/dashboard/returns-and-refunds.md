# Dashboard Pattern: Returns & Refunds

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

- Customer service / returns operations manager (the primary reader).
- Quality or category manager investigating a return-rate spike.
- Finance stakeholder assessing refund exposure.

## Intended purpose

`monitoring` (primary) with a `diagnostic` component -- watches a
return/refund rate outcome and, when it moves, supports asking why.

## Common question families

- "What is the current return/refund rate, and is it trending up or down?"
- "Which products/categories/locations have unusually high return rates?"
- "What are the most common reasons behind returns, where reason data
  exists?"
- "What is the financial exposure from returns/refunds this period?"

## Metric roles (roles, not named metrics)

- **Outcome role(s)**: a return/refund-rate outcome and/or a refund-value
  outcome.
- **Guardrail role**: a rate or value threshold that should not be breached
  (e.g. a return-rate guardrail relative to a historical or target band).
- **Driver role(s)**: optional -- a reason-code or product/category driver
  breakdown, when the subject area has committed reason data; this role is
  frequently a GAP (see risks below) rather than something every subject
  area can supply.

## Common page structure

1. `header` -- title + period context.
2. `kpi_strip` -- headline return-rate and/or refund-value outcome metrics,
   each with a comparison (vs prior period, vs target/guardrail band).
3. `main_insight` -- a trend visual of the return/refund outcome over time.
4. `diagnostic` -- breakdowns by product/category/location, and by reason
   code if available.
5. `exception_detail` -- row-level detail for specific high-return
   products/locations or individual return transactions, if needed.
6. `filter_rail` -- product/category/location/reason slicers.
7. `footer_status` -- data-as-of / refresh note.

## Recommended visual roles

- KPI-card role for the return-rate and/or refund-value outcome(s).
- A trend-line role for the main insight.
- Breakdown-chart roles (bar/column) for product/category/location and
  reason-code cuts.
- A detail-table role for row-level exception inspection.

## Expected action paths

- Drill from a high-return product/category/location into row-level detail.
- A callout naming the top driver of a return-rate spike, where reason data
  supports it (`key_exception`).
- An escalation path to quality/vendor management for a persistent
  above-guardrail return rate, if the report's intent includes that action.

## Common design risks

- **Reason-code driver assumed but unavailable**: many subject areas record
  that a return happened but not why -- assuming a reason-code breakdown
  exists without verifying the field is mapped is this pattern's most common
  overreach; surface it as a gap via `retail dashboard-gaps`, never
  fabricate reason categories.
- **Rate without volume context**: a return RATE shown without also
  indicating the underlying volume can mislead (a high rate on a tiny base is
  a different risk than a high rate on a large base) -- pair rate and volume
  context where the model supports it.
- **No guardrail band**: a return-rate trend shown with no threshold/band
  context leaves the reader unable to judge "is this a problem" -- avoid a
  bare trend line with no reference band.
- **Financial exposure conflated with volume**: return count and refund
  value answer different questions; keep them as distinct outcome roles
  rather than one blended metric.
