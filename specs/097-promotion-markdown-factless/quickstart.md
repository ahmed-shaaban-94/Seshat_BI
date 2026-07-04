# Quickstart: Promotion/Markdown Fact and Factless-Fact Coverage Pattern

**Feature**: `specs/097-promotion-markdown-factless/` | **Phase**: 1 (design)

This walks through how an agent or analyst EXERCISES this feature once built
(the pattern doc at `docs/patterns/promotion-markdown-factless.md` and the
template at `templates/factless-fact.yaml`, both authored at implement
stage). It does not build, migrate, or validate anything live -- every step
below either reads a committed doc/template or hands off to the existing,
unchanged source-mapping gate.

## Scenario A -- "What did we discount that did not sell?" (US1, P1)

An analyst is asked this exact business question.

1. **Read the pattern doc.** Open `docs/patterns/promotion-markdown-
   factless.md` and find the section explaining why a measure-bearing
   promotion fact alone cannot answer this -- no row exists for a promotion
   that sold zero units.
2. **Identify the coverage unit.** The doc names the factless coverage fact's
   grain: one row per (product, store, day, promotion) COMBINATION that was
   true regardless of a sale. The analyst restates this in their own words
   (this is the pattern doc's own Independent Test, spec.md US1).
3. **Read the anti-join illustration.** The doc's placeholder-only SQL sketch
   (data-model.md Entity 3) shows the technique: a LEFT JOIN from the
   coverage fact to the sales fact on shared conformed keys, filtered to
   `WHERE sales_fact.<key> IS NULL`. The analyst confirms this is a
   description of the technique, not a runnable migration against any real
   table.
4. **Check for a shared conformed key.** Before applying this to a REAL
   table, the analyst confirms their promotion-coverage source and their
   sales source share a conformed, grain-compatible key (e.g. both have a
   product key at the same grain). If they do NOT share one, this is a
   blocking mapping-gate question (Principle V) -- the analyst raises it in
   that table's own `unresolved-questions.md`, exactly as any other grain
   ambiguity. This feature does not resolve it or invent a crosswalk.
5. **STOP here if no real table exists yet.** The pattern doc and template
   are sufficient to answer the business question in the abstract (SC-001).
   Building a real coverage fact is a SEPARATE, later effort (see Scenario C).

## Scenario B -- Model a real promotion/markdown fact (US2, P2)

An analyst has a real promotion or markdown source (line items or events
tagged with a promotion identifier and a discount/markdown amount).

1. **Read the promotion/markdown fact section** of the pattern doc
   (data-model.md Entity 1). Note the candidate grain example (e.g. "one row
   per promotion line per day per store") is a PLACEHOLDER, not a value this
   feature supplies -- the real grain is decided at that table's own
   Mapping Ready gate (Principle IV/V).
2. **Identify the additive measure(s)** the doc illustrates (a
   markdown-amount-shaped measure, a promoted-units-shaped measure) as
   candidates; the analyst's real source determines which actually exist.
3. **Identify the conformed dimensions to REUSE.** The doc names product,
   store/location, and date as the dimensions expected to be the SAME
   instance an existing sales star already carries -- not a new copy. The
   doc cites spec 087 (cross-star conformed-dimension readiness, reserved
   rule id HR1, currently Draft/not yet ratified) as the FUTURE mechanism
   that would verify this conformance; nothing in this feature enforces it
   today.
4. **Hand off to the existing source-mapping gate.** From here, the analyst
   follows the SAME, UNCHANGED flow any new table follows: `retail-onboard-
   table` -> `source-mapping` (profile, fill the five mapping artifacts
   under `mappings/<table>/`, clear the gate) -> `retail-build-warehouse`
   (author silver/gold SQL, stop before executing) -> `retail-validate`
   (live checks, when a DSN is available). This feature changes none of
   those steps' mechanics.

## Scenario C -- Adopt the factless-fact template for a real coverage table

Once a table's promotion-coverage source is ready to be mapped (via the
SAME source-mapping gate as any other table):

1. **Copy `templates/factless-fact.yaml`** into that table's own working
   area, the same way `templates/source-map.yaml` is copied for a
   measure-bearing table today.
2. **Fill `meta:`** (grain, primary key, reviewed_by/on) with the REAL
   table's values -- this is that table's own Mapping Ready decision, not a
   value this feature pre-supplies.
3. **Fill `columns:`** for every real source column (keep/drop/derive), per
   the existing Phase 2.1-2.5 discipline. If a genuine money/quantity column
   turns up here, STOP and reconsider: that may mean the real shape needed is
   the measure-bearing promotion/markdown fact (Scenario B / Entity 1), not a
   factless coverage fact.
4. **Leave `gold_star.fact.measures` as `[]`.** This is the one field the
   factless-fact template fixes structurally; do not add a fabricated
   `coverage_count` column here (per the pattern doc's Edge Cases guidance --
   a `COUNT(*)` at query time is the valid substitute, never a stored
   measure).
5. **Fill `gold_star.dimensions`** with the SAME conformed dimension names
   (`dim_product`, `dim_store`, `dim_date`, or that table's real equivalents)
   an existing sales star already uses -- never mint a parallel copy.
6. **Take the filled template through the existing mapping-gate review**
   exactly like `source-map.yaml` -- a named human reviews and approves it
   before any `silver.*` SQL is written (Principle IV, unchanged).

## Scenario D -- Verify the feature stayed generic (US3, P3)

Anyone reviewing this feature's own deliverables (the pattern doc and the
template) rather than a future adopter's filled instance:

1. **Grep the pattern doc and template for real names.** Search for
   `retail_store_sales`, `fct_sales_rss`, `C086`, `pharmacy`, or any other
   worked-example-specific noun. Confirm every hit is a citation ("see ...")
   never inlined content (SC-003).
2. **Confirm the template's shape matches `source-map.yaml`'s convention.**
   Same top-level sections, same placeholder style (angle-bracket
   `<placeholder>` names), same authoring-notes header pattern -- without
   copying `source-map.yaml`'s own specific example values.
3. **Confirm `retail check` still exits 0.** Run the existing static
   governance checker over the repo including the two new files. No new rule
   fires (none was added by this feature); this run only confirms the new
   ASCII/UTF-8-no-BOM Markdown and YAML files trip no EXISTING rule (e.g. a
   secret-pattern scan, an encoding check).

## What this quickstart deliberately does NOT do

- Does not connect to a database, run `retail validate`, or execute any SQL
  (Principle VIII; the anti-join sketch in Scenario A step 3 is illustration
  only).
- Does not pick a grain, PK, or PII ruling for any real table (Principle V;
  Scenarios B and C explicitly hand that decision to the adopting table's own
  mapping-gate review).
- Does not touch, redefine, or flip the status of Discount Amount, Discount
  Rate %, or Promotion Uplift % (FR-010).
- Does not add, wire, or depend on spec 087 / HR1 landing (FR-006).
- Does not emit or reference any numeric confidence/health/maturity score
  (hard rule #9) -- every checkpoint above is a status word (pass / blocked /
  a named human decision), never a number.
