# Unresolved questions -- `sales_c086`

> The open questions that BLOCK the build -- the decisions the agent cannot make
> alone. Committed, reviewable form of the playbook's Phase 2 decision points +
> Phase 4 review gate. No `silver.*` SQL is written until every blocking question
> here is `answered`. Derived from the independent live profile (2026-06-29).
> ASCII only. Rule: the agent recommends, the analyst decides.

---

- **Table id:** `sales_c086` (El Ezaby pharmacy branch C086 sales)
- **Date raised:** `2026-06-29`
- **Raised by:** agent (fresh analysis)
- **Maps to playbook phases:** Phase 2 (decision points) + Phase 4 (review gate)
- **Gate status:** `OPEN` -- the build is blocked until every row below is `answered`.

---

## Open questions (the build is blocked until these are `answered`)

`Who must answer`: **analyst** (business meaning/grain/rollups), **governance**
(PII/publish-safety), **data-owner** (source semantics).

| ID | Question | Why it blocks | Who must answer | Proposed default (if unanswered) | Status | Resolution |
|----|----------|---------------|-----------------|----------------------------------|--------|------------|
| Q1 | Is `billing_type_2 IN ('Z4','Z5','Z6','Z8','Z10')` the authoritative return flag, and what is the full Arabic->English label map for all 10 codes? | `is_return` (RC8) and `dim_billing_type` labels cannot be built without the confirmed code semantics. | data-owner | Adopt the 5-code rule (each maps to an Arabic label meaning "return" -- transliterated `murtaja` -- and carries negative avg_net); label map per the observed 1:1 pairs; UNMAPPED codes raise loudly. | `open` | |
| Q2 | Publish-safety sign-off for the 7 PII columns (`person_name`, `buyer`, `customer_name`, `cosm_mg`, `area_mg`, `insurance_tel`, `insurance_no`) -- drop, or mask/hash with a stated need? | A published BI dataset is effectively irreversible; insurance phone/claim no. are patient-health-adjacent. Agent cannot rule "safe to publish". | governance | Drop all 7 before the BI layer (RC4). Never use RLS to hide a *column*. | `open` | |
| Q3 | This extract is single-branch (`site`='C086', 1 distinct value). Drop `site`/`site_name` to a constant, or keep a 1-member `dim_branch` for conformance with future multi-store loads? | Determines whether the gold star has a `dim_branch`. The map currently drops it (4 entity dims). | analyst | Drop to constant for this single-branch extract; add `dim_branch` only when a multi-branch load arrives. | `open` | |
| Q4 | Confirm the bronze->silver row filters: drop junk divisions (`AUX`/`ARCHIVE`/`EL EZABY SERVICES`/blank = 513 rows) AND zero-value lines (`quantity=0 AND gross_sales=0` = 1,680 rows), union 2,190 -> silver 246,916. | The silver row count and all measure totals depend on which rows are filtered. Wrong filter = wrong totals. | analyst | Apply both filters (they exactly account for the 2,190-row gap; no overlap). | `open` | |
| Q5 | Confirm the independent measure set = {gross_sales, net_sales, tax, discount(dis_tax), quantity}, and that `salse_not_tax`, `subtotal5_discount`, `kzwi1`, `add_dis`, `paid`, `fi_document_no` are droppable (near-duplicate or operational). | RC9 keeps independent measures and drops true duplicates; no money identity holds universally (78%/35%), so the call needs the data-owner's definition of the reported measures. | data-owner | Keep the 5; drop the 6 listed (near-dups / operational / unused finance ref). | `open` | |
| Q6 | The `customer` field is contaminated: **85,911 rows (34.5%) have `customer = 'C086'`** (the site code, not a customer id) -- almost certainly walk-in/cash sales. How should these be modeled in `dim_customer`: an explicit "Walk-in / Cash" member, or routed to the `-1` unknown member? | A naive `dim_customer` would gain an 85,911-row "customer" that is really *no customer*, distorting any customer-level analysis. NOTE: this is a VALUE REMAP (`customer='C086'` is present-but-wrong), NOT a missing-value sentinel -- a `missing_policy` would not fire on a non-null value. | analyst | Explicit `WALK_IN` member via `derived_columns.customer_id_clean` (a `CASE` remap in silver), preferred -- it is a meaningful business category, not "unknown". Alternative: leave raw id, let it COALESCE to the `-1` unknown member. Confirm business meaning first. | `open` | |

> Do not delete answered rows -- flip `Status` to `answered`, fill `Resolution`
> with the decision + date + who, so review sees the audit trail.

### Categories considered

- **Grain ambiguity (RC1/RC2):** resolved on the data -- `(billing_document,item_no)`
  unique, 0 NULL, 2.42 lines/invoice. No open question. (source-profile.md)
- **PII (RC4, governance):** Q2.
- **Business-rollup (RC11, analyst):** none requested; none invented. (If a
  division->segment rollup is wanted later, the analyst must supply the full map.)
- **Sentinel-vs-null (RC5/RC6):** dim grouping attributes get `UNKNOWN`/`UNCLASSIFIED`
  sentinels; facts stay NULL. The non-default sentinel choices are Q3/Q6.
- **Returns (RC8, data-owner):** Q1.
- **Hierarchy multi-parent (RC12):** resolved on the data -- 36 multi-parent subcats ->
  flat. No open question.

---

## Kit-level open decisions (inherited)

- **[RESOLVED -- feature 002] D-namespace disambiguation.** ADR defaults are RC1-RC16;
  the checker keeps D1-D8. No collision.
- **[RESOLVED -- ADR 0003] per-table artifact location.** This set lives in
  `mappings/sales_c086/`.
- **[NEEDS CLARIFICATION: deferred `retail validate` live surface]** The live checks
  (PK uniqueness, date coverage, 0 orphan FKs, cross-layer reconciliation) are
  implemented (`src/retail/validate.py`) but the per-table live run for `sales_c086`
  has NOT been performed (no silver/gold built). `reconciliation-report.md` is PENDING.

## See also

- Method: `docs/medallion-playbook.md` Phase 2 + Phase 4.
- Defaults: `docs/decisions/0002-retail-cleaning-defaults.md` (RC1-RC16).
- Sibling artifacts: `source-profile.md`, `source-map.yaml`, `assumptions.md`,
  `reconciliation-report.md` (this folder).
- Prior worked example (reference, NOT reused): `docs/worked-examples/c086-pharmacy.md`.
