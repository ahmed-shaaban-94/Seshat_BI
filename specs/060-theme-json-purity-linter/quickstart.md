# Quickstart: Theme JSON Purity Linter

How a developer builds, tests, and runs this rule after the spec is ratified.

## Prerequisites

- The retail governance framework is already present (`src/retail/registry.py`,
  `src/retail/core`). No new dependency is added; stdlib only.
- The human ruling on the forbidden-key literal vocabulary (spec ## Clarifications
  OPEN items) has been recorded. Wiring the golden records is gated on it.

## Build steps (summary -- full ordering in tasks.md)

1. Add fixture theme files under the test-fixture exemption path: one clean
   (allowed-only), one with a single forbidden key, one with two forbidden keys,
   one with a nested forbidden key, one malformed (invalid JSON), one with a value
   that equals a forbidden word.
2. Write the failing unit tests (`tests/unit/test_design_theme.py`) encoding the
   behavioral contract rows C1-C11.
3. Implement `src/retail/rules/design_theme.py`: a `@register`-decorated function
   that discovers theme files generically, parses each, walks keys against the
   generic forbidden-key vocabulary, and emits ERROR findings with
   `file#/pointer` locators. Reuse the pbir.py pattern and `is_test_path`.
4. Wire the five governance places:
   - add `design_theme` to the import tuple + `__all__` in `rules/__init__.py`;
   - add the fresh rule id to `EXPECTED_RULE_IDS` in
     `tests/unit/test_rules_wiring.py`;
   - regenerate `docs/rules/rules-manifest.json`;
   - regenerate `docs/rules/severity-posture.json`.
5. Run the gate.

## How to run

- Unit tests: `pytest -m unit`
- Full governance gate: `retail check`
- Regenerate manifest / severity golden records: the existing `retail manifest`
  (and the severity-posture regeneration) commands.

## Acceptance (maps to Success Criteria)

- A fixture with a forbidden key fails the check with an ERROR (SC-001).
- The clean fixture and the current committed starter theme produce zero findings
  (SC-002, SC-003).
- A two-forbidden-key fixture yields exactly two findings (SC-004).
- Adding a second theme file is scanned with no code change (SC-005).
- The rule id appears in the registry + all golden records and the wiring test
  passes (SC-006).
