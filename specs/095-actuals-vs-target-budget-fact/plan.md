# Implementation Plan: Actuals-vs-Target (Budget) Fact + Variance Readiness

**Branch**: `095-actuals-vs-target-budget-fact` | **Date**: 2026-07-04 | **Spec**: `specs/095-actuals-vs-target-budget-fact/spec.md`

**Input**: Feature specification from `specs/095-actuals-vs-target-budget-fact/spec.md`

**Note**: This plan is docs-only, per the SCOPE GUARD and the collision-avoidance
allocation. It plans a documentation/template deliverable (a modelling pattern,
a filled contract-shape instance, and a second worked-example narrative
section), not a runtime feature. There is no application code, no SQL, no
`retail check` rule, and no new readiness stage to design.

## Summary

The primary requirement is to close a structural modelling gap named in
`skills/retail-kpi-knowledge/domains/targets-and-budgets.md`: no target/budget
fact has ever been modelled in this kit, so the actual-vs-plan (RAG) variance
view -- a core retail executive question -- is unmodellable. This feature closes
the gap as a PATTERN, not a shipped table (SCOPE GUARD: no target VALUES). The
technical approach (research.md) is: cite and extend three already-shipped
surfaces -- the domain doc's own named ambiguities, the F009 `metric-contract.yaml`
field set, and the `retail-store-sales.md` / `0004_*.sql` committed actuals
star -- to author three new artifacts at the paths the spec's Clarifications
already resolved:

1. `docs/patterns/target-budget-fact.md` -- the modelling pattern (conformance,
   grain-is-owner-supplied, non-additive variance calculation, missing-target
   flagging, comparison-at-coarser-grain).
2. `templates/metric-contract-shape.variance-vs-target.yaml` -- a filled
   pattern of `templates/metric-contract.yaml`'s EXACT field set applied to a
   variance metric, with the two-table `binds_to` tension resolved as an
   explicit open note (research.md Sec 5), not a new field.
3. `docs/worked-examples/target-budget-pattern-retail-store-sales.md` -- the
   second worked-example narrative (Principle VII genericity proof), applying
   the pattern to `retail_store_sales`'s existing conformed dimensions with
   zero fabricated target data.

Every open judgment call (target-fact grain, RAG thresholds, versioning/
reforecast handling) stays an explicit, named, OPEN `[NEEDS CLARIFICATION]`
marker per Principle V -- this plan does not resolve them, and no later stage
of this feature may resolve them either (they are per-table owner decisions
made when a REAL target fact is eventually onboarded).

## Technical Context

**Language/Version**: N/A -- documentation and YAML only (no code produced or
modified).

**Primary Dependencies**: None new. Cites existing repo artifacts only:
`templates/metric-contract.yaml` (F009), `docs/worked-examples/
retail-store-sales.md`, `warehouse/migrations/
0004_create_gold_retail_store_sales_star.sql`, `skills/retail-kpi-knowledge/
domains/targets-and-budgets.md`, `docs/decisions/
0002-retail-cleaning-defaults.md` (RC14), `.specify/memory/constitution.md`.

**Storage**: N/A. No database, no migration, no live connection is produced or
assumed by this feature. There is no target/budget data anywhere in the repo
and none is added.

**Testing**: N/A for this feature's own deliverable (it is prose + a YAML
instance). Validation of this spec chain is: (a) a manual field-set diff of
the contract shape against `templates/metric-contract.yaml` confirming 0
new/renamed keys (SC-005); (b) a manual name-check of every dimension/table
name in the second worked example against `0004_create_gold_retail_store_sales_star.sql`
and `retail-store-sales.md` confirming 0 invented names (SC-006); (c) a
read-only `retail check` dry run over the new files (ASCII/UTF-8-no-BOM,
secret-pattern, YAML-validity checks) reported with its exact exit code -- no
mutation, no live DB.

**Target Platform**: N/A -- Markdown/YAML documentation, consumed by a future
analyst or agent authoring a real target/budget table.

**Project Type**: Documentation / pattern-and-template (Spec-Kit "docs-first"
slice, matching the precedent of `specs/084-worked-example-factory/`, which
also shipped as docs-only with "Readiness stages affected: None").

**Performance Goals**: N/A.

**Constraints**: MUST NOT invent target VALUES, variance percentages, or RAG
colors/thresholds anywhere (Principle V; SCOPE GUARD; FR-010). MUST NOT edit
`docs/worked-examples/retail-store-sales.md`, `templates/metric-contract.yaml`,
or `skills/retail-kpi-knowledge/domains/targets-and-budgets.md` (FR-015). MUST
NOT add a new readiness stage, four-status gate, or `retail check` rule ID
(FR-014; collision-avoidance allocation). MUST NOT author any live DB
connection, migration SQL, or execution code (FR-018). MUST stay ASCII,
UTF-8 without BOM, with short repo-relative paths (FR-017; Principle IX).

**Scale/Scope**: One feature's worth of documentation and one YAML template
instance: the four `specs/095-actuals-vs-target-budget-fact/` chain files
(this plan's own deliverable), plus three implementation-stage deliverables
at the paths the spec's Clarifications already fixed (see Project Structure).
No other directory is touched.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Check | Result |
|---|---|---|
| I. Agent-First, Gate-Enforced | Does this feature add, weaken, or bypass a gate? | No new gate; no gate weakened. This feature adds a pattern doc and a contract-shape instance that a future analyst reads before using the EXISTING gates (`retail check`, the source-mapping gate, Semantic Model Ready). Compliance remains demonstrable by running `retail check` over the new files (ASCII/secret/YAML-validity checks apply to them like any committed text). PASS. |
| II. Depend, Never Fork | Does this feature touch the Power BI execution adapter, or fork a dependency? | No. F016 is explicitly not assumed reachable (research.md Sec 4); no adapter is referenced beyond citing that it does not exist yet. PASS (N/A in substance). |
| III. Medallion, Postgres-First, Gold-Only | Does this feature propose a new storage substrate, or a binding to silver/bronze? | No new substrate. The pattern document's core claim is that gold MUST stay a Kimball star: the (hypothetical) target fact conforms to the SAME dimension keys as an existing actuals gold star, and the contract shape's `binds_to.gold_table` names a `gold.*` table only, exactly like `metric-contract.yaml` already requires. PASS. |
| IV. Source Mapping Before Silver | Does this feature let silver be written before a source is mapped? | No silver SQL is authored at all (FR-018). The pattern document explicitly states that a real target-fact build restarts at Mapping Ready for the NEW target source (FR-013) -- it does not let a future reader skip the gate. PASS. |
| V. Agent Stops at Judgment Calls | Does this feature let the agent decide grain, RAG thresholds, versioning, or self-grant an approval? | No -- this is the feature's central discipline. Target-fact grain (FR-002), RAG thresholds (FR-009), and versioning/reforecast handling (Edge Cases) are each explicitly left as OPEN `[NEEDS CLARIFICATION]` markers, not resolved defaults. The spec's own Clarifications session recorded all three as "OPEN owner ruling... NOT answered here." No `approvals[]` entry, no readiness `pass`, and no confidence score is authored for any real table. PASS. |
| VI. Defaults Then Deviations | Does this feature bypass the defaults-then-deviations discipline, or invent a new default without a triggering data fact? | No new RC default is proposed. FR-019 requires the pattern document and the contract shape to explicitly separate already-resolved structural defaults (conformed dims, non-additive variance calculation, missing-target-must-flag) from open Principle-V judgment calls (grain, RAG, versioning) -- reinforcing, not bypassing, the same adopted-vs-open discipline `assumptions.md` already uses. PASS. |
| VII. C086 Is An Example, Not The Schema | Does this feature bake worked-example specifics into a generic template, or fail the two-example genericity bar? | The pattern document and contract shape stay generic (no table-specific grain, no table-specific column names baked in). The second worked-example narrative (FR-011) is the SECOND data point the principle itself calls for -- it grounds the pattern against `retail_store_sales`'s existing, committed dimension names without editing the first example or restating its answers. PASS. |
| VIII. Static-First Governance, Live Deferred | Does this feature claim a live-validation result it did not run, or blur static vs. live? | No live surface is touched at all (research.md Sec 4) -- there is nothing to mark `[PENDING LIVE PROFILE]` because no live connection, query, or profiling happens anywhere in this feature. The only deferred markers used are Principle-V `[NEEDS CLARIFICATION]` business-policy markers, which this plan is careful not to conflate with a live-data deferral. PASS. |
| IX. Secrets and Reproducibility | Does this feature commit a secret, a real connection string, or an over-long path? | No secret, no host, no DSN anywhere (there is no live surface to connect to). All three deliverable paths are short and ASCII (`docs/patterns/target-budget-fact.md`, `templates/metric-contract-shape.variance-vs-target.yaml`, `docs/worked-examples/target-budget-pattern-retail-store-sales.md`), well under the Windows `MAX_PATH` budget. PASS. |
| Hard rule #9 (no fabricated score) | Does this feature emit a numeric confidence/health/maturity/completeness score anywhere? | No. Any readiness framing in the second worked example uses only the four explicit statuses (`not_started \| blocked \| warning \| pass`), applied honestly as `not_started` (no target fact exists for `retail_store_sales` today) -- never a fabricated score or a status implying progress that has not happened (FR-016). PASS. |
| Readiness System (spine) | Which readiness stage does this feature advance? | **None**, for any real table. This is a cross-cutting pattern/template addition, precedented by `specs/084-worked-example-factory/plan.md`'s own "Readiness stages affected: None" row for the same reason (a meta/process addition, not a per-table stage advance). It instead supplies the PATTERN a future real target-fact table's Mapping-Ready-through-Semantic-Model-Ready stages would consume. Documented here as a precedented, justified deviation from the per-stage guiding rule, not a violation of it. |

**Overall**: PASS. No violation requires a Complexity Tracking entry (see
below -- table intentionally empty).

## Project Structure

### Documentation (this feature -- the spec-chain files this PLAN stage writes)

```text
specs/095-actuals-vs-target-budget-fact/
|-- spec.md              # Feature spec, clarified (input to this plan; not written here)
|-- plan.md              # This file (Phase 0/1 output)
|-- research.md          # Phase 0 output (this stage)
|-- data-model.md        # Phase 1 output (this stage)
|-- quickstart.md        # Phase 1 output (this stage)
`-- tasks.md              # Phase 2 output (a LATER /speckit-tasks stage; not created here)
```

### Feature deliverables (authored at the IMPLEMENT stage, at the paths the spec's Clarifications already fixed -- listed here for planning clarity; not written by this PLAN stage)

```text
docs/
`-- patterns/
    `-- target-budget-fact.md                          # FR-001..FR-005, FR-019: the modelling pattern

templates/
`-- metric-contract-shape.variance-vs-target.yaml       # FR-006..FR-009: the variance contract shape
                                                         # (co-located ALONGSIDE, never inside,
                                                         #  templates/metric-contract.yaml)

docs/
`-- worked-examples/
    `-- target-budget-pattern-retail-store-sales.md     # FR-011..FR-013: the second worked-example
                                                         # narrative (distinct from, never editing,
                                                         # docs/worked-examples/retail-store-sales.md)
```

**Structure Decision**: No source code, no `src/`, `warehouse/`, `powerbi/`,
or `mappings/` path is added or modified by this feature. Everything this
feature produces lives under `docs/`, `templates/`, and this feature's own
`specs/095-actuals-vs-target-budget-fact/` chain -- exactly the sanctioned
surfaces named by the collision-avoidance allocation ("Adds NO static rule
... New files under docs/ + templates/ + a worked-example dir; touches no
shared schema"). The three feature deliverables above are NOT written during
this PLAN stage (which produces only the four `specs/095-.../` chain files
listed first); they are the concrete target of a later implementation pass
that this plan and its `tasks.md` successor describe but do not yet execute.

## Files/dirs a FUTURE real target-fact build would touch (identified for planning clarity only; NOT created here)

Per FR-018 and Constitution Principle VIII, a real per-table target/budget
fact build is a separate, later feature. For orientation only, it would
eventually touch (none of these exist yet and none are created by this
feature):

- `mappings/<target-source-table>/` (the standard five mapping-gate artifacts,
  authored by walking the existing `source-mapping` skill)
- `warehouse/migrations/NNNN_create_silver_<target-source-table>.sql` and
  `..._gold_<target-source-table>_fact.sql` (authored by `retail-build-warehouse`,
  after the mapping gate clears)
- `mappings/<target-source-table>/metrics/<VarianceMetricName>.yaml` (a REAL
  filled contract, using this feature's contract shape as a starting pattern,
  with a real owner, real grain, and eventually a real RAG threshold)
- `mappings/<target-source-table>/readiness-status.yaml` (a fresh per-table
  spine record restarting at Mapping Ready, per FR-013)

## Complexity Tracking

*No entries.* The Constitution Check above found no violation requiring
justification -- this feature adds zero new templates (it fills an EXISTING
one as a pattern instance), zero new fields, zero new rules, zero new readiness
stages, and zero new runtime surfaces.
