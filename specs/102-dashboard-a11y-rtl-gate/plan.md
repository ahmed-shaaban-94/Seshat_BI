# Implementation Plan: Dashboard Accessibility + RTL/Arabic Readiness Checklist

**Branch**: `102-dashboard-a11y-rtl-gate` | **Date**: 2026-07-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/102-dashboard-a11y-rtl-gate/spec.md`

## Summary

Turn a11y (WCAG contrast, colorblind-safe palette) and RTL/Arabic layout
readiness from PROSE GUIDANCE into a REQUIRED, REVIEWED Dashboard-Ready
(Stage 6) evidence item: a generic, per-page checklist template
(`templates/a11y-rtl-readiness-checklist.md`) covering exactly three
dimensions -- WCAG contrast (citing CT1's already-shipped result, never
re-derived), colorblind-safe palette separation (reviewed against a fixed
generic criteria list), and RTL/Arabic layout readiness (reviewed against a
fixed generic criteria list). The fixed criteria for the latter two
dimensions are documented ONCE, as a new section extending
`docs/powerbi/visual-design-system.md`'s existing "Accessible contrast"
principle, and cited by every filled checklist (never re-authored per page).
The checklist is cited as a required `evidence[]` item on the EXISTING
`dashboard_ready` gate (`docs/readiness/dashboard-ready.md`), following the
F034 "design approved vs page implemented" precedent verbatim: no new
status, no new readiness stage, and no new `retail check` rule id (the spec
explicitly declined the offered HR10 reservation, reasoning that a second
rule recomputing CT1's contrast math over a different file name would be the
duplicate-surface problem the Collision-Avoidance guard exists to prevent).
The feature is docs/template-only -- it authors static artifacts and stops;
it never renders, opens, publishes, or connects to Power BI (F016 remains
gated and unbuilt) and emits no numeric score anywhere (hard rule #9). Two
Principle-V judgment calls (RTL-dimension applicability default;
block-vs-warning pass-bar severity) are raised to a named human and are NOT
resolved by this plan.

## Technical Context

**Language/Version**: N/A -- agent-authored Markdown/prose artifacts only
(a generic template, a prose-doc extension, a stage-doc evidence-item edit,
a worked-example filled instance). No Python module, no new dependency. The
agent is the runtime that fills the checklist per page, the same posture as
`source-mapping`, `retail-build-warehouse`, and the F034
visual-implementation-review workflow.

**Primary Dependencies**: None new. This feature CONSUMES (never
re-implements) the already-shipped CT1 rule
(`src/retail/rules/design_contrast.py`) as its contrast-dimension citation
source, the F034 template shape (`templates/visual-implementation-trace.md`)
as its structural precedent, and the `dashboard-qa.md` <->
`docs/powerbi/visual-qa.md` catalog/prose-home split as its
criteria-documented-once precedent. No `pbi-cli`, no Power BI MCP, no
network, no DB driver, no new Python.

**Storage**: Committed text only. A new generic template under `templates/`,
a new prose section appended to an existing `docs/powerbi/` file, an
additive edit to an existing `docs/readiness/` stage doc, and one filled
worked instance under the existing `mappings/retail_store_sales/design/`
co-location directory. No database writes, no PBIR generation, no schema
change, no runtime executor.

**Testing**: Doc/fixture review, matching the F034 precedent's docs-slice
testing posture (no new pytest surface -- this is not a rule module):
(a) a deterministic grep proving the template contains no C086/pharmacy
domain noun and no literal Arabic string (SC-004, FR-013, FR-009); (b) a
grep proving the template and every filled instance carry no numeric
confidence/health/maturity/completeness field (SC-003, FR-012); (c) a
manual walkthrough filling the worked-example checklist for
`retail_store_sales` and confirming each dimension traces to a real,
confirmed-present repo-relative path (SC-006): the token file
(`design/tokens/tower-retail-design-tokens.yaml`), the theme file
(`themes/tower-retail.theme.json`), and the page layout artifact
(`mappings/retail_store_sales/design/dashboard-layout.md`); (d) a check
that `retail check`'s rule count and rule-id set are UNCHANGED before/after
this feature (SC-005), the same assertion F034 made for its own additive
evidence-item edit; (e) ASCII + UTF-8-no-BOM verification on every authored
file (FR-013, Principle IX).

**Target Platform**: The Claude Code agent in this repo (Windows; 260-char
path budget). All new repo-relative paths kept short.

**Project Type**: Docs/template slice (Layer 6 Dashboard & Delivery),
single repo. Not a library/web-service/app; no `src/` change.

**Performance Goals**: N/A -- a template, a prose-doc extension, a
stage-doc evidence-item edit, and a worked instance, not a runtime service.

**Constraints**: ASCII + UTF-8 no BOM (no literal Arabic string in the
GENERIC template; a real Arabic example, if any, lives only in a filled
per-page instance -- FR-013); generic (Principle VII: no C086/pharmacy
specifics baked into the template or the criteria doc -- FR-009); no real
host/DSN/secret in any output (Principle IX); never renders/opens/publishes
Power BI or connects to a live semantic model (FR-002, Principle VIII;
F016 stays gated and unbuilt); adds NO new `retail check` rule id, NO new
readiness stage, NO new `dashboard_ready` status value (FR-008); never
self-grants `dashboard_ready: pass` (the checklist is evidence FOR the
existing BI/report-owner sign-off, never a substitute for it); the contrast
dimension never re-derives a ratio that could contradict CT1's registered
finding (FR-003/FR-004).

**Scale/Scope**: One new generic template
(`templates/a11y-rtl-readiness-checklist.md`), one additive prose-section
extension to `docs/powerbi/visual-design-system.md` (the fixed,
generic colorblind-safe + RTL/Arabic review criteria, documented once), one
additive `evidence[]`-item edit to `docs/readiness/dashboard-ready.md`
(mirroring the F034 "design approved vs page implemented" precedent's
shape, verbatim pattern), and one worked-example filled instance under
`mappings/retail_store_sales/design/`. No `src/` file, no new dependency,
no new top-level directory.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design
(below). Source: `.specify/memory/constitution.md`.*

| Principle | How this feature complies |
|-----------|----------------------------|
| I. Agent-First, Gate-Enforced | The checklist is enforced the SAME way F034's "page implemented" evidence item is enforced today: by the EXISTING human design-review sign-off gate on `dashboard_ready`, which already fails closed (a missing/unfilled checklist is a recorded `blocking_reasons[]` entry, not a soft note -- FR-007). No new mechanical rule is added, but the fail-closed property is preserved: an absent or partially-unfilled checklist blocks `pass` exactly as an orphan visual does today. The agent is not the authority on whether the checklist counts as filled -- the design-review sign-off (a named human) is. |
| II. Depend, Never Fork | No fork, no vendored engine, no Power BI Desktop automation, no `retail` CLI subcommand. The checklist CITES CT1's already-shipped result rather than re-implementing contrast math (US2) -- the definition of depend-not-duplicate applied to a static rule's output. |
| III. Medallion, Postgres-First, Gold-Only | Unaffected. This feature touches no schema, no SQL, no `gold`/`silver`/`bronze` table. It operates entirely on Stage 6 design/theme artifacts. |
| IV. Source Mapping Before Silver | Unaffected; no interaction with the source-mapping gate. |
| V. Agent Stops at Judgment Calls | The two business-policy questions the spec raises (Q-FR014-SCOPE: is RTL review in-scope-by-default or out-of-scope-by-default; Q-FR014-SEVERITY: does an open finding block or only warn) are carried forward as OPEN in `## Clarifications` and are NOT answered by this plan, the template, the criteria doc, or the stage-doc edit. The template's not-applicable-with-reason field for the RTL dimension requires an EXPLICIT human LTR-only ruling citation per page -- it does not default any page out of scope on its own authority. The severity field records "at minimum a warning-class finding," leaving the blocked-vs-warning escalation for the pending owner ruling, per the spec's own interim floor. |
| VI. Defaults Then Deviations | Two NON-Principle-V defaults are adopted and recorded here (mirroring the spec's own Clarifications C1/C2 pattern): (a) the fixed criteria are documented once by extending `docs/powerbi/visual-design-system.md` rather than forking a new doc (R4, research.md); (b) the contrast-dimension token-file citation is resolved via the EXISTING `mappings/<subject>/design/` co-location convention F034 already established (R5, research.md; Clarifications C1). Both are reversible, plan-time shape choices, not judgment calls about business meaning. |
| VII. C086 Is An Example, Not The Schema | The template, the extended criteria prose, and the stage-doc edit are generic: placeholders only, no C086/pharmacy/retail_store_sales domain noun, color literal, or grain key. The worked-example filled instance (the ONE place real values appear) lives under `mappings/retail_store_sales/design/`, cited, never inlined into the generic artifacts (FR-009, SC-004). |
| VIII. Static-First Governance, Live Deferred | The entire feature is static: it reads already-committed YAML/JSON/Markdown and writes derived Markdown evidence. It never renders, opens, publishes, or connects to Power BI Desktop, a live semantic model, or F016 (which remains gated and unbuilt) -- FR-002. Colorblind-safe and RTL/Arabic legibility are explicitly NOT mechanically verifiable from static text without rendering the report (spec Assumptions); this feature is therefore a documented review checklist, never a `retail check` rule, until/unless a future CVD-simulation rule is separately specified and ruled non-duplicative. |
| IX. Secrets and Reproducibility | No real host/DSN/secret in any authored artifact. All new/edited files are ASCII, UTF-8 without BOM; the generic template carries no literal Arabic string (a real Arabic example, if any, lives only in a filled per-page instance) -- FR-013. Repo-relative paths stay short. |
| Hard rule #9 (no fabricated score) | The checklist records each dimension as `reviewed-clean` / `not-applicable-with-reason` / `blocked` ONLY -- no numeric confidence/health/maturity score, no completeness count, anywhere in the template, the criteria doc, the stage-doc edit, or the worked instance (FR-012, SC-003). |

**Readiness System (spine) compliance** -- this feature is Layer 6 /
Dashboard Ready and MUST NOT weaken the spine:

- Adds NO new gate, NO new readiness stage, NO new readiness status, NO new
  `retail check` rule (FR-008; SC-005 verified before/after against the
  rule registry and `readiness-model.md`). `dashboard_ready`'s existing gate
  (design review: every visual maps to an approved contract) and its
  existing owner (BI/report owner) are UNCHANGED; this feature adds ONLY an
  `evidence[]` item under that existing owner, the same non-disruption
  guarantee F034 already demonstrated for its own evidence item.
- Records readiness with the four existing statuses + `evidence[]` +
  `blocking_reasons[]` only, never a fabricated score (hard rule #9), and
  never self-grants `dashboard_ready: pass` -- `pass` stays the BI/report
  owner's recorded design-review action, now additionally evidenced by a
  filled checklist.

**Collision-Avoidance compliance** (per this feature's non-negotiable
allocation): NO static-rule id is reserved (HR10 declined, per the spec's
own "Rule-id reservation decided against CT1" section). This feature adds a
Dashboard-Ready checklist evidence item only. It touches no shared schema,
no rule registry, no golden record, and stays DISTINCT from the theme-json
purity linter (spec 060, forbidden-KEY scan) by reviewing LEGIBILITY of
declared colors/layout, never which keys a theme file may contain.

**Result**: PASS (9 principles + hard rule #9 + spine + Collision-Avoidance).
No violations requiring justification. Complexity Tracking omitted below.

## Project Structure

### Documentation (this feature)

```text
specs/102-dashboard-a11y-rtl-gate/
|-- spec.md              # the feature spec (already clarified; committed)
|-- plan.md              # this file
|-- research.md          # Phase 0 output
|-- data-model.md        # Phase 1 output
|-- quickstart.md        # Phase 1 output
`-- tasks.md             # Phase 2 output (/speckit-tasks -- NOT produced by this stage)
```

No `contracts/` directory: this feature defines no API/service contract and
no rule behavioral contract (unlike spec 060's `contracts/rule-contract.md`,
which exists because 060 adds a rule). The "contract" here is the checklist
template's shape itself, fully specified in `data-model.md`.

### Source / deliverable manifest (repository root)

Real repo paths this feature adds or edits. Generic artifacts carry
placeholders only; worked values live in the per-subject-area instance.

```text
templates/
`-- a11y-rtl-readiness-checklist.md   # NEW generic copy-me blank (Principle VII): the per-page
                                       #   checklist -- three dimensions (contrast, colorblind-safe,
                                       #   RTL/Arabic), each recorded reviewed-clean /
                                       #   not-applicable-with-reason / blocked with a citation to its
                                       #   evidence source; the readiness-status header (four statuses +
                                       #   evidence[] + blocking_reasons[]); a FORBIDDEN OPERATIONS
                                       #   section (no render/open/publish/connect -- F016 named); a
                                       #   stop-and-ask section for the two OPEN Principle-V questions.
                                       #   Placeholders only -- no C086/retail_store_sales value, no
                                       #   literal Arabic string.

docs/powerbi/
`-- visual-design-system.md           # EDIT (additive prose-section extension only): adds a new
                                       #   "Colorblind-safe palette separation" and "RTL/Arabic layout
                                       #   readiness" criteria subsection alongside the EXISTING
                                       #   "Accessible contrast" paragraph (~line 90). Documents the
                                       #   fixed, generic review criteria ONCE (FR-005/FR-006/FR-009),
                                       #   referenced by every filled checklist -- never restated or
                                       #   reinvented per page. No new file; no change to any other
                                       #   section's meaning.

docs/readiness/
`-- dashboard-ready.md                 # EDIT (additive evidence-item only, mirroring the F034 "design
                                       #   approved vs page implemented" precedent verbatim): a new
                                       #   "Evidence item: a11y/RTL readiness checklist" subsection
                                       #   naming the checklist as a REQUIRED evidence[] item before
                                       #   dashboard_ready may record pass, and the interim severity
                                       #   floor from Q-FR014-SEVERITY (at minimum a warning-class
                                       #   finding, escalation to blocked pending the owner ruling). NO
                                       #   new status, NO new gate, NO new retail check rule, NO change
                                       #   to the existing owner, required checks, or blocking-reasons
                                       #   shape (FR-008).

mappings/retail_store_sales/design/                        # EXISTING co-location dir (confirmed present)
`-- a11y-rtl-readiness-checklist.md    # NEW worked-example FILLED instance: the retail_store_sales
                                       #   executive page's checklist, citing design/tokens/
                                       #   tower-retail-design-tokens.yaml + its current CT1 result for
                                       #   the contrast dimension, themes/tower-retail.theme.json's
                                       #   dataColors for the colorblind-safe dimension, and
                                       #   mappings/retail_store_sales/design/dashboard-layout.md for
                                       #   the RTL/Arabic layout dimension. Real values live ONLY here.
```

**Structure Decision**:

1. **The checklist template lives in the EXISTING `templates/` dir**, next
   to `visual-implementation-trace.md`, `visual-contract-binding-map.md`,
   and `visual-spec.yaml` -- the same "templates are generic blanks;
   instances live in `mappings/<subject>/design/`" separation ADR 0003 and
   F034 already use. No new top-level directory.
2. **The fixed criteria are documented ONCE by extending an EXISTING doc**
   (`docs/powerbi/visual-design-system.md`), not by forking a new
   `docs/powerbi/a11y-rtl-criteria.md` file (R4, research.md). This keeps
   one prose home for design-legibility principles and reuses the
   `dashboard-qa.md` <-> `visual-qa.md` catalog/prose-home split already
   proven, satisfying User Story 3's "same generic template ... same fixed
   review-criteria list" requirement without adding a new document surface.
3. **The Dashboard Ready edit is an EVIDENCE-ITEM addition, NOT a
   structural change** -- identical in kind to F034's own edit to the same
   file. It touches no gate, no status meaning, no blocking-reason list
   shape, no required-check table, no owner. It only names the checklist as
   a required `evidence[]` item and records the interim severity floor the
   spec's Q-FR014-SEVERITY section already states pending the owner ruling.
   No second source of truth is created (Governance amendment clause).
4. **The worked instance lives in the EXISTING co-location directory**
   `mappings/retail_store_sales/design/`, parallel to its sibling design
   artifacts (`dashboard-layout.md`, `visual-contract-binding-map.md`,
   `visual-list.md`) and to where `visual-implementation-trace.md`'s own
   filled instance would land -- reusing the SAME resolution convention
   FR-015/Clarifications C1 specify, introducing no new lookup mechanism.
5. **No `src/` change, no new `retail check` rule, no rule-registry
   wiring, no golden-record regeneration, no CLI, no MCP call** -- the
   defining structural difference from spec 060 (see research.md R1). This
   is the SCOPE GUARD's non-negotiable: a Dashboard-Ready checklist
   evidence item, not a static rule.

## Phasing

- **Phase 0 (research)**: see `research.md`. Confirms the F034 structural
  precedent (not spec 060's rule-wiring shape), surveys the shipped
  artifacts this feature reuses and stays distinct from, confirms every
  cited path is real (not fictional), and records the two OPEN Principle-V
  questions as carried-forward, not resolved.

- **Phase 1 (design)**: see `data-model.md` and `quickstart.md`. Defines the
  checklist's three-dimension shape, the contrast-citation mechanic (cite
  CT1, never recompute), the not-applicable-with-reason escape hatch, and
  the criteria-doc-extension shape. Authors the four deliverables named in
  Project Structure above: the generic template, the criteria-doc
  extension, the stage-doc evidence-item edit, and the worked instance.

- **Phase 2 (tasks)**: enumerated in `tasks.md` (`/speckit-tasks` output;
  not produced by this stage). Expected ordering: (1) write the fixed
  criteria extension to `visual-design-system.md`; (2) write the generic
  template citing that extension + CT1's contract; (3) edit
  `dashboard-ready.md`'s evidence-item section; (4) fill the worked
  instance for `retail_store_sales`, running CT1 (`retail check`) to obtain
  its real current finding for `design/tokens/tower-retail-design-tokens.yaml`
  before citing it; (5) run the deterministic checks (ASCII/no-BOM, no
  C086-leakage in generic files, no numeric-score field anywhere, `retail
  check` rule count unchanged).

## Post-Design Constitution Re-Check

Expected to stay PASS (9 principles + hard rule #9 + spine +
Collision-Avoidance) after Phase 1 authoring: the planned artifacts add no
code, no dependency, no rule id, no new gate/status, no data write, and no
automation; both OPEN Principle-V questions remain unresolved in every
authored artifact; every worked-example citation traces to a confirmed real
path. Re-verified in tasks' final verification phase (see Phasing above).

## Complexity Tracking

Not applicable -- Constitution Check has no violations. The feature adds no
new top-level directory (the template extends `templates/`; the criteria
extend an existing `docs/powerbi/` file; the stage-doc edit extends an
existing `docs/readiness/` file; the worked instance extends the existing
`mappings/retail_store_sales/design/` directory), no new dependency, no new
gate/status/rule, no data write, and no automation.
