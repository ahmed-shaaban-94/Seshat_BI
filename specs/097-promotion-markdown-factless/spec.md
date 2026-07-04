# Feature Specification: Promotion/Markdown Fact and Factless-Fact Coverage Pattern

**Feature Branch**: `097-promotion-markdown-factless`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Promotion/markdown fact + factless-fact coverage (gap #11).
A pattern for a promotion/markdown fact AND a factless fact (which products were on promo
but did NOT sell). Discount knowledge exists but there's no promotion fact and no
factless-fact concept, so 'what we discounted that didn't move' is unanswerable."

## Overview

`skills/retail-kpi-knowledge/domains/discounts-and-promotions.md` already carries two
Seeded KPIs (Discount Amount, Discount Rate %) computed off the discount fields already
present on the sales fact, plus one Planned KPI: **Promotion Uplift %**, explicitly marked
"needs promotion dimension + baseline rule." That domain doc tells the truth about the
gap: there is no promotion/markdown FACT in the kit's vocabulary today, and there is no
FACTLESS-FACT concept at all -- every worked fact in the repo (the `retail_store_sales`
star's `fct_sales_rss`, the source-map `gold_star.fact` template) carries at least one
additive measure. A Kimball star whose fact table records only that an EVENT or a
CONDITION occurred -- no dollar amount, no quantity, just the combination of dimension
keys that were true together -- has no home in the kit's documented shape.

This absence is not cosmetic. The business question the gap names -- "what did we
discount that did NOT sell?" -- is structurally unanswerable without a factless fact: it
requires a COVERAGE record (which product, at which store, on which day, was on
promotion) that exists independently of whether a sale happened, so it can be
LEFT-ANTI-JOINed against the sales fact to find the rows with no match. A promotion fact
that only records line items where discounted units actually SOLD can never answer this,
because a promotion that sold zero units leaves no row to look at. The kit needs to teach
both shapes -- a promotion/markdown fact (the normal, measure-bearing fact that lets a
promotion's own numbers be measured: markdown amount, promoted units, promotion count)
and a factless coverage fact (the enabling structure that makes "on promo but did not
sell" answerable) -- as a documented, reusable PATTERN, not as one more one-off table
build.

This feature adds that pattern as DOCUMENTATION AND A COPY-ME TEMPLATE ONLY. It teaches
the SHAPE (what a promotion/markdown fact looks like at the grain level; what a factless
fact looks like; how a factless fact still satisfies "gold IS a Kimball star" with no
additive measure; how the two compose with the existing sales star through conformed
dimensions to answer the "discounted but didn't move" question). It does not invent
promotion mechanics (discount types, promo funding source, promo hierarchy), does not
pick a grain for any real table, does not resolve the Promotion Uplift % baseline rule,
and does not build, migrate, or validate anything live. An adopting table's own analyst
and data owner make every mechanics/grain/PII decision, through the existing
source-mapping gate -- this feature changes nothing about how that gate works.

## Boundary against neighbouring shipped work (read first)

This feature is a genuine NEW pattern for a fact shape nothing in the kit documents
today, not a restatement of existing work. Four things it must stay distinct from:

- **`skills/retail-kpi-knowledge/domains/discounts-and-promotions.md`** already owns the
  Discount Amount / Discount Rate % / Promotion Uplift % KPI definitions and their
  Seeded/Planned status. This feature does NOT redefine those KPIs, does NOT change any
  KPI's status marker, and does NOT resolve the Promotion Uplift % baseline rule the
  domain doc names as the reason it stays Planned. It supplies the missing STRUCTURAL
  ingredient (a promotion dimension/fact and a factless coverage fact) that a future,
  separate KPI-contract change could eventually build on; enabling a structure is not the
  same as defining or promoting a metric, and this feature does neither.
- **`templates/source-map.yaml`** (Principle IV, the source-mapping gate) is the existing,
  UNCHANGED artifact an adopting table still fills to bring a promotion/markdown table or
  a factless coverage table to Mapping Ready. This feature adds NO new key to
  `source-map.yaml` and edits NO existing template. Its own factless-fact template is a
  SEPARATE new file that shows how to fill the existing `gold_star` shape for the case
  where a fact carries no measure -- it does not touch the file at all.
- **`docs/worked-examples/retail-store-sales.md`** and its `fct_sales_rss` star are the
  kit's one filled, measure-bearing fact example; this feature's pattern doc references it
  only as "the measure-bearing fact this pattern's coverage fact would be anti-joined
  against" -- it does not edit that worked example, does not add a promotion table to it,
  and invents no worked numbers for it.
- **Spec 087 (cross-star conformed-dimension readiness, HR1)** is the CROSS-STAR
  conformance GATE for shared dimensions once two or more stars exist. This feature's
  pattern explicitly tells an adopter that a shared dimension (a product or store or date
  dimension reused by both the sales star and the new promotion/factless star) MUST be
  conformed -- but it adds NO static rule, reserved rule id, or wiring to enforce that;
  HR1 (087), if and when ratified, is the only mechanism that checks conformance. This
  feature is docs + a template; it defines no `retail check` rule of its own and touches
  no rule registry, glossary rules table, or rule-count manifest.

This feature adds NO static `retail check` rule and NO new readiness stage. It composes
above the existing per-table spine exactly the way any new table would: an adopting table
still walks Source Ready through Publish Ready through the unchanged gates. The pattern
doc and its template are read-only guidance; they do not touch a shared schema file.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Answer "what did we discount that did not sell?" with a factless coverage fact (Priority: P1)

An analyst is asked the business question the gap names: "which products were marked
down / put on promotion but did not sell?" Today no artifact in the kit can even
represent the input this question needs, because every documented fact requires a sale to
exist as a row. Following the new pattern doc, the analyst understands that the answer
requires a FACTLESS fact -- one row per (product, store, day, promotion) COMBINATION that
was true regardless of whether a sale happened -- and that the question is answered by a
set-difference (a LEFT ANTI JOIN) between that coverage fact and the sales fact on their
shared conformed dimensions, not by adding a column to the sales fact.

**Why this priority**: This is the exact business question the gap is named for, and it
is the one question that is structurally impossible without a factless fact. If the
pattern doc does not make this case, and make it correctly, the feature has not closed
the gap it exists to close.

**Independent Test**: Given only the pattern doc and the factless-fact template, an
analyst unfamiliar with factless facts can (a) state, in their own words, why a
measure-bearing promotion fact alone cannot answer "discounted but did not sell", (b)
identify that a coverage row (product x store x day x promotion) is the unit the factless
fact records, and (c) describe the anti-join against the sales fact (on conformed
dimensions) that answers the question -- all without inventing any concrete promo
mechanics, because the doc supplies the shape and a fully placeholder-only illustration.

**Acceptance Scenarios**:

1. **Given** the pattern doc, **When** a reader looks for how "on promo but did not sell"
   is answered, **Then** the doc names a LEFT ANTI JOIN (or equivalent set-difference)
   between the factless coverage fact and the sales fact as the mechanism, and states
   this explicitly as the reason a factless fact is needed at all.
2. **Given** the factless-fact template, **When** a reader inspects its `gold_star.fact`
   shape, **Then** the template shows a fact with NO required additive measure (its
   `measures[]` may be empty or a documented degenerate coverage marker) and states that
   this is the defining difference from every other fact template in the repo.
3. **Given** the pattern doc's illustration, **When** it is checked for domain leakage,
   **Then** every dimension, key, and column name in the illustration is a generic
   placeholder (no real product, store, or promotion name/mechanic), per Principle VII.

---

### User Story 2 - Model the promotion/markdown fact itself (Priority: P2)

An analyst who has a real promotion or markdown source (line items or events tagged with
a promotion identifier and a markdown/discount amount) wants to know what SHAPE that
becomes in gold: a measure-bearing fact (promotion/markdown amount, promoted units,
promotion-line count) at its own grain, joined to the same conformed dimensions the sales
star already uses (product, store, date), so promotion activity can be measured on its
own terms (not only inferred from the sales fact's existing discount columns).

**Why this priority**: This is the fact half of the pattern and is what most future KPIs
in this domain (beyond the two already-Seeded discount KPIs) will be built on. It is P2,
not P1, because the coverage/factless case (US1) is the harder, previously-impossible
capability and the actual reason the gap was opened; the measure-bearing fact is a more
conventional Kimball pattern the kit's existing worked example already demonstrates the
mechanics for (a fact + conformed dims), just not for this subject.

**Independent Test**: Given the pattern doc's promotion/markdown fact section alone (no
other section), an analyst can state its candidate grain in placeholder terms (e.g. "one
row per promotion line per day per store"), name at least one additive measure it would
carry, and identify which existing conformed dimensions it would reuse rather than
duplicate -- all clearly marked as a decision the adopting table's own mapping gate makes,
not a decision this feature makes for them.

**Acceptance Scenarios**:

1. **Given** the pattern doc, **When** a reader looks for the promotion/markdown fact's
   candidate shape, **Then** the doc shows a `gold_star.fact` with at least one additive
   measure placeholder (e.g. a markdown-amount-shaped measure) and states the grain
   question is an adopting-table decision, not a value this feature supplies.
2. **Given** the pattern doc, **When** a reader looks for which dimensions the
   promotion/markdown fact shares with the sales star, **Then** the doc names product,
   store/location, and date as the dimensions expected to be CONFORMED (reused, not
   re-created) and cites spec 087 as the mechanism that would eventually verify that
   conformance, without this feature adding that mechanism itself.
3. **Given** the pattern doc, **When** checked against the discounts-and-promotions
   domain doc, **Then** it does not restate or alter the Discount Amount / Discount Rate %
   contracts and does not assert a value or status for Promotion Uplift %.

---

### User Story 3 - The pattern is generic and reusable across tables (Priority: P3)

A future analyst onboarding a second, unrelated table with its own promotion or
markdown source reuses the same pattern doc and factless-fact template -- copying the
template, filling it with their own table's real names via the existing source-mapping
gate -- without the pattern doc or template containing any specific table's names, so
the pattern is proven reusable rather than a one-off write-up for a single table.

**Why this priority**: Genericity (Principle VII) is what turns this from a one-time memo
into a reusable kit pattern; a working, correct pattern for one hypothetical case (US1/US2)
is already the valuable slice, so verifying it stays generic is P3.

**Independent Test**: Grep the pattern doc and the factless-fact template for any
worked-example (C086/pharmacy, `retail_store_sales`) or any other real table's specific
column/dimension/promotion names; confirm none appear except as an explicitly cited
external reference (a "see" pointer to the existing worked example), never inlined as if
it were the pattern's own content.

**Acceptance Scenarios**:

1. **Given** the pattern doc, **When** searched for domain-specific nouns, **Then** only
   generic placeholder names appear in the pattern's own illustrations.
2. **Given** the factless-fact template, **When** compared to `templates/source-map.yaml`,
   **Then** it follows the same `gold_star` shape and authoring-notes convention (so a
   reader already familiar with `source-map.yaml` recognizes the pattern immediately)
   without copying any of that file's placeholder table's specific values.
3. **Given** the pattern doc's references, **When** it points to `retail_store_sales`,
   **Then** it is cited as "an existing measure-bearing fact to anti-join against," never
   restated with invented promotion data that worked example does not have.

---

### Edge Cases

- What happens when an adopting table's promotion coverage rows and its sales rows do not
  share a conformed dimension (e.g. the promotion source only has a category, not a
  product key)? The pattern doc must state that the anti-join in US1 requires the two
  facts to share a conformed grain-compatible key on the joined dimension(s); when they do
  not, the pattern names this as a blocking mapping-gate question for that adopting table
  to resolve (a Principle-V grain/mapping judgment), not something this feature resolves
  or works around with an invented crosswalk.
- What happens when a product/store/day combination was on promotion for only PART of a
  day, or under more than one overlapping promotion? Grain and overlap-handling for a real
  promotion source are adopting-table mapping decisions (Principle V); the pattern
  states this explicitly as an open question the template's grain field flags rather than
  answering.
- What happens when "did not sell" needs to mean "sold below a baseline" rather than
  "zero units"? That is the same baseline-rule gap the Promotion Uplift % KPI is already
  Planned pending (per the domain doc); this feature's factless fact enables a
  zero-units anti-join today and explicitly does not define or resolve a baseline rule --
  that stays a future, separate KPI-contract decision.
- What happens when someone tries to add a "coverage count" measure to the factless fact
  to make it "feel" like a normal fact? The pattern doc must state that a `COUNT(*)` over
  the factless fact's degenerate rows answers "how many combinations were on promotion,"
  which is a valid read, but adding a stored additive measure column to a factless fact
  (inventing a quantity/amount that does not exist in the source) would misrepresent the
  fact's nature and is explicitly discouraged.
- What happens when only ONE of the two patterns (promotion fact OR factless fact) is
  relevant to a given adopting table? The pattern doc and template must be usable
  independently -- a table with real promotion transaction data but no need for
  "did-not-sell" analysis can adopt only the promotion/markdown fact section, and a table
  that already has a promotion fact elsewhere can adopt only the factless-coverage
  section.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: This feature MUST add exactly one new pattern document under `docs/`
  describing (a) a promotion/markdown fact shape and (b) a factless coverage-fact shape,
  and how the two compose with an existing sales star to answer "what was discounted/on
  promotion but did not sell."
- **FR-002**: This feature MUST add exactly one new copy-me template for the
  factless-fact shape, following the existing `templates/source-map.yaml` `gold_star`
  authoring convention (fact + dimensions + placeholders + authoring notes), and MUST NOT
  edit `templates/source-map.yaml` or any other existing template.
- **FR-003**: The pattern doc MUST explain WHY a measure-bearing fact alone cannot answer
  "on promo but did not sell" (no row exists for a promotion that sold zero units) and
  MUST name the LEFT ANTI JOIN (or equivalent set-difference) between the factless
  coverage fact and the sales fact, on their shared conformed dimensions, as the mechanism
  that answers the question.
- **FR-004**: The pattern doc and the factless-fact template MUST show a factless fact
  whose `gold_star.fact` carries NO REQUIRED additive measure -- an empty or
  degenerate-only `measures[]` -- and MUST state this is the defining structural
  difference from every measure-bearing fact template already in the repo (Principle III:
  the factless fact is still a valid Kimball star -- fact + conformed dimensions -- even
  though its fact table has no dollar/quantity measure).
- **FR-005**: The pattern doc MUST also document a promotion/markdown fact shape that
  DOES carry at least one additive measure placeholder (e.g. a markdown-amount-shaped
  measure, a promoted-units-shaped measure), distinct from the factless coverage fact, so
  the two shapes are not conflated.
- **FR-006**: The pattern doc MUST state that both the promotion/markdown fact and the
  factless coverage fact are expected to reuse the SAME conformed dimensions (product,
  store/location, date) that an existing sales star already carries, rather than each
  minting its own copy -- and MUST cite spec 087 (cross-star conformed-dimension
  readiness) as the existing/pending mechanism that would verify that conformance, without
  this feature adding, wiring, or duplicating that mechanism itself.
- **FR-007**: This feature MUST NOT add, modify, or reserve any `retail check` static rule
  id, MUST NOT touch `src/retail/rules/__init__.py`, `EXPECTED_RULE_IDS`, the glossary
  rules table, `docs/rules/rules-manifest.json`, or the severity-posture record, and MUST
  NOT add a new readiness stage or a new key to any `mappings/<table>/readiness-status.yaml`
  shape.
- **FR-008**: This feature MUST NOT invent promotion mechanics (discount-type taxonomy,
  promo funding source, promo hierarchy/campaign structure) beyond generic,
  clearly-labeled placeholders; every concrete mechanic is an adopting table's own
  source-mapping-gate decision (Principle IV/V).
- **FR-009**: This feature MUST NOT pick a grain, primary key, or column set for any real
  table, and MUST NOT resolve the Promotion Uplift % baseline rule the
  discounts-and-promotions domain doc already marks Planned; both remain explicitly
  adopter/owner decisions the pattern flags rather than answers.
- **FR-010**: The pattern doc and template MUST NOT alter the Discount Amount or Discount
  Rate % KPI contracts, MUST NOT change any KPI's Seeded/Planned status in
  `skills/retail-kpi-knowledge/domains/discounts-and-promotions.md`, and MUST NOT define a
  new metric contract.
- **FR-011**: This feature MUST NOT connect to a database, execute or propose any
  migration SQL, or invoke any deferred execution adapter (F016); it is static
  documentation and a template only (Principle VIII).
- **FR-012**: The pattern doc and template MUST stay generic (Principle VII): no
  worked-example (C086/pharmacy, `retail_store_sales`) or other real table's specific
  column, dimension, or promotion name may be inlined into the pattern's own
  illustrations; the shipped worked example may be cited only as an external reference
  (a "see" pointer).
- **FR-013**: The pattern doc MUST explicitly document at least the four edge cases named
  in this spec's Edge Cases section (dimension mismatch for the anti-join, partial-day/
  overlapping-promotion grain ambiguity, the "did not sell" vs "sold below baseline"
  distinction, and the discouraged practice of adding a fabricated measure to a factless
  fact) as adopter-facing guidance, not as answers this feature supplies.
- **FR-014**: This feature MUST NOT emit, and the pattern doc/template MUST NOT contain,
  any numeric confidence/health/maturity score or completeness count (hard rule #9).
- **FR-015**: All authored artifacts MUST be ASCII, UTF-8 without BOM (use `--` and `->`,
  no glyphs such as em-dashes or curly quotes), and MUST use short repo-relative paths
  (Windows 260-char budget) (Principle IX).
- **FR-016**: RESOLVED (Default adopted, non-Principle-V naming call; see Clarifications).
  The new pattern doc MUST live at `docs/patterns/promotion-markdown-factless.md` (a new
  `docs/patterns/` subdirectory, following the existing `docs/<topic>/` layout convention
  used by `docs/worked-examples/`, `docs/architecture/`, etc.) and the new factless-fact
  template MUST live at `templates/factless-fact.yaml` (flat under `templates/`, matching
  every existing template's placement -- `templates/` has no subfolders except the
  unrelated `templates/handoff/` bundle). Both paths are short and well within the Windows
  260-char budget (Principle IX / FR-015). The plan stage MUST use these exact paths rather
  than inventing alternates.

### Key Entities *(include if feature involves data)*

- **Promotion/markdown fact (pattern)**: a documented, measure-bearing Kimball fact shape
  at a placeholder grain (e.g. one row per promotion line per store per day), carrying at
  least one additive measure (a markdown-amount-shaped placeholder), joined to conformed
  product/store/date dimensions. No concrete table's grain or measure set is fixed by this
  feature.
- **Factless coverage fact (pattern)**: a documented Kimball fact shape recording that a
  (product, store, day, promotion) COMBINATION held true, independent of any sale --
  carrying NO required additive measure. Its only "measure" is a row-count / degenerate
  coverage marker. It is still a valid Kimball star because it retains a fact table plus
  conformed dimensions (Principle III); what it lacks is an additive measure, not a
  dimension.
- **Anti-join mechanism (pattern)**: the documented LEFT ANTI JOIN (or equivalent
  set-difference) between the factless coverage fact and an existing sales fact, on their
  shared conformed dimensions, that answers "on promo but did not sell." A described
  technique, not an executed query.
- **Factless-fact template**: the new copy-me artifact under `templates/` that shows how
  to fill a `gold_star`-shaped block for a fact with no required measure, mirroring
  `templates/source-map.yaml`'s authoring-notes convention.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader with no prior exposure to factless facts can, from the pattern doc
  alone, correctly explain why a measure-bearing promotion fact cannot answer "discounted
  but did not sell" and correctly name the anti-join mechanism that does.
- **SC-002**: The shipped factless-fact template contains zero required entries under its
  fact's `measures[]` (its measure list is empty or explicitly marked degenerate/optional),
  distinguishing it from every existing measure-bearing fact template in the repo.
- **SC-003**: Zero worked-example (C086/pharmacy, `retail_store_sales`) or other real
  table's specific column, dimension, or promotion names appear inlined in the pattern
  doc's or template's own illustrations (verified by inspection); any reference to a real
  table is a citation, not inlined content.
- **SC-004**: Zero `retail check` rule ids, rule-registry files, or readiness-status.yaml
  keys are added, modified, or referenced as owned by this feature.
- **SC-005**: Zero numeric confidence/health/maturity scores or completeness counts appear
  in any artifact this feature produces.
- **SC-006**: The Discount Amount and Discount Rate % KPI contract files and the
  Promotion Uplift % Planned marker are byte-identical before and after this feature
  lands (this feature changes neither).

## Assumptions

- The discounts-and-promotions domain doc's characterization of the gap (Discount Amount
  and Discount Rate % are Seeded; Promotion Uplift % is Planned pending "a promotion
  dimension + baseline rule") is accurate and current as read on 2026-07-04; this feature
  supplies the missing structural half (the promotion dimension/fact and the factless
  coverage concept) and leaves the baseline-rule half explicitly open for a future,
  separate decision.
- No promotion or markdown source table exists yet in any mapped table in this repo; this
  feature is pattern-only and does not onboard, profile, or map any such table.
- An adopting table's promotion/markdown fact and factless coverage fact will each go
  through the existing, unchanged source-mapping gate (Principle IV) exactly like any
  other new table; this feature changes nothing about that gate's mechanics or its five
  artifacts.
- Cross-star conformance between a new promotion/factless star's dimensions and an
  existing sales star's dimensions is expected to eventually be checked by spec 087's HR1
  rule if and when that spec is ratified and implemented; this feature does not depend on
  087 landing first, and does not itself add any conformance check.
- "Did not sell" is treated, for this pattern's illustration, as "zero recorded sale rows
  for that combination" (a plain anti-join); a more nuanced "sold below expectation"
  definition is a business-policy decision left to a future baseline-rule/KPI feature, not
  answered here.
- The new pattern doc and factless-fact template are the ONLY new artifacts; no change to
  `src/retail/`, `src/retail/rules/`, any `mappings/<table>/` folder, or any existing
  template is in scope for this feature.

## Clarifications

### Session 2026-07-04

- **Q1 (touches FR-016)**: What exact file paths should the new pattern doc and the new
  factless-fact template use?
  **Resolution**: Default adopted. `docs/patterns/promotion-markdown-factless.md` for the
  pattern doc (new `docs/patterns/` subdirectory, following the repo's existing
  `docs/<topic>/` layout convention) and `templates/factless-fact.yaml` for the template
  (flat under `templates/`, matching every existing template's placement). This is a
  naming/placement choice (non-Principle-V), so Principle VI applies: the spec's own "e.g."
  examples are adopted verbatim as the fixed paths rather than left open. FR-016 updated
  from `[NEEDS CLARIFICATION]` to RESOLVED with these paths.

- **Q2 (touches FR-004, FR-013)**: FR-004 allows the factless fact's `measures[]` to be
  "empty or a documented degenerate coverage marker" -- which of the two should the shipped
  template actually show, so SC-002 ("zero required entries") is unambiguous to verify?
  **Resolution**: Default adopted. The template MUST show `measures: []` (empty) as the
  fact's measure list, plus an authoring note stating that `COUNT(*)` over the coverage
  fact's rows is a valid read ("how many combinations were on promotion") without being a
  stored measure column. This keeps the template's `measures[]` unambiguously empty for
  SC-002's inspection test, and is consistent with the Edge Cases section's explicit
  discouragement of adding a fabricated `coverage_count` column to the fact.

- **Q3 (touches FR-003, FR-011, FR-012)**: Should the pattern doc's LEFT ANTI JOIN
  mechanism (FR-003) be shown as an illustrative SQL sketch or described only in prose,
  given FR-011 bars any migration/execution SQL and FR-012 bars real table names?
  **Resolution**: Default adopted. The doc shows one short, fully placeholder-only
  illustrative SQL sketch of the anti-join (generic table/column names only, e.g.
  `coverage_fact` LEFT ANTI JOIN-equivalent against `sales_fact` on placeholder conformed
  keys), explicitly labeled as an illustration of the technique, not a proposed or runnable
  migration. This satisfies FR-003's "name the mechanism" requirement more concretely than
  prose alone, while FR-011's bar on migration/execution SQL is read as barring SQL meant to
  be run or proposed for execution against a real table -- not barring a labeled,
  non-executable illustrative sketch -- and FR-012's placeholder-only rule is met by using
  no real table, column, or promotion name in the sketch.

No Principle-V judgment calls (grain, PII, promotion mechanics, the Promotion Uplift %
baseline rule, or any approval decision) were surfaced as open by this clarification pass.
Every such call the spec touches is, by design, already delegated to an adopting table's
own analyst/data-owner through the unchanged source-mapping gate (see Boundary section and
FR-008/FR-009); recording that delegation as an OPEN item here would misstate this
feature's own scope as blocked on a decision it explicitly does not make. There is
therefore no OPEN owner ruling to carry forward from this stage.
