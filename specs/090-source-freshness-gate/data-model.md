# Data Model: Source Freshness / Staleness Declaration and Static Presence Check

Phase 1 output. Defines the shapes HR4 reads and produces. Generic (Principle
VII): any table id, cadence word, or duration value below is an ILLUSTRATION
ONLY, never a required or copied worked-example value. No C086/
`retail_store_sales` specifics are inlined.

## Entities (from spec.md Key Entities)

### FreshnessDeclaration (`meta.freshness`)

The human-authored SLA statement living under a table's `source-map.yaml`
`meta:` block. Declared, never computed, by this feature (FR-002).

```yaml
# mappings/<table>/source-map.yaml (SHAPE -- illustrative values only)
meta:
  table_id: "<TABLE_ID>"
  # ... existing meta keys unchanged (source_system, profiled_from, grain,
  #     primary_key, reviewed_by, reviewed_on) ...
  freshness:                          # NEW sibling key (this feature's allocation)
    expected_cadence: "<cadence>"     # e.g. daily | weekly | monthly | quarterly
                                       #      | annual | one_time (or "static")
    max_staleness: "<duration>"       # e.g. "2 days" | "1 week" | "n/a" (one_time only)
```

| Field | Type | Required when block present | Notes |
|---|---|---|---|
| `meta.freshness` | mapping | n/a (the block itself is OPTIONAL -- see "Presence-gating," FR-014) | sibling of `meta.grain`/`meta.primary_key`/`meta.reviewed_by`; no other `meta` key is added, renamed, or removed (FR-001) |
| `meta.freshness.expected_cadence` | string, closed vocabulary | yes, once the block exists | human-declared; never inferred or defaulted by automation (FR-002, FR-008) |
| `meta.freshness.max_staleness` | string, magnitude+unit or `n/a` sentinel | yes, once the block exists | human-declared; never inferred or defaulted by automation (FR-002, FR-008) |

**Presence is optional; well-formedness is not (the load-bearing distinction
this data model encodes).** `meta.freshness` itself may be ABSENT from any
given filled `source-map.yaml` with zero HR4 Findings -- whether it becomes
mandatory (retroactively or going forward) is the OPEN Q-FR014-SCOPE ruling
(FR-014), not decided by this feature. But once the block IS present, BOTH
sub-keys MUST be present, non-blank, and match the grammar below, or HR4
fails closed (FR-004(b)). This is the same shape as an optional field in a
schema that becomes strictly validated the moment it is supplied.

### Token grammar (Clarification C1, resolved at plan stage)

Small, generic, calendar-vocabulary-only (Principle VII: no C086 value
inlined). Both checks trim leading/trailing whitespace before matching
(FR-002); comparison is case-insensitive.

**`expected_cadence`** -- closed enum:

| Recognized value | Synonyms accepted | Meaning |
|---|---|---|
| `daily` | -- | new data expected every day |
| `weekly` | -- | new data expected every week |
| `monthly` | -- | new data expected every month |
| `quarterly` | -- | new data expected every quarter |
| `annual` | `annually`, `yearly` | new data expected every year |
| `one_time` | `static` | a genuinely one-time/static reference source (Clarification C2); pairs with `max_staleness: "n/a"` |

Any other string -- empty, whitespace-only, a typo, a free-text phrase, a
number, an unrecognized synonym -- is MALFORMED (fail-closed ERROR, FR-004(b)
and Edge Cases "unparseable form").

**`max_staleness`** -- magnitude-plus-unit duration, OR the `n/a` sentinel:

- Duration form (regex, generic calendar units only):
  `^\s*\d+\s*(hour|day|week|month|quarter|year)s?\s*$` (case-insensitive) --
  a positive integer magnitude, optional whitespace, one recognized
  calendar-unit word, an optional trailing `s` for the plural, optional
  surrounding whitespace. Examples of WELL-FORMED values: `"2 days"`,
  `"1 week"`, `"3 hours"`, `"1quarter"`. Examples of MALFORMED values: `""`,
  `"soon"`, `"a few days"`, `"days"` (no magnitude), `"-1 day"` (non-positive),
  `"2 fortnights"` (unrecognized unit).
- Sentinel form: the literal `n/a` (case-insensitive), reserved for pairing
  with `expected_cadence: one_time`/`static` (Clarification C2). Using `n/a`
  with any OTHER `expected_cadence` value is still WELL-FORMED at the grammar
  level (the grammar does not cross-validate the two fields against each
  other -- that pairing rule is a documentation convention, not an HR4 check,
  keeping the rule simple and avoiding a second axis of "malformed"); HR4
  only ever evaluates each sub-key's own well-formedness independently.

**Why this shape (traceability to C1's constraints)**: a closed enum plus a
strict duration regex makes "unparseable" a well-defined, fail-closed-able
test (Principle I cannot rest on an undefined predicate) while remaining
small and permissive enough that a legitimate phrasing among the recognized
calendar units is never false-positived (C1's explicit caution). Neither list
contains a C086/`retail_store_sales`-specific cadence or duration (FR-011).
The exact member list is a mechanical vocabulary choice, not a business-SLA
or governance judgment (C1 reasoning), so it is safe to fix here even though
Q-FR014-SCOPE (which tables must use it) remains open.

### HR4 (static presence/well-formedness rule)

The one new `@register`-ed `retail check` rule this feature adds.

- **Reads**: every `mappings/<table>/source-map.yaml` matching the pattern
  `mappings/<name>/source-map.yaml` from `ctx.tracked_files`, EXCLUDING
  `templates/source-map.yaml` (Clarification C3 -- the template is schema
  documentation, not an instance) and excluding anything under `tests/`
  (`is_test_path`, fixture exemption for the rule's own unit tests).
- **Table identity for locators**: the table directory segment
  (`mappings/<TABLE>/source-map.yaml` -> `<TABLE>`), which is always present
  regardless of whether the file's own `meta.table_id`/`source_id` uses the
  rich or compact form (mirrors the robustness lesson from the HR1 precedent,
  where the two committed instances use different internal identity fields).
- **Is-in-scope-to-parse test**: a table is evaluated by HR4 if and only if
  its `mappings/<table>/source-map.yaml` file exists and parses as YAML with
  a top-level `meta:` mapping. A table with no such file (Stage 1,
  pre-mapping) is entirely excluded (FR-005) -- HR4 never fires ahead of
  Stage 2.
- **Never writes**: `source-map.yaml`, `readiness-status.yaml`, or
  `approvals[]` (FR-008). Read-only, side-effect-free, matching every other
  `retail check` rule's contract (`Rule = Callable[[RuleContext],
  Iterable[Finding]]`, `src/retail/core.py`).

### FreshnessFinding

Not a new class -- this feature emits the EXISTING `Finding` dataclass
(`src/retail/core.py`, unchanged) with `rule_id = "HR4"`. No new Finding
schema is introduced; the table below documents HR4's USAGE of the existing
fields.

| Field | HR4 usage |
|---|---|
| `rule_id` | always the literal string `"HR4"` |
| `severity` | `Severity.ERROR` for every case in the Finding taxonomy below (HR4 has no WARNING case -- unlike SF1/HR1, there is no "stale declaration" concept here because there is no cross-file manifest to go stale; a missing sub-key IS the whole defect) |
| `message` | categorical prose naming the table, the specific missing/malformed field (`expected_cadence` and/or `max_staleness`), and the offending raw value when present -- NEVER a number expressing a score, ratio, staleness duration, or "N of M" tally (hard rule #9, FR-007) |
| `locator` | `mappings/<table>/source-map.yaml:meta.freshness.<field>` when a specific sub-key is at fault, or `mappings/<table>/source-map.yaml:meta.freshness` when the whole block is malformed in a way not isolated to one sub-key (e.g. the block exists but is not a mapping) |

## Finding taxonomy (exhaustive; matches spec.md Edge Cases + FR-002/FR-004/FR-005)

| Case | Trigger | Severity | FR / Edge Case |
|---|---|---|---|
| Block absent entirely | filled `source-map.yaml` exists, `meta.freshness` key is not present at all | **no Finding** (presence-gated; see plan.md and research.md "Landing precondition") | FR-014 (OPEN scope), Edge Cases (retroactive-map bullet) |
| Block present, both sub-keys well-formed | `expected_cadence` matches the enum AND `max_staleness` matches the duration/`n/a` grammar | no Finding | SC-001 |
| Block present, `expected_cadence` missing/blank | `meta.freshness.expected_cadence` absent, `null`, or empty/whitespace-only after trim | ERROR | FR-004(b) |
| Block present, `expected_cadence` unparseable | a non-empty string not in the closed enum (case-insensitive) | ERROR | FR-004(b), Edge Cases ("a cadence string the rule cannot classify") |
| Block present, `max_staleness` missing/blank | `meta.freshness.max_staleness` absent, `null`, or empty/whitespace-only after trim | ERROR | FR-004(b) |
| Block present, `max_staleness` unparseable | a non-empty string matching neither the duration regex nor the `n/a` sentinel | ERROR | FR-004(b) |
| Block present but not a mapping (e.g. a bare string/list) | `meta.freshness` exists but is not a YAML mapping | ERROR (whole-block locator) | FR-004(b) (malformed) |
| `source-map.yaml` missing/unparseable as YAML | file absent or fails to parse | table excluded from HR4 entirely; no HR4 Finding for that table (a different rule's concern, not HR4's) | FR-005 (pre-Stage-2 case is one instance of this) |
| `templates/source-map.yaml` itself | the template file, whatever placeholder text it carries | never evaluated -- explicitly excluded by path | FR-011, Clarification C3 |
| Fixture under `tests/` | any path where `is_test_path` is true | never evaluated as a real subject (used only by HR4's own unit tests) | mirrors SF1/HR1 convention |

## Relationships

```text
ctx.tracked_files
        |
        |  filter: matches "mappings/<name>/source-map.yaml"
        |          AND NOT "templates/source-map.yaml"
        |          AND NOT is_test_path(path)
        v
   candidate filled source-map.yaml paths (one per table)
        |
        |  parse YAML; no top-level `meta:` mapping? --> excluded (not HR4's concern)
        v
   meta.freshness present?  --no--> no Finding for this table (presence-gated)
        |  yes
        v
   is `meta.freshness` a mapping?  --no--> ERROR (whole-block locator)
        |  yes
        v
   expected_cadence well-formed (enum)?  --no--> ERROR (field locator)
   max_staleness well-formed (duration|n/a)?  --no--> ERROR (field locator)
        |  both yes
        v
   no Finding for this table
```

HR4's overall return value is `list[Finding(rule_id="HR4", ...)]` -- no side
effects, no writes, exactly the existing `Rule` contract.

## Non-goals for this data model (YAGNI, matches spec.md Assumptions)

- No live/measured arrival-time field anywhere (that is the deferred
  `retail validate` concern, FR-006).
- No numeric field anywhere in `FreshnessFinding` or the grammar that would
  compute a percentage, ratio, elapsed-time, or freshness score (FR-007).
- No new top-level key in `source-map.yaml` beyond `meta.freshness` itself,
  and no new file (FR-001).
- No cross-table manifest (unlike HR1's `conformed-dimension-map.yaml`) --
  HR4 evaluates each table's own `source-map.yaml` in isolation; there is
  nothing to reconcile across tables for this concern.
- No `approvals[]` entry shape or new `readiness-status.yaml` key, and no
  eighth readiness stage or fifth status value (Assumptions: "no new
  readiness stage... no change to the four-status model").
- No decision on Q-FR014-SCOPE (mandatory vs. going-forward, one-time
  exemption shape) -- that ruling, once made, is a FUTURE change to the
  "block absent entirely" row above, not something this data model
  anticipates with a half-built mechanism.
