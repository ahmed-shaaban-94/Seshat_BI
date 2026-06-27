# Metric Contracts

A metric contract is the governed, reviewable definition of one KPI. It is the artifact
this layer produces and the input every downstream layer consumes.

## Why contracts exist

Without contracts, each report author re-derives a KPI from memory. The result is
duplicated DAX (three measures that all claim to be "net sales"), and ambiguous
dashboards (two tiles labelled the same that disagree). A contract fixes the meaning
once, names an owner, and forces ambiguities to be resolved before code is written.

A contract does three jobs:

1. **Pins meaning** — one agreed business definition and formula.
2. **Pins shape** — grain, additivity, required fields, dimensions, filters.
3. **Pins handoff** — what the DAX/semantic layer must implement and what it must not
   assume.

## Required sections

Every contract in `contracts/` uses this fixed structure:

- Business question
- Business definition
- Formula in business terms
- Required fields
- Grain
- Additivity
- Recommended dimensions
- Filters / exclusions
- Interpretation
- Common mistakes
- Validation checks
- Semantic model / DAX handoff notes
- Dashboard use
- Priority
- Owner
- Status — one of **Seeded**, **Planned**, **Needs business definition**

The canonical blank is `references/metric-contract-template.md`.

## Status meaning

- **Seeded** — contract is complete and live in this seed; safe to hand off.
- **Planned** — KPI is recognised and scheduled but not yet contracted; do not hand off.
- **Needs business definition** — a required policy (VAT, returns, cost method,
  same-store, snapshot date) is unresolved; the KPI is blocked until the owner decides.

## Handoff to DAX

A completed contract hands off to the DAX/semantic layer with:

- the business-terms formula (never DAX code from this layer),
- the required fact/dimension fields and which are assumptions,
- the grain and additivity call (so the measure aggregates correctly),
- filter/exclusion rules (so filter context is built right),
- known ambiguities still open (so they are not silently coded around).

The DAX layer owns the actual measure, filter context, and relationships. This layer
owns only the contract. A contract that fails the metric-contract-review-checklist is
**not** ready for handoff, and no contract grants dashboard-readiness — that is the
Readiness layer's decision.
