-- Reconciliation defect (data-model.md section 2): silver and gold net_amount sums
-- differ by exactly one cent -- one gold row's amount is offset by 0.01 post-load.
-- Violates no constraint (it is a value mismatch, not a grain/FK/coverage defect) --
-- check_reconciliation (V-RC16) is what detects the one-cent gap. Grain unique,
-- dates and product_keys valid so PK/date/orphan stay clean.
INSERT INTO silver.stg_order_line (order_line_id, order_date, product_key, quantity, net_amount) VALUES
    ('OL-001', '2026-01-05', 'P001', 2, 20.00),
    ('OL-002', '2026-01-06', 'P002', 1, 15.50);

INSERT INTO gold.fct_order_line (order_line_id, date_key, product_key, quantity, net_amount) VALUES
    ('OL-001', '2026-01-05', 'P001', 2, 20.00),
    ('OL-002', '2026-01-06', 'P002', 1, 15.51);
