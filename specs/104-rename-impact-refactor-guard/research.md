# Phase 0 Research: Rename/Impact Refactor-Safety Static Rule (HR9)

**Feature**: `104-rename-impact-refactor-guard` | **Date**: 2026-07-04

## Purpose

This is a docs/governance planning artifact (Spec-Kit Phase 0), not application
code. It surveys the SHIPPED precedent this feature reuses, states what it
deliberately stays distinct from, confirms the real input sources HR9 will read
when it is later implemented, and records the capabilities this feature does
NOT assume exist. No code is written in this stage.

## 1. Precedent survey -- what SHIPPED and is reused

### 1.1 The reconcile-and-fail-closed CODE PATTERN (reused)

Three rules are committed on `main` today and share one shape: read a
reference, resolve it against a truth set, fail closed (ERROR) on the first
reference that does not resolve. HR9 reuses this SHAPE, not any of their code
directly (each has its own truth set / reference set).

- **SC1 -- stale-marker sweep** (`src/retail/rules/status_claims.py`, spec 050,
  ratified in `docs/roadmap/roadmap.md`). Reconciles a hand-curated manifest
  (`docs/quality/status-claims.yaml`) of prose build/planned claims against
  `ctx.tracked_files`. Fails loud on a missing manifest, a missing/stale
  `anchor`, or a `built`/`planned` claim that contradicts the tracked-file set.
- **DF1 -- parked-on dependency-edge reconciler** (`src/retail/rules/parked_on.py`,
  spec 051). Same shape applied to a different manifest
  (`docs/quality/parked-on.yaml`): a dependency edge's `doc` + `anchor` +
  `evidence` must all resolve to tracked files, and a `shipped_when_tracked`
  path that is now tracked contradicts the edge (parked-but-shipped).
- **SF1 -- cross-layer checklist fork detector** (`src/retail/rules/rule_sf1.py`,
  spec 086, PR #182). Globs `skills/**/checklists/*.md` from `ctx.tracked_files`,
  groups by basename, and reconciles same-basename collisions against a
  human-authored manifest (`docs/quality/shared-spine.yaml`). Notably, SF1's
  reference SET (the checklist files) is DERIVED from `ctx.tracked_files`
  directly -- only the shared/distinct DECLARATION is hand-authored. This is
  the closer precedent for HR9's derived-reference-set half (see 2.2 below).

All three: lazy `import yaml` inside the check function (never module-scope,
per Principle VIII / B1 / B3), read only `ctx.repo_root` + `ctx.tracked_files`,
open no DB, execute nothing, emit ERROR/WARNING findings only -- no numeric
score (hard rule #9).

### 1.2 The TMDL parsing surface (reused directly)

`src/retail/tmdl.py` (hand-rolled TMDL parser; decision recorded in
`docs/decisions/0001-tmdl-pbir-parser.md`) already provides everything HR9
needs to derive its TRUTH SET:

- `parse_tmdl(text) -> TmdlTable | None` -- `TmdlTable.columns` (each a
  `TmdlColumn.name`) and `TmdlTable.measures` (each a `TmdlMeasure.name` +
  `TmdlMeasure.expression`, the raw DAX body).
- `iter_model_files(ctx, ".tmdl") -> Iterable[tuple[rel_path, text]]` -- yields
  every non-test TMDL file under `*.SemanticModel/definition/`, already
  excluding `tests/` fixtures via `is_test_path`.

This is consumed today by `src/retail/rules/dax.py` (D1-D11, C1) exactly the
way HR9 will consume it: `for rel, text in iter_model_files(ctx, ".tmdl"):
table = parse_tmdl(text)`.

**One caveat found during this survey, to flag for the implementing stage
(Phase 2/tasks, not resolved here):** `dax.py`'s
`_strip_dax_comments_and_strings` helper strips `//` / `/* */` comments,
double-quoted strings, AND single-quoted `'Table Name'` identifiers (it
treats a single-quoted run as a delimiter-safety measure against a `/` inside
a table name, for D4). HR9's own reference-extraction needs the OPPOSITE
behavior for `'table'[column]` tokens: the single-quoted table name is the
signal it must capture, not strip. HR9 needs its own sibling stripping helper
(comments + double-quoted strings only) rather than reusing
`_strip_dax_comments_and_strings` as-is. This is implementation detail deferred
to the tasks stage; it does not change this feature's design or scope.

### 1.3 The metric-contract scan convention (reused directly)

`src/retail/rules/assumption_coherence.py` (AL2) already establishes the exact
glob + exclusion convention for iterating metric contracts:

```python
_METRICS_RE = re.compile(r"^mappings/[^/]+/metrics/[^/]+\.ya?ml$")
_TEMPLATE_PATH = "templates/metric-contract.yaml"
```

filtered against `ctx.tracked_files`, excluding the generic template and
`tests/` fixtures (`is_test_path`). HR9 reuses this exact pattern to find every
`binds_to.columns` reference (FR-003), and reuses `binds_to.gold_table`
resolution logic from the same module as the model for reading `binds_to`
safely (guard against a non-dict `binds_to`, a missing/placeholder
`gold_table`).

### 1.4 Committed filled-instance shapes confirmed by inspection

Read directly from `retail_store_sales` (the current worked example,
Principle VII -- cited, not copied):

- `mappings/retail_store_sales/metrics/TotalSales.yaml`:
  `binds_to: {gold_table: "gold.fct_sales_rss", columns: ["total_spent"]}`.
- `powerbi/RetailStoreSales.SemanticModel/definition/tables/gold fct_sales_rss.tmdl`:
  table header `table 'gold fct_sales_rss'`; measure
  `measure TotalSales = SUM('gold fct_sales_rss'[total_spent])`; a
  measure-to-measure reference `measure AvgTransactionValue = DIVIDE([TotalSales], ...)`.
- `mappings/retail_store_sales/design/visual-contract-binding-map.md`: a
  `semantic_model_field(s)` column with cells like `` `[TotalSales]` ``,
  `` `[TotalSales]` by `dim_date_rss[full_date]` (month) ``, and
  `` `[TransactionCount]` by `dim_customer_rss[customer_id]` (Top N) ``.

These three confirm: (a) `binds_to.gold_table`'s `schema.table` form
(`gold.fct_sales_rss`) maps to the TMDL table header's `schema table` form
(`'gold fct_sales_rss'`) by a dot-to-space substitution -- the same
normalization already implicit in how the worked example's own contract and
TMDL agree; (b) a binding-map cell mixes bracket-delimited exact tokens with
prose/qualifiers exactly as FR-005 / Q-BINDING-CELL-PARSE describes.

## 2. What HR9 stays distinct from (do not restate, do not extend)

- **HR1 -- conformed-dimension readiness** (spec 087, reserved id, **no rule
  source exists in this tree today** -- spec-only / in-flight). HR1 checks
  cross-STAR structural agreement (grain/key/type) on a dimension DECLARED
  conformed by a human, reading `source-map.yaml` `gold_star.dimensions[]`.
  HR9 checks a same-table reference-resolution question by reading TMDL. HR9
  does not read `conformed-dimension-map.yaml`; HR1 gains no reference-orphan
  check from this feature. Cited here as a design-precedent SIBLING (the
  "human-declares, rule-reads" manifest shape it *doesn't* need -- see 2.2),
  not as reusable code.
- **HR6** (referenced in the spec's FR-014 as a wiring precedent -- "mirrors the
  HR6 FR-017 precedent of keeping the gate doc's Blocking-reasons table and the
  rule's own registration in agreement"). Searched this tree: **HR6 has no rule
  source and no HR6 text outside specs 092/103/105**, which are themselves
  other in-flight specs, not shipped code. Treat "the HR6 FR-017 precedent" as
  a NAMING CONVENTION the spec author is pointing at (keep the gate doc and the
  registry in agreement whenever a new rule id lands), not a file to open or
  depend on. This plan does not cite HR6 as an existing artifact.
- **SF1** is named alongside DF1 in the feature's own collision-avoidance
  framing as a sibling reconcile rule, not a variant to extend; HR9 does not
  touch `docs/quality/shared-spine.yaml`.
- **Spec 099 (cross-table column-level lineage/impact)**: a descriptive,
  read-only generator that treats a missing hop as a GAP and defers
  fuzzy-name resolution to a human. HR9 is the prescriptive opposite (exact
  tokens only, orphan = ERROR). No shared code; the boundary is already
  spelled out in the spec's own "Boundary against neighbouring shipped work"
  section and is not re-litigated here.

### 2.1 The manifest-less departure (the one real divergence from precedent)

SC1, DF1, and SF1 each reconcile a **hand-curated** `docs/quality/*.yaml`
manifest against tracked-file evidence -- a human declares the claim/edge/
collision-intent, the rule only verifies it. HR9 introduces **no such
manifest**. Both of HR9's sets are DERIVED directly from already-committed
model artifacts:

- **Truth set** -- read straight from committed TMDL (`parse_tmdl` output).
- **Reference set** -- read straight from committed metric contracts (already
  scanned by AL2's convention), TMDL measure DAX bodies, and the committed
  binding-map file.

Nothing is hand-curated because there is nothing to declare: unlike a
prose-status claim or a fork-vs-intentional-difference call, "does this name
resolve" is a mechanical fact fully determined by the committed text itself.
This is precisely what the spec's collision-avoidance allocation means by "no
shared-schema addition" -- HR9 needs no new YAML shape, so it cannot itself rot
out of sync with the model it describes (a manifest-based rule's manifest CAN
drift from the model; a derived rule cannot, by construction).

### 2.2 Precedent for a derived (non-manifest) reference set

SF1 already derives its own reference set (the checklist file list) from
`ctx.tracked_files` via a glob + basename grouping, and only the
shared/distinct DISPOSITION is manifest-driven. HR9 takes that one step
further: neither the truth set nor the disposition needs a human declaration,
because referential resolution is not a judgment call, it is exact-token
lookup.

## 3. Input-source confirmation

| Input | Path pattern | Confirmed via |
|---|---|---|
| TMDL truth set (columns, measures, DAX bodies) | `powerbi/*.SemanticModel/definition/tables/*.tmdl` | `tmdl.py` + `iter_model_files`; real file `powerbi/RetailStoreSales.SemanticModel/definition/tables/gold fct_sales_rss.tmdl` |
| Metric contract references | `mappings/<table>/metrics/*.yaml` (`binds_to.columns`) | AL2's `_METRICS_RE`; real file `mappings/retail_store_sales/metrics/TotalSales.yaml` |
| Dashboard binding-map references | `mappings/<table>/design/visual-contract-binding-map.md` (`semantic_model_field(s)` column) | real file `mappings/retail_store_sales/design/visual-contract-binding-map.md` |
| Rule registration surface | `src/retail/rules/__init__.py` (import + `__all__`), `src/retail/registry.py` (`@register`) | inspected directly |
| Rule inventory / count lockstep | `docs/rules/rules-manifest.json` (generated), `tests/unit/test_rules_wiring.py` (`EXPECTED_RULE_IDS` frozenset, never a bare literal) | inspected directly |
| Gate-doc "Blocking reasons" listing | `docs/readiness/semantic-model-ready.md`, `docs/readiness/dashboard-ready.md` | inspected directly; both already list D1-D11/C1/R1/G6 by id |

No new manifest, no new shared-schema key, no new template. This satisfies
the collision-avoidance allocation's "reuses SC1/DF1 manifest pattern -- no
shared-schema addition" by reusing the CODE shape while explicitly needing
none of the manifest schema.

## 4. Deferred capabilities NOT assumed

This feature's design assumes NONE of the following exist, and does not
require them to exist for HR9 to be specified or later implemented:

- **F016 (Power BI execution adapter)** does not exist and is not assumed.
  HR9 never opens a live Power BI/PBIP connection, never executes DAX, never
  confirms the TMDL's claims against a running model -- that live cross-check
  is explicitly OUT OF SCOPE (spec Assumptions) and remains F016's deferred
  territory (Principle II, Principle VIII).
- **No live database surface** is assumed or required. HR9 is 100%
  static/committed-text (Principle VIII); a live DB surface, if ever added to
  a NEIGHBORING rule, would be a separate, explicitly marked-PENDING surface
  (per Principle VIII's live-deferred split) -- HR9 itself has no live half to
  defer, mark, or gate.
- **No hand-curated manifest** is assumed (see 2.1) -- this is a deliberate
  design choice, not a missing input.
- **HR1's `conformed-dimension-map.yaml`** is not assumed to exist or to ship
  before HR9; the two rules are independent and neither blocks the other.
- **No new readiness-computation code path** is assumed. FR-011's "surface HR9
  in `blocking_reasons[]`" is satisfied the same way D1-D11/C1 already are
  today: `retail check`'s finding stream plus the gate doc's Blocking-reasons
  listing (docs, not new code in `readiness_status.py`/RS1, which only checks
  the internal consistency of an already-authored `readiness-status.yaml`).
  Confirmed by reading `src/retail/rules/readiness_status.py`: RS1 verifies a
  `blocking_reasons[]` list is present/non-empty on a blocked stage; it does
  not compute which findings populate that list. No change to RS1 is implied
  or needed by this feature.
- **No auto-rename / auto-fix capability** is assumed or introduced (scope
  guard, FR-009): HR9 never suggests, applies, or infers a "correct" name.

## 5. Conclusion carried into Phase 1

HR9 is buildable entirely from already-shipped, already-committed pieces:
the `tmdl.py` parser, the SC1/DF1/SF1 reconcile-and-fail-closed shape, and
AL2's metrics-glob convention. The only new logic is (a) a comment/string
stripper that PRESERVES single-quoted table-qualifier tokens (unlike
`dax.py`'s existing stripper), (b) bracket-token extraction from a
binding-map cell, and (c) the dot-to-space `schema.table` <-> TMDL-table-name
normalization. None of this requires a new manifest, a new dependency, a live
surface, or F016.
