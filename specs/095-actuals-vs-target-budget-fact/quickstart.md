# Quickstart: Actuals-vs-Target (Budget) Fact + Variance Readiness

**Feature**: `specs/095-actuals-vs-target-budget-fact/` | **Phase**: 1 (design)

This walks how an analyst or agent EXERCISES this feature's three
deliverables once they are authored -- it is a usage guide for the pattern +
contract shape + second worked example, not a build guide for a real target
fact (that is a separate, later feature; see step 5).

## Prerequisite

An actuals star already exists at Gold Ready or later for the table you want
to eventually compare against a plan. (For the abstract pattern in step 1,
even this is optional -- the pattern generalizes. For a REAL build, see step
5.)

## Step 1 -- Read the modelling pattern

Open `docs/patterns/target-budget-fact.md`. Confirm, with zero external
lookups beyond `docs/decisions/0002-retail-cleaning-defaults.md` and the
existing actuals-star pattern it cites, that you can answer:

- Which dimension keys must a target/budget fact reuse from the actuals star
  it will be compared against? (Answer: the SAME conformed keys -- RC14.)
- Is the target fact's grain asserted by the pattern, or is it yours to
  decide? (Answer: yours -- it is marked
  `[NEEDS CLARIFICATION: target-fact grain is owner-supplied per table]`.)
- How is the variance percentage computed when actuals and targets are
  rolled up? (Answer: aggregate each side SEPARATELY at the comparison grain,
  then recompute the ratio -- never average two pre-computed percentages;
  cited from `skills/retail-kpi-knowledge/domains/targets-and-budgets.md`.)
- What happens when a dimension member has no corresponding target? (Answer:
  it MUST be flagged, never defaulted to 0% or silently dropped.)

If any of these answers is not obvious from the document alone, the pattern
document has a gap (see SC-001) -- stop and treat that as a defect in the
pattern doc, not something to guess past.

## Step 2 -- Draft a variance metric contract from the contract shape

Open `templates/metric-contract-shape.variance-vs-target.yaml` side-by-side
with `templates/metric-contract.yaml`. Confirm every field name in the shape
matches the template exactly (SC-005) -- if you find a field in the shape that
is not in the template, that is a defect (the shape must never fork the
template).

Using the shape as your starting point, draft your own table's REAL variance
contract (e.g. under `mappings/<your-table>/metrics/<VarianceMetricName>.yaml`,
once a real target fact exists for that table -- see step 5). While drafting:

- Fill `binds_to.gold_table` with your ACTUALS gold table (the shape's
  resolution of the two-table tension: the target table's identity goes in
  `formula_intent`, flagged for human review, never forced into a second
  `binds_to` key).
- Copy the `ambiguities[]` entry pattern for the missing-target case into your
  contract, adapted to your table's real dimension member.
- Leave the RAG-threshold marker in place (`[NEEDS CLARIFICATION: RAG
  thresholds are owner-supplied business policy, not a kit default]`) until a
  named owner supplies one. Your contract's `readiness.status` stays `blocked`
  with that marker recorded as a `blocking_reasons[]` entry until they do.

## Step 3 -- Consult the second worked example for a concrete-but-abstract walkthrough

Open `docs/worked-examples/target-budget-pattern-retail-store-sales.md`. It
shows the pattern applied to `retail_store_sales`'s existing, committed
conformed dimensions (`dim_customer_rss`, `dim_product_rss`,
`dim_payment_method_rss`, `dim_location_rss`, `dim_date_rss`, from
`0004_create_gold_retail_store_sales_star.sql`) -- with ZERO target values,
variance figures, or RAG assignments anywhere in it. Use it to confirm your
own table's draft (step 2) is reading dimension names the same way this
section does, not inventing a shortcut.

Confirm while reading: the section states plainly that `retail_store_sales`
has NO target fact today, and that building one would restart at Mapping
Ready for a NEW source -- it never implies the actuals star's Gold Ready /
Dashboard Ready status extends to an unbuilt target fact (FR-013). If you are
tempted to treat this section as evidence of a `retail_store_sales` target
fact's readiness, stop -- that is explicitly not what this document is
(Edge Cases).

## Step 4 -- STOP at every owner judgment call

Before proceeding past this point for a REAL table, the following remain
OPEN and this feature's artifacts will not resolve them for you (Principle
V -- the agent, and this feature, MUST NOT decide these alone):

| Open item | Who decides | Where it gets recorded |
|---|---|---|
| The target fact's actual grain | The data/finance owner | That table's own `mappings/<table>/unresolved-questions.md`, once a real target fact is being onboarded |
| RAG (red/amber/green) numeric thresholds | Finance/Sales owner (per `targets-and-budgets.md`'s "Owner" section) | The filled `metric-contract.yaml`-shaped contract's `evidence[]`, once supplied |
| Whether a version/as-of dimension is needed for reforecasts | The data/finance owner | That table's own `assumptions.md` / `unresolved-questions.md` |

If any of these is unanswered, do NOT invent a value, do NOT mark the
contract `pass`, and do NOT self-grant an approval. Raise the entry and stop
-- exactly the same discipline `source-mapping` already enforces for grain
and PII.

## Step 5 -- (Later, separate feature) Build a real target/budget fact

This feature's artifacts are consumed, not executed, by a future real build.
That future work is NOT scheduled or numbered by this spec (spec.md
Assumptions) and walks the EXISTING sequence, unchanged:

1. `source-mapping` -- profile the real target/budget source (a finance file,
   a budget spreadsheet, whatever the owner hands over), decide grain/PK/PII,
   fill the five mapping artifacts, clear the mapping gate.
2. `retail-build-warehouse` -- author the silver + gold migration SQL for the
   target fact, conformed to the SAME dimension keys as the actuals star
   (per this feature's pattern document), then STOP before executing.
3. `retail-validate` -- once the migrations are applied to a live database,
   run the live checks (PK uniqueness, 0 orphan FKs, penny-exact
   reconciliation) against the materialized target fact.
4. Fill a REAL variance metric contract (per this feature's contract shape),
   supply the grain/RAG/versioning answers from step 4 above, and route it
   through Semantic Model Ready like any other metric contract.

None of these four steps is performed by this feature. This quickstart only
describes how they would eventually consume today's pattern + shape + second
example.

## What "done" looks like for THIS feature (not for a future real build)

- An analyst can read `docs/patterns/target-budget-fact.md` alone and state
  every structural default it makes for them vs. every decision left theirs
  (SC-001).
- Zero authored artifact in this feature contains a fabricated target value,
  variance percentage, or RAG color/threshold (SC-002).
- Zero authored artifact adds a new readiness-stage name, four-status gate, or
  `retail check` rule ID (SC-003).
- Zero authored artifact modifies `docs/worked-examples/retail-store-sales.md`,
  `templates/metric-contract.yaml`, or
  `skills/retail-kpi-knowledge/domains/targets-and-budgets.md` (SC-004).
- The contract shape's field set matches `templates/metric-contract.yaml`'s
  field set with 0 new/renamed fields (SC-005).
- The second worked-example section references only names already present in
  `0004_create_gold_retail_store_sales_star.sql` or `retail-store-sales.md`
  (SC-006).
- Every `[NEEDS CLARIFICATION]` marker this feature leaves open (grain, RAG
  thresholds, versioning) is locatable in under one pass of the pattern
  document and the contract shape, each naming exactly what a future owner
  must supply (SC-007).
