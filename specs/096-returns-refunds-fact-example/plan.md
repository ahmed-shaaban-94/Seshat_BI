# Implementation Plan: Returns/Refunds Fact Worked Example (Negative-Quantity Additivity)

**Branch**: `096-returns-refunds-fact-example` | **Date**: 2026-07-04 | **Spec**: `specs/096-returns-refunds-fact-example/spec.md`

**Input**: Feature specification from `specs/096-returns-refunds-fact-example/spec.md`
(Clarifications session 2026-07-04, Q1-Q5 resolved)

**Note**: This template is filled in by the `/speckit-plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

## Summary

Seshat BI ships exactly one worked example (`retail_store_sales`), and that example
explicitly recorded returns as `N/A` (RC8 deviation). This feature authors the design
for a SECOND worked example -- a generic returns/refunds fact -- that walks readiness
Stages 2-6 (Mapping Ready through Semantic Model Ready) on the one fact type that
breaks naive additivity: signed quantities/amounts, an additive returns-VALUE measure
paired with a non-additive returns-RATE measure, and a documented cross-period
reconciliation. The technical approach is NOT novel: it reuses the exact artifact
shapes, gates, RC defaults, and additivity vocabulary already shipped
(`mappings/<table>/` five-artifact set, `templates/metric-contract.yaml`, RC1-RC16,
rule AD1's closed vocabulary), applied to a new domain. It adds no new rule, no new
RC default, no new readiness stage, and no new machine-readable field -- the entire
"newness" is the domain (returns) and the two governance-open items it must correctly
leave open (VAT/tax treatment of refunds; the operative reporting date axis).

## Technical Context

**Language/Version**: N/A for this planning stage -- artifacts are Markdown/YAML
(governance docs) plus SQL migrations authored later at build time (Stage 3-4), same
dialect as the existing spine (`warehouse/migrations/*.sql`, Postgres-first per
Principle III).

**Primary Dependencies**: None new. Reuses shipped: `retail check` (static gate,
already includes rule AD1), the `mappings/<table>/` template set
(`templates/source-profile.md`, `source-map.yaml`, `assumptions.md`,
`unresolved-questions.md`, `reconciliation-report.md`, `metric-contract.yaml`,
`design/`, `handoff/`, `readiness-status.yaml`), `docs/decisions/0002-retail-cleaning-defaults.md`
(RC1-RC16), `skills/retail-kpi-knowledge/domains/returns.md` +
`skills/retail-kpi-knowledge/contracts/returns-rate-value.md` (KPI-MC-08).

**Storage**: A committed, hand-authored synthetic dataset under
`mappings/<returns-example>/` (Clarification Q5) -- not a live DB at authoring time.
At build time (out of this plan's scope), silver/gold tables would live in the same
Postgres warehouse `retail_store_sales` uses, under the shared `gold` schema
(Principle III).

**Testing**: `retail check` (static gate; stdlib-only rules, reads committed files)
is the only automated check this feature's artifacts are exercised against. No new
test framework, no new rule, no live `retail validate` run assumed (Principle VIII --
deferred, no live DB available).

**Target Platform**: N/A (documentation/governance artifacts + SQL text; no runtime
service).

**Project Type**: Documentation/governance feature inside a standalone analytics-repo
kit (matches every other worked-example / Product-Module feature in this repo, e.g.
084, 087, 009). Not a web/mobile/library project in the generic template's sense.

**Performance Goals**: N/A.

**Constraints**: Windows 260-character path budget (Principle IX) -- the chosen
`<returns-example>` table name and every nested artifact path must stay short
(FR-015). ASCII / UTF-8-without-BOM only, no glyphs (FR-015). No secrets, no real
host/DSN anywhere (Principle IX).

**Scale/Scope**: One new narrative doc
(`docs/worked-examples/<returns-example>.md`), one new README index row, one new
`mappings/<returns-example>/` directory with the full artifact set, two new metric
contracts, one small hand-authored synthetic dataset. No changes to any shipped
rule, template, RC default, or another table's artifacts.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design below.*

| Principle | How this design satisfies it |
|---|---|
| **I -- Agent-First / Gate-Enforced** | This feature adds NO new rule and weakens NO existing gate. Compliance is demonstrable exactly as every other table's is: run `retail check` over the new `mappings/<returns-example>/` + `docs/worked-examples/<returns-example>.md` paths and it exits 0 (C-H5 in the 084 completeness contract). Nothing here advances a readiness stage without the required evidence + a gate pass; the design fails CLOSED by construction (no self-authored bypass). |
| **III -- Medallion / Gold-Only** | The example's gold layer is its own Kimball star (a returns fact + conformed dimensions + a marked `dim_date`, mirroring `retail_store_sales`'s `fct_sales_rss` + 4 dims + `dim_date_rss` shape), built Postgres-first, in the same shared `gold` schema. Its two metric contracts (`binds_to.gold_table`) bind to `gold.*` only, per `templates/metric-contract.yaml`'s existing FR-012 rule -- never silver/bronze. Any question of whether this star's dimensions are the SAME conformed dimension as an existing star's is explicitly deferred to spec 087/HR1 (noted in prose only, per FR-012 of this spec), not answered here. |
| **IV -- Source-Mapping-Before-Silver** | The design's Project Structure below places `mappings/<returns-example>/source-map.yaml` + `assumptions.md` + `unresolved-questions.md` (Stage 2, Mapping Ready) strictly before any `warehouse/migrations/*_silver_<returns-example>.sql` file. No silver SQL is authored or planned until that map's gate is CLEARED (mirrors the existing `retail-onboard-table` / `source-mapping` skill sequencing). |
| **V -- Agent-Stops-at-Judgment** | Two genuine business-policy questions this design must NOT resolve are explicitly carried forward as OPEN in `unresolved-questions.md` at build time, never answered here or there: (a) VAT/tax treatment of a refund (Clarification Q2), (b) the operative reporting date axis, sale-date vs. return-date (Clarification Q1b / KPI ambiguity A3) -- the reversible worked-example default (return date = the fact's own transaction date) governs ONLY the example's own synthetic figures and is explicitly barred from being cited as having settled A3 (FR-013). Every named-human approval seam (Mapping Ready, Semantic Model Ready at minimum) is designed to start and stay with an EMPTY `approvals[]` entry -- the agent never self-grants (FR-010). |
| **VI -- Defaults-Then-Deviations** | RC8 ("keep returns, derive `is_return` from the authoritative transaction-type column, never sign") is the ADOPTED default this example is specifically built to exercise for the first time (unlike `retail_store_sales`'s RC8 = N/A). The synthetic source-data posture (Clarification Q5) and the reversible date-axis default for worked figures (FR-013) are both recorded as Principle-VI defaults with their triggering rationale cited, not silent choices. |
| **VII -- C086-is-an-Example-not-the-Schema** | The example is a GENERIC synthetic returns dataset -- no client-specific fact, billing code, or C086-archived specific appears anywhere (FR-014, SC-007). The design's data-model.md below sketches artifact SHAPES, not filled pharmacy/client content. |
| **VIII -- Static-First / Live-Deferred** | No live DB and no F016 (Power BI execution adapter) are assumed available (Sec 4 of research.md). Every live-gated check (Gold Ready's live PK/grain/orphan-FK/reconciliation checks; any live semantic-model connection) is designed to be recorded `blocked` with a `blocking_reasons[]` entry, or `[PENDING LIVE PROFILE]` in numeric cells -- never a fabricated `pass` (FR-009). |
| **IX -- Secrets / Reproducibility** | The synthetic dataset and every migration/model file are committed, ASCII, UTF-8-without-BOM, with no real host/DSN/secret (Power BI parameterized connection only, matching `retail_store_sales`'s TMDL precedent). The chosen `<returns-example>` table name and all nested paths are kept short for the Windows 260-char budget (FR-015). |
| **Hard rule #9 (no fabricated score)** | No numeric confidence/health/maturity score or "N of M" / percentage completeness tally is designed into any artifact. Readiness is expressed only via the four-status model (`not_started` / `blocked` / `warning` / `pass`) + `evidence[]` + `blocking_reasons[]`, exactly like `retail_store_sales`'s `readiness-status.yaml` (FR-011, SC-005). |

**Result**: PASS. No principle requires a documented complexity exception; see
Complexity Tracking below (empty by design).

## Project Structure

### Documentation (this feature)

```text
specs/096-returns-refunds-fact-example/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

No `contracts/` subdirectory is produced by this feature's Phase 1: this feature
consumes spec 084's completeness contract and spec 068/AD1's additivity vocabulary
by reference (cited by path); it does not define a new machine contract of its own.

### Source Code (repository root)

This is a documentation/governance feature (worked example + mapping artifacts), not
an application-code feature. The real repo paths this feature adds or edits at
BUILD time (Stage 2-6, out of this plan's authoring scope but named here so the
seam is unambiguous) are:

```text
docs/worked-examples/
├── README.md                          # EDIT: one new row added to "The examples" table
└── <returns-example>.md               # NEW: narrative doc, mirrors retail-store-sales.md's
                                        #   section structure (Readiness-at-a-glance,
                                        #   Source Ready .. Publish Ready sections, See also)

mappings/<returns-example>/            # NEW directory -- the full artifact set, per
│                                       #   mappings/README.md's layout + the 084
│                                       #   completeness contract (Tier 1, sections A-H)
├── source-profile.md                  # Stage 1 (profile of the hand-authored synthetic data)
├── source-map.yaml                    # Stage 2 (grain/PK/columns/gold placement;
                                        #   is_return derived from transaction-type, RC8)
├── assumptions.md                     # Stage 2 (RC1-RC16 adopted vs. deviated table)
├── unresolved-questions.md            # Stage 2 (gate status; carries forward the
                                        #   OPEN VAT/tax and date-axis owner rulings)
├── reconciliation-report.md           # Stage 4 (numeric cells stay <placeholder> /
                                        #   [PENDING LIVE PROFILE] -- no live DB)
├── <synthetic-data-file>              # the committed hand-authored dataset (Q5)
├── metrics/
│   ├── ReturnValue.yaml               # Stage 5 (additive; templates/metric-contract.yaml shape)
│   └── ReturnRatePercent.yaml         # Stage 5 (non-additive; same shape, no new field)
├── design/                            # Stage 6 (layout, visual list, binding map)
├── handoff/                           # Stage 6/7 (handoff pack; Publish Ready is likely
                                        #   blocked -- out of this feature's required scope,
                                        #   spec covers Stages 2-6)
└── readiness-status.yaml              # cross-cutting: all seven stages, empty approvals[]
                                        #   until a named human signs, no numeric score

warehouse/migrations/
├── NNNN_create_silver_<returns-example>.sql   # Stage 3 (idempotent, numbered)
└── NNNN_create_gold_<returns-example>_star.sql # Stage 4 (Kimball star; suffix distinct
                                                 #   from _rss to avoid physical name
                                                 #   collision in the shared `gold` schema,
                                                 #   e.g. a `_ret` suffix)

powerbi/<ReturnsExample>.SemanticModel/         # Stage 5 (governed TMDL model; authored,
                                                 #   statically checkable; NOT opened in
                                                 #   Power BI Desktop -- F016 deferred)
```

**Explicitly NOT added by this feature** (collision-avoidance allocation, spec.md
Boundary section):

- No file under `src/retail/rules/` -- no new `retail check` rule.
- No new entry/field in `docs/decisions/0002-retail-cleaning-defaults.md` -- no new
  RC default.
- No new key in `docs/readiness/readiness-model.md` -- no new readiness stage.
- No edit to `docs/quality/conformed-dimension-map.yaml` (it does not exist yet;
  spec 087/HR1 is spec-only -- see research.md Sec 2 row 4).
- No edit to `src/retail/rules/additivity_consistency.py` or to any file already
  under its `skills/retail-kpi-knowledge/contracts/*.md` read glob other than this
  feature's own two new contract files, which live under
  `mappings/<returns-example>/metrics/*.yaml` -- OUTSIDE that glob entirely
  (research.md Sec 1 row 7).
- No edit to `docs/worked-examples/retail-store-sales.md` or any of
  `mappings/retail_store_sales/*`.

**Structure Decision**: This feature follows the existing per-table worked-example
structure verbatim (`mappings/<table>/` five-plus artifacts + narrative doc + README
index row), the only precedent this repo has for "a new domain walked through the
readiness spine." No alternative structure was considered: inventing a different
shape for a second worked example would itself violate spec 084's completeness
contract, which is calibrated against exactly this shape (research.md Sec 1 row 1).

## Complexity Tracking

*No entries.* The Constitution Check above found no violation requiring
justification: this feature reuses every governing mechanism (gates, templates, RC
defaults, additivity vocabulary) unchanged and adds no new rule, stage, or
machine-readable field.
