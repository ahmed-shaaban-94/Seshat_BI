# Feature Specification: Publish Approval Receipt (record-and-STOP token)

**Feature**: none (no roadmap F-number -- this idea is from the exploratory idea-bank, `docs/roadmap/idea-backlog.md`, which is "not a roadmap and not a commitment"; promotion + F-numbering is a human decision) | **Spec directory**: `041-publish-approval-receipt-record-and` (next free on-disk slot -- the create-new-feature script numbers from the current max `040`, not the first gap)

**Feature Branch**: `041-publish-approval-receipt-record-and` (located via `.specify/feature.json`)

**Created**: 2026-06-29

**Status**: Ratified (Ahmed Shaaban, 2026-06-29)

**Input**: User description: "Publish Approval Receipt (record-and-STOP token)"

**Readiness stage advanced**: Publish Ready (stage 7 of 7) -- it makes the record-and-STOP semantics already in prose at `docs/readiness/publish-ready.md` explicit IN the existing handoff pack's "Publish approval" section, WITHOUT adding a gate, an executor, or a new artifact.

## Clarifications

This block records the load-bearing ambiguities. Items marked Principle-V were deliberate
judgment calls the agent did not answer (constitution Principle V); they were recorded for
the human owner and ruled at ratification (2026-06-29). Items resolved by the advisor in
clarification are recorded under the dated session below.

### Owner judgment calls (Principle V -- RESOLVED at ratification, 2026-06-29)

- **[RESOLVED -- Principle V, Ahmed Shaaban 2026-06-29] Required authority class for the `publish_ready` sign-off.**
  RULING: the authority class is **data-owner OR governance** (either may sign off). The pack's
  "Publish approval" section names the CLASS as the placeholder `<data_owner | governance>` and
  MUST NOT pick the person; it never self-grants. This preserves the never-self-grant seam
  (Principle V): the empty owner line IS the gate.
- **[RESOLVED -- Principle V, Ahmed Shaaban 2026-06-29] Roadmap promotion + feature number.**
  RULING (owner delegated to the conservative recommended default): **stay spec-only -- NO roadmap
  F-number assigned.** The idea maps to the Publish Ready readiness stage and is implemented directly
  from this spec dir; the roadmap remains the human-curated commitment ledger and gains no row for
  this work. The spec assigns no F-number. (This default commits nothing additional and is
  reversible: promotion remains available later via the normal spec process.)
- **[RESOLVED -- Principle V, Ahmed Shaaban 2026-06-29] Receipt-vs-pack boundary ruling (Option B).**
  RULING: the record-and-STOP semantics are NOT a new standalone artifact; they FOLD INTO the
  EXISTING "Publish approval" section of `templates/handoff/bi-handoff-pack.md`. That section already
  carries the `approvals[]` / stage `publish_ready` shape, the never-self-grant gate, and the
  blocked-not-pass rule; this work only ADDS the record-and-STOP label/framing and the explicit
  "no automated publish today (F016 absent)" line. A separate standalone receipt would be a third
  presentation of sign-off facts that already live in three committed artifacts (the pack section,
  `handoff-review-checklist.md`, and the pack's readiness verdict) -- the exact duplication pattern
  this repo rejects (the idea-bank REJECTs Doc-Count Drift Guard and KPI Rollup; the rescue pattern
  is fold-and-point, as with the Net-Sales Caveat Card / DP1). Option B keeps ONE source of truth
  for publish sign-off and makes drift structurally impossible.
  (Attribution: owner Ahmed Shaaban 2026-06-29, after an owner-authorized analysis recommended B
  and the owner confirmed.)

### Session (2026-06-29, ratified by Ahmed Shaaban)

> The advisor recommendations below were integrated into the spec body during clarification.
> The 3 Principle-V items were REFUSED by the agent and left open until ratification; at
> ratification on 2026-06-29 the owner (Ahmed Shaaban) ruled all three -- see "Owner judgment
> calls" above, now RESOLVED.
>
> Clarify ledger: 3 ordinary ambiguities were resolved by the advisor (highest Impact*Uncertainty
> first) and integrated -- (1) status vocabulary -> readiness four-status set, (2) read-vs-write of
> the `approvals[]` slot -> read/cite only, (3) the Principle-IV-vs-V mislabel -> Principle V. The
> 3 Principle-V judgment calls (authority class -> data-owner OR governance; roadmap promotion ->
> stay spec-only, no F-number; receipt-vs-pack boundary -> fold into the existing pack section
> (Option B)) were the owner's to make and were ruled at ratification, not by the agent.

- Q: The publish-authorization record carries a per-stage status, but the idea text names only
  "record and STOP". Which status vocabulary does the status field admit? ->
  A (advisor, recommended): it reuses the readiness four-status set verbatim
  (`not_started` / `blocked` / `warning` / `pass`) plus `evidence[]` + `blocking_reasons[]`,
  never a fabricated score (constitution readiness-system clause; rule 9). The state is
  `pass` ONLY when a `publish_ready` approval is already recorded by a named human in
  `readiness-status.yaml` `approvals[]`; absent that, it is `blocked`
  ("no recorded publish approval"). It MUST NOT introduce a fifth status. Reasoning:
  the readiness model is the single status authority; inventing its own vocabulary
  would fork it. Reversible: easy (status text is template prose).

- Q: Does the record READ the `approvals[]` entry, or does it WRITE / re-record it? ->
  A (advisor, recommended): it POINTS AT (cites/reads) the existing `approvals[]`
  entry for stage `publish_ready` and the deliberately-empty owner line; it MUST NOT populate
  that slot. Writing the approval is the named human's action (operationalized by F027
  approval-console, which transcribes a named human's answer). The record composes with F027,
  it does not duplicate or contradict it. Reasoning: Principle V -- the agent fills every true
  field but is forbidden to populate the sign-off; the empty field IS the gate. Reversible:
  costly (a record that wrote the slot would violate Principle V -- the load-bearing constraint).

- Q: The idea text labels the un-fillable sign-off a "Principle-IV seam". Which principle is
  authoritative? -> A (advisor, recommended): Principle V (Agent Stops at Judgment Calls), NOT
  Principle IV (Source Mapping Before Silver). The idea text MIS-LABELS it; the spec cites
  Principle V throughout. Reasoning: Principle IV is the source-mapping gate; the never-self-grant
  / stop-at-judgment seam is Principle V (constitution, Principle V; the readiness-system clause
  cites Principle V for "a stage's approval is a named human action the agent cannot self-grant").
  Reversible: easy (a citation fix).

## Why this feature exists

The readiness spine defines Stage 7, **Publish Ready** (`docs/readiness/publish-ready.md`): the
BI handoff pack is complete, reviewed, and the data-owner / governance has signed off to
publish. That doc's "Next allowed action" already states the exact semantics this idea names:

> "Until feature 016 is built, the next action is to record the approved pack and STOP; there
> is no automated publish today."

The record-and-STOP behavior therefore already exists in PROSE, and the handoff pack already has
a "Publish approval" section that models the recorded sign-off. What does NOT yet exist is an
explicit statement, IN that section, that the section IS the terminal record-and-STOP
publish-authorization record: that it records authorization and the agent STOPS here because no
executor exists (F016 absent). Today an analyst who reaches Publish Ready has the prose
instruction and the pack section, but the section does not yet SAY "this IS the terminal STOP"
or honestly name the absent executor -- exactly the kind of unrecorded boundary this kit exists
to make explicit.

This feature fills that gap by **EDITING the existing "Publish approval" section of
`templates/handoff/bi-handoff-pack.md`** to add (a) a record-and-STOP label/framing -- this
section IS the terminal publish-authorization record -- and (b) an explicit
"no automated publish today; F016 (the official Power BI MCP / connection) is the deferred,
gated, execution-only owner and is verified ABSENT -- this records authorization and STOPS"
line. The section's single most important property already holds and is unchanged: the
sign-off / owner line is **deliberately un-fillable by the agent**: the agent verifies the
approval slot EXISTS and is recorded by a named human, and the section's status follows from
that; the agent never populates it. That empty-until-a-human-acts field IS the never-self-grant
gate (Principle V), now explicitly labeled as the terminal record-and-STOP token.

## The core idea: a terminal record-and-STOP token, not an executor

The single load-bearing behavior this feature adds is **making the existing pack "Publish approval"
section explicitly the publish-ready record-and-STOP token -- its sign-off line the agent cannot
self-grant -- while crossing no automation boundary and creating no new file**. Three properties
hold together:

| Property | What it means | Why it matters |
|----------|---------------|----------------|
| **Terminal record-and-STOP** | the pack's "Publish approval" section records that a table reached publish authorization and the agent STOPPED; it triggers nothing | there is no automated publish today (F016 is verified absent); the section must STATE the STOP, never imply an executor |
| **Sign-off line is agent-un-fillable** | the section CITES the `publish_ready` `approvals[]` entry + owner line; the agent verifies the slot exists, never writes it | the empty-until-a-named-human-acts field IS the gate (Principle V); self-granting would defeat the readiness system |
| **Folds into existing evidence, invents nothing** | the record-and-STOP framing is ADDED to a section that already carries the `approvals[]` shape and points at artifacts that already exist | it is a terminal label on the ONE source of truth, not a second source; it adds no number, no metric, no executor, no file |

The failure mode this feature exists to prevent is a **silent or fabricated publish
authorization**: an agent (or a careless build) marking a table "published" or "approved" with
no recorded human sign-off and no honest statement that no executor exists -- fabricating the very
publish-safety decision Principle V reserves for a human, or implying a publish happened when
none can.

## Relationship to the existing pack "Publish approval" section (Option B -- the edit, not a new file)

`templates/handoff/bi-handoff-pack.md` ALREADY models a recorded publish sign-off: its section
"Publish approval (the one non-inherited thing the pack adds)" (line 87) and its index row
`f | Publish approval | recorded sign-off in readiness-status.yaml approvals[]` (line 52) use the
`approvals[]` / stage `publish_ready` shape, the never-self-grant gate ("the agent CANNOT
self-grant it -- it STOPS"), and the blocked-not-pass rule ("Absent approval -> `publish_ready`
is `blocked`; it does NOT become `pass`"). Under the owner's Option B ruling, the deliverable
folds INTO that existing section rather than standing apart from it:

- **The pack's "Publish approval" section IS the terminal record-and-STOP publish-authorization
  token.** Option B keeps ONE source of truth for publish sign-off: this section. A separate
  standalone receipt would be a THIRD presentation of facts that already live in three committed
  artifacts (this section, `handoff-review-checklist.md`, and the pack's readiness verdict) -- the
  exact duplication the repo rejects. Folding in makes drift structurally impossible.
- **The edit ADDS only the missing words, never re-records the approval.** The section already
  carries the `approvals[]` / `publish_ready` shape, the never-self-grant gate, and the
  blocked-not-pass rule. This feature ADDS (a) the record-and-STOP label/framing and (b) the
  F016-absent line. It does not move, copy, or duplicate the sign-off; the sign-off stays where it
  already is.
- **[RESOLVED -- receipt-vs-pack boundary, Option B, owner ruling 2026-06-29]** The owner ruled
  the record-and-STOP semantics fold INTO the pack's existing "Publish approval" section
  (recorded in Clarifications -> Owner judgment calls, now RESOLVED). No standalone artifact is
  created; the section becomes the explicitly-labeled terminal token, citing (never re-recording)
  the `approvals[]` sign-off it already verifies.

## Relationship to F027 (approval-console -- composes, never contradicts)

F027 (the `approval-console` skill, SHIPPED) is the adjacent machinery that WRITES `approvals[]`
entries -- it transcribes a named human's answer into the readiness status, never authors the
decision (its transcribe-never-author boundary). The pack's "Publish approval" section is the
publish-stage terminal record of the SAME never-self-grant seam:

- F027 is HOW a `publish_ready` approval gets recorded (a human decides; F027 transcribes).
- The pack's "Publish approval" section is WHAT terminally points at that recorded approval and
  STOPS. It READS the slot F027 writes; it never writes it and never re-runs F027.
- The section MUST compose with F027, not duplicate it: it is `pass` only when the
  `approvals[]` entry F027 (or an equivalent named-human action) already recorded EXISTS.

## Relationship to F016 (the it-is-NOT-an-executor boundary)

This feature deliberately sits at the boundary of F016 (the deferred Power BI EXECUTION adapter --
the official Power BI MCP / connection; `pbi-cli` no longer preferred). F016 is verified ABSENT
from `src/` (the roadmap: "NOT BUILT -- the only remaining feature, gated by design"). The
section's honesty depends on STATING that absence -- which is exactly the line this feature adds:

- **F016 is EXECUTION AUTOMATION** that would publish an already-approved model to a workspace.
  Roadmap rule #6 / Principle II make it the last, gated, execution-only step.
- **The pack's "Publish approval" section is a record-and-STOP record, not an executor.** It
  records authorization and STOPS; it triggers no publish, no deployment, no Fabric action, and
  runs no pbi-cli / Power BI MCP command. It must NEVER imply an executor exists.
- **The section is therefore INDEPENDENT of F016, not blocked by it.** "No current readiness
  stage depends on F016" (roadmap). The added line explicitly STATES "no automated publish today"
  and names F016 as the owner of any future publish; if asked to publish, the agent STOPS.

## Architecture (a docs/templates authoring slice; no code, no rule, no CLI, no DB)

The slice is committed text only; it adds NO `retail check` rule, NO CLI verb, NO Python, opens
NO DB connection (Principle VIII; rule 8 docs/templates-first):

- **One edited existing section** -- `templates/handoff/bi-handoff-pack.md` "Publish approval"
  section: this work ADDS, to the section that already exists, (a) a record-and-STOP label/framing
  (this section IS the terminal publish-authorization record) and (b) the explicit
  "no automated publish today (F016 absent) -- this records authorization and STOPS" line. The
  section already carries the table's pack context, the CITED `publish_ready` `approvals[]` entry +
  the deliberately-empty owner line, the never-self-grant gate, the blocked-not-pass rule, and a
  status from the readiness four-status set with `evidence[]` + `blocking_reasons[]`. NO new file
  is created. The per-table filled instance is the EXISTING per-table pack copy
  `mappings/<table>/handoff/bi-handoff-pack.md`.
- **One non-gating doc note** -- `docs/readiness/publish-ready.md` gains a ONE-LINE, NON-GATING
  `evidence[]`-style note pointing at the pack's "Publish approval" section
  (`templates/handoff/bi-handoff-pack.md`) as the concrete record of the record-and-STOP action. It
  adds NO new blocking reason, NO new gate, NO new status, and NO new required artifact; the
  stage's gates (prior stages `pass`; handoff review; recorded approval) are unchanged.

There is NO new `retail check` rule, NO CLI command, NO Python, NO new file, and NO
publish/executor step -- by design. The agent's role is to EDIT the existing pack section + add
the non-gating note and, per table, to VERIFY (read-only) that the `approvals[]` slot EXISTS --
never to populate the sign-off, never to publish.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The pack's "Publish approval" section records the terminal publish-authorization, points at the recorded approval, and STOPS (Priority: P1)

A table has reached Publish Ready: stages 1-6 are `pass`, the handoff pack is complete and
reviewed, and a named human (via F027 or an equivalent recorded action) has recorded a
`publish_ready` approval in `readiness-status.yaml` `approvals[]`. The analyst wants the pack's
"Publish approval" section to read as a concrete, reviewable terminal record: "this table is
recorded as publish-authorized; the pack it terminalizes is this very bundle; no executor exists
today; STOP." Filling the pack, the agent completes every TRUE field of the section -- the cited
approval entry, the explicit no-executor (F016-absent) statement, the record-and-STOP label --
and leaves the sign-off / owner line as a pointer to the recorded `approvals[]` owner, NEVER
populating it itself. The section's status reads `pass` because a recorded approval exists; the
committed pack is reviewed in git like any handoff artifact.

**Why this priority**: this is the feature. Making the pack's "Publish approval" section
explicitly the record-and-STOP terminal token -- with an agent-un-fillable sign-off and an honest
F016-absent statement -- is the one Publish Ready step that the section did not yet state.
Everything else is the guardrail around it.

**Independent Test**: for a fixture table at Publish Ready with a recorded `publish_ready`
approval, fill the pack; an auditor confirms the "Publish approval" section's every true field is
populated, the sign-off / owner line CITES the recorded `approvals[]` owner (and is not authored
by the agent), the section states "no automated publish today (F016 absent)", the status is `pass`
with `evidence[]` citing the pack + the approval, and 0 publish/executor actions occurred.

**Acceptance Scenarios**:

1. **Given** a table whose stages 1-6 are `pass`, whose pack is complete and reviewed, and whose
   `readiness-status.yaml` records a `publish_ready` `approvals[]` entry by a named human,
   **When** the agent fills the pack's "Publish approval" section, **Then** every true field is
   populated, the sign-off / owner line cites the recorded approval owner (agent authors nothing
   in it), the section states no executor exists today, and the status is `pass` with `evidence[]`
   citing the pack + approval.
2. **Given** the filled pack section, **When** it is committed and reviewed in git, **Then** it is
   a plain-text record a reviewer reads like code, it triggers no publish, and it adds no readiness
   gate, status, or rule beyond the existing Publish Ready stage.
3. **Given** the section, **When** it is inspected, **Then** it carries NO numeric confidence /
   readiness / health score -- only the four-status verdict + `evidence[]` + `blocking_reasons[]`.

### User Story 2 - Refuse to self-grant: leave the sign-off un-filled and STOP when no approval is recorded (Priority: P1)

A request would have the agent "approve publish", "sign off", or "mark this published" for a
table whose `readiness-status.yaml` records NO `publish_ready` approval. The pack section's
load-bearing constraint -- the sign-off / owner line is the never-self-grant gate (Principle V) --
makes the agent REFUSE to populate it. It records the section as `blocked` ("no recorded publish
approval"), names the authority class as a placeholder it does NOT fill, points the owner at F027
(the recorded-approval path), and STOPS. The agent never writes the sign-off, never invents the
owner, and never marks `publish_ready: pass`.

**Why this priority**: the un-fillable sign-off is the whole point (Principle V). A pack section
that let the agent self-grant -- or fabricate an owner -- would defeat the readiness system and the
constitution's load-bearing judgment-call floor. Refusing is as load-bearing as recording.

**Independent Test**: for a fixture table with no recorded `publish_ready` approval (and one whose
prior stages are not all `pass`), an "approve / sign-off / publish" request yields a pack section
with the sign-off line UN-FILLED, status `blocked` with the matching blocking reason, the authority
class left as a placeholder, and 0 self-granted approvals; an auditor confirms the agent authored
nothing in the sign-off slot in every case.

**Acceptance Scenarios**:

1. **Given** a table with no recorded `publish_ready` approval, **When** the agent is asked to
   complete the section, **Then** the sign-off / owner line is left UN-FILLED (a placeholder
   pointer), the status is `blocked` ("no recorded publish approval"), and the agent points at the
   recorded-approval path (F027) and STOPS.
2. **Given** a request to "just sign it off" or "mark it approved", **When** the agent responds,
   **Then** it REFUSES to populate the sign-off (Principle V), records the refusal as the blocking
   reason, and never writes an owner or a date into the `approvals[]` slot.
3. **Given** a table whose stages 1-6 are not all `pass`, **When** the section is attempted,
   **Then** the status is `blocked` with the not-pass prior stage as the blocking reason, never
   `pass`, and no sign-off is authored.

### User Story 3 - Stay strictly inside the record-and-STOP boundary: no executor, no publish (Priority: P1)

A user asks the pack's "Publish approval" section to "publish to the workspace", "run the Power BI
adapter", "deploy to Fabric", or "trigger the release". The section STOPS at the record-and-STOP
boundary: it records authorization state and names F016 (verified absent) as the owner of any
publish. The slice runs no pbi-cli / Power BI MCP command, opens no DB connection, deploys nothing,
and the section's text NEVER implies an executor exists.

**Why this priority**: this is the boundary that keeps the section from being read as an executor
or as pre-empting the deferred, gated F016 (rule #6, Principle II). Recording authorization is
allowed; publishing it is F016's role, and F016 does not exist yet.

**Independent Test**: across a fixture set of requests including "publish", "run the adapter",
"deploy to Fabric", the section produces zero publish/executor output, names F016 in each case,
and an auditor confirms 0 pbi-cli/MCP commands, 0 publish actions, 0 DB connections, and that the
section text states "no automated publish today (F016 absent)" rather than implying an executor.

**Acceptance Scenarios**:

1. **Given** a request to "publish to the workspace", **When** the agent responds, **Then** it
   STOPS, records authorization state only, and names F016 as the owner of any publish -- it
   performs no publish and runs no command.
2. **Given** a request to "deploy to Fabric" or "run the Power BI execution adapter", **When** the
   agent responds, **Then** it STOPS and names F016 (verified absent), performing no deployment and
   opening no connection.
3. **Given** the slice's committed edit, **When** it is inspected, **Then** it contains 0
   pbi-cli/MCP commands, 0 publish/deploy steps, 0 DB connections, 0 new `retail check` rules, and
   the section text explicitly states no executor exists today.

### Edge Cases

- **The recorded approval is later retracted upstream.** If the `publish_ready` `approvals[]`
  entry is removed or the prior-stage gate regresses, the section's status MUST follow the
  readiness status (back to `blocked`); the section does not silently keep a stale `pass`. It
  reflects the recorded state, it does not freeze it.
- **A consumer asks to add an authority the section does not name.** Naming the required authority
  class (data-owner / governance / both) is a Principle V judgment call left to the owner; the
  agent records it as a placeholder and STOPS, never picking the person.
- **Windows path / encoding limits.** The pack copied to `mappings/<table>/handoff/` plus short
  table names must stay under the 260-char path limit; committed text is ASCII, UTF-8 without BOM
  (CLAUDE.md hard rules; Principle IX).
- **The section is mistaken for a publish trigger.** The "Publish approval" section MUST read as a
  terminal RECORD, not a command. Its label, status, and no-executor statement make explicit that
  it triggers nothing -- it is reviewed in git, not "run".
- **The first filled instance is the existing per-table pack copy.** The generic
  `templates/handoff/bi-handoff-pack.md` "Publish approval" section carries placeholders only; the
  first filled instance is the EXISTING per-table copy at
  `mappings/retail_store_sales/handoff/bi-handoff-pack.md` (C086). No C086/pharmacy specifics
  (table name, segments, PII columns, named approver) may appear in the generic template
  (Principle VII).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The slice MUST EDIT the EXISTING "Publish approval" section of
  `templates/handoff/bi-handoff-pack.md` to ADD (a) a record-and-STOP label/framing -- this
  section IS the terminal publish-authorization record -- and (b) an explicit
  "no automated publish today; F016 (the official Power BI MCP / connection) is the deferred,
  gated, execution-only owner and is verified ABSENT -- this records authorization and STOPS"
  line. It MUST create NO new standalone file. The section's existing `approvals[]` / stage
  `publish_ready` shape, never-self-grant gate, blocked-not-pass rule, and four-status verdict are
  preserved; this work only ADDS the missing record-and-STOP + F016-absent words.
- **FR-002**: The section's sign-off / owner line MUST remain deliberately UN-FILLABLE by the
  agent: the agent verifies the `publish_ready` `approvals[]` slot EXISTS and is recorded by a named
  human, and CITES it; it MUST NOT populate the owner, the date, or the approval itself. That
  empty-until-a-named-human-acts field IS the never-self-grant gate (Principle V).
- **FR-003**: The section MUST compose with the recorded approval written by F027 (approval-console)
  or an equivalent named-human action -- it READS / CITES the `approvals[]` entry; it MUST NOT
  re-record it, duplicate F027, or run F027.
- **FR-004**: The section's status MUST be drawn from the readiness four-status set
  (`not_started` / `blocked` / `warning` / `pass`) with `evidence[]` + `blocking_reasons[]`. It is
  `pass` ONLY when a `publish_ready` approval is already recorded by a named human; absent that, it
  is `blocked` ("no recorded publish approval"). It MUST NOT introduce a fifth status.
- **FR-005**: The section MUST carry NO fabricated confidence / readiness / health NUMBER anywhere
  -- statuses + evidence + blockers only (rule #9).
- **FR-006**: The slice MUST add a ONE-LINE, NON-GATING note to `docs/readiness/publish-ready.md`
  pointing at the pack's "Publish approval" section (`templates/handoff/bi-handoff-pack.md`) as the
  concrete record of the record-and-STOP action. It MUST NOT add a new gate, a new blocking reason,
  a new status, or a new required artifact; the stage's existing gates (prior stages `pass`;
  handoff review; recorded approval) stay unchanged.
- **FR-007**: The slice MUST NOT publish, deploy, trigger a release, run any pbi-cli / Power BI MCP
  command, open any DB connection, or deploy to Fabric, and the section text MUST NOT imply an
  executor exists. Any such request is STOPPED and F016 (verified absent) is named as the owner
  (rule #6, Principle II).
- **FR-008**: The slice MUST add NO new `retail check` rule, NO CLI verb, and NO Python code; it is
  a docs/templates authoring slice (Principle VIII; rule 8). `retail check` MUST exit 0 with its
  rule count UNCHANGED.
- **FR-009**: The edited generic section + the doc note MUST stay GENERIC to retail BI
  (Principle VII): no C086/pharmacy or other subject-area specifics (table name, segments, PII
  columns, named approver) in any committed generic file. The first filled instance lives only in
  the existing per-table pack copy `mappings/<table>/handoff/bi-handoff-pack.md` and the worked
  example is cited by reference, never inlined.
- **FR-010**: The spec and the section MUST cite Principle V (Agent Stops at Judgment Calls) as the
  owning principle of the never-self-grant seam -- NOT Principle IV. (The idea text mislabels it
  "Principle-IV"; that is corrected here.)
- **FR-011**: The slice MUST stop at Principle V judgment calls -- the required authority class for
  the sign-off, whether to promote this onto the roadmap / assign an F-number, and the
  receipt-vs-pack boundary ruling -- surfacing them to the human owner (recorded in Clarifications
  -> Owner judgment calls; all three RESOLVED at ratification) rather than self-answering or
  self-granting.
- **FR-012**: The section's status MUST reflect the recorded readiness state and MUST NOT freeze a
  stale `pass`: if the recorded approval is retracted or a prior-stage gate regresses, the section
  follows the readiness status back to `blocked`.
- **FR-013**: All committed files MUST be ASCII, UTF-8 without BOM (use `--` and `->`, no glyphs),
  with short repo-relative paths (`<= 200` chars) honoring the Windows 260-char limit, and MUST NOT
  bake in any real connection host or secret (Principle IX).

### Key Entities

- **Pack "Publish approval" section (the edited section -- ONE source of truth)**: the
  "Publish approval" section of `templates/handoff/bi-handoff-pack.md` (generic) and its per-table
  filled copy under `mappings/<table>/handoff/bi-handoff-pack.md` -- the terminal record-and-STOP
  publish-authorization token recording the table's pack context, the CITED `publish_ready`
  `approvals[]` entry, the deliberately-empty sign-off / owner line, the explicit no-executor
  (F016-absent) statement, and a four-status verdict + `evidence[]` + `blocking_reasons[]`.
  Recorded and reviewed in git; it triggers nothing. This work ADDS the record-and-STOP label and
  the F016-absent line; it creates no new file.
- **Recorded publish approval (cited input, NOT written by the section)**: the `publish_ready`
  entry in `mappings/<table>/readiness-status.yaml` `approvals[]` (`{stage, owner, at}`), recorded
  by a named human via F027 or an equivalent action. The section cites it; it never writes it.
- **BI handoff pack (the host bundle)**: `templates/handoff/bi-handoff-pack.md` (and its filled
  per-table copy) -- the bundle whose "Publish approval" section IS the terminal token. Under
  Option B the token is not a separate object; it is this section of this pack.
- **Publish Ready doc note (output)**: the one-line, non-gating `evidence[]`-style note in
  `docs/readiness/publish-ready.md` pointing at the pack's "Publish approval" section -- no new
  gate, status, or rule.
- **F027 approval-console (composes-with, NOT invoked)**: the shipped machinery that WRITES
  `approvals[]` from a named human's answer. The section reads the slot F027 writes; it never runs
  or duplicates F027.
- **F016 Power BI execution adapter (the deferred boundary, verified ABSENT, NOT an input)**: the
  execution-only adapter that WOULD publish. Named as the owner of any publish; never invoked; its
  absence is stated honestly by the added line.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The existing "Publish approval" section of `templates/handoff/bi-handoff-pack.md` is
  EDITED to carry the record-and-STOP label and the explicit "no automated publish today
  (F016 absent)" line, while preserving its `approvals[]` shape, never-self-grant gate, and
  blocked-not-pass rule; NO new standalone file is created; a reviewer scanning the generic section
  finds placeholders only and 0 subject-area specifics.
- **SC-002**: In 100% of filled instances, the sign-off / owner line is CITED from the recorded
  `approvals[]` entry, never authored by the agent; across all runs the agent self-grants the
  publish sign-off in 0 cases (Principle V holds 100% of the time).
- **SC-003**: For a fixture table with a recorded `publish_ready` approval the section reads `pass`
  with `evidence[]` citing the pack + approval; for a fixture with NO recorded approval (or a
  not-pass prior stage) it reads `blocked` with the matching blocking reason -- in 100% of gated
  cases the status follows the recorded readiness state.
- **SC-004**: Across all runs the slice emits 0 publish/deploy actions, 0 pbi-cli / Power BI MCP
  commands, 0 DB connections, and 0 Fabric deployments; the section text states "no automated
  publish today (F016 absent)" and implies an executor in 0 places (rule #6 holds 100%).
- **SC-005**: The slice adds 0 new readiness stages, 0 new readiness statuses, 0 new blocking
  reasons to the stage, 0 new required artifacts, 0 new files, and 0 new `retail check` rules; the
  doc note is non-gating; `retail check` exits 0 with its rule count UNCHANGED.
- **SC-006**: 0 fabricated confidence / readiness / health numbers appear in the edited section or
  any filled instance -- statuses + evidence + blockers only (rule #9).
- **SC-007**: 0 C086/pharmacy or other subject-area specifics appear in any committed GENERIC
  artifact (the edited section, the doc note); the worked example is cited by reference only
  (Principle VII).
- **SC-008**: The spec and the section cite Principle V (not Principle IV) as the owning principle
  in 100% of references to the never-self-grant seam; 0 references mislabel it "Principle IV".
- **SC-009**: All committed files are ASCII + UTF-8 no BOM with repo-relative paths `<= 200` chars
  under the Windows 260-char limit; 0 real hosts/secrets appear in any committed file.

## Assumptions

- **Publish Ready (stage 7) and its gates are unchanged.** The stage's gates (prior stages 1-6
  each `pass`; the handoff review; the recorded data-owner / governance approval) and its owner
  stay exactly as `docs/readiness/publish-ready.md` defines them. This feature adds a non-gating
  EVIDENCE-style note + a record-and-STOP label on the existing pack section, NOT a gate (no
  divergent source of truth -- constitution Governance amendment clause).
- **F027 (approval-console) is the shipped recorded-approval path and is SHIPPED.** The section
  composes with it: F027 (or an equivalent named-human action) WRITES the `publish_ready`
  `approvals[]` entry; the section READS / CITES it and never re-records it.
- **F016 (the Power BI execution adapter) is the deferred publish/execution engine and is verified
  ABSENT from `src/`** (roadmap: "NOT BUILT -- the only remaining feature, gated by design"). A
  record-and-STOP record is NOT F016 and does not wait on it (rule #6 gates the automation, not
  the record). The section states the absence honestly.
- **This idea has NO roadmap F-number.** It is from the exploratory idea-bank
  (`docs/roadmap/idea-backlog.md`), which is "not a roadmap and not a commitment". It maps to the
  Publish Ready readiness stage and is implemented directly from this spec dir; whether to promote
  it and assign an F-number is a human decision (recorded in Clarifications -> Owner judgment calls;
  the owner ruled stay-spec-only at ratification). This spec assigns none.
- **The never-self-grant seam is owned by Principle V, not Principle IV.** The idea text mislabels
  it; the spec corrects it. Principle IV is Source Mapping Before Silver; Principle V is Agent Stops
  at Judgment Calls (the readiness-system clause cites Principle V for "a stage's approval is a
  named human action the agent cannot self-grant").
- **The receipt-vs-pack boundary is RESOLVED as Option B.** The existing `bi-handoff-pack.md`
  "Publish approval" section already uses the `approvals[]` / `publish_ready` shape; the owner ruled
  the record-and-STOP semantics FOLD INTO that section rather than standing as a separate file
  (Clarifications -> Owner judgment calls, RESOLVED). One source of truth for publish sign-off;
  drift is structurally impossible.
- **The first worked instance is `retail_store_sales` (C086).** C086 is the prior worked example,
  not the schema (rule #7, Principle VII); the generic pack section carries placeholders only and
  cites the worked example by reference; the first filled instance is the existing per-table copy
  at `mappings/retail_store_sales/handoff/bi-handoff-pack.md`.
- **Reuse over new surface (Principle II, YAGNI):** docs/templates only -- no new file, no new
  `retail check` rule, no CLI verb, no Python, no DB connection, no executor. The value is the
  record-and-STOP label folded into the existing pack section + the non-gating note.
- **This is a planning + authoring slice consistent with the readiness roadmap** (Publish Ready,
  stage 7). It changes no existing gate, moves no existing doc's authority, and writes no runtime
  code.
