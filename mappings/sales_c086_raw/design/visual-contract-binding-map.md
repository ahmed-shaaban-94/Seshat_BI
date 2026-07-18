# Visual -> contract binding map -- sales_c086_raw

The artifact the DESIGN REVIEW signs off: proves every measure-bearing visual
binds to exactly ONE approved metric contract (no orphan visual) and that no
approved contract is silently dropped. Authored from `dashboard-layout.md` /
`visual-list.md`; it NEVER invents a metric and NEVER self-grants
`dashboard_ready: pass` -- that requires the review sign-off below, recorded
by the reviewer, not by the agent. ASCII, UTF-8 no BOM.

## Subject area

- subject_area: `SalesC086` (`gold.fct_sales_c086`)
- governed_model: not yet built (PBIP/DAX authoring is a separate later step)
- semantic_model_ready: `pass`

## Binding map (every visual -> exactly one APPROVED contract)

The 1 approved contract is bound; 1 measure-bearing visual, zero orphans.

| visual_id | visual_type | business_question | bound_contract (approved) | semantic_model_field(s) |
|-----------|-------------|--------------------|-----------------------------|-------------------------|
| v01 | card | Q1 headline gross sales | TotalSales | `[TotalSales]` (no slice -- whole-table total) |

> The one visual cites the one APPROVED contract by name. No visual lacks a
> backing approved contract (no orphan).

## Contract coverage (the 1 approved contract appears)

| approved_contract | on which visuals |
|--------------------|-------------------|
| TotalSales | v01 |

## Dropped contracts (record each -- no silent omission)

None. The single approved contract (TotalSales) is bound to its one visual.

## Caveat carried to the page (not a binding issue, a data-honesty note)

- v01 (TotalSales): reported gross of returns (all rows, including negative/zero
  is_return=true rows, summed as-is -- see `../metrics/TotalSales.yaml` A2
  ruling). Tax treatment is EXPLICITLY DEFERRED (A1 ruling, 2026-07-16): the
  number is gross_sales as landed, with no stated pre-tax/tax-inclusive
  position. Neither of these is a defect -- both are recorded, named-owner
  rulings -- but the card should not imply a tax-adjusted or net-of-returns
  figure it does not compute.

## Review sign-off (Principle V -- the reviewer's action, NOT the agent's)

- reviewer (BI report owner): `Ahmed Shaaban (data_owner)`
- decision: `approved`
- at: `2026-07-16`

> Sign-off recorded 2026-07-16: the BI report owner reviewed this binding map
> (1 visual, bound 1:1 to the approved TotalSales contract, zero orphans, the
> gross-of-returns and deferred-tax caveats noted) and approved the design as
> drafted, with no requested changes. `dashboard_ready` is promoted to `pass`
> with a matching `approvals[]` entry in `readiness-status.yaml`. (Recorded by
> the reviewer, not self-granted by the agent.)

## See also

- The layout: `dashboard-layout.md`. The visual list: `visual-list.md`.
- The contract: `../metrics/TotalSales.yaml`.
