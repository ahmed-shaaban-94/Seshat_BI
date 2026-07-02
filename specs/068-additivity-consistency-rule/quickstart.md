# Quickstart: Additivity-Consistency Lineage Rule

## Run the rule as part of the retail check

The rule runs automatically inside the existing retail governance check (the same check
already wired into the pre-commit path and CI). No new command is introduced. On the
current committed corpus it should produce zero findings (SC-001).

## Confirm the rule fires on an illegal composition

1. Add a test fixture pair of define-layer contracts where a parent metric composes a
   non-additive (ratio) child by direct SUM.
2. Run the unit test suite (unit-marked): the rule-behavior test asserts exactly one ERROR
   finding naming the offending metric (SC-002).
3. Repair the fixture (recompute base-over-base) and confirm zero findings.

## Confirm the rule refuses an absent/ambiguous class

1. Add a fixture where a metric on a derivation edge has no recognizable additivity word.
2. Run the unit test: the rule ERRORs that the class is absent/ambiguous and emits no
   inferred composition verdict (SC-003, FR-004).

## Confirm the wiring / count

1. Run the rule-wiring unit test: actual registered rule ids equal the expected set
   (including the new id) and the manifest count equals that set's length (SC-004).

## What the rule never does

- Never runs DAX, opens a connection, or renders a visual.
- Never emits a numeric score, confidence, or threshold.
- Never infers a missing class, invents an edge, or re-classifies a metric (a human owner
  resolves every finding).
