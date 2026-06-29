# Feature Specification: Publish Approval Receipt (record-and-STOP token)

**Feature**: none (no roadmap F-number -- this idea is from the exploratory idea-bank, `docs/roadmap/idea-backlog.md`, which is "not a roadmap and not a commitment"; promotion + F-numbering is a human decision) | **Spec directory**: `041-publish-approval-receipt-record-and` (next free on-disk slot -- the create-new-feature script numbers from the current max `040`, not the first gap)

**Feature Branch**: `041-publish-approval-receipt-record-and` (located via `.specify/feature.json`)

**Created**: 2026-06-29

**Status**: Draft

**Input**: User description: "Publish Approval Receipt (record-and-STOP token)"

**Readiness stage advanced**: Publish Ready (stage 7 of 7) -- it makes the record-and-STOP semantics already in prose at `docs/readiness/publish-ready.md` a concrete, copy-me artifact, WITHOUT adding a gate or an executor.

## Clarifications

This block records the load-bearing ambiguities. Items marked `[OPEN -- Principle V]`
are deliberate judgment calls the agent MUST NOT answer (constitution Principle V): they
are recorded for the human owner and left as `[NEEDS CLARIFICATION]` markers in the body.
Items resolved by the advisor in clarification are recorded under a dated session below.

### Open for human (Principle V -- not answered here)

- **[OPEN -- Principle V] Required authority class for the `publish_ready` sign-off.**
  `docs/readiness/publish-ready.md` says "data-owner / governance" approves publish. WHO is
  the required authority class -- data-owner, governance, or both -- is a publish-safety
  judgment call. The receipt template MUST name the authority CLASS as a placeholder
  (`<data_owner | governance>`) and MUST NOT pick the person; it never self-grants. This is
  the never-self-grant seam (Principle V) made concrete.
- **[OPEN -- Principle V] Roadmap promotion + feature number.** This idea maps to the
  Publish Ready readiness stage but carries NO roadmap F-number (it is from the non-committal
  idea-bank). Whether to promote it onto `docs/roadmap/roadmap.md` and assign an F-number is a
  human decision via the normal spec process; the spec does not assign one.
- **[OPEN -- Principle V] Receipt-vs-pack boundary ruling.** `templates/handoff/bi-handoff-pack.md`
  already carries a "Publish approval" section using the identical `approvals[]` / `publish_ready`
  shape. Whether the new `publish-receipt.md` is a genuinely DISTINCT terminal authorization
  object or a DUPLICATE of the pack's existing section is a human ruling so the kit does not ship
  two competing publish-sign-off artifacts. This spec states the candidate boundary (below) but
  does not ratify it; the owner rules.

### Session (date pending)

> The operator MUST fill the session date before this block is considered authoritative;
> scripts cannot supply a real date. The advisor recommendations below were integrated into
> the spec body during clarification; the Principle V items above were NOT answered.
>
> Clarify ledger: 3 ordinary ambiguities were resolved by the advisor (highest Impact*Uncertainty
> first) and integrated -- (1) status vocabulary -> readiness four-status set, (2) read-vs-write of
> the `approvals[]` slot -> read/cite only, (3) the Principle-IV-vs-V mislabel -> Principle V. The
> 3 Principle-V judgment calls (authority class; roadmap promotion / F-number; receipt-vs-pack
> boundary) were REFUSED and recorded in "Open for human" above; none is build-blocking -- the
> generic template's shape is fully specifiable without them.

- Q: The receipt records a per-stage publish status, but the idea text names only
  "record and STOP". Which status vocabulary does the receipt's status field admit? ->
  A (advisor, recommended): the receipt reuses the readiness four-status set verbatim
  (`not_started` / `blocked` / `warning` / `pass`) plus `evidence[]` + `blocking_reasons[]`,
  never a fabricated score (constitution readiness-system clause; rule 9). A receipt is
  `pass` ONLY when a `publish_ready` approval is already recorded by a named human in
  `readiness-status.yaml` `approvals[]`; absent that, the receipt is `blocked`
  ("no recorded publish approval"). The receipt MUST NOT introduce a fifth status. Reasoning:
  the readiness model is the single status authority; a receipt inventing its own vocabulary
  would fork it. Reversible: easy (status text is template prose).

- Q: Does the receipt READ the `approvals[]` entry, or does it WRITE / re-record it? ->
  A (advisor, recommended): the receipt POINTS AT (cites/reads) the existing `approvals[]`
  entry for stage `publish_ready` and the deliberately-empty owner line; it MUST NOT populate
  that slot. Writing the approval is the named human's action (operationalized by F027
  approval-console, which transcribes a named human's answer). The receipt composes with F027,
  it does not duplicate or contradict it. Reasoning: Principle V -- the agent fills every true
  field but is forbidden to populate the sign-off; the empty field IS the gate. Reversible:
  costly (a receipt that wrote the slot would violate Principle V -- the load-bearing constraint).

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

The record-and-STOP behavior therefore already exists in PROSE. What does NOT exist is a
concrete, copy-me ARTIFACT that makes that STOP a durable, reviewable token: a small terminal
receipt a human can point at to say "this table is recorded as publish-authorized, and the
agent stopped here because there is no executor". Today an analyst who reaches Publish Ready has
the prose instruction but no committed object that captures the STOP -- exactly the kind of
unrecorded boundary this kit exists to make explicit.

This feature fills that gap with a **publish approval receipt**: a GENERIC template
(`templates/handoff/publish-receipt.md`) that records the terminal publish-authorization state
of a table -- citing the recorded approval, the pack it terminalizes, and the verified absence
of an executor -- and STOPS. Its single most important property is that the sign-off / owner
line is **deliberately un-fillable by the agent**: the agent verifies the approval slot EXISTS
and is recorded by a named human, and the receipt's own status follows from that; the agent
never populates it. That empty-until-a-human-acts field IS the never-self-grant gate
(Principle V), made into a concrete artifact.

## The core idea: a terminal record-and-STOP token, not an executor

The single load-bearing behavior this feature adds is **turning the publish-ready record-and-STOP
prose into a committed, reviewable receipt whose sign-off line the agent cannot self-grant, while
crossing no automation boundary**. Three properties hold together:

| Property | What it means | Why it matters |
|----------|---------------|----------------|
| **Terminal record-and-STOP** | the receipt records that a table reached publish authorization and the agent STOPPED; it triggers nothing | there is no automated publish today (F016 is verified absent); the receipt must STATE the STOP, never imply an executor |
| **Sign-off line is agent-un-fillable** | the receipt CITES the `publish_ready` `approvals[]` entry + owner line; the agent verifies the slot exists, never writes it | the empty-until-a-named-human-acts field IS the gate (Principle V); a receipt that self-granted would defeat the readiness system |
| **Composes existing evidence, invents nothing** | every field points at an artifact that already exists (the pack, the recorded approval, the readiness status) | the receipt is a terminal pointer, not a second source of truth; it adds no number, no metric, no executor |

The failure mode this feature exists to prevent is a **silent or fabricated publish
authorization**: an agent (or a careless build) marking a table "published" or "approved" with
no recorded human sign-off and no honest statement that no executor exists -- fabricating the very
publish-safety decision Principle V reserves for a human, or implying a publish happened when
none can.

## Relationship to the existing pack "Publish approval" section (the boundary that MUST be stated)

`templates/handoff/bi-handoff-pack.md` ALREADY models a recorded publish sign-off: its section
"Publish approval (the one non-inherited thing the pack adds)" (line 87) and its index row
`f | Publish approval | recorded sign-off in readiness-status.yaml approvals[]` (line 52) use the
identical `approvals[]` / stage `publish_ready` shape this receipt points at. So the boundary
MUST be stated, or this feature would ship a second, competing publish-sign-off artifact:

- **The pack's "Publish approval" section is a COMPLETENESS check inside the bundle.** It is one
  row of the handoff pack's required-section index -- "is a sign-off recorded? path / GAP" -- one
  element of the larger pack that the handoff-review checklist gates. It lives INSIDE the pack.
- **The candidate publish receipt is a TERMINAL TOKEN that points at that same recorded sign-off.**
  It is the small standalone object that says "this table's publish authorization is recorded
  HERE, the pack it terminalizes is THERE, no executor exists, STOP". It does not re-record the
  approval; it cites the one the pack's section already verifies.
- **[NEEDS CLARIFICATION: receipt-vs-pack boundary -- Principle V human ruling]** Whether this
  terminal token is genuinely DISTINCT from the pack's section, or is a DUPLICATE that should
  instead be folded into the pack, is a human ruling (recorded in Clarifications -> Open for human).
  This spec describes the candidate distinct-terminal-token shape; it does NOT ratify shipping two
  artifacts. If the owner rules it a duplicate, the deliverable is a pointer/section change, not a
  new competing template.

## Relationship to F027 (approval-console -- composes, never contradicts)

F027 (the `approval-console` skill, SHIPPED) is the adjacent machinery that WRITES `approvals[]`
entries -- it transcribes a named human's answer into the readiness status, never authors the
decision (its transcribe-never-author boundary). The receipt is the publish-stage terminal token
of the SAME never-self-grant seam:

- F027 is HOW a `publish_ready` approval gets recorded (a human decides; F027 transcribes).
- The receipt is WHAT terminally points at that recorded approval and STOPS. It READS the slot
  F027 writes; it never writes it and never re-runs F027.
- The receipt MUST compose with F027, not duplicate it: a receipt is `pass` only when the
  `approvals[]` entry F027 (or an equivalent named-human action) already recorded EXISTS.

## Relationship to F016 (the it-is-NOT-an-executor boundary)

This feature deliberately sits at the boundary of F016 (the deferred Power BI EXECUTION adapter --
the official Power BI MCP / connection; `pbi-cli` no longer preferred). F016 is verified ABSENT
from `src/` (the roadmap: "NOT BUILT -- the only remaining feature, gated by design"). The
receipt's honesty depends on STATING that absence:

- **F016 is EXECUTION AUTOMATION** that would publish an already-approved model to a workspace.
  Roadmap rule #6 / Principle II make it the last, gated, execution-only step.
- **The receipt is a record-and-STOP TOKEN, not an executor.** It records authorization and
  STOPS; it triggers no publish, no deployment, no Fabric action, and runs no pbi-cli / Power BI
  MCP command. It must NEVER imply an executor exists.
- **The receipt is therefore INDEPENDENT of F016, not blocked by it.** "No current readiness
  stage depends on F016" (roadmap). The receipt explicitly STATES "no automated publish today"
  and names F016 as the owner of any future publish; if asked to publish, the agent STOPS.

## Architecture (a docs/templates authoring slice; no code, no rule, no CLI, no DB)

The slice is committed text only; it adds NO `retail check` rule, NO CLI verb, NO Python, opens
NO DB connection (Principle VIII; rule 8 docs/templates-first):

- **One generic template** -- `templates/handoff/publish-receipt.md`: a copy-me blank that, for
  any subject area, records the terminal publish-authorization state -- the table, the pack it
  terminalizes (by relative path), the CITED `publish_ready` `approvals[]` entry + the
  deliberately-empty owner line, the explicit "no executor today (F016 absent)" statement, and a
  status drawn from the readiness four-status set with `evidence[]` + `blocking_reasons[]`. It
  lands beside its two siblings `bi-handoff-pack.md` and `handoff-review-checklist.md` and is
  copied per table to `mappings/<table>/handoff/`.
- **One non-gating doc note** -- `docs/readiness/publish-ready.md` gains a ONE-LINE, NON-GATING
  `evidence[]`-style note pointing at the receipt as the concrete artifact of the record-and-STOP
  action. It adds NO new blocking reason, NO new gate, NO new status, and NO new required artifact;
  the stage's gates (prior stages `pass`; handoff review; recorded approval) are unchanged.

There is NO new `retail check` rule, NO CLI command, NO Python, and NO publish/executor step --
by design. The agent's role is to AUTHOR the generic template + the non-gating note and, per
table, to VERIFY (read-only) that the `approvals[]` slot EXISTS -- never to populate the sign-off,
never to publish.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record a terminal publish-authorization receipt that points at the recorded approval and STOPS (Priority: P1)

A table has reached Publish Ready: stages 1-6 are `pass`, the handoff pack is complete and
reviewed, and a named human (via F027 or an equivalent recorded action) has recorded a
`publish_ready` approval in `readiness-status.yaml` `approvals[]`. The analyst wants a concrete,
reviewable token that captures the terminal state: "this table is recorded as publish-authorized;
the pack it terminalizes is at this path; no executor exists today; STOP." Following the template,
the agent fills every TRUE field -- the table, the pack path, the cited approval entry, the
explicit no-executor statement -- and leaves the sign-off / owner line as a pointer to the
recorded `approvals[]` owner, NEVER populating it itself. The receipt's status reads `pass`
because a recorded approval exists; the committed receipt is reviewed in git like any handoff
artifact.

**Why this priority**: this is the feature. Turning the record-and-STOP prose into a committed,
reviewable terminal token with an agent-un-fillable sign-off is the one Publish Ready step that
had no concrete artifact. Everything else is the guardrail around it.

**Independent Test**: for a fixture table at Publish Ready with a recorded `publish_ready`
approval, fill the receipt; an auditor confirms every true field is populated, the sign-off /
owner line CITES the recorded `approvals[]` owner (and is not authored by the agent), the receipt
states "no automated publish today (F016 absent)", the status is `pass` with `evidence[]` citing
the pack + the approval, and 0 publish/executor actions occurred.

**Acceptance Scenarios**:

1. **Given** a table whose stages 1-6 are `pass`, whose pack is complete and reviewed, and whose
   `readiness-status.yaml` records a `publish_ready` `approvals[]` entry by a named human,
   **When** the agent fills the receipt, **Then** every true field is populated, the sign-off /
   owner line cites the recorded approval owner (agent authors nothing in it), the receipt states
   no executor exists today, and the status is `pass` with `evidence[]` citing the pack + approval.
2. **Given** the filled receipt, **When** it is committed and reviewed in git, **Then** it is a
   plain-text token a reviewer reads like code, it triggers no publish, and it adds no readiness
   gate, status, or rule beyond the existing Publish Ready stage.
3. **Given** the receipt, **When** it is inspected, **Then** it carries NO numeric confidence /
   readiness / health score -- only the four-status verdict + `evidence[]` + `blocking_reasons[]`.

### User Story 2 - Refuse to self-grant: leave the sign-off un-filled and STOP when no approval is recorded (Priority: P1)

A request would have the agent "approve publish", "sign off", or "mark this published" for a
table whose `readiness-status.yaml` records NO `publish_ready` approval. The receipt's
load-bearing constraint -- the sign-off / owner line is the never-self-grant gate (Principle V) --
makes the agent REFUSE to populate it. It records the receipt as `blocked` ("no recorded publish
approval"), names the authority class as a placeholder it does NOT fill, points the owner at F027
(the recorded-approval path), and STOPS. The agent never writes the sign-off, never invents the
owner, and never marks `publish_ready: pass`.

**Why this priority**: the un-fillable sign-off is the whole point (Principle V). A receipt that
let the agent self-grant -- or fabricate an owner -- would defeat the readiness system and the
constitution's load-bearing judgment-call floor. Refusing is as load-bearing as recording.

**Independent Test**: for a fixture table with no recorded `publish_ready` approval (and one whose
prior stages are not all `pass`), an "approve / sign-off / publish" request yields a receipt with
the sign-off line UN-FILLED, status `blocked` with the matching blocking reason, the authority
class left as a placeholder, and 0 self-granted approvals; an auditor confirms the agent authored
nothing in the sign-off slot in every case.

**Acceptance Scenarios**:

1. **Given** a table with no recorded `publish_ready` approval, **When** the agent is asked to
   record the receipt, **Then** the sign-off / owner line is left UN-FILLED (a placeholder
   pointer), the status is `blocked` ("no recorded publish approval"), and the agent points at the
   recorded-approval path (F027) and STOPS.
2. **Given** a request to "just sign it off" or "mark it approved", **When** the agent responds,
   **Then** it REFUSES to populate the sign-off (Principle V), records the refusal as the blocking
   reason, and never writes an owner or a date into the `approvals[]` slot.
3. **Given** a table whose stages 1-6 are not all `pass`, **When** the receipt is attempted,
   **Then** the status is `blocked` with the not-pass prior stage as the blocking reason, never
   `pass`, and no sign-off is authored.

### User Story 3 - Stay strictly inside the record-and-STOP boundary: no executor, no publish (Priority: P1)

A user asks the receipt to "publish to the workspace", "run the Power BI adapter", "deploy to
Fabric", or "trigger the release". The receipt STOPS at the record-and-STOP boundary: it records
authorization state and names F016 (verified absent) as the owner of any publish. The slice runs
no pbi-cli / Power BI MCP command, opens no DB connection, deploys nothing, and the receipt's text
NEVER implies an executor exists.

**Why this priority**: this is the boundary that keeps the receipt from being read as an executor
or as pre-empting the deferred, gated F016 (rule #6, Principle II). Recording authorization is
allowed; publishing it is F016's role, and F016 does not exist yet.

**Independent Test**: across a fixture set of requests including "publish", "run the adapter",
"deploy to Fabric", the receipt produces zero publish/executor output, names F016 in each case,
and an auditor confirms 0 pbi-cli/MCP commands, 0 publish actions, 0 DB connections, and that the
receipt text states "no automated publish today (F016 absent)" rather than implying an executor.

**Acceptance Scenarios**:

1. **Given** a request to "publish to the workspace", **When** the agent responds, **Then** it
   STOPS, records authorization state only, and names F016 as the owner of any publish -- it
   performs no publish and runs no command.
2. **Given** a request to "deploy to Fabric" or "run the Power BI execution adapter", **When** the
   agent responds, **Then** it STOPS and names F016 (verified absent), performing no deployment and
   opening no connection.
3. **Given** the slice's committed artifacts, **When** they are inspected, **Then** they contain 0
   pbi-cli/MCP commands, 0 publish/deploy steps, 0 DB connections, 0 new `retail check` rules, and
   the receipt text explicitly states no executor exists today.

### Edge Cases

- **The recorded approval is later retracted upstream.** If the `publish_ready` `approvals[]`
  entry is removed or the prior-stage gate regresses, the receipt's status MUST follow the
  readiness status (back to `blocked`); the receipt does not silently keep a stale `pass`. The
  receipt reflects the recorded state, it does not freeze it.
- **A consumer asks to add an authority the receipt does not name.** Naming the required authority
  class (data-owner / governance / both) is a Principle V judgment call left to the owner; the
  agent records it as a placeholder and STOPS, never picking the person.
- **Windows path / encoding limits.** The receipt copied to `mappings/<table>/handoff/` plus short
  table names must stay under the 260-char path limit; committed text is ASCII, UTF-8 without BOM
  (CLAUDE.md hard rules; Principle IX).
- **The receipt is mistaken for a publish trigger.** The receipt MUST read as a terminal RECORD,
  not a command. Its title, status, and no-executor statement make explicit that it triggers
  nothing -- it is reviewed in git, not "run".
- **No worked instance exists yet for a generic-template review.** The generic template carries
  placeholders only; the first filled instance would be `retail_store_sales` (C086) under
  `mappings/retail_store_sales/handoff/`. No C086/pharmacy specifics (table name, segments, PII
  columns, named approver) may appear in the generic template (Principle VII).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The slice MUST add a GENERIC, copy-me template
  `templates/handoff/publish-receipt.md` that records the terminal publish-authorization state of
  a table -- the table identity, the BI handoff pack it terminalizes (by relative path), the CITED
  `publish_ready` `approvals[]` entry, the deliberately-empty sign-off / owner line, an explicit
  "no automated publish today (F016 absent)" statement, and a status -- and STOPS.
- **FR-002**: The receipt's sign-off / owner line MUST be deliberately UN-FILLABLE by the agent:
  the agent verifies the `publish_ready` `approvals[]` slot EXISTS and is recorded by a named
  human, and CITES it; it MUST NOT populate the owner, the date, or the approval itself. That
  empty-until-a-named-human-acts field IS the never-self-grant gate (Principle V).
- **FR-003**: The receipt MUST compose with the recorded approval written by F027 (approval-console)
  or an equivalent named-human action -- it READS / CITES the `approvals[]` entry; it MUST NOT
  re-record it, duplicate F027, or run F027.
- **FR-004**: The receipt's status MUST be drawn from the readiness four-status set
  (`not_started` / `blocked` / `warning` / `pass`) with `evidence[]` + `blocking_reasons[]`. It is
  `pass` ONLY when a `publish_ready` approval is already recorded by a named human; absent that, it
  is `blocked` ("no recorded publish approval"). It MUST NOT introduce a fifth status.
- **FR-005**: The receipt MUST carry NO fabricated confidence / readiness / health NUMBER anywhere
  -- statuses + evidence + blockers only (rule #9).
- **FR-006**: The slice MUST add a ONE-LINE, NON-GATING note to `docs/readiness/publish-ready.md`
  pointing at the receipt as the concrete artifact of the record-and-STOP action. It MUST NOT add a
  new gate, a new blocking reason, a new status, or a new required artifact; the stage's existing
  gates (prior stages `pass`; handoff review; recorded approval) stay unchanged.
- **FR-007**: The slice MUST NOT publish, deploy, trigger a release, run any pbi-cli / Power BI MCP
  command, open any DB connection, or deploy to Fabric, and the receipt text MUST NOT imply an
  executor exists. Any such request is STOPPED and F016 (verified absent) is named as the owner
  (rule #6, Principle II).
- **FR-008**: The slice MUST add NO new `retail check` rule, NO CLI verb, and NO Python code; it is
  a docs/templates authoring slice (Principle VIII; rule 8). `retail check` MUST exit 0 with its
  rule count UNCHANGED.
- **FR-009**: The generic template + the doc note MUST be GENERIC to retail BI (Principle VII): no
  C086/pharmacy or other subject-area specifics (table name, segments, PII columns, named approver)
  in any committed generic file. The first filled instance lives only in
  `mappings/<table>/handoff/` and the worked example is cited by reference, never inlined.
- **FR-010**: The spec and the receipt MUST cite Principle V (Agent Stops at Judgment Calls) as the
  owning principle of the never-self-grant seam -- NOT Principle IV. (The idea text mislabels it
  "Principle-IV"; that is corrected here.)
- **FR-011**: The slice MUST stop at Principle V judgment calls -- the required authority class for
  the sign-off, whether to promote this onto the roadmap / assign an F-number, and the
  receipt-vs-pack boundary ruling -- surfacing them to the human owner (recorded in Clarifications
  -> Open for human) rather than self-answering or self-granting.
- **FR-012**: The receipt's status MUST reflect the recorded readiness state and MUST NOT freeze a
  stale `pass`: if the recorded approval is retracted or a prior-stage gate regresses, the receipt
  follows the readiness status back to `blocked`.
- **FR-013**: All committed files MUST be ASCII, UTF-8 without BOM (use `--` and `->`, no glyphs),
  with short repo-relative paths (`<= 200` chars) honoring the Windows 260-char limit, and MUST NOT
  bake in any real connection host or secret (Principle IX).

### Key Entities

- **Publish receipt (the central artifact)**: `templates/handoff/publish-receipt.md` (generic
  blank) and its per-table filled instance under `mappings/<table>/handoff/` -- a terminal token
  recording the table, the pack it terminalizes (by path), the CITED `publish_ready` `approvals[]`
  entry, the deliberately-empty sign-off / owner line, the explicit no-executor statement, and a
  four-status verdict + `evidence[]` + `blocking_reasons[]`. Recorded and reviewed in git; it
  triggers nothing.
- **Recorded publish approval (cited input, NOT written by the receipt)**: the `publish_ready`
  entry in `mappings/<table>/readiness-status.yaml` `approvals[]` (`{stage, owner, at}`), recorded
  by a named human via F027 or an equivalent action. The receipt cites it; it never writes it.
- **BI handoff pack (terminalized input)**: `templates/handoff/bi-handoff-pack.md` (and its filled
  per-table copy) -- the bundle whose "Publish approval" section the receipt's terminal token
  points at. The receipt does not duplicate the pack's section (boundary ruling open).
- **Publish Ready doc note (output)**: the one-line, non-gating `evidence[]`-style note in
  `docs/readiness/publish-ready.md` pointing at the receipt -- no new gate, status, or rule.
- **F027 approval-console (composes-with, NOT invoked)**: the shipped machinery that WRITES
  `approvals[]` from a named human's answer. The receipt reads the slot F027 writes; it never runs
  or duplicates F027.
- **F016 Power BI execution adapter (the deferred boundary, verified ABSENT, NOT an input)**: the
  execution-only adapter that WOULD publish. Named as the owner of any publish; never invoked; its
  absence is stated honestly by the receipt.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A generic `templates/handoff/publish-receipt.md` exists, lands beside its two
  siblings (`bi-handoff-pack.md`, `handoff-review-checklist.md`), records the terminal
  publish-authorization state, and STOPS; a reviewer scanning it finds placeholders only and 0
  subject-area specifics.
- **SC-002**: In 100% of filled instances, the sign-off / owner line is CITED from the recorded
  `approvals[]` entry, never authored by the agent; across all runs the agent self-grants the
  publish sign-off in 0 cases (Principle V holds 100% of the time).
- **SC-003**: For a fixture table with a recorded `publish_ready` approval the receipt reads `pass`
  with `evidence[]` citing the pack + approval; for a fixture with NO recorded approval (or a
  not-pass prior stage) it reads `blocked` with the matching blocking reason -- in 100% of gated
  cases the status follows the recorded readiness state.
- **SC-004**: Across all runs the slice emits 0 publish/deploy actions, 0 pbi-cli / Power BI MCP
  commands, 0 DB connections, and 0 Fabric deployments; the receipt text states "no automated
  publish today (F016 absent)" and implies an executor in 0 places (rule #6 holds 100%).
- **SC-005**: The slice adds 0 new readiness stages, 0 new readiness statuses, 0 new blocking
  reasons to the stage, 0 new required artifacts, and 0 new `retail check` rules; the doc note is
  non-gating; `retail check` exits 0 with its rule count UNCHANGED.
- **SC-006**: 0 fabricated confidence / readiness / health numbers appear in the template or any
  filled instance -- statuses + evidence + blockers only (rule #9).
- **SC-007**: 0 C086/pharmacy or other subject-area specifics appear in any committed GENERIC
  artifact (the template, the doc note); the worked example is cited by reference only
  (Principle VII).
- **SC-008**: The spec and the receipt cite Principle V (not Principle IV) as the owning principle
  in 100% of references to the never-self-grant seam; 0 references mislabel it "Principle IV".
- **SC-009**: All committed files are ASCII + UTF-8 no BOM with repo-relative paths `<= 200` chars
  under the Windows 260-char limit; 0 real hosts/secrets appear in any committed file.

## Assumptions

- **Publish Ready (stage 7) and its gates are unchanged.** The stage's gates (prior stages 1-6
  each `pass`; the handoff review; the recorded data-owner / governance approval) and its owner
  stay exactly as `docs/readiness/publish-ready.md` defines them. This feature adds a non-gating
  EVIDENCE-style note + a terminal token, NOT a gate (no divergent source of truth -- constitution
  Governance amendment clause).
- **F027 (approval-console) is the shipped recorded-approval path and is SHIPPED.** The receipt
  composes with it: F027 (or an equivalent named-human action) WRITES the `publish_ready`
  `approvals[]` entry; the receipt READS / CITES it and never re-records it.
- **F016 (the Power BI execution adapter) is the deferred publish/execution engine and is verified
  ABSENT from `src/`** (roadmap: "NOT BUILT -- the only remaining feature, gated by design"). A
  record-and-STOP receipt is NOT F016 and does not wait on it (rule #6 gates the automation, not
  the record). The receipt states the absence honestly.
- **This idea has NO roadmap F-number.** It is from the exploratory idea-bank
  (`docs/roadmap/idea-backlog.md`), which is "not a roadmap and not a commitment". It maps to the
  Publish Ready readiness stage; whether to promote it and assign an F-number is a human decision
  (recorded in Clarifications -> Open for human). This spec assigns none.
- **The never-self-grant seam is owned by Principle V, not Principle IV.** The idea text mislabels
  it; the spec corrects it. Principle IV is Source Mapping Before Silver; Principle V is Agent Stops
  at Judgment Calls (the readiness-system clause cites Principle V for "a stage's approval is a
  named human action the agent cannot self-grant").
- **The receipt-vs-pack boundary is a recorded OPEN item, not pre-decided.** The existing
  `bi-handoff-pack.md` "Publish approval" section uses the identical `approvals[]` / `publish_ready`
  shape; whether the receipt is a distinct terminal token or a duplicate is a human ruling. This
  spec states the candidate distinct-token shape and defers the ruling (Clarifications -> Open for
  human).
- **The first worked instance is `retail_store_sales` (C086).** C086 is the prior worked example,
  not the schema (rule #7, Principle VII); the generic template carries placeholders only and cites
  the worked example by reference.
- **Reuse over new surface (Principle II, YAGNI):** docs/templates only -- no new `retail check`
  rule, no CLI verb, no Python, no DB connection, no executor. The value is the committed terminal
  token + the non-gating note.
- **This is a planning + authoring slice consistent with the readiness roadmap** (Publish Ready,
  stage 7). It changes no existing gate, moves no existing doc's authority, and writes no runtime
  code.
