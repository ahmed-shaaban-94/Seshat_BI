-- Deterministic feature-133 seed. Values are synthetic and contain no secrets.
CREATE SCHEMA IF NOT EXISTS bronze;

DROP TABLE IF EXISTS bronze.retail_store_sales;
CREATE TABLE bronze.retail_store_sales (
    transaction_id TEXT,
    customer_id TEXT,
    category TEXT,
    item TEXT,
    price_per_unit TEXT,
    quantity TEXT,
    total_spent TEXT,
    payment_method TEXT,
    location TEXT,
    transaction_date TEXT,
    discount_applied TEXT
);

INSERT INTO bronze.retail_store_sales VALUES
    ('TXN-001', 'CUS-001', 'Food', 'Tea', '10.00', '2', '20.00', 'Card', 'Cairo', '2024-01-02', 'true'),
    ('TXN-002', 'CUS-002', 'Food', 'Coffee', '5.50', '3', '16.50', 'Cash', 'Giza', '2024-01-03', 'false'),
    ('TXN-003', '', 'Unknown', '', '7.00', '1', '7.00', 'Wallet', 'Cairo', '2024-01-04', ''),
    ('TXN-004', 'CUS-001', 'Home', 'Mug', '12.25', '2', '24.50', 'Card', 'Alexandria', '2024-01-05', 'true'),
    ('TXN-005', 'CUS-003', 'Home', 'Mug', '', '', '', 'Cash', 'Alexandria', '2024-01-06', '');
