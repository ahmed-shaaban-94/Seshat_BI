# design/backgrounds/

The home for **exported background/canvas assets** -- the static PNG/SVG/JPG
images a Power BI page sits on. This is **surface 2** (external
background/canvas) of the Power BI Visual Foundation (F011A): the live,
data-bound visuals are authored separately and sit editable ABOVE these images.

This README is the authority that other artifacts defer to for **where assets
live and how they are named**. The prose workflow (`docs/powerbi/background-assets.md`)
and the per-page blank (`templates/background-spec.yaml`) both point here for the
storage location and naming convention.

## The one rule (surface-2 purity)

Background is STATIC STRUCTURE, never data. Never bake a KPI value, a dynamic title, or any other dynamic/refreshing content into a static background image. The background carries layout structure (safe zones, containers, grid); the live Power BI visuals sit editable ABOVE it.

Everything below follows from that rule: this folder holds layout structure
(safe zones, containers, grid, branding chrome) only -- no number, no date, no
dynamic title is ever drawn into a committed image here.

## Where assets live

Exported background images are committed **directly in this folder**
(`design/backgrounds/`). One image per dashboard page. The editable source file
(the Figma/Canva/PowerPoint/Illustrator document the image was exported from)
is NOT required here -- if kept, reference it from the page's
`templates/background-spec.yaml` (`asset_path.source_file_ref`); only the static
export is committed under `design/backgrounds/`.

```
design/backgrounds/
|-- README.md                       # this file (storage + naming authority)
|-- <page>-bg.png                   # one static export per page (see naming below)
`-- <page>-bg.svg                   # (alternate format for the same page)
```

## Naming convention

```
<page>-bg.<ext>
```

- `<page>` -- the page's name, matching the stem of that page's blueprint file in
  `reports/blueprints/` (kebab-case, e.g. `executive-summary`). Anchoring the
  asset name to the blueprint stem keeps each background tracking the page it
  serves, and keeps the name short (Windows 260-char path limit; repo paths
  `<= 200` chars).
- `-bg` -- the fixed suffix marking this as a background/canvas asset (surface 2),
  not a screenshot, a logo, or an exported visual.
- `<ext>` -- the export format: `png`, `svg`, or `jpg` (see Export formats below).

Examples (the four starter pages):

```
design/backgrounds/executive-summary-bg.png
design/backgrounds/branch-performance-bg.png
design/backgrounds/product-mix-bg.png
design/backgrounds/data-quality-control-room-bg.png
```

If a page needs more than one background variant, keep the `<page>-bg` stem and
distinguish by extension (a `.png` and a `.svg` of the same layout). Do not
introduce ad-hoc variants (`bg-<page>`, `<page>_background`, dated stamps) -- the
single `<page>-bg.<ext>` form is what `templates/background-spec.yaml`
(`asset_path.file`) expects.

## Export formats

Export from the external design tool (surface 2) at the canvas size in
`design/grids/16x9-grid.yaml` (desktop) or `design/grids/mobile-grid.yaml`
(phone), 1:1 so the asset aligns to the grid:

| Format | Use it for | Notes |
|--------|------------|-------|
| `png`  | crisp UI chrome, panels, dividers, transparency | the default for background structure |
| `svg`  | vector chrome that must stay sharp at any scale  | smallest, resolution-independent |
| `jpg`  | photographic / image fills only                  | no transparency; avoid for crisp chrome |

PNG is the default for layout structure (crisp edges, transparency so the page
color shows where unset). Use SVG when the chrome should stay sharp at any zoom.
Use JPG only for a photographic fill; never for panels, dividers, or text chrome
(its compression softens edges and it has no transparency).

## See also

- The surface-2 workflow (the agent procedure):
  `.claude/skills/powerbi-dashboard-design/workflows/background-asset-design.md`.
- The prose reference (surface 2): `docs/powerbi/background-assets.md`.
- The per-page blank that records each asset's path/format/safe zones:
  `templates/background-spec.yaml`.
- The canvas grids the assets are exported to fit:
  `design/grids/16x9-grid.yaml`, `design/grids/mobile-grid.yaml`.

> Storage + naming reference only. Importing an asset into a report is an
> implementation step: the handoff stops at NOTES and F016 owns any execution
> (no PBIP/PBIR edit, no pbi-cli automation in this slice).
