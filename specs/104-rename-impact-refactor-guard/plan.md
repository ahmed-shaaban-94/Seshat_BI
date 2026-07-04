# Implementation Plan: Rename/Impact Refactor-Safety Static Rule (HR9)

**Branch**: `104-rename-impact-refactor-guard` | **Date**: 2026-07-04 | **Spec**: `specs/104-rename-impact-refactor-guard/spec.md`

**Input**: Feature specification from `specs/104-rename-impact-refactor-guard/spec.md` (clarified 2026-07-04)

**Note**: This template is filled in by the `/speckit-plan` command. See
`.specify/templates/plan-template.md` for the execution workflow. This is a
GOVERNANCE/DOCS plan (a new static `retail check` rule), not an application
feature plan.

## Summary

Add a new static `retail check` rule, reserved id **HR9**, that extends the
shipped SC1/DF1/SF1 reconcile-and-fail-closed pattern to the Power BI model
surface. HR9 derives a TRUTH SET (currently-existing gold column names and
TMDL measure names) directly from committed TMDL under
`powerbi/*.SemanticModel/definition/tables/*.tmdl`, then resolves every
reference to a gold column or measure name found in (a) a metric contract's
`binds_to.columns`, (b) a TMDL measure's own DAX expression
(measure-to-measure and measure-to-column tokens), and (c) a dashboard
visual-contract binding map's `semantic_model_field(s)` cells, against that
truth set. A reference that does not resolve is an orphan -- the dangling
state a careless rename leaves behind -- and HR9 fails closed (ERROR), naming
the orphaned reference and the artifact that carries it. HR9 is
**manifest-less by design**: unlike SC1/DF1 (a hand-curated
`docs/quality/*.yaml` manifest), both of HR9's sets are derived directly from
already-committed model artifacts, so no new schema is introduced and nothing
can itself drift out of sync with the model it describes. HR9 never decides
which name is correct, never edits or renames anything, and never emits a
numeric score -- it names the break and stops, exactly as SC1/DF1/HR1 already
do for their own surfaces.

## Technical Context

**Language/Version**: Python 3.11+ (matches the existing `src/retail/` static
checker core; no new runtime).

**Primary Dependencies**: stdlib only (`re`, `pathlib`) for the rule's core
resolution logic, matching Principle VIII / B1 / B3. `yaml` (PyYAML) is
imported **lazily inside the check function** only where a committed metric
contract (`mappings/<table>/metrics/*.yaml`) is parsed -- the same posture
SC1/DF1/SF1/AL2 already use, keeping the `retail check` static core's
module-scope import list dependency-free.

**Storage**: N/A. HR9 reads committed text (`ctx.repo_root` + `ctx.tracked_files`)
only; no database, no cache, no generated artifact beyond `Finding` objects.

**Testing**: `pytest`, following the existing `tests/unit/test_rule_*.py` /
`tests/unit/test_rules_wiring.py` conventions; a new golden-fixture pair under
`tests/fixtures/` (a clean TMDL+contract+binding-map trio and a planted-orphan
variant) mirroring the pattern already used for D1-D11 (`tests/fixtures/golden_pbip/`).
Deferred to the tasks stage (Phase 2), not authored here.

**Target Platform**: Same as the existing checker -- runs in CI and locally on
Windows/Linux via `retail check`; no platform-specific code.

**Project Type**: Single project (existing `src/retail/` static-checker
library + CLI). No frontend/backend split; Option 1 from the plan template.

**Performance Goals**: N/A (a linear scan over committed TMDL/YAML/Markdown
files; the checker already scans the full tree per `retail check` invocation
at this scale -- no new performance category).

**Constraints**: Fails CLOSED, never merely advises (Principle I). Reads
committed text only -- no DB, no execution, no live Power BI/PBIP surface
(Principle VIII). Emits no numeric confidence/health/maturity/completeness
score (hard rule #9). Generic: no worked-example (C086/pharmacy/
retail_store_sales) domain specific may be hardcoded into the rule's own
source (Principle VII, FR-013).

**Scale/Scope**: One new rule module, its registration wiring, two doc edits,
and its tests -- scoped identically to how SF1 (spec 086) and AL2 landed
(one rule, one registration diff, one doc-table edit each).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design below.*

| Principle | How HR9's design satisfies it |
|---|---|
| **I. Agent-First, Gate-Enforced** | HR9 registers under `@register("HR9", ...)` exactly like every other rule; a finding is `Severity.ERROR`, which fails `retail check`'s exit code (non-zero), not a WARNING an agent could rationalize past. Compliance is demonstrable by running `retail check` over the committed tree -- no separate prose claim of correctness is accepted. |
| **III. Medallion/Gold-Only** | HR9 reads ONLY the `gold`-schema TMDL model surface (`powerbi/*.SemanticModel/definition/tables/*.tmdl`) and artifacts that reference it (metric contracts bound to `gold_table`, binding-map cells naming gold measures/dim columns). It does not read `silver`/`bronze`, does not touch `source-map.yaml`'s star declarations (that is HR1's territory), and adds no new fact/dimension shape -- gold's Kimball-star shape is unchanged. |
| **IV. Source-Mapping-Before-Silver** | HR9 writes no `silver.*` SQL and gates nothing about the mapping stage; it operates strictly downstream, at Semantic Model Ready / Dashboard Ready, on artifacts that already presuppose an approved map. This principle is not implicated by HR9's scope; it is neither strengthened nor weakened. |
| **V. Agent-Stops-at-Judgment** | HR9 itself makes no judgment call -- "does this reference resolve" is a mechanical fact, not a business/PII/grain/approval decision, so the rule may compute it directly (this is the same posture SC1/DF1 already take on their own reconcile questions). The ONE genuine Principle-V question the spec surfaces -- Q-APPROVAL-SEAM (does a clean HR9 run need its own new named-human approval seam, FR-016) -- is explicitly left OPEN for an owner ruling and is NOT decided by this plan; FR-016's RECORDED PENDING DEFAULT (MECHANICAL, no new approval seam) stays PENDING, not promoted to adopted. This plan raises the item; it does not close it. |
| **VI. Defaults-Then-Deviations** | HR9's non-Principle-V ambiguities (case-insensitive name resolution; bracket-token-only extraction from a binding-map cell) were resolved as reasonable, reversible constitution-safe defaults during Clarifications (Q-CASE-SENSITIVITY, Q-BINDING-CELL-PARSE) and are recorded in the spec, not re-litigated here. |
| **VII. C086-Is-An-Example** | HR9's own rule source (module docstring + implementation) MUST cite no worked-example-specific table/column/measure name; `retail_store_sales` is used in `research.md` and in this plan ONLY as an inspected, cited filled instance to confirm the concrete artifact shapes (per FR-013 / SC-004). The rule logic itself is fully generic: it reads whatever TMDL/YAML/Markdown the committed tree contains. |
| **VIII. Static-First/Live-Deferred** | HR9 is 100% static: it never opens a database connection, never runs DAX, never opens a live Power BI/PBIP surface. There is no live half of HR9 to defer or mark PENDING -- unlike `retail validate`'s live checks, HR9 has no live counterpart by design (referential-integrity-against-committed-text is not a category that has a "live" analogue the way PK-uniqueness-on-materialized-rows does). F016 (the execution adapter) is correctly treated as non-existent; HR9 does not call it, wait on it, or reference its API. |
| **IX. Secrets/Reproducibility** | HR9 introduces no connection string, no DSN, no credential of any kind -- it is a pure text-reconciliation rule. Nothing in its design touches `.env` or any secret surface. |
| **Hard rule #9 (no fabricated score)** | HR9's finding is binary: a reference resolves (no finding) or it does not (one ERROR finding). No confidence/health/maturity/completeness number is computed, stored, or surfaced anywhere in this design (FR-012). |

**Result**: PASS. No principle requires a justified deviation; Complexity
Tracking below is empty by design.

## Project Structure

### Documentation (this feature)

```text
specs/104-rename-impact-refactor-guard/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
└── tasks.md              # Phase 2 output (/speckit-tasks command -- NOT created by this stage)
```

No `contracts/` subdirectory: HR9 is a static rule with no request/response
API surface (N/A for this feature shape, matching how SF1/AL2/HR1's own plans
have no `contracts/` either).

### Source Code (repository root)

**Structure Decision**: Single project (Option 1) -- this feature extends the
existing `src/retail/` static-checker library in place. No new top-level
directory, no new package, no frontend/backend split. Real repo paths this
feature touches (author-and-stop scope for the PLAN stage; the tasks stage
authors the actual diffs):

```text
src/retail/
├── rules/
│   ├── __init__.py                 # EDIT: add `rename_impact` (or similar) to the
│   │                                #   side-effecting import list AND __all__
│   ├── rename_impact_guard.py      # NEW: HR9 rule module (@register("HR9", ...))
│   │                                #   - derives the truth set via tmdl.parse_tmdl /
│   │                                #     tmdl.iter_model_files (reused, no changes)
│   │                                #   - derives the metric-contract reference set via
│   │                                #     the AL2 _METRICS_RE glob convention (reused
│   │                                #     pattern, own module-local copy or a shared
│   │                                #     helper -- a tasks-stage decision)
│   │                                #   - derives the DAX cross-reference set via a NEW
│   │                                #     sibling stripping helper that preserves
│   │                                #     single-quoted 'table' tokens (dax.py's
│   │                                #     `_strip_dax_comments_and_strings` cannot be
│   │                                #     reused as-is -- see research.md Sec 1.2)
│   │                                #   - derives the binding-map reference set by
│   │                                #     reading the committed binding-map Markdown
│   │                                #     and extracting bracket-delimited tokens only
│   ├── assumption_coherence.py     # REFERENCE ONLY (AL2): metrics-glob convention
│   ├── dax.py                      # REFERENCE ONLY (D1-D11/C1): iter_model_files usage
│   ├── status_claims.py            # REFERENCE ONLY (SC1): reconcile-and-fail-closed shape
│   └── parked_on.py                # REFERENCE ONLY (DF1): reconcile-and-fail-closed shape
├── tmdl.py                          # REUSED UNCHANGED: parse_tmdl, iter_model_files
├── core.py                          # REUSED UNCHANGED: Finding, RuleContext, Severity, is_test_path
└── registry.py                      # REUSED UNCHANGED: @register

docs/
├── rules/
│   └── rules-manifest.json          # REGENERATE (via `retail manifest`) to add HR9's
│                                     #   {"id": "HR9", "title": "..."} entry -- never
│                                     #   hand-edited (FR-015)
└── readiness/
    ├── semantic-model-ready.md      # EDIT: "Blocking reasons" table gains an HR9 line
    │                                 #   (mirrors the existing "A retail check D1-D11
    │                                 #   DAX/TMDL finding" bullet's shape)
    └── dashboard-ready.md           # EDIT: "Blocking reasons" table gains an HR9 line,
                                      #   scoped to the binding-map-orphan case only
                                      #   (FR-014, FR-011)

tests/
├── unit/
│   ├── test_rules_wiring.py         # EDIT: EXPECTED_RULE_IDS frozenset gains "HR9"
│   │                                 #   (FR-015; the count is derived from this set's
│   │                                 #   len(), never a bare literal)
│   └── test_rename_impact_guard.py  # NEW: unit tests for HR9 (clean run, orphan column
│                                     #   ref, orphan measure-to-measure ref, orphan
│                                     #   binding-map ref, table-qualified vs unqualified
│                                     #   scoping, case-insensitive match, no-TMDL no-op)
└── fixtures/
    └── (a small planted-orphan TMDL + contract + binding-map trio, generic
        names only -- NOT retail_store_sales/C086 specifics per FR-013/VII)
```

No changes to `mappings/`, `powerbi/`, `warehouse/`, `templates/`, or any
`skills/` directory -- HR9 reads those trees, it does not add to them. No new
`docs/quality/*.yaml` manifest (see research.md Sec 2.1 -- this is the
deliberate manifest-less departure from the SC1/DF1 precedent, satisfying the
collision-avoidance allocation's "no shared-schema addition").

## Complexity Tracking

*No entries.* The Constitution Check above found no principle requiring a
justified deviation; HR9's design fits entirely within the existing
static-rule shape (one module, one registration, two doc edits, one test
file) with no new dependency, no new manifest schema, and no new gate
category.
