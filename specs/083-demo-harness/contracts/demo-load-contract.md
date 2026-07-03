# Contract: `retail demo load`

## Purpose

Load the sample dataset's rows into either (a) the offline working area only
(no DB configured -- reports the live leg as skipped), or (b), when a DSN
resolves and the `db` extra is installed, into a demo-scoped schema/table set
in a real Postgres, idempotently.

## Interface

- **Invocation**: `retail demo load [--dsn postgresql://...]`
- **`--dsn`** (optional): overrides env, exactly mirroring `retail
  validate`'s `--dsn` flag and `resolve_dsn` precedence
  (`--dsn` > `DATABASE_URL` > `ANALYTICS_DB_*` parts > none).
- **Exit codes**: `0` in both the offline-skip case and the successful-live-load
  case. Non-zero only on a genuine failure to write to an already-resolved,
  already-confirmed-demo-scoped target (e.g. a permissions error on that
  schema) -- never merely because no DSN was configured.
- **Prerequisite**: `retail demo init` MUST have been run first (Edge Cases:
  "What happens when `retail demo run` is invoked before `retail demo init`");
  `load` reports a clear ordering error naming `init` as the missing
  prerequisite if the working directory is not yet materialized.

## Inputs read (read-only)

- The materialized fixtures in the demo working directory (written by `init`).
- Environment / `.env` for DSN resolution (Principle IX; never a hardcoded
  credential).

## Outputs / side effects

**Offline case (no DSN resolves, or `db` extra not installed):**
- Writes a load summary to the demo working directory only (rows "loaded"
  logically, no DB write attempted).
- Reports explicitly: live leg skipped, and why (`db` extra missing, or DSN
  unresolved) -- consistent with the `[PENDING LIVE PROFILE]`-style messaging
  convention in `AGENTS.md` / `src/retail/validate.py`.
- Exit 0. This is the expected, common path (User Story 1) -- not a
  degraded error state to apologize for.

**Live case (DSN resolves and `db` extra installed):**
- Before writing anything, MUST verify the resolved target's schema/table
  names carry the demo-scoped naming marker (FR-011, `research.md` R4). If
  the target cannot be confirmed demo-scoped, MUST refuse to write and report
  the refusal (Stop Conditions in `spec.md`) rather than proceeding.
- Creates (if absent) or upserts (if present) the demo-scoped bronze/silver
  rows for the sample dataset, using the existing lazy-`psycopg2`-import
  convention from `src/retail/validate.py` (no new DB driver dependency).
- Re-running `load` against the same target converges to the same row state
  (idempotent -- FR-004). It does not duplicate rows, and does not error with
  "already exists" as a fatal condition.
- Reports the target host/database name only in its summary (never a full
  DSN with embedded credentials -- Principle IX).

## Boundary contract

- MUST NOT provision, create, or manage a Postgres instance/server itself
  (Non-Goals: "NOT a live-DB provisioning tool"). It only writes rows into an
  ALREADY-reachable database the evaluator configured.
- MUST NOT write to any schema/table lacking the demo-scoped naming marker
  (FR-011) -- this is a hard refusal, not a warning.
- MUST NOT write to any tracked repo path (FR-010) in either case.
- MUST NOT require network access in the offline case (Safety Constraints).
- The `psycopg2` import (or equivalent driver) MUST be lazy, inside this
  verb's handler only, so `retail check`'s stdlib-only import chain is
  unaffected (Principle VIII, mirroring `_run_validate`'s existing pattern).

## Failure modes and required behavior

| Condition | Required behavior |
|---|---|
| `demo init` not yet run | Report the ordering error naming `init`, exit non-zero |
| `db` extra not installed, no DSN | Offline path: report skip + reason, exit 0 |
| `db` extra installed, DSN unresolved | Offline path: report skip + reason, exit 0 |
| DSN resolves but target lacks demo-scoped naming | Refuse to write, report the refusal + the expected naming convention, exit non-zero |
| DSN resolves, target confirmed demo-scoped, write succeeds | Report success summary (host/db name only), exit 0 |
| DSN resolves but connection fails (network/auth) | Report the concrete connection error, exit non-zero -- never silently fall back to "offline" without saying so |
| Re-run after a prior successful load (offline or live) | Converge to the same state, exit 0 (idempotent) |

## What this verb explicitly does NOT do

- Does not run `retail validate`'s live CHECKS (PK uniqueness, orphan FKs,
  reconciliation) -- that happens in `demo run`, which reads the rows this
  verb loaded. `load` only loads; it does not validate.
- Does not grant any readiness stage a `pass` -- that is computed and
  reported by `run`/`report`, never asserted by `load`.
- Does not provision infrastructure.
