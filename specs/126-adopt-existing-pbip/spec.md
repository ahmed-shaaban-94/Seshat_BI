# Feature Specification: Governed Existing PBIP Adoption

**Feature Branch**: `126-adopt-existing-pbip`

**Created**: 2026-07-14

**Status**: Draft

**Input**: User description: "Use the Spec Kit chain to specify a governed way for Power BI analysts using AI to bring an existing PBIP project into Seshat BI. Inspect the project conservatively, reuse shipped governance and readiness capabilities, never invent meaning or approvals, and return one next allowed action. PBIP is supported in v1; PBIX receives truthful conversion guidance."

## Overview

Seshat BI can initialize a new workspace and can govern committed PBIP, TMDL,
PBIR, metric, mapping, validation, and dashboard artifacts. It does not yet give
an analyst with an existing PBIP project a single governed entry path that says
what is already present, what can count only as candidate evidence, what remains
missing, and what the analyst or agent may do next.

This feature adds that adoption path. It inventories an existing local PBIP
project without changing it, relates observed artifacts to Seshat's seven-stage
readiness spine, and produces a reviewable adoption assessment. Any structural
inference is explicitly proposed; business meaning, mappings, metric contracts,
approvals, validation results, and readiness passes are never inferred. A
separate, explicit adoption step may create only missing Seshat-owned governance
artifacts after the user accepts the assessment. The feature never edits the
adopted PBIP project.

## Clarifications

### Session 2026-07-14

- Q: Should v1 include both the read-only assessment and the explicitly accepted scaffold-writing step? → A: Include both; assessment remains read-only and scaffolding is a separate explicit action.
- Q: Should the assessment persist a report inside the selected project by default? → A: No; return equivalent human-reviewable and agent-readable output without persisting a project file.
- Q: May adoption initialize version control when the selected project is not a repository? → A: No; assessment may proceed, but scaffolding stops until the user initializes version control explicitly.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Assess an Existing PBIP Project (Priority: P1)

A Power BI analyst points Seshat at an existing local PBIP project and receives
a readable assessment of the project artifacts Seshat can observe, candidate
readiness evidence, concrete gaps and blockers, and exactly one next allowed
action. The assessment changes no file in the project.

**Why this priority**: Existing Power BI users need value before they will adopt
a new governance workflow. A truthful, read-only assessment is the smallest safe
slice that connects Seshat's shipped capabilities to their current work.

**Independent Test**: Run the assessment against a supported PBIP fixture that
contains a semantic model, measures, relationships, parameters, report pages,
and visuals but no Seshat governance artifacts. Verify the assessment cites each
observation, distinguishes observations from proposals and missing evidence,
names one next allowed action, and leaves every input byte unchanged.

**Acceptance Scenarios**:

1. **Given** a readable PBIP project with supported semantic-model and report artifacts, **When** the analyst requests adoption assessment, **Then** the result inventories the observable artifacts, states the coverage boundary, cites the local evidence for every observation, and changes no input file.
2. **Given** a PBIP project with no Seshat source profile, source map, metric contracts, or approval records, **When** it is assessed, **Then** those artifacts are reported as missing and no readiness stage is marked `pass` from PBIP structure alone.
3. **Given** an observed relationship, measure, source reference, or report binding that suggests meaning, **When** it is reported, **Then** the structural fact is recorded as observed while any interpretation is marked `proposed` and is never presented as approved business meaning.
4. **Given** an adopted project containing a literal host, connection detail, credential-like value, or suspected sensitive value, **When** the assessment is produced, **Then** the output redacts the value, cites only a safe location or category, and reports the appropriate existing governance blocker.
5. **Given** multiple valid blockers, **When** the assessment completes, **Then** it uses the existing readiness ordering to return exactly one next allowed action at the earliest unresolved stage.
6. **Given** a successful or blocked assessment, **When** its result is returned, **Then** equivalent human-reviewable and agent-readable facts are available without persisting a report inside the selected project.

---

### User Story 2 - Create the Governed Adoption Scaffold (Priority: P2)

After reviewing the assessment, the analyst explicitly accepts creation of the
minimum missing Seshat-owned governance structure. Seshat creates only new
adoption and readiness artifacts, preserves all observed facts as evidence or
proposals, leaves approval slots empty, and does not edit PBIP, TMDL, PBIR, DAX,
SQL, or source data.

**Why this priority**: Assessment proves immediate value, but adoption becomes
durable only when the project has a reviewable Seshat evidence seam. Keeping the
write step explicit protects existing projects and human authority.

**Independent Test**: Apply an accepted assessment to a copy of a PBIP fixture.
Verify only the declared new Seshat-owned files appear, all existing project
files retain their original bytes, every proposal is labeled, approval fields
remain empty, and a rerun refuses or reports collisions rather than overwriting.

**Acceptance Scenarios**:

1. **Given** a completed assessment and explicit user acceptance, **When** the adoption scaffold is created, **Then** only the minimum missing Seshat-owned artifacts are added and their contents trace to the assessment.
2. **Given** no explicit acceptance, **When** the analyst requests assessment, **Then** no scaffold or governance artifact is written.
3. **Given** a target Seshat-owned file already exists, **When** adoption is requested, **Then** the operation fails closed with a collision explanation and does not overwrite or partially write files.
4. **Given** the scaffold contains decisions requiring business or data-owner judgment, **When** it is written, **Then** those decisions remain proposed, unresolved, or blocked with named human roles and empty approval slots.
5. **Given** any existing PBIP, TMDL, PBIR, DAX, SQL, or source file, **When** the scaffold step succeeds or fails, **Then** that file is byte-identical to its pre-adoption state.
6. **Given** a selected project that is not a version-control repository, **When** scaffolding is requested, **Then** scaffolding stops with the explicit initialization prerequisite and does not initialize version control itself.

---

### User Story 3 - Reassess Adoption Progress (Priority: P3)

An analyst reruns the adoption assessment after adding or approving governance
artifacts. Seshat reports what changed, reuses the canonical readiness state,
and returns the new one next allowed action without maintaining a second run
state or silently accepting drift.

**Why this priority**: Repeat assessment turns a one-time intake report into an
ongoing guided adoption journey while preserving the readiness system as the
only state authority.

**Independent Test**: Assess a fixture, add one required evidence artifact, and
assess again. Verify the second result identifies the changed evidence, leaves
unchanged observations stable, recomputes the earliest blocker, and produces no
independent adoption-stage state.

**Acceptance Scenarios**:

1. **Given** unchanged project and governance artifacts, **When** assessment is repeated, **Then** the result is semantically identical apart from explicitly non-authoritative run metadata.
2. **Given** a newly committed valid evidence artifact, **When** assessment is repeated, **Then** the result cites the new evidence and recomputes the next allowed action through the existing readiness rules.
3. **Given** an adopted PBIP artifact changed after the prior assessment, **When** reassessed, **Then** the change is surfaced for review and is not silently treated as approved evidence.
4. **Given** a recorded human approval whose governed input later changes, **When** reassessed, **Then** the existing approval-validity rules determine whether it remains valid; the adoption feature never decides independently.

### Edge Cases

- A `.pbix` binary is supplied instead of a PBIP directory: return a supported
  conversion path and stop; do not parse or modify the binary.
- The directory contains more than one semantic model or more than one report:
  inventory all supported components, state their relationships when explicit,
  and block on ambiguity rather than choosing silently.
- The PBIP references an external or missing semantic model: report the missing
  dependency and stop at the earliest affected readiness stage.
- The PBIP schema or visual type is unsupported: preserve supported observations,
  name the unsupported boundary, and never present partial coverage as complete.
- The project is not under version control: assessment may proceed, but files
  cannot qualify as committed readiness evidence and the next action must state
  the version-control prerequisite.
- The supplied path escapes the selected project root through traversal,
  redirection, or a linked target: refuse that path and write nothing.
- A scan is interrupted or an output target is unavailable: no partial adoption
  scaffold survives; the existing project remains unchanged.
- A PBIP uses a non-gold source or contains an unsafe literal connection value:
  cite the existing governance finding and do not normalize or repair it silently.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept one local PBIP project directory as the bounded assessment target.
- **FR-002**: The system MUST discover supported semantic models, reports, pages, visuals, measures, relationships, parameters, and source references within the selected project boundary.
- **FR-003**: The system MUST record the coverage boundary, including supported, unsupported, unreadable, missing, and ambiguous components.
- **FR-004**: Every reported fact MUST be classified as `observed`, `proposed`, `missing`, `blocked`, or `unavailable_with_reason`.
- **FR-005**: Every `observed` fact MUST cite a project-relative artifact location; every unavailable fact MUST name its reason.
- **FR-006**: The system MUST distinguish structural observations from business meaning and MUST label any interpretation as `proposed`.
- **FR-007**: The system MUST NOT create or approve a source mapping, grain ruling, PII disposition, cleaning rule, metric definition, rollup, sentinel policy, dashboard intent, or business decision from PBIP structure alone.
- **FR-008**: The system MUST NOT grant an approval or mark a readiness stage `pass` solely because an artifact exists or a static check is green.
- **FR-009**: The assessment MUST reuse existing Seshat governance findings and readiness ordering rather than defining a second rule set or adoption state machine.
- **FR-010**: The assessment MUST return exactly one next allowed action, derived from the earliest unresolved readiness stage and its committed evidence.
- **FR-011**: Assessment MUST be read-only and MUST leave all selected-project files byte-identical.
- **FR-012**: Assessment output MUST redact credential-like values, literal connection details, raw data values, and suspected sensitive values.
- **FR-013**: The system MUST report unsafe connection literals, non-gold sourcing, missing relative model references, and other already-governed defects through their existing rule identities where applicable.
- **FR-014**: The assessment MUST operate without opening Power BI Desktop, connecting to the Power BI Service, executing the Power BI adapter, running DAX queries, or connecting to a live database.
- **FR-015**: The system MUST allow the analyst to explicitly accept or decline creation of the adoption scaffold after reviewing the assessment.
- **FR-016**: Without explicit acceptance, the system MUST write no scaffold or governance artifact.
- **FR-017**: With explicit acceptance, the system MUST create only missing Seshat-owned adoption and governance artifacts declared in the assessment.
- **FR-018**: The scaffold MUST preserve observed facts as cited evidence, preserve interpretations as proposals, leave approval slots empty, and record concrete blockers.
- **FR-019**: The scaffold step MUST NOT modify, replace, reformat, or delete any existing PBIP, TMDL, PBIR, DAX, SQL, source, mapping, metric, decision, approval, or readiness artifact.
- **FR-020**: If any target file already exists or any planned write is unsafe, the scaffold step MUST fail before writing and MUST identify the collision or unsafe target.
- **FR-021**: Repeated assessment over identical authoritative inputs MUST produce the same substantive observations, classifications, blockers, and next action.
- **FR-022**: Reassessment MUST surface changed PBIP or governance evidence and MUST defer approval validity and readiness changes to existing Seshat predicates.
- **FR-023**: The system MUST NOT parse, extract, convert, or modify `.pbix` binaries in v1; it MUST return truthful PBIP conversion guidance and stop.
- **FR-024**: The system MUST refuse any input or output path that resolves outside the selected project root.
- **FR-025**: The system MUST never emit a readiness, quality, safety, or adoption score.
- **FR-026**: The system MUST degrade gracefully when optional readers, expected artifacts, or supported schema versions are unavailable, naming the boundary and an enabling action without a traceback.
- **FR-027**: Assessment and scaffold results MUST be available in a human-reviewable form and a stable agent-readable form with equivalent substantive facts.
- **FR-028**: The feature MUST compose shipped PBIP readers, governance checks, readiness projections, blocker explanations, and next-action logic; it MUST NOT duplicate their authoritative decisions.
- **FR-029**: Assessment MUST NOT persist an assessment report or other project file by default; its human-reviewable and agent-readable forms MUST be returned without changing the selected project.
- **FR-030**: Assessment MAY inspect a project outside version control, but scaffold creation MUST require an existing version-control repository and MUST NOT initialize one implicitly.

### Key Entities

- **Adoption Target**: The bounded local PBIP project selected by the analyst; identified by a safe project-relative identity and its supported components.
- **Adoption Assessment**: A read-only, reviewable account of scan coverage, observed artifacts, candidate evidence, gaps, blockers, and the one next allowed action.
- **Adoption Observation**: One cited fact classified as observed, proposed, missing, blocked, or unavailable with a reason; it carries no approval authority.
- **Adoption Scaffold Plan**: The exact set of new Seshat-owned files that may be created after explicit acceptance, including collision and safety preconditions.
- **Adoption Change**: A reassessment observation that identifies an added, removed, or changed authoritative input without independently changing readiness or approval state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time analyst can obtain a complete adoption assessment and one next allowed action from a supported existing PBIP project in under five minutes without reading the repository documentation first.
- **SC-002**: In the reference suite, 100% of reported observations cite a project-relative artifact or state an explicit unavailability reason.
- **SC-003**: Across success, warning, blocked, unsupported, and interrupted assessment scenarios, 100% of existing project files remain byte-identical.
- **SC-004**: Across synthetic fixtures containing credential-like and sensitive values, no prohibited value appears in human-reviewable or agent-readable output.
- **SC-005**: Every assessed scenario returns exactly one next allowed action or one terminal supported stop with its concrete reason; none returns competing next actions.
- **SC-006**: Identical authoritative inputs produce substantively identical assessment outputs across repeated runs.
- **SC-007**: In scaffold tests, 100% of planned writes are declared before acceptance, no write occurs before acceptance, and any collision leaves zero partial new files.
- **SC-008**: No reference scenario gains a readiness pass, approved decision, metric definition, or source mapping solely from adoption assessment or scaffold creation.
- **SC-009**: Unsupported `.pbix`, PBIP schema, missing-model, multi-model, and out-of-root-path scenarios end with a concise supported boundary and no unhandled failure.
- **SC-010**: Human-reviewable and agent-readable outputs agree on all observations, classifications, blockers, evidence references, and the next allowed action in the reference suite.

## Assumptions

- The primary user is a Power BI analyst or BI developer using an AI coding
  agent and holding local access to a PBIP project.
- PBIP, TMDL, and PBIR text artifacts are the only Power BI project inputs in
  v1. Binary `.pbix` support is limited to conversion guidance.
- Existing Seshat parsers, check rules, readiness projections, and approval
  predicates remain authoritative and are reused without semantic changes.
- Assessment can inspect a project that is not yet under version control, but
  uncommitted files cannot become readiness evidence.
- A typical first-success project contains no more than five reports, five
  semantic models, 500 measures, and 100 report pages. Larger projects must be
  inventoried without silent truncation and may report an explicit coverage or
  performance boundary.
- Adoption scaffolding is a separate explicit action after assessment; it never
  occurs implicitly.

## Out of Scope

- Parsing, extracting, converting, or repairing `.pbix` binaries.
- Publishing to or mutating Power BI Desktop, Fabric, or the Power BI Service.
- Connecting to a live database, profiling source values, or running live DAX.
- Editing or regenerating existing PBIP, TMDL, PBIR, DAX, SQL, source, mapping,
  metric, decision, approval, or readiness artifacts.
- Inferring business meaning, approving mappings or metrics, or granting a
  readiness stage.
- Creating a numeric readiness, quality, safety, or adoption score.
- Replacing the existing seven-stage readiness system with an adoption-specific
  workflow or run-state engine.
