# Feature Specification: D-Namespace Disambiguation (ADR defaults -> RC*)

**Feature Branch**: `002-d-namespace-disambiguation` (work proceeds on `main` per repo session convention; feature located via `.specify/feature.json`)

**Created**: 2026-06-24

**Status**: Draft

**Input**: User description: "Disambiguate the D-namespace collision: rename the ADR 0002 retail cleaning/modeling defaults from D1-D16 to RC1-RC16 (Retail Cleaning), leaving the governance checker's TMDL/DAX rule IDs D1-D8 untouched. Docs-only rename; owning artifact is docs/decisions/0002-retail-cleaning-defaults.md. Constitution amendment v1.1.0 -> v1.2.0."

## Why this feature exists

Two unrelated namespaces both use the `D` prefix: the **ADR 0002 retail cleaning/modeling
defaults** (`D1-D16`) and the **governance checker's TMDL/DAX rules** (`D1-D8`). "D7" and
"D8" are ambiguous -- ADR-D8 = returns-flag-from-authoritative-column; checker-D8 =
Power-BI-reads-gold. The kit's own constitution (Principle VI / VIII) and the worked example
flag this collision as deliberately-unresolved, and forbid wiring any ADR default into
`retail check` until it is fixed. This feature fixes it -- the prerequisite that unblocks the
"wire static ADR defaults into the checker" slice.

**Direction (settled, not open):** rename the **ADR** namespace to `RC1-RC16` ("Retail
Cleaning"); leave the **checker** `D1-D8` untouched. Rationale: the checker IDs are in CODE
(`@register("D1"...)` in `src/retail/rules/dax.py`, the test suite, CI output, public
`retail check` finding IDs) -- renaming them is a breaking API change. The ADR IDs are in
DOCS/TEMPLATES only -- renaming them is mechanical and safe. The ADR is literally titled
"retail cleaning," so `RC` fits; the C086 compliance matrix already proposed exactly this.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader can tell the two namespaces apart (Priority: P1)

A reviewer reading any kit doc encounters a `D`-number and must know, without guessing,
whether it means a cleaning default or a checker rule.

**Why this priority**: This IS the feature -- the collision is the problem. Resolving it is
the whole value; everything else is propagation.

**Independent Test**: After the rename, a reviewer reading the ADR, the compliance matrix,
the worked example, and the templates finds every cleaning default written as `RC<n>` and
every checker rule still written as `D<n>`, with no `D`-token whose meaning is ambiguous.

**Acceptance Scenarios**:

1. **Given** `docs/decisions/0002-retail-cleaning-defaults.md`, **When** a reviewer reads it,
   **Then** every default is labeled `RC1`..`RC16` (no bare `D<n>` cleaning labels remain).
2. **Given** a doc that references both namespaces (e.g. the C086 compliance matrix, which
   notes "ADR-D8 vs checker-D8"), **When** a reviewer reads it, **Then** the cleaning sense
   reads `RC8` and the checker sense reads `D8`, and the collision note explains the history.
3. **Given** the governance checker, **When** `retail check` runs, **Then** it still reports
   exactly **23 rules** with the same IDs (S*, D1-D8, R1, C*, G*, P*) -- no checker ID changed.

### User Story 2 - The normative layer stays truthful (Priority: P2)

The constitution and the feature-001 artifacts name both namespaces; after the rename they
must use the new `RC*` labels for cleaning defaults and record the change.

**Why this priority**: A rename that leaves the constitution citing the old labels makes the
normative layer lie. Depends on US1 (the rename) but is a distinct, separately-verifiable slice.

**Independent Test**: A reviewer confirms the constitution (Principles VI/VIII, Sync Impact
Report), the ADR, and the feature-001 docs/templates all use `RC*` for cleaning defaults,
and the constitution is amended to v1.2.0 recording the rename.

**Acceptance Scenarios**:

1. **Given** the constitution, **When** a reviewer reads Principle VI ("Defaults Then
   Deviations") and the D-namespace flag in Principle VIII, **Then** cleaning defaults are
   cited as `RC*` and the surviving `D1-D8` reference is explicitly the checker namespace.
2. **Given** the constitution footer + Sync Impact Report, **When** a reviewer reads them,
   **Then** the version is **v1.2.0** with an amendment record naming the rename and its
   dependent-artifact propagation.

### Edge Cases

- A `D`-token inside a code-fenced example or a checker-rule list MUST NOT be renamed (it is a
  checker reference). Sense-classification is per-occurrence, not a blind replace.
- `docs/superpowers/plans/2026-06-23-pbi-governance-layer.md` and `...-design.md` are the
  CHECKER's own design/plan -- their `D1-D8` are checker rules and MUST stay `D` (the bulk of
  the 393 raw occurrences live here and are NOT in the rename set).
- A range like "D1-D16" becomes "RC1-RC16"; a range "D1-D8" describing checker rules stays.
- Cross-references between docs (e.g. "see RC13") must still resolve after the rename.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST rename the 16 ADR 0002 cleaning/modeling defaults from `D1`..`D16`
  to `RC1`..`RC16` in the owning artifact `docs/decisions/0002-retail-cleaning-defaults.md`,
  preserving each default's meaning and order (RC<n> == old D<n>).
- **FR-002**: The system MUST propagate the `RC*` rename to every doc/template that references
  a cleaning default by number, classifying each `D`-token BY SENSE: cleaning-default ->
  `RC<n>`; checker-rule -> unchanged `D<n>`.
- **FR-003**: The system MUST NOT change any governance checker rule ID. The checker's
  `D1`..`D8` (and S*, R1, C*, G*, P*) in `src/retail/` and tests MUST remain byte-for-byte
  unchanged; no code file is edited by this feature.
- **FR-004**: The system MUST keep the dual-namespace explanation intact (now phrased as
  "ADR cleaning defaults are `RC*`; the checker's `D1-D8` is a separate namespace"), so the
  history of the collision remains legible rather than erased.
- **FR-005**: The system MUST amend the constitution from v1.1.0 to **v1.2.0** (MINOR --
  terminology disambiguation, no principle added/removed/redefined), updating the Sync Impact
  Report and the cleaning-default references in Principles VI and VIII.
- **FR-006**: The system MUST update feature-001 artifacts (architecture doc, spec, plan,
  research, data-model, quickstart, tasks) and the five templates to use `RC*` for cleaning
  defaults, keeping them consistent with the renamed ADR.
- **FR-007**: The rename MUST be verifiable: after it, no `D`-token in a cleaning-default
  SENSE remains anywhere in docs/specs/templates.

### Key Entities

- **Cleaning default (RC<n>)**: one of the 16 retail cleaning/modeling rulings in ADR 0002
  (grain, PII, types, returns, star schema, date dim, reconciliation, ...). Owned by the ADR.
- **Checker rule (D<n>, S*, R1, C*, G*, P*)**: one of the 23 static governance rules in
  `src/retail/`. Owned by code. NOT touched by this feature.
- **D-token occurrence**: a textual reference to a `D`-number in a doc/template, which this
  feature classifies as cleaning-sense (rename) or checker-sense (keep).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After the rename, a token scan finds **zero** cleaning-sense `D<n>` references
  in `docs/`, `specs/`, `.specify/`, `templates/` -- every cleaning default reads `RC<n>`.
- **SC-002**: Every surviving bare `D1`..`D8` in those trees is **provably a checker
  reference** (in a checker-rule list, the checker's own spec/plan, or an explicit
  "checker-D<n>" disambiguation).
- **SC-003**: `retail check` still reports **exactly 23 rules** with unchanged IDs, and the
  **187-test suite stays green** -- proving no checker ID was touched (FR-003).
- **SC-004**: The C086 compliance matrix and worked example still read coherently end to end:
  their per-default structure (now `RC1`..`RC16`) maps 1:1 to the ADR, with no dangling or
  mis-numbered reference.
- **SC-005**: The constitution is at **v1.2.0** with an amendment record, and no kit file
  cites a cleaning default by an old `D<n>` label.
- **SC-006**: `git diff` touches **zero files under `src/` or `tests/`** (docs-only change).

## Assumptions

- **Docs-only rename**: the ADR namespace is referenced only in docs/templates; the checker
  namespace is in code. Verified by token scan (393 raw `D`-occurrences across 19 files; the
  bulk are checker-sense in the governance plan/design docs and stay `D`).
- **`RC` is the chosen prefix** ("Retail Cleaning"), matching the ADR title and the
  compliance matrix's own proposal. Not re-opened.
- **Work proceeds on `main`** per this repo's session convention (commits/pushes to main are
  user-authorized); the feature is located via `.specify/feature.json`, not a git branch.
- **Constitution amendment is in scope** (v1.2.0) because the constitution names both
  namespaces; this is the sanctioned mechanism, not scope creep.
- The "wire static ADR defaults into `retail check`" slice remains **out of scope** -- this
  feature only unblocks it by disambiguating the namespace.

## See also

- Owning artifact: `docs/decisions/0002-retail-cleaning-defaults.md`
- Constitution: `.specify/memory/constitution.md` (Principles VI, VIII; to become v1.2.0)
- Evidence the collision was flagged: `docs/c086-adr0002-compliance.md`,
  `docs/worked-examples/c086-pharmacy.md`, feature-001 `research.md` (Q-1).
- Checker namespace (NOT touched): `src/retail/rules/dax.py`,
  `docs/superpowers/specs/2026-06-23-pbi-governance-layer-design.md`.
