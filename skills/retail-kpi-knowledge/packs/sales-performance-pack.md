# Sales Performance KPI Pack

ID: KPI-PK-02

**Purpose**
Executive and sales-management view focused on revenue generation, trend, discounting,
and progress vs target.

**Included KPIs**

| KPI | Contract | State |
|-----|----------|-------|
| Gross Sales | `contracts/gross-sales.md` | Live |
| Net Sales | `contracts/net-sales.md` | Live |
| Transactions Count | `contracts/transactions-count.md` | Live |
| Average Transaction Value | `contracts/average-transaction-value.md` | Live |
| Discount Amount | `contracts/discount-amount.md` | Live |
| Discount Rate % | `contracts/discount-rate.md` | Live |
| Returns Rate % (Value) | `contracts/returns-rate-value.md` | Live |
| Net Sales Growth % | — | Planned |
| Average Basket Size (Units) | — | Planned |
| YTD Net Sales | — | Planned |
| Net Sales vs Target % | — | Planned |

**Required fields**
Sales fact (gross, net/discount, transaction id), date dimension. Planned additions:
fiscal calendar (YTD, growth), target fact (vs target), quantity for basket size.

**Blocked-by conditions**
VAT / returns policy confirmed for revenue KPIs; target fact and fiscal calendar for the
planned items.

**Owner**
Finance and Sales.

**Recommended dashboard / page use**
Sales Performance page; executive summary trend tiles.

**Readiness notes**
Does not imply readiness; Readiness layer decides.

**Handoff notes**
Seven live contracts ready for DAX handoff; four planned KPIs return to this layer for
contracting first.
