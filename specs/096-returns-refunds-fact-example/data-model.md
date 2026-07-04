# Phase 1 Data Model: Returns/Refunds Fact Worked Example

**Feature**: `specs/096-returns-refunds-fact-example/` | **Date**: 2026-07-04

**What this is.** The key entities and artifact SHAPES (generic YAML/Markdown
structures) this feature introduces. Per Principle VII (C086-is-an-example-not-the-
schema) and FR-014, every shape below is a GENERIC skeleton -- no filled client
content, no invented business policy. Concrete values (table name, exact columns,
exact figures) are Mapping-Ready/Stage-2 authoring decisions made at BUILD time, not
fixed by this plan.

---

## 1. Returns/refunds fact (the example's subject)

A NEW fact table, distinct from `retail_store_sales`'s sales fact. Its grain,
natural key, and source system are a Stage-2 (Mapping Ready) judgment made during
the example's own build (spec.md Key Entities), not invented here. The shape every
instance of this entity MUST carry:

| Attribute | Generic shape | Governing rule |
|---|---|---|
| grain | one row = one transaction line (sale OR return) | decided first, per RC1, at build time |
| signed quantity and/or amount | a numeric column whose sign distinguishes a return from a sale on at least one committed row | FR-003 |
| `is_return` classification | boolean/flag, DERIVED from an authoritative transaction-type/reason column | RC8; FR-004 -- never derived from measure sign alone |
| transaction date | the fact's own date (see "Cross-period return" below for the axis question) | FR-007/FR-013 |
| original-sale reference (for return rows only) | a reference attribute/FK-like pointer to the paired original sale, carried for lineage | FR-013 (reference only, not the reporting axis) |

## 2. `is_return` classification (RC8-derived)

```yaml
# illustrative shape only -- concrete column names decided at Stage 2
is_return:
  source_column: "<authoritative transaction_type/reason column>"   # e.g. transaction_type
  derivation: "true when <source_column> = 'RETURN' (or equivalent authoritative value)"
  never_derived_from: "measure sign (quantity/amount < 0)"          # RC8's explicit prohibition
  discrepancy_handling: "any row where sign and <source_column> disagree is surfaced in
                          assumptions.md / unresolved-questions.md as a data-quality
                          finding -- never silently coerced to agree"
```

This is documented in `source-map.yaml`'s `columns[]` entry for the classification
field (same shape `retail_store_sales/source-map.yaml` already uses for every
column: `source_name` / `decision` / `reason` / `rename_to` / `silver_type` /
`missing_policy` / `pii` / `gold_placement`) -- no new YAML key is introduced for
this concept; RC8 is recorded under `defaults.adopted`, not `deviations`, for the
first time in this repo's worked examples.

## 3. Return Value contract (additive)

Shape follows `templates/metric-contract.yaml` EXACTLY -- no new field:

```yaml
name: "ReturnValue"                    # PascalCase, short
grain: "<the grain this metric is valid at, e.g. return line>"
formula_intent: "The sum of the returned money value across all kept return lines
                  (absolute value of refunded/reversed sales)."
owner: "<named metric owner -- filled at build time, never the authoring agent>"
binds_to:
  gold_table: "gold.<returns_fact_or_view>"
  columns:
    - "<return_value_column>"
  pii_sensitive: false
readiness:
  status: "not_started"                # promoted only by a named human's approval
  evidence: []
  blocking_reasons: []
ambiguities: []                        # A2 is resolved by this example's own RC8
                                        #   modelling choice, not left open here
```

**Additivity is stated in PROSE**, matching `returns-rate-value.md`'s own statement
and AD1's closed vocabulary (`skills/retail-kpi-knowledge/contracts/*.md`'s
`**Additivity**` heading convention) -- e.g. a comment or an accompanying narrative
line: `# Additivity: Fully additive (summable across any dimension)`. This is
**not** a new machine-readable field on the contract; `metric-contract.yaml` has no
`additivity:` key today and FR-005 forbids adding one. AD1's own read surface is
`skills/retail-kpi-knowledge/contracts/*.md`, not `mappings/*/metrics/*.yaml` --
this contract's additivity statement is for human/narrative consistency with
`returns-rate-value.md`, not for AD1 to parse.

## 4. Return Rate % contract (non-additive)

Same shape as Sec 3, with two differences:

- `formula_intent` states a RATIO in plain language (e.g. "Return Value divided by
  Net Sales for the same period, expressed as a percentage"), never a SUM.
- Its prose additivity statement reads "Non-additive (must be recomputed per level,
  never summed directly)", matching `returns-rate-value.md` verbatim.
- If this contract records a derivation lineage (its two parent measures), that
  lineage MUST NOT compose the rate by direct SUM of Return Value and a sales-value
  measure -- it is a ratio recomputed base-over-base, the AD1-legal composition kind
  (research.md Sec 1 row 7; FR-006).

```yaml
name: "ReturnRatePercent"
grain: "<the rollup grain the rate is valid at, e.g. branch-period>"
formula_intent: "Return Value for a period divided by Net Sales for the same period,
                  expressed as a percentage. Recomputed at each reporting level; never
                  summed directly from a finer level's rate."
owner: "<named metric owner>"
binds_to:
  gold_table: "gold.<returns_fact_or_view>"
  columns:
    - "<return_value_column>"
    - "<net_sales_column>"
  pii_sensitive: false
readiness:
  status: "not_started"
  evidence: []
  blocking_reasons: []
ambiguities: []                        # at build time, likely gains an A3 entry
                                        #   (date axis) with decision_status:
                                        #   undecided, number_moving: true --
                                        #   which per templates/metric-contract.yaml's
                                        #   own fail-safe forces readiness.status to
                                        #   blocked, not a clean not_started. This
                                        #   sketch shows the blank shape; the build-
                                        #   time author fills the honest state.
```

## 5. Cross-period return

A return whose transaction date falls in a later reporting period than its original
sale's date. This is the entity the worked reconciliation figure (FR-007, SC-003)
must demonstrate correctly. Its shape in the synthetic dataset:

```text
original sale:  date = P1, amount = +X, is_return = false
paired return:  date = P2 (P2 > P1, different reporting period),
                amount = -X (or the returned portion), is_return = true,
                original-sale reference = <the P1 sale's key>  # lineage only
```

The narrative doc's worked figure shows the P1 and P2 period totals under the
chosen primary date axis (FR-013's reversible default: return date = the return
row's own transaction date) and states, in prose, that the value is neither dropped
nor double-counted under that axis. This entity does NOT carry an `additivity`
field or any new machine-readable marker -- it is proven by a worked arithmetic
example in the narrative doc, the same evidentiary style
`retail-store-sales.md` Sec 4 already uses for its own reconciliation figures.

## 6. Synthetic source-data required-row shape (Clarification Q5)

The minimum set of rows the hand-authored dataset must contain (illustrative
columns only; exact names decided at Stage 2):

| Row purpose | is_return (per authoritative column) | quantity/amount sign | date | notes |
|---|---|---|---|---|
| a normal sale | false | positive | P1 | baseline |
| a same-period return | true | negative (or zero/positive per discrepancy case below) | P1 | exercises RC8 derivation |
| a cross-period return | true | negative | P2 (> P1) | the FR-007 worked figure's subject; carries the original-sale reference |
| a sign/type discrepancy row | true (per column) | positive (disagrees with the column) OR false (per column) with a negative amount | either | FR-004's discrepancy check; surfaced, never coerced |

No row encodes an exchange scenario unless one is later found necessary; if none is
included, the narrative states exchange handling is out of scope for this instance
(Clarification Q3) without answering the underlying policy question.

## 7. Worked-example artifact set (cross-cutting shape)

The complete set this feature's build must produce, matching spec 084's
completeness contract Tier 1 sections A-H and `retail_store_sales`'s own set
(spec.md Key Entities; no narrower or differently-shaped set is acceptable):

```text
mappings/<returns-example>/
├── source-profile.md
├── source-map.yaml
├── assumptions.md
├── unresolved-questions.md
├── reconciliation-report.md
├── <synthetic dataset file(s)>
├── metrics/ReturnValue.yaml
├── metrics/ReturnRatePercent.yaml
├── design/ (layout, visual list, binding map)
├── handoff/ (pack + review checklist)
└── readiness-status.yaml

docs/worked-examples/<returns-example>.md
docs/worked-examples/README.md            # edited: one new index row
```

## 8. `readiness-status.yaml` shape (no numeric score -- hard rule #9)

Identical structure to `mappings/retail_store_sales/readiness-status.yaml`
(`stages:` with the seven stage keys, each `{status, evidence[], blocking_reasons[]}`;
top-level `approvals:` list; `next_action`; `last_checked_at`; `checked_by`). The
ONLY difference in shape-level expectation for this feature:

- Every stage whose evidence would require a live DB connection or F016 is recorded
  `blocked` (never `pass`) with a `blocking_reasons[]` entry naming the missing live
  surface (FR-009).
- `approvals:` is designed to START and STAY empty for every stage until a real
  named human signs (FR-010) -- this is a stronger initial condition than
  `retail_store_sales` ended at (which already has three recorded approvals); this
  feature's plan does not assume any approval exists at authoring time.
- No `score`, `confidence`, `health`, `maturity`, or "N of M" / percentage field
  appears anywhere in the file (FR-011).
