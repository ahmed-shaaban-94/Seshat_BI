# Contract: `retail demo report`

## Purpose

Render the sample table's readiness status (status + evidence + blocking
reasons, per stage) as a human-readable text report -- and ONLY that. This
verb is the demo's single most safety-critical contract surface, because it
is the one most tempted toward scope creep into "just render a little
dashboard too."

## Interface

- **Invocation**: `retail demo report [--format text|json]`
- **`--format`**: `text` (default, human-readable) or `json` (structured,
  same shape as `templates/readiness-status.yaml` conceptually, for scripting
  / future tooling). Both formats are status/evidence/blockers renderings --
  neither is ever a chart, image, or Power BI artifact.
- **Exit codes**: `0` always for a well-formed report, regardless of what
  stages show (a `blocked` stage is correct output, not a CLI failure). This
  INCLUDES the cold-start case (`demo init` never run / no working directory):
  the report renders every stage `not_started` and exits `0` -- a cold-start
  report MUST NOT error (see Edge Cases and the Failure-modes table below). A
  non-zero exit is reserved for an actual CLI/usage error (e.g. an unreadable
  or malformed committed artifact the surface cannot parse), not for any
  legitimate readiness state.

## Inputs read (read-only)

- The computed status snapshot written by the most recent `demo run`, if one
  exists in the demo working directory.
- If NO snapshot exists yet (cold start, `run` never called): `report` MAY
  compute the always-cheap OFFLINE-ONLY legs itself (equivalent to calling
  `run`'s offline path inline) so that "fresh clone, run `report` first" does
  not error -- but it MUST NOT attempt a live-DB leg on its own initiative;
  that remains `run`'s (or `load`'s) responsibility to have already done.

## Outputs / side effects

- Prints the report to stdout (or writes to the demo working directory if
  `--format json` output is redirected -- either way, still never a tracked
  path).
- Writes NOTHING to any tracked repo path (FR-010). `demo report` is
  read-only with respect to the rest of the repository.

## Content contract (the hard boundary against dashboard creep)

- **MUST show, per stage**: the stage name, its status (one of the four
  canonical values only; "pending" is display-only phrasing over
  `blocked`/`not_started`, never a fifth stored value), its evidence
  citations (if `pass`/`warning`) or its named blocking reason (if
  `blocked`/`not_started`), and, for any approval-gated stage still unmet (the
  four spine stages plus the CSV `source_ready` RS1 approval, FR-007/FR-017),
  the specific approval owner-class still required.
- **MUST NOT show a numeric confidence/health/percent-ready score**, in
  either `text` or `json` format (FR-006, SC-005). If `--format json` output
  is later consumed by some other tool, that tool's own scoring is out of
  scope for this feature and MUST NOT be implied as endorsed here.
- **MUST NOT render, generate, or link to a chart, visual, dashboard image,
  or PBIP/TMDL artifact** of any kind (FR-013, Non-Goals: "NOT one-click
  dashboard generation"). This is the report's single hardest constraint.
- **MUST label EVERY shipped illustrative approval** -- the mandatory
  `source_ready` (RS1) and `mapping_ready` approvals that the PRIMARY offline
  path (US1) renders as `pass`, AND the optional `semantic_model_ready` one
  (US3) -- inline, next to the stage it applies to, as "illustrative fixture,
  pre-committed with the sample -- not produced by this run" (FR-016) -- not
  in a separate
  footnote easy to miss.
- **MUST name a concrete `next_action`** (mirrors
  `templates/readiness-status.yaml`'s `next_action` field) -- e.g. "configure
  a local Postgres DSN and re-run `demo load`" or "read
  docs/worked-examples/retail-store-sales.md for the full narrative" -- never
  a bare "not ready" with no next step.

## Boundary contract

- MUST NOT invoke `retail check` or `retail validate` itself (that is `run`'s
  job); `report` only reads what `run` already computed, or computes the
  cheap offline legs inline per the cold-start rule above. This keeps
  `report` always fast and always safe to call repeatedly (`research.md` R2).
- MUST NOT write, infer, or mutate an `approvals[]` entry or any other
  governed artifact.
- MUST NOT claim a stage is `pass` beyond what the underlying snapshot
  (or its own inline offline computation) actually supports -- it renders,
  it does not upgrade a status for presentation's sake.

## Failure modes and required behavior

| Condition | Required behavior |
|---|---|
| `demo init` never run (no working directory at all) | Render a report with every stage `not_started` and `next_action` = "run `retail demo init`"; exit 0 (Edge Cases: cold-start report MUST NOT error) |
| `demo run` never called, but `init`/`load` were | Compute the offline-only legs inline and render; note in the report that the live leg (if a DSN is configured) has not yet been checked by a `run` |
| Computed snapshot is stale relative to changed fixtures (e.g. someone hand-edited a fixture after the last `run`) | Report what the snapshot says, but this is a known limitation to flag in `tasks.md`/future work -- NOT a defect this spec-work phase is required to solve (the demo is not expected to file-watch); the honest baseline behavior is still correct because the offline legs `report` computes inline are always freshly derived. **RATIFIER-RESOLVED 2026-07-03:** the `run`->snapshot / `report`->snapshot split is confirmed NOT a second state engine (it matches the recompute-and-render model in AGENTS.md; offline legs are always re-derived inline, only the live/gold leg is cached), and the bounded live-leg staleness window is ACCEPTED as a documented limitation (refresh by re-running `demo run`). This closes 083's open ratifier question. |

## What this verb explicitly does NOT do

- Does not run any check or validator.
- Does not write to any tracked file.
- Does not render a dashboard, chart, or visual of any kind.
- Does not grant, upgrade, or infer any approval or readiness status beyond
  what its inputs already support.
