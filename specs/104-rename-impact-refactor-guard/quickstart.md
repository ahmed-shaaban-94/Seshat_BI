# Quickstart: Exercising HR9 (Rename/Impact Refactor-Safety Guard)

**Feature**: `104-rename-impact-refactor-guard` | **Date**: 2026-07-04

This describes how an agent or developer exercises HR9 ONCE IT IS BUILT (the
tasks/implementation stage, not this planning stage). Nothing here has been
executed; there is no code yet. This is the expected-usage walkthrough the
tasks stage should make true.

## 1. Run the gate the normal way

HR9 needs no special invocation -- it is one more registered rule inside the
existing gate:

```bash
retail check
```

or, for structured output (existing B2 capability):

```bash
retail check --format json
```

A clean tree (every `binds_to.columns` entry, every DAX cross-reference, and
every binding-map bracket token resolves against the current committed TMDL)
produces zero `"rule_id": "HR9"` findings and does not affect the exit code.

## 2. Reproduce User Story 1 -- an orphaned contract column reference

1. Open a table's committed TMDL file under
   `powerbi/<Model>.SemanticModel/definition/tables/`.
2. Rename a column, e.g. change `column total_spent` to
   `column total_amount` (leave everything else untouched -- do not update any
   measure, contract, or binding map).
3. Run `retail check`.
4. **Expected**: one HR9 finding (`Severity.ERROR`) naming the metric
   contract file (e.g. `mappings/<table>/metrics/TotalSales.yaml`), the stale
   column name (`total_spent`), and the TMDL table it no longer resolves
   against. `retail check` exits non-zero.
5. Revert the TMDL rename (or instead update the contract's
   `binds_to.columns` to `total_amount`). Run `retail check` again.
6. **Expected**: zero HR9 findings for that reference (Acceptance Scenario 2).

## 3. Reproduce User Story 2 -- an orphaned measure reference (DAX + binding map)

1. In the same TMDL table, rename a measure, e.g. `measure TotalSales` to
   `measure TotalRevenue`, leaving a second measure's DAX body still saying
   `DIVIDE([TotalSales], ...)`, and leaving the binding map's
   `semantic_model_field(s)` column still citing `` `[TotalSales]` `` on one
   or more visual rows.
2. Run `retail check`.
3. **Expected**: TWO HR9 findings --
   - one naming the referencing measure (e.g. `AvgTransactionValue`), the
     TMDL file, and the stale `[TotalSales]` token (a `dax-cross-ref` orphan);
   - one naming the binding-map file, the affected `visual_id` row, and the
     same stale `[TotalSales]` token (a `binding-map` orphan).
4. Update BOTH the DAX expression and the binding-map cell to
   `` [TotalRevenue] ``. Run `retail check` again.
5. **Expected**: zero HR9 findings for either reference (Acceptance Scenario 3).

## 4. Reproduce User Story 3 -- a table with no model surface is a clean no-op

1. Onboard (or point at) a table that has a filled `source-map.yaml` and
   metric-contract drafts under `mappings/<table>/metrics/`, but has NO
   committed TMDL file yet under `powerbi/*.SemanticModel/definition/tables/`.
2. Run `retail check`.
3. **Expected**: zero HR9 findings for that table (FR-007; no premature
   engagement, mirroring the HR1 zero/one-star no-op precedent).
4. Once that table's TMDL model surface is committed, run `retail check`
   again.
5. **Expected**: HR9 now checks that table's contract/DAX/binding-map
   references against the newly-existing truth set.

## 5. Exercise the edge cases the spec calls out

- **Case-insensitive resolution (Q-CASE-SENSITIVITY)**: write a DAX reference
  as `[totalsales]` where the committed measure is named `TotalSales`. Run
  `retail check`. **Expected**: NOT flagged (resolves case-insensitively,
  mirroring the Power BI engine's own resolution).
- **Table-qualified vs. unqualified scoping (FR-006)**: two different tables
  each have a column with the same name (e.g. both a fact and a dimension
  have a `notes` column). A table-qualified reference
  `'gold dim_x'[notes]` must resolve ONLY against `dim_x`'s own columns, never
  against the fact table's `notes` column even though the name matches.
  **Expected**: no false match across tables.
- **Binding-map prose/qualifiers (Q-BINDING-CELL-PARSE)**: a cell reads
  `` `[TotalSales]` by `dim_date_rss[full_date]` (month) ``. **Expected**: HR9
  extracts exactly two tokens (`[TotalSales]` and `dim_date_rss[full_date]`)
  and ignores "by" and "(month)" -- no fuzzy match attempted on either.
- **Reverse direction not checked**: a TMDL measure exists but no metric
  contract references it yet. **Expected**: HR9 emits nothing for this case
  (it is Semantic Model Ready's own existing "measure with no contract"
  blocking reason, not HR9's).
- **Cross-model isolation**: two different tables' `*.SemanticModel/` folders
  each define a measure with the same name. **Expected**: each reference is
  resolved only against the model folder its OWN referencing artifact
  belongs to, never against a different table's model.

## 6. What "done" looks like for this rule (read-only verification)

- `retail check` still reports the SAME live rule count plus one (HR9) --
  never a hand-typed number (verify against `docs/rules/rules-manifest.json`
  and `tests/unit/test_rules_wiring.py`'s `EXPECTED_RULE_IDS`, per FR-015).
- `docs/readiness/semantic-model-ready.md` and `docs/readiness/dashboard-ready.md`
  "Blocking reasons" tables each list HR9 (FR-014, SC-007).
- Zero HR9 findings on the current committed tree TODAY (before any planted
  rename) -- this is the expected green baseline HR9 ships against, the same
  way SC1/DF1/SF1/AL2 each shipped with a zero-findings baseline on `main`.
- HR9's own rule source contains no `retail_store_sales` / C086 / pharmacy
  specific literal (SC-004) -- grep the new module for those names as a
  sanity check; it should find none.
- No file is written, renamed, or modified by an HR9 run -- `git status`
  before and after `retail check` is byte-identical (SC-006).

## 7. What this quickstart does NOT cover (deliberately out of scope)

- It does not exercise F016 (the Power BI execution adapter) -- HR9 has no
  live/execution path to demonstrate.
- It does not exercise HR1 (conformed-dimension readiness) -- a separate,
  independent rule on a different surface.
- It does not demonstrate an auto-fix -- HR9 never offers one; a human edits
  the correct file and re-runs `retail check` to confirm the finding cleared.
- It does not resolve Q-APPROVAL-SEAM -- whether a clean HR9 run needs its own
  new named-human approval seam is an OPEN Principle-V question for an owner,
  not something this quickstart (or any workflow) may decide.
