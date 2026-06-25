# mobile-layout

Surface 1 (report visuals), mobile intent. Open this workflow when someone asks
for a phone layout, a mobile view, or "how does this page look on a phone." This
is the phone-canvas counterpart of `page-blueprint.md` (the desktop page) and
`visual-design-system.md` (the visual choices on it).

Mobile layout is REFLOW, not new design. The page's visuals were already chosen
and bound to approved metric contracts on the desktop blueprint; the phone view
re-arranges and prioritizes those SAME visuals onto a narrow canvas. It opens no
new contract question. The inherited gate and the four-status readiness
vocabulary apply to surface-1 work -- see `../SKILL.md` (the four surfaces + the
inherited gate) and `docs/readiness/dashboard-ready.md`. This workflow does not
restate them; it consumes a page that already cleared them.

## What this workflow produces

A `mobile` section for the page blueprint (the `mobile notes` field in
`templates/dashboard-page-blueprint.yaml`): the ordered list of which desktop
visuals survive to the phone, in what order, on the phone grid -- plus a short
note of what is deliberately desktop-only. No PBIP/PBIR edit; the phone layout in
Power BI Desktop is F016's execution step (surface 4, `powerbi-handoff.md`).

## The phone canvas

Use the phone grid in `design/grids/mobile-grid.yaml` -- a tall, narrow,
single-column canvas, the opposite of the desktop 16:9. Design against that grid;
do not free-place. The phone is read one-thumb, top-to-bottom, often glanced at
rather than studied, so the layout is a vertical PRIORITY STACK: the most
important answer first, detail further down or not at all.

This is the extreme case of the design principle that executive pages use fewer
visuals (see `docs/powerbi/visual-design-system.md`). On a phone the budget is
tightest: a few stacked visuals beat a shrunken copy of the desktop page.

## What survives to mobile vs. desktop-only

Reuse the page section vocabulary from `page-blueprint.md` -- header / KPI strip /
main insight / diagnostic / exception-detail / filter rail / footer-status -- and
decide each section's fate on the phone:

| Section | On the phone |
|---------|--------------|
| Header (page title + date context) | Survives -- compact; the date context stays so a glanced number is never read without its period. |
| KPI strip | Survives FIRST -- the headline numbers are the reason to open the page on a phone. Stack the cards vertically (or two-up) rather than shrinking a wide row. |
| Main / top insight | Survives -- the single chart that answers the page's business question, full phone width. |
| Diagnostic (supporting breakdowns) | Usually desktop-only -- include at most one if it is genuinely glanceable; otherwise drop. |
| Exception-detail / dense tables | Desktop-only -- a wide table or matrix is unreadable on a phone; do not shrink it onto the canvas. |
| Filter rail / many slicers | Desktop-only as a rail -- keep at most one or two essential slicers, placed inline at the top, not a side rail. |
| Footer-status (last-refresh, data-quality flag) | Survives -- compact, at the bottom; a glanced number needs its freshness. |

Rule of thumb: the phone keeps the KPI strip + the one top insight (the "what" and
the headline "why"); it sheds the diagnostic depth, the exception detail, and the
filtering breadth that belong to a seated desktop session.

## Reflow guidance

- **One column, priority order.** Stack visuals top-to-bottom by importance.
  Do not try to preserve the desktop's two-dimensional arrangement.
- **Cards stack, charts go full-width.** A KPI card row becomes a vertical (or
  two-up) stack; the main chart spans the phone width.
- **Keep titles and number formats identical to desktop.** Mobile changes
  position and selection, never a metric, a contract binding, or a number format.
- **Touch targets, not hover.** A phone has no hover, so a visual that relies on a
  tooltip for its context must carry that context on its face (a comparison value,
  a label) or be left desktop-only.
- **Essential slicers inline at top.** If a slicer must travel to the phone, place
  it inline above the visuals it filters, not in a side rail.

## When the phone is overcrowded (record, do not silently comply)

If the request asks to cram the full desktop page onto the phone -- every visual,
the dense table, the full slicer rail -- that is a readability deviation, the
mobile analog of a dark, dense executive page. Do not silently shrink everything
to fit, and do not silently override the user. Record it as a `warning`-class
design note (status vocabulary per `docs/readiness/readiness-model.md`) with the
reason, and propose the accessible alternative: the priority stack above (KPI
strip + top insight, detail dropped). Which sections are essential on the phone is
a Principle V judgment call -- surface it for the owner rather than deciding it to
make the page fit.

## See also

- The phone grid this workflow designs against: `design/grids/mobile-grid.yaml`.
- The desktop page it reflows: `workflows/page-blueprint.md` (the section
  vocabulary) + `workflows/visual-design-system.md` (the visual choices).
- The "fewer visuals" principle this is the extreme case of:
  `docs/powerbi/visual-design-system.md`.
- The router + the four surfaces + the inherited gate: `../SKILL.md`.
- The four-status readiness vocabulary (no numeric score):
  `docs/readiness/readiness-model.md`.
- The execution owner for the phone layout in Power BI Desktop:
  `workflows/powerbi-handoff.md` (surface 4; F016 owns execution).
