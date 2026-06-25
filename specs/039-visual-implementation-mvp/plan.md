# Implementation Plan: Visual Implementation MVP (F034) -- turn an approved blueprint into a real PBIR page, built by hand, reviewed in git

**Feature**: F034 (roadmap F-number, authoritative) | **Spec directory**: `039-visual-implementation-mvp` (next free on-disk slot -- the script numbers from the current max `038`, not the first gap)

**Branch**: `039-visual-implementation-mvp` | **Date**: 2026-06-25 | **Spec**: [spec.md](./spec.md)

**Status**: Draft

**Input**: Feature specification from `specs/039-visual-implementation-mvp/spec.md`

## Summary

Author the manual VISUAL-IMPLEMENTATION slice: one agent-procedure workflow
(per O-1, `visual-implementation-review.md` ALONGSIDE `powerbi-handoff.md` under
`.claude/skills/powerbi-dashboard-design/workflows/`), one generic trace template
(`templates/visual-implementation-trace.md`), one EVIDENCE-ITEM edit to the
Dashboard Ready stage doc (`docs/readiness/dashboard-ready.md`), and one worked
example -- the `retail_store_sales` empty Page 1 built by a HUMAN in Power BI
Desktop, saved as plain-text PBIR, committed, plus its filled trace under
`mappings/retail_store_sales/design/`. The one load-bearing behavior is **closing
the loop between the approved binding map and the built page, with a git-reviewable
1:1 trace, while crossing no automation boundary.** The slice adds NO new gate, NO
new readiness stage, NO new readiness status, NO new `retail check` rule -- only an
evidence item under the EXISTING Dashboard Ready owner. It inherits the Dashboard
Ready rule-5 gate VERBATIM and is docs/templates/skill only (rule 8), generic
(rule 7). No PBIR generation, no DAX, no SQL, no semantic-model edit, no pbi-cli /
Power BI MCP automation, no publish -- those are F016, and F034 is INDEPENDENT of
F016 (a manual Desktop build with git-diff review is not execution automation).

## Technical Context

**Language/Version**: N/A -- agent-procedure Markdown (one workflow), one generic
Markdown template, one stage-doc edit, plus a HUMAN-built PBIR page committed as
plain text. The agent is the runtime, same posture as `source-mapping`,
`retail-build-warehouse`, the F011/012 `dashboard-design` verb, and the F011A
`powerbi-dashboard-design` foundation.

**Primary Dependencies**: none new. The slice CONSUMES (does not re-derive) the
F011A `powerbi-handoff` build notes as its input contract
(`.claude/skills/powerbi-dashboard-design/workflows/powerbi-handoff.md`), the
F011/012 approved design artifacts (the layout plan, visual list, and
visual->contract binding map under `mappings/<subject>/design/`), the approved
metric contracts (F009), the governed PBIP model (F010), the readiness model
(`docs/readiness/readiness-model.md`), and the Dashboard Ready stage doc + its
rule-5 gate and R1 check (`docs/readiness/dashboard-ready.md`). No `pbi-cli`, no
Power BI MCP, no network, no DB driver, no new Python.

**Storage**: committed text only -- the workflow + the trace template + the stage-doc
edit, plus the human's Desktop save of the PBIR page (`<report>/definition/`) and the
filled trace instance. No DB writes, no PBIR GENERATION (the page is built in Desktop,
not emitted by the agent), no semantic-model edit, no publish.

**Testing**: doc/fixture review -- (a) a gate fixture exercising each non-`pass`
`semantic_model_ready` status and a `pass`-but-no-sign-off case, asserting 0
implemented-page evidence + the matching blocking reason (SC-003, US2); (b) a trace
fixture with an orphan visual (not in the approved binding map) and an unmapped field,
asserting `trace: blocked` never `pass` (SC-002, US2); (c) a boundary fixture of
"generate the PBIR" / "run pbi-cli" / "publish to workspace" requests, asserting 0
automation output and F016 named each time (SC-004, US3); (d) deterministic checks:
ASCII + UTF-8 no BOM, C086-leakage grep over every generic file (SC-006), the discount
50.37% / no-stale-rate grep on the worked example (SC-007), `retail check` exit 0 with
its rule count UNCHANGED (SC-005), and a grep proving 0 generated PBIR / 0 DAX / 0 SQL /
0 semantic-model edits / 0 pbi-cli-MCP commands (SC-004). No new unit-test surface --
this is a docs/templates/skill slice (same posture as 010, 012, and 017).

**Target Platform**: the Claude Code agent in this repo (Windows; 260-char path limit).
The nested PBIR `definition/pages/<id>/...` folders plus short project/table names MUST
stay under 260 chars; all new repo-relative paths kept `<= 200` chars.

**Project Type**: agent-design slice (Layer 6 Dashboard & Delivery), single repo. Not a
library/web-service/app. The deliverable is a committed procedure + a reviewable trace;
the build itself is a human Desktop action and the review is a human reading a git diff.

**Performance Goals**: N/A (a procedure + a template + a worked example, not a runtime
service).

**Constraints**: ASCII + UTF-8 no BOM; generic (no C086/pharmacy or other subject-area
specifics in any generic file -- worked values only in the `retail_store_sales`
instance); no real host/secret in any output (Principle IX + G6); the PBIR references
the model by a RELATIVE path (R1); never crosses the build/publish boundary (rule 6,
F016 owns it); never defines a second gate or a divergent source of truth; never
self-grants `dashboard_ready: pass`; never invents/re-binds a metric; the worked-example
discount visual + its trace row show the corrected `DiscountedTransactionRate` = 50.37%
with the contract caveats (33.39% unknown excluded; 33.55% floor) and never the
retracted/stale figure.

**Scale/Scope**: 1 new workflow file (`visual-implementation-review.md`) + 1 new generic
template (`templates/visual-implementation-trace.md`) + 1 edit to
`docs/readiness/dashboard-ready.md` (an evidence-item distinction, not a gate/status
change). The worked example is a per-subject-area working set: 1 HUMAN-built PBIR page
(Desktop save of `powerbi/RetailStoreSales.Report/definition/`) + 1 filled trace
(`mappings/retail_store_sales/design/visual-implementation-trace.md`). ~2 new generic
files + 1 edited + 2 worked-example artifacts, all committed text.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design (below).
Source: `.specify/memory/constitution.md`.*

| Principle | How this feature complies |
|-----------|---------------------------|
| I. Agent-First, Gate-Enforced | A new workflow (agent procedure) + a trace template. The agent reads the approved binding map + the built page and VERIFIES (read-only) the 1:1 trace; the gate (rule 5 + R1, owned by the stage doc + F011/012) and the BI owner's design-review DISPOSE. The agent proposes the trace; it never self-grants a `pass` (FR-012). |
| II. Depend, Never Fork | No fork, no vendored engine, no PBIR generator, no theme/page codegen, no `retail` CLI subcommand. The page is built in Power BI Desktop (the repo's already-endorsed `pbip-workflow`); the agent REUSES the F011A handoff notes as input and verifies the human's Desktop save. pbi-cli/MCP stays the LATER, gated adapter (F016); this slice never invokes it. |
| III. Medallion, Postgres-First, Gold-Only | Unaffected -- the slice realizes a report bound to the gold semantic model; it adds no read surface, edits no SQL, touches no schema. |
| IV. Source Mapping Before Silver | Unaffected; reinforced by analogy -- the same realize-then-verify, consume-don't-re-derive posture, four stages later. |
| V. Agent Stops at Judgment Calls | The procedure STOPS on the judgment seams (FR-011): whether a built page faithfully realizes the approved design, whether a layout deviation discovered during the build is acceptable, whether the design-review sign-off covers the built page -- surfacing them to the BI owner, never self-answering or self-granting `dashboard_ready: pass`. |
| VI. Defaults Then Deviations | The default is: the built page matches the approved binding map 1:1. A deviation discovered during the build (a visual no longer in the map, a map entry with no built visual, an accepted layout adjustment) is recorded as a `warning`/`blocked` finding ON THE PAGE with a reason -- it never silently passes and never retracts the design approval. |
| VII. C086 Is An Example | Every generic artifact (the workflow, the trace template, the stage-doc edit) is generic to retail BI; worked values live ONLY in the `retail_store_sales` instance (FR-010, SC-006). C086/pharmacy is the prior worked example, not the schema. |
| VIII. Static-First, Live Deferred | Docs/templates/skill-first (rule 8): a committed procedure + a reviewable trace BEFORE any automation. No new gate, no new rule -- reuses R1 and the stage doc verbatim. Generation/publish (live) is deferred to F016. |
| IX. Secrets and Reproducibility | No real host/secret in any output (G6, FR-014); ASCII + UTF-8 no BOM; repo-relative paths `<= 200` chars; the PBIR references the model by a RELATIVE path (FR-007); the PBIR page folders stay under the Windows 260-char limit. |

**Readiness System (spine) compliance** -- this feature is Layer 6 / Dashboard Ready
and MUST NOT weaken the spine:

- Adds NO new gate, NO new readiness stage, NO new readiness status, NO new `retail
  check` rule. Dashboard Ready's gate (rule 5: contracts first + the design-review
  sign-off) and the rule-6 publish boundary are owned by
  `docs/readiness/dashboard-ready.md` + F011/012; this slice INHERITS them verbatim
  (FR-005/FR-006) and adds ONLY an `evidence[]` item ("built-page traces to approved
  binding map; R1 passes") under the existing owner -- it creates no second, divergent
  source of truth (Governance amendment clause: no divergent source of truth).
- Records `dashboard_ready` with the four statuses + evidence + blockers, never a
  fabricated score (rule 9, FR-012), and never self-grants `pass` (FR-012, SC-008) --
  `pass` stays the BI owner's recorded design-review action.

**Roadmap hard rules**: rule 5 (no implementation before contracts + sign-off) =
FR-006/US2; rule 6 (no pbi-cli/MCP/publish, F016 owns it) = FR-008/US3 -- F034 is
INDEPENDENT of F016, not blocked by it (a manual Desktop build is not the gated
automation); rule 7 (generic) = FR-010/SC-006; rule 8 (docs/templates first) = the
whole slice shape; rule 9 (no fake confidence) = FR-012.

**Result**: PASS (9/9 + spine + roadmap rules). No violations. No new top-level
directory, no new dependency, no data write -- nothing requires Complexity Tracking
justification (see below).

## Project Structure

### Documentation (this feature)

```text
specs/039-visual-implementation-mvp/
|-- spec.md                  # the feature spec (committed)
|-- plan.md                  # this file
|-- tasks.md                 # the task list (speckit-tasks output)
`-- checklists/
    `-- requirements.md      # the spec-quality checklist (speckit-checklist output)
```

No `research.md` / `data-model.md` / `quickstart.md` / `contracts/`: there is no
unknown to research (the stage doc, the readiness model, F011/012's binding map, the
F011A `powerbi-handoff` notes, R1, and `pbip-workflow` already specify the gate,
inputs, build order, and checks), no data model (the entities are the design artifacts
this slice consumes -- owned by F009/F010/F011-012 -- plus a generic trace template that
IS its own shape), and no API contract (a workflow + a template, not a service). O-1
(workflow-alongside vs standalone verb skill) is a documented decision with a reversible
default, NOT a research unknown. This mirrors the lightweight docs-slice shape 010, 012,
and 017 used.

### Source / deliverable manifest (repository root)

The deliverables the tasks author. Generic artifacts carry placeholders only; worked
values live in the per-subject-area instance.

```text
.claude/skills/powerbi-dashboard-design/workflows/
`-- visual-implementation-review.md    # NEW (per O-1, ALONGSIDE powerbi-handoff.md): the manual-build +
                                       #   git-review procedure. (a) restates the build order FROM the
                                       #   handoff notes (theme -> background -> visuals -> slicers/
                                       #   interactions -> mobile -> QA), never re-deriving it; (b) defines
                                       #   the git-diff review checklist a reviewer runs on the committed
                                       #   PBIR (plain text, no opaque .pbix; Desktop owns report.json /
                                       #   diagramLayout.json -- forbid hand-editing); (c) defines the 1:1
                                       #   trace check (every measure-bearing visual -> exactly one approved
                                       #   contract by name + a mapped model field; orphan visual or
                                       #   unmapped field => blocked); (d) inherits the rule-5 gate VERBATIM;
                                       #   (e) names F016 as the owner of any generation/publish (rule 6).
                                       #   Verifies a committed page; never authors or publishes one.

templates/
`-- visual-implementation-trace.md     # NEW generic copy-me blank (rule 7): one row per built
                                       #   measure-bearing visual -> the contract it binds to (by name) ->
                                       #   the mapped field(s) -> a PASS / blocking-reason column; plus the
                                       #   readiness header (status + evidence[] + blocking_reasons[]).
                                       #   Placeholders only (<visual>, <contract>, <field>) -- no C086, no
                                       #   retail_store_sales values.

docs/readiness/dashboard-ready.md      # EDIT (evidence-item distinction only): distinguish "design
                                       #   approved" from "page implemented" as an EVIDENCE ITEM under the
                                       #   existing owner -- a pass may record `evidence: built-page traces
                                       #   to the approved binding map; R1 passes`. NO new status, NO new
                                       #   gate, NO new rule, NO change to the gate/owner/blocking reasons.

mappings/retail_store_sales/design/                       # WORKED EXAMPLE (per-subject-area working set)
`-- visual-implementation-trace.md     # FILLED instance: the 10 approved visuals, each -> its one approved
                                       #   contract + mapped field + PASS; the discount row shows
                                       #   DiscountedTransactionRate = 50.37% with the 33.39%/33.55% caveats
                                       #   (never the retracted/stale figure). Slicers are dimension
                                       #   controls, NOT trace rows.

powerbi/RetailStoreSales.Report/definition/               # WORKED EXAMPLE (HUMAN Desktop save -- not agent-authored)
`-- pages/<id>/...                     # the empty Page 1 built into the approved 10-visual page in Power BI
                                       #   Desktop, saved as plain-text PBIR, committed as a reviewable git
                                       #   diff. One visual container per approved measure-bearing visual;
                                       #   model referenced by relative path (R1 passes).
```

**Structure Decision**:

1. **Workflow under the EXISTING F011A skill dir, not a new skill (O-1 default).** The
   procedure ships as `visual-implementation-review.md` ALONGSIDE `powerbi-handoff.md`
   under `.claude/skills/powerbi-dashboard-design/workflows/`, because the build is the
   natural continuation of surface 4 (the handoff) and reuses its inputs verbatim. This
   adds NO new top-level directory and NO new skill -- it extends the foundation that
   F011A already ships. If review prefers a standalone verb skill, that split is a later,
   separate, reversible decision recorded in tasks; this slice does not pre-empt it (the
   same posture F011A used for its router-vs-verb O-1).
2. **The trace template lives in the EXISTING `templates/` dir** as a generic copy-me
   blank, next to `visual-spec.yaml` / `dashboard-page-blueprint.yaml` -- the same
   "templates are generic blanks; instances live elsewhere" separation ADR 0003 and
   F011A already use. The filled instance lives in the per-subject-area working set
   (`mappings/retail_store_sales/design/`), parallel to its sibling design artifacts
   (the layout plan, visual list, binding map).
3. **The Dashboard Ready edit is an EVIDENCE-ITEM distinction, NOT a structural change.**
   It touches no gate, no status meaning, no blocking-reason list, no required-check
   table, no owner -- it only names the "design approved" vs "page implemented"
   distinction and the evidence string the existing owner may record. No second source
   of truth (Governance amendment clause).
4. **The only PBIR change is a HUMAN Desktop save**, committed as plain text under
   `powerbi/RetailStoreSales.Report/definition/`. The agent authors NO PBIR, hand-edits
   NO `report.json` / `diagramLayout.json`, and hand-authors NO visual-container JSON
   (FR-009) -- the reviewable diff comes from a real Desktop save, keeping the project
   openable per `pbip-workflow`.
5. **No `src/` change, no new `retail check` rule, no codegen, no CLI, no MCP call** --
   consistent with the all-skills verb architecture and roadmap rules 6 and 8. R1 already
   covers the relative model reference; this slice consumes it and adds nothing.

## Phasing

- **Phase 0 (research + decisions)**: none required as research -- the stage doc +
  readiness model + F011/012 binding map + F011A handoff notes + R1 + `pbip-workflow`
  are the authoritative inputs and already exist. Record the single open decision:

  - **O-1 (recorded, reversible default): does the implementation verification live as a
    new WORKFLOW alongside `powerbi-handoff.md`, or as a thin new VERB skill?**
    Recommended reversible default = **a new workflow ALONGSIDE `powerbi-handoff.md`**
    (`visual-implementation-review.md`), because the build is the natural continuation of
    surface 4 and reuses its inputs. If review prefers a standalone verb skill, the split
    is a later, separate decision captured in tasks -- this slice does not pre-empt it.

- **Phase 1 (author the generic artifacts)**: write the two generic deliverables and the
  one stage-doc edit (the workflow, the trace template, the Dashboard Ready
  evidence-item distinction). The boundary facts (the inherited rule-5 gate; the
  no-divergent-source-of-truth / evidence-item-only rule; the 1:1 trace definition with
  orphan/unmapped as blocking; the manual/no-publish boundary naming F016; the
  build-it-in-Desktop, never-hand-edit-Desktop-files rule) are FIXED FIRST (a
  foundational step in tasks) and reused verbatim across the workflow and the template.

- **Phase 2 (build the worked example + trace)**: a HUMAN builds the
  `retail_store_sales` empty Page 1 into the approved 10-visual page in Power BI Desktop,
  saves as plain-text PBIR, and commits `definition/`; the agent then produces the filled
  `visual-implementation-trace.md` (each built measure-bearing visual -> its one approved
  contract + mapped field + PASS), with the discount row showing the corrected 50.37%
  framing + the 33.39%/33.55% caveats. The reviewer reads the page diff + the trace in git.

- **Phase 3 (verify)**: run the fixture + deterministic checks (Testing above): the gate
  fixture (SC-003), the orphan/unmapped trace fixture (SC-002), the boundary fixture
  (SC-004), the C086-leakage grep (SC-006), the discount-rate grep (SC-007), `retail
  check` exit 0 with unchanged rule count (SC-005), and the 0-automation grep (SC-004).
  Re-run the Constitution Check (expected to stay PASS -- no new gate, no new rule, no
  data edit, no automation).

- **Phase 4 (tasks)**: enumerated in `tasks.md` (speckit-tasks output).

## Complexity Tracking

> No items to justify. The slice adds NO new top-level directory (the workflow extends
> the existing F011A skill; the template extends the existing `templates/`; the trace
> instance extends the existing `mappings/<subject>/design/` working set), NO new
> dependency, NO new gate/status/rule, NO data write, and NO automation. It passed 9/9 +
> spine + roadmap rules with no deviation -- unlike F011A (017), which introduced new
> top-level directories and recorded that single justification here.

## Post-Design Constitution Re-Check

To be re-evaluated after Phase 1/2 artifacts are authored: expected to stay PASS (9/9 +
spine + roadmap rules). The Phase 1 artifacts are a workflow + a template + an
evidence-item doc edit that VERIFY and RECORD; the Phase 2 worked example is a human
Desktop save plus a filled trace. Together they add no code, no dependency, no data
write, no new gate/status/rule, no resolution of the deferred F016 decision, no automation
or publish, and no divergent source of truth. Recorded in tasks' final verification phase.
