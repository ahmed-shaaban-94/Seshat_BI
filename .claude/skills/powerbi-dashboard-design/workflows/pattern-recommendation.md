# pattern-recommendation

Surface 1 (report visuals). Spec 123, User Story 3 (FR-012/FR-013/FR-014). This
workflow turns a committed, approved **Report Intent**
(`templates/report-intent.yaml` / `mappings/<subject-area>/design/report-intent.yaml`)
into a proposal of ZERO OR MORE candidate **Dashboard Patterns**
(`docs/patterns/dashboard/*.md`) -- generic design GUIDANCE, never a named KPI,
never tenant-specific business logic, and never something auto-applied. The
human always chooses; this workflow only narrows the menu.

The router (`../SKILL.md`) opens this workflow for "Recommend a dashboard
pattern for an approved intent." Run it AFTER a Report Intent is approved and
BEFORE (or alongside) `page-blueprint.md` -- a recommended pattern informs the
blueprint's section/visual choices, but never replaces the blueprint itself
(the pattern is guidance; the blueprint is the committed page design).

## The one load-bearing rule

**A pattern is design guidance, not a design.** It never defines a KPI, never
supplies a formula/DAX, never invents a metric, and never fabricates a
dimension the subject area lacks. This workflow's whole job is: read intent ->
propose candidate pattern(s) -> let the human pick/adapt/reject -> for any
requirement a chosen pattern needs but the subject area lacks, hand off to
`retail dashboard-gaps` (never invent it here).

## Step 1 -- Read the approved Report Intent

Read the committed `report-intent.yaml`'s `purpose` field (one of:
`executive | monitoring | diagnostic | action_oriented | analytical_exploration`),
its `business_questions`, and its `outcome_metrics` / `driver_metrics` /
`guardrail_metrics` role lists (names only). Do not proceed against an
unapproved or `not_started`/`blocked` intent -- a pattern recommendation on an
unresolved intent has nothing stable to match against; STOP and route back to
the `report-intent-interview` skill instead.

## Step 2 -- Map `purpose` -> candidate pattern(s)

Use this table to shortlist candidates. It is a many-to-many map: one `purpose`
commonly matches more than one family, and a family may fit more than one
`purpose`. **Never auto-pick when more than one candidate matches** (FR-014) --
always present every match for human choice.

| Report Intent `purpose` | Candidate pattern(s) (`docs/patterns/dashboard/`) |
|---|---|
| `executive` | `executive-performance.md` |
| `monitoring` | `branch-performance.md`, `inventory-health.md`, `returns-and-refunds.md`, `data-quality-control-room.md` |
| `diagnostic` | `sales-diagnosis.md`, `promotion-effectiveness.md`, `branch-performance.md` (when combined with a per-location "why"), `product-performance.md` (when combined with a mix-shift "why") |
| `action_oriented` | `action-and-exceptions.md`, `inventory-health.md` (when the intent is action-first, not just observational) |
| `analytical_exploration` | `product-performance.md`, `customer-behavior.md`, `promotion-effectiveness.md` (when the intent leans exploratory rather than diagnostic) |

Every one of the ten families is reachable from at least one `purpose` row
above; none is orphaned. Use the intent's `business_questions` text and its
metric-role names (not their definitions) to break ties between candidates
that share a `purpose` row -- e.g. a `monitoring` intent whose questions
mention stock/coverage points at `inventory-health.md`, not
`branch-performance.md`.

## Step 3 -- Score fit as strong or partial, never a number

For each candidate, compare the pattern's `common_question_families` and
`metric_roles` against the intent's `business_questions` and declared metric
roles:

- **Strong fit**: the intent's questions and metric roles align closely with
  the pattern's question families and roles, and the intent supplies (or the
  subject area can supply, per Step 4) every role the pattern assumes.
- **Partial fit**: the pattern matches the `purpose` and most question
  families, but some assumed role, dimension, or structural element is
  missing, ambiguous, or only loosely implied by the intent.

**Never emit a numeric score, percentage, or ranking** (FR-035) -- "strong" and
"partial" are the only two categorical labels this workflow uses, and both are
presented, never silently filtered to just the top one.

## Step 4 -- Surface unavailable requirements as gaps, never fabricate

For any pattern requirement a chosen (or candidate) pattern assumes -- a metric
role, a dimension, a hierarchy level, a reason-code field, a baseline period --
that the subject area does not have committed and approved:

- **Do NOT invent it.** This workflow authors no metric, no dimension, no
  fabricated baseline.
- **Route it through the shipped `retail dashboard-gaps`** (spec 117,
  `src/seshat/gap_detector.py` / `src/seshat/cli/commands/gap_detector.py`).
  Build the gap-detector's page-intent input from the pattern's assumed
  metric/dimension requirements plus the Report Intent's committed
  business questions, then run `retail dashboard-gaps` against the target
  subject area and cite its categorical verdict (`Covered` /
  `Blocked -- missing definition` / `Blocked -- missing field` / `Planned` /
  `Out of scope`) in the recommendation. This workflow does NOT recompute
  gap detection itself -- it reuses the shipped tool's output (mirrors
  FR-020's reuse discipline for the semantic audit).
- **Record the misfitting requirement as a partial-fit flag** (Step 3) so the
  human sees exactly which part of the pattern needs adaptation, not just
  that "some gap exists."

## Step 5 -- Present candidates for human choice; STOP

Present every candidate from Step 2 (not just the best-fitting one), each
labeled strong or partial fit, each with its misfitting parts named (Step 4).
Ask the human to:

- **Accept** a candidate as-is (informs the subsequent `page-blueprint.md`
  run), or
- **Adapt** a candidate (the human names which page structure / visual roles
  to keep, drop, or combine across candidates), or
- **Reject** all candidates (proceed to `page-blueprint.md` with no pattern
  guidance -- the blueprint is still fully authorable without one; a pattern
  is guidance, never a requirement).

**Never silently pick one candidate when more than one fits** (FR-014). This
workflow's output is a recommendation with a human decision pending, never a
committed artifact -- there is no `readiness:` block here to set to `pass`;
the *pattern* itself carries no readiness state (only the blueprint that
adopts it does).

## Common failure modes (mirrors `docs/patterns/dashboard/*.md` risks)

- Recommending a pattern whose question families do not match the intent's
  actual `business_questions` text -- re-check Step 2/3 rather than defaulting
  to the most common family.
- Treating a "partial fit" flag as something this workflow resolves on its own
  by inventing the missing piece -- it never does; Step 4 is the only
  permitted response to a missing requirement.
- Naming a concrete KPI, a DAX expression, or a tenant-specific metric
  anywhere in a recommendation -- patterns and this workflow stay at the ROLE
  level (outcome/driver/guardrail), never a named metric (FR-013).

## See also

- The ten pattern docs: `../../../../docs/patterns/dashboard/*.md` (note the
  distinct, non-colliding location from the data-modeling `docs/patterns/*.md`
  docs).
- The Report Intent this workflow reads:
  `../../../../templates/report-intent.yaml`; the interview that produces one:
  `../../../report-intent-interview/SKILL.md`.
- The gap-surfacing tool this workflow reuses (never recomputes):
  `retail dashboard-gaps` / `../../../../src/seshat/gap_detector.py`.
- Where a chosen/adapted pattern feeds next: `page-blueprint.md` (the
  committed page design), `visual-design-system.md` (chart-by-question/grain
  selection).
- The router + the four-surface table: `../SKILL.md`.
