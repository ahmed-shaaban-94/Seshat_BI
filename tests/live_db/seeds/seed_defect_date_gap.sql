-- Date-coverage defect (data-model.md section 2): one gold fact row whose date_key
-- ('2026-02-15') is OUTSIDE dim_date's generated Jan-2026 range. Insertable because
-- the FK is logical, not a REFERENCES constraint -- check_date_coverage (V-RC15) is
-- what detects the gap. Grain unique and product_keys valid so PK/orphan/recon stay
-- clean (silver mirrors gold so reconciliation still balances).
INSERT INTO silver.stg_order_line (order_line_id, order_date, product_key, quantity, net_amount) VALUES
    ('OL-001', '2026-01-05', 'P001', 2, 20.00),
    ('OL-002', '2026-02-15', 'P002', 1, 15.50);

INSERT INTO gold.fct_order_line (order_line_id, date_key, product_key, quantity, net_amount) VALUES
    ('OL-001', '2026-01-05', 'P001', 2, 20.00),
    ('OL-002', '2026-02-15', 'P002', 1, 15.50);
