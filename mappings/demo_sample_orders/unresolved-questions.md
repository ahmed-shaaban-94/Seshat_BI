# Unresolved Questions -- demo_sample_orders (spec 083 demo fixture)

> The Principle-V human-decision ledger for the mapping gate. GENERIC, invented
> sample -- not client data, not C086.

## Gate status: CLEARED

All questions answered; the map is reviewed and approved (see the illustrative
approval recorded in `readiness-status.yaml` `approvals[]`). This is a
pre-reviewed fixture: the "answers" below are authored as part of building the
demo, labeled illustrative, never inferred by a `demo run`.

## Questions (all answered)

- **Q1 (grain):** one order line per row? -> YES. `order_id` measured unique
  (ratio 1.00). Answered: illustrative fixture owner.
- **Q2 (PII):** any customer-identifying column? -> NO. None present in the
  sample. No PII ruling required. Answered: illustrative fixture owner.
- **Q3 (business rollups):** any value->group rollup needed (e.g. category
  hierarchy)? -> NO. `product_category` is used as-is, flat. Answered:
  illustrative fixture owner.
- **Q4 (sentinel-vs-null):** any column needing a sentinel? -> NO. No missing
  values in the sample; gold dims use the standard `-1` unknown member (RC14).
  Answered: illustrative fixture owner.

No build-blocking question remains.
