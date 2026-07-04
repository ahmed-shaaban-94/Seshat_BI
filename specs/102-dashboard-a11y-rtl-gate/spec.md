# Feature Specification: Dashboard Accessibility + RTL/Arabic Readiness Checklist

**Feature Branch**: `102-dashboard-a11y-rtl-gate`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "H9 (gap #14). Dashboard accessibility + RTL/Arabic layout
readiness: make a11y (WCAG contrast, colorblind-safe) and RTL/Arabic layout CHECKED
Dashboard-Ready evidence items, not just design guidance."

## Overview

Seshat BI's retail audience reads Arabic and expects right-to-left layout; the repo
already ships a bilingual retail-term dictionary (`templates/retail-term-dictionary.md`,
Stage 1) that records Arabic-to-English term meanings. But at Stage 6 (Dashboard Ready),
accessibility and RTL/Arabic layout are only PROSE GUIDANCE: `docs/powerbi/
visual-design-system.md` states "Accessible contrast" as a design principle, and
`dashboard-qa.md` / `screenshot-review.md` treat a contrast or readability problem as a
`warning`-class design NOTE -- recorded, but never a required, filled, reviewed piece of
evidence a dashboard needs before `dashboard_ready` can be `pass`. Nothing in the stage
today asks, as a checked item, "was this page's layout reviewed for RTL/Arabic support?"
or "was this page's palette checked for colorblind-safety?" -- and colorblind-safe
palette separation is not covered by any existing mechanical rule.

This feature turns a11y (WCAG contrast, colorblind-safe palette) and RTL/Arabic layout
readiness into a REQUIRED, REVIEWED Dashboard-Ready evidence item -- a static checklist
filled per dashboard page against committed design/theme artifacts, cited in
`evidence[]` the same way the F034 visual-implementation-trace evidence item already is.
It does not render or execute Power BI (F016 is gated and does not exist), and it
introduces no numeric score.

## Boundary against neighbouring shipped work (read first)

This feature is a genuine EXTENSION of existing a11y guidance into checked evidence, not
a restatement of an existing rule or dictionary. The real shipped neighbours it must stay
distinct from:

- **CT1 / `src/retail/rules/design_contrast.py`** (spec-adjacent, already registered)
  computes the WCAG 2.x contrast ratio between DECLARED `colors.text.*` /
  `colors.background` pairs in committed `*-design-tokens.yaml` files against a
  token-declared floor, and fails closed. This feature does NOT duplicate CT1's math or
  re-scan the same file for the same pairs -- the checklist CITES CT1's pass/fail result
  as one input line for the contrast dimension. It covers what CT1 structurally cannot:
  RTL/Arabic layout review and colorblind-safe palette-separation review, which are not
  mechanically checkable without rendering the report (F016, gated).
- **Theme JSON Purity Linter (spec 060, forbidden-key scan)** enforces that a theme JSON
  file carries no business-logic KEY (DAX, measure, threshold, rule). This feature is
  about a11y/RTL LEGIBILITY REVIEW of what the theme's declared colors/layout produce for
  a reader, not about which keys a theme file is allowed to contain -- a distinct concern
  even where both read the same committed theme file.
- **`src/retail/rules/design_theme_fidelity.py`** checks that a committed theme's palette
  matches the declared design tokens (token-to-theme fidelity). This feature does not
  check fidelity between two artifacts; it checks legibility/layout-readiness of one
  artifact for an accessibility and RTL/Arabic audience.
- **F034 Visual Implementation MVP** (`docs/readiness/dashboard-ready.md`, "Evidence item:
  'design approved' vs 'page implemented'") is the structural precedent this feature
  mirrors: an ADDITIVE evidence item on the SAME Dashboard Ready stage that adds NO new
  status, NO new gate, and NO new `retail check` rule, and does not change the stage's
  owner, required checks, or blocking reasons.
- **`templates/retail-term-dictionary.md`** (Stage 1, Source Ready) records Arabic <->
  English TERM MEANING for silver mapping. This feature is Stage 6 dashboard LAYOUT/
  DIRECTION readiness (does the page read correctly right-to-left, is it legible) -- a
  different stage and a different concern; it does not read or alter the term
  dictionary.
- **`.claude/skills/powerbi-dashboard-design/workflows/mobile-layout.md`** is the reflow
  precedent for a non-desktop layout concern living as a design workflow output (a
  `mobile notes` field) rather than a retail-check rule; this feature's checklist is the
  analogous artifact for RTL/a11y, not a rule.

This feature adds NO new readiness stage, NO new `dashboard_ready` status value, and (per
the Collision-Avoidance default below) NO new `retail check` rule identifier. It reuses
the F024 evidence-item shape; a new roadmap F-number, if warranted, is a roadmap-ledger
edit at plan time, not invented here.

### Rule-id reservation decided against CT1 (no HR10)

The task framing offered reserving a static-rule id (HR10) "if it truly adds a
`retail-check` rule (contrast on committed theme.json)." Contrast-on-a-committed-color-
artifact is exactly what CT1 already computes (against `*-design-tokens.yaml`); adding a
second rule to recompute the same WCAG math against a different file name would be the
duplicate-surface problem the Collision-Avoidance guard exists to prevent, not a new
concern. RTL/Arabic layout and colorblind-safe legibility, in turn, are not mechanically
verifiable from static text without rendering the report (Principle VIII; F016 is
gated). This feature therefore reserves NO rule id and adds a Dashboard-Ready checklist
evidence item instead, citing CT1's result for the contrast dimension.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A dashboard cannot reach Dashboard Ready without a filled a11y/RTL checklist (Priority: P1)

A BI report owner has a page whose visuals already bind to approved metric contracts
(the existing `dashboard_ready` design-review requirement). Before recording
`dashboard_ready: pass`, they must also fill a committed a11y/RTL readiness checklist for
that page: it cites CT1's contrast result, records a colorblind-safe palette-separation
review, and records an RTL/Arabic layout review (text direction, mirrored visual
alignment, numeral/date formatting). Only once the checklist is filled and reviewed does
the stage's evidence show it; an unfilled or missing checklist is a recorded blocker.

**Why this priority**: This is the whole point of the feature -- moving a11y/RTL from
prose guidance to a required, checked artifact. Without this, the feature delivers
nothing.

**Independent Test**: For a page whose design-review is otherwise complete, attempt to
record `dashboard_ready: pass` with the a11y/RTL checklist absent or containing an
unfilled placeholder; confirm the stage is `blocked` naming the missing/unfilled
checklist. Then fill the checklist with all three dimensions reviewed and confirm the
blocker clears.

**Acceptance Scenarios**:

1. **Given** a page with an approved visual -> contract binding map but no committed
   a11y/RTL checklist, **When** `dashboard_ready` status is evaluated, **Then** the stage
   records a blocker naming the missing checklist path and does not reach `pass`.
2. **Given** a page with a committed a11y/RTL checklist that still contains an unfilled
   `<placeholder>` in any of the three reviewed dimensions (contrast, colorblind-safe
   palette, RTL/Arabic layout), **When** the stage is evaluated, **Then** it is `blocked`
   naming the unfilled dimension.
3. **Given** a page with a fully filled a11y/RTL checklist (all three dimensions reviewed
   with evidence) and an otherwise-complete design review, **When** the stage is
   evaluated, **Then** the checklist is cited in `evidence[]` alongside the existing
   design-review evidence and does not itself block `pass`.

---

### User Story 2 - The checklist cites CT1 rather than re-deriving contrast (Priority: P1)

A contributor filling the checklist for the contrast dimension does not re-measure colors
by hand or invent a pass/fail judgment; they cite the committed `*-design-tokens.yaml`
file and the current `retail check` CT1 result for that file. If CT1 reports an ERROR for
the page's token file, the checklist's contrast dimension cannot be marked reviewed-clean
-- it must reflect CT1's actual finding.

**Why this priority**: Without this, a filled checklist could silently contradict the
mechanical CT1 result, defeating the "fails closed" property (Principle I) that CT1
already provides. This is required for the checklist to be trustworthy from day one.

**Independent Test**: Fill a checklist's contrast dimension for a page whose token file
currently fails CT1; confirm the checklist cannot be marked clean for that dimension and
instead surfaces the CT1 finding as a blocker.

**Acceptance Scenarios**:

1. **Given** a page's design-tokens file passes CT1 with zero findings, **When** the
   checklist's contrast dimension is filled, **Then** it cites the token file path and
   states the CT1 result as clean.
2. **Given** a page's design-tokens file has an open CT1 ERROR finding, **When** the
   checklist's contrast dimension is filled, **Then** it cannot be marked clean -- it
   records the open CT1 finding as a blocker for the checklist.
3. **Given** a page whose design-tokens file cannot be found, **When** the checklist's
   contrast dimension is filled, **Then** it records that missing file as a blocker
   rather than inventing a passing result.

---

### User Story 3 - Colorblind-safe and RTL/Arabic dimensions are reviewed against committed criteria, not invented per page (Priority: P2)

An analyst filling the colorblind-safe and RTL/Arabic dimensions for a new page follows
the SAME generic review criteria every other page uses (a documented, generic checklist
of what "colorblind-safe" and "RTL/Arabic-ready" mean for a Power BI page), rather than
each reviewer inventing their own bar. The criteria are generic (Principle VII): no
worked-example (C086 / retail_store_sales) domain specifics are baked into the checklist
template.

**Why this priority**: Consistency and genericity make this a reusable evidence item
rather than a one-off review; a single working checklist (P1 stories) already delivers
the core value, so this is P2.

**Independent Test**: Fill the checklist for two different pages using the same generic
template; confirm both cite the same generic review criteria and neither checklist
contains a C086/pharmacy-specific label, color literal, or grain key.

**Acceptance Scenarios**:

1. **Given** the generic a11y/RTL checklist template, **When** it is copied for a new
   page, **Then** the copied checklist references the same fixed review-criteria list
   (no page-specific criteria invented).
2. **Given** two filled checklists for two different pages, **When** compared, **Then**
   both use identical dimension labels and criteria wording, differing only in the
   per-page evidence/citations.
3. **Given** the generic template, **When** inspected, **Then** it contains no
   C086/pharmacy-specific domain noun.

---

### Edge Cases

- What happens when a page has no `dataColors` palette declared at all (e.g., a
  single-series page)? The colorblind-safe dimension records that no multi-series palette
  separation applies and is marked not-applicable-with-reason, never silently skipped.
- What happens when a page is explicitly scoped as English-only / LTR-only (no Arabic
  audience for that specific page)? [NEEDS CLARIFICATION -- resolved to OPEN owner
  ruling, see ## Clarifications, Q-FR014-SCOPE] -- this is a business-policy/
  audience-scope call the agent must not decide for itself.
- What happens when CT1 itself cannot run (e.g., the token file fails to parse)? The
  checklist's contrast dimension records CT1's own parse-failure finding as a blocker; it
  does not attempt an independent contrast judgment.
- What happens when a page was reviewed for a11y/RTL and later the theme/token file
  changes? The checklist becomes STALE evidence; re-filling it is required before the
  next `dashboard_ready: pass` claim relies on it (the checklist is not evaluated as an
  immutable one-time pass).
- What happens when the checklist flags a genuine RTL/mirroring defect (e.g., a trend
  chart's implied left-to-right time direction is not mirrored for RTL readers)? That is
  recorded as a `warning`- or `blocked`-class finding per the resolved pass-bar [NEEDS
  CLARIFICATION -- resolved to OPEN owner ruling, see ## Clarifications, Q-FR014-SEVERITY],
  proposing the accessible/RTL-correct alternative -- never silently overridden and never
  silently complied with (Principle V/VI, matching the existing dashboard-qa.md
  stop-and-ask discipline).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST define a generic a11y/RTL readiness checklist template
  (analogous in shape to `templates/visual-implementation-trace.md`) covering exactly
  three reviewed dimensions per dashboard page: (a) WCAG contrast, (b) colorblind-safe
  palette separation, and (c) RTL/Arabic layout readiness.
- **FR-002**: The checklist MUST be a STATIC evidence item filled per page against
  already-committed design/theme artifacts. It MUST NOT render, open, publish, or connect
  to Power BI Desktop, a live semantic model, or any deferred execution surface (F016;
  Principle VIII).
- **FR-003**: For the contrast dimension, the checklist MUST cite the relevant committed
  `*-design-tokens.yaml` file path and the current CT1 (`design_contrast.py`) result for
  that file; it MUST NOT re-derive a contrast ratio or assert a contrast judgment that
  contradicts CT1's registered finding.
- **FR-004**: When CT1 reports an open ERROR finding (or a parse failure) for the page's
  relevant token file, the checklist's contrast dimension MUST NOT be marked
  reviewed-clean; it MUST record the CT1 finding as a blocker.
- **FR-005**: For the colorblind-safe dimension, the checklist MUST record, per page, a
  review of the page's declared multi-series `dataColors` (or category palette) against a
  fixed, generic set of colorblind-safe review criteria (documented once, referenced by
  every filled checklist) -- or record not-applicable-with-reason when the page declares
  no multi-series palette (see Edge Cases). This review is a documented HUMAN/agent-read
  judgment against fixed criteria, not a numeric simulation score.
- **FR-006**: For the RTL/Arabic layout dimension, the checklist MUST record, per page, a
  review against a fixed, generic set of RTL/Arabic layout review criteria (text
  direction, mirrored visual/axis alignment where direction carries meaning, Arabic
  numeral/date formatting expectations) -- or record not-applicable-with-reason per the
  resolved audience-scope ruling [NEEDS CLARIFICATION -- resolved to OPEN owner ruling,
  see ## Clarifications, Q-FR014-SCOPE].
- **FR-007**: The checklist MUST be cited as a REQUIRED item in `dashboard_ready`
  `evidence[]` before that stage may record `pass`, for every dashboard page -- an
  absent, missing, or partially-unfilled (`<placeholder>` remaining in any dimension)
  checklist MUST be a recorded `blocking_reasons[]` entry. A dimension that genuinely does
  not apply to a page (e.g., RTL/Arabic layout on a page a human has ruled out of that
  scope, per FR-014) is filled as not-applicable-with-reason, which counts as filled --
  it is never left blank or silently omitted. This is enforced the same way the existing
  "every visual maps to a contract" design-review requirement is enforced today: by the
  human design-review sign-off gate on `dashboard_ready`, NOT by a new `retail check`
  rule (Principle I fails-closed via the existing gate, not a new mechanical rule).
- **FR-008**: This feature MUST add NO new `dashboard_ready` status value, NO new
  readiness stage, and NO new `retail check` rule identifier (Collision-Avoidance
  default, reasoned in "Rule-id reservation decided against CT1" above). It is an
  ADDITIVE evidence item on the existing Dashboard Ready gate, matching the F034
  precedent's non-disruption guarantee.
- **FR-009**: The checklist and its template MUST stay generic (Principle VII): the
  worked example (C086 / retail_store_sales) may appear only as a cited filled instance,
  never inlined into the template or a fixed dimension label; the module MUST resolve a
  generic per-page path under the page's design mapping location.
- **FR-010**: The checklist MUST record staleness discipline: when the cited
  design-tokens/theme file changes after a checklist was filled, the prior checklist
  entry is treated as STALE and MUST be re-filled before it is relied on for a fresh
  `dashboard_ready: pass` claim (Edge Cases). Per FR-008 (no new `retail check` rule),
  staleness detection is a human REVIEW-DISCIPLINE obligation enforced at the existing
  design-review sign-off, not a mechanical timestamp/hash check -- there is no new
  automated staleness detector (see Clarifications, C2).
- **FR-011**: A genuine RTL/mirroring or colorblind-safety defect the checklist surfaces
  MUST be recorded as a `warning`- or `blocked`-class finding (per the resolved pass-bar)
  with the proposed accessible/RTL-correct alternative; it MUST NOT be silently
  overridden and MUST NOT be silently complied with against the reviewer's own finding
  (Principle V/VI, matching the existing dashboard-qa.md stop-and-ask discipline).
- **FR-012**: The checklist MUST NOT emit any numeric confidence/health/maturity score or
  a completeness count (hard rule #9); each dimension is recorded as
  reviewed-clean / not-applicable-with-reason / blocked, with evidence, only.
- **FR-013**: All authored artifacts MUST be ASCII, UTF-8 without BOM (use `--` and `->`,
  no glyphs -- including no literal Arabic string in the generic template; a real Arabic
  example, if any, lives only in a filled per-page instance, never the template), and
  MUST use short repo-relative paths (Windows 260-char budget) (Principle IX).
- **FR-014**: Whether the RTL/Arabic layout DIMENSION applies to a given page (some pages
  may be explicitly ruled English-only/LTR-only by a human, versus every page being
  potentially read by an Arabic-speaking audience by default), and whether an open
  finding in any dimension makes the page `blocked` or only downgrades it to `warning`
  (the way contrast currently does in dashboard-qa.md today), are business-policy /
  audience-scope decisions. The checklist itself is always required (FR-007); what is
  open is the RTL-dimension applicability default (see ## Clarifications,
  Q-FR014-SCOPE) and the block-vs-warning severity bar (see ## Clarifications,
  Q-FR014-SEVERITY). [NEEDS CLARIFICATION -- resolved to OPEN owner ruling, see
  ## Clarifications: (a) is every page presumed in-scope for RTL/Arabic review unless a
  human explicitly marks it LTR-only, or the reverse (out-of-scope unless flagged in)?
  (b) does an open a11y/RTL finding make `dashboard_ready` `blocked`, or only downgrade
  it to `warning` as contrast findings do today? This is a Principle-V judgment call the
  agent must not decide for itself; it is raised here for a named human ruling, not
  answered by a default.]
- **FR-015**: The checklist MUST resolve, per page, which committed
  `*-design-tokens.yaml` file the contrast dimension (FR-003) cites by following the
  same co-location convention as the F034 visual-implementation-trace evidence item: the
  token file already associated with that page's design mapping under the subject
  area's `design/` location (see Clarifications, C1). This is a path-resolution default,
  not an invented mapping -- it reuses an existing, already-committed association rather
  than introducing a new lookup mechanism.

### Key Entities

- **A11y/RTL Readiness Checklist**: the per-page, committed evidence artifact this
  feature defines -- three reviewed dimensions (contrast, colorblind-safe palette,
  RTL/Arabic layout), each recorded as reviewed-clean / not-applicable-with-reason /
  blocked, with a citation to its evidence source. Carries no score.
- **Contrast dimension**: cites the page's `*-design-tokens.yaml` file and the current
  CT1 rule result; never re-derives a contrast judgment.
- **Colorblind-safe dimension**: a review of the page's declared multi-series palette
  against a fixed, generic set of colorblind-safe criteria.
- **RTL/Arabic layout dimension**: a review of the page's layout (text direction, mirrored
  alignment, numeral/date formatting) against a fixed, generic set of RTL/Arabic criteria.
- **Dashboard Ready evidence item**: the existing Stage 6 gate this feature extends
  additively, following the F034 precedent -- no new status, gate, or rule.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of pages recording `dashboard_ready: pass` after this feature ships
  have a committed a11y/RTL checklist with all three dimensions filled (reviewed-clean or
  not-applicable-with-reason) -- zero pages reach `pass` with an unfilled dimension.
- **SC-002**: 0 filled checklists assert a contrast judgment that contradicts the current
  CT1 result for the cited token file.
- **SC-003**: 0 generated/filled checklists, and the generic template, contain a numeric
  confidence/health/maturity score or a completeness count.
- **SC-004**: 0 generic template artifacts contain a worked-example (C086/pharmacy)
  domain specific or a literal Arabic string.
- **SC-005**: This feature adds exactly 0 new `retail check` rule identifiers and exactly
  0 new `dashboard_ready` status values (verified against the rule registry and
  `readiness-model.md` before/after).
- **SC-006**: A named human can trace every checklist dimension's evidence to a committed
  repo-relative path (the token file for contrast; the theme/palette file for
  colorblind-safety; the page blueprint/layout artifact for RTL) with no unsourced claim.

## Assumptions

- CT1 (`src/retail/rules/design_contrast.py`) remains the authoritative, already-shipped
  mechanical contrast check; this feature composes its result rather than re-implementing
  contrast math.
- `docs/readiness/dashboard-ready.md` remains the authoritative Stage 6 gate definition;
  this feature edits it additively (a new required evidence item), following the F034
  precedent, and does not alter its status vocabulary, owner, or blocking-reasons shape.
- Colorblind-safe palette-separation and RTL/Arabic layout readiness are NOT mechanically
  verifiable from committed static text alone without rendering the report (Principle
  VIII); this feature is therefore a documented review checklist, not a `retail check`
  rule, until/unless a future deterministic static check (e.g., CVD-simulation math over
  a `dataColors` palette) is separately specified and ruled non-duplicative of CT1.
  Colorblind-safe review in this feature is a documented judgment against fixed criteria,
  not a numeric simulation.
- The generic per-page location for the filled checklist mirrors the existing F034
  visual-implementation-trace co-location convention (per-subject-area `design/`
  location); the exact filename is a plan-time detail, not invented here.
- This feature is docs/template only (the agent is the runtime, per the F028/F034
  precedent); it adds no runtime executor and no new `retail check` rule.
- The new roadmap F-number, if one is assigned, is a roadmap-ledger edit at plan time;
  the spec does not invent one.
- The audience-scope and pass-bar question (FR-014) is left OPEN for a named human ruling
  and is not defaulted here (Principle V).

## Clarifications

<!-- Principle-V carve-out questions are recorded under their own subsection for a human
     ruling; the workflow is forbidden to answer these. Non-Principle-V ambiguities resolved
     with reasonable constitution-safe defaults (Principle VI) are recorded under the dated
     session subsection. -->

### Session 2026-07-04

Non-Principle-V ambiguities resolved against the constitution, the F034
visual-implementation-trace precedent (same co-location shape, same "additive evidence
item, no new rule" guardrail), and the CT1 contract already shipped. All three (C1, C2,
C3) are reversible docs/plan choices that confirm a shape the spec already implies;
none invents a new mechanism or a new mechanical check.

CLARIFY pass (this session): re-checked the spec body for any bare `[NEEDS
CLARIFICATION]` marker left unannotated -- none found; all three marker occurrences
(Edge Cases LTR-only-page bullet, FR-006, FR-014) already resolve to the two OPEN
owner-ruling items below. One additional non-Principle-V gap was found (where the fixed
colorblind-safe/RTL criteria lists are documented) and resolved as C3. The two OPEN
Principle-V items (Q-FR014-SCOPE, Q-FR014-SEVERITY) were reviewed and are correctly left
OPEN -- they are genuine audience-scope/pass-bar business-policy calls, not defaulted.

- **C1 (which token file the contrast dimension cites -- FR-003\FR-009\FR-015) --
  Default adopted.** Q: FR-003 requires the checklist to cite "the relevant committed
  `*-design-tokens.yaml` file" for a page's contrast dimension, but the spec never states
  HOW the checklist resolves which token file belongs to which page. A: reuse the
  co-location convention the F034 visual-implementation-trace evidence item already
  established -- the token file already associated with that page's design mapping under
  the subject area's `design/` location (the same location Assumptions already names for
  the filled checklist itself). No new lookup mechanism, index, or naming rule is
  introduced; the checklist points at the SAME file the page's existing design mapping
  already points at. Reasoning: FR-009 already requires "a generic per-page path under
  the page's design mapping location" for the checklist itself, so resolving the cited
  token file the same way is the shape the spec already implies, not a new decision;
  inventing a second, independent resolution mechanism would be unnecessary surface
  (Principle VII: stay generic, do not multiply mechanisms). Reversible: easy (a plan-time
  path convention, not a schema or gate change). Touches: FR-003, FR-009, new FR-015.
- **C2 (staleness is a review-discipline obligation, not a mechanical detector --
  FR-008\FR-010) -- Default adopted.** Q: FR-010 requires the checklist to be treated as
  STALE when its cited design-tokens/theme file changes, but FR-008 forbids this feature
  from adding a new `retail check` rule -- so what actually enforces staleness? A:
  staleness is enforced the same way FR-007's "every dimension filled" requirement is
  enforced -- at the EXISTING human design-review sign-off on `dashboard_ready`, not by a
  new automated timestamp/hash/diff detector. There is no new mechanical staleness check;
  a reviewer re-confirming a `dashboard_ready: pass` claim is responsible for noticing the
  cited file changed and re-filling the checklist before relying on it. Reasoning: adding
  an automated staleness detector would require either a new `retail check` rule (forbidden
  by FR-008 / the Collision-Avoidance default) or a new runtime executor (forbidden by the
  Assumptions' "docs/template only" constraint); the review-discipline reading is the only
  one consistent with both constraints already in the spec. Reversible: easy (a
  documentation clarification of an existing requirement, not a new mechanism). Touches:
  FR-008, FR-010.
- **C3 (where the fixed, generic colorblind-safe / RTL-Arabic review-criteria lists are
  documented -- FR-005\FR-006\User Story 3) -- Default adopted.** Q: FR-005 and FR-006
  both require every filled checklist to reference "a fixed, generic set" of review
  criteria "documented once," and User Story 3 requires two different pages' checklists to
  cite "the same fixed review-criteria list" -- but the spec never states WHERE that fixed
  criteria list is documented, only that it must exist and be singular. A: the criteria
  lists live inside the SAME generic template FR-001 already requires (analogous in shape
  to `templates/visual-implementation-trace.md`) -- i.e., the template file itself is both
  the fill-in shape AND the one committed home for the fixed colorblind-safe and
  RTL/Arabic criteria text, so every filled per-page checklist cites/inherits from that one
  template rather than restating or re-deriving criteria per page. No second file, index,
  or registry is introduced. Reasoning: FR-001 already establishes one generic template as
  the checklist's authoring source; splitting the fixed criteria text into a separate
  document would be an unnecessary second mechanism for a single-purpose list (Principle
  VII: stay generic, do not multiply mechanisms), and would risk the two-document set
  drifting out of sync -- exactly the duplicate-surface problem the Collision-Avoidance
  guard exists to prevent, mirrored here at template-authoring scope. Reversible: easy (a
  plan-time authoring detail -- one file's internal structure -- not a schema or gate
  change). Touches: FR-005, FR-006, User Story 3.

### Principle-V carve-out (OPEN -- owner ruling required; the workflow is forbidden to answer)

- **Q-FR014-SCOPE (FR-014a) -- OPEN owner ruling.** Q: Is every dashboard page presumed
  IN-SCOPE for the RTL/Arabic layout dimension by default, requiring a human to explicitly
  mark a specific page LTR-only/English-only before that dimension may be recorded
  not-applicable-with-reason -- or is the reverse true (a page is OUT-OF-SCOPE for RTL
  review by default unless a human explicitly flags it as serving an Arabic-reading
  audience)? This is an audience-scope / business-policy decision the agent MUST NOT settle
  alone (Principle V): the repo ships a bilingual retail-term dictionary and states an
  Arabic retail audience in this feature's own framing, but asserting "every page defaults
  in-scope" on the business's behalf without a named human ruling would still be the agent
  deciding a business-policy question, not observing one already decided. RECORDED PENDING
  DEFAULT the owner may ratify: every page is presumed IN-SCOPE for RTL/Arabic review
  unless a named human explicitly marks that specific page LTR-only/English-only (with a
  recorded reason), matching the feature's own stated Arabic-retail-audience premise and
  erring toward the more conservative (more-reviewed, not less) reading. Until the owner
  rules, no page may be marked not-applicable-with-reason for the RTL dimension on the
  strength of an assumed default alone -- the exemption must cite an explicit human
  LTR-only ruling for that page. Touches: FR-006, FR-007, FR-014, Edge Cases (LTR-only-page
  bullet).
- **Q-FR014-SEVERITY (FR-014b) -- OPEN owner ruling.** Q: When the checklist surfaces an
  open finding in any dimension (a contrast citation showing an open CT1 ERROR, an
  unreviewed/failing colorblind-safe palette, or a genuine RTL/mirroring defect), does that
  finding make `dashboard_ready` `blocked`, or does it only downgrade the stage to
  `warning` -- the way a contrast NOTE is treated as a `warning`-class design note in
  `dashboard-qa.md` / `screenshot-review.md` today? This is a business-policy pass-bar
  decision the agent MUST NOT settle alone (Principle V): the existing contrast-as-warning
  precedent is itself the practice this feature exists to tighten (per the Overview -- a11y
  is "only ever a `warning`-class design NOTE" today, which the feature reframes as
  required evidence), so silently carrying the `warning`-only precedent forward would
  undercut the feature's own stated purpose without a named human choosing that outcome;
  conversely, silently defaulting to `blocked` would unilaterally raise the stage's pass-bar
  strictness on the business's behalf. Until the owner rules, an open finding in any
  dimension MUST be recorded as at minimum a `warning`-class finding cited in
  `blocking_reasons[]` or an equivalent warning-evidence entry (never silently dropped);
  whether it escalates to `blocked` for that page's `dashboard_ready` status is UNDECIDED
  pending this ruling. Touches: FR-007, FR-011, FR-014, Edge Cases (RTL-mirroring-defect
  bullet).
