# Feature Specification: Currency / Unit-of-Measure Contract

**Feature Branch**: `103-currency-unit-contract`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Gap #7. Currency / unit-of-measure contract -- declare
currency (e.g. EGP) and unit (kg vs each) on the mapping + a static check that a summed
measure's inputs share a unit. 12 kg + 3 each sums silently wrong today; no gate catches it."

## Overview

Today, `templates/source-map.yaml` records a source column's silver type, its missing-value
policy, and its PII flag, but nothing about what UNIT or CURRENCY the column's numeric values
are expressed in. `templates/metric-contract.yaml` records a metric's `binds_to.columns[]` --
the `gold` column(s) a summed measure reads -- but nothing states what unit that sum is
supposed to be in. If a fact table lands `quantity_kg` (kilograms) alongside
`quantity_each` (item count) and an analyst's metric contract sums both into one
`TotalQuantity` measure, or if two money columns are landed in different currencies (EGP vs
USD) and summed together, the result is a number that is arithmetically well-formed and
silently WRONG -- 12 kg + 3 each is 15 of nothing real. No stage of the readiness spine, and
no `retail check` rule, notices this today; a Stage 5 (Semantic Model Ready) `pass` can be
reached on a measure that adds incompatible units or currencies.

This feature closes that gap in two parts, mirroring the shape of the metric-contract /
source-map split (F009 defines, F010 checks): it adds a DECLARATION field --
`columns[].unit` and `columns[].currency` on `templates/source-map.yaml`, and `unit` on
`templates/metric-contract.yaml` -- so a human author records, at mapping time, what each
numeric column measures in and (separately) what it is a metric's own declared unit; and it
adds exactly ONE new static `retail check` rule (reserved id **HR11**) that, for a metric
contract whose `binds_to.columns[]` names two or more columns being summed, traces each bound
column back to its source-map `columns[].unit` and `columns[].currency` and fails closed when
the bound columns do not agree. The rule is wired into the Semantic Model Ready gate the same
way HR6 (RLS role-contract check) already demonstrates the pattern: it is a new INPUT to that
stage's existing verdict, not a new stage and not a replacement for any existing check.

## Boundary against neighbouring shipped work (read first)

This feature is a narrow DECLARATION-plus-SAME-UNIT-CHECK addition. It does not restate, and
must stay visibly distinct from, several already-shipped or already-scoped surfaces:

- **`templates/metric-contract.yaml` (F009, define-layer)** already declares a metric's
  `grain`, `formula_intent`, `owner`, and `binds_to.gold_table` / `binds_to.columns[]` /
  `binds_to.pii_sensitive`. This feature adds exactly one new top-level key, `unit`, to that
  template. It does NOT add a `currency` key to the metric contract (see Scope Guard --
  currency is validated across the bound columns themselves, not against a metric-level
  currency field) and it does NOT touch `grain`, `formula_intent`, `binds_to.pii_sensitive`,
  or the `ambiguities[]` ledger (spec 058).
- **`templates/source-map.yaml` (Phase 2.1-2.5 of the medallion playbook)** already records,
  per source column, `decision`, `reason`, `rename_to`, `silver_type`, `missing_policy`, and
  `pii`. This feature adds exactly two new per-column keys, `columns[].unit` and
  `columns[].currency`. It does NOT touch `decision`, `silver_type`, `missing_policy`, `pii`,
  `derived_columns`, or `gold_star` -- those remain the concern of the existing mapping
  phases.
- **`retail-semantic-check` / F010 (Semantic Model Readiness, on-disk feature 011)** already
  computes the Semantic Model Ready verdict from D1-D11/C1/R1/G6 `retail check` findings plus
  the measure-to-contract trace. This feature adds HR11 as ONE MORE input finding to that
  same verdict (mirroring how HR6, the RLS role-contract check, plugs into the identical
  gate) -- it does not replace, re-run, or duplicate F010's measure-to-contract check, and it
  does not compute or alter the verdict logic itself.
- **spec 068 additivity-consistency-rule** (a distinct, separately-scoped static rule) checks
  whether a metric's ADDITIVITY CLASSIFICATION (additive / semi-additive / non-additive, e.g.
  "can a ratio be summed across store") is legally composed when one metric derives from
  another. That is a question about WHETHER an aggregation across a dimension is
  mathematically legal for that metric's kind. This feature asks a completely different
  question: for a metric that IS being summed, are the raw inputs to that sum expressed in
  the SAME unit and the SAME currency in the first place. A metric can pass 068's
  additivity-legality check and still fail HR11 (a well-formed SUM of two genuinely
  additive-but-differently-united columns), and vice versa. Neither rule reads the other's
  classification or blocking_reasons.
- **`skills/bi-python-knowledge` cleaning guidance** (source-side cleaning/standardization
  knowledge, e.g. Phase 2.5 type discipline) already tells an author how to CLEAN and
  normalize a column's representation (e.g. strip a unit suffix from a text field, coerce to
  NUMERIC). This feature does not change that guidance and performs no cleaning itself; it
  only adds a place to DECLARE the resulting unit/currency and a static check that declared
  units/currencies AGREE across a sum's inputs. It never rewrites, converts, or re-derives a
  column's numeric value.
- **HR6 (RLS role-contract check, in-flight sibling feature, reserved id, not yet shipped)**
  is cited here only as the PATTERN this feature mirrors -- a small, single-purpose static
  `retail check` rule that plugs into the existing Semantic Model Ready verdict as one more
  input. This feature does not depend on HR6 landing first and does not share any file,
  template key, or rule logic with it.

## Scope Guard (non-negotiable)

- This feature MUST NOT convert a currency amount from one currency to another, and MUST NOT
  convert a quantity from one unit of measure to another (e.g. kg to lb, EGP to USD). Currency
  conversion RATES and unit-conversion FACTORS are an owner ruling (Principle V) entirely out
  of scope here.
- This feature MUST NOT recommend, suggest, look up, or hardcode any conversion rate or
  conversion factor, anywhere -- not in the template, not in the rule's own source, not in a
  finding message.
- This feature is DECLARATION (the two template additions) plus a SAME-UNIT / SAME-CURRENCY
  STATIC CHECK (HR11) only. It MUST NOT normalize, coerce, or silently re-express any
  column's value; a divergence is reported and the gate fails closed, never auto-fixed.
- Shared-schema key allocation (collision-avoidance; non-negotiable): this feature is the ONE
  source-map adder assigned `columns[].unit` and `columns[].currency`, and the ONE
  metric-contract adder assigned the top-level `unit` key. No other key name (`uom`,
  `unit_of_measure`, `measure_unit`, `binds_to.currency`, `metric.currency`, or similar) may
  be introduced by this feature for the same purpose.
- This feature MAY reserve rule id **HR11** in `src/retail/rules/`, and MUST do so only by
  adding a same-unit (and same-currency) static rule under that id -- it MUST NOT repurpose
  HR11 for any other check, and MUST NOT renumber, rename, or touch any other rule id.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A summed metric with clashing units fails closed (Priority: P1)

An analyst has mapped a source table where one column is landed in kilograms and another in
item counts (e.g. `weight_kg` and `unit_count`), each with its own declared
`columns[].unit`. A metric contract's author, without noticing the mismatch, defines
`TotalQuantity` with `binds_to.columns: [weight_kg, unit_count]` intending a simple sum.
Running `retail check` traces both bound columns back to the source-map, finds their declared
units disagree (`kg` vs `each`), and fails closed with an HR11 finding naming the metric and
the two clashing column/unit pairs. The Semantic Model Ready stage records HR11 in its
`blocking_reasons[]` and cannot reach `pass` while the finding stands.

**Why this priority**: This is the exact failure mode the gap describes (12 kg + 3 each
summing silently wrong) and the entire reason the feature exists. Without this, the feature
delivers nothing.

**Independent Test**: Author a source-map with two columns declaring different
`columns[].unit` values, author a metric contract whose `binds_to.columns[]` names both, run
`retail check`, and confirm an HR11 finding is emitted naming the metric and the two
clashing columns/units, and that the finding appears in the table's Semantic Model Ready
`blocking_reasons[]`.

**Acceptance Scenarios**:

1. **Given** a source-map with `weight_kg` declaring `unit: "kg"` and `unit_count` declaring
   `unit: "each"`, and a metric contract summing both, **When** `retail check` runs, **Then**
   it fails closed with an HR11 finding naming the metric, both column names, and both
   declared units.
2. **Given** an HR11 finding exists for a table's metric contracts, **When** the Semantic
   Model Ready status is read for that table, **Then** HR11 appears in
   `blocking_reasons[]` and the stage does not read `pass`.
3. **Given** the same clashing-unit metric, **When** the HR11 finding text is inspected,
   **Then** it names the mismatch only (unit strings and column names) and contains no
   conversion factor, no suggested rate, and no converted value.

---

### User Story 2 - A same-unit summed metric binds cleanly and clears HR11 (Priority: P1)

The metric contract's author fixes the definition so it only sums columns that share a
declared unit and currency (e.g. `TotalWeightKg` sums only `weight_kg` and
`secondary_weight_kg`, both declared `unit: "kg"`). Running `retail check` again shows no
HR11 finding for that metric; the Semantic Model Ready block that HR11 was raising is gone
(all other Stage 5 conditions being already met).

**Why this priority**: A gate that can only fail is not trustworthy -- an author must be able
to reach a clean, correct state by declaring and binding correctly. This is the other half of
the same slice as User Story 1 and is required for the feature to be usable, so it is also
P1.

**Independent Test**: Point a metric contract's `binds_to.columns[]` at two columns whose
source-map entries declare the same `unit` and the same `currency` (or both leave currency
inapplicable, e.g. a quantity metric), re-run `retail check`, and confirm no HR11 finding is
emitted for that metric.

**Acceptance Scenarios**:

1. **Given** a metric contract summing two columns that both declare `unit: "kg"`, **When**
   `retail check` runs, **Then** no HR11 finding is emitted for that metric.
2. **Given** a metric contract summing two money columns that both declare
   `currency: "EGP"`, **When** `retail check` runs, **Then** no HR11 finding is emitted for
   that metric on currency grounds.
3. **Given** all other Semantic Model Ready conditions already hold and HR11 now passes for
   every metric contract, **When** the Semantic Model Ready status is recomputed, **Then**
   HR11 does not appear in `blocking_reasons[]`.
4. **Given** a metric contract that passes HR11, **When** the contract is inspected, **Then**
   it carries no numeric confidence/health score and no completeness count -- HR11 emits only
   a pass/fail finding, per hard rule #9.

---

### User Story 3 - A currency mismatch across summed money columns is caught the same way (Priority: P2)

A metric contract sums two money columns whose source-map entries declare different
currencies (e.g. one column landed in EGP, another in USD, both mistakenly summed into one
`TotalRevenue` measure). HR11 catches this the same way it catches a unit mismatch -- it does
not require the columns to be quantities; a currency clash on summed money columns is the
same defect class.

**Why this priority**: Currency is named explicitly in the gap alongside unit ("declare
currency (e.g. EGP) and unit (kg vs each)"); a check that only ever looked at physical units
would silently miss half of the stated gap. This is P2 because the P1 slice (unit-only) is
already independently valuable and testable; currency is the second half of the same
mechanism, not a separate feature.

**Independent Test**: Author a source-map with two money columns declaring different
`columns[].currency` values, author a metric contract summing both, run `retail check`, and
confirm an HR11 finding is emitted naming the metric and the two clashing column/currency
pairs.

**Acceptance Scenarios**:

1. **Given** a source-map with `revenue_egp` declaring `currency: "EGP"` and `revenue_usd`
   declaring `currency: "USD"`, and a metric contract summing both, **When** `retail check`
   runs, **Then** it fails closed with an HR11 finding naming the metric, both column names,
   and both declared currencies.
2. **Given** the same clashing-currency metric, **When** the HR11 finding text is inspected,
   **Then** it contains no conversion rate, no suggested exchange rate, and no converted
   value (Scope Guard).
3. **Given** a metric contract sums columns that agree on unit but one declares a currency
   and the other declares none, **When** `retail check` runs, **Then** HR11 treats the
   declared-vs-undeclared currency pairing as a mismatch requiring the author to reconcile the
   declarations (an undeclared currency on one side of a money sum is not treated as
   "matches anything").

---

### Edge Cases

- What happens when a metric contract's `binds_to.columns[]` names only ONE column (no sum of
  multiple inputs, e.g. a simple pass-through measure)? HR11 has nothing to compare and MUST
  NOT fire -- the same-unit check applies only when two or more bound columns are being
  combined by the metric.
- What happens when a metric's `definition.aggregation` (the optional DAX-generator block) is
  present and is NOT `sum` (e.g. `count_rows`, `distinct_count`)? [OPEN -- deferred to
  implementation-planning per FR-013: whether HR11 scopes itself to metrics whose optional
  `definition.aggregation` is `sum` specifically, or to any metric whose `binds_to.columns[]`
  lists two or more columns regardless of `definition` presence. Neither reading is safe to
  default here -- scoping ONLY to `definition.aggregation: sum` would silently exempt every
  metric with no `definition` block (which the template documents as the common case: "a
  contract WITHOUT it behaves exactly as today"), reopening the exact gap HR11 exists to
  close; scoping to ANY 2+-column bind would false-positive on a legitimate ratio metric
  (e.g. a `[numerator_col, denominator_col]` pair that is not a sum at all), which User
  Story 2 rules out as untrustworthy. Since neither candidate is constitution-safe to adopt
  unilaterally and FR-013 already routes this to implementation planning, it stays OPEN --
  not invented here].
- What happens when one of the bound columns' source-map entry has NO `columns[].unit` (or no
  `columns[].currency`) declared at all -- an undeclared value, not a declared-and-differing
  one? [OPEN -- owner ruling required: whether an undeclared unit/currency on a bound column
  of a multi-column sum is itself an HR11 blocking finding (treating "undeclared" as a
  mandatory gap the gate must catch), or whether it is a softer warning-level finding, or
  whether it is silently skipped until a unit is explicitly declared -- this is a
  governance-policy call about how strictly the new declaration fields are enforced
  retroactively on existing mappings (Principle V/VI), and the agent MUST NOT default it to
  whichever reading is most/least strict on its own authority.
  NOTE -- internal-consistency flag surfaced during Clarification: User Story 3's Acceptance
  Scenario 3 (a currency-declared-vs-currency-undeclared pairing "is not treated as matches
  anything") pre-supposes the STRICT ("undeclared is a mismatch") answer to this exact open
  question, while FR-006 only fires HR11 on two or more "different, non-null" currency
  values -- a null-vs-non-null pairing is outside FR-006's literal fail condition as
  written. This spec does NOT resolve that inconsistency by picking a side; US3 Acceptance
  Scenario 3 is recorded as one CANDIDATE answer for the owner to ratify or reject when this
  OPEN item is decided, not as a settled requirement. Until ruled, FR-006 (as literally
  written) governs and US3 Acceptance Scenario 3 is NOT guaranteed by the requirements as
  they stand].
- What happens when the two bound columns' units are textually different strings that a human
  would recognize as equivalent (e.g. `"kg"` vs `"Kg"` vs `"kilogram"`)? HR11 performs an
  exact, case-sensitive string-equality check on the declared values as committed; it MUST
  NOT apply any unit-name normalization, alias table, or fuzzy matching -- normalizing unit
  vocabulary is a separate, explicitly out-of-scope concern (Scope Guard: no conversion logic
  of any kind, and no synonym table that could silently paper over a real mismatch).
- What happens when the referenced source-map for the table does not exist, is unreadable, or
  the named bound column is not found among its `columns[]` entries? HR11 records this as a
  blocking finding naming the missing/unreadable path or the unresolved column name -- it
  MUST NOT assume a matching unit/currency when the source of truth cannot be read (mirrors
  HR6's "unresolvable column" treatment).
- What happens to a metric contract authored BEFORE this feature shipped, whose bound
  columns' source-map entries have never had `columns[].unit` / `columns[].currency` filled
  in? This is the same question as the undeclared-value edge case above; see that
  [OPEN -- owner ruling required] entry -- no retroactive-enforcement policy is assumed here.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `templates/source-map.yaml` MUST gain two new OPTIONAL per-column keys inside
  each `columns[]` entry: `unit` (the unit of measure the column's numeric value is expressed
  in, e.g. `"kg"`, `"each"`, free-text) and `currency` (the ISO-style currency code the
  column's monetary value is expressed in, e.g. `"EGP"`, free-text), each defaulting to an
  explicit "not applicable / not yet declared" value (e.g. `null`) rather than being silently
  absent, so a reviewer can distinguish "declared as N/A" from "field never filled in."
- **FR-002**: `templates/metric-contract.yaml` MUST gain exactly one new OPTIONAL top-level
  key, `unit` (the unit of measure the metric's own resulting value is expressed in), sibling
  to `grain` and `binds_to`. The metric contract MUST NOT gain a `currency` key (Scope Guard
  -- currency agreement is validated across the bound columns' own `columns[].currency`
  declarations, not against a metric-level currency field).
- **FR-003**: The feature MUST add exactly one new static `retail check` rule, registered
  under the reserved id **HR11**, that runs over every committed metric contract
  (`mappings/<table>/metrics/*.yaml`) whose `binds_to.columns[]` lists two or more columns.
- **FR-004**: For each such multi-column metric contract, HR11 MUST resolve every named
  bound column to its entry in the table's committed `source-map.yaml` `columns[]` list and
  read that entry's declared `unit` and `currency`.
- **FR-005**: HR11 MUST fail (record a finding) when two or more of a metric's resolved bound
  columns declare a different, non-null `unit` value, naming the metric, the clashing column
  names, and their declared unit values verbatim.
- **FR-006**: HR11 MUST fail (record a finding) when two or more of a metric's resolved bound
  columns declare a different, non-null `currency` value, naming the metric, the clashing
  column names, and their declared currency values verbatim. This check is independent of
  FR-005 (a metric may clash on unit, on currency, on both, or on neither).
- **FR-007**: HR11 MUST perform an exact, case-sensitive string comparison of declared
  `unit` / `currency` values. It MUST NOT normalize, alias, or fuzzy-match unit or currency
  vocabulary (e.g. `"kg"` vs `"Kg"` vs `"kilogram"` are treated as distinct values whose
  mismatch is reported, not reconciled).
- **FR-008**: HR11 MUST NOT convert, normalize, rescale, or re-express any value in any
  unit or currency, MUST NOT compute or embed a conversion rate or conversion factor, and
  MUST NOT emit a converted value or a suggested rate in any finding message (Scope Guard;
  Principle V rate ruling stays with a human owner).
- **FR-009**: HR11 MUST NOT execute any DAX or SQL, MUST NOT open any database or network
  connection, and MUST NOT read a live Power BI/PBIP surface -- it reads only already-
  committed `source-map.yaml` and metric-contract text (Principle VIII, static-first).
- **FR-010**: When a metric contract's `binds_to.columns[]` names a column that cannot be
  resolved in the table's committed `source-map.yaml` `columns[]` list, or when the table's
  `source-map.yaml` itself is missing or unreadable, HR11 MUST record a blocking finding
  naming the unresolved column or the missing/unreadable path -- it MUST NOT assume a
  matching unit/currency when the source of truth cannot be read.
- **FR-011**: HR11 MUST NOT fire on a metric contract whose `binds_to.columns[]` lists fewer
  than two columns (nothing to compare).
- **FR-012**: When HR11 produces one or more findings for a table's committed metric
  contracts, the Semantic Model Ready readiness computation (`retail-semantic-check`) MUST
  surface HR11's finding(s) in that table's `blocking_reasons[]`, the same way an existing
  D1-D11/G6/HR-family finding already blocks that stage -- this feature adds an input to the
  existing verdict; it does not replace or duplicate F010's measure-to-contract check.
- **FR-013**: The feature MUST NOT decide, and MUST record as an explicit open question
  (never invent an answer for), how HR11 detects that a metric contract represents a "sum of
  its bound columns" when the optional `definition.aggregation` block is absent -- see Edge
  Cases [OPEN -- deferred to implementation-planning]. This detection-scope decision is left
  to implementation planning, not resolved here.
- **FR-014**: The feature MUST NOT decide, and MUST record as an explicit open question
  (never invent an answer for), whether an UNDECLARED (null/absent) `unit` or `currency` on
  one side of a multi-column bind is itself a blocking condition, a warning, or a silent
  no-op -- see Edge Cases [OPEN -- owner ruling required]. This is a governance-policy call about
  retroactive enforcement strictness (Principle V/VI), not an implementation detail the agent
  may default on its own authority.
- **FR-015**: The `unit` / `currency` template fields and the HR11 rule MUST NOT emit or
  require any numeric confidence/health/maturity score or a completeness count ("N of M");
  readiness stays expressed only via the four explicit statuses plus `evidence[]` and
  `blocking_reasons[]` (hard rule #9).
- **FR-016**: The template additions and the HR11 rule MUST stay generic (Principle VII): no
  C086 / retail_store_sales-specific unit label, currency code, or column name may be
  inlined into `templates/source-map.yaml`, `templates/metric-contract.yaml`, or the HR11
  rule's own source as a hardcoded default; C086 or retail_store_sales may appear only as a
  cited filled instance elsewhere (e.g. a worked example under `docs/worked-examples/`).
- **FR-017**: All authored artifacts MUST be ASCII, UTF-8 without BOM (`--` and `->`, no
  glyphs), and MUST use short repo-relative paths respecting the Windows 260-char PBIP path
  budget (Principle IX).
- **FR-018**: `docs/readiness/semantic-model-ready.md` MUST be updated to list HR11 alongside
  the existing D1-D11/C1/R1/G6 (and any already-listed HR-family) gate checks in its
  "Required checks" and "Blocking reasons" tables, so the gate documentation and the running
  rule stay in sync (mirrors how G6 and HR6 are already, or would be, documented there).
- **FR-019**: The feature MUST NOT introduce any live-database-backed check; a live
  verification that a materialized column's actual values are consistent with its declared
  unit/currency (e.g. sampling real data) is explicitly OUT OF SCOPE and deferred to a future
  `retail validate` extension, not this feature (Principle VIII, static-first / live
  deferred).
- **FR-020**: The feature MUST NOT define, recommend, or auto-fill WHAT unit or currency any
  column should be declared as -- the analyst who fills the source-map decides the declared
  value from the profiled source data; the agent's role is limited to recording the
  human-supplied declaration and running the static comparison (Principle V).

### Key Entities

- **Unit declaration**: the `columns[].unit` field on a source-map column entry, recording
  the unit of measure that column's numeric value is expressed in (human-authored,
  free-text, optional, defaults to an explicit not-yet-declared value).
- **Currency declaration**: the `columns[].currency` field on a source-map column entry,
  recording the currency code that column's monetary value is expressed in (human-authored,
  free-text, optional, defaults to an explicit not-yet-declared value).
- **Metric unit**: the `unit` top-level field on a metric contract, recording the unit of
  measure the metric's own resulting value is expressed in (human-authored, optional; no
  metric-level currency counterpart by design -- see Scope Guard).
- **HR11 finding**: a static `retail check` finding raised when a metric contract's two or
  more bound columns resolve to declared units, or declared currencies, that disagree (or
  when a bound column cannot be resolved against the committed source-map).
- **Semantic Model Ready blocking reason (HR11-sourced)**: an entry in a table's
  `readiness-status.yaml` `semantic_model_ready.blocking_reasons[]` that traces back to a
  live HR11 finding; cleared only when the underlying declarations or bindings are corrected
  and HR11 re-runs clean.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of metric contracts whose `binds_to.columns[]` names two or more columns
  with disagreeing declared `unit` values are caught by `retail check` with an HR11 finding
  before Semantic Model Ready can read `pass` for that table.
- **SC-002**: 100% of metric contracts whose `binds_to.columns[]` names two or more columns
  with disagreeing declared `currency` values are caught by `retail check` with an HR11
  finding before Semantic Model Ready can read `pass` for that table.
- **SC-003**: 0 HR11 findings, template fields, or rule source lines contain a conversion
  rate, a conversion factor, or a converted value (Scope Guard verifiable by static grep).
- **SC-004**: A metric contract whose bound columns all agree on declared unit and currency
  produces 0 HR11 findings (no false positives on a correctly-declared, correctly-bound
  metric).
- **SC-005**: 0 generated artifacts (template fields, HR11 finding text) contain a numeric
  confidence/health/maturity score or a completeness count.
- **SC-006**: 0 generic template files (`templates/source-map.yaml`,
  `templates/metric-contract.yaml`) contain a worked-example (C086/retail_store_sales)
  domain-specific unit label, currency code, or column name.

## Assumptions

- `templates/source-map.yaml` and `templates/metric-contract.yaml` remain the authoritative
  templates for their respective artifacts; this feature extends both with additive,
  optional fields rather than replacing or restructuring either file.
- `src/retail/rules/` is the existing static-rule runner (each rule self-registers, e.g.
  `g6.py` registers `G6`); HR11 is added as one new rule module in that same pattern, and the
  id HR11 is not claimed by any other in-flight feature (per the collision-avoidance
  allocation this spec was given).
- `retail-semantic-check` / F010 is the existing Semantic Model Ready verdict computation;
  this feature adds HR11 as one more input finding to that computation without altering its
  existing measure-to-contract trace logic.
- The metric-contract's own top-level `unit` field (FR-002) is DOCUMENTARY only in this
  feature: HR11's comparison (FR-005/FR-006) is column-to-column agreement among a metric's
  `binds_to.columns[]` only. No FR requires HR11 to cross-check a metric's declared `unit`
  against its bound columns' declared units, and this spec does not add one -- doing so would
  be a second, un-scoped comparison the gap description and Scope Guard do not ask for.
  Default adopted (Principle VI): narrows scope rather than widens it.
- HR11 resolves a metric contract's `binds_to.columns[]` entries (gold-facing names) against
  the table's `source-map.yaml` `columns[]` list by matching on the silver name
  (`columns[].rename_to`), since `binds_to.columns[]` documents gold column names and
  `source-map.yaml` is keyed by source name with a `rename_to` silver alias, not by a gold
  name; a `derived_columns` entry (which carries no `unit`/`currency` field at all) is
  therefore never a resolvable match and falls under FR-010's "cannot be resolved" blocking
  path rather than being silently treated as unit/currency-agnostic. Default adopted
  (Principle VI): the most literal join key already present in both committed artifacts,
  fails closed (via FR-010) rather than guessing when a bound name is a derived column.
- The detection rule for "which metric contracts are a same-unit-relevant sum" (FR-013) and
  the enforcement posture for undeclared unit/currency values (FR-014) are both left as
  explicit open questions for implementation planning / a named human ruling; this spec does
  not assume either answer.
- No currency-conversion-rate table, exchange-rate service, or unit-conversion-factor table
  is introduced, referenced, or planned by this feature at any point (Scope Guard).
- The dashboard/visual layer, the DAX Generator's optional `definition` block semantics
  beyond what FR-013 already flags as open, and any live-data sampling of actual column
  values are OUT OF SCOPE for this feature.

## Clarifications

### Session 2026-07-04

- **Q1 (Edge Cases / FR-013)**: How does HR11 detect that a metric contract is a
  "same-unit-relevant sum" when the optional `definition.aggregation` block is absent (most
  contracts, per the template's own note that "a contract WITHOUT it behaves exactly as
  today")? -> **OPEN, deferred to implementation-planning per FR-013's own routing** (not a
  Principle-V human-values ruling; a design-detection-scope decision). Not defaulted here
  because neither candidate reading is constitution-safe to adopt unilaterally: scoping ONLY
  to `definition.aggregation: sum` would silently exempt the common no-`definition` case,
  reopening the exact silent-wrong-sum gap the feature exists to close (contradicts the
  Overview and SC-001/SC-002); scoping to ANY metric with 2+ `binds_to.columns[]` would fire
  on a legitimate ratio metric (numerator/denominator pair), producing a false positive that
  User Story 2 rules out ("a gate that can only fail is not trustworthy"). Touches: FR-013,
  Edge Cases (definition.aggregation edge case).
- **Q2 (Edge Cases / FR-014)**: Is an UNDECLARED (null/absent) `unit` or `currency` on one
  side of a multi-column bind itself a blocking finding, a warning, or a silent no-op? ->
  **OPEN owner ruling required** (Principle V/VI governance-policy call on retroactive
  enforcement strictness against existing mappings that predate this feature; the spec
  explicitly forbids the agent from defaulting this on its own authority). Touches: FR-014,
  Edge Cases (undeclared-unit edge case, pre-existing-contract edge case).
- **Q2a (internal-consistency flag, surfaced while triaging Q2)**: User Story 3 Acceptance
  Scenario 3 states that a declared-vs-undeclared currency pairing "is not treated as
  matches anything" -- i.e. it pre-supposes the STRICT answer to Q2. But FR-006 as literally
  written only fires HR11 on two-or-more bound columns with a "different, **non-null**"
  currency value, which does not cover a null-vs-non-null pairing. This spec does NOT
  resolve the inconsistency by picking a side while Q2 is open: US3 Acceptance Scenario 3 is
  recorded as one CANDIDATE answer for the Q2 owner to ratify (or reject) when Q2 is ruled,
  not as an already-settled requirement independent of Q2. Until Q2 is ruled, FR-006's
  literal non-null-vs-non-null comparison governs, and US3 Acceptance Scenario 3 is not
  guaranteed by the requirements as currently written. Touches: FR-006, FR-014, User Story 3
  Acceptance Scenario 3.
- **Q3 (metric-level `unit` field scope, FR-002)**: Does HR11 cross-check a metric
  contract's own top-level `unit` (FR-002) against its bound columns' declared units, or is
  that field documentary only? -> **Default adopted**: documentary only -- HR11's comparison
  is column-to-column agreement among `binds_to.columns[]` (FR-005/FR-006); no FR asks for a
  metric-vs-bound-column unit cross-check, and adding one would be an un-scoped second
  comparison beyond what the gap description and Scope Guard request (Principle VI: narrow,
  do not widen, an unstated requirement). Touches: FR-002, FR-005, FR-006.
- **Q4 (bound-column resolution key)**: `binds_to.columns[]` on a metric contract names
  gold-facing column names; `source-map.yaml`'s `columns[]` list is keyed by
  `source_name` with a `rename_to` silver alias, and carries no gold name. How does HR11
  join one to the other? -> **Default adopted**: match on the silver name
  (`columns[].rename_to`), the only literal join key already present in both committed
  artifacts; a `binds_to.columns[]` entry that names a `derived_columns` entry (which has no
  `unit`/`currency` field) is therefore never resolvable and falls under FR-010's
  cannot-be-resolved blocking path rather than being silently skipped or treated as
  unit/currency-agnostic (Principle VI: adopt the existing literal key; fail closed per
  FR-010 rather than guess). Touches: FR-004, FR-010.
