-- L4 value-check scenario (data-model.md section 2): a gold table with a known,
-- hand-computable sum(net_amount) total for use as the L4 target measure.
-- Total: 20.00 + 15.50 + 30.00 = 65.50.
INSERT INTO gold.fct_order_line (order_line_id, date_key, product_key, quantity, net_amount) VALUES
    ('OL-001', '2026-01-05', 'P001', 2, 20.00),
    ('OL-002', '2026-01-06', 'P002', 1, 15.50),
    ('OL-003', '2026-01-07', 'P001', 3, 30.00);
