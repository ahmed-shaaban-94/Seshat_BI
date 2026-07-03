# Feature Specification: Run-Next Readiness State Machine

**Feature Branch**: `080-run-next-readiness-state-machine`

**Created**: 2026-07-03

**Status**: Draft

**Input**: User description: "Define a state-machine style, READ-ONLY agent surface
that reads the readiness artifacts and returns ONLY the next allowed action -- it
does NOT execute actions. It does not execute actions; it only identifies the next
allowed action. It must enforce stage order (the 7-stage readiness spine). It must
stop at: mapping approval, grain approval, KPI approval, semantic model readiness,
dashboard readiness, publish approval. It must return blocking reasons and evidence
gaps. It must NEVER self-promote readiness (never write a `pass`, never grant an
approval)."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
-->

### User Story 1 - "What is the one next allowed action for this table?" (Priority: P1)

An agent (or a human driving the agent) is mid-workflow on one table and wants a
single, authoritative answer to "what is the next thing I am allowed to do here,"
computed fresh from the table's committed `readiness-status.yaml` rather than
trusted blindly from a possibly-stale `next_action` string. The agent asks the
run-next surface for that table; the surface reads the table's readiness status,
walks the seven-stage spine in order starting from the first non-`pass` stage,
and returns exactly one recommended next action, OR a stop-reason if the table is
blocked, OR a human-approval-required flag if the next step needs a named-human
sign-off the agent cannot grant itself.

**Why this priority**: This is the entire feature. Every other behavior (conflict
surfacing, evidence-gap reporting, stage-order enforcement) is a refinement of this
one answer. Without it there is no MVP.

**Independent Test**: Point the surface at a single filled
`mappings/<table>/readiness-status.yaml` fixture with `mapping_ready: pass` (with a
valid `approvals[]` entry) and `silver_ready: not_started`. Confirm the surface
returns "author/apply the silver migration" (or equivalent Silver Ready action) and
nothing else -- no execution, no file written, no stage advanced.

**Acceptance Scenarios**:

1. **Given** a readiness status with `source_ready: pass` and every later stage
   `not_started`, **When** the surface is asked for the next action, **Then** it
   returns the Mapping Ready action (start/continue the source-mapping gate) and
   states the still-open prerequisite is none (source_ready already passed).
2. **Given** a readiness status with `mapping_ready: blocked` and a non-empty
   `blocking_reasons[]`, **When** the surface is asked for the next action,
   **Then** it returns a STOP response citing the exact `blocking_reasons[]` text
   verbatim, and recommends no forward action past the blocked stage.
3. **Given** a readiness status where every stage up to `dashboard_ready` is
   `pass` (with required `approvals[]` entries) and `publish_ready` is
   `not_started`, **When** the surface is asked for the next action, **Then** it
   returns the Publish Ready next action (begin the publish-readiness handoff),
   noting that a named-human publish approval is required to move Publish Ready TO
   `pass` -- and it does not simulate, record, or grant that approval. (Rationale:
   `publish_ready` is `not_started`, so it is the earliest non-`pass` stage and the
   walk returns its forward next action; the human-approval-required branch fires
   only on a stage recorded `pass` that lacks its matching approval -- see FR-005,
   data-model.md "State Transitions", and contracts/run-next-response.md. The
   publish approval gates the transition to `pass`, not entry into the stage.)

---

### User Story 2 - Stop at a named human-approval seam, never past it (Priority: P1)

A stage transition that requires a named-human sign-off (Mapping Ready, Semantic
Model Ready, Dashboard Ready, Publish Ready, and Source Ready when the source is a
file) must never be silently treated as satisfied by the surface. When the current
stage is one of these and lacks a matching, shape-valid `approvals[]` entry, the
surface's answer is "this stage needs a named-human approval" -- not a forward
action past it, and not an offer to grant it.

**Why this priority**: This is the feature's core safety property (constitution
Principle V; hard rule "never self-grant approval"). A run-next surface that
recommends stepping past an ungranted approval, or that reports the approval as
present, defeats the entire purpose of the spine's approval seams.

**Independent Test**: Feed a readiness status where `mapping_ready: pass` but
`approvals[]` has no shape-valid entry for `mapping_ready` (RS1 would already flag
this as invalid). Confirm the surface reports the approval gap rather than
recommending the Silver Ready action.

**Acceptance Scenarios**:

1. **Given** `semantic_model_ready: pass` with an `approvals[]` entry whose owner
   is a bare role token (e.g. `"metric_owner"`, no name), **When** the surface
   computes the next action, **Then** it treats the approval as ABSENT (mirroring
   RS1's shape check) and reports "Semantic Model Ready needs a named-human
   approval," never "proceed to Dashboard Ready."
2. **Given** a fully-approved chain through `dashboard_ready: pass`, **When**
   asked for the next action, **Then** the surface returns the Publish Ready
   action/approval-need and never claims to grant it itself.

---

### User Story 3 - Surface evidence gaps and stored/computed disagreement, never resolve them (Priority: P2)

A stage may be recorded `pass` with empty `evidence[]` (a recognized defect
pattern per the readiness model), or the file's own `next_action` string may
disagree with what the surface computes fresh from the stage data. In both cases
the agent needs to see the discrepancy named explicitly, not have it silently
papered over or silently overridden.

**Why this priority**: Without this, the feature degrades into "trust the stored
`next_action` field" (which readiness-viewer already renders) or "trust a `pass`
that mechanically satisfies RS1 but has no real evidence." Naming the gap is what
makes this a genuine, independent computation rather than a re-render.

**Independent Test**: Feed a readiness status with `gold_ready: pass` and
`evidence: []`. Confirm the surface's response includes an explicit "pass without
evidence" flag for that stage, in addition to whatever next action it computes.

**Acceptance Scenarios**:

1. **Given** a readiness status whose stored `next_action` text names a different
   stage than the one the surface computes from stage statuses, **When** the
   surface responds, **Then** it reports BOTH values side by side, flags the
   disagreement explicitly, and does not silently prefer or rewrite either one.
2. **Given** a `pass` stage with an empty `evidence[]` earlier in the chain than
   the stage the surface is about to recommend acting on, **When** the surface
   responds, **Then** the evidence gap is included as a caveat attached to its
   answer (the answer is not withheld, but the gap is never hidden).

---

### Edge Cases

- **Missing readiness-status.yaml entirely**: the surface reports "no readiness
  file found for this table; the next allowed action is Source Ready (start
  onboarding)" -- it does not error opaquely and does not fabricate stage history.
- **Malformed / partially-parseable YAML**: the surface reports "readiness file
  incomplete/unparseable" and does not guess the missing stage statuses (mirrors
  readiness-viewer's honest-state rule).
- **`current_stage` field disagrees with the per-stage statuses** (e.g.
  `current_stage: gold_ready` but `silver_ready.status == blocked`): the surface
  computes from the STAGE STATUSES (the walk-in-order rule), not from the
  possibly-stale `current_stage` label, and flags the disagreement.
- **Every stage already `pass` through Publish Ready with all approvals present**:
  the surface reports "all seven stages pass; no further readiness action is
  outstanding" -- it does not invent a post-spine action (e.g. it does not
  recommend running the Power BI execution adapter; that is Principle II
  execution-adapter territory, out of scope here).
- **A stage's status is an invalid/unrecognized string** (not one of the four
  readiness words): the surface reports "invalid stage status; cannot compute a
  next action past this point" rather than guessing a default.
- **`warning` status on the current stage**: per the readiness model, `warning`
  does not block the next stage. The surface returns the NEXT stage's action but
  carries the `warning` forward as a caveat, never silently drops it.
- **Two stages both `blocked`**: the surface reports the EARLIEST blocked stage
  only (stage order is walked front-to-back; a later blocked stage is unreachable
  until the earlier one clears) and names both in the response if useful context,
  but the single "next allowed action" targets the earliest blocker.
- **The file source_ready approval sub-case** (RS1's file-source encoding gate):
  when `source_ready` declares a file `source_kind` and is `pass` without a
  matching `source_ready` approval, the surface treats this exactly like any other
  missing required approval -- it is a stop condition, not a pass-through.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The surface MUST read exactly one table's committed
  `mappings/<table>/readiness-status.yaml` (ADR 0004 canonical location) as its
  sole source of stage state; it MUST NOT read any other file as an alternate
  source of stage truth.
- **FR-002**: The surface MUST compute the current position by walking the seven
  stages in fixed order (Source Ready -> Mapping Ready -> Silver Ready -> Gold
  Ready -> Semantic Model Ready -> Dashboard Ready -> Publish Ready) and finding
  the EARLIEST stage that is not `pass`. It MUST NOT rely on the file's
  `current_stage` field as its computation source (that field may be stale); it
  MAY report `current_stage` for comparison/conflict-flagging only (see FR-010).
- **FR-003**: When the earliest non-`pass` stage is `not_started` or `warning`,
  the surface MUST return that stage's single next allowed action (drawn from
  that stage's `docs/readiness/<stage>-ready.md` "Next allowed action" text) as
  its answer.
- **FR-004**: When the earliest non-`pass` stage is `blocked`, the surface MUST
  return a STOP response, MUST include that stage's `blocking_reasons[]` text
  verbatim, and MUST NOT recommend any action for a later stage.
- **FR-005**: When the stage-order walk reaches a stage that is one of the four
  named human-approval stages (Mapping Ready, Semantic Model Ready, Dashboard
  Ready, Publish Ready) -- or Source Ready when the source is a file source
  (`source_kind` in {`csv`, `tsv`, `excel`}, matching RS1's `_FILE_SOURCE_KINDS`;
  a non-file `source_kind` such as `db-table` does NOT require the Source Ready
  approval) -- and that stage is recorded `pass` but lacks a
  matching, shape-valid `approvals[]` entry (same shape rule RS1 enforces: named
  person + authority class), the surface MUST report "human approval required for
  <stage>" instead of treating that stage as cleared, and MUST NOT recommend
  proceeding past it to a later stage. (Note: a `pass` stage is not the "earliest
  non-`pass` stage" -- this rule fires on the PASS branch of the walk, when the
  surface is about to treat an approval-required `pass` stage as done and move on;
  see data-model.md "State Transitions" and contracts/run-next-response.md Example
  C for the exact placement.)
- **FR-005a (the two paths an approval-need surfaces)**: An outstanding approval
  reaches a caller by one of two paths, and the surface MUST support both. (a) The
  COMMON, correctly-recorded path: an as-yet-unapproved Mapping/Semantic stage is
  recorded `blocked` (per `docs/readiness/mapping-ready.md`, "Map is filled but
  not yet reviewed/APPROVED" is a listed BLOCKING REASON), and the need surfaces
  via FR-004 as `stop_blocked`, with the approval named in the verbatim
  `blocking_reasons[]`. (b) The SAFETY-NET path: a stage MISLABELED `pass` without
  its approval (an RS1-dirty input) is caught by FR-005 as `approval_required`.
  When both a blocked stage and a mislabeled-pass stage exist, the **earliest stage
  in walk order wins** -- and ONLY position decides: the walk returns the outcome of
  whichever stage comes first in stage order (an earlier mislabeled-`pass` stage
  yields `approval_required`; an earlier `blocked` stage yields `stop_blocked`).
  There is no type-based tie-break -- outcome TYPE never overrides walk position (see
  contracts/run-next-response.md guarantee #4). FR-005 is therefore primarily the
  mislabeled-`pass` catch, not the day-to-day mechanism -- the day-to-day mechanism
  is FR-004 over a correctly-`blocked` stage.
- **FR-006**: The surface MUST NEVER write to `readiness-status.yaml` or any other
  committed artifact. It MUST NEVER set a stage `status` to `pass`, MUST NEVER add
  or modify an `approvals[]` entry, and MUST NEVER clear a `blocking_reasons[]`
  entry. It is read-only in the strict sense: after a run, `git status` MUST show
  zero modified files.
- **FR-007**: The surface MUST NEVER emit a numeric confidence, health, or
  percent-ready score. Its output is limited to: the four readiness statuses, the
  computed next action (or stop reason, or approval-required flag), evidence
  references, and blocking reasons -- text only (constitution "No fake
  confidence").
- **FR-008**: The surface MUST NEVER execute, trigger, or invoke any build,
  validation, or publish step (`retail check`, `retail validate`, warehouse SQL,
  the Power BI execution adapter, or any other side-effecting command) as part of
  computing its answer. It answers the question "what is allowed next"; it never
  performs that action.
- **FR-009**: When a stage recorded `pass` has an empty `evidence[]`, the surface
  MUST surface this as an explicit "pass without evidence" flag attached to its
  answer, whether or not that stage is the one currently blocking forward
  progress.
- **FR-010**: When the file's own `next_action` string and the surface's freshly
  computed next action disagree (name a different stage, or a materially
  different action), the surface MUST report both values and flag the
  disagreement explicitly. It MUST NOT silently prefer one, MUST NOT rewrite the
  stored field, and MUST NOT suppress either value.
- **FR-011**: When `readiness-status.yaml` is missing entirely for the requested
  table, the surface MUST report that absence and return "Source Ready" (start
  onboarding) as the next action, without fabricating any stage history.
- **FR-012**: When `readiness-status.yaml` exists but is malformed (invalid YAML,
  not a mapping, missing the `stages` key, or a stage status outside the four
  recognized values), the surface MUST report "readiness file
  incomplete/unparseable" for the specific defect and MUST NOT guess a stage
  status or a next action past the point of the defect.
- **FR-013**: The surface MUST operate on exactly one table per invocation (a
  single `readiness-status.yaml`). Cross-table roll-up, aggregation, or
  worst-first ranking across many tables is explicitly out of scope (see
  Non-Goals) -- that is F012/readiness-viewer territory.
- **FR-014**: The surface's output MUST be traceable: every value it reports
  (a stage status, an evidence reference, a blocking reason, the current
  `approvals[]` entries) MUST be attributable to the exact source file and field
  it was read from -- never a value the surface invents.
- **FR-015**: The surface MUST treat an `approvals[]` entry as satisfying an
  approval requirement ONLY when it passes the same named-human shape check RS1
  already enforces (a non-role person name plus one of the four recognized
  authority classes, parenthesized). A bare role token, a name with no class, or
  an unrecognized class MUST be treated as "no approval," consistent with RS1 and
  with FR-005.
- **FR-016**: The surface MUST be invocable in a repo-only mode (no database
  connection, no network call) for every one of its behaviors described above --
  it never depends on a live DB or live validator output beyond what is already
  recorded as `evidence[]` text in the committed file.

### Key Entities *(include if feature involves data)*

- **Readiness Status (per table)**: the existing `mappings/<table>/readiness-status.yaml`
  artifact (ADR 0004). Read-only input; not owned or modified by this feature.
  Carries `current_stage`, the seven `stages.<stage>.{status, evidence[],
  blocking_reasons[]}` blocks, `approvals[]`, and `next_action`.
- **Stage Doc**: the existing `docs/readiness/<stage>-ready.md` per stage,
  specifically its "Next allowed action" and "Required owner / approval" fields.
  Read-only reference input this feature consults to phrase its computed action
  and to know which stages require a named-human approval.
- **Run-Next Response** (the feature's sole output shape; not a new committed
  artifact -- an ephemeral answer returned to the caller): one of {a single next
  action for a `not_started`/`warning` stage; a STOP with verbatim
  `blocking_reasons[]`; a human-approval-required flag naming the stage and
  required authority class}, plus zero or more attached caveats (evidence gaps,
  `next_action` disagreement, invalid-status defects). Never persisted to disk by
  this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For any of the acceptance-scenario fixture shapes above (an
  unblocked stage, a blocked stage, an approval-pending stage, a fully-passed
  chain, a missing file, a malformed file), the surface returns exactly one
  well-formed response and never raises an unhandled error to the caller.
- **SC-002**: Across 100% of test fixtures where a stage requires a named-human
  approval and none is recorded (or the recorded one fails the shape check), the
  surface's response never recommends an action past that stage.
- **SC-003**: Across 100% of test runs, `git status` after invocation shows zero
  modified or created files under `mappings/` or anywhere else in the repo (proof
  of read-only behavior).
- **SC-004**: Zero occurrences, across all fixtures, of a numeric score, percent,
  or confidence value appearing anywhere in the surface's response.
- **SC-005**: For every fixture where the stored `next_action` field and the
  freshly computed action disagree, both values appear in the response (never
  exactly one silently chosen).

## Assumptions

- **Assumption A1 (scope: per-table, not cross-table)**: this feature answers the
  question for ONE table's readiness status per invocation. A cross-table
  worst-first roll-up already exists (F012 `retail-control-room`) and a
  cross-table per-stage matrix already exists (F026 `readiness-viewer`); this
  feature does not re-implement either. If a caller wants "the next action for
  every table," it invokes this surface once per table (or a future orchestration
  layer does) -- that composition is out of scope here.
- **Assumption A2 (relationship to the stored `next_action` field)**: the file
  already carries a `next_action` string, written by whoever/whatever last
  updated the status file. This feature does NOT trust that string as its
  authority -- it recomputes the next action fresh from the seven stage statuses
  and the approval rules, and reports a disagreement as an explicit flag rather
  than silently preferring either value (FR-010). This is a deliberate
  independent-computation design, not a duplicate of readiness-viewer (which
  renders the stored field verbatim and never recomputes).
- **Assumption A3 (relationship to `retail-orchestrate`)**: `retail-orchestrate`
  already contains a "read disk state -> current phase/action" table it uses
  internally to decide what to sequence next, and then it EXECUTES that phase
  (build, self-heal loop, gate re-run). This feature factors the READ-ONLY
  decision half of that pattern into a standalone, independently invocable
  surface -- it does not replace or re-architect `retail-orchestrate`'s
  execution/self-heal behavior. A future refactor MAY have `retail-orchestrate`
  consume this surface's answer instead of recomputing its own inline table, but
  that wiring change is out of scope for this spec (see Non-Goals).
- **Assumption A4 (relationship to RS1)**: RS1 (`src/retail/rules/readiness_status.py`)
  is the static consistency LINTER for `readiness-status.yaml` files -- it flags
  internal contradictions (invalid status values, `pass` without evidence,
  `blocked` without reasons, an invalid approval owner shape, `current_stage`
  skipping past an earlier blocker). This feature does NOT re-implement that
  linter and does NOT add a new `retail check` rule ID. It assumes RS1 already
  ran (or would run) over the file; it happens to apply the SAME approval-shape
  rule as RS1 (FR-015) so its notion of "approved" matches the gate's, but it is
  a separate, non-gate surface that runs even on files RS1 has not (yet) checked,
  and it degrades gracefully (reports the defect) rather than assuming RS1-clean
  input.
- **Assumption A5 ("stage order" and "approval" naming maps onto existing seams,
  not new ones)**: the task description's "stop at: mapping approval, grain
  approval, KPI approval, semantic model readiness, dashboard readiness, publish
  approval" is read as six named stop-conditions that map onto the SPINE'S FOUR
  EXISTING approval-required stages, not six new gates:
  - "mapping approval" -> `mapping_ready` approval (existing).
  - "grain approval" -> the grain judgment call is a Principle-V decision made
    and recorded INSIDE the mapping gate (an `unresolved-questions.md` /
    `assumptions.md` entry feeding `mapping_ready`'s approval), not a distinct
    eighth stage. This feature does not invent a separate "grain_ready" stage.
  - "KPI approval" -> the metric-contract owner approval that gates
    `semantic_model_ready` (metric contracts owner-approved is already part of
    that stage's required evidence per `docs/architecture/readiness-pipeline.md`).
  - "semantic model readiness" -> `semantic_model_ready` (existing).
  - "dashboard readiness" -> `dashboard_ready` (existing).
  - "publish approval" -> `publish_ready` (existing).
  This reading is load-bearing: the constitution and readiness model are explicit
  that "the spine adds no new gate" and RS1 tracks exactly four approval-required
  stages plus the Source Ready file-source special case. Inventing an eighth
  ("grain_ready") or ninth ("kpi_ready") stage would contradict that. If this
  reading is wrong and the task intends genuinely new stages, that is a
  scope-changing decision -- see NEEDS CLARIFICATION #1.
- **Assumption A6 (no persisted run-state)**: "state machine" in the feature name
  describes the CONCEPTUAL model (an ordered walk through the seven stages with
  transition rules), not a running process or a persisted counter. Every
  invocation recomputes fresh from the committed `readiness-status.yaml`; the
  feature introduces no new file, cache, or daemon that remembers a "current
  position" between calls. This matches the constitution's "Recompute
  `current_stage` from committed artifacts... there is no separate run-state
  engine" and `retail-orchestrate`'s explicit "no daemon, no scheduler, no
  persisted counter."
- **Assumption A7 (delivery shape)**: consistent with how `readiness-viewer` and
  `retail-orchestrate` are delivered (an agent-facing skill/procedure the agent
  follows, backed by existing templates/docs, not a new `src/retail/rules/*.py`
  checker), this feature is expected to ship as a read-only Product Module
  (skill + short doc), not a new governance rule. The plan phase confirms this;
  see plan.md Constitution Check.
- **Assumption A8 (Power BI adapter and beyond-spine questions are out of
  scope)**: once all seven stages are `pass`, the surface reports "no further
  readiness action outstanding." It does not recommend invoking the Power BI
  execution adapter (Principle II, a later execution-only step gated on but not
  part of the readiness spine) and does not answer questions about what happens
  after Publish Ready.

## Non-Goals (explicit)

- **NG-001**: This feature does NOT execute any action it recommends (no SQL, no
  `retail check`/`retail validate` invocation as a side effect, no Power BI
  operation, no file write).
- **NG-002**: This feature does NOT grant, simulate, infer, or back-fill any
  approval. An approval is satisfied only by a pre-existing, shape-valid
  `approvals[]` entry the surface finds already committed.
- **NG-003**: This feature does NOT aggregate or rank across multiple tables
  (that is F012 `retail-control-room` / F026 `readiness-viewer` territory).
- **NG-004**: This feature does NOT replace, re-implement, or change RS1's
  consistency-linting behavior, and does NOT add a new `retail check` rule ID.
- **NG-005**: This feature does NOT change `retail-orchestrate`'s existing
  self-heal loop, its execution of build phases, or its own internal
  next-phase table. Wiring `retail-orchestrate` to consume this surface instead
  of its inline table is a separate, future decision.
- **NG-006**: This feature does NOT introduce a persisted run-state file, cache,
  daemon, or counter. Every answer is recomputed fresh per invocation.
- **NG-007**: This feature does NOT invent new readiness stages (no
  "grain_ready," no "kpi_ready") beyond the seven the spine already defines (see
  Assumption A5).
- **NG-008**: This feature does NOT connect to a live database, does NOT run a
  network call, and does NOT depend on live `retail validate` output beyond
  whatever is already recorded as committed `evidence[]` text.
- **NG-009**: This feature does NOT emit a numeric confidence/health/percent-ready
  score under any circumstance.
- **NG-010**: This feature does NOT modify `docs/readiness/*.md`, the
  constitution, or any template as part of shipping (it consumes them as
  reference input; changing their content is out of scope for this spec).

## Human-Approval Boundaries

Per constitution Principle V and the readiness model's four named-human seams,
this feature treats the following as boundaries it can only REPORT ON, never
cross or grant:

1. **Mapping Ready approval** -- named analyst/governance/data-owner sign-off on
   the source map (grain, PK, PII decisions included).
2. **Semantic Model Ready approval** -- metric-contract owner approval of the KPI
   / metric contracts.
3. **Dashboard Ready approval** -- report owner sign-off on the visual-to-contract
   binding.
4. **Publish Ready approval** -- data-owner/governance publish approval.
5. **Source Ready approval (file-source special case)** -- data-owner
   confirmation of encoding/delimiter/header for a CSV/Excel source only (RS1's
   existing rule); not required for a DB-table source.

At each of these, the surface's strongest recommendation is "this needs a named
human's sign-off, recorded as an `approvals[]` entry" -- never a workaround, never
a default acceptance, never a simulated approval.

## Safety Constraints

- **Read-only, provably so**: `git status` (or equivalent) shows no changes after
  any invocation (SC-003).
- **No score, ever**: constitution "No fake confidence" is absolute here; this
  surface is exactly the kind of aggregation point where an invented "readiness
  %" is tempting, and it is forbidden.
- **Fail loud on ambiguity, never guess**: an invalid stage status, a malformed
  file, or a disagreement between `current_stage` and the per-stage statuses is
  reported as a flag/defect, never silently resolved in either direction.
- **Stage order is authoritative over the stored label**: the walk-in-order
  computation (FR-002) is what decides the next action; `current_stage` is a
  cross-check value only, consistent with readiness-viewer's "surface conflicts,
  never resolve them" posture.

## Stop Conditions (summary)

The surface's answer is a STOP (not a forward action) when:

- The earliest non-`pass` stage is `blocked` (return the `blocking_reasons[]`).
- The earliest non-`pass` stage is `pass` but its required approval is missing or
  shape-invalid (return "approval required," naming the stage).
- The readiness file is malformed past the point where stage order can be
  determined (return "cannot compute; file defect").

The surface's answer is a forward next action only when the earliest non-`pass`
stage is `not_started` or `warning` and, if that stage requires an approval to
have already been granted for an EARLIER stage, that earlier approval is present
and shape-valid.

## Evidence Requirements

Every "pass" the surface treats as satisfied when walking the stage order MUST
carry non-empty `evidence[]` in the source file; when it does not, the surface
still uses that `pass` for its stage-order walk (it does not downgrade the file's
recorded status) but MUST attach a "pass without evidence" caveat to its answer
(FR-009). The surface never invents evidence and never treats an evidence gap as
disqualifying a `pass` it did not itself have the authority to change.

## NEEDS CLARIFICATION

Per the informed-guess policy (at most 3 markers, only for genuinely
scope-changing unknowns), the following is flagged. It does not block writing
this spec because Assumption A5 supplies a documented default; it is flagged
because a wrong default here would change the shape of the state machine itself.

1. **[NEEDS CLARIFICATION-1]**: Does "grain approval" and "KPI approval" in the
   task description mean (a) the existing judgment calls already folded into
   `mapping_ready` and `semantic_model_ready` respectively (Assumption A5's
   reading, adopted as the default in this spec), or (b) two genuinely NEW,
   separately-tracked approval stages/fields the readiness spine does not
   currently have? Adopting (b) would require a constitution/readiness-model
   amendment (a new stage or a new approval sub-field) before this feature could
   be built, which is explicitly out of scope for a spec-only slice. This spec
   proceeds under reading (a).

(Only one marker is used; the other candidate ambiguities -- the
`next_action`-disagreement handling and the persisted-state question -- were
resolved with documented defaults in Assumptions A2 and A6 because the existing
architecture and constitution already settle them unambiguously.)
