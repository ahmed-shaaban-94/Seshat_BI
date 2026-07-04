# Implementation Plan: 088-drill-nav-periods

**Branch**: `088-drill-nav-periods` (worktree ZEUS) | **Spec**: `spec.md` | **Clarify**: `clarify.md`
**Status**: Draft (stops at ratify ledger)

## Approach

Additive DEFINE-only authoring across two feature areas:
- **#4 (F011A)**: drill_through/drill_down INTENT fields on visual-spec + a new
  report-composition.yaml (references pages, never inlines).
- **#5 (F009)**: three growth-metric contracts authored as STRUCTURE (Non-additive,
  base-over-base, AD1-legal) with the comparison-baseline (uncoded) + A11 flagged owner-pending -- the agent writes
  no baseline definition.

No `retail check` rule, no PBIR/DAX/SQL.

## Constitution / boundary check

| Principle / boundary | How honored |
|---|---|
| DEFINE / CHECK | template fields + new template + new contract files; no rule |
| #4 intent vs execution | drill/nav = design intent (offers/target/hierarchy by name); F016 renders. No runtime field. |
| #5 Principle V (BLOCKING) | comparison-baseline (uncoded) + A11 same-store flagged undecided/blocking; agent writes NO definition; Status = honest open |
| AD1 schema-guard | each growth contract declares `Non-additive` + base-over-base derivation (verified AD1 reads contracts/*.md and ERRORs a direct-sum non-additive) |
| No numeric score (#9) | growth = ratio relation in intent; no score field |
| Reference-by-name (VII) | drill targets, composition pages, growth factors = names |
| Generic (VII) | placeholders; no tenant/C086 |

## Components

1. **`templates/visual-spec.yaml`** (+2 blocks in/near `interactions`):
   `drill_through{offers,target_page,carried_filters}`, `drill_down{hierarchy}` --
   intent-only, reference-by-name, comment states F016 renders.
2. **`templates/report-composition.yaml`** (NEW, gated on clarify C2):
   `pages[]` (blueprint refs), `landing_page`, `navigation[]` (incl. footer DQ link),
   `cross_page_filters[]`. Orphan page ref = blocking.
3. **`skills/retail-kpi-knowledge/contracts/net-sales-growth.md`** (NEW):
   Non-additive; derives base-over-base from NetSales this-vs-baseline; comparison-baseline (uncoded) flagged.
4. **`.../same-store-sales-growth.md`** (NEW): Non-additive; comparison-baseline (uncoded) + A11 flagged;
   comparable-store definition owner-pending.
5. **`.../ytd.md`** (NEW): Non-additive/period-accumulation; comparison-baseline / partial-period (uncoded)
   normalization) flagged.
6. **`reports/blueprints/executive-summary.yaml`** (comment annotation only):
   note the `<period-comparison-contract>` placeholder now has a structure to ref.

## AD1 correctness (the load-bearing guard)

Each growth contract:
- `**Additivity**` line opens `Non-additive` (closed vocabulary).
- `**Derives from**` states a base-over-base ratio (e.g. "Net Sales Growth % =
  (Net Sales[period] - Net Sales[baseline]) / Net Sales[baseline]" -- a ratio
  recompute, NOT a direct sum of a non-additive child) so AD1 marks it LEGAL.
- Reference base contracts by ID (KPI-MC-##), matching the existing lineage style.

## What this does NOT touch (scope guards)

- No comparison-baseline / A11 RULING (Principle V; owner rules later).
- No real drill/nav/growth VALUES for actual pages/KPIs (FR-011).
- No `retail check` rule (FR-010; optional target-page-resolves rule deferred).
- No binding change to executive-summary (comment only).

## Test strategy (DEFINE-only)

- YAML/markdown validity of every edited/new file.
- AD1 correctness: run `retail check` (AD1 reads the 3 new contracts) -> green;
  spot-run `test_additivity_consistency`.
- Boundary grep: new drill/nav blocks contain no execution/runtime token; growth
  contracts contain no agent-written baseline definition (comparison-baseline + A11 marked open).
- Generic-placeholder + ASCII/no-BOM check.

## Sequencing

One PR. US1 (drill fields) + US3 (growth contracts) are P1; US2 (report-composition)
P2, gated on C2. No registry/count change (no @register rule) -> no serialization
point.

## Risks

- **AD1 ERROR on a misdeclared growth contract** -> the AD1 run in T-checks catches
  it; base-over-base derivation is mandatory (FR-006).
- **Agent drifting into defining the baseline** -> FR-007 + C1 make the comparison-baseline + A11
  owner-pending explicit; the adversarial reviewer is aimed at exactly this.
- **report-composition colliding with one-file-one-page** -> C2 confirms
  absent-by-gap; the artifact only references pages.
