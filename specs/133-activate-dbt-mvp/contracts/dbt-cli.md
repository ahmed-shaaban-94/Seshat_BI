# CLI Contract: `seshat dbt`

The nested `dbt` family is a helper surface. The agent workflow remains the product interface. All commands accept `--repo` (default `.`) and `--format text|json` (default `text`) unless noted.

## Stable Commands

### `seshat dbt doctor`

Read-only checks:

1. Python is 3.13 or newer.
2. `seshat-bi[dbt]` exact versions are installed.
3. The current environment contains the dbt executable.
4. `dbt/`, `dbt_project.yml`, `selectors.yml`, root `profiles.example.yml`, ignore rules, and evidence schema exist.
5. A local `profiles.yml`, when present, is ignored and contains only `env_var()` references.
6. Required `.env` keys are present without printing values.

No table and no database connection are required. Exit 0 means checks completed and no blocker was found; exit 2 means prerequisites are unavailable.

### `seshat dbt validate --table <table>`

Read-only static validation of one working set, mapping gate, project, selector declaration, shadow schemas, and model citations. It invokes no database query. Exit 3 is a governance refusal; exit 2 is unavailable tooling; exit 0 means the static validation completed.

### `seshat dbt plan --table <table>`

Runs non-DB dbt parse/list, validates manifest v12, resolves exact node IDs, writes `.seshat/dbt/plans/<table>-shadow.json`, and returns the canonical plan plus its SHA-256 digest.

Text output ends with:

```text
accept_plan: <64-lowercase-hex>
next: seshat dbt build --table <table> --accept-plan <64-lowercase-hex>
```

JSON output:

```json
{"digest":"<64-lowercase-hex>","plan":{"schema_version":1}}
```

The actual `plan` is complete and validates against `dbt-execution-plan.schema.json`.

### `seshat dbt build --table <table> --accept-plan <digest>`

Recomputes the plan before database access, requires an exact digest match, acquires the table/target lock, and runs fixed argv equivalent to:

```text
dbt build --select selector:seshat_table_<table> --target shadow --no-use-colors --log-format json
```

Seshat supplies fixed project, profiles, target, log, and target-path arguments. Users cannot override or append dbt arguments. After valid build artifacts, Seshat invokes the fixed governed parity audit with `dbt show`, writes normalized evidence, prints its repository-relative path, and stops for named-human approval.

### `seshat dbt test --table <table> --accept-plan <digest>`

Uses the same replan, digest, selector, target, lock, artifact, parity, and evidence boundaries as `build`, with fixed operation `dbt test`. It never changes readiness status.

### `seshat dbt inspect-run --table <table> --artifacts <directory>`

Reads an existing local artifact directory, validates supported manifest/run-results shape and selected node IDs, sanitizes findings, and writes or prints normalized evidence. The artifact directory must resolve inside `.seshat/dbt/runs/`; arbitrary external paths are rejected. It never connects to a database.

## Common JSON Result

Non-plan commands return one JSON object:

```json
{
  "command": "validate",
  "table_id": "retail_store_sales",
  "outcome": "pass",
  "exit_code": 0,
  "message": "static dbt validation completed",
  "evidence_path": null,
  "blocking_reasons": []
}
```

`message` and blocker messages are sanitized. No raw stdout, stderr, host, user, password, database name, DSN, home directory, or absolute repository path appears.

## Exit Codes

| Exit | Stable meaning |
|---|---|
| `0` | Requested command completed; for dbt runs this is derived evidence, never readiness approval. |
| `1` | dbt completed with handled model/test/parity failure. |
| `2` | Usage error or Python/dbt/profile/database prerequisite unavailable. |
| `3` | Governance refusal, unsafe project/profile, or accepted-plan drift. |
| `4` | Artifact or normalized-evidence integrity failure. |

Expected failures print no traceback.

## Forbidden Arguments

The parser exposes none of these:

- raw `--select`, `--selector`, `--exclude`, or `--models`;
- raw `--target`, `--profile`, `--profiles-dir`, `--project-dir`, or schema override;
- `--vars`, `--full-refresh`, `--threads`, `--state`, `--defer`, or arbitrary dbt flags;
- inline SQL, macros, or `run-operation` arguments;
- Power BI execution or readiness-stage mutation flags.
