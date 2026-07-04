# Phase 1 Data Model: Dashboard Accessibility + RTL/Arabic Readiness Checklist

This feature introduces no code and no persisted database entity. The "data
model" here is the shape of the committed Markdown/YAML-in-Markdown
artifacts an agent or human authors and reads. All shapes are GENERIC
(Principle VII): placeholders only in every template; real values appear
only in the one worked instance under `mappings/retail_store_sales/design/`.

## Entity: A11y/RTL Readiness Checklist (the per-page evidence artifact)

The checklist this feature defines. One committed Markdown file per
dashboard page, filled by an analyst/agent against already-committed
design/theme artifacts. Lives at
`mappings/<subject>/design/a11y-rtl-readiness-checklist.md` (or, for a
report with multiple pages, one section per page within that file -- a
plan-time authoring detail, not a schema constraint).

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `subject_area` | string | yes | `<schema.table or model name>` -- matches the sibling design artifacts' header convention (`dashboard-layout.md`, `visual-contract-binding-map.md`). |
| `page_id` | string | yes | Which report page this checklist covers (matches the built/approved page identity used by the visual-implementation-trace, if one exists). |
| `filled_by` | string | yes | `<analyst_or_agent>` -- who filled this checklist. |
| `filled_at` | date | yes | `<YYYY-MM-DD>`. |
| `dimensions` | object (3 required sub-entities) | yes | See "Dimension" shapes below. Exactly three: `contrast`, `colorblind_safe`, `rtl_arabic_layout`. |
| `overall_status` | enum | yes | One of `not_started` / `blocked` / `warning` / `pass` -- rolled up to the WORST dimension status, matching the `visual-implementation-trace.md` roll-up rule. NEVER a number. |
| `evidence` | list[string] | yes when `overall_status` is not `not_started` | Repo-relative paths / citations backing the recorded dimension dispositions. |
| `blocking_reasons` | list[string] | required when any dimension (or the overall status) is `blocked` | Concrete reasons, naming the missing/unfilled/failing dimension. |

No `score`, `confidence`, `health`, `maturity`, or `completeness_count`
field exists anywhere in this shape (hard rule #9, FR-012).

### Dimension shape (shared shape across all three dimensions)

Each of the three dimensions uses the same base shape; the DISPOSITION enum
and the citation contents differ per dimension (detailed below).

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `disposition` | enum | yes | `reviewed-clean` \| `not-applicable-with-reason` \| `blocked`. NEVER left blank/omitted (FR-007) -- a genuinely inapplicable dimension is `not-applicable-with-reason`, never silently skipped. |
| `reason` | string | required when `disposition` is `not-applicable-with-reason` or `blocked` | Free-text citing the concrete fact (e.g. "no multi-series palette declared on this page" or "CT1 reports an open ERROR for this token file"). |
| `citation` | list[string] | yes | Repo-relative path(s) this dimension's disposition traces to (SC-006: no unsourced claim). |
| `stale` | boolean (implicit, review-discipline only) | n/a | Not a stored field -- staleness is a REVIEW-DISCIPLINE obligation checked at the next design-review sign-off (Clarifications C2), not a mechanical flag this schema persists. |

### Dimension: `contrast` (FR-003, FR-004, US2)

| Field | Value shape | Notes |
|-------|-------------|-------|
| `token_file` | repo-relative path | `<*-design-tokens.yaml file already associated with this page's design mapping, per Clarifications C1>`. Resolved via the SAME co-location convention `visual-implementation-trace.md` uses -- no new lookup mechanism. |
| `ct1_result` | one of: `clean` \| `open-error: <finding text>` \| `parse-failure: <finding text>` \| `file-not-found` | The CURRENT `retail check` CT1 (`design_contrast.py`) finding for `token_file`. This field is a CITATION of CT1's registered output, never an independently computed ratio. |
| `disposition` | derived from `ct1_result` | `ct1_result: clean` -> `disposition: reviewed-clean`. `ct1_result: open-error / parse-failure / file-not-found` -> `disposition: blocked` (the checklist's contrast dimension MUST NOT be marked reviewed-clean while CT1 reports an open finding -- FR-004). `not-applicable-with-reason` is NOT a valid disposition for this dimension (every page has SOME background/text pairing; contrast always applies). |

**Invariant (US2/SC-002)**: `disposition: reviewed-clean` for the contrast
dimension implies `ct1_result: clean` -- these two fields MUST NEVER
disagree. A filled checklist asserting `reviewed-clean` while CT1 reports an
open ERROR for the same token file is a defect.

### Dimension: `colorblind_safe` (FR-005)

| Field | Value shape | Notes |
|-------|-------------|-------|
| `palette_source` | repo-relative path | The committed theme/palette file whose `dataColors` (or category palette) this dimension reviews (e.g. `themes/<name>.theme.json`). |
| `criteria_ref` | fixed pointer | `docs/powerbi/visual-design-system.md#colorblind-safe-palette-separation` (or the exact heading the Phase-1 authoring step lands on) -- the ONE generic criteria list every filled checklist cites; never restated inline. |
| `disposition` | enum | `reviewed-clean` (the declared palette was reviewed against the cited criteria and separates cleanly), `not-applicable-with-reason` (no multi-series `dataColors`/category palette declared on this page -- Edge Cases), or `blocked` (the review found a genuine separation defect). |
| `finding_detail` | string, required if `disposition` is `blocked` | Names the specific colors/series that fail separation and proposes the accessible alternative (FR-011) -- never silently overridden or silently complied with. |

This is a documented HUMAN/agent-read judgment against fixed criteria, NOT
a numeric CVD-simulation score (Assumptions; a future deterministic
simulation rule, if separately specified, is a different feature).

### Dimension: `rtl_arabic_layout` (FR-006, FR-014)

| Field | Value shape | Notes |
|-------|-------------|-------|
| `layout_source` | repo-relative path | The page blueprint/layout artifact reviewed (e.g. `mappings/<subject>/design/dashboard-layout.md`). |
| `criteria_ref` | fixed pointer | `docs/powerbi/visual-design-system.md#rtl-arabic-layout-readiness` -- the ONE generic criteria list (text direction, mirrored visual/axis alignment where direction carries meaning, Arabic numeral/date formatting expectations) every filled checklist cites. |
| `disposition` | enum | `reviewed-clean`, `not-applicable-with-reason`, or `blocked`. |
| `scope_ruling_citation` | string, REQUIRED when `disposition` is `not-applicable-with-reason` | Per Q-FR014-SCOPE (OPEN): until the owner rules, this field MUST cite an EXPLICIT named-human LTR-only ruling FOR THIS SPECIFIC PAGE. An assumed default alone (e.g. "presumably English-only") is NOT a valid citation -- the checklist MUST record the dimension as at least reviewed pending, never mark it not-applicable on the strength of an assumed default. |
| `finding_detail` | string, required if `disposition` is `blocked` | Names the specific mirroring/direction/formatting defect and proposes the RTL-correct alternative (FR-011). |

## Entity: Fixed Review Criteria (documented once; not a per-page artifact)

Lives as a prose extension of `docs/powerbi/visual-design-system.md`
(alongside the existing "Accessible contrast" paragraph). NOT a YAML
structure -- prose sections, generic, referenced by pointer from every
filled checklist's `criteria_ref` field. Two subsections:

- **Colorblind-safe palette separation criteria**: what "colorblind-safe"
  means for a Power BI category/data-color palette on this kit's pages
  (e.g. do not rely on hue alone to distinguish adjacent series; pair color
  with a second encoding -- pattern, label, position -- for
  distinctions that matter; avoid red/green as the ONLY distinguishing pair
  for a pass/fail or good/bad encoding). Generic -- no C086 color literal.
- **RTL/Arabic layout readiness criteria**: text direction (does the page
  respect right-to-left reading order where the report locale is Arabic);
  mirrored visual/axis alignment (does a trend's implied left-to-right time
  direction get mirrored for RTL readers, where direction carries meaning);
  Arabic numeral/date formatting expectations (does the page's number/date
  formatting match the audience's locale expectations). Generic -- no
  literal Arabic string (FR-013); a real Arabic example, if any, lives only
  in a filled per-page instance.

This entity has NO status/evidence/blocking-reasons shape of its own -- it
is reference prose, not a readiness record.

## Entity: Dashboard Ready evidence-item extension (stage-doc edit)

Not a new entity -- an additive extension of the EXISTING
`docs/readiness/dashboard-ready.md` shape (same file F034 already extended
once). Adds one new subsection ("Evidence item: a11y/RTL readiness
checklist") stating:

- the checklist is a REQUIRED `evidence[]` item before `dashboard_ready` may
  record `pass`, for every page (FR-007);
- an absent, missing, or partially-unfilled checklist (any dimension not
  `reviewed-clean` / `not-applicable-with-reason` / `blocked` --
  i.e. still carrying a `<placeholder>`) is a recorded
  `blocking_reasons[]` entry;
- the interim severity floor from Q-FR014-SEVERITY (OPEN): an open finding
  in any dimension is recorded as AT LEAST a `warning`-class finding cited
  in `blocking_reasons[]` or an equivalent warning-evidence entry; whether
  it escalates that page's `dashboard_ready` all the way to `blocked` is
  UNDECIDED pending the named-human ruling;
- no change to the gate, owner, required-checks table, or the meaning of
  the four statuses themselves.

## State transitions (per dimension, and rolled up)

```text
not_started -> blocked                 (dimension left with a <placeholder>, or CT1 open-error/parse-failure/file-not-found)
not_started -> not-applicable-with-reason   (genuinely inapplicable, with a citation)
not_started -> reviewed-clean          (reviewed against fixed criteria / CT1 clean; no open finding)
blocked -> reviewed-clean              (blocker resolved -- CT1 finding fixed, or the flagged defect corrected)
reviewed-clean -> blocked              (STALE: the cited token/theme/layout file changed after filling --
                                         re-fill required before the next dashboard_ready: pass claim relies
                                         on it; enforced at the design-review sign-off, Clarifications C2,
                                         not by an automated detector)
```

Overall checklist `overall_status` is the WORST of the three dimension
dispositions, mapped onto the four readiness statuses (mirroring
`visual-implementation-trace.md`'s roll-up rule): any dimension `blocked` ->
overall `blocked` (or `warning`, pending Q-FR014-SEVERITY); all dimensions
`reviewed-clean` or `not-applicable-with-reason` (with a valid citation) ->
overall contributes toward `pass` for the checklist evidence item (the
checklist itself never grants `dashboard_ready: pass` -- that stays the
BI/report owner's recorded action, per the F034 precedent).

## Invariants (cross-cutting)

- No numeric confidence/health/maturity score or completeness count exists
  anywhere in this data model (hard rule #9, FR-012, SC-003).
- Every `citation` / `token_file` / `palette_source` / `layout_source`
  value in a FILLED instance is a real, confirmed repo-relative path
  (SC-006) -- never a placeholder left over from the generic template.
- The generic template and the criteria-doc extension contain NO
  C086/pharmacy domain noun, color literal, or grain key, and NO literal
  Arabic string (SC-004, FR-009, FR-013).
- The `contrast.disposition` field is a pure function of `ct1_result` --
  it is never set independently of CT1's registered finding (US2, SC-002).
- `rtl_arabic_layout.disposition: not-applicable-with-reason` is INVALID
  unless `scope_ruling_citation` names an explicit human ruling for that
  specific page (Q-FR014-SCOPE interim floor) -- this invariant holds until
  the owner rules otherwise.
- Filling this checklist NEVER itself sets `dashboard_ready: pass` -- it
  produces evidence FOR that existing, separately-recorded sign-off.
