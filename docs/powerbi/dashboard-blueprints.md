# Dashboard Blueprints

How a page blueprint is read, the section vocabulary it uses, and an index of the
four starter blueprints in `reports/blueprints/`.

A page blueprint is the durable design intent for ONE dashboard page: who it is
for, the single business question it answers, the upstream contracts it depends
on, and the sections and candidate visuals that fill it. It is surface 1 (report
visuals) design intent -- it is NOT the report (that is built later, F016), NOT a
metric definition (that is F009), and NOT a theme or a background (surfaces 3 and
2). This doc explains how to read one; it does not author a specific page (that is
the `dashboard-design` verb's job) and does not restate the template (see the
copy-me blank `templates/dashboard-page-blueprint.yaml`).

## How a page blueprint is read

A blueprint is read top-down as REFERENCES, never as embedded definitions. Each
section below says what it carries and -- the load-bearing rule -- what it points
AT instead of inlining.

| Field | What it carries | The reference rule |
|-------|-----------------|--------------------|
| audience | who reads this page (executive, branch manager, analyst) | plain text -- describes the reader, invents no metric |
| business question | the ONE question the page answers | a question, not a formula; a page that answers two questions is two pages |
| readiness dependencies | the upstream stage(s) that must be `pass` first | names the stage (`semantic_model_ready`), never re-states the gate |
| required metric contracts | the approved contracts each KPI/visual binds to | REFERENCE by contract name -- never an inlined metric formula or DAX |
| required semantic model contract | the governed model the visuals read fields from | REFERENCE by name/path -- never a copied relationship or column definition |
| background asset | the static canvas behind the page, if any | REFERENCE by path -- the image is surface 2 (structure, not data) |
| theme JSON | the default palette/fonts/formatting | REFERENCE by path -- the theme is surface 3 (defaults, not meaning) |
| sections | the page layout in the section vocabulary (below) | the ordered regions of the page |
| candidate visuals | the visuals proposed per section | each data-bound visual cites one contract + a mapped field |
| QA rules | the anti-patterns to check this page against | names the rule; the reference list lives in `visual-qa.md` |

The single discipline a blueprint encodes: it REFERENCES its contracts, model,
theme, and background by name/path -- it never embeds a metric formula, a DAX
expression, a relationship, or a theme color. A blueprint that inlines a metric
has crossed into F009's territory; a blueprint that inlines theme colors has
crossed into surface 3. Keep them as references.

### The contracts-first gate still applies

A page blueprint describes data-bound visuals (surface 1), so it inherits the
Dashboard Ready gate: no data-bound dashboard design before the subject area's
`semantic_model_ready` is `pass`. A blueprint may be authored as GENERIC
reference (placeholders, no concrete metric) at any time -- the four starters in
`reports/blueprints/` are exactly that -- but a blueprint filled for a SPECIFIC
subject area is gated. This doc does not re-define that gate: it is owned by
`docs/readiness/dashboard-ready.md` and the `dashboard-design` verb. See that
stage doc for the gate, its statuses, and the design-review sign-off.

## Section vocabulary

A page is laid out in the SAME named sections the `page-blueprint.md` workflow and
the `templates/dashboard-page-blueprint.yaml` template use -- this is an index of
that one vocabulary, not a second definition of it. The seven sections, in
top-to-bottom reading order:

| Section | What it holds |
|---------|---------------|
| header | page title, date/period context, the audience cue -- static structure, no live KPI baked into a background |
| KPI strip | the few headline KPIs, each with a comparison (vs prior period / target) -- every KPI cites one contract |
| main insight | the one primary visual that answers the page's business question |
| diagnostic | the supporting visuals that explain the main insight (the "why") |
| exception-detail | the drill/detail (table or matrix) for the rows that need attention -- detail, not the executive headline |
| filter rail | the slicers/filters; kept to the side so they do not dominate the canvas |
| footer-status | data-as-of, refresh note, and any data-quality flag -- never the page's main content |

Not every page uses every section -- an executive summary leans on header + KPI
strip + main insight; a control room leans on exception-detail + footer-status.
The vocabulary is the shared menu; the blueprint records which sections a given
page uses and in what order.

## The four starter blueprints

Four generic starter blueprints ship in `reports/blueprints/`. Each is a GENERIC
reference (audience + business question + required contracts and model
dependencies as PLACEHOLDERS + sections + candidate visuals + QA rules); each
invents no concrete business metric beyond a named placeholder. They are starting
points to copy and fill for a specific subject area -- not finished pages.

| Blueprint | Audience | The business question it answers (generic) |
|-----------|----------|--------------------------------------------|
| `reports/blueprints/executive-summary.yaml` | executive / leadership | How is overall performance this period versus the prior period and target? |
| `reports/blueprints/branch-performance.yaml` | regional / branch manager | How do locations (branches/stores) compare, and which are over- or under-performing? |
| `reports/blueprints/product-mix.yaml` | merchandising / category analyst | How is the mix across product categories shifting, and where is it concentrated? |
| `reports/blueprints/data-quality-control-room.yaml` | data steward / analyst | Is the data behind these dashboards trustworthy -- what is fresh, complete, and reconciled? |

The business questions above are generic placeholders that describe the page's
purpose; they are NOT metric definitions. The concrete metric a visual binds to
comes from an approved contract (F009), referenced by name in the blueprint -- the
blueprint never defines it.

## See also

- `templates/dashboard-page-blueprint.yaml` -- the copy-me blank a blueprint fills.
- `.claude/skills/powerbi-dashboard-design/workflows/page-blueprint.md` -- the
  workflow that authors a page from the vocabulary above (surface 1).
- `docs/powerbi/visual-design-system.md` -- the four surfaces and the Power BI
  design principles.
- `docs/powerbi/visual-qa.md` -- the anti-pattern reference the QA rules name.
- `docs/readiness/dashboard-ready.md` -- the stage and the contracts-first gate
  (owner of the gate; this doc reuses it, does not re-define it).
- `reports/blueprints/executive-summary.yaml`,
  `reports/blueprints/branch-performance.yaml`,
  `reports/blueprints/product-mix.yaml`,
  `reports/blueprints/data-quality-control-room.yaml` -- the four starters indexed
  above.
