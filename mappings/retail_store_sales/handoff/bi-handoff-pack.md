# BI Handoff Pack -- gold.fct_sales_rss (retail_store_sales)

Filled instance of `templates/handoff/bi-handoff-pack.md` (the second worked example,
after C086). The documentation/evidence bundle for the BI consumer of the
`RetailStoreSales` model. COMPOSES existing committed evidence -- invents nothing. No
publish, no execution adapter (F016 owns live publish/refresh). ASCII, UTF-8 no BOM.

## Header

| Field | Value |
|-------|-------|
| Table / report | `gold.fct_sales_rss` + 5 dims (the `RetailStoreSales` star) |
| Source family | Kaggle "retail store sales (dirty)" -- single CSV, training DB |
| Assembled on | 2026-06-25 |
| Assembled by | agent (dashboard-design sibling; authoring only) |
| Prior-stage gate | stages 1-6 each `pass`? **yes** (readiness-status.yaml: source/mapping/silver/gold/semantic_model/dashboard all pass) |

## Required-section index (each points at an EXISTING committed artifact)

| # | Section | Points at (existing artifact) | Resolved? |
|---|---------|-------------------------------|-----------|
| a | Metric contracts (stage 5, approved) | `../metrics/*.yaml` (5 contracts, all `pass`, owner-approved 2026-06-25) | yes |
| b | Readiness scorecard | `../readiness-status.yaml` (all 7 stages pass; publish approved 2026-06-25) | yes |
| c | Reconciliation evidence (stage 4) | `../reconciliation-report.md` (FILLED, PASS: penny-exact, 0 orphans) | yes |
| d | Known data issues / caveats | `../data-issues`-equivalent + `../assumptions.md` (composed below) | yes |
| e | Data dictionary (deployed schema) | below | yes |
| f | Publish approval | `../readiness-status.yaml` `approvals[]` (recorded below) | yes |

## Known data issues / caveats (MANDATORY -- all four)

Composed from the source-profile + assumptions + the approved contracts; recorded,
never re-decided.

1. **PII exclusion.** No raw PII in the model. `customer_id` is a pseudonymous
   surrogate (`CUST_xx`, 25 distinct) KEPT as `dim_customer_rss` per the owner ruling
   (Q1) -- no name/phone/email/address exists in the source. No column was dropped for
   PII (none present); the deviation from the RC4 auto-drop is recorded in
   `../assumptions.md`.
2. **Returns handling.** NONE in this source. All measures are strictly positive and
   there is no transaction-type/return column; the data owner confirmed returns live in
   a separate figure/system not loaded here. RC8 is N/A. Do NOT infer returns from a
   measure sign. (`../assumptions.md` deviation 1.)
3. **Known gaps (measured).**
   - `discount_applied` is UNKNOWN (NULL) on **4,199 / 12,575 (33.39%)** of
     transactions. The `DiscountedTransactionRate` metric counts unknowns as
     not-discounted, so the reported rate (**33.55%**) is a FLOOR; the rate among
     KNOWN-status transactions is **50.37%**. Any discount visual MUST surface this.
   - `item` is missing on **1,213 / 12,575 (9.65%)** of transactions -- these land on
     the `-1` unknown member of `dim_product_rss` (kept, not dropped; Q4).
   - `price_per_unit` / `quantity` / `total_spent` each missing ~4.8% (~604 rows);
     these NULLs are truly unknown (not recoverable from price*qty -- verified) and are
     ignored in the sums (no revenue discarded).
4. **Out of scope.** No margin/profit (no cost data). No returns (above). No customer
   demographics (only a pseudonymous id). No live refresh/publish wiring (F016).

## Data dictionary (against the DEPLOYED `gold` schema)

Every deployed column appears once; business meaning carried from `../source-map.yaml`.

### gold.fct_sales_rss (fact, one row = one transaction)
| Column | Type | Role | Meaning |
|--------|------|------|---------|
| fct_sales_rss_sk | integer | surrogate PK | fact surrogate key |
| transaction_id | text | degenerate dim | the transaction natural key (`TXN_*`) |
| discount_applied | boolean | degenerate dim | discount flag; NULL = unknown (33%, see caveat 3) |
| customer_sk | integer | FK -> dim_customer_rss | |
| product_sk | integer | FK -> dim_product_rss | -1 = unknown product (missing item) |
| payment_method_sk | integer | FK -> dim_payment_method_rss | |
| location_sk | integer | FK -> dim_location_rss | |
| date_sk | integer | FK -> dim_date_rss | YYYYMMDD |
| price_per_unit | numeric | measure (attribute) | unit price |
| quantity | numeric | measure | units sold (TotalQuantity) |
| total_spent | numeric | measure | line total (TotalSales); = price*quantity |

### Dimensions
| Table | Key | Attributes | Meaning |
|-------|-----|------------|---------|
| dim_customer_rss | customer_sk | customer_id | pseudonymous customer (25 + `-1`) |
| dim_product_rss | product_sk | item, category | product (item 1:1 category); `-1` unknown |
| dim_payment_method_rss | payment_method_sk | payment_method | Cash / Credit Card / Digital Wallet |
| dim_location_rss | location_sk | location | In-store / Online |
| dim_date_rss | date_sk | full_date, year, quarter, month, month_name, day, day_name, iso_week, is_weekend | contiguous calendar 2022-01-01..2025-01-18; marked date table |

## Publish approval (named human sign-off; agent never self-grants)

```yaml
approvals:
  - stage: "publish_ready"
    owner: "data_owner"                  # acting as governance / release authority
    at: "2026-06-25"
    note: "reviewed this pack and authorized release; the live publish ACTION is F016"
```

RECORDED 2026-06-25: the data owner reviewed this pack and AUTHORIZED release ->
`publish_ready` is `pass` (the matching `approvals[]` entry is in
`../readiness-status.yaml`, recorded by the reviewer, not self-granted by the agent).
This authorizes RELEASE of the governed artifacts; the live publish/refresh ACTION to
a Power BI workspace remains the deferred, gated F016 execution adapter.

## Readiness verdict for this pack

`pass` -- the pack is assembled, every required section resolves to a committed
artifact, AND the publish approval is recorded (data_owner, 2026-06-25, above + in
`readiness-status.yaml` `approvals[]`). All 7 readiness stages are now `pass`. NO
numeric confidence score. The live publish/refresh ACTION is the deferred F016 adapter.

## See also

- The checklist that gates this pack: `handoff-review-checklist.md`.
- The composed evidence: `../metrics/*.yaml`, `../reconciliation-report.md`,
  `../readiness-status.yaml`, `../assumptions.md`, `../source-map.yaml`,
  `../design/visual-contract-binding-map.md`.
- The stage authority: `../../../docs/readiness/publish-ready.md`. Live publish (out of
  scope) is the F016 execution adapter.
