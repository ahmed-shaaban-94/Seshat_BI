# Feature Specification: Returns/Refunds Fact Worked Example (Negative-Quantity Additivity)

**Feature Branch**: `096-returns-refunds-fact-example`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Gap #4. Returns/refunds fact worked example
(negative-quantity additivity). A second worked example modeling a returns fact
end-to-end (Stages 2-6): negative quantities, net-vs-gross additivity, cross-period
returns. Returns knowledge+contract are seeded but never modeled; the spine is
unproven on the fact type that breaks naive additivity."

## Overview

Seshat BI ships exactly one worked example, `retail_store_sales`
(`docs/worked-examples/retail-store-sales.md`), and that example explicitly recorded
returns as OUT OF SCOPE: its `source-map.yaml` marks RC8 (the returns cleaning default)
`N/A -- no return-flag column, all measures strictly positive`
(`docs/worked-examples/retail-store-sales.md` line 116). Meanwhile the KPI knowledge
layer already SEEDS a returns domain and a filled metric contract --
`skills/retail-kpi-knowledge/domains/returns.md` and
`skills/retail-kpi-knowledge/contracts/returns-rate-value.md` (`KPI-MC-08`) -- that state
the exact fact this repo has never modeled: **return value is additive; the return RATE
is non-additive and must be recomputed per level**, and that returns must carry an
explicit `transaction_type` / return flag rather than being netted invisibly into sales
(knowledge-layer ambiguity A2), with the sale-date-vs-return-date axis (A3) left as an
open business definition.

This means the medallion spine -- profile, map, gate, build, validate, contract, model,
design (Stages 2-6 of the seven-stage readiness model) -- has never been exercised on a
fact type that BREAKS NAIVE ADDITIVITY: a returns line can carry a negative quantity
and/or a negative amount, a "net sales" figure only reconciles when returns are
correctly signed and dated, and a return recorded in a period after its original sale
(a cross-period return) is exactly the case that silently corrupts a period total if the
wrong date axis is chosen. `retail_store_sales` proved the spine on a fact where every
measure is a plain, strictly-positive SUM; it proved nothing about a fact where additivity
itself is a modelling decision.

This feature defines a SECOND worked example -- a generic returns/refunds fact, built
under `docs/worked-examples/` and `mappings/<returns-example>/` -- that walks Stages 2-6
of the readiness spine on that harder fact type: negative-quantity handling, a
correctly-classified additive-value / non-additive-rate measure pair, and a documented
cross-period reconciliation. It is the first concrete SECOND instance produced under the
worked-example factory's recipe (spec 084) and stresses a genericity axis
`retail_store_sales` cannot: presence of returns (spec 084 FR-002's "returns
presence/absence" axis, named there only as an illustrative candidate, never built).

## Boundary against neighbouring shipped work (read first)

This feature is a genuine SECOND worked example filling a proven gap, not a restatement
of existing work. Four shipped/reserved neighbours must stay distinct:

- **`docs/worked-examples/retail-store-sales.md`** (the repo's only worked example today)
  is the sharpest boundary: it recorded RC8 as `N/A` and never modeled a return. This
  feature is the instance that proves the returns path `retail_store_sales` explicitly
  deferred. It does NOT edit `retail-store-sales.md`, does NOT reuse its table name or
  any of its recorded approvals/figures, and does NOT retroactively add returns to that
  table's source (its source genuinely has none).
- **spec 084 (worked-example-factory)** defines the REPEATABLE PROCESS and the
  completeness contract for producing a new worked example, and explicitly forbids
  ITSELF from authoring or scaffolding one (084 FR-011, Non-Goals). This feature is that
  process's first real consumer: it MUST satisfy 084's completeness contract
  (`contracts/worked-example-completeness.md`, once authored) rather than invent its own
  bar, and it MUST NOT propose a new RC default or `retail check` rule to make the
  domain expressible (084 FR-012) -- it is scoped to what RC8 (returns kept, `is_return`
  derived from the authoritative transaction-type column, never from measure sign) and
  the existing rule set already allow.
- **spec 068 / rule AD1 (additivity-consistency-rule)** owns the additivity
  CLASSIFICATION vocabulary and the composition-legality check ("Fully additive" /
  "Semi-additive" / "Non-additive"; no direct SUM of a non-additive/semi-additive
  metric). This feature CONSUMES that vocabulary when classifying its returns-value and
  returns-rate measures; it does NOT redefine the vocabulary, does NOT add a new
  legality rule, and does NOT modify `src/retail/rules/rule_ad1.py` or its wiring. Any
  additivity KEY this example's metric contracts populate is the key AD1 already reads
  (define-layer prose), never a new field invented here.
- **spec 087 / rule HR1 (conformed-dimension-readiness)** owns cross-star CONFORMED
  DIMENSION declaration and enforcement (`docs/quality/conformed-dimension-map.yaml`).
  If this example's returns fact shares a dimension (e.g. a product or date dimension)
  with `retail_store_sales` or `demo_sample_orders`, this feature MUST NOT declare that
  conformance itself -- declaring two stars' same-named dimension as one conformed
  business dimension is HR1's human-authored judgment call, not a worked-example
  authoring step. This feature may NOTE that the question exists; it does not answer it.

This feature adds NO new `retail check` rule, NO new RC cleaning default, and NO new
readiness stage (collision-avoidance allocation). It adds exactly one new worked-example
narrative doc and one new `mappings/<returns-example>/` directory; it CONSUMES the
additivity vocabulary (068/AD1) and, where relevant, notes the conformed-dimension
question (087/HR1) without resolving either.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An author walks a returns fact through Stages 2-6 without breaking additivity (Priority: P1)

An author (agent or analyst) building the repo's second worked example profiles a raw
returns/refunds source, maps it (Stage 2), gates the map, builds silver+gold (Stage 3-4),
and authors metric contracts and a governed model (Stage 5-6) for a fact whose measures
include a signed quantity/amount. The resulting example correctly classifies "Return
Value" as additive and "Return Rate %" as non-additive (per
`skills/retail-kpi-knowledge/contracts/returns-rate-value.md`), never SUMs the rate, and
documents how a return recorded in a later period than its original sale is handled so
period totals do not silently misstate.

**Why this priority**: This is the entire point of the gap -- proving the spine on the
one fact type (returns) whose naive handling (summing a rate, netting a return
invisibly into sales, or picking the wrong date axis) produces a plausible-looking but
wrong number. Without this, the feature delivers nothing beyond a second copy of the
first example's easy case.

**Independent Test**: Given the completed example's metric contracts, confirm the
Return Value contract states additivity "Fully additive" and the Return Rate % contract
states "Non-additive" (matching `returns-rate-value.md`'s own additivity statement
verbatim), confirm no derivation edge in the example composes the rate by direct SUM
(the AD1 legality check the example's contracts must satisfy), and confirm the example's
narrative doc states which date axis (sale date or return date) is primary for its
worked figures and why a cross-period return does not double-count or drop value under
that choice.

**Acceptance Scenarios**:

1. **Given** the returns example's silver layer carries a signed quantity/amount for
   return lines, **When** the gold-layer measures are defined, **Then** "Return Value"
   is documented as additive (summable across any dimension) and "Return Rate %" is
   documented as non-additive (must be recomputed per level, never summed), matching the
   seeded contract's own additivity statement.
2. **Given** a return that occurred in a calendar period after its original sale,
   **When** the example's reconciliation narrative is read, **Then** it states the
   chosen primary date axis and shows, with a worked evidence figure from the example's
   own committed data, that a period total under that axis does not silently drop or
   double-count the return's value.
3. **Given** the example's metric contracts for Return Value and Return Rate %, **When**
   `retail check`'s AD1 rule is run against the repo, **Then** it emits zero ERROR
   findings attributable to this example's contracts (no illegal composition
   introduced).

---

### User Story 2 - Negative quantities are sign-managed, never assumed from measure sign alone (Priority: P1)

An author models the returns fact's grain and its `is_return` classification using RC8:
the return/non-return flag is derived from an authoritative transaction-type column
(never inferred from whether an amount happens to be negative), and the source-map
documents how negative quantities and negative amounts are validated (e.g. a return line
must carry a negative or zero quantity, never a positive one) as part of the mapping
gate's reconciliation evidence.

**Why this priority**: RC8 already exists as a shipped default specifically to prevent
"treating returns as negative sales with no separate visibility"
(`skills/retail-kpi-knowledge/contracts/returns-rate-value.md`, "Common mistakes"; A2 in
the domain doc). A worked example that let sign alone stand in for classification would
demonstrate the exact anti-pattern the KPI layer warns against, defeating the feature's
purpose. This is co-equal in priority with US1: additivity and sign-correctness are two
faces of the same negative-quantity problem.

**Independent Test**: Inspect the example's `source-map.yaml`; confirm `is_return` (or
the equivalent classification field) is mapped from a transaction-type/reason column,
confirm the reconciliation report documents a check that return lines carry non-positive
quantity, and confirm the mapping's assumptions/unresolved-questions record any case
where sign and transaction-type column disagree as a surfaced anomaly, not a silently
resolved one.

**Acceptance Scenarios**:

1. **Given** the returns source carries both a transaction-type column and a signed
   quantity column, **When** the source-map is authored, **Then** `is_return` (or its
   mapped equivalent) is derived from the transaction-type column per RC8, and the map
   records this choice as the applied default (not a deviation).
2. **Given** a source row where the transaction-type column says "return" but the
   quantity is recorded as positive (or vice versa), **When** the mapping is profiled,
   **Then** the discrepancy is surfaced in the mapping's assumptions or
   unresolved-questions artifact, never silently coerced to agree.
3. **Given** the completed gold layer, **When** net sales and gross sales are both
   computed, **Then** the narrative shows the arithmetic relationship between them
   (gross minus return value equals net, or the example's own stated equivalent) with a
   real evidence figure, not an asserted claim.

---

### User Story 3 - The example stops honestly at what a repo-only, no-live-DB build can prove (Priority: P2)

An author or reviewer checks how far the returns example reaches without a live
database connection or the (deferred, not-yet-built) Power BI execution adapter (F016).
The example's `readiness-status.yaml` shows Stages 2-3 (Mapping Ready, Silver Ready) and
the static parts of Stage 4-6 (Gold Ready's static checks, metric contracts, the
governed TMDL model) authored and internally consistent, while every LIVE-gated check
(Gold Ready's live reconciliation, a live semantic-model connection) is explicitly
`blocked` or `[PENDING LIVE PROFILE]` -- never a fabricated `pass` and never a numeric
completeness score.

**Why this priority**: Matches the repo-only completeness tier spec 084 defines and the
constitution's Static-First/Live-Deferred principle; without this boundary the example
could misrepresent how far it actually got. It is P2 because the honest-stopping-point
behavior is a correctness property of the DOCUMENTATION, not the core additivity proof
that makes the example valuable (US1/US2 are the substance).

**Independent Test**: Read the example's `readiness-status.yaml`; confirm every stage
whose evidence would require a live DB connection or F016 shows `blocked` with a
`blocking_reasons[]` entry naming the missing live surface, and confirm no stage shows
`pass` without a cited committed-artifact evidence line.

**Acceptance Scenarios**:

1. **Given** no live database is available to this feature's authoring, **When** Gold
   Ready's live checks (PK/grain uniqueness, orphan-FK, penny-exact reconciliation) are
   reached, **Then** `readiness-status.yaml` records them `blocked` with a
   `blocking_reasons[]` entry naming the missing live surface, never a fabricated `pass`.
2. **Given** F016 (the Power BI execution adapter) does not exist, **When** the example's
   semantic model is authored, **Then** the narrative states the TMDL model is authored
   and statically checkable but not opened in Power BI Desktop or connected live.
3. **Given** the completed example, **When** its readiness record is inspected, **Then**
   it contains no numeric confidence/health/maturity score and no "N of M" completeness
   tally anywhere (hard rule #9).

---

### Edge Cases

- What happens when the exchange-handling question arises (a customer returns one item
  and buys another in the same visit)? Per the seeded domain doc's own ambiguity
  ("Exchanges: treat as return + new sale, or netted? Needs business definition",
  `skills/retail-kpi-knowledge/domains/returns.md`), the example MUST NOT invent an
  answer -- it records this as an unresolved question in the example's own
  `unresolved-questions.md` and, if the chosen source data contains no exchange case,
  states that the scenario is out of scope for this instance rather than fabricating one.
- What happens when the primary date axis (sale date vs return date, ambiguity A3) is
  needed to compute a period total? The example MUST record which axis it uses as an
  explicit, cited choice (Principle VI default-then-deviation) or, if the choice is a
  genuine business-policy call the source data cannot settle on its own, raise it as
  [NEEDS CLARIFICATION] rather than silently picking one -- see FR-013.
- What happens when VAT/tax treatment of a refund differs from the original sale's tax
  treatment? Per the SCOPE GUARD, the example MUST NOT invent a VAT or period-close
  policy; it either finds source data where tax handling is already explicit and cites
  it, or raises the gap as [NEEDS CLARIFICATION] / an explicit Assumption naming the
  deferred policy.
- What happens when a return references an original sale that is outside the chosen
  source's captured date range (an orphaned return)? The mapping's reconciliation
  evidence must surface this as a data-quality finding, not silently drop or fabricate
  the missing original sale.
- What happens when the returns example's dimensions (e.g. product, date) share a name
  with a dimension already used by `retail_store_sales` or `demo_sample_orders`? The
  example notes the potential cross-star conformance question and points to spec
  087/HR1 as the mechanism that would enforce it; it does NOT author or edit
  `docs/quality/conformed-dimension-map.yaml` itself (that is a human declaration, per
  087's own boundary).
- What happens when a named-human approval (Mapping Ready, Semantic Model Ready) has not
  yet been granted at the time this instance is authored? The readiness record shows
  that stage `blocked` with an empty `approvals[]` slot, exactly like every other
  worked-example and Product-Module precedent (Principle V) -- the agent never
  self-grants it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST define a SECOND worked example, distinct from
  `retail_store_sales`, whose subject is a returns/refunds fact, under a NEW
  `docs/worked-examples/<returns-example>.md` narrative doc and a NEW
  `mappings/<returns-example>/` directory, following the section structure and artifact
  set `retail-store-sales.md` established (per `docs/worked-examples/README.md`'s "How
  to reuse it").
- **FR-002**: The example MUST walk readiness Stages 2 through 6 (Mapping Ready through
  Semantic Model Ready, per `docs/readiness/readiness-model.md`) using the SAME gates,
  templates, and RC cleaning defaults every other table uses -- no new template, no new
  RC default, no new `retail check` rule introduced to make the domain expressible
  (mirrors spec 084 FR-012's constraint).
- **FR-003**: The example's source data MUST include at least one return/refund
  transaction whose quantity and/or amount is recorded with a sign or flag distinguishing
  it from a normal sale, so the negative-quantity/additivity behavior in US1/US2 is
  exercised on REAL committed data, never a hypothetical. DEFAULT ADOPTED (Principle VI):
  the source data is a small, hand-authored GENERIC synthetic dataset committed under
  `mappings/<returns-example>/`, in the same posture `retail_store_sales` used for its
  own source -- not a live-fetched or third-party dataset -- sized only as large as
  needed to exercise US1/US2/US3's acceptance scenarios (including at least one
  cross-period return and, per FR-004, at least one row usable to demonstrate the
  sign-vs-transaction-type discrepancy check).
- **FR-004**: The example MUST derive its return/non-return classification (`is_return`
  or an equivalent field) from an authoritative transaction-type/reason column per RC8,
  and MUST NOT derive that classification from measure sign alone. Any row where sign and
  the authoritative column disagree MUST be surfaced in the mapping's
  assumptions/unresolved-questions artifact, never silently coerced.
- **FR-005**: The example MUST author a metric contract for a returns VALUE measure
  (additive) and, separately, a returns RATE measure (non-additive), each stating its
  additivity classification using the same closed vocabulary spec 068/AD1 reads ("Fully
  additive" / "Semi-additive" / "Non-additive"), consistent with
  `skills/retail-kpi-knowledge/contracts/returns-rate-value.md`'s own additivity
  statement. It MUST NOT introduce a new additivity vocabulary word or a new
  machine-readable additivity field beyond what AD1 already reads.
- **FR-006**: The example's derivation lineage (if a returns-rate contract declares it
  derives from the returns-value and a sales-value contract) MUST NOT compose the rate by
  direct SUM of its parents -- consistent with the AD1 legality table -- so that running
  `retail check`'s AD1 rule against the repo after this example lands produces zero new
  ERROR findings.
- **FR-007**: The example MUST document, in its narrative doc, which date axis (original
  sale date or return date) is primary for its worked period-total figures, and MUST show
  at least one worked reconciliation figure demonstrating that a cross-period return
  (recorded in a later period than its original sale) does not silently drop or
  double-count value under the chosen axis.
- **FR-008**: The example MUST NOT invent an exchange-handling policy, a VAT/tax
  treatment for refunds, or a period-close rule. Where the source data does not already
  make such a policy explicit, the example MUST record it as an open item in
  `unresolved-questions.md` and/or an explicit Assumption citing the deferred policy --
  never silently assume an answer (Principle V; SCOPE GUARD).
  - VAT/tax treatment of refunds is RESOLVED TO OPEN OWNER RULING (no default): this is
    the exact case the SCOPE GUARD names ("VAT/period rules are owner rulings"). The
    example MUST NOT default to "pre-tax" or any other treatment on its own authority --
    `returns-rate-value.md`'s "pre-tax unless policy differs" is knowledge-layer wording,
    not a ruling this feature may adopt. If the chosen source data already makes tax
    handling explicit (e.g. a tax-inclusive/exclusive column), the example cites that
    fact as found; otherwise it raises the gap in `unresolved-questions.md` and stops.
  - Exchange-handling policy gets a Default adopted: IF the chosen source data contains
    no exchange case, the example states exchange handling is out of scope for this
    instance (declining to invent a scenario is the safe default; scoping out is not the
    same as answering the policy question). The underlying business definition (treat an
    exchange as return + new sale, or netted) remains a genuine OPEN owner ruling per the
    seeded domain doc and is never answered by this feature even if a source exchange
    case is later found.
- **FR-009**: The example's `readiness-status.yaml` MUST record every LIVE-gated check
  (Gold Ready's live PK/grain/orphan-FK/reconciliation checks; any live semantic-model
  connection) as `blocked` with a `blocking_reasons[]` entry naming the missing live
  surface when no live database or the Power BI execution adapter (F016) is available,
  per Principle VIII (Static-First/Live-Deferred). It MUST NOT record a fabricated
  `pass` for any such stage.
- **FR-010**: Every named-human approval seam the example reaches (at minimum Mapping
  Ready and Semantic Model Ready, per the always-required seams spec 084 names) MUST be
  left with an EMPTY `approvals[]` entry until a real named human signs it. The agent
  authoring this example MUST NOT self-grant any approval (Principle V).
- **FR-011**: The example MUST NOT emit, anywhere in its artifacts, a numeric
  confidence/health/maturity score or an "N of M" / percentage completeness tally (hard
  rule #9). Readiness is expressed only via the four-status model plus evidence plus
  blocking reasons.
- **FR-012**: If the example's dimensions share a name with a dimension already used by
  an existing worked example (`retail_store_sales`, `demo_sample_orders`), the example
  MUST note the potential cross-star conformance question in its narrative but MUST NOT
  author, edit, or pre-fill `docs/quality/conformed-dimension-map.yaml` itself --
  declaring conformance is a human judgment under spec 087/HR1, not a worked-example
  authoring step.
- **FR-013**: The example's WORKED FIGURES (the synthetic reconciliation figure(s) proving
  US1/FR-007) MUST use the reversible worked-example DEFAULT: return date is treated as
  the returns fact's own transaction date, and the original sale date is carried as a
  reference attribute for lineage only (Principle VI). This default governs the example's
  committed data and narrative arithmetic ONLY -- it MUST NOT be stated or implied as a
  ruling on which axis is the business's operative REPORTING axis for real returns
  data. [NEEDS CLARIFICATION -- RESOLVED TO OPEN OWNER RULING: which date axis (original
  sale date or return date, KPI-domain ambiguity A3) is the business's operative
  reporting axis is a genuine business-policy judgment (Principle V) that no committed
  artifact settles today. It is NOT answered by this spec or by the worked-example
  default above; it is recorded in the example's own `unresolved-questions.md` at build
  time and left for a named-human ruling. The worked-example default may not be cited as
  having resolved it.]
- **FR-014**: The example, its narrative doc, and its mapping artifacts MUST stay a
  GENERIC worked example (Principle VII): no client-specific fact, billing code, or any
  C086-archived specific may appear (per spec 084 FR-007's prohibition, which extends to
  every worked example this repo produces, not only the one it names).
- **FR-015**: All authored artifacts MUST be ASCII, UTF-8 without BOM (use `--` and `->`,
  no glyphs), and MUST use short repo-relative paths respecting the Windows 260-character
  path budget (Principle IX) -- in particular the chosen `<returns-example>` table name
  MUST be short.
- **FR-016**: The example MUST satisfy spec 084's completeness contract
  (`specs/084-worked-example-factory/contracts/worked-example-completeness.md`, confirmed
  authored and committed as of this spec's Clarifications) at the repo-only completeness
  tier, cited explicitly by path rather than re-derived. (The fallback to
  `retail_store_sales`'s own artifact set applies only if a future re-read of this spec
  finds that contract file missing or reverted; it is not the operative path today.)

### Key Entities

- **Returns/refunds fact (the example's subject)**: a NEW fact table, distinct from
  `retail_store_sales`'s sales fact, whose grain includes at least one return/refund
  transaction with a signed quantity/amount and an authoritative transaction-type/reason
  column; the concrete grain, natural key, and source system are a Mapping Ready
  (Stage 2) judgment made during this example's own build, not invented in this spec.
- **Return Value contract**: the example's additive returns-value metric contract,
  citing `skills/retail-kpi-knowledge/contracts/returns-rate-value.md`'s business
  definition and stating additivity "Fully additive" in the AD1-readable vocabulary.
- **Return Rate % contract**: the example's non-additive returns-rate metric contract,
  stating additivity "Non-additive" and never composed by direct SUM of its parents
  (AD1-consistent).
- **Cross-period return**: a return whose transaction date falls in a later reporting
  period than its original sale's date; the case whose correct handling (via the
  documented primary date axis, FR-007/FR-013) is this example's central proof point.
- **`is_return` classification**: the RC8-derived boolean/flag distinguishing a return
  line from a normal sale, sourced from an authoritative transaction-type/reason column,
  never inferred from measure sign alone (FR-004).
- **Worked-example artifact set**: the same artifact set spec 084 names (the five
  mapping-gate artifacts, silver+gold migrations, metric contracts, governed
  PBIP/TMDL model, `design/` set, `handoff/` pack, `readiness-status.yaml`, and this
  narrative doc) -- this feature's concrete output must match that set, not a narrower
  or differently-shaped one.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The example's Return Value contract states additivity "Fully additive" and
  its Return Rate % contract states "Non-additive", each matching
  `skills/retail-kpi-knowledge/contracts/returns-rate-value.md`'s own additivity
  statement, verifiable by reading both contract files side by side.
- **SC-002**: Running `retail check`'s AD1 rule against the repo after this example
  lands produces zero new ERROR findings attributable to this example's metric
  contracts (no illegal SUM-of-a-non-additive composition introduced).
- **SC-003**: The example's narrative doc contains at least one worked reconciliation
  figure, sourced from the example's own committed data, showing a cross-period return
  correctly reflected under the documented primary date axis (no silent drop, no double
  count).
- **SC-004**: The example's `source-map.yaml` derives `is_return` (or its equivalent)
  from an authoritative transaction-type/reason column, never from measure sign alone,
  verifiable by reading the map's derivation for that field.
- **SC-005**: 0 stages in the example's `readiness-status.yaml` show `pass` without a
  cited committed-artifact evidence line, and every live-gated stage shows `blocked`
  with a `blocking_reasons[]` entry naming the missing live surface (no fabricated
  `pass`, no numeric score anywhere in the example's artifacts).
- **SC-006**: 0 named-human approval seams in the example's `readiness-status.yaml` show
  a filled `approvals[]` entry authored by the building agent itself (every approval
  seam starts and stays empty until a real human signs).
- **SC-007**: 0 artifacts produced by this feature reference C086 or any client-specific
  fact, and 0 artifacts author or modify `docs/quality/conformed-dimension-map.yaml`.

## Assumptions

- **`retail_store_sales`'s RC8 = N/A deviation is the confirmed gap.** The worked-example
  README and `retail-store-sales.md` line 116 are read as authoritative evidence that no
  shipped example has modeled a return; this feature exists to fill exactly that gap, not
  a broader or different one.
- **Spec 084's completeness contract is the calibration bar.** Per 084 Assumption A-001,
  the artifact set `retail_store_sales` produced is the completeness bar for any second
  example; this feature targets that same bar rather than inventing a stricter or looser
  one. If 084's `contracts/worked-example-completeness.md` has not yet been authored when
  this feature is built, the artifact set is read directly from `retail-store-sales.md`
  and `mappings/retail_store_sales/` (FR-016).
- **Additivity vocabulary and legality table are owned by spec 068/AD1, consumed here.**
  This feature populates the additivity classification of its own two new metric
  contracts using AD1's existing closed vocabulary and read path (the define-layer prose
  corpus); it introduces no new field, no new vocabulary word, and no new rule.
- **Conformed-dimension declaration is owned by spec 087/HR1, out of scope here.** If a
  dimension name collides with an existing worked example's dimension, this feature
  raises the question in prose; only a named human, via 087's declared mechanism, rules
  it conformed or distinct.
- **RC8 (returns kept, `is_return` derived from the authoritative column, never sign) is
  the applied default, not a deviation, for this example** -- unlike `retail_store_sales`
  where RC8 was N/A. This is the one RC default this feature is specifically built to
  exercise.
- **The primary date axis (sale date vs return date) and exchange-handling policy are
  genuine open business-definition questions** (KPI-domain ambiguities A3 and the
  exchanges note in `skills/retail-kpi-knowledge/domains/returns.md`), not settled by any
  committed artifact today; FR-013 and the Edge Cases record them as resolved-to-OPEN
  owner rulings / Assumption-with-citation rather than a silently invented answer, per
  the SCOPE GUARD (no invented returns POLICY; VAT/period rules are owner rulings). See
  `## Clarifications` for the full resolution of each point.
- **No live database and no Power BI execution adapter (F016) are available during this
  feature's authoring.** Every live-gated check stays `[PENDING LIVE PROFILE]` /
  `blocked`; this mirrors the repo-only completeness tier spec 084 defines and
  Constitution Principle VIII.
- **The example's table name is chosen at build time**, short enough for the Windows
  260-character path budget and distinct from `retail_store_sales` and
  `demo_sample_orders`; this spec does not fix the exact name, only the requirement that
  it be generic and non-client-specific (Principle VII).
- **This feature adds no static rule, no RC default, and no readiness stage** -- it
  consumes the reserved additivity (068/AD1) and conformed-dimension (087/HR1) concepts
  by reference and does not re-implement or re-define either (collision-avoidance
  allocation).

## Clarifications

### Session 2026-07-04

- **Q1 (FR-013): Which date axis governs the example's worked period-total figures, and
  is that the same thing as the business's operative reporting axis?**
  Resolution -- SPLIT, both parts recorded: (a) Default adopted (Principle VI) for the
  example's own synthetic worked figures only -- return date is treated as the returns
  fact's transaction date, with original sale date carried as a reference attribute for
  lineage; this default is reversible and settles nothing about real business intent.
  (b) OPEN owner ruling (Principle V) for which axis is the business's actual operative
  REPORTING axis (KPI-domain ambiguity A3) -- no committed artifact settles this today,
  and the example's `unresolved-questions.md` MUST carry it forward for a named-human
  ruling rather than let the worked-example default be read as having answered it.
  FR touched: FR-013.

- **Q2 (FR-008): What VAT/tax treatment applies to a refund whose original sale carried
  tax?**
  Resolution -- OPEN owner ruling (Principle V; SCOPE GUARD names this explicitly: "VAT
  /period rules are owner rulings"). No default is adopted. The example either cites tax
  handling already explicit in its chosen source data, or raises the gap in
  `unresolved-questions.md`. `returns-rate-value.md`'s "pre-tax unless policy differs" is
  knowledge-layer framing, not a ruling this feature may treat as settled.
  FR touched: FR-008.

- **Q3 (FR-008 / Edge Cases): How should the example handle an exchange (return + new
  sale in one visit) if the question arises during authoring?**
  Resolution -- Default adopted (Principle VI): IF the chosen source data contains no
  exchange case, the example states exchange handling is out of scope for this instance.
  Declining to fabricate a scenario is the safe default; it is distinct from answering
  the underlying policy question. The underlying business definition (return + new sale
  vs netted) remains a genuine OPEN owner ruling per the seeded domain doc regardless of
  whether a source exchange case later surfaces.
  FR touched: FR-008.

- **Q4 (FR-016): Does spec 084's completeness contract
  (`contracts/worked-example-completeness.md`) exist yet, and which completeness bar
  applies?**
  Resolution -- Default adopted, now a factual resolution: the contract is confirmed
  authored and committed at
  `specs/084-worked-example-factory/contracts/worked-example-completeness.md` as of this
  clarification pass. The example targets that contract's repo-only completeness tier,
  cited explicitly by path. The `retail_store_sales`-artifact-set fallback in FR-016
  remains written down only as a contingency should a future re-read find that file
  missing or reverted; it is not the operative path today.
  FR touched: FR-016.

- **Q5 (FR-003): What source data does the example use to exercise negative-quantity /
  additivity behavior on "real committed data"?**
  Resolution -- Default adopted (Principle VI): a small, hand-authored GENERIC synthetic
  dataset committed under `mappings/<returns-example>/`, in the same posture
  `retail_store_sales` used for its own source (not live-fetched, not third-party),
  sized only as large as needed to exercise the US1/US2/US3 acceptance scenarios
  (at least one cross-period return; at least one row usable for the FR-004
  sign-vs-transaction-type discrepancy check).
  FR touched: FR-003.
