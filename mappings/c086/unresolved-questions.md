# Unresolved questions -- `C086`

> **SUPERSEDED (2026-07-02).** Historical artifact of the FIRST build (0001/0002).
> The current approved map is [`mappings/sales_c086/`](../sales_c086/) (built by
> 0005/0006). See [`./README.md`](./README.md) for the audit notes on this
> folder's known inaccuracies.

> **Filled instance** (back-authored from the committed, live-validated warehouse).
> ASCII only. Links are `../../docs/...` (this file sits two levels deep under
> `mappings/c086/`).
>
> **What this file is for.** The open questions that block the build -- the decisions
> the agent cannot make alone. It is the committed form of the
> [medallion playbook](../../docs/medallion-playbook.md)'s Phase 2 analyst decision
> points and its Phase 4 review gate. No `silver.*` SQL is written until every blocking
> question is `answered` (the source-mapping gate --
> [architecture Sec 5](../../docs/architecture/tower-bi-agent-kit.md)).
>
> **Sibling artifacts (read as a set):** [`source-profile.md`](./source-profile.md),
> [`source-map.yaml`](./source-map.yaml), [`assumptions.md`](./assumptions.md),
> [`reconciliation-report.md`](./reconciliation-report.md).
>
> **Rule:** the agent recommends, the analyst decides. For C086 every judgment call was
> resolved before the build and confirmed by the live run -- the gate is CLEARED.

---

- **Table id:** `C086` (El Ezaby pharmacy sales)
- **Date raised:** `2026-06-24`
- **Raised by:** back-authored from committed 0001/0002 (live-validated)
- **Maps to playbook phases:** Phase 2 (decision points) + Phase 4 (review gate)
- **Gate status:** `CLEARED` -- 16/16 ADR 0002 defaults pass, validated live
  (2026-06-24). Zero open rows; all judgment calls resolved (closed log below).
- **AUDIT NOTE (2026-07-02):** this CLEARED rests on mechanical live validation,
  NOT on a named-human approval -- no resolution below records WHO decided, and no
  approvals[] entry exists for this map (the gate order was inverted: the map was
  back-authored from the SQL). Kept as history; the successor map
  (`mappings/sales_c086/`) carries a real recorded approval.

---

## Open questions (the build is blocked until these are `answered`)

**None.** There are zero open rows -- every blocking decision for C086 was resolved and
recorded before the silver build, and confirmed by the live reconciliation run. The
resolved decisions are kept below as a closed audit log (do not delete -- they show the
review trail), each flipped to `answered` with its resolution.

| ID | Question | Why it blocks | Who must answer | Proposed default (if unanswered) | Status | Resolution |
|----|----------|---------------|-----------------|----------------------------------|--------|------------|
| Q1 | What is the grain -- one row per invoice, or per invoice line item? | Grain fixes the non-droppable PK keys; all column decisions depend on it. | analyst | RC1: lowest grain the source provides | `answered` | Grain = one invoice line item; PK `(invoice_no, line_no)`. Verified live: 246,916 rows = 246,916 distinct, 0 NULL PK (2026-06-24). |
| Q2 | Are `insurance_no` / `insurance_phone` safe to carry to the BI layer? | A published dataset is effectively irreversible; PII cannot be un-published. | governance | RC4: drop the columns | `answered` | Both are patient-health PII -> DROPPED early, absent from the silver SELECT entirely (2026-06-24). |
| Q3 | Which column authoritatively marks a return? | `is_return` must come from the authoritative column, never the measure sign (RC8). | data-owner | RC8: derive from the authoritative type column | `answered` | Authoritative column = `billing_type_code` (Z-codes); `is_return = code IN ('Z4','Z5','Z6','Z8','Z10')`. Not the qty/amount sign. |
| Q4 | Is there a division->segment business rollup, and what is the full value map? | RC11 forbids inventing a rollup; it must be analyst-supplied. | analyst | RC11: no rollup unless supplied; `ELSE 'UNMAPPED'` | `answered` | Analyst-supplied enumerated `business_segment` map (PHARMA/HVI/NON-PHARMA), `ELSE 'UNMAPPED'`. Full table in `assumptions.md`. |
| Q5 | For columns with missing values, NULL or a grouping sentinel? | A sentinel is justified only for grouping dims and only if 0-collision (RC5/RC6). | analyst | RC5: `''`->NULL; RC6: NULL unless a grouping need is stated | `answered` | Sentinel `'UNKNOWN'` on salesperson_id/name, job_title, brand; `'UNCLASSIFIED'` on product_cluster; 0-collision verified. All other missings NULL; `original_invoice_ref` (a fact) left NULL. |
| Q6 | Is the product hierarchy a clean single-parent tree? | A non-tree forced into one parent destroys real overlap (RC12). | analyst | RC12: flat denormalized levels, not a snowflake | `answered` | Not a clean tree -- multi-parent overlaps exist -> kept flat in one `dim_product`; overlaps preserved. |

> Answered rows are kept (not deleted) so review sees the audit trail.
>
> **AUDIT NOTE (2026-07-02) on Q4:** the successor map contradicts this resolution --
> `mappings/sales_c086/` records NO analyst-supplied business_segment rollup (RC11:
> "none requested; none invented") and migration 0005 builds none. The rollup
> described here existed only in the superseded 0001/0002 build.

### Categories to prompt for (do not leave a category unconsidered)

Each recurring decision class was raised and resolved (cross-referenced above):

- **Grain ambiguity** (Phase 2.0; RC1/RC2) -- resolved Q1: one row = one invoice line
  item; PK `(invoice_no, line_no)` re-verified on the transformed data.
- **PII judgment calls** (Phase 2.2; RC4; governance) -- resolved Q2:
  `insurance_no`/`insurance_phone` dropped early as patient-health PII.
- **Business-rollup mappings** (Phase 2.7; RC11; analyst-supplied) -- resolved Q4:
  enumerated division->segment map; `ELSE 'UNMAPPED'`.
- **Sentinel-vs-null choices** (Phase 2.4; RC5/RC6) -- resolved Q5:
  `'UNKNOWN'`/`'UNCLASSIFIED'` on named grouping dims (0-collision); else NULL.
- **Returns identification** (Phase 2.6; RC8; data-owner) -- resolved Q3: from
  `billing_type_code` Z-codes, never the measure sign.
- **Hierarchy multi-parent handling** (Phase 2.8; RC12) -- resolved Q6: not a tree ->
  flat denormalized levels.

> **Namespace note (flagged, not resolved here).** The `RC<n>` ids above are ADR 0002
> cleaning/modeling defaults (RC1-RC16) in
> `../../docs/decisions/0002-retail-cleaning-defaults.md`. They are a different namespace
> from the `retail check` checker's TMDL/DAX rules (`D1-D8`). Distinct prefixes, no
> collision (disambiguated in feature 002).

---

## Kit-level open decisions (inherited)

Not per-table questions -- the architecture's own open decisions, restated so a reviewer
of this table's gate also sees what is unsettled kit-wide. Authoritative source:
[`../../docs/architecture/tower-bi-agent-kit.md` Sec 9](../../docs/architecture/tower-bi-agent-kit.md).

- **[RESOLVED -- feature 002] D-namespace disambiguation.** ADR 0002 cleaning defaults
  are now `RC1-RC16`; the `retail check` checker keeps its separate `D1-D8`. No collision.

- **[RESOLVED -- ADR 0003] per-table mapping artifact location.** The five mapping
  artifacts live in `mappings/<table>/` -- this folder (`mappings/c086/`) is the first
  filled instance.

- **[NEEDS CLARIFICATION: agent orchestration shape]** Which agent/skill drives the
  playbook conversationally (Layer D), and how it self-heals against `retail check`, is
  designed as a seam, not a runtime, in this slice.

- **[NEEDS CLARIFICATION: deferred `retail validate` live surface]** The live-validator
  categories were documented-only at first; they are now implemented (feature 004) and
  C086's live results are filled in [`reconciliation-report.md`](./reconciliation-report.md)
  from the read-only run of 2026-06-24.

---

## See also

- **Method:** [`../../docs/medallion-playbook.md`](../../docs/medallion-playbook.md) --
  Phase 2 (analyst decision points) and Phase 4 (review gate).
- **Defaults:** [`../../docs/decisions/0002-retail-cleaning-defaults.md`](../../docs/decisions/0002-retail-cleaning-defaults.md)
  -- the RC1-RC16 defaults.
- **Architecture:** [`../../docs/architecture/tower-bi-agent-kit.md`](../../docs/architecture/tower-bi-agent-kit.md)
  -- Sec 5 (source-mapping gate), Sec 9 (inherited open decisions).
- **Sibling templates:** [`source-profile.md`](./source-profile.md),
  [`source-map.yaml`](./source-map.yaml), [`assumptions.md`](./assumptions.md),
  [`reconciliation-report.md`](./reconciliation-report.md).
- **Worked example + compliance:** [`../../docs/worked-examples/c086-pharmacy.md`](../../docs/worked-examples/c086-pharmacy.md)
  + [`../../docs/c086-adr0002-compliance.md`](../../docs/c086-adr0002-compliance.md).
