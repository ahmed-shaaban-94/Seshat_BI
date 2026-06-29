# Reconciliation Report -- `sales_c086`

> The LIVE acceptance blank for this table. The other four artifacts are authored
> BEFORE silver SQL; this one is completed only AFTER silver + gold are built and a
> live DB is reachable. Right now the **gate is shut and no silver/gold exists**, so
> the live results below are `PENDING`. Only the SOURCE (bronze) baseline is filled,
> measured 2026-06-29. ASCII only.

---

## What this report is (and is not)

Documents the LIVE acceptance gates (playbook Phase 5/6; ADR RC2, RC15, RC16) --
checks provable only against a running database, implemented as `retail validate`
(`src/retail/validate.py`): PK uniqueness (RC2), date coverage (RC15), 0 orphan FKs
(RC16), penny-exact reconciliation (RC16).

> **STATUS: PENDING BUILD.** silver/gold for `sales_c086` were dropped and not rebuilt
> in this session; the source-mapping gate is OPEN (see `unresolved-questions.md`).
> The Observed columns below stay `PENDING` until (a) the gate clears, (b) the silver
> + gold migrations are authored and applied, and (c) a read-only `retail validate`
> run is performed. The SOURCE baseline is recorded now so the later run has a
> reconciliation target.

> Namespace note: `RC2`/`RC15`/`RC16` are ADR 0002 cleaning defaults, distinct from the
> checker's `D1`-`D8` TMDL/DAX rules.

---

## Run header

| Field | Value |
|-------|-------|
| Table id | `sales_c086` |
| Silver object | `silver.sales_c086` (NOT YET BUILT) |
| Gold objects | `gold.fct_sales` + `gold.dim_product`/`dim_customer`/`dim_salesperson`/`dim_billing_type` + `gold.dim_date` (NOT YET BUILT) |
| Run date | `<PENDING -- live run not yet performed>` |
| DB cluster | `db-pgsql-fra1-29712` (fra1) |
| Database | `ezaby_demo` (confirmed -- holds the data; `defaultdb` is empty) |
| Run by | `<PENDING>` |
| Connection | **READ-ONLY.** Credentials from gitignored `.env` at runtime; no writes. |

---

## 0. SOURCE baseline (bronze, measured 2026-06-29)

Recorded now as the reconciliation target. These are totals over **all 249,106
landed bronze rows** -- they will NOT equal silver until the Q4 filters (2,190 rows)
are applied. The whole point of the report is to account for the difference.

| Metric | bronze.sales_c086_raw |
|--------|------------------------|
| Row count | 249,106 |
| sum(gross_sales) | 38,834,389.31 |
| sum(net_sales) | 35,727,363.84 |
| sum(tax) | 1,110,981.60 |
| sum(dis_tax) [discount] | -1,922,141.75 |
| sum(quantity) | 314,608.67 |
| Expected silver row count (after Q4 filters) | 246,916 (= 249,106 - 2,190) |

---

## 1. PK uniqueness (ADR RC2)

**Gate:** silver row count = distinct PK tuples, 0 NULL PK, verified on TRANSFORMED rows.

| Check | Expected | Observed |
|-------|----------|----------|
| Silver row count | 246,916 (pending Q4 confirm) | PENDING |
| Distinct PK tuples `(invoice_no, line_no)` | = row count | PENDING |
| NULL PK values | 0 | PENDING |

**Result:** PENDING -- landed-data proof exists (249,106 = 249,106 distinct, 0 NULL,
source-profile.md); RC2 requires re-proof on the silver output once built.

---

## 2. Date-dim coverage (ADR RC15)

**Gate:** `gold.dim_date` is a contiguous `generate_series` calendar spanning every real
`sale_date`, 0 missing.

| Check | Expected | Observed |
|-------|----------|----------|
| Calendar span | 2023-01-01 .. 2025-12-31 | PENDING |
| Calendar row count | 1,096 (contiguous, 3 yrs incl. 2024 leap) | PENDING |
| Contiguous (no missing interior days) | yes | PENDING |
| Real fact dates outside the calendar | 0 | PENDING |

**Result:** PENDING. Source fact has 1,094 distinct dates within 2023-01-01..2025-12-31.

---

## 3. Orphan FKs (ADR RC16)

**Gate:** 0 hard orphan FKs across all dims; rows on each `-1` member counted as a DQ signal.

| Dimension | Hard orphan FKs (expected 0) | Rows on `-1` unknown member (DQ signal) |
|-----------|------------------------------|-----------------------------------------|
| `dim_product` | PENDING | PENDING |
| `dim_customer` | PENDING | PENDING -- WATCH: ~85,911 walk-in (`C086`) rows may land here if Q6 routes them to `-1` instead of a `WALK_IN` member |
| `dim_salesperson` | PENDING | PENDING -- WATCH: ~1,748 rows have blank `personel_number` |
| `dim_billing_type` | PENDING | PENDING |

**Result:** PENDING.
**DQ signals (predicted from source profile):** customer walk-in contamination (Q6) and
salesperson blanks are the two members to count once built.

---

## 4. Cross-layer measure reconciliation (ADR RC16)

**Gate:** every measure total matches to the penny source -> silver -> gold (-> BI).
Source column = bronze total; silver/gold = after the Q4 filters.

| Measure | Source (bronze) | Silver | Gold | BI | Match? |
|---------|-----------------|--------|------|----|--------|
| gross_sales | 38,834,389.31 | PENDING | PENDING | n/a | PENDING |
| net_sales | 35,727,363.84 | PENDING | PENDING | n/a | PENDING |
| tax_amount | 1,110,981.60 | PENDING | PENDING | n/a | PENDING |
| discount_amount | -1,922,141.75 | PENDING | PENDING | n/a | PENDING |
| quantity | 314,608.67 | PENDING | PENDING | n/a | PENDING |
| Row count | 249,106 | PENDING (246,916 expected) | PENDING | n/a | PENDING |

**Result:** PENDING. NOTE: source != silver by design (the Q4 filters remove 2,190 rows);
the silver totals must equal the bronze totals minus the filtered rows' contribution, and
that delta must be explained, not rounded away.

---

## Verdict

| Category | ADR | Playbook | Result |
|----------|-----|----------|--------|
| 1. PK uniqueness | RC2 | Phase 5 | PENDING |
| 2. Date-dim coverage | RC15 | Phase 6 | PENDING |
| 3. Orphan FKs | RC16 | Phase 6 | PENDING |
| 4. Cross-layer reconciliation | RC16 | Phase 5/6 | PENDING |

**Overall:** **PENDING** -- no silver/gold built; the source-mapping gate is OPEN. This
report is the blank that the live `retail validate` run fills once the gate clears, the
build is authored + applied, and the 6 unresolved questions are answered.

## See also

- Method: `docs/medallion-playbook.md` Phase 5 (silver) + Phase 6 (gold).
- Defaults: `docs/decisions/0002-retail-cleaning-defaults.md` (RC2, RC15, RC16).
- Live surface: `src/retail/validate.py` (`retail validate`).
- Sibling artifacts: `source-profile.md`, `source-map.yaml`, `assumptions.md`,
  `unresolved-questions.md` (this folder).
- Prior worked example (reference, NOT reused): `docs/worked-examples/c086-pharmacy.md` Sec 5.
