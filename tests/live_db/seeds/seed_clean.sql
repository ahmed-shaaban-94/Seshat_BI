-- Clean scenario (data-model.md section 2): all checks pass, L4 matches.
-- 3 order lines; all dates in dim_date; all product_keys present; silver/gold
-- net_amount sums equal to the penny.
INSERT INTO silver.stg_order_line (order_line_id, order_date, product_key, quantity, net_amount) VALUES
    ('OL-001', '2026-01-05', 'P001', 2, 20.00),
    ('OL-002', '2026-01-06', 'P002', 1, 15.50),
    ('OL-003', '2026-01-07', 'P001', 3, 30.00);

INSERT INTO gold.fct_order_line (order_line_id, date_key, product_key, quantity, net_amount) VALUES
    ('OL-001', '2026-01-05', 'P001', 2, 20.00),
    ('OL-002', '2026-01-06', 'P002', 1, 15.50),
    ('OL-003', '2026-01-07', 'P001', 3, 30.00);
