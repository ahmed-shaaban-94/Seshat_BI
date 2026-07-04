# Research: Row-Level Security as a Semantic-Model-Ready Dimension

**Feature**: 092-rls-access-readiness | **Date**: 2026-07-04 | **Phase**: 0

## Purpose

Confirm this feature reuses shipped SHAPES and shipped PARSING mechanisms
rather than inventing new ones, before any design decision in `plan.md` is
made. Every finding below cites a real, already-committed repo path.

## Precedent survey

### P1 -- Declare/bind/readiness contract shape: `templates/metric-contract.yaml` (F009)

`templates/metric-contract.yaml` already ships the exact three-part shape this
feature needs for a role contract: an `identity` block (`name`, owner), a
`binds_to` block (`gold_table` + `columns`, gold-only per Principle III), and a
`readiness` block using the four explicit statuses
(`not_started | blocked | warning | pass`) plus `evidence[]` and
`blocking_reasons[]` (no numeric score, per hard rule #9). A filled instance
lives at `mappings/retail_store_sales/metrics/TotalSales.yaml`.

**Decision**: `templates/rls-role-contract.yaml` REUSES this shape (identity +
a binding block + the same four-status readiness block) but is a **wholly
separate file** -- per the collision-avoidance allocation and FR-002, no key
is added to `metric-contract.yaml`. The binding block's field names differ in
meaning (a role's `filter: {gold_table, column}` restricts ROWS on a
DIMENSION; a metric's `binds_to: {gold_table, columns}` names which columns a
MEASURE reads) even though the surrounding shape rhymes.

### P2 -- Docs pointer for the store: `docs/metrics/metric-contract-store.md` (F009)

F009's authoring guide documents where filled contracts live
(`mappings/<table>/metrics/<MetricName>.yaml`) and how the store is reviewed.
No equivalent guide exists yet for role contracts.

**Decision**: this feature's plan does not require a new top-level store guide
doc (out of scope per FR-004's narrow ask: template + one rule). The template's
own header comments (mirroring `metric-contract.yaml`'s own header) carry the
authoring notes; `docs/readiness/semantic-model-ready.md` gets the FR-017
listing update. A dedicated store-guide doc is left as a follow-up, not
required by this spec's Functional Requirements.

### P3 -- Static rule shape + registration: `src/retail/rules/g6.py`, `src/retail/registry.py`

Every static rule is a pure function `RuleContext -> Iterable[Finding]`,
registered exactly once via `@register("ID", "description")`
(`src/retail/core.py`: `Rule = Callable[[RuleContext], Iterable[Finding]]`).
`g6.py` is the closest sibling: it scans committed text
(`*.SemanticModel/definition/expressions.tmdl`), applies a regex, and emits
`Finding(rule_id="G6", severity=Severity.ERROR, message=..., locator=...)` for
each violation, skipping `tests/` fixtures via `is_test_path()`.

**Decision**: HR6 follows the identical shape -- a pure function over
`ctx.tracked_files`, one `@register("HR6", "...")`, `Finding` objects with
`Severity.ERROR` for hard failures (never `Severity.WARNING`; see C1 in the
spec's Clarifications -- HR6 must fail CLOSED per Principle I, unlike S5/S6/S7
which are `WARNING`-tier ADR-default advisories, a different rule family this
feature must NOT mirror by analogy).

### P4 -- YAML parsing mechanism (resolves spec Clarification C2)

The static core is documented as "stdlib-only" in spirit (Principle VIII), but
`pyyaml>=6` is in fact an already-approved **runtime** dependency
(`pyproject.toml`, commented "pyyaml is a RUNTIME dependency: ~10 governance
rules... import yaml"). The existing pattern every YAML-reading rule follows
is a **lazy, function-scope** `import yaml` (never module-scope, which is what
B1 -- `src/retail/rules/never_execute.py` -- actually forbids: module-scope
DB/network-flavored execution imports, not YAML). The concrete precedent is
`src/retail/rules/readiness_status.py` (RS1):

```python
import yaml  # lazy: keep retail check import path stdlib-light
try:
    data = yaml.safe_load(raw)
except yaml.YAMLError as exc:
    findings.append(_finding(f"... is not valid YAML: {exc}", rel))
    continue
```

**Decision**: HR6 reads each `rls-role-contract.yaml` the same way -- read
text as `utf-8-sig`, lazy `import yaml` inside the rule function, `safe_load`,
catch `yaml.YAMLError` and `OSError`/`UnicodeDecodeError` as findings (never an
uncaught crash of the whole gate, matching RS1's and B1's "fail as a Finding,
not an exception" posture). No new dependency is added; B1 is unaffected
because the import stays inside the rule function, not at module scope.

### P5 -- Gold table/column existence from committed SQL (resolves spec Clarification C2/C3)

`src/retail/rules/sql.py` (S6/S8) already extracts `gold.dim_*` / `gold.fct_*`
table names from committed migration SQL via regex over noise-stripped text
(comments and string literals blanked, not removed structurally):

```python
_CREATE_GOLD_DIM = re.compile(
    r"\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?gold\.(dim_\w+)", re.IGNORECASE
)
```

and a `_strip_sql_noise()` helper that blanks comments/string literals while
preserving line counts (for locator accuracy) before the regex ever runs.
Column names for a given table are extractable the same way: the columns
listed inside that `CREATE TABLE gold.<table> ( ... )` parenthesized body.

**Decision**: HR6 reuses this exact family -- a regex over the same
noise-stripped text, extended to also capture `gold.fct_\w+` (needed for the
C1 fact-vs-dim mismatch check) and to capture each `CREATE TABLE`'s column
list (name up to the first whitespace/type token, one per comma-separated
line inside the parens). This is NOT a new parsing approach; it is the same
mechanism S6/S8 already use, applied to a second question (column existence +
table kind) instead of a first (unknown-member insert presence). No SQL
parser dependency is introduded; the committed migration SQL under
`warehouse/migrations/*.sql` remains the static source of truth (per the
spec's Assumptions), matching how F009's own `binds_to` column check is
implemented.

### P6 -- Dim-vs-fact classification: `docs/conventions.md`

The `dim_`/`fct_` prefix convention is already constitution-fixed and
repo-wide (`docs/conventions.md`: "Object prefixes: views `vw_`, fact tables
`fct_`, dimension tables `dim_`"). Clarification C3 in the spec already
settles that HR6 reuses this prefix rather than inventing a second
classification mechanism (e.g. a new metadata key). No further research
needed here; this is a direct convention read, not a design choice.

### P7 -- Stage-5 gate wiring: `.claude/skills/retail-semantic-check/`, `docs/readiness/semantic-model-ready.md`

`retail-semantic-check` (on-disk feature 011 / F010) is READ-ONLY and
invoke-and-interpret only: it runs `retail check` and reads the committed
metric-contract store; it does not special-case individual rule ids in its
own logic beyond running the checker and reading the exit code +
`FindingDict` list. `docs/readiness/semantic-model-ready.md`'s "Required
checks" table already lists `D1-D11, C1 (connection params), R1, G6` as the
`retail check` scope for this stage.

**Decision**: HR6 needs **no new code** in `retail-semantic-check` -- because
that skill already runs the full `retail check` rule set and inherits any new
`Severity.ERROR` finding's effect on the process exit code, wiring HR6 in is
a **documentation-only** edit (FR-017): add `HR6` to the "Required checks" and
"Blocking reasons" tables in `semantic-model-ready.md`, exactly the way `G6`
is already listed there. This is the same "adds one more input to the
existing verdict" posture the spec's Requirements (FR-011) describe, and
matches how G6 itself was wired in without touching the skill's own source.

### P8 -- Per-table co-location convention: ADR 0003, `mappings/<table>/`

ADR 0003 ("cohesive per-table working set") is why `metrics/<MetricName>.yaml`
lives under `mappings/<table>/metrics/`. The spec's Clarification C4 already
fixes that a role contract is co-located the same way, one-role-per-file,
discoverable by folder scan (so HR6's duplicate-name check, FR-009, can run
over every file under the folder without needing a manifest).

**Decision**: filled role contracts live under `mappings/<table>/` (a new
`roles/` subfolder, mirroring `metrics/`'s pattern:
`mappings/<table>/roles/<RoleName>.yaml`). HR6 discovers every such file via a
`tracked_files` path-suffix scan (`mappings/*/roles/*.yaml`), the same
discovery style RS1 uses for `mappings/*/readiness-status.yaml`. The literal
subfolder name (`roles/`) is an implementation naming choice fixed here at
plan time, not a Principle-V question (spec C4 explicitly defers only the
filename token, not the discoverability shape).

## Input-source confirmation

| Input this feature reads | Source | Already exists? |
|---|---|---|
| Role contract shape to mirror | `templates/metric-contract.yaml` | Yes (F009, shipped) |
| Rule registration mechanism | `src/retail/registry.py`, `src/retail/core.py` | Yes (shipped) |
| Sibling static-rule pattern | `src/retail/rules/g6.py` | Yes (shipped) |
| YAML-parsing pattern | `src/retail/rules/readiness_status.py` (RS1) | Yes (shipped) |
| Gold table/column existence source | `warehouse/migrations/000{3,4,5}_*.sql` (committed) | Yes (shipped, table-specific instance; the MECHANISM -- reading `warehouse/migrations/*.sql` -- generalizes to any future table) |
| Dim/fact naming convention | `docs/conventions.md` | Yes (shipped) |
| Stage-5 gate doc to update | `docs/readiness/semantic-model-ready.md` | Yes (shipped; FR-017 edits it) |
| Co-location convention | ADR 0003 (`docs/decisions/0003-*.md`), ADR usage in `mappings/retail_store_sales/metrics/` | Yes (shipped) |
| Severity enum | `src/retail/core.py` (`Severity.ERROR/WARNING/INFO`) | Yes (shipped) |

No input this feature needs is missing or requires new infrastructure. Every
artifact this plan proposes to touch or add already has a load-bearing sibling
in the repo to model itself on.

## Deferred capabilities NOT assumed (Principle VIII / scope guard)

This feature's design MUST NOT assume, simulate, or partially build any of the
following. Restated explicitly so `plan.md` and `tasks.md` cannot silently
smuggle one in:

- **No F016 (Power BI execution adapter).** HR6 never opens a PBIP file, never
  connects to Power BI Desktop or the Power BI service, never evaluates or
  previews a role filter ("view as role"). F016 does not exist in this repo
  and this feature does not assume any interface from it.
- **No live database connection.** HR6 verifies a column's EXISTENCE by
  reading committed migration SQL text, never by connecting to Postgres (or
  any engine) and querying `information_schema`. `retail validate` (the live
  surface) is untouched by this feature.
  A live check that a role's filter ACTUALLY restricts rows as intended is
  explicitly out of scope (FR-018) and is not stubbed, not TODO-commented as
  future code in this feature's rule module, and not given a placeholder CLI
  flag -- it simply does not appear.
- **No new readiness stage.** The seven stages (Source -> Mapping -> Silver ->
  Gold -> Semantic Model -> Dashboard -> Publish) are unchanged. HR6 is one
  more `retail check` rule folded into the EXISTING Semantic Model Ready
  (Stage 5) gate, not a new stage, and this feature adds no new `retail check`
  subcommand (spec Assumptions, final bullets).
- **No `templates/metric-contract.yaml` or `templates/kpi-pack.yaml` edit.**
  Per the collision-avoidance allocation, zero keys are added to either file
  (verified by SC-005).
- **No answer to Q-ZERO-ROLES.** Whether a table with zero committed role
  contracts should block, warn, or pass Semantic Model Ready is an OPEN
  Principle-V governance ruling (FR-010). This feature's design in `plan.md`
  and `data-model.md` MUST leave this question visibly open -- HR6's shipped
  behavior only fires findings for role contracts that DO exist and are
  malformed; it does not synthesize a finding, a pass, or a block for the
  zero-contract case as a final answer.
- **No numeric confidence/health/maturity score anywhere** (hard rule #9):
  not in the template, not in an HR6 finding message, not in any doc this
  feature edits.

## Open questions carried into plan.md

- Q-ZERO-ROLES (Principle-V; spec FR-010) -- carried forward unresolved into
  `plan.md`'s Constitution Check (Principle V) and `data-model.md`'s
  readiness-block notes. Not answered by this research or by any later phase
  of this feature.
