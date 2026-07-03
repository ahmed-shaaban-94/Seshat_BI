# Feature Specification: Local Demo Harness

**Feature Branch**: `083-demo-harness`

**Created**: 2026-07-03

**Status**: Draft

**Input**: User description: "Define a LOCAL demo flow that proves Seshat BI on a
GENERIC sample dataset. Possible surface: `retail demo init` / `retail demo load` /
`retail demo run` / `retail demo report`. GENERIC sample data only (invented,
neutral). No secrets. No cloud dependency. Demonstrates the readiness spine
HONESTLY (status/evidence/blockers as they really are, including pending/blocked
where a live DB isn't present). Must NOT become one-click dashboard generation."

## Why this feature, and why now

Seshat BI ships one worked example
(`docs/worked-examples/retail-store-sales.md`, backed by the public Kaggle
"retail store sales, dirty" CSV) and a reading-path tour of it
(`docs/demo/retail-store-sales-demo.md`). Neither is a **runnable** local demo: a
new evaluator cannot, in one command sequence, watch the readiness spine move
(or honestly refuse to move) against a small dataset that ships *with the kit
itself* and needs nothing external — no Kaggle download, no client data, no
live database. This feature closes that gap: a CLI-driven demo harness over an
**invented, generic** sample dataset, small enough to commit, that traverses as
much of the readiness spine as is honestly reachable **without** a live database,
and degrades visibly (not silently) to `pending`/`blocked` for the legs that need
one.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Evaluator proves the spine offline in minutes (Priority: P1)

A person evaluating Seshat BI for the first time — no DigitalOcean Postgres, no
`.env`, no `db` extra installed — wants to see the readiness spine actually move
across real, committed artifacts, on data that isn't tied to any client, within
minutes of cloning the repo.

**Why this priority**: This is the whole point of the feature. Without it,
"prove it works" requires either trusting the worked-example prose or standing
up a real Postgres instance first. A P1 that runs with zero external
dependencies is the only version of this feature worth shipping.

**Independent Test**: From a clean checkout with the repo's normal dev install
(`pip install -e ".[dev]"`, no `db` extra), run the demo verb sequence
(`retail demo init` -> `retail demo load` -> `retail demo run` -> `retail demo
report`) and confirm: (a) it completes without error, (b) it never contacts a
network or database, (c) the emitted report shows Source Ready, Mapping Ready,
AND Silver Ready reaching `pass` with cited evidence -- where Source Ready's
and Mapping Ready's `pass` each rest on a shipped, clearly-labeled illustrative
approval fixture (FR-016), and Silver Ready's `pass` rests on the committed
silver migration fixture being statically clean under `retail check` (S1-S7),
per `docs/readiness/silver-ready.md`'s "authoring only" gate -- and (d) every
stage from `gold_ready` onward is honestly `blocked`/`not_started` (never
`pass`) because Gold Ready's gate is the LIVE `retail validate`, which cannot
run without a database (`docs/readiness/gold-ready.md`: "Emit a `pass` while in
deferred mode ... is [forbidden] -- report blocked-deferred instead").

**Acceptance Scenarios**:

1. **Given** a clean checkout with only the base (non-`db`) install, **When**
   the evaluator runs the four demo verbs in order, **Then** the command
   sequence exits 0 at each step and the final report names which stages are
   `pass` (with evidence) and which are `pending`/`blocked` (with a named
   reason), never a numeric score.
2. **Given** the same offline run, **When** the evaluator inspects
   `git status` afterward, **Then** it is clean — the demo commands read
   committed fixtures and write only to an explicitly demo-scoped, git-ignored
   working area (see FR-010), never to tracked files.
3. **Given** the offline run, **When** the report reaches Gold Ready and the
   later semantic-model, dashboard, and publish stages, **Then** it reports
   them as `blocked` or `not_started` (per FR-006) with the concrete unmet
   precondition named (Gold Ready: "live `retail validate` not run -- no DB";
   later stages: "prior stage not `pass`"), never as `pass`, and never invents
   or renders a dashboard.

---

### User Story 2 - Evaluator with a local Postgres sees the live leg too (Priority: P2)

An evaluator who *does* have a local/disposable Postgres reachable (for
example, via the sibling live-validation harness) wants the same demo to
additionally exercise the live checks (`retail validate`) against the sample
data, so they can see Gold Ready reached honestly with live evidence, not just
the static legs.

**Why this priority**: It completes the story ("the spine really does reach
further with a DB") but is not required for the core value (P1 already proves
the kit is honest and runnable). It also must not become a hard dependency —
the demo cannot assume this harness exists or is running.

**Independent Test**: With `ANALYTICS_DB_*`/`DATABASE_URL` set in a local
`.env` and the `db` extra installed, run `retail demo load` (which now also
materializes the sample rows into the connected database) followed by
`retail demo run`, and confirm the report shows `gold_ready` reaching `pass`
with live-validate evidence (PK uniqueness, 0 orphan FKs, reconciliation),
while `semantic_model_ready` and beyond remain honestly gated on the
human-approval seams in FR-007.

**Acceptance Scenarios**:

1. **Given** a reachable local Postgres and the `db` extra, **When** the
   evaluator runs `retail demo load` then `retail demo run`, **Then**
   `gold_ready` reports `pass` citing an actual `retail validate` run's
   findings (not a fabricated pass).
2. **Given** the DB becomes unreachable mid-sequence (e.g., `retail demo run`
   without a prior successful `load`), **When** the evaluator re-runs `retail
   demo run`, **Then** the report reports `gold_ready` as `pending` with the
   concrete reason ("no live-validated data; DSN unset or load not run"), and
   does not crash or fake a pass.
3. **Given** a DSN is present but points at a non-demo database, **When**
   `retail demo load` runs, **Then** it refuses to write outside its own
   demo-scoped schema/table names and reports the refusal rather than risking
   collision with real data (see FR-011).

---

### User Story 3 - Evaluator sees the approval seam, not a shortcut around it (Priority: P3)

An evaluator who has completed User Story 2 wants to understand what it would
take to advance further (Semantic Model Ready and beyond), including seeing a
**pre-committed, clearly-labeled illustrative approval fixture** so they
understand the *shape* of an approval record — without the demo ever minting
one itself.

**Why this priority**: This is a comprehension/trust feature layered on top of
1 and 2 — it demonstrates Principle V (agent stops at judgment calls) rather
than just asserting it in prose, but the demo is fully valuable without it.

**Independent Test**: Run `retail demo report` after User Story 2's sequence
and confirm the report (a) names the exact human-approval seam blocking
`semantic_model_ready` (metric-contract owner sign-off), (b) if a fixture
approval ships with the sample, labels it explicitly as an illustrative,
pre-committed fixture and not something `demo run` produced, and (c) the demo
process itself never writes an `approvals[]` entry.

**Acceptance Scenarios**:

1. **Given** the sample ships a pre-committed illustrative metric-contract
   approval fixture, **When** the report renders `semantic_model_ready`,
   **Then** it labels that approval as "illustrative fixture, pre-committed
   with the sample -- not produced by this run."
2. **Given** any point in the demo sequence, **When** the evaluator diffs
   tracked files before and after, **Then** no `approvals[]` entry, contract
   file, or readiness status file was modified or created by the run itself.

---

### Edge Cases

- What happens when `retail demo run` is invoked before `retail demo init`
  (no sample fixtures materialized yet)? -> Report a clear ordering error
  naming the missing prerequisite verb; do not partially run.
- What happens when `retail demo load` is re-run after a prior successful
  load (offline or live)? -> Idempotent: re-running converges to the same
  state, consistent with Principle IX's idempotent-migration posture; it does
  not duplicate rows or error on "already exists."
- What happens when the `db` extra is installed but no DSN is configured? ->
  Same as no DB at all: the live leg is `pending`, not attempted, not an
  exception.
- What happens when a demo command finds `git status` dirty from unrelated
  work? -> The demo does not touch tracked files, so it must not care about
  pre-existing repo dirtiness; document that the "clean status" acceptance
  check is scoped to files the demo itself could plausibly touch.
- What happens if someone tries to point the demo's DSN at the real
  `ezaby_demo` / production analytics database? -> FR-011's demo-scoped
  naming convention means the demo's own objects cannot collide with real
  schema objects, but the spec must also warn (in the CLI help text / docs)
  that the demo is not meant to run against a production DSN.
- What happens when `retail demo report` is asked to run before any other
  verb (fresh clone, nothing done)? -> It renders a report showing every
  stage `not_started`, with `next_action` pointing at `retail demo init`; it
  does not error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a `retail demo` command group with at
  least the four verbs `init`, `load`, `run`, `report`, each independently
  invocable and each documented with `--help` text describing its inputs,
  outputs, and offline/live behavior.
- **FR-002**: `retail demo init` MUST materialize the committed generic sample
  dataset's fixture files (bronze-shaped source rows, already-filled mapping
  artifacts per Principle IV) into a demo-scoped working location, without
  requiring network access or a database.
- **FR-003**: `retail demo load` MUST, when no live database is configured,
  report that the live leg is skipped and why (`[PENDING LIVE PROFILE]`-style
  messaging, consistent with existing CLI conventions in
  `src/retail/validate.py` / `AGENTS.md`), without raising an unhandled
  exception.
- **FR-004**: `retail demo load` MUST, when a local database DSN is
  configured, load the sample dataset's silver/gold-shaped rows into that
  database using the demo's own namespaced schema/table names (FR-011), and
  MUST be idempotent (re-running converges to the same row state).
- **FR-005**: `retail demo run` MUST NOT implement a separate run-state
  engine. It MUST recompute each stage's status from committed artifacts,
  `retail check` exit status, and (when reachable) a `retail validate` run —
  the same "recompute, never a separate state machine" posture the readiness
  spine already mandates (AGENTS.md: "Recompute `current_stage` from committed
  artifacts ... there is no separate run-state engine"; readiness-viewer:
  "renders, never re-derives").
- **FR-006**: `retail demo run` and `retail demo report` MUST express every
  stage using only the four defined statuses (`not_started`, `blocked`,
  `warning`, `pass`) plus evidence/blocking-reasons, per
  `docs/readiness/readiness-model.md`. Neither verb MUST ever emit a numeric
  confidence/health/percent-ready score.
- **FR-007**: For each of the four human-approval-gated spine stages (Mapping
  Ready, Semantic Model Ready, Dashboard Ready, Publish Ready) -- and, for a
  CSV file source, additionally the `source_ready` encoding-confirmation
  approval that rule RS1 requires (FR-017; not a stage approval in the spine's
  sense, but the demo ships and renders it too) -- `retail demo run`/`report`
  MUST name the specific required approval and its owner class (per
  `docs/readiness/readiness-model.md`'s `approvals[]` shape) rather than
  silently reporting `blocked` with no explanation.
- **FR-008**: Neither `retail demo run` nor any other demo verb MUST write,
  modify, or synthesize an `approvals[]` entry (for ANY stage -- source_ready,
  mapping_ready, semantic_model_ready, or any other), a metric contract, a
  readiness-status stage transition, or any other governed artifact. The demo
  reads and renders; it does not grant. Any approval a stage's `pass` rests on
  MUST be a pre-committed fixture authored at fixture-build time (a
  human-reviewed act), never minted at demo-run time.
- **FR-009**: The demo's sample dataset MUST be wholly invented/generic (no
  client-specific fields, no C086 data, no re-use of the `retail_store_sales`
  Kaggle CSV) and MUST be small enough to commit as plain text fixtures (target:
  well under 1,000 rows / a few dozen KB).
- **FR-010**: All demo verbs MUST confine their writes (materialized fixtures,
  logs, any local report output) to a single git-ignored demo working
  directory; no demo verb MUST write to any tracked path. `git status` MUST be
  clean after any demo verb runs on an otherwise-clean tree.
- **FR-011**: When a live database is used, every demo-created database object
  (schema, tables) MUST carry a distinct demo-scoped naming prefix/suffix
  (e.g. an `_seshat_demo` / `demo_` convention) so it cannot collide with, or
  be mistaken for, a real table's objects (parallel to the worked example's
  `_rss` suffixing convention for sharing the `gold` schema safely).
- **FR-012**: `retail demo run` MUST detect and report the presence/absence of
  a usable live DB connection (extra installed + DSN resolvable) before
  attempting any live leg, and MUST degrade to the offline-only report path
  without raising when a live connection is unavailable, per the existing
  `resolve_dsn` / graceful-deferred-mode convention in `src/retail/validate.py`
  and `AGENTS.md`.
- **FR-013**: `retail demo report` MUST be a status/evidence/blockers report
  (text or structured data), never a rendered chart, visual, or Power BI
  artifact. It MUST NOT design, generate, or bind any dashboard visual.
- **FR-014**: The demo harness MUST NOT require, read, or write any secret or
  real credential; any DSN it uses MUST come from the same git-ignored `.env`
  / environment-variable convention as the rest of the kit (Principle IX), and
  no demo documentation or fixture MUST contain a real host or credential.
- **FR-015**: The demo harness MUST be documented (quickstart) as complementary
  to, not a replacement for, the existing worked example and its reading-path
  tour: it MUST NOT duplicate `docs/worked-examples/retail-store-sales.md` or
  `docs/demo/retail-store-sales-demo.md` content, and MUST cross-link to them
  for the "fuller narrative" reader.
- **FR-016**: EVERY pre-committed approval fixture the demo's sample data
  ships -- the `source_ready` approval (mandatory for a CSV file source, see
  FR-017), the `mapping_ready` gate approval (mandatory for Mapping Ready to
  read `pass`), and the optional `semantic_model_ready` illustrative approval
  (User Story 3) -- MUST be labeled in both the fixture file (a comment) and
  the rendered report as an illustrative, pre-committed example with a
  fictional named owner, never presented as something the demo run itself
  produced or validated.
- **FR-017**: The sample's `readiness-status.yaml` fixture, because the sample
  is a CSV file source, MUST declare `source_kind: csv` in its `source_ready`
  block and MUST ship the matching `{stage: source_ready}` approval entry the
  RS1 rule (`src/retail/rules/readiness_status.py`) requires for a file
  source's `source_ready: pass` -- otherwise `retail check` fails RS1 on the
  committed fixture. This approval is a pre-committed illustrative fixture per
  FR-016, never minted by a demo verb.

### Key Entities *(include if feature involves data)*

- **Demo sample dataset**: an invented, generic small retail-style dataset
  (entity shape only — described in `data-model.md`, not created by this spec
  work) that ships as committed bronze-shaped fixture rows plus a filled
  mapping set (source-profile, source-map, assumptions, unresolved-questions),
  independent of `retail_store_sales` and any client data.
- **Demo working directory**: a git-ignored, demo-scoped local directory where
  `init`/`load`/`run` materialize working state (loaded rows, local reports);
  never a tracked path.
- **Demo readiness snapshot**: the per-stage status/evidence/blocking-reasons
  view that `retail demo run`/`report` compute and render for the sample
  table, shaped like `templates/readiness-status.yaml` but scoped to the demo
  sample and never mutating any tracked readiness-status file.
- **Illustrative approval fixtures**: pre-committed, clearly-labeled
  `approvals[]` entries shipped with the sample data, each with a fictional
  named owner + authority class, never minted by a demo verb. TWO are
  mandatory for the offline path to be honest: a `source_ready` approval
  (required by rule RS1 for a CSV file source, FR-017) and a `mapping_ready`
  gate approval (required for Mapping Ready to read `pass`). A third,
  `semantic_model_ready`, is OPTIONAL (User Story 3) and only shipped to
  illustrate a `pass` one stage past the offline/live ceiling.

## Non-Goals (explicit)

- **NOT one-click dashboard generation.** `retail demo report` renders a
  readiness/evidence report, never a Power BI visual, PBIP artifact, or
  dashboard design. This repeats the release-notes non-goal deliberately: "Seshat
  BI is not an automatic dashboard generator; dashboards are designed from
  approved metric contracts" (`RELEASE_NOTES.md`). The demo harness does not
  create an exception to that rule for the sake of a flashier demo.
- **NOT a live-DB provisioning tool.** The demo does not stand up, install, or
  manage a Postgres instance. It optionally *uses* one if already reachable
  (locally, or via the sibling `082-postgres-live-validation-suite` harness);
  it never provisions one itself (repo `CLAUDE.md` YAGNI: "no live DB
  provisioning ... unless explicitly requested").
- **NOT a replacement for the worked example.** `docs/worked-examples/retail-store-sales.md`
  remains the canonical full narrative on real (Kaggle) data; this feature is
  a smaller, faster, fully-offline-capable, invented-data companion, not a
  competing or superseding artifact.
- **NOT an approval mechanism.** No demo verb ever writes, infers, or fakes an
  `approvals[]` entry, a readiness `pass` it cannot cite evidence for, or a
  numeric confidence score (Principle V, hard rule #9).
- **NOT a stage-skipping shortcut.** The demo obeys the same "prior stage must
  be `pass`" ordering as every other readiness workflow; it does not offer a
  "jump to Dashboard Ready" convenience path.
- **NOT client data, ever.** No C086 artifact, table name, column name, or
  business fact is reintroduced via this feature, in the sample dataset, docs,
  or fixtures.

## Relationship to sibling/adjacent work (differentiation, not overlap)

- **`docs/demo/retail-store-sales-demo.md`** is a curated **reading path**
  through the already-committed `retail_store_sales` artifacts (a documentation
  tour, no executable verbs, no invented dataset). This feature is a
  **runnable CLI harness** over a **different, invented** sample dataset. They
  are complementary reading vs. doing artifacts; neither supersedes the other.
  FR-015 requires this feature's docs to cross-link rather than duplicate.
- **`docs/worked-examples/retail-store-sales.md`** is the full narrative
  evidence record for the Kaggle-sourced worked example, including live
  validation actually run against a real database. This feature does not
  reuse that dataset (FR-009) and does not claim the live validation this
  feature performs (if any) supersedes or updates that record.
- **`082-postgres-live-validation-suite`** (sibling spec, concurrently being
  specced; not yet merged as of this writing) is the local Postgres harness
  this feature's User Story 2 may optionally sit on top of. Dependency
  direction: **083 (this feature) depends optionally on 082's local DB being
  reachable; 082 has no dependency on 083.** If 082 does not exist or is not
  running, this feature's live leg is `pending`, never an error (FR-003,
  FR-012).
- **`084-worked-example-factory`** (sibling spec, not yet on disk as of this
  writing) is expected to define *how* worked examples are authored/generalized
  as a repeatable process. This feature does not define that process; it
  *consumes* one already-shaped sample dataset and *runs* a demo over it. If
  084 ships a factory process later, a future amendment could point this
  feature's sample dataset at that process's output — out of scope here.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new evaluator with only the base (non-`db`) dev install can go
  from a clean checkout to a rendered readiness report in under 5 minutes,
  using only the four documented demo verbs, with zero network calls.
- **SC-002**: The offline demo report always shows Source Ready, Mapping
  Ready, AND Silver Ready as `pass` with cited evidence (Source/Mapping citing
  their shipped, labeled approval fixtures + committed artifacts; Silver citing
  the committed silver migration fixture's `retail check` S1-S7 exit 0), and
  always shows `gold_ready` and every later stage as `blocked`/`not_started`
  (never `pass`) when no live DB is reachable -- 100% of offline runs, no
  flakiness, no partial-pass state. Gold Ready is the honest offline ceiling
  because its gate is the live `retail validate`.
- **SC-003**: When a local DB is reachable and `retail demo load` has
  succeeded, `gold_ready` reaches `pass` citing an actual live-validate run's
  findings in 100% of such runs (never a fabricated pass).
- **SC-004**: Zero demo runs (offline or live) leave `git status` non-clean on
  an otherwise-clean tree; zero demo runs write, modify, or synthesize an
  `approvals[]` entry or any other governed artifact.
- **SC-005**: The rendered report never contains a numeric confidence/health/
  percent-ready score, in 100% of runs, across both the offline and live
  paths.
- **SC-006**: The sample dataset contains zero fields, table names, or values
  traceable to C086 or any real client, verified by a docs/fixture review
  against the C086 term list already used by existing governance checks.

## Evidence Requirements

- Every `pass` the demo report renders MUST cite the specific committed
  artifact(s) or check-run output it derives from (mirrors
  `docs/readiness/readiness-model.md`'s "a `pass` MUST cite evidence" rule) --
  never an assertion without a citable source.
- Every `blocked`/`pending` the demo report renders MUST name the concrete
  unmet precondition (missing DB, missing approval, missing artifact) --
  never a bare "not ready."
- The live leg's evidence (when run) MUST be the actual output of a real
  `retail validate` invocation against the demo's own DSN-scoped objects, not
  a canned/replayed result.

## Human-Approval Boundaries

- The demo harness itself never plays the role of the approving human at any
  of the four approval-gated spine stages (Mapping Ready, Semantic Model
  Ready, Dashboard Ready, Publish Ready), nor at the CSV `source_ready`
  encoding-confirmation approval RS1 requires (FR-017) — see FR-007, FR-008,
  FR-016.
- Every illustrative approval fixture shipped with the sample data — the
  mandatory `source_ready` (RS1) and `mapping_ready` gate approvals, and the
  optional `semantic_model_ready` one (User Story 3) — is a **pre-committed,
  static, clearly-labeled** artifact authored once as part of building this
  feature's sample data (an implementation-time, human-reviewed action) — not
  something a demo verb invents or infers at run time. This mirrors how
  `retail_store_sales`'s own approvals were recorded by a named human, not
  synthesized by tooling. The demo shipping these labeled approvals is what
  lets it show what a `pass` LOOKS like without ANY demo verb ever granting
  one — the line between "shows the shape of a pass" and the fake-pass the
  feature exists to prevent.
- If a future evaluator wants the demo's sample table to actually *reach* a
  human-gated stage for real, they must supply their own named approval the
  same way any other table would (Principle V) — the demo does not shortcut
  that for its own sample.

## Safety Constraints

- No secrets: no demo command reads or writes anything but the git-ignored
  `.env` / environment-variable convention already established (Principle
  IX); no fixture, doc, or test contains a real host, credential, or
  connection string.
- No cloud dependency: every demo verb's offline path (User Story 1) MUST
  function with zero network access. The optional live leg (User Story 2)
  MUST target only an already-locally-reachable database the evaluator
  configured themselves — the demo never reaches out to provision or discover
  a remote database.
- No collision with real data: FR-011's demo-scoped naming convention is a
  hard requirement whenever a live DB is used, precisely to prevent a
  misconfigured DSN from writing demo rows into (or reading fabricated
  confidence from) a real analytics schema.
- No governed-file writes: FR-008, FR-010, SC-004.

## Stop Conditions

- If `retail demo load`'s live leg cannot confirm it is writing to a
  demo-scoped schema/table set (FR-011), it MUST refuse to write and report
  the refusal, rather than proceeding against an ambiguous target.
- If any demo verb would need to write to a tracked path to complete its
  work, it MUST stop and report that instead of writing (FR-010) — this is a
  design defect to be caught at build time, not a runtime fallback to silently
  allow.
- If a stage's status cannot be honestly recomputed from committed artifacts
  and check output (FR-005), the verb MUST report `blocked`/`pending` with the
  reason, never guess a status.
- If the sample dataset is found (at any point, including future edits) to
  contain a field, value, or name traceable to C086 or a real client, that is
  a defect to fix immediately (Principle VII), not a deviation to record.

## Assumptions

- The demo's sample dataset is a **new, invented, generic** dataset (e.g. a
  small fictional retail store's transactions), distinct from
  `retail_store_sales` — chosen because the task explicitly calls for
  "invented, neutral" data and because a demo's value depends on being tiny,
  instant, and committable, which the existing (12,575-row, externally
  licensed) Kaggle CSV is not optimized for. The rejected alternative (reusing
  `retail_store_sales`) was set aside for that reason, not because the
  existing worked example is unsuitable for its own (narrative, full-scale)
  purpose.
- "Local" database in User Story 2 means any Postgres the evaluator has
  already made reachable via a DSN in their own `.env` — whether that is a
  literal `localhost` instance, a Docker container, or the sibling
  `082-postgres-live-validation-suite` harness. This feature does not care
  which, as long as it is not a production/client database (FR-011 guards
  against accidental collision either way).
- "Runs in minutes" (SC-001) assumes a machine with the repo's normal dev
  dependencies already installed; first-time `pip install` time is excluded.
- The CLI surface for these verbs sits under the existing `retail` command
  (`src/retail/cli.py`'s `add_parser` pattern) as a new `demo` subcommand
  group, consistent with how `check`/`validate`/`semantic-check` etc. are
  already structured — no new top-level executable.

## [NEEDS CLARIFICATION] items

None required to be blocking for this spec. The informed defaults above
(invented dataset scope, CLI surface shape, demo-scoped DB naming) are
recorded as Assumptions because they are build-guiding choices a reviewer can
accept or override without changing the feature's fundamental shape. No
scope-changing unknown was identified that would require stopping here.
