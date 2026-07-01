# Phase 1 Data Model: Wiring Meta-Gate

This feature persists NO new data. The "entities" below are conceptual surfaces
the meta-gate reads and compares in-process; there is no new schema, table, or
golden file.

## Entity: Live-Registry Snapshot (ground truth)

- **Source**: `retail.registry.all_rules()` after a deterministic clear-and-reload
  of the rules package.
- **Shape**: an ordered tuple of registered rules; each carries exactly `id` (str)
  and `title` (str). No severity field.
- **Derived views used by the meta-gate**:
  - `live_ids`: the set of `id` values.
  - `live_id_title`: the `{id: title}` mapping.
  - `live_count`: `len(all_rules())` (for the duplicate-id guard).
- **Invariants**: non-empty; `len(live_ids) == live_count` (no duplicate ids).

## Entity: Wiring Place

One of the five consistency surfaces the meta-gate proves consistent with the
ground truth (and, for place 2, internally consistent):

1. **Rule modules** -- the on-disk submodule set of the rules package
   (introspected, excluding the package initializer).
2. **Package import list + exports** -- the side-effecting import list and the
   public export list (`__all__`) of the rules package. Place 2 has THREE views
   that must be equal: import-list names, export-list names, on-disk submodule set.
3. **Expected-rule-id set** -- the hand-maintained id source of truth (the
   existing test constant), a set of rule-id strings.
4. **Golden manifest** -- the committed `{id, title}` inventory JSON; the
   meta-gate reads its id set (and titles) statically.
5. **Golden posture record** -- the committed severity-posture JSON; the meta-gate
   reads its `registered` section's id set and its non-registered surface keys
   statically.

## Entity: Non-Registered-Surface Exemption List

- **Shape**: an explicit constant set of surface keys that legitimately carry no
  rule id (per ADR-0007). Starts with exactly the one known L3 surface key.
- **Rule**: a non-registered surface key present in the posture golden is allowed
  ONLY if it is on this list; any other non-registered key fails closed.

## Entity: Lockstep Report (failure output)

- **Not persisted.** Produced only on failure as the test's assertion message.
- **Content**: which wiring place disagrees, and the specific offending
  symbol/id, plus the direction (missing here / extra there).
- **Requirement**: unambiguous enough that the fix location is identifiable
  without opening source (SC-005).

## Cross-Check Relationships (the lockstep)

| Check | Left (ground truth) | Right (place) | Fail-closed when |
|-------|---------------------|---------------|------------------|
| C1 package symmetry | on-disk submodules | import list AND `__all__` | any of the three sets differ |
| C2 id source of truth | `live_ids` | expected-rule-id set | sets differ (missing/unexpected) |
| C3 manifest | `live_id_title` | manifest golden id/title | any id added/removed/retitled |
| C4 posture | `live_ids` | posture golden `registered` ids | any live id absent from record |
| C5 exemption | posture non-registered keys | exemption list | a non-registered key not exempted |
| C6 vacuity | -- | -- | zero submodules or zero rules |
| C7 duplicates | `live_count` | `len(live_ids)` | counts differ |

## Validation Rules

- All set comparisons normalize on content only (order-independent).
- Any JSON read uses UTF-8 without BOM; comparisons are on parsed values, not raw
  bytes, so line-ending/BOM cosmetics cannot cause a false pass or fail.
- All filesystem paths are built relative to the repo root discovered from the
  package location; no absolute-path assumption that breaks on a deep checkout.
