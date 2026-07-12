# Feature Specification: Contract-Driven Discovery-to-Decision Flow

**Feature Branch**: `122-contract-driven-discovery`

**Created**: 2026-07-12

**Status**: Draft

**Input**: User description: "Close the first major product gap between a real multi-table retail data source and governed, human-approved business decisions. Let an agent safely (1) inspect a real database or supported file source read-only; (2) produce a reviewable multi-table discovery profile; (3) propose a retail domain and a bounded first-project scope; (4) hand the grounded discovery evidence into the already-shipped Business Knowledge Interview and Decision Store; (5) use the existing Database-to-PBIP Knowledge Contracts to determine the one next allowed action; (6) stop truthfully whenever required evidence, decisions, or human approvals are missing. Product specification only."

## Overview

### Feature Summary

Spec 121 shipped the **decision foundation** of the Database-to-PBIP flow: the machine-readable Decision Store, the Business Knowledge Interview behavior, the per-stage Knowledge Contracts (`contracts/knowledge/database-to-pbip-flow.yaml`), the approval-authority map, and the pass/warn/blocked gate verdicts. Those contracts already *declare* three early stages — `discovery`, `domain_guess`, `scope_proposal` — each with `required_inputs`, `required_outputs`, stop rules, and a handoff target. But 121 explicitly listed **"Automating discovery, domain guessing, or scope proposal"** as out of scope ("Future Slice 1"). Nothing on `main` today **produces** the artifacts those three contracts promise: there is no multi-table discovery profile, no recorded domain-guess decision, and no recorded scope proposal. The interview therefore has a declared input it cannot yet be fed by the tool.

This feature builds the **behavior** for those already-declared contracts. Given a reachable real retail source, an agent performs read-only discovery, produces one reviewable multi-table discovery profile, proposes a retail domain and a bounded first-delivery scope as **proposed** (not approved) decisions in the existing Decision Store, and hands the grounded evidence into the already-shipped Business Knowledge Interview. At every step the agent consults the existing Knowledge Contracts to determine the single next allowed action, and stops truthfully — naming the concrete missing artifact, decision, or approval — whenever evidence or a human decision is absent. It writes no Silver/Gold SQL, defines no KPI meaning, generates no DAX/PBIP, and grants no approval.

### Problem Statement

A new external user can install the kit and reach the shipped decision layer, but there is no governed on-ramp **into** it from a real, multi-table source. The single-table front door (`retail-onboard-table`) walks *one* `<schema>.<table>` from Source Ready to Mapping Ready; it does not survey a whole database, propose which subject area the data represents, or scope a first delivery slice. Confronted with a source of dozens or hundreds of tables, the agent today has no governed way to answer "what is this, and where do we start?" without inventing meaning. The consequence is either paralysis (the user must read the whole repo and drive table-by-table) or ungoverned guessing (the agent silently decides the domain and scope). This feature closes that gap while preserving every existing gate: discovery is evidence, not meaning; domain and scope are proposals, not approvals; the interview and Decision Store are reused, not reimplemented.

### Product Goal

A BI developer, data analyst, retail operations analyst, consultant, or agent operator can point Seshat BI at a real retail source and receive a **governed, reviewable path from source discovery to recorded business decisions** — a committed multi-table discovery profile, a proposed domain, a proposed first scope, and a clean handoff into the existing interview — **without** the agent inventing meaning, executing transformations, exposing raw PII, bypassing readiness gates, or granting approval. At any point the agent can name exactly one next allowed action from committed evidence and the existing contracts, and it stops truthfully when required evidence, decisions, or approvals are missing.

### Primary Actors

- **BI developer / data analyst** who supplies the source and drives the agent.
- **Data owner / business owner** who confirms business meaning and approves critical decisions (never the agent).
- **Agent operator** using Claude Code, Codex, or another compatible agent (the agent is the runtime; Principle I).
- **Human reviewer / approver** with an eligible authority class per `contracts/knowledge/approval-authority.yaml`.
- **Seshat governance layer** — the readiness spine, the Knowledge Contracts, the Decision Store, and the static gate — which evaluates committed evidence and blocks unsafe progression. It owns pass/block; it never invents answers.

### Relationship to Already-Shipped Capabilities (no-duplicate check)

| Already on `main` (do NOT rebuild) | This feature's relationship |
|---|---|
| `contracts/knowledge/database-to-pbip-flow.yaml` — declares `discovery`/`domain_guess`/`scope_proposal` stages | This feature **produces the `required_outputs`** those contracts already declare; it does not add, reorder, or redefine any stage. |
| Business Knowledge Interview + `contracts/interview/business-knowledge-interview.yaml` (spec 121) | This feature **feeds** the interview its declared `required_inputs` ("a committed discovery profile", "a proposed scope"); it never re-runs or re-implements the interview. |
| The project Decision Store (spec 121) | Domain and scope proposals are **records in the existing store**; this feature adds no second store and no second decision vocabulary. |
| Seven-stage readiness spine + `retail status` / `next` / `blockers` (shipped) | The current-stage / next-action projection is a **view over the existing status/next/blocker surfaces + the contracts**; it is not a new readiness engine or state machine. |
| `retail-onboard-table` (single-table Source→Mapping front door) | This feature is the **multi-table survey that sits before/around it**; it hands each in-scope table to the existing per-table onboarding and does NOT re-implement per-table profiling. |
| Static gate verdicts pass/warn/blocked (spec 121, DS-rules) | Reused as-is for truthful stops; this feature adds no new confidence or readiness score. |

## Clarifications

### Session 2026-07-12

Three product decisions that scoped User Stories 2–4 were resolved by the owner (recommended option in each case):

- Q: How do domain/scope proposals enter the store without a second vocabulary (121 has no `domain_classification`/`scope_proposal` type)? → A: **Non-critical proposals, confirmed inside the interview** — no new critical `decision_type`, no new `approval-authority.yaml` row; 121's vocabulary stays frozen (FR-019).
- Q: What is the delivery surface under the ratified Option-B (skill-driven) direction? → A: **A new dedicated skill**, mirroring how 121 shipped `business-knowledge-interview` (FR-005).
- Q: How does the multi-table profile relate to the existing single-table `source-profile.md`? → A: **Portfolio survey first, then per-table onboarding** — a new portfolio-level survey artifact precedes the existing `retail-onboard-table` per-table profiler (FR-013).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Produce a Reviewable Multi-Table Discovery Profile (Priority: P1) — MVP

A user supplies a reachable database or a supported file source (or a folder of files). The agent performs **read-only** discovery across all reachable tables and produces one committed, reviewable multi-table discovery profile. The profile is *evidence* — measured facts and honestly-marked unknowns — never approved business meaning.

**Why this priority**: The discovery profile is the single input that the domain guess, the scope proposal, and the Business Knowledge Interview all depend on. It is independently valuable (a user gets a legible survey of an unfamiliar source without reading the repo) and independently testable. It is the smallest slice that delivers the feature's core promise, so it is the MVP.

**Independent Test**: Point the flow at a worked-example multi-table source (or a fixture of table/column metadata). Verify a single committed discovery-profile artifact is produced covering every reachable table; that measured facts are recorded and every unmeasurable property is marked with its exact reason; that suspected-PII values are masked; and that no raw PII, credential, DSN, or connection string appears in the committed artifact.

**Acceptance Scenarios**:

1. **Given** a reachable multi-table source, **When** discovery runs read-only, **Then** the committed discovery profile records, per table: source identity (without credentials), table and column inventory, data types, row-count/size observations where measurable, candidate primary keys, candidate table grains, candidate relationships and cardinalities, date columns with observed date coverage, missingness observations, suspected-PII indicators, masked sample evidence where samples are allowed, and — for each unavailable measurement — the exact reason it is unavailable.
2. **Given** a suspected-PII column, **When** sample evidence is shown, **Then** values are masked by default and no raw suspected-PII value is written to the committed artifact.
3. **Given** a source with hundreds of tables, **When** discovery runs, **Then** the profile inventories all reachable tables and, if any coverage limit is applied, the limit and what was omitted are stated explicitly (never a silent truncation presented as complete).
4. **Given** database access is unavailable, an optional reader is missing, or a property is unmeasurable, **When** discovery runs, **Then** the affected observations are marked `[PENDING LIVE PROFILE]` / `needs_sample` with the boundary named and the enabling step stated; the artifact records `warning`/`blocked` semantics as appropriate and never a fabricated value or false pass.
5. **Given** discovery is rerun after new tables or columns appear, **When** the profile regenerates, **Then** newly observed structure is reflected and no previously committed decision is overwritten (drift is surfaced, not silently absorbed).
6. **Given** a candidate primary key that is non-unique or nullable on the observed rows, **When** the profile records it, **Then** it is recorded as a *candidate* with the disqualifying observation (duplicate/null count), never asserted as the key.

---

### User Story 2 - Propose a Retail Domain from Discovery Evidence (Priority: P2)

From the committed discovery evidence, the agent proposes a retail domain or subject area (for example sales, inventory, purchasing, customers, products, or finance). The proposal is recorded as a **proposed** decision in the existing Decision Store, citing the specific profile facts it rests on. The agent never silently approves the classification.

**Why this priority**: The domain guess narrows the interview and the scope proposal, but it depends entirely on User Story 1's profile and can be delivered after it. It is a proposal, so its value is realized only once a human can confirm or supersede it.

**Independent Test**: Run the domain guess against a committed discovery profile fixture. Verify a domain proposal is recorded in the Decision Store with `status: proposed`, cited evidence (the profile facts), and agent confidence kept separate from approval; verify no downstream stage may consume it as approved; verify an ambiguous source yields either an explicitly-uncertain proposal or a recorded "cannot determine domain from available evidence" outcome — never a confident guess dressed as fact.

**Acceptance Scenarios**:

1. **Given** a committed discovery profile, **When** the domain guess runs, **Then** a domain proposal is recorded in the existing Decision Store as a proposed decision citing the profile evidence, and it remains proposed until a named human confirms or supersedes it.
2. **Given** the domain is ambiguous (evidence points to multiple domains or none), **When** the guess runs, **Then** the ambiguity is recorded explicitly (alternatives with their competing evidence, or an honest "undetermined") and no single domain is asserted.
3. **Given** a recorded domain proposal, **When** any consumer reads it, **Then** the agent's confidence value is visible and is never presented as readiness or approval.
4. **Given** no committed discovery profile exists, **When** the domain guess is requested, **Then** the contract's stop rule halts it and names the missing profile as the unblocking artifact.

---

### User Story 3 - Propose a Bounded First-Delivery Scope (Priority: P2)

The agent proposes a bounded first delivery scope: candidate tables, candidate business questions, candidate KPIs (named as candidates only — not defined), explicitly excluded tables or domains, unresolved dependencies, and the decisions required from the owner. The proposal remains **proposed** until a named human confirms or supersedes it.

**Why this priority**: Scope depends on both the profile and the domain guess. A bounded first scope is what makes the subsequent interview focused (fewer rounds than the source column count), but it is a proposal that a human must confirm, so it follows domain guess.

**Independent Test**: Run the scope proposal against a committed profile and a recorded domain proposal. Verify a scope proposal is recorded with candidate tables, candidate questions, candidate KPI *names*, explicit exclusions, unresolved dependencies, and required owner decisions; verify it stays proposed; verify that when the proposed scope is unreasonably large the proposal flags it and recommends a narrower first slice rather than accepting an oversized scope.

**Acceptance Scenarios**:

1. **Given** a committed profile and a recorded domain proposal, **When** the scope proposal runs, **Then** it records candidate tables, candidate business questions, candidate KPI names, explicitly excluded tables/domains, unresolved dependencies, and the decisions the owner must make — all as a proposed decision citing profile + domain evidence.
2. **Given** the proposed scope exceeds a reasonable first delivery slice, **When** the proposal is composed, **Then** the oversize is flagged and a narrower first slice is recommended; the proposal is not silently enlarged.
3. **Given** a candidate KPI appears in scope, **When** it is recorded, **Then** it is named as a *candidate KPI* only; its business meaning is NOT defined here and any meaning question routes to the Retail KPI knowledge boundary.
4. **Given** no recorded domain proposal exists, **When** the scope proposal is requested, **Then** the `scope_proposal` contract's **stop rule / `required_inputs`** halts it and names the missing domain-guess decision. (This sequencing gate is enforced by the stage contract's `required_inputs`/`stop_rules` — NOT by `blocking_decision_categories`; consistent with FR-019, a domain/scope decision_type never sits in a blocking category, yet a missing upstream proposal still halts the next stage via the contract's input requirement.)

---

### User Story 4 - Hand Grounded Discovery into the Business Knowledge Interview (Priority: P3)

The feature passes the committed discovery profile and the proposed scope into the already-shipped Business Knowledge Interview, matching the interview contract's declared `required_inputs`. The existing Decision Store is loaded first; existing decisions are presented for confirmation or supersession, never overwritten. Interview questions are grounded in discovery evidence.

**Why this priority**: The handoff is the value bridge to the shipped decision layer, but it depends on Stories 1–3 producing the inputs the interview requires. It is deliberately a **thin boundary**: this feature *hands off*; the interview (spec 121) *runs*.

**Independent Test**: With a committed profile, a proposed scope, and a seeded Decision Store, invoke the handoff. Verify the exact `required_inputs` declared in `contracts/interview/business-knowledge-interview.yaml` are satisfied ("a committed discovery profile", "a proposed scope", "the existing Decision Store, loaded first"); verify existing decisions are presented for confirmation/supersession and none is overwritten; verify the feature does not itself record interview outcomes, define metric contracts, or grant approvals (those belong to the interview and its downstream).

**Acceptance Scenarios**:

1. **Given** a committed profile, a proposed scope, and an existing Decision Store, **When** the handoff runs, **Then** the interview receives exactly the inputs its contract declares, with the store loaded first, and control passes to the interview (this feature does not re-implement it).
2. **Given** existing Decision Store records for the source, **When** the handoff prepares the interview, **Then** those records are presented for confirmation or supersession and none is silently overwritten.
3. **Given** a suspected-PII column that cannot be sampled safely, **When** the handoff prepares evidence, **Then** the interview's PII stop rule is respected (masked sample or an explicit owner unmasking decision) and no raw value crosses the boundary.
4. **Given** the interview would need a KPI *meaning*, **When** the handoff scopes questions, **Then** meaning questions are marked to route to the Retail KPI knowledge boundary; this feature does not answer them.

---

### User Story 5 - Determine the One Next Allowed Action and Stop Truthfully (Priority: P3)

At any point, the agent consults the existing Knowledge Contracts and committed state to determine the current stage, required inputs, missing evidence, unresolved blocking decisions, the one next allowed action, the forbidden scope, the required human approval, and the required stop point — then performs only that one action and re-evaluates. Every blocked result names the concrete missing artifact/decision/approval and what would unblock it; every pass cites committed evidence.

**Why this priority**: Truthful next-action/stop behavior is what makes the whole flow governed rather than a straight-line script. It projects over everything Stories 1–4 produce, so it is specified last, but it applies throughout.

**Independent Test**: Seed committed states (no profile; profile only; profile + proposed domain; profile + domain + proposed scope; a missing critical decision; an invalid approval) and verify that for each, exactly one next allowed action is derived from the contracts and committed evidence, that a missing critical decision yields a deterministic `blocked` verdict naming it, and that no state infers a pass from absence.

**Acceptance Scenarios**:

1. **Given** any committed state, **When** the next action is computed, **Then** the answer is exactly one allowed action derived from the relevant stage contract and committed evidence — never two, never "proceed generally".
2. **Given** a required critical decision that is completely absent (not merely pending), **When** the dependent stage is evaluated, **Then** the verdict is `blocked` and absence is never interpreted as approval, pass, not-applicable, or low-risk.
3. **Given** a blocked verdict, **When** it is reported, **Then** it names the concrete missing artifact, missing decision, invalid approval, or conflicting evidence, and the action that would unblock it.
4. **Given** a pass verdict, **When** it is reported, **Then** it cites the committed evidence it rests on (a pass with no citable evidence is a defect).
5. **Given** the requested next action would cross into a future out-of-scope capability (KPI contract authoring, Silver/Gold execution, DAX/PBIP generation, dashboard work, publishing), **When** it is evaluated, **Then** the flow stops at the declared handoff boundary and states that the crossing is out of scope for this feature.

### Edge Cases

- **Hundreds of tables**: the profile inventories all reachable tables; any coverage limit is stated with what was omitted (no silent truncation).
- **No obvious fact table**: the profile records the absence as an observation; the domain guess may be low-confidence or undetermined; scope surfaces it as an unresolved dependency — never a fabricated fact table.
- **Multiple tables appear to represent the same business process**: recorded as candidate duplicates/overlaps with the competing evidence; not resolved silently.
- **Candidate relationships conflict or are unprovable**: recorded as *candidate* with the conflict noted; never asserted as a proven relationship.
- **Candidate PK non-unique or nullable**: recorded as a candidate with the disqualifying observation; grain ambiguity is a human seam, not an agent decision (Principle V).
- **Table with no measurable row count (restricted access)**: the measurement is marked unavailable with the exact reason; the table still appears in the inventory.
- **DB access lost after a partial artifact exists**: the partial static evidence is preserved; the missing live portions are marked `[PENDING LIVE PROFILE]`/`blocked` with the boundary named; no false pass.
- **File with unknown encoding/delimiter/header/worksheet**: those are `[PROPOSED]` inferences requiring owner confirmation (consistent with Source Ready RS1); text-column evidence rests on them and is flagged accordingly.
- **Suspected-PII column that cannot be sampled safely**: recorded as `needs_sample`; no raw value; dependent verdicts block truthfully.
- **User refuses to expose samples**: the refusal is honored; affected evidence stays masked/`needs_sample`; nothing is fabricated.
- **Existing Decision Store records conflict with newly discovered evidence**: surfaced as a conflict/stale-evidence condition (per spec 121's staleness rule); not silently reconciled.
- **An approved decision cites evidence that has changed or disappeared**: handled by spec 121's existing stale-evidence behavior (blocked for critical types until re-confirmed); this feature does not weaken it.
- **A critical decision is completely missing (not pending)**: blocks the dependent stage exactly as a pending/invalid decision would (User Story 5, AC-2).
- **User stops discovery or interview partway**: whatever valid evidence exists is preserved; unanswered items stay `pending`/`needs_user_input`; nothing is auto-approved.
- **Feature rerun after new tables/columns appear**: new structure is reflected; committed decisions are not overwritten; drift is surfaced.
- **Domain classification ambiguous**: recorded as ambiguous/undetermined, never a confident single guess.
- **Proposed scope exceeds a reasonable first slice**: flagged with a narrower recommendation (User Story 3, AC-2).
- **Scale-out (big-data) route requested without recorded scale evidence**: refused; consistent with the flow's existing invariant (bigdata requires recorded scale evidence, else the route is python).
- **Requested next action crosses into a future out-of-scope capability**: the flow stops at the handoff boundary and says so (User Story 5, AC-5).

## Requirements *(mandatory)*

### Functional Requirements

#### Governance invariants (reused, not re-created)

- **FR-001**: The feature MUST reuse the existing seven-stage readiness spine and the existing eleven-stage `contracts/knowledge/database-to-pbip-flow.yaml`. It MUST NOT create a second state machine, approval model, decision vocabulary, or readiness score.
- **FR-002**: The feature MUST NOT grant, infer, or fabricate any human approval. Domain and scope outputs are proposals; critical decisions require explicit named-human approval from an authority class eligible for that decision type per `contracts/knowledge/approval-authority.yaml`. An agent identity never satisfies `approved_by` (Principle V).
- **FR-003**: Agent confidence MUST remain separate from approval and MUST NOT be presented as readiness. The feature MUST NOT emit a numeric readiness or confidence score.
- **FR-004**: The existing `status`, `next`, blocker, approval, and evidence surfaces MUST remain projections of committed truth; the feature's current-stage/next-action output is a projection over them and the contracts, not a new engine.
- **FR-005**: Orchestration MUST remain agent-driven and skill-driven. The feature MUST NOT introduce a daemon, scheduler, background runtime, autonomous approval loop, or a broad new CLI command surface. It is delivered as **a new dedicated skill** (consistent with the ratified Option-B direction and mirroring how spec 121 shipped the `business-knowledge-interview` skill); it adds no new CLI verb (Resolved 2026-07-12).
- **FR-006**: The agent MUST perform only the one next allowed action and then re-evaluate committed state.
- **FR-007**: Every blocked result MUST name the concrete missing artifact, missing decision, invalid approval, or conflicting evidence, and the action that would unblock it. Every pass MUST cite committed evidence.

#### Read-only discovery

- **FR-008**: Discovery MUST be read-only. No DDL, DML, schema mutation, ingestion, transformation, warehouse execution, Power BI execution, or publishing is permitted.
- **FR-009**: The multi-table discovery profile MUST cover, per reachable table: source identity (without credentials), table/column inventory, data types, row-count or size observations where measurable, candidate primary keys, candidate table grains, candidate relationships and cardinalities, date columns and observed date coverage, missingness observations, suspected-PII indicators, masked sample evidence where samples are allowed, and for each unavailable measurement the exact reason it is unavailable.
- **FR-010**: Discovery observations are **evidence, not approved business meaning**. The profile MUST NOT assert grain, PK, relationships, PII rulings, or domain as fact; each is recorded as a candidate/observation for human confirmation.
- **FR-011**: Suspected PII MUST be masked by default. Raw suspected-PII values, credentials, secrets, DSNs, and connection strings MUST NEVER be committed to any artifact (Principle IX).
- **FR-012**: When database access, an optional dependency, a source reader, or a measurable property is unavailable, the feature MUST report the unavailable boundary, name what would unblock it, preserve any valid static evidence, use `warning`/`blocked`/`pending`/`needs_sample` semantics as appropriate, never fabricate profile values, and never produce a false pass.
- **FR-013**: The feature MUST NOT re-implement the per-table Source Ready profiler. It MUST reuse the existing read-only profiling mechanics and hand each in-scope table off to the existing single-table onboarding (`retail-onboard-table` / Source Ready) rather than duplicating `mappings/<table>/source-profile.md` authoring. The multi-table profile is a **distinct portfolio-level survey artifact that precedes per-table onboarding** (Resolved 2026-07-12): the survey orients the user across the whole source, and each in-scope table then flows through the existing per-table profiler. The survey MUST NOT restate or supersede per-table `source-profile.md` truth once a table is onboarded.
- **FR-014**: If a coverage limit is applied when discovering a very large source, the limit and the omitted scope MUST be stated explicitly; the feature MUST NOT present a truncated inventory as complete.

#### Domain and scope proposals

- **FR-015**: The domain guess MUST be recorded as a **proposed** decision in the existing Decision Store, citing the specific profile facts it rests on, and MUST remain proposed until a named human confirms or supersedes it.
- **FR-016**: When the domain is ambiguous, the feature MUST record the ambiguity explicitly (competing alternatives with evidence, or an honest "undetermined") and MUST NOT assert a single domain.
- **FR-017**: The first-scope proposal MUST record candidate tables, candidate business questions, candidate KPI *names*, explicitly excluded tables/domains, unresolved dependencies, and the decisions required from the owner — as a **proposed** decision citing profile + domain evidence — and MUST remain proposed until a named human confirms or supersedes it.
- **FR-018**: When the proposed scope exceeds a reasonable first delivery slice, the feature MUST flag the oversize and recommend a narrower first slice; it MUST NOT silently enlarge scope.
- **FR-019**: Domain and scope proposals MUST enter the **existing** Decision Store using the existing decision vocabulary and lifecycle; the feature MUST NOT introduce a parallel store or a second vocabulary. They are recorded as **non-critical proposals confirmed within the interview** (Resolved 2026-07-12): NO new critical `decision_type` is added and NO new row is added to `approval-authority.yaml` — 121's critical-decision vocabulary and authority map stay frozen. This is structurally supported by the existing Decision Store record schema, which already admits **non-critical free-form `decision_type` tokens via its pattern branch** (only critical types are enumerated; only non-critical types may be batch-approved) — so no schema change is required. Two structural constraints keep "non-critical / no new authority row" true and MUST hold:
  - the domain/scope record's `decision_type` MUST NOT appear in any stage's `blocking_decision_categories` (the `discovery`/`domain_guess`/`scope_proposal` stages already declare `blocking_decision_categories: []`), so 121's fail-closed rule for "an unknown type **inside a blocking category**" is never triggered by these records; and
  - confirmation MUST use the interview's low-risk confirmation path and MUST NOT route through the critical-decision approval-metadata gate (the `approved_by` + authority-class eligibility check per `approval-authority.yaml`).
  A domain/scope proposal is a `proposed` record that a named human confirms or supersedes through the existing interview confirmation flow (the same mechanism used for low-risk items), never batch-auto-approved and never self-granted. The critical decisions that DO gate downstream stages (grain, PII, KPI meaning, etc.) remain 121's existing types, unchanged.

#### Handoff to the Business Knowledge Interview

- **FR-020**: The feature MUST hand the committed discovery profile and the proposed scope into the already-shipped Business Knowledge Interview, satisfying exactly the `required_inputs` declared in `contracts/interview/business-knowledge-interview.yaml` ("a committed discovery profile", "a proposed scope", and "the existing Decision Store, loaded first"). It MUST NOT invent inputs the interview does not accept, and MUST NOT re-implement the interview.
- **FR-021**: Interview questions handed off MUST be grounded in discovery evidence. Existing Decision Store decisions MUST be loaded first and presented for confirmation or supersession, never overwritten.
- **FR-022**: The feature MUST NOT itself record interview outcomes, define metric contracts, define KPI meaning, or grant approvals; those are owned by the interview and its downstream. KPI-meaning questions MUST route to the existing Retail KPI knowledge boundary.
- **FR-023**: The feature MUST clearly define and observe the handoff boundary to the later `kpi_contracts` stage: it stops before KPI contract authoring. The interview stage's declared handoff (`kpi_contracts`) is downstream and out of scope for this feature.

#### Missing-input, missing-decision, and truthful stop behavior

- **FR-024**: A required critical decision that is **completely absent** MUST block the dependent stage just as an existing pending or invalid decision would. Absence MUST NEVER be interpreted as approval, pass, not-applicable, or low-risk.
- **FR-025**: Missing, malformed, unreadable, conflicting, stale, or invalid critical decisions MUST block affected downstream stages (fail-closed), consistent with the existing verdict rules (spec 121).
- **FR-026**: Required stage inputs MUST be expressible and evaluable in a machine-readable, fail-closed form, consistent with the existing contract shape (`required_inputs`, `stop_rules`, `blocking_decision_categories`); the feature MUST NOT add a parallel evaluation mechanism.
- **FR-027**: The current-stage and next-action projection MUST derive the current stage, required inputs, missing evidence, unresolved blocking decisions, the one next allowed action, the forbidden scope, the required human approval, and the required stop point from the existing contracts and committed state — introducing no second readiness engine or parallel workflow state.

#### Explicit non-production boundaries

- **FR-028**: The feature MUST NOT write Silver or Gold SQL, MUST NOT define KPI meaning, and MUST NOT generate DAX, metric contracts, dashboard visuals, PBIP artifacts, or Power BI reports.
- **FR-029**: The feature MUST preserve approved decisions as immutable records; any change MUST use supersession (reusing spec 121's supersession behavior, not a new mechanism).
- **FR-030**: A scale-out (big-data) route MUST NOT be selected without recorded evidence that the source exceeds single-node capacity; absent that evidence the route is the single-node (python) path, consistent with the flow's existing boundary invariant.

### Reconciliation Requirements (product-level; resolve, do not expand into unrelated cleanup)

- **RC-1** (`retail-onboard-table`): It is single-table (Source Ready → Mapping Ready). This feature is the multi-table survey around it. The feature MUST NOT re-implement per-table profiling; it composes/aggregates or precedes the existing per-table onboarding (see FR-013 clarification).
- **RC-2** (`retail-orchestrate`): The conductor's older sequence (profile → map → gate → build → validate → Power BI) does not yet express Discovery, Domain Guess, Scope Proposal, Business Knowledge Interview, and KPI Contracts as explicit conductor stages. This feature's stages already exist as *contracts* (`database-to-pbip-flow.yaml`); whether/how the conductor's narrative sequence is updated to name them is a bounded, additive documentation-alignment item to be scoped at plan time (the contracts already exist; the conductor change is additive prose, not a new gate) — it is deliberately NOT raised as a blocking clarification.
- **RC-3** (spine placement): Discovery/Domain/Scope sit in the "Source Ready / Mapping Ready neighborhood" (spec 121's own assumption). Source Ready is per-table and single-table (`docs/readiness/source-ready.md`); this multi-table discovery precedes or wraps it. The feature MUST NOT add an eighth spine stage; the seven stages are unchanged.
- **RC-4** (agent-is-the-runtime): Preserved (Principle I) — the agent performs the flow; no runtime engine is added.
- **RC-5** (existing gates preserved): The source-mapping gate, "no source directly to Silver", "no dashboard before approved metric contracts", and "no Power BI execution before semantic-model readiness and human approval" are all preserved unchanged.
- **RC-6** (approval authority): Every new approval requirement MUST use an existing eligible authority class or explicitly justify a new one. Per the FR-019 resolution, domain/scope proposals are **non-critical** and add NO new critical decision type and NO new `approval-authority.yaml` row — so this feature introduces **no new approval requirement** into the critical-decision authority map; the existing critical decision types and their eligible classes are unchanged.

## Key Entities

- **Multi-Table Discovery Profile**: One committed, reviewable artifact surveying all reachable tables of a source — the `required_outputs` of the `discovery` contract, at portfolio scale. Contains measured facts, candidate structures (PK/grain/relationships), date coverage, missingness, suspected-PII indicators (masked), masked samples where allowed, and explicitly-marked unavailable measurements with reasons. Evidence, never approved meaning.
- **Domain Proposal**: A **proposed** decision in the existing Decision Store naming a candidate retail subject area, citing profile evidence, carrying agent confidence separate from approval, and remaining proposed until a named human confirms/supersedes.
- **First-Scope Proposal**: A **proposed** decision in the existing Decision Store bounding a first delivery slice — candidate tables, candidate questions, candidate KPI names, exclusions, unresolved dependencies, required owner decisions — citing profile + domain evidence, remaining proposed until confirmed/superseded.
- **Handoff Package**: The set of inputs this feature presents to the Business Knowledge Interview, matching the interview contract's declared `required_inputs` exactly (committed profile, proposed scope, existing Decision Store loaded first). Not a new artifact type where the contract already names the inputs; it is the act of satisfying them.
- **Current-Stage / Next-Action Projection**: A read-only view derived from the existing contracts and committed state (over the shipped `status`/`next`/`blockers` surfaces) reporting the current stage, the one next allowed action, blockers, required approval, and the required stop point. Holds no independent state.
- **Blocker Explanation**: The concrete naming of a missing artifact / decision / invalid approval / conflicting evidence and its unblocking action (reuses the existing blocker surface).
- **Evidence & Approval References**: Pointers from proposals/verdicts to the committed profile facts and (for approved decisions) the approval metadata — reusing spec 121's approval-record shape; no new metadata model.

> **Artifact-shape decision (separate artifacts vs one package)**: Per the contract's own `required_outputs`, the discovery profile is **one new artifact** (multi-table); the domain and scope proposals are **records in the existing Decision Store** (not new files); the current-stage/next-action output is a **projection view** (not a stored artifact); blocker/evidence/approval references reuse existing surfaces. This avoids duplicate truth: the profile is the single home for observations, the store is the single home for decisions, and the projection derives everything else. The precise packaging (one profile file vs a small profile-plus-index set) is a plan-time layout choice that does not change this ownership split.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new external user can provide a real multi-table retail source (>= 5 tables) and receive one reviewable discovery package without reading the whole repository — verified by a moderated walkthrough where the user locates every required profile element from the single artifact.
- **SC-002**: For a worked-example source, the produced discovery evidence is sufficient to conduct a focused Business Knowledge Interview with **fewer question rounds than the source column count** (the profile pre-answers the mechanical questions so the interview concentrates on meaning).
- **SC-003**: Domain and scope proposals are clearly distinguished from approved decisions — 100% of seeded proposals read `status: proposed` and none is consumable as approved by any downstream stage.
- **SC-004**: Zero raw suspected-PII values, credentials, secrets, DSNs, or connection strings appear in any committed artifact across all fixtures.
- **SC-005**: A missing critical decision produces a **deterministic `blocked`** verdict naming the decision — 100% of seeded "completely absent" cases block (no false pass, no absence-as-approval).
- **SC-006**: Existing approved decisions are preserved and any change occurs only through supersession — 0 in-place edits or overwrites across rerun fixtures.
- **SC-007**: From any seeded committed state, the agent identifies **exactly one** next allowed action from committed evidence and the contracts (never zero-when-work-remains, never more than one).
- **SC-008**: The workflow stops before KPI contract authoring, warehouse execution, dashboard creation, PBIP generation, and publishing — verified by inspection of delivered artifacts (none produced).
- **SC-009**: The feature duplicates no capability already shipped on `main` — verified against `docs/capabilities/capabilities.yaml` (no discovery/domain/scope producer exists today) and against spec 121 (which declares these stages but scopes their automation out).
- **SC-010**: Every acceptance criterion is observable and testable without relying on subjective confidence or a numeric readiness score.

## MVP Boundary

- **MVP = User Story 1 (P1)**: the read-only multi-table discovery profile. It is the input every later story depends on, it is independently testable, and it delivers standalone value (a legible survey of an unfamiliar source).
- **Later enhancements**: User Story 2 (domain guess) and User Story 3 (scope proposal) at P2; User Story 4 (interview handoff) and User Story 5 (next-action / truthful-stop) at P3. These are separable slices layered on the MVP profile.

## Non-Goals and Out of Scope

- No KPI Contract Elicitation implementation; no expansion of the Retail KPI catalog.
- No Date-Spine, YTD, base-over-base, semi-additive, or value-check expansion.
- No Silver or Gold execution; no new database write adapter.
- No dashboard generation; no Blueprint-to-PBIP compiler; no PBIP prototype generation.
- No F016 Power BI publish or execution adapter.
- No package publication or marketplace release.
- No portfolio-level prioritization or numeric blocker ranking.
- No ML, forecasting, anomaly detection, or universal ERP connectors.
- No broad refactor of existing governance rules.
- No new confidence or readiness scoring system.
- No replacement of the existing Decision Store, Business Knowledge Interview, readiness spine, or source-mapping process.

## Assumptions

- Spec 121 (Business Knowledge Interview, Decision Store, Knowledge Contracts, approval-authority map) is shipped on `main` and is consumed as-is; this feature produces the inputs the already-declared `discovery` / `domain_guess` / `scope_proposal` contracts promise.
- The seven-stage readiness spine and the shipped `status` / `next` / `blockers` surfaces remain the single authority for stage state; this feature's projection reads them, never replaces them.
- Read-only profiling mechanics for DB and file sources already exist (Source Ready) and are reused; this feature does not build new profilers.
- The named-human-plus-authority-class approval convention (`approval-authority.yaml`) applies unchanged; any new authority need is justified against it (RC-6).
- Discovery may run without a live connection: static evidence is preserved and unavailable live measurements are marked truthfully (`needs_sample` / `[PENDING LIVE PROFILE]`), never fabricated.
- The three product decisions that scoped US2–US4 are resolved (see Clarifications, Session 2026-07-12): delivery is a new dedicated skill (FR-005), the profile is a portfolio survey preceding per-table onboarding (FR-013), and domain/scope are non-critical proposals confirmed in the interview with no new decision type (FR-019). Exact artifact paths and file layout remain a plan-time detail that does not change the specified behavior.
- Artifacts are English plain text, UTF-8 without BOM, ASCII arrows (`->`), consistent with the repo (Principle IX).
- Treat KPI Contract Elicitation, Live Proof 2.0, Blueprint-to-PBIP compilation, F016 publishing, and public beta release as future dependent features, not part of this specification.
