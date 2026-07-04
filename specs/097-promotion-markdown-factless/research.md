# Research: Promotion/Markdown Fact and Factless-Fact Coverage Pattern

**Feature**: `specs/097-promotion-markdown-factless/` | **Phase**: 0 (research)

This is documentation research, not code research: what already-shipped
artifacts this feature must reuse, what it must stay distinct from, and what
capabilities are explicitly NOT assumed. Every claim below cites the artifact
it rests on (real repo paths).

## 1. Precedent survey -- what SHIPPED artifacts this feature reuses

| Shipped artifact | Real repo path | What this feature reuses from it |
|---|---|---|
| The domain-knowledge doc that names the gap | `skills/retail-kpi-knowledge/domains/discounts-and-promotions.md` | The KPI table (Discount Amount / Discount Rate % Seeded; Promotion Uplift % Planned "needs promotion dimension + baseline rule") and the decision-question table. This feature CITES this verbatim as the reason the pattern is needed; it does not redefine a KPI or flip a status marker (FR-010). |
| The mapping-gate template whose `gold_star` shape every fact template must mirror | `templates/source-map.yaml` | The `gold_star.fact` / `gold_star.dimensions` / `derived_columns` shape and the file's authoring-notes convention (a commented header explaining WHAT the file is, WHICH playbook phases it formalizes, and a placeholder-only body). The new `templates/factless-fact.yaml` (authored at implement stage, not this stage) follows this convention; this feature does not edit `source-map.yaml` itself (FR-002). |
| The one filled, measure-bearing worked example | `docs/worked-examples/retail-store-sales.md` and its gold star `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` | Cited ONLY as "an existing measure-bearing fact to anti-join against" (a "see" pointer). Per Principle VII and this spec's User Story 3 / FR-012, its real dimension and fact names (e.g. `fct_sales_rss`) are NOT inlined into the pattern doc's own illustration -- unlike spec 095's worked-example narrative (which legitimately inlines real names because it narrates that SAME table), this feature's illustration stays 100% generic placeholders (`sales_fact`, `dim_product`, `dim_store`, `dim_date`). |
| The RC14 conformed-dimension / Kimball-star discipline | `docs/decisions/0002-retail-cleaning-defaults.md` (RC14 -- "gold is a Kimball star: one fact at the silver grain + conformed dims, `_sk` surrogate keys, `-1` unknown member, FK COALESCE, degenerate dims") | The structural basis for FR-004's claim that a factless fact is STILL a valid Kimball star: it keeps the fact-plus-conformed-dimensions shape RC14 describes; what it lacks is an additive measure, not a dimension or a conformed-key discipline. |
| The cross-star conformed-dimension gate (pending, not yet ratified) | `specs/087-conformed-dimension-readiness/spec.md` (reserved rule id **HR1**, Draft status as of 2026-07-04) | Cited by FR-006 as the mechanism that WOULD eventually verify that a promotion/markdown star's and a factless star's shared dimensions (product, store, date) conform to an existing sales star's -- without this feature depending on 087 landing first, adding HR1 itself, or wiring any conformance check. |
| The Constitution's stop-and-ask discipline | `.specify/memory/constitution.md` Principle V | The obligation that grain, PII, promo mechanics, and the Promotion Uplift % baseline rule stay adopting-table/owner decisions, routed through the unchanged source-mapping gate -- never resolved by this feature (FR-008, FR-009). |
| The rule-registry / no-new-rule discipline | `src/retail/rules/__init__.py`, `docs/rules/rules-manifest.json`, `docs/rules/severity-posture.json` (existence confirmed, not read in full -- this feature does not open them) | The commitment this feature makes NOT to touch: no rule id reserved or added, no manifest regenerated, no severity posture changed (FR-007, SC-004). Mirrors the same "collision-avoidance allocation" discipline spec 095 and 087 each state for their own no-new-rule or reserved-id claims. |
| A recent same-shape sibling: a docs-only KPI-domain-gap pattern feature, same day | `specs/095-actuals-vs-target-budget-fact/research.md`, `spec.md` | The "documentation research, not code research" framing, the precedent-survey table shape, the "Deferred capabilities NOT assumed" section shape, and the discipline of citing a domain doc's Planned-KPI marker without touching it. This feature's research.md follows the same skeleton. |
| A recent same-shape sibling: a docs-only, no-new-rule plan (Constitution Check table format) | `specs/084-worked-example-factory/plan.md` | The table-format Constitution Check (one row per Principle, a Check question, a Result), the ASCII-tree Project Structure convention, and the "ride the existing spine, add zero new stage" framing for a feature that composes above the per-table spine rather than adding to it. |

## 2. Precedent survey -- what this feature must stay DISTINCT from (boundary)

Per the spec's own "Boundary against neighbouring shipped work" section, four
shipped/pending surfaces are cited and composed with, never edited or
resolved:

| Surface | Path | Why it stays untouched |
|---|---|---|
| The discounts-and-promotions domain doc | `skills/retail-kpi-knowledge/domains/discounts-and-promotions.md` | Owns the Discount Amount / Discount Rate % / Promotion Uplift % KPI definitions and statuses; this feature supplies a missing STRUCTURAL ingredient (a promotion fact shape and a factless-fact concept), never a KPI redefinition or a status flip. Byte-identical before/after (SC-006). |
| The source-mapping gate template | `templates/source-map.yaml` | Remains the existing, UNCHANGED artifact an adopting table fills to reach Mapping Ready for either a real promotion/markdown table or a real factless coverage table. This feature's own `templates/factless-fact.yaml` is a SEPARATE new file (authored at implement stage) that shows how to fill the same `gold_star` shape for a no-measure fact -- it does not touch `source-map.yaml` at all (FR-002). |
| The retail_store_sales worked example | `docs/worked-examples/retail-store-sales.md` | Cited only as an external "see" pointer (the sales fact a coverage fact would be anti-joined against); this feature does not edit it, add a promotion table to it, or invent worked numbers for it (FR-012). |
| Spec 087 (cross-star conformed-dimension readiness, HR1) | `specs/087-conformed-dimension-readiness/spec.md` | The CROSS-STAR conformance gate for shared dimensions once two-plus stars exist. This feature's pattern tells an adopter that a shared product/store/date dimension MUST be conformed, but adds no static rule, no reserved id, and no wiring of its own -- HR1, if and when ratified, is the only enforcement mechanism (FR-006). |

A repo-wide directory check confirms `docs/patterns/` does not yet exist as a
subdirectory (current `docs/*` top-level listing has no `patterns/`; see
`docs/architecture/`, `docs/readiness/`, `docs/decisions/`, `docs/worked-examples/`
as the closest siblings) and `templates/factless-fact.yaml` does not exist
under the flat `templates/` directory (43 existing template files enumerated,
none named `factless-fact.yaml`). This feature is additive only -- it creates
one new subdirectory under `docs/` (following the existing `docs/<topic>/`
convention) and one new flat file under `templates/`, at implement stage;
this plan stage creates neither of those two artifacts itself.

## 3. Input-source confirmation

The feature's only inputs are already-committed repository text, confirmed
present and read during this research pass:

- `specs/097-promotion-markdown-factless/spec.md` -- exists, read in full
  (Overview, Boundary section, three user stories, Edge Cases, 16 functional
  requirements, Key Entities, Success Criteria, Assumptions, Clarifications
  Q1-Q3, all RESOLVED).
- `skills/retail-kpi-knowledge/domains/discounts-and-promotions.md` -- exists,
  read in full; confirms Discount Amount and Discount Rate % are Seeded,
  Promotion Uplift % is Planned "needs promotion dimension + baseline rule."
- `templates/source-map.yaml` -- exists, read in full (every section: `meta`,
  `defaults`, `columns[]`, `gold_star.fact` / `.dimensions` /
  `.degenerate_dimensions` / `.date_dimension`, `derived_columns`, and the
  authoring-notes header).
- `docs/worked-examples/retail-store-sales.md` -- exists, read (header,
  "Readiness at a glance" table, Sec 1-2 structure) as the cited-only
  measure-bearing fact reference.
- `specs/087-conformed-dimension-readiness/spec.md` -- exists, Status: Draft
  (not yet ratified/implemented as of 2026-07-04); read (Overview, the two-part
  design: `docs/quality/conformed-dimension-map.yaml` + reserved rule id HR1).
- `.specify/memory/constitution.md` -- exists at version 1.7.0; Principles I
  through IX and the Readiness System section confirmed present and read in
  full.
- `specs/095-actuals-vs-target-budget-fact/research.md` and `spec.md` -- exist;
  read as the closest same-day sibling precedent for a docs-only,
  no-new-rule, KPI-domain-gap-closing pattern feature.
- `specs/084-worked-example-factory/plan.md` -- exists; read as the
  Constitution-Check-table-format precedent for a docs-only feature that adds
  zero new rule and zero new readiness stage.
- `templates/` directory listing (43 files) -- confirms no existing
  `factless-fact.yaml` and confirms the flat (no-subfolder, except the
  unrelated `templates/handoff/` bundle) placement convention FR-016 cites.
- `docs/` directory listing (119+ files across `architecture/`, `decisions/`,
  `readiness/`, `worked-examples/`, `roadmap/`, `quality/`, etc.) -- confirms
  the `docs/<topic>/` subdirectory convention FR-016 cites, and confirms
  `docs/patterns/` does not yet exist.

No external (non-repo) source is consulted. No promotion/markdown source
table, no real discount transaction file, and no live database connection is
available or sought -- confirmed absent by design (spec.md Assumptions: "No
promotion or markdown source table exists yet in any mapped table in this
repo; this feature is pattern-only").

## 4. Deferred capabilities NOT assumed

This feature explicitly does NOT assume the following exist or are reachable,
and authors nothing that depends on them:

- **F016 (Power BI execution adapter)** does not exist and is not assumed
  reachable. This feature produces no dashboard, no publish-layer artifact,
  and no live Power BI consequence of the pattern -- Constitution Principle II
  (the adapter is execution-only and gated on Semantic Model Ready, which
  this feature does not advance for any real table).
- **No live database connection, anywhere.** Per Constitution Principle VIII
  (static-first, live-deferred), this feature authors zero SQL migration,
  zero `retail validate` run, and zero live profiling. Unlike a feature with a
  live surface that marks an unmeasured number `[PENDING LIVE PROFILE]`, this
  feature has NO live surface to defer at all -- there is nothing to mark
  pending because nothing here connects to, queries, or assumes a database
  exists. The one illustrative SQL sketch this feature's pattern doc will
  contain (the anti-join, per Clarification Q3) is explicitly labeled
  non-executable and placeholder-only, never a proposed migration.
- **No new readiness stage, no new `retail check` rule, no reserved rule id.**
  This feature rides the EXISTING seven-stage per-table spine and the
  EXISTING source-mapping gate only (collision-avoidance allocation, FR-007).
  No file under `src/retail/rules/` is added or edited;
  `docs/rules/rules-manifest.json` and the severity-posture record are
  unaffected; no `mappings/<table>/readiness-status.yaml` key is added.
- **No real promotion/markdown table build.** No `mappings/<table>/`
  directory, no `warehouse/migrations/*.sql` for a promotion or factless
  fact, and no `powerbi/*.SemanticModel/` change is authored for any table. A
  real per-table promotion or factless-fact build is a separate, later effort
  that would walk the existing `source-mapping` -> `retail-build-warehouse`
  -> `retail-validate` sequence (spec.md Assumptions).
- **No promotion mechanics, grain, PII ruling, or baseline-rule decision.**
  Discount-type taxonomy, promo funding source, promo hierarchy, a real
  table's grain/PK, and the Promotion Uplift % baseline rule are all
  Principle-V judgment calls this feature explicitly flags as adopting-table/
  owner decisions, never resolves (FR-008, FR-009).
- **Spec 087 / HR1 is NOT assumed to land.** The pattern cites 087 as the
  future mechanism that would verify cross-star dimension conformance, but
  this feature's own correctness does not depend on 087 being ratified,
  implemented, or even remaining in its current Draft form.

## 5. The generic-illustration discipline (the delicate design point)

Unlike spec 095 (which legitimately inlines real committed names --
`dim_product_rss`, `gold.fct_sales_rss` -- because it narrates that SAME
table as a second worked example), this feature's pattern doc and template
are GENERIC artifacts (Principle VII) meant to be copied by any future table.
The discipline this feature holds, verified by FR-012 / SC-003 / User Story 3:

1. The pattern doc's own illustrations (the promotion/markdown fact shape,
   the factless coverage fact shape, the anti-join sketch) use ONLY generic
   placeholder names: `sales_fact`, `coverage_fact`, `promotion_fact`,
   `dim_product`, `dim_store`, `dim_date`, `promotion_id`, `markdown_amount`,
   `promoted_units`. None of these collide with a real committed name (the
   `_rss` suffix family, or any C086/pharmacy name).
2. `retail_store_sales` and `fct_sales_rss` are named exactly ONCE, as a
   citation ("see `docs/worked-examples/retail-store-sales.md` for an
   existing measure-bearing fact this pattern's coverage fact would be
   anti-joined against") -- never restated with an invented promotion column
   or an invented worked number.
3. The factless-fact template (authored at implement stage) mirrors
   `templates/source-map.yaml`'s OWN placeholder convention (angle-bracket
   placeholders like `<TABLE_ID>`, `<entity_a>`) rather than borrowing that
   file's specific example values.

This is the inverse of 095's resolution to its own two-table `binds_to`
tension (095 solves a structural-fit problem within an existing template;
097 solves a genericity-discipline problem across a brand-new pattern doc and
template pair) -- both are documented here as the load-bearing design choice
each feature made, but they are not the same choice.

## Sources cited in this research

- `specs/097-promotion-markdown-factless/spec.md` (this feature's own,
  now-clarified spec)
- `skills/retail-kpi-knowledge/domains/discounts-and-promotions.md`
- `templates/source-map.yaml`
- `docs/worked-examples/retail-store-sales.md`
- `specs/087-conformed-dimension-readiness/spec.md` (Draft; reserved id HR1)
- `docs/decisions/0002-retail-cleaning-defaults.md` (RC14)
- `.specify/memory/constitution.md` (Principles I-IX; Readiness System section)
- `specs/095-actuals-vs-target-budget-fact/research.md`, `spec.md` (style +
  structure precedent for a docs-only, no-new-rule, KPI-domain-gap pattern
  feature)
- `specs/084-worked-example-factory/plan.md` (Constitution Check table format
  precedent)
