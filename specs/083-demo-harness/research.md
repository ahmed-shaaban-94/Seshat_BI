# Research: Local Demo Harness

Phase 0 output. Each decision cites the requirement it resolves and the
alternative considered.

## R1 -- What shape should the generic sample dataset take?

**Decision**: A small, invented, single-entity retail transaction dataset
(a fictional small store's order/sale lines) -- structurally similar in kind
to `retail_store_sales` (one fact grain, a handful of dimension-shaped
columns) but with none of its actual values, field names, or scale.
Target size: well under 1,000 rows (FR-009), enough to demonstrate grain,
PK uniqueness, a couple of dimension attributes, and one money measure -- not
enough to need real profiling effort.

**Rationale**: The task explicitly requires "GENERIC sample data only
(invented, neutral)" and "NO client-specific or C086 data." A transaction/order
grain is the most universally legible retail shape for a demo audience (it
does not require inventing an unfamiliar domain), and reusing the *shape* of
grain (one fact + a few dims) without reusing the *content* keeps the pattern
recognizable to anyone who has already read the worked example, while staying
independently invented.

**Alternatives considered**:
- **Reuse `retail_store_sales` (the Kaggle CSV) directly.** Rejected: it is
  12,575 rows (too large to "run in minutes" the way SC-001 wants), externally
  licensed (Kaggle terms), and reusing it would collapse this feature into
  "run the worked example again," which is explicitly the `docs/demo/`
  reading-path artifact's job, not this feature's (see the Relationship
  section in `spec.md`).
- **Invent a non-retail domain (e.g. a library checkout log) to maximize
  distance from any real client.** Rejected: the task frames this as a
  "generic retail store dataset" example; a non-retail domain would work
  technically but would undercut the demo's "this is what YOUR retail table
  onboarding looks like" value.
- **Generate the sample data programmatically at `demo init` time (e.g. a
  seeded random generator) instead of shipping a committed fixture.**
  Rejected: FR-002 requires materializing from committed fixtures, not
  generating fresh data every run, because (a) reproducibility matters for a
  demo people compare notes on, and (b) a committed fixture is auditable
  (someone can `git diff` it) in a way a generator's output is not without
  extra machinery.

## R2 -- How does the demo stay honest about the readiness spine?

**Decision**: `demo run` performs **recompute, never track** -- it re-derives
every stage's status from (a) which mapping-gate artifacts exist and are
well-formed, (b) `retail check`'s exit code over those artifacts, and (c),
only if a DB is reachable, an actual `retail validate` run's findings. It
never persists its own separate "demo state" that could drift from what the
artifacts + gates actually say.

**Rationale**: This is not a design preference -- it is what the repo already
mandates. `AGENTS.md` states plainly: *"Recompute `current_stage` from
committed artifacts + `Gate status` + migration presence -- there is no
separate run-state engine."* The `readiness-viewer` skill's contract is
"renders, never re-derives" state that already exists; `first-hour-compass`'s
contract is "creates no truth, changes no state... after a run, `git status`
is clean." A demo harness that maintained its own separate progress tracker
would violate the same architectural rule every other readiness surface
follows, and would risk becoming the "fake confidence" / "hidden live pass"
failure mode Principle V and the readiness model explicitly forbid.

**Consequence for verb design**: `run` and `report` are necessarily close in
behavior (`run` computes, `report` renders what was computed, or `report` can
recompute-and-render in one step if `run` is treated as a no-op alias for "do
the load-triggered computation now"). This plan keeps them as two verbs
because the task's given surface names both, and because separating "do the
work of checking" (`run`, which may take a few seconds if it invokes `retail
validate`) from "show me what's known" (`report`, always instant, always safe
to call repeatedly) is a real, defensible ergonomic split -- not an artificial
one. `contracts/demo-run-contract.md` and `contracts/demo-report-contract.md`
pin the exact boundary: `run` is allowed to invoke `retail validate` /
`retail check`; `report` MUST NOT invoke either and only reads what `run`
last computed (a small git-ignored, demo-scoped status file) or, if `run` was
never called, computes the always-cheap offline-only legs itself.

**Alternatives considered**:
- **Make `demo run` an orchestrator that also drives stage transitions
  forward (e.g. "try to reach Gold Ready").** Rejected outright: this would
  be exactly the "separate run-state engine" AGENTS.md forbids, and it risks
  becoming an approval-granting shortcut (Principle V) the moment "try to
  advance" meets a stage that needs a human sign-off.
- **Collapse `run` and `report` into one verb.** Rejected: the task's given
  surface names both verbs, and there is a genuine behavioral difference
  (network/DB-touching vs. always-safe-to-re-run) worth preserving as a
  contract boundary, per the reasoning above. If a future implementer finds
  the split adds no real value once built, `analysis/analyze-report.md` flags
  this as a specific over-governance risk to revisit, but this spec-work
  phase does not merge them pre-emptively.

## R3 -- Repo-only vs. live-DB leg split

**Decision**: Every demo verb has a default, always-available **repo-only**
behavior that touches no network and no database, and an **optional live-DB**
behavior that activates only when both (a) the `db` extra is installed and
(b) a DSN resolves (via `--dsn`, `DATABASE_URL`, or `ANALYTICS_DB_*`, exactly
mirroring `src/retail/validate.py`'s `resolve_dsn` convention). The two legs
are documented per-verb in `contracts/`.

**Rationale**: This is the same host-agnostic, optional-driver, graceful-
degrade posture Principle VIII already mandates for `retail validate` itself
("Connection is host-agnostic... The DB driver (psycopg2) is OPTIONAL and
imported LAZILY"). Reusing the exact pattern (rather than inventing a second
one for the demo) keeps the kit's degrade-to-pending behavior consistent
everywhere a user might encounter it, and lets the demo's live leg literally
call the existing `run_live_checks`/`QueryRunner` machinery instead of
re-implementing live validation logic.

**Alternatives considered**:
- **Require a DB for the demo to be meaningful at all (skip the offline
  path).** Rejected: this directly contradicts the task's "No cloud
  dependency" instruction and SC-001's "under 5 minutes... zero network
  calls" outcome; it would also make the demo strictly harder to run than the
  kit's other CLI surfaces, which is backwards for an evaluator's first
  contact.
- **Build a bespoke, lighter-weight DB connector just for the demo (skip
  reusing `validate.py`'s `QueryRunner`).** Rejected: this would duplicate a
  Protocol the kit already has, tested, and trusted; reuse is both less code
  and less risk of a second, subtly-different degrade-to-pending
  implementation drifting from the first.

## R4 -- Naming demo-created database objects to avoid collision

**Decision**: Any live-leg-created schema/table objects carry a distinct
demo-scoped marker (exact convention -- e.g. `demo_` prefix or `_seshat_demo`
suffix -- to be finalized at implementation time, not fixed here) so they
cannot be confused with, or overwrite, a real table's objects even if a
misconfigured DSN points at a real analytics database.

**Rationale**: `retail_store_sales`'s own gold objects use an `_rss` suffix
specifically to share the `gold` schema with C086 without collision (worked
example, Gold Ready section: "the objects carry an `_rss` suffix"). The same
precedent applies here, and is more urgent for a demo: a demo is exactly the
kind of thing someone might accidentally run with a DSN still set from a
previous, real session.

**Alternatives considered**:
- **Require the demo's live leg to use its own dedicated Postgres
  database/instance (never a shared one).** Considered but not mandated here:
  it would be a stronger guarantee but foists more setup burden on the
  evaluator (contradicts "in minutes"); the naming-convention guard plus the
  explicit refusal behavior (spec Stop Conditions) is judged sufficient
  without requiring dedicated infrastructure the kit does not otherwise ask
  for.

## R5 -- CLI surface shape

**Decision**: `retail demo <verb>` as a new subparser group in
`src/retail/cli.py`, following the exact `sub.add_parser(...)` pattern already
used for `check`/`validate`/`semantic-check`/`value-check`/`generate`, with
lazy imports inside each verb's handler (so the stdlib-only `retail check`
import chain is never affected by adding this feature -- Principle VIII).

**Rationale**: Consistency with the one CLI the kit already has, rather than
inventing a second entry point or a separate script. This is the path of
least surprise for anyone who already knows `retail check`/`retail validate`.

**Alternatives considered**:
- **A standalone `retail-demo` script outside the `retail` package.**
  Rejected: fragments the CLI surface for no benefit; the task's own possible-
  surface framing (`retail demo init` etc.) already implies a subcommand of
  `retail`.
