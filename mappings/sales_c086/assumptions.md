# Assumptions -- `sales_c086`

> Per-table record of which ADR 0002 cleaning/modeling defaults (RC1-RC16) this
> table adopted as-is vs deviated from. Derived from an independent live profile
> (2026-06-29); NOT copied from the prior c086 worked example. ASCII only.

| Field | Value |
|-------|-------|
| Table id | `sales_c086` (`bronze.sales_c086_raw` -> `silver.sales_c086`) |
| Date | `2026-06-29` |
| Author | agent (fresh analysis) |
| Source profile | `mappings/sales_c086/source-profile.md` (the profiled evidence) |
| Source map | `mappings/sales_c086/source-map.yaml` (keep/drop/type/grain/star decisions) |
| Per-table ADR | `<TBD -- docs/decisions/00NN-sales_c086-deviations.md if any deviation is confirmed at review>` |

**Data flow:** `source-profile.md` (evidence) + `source-map.yaml` (decisions) ->
**`assumptions.md`** (which defaults held / were overridden).

---

## Defaults adopted as-is

`[OK]` = adopted unchanged; `[x]` = deviated (recorded in Deviations below).

| ADR id | Default summary (generic ruling) | Adopted? | Note |
|--------|----------------------------------|----------|------|
| RC1  | Model at lowest grain; decide grain first. | `[OK]` | invoice line item; 2.42 lines/invoice |
| RC2  | Verify PK on data + re-verify on transformed output. | `[OK]` | `(billing_document,item_no)` 249,106=249,106, 0 NULL on landed data; silver must re-prove |
| RC3  | Drop no-signal columns. | `[OK]` | `knumv`/`ref_return_date` 100% empty; `crm_order` 99.5%; redundant `mat_group_2` |
| RC4  | Remove PII before BI layer, decided early. | `[OK]` | 7 PII columns dropped by default; governance sign-off is Q2 |
| RC5  | `''` -> NULL; measure missingness as `'' OR NULL`. | `[OK]` | applied to all columns |
| RC6  | NULL for unknown facts; sentinel only on grouping dims, no-collision checked. | `[x]` | see Deviations -- single-branch constants + walk-in member need an explicit ruling (Q3/Q6) |
| RC7  | Money/qty -> NUMERIC; dates -> DATE; leading-zero ids stay TEXT. | `[OK]` | 5 measures numeric; `invoice_no`/`product_id`/`customer_id` TEXT; `line_no` smallint |
| RC8  | Derive `is_return` from authoritative type column, not measure sign. | `[OK]` | from `billing_type_2` Z-codes; confirmation is Q1 |
| RC9  | Keep independent money measures; drop true duplicates. | `[OK]` | kept gross/net/tax/discount/qty; dropped near-dups (`salse_not_tax`,`subtotal5_discount`,`kzwi1`) -- Q5 confirm |
| RC10 | Unify categorical encodings; keep original code if a stable join key. | `[OK]` | billing_type_2 (code) kept as join key; Arabic label kept as attribute |
| RC11 | Business rollups only from analyst-supplied mapping; never invent. | `[OK]` | NO rollup invented; none added (could be a future analyst request) |
| RC12 | Model non-tree hierarchy as flat denormalized levels. | `[OK]` | product hierarchy flat (36 subcats are multi-parent) |
| RC13 | Materialize silver as TABLE via idempotent numbered migration. | `[OK]` | applies at build; no silver SQL written yet (gate shut) |
| RC14 | Gold Kimball star: `_sk`, `-1` member + FK COALESCE, degenerate dims. | `[OK]` | 1 fact + 4 entity dims + date dim; 4 degenerate dims |
| RC15 | Contiguous generated date dim over full span. | `[OK]` | `generate_series` 2023-01-01..2025-12-31 |
| RC16 | Reconcile measure totals every layer; 0 orphan FKs before done. | `[OK]` | deferred to live run (reconciliation-report.md, PENDING -- no build yet) |

**Integrity invariant:** every `[x]` row has a matching Deviations entry below.

> Namespace note: `RC1`-`RC16` are ADR 0002 cleaning defaults; the `retail check`
> governance checker uses a separate `D1`-`D8` for TMDL/DAX rules. No collision.

---

## Deviations

**Status for this table:** `1 deviation (RC6), + 1 honest data-quality divergence
from the prior run -- recorded below`.

| Field | Value |
|-------|-------|
| ADR id | `RC6` (fill policy: NULL vs sentinel) |
| What we did instead | For the `customer` column we propose a `WALK_IN` member rather than a plain `'' -> NULL`, and we drop the single-branch `site`/`site_name` to constants rather than modeling a `dim_branch`. |
| Triggering data fact | `customer = 'C086'` (the site code) on **85,911 rows (34.5%)** -- not a customer id; almost certainly walk-in/cash sales (source-profile.md, DQ issue #1). And `site`/`site_name`/`cosm_mg`/`area_mg` each have **1 distinct value** -- single-branch extract (source-profile.md per-column table). |
| Recorded in | this file + `unresolved-questions.md` Q3 and Q6 (the rulings that confirm the deviation are blocking questions, not agent decisions) |

**Honest divergence from the prior c086 run (not a defect, a transparency note).**
The prior worked example (`docs/worked-examples/c086-pharmacy.md`) reports C086 as
**16/16 defaults adopted, 0 deviations**, and a star of **1 fact + 6 dims** (including
`dim_branch`). This fresh analysis differs on two points, each grounded in the live data:
1. The contaminated `customer` field (85,911 rows = site code) is surfaced here as a
   blocking question (Q6); the prior run apparently resolved it without recording a
   deviation. We do not assume their resolution -- we raise it.
2. We collapse `dim_branch` to a constant because this extract is single-branch
   (1 distinct `site`). The prior run kept a 1-member `dim_branch` for conformance.
   Whether to keep it for multi-store future loads is Q3. **Both are defensible; we
   record ours and flag the difference rather than silently matching theirs.**

---

## Kit-level assumptions

Inherited from architecture/constitution (not per-table):
- **Gold-only for Power BI.** Semantic model reads `gold` only; `bronze`/`silver` are substrate.
- **Postgres-first medallion.** DigitalOcean Postgres `bronze -> silver -> gold`; no DuckDB/Parquet copy.
- **Mapping before silver.** No `silver.*` SQL until this artifact set is reviewed (the gate).
- **Validators are categories.** Static `retail check` (shipped) vs live `retail validate` (per-table live run pending).

## See also

- Defaults: `docs/decisions/0002-retail-cleaning-defaults.md` (RC1-RC16).
- Constitution: "Defaults Then Deviations" (`.specify/memory/constitution.md`).
- Sibling artifacts: `source-profile.md`, `source-map.yaml`, `unresolved-questions.md`,
  `reconciliation-report.md` (this folder).
- Prior worked example (reference, NOT reused): `docs/worked-examples/c086-pharmacy.md`.
