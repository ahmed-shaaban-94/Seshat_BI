# Generic Retail KPI Catalog

A **menu of common retail KPIs**, grouped into candidate packs, to copy into a real
per-table metric contract. This is the generic content half of feature F009 (the
`templates/metric-contract.yaml` schema + the `docs/metrics/metric-contract-store.md`
store rules are the other half). It is **intent + typical binding only** -- never DAX,
never a check, never an approval.

> **How to use:** pick the KPIs a subject area needs, copy each into
> `mappings/<table>/metrics/<MetricName>.yaml` (the atomic contract template), fill in
> the table's real `gold` binding, and route it through the store lifecycle. Group the
> ones you adopt into a `metrics/packs/<pack_name>.yaml` (the pack template).

## The rules this catalog obeys (do not drift)

- **Generic only (hard rule #7).** Every name/intent below is generic retail; no C086
  (pharmacy) or any one table's specifics. C086 is cited as an example elsewhere, never
  inlined here.
- **DEFINE, not CHECK or APPROVE.** Authoring intent is in-scope (same category as
  authoring `mappings/` artifacts). Nothing here reads `powerbi/`, asserts a measure, or
  approves anything. A copied contract starts at `status: not_started`; only the named
  **metric owner** moves it to `pass` (Principle I).
- **No fake confidence (rule #9).** Readiness is the four statuses + evidence + blockers,
  never a number.
- **Stop at judgment calls (Principle V).** KPIs flagged **[owner ruling]** below depend
  on a human decision or data that may not exist (cost, returns source, customer identity,
  a discount-status convention). Do not invent the answer -- record a `blocking_reason`
  and stop for the owner.
- **Gold-only binding (Principle III).** Every `binds_to` points at a `gold` column;
  binding to `silver`/`bronze` is a defect.
- **Additivity matters.** A `non-additive` metric (a ratio/average) must be recomputed at
  the current filter grain, never summed. State it in the contract's `grain` field.

## Pack: `sales_overview` -- headline volume & value

| Metric (PascalCase) | Intent (plain language) | Additive? | Typical gold binding |
|---------------------|-------------------------|-----------|----------------------|
| `TotalSales` | sum of the sale amount across the filtered rows | additive | fact money measure (e.g. `total_spent`) |
| `TotalQuantity` | sum of units sold | additive | fact qty measure (e.g. `quantity`) |
| `TransactionCount` | number of distinct transactions | additive (count) | fact grain key (e.g. `transaction_id`) |
| `AvgTransactionValue` | `TotalSales / TransactionCount` -- the average basket value | non-additive | derived from the two above |
| `GrossMargin` **[owner ruling]** | sale amount minus cost of goods | additive | needs a `gold` cost column; **stop if none exists** |
| `GrossMarginRate` **[owner ruling]** | `GrossMargin / TotalSales` | non-additive | depends on `GrossMargin` (cost data) |

## Pack: `basket_analysis` -- what one transaction looks like

| Metric | Intent | Additive? | Typical gold binding |
|--------|--------|-----------|----------------------|
| `UnitsPerTransaction` | `TotalQuantity / TransactionCount` -- average units per basket | non-additive | derived |
| `AvgUnitPrice` | average price per unit across the filtered rows | non-additive | fact unit-price attribute |
| `LinesPerTransaction` **[owner ruling]** | average distinct line items per basket | non-additive | needs a line-item grain; **N/A for single-row-per-transaction sources** |

## Pack: `customer_activity` -- who is buying

| Metric | Intent | Additive? | Typical gold binding |
|--------|--------|-----------|----------------------|
| `ActiveCustomerCount` | number of distinct customers with a transaction in the filter | additive (count) | `dim_customer` key |
| `SalesPerCustomer` | `TotalSales / ActiveCustomerCount` | non-additive | derived |
| `RepeatPurchaseRate` **[owner ruling]** | share of customers with more than one transaction | non-additive | needs durable customer identity; **PII publish-safety ruling required** |
| `NewVsReturningSales` **[owner ruling]** | sales split by first-ever vs repeat customer | additive within split | needs a first-purchase definition (owner-supplied) |

## Pack: `discount_promotion` -- promotion effectiveness

| Metric | Intent | Additive? | Typical gold binding |
|--------|--------|-----------|----------------------|
| `DiscountedTransactionRate` **[owner ruling]** | share of transactions that had a discount applied | non-additive | discount flag; **the denominator is an owner ruling** -- all transactions, or only known-status ones? (see the worked-example lesson below) |
| `AvgDiscountDepth` **[owner ruling]** | average discount amount or % per discounted transaction | non-additive | needs a discount **amount**, not just a flag; **stop if only a flag exists** |

> **Worked-example lesson (denominator rulings matter).** In
> `docs/worked-examples/retail-store-sales.md`, `DiscountedTransactionRate` turned on
> whether a *blank* discount status counts. The owner ruled blank = **unknown, excluded**,
> making the rate `discounted / known-status` (50.37%), not `discounted / all` (33.55%).
> The wrong denominator silently changes the headline number -- which is exactly why this
> is an **[owner ruling]**, not an agent default.

## Pack: `channel_mix` -- where sales happen

| Metric | Intent | Additive? | Typical gold binding |
|--------|--------|-----------|----------------------|
| `SalesByChannel` | `TotalSales` sliced by channel (e.g. in-store vs online) | additive within channel | `dim_location` / channel attribute |
| `ChannelMixRate` | a channel's share of `TotalSales` | non-additive | derived from `SalesByChannel` |
| `SalesByPaymentMethod` | `TotalSales` sliced by payment method | additive within method | `dim_payment_method` attribute |

## Pack: `time_trend` -- movement over time

| Metric | Intent | Additive? | Typical gold binding |
|--------|--------|-----------|----------------------|
| `SalesMTD` / `SalesYTD` | `TotalSales` to-date within the current month / year | additive | needs a **marked date table** (rule S8) + time-intelligence DAX |
| `SalesGrowthRate` | period-over-period change in `TotalSales` | non-additive | date intelligence over the date dim |
| `SameStoreSalesGrowth` **[owner ruling]** | growth limited to stores open in both periods | non-additive | needs a store dimension + an "open in both periods" definition (owner-supplied) |

## Authoring checklist (per KPI you adopt)

1. Copy `templates/metric-contract.yaml` to `mappings/<table>/metrics/<MetricName>.yaml`.
2. Fill `name` (PascalCase, unique in the store), `grain` (state non-additivity here),
   `formula_intent` (plain language), `owner`, and `binds_to` (gold column(s)).
3. If the KPI is **[owner ruling]**, set `status: blocked` with the `blocking_reason`
   until the owner decides -- never invent the rule.
4. Group adopted KPIs into `metrics/packs/<pack_name>.yaml`; every referenced name must
   resolve to a contract that exists (a dangling reference is a defect).
5. Leave `status: not_started` until the named owner approves (then `pass` with
   `evidence: ["approved by <owner> on <YYYY-MM-DD>"]`).

## See also

- The atomic contract template: `../../templates/metric-contract.yaml`.
- The pack template: `../../templates/kpi-pack.yaml`.
- The store rules + lifecycle: `metric-contract-store.md`.
- A filled set of five contracts (real example): `../../mappings/retail_store_sales/metrics/`.
- The stage that reads contracts: `../readiness/semantic-model-ready.md`.
- The glossary entries (metric contract, KPI pack, additivity): `../glossary.md`.
