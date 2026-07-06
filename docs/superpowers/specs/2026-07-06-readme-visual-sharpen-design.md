# README Visual Sharpen -- Design

- **Date:** 2026-07-06
- **Scope:** Presentation-only upgrade of the root `README.md`. No content change.
- **Trigger:** "make a professional and visually brilliant README."
- **Outcome after brainstorming:** the README is already strong and link-clean;
  the honest gap is asset-shaped, not content-shaped. This spec covers a
  **targeted sharpen**, not a rewrite.

---

## 1. Guiding constraint -- content is frozen

Every factual claim in the README is governance-load-bearing in a product whose
entire premise is *never faking status*: the "What is built today" vs "Roadmap"
split, the `warning` states, "never fakes a pass", F016 "gated by design". This
pass **preserves every factual statement verbatim.** If a content change ever
seems warranted, it is surfaced as an explicit question -- never folded into a
visual edit. (Ref: memory `stale-docs-are-gate-defined`.)

Baseline verified before any edit: **all 18 doc links + 3 brand assets + 5
top-level files referenced by the README resolve.** The README is already
link-clean; this pass must not break that.

## 2. GitHub render constraints (the whole toolkit)

GitHub's Markdown/HTML sanitizer strips `class` and `style` -- **there is no
CSS.** The only visual levers are: image assets, shields.io badges (with `logo=`
+ hex), Mermaid, aligned tables, `<div align>`, `<details>`, and `<picture>` for
light/dark. The current README already uses most of these well -- which is why
the gap is small. Additional SVG constraint: GitHub sanitizes referenced SVGs
and **blocks embedded/linked web fonts**, so any `<text>` relying on a web font
falls back unpredictably. Mitigation: hero text is drawn as **vector paths /
simple geometry**, not font-dependent `<text>`.

## 3. Changes (three)

### 3.1 Hero banner -- one new asset

- **File:** `assets/brand/seshat-bi-hero.svg`, `viewBox="0 0 1280 360"`.
- **Composition** (mirrors the brand board's WORDMARK lockup):
  - Left: gold crescent-orbit ring + seven-point star (path reused verbatim from
    `assets/brand/seshat-seven-star.svg`) + teal data-network nodes.
  - Right: "SESHAT" wordmark -> gold divider rule -> teal "BI" -> wide-tracked
    "RETAIL BI READINESS SYSTEM" -> gold hairline -> tagline
    "From messy retail data to trusted, governed BI."
  - Field: deep navy `#001E35` with a subtle `midnight_navy #04172A` radial;
    thin gold frame.
- **Text rendering:** geometric/outlined, font-independent.
- **Brand rule compliance:** star is verifiably **seven-pointed** (rule #1);
  teal nodes read as a data network (rule #5); palette exact (section 5 of the
  visual-identity doc).
- **Known limitation (accepted by user):** this is a clean *geometric
  interpretation* of the wordmark, not a pixel replica of the commissioned
  Cinzel-style serif on the brand board. If exact board typography is later
  required, export the real asset and swap the file (same path, same layout).

### 3.2 Badge row upgrade

Same six badges, sharpened: add `logo=` (powerbi / python / postgresql), set
`labelColor=001E35` (deep navy) and brand-hex accent colors (gold `C69214`,
teal `0B9A9A`). Flat style (not `for-the-badge`) -- cleaner for a technical repo.
No badge is added or removed; only styling changes.

### 3.3 Header polish

Replace the 280px square logo with the hero SVG; keep tagline + `<br/>` + badge
row + `---` divider; tighten spacing. No structural change below the fold.

## 4. Explicitly out of scope

- No prose edits below the header block.
- No new sections, no reordering.
- No `<picture>` light/dark variant (navy logo already survives both themes).
- No fabricated raster art.

## 5. Verification

1. Render the SVG (headless browser screenshot) -- confirm seven points,
   correct palette, legible wordmark.
2. Re-run the link/asset integrity check -- all still resolve.
3. Confirm new files are ASCII / UTF-8 without BOM (repo hard rule).
4. `retail check` unaffected (README + brand SVG are outside gated surfaces; a
   green check must remain green).
