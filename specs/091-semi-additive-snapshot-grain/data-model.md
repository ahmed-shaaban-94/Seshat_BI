# Data Model: Semi-Additive (Snapshot) Grain in the Metric Contract

**Feature**: 091-semi-additive-snapshot-grain | **Date**: 2026-07-04

This feature introduces one new schema field and one new categorical finding
shape. It defines no persisted store, no database table, and no new file
format. Everything below is a description of YAML/markdown structure,
generic per Principle VII -- no worked-example (C086 / retail_store_sales /
pharmacy) value appears in any example below beyond the pre-existing
placeholder conventions already used in `templates/metric-contract.yaml`.

## Entity 1: `time_additivity` field (new)

**Where it lives**: a new, OPTIONAL, top-level scalar key on
`templates/metric-contract.yaml`, positioned alongside the existing `grain`
and `readiness` fields, and on every filled copy under
`mappings/<table>/metrics/*.yaml`.

**Shape**:

```yaml
time_additivity: "<fully | semi | non>"   # OPTIONAL; omit if not yet flagged
```

| Attribute | Value |
|---|---|
| Type | scalar string (YAML string node) |
| Required | No -- optional on every contract; becomes REQUIRED-in-effect (via HR5) only on a contract that also carries an A10 `ambiguities[]` entry |
| Closed vocabulary | exactly `fully`, `semi`, `non` (lowercase, case-sensitive, untrimmed -- FR-002/FR-002a) |
| Who writes it | a named human metric owner, authoring or reviewing the contract |
| Who reads it | HR5 (validates only); no other rule or generator reads or writes it in this build |
| What it means | the metric's additivity classification specifically over the DATE axis -- can this measure be validly summed across multiple dates |
| What it does NOT mean | AD1's whole-metric composition-legality classification (a different, orthogonal question); see spec "Boundary against neighbouring shipped work" |
| Citation | the field's authoring comment MUST cite `skills/retail-kpi-knowledge/knowledge/kpi-additivity-and-grain.md` (FR-001); it MUST NOT restate or redefine what "semi-additive" means (FR-003, FR-015) |

**Absence/degenerate-value normalization** (Clarifications Q3/Q3b; not
stored differently on disk, but interpreted identically by HR5):

| On-disk form | HR5 treats it as |
|---|---|
| key entirely absent | `ABSENT` |
| `time_additivity:` with no value (YAML null) | `ABSENT` (same bucket as missing -- FR-004b) |
| `time_additivity: ""` (empty string) | `ABSENT` (same bucket as missing -- FR-004b) |
| `time_additivity: "fully"` | `FULLY` (in-vocabulary) |
| `time_additivity: "semi"` | `SEMI` (in-vocabulary) |
| `time_additivity: "non"` | `NON` (in-vocabulary) |
| `time_additivity: "Fully"` / `"SEMI"` / `"non "` (case/whitespace variant) | `OUT_OF_VOCAB` (FR-002a -- never normalized) |
| `time_additivity: "sometimes"` (free text, typo, numeric placeholder) | `OUT_OF_VOCAB` (FR-006) |
| `time_additivity: [a, b]` or a mapping (non-scalar YAML node) | `OUT_OF_VOCAB` (FR-006a -- read without raising) |

## Entity 2: A10 ambiguities-ledger entry (existing, unchanged, read-only)

**Where it lives**: the existing `ambiguities[]` list on
`templates/metric-contract.yaml` / `mappings/<table>/metrics/*.yaml`
(unchanged shape; this feature adds no field to it).

**Shape** (excerpt of the existing schema, reproduced for reference only):

```yaml
ambiguities:
  - id: "A10"                    # one of A1..A11; HR5 matches ONLY the exact
                                  #   literal "A10" (FR-004a) -- no case-fold,
                                  #   no substring/prefix match
    decision_status: "undecided" # decided | undecided -- HR5 does NOT gate on
                                  #   this (a decided A10 entry still requires
                                  #   a time_additivity declaration; the two
                                  #   fields answer different questions)
    ruling: ""
    evidence: []
    number_moving: true
```

**HR5's read of this entity**: iterate `ambiguities[]` (a list of mappings);
an entry is an "A10 entry" iff `entry.get("id") == "A10"` (exact string
equality). Presence of ANY such entry (regardless of position, regardless of
how many other unrelated entries exist, regardless of `decision_status`)
sets the per-contract trigger `HAS_A10 = True`. No other field of the entry
is read by HR5.

## Entity 3: HR5 finding (new, in-memory / emitted only)

**Where it lives**: not persisted to disk. Constructed and returned by the
new rule module as part of the `retail check` run's `Iterable[Finding]`
result, using the existing `Finding` / `Severity` shapes from
`src/retail/core.py` (unchanged by this feature).

**Shape** (using the existing `Finding` dataclass fields):

```text
Finding(
    rule_id="HR5",
    severity=Severity.ERROR,       # HR5 emits ERROR only -- no WARNING, no score (FR-009)
    message="<one of the four categorical messages below>",
    locator="<repo-relative path to the offending contract file>",
)
```

HR5 never emits a `Severity.WARNING`, a numeric field, or a graded value of
any kind (hard rule #9 / FR-009).

## The decision table (the full ERROR / CLEAN truth table)

This is the complete logic HR5 implements. Each row is independently
testable per the spec's Acceptance Scenarios / Edge Cases / Independent
Tests. `HAS_A10` is computed per Entity 2 above; `TA_STATE` is computed per
Entity 1's normalization table above.

| # | File readable? | `HAS_A10` | `TA_STATE` | Outcome | Message class |
|---|---|---|---|---|---|
| 1 | No | -- | -- | **ERROR** | fail-loud: "could not read/parse metric contract: `<exc>`" (mirrors AL1's unreadable-file message; FR-014) |
| 2 | Yes | False | `ABSENT` | CLEAN | (no finding -- field is optional when not A10-flagged; FR-007) |
| 3 | Yes | False | in-vocab (`FULLY`/`SEMI`/`NON`) | CLEAN | (no finding -- an owner may volunteer the declaration early; validated-only per Edge Cases / Acceptance Scenario 3 of US2) |
| 4 | Yes | False | `OUT_OF_VOCAB` | **ERROR** | "unrecognized `time_additivity` value" (FR-006 fires regardless of A10 presence) |
| 5 | Yes | True | `ABSENT` | **ERROR** | "missing `time_additivity` declaration on an A10-flagged (snapshot) contract" (FR-004) |
| 6 | Yes | True | `FULLY` | **ERROR** | "an A10-flagged contract cannot declare `time_additivity: fully`" (FR-005 -- distinct message from row 5) |
| 7 | Yes | True | `SEMI` | CLEAN | (no finding -- valid declaration; SC-002/SC-003 clearing case) |
| 8 | Yes | True | `NON` | CLEAN | (no finding -- valid declaration) |
| 9 | Yes | True | `OUT_OF_VOCAB` | **ERROR** | "unrecognized `time_additivity` value" (FR-006 -- same message class as row 4, distinct from rows 5/6 per SC-004) |

Three distinct ERROR message classes exist (row 1 unreadable; rows 5
missing; row 6 illegal-fully; rows 4/9 unrecognized), matching SC-004's
requirement that the missing-field and unrecognized-value findings be
distinguishable, and matching FR-005's requirement that "declares `fully`"
be its own outcome distinct from "declares nothing."

**No contracts on disk / no contract carries A10** (Edge Case, FR-013):
degenerate case of rows 2/3 applied to an empty or all-row-2/3 corpus --
zero findings, a clean pass, matching the current committed corpus (research.md
Section 1.6 confirms zero `A10` hits in `mappings/*/metrics/*.yaml` today).

## Non-goals (explicitly NOT part of this data model)

- No `time_additivity_reason` / free-text justification field is added --
  the spec's Key Entities section defines exactly one new field.
- No numeric/graded severity or confidence field is added to `Finding` or
  to the template (hard rule #9).
- No change to the `ambiguities[]` entry shape (`id`, `decision_status`,
  `ruling`, `evidence`, `number_moving` are unchanged).
- No new top-level key besides `time_additivity` is added to
  `templates/metric-contract.yaml` by this feature (collision avoidance vs.
  092's separate file and 103's own key).
- No cross-reference field linking a `time_additivity` value to AD1's
  additivity-composition classification is added (the two stay orthogonal
  and unlinked in this build).
