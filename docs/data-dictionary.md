# Data Dictionary

The per-warehouse catalog of medallion layers, tables, columns, and business rules.
This file is a **generic placeholder**: the kit ships no client warehouse, so there is
no populated catalog here. Each adopter's `retail init` + onboarding run produces the
concrete catalog for *their* tables.

## What a filled data dictionary contains

A completed data dictionary (see the worked example below) documents, per table:

- **Medallion layer** — `bronze` (raw landing) → `silver` (typed/cleaned) → `gold`
  (Kimball star; **Power BI reads gold only**). Built by `warehouse/migrations/`.
- **Grain** — one row = one `<business event>` (e.g. one invoice line item).
- **Row counts** — bronze landed → silver post-clean → gold fact/dim cardinalities,
  each dimension noting its `-1` "Unknown" member (Kimball unknown-member pattern).
- **Columns** — name, type, source column, PII flag, gold placement.
- **Key facts that shaped silver** — grain/uniqueness proof, returns identification,
  encoding/cleaning fixes, reconciliation deltas.
- **Reference mappings** — code→label lookups and any business-segment rollups.
- **Caveats & known limitations** — sign conventions, excluded PII, undercounts.

## Worked example (filled instance)

`docs/worked-examples/retail-store-sales.md` — a validated medallion table on the
public Kaggle "retail store sales (dirty)" dataset, carried through the full
seven-stage spine. It is a *filled instance*, never the universal schema.

## How to produce yours

Run the onboarding walk (`retail-onboard-table` → `source-mapping` →
`retail-build-warehouse`) against your own source; the catalog for your tables is
generated from the committed `mappings/<table>/` artifacts + the `warehouse/migrations/`
transforms.

> **Never commit client data.** Keep real names, PII values, and hosts out of tracked
> files — credentials live only in the gitignored `.env`; PII columns are dropped before
> silver (RC4) and must not re-enter any Power BI dataset without a governance review.
