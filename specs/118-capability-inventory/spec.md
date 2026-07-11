# Feature Specification: Capability Inventory -- read-only, truthful "what can this kit do" surface

**Feature Branch**: `118-capability-inventory`

**Created**: 2026-07-11

**Status**: Draft

**Input**: User description: "A read-only surface that emits a truthful, categorical inventory of Seshat BI's shipped / advisory / agent-companion / human-gated / deferred capabilities, derived from committed reviewable project metadata (never inferred from mere file existence). Human-readable grouped output plus a stable machine-readable form. Distinguishes shipped, advisory, human-gated, spec-only, and deferred; never emits a numeric maturity/confidence/health score; grants or changes no readiness; writes no files; connects to no database; runs no Power BI. Canonical single source of truth for the inventory rather than duplicating claims across README and CLI code."

## Clarifications

### Session 2026-07-11

- Q: The original brief asked for a `seshat capabilities` / `retail capabilities`
  **CLI verb**. But `docs/roadmap/decisions/cli-verbs-vs-skill-driven.md` (Option B,
  ratified by the repo owner 2026-07-07) explicitly REJECTED growing the CLI verb
  surface for discoverability -- it names "`seshat --help` lists everything" as the
  rejected Option A trait, and sanctioned exactly ONE deliberate CLI addition
  (`status`, spec 109). Specs 110-113 each ship discoverability as docs/skills with
  "NO new CLI verb". How is this feature surfaced? -> A: As a **read-only companion
  SURFACE (a skill / composer), NOT a new top-level CLI verb.** This keeps the
  ratified Option-B decision intact and matches the 110-113 precedent. The feature
  is the truthful inventory CONTRACT; the surface is the Option-B-compliant form.
  Re-opening the CLI-verb decision would need the same explicit owner ratification
  `status` received and is out of scope here.
- Q: What is the canonical single source of truth for the inventory, given that no
  single committed file today enumerates the full capability surface with the
  required categorical fields, and `state` / `requires-db` / `advisory-vs-gated` /
  `authority` exist nowhere as structured fields (prose only)? -> A: A **new single
  committed capability manifest owns ONLY the fields nothing else records** --
  `state`, `requirements` (db / optional-dependency), and `authority`. Everything
  already structured is REFERENCED from its existing owner, never re-declared: rule
  ids/titles from `docs/rules/rules-manifest.json`, skill names/descriptions from
  `.claude/skills/*/SKILL.md` frontmatter, orchestration verbs + hard-stops from
  `.seshat/kit-source.yaml`, F-numbered ship status from `docs/roadmap/roadmap.md`.
  The manifest is the AUTHORITY for the categorical classification; the feeders are
  the authority for their own structured facts, and the manifest MUST NOT contradict
  them (an independent test, not a `retail check` gate, enforces the 1:1 mapping).

## Why this feature exists

A new user, a maintainer, or an AI agent arriving at Seshat BI cannot answer, in one
read, "what can this kit actually do right now, what needs a database, what is
advisory only, what is a human's decision, and what is deliberately not shipped yet?"
The answer exists, but it is **scattered and partly prose-only**:

- `docs/quality/post-idea-bank-capability-state.md` hand-narrates "Works now / Planned
  / deferred / forbidden / needs-ruling / needs-data" and a "Capability table by
  layer" -- but it is a Markdown snapshot that drifts, not a structured, testable
  contract.
- `README.md`'s "What is built today" table lists ~16 shipped capabilities in prose.
- `docs/architecture/product-modules.md` owns the CATEGORY VOCABULARY (Core Authority
  / Official Workflow Skill / Product Module / Execution Adapter / Maintenance
  Automation, plus an authority matrix and read-only/artifact-writing/execution-capable
  levels) -- but as an author-facing classification contract, not an inventory.
- The genuinely structured facts live in separate golden files: rule ids/titles in
  `docs/rules/rules-manifest.json`; the orchestration verbs + `hard_stops` in
  `.seshat/kit-source.yaml`; F-numbered ship status in `docs/roadmap/roadmap.md`;
  skills as bare `SKILL.md` frontmatter (name + description, no category).

Three fields the brief demands -- `state`, `requirements` (does it need a DB / optional
dependency), and `authority` (is this the agent's to run, or a human's to decide) --
have **no structured home anywhere**; they exist only inside prose sentences.

This feature is the missing single, committed, categorical inventory: one authoritative
manifest that classifies every capability by state / surface / requirements / authority,
rendered as a grouped human reading and a stable machine reading. It re-orders and
re-presents ALREADY-COMMITTED truth; it invents no maturity, computes no readiness,
and touches no project state.

## What this feature is NOT (the scope wall)

The surface's PURPOSE ("tell me what this kit can do") is a truth-claim risk; this wall
is load-bearing. The danger is not a wrong number -- it is a false "this is shipped".

- **It is a READ-ONLY companion surface, NOT a new top-level CLI verb.** Per the
  ratified Option-B decision (`docs/roadmap/decisions/cli-verbs-vs-skill-driven.md`,
  2026-07-07) and the 110-113 packaging precedent. It adds no `seshat capabilities`
  / `retail capabilities` verb to the argparse surface. Re-opening that decision is
  out of scope and would require the owner ratification `status` received.
- **It WRITES NOTHING.** No write path may exist structurally -- grep-verifiable zero
  write calls, matching the shipped read-only surfaces (`approval_inbox`,
  `blocker_explainer`, `pii_notice`, `approver_view`). "Writes nothing" is a
  structural guarantee, not a docstring promise.
- **It connects to NO database and runs NO Power BI.** It reads committed files only.
  No driver import, no DSN resolution, no `pbi`/PBIR execution. It has no live leg,
  so it needs none of the DSN-redaction machinery live commands carry.
- **It emits NO numeric score of any kind** (hard-stop `never_fabricate_a_confidence_score`,
  a.k.a. hard rule #9): no maturity level, no confidence, no completeness percentage,
  no health score, no "N of M shipped" tally used as a ranking. Capabilities are
  classified and listed; never scored or ranked by a computed number.
- **It computes, grants, and changes NO readiness.** It reads no per-table
  `readiness-status.yaml`, moves no stage, records no approval. `retail check` remains
  the governance-gate authority; `seshat status` remains the readiness-state
  projection; `seshat next` remains the next-allowed-action authority; `seshat doctor`
  remains the repository-drift diagnostician. This surface answers a DIFFERENT
  question ("what can the kit do") and defers to those four for their questions.
- **It adds NO gate.** No new `retail check` rule, no `blocking_reasons[]` entry, no
  stage dependency. Its presence/absence is never a gate requirement, and staleness
  detection is a TEST (an independent oracle), not a build-blocking rule -- adding a
  rule here would violate the non-goals and duplicate what a test already proves.
- **It infers NO capability from mere file existence.** A capability appears in the
  inventory ONLY because the committed manifest declares it. A stray `SKILL.md` or a
  half-built module on disk that the manifest does not list is NOT a capability; a
  manifest entry whose referenced source is missing is a contradiction the test
  catches, not a silent capability.
- **It NEVER describes draft or locally-verified work as publicly released.** The
  provenance/release distinction (e.g. a plugin that is "locally verified" vs
  "publicly released") is a distinct field the manifest records explicitly; the
  surface echoes it verbatim and never upgrades it.
- **It is generic (Principle VII).** Over committed metadata; no hardcoded table
  names, no client-specific (C086/`retail_store_sales`) assumptions. The inventory
  is about the KIT's capabilities, not any one onboarded table.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A new user sees what works without a database (Priority: P1)

A newcomer runs the inventory and reads, grouped by state, the capabilities usable
right now with no database and no optional dependency -- separated clearly from the
ones that require a configured database or an optional extra. They can start using the
"available now" set immediately and know exactly which items they cannot yet reach.

**Why this priority**: This is the feature -- one truthful, grouped read of what the
kit can do. Without it there is no MVP.

**Independent Test**: Run the inventory with no database configured and no optional
extras installed; confirm that -- APPLYING THE FIXED GROUP PRECEDENCE (Deferred >
Human-gated > Requires-DB/extra > Agent-companion > Available-now) -- the "Available now"
group lists only shipped, agent-runnable capabilities whose manifest `requirements` are
empty, and that "Requires database or optional dependency" lists exactly the shipped,
agent-runnable capabilities WITH a recorded DB/extra requirement (a deferred or
human-gated capability that also needs a DB is placed by precedence in its higher-ranked
group, not here). No capability appears in two groups, and no numeric score appears
anywhere.

**Acceptance Scenarios**:

1. **Given** the committed capability manifest, **When** the inventory is composed in
   its default human-readable form, **Then** capabilities are grouped under clear
   categorical headings (Available now; Requires database or optional dependency;
   Agent / companion; Human-gated; Deferred / not shipped), each item shows its
   canonical command-or-documentation entry point, and the grouping is deterministic
   (stable order across runs).
2. **Given** a SHIPPED, agent-runnable capability whose manifest `requirements` records
   a database or an optional dependency, **When** the inventory is composed, **Then** it
   appears under "Requires database or optional dependency" and NOT under "Available now",
   and the requirement is shown verbatim from the manifest. (A capability that is
   ALSO deferred or human-gated is placed by the fixed precedence in its higher-ranked
   group; the requirement still shows in its record.)
3. **Given** any capability, **When** the inventory is composed, **Then** no numeric
   maturity, confidence, completeness, or health value is emitted for it.

---

### User Story 2 - An agent requests the machine-readable form and routes correctly (Priority: P1)

An AI agent requests the stable machine-readable output, receives a deterministic
record per capability with explicit categorical fields, and routes the user to the
correct entry point for a chosen capability -- without guessing from prose.

**Why this priority**: The machine form is what makes the inventory usable by the
agent that drives this kit; it is co-equal with the human read.

**Independent Test**: Request the machine-readable form twice on the same committed
inputs; confirm byte-identical output, a schema-conformant record per capability with
the categorical fields present, and that the entry-point field for a shipped
capability resolves to a real committed command or doc.

**Acceptance Scenarios**:

1. **Given** the committed manifest, **When** the machine-readable form is requested,
   **Then** each record carries explicit categorical fields (identity, human name,
   summary, `state`, `surface`, entry-point command, documentation pointer,
   `requirements`, `readiness_stage`, `authority`) and the output is deterministic
   (byte-identical on repeated runs over unchanged inputs).
2. **Given** a shipped capability's record, **When** an agent reads its entry-point
   field, **Then** it points at a real committed command or documentation location
   (verified to exist), so the agent can route without inferring.
3. **Given** the machine-readable form, **When** it is validated against the declared
   schema, **Then** every record conforms and the field set is closed (no undeclared
   fields, no missing required field).

---

### User Story 3 - A user is not misled about human-gated or deferred capabilities (Priority: P1)

A user reads a human-gated capability (e.g. a stage approval) and understands it is a
human's decision the agent will NOT perform automatically; and reads a deferred /
not-shipped capability and understands it is not available today -- neither is
mistaken for an automated, ready-now feature.

**Why this priority**: The whole value is truthfulness. A human-gated action shown as
automated, or a spec-only item shown as shipped, is the exact failure this feature
exists to prevent.

**Independent Test**: For a capability the manifest marks human-gated and one marked
deferred/spec-only, confirm each renders under its own group with wording that names
it human-gated / not-shipped respectively, and that neither appears under "Available
now" nor carries an entry-point implying it runs automatically.

**Acceptance Scenarios**:

1. **Given** a capability whose manifest `authority` is a human decision, **When** the
   inventory is composed, **Then** it appears under "Human-gated", its `authority`
   is shown, and nothing presents it as an automated action.
2. **Given** a capability whose manifest `state` is deferred / spec-only, **When** the
   inventory is composed, **Then** it appears under "Deferred / not shipped", is
   never grouped with shipped capabilities, and its documentation pointer (e.g. its
   spec) is shown.
3. **Given** a capability whose manifest records a provenance/release distinction
   (locally-verified vs publicly-released, e.g. the Claude Code plugin), **When** the
   inventory is composed, **Then** that distinction is shown verbatim and the item is
   never described as publicly released unless the manifest says so.

---

### User Story 4 - A maintainer catches contradictory or stale capability metadata (Priority: P2)

A maintainer renames or removes a capability, or the manifest and a feeder source
disagree. The inventory's own tests fail, surfacing the contradiction, so the
inventory cannot silently drift into a false claim.

**Why this priority**: Discoverability is only valuable if it stays honest under
change; this is what keeps the inventory from becoming a stale, trusted lie.

**Independent Test**: Introduce a manifest entry whose referenced command/skill/rule
does not exist in its feeder source (and, separately, remove a wired capability the
manifest still lists); confirm the inventory's test suite reports the contradiction in
both directions (orphan manifest entry; unlisted real capability).

**Acceptance Scenarios**:

1. **Given** a manifest entry whose referenced feeder fact is absent (a rule id not in
   `rules-manifest.json`, a skill name with no `SKILL.md`, a command not wired),
   **When** the inventory's tests run, **Then** they fail and name the orphaned entry.
2. **Given** a real, wired capability the manifest does NOT list, **When** the
   inventory's tests run, **Then** they fail and name the unlisted capability -- so a
   rename/removal cannot silently make the inventory stale.
3. **Given** the manifest and a feeder disagree on a structured fact (e.g. a rule's
   title), **When** the inventory's tests run, **Then** the disagreement is reported,
   and the manifest never silently overrides the feeder's owned fact.
4. **Given** a capability marked `state: shipped` for which NO committed ship-status
   feeder positively records it as shipped/built (its only evidence is that a spec dir
   or file exists), **When** the inventory's tests run, **Then** they FAIL (fail-closed
   per FR-013(c)) -- "the file exists" is not "it is shipped".
5. **Given** a capability marked `provenance: publicly-released` with no committed
   external-release evidence (e.g. a plugin not present in the tracked tree), **When**
   the inventory's tests run, **Then** they FAIL (fail-closed per FR-013(d)) -- draft or
   locally-verified work can never be rendered as publicly released.

---

### User Story 5 - Existing surfaces are undisturbed and clearly distinguished (Priority: P2)

A user who already relies on `retail check`, `seshat status`, `seshat next`, and
`seshat doctor` sees their behavior unchanged, and reads documentation that explains
how the capability inventory differs from each of them.

**Why this priority**: The inventory must not be confused with, or regress, the four
existing authorities; the distinction must be documented.

**Independent Test**: Run the four existing surfaces before and after this feature and
confirm byte-identical behavior; confirm the documentation states the difference
between capabilities (what the kit can do), status (per-table readiness), next
(next allowed action), doctor (repo drift), and check (governance gate).

**Acceptance Scenarios**:

1. **Given** the four existing authorities, **When** this feature is added, **Then**
   their argparse surface, exit codes, and output are unchanged.
2. **Given** the shipped documentation, **When** a user reads it, **Then** it
   explains, in one place, how the inventory differs from status, next, doctor, and
   check, so no user mistakes one for another.

---

### Edge Cases

- **Empty / minimal manifest** (a drop-in repo the kit was merely downloaded into):
  the inventory renders the categorical groups it can and states plainly where a group
  is empty; it never fabricates entries to fill a group.
- **A manifest entry references a source that is present but the feeder fact is
  absent** (e.g. rule id typo): a contradiction the tests catch (US4), not a silent
  best-guess capability.
- **A capability is both DB-requiring AND human-gated**: the manifest's categorical
  fields are orthogonal; the surface places it deterministically by a documented,
  fixed precedence so it appears in exactly one primary group while its other
  attributes remain visible in its record. No item is silently dropped or duplicated.
- **A deferred item has a spec but no code**: it is listed under "Deferred / not
  shipped" with its spec as the documentation pointer; it is never inferred as shipped
  from the spec file's existence.
- **The provenance field is unset for an item where it matters** (e.g. plugin): the
  surface shows the field as unrecorded rather than assuming "publicly released".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST expose a read-only inventory as a companion SURFACE
  (skill / composer), and MUST NOT add a new top-level CLI verb, honoring the ratified
  Option-B decision (`docs/roadmap/decisions/cli-verbs-vs-skill-driven.md`).
- **FR-002**: The inventory MUST be derived exclusively from committed, reviewable
  project metadata. It MUST NOT treat the BARE existence of a file (an empty or
  frontmatter-less module, a spec dir with no declaring metadata) as evidence of a
  capability. The line is drawn at DECLARED, REVIEWABLE metadata, not at "a file is on
  disk": a committed `SKILL.md` carrying declaring frontmatter (`name` + `description`)
  IS reviewable capability metadata a human authored and committed, and so IS admissible
  positive evidence that the skill-shaped capability exists and is shipped-as-a-skill --
  whereas a directory or module whose presence declares nothing is NOT. (This is the
  same standard FR-013(c) applies: a spec dir's existence is not evidence of shipping,
  but a frontmatter'd `SKILL.md` is a declaration, not an incidental file.) The manifest
  never manufactures a capability from a file that declares nothing about itself.
- **FR-003**: A single committed capability manifest MUST be the canonical authority
  for the inventory's categorical classification. It MUST own only the fields that no
  other committed source records, and MUST reference -- never re-declare -- facts
  already owned by an existing source. Crucially, `state` is NOT wholly unowned: the
  SHIPPED-vs-NOT-SHIPPED axis of `state` is PARTIALLY feeder-owned -- `docs/roadmap/
  roadmap.md` records F-numbered ship status and `docs/quality/status-claims.yaml`
  records `claimed-status: built|planned` (already reconciled against tracked-file
  existence by rule SC1). The manifest MUST therefore reconcile a capability's
  shipped/deferred claim against those feeders where the capability is covered by one,
  and may originate only the finer buckets those feeders do NOT record (advisory vs
  gated, agent/companion, human-gated) and the fields with no feeder at all
  (`requirements`, `authority`, provenance/release). A capability's shipped-ness is a
  checked claim, not a manifest assertion taken on faith.
- **FR-004**: Each capability record MUST carry explicit, categorical fields covering:
  a stable identity; a human-readable name; a short summary; a `state`; a `surface`;
  a canonical entry-point command (when one exists); a documentation pointer; a
  `requirements` classification (e.g. none / database / optional dependency); a
  `readiness_stage` association (or an explicit "not stage-scoped"); and an `authority`
  (agent-runnable vs human-decision). Exact field names are refined in planning, but
  the set MUST remain categorical and closed (no free-form catch-all that defeats
  determinism). NOTE: the seven-stage vocabulary that `readiness_stage` draws from has
  no single canonical committed data file today (it is a hardcoded tuple duplicated
  across `status_surface.py`, `run_next.py`, and `rules/readiness_status.py`); the plan
  MUST pick one canonical source for this field so FR-003's "reference, don't
  re-declare" is not quietly violated for `readiness_stage`.
- **FR-005**: The classification MUST use ORTHOGONAL axes -- a capability is not
  described by one blended label. At minimum:
  (a) a LIFECYCLE axis `state` distinguishing shipped / spec-only / deferred (a
      ship-status fact, feeder-reconciled per FR-003/FR-013);
  (b) an AUTHORITY axis distinguishing agent-runnable / advisory / human-gated (whose
      decision it is), carried by the `authority` field of FR-004, NOT by `state`;
  (c) a REQUIREMENTS axis (none / database / optional dependency), per FR-004; and
  (d) a PROVENANCE / release axis distinguishing at least locally-verified /
      publicly-released / unrecorded.
  `state` MUST NOT absorb authority values (advisory / agent-companion / human-gated)
  or provenance values -- those live on their own fields -- so that a shipped
  human-gated capability is expressible as (`state: shipped`, `authority: human-gated`)
  without the two axes colliding (this is what makes FR-008's single-primary-group
  precedence well-defined). "advisory" and "human-gated" are AUTHORITY values;
  "spec-only"/"deferred" are LIFECYCLE values; "publicly-released" is a PROVENANCE
  value.
- **FR-006**: The default human-readable output MUST group capabilities into clear
  categorical sections -- at least: Available now; Requires database or optional
  dependency; Agent / companion; Human-gated; Deferred / not shipped -- with each item
  showing its canonical command-or-documentation entry point.
- **FR-007**: The feature MUST provide a stable machine-readable output form whose
  records are deterministic (byte-identical over unchanged committed inputs) and
  schema-testable.
- **FR-008**: The inventory MUST classify each capability by its manifest-declared
  fields; it MUST place every listed capability in exactly one primary human-readable
  group by a fixed, documented precedence, with no capability dropped or duplicated.
- **FR-009**: The inventory MUST NOT emit any numeric maturity, confidence,
  completeness, or health score, and MUST NOT rank capabilities by a computed number
  (hard-stop `never_fabricate_a_confidence_score`).
- **FR-010**: The inventory MUST write no files, connect to no database, and execute
  no Power BI. Absence of any write / DB-driver / PBIR-execution path MUST be a
  structural, grep-verifiable guarantee.
- **FR-011**: The inventory MUST compute, grant, or change no readiness: it reads no
  per-table `readiness-status.yaml` for state derivation, moves no stage, and records
  no approval. `retail check`, `seshat status`, `seshat next`, and `seshat doctor`
  remain the sole authorities for governance, readiness state, next action, and repo
  drift respectively.
- **FR-012**: The inventory MUST NOT add a `retail check` rule or any build-blocking
  gate. Its presence/absence MUST never be a gate requirement.
- **FR-013**: Staleness / contradiction detection MUST be enforced by an independent
  TEST oracle -- not a `retail check` rule -- that fails when:
  (a) a manifest entry references a feeder fact that does not exist (orphan -- a rule
      id not in `rules-manifest.json`, a skill name with no `SKILL.md`, a verb not in
      `kit-source.yaml`, a command not wired);
  (b) a real, wired capability of a covered kind is absent from the manifest (unlisted),
      so a rename or removal cannot silently make the inventory stale;
  (c) a `state: shipped` claim is NOT positively backed by a committed ship-status
      feeder. This is FAIL-CLOSED: a capability may be marked `shipped` ONLY when a
      committed feeder POSITIVELY records it as shipped/built (an F-numbered feature
      marked SHIPPED in `docs/roadmap/roadmap.md`; a doc-anchored `claimed-status:
      built` in `docs/quality/status-claims.yaml`; a wired CLI command registered in the
      dispatch table; or, for a skill-shaped capability, a committed `SKILL.md` bearing
      declaring frontmatter (`name` + `description`) -- the skill's declaration IS its
      shipped evidence, per FR-002; a bare directory is not). If NO ship-status feeder
      covers the capability, `state: shipped` MUST fail the oracle --
      "not contradicted" is NOT "confirmed", and reference existence (a spec dir, a
      file on disk) is explicitly NOT positive shipped evidence. A capability with no
      positive shipped evidence MUST be `spec-only` or `deferred`, never `shipped`; AND
  (d) a `provenance: publicly-released` claim is NOT backed by committed external-release
      evidence. This is FAIL-CLOSED identically: `publicly-released` is assertable ONLY
      with committed evidence of the release; absent that, only `locally-verified` or
      `unrecorded` may be recorded. A locally-verified (or non-existent) artifact marked
      `publicly-released` MUST fail the oracle.
  The oracle MUST read its ground truth from the feeder sources, independently of the
  inventory's own rendering code, so it sits ON the truthfulness risk (a false "shipped"
  and a false "publicly-released") rather than adjacent to it. Which committed feeders
  positively enumerate each capability KIND (notably the shipped-skill surface, which
  roadmap F-rows and `status-claims.yaml` do NOT fully cover today) is fixed in the plan;
  the fail-closed REQUIREMENT above does not depend on that enumeration.
- **FR-014**: The manifest MUST NOT contradict a feeder source on a fact that feeder
  owns; where the manifest references such a fact, the test oracle MUST confirm they
  agree, and the feeder remains authoritative.
- **FR-015**: Every displayed capability item -- in both output forms -- MUST be
  traceable to a committed source: its own manifest entry, and (for referenced facts)
  the feeder that owns them. No item may originate from uncommitted or inferred state.
- **FR-016**: The feature MUST leave the behavior of every existing command and surface
  unchanged (argparse surface, exit codes, output).
- **FR-017**: Documentation MUST explain, in one place, how the capability inventory
  differs from `seshat status` (per-table readiness), `seshat next` (next allowed
  action), `seshat doctor` (repo drift), and `retail check` (governance gate).
- **FR-018**: The inventory MUST be generic (Principle VII): no hardcoded onboarded-
  table names and no client-specific assumptions; it inventories the KIT's
  capabilities.
- **FR-019**: Human-readable output MUST be ASCII-only, UTF-8 without BOM (matching the
  repo's established output convention for read-only surfaces), using `--` and `->`
  rather than Unicode dashes/arrows.
- **FR-020**: Where a required categorical field is genuinely unrecorded for a
  capability, the surface MUST show it as explicitly unrecorded (a GAP marker) rather
  than guessing a default. Consistent with FR-013's fail-closed rule, the SAFE default
  for an unbacked lifecycle claim is `spec-only`/`deferred` (never `shipped`), and for
  an unbacked provenance claim is `unrecorded`/`locally-verified` (never
  `publicly-released`). The surface MUST NOT round an unrecorded field UP toward a
  stronger claim.

### Key Entities

- **Capability**: one thing the kit can do (a shipped command/skill, an advisory
  companion, a human-gated action, an adapter, a deferred roadmap item). Attributes:
  identity, name, summary, state, surface, entry-point command, documentation pointer,
  requirements, readiness-stage association, authority, provenance/release.
- **Capability manifest**: the single committed file that is the canonical authority
  for the categorical classification of every capability; owns the fields no feeder
  records; references (does not copy) feeder-owned facts.
- **Feeder source**: an existing committed source authoritative for a slice of
  structured fact the manifest references -- e.g. the rule-registry golden manifest
  (rule ids/titles), the kit-source charter (orchestration verbs + hard-stops), the
  roadmap (F-numbered ship status), skill frontmatter (skill names/descriptions). The
  feeder remains authoritative for its own facts; the manifest must not contradict it.
- **Inventory rendering**: the two output forms (grouped human read; stable
  machine-readable form) projected deterministically from the manifest + referenced
  feeders. Reads only; produces text, never state.
- **Staleness oracle**: an independent test that reconciles the manifest against the
  feeder sources in both directions (orphan entries; unlisted real capabilities),
  reading ground truth from the feeders, not from the inventory's own code.

### Appendix A: Named capabilities the inventory MUST account for

The brief named specific capabilities the inventory must classify. This appendix fixes
the EXPECTED classification for each so the taxonomy is demonstrated against real cases,
not only defined abstractly. It is a conformance target for the taxonomy, not an
implementation list; the manifest MUST place each of these consistently with the state
recorded by its committed feeder (US4 catches a manifest that disagrees).

| Capability | Expected `state` | Expected `surface` | Expected `authority` | Grouping |
|---|---|---|---|---|
| `retail check` | shipped | CLI (existing) | agent-runnable (gate authority) | Available now |
| `retail validate` | shipped | CLI (existing) | agent-runnable | Requires database or optional dependency |
| `retail semantic-check` | shipped | CLI (existing) | agent-runnable | Available now |
| `retail value-check` | shipped | CLI (existing) | agent-runnable | Available now |
| `retail generate` | shipped | CLI (existing) | agent-runnable | Available now |
| `retail / seshat status` | shipped | CLI (existing, the ONE Option-A exception) | agent-runnable | Available now |
| `retail / seshat next` | shipped | CLI (existing) | agent-runnable | Available now |
| `retail / seshat doctor` | shipped | CLI (existing) | agent-runnable | Available now |
| `init-project` | shipped | CLI (existing) | agent-runnable | Available now |
| `scaffold` | shipped | CLI (existing) | agent-runnable | Available now |
| PBIR authoring adapters | shipped (per its own committed status) | CLI (existing pbir-* verbs) | agent-runnable | Available now |
| KPI derivation lineage | per feeder, fail-closed (spec 044 exists but has NO roadmap F-number and NO status-claims entry; the spec dir's existence is NOT shipped evidence -> a committed `SKILL.md` with declaring frontmatter makes it a shipped skill, otherwise spec-only) | companion / docs | advisory | Agent / companion if shipped-as-skill, else Deferred / not shipped |
| cross-table lineage impact | per feeder | companion / skill | advisory | Agent / companion |
| readiness viewer | per feeder | companion / skill | advisory (read-only) | Agent / companion |
| approval console | per feeder | companion / skill | HUMAN-gated (write-back) | Human-gated |
| evidence-pack generator | per feeder | CLI/skill (existing) | agent-runnable | Available now |
| PR readiness reviewer | per feeder | companion / skill | advisory | Agent / companion |
| dbt advisory adapter | shipped (F029 SHIPPED in roadmap.md; `.claude/skills/dbt-transformation-adapter/` present) | advisory skill | advisory (not connected) | Agent / companion |
| Dagster advisory adapter | shipped (F030 SHIPPED in roadmap.md; `.claude/skills/dagster-orchestration-adapter/` present) | advisory skill | advisory (not connected) | Agent / companion |
| Claude Code plugin & commands | per feeder (fail-closed) | plugin | agent-runnable | grouped by lifecycle `state`; **provenance shown verbatim** and fail-closed per FR-013(d): NOT `publicly-released` without committed release evidence -- if no plugin artifact is committed, provenance is `unrecorded`, never `publicly-released` |
| F016 Power BI execution adapter | deferred / not shipped | execution adapter | execution-capable (deferred) | Deferred / not shipped |
| F034 human-built Power BI page | human action (not automated) | human-built artifact | HUMAN | Human-gated |
| spec-only / deferred roadmap items | spec-only / deferred | spec | n/a | Deferred / not shipped |

"per feeder" means the manifest MUST NOT hardcode a state this appendix cannot itself
confirm from a committed source; where the feeder's recorded state differs from a guess
here, the FEEDER wins and US4's oracle enforces it. Per FR-013(c) this is FAIL-CLOSED:
"per feeder" with NO covering ship-status feeder resolves to `spec-only`/`deferred`,
NEVER `shipped`. For an execution adapter, the SHIPPED advisory skill facet and any
DEFERRED connected-execution facet are DISTINCT capabilities: the advisory skill is
shipped (its `SKILL.md`/roadmap F-row is positive evidence) and groups under Agent /
companion; a not-yet-built connected executor is `deferred` and appears (only if a
feeder records it as a planned capability) under Deferred / not shipped -- the two are
never merged into one row with a blended state. The four authorities
(`check`/`status`/`next`/`doctor`) appear as capabilities in the inventory AND retain
their distinct roles per FR-011/FR-017 -- being listed does not make the inventory their
authority.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A newcomer with no database and no optional extras can, from a single
  inventory read, list every capability usable right now and every capability that is
  not yet reachable, with zero items miscategorized between the two.
- **SC-002**: Every capability shown in either output form resolves to a committed
  source (its manifest entry, and for referenced facts the owning feeder); an audit
  finds no displayed item that originates from uncommitted or file-existence-inferred
  state.
- **SC-003**: The machine-readable form is byte-identical across repeated runs over
  unchanged committed inputs, and 100% of its records conform to the declared schema
  with a closed field set.
- **SC-004**: No output of the feature contains a numeric maturity, confidence,
  completeness, or health value, and no capability is ordered by a computed number
  (verifiable by inspection of both forms).
- **SC-005**: Every human-gated capability is shown as a human decision and never as an
  automated action; every deferred / spec-only capability is shown as not-shipped and
  never grouped with shipped capabilities; a capability with a provenance distinction
  is never described as publicly released unless its manifest records that.
- **SC-006**: Introducing an orphan manifest entry, removing a listed real capability,
  marking a spec-only capability `shipped` without positive feeder backing, or marking
  locally-verified work `publicly-released`, each causes the inventory's test suite to
  fail and name the specific discrepancy (fail-closed, both directions).
- **SC-007**: Running `retail check`, `seshat status`, `seshat next`, and
  `seshat doctor` before and after the feature produces byte-identical behavior; the
  feature adds no new `retail check` rule and no gate.
- **SC-008**: A reader of the shipped documentation can state, unaided, how the
  capability inventory differs from status, next, doctor, and check.

## Assumptions

- **Surface = skill/composer, not a CLI verb** (owner decision, Session 2026-07-11).
  The original brief's `seshat capabilities` / `retail capabilities` CLI verb is
  deliberately NOT built, to preserve the ratified Option-B decision. If the owner
  later grants a CLI-verb exception (as `status` received), a thin verb over the same
  manifest could be added under a separate, ratified spec; that is out of scope here.
- **Source of truth = new manifest for the gap fields, reuse for the rest** (owner
  decision, Session 2026-07-11). The manifest owns `state`/`requirements`/`authority`
  (fields with no structured home today) and references rule/skill/verb/roadmap facts
  from their existing owners.
- The category vocabulary reuses `docs/architecture/product-modules.md`'s existing
  classification scheme (Core Authority / Workflow Skill / Product Module / Execution
  Adapter / Maintenance Automation) rather than inventing a parallel taxonomy; the
  display groups (Available now / Requires DB-or-extra / Agent-companion / Human-gated
  / Deferred) map onto it.
- The hand-authored `docs/quality/post-idea-bank-capability-state.md` and README "What
  is built today" table are the prose predecessors this manifest supersedes as the
  structured authority; keeping them honestly in sync with the manifest (or pointing
  them at it) is a follow-up the plan phase will scope, not a silent side effect here.
- No live DB provisioning, no ingestion, no Power BI execution, no orchestrator
  integration is implied (repo YAGNI scope discipline). The seam is the manifest +
  read-only rendering + staleness test; nothing more.
- This spec DEFINES and CHECKS the contract only. It does not implement, does not
  approve, and does not touch `main`. Ratification is a human action at the ratify
  seam; the agent does not self-ratify.

## Ratify ledger

- **Status: RATIFIED.** Approved by the repo owner (Ahmed Shaaban) on 2026-07-11 to
  proceed to implementation. This is a human action recorded by the agent, not a
  self-ratification (Principle V). Scope as specified: read-only capability inventory as
  an Option-B SKILL (no CLI verb); new YAML capability manifest owning the gap fields;
  fail-closed truthfulness oracle as a TEST (no `retail check` gate). The two brief-vs-
  reality decisions (skill-not-verb; manifest-for-state) and all `/speckit-analyze`
  findings (I1 highest) are resolved in this spec + plan + tasks. Build order: implement
  (Sonnet) -> final whole-branch review (Opus) + CodeScene new-code health gate.
