# Contract: the `seshat dagster` CLI family (spec 134)

Lazy-loaded nested group. No verb imports `dagster`; the runtime is always a
child process in the orchestration project's own environment. All output is
redacted (no DSN/host/user/password/profile path ever surfaces). Exit codes are
stable API:

| Exit | Meaning |
|------|---------|
| 0 | Success. |
| 1 | Usage error (unknown verb/flag). |
| 2 | Preflight/gate refusal: doctor blockers, gate not CLEARED, missing prerequisite. |
| 3 | Run failed / fail-closed halt (the CI signal). |
| 4 | Unexpected internal error (redacted; no raw traceback in default output). |

## `seshat dagster doctor [--json]`

Read-only preflight. Reports DoctorFindings: orchestration project present;
orchestration venv present + importable definitions; pinned pair versions
consistent (`dagster==1.13.14`/`dagster-dbt==0.29.14`); per-table GateState
(gate_status, open_rows); DSN presence (reported as present/absent only --
value never echoed). Any `blocker` finding -> exit 2, else 0. Absent DSN alone
is a `warning` (deferred boundary), not a blocker.

## `seshat dagster run --job <full_sequence_job|through_gold_job> [--table <table>] [--json]`

1. Runs the doctor preflight; any blocker -> exit 2 (nothing executed).
2. Launches the closed-argv child process:
   `<orch-python> -m dagster job execute -m tower_bi_orchestration.definitions -j <job>`
   (plus an asset selection when `--table` is given). No shell. No raw
   pass-through arguments of any kind.
3. On child exit, validates `.seshat/dagster/runs/<run-id>/records.jsonl`
   against `schemas/dagster-run-evidence.schema.json` and renders
   `orchestration/dagster/run-evidence/<run-id>.md`.
4. Exit 0 when run_status is `succeeded`; exit 3 when `failed` (fail-closed
   halt or gate failure) -- evidence is rendered in BOTH cases.

## `seshat dagster evidence [--run-id <id>] [--json]`

Without `--run-id`: lists known runs (id, status, started, tables). With
`--run-id`: validates the raw records and renders/re-renders the committed
markdown; prints its path. Refuses (exit 2) when records fail schema
validation. Never mutates raw records; rendering is deterministic.

## Forbidden in every verb

Writing any readiness `status`, `Gate status`, `approvals[]`; accepting raw
dagster arguments, selectors, or config overrides; echoing secrets; emitting
any numeric health/confidence/maturity score.
