# Screenshot Review -- `<page_or_report_name>`

> **GENERIC TEMPLATE.** This is the blank a reviewer fills when critiquing an EXISTING
> dashboard screenshot. Copy it per screenshot, replace every `<placeholder>`, and record
> the findings. It is a SURFACE 1 (report visuals) artifact: its output is a CRITIQUE --
> findings + recommended fixes + a forbidden-changes guardrail -- never a redesign, a new
> page, or a new metric.
>
> It carries the SAME section shape as the workflow procedure that produces it:
> `.claude/skills/powerbi-dashboard-design/workflows/screenshot-review.md`. The workflow is
> the procedure; this template is the output shape it fills. Keep the two in sync.
>
> This template is GENERIC to retail BI (roadmap rule 7). Do NOT copy any C086/pharmacy
> specifics (billing codes, segment rollups, insurance/PII columns, pharmacy grain keys, real
> measure names) into it -- those belong only in a per-subject-area working set, never here.

---

## What this review is (and is not)

This is a critique of how a page READS -- hierarchy, readability, spacing, color/contrast,
chart fit, slicer placement, KPI context, and the static background behind the visuals. It
records findings and recommends fixes; it does NOT redesign the page (that is the
`page-blueprint.md` + `visual-design-system.md` workflows), define or redefine a metric (that
is F009), or edit anything in Power BI.

A review MAY FLAG that a visual appears to use a metric with no contract or a field not in the
governed semantic model, but it MUST NOT redefine the metric -- it records the finding and
points upstream to F009. The readable explanations of each anti-pattern named below live in
`docs/powerbi/visual-qa.md`; the procedure that fills this template lives in
`workflows/dashboard-qa.md` and `workflows/screenshot-review.md`.

Use words, never a number, for every assessment and severity. The readiness vocabulary is
exactly four statuses (`not_started` / `blocked` / `warning` / `pass`); per-finding severity
is `blocking` / `warning` / `minor`. Never a numeric score (roadmap rule 9). This review never
self-grants `dashboard_ready: pass` -- that is the verb owner's recorded design-review.

---

## Review header

| Field | Value |
|-------|-------|
| Page / report name | `<page_or_report_name>` |
| Screenshot under review | `<path_or_description_of_the_screenshot>` |
| Surface | 1 (report visuals) -- this review critiques live, data-bound objects |
| Audience | `<who_the_page_is_for; e.g. executive / branch manager / analyst>` |
| Reviewed by | `<analyst_or_agent>` |
| Review date | `<YYYY-MM-DD>` |
| Theme / background in use | `<theme_path_if_known>` / `<background_path_if_known>` (REFERENCE only -- not edited here) |

---

## 1. Page purpose

The one business question this page answers, and whether the screenshot delivers it.

| Field | Value |
|-------|-------|
| The one business question this page should answer | `<the single business question; STOP and ask if unclear>` |
| Does the page answer it clearly? | `<yes | partly | no>` |
| Notes | `<does the layout lead the eye to the answer, or bury it?>` |

> If the business question is unclear, this is a Principle V STOP: ask, do not guess.

---

## 2. Visual hierarchy

Qualitative only -- `strong` / `adequate` / `weak`. NOT a numeric score.

| Field | Value |
|-------|-------|
| Hierarchy assessment | `<strong | adequate | weak>` |
| Does the most important number read first? | `<yes | no>` |
| Issues | `<too many co-equal visuals, no focal point, headline buried, etc.>` |

---

## 3. Readability

Can a reader parse the page at a glance?

| Finding | Severity | Note |
|---------|----------|------|
| `<e.g. font too small for the audience/distance>` | `<blocking | warning | minor>` | `<...>` |
| `<e.g. too many visuals on one page>` | `<blocking | warning | minor>` | `<...>` |
| `<...>` | `<...>` | `<...>` |

---

## 4. Spacing and alignment

| Finding | Severity | Note |
|---------|----------|------|
| `<e.g. visuals not aligned to a grid; ragged edges>` | `<blocking | warning | minor>` | `<...>` |
| `<e.g. crowded, no whitespace / breathing room>` | `<blocking | warning | minor>` | `<...>` |
| `<...>` | `<...>` | `<...>` |

---

## 5. Color and contrast

Color carries meaning; contrast must be accessible. (Color DEFAULTS are the theme's job,
surface 3 -- this review flags color PROBLEMS, it does not edit the theme.)

| Finding | Severity | Note |
|---------|----------|------|
| `<e.g. insufficient text/background contrast (accessibility)>` | `<blocking | warning | minor>` | `<...>` |
| `<e.g. theme colors overridden randomly per visual>` | `<blocking | warning | minor>` | `<...>` |
| `<e.g. inconsistent branch/category colors across visuals>` | `<blocking | warning | minor>` | `<...>` |
| `<...>` | `<...>` | `<...>` |

---

## 6. Chart choice

Does each visual fit the question and the grain it answers? (Defaults by question/grain live
in `workflows/visual-design-system.md`; a deviation is a `warning`-class note with a reason.)

| Visual | Question it answers | Chosen type | Fits question/grain? | Note |
|--------|---------------------|-------------|----------------------|------|
| `<visual_id_or_label>` | `<the question>` | `<card | bar | line | matrix | ...>` | `<yes | no>` | `<e.g. pie with too many slices; table used as the main executive visual>` |
| `<...>` | `<...>` | `<...>` | `<...>` | `<...>` |

---

## 7. Slicer and filter placement

| Finding | Severity | Note |
|---------|----------|------|
| `<e.g. slicers dominate the page / crowd out the insight>` | `<blocking | warning | minor>` | `<...>` |
| `<e.g. filter state not visible to the reader>` | `<blocking | warning | minor>` | `<...>` |
| `<...>` | `<...>` | `<...>` |

---

## 8. KPI context

Every KPI carries a comparison/context; the date context must be clear.

| KPI / card | Has comparison/context (vs prior / vs target)? | Date context clear? | Number format correct? | Note |
|------------|------------------------------------------------|---------------------|------------------------|------|
| `<kpi_label>` | `<yes | no>` | `<yes | no>` | `<yes | no>` | `<e.g. bare number, no comparison; ambiguous period; wrong unit/decimals>` |
| `<...>` | `<...>` | `<...>` | `<...>` | `<...>` |

> A bare KPI with no comparison, an unclear date context, or a wrong number format are named
> anti-patterns -- see `docs/powerbi/visual-qa.md`.

---

## 9. Background and canvas issues

Background is STATIC STRUCTURE, never data. Never bake a KPI value, a dynamic title, or any other
dynamic/refreshing content into a static background image. The background carries layout structure
(safe zones, containers, grid); the live Power BI visuals sit editable ABOVE it.

Flag a background PROBLEM here; the background itself is designed in surface 2
(`workflows/background-asset-design.md`). Do NOT edit the background in this review.

| Finding | Severity | Note |
|---------|----------|------|
| `<e.g. a KPI value or dynamic title baked into the static background -- FORBIDDEN>` | `<blocking | warning | minor>` | `<...>` |
| `<e.g. dark background behind dense charts -- readability>` | `<blocking | warning | minor>` | `<...>` |
| `<e.g. background fights the visuals / no preserved whitespace>` | `<blocking | warning | minor>` | `<...>` |
| `<...>` | `<...>` | `<...>` |

---

## 10. Recommended fixes

Concrete, in-surface fixes. Each fix names the finding it addresses and stays inside surface 1
(or names the surface that owns it). Reference contracts/fields/theme/background by name -- do
not inline a metric formula or a theme color here.

| # | Fix | Addresses (finding) | Owning surface / workflow |
|---|-----|---------------------|---------------------------|
| 1 | `<the concrete change>` | `<which finding above>` | `<surface 1 visual-design-system | surface 2 background | surface 3 theme | F009 contract>` |
| 2 | `<...>` | `<...>` | `<...>` |
| 3 | `<...>` | `<...>` | `<...>` |

---

## 11. FORBIDDEN changes (standing guardrail -- do NOT fill; these always hold)

This review is a critique. It MUST NOT do any of the following, regardless of what a finding
suggests:

- **Do NOT redefine or invent a metric.** A review may FLAG that a visual seems to use a
  metric with no contract or a field not in the governed semantic model, but the metric
  definition is F009's job -- record the finding and point upstream; never write the formula
  here.
- **Do NOT bake a dynamic value into a static background.** Background is STATIC STRUCTURE,
  never data -- no KPI value, no dynamic title (the surface-2 rule, section 9).
- **Do NOT put business meaning in the theme.** Theme JSON controls DEFAULTS only (palette,
  fonts, defaults, sentiment COLORS); a sentiment THRESHOLD/RULE is a metric contract (F009),
  not a theme value.
- **Do NOT redesign the page.** A critique records findings + fixes; producing a new page or a
  new file is the `page-blueprint.md` workflow, not this one.
- **No data-bound design before the gate.** No data-bound dashboard design before the subject
  area `semantic_model_ready` is `pass` (roadmap rule 5); this review records a blocking reason
  and STOPS rather than critiquing data-bound visuals built on absent contracts.

This slice edits no PBIP/PBIR file, generates no DAX, changes no SQL, edits no semantic-model file,
and adds no pbi-cli automation. The handoff stops at implementation NOTES and names F016 as the
owner of any execution step (PBIP/PBIR authoring, pbi-cli, workspace publish).

---

## Verdict

| Field | Value |
|-------|-------|
| Blocking findings | `<count or "none">` |
| Warning findings | `<count or "none">` |
| Minor findings | `<count or "none">` |
| Overall | `<one-line summary of the page's readability and the top fixes>` |

> This verdict is a design-review INPUT, not a sign-off. It never sets `dashboard_ready: pass`
> -- that is the F011/012 dashboard-design verb owner's recorded design-review.

---

## See also

- **The procedure that fills this template:**
  `.claude/skills/powerbi-dashboard-design/workflows/screenshot-review.md`.
- **The anti-pattern reference (prose):** `docs/powerbi/visual-qa.md`; the QA procedure:
  `.claude/skills/powerbi-dashboard-design/workflows/dashboard-qa.md`.
- **Chart selection + visual objects:**
  `.claude/skills/powerbi-dashboard-design/workflows/visual-design-system.md`.
- **The router + the four surfaces:** `.claude/skills/powerbi-dashboard-design/SKILL.md`.
- **The gate to inherit + the four statuses:** `docs/readiness/dashboard-ready.md`,
  `docs/readiness/readiness-model.md`.
- **Metric definitions live upstream (referenced, never redefined here):** F009.
