# BI Handoff Pack -- gold.fct_sales_c086 (sales_c086_raw)

Filled instance of `templates/handoff/bi-handoff-pack.md` for the C086 pharmacy
branch sales worked example. The documentation/evidence bundle for the BI
consumer of this model. COMPOSES existing committed evidence -- invents
nothing. No publish, no execution adapter (F016 owns live publish/refresh).
ASCII, UTF-8 no BOM.

## Header

| Field | Value |
|-------|-------|
| Table / report | `gold.fct_sales_c086` + 4 dims + `gold.dim_date_c086` (the `sales_c086_raw` star) |
| Source family | `pharmacy_branch_c086_sales_export` -- single-branch (C086) billing-line export |
| Assembled on | 2026-07-16 |
| Assembled by | agent (dashboard-design sibling; authoring only) |
| Prior-stage gate | stages 1-6 each `pass`? **yes** (readiness-status.yaml: source/mapping/silver/gold/semantic_model/dashboard all pass, 2026-07-16) |

## Required-section index (each points at an EXISTING committed artifact)

| # | Section | Points at (existing artifact) | Resolved? |
|---|---------|-------------------------------|-----------|
| a | Metric contracts (stage 5, approved) | `../metrics/TotalSales.yaml` (1 contract, `pass`, owner-approved 2026-07-16) | yes |
| b | Readiness scorecard | `../readiness-status.yaml` (all seven stages `pass` once this pack is approved) | yes |
| c | Reconciliation evidence (stage 4) | `../readiness-status.yaml` `gold_ready.evidence[]` (RC16: row parity 248,593 = 248,593, 0 orphan FKs across 5 dims, exact SUM reconciliation) | yes |
| d | Known data issues / caveats | composed below from `source-profile.md`, `source-map.yaml`, and `readiness-status.yaml` | yes |
| e | Data dictionary (deployed schema) | below | yes |
| f | Publish approval | `../readiness-status.yaml` `approvals[]` -- recorded 2026-07-16, Ahmed Shaaban (data_owner) | yes |

## Known data issues / caveats (MANDATORY -- all four)

Composed from the source profile, the approved source-map, and the recorded
rulings; recorded, never re-decided.

1. **PII exclusion / handling.** `insurance_tel` and `insurance_no` (genuine
   third-party insurance contact/policy data, ~62% populated) were **DROPPED
   ENTIRELY** and do not exist anywhere in `silver`/`gold` (RC4 default,
   ruled 2026-07-16). `person_name` (staff/employee data: driver, cashier,
   pharmacist, branch-manager roles observed) is **MASKED** -- it survives
   only as `staff_name_masked`, a deterministic `md5()` hash (same
   `staff_code` always -> same hash); no raw name column exists in silver or
   gold. `customer_name` was reviewed and ruled **LOW RISK, KEEP AS-IS**
   (sampled as predominantly B2B/institutional: insurance companies, pharma
   distributors, branch names; only 517/249,106 rows show a redacted-looking
   hash pattern, no individual patient names observed) -- it is NOT masked.
2. **Returns handling.** Returns are identified from the AUTHORITATIVE
   `billing_type` column (translated to English; `LIKE '%Return%'` on the
   translated label), **never from the `quantity` or `gross_sales` sign**.
   Measured `is_return` rate in the deployed gold fact: **12,280 / 248,593
   (4.94%)**. `TotalSales` (the only approved metric) is **gross of
   returns**: it sums `gross_sales` across every row including
   `is_return=true` rows. This is safe because those rows are already
   negative or zero in the source -- verified 2026-07-16 against the
   deployed fact: of the 12,280 `is_return=true` rows, 10,603 (86.4%) carry
   negative `gross_sales` and 1,677 (13.6%) are exactly zero; **none are
   positive**. A separate `ReturnsSales` metric (return-only) does not exist
   yet and would need its own contract.
3. **Known gaps (measured).**
   - **Row filter (513 / 249,106 rows, 0.21%, excluded from silver/gold
     entirely):** rows where `division IN ('ARCHIVE', 'AUX', '', 'EL EZABY
     SERVICES')` were excluded as out-of-scope for a retail sales-of-goods
     fact (retired/discontinued-product archive lines, negligible
     miscellaneous-tagged rows, genuinely blank division, and non-product
     service charges such as injection fees). **Caveat: 85 of those 513
     excluded rows were themselves return transactions** (72 Arabic-prefix +
     13 "Pick-Up Order Return"), so the full-bronze return count (12,365)
     is NOT the same as the deployed gold return count (12,280) -- a 85-row
     gap, verified, not an oversight.
   - **No tax/discount measures in the model.** `tax`, `dis_tax`, `add_dis`,
     `subtotal5_discount`, and `paid` were all dropped. Landed `net_sales`
     was ruled unreliable (the `gross_sales + dis_tax + add_dis - tax`
     identity held on only 90.4% of rows, with no alternative formula
     found across 7 tested combinations) and was never carried forward.
     **There is no net-sales measure anywhere in this model** -- `gross_sales`
     is the sole standing "sales" figure.
   - **VAT/tax treatment on `gross_sales` is explicitly DEFERRED, not
     resolved.** The data owner directed "we will ignore tax for now"
     (2026-07-16). `gross_sales` is reported as-landed with no stated
     pre-tax/tax-inclusive position. Do not assume either without a fresh
     ruling.
   - Sentinel/unknown-member rates (measured, not estimated): `item_cluster`
     -> `'UNKNOWN'` on 79,734 / 249,106 rows (32.01%); `staff_code` /
     `dim_staff_c086` -1 member -> 1,745 fact rows route there (blank
     `personel_number`); all other kept dimension columns show 0
     `'UNKNOWN'` rows. Slicing by `item_cluster` or by staff understates
     the real members and overstates the `UNKNOWN`/`-1` bucket; grand
     totals (e.g. `TotalSales`) are unaffected since the row is still
     counted, just under the unknown member.
4. **Out of scope.** No net-sales or tax-aware measure (above). No
   returns-only metric (`ReturnsSales` not yet contracted). No
   by-product / by-division / by-billing-type / staff-activity breakdown
   (deferred -- no approved contract exists for any of them; see
   `dashboard-layout.md`'s "Deferred, not forgotten" list). No
   `purchaser`/`buyer` dimension (added during investigation, later dropped
   entirely from the model). No live refresh/publish wiring (F016).

## Data dictionary (against the DEPLOYED `gold` schema)

Every deployed column appears once; business meaning carried from
`../source-map.yaml`.

### gold.fct_sales_c086 (fact, one row = one billing-document line item)
| Column | Type | Role | Meaning |
|--------|------|------|---------|
| fct_sales_c086_sk | integer | surrogate PK | fact surrogate key |
| reference_no | text | degenerate dim (grain key) | billing-document reference (C086 + 10 digits) |
| item_no | text | degenerate dim (grain key) | line-item sequence within the document |
| is_return | boolean | degenerate dim (derived) | derived from the translated `billing_type` label (`LIKE '%Return%'`), never from a measure sign; 12,280/248,593 (4.94%) true |
| product_sk | integer | FK -> dim_product_c086 | -1 = unknown product |
| billing_type_sk | integer | FK -> dim_billing_type_c086 | -1 = unknown billing type |
| customer_sk | integer | FK -> dim_customer_c086 | -1 = unknown customer |
| staff_sk | integer | FK -> dim_staff_c086 | -1 = unknown staff (1,745 rows route here) |
| date_sk | integer | FK -> dim_date_c086 | YYYYMMDD; NOT NULL, no -1 member (marked date table) |
| quantity | numeric(14,3) | measure | units sold on this line |
| gross_sales | numeric(18,2) | measure | gross sales value (EGP); the sole "sales" measure; gross of returns; tax treatment deferred |

### Dimensions
| Table | Key | Attributes | Meaning |
|-------|-----|------------|---------|
| dim_product_c086 | product_sk | material, material_desc, category, subcategory, segment, division, brand, item_cluster | product (material 1:1 material_desc); `-1` unknown |
| dim_billing_type_c086 | billing_type_sk | billing_type, billing_type_code | translated English billing/return type (10 values) + its 1:1 short code |
| dim_customer_c086 | customer_sk | customer, customer_name | customer/pharmacy (predominantly B2B/institutional); `-1` unknown |
| dim_staff_c086 | staff_sk | staff_code, staff_name_masked, staff_position | staff who processed the line; name masked (md5, deterministic); `-1` unknown |
| dim_date_c086 | date_sk | full_date, year, quarter, month, month_name, day, day_name, iso_week, is_weekend | contiguous calendar 2023-01-01..2025-12-31; marked date table, no unknown member |

## Publish approval (named human sign-off; agent never self-grants)

`publish_ready` approval RECORDED. Per Principle V, the agent never
self-grants this -- it composed and presented this pack, then STOPPED and
requested the named data owner's sign-off, which was given explicitly
("yes, approve publish_ready").

```yaml
approvals:
  - stage: "publish_ready"
    owner: "Ahmed Shaaban (data_owner)"
    at: "2026-07-16"
```

## Readiness verdict for this pack

`pass` -- the pack is fully assembled: every content section resolves to a
committed artifact, all four mandatory caveats are present with measured
counts (not adjectives), the data dictionary matches the deployed `gold`
schema exactly (verified against LIVE `information_schema.columns`,
column-by-column -- not just the design in `source-map.yaml`), and the
named data owner has recorded a dated `publish_ready` approval above. This
closes all seven readiness stages for `sales_c086_raw`. The live
publish/refresh ACTION remains the deferred F016 execution adapter -- this
pack and its approval authorize release; they do not perform it.

## See also

- The checklist that gates this pack: `handoff-review-checklist.md`.
- The composed evidence: `../metrics/TotalSales.yaml`, `../readiness-status.yaml`,
  `../source-map.yaml`, `../source-profile.md`, `../design/visual-contract-binding-map.md`.
- The stage authority: Publish Ready (Stage 7) in the Seshat_BI kit's
  `docs/readiness/publish-ready.md`. Live publish (out of scope) is the F016
  execution adapter.
