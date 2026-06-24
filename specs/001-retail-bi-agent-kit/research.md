# Phase 0 Research -- Tower BI Agent Kit Foundation (001)

**Plan**: [`plan.md`](./plan.md) | **Date**: 2026-06-24

> This records the design decisions behind the committed deliverables. Because feature 001
> *ratifies* already-shipped work, most "research" is **citation of a settled decision**,
> not a fresh evaluation. The four deferred clarifications are preserved as
> **deferred-by-design** -- this plan MUST NOT resolve them (constitution v1.1.0 parked
> them; the amendment procedure forbids the plan becoming a divergent source of truth).

## Settled decisions (ratified, not re-opened)

### D-001: Depend on `pbi-cli`, do not fork
- **Decision**: consume `pbi-cli` as an external `pipx` dependency; place it as a *later*
  Power BI semantic-model adapter at the bottom of the stack.
- **Rationale**: forking an opinion-less, maximally-capable tool strands the kit on a
  snapshot and turns every upstream upgrade into a merge conflict ("no fork tax").
- **Alternatives rejected**: fork-and-add-opinion (permanent fork tax); make `pbi-cli` the
  core (couples the kit to one engine's lifecycle).
- **Source**: governance spec decision #1; constitution Principle II.

### D-002: Gold-only, Postgres-first medallion (no Parquet-first)
- **Decision**: `bronze -> silver -> gold`; Power BI reads `gold` only; no DuckDB/Parquet
  -first ADR or gold-as-Parquet materialization in the MVP.
- **Rationale**: a single downstream read surface keeps the BI contract narrow; the
  VertiPaq / redundant-second-source-of-truth rationale for rejecting a Parquet copy of
  `gold` lives canonically in **constitution Principle III** (cited, not reproduced here).
- **Alternatives rejected**: Power BI reading `silver`/`bronze` (couples reports to
  ungoverned state); gold-as-Parquet (two columnar copies of one truth).
- **Source**: governance spec decision #3; constitution Principle III; the Parquet question
  was explicitly raised and reversed earlier in the project.

### D-003: Source-mapping gate before silver (the one new idea)
- **Decision**: before any `silver.*` SQL, the source MUST be profiled and mapped into
  committed, reviewed artifacts; silver is downstream of an approved map.
- **Rationale**: writing silver first bakes ungoverned grain/type/PII decisions into a
  table gold's FKs depend on -- reversing them means rebuilding gold and re-publishing the
  cached BI model (effectively irreversible).
- **Reconciliation (not a fork)**: the gate FORMALIZES the medallion playbook's Phase 1 +
  Phase 2.0-2.5/2.7-2.8 + Phase 4 review into committed artifacts. The playbook stays
  authoritative on *how to decide*; the templates on *what to record*. It is NOT a second
  method.
- **Source**: architecture Sec 5; constitution Principle IV; medallion-playbook.md.

### D-004: Agent stops at judgment calls
- **Decision**: the agent MUST NOT decide alone -- and MUST raise an `unresolved-questions`
  entry -- for business-rollup mappings (analyst-supplied, never invented), PII
  publish-safety (governance sign-off), grain ambiguity, sentinel-vs-null, and any
  build-blocking question.
- **Rationale**: an agent-first kit without a stop-and-ask floor silently invents the very
  business/PII/grain decisions the playbook reserves for a human.
- **Source**: constitution Principle V; spec FR-016; `unresolved-questions.md`; playbook
  interaction protocol + Phase 2 decision points. (Added by the v1.0.0 adversarial review,
  Gate 7.)

### D-005: Static-first governance, live deferred
- **Decision**: the shippable gate is the 23-rule static checker (committed text, CI-able,
  no `pbi-cli`/Desktop/network). Live validators (PK uniqueness, date coverage, orphan FKs,
  reconciliation) are deferred to a later `retail validate` surface; this slice documents
  their categories only.
- **Source**: governance spec static surface; constitution Principle VIII; spec FR-005.

### D-006: Spec-Kit initialized (constitution v1.1.0 amendment)
- **Decision**: initialize Spec-Kit into the repo (`specify init --here --integration
  claude --script ps`) to back the spec -> plan -> tasks chain; preserve the hand-authored
  constitution unchanged.
- **Rationale**: the chain framework chosen for Spec 2+; the init is non-destructive to the
  constitution (verified byte-identical to `7a691e0`).
- **Amendment**: v1.0.0 -> v1.1.0 (MINOR, scope expansion) -- the v1.0.0 Scope Boundaries
  said a full init was NOT scaffolded; this is the sanctioned lift.
- **Source**: constitution v1.1.0 Sync Impact Report.

## Deferred by design -- NOT resolved here

These are the four `[NEEDS CLARIFICATION]` items the spec marks open. The plan **records**
them; it does not decide them (constitution amendment procedure clause 4: this layer MUST
NOT become a divergent source of truth).

| ID | Open question | Why deferred | Owner / next step |
|----|---------------|--------------|-------------------|
| Q-1 | **D-namespace collision** -- ADR 0002 (then `D1-D16`) vs checker `D1-D8` | Renaming touches multiple committed artifacts; must be disambiguated *before* wiring any ADR default into `retail check`, not as a side effect of this slice. | **RESOLVED in feature 002** -- ADR renamed to `RC1-RC16`; checker keeps `D1-D8`. (Recorded here as 001's deferral; 001 itself did not do it.) |
| Q-2 | **Per-table mapping-artifact location** -- `mappings/<table>/` vs alongside the migration vs `docs/` | No table has run through the kit yet; deciding the directory before the first real use is premature. | Decide at the first table build; templates currently note links re-point on copy. |
| Q-3 | **Agent orchestration shape** (Layer D) -- which agent/skill drives the playbook and self-heals against the gate | Designed as a seam; the runtime is a later slice and depends on the kit being exercised. | A Layer-D orchestration slice. |
| Q-4 | **`retail validate` live-surface spec** | The live-validator categories are documented (D-005) but their implementation needs its own spec + a live DB harness. | A `retail validate` feature spec. |

**No NEEDS CLARIFICATION remains that blocks Phase 1.** The four above are scoped *out* of
001 on purpose; Phase 1 design proceeds without them.
