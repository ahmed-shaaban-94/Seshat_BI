# Implementation Plan: Postgres live-validation suite (local, ephemeral, honest)

**Branch**: `082-postgres-live-validation-suite` | **Date**: 2026-07-03 | **Spec**:
`specs/082-postgres-live-validation-suite/spec.md`

**Input**: Feature specification from `specs/082-postgres-live-validation-suite/spec.md`

**Note**: This plan is a design artifact only. No implementation, no `src/**` edits, no manifest
changes, and no CI changes occur in this spec-only chain (see spec.md's Human-Approval
Boundaries and this repo's operating boundaries for this task).

## Summary

Build a **local-only, ephemeral, credential-free** test harness that stands up a real Postgres
container (Docker), seeds it with a small generic silver+gold dataset shaped to the ADR-0002
defaults, and runs the **already-shipped** live-check surfaces (`retail validate`'s four RC
checks, `retail value-check`'s L4 check) against it via their real `psycopg2`-backed
`QueryRunner` -- then feeds one clean run's real output into the existing 057 evidence recorder
to prove the seam end-to-end. The harness's defining discipline (FR-009, the contract in
`contracts/live-pass-contract.md`) is that any unmet precondition (Docker absent, container
failed to start, port conflict, seed failed, driver missing) collapses the affected scenario to
an honest `skipped`/`pending` pytest outcome -- never a pass, never a silent omission. The suite
is structurally separated (a distinct test directory + pytest marker) from the repo's existing
repo-only checks, which remain fully Docker-independent.

## Technical Context

**Language/Version**: Python 3.11+ (matching the existing `retail` package's floor; confirm
exact floor in `pyproject.toml` `requires-python` at implementation time -- not re-verified here
since this chain makes no code change).

**Primary Dependencies (described, NOT added to any manifest by this chain)**:
- Reused as-is: `psycopg2-binary` (the existing `db` extra) for the real `QueryRunner`.
- Would-be new, optional-only: a Docker-orchestration library (`research.md` Decision 1
  recommends `testcontainers[postgres]`), bundled under a would-be new `livetest` extra --
  described in `research.md`/`data-model.md`, never touched in `pyproject.toml` here.

**Storage**: An ephemeral, containerized PostgreSQL instance, local-only, torn down after each
test session (or reset between scenarios within a session) -- never a persistent store, never
cloud infrastructure.

**Testing**: pytest, using a new `@pytest.mark.live_db` marker (would be registered in
`pyproject.toml`'s `[tool.pytest.ini_options] markers` list alongside the existing `unit` /
`integration` markers -- a one-line config addition, still a manifest touch, so still out of
scope for this spec-only chain; named here as a task for the implementation phase).

**Target Platform**: Local developer machines (Windows, per repo CLAUDE.md, plus macOS/Linux);
explicitly NOT CI (Non-Goals).

**Project Type**: Single Python project (matches the existing `retail` package layout) --
test-harness-only addition, no new top-level project.

**Performance Goals**: A full live-suite run (happy path + all defect scenarios + L4 scenarios)
completes within an operationally reasonable bounded time once Docker is warmed up (see
`quickstart.md`'s "Operational timing expectation"; a concrete number is deferred to
implementation-time measurement on a representative host, per Constitution Principle IX's
Windows-safety posture).

**Constraints**: No cloud infrastructure; no real credentials; no CI wiring; no new `retail
check` rule; no modification to `validate.py` / `value_proxy.py` / `readiness_evidence.py`; no
module-scope Docker/DB-driver import anywhere under `src/retail/` (B3 guard, FR-011).

**Scale/Scope**: One fact table, 2-3 conformed dimensions (including a contiguous date
dimension), ~6 seed-scenario `.sql` files, ~4-6 test modules under the new live-DB test
directory. Deliberately small (`data-model.md` section 1) -- this is a proof harness, not a
worked-example-scale build.

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.6.1.*

| Principle | Check | Result |
|---|---|---|
| I. Agent-First, Gate-Enforced | Does this feature weaken the checker-exit-code-is-the-contract posture? | **PASS.** This feature adds no new gate and does not touch `retail check`'s rule set. It is a consumer of existing live surfaces, run under pytest, which has its own long-established exit-code contract (a failed/errored test fails the run). |
| II. Depend, Never Fork | Does this feature fork or vendor anything? | **PASS.** The would-be Docker-orchestration library is consumed as an unforked, optional dependency (mirroring how `psycopg2` is already consumed for `db`). No engine is forked. |
| III. Medallion, Postgres-First, Gold-Only | Does the seed schema respect bronze->silver->gold, gold-only Power BI read? | **PASS.** The generic seed schema (`data-model.md`) is silver+gold only, Postgres, and does not introduce a Power BI read path at all -- this feature never touches Power BI. |
| IV. Source Mapping Before Silver | Does this feature write `silver.*` SQL before a mapping gate clears? | **PASS -- not applicable in the gate's sense.** The seed `.sql` files are test fixtures for a **generic, synthetic** dataset, not a real onboarded table's silver build; there is no real table being mapped, so the mapping gate is not being bypassed for any real source. `spec.md` Non-Goals explicitly excludes wiring this harness to a real `source-map.yaml`-driven table. |
| V. Agent Stops at Judgment Calls | Does this feature self-grant any judgment-call decision (grain, PII, business rollup, stage pass)? | **PASS.** FR-012 explicitly forbids the suite from granting a stage pass. The seed schema's "grain" is a synthetic test fixture, not a business ruling requiring an analyst. No PII exists in synthetic data. No rollup/segment mapping is invented. |
| VI. Defaults Then Deviations | Does the seed schema start from the ADR-0002 defaults? | **PASS.** `data-model.md` section 1 explicitly shapes the seed schema on RC2 (grain/PK), RC14 (-1 unknown member), RC15 (contiguous `generate_series` date dim), RC16 (0 orphan + penny reconciliation) -- adopted as-is, no deviation to record. |
| VII. C086 Is An Example, Not The Schema | Does this feature hardcode any worked-example specific name? | **PASS.** All seed schema names (`order_line`, `product`, `dim_date`) are generic placeholders, not C086/pharmacy-specific. |
| VIII. Static-First Governance, Live Deferred | Does this feature preserve the static-core/live-surface split? | **PASS, and this is the feature's central alignment.** This feature is explicitly the local, credential-free way to exercise "the live run against a real database" that Principle VIII names as the deferred step -- without touching the static core's `dependencies = []` invariant (FR-011: no Docker/DB import at module scope anywhere in `src/retail/`; the harness is entirely test-side). |
| IX. Secrets and Reproducibility | Does this feature risk a committed secret or a non-reproducible artifact? | **PASS.** No real credential is ever in scope (Safety Constraints); the ephemeral container's generated password is redacted wherever it could surface (FR-003). Seed `.sql` files are committed, deterministic text -- reproducible by construction. |

**Readiness System alignment**: this feature does not add a new stage, gate, or approval seam.
It is purely evidentiary tooling that lets an implementer (or reviewer) locally exercise the
Gold Ready stage's already-defined live gate (`docs/readiness/gold-ready.md`) without a cloud DB
-- see `contracts/live-pass-contract.md`'s explicit disclaimer that this suite's green result is
not itself a stage-pass grant.

**Gate result: PASS.** No violation requires a Complexity Tracking entry.

## Project Structure

### Documentation (this feature)

```text
specs/082-postgres-live-validation-suite/
├── spec.md
├── plan.md              # this file
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── live-pass-contract.md
├── checklists/
│   └── requirements.md
├── analysis/
│   └── analyze-report.md   # Step 4 output (manual fallback; see analysis.md note)
└── tasks.md              # Step 3 output
```

### Source code (repository root) -- DESCRIBED for a future implementation, none created here

```text
# Existing, UNCHANGED by this feature (reused, never modified):
src/retail/
├── validate.py               # the four RC live checks + make_psycopg2_runner (reused as-is)
├── value_proxy.py            # the L4 live check (reused as-is)
├── readiness_evidence.py     # the 057 recorder (reused as-is, called once for proof)
└── rules/live_surface_boundary.py   # B3 guard -- this feature MUST keep it green (FR-011)

# NEW, test-side only (this feature's actual contribution; not created by this spec chain):
tests/
├── unit/                     # UNCHANGED -- existing fixture-based tests for validate.py /
│                              # value_proxy.py / readiness_evidence.py stay exactly as they are
└── live_db/                  # NEW directory -- everything this feature adds lives here
    ├── conftest.py            # session-scoped fixture: Docker availability probe, container
    │                          # start/wait/teardown, honest skip on any precondition failure
    ├── seeds/
    │   ├── schema.sql                              # the shared DDL (data-model.md section 1)
    │   ├── seed_clean.sql
    │   ├── seed_defect_pk_duplicate.sql
    │   ├── seed_defect_date_gap.sql
    │   ├── seed_defect_orphan_fk.sql
    │   ├── seed_defect_reconciliation_mismatch.sql
    │   └── seed_value_check.sql
    ├── test_live_validate_clean.py       # User Story 1
    ├── test_live_validate_defects.py     # User Story 2 (4 scenarios, one per RC check)
    ├── test_live_value_check.py          # User Story 3
    ├── test_live_db_unavailable.py       # User Story 4 (mocked precondition failures)
    └── test_live_db_wiring.py            # structural guard: every test in this dir carries
                                           # @pytest.mark.live_db; no bare except-pass around a
                                           # Docker/connection call (contracts/live-pass-
                                           # contract.md's "Verification approach")

# NEW, manifest-adjacent (described only -- NOT edited by this spec chain):
pyproject.toml   # would gain: the `livetest` optional extra; `live_db` added to the
                 # registered pytest `markers` list. Both are single-line-ish additions,
                 # but ANY manifest edit is implementation, not spec work -- deferred.
```

**Structure Decision**: a single new `tests/live_db/` directory, parallel to the existing
`tests/unit/` (there is currently no `tests/integration/` directory despite the marker existing
in `pyproject.toml`, so this feature does not need to reconcile with an existing `integration/`
layout -- `live_db` is a new, distinctly-named directory + marker, not a repurposing of
`integration`). This keeps the live-DB surface trivially `git`-visible as separate from
repo-only tests (`research.md` Decision 3), and requires zero change to `src/retail/` (the
Constitution Check's key finding: this is entirely additive, test-side tooling).

## Forbidden scope (explicit, restating spec.md Non-Goals for plan-level clarity)

- No edit to `pyproject.toml` or any other manifest in this chain (the `livetest` extra and the
  `live_db` marker registration are described above as future implementation tasks, not
  performed here).
- No edit to `src/retail/**`.
- No new `retail check` rule id.
- No CI workflow file added or edited.
- No golden-file regeneration.
- No write to any `mappings/<table>/readiness-status.yaml`.
- No commit, push, PR, or merge performed by this planning chain.

## Complexity Tracking

*No entry required -- the Constitution Check gate above reports PASS on all nine principles with
no violation needing justification.*
