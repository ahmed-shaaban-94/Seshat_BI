# Quickstart -- Bringing a New Retail Table Through the Tower BI Agent Kit

**Plan**: [`plan.md`](./plan.md) | **Date**: 2026-06-24

> The forward-looking artifact: the end-to-end path a **new** retail source table takes
> through the kit, from raw landing to a governed Power BI model. The *questions and gates*
> below generalize to any table; C086 is cited as the first filled instance. This is the
> workflow an agent (Layer D) runs conversationally and a reviewer audits from committed
> files.

## Prerequisites

- Source landed faithfully in `bronze.<table>_raw` (all-TEXT, no cleaning yet).
- Read-only DB access; credentials in the git-ignored `.env` (never inline).
- The kit's normative layer: `.specify/memory/constitution.md` (v1.1.0) and the five
  templates under `templates/`.

## The path (gate-by-gate)

### Step 1 -- Profile  (playbook Phase 1)
Copy `templates/source-profile.md` and fill it from a read-only profiling pass: row/column
counts, per-column missingness **measured as `'' OR NULL`** (not `IS NULL` alone),
cardinality, candidate-key uniqueness on the data, returns population, encoding/drift.
- **Exit gate**: you can state grain, candidate keys, returns rule, and top DQ issues --
  **with numbers**.

### Step 2 -- Map  (playbook Phase 2.0-2.5/2.7-2.8 -> `templates/source-map.yaml`)
Fill the source map -- **grain and PK first** (they become non-droppable), then per-column
keep/drop/rename/type/PII/gold-placement, then the `gold_star` (1 fact at the grain;
conformed dims with `_sk` + a `-1` unknown member; degenerate dims; a `generate_series`
date dim). Start from the **ADR 0002 RC1-RC16 defaults** -- record only deviations.

### Step 3 -- Record decisions  (`assumptions.md` + `unresolved-questions.md`)
- `assumptions.md`: mark each RC1-RC16 default adopted vs deviated; every deviation needs its
  **triggering data fact**.
- `unresolved-questions.md`: log every build-blocking question the agent **cannot decide
  alone** -- business-rollup mappings (analyst MUST supply; never invented), PII
  publish-safety (governance sign-off), grain ambiguity, sentinel-vs-null. Each carries a
  **who-must-answer** owner. **The agent stops here and asks** (constitution Principle V).

### Step 4 -- Review gate  (playbook Phase 4 == the mapping gate)
A human reviews the profile + map + assumptions + open questions. **No `silver.*` SQL is
written until every blocking question is `answered`.** This is the hard gate of Principle IV
-- silver is downstream of an approved map.

### Step 5 -- Build silver  (playbook Phase 5)
Write the silver migration as a **numbered, idempotent** `warehouse/migrations/NNNN_*.sql`
(DROP+CREATE in one `BEGIN/COMMIT`; transform order: TRIM -> fix encoding -> junk filters
-> `''`->NULL -> casts via `NULLIF` -> numeric filters -> derived columns). The static gate
(`retail check`) enforces snake_case, medallion schemas, migration form, etc.

### Step 6 -- Build gold  (playbook Phase 6)
Write the `gold` Kimball star: fact at the silver grain + conformed dims; `_sk` IDENTITY
keys; a `-1` unknown member per dim; fact FKs `COALESCE(...,-1)`; transaction ids as
degenerate dims; `dim_date` from `generate_series`. FK constraints added **after** load.

### Step 7 -- Reconcile (live acceptance)  (playbook Phase 5/6 -> `reconciliation-report.md`)
Run the read-only acceptance checks and fill the report: PK uniqueness on materialized rows;
date-dim coverage (contiguous, spans every real date); **0 orphan FKs** (count rows on each
`-1` member as a DQ signal); penny-exact measure reconciliation source->silver->gold for
**every** measure. These are the deferred `retail validate` live categories (Principle VIII).

### Step 8 -- Build the Power BI model
Power BI reads `gold` **only** (Principle III), via parameters (no baked connection
strings). `pbi-cli` is the later authoring adapter for this step (Principle II). The static
gate enforces gold-only sourcing, PascalCase measures, single-direction relationships, etc.

## The gates, in one line each

| Gate | Enforced by | Blocks until |
|------|-------------|--------------|
| Profile exit | human/agent judgment | grain + keys + returns + DQ stated with numbers |
| Mapping review (Step 4) | human review (Principle IV) | every `unresolved-questions` entry answered |
| Static governance | `retail check` (23 rules, CI) | non-zero exit cleared (snake_case, gold-only, migration form, ...) |
| Live acceptance (Step 7) | `reconciliation-report` (future `retail validate`) | PK unique, date coverage, 0 orphans, penny-exact |

## What an agent must NOT do (stop-and-ask -- Principle V)

Invent a business-rollup mapping; publish PII without governance sign-off; resolve grain
ambiguity or a non-unique PK silently; pick a sentinel over NULL without recording it; write
silver while a blocking question is open. In every case: **raise an `unresolved-questions`
entry and stop.**

## Cited filled instance

See `docs/worked-examples/c086-pharmacy.md` for all of the above filled end to end (C086:
249,106 raw -> 246,916 silver rows, 1 fact + 6 dims, 16/16 ADR defaults, penny-exact
reconciliation across 5 measures). C086 is the example, **never** the universal schema.
