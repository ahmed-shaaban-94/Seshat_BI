# Contract: A3 Route-Registry Coverage Reconciler

A3 is a registered static rule consumed by `retail check`. Its contract is the
existing rule interface; this document pins the A3-specific behavior.

## Interface (reused, UNCHANGED)

- **Registration**: `@register("A3", "<title>")` on the handler function, fired by
  importing the rule submodule (side-effecting import via `src/retail/rules/__init__.py`).
- **Signature**: `check_route_coverage(ctx: RuleContext) -> Iterable[Finding]`.
- **Input**: `RuleContext(repo_root: Path, tracked_files: tuple[str, ...], ...)`.
- **Output**: an iterable of `Finding(rule_id, severity, message, locator)`.
- **Purity**: no side effects, no execution, no network, no DB, no document writes.

## Inputs read (read-only)

- `docs/knowledge-map.md` -- the "Route by task" table id column.
- `docs/routing/routes.yaml` -- the manifest route ids (lazy `import yaml`).

Both MUST be in `ctx.tracked_files` and resolvable under `ctx.repo_root`.

## Behavior contract

| # | Condition | Output |
|---|-----------|--------|
| C1 | map id set == manifest id set | `[]` (zero findings) |
| C2 | id in map, not in manifest | one ERROR naming the id, "map ... not in manifest" |
| C3 | id in manifest, not in map | one ERROR naming the id, "manifest ... not in map" |
| C4 | manifest missing / untracked | one ERROR naming the manifest as unreadable |
| C5 | manifest invalid YAML / wrong shape | one ERROR describing the malformed manifest |
| C6 | map file missing / "Route by task" table not locatable | one ERROR naming the map source as unreadable |

All findings carry `rule_id == "A3"` and `severity == Severity.ERROR` (advisor
default; pending human ratification of the severity posture -- see spec
## Clarifications). The `locator` points at the responsible document.

## Generic-message contract (Principle VII)

Every message references ONLY abstract route ids (e.g. "1", "12a", "17d") and
document structure. NO domain-specific route value, table name, billing code,
segment, or PII column may appear -- in code or in test fixtures.

## Scope contract (Principle VIII)

- Core import path stays stdlib-only; `yaml` is imported lazily inside the handler.
- The map-table extractor is hand-rolled stdlib; NO markdown-parsing dependency.
- The extractor reads ONLY the "Route by task" section (stops at the next `## `
  heading); other pipe tables in the map MUST NOT contribute ids.
- Never returns `[]` on an unreadable input (no vacuous green).

## Wiring contract

- "A3" MUST be added to `EXPECTED_RULE_IDS` in `tests/unit/test_rules_wiring.py`
  (33 -> 34) in the same change.
- `routes_coverage` MUST be added to the import tuple and `__all__` in
  `src/retail/rules/__init__.py`.
