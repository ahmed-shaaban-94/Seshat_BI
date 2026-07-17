# Quickstart: Governed dbt MVP

This quickstart demonstrates the intended feature after implementation. It does not grant a readiness or build-path approval.

## 1. Verify Local Prerequisites

From the feature worktree with Python 3.13 available:

```powershell
python --version
python -m pip install -e ".[dev,dbt]"
seshat dbt doctor --format json
```

Expected version evidence:

```text
Python 3.13+
dbt-core 1.12.0
dbt-postgres 1.10.2
```

If Python is missing, report `[PENDING LOCAL PYTHON 3.13]`. If the dbt extra is missing, doctor returns exit 2 and recommends `python -m pip install -e ".[dbt]"`; it does not traceback.

## 2. Confirm the Approved Working Set

```powershell
seshat dbt validate --table retail_store_sales --format json
```

This reads:

- `mappings/retail_store_sales/readiness-status.yaml`;
- `mappings/retail_store_sales/unresolved-questions.md`;
- `mappings/retail_store_sales/source-map.yaml`;
- model properties and citations under `dbt/models/`.

It must invoke no database query. A blocked mapping returns exit 3 with a concrete reason.

## 3. Configure a Local Profile Safely

Copy the committed environment-reference profile:

```powershell
Copy-Item -LiteralPath profiles.example.yml -Destination profiles.yml
```

Do not replace its `env_var()` expressions with literal connection values. Put real values only in the ignored `.env`:

```dotenv
SESHAT_DBT_HOST=<local-or-approved-host>
SESHAT_DBT_PORT=5432
SESHAT_DBT_USER=<approved-user>
SESHAT_DBT_PASSWORD=<secret>
SESHAT_DBT_DBNAME=<approved-database>
SESHAT_DBT_SCHEMA=seshat_dbt_shadow
SESHAT_DBT_SSLMODE=prefer
```

Never commit `.env` or `profiles.yml`. Confirm both are ignored:

```powershell
git check-ignore .env profiles.yml
```

## 4. Create and Review the Immutable Plan

```powershell
seshat dbt plan --table retail_store_sales --format json
```

Review the table, mapping blob, project fingerprint, dbt versions, selected unique IDs, target, and shadow schemas. Copy the returned digest only after those facts are acceptable.

Planning uses dbt parse/list and must not query PostgreSQL.

## 5. Run the Governed Shadow Build

```powershell
seshat dbt build --table retail_store_sales --accept-plan <digest> --format json
```

The command must:

1. recompute the plan and reject any drift before DB access;
2. build only selector `seshat_table_retail_store_sales`;
3. materialize only `seshat_dbt_shadow_silver`, `seshat_dbt_shadow_gold`, and `seshat_dbt_shadow_audit`;
4. validate manifest and run-results artifacts;
5. collect the fixed parity audit through machine-readable `dbt show`;
6. write normalized evidence under `mappings/retail_store_sales/dbt-evidence/`;
7. leave all readiness statuses and migration ownership unchanged.

If no governed DSN is available, stop here with `[PENDING LIVE PROFILE]`.

## 6. Review Evidence

```powershell
seshat dbt inspect-run --table retail_store_sales --artifacts .seshat/dbt/runs/<invocation-id> --format json
```

The committed record must conform to `schemas/dbt-run-evidence.schema.json`, include all eight parity assertions, contain artifact hashes, and contain no raw logs or secrets.

Passing evidence permits only this recommendation:

```text
dbt shadow parity passed. Migrations remain the default. A named human may review a build-path switch; Seshat has not approved one.
```

## 7. Run Verification

Static and package checks:

```powershell
python -m pytest -m "unit or integration" -q
python -m ruff check src tests
python -m seshat.cli check --repo .
python scripts/export_agent_bundles.py --check
git diff --check
git status --short
```

Pinned dbt project checks:

```powershell
dbt parse --project-dir dbt --profiles-dir . --target shadow --no-partial-parse
dbt compile --project-dir dbt --profiles-dir . --target shadow --select selector:seshat_table_retail_store_sales
```

Optional live Postgres checks require the repository's live-test prerequisites:

```powershell
python -m pip install -e ".[dev,dbt,db,livetest]"
python -m pytest tests/live_db/test_dbt_retail_store_sales.py -m live_db -v
```

Unavailable Docker/Postgres remains `[PENDING LIVE PROFILE]`; it is never reported as passing.
