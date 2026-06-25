# background-asset-design (surface 2)

The external background/canvas workflow. A background/canvas asset is a PNG, SVG,
or JPG that carries the page's STATIC layout structure -- safe zones, containers,
grid, branding frame -- designed OUTSIDE Power BI and imported as the page
background or an image layer. The live, data-bound Power BI visuals sit editable
ABOVE it. This is one of the four surfaces the `powerbi-dashboard-design` router
classifies into; route here only for a background/canvas request.

## Scope (read first)

This workflow designs STATIC STRUCTURE only. It produces (or specifies) an
exported image asset and the instructions to import it -- it never carries a data
value and it never edits a PBIP/PBIR file. The live visuals are a surface-1
concern (`workflows/visual-design-system.md` + `workflows/page-blueprint.md`);
actually placing the asset in Power BI Desktop is execution that F016 owns
(`workflows/powerbi-handoff.md`). This workflow stops at the asset + the import
instruction.

## The surface-2 purity rule (carry verbatim)

Background is STATIC STRUCTURE, never data. Never bake a KPI value, a dynamic title, or any other
dynamic/refreshing content into a static background image. The background carries layout structure
(safe zones, containers, grid); the live Power BI visuals sit editable ABOVE it.

## Not gated on contracts

Surface-2 work carries STRUCTURE, not data, so it is NOT gated on
`semantic_model_ready`. A background's safe zones, grid, and containers may be
designed before any metric contract exists -- the inherited Dashboard Ready gate
(rule 5) applies to data-bound design (surface 1), not to a static canvas. Record
readiness with the four statuses (`not_started` / `blocked` / `warning` / `pass`)
plus `evidence[]` and `blocking_reasons[]`; never a numeric score.

## Procedure

### 1. Confirm the surface and intent

Confirm this is a background/canvas request (a branded frame, a layout grid, a
safe-zone scaffold, a static container set) and not a request to arrange live
visuals (surface 1) or to set colors/fonts as defaults (surface 3). If the
request is ambiguous ("make this page look better"), STOP and ask which surface
is meant (Principle V) rather than inventing a blended plan.

### 2. Design OUTSIDE Power BI

Author the asset in an external design tool -- Figma, Canva, PowerPoint, or
Illustrator. None of these is data-aware, which is the point: the tool that draws
the background cannot accidentally bind a metric. Lay out:

- **Canvas size** -- match the page's canvas (default desktop 16:9; see
  `design/grids/16x9-grid.yaml`). Use one consistent canvas across pages of a
  report so the frame does not shift.
- **Safe zones** -- the margins and reserved bands the live visuals must stay
  within (header band, KPI strip, main body, filter rail, footer-status band).
  The background marks the zones; it never fills them with values.
- **Static containers / grid** -- panels, dividers, and the alignment grid that
  give the page a consistent rhythm. These are decoration and structure only.
- **Branding frame** -- logo, title plate (the plate, NOT the live title text),
  and a consistent color field that defers to the theme's palette.

Keep the asset conservative: preserve whitespace, avoid heavy dark fields behind
dense charts (a readability `warning`), and keep the structure legible at the
exported resolution.

### 3. Fill the background spec

Record the design in `templates/background-spec.yaml` (copy the blank): page,
canvas size, asset path, export format, safe zones, static regions, the explicit
FORBIDDEN dynamic content section, import instructions, and the QA checklist. The
spec is the reviewable artifact; the image is what it points at.

### 4. Export the asset

Export to PNG, SVG, or JPG at the page's canvas resolution. PNG or SVG for crisp
edges and transparency where containers must let the page background show through;
JPG only for a photographic field with no hard lines. Name the file per the
convention in `design/backgrounds/README.md` and store it there.

### 5. Specify the import (do NOT perform it)

Document how the asset is imported so a later builder can apply it: import as the
**page background** (Format pane -> Canvas background -> Browse -> the exported
file, Image fit = Fit, Transparency = 0%) or as a back-most **image layer** when
a per-region container is needed. State plainly that the live, data-bound visuals
are then placed editable ABOVE the background, inside the safe zones. This
workflow writes the instruction only -- it edits no PBIP/PBIR file; the actual
Desktop authoring is execution F016 owns (`workflows/powerbi-handoff.md`).

## Forbidden dynamic content

The background is an image. It cannot refresh, so it must contain nothing that is
supposed to change with the data:

- **No KPI value** baked into the image (a "Sales: 1.2M" rendered into the PNG is
  a number that never updates).
- **No dynamic title** baked in (the page/visual title that reflects a slicer or
  a date is a live text element, surface 1, ABOVE the background -- not part of
  the static asset).
- **No legend, axis label, or data point** that belongs to a live visual.

A title PLATE (the empty frame the live title sits on) is structure and belongs
to the background; the title TEXT is live and does not. If a request asks to "put
the total in the banner," split it: the banner shape is surface 2, the total is a
surface-1 card placed above it.

## QA checklist (before handing off the asset)

- The asset carries zero data values and zero dynamic titles (purity rule).
- Canvas size matches the page grid; safe zones leave room for every planned
  visual.
- Whitespace is preserved; no dark dense field sits behind a dense chart (or the
  deviation is recorded as a `warning` with a reason).
- The frame is consistent across the report's pages.
- Colors defer to the theme palette; the background invents no business-meaning
  color (sentiment meaning lives in the theme + the metric contract, not here).
- The export format and resolution match the canvas; the file is named and stored
  per `design/backgrounds/README.md`.

## See also

- The prose reference for this surface: `docs/powerbi/background-assets.md`.
- The spec blank this workflow fills: `templates/background-spec.yaml`.
- The desktop grid + safe zones: `design/grids/16x9-grid.yaml` (and
  `design/grids/mobile-grid.yaml` for phone).
- Where exported assets live + the naming convention:
  `design/backgrounds/README.md`.
- The live visuals that sit above the background (surface 1):
  `workflows/visual-design-system.md` + `workflows/page-blueprint.md`.
- The handoff that consumes this asset (surface 4; F016 owns execution):
  `workflows/powerbi-handoff.md`.
- The router that classified this request: `SKILL.md`.
