# Dashboard layout plan -- sales_c086_raw

Filled instance for the C086 pharmacy branch table. Authored from the ONE
APPROVED metric contract (TotalSales) once `semantic_model_ready` reached
`pass` (2026-07-16). AUTHORING ONLY -- no publish, no Power BI Desktop / DB
connection, no execution adapter (that is the deferred F016). ASCII, UTF-8 no BOM.

## Subject area

- subject_area: `SalesC086` (gold star `gold.fct_sales_c086`)
- governed_model: not yet built (PBIP/DAX authoring is a separate later step;
  this design gate only defines what the model SHOULD show)
- semantic_model_ready: `pass` (mappings/sales_c086_raw/readiness-status.yaml)

## Scope decision (data owner, 2026-07-16)

Deliberately MINIMAL: only `TotalSales` has an approved metric contract right
now. Rather than design a dashboard with orphan visuals (a visual with no
approved contract behind it, which blocks this stage), the first dashboard
ships with exactly the one governed number. Additional visuals (returns,
by-product, by-billing-type, by-staff breakdowns) are explicitly deferred
until their own contracts are authored and approved -- see "Deferred, not
forgotten" below.

## Business questions (in scope today)

1. How much did C086 sell in total, gross of returns? (TotalSales)

> Out of scope with the current contract set (recorded, not invented): returns
> volume/rate as its own metric, per-product or per-division breakdowns,
> per-billing-type (credit/cash/delivery) splits, staff-level activity, and any
> trend/time-series view of TotalSales. None of these are wrong to want -- they
> simply have no approved contract yet. Adding any of them to this page before
> a contract exists and is approved would create an orphan visual.

## Page / section structure

A single, deliberately small page: one KPI card, nothing else.

| Region | Purpose | Business question it serves |
|--------|---------|-----------------------------|
| Header | title + as-of context | (orientation) |
| KPI strip | the one headline number | Q1 |
| Footer-status | data-as-of + scope note | (honesty: this page is intentionally minimal) |

## Notes

- No filter rail: with a single KPI card and no breakdown dimension in scope,
  there is nothing for a slicer to usefully control yet. Revisit once a
  by-dimension contract (e.g. TotalSales by division) is approved.
- No trend/time-series visual: a "TotalSales over time" line chart would still
  bind to the same TotalSales contract (sliced by `dim_date_c086`), so it is
  NOT an orphan-visual risk -- it was left out here purely by the "minimal"
  scope decision, not a governance blocker. It is the most likely next
  addition once a second page/iteration is wanted.

## Deferred, not forgotten

The following are known future asks, explicitly NOT designed here because they
lack an approved contract:
- ReturnsSales / return rate (needs its own contract; A2 already ruled gross-of-returns
  for TotalSales, but a dedicated returns metric is a separate decision)
- TotalSales by division / by billing_type / by product (each breakdown needs
  its own contract or an explicit ruling that TotalSales is valid sliced by
  that dimension)
- Staff-level activity (person/staff dimension exists in gold but has no bound metric)

## See also

- The binding map (the review sign-off artifact): `visual-contract-binding-map.md`.
- The visual list: `visual-list.md`. The contract: `../metrics/TotalSales.yaml`.
- The stage: Dashboard Ready (readiness-status.yaml stages.dashboard_ready).
