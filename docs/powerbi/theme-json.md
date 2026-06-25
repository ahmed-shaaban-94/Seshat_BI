# Theme JSON -- what it controls, and what it must NOT

Theme JSON is **surface 3** of the four design surfaces (see
`visual-design-system.md`). It is a single JSON file imported into Power BI that
sets the report's *styling defaults*: colors, fonts, and the default formatting
visuals inherit unless a visual overrides them. It is the only surface whose job
is DEFAULTS. It carries no data, no business logic, and no layout structure --
those belong to surfaces 1, 2, and 4.

Surface-3 work is not gated on metric contracts. The theme carries defaults, not
data, so picking a palette and fonts may proceed even when a subject area's
`semantic_model_ready` is not yet `pass`. (Designing data-bound visuals -- surface
1 -- is gated; styling defaults are not.)

## The governing rule

Theme JSON controls DEFAULTS, never business meaning. It MAY set: color palette, fonts, visual
defaults, page/wallpaper defaults, filter-pane defaults, sentiment COLORS. It MUST NOT control:
DAX, metric definitions, semantic-model relationships, source mapping, visual storytelling, or
data validation. (A sentiment COLOR belongs in the theme; the sentiment THRESHOLD/RULE is a
metric contract, F009.)

## What theme JSON DOES control

A theme JSON MAY set these -- all of them are defaults a visual inherits, none of
them is business meaning:

- **Color palette** -- the ordered data colors a chart cycles through, plus the
  named accent/structural colors (background, foreground, table accent).
- **Fonts** -- the default font family AND the default font sizes for titles,
  labels, and headers.
- **Visual defaults** -- the default formatting visuals start from (gridlines,
  borders, padding, data-label on/off, title styling) before any per-visual edit.
- **Page and wallpaper defaults** -- the default page background / wallpaper
  color or fill applied to a page when no external background asset is set.
- **Filter-pane defaults** -- the default styling of the filter pane and filter
  cards (background, border, text color, applied/available states).
- **Sentiment COLORS** -- the colors that mean good / caution / bad (for example
  a success green, a warning amber, a danger red). The theme owns the *color*;
  it does NOT own the rule that decides which color applies (see below).

## What theme JSON MUST NOT control

A theme JSON MUST NOT carry any of these -- each is business meaning, data, or
structure that lives in another surface or another feature:

- **DAX** -- no measures, no calculated columns, no calculated tables. A theme is
  styling; it computes nothing.
- **Metric definitions** -- the meaning of a KPI (what it counts, its grain, its
  filters) is a metric contract (F009), never a styling default.
- **Semantic-model relationships** -- table joins and the model's shape are
  governed in the semantic model (F010), not declared in a theme.
- **Source mapping** -- which source column feeds which model field is a
  source-mapping concern, not a color/font default.
- **Visual storytelling** -- which visual answers which business question, and how
  a page is arranged to tell that story, is the page blueprint (surface 1), not
  the theme.
- **Data validation** -- any rule that checks or constrains data values is logic,
  not styling; it does not belong in a theme file.

### The sentiment color / sentiment rule split

This is the one boundary that is easy to blur, so state it plainly: a sentiment
COLOR belongs in the theme (surface 3); the sentiment THRESHOLD / RULE that
decides *when* a value is good, caution, or bad is business logic and belongs in
a metric contract (F009). The theme says "danger is this red"; the contract says
"below this number is danger." Never let the theme carry the threshold.

## Why the split matters

A metric definition hidden inside a styling file is unreviewed business logic in
the wrong place: it bypasses the metric-contract review (F009), it is invisible to
anyone reading the contracts, and it silently changes meaning when someone edits a
"color file." Keeping the theme to defaults only keeps business meaning in the one
place it is governed and reviewed.

## See also

- `visual-design-system.md` -- the four design surfaces and where theme JSON sits
  among them.
- `../../.claude/skills/powerbi-dashboard-design/workflows/theme-json-design.md`
  -- the surface-3 authoring procedure (the agent workflow that produces a theme).
- `../../templates/theme-json-spec.md` -- the copy-me theme spec (palette /
  typography / sentiment / defaults + the explicit must-NOT-control list).
- `../../themes/tower-retail.theme.json` -- the conservative starter theme; it
  MUST be validated in Power BI Desktop before use.
- `../../themes/README.md` -- what the starter theme is, the validate-in-Desktop
  note, and the schema-uncertainty note.
- `../../design/tokens/tower-retail-design-tokens.yaml` -- the design tokens the
  theme draws its palette, typography, and sentiment colors from.
