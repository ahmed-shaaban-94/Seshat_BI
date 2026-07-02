# Rule I/O Contract: Additivity-Consistency Lineage Rule

This is the behavioral contract of the CHECK RULE (its inputs, outputs, invariants). It is
NOT a metric contract and defines no metric.

## Inputs

- The committed repository text corpus, specifically the define-layer prose metric
  contracts (additivity heading + derives-from heading) and the rendered derivation-lineage
  document, reached by a GENERIC glob (Clarifications Q2, research.md R2).
- A rule context providing the tracked-file list, the repo root, and the test-path
  predicate (the same context AL1 consumes).

## Output

- An iterable of categorical ERROR findings (possibly empty).
- Each finding names an offending metric + the specific illegal or absent/ambiguous
  composition and its committed locator.

## Trigger conditions (ERROR)

1. A stated composition matches an ILLEGAL row of the closed legality table (e.g. a
   non-additive child composed by direct SUM; a semi-additive component in a plain-SUM
   parent).
2. A metric that participates in a committed derivation edge has an
   `ABSENT_OR_AMBIGUOUS` additivity class (FR-004 -- refused, never inferred).
3. A tracked source artifact in the corpus is unreadable/unparseable (fail-loud, names the
   path).

## Non-trigger conditions (pass, no finding)

- A non-additive child recomputed base-over-base from fully-additive parents (LEGAL).
- A metric with a valid class but no derivation edges (nothing to compose).
- An empty corpus (no contracts on disk).
- The generic template path and any test-fixture path (exempt).

## Invariants (MUST hold for every run)

- **No execution**: never runs DAX, never opens a connection, never renders a visual.
- **Core stays stdlib-only at module scope**: any non-stdlib parser is imported lazily
  inside the handler.
- **Categorical only**: severity is always ERROR; no numeric score, confidence, or
  threshold is ever emitted.
- **No inference**: an absent/ambiguous class ERRORs; a class is never defaulted or guessed.
- **No resolution**: never picks a winner, invents a derivation edge, or re-classifies a
  metric (Principle V).
- **Generic**: no worked-example metric names, ids, or paths; the closed table is generic
  retail arithmetic.
- **Off-spine**: advances no readiness stage, grants no approval.

## Wiring contract

- Registered via the rule-registry decorator with a new unique id.
- Present in the registry import block + export list, the expected-rule-id set, the rules
  manifest, and the severity-posture manifest.
- The authoritative rule count advances by exactly one (current + 1).
