# Feature Specification: Activate the Professional dbt MVP

**Feature Branch**: `133-activate-dbt-mvp`

**Created**: 2026-07-16

**Status**: Implemented; activation deferred `[PENDING LIVE PROFILE]`

**Roadmap identity**: Activates the runtime build slice planned by F029 / on-disk
spec `023-dbt-transformation-adapter`. Spec 023 remains the historical planning
record; this spec owns the runnable project, Python control layer, public agent
surface, and evidence implementation.

**Input**: "Activate the dbt MVP as a professional layer across the dbt project,
agent skills, plugin commands, and Python package. Use an isolated worktree,
Superpowers, and Spec Kit. Apply all recommended choices across the session."

## Purpose and Readiness Stage

This feature implements the shipped dbt advisory seam as a governed Postgres
transformation-adapter candidate. dbt remains the build engine and Seshat BI remains
the readiness authority. Runtime activation remains deferred until FR-043 compile
proof and the named-owner compatibility attestation exist. The candidate serves
**Silver Ready** and **Gold Ready** only.
Its entry gate is **Mapping Ready = `pass`** with a matching named-human approval
and a cleared unresolved-question mirror.

The adapter never creates mapping truth, never grants an approval, never advances
a readiness stage, and never publishes Power BI. It materializes approved
transformations into isolated shadow schemas, runs tests and parity checks, and
produces sanitized derived evidence for the existing readiness spine.

The first filled instance is `retail_store_sales`, whose mapping gate is already
cleared. That instance proves the generic mechanism; it is not a universal schema.

## Scope

The MVP is one vertical slice with five coordinated surfaces:

1. A top-level `dbt/` project for Postgres, including a complete shadow build of
   the `retail_store_sales` silver table and gold star.
2. A Python control layer under `src/seshat/dbt_adapter/` that validates gates,
   creates immutable plans, invokes dbt in an isolated process, parses artifacts,
   redacts sensitive values, and emits normalized evidence.
3. A lazy-loaded `seshat dbt` CLI command family.
4. A shared public `dbt-workflows` skill for Claude and Codex plus guarded Claude
   slash-command wrappers.
5. Generated, drift-checked Claude and Codex plugin bundles and accurate capability
   claims.

The MVP is Postgres-only. It does not add orchestration, incremental models,
additional warehouse engines, Power BI execution, or an automatic build-path
switch.

## Architecture

### 1. dbt runtime project

The repository gains a top-level `dbt/` directory, parallel to `warehouse/`:

```text
dbt/
|- dbt_project.yml
|- macros/
|  |- generate_schema_name.sql
|  `- parity_helpers.sql
|- models/
|  |- sources/
|  |- staging/
|  |- marts/
|  `- audit/
`- tests/
```

The existing repository-root `profiles.example.yml` remains the one committed
example. A local git-ignored `profiles.yml` contains `env_var()` references only;
all real connection values remain in the git-ignored `.env`, consistent with the
repository secret boundary.

The default target writes to isolated relations:

- `<target.schema>_silver` for staging/silver models;
- `<target.schema>_gold` for dimensions and facts; and
- `<target.schema>_audit` for measured parity rows.

The default target MUST NOT write to migration-owned `silver` or `gold`. The
`retail_store_sales` instance contains one staging model, five dimension models,
one fact model, and one parity-audit model. This corrects the earlier planning
shorthand that referred to "one mart model" even though the governed gold output
is a fact plus five dimensions.

### 2. Python control layer

The Python layer is divided into small units with stable interfaces:

- `gate`: reads and validates readiness, approval, unresolved-question, and map
  evidence without writing it;
- `contracts`: validates adapter/model contracts and complete map citations;
- `project`: validates dbt project structure, allowed selectors, target schemas,
  and version compatibility;
- `planning`: produces a canonical execution plan and SHA-256 acceptance digest;
- `runner`: launches the current environment's pinned dbt executable as a child
  process with a closed argument set and no shell;
- `artifacts`: validates and parses `manifest.json`, `run_results.json`, and
  machine-readable `dbt show` output;
- `evidence`: creates a sanitized, schema-validated run record; and
- `redaction`: removes profile paths, hosts, user names, passwords, DSNs, and
  environment-derived secrets from all surfaced errors and evidence.

dbt runs in a separate process because dbt documents same-process parallel
invocations as unsafe and does not fully contract the Python objects returned by
`dbtRunner`. Seshat consumes the durable JSON artifacts instead.

### 3. CLI and public agent surface

The Python package exposes:

```text
seshat dbt doctor
seshat dbt validate --table <table>
seshat dbt plan --table <table>
seshat dbt build --table <table> --accept-plan <digest>
seshat dbt test --table <table> --accept-plan <digest>
seshat dbt inspect-run --table <table> --artifacts <target-dir>
```

The public plugin layer exposes a shared `dbt-workflows` skill to both Claude and
Codex. Claude also receives `dbt-doctor`, `dbt-plan`, `dbt-build`, and
`dbt-review` command wrappers. Codex uses `$dbt-workflows`, consistent with its
skills-first plugin surface.

All public entries are declared in the canonical public command surface, reviewed
through the public allowlist, generated into both bundles, and tested for exact
drift. This feature consumes the command-surface work currently being completed in
the main checkout; it MUST be rebased onto that committed work rather than copying
or overwriting its uncommitted files.

### 4. Evidence model

Raw dbt `target/` artifacts are local and git-ignored. A successful or handled
failed invocation produces one sanitized JSON record under:

```text
mappings/<table>/dbt-evidence/<invocation-id>.json
```

The record conforms to `schemas/dbt-run-evidence.schema.json` and includes:

- schema version and invocation ID;
- source table ID and approved map path plus Git revision;
- accepted plan digest and project fingerprint;
- dbt Core and adapter versions;
- target name and redacted shadow-schema names;
- selected model/test unique IDs;
- per-status counts from `run_results.json`;
- the four measured parity assertions;
- artifact hashes;
- start/end timestamps and elapsed duration; and
- an outcome of `pass`, `blocked`, `failed`, or `unavailable`.

`pass` means the dbt invocation and parity checks completed successfully. It is
derived evidence only and MUST NOT be interpreted as Silver Ready, Gold Ready, or
a build-path approval.

The command prints a deterministic readiness evidence fragment that the agent may
cite in `readiness-status.yaml`. The Python command does not rewrite the commented
human-audit YAML automatically. The agent records the citation and any concrete
blocker while leaving stage statuses unchanged.

## Governed Data Flow

1. `doctor` checks package versions, dbt executable provenance, project presence,
   profile availability, ignore rules, and target safety. It opens no database.
2. `validate` reads `mappings/<table>/` and fails closed unless Mapping Ready is
   `pass`, a matching named-human approval exists, the question gate says
   `CLEARED`, and the approved map is present. It then validates every model
   contract and citation.
3. `plan` resolves an allowlisted table selector, the exact dbt nodes, shadow
   schemas, approved map revision, project fingerprint, dbt versions, and profile
   target into canonical JSON. It returns a digest and writes no database state.
4. `build` or `test` requires that exact digest, recomputes every input, and refuses
   if readiness, source files, versions, profile target, or node selection drifted.
5. `build` launches a fixed `dbt build --select <governed-selector>` command in an
   isolated child process. No raw pass-through dbt arguments are accepted.
6. dbt materializes only shadow silver/gold relations and runs uniqueness,
   not-null, relationship, and parity tests in DAG order.
7. The audit model returns one row per parity assertion. Seshat calls `dbt show`
   with JSON output for that single audit node and captures expected, actual,
   delta, tolerance, and pass/fail values.
8. Seshat validates artifact schemas and cross-checks selected unique IDs against
   the accepted plan before emitting the sanitized evidence record.
9. The agent cites the evidence or records the concrete blocker in the existing
   readiness status. The agent recommends and stops; a named human decides any
   build-path switch.

## User Scenarios and Testing

### User Story 1 - Discover and diagnose the dbt layer (Priority: P1)

An analyst or agent can discover the dbt workflow from either public plugin and
run a read-only diagnostic that explains whether the local package, project,
profile, table gate, and versions are ready.

**Why this priority**: A professional execution adapter must fail gracefully before
it touches a database and must be discoverable from the product's primary agent
surface.

**Independent Test**: Install each generated plugin bundle in an isolated fixture
and invoke its dbt route against environments with and without the optional dbt
extra and profile.

**Acceptance Scenarios**:

1. **Given** the optional dbt extra and project are installed, **When** `doctor`
   runs, **Then** it reports compatible versions, safe ignored paths, and one next
   action without opening a database.
2. **Given** dbt or a real profile is absent, **When** `doctor` runs, **Then** it
   returns `unavailable`, prints the exact enable steps, emits no traceback, and
   claims no live pass.
3. **Given** either installed plugin, **When** a user asks for dbt work, **Then**
   the router reaches `dbt-workflows` and preserves the Seshat readiness gates.

---

### User Story 2 - Validate and accept an immutable execution plan (Priority: P1)

An agent can validate a mapped table's dbt project and present an exact, reviewable
plan before any database mutation.

**Why this priority**: The plan digest closes the gap between a safe preflight and
the code, gate, versions, target, or selection that actually executes.

**Independent Test**: Generate a plan for `retail_store_sales`, mutate each bound
input independently, and verify execution refuses every stale digest.

**Acceptance Scenarios**:

1. **Given** Mapping Ready is passed with a matching approval and cleared mirror,
   **When** the models and contracts cite the approved map completely, **Then**
   `plan` returns the exact selected nodes, shadow target, and acceptance digest.
2. **Given** Mapping Ready is not passed, the approval is missing, or the mirror
   disagrees, **When** validation runs, **Then** it returns a governance block and
   invokes no dbt command.
3. **Given** an accepted plan, **When** a bound file, map revision, version, target,
   or node selection changes, **Then** `build` refuses the stale digest and requires
   a new plan.

---

### User Story 3 - Build and test in isolated shadow schemas (Priority: P1)

An agent can execute the approved Postgres dbt project without allowing dbt to
write into migration-owned schemas or bypass the selected table boundary.

**Why this priority**: This is the runtime activation promised by F029 while
preserving migrations as the default and rollback oracle.

**Independent Test**: Run the child-process seam against a fake executable and a
fixture artifact set, then run the optional live suite against ephemeral Postgres.

**Acceptance Scenarios**:

1. **Given** a current accepted plan and valid profile, **When** `build` runs,
   **Then** it invokes the exact governed selector and builds only the table's
   shadow silver, gold, audit models, and tests.
2. **Given** a user attempts to pass a raw selector, schema override, profile,
   exclusion, full refresh, or arbitrary dbt argument, **When** arguments are
   parsed, **Then** the command rejects them before invoking dbt.
3. **Given** dbt returns a handled model or test failure, **When** artifacts are
   inspected, **Then** Seshat writes a sanitized failed/blocked evidence record,
   returns non-zero, and leaves readiness stages unchanged.

---

### User Story 4 - Prove parity and stop for human approval (Priority: P2)

For the worked table, the dbt shadow gold star is compared with the retained
migration-built gold star using measured values.

**Why this priority**: Parity is the condition for recommending dbt as a table's
build path, but it is meaningful only after the gated build exists.

**Independent Test**: Seed the migration and dbt outputs with matching and
divergent fixtures and assert each parity row and blocker independently.

**Acceptance Scenarios**:

1. **Given** matching migration and dbt outputs, **When** parity runs, **Then** it
   records equal fact row count, equal distinct business-key count, every additive
   money sum within `0.01`, and equal member count for each conformed dimension.
2. **Given** any assertion differs, **When** evidence is emitted, **Then** it names
   the assertion, expected value, actual value, and delta as a concrete blocker;
   migrations remain the default.
3. **Given** all assertions pass, **When** evidence is emitted, **Then** the agent
   recommends a build-path decision and stops. It does not change the build path or
   readiness status without a named-human approval.

---

### User Story 5 - Ship one accurate package and plugin capability (Priority: P2)

Maintainers can publish the Python extra and both agent bundles from reviewed
canonical inputs without hand-edited generated copies or false capability claims.

**Why this priority**: The professional layer is incomplete if the runtime exists
only in the development tree or if installed agents advertise a different surface.

**Independent Test**: Regenerate both bundles, compare exact trees, install each in
an isolated acceptance environment, and reconcile the capability manifest with the
actual CLI, skill, commands, and optional dependencies.

**Acceptance Scenarios**:

1. **Given** canonical wrappers and allowlist entries, **When** bundles regenerate,
   **Then** Claude and Codex contain the same `dbt-workflows` skill and Claude
   contains exactly the declared dbt commands.
2. **Given** the package is installed without `[dbt]`, **When** non-dbt Seshat
   commands import or run, **Then** no dbt module or Postgres driver is imported.
3. **Given** runtime or bundle evidence is missing, **When** capability inventory is
   validated, **Then** the dbt capability cannot be classified as shipped.

## Edge Cases

- A model exists for a table whose mapping is blocked or absent: refuse before
  parsing or running dbt.
- Readiness says `pass` but lacks a matching named-human mapping approval: refuse.
- Readiness and `unresolved-questions.md` disagree: refuse and name both facts.
- A source map changed after a model contract was authored: mark the citation stale.
- A model builds a column, grain, key, PII rule, or placement not in the map: defect.
- The accepted plan uses an old Git revision, project hash, version, selector, or
  target: reject it as stale.
- `profiles.yml` is tracked, contains a literal connection value instead of
  `env_var()` references, or the committed example contains a literal host: refuse
  and report the secret-safety boundary.
- The resolved dbt executable is outside the current Python environment or reports
  unexpected versions: refuse rather than running an ambient global installation.
- Two invocations target the same table and shadow target concurrently: the second
  invocation refuses through a per-target lock; it never runs concurrently.
- dbt exits without valid artifacts or artifacts name nodes outside the accepted
  plan: treat the run as an integrity failure.
- dbt logs echo profile-derived values: redact them before any output or evidence is
  surfaced.
- Tests are green but parity rows are absent or incomplete: block; green tests alone
  are insufficient evidence.
- Parity passes but no human approves the switch: migrations remain the default.
- A partial dbt build leaves shadow relations: record failure; never treat partial
  relations as readiness evidence.
- Python, dbt, the profile, or a DSN is unavailable: report `[PENDING LIVE PROFILE]`
  with enable steps and keep static/project validation useful.
- A generated plugin file is edited directly: bundle drift checks fail.
- Windows paths exceed the repository target: fail static validation before dbt.

## Requirements

### Governance and authority requirements

- **FR-001**: Every dbt `validate`, `plan`, `build`, and `test` request MUST resolve
  exactly one `mappings/<table>/` working set.
- **FR-002**: The adapter MUST refuse before invoking dbt unless Mapping Ready is
  `pass`, a matching named-human mapping approval exists, the unresolved-question
  mirror is `CLEARED`, and the approved source map exists.
- **FR-003**: Every model MUST carry a model contract citing the approved map path,
  Git revision, grain, key, and every output column. Missing or stale citations
  MUST block execution.
- **FR-004**: The adapter and models MUST NOT define source meaning, metrics,
  business rollups, semantic logic, PII rulings, or dashboard design.
- **FR-005**: The default dbt target MUST materialize only into isolated shadow
  schemas and MUST NOT write to migration-owned `silver` or `gold`.
- **FR-006**: `warehouse/migrations` MUST remain the default build path and retained
  parity oracle. The adapter MUST NOT delete, supersede, or stop applying a
  migration automatically.
- **FR-007**: A build-path switch MUST require passing parity evidence plus a named
  human approval. The adapter may recommend and MUST stop.
- **FR-008**: dbt run/test/parity results MUST be treated as derived evidence only.
  No dbt outcome may write a readiness stage to `pass`.
- **FR-009**: dbt MUST stop at gold and MUST NOT invoke or configure the Power BI
  execution adapter.
- **FR-010**: No numeric readiness, maturity, or confidence score may be emitted.

### dbt project requirements

- **FR-011**: The project MUST use Postgres and reuse the committed
  repository-root placeholder-only `profiles.example.yml`. The local
  `profiles.yml` MUST be git-ignored, MUST contain `env_var()` references rather
  than literal connection values, and MUST obtain real values only from the
  git-ignored `.env`.
- **FR-012**: The default schema macro MUST produce target-prefixed silver, gold,
  and audit schemas and MUST reject unsafe schema identifiers.
- **FR-013**: The worked instance MUST reproduce the complete migration-built gold
  star: one fact and all five dimensions, including the approved unknown-member
  behavior.
- **FR-014**: The worked instance MUST include uniqueness and not-null tests on the
  fact business key plus relationships tests for every fact foreign key.
- **FR-015**: Parity MUST measure fact row count, distinct business-key count,
  additive money totals with absolute delta `<= 0.01` per measure, and each
  conformed dimension member count.
- **FR-016**: Parity MUST expose one structured audit row per assertion containing
  assertion ID, expected, actual, delta, tolerance, and passed status.
- **FR-017**: The MVP MUST use deterministic full-refresh table/view
  materializations. Incremental materialization is deferred.
- **FR-018**: Generic project macros, schemas, skills, templates, and contracts MUST
  contain no worked-table-specific business answers.

### Python runtime and CLI requirements

- **FR-019**: The package MUST expose a `dbt` optional extra that pins a tested
  dbt Core and dbt Postgres pair together. The initial supported pair is
  `dbt-core==1.12.0` and `dbt-postgres==1.10.2`.
- **FR-020**: dbt and adapter imports MUST remain lazy so installing or importing
  base Seshat BI does not import dbt or a DB driver.
- **FR-021**: The runner MUST invoke dbt in a child process without a shell and MUST
  resolve the executable from the current Python environment.
- **FR-022**: The CLI MUST expose `doctor`, `validate`, `plan`, `build`, `test`, and
  `inspect-run` under one lazy-loaded `seshat dbt` command group.
- **FR-023**: Mutating commands MUST accept only Seshat-owned arguments and MUST NOT
  provide raw dbt argument pass-through.
- **FR-024**: `plan` MUST bind the table, approved map revision, project fingerprint,
  selected unique IDs, versions, target, and shadow schemas into canonical JSON and
  a SHA-256 digest.
- **FR-025**: `build` and `test` MUST require `--accept-plan`, recompute the plan,
  and refuse any digest drift before database access.
- **FR-026**: The runner MUST prevent concurrent invocations for the same table and
  target through a bounded per-target lock.
- **FR-027**: The runner MUST validate `manifest.json` and `run_results.json` and
  cross-check all executed unique IDs against the accepted plan.
- **FR-028**: Measured parity rows MUST be collected through one machine-readable
  `dbt show` invocation against the governed audit node; arbitrary inline SQL is
  forbidden.
- **FR-029**: Each handled invocation MUST emit a sanitized record conforming to
  `schemas/dbt-run-evidence.schema.json` and MUST hash the raw artifacts it cites.
- **FR-030**: Raw dbt `target/`, `logs/`, `profiles.yml`, and local lock files MUST be
  git-ignored and MUST NOT be copied into committed evidence.
- **FR-031**: The CLI MUST emit stable text and JSON formats, actionable unavailable
  instructions, and no traceback for expected environment or dbt failures.
- **FR-032**: Exit behavior MUST distinguish success, handled dbt/test failure,
  unavailable prerequisites, governance refusal, and artifact-integrity failure.
- **FR-033**: Every surfaced error and evidence field MUST pass component-level
  secret and path redaction before output.

### Agent and plugin requirements

- **FR-034**: A portable `dbt-workflows` skill MUST ship in both Claude and Codex
  bundles and route doctor, planning, execution, evidence review, and approval stops.
- **FR-035**: Claude MUST ship `dbt-doctor`, `dbt-plan`, `dbt-build`, and
  `dbt-review` wrappers declared by the canonical public command surface.
- **FR-036**: The Seshat router and help surface MUST discover every shipped dbt
  skill/command and MUST advertise no deferred command.
- **FR-037**: Public wrappers and skills MUST reference installed package paths and
  portable artifacts only; development-only `.claude/skills/` paths are forbidden.
- **FR-038**: Public sources MUST be explicitly allowlisted, secret-scanned, license
  reviewed, and deterministically exported into both generated bundles.
- **FR-039**: Capability inventory MUST classify the dbt adapter from real ship
  feeders: CLI dispatch, runtime project, public skill/bundles, tests, and the
  mandatory FR-043 proof. It MUST remain deferred while any required feeder is
  blocked; the old advisory-only claim MUST still be corrected.
- **FR-040**: The existing internal dbt skill, ADR, contracts, integration guide,
  roadmap/capability docs, installation docs, and release notes MUST be reconciled
  from "planned runtime" to the implemented candidate boundary without erasing
  history or claiming activation before mandatory verification.

### Testing and verification requirements

- **FR-041**: Gate, citation, plan digest, selection, redaction, locking, artifact
  parsing, parity interpretation, and evidence serialization MUST have unit tests
  that require neither dbt nor a database.
- **FR-042**: CLI parser/dispatch, optional-extra isolation, JSON schemas, capability
  claims, public command surface, allowlist, bundle regeneration, and generated-tree
  equality MUST have contract tests.
- **FR-043**: The dbt project MUST pass parse/compile and fixture artifact tests under
  the pinned pair.
- **FR-044**: An optional `live_db` suite MUST build migration and dbt shadow outputs
  in ephemeral Postgres and verify all four parity classes plus divergence cases.
- **FR-045**: If Python, dbt, Docker, the DB extra, or a DSN is unavailable, live
  verification MUST be reported as pending/unavailable, never as pass.
- **FR-046**: Final verification MUST include the full native test suite, lint,
  `retail check`, bundle regeneration check, secret scan, and a clean worktree diff.

## Key Entities

- **dbt execution plan**: Immutable preflight facts bound to a digest: table, map
  revision, project fingerprint, selection, versions, target, and shadow schemas.
- **dbt run evidence**: Sanitized derived record of one invocation and its measured
  test/parity results. It is evidence, never approval or run state.
- **model contract**: Per-model citation record connecting every built column and
  grain/key assertion to the approved source map.
- **parity audit row**: One measured comparison with expected, actual, delta,
  tolerance, and passed status.
- **governed selector**: Seshat-owned mapping from one table ID to an exact set of dbt
  unique IDs; users cannot widen it with raw dbt syntax.
- **build-path decision**: Named-human approval, after passing parity, that chooses
  dbt instead of migrations for a table. It is not made by this adapter.

## Error and Exit Contract

Expected failures never traceback and never expose secrets:

| Exit | Meaning | Evidence behavior |
|------|---------|-------------------|
| `0` | Command completed as requested | May write derived run evidence; never means readiness pass |
| `1` | dbt completed with handled model/test/parity failure | Write sanitized failed/blocked evidence when artifacts are valid |
| `2` | Usage or prerequisite unavailable | No DB access; print enable steps; optional unavailable record only |
| `3` | Governance refusal or stale plan | No dbt invocation; print concrete blocker |
| `4` | Artifact/evidence integrity failure | Treat run as failed; never trust partial evidence |

Unhandled programmer defects may retain the normal Python failure behavior in
development tests, but public command handlers MUST convert all documented
environment, gate, process, dbt, and artifact failures into the contract above.

## Human Approval Boundary

- A named table/data owner approves Mapping Ready before any model runs.
- A named human approves any change from migrations to dbt only after parity passes.
- A named human resolves grain, PII, sentinel-vs-null, rollup, or business-meaning
  ambiguity before affected models are authored or executed.
- A named reviewer approves any compatibility-policy change or major dbt upgrade.
- The agent and dbt may recommend. Neither may grant these approvals.

## Allowed Operations

- Read committed readiness, mapping, contracts, and project files.
- Parse/compile the dbt project without database mutation.
- After the gate and accepted-plan checks, build/test only the governed selector in
  shadow schemas.
- Read dbt JSON artifacts and the single governed parity audit node.
- Write sanitized derived evidence and recommend a human decision.

## Forbidden Operations

- Running any model before the mapping gate is fully passed.
- Using dbt models to invent or override business meaning.
- Accepting raw dbt selectors or arbitrary pass-through arguments.
- Writing to migration-owned silver/gold before a separately approved switch.
- Treating green dbt results as stage approval.
- Deleting the migration parity oracle.
- Publishing or changing Power BI.
- Committing a real connection value, host, DSN, credential, raw dbt target
  artifact, or log; or placing a literal secret in the local profile instead of
  `.env`.
- Running concurrent dbt invocations for the same table/target.
- Emitting a confidence/readiness score.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Every blocked/missing/mismatched Mapping Ready fixture invokes zero dbt
  subprocesses and returns a concrete governance blocker.
- **SC-002**: Mutating commands execute only when the recomputed plan digest is exactly
  equal to the accepted digest; all bound-input drift fixtures refuse execution.
- **SC-003**: The worked example builds one staging model, five dimensions, one fact,
  and one audit model exclusively in target-prefixed shadow schemas.
- **SC-004**: The parity evidence reports 100% of the required assertion classes with
  expected, actual, and delta values; every injected divergence is detected.
- **SC-005**: Zero green dbt fixtures alter a readiness stage or create an approval.
- **SC-006**: Base-package import tests observe no imported dbt or database-driver
  modules when the `[dbt]` extra is absent.
- **SC-007**: Every expected secret/DSN/profile-path fixture is absent from stdout,
  stderr, JSON evidence, and generated bundles.
- **SC-008**: Claude and Codex bundles contain identical `dbt-workflows` skill content;
  Claude contains exactly the four declared dbt wrappers and Codex advertises none as
  slash commands.
- **SC-009**: Clean regeneration of both bundles is byte-identical to committed output.
- **SC-010**: The dbt capability is reported shipped only when CLI, runtime project,
  public skill, generated bundles, and verification feeders all exist.
- **SC-011**: With the pinned extra and ephemeral Postgres available, the live suite
  proves the matching worked example and at least one failure for each parity class.
- **SC-012**: Without live prerequisites, the same suite reports unavailable/pending
  with enable steps and produces no fabricated pass.

## Testing Strategy

1. **Unit tests without dbt/DB**: pure fixtures for gates, citations, plans,
   selectors, versions, redaction, artifacts, evidence, locks, and exit mapping.
2. **CLI and contract tests**: parser/dispatch, optional imports, JSON schema,
   capability feeders, command surface, allowlist, routers, generated bundles, docs,
   and help accuracy.
3. **Pinned dbt compatibility tests**: install `[dbt]`, run `dbt parse`, compile the
   worked selector, validate manifest/run-results schema versions, and exercise
   machine-readable parity output.
4. **Optional live Postgres tests**: apply retained migrations, seed the worked data,
   build shadow models, verify matching parity, inject each divergence, and rerun.
5. **Repository gates**: full pytest suite, Ruff, `retail check`, bundle check,
   capability reconciliation, secret scan, path/encoding checks, and Git diff review.

## Dependencies

- Accepted F029 ADR, contracts, integration guide, and internal skill.
- The approved per-table mapping artifacts and readiness spine.
- The retained warehouse migrations used as parity oracle.
- The canonical public-command-surface feature currently uncommitted in the main
  checkout. This branch must consume its committed result before implementation of
  plugin declarations.
- Python 3.13 for the repository test/runtime baseline.
- Optional dbt Core/Postgres dependencies and, for live proof, a Postgres profile or
  ephemeral test container.

## Assumptions

- Postgres remains the only transformation engine in this MVP.
- `retail_store_sales` remains the first filled instance because its mapping gate and
  human approval are already complete.
- Full-refresh deterministic materialization is sufficient for MVP data volume.
- The current stable candidate pair is dbt Core 1.12.0 plus dbt Postgres 1.10.2;
  implementation must prove the pair before publishing the extra.
- Raw artifacts remain local; the normalized evidence schema is the durable contract.
- A real profile and live database may be unavailable during development. Static,
  fixture, compile, package, and plugin work remains required and useful.
- The user's standing instruction approves recommended design choices through this
  session; only repository authority gates or unavailable external prerequisites stop
  progress.

## Non-Goals

- Replacing dbt with a custom SQL engine or forking dbt.
- Supporting Snowflake, SQL Server, MySQL, DuckDB, Parquet, or Fusion in this MVP.
- Incremental models, snapshots, seeds, exposures, the dbt Semantic Layer, or dbt
  orchestration.
- Automatically generating business transformation SQL from incomplete mappings.
- Automatically switching production build paths or editing Power BI connections.
- Publishing Power BI, scheduling jobs, or implementing Dagster integration.
- Retiring migrations or removing their role as rollback/parity oracle.
- Adding a new readiness stage, run-state engine, or numeric readiness score.

## Evidence Required for Completion

- Passing unit, CLI, schema, bundle, capability, and repository gate results.
- A compatibility record for the pinned dbt Core/Postgres pair.
- A compiled manifest proving the complete worked selector and shadow targets.
- Live Postgres parity evidence when the required local tools are available; otherwise
  an explicit `[PENDING LIVE PROFILE]` boundary with enable steps.
- A clean generated-bundle comparison and secret scan.
- No automatic readiness pass or build-path approval in any diff or evidence file.
