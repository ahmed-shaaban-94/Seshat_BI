# Data Model: Activate the Dagster Orchestration MVP (spec 134)

All artifacts are ASCII, UTF-8 without BOM. No entity carries a numeric
health/confidence/maturity score field (hard rule #9); adding one is a schema
violation, not a config choice.

## AssetRecord (one JSONL row per asset outcome; raw, git-ignored)

Written by `tower_bi_orchestration` to `.seshat/dagster/runs/<run-id>/records.jsonl`.

| Field | Type | Rules |
|-------|------|-------|
| `run_id` | string | Dagster run identifier; matches the RunSummary. |
| `asset` | string | One of the 11 asset names (graph order enforced at render). |
| `table` | string | The `<table>` in scope (e.g. `retail_store_sales`). |
| `gate_command` | string | The SAME command CI runs, or `n/a -- <reason>`. Redacted. |
| `exit_code` | integer or null | null only where gate_command is `n/a`. |
| `measured` | object | Measured numbers only (counts, deltas, paths); no adjectives, no scores. |
| `outcome` | enum | `materialized` / `failed` / `skipped` / `blocked` / `deferred`. NEVER `pass`. |
| `blocking_reason` | string or null | REQUIRED (concrete, measured) when outcome is failed/skipped/blocked/deferred. |
| `owner` | string or null | Named owner who can clear it; REQUIRED when blocking_reason is set. |
| `ts` | string | UTC ISO-8601. |

State transitions: an asset reaches exactly one terminal outcome per run.
`failed` upstream forces `skipped` downstream (STOP edge). Absent committed
approval forces `blocked` on the human-seam asset and `skipped` downstream.
Missing DSN forces `blocked` (build assets) or `deferred` (live validate).

## RunSummary (one JSON object per run; raw, git-ignored)

`.seshat/dagster/runs/<run-id>/summary.json`.

| Field | Type | Rules |
|-------|------|-------|
| `run_id` | string | |
| `commit_sha` | string | Repo state the run executed against. |
| `started` / `finished` | string | UTC ISO-8601. |
| `trigger` | enum | `schedule` / `sensor` / `manual-CI`. |
| `tables` | array[string] | Tables in scope. |
| `run_status` | enum | `succeeded` / `failed`. A halted/fail-closed run is `failed` (the CI signal). |

## RunEvidence (committed markdown)

`orchestration/dagster/run-evidence/<run-id>.md`, rendered from AssetRecords +
RunSummary strictly per `templates/dagster-run-evidence.md`: run header table,
per-asset results table (11 rows in graph order + the live validate row),
blocked/skipped table (reason + named owner), and the no-authored-truth
attestation. Rendering REFUSES records that fail schema validation.

## GateState (read-only view; never written)

Produced by `seshat.dagster_adapter.gate` readers.

| Field | Source | Rules |
|-------|--------|-------|
| `table` | `mappings/<table>/` dir name | |
| `gate_status` | `- **Gate status:**` line in `unresolved-questions.md` | `CLEARED` / `OPEN` / `MISSING`. |
| `open_rows` | unresolved-questions open items | integer >= 0. |
| `approvals` | `approvals[]` in `readiness-status.yaml` | list of {stage, owner, date}; read verbatim. |
| `publish_ready` | `readiness-status.yaml` publish stage `status` | read verbatim; only `pass` permits the F016 trigger. |

Writes to any source field are FORBIDDEN in every code path (FR-005).

## DoctorFinding

| Field | Type | Rules |
|-------|------|-------|
| `id` | string | Stable id, e.g. `DAG-ENV-01`. |
| `severity` | enum | `blocker` / `warning` / `info`. No numeric severity. |
| `message` | string | Concrete, measured, redacted. |
| `remedy` | string | The enable step, e.g. the exact install command. |

Doctor exit: any `blocker` -> exit 2; else 0.
