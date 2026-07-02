# Assumptions -- `C086`

> **SUPERSEDED (2026-07-02).** Historical artifact of the FIRST build (0001/0002).
> The current approved assumptions are in [`mappings/sales_c086/`](../sales_c086/)
> (RC9/RC2/RC6 deviations recorded there). See [`./README.md`](./README.md).

> **Filled instance.** Per-table record of which ADR 0002 cleaning/modeling defaults
> (`RC1`-`RC16`) C086 adopted as-is versus deviated from. C086 adopted **16/16 with 0
> deviations** after live DB validation. This is the engineering expression of the
> constitution principle "Defaults Then Deviations".

| Field | Value |
|-------|-------|
| Table id | `C086` (`silver.sales_c086`) |
| Date | `2026-06-24` |
| Author | back-authored from committed 0001/0002 (live-validated) |
| Source profile | `mappings/c086/source-profile.md` (the profiled evidence) |
| Source map | `mappings/c086/source-map.yaml` (the keep/drop/type/grain/star decisions) |
| Per-table ADR | none required -- 0 deviations (the global `../../docs/decisions/0002-retail-cleaning-defaults.md` defaults all held) |

**Where this sits in the data flow:** `source-profile.md` (evidence) +
`source-map.yaml` (decisions) `->` **`assumptions.md`** (which ADR defaults held, which
were overridden). The 16 rows below are exactly the ADR 0002 defaults `RC1`-`RC16`.

---

## Defaults adopted as-is

All 16 adopted unchanged. `[OK]` = adopted; `[x]` = deviated. C086 has no `[x]` rows.

| ADR id | Default summary (generic ruling) | Adopted? | Note |
|--------|----------------------------------|----------|------|
| RC1  | Model at the lowest grain the source provides; decide grain first. | `[OK]` | Grain = one invoice line item; decided before any column drop. |
| RC2  | Verify the PK on the data, and re-verify on the transformed output. | `[OK]` | Live: 246,916 rows = 246,916 distinct `(invoice_no,line_no)`, 0 NULL PK. |
| RC3  | Drop no-signal columns (100%-empty, single-value, verified dup, code half of a 1:1 code/label pair). | `[OK]` | No no-signal kept columns; `billing_type_code` Z-code kept as a stable join key (RC3 exception). |
| RC4  | Remove PII/sensitive data before the BI layer, decided early (not at review). | `[OK]` | `insurance_no` + `insurance_phone` (patient health PII) dropped from the silver SELECT entirely. |
| RC5  | Treat the empty string as missing: `''` `->` NULL first; measure missingness as `'' OR NULL`. | `[OK]` | `NULLIF(trim(x),'')` on every cast; junk filter runs BEFORE `''`->NULL so blanks still match. |
| RC6  | Fill policy: NULL for unknown facts; sentinel only on grouping dims, after a no-collision check. | `[OK]` | Sentinels `'UNKNOWN'`/`'UNCLASSIFIED'` only on grouping dim attrs; `original_invoice_ref` (a fact) left NULL. 0-collision verified. |
| RC7  | Money/qty `->` exact `NUMERIC`; dates `->` `DATE`; leading-zero IDs/codes stay `TEXT`. | `[OK]` | money `numeric(18,2)`, qty `numeric(18,4)`, `sale_date::date`; ids TEXT; `line_no` smallint. |
| RC8  | Keep returns; derive `is_return` from the authoritative type column, never the measure sign. | `[OK]` | `is_return = billing_type_code IN ('Z4','Z5','Z6','Z8','Z10')`. See is_return rule below. |
| RC9  | Keep the independent money measures (gross/net/tax/discount); drop only true duplicates. | `[OK]` | All four kept: sales_amount/net_amount/tax_amount/discount_amount. None collapsed. |
| RC10 | Unify categorical encodings to one standard; keep the original code if it is a stable join key. | `[OK]` | `billing_type` Arabic -> English, one standard; Z-code kept separately. See CASE map below. |
| RC11 | Add business rollups only from an analyst-supplied mapping; never invent the mapping. | `[OK]` | `business_segment` from an enumerated division->segment map; `ELSE 'UNMAPPED'`. See map below. |
| RC12 | Model a non-tree hierarchy as flat denormalized levels, not a snowflake. | `[OK]` | Product hierarchy kept flat in one `dim_product`; multi-parent overlaps preserved. |
| RC13 | Materialize silver as a TABLE via an idempotent numbered migration; transform order is load-bearing. | `[OK]` | `0001` DROP+CREATE in one `BEGIN/COMMIT`, numbered; 7-step transform order load-bearing. S4b layer-aware: 0 findings. |
| RC14 | Gold is a Kimball star: surrogate `_sk` keys, `-1` unknown member + FK `COALESCE`, degenerate dims. | `[OK]` | 6 dims + 1 fact; `_sk` IDENTITY PKs; `-1` member per dim; FK COALESCE(...,-1); 3 degenerate dims. |
| RC15 | Date dimension is a contiguous generated calendar over the full span (never `SELECT DISTINCT date`). | `[OK]` | `generate_series(2023-01-01 .. 2025-12-31, 1 day)` = 1,096 rows; spans all sale_dates, 0 missing. |
| RC16 | Reconcile measure totals at every layer and assert 0 orphan FKs before declaring the build done. | `[OK]` | Live: 0 hard orphan FKs on all 6 dims; 5 measures reconcile silver<->gold to the penny. |

**Integrity invariant:** every `[x]` row must have a matching Deviations entry. C086 has
zero `[x]` rows and an empty Deviations section -- consistent.

> **Namespace note (disambiguated).** The `RC1`-`RC16` ids are ADR 0002 cleaning/modeling
> defaults ("retail cleaning"). The `retail check` governance checker uses a separate
> `D1`-`D8` for its TMDL/DAX rules -- distinct prefixes, no collision. When this file
> says `RC7` it means the ADR cleaning default; a checker rule would read `D7`.

---

## Deviations

**Status for this table:** `none -- adopted 16/16`.

C086 overrode no ADR 0002 default. After live DB validation (2026-06-24) all 16 held, so
this section is empty -- a filled instance of "all defaults held." No per-table
deviation ADR is required.

---

## Resolved mapping decisions (the analyst-supplied tables RC8/RC10/RC11 reference)

These are not deviations -- they are the enumerated mappings the defaults REQUIRE be
supplied (never invented). They are recorded here so the gate review sees the full,
auditable value lists.

### is_return rule (RC8 -- authoritative column, not measure sign)

`is_return = (billing_type_code IN ('Z4','Z5','Z6','Z8','Z10'))`, else `false`.
Derived from the authoritative Z-code, NOT from the quantity/amount sign (the sign
misses zero-value and edge-case returns).

### billing_type CASE map (RC10 -- Arabic -> English, one standard, 10 arms + ELSE)

The Arabic strings below are REAL source data literals (the only non-ASCII content
permitted in this artifact); they must appear verbatim for the mapping to be auditable.

| Source value (Arabic) | English standard |
|-----------------------|------------------|
| اجل | Credit |
| فورى | Cash |
| مرتجع اجل | Credit Return |
| مرتجع فورى | Cash Return |
| Pick-Up Order | Pick-Up Order |
| Pick-Up Order Return | Pick-Up Order Return |
| توصيل | Delivery |
| مرتجع توصيل | Delivery Return |
| توصيل - اجل | Delivery Credit |
| مرتجع توصيل - اجل | Delivery Credit Return |
| (anything else) | UNMAPPED |

### business_segment rollup map (RC11 -- analyst-supplied division -> segment, ELSE 'UNMAPPED')

| Source `product_division` value | `business_segment` |
|---------------------------------|--------------------|
| OTC | PHARMA |
| RX | PHARMA |
| NUTRACEUTICAL | PHARMA |
| EVERYDAY ESSENTIALS | PHARMA |
| HOME HEALTH CARE | PHARMA |
| HIGH VALUE ITEMS | HVI |
| BEAUTY SKIN CARE | NON-PHARMA |
| TOTAL HAIR CARE | NON-PHARMA |
| BABY AND MOM | NON-PHARMA |
| COSMETICS | NON-PHARMA |
| PREMIUM SKIN CARE | NON-PHARMA |
| (anything else) | UNMAPPED |

### Sentinel choices (RC6 -- grouping dims only, 0-collision verified)

- `'UNKNOWN'` on: `salesperson_id`, `salesperson_name`, `job_title`, `product_brand`.
- `'UNCLASSIFIED'` on: `product_cluster`.
- All other missing values stay `NULL` (RC5). `original_invoice_ref` is a fact, not a
  grouping dim -> left `NULL`, no fill.

---

## Kit-level assumptions

Inherited from the architecture and constitution; true for every table:

- **Gold-only for Power BI.** The semantic model reads `gold` only; `bronze`/`silver`
  are upstream substrate.
- **Postgres-first medallion.** Storage is the DigitalOcean Postgres medallion
  (`bronze` `->` `silver` `->` `gold`); no DuckDB/Parquet-first copy in the MVP.
- **Mapping before silver.** No `silver.*` SQL until the source is profiled and mapped
  into committed, reviewed artifacts -- the source-mapping gate. This file is one of them.
- **`pbi-cli` is a later adapter, not the core.**
- **Validators:** static (`retail check`) vs live (`retail validate`) are distinct
  surfaces; the live results for C086 are in `reconciliation-report.md`.

---

## See also

- **Sibling templates:** `source-profile.md` (Phase 1 evidence), `source-map.yaml`
  (decisions), `unresolved-questions.md` (Phase 2 + Phase 4 gate),
  `reconciliation-report.md` (Phase 5/6 live acceptance).
- **Defaults this file checks against:** `../../docs/decisions/0002-retail-cleaning-defaults.md`
  (`RC1`-`RC16`).
- **Constitution principle realized:** "Defaults Then Deviations" in
  `../../.specify/memory/constitution.md`.
- **Architecture:** `../../docs/architecture/tower-bi-agent-kit.md`.
- **Method:** `../../docs/medallion-playbook.md`.
- **Worked example + compliance:** `../../docs/worked-examples/c086-pharmacy.md` +
  `../../docs/c086-adr0002-compliance.md` -- 16/16 defaults, 0 deviations, validated live.
