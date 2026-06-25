# Background Assets (Surface 2) -- the external background/canvas workflow

Status note: Planning (docs/templates/skill only; no runtime code, no PBIP/PBIR
edit). Reference doc for the Power BI Visual Foundation (F011A).

## What this doc is

This is the prose reference for **surface 2** of Power BI dashboard design: the
external background/canvas assets a page sits on. Power BI dashboard design is
four separate surfaces (report visuals / external background-canvas / theme JSON
/ implementation handoff); the full router table lives in
`docs/powerbi/visual-design-system.md`. This file covers only surface 2 -- what a
background asset is, how it is produced and imported, and the rules that keep it
from drifting into the other surfaces.

The agent procedure that USES this reference is
`.claude/skills/powerbi-dashboard-design/workflows/background-asset-design.md`;
the copy-me blank an author fills per page is `templates/background-spec.yaml`.

## The one rule (surface-2 purity)

Background is STATIC STRUCTURE, never data. Never bake a KPI value, a dynamic title, or any other dynamic/refreshing content into a static background image. The background carries layout structure (safe zones, containers, grid); the live Power BI visuals sit editable ABOVE it.

Everything else in this doc follows from that rule.

## Surface 2 is NOT gated on contracts

A background asset carries layout structure, not data, so it does NOT require
approved metric contracts to author. The contracts-first hard gate (no
data-bound design before `semantic_model_ready` is `pass`) applies to surface 1
(report visuals), not here. A safe-zone grid or a branded canvas may be produced
while the subject area's contracts are still `not_started`. (The gate itself is
owned by `docs/readiness/dashboard-ready.md` and the F011/012 dashboard-design
verb; this doc neither re-defines it nor extends it to surface 2.)

## The workflow

Design the background OUTSIDE Power BI, export it, then import it as a page
background or image layer with the live visuals editable above it.

1. **Design outside Power BI.** Author the background in a design tool --
   Figma, Canva, PowerPoint, or Illustrator. Power BI does not draw the
   background; it only displays the exported asset.
2. **Lay out static structure only.** Place safe zones, static layout
   containers (header band, KPI-strip frame, section dividers, footer band), a
   grid, and branding (logo, page chrome). Do NOT place any value that would
   need to refresh -- no number, no date, no dynamic title.
3. **Export the asset.** Export to PNG, SVG, or JPG at a consistent 16:9 frame
   so every page in the report shares one canvas size. Record the canvas size
   and safe zones in the page's `templates/background-spec.yaml`.
4. **Store the asset.** Put the exported file under the asset home and name it
   per the convention in `design/backgrounds/README.md`.
5. **Import into Power BI.** Set the asset as the page background (wallpaper) or
   add it as an image layer sent to the back. Match the import "fit" so the
   asset is not stretched off its 16:9 frame.
6. **Keep the visuals editable above it.** The live, data-bound visuals (cards,
   charts, slicers) sit ON TOP of the background and remain fully editable. The
   background never carries a value; the visuals on top carry every value.

## Canvas size and safe zones (reference, do not hardcode)

State the canvas size and safe zones by pointing at the grid files, so the
background frame stays consistent with everything else and cannot drift to a
different number:

- Desktop 16:9 canvas dimensions, columns/rows, gutters, and safe zones:
  `design/grids/16x9-grid.yaml`.
- Phone canvas grid: `design/grids/mobile-grid.yaml`.

Each page's `templates/background-spec.yaml` records the canvas size and safe
zones it used (by reference to the grid), the exported asset path, and the
export format.

## Design rules for a background asset

- **Structure, not data.** See the surface-2 purity rule above. No KPI value,
  no dynamic title, no refreshing content in the image.
- **Document canvas size + safe zones.** Every background states its canvas size
  and safe zones (by reference to `design/grids/16x9-grid.yaml`); visuals are
  placed inside the safe zones, never into the page bleed.
- **Export at a consistent 16:9.** All pages in a report share one canvas size
  so the background frame lines up page to page.
- **Preserve whitespace.** Leave breathing room between containers; a dense,
  edge-to-edge background fights the visuals that sit on top of it.
- **Avoid dark backgrounds behind dense charts.** A dark canvas behind a dense
  chart or table hurts readability. This is a `warning`-class readability note,
  not a silent override: if a user asks for a dark, dense page, record the
  readability concern and propose the accessible alternative (lighter canvas
  behind the dense region, or fewer visuals), rather than complying against the
  principle or overriding the user silently. The judgment call is surfaced for a
  human (Principle V).

## Forbidden in a background asset

A static background image MUST NOT contain:

- a KPI value (any number that should refresh);
- a dynamic title (a title that depends on a slicer, filter, or measure);
- any other dynamic/refreshing content.

If a request asks to put a live value into the background, that is a blended
surface (mixing surface 1 into surface 2) and produces a number that never
refreshes. Split it: the structure goes in the background (surface 2); the value
goes in a visual ON TOP of it (surface 1). The page's
`templates/background-spec.yaml` carries an explicit "forbidden dynamic content"
section that bans KPI values and dynamic titles in the static image.

## What this doc does NOT do

- It does not edit any PBIP/PBIR file, generate DAX, change SQL, edit any
  semantic-model file, or add pbi-cli automation. Importing the asset into a
  report is an implementation step owned by the handoff surface
  (`.claude/skills/powerbi-dashboard-design/workflows/powerbi-handoff.md`) and,
  for any automation, by F016.
- It does not design report visuals (surface 1), set theme defaults (surface 3),
  or define a metric (that is F009).

## See also

- The four surfaces + design principles: `docs/powerbi/visual-design-system.md`.
- The agent procedure (surface 2):
  `.claude/skills/powerbi-dashboard-design/workflows/background-asset-design.md`.
- The per-page blank: `templates/background-spec.yaml`.
- Asset storage + naming: `design/backgrounds/README.md`.
- Canvas grid + safe zones: `design/grids/16x9-grid.yaml`,
  `design/grids/mobile-grid.yaml`.
- Theme JSON (surface 3): `docs/powerbi/theme-json.md`.
- The stage + its gate (owned there, not here):
  `docs/readiness/dashboard-ready.md`.
