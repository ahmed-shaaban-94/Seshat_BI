# Dashboard Pattern: Customer Behavior

**Status of this document**: a GENERIC dashboard-design pattern (spec 123, US3).
It supplies design GUIDANCE ONLY -- suitable audiences, intended purpose, common
question families, metric ROLES (not named metrics), a common page structure,
recommended visual roles, expected action paths, and common design risks. It
defines NO KPI, NO formula, NO DAX, and NO tenant-specific business logic. A
report that adopts this pattern still authors its own Report Intent
(`templates/report-intent.yaml`), page blueprints, and visual specs, and still
resolves every metric role to an APPROVED metric contract (F009) by name --
never invents one (FR-003/FR-013). Where this pattern needs a customer
dimension or grain input, it refers to the existing generic modelling patterns
`docs/patterns/customer-dimension-pattern.md` and
`docs/patterns/customer-grain-pattern.md` (data-modeling layer, distinct from
this design layer) rather than restating that structure here.

**How this is used**: the pattern-recommendation workflow
(`.claude/skills/powerbi-dashboard-design/workflows/pattern-recommendation.md`)
proposes this pattern (alongside any other fitting pattern) when a committed
Report Intent's `purpose` matches. The human accepts, adapts, or rejects it
(FR-014); nothing here is auto-applied.

## Suitable audiences

- CRM / loyalty / customer-marketing manager (the primary reader).
- Analyst exploring customer segments or cohorts.
- Executive interested in customer-base health as a secondary reader.

## Intended purpose

`analytical_exploration` (primary), sometimes combined with `monitoring` for
a recurring customer-health check (e.g. retention/repeat-purchase tracking).

## Common question families

- "How is the customer base changing (new vs returning, growing vs
  shrinking)?"
- "Which customer segments/cohorts contribute most to the outcome?"
- "How does behavior differ across segments (frequency, recency, basket
  composition)?"
- "Is customer retention/repeat behavior improving or declining?"

## Metric roles (roles, not named metrics)

- **Outcome role(s)**: a customer-base or engagement outcome (e.g. "the
  active-customer-count outcome," "the repeat-rate outcome").
- **Driver role(s)**: segment/cohort/behavioral metrics explaining the
  outcome (e.g. a new-customer-acquisition driver, a frequency driver).
- **Guardrail role**: optional; a metric that should not slip while pursuing
  growth (e.g. a churn/attrition guardrail alongside an acquisition-outcome
  focus).

## Common page structure

1. `header` -- title + period context + segment/cohort selector, if used.
2. `kpi_strip` -- headline customer-base or engagement outcome metrics, each
   with a comparison (vs prior period).
3. `main_insight` -- a segmentation or cohort visual (e.g. a
   new-vs-returning split, or a cohort-retention role) answering the primary
   question.
4. `diagnostic` -- supporting breakdowns by segment/behavior dimension.
5. `exception_detail` -- row-level or segment-level detail for drill-down,
   where PII constraints allow (customer-level detail is subject to the
   PII-masking rule below).
6. `filter_rail` -- segment/cohort/date slicers.
7. `footer_status` -- data-as-of / refresh note.

## Recommended visual roles

- KPI-card role for the customer-base/engagement outcome(s).
- A segmentation-chart role (stacked bar, cohort grid, or similar) for the
  main insight.
- Breakdown-chart roles for the driver-role segment/behavior cuts.
- Segment/cohort slicer roles, contained in `filter_rail`.

## Expected action paths

- Drill from a segment/cohort into its own detail view.
- A callout naming the segment most responsible for a shift in the outcome
  (`key_exception`), human-supplied.
- A recommended-action narrative slot for marketing/retention decisions,
  human-supplied -- never an auto-generated targeting recommendation.

## Common design risks

- **PII exposure**: any customer-identifying field surfaced in a visual or
  tooltip MUST be masked by default (SEC-003); unmasking is itself a
  recorded, named-human `pii_handling` decision via the shipped Decision
  Store -- this pattern never assumes unmasked customer detail is
  available.
- **Segment defined without an approved grain**: customer segmentation
  requires a stable, approved customer grain (see
  `docs/patterns/customer-grain-pattern.md`); building a segment view on an
  unresolved or ambiguous grain risks double-counting or undercounting
  customers.
- **Cohort view assumed but unsupported**: a cohort-retention visual needs a
  committed way to identify a customer's acquisition period; where that
  is not mapped, surface the gap via `retail dashboard-gaps` rather than
  approximating cohorts from an unrelated date field.
- **Vanity metric with no action**: a customer-count or engagement trend
  shown with no driver or action path reads as decoration; pair the outcome
  with at least one driver-role breakdown.
