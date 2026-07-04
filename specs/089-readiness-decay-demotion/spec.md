# Feature Specification: Readiness Decay -- Drift Raises a Stale-Pass Demotion Blocker

**Feature Branch**: `089-readiness-decay-demotion`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "gap #2. Readiness decay: drift raises a stale-pass demotion
blocker. Serves: Source Ready -> all downstream. Lens/justification: Principle V +
source-drift.md:74. When source drift is detected, raise a stale_pass BLOCKER on every
downstream stage built on the old profile, and a static rule that a `pass` whose evidence
file changed after the approval date must show a re-review. The human demotes; the system
only surfaces. source-drift.md:74 forbids AUTO-demote -- this respects that while closing
the no-path-to-reopen hole."

## Overview

The readiness spine has a documented hole. `docs/readiness/source-drift.md:74` states the
rule plainly: "A `blocked`/`warning` drift at Source Ready makes downstream `pass` stages
... SUSPECT and requiring RE-confirmation against the new shape. The detector FLAGS this; it
MUST NOT silently demote or auto-`pass` any downstream stage -- the human/agent re-runs the
stage gate." That sentence describes the correct behavior in prose, but nothing today
ENFORCES it. `RS1` (`src/retail/rules/readiness_status.py`) checks that a filled
`readiness-status.yaml` is internally consistent -- statuses are one of the four words,
`pass` carries evidence, `blocked` carries blockers, approval-required stages carry a
shape-valid approval -- but RS1 never compares an approval's date against the evidence it
approved, and never reads the source-drift signal at all. The result: a table can drift at
Source Ready, nothing downstream ever gets re-confirmed, and `retail check` stays green
throughout, because there is no rule watching for exactly that condition. The prose promise
("the human/agent re-runs the stage gate") has no enforcement path -- staleness is invisible
until someone happens to notice by eye.

This feature closes that hole with a SECOND static rule, reserved id **HR3**, that fails
`retail check` CLOSED (Principle I) whenever either of two committed-evidence conditions
holds for a table's `readiness-status.yaml`:

1. **Drift-triggered staleness**: `stages.source_ready.status` is `warning` or `blocked`
   (the source-drift signal per `docs/readiness/source-drift.md`) while one or more
   downstream stages are recorded `pass`. Every such downstream `pass` is stale.
2. **Approval-lag staleness**: an approval-bearing stage is `pass` with a recorded
   `approvals[]` entry, but a piece of evidence that stage's `pass` cites has a later
   git-commit date than the approval's `at:` date -- the thing the human signed off on has
   changed since they signed it.

HR3 NEVER writes to `readiness-status.yaml`. It never sets a status, never appends a
`blocking_reasons[]` entry into the file, and never demotes a `pass` to `blocked` on disk --
doing any of that would itself be the auto-demote source-drift.md:74 forbids, AND it would
manufacture a fresh RS1 violation (RS1 already rejects a non-`blocked` stage that carries
`blocking_reasons[]`). Instead, HR3 raises its own `retail check` finding -- a `stale_pass`
ERROR reported the same way every other rule reports a finding (rule id + message + file
locator), pointing at the stale stage and the evidence that moved. The human is the only
actor who can clear it: either by acting on the drift (re-confirming or demoting the stage
themselves, which is their edit to the YAML, not the rule's), or by recording a fresh
`stale_review` entry (a new, HR3-owned top-level key in `readiness-status.yaml`, structurally
parallel to `approvals[]`) that reaffirms the stage is still sound despite the newer
evidence. The system surfaces; the human decides; nothing here scores, demotes, or re-passes
anything on its own.

## Boundary against neighbouring shipped work (read first)

This feature is a targeted gap-closer, not a restatement of any of the following shipped
pieces. Each must stay exactly as it is:

- **Source Drift Detector (spec `015-source-drift-detector`, roadmap F014,
  `docs/readiness/source-drift.md`)** defines the nine-class drift TAXONOMY and states, in
  prose, that a Source Ready `warning`/`blocked` makes downstream `pass` stages suspect and
  that the detector "FLAGS this" without auto-demoting (`source-drift.md:74`). That doc is
  DESIGN ONLY -- no runtime, no `retail drift` CLI, no comparator. This feature does NOT
  reopen that spec, does NOT add a drift class, does NOT build a live re-profile runtime,
  and does NOT compute drift itself. It CONSUMES the drift signal exactly as source-drift.md
  already defines it can be observed today: the committed `stages.source_ready.status` field
  in `readiness-status.yaml` (and, when present, a committed `source-drift-report.md`). HR3
  is the missing ENFORCEMENT half of the sentence source-drift.md:74 already wrote; it does
  not touch the detector's design.
- **RS1 -- readiness-status contradiction linter (`src/retail/rules/readiness_status.py`)**
  checks structural self-consistency of one `readiness-status.yaml` at a single point in
  time (status vocabulary, evidence/blocker pairing, approval shape, stage-order
  contradictions). RS1 has no notion of TIME -- it never compares an evidence file's age to
  an approval's date, and never reads a downstream implication of Source Ready's status.
  HR3 is RS1's sibling, not its replacement: HR3 reuses RS1's owner-shape validation
  (`Person Name (authority_class)`, audit C4) for the new `stale_review` entries, but adds
  no field to RS1's file and does not change what RS1 itself checks. Both rules run
  independently; a table can be simultaneously RS1-clean and HR3-flagged.
- **F027 Approval Console (`.claude/skills/approval-console/`, spec `021`)** is the tool a
  named human uses to RECORD a decision -- an approval, a demotion, or (per this feature) a
  `stale_review` reaffirmation -- into the committed artifacts. HR3 raises the finding that
  gives the Approval Console something to act on; HR3 itself writes nothing back. The two
  compose exactly as F027 already composes with every other blocker source.
- **F028 Evidence Pack Generator / F035 Approval Evidence Pack
  (`.claude/skills/evidence-pack-generator/`, `.claude/skills/approval-evidence-pack/`)**
  compose human-facing packets from already-recorded evidence and blockers. Once HR3 exists,
  a `stale_pass` finding is one more recorded blocker those packs may cite -- this feature
  does not edit either pack generator's template or section list.
- **Readiness Viewer / retail-control-room / run-next-readiness** (`.claude/skills/
  readiness-viewer/`, `.claude/skills/retail-control-room/`, `.claude/skills/
  run-next-readiness/`) display or aggregate ALREADY-recorded state; they compute or render,
  they do not create new findings. A `stale_pass` HR3 finding becomes one more fact those
  read-only tools can surface once it exists; this feature does not change any of their
  logic.

This feature adds exactly ONE new static rule (`HR3`) and exactly ONE new optional
`readiness-status.yaml` top-level key (`stale_review`, additive and back-compatible -- a
file without it is unaffected). It adds no new readiness stage, no new file source, no
executor, and no live DB read.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Drift at Source Ready blocks every downstream `pass` from staying silently green (Priority: P1)

A table has `mapping_ready`, `silver_ready`, and `gold_ready` all recorded `pass`. Later, a
re-profile records `source_ready.status: warning` (or `blocked`) in the table's
`readiness-status.yaml`, per the source-drift taxonomy -- the source has changed shape since
the profile those downstream stages were built against. Today `retail check` stays green
and nothing signals that the three downstream passes are now suspect. With HR3, `retail
check` fails with a `stale_pass` finding naming each downstream `pass` stage built on the
now-drifted source, so the drift cannot be silently ignored.

**Why this priority**: This is the exact hole named in the gap description ("raise a
stale_pass BLOCKER on every downstream stage built on the old profile") and the literal
enforcement of source-drift.md:74's prose promise. Without this story the feature delivers
nothing.

**Independent Test**: Set `stages.source_ready.status` to `warning` in a table's
`readiness-status.yaml` while `stages.mapping_ready.status` is `pass`; run `retail check`;
confirm it fails with an HR3 `stale_pass` finding naming `mapping_ready`, and confirm the
YAML file is byte-for-byte unchanged after the run (no field was written).

**Acceptance Scenarios**:

1. **Given** `source_ready` is `pass` and every downstream stage is `not_started`, **When**
   `retail check` runs, **Then** HR3 reports no finding for that table (nothing downstream
   is built on a drifted profile yet).
2. **Given** `source_ready` is `warning` and `mapping_ready` is `pass`, **When** `retail
   check` runs, **Then** HR3 reports exactly one `stale_pass` finding naming `mapping_ready`
   and citing the drifted `source_ready` status as the reason.
3. **Given** `source_ready` is `blocked` and `mapping_ready`, `silver_ready`, and
   `gold_ready` are all `pass`, **When** `retail check` runs, **Then** HR3 reports one
   `stale_pass` finding per stale downstream `pass` stage (three findings), each naming its
   own stage.
4. **Given** any of the above drifted cases, **When** `retail check` runs and then the
   table's `readiness-status.yaml` is re-read from disk, **Then** every field is identical
   to before the run -- HR3 wrote nothing.

---

### User Story 2 - An approval-bearing `pass` whose evidence changed after sign-off must show a re-review (Priority: P1)

A table's `mapping_ready` stage is `pass`, citing `mappings/<table>/source-map.yaml` as
evidence, with a recorded `approvals[]` entry dated `2026-06-01` by a named data owner.
On `2026-06-20`, `source-map.yaml` is edited and committed again (a legitimate follow-up
change, not necessarily malicious) -- but the approval date was never bumped and no new
sign-off was recorded. The thing the human approved is no longer the thing on disk. With
HR3, `retail check` fails with a `stale_pass` finding naming `mapping_ready`, the changed
evidence path, the approval date, and the evidence's later commit date -- until a human
either re-approves (a fresh `approvals[]` entry with a later date) or records a
`stale_review` reaffirming the stage is still sound.

**Why this priority**: This is the second half of the gap description ("a `pass` whose
evidence file changed after the approval date must show a re-review") and is the general
case that does not require drift at all -- any post-approval edit to cited evidence is a
silent staleness risk today. Equally load-bearing as User Story 1.

**Independent Test**: Commit a change to an evidence path cited by an already-`pass`,
already-approved stage, with the new commit dated after the recorded `approvals[].at`; run
`retail check`; confirm an HR3 `stale_pass` finding fires naming the stage, the changed
evidence path, and both dates.

**Acceptance Scenarios**:

1. **Given** an approval-bearing stage is `pass` with `approvals[].at` = `2026-06-01` and
   its cited evidence path's last commit date is `2026-05-20` (evidence predates the
   approval), **When** `retail check` runs, **Then** HR3 reports no finding for that stage
   (the human signed off on the current content).
2. **Given** the same stage, **When** the cited evidence path is committed again on
   `2026-06-20` (after the `2026-06-01` approval) with no new `approvals[]` entry, **Then**
   `retail check` fails with an HR3 `stale_pass` finding naming the stage, the changed
   evidence path, the approval date, and the evidence's later commit date.
3. **Given** the stale state in scenario 2, **When** a human adds a fresh `approvals[]`
   entry for that stage dated `2026-06-21` (on or after the evidence's commit date), **Then**
   a subsequent `retail check` run reports no HR3 finding for that stage (the re-approval
   clears it).
4. **Given** an approval's `at:` date is missing, malformed, or unparseable, **When**
   `retail check` runs, **Then** HR3 treats this as its own finding (a distinct message,
   not a silently-skipped check and not a fabricated date) -- the ambiguity is surfaced,
   never guessed past.

---

### User Story 3 - A human reaffirms a stale pass without re-running the whole approval, and the reaffirmation traces to a named person (Priority: P2)

Rather than re-approving from scratch, a named human reviews a `stale_pass` finding and
judges the stage is still sound (e.g., the evidence edit was a typo fix that does not change
the ruling). They record a `stale_review` entry -- a new top-level key in
`readiness-status.yaml`, naming the stage, the evidence path that triggered the finding, the
reviewer (in the same `Person Name (authority_class)` shape RS1 already requires of
`approvals[]`), the review date, and a short note. A `stale_review` dated on or after the
triggering evidence's commit date clears the HR3 finding for that specific stage/evidence
pair; the agent can construct and offer the entry as a draft, but only a shape-valid,
human-named entry counts, and the agent never writes it into the file on the human's
behalf without them supplying the name.

**Why this priority**: This is the intended day-to-day resolution path (lighter than a full
re-approval) and completes the escape hatch source-drift.md:74 implies ("the human/agent
re-runs the stage gate") without requiring every trivial evidence touch-up to trigger a full
re-approval cycle. It depends on Stories 1/2 existing first (there is nothing to reaffirm
against otherwise), so it is P2.

**Independent Test**: Starting from the stale state in User Story 2 scenario 2, add a
`stale_review` entry naming a valid `Person Name (authority_class)` reviewer dated on or
after the evidence's commit date; run `retail check`; confirm the HR3 finding for that
stage/evidence pair no longer appears, and confirm no other file was modified.

**Acceptance Scenarios**:

1. **Given** the stale state from User Story 2 scenario 2, **When** a `stale_review` entry
   is added naming `stage: mapping_ready`, a shape-valid reviewer, and a date on or after the
   evidence's last commit date, **Then** `retail check` no longer reports the HR3 finding for
   that stage/evidence pair.
2. **Given** a `stale_review` entry whose `reviewer` field is a bare role token (e.g.
   `"data_owner"`) rather than `"Person Name (authority_class)"`, **When** `retail check`
   runs, **Then** the entry does NOT count toward clearing the finding, and HR3 reports a
   distinct invalid-reviewer finding (mirroring RS1's C4 discipline) rather than silently
   accepting it.
3. **Given** a `stale_review` entry dated BEFORE the evidence's triggering commit date,
   **When** `retail check` runs, **Then** the finding still fires (a reaffirmation cannot
   predate the thing it reaffirms).
4. **Given** the agent is asked to "clear this stale_pass finding", **When** it responds,
   **Then** it drafts the `stale_review` entry's stage/evidence/note fields but leaves the
   `reviewer` name for the human to supply, and it does not commit the entry on the human's
   behalf without that name (Principle V: never self-grant).

---

### Edge Cases

- What happens when a table has NO `readiness-status.yaml` at all? HR3 does not fire (there
  is no committed state to compare); this mirrors RS1's existing "absence is not an error"
  handling and is not a new case this feature invents.
- What happens when `source_ready.status` is `not_started` (never yet profiled) and a
  downstream stage is somehow `pass`? That is already an RS1-adjacent structural oddity
  (a stage entered before its predecessor passed); HR3 does not layer a second finding on
  top of a state RS1 already flags as invalid stage-order -- HR3's drift-triggered check
  applies only when `source_ready` is specifically `warning` or `blocked` (a recorded
  drift signal), not `not_started`.
- What happens when an approval-bearing stage is `pass` but cites NO evidence at all? RS1
  already rejects a `pass` with empty `evidence[]`; HR3 has nothing to date-compare and does
  not fire a second finding for the same root defect.
- What happens when an evidence path cited by a `pass` stage does not exist on disk (e.g. a
  stale citation to a deleted file)? HR3 reports this as its own distinct finding (an
  unresolvable evidence citation) rather than silently skipping the comparison or treating a
  missing file as "not changed."
- What happens when MULTIPLE evidence paths are cited and only one changed after approval?
  HR3 fires -- one changed citation is enough; it does not require every cited path to have
  moved.
- What happens on the exact same calendar date for both the approval and the evidence
  commit (date-granularity tie)? HR3 treats same-day as NOT stale (the comparison is
  evidence-commit-date STRICTLY LATER than approval date) -- this is the conservative
  direction for a day-granularity signal and avoids false positives from approve-and-commit
  same-day workflows. Confirmed as the shipped default (see Clarifications); FR-003's
  "strictly later" wording already encodes it.
- What happens when a stage's `evidence[]` list contains a free-text entry with NO
  extractable repo-relative path token at all (e.g. `"retail check exit 0 (S1-S7);
  PK transaction_id re-proven unique"` or `"approval recorded in approvals[] below
  (data owner, 2026-06-25)"`) -- both real, committed forms today? HR3 treats such an
  entry as prose, not a citation: it is skipped by both the date-comparison (FR-003) and
  the unresolvable-citation check (FR-013). Only an evidence entry containing a
  repo-relative path token is a "cited evidence path" for HR3's purposes; see
  Clarifications for the extraction rule and why this is required for SC-006.
- What happens when an approval-bearing stage has MORE THAN ONE `approvals[]` entry for
  the same stage (e.g. an original approval plus a later re-approval)? HR3 compares each
  cited evidence path's commit date against the MOST RECENT (latest `at`) `approvals[]`
  entry for that stage, not the earliest -- this is what makes a fresh re-approval
  (User Story 2, Acceptance Scenario 3) actually clear the finding. See Clarifications.
- What happens when a mechanical stage with no `approvals[]` concept (`silver_ready`,
  `gold_ready`) is `pass` and drift fires at Source Ready? Approval-lag staleness (User
  Story 2) does not apply to these stages (they carry no approval date to compare against),
  but drift-triggered staleness (User Story 1) still applies -- a mechanical `pass` built on
  a drifted source is exactly as suspect as an approval-bearing one, and User Story 1's
  finding covers it independently of any approval date.
- What happens when the repository has uncommitted (working-tree) edits to a cited evidence
  file that have not yet been committed? HR3 reads committed git history only (Principle IX
  reproducibility); an uncommitted edit is invisible to it until committed, exactly like
  every other `retail check` rule that reasons over `ctx.tracked_files`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST implement exactly one new static `retail check` rule with the
  reserved id `HR3` that fails CLOSED (an ERROR-severity finding that fails the check run,
  per Principle I) rather than merely warning, for both conditions below.
- **FR-002**: HR3 MUST raise a `stale_pass` finding for every stage recorded `pass` in a
  table's `readiness-status.yaml` when that table's `stages.source_ready.status` is
  `warning` or `blocked` (the committed source-drift signal). Each finding MUST name the
  specific stale stage; a table with N stale downstream `pass` stages produces N findings,
  not one rolled-up finding. A stage that is simultaneously drift-stale (FR-002) AND
  approval-lag-stale (FR-003) MUST produce both findings independently, with no
  deduplication or merging -- they name different root causes (an upstream drift signal
  vs. a specific evidence path outrunning its own approval) and clear through different
  human actions, so collapsing them into one finding would hide which cause remains
  unresolved (see Clarifications).
- **FR-003**: HR3 MUST raise a `stale_pass` finding for an approval-bearing stage recorded
  `pass` when at least one evidence path that stage's `pass` cites has a git-commit date
  strictly later than the date recorded in that stage's matching `approvals[].at` entry.
  The finding MUST name the stage, the specific evidence path that changed, the recorded
  approval date, and the evidence's later commit date. Only an `evidence[]` entry
  containing an extractable repo-relative path token that resolves to a path in
  `ctx.tracked_files` counts as a "cited evidence path" for this comparison; a free-text
  `evidence[]` entry with no such token (e.g. a narrative summary of a check result) is
  not a citation and is neither date-compared nor treated as evidence at all (see
  FR-013 for the sibling case of a path token that IS present but does not resolve).
  When a stage's `approvals[]` carries more than one entry for that stage, HR3 MUST use
  the entry with the latest `at` date as "that stage's matching `approvals[].at` entry"
  (the most recent sign-off is the one the current evidence must not have outrun).
- **FR-004**: HR3 MUST use the evidence path's git-commit history (the reproducible,
  version-controlled signal) to determine "changed after approval," and MUST NOT use
  filesystem modification time (`mtime`) as the change signal -- filesystem mtime reflects
  local checkout time, not repository history, and is not reproducible across clones
  (Principle IX). Specifically, HR3 MUST use each commit's AUTHOR date, not its committer
  date, for both the evidence path's "last changed" date and any other git-commit date it
  reads -- author date reflects when the content was actually written, while committer
  date can be rewritten by a rebase or cherry-pick long after the fact and would make
  evidence look freshly "changed" for reasons unrelated to the human editing it (see
  Clarifications).
- **FR-005**: HR3 MUST NOT write, modify, or append to `readiness-status.yaml` or any other
  source artifact under any circumstance. It reports findings the same way every other
  `retail check` rule does (rule id + message + file locator) and stops. This includes never
  writing a `blocking_reasons[]` entry into the file (which would itself manufacture an RS1
  violation, since RS1 rejects `blocking_reasons[]` on a non-`blocked` stage) and never
  changing a stage's `status` field.
- **FR-006**: The system MUST define exactly one new, optional, additive top-level key in
  `readiness-status.yaml`, named `stale_review`, structurally parallel to `approvals[]`: a
  list of entries each carrying `stage`, `evidence` (the specific path being reaffirmed),
  `reviewer`, `at`, and an optional `note`. A `readiness-status.yaml` without this key is
  valid and unaffected (back-compatible with every already-filled instance).
- **FR-007**: A `stale_review` entry MUST clear the corresponding HR3 approval-lag finding
  (FR-003) for that specific (stage, evidence path) pair only when: (a) its `reviewer` field
  is shape-valid in the same form RS1 requires of `approvals[].owner`
  ("Person Name (authority_class)"; reuse RS1's validation discipline, do not redefine a
  second shape), and (b) its `at` date is on or after the triggering evidence's git-commit
  date. A `stale_review` entry that fails either condition MUST NOT clear the finding.
- **FR-008**: When a `stale_review` entry's `reviewer` field is not shape-valid (a bare role
  token, a name with no class, or an unknown class), HR3 MUST report this as a distinct
  finding, mirroring RS1's existing C4 discipline for `approvals[].owner`, rather than
  silently ignoring or silently accepting the entry.
- **FR-009**: HR3 MUST NOT clear, resolve, or auto-populate a `stale_review` entry on its
  own. The agent MAY draft the `stage`, `evidence`, and `note` fields of a candidate entry
  for a human to complete, but MUST leave the `reviewer` name for a human to supply and MUST
  NOT commit a `stale_review` entry without a human-supplied reviewer name (Principle V:
  never self-grant a readiness pass or its reaffirmation).
- **FR-010**: HR3's drift-triggered check (FR-002) MUST consume the source-drift signal
  exactly as `docs/readiness/source-drift.md` already defines it as observable today
  (`stages.source_ready.status` in the committed `readiness-status.yaml`); it MUST NOT
  invoke, assume, or depend on a live re-profiling runtime, a `retail drift` CLI, or any
  database connection (Principle VIII; no such runtime exists).
- **FR-011**: HR3's approval-lag check (FR-003) applies only to stages that carry an
  `approvals[]` concept (the four approval-required stages recognized by RS1: mapping_ready,
  semantic_model_ready, dashboard_ready, publish_ready, plus a file-source `source_ready`
  approval where applicable). It MUST NOT be applied to a mechanical stage
  (`silver_ready`, `gold_ready`) that carries no approval date to compare against; those
  stages remain covered only by the drift-triggered check (FR-002) when applicable.
- **FR-012**: HR3 MUST NOT emit any numeric decay, staleness, or confidence score, and MUST
  NOT emit a completeness or "N of M" count (hard rule #9). Every finding is a discrete
  `stale_pass` (or invalid-reviewer, per FR-008) finding tied to a specific stage and,
  where applicable, a specific evidence path -- never a rolled-up numeric measure of "how
  stale" a table is.
- **FR-013**: When a `pass` stage's `evidence[]` entry contains an extractable
  repo-relative path token that does NOT resolve to a path in `ctx.tracked_files` (i.e. it
  looks like a citation but the file is absent or unreadable), HR3 MUST report a distinct
  finding for the unresolvable citation rather than silently skipping the date comparison
  for that path or treating its absence as "not changed." This does NOT apply to a
  free-text `evidence[]` entry that never contained an extractable path token in the first
  place (FR-003) -- that entry is prose, not an unresolvable citation.
- **FR-014**: When an `approvals[].at` date is missing, malformed, or otherwise
  unparseable for a stage HR3 is evaluating under FR-003, HR3 MUST report a distinct
  finding naming the parse failure rather than skipping the stage silently or assuming a
  default date.
- **FR-015**: HR3 MUST be additive to the existing rule registry: it MUST NOT change RS1's
  behavior, MUST NOT remove or relax any existing `retail check` rule, and MUST NOT change
  the meaning of any existing `readiness-status.yaml` field. The only new schema surface is
  the `stale_review` key (FR-006).
- **FR-016**: All authored artifacts (rule module, doc updates, template additions) MUST be
  ASCII, UTF-8 without BOM, and MUST use short repo-relative paths (Windows 260-char
  budget) (Principle IX).
- **FR-017**: The feature MUST NOT introduce any new readiness stage, any new
  `retail validate` live check, or any executor/adapter code; HR3 is a static, read-only
  `retail check` rule exactly like RS1, operating on already-tracked files
  (`ctx.tracked_files`) and git history only.

### Key Entities

- **`stale_pass` finding**: an HR3-raised `retail check` finding (rule id `HR3`, ERROR
  severity) naming one stage of one table as built on stale evidence, either because
  Source Ready has recorded drift (FR-002) or because a cited evidence path changed after
  the stage's approval date (FR-003). Carries no score; traces to a specific stage and
  (for FR-003) a specific evidence path and two dates.
- **`stale_review` entry**: a new, optional, additive `readiness-status.yaml` top-level
  list entry (`stage`, `evidence`, `reviewer`, `at`, optional `note`) a named human records
  to reaffirm that a `pass` stage remains sound despite a later evidence change. Structurally
  parallel to `approvals[]`; never written by the agent without a human-supplied reviewer
  name.
- **Source-drift signal**: the existing, already-defined `stages.source_ready.status`
  field (`warning`/`blocked`) from `readiness-status.yaml`, as already specified by
  `docs/readiness/source-drift.md`. HR3 consumes it; it does not redefine or recompute it.
- **Approval record**: the existing `approvals[]` entry (`stage`, `owner`, `at`) RS1 already
  validates for shape. HR3 reads its `at` date; it does not alter RS1's ownership/shape
  rules.
- **Evidence git-commit date**: the reproducible "when did this path last change" signal
  HR3 uses in place of filesystem mtime -- the last commit date, in tracked git history, of
  a path cited in a stage's `evidence[]`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A table with `source_ready` recorded `warning`/`blocked` and one or more
  downstream `pass` stages produces exactly one HR3 `stale_pass` finding per stale
  downstream stage, every time `retail check` runs against it -- 0 such tables pass
  `retail check` silently.
- **SC-002**: A table with an approval-bearing `pass` stage whose cited evidence has a
  later git-commit date than its recorded approval produces an HR3 finding naming the
  stage, the changed path, and both dates -- 0 such tables pass `retail check` silently.
- **SC-003**: 0 `retail check` runs of HR3, across every acceptance scenario in this spec,
  write, modify, or append to `readiness-status.yaml` or any other tracked file -- the rule
  is verifiably read-only (diff of the working tree before and after a check run is empty).
- **SC-004**: 0 HR3 findings, and 0 `stale_review` entries, contain a numeric decay,
  staleness, confidence, or completeness score (hard rule #9).
- **SC-005**: A `stale_review` entry that is shape-valid (named reviewer + authority class)
  and dated on or after the triggering evidence's commit date clears the matching HR3
  finding on the next `retail check` run, and no other finding or file changes as a side
  effect.
- **SC-006**: Every existing filled `readiness-status.yaml` instance in the repo (that
  carries no drift and no post-approval evidence edit) continues to pass `retail check`
  with 0 new HR3 findings after HR3 ships -- the new rule adds no false positive against
  the current committed state.

## Assumptions

- `docs/readiness/source-drift.md` remains the authoritative definition of what "drift"
  means and how it is recorded (`stages.source_ready.status`); this feature reads that
  signal and does not redefine the drift taxonomy.
- `mappings/<table>/readiness-status.yaml` (ADR 0004) is the canonical, per-table state
  artifact; HR3 reads it exactly as RS1 already does, over the same `ctx.tracked_files`
  surface `retail check` already walks.
- Git commit history of a tracked path is a reproducible, available signal at `retail
  check` time (the same class of git-metadata read `src/retail/rules/git_meta.py` already
  performs for other rules); a shallow clone without full history is an environmental
  concern for the CI runner, not a new design constraint this feature introduces.
- The `Person Name (authority_class)` owner shape and its four authority classes (analyst,
  governance, data_owner, metric_owner) already defined and validated by RS1 are reused
  as-is for `stale_review.reviewer`; this feature does not define a new authority
  vocabulary.
- No live database connection, drift-detection runtime, or `retail drift` CLI exists or is
  assumed by this feature (Principle VIII); HR3 operates purely on already-committed,
  already-tracked text/YAML and git history.
- The `stale_review` key is additive only; no migration of existing `readiness-status.yaml`
  files is required, and their absence of the key is not itself a finding.
- The same-day tie-breaking direction for the approval-vs-evidence date comparison (see
  Edge Cases) is a reversible rule-behavior default, not a Principle-V judgment call;
  confirmed as "same-day is not stale" (see Clarifications) and encoded in FR-003's
  "strictly later" wording.
- Only an `evidence[]` entry containing an extractable repo-relative path token is a
  "cited evidence path" for HR3's date-comparison (FR-003) and unresolvable-citation
  (FR-013) checks; a free-text entry with no such token is prose and is not evaluated by
  either check (see Clarifications). When a stage carries more than one `approvals[]`
  entry, the latest `at` date is the one HR3 compares evidence against (see
  Clarifications).

## Clarifications

### Session 2026-07-04

- Q: On the exact same calendar date for both an approval and an evidence commit
  (date-granularity tie), does HR3 treat this as stale or not-stale? -> A: [Default
  adopted] Same-day is NOT stale -- the comparison is evidence-commit-date STRICTLY LATER
  than the approval date. This is the conservative direction for a day-granularity
  signal (avoids false positives from legitimate approve-and-commit-same-day workflows)
  and is a reversible rule-behavior choice, not a Principle-V judgment call. Touches
  FR-003; the Edge Cases same-day bullet and the Assumptions bullet on this topic are
  updated to state the confirmed default rather than an open marker.
- Q: `evidence[]` entries in real, committed `readiness-status.yaml` files are free text,
  and many carry no repo-relative path at all (e.g. `"retail check exit 0 (S1-S7); PK
  transaction_id re-proven unique"`, `"approval recorded in approvals[] below (data
  owner, 2026-06-25)"` -- both present in `mappings/retail_store_sales/
  readiness-status.yaml` today). If HR3 treated every `evidence[]` string as a citation,
  these prose entries would either be wrongly date-compared or wrongly flagged as
  unresolvable citations (FR-013), which would fire against the CURRENT committed state
  and break SC-006 ("0 new HR3 findings" against tables with no drift and no post-approval
  edit). What counts as a "cited evidence path" HR3 must evaluate? -> A: [Default
  adopted] Only an `evidence[]` entry containing an extractable repo-relative path token
  that resolves to a path in `ctx.tracked_files` is a "cited evidence path." A free-text
  entry with no extractable path token is prose, not a citation, and is skipped by both
  the date-comparison (FR-003) and the unresolvable-citation check (FR-013); FR-013 fires
  only when a path token IS present but does not resolve to a tracked file. This is a
  parsing/scope default over the existing free-text `evidence[]` shape, not a schema
  change (FR-015 stays intact -- `evidence[]` is not restructured into typed path
  entries). Touches FR-003, FR-013, and the Edge Cases/Assumptions sections; verified
  against `mappings/retail_store_sales/readiness-status.yaml` as the SC-006 canary (its
  prose-only and non-path evidence entries produce zero HR3 findings under this default).
- Q: RS1 permits more than one `approvals[]` entry for the same stage (a re-approval adds
  a new entry rather than replacing the old one), and User Story 2's Acceptance Scenario 3
  clears a stale finding by recording a FRESH, later-dated approval. FR-003 as originally
  worded compared evidence against "that stage's matching `approvals[].at` entry"
  (singular) without saying which entry wins when several exist for the same stage. Which
  entry governs the comparison? -> A: [Default adopted] HR3 compares cited evidence
  against the MOST RECENT (latest `at`) `approvals[]` entry recorded for that stage, not
  the earliest. This is the only reading under which User Story 2 Acceptance Scenario 3
  (a fresh, later-dated approval clears the finding) is coherent, and is a mechanical
  rule-behavior default rather than a Principle-V judgment call. Touches FR-003 and the
  new Edge Cases bullet on multiple approvals per stage.
- Q: Does a `stale_review` entry clear a drift-triggered `stale_pass` finding (FR-002,
  User Story 1) in addition to an approval-lag finding (FR-003, User Story 2), or is
  `stale_review` scoped to approval-lag only? -> A: OPEN owner ruling. The spec text as
  written (FR-007, User Story 3) scopes `stale_review` to "the corresponding HR3
  approval-lag finding (FR-003)" only, and User Story 1's own resolution path is the
  human editing `stages.source_ready.status` (re-confirming or demoting) rather than
  filing a reaffirmation against a drift-triggered finding. Whether a future revision
  should also let a `stale_review` entry cover a drift-triggered finding (e.g. "I
  re-confirmed this downstream stage is still sound despite the upstream drift, without
  yet resolving the drift itself") is a product-scope decision about what the
  reaffirmation escape hatch is FOR, not a mechanical default this stage should silently
  pick -- left OPEN for the feature owner to confirm at plan time. Until answered, HR3 MUST
  implement `stale_review` as FR-007 already states: clearing FR-003 approval-lag findings
  only; a drift-triggered FR-002 finding clears only via a change to
  `stages.source_ready.status` or the stale downstream stage's own status, never via
  `stale_review`. Touches FR-002/FR-007/User Story 1/User Story 3 boundary.
- Q: A git commit carries two dates -- author date (when the content was written) and
  committer date (when the commit object was last written, which a rebase or cherry-pick
  can change long after the original edit). FR-004 said "git-commit date" without
  specifying which one governs the approval-lag comparison; using committer date would let
  a routine history rewrite (unrelated to any human re-editing the evidence) spuriously
  make an already-approved file look freshly changed, and Principle IX is the reason FR-004
  gives for preferring git over filesystem mtime in the first place -- the intent is
  reproducibility of WHEN THE CONTENT CHANGED, not of when the commit object was last
  touched. Which date governs? -> A: [Default adopted] Author date, not committer date, for
  every git-commit date HR3 reads (the evidence path's "last changed" date used throughout
  FR-003, FR-004, User Story 2, and Acceptance Scenarios). This is a reversible
  implementation-signal default consistent with Principle IX's own stated rationale, not a
  Principle-V judgment call. Touches FR-004.
- Q: FR-002 (drift-triggered) and FR-003 (approval-lag) are independent checks reading
  different signals (`source_ready.status` vs. an evidence path's commit date against its
  approval date). Neither requirement said what happens when the SAME stage qualifies under
  both at once -- e.g. `source_ready` is `blocked` AND `mapping_ready`'s cited evidence was
  also edited after its own approval. Does the stage get one finding or two? -> A: [Default
  adopted] Both findings fire independently, with no deduplication -- a stage that is
  simultaneously drift-stale and approval-lag-stale produces one `stale_pass` finding for
  each triggering condition, because each names a different root cause and clears through a
  different human action (resolving the upstream drift vs. re-approving or reaffirming the
  specific evidence path). This is a mechanical rule-behavior default, not a Principle-V
  judgment call. Touches FR-002.
