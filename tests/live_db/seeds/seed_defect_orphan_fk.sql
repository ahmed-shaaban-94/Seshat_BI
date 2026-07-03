-- Orphan-FK defect (data-model.md section 2): one gold fact row whose product_key
-- ('P999') matches no dim_product row (and is not the '-1' unknown member).
-- Insertable because the FK is logical, not a REFERENCES constraint --
-- check_orphan_fks (V-RC16) is what detects the orphan. Grain unique, dates valid,
-- silver mirrors gold so reconciliation stays clean.
INSERT INTO silver.stg_order_line (order_line_id, order_date, product_key, quantity, net_amount) VALUES
    ('OL-001', '2026-01-05', 'P001', 2, 20.00),
    ('OL-002', '2026-01-06', 'P999', 1, 15.50);

INSERT INTO gold.fct_order_line (order_line_id, date_key, product_key, quantity, net_amount) VALUES
    ('OL-001', '2026-01-05', 'P001', 2, 20.00),
    ('OL-002', '2026-01-06', 'P999', 1, 15.50);
