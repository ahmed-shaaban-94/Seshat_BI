# Quickstart: Returns/Refunds Fact Worked Example

**Feature**: `specs/096-returns-refunds-fact-example/` | **Date**: 2026-07-04

**Purpose**: How an agent or a developer exercises this feature once built (Stages
2-6 authored under `mappings/<returns-example>/` and
`docs/worked-examples/<returns-example>.md`). This is a verification walkthrough,
not a build guide -- the build itself follows the same skills/playbook every other
table uses (`source-mapping`, `retail-build-warehouse`, `retail-semantic-check`,
`dashboard-design`).

## Prerequisites

- The feature has been implemented: `mappings/<returns-example>/` (full artifact
  set per data-model.md Sec 7) and `docs/worked-examples/<returns-example>.md`
  exist and are committed.
- No live database connection or F016 (Power BI execution adapter) is required for
  any step below -- every check here is static / repo-only, consistent with
  Principle VIII.

## Step 1 -- Confirm the completeness bar this instance targets

```text
Read: specs/084-worked-example-factory/contracts/worked-example-completeness.md
Read: mappings/<returns-example>/ (the full directory)
```

Walk Tier-1 sections A-H item by item against the built artifact set. Each item is
binary (yes/no, cited to a real file/line) -- never report a fraction or percentage
(hard rule #9). Record which Tier-1 items are satisfied and which (if any) are
honestly incomplete.

## Step 2 -- Verify the additivity split (SC-001, US1)

```text
Read: mappings/<returns-example>/metrics/ReturnValue.yaml
Read: mappings/<returns-example>/metrics/ReturnRatePercent.yaml
Read: skills/retail-kpi-knowledge/contracts/returns-rate-value.md
```

Confirm, side by side:

- `ReturnValue`'s stated additivity (in its prose/comment) matches "additive" /
  "Fully additive".
- `ReturnRatePercent`'s stated additivity matches "non-additive" / "Non-additive".
- Neither statement introduces a new vocabulary word beyond AD1's closed set
  (Fully additive / Semi-additive / Non-additive).

This is a human/textual side-by-side read. It is NOT a `retail check` rule
invocation for this specific comparison -- no rule reads
`mappings/*/metrics/*.yaml` for additivity today.

## Step 3 -- Run `retail check` and confirm AD1 stays clean (SC-002)

```bash
retail check
```

Expected: exit code 0, including rule AD1. AD1's read surface is
`skills/retail-kpi-knowledge/contracts/*.md` only (confirmed in
`src/retail/rules/additivity_consistency.py`'s `_CORPUS_RE`) -- this feature does
not edit any file under that glob other than files it might add there (it adds
none; its two new contracts live under `mappings/<returns-example>/metrics/`,
outside AD1's corpus). Zero new AD1 ERROR findings is therefore expected by
construction; running the check confirms nothing else was inadvertently broken.

## Step 4 -- Verify the cross-period reconciliation figure (SC-003, FR-007)

```text
Read: docs/worked-examples/<returns-example>.md
```

Locate the worked reconciliation section. Confirm it:

- States which date axis (sale date or return date) is primary for the worked
  figures, and cites FR-013's reversible default explicitly (return date = the
  fact's own transaction date; original sale date is a reference attribute only).
- Shows a real arithmetic example, sourced from the example's own committed
  synthetic data, where a cross-period return's value is neither dropped nor
  double-counted under that axis.
- Does NOT claim the chosen axis is the business's operative reporting axis (that
  remains OPEN -- see Step 7).

## Step 5 -- Verify `is_return` derivation and the discrepancy check (SC-004, US2)

```text
Read: mappings/<returns-example>/source-map.yaml
Read: mappings/<returns-example>/assumptions.md
Read: mappings/<returns-example>/unresolved-questions.md
```

Confirm:

- `source-map.yaml`'s classification column entry derives `is_return` from an
  authoritative transaction-type/reason column, and RC8 is listed under
  `defaults.adopted` (not `deviations`) for this table.
- The planted sign-vs-transaction-type discrepancy row (data-model.md Sec 6) is
  surfaced in `assumptions.md` or `unresolved-questions.md` as a data-quality
  finding, not silently coerced.
- The gross/net arithmetic (gross minus return value equals net, or the example's
  own stated equivalent) is shown with a real evidence figure in the narrative doc.

## Step 6 -- Verify the honest stopping point (SC-005, US3)

```text
Read: mappings/<returns-example>/readiness-status.yaml
```

Confirm:

- Every stage requiring a live DB connection or F016 is `blocked`, each with a
  `blocking_reasons[]` entry naming the missing live surface -- never a fabricated
  `pass`.
- Every `pass` entry (if any -- e.g. a static-only sub-check) cites a real
  committed-artifact evidence line.
- No numeric confidence/health/maturity score and no "N of M" / percentage
  completeness tally appears anywhere in the file or any other artifact this
  feature produced.

## Step 7 -- Verify approvals were never self-granted (SC-006, FR-010)

```text
Read: mappings/<returns-example>/readiness-status.yaml (approvals: section)
```

Confirm every `approvals[]` entry (if any exist at review time) names a real human
+ authority class, never the authoring agent. At minimum, confirm Mapping Ready and
Semantic Model Ready either show an empty `approvals[]` slot or a genuinely named
human's signed entry -- never a placeholder or role-only name.

Also confirm `unresolved-questions.md` still carries, as OPEN (not silently
resolved by this feature):

- The VAT/tax treatment of refunds (Clarification Q2).
- The operative reporting date axis, sale-date vs. return-date (Clarification Q1b
  / KPI ambiguity A3) -- distinct from the reversible worked-example default used
  for the synthetic figures (Step 4).

## Step 8 -- Verify the genericity and conformance boundaries (SC-007, FR-012/FR-014)

```text
Grep: "C086" across mappings/<returns-example>/ and docs/worked-examples/<returns-example>.md
Check: docs/quality/conformed-dimension-map.yaml does not exist or, if it now does
       (a later feature may have created it), was NOT edited by this feature's commits
```

Confirm zero hits for C086 or any client-specific fact, and confirm this feature's
artifacts never authored or modified a conformed-dimension declaration file --  any
shared-dimension-name observation is prose only, pointing to spec 087/HR1 as the
mechanism, not a self-made declaration.

## Done

If Steps 1-8 all pass, the returns/refunds worked example has proven the medallion
spine (Stages 2-6) on a fact type that breaks naive additivity, without inventing a
business policy, without self-granting an approval, and without fabricating a
readiness score -- matching this feature's spec exactly.
