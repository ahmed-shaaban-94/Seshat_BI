# Tower BI Agent Kit -- Roadmap

- **Status:** Active planning (docs/planning only; no runtime code in this doc).
- **Product identity:** **Tower BI Agent Kit** is the product. The **Tower BI
  Readiness System** is the operating spine inside it.
- **Read first:** `docs/readiness/readiness-model.md` (the spine),
  `docs/architecture/readiness-pipeline.md` (how it sits on the existing kit).

> The kit already ships an agent-first constitution, a source-mapping gate, the
> Spec-Kit foundation, the C086 worked example, a 27-rule static `retail check`,
> and a `retail validate` live surface. This roadmap reconciles that foundation
> (feature 001-004 + the orchestration/builder slices) with the readiness
> direction: every future feature advances one **readiness stage**.

## What the readiness spine answers

For every source / table / report, the spine must answer -- with **evidence and
blockers, never a hallucinated confidence score**:

| Question | Where it is answered |
|----------|----------------------|
| Where are we now? | `current_stage` in the readiness status |
| What artifacts exist? | `evidence[]` (committed files) |
| What checks passed? | stage `checks` + `retail check` / `retail validate` exit codes |
| What blockers remain? | `blocking_reasons[]` |
| Who must approve? | `approvals[]` (named owner) |
| What is the next allowed action? | `next_action` (one step) |

## Core readiness stages

The seven stages the spine tracks (detail per stage under `docs/readiness/`):

| # | Stage | Gate it enforces |
|---|-------|------------------|
| 1 | **Source Ready** | a profiled, understood source exists |
| 2 | **Mapping Ready** | grain/PK/PII/placement mapped + reviewed (the source-mapping gate) |
| 3 | **Silver Ready** | typed/cleaned silver built + statically clean |
| 4 | **Gold Ready** | Kimball star built + live-validated (PK/coverage/orphans/reconcile) |
| 5 | **Semantic Model Ready** | metric contracts + governed PBIP model |
| 6 | **Dashboard Ready** | report designed against approved metric contracts |
| 7 | **Publish Ready** | handoff pack complete; approved to publish |

No stage is entered before the prior stage is `pass`. The hard rules below make
the ordering non-negotiable.

## Six product layers

The kit's surfaces, top (what the user touches) to bottom (later adapter):

| Layer | Name | What it is | Status |
|-------|------|------------|--------|
| 1 | **Agent Experience** | the agent + skills are the interface; CLI is a gate it calls | shipped (conductor + verbs) |
| 2 | **Source Intelligence** | profile, business meaning, Arabic retail dictionary | next (F006-F007) |
| 3 | **Mapping Governance** | the source-mapping gate, grain confidence, mapping diff | shipped gate; F008 deepens |
| 4 | **Validation & Readiness** | `retail check` / `retail validate` + the readiness spine | shipped checks; F005 spine |
| 5 | **Metrics & Semantic Model** | metric contracts, KPI packs, governed PBIP model | F009-F010 |
| 6 | **Dashboard & Delivery** | dashboard design, QC room, handoff pack, publish | F011-F016 (gated, later) |

## Feature sequence

Each feature advances a readiness stage. **Feature 005 is the next executable
slice.** Dashboard and pbi-cli/PBIP work are explicitly **later and gated**.

### Now

| Feature | Name | Layer | Advances stage | One-line scope |
|---------|------|-------|----------------|----------------|
| **005** | Retail Readiness Model | 4 | the spine itself (all stages) | the readiness state model + status template + per-stage docs (this slice's home) |
| **006** | Table Onboarding Wizard | 1-2 | Source -> Mapping | an agent workflow that walks a new table through profile -> map -> gate |
| **007** | Business Meaning Registry + Arabic Retail Dictionary | 2 | Source Ready | a generic registry of business terms + an Arabic<->English retail term dictionary (generic, not C086 values) |

### Next

| Feature | Name | Layer | Advances stage | One-line scope |
|---------|------|-------|----------------|----------------|
| **008** | Grain Confidence + Mapping Diff Reviewer | 3 | Mapping Ready | surface grain-uniqueness confidence + a reviewable diff between mapping versions |
| **009** | Metric Contract Store + Retail KPI Packs | 5 | Semantic Model Ready | a store of metric definitions (name, grain, formula intent, owner) + generic retail KPI packs |
| **010** | Semantic Model Readiness | 5 | Semantic Model Ready | readiness checks for the PBIP model (relationships, date table, measures bind to contracts) |

### Then

| Feature | Name | Layer | Advances stage | One-line scope |
|---------|------|-------|----------------|----------------|
| **011** | Power BI Dashboard Design Skill | 6 | Dashboard Ready | an agent skill that designs a dashboard FROM approved metric contracts (no contracts -> no design) |
| **012** | Data Quality Control Room | 4 | all stages | a consolidated view of data-quality findings + blockers across tables |
| **013** | BI Handoff Pack | 6 | Publish Ready | the documentation/evidence bundle handed to a BI consumer |

### Later

| Feature | Name | Layer | Advances stage | One-line scope |
|---------|------|-------|----------------|----------------|
| **014** | Source Drift Detector | 2 | Source Ready | detect when a source's shape/semantics drift from its profile |
| **015** | Reconciliation Ledger | 4 | Gold Ready | a durable ledger of cross-layer reconciliation results over time |
| **016** | pbi-cli / PBIP Adapter | 6 | Dashboard/Publish | the deferred Power BI authoring engine -- LAST, gated on semantic-model readiness |

## Hard design rules (non-negotiable, gate the sequence)

These are the ordering constraints the roadmap encodes. They reinforce the
existing constitution (Principles I, IV, V, VIII), they do not replace it:

1. **Agent-first, not CLI-first.** The agent is the interface; `retail check` /
   `retail validate` are gates/helpers the agent calls.
2. **No source goes directly to silver.** Mapping Ready must `pass` first.
3. **No silver without** a source profile + source map + declared grain +
   reviewed/accepted unresolved questions.
4. **No gold to Power BI before validation.** Gold Ready requires the live checks.
5. **No dashboard design before metric contracts.** F011 is gated on F009/F010.
6. **No pbi-cli / PBIP automation before semantic-model readiness.** F016 is last.
7. **C086 is the first worked example, not the universal schema.** Generic
   templates carry no pharmacy specifics.
8. **Docs/templates/checklists first; automate only after artifacts prove
   useful.** A readiness stage is a doc + a status entry before it is code.
9. **No fake confidence.** Readiness is explicit `status` + `evidence` +
   `blocking_reasons`. Numeric scores are optional/deferred until scoring rules
   are defined (`docs/readiness/readiness-model.md`).

## What is intentionally out of scope (this roadmap slice)

- No runtime code, new validators, dashboard generation, pbi-cli publishing,
  Fabric deployment, ML, forecasting, a universal ERP connector, or fully
  automated mapping approval.
- This is a planning update: it sequences the work and defines the readiness
  stages as docs/templates. Each feature above gets its own spec before code.

## See also

- The spine: `docs/readiness/readiness-model.md`, `readiness-pipeline.md`,
  and the seven `docs/readiness/<stage>-ready.md` stage docs.
- Architecture: `docs/architecture/readiness-pipeline.md` (spine on the kit),
  `docs/architecture/tower-bi-agent-kit.md` (the kit).
- Foundation: `.specify/memory/constitution.md`, `specs/001-retail-bi-agent-kit/`,
  `docs/medallion-playbook.md`, `docs/worked-examples/c086-pharmacy.md`.
