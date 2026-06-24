# Phase 1 Data Model -- Tower BI Agent Kit Foundation (001)

**Plan**: [`plan.md`](./plan.md) | **Date**: 2026-06-24

> This feature has no runtime database schema. Its "data model" is the set of **five
> committed mapping-gate artifacts** -- document/record shapes a table's mapping must
> satisfy. They map 1:1 to the spec's Key Entities and to the templates. The
> machine-readable one is `templates/source-map.yaml`; the others are structured Markdown.
> The *downstream* schema these artifacts describe (the medallion `gold` star) is owned by
> ADR 0002 / the playbook, not re-modeled here.

## The five artifacts (entities)

### 1. Source Profile  (`templates/source-profile.md`)
- **Represents**: a raw source's shape, quality, and semantics, with numbers.
- **Key fields**: table id; source system; connection (read-only, `.env`-sourced); row +
  column counts; per-column profile (name, landed type, missingness measured as
  `'' OR NULL`, distinct cardinality, candidate-key flag); semantics (code<->label,
  fan-out, hierarchy shape, returns population, encoding, drift); candidate grain + PK
  (verified unique on the data).
- **Formalizes**: playbook Phase 1.
- **Filled by**: a profiling run (C086 = 249,106 raw rows -- cited instance).

### 2. Source Map  (`templates/source-map.yaml`)  -- the spine
- **Represents**: the machine-readable per-column mapping from source to silver to gold.
- **Key fields**: `meta` (grain + PK decided first, profiled-from ref); `defaults`
  (adopted vs deviation ADR ids); `columns[]` (source_name, decision keep/drop/derive,
  rename_to, silver_type, missing_policy, pii, gold_placement); `gold_star` (fact +
  measures; dimensions with `_sk` + `-1` unknown member; degenerate dims; `generate_series`
  date dim); `derived_columns` (e.g. `is_return` from the authoritative column).
- **Formalizes**: playbook Phase 2.0-2.5 + 2.7-2.8; ADR RC7/RC14.
- **Validation**: must be valid YAML; `gold_placement` dim references must resolve to a
  `gold_star.dimensions` entry; `meta.grain` == `fact.grain`.

### 3. Assumptions record  (`templates/assumptions.md`)
- **Represents**: which ADR 0002 RC1-RC16 defaults were adopted as-is vs deviated from.
- **Key fields**: per-default adopted flag; per-deviation (ADR id, alternative ruling,
  **triggering data fact**, where recorded). Integrity rule: a `deviated` row MUST have a
  triggering data fact (a deviation without one is a defect).
- **Formalizes**: playbook Phase 2 + 3; realizes constitution Principle VI.

### 4. Unresolved Question  (`templates/unresolved-questions.md`)
- **Represents**: an open, build-blocking decision the agent cannot settle alone.
- **Key fields**: Q-id; question; why it blocks; **who must answer** (analyst / governance
  / data-owner); proposed default; status (open/answered); resolution. Plus the inherited
  kit-level open decisions (Q-1..Q-4 from research.md).
- **State rule**: no `silver.*` SQL is written while any question is `open`.
- **Formalizes**: playbook Phase 2 decision points + Phase 4; realizes Principle V.

### 5. Reconciliation Report  (`templates/reconciliation-report.md`)
- **Represents**: the live-acceptance contract for a built table (live-validator
  CATEGORIES only -- no validator logic this slice).
- **Key fields**: PK uniqueness (rows = distinct PK, 0 NULL); date-dim coverage
  (contiguous, spans every real date); orphan-FK count (0; rows on each `-1` member as a
  DQ signal); cross-layer measure reconciliation (source->silver->gold, penny-exact, every
  measure); per-category + overall verdict.
- **Formalizes**: playbook Phase 5/6; ADR RC2/RC15/RC16. Belongs to the deferred
  `retail validate` surface (Principle VIII).
- **Filled by**: a read-only live run (C086 = 246,916 rows, penny-exact across 5 measures
  -- cited instance).

## Flow between artifacts

```text
source-profile.md   (evidence: the numbers)
        |
        v
source-map.yaml     (decisions: keep/drop/type/grain/star placement)  <-- the spine
        |  \
        |   +--> assumptions.md          (which defaults adopted vs deviated + why)
        |   +--> unresolved-questions.md (what blocks the build -- stop-and-ask)
        v
   [REVIEW GATE]  (playbook Phase 4 == mapping-gate review; all questions answered)
        |
        v
   silver.* + gold.* migrations  (built only after the gate passes)
        |
        v
reconciliation-report.md  (live acceptance: PK / coverage / orphans / penny-exact)
```

## Out of scope (this data model does NOT define)

- The concrete `gold` star DDL -- owned by ADR 0002 / `warehouse/migrations/` (no new
  tables this slice).
- Any C086-specific columns/codes -- C086 is a cited filled instance, never the schema
  (Principle VII).
