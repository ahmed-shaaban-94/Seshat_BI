# Dashboard Pattern: Promotion Effectiveness

**Status of this document**: a GENERIC dashboard-design pattern (spec 123, US3).
It supplies design GUIDANCE ONLY -- suitable audiences, intended purpose, common
question families, metric ROLES (not named metrics), a common page structure,
recommended visual roles, expected action paths, and common design risks. It
defines NO KPI, NO formula, NO DAX, and NO tenant-specific business logic. A
report that adopts this pattern still authors its own Report Intent
(`templates/report-intent.yaml`), page blueprints, and visual specs, and still
resolves every metric role to an APPROVED metric contract (F009) by name --
never invents one (FR-003/FR-013). Where this pattern needs a promotion/markdown
factless-style structural input, it refers to the existing generic modelling
pattern `docs/patterns/promotion-markdown-factless.md` (data-modeling layer,
distinct from this design layer) rather than restating that structure here.

**How this is used**: the pattern-recommendation workflow
(`.claude/skills/powerbi-dashboard-design/workflows/pattern-recommendation.md`)
proposes this pattern (alongside any other fitting pattern) when a committed
Report Intent's `purpose` matches. The human accepts, adapts, or rejects it
(FR-014); nothing here is auto-applied.

## Suitable audiences

- Marketing / promotions manager (the primary reader).
- Category manager evaluating whether to repeat or retire a promotion.
- Finance stakeholder assessing promotional spend efficiency.

## Intended purpose

`diagnostic` (primary) with an `analytical_exploration` component -- did a
promotion work, and why (or why not)? This pattern requires a comparison
baseline (a non-promoted period or a control group) to be meaningful.

## Common question families

- "Did the promotion lift the outcome versus a non-promoted baseline?"
- "Which products/locations benefited most from the promotion?"
- "Was the lift incremental, or did it just pull forward demand from
  adjacent periods (cannibalization)?"
- "Was the promotion's cost/margin impact justified by the lift?"

## Metric roles (roles, not named metrics)

- **Outcome role**: an incremental-lift outcome (promoted-period result
  compared against a defined baseline).
- **Driver role(s)**: metrics that explain where the lift came from (e.g. a
  product-mix driver, a location/channel driver, a new-vs-existing-customer
  driver).
- **Guardrail role**: a margin or promotional-cost guardrail -- lift without
  a guardrail check risks reporting a promotion as a success when it eroded
  profitability.

## Common page structure

1. `header` -- title + the specific promotion/period being evaluated +
   baseline definition.
2. `kpi_strip` -- headline lift outcome metric(s), each explicit about its
   comparison baseline (never a bare "sales during the promo" number).
3. `main_insight` -- a before/during/after trend visual isolating the
   promotional window against the baseline.
4. `diagnostic` -- breakdowns by product/location/channel showing where the
   lift concentrated.
5. `exception_detail` -- row-level detail for specific products/locations, if
   needed for a post-promotion review.
6. `filter_rail` -- promotion/period selector, product/location slicers.
7. `footer_status` -- data-as-of / refresh note.

## Recommended visual roles

- KPI-card role for the lift outcome, always labeled with its baseline.
- A before/during/after trend-line role for the main insight.
- Breakdown-chart roles (bar/column) for the driver-role dimension cuts.
- A margin/cost guardrail visual paired near the lift outcome, not
  presented separately where it would be missed.

## Expected action paths

- A recommend/repeat-or-retire narrative slot (human-supplied), informed by
  the lift-vs-guardrail comparison.
- Drill from a driver breakdown into the specific product/location detail.
- A `key_exception` callout for any location/product where the promotion
  under-performed materially against the baseline.

## Common design risks

- **No baseline stated**: showing promotional-period performance without
  naming the comparison baseline is this pattern's defining anti-pattern --
  the reader cannot tell lift from ordinary variation.
- **Ignoring cannibalization/pull-forward**: a lift that merely shifted
  demand from an adjacent period reads as pure incremental gain unless the
  before/after window is wide enough to expose the pattern; flag this as a
  design risk for human review of the window choice, not something the
  pattern resolves automatically.
- **Guardrail omitted**: reporting lift without a margin/cost guardrail risks
  declaring an unprofitable promotion a success.
- **Unavailable baseline or promotion-flag data**: if the subject area has no
  approved way to identify the promotional window or a comparison baseline
  (see the promotion-markdown-factless structural pattern for what a
  promotion fact needs), surface the gap via `retail dashboard-gaps` --
  never invent a baseline period.
