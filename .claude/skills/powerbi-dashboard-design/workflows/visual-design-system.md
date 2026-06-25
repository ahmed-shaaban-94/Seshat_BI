# visual-design-system (surface 1: report visuals)

Surface 1 of the four-surface router (`../SKILL.md`). This workflow covers the
live, data-bound report objects -- cards, charts, slicers, tables/matrices,
tooltips, bookmarks, titles, interactions -- and how to CHOOSE the right object
for a business question at a given grain. It is the arrangement-and-selection
procedure the router opens for "chart / card / slicer arrangement"; it pairs with
`page-blueprint.md` (which arranges these objects into a page that answers one
business question).

## Scope (read first)

This workflow SELECTS and SPECIFIES report visuals; it does not author them in
Power BI (that is F016) and it does not define a metric (that is F009). Every
data-bound visual it specifies cites one approved metric contract by name AND a
mapped semantic-model field -- nothing invented, nothing unmapped. It binds
visuals only against contracts that already exist; if they do not, the inherited
gate below applies and this workflow STOPS.

## The inherited gate

No data-bound dashboard design before the subject area semantic_model_ready is pass (roadmap
rule 5). This feature DEFINES NO new gate and is NOT a second source of truth: the gate, the
design-review sign-off, and the dashboard_ready: pass are owned by docs/readiness/dashboard-ready.md
and the F011/012 dashboard-design verb (spec-only today). This feature documents and reuses them.

Every visual specified here is data-bound (surface 1), so the gate applies in
full: do not specify a single data-bound visual until the subject area's
`semantic_model_ready` is `pass`. Pure-styling concerns (a card's corner radius
default, a page's wallpaper) are theme/background work and belong to surfaces 2/3
(`background-asset-design.md`, `theme-json-design.md`), not here.

## The contract + field rule (every data-bound visual)

Each data-bound visual MUST trace to both:

1. **one approved metric contract** (F009), cited BY NAME -- never an inline
   formula, never DAX, never an invented metric; and
2. **a field present in the governed semantic model** (F010) -- the dimension and
   any measure the visual displays must already be mapped.

When either is missing, do NOT design around it -- record the blocking reason and
STOP the visual:

- No backing contract -> record `orphan visual: no contract for <question>` and
  emit no visual (the foundation never invents a metric to fill a card).
- A field not in the governed model -> record `unmapped field: <field>` as a
  blocking reason and STOP -- bind only to mapped fields.

Reference contracts and fields by placeholder name (e.g. `<sales_amount>`,
`<branch>`, `<period>`); this workflow is generic and inlines no concrete metric
definition.

## The report-visual objects (surface 1)

| Object | What it is for | Binds to |
|--------|----------------|----------|
| Card / KPI card | one headline number + its comparison/context | one metric contract; a period/comparison field |
| Multi-row card | a small set of related headline numbers | one contract per number |
| Column / bar chart | compare a measure ACROSS a category | one metric contract; one category field |
| Line / area chart | a measure OVER time | one metric contract; a date/period field |
| Combo chart | two related measures at the same grain (e.g. value + rate) | two metric contracts; one shared category/period field |
| Donut / pie | part-to-whole at low category count (use sparingly) | one metric contract; one low-cardinality category |
| Scatter | relationship between two measures across items | two metric contracts; one item-grain field |
| Map | a measure across a geographic field | one metric contract; one geo field in the model |
| Table | row-level DETAIL, many columns, exact values | mapped fields; not for executive insight |
| Matrix | a measure across two crossed dimensions (rows x columns) | one+ contracts; two category fields |
| Slicer | a filter control on the page | a mapped dimension field (carries no metric) |
| Tooltip | on-hover context for a visual (default or report-page tooltip) | the visual's contract + supporting context fields |
| Bookmark | a saved view/state (filter set, drill state, toggle) | references visuals; defines no metric |
| Title / subtitle | static label naming the visual's question | static text (no dynamic KPI baked in -- that is a measure, not a title) |
| Interaction (cross-highlight / cross-filter) | how selecting in one visual affects others | set per page; default to cross-highlight, justify cross-filter |

A slicer carries a dimension, never a metric. A title is static text -- a number
that should update is a card/measure, not a baked-in title string.

## Chart selection by business question + grain

Choose the object from the QUESTION the visual answers and the GRAIN of its
contract/field, not from preference. Defaults below; a deviation is a
`warning`-class design note with a reason (Principle VI), surfaced for review.

| The question the visual answers | Grain | Default object |
|---------------------------------|-------|----------------|
| "What is the headline number now, vs a comparison?" | one value + one comparison | KPI card (with comparison/context) |
| "How does this measure compare ACROSS categories?" | measure x one category | column/bar chart (sorted) |
| "How does this measure move OVER time?" | measure x date/period | line chart |
| "How do two related measures move together?" | two measures x shared period | combo chart |
| "What is the part-to-whole split?" (few parts) | measure x low-cardinality category | donut/pie (only if few categories) |
| "Where does a measure concentrate geographically?" | measure x geo field | map |
| "What are the exact row-level values?" | row detail | table (detail page, not the executive page) |
| "How does a measure vary across TWO dimensions?" | measure x two categories | matrix |
| "Is there a relationship between two measures?" | two measures x item grain | scatter |
| "Let the user narrow the page" | a dimension | slicer (kept off to the side, not dominating) |

Grain guidance:

- Match the visual's grain to the contract's grain. A measure defined at one
  grain shown against a finer field is a grain mismatch -- record it as a
  `warning`-class note and surface it, do not silently reshape the data.
- A category with high cardinality belongs in a sorted bar/column or a table, not
  a pie/donut.
- A KPI card always carries comparison/context (vs prior period, vs target) -- a
  bare number with no comparison is an anti-pattern (see `dashboard-qa.md`).

## How to specify a visual

For each chosen visual, fill `../../../../templates/visual-spec.yaml` (copy the
blank): visual id, type, the business question it answers, the metric contract
(reference by name), the mapped semantic-model fields, position, formatting rules,
interactions, tooltip behavior, sorting, number format, and the anti-pattern
checks. Pull conservative defaults (number formats, KPI-card rules, max visuals
per executive page) from
`../../../../design/tokens/tower-retail-design-tokens.yaml`; pull colors/fonts
from the theme, not from per-visual overrides.

Keep the visual count low on executive pages (fewer visuals, more hierarchy);
push row-level tables to a detail or data-quality page. The full readable
design-principles and anti-pattern explanations live in the prose reference, not
here.

## Stop-and-ask (Principle V)

STOP and surface to a human rather than self-answering when:

- which business question a visual/page answers is unclear;
- a chart choice deviates from the grain default (record the `warning`-class note
  and ask);
- a readability deviation is proposed (dense layout, low contrast);
- a visual would need a metric with no contract or an unmapped field (record the
  blocking reason above and STOP).

Never invent a metric to make a visual work, and never self-grant
`dashboard_ready: pass` -- that is the verb owner's recorded design-review.

## See also

- The router + the four-surface table: `../SKILL.md`.
- Arrange these objects into a page: `page-blueprint.md`.
- Final-review anti-pattern reference: `dashboard-qa.md`.
- The prose design-principles + anti-pattern explanations:
  `docs/powerbi/visual-design-system.md` and `docs/powerbi/visual-qa.md`.
- The visual spec blank: `templates/visual-spec.yaml`.
- Conservative defaults: `design/tokens/tower-retail-design-tokens.yaml`.
- The gate to inherit + the four statuses: `docs/readiness/dashboard-ready.md`,
  `docs/readiness/readiness-model.md`.
