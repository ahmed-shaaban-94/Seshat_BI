# Assumptions -- demo_sample_orders (spec 083 demo fixture)

> Records which ADR-0002 (RC1-RC16) cleaning/modeling defaults were ADOPTED as-is
> vs DEVIATED from, per Principle VI. Every deviation must cite a triggering data
> fact. GENERIC, invented sample -- not client data, not C086.

## Adopted as-is (no deviation)

- **RC1** (faithful bronze landing): CSV landed all-TEXT.
- **RC2** (PK verified on transformed data): `order_id` measured unique (ratio 1.00).
- **RC3** (drop no-signal columns): none dropped -- all 9 columns carry signal.
- **RC7** (type discipline): `quantity` -> INTEGER; `unit_price`/`line_total` ->
  exact NUMERIC (money); `order_id` kept TEXT (alphanumeric id).
- **RC14** (gold `-1` unknown member): each conformed dim gets a `-1` unknown member.
- **RC15** (contiguous date dim): `dim_date` built from a `generate_series` calendar
  spanning `order_date`.
- **RC16** (reconciled totals, zero orphan FKs): silver/gold `line_total` sums
  reconcile; all FKs resolve.

## Deviations

- None. This sample is deliberately simple (no returns, no discount flag, no
  customer PII) so no RC default needed a data-fact-justified deviation. The
  worked example (`docs/worked-examples/retail-store-sales.md`) remains the
  reference for the richer deviation stories (RC4 customer_id, RC8 returns).
