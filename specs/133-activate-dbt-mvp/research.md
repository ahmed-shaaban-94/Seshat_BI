# Research: Activate the Professional dbt MVP

**Feature**: 133-activate-dbt-mvp  
**Date**: 2026-07-16  
**Status**: Complete for planning

## D1 -- Invocation Boundary

**Decision**: Invoke dbt through a child process with `shell=False`, an argv tuple owned by Seshat, and the `dbt` executable resolved from the current Python environment's scripts directory.

**Rationale**: dbt documents `dbtRunner` for programmatic calls but warns that concurrent invocations in one process are unsafe and that returned Python objects are not fully contracted. Seshat needs concurrency isolation, stable exit behavior, and artifact-based evidence, so the CLI boundary is safer and easier to audit.

**Rejected alternatives**:

- `dbtRunner` in-process: rejected because a long-lived agent process could overlap invocations and couple Seshat to unstable result objects.
- Shell command strings: rejected because they permit quoting ambiguity and argument injection.
- Global PATH lookup: rejected because it can run a dbt installation outside the active Seshat environment.

**Source**: [dbt programmatic invocations](https://docs.getdbt.com/reference/programmatic-invocations)

## D2 -- Version Pair and Artifact Schemas

**Decision**: Pin `dbt-core==1.12.0` and `dbt-postgres==1.10.2` together. Accept manifest schema v12 and run-results schema v6 only after the compatibility task reproduces them under this exact pair.

**Rationale**: dbt Core 1.12.0 supports Python 3.13. dbt Postgres 1.10.2 declares dbt Core `>=1.8,<2`, so the pair is metadata-compatible. dbt's current manifest documentation maps Core 1.8 through 1.11 to v12, and current run-results documentation names v6. Because Core 1.12.0 is newer than the displayed manifest table, execution must prove the exact artifacts before publication.

**Rejected alternatives**:

- Loose compatible ranges: rejected because artifacts and behavior could drift between installs.
- dbt Core 2/Fusion: rejected because this MVP was designed and contracted around the stable Core 1.x/Postgres adapter pair.
- Trusting package metadata alone: rejected because dependency compatibility does not prove project parse/compile or artifact compatibility.

**Sources**:

- [dbt-core on PyPI](https://pypi.org/project/dbt-core/)
- [dbt-postgres 1.10.2 metadata](https://pypi.org/pypi/dbt-postgres/1.10.2/json)
- [dbt manifest JSON](https://docs.getdbt.com/reference/artifacts/manifest-json)
- [dbt run results JSON](https://docs.getdbt.com/reference/artifacts/run-results-json)

## D3 -- Non-Database Plan Preflight

**Decision**: `plan` runs `dbt parse --no-partial-parse` and `dbt ls --select selector:<name> --output json` in an isolated local target directory, then binds the returned enabled unique IDs into the plan.

**Rationale**: `dbt ls` reads the profile to resolve target-specific Jinja but does not connect or issue queries. Parse/list therefore closes selector ambiguity before mutation while preserving dbt as the source of truth for its graph. The plan can hash the manifest and exact node IDs.

**Rejected alternatives**:

- Reimplement dbt selection in Python: rejected as a fork of dbt behavior.
- Plan from filenames/tags only: rejected because enabled state, tests, and graph expansion would be incomplete.
- Run `dbt compile` as preflight: rejected because compile can execute introspective queries and crosses the desired non-DB boundary.

**Sources**:

- [dbt parse command](https://docs.getdbt.com/reference/commands/parse)
- [dbt ls command](https://docs.getdbt.com/reference/commands/list)
- [dbt YAML selectors](https://docs.getdbt.com/reference/node-selection/yaml-selectors)

## D4 -- Immutable Acceptance Plan

**Decision**: Canonicalize the plan as UTF-8 JSON with sorted keys and compact separators, omit the digest field from the hashed payload, and use lowercase SHA-256 hex. Save it locally under `.seshat/dbt/plans/<table>-<target>.json`.

**Bound facts**:

- schema version;
- table ID;
- approved source-map path and committed blob revision;
- readiness and unresolved-question content hashes;
- dbt project fingerprint;
- exact selected unique IDs;
- dbt Core and adapter versions;
- fixed selector and target;
- derived shadow silver/gold/audit schema names;
- manifest schema and an allowlisted semantic SHA-256 of the governed graph.

Pinned-runtime verification showed that dbt rewrites `generated_at` and
`invocation_id` on every parse. The plan therefore binds the deterministic
allowlisted graph fingerprint; evidence separately preserves the raw artifact
SHA-256 for byte-level provenance.

**Rationale**: Recomputing all facts immediately before build/test makes plan acceptance a meaningful authorization of a specific action, not a stale acknowledgement.

**Rejected alternatives**:

- Timestamp in the hashed payload: rejected because identical inputs would produce different plans.
- Git HEAD alone: rejected because it would not detect uncommitted project or profile-template drift.
- Persisted run-state engine: rejected because readiness remains recomputed from artifacts and approvals.

## D5 -- Mapping and Citation Gate

**Decision**: Resolve exactly one `mappings/<table>/` directory; require Mapping Ready `pass`, a matching mapping approval with named approver/date, `Gate status: CLEARED`, a tracked clean `source-map.yaml`, and a model/column citation contract that names the map path and committed blob revision.

**Rationale**: The existing ADR and skill make mapping the first refusal point. Requiring the committed blob revision prevents a model contract from silently citing pre-approval or locally changed meaning.

**Rejected alternatives**:

- Readiness status alone: rejected because the mirror and source map can drift.
- Parse comments inside SQL for citations: rejected because comments are hard to validate structurally and do not enter dbt's manifest.
- Let dbt tests validate meaning: rejected because tests are evidence, not business approval.

## D6 -- Model Contract Location

**Decision**: Store filled contracts in dbt model property YAML. Every model has `meta.seshat` with `table_id`, `source_map`, `source_map_revision`, `grain`, `business_key`, and `authority: derived`; every output column has `meta.seshat.source_columns` or a named governed derivation.

**Rationale**: Properties are structured, version-controlled, and represented in `manifest.json`, allowing validation both before and after execution. Generic templates remain table-neutral while the filled worked instance can cite its approved facts.

**Rejected alternatives**:

- Separate Markdown-only contracts: rejected as insufficient for fail-closed machine validation.
- SQL header comments only: rejected for the same reason.
- One table-level contract for all models: rejected because every model and output column needs its own lineage boundary.

## D7 -- Shadow Schema Isolation

**Decision**: Models declare custom schemas `silver`, `gold`, or `audit`. A `generate_schema_name` macro validates the configured target schema and custom schema and returns `<target.schema>_<custom_schema>`.

**Rationale**: A fixed macro makes migration-owned schemas unreachable through normal model configuration. Validation checks both static configs and compiled relation names.

**Rejected alternatives**:

- Write to `silver`/`gold` with aliases: rejected because it risks dual writers.
- Use database-per-run isolation: rejected as unnecessary infrastructure for the MVP.
- Accept a CLI schema override: rejected because Seshat must own the target boundary.

## D8 -- Worked Star Materialization

**Decision**: Reproduce migration 0003/0004 with one staging table, four entity dimension tables, one date dimension table, one fact table, and one audit view. Generate deterministic surrogate keys with ordered `row_number()` plus explicit `-1` sentinel rows for entity dimensions; date has no sentinel.

**Rationale**: Parity requires full fact/dimension behavior, including unknown members. Deterministic keys make reruns reproducible while retaining the approved sentinel policy.

**Rejected alternatives**:

- One flattened mart model: rejected because it does not reproduce the migration-built star.
- Identity columns: rejected because dbt create-table-as materialization does not provide portable deterministic identity setup.
- Incremental models: rejected by the MVP full-refresh constraint.

## D9 -- Parity Collection

**Decision**: Materialize `audit_retail_store_sales_parity` as a view with exactly one row per required assertion. Collect it using fixed `dbt show --select audit_retail_store_sales_parity --output json --log-format json --limit -1`; parse only dbt's machine-readable result event.

**Assertion classes**:

- fact row count;
- distinct transaction/business key count;
- additive `total_spent` sum with absolute delta `<= 0.01`;
- member count for customer, product, payment method, location, and date dimensions, including sentinel members where approved.

**Rationale**: One governed audit node avoids arbitrary SQL and provides explicit expected, actual, delta, tolerance, and pass fields for every assertion.

**Rejected alternatives**:

- Parse pretty terminal tables: rejected as unstable.
- Accept inline SQL from the CLI: rejected as an injection and governance bypass.
- Treat green tests as parity: rejected because test success does not prove all parity rows exist.

**Sources**:

- [dbt show command](https://docs.getdbt.com/reference/commands/show)
- [dbt build command](https://docs.getdbt.com/reference/commands/build)

## D10 -- Artifact Integrity

**Decision**: Validate JSON object shape, exact schema URI, invocation command, unique IDs, status values, and artifact hashes. Cross-check every executed project node against the accepted selection plus dbt-generated tests whose dependencies stay within that selection. Reject missing, extra, unknown-schema, or partial artifacts with exit 4.

**Rationale**: `manifest.json` describes the full graph while `run_results.json` contains only executed nodes. Both are necessary to prove selection and interpret tests.

**Rejected alternatives**:

- Trust the subprocess exit code: rejected because partial or wrong-selection results can share the same coarse exit.
- Commit raw artifacts: rejected because they contain absolute paths, compiled SQL, timing, and adapter messages.
- Accept arbitrary future schema versions: rejected because parsing unverified shapes could fabricate evidence.

**Sources**:

- [dbt manifest JSON](https://docs.getdbt.com/reference/artifacts/manifest-json)
- [dbt run results JSON](https://docs.getdbt.com/reference/artifacts/run-results-json)

## D11 -- Redaction and Evidence

**Decision**: Load `.env` into a child-only environment, collect non-empty values for known dbt environment variables, redact exact values and URI components, replace absolute repository/home paths with stable tokens, and recursively sanitize every user-visible string. Commit only normalized JSON under `mappings/<table>/dbt-evidence/<invocation-id>.json`.

**Rationale**: dbt logs and adapter messages can reformulate credentials or reveal machine paths. Component-level redaction plus normalized allowlisted fields is safer than copying output.

**Rejected alternatives**:

- Literal DSN replacement only: rejected because drivers reformat host/user/password components.
- Store raw stdout/stderr in evidence: rejected because it expands secret and stability risk.
- Put credentials in `profiles.yml`: rejected by the repository's `.env`-only rule.

## D12 -- Concurrency and Exit Contract

**Decision**: Use an atomic local lock file keyed by sanitized table and target, wait at most one second, and refuse if held. Map handled outcomes to exits: 0 complete, 1 dbt/test/parity failure, 2 unavailable/usage, 3 governance/stale plan, 4 artifact integrity.

**Rationale**: dbt overwrites target artifacts per invocation, and concurrent writes can corrupt the evidence boundary. A short bounded lock is cross-platform and sufficient for a local agent workflow.

**Rejected alternatives**:

- Unbounded wait: rejected because agent calls must not hang.
- Process-local mutex: rejected because separate CLI processes would bypass it.
- One global lock: rejected because independent tables/targets should not block each other.

## D13 -- Public Agent Surface

**Decision**: Add one shared `dbt-workflows` skill for Claude and Codex plus four thin Claude wrappers: `dbt-doctor`, `dbt-plan`, `dbt-build`, and `dbt-review`. Codex discovers the shared skill rather than receiving a duplicate slash-command convention.

**Rationale**: This follows the repository's canonical command-surface design: one portable skill contains workflow truth, wrappers only route intent, and generated bundles are deterministic.

**Rejected alternatives**:

- Keep only the internal `.claude/skills/dbt-transformation-adapter`: rejected because installed public plugins cannot refer to development-only paths.
- Duplicate full procedures in every wrapper: rejected because the surfaces would drift.
- Add a dbt command for every low-level CLI action: rejected because the agent workflow should remain smaller than the helper CLI.

## Resolved Unknowns

No planning-time clarification marker remains. Runtime availability is not a design ambiguity:

- Python 3.13 unavailable locally -> `[PENDING LOCAL PYTHON 3.13]`.
- dbt/profile/Postgres unavailable -> `[PENDING LIVE PROFILE]`.
- Public command registry uncommitted in the primary checkout -> integrate only after its owning change is committed.
