# Quickstart: Currency / Unit-of-Measure Contract

**Feature**: 103-currency-unit-contract | **Phase**: 1

This walks through how an agent or a human developer exercises HR11 and the
two template additions once this feature is BUILT (post-`tasks.md`/
implementation). Nothing here executes early; it describes the intended
usage of the shipped artifacts.

## Prerequisites

- The table's `source-map.yaml` exists and is committed (Mapping Ready has
  at least been started -- HR11 reads whatever `columns[]` entries are
  currently committed, whether or not `unit`/`currency` are filled in).
- At least one metric contract exists under `mappings/<table>/metrics/`
  whose `binds_to.columns[]` names two or more gold-facing column names.

## Step 1 -- An analyst declares unit/currency at mapping time

In the table's `mappings/<table>/source-map.yaml`, each `columns[]` entry
gains two new OPTIONAL fields:

```yaml
columns:
  - source_name: "<SRC_WEIGHT>"
    decision: "keep"
    reason: "quantity measure in kilograms"
    rename_to: "weight_kg"
    silver_type: "numeric(12,3)"
    missing_policy: "null"
    pii: false
    gold_placement: "fact_measure"
    unit: "kg"                      # NEW -- declared from the profiled data
    currency: null                  # not a monetary column

  - source_name: "<SRC_COUNT>"
    decision: "keep"
    reason: "item count"
    rename_to: "unit_count"
    silver_type: "numeric(12,0)"
    missing_policy: "null"
    pii: false
    gold_placement: "fact_measure"
    unit: "each"                    # NEW -- a DIFFERENT declared unit
    currency: null
```

The agent MUST NOT choose `unit`/`currency` on the analyst's behalf
(Principle V, FR-020) -- if asked to "just fill in the units," the agent
raises this as a question for the analyst rather than inventing a value
from the column name or a guess.

## Step 2 -- A metric owner defines a contract that (accidentally) sums both

```yaml
name: "TotalQuantity"
grain: "sum across all kept fact rows"
unit: null                          # not yet declared -- documentary only
formula_intent: "Total physical quantity moved, across weight and count columns."
owner: "<named metric owner>"
binds_to:
  gold_table: "gold.fct_<table>"
  columns:
    - "weight_kg"
    - "unit_count"
  pii_sensitive: false
```

## Step 3 -- Run the static check

```powershell
retail check
```

or, scoped to see only HR11 output, filter the JSON:

```powershell
retail check --format json | ConvertFrom-Json | Where-Object { $_.rule_id -eq "HR11" }
```

### Failure case (User Story 1 -- clashing unit)

```text
[ERROR] HR11  mappings/<table>/metrics/TotalQuantity.yaml
  metric 'TotalQuantity' sums columns with clashing units: 'weight_kg' (kg)
  vs 'unit_count' (each) -- resolve the declared units or the binding; HR11
  never converts or normalizes a unit
```

### Failure case (User Story 3 -- clashing currency)

```text
[ERROR] HR11  mappings/<table>/metrics/TotalRevenue.yaml
  metric 'TotalRevenue' sums columns with clashing currencies: 'revenue_egp'
  (EGP) vs 'revenue_usd' (USD) -- resolve the declared currencies or the
  binding; HR11 never converts or suggests an exchange rate
```

### Unresolvable-column case (Edge Case, FR-010)

```text
[ERROR] HR11  mappings/<table>/metrics/TotalQuantity.yaml
  metric 'TotalQuantity' binds to 'unit_count', which does not resolve to
  any columns[].rename_to in mappings/<table>/source-map.yaml -- HR11 never
  assumes a matching unit/currency when the source of truth cannot be read
```

## Step 4 -- The metric owner (or analyst) fixes and re-runs

The owner either narrows the metric to sum only same-unit columns, or the
analyst corrects a mis-declared unit, so both bound columns agree:

```yaml
name: "TotalWeightKg"
binds_to:
  gold_table: "gold.fct_<table>"
  columns:
    - "weight_kg"
    - "secondary_weight_kg"          # both declare unit: "kg" in source-map.yaml
  pii_sensitive: false
```

Re-run `retail check` (User Story 2): no HR11 finding is emitted for this
metric.

```powershell
retail check
```

## Step 5 -- Reading the Semantic Model Ready verdict

Run the existing, unchanged Stage-5 checker skill:

```text
retail-semantic-check
```

It runs `retail check` (now including HR11) exactly as before -- no code in
`retail-semantic-check` itself changes for this feature (`plan.md`, Project
Structure). Any HR11 `Severity.ERROR` finding surfaces in the table's
`mappings/<table>/readiness-status.yaml` under
`stages.semantic_model_ready.blocking_reasons[]`, prefixed `HR11:`,
alongside any existing D1-D11/C1/R1/G6 blocking reason.

## Step 6 -- Regenerate the rule manifest (implementation-time, not authoring-time)

After HR11 is registered in code (a `tasks.md`/implementation step, not this
plan), the authoritative rule inventory must be regenerated so the registry
snapshot test does not fail:

```powershell
retail manifest
```

This produces the updated `docs/rules/rules-manifest.json` listing HR11
alongside every other registered rule id.

## Step 7 -- Confirm the template additions landed (verification, not "zero diff")

Unlike a feature that adds a wholly new template file, this feature EDITS
two existing templates. The useful post-implementation check is that both
diffs are small, additive, and free of any conversion logic -- not that
either diff is empty:

```powershell
git diff --stat templates/source-map.yaml templates/metric-contract.yaml
git diff templates/source-map.yaml templates/metric-contract.yaml | Select-String -Pattern "rate|factor|convert" -CaseSensitive:$false
```

The first command should show a small, non-zero, additive diff on both
files. The second should return NOTHING -- any hit would indicate a
conversion concept leaked into a generic template (Scope Guard, SC-003).
Separately, confirm `templates/metric-contract.yaml` gained no `currency`
key:

```powershell
git diff templates/metric-contract.yaml | Select-String -Pattern "^\+.*currency" -CaseSensitive:$false
```

This should also return nothing -- an empty result confirms the
collision-avoidance allocation held (only `unit` was added).

## What this feature does NOT let you do (guardrails to demonstrate)

- **No auto-fill.** Asking the agent to "just guess the unit from the
  column name" is refused; the agent raises an unresolved question instead
  (Principle V, FR-020).
- **No conversion, ever.** There is no `retail check --convert` or
  equivalent; HR11 never computes, embeds, or suggests a conversion rate or
  factor, and never emits a converted value in a finding message (Scope
  Guard, FR-008, SC-003).
- **No fuzzy unit matching.** `"kg"` vs `"Kg"` vs `"kilogram"` are treated
  as distinct, mismatching values -- HR11 does not maintain or consult a
  synonym table (FR-007).
- **No score.** `retail check`'s HR11 output never prints a confidence/
  health number -- only the finding message + locator (hard rule #9,
  FR-015).
- **No settled answer to FR-013 or FR-014.** This feature does not ship a
  behavior that silently assumes "only `definition.aggregation: sum`
  counts" or "any 2+-column bind counts" (FR-013), nor one that silently
  assumes "undeclared always blocks" or "undeclared never blocks" (FR-014).
  Both remain open for implementation planning / an owner ruling; exercising
  HR11 today only demonstrates the DECLARED-non-null-vs-DECLARED-non-null
  comparison (FR-005/FR-006 literal), never the undeclared-value edge.
- **No metric-contract.yaml `currency` key.**
  `git diff templates/metric-contract.yaml` never shows a line adding
  `currency:` at any level (SC-006 by extension of the Scope Guard) -- a
  useful one-line check an agent can run after implementation (Step 7).
