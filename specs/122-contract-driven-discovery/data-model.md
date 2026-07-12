# Phase 1 Data Model: Contract-Driven Discovery-to-Decision Flow

**Feature**: `specs/122-contract-driven-discovery` | **Date**: 2026-07-12

This feature adds exactly ONE new artifact shape (the Layer-A portfolio survey) and
otherwise REUSES existing data models unchanged. Where an entity is reused, this
document points at its shipped shape rather than restating it, and records only the
122-specific constraints. **No new Decision Store status, no new `decision_type`, no
new authority-map row, and no change to the flow-contract schema are introduced.**

---

## Entity 1 (NEW): Portfolio Survey (Layer A)

The single committed, workspace-local artifact surveying all reachable tables of a
source from read-only **metadata only**. It is the `required_outputs` of the existing
`discovery` stage contract, at portfolio scale. Authored from the new
`templates/portfolio-survey.md` blank by the discovery skill. Never authored under
`mappings/<table>/` (that is per-table Layer-B truth).

**Header (per source)**

| Field | Type | Notes |
|-------|------|-------|
| source_kind | enum | `db-schema` \| `csv` \| `excel` \| `file-folder` (R-7; the kinds the existing profilers handle) |
| source_identity | string | schema/folder identity WITHOUT credentials, DSN, or connection string (FR-011) |
| reachable_tables_total | integer | count of tables the survey inventoried |
| coverage_limits | list | ONLY genuinely-unreachable metadata, each with the exact reason (FR-014); empty when all reachable metadata was read; NEVER an agent-chosen cap |
| candidate_domain_evidence | list | survey-level facts that inform the domain proposal (hints, not a ruling) |
| candidate_first_scope_tables | list | tables the survey flags as candidates for the first scope (hints) |
| generated_at | date | ISO date; regeneration reflects drift, never overwrites a committed decision |

**Per-table row (metadata + hints only)**

| Field | Type | Notes |
|-------|------|-------|
| table_id | string | table/relation identity (no credentials) |
| columns | list | column inventory with declared data types |
| declared_pk | list \| null | declared PK columns FROM METADATA where the source exposes them (candidate only) |
| declared_fks | list | declared FK relationships FROM METADATA (candidate only; conflicts noted) |
| candidate_grain | string \| null | inferred from declared PK/metadata -- the contract's "candidate grains" output at the metadata level (NOT a value-backed proof) |
| approx_row_count | integer \| null | approximate/metadata row count/size where safely available; else null with reason |
| date_hints | list | column-name-and-type-based date hints |
| pii_suspicion_hints | list | column-name-and-type-based PII suspicion hints -- HINTS ONLY; no value is sampled at Layer A |
| structural_role_hint | enum \| null | `transaction` \| `snapshot` \| `dimension` \| `reference` \| `technical` \| null (hint) |
| unavailable | list | each unavailable metadata item with its exact reason (`[PENDING LIVE PROFILE]` / `needs_sample` boundary) |

**Invariants (enforced by fixtures; no new `retail check` rule at MVP, R-4)**

- Contains **no value-backed measurement**: no measured uniqueness/nullability, no
  measured missingness (`'' OR NULL`), no measured date coverage, no raw or masked
  value samples, no returns-column population. Those are Layer-B (Entity 2).
- Contains **no raw suspected-PII value, credential, DSN, or connection string**
  (FR-011, Principle IX).
- Inventories **every reachable table** (FR-014); the only omission ever recorded is
  genuinely-unreachable metadata, stated per-table.
- Every entry is an **observation or hint**, never an asserted semantic ruling (FR-010).

## Entity 2 (REUSED, not authored here): Deep Per-Table Profile (Layer B)

Produced by the EXISTING per-table profiler via `retail-onboard-table` / Source Ready
for each in-scope table; committed as the existing `mappings/<table>/source-profile.md`.
Carries the value-backed measures (measured missingness, blank-vs-null, PK
uniqueness/nullability, value-backed grain and relationship/orphan evidence, measured
date coverage, masked samples, returns-column population). **This feature invokes that
profiler; it authors no per-table profile and duplicates none of its shape** (FR-009B/
FR-013, R-2). See `docs/readiness/source-ready.md` and `templates/source-profile.md`.

## Entity 3 (REUSED store record): Domain Proposal

A record in the EXISTING `.seshat/semantic-decisions.yaml`, validated by the EXISTING
DS1-DS5. Shape is `decision-record.schema.json` -- not restated here. 122-specific use:

| Field | 122 constraint |
|-------|----------------|
| decision_type | a **non-critical free-form** token (schema pattern branch), e.g. `domain_classification`; it MUST NOT be a critical enum type and MUST NOT appear in any stage's `blocking_decision_categories` (all three early stages declare `[]`) |
| status (at authoring) | `proposed` (schema requires `confidence` on a proposal) |
| confidence | `low` \| `medium` \| `high` -- the agent's proposal confidence; never approval, never a readiness signal |
| proposed_by | the agent identity (never satisfies approval/confirmation) |
| evidence | cites the survey facts the guess rests on (repo-relative refs; no raw PII) |
| scope | names the affected tables/artifacts (schema `scope_selector`) |

## Entity 4 (REUSED store record): First-Scope Proposal

Same store, same schema, same DS1-DS5. Non-critical free-form `decision_type` (e.g.
`scope_proposal`), authored `proposed` with `confidence`, `proposed_by` = agent, citing
survey + domain evidence. Records candidate tables, candidate questions, candidate KPI
*names* (never defined), explicit exclusions, unresolved dependencies, required owner
decisions. Deterministic bounding (FR-018): honor an explicit user limit; else prefer
one coherent business process / one primary fact grain / KPIs sharing a coherent model
boundary; describe categorically only as **coherent** / **cross-boundary** /
**unresolved** / **needs user input** (descriptive prose, NOT a stored scale) and use
the existing `needs_user_input` status when a human choice is required. No numeric
score, table-count threshold, or fabricated rank.

## Lifecycle (REUSED -- existing statuses/fields only; the batch resting status is NOT re-pinned)

Domain and scope records use ONLY 121's nine statuses and existing fields. There is **no
`confirmed` status** and **no second lifecycle**. Spec 122 introduces no new status and
no new confirmation mechanic.

```text
[agent] proposed (+confidence, proposed_by=agent)
   |
   +-- named human confirms  --> via the existing low-risk BATCH path:
   |                             a batches[] entry (confirmed_by = named human +
   |                             authority class; member carries batch_id).
   |                             Non-critical => NO authority-class eligibility check,
   |                             NO new approval-authority.yaml row.
   |                             [recorded status of the confirmed member follows
   |                              121's existing convention -- NOT pinned here]
   |
   +-- named human rejects   --> status: rejected  (existing terminal "refused")
   |
   +-- changed (new evidence)--> a NEW record supersedes the prior;
   |                             prior -> superseded (superseded_by set)
   |
   +-- partial acceptance    --> a NEW bounded proposed record (accepted subset)
                                 supersedes the original; original -> superseded, so
                                 no two ACTIVE records of the same type share a scope
                                 key (DS4). (FR-019B)
```

**Why the resting status is left to 121's convention (continuity note, do NOT re-pin)**:
the shipped `batch` object has no `evidence_identity`/`reviewed_scope` fields, so whether
a batch-confirmed member rests at `approved` (with its own approval block) or at another
status is **under-determined in what is shipped on `main`**. Resolving it is a latent
spec-121 clarification, not spec-122's. The DS2 fact -- any `approved` record fires the
full approval-completeness requirement regardless of criticality -- is the *reason*
confirmation MUST route through the low-risk batch path rather than a naive status flip;
it is NOT used to pin the outcome. (See spec FR-019 and research R-5; carried identically
here.)

**Gate interaction**: because the domain/scope `decision_type` is in no
`blocking_decision_categories`, these records gate no downstream stage regardless of
status. Sequencing (`no survey -> no domain; no domain -> no scope`) is enforced by the
existing stage contracts' `required_inputs`/`stop_rules`, not by a blocking category.

## Entity 5 (REUSED, act-not-artifact): Handoff Package

The set of inputs presented to the existing Business Knowledge Interview, matching its
declared `required_inputs` exactly. The interview's "a committed discovery profile"
input is satisfied by the Stage-1 per-table (Layer-B) profile of the in-scope tables
(the interview contract names it "Stage-1 read-only profile of `retail-onboard-table`
or equivalent") -- NOT by the Layer-A survey. Not a new artifact; it is the act of
satisfying the interview's existing inputs (spec Key Entities).

## Entity 6 (REUSED projection): Current-Stage / Next-Action (bounded flow)

A read-only projection over the existing `status`/`next`/`blockers` surfaces and the
existing stage contracts, reporting the one next allowed action WITHIN this feature's
bounded flow. Holds no independent state; computes no global all-stage next action and
repairs no general Decision Gate (FR-027, R-6).

---

## Cross-checks

- No new status / `decision_type` enum member / authority-map row / flow-contract field
  is defined. (FR-019, FR-026)
- No entity restates or supersedes `mappings/<table>/source-profile.md`. (FR-013)
- The only new persisted shape is Entity 1 (the portfolio survey), delivered as a
  `templates/` blank + a feature-local schema. (R-8)
