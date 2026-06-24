# Implementation Plan: Tower BI Agent Kit -- Foundation (Phase 0/1)

**Branch**: `001-retail-bi-agent-kit` | **Date**: 2026-06-24 | **Spec**: [`spec.md`](./spec.md)

**Input**: Feature specification from `specs/001-retail-bi-agent-kit/spec.md`

> **Nature of this plan.** Feature 001's deliverables are **already implemented and
> committed** (`7a691e0`: the architecture doc, constitution v1.1.0, this spec, and the
> five mapping-gate templates). This plan therefore (a) documents their design, (b) runs
> the **Constitution Check** against all nine principles, and (c) sets up the forward
> chain. It is a docs-and-methodology foundation, not a software build -- so code-shaped
> sections (Storage, Performance, contracts/) are marked N/A with a reason rather than
> force-fit. Table-building, validators, and the four deferred decisions are out of scope
> (later slices).

## Summary

Ratify the already-shipped retail medallion + governance work as a named, agent-first
product -- the **Tower BI Agent Kit** -- and add one new load-bearing rule: a source MUST
be profiled and mapped into committed, reviewed artifacts **before any `silver.*` SQL is
written** (the source-mapping gate). The technical approach is documentation + generic
templates layered over existing, committed machinery (`retail check`'s 23-rule static
core, the 7-phase medallion playbook, ADR 0002's D1-D16 defaults, the C086 worked
example) -- referenced, never re-implemented or re-decided.

## Technical Context

**Language/Version**: Markdown + YAML (the deliverables). The governance engine the kit
references is Python 3.13, standard-library only (`src/retail/`); the medallion substrate
is PostgreSQL (DigitalOcean).

**Primary Dependencies**: None added by this slice. Referenced (not wired): `retail check`
(stdlib Python), `pbi-cli` (PyPI, via `pipx`, a *later* adapter -- Principle II), Spec-Kit
(`specify` 0.8.10, initialized into the repo at constitution v1.1.0).

**Storage**: N/A for this docs slice. The substrate the kit governs is the Postgres
medallion (`bronze` -> `silver` -> `gold`; Power BI reads `gold` only -- Principle III).
No DB writes in this slice.

**Testing**: N/A as code tests. The quality gate for this slice was a **7-criterion
adversarial review** (Spec-Kit format, terminology consistency, C086 leakage, scope creep,
contradictions, mapping-mandatory, stop-and-ask) plus deterministic checks (ASCII-only,
YAML validity, cross-link existence, principle-renumber consistency). The governance core
it references is itself covered by pytest (`tests/`, 187 tests) -- out of scope here.

**Target Platform**: Windows dev machine (MAX_PATH <= 200 repo-relative, UTF-8 no BOM,
CRLF/LF via `.gitattributes` -- Principle IX); CI runs the static checker OS-independently.

**Project Type**: Documentation / methodology foundation (agent-first BI kit). Not a
library/web-service/app.

**Performance Goals**: N/A (no runtime in this slice). The governance core's relevant
property is "CI-able with no live DB/Desktop/network" -- a static checker, not a perf target.

**Constraints**: Docs/templates only -- no validator scripts, no `pbi-cli` integration, no
CLI installer, no new warehouse tables, no DB writes, no moved docs (constitution Scope
Boundaries). Templates MUST stay generic (no C086 specifics baked in -- Principle VII).

**Scale/Scope**: 8 foundation files (1,861 lines), 5 reusable templates, 1 worked example
cited (C086, 246,916 silver rows). Generalizes to every future retail source table.

## Constitution Check

*GATE: must pass before Phase 0. Re-checked after Phase 1 (below). Source:
`.specify/memory/constitution.md` v1.1.0.*

| # | Principle | This feature's compliance | Status |
|---|-----------|---------------------------|--------|
| I | Agent-First, Gate-Enforced | The kit names the agent as the primary surface (architecture Layer D) and the checker's non-zero exit as the contract. This slice writes the normative layer; it wires no gate. | PASS (by construction) |
| II | Depend, Never Fork | `pbi-cli` is documented as a later adapter, never vendored or wired. Spec-Kit is consumed via `specify init`, not forked. | PASS |
| III | Medallion, Postgres-First, Gold-Only | Architecture + constitution state `bronze->silver->gold`, Power BI reads `gold` only, no Parquet-first ADR. No data touched this slice. | PASS |
| IV | Source Mapping Before Silver | The gate is the feature's core (FR-001, US1); stated as mandatory in architecture Sec 5, constitution IV, spec FR-001. | PASS (this slice defines it) |
| V | Agent Stops at Judgment Calls | Encoded in constitution V + spec FR-016 + `unresolved-questions.md` (the five decision classes, who-must-answer column). | PASS |
| VI | Defaults Then Deviations | `assumptions.md` records D1-D16 adopted-vs-deviated with triggering data fact; references ADR 0002 by path, does not restate. | PASS |
| VII | C086 Is An Example, Not The Schema | Verified: zero pharmacy specifics in template bodies; C086 cited as a filled instance only (SC-002). | PASS |
| VIII | Static-First Governance, Live Deferred | `reconciliation-report.md` documents live-validator categories only; no validator logic written (FR-005). | PASS |
| IX | Secrets and Reproducibility | No secrets in any file; `.env` gitignored; ASCII no-BOM; <=200-char paths; numbered idempotent migrations referenced. | PASS |

**Gate result: PASS (9/9).** No violations -> Complexity Tracking is empty (below). The
plan introduces no new principle conflict; it documents a feature whose deliverables were
authored *to* these principles. This Constitution Check also discharges the
deferred-Constitution-Check note recorded in the spec Assumptions.

## Project Structure

### Documentation (this feature)

```text
specs/001-retail-bi-agent-kit/
|-- spec.md              # Feature spec (committed 7a691e0)
|-- plan.md              # This file (/speckit-plan)
|-- research.md          # Phase 0 -- design decisions + the four deferred items
|-- data-model.md        # Phase 1 -- the five mapping-gate artifacts as a data model
|-- quickstart.md        # Phase 1 -- how a new table flows through the kit
`-- tasks.md             # Phase 2 -- /speckit-tasks output (not created by /speckit-plan)
```

### Source Code (repository root)

This is a docs/methodology foundation; the "source" is the committed kit + the existing
machinery it references. The real tree:

```text
docs/
|-- architecture/tower-bi-agent-kit.md     # the agent-first map (keystone)
|-- medallion-playbook.md                  # the 7-phase method (referenced)
|-- decisions/0002-retail-cleaning-defaults.md   # D1-D16 (referenced)
`-- worked-examples/c086-pharmacy.md        # the first filled instance (cited)

.specify/
|-- memory/constitution.md                 # v1.1.0 -- the normative layer
|-- templates/                             # Spec-Kit canonical templates (from init)
`-- scripts/powershell/                    # spec->plan->tasks driver scripts

specs/001-retail-bi-agent-kit/             # this feature's artifacts (above)

templates/                                 # the 5 generic mapping-gate artifacts:
|-- source-profile.md  source-map.yaml  assumptions.md
|-- unresolved-questions.md  reconciliation-report.md

src/retail/        # the 23-rule static checker (existing; referenced, not changed)
warehouse/         # bronze/silver/gold migrations (existing; no new tables this slice)
```

**Structure Decision**: No new source directories. The feature's deliverables live in
`docs/architecture/`, `.specify/memory/`, `specs/001-retail-bi-agent-kit/`, and
`templates/` -- all created/committed already. `src/retail/` and `warehouse/` are
referenced as the existing machinery the kit governs and are untouched by this slice.

## Phase 0 -> research.md

Records the design decisions behind the committed deliverables and -- critically --
preserves the **four deferred `[NEEDS CLARIFICATION]` items as deferred-by-design** (the
spec and constitution v1.1.0 parked them deliberately; the plan MUST NOT resolve them and
become a divergent source of truth -- constitution amendment procedure clause 4).

## Phase 1 -> data-model.md, quickstart.md, contracts/

- **data-model.md**: the five mapping-gate artifacts as a document/record model (1:1 with
  the templates and the spec's Key Entities; the machine-readable schema is
  `templates/source-map.yaml`).
- **quickstart.md**: the forward-looking artifact -- how a new retail table flows through
  the kit end to end (profile -> map -> review gate -> silver -> gold -> reconciliation).
- **contracts/**: N/A as a separate directory. The five templates **are** the contracts
  (the committed shapes a table's artifacts must satisfy); `templates/source-map.yaml` is
  the machine-readable one. Skipped per the Spec-Kit rule that purely-internal projects
  need no separate contracts dir.

## Complexity Tracking

> Empty -- Constitution Check passed 9/9 with no violations to justify.

## Post-Design Constitution Re-Check

Re-evaluated after Phase 1 artifacts: still **9/9 PASS**. The Phase 1 artifacts
(research/data-model/quickstart) are documentation that *describes* the committed kit;
they add no code, no dependency, no data write, and no resolution of a deferred decision.
No new violation introduced.
