-- PK-duplicate defect (data-model.md section 2): two gold+silver rows share the
-- same order_line_id (the declared grain). Insertable BECAUSE the grain is logical,
-- not a DB PK -- check_pk_uniqueness (V-RC2) is what detects the duplicate.
-- Dates and product_keys stay valid so the other three checks stay clean.
INSERT INTO silver.stg_order_line (order_line_id, order_date, product_key, quantity, net_amount) VALUES
    ('OL-001', '2026-01-05', 'P001', 2, 20.00),
    ('OL-001', '2026-01-06', 'P002', 1, 15.50);

INSERT INTO gold.fct_order_line (order_line_id, date_key, product_key, quantity, net_amount) VALUES
    ('OL-001', '2026-01-05', 'P001', 2, 20.00),
    ('OL-001', '2026-01-06', 'P002', 1, 15.50);
