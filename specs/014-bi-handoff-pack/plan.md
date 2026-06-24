# Implementation Plan: BI Handoff Pack

**Branch**: `014-bi-handoff-pack` | **Date**: 2026-06-24 | **Spec**:
[spec.md](./spec.md)

**Roadmap**: F013 (Layer 6). Advances **Publish Ready** (stage 7).

**Input**: Feature specification from `specs/014-bi-handoff-pack/spec.md`

## Summary

Deliver the **BI Handoff Pack** as a generic, docs/templates-first artifact set:
a copy-per-table pack template (`templates/handoff/bi-handoff-pack.md`), a
handoff-review checklist (`templates/handoff/handoff-review-checklist.md`), and
the cross-links that wire them into the readiness spine (publish-ready.md +
readiness-model.md "See also"). The pack **composes existing readiness
evidence** (metric contracts, readiness scorecard, reconciliation report,
data-issues, assumptions, deployed schema) and adds exactly one new thing: a
recorded, named **publish approval**. No publishing, no pbi-cli/PBIP, no Fabric,
no validator (hard rules #6, #8, #9).

**Technical approach**: pure documentation. The "engine" is the existing
readiness model + the five mapping-gate templates + the four readiness templates.
This slice authors two new template files and edits two existing stage docs to
reference them. There is no code, no dependency, no runtime surface.

## Technical Context

**Language/Version**: N/A -- Markdown docs/templates only (ASCII, UTF-8 no BOM).

**Primary Dependencies**: None new. References existing artifacts:
`templates/readiness-scorecard.md`, `templates/data-issues.md`,
`templates/blocking-reasons.md`, `templates/readiness-status.yaml`,
`templates/assumptions.md`, `templates/source-map.yaml`,
`templates/reconciliation-report.md`, `docs/readiness/publish-ready.md`,
`docs/readiness/dashboard-ready.md`, `docs/readiness/readiness-model.md`.

**Storage**: Git-tracked Markdown/YAML. No database, no live connection.

**Testing**: Docs-level acceptance only -- cross-link existence, ASCII/UTF-8
no-BOM, generic (no worked-example specifics), and a manual walk of the
checklist against a generic placeholder table. No unit/integration test code is
introduced (this slice ships no code).

**Target Platform**: Repo docs; consumed by an agent + a human reviewer on
Windows (MAX_PATH-aware paths).

**Project Type**: Documentation/templates slice within the Tower BI Agent Kit
(no `src/` change).

**Performance Goals**: N/A (docs).

**Constraints**: ASCII + UTF-8 no BOM; short repo-relative paths (Principle IX);
generic only (Principle VII); composes-not-invents (rule #9); no
publish/pbi-cli/Fabric (rule #6); docs-before-code (rule #8).

**Scale/Scope**: Two new template files + two stage-doc edits + the spec chain.
Bounded; no fan-out into code.

## Constitution Check

*GATE: must pass before and after design. This is a docs slice; the gates are
the constitution principles and the roadmap hard rules.*

| Gate (principle / rule) | How this plan satisfies it |
|-------------------------|----------------------------|
| **I. Agent-First, Gate-Enforced** | The pack is what the agent assembles at the Publish Ready gate; the gate authority stays the existing checks + the human approval, not the pack itself. The pack adds no new "agent decides" authority. |
| **II. Depend, Never Fork** | No pbi-cli touch at all. The adapter stays the later, gated F016. |
| **III. Medallion, Gold-Only** | Data dictionary is written against the DEPLOYED `gold` schema only; no silver/bronze read surface introduced. |
| **IV. Source Mapping Before Silver** | Untouched -- this stage is downstream of an approved map; the pack only references the mapping artifacts. |
| **V. Agent Stops at Judgment Calls** | The publish approval is a named human sign-off the agent MUST NOT self-grant; PII/rollup/grain/identity are recorded, not decided, by the pack. |
| **VI. Defaults Then Deviations** | The caveats compose `assumptions.md` (adopted-vs-deviated already recorded); the pack does not re-derive defaults. |
| **VII. C086 Is An Example** | Template + checklist are generic; the worked example is cited by reference only. |
| **VIII. Static-First, Live Deferred** | Docs-only; no new validator. Reconciliation evidence is the already-built `retail validate` output referenced via `reconciliation-report.md`. |
| **IX. Secrets & Reproducibility** | No credentials; ASCII/UTF-8 no BOM; short paths. The pack references `.env`-sourced read-only runs but stores no secret. |
| **Rule #6 (no pbi-cli before F016)** | Explicit FR-008 / agent-must-not list; nothing in the pack publishes or authors. |
| **Rule #8 (docs/templates first)** | The entire deliverable is docs + a checklist; no automation. |
| **Rule #9 (no fake confidence)** | FR-010: four explicit statuses + evidence + blockers; no score. |
| **Readiness System (spine)** | The pack is the Publish Ready stage's concrete artifact; it enters only when `dashboard_ready: pass`. |

**Result**: PASS. No violations; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/014-bi-handoff-pack/
├── spec.md          # /speckit-specify output (done)
├── plan.md          # This file (/speckit-plan output)
├── tasks.md         # /speckit-tasks output
└── analysis.md      # /speckit-analyze findings
```

No `research.md` / `data-model.md` / `contracts/` / `quickstart.md` are needed:
this is a docs/templates slice with no code design, no API, and no data model
beyond the existing readiness templates.

### Source Code (repository root)

No `src/` change. The delivered artifacts are docs/templates:

```text
templates/
└── handoff/
    ├── bi-handoff-pack.md             # NEW: the generic pack index (composes evidence)
    └── handoff-review-checklist.md    # NEW: the completeness gate (human-walked)

docs/readiness/
├── publish-ready.md                   # EDIT: Required artifacts + See also -> pack path
└── readiness-model.md                 # EDIT: See also -> the pack template (spine consistency)
```

**Structure Decision**: Place the two new templates under `templates/handoff/`
to keep them beside the other readiness templates (`templates/*.md`,
`templates/*.yaml`) while grouping the two pack files in one short subdirectory.
A per-table FILLED instance is NOT created in this slice (generic only); when a
real table is handed off, the analyst copies these blanks. Edits to the two
existing readiness docs keep the spine's cross-links internally consistent
(FR-013).

## Phasing (docs slice)

1. **P1 -- Pack template + checklist (US1, US2).** Author
   `bi-handoff-pack.md` (index of required sections, each -> existing artifact;
   caveats block; approval slot) and `handoff-review-checklist.md` (one line per
   required section; satisfied-or-gap). This is the MVP.
2. **P2 -- Caveats hardening (US3).** Make the four caveats (PII / returns /
   known-gaps / out-of-scope) mandatory in the template and a FAIL condition in
   the checklist.
3. **P3 -- Data dictionary (US4).** Add the column-by-column dictionary section
   keyed to the deployed schema, with the "matches deployed schema" checklist
   item.
4. **P4 -- Spine wiring (FR-013).** Edit `publish-ready.md` and
   `readiness-model.md` See-also/Required-artifacts to point at the new pack
   path; verify all cross-links resolve.

## Complexity Tracking

> No constitution violations. Section intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| -- | -- | -- |
