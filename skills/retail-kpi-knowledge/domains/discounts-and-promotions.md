# Discounts and Promotions Domain

Value given away to customers and the effectiveness of promotional activity.

## KPIs in this domain

| KPI | Contract | Status |
|-----|----------|--------|
| Discount Amount | `contracts/discount-amount.md` | Seeded |
| Discount Rate % | `contracts/discount-rate.md` | Seeded |
| Promotion Uplift % | — | Planned (needs promotion dimension + baseline rule) |

## Key ambiguities (see knowledge/kpi-ambiguities.md)

- A5 Discount line vs header — state which fields exist and how they combine; avoid
  double-counting.
- A4 Gross vs net — discount rate uses **gross** sales in the denominator.
- Separate commercial discounts from accounting write-offs and loyalty-point redemptions.
- Retailer-funded vs supplier-funded discount — split only if the source supports it.

## Owner

Commercial and Finance.

## Notes

Discount Rate % is non-additive (recompute as total discount ÷ total gross at each
level). Promotion Uplift % requires a robust promotion fact and an agreed baseline
period; it stays planned until both exist.
