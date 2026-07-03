# Quickstart: Postgres live-validation suite

**Feature**: `specs/082-postgres-live-validation-suite/spec.md`

This describes how a future implementation of this feature would be used. It documents intended
commands/flow for the plan and tasks phases; **no code exists yet** -- this spec chain builds no
implementation.

## Prerequisites (documented, not installed by this chain)

- Docker Desktop (or an equivalent Docker-compatible runtime) installed and running.
- The optional extras this feature's plan phase would define, installed in the dev environment
  (described only -- see `research.md` Decision 1):
  - the existing `db` extra (`pip install 'retail[db]'`) for the real `psycopg2`-backed
    `QueryRunner`.
  - the would-be new `livetest` extra (working name; `pip install 'retail[livetest]'`) for the
    Docker-orchestration library selected in `research.md` Decision 1.
- No `.env`, no real credentials, no network access beyond Docker's one-time Postgres image pull.

## Running repo-only checks (unaffected by this feature, always available)

```bash
ruff format --check src/ tests/
ruff check src/ tests/
pytest -m unit -x -q
retail check
```

These commands have zero dependency on Docker and are unaffected whether or not this feature's
live suite exists on the machine -- this is the separation FR-010/SC-005 require, demonstrated
here as the "before" baseline any implementation must preserve.

## Running the live-validation suite (once implemented)

```bash
# Opt-in only (see spec.md NEEDS CLARIFICATION-1 working default): the live suite is
# never collected by the default `-m unit` run.
pytest -m live_db -x -q
```

Expected honest outcomes, by environment:

| Environment | Expected result |
|---|---|
| Docker running, driver installed, no port conflict | Every scenario reports `mode: "live"`; clean scenarios show 0 ERROR findings; defect scenarios show exactly their expected `V-RC2`/`V-RC15`/`V-RC16`/`V-L4` ERROR finding. Pytest outcome: `PASSED` for the *test* (the test asserts the *expected* finding shape, which may itself be "one ERROR expected and observed" -- the test passing means the assertion held, not that the seeded data was defect-free). |
| Docker not installed / not running | Every `live_db`-marked test reports pytest `SKIPPED`, reason `"docker not available"`. Repo-only commands above are unaffected. |
| Docker running, `psycopg2` not installed | Every `live_db`-marked test reports `SKIPPED`, reason `"driver not installed"`. |
| Docker running, container fails to become ready in time | Affected test(s) report `SKIPPED`, reason `"container failed to start"` (or `"port conflict"` if that is the specific detected cause). |
| Container up, seed script errors | Affected test(s) report `SKIPPED`, reason `"seed failed"`. |

## Reading the report

A contributor should be able to answer, from the test output alone (per FR-014):

1. Did each live scenario actually run against a real database, or was it skipped?
2. If skipped, exactly which precondition was unmet?
3. If it ran, what did each check find (and does that match the scenario's expectation)?

None of these three answers should require reading the harness's source code.

## What this quickstart deliberately does not cover

- CI usage (Non-Goals in `spec.md`; a future feature's concern).
- Pointing the suite at any real onboarded table's `source-map.yaml` (Non-Goals).
- Any stage-pass action -- running this suite, however cleanly, never changes any
  `readiness-status.yaml` file (FR-012; this suite doesn't write that file at all, per
  `data-model.md` section 4).

## Operational timing expectation

Per `research.md` Decision 5, a full local run (happy path + all defect scenarios + L4
scenarios) with Docker already warmed up is expected to complete within roughly one to a few
minutes on a typical developer machine (container startup dominates; the seed + check queries
themselves are near-instant on this feature's small generic dataset). The plan phase should
pin a concrete timeout budget once the container-orchestration library (`research.md` Decision 1)
is selected and its actual cold-start latency is measured on a representative Windows host, per
Constitution Principle IX's Windows-safety posture.
