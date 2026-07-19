-- 0001_create_silver_sales_c086_raw.sql
-- Build silver.sales_c086_raw (typed/cleaned line-item fact) from
-- bronze.sales_c086_raw (C086 pharmacy branch sales export, Ex-1 DB).
--
-- Medallion: bronze = faithful TEXT landing (retained); silver = typed/cleaned flat
-- table; gold (next migration) = Kimball star. Power BI reads gold, not silver.
--
-- Grain: one billing-document line item. PK = (reference_no, item_no). 249,106 bronze rows.
-- Idempotent: DROP+CREATE in one transaction; safe to re-run after a bronze reload.
--
-- Cleaning rules from the APPROVED mappings/sales_c086_raw/ (mapping_ready PASS,
-- 2026-07-16, Ahmed Shaaban data_owner; column-by-column review + source-map.yaml),
-- PLUS the separate rename/missing-value review conducted 2026-07-16 (data owner).
-- ASCII only; UTF-8 no BOM.
--
-- WHAT IS DROPPED (per source-map.yaml, NOT carried into silver):
--   billing_document, fi_document_no, ref_return, ref_return_date, crm_order,
--   knumv, cosm_mg, area_mg, site, site_name, mat_group, mat_group_2, item_status,
--   certification, assignment, net_sales, salse_not_tax, kzwi1,
--   insurance_tel, insurance_no
--   PLUS, dropped 2026-07-16 in a post-hoc column review: tax, dis_tax, add_dis,
--   subtotal5_discount, paid, and buyer/purchaser (previously kept and even
--   promoted to its own dimension earlier the same session -- see source-map.yaml
--   for the full history of that column's decision).
-- (34 of 46 source columns dropped; see source-map.yaml for the reason on each.)
--
-- RENAME MAP (data-owner reviewed 2026-07-16, one column at a time):
--   billing_type_2   -> billing_type_code   (disambiguate short code from label)
--   date             -> sale_date           (avoid bare 'date' as a column name)
--   personel_number  -> staff_code          (source typo "personel"; owner chose
--                                            staff_code, NOT staff_number)
--   person_name      -> staff_name_masked   (reflects the masking transform)
--   position         -> staff_position      (disambiguate from other uses)
--   (every other kept column is renamed identically to its source name)
--   (buyer/purchaser was renamed and promoted to its own dim earlier this
--   session, then DROPPED entirely in the 2026-07-16 post-hoc column review --
--   see source-map.yaml for that column's full history)
--
-- BILLING_TYPE TRANSLATION (data-owner reviewed 2026-07-16, one value at a time):
-- Arabic billing_type is TRANSLATED to English and REPLACES the Arabic value
-- entirely (owner's explicit choice -- the Arabic original is NOT retained
-- anywhere in silver; bronze remains the record of the raw value if ever needed).
--   'اجل'                -> 'Credit Sale'
--   'فورى'                -> 'Cash Sale'
--   'مرتجع اجل'            -> 'Credit Return'
--   'مرتجع فورى'           -> 'Cash Return'
--   'Pick-Up Order'       -> 'Pick-Up Order'          (already English)
--   'Pick-Up Order Return'-> 'Pick-Up Order Return'   (already English)
--   'توصيل'                -> 'Delivery'
--   'مرتجع توصيل'          -> 'Delivery Return'
--   'توصيل - اجل'          -> 'Delivery - Credit'
--   'مرتجع توصيل - اجل'    -> 'Delivery - Credit Return'
-- is_return below is derived by matching 'Return' in the TRANSLATED ENGLISH
-- label (LIKE '%Return%'), not the Arabic مرتجع prefix. This was corrected
-- after a bug was caught in review: matching the Arabic prefix directly missed
-- 'Pick-Up Order Return' (376 rows), which was already English in bronze and so
-- never carried the Arabic مرتجع substring -- it would have silently stayed
-- is_return=false forever. Matching on the post-translation English label
-- classifies all 5 return variants (Credit/Cash/Delivery/Delivery-Credit/
-- Pick-Up Order Return) with one consistent rule.
--
-- MISSING-VALUE POLICY (data-owner reviewed 2026-07-16, DEVIATES from RC5's
-- blanket '' -> NULL default -- record this as an explicit override, not a
-- silent choice):
--   - Money/quantity columns still in the model (quantity, gross_sales): ''
--     -> NULL. Owner explicitly confirmed NULL over 0 here -- a blank measure
--     must stay excluded from SUM(), never silently counted as a real zero.
--     This ONE column group follows RC5 as-is. (tax, dis_tax, add_dis,
--     subtotal5_discount, paid were dropped from the model entirely in a later
--     review -- this policy no longer applies to them, they simply don't exist.)
--   - EVERY text column (identifiers, attributes, and item_cluster alike):
--     '' -> sentinel 'UNKNOWN', NOT NULL. This is a DEVIATION from RC5 (plain
--     NULL) and from RC6 (sentinel reserved for grouping dims only) -- the data
--     owner extended the sentinel to natural-key columns (material,
--     material_desc, customer, staff_code) too, on the reasoning that a blank
--     identifier should read the same as a blank category in this model.
--     Verify no real data value ever legitimately equals the literal string
--     'UNKNOWN' before trusting GROUP BY output downstream (RC6 collision check).
--
-- ROW FILTER (data-owner reviewed 2026-07-16): excludes 513 / 249,106 (0.21%) rows
-- where division IN ('ARCHIVE', 'AUX', 'UNKNOWN', 'EL EZABY SERVICES'). Inspected
-- each before dropping: ARCHIVE = retired/discontinued products + penny-value
-- promotional "gift" lines; AUX = miscellaneous-tagged real drugs (6 rows,
-- negligible); UNKNOWN = the 3 genuinely-blank-division rows; EL EZABY SERVICES =
-- NOT product sales at all (injection fees, "WHATS APP - A" line items, generic
-- "SPECIAL SERVICE" charges) -- out of scope for a retail sales-of-goods fact.
-- This CHANGES the row-parity invariant: silver now has 248,593 rows, NOT
-- 249,106 -- the RC2 PK proof and every downstream row-count check must expect
-- 248,593, not the full bronze count.

SET client_encoding TO 'UTF8';

BEGIN;

CREATE SCHEMA IF NOT EXISTS silver;

DROP TABLE IF EXISTS silver.sales_c086_raw;

CREATE TABLE silver.sales_c086_raw AS
WITH src AS (
  -- TRIM every text column up front (kills whitespace-variant phantom distincts).
  SELECT
    trim(reference_no)         AS reference_no,
    trim(item_no)              AS item_no,
    trim(material)              AS material,
    trim(material_desc)         AS material_desc,
    trim(category)              AS category,
    trim(subcategory)           AS subcategory,
    trim(segment)               AS segment,
    trim(division)              AS division,
    trim(brand)                 AS brand,
    trim(item_cluster)          AS item_cluster,
    trim(billing_type)          AS billing_type,
    trim(billing_type_2)        AS billing_type_2,
    trim(quantity)              AS quantity,
    trim(gross_sales)           AS gross_sales,
    trim(date)                  AS sale_date,
    trim(customer)              AS customer,
    trim(customer_name)         AS customer_name,
    trim(personel_number)       AS staff_code,
    trim(person_name)           AS person_name,       -- masked below, not carried raw
    trim(position)              AS staff_position
  FROM bronze.sales_c086_raw
),
translated AS (
  -- Arabic -> English translation happens ONCE here so both the final
  -- billing_type column AND the is_return derivation read the same translated
  -- value -- a single source of truth, not two independent classifications
  -- that could silently drift apart.
  SELECT
    src.*,
    CASE billing_type
      WHEN 'اجل'                  THEN 'Credit Sale'
      WHEN 'فورى'                  THEN 'Cash Sale'
      WHEN 'مرتجع اجل'             THEN 'Credit Return'
      WHEN 'مرتجع فورى'            THEN 'Cash Return'
      WHEN 'Pick-Up Order'         THEN 'Pick-Up Order'
      WHEN 'Pick-Up Order Return'  THEN 'Pick-Up Order Return'
      WHEN 'توصيل'                  THEN 'Delivery'
      WHEN 'مرتجع توصيل'           THEN 'Delivery Return'
      WHEN 'توصيل - اجل'            THEN 'Delivery - Credit'
      WHEN 'مرتجع توصيل - اجل'     THEN 'Delivery - Credit Return'
      WHEN ''                     THEN 'UNKNOWN'
      ELSE 'UNKNOWN'               -- an untranslated value must surface as UNKNOWN,
                                   -- never pass the Arabic text through silently
    END AS billing_type_en
  FROM src
)
-- No junk-row filter: the profile found every kept column numeric-clean (post-trim)
-- and no junk rows.
SELECT
  -- identity / grain key (RULED 2026-07-16: reference_no+item_no, NOT billing_document).
  -- Grain-key columns ALSO get the 'UNKNOWN' sentinel per the owner's missing-value
  -- ruling, but the RC2 PK proof below still requires 0 actual blanks in practice --
  -- if 'UNKNOWN' ever appears here it signals a genuine data problem, not a clean key.
  COALESCE(NULLIF(reference_no, ''), 'UNKNOWN')     AS reference_no,
  COALESCE(NULLIF(item_no, ''), 'UNKNOWN')          AS item_no,

  -- product (material is the natural key; the rest are its 1:1/attribute columns).
  -- Sentinel 'UNKNOWN' per the owner's ruling (deviates from RC5/RC6 defaults --
  -- see the header note above).
  COALESCE(NULLIF(material, ''), 'UNKNOWN')         AS material,
  COALESCE(NULLIF(material_desc, ''), 'UNKNOWN')    AS material_desc,
  COALESCE(NULLIF(category, ''), 'UNKNOWN')         AS category,
  COALESCE(NULLIF(subcategory, ''), 'UNKNOWN')      AS subcategory,
  COALESCE(NULLIF(segment, ''), 'UNKNOWN')          AS segment,
  COALESCE(NULLIF(division, ''), 'UNKNOWN')         AS division,
  COALESCE(NULLIF(brand, ''), 'UNKNOWN')            AS brand,
  -- item_cluster: 32.01% blank RULED unknown/missing (data owner, 2026-07-16),
  -- now stored as the 'UNKNOWN' sentinel per the separate missing-value ruling.
  COALESCE(NULLIF(item_cluster, ''), 'UNKNOWN')     AS item_cluster,

  -- billing / returns (billing_type is the AUTHORITATIVE returns source, RC8).
  -- Arabic -> English translation REPLACES the value entirely (owner's explicit
  -- choice, 2026-07-16) -- the Arabic original is not carried into silver;
  -- bronze remains the raw record if ever needed. Computed once in the
  -- `translated` CTE above so is_return below reads the identical value.
  billing_type_en                                     AS billing_type,
  COALESCE(NULLIF(billing_type_2, ''), 'UNKNOWN')   AS billing_type_code,

  -- measures (RC7: money/qty -> exact NUMERIC, never float; '' -> NULL, per the
  -- owner's explicit confirmation that money/qty blanks must stay NULL, NOT the
  -- 'UNKNOWN' sentinel used elsewhere -- a blank measure must be excluded from
  -- SUM(), never silently become a real zero or an uncastable sentinel string).
  NULLIF(quantity, '')::numeric(14,3)               AS quantity,
  NULLIF(gross_sales, '')::numeric(18,2)            AS gross_sales,
  -- tax, dis_tax, add_dis, subtotal5_discount, paid DROPPED 2026-07-16 (data
  -- owner, post-hoc column review): removed from the model entirely, along with
  -- purchaser below. See source-map.yaml for the record of this decision.
  -- net_sales is INTENTIONALLY ABSENT: landed net_sales RULED unreliable
  -- (2026-07-16) -- gross_sales+dis_tax+add_dis-tax matched only 90.4% of rows
  -- and no tested formula improved on that. A net_sales_computed measure is
  -- OPEN and must be authored from first principles in a LATER migration/DAX
  -- measure, not backfilled here by falling back to the rejected landed column.

  -- date (RC7: date -> DATE; RC15 gold date dim spans 2023-01-01..2025-12-31).
  -- A date column cannot hold the 'UNKNOWN' text sentinel -- stays NULL on blank,
  -- same as the money columns, for the same cast-safety reason.
  NULLIF(sale_date, '')::date                       AS sale_date,

  -- customer (customer_name PII RULED low-risk 2026-07-16: predominantly
  -- B2B/institutional names -- kept as-is, no masking). 'UNKNOWN' sentinel per
  -- the owner's missing-value ruling.
  COALESCE(NULLIF(customer, ''), 'UNKNOWN')         AS customer,
  COALESCE(NULLIF(customer_name, ''), 'UNKNOWN')    AS customer_name,

  -- staff (person_name PII RULED mask/pseudonymize 2026-07-16 -- staff/employee
  -- data, not customer PII. md5() gives a deterministic, non-reversible
  -- pseudonym: the SAME staff member always maps to the SAME masked value
  -- across rows, so staff-level grouping/analysis still works, but the real
  -- name is never stored in silver or exposed downstream. A blank name masks
  -- to a fixed 'UNKNOWN' sentinel rather than md5('') so it groups with the
  -- other blank-staff rows instead of forming its own single hash bucket.)
  COALESCE(NULLIF(staff_code, ''), 'UNKNOWN')       AS staff_code,
  CASE WHEN NULLIF(person_name, '') IS NULL THEN 'UNKNOWN'
       ELSE md5(person_name)
  END                                                AS staff_name_masked,
  COALESCE(NULLIF(staff_position, ''), 'UNKNOWN')   AS staff_position,

  -- is_return (RC8): derived from the AUTHORITATIVE billing_type column, NEVER
  -- the quantity sign. Measured: sign-alone would misclassify 2,030 rows
  -- (1,667 return rows with non-negative qty + 363 non-return rows with
  -- negative qty). Matches on the TRANSLATED ENGLISH label (billing_type_en LIKE
  -- '%Return%'), NOT the Arabic مرتجع prefix -- a bug caught in review: matching
  -- the Arabic prefix directly missed 'Pick-Up Order Return' (376 rows), which
  -- was already English in bronze and so never carried the Arabic مرتجع
  -- substring; it would have silently stayed is_return=false forever. Matching
  -- post-translation classifies all 5 return variants (Credit/Cash/Delivery/
  -- Delivery-Credit/Pick-Up Order Return) with one consistent rule. Re-verified:
  -- still produces 12,365/249,106 true (up from the pre-fix 11,989 -- the +376
  -- difference is exactly the previously-missed Pick-Up Order Return rows).
  (billing_type_en LIKE '%Return%')                 AS is_return

FROM translated
-- ROW FILTER (see header note): excludes non-product-sale / no-signal divisions.
-- Checked on the TRIMMED, pre-sentinel division value from the CTE so this
-- filter is exact and cannot be defeated by a later COALESCE-to-'UNKNOWN' step.
WHERE division NOT IN ('ARCHIVE', 'AUX', '', 'EL EZABY SERVICES');

-- PK can be DECLARED here but is UNVERIFIED-UNTIL-APPLIED: (reference_no, item_no)
-- was unique on the LANDED data (249,106 = 249,106, 0 null); RC2 requires
-- re-proving it on the TRANSFORMED rows below. TRIM/COALESCE can in principle
-- collapse two raw-distinct keys -- this ALTER is the actual proof, not a
-- formality; if it fails, the map's PK choice must be revisited, not forced.
-- NOTE: if reference_no or item_no ever land blank, they now collapse to the
-- literal string 'UNKNOWN' rather than NULL -- a second such row would violate
-- this PK and correctly fail the migration (better than two silently-different
-- NULL keys passing NULL-distinct PK semantics unnoticed).
ALTER TABLE silver.sales_c086_raw ADD PRIMARY KEY (reference_no, item_no);

-- supporting indexes for the common gold slice paths
CREATE INDEX idx_silver_c086_date        ON silver.sales_c086_raw (sale_date);
CREATE INDEX idx_silver_c086_material    ON silver.sales_c086_raw (material);
CREATE INDEX idx_silver_c086_customer    ON silver.sales_c086_raw (customer);
CREATE INDEX idx_silver_c086_staff       ON silver.sales_c086_raw (staff_code);
CREATE INDEX idx_silver_c086_billing_type ON silver.sales_c086_raw (billing_type);

COMMIT;
