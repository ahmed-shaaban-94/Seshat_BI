# Dashboard Pattern: Action & Exceptions

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

- Operations / frontline manager who must act on exceptions day-to-day.
- Any audience whose report explicitly names expected actions and
  exceptions in its Report Intent (`expected_actions_and_exceptions`).

## Intended purpose

`action_oriented` -- the reader's job on this page is to find the specific
thing that needs attention right now and act on it, not to explore or
diagnose broadly. This pattern is the narrowest and most task-focused of the
ten families.

## Common question families

- "What needs my attention today?"
- "Which specific items/locations/records have breached a guardrail and
  require action?"
- "What is the recommended next step for each flagged exception?"
- "Has a previously flagged exception been resolved?"

## Metric roles (roles, not named metrics)

- **Guardrail role(s)**: the thresholds whose breach DEFINES an exception
  (e.g. a risk/performance guardrail per record) -- this pattern is
  organized entirely around guardrail breaches, more than any other family.
- **Outcome role**: optional, light; a summary count/rate of open
  exceptions, used only as page-level context, not the main content.
- **Driver role**: not typically required -- this pattern surfaces WHAT needs
  action, leaving WHY (the diagnostic question) to a linked diagnostic page
  if the intent needs it.

## Common page structure

1. `header` -- title + as-of context.
2. `kpi_strip` (light) -- a count/rate of currently open exceptions, as
   summary context only.
3. `exception_detail` -- THE main content of this pattern: a row-level,
   actionable list of specific exceptions, each naming what breached, by how
   much, and the recommended action.
4. `filter_rail` -- slicers to narrow the exception list (by owner, severity,
   category, location).
5. `footer_status` -- data-as-of / refresh note (exception lists go stale
   fast; freshness matters).

Unlike most other families, `main_insight` and `diagnostic` are typically
absent or minimal here -- the exception list itself IS the main content.

## Recommended visual roles

- A detail-table (or card-list) role as the primary visual, sorted by
  severity/urgency, with clear per-row action guidance.
- A light KPI-card role for the open-exception count/rate.
- Slicer roles for severity/owner/category, contained in `filter_rail`.
- Conditional-formatting/status-color use for severity, sourced from the
  theme's sentiment palette (color only -- the underlying threshold/rule
  stays a metric-contract concern, never baked into the theme).

## Expected action paths

- Every row in the exception list resolves to a clear, human-supplied
  recommended action (this pattern's entire reason to exist).
- A resolution/acknowledgment path, if the subject area's operational
  process supports tracking exception status (open/acknowledged/resolved).
- No open-ended exploratory drill -- action paths here are narrow and
  specific, not general analytical navigation.

## Common design risks

- **Table as the exec headline elsewhere, but correct here**: unlike most
  other families, an action-oriented table-as-primary-visual is CORRECT for
  this pattern -- do not flag it against the general
  `table_as_main_executive_visual` anti-pattern, which is scoped to
  executive-purpose pages, not this one.
- **No recommended action per row**: an exception list with no action
  guidance is just a filtered report, not an action surface -- defeats the
  pattern's purpose.
- **Guardrail threshold invented**: as with Data Quality Control Room, the
  breach threshold defining "this is an exception" must come from an
  approved metric contract or operational agreement, never an arbitrary
  design-time number.
- **Stale exception list presented as current**: a missing or unclear
  `footer_status` risks the reader acting on outdated exceptions.
- **Mixed with broad exploration**: adding open-ended analytical visuals to
  this page dilutes its narrow, task-focused purpose -- if broader
  exploration is also needed, that belongs on a separate page under a
  different pattern (e.g. Sales Diagnosis or Product Performance).
