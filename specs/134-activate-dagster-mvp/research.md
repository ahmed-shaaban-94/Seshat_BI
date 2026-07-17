# Research: Activate the Dagster Orchestration MVP (spec 134)

All Technical Context unknowns resolved. Format per speckit-plan Phase 0.

## D1 -- The pinned dagster / dagster-dbt pair

- **Decision**: `dagster==1.13.14` + `dagster-dbt==0.29.14`, pinned exactly and
  together in `orchestration/dagster/pyproject.toml`.
- **Rationale**: measured from PyPI 2026-07-17: dagster 1.13.14 requires
  `>=3.10,<3.15` (Python 3.13 OK); dagster-dbt 0.29.14 requires `>=3.10,<3.14`
  (3.13 OK) and hard-pins `dagster==1.13.14` -- the libraries release in
  lockstep, so pinning the pair IS the upstream contract. Installing dagster-dbt
  now (even while the dbt integration is a seam) proves the pinned pair loads
  together, which is exactly what the FR-009/spec-024 definitions-load smoke
  must catch on future bumps.
- **Alternatives considered**: floating minor ranges (rejected: spec 024
  auto-update posture forbids independent bumps); omitting dagster-dbt until
  spec 133 merges (rejected: the pair-pin and the version-skew smoke are spec
  024 commitments independent of dbt adoption).

## D2 -- Execution mechanism

- **Decision**: `seshat dagster run` launches the orchestration venv's
  interpreter as a child process with a CLOSED argv (no shell):
  `<orch-venv-python> -m dagster job execute -m tower_bi_orchestration.definitions
  -j <job>`; ephemeral Dagster instance (no DAGSTER_HOME, no daemon).
- **Rationale**: mirrors the spec-133 runner posture (child process, closed
  argument set, durable artifacts over in-process objects). An ephemeral
  instance needs no daemon; schedules/sensors ship STOPPED so nothing requires
  a long-lived process this slice.
- **Alternatives considered**: in-process `materialize()` from seshat
  (rejected: would force dagster into the main package environment, breaking
  the stdlib-only static core); `dagster dev` webserver (rejected: interactive
  surface, out of MVP scope -- documented in the README as optional local UI).

## D3 -- Evidence capture

- **Decision**: assets append structured JSONL records (one per asset outcome)
  to `.seshat/dagster/runs/<run-id>/records.jsonl` (git-ignored) via a tiny
  writer inside `tower_bi_orchestration`; `seshat dagster evidence` validates
  the records against `schemas/dagster-run-evidence.schema.json` and renders
  the committed `orchestration/dagster/run-evidence/<run-id>.md` per
  `templates/dagster-run-evidence.md`.
- **Rationale**: rendering lives in the control layer (testable without dagster
  installed); the raw facts are written by the code that measured them.
  Parsing Dagster's internal event log was rejected as version-fragile --
  the same reason spec 133 consumes dbt's JSON artifacts, not dbtRunner objects.
- **Alternatives considered**: Dagster sensors/hooks writing the md directly
  (rejected: couples the template rendering to the dagster API surface);
  parsing `dagster job execute` stdout (rejected: not a stable contract).

## D4 -- Gate-read implementation and the two-venv boundary

- **Decision**: the read-only gate readers (Gate status: `- **Gate status:**`
  line + open-row count from `unresolved-questions.md`; `approvals[]` +
  `publish_ready` from `readiness-status.yaml`) live in
  `src/seshat/dagster_adapter/gate.py`. The orchestration venv installs the
  repo root editable (`uv pip install -e ../.. -e .`), so
  `tower_bi_orchestration` imports the SAME reader; `seshat dagster doctor`
  uses it too and works when the orchestration venv is absent.
- **Rationale**: one tested implementation of the most safety-critical read;
  the dependency direction (orchestration -> seshat) matches the authority
  direction (Seshat is the brain, Dagster the runner).
- **Alternatives considered**: duplicate readers per venv (rejected: two
  sources of truth for a human-seam read); orchestration as a dependency of
  seshat (rejected: main package must stay dagster-free).

## D5 -- DB boundary in assets

- **Decision**: DB-touching assets (bronze load, silver/gold migration apply,
  live validate) read the DSN from env (`DATABASE_URL` / `ANALYTICS_DB_*`,
  git-ignored `.env`). Missing DSN: build assets fail closed with
  `blocking_reason` "no database credentials (deferred boundary)"; the live
  validate step records outcome `deferred` and never marks anything. psycopg2
  is a dependency of the ORCHESTRATION project only. Validation connections are
  read-only.
- **Rationale**: FR-007 + spec 024 edge case; the main package keeps its
  optional `db` extra unchanged.

## D6 -- Definitions-load smoke (CI)

- **Decision**: CI job installs the orchestration project (its own venv),
  then runs BOTH `python -c "from tower_bi_orchestration.definitions import
  defs"` (version-stable) and `dagster definitions validate -m
  tower_bi_orchestration.definitions`, then the orchestration unit tests.
  No DB, no secrets.
- **Rationale**: the import assert is stable across dagster versions; the
  validate command adds the deeper structural check while it exists.

## D7 -- Table discovery and the job set

- **Decision**: definitions discover tables by scanning `mappings/<table>/`
  for a `source-map.yaml` at load time (repo root located relative to the
  package). Jobs: `full_sequence_job` (all 11 assets) and `through_gold_job`
  (assets 1-6 + live validate step). `retail_store_sales` (Gate status:
  CLEARED on main) is the filled first instance; `demo_sample_orders` also
  resolves, proving genericity.
- **Rationale**: no per-table code, Principle VII; the graph shape stays the
  spec-024 shape.

## D8 -- Automations shipped STOPPED

- **Decision**: `ScheduleDefinition(..., default_status=STOPPED)` daily on
  `full_sequence_job`; one `@sensor(default_status=STOPPED)` watching the
  configured raw-landing directory for new files. Enabling either is a
  named-human action (out of scope).
- **Rationale**: FR-013; fail-closed posture (Principle V).

## D9 -- CLI exit codes

- **Decision**: stable exit codes mirroring the spec-133 family: `0` success;
  `1` usage error; `2` preflight/gate refusal (doctor findings, gate not
  CLEARED); `3` run failed / fail-closed halt (the CI signal); `4` unexpected
  internal error (redacted).
- **Rationale**: agents and CI need stable, documented semantics; consistency
  with the dbt sibling keeps the public surface learnable.

## D10 -- dagster-dbt seam (documentation only this slice)

- **Decision**: `docs/integrations/dagster-adapter.md` gains an "engine seam"
  subsection: where `silver_tables`/`gold_tables` switch from SQL-migration
  execution to `dagster-dbt` assets after spec 133 merges, with IDENTICAL gate
  semantics. No code references spec-133 modules.
- **Rationale**: zero coupling between unmerged branches (user decision
  2026-07-17); spec 024 explicitly blesses either engine behind the same gates.
