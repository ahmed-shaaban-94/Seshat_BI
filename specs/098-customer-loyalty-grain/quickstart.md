# Quickstart: Customer / Loyalty Grain + Dimension Pattern

How an agent or developer exercises this feature once it is authored. This is
a walkthrough of the INTENDED usage, not an implementation guide -- it assumes
`docs/patterns/customer-dimension-pattern.md`,
`docs/patterns/customer-grain-pattern.md`, and `templates/customer-dimension.md`
already exist per plan.md / data-model.md. All names below (`<table>`,
`dim_customer`) are illustrative placeholders (Principle VII); none is
`retail_store_sales` or `customer_id`.

This feature adds NO `retail check` rule, so there is no "run the gate and see
a new Finding" step (unlike a rule-adding feature). The exercise here is
read -> copy -> fill-by-owner -> cite, followed by confirming nothing else in
the repo moved.

## 0. Preconditions

- The two new pattern docs and the one new template exist under
  `docs/patterns/` and `templates/` (this Plan stage's Phase 1 output).
- No table is REQUIRED to exist yet for the pattern docs to be readable in
  isolation (spec.md Independent Tests for User Story 1 and User Story 2) --
  an analyst can read them before onboarding any real customer-bearing table.

## 1. An analyst reads the dimension pattern before mapping a new table

```text
docs/patterns/customer-dimension-pattern.md
```

- Confirms a surrogate key (`customer_sk`), an explicit unresolved
  identity-key slot, an explicit unresolved PII-publish slot, an explicit
  unresolved SCD/historization-type slot, and the `-1` unknown-member row
  convention (RC14) -- all present, none of the four unresolved slots
  answered (User Story 1, Acceptance Scenarios 1-3).
- Confirms the identity-resolution section states the multi-id problem as a
  reserved owner ruling and links to `domains/customer.md`, proposing no
  merge rule (User Story 3).

## 2. The analyst reads the grain pattern to see candidate grains

```text
docs/patterns/customer-grain-pattern.md
```

- Confirms one candidate-grain entry exists for each of the four Planned
  customer KPIs named in `domains/customer.md` (Customer Retention Rate,
  Purchase Frequency, Customer Lifetime Value, New-vs-Returning split) --
  SC-002's "100% of four KPIs have a candidate-grain entry."
- Confirms every candidate grain states its FK join to `customer_sk`,
  COALESCE'd to `-1` -- the structural join fixed by Clarify Q2.
- Confirms the retention window, the CLV horizon/discounting choice, and the
  new-vs-returning anchor are each marked
  `[NEEDS CLARIFICATION: ... -- owner ruling]`, never a decided value
  (User Story 2, Acceptance Scenarios 1-3; SC-002's "0 of four have a decided
  period length, horizon, discount rate, or anchor value").

## 3. A future table's analyst copies the dimension template

```text
templates/customer-dimension.md  ->  (copied into that table's own mapping work)
```

- The analyst copies the template, exactly as the existing five mapping-gate
  templates are copied into `mappings/<table>/` (ADR 0003 pattern) -- this
  feature does not prescribe a new destination directory for the copy; that
  choice belongs to the table's own mapping work, consistent with how the
  existing source-mapping templates are handled.
- The template's four slots (identity-key, PII-publish, SCD/historization,
  plus the grain pattern's retention/CLV/anchor values) are STILL unresolved
  at this point. Copying the template does not answer anything.

## 4. The table's own owner rules the open slots (Principle V -- the agent does not do this)

For a REAL table (not this feature, which ships no filled instance):

- The identity-key slot is filled once a named owner confirms which raw
  field(s) uniquely identify a customer for THAT source.
- The PII-publish slot is filled once governance signs off on
  keep/drop/hash/mask for THAT source's customer identifier(s).
- The SCD/historization slot is filled once the table's owner picks Type 1
  (overwrite) or Type 2 (track history) for THAT source.
- The retention window / CLV horizon / new-vs-returning anchor are filled by
  the table's own owner, per `domains/customer.md`'s existing stop language.

The agent's role at this step is limited to surfacing that these slots exist
and are unfilled (as the pattern docs already do) -- it never fills a slot on
its own judgment, and this feature ships zero filled instances of any slot.

## 5. The filled decision is recorded in that table's OWN artifacts, not here

- A real table's answers land in ITS OWN
  `mappings/<table>/unresolved-questions.md` and
  `mappings/<table>/source-map.yaml` `gold_star.dimensions[]` entry -- citing
  `templates/customer-dimension.md` by name (FR-014) rather than
  re-describing the pattern's prose inline.
- Neither new pattern document nor the template is edited per table. They
  stay generic (Principle VII); only the table's own mapping artifacts record
  the table-specific answer.

## 6. Confirm the two shipped neighbours stayed byte-identical (SC-005)

```text
warehouse/migrations/0004_create_gold_retail_store_sales_star.sql
powerbi/RetailStoreSales.SemanticModel/definition/tables/gold dim_customer_rss.tmdl
skills/retail-kpi-knowledge/domains/customer.md
```

- None of the three files above is touched by this feature. A diff against
  the pre-feature tree on these three paths is empty.

## 7. Confirm no C086-specific answer leaked into the generic artifacts (SC-003, FR-011)

- Grep the two new pattern docs and the new template for `retail_store_sales`,
  `customer_id`, and "keep" / "drop" presented as a default PII answer:
  none should appear as a filled value. The worked example may be
  cited only in prose as "see `mappings/retail_store_sales/...` for one
  filled, source-specific answer" -- never as a default baked into a slot.

## 8. Confirm no numeric score was introduced (SC-004, hard rule #9)

- Grep the two new pattern docs and the new template for a percentage, a
  health/maturity/confidence number, or an "N of M" completeness count:
  none should appear. Readiness/applicability is expressed only as which
  slots are filled (generic, structural) vs. which remain an explicit owner
  ruling.

## 9. Confirm `retail check` is unaffected (SC-006)

```
retail check
```

- Exits 0 over the changed tree with the SAME registered-rule count as before
  this feature (no new rule id introduced -- FR-001, FR-015). This feature
  adds docs and a template only; there is nothing for the static checker to
  newly enforce.

## 10. Confirm no `contracts/` file was touched (SC-007, FR-009)

- `contracts/` (F009's metric-contract store) has zero files created or
  modified by this feature. No customer metric contract is seeded here; F009's
  own template + review process still applies whenever a real customer
  contract is eventually authored.

## 11. Confirm no live surface was touched (Principle VIII)

None of the steps above require a database connection, a Power BI Desktop
session, network access, or the deferred F016 execution adapter. Every
artifact this feature produces is static committed text, readable and
verifiable offline.
