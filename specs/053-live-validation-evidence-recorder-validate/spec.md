# Feature Specification: Live-validation evidence recorder (validate.py Findings -> readiness-status block)

**Feature Branch**: `053-live-validation-evidence-recorder-validate`

**Created**: 2026-07-01

**Status**: Draft

**Input**: User description: "Live-validation evidence recorder (validate.py Findings -> readiness-status block)"

## Overview

Today `retail validate` runs the four live read-only checks (V-RC2 / V-RC15 /
V-RC16) against a real Postgres database and returns a list of Finding objects.
The CLI handler `_run_validate` ONLY prints those findings to stdout/stderr and
sets an exit code (1 iff any ERROR). Nothing captures the run as durable
evidence. The readiness spine (`docs/readiness/gold-ready.md` +
`templates/readiness-status.yaml`) already asserts that a `gold_ready` stage
records `status` + `evidence[]` + `blocking_reasons[]`, and literally cites
"retail validate exit 0" as the evidence a clean run should leave -- but no code
produces that block. This feature closes exactly that gap: it turns a validate
run's Findings into a proposed `gold_ready` readiness-status block (evidence and
blocking reasons), so a live run leaves a machine-readable, human-reviewable
trace instead of only console output.

Consistent with the repo's YAGNI discipline ("add the seam, not the
implementation") and hard rule #8 (docs/templates first, automate after the
artifact proves useful), this is the automation seam on top of an artifact that
already exists. It does NOT provision databases, does NOT invent a readiness
score, and does NOT self-grant a stage pass.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Capture a clean live run as gold_ready evidence (Priority: P1)

An analyst runs the live validator against a table whose gold star is built,
with a real database reachable. All four live checks return zero ERROR findings.
Instead of only seeing "all live checks passed" on the console, the analyst
obtains a structured `gold_ready` readiness-status block that records the clean
run as evidence, in the same shape the readiness template already defines
(status + evidence[] + blocking_reasons[]).

**Why this priority**: This is the core value -- a live run today is
ephemeral console output; the readiness spine needs it as durable, structured
evidence. Without it, `gold_ready` status is filled by hand from memory of a
console scroll.

**Independent Test**: Feed a synthetic empty findings list (a clean run) to the
recorder and assert it emits a `gold_ready` block with a non-empty `evidence[]`
citing the validate run and an empty `blocking_reasons[]`, using only stdlib
(no DB, no driver, no network).

**Acceptance Scenarios**:

1. **Given** a live validate run that returned zero findings for a named table,
   **When** the recorder consumes that result, **Then** it produces a
   `gold_ready` block whose `evidence[]` records that a live validate run
   completed with zero ERROR findings for that table, and whose
   `blocking_reasons[]` is empty.
2. **Given** the same clean run, **When** the recorder produces the block,
   **Then** the block never contains a numeric confidence/score field.

### User Story 2 - Capture live findings as blocking reasons (Priority: P1)

An analyst runs the live validator and one or more checks return ERROR findings
(e.g. a V-RC15 date gap or a V-RC16 orphan FK / reconciliation mismatch). The
recorder converts each ERROR finding into a `blocking_reasons[]` entry on the
`gold_ready` block, preserving the finding's rule id, message, and locator so
the blocker is actionable and traceable back to the check that raised it.

**Why this priority**: The readiness spine's whole purpose is to name the single
next allowed action; a blocked gold_ready stage with the specific V-RC* blockers
recorded is what tells the analyst what to fix. Equal-priority with Story 1
because a recorder that only records the happy path is half a recorder.

**Independent Test**: Feed a synthetic findings list containing ERROR findings
to the recorder and assert each ERROR becomes a `blocking_reasons[]` entry
carrying its rule id + message + locator, and the block status reflects "not a
clean pass".

**Acceptance Scenarios**:

1. **Given** a live validate run that returned one or more ERROR findings,
   **When** the recorder consumes that result, **Then** each ERROR finding
   appears as a distinct `blocking_reasons[]` entry preserving its rule id,
   message, and locator.
2. **Given** a finding whose message embeds a DSN or credential fragment,
   **When** the recorder records it, **Then** the recorded text carries no DSN,
   password, username, or host secret (the CLI's existing redaction is
   preserved end-to-end).

### User Story 3 - Record the deferred boundary honestly (Priority: P2)

An analyst invokes validate with no database reachable (no DSN, or the optional
DB driver is not installed). Today this only prints to stderr and returns 1. The
recorder should represent this "blocked-deferred" state explicitly rather than
silently, so the readiness trace distinguishes "we ran and found a defect" from
"we could not run a live check at all" -- never inferring a pass from a
non-run.

**Why this priority**: Principle VIII forbids faking a pass in deferred mode;
recording the deferred boundary as an explicit blocked state (rather than
nothing) makes the honest-boundary behavior legible in the artifact. Lower
priority than P1 because the print-only behavior is already safe today; this
makes it durable.

**Independent Test**: Invoke the recorder path for the deferred case (no
findings because no run occurred) and assert it produces a `blocked` gold_ready
block whose `blocking_reasons[]` names the deferred boundary, with no evidence
that would read as a clean pass.

**Acceptance Scenarios**:

1. **Given** a validate invocation in deferred mode (no DSN or no DB driver),
   **When** the recorder runs, **Then** the produced block has status `blocked`
   with a `blocking_reasons[]` entry naming the deferred boundary and no
   `evidence[]` implying a completed clean run.

### Edge Cases

- What happens when the findings list mixes ERROR and WARNING severities? WARNING
  findings must be represented as recorded warnings (advanced-with-a-recorded-issue),
  never dropped and never treated as blockers; only ERROR findings block.
- How does the system handle a finding message that already contains a redaction
  placeholder? It must pass through unchanged (idempotent redaction, no
  double-scrubbing artifacts).
- What happens if the target table identifier is missing from the run context?
  The recorder must fail fast with a clear error rather than emit a block with a
  blank/placeholder table identity.
- What happens when the block would be written to a generic template rather than
  a table-specific filled copy? The recorder must refuse to write findings
  (which embed specific table/column identifiers) into the generic
  `templates/readiness-status.yaml`; findings-bearing blocks belong only in a
  table-specific filled copy.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The recorder MUST consume the output of a live validate run (a
  list of Finding results plus the target table identity) and produce a
  `gold_ready` readiness-status block matching the shape defined by
  `templates/readiness-status.yaml` (a stage `status`, an `evidence[]` list, and
  a `blocking_reasons[]` list).
- **FR-002**: When the run returned zero ERROR findings, the recorder MUST record
  in `evidence[]` that a live validate run completed with zero ERROR findings for
  the named table (the "evidence recorded" condition `gold-ready.md` requires),
  and MUST leave `blocking_reasons[]` empty.
- **FR-003**: When the run returned one or more ERROR findings, the recorder MUST
  emit one `blocking_reasons[]` entry per ERROR finding, preserving that
  finding's rule id, message, and locator.
- **FR-004**: The recorder MUST represent WARNING-severity findings as recorded
  warnings, distinct from blockers; a WARNING MUST never be recorded as a
  blocking reason and MUST never be silently dropped.
- **FR-005**: The recorder MUST NOT emit any numeric confidence or readiness
  score field; it emits only the explicit statuses, evidence, warnings, and
  blocking reasons (hard rule #9 / Principle IX -- no fake confidence).
- **FR-006**: The recorder MUST preserve the existing DSN/credential redaction so
  that no recorded evidence or blocking-reason text contains a DSN, password,
  username, or host secret.
- **FR-007**: The recorder MUST build a NEW block structure and MUST NOT mutate
  its Finding inputs (the Finding dataclass is frozen; immutability rule).
- **FR-008**: The recorder MUST remain stdlib-only in the import path it shares
  with `retail check` / `retail validate`; it MUST NOT introduce a module-scope
  import of a YAML library, a database driver, or any heavy dependency into
  `validate.py` or the live-surface modules (the B3 import-boundary guard and the
  driver-free / never-execute invariant must continue to pass).
- **FR-009**: The recorder MUST stay generic: it MUST NOT hardcode any worked-example
  (C086 / pharmacy) table, column, or measure name. The specific table's
  identifiers appear in a recorded block only because they arrive from the run's
  Findings and target identity, and only in a table-specific filled copy.
- **FR-010**: The recorder MUST NOT write a findings-bearing block into the
  generic `templates/readiness-status.yaml`; the generic template stays a
  placeholder schema.
- **FR-011**: When invoked in deferred mode (no DSN or no DB driver -- no live
  run occurred), the recorder MUST represent the state as `blocked` with a
  `blocking_reasons[]` entry naming the deferred boundary, and MUST NOT emit
  evidence that reads as a completed clean run.
- **FR-012**: The recorder MUST NOT set a `gold_ready` status to `pass` on its
  own where the readiness model treats a `pass` as an authoritative claim; the
  disposition of who/what may set `pass` is governed by [NEEDS CLARIFICATION:
  pass-set authority -- may the recorder set gold_ready.status to pass on a
  zero-ERROR run given gold-ready.md calls the stage "mechanical -- no human
  approval", or must it only populate evidence[]/blocking_reasons[] and leave
  status-setting to a human/approval action? (Principle V self-grant boundary)].
- **FR-013**: The delivery mode of the produced block -- whether the recorder
  WRITES `mappings/<table>/readiness-status.yaml` directly or only EMITS a
  proposed block (structured output) for a human/skill to apply -- is [NEEDS
  CLARIFICATION: write-vs-emit -- direct write to the filled copy risks a
  Principle V self-grant; emit-only keeps the human in the loop. Which is the
  first-step scope?].
- **FR-014**: Whether an empty V-RC2 result may be recorded as evidence that the
  declared grain/uniqueness holds (versus only "no duplicate observed on current
  rows") is [NEEDS CLARIFICATION: grain-claim semantics -- a grain/uniqueness
  claim is a Principle V human-ratified judgment; does an empty V-RC2 count as
  grain evidence or only as an observation? Who ratifies the grain claim?].

### Key Entities *(include if feature involves data)*

- **Live validate run result**: the input -- the list of Finding results
  returned by the four live checks plus the target table identity (and the
  run mode: live vs deferred). The Finding is a frozen record carrying rule id,
  severity, message, and locator.
- **Readiness-status block (gold_ready)**: the output -- a structure with a
  stage `status` (one of not_started / blocked / warning / pass), an `evidence[]`
  list, a `blocking_reasons[]` list, and optional recorded `warnings[]`. Never
  carries a numeric score.
- **Target table identity**: the table/source the run was executed against;
  drives which table-specific filled copy a block belongs to and appears in
  recorded evidence/blockers by design (never hardcoded, never leaked into the
  generic template).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A clean live run (zero ERROR findings) yields a `gold_ready` block
  with at least one `evidence[]` entry recording the run and zero
  `blocking_reasons[]` -- reproducible from a synthetic empty findings list with
  no database access.
- **SC-002**: A run with N ERROR findings yields exactly N `blocking_reasons[]`
  entries, each traceable to its originating finding by rule id and locator.
- **SC-003**: No produced block, under any input (clean, findings, deferred),
  contains a numeric confidence/score field or an unredacted DSN/credential
  fragment -- verifiable by scanning the block output.
- **SC-004**: The static check surface (`retail check`) and the import-boundary
  guard continue to pass with the recorder present -- i.e. no new heavy import
  leaks into the stdlib-only path (measured by the existing boundary-guard test
  staying green).
- **SC-005**: The recorder produces identical output for the same inputs on
  repeated runs (deterministic, no wall-clock or environment-derived nondeterminism
  in the recorded evidence text beyond an explicitly-supplied timestamp).

## Assumptions

- The four live checks and their Finding return shape (`run_live_checks ->
  list[Finding]`) and the frozen `Finding` dataclass with `to_dict()` (shipped by
  idea-bank B2) are treated as the stable seam this feature consumes; this feature
  does not modify the checks themselves.
- The readiness-status schema (four statuses; pass requires evidence; blocked
  requires blocking_reasons; no fake confidence) is authoritative as defined in
  `templates/readiness-status.yaml` + `docs/readiness/gold-ready.md`; this feature
  conforms to it and does not redefine it.
- The canonical write target for a filled copy is
  `mappings/<table>/readiness-status.yaml` (ADR 0004); the generic
  `templates/readiness-status.yaml` is a schema placeholder only.
- No DEFERRED capability is assumed to exist -- specifically not the F016 Power BI
  Execution Adapter nor the F031-F033 spec-only runtimes; this feature touches
  only the existing validate surface and the readiness artifact.
- The DSN redaction helper already present in the CLI (`_redact_dsn`) defines the
  scrubbing contract this feature must preserve; the feature reuses that contract
  rather than inventing a new one.
- This idea is not on the roadmap feature sequence (F005-F016) nor the idea-bank
  sequence; the readiness stage it advances (gold_ready evidence automation vs a
  cross-cutting observability seam) is treated as gold_ready evidence automation
  for scoping, pending the placement clarification recorded below.

## Clarifications

The following are Principle V / governance judgments the planning agent is
structurally forbidden to self-answer. They are recorded here for a named human
to rule on; the spec is written to remain valid under the recommended defaults
noted in the clarify session, but the authoritative ruling is a human action.

- **Write-vs-emit (FR-013)**: Does the first-step recorder WRITE
  `mappings/<table>/readiness-status.yaml` directly, or only EMIT a proposed
  block for a human/skill to apply? (Open for human.)
- **Pass-set authority (FR-012)**: May the recorder set `gold_ready.status` to
  `pass` on a zero-ERROR run (gold-ready.md calls the stage "mechanical -- no
  human approval"), or must `pass` remain a human/approval action while the
  recorder only writes evidence + blocking reasons? (Open for human.)
- **Grain-claim semantics (FR-014)**: Does an empty V-RC2 result count as
  evidence that the declared grain holds, or only that no duplicate was observed
  on current rows, and who ratifies the grain claim? (Open for human --
  grain/uniqueness is a carved-out Principle V judgment.)
- **Deferred-state recording (Story 3)**: Should the blocked-deferred state be
  recorded as `blocked` with a blocking reason (recommended), or left print-only
  as today? (Advisor-recommended in the clarify session; low reversibility risk.)
- **Readiness placement**: Which readiness stage/seam does this advance --
  gold_ready evidence automation, or a cross-cutting observability seam? (No
  F-number; open for human placement.)
