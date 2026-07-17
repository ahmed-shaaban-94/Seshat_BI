# Feature Specification: Activate the Dagster Orchestration MVP

**Feature Branch**: `134-activate-dagster-mvp`

**Created**: 2026-07-17

**Status**: Approved for planning

**Roadmap identity**: Activates the runtime build slice planned by F030 / on-disk
spec `024-dagster-orchestration-adapter`. Spec 024 remains the historical planning
record and the authority-boundary text; this spec owns the runnable orchestration
project, the Python control layer, the public agent surface, the automations, and
the evidence implementation.

**Input**: User description: "Activate the Dagster Orchestration MVP: turn the
shipped Dagster advisory seam (spec 024 / F030) into the real unattended/CI
runtime. Full 11-asset graph in orchestration/dagster/ (package
tower_bi_orchestration, dagster+dagster-dbt pinned together), silver/gold via
existing warehouse/migrations SQL with a documented dagster-dbt seam for after
spec-133 merges, src/seshat/dagster_adapter/ control layer with lazy
seshat dagster doctor/run/evidence CLI, updated dagster-orchestration-adapter
skill, dagster-doctor/run/evidence slash commands in
distribution/public-command-surface.yaml + regenerated bundles, capabilities.yaml
runtime claim, CI definitions-load smoke workflow, one daily schedule + one
file-arrival sensor shipped STOPPED. Fail-closed everywhere; run-evidence per
templates/dagster-run-evidence.md; no readiness status/approval writes; no
numeric scores. Design doc:
docs/superpowers/specs/2026-07-17-dagster-mvp-activation-design.md."

## Purpose and Readiness Stage

This feature turns the shipped Dagster advisory seam into a real, governed
unattended/CI runtime for the medallion sequence. Dagster remains the runner and
Seshat BI remains the readiness authority: the gate exit code and the named human
decide every stage; Dagster sequences all seven readiness stages and DECIDES none.

The adapter is Execution Adapter / `DB-connected` (F024 category, unchanged from
spec 024). It reads committed approvals as its only GO signal, executes approved
steps behind STOP / HUMAN-SEAM edges, writes derived run-evidence, and fails
closed at every gate -- including the publish wall, where it can only TRIGGER the
parked F016 adapter and fails closed while F016 is absent.

The first filled instance is `retail_store_sales`, whose mapping gate is already
cleared on main. That instance proves the generic mechanism; it is not a
universal schema.

## Scope

One vertical slice with five coordinated surfaces:

1. A top-level `orchestration/dagster/` project (package
   `tower_bi_orchestration`) implementing the full 11-asset graph from spec 024,
   with jobs, one daily schedule and one file-arrival sensor both shipped
   STOPPED, and a `run-evidence/` output area.
2. A Python control layer under `src/seshat/dagster_adapter/` that validates
   gates read-only, invokes the Dagster runtime in an isolated process with a
   closed argument set, parses run output, redacts sensitive values, and emits
   normalized evidence.
3. A lazy-loaded `seshat dagster` CLI command family: `doctor`, `run`,
   `evidence`.
4. An updated `dagster-orchestration-adapter` skill (seam note replaced by the
   operational procedure) plus guarded Claude slash-command wrappers
   (`dagster-doctor`, `dagster-run`, `dagster-evidence`).
5. Canonical command-surface entries in `distribution/public-command-surface.yaml`
   with regenerated Claude/Codex bundles and `integrations/` trees, and an
   accurate `docs/capabilities/capabilities.yaml` runtime claim, plus a CI
   definitions-load smoke workflow.

The MVP is Postgres-only. Silver/gold build assets wrap the existing
`warehouse/migrations/*.sql` path; the `dagster-dbt` integration is a documented
seam that activates only after the dbt MVP (spec 133, separate worktree) merges.
The MVP does not enable any schedule or sensor, does not publish Power BI, does
not add incremental orchestration of non-Postgres sources, and does not emit any
numeric score.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A failed gate asset stops every downstream asset and fails the run (Priority: P1)

An operator (or CI) executes the full-sequence job unattended. A gate asset
fails -- e.g. the `retail check` step returns non-zero, or a build step errors.
That asset is failed, every downstream asset is skipped (never run around), the
run terminates with a failed status (the CI signal), and the run-evidence record
carries the failing exit plus measured numbers.

**Why this priority**: fail-closed propagation is the core safety property of an
unattended runtime; without it a scheduler would build dashboards on a broken
gold star. This is the constitutional heart of spec 024 US1/FR-005/FR-013.

**Independent Test**: with a fixture where a mid-graph gate asset is forced to a
non-zero exit, run the job in-process and confirm (a) the asset is failed,
(b) no downstream asset materializes, (c) the run status is failed, (d) evidence
records the exit and numbers, and (e) no readiness stage changed.

**Acceptance Scenarios**:

1. **Given** a gate asset forced to fail, **When** the full-sequence job runs,
   **Then** that asset is failed and all downstream assets are skipped.
2. **Given** the failed run, **When** evidence is written, **Then** it carries
   the non-zero exit and measured findings, not an adjective and not a score.
3. **Given** the failure, **When** the run completes, **Then** the run status is
   failed and no `readiness-status.yaml` stage, `Gate status`, or `approvals[]`
   entry changed.

---

### User Story 2 - A human-seam asset reads committed approval; absent means block (Priority: P1)

The `source_map` asset reads `Gate status: CLEARED` + zero open rows from
`mappings/<table>/unresolved-questions.md` and the `approvals[]` owner+date from
`readiness-status.yaml`. When the approval is absent, `silver_tables` does not
materialize; the run surfaces the open blocker with its named owner and writes
no approval. When it is present, the silver build is permitted.

**Why this priority**: this is the human seam (Principles IV/V) enforced by the
unattended runtime -- the exact failure the kit exists to prevent is an
orchestrator that approves its own mapping.

**Independent Test**: fixture table with `Gate status: OPEN` -> silver blocked,
blocker + owner recorded, nothing wrote CLEARED; flip the fixture to CLEARED ->
silver permitted.

**Acceptance Scenarios**:

1. **Given** `Gate status: OPEN`, **When** the run reaches `silver_tables`,
   **Then** it blocks, reports the open blocker + named owner, and writes no
   approval.
2. **Given** `Gate status: CLEARED` with zero open rows, **When** the run
   reaches `silver_tables`, **Then** the build is permitted with no parallel
   approval marker invented.
3. **Given** `publish_ready` not `pass` (or F016 absent even when it is `pass`),
   **When** the run reaches `publish_execution_evidence`, **Then** it fails
   closed and triggers/publishes nothing.

---

### User Story 3 - A completed run writes derived evidence and flips no stage (Priority: P1)

A run (green or partially blocked) writes `orchestration/dagster/run-evidence/
<run-id>.md` per `templates/dagster-run-evidence.md`: per-asset gate command,
exit code, measured numbers, timestamps, commit sha, and per blocked/skipped
asset the concrete `blocking_reason` + named owner. Measured results are also
surfaced as `evidence[]` / `blocking_reasons[]` on the affected table's
readiness status. No readiness `status`, `Gate status`, or approval is written;
no numeric score appears anywhere.

**Why this priority**: the run-evidence record is what makes an unattended run
auditable -- and it is where an orchestrator is most tempted to "tidy up" by
writing a pass; this story forbids exactly that.

**Independent Test**: run a fixture sequence; assert the evidence record's
required fields exist and `git diff` shows zero changes to any readiness truth
fields.

**Acceptance Scenarios**:

1. **Given** a completed run, **When** evidence is written, **Then** it records
   per-asset command, exit, measured numbers, timestamp, commit sha -- no score.
2. **Given** a partially blocked run, **When** evidence is written, **Then**
   each blocked/skipped asset carries a concrete `blocking_reason` + named owner.
3. **Given** any run, **When** its writes are inspected, **Then** no readiness
   `status`, `Gate status`, or `approvals[]` changed.

---

### User Story 4 - An operator preflights the adapter without a database (Priority: P2)

An operator runs `seshat dagster doctor` and gets a truthful preflight: is the
orchestration project present, does its environment resolve, are the pinned
`dagster`/`dagster-dbt` versions consistent, which tables have a cleared mapping
gate, and what exactly is missing otherwise. Without DB credentials the doctor
reports the deferred boundary explicitly; it never fabricates readiness.

**Why this priority**: the doctor is the front door for both humans and agents;
without it every failure surfaces as a cryptic runtime error.

**Independent Test**: run doctor in a repo without the orchestration environment
installed and without a DSN -> actionable findings, exit non-zero for missing
prerequisites, zero fabricated claims.

**Acceptance Scenarios**:

1. **Given** a missing orchestration environment, **When** doctor runs, **Then**
   it reports the concrete missing prerequisite and the enable step.
2. **Given** no DSN in the environment, **When** doctor runs, **Then** DB-scoped
   checks report a deferred boundary, never a pass.

---

### User Story 5 - The agent surface routes to the adapter consistently (Priority: P2)

An agent (Claude or Codex) discovers `dagster-doctor`, `dagster-run`, and
`dagster-evidence` commands from the canonical public command surface, and the
updated `dagster-orchestration-adapter` skill describes the operational
procedure instead of the "not created yet" seam. Bundles and `integrations/`
trees are regenerated from the authority file and pass the existing drift check.

**Why this priority**: the kit's contract is that
`distribution/public-command-surface.yaml` is the single authority; an activated
runtime whose commands are absent (or drift) breaks the agent-first surface.

**Independent Test**: run the existing command-surface drift/consistency checks;
confirm the three commands appear once each in the authority file, the bundle
templates, and the integrations trees, with no drift findings.

**Acceptance Scenarios**:

1. **Given** the regenerated bundles, **When** the drift check runs, **Then** it
   reports zero drift for the dagster command family.
2. **Given** the updated skill, **When** an agent reads it, **Then** it finds
   doctor/run/evidence procedure and the unchanged authority boundary.

---

### User Story 6 - CI proves the definitions load without secrets (Priority: P3)

CI installs the orchestration project and asserts the Definitions object loads
(the FR-009 minimum gate from spec 024) and the orchestration unit tests pass --
with no database and no secrets. The daily schedule and file-arrival sensor are
present but STOPPED; enabling them is a named-human action.

**Why this priority**: the definitions-load smoke is spec 024's stated minimum
CI gate; it catches version skew in the pinned dagster/dagster-dbt pair.

**Independent Test**: the workflow runs green on a runner with no DB service and
no repository secrets; grep confirms both automation objects declare a stopped/
paused default.

**Acceptance Scenarios**:

1. **Given** the CI workflow, **When** it runs on a clean runner, **Then** the
   definitions-load smoke and orchestration tests pass with no DB and no secrets.
2. **Given** the shipped schedule and sensor, **When** definitions load, **Then**
   both carry a stopped/paused default status.

### Edge Cases

- `retail validate` cannot connect (no creds / DB down): the affected asset
  records `deferred-boundary` with timestamp; it never fabricates a pass.
- `publish_ready = pass` but F016 absent: publish asset FAILS CLOSED with
  `blocking_reason` "F016 publish adapter not available" + named owner.
- A downstream asset is requested directly while an upstream gate is broken:
  the STOP edge still blocks it; no run-around.
- A judgment call surfaces mid-run (grain, PII, rollup, sentinel-vs-null): the
  affected asset HALTS and escalates to the named owner; nothing auto-resolves.
- dagster / dagster-dbt version skew: the definitions-load smoke fails closed in
  CI; the pinned-together pair prevents silent partial upgrade.
- Run-evidence write conflicts with a human edit: evidence is append/record-only
  and never overwrites a human-authored gate field; a conflict surfaces.
- The dbt MVP (spec 133) merges later: the dagster-dbt seam documents exactly
  where the build assets switch engines; gate semantics are identical either way.
- Secrets in errors: any DSN/host/credential appearing in a child-process error
  is redacted before it reaches evidence or console output.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repo MUST gain a top-level `orchestration/dagster/` project
  with its own `pyproject.toml` (package `tower_bi_orchestration`) that pins
  `dagster` and `dagster-dbt` TOGETHER; the main `seshat` package MUST gain no
  Dagster dependency and its static core MUST stay stdlib-only.
- **FR-002**: The project MUST implement the full 11-asset graph from spec 024
  with the committed edge semantics: STOP edges halt all downstream assets;
  HUMAN-SEAM assets read committed approvals (`Gate status`, `approvals[]`,
  `publish_ready`) as their only GO signal and halt when absent; the terminal
  asset only TRIGGERS F016 and fails closed while F016 is absent.
- **FR-003**: Silver/gold build assets MUST execute the existing
  `warehouse/migrations/*.sql` path; the `dagster-dbt` alternative MUST exist
  only as a documented seam that activates after spec 133 merges, with
  identical gate semantics stated.
- **FR-004**: Every gated asset MUST fail closed: a failed gate marks the asset
  failed, skips all downstream assets, and terminates the run with a failed
  status (the CI signal). No code path may run around a STOP edge.
- **FR-005**: No code path in the orchestration project or control layer may
  write a readiness `status`, a `Gate status`, an `approvals[]` entry, a metric
  definition, a mapping, or any Power BI publish. Run evidence and
  `evidence[]` / `blocking_reasons[]` surfacing are the ONLY writes.
- **FR-006**: Each run MUST write `orchestration/dagster/run-evidence/<run-id>.md`
  filled per `templates/dagster-run-evidence.md` -- per-asset gate command, exit
  code, measured numbers, timestamp, commit sha, and per blocked/skipped asset a
  concrete `blocking_reason` + named owner -- and MUST NOT contain any numeric
  health/confidence/maturity score.
- **FR-007**: DB-touching assets MUST detect missing credentials and record a
  `deferred-boundary` outcome with timestamp instead of failing cryptically or
  fabricating success; validation connections MUST be read-only.
- **FR-008**: The control layer (`src/seshat/dagster_adapter/`) MUST be small
  read-only-gate units -- gate preflight, subprocess runner (closed argument
  set, no shell), evidence normalization, and redaction that strips profile
  paths, hosts, user names, passwords, and DSNs from every surfaced error.
- **FR-009**: The CLI MUST expose exactly `seshat dagster doctor`,
  `seshat dagster run`, and `seshat dagster evidence`, lazy-loaded so `seshat`
  startup cost and the stdlib-only static core are unchanged when the family is
  unused.
- **FR-010**: The `dagster-orchestration-adapter` skill MUST be updated to the
  operational procedure (doctor/run/evidence, seams, enable steps) with the
  authority-boundary text unchanged; slash commands `dagster-doctor`,
  `dagster-run`, `dagster-evidence` MUST be added to
  `distribution/public-command-surface.yaml` and regenerated into the
  Claude/Codex bundle templates and `integrations/` trees with zero drift.
- **FR-011**: `docs/capabilities/capabilities.yaml` MUST reflect the activated
  runtime truthfully (locally-verified provenance; command references), and the
  claim MUST NOT overstate what ships (no live-DB claim without a DSN).
- **FR-012**: CI MUST gain a definitions-load smoke job that installs the
  orchestration project and asserts the Definitions object loads plus the
  orchestration unit tests pass, using no database and no secrets.
- **FR-013**: Exactly one daily schedule and one file-arrival sensor MUST ship
  with a stopped/paused default status; enabling them is a named-human action
  recorded outside this feature.
- **FR-014**: All authored artifacts MUST be generic (placeholders like
  `<table>`; `retail_store_sales` appears only as the filled first instance),
  ASCII-only, UTF-8 without BOM; secrets only via the git-ignored `.env`
  (committed examples carry placeholders only).

### Key Entities

- **Orchestration project (`tower_bi_orchestration`)**: the runnable Dagster
  package -- definitions, 11 assets, jobs, one stopped schedule, one stopped
  sensor, gate readers, evidence writer.
- **Asset**: one orchestrated step carrying a gate command and an exit; its
  success means "the command ran and returned this exit", never "the stage
  passed".
- **STOP edge / HUMAN-SEAM edge**: dependency semantics from spec 024 --
  fail-closed propagation vs committed-approval read.
- **Run-evidence record**: the derived, measured, timestamped log of a run at
  `orchestration/dagster/run-evidence/<run-id>.md`; also surfaced as
  `evidence[]` / `blocking_reasons[]` on the affected table's readiness status.
- **Control layer (`seshat.dagster_adapter`)**: gate preflight, subprocess
  runner, evidence normalizer, redactor; the `seshat dagster` CLI family.
- **Command-surface entry**: one row per public command in
  `distribution/public-command-surface.yaml`, the single authority the bundles
  and integrations regenerate from.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The Definitions object loads with all 11 assets, the jobs, one
  schedule, and one sensor present -- verified by an in-process load test that
  needs no database.
- **SC-002**: The US1-US3 acceptance tests pass in-process with zero DB
  credentials: fail-closed propagation, human-seam blocking, evidence written
  with zero readiness-truth changes (asserted via git diff in the test).
- **SC-003**: `seshat dagster doctor` completes on a machine with no
  orchestration environment and no DSN, reporting each missing prerequisite
  concretely and fabricating nothing.
- **SC-004**: The command-surface drift check reports zero drift with the three
  dagster commands present in the authority file, both bundle templates, and
  the integrations trees.
- **SC-005**: A reviewer can grep the diff and find zero writes to readiness
  `status:` fields, `Gate status:` lines, or `approvals[]` entries by adapter
  code, and zero numeric score fields in any evidence artifact.
- **SC-006**: The CI smoke workflow runs green on a runner with no DB service
  and no repository secrets.
- **SC-007**: The full existing test suite plus the new unit tests pass; ruff
  format/lint clean; `retail check` (static governance) reports no new findings.

## Assumptions

- Spec 024's authority text, asset graph, and forbidden-operations matrix are
  FIXED inputs; this spec activates them without redefining them.
- `retail_store_sales` has a cleared mapping gate on main and serves as the
  filled first instance (same posture as spec 133 for dbt).
- The dbt MVP (spec 133) is unmerged and MUST NOT be depended on; the
  dagster-dbt seam is documentation this slice, code a later slice.
- The orchestration project keeps its own virtual environment; `seshat dagster`
  invokes it as a child process and treats its absence as a doctor finding, not
  an install trigger.
- Python 3.13 is the floor for both the main package and the orchestration
  project; the pinned dagster/dagster-dbt pair must support it.
- Enabling schedules/sensors, F016 publish, dbt internals, non-Postgres
  engines, and numeric scoring stay out of scope (spec 024 deferred decisions
  unchanged).
