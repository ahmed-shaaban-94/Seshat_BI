# Implementation Plan: Contract-Driven Discovery-to-Decision Flow

**Branch**: `122-contract-driven-discovery` | **Date**: 2026-07-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/122-contract-driven-discovery/spec.md`

## Summary

Build the agent behavior for the three already-declared early stages of the
Database-to-PBIP flow (`discovery`, `domain_guess`, `scope_proposal`) that spec 121
declared but scoped out of automation. Given a reachable retail source, the agent
runs read-only discovery in **two layers** -- a portfolio-level *metadata* survey
(Layer A) across all reachable tables, then deep value-backed profiling (Layer B)
delegated to the existing per-table profiler for the tables selected into scope --
proposes a retail domain and a bounded first scope as **non-critical proposals** in
the existing Decision Store, and hands the grounded evidence into the already-shipped
Business Knowledge Interview. Delivery follows the repo's governance-slice shape and
121's precedent: **one new dedicated skill** (`retail-discover-portfolio`, working name)
+ **one new template** (the Layer-A survey blank) + a feature-local survey schema + a
kit-router verb entry + a `capabilities.yaml` row. Layer-A table enumeration is
agent-issued read-only metadata; the **DB branch MUST route through a mandatory
redaction-mirroring helper** (an `information_schema.tables` read over the existing DB
access seam, returning rows or a redacted error via `dialect.redact()`), while the
**file-folder branch** is an inline directory listing (no DSN, no leak vector). This
closes the credential-leak hole a raw inline DB query would carry (FR-011; see Technical
Context / R-2a). No new CLI verb, no runtime engine, no
second Decision Store, no second per-table profiler, no new `retail check` rule at MVP,
no change to the existing flow contracts, no PBIP/publish/warehouse execution. The
load-bearing engineering here is codifying what NOT to build.

## Technical Context

**Language/Version**: The feature is delivered primarily as an agent-conducted skill
plus YAML/Markdown artifacts (survey template, feature-local schema, kit-router block),
**plus one small new Python helper** for DB table enumeration (Python 3.13, matching the
package contract). Rationale (R-2a): `src/seshat/profile.py`/`dialect.py` expose per-table
`information_schema` column reads but NO schema-level "list all tables" enumerator, so
the reachable-table list is genuinely new work. The **DB branch MUST use this helper**
(no raw inline agent query) so DSN redaction has a single tested code path; it mirrors
`run_validate`'s config-resolve + `_ensure_driver` gate + `dialect.redact(exc, config)`
(repo lesson: db-cli-must-mirror-validate-redact). The **file-folder branch** is an
inline stdlib directory listing (no DSN, no leak vector). Either way Layer A adds no
value-backed measurement.

**Primary Dependencies**: No new third-party dependency. The DB enumeration helper
reuses the existing read-only DB access path (`QueryRunner`/`Dialect`, the same
driver-optional seam `profile.py`/`validate.py` use) for the `information_schema.tables`
read; the file-folder branch uses the stdlib. Layer-B profiling reuses the existing
per-table profilers (`src/seshat/profile.py` for DB, `src/seshat/file_profile.py` for
files) via `retail-onboard-table`; domain/scope records reuse the existing Decision Store
(`src/seshat/decision_store.py`) and its DS1-DS5 static rules; verdicts reuse the
existing gate. No new connector, reader, or engine.

**Storage**: Local committed files only. The Layer-A survey is one new committed
artifact per source (path/layout finalized in research.md, workspace-local); domain
and scope proposals are **records in the existing** `.seshat/semantic-decisions.yaml`
(non-critical free-form `decision_type` via the schema's pattern branch); Layer-B
per-table truth stays in the existing `mappings/<table>/source-profile.md`. No new
store, no database or service state.

**Testing**: pytest fixtures for the survey-artifact shape (metadata-only; no
value-backed measurement present; no raw PII/credentials); Decision Store fixtures
proving domain/scope records validate under the existing DS1-DS5 and never enter a
`blocking_decision_categories` set; a fail-closed test that a missing local input
(no survey / no domain proposal) yields a truthful local stop; a boundary test that
the survey never re-authors `mappings/<table>/source-profile.md`; and -- for the
mandatory DB enumeration helper (R-2a) -- monkeypatch tests for the three DSN-leak
failure modes (config-resolve, driver gate, `dialect.redact`), no real DB required.
`retail check` self-run stays exit 0 on the repo. No new rule family at MVP, so no
manifest regeneration is required for US1.

**Target Platform**: Windows-first (release gate), macOS/Linux best effort; CI on
Linux. Fully offline-capable -- Layer A reads metadata only; a live connection or an
optional reader being absent is a truthful `[PENDING LIVE PROFILE]`/`needs_sample`
boundary, never a fabricated inventory.

**Project Type**: Single Python CLI/agent toolkit -- a governance/discovery slice
(skill + template + feature-local contract + kit verb + capability row), consistent
with how spec 121 and the readiness spine shipped.

**Performance Goals**: Agent-conducted; no hard latency target. The Layer-A survey is
metadata-only and MUST inventory every reachable table regardless of source size
(FR-014, no agent-chosen coverage cap); it is expected to complete within a normal
interactive agent turn for hundreds of tables. Any static validation added later must
stay within the existing `retail check` run budget (< 2 s added).

**Constraints**: Read-only discovery only (no DDL/DML/execution/publish); two-layer
split enforced (Layer A metadata-only; Layer B delegates to the existing profiler);
no second per-table profiler; domain/scope are non-critical proposals confirmed via
121's existing low-risk batch path (no new status, no new `decision_type`, no new
`approval-authority.yaml` row, no self-grant); no numeric readiness/confidence score;
bounded local-stop behavior only (no global Decision Gate repair); no raw
suspected-PII/credentials/DSN in any committed artifact; UTF-8 without BOM; ASCII
arrows (`->`); repo-relative paths <= 200 chars (Windows MAX_PATH).

**Scale/Scope**: Sources of dozens-to-hundreds of tables at the Layer-A survey
(all inventoried); a first scope of a handful of in-scope tables carried into Layer-B
profiling; the three existing flow-stage contracts consumed unchanged. In scope for
the MVP: US1 (the Layer-A portfolio survey). Not in scope: an interview/runtime engine,
a PBIP compiler, KPI catalog expansion, a second Decision Store or readiness engine, a
new flow stage or contract-schema change, the deferred global machine-readable
required-inputs work (see spec "Future follow-up").

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.7.0 before research and
re-checked after Phase 1 design.*

| Principle | Verdict | Basis |
|-----------|---------|-------|
| I. Agent-First, Gate-Enforced | PASS / reinforced | The discovery flow is an agent-conducted skill; the enforced gates are the EXISTING ones (`retail check` DS1-DS5 over the domain/scope records; the existing pass/warn/blocked verdicts; artifact review of the survey). The agent proposes; the gate disposes. No new gate is added at MVP. |
| II. Depend, Never Fork | PASS / untouched | No execution adapter touched. F016 stays deferred and gated; nothing here defines meaning, mapping, metrics, or approval. |
| III. Medallion, Postgres-First, Gold-Only | PASS / untouched | Read-only discovery only; no warehouse authoring, no gold read-path change. Multi-engine/file reads stay within the existing read-only profile+validate seam and its optional-extra boundaries; no new engine. |
| IV. Source Mapping Before Silver | PASS / reinforced | The flow sits BEFORE mapping: Layer A orients, Layer B hands each in-scope table to the existing `retail-onboard-table` (Source Ready -> Mapping Ready). It writes no `silver.*` and never clears the mapping gate. |
| V. Agent Stops at Judgment Calls | PASS / reinforced | Domain/scope are proposals a named human confirms (via the existing low-risk batch path), rejects, or supersedes; the agent never self-confirms. Grain/PII/identity remain the existing per-table human seams, unchanged. |
| VI. Defaults Then Deviations | PASS / untouched | No cleaning/modeling ruling is authored here; RC1-RC16 are untouched. The survey records candidate structure as hints, never adopted defaults. |
| VII. C086 Is An Example, Not The Schema | PASS | Skill, template, and schema are generic with placeholders; fixtures use synthetic multi-table metadata; no worked-example specifics baked in. |
| VIII. Static-First Governance, Live Deferred | PASS / reinforced | Layer A is static/metadata; unavailable live measurement is `[PENDING LIVE PROFILE]`/`needs_sample`, never fabricated. No new live surface; no new static rule at MVP (a survey-shape rule is deferred until a filled target exists -- see research.md R-4). |
| IX. Secrets and Reproducibility | PASS / reinforced | No raw suspected-PII, credentials, DSNs, or connection strings in any committed artifact (FR-011); PII handled as name/type hints at Layer A; UTF-8 no BOM; ASCII arrows; short paths. |

**Result: PASS. No constitutional violation requires Complexity Tracking.**

**Anti-scope-creep gates carried from the spec's four review corrections** (these are
the boundaries the plan must not let the implementation cross; research.md records the
"why NOT" for each):

- **No second per-table profiler** (FR-009B/FR-013): Layer B is a delegation to the
  existing profiler, never a re-implementation of `mappings/<table>/source-profile.md`.
- **No new Decision Store status / vocabulary / authority row** (FR-019): domain/scope
  are non-critical records in the existing store; the recorded status of a
  batch-confirmed member follows 121's existing convention (NOT re-pinned here).
- **No global Decision Gate repair** (FR-024-027): only bounded local stops within the
  discovery->interview-handoff flow; the global work is the spec's deferred follow-up.
- **No flow-contract change** (FR-026): the `discovery`/`domain_guess`/`scope_proposal`
  entries in `contracts/knowledge/database-to-pbip-flow.yaml` are consumed unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/122-contract-driven-discovery/
├── plan.md                       # This file
├── research.md                   # Phase 0 output (decisions incl. the "why NOT" record)
├── data-model.md                 # Phase 1 output (survey shape + reused store lifecycle)
├── quickstart.md                 # Phase 1 output (agent walkthrough of the bounded flow)
├── contracts/                    # Phase 1 output (FEATURE-LOCAL design artifacts only)
│   └── portfolio-survey.schema.md # the Layer-A survey artifact shape (new interface)
├── checklists/requirements.md    # (existing)
├── spec.md                       # (existing)
└── tasks.md                      # Phase 2 output (/speckit-tasks -- NOT created here)
```

### Source Code (repository root)

```text
.claude/skills/retail-discover-portfolio/   # NEW agent-conducted verb (working name)
└── SKILL.md                                 #   Layer-A survey -> domain -> scope ->
                                             #   selected-table onboarding -> interview handoff -> stop

templates/                                   # existing dir
└── portfolio-survey.md                      # NEW blank: the Layer-A metadata survey shape

.seshat/kit-source.yaml                      # + router entry for the new verb (regenerated block)

docs/capabilities/capabilities.yaml          # + a discovery/domain/scope producer row (SC-009)
docs/knowledge-map.md                        # + route note: portfolio discovery (if a route is cited)
docs/glossary.md                             # + Layer A / Layer B / portfolio survey terms

tests/unit/
├── test_portfolio_survey.py                 # survey shape: metadata-only; no value-backed
│                                            #   measurement; no raw PII/credentials; all
│                                            #   reachable tables inventoried
└── test_discovery_flow_stops.py             # bounded-flow local stops: no survey / no domain
                                             #   proposal -> truthful local stop; domain/scope
                                             #   records validate under existing DS1-DS5 and sit
                                             #   in NO blocking_decision_categories

# NOT touched (asserted, not edited):
#   contracts/knowledge/database-to-pbip-flow.yaml   (FR-026 -- consumed unchanged)
#   contracts/knowledge/approval-authority.yaml      (FR-019 -- no new row)
#   src/seshat/decision_store.py + rules/decision_store.py  (reused as-is)
#   src/seshat/profile.py / file_profile.py           (reused via retail-onboard-table)
#   mappings/<table>/source-profile.md                (Layer B authors it; this feature never does)
```

**Structure Decision**: single-project layout on the existing repo. The only genuinely
new artifacts are (1) the agent-conducted discovery skill, (2) the Layer-A portfolio
survey template, and (3) its feature-local schema. Everything else is reuse or an
additive row/entry (kit-router, capabilities). This mirrors exactly how spec 121
shipped a governance slice (skill + templates + contracts + kit verb), minus the new
static-rule family -- which is intentionally deferred at MVP (research.md R-4) because a
new fail-closed rule needs a filled target and must be <no-finding> on `main` to land.

## Complexity Tracking

No constitutional violations; table intentionally empty.
