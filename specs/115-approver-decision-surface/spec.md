# Feature Specification: Approver Decision Surface -- refutation-first reading view for the human signer

**Feature Branch**: `115-approver-decision-surface`

**Created**: 2026-07-09

**Status**: Draft

**Input**: User description: "Approver Decision Surface -- a read-only, refutation-first reading view for the human signer at a readiness approval moment. It re-sequences ALREADY-COMMITTED readiness evidence into a 'what would make me refuse to sign, first / reassurance last' order, spanning readiness-status.yaml (blocking_reasons[], approvals[], current_stage) AND unresolved-questions.md (open rows). Writes nothing, grants no approval, moves no stage -- a companion to F027 approval-console which owns the write-back."

## Clarifications

### Session 2026-07-09

- Q: Which stage statuses contribute items to the signer's REFUSAL case? -> A:
  `blocked` AND `warning` stages (their `blocking_reasons[]`/notes) PLUS any
  stage that requires approval but has no valid `approvals[]` entry, PLUS OPEN
  `unresolved-questions.md` rows. `pass` stages, recorded valid approvals, and
  `answered` questions are REASSURANCE (shown last). This is wider than
  `blocker_explainer` (which surfaces only `blocked`): a `warning` is genuinely
  something a signer should weigh before signing.
- Q: How is an OPEN `unresolved-questions.md` row assigned to a refutation
  category (its position in the order)? -> A: by the row's committed
  `Who must answer` column: `governance` and `data-owner` -> the `approval`
  bucket (rank 1, top); `analyst` -> the `grain`/`readiness` bucket (by the same
  keyword classifier used for blocking reasons); an unrecognized owner ->
  `readiness` (default, last). Mapping by the STRUCTURED owner column (not by
  scanning free-text question prose) keeps every ordering input a committed fact,
  so no category is synthesized (hard rule #9 stays clean by construction).

## Why this feature exists

At a readiness approval moment, a named human is asked to sign off on a stage
(mapping_ready, semantic_model_ready, dashboard_ready, publish_ready). The
evidence they need to decide "should I refuse?" is already committed, but it is
scattered and NOT ordered for a signer: `readiness-status.yaml` holds per-stage
`blocking_reasons[]`, an `approvals[]` list, and `current_stage`; the per-table
`unresolved-questions.md` holds an Open-questions table (each row with a
`Who must answer` owner, a `Status`, and a `Resolution`). A signer today must
read these top-to-bottom, in the order the files happen to store them, and
assemble the refusal case themselves.

No shipped surface presents this refutation-first. Verified against `main`
@ 84d05c8: `approval_inbox` sorts by (source_path, stage-index); `blocker_explainer`
sorts by (source_path, stage, reason) lexically; `run_next` is a single-table
next-action dispatcher; `readiness-viewer` renders `approvals[]` chronologically.
None orders items by "what would make me refuse to sign, first", and NONE reads
`unresolved-questions.md` at all.

This feature is the missing reading order: it re-sequences the ALREADY-COMMITTED
readiness evidence for one table into a decision-first view -- the things that
would make a signer REFUSE first (unmet approvals, open governance/PII questions,
recorded blockers), reassurance (passed stages, recorded approvals) last -- so the
signer reads the refusal case before the comfort. It records nothing, grants
nothing, and moves no stage; the write-back remains F027 approval-console's job.

## What this feature is NOT (the scope wall)

The surface's NAME ("approver") is itself the risk flag; this wall is load-bearing.

- **It grants NO approval and moves NO stage.** It is a READING VIEW, not a
  decision. F027 approval-console owns the write-back (`approvals[]`, the
  `unresolved-questions.md` `Resolution` column, stage flips). This surface only
  RE-ORDERS what is already committed. never_self_grant_approval (Principle V)
  holds absolutely.
- **It WRITES NOTHING.** No write path may exist STRUCTURALLY -- grep-verifiable
  zero write calls, matching the three shipped read-only surfaces
  (`approval_inbox`, `blocker_explainer`, `run_next`). "Writes nothing" is a
  structural guarantee, not a docstring promise.
- **The reorder key is a FIXED, COMMITTED enum rank -- never a synthesized
  value.** Ordering reuses the already-shipped `blocker_explainer` category rank
  (approval > grain > live_validation > artifact > readiness). The surface MUST
  NOT compute a priority/urgency/severity/confidence number to sort by -- a
  rolled-up rank the surface itself computes trips hard rule #9 EVEN when
  expressed as list position rather than a printed number. The rank is a fixed
  lookup, not a computation.
- **It adds NO gate.** No new `retail check` rule, no `blocking_reasons[]` entry,
  no stage move; its presence/absence is never a gate requirement.
- **It emits NO score and NO count** (hard rule #9): no "N blockers", no
  readiness percentage, no confidence value. Items are ordered and shown; not
  scored or tallied.
- **It is generic (Principle VII).** Per-table over committed
  `readiness-status.yaml` + `unresolved-questions.md`; no hardcoded table names,
  column names, PII categories, or grain keys.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Signer reads the refusal case first (Priority: P1)

A named human about to approve a stage opens the surface for one table and sees,
at the TOP, the items that would make them refuse to sign -- an unmet/invalid
approval for the stage, then open grain/PK questions, then live-validation gaps,
then missing artifacts -- each shown with its committed reason and where it lives.
Reassurance (passed stages, recorded approvals) is LAST. They can assess the
refusal case without hand-assembling it from raw files.

**Why this priority**: This is the feature -- the refutation-first ORDERING of
committed evidence for the signing moment. Without it there is no MVP.

**Independent Test**: Run the surface for a table whose `readiness-status.yaml`
has a recorded `blocking_reasons[]` entry and a missing approval; confirm the
approval-category and blocker items sort ABOVE the passed-stage reassurance, in
the fixed enum-rank order, and that no synthesized priority number appears.

**Acceptance Scenarios**:

1. **Given** a table with items in more than one refutation category (e.g. a
   missing approval AND a recorded blocker), **When** the surface is composed,
   **Then** items appear in the fixed enum-rank order (approval > grain >
   live_validation > artifact > readiness), refusal-bearing items before
   reassurance, and the ordering is stable/deterministic.
2. **Given** the same table, **When** the surface is composed, **Then** each item
   shows its committed reason verbatim and its source location, and NO item
   carries a computed priority/urgency/confidence value.
3. **Given** a table at full `pass` with recorded approvals and no open items,
   **When** the surface is composed, **Then** it shows the reassurance items only
   and states plainly there is nothing in the refusal case, emitting no score.

---

### User Story 2 - Open governance/PII questions surface in the refusal case (Priority: P1)

The signer must see OPEN rows from `unresolved-questions.md` -- the questions a
named human still owes an answer to (Who-must-answer = governance / analyst /
data-owner) -- as part of the refusal case, because an unanswered build-blocking
question is exactly a reason to refuse. This is the net-new input no shipped
surface reads.

**Why this priority**: Equal-P1. Ingesting `unresolved-questions.md` open rows is
half of what makes this surface distinct from the shipped blocker surfaces; a
refusal case that omits open questions is incomplete.

**Independent Test**: Run the surface for a table whose `unresolved-questions.md`
has at least one OPEN (not `answered`) row; confirm that row appears in the
refusal case with its owner and question text, and that ANSWERED rows do not clog
the refusal case.

**Acceptance Scenarios**:

1. **Given** a table whose `unresolved-questions.md` has an OPEN question row,
   **When** the surface is composed, **Then** that row appears among the
   refutation items with its `Who must answer` owner and question text, ordered
   by the same fixed enum rank (an open question maps to its category, e.g. a PII
   question to the approval/governance bucket).
2. **Given** a table whose `unresolved-questions.md` rows are all `answered`
   (Gate status CLEARED), **When** the surface is composed, **Then** no answered
   row is presented as an open refusal item; answered rows may appear only as
   reassurance, never as an open blocker.

---

### User Story 3 - Missing or unreadable input is surfaced, not fabricated (Priority: P2)

A signer running the surface for a table missing one of the two inputs
(`readiness-status.yaml` or `unresolved-questions.md`) gets an honest signal
naming what is missing, never an empty view that reads as "nothing to refuse".

**Why this priority**: Robustness at the input boundary; secondary to the core
ordering.

**Independent Test**: Point the surface at a table with a `readiness-status.yaml`
but no `unresolved-questions.md` (or vice-versa); confirm it composes from the
present input and explicitly notes the missing one, never fabricating items.

**Acceptance Scenarios**:

1. **Given** a table missing `readiness-status.yaml`, **When** the surface is
   composed, **Then** it names the missing path and does not fabricate a refusal
   case.
2. **Given** a table with `readiness-status.yaml` present but
   `unresolved-questions.md` absent, **When** the surface is composed, **Then** it
   composes the refusal case from the status file and explicitly notes the open
   questions were not available (not "no open questions").

---

### Edge Cases

- An item whose reason matches NO refutation category -> it lands in the default
  `readiness` bucket (last in the refusal case), exactly as `blocker_explainer`
  already classifies; the surface introduces no new category vocabulary.
- Two items in the same category -> a stable secondary order (the shipped
  lexical tie-break) keeps output deterministic; no computed priority breaks the
  tie.
- An `unresolved-questions.md` open row whose `Who must answer` owner is
  unrecognized -> shown in the refusal case under the default bucket with the
  owner echoed verbatim; the surface does not invent an owner class.
- A table at `current_stage` with a recorded valid approval for that stage ->
  that approval is reassurance, not a refusal item (mirrors how
  `blocker_explainer` treats a satisfied approval).
- A stage with status `warning` -> its reasons/notes go in the refusal case
  (Clarification Q1), distinct from `blocker_explainer` which surfaces only
  `blocked`; a `warning` is a weigh-before-signing item, not reassurance.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The surface MUST present, for ONE table, the committed readiness
  evidence ordered refutation-first: refusal-bearing items before reassurance.
  The refusal case comprises (Clarification Q1): stages with status `blocked` OR
  `warning` (their `blocking_reasons[]`/notes), any approval-requiring stage with
  no valid `approvals[]` entry, and OPEN `unresolved-questions.md` rows.
  Reassurance comprises `pass` stages, recorded valid approvals, and `answered`
  questions.
- **FR-002**: The ordering key MUST be the ALREADY-SHIPPED fixed category enum
  rank (approval > grain > live_validation > artifact > readiness) reused from
  `blocker_explainer`; the surface MUST NOT compute a priority/urgency/severity/
  confidence value to order by. The rank is a fixed committed lookup, not a
  computation (hard rule #9).
- **FR-003**: The surface MUST ingest OPEN rows from the table's
  `unresolved-questions.md` (rows whose `Status` is not `answered`) as refutation
  items, each carrying its `Who must answer` owner and question text verbatim,
  and MUST assign each row's refutation category by that committed `Who must
  answer` column (Clarification Q2): `governance`/`data-owner` -> `approval`
  bucket; `analyst` -> `grain`/`readiness` by the shipped keyword classifier;
  unrecognized owner -> `readiness` default. It MUST NOT synthesize a category by
  scoring the free-text question prose.
- **FR-004**: An `answered` `unresolved-questions.md` row MUST NOT appear as an
  open refusal item; answered questions may appear only as reassurance.
- **FR-005**: Every item MUST show its committed reason/text verbatim and cite its
  source location (which file, which stage/row); the surface MUST NOT paraphrase
  or generate reasons.
- **FR-006**: The surface MUST write NOTHING and MUST grant/self-grant no
  approval and move no readiness stage; it MUST contain no file-write path
  (structurally verifiable: zero write calls, matching the shipped read-only
  surfaces).
- **FR-007**: The surface MUST NOT add a `retail check` rule or any gate, and its
  presence/absence MUST NOT be a gate requirement.
- **FR-008**: The surface MUST emit no numeric score, count, or percentage
  anywhere (hard rule #9).
- **FR-009**: The surface MUST read only committed on-disk artifacts
  (`readiness-status.yaml`, `unresolved-questions.md`) and MUST open no DB, Power
  BI, or network connection.
- **FR-010**: When one of the two inputs is missing or unreadable, the surface
  MUST compose from the present input and explicitly name the missing one, and
  MUST NOT fabricate items or present a missing input as "nothing to refuse".
- **FR-011**: The surface MUST be generic across tables (Principle VII): no
  hardcoded table names, column names, PII categories, or grain keys; it operates
  over whatever the target table's two committed artifacts contain.
- **FR-012**: The refutation ordering MUST be deterministic and stable
  (re-running on unchanged inputs yields identical order), reusing the shipped
  lexical secondary tie-break so no computed value is needed to break ties.
- **FR-013**: Output MUST be ASCII-only, UTF-8 without BOM, using `--` and `->`
  (no glyphs), with short repo-relative paths (Windows 260-char budget).

### Key Entities *(include if feature involves data)*

- **Refutation item**: one committed evidence element the signer weighs -- an
  unmet approval, an open question, a recorded blocker, or a missing artifact.
  Attributes: table, source location, category (from the shipped enum), reason/
  text (verbatim), and (for questions) the `Who must answer` owner.
- **Reassurance item**: a committed positive signal -- a passed stage, a recorded
  valid approval, an answered question. Shown last, never scored.
- **Approver Decision view**: the composed, refutation-first ordered output for
  one table. Read-only; the output vehicle (printed view vs a written companion
  file) is a plan-phase decision (see Assumptions).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a table with a missing approval AND a recorded blocker AND an
  open question, a signer sees all three in the refusal case, ordered by the fixed
  enum rank, above any reassurance -- without opening `readiness-status.yaml` or
  `unresolved-questions.md` directly.
- **SC-002**: The output contains zero synthesized priority/urgency/confidence
  values and zero numeric scores/counts/percentages (verifiable by inspection:
  ordering is by the fixed enum rank only).
- **SC-003**: The composed surface writes nothing -- after a run, `git status`
  shows no new or modified tracked file attributable to the surface, and the
  implementation contains no file-write call (grep-verifiable), matching the three
  shipped read-only surfaces.
- **SC-004**: Every refutation and reassurance item reproduces its committed
  reason/question text verbatim and cites its source location.
- **SC-005**: Open `unresolved-questions.md` rows appear in the refusal case and
  answered rows never appear as open refusal items, demonstrated on a table with
  both.
- **SC-006**: The surface produces a correct refutation-first view for any
  conformant table with no code change (generic), demonstrated on at least two
  distinct tables.

## Assumptions

- The refutation categories and their rank are NOT re-invented here: they are the
  committed `blocker_explainer._CATEGORY_RULES` enum (approval > grain >
  live_validation > artifact > readiness). This spec reuses that rank as the
  refutation-first order; it does not author a new priority scheme.
- The OUTPUT VEHICLE and, critically, the STANDALONE-MODULE vs
  SORT-MODE-ON-`blocker_explainer` decision are DEFERRED to the plan phase. The
  verified net-new collapses to (a) sorting `blocker_explainer`'s existing items
  by its existing enum rank instead of lexically, and (b) ingesting
  `unresolved-questions.md` open rows. The plan MUST decide explicitly whether to
  add this as a new signer-facing MODE ON `blocker_explainer` (reusing its
  classifier + read-only proof) or a separate module, and SHOULD prefer folding
  it in rather than re-reading and re-categorizing the same `readiness-status.yaml`
  in a parallel module. The spec fixes the behavior, not the vehicle.
- The surface is a companion to F027 approval-console (the write-back); it is
  never a prerequisite for any readiness stage, following the read-only
  optional-companion posture.
- "Refusal case" and "reassurance" are presentation groupings over committed
  data, not new stored fields; the surface adds no field to any artifact.
- An open `unresolved-questions.md` row maps to a refutation category by its
  committed `Who must answer` column (Clarification Q2), NOT by scoring the
  free-text question prose: `governance`/`data-owner` -> approval bucket,
  `analyst` -> grain/readiness by the shipped keyword classifier, unrecognized ->
  readiness default. Mapping by a structured committed field (not prose) keeps
  every ordering input a committed fact, so no category is synthesized.
