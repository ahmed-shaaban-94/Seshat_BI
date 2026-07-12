# Dashboard Pattern: Branch Performance

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

- Branch / location / store manager (the primary reader).
- Regional or multi-location operations manager comparing across sites.

## Intended purpose

`monitoring` (most common) or `diagnostic` (when a branch manager also needs
the "why" behind their own location's result) -- a per-location or
cross-location comparison view for spotting under/over-performing locations.

## Common question families

- "How is my location/branch performing this period, and against what
  comparison (target, peer average, prior period)?"
- "Which locations are underperforming and need attention?"
- "How does my location rank/compare against peers?"
- "Is an underperforming location's issue broad or narrow (one metric or
  many)?"

## Metric roles (roles, not named metrics)

- **Outcome role(s)**: the per-location result metric(s) being monitored
  (e.g. a location-level performance outcome).
- **Comparison role**: implicit in this pattern -- every outcome MUST carry a
  peer/target/prior-period comparison; a location number with no comparison
  reads as noise, not signal (this pattern amplifies the general
  kpi-without-comparison anti-pattern into its central risk).
- **Driver role(s)**: optional, present only when the pattern is combined
  with a diagnostic purpose -- see Sales Diagnosis for the deep-drill
  variant.
- **Guardrail role**: optional; a metric that must not slip while a location
  is compared on its primary outcome (e.g. a service/quality guardrail
  alongside a volume outcome).

## Common page structure

1. `header` -- title + period context + the location/branch identifier or
   selector.
2. `kpi_strip` -- headline outcome metric(s) for the selected location, each
   with a comparison (vs peer average, vs target, vs prior period).
3. `main_insight` -- a ranked comparison visual across locations (e.g. a
   ranked bar/column of the outcome metric by location).
4. `diagnostic` (optional) -- light supporting breakdown for an
   underperforming location, if the intent includes a diagnostic component.
5. `filter_rail` -- a location selector/slicer (and any relevant time-period
   slicer).
6. `footer_status` -- data-as-of / refresh note.

## Recommended visual roles

- KPI-card role per outcome metric, always paired with a comparison.
- A ranked bar/column-chart role for the cross-location comparison (main
  insight).
- A location slicer role, contained in `filter_rail`.
- A small-multiples or matrix role if multiple outcome metrics need
  side-by-side comparison across many locations.

## Expected action paths

- Drill from the ranked comparison visual into a single location's detail
  (this location's own kpi_strip context, or a diagnostic page).
- A callout naming the location(s) most in need of attention (the
  `key_exception` narrative slot), human-supplied.
- An escalation path for a location breaching a guardrail threshold, routed
  to the Action & Exceptions pattern if the report also needs that surface.

## Common design risks

- **Comparison omitted**: a location metric shown without a peer/target/prior
  comparison is the pattern's most common failure -- it cannot answer "is
  this location doing well," only "what is the number."
- **Ranking without a fair basis**: comparing locations on an outcome without
  normalizing for a relevant factor (e.g. size, footfall) the subject area
  actually supports is a design risk to flag for human review, not something
  this pattern resolves on its own.
- **Too many locations rendered flatly**: a long unranked list defeats the
  "which locations need attention" question; prefer a ranked/sorted
  presentation and a Top/Bottom-N framing where the subject area supports it.
- **Unavailable peer-average or target baseline**: if no approved
  target/budget contract exists for the comparison, surface the gap via
  `retail dashboard-gaps` -- never substitute an invented baseline.
