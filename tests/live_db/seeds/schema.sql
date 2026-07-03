-- Shared DDL for the local live-validation suite (spec 082, data-model.md section 1).
--
-- Grain and foreign keys are declared LOGICALLY, not as engine constraints: no
-- PRIMARY KEY / UNIQUE / REFERENCES anywhere. This is load-bearing, not an
-- omission. The `retail validate` live checks exist to catch grain/FK/coverage
-- defects on MATERIALIZED rows that a real warehouse does NOT enforce as engine
-- constraints (silver staging does not PK-enforce the declared grain; gold
-- validates FKs post-load). If this schema enforced PK/FK as constraints, the
-- defect seeds (duplicate grain, orphan FK, date gap) would be REJECTED at INSERT
-- time -- the seed would fail, the check would skip, and the true-positive proof
-- (US2 / SC-002) would silently never run. So each grain/FK relation is a plain
-- column the check verifies, never a constraint the engine enforces.

CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- silver staging table (one fact-shaped table at silver grain).
CREATE TABLE silver.stg_order_line (
    order_line_id  TEXT    NOT NULL,   -- RC2 target: declared grain (logical, not a DB PK)
    order_date     DATE    NOT NULL,
    product_key    TEXT    NOT NULL,   -- logical FK target for the RC16 orphan check
    quantity       NUMERIC NOT NULL,
    net_amount     NUMERIC NOT NULL    -- RC16 reconciliation measure
);

-- gold date dimension: a contiguous generate_series calendar (RC15 target).
CREATE TABLE gold.dim_date (
    date_key  DATE NOT NULL,           -- logical calendar key (not a DB PK)
    year      INT  NOT NULL,
    month     INT  NOT NULL,
    day       INT  NOT NULL
);

INSERT INTO gold.dim_date (date_key, year, month, day)
SELECT d::date,
       EXTRACT(YEAR  FROM d)::int,
       EXTRACT(MONTH FROM d)::int,
       EXTRACT(DAY   FROM d)::int
FROM generate_series(DATE '2026-01-01', DATE '2026-01-31', INTERVAL '1 day') AS g(d);

-- gold conformed product dimension with a -1 unknown member (RC14 pattern).
CREATE TABLE gold.dim_product (
    product_key   TEXT NOT NULL,       -- logical key; includes the '-1' unknown member
    product_name  TEXT NOT NULL
);

INSERT INTO gold.dim_product (product_key, product_name) VALUES
    ('-1', 'Unknown'),
    ('P001', 'Widget'),
    ('P002', 'Gadget');

-- gold fact, same grain as silver.stg_order_line.
CREATE TABLE gold.fct_order_line (
    order_line_id  TEXT    NOT NULL,   -- logical grain (RC2 proves uniqueness on the rows)
    date_key       DATE    NOT NULL,   -- logical FK to gold.dim_date (RC15 proves coverage)
    product_key    TEXT    NOT NULL,   -- logical FK to gold.dim_product (RC16 proves 0 orphans)
    quantity       NUMERIC NOT NULL,
    net_amount     NUMERIC NOT NULL    -- reconciled against silver.stg_order_line.net_amount
);
