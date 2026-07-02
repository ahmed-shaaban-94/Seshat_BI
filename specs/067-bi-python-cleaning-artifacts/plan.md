# Implementation Plan: Land bi-python's Planned Cleaning Artifacts

**Branch**: `067-bi-python-cleaning-artifacts` | **Date**: 2026-07-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/067-bi-python-cleaning-artifacts/spec.md`

## Summary

Land the one planned terminal artifact the live cleaning route dead-ends on --
`skills/bi-python-knowledge/checklists/cleaning-review-checklist.md` -- by
distilling the reasoning that already exists in
`knowledge/cleaning-and-standardization.md` into a checkbox-plus-verdict review
artifact that MIRRORS the shape of the shipped `aggregation-grain-checklist.md`,
then flip that route from "planned" to "live" across `INDEX.md`, the cleaning
knowledge file's inline notes, and `README.md`. No runtime code, no new
static-analysis rule, no new IDs, no new metric or gating logic. This is a
docs-only knowledge-skill content-completion change (Static-First / hard rule 8).

## Technical Context

**Language/Version**: N/A -- Markdown documentation inside a knowledge SKILL. No
executable code is added (the agent is the runtime; Static-First / hard rule 8).

**Primary Dependencies**: None. Content depends only on existing files in
`skills/bi-python-knowledge/` (the cleaning knowledge file, the aggregation-grain
checklist as shape template, `references/id-conventions.md`,
`references/retail-dataframe-schema.md`).

**Storage**: N/A (plain-text files committed to git).

**Testing**: Manual / reviewer verification against the spec's Success Criteria
and the plan-review skeptic pass. No automated test framework applies to a
docs-only knowledge artifact; there is no retail check rule and no Python module
introduced by this feature. (Verification method = grep + read-through, per each
SC.)

**Target Platform**: Repo-hosted knowledge skill consumed by an AI agent; edited
on Windows (UTF-8 no BOM, ASCII, short paths -- Principle IX / hard rule 9).

**Project Type**: Documentation / knowledge-skill content (single knowledge tree).

**Performance Goals**: N/A (static docs).

**Constraints**: ASCII-only (`--`, `->`, no glyphs); UTF-8 without BOM; short
repo-relative paths; no C086/pharmacy inline specifics; no numeric score; no
newly minted IDs; no runtime code; no flipping of unrelated planned routes.

**Scale/Scope**: One NEW file + edits to three EXISTING files
(`INDEX.md`, `knowledge/cleaning-and-standardization.md`, `README.md`). Bounded.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle VIII (Static-First; hard rule 8 docs/templates first)**: PASS --
  the feature adds only reasoning-content docs; the agent is the runtime. No
  runtime Python, no new retail check rule.
- **Principle VII (C086 is an example, not the schema; hard rule 7)**: PASS by
  design -- FR-014 + SC-006 forbid inline pharmacy specifics; examples cite only
  `references/retail-dataframe-schema.md`; C086 only as an external worked example.
- **Principle V (agent stops at judgment calls)**: PASS -- human-reserved cleaning
  decisions become "recorded by a human" checkboxes (FR-007); the verdict
  vocabulary and roadmap-stage mapping are deferred to a human ratifier (spec
  ## Clarifications), never self-answered.
- **Principle II analog / big-data fork boundary**: PASS -- FR-013 keeps the
  checklist single-node and hands distributed cleaning to
  `skills/bi-bigdata-knowledge/`.
- **Aggregation-grain fork boundary**: PASS -- FR-012 references, does not re-own,
  the aggregation-grain checklist.
- **Principle IX (reproducibility / Windows)**: PASS -- FR-015 fixes encoding /
  ASCII / short-path constraints.
- **IL1 ledger / no-fake-confidence (hard rule 9)**: PASS -- FR-006 forces a
  categorical verdict (no numeric score); FR-016 forbids self-assigning an F-row.
- **Layer-boundary discipline (SKILL.md)**: PASS -- the checklist hands off at its
  edge (SQL/DAX/readiness); it does not define metric meaning or gating.

No violations -> Complexity Tracking left empty.

## Project Structure

### Documentation (this feature)

```text
specs/067-bi-python-cleaning-artifacts/
├── spec.md              # Stage 2 (specify)
├── plan.md              # This file (Stage 4 plan)
├── tasks.md             # Stage 4 tasks
├── analysis.md          # Stage 5 analyze (repo convention: analyze writes here)
├── plan-review.md       # Stage 6 adversarial plan-review
└── checklists/
    └── requirements.md  # Stage 2 spec-quality checklist
```

No research.md / data-model.md / quickstart.md / contracts/ are produced: this is
a docs-only content change with no data model, no API, and no external research
(the source material already lives in the skill). Their absence is deliberate,
not an omission.

### Source Code (repository root)

The "source" of this feature is documentation inside the knowledge skill:

```text
skills/bi-python-knowledge/
├── INDEX.md                              # EDIT: flip cleaning-review route planned -> live
├── README.md                            # EDIT: coverage claim reflects landed checklist
├── knowledge/
│   └── cleaning-and-standardization.md  # EDIT: "Ends on" + PY-CN-033/PY-CN-036 inline notes
└── checklists/
    ├── aggregation-grain-checklist.md   # UNCHANGED (shape template only)
    └── cleaning-review-checklist.md      # NEW: the terminal artifact this feature lands
```

**Structure Decision**: Land exactly one new file in the existing `checklists/`
home and edit exactly three existing files. No new directories. No `patterns/`
files (Clarification C1: pattern files are OUT of scope). The aggregation-grain
checklist is a read-only shape reference and is NOT modified.

## Phased Approach

**Phase 0 -- Grounding (already done in the spec).** Source content, shape
template, ID families, and fork boundaries are confirmed by the grounding seed;
no additional research needed.

**Phase 1 -- Author the checklist.** Write
`checklists/cleaning-review-checklist.md`: lettered sections (A..) of checkbox
items, each citing an EXISTING ID (PY-BP-005, PY-CN-031..037, PY-AP-001); a
row-count-ledger "Attach" line; human-reserved decisions as "recorded by a human"
checkboxes; a categorical verdict block whose exact wording carries a visible
"[reserved for human ratification]" note (FR-006) rather than a self-invented
threshold; a one-line reference to the aggregation-grain checklist (fork boundary)
and a one-line single-node handoff to `bi-bigdata-knowledge`.

**Phase 2 -- Flip the route (bounded).** Edit `INDEX.md` (remove the checklist row
from Planned routes; point the cleaning task + symptom routes at the checklist;
rewrite the cleaning-route endpoint note; add the checklist under the shipped
`checklists/` file-map line), `knowledge/cleaning-and-standardization.md` (rewrite
the "Ends on" block and the PY-CN-033 / PY-CN-036 "planned" phrasing about the
checklist), and `README.md` (update the coverage claim). Touch NOTHING about the
other planned siblings.

**Phase 3 -- Verify.** Grep for the checklist path and for "planned / not yet
implemented" to confirm the flip is complete (SC-002) and bounded (SC-005); read
through against SC-001, SC-003, SC-004, SC-006.

## Complexity Tracking

> No Constitution Check violations -- section intentionally empty.
