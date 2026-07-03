# Contract: when a live check may report "pass" (and when it must not)

**Feature**: `specs/082-postgres-live-validation-suite/spec.md`
**Status**: Design contract (not executable code) -- this file defines the rule an
implementation's harness code MUST satisfy; it is not itself a runtime artifact.

## Why this contract exists

This is the single most important seam in this feature. Every other requirement in `spec.md`
(FR-001..FR-014) exists in service of this rule: **a live check's result may be reported as a
completed live outcome (pass-through of its real findings, including zero findings) if and only
if every precondition below is independently verified true for that specific run.** Any
precondition's failure collapses the outcome to `skipped`/`pending` -- never a pass, never a
silent omission.

## The preconditions (ALL required, checked in this order)

1. **Docker is available and running.** The container runtime responds to a basic
   availability probe (e.g. a version/info call) within a bounded timeout. Failure reason:
   `"docker not available"`.
2. **The DB driver (`psycopg2`) is importable.** The optional `db` extra is installed in the
   test environment. Failure reason: `"driver not installed"`. (Checked independently of #1 --
   Docker being available says nothing about whether the Python environment running pytest has
   the driver; per `spec.md` Edge Cases, these are distinct reasons and MUST NOT be conflated.)
3. **The ephemeral Postgres container starts and becomes reachable within a bounded timeout.**
   A real TCP connection (or the chosen library's readiness probe) succeeds before the timeout
   elapses. Failure reasons: `"container failed to start"` (the container process itself did not
   come up) or `"port conflict"` (the container came up but the chosen host port could not bind
   / was already occupied by a stale prior run).
4. **The seed step completes without error.** The scenario's `.sql` seed file executes to
   completion against the reachable container with no SQL error. Failure reason: `"seed failed"`.
5. **The check itself executes to completion against the seeded, materialized rows** (the real
   `QueryRunner`/`psycopg2` connection, not a fake), without an unhandled exception at the DB
   boundary. Failure reason (rare, but must still be honest): `"live check raised an unexpected
   error"` -- this is not treated as a `V-RC*`/`V-L4` finding (those come FROM the check's own
   return value), it is a harness-level failure and must ALSO resolve to `skipped`/`pending`, not
   to a silently-swallowed exception that leaves the scenario's outcome ambiguous.

**Only when all five preconditions hold** does the scenario report `mode: "live"` with the
check's real `Finding[]` (which may itself be empty -- zero findings on a clean seed -- or
contain one or more ERROR/WARNING findings on a defect seed). The check's own findings are never
edited, filtered, or reinterpreted by the harness; the harness's only job under this contract is
deciding whether to let the real result through (`live`) or to report `skipped` before the check
ever runs (or immediately upon a mid-run harness-level failure).

## What "pass" does NOT mean here (a second, easily-confused claim)

Even within a `mode: "live"` outcome with zero ERROR findings, this contract explicitly does
**not** claim:

- That any readiness stage (e.g. `gold_ready`) is now `pass`. That remains a separate,
  human/approval-gated action (Constitution Principle V; 057 FR-012). This suite's "live, zero
  ERROR findings" result is evidence a human or a later automated step MAY cite -- it is not
  itself a stage-pass grant.
- That the declared grain/PK is a ratified business fact. Per 057's FR-014 (unchanged by this
  feature), a clean `V-RC2` result is recorded as "no duplicate observed on current [seeded]
  rows," not as a ratified uniqueness claim -- doubly true here, since the "current rows" are
  synthetic seed data, not a real table's production rows.
- That the suite proves anything about a real onboarded table. This contract governs only the
  suite's own generic seed scenarios (see `data-model.md`); extending it to a real
  `source-map.yaml`-driven table is explicitly out of scope (`spec.md` Non-Goals).

## The forbidden shape (what this contract exists to prevent)

An implementation VIOLATES this contract if any of the following occurs:

- A scenario reports `mode: "live"` while any of the five preconditions actually failed (e.g. a
  readiness-wait timeout is caught and silently treated as "probably fine, proceed anyway").
- A scenario's precondition check fails, but the harness reports no outcome at all for that
  scenario (silent omission) rather than an explicit `skipped` -- an omitted scenario in a test
  report can misleadingly read as "not applicable" rather than "attempted and blocked."
- A scenario's underlying pytest test method returns/passes (green) via a bare `try/except:
  pass` around a Docker/connection failure, rather than calling `pytest.skip(reason=...)` --
  this is the single most concrete anti-pattern this contract forbids: a vacuously green test
  when the DB is absent is exactly the hidden pass named in the task's central discipline.
- A precondition failure's reason string is generic ("setup failed", "error") rather than one of
  the five named reasons above -- genericness defeats FR-014's "reviewer can act on it without
  reading source code."

## Verification approach (for `tasks.md` to schedule as tests)

- One test per precondition, each simulating that precondition's failure in isolation (mocking
  Docker absence, mocking a container start timeout, mocking a seed script error, mocking the
  driver import failing) and asserting: (a) the pytest outcome is `SKIPPED`, not `PASSED`; (b)
  the skip reason string matches the expected named reason; (c) no `Finding`/check result is
  reported for that scenario.
- One combinatorial-adjacent check (not literally combinatorial -- five independent single-fault
  tests are sufficient, per `spec.md`'s edge cases, which are all single-fault) confirming the
  five failure reasons are mutually distinguishable strings (no two preconditions share a reason
  string), so a reviewer reading a report can always tell which precondition failed.
- A meta-assertion (a wiring test, mirroring `tests/unit/test_rules_wiring.py`'s existing style)
  scanning the live-DB test directory's source for the anti-pattern `except Exception:\s*pass`
  (or equivalent silent-swallow shapes) around any Docker/connection call, failing the wiring
  test if found -- a static guard against the forbidden shape above, on top of the runtime tests.

## Relationship to existing contracts this feature does not redefine

- This contract is layered ON TOP OF, and does not modify, `validate.py`'s own severity contract
  (WARNING = suspect static pattern, ERROR = proven live defect) or `value_proxy.py`'s tolerance
  contract for `check_expected_value`. Those checks' own pass/fail semantics for a GIVEN set of
  materialized rows are unchanged; this contract only governs whether the harness is honest about
  whether those rows were ever real and reachable in the first place.
- This contract does not modify 057's `build_gold_ready_block` status-derivation rules (`live`
  errors -> `blocked`; clean/warning-only -> `warning`, never `pass`). It is a precondition this
  feature must satisfy before it is even permitted to call that function with `run_mode="live"`.
