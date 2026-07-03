# Implementation Plan: Local Demo Harness

**Branch**: `083-demo-harness` | **Date**: 2026-07-03 | **Spec**: `specs/083-demo-harness/spec.md`

**Input**: Feature specification from `specs/083-demo-harness/spec.md`

**Note**: This plan is SPEC WORK. No implementation, no `src/**` edits, no rule
registration, no golden-file regeneration, no CI changes, and no new
dependencies happen as part of producing this plan. It identifies likely files
and a task order for a future, separately-authorized implementation pass.

## Summary

Add a `retail demo` CLI verb group (`init`, `load`, `run`, `report`) that
proves the readiness spine end-to-end on a small, invented, generic sample
dataset shipped with the kit -- fully offline by default, with an optional
live leg when a local Postgres DSN is already reachable. `demo run` computes
status by re-reading committed artifacts + `retail check` + (if reachable)
`retail validate`, exactly like every other readiness surface -- it does not
introduce a second state engine. `demo report` renders status + evidence +
blockers, never a score, never a dashboard. The technical approach is a thin
CLI + fixture-data layer over **existing** primitives
(`src/retail/validate.py`'s `QueryRunner` Protocol and `resolve_dsn`,
`src/retail/cli.py`'s subparser pattern, `templates/readiness-status.yaml`'s
shape) -- no new architecture, no new governance rule.

## Technical Context

**Language/Version**: Python 3.13 (matches the rest of `src/retail/`; no
version bump).

**Primary Dependencies**: stdlib only for the offline path (argparse, pathlib,
csv/json for fixtures), consistent with Principle VIII's static-core-stdlib
posture. The live leg reuses the EXISTING optional `db` extra (`psycopg2`, via
`src/retail/validate.py`'s lazy import) -- **no new dependency** is added by
this feature.

**Storage**: Committed plain-text fixture files (CSV/YAML) for the offline
path (target: `mappings/demo_sample_orders/` + a small `bronze`-shaped CSV
under a demo fixtures location -- exact paths TBD at implementation time, not
fixed here). Optionally, a local/disposable Postgres for the live leg -- no
new storage engine, no new schema design beyond the existing medallion
bronze/silver/gold shape at a tiny scale.

**Testing**: `pytest -m unit` for the CLI wiring, fixture-shape assertions,
and the offline degrade-to-pending path (driver-free, per the repo's existing
`QueryRunner` Protocol test pattern in `tests/unit/`). A `pytest -m
integration`-tagged (or explicitly opt-in) test for the live leg, skipped by
default when no DSN is configured -- mirrors how `retail validate`'s own live
checks are tested today (fixture `QueryRunner`, no real DB in CI).

**Target Platform**: Same as the rest of the kit -- cross-platform CLI
(Windows-primary dev machine per repo `CLAUDE.md`, Linux CI).

**Project Type**: Single project (CLI extension to the existing `retail`
package) -- Option 1 in the template; no frontend/mobile split.

**Performance Goals**: Not performance-sensitive; the whole point is a fast
(<5 minute, per SC-001), tiny-data demo. No specific throughput target beyond
"finishes quickly on a laptop."

**Constraints**: Zero network calls in the offline path (User Story 1). No
writes to tracked files (FR-010). No new top-level dependency. No secret ever
written to a tracked file (Principle IX).

**Scale/Scope**: A single small invented sample table (target: a few dozen to
a few hundred rows -- FR-009 caps it "well under 1,000 rows"), traversing at
most the same seven-stage spine as any other table -- no multi-table scope.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
|---|---|---|
| I. Agent-First, Gate-Enforced | Does `demo run`/`report` claim authority `retail check`/`retail validate` should hold? | **PASS.** FR-005/FR-012 route all pass/fail authority through the existing gates; the demo verbs only recompute/render from their exit status, never invent their own. |
| II. Depend, Never Fork | Does this feature touch the Power BI execution adapter or fork it? | **PASS (N/A).** The demo never invokes the execution adapter; FR-013 keeps `report` a text/data artifact, not a Power BI publish. |
| III. Medallion, Postgres-First, Gold-Only | Does the live leg read `silver`/`bronze` from a BI tool, or invent a non-Postgres engine? | **PASS.** The live leg (if run) is `bronze -> silver -> gold` at demo scale, over Postgres via the existing `QueryRunner`; no BI tool is wired to any layer here. |
| IV. Source Mapping Before Silver | Does the demo write `silver.*` before a reviewed map exists? | **PASS.** `demo init` materializes the sample's mapping set (`source-profile.md`, `source-map.yaml`, `assumptions.md`, `unresolved-questions.md`) as already-filled, already-reviewed fixtures (an implementation-time authoring act, not a `demo run`-time decision) -- consistent with how `retail_store_sales` itself was built. The committed silver migration fixture is authored strictly from the CLEARED map (Foundational task T008); Silver Ready's static "authoring only" gate (`docs/readiness/silver-ready.md`) lets `silver_ready` reach `pass` offline without ever executing SQL before the map exists. |
| V. Agent Stops at Judgment Calls | Does any demo verb self-grant an approval or invent a business rule? | **PASS.** FR-007/FR-008/FR-016/FR-017 + Human-Approval Boundaries make every approval a pre-committed, human-authored (at fixture-build time), clearly-labeled illustrative record -- including the two MANDATORY ones (`source_ready`, required by rule RS1 for a CSV source; and `mapping_ready`) that the offline path's `pass` states rest on -- or else an honestly `blocked` stage. NO approval is ever minted at `demo run` time. |
| VI. Defaults Then Deviations | Does the sample dataset skip recording its RC adopt/deviate decisions? | **PASS (deferred to data-model.md).** The sample's `assumptions.md` fixture MUST record RC adopt/deviate the same way `retail_store_sales` does; `data-model.md` describes this shape without authoring it. |
| VII. C086 Is An Example, Not The Schema | Does the sample data reintroduce C086 fields/values? | **PASS.** FR-009 + SC-006 forbid it outright; the sample is a wholly new invented dataset. |
| VIII. Static-First Governance, Live Deferred | Does the offline path require a DB import, or does the live leg fake a pass? | **PASS.** FR-003/FR-012 require the exact `resolve_dsn`/lazy-import/graceful-degrade pattern already proven in `src/retail/validate.py`; SC-003 forbids a fabricated live pass. |
| IX. Secrets and Reproducibility | Any real DSN, host, or credential proposed for a committed file? | **PASS.** FR-014 + Safety Constraints keep every DSN in `.env`/env vars; fixtures contain no live host. `demo load`'s writes are idempotent per FR-004 (parallels "migrations MUST converge to the same state"). |
| Readiness Spine (supporting section) | Does `demo run` add a second state engine or a fabricated score? | **PASS.** FR-005/FR-006 explicitly forbid both, quoting AGENTS.md's "no separate run-state engine" and the spine's "no fake confidence" rule. |

**Overall: PASS, no violations to record in Complexity Tracking.**

## Project Structure

### Documentation (this feature)

```text
specs/083-demo-harness/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/            # Phase 1 output
│   ├── demo-init-contract.md
│   ├── demo-load-contract.md
│   ├── demo-run-contract.md
│   └── demo-report-contract.md
├── checklists/
│   └── requirements.md
├── analysis/
│   └── analyze-report.md
└── tasks.md              # Phase 2 output (speckit-tasks, not this command)
```

### Source Code (repository root) -- likely files, NOT created by this plan

This is Option 1 (single project); the demo verbs extend the existing
`retail` CLI package rather than introducing a new project root.

```text
src/retail/
├── cli.py                      # ADD a `demo` subparser group (init/load/run/report),
│                                #   following the existing add_parser pattern (see
│                                #   `check`/`validate`/`semantic-check` for the
│                                #   lazy-import-in-handler convention)
├── demo/                        # LIKELY new subpackage (naming TBD at implementation
│   ├── __init__.py              #   time) holding the four verb handlers, kept
│   ├── fixtures.py              #   separate from src/retail/rules/* (no new
│   ├── init.py                  #   `retail check` rule is added by this feature)
│   ├── load.py
│   ├── run.py
│   └── report.py
└── validate.py                  # REUSED, not modified: `QueryRunner` Protocol,
                                  #   `resolve_dsn`, `run_live_checks` are called
                                  #   from demo/run.py and demo/load.py, not
                                  #   reimplemented

mappings/
└── demo_sample_orders/          # LIKELY new fixture set (naming TBD), same five
    ├── source-profile.md        #   mapping-gate artifacts as any other table,
    ├── source-map.yaml          #   pre-filled and pre-reviewed as part of building
    ├── assumptions.md           #   this feature (an implementation-time authoring
    ├── unresolved-questions.md  #   act, not a demo-run-time decision) -- see
    └── readiness-status.yaml    #   data-model.md for the described (not created)
                                  #   shape

<demo fixture data location TBD>/
└── demo_sample_orders.csv       # the small invented bronze-shaped CSV itself --
                                  #   NOT created by this spec-work phase (data-model.md
                                  #   describes its shape; creating it is implementation)

tests/unit/
└── test_demo_cli.py             # LIKELY new: CLI wiring + offline degrade-to-pending
                                  #   assertions, following the existing `QueryRunner`
                                  #   fake-driver test pattern used for `validate.py`

docs/
└── demo/
    └── demo-harness.md          # LIKELY new: short doc cross-linking (FR-015) to
                                  #   docs/worked-examples/retail-store-sales.md and
                                  #   docs/demo/retail-store-sales-demo.md rather than
                                  #   duplicating them
```

**Structure Decision**: Single project (Option 1). The feature is additive to
the existing `retail` package: one new CLI subparser group, one new (likely)
`src/retail/demo/` subpackage for the four verb handlers, one new fixture set
under `mappings/`, and one new small doc. No new top-level package, no new
repo root, no changes to `src/retail/rules/` (this feature registers no new
`retail check` rule) and no changes to `src/retail/validate.py` (its
`QueryRunner`/`resolve_dsn` primitives are reused, not modified).

## Phase 0: Research

See `research.md` for: the sample-dataset shape decision, how the demo stays
honest about the spine (recompute-not-track), and the repo-only vs. live-DB
leg split.

## Phase 1: Design

See `data-model.md` (sample dataset shape, described not created),
`quickstart.md` (the demo walkthrough), and `contracts/` (per-verb
input/output contracts).

## Tests and validation (identified now, authored at implementation time)

- **Unit**: CLI argument wiring for `demo init/load/run/report` (argparse
  subparser registration, `--help` text present); offline degrade-to-pending
  path using a stub/absent DSN (no real DB, no network) -- mirrors existing
  `QueryRunner` fake-driver tests for `validate.py`.
- **Unit**: fixture-shape assertions -- the sample's `source-map.yaml` /
  `assumptions.md` parse and satisfy the same shape checks the mapping-gate
  templates already enforce (reuse existing template-shape tests where
  possible; do not invent a parallel checker).
- **Integration (opt-in / skipped without a DSN)**: the live leg against a
  local/disposable Postgres -- `demo load` then `demo run` reaching
  `gold_ready == pass` with real `retail validate` evidence. Skipped
  automatically (not failed) when no DSN is configured, consistent with how
  the existing live-validator tests behave.
- **Validation task** (tasks.md will enumerate): manually run the offline
  four-verb sequence from a clean checkout and confirm `git status` stays
  clean (FR-010, SC-004) -- this is a `quickstart.md`-driven manual check, not
  an automated test, because it asserts on the ambient repo state.

## Operational risks

- **Risk: scope creep toward "one-click dashboard."** Mitigation: FR-013 +
  the Non-Goals section make `demo report` a text/data report by contract;
  `analysis/analyze-report.md` (Step 4) explicitly re-checks this at the end
  of the chain.
- **Risk: the live leg silently becomes a hard dependency.** Mitigation:
  FR-003/FR-012 require the same graceful-deferred-mode already proven in
  `src/retail/validate.py`; the acceptance scenarios in User Story 1 test the
  no-DB path as the PRIMARY path, not an edge case.
- **Risk: a demo DSN misconfigured to point at a real analytics DB.**
  Mitigation: FR-011's demo-scoped naming convention + the refusal behavior in
  the Stop Conditions section.
- **Risk: sample dataset drifts toward looking like C086 or `retail_store_sales`
  over time (copy-paste habit).** Mitigation: SC-006 names an explicit
  C086-term-list review as a measurable success criterion, not just a stated
  intent.
- **Risk: the demo's illustrative approval fixture gets mistaken for a real
  approval in review.** Mitigation: FR-016 requires the label to live in BOTH
  the fixture file and the rendered report output, not just one place.

## Backwards compatibility

- Purely additive: a new `demo` subparser group and a new fixture set. No
  existing CLI verb's argument shape, exit-code contract, or output format
  changes. No existing rule ID is added, changed, or removed (Step 4's
  analyze pass should confirm no rule registry drift). No existing template
  or worked-example file is modified.

## Repo-only vs. live-DB legs (explicit split)

| Leg | Verbs involved | Requires | Honest offline ceiling / failure mode |
|---|---|---|---|
| Repo-only (default) | `init`, `load` (no-op live leg), `run` (static recompute only), `report` | Base dev install only | Reaches `source_ready`/`mapping_ready`/`silver_ready` = `pass` (Source/Mapping on shipped labeled approval fixtures; Silver on the static `retail check` gate). `gold_ready` and later are `blocked`/`not_started` -- Gold Ready's gate is the live `retail validate`, so it is the honest offline ceiling. |
| Live-DB (optional) | `load` (materializes rows), `run` (adds `retail validate` leg) | `db` extra + a resolvable DSN (local/disposable Postgres, e.g. via `082-postgres-live-validation-suite`) | `gold_ready` reaches `pass` with cited live evidence. When unavailable: `gold_ready` reports `blocked` (deferred) with the concrete reason (FR-003, FR-012); never an exception, never a fabricated pass |

## Forbidden scope (restated from spec Non-Goals, for implementer visibility)

- No Power BI execution-adapter invocation, no PBIP/TMDL generation, no
  dashboard rendering (Principle II, FR-013).
- No live-DB provisioning code (repo `CLAUDE.md` YAGNI).
- No new `retail check` rule ID.
- No modification of `retail_store_sales`'s own artifacts or of
  `docs/demo/retail-store-sales-demo.md` / `docs/worked-examples/retail-store-sales.md`.
- No C086 data, field, or term (FR-009, SC-006).
- No self-granted `approvals[]` entry at any point (FR-008).

## Complexity Tracking

*No Constitution Check violations were found; this section is intentionally empty.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | -- | -- |
