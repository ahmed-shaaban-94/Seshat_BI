# Feature Specification: Source Data-Contract -- Forward Schema + Arrival + Restatement Policy

**Feature Branch**: `105-source-data-contract-restatement`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Gap #10. Source data-contract: forward schema + arrival and
restatement policy -- a forward source data-contract (expected schema + arrival + a
declared restatement policy for late-arriving/corrected rows) the supplier is held to,
turning drift from reactive-vs-baseline into a preventive agreed-correct gate. Serves:
Stage 1 Source Ready (upstream boundary). Lens/justification: Big-data (late data changes
yesterday's totals) + Principle IV. Complements #2 (decay) and #16 (idempotency)."

## Overview

Every readiness check the Seshat BI spine runs today at Source Ready is REACTIVE-vs-BASELINE:
`docs/readiness/source-drift.md` re-profiles a source and compares the new shape against
whatever shape was profiled last time, and 090 (`meta.freshness` / HR4) declares an internal
staleness tolerance and checks it is present. Both answer "did the source change since we
last looked?" Neither answers a different, earlier question: "what did the upstream SUPPLIER
agree to deliver in the first place, and what happens when they correct a row after the fact?"
Nothing in the repo captures that up front. The result is the exact failure the
`bi-bigdata-knowledge` skill's big-data lens describes: yesterday's published totals are
correct at publish time, then a source system quietly restates a handful of rows for a date
that was already loaded and approved -- a chargeback posts three days late, a return is
re-coded, a promo line is corrected -- and there is no supplier-facing commitment describing
whether that is expected, how it will arrive, or how the warehouse should treat it. Drift
detection can only notice this AFTER it already happened, by comparing against whatever
baseline was profiled; there is no PREVENTIVE artifact stating what "agreed-correct" arrival
and correction behavior looks like before the first load ever runs.

This feature adds that preventive artifact: a NEW, generic, human-authored forward
declaration -- the **source data-contract** -- naming (a) the expected column-level schema,
(b) the expected arrival cadence, and (c) a declared restatement policy for late-arriving or
corrected rows (does the supplier ever resend a closed period; if so, how is a correction
identified and how far back can it reach). It ships as a NEW, separate template,
`templates/source-data-contract.yaml`, filled once per onboarded table, and it reserves ONE
new static `retail check` rule, id **HR12**, that verifies the contract file is PRESENT and
STRUCTURALLY WELL-FORMED (every required section has a non-placeholder value) for any table
that declares one. Per Principle VIII (static-first / live-deferred), this feature is the
STATIC HALF ONLY: it does not open a database connection, it does not compare a live
`MAX(<date column>)` against the declared cadence, and it does not detect an actual
restatement event on live data -- those are live-surface concerns explicitly deferred to a
future `retail validate` extension. Per Principle V, the contract's actual VALUES (what
schema, what cadence, what restatement policy) are owner-supplied facts about a real upstream
system; the agent never invents them, and HR12 never judges whether a declared policy is
"good," only whether one was declared and is well-formed.

## Boundary against neighbouring shipped work (read first)

This feature is a genuinely NEW, forward-looking artifact. Several existing and
in-flight neighbours sit close to it and must stay distinct.

- **090 source-freshness-gate (`meta.freshness` in `source-map.yaml`, rule HR4;
  draft, same date)** is the sharpest boundary and must be drawn explicitly, because
  both features touch "arrival" at Source Ready. 090's `meta.freshness` is an INTERNAL
  staleness TOLERANCE: how stale is this warehouse allowed to let its own copy of the
  source get before it is a blocker, checked by comparing a declared cadence against
  (eventually) a live `MAX(<date column>)`. This feature's arrival declaration is a
  SUPPLIER-FACING AGREEMENT: what the upstream system has committed to deliver and when,
  independent of how the warehouse later measures its own staleness. The two concepts can
  agree in value but are not the same field and are not read by the same rule: HR12 reads
  only the new `templates/source-data-contract.yaml` copy at
  `mappings/<table>/source-data-contract.yaml`; HR4 reads only `meta.freshness` inside
  `source-map.yaml`. Neither rule reads the other's file or key, and this feature adds no
  key to `source-map.yaml` (the collision-avoidance allocation, non-negotiable). A table
  may carry both, one, or neither artifact without either rule needing to know about the
  other.
- **`docs/readiness/source-drift.md` (roadmap F014, design-only, "Later" tier)** is the
  conceptual foil named directly in this feature's own justification (Overview). Source-drift
  is REACTIVE-vs-BASELINE: it re-profiles a source over time and flags when the observed
  shape no longer matches a previously recorded baseline (columns added/removed, types
  changed, missingness/cardinality shifted). This feature is PREVENTIVE-AGREED-CORRECT: it
  records, before the fact, what shape and arrival/restatement behavior the supplier
  committed to, so a later drift comparison has an agreed baseline to compare against rather
  than just "whatever we last happened to observe." This feature does not edit
  `source-drift.md`, its taxonomy, or its (future) `source-drift-report.md` template, and it
  does not fold restatement into the nine-class drift taxonomy. A future drift detector MAY
  choose to compare against this contract's declared schema instead of (or in addition to) a
  prior profile -- that wiring is explicitly out of scope here.
- **089 readiness-decay-demotion (rule HR3; draft, same date)** closes the DOWNSTREAM half of
  the same big-data lens this feature's justification cites ("Complements #2"): HR3 fires
  AFTER a drift or a stale approval is observed, raising a `stale_pass` blocker on every
  downstream stage built on the now-suspect profile. This feature fires BEFORE any load ever
  runs, declaring what correct arrival/restatement looks like so there is a named agreement
  to be stale against. HR12 does not read `readiness-status.yaml` and does not raise a
  `stale_pass` blocker; HR3 does not read the source data-contract. The two are sequential
  neighbours (declare-first, demote-later), not overlapping checks.
- **093 reload-idempotency-readiness (rule HR7; draft, same date)** closes the LOAD-MECHANISM
  half of the same lens ("Complements #16"): HR7 checks that a table's OWN load (its
  migration / `load-policy.md`) declares how it stays idempotent when re-run. This feature's
  restatement policy is a SOURCE-SUPPLIER commitment (does the upstream system ever resend a
  closed period, and how is a resend identified) captured at Source Ready, before any silver
  or gold migration exists. HR7 answers "if we reload, will we double-count"; this feature
  answers "will the supplier ever hand us a correction to reload in the first place, and how
  do we recognize it." A table's restatement policy here may name the fact that a downstream
  reload should be idempotent, but this feature does not declare or check idempotency itself
  -- it cites 093/HR7 as the place that concern is enforced, and does not restate HR7's
  checks.
- **The source-mapping gate itself (Principle IV, spec 001; `templates/source-map.yaml`)**
  remains the DESCRIPTIVE map of what the source actually looks like once profiled and
  reviewed (grain, PK, per-column decisions). This feature's contract is a separate,
  FORWARD-LOOKING agreement about what the source is expected to look like and how it is
  expected to behave over time, authored as its own file precisely so it does not become a
  sixth concern competing for space inside `source-map.yaml` (which already carries the
  mapping gate's own five artifacts plus 090's `meta.freshness` and 087/092's conformance
  reads). `templates/source-data-contract.yaml` is a NEW, independent file under
  `mappings/<table>/`; it is not one of the five mapping-gate artifacts and does not change
  the Mapping Ready gate's required-artifact list.

This feature adds no new readiness stage. It adds one static rule (HR12) that runs at the
existing Source Ready stage as an additional, OPT-IN evidence check (see FR-002 on
enforcement posture), and one new declaration artifact
(`templates/source-data-contract.yaml`, filled per table at
`mappings/<table>/source-data-contract.yaml`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An analyst declares the forward contract before onboarding a table (Priority: P1)

An analyst onboarding a new source table fills in `mappings/<table>/source-data-contract.yaml`
before or alongside Source Ready profiling: the expected column-level schema (names and
types the supplier has committed to), the expected arrival cadence in plain terms (e.g. daily
by 6am, weekly on Mondays), and a restatement policy stating whether the supplier ever resends
rows for an already-loaded period, and if so, how a correction is identified (a
last-modified column, a resend flag, a full-period reload) and how far back a resend can
reach. `retail check` (rule HR12) verifies the file is present and every required section
carries a non-placeholder value.

**Why this priority**: This is the whole point of the feature -- without a filled contract to
check, there is nothing preventive to enforce, and the feature delivers no value.

**Independent Test**: Author `mappings/<table>/source-data-contract.yaml` with all three
sections (schema, arrival, restatement) filled with real values (no template placeholder
text remaining); running `retail check` reports HR12 as passing for that table.

**Acceptance Scenarios**:

1. **Given** a table whose `source-data-contract.yaml` has a filled schema list, a filled
   arrival cadence, and a filled restatement policy (including whether resends occur and how
   they are identified), **When** `retail check` runs, **Then** HR12 passes for that table
   and cites the contract file path as its evidence.
2. **Given** the same filled contract, **When** a human reviews it, **Then** every value is
   traceable to a real statement about the actual upstream source system, not an invented or
   generic placeholder.
3. **Given** a table with no `source-data-contract.yaml` at all, **When** `retail check` runs,
   **Then** HR12 does not fail for that table (the contract is opt-in per FR-002) and no other
   Source Ready evidence is affected.

---

### User Story 2 - A declared-but-incomplete contract fails closed (Priority: P1)

An analyst creates `mappings/<table>/source-data-contract.yaml` from the template but leaves
a required section as the unedited placeholder (for example, the restatement policy still
reads the template's placeholder text, or the arrival cadence field is blank). `retail check`
(HR12) fails CLOSED for that table, naming exactly which section is missing or still a
placeholder, rather than silently treating a half-filled contract as good enough or silently
skipping the check.

**Why this priority**: A contract that exists but is unfilled is worse than no contract at
all if the check does not notice -- it would look preventive while providing no real
agreement. This must hold from day one, alongside User Story 1, for the feature to be
trustworthy.

**Independent Test**: Author a `source-data-contract.yaml` with the schema section filled but
the restatement-policy section left as the template placeholder; running `retail check`
reports HR12 as failing for that table, naming the restatement-policy section specifically.

**Acceptance Scenarios**:

1. **Given** a `source-data-contract.yaml` whose restatement-policy section is unedited
   template placeholder text, **When** `retail check` runs, **Then** HR12 fails closed and
   the finding names the restatement-policy section as the incomplete one.
2. **Given** a `source-data-contract.yaml` with a blank or missing arrival-cadence field,
   **When** `retail check` runs, **Then** HR12 fails closed and the finding names the
   arrival section.
3. **Given** a `source-data-contract.yaml` with an empty schema list (no columns declared),
   **When** `retail check` runs, **Then** HR12 fails closed and the finding names the schema
   section.

---

### User Story 3 - The contract stays a static, forward artifact with no live enforcement (Priority: P2)

An analyst or reviewer inspects HR12's behavior and confirms it never opens a database
connection, never compares the declared arrival cadence against an actual live arrival
timestamp, and never detects an actual restatement event on live data -- it only checks that
the forward-looking declaration itself is present and well-formed. Live arrival and
restatement enforcement remain explicitly deferred to a future `retail validate` extension
(Principle VIII).

**Why this priority**: This is what keeps the feature inside its scope guard and prevents it
from silently growing into a live-surface feature; a single working static check (P1) is
already a viable, valuable slice, so the deferral confirmation is P2.

**Independent Test**: Run `retail check` with no DSN configured and no live database
reachable; HR12 still evaluates fully and produces a pass/fail result based only on committed
files, proving it needs no live connection.

**Acceptance Scenarios**:

1. **Given** no database connection is configured anywhere in the environment, **When**
   `retail check` runs, **Then** HR12 still evaluates and reports a result (pass, fail, or
   not-applicable) based solely on committed files.
2. **Given** a filled, well-formed contract, **When** `retail check` runs, **Then** HR12 does
   not attempt to verify the declared schema or cadence against any live table -- that
   remains explicitly out of scope and unimplemented.
3. **Given** the feature's documentation, **When** a reviewer reads it, **Then** it states
   plainly that live arrival-time comparison and live restatement-event detection are
   deferred, naming `retail validate` as the eventual home for that live check.

---

### Edge Cases

- What happens when a table has `source-map.yaml` but no `source-data-contract.yaml`? HR12
  treats the contract as opt-in (per the enforcement-posture default in FR-002): the table is
  not penalized for omitting it, and no other Source Ready evidence changes. This differs
  deliberately from a mandatory-presence rule that would fail every table retroactively.
- What happens when the declared restatement policy says the supplier NEVER resends a closed
  period? That is a valid, complete answer -- HR12 requires the section be filled with a real
  statement (including an explicit "never" with its stated basis), not that it describe a
  resend mechanism that does not exist.
- What happens when the declared schema in the contract no longer matches what
  `source-map.yaml` / the latest profile actually shows? HR12 does not compare the two files
  against each other -- that reactive-vs-baseline comparison is source-drift's job (see
  Boundary section), and this feature does not implement it. A future feature MAY wire the
  contract into drift detection; that wiring is out of scope here.
- What happens when a table declares both `meta.freshness` (090/HR4) and this feature's
  arrival section, and the two disagree (e.g. the contract says "daily by 6am" but
  `meta.freshness.expected_cadence` says weekly)? HR12 does not detect or flag that
  disagreement -- each rule reads only its own file and stays silent about the other's
  content, per the Boundary section. Reconciling the two, if ever needed, is a future
  cross-artifact concern, not this feature's.
- What happens when the contract template's placeholder text is copied verbatim into a real
  table's contract by mistake? HR12 fails closed for that table (User Story 2) rather than
  passing on unedited template prose.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST define a NEW, generic, copy-me template,
  `templates/source-data-contract.yaml`, declaring three required sections: (a) an expected
  column-level SCHEMA -- a list of entries, each carrying at minimum a column NAME and an
  expected TYPE; an entry with a name but no type is malformed on the same footing as an
  empty list (see FR-006), (b) an expected ARRIVAL cadence -- a plain-language free-text
  statement of when data is expected to land (e.g. "daily by 6am", "weekly on Mondays");
  HR12 checks only that the field is present and non-placeholder, and performs no semantic
  parsing of cadence structure or format, and (c) a declared RESTATEMENT policy -- a SINGLE
  free-text field (mirroring the arrival section's treatment) in which the owner states
  whether the supplier ever resends rows for an already-loaded period, and if so, how a
  correction is identified and how far back it can reach; HR12 checks only that the field
  is present and non-placeholder (one sentinel token for the whole section) and performs no
  semantic parsing or conditional sub-field validation of its contents -- a stated "never
  resends" is as complete an answer as a stated mechanism-plus-lookback (see Edge Cases).
- **FR-002**: The feature MUST reserve exactly one new static `retail check` rule, id
  **HR12**, that checks the PRESENCE and STRUCTURAL WELL-FORMEDNESS of a table's
  `mappings/<table>/source-data-contract.yaml` when that file exists for the table. Per
  Principle VI (defaults-then-deviations) and consistent with the 090/HR4 and 093/HR7
  precedents, the contract is OPT-IN: a table with no `source-data-contract.yaml` is not
  penalized by HR12's absence-case; HR12 fails CLOSED only when the file IS present but
  incomplete or malformed (a required section missing, blank, or left as unedited template
  placeholder text). A present file that is not valid YAML at all (a parse error) is a
  malformed case too: HR12 fails CLOSED naming the file itself, rather than raising an
  unhandled exception or silently skipping the table as not-applicable.
- **FR-003**: HR12 MUST NOT connect to a database, MUST NOT read or compute a live
  `MAX(<date column>)` or any other live arrival signal, and MUST NOT attempt to detect an
  actual restatement event on live data (Principle VIII, static-first / live-deferred). Live
  enforcement of this contract is explicitly deferred to a future `retail validate` extension
  and is out of scope for this feature.
- **FR-004**: HR12 MUST NOT read or write `source-map.yaml`, MUST NOT read or write
  `meta.freshness` (090/HR4's key), and MUST NOT read `readiness-status.yaml` or raise a
  `stale_pass` blocker (089/HR3's concern). It reads only
  `mappings/<table>/source-data-contract.yaml`.
- **FR-005**: The feature MUST NOT invent, infer, or default the actual VALUES of a table's
  schema, arrival cadence, or restatement policy -- these are owner-supplied facts about a
  real upstream system (Principle V). The agent's role is limited to authoring the generic
  template and the presence/well-formedness check; a human fills each table's copy.
- **FR-006**: HR12 MUST treat unedited template placeholder text in a required section as
  equivalent to that section being missing, and MUST fail closed naming the specific
  incomplete section (schema, arrival, or restatement) rather than a single undifferentiated
  failure. Detection MUST be purely structural, not semantic: `templates/source-data-contract.yaml`
  ships each required field pre-filled with a distinctive, greppable sentinel placeholder
  string (e.g. `REPLACE_ME: ...`-style token, one per section) that would not plausibly
  appear in a real owner-authored value; HR12 fails a section closed when that field is
  absent, blank/empty, or still contains the sentinel token verbatim. HR12 performs no
  judgment on whether a non-placeholder value is a "good" or "complete" answer (Principle V,
  FR-005) -- only whether the sentinel is gone.
- **FR-007**: The template and HR12 MUST stay generic (Principle VII): no worked-example
  (C086 / retail_store_sales) schema, cadence, or restatement specifics may be inlined into
  the template or into HR12's fixed messages; the worked example may appear only as a cited
  filled instance under `mappings/<table>/`.
- **FR-008**: The generated per-table contract MUST live at
  `mappings/<table>/source-data-contract.yaml`, co-located with the table's other mapping
  artifacts, and MUST NOT be merged into or stored as new keys inside `source-map.yaml`
  (collision-avoidance allocation, non-negotiable).
- **FR-009**: HR12 MUST NOT emit any numeric confidence / health / maturity score and MUST
  NOT emit a completeness count or "N of M" tally (hard rule #9). Its result is expressed
  only as pass / fail (or not-applicable when the file does not exist) plus the specific
  incomplete section(s) named on failure.
- **FR-010**: This feature MUST NOT add a new readiness stage and MUST NOT change the
  Mapping Ready gate's required five-artifact list; `source-data-contract.yaml` is an
  additional, independent artifact, not a sixth mapping-gate artifact.
- **FR-011**: All authored artifacts MUST be ASCII, UTF-8 without BOM (use `--` and `->`, no
  glyphs), and MUST use short repo-relative paths (Windows 260-char budget) (Principle IX).
- **FR-012**: Where the declared restatement policy names a downstream reload consequence,
  the template MUST point to 093/HR7 (`load-policy.md` / the reload-idempotency check) by
  reference rather than restating or re-checking idempotency itself (per the Boundary
  section).
- **FR-013**: **[OPEN -- owner ruling required, unresolved]** Whether HR12 is wired as a
  BLOCKING Source Ready condition once a table opts in (i.e., does declaring a
  `source-data-contract.yaml` retroactively make it mandatory to keep well-formed for that
  table going forward, blocking Source Ready `pass` on a later break), or whether it remains
  a best-effort evidence check that is recorded but never blocks the stage from reaching
  `pass`, is NOT decided by this spec and MUST NOT be defaulted by the agent. FR-002 adopts
  the opt-in default for the file's EXISTENCE only (no penalty for omitting it, mirroring
  090/HR4 and 093/HR7's own "declare or default" posture) -- that default is settled. The
  separate question of enforcement STRENGTH once a table has opted in is a governance-owner
  call (Principle V: business-policy/approval judgment, not a shape decision) and stays an
  open, unresolved item until a named governance owner rules on it via the approval-console
  workflow (see `## Clarifications` below). Until ruled, plan/implement MUST treat HR12 as
  non-blocking evidence only (never fails the Source Ready stage verdict itself, only its own
  pass/fail/not-applicable result), consistent with the letter of FR-002/FR-009's "evidence,
  not gate-of-the-stage" framing -- this fallback is a safe-default STANCE for implementation
  sequencing, not a resolution of the open question itself.

### Key Entities

- **Source data-contract**: the new per-table forward declaration
  (`mappings/<table>/source-data-contract.yaml`), instantiated from
  `templates/source-data-contract.yaml`. Carries an expected schema, an expected arrival
  cadence, and a declared restatement policy. Authored once per table by a human; read-only
  to HR12.
- **HR12 (reserved rule id)**: the new static `retail check` rule verifying presence and
  structural well-formedness of a table's source data-contract, when one exists. Fails
  closed on an incomplete or placeholder-only contract; is silent (not-applicable) when no
  contract file exists for the table.
- **Restatement policy**: the declared statement, inside the contract, of whether and how
  the upstream supplier resends or corrects rows for an already-loaded period (resend
  trigger, correction-identification mechanism, maximum lookback).
- **Arrival cadence**: the declared statement, inside the contract, of when the supplier
  commits to deliver data -- a supplier-facing agreement, distinct from 090's internal
  staleness tolerance (`meta.freshness`).
- **Expected schema (contract section)**: the declared column-level shape (name + type) the
  supplier commits to deliver -- a forward agreement, distinct from the descriptive,
  already-profiled shape recorded in `source-map.yaml`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A table that fills `source-data-contract.yaml` with real schema, arrival, and
  restatement values passes HR12, with the passing evidence citing the contract's committed
  path.
- **SC-002**: A table whose contract leaves any one of the three required sections as
  unedited template placeholder text fails HR12, and the failure names that specific section.
- **SC-003**: A table with no `source-data-contract.yaml` at all is not penalized by HR12 (the
  check is not-applicable for that table), confirming the opt-in posture.
- **SC-004**: HR12 evaluates to a result with no database connection configured or reachable,
  confirming it is fully static.
- **SC-005**: 0 generated or template artifacts contain a numeric confidence/health/maturity
  score or a completeness count.
- **SC-006**: 0 keys are added to `source-map.yaml` by this feature; the contract exists only
  as the separate `templates/source-data-contract.yaml` / `mappings/<table>/source-data-contract.yaml`
  files.
- **SC-007**: 0 generic artifacts (template, fixed rule messages) contain a worked-example
  (C086/pharmacy) domain specific.

## Assumptions

- `docs/readiness/source-ready.md` (Stage 1) is the stage this feature's evidence attaches
  to; the feature adds an additional, opt-in check at that existing stage rather than a new
  stage.
- The 090 (`meta.freshness`/HR4), 089 (`stale_pass`/HR3), and 093 (load-policy/HR7) features
  are drafted in parallel under the same collision-avoidance allocation and dated batch; they
  are treated here as reserved, distinct neighbours (per their own spec boundaries), not as
  already-shipped tools, since all four are Draft as of this writing.
- HR12 is the correct next free id in the `HR*` static-rule id family at the time of writing
  (HR1, HR2, HR4, HR6, HR7 are the other reserved/allocated ids found in-repo); the exact id
  is confirmed and reconciled against the live rule registry at plan/implement time.
- This feature is docs/template/rule-only; it adds no runtime executor beyond the one static
  `retail check` rule (HR12) and no Power BI / PBIP surface.
- Live arrival-time and live restatement-event detection are explicitly out of scope for this
  feature and are left to a future `retail validate` extension (Principle VIII); this feature
  does not name or commit to that extension's design.
- The enforcement-posture question in FR-013 (whether an opted-in contract can block Source
  Ready `pass` once broken) is left open for a governance-owner ruling; this feature's own
  default (FR-002) only covers the file's existence, not its ongoing blocking strength once
  present.

## Clarifications

### Session 2026-07-04

- **Q1 (FR-013)**: Should HR12 be wired as a BLOCKING Source Ready condition once a table
  opts in (declaring `source-data-contract.yaml` makes it mandatory to keep well-formed going
  forward, able to block Source Ready `pass` on a later break), or does it remain a
  best-effort evidence check that never blocks the stage? -> **Resolution: OPEN owner
  ruling.** This is a Principle-V business-policy/enforcement-strength judgment, not a shape
  decision the agent may default silently. Precedent from the same dated batch (090/HR4
  FR-014, 093/HR7's own analogous mandatory-vs-advisory question) also leaves this class of
  question unresolved rather than defaulted, confirming it is a genuine owner call and not an
  oversight. Left as `[OPEN -- owner ruling required, unresolved]` in FR-013; a safe
  non-blocking implementation stance is named as the interim fallback for plan/implement
  sequencing only, and does NOT resolve the question. Touches: **FR-013**.
- **Q2 (FR-006)**: FR-006 requires HR12 to "treat unedited template placeholder text... as
  equivalent to missing," but the spec did not say how HR12 mechanically recognizes
  placeholder text versus a real owner-authored value. -> **Resolution: Default adopted.**
  `templates/source-data-contract.yaml` ships each required field pre-filled with a
  distinctive, greppable sentinel token (e.g. a `REPLACE_ME`-style string) per section; HR12
  fails a section closed when the field is absent, blank, or still contains the sentinel
  verbatim -- a purely structural, non-semantic test, keeping HR12 inside Principle V (no
  judgment on whether a filled value is a "good" answer) and FR-009 (no scoring). Touches:
  **FR-006**.
- **Q3 (FR-001 / Edge Cases AS-3)**: FR-001 requires the schema section to declare "column
  name + expected type, at minimum," but Acceptance Scenario 3 (User Story 2) only specified
  that an EMPTY schema list fails HR12 -- it did not say whether a non-empty list of column
  names WITHOUT a paired type also fails. -> **Resolution: Default adopted.** Each declared
  schema entry MUST carry both a name and a type; an entry with a name but no type is
  malformed on the same footing as an empty list and fails HR12 closed, naming the schema
  section (consistent with FR-006's per-section, named-failure requirement). This keeps the
  schema section meaningful (a bare list of column names without types would not satisfy
  FR-001's own "name + expected type, at minimum" requirement). Touches: **FR-001**.
- **Q4 (FR-001, arrival section)**: FR-001 allowed the arrival-cadence statement to be
  "plain-language or structured"; it was unclear whether HR12 must parse or validate cadence
  FORMAT (e.g. recognizing "daily," "weekly on Mondays" as valid cadence vocabulary) or only
  check the field's presence. -> **Resolution: Default adopted.** The arrival section is
  free text; HR12 checks only that the field is present, non-blank, and not the sentinel
  placeholder (per Q2's mechanism) -- it performs no semantic parsing of cadence wording or
  structure. This keeps HR12 a structural presence/well-formedness check only, consistent
  with FR-003's static-first scope (no live-cadence comparison) and Principle V (the agent
  does not judge whether a stated cadence is well-formed prose, only whether one was stated).
  Touches: **FR-001**.
- **Q5 (FR-001, restatement section)**: FR-001(c) describes the restatement policy as
  having internal conditional structure ("whether the supplier ever resends... if so, how a
  correction is identified and how far back it can reach"), but unlike the schema section
  (Q3, resolved to a structured name+type list) and the arrival section (Q4, resolved to
  free text), the spec did not say whether HR12 must validate the restatement section's
  internal sub-fields (e.g. requiring an identification mechanism and a lookback value
  whenever resends are claimed to occur) or treat it as one undifferentiated free-text
  field. -> **Resolution: Default adopted.** The restatement section is a SINGLE free-text
  field, exactly like the arrival section (Q4's mechanism): HR12 checks only that the field
  is present, non-blank, and not the sentinel placeholder, performing no conditional
  sub-field or semantic validation of its contents. This is required by the edge case
  already in this spec stating that a supplier who NEVER resends a closed period is a
  valid, complete answer -- a rule that mandated a resend-identification mechanism or a
  lookback value whenever resends are claimed would be unable to also accept "never" as
  complete without smuggling in exactly the semantic, conditional judgment Principle V and
  FR-006 bar. Touches: **FR-001**.
- **Q6 (FR-002, malformed-YAML edge case)**: FR-002 names HR12 failing closed on a file that
  is "incomplete or malformed" but did not separately address a `source-data-contract.yaml`
  that exists and is not a placeholder-copy but is not valid YAML at all (a syntax error),
  as distinct from a structurally well-formed YAML document missing a required section. ->
  **Resolution: Default adopted.** An unparseable file is treated the same as a
  present-but-incomplete contract: HR12 fails CLOSED, naming the file itself (not a specific
  section, since none could be parsed) rather than raising an unhandled exception or
  silently treating the table as not-applicable. This is the same fail-closed posture
  FR-002/FR-006 already establish for the parseable-but-incomplete case, extended to the
  narrower case of a parse error, and emits no score (FR-009). Touches: **FR-002**.
