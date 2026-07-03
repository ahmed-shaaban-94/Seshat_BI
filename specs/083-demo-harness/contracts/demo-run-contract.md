# Contract: `retail demo run`

## Purpose

Recompute the sample table's per-stage readiness status from committed
mapping-gate artifacts, `retail check`'s exit status, and -- only if a
database was successfully loaded into (via `demo load`) and remains
reachable -- an actual `retail validate` run. Persist that computed snapshot
to the demo working directory for `demo report` to render. **This verb
introduces no separate run-state engine** -- every value it produces is
re-derivable at any time from the same committed artifacts + gate outputs
(AGENTS.md: "Recompute... there is no separate run-state engine").

## Interface

- **Invocation**: `retail demo run [--dsn postgresql://...]`
- **`--dsn`**: same resolution precedence as `demo load` and `retail
  validate`. If omitted and none resolves, `run` performs the offline-only
  computation (does not error).
- **Exit codes**: `0` whenever the computation itself completes, REGARDLESS
  of whether individual stages come out `pass`, `blocked`, or `pending` --
  a `blocked` sample stage is not a CLI failure; it is the honest, correct
  answer for an offline run. Non-zero only on an unexpected internal error
  (e.g. a malformed committed fixture that prevents computation entirely).

## Inputs read (read-only)

- The mapping-gate artifacts in the demo working directory (materialized by
  `init`): `source-profile.md`, `source-map.yaml`, `assumptions.md`,
  `unresolved-questions.md`.
- `retail check`'s exit status/findings over those artifacts (invoked as a
  subprocess or in-process call to the existing checker -- implementation
  detail, not fixed here).
- If a DSN resolves AND `demo load`'s live leg previously succeeded (or
  succeeds now): `retail validate`'s findings over the demo-scoped gold
  objects, via the existing `QueryRunner` Protocol / `run_live_checks`
  (`src/retail/validate.py`) -- REUSED, not reimplemented.

## Outputs / side effects

- Writes a computed status snapshot to the demo working directory only
  (git-ignored; never a tracked file -- FR-010).
- Prints a short summary of what changed since the last computed snapshot
  (or "first run" on a cold start).
- Does NOT print the full report (that is `demo report`'s job) -- though
  `run` MAY offer to chain into `report` for ergonomics, the underlying
  computation is owned by `run` alone (single source of truth for "what did
  we last determine," per the recompute-not-track design in `research.md` R2).

## Status computation rules (the honesty contract)

- **Every stage's status MUST be one of exactly four values**:
  `not_started`, `blocked`, `warning`, `pass` (FR-006). No numeric score is
  ever computed or stored.
- **A stage MUST NOT be reported `pass` without citable evidence** (Evidence
  Requirements in `spec.md`): a specific artifact path, or a specific
  `retail check`/`retail validate` finding.
- **`silver_ready` and `gold_ready` are mechanical gates** (per
  `docs/readiness/silver-ready.md` and `docs/readiness/gold-ready.md`), and
  they draw the offline honest line at DIFFERENT places:
  - `silver_ready` is "authoring only" (`silver-ready.md`): its gate is
    `retail check` (S1-S7) exit 0 over the **committed silver migration
    fixture** plus a Phase-5-order self-review, with **no owner approval**.
    This gate is fully STATIC, so `silver_ready` CAN honestly reach `pass`
    OFFLINE for the demo -- the migration `.sql` fixture exists and is
    statically clean. (The worked example additionally cited a live V-RC2
    re-proof as stronger-than-minimum evidence; that is not the gate.)
  - `gold_ready` requires an ACTUAL live `retail validate` pass
    (`gold-ready.md`: "Emit a `pass` while in deferred mode ... [is
    forbidden] -- report blocked-deferred instead"). If no DB was loaded
    into, `gold_ready` is `blocked` (deferred), never `pass`, no matter how
    clean the static artifacts look (Principle VIII: "`retail check` exit 0
    is necessary, not sufficient"). Gold Ready is therefore the honest
    offline ceiling.
- **Approval-gated stages require a named-human approval to show `pass`.**
  `mapping_ready` (gate sign-off), `semantic_model_ready`, `dashboard_ready`,
  `publish_ready` -- and, because the sample is a CSV file source,
  `source_ready` too (rule RS1 refuses a file source's `source_ready: pass`
  without a matching `{stage: source_ready}` approval, per
  `docs/readiness/source-ready.md` and `src/retail/rules/readiness_status.py`).
  For this demo, each such approval is either (a) absent -> stage is honestly
  `blocked`/`not_started` with the specific owner/class named (FR-007), or (b)
  a pre-committed illustrative fixture -> stage MAY show `pass` but MUST carry
  the illustrative-fixture label (FR-016) in the computed snapshot, so `report`
  can render it labeled. The sample SHIPS the `source_ready` and
  `mapping_ready` approvals (mandatory for the offline path to be honest); the
  `semantic_model_ready` one is optional (User Story 3).
- **This verb MUST NOT create, infer, or mutate an `approvals[]` entry.** It
  only reads whatever is already present in the committed fixture (FR-008).

## Boundary contract

- MUST NOT drive stages forward ("try to advance to Gold Ready") -- it only
  computes the CURRENT truth. There is no "attempt" semantics; either the
  evidence already exists (via a prior `demo load` or the committed
  fixtures) or the stage is honestly not yet reached.
- MUST NOT write to any tracked repo path.
- MUST NOT require a DSN to complete successfully -- the offline computation
  is always a complete, valid, exit-0 run on its own (User Story 1 is the
  primary path, not a fallback).
- The live-leg subprocess/call to `retail validate` MUST use the exact same
  graceful-deferred-mode behavior it already has when no DSN resolves
  (FR-012) -- `run` does not re-implement that degrade logic; it inherits it
  by calling the same code path.

## Failure modes and required behavior

| Condition | Required behavior |
|---|---|
| `demo init` never run | Report the ordering error naming `init`, exit non-zero |
| No DSN, no prior `demo load` live success | Compute offline-only legs; `source_ready`/`mapping_ready`/`silver_ready` may reach `pass` (Source/Mapping on shipped labeled approval fixtures, Silver on static `retail check`); `gold_ready`+ report `blocked` (deferred); exit 0 |
| DSN resolves, prior `demo load` succeeded | Compute offline legs + live leg; `gold_ready` may reach `pass` with cited live evidence; exit 0 |
| DSN resolves but the demo-scoped objects are absent (load never actually ran against this DB) | Report `gold_ready` as `blocked` with reason "no live-validated data; DSN unset or load not run" (Edge Cases in `spec.md`), exit 0 -- NOT an error, an honest state |
| A committed mapping-gate fixture is malformed | Report the concrete parse/shape error, exit non-zero |

## What this verb explicitly does NOT do

- Does not render the human-readable report (that is `demo report`).
- Does not touch any tracked file.
- Does not grant, infer, or synthesize any approval.
- Does not attempt to reach stages beyond what the actual evidence supports,
  regardless of how "close" a stage might look.
