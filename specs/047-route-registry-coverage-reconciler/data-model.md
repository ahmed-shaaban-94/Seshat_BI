# Phase 1 Data Model: Route-Registry Coverage Reconciler (A3)

A3 is a static rule; its "data model" is the abstract values it derives in memory
during one gate run. Nothing is persisted; both source documents are read-only.

## Entities

### Map id set

- **What it is**: the set of route id tokens extracted from the knowledge map's
  "Route by task" table id column.
- **Derivation**: scan `docs/knowledge-map.md`; locate the `## Route by task`
  section; read its GFM pipe-table data rows (skipping header + separator); for each
  row take the first cell's leading token, strip a trailing period; stop at the next
  `## ` heading.
- **Type**: `set[str]` (e.g. `{"1", "2", ..., "12a", "17d"}`).
- **Validation**: the section MUST be locatable and yield at least one id; otherwise
  the input is unreadable -> ERROR (never an empty-set vacuous pass).

### Manifest id set

- **What it is**: the set of route id tokens declared in `docs/routing/routes.yaml`.
- **Derivation**: lazy `import yaml`; `safe_load`; require a mapping with a `routes`
  list; collect each route's `id` as a string.
- **Type**: `set[str]`.
- **Validation**: manifest MUST be tracked, valid YAML, and the expected
  `{routes: [...]}` shape; otherwise -> ERROR (fail loud).

### Difference (the comparison result)

- **map_only** = map_ids - manifest_ids -- ids in the map with no manifest route.
- **manifest_only** = manifest_ids - map_ids -- manifest routes with no map row.
- **Bijection holds** iff both are empty (then zero findings).

### Finding (reused from core.py, UNCHANGED)

- Fields: `rule_id` (= "A3"), `severity` (= ERROR), `message`, `locator`.
- One finding per drifting id (or per unreadable-input condition).
- `locator` points at the responsible document (the map section for a map-only id,
  the manifest for a manifest-only id; the relevant file for an unreadable input).
- `message` is generic: it names the id and the difference direction, never any
  domain-specific route value.

## Relationships

```text
docs/knowledge-map.md ("Route by task")  --extract-->  Map id set     --+
                                                                        |--> Difference --> Finding[]
docs/routing/routes.yaml                  --extract-->  Manifest id set --+
```

## State transitions

None. A3 is a pure function: `(RuleContext) -> Iterable[Finding]`. No mutation, no
persistence, no lifecycle.

## Invariants

- INV-1: On a clean main checkout, map id set == manifest id set, so A3 yields `[]`.
- INV-2: A3 never mutates either source document.
- INV-3: A3 never returns `[]` when an input was unreadable (no vacuous green).
- INV-4: Every emitted message is generic (no C086/pharmacy specifics).
