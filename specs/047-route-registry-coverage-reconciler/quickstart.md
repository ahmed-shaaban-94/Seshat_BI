# Quickstart: Route-Registry Coverage Reconciler (A3)

Audience: the implementer picking up the ratified spec. This is the build at a glance.

## What you are building

A3: a static `retail check` rule that fails the gate when the knowledge map's
"Route by task" id set and the routing manifest's id set differ in either
direction. Mirror the shipped A1 rule's shape.

## Files

| File | Action |
|------|--------|
| `src/retail/rules/routes_coverage.py` | NEW -- the A3 rule |
| `src/retail/rules/__init__.py` | EDIT -- add `routes_coverage` to import tuple + `__all__` |
| `tests/unit/test_routes_coverage.py` | NEW -- TDD incl. live map-vs-manifest guard |
| `tests/unit/test_rules_wiring.py` | EDIT -- add `"A3"` to `EXPECTED_RULE_IDS` (33 -> 34) |
| `docs/roadmap/roadmap.md` | EDIT -- ledger row: A3 shipped, rule count 33 -> 34 |

Read `src/retail/rules/routes.py` and `tests/unit/test_routes.py` first -- A3
copies their shape (register, ERROR, lazy yaml, fail-loud, live guard).

## TDD order (RED -> GREEN)

1. Write `test_routes_coverage.py` cases FIRST (they fail): bijection-holds ->
   `[]`; map-only id -> 1 ERROR; manifest-only id -> 1 ERROR; missing manifest ->
   ERROR; malformed manifest -> ERROR; map section not locatable -> ERROR; the
   live map-vs-manifest guard -> `[]`.
2. Add `"A3"` to `EXPECTED_RULE_IDS` and the `__init__.py` wiring (RED: rule
   missing).
3. Implement `routes_coverage.py` until all tests pass (GREEN).
4. Add the roadmap ledger row.

## Verify (the gate set)

```bash
ruff check .
pytest -m unit
retail check          # expect exit 0 and rule count 34
retail semantic-check
```

`retail check` must exit 0 (the bijection holds on main, so A3 emits zero
findings) and report 34 rules.

## Guardrails

- stdlib-only core import path; `import yaml` lazily inside the handler; NO
  markdown dependency (hand-roll the table scan).
- Extract ONLY the "Route by task" section; stop at the next `## ` heading.
- Fail loud on missing/malformed inputs -- never return `[]` on an unreadable input.
- Generic messages and fixtures only -- no C086/pharmacy route values.
- The severity posture, bijection scope, and roadmap-stage claim are RESERVED for
  human ratification (spec ## Clarifications). Build on the advisor defaults
  (ERROR-both, "Route by task" only, no-stage) unless a human ruling says otherwise.
