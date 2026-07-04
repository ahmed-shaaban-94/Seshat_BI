# Data Model: Dimension History / SCD Policy Readiness

Phase 1 output. Defines the shapes HR2 reads and produces. Generic (Principle VII):
`dim_<entity>`, `dim_customer_rss`, and any table id below are ILLUSTRATIONS ONLY, never
required names. No worked-example (C086/pharmacy) specifics are inlined.

## Entities (from spec.md Key Entities)

### SCD declaration

The `gold_star.dimensions[].scd_type` field -- this feature's entire new schema footprint
(collision-avoidance allocation).

| Property | Value |
|---|---|
| Location | nested under EACH entry of `gold_star.dimensions[]` in `mappings/<table>/source-map.yaml`, alongside `name` / `surrogate_key` / `has_unknown_member` / `attributes[]` |
| Type | string enum |
| Permitted values | exactly `type_1` (overwrite -- matches today's drop-and-rebuild default) or `type_2` (historized -- changes must be preserved as dated rows) |
| Authored by | a human, at Mapping Ready (Stage 2), inside the same reviewed `source-map.yaml` a human already approves -- NEVER inferred, defaulted, or auto-filled by HR2 or any tool (FR-003, Principle V) |
| Absent, or present but empty/placeholder (`""`, `null`, or a case-insensitive `"tbd"`) | a fail-closed Needs-decision ERROR (FR-005; routing per Clarification C6) -- NOT silently treated as `type_1`; there is no already-approved-map grandfather clause. A placeholder is semantically an undeclared decision, so it routes here, not to the invalid-value case below |
| Present, non-empty, and not a recognized placeholder, but not exactly `type_1` or `type_2` | a fail-closed ERROR naming the dimension and the invalid value (FR-006; e.g. a typo like `"type1"` or an out-of-scope taxonomy value like `"type_3"`) |
| Read by | HR2 only. Never written, generated, or defaulted by HR2 (FR-011) |
| Out of scope | `gold_star.degenerate_dimensions[]` entries and the `gold_star.date_dimension` block never carry or require this field (FR-010, Edge Cases) |

```yaml
# templates/source-map.yaml (SHAPE -- illustrative names only; this is the ONLY new key)
gold_star:
  dimensions:
    - name: "dim_<entity_a>"
      surrogate_key: "<entity_a>_sk"
      has_unknown_member: true
      scd_type: "type_1"          # NEW (this feature): "type_1" | "type_2" -- human-declared
      attributes:
        - "<entity_a>_id"
        - "<entity_a>_attribute"
```

### Gold migration construct (the drop-and-rebuild signal)

Not a new artifact type -- a recognized SHAPE inside an EXISTING file class,
`warehouse/migrations/*create_gold_<table>_star.sql`, that HR2 reads as committed TEXT only
(never executed).

| Property | Value |
|---|---|
| File pattern | `warehouse/migrations/*create_gold_<table>_star.sql` (the existing `retail-build-warehouse` gold-migration naming convention); `<table>` resolves from the mapping-directory name (`mappings/<table>/source-map.yaml`), per Clarification C7 |
| Recognized construct | a `DROP TABLE IF EXISTS <dim_table>` for a dimension's own gold table PLUS a same-file `CREATE TABLE <dim_table>` that recreates it -- in EITHER authored form: `CREATE TABLE <dim_table> AS SELECT ...` (CTAS) OR explicit column DDL (`CREATE TABLE <dim_table> (...)`) followed by one or more `INSERT INTO <dim_table> ...` statements |
| Adjacency | NOT required -- the documented (and confirmed committed) shape batches every `DROP TABLE IF EXISTS` up front, then recreates each table further down in the same file (research.md C5) |
| `<dim_table>` resolution | the dimension entry's own `gold_star.dimensions[].name`, with an optional leading `<schema>.` prefix (e.g. `gold.`) stripped from BOTH the declared `name` and the `DROP`/`CREATE` token before comparing the bare identifier (research.md C4) -- this SCOPES the match to that one dimension's own table so an unrelated `type_1` dimension's ordinary drop-and-rebuild in the same file never fires a finding against a different, `type_2`-declared dimension |
| Meaning when found for a `type_2`-declared dimension | the construct DISCARDS prior attribute values on every re-run -- proven, mechanical, cannot honor a `type_2` declaration (FR-007) |
| Meaning when found for a `type_1`-declared dimension | correct, honored behavior -- no finding (FR-009) |
| Meaning when the migration glob matches ZERO files | not-yet-buildable state -- no finding fabricated either way (FR-008) |
| Meaning when the migration glob matches MORE THAN ONE file | an ambiguous-migration state -- a single fail-closed ERROR naming the table and every matched filename, rather than inspecting any one of them or guessing which is current (FR-008, Clarification C7) |
| Positive-signal recognition (a valid, correctly-authored Type-2 construct) | explicitly OUT OF SCOPE for this feature -- no such construct exists in any committed migration today (research.md, Clarification C3); a future feature that adds Type-2 authoring will need to add this |

### HR2 Finding

Not a new class -- this feature emits the EXISTING `Finding` dataclass (`src/retail/core.py`,
unchanged) with `rule_id = "HR2"`. No new Finding schema is introduced; the table below
documents HR2's USAGE of the existing fields, not a new type.

| Field | HR2 usage |
|---|---|
| `rule_id` | always the literal string `"HR2"` |
| `severity` | `Severity.ERROR` in every emitting case (Needs-decision, invalid value, proven drop-and-rebuild mismatch) -- there is no WARNING-only HR2 case (Assumptions: "Severity posture"; each case is either a required-and-absent human decision or a proven mechanical contradiction) |
| `message` | categorical prose naming the dimension, the table, and WHAT is wrong (undeclared, invalid value + the value seen, or declared-`type_2`-but-not-honored + the migration file) -- NEVER a number expressing a score, ratio, or "N of M" tally (hard rule #9, FR-013) |
| `locator` | a repo-relative pointer, e.g. `mappings/<table>/source-map.yaml:<dimension_name>` for a declaration-level finding (undeclared/invalid), or the migration file path for a build-mismatch finding (mirrors SF1's `f"{SPINE_REL}:{basename}"` and HR1's compound-locator convention) |

## Finding taxonomy (exhaustive; matches spec.md Edge Cases + FR-005..FR-010, Clarifications C6/C7)

| Case | Trigger | Severity | FR / User Story |
|---|---|---|---|
| Undeclared `scd_type` (Needs-decision) | a `gold_star.dimensions[]` entry has no `scd_type` key at all | ERROR | FR-005, US3 |
| Placeholder `scd_type` (Needs-decision, same message/remedy as undeclared) | `scd_type` present but holds `""`, `null`, or a case-insensitive `"tbd"` | ERROR | FR-005, Clarification C6 |
| Invalid `scd_type` value | `scd_type` present, non-empty, not a recognized placeholder, and not exactly `type_1` or `type_2` (e.g. a typo `"type1"` or an out-of-scope value `"type_3"`) | ERROR | FR-006, US1 AS3, Clarification C6 |
| Declared `type_2`, migration builds by drop-and-rebuild | a `type_2`-declared dimension's own gold table matches the FR-007 construct in its own `warehouse/migrations/*create_gold_<table>_star.sql` | ERROR | FR-007, US2 AS1 |
| Declared `type_1`, any build shape | drop-and-rebuild is the correct, honored mechanism for an overwrite policy | no Finding | FR-009, US2 AS2 |
| Declared `type_2`, no gold migration exists yet (glob matches zero files) | the table's `warehouse/migrations/*create_gold_<table>_star.sql` cannot be found | no Finding (not-yet-buildable; not fabricated) | FR-008, US2 AS3 |
| Migration glob matches MORE THAN ONE file for a table | ambiguous migration set -- HR2 does not inspect any of them or guess which is current | ERROR naming the table and every matched filename | FR-008, Clarification C7 |
| Declared `type_2`, migration exists but does not match the drop-and-rebuild construct (e.g. hand-authored upsert) | no recognized negative signal fires | no Finding (this feature does not validate CORRECTNESS of a non-drop-and-rebuild pattern -- Edge Cases; live-data question, deferred) | Edge Cases |
| Every dimension of a table validly declared, and no `type_2` dimension's migration matches the construct (or none exists) | -- | zero Findings for that table | SC-001 |
| `gold_star.degenerate_dimensions[]` entries | never read for `scd_type` purposes | no Finding, no requirement | FR-010, Edge Cases |
| `gold_star.date_dimension` block | never read for `scd_type` purposes | no Finding, no requirement | FR-010, Edge Cases |

## Relationships

```text
mappings/<table>/source-map.yaml (N files, one per table)
        |
        |  gold_star.dimensions[] entries only (never degenerate_dimensions[]/date_dimension)
        v
      { dimension_name: scd_type | <missing> | <placeholder> | <invalid value> }
        |
        |  scd_type missing OR placeholder ("", null, "tbd")?
        |                          --> ERROR (FR-005, Needs-decision, C6)
        |  scd_type invalid (non-empty, non-placeholder, not type_1/type_2)?
        |                          --> ERROR (FR-006, C6)
        |  scd_type == "type_1"   --> no Finding regardless of build (FR-009)
        |  scd_type == "type_2"   --> look up this table's gold migration
        v
      warehouse/migrations/*create_gold_<table>_star.sql  (glob; C7)
        |
        |  zero matches?     --> no Finding (FR-008, not-yet-buildable)
        |  2+ matches?       --> ERROR naming the table + every matched
        |                        filename (FR-008, C7); no file inspected
        |  exactly 1 match   --> scope-match DROP+CREATE for THIS dimension's
        |                        own <dim_table> (schema-prefix-stripped
        |                        compare, C4)
        v
      construct found (CTAS or DDL+INSERT, non-adjacent OK, C5)?
        |
        |  yes --> ERROR (FR-007, proven mismatch)
        |  no  --> no Finding (a non-drop-and-rebuild pattern's CORRECTNESS is
        |          out of scope -- Edge Cases)
        v
      list[Finding(rule_id="HR2", ...)]   <-- HR2's return value; no side effects, no writes
```

## Non-goals for this data model (YAGNI, matches spec.md Assumptions)

- No live/materialized-data shape (SCD-2 row-level correctness auditing -- duplicate current
  rows, `effective_to` gaps, `is_current` flags -- is a future `retail validate` concern).
- No numeric field anywhere in the Finding usage or the `scd_type` declaration that would
  compute a percentage, ratio, or count-based score (hard rule #9).
- No fuller SCD taxonomy (Type-0/3/4/6) -- exactly the two-value enum `type_1`/`type_2`
  (Clarification C2).
- No positive-recognition signal for a valid, correctly-authored Type-2 construct -- future
  scope once Type-2 authoring exists (Clarification C3); nothing in this data model assumes
  or scaffolds that signal.
- No migration/backfill mechanism for a dimension changing declared type after gold already
  exists -- a type change is treated as an ordinary Mapping Ready map edit (Edge Cases).
- No `approvals[]` entry shape or new `readiness-status.yaml` key -- FR-017
  (Q-APPROVAL-SEAM) is OPEN; this data model records no such structure.
- No new top-level `source-map.yaml` key and no other sibling key on the dimension entry --
  the schema footprint is exactly `gold_star.dimensions[].scd_type` (collision-avoidance
  allocation shared with 090/103/105, each in their own, different sub-key).
