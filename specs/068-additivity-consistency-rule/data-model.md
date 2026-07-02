# Phase 1 Data Model: Additivity-Consistency Lineage Rule

No persisted schema and no new contract field are introduced. These are the in-memory
shapes the rule builds while reading committed text. All are read-only projections of
committed facts; the rule writes none of them back.

## AdditivityClass (closed enum)

One of exactly:

- `FULLY_ADDITIVE`   (committed word: "Fully additive")
- `SEMI_ADDITIVE`    (committed word: "Semi-additive")
- `NON_ADDITIVE`     (committed word: "Non-additive")
- `ABSENT_OR_AMBIGUOUS` (no recognized word, or more than one conflicting word)

Rule: the class is assigned ONLY by matching the exact committed word in the closed
vocabulary. `ABSENT_OR_AMBIGUOUS` is never treated as a real class in the legality table;
it triggers an ERROR (FR-004, User Story 2). The rule NEVER infers a real class.

## ClassificationRecord

- `metric`: the committed metric identity as written in the define-layer corpus (an
  identifier the corpus already uses; the rule reads it, it does not mint one).
- `klass`: an `AdditivityClass`.
- `source_locator`: the committed path (+ heading) the class was read from, for the finding.

## DerivationEdge

- `child`: the deriving metric's committed identity.
- `parents`: the list of metrics the child derives from, as stated in committed prose.
- `composition_kind`: how the child is composed, as stated in the committed source, limited
  to what the corpus explicitly says (e.g. a direct-SUM composition vs a base-over-base
  recompute). If the composition kind is not explicitly stated, it is treated as unknown
  and does NOT produce an inferred verdict (Principle V) -- only explicitly stated illegal
  compositions ERROR.
- `source_locator`: the committed path (+ heading / lineage row) the edge was read from.

## LegalityTable (fixed, closed, generic)

A pure lookup: `(parent_class, child_class, composition_kind) -> LEGAL | ILLEGAL`.

Seeded from committed generic knowledge (see research.md R3). The exact matrix is FR-012,
recorded OPEN for owner ratification. Illustrative rows:

- `(FULLY_ADDITIVE, NON_ADDITIVE, base_over_base_recompute) -> LEGAL`
- `(*, NON_ADDITIVE, direct_sum) -> ILLEGAL`   (a ratio/percentage/average summed)
- `(*, SEMI_ADDITIVE, plain_sum_parent) -> ILLEGAL`  (semi-additive poisoning a plain SUM)

The table contains no metric names, no worked-example ids, no paths -- generic classes only.

## Finding (existing model, reused)

- `rule_id`: the new rule's id.
- `severity`: always `ERROR` (categorical; no score/band -- FR-002).
- `message`: names the offending metric and the specific illegal or absent/ambiguous
  composition; states that a human must resolve it (never the rule).
- `locator`: the `source_locator` of the offending metric/edge.

## Invariants

- Read-only: no source artifact is mutated.
- No execution: no DAX, no connection, no visual (FR-003).
- No inference: an absent/ambiguous class ERRORs; a class is never defaulted (FR-004).
- No resolution: the rule never picks a winner, invents an edge, or re-classifies (FR-005).
- Categorical only: ERROR or pass; never a number (FR-002).
