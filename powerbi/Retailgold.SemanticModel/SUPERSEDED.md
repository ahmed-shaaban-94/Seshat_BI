# SUPERSEDED - Retailgold.SemanticModel

Status: SUPERSEDED (2026-07-02, adversarial audit findings C2 + C15).
Retained for history only. Do NOT refresh, build from, or cite this model as
current evidence.

## This model is DEAD against the current gold schema

This model cannot refresh against the authoritative gold DDL. Migration
`warehouse/migrations/0006_create_gold_sales_c086_star.sql` rebuilt
`gold.fct_sales` with only two measures -- `gross_sales` + `quantity` -- and
DROPPED the columns this model binds to:

- `sales_amount`  (bound by `TotalSales = SUM(sales_amount)`)
- `net_amount`    (bound by `NetSales  = SUM(net_amount)`)
- `tax_amount`    (bound by `TotalTax  = SUM(tax_amount)`)
- `discount_amount` (bound by `TotalDiscount = SUM(discount_amount)`)

It also binds dimension attributes that 0006's `gold.dim_product` does not
have: `product_brand`, `product_group`, `business_segment`. (0006's
`dim_product` carries `brand`, `category`, `subcategory`, `segment`,
`division`, `cluster` instead.)

Its `partition` reads `Schema = "gold", Item = "fct_sales"` -- the very table
0006 rebuilt -- so a refresh against the live gold DB would FAIL on the missing
columns. The measure and table definitions in `definition/` are left unchanged
(tombstone only); they are simply no longer refreshable.

## The current model

The current, refreshable c086 semantic model is:

    powerbi/c086 _sales.SemanticModel

(Note the space before `_sales` in the folder name.) It binds to the live 0006
gold star (`gross_sales`, `quantity`, `is_return`).

## NetSales means something DIFFERENT here (finding C15)

`NetSales` is NOT the same measure across the two models, despite the shared
name:

- THIS (dead) model: `NetSales = SUM('gold fct_sales'[net_amount])`
  -- net of DISCOUNTS (a discount-net revenue figure).
- Current c086 model: `NetSales = SUM('gold fct_sales'[gross_sales])`
  -- net of RETURNS (return lines carry negative `gross_sales`, so a plain SUM
  is already net of returns).

They are different measures. Do not treat this model's discount-net `NetSales`
as evidence for the current model's return-net `NetSales`. Note also: the
current gold star has NO discount column at all, so no live, refreshable
discount-net measure exists anywhere -- the discount-net definition below is
retained for history only.

## Do not

- Do not refresh this model.
- Do not build a dashboard or new model from it.
- Do not cite its measures as current / proven readiness evidence.
