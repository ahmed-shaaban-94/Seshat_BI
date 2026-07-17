# Activate the Professional dbt MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Every implementation task follows `superpowers:test-driven-development`; completion claims follow `superpowers:verification-before-completion`.

**Branch**: `133-activate-dbt-mvp` | **Date**: 2026-07-16 | **Spec**: [spec.md](./spec.md)

**Goal:** Ship a governed Postgres dbt execution adapter, a complete shadow build for the approved `retail_store_sales` example, normalized evidence, and portable Claude/Codex agent surfaces without allowing dbt to become readiness authority.

**Architecture:** A lazy Python control layer performs the Mapping Ready gate, validates model citations, creates an immutable accepted plan from dbt's non-DB parse artifacts, and invokes a fixed dbt selector in a shell-free child process. dbt materializes only target-prefixed shadow silver/gold/audit schemas; Seshat validates artifacts and parity rows, sanitizes the result into committed derived evidence, and stops for named-human approval.

**Tech Stack:** Python 3.13, stdlib plus existing PyYAML, argparse, pytest, dbt Core 1.12.0, dbt Postgres 1.10.2, PostgreSQL, SQL/Jinja, JSON Schema, Claude Code and Codex plugin bundles.

## Global Constraints

- Product name is Seshat BI; Python distribution is `seshat-bi`; console commands are `seshat` and the deprecated `retail` alias.
- Python is exactly the repository floor, `>=3.13`.
- The initial dbt pair is exactly `dbt-core==1.12.0` and `dbt-postgres==1.10.2`, pinned together in the optional `dbt` extra.
- Postgres is the only adapter in this MVP.
- dbt writes only `<target.schema>_silver`, `<target.schema>_gold`, and `<target.schema>_audit`; migration-owned `silver` and `gold` remain untouched.
- Mapping Ready `pass`, a matching named-human approval, `Gate status: CLEARED`, and a committed approved map are required before plan/build/test.
- A green dbt run is evidence only; it never writes readiness `pass` or approves a build-path switch.
- `warehouse/migrations/` remains the default build path and retained parity oracle.
- Full-refresh table/view materializations only; incremental models are deferred.
- Mutating commands accept no raw dbt arguments, selectors, targets, profiles, schema overrides, or inline SQL.
- Secrets exist only in the gitignored `.env`; a local ignored `profiles.yml` may contain `env_var()` references only.
- Raw `target/`, `logs/`, local plans, and locks are ignored; committed evidence is normalized and sanitized.
- `retail_store_sales` is a filled example, never a generic schema.
- dbt stops at gold and never invokes the Power BI execution adapter.
- Authored text is UTF-8 without BOM and ASCII unless an existing format requires otherwise.

---

## Summary

Feature 133 activates the runtime that feature 023 deliberately left planned. The deliverable is one coherent vertical slice: a real `dbt/` project, one approved worked table, Python gate/plan/runner/evidence modules, a nested CLI group, plugin commands and skills, package metadata, tests, and reconciled documentation. The public command surface work currently present as uncommitted changes in the primary checkout is an explicit integration dependency; this worktree must consume that canonical registry after it is committed, never recreate or overwrite it from a stale base.

## Technical Context

**Language/Version**: Python 3.13; dbt SQL/Jinja; YAML and JSON Schema.

**Primary Dependencies**: Existing runtime `pyyaml>=6`; optional exact pair `dbt-core==1.12.0`, `dbt-postgres==1.10.2`; existing optional `psycopg2-binary>=2.9` and `testcontainers[postgres]>=4.0` for live verification.

**Storage**: Committed mappings, dbt project files, JSON Schema, and normalized evidence; local ignored `.seshat/dbt/` run artifacts; PostgreSQL only at the live boundary.

**Testing**: pytest unit, contract, integration, and optional `live_db`; Ruff; `retail check`; deterministic bundle export and equality; secret scan.

**Target Platform**: Windows, macOS, and Linux package/agent installs; PostgreSQL for runtime execution.

**Project Type**: Python CLI/library plus an external dbt project and generated agent plugin bundles.

**Performance Goals**: Preflight work is linear in governed files and manifest nodes; per-table/target execution is single-writer; no unbounded lock wait or raw artifact copy.

**Constraints**: Stable exit codes `0..4`; no expected traceback; component and path redaction; manifest v12 and run-results v6 accepted for the pinned pair; complete parity rows required even when dbt tests are green.

**Scale/Scope**: One worked table, seven dbt transformation models plus one parity audit model, one governed selector, one nested CLI family, four Claude wrappers, and one shared skill in both public bundles.

## Constitution Check

*GATE: Passed before research and re-checked after design.*

| Principle | Design proof | Status |
|---|---|---|
| I -- Agent-first, gate-enforced | CLI exposes deterministic gates/evidence; agent skill remains the workflow interface. | PASS |
| II -- Depend, never fork | Uses dbt Core/Postgres and their stable JSON artifacts through a subprocess; no dbt engine reimplementation. | PASS |
| III -- Medallion, gold-only | Adapter materializes shadow silver/gold/audit and stops before semantic/Power BI execution. | PASS |
| IV -- Mapping before silver | `evaluate_mapping_gate()` runs before any dbt selection or DB access. | PASS |
| V -- Stop at judgment calls | Parity can recommend, but readiness/build-path changes require a named human. | PASS |
| VI -- Defaults then deviations | Migrations stay default until exact parity plus human approval. | PASS |
| VII -- Example, not schema | Generic code and skill contain no worked-table answers; filled models are isolated under the worked selector. | PASS |
| VIII -- Static-first, live deferred | Unit/contract/project compile work without a live DSN; live results are `[PENDING LIVE PROFILE]` when unavailable. | PASS |
| IX -- Secrets and reproducibility | Exact version pair, environment-only secrets, raw artifact isolation, hashes, and redaction. | PASS |

**Post-design re-check:** PASS. Shadow schemas, plan acceptance, artifact integrity checks, and evidence-only semantics strengthen the existing adapter ADR without changing any readiness stage or approval authority.

## Project Structure

### Documentation for Feature 133

```text
specs/133-activate-dbt-mvp/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- dbt-cli.md
|   |-- dbt-execution-plan.schema.json
|   `-- dbt-run-evidence.schema.json
|-- checklists/requirements.md
`-- tasks.md
```

### Runtime Source and Tests

```text
src/seshat/dbt/
|-- __init__.py          # Public adapter constants only; imports no dbt package.
|-- gate.py              # Working-set resolution and Mapping Ready refusal.
|-- contracts.py         # Immutable plan, invocation, artifact, parity, and evidence types.
|-- project.py           # Project fingerprint, profile/schema/selector/model-citation validation.
|-- planning.py          # Non-DB parse/list preflight, canonical plan JSON, SHA-256 digest.
|-- runner.py            # Current-environment executable, fixed argv, bounded lock, subprocess.
|-- artifacts.py         # Manifest v12/run-results v6 validation and node cross-checks.
|-- redaction.py         # Environment component and path redaction for text/objects.
`-- evidence.py          # Parity interpretation, normalized record, schema validation/write.

src/seshat/cli/
|-- parser.py            # Register the one top-level `dbt` group.
|-- parser_dbt.py        # Define doctor/validate/plan/build/test/inspect-run arguments.
|-- __init__.py          # Lazy `_DISPATCH["dbt"]` entry.
`-- commands/dbt.py      # Stable text/JSON presentation and exit mapping.

dbt/
|-- dbt_project.yml
|-- selectors.yml
|-- macros/generate_schema_name.sql
|-- models/sources/_sources.yml
|-- models/staging/retail_store_sales/{stg_retail_store_sales.sql,_models.yml}
|-- models/marts/retail_store_sales/{dim_customer_rss.sql,dim_product_rss.sql,
|   dim_payment_method_rss.sql,dim_location_rss.sql,dim_date_rss.sql,
|   fct_sales_rss.sql,_models.yml}
`-- models/audit/retail_store_sales/{audit_retail_store_sales_parity.sql,_models.yml}

schemas/dbt-run-evidence.schema.json
profiles.example.yml
.gitignore
pyproject.toml

tests/
|-- unit/dbt/{test_gate.py,test_project.py,test_planning.py,test_runner.py,
|   test_artifacts.py,test_redaction.py,test_evidence.py}
|-- unit/test_cli_dbt.py
|-- contract/test_dbt_project.py
|-- contract/test_dbt_evidence_schema.py
|-- contract/test_dbt_public_surface.py
|-- integration/test_dbt_artifact_flow.py
`-- live_db/test_dbt_retail_store_sales.py
```

### Public Agent Surface

```text
distribution/public-command-surface.yaml
distribution/public-knowledge-allowlist.yaml
distribution/bundle-templates/claude/commands/{dbt-doctor,dbt-plan,dbt-build,dbt-review}.md
distribution/bundle-templates/shared/skills/dbt-workflows/SKILL.md
integrations/claude-code/seshat-bi/commands/{dbt-doctor,dbt-plan,dbt-build,dbt-review}.md
integrations/{claude-code,codex}/seshat-bi/skills/dbt-workflows/SKILL.md
```

**Structure Decision**: Keep the adapter under `src/seshat/dbt/` because Seshat owns governance, invocation, and normalized evidence; keep transformations in top-level `dbt/` because dbt owns compilation and materialization. CLI presentation remains in the existing lazy command architecture. Public wrappers are authored only from distribution templates and regenerated into platform bundles.

## Interfaces Locked by This Plan

```python
# gate.py
def resolve_working_set(repo_root: Path, table_id: str) -> WorkingSet: ...
def evaluate_mapping_gate(working_set: WorkingSet) -> GateDecision: ...

# project.py
def validate_project(repo_root: Path, working_set: WorkingSet) -> ProjectValidation: ...
def fingerprint_project(repo_root: Path) -> str: ...

# planning.py
def create_plan(repo_root: Path, table_id: str, runner: DbtRunner) -> ExecutionPlan: ...
def canonical_plan_bytes(plan: ExecutionPlan) -> bytes: ...
def plan_digest(plan: ExecutionPlan) -> str: ...
def save_plan(repo_root: Path, plan: ExecutionPlan) -> Path: ...
def require_accepted_plan(expected_digest: str, actual: ExecutionPlan) -> None: ...

# runner.py
def resolve_dbt_executable(scripts_dir: Path | None = None) -> Path: ...
def build_dbt_argv(operation: Operation, context: RunContext) -> tuple[str, ...]: ...
def invoke_dbt(context: RunContext, argv: tuple[str, ...]) -> InvocationResult: ...
@contextmanager
def target_lock(repo_root: Path, table_id: str, target: str, timeout_s: float = 1.0): ...

# artifacts.py
def load_manifest(path: Path) -> ManifestSummary: ...
def load_run_results(path: Path) -> RunResultsSummary: ...
def cross_check_execution(plan: ExecutionPlan, results: RunResultsSummary) -> None: ...

# evidence.py
def parse_parity_rows(show_stdout: str) -> tuple[ParityAssertion, ...]: ...
def build_evidence(plan: ExecutionPlan, invocation: InvocationResult, artifacts: ArtifactSet,
                   parity: tuple[ParityAssertion, ...]) -> RunEvidence: ...
def write_evidence(repo_root: Path, evidence: RunEvidence) -> Path: ...
```

Exact field definitions and invariants are in [data-model.md](./data-model.md) and `contracts/`.

## Delivery Phases

1. **Foundation**: package extra, ignore rules, typed contracts, working-set gate, redaction, project/profile/citation validation.
2. **Immutable preflight**: fixed current-environment dbt executable, non-DB parse/list, manifest selection, canonical plan and digest.
3. **Governed execution**: lock, build/test fixed argv, artifact schema/node integrity, machine-readable parity collection, evidence schema/write.
4. **Worked dbt project**: shadow schema macro, source/staging/star/audit models, properties/tests/citations, pinned parse/compile verification.
5. **CLI and agents**: nested CLI family, shared public skill, Claude wrappers, canonical registry/allowlist, regenerated bundles.
6. **Reconciliation and proof**: docs/capabilities/release updates, full static verification, optional live Postgres parity and divergence tests.

## Dependency and Integration Risks

- The primary checkout contains an uncommitted canonical public command surface implementation from feature 126. Task T011 is blocked from editing those exact files until that work is committed and rebased/cherry-picked into this worktree. All runtime/dbt work can proceed first.
- This environment currently has no Python or `py` launcher. RED/GREEN test execution is `[PENDING LOCAL PYTHON 3.13]` until a Python 3.13 interpreter is installed or made available.
- Live dbt verification additionally needs the optional extras, Docker or a disposable Postgres instance, and `.env` values. Until present it is `[PENDING LIVE PROFILE]`, not a pass.
- dbt Core 1.12.0 was released on the planning date while the official docs still list Core 1.11 for manifest v12. The compatibility task must prove Core 1.12.0 + Postgres 1.10.2 produces manifest v12 and run-results v6 before capability state becomes shipped.

## Complexity Tracking

No constitution violation is accepted. The separate dbt project, control package, and distribution templates are the minimum boundaries required by the external engine, the governance authority split, and the two plugin platforms; they are one vertical feature rather than independent products.

## Evidence and Stop Points

- A static/compile checkpoint may complete without a DSN, but it must retain `[PENDING LIVE PROFILE]` for database assertions.
- Any mapping/citation/plan drift returns exit 3 and invokes zero DB-connected dbt commands.
- Missing Python/dbt/profile returns exit 2 without traceback.
- Unknown or incomplete artifacts return exit 4 and produce no trusted pass evidence.
- Passing parity produces an evidence record and a recommendation only. A named human decides any migration-to-dbt build-path switch.
