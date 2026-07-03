# Contract: `retail demo init`

## Purpose

Materialize the committed generic sample dataset's fixtures (bronze-shaped
sample rows + the pre-filled, pre-reviewed mapping-gate artifact set) into a
git-ignored demo working directory, with zero network access and zero
database access.

## Interface

- **Invocation**: `retail demo init [--force]`
- **Exit codes**: `0` on success (fixtures materialized or already present
  and unchanged); non-zero only on an unexpected filesystem error (e.g.
  working directory not writable) -- never on "no DB configured" (that is not
  an error condition for this verb).
- **`--force`** (optional): re-materialize even if the working directory
  already has content, without prompting. Without it, re-running `init` on an
  already-initialized working directory is a no-op that reports "already
  initialized" (idempotent, mirrors FR-004's idempotency requirement extended
  to this verb for consistency).

## Inputs read (read-only)

- The committed sample fixture files under `mappings/demo_sample_orders/`
  (or final chosen path) and the small invented CSV (or equivalent) described
  in `data-model.md`.

## Outputs / side effects

- Writes ONLY inside the git-ignored demo working directory (`data-model.md`'s
  "Demo working directory" entity). Writes NOTHING to any tracked path
  (FR-010).
- Prints a short human-readable summary: which fixtures were materialized,
  the sample table's row count, and the next suggested command (`retail demo
  load`).

## Boundary contract

- MUST NOT contact a network (Safety Constraints: "every demo verb's offline
  path... MUST function with zero network access").
- MUST NOT open a database connection -- `init` has no live leg at all; the
  live/offline split begins at `load` (FR-002, FR-003).
- MUST NOT modify, move, or delete the committed fixtures it reads from --
  it copies/materializes into the working directory, never edits the source.
- MUST NOT write, infer, or alter an `approvals[]` entry or any other
  governed artifact (FR-008).

## Failure modes and required behavior

| Condition | Required behavior |
|---|---|
| Working directory already initialized, no `--force` | Report "already initialized," exit 0 (idempotent no-op) |
| Working directory not writable | Report the concrete filesystem error, exit non-zero |
| Committed fixtures missing/corrupt (packaging defect) | Report the concrete missing/malformed file, exit non-zero -- never silently skip |

## What this verb explicitly does NOT do

- Does not load anything into a database (that is `demo load`).
- Does not compute or render any readiness status (that is `demo run` /
  `demo report`).
- Does not touch git-tracked files under any circumstance.
