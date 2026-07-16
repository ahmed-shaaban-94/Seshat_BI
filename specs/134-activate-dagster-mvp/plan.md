# Activate the Dagster Orchestration MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to
> implement this plan task-by-task. Every implementation task follows
> `superpowers:test-driven-development`; completion claims follow
> `superpowers:verification-before-completion`.

**Branch**: `134-activate-dagster-mvp` | **Date**: 2026-07-17 | **Spec**: [spec.md](./spec.md)

**Goal:** Ship the unattended/CI orchestration runtime spec 024 (F030) enumerated:
a real `orchestration/dagster/` project running the 11-asset medallion graph
behind every gate, a `seshat dagster` control layer, portable agent surfaces,
paused automations, and derived run-evidence -- without Dagster ever becoming
readiness authority.

**Architecture:** The orchestration project (`tower_bi_orchestration`, its own
venv, `dagster==1.13.14` + `dagster-dbt==0.29.14` pinned together) discovers
mapped tables from `mappings/<table>/`, executes approved steps behind STOP /
HUMAN-SEAM edges, and appends raw JSONL evidence per asset. The lazy
`seshat dagster` family (doctor/run/evidence) preflights gates read-only,
launches the runtime as a shell-free child process with closed argv, validates
records against a JSON schema, and renders the committed run-evidence markdown
per `templates/dagster-run-evidence.md`. Gate readers live once, in
`seshat.dagster_adapter.gate`, imported by both sides (research D4).

**Tech Stack:** Python 3.13, stdlib + existing PyYAML, argparse, pytest;
dagster 1.13.14 + dagster-dbt 0.29.14 + psycopg2-binary (orchestration venv
ONLY); JSON Schema; GitHub Actions; Claude/Codex plugin bundles.

## Global Constraints

- The main `seshat` package gains NO dagster dependency; the static core import
  path stays stdlib-only (existing B1/B3 guard posture).
- The pinned pair is exactly `dagster==1.13.14` + `dagster-dbt==0.29.14`,
  together, in `orchestration/dagster/pyproject.toml` only.
- Fail-closed everywhere: failed gate -> asset failed -> downstream skipped ->
  run failed (exit 3, the CI signal). No run-around of a STOP edge.
- Human-seam reads only: `Gate status`, `approvals[]`, `publish_ready` are READ;
  no code path writes readiness `status`, `Gate status`, `approvals[]`, a
  metric/mapping/grain/PII definition, or a Power BI publish.
- The publish asset only TRIGGERS F016 and FAILS CLOSED while F016 is absent.
- Missing DSN: build assets block (deferred boundary named in the reason); live
  validate records `deferred`; nothing fabricates success. Read-only validation.
- Evidence outcomes are execution words (`materialized|failed|skipped|blocked|deferred`),
  never `pass`; no numeric health/confidence/maturity score anywhere.
- Schedule + sensor ship `default_status=STOPPED`; enabling is a named-human act.
- Secrets only in the git-ignored `.env`; every surfaced error is redacted
  (DSN/host/user/password/paths).
- `warehouse/migrations/` is the build path this slice; `dagster-dbt` is a
  documented seam (research D10) -- no code touches spec-133 modules.
- ASCII, UTF-8 without BOM; short repo-relative paths (Windows MAX_PATH).
- `retail_store_sales` is the filled instance, never the generic schema
  (Principle VII); `demo_sample_orders` proves table discovery is generic.

## Summary

Feature 134 activates the runtime that feature 024 deliberately left planned:
one vertical slice -- orchestration project + control layer + CLI + skill/
commands/bundles + capabilities claim + CI smoke + paused automations + tests +
reconciled docs. The canonical `distribution/public-command-surface.yaml`
registry (PR #297, on main) is consumed, never recreated.

## Technical Context

**Language/Version**: Python 3.13 exactly (repo floor); YAML/JSON Schema; GitHub Actions YAML.

**Primary Dependencies**: main package unchanged (`pyyaml>=6`); orchestration
venv: `dagster==1.13.14`, `dagster-dbt==0.29.14`, `psycopg2-binary>=2.9`,
`seshat-bi` (repo root, editable).

**Storage**: committed mappings + run-evidence markdown; git-ignored
`.seshat/dagster/runs/<run-id>/` raw records; PostgreSQL only at the live boundary.

**Testing**: pytest (unit/contract in main suite; orchestration tests in its own
tree, runnable in CI with the orchestration venv); Ruff; `retail check`;
bundle-regeneration equality; secret scan. Baseline on this worktree:
2644 passed / 9 pre-existing failures (recorded 2026-07-17); the gate is zero
NEW failures.

**Target Platform**: Windows/macOS/Linux dev installs; Linux CI runner (no DB, no secrets).

**Project Type**: Python CLI/library + a separate orchestration Python project +
generated agent plugin bundles.

**Performance Goals**: doctor and evidence are linear in mapped tables /
recorded assets; run cost is the underlying gate commands.

**Constraints**: stable exit codes 0..4; no raw traceback in default output;
records schema-validated before render; deterministic evidence rendering.

**Scale/Scope**: one orchestration package (11 assets, 2 jobs, 1 schedule,
1 sensor), one control layer (4 modules), one CLI family (3 verbs), 3 Claude
wrappers + shared skill update, 1 CI workflow, ~10 test modules.

## Constitution Check

*GATE: Passed before research and re-checked after design.*

| Principle | Design proof | Status |
|---|---|---|
| I -- Agent-first, gate-enforced | Assets run the SAME gate commands CI runs; asset success = exit code evidence; the checker/named human remain sole pass authority. | PASS |
| II -- Depend, never fork | Dagster consumed as pinned external dependency in an isolated project; no fork, no vendoring; publish stays behind the F016 trigger. | PASS |
| III -- Medallion, gold-only | The graph sequences bronze->silver->gold; no Power BI read of silver/bronze; Postgres-only this slice. | PASS |
| IV -- Mapping before silver | `source_map` HUMAN-SEAM asset blocks `silver_tables` until `Gate status: CLEARED` + zero open rows; reader never writes. | PASS |
| V -- Stop at judgment calls | Judgment calls halt the affected asset and record owner + reason; schedule/sensor STOPPED; approvals never self-granted. | PASS |
| VI -- Defaults then deviations | Executes committed migrations/defaults; defines nothing new. | PASS |
| VII -- Example, not schema | Table discovery is generic (mappings scan); retail_store_sales is the filled instance; no specifics in generic code. | PASS |
| VIII -- Static-first, live deferred | Definitions-load smoke + fixture tests need no DB; live steps record deferred boundaries without creds. | PASS |
| IX -- Secrets and reproducibility | `.env`-only credentials, redaction module, exact version pins, ASCII/UTF-8-no-BOM, short paths. | PASS |

**Post-design re-check:** PASS. The two-venv boundary (research D4) strengthens
Principle II/VIII; evidence-only semantics unchanged from spec 024.

## Project Structure

### Documentation for Feature 134

```text
specs/134-activate-dagster-mvp/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- dagster-cli.md
|   `-- dagster-run-evidence.schema.json
|-- checklists/requirements.md
`-- tasks.md
```

### Orchestration project

```text
orchestration/dagster/
|-- README.md                          # run/setup, human seams, gate-read posture, dagster-dbt seam pointer
|-- pyproject.toml                     # tower-bi-orchestration; the pinned pair; psycopg2; seshat-bi editable dep documented
|-- .gitignore                         # .venv/, local dagster artifacts
|-- src/tower_bi_orchestration/
|   |-- __init__.py
|   |-- definitions.py                 # Definitions: discovered per-table asset groups, jobs, schedule, sensor
|   |-- repo.py                        # repo-root/table discovery (mappings/<table>/source-map.yaml scan)
|   |-- evidence_writer.py             # JSONL AssetRecord/RunSummary appender (.seshat/dagster/runs/<run-id>/)
|   |-- db.py                          # DSN resolution from env; read-only helpers; deferred-boundary detection
|   |-- assets/
|   |   |-- __init__.py
|   |   |-- ingest.py                  # raw_source_file, bronze_<table>, source_profile
|   |   |-- gates.py                   # source_map (HUMAN SEAM), silver_tables, gold_tables, live validate step
|   |   `-- downstream.py              # metric_contracts, semantic_model, dashboard_blueprint, handoff_pack, publish_execution_evidence
|   |-- jobs.py                        # full_sequence_job, through_gold_job
|   |-- schedules.py                   # daily schedule, default_status=STOPPED
|   `-- sensors.py                     # file-arrival sensor, default_status=STOPPED
|-- run-evidence/README.md             # what a committed <run-id>.md is; template pointer
`-- tests/
    |-- test_definitions_load.py       # SC-001 smoke (11 assets, jobs, stopped automations)
    |-- test_fail_closed.py            # US1 in-process materialize with forced failure
    |-- test_human_seam.py             # US2 OPEN blocks silver; CLEARED permits; no writes
    `-- test_evidence_records.py       # US3 records written, schema-valid, no readiness diffs
```

### Control layer, CLI, schema

```text
src/seshat/dagster_adapter/
|-- __init__.py                        # constants only; imports no dagster
|-- gate.py                            # GateState readers (Gate status, open rows, approvals[], publish_ready) -- READ-ONLY
|-- doctor.py                          # DoctorFindings (env, project, pinned pair, gate state, DSN presence)
|-- runner.py                          # closed-argv child process (orch venv python -m dagster job execute ...)
|-- redaction.py                       # DSN/host/user/password/path scrubber for all surfaced text
`-- evidence.py                        # schema validation + deterministic template rendering

src/seshat/cli/  (follow the existing registration pattern for a lazy nested group)
|-- commands/dagster.py                # text/JSON presentation + exit mapping 0..4
`-- (parser/dispatch touchpoints per the existing dbt-family precedent)

schemas/dagster-run-evidence.schema.json   # canonical copy of the contract schema

tests/
|-- unit/dagster_adapter/{test_gate.py,test_doctor.py,test_runner.py,test_redaction.py,test_evidence.py}
|-- unit/test_cli_dagster.py
`-- contract/test_dagster_evidence_schema.py
```

### Public agent surface + automations

```text
distribution/public-command-surface.yaml                 # + dagster-doctor, dagster-run, dagster-evidence
distribution/bundle-templates/claude/commands/{dagster-doctor,dagster-run,dagster-evidence}.md
integrations/claude-code/seshat-bi/commands/{dagster-doctor,dagster-run,dagster-evidence}.md
.claude/skills/dagster-orchestration-adapter/SKILL.md    # seam note -> operational procedure
docs/capabilities/capabilities.yaml                      # runtime claim (locally-verified) + command refs
docs/integrations/dagster-adapter.md                     # PLANNED -> BUILT sections; dagster-dbt engine seam
.github/workflows/dagster-smoke.yml                      # definitions-load smoke + orchestration tests (no DB/secrets)
.gitignore                                               # .seshat/dagster/ runs area
```

**Structure Decision**: hybrid layout per the user's 2026-07-17 decision --
the enumerated `orchestration/dagster/` project (spec 024 shape) plus the
`src/seshat/dagster_adapter/` control layer mirroring the spec-133 dbt family.
Follow the existing CLI registration pattern found in `src/seshat/cli/` at
implementation time (the dbt worktree's exact file split is NOT assumed here;
this branch reads its own tree).

## Complexity Tracking

No constitution violations to justify. The only structural addition beyond the
dbt-sibling pattern is the second virtual environment (orchestration project),
required by Principle II/VIII to keep dagster out of the main package; rejected
simpler alternative (dagster as a main-package extra) would put a heavy,
fast-moving framework on the governed import path.
