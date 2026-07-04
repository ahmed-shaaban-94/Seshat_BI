# Phase 0 Research: Dashboard Accessibility + RTL/Arabic Readiness Checklist

## R1 -- Structural precedent: F034 (spec 039), NOT the theme-purity linter (spec 060)

**Decision**: Model this feature's shape on F034 (Visual Implementation MVP,
`specs/039-visual-implementation-mvp/`), not on spec 060 (Theme JSON Purity
Linter). F034's deliverable set -- one generic committed template, one
additive `evidence[]` edit to `docs/readiness/dashboard-ready.md`, one worked
example under `mappings/retail_store_sales/design/` -- is exactly this
feature's shape (per the spec's own "Boundary against neighbouring shipped
work" section and FR-008). Spec 060 instead adds a `src/retail/rules/*.py`
module, wires five governance golden records (`rules-manifest.json`,
`severity-posture.json`, `EXPECTED_RULE_IDS`, `rules/__init__.py`, a fixture
set) and changes the `retail check` rule count. This feature MUST NOT do any
of that (FR-008, SC-005; the spec explicitly declined the offered HR10
rule-id reservation in "Rule-id reservation decided against CT1").

**Rationale**: The SCOPE GUARD names "a Dashboard-Ready checklist evidence
item ... no rule-id" as the default, and the spec's boundary section already
resolved the rule-vs-evidence-item question against CT1 duplication. F034 is
the one shipped precedent that is an ADDITIVE Dashboard-Ready evidence item
with a generic template + worked instance and no new `retail check` id --
the load-bearing structural match.

**Alternatives rejected**: Copying spec 060's wiring shape (a new rule
module + golden-record touches). Rejected -- directly contradicts FR-008 and
the spec's own reasoning for declining HR10; would also duplicate CT1's
contrast math on a second surface, the exact duplicate-surface problem the
Collision-Avoidance guard exists to prevent.

## R2 -- What SHIPPED artifacts this feature reuses (cite, never re-derive)

- **`src/retail/rules/design_contrast.py` (CT1)** -- the WCAG contrast rule,
  already registered and shipped. This feature's contrast dimension CITES
  CT1's result for the page's token file; it never recomputes a ratio
  (FR-003, FR-004, US2).
- **`templates/visual-implementation-trace.md` + its F034 workflow
  (`.claude/skills/powerbi-dashboard-design/workflows/
  visual-implementation-review.md`)** -- the structural precedent for a
  generic, per-page, copy-me evidence template with a readiness-status
  header (four statuses + `evidence[]` + `blocking_reasons[]`), a FORBIDDEN
  OPERATIONS section, and a "how it handles a missing input" stop-and-ask
  section. This feature's checklist template follows the same shape (FR-001,
  FR-012).
- **`docs/readiness/dashboard-ready.md`, "Evidence item: 'design approved' vs
  'page implemented'"** -- the exact additive-evidence-item precedent this
  feature's stage-doc edit mirrors: no new status, no new gate, no new
  `retail check` rule, same owner (BI/report owner), same `evidence[]`
  mechanism (FR-007, FR-008).
- **`.claude/skills/powerbi-dashboard-design/workflows/dashboard-qa.md`
  paired with `docs/powerbi/visual-qa.md`** -- the catalog/prose-home split
  this feature reuses for the colorblind-safe and RTL/Arabic REVIEW CRITERIA
  (FR-005, FR-006, FR-009): a fixed, generic criteria list lives once in a
  prose doc; the checklist workflow/template CITES it rather than restating
  or reinventing per-page criteria. `dashboard-qa.md` also demonstrates the
  existing severity split (gate / purity / style) this feature must NOT
  silently collapse into a stricter or looser bar on its own authority
  (Q-FR014-SEVERITY stays open).
- **`docs/powerbi/visual-design-system.md`, "Accessible contrast"
  paragraph** (line ~90) -- the existing PROSE guidance this feature turns
  into a checked citation. The paragraph already states the design
  requirement; this feature does not restate contrast math there, it points
  the checklist's contrast dimension at CT1 + the token file instead.
- **`design/tokens/tower-retail-design-tokens.yaml`** (confirmed present on
  disk) -- a real `*-design-tokens.yaml` file CT1 already scans; the worked
  example's contrast dimension cites this file's current CT1 result, not a
  fictional path.
- **`themes/tower-retail.theme.json`** (confirmed present on disk) -- the
  committed theme file whose declared `dataColors` the worked example's
  colorblind-safe dimension reviews.
- **`mappings/retail_store_sales/design/`** (confirmed present: contains
  `dashboard-layout.md`, `visual-contract-binding-map.md`,
  `visual-list.md`) -- the existing per-subject-area co-location directory
  this feature's checklist instance and the visual-implementation-trace
  instance already share (Clarifications C1).
- **`templates/module-contract.md`** -- the authority-matrix boundary
  language (`Product Module / artifact-writing`) F034's trace template
  quotes verbatim; this feature's template reuses the identical boundary
  framing since it, too, only reads committed files and writes a derived
  evidence artifact -- it never approves, connects, publishes, or executes.

## R3 -- What this feature stays DISTINCT from (do not duplicate)

- **CT1 (`design_contrast.py`)** -- computes the ratio; this feature never
  re-derives one. It cites CT1's registered finding for the page's token
  file (US2, FR-003/FR-004).
- **Theme JSON Purity Linter (spec 060, `design_theme.py` when built)** --
  scans for FORBIDDEN KEYS (business logic in a styling file). This feature
  reviews LEGIBILITY of what the declared colors/layout produce for a
  reader -- a different question even over the same theme file.
- **`design_theme_fidelity.py`** -- checks token-to-theme FIDELITY (do two
  artifacts agree). This feature checks READABILITY of one artifact for an
  a11y/RTL audience, not agreement between two artifacts.
- **`templates/retail-term-dictionary.md`** -- Stage 1 Arabic<->English TERM
  MEANING for silver mapping. This feature is Stage 6 LAYOUT/DIRECTION
  readiness. Different stage, different concern; this feature does not read
  or edit the term dictionary.
- **`.claude/skills/powerbi-dashboard-design/workflows/mobile-layout.md`** --
  the precedent for a non-desktop layout concern recorded as a design
  workflow output (a `mobile notes` field), not a `retail check` rule. This
  feature's checklist is the analogous artifact for a11y/RTL, reinforcing
  (not inventing) the "layout concern as reviewed note, not mechanical rule"
  pattern.

## R4 -- Where the fixed, generic review criteria are documented once (FR-005/FR-006/FR-009)

**Decision**: Add the colorblind-safe and RTL/Arabic review-criteria lists as
a new prose section in `docs/powerbi/visual-design-system.md` (extending the
existing "Accessible contrast" guidance in the same document), and have the
checklist template's two dimensions CITE that section by link rather than
re-stating the criteria inline in every filled copy. This mirrors the
`dashboard-qa.md` (procedure/catalog) <-> `docs/powerbi/visual-qa.md` (prose
home) split already shipped: the readable "what these criteria mean and
why" lives in the `docs/powerbi/` prose doc; the checklist is the
copy-per-page PROCEDURE that cites it.

**Rationale**: FR-005/FR-006 require "a fixed, generic set of ... criteria
(documented once, referenced by every filled checklist)" -- documenting the
criteria once in the SAME doc that already carries the "Accessible contrast"
design principle keeps a11y/RTL guidance in one prose home, avoids forking a
second generic-criteria file, and directly satisfies User Story 3's "same
generic template ... same fixed review-criteria list" requirement. Adding
it to the EXISTING file is additive (no new top-level doc), matching the
Collision-Avoidance and YAGNI posture the SCOPE GUARD asks for.

**Alternatives rejected**:
- A brand-new standalone doc (e.g. `docs/powerbi/a11y-rtl-criteria.md`).
  Rejected as unnecessary surface multiplication (Principle VII) when the
  existing `visual-design-system.md` already anchors the "Accessible
  contrast" principle this feature operationalizes; extending it keeps one
  prose home for design-legibility principles, consistent with how
  `visual-qa.md` is the one prose home for anti-pattern explanations.
- Inlining the full criteria text into the template itself. Rejected --
  would force every filled per-page checklist to duplicate the same prose,
  which drifts under edit (fixable in one place vs. many) and does not match
  the `dashboard-qa.md`/`visual-qa.md` citation pattern already proven.

This is a reversible, plan-time default (like F034's O-1), not a Principle-V
judgment call -- it decides WHERE generic prose lives, not what a page's
scope or pass-bar is.

## R5 -- Contrast-citation resolution mechanic (per Clarifications C1)

**Decision**: The checklist's contrast dimension resolves which
`*-design-tokens.yaml` file to cite by following the SAME co-location
convention `visual-implementation-trace.md` already uses: the token file
already associated with the page's design mapping under
`mappings/<subject>/design/`. No new lookup mechanism, path index, or naming
convention is introduced.

**Rationale**: FR-015 / Clarifications C1 already resolve this by pointing
at the existing co-location convention; inventing a second, independent
resolution mechanism (e.g. a manifest mapping page IDs to token paths) would
be unnecessary surface (Principle VII) for a decision the spec already
settled as a default.

**Alternatives rejected**: A new `page-to-tokens.yaml` index file. Rejected
-- no evidence of a real ambiguity case in the current one-token-file /
one-theme-file corpus; adding an index before there are multiple candidate
token files per subject area would be speculative (YAGNI).

## R6 -- Input-source confirmation (files this feature's worked example cites are REAL)

Confirmed present on disk in this worktree (not fictional paths):

| Path | Confirmed | Role for this feature |
|------|-----------|------------------------|
| `design/tokens/tower-retail-design-tokens.yaml` | yes (glob) | contrast dimension's cited token file for the worked example |
| `themes/tower-retail.theme.json` | yes (glob) | colorblind-safe dimension's cited `dataColors` source |
| `src/retail/rules/design_contrast.py` (CT1) | yes (read) | the rule whose result the contrast dimension cites |
| `docs/readiness/dashboard-ready.md` | yes (read) | the Stage 6 gate doc this feature additively edits |
| `templates/visual-implementation-trace.md` | yes (read) | the structural template precedent |
| `mappings/retail_store_sales/design/` (3 files) | yes (glob) | the co-location directory for the worked instance |
| `docs/powerbi/visual-design-system.md` ("Accessible contrast") | yes (grep, line ~90) | the prose principle this feature operationalizes into checked evidence |
| `.claude/skills/powerbi-dashboard-design/workflows/dashboard-qa.md` | yes (read) | the catalog/prose-home split precedent (R4) |

No path in this research or the resulting plan/data-model/quickstart is
invented without a corresponding confirmed file or a clearly-marked FUTURE
edit target.

## R7 -- Deferred capabilities NOT assumed (Principle VIII)

This feature's design assumes NONE of the following exist or run:

- **F016 (Power BI execution adapter)** -- does not exist; not called,
  imported, or referenced as available. No visual is rendered, no report is
  opened, no Power BI Desktop or MCP connection occurs at any point in the
  checklist-filling procedure.
- **Any live database connection** -- this feature reads only committed
  static text (YAML/JSON/Markdown) already on disk; it opens no DSN, no
  Postgres connection, and does not depend on `retail validate`'s optional
  `db` extra.
- **Any CVD (color-vision-deficiency) simulation engine** -- the
  colorblind-safe dimension is a documented HUMAN/agent-read judgment
  against fixed criteria (FR-005), never a numeric simulation score. A
  future deterministic CVD-simulation rule over a `dataColors` palette is
  explicitly named in the spec's Assumptions as a SEPARATE, not-yet-specified
  feature this one does not build or presuppose.
- **A new `retail check` rule / rule id** -- FR-008 forbids it; this
  research and the plan that follows introduce no rule module, no registry
  wiring, and no golden-record touch.
- **A new readiness stage or `dashboard_ready` status value** -- FR-008
  forbids both; the four existing statuses (`not_started` / `blocked` /
  `warning` / `pass`) are reused verbatim.
- **An automated staleness detector** -- per Clarifications C2, staleness is
  a human review-discipline obligation at the existing design-review
  sign-off, not a new timestamp/hash/diff mechanism.
- **A roadmap-ledger edit** -- the spec's Assumptions state the new
  F-number, if any, "is a roadmap-ledger edit at plan time, not invented
  here." This plan records F039 as the TENTATIVE next-free number (the
  highest currently allocated is F038; see `docs/roadmap/roadmap.md`) for
  cross-reference only. It does NOT edit `docs/roadmap/roadmap.md` in this
  stage -- that file is a shared surface across the 19 parallel in-flight
  features and editing it here would risk exactly the collision the
  COLLISION-AVOIDANCE ALLOCATION guard exists to prevent. The roadmap edit,
  if wanted, is a separate follow-up action for whoever lands this feature.

## R8 -- Open Principle-V questions carried forward, not resolved here

Per the spec's `## Clarifications` "Principle-V carve-out (OPEN)" section,
Q-FR014-SCOPE (RTL-dimension applicability default) and Q-FR014-SEVERITY
(block-vs-warning pass-bar) remain OPEN for a named human ruling. This
research, and the plan/data-model/quickstart that follow, treat both as
UNRESOLVED: the design accommodates either answer without needing to be
re-shaped (the checklist records a not-applicable-with-reason field and a
severity-disposition field regardless of which way the ruling goes), and no
artifact in this feature answers either question on the business's behalf.
