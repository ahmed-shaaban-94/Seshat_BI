# theme-json-design (surface 3)

The theme JSON workflow. A Power BI theme is a single JSON file, imported into a
report, that sets the report's visual DEFAULTS -- the color palette, fonts,
visual/page/wallpaper/filter-pane defaults, and sentiment COLORS. It is the one
place a consistent look is declared once and inherited by every visual, instead
of each visual being styled by hand. This is one of the four surfaces the
`powerbi-dashboard-design` router classifies into; route here only for a
colors/fonts/default-formatting request.

## Scope (read first)

This workflow authors (or specifies) styling DEFAULTS only. It produces a theme
JSON -- or the human-readable spec that backs one -- and it never carries business
meaning and never edits a PBIP/PBIR file. The live, data-bound visuals are a
surface-1 concern (`workflows/visual-design-system.md` +
`workflows/page-blueprint.md`); the static page frame is a surface-2 concern
(`workflows/background-asset-design.md`); actually importing the theme in Power BI
Desktop is execution that F016 owns (`workflows/powerbi-handoff.md`). This
workflow stops at the theme JSON + the spec + the import instruction.

## The surface-3 purity rule (carry verbatim)

Theme JSON controls DEFAULTS, never business meaning. It MAY set: color palette, fonts, visual
defaults, page/wallpaper defaults, filter-pane defaults, sentiment COLORS. It MUST NOT control:
DAX, metric definitions, semantic-model relationships, source mapping, visual storytelling, or
data validation. (A sentiment COLOR belongs in the theme; the sentiment THRESHOLD/RULE is a
metric contract, F009.)

## Not gated on contracts

Surface-3 work carries DEFAULTS, not data, so it is NOT gated on
`semantic_model_ready`. A palette, a font set, and the filter-pane defaults may be
chosen before any metric contract exists -- the inherited Dashboard Ready gate
(rule 5) applies to data-bound design (surface 1), not to a styling default.
Record readiness with the four statuses (`not_started` / `blocked` / `warning` /
`pass`) plus `evidence[]` and `blocking_reasons[]`; never a numeric score.

## What to SET (the theme's job)

The theme is the right home for every one of these; set them here so they are
declared once and inherited everywhere:

- **Color palette** -- the report's `dataColors` (the ordered series colors a
  chart cycles through) and the primary/secondary brand colors. Seed these from
  the design tokens (`design/tokens/tower-retail-design-tokens.yaml`) so the
  theme and the design system agree.
- **Fonts** -- the font family and the default text sizes/weights for titles,
  labels, and values. One typeface family across the report; size carries the
  hierarchy, not a different font per visual.
- **Visual defaults** -- the default formatting every visual inherits (background,
  border, title on/off and alignment, data-label defaults, gridline style). A
  visual overrides a default only with a recorded reason, never randomly.
- **Page / wallpaper defaults** -- the default page background and wallpaper color
  so empty canvas is consistent. (A designed background IMAGE is a surface-2
  asset, `workflows/background-asset-design.md`; the theme sets only the default
  color behind it.)
- **Filter-pane defaults** -- the filter pane's background, font, and border
  defaults so the pane matches the report instead of using Power BI's raw look.
- **Sentiment COLORS** -- the success / warning / danger colors used to signal
  good/neutral/bad. The COLOR is a styling default and belongs here. The
  THRESHOLD or RULE that decides which color a value gets is business logic and
  belongs to a metric contract (F009) -- see the judgment call below.

## What the theme must NOT control

Restating the purity rule as a checklist -- the theme MUST NOT control any of
these (each belongs to another surface or another stage):

- **DAX** -- expressions are a semantic-model / metric concern, never styling.
- **Metric definitions** -- a metric is defined in a metric contract (F009), not
  declared in a theme.
- **Semantic-model relationships** -- modeling lives in the governed model (F010),
  not a styling file.
- **Source mapping** -- column keep/drop/rename/grain is the source-mapping stage,
  not the theme.
- **Visual storytelling** -- which visual answers which business question is a
  page-blueprint (surface 1) concern, not a default.
- **Data validation** -- correctness rules belong to the readiness gates, never to
  a color file.

If a supplied theme tries to encode any of the above, separate it: keep the
styling default in the theme, and route the business logic to its owning stage --
do not let the theme carry the rule.

## The sentiment COLOR vs THRESHOLD judgment call

A common request is "make the theme show red when we are below target." Split it:

- The **sentiment COLOR** (the specific red/amber/green) is a styling default ->
  it belongs in the theme (and in the design tokens it seeds from).
- The **sentiment THRESHOLD / RULE** ("below target" = below what, measured how)
  is business logic -> it belongs in a metric contract (F009), not the theme.

The theme declares the palette of meaning-colors; the contract decides when each
applies. A theme that bakes in the threshold has crossed into surface-1 business
logic (a purity-rule violation). This is a Principle V boundary, not a styling
choice -- keep the rule with the contract.

## Procedure

### 1. Confirm the surface and intent

Confirm this is a colors/fonts/default-formatting request and not a request to
arrange live visuals (surface 1), to design a background image (surface 2), or to
implement in Power BI (surface 4). If the request is ambiguous ("make this look
better"), STOP and ask which surface is meant (Principle V) rather than inventing
a blended plan.

### 2. Seed from the design tokens

Start from `design/tokens/tower-retail-design-tokens.yaml` -- the conservative
executive retail seed (palette, sentiment colors, neutrals, font, spacing). The
theme is the Power-BI-specific compilation of those tokens; do not invent a new
palette that disagrees with the design system. If the tokens are missing a value
the theme needs, add it to the tokens first, then reflect it in the theme.

### 3. Fill the theme spec

Record the design in `templates/theme-json-spec.md` (copy the blank): palette,
typography, sentiment colors, data colors, visual defaults, filter-pane defaults,
page background, accessibility checks, and the explicit "must NOT control" list.
The spec is the human-readable, reviewable artifact -- author it before the JSON
so the review is about the choices, not the syntax.

### 4. Author the theme JSON (defaults only)

Write or extend the starter theme `themes/tower-retail.theme.json` -- a minimal,
conservative starter (`name`, `dataColors`, `background`, `foreground`,
`tableAccent`, and safe `visualStyles` defaults). Keep it ASCII, UTF-8 without
BOM, and contain DEFAULTS only: no DAX, no metric, no relationship, no connection
string, no secret. See `themes/README.md` for what the starter is and is not.

### 5. Treat the schema as uncertain -- validate in Power BI Desktop

The exact Power BI theme schema is treated as UNCERTAIN in this slice. The theme
JSON is a STARTER that MUST be validated by importing it into Power BI Desktop
(View -> Themes -> Browse for themes) before it is relied on. A key Power BI
silently ignores is a no-op, not a fix; do not claim schema completeness. Record
the validation step as evidence; do not mark the theme `pass` on author alone.

### 6. Specify the import (do NOT perform it)

Document how the theme is applied so a later builder can use it: in Power BI
Desktop, View -> Themes -> Browse for themes -> select the exported
`themes/tower-retail.theme.json`. State plainly that this workflow writes the
instruction only -- it edits no PBIP/PBIR file; the actual Desktop authoring and
any pbi-cli automation are execution F016 owns (`workflows/powerbi-handoff.md`).

## QA checklist (before handing off the theme)

- The theme controls DEFAULTS only -- zero DAX, metric definitions, relationships,
  source mapping, storytelling, or validation (purity rule).
- Sentiment COLORS are in the theme; the sentiment THRESHOLD/RULE is in a metric
  contract (F009), not here.
- The palette and fonts agree with `design/tokens/tower-retail-design-tokens.yaml`;
  the theme invented no off-system color.
- Contrast is accessible (text vs background, sentiment colors distinguishable);
  any deviation is recorded as a `warning` with a reason.
- The JSON is valid, ASCII, UTF-8 without BOM, with no connection string or
  secret.
- The theme is marked a STARTER pending Power BI Desktop validation -- not
  self-granted `pass` on author alone.

## See also

- The prose reference for this surface: `docs/powerbi/theme-json.md`.
- The spec blank this workflow fills: `templates/theme-json-spec.md`.
- The starter theme + its caveats: `themes/tower-retail.theme.json` +
  `themes/README.md`.
- The palette/typography source this theme seeds from:
  `design/tokens/tower-retail-design-tokens.yaml`.
- The static page frame the theme sets the default color behind (surface 2):
  `workflows/background-asset-design.md`.
- The live visuals that inherit these defaults (surface 1):
  `workflows/visual-design-system.md` + `workflows/page-blueprint.md`.
- The handoff that consumes this theme (surface 4; F016 owns execution):
  `workflows/powerbi-handoff.md`.
- The router that classified this request: `SKILL.md`.
