# page-blueprint

Surface 1 (report visuals). This workflow turns a "design a new page / new
dashboard" request into a reviewable **page blueprint** -- a committed plan of
what the page answers, how it is laid out, and which approved contract + mapped
field each data-bound visual binds to. It produces a filled
`templates/dashboard-page-blueprint.yaml`, not a Power BI file. It designs the
page on paper; it edits no PBIP/PBIR and builds nothing in Power BI.

The router (`../SKILL.md`) opens this workflow for "New dashboard / page design"
and (with `visual-design-system.md`) for "Chart / card / slicer arrangement". Use
`visual-design-system.md` for chart-by-question/grain selection; use this file for
the page as a whole.

## The one load-bearing rule

**A page answers exactly ONE business question.** The business question is the
page's reason to exist; every section and every visual serves it. If a request
names two unrelated questions ("show sales AND inventory health"), that is two
pages -- split it, do not crowd one page.

Principle V STOP: if the request does NOT supply the page's business question,
ask for it. Never invent the question to fill a page (FR-009).

## Step 1 -- Gate check FIRST (before binding any data-bound visual)

Data-bound visuals (surface 1) are gated. Confirm the subject area's
`semantic_model_ready` is `pass` before binding any visual to a metric:

- **If `semantic_model_ready` is not `pass`:** bind NO data-bound visual. Record
  the page's `dashboard_ready` status as `blocked` (or `not_started` if the prior
  stage simply has not begun) with the blocking reason
  `"semantic_model_ready is not pass -- Dashboard Ready gate, rule 5"`, and route
  the request upstream to the metric-contract / semantic-model stage. STOP the
  data-bound part here.
- **You MAY still sketch the layout-only frame** while gated: the page's business
  question, audience, section vocabulary, canvas, grid, background reference, and
  theme reference carry structure and defaults, not data, so they are not gated.
  Leave every `visual.metric_contract` and `visual.fields` as a `<placeholder>`
  until contracts exist.
- **If `semantic_model_ready` is `pass`:** proceed to bind visuals (Step 4),
  citing approved contracts + mapped fields only.

The gate, the design-review sign-off, and `dashboard_ready: pass` are NOT defined
here -- see "The inherited gate" below.

## Step 2 -- Name the page (audience + question)

Fix three things before any layout:

- **Page name** -- short, generic (`<page_name>`), Windows-path-safe.
- **Audience** -- who reads it (executive / branch manager / analyst). Audience
  sets density: an executive page uses FEWER visuals; an analyst page may carry
  detail.
- **Business question** -- the single question the page answers, in one sentence.

## Step 3 -- Lay out the seven sections

A page is composed from this section vocabulary. Use these exact names and this
order; a page uses the sections it needs and omits the rest (an executive summary
rarely needs an exception-detail table).

| Section | What goes here |
|---------|----------------|
| header | page title (static text), date-context label, branding -- the orientation strip |
| KPI strip | the few headline KPIs as cards, each with a comparison/context, answering the page question at a glance |
| main insight | the primary chart that carries the page's story (the trend/comparison the question asks about) |
| diagnostic | the "why" visuals -- breakdowns by category/branch/time that explain the main insight |
| exception-detail | the detail table/matrix for drill -- detail, NOT the executive headline (tables are for detail, not executive insight) |
| filter rail | slicers and filters, kept to the side so they do not dominate the canvas |
| footer-status | data-as-of / refresh note / data-quality flag -- the trust strip, static text only |

Layout discipline (generic, from the design principles in
`../../../docs/powerbi/visual-design-system.md`): every KPI carries a comparison
or context; executive pages use fewer visuals; the filter rail does not dominate;
the exception-detail table is never the page's main visual; number formats and
category colors are consistent across the page.

## Step 4 -- Fill `templates/dashboard-page-blueprint.yaml`

Copy the blank `templates/dashboard-page-blueprint.yaml` and fill it. Walk its
fields:

| Field | How to fill it |
|-------|----------------|
| `page` | the page name (`<page_name>`), generic and path-safe |
| `audience` | who reads it (executive / branch manager / analyst) |
| `business_question` | the single question the page answers (Step 2) |
| `readiness_dependencies` | the readiness stages this page depends on (e.g. `semantic_model_ready: pass`) -- a REFERENCE to state, not a copy of it |
| `required_metric_contracts` | the approved metric contracts each visual binds to, BY NAME/PATH (REFERENCE) -- never an inlined metric formula or DAX |
| `required_semantic_model_contract` | the governed semantic model the page reads, BY PATH (REFERENCE) -- never an embedded model definition |
| `background` | the background asset by PATH (surface 2) -- structure only, no baked-in data |
| `theme` | the theme JSON by PATH (surface 3) -- defaults only, no business meaning |
| `canvas` | canvas size (e.g. `16:9`) -> `../../../design/grids/16x9-grid.yaml` |
| `grid` | the grid + safe zones the visuals snap to |
| `sections` | the Step-3 sections this page uses, in order |
| `visuals` | one entry per visual: id / type / the question it answers / `metric_contract` (REFERENCE, one approved contract) / `fields` (mapped semantic-model fields) / position / number format -- one `templates/visual-spec.yaml` per visual for the detail |
| `slicers` | the filter-rail slicers (which field, default selection) |
| `tooltips` | tooltip behavior per visual (what context a hover adds) |
| `mobile` | what survives to phone (KPI strip + top insight) -> `mobile-layout.md` |
| `qa` | the QA rules to check before handoff -> `dashboard-qa.md` |

**Reference, never embed (FR-002, US3).** The blueprint REFERENCES contracts,
the semantic model, the background, and the theme by name/path. It NEVER inlines a
metric formula, DAX, a theme color, or a model definition. The metric lives in its
contract (F009); the field lives in the governed model (F010); the blueprint only
points at them.

**Each data-bound visual cites exactly one approved contract + one mapped field:**

- A visual with no backing approved contract is an **orphan** -- do NOT emit it;
  record `"orphan visual: no contract for <question>"` as a blocking reason. The
  blueprint never invents a metric to fill a card.
- A visual using a field not in the governed semantic model is **unmapped** --
  do NOT design around it; record `"unmapped field: <field>"` and STOP that visual.

For the worked starters of this shape, read the four
`../../../reports/blueprints/*.yaml` (executive-summary, branch-performance,
product-mix, data-quality-control-room) -- each is a generic placeholder page, not
a concrete metric.

## Step 5 -- Record readiness and STOP

Record the page's `dashboard_ready` readiness consistent with the readiness model
(four statuses + `evidence[]` + `blocking_reasons[]`). The blueprint is a design
proposal; it does not grant its own pass. Hand the filled blueprint + per-visual
specs to the design reviewer. STOP at the handoff boundary -- this workflow edits
no PBIP/PBIR file and builds nothing in Power BI (that is `powerbi-handoff.md` ->
F016).

## The inherited gate

No data-bound dashboard design before the subject area semantic_model_ready is pass (roadmap
rule 5). This feature DEFINES NO new gate and is NOT a second source of truth: the gate, the
design-review sign-off, and the dashboard_ready: pass are owned by docs/readiness/dashboard-ready.md
and the F011/012 dashboard-design verb (spec-only today). This feature documents and reuses them.

Record readiness with the four statuses (`not_started` / `blocked` / `warning` /
`pass`) plus `evidence[]` and `blocking_reasons[]` only -- never a numeric score,
and never self-grant `dashboard_ready: pass` (that is the verb owner's recorded
design-review).

## See also

- The router + the four-surface table: `../SKILL.md`.
- Chart-by-question/grain selection (the visuals this page holds):
  `visual-design-system.md`.
- The QA reference run before handoff: `dashboard-qa.md`.
- Phone layout: `mobile-layout.md`.
- The blueprint template this workflow fills:
  `../../../templates/dashboard-page-blueprint.yaml`; the per-visual detail:
  `../../../templates/visual-spec.yaml`.
- How a blueprint is read + the four starters' index:
  `../../../docs/powerbi/dashboard-blueprints.md`.
- The starter blueprints (generic examples): `../../../reports/blueprints/*.yaml`.
- The stage this backs + the readiness model:
  `../../../docs/readiness/dashboard-ready.md`,
  `../../../docs/readiness/readiness-model.md`.
