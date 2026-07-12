# Dashboard Pattern: Sales Diagnosis

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

- BI analyst / developer investigating a movement.
- Operations or category manager who owns the "why" behind a result.
- Executive escalation ("the headline moved -- why?") as a secondary reader.

## Intended purpose

`diagnostic` -- explain WHY an outcome moved, by decomposing it across the
dimensions and driver metrics that plausibly caused the movement. This pattern
is defined by having drivers; a diagnostic page with no driver metrics
represented is incomplete (see FR-018 / the Dashboard Semantic Audit).

## Common question families

- "What is driving the change in the headline outcome?"
- "Which segment/dimension contributed most to the movement?"
- "Is the movement broad-based or concentrated in a few contributors?"
- "Does the movement reverse or continue a prior trend?"

## Metric roles (roles, not named metrics)

- **Outcome role**: the single result being explained (referenced, not
  redefined here -- it is owned by the report's Report Intent).
- **Driver role(s)**: one or more contributing metrics/dimensions whose
  movement plausibly explains the outcome's movement (e.g. a volume driver, a
  price/mix driver, a channel-contribution driver). A diagnostic page requires
  at least one driver role to be represented -- this is the pattern's defining
  requirement (FR-018 "diagnostic reports include drivers").
- **Guardrail role**: optional; a metric that should not be sacrificed while
  chasing the outcome (e.g. a margin guardrail while diagnosing a volume
  outcome).

## Common page structure

1. `header` -- title + period context + the outcome being diagnosed.
2. `kpi_strip` (light) -- the outcome metric, with comparison, as anchor
   context; not the page's main content.
3. `main_insight` -- the decomposition/contribution visual answering "what
   drove this."
4. `diagnostic` -- one or more supporting breakdowns by dimension (category,
   branch, channel, segment).
5. `exception_detail` -- row-level detail for the top contributors/outliers,
   if the audience needs to inspect specifics.
6. `filter_rail` -- dimension slicers to re-slice the decomposition.
7. `footer_status` -- data-as-of / refresh note.

## Recommended visual roles

- A decomposition or contribution-breakdown chart role for the main insight
  (e.g. waterfall/decomposition-tree/key-influencers role -- see the driver /
  decomposition template, `templates/driver-decomposition.md`).
- Bar/column breakdown-chart roles for the supporting dimension cuts.
- A detail-table role for row-level exception inspection (kept in
  `exception_detail`, never promoted to the main insight).
- Slicer roles contained in `filter_rail` (never dominating the canvas).

## Expected action paths

- Drill-through from a top-contributor bar/segment into the row-level detail
  table.
- A narrative `so_what` / `recommended_action` field (per
  `dashboard-page-blueprint.yaml`'s narrative block) naming the concrete
  next step implied by the diagnosis -- human-supplied, never auto-invented.
- A `key_exception` callout naming the single most important outlier
  contributor, if one dominates the movement.

## Common design risks

- **No driver represented**: the most common failure of this pattern -- a
  page that only restates the outcome (an executive-style page mislabeled as
  diagnostic) produces a `missing` or `incomplete` audit finding.
- **Too many simultaneous dimension cuts**: diagnosing across every dimension
  at once obscures which one actually explains the movement; prioritize the
  cut(s) the driver-decomposition analysis actually supports.
- **Guardrail omitted**: chasing the outcome without showing a guardrail risks
  presenting an incomplete diagnosis (e.g. volume up, margin quietly down).
- **Mixed purpose on one page**: blending monitoring ("is it on track") with
  diagnosis ("why") on the same page is flagged `conflicting` by the
  Dashboard Semantic Audit.
- **Unavailable driver dimension**: if the subject area lacks the dimension a
  plausible driver needs, surface the gap via `retail dashboard-gaps` --
  never approximate with an adjacent, unverified dimension.
