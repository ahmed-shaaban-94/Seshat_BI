# screenshot-review (surface 1 -- critique an existing dashboard screenshot)

Surface 1, QA intent. The agent reached this workflow because the router classified
the request as "critique this dashboard screenshot." This procedure CRITIQUES an
existing report image and emits structured findings + recommended fixes. It is not a
redesign and it produces no new file. A redesign request belongs to
`workflows/page-blueprint.md`; the broader anti-pattern reference lives in
`workflows/dashboard-qa.md` and its prose home `docs/powerbi/visual-qa.md`.

The critique reads against the design principles in
`docs/powerbi/visual-design-system.md` and the anti-pattern list in
`workflows/dashboard-qa.md`. Use `templates/screenshot-review.md` for the output
shape -- this workflow tells you HOW to critique; that template is WHAT the written
critique looks like.

## Scope (read first)

- **Critique only.** The output is findings + recommended fixes + a forbidden-changes
  note. Do NOT redesign the page, author a new blueprint, or emit any new artifact.
  Acceptance scenario 2: a screenshot critique produces a critique, NOT a redesign
  or a new file.
- **You critique a static image.** You may not see the underlying contracts, fields,
  or DAX from a screenshot alone. State that limitation; phrase contract/field
  observations as findings to verify upstream, not as facts you confirmed.
- **You may FLAG a suspect metric; you may NOT redefine it.** If a visual appears to
  use a metric with no contract, or a field that looks unmapped, RECORD the finding
  and point upstream to F009 (metric contracts) / F010 (semantic model). Never
  define, rename, or correct the metric here -- metric definition is F009's job
  (FR-009). The critique flags; the upstream stage decides.
- **One surface.** This is surface 1 (report visuals). If the request is really about
  a background asset, a theme/colors choice, or a build/implement step, stop and
  re-route via the SKILL.md router -- do not blend surfaces in a single critique.

## Procedure

1. **Identify the page.** State the page name (if visible) and your best read of its
   intended audience and the ONE business question it appears to answer. If the
   business question is not inferable, that is itself a finding -- a page that does
   not answer a clear question is the first anti-pattern.
2. **Walk the sections top to bottom.** Header, KPI strip, main insight, diagnostic,
   exception detail, filter rail, footer/status. Note what is present, what is
   missing, and what is in the wrong section.
3. **Score each output dimension qualitatively** (below). Use `strong` / `adequate`
   / `weak` with the SPECIFIC reason -- never a fabricated number. (A made-up rating
   like "7/10" reads against the no-numeric-score rule on review; say WHY it is weak,
   not a digit.)
4. **List concrete findings per dimension**, each tied to the principle or
   anti-pattern it violates (cross-reference `workflows/dashboard-qa.md`).
5. **Write recommended fixes** -- surface-1 suggestions only (reorder, change a chart
   type, fix a number format, add a comparison/context, raise contrast, move a
   slicer). A fix is a SUGGESTION the report owner applies later; it is not an edit
   and not a new page.
6. **Write the forbidden-changes note** (verbatim block below) so the reader knows
   what this critique will not do.
7. **Record readiness** as a `warning`-class design note when the page binds to
   contracts but has non-fatal issues; never self-grant `dashboard_ready: pass`
   (that is the verb owner's recorded design-review). Use the four statuses only --
   `not_started` / `blocked` / `warning` / `pass` -- with `evidence[]` and
   `blocking_reasons[]`, never a numeric confidence score.

## Output sections (fill the `templates/screenshot-review.md` shape)

Emit these in order. Each carries a qualitative score (`strong` / `adequate` /
`weak`) plus specific findings; an empty dimension is recorded as "no issues
observed," not omitted.

- **Page purpose** -- the one business question the page appears to answer (or a
  finding that none is clear) + the intended audience.
- **Visual-hierarchy** -- does the eye land on the headline KPI/insight first? Score
  qualitatively. Findings: no clear hierarchy, competing focal points, the most
  important number buried, decoration outranking data.
- **Readability** -- font sizes, label legibility, data density, dark-behind-dense
  charts, truncated labels, overlapping text. A dark, dense executive page is a
  readability finding (propose the accessible alternative, do not silently accept).
- **Spacing / alignment** -- gutters, edge margins, visuals snapped to a grid,
  inconsistent padding, crowding, uneven whitespace.
- **Color / contrast** -- accessible contrast, colors carrying meaning (not
  decoration), consistent category/branch colors where applicable, theme colors
  overridden randomly per visual.
- **Chart-choice** -- does each chart fit its question and grain? (trend -> line;
  part-to-whole -> bar/stacked with care; comparison -> bar; single value -> card;
  detail -> table/matrix, NOT as the main executive visual.)
- **Slicer / filter** -- do slicers dominate the canvas, is the active filter/date
  context clear, is the filter rail where the reader expects it?
- **KPI-context** -- does every KPI carry a comparison or context (vs prior period,
  vs target, vs benchmark)? A bare KPI with no comparison is an anti-pattern.
- **Background / canvas** -- is the background static structure (safe zones,
  containers, grid) and NOT carrying data? If the image appears to bake in a KPI
  value or a dynamic title, that is a surface-2 purity violation -- flag it.
- **Recommended fixes** -- the prioritized, surface-1 suggestions. Suggestions only.
- **FORBIDDEN changes** -- the block below, verbatim.

## Flagging a suspect metric or field (FR-009 -- flag, never redefine)

From a screenshot you cannot confirm a visual's contract or field binding. When a
visual LOOKS like it uses a metric with no contract (an "orphan visual") or a field
that is not in the governed model (an "unmapped field"):

- Record the finding -- e.g. "suspected orphan visual: <visual> shows <quantity> with
  no obvious approved metric contract -- verify against F009" or "suspected unmapped
  field: <field> -- verify against the governed semantic model, F010."
- Point upstream and STOP at the flag. Do NOT invent the metric, propose its DAX,
  rename it, or redefine it. The metric belongs to F009; the field binding to F010.
- Keep it a finding-to-verify, phrased as a suspicion (you saw an image, not the
  contracts), not a confirmed defect.

## FORBIDDEN changes (the critique will not do these)

This is the heart of the critique boundary. The forbidden list, in order:

- **Redefine or invent a metric.** A suspect metric is FLAGGED and pointed upstream
  to F009; it is never defined, renamed, or corrected here.
- **Redesign the page or emit a new file.** This is a critique; recommended fixes are
  suggestions, not edits and not a new blueprint/page.
- **Blend surfaces.** Never recommend baking a KPI value or dynamic title into the
  background (surface 1 into 2), and never recommend putting a metric, threshold, or
  meaning into the theme (surface 1 into 3). Sentiment COLORS are the theme's; the
  sentiment THRESHOLD/RULE is a metric contract (F009).
- **Fabricate a readiness/confidence score.** Scores are qualitative (`strong` /
  `adequate` / `weak`) with reasons; readiness uses the four statuses only.
- **Self-grant `dashboard_ready: pass`.** That is the verb owner's recorded
  design-review (F011/012), not this critique's to award.

And the no-data-edit / handoff boundary that bounds every workflow in this
foundation, verbatim:

This slice edits no PBIP/PBIR file, generates no DAX, changes no SQL, edits no semantic-model file,
and adds no pbi-cli automation. The handoff stops at implementation NOTES and names F016 as the
owner of any execution step (PBIP/PBIR authoring, pbi-cli, workspace publish).

## See also

- The output shape this workflow fills: `templates/screenshot-review.md`.
- The anti-pattern reference this critique reads against:
  `workflows/dashboard-qa.md` (procedure) + `docs/powerbi/visual-qa.md` (prose).
- The design principles: `docs/powerbi/visual-design-system.md`.
- The router and the four surfaces: `../SKILL.md`.
- The stage this foundation backs: `docs/readiness/dashboard-ready.md`;
  the four statuses: `docs/readiness/readiness-model.md`.
