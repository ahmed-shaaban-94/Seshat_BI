# Dashboard Pattern: Inventory Health

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

- Inventory / supply-chain planner (the primary reader).
- Operations manager monitoring stock risk.
- Category/product manager watching availability of their assortment.

## Intended purpose

`monitoring` (primary) with an `action_oriented` component -- inventory health
is watched continuously and typically drives a direct replenishment/adjustment
action, not just observation.

## Common question families

- "Which items/locations are at risk of stock-out or overstock right now?"
- "How is stock coverage/availability trending?"
- "Which items need a replenishment or markdown action this week?"
- "Is inventory risk concentrated in a few items/locations or broad-based?"

## Metric roles (roles, not named metrics)

- **Outcome role(s)**: an availability/coverage outcome (e.g. "the
  stock-coverage outcome," "the availability-rate outcome").
- **Guardrail role(s)**: risk-flagging metrics that must stay within bounds
  (e.g. a stock-out-risk guardrail, an overstock/aging guardrail) -- this
  pattern is defined by guardrails being central, not secondary.
- **Driver role**: optional; a metric explaining why coverage moved (e.g. a
  demand-shift or receipt-timing driver), used when the intent also needs a
  diagnostic angle.

## Common page structure

1. `header` -- title + period/as-of context.
2. `kpi_strip` -- headline availability/coverage outcome metrics, each with a
   comparison (vs target coverage band, vs prior period).
3. `main_insight` -- a risk-ranked visual surfacing the items/locations
   closest to a guardrail breach (stock-out or overstock risk).
4. `exception_detail` -- a row-level table of specific at-risk items/locations
   needing action.
5. `filter_rail` -- item/category/location slicers.
6. `footer_status` -- data-as-of / refresh note (freshness matters
   disproportionately here -- a stale inventory snapshot is misleading).

## Recommended visual roles

- KPI-card role for the availability/coverage outcome(s).
- A risk-ranked bar/table role for the main insight (sorted by proximity to a
  guardrail threshold).
- A detail-table role in `exception_detail` for the specific action list.
- Slicer roles for item/category/location, contained in `filter_rail`.

## Expected action paths

- A direct action list (`exception_detail`) naming items/locations requiring
  replenishment, transfer, or markdown -- this pattern's primary reason to
  exist is prompting that action, not just reporting a trend.
- Drill from a risk-ranked item into its own detail (movement history,
  current coverage) if the subject area supports it.
- An explicit `key_exception` narrative callout for the single most urgent
  risk, human-supplied.

## Common design risks

- **Guardrail treated as decoration**: this pattern fails if the
  stock-out/overstock guardrail is shown without a clear threshold/band
  context -- a bare number cannot answer "is this a problem."
- **Stale freshness not flagged**: inventory snapshots go stale fast; a page
  missing a clear data-as-of / freshness note misleads the reader into acting
  on outdated risk. `footer_status` is mandatory here, not optional.
- **No action list**: a purely observational page (coverage trend only, no
  `exception_detail`) undercuts the pattern's action-oriented purpose --
  flagged `incomplete` for missing action paths.
- **Unavailable coverage or receipt-timing dimension**: if the subject area
  cannot compute stock coverage (e.g. no committed inventory-position or
  lead-time field), surface the gap via `retail dashboard-gaps` -- never
  approximate coverage from an unrelated proxy metric.
