# Branch / Store Performance Domain

Performance compared across the store network. Needs store master data and a same-store
rule to be meaningful.

## KPIs in this domain

| KPI | Contract | Status |
|-----|----------|--------|
| Net Sales per Branch | — | Planned (reuses Net Sales sliced by branch) |
| Same-Store Sales Growth % | — | Planned (Needs business definition: same-store rule) |
| Sales per Square Meter | — | Planned (needs floor-area field) |

Branch-level cuts of seeded KPIs (Net Sales, Transactions Count, ATV, Discount Rate %,
Returns Rate %, Gross Margin %) are available now by slicing those contracts on the
branch key.

## Key ambiguities (see knowledge/kpi-ambiguities.md)

- A9 Branch name vs branch key — aggregate on the key only.
- A11 Same-store definition — minimum months open, relocations, refurb, closures.
- Treatment of click-and-collect / e-commerce sales attributed to a store.
- Exclude head-office / warehouse pseudo-branches.

## Owner

Operations and Finance.

## Notes

Net Sales per Branch is additive across branches and time. Same-store growth and sales
per sqm are non-additive ratios and stay planned until the same-store rule and store
master data are confirmed.
