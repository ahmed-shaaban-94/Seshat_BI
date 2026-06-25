# Implementation Plan: Power BI Visual Foundation (F011A) -- the design substrate the Dashboard Ready verb reasons with

**Branch**: `017-powerbi-visual-foundation` | **Date**: 2026-06-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/017-powerbi-visual-foundation/spec.md`

## Summary

Author the Power BI design FOUNDATION: a router skill
(`.claude/skills/powerbi-dashboard-design/`) plus reference docs (`docs/powerbi/`), generic
templates (`templates/`), a design-system seed (`design/`), a starter theme (`themes/`), and
four starter page blueprints (`reports/blueprints/`). The one load-bearing behavior is
**routing every visual-design request into exactly one of four surfaces -- report visuals,
external background/canvas, theme JSON, implementation handoff -- and never blending them.**
The foundation is the vocabulary the Dashboard Ready VERB (F011 / on-disk 012) reasons with;
it adds NO new gate, inherits Dashboard Ready's rule-5 / rule-6 gating verbatim, and is
docs/templates/skill only (rule 8), generic (rule 7). No PBIP/PBIR edit, no DAX, no SQL, no
semantic-model edit, no pbi-cli automation, no codegen engine, no CLI, no new `retail check`
rule.

## Technical Context

**Language/Version**: N/A -- agent-procedure Markdown (`SKILL.md` + workflows), reference
Markdown, generic YAML templates, one starter JSON theme. The agent is the runtime, same
posture as `source-mapping`, `retail-build-warehouse`, `retail-orchestrate`, and the F011/012
`dashboard-design` verb.

**Primary Dependencies**: none new. The foundation REFERENCES (does not wire) the approved
metric contracts (F009, PLANNED), the governed PBIP model (F010), the readiness model
(`docs/readiness/readiness-model.md` + `templates/readiness-status.yaml`), the Dashboard
Ready stage doc (`docs/readiness/dashboard-ready.md`), and the F011/012 verb
(`.claude/skills/dashboard-design/SKILL.md`). No `pbi-cli`, no Power BI Desktop, no network,
no DB driver, no new Python.

**Storage**: committed text only. Outputs are the skill + workflows + docs + templates +
tokens + theme + blueprints listed in the deliverable manifest. No DB writes, no PBIR
generation, no PBIP edit.

**Testing**: doc/fixture review -- (a) a router fixture of ~10 generic requests exercising all
four surfaces + ambiguous cases (SC-001); (b) a gate fixture exercising each non-`pass`
`semantic_model_ready` status on a data-bound request and an allowed pure-styling request
(SC-002); (c) deterministic checks: YAML validity, JSON validity for the theme, ASCII +
UTF-8 no BOM, C086-leakage grep, `retail check` exit 0 with unchanged rule count, and a grep
proving 0 PBIP/PBIR/DAX/SQL/semantic-model/pbi-cli edits (SC-003/SC-007/SC-008). No new
unit-test surface -- this is a docs/templates/skill slice (same posture as 010 and 012).

**Target Platform**: the Claude Code agent in this repo (Windows; 260-char path limit -> the
skill dir/name is short: `powerbi-dashboard-design`; all new paths kept `<= 200` chars
repo-relative).

**Project Type**: agent-design foundation (Layer 6 Dashboard & Delivery), single repo. Not a
library/web-service/app.

**Performance Goals**: N/A (reference material + an authoring procedure, not a runtime
service).

**Constraints**: ASCII + UTF-8 no BOM; generic (no C086/pharmacy specifics); no real
host/secret in any output (G6 + repo secret rule); never crosses the author/publish boundary
(rule 6); never defines a second gate or a divergent source of truth; never self-grants
`dashboard_ready: pass`.

**Scale/Scope**: 1 router skill + 8 workflow files; 5 reference docs (`docs/powerbi/`:
visual-design-system, background-assets, theme-json, dashboard-blueprints, visual-qa); 5
generic templates; 1 tokens file + 1 grids pair + 1 backgrounds README; 1 starter theme + 1
themes README; 4 starter blueprints; plus two pointer/registration edits to existing docs
(`docs/readiness/dashboard-ready.md` -- "foundation that backs this stage"; and
`docs/roadmap/roadmap.md` -- the F011A row). ~30 new files + 2 edited, all committed text.
One worked instance is a per-subject-area working set, NOT part of this slice's commit.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design (below). Source:
`.specify/memory/constitution.md` v1.6.0.*

| Principle | How this feature complies |
|-----------|---------------------------|
| I. Agent-First, Gate-Enforced | A router skill (agent verb) + reference material. The agent reads the foundation to choose a surface; the gate (rule 5 + `retail check` R1, owned by the stage doc + F011/012) and the human design-review dispose. The foundation proposes; it does not self-grant a `pass`. |
| II. Depend, Never Fork | No fork, no vendored engine, no codegen, no theme generator, no `retail design` CLI. pbi-cli stays the LATER adapter (F016); this slice never invokes it. The starter theme is a hand-authored conservative seed, not a generated artifact. |
| III. Medallion, Postgres-First, Gold-Only | Unaffected -- the foundation describes designing against the gold-bound semantic model; it adds no read surface, edits no SQL, touches no schema. |
| IV. Source Mapping Before Silver | Unaffected; reinforced by analogy -- the same author-then-stop, reference-don't-embed posture, two stages later. |
| V. Agent Stops at Judgment Calls | The router STOPS on an ambiguous surface, the business-question choice, a readability/grain deviation, and the design-review sign-off -- it surfaces them, never self-answers (FR-009). |
| VI. Defaults Then Deviations | Conservative executive tokens + grain-appropriate visuals are the DEFAULT; a deviation (dark dense page, grain mismatch) must be recorded as a `warning`-class note with a reason. |
| VII. C086 Is An Example | Every skill/doc/template/token/theme/blueprint is generic; worked values live only in a per-subject-area instance (FR-008, SC-007). |
| VIII. Static-First, Live Deferred | Docs/templates/skill-first (rule 8). No new gate, no new rule -- reuses existing R1 and the stage doc. Publishing (live) is deferred to F016. |
| IX. Secrets and Reproducibility | No real host/secret in any output (G6); ASCII + UTF-8 no BOM; paths `<= 200` chars; the theme JSON is parameter/default-only, no connection string (FR-014). |

**Readiness System (spine) compliance** -- this feature is Layer 6 / Dashboard Ready
foundation and MUST NOT weaken the spine:

- Adds NO new gate. Dashboard Ready's gate (rule 5 contracts-first; the design-review
  sign-off) and the rule-6 publish boundary are owned by `docs/readiness/dashboard-ready.md`
  + F011/012; this slice DOCUMENTS and REUSES them verbatim (FR-004) -- it does not create a
  second, divergent source of truth (Governance amendment clause 4).
- Records `dashboard_ready` with the four statuses + evidence + blockers, never a fabricated
  score (rule 9, FR-010), and never self-grants `pass` (FR-010).

**Roadmap hard rules**: rule 5 (no design before contracts) = FR-002/FR-004/US2; rule 6 (no
pbi-cli/PBIP before semantic-model readiness) = FR-007/US1 scenario 6/handoff workflow;
rule 7 (generic) = FR-008; rule 8 (docs/templates first) = the whole foundation shape;
rule 9 (no fake confidence) = FR-010.

**Result**: PASS (9/9 + spine + roadmap rules). No violations. Complexity Tracking below
records the one item that needs justification: the new top-level directories.

## Project Structure

### Documentation (this feature)

```text
specs/017-powerbi-visual-foundation/
|-- spec.md                  # the feature spec (committed)
|-- plan.md                  # this file
|-- tasks.md                 # the task list (speckit-tasks output)
`-- checklists/
    `-- requirements.md      # the spec-quality checklist (speckit-checklist output)
```

No `research.md` / `data-model.md` / `quickstart.md` / `contracts/`: there is no unknown to
research (the stage doc `docs/readiness/dashboard-ready.md`, the readiness model, F011/012,
and R1 already specify the gate, artifacts, and checks), no data model (the entities are the
contracts/model this foundation consumes, owned by F009/F010, plus generic templates that ARE
their own shape), and no API contract (a skill + reference material, not a service). This
mirrors the lightweight docs-slice shape 010 and 012 used.

### Source / deliverable manifest (repository root)

The deliverables the tasks author. (Skill under `.claude/skills/` -- see Structure Decision.)

```text
.claude/skills/powerbi-dashboard-design/
|-- SKILL.md                          # the four-surface ROUTER (front door) + hard rules
`-- workflows/
    |-- visual-design-system.md       # surface 1: cards/charts/slicers/tables/tooltips/bookmarks/interactions
    |-- background-asset-design.md    # surface 2: external PNG/SVG backgrounds, safe zones, static containers
    |-- theme-json-design.md          # surface 3: palette/fonts/visual+page+filter-pane defaults, sentiment colors
    |-- page-blueprint.md             # surface 1: page = one business question; sections; visual list
    |-- dashboard-qa.md               # surface 1: the visual anti-pattern reference
    |-- screenshot-review.md          # surface 1: critique procedure (findings + fixes + forbidden changes)
    |-- mobile-layout.md              # surface 1: phone layout guidance
    `-- powerbi-handoff.md            # surface 4: consumes the artifacts -> implementation NOTES only; F016 owns execution

docs/powerbi/
|-- visual-design-system.md           # the four surfaces distinguished + Power BI design principles
|-- background-assets.md              # the external-background workflow + background rules (structure not data)
|-- theme-json.md                     # what theme JSON controls + what it must NOT control
|-- dashboard-blueprints.md           # how a page blueprint is read + the four starters' index
`-- visual-qa.md                      # the QA reference doc (prose home of the anti-pattern list)

templates/                            # generic, copy-me blanks (rule 7) -- one per surface concern
|-- dashboard-page-blueprint.yaml     # page name/audience/business question/readiness deps/contracts/model/
|                                     #   background/theme/canvas/grid/sections/visuals/slicers/tooltips/mobile/QA
|-- visual-spec.yaml                  # visual id/type/question/contract/fields/position/formatting/interactions/
|                                     #   tooltip/sorting/number-format/anti-pattern checks
|-- background-spec.yaml              # page/canvas/asset path/export format/safe zones/static regions/
|                                     #   FORBIDDEN dynamic content/import instructions/QA checklist
|-- theme-json-spec.md                # human-readable theme spec: palette/typography/sentiment/data colors/
|                                     #   visual+filter-pane defaults/background/accessibility/JSON-validation reminder
`-- screenshot-review.md              # the critique checklist template (output shape)

design/
|-- tokens/
|   `-- tower-retail-design-tokens.yaml   # conservative executive seed: colors/text/sentiment/neutrals/
|                                         #   font/spacing/KPI-card rules/max-visuals-per-exec-page/number formats
|-- grids/
|   |-- 16x9-grid.yaml                 # desktop canvas grid + safe zones
|   `-- mobile-grid.yaml               # phone canvas grid
`-- backgrounds/
    `-- README.md                      # where exported background assets live + naming + the structure-not-data rule

themes/
|-- tower-retail.theme.json            # minimal CONSERVATIVE starter (name/dataColors/background/foreground/
|                                      #   tableAccent/safe visualStyles defaults) -- VALIDATE in Desktop
`-- README.md                          # what the theme is, the validate-in-Desktop note, the schema-uncertainty note

reports/blueprints/                    # four GENERIC starter page blueprints (placeholders, no invented metric)
|-- executive-summary.yaml
|-- branch-performance.yaml
|-- product-mix.yaml
`-- data-quality-control-room.yaml

docs/readiness/dashboard-ready.md      # EDIT (pointer only): add "the design foundation that backs this stage"
                                       #   row pointing at the skill + docs/powerbi/ -- no gate/status change
docs/roadmap/roadmap.md                # EDIT (registration only): add the F011A row (Layer 6, Dashboard Ready
                                       #   foundation) + the 017=F011A numbering note -- no hard-rule/ordering change
```

**Structure Decision**:

1. **Skill at `.claude/skills/powerbi-dashboard-design/`, not top-level `skills/`.** The
   input wrote `skills/`, but this repo discovers skills only under `.claude/skills/` (all 20
   existing skills live there). A skill authored at top-level `skills/` would not load -- a
   dead artifact. The deviation is deliberate and recorded; only the SKILL has this
   loadability constraint. The other input paths (`design/`, `themes/`, `reports/`,
   `docs/powerbi/`, `templates/`) are honored literally.
2. **New top-level dirs `design/`, `themes/`, `reports/`** are introduced because they are
   distinct artifact families with distinct lifecycles: `design/` is the design-system source
   (tokens/grids/backgrounds, tool-agnostic), `themes/` is the Power-BI-specific compiled
   default (`.theme.json`), `reports/blueprints/` is the per-page design intent (parallel to
   how `mappings/<table>/` holds per-table working sets and `warehouse/migrations/` holds
   SQL). Keeping them separate keeps `templates/` as generic blanks and `docs/` as narrative
   (the same separation ADR 0003 made for mappings). Justified in Complexity Tracking.
3. **No `src/` change, no new `retail check` rule, no codegen, no CLI** -- consistent with the
   all-skills verb architecture and roadmap rule 8. R1 already covers the relative model
   reference; this slice consumes it, adds nothing.
4. **`docs/powerbi/` carries TWO QA homes by design:** `visual-qa.md` (prose reference, the
   readable anti-pattern explanations) and the skill's `dashboard-qa.md` workflow (the
   agent-procedure that USES them). Same doc/skill split as the rest of the kit.

## Phasing

- **Phase 0 (research)**: none required -- the stage doc + readiness model + F011/012 +
  R1 are the authoritative inputs and already exist. Recorded as "no open unknowns" (O-1, the
  router-alongside-vs-absorb question, is a documented decision with a reversible default, not
  a research unknown).
- **Phase 1 (design = author the foundation)**: the deliverable manifest above. The boundary
  facts (four surfaces, the inherited gate, the no-divergent-source-of-truth rule, the
  structure-not-data and defaults-not-meaning rules) are FIXED FIRST (a foundational phase in
  tasks) and reused verbatim across every artifact. Re-run Constitution Check (still PASS --
  no new gate, no new rule, no data edit).
- **Phase 2 (tasks)**: enumerated in `tasks.md`.

## Complexity Tracking

> One item to justify: the new top-level directories. Everything else passed 9/9 with no
> violation.

| Item | Why needed | Simpler alternative rejected because |
|------|------------|--------------------------------------|
| New top-level `design/`, `themes/`, `reports/` directories | Three distinct artifact families with distinct lifecycles and audiences: tool-agnostic design-system source (`design/`), the Power-BI-specific compiled theme default (`themes/`), and per-page design intent (`reports/blueprints/`). | Folding all into `templates/` would mix generic copy-me blanks with concrete seeds (tokens, the starter theme, four named blueprints), breaking the "templates are generic, instances are elsewhere" separation the kit already uses (ADR 0003 mappings/, warehouse/migrations/). Folding into `docs/` would put a machine-read YAML/JSON next to narrative prose. The split keeps each home single-purpose. |

## Post-Design Constitution Re-Check

To be re-evaluated after Phase 1 artifacts are authored: expected to stay PASS (9/9 + spine +
roadmap rules). The Phase 1 artifacts are documentation/templates/a-skill that DESCRIBE and
ROUTE; they add no code, no dependency, no data write, no new gate, no resolution of a
deferred decision, and no divergent source of truth. Recorded in tasks' final verification
phase.
