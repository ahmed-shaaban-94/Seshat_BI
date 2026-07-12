# Dashboard Pattern: Data Quality Control Room

**Status of this document**: a GENERIC dashboard-design pattern (spec 123, US3).
It supplies design GUIDANCE ONLY -- suitable audiences, intended purpose, common
question families, metric ROLES (not named metrics), a common page structure,
recommended visual roles, expected action paths, and common design risks. It
defines NO KPI, NO formula, NO DAX, and NO tenant-specific business logic. A
report that adopts this pattern still authors its own Report Intent
(`templates/report-intent.yaml`), page blueprints, and visual specs, and still
resolves every metric role to an APPROVED metric contract (F009) by name --
never invents one (FR-003/FR-013). A starter blueprint already exists for this
family (`reports/blueprints/data-quality-control-room.yaml`); this document
supplies the reusable design guidance that starter (and any other filled
instance) draws on.

**How this is used**: the pattern-recommendation workflow
(`.claude/skills/powerbi-dashboard-design/workflows/pattern-recommendation.md`)
proposes this pattern (alongside any other fitting pattern) when a committed
Report Intent's `purpose` matches. The human accepts, adapts, or rejects it
(FR-014); nothing here is auto-applied.

## Suitable audiences

- Data/BI engineer or analyst responsible for pipeline health.
- Data governance owner monitoring freshness and completeness commitments.
- Any dashboard consumer needing to judge "can I trust this data right now"
  before reading other reports.

## Intended purpose

`monitoring` -- a dedicated, always-available surface for data trustworthiness
itself, distinct from any business-outcome report. This pattern's subject IS
the data pipeline's health, not a business result.

## Common question families

- "Is the data as fresh as expected (last successful refresh, expected
  cadence)?"
- "Are there completeness or reconciliation issues (row counts, expected
  vs actual)?"
- "Which tables/sources currently have a known data-quality issue?"
- "Where should I look before trusting a business report right now?"

## Metric roles (roles, not named metrics)

- **Outcome role(s)**: a freshness outcome (time since last successful load)
  and a completeness/reconciliation outcome (rows loaded vs expected, or
  similar).
- **Guardrail role(s)**: thresholds that must not be breached (e.g. a
  maximum-staleness guardrail, a maximum-row-variance guardrail).
- **Driver role**: not typically applicable to this pattern -- data-quality
  status is reported categorically (this pattern intentionally avoids
  inventing a "why the pipeline failed" diagnostic role; that belongs to
  pipeline-owner tooling outside dashboard scope).

## Common page structure

1. `header` -- title + "as of" timestamp, prominent (this page's entire
   purpose is trust-in-the-data, so the timestamp is not a footer detail
   here the way it is on other patterns).
2. `kpi_strip` -- freshness and completeness outcome metrics, each compared
   against its expected cadence/threshold.
3. `main_insight` -- a status-by-table/source visual (e.g. a status grid or
   list) showing which sources are current vs stale vs flagged.
4. `exception_detail` -- row-level detail naming the specific issue per
   flagged table/source.
5. `filter_rail` -- source/table/domain slicers, if the control room spans
   many subject areas.
6. `footer_status` -- redundant with the header here; may be omitted if the
   header already carries the as-of context prominently.

## Recommended visual roles

- KPI-card role for freshness/completeness outcomes, using status color
  (from the theme's sentiment palette, never a business-logic threshold
  baked into the theme itself -- see the theme-json surface boundary).
- A status-grid or categorical-list role for the main insight (per-source
  status), not a business trend chart.
- A detail-table role in `exception_detail` naming the specific flagged
  issue and its owner.

## Expected action paths

- A direct link or reference to the responsible pipeline owner/runbook for
  each flagged issue (naming the owner is a Principle-V, human-supplied
  field, not auto-derived).
- No "drill into business data" path from this page -- its job stops at
  "here is what's wrong and who owns it," never at explaining or acting on
  the underlying business result.

## Common design risks

- **Treated as a business report**: this pattern's most distinctive risk is
  scope creep -- adding business-outcome visuals to the control room blurs
  its purpose; keep it strictly about pipeline/data health.
- **Stale "as of" not itself flagged**: if the control room's OWN refresh is
  stale, that must be visible too (a control room that silently fails to
  refresh is worse than no control room).
- **No named owner for a flagged issue**: an exception with no responsible
  owner leaves the reader unable to act; every `exception_detail` row should
  resolve to a named owner or escalation path.
- **Guardrail thresholds invented rather than sourced**: freshness/row-count
  thresholds must come from an approved operational agreement, not an
  arbitrary number picked during design; where no such agreement is
  committed, surface the gap rather than inventing a threshold.
