# Data Model: Currency / Unit-of-Measure Contract

**Feature**: 103-currency-unit-contract | **Phase**: 1

All shapes below are GENERIC (Principle VII): every example value is an
obvious placeholder. No `retail_store_sales`/C086-specific unit label,
currency code, or column name is used. A filled worked example, if authored
later, belongs under `docs/worked-examples/` or the table's own
`mappings/<table>/source-map.yaml` / `mappings/<table>/metrics/*.yaml`, never
inlined here or in either shipped template.

## Entity 1 -- Unit declaration (`columns[].unit`, source-map)

A new OPTIONAL field inside each `columns[]` entry of a filled
`source-map.yaml` (`mappings/<table>/source-map.yaml`). Human-authored by
the analyst who profiled the source data; the agent never fills this in on
the analyst's behalf (Principle V, FR-020).

### Shape (addition to `templates/source-map.yaml`, existing `columns[]` entry)

```yaml
columns:
  - source_name: "<SRC_AMOUNT>"
    decision: "keep"
    reason: "core money measure; exact, not derivable from the others (RC9)"
    rename_to: "<measure_a>"
    silver_type: "numeric(18,2)"
    missing_policy: "null"
    pii: false
    gold_placement: "fact_measure"
    unit: null                       # NEW (FR-001). Unit of measure the
                                      #   column's numeric value is expressed
                                      #   in, e.g. "kg", "each". Free-text,
                                      #   human-authored. null = not yet
                                      #   declared (distinct from "declared
                                      #   as not applicable", which an
                                      #   analyst records as an explicit
                                      #   string, e.g. "n/a", if that is the
                                      #   honest state for a non-quantity
                                      #   column).
    currency: null                   # NEW (FR-001). ISO-style currency code
                                      #   the column's monetary value is
                                      #   expressed in, e.g. "EGP". Free-text,
                                      #   human-authored. null = not yet
                                      #   declared.
```

### Field notes

| Field | Type | Required | HR11 use |
|---|---|---|---|
| `columns[].unit` | string \| null | no (optional) | read verbatim, compared by exact case-sensitive string equality across a metric's resolved bound columns (FR-004, FR-005, FR-007) |
| `columns[].currency` | string \| null | no (optional) | read verbatim, compared by exact case-sensitive string equality across a metric's resolved bound columns (FR-004, FR-006, FR-007) |

**Never present**: a conversion rate, a conversion factor, a converted
value, a unit-alias/synonym table, or any normalization of the declared
string (Scope Guard, FR-007, FR-008). The field records ONLY what the
analyst observed the column to be expressed in -- HR11 never rewrites,
derives, or infers this value.

**Defaulting**: a filled copy that never sets `unit`/`currency` inherits the
`null` default shown in the generic template -- an explicit, visible
"not yet declared" state, not a silently absent key (FR-001). Whether HR11
treats a null value on one side of a multi-column bind as a blocking
mismatch, a warning, or a silent no-op is **FR-014, an OPEN Principle-V/VI
question** (see Entity 3 below) -- this entity's shape does not pre-empt
that ruling.

## Entity 2 -- Metric unit (`unit`, metric-contract)

A new OPTIONAL top-level field on a filled `metric-contract.yaml`
(`mappings/<table>/metrics/<MetricName>.yaml`), sibling to `grain` and
`binds_to`. Human-authored by the metric's owner.

### Shape (addition to `templates/metric-contract.yaml`, top level)

```yaml
name: "<MetricName>"
grain: "<the grain this metric is valid at>"
unit: null                            # NEW (FR-002). The unit of measure the
                                       #   metric's OWN resulting value is
                                       #   expressed in, e.g. "kg", "EGP",
                                       #   "count". Free-text, human-authored,
                                       #   optional, null = not yet declared.
                                       #   DOCUMENTARY ONLY (Clarification Q3):
                                       #   HR11 never cross-checks this value
                                       #   against binds_to.columns[]'s own
                                       #   declared units -- HR11's comparison
                                       #   is strictly column-to-column among
                                       #   binds_to.columns[] (see Entity 4).
                                       #   No metric-level `currency` field
                                       #   exists (Scope Guard) -- currency
                                       #   agreement is validated only across
                                       #   the bound columns' own
                                       #   columns[].currency declarations.
formula_intent: "<plain-language meaning of the metric; NOT DAX, NOT SQL>"
owner: "<named metric owner>"
binds_to:
  gold_table: "gold.<fact_or_dim>"
  columns:
    - "<gold_column_a>"
  pii_sensitive: false
```

### Field notes

| Field | Type | Required | HR11 use |
|---|---|---|---|
| `unit` (top-level) | string \| null | no (optional) | NOT read or compared by HR11 at all (documentary only, Q3) |

**Never present**: a metric-level `currency` field (Scope Guard, FR-002) --
adding one would create a second place to declare currency, contradicting
the single-source-of-truth intent of Entity 1.

## Entity 3 -- HR11 finding

Not a file -- the in-memory `Finding` (per `src/retail/core.py`) HR11 emits
at `retail check` runtime for a violation. Uses the existing `Finding`
dataclass unchanged; HR11 introduces no new finding shape, only new finding
INSTANCES under a new `rule_id`.

```text
Finding(
    rule_id="HR11",
    severity=Severity.ERROR,          # always ERROR -- HR11 fails closed
                                       # (Principle I). Never Severity.WARNING
                                       # for a genuine unit/currency clash
                                       # (unlike the ADR-default S5/S6/S7
                                       # family, a different rule lineage).
    message="<human-readable defect, naming the metric, the clashing column
              names, and their declared unit/currency values VERBATIM -- NO
              conversion factor, NO suggested rate, NO converted value>",
    locator="<repo-relative path to the offending metrics/<MetricName>.yaml>",
)
```

### Finding triggers (traces to Functional Requirements)

| Condition | Severity | FR |
|---|---|---|
| Two or more of a metric's resolved bound columns declare a different, non-null `unit` value | ERROR | FR-005 |
| Two or more of a metric's resolved bound columns declare a different, non-null `currency` value | ERROR | FR-006 |
| A `binds_to.columns[]` entry cannot be resolved against the table's `source-map.yaml` `columns[].rename_to` (including a name that only matches a `derived_columns` entry) | ERROR | FR-010, Clarification Q4 |
| The table's `source-map.yaml` is missing or unreadable | ERROR | FR-010 |

All four are `Severity.ERROR` -- Principle I requires the rule to fail
CLOSED for a genuine, resolvable clash or an unresolvable reference. No
finding trigger in this table is WARNING-tier.

**Explicitly NOT (yet) a finding trigger, pending an open question**:

- A metric contract whose `binds_to.columns[]` lists fewer than two columns
  -- HR11 has nothing to compare and MUST NOT fire (FR-011).
- **FR-013, OPEN (detection scope)**: whether a metric contract whose
  optional `definition.aggregation` is present and is NOT `sum` (e.g.
  `count_rows`, `distinct_count`) is in-scope for HR11 at all, and whether a
  metric with NO `definition` block is in-scope by default. Neither
  candidate is adopted here; see `plan.md`'s Constitution Check and
  `research.md`'s "Deferred capabilities" section. This table intentionally
  does not list a row for "which contracts trigger HR11 at all" beyond "2+
  bound columns" -- the finer scoping rule is the open item.
- **FR-014, OPEN (undeclared-value posture)**: whether an undeclared
  (null/absent) `unit`/`currency` on one side of a multi-column bind is
  itself a blocking finding, a warning, or a silent no-op. FR-005/FR-006 as
  literally written fire only on two-or-more DIFFERENT, NON-NULL values --
  a null-vs-non-null pairing is outside that literal condition until FR-014
  is ruled. **Q2a (internal-consistency flag)**: User Story 3 Acceptance
  Scenario 3 states a currency-declared-vs-undeclared pairing "is not
  treated as matches anything" -- i.e. it presupposes the STRICT answer to
  FR-014 -- but that scenario is recorded only as a CANDIDATE answer for the
  FR-014 owner to ratify or reject, not as a settled requirement. Until
  FR-014 is ruled, the literal FR-005/FR-006 non-null-vs-non-null comparison
  governs and this scenario is NOT guaranteed by the requirements as they
  stand.

## Entity 4 -- Resolved bound-column pair

Not a file -- the in-memory join HR11 performs between one metric
contract's `binds_to.columns[]` entry and that SAME table's
`source-map.yaml` `columns[]` entry, keyed on `columns[].rename_to`
(Clarification Q4, research P6). Called out as its own entity because it is
the one piece of structural DATA the HR11 check actually evaluates across
TWO files; everything else in either contract is read but not
cross-referenced.

```text
metric_contract.binds_to.columns[i]   (a gold-facing column name, e.g. "total_spent")
        │  matched against
        ▼
source_map.columns[j].rename_to       (the silver alias in that table's
        │                              source-map.yaml)
        │  when matched, read
        ▼
(source_map.columns[j].unit, source_map.columns[j].currency)
        │  compared pairwise across every resolved bound column of the SAME
        │  metric contract
        ▼
agree on both -> no finding   |   disagree on either -> HR11 Finding (Entity 3)
```

A `binds_to.columns[]` entry that names a `derived_columns` entry (which
carries no `unit`/`currency` field at all, per `templates/source-map.yaml`'s
existing shape) never matches any `columns[].rename_to` and therefore falls
under the "cannot be resolved" blocking path (FR-010) -- it is NOT silently
treated as unit/currency-agnostic.

## Relationships between entities

```text
templates/source-map.yaml          (generic template, Principle VII)
templates/metric-contract.yaml     (generic template, Principle VII)
        │  both edited additively; copied + filled per table/metric
        ▼
mappings/<table>/source-map.yaml          (filled source-map; Entity 1 lives
        │                                   inside its columns[] entries)
mappings/<table>/metrics/<MetricName>.yaml  (filled metric contract; Entity 2
        │                                     is its own top-level unit field)
        │
        │  HR11 joins the two via columns[].rename_to (Entity 4)
        ▼
Resolved bound-column pairs (unit, currency) compared pairwise
        │  disagreement or unresolvable reference
        ▼
Finding(rule_id="HR11", ...)               (HR11 finding, Entity 3)
        │  surfaced into
        ▼
mappings/<table>/readiness-status.yaml
  .stages.semantic_model_ready.blocking_reasons[]
        │  blocks
        ▼
Semantic Model Ready (Stage 5) reaching `pass`
```

A blocking reason traceable to HR11 reads like:

```yaml
stages:
  semantic_model_ready:
    status: "blocked"
    evidence: []
    blocking_reasons:
      - "HR11: metric 'TotalQuantity' sums columns with clashing units -- 'weight_kg' (kg) vs 'unit_count' (each) (mappings/<table>/metrics/TotalQuantity.yaml)"
```

Cleared only when the underlying declarations or bindings are corrected and
a subsequent `retail check` run produces no HR11 finding for that metric --
exactly the same clear-by-recheck lifecycle every other `retail
check`-sourced blocking reason (D1-D11, C1, R1, G6) already follows in this
file.

No entity in this feature reaches into `silver`/`bronze`, opens a database
connection, reads/writes a live PBIP surface, or computes/embeds a
conversion rate or factor -- every arrow above is a read of already-
committed text, and every comparison is an exact string-equality check.
