# Phase 0 Research: Contract-Driven Discovery-to-Decision Flow

**Feature**: `specs/122-contract-driven-discovery` | **Date**: 2026-07-12

No `NEEDS CLARIFICATION` markers remain in Technical Context (the spec was clarified
across two sessions: the owner scoping decisions and the clarify pass). This document
therefore records the load-bearing **design decisions** -- and, because this feature's
value is in what it does NOT build, an explicit **"why NOT" record** for each boundary
the four spec-review corrections established.

Format per decision: **Decision / Rationale / Alternatives considered**.

---

## R-1: Delivery surface -- a new dedicated agent-conducted skill (no CLI verb, no engine)

- **Decision**: Ship the flow as one new `.claude/skills/retail-discover-portfolio/SKILL.md`
  (working name), mirroring how spec 121 shipped `business-knowledge-interview`. The
  agent is the runtime; the skill sequences Layer-A survey -> domain proposal -> scope
  proposal -> selected-table onboarding -> interview handoff -> stop.
- **Rationale**: FR-005 and the ratified Option-B (skill-driven) direction. Principle I
  (agent-first). A skill adds no daemon/scheduler/loop and no new `retail` subcommand,
  and it is the exact pattern the repo already uses for governed conversational flows.
- **Alternatives considered**: (a) a new `retail discover` CLI verb -- rejected:
  FR-005 forbids a broad new CLI surface, and it would duplicate the kit-router's
  agent-verb model; (b) an orchestration runtime that walks the flow -- rejected:
  Principle I + the parked orchestration-runtime decision (`retail-orchestrate` is a
  procedure the agent performs, not an engine).

## R-2: Two-layer discovery -- Layer A (portfolio metadata survey) vs Layer B (existing per-table profiler)

- **Decision**: Layer A is one new committed artifact authored by the skill from
  read-only **metadata only** (identity, inventory, declared types, declared PK/FK
  metadata, candidate grain from that metadata, approximate/metadata row count,
  name/type-based date & PII *hints*, structural role hints, coverage limits, candidate
  domain/scope evidence). Layer B (value-backed profiling) is **delegated** to the
  existing `retail-onboard-table` / Source Ready profiler, run ONLY for tables selected
  into the proposed scope.
- **Rationale**: FR-009 / FR-009B / FR-013. Resolves the original FR-009-vs-FR-013
  conflict (survey deep-measures every table vs "do not duplicate the per-table
  profiler"). Metadata-only Layer A is inexpensive, so it can cover every reachable
  table (R-3) without a value-backed cost per table.
- **Why NOT a second per-table profiler**: `src/seshat/profile.py` (DB) and
  `file_profile.py` (files) already compute value-backed measures, and
  `mappings/<table>/source-profile.md` is their committed home. Re-implementing any of
  that in the survey would fork per-table truth (violates FR-013 and RC-1). The survey
  therefore records candidate structure as *hints*, never as measured rulings.
- **Alternatives considered**: (a) one deep multi-table profile of every reachable
  table -- rejected: this was the removed inconsistency; it duplicates the per-table
  profiler and makes the MVP unboundedly expensive; (b) Layer A also samples values for
  PII confirmation -- rejected: no value is sampled at Layer A (PII is a name/type hint;
  any masked sample arises only during Layer-B profiling).

## R-2a: Layer-A table enumeration -- agent-issued read-only metadata (no existing schema-lister)

- **Decision**: The reachable-table list for Layer A is produced by an **agent-issued
  read-only metadata read** -- for a DB schema, an `information_schema.tables` query
  over the existing read-only DB access seam (`QueryRunner`/`Dialect`); for a file
  folder, a stdlib directory listing. The agent then records each table's metadata
  (reusing the per-table `information_schema.columns` read that `profile.py`/`dialect.py`
  already expose). If a thin read-only enumeration helper is preferred over an inline
  agent query at implementation time, it targets Python 3.13 and MUST mirror
  `run_validate`'s config-resolve + `_ensure_driver` gate + `dialect.redact(exc, config)`
  so a connection failure never leaks the DSN.
- **Rationale**: A grep of `src/seshat/` confirms the shipped profilers are **per-table**
  -- `profile.py._discover_columns` reads `information_schema.columns` for one given
  `schema.table`, and `dialect.py`'s catalog queries are all `WHERE table_schema = %s AND
  table_name = %s`. There is **no schema-level "list every table" enumerator**. Layer A
  (the MVP) needs exactly that enumeration, so it is a genuinely new operation. Framing
  it as agent-issued metadata reads keeps Principle I (agent-first, the same way
  `retail-onboard-table` *calls* `profile.py` rather than being an engine) without a new
  connector or engine.
- **FR-011 / redaction guarantee**: because Layer A may touch a live DB for metadata,
  the survey MUST NOT contain any DSN, credential, or connection string, and any driver/
  connection error surfaced during enumeration MUST be redacted via the existing
  `dialect.redact()` path -- the same three monkeypatch-testable failure modes the
  validate/profile legs already cover (repo lesson: db-cli-must-mirror-validate-redact).
- **Correcting the earlier "no new source" framing**: an initial draft asserted "no new
  Python source at the MVP." That is not safely true -- schema enumeration does not exist
  today. The plan now states the mechanism explicitly (agent-issued query, or a thin
  redaction-mirroring helper) rather than asserting zero code.
- **Alternatives considered**: (a) reuse `profile.py` to also list tables -- rejected:
  it takes a table as input and profiles values; it is not an enumerator and using it
  would drag in value-backed measurement (violates Layer A metadata-only); (b) a new
  general catalog/inspection engine -- rejected: out of scope; a single read-only
  `information_schema.tables` read (or folder listing) is sufficient.

## R-3: Survey coverage -- inventory every reachable table; never an agent-chosen cap

- **Decision**: The Layer-A survey inventories the metadata of every reachable table
  regardless of source size. The only "coverage limit" ever recorded is metadata that
  is genuinely unreachable (e.g. restricted access), stated per-table with the exact
  reason. No agent-chosen table-count or time-budget cap; no silent truncation.
- **Rationale**: Clarify pass (2026-07-12), FR-014. A metadata survey is cheap, and any
  silent or heuristic cap contradicts the no-silent-truncation invariant and would make
  SC-001 / the "hundreds of tables" edge case non-deterministic.
- **Alternatives considered**: (a) truncate on an explicit user limit only -- folded in
  (an explicit user scope limit still applies at the *scope* step, not as a survey
  truncation); (b) an agent heuristic cap -- rejected by the recommended clarify answer.

## R-4: No new `retail check` rule at MVP (survey-shape enforcement deferred)

- **Decision**: The MVP adds NO new fail-closed static rule family. Domain/scope records
  are validated by the EXISTING DS1-DS5 (they are non-critical records in the existing
  store, which has a real target). Survey-shape enforcement (metadata-only; no
  value-backed measurement; no raw PII) is a spec-level invariant tested by fixtures,
  and any future static rule is deferred until a filled survey instance exists.
- **Rationale**: A new fail-closed rule MUST be `<no-finding>` on `main` to land, and it
  needs a filled target before its shape can be enforced without false positives
  (documented repo lessons: rule-emits-on-main, live-target-before-rule). No filled
  survey exists on `main` yet, so a rule now would either false-positive or be a rule
  with nothing to check. The existing DS-rules already guard the store side.
- **Alternatives considered**: (a) add a "survey shape / no-PII" rule now -- rejected:
  no filled target, emits-on-main risk, and the 9-surface wiring + manifest regen cost
  is unjustified at MVP; (b) rely on `retail check` for domain/scope validity -- already
  true via DS1-DS5, no new rule required. If a future slice authors many surveys, a
  dedicated rule can be added then, acknowledging the emits-on-main + wiring + manifest
  constraints.

## R-5: Domain/scope lifecycle -- reuse the existing store; do not re-pin the batch resting status

- **Decision**: Domain and scope proposals are non-critical free-form `decision_type`
  records in the existing `.seshat/semantic-decisions.yaml`. The agent authors them
  `proposed` (with `confidence`, `proposed_by` = agent). A named human confirms via the
  existing low-risk **batch** path (a `batches[]` entry, `confirmed_by` = named human +
  authority class), rejects (`status: rejected`), or supersedes; partial acceptance is a
  bounded superseding proposal (original -> `superseded`). The **recorded status of a
  batch-confirmed member follows 121's existing convention** and is NOT pinned here.
- **Rationale**: FR-019 / FR-019B. Verified against `decision-record.schema.json`,
  `decision_store.py`, DS1-DS5, the DS3 batch fixtures, and 121's `data-model.md`. Two
  hard facts fix the boundaries: (1) the domain/scope `decision_type` sits in no stage's
  `blocking_decision_categories` (all three stages declare `[]`), so its gate-openness
  halts nothing and 121's "unknown type inside a blocking category" fail-closed rule is
  never triggered; (2) DS2 fires the full approval-completeness requirement for ANY
  `approved` record regardless of criticality -- which is precisely why confirmation must
  route through the low-risk batch path and never a naive status flip.
- **Why NOT pin the resting status to `approved`**: the shipped `batch` object lacks
  `evidence_identity` and `reviewed_scope`, so whether a batch member rests at
  `approved` (with its own approval block) or at another status is **under-determined in
  what is shipped on `main`**. Resolving it is a latent spec-121 clarification, not
  spec-122's job. Pinning it would risk contradicting 121's real usage -- the one thing
  the revision task forbids. data-model.md carries the identical hedge.
- **Alternatives considered**: (a) a new `confirmed` status -- rejected: no such status
  exists; adding one is a second lifecycle (forbidden); (b) a new critical
  `decision_type` + `approval-authority.yaml` row -- rejected: FR-019 freezes 121's
  critical vocabulary and authority map; domain/scope are non-critical.

## R-6: Bounded local-stop routing only -- no global Decision Gate repair

- **Decision**: The skill determines the one next allowed action WITHIN its bounded flow
  (`portfolio discovery -> domain -> scope -> selected-table onboarding -> interview
  handoff -> stop`) using the existing stage contracts and committed state, and stops
  truthfully naming the local missing artifact/decision. It does not extend the general
  cross-stage Decision Gate.
- **Rationale**: FR-024-027 (narrowed). The global work -- all-eleven-stage
  machine-readable `required_inputs`, detecting a specific completely-absent critical
  decision inside a non-empty store, general gate/all-stage next-action -- is the spec's
  explicitly labeled, non-blocking **Future follow-up**, not this feature.
- **Why NOT touch the flow contracts**: the `discovery`/`domain_guess`/`scope_proposal`
  entries already declare their `required_inputs`/`stop_rules`/`blocking_decision_categories`
  in `contracts/knowledge/database-to-pbip-flow.yaml`; FR-026 forbids modifying the
  contract or schema. The feature consumes them unchanged.
- **What is relied on unchanged (corrected after Codex review of `72ab8e4`)**: PR #257
  fails closed for a **malformed/unreadable** store, **invalid approvals**, and
  **conflicting records** (via `_failclosed_verdict` + DS2/DS4). It does **NOT** block an
  **absent or empty** store for the bounded stages: verified in
  `src/seshat/decision_gate.py` -- `_failclosed_verdict` returns None for an absent/empty
  store (no `store.problems`), and `_final_verdict` only emits the not-started blocker
  when the stage declares non-empty `blocking_decision_categories`; `discovery`,
  `domain_guess`, `scope_proposal`, and `business_knowledge_interview` all declare `[]`,
  so the gate returns `pass`. Therefore the feature owns its OWN local stop for an
  absent/empty store / missing local input (FR-024/FR-025); it does NOT rely on the
  inherited gate to block those. An earlier draft (and earlier advisor guidance)
  wrongly claimed the inherited gate blocks an absent/empty store -- corrected here.
  Two out-of-scope future concerns remain: (a) detect one *specific* missing critical
  decision inside a non-empty store; (b) whether the general gate should block
  empty-category stages on an absent store at all.

## R-7: Supported source kinds -- exactly what the reused read-only mechanics handle

- **Decision**: The survey supports a DB schema's tables (existing DB profiler metadata
  read) and standalone file sources -- CSV/Excel and a folder of such files (existing
  file profiler). No new reader, connector, or engine. Engine/reader availability
  follows the shipped optional-extra boundaries (Principle III/VIII); an unavailable
  reader is a truthful `[PENDING LIVE PROFILE]`/`needs_sample` boundary.
- **Rationale**: Clarify pass (2026-07-12), FR-008/FR-012. Reuses `profile.py` /
  `file_profile.py` and the `Dialect` seam already shipped; adds nothing new.
- **Alternatives considered**: universal ERP/SaaS connectors -- rejected (Non-Goals).

## R-8: Survey artifact home & packaging -- workspace-local, single artifact (layout is a plan detail)

- **Decision**: The Layer-A survey is a single committed workspace-local artifact per
  source (one file, or a small survey-plus-index set), authored from the new
  `templates/portfolio-survey.md` blank. It is the `required_outputs` of the `discovery`
  stage at portfolio scale. It is NOT stored under `mappings/<table>/` (that dir is
  per-table Layer-B truth).
- **Rationale**: The spec's "Artifact-shape decision" blockquote fixes the ownership
  split (survey = portfolio metadata home; per-table profiler = value-backed home; store
  = decisions; projection derives the rest). The exact filename/layout is a plan-time
  detail that does not change specified behavior; finalized in data-model.md.
- **Alternatives considered**: appending survey rows into per-table `source-profile.md`
  -- rejected: forks the ownership split and would restate per-table truth (FR-013).

---

## Consolidated decisions (summary)

| # | Decision | Anchor |
|---|----------|--------|
| R-1 | New agent-conducted skill; no CLI verb, no engine | FR-005, Principle I |
| R-2 | Two layers: A = metadata survey; B = existing per-table profiler (in-scope only) | FR-009/009B/013 |
| R-2a | Layer-A enumeration = agent-issued read-only `information_schema.tables` / folder listing; no schema-lister exists today; DSN-redaction mirrors validate | FR-009/011, db-redact lesson |
| R-3 | Inventory every reachable table; no agent cap; only unreachable metadata is a limit | FR-014, clarify |
| R-4 | No new `retail check` rule at MVP; existing DS1-DS5 validate store records | repo rule-landing lessons |
| R-5 | Domain/scope = non-critical store records; batch confirmation; resting status per 121 (not re-pinned) | FR-019/019B |
| R-6 | Bounded local stops only; no global gate repair; contracts consumed unchanged | FR-024-027, FR-026 |
| R-7 | Source kinds = DB tables + CSV/Excel/folder via existing profilers; no new reader | FR-008/012, clarify |
| R-8 | Survey = single workspace-local artifact from a new template; layout is a plan detail | Artifact-shape blockquote |

All Technical Context items are resolved; no open `NEEDS CLARIFICATION`.
