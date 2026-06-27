# Basket and Transactions Domain

Customer purchase behaviour at the receipt level. The most grain-sensitive domain:
receipt vs line confusion breaks every metric here.

## KPIs in this domain

| KPI | Contract | Status |
|-----|----------|--------|
| Transactions Count | `contracts/transactions-count.md` | Seeded |
| Average Transaction Value | `contracts/average-transaction-value.md` | Seeded |
| Average Basket Size (Units) | — | Planned |

## Key ambiguities (see knowledge/kpi-ambiguities.md)

- Grain: count distinct receipts (`transaction_id`), never transaction lines.
- A7 Exclude cancelled / void / test transactions.
- Returns-only receipts: usually excluded from transaction count and ATV — confirm.
- A1/A4 ATV uses **net sales** in the numerator; keep VAT and gross/net consistent.

## Owner

Sales / Commercial (Operations for traffic-style metrics).

## Notes

Transaction count is effectively additive across days/branches when `transaction_id` is
unique and time-bounded. ATV and basket size are non-additive — recompute from net sales
÷ distinct receipts (or units ÷ receipts) at every level.
