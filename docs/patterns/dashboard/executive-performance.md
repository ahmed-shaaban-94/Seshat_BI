# Dashboard Pattern: Executive Performance

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

- Executive / leadership (the primary reader).
- Board or investor-facing summary contexts (occasional, not the common case).

## Intended purpose

`executive` -- a small set of headline results reviewed at a glance, with just
enough comparison context to judge "are we on track," not to diagnose why.

## Common question families

- "How is overall performance this period versus the prior period and versus
  target/plan?"
- "Is any headline result moving in a direction that needs attention?"
- "What is the single most important number leadership should know right now?"

These are question SHAPES, not filled-in business questions -- a real report
states its own primary business questions in its Report Intent.

## Metric roles (roles, not named metrics)

- **Outcome role(s)**: one to three headline result metrics the audience is
  ultimately accountable for (e.g. "the top-line performance outcome," "the
  profitability outcome"). Each MUST carry a comparison (vs prior period and/or
  vs target) -- a bare outcome number with no comparison is the pattern's
  central anti-pattern.
- **Driver role**: at most one light supporting breakdown explaining the
  outcome's movement -- kept minimal; this pattern is deliberately NOT a
  diagnostic pattern (see Sales Diagnosis for deep drivers).
- **Guardrail role**: optional; a secondary outcome that must not silently
  slip while the primary outcome improves (e.g. a profitability guardrail
  alongside a growth outcome).

## Common page structure

A single page, sparse by design (fewer visuals than any other family):

1. `header` -- title + period/comparison context.
2. `kpi_strip` -- 3-4 headline outcome-role metrics, each with a comparison.
3. `main_insight` -- one trend visual answering the primary question.
4. `diagnostic` (light) -- at most one supporting breakdown; may be omitted.
5. `footer_status` -- data-as-of / refresh note.

`exception_detail` and `filter_rail` are typically absent or minimal on this
pattern -- an executive page is not a working/detail surface.

## Recommended visual roles

- KPI-card role for each outcome/guardrail metric (comparison always visible).
- A single trend-chart role for the main insight.
- At most one light breakdown-chart role for the driver role, if present.
- No table-as-headline role (a table is a detail surface, never the executive
  headline -- a shared anti-pattern across every family, see
  `docs/powerbi/visual-qa.md`).

## Expected action paths

- A "drill to diagnostic" path from any outcome or driver visual into a
  diagnostic-purpose page (typically Sales Diagnosis or Branch Performance),
  for the reader who needs the "why" behind a headline movement.
- No in-page exception/action workflow -- action and exception handling is the
  Action & Exceptions pattern's job; this pattern's action is "go look deeper
  elsewhere," not "resolve this here."

## Common design risks

- **Too many visuals**: this pattern is defined by scarcity; adding diagnostic
  or detail visuals directly onto the executive page is the most common
  drift, and the dashboard QA anti-pattern catalog flags it
  (`too_many_visuals`).
- **KPI without comparison**: an outcome-role metric shown as a bare number
  with no vs-prior/vs-target context defeats the pattern's purpose.
- **Mixed purpose on one page**: adding a diagnostic or monitoring concern to
  this page produces a `conflicting` finding under the Dashboard Semantic
  Audit (US5) -- keep this page single-purpose.
- **Unavailable comparison baseline**: if the subject area has no approved
  target/budget contract or no prior-period baseline, the comparison
  requirement is a GAP (route via `retail dashboard-gaps`), never a fabricated
  baseline.
