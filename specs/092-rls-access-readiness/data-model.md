# Data Model: Row-Level Security as a Semantic-Model-Ready Dimension

**Feature**: 092-rls-access-readiness | **Phase**: 1

All shapes below are GENERIC (Principle VII): every example value is an
obvious placeholder. No `retail_store_sales`/C086-specific role, column, or
table name is used. A filled worked example, if authored later, belongs under
`docs/worked-examples/` or `mappings/<table>/roles/`, never inlined here or in
the shipped template.

## Entity 1 -- RLS role contract

A filled copy of `templates/rls-role-contract.yaml`, one file per role,
co-located under `mappings/<table>/roles/<RoleName>.yaml` (research P8, spec
Clarification C4). Human-authored; the agent never fills or self-approves
one (Principle V, Principle I).

### Shape

```yaml
# templates/rls-role-contract.yaml  --  the machine-readable DEFINITION of
# one Power BI RLS role. Sibling of templates/metric-contract.yaml; SEPARATE
# file (collision-avoidance allocation -- no key lives in metric-contract.yaml).

# -----------------------------------------------------------------------
# identity -- the stable name a PBIP role (roles.tmdl) references.
# -----------------------------------------------------------------------
name: "<RoleName>"                 # e.g. RegionManager. Stable; MUST be UNIQUE
                                   #   across every committed role contract
                                   #   (HR6 flags a duplicate -- FR-009).

# -----------------------------------------------------------------------
# filter -- the {gold_table, column} pair this role's filter expression is
# claimed to restrict. GOLD DIMENSION ONLY (Principle III + FR-003/FR-005):
# a gold.fct_* binding, a silver/bronze binding, or a binding to a gold
# table absent from committed migrations is a defect HR6 catches.
# Declares WHICH column the filter targets; does NOT carry the DAX/M filter
# EXPRESSION's logic itself (that lives in the PBIP roles.tmdl, authored and
# reviewed separately -- this contract is the declared INTENT to bind).
# -----------------------------------------------------------------------
filter:
  gold_table: "gold.<dim_table>"   # e.g. gold.dim_store -- MUST be a gold.dim_*
                                   #   table (a gold.fct_* binding hard-fails
                                   #   per Clarification C1; FR-005).
  column: "<column>"               # e.g. store_id -- MUST exist on the named
                                   #   gold_table per committed migration SQL
                                   #   (FR-006). Empty/missing/blank hard-fails
                                   #   (FR-005).

# -----------------------------------------------------------------------
# readiness -- the contract's lifecycle state. FOUR explicit statuses ONLY;
# NO numeric score field anywhere (hard rule #9).
#   not_started  drafted but not yet reviewed/approved (the default)
#   blocked      a blocking_reason holds
#   warning      reviewable with a recorded non-fatal issue; never auto-promotes
#   pass         owner-approved -- REQUIRES a non-empty evidence[] (FR-008)
# -----------------------------------------------------------------------
readiness:
  status: "not_started"            # not_started | blocked | warning | pass
  evidence: []                     # for a pass: ["approved by <owner> on <YYYY-MM-DD>"]
  blocking_reasons: []             # required when status is blocked
```

### Field notes

| Field | Type | Required | HR6 checks |
|---|---|---|---|
| `name` | string | yes | non-empty; unique across all committed role contracts (FR-009) |
| `filter.gold_table` | string | yes | non-empty; matches `^gold\.\w+$`; must be a `dim_*`-prefixed table (per `docs/conventions.md`) present in committed migration SQL (FR-003, FR-005, FR-007); a `gold.fct_*` binding is a hard failure (Clarification C1) |
| `filter.column` | string | yes | non-empty; must exist as a column of the referenced `gold_table` per committed migration SQL (FR-005, FR-006) |
| `readiness.status` | enum | yes | one of the four explicit values only; no 5th value, no numeric field (hard rule #9) |
| `readiness.evidence` | list[string] | conditionally | non-empty whenever `status: pass` (FR-008) |
| `readiness.blocking_reasons` | list[string] | conditionally | non-empty whenever `status: blocked` |

**Never present**: a DAX/M filter expression string, a live PBIP role
definition, a numeric confidence/health score, a viewer/user-to-role mapping.
Those are, respectively, F016's execution concern, this feature's declared
scope boundary (FR-013), hard rule #9, and the OPEN Q-ZERO-ROLES-adjacent
who-sees-what governance ruling this feature never makes.

## Entity 2 -- Filter binding

Not a separate file -- the `filter: {gold_table, column}` block embedded in
Entity 1. Called out as its own entity (per the spec's Key Entities section)
because it is the one piece of structural DATA the HR6 check actually
evaluates; everything else in the contract (`name`, `readiness`) is checked
for shape/uniqueness/evidence but the filter binding is checked against an
EXTERNAL source of truth (the committed gold migration SQL). Declares intent
to bind; carries no expression logic.

## Entity 3 -- HR6 finding

Not a file -- the in-memory `Finding` (per `src/retail/core.py`) HR6 emits at
`retail check` runtime for a violation. Uses the existing `Finding` dataclass
unchanged; HR6 introduces no new finding shape, only new finding INSTANCES
under a new `rule_id`.

```text
Finding(
    rule_id="HR6",
    severity=Severity.ERROR,        # always ERROR -- HR6 fails closed
                                     # (Principle I; Clarification C1). Never
                                     # Severity.WARNING for a malformed
                                     # contract (unlike the ADR-default S5/S6/S7
                                     # family, a different rule lineage).
    message="<human-readable defect, naming the role and the unresolved column/table>",
    locator="<repo-relative path to the offending rls-role-contract.yaml>",
)
```

### Finding triggers (traces to Functional Requirements)

| Condition | Severity | FR |
|---|---|---|
| `filter.column` missing, empty, or blank | ERROR | FR-005 |
| `filter.column` does not exist on the referenced `gold_table` (per committed migration SQL) | ERROR | FR-006 |
| `filter.gold_table` names a `silver.*`/`bronze.*` object, or a `gold` table absent from committed migrations | ERROR | FR-007 |
| `filter.gold_table` names a `gold.fct_*` table (fact, not dimension) | ERROR | FR-005 + Clarification C1 |
| `readiness.status: pass` with `evidence: []` | ERROR | FR-008 |
| Two or more committed role contracts share the same `name` | ERROR | FR-009 |

All six are `Severity.ERROR` -- Principle I requires the rule to fail CLOSED,
and Clarification C1 explicitly rejects a WARNING tier for the fact-binding
case as the exact leak-through direction this feature exists to prevent. No
finding trigger in this table is WARNING-tier; this is a deliberate,
documented departure from the S5/S6/S7 ADR-default family (which IS
WARNING-tier by design, a different kind of rule).

**Explicitly NOT a finding trigger (Q-ZERO-ROLES, FR-010, OPEN)**: a table
with ZERO committed `rls-role-contract.yaml` files under
`mappings/<table>/roles/`. HR6 as specified here evaluates DECLARED contracts
only; it does not synthesize a finding for their absence. Whether the
Semantic Model Ready computation should separately surface the zero-contract
state (e.g. as a non-blocking `INFO`-tier note, per the PENDING DEFAULT in
`plan.md`'s Constitution Check) is left open for a named human ruling and/or
`tasks.md` to decide within that constraint -- it is not resolved by this
data model.

## Entity 4 -- Semantic Model Ready blocking reason (HR6-sourced)

Not a new schema -- an existing entry shape in a table's
`mappings/<table>/readiness-status.yaml` (`RS1`-governed structure, per
`src/retail/rules/readiness_status.py`) under
`stages.semantic_model_ready.blocking_reasons[]`. This feature adds a new
SOURCE of such entries (an HR6 finding), not a new FIELD or new file. A
blocking reason traceable to HR6 reads like:

```yaml
stages:
  semantic_model_ready:
    status: "blocked"
    evidence: []
    blocking_reasons:
      - "HR6: role 'RegionManager' filter.column is empty (mappings/<table>/roles/RegionManager.yaml)"
```

Cleared only when the underlying `rls-role-contract.yaml` is corrected and a
subsequent `retail check` run produces no HR6 finding for that role -- exactly
the same clear-by-recheck lifecycle every other `retail check`-sourced
blocking reason (D1-D11, C1, R1, G6) already follows in this file.

## Relationships between entities

```text
templates/rls-role-contract.yaml  (generic template, Principle VII)
        │  copied + filled by a security owner, one per role
        ▼
mappings/<table>/roles/<RoleName>.yaml   (RLS role contract, Entity 1)
        │  contains
        ▼
filter: {gold_table, column}             (Filter binding, Entity 2)
        │  checked against
        ▼
warehouse/migrations/*.sql               (committed gold schema; static source
        │                                  of truth, Principle VIII)
        │  HR6 evaluates the pair, emits on defect
        ▼
Finding(rule_id="HR6", ...)               (HR6 finding, Entity 3)
        │  surfaced into
        ▼
mappings/<table>/readiness-status.yaml
  .stages.semantic_model_ready.blocking_reasons[]   (Entity 4)
        │  blocks
        ▼
Semantic Model Ready (Stage 5) reaching `pass`
```

No entity in this feature reaches into `silver`/`bronze`, opens a database
connection, or reads/writes a live PBIP surface -- every arrow above is a
read of already-committed text.
