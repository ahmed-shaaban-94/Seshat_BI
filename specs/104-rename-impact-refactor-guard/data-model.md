# Phase 1 Data Model: Rename/Impact Refactor-Safety Static Rule (HR9)

**Feature**: `104-rename-impact-refactor-guard` | **Date**: 2026-07-04

## Purpose

HR9 introduces **no new persisted schema** (no new manifest YAML, no new
template, no new key on an existing artifact -- research.md Sec 2.1/2.2). This
document instead describes the KEY ENTITIES / in-memory shapes the rule's
logic reasons over while it runs, all of them DERIVED at check-time from
already-committed artifacts. Every shape below is generic (Principle VII):
field names, not table/column/measure examples from any one worked instance.

## Entity 1: Truth Set

The currently-existing gold column names and TMDL measure names for one
table's model, derived by reading that table's committed TMDL file(s).

```text
TruthSet (per TMDL model file, keyed by repo-relative path):
  table_name: str            # from TmdlTable.name, e.g. "gold <table>"
  columns: set[str]          # lowercased TmdlColumn.name values (case-insensitive
                              #   resolution per Q-CASE-SENSITIVITY)
  measures: set[str]         # lowercased TmdlMeasure.name values declared in THIS
                              #   file. Resolution of an unqualified [Measure]
                              #   reference is NOT limited to one file's own set --
                              #   per FR-006 / Q-MEASURE-SCOPE it uses the UNION of
                              #   every TMDL table file's `measures` set that shares
                              #   the same `*.SemanticModel/definition/` FOLDER
                              #   (Power BI measures are model-scoped, not
                              #   table-scoped or file-scoped; see the Scope
                              #   discipline bullet below and Entity 3 step 1)
```

- **Source**: `tmdl.parse_tmdl(text) -> TmdlTable | None`, called once per file
  yielded by `tmdl.iter_model_files(ctx, ".tmdl")`.
- **Scope discipline (FR-006, FR-007)**: a table-qualified reference
  (`'table'[column]`) resolves ONLY within that table's own `TruthSet.columns`;
  an unqualified measure reference (`[Measure]`) resolves within the union of
  `TruthSet.measures` across every TMDL table file that shares the same
  `*.SemanticModel/` model folder (Power BI measures are model-scoped, not
  table-scoped). A table with zero committed TMDL files contributes no
  `TruthSet` entry at all -- HR9 emits nothing for it (US3, FR-007).
- **Never derived from**: a hand-curated manifest, migration SQL, or a live
  Power BI/DB connection (spec Assumptions; Principle VIII).

## Entity 2: Reference Set

Every gold-column or measure-name reference found in a metric contract's
`binds_to.columns`, a TMDL measure's own DAX expression, or a dashboard
visual-contract binding map's `semantic_model_field(s)` column.

```text
Reference:
  kind: "contract-column" | "dax-cross-ref" | "binding-map"
  token: str                 # the raw name/token as written (before case-fold)
  qualifier: str | None      # the table name for a 'table'[column] token, the
                              #   dim name for a dim[column] binding-map token,
                              #   or None for an unqualified [Measure] token
  is_bracket_measure: bool   # True for a [Measure]-shaped token, False for a
                              #   [table/dim][column]-shaped token
  source_file: str           # repo-relative path of the artifact carrying it
  locator_detail: str        # measure name / visual row id / contract field,
                              #   whatever anchors the finding message precisely
```

Three sub-shapes, one per FR:

### 2a. Contract-column reference (FR-003)

- **Source**: every tracked file matching `mappings/[^/]+/metrics/[^/]+\.ya?ml`
  (AL2's `_METRICS_RE` convention), excluding `templates/metric-contract.yaml`
  and `tests/` paths.
- **Extraction**: for each entry in `binds_to.columns` (a list of plain column
  name strings), emit one `Reference(kind="contract-column", token=<entry>,
  qualifier=<binds_to.gold_table's table part>, is_bracket_measure=False,
  source_file=<contract path>, locator_detail=<contract name>)`.
- **Engagement independent of approval state (FR-008)**: extracted regardless
  of the contract's own `readiness.status` value.
- **Malformed contract handling**: a `binds_to` that is not a mapping, or a
  `gold_table` that is missing/a placeholder (`<...>`), yields no reference
  from that contract for HR9 purposes -- consistent with AL2's own
  `_group_key` exclusion, since HR9 has nothing to resolve a placeholder
  against; this is not itself an HR9 finding (a different, already-existing
  rule owns placeholder hygiene).

### 2b. DAX cross-reference (FR-004)

- **Source**: every `TmdlMeasure.expression` from every parsed TMDL table in
  scope (`iter_model_files` + `parse_tmdl`, same traversal as Entity 1).
- **Extraction**: after stripping comments (`//`, `/* */`) and double-quoted
  string literals ONLY (a new sibling helper -- NOT `dax.py`'s
  `_strip_dax_comments_and_strings`, which also strips single-quoted table
  identifiers HR9 needs to keep -- research.md Sec 1.2), scan for two token
  shapes:
  - `[MeasureName]` -- an unqualified bracket token -> `Reference(kind=
    "dax-cross-ref", token="MeasureName", qualifier=None,
    is_bracket_measure=True, ...)`.
  - `'Table Name'[ColumnName]` -- a table-qualified token -> `Reference(kind=
    "dax-cross-ref", token="ColumnName", qualifier="Table Name",
    is_bracket_measure=False, ...)`.
- **Disambiguation assumption (stated explicitly, not inferred)**: DAX/TMDL
  practice -- and every committed measure in the worked instance -- always
  table-qualifies a COLUMN reference (`'gold fct_sales_rss'[total_spent]`)
  and never table-qualifies a MEASURE reference (`[TotalSales]`, bare).
  Extraction therefore tags every unqualified bracket token as a candidate
  MEASURE reference (`is_bracket_measure=True`) and every qualified token as
  a candidate COLUMN reference (`is_bracket_measure=False`) -- it does not
  attempt to distinguish an unqualified column reference from a measure
  reference by any other means, because DAX has no such form in practice on
  this model. If a future model introduces an unqualified column reference,
  HR9 would misclassify it as a measure lookup and could false-positive;
  this is a known, explicitly documented limitation carried forward to the
  tasks stage, not a silent gap.
- `locator_detail` names the REFERENCING measure (the measure whose body the
  token was found in), so a finding can say "measure X references stale token
  Y".

### 2c. Binding-map reference (FR-005)

- **Source**: the committed dashboard visual-contract binding map (e.g.
  `mappings/<table>/design/visual-contract-binding-map.md` or an equivalent
  committed binding artifact the spec's Assumptions name generically) --
  specifically its `semantic_model_field(s)` table column, one cell per
  visual row.
- **Extraction (Q-BINDING-CELL-PARSE)**: from each cell's raw text, extract
  ONLY bracket-delimited tokens matching `` `[Measure]` `` or
  `` `dim[column]` `` shapes; ignore all surrounding prose, the grouping word
  "by", and parenthetical qualifiers like `(Top N)` / `(month)`. No fuzzy or
  prose matching is attempted -- a cell that names zero bracket tokens
  contributes zero references (not a finding). Each extracted token becomes a
  `Reference(kind="binding-map", ...)` with `qualifier` set to the dim name
  for a `dim[column]` token, or `None` for a bare `[Measure]` token.
- `locator_detail` names the `visual_id` (the row) the cell belongs to.

## Entity 3: Orphaned Reference

A member of the Reference Set that does not resolve against the Truth Set --
the dangling state a rename leaves behind when only one side is updated.

```text
OrphanedReference:
  reference: Reference        # the unresolved Reference (Entity 2)
  resolved_against: str       # which TruthSet (by model-file path) it was
                               #   checked against, for the finding message
  reason: str                 # human-readable: "no column named X in table Y's
                               #   current TMDL" / "no measure named X in this
                               #   model" / etc.
```

**Resolution algorithm (case-insensitive, Q-CASE-SENSITIVITY):**

0. **Locate the governing model first.** Every reference must be resolved
   against a specific `*.SemanticModel/` folder before path 1 or 2 can run.
   For a `dax-cross-ref` (Entity 2b), the governing model is the one the
   referencing TMDL file itself lives in (trivial -- same folder). For a
   `contract-column` (Entity 2a) or `binding-map` (Entity 2c) reference, the
   `mappings/<table>/` artifact does not itself live inside a
   `*.SemanticModel/` folder, so the governing model is read from the
   artifact's own committed pointer: a binding map states it explicitly
   (`governed_model: ../../../powerbi/<Model>.SemanticModel`, confirmed in
   the inspected worked instance); a metric contract's `binds_to.gold_table`
   identifies its table, and that table's TMDL file's OWN
   `*.SemanticModel/` folder is the governing model transitively. No
   reference is resolved without first pinning down which model folder's
   `TruthSet`(s) it is checked against -- this is what keeps FR-006's
   cross-model isolation guarantee real rather than aspirational.
1. If `reference.is_bracket_measure` and `reference.qualifier is None`:
   case-fold `reference.token` and look it up in the UNION of
   `TruthSet.measures` across all TMDL table files inside the governing model
   folder located in step 0. No match -> orphan.
2. If `reference.qualifier is not None` (a `'table'[column]` or
   `dim[column]` token): resolve `qualifier` to a specific TMDL table WITHIN
   the governing model folder located in step 0, trying BOTH forms so a
   reference written either way resolves (Entity 4):
   (a) an EXACT match against `TmdlTable.name` (handles a
   `binds_to.gold_table`-style `schema.table` reference, dot-to-space
   normalized -- `gold.fct_sales_rss` -> `gold fct_sales_rss`); or
   (b) a match against `TmdlTable.name` with its leading `<schema> ` word
   stripped (handles a BARE table/dim identifier with no schema prefix --
   `dim_product_rss` matching TMDL table `gold dim_product_rss`, exactly the
   form the inspected worked instance's binding map actually uses:
   `` dim_product_rss[category] ``, `` dim_date_rss[full_date] ``,
   `` dim_customer_rss[customer_id] ``). If NEITHER form matches any TMDL
   table in the governing model, the qualifier itself is unresolved -> orphan
   (naming the qualifier, not a column). If the qualifier resolves, case-fold
   `reference.token` and look it up in that TABLE's own `TruthSet.columns`
   ONLY (FR-006 -- never a different table's columns, even if same-named). No
   match on the column within it -> orphan.
3. A contract-column reference (`kind="contract-column"`) always carries an
   implicit qualifier (`binds_to.gold_table`); it follows path 2 form (a),
   not path 1.

Each `OrphanedReference` produces exactly one `Finding`:

```text
Finding(
    rule_id="HR9",
    severity=Severity.ERROR,
    message="<artifact/measure/visual> references '<token>', which does not "
            "resolve against <table/model>'s current committed TMDL "
            "(<reason>)",
    locator="<source_file>:<locator_detail>",
)
```

## Entity 4: Table-Qualifier <-> TMDL-Table-Name Normalization

Not a persisted entity -- a pure function needed to bridge TWO DIFFERENT
qualifier forms found in committed artifacts to Entity 1's `TmdlTable.name`
(schema-prefixed, e.g. `"gold fct_sales_rss"` / `"gold dim_product_rss"` --
confirmed by direct inspection of the committed worked instance's TMDL
headers `table 'gold fct_sales_rss'` and file `gold dim_product_rss.tmdl`).
Both forms are real and both are needed -- inspection of the worked instance's
OWN committed artifacts shows each form used by a different artifact family:

1. **Dotted `schema.table` form** -- how a metric contract's
   `binds_to.gold_table` names its table (`"gold.fct_sales_rss"`). Bridged by
   a dot-to-space substitution: `"gold.fct_sales_rss"` -> `"gold fct_sales_rss"`,
   an EXACT match against `TmdlTable.name`.
2. **Bare identifier form** -- how the binding map's `semantic_model_field(s)`
   cells qualify a dimension column with NO schema prefix at all
   (`` dim_product_rss[category] ``, `` dim_date_rss[full_date] ``,
   `` dim_customer_rss[customer_id] `` -- all confirmed present in the
   inspected worked instance, rows v05-v10). Bridged by stripping the leading
   `<schema> ` word (whatever it is, generically -- Principle VII) from
   `TmdlTable.name` and comparing what remains: `"gold dim_product_rss"`
   minus its leading schema word is `"dim_product_rss"`, which then matches
   the bare qualifier exactly.

```text
normalize_qualifier(qualifier: str, tmdl_table_names: Iterable[str]) -> str | None:
    # Try form 1 first: dot -> space, exact match against tmdl_table_names.
    # Fall back to form 2: for each candidate TMDL table name, strip its
    # leading "<word> " (the schema segment) and compare the remainder
    # against the bare qualifier. Returns the matched TmdlTable.name, or
    # None if neither form resolves (an orphaned qualifier itself).
    # No hardcoded schema/table name (Principle VII) -- "gold" is read as
    # whatever leading word each TMDL table name actually carries, not
    # assumed. Comparison is otherwise exact except for the case-insensitive
    # fold already applied to column/measure names (Q-CASE-SENSITIVITY);
    # the same fold is applied here for consistency.
```

Without both forms, HR9 would fire a false-positive orphan on every dim
column reference in the currently committed, already-approved binding map
(the bare form is the ONLY form that binding map uses for dimension
qualifiers) -- which would contradict this feature's own zero-findings
green-baseline expectation (quickstart Sec 6; research.md Sec 5) and SC-005's
sibling "no premature engagement" spirit. Pinning both forms here is what
keeps that baseline claim true once HR9 is implemented.

## Entity 5: HR9 Finding (Key Entity, spec-named)

Already defined by the spec's own "Key Entities" section; restated here as
the terminal output shape, using the repo's existing `Finding` dataclass
(`src/retail/core.py`) with no new fields:

```text
Finding.rule_id      = "HR9"
Finding.severity     = Severity.ERROR   # always ERROR -- HR9 has no WARNING
                                          # tier; a reference either resolves
                                          # or it is a genuine orphan (binary,
                                          # hard rule #9 posture)
Finding.message       = <see Entity 3>
Finding.locator       = "<repo-relative path>:<detail>"
```

## Entity 6: Semantic Model Ready / Dashboard Ready Blocking Reason (HR9-sourced)

Already defined by the spec's own "Key Entities" section. No new field is
added to `readiness-status.yaml`'s existing `blocking_reasons: list[str]`
shape (validated for internal consistency by RS1, `readiness_status.py`) --
an HR9 finding is transcribed into that list the same way a D1-D11/C1 finding
already is, by whoever authors the readiness record from a `retail check`
run. This feature adds no code to `readiness_status.py`.

## Non-entities (explicitly out of scope, for clarity)

- **No `HR9RuleConfig` / settings object** -- the rule takes only `RuleContext`
  (repo_root, tracked_files), exactly like every other rule in `src/retail/rules/`.
- **No cache / memoization entity** -- each `retail check` invocation re-parses
  the tree; no persisted intermediate state crosses runs.
- **No confidence/score field anywhere in this model** (hard rule #9) --
  Entity 3/5's only severity value is `ERROR`; there is no numeric field to
  compute or store.
