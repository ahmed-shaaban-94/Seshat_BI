# Implementation Plan: Promotion/Markdown Fact and Factless-Fact Coverage Pattern

**Branch**: `097-promotion-markdown-factless` | **Date**: 2026-07-04 | **Spec**: `specs/097-promotion-markdown-factless/spec.md`

**Input**: Feature specification from `specs/097-promotion-markdown-factless/spec.md`

**Note**: This plan is docs-only, per the spec's own SCOPE GUARD. It plans a
**pattern document plus a copy-me template** (both authored at implement
stage, not this stage) -- not a runtime feature, not a static rule, not a
database build. There is no code to design.

## Summary

The primary requirement (spec Overview, FR-001 through FR-006) is a single new
pattern document under `docs/patterns/` that teaches two Kimball fact shapes
the kit's vocabulary is currently missing -- a measure-bearing
promotion/markdown fact, and a factless coverage fact with no required
additive measure -- plus a single new copy-me template under `templates/`
that shows how to fill the existing `gold_star` shape for the no-measure
case. The technical approach (research.md) is: cite and compose already-
shipped artifacts (`templates/source-map.yaml`'s `gold_star` convention, the
discounts-and-promotions domain doc's named gap, RC14's Kimball-star
discipline, spec 087's pending cross-star conformance mechanism) -- add no
new template field, no new rule, no new readiness stage, no live surface. The
one load-bearing idea this feature contributes is the factless-fact concept
itself: a fact table that is still a valid Kimball star (fact + conformed
dimensions, Principle III) despite carrying no additive measure, whose sole
purpose is to make a LEFT ANTI JOIN against an existing sales fact possible --
answering "what was on promotion but did not sell," a question structurally
unanswerable by any measure-bearing fact alone (no row exists for a zero-unit
promotion).

## Technical Context

**Language/Version**: N/A -- documentation only (no code produced or
modified). The one artifact with syntax to validate is the factless-fact
template's YAML body (must parse as valid YAML, per `templates/source-map.yaml`'s
own "keep this YAML valid" authoring note) and one illustrative SQL sketch in
the pattern doc (non-executable, placeholder-only, not run or linted as a
migration).

**Primary Dependencies**: None new. Cites existing repo artifacts only:
`templates/source-map.yaml` (the `gold_star` shape and authoring-notes
convention the new template mirrors), `skills/retail-kpi-knowledge/domains/
discounts-and-promotions.md` (the named gap), `docs/worked-examples/
retail-store-sales.md` (cited once as an external "see" pointer),
`docs/decisions/0002-retail-cleaning-defaults.md` (RC14), `specs/087-
conformed-dimension-readiness/spec.md` (cited as the pending, not-yet-
ratified cross-star conformance mechanism), `.specify/memory/constitution.md`.

**Storage**: N/A. No database, no migration, no live connection is produced
or assumed by this feature. A *future* table that adopts this pattern would
use the existing DigitalOcean Postgres medallion, unchanged and out of scope
here.

**Testing**: N/A for this feature's own deliverable (it is prose + one YAML
template + one illustrative SQL sketch). The validation of this spec chain is
inspection against the spec's own Success Criteria (SC-001 through SC-006 --
each is a grep/read check, never a numeric score) plus a read-only
`retail check` run at implement-stage completion, reported with its exact
exit code (no mutation, no live DB, no rule added for it to newly catch).

**Target Platform**: N/A -- Markdown (pattern doc) and YAML (template),
consumed by a future human analyst or agent onboarding a promotion/markdown
or factless-coverage table through the unchanged source-mapping gate.

**Project Type**: Documentation / reusable-pattern-definition (Spec-Kit
"docs-first" slice, matching the precedent of spec 095's same-day
KPI-domain-gap pattern feature and spec 084's worked-example-factory: a
cross-cutting kit-vocabulary addition, not a per-table stage advance).

**Performance Goals**: N/A.

**Constraints**: Must not invent promotion mechanics (discount-type taxonomy,
funding source, promo hierarchy) beyond generic placeholders (FR-008). Must
not pick a grain, PK, or column set for any real table (FR-009). Must not
alter the Discount Amount / Discount Rate % contracts or the Promotion
Uplift % Planned marker (FR-010, SC-006). Must not add, modify, or reserve
any `retail check` rule id, touch `src/retail/rules/__init__.py`,
`EXPECTED_RULE_IDS`, the glossary rules table, `docs/rules/rules-manifest.json`,
or the severity-posture record, and must not add a readiness stage or a
`readiness-status.yaml` key (FR-007, SC-004). Must not connect to a database,
execute or propose migration SQL, or invoke F016 (FR-011). Must stay generic
-- zero real worked-example/table-specific names inlined into the pattern's
own illustrations (FR-012, SC-003). Must emit zero numeric confidence/health/
maturity score or completeness count (FR-014, SC-005, hard rule #9). Must
stay ASCII, UTF-8 without BOM, short repo-relative paths (FR-015).

**Scale/Scope**: One feature's worth of Spec-Kit documentation (spec, plan,
research, data-model, quickstart inside `specs/097-promotion-markdown-
factless/`) at THIS stage. The pattern doc (`docs/patterns/promotion-markdown-
factless.md`) and the template (`templates/factless-fact.yaml`) are the
feature's DELIVERABLES, authored at implement stage -- this plan stage does
not create them.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Check | Result |
|-----------|-------|--------|
| I. Agent-First, Gate-Enforced | Does this feature add, weaken, or bypass a gate? | No new gate; no gate weakened. The feature adds no `retail check` rule (FR-007) -- compliance is demonstrable by running `retail check` over the two new committed files (the pattern doc and the template) and observing exit 0, exactly as any other committed text is checked; no new rule exists for it to newly satisfy or evade. PASS. |
| II. Depend, Never Fork | Does this feature touch the Power BI execution adapter? | No. F016 is not referenced beyond the explicit deferral in FR-011 ("MUST NOT ... invoke any deferred execution adapter (F016)"). PASS. |
| III. Medallion, Postgres-First, Gold-Only | Does this feature respect gold-is-a-Kimball-star (fact + conformed dimensions)? | Yes, and this is the feature's central design resolution: a factless coverage fact is STILL a valid Kimball star -- it keeps the fact-plus-conformed-dimensions shape RC14 requires; what it lacks is an additive MEASURE, not a dimension or the conformed-key discipline (FR-004). The promotion/markdown fact shape is an ordinary measure-bearing fact reusing the same conformed product/store/date dimensions (FR-005, FR-006). Power BI's gold-only read is unaffected -- no real gold table is created. PASS. |
| IV. Source Mapping Before Silver | Does this feature let silver be written before mapping, or bypass the gate? | No -- no silver SQL is authored anywhere in this feature (FR-011), and the pattern doc explicitly states that an adopting table's promotion/markdown fact and factless coverage fact each go through the EXISTING, UNCHANGED source-mapping gate exactly like any other new table (spec.md Assumptions). PASS. |
| V. Agent Stops at Judgment Calls | Does this feature let the agent decide grain, PII, promo mechanics, or a baseline rule, or self-grant an approval? | No -- every such call (grain, PK, promo mechanics, PII, the Promotion Uplift % baseline rule, the dimension-mismatch edge case) is explicitly named in the pattern doc as an adopting-table/owner decision routed through the unchanged source-mapping gate, never resolved here (FR-008, FR-009, Edge Cases). No approval of any kind is recorded by this feature. PASS. |
| VI. Defaults Then Deviations | Does this feature bypass or restate the RC-defaults discipline? | No -- reinforced: the factless-fact template mirrors `source-map.yaml`'s existing `defaults.adopted[]` / `defaults.deviations[]` shape verbatim; an adopting table still records only its deviations with a triggering data fact, exactly as today. PASS. |
| VII. C086 Is An Example, Not The Schema | Does this feature inline a real worked-example's or table's specific names into its own illustrations? | No -- the pattern doc's and template's illustrations use ONLY generic placeholders (`sales_fact`, `coverage_fact`, `dim_product`, `dim_store`, `dim_date`, `promotion_id`); `retail_store_sales` / `fct_sales_rss` appear only as an external "see" citation, never restated with invented data (FR-012, SC-003, research.md Sec 5). PASS. |
| VIII. Static-First Governance, Live Deferred | Does this feature claim a live-validation result, or blur static vs. live? | No live surface exists in this feature at all -- not "deferred and marked PENDING," but genuinely absent: no SQL, no `retail validate` run, no live profiling (research.md Sec 4). The one SQL sketch in the pattern doc is explicitly labeled a non-executable illustration of the anti-join technique, never a proposed or runnable migration (Clarification Q3). PASS. |
| IX. Secrets and Reproducibility | Does this feature commit a secret, a real connection string, or a non-ASCII/BOM file? | No -- none referenced. Both new files (authored at implement stage) will be ASCII, UTF-8 without BOM, using `--` and `->` (no em-dashes/curly quotes), at the short fixed paths FR-016 resolved (`docs/patterns/promotion-markdown-factless.md`, `templates/factless-fact.yaml`), both well within the Windows 260-char budget. PASS. |
| Hard rule #9 (no fabricated score) | Does this feature emit a numeric confidence/health/maturity score or completeness count anywhere? | No -- SC-005 requires zero such numbers in any artifact this feature produces; none appear in this plan, research, data-model, or quickstart, and none will appear in the pattern doc or template. PASS. |
| Readiness System (spine) | Which readiness stage does this feature advance? | **None directly.** This is a cross-cutting kit-vocabulary addition ("Serves: Stages 2-6, new fact pattern" per the feature's own framing) orthogonal to the seven-stage per-table spine -- precedented by spec 084 (worked-example-factory) and spec 095 (actuals-vs-target pattern), both of which recorded the same "no stage advanced for any real table" posture for a reusable-pattern feature. A FUTURE table that adopts this pattern would advance its OWN Mapping-Ready-through-Gold-Ready stages via the unchanged gate; this feature supplies the pattern that adoption would use, not the adoption itself. |

**Overall**: PASS. No violation requires a Complexity Tracking entry.

## Project Structure

### Documentation (this feature)

```text
specs/097-promotion-markdown-factless/
|-- spec.md              # Feature spec (done, clarified)
|-- plan.md              # This file (Phase 0/1 output)
|-- research.md          # Phase 0 output (done)
|-- data-model.md        # Phase 1 output (done)
|-- quickstart.md        # Phase 1 output (done)
`-- tasks.md              # Phase 2 output (/speckit-tasks -- NOT created by /speckit-plan)
```

### Source code / repo artifacts (repository root)

**Structure Decision**: This feature adds exactly TWO new files to the repo,
both authored at IMPLEMENT stage (not this plan stage), at the exact paths
FR-016 resolved:

```text
docs/
`-- patterns/                                       # NEW subdirectory (docs/<topic>/ convention)
    `-- promotion-markdown-factless.md              # NEW -- the pattern doc (FR-001)

templates/
`-- factless-fact.yaml                              # NEW -- flat under templates/ (FR-002)
```

No other file is created or modified. Explicitly UNCHANGED / NOT TOUCHED by
this feature (the collision-avoidance allocation and FR-007/FR-010):

- `templates/source-map.yaml` -- read and cited for its `gold_star` shape and
  authoring-notes convention; not edited (FR-002).
- `skills/retail-kpi-knowledge/domains/discounts-and-promotions.md` -- read
  and cited; byte-identical before/after (FR-010, SC-006).
- `docs/worked-examples/retail-store-sales.md` -- cited once as an external
  "see" pointer; not edited (FR-012).
- `src/retail/rules/__init__.py`, `EXPECTED_RULE_IDS`, the glossary rules
  table, `docs/rules/rules-manifest.json`, `docs/rules/severity-posture.json`
  -- no rule id added, modified, or reserved (FR-007, SC-004).
- Any `mappings/<table>/readiness-status.yaml` -- no new key, no new stage
  (FR-007).
- `specs/087-conformed-dimension-readiness/spec.md` -- cited as the pending
  mechanism; not implemented, not depended on landing first (FR-006).
- Any `src/`, `warehouse/`, `powerbi/`, or `mappings/` path -- no code, no
  migration, no semantic model, no per-table mapping artifact (FR-011 and
  spec.md Assumptions).

There is no `src/`, `backend/`, `frontend/`, or `tests/` change of any kind.
The only future consumer of this feature's two deliverables is a SEPARATE,
later effort that would onboard a real promotion/markdown or factless-
coverage table through the existing `source-mapping` -> `retail-build-
warehouse` -> `retail-validate` sequence -- that effort is out of scope here
and touches none of the paths this feature creates or edits, beyond reading
them as a copy-me starting point.

## Complexity Tracking

*No entries.* The Constitution Check above found no violation requiring
justification -- this feature adds zero new templates fields, zero new rules,
zero new readiness stages, and zero new runtime surfaces; it adds exactly one
new pattern doc and one new copy-me template, both additive and both
mirroring an existing convention (`templates/source-map.yaml`'s `gold_star`
shape) rather than inventing a new one.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | -- | -- |
