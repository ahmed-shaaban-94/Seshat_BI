# Tasks: Activate the Dagster Orchestration MVP (spec 134)

**Input**: spec.md, plan.md, research.md, data-model.md, contracts/ in this directory.
**TDD**: every implementation task is preceded by its failing test task (RED -> GREEN).
**Paths**: repo-root relative (worktree `.worktrees/dagster-mvp`).

## Phase 1: Setup

- [X] T001 Create the orchestration project skeleton: orchestration/dagster/{README.md,pyproject.toml,.gitignore,run-evidence/README.md} with the exact pinned pair dagster==1.13.14 + dagster-dbt==0.29.14 + psycopg2-binary>=2.9 (research D1), package src/tower_bi_orchestration/__init__.py
- [X] T002 Create the orchestration venv and install (uv pip install -p orchestration/dagster/.venv -e . -e orchestration/dagster) proving the pinned pair resolves on Python 3.13; record versions in orchestration/dagster/README.md
- [X] T003 [P] Add the canonical evidence schema at schemas/dagster-run-evidence.schema.json (copy of specs/134-activate-dagster-mvp/contracts/dagster-run-evidence.schema.json)
- [X] T004 [P] Add .seshat/dagster/ to the repo .gitignore run-artifacts area (mirror the existing .seshat/dbt-style ignore posture if present; else add a comment block)

## Phase 2: Foundational (blocking prerequisites)

- [X] T005 Write failing unit tests for the read-only gate readers in tests/unit/dagster_adapter/test_gate.py: CLEARED/OPEN/MISSING gate_status, open-row count, approvals[] read, publish_ready read, and a guard test that gate.py exposes NO write/mutate function
- [X] T006 Implement src/seshat/dagster_adapter/{__init__.py,gate.py} GateState readers over mappings/<table>/ (format per data-model.md; fixtures copied from mappings/retail_store_sales shape)
- [X] T007 [P] Write failing unit tests for redaction in tests/unit/dagster_adapter/test_redaction.py (DSN, host, user, password, profile path, ANALYTICS_DB_* values scrubbed from text and dict payloads)
- [X] T008 [P] Implement src/seshat/dagster_adapter/redaction.py
- [X] T009 [P] Write failing contract test tests/contract/test_dagster_evidence_schema.py: schemas/dagster-run-evidence.schema.json validates a good record set; rejects outcome "pass", rejects numeric score fields via additionalProperties, requires blocking_reason+owner on halted outcomes
- [X] T010 [P] Implement orchestration/dagster/src/tower_bi_orchestration/{repo.py,evidence_writer.py}: repo-root + mapped-table discovery (source-map.yaml scan, research D7) and JSONL AssetRecord/RunSummary appender to .seshat/dagster/runs/<run-id>/ -- with tests in orchestration/dagster/tests/test_evidence_records.py written FIRST (schema-valid rows; halted rows carry reason+owner)

## Phase 3: User Story 1 -- fail-closed run (P1)

- [X] T011 [US1] Write failing test orchestration/dagster/tests/test_fail_closed.py: in-process materialize of the graph over a tmp fixture repo with a forced non-zero gate command -> the asset is failed, every downstream asset is skipped (recorded skipped, not run), the run status is failed, and no readiness file changed (git-diff/hash assertion)
- [X] T012 [US1] Implement orchestration/dagster/src/tower_bi_orchestration/db.py: DSN resolution from env (DATABASE_URL / ANALYTICS_DB_*), deferred-boundary detection, read-only query helper (research D5)
- [X] T013 [US1] Implement the ingest assets in orchestration/dagster/src/tower_bi_orchestration/assets/ingest.py: raw_source_file, bronze_<table> (blocked with "no database credentials (deferred boundary)" when DSN absent), source_profile
- [X] T014 [US1] Implement the gate assets in orchestration/dagster/src/tower_bi_orchestration/assets/gates.py: silver_tables + gold_tables (apply warehouse/migrations/*.sql for the table then run the packaged checker with the SAME command CI runs; raise dagster.Failure on non-zero), plus the live validate step recording deferred without creds
- [X] T015 [US1] Implement orchestration/dagster/src/tower_bi_orchestration/{jobs.py,definitions.py}: full_sequence_job, through_gold_job, per-table asset groups from repo.py discovery; make test_fail_closed.py GREEN

## Phase 4: User Story 2 -- human seams read, never write (P1)

- [X] T016 [US2] Write failing test orchestration/dagster/tests/test_human_seam.py: fixture with Gate status OPEN -> source_map blocked, silver_tables skipped, blocker + named owner recorded, no file under mappings/ modified; CLEARED fixture -> silver permitted; publish_ready != pass -> publish asset blocked; publish_ready == pass -> publish asset FAILS CLOSED with blocking_reason "F016 publish adapter not available"
- [X] T017 [US2] Implement source_map HUMAN-SEAM asset in assets/gates.py using seshat.dagster_adapter.gate readers (research D4)
- [X] T018 [US2] Implement the downstream assets in orchestration/dagster/src/tower_bi_orchestration/assets/downstream.py: metric_contracts (read-only), semantic_model (check + approval read), dashboard_blueprint, handoff_pack, publish_execution_evidence (publish wall); make test_human_seam.py GREEN

## Phase 5: User Story 3 -- derived evidence rendering (P1)

- [X] T019 [US3] Write failing unit tests tests/unit/dagster_adapter/test_evidence.py: schema validation refusal on bad records; deterministic rendering of templates/dagster-run-evidence.md sections (run header, 11-row per-asset table + live validate row, blocked/skipped table, no-authored-truth attestation); rendering twice is byte-identical
- [X] T020 [US3] Implement src/seshat/dagster_adapter/evidence.py (validate + render to orchestration/dagster/run-evidence/<run-id>.md); make T019 GREEN
- [X] T021 [US3] Extend orchestration/dagster/tests/test_evidence_records.py: a green in-process run writes records.jsonl + summary.json that pass the canonical schema end-to-end

## Phase 6: User Story 4 -- doctor + CLI family (P2)

- [X] T022 [US4] Write failing unit tests tests/unit/dagster_adapter/test_doctor.py: findings for missing orchestration project/venv, pinned-pair mismatch, gate state per table, DSN absent = warning not blocker; blocker -> exit 2 semantics
- [X] T023 [US4] Implement src/seshat/dagster_adapter/doctor.py; make T022 GREEN
- [X] T024 [US4] Write failing unit tests tests/unit/dagster_adapter/test_runner.py: closed argv construction (orch venv python -m dagster job execute -m tower_bi_orchestration.definitions -j <job>), no shell, rejects raw pass-through args, child failure -> exit 3 mapping, output redacted
- [X] T025 [US4] Implement src/seshat/dagster_adapter/runner.py; make T024 GREEN
- [X] T026 [US4] Write failing CLI tests tests/unit/test_cli_dagster.py: seshat dagster doctor/run/evidence registered lazily (no dagster import on seshat startup -- extend the existing import-guard pattern), exit codes 0..4 per contracts/dagster-cli.md, --json shapes
- [X] T027 [US4] Implement the CLI family following the existing lazy nested-group registration pattern in src/seshat/cli/ (new src/seshat/cli/commands/dagster.py + the parser/dispatch touchpoints the pattern requires); make T026 GREEN

## Phase 7: User Story 5 -- agent surface (P2)

- [X] T028 [P] [US5] Update .claude/skills/dagster-orchestration-adapter/SKILL.md: replace the "NOT created yet" seam note with the operational doctor/run/evidence procedure + two-venv setup; authority-boundary text unchanged
- [X] T029 [US5] Add dagster-doctor, dagster-run, dagster-evidence to distribution/public-command-surface.yaml following the file's own add-a-command recipe
- [X] T030 [US5] Create distribution/bundle-templates/claude/commands/{dagster-doctor,dagster-run,dagster-evidence}.md and regenerate integrations/ trees with the repo's canonical bundle-regeneration procedure; run the bundle-equality contract test and record its baseline state (pre-existing failure on this worktree must not worsen)
- [X] T031 [P] [US5] Update docs/capabilities/capabilities.yaml: dagster-orchestration-adapter entry gains the runtime claim (locally-verified) + command references; add CLI command entries per the file's existing shape
- [X] T032 [P] [US5] Update docs/integrations/dagster-adapter.md: PLANNED sections -> BUILT (project shape as shipped), add the dagster-dbt engine seam subsection (research D10)

## Phase 8: User Story 6 -- automations shipped STOPPED + CI smoke (P3)

- [X] T033 [US6] Extend orchestration/dagster/tests/test_definitions_load.py (write FIRST): defs load with 11 assets per discovered table, both jobs, exactly one schedule and one sensor BOTH default_status STOPPED
- [X] T034 [US6] Implement orchestration/dagster/src/tower_bi_orchestration/{schedules.py,sensors.py} (daily schedule on full_sequence_job; file-arrival sensor on the configured landing dir; both STOPPED); make T033 GREEN
- [X] T035 [US6] Add .github/workflows/dagster-smoke.yml: checkout, Python 3.13, install orchestration project (own venv) + repo root, python -c import defs, dagster definitions validate, pytest orchestration/dagster/tests -q; no DB service, no secrets (research D6)

## Phase 9: Polish and verification

- [X] T036 [P] Fill orchestration/dagster/README.md fully: setup (quickstart.md content), human seams, evidence flow, dagster dev note, auto-update posture (pin pair, PR-only, no automerge majors)
- [X] T037 Run the full verification set and fix findings: .venv/Scripts/python -m pytest -q (zero NEW failures vs the 2026-07-17 baseline of 9), ruff format --check + ruff check, the packaged checker (seshat check), and the CodeScene delta gate on changed files
- [X] T038 Reconcile specs/134-activate-dagster-mvp/checklists/requirements.md and mark tasks complete; confirm SC-001..SC-007 each have evidence

## Dependencies

- Phase 1 -> Phase 2 -> US1 (T011-T015) -> US2 (T016-T018) -> US3 (T019-T021)
- US4 (T022-T027) depends on Phase 2 + US3 (evidence.py used by the run verb)
- US5 (T028-T032) depends on US4 (commands must exist before surfacing them)
- US6 (T033-T035) depends on US1 definitions; independent of US4/US5
- Phase 9 last.

## Parallel opportunities

- T003/T004 with T001-T002; T005-T010 pairs across different files; T028/T031/T032
  while T029-T030 run sequentially (same registry); orchestration tests vs main-suite
  tests touch disjoint trees throughout.

## MVP scope note

US1+US2+US3 (fail-closed graph + seams + evidence) is the governed core; US4-US6
make it operable and public. All are in scope for this slice per the approved design.
