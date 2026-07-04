# Data Model: Cross-Star Conformed-Dimension Readiness Gate

Phase 1 output. Defines the shapes HR1 reads and produces. Generic (Principle
VII): `dim_product` / `dim_store` / `dim_date` and any table id below are
ILLUSTRATIONS ONLY, never required names. No worked-example (C086/pharmacy)
specifics are inlined.

## Entities (from spec.md Key Entities)

### Star

One fact + its dimensions, as recorded in a single table's
`mappings/<table>/source-map.yaml`. Not a new shape -- this is the
EXISTING `gold_star` block the source-mapping gate already owns; HR1 only
reads it.

- **Identity**: `meta.table_id` (rich form) or `source_id` (compact form,
  e.g. `demo_sample_orders`) -- either serves as the star's identity string
  for Findings and for the manifest's `stars:` list.
- **Is-a-star test**: a table IS a star if and only if its `source-map.yaml`
  carries a `gold_star.fact` key (either the rich sub-mapping form
  `gold_star.fact.name` or the compact string form `gold_star.fact`). A
  table with no `gold_star.fact` is not a star and is excluded from every
  HR1 computation.
- **Multi-fact trigger** (FR-007, US3): the "more than one star" condition
  that engages HR1 is `count(tables where is-a-star) >= 2`, counted across
  every table under `mappings/*/source-map.yaml`.

### GoldDimension

One conformable unit HR1 compares across stars: a single dimension's
recorded shape as declared in ONE star's `source-map.yaml`.

| Field | Source (rich form) | Source (compact form) | Present on both forms? |
|---|---|---|---|
| `name` | `gold_star.dimensions[].name` | `gold_star.dimensions[].name` | YES -- always present; this is the join key for cross-star name-collision detection (FR-006) |
| `surrogate_key` | `gold_star.dimensions[].surrogate_key` | absent | NO -- compact form has no surrogate-key field |
| `attributes` | `gold_star.dimensions[].attributes[]` (list of attribute name strings) | `gold_star.dimensions[].attributes[]` (list of attribute name strings) | YES -- present on both, but compact-form entries carry no per-attribute type join |
| `attribute_silver_type(attr)` | resolved via `columns[]` entries whose `gold_placement == "dim:<name>.<attr>"`, reading that entry's `silver_type` | absent (compact form has no top-level `columns[]` block to join against) | NO -- the type limb is a no-op wherever this join is unavailable |
| `is_date_dim` | true if this entry's `name` matches the table's `gold_star.date_dimension.name`, OR if the entry is itself the sole date-shaped record when no standalone `date_dimension:` block exists | same test | derived, not a raw field |

**Date-dimension recognition (C1, FR-004)**: a table records its date
dimension in ONE of two committed forms and HR1 MUST recognize both:

1. **Standalone block**: `gold_star.date_dimension` (a sibling of
   `gold_star.dimensions[]`, not an entry inside it) -- carries `name`,
   `surrogate_key`, `method`, `contiguous`, `span`. When present, HR1
   treats this block as ONE additional `GoldDimension` for conformance
   purposes (grain = the date grain; key = `surrogate_key`; type is N/A --
   a date dim's grain IS its type). RC15's contiguity is Gold Ready's job,
   not re-checked by HR1.
2. **Inline entry**: an entry inside `gold_star.dimensions[]` that carries
   `built_from` instead of (or in addition to) `surrogate_key` (the compact
   form's shape, e.g. `demo_sample_orders`'s `dim_date` with
   `built_from: order_date`). HR1 treats this exactly as any other
   `GoldDimension` entry inside `dimensions[]` -- no special-casing needed
   because it is already inside the scanned list.

**Explicitly OUT of the GoldDimension set (C1)**: `gold_star.
degenerate_dimensions[]` entries. These are per-star transaction ids on the
fact (RC14), never shared lookup dimensions, and are structurally excluded
from every HR1 scan -- HR1 never reads this key for conformance purposes
(it may still exist in the file; HR1 simply does not traverse into it).

**Graceful degradation rule (research.md, load-bearing)**: because the two
committed instances use materially different schema shapes (rich vs.
compact), HR1 MUST treat every field above as OPTIONAL per star and MUST
NEVER raise/crash on a missing `surrogate_key` or an unresolvable
`attribute_silver_type`. The comparison rule is: **compare only the fields
present on BOTH sides of a declared-conformed pair; a field absent on
either side is silently excluded from that pair's comparison, never treated
as a divergence and never treated as a crash.** (A field present on one
side and absent on the other is not itself a FR-005 divergence -- there is
nothing to compare.)

### ConformedDeclaration (the manifest entry shape)

One entry in the NEW human-authored file
`docs/quality/conformed-dimension-map.yaml` (clarify C2: mirrors the SF1
`shared-spine.yaml` shape -- top-level mapping, enum value, fail-closed on
an unrecognized value).

```yaml
# docs/quality/conformed-dimension-map.yaml (SHAPE -- illustrative names only)
dimensions:
  <dimension_name>:               # e.g. dim_product (bare gold_star.dimensions[].name)
    status: conformed             # conformed | distinct -- the ONLY two valid values
    stars:                        # the set of table ids this ruling covers
      - <table_id_a>               # e.g. star_a (meta.table_id or source_id)
      - <table_id_b>               # e.g. star_b
    # note: (optional human commentary; HR1 never reads or requires this key)
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `dimensions` | mapping | yes (top-level key) | keys are bare gold dimension names (matches `GoldDimension.name`, not a schema-qualified variant -- see Honesty limitation below) |
| `<name>.status` | string enum | yes | MUST be exactly `conformed` or `distinct`; any other value (including case variants, typos, or a missing key) is a fail-closed ERROR naming the offending entry (FR-010) |
| `<name>.stars` | list of strings | yes | each entry MUST resolve to a table whose `source-map.yaml` exists and parses; a listed table that cannot be found/parsed is the FR-010 malformed case (ERROR); a listed table that parses but does not carry the named dimension is the FR-009/C5 stale case (WARNING) |

**Human-authored, never machine-generated (Principle V)**: this file's
CONTENT (which names are declared, and as `conformed` vs `distinct`) is
authored by a named human. The agent may scaffold only the empty SHAPE
(`dimensions: {}`) at the owner's explicit instruction when there is
nothing yet to adjudicate (see research.md "Landing precondition") --
it never rules an actual collision.

### ConformanceFinding

Not a new class -- this feature emits the EXISTING `Finding` dataclass
(`src/retail/core.py`, unchanged) with `rule_id = "HR1"`. No new Finding
schema is introduced; the shape below documents HR1's USAGE of the existing
fields, not a new type.

| Field | HR1 usage |
|---|---|
| `rule_id` | always the literal string `"HR1"` |
| `severity` | `Severity.ERROR` for: a declared-conformed divergence (grain/key/type), an undeclared cross-star name collision, a missing/unparseable manifest with 2+ stars, or a malformed manifest entry. `Severity.WARNING` for: a stale declared-conformed/distinct entry (fewer than 2 surviving stars, or a listed star that parses but lacks the dimension), or a moot `distinct` entry (stars have become identical in shape). |
| `message` | categorical prose naming the dimension, the disagreeing/colliding stars, and WHAT diverged (which of grain/key/type, and the conflicting values) -- NEVER a number expressing a score, ratio, or "N of M" tally (hard rule #9, FR-012) |
| `locator` | a repo-relative pointer, e.g. `docs/quality/conformed-dimension-map.yaml:<dimension_name>` for a manifest-level finding, or a compound locator naming the offending `source-map.yaml` paths for a shape divergence (mirrors SF1's `f"{SPINE_REL}:{basename}"` locator convention) |

## Finding taxonomy (exhaustive; matches spec.md Edge Cases + FR-005..FR-010)

| Case | Trigger | Severity | FR / Edge Case |
|---|---|---|---|
| Declared-conformed divergence (key) | `conformed` entry; two+ named stars' `surrogate_key` for that dim differ | ERROR | FR-005 |
| Declared-conformed divergence (type) | `conformed` entry; a Kimball conformed-subset attribute's `silver_type` differs across named stars | ERROR | FR-005, C4 |
| Declared-conformed divergence (grain) | `[PENDING SCHEMA PREREQUISITE]` -- not implemented this feature; see research.md C3 | N/A (deferred) | FR-005 (grain limb), C3 |
| Undeclared cross-star collision | same dimension `name` in 2+ stars' `gold_star.dimensions[]`, no manifest entry | ERROR | FR-006, US2 |
| Missing/unparseable manifest | `docs/quality/conformed-dimension-map.yaml` absent or fails to parse, AND 2+ stars exist | ERROR | FR-010 |
| Malformed manifest entry (bad status) | a `status` value that is not exactly `conformed`/`distinct` | ERROR | FR-010 |
| Malformed manifest entry (unresolvable star) | a listed `stars[]` table id whose `source-map.yaml` is missing/unparseable | ERROR | FR-010 |
| Stale declared entry (fewer than 2 surviving stars) | a declared dimension (conformed or distinct) whose named stars no longer number >= 2 with that dimension present | WARNING | FR-009 |
| Stale declared entry (named star lacks the dimension) | a listed star parses fine but its `gold_star` shape does not carry the declared dimension name | WARNING | FR-009, C5 |
| Moot `distinct` entry | a `distinct` entry whose stars have become identical in shape (key + type + -- when implemented -- grain) | WARNING | Edge Cases (moot-distinct) |
| Zero or one star | fewer than 2 tables carry `gold_star.fact` | no Finding (no-op) | FR-007, US3 |
| `distinct`-declared pair that differs | a `distinct` entry; stars disagree in shape | no Finding | FR-008 |
| Single-star-only dimension name | a name appears in exactly one star | no Finding | US2 scenario 2 |

## Relationships

```text
mappings/<table>/source-map.yaml (N files, one per table)
        |
        |  gold_star.fact present?  --no--> excluded from HR1 entirely
        |  yes
        v
      Star (table_id, [GoldDimension, ...])
        |
        |  group all Stars' GoldDimensions by GoldDimension.name
        v
      { dimension_name: [ (table_id, GoldDimension), ... ] }
        |
        |  filter to groups with >= 2 entries (a "collision")
        v
      docs/quality/conformed-dimension-map.yaml  --read-only-->  ConformedDeclaration lookup by name
        |
        |  for each collision: declared? compare per Finding taxonomy above
        |                       undeclared? ERROR (FR-006)
        v
      list[Finding(rule_id="HR1", ...)]   <-- HR1's return value; no side effects, no writes
```

## Non-goals for this data model (YAGNI, matches spec.md Assumptions)

- No live/materialized-data shape (that is a future `retail validate`
  concern).
- No numeric field anywhere in `ConformanceFinding` or the manifest that
  would compute a percentage, ratio, or count-based score.
- No new key added to `source-map.yaml`'s schema by this feature (the
  natural-key marker research.md identifies as the C3 prerequisite is a
  FUTURE cross-feature change, not part of this data model).
- No `approvals[]` entry shape or new `readiness-status.yaml` key -- FR-016
  (Q-APPROVAL-SEAM) is OPEN; this data model records no such structure.
