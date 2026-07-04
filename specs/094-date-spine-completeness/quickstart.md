# Quickstart: Date-Spine Completeness Static Gate (HR8)

How an agent or developer exercises HR8 once it is BUILT (this feature is
currently at the PLAN stage -- nothing below runs yet against `main`; this
describes the intended post-implementation experience so the plan's shape is
concrete).

## 1. Run the gate

HR8 is one more rule inside the existing static checker -- no new command, no
new flag:

```bash
retail check
```

or, scoped to unit tests during development:

```bash
pytest tests/unit/test_rc_defaults.py -k hr8 -m unit
```

There is no live-DB variant of this command for HR8 -- it never opens a
database connection (Principle VIII). `retail validate` (V-RC15) remains the
separate, live command for row-level coverage, unchanged by this feature.

## 2. What triggers a finding

HR8 only looks at an `INSERT INTO ... dim_date...` statement (any name
starting with `dim_date`, per S7's existing convention) inside a committed
`warehouse/migrations/*.sql` file, and only once that statement already
contains a `generate_series(...)` call (S7's own precondition for "not
gappy"). A statement using `SELECT DISTINCT` instead is S7's concern, not
HR8's -- HR8 emits nothing for it.

### Example -- non-daily step (FR-003, US1)

```sql
INSERT INTO gold.dim_date
SELECT (to_char(d,'YYYYMMDD'))::int AS date_sk, d::date AS full_date
FROM generate_series(DATE '2022-01-01', DATE '2025-01-18', INTERVAL '1 month') AS g(d);
```

`retail check` emits:

```text
[ERROR] HR8  warehouse/migrations/0010_example.sql:3
  dim_date generate_series step is INTERVAL '1 month', not daily (INTERVAL
  '1 day') -- every day between generated rows is absent from the calendar,
  breaking time-intelligence measures (TOTALYTD, SAMEPERIODLASTYEAR, DATEADD).
```

Changing the step to `INTERVAL '1 day'` clears the ERROR with the bounds
otherwise unchanged (SC-002).

### Example -- reversed literal bounds (FR-005, US2)

```sql
FROM generate_series(DATE '2025-01-18', DATE '2022-01-01', INTERVAL '1 day') AS g(d);
```

`retail check` emits an ERROR naming the file:line and BOTH literal values in
the order given (start, then end). Swapping the bounds back to chronological
order clears the ERROR (SC-003).

### Example -- unclassifiable step (FR-004, Edge Cases)

```sql
FROM generate_series(DATE '2022-01-01', DATE '2025-01-18', some_step_variable) AS g(d);
```

`retail check` emits an ERROR with wording distinct from the non-daily-step
message ("unreadable/unclassifiable step" vs "wrong step") -- a fail-closed
rule must not let an unclassifiable step pass silently.

### Example -- clean build (US3, FR-007)

```sql
FROM generate_series(DATE '2022-01-01', DATE '2025-01-18', INTERVAL '1 day') AS g(d);
```

`retail check` emits zero ERROR/WARNING findings for this statement and
exactly one INFO record:

```text
[INFO] HR8  warehouse/migrations/0004_create_gold_retail_store_sales_star.sql:107
  dim_date generate_series step (daily) and literal bounds order are
  structurally sound. Whether the calendar actually covers this fact's real
  transaction-date span is NOT proven here -- that is `retail validate`
  (V-RC15)'s job; live coverage is PENDING until it runs.
```

This is the shipped worked-example migration's actual state today (verified in
research.md) -- HR8 lands GREEN on the current tree, producing this one INFO
record and no ERROR (SC-001, SC-006).

### Example -- non-literal (fact-derived) bound

```sql
FROM generate_series(
  (SELECT min(sale_date) FROM silver.sales),
  DATE '2025-01-18',
  INTERVAL '1 day'
) AS g(d);
```

The bounds-order check (US2) does not fire (one side is not a literal), but
the same pending-live INFO record (US3) still applies -- a fact-derived bound
narrows drift risk but is not itself a coverage proof.

## 3. What HR8 will never say

Per hard rule #9 and FR-008, no HR8 output anywhere contains a numeric
confidence/health/completeness score, a percentage, or an "N of M" tally.
Per FR-007/FR-008, the INFO record never uses the words "covers", "complete",
"gap-free" (or an equivalent) to describe the fact's actual date range --
only that the migration's STRUCTURE (step, bounds order) is sound and live
coverage is unverified here.

## 4. What HR8 will never do

- Never edits, auto-fixes, or reformats a migration file (FR-009). On a
  breach it stops at the Finding; a human or agent-author fixes the SQL by
  hand.
- Never opens a database connection or reads a live Power BI/PBIP surface
  (Principle VIII).
- Never writes to `source-map.yaml` or any `readiness-status.yaml`, and never
  self-grants or records a Gold Ready pass (SCOPE GUARD; Principle V) -- Gold
  Ready's `pass` state still requires a clean `retail validate` run
  (RC2/RC15/RC16) plus penny-exact reconciliation, unchanged.
- Never changes `S7`'s or `V-RC15`'s own behavior, severity, or message text
  (FR-010).

## 5. Where to look when a finding appears

| Finding | Where the fix goes |
|---------|---------------------|
| `HR8` ERROR, non-daily step | Edit the named migration's `generate_series(...)` call's THIRD argument to `INTERVAL '1 day'` |
| `HR8` ERROR, unclassifiable step | Replace the step argument with a literal `INTERVAL '1 day'` expression |
| `HR8` ERROR, reversed bounds | Swap the named migration's `generate_series(...)` call's first two arguments into chronological order |
| `HR8` INFO, pending live coverage | No action required to pass `retail check`; before Gold Ready is `pass`, run `retail validate` (needs `db` extra + DSN) to clear V-RC15 |

## 6. Confirming the wiring landed correctly (implementer checklist)

After HR8 is authored, these are the checks a reviewer runs to confirm the
meta-gate lockstep held (per plan.md's Project Structure):

```bash
pytest tests/unit/test_rules_wiring.py -m unit      # EXPECTED_RULE_IDS contains "HR8"; count matches registry
pytest tests/unit/test_wiring_meta_gate.py -m unit  # 5-surface lockstep (manifest/severity-posture/glossary/count-claims)
pytest tests/unit/test_rc_defaults.py -k hr8 -m unit  # HR8's own mutation-verified tests
retail check                                        # full gate; must still exit 0 on the current tree
```
