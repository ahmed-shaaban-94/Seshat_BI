# Feature Specification: Postgres live-validation suite (local, ephemeral, honest)

**Feature Branch**: `082-postgres-live-validation-suite`

**Created**: 2026-07-03

**Status**: Draft

**Input**: User description: "Define a Docker/Testcontainers-style LIVE VALIDATION suite that
runs PostgreSQL LOCALLY and proves live validation against real materialized data. No real
credentials. No cloud infrastructure. Must prove live DB paths HONESTLY. Must run `retail
validate` and relevant `value-check` paths ONLY when a real local DB is available. Must keep
repo-only checks SEPARATE from live-DB checks. Must NOT claim a live pass when DB setup fails
or is skipped (mark pending/skipped honestly)."

## Overview

This feature stands up a **real, local, ephemeral PostgreSQL instance** (no cloud, no real
credentials) and seeds it with **generic sample data**, so the already-built live-check surfaces
-- `retail validate`'s four checks (V-RC2/V-RC15/V-RC16, `src/retail/validate.py`), `retail
value-check`'s L4 measure check (`src/retail/value_proxy.py`), and the live-validation evidence
recorder (`057-live-validation-evidence-recorder`, `src/retail/readiness_evidence.py`) -- have
something real to run against. It builds **none** of those checks: it builds the local-DB
**substrate + seed + run harness** they need. This is the concrete instantiation of the "the
live run against a real database is the remaining deferred step" clause of Constitution
Principle VIII (Static-First Governance, Live Deferred) -- proven **without** cloud
infrastructure or credentials, by running everything against a disposable local database.

The central discipline this feature exists to enforce: a live check may report a result **only**
when a real local database was actually started, became reachable, was seeded, and the check
executed against materialized rows. If **any** precondition fails -- Docker unavailable, the
container fails to start, a port conflict, seed failure, the optional DB driver missing -- the
suite MUST report `pending` / `skipped` / `blocked`, **never** a pass. Absence of failure is not
evidence of a pass.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prove the four live validate checks against real materialized rows (Priority: P1)

A contributor (or CI, later, out of scope here) wants concrete proof that `retail validate`'s
four live checks (PK uniqueness, date coverage, orphan FKs, reconciliation) actually work
against **real rows in a real database** -- not only against the fixture `QueryRunner` fakes
the unit suite already exercises. They run the local live-validation suite. It starts a
disposable local Postgres, applies a small generic silver+gold schema (one fact, a couple of
conformed dimensions, a contiguous date dimension) built from the ADR-0002 defaults, seeds it
with synthetic rows (including at least one seeded defect scenario per check, see User Story 2),
and runs `run_live_checks` against it via the real `psycopg2`-backed `QueryRunner`. The
contributor sees an honest, itemized result: which checks ran, against what row counts, with
what findings -- and that result is reproducible by anyone with Docker available, using no
credentials beyond a suite-generated local password that is never shared, logged, or persisted
outside the ephemeral container's own lifetime.

**Why this priority**: This is the reason the feature exists -- until now the four live checks
have only ever been proven against synthetic fakes; a clean local run against a real materialized
Postgres is the first "this actually executes real SQL against a real database" proof the kit
has produced. Without it, "live run deferred" (Principle VIII) has no local, credential-free way
to be un-deferred for review purposes.

**Independent Test**: With Docker available locally, run the suite's happy-path scenario end to
end and assert (a) all four live checks execute against the seeded database (not a fake runner),
(b) a clean seed yields zero ERROR findings, (c) the evidence recorder (057) is fed the real
`Finding[]` output and produces a `gold_ready` block with `run_mode="live"` and non-empty
`evidence[]`.

**Acceptance Scenarios**:

1. **Given** Docker is available and the suite is invoked, **When** the local Postgres
   container starts, becomes reachable, and is seeded with the generic clean fixture dataset,
   **Then** all four live checks (`check_pk_uniqueness`, `check_date_coverage`,
   `check_orphan_fks`, `check_reconciliation`) run against the real database via a real
   `psycopg2` `QueryRunner` and report zero ERROR findings.
2. **Given** the same clean run, **When** its `Finding[]` output is fed to
   `readiness_evidence.build_gold_ready_block` with `run_mode="live"`, **Then** the emitted block
   has `status: warning` (never `pass` -- FR-012 of 057 still applies; this feature does not
   change that rule) and non-empty `evidence[]` naming a real live run.
3. **Given** the same run, **When** the suite report is inspected, **Then** it explicitly states
   the mode was `live` (not `skipped`/`pending`) and names the transient container identity
   without ever printing the container's generated password or a full connection string.

---

### User Story 2 - Prove each live check catches its seeded defect (Priority: P1)

A contributor wants confidence that the four live checks are not just "runs without crashing"
but **actually detect** the defect each one is designed to catch. They run the suite's
defect-injection scenarios: a duplicate-PK seed (for V-RC2), a fact date missing from the date
dimension (for V-RC15), a fact row with a foreign key that matches no dimension row (for
V-RC16 orphan), and a silver/gold measure total that differs by one cent (for V-RC16
reconciliation). Each scenario seeds its own small, isolated dataset (or a shared dataset with
one deliberately broken slice) and asserts the corresponding check returns exactly the expected
ERROR finding(s) -- and that the other checks on the same run stay clean, so a single injected
defect does not cause an unrelated check to misfire.

**Why this priority**: A live-check suite that only ever proves the happy path is not proof the
checks catch real problems; equal priority to User Story 1 because a live-validation suite that
cannot demonstrate a true positive is not trustworthy evidence of anything.

**Independent Test**: For each of the four checks, seed the one defect scenario in isolation,
run only that check, and assert exactly the expected `rule_id` (`V-RC2` / `V-RC15` / `V-RC16`)
and `Severity.ERROR` finding is returned, with no other ERROR finding.

**Acceptance Scenarios**:

1. **Given** a seeded fact table containing two rows sharing the same declared PK tuple,
   **When** `check_pk_uniqueness` runs against the live database, **Then** it returns a
   `V-RC2` ERROR finding whose message states the duplicate count.
2. **Given** a seeded fact table containing a date value absent from the seeded date dimension,
   **When** `check_date_coverage` runs, **Then** it returns a `V-RC15` ERROR finding naming the
   coverage gap.
3. **Given** a seeded fact row whose foreign key value matches no row in its dimension table,
   **When** `check_orphan_fks` runs, **Then** it returns a `V-RC16` ERROR finding naming the
   orphan.
4. **Given** seeded silver and gold tables whose measure totals differ by one cent, **When**
   `check_reconciliation` runs, **Then** it returns a `V-RC16` ERROR finding naming the exact
   gap amount.

---

### User Story 3 - Prove the L4 value-check path against a live measure (Priority: P2)

A contributor wants the `retail value-check` L4 path (`value_proxy.check_expected_value`) proven
against a real live aggregate, not only the fixture runner the unit suite already covers. They
run the suite's value-check scenario: it seeds a small gold table with a known, computable
measure total, builds an `ExpectedValue` target that matches the seeded total exactly, and
asserts the live check reports a match; then it perturbs the expected value beyond tolerance and
asserts the live check reports a mismatch.

**Why this priority**: L4 is the other named live-DB surface in scope (alongside `retail
validate`) per the task's remit ("relevant `value-check` paths"); it is P2 (not P1) because the
four RC checks are the core of the readiness spine's Gold Ready gate, while L4 is a
contract-drift safeguard layered on top -- valuable, but not the load-bearing gate this feature
primarily exists to prove.

**Independent Test**: Seed one gold measure total, run `check_expected_value` against it live
with a matching expected value (assert no finding) and then with a mismatched expected value
(assert exactly one `V-L4` ERROR finding naming the observed vs. expected gap).

**Acceptance Scenarios**:

1. **Given** a seeded gold table with a known `sum`-aggregate measure total, **When**
   `check_expected_value` runs live with an `ExpectedValue` matching that total (within
   tolerance), **Then** it returns no finding.
2. **Given** the same seeded table, **When** `check_expected_value` runs live with an
   `ExpectedValue` that differs beyond tolerance, **Then** it returns exactly one `V-L4` ERROR
   finding naming the observed and expected values.

---

### User Story 4 - Honest pending/skipped reporting when the local DB is unavailable (Priority: P1)

A contributor without Docker installed, or with Docker installed but not running, or hitting a
port conflict, or seed failure, invokes the suite. Instead of a crash, a silent no-op, or --
worst of all -- a false green, the suite reports each live scenario as **skipped** (pytest
`skip`) or the harness reports `pending`, names the specific precondition that failed (Docker
unavailable / container failed to start / port conflict / seed failed / driver missing), and
exits in a way that is visibly distinguishable from "all live checks ran and passed." Repo-only
checks (`retail check`, the unit suite's fixture-based `QueryRunner` tests) are completely
unaffected and continue to run and pass with no dependency on Docker being present.

**Why this priority**: This is the other half of the feature's reason to exist -- named
explicitly in the task remit ("Must NOT claim a live pass when DB setup fails or is skipped").
Equal priority to User Story 1 because a live-validation suite without this discipline is worse
than no suite: it would let a broken/absent Docker setup masquerade as a validated live path.

**Independent Test**: Simulate each unavailability precondition (mock Docker absent; mock
container start timeout; mock seed script failure) in isolation and assert the suite's result
for that precondition is `skipped`/`pending` with a named reason, and that no scenario under any
precondition reports a passing live-check result.

**Acceptance Scenarios**:

1. **Given** Docker is not available on the host, **When** the live-validation suite is invoked,
   **Then** every live scenario reports `skipped` with a reason naming "Docker not available",
   and the process exit code / test outcome is distinguishable from a passing live run (e.g. a
   pytest `SKIPPED` outcome, not `PASSED`).
2. **Given** Docker is available but the Postgres container fails to become ready within its
   startup timeout, **When** the suite is invoked, **Then** the affected scenario(s) report
   `skipped`/`pending` naming "container failed to become ready", not a pass, and not a raw
   unhandled traceback.
3. **Given** the container starts but the seed step fails (e.g. a seed SQL script errors),
   **When** the suite is invoked, **Then** the affected scenario(s) report `skipped`/`pending`
   naming "seed failed", not a pass.
4. **Given** any of the above unavailable/failed preconditions, **When** the repo-only checks
   (`retail check`, the existing fixture-based unit tests for `validate.py` / `value_proxy.py` /
   `readiness_evidence.py`) are run, **Then** they are wholly unaffected -- they require no
   Docker, no container, and no local Postgres, and their pass/fail is independent of the local
   live suite's availability.

---

### Edge Cases

- What happens when the optional `db` extra (`psycopg2-binary`) is not installed, but Docker
  IS available? The suite MUST report `skipped`/`pending` naming "DB driver not installed",
  distinct from "Docker not available" -- these are two different missing preconditions and
  MUST NOT be conflated in the reported reason.
- What happens when a previous run's container is still occupying the chosen port (a stale
  container from a crashed prior run)? The suite MUST detect the port conflict, report
  `skipped`/`pending` naming "port conflict", and MUST NOT silently connect to a stale,
  possibly-differently-seeded container and report its result as if it were this run's own.
- What happens when the suite is run twice in a row (idempotency of the harness itself, not the
  SQL migrations)? Each run MUST use a freshly created and torn-down container (or a schema
  reset within a reused container) so that seed-scenario N's defect does not leak into run N+1's
  clean-scenario assertions.
- What happens on a platform where Docker Desktop requires elevated permissions or is
  unreachable inside a sandboxed CI-less local shell (Windows-specific)? The suite MUST detect
  the failure mode and report `skipped`/`pending`, not hang indefinitely -- a bounded startup
  timeout is required.
- What happens if a live check scenario partially runs (e.g. two of four checks executed) before
  a mid-run failure (e.g. the container is killed externally mid-suite)? Only the checks that
  actually completed against materialized rows may report a result; any check that did not
  complete MUST report `skipped`/`pending`, never inherit a neighboring check's result.
- What happens if someone tries to point the suite at a real remote/cloud DSN instead of the
  local ephemeral container? Out of scope / explicitly forbidden by this feature (see Non-Goals)
  -- the suite's harness only ever manages a container it started itself; it MUST NOT accept an
  arbitrary external DSN as a substitute live target.
- What happens when the suite's generated local database password or connection details would
  otherwise appear in a test report or log? They MUST be redacted using the same discipline
  `readiness_evidence._scrub` / `cli._redact_dsn` already apply, even though this is a local,
  throwaway credential with no external validity -- consistent secret hygiene, no exceptions
  carved out for "it's only local."

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The suite MUST provision a real, local, ephemeral PostgreSQL server for the
  duration of a live scenario, using a container-based mechanism (Docker), and MUST tear it
  down afterward (or reuse-and-reset it within a bounded test session) so no state persists
  beyond the run.
- **FR-002**: The suite MUST NOT connect to any cloud, remote, or shared database. It MUST NOT
  accept an externally supplied DSN as a substitute for the container it manages -- the only
  live target is the local ephemeral instance the suite itself started.
- **FR-003**: The suite MUST NOT require, accept, or store any real credential. Any password or
  connection secret used is generated locally for the ephemeral container's lifetime only, is
  never a value with meaning outside that container, and MUST be redacted wherever a check
  result, log, or report might otherwise surface it verbatim.
- **FR-004**: The suite MUST seed the ephemeral database with a small, generic (non-worked-example,
  no client-specific naming) silver+gold schema and dataset built from the ADR-0002 defaults
  (RC2 grain/PK, RC14 `-1` unknown member, RC15 contiguous `generate_series` date dimension,
  RC16 zero-orphan + penny-exact reconciliation) sufficient to exercise all four `retail
  validate` live checks and at least one `value-check` L4 measure.
- **FR-005**: The suite MUST provide, for each of the four `retail validate` live checks, a
  seeded "clean" scenario (zero findings expected) AND a seeded "defect" scenario that
  deliberately triggers exactly that check's ERROR finding (User Story 2), isolated so that one
  check's injected defect does not cause a different check to report a false ERROR.
- **FR-006**: The suite MUST run the real `psycopg2`-backed `QueryRunner`
  (`validate.make_psycopg2_runner`) against the ephemeral database for every live scenario --
  it MUST NOT substitute a fake/mock `QueryRunner` for a scenario it reports as `live`.
- **FR-007**: The suite MUST feed at least one live run's `Finding[]` output into the
  live-validation evidence recorder (`readiness_evidence.build_gold_ready_block`) with
  `run_mode="live"`, demonstrating that a real live run (not only a synthetic Finding list)
  produces the block 057 defines -- WITHOUT re-implementing or modifying the recorder itself.
- **FR-008**: The suite MUST report, for every scenario, one of exactly three outcomes: the live
  check(s) ran against materialized rows and their findings are reported as-is (pass-through,
  including any ERROR); OR the scenario is `skipped`/`pending` naming the specific unmet
  precondition; there is no third "unclear" outcome.
- **FR-009 (the honest-pending discipline; central to this feature)**: The suite MUST NOT report
  a live check as passing, or feed a "clean run" evidence block to the recorder, unless a real
  local database was started, became reachable, was seeded, and the check actually executed
  against materialized rows and returned zero ERROR findings. Any failure of any precondition
  (Docker unavailable, container failed to start, port conflict, seed failed, driver missing,
  mid-run container loss) MUST result in `skipped`/`pending`/`blocked`, never a pass and never a
  silently-omitted scenario. Absence of a failure signal is not, by itself, evidence of a pass.
- **FR-010**: The suite's live scenarios MUST be structurally separated from the repo's existing
  repo-only checks (the static `retail check` rule suite and the existing fixture-based unit
  tests for `validate.py` / `value_proxy.py` / `readiness_evidence.py`), such that the repo-only
  checks continue to run and pass with zero dependency on Docker, a container runtime, or a local
  Postgres being available. This MUST be enforced structurally (e.g. a distinct pytest marker
  and/or directory), not merely by convention.
- **FR-011**: The suite MUST NOT introduce any Docker/testcontainers/live-DB import at module
  scope in any file under `src/retail/` (preserving the B3 live-surface import-boundary
  guard and the static core's `dependencies = []` invariant); any such import belongs only in
  the test-harness code that this feature specifies, never in the shipped package.
- **FR-012**: A green run of this suite's live scenarios MUST NOT itself move any readiness
  stage (e.g. `gold_ready`) to `pass`. It proves the four live checks and the L4 check execute
  correctly against real data; stage-pass remains the separate human/approval action already
  established by Constitution Principle V and by 057's FR-012 (the recorder never self-grants
  `pass`). This feature MUST NOT introduce a new path that grants a stage pass.
- **FR-013**: The suite MUST run on a local developer machine without any dependency on CI
  infrastructure, cloud secrets, or network access beyond what Docker itself requires to pull
  its Postgres image (a one-time, documented, offline-tolerable step).
- **FR-014**: The suite's documentation/report output MUST name, for every run, which mode it
  operated in (`live` vs `skipped`/`pending`) in language a reviewer can act on without reading
  source code -- consistent with the readiness spine's "no fake confidence" discipline
  (Constitution: Readiness System section; no numeric score standing in for this distinction).

### Key Entities *(include if feature involves data)*

- **Ephemeral local Postgres instance**: a container-managed, disposable PostgreSQL server
  started and torn down by the suite itself; never a stand-in for a remote/cloud database; the
  only entity this feature is permitted to treat as a "live" target.
- **Generic seed dataset**: a small, non-worked-example silver+gold dataset (one fact, a
  handful of conformed dimensions including a contiguous date dimension) built to the ADR-0002
  defaults, with both a "clean" variant and four isolated "defect" variants (one per RC2/RC15/
  RC16-orphan/RC16-reconciliation check) plus one L4-measure variant.
  Table/column names are placeholders (e.g. `<fact_table>`, `<dim_table>`), never a client's
  actual schema.
- **Scenario outcome record**: the per-scenario result the suite reports -- one of "live: N
  findings" (N may be 0) or "skipped/pending: `<named precondition>`". Never a numeric
  confidence score; never a bare boolean pass/fail without the mode attached.
- **Precondition check**: a single named gate the suite verifies before attempting a live run
  (Docker present and running, container reachable within timeout, seed completed, driver
  installed); each has its own distinct failure reason string, never merged into a generic
  "setup failed."

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a machine with Docker available, running the suite's User Story 1 happy-path
  scenario produces zero ERROR findings from all four `retail validate` live checks executed
  against a real, materialized, local Postgres database (not a fixture/fake runner) -- verifiable
  by inspecting the scenario's recorded `run_mode` and confirming it is `live`.
- **SC-002**: Each of the four `retail validate` live checks has at least one reproducible
  defect-injection scenario (User Story 2) that yields exactly the expected `V-RC2` / `V-RC15` /
  `V-RC16` ERROR finding and no unrelated ERROR finding on the same run.
- **SC-003**: The L4 value-check path has at least one live scenario proving a match (no finding)
  and one proving a mismatch (exactly one `V-L4` ERROR finding) against a real materialized gold
  table (User Story 3).
- **SC-004 (the no-hidden-live-pass criterion)**: For every one of the simulated unavailability
  preconditions in User Story 4 (Docker absent, container start failure, port conflict, seed
  failure, driver missing), the suite's reported outcome for the affected scenario(s) is
  `skipped`/`pending`, and zero scenarios anywhere in the suite report a `live` pass under any
  of those preconditions -- verifiable by asserting no `PASSED` (only `SKIPPED`/`XFAIL`-style)
  test outcome exists for a live scenario when its precondition is unmet.
- **SC-005**: Running `retail check` and the existing fixture-based unit test suite (`pytest -m
  unit`) succeeds identically whether or not Docker is installed/running on the host -- zero
  behavioral coupling between repo-only checks and the local live suite's availability.
- **SC-006**: No test report, log line, or committed fixture produced by this suite contains a
  literal DSN, password, or the local container's generated credential in unredacted form --
  verifiable by a text scan of the suite's own output artifacts.
- **SC-007**: A full run of the suite's live scenarios (happy path + all defect scenarios +
  L4 scenarios), when Docker is available, completes within an operationally reasonable bounded
  time (e.g. a documented timeout budget in `plan.md`/`quickstart.md`), so the suite is usable
  interactively by a contributor, not only as an unattended long-running job.

## Non-Goals (explicitly out of scope)

- **No CI wiring.** This feature does not add or modify any CI workflow/Action. Whether/how a
  future feature runs this suite in CI (with Docker-in-CI implications) is explicitly deferred.
- **No cloud or remote database of any kind.** Not DigitalOcean, not any managed Postgres, not
  a shared dev database. Local and ephemeral only.
- **No real credentials, ever**, including in a `.env`, an example file, or a fixture -- only
  suite-generated, container-scoped, throwaway values.
- **No new `retail check` static rule.** This feature does not add, remove, or change any
  governance rule id.
- **No golden-file regeneration.**
- **No change to `validate.py`, `value_proxy.py`, or `readiness_evidence.py`'s public behavior.**
  This feature is a consumer/harness for those modules, not a modification of them.
- **No new dependency added to any manifest** (`pyproject.toml` or otherwise). Docker,
  testcontainers-python (or an equivalent), and the existing `psycopg2-binary` `db` extra are
  DESCRIBED as what an implementation would need (see `plan.md`/`research.md`), never added here.
- **No stage-pass automation.** This feature does not grant, or add a path to grant, any
  readiness stage's `pass` status. See FR-012.
- **No orchestrator integration**, per repo CLAUDE.md YAGNI scope discipline.
- **No live run against a per-table `source-map.yaml` from a real onboarded table.** The seed
  dataset is generic and synthetic; wiring this harness to validate an actual mapped table is a
  possible future extension, not this feature.

## Human-Approval Boundaries

- This spec chain (spec -> plan -> tasks -> analyze) requires no human approval to produce, per
  the task's operating mode (spec work only, isolated worktree, no merge).
- Ratification of this spec (moving it from Draft to Ratified/adopted) is a named-human action,
  consistent with Constitution Principle V and the repo's `Ratify seam not auto-cleared` lesson
  -- it is explicitly NOT performed by this chain.
- Any future implementation of this spec that touches `src/retail/` import boundaries, adds an
  optional dependency to a manifest, or wires CI MUST pass through the repo's normal review gate
  (`retail check`, the B3 import-boundary guard, and a named human PR review) before merge --
  none of that happens in this spec-only chain.
- Enabling Docker-based live testing as a default developer workflow step (e.g. via a Makefile
  target or documented onboarding step) is a scope decision for whoever picks up the
  implementation tasks; this spec only defines what "honest" behavior such a step must have.

## Safety Constraints

- No secret, DSN, hostname, or credential of any kind (real or example-realistic) appears in
  this spec chain's committed text. All connection examples use clearly-broken `<placeholder>`
  forms.
- The suite MUST NOT be able to accidentally target a real database: by construction (FR-002) it
  only ever manages a container it started itself, with no code path that accepts an external
  `--dsn`-equivalent for live scenarios.
- The suite MUST default to read-only-safe behavior consistent with the existing live-surface
  posture (`validate.make_psycopg2_runner` already opens read-only sessions for the four RC
  checks); seeding the ephemeral database is the one intentional write path, confined entirely
  to the suite's own disposable container.

## Stop Conditions

This spec-authoring chain stops, and does not proceed to implementation, at any of the
following (none of which are expected mid-chain, but are named per the task's boundaries):

- A scope-changing ambiguity that cannot be resolved by a documented Assumption (see
  `[NEEDS CLARIFICATION]` markers below, capped at 3).
- Any point at which producing an artifact would require touching `src/retail/`, adding a
  dependency to a manifest, changing CI, or regenerating a golden file -- all forbidden to this
  chain by its operating boundaries.
- Any point at which a human approval/ratification would be required to proceed -- this chain
  stops at the ratify boundary and does not self-approve.

## Assumptions

- **Docker is the containerization mechanism** this feature designs around (the task explicitly
  frames it as "Docker/Testcontainers-style"); the plan phase will name a specific tool choice
  (raw Docker via a Python client, `testcontainers-python`, or `docker-compose` invoked from a
  test fixture) as a research decision, not a foregone conclusion.
- **The `db` extra (`psycopg2-binary`) already defined in `pyproject.toml` is reused as-is** for
  the real `QueryRunner`; this feature does not need a second Postgres driver.
- **A new optional extra (working name: `livetest`)** would bundle whatever
  Docker-orchestration library the plan phase selects, kept separate from `db` (which only
  covers the driver) and separate from `dev` (which CI installs) -- so CI continues to install no
  Docker-orchestration dependency and no behavior changes for existing CI. This is a plan-phase
  design choice, described only, never added to a manifest in this chain.
- **The generic seed dataset is minimal by design**: one fact table, 2-3 conformed dimensions
  (including a contiguous date dimension), and one or two measures -- enough to exercise all four
  RC checks and one L4 measure, not a full worked-example-scale schema.
- **pytest is the test runner** or in the reasonable case that this suite is a fixture provider
  the checkpoint above still holds: a distinct marker (working name: `@pytest.mark.live_db`) is
  how repo-only vs live-DB tests are structurally separated, mirroring the existing `unit` /
  `integration` marker convention referenced in the global Python rules.
- **This feature feeds, but does not replace or extend, 057's recorder.** Any evidence produced
  during this suite's run that happens to flow through `build_gold_ready_block` is for
  demonstration/proof purposes within the suite; it is not wired to write into any table's real
  `mappings/<table>/readiness-status.yaml`.
- **Windows is a supported development host** (per repo CLAUDE.md), so the plan phase must
  account for Docker Desktop's Windows-specific behavior (start-up latency, permission prompts)
  in its operational-risk analysis, rather than assuming a Linux CI-like environment.

## Clarifications

No interactive clarification session occurred (this chain cannot reach a human). The following
are the load-bearing informed guesses, each already absorbed into an Assumption above rather than
left as an open question, because none of them changes the feature's scope or safety posture --
only its implementation detail:

- Docker-orchestration tool choice (raw Docker client vs `testcontainers-python` vs
  `docker-compose`) -- Assumption above; deferred to `research.md`.
- New optional extra name (`livetest`, working name) -- Assumption above; deferred to `plan.md`.
- Seed dataset shape/size -- Assumption above; deferred to `data-model.md`.

### [NEEDS CLARIFICATION] markers (scope-forking only, capped at 3)

1. **[NEEDS CLARIFICATION-1]** Should this suite's live scenarios be runnable as part of a
   contributor's normal `pytest -m unit -x -q` local-verification habit (i.e. auto-skip silently
   when Docker is absent, so it's harmless to leave in the default collection), or should they
   require an explicit opt-in flag/marker selection (e.g. `pytest -m live_db`) so a Docker-less
   contributor never even sees "skipped" noise? This is scope-forking because it changes whether
   the suite is discovered by default or invoked deliberately -- a plan-level decision the human
   reviewer should confirm, not one this chain should assume silently. **Working default if
   unresolved**: opt-in marker (`-m live_db`), never collected by the default `unit` marker run,
   because that keeps the existing mandatory local-verification command
   (`pytest -m unit -x -q`) behaviorally unchanged for every contributor, Docker or not.
2. **[NEEDS CLARIFICATION-2]** Should a future CI job running this suite (explicitly out of
   scope to build here, per Non-Goals) be anticipated in this design at all -- i.e. should
   `plan.md`'s operational-risk section merely note Docker-in-CI as a risk, or should the harness
   be designed so a later CI feature could adopt it with zero rework? This is scope-forking
   because "design for future CI adoption" vs "design for local-only, CI is someone else's
   problem" changes how much the harness code should abstract the container lifecycle. **Working
   default if unresolved**: note it as an operational risk only (per the task's explicit "no CI
   changes" boundary); do not over-design for a hypothetical future CI consumer (YAGNI, repo
   CLAUDE.md scope discipline).
3. **[NEEDS CLARIFICATION-3]** Does "relevant `value-check` paths" (from the task description)
   mean only the `sum`/`count`-style aggregate paths already shown in User Story 3, or does it
   also require proving the `ratio` aggregate path (`value_proxy`'s numerator/denominator
   recompute) live? This is scope-forking because the `ratio` path requires a second measure
   shape and doubles the L4 seed surface. **Working default if unresolved**: prove one
   non-ratio aggregate (`sum`) live, as User Story 3 specifies; treat live-proving the `ratio`
   path as a natural follow-on extension, not required for this feature's completion, since the
   task's example list ("relevant `value-check` paths") reads as "prove the surface is live-
   provable," not "prove every aggregate kind."
