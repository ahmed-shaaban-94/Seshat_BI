# Quickstart: Dagster Orchestration MVP (spec 134)

## One-time setup

```text
# 1. Main package (repo root) -- unchanged
python -m venv .venv && .venv/Scripts/pip install -e ".[dev]"

# 2. Orchestration project (its OWN environment; the main venv stays dagster-free)
cd orchestration/dagster
uv venv .venv
uv pip install -p .venv -e ../.. -e ".[dev]"
cd ../..

# 3. Credentials (optional; live DB steps only)
#    Put DATABASE_URL (or the ANALYTICS_DB_* set) in the git-ignored .env.
#    Without it, DB-touching assets record a deferred boundary / block fail-closed.
```

## Daily loop

```text
seshat dagster doctor                 # preflight: env, pinned pair, gate state per table
seshat dagster run --job through_gold_job --table retail_store_sales
seshat dagster evidence               # list runs
seshat dagster evidence --run-id <id> # render orchestration/dagster/run-evidence/<id>.md
```

A failed gate halts downstream assets and exits 3 (the CI signal); evidence is
still written. The mapping gate (`Gate status: CLEARED`) is READ, never written:
an OPEN gate blocks `silver_tables` with the named owner in the evidence.

## CI smoke (no DB, no secrets)

The workflow installs `orchestration/dagster/` and runs:

```text
python -c "from tower_bi_orchestration.definitions import defs"
dagster definitions validate -m tower_bi_orchestration.definitions
pytest orchestration/dagster/tests -q
```

## What this MVP never does

Write a readiness `status` / `Gate status` / `approvals[]`; publish Power BI
(the terminal asset only TRIGGERS F016 and fails closed while F016 is absent);
enable the shipped schedule/sensor (they default STOPPED; enabling is a named
human action); emit any numeric score.
