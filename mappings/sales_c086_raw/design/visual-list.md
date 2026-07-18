# Visual list -- sales_c086_raw

The proposed visuals for the single minimal-scope page (see `dashboard-layout.md`).
Deliberately ONE visual: only `TotalSales` has an approved contract. Every visual
binds to exactly ONE approved contract (the binding map is the sign-off artifact).

| visual_id | region | type | answers | measure (approved contract) | sliced by |
|-----------|--------|------|---------|-----------------------------|-----------|
| v01 | KPI strip | card | Q1 headline gross sales | TotalSales | (none -- whole-table total) |

## Design discipline (why this set, and what was deliberately left off)

- **1 visual, single page** -- the minimal scope the data owner chose given
  only one approved contract exists. Not a design compromise: adding a second
  visual today would require either reusing TotalSales in a new cut (fine,
  still one contract) or introducing a metric with no contract (an orphan,
  which blocks Dashboard Ready).
- **No trend line, no breakdown bars, no detail table.** Each of those would
  need either a new contract (a returns metric, a by-dimension metric) or an
  explicit ruling that TotalSales is valid sliced by a given dimension. Neither
  exists yet -- see "Deferred, not forgotten" in `dashboard-layout.md`.
- **Visual type fits the contract grain**: TotalSales is a fully-additive
  measure across the whole fact with no time or category dimension declared
  in scope yet -> a single card, not a line/bar (those imply a slice that
  is not yet contracted for).

## See also

- The sign-off artifact: `visual-contract-binding-map.md`.
- The layout: `dashboard-layout.md`. The contract: `../metrics/TotalSales.yaml`.
