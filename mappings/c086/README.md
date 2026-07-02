# mappings/c086 -- SUPERSEDED map (history) + CURRENT metric contracts

> **Status (2026-07-02): the five mapping artifacts in this folder are SUPERSEDED.**
> They document the FIRST c086 build (migrations 0001/0002) and are retained as
> history only. The current, human-approved map for `table_id: sales_c086` lives in
> [`mappings/sales_c086/`](../sales_c086/) and is built by migrations 0005/0006.
> Where the two folders disagree (PK, invoice-column identity, kept measures,
> business rollup), **`mappings/sales_c086/` wins**. Do not build from this map.
>
> **The `metrics/` subfolder is NOT superseded** -- its 33 metric contracts bind the
> CURRENT (0006) gold star (`gross_sales`, `purchaser_sk`, the `WALK_IN` remap) and
> remain the live contract store for the c086 semantic model.

## Known inaccuracies in the superseded artifacts (adversarial audit, 2026-07-02)

Recorded here rather than silently rewritten, so the history stays reviewable:

1. **Back-authored, never human-approved.** `source-map.yaml` `reviewed_by` says
   "back-authored from committed 0001/0002" -- the map was written FROM the SQL it
   was meant to gate (gate order inverted), and no `approvals[]` record exists for
   it. Its `Gate status: CLEARED` rests on mechanical live validation, not a named
   human decision. The successor map carries a real recorded approval (2026-07-02).
2. **Column coverage was overstated.** The map claims "30 total ... every source
   column appears", but the live profile of the same bronze table records **48
   landed columns**; 16 business columns (certification, assignment, salse_not_tax,
   fi_document_no, dis_tax, paid, kzwi1, crm_order, item_status, mat_group_2, knumv,
   cosm_mg, area_mg, ref_return_date, billing_document, insurance_tel) never
   received a keep/drop decision here. The successor map decides all 48.
3. **Phantom column.** The map's PII inventory lists `insurance_phone`; the actual
   landed column is `insurance_tel` (see `../sales_c086/source-profile.md`).
4. **Contradicted rollup.** Q4 here records an analyst-supplied `business_segment`
   rollup (PHARMA/HVI/NON-PHARMA). The successor records **none** analyst-supplied
   (RC11: "none requested; none invented") and migration 0005 builds none.
5. **Different PK story.** This map declares PK `(invoice_no, line_no)`; the
   approved map uses a generated surrogate `sale_sk` with the natural key
   `(billing_document, item_no)` kept silver-only as the uniqueness proof.

## What remains valid

- `reconciliation-report.md` records a REAL read-only validation run (2026-06-24)
  -- but against the superseded 0001/0002 star. It does not certify the current
  0005/0006 star, whose live validation is PENDING
  (see `../sales_c086/reconciliation-report.md`).
- The narrative worked example (`docs/worked-examples/c086-pharmacy.md`) still
  describes the journey; read it with this supersession note in mind.

## Redaction note (2026-07-02)

Per the data-owner's redaction decision (adversarial audit, finding C16): exact
client financial totals were masked to rounded figures or `[masked]` across the
mapping artifacts and metric contracts; manager/store names were replaced with
placeholders; and the rendered KPI deliverable
(`metrics/c086-kpi-deliverable.html`) was REMOVED from the tracked tree --
client deliverables full of exact figures live outside git. Git HISTORY retains
earlier revisions; a history purge is a separate, coordinated step.
