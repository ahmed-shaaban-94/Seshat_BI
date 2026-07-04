# Quickstart: Dashboard Accessibility + RTL/Arabic Readiness Checklist

How an agent or a BI/report owner exercises this feature once the four
Phase-1 artifacts exist (the template, the criteria-doc extension, the
stage-doc evidence-item edit, and a worked instance). This is a
docs/template feature -- there is no CLI subcommand, no pytest suite, and
no `retail check` rule to invoke; the "build" is authoring committed
Markdown, and the "run" is a manual fill-and-review procedure plus a
handful of deterministic greps.

## Prerequisites

- `semantic_model_ready` is `pass` for the subject area (the same
  precondition `visual-implementation-trace.md` already requires) -- a
  page cannot reach `dashboard_ready` before its contracts exist.
- The page's design-review (visual -> contract binding) is otherwise
  underway or complete; this checklist is ADDITIONAL required evidence, not
  a replacement for that review.
- `retail check` is runnable locally (no new extra needed -- CT1 is
  already shipped and requires no live DB).

## Filling a checklist for a new page (the per-page procedure)

1. **Copy the generic template.** Copy
   `templates/a11y-rtl-readiness-checklist.md` to
   `mappings/<subject>/design/a11y-rtl-readiness-checklist.md` (or append a
   new page section if the subject area already has one). Do not invent new
   dimension labels or criteria -- the three dimensions and their fixed
   criteria references are FIXED by the template (User Story 3).

2. **Fill the contrast dimension by CITING CT1, never re-deriving it.**
   - Resolve the page's `*-design-tokens.yaml` file the same way
     `visual-implementation-trace.md` already resolves its inputs: the
     token file already associated with this page's design mapping under
     `mappings/<subject>/design/` (Clarifications C1).
   - Run `retail check` and read CT1's current finding for that exact file.
   - If CT1 reports no finding for that file: `disposition: reviewed-clean`,
     `ct1_result: clean`.
   - If CT1 reports an open ERROR, a parse failure, or the file cannot be
     found: `disposition: blocked`, `ct1_result` records the CT1 finding
     text verbatim (or `file-not-found`), and this becomes a
     `blocking_reasons[]` entry on the checklist. Do NOT mark this
     dimension `reviewed-clean` while an open CT1 finding exists (FR-004).

3. **Fill the colorblind-safe dimension against the documented-once
   criteria.**
   - Cite the page's declared theme/palette file (e.g.
     `themes/<name>.theme.json`) as `palette_source`.
   - Read the fixed criteria at
     `docs/powerbi/visual-design-system.md` ("Colorblind-safe palette
     separation" subsection, added by this feature) and review the page's
     declared multi-series `dataColors` against them.
   - If the page declares no multi-series palette at all (a single-series
     page): `disposition: not-applicable-with-reason`, `reason: "no
     multi-series dataColors palette declared on this page"` -- never
     silently skip the row.
   - If a genuine separation defect is found (e.g. two adjacent series
     distinguishable by hue alone): `disposition: blocked`,
     `finding_detail` names the colors and proposes the accessible
     alternative (a second encoding: pattern, label, or position).
   - Otherwise: `disposition: reviewed-clean`.

4. **Fill the RTL/Arabic layout dimension against the documented-once
   criteria -- respecting the OPEN scope ruling.**
   - Cite the page's layout/blueprint artifact (e.g.
     `mappings/<subject>/design/dashboard-layout.md`) as `layout_source`.
   - Read the fixed criteria at `docs/powerbi/visual-design-system.md`
     ("RTL/Arabic layout readiness" subsection) and review text direction,
     mirrored visual/axis alignment (where direction carries meaning), and
     Arabic numeral/date formatting expectations.
   - **STOP before marking this dimension `not-applicable-with-reason`**
     unless a named human has EXPLICITLY ruled this specific page
     LTR-only/English-only (Q-FR014-SCOPE is OPEN). An assumed default
     ("probably fine, no Arabic audience for this one") is NOT a valid
     citation -- record `scope_ruling_citation` naming the actual human
     ruling, or leave the dimension actively reviewed (not exempted).
   - If a genuine RTL/mirroring defect is found (e.g. a trend chart's
     implied left-to-right time direction is not mirrored for RTL
     readers): `disposition: blocked`, `finding_detail` names the defect
     and proposes the RTL-correct alternative (FR-011) -- never silently
     overridden, never silently complied with.
   - Otherwise: `disposition: reviewed-clean`.

5. **Roll up and cite in `evidence[]`.** Set `overall_status` to the worst
   of the three dimension dispositions (mapped onto the four readiness
   statuses, per `data-model.md`). If all three are `reviewed-clean` or a
   validly-cited `not-applicable-with-reason`, the checklist itself is
   ready to be cited as an `evidence[]` entry for `dashboard_ready`. The
   checklist does NOT itself set `dashboard_ready: pass` -- hand the filled,
   clean checklist to the BI/report owner's existing design-review sign-off
   (`docs/readiness/dashboard-ready.md`, "Required owner / approval").

6. **STOP on any open finding rather than downgrading it silently.** Per
   the interim floor recorded in `dashboard-ready.md`'s new evidence-item
   subsection: any dimension left `blocked` is AT LEAST a `warning`-class
   finding cited in `blocking_reasons[]`; whether it additionally forces
   `dashboard_ready` to `blocked` for this page is the pending
   Q-FR014-SEVERITY ruling -- do not resolve that on your own authority.

## Re-filling after a cited file changes (staleness -- Clarifications C2)

There is no automated staleness detector. When a reviewer re-confirms a
`dashboard_ready: pass` claim, they are responsible for checking whether the
cited token/theme/layout file has changed since the checklist was filled. If
it has, treat the checklist as STALE and re-run steps 2-5 above before
relying on it for a fresh `pass` claim.

## Deterministic checks (no pytest suite; a docs/template feature)

Run these before considering the feature's authored artifacts complete:

- **No C086/pharmacy leakage in generic files** -- grep
  `templates/a11y-rtl-readiness-checklist.md` and the new
  `docs/powerbi/visual-design-system.md` subsections for any
  `retail_store_sales`/pharmacy-specific noun, color literal, or grain key.
  Expect zero matches (SC-004).
- **No literal Arabic string in the generic template** -- grep the template
  file for non-ASCII bytes. Expect zero matches (FR-013). (A filled
  per-page instance MAY carry a real Arabic example if one is used; the
  GENERIC template never does.)
- **No numeric score field anywhere** -- grep the template, the criteria
  extension, the stage-doc edit, and the worked instance for
  `score`/`confidence`/`health`/`maturity`/`completeness` used as a
  numeric field. Expect zero matches (SC-003, hard rule #9).
- **`retail check` rule count unchanged** -- run `retail check` (or `retail
  manifest`) before and after this feature's changes; the registered rule
  id set is IDENTICAL (SC-005). This feature adds no rule module and
  touches no golden record.
- **Every worked-instance citation resolves to a real file** -- for the
  `retail_store_sales` worked example, confirm
  `design/tokens/tower-retail-design-tokens.yaml`,
  `themes/tower-retail.theme.json`, and
  `mappings/retail_store_sales/design/dashboard-layout.md` all exist on
  disk and that the cited CT1 result matches what `retail check` actually
  reports for that token file at authoring time (SC-006).
- **ASCII / UTF-8-no-BOM** on every new/edited file (Principle IX).

## What this feature does NOT let you do

- It does NOT render, open, publish, or connect to Power BI Desktop, a live
  semantic model, or the Power BI execution adapter (F016 remains gated and
  unbuilt) -- filling the checklist is a purely static, read-committed-text
  procedure.
- It does NOT add a `retail check` rule id, a new readiness stage, or a new
  `dashboard_ready` status value -- if you find yourself editing
  `src/retail/rules/`, `docs/rules/rules-manifest.json`, or
  `tests/unit/test_rules_wiring.py` for this feature, stop: that is out of
  scope (the SCOPE GUARD default; the spec explicitly declined the offered
  HR10 rule-id reservation).
- It does NOT let the agent decide, on its own authority, that a page is
  RTL-out-of-scope by default, or that an open finding is merely a
  `warning` rather than `blocked` -- both are OPEN Principle-V questions
  (Q-FR014-SCOPE, Q-FR014-SEVERITY) awaiting a named human ruling. Raise
  them; do not answer them.
- It does NOT emit a numeric confidence/health/maturity score or a
  completeness count anywhere (hard rule #9).
