# Quickstart: Reload / Idempotency Readiness (HR7)

## Run the rule as part of the retail check

HR7 runs automatically inside the existing `retail check` governance command (the
same command already wired into the pre-commit path and CI). No new command is
introduced. On the current committed migration set
(`warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`, the only gold
migration today) it produces ZERO Findings out of the box -- full drop-and-rebuild
is the default and needs no edit or new file to pass (SC-001).

```bash
retail check
```

## Confirm the default (drop-and-rebuild) path stays free

1. Run `retail check` against the repo as committed today.
2. Confirm HR7 emits no Finding for `0004_create_gold_retail_store_sales_star.sql`
   (it drops every fact/dim with `DROP TABLE IF EXISTS` and recreates via a clean
   `INSERT ... SELECT`, with no append/upsert logic and no declaration in its header
   comment or in a `load-policy.md` -- none is required).

## Confirm an undeclared deviation fails closed

1. In a scratch/test fixture (never a real, executed migration), author a gold
   migration whose load is a bare `INSERT INTO gold.<table>` with no
   `DROP TABLE IF EXISTS` for that target, no `ON CONFLICT`/merge clause, and no
   `TRUNCATE`/partition-overwrite before the insert.
2. Add NO `reload-strategy:` marker anywhere (neither in the fixture's header
   comment nor in a `load-policy.md`).
3. Run the unit test suite (unit-marked): the HR7 rule-behavior test asserts
   exactly ONE `ERROR` Finding naming that migration file and stating the
   declaration is required and absent (SC-002).

## Confirm a declaration clears the Finding

1. Take the same fixture and add a single-line marker to its header comment:
   `-- reload-strategy: <key1>, <key2>` (or add an entry to a fixture
   `load-policy.md` naming the migration filename, the target table, and the same
   marker).
2. Re-run the unit test: the ERROR Finding clears with no other change to the
   fixture's data logic (SC-002). HR7 checks that a key is DECLARED, not that the
   load has been proven correct at runtime.

## Confirm an in-SQL key satisfies the requirement without a redundant declaration

1. Take a fixture whose load uses `ON CONFLICT (<key>) DO UPDATE` (upsert-on-key),
   or overwrites a named partition/date range via `DELETE`/`TRUNCATE` before insert,
   with NO separate `reload-strategy:` marker anywhere.
2. Run the unit test: HR7 recognizes the in-SQL key as satisfying the requirement
   and emits no Finding (FR-006).

## Confirm a mixed migration classifies per table

1. Take a fixture migration that drops-and-rebuilds one target table (e.g. a
   dimension) but bare-appends into a second target table (e.g. a fact) with no
   declaration for the second table.
2. Run the unit test: HR7 emits exactly one ERROR Finding naming the SECOND table
   only; the drop-and-rebuilt table contributes no Finding (Edge Cases).

## Confirm HR7 stays static-only

1. Inspect the HR7 rule module: confirm it imports no database driver, opens no
   connection, and never depends on the `db` extra or a DSN (SC-004).
2. Inspect HR7's Finding/pass message text and the `docs/readiness/gold-ready.md`
   doc update: confirm neither states or implies that a passing declaration or an
   HR7 pass proves a live rerun would in fact be duplicate-free -- that proof stays
   with the existing RC2 (grain/PK uniqueness) and RC16 (penny-exact reconciliation)
   live checks under `retail validate`, which HR7 does not alter (US3).

## Confirm the wiring / count

1. Run the rule-wiring unit tests: `test_rules_wiring.py` (HR7 is in
   `EXPECTED_RULE_IDS`), `test_wiring_meta_gate.py` (C1-C7 all pass: package
   symmetry, id/manifest/posture lockstep, no duplicate registration, registry not
   vacuous), and `test_glossary_rule_table.py` (HR7 has a row in
   `docs/glossary.md`'s "Static check rules" table).
2. Confirm `docs/rules/rules-manifest.json` and `docs/rules/severity-posture.json`
   both carry an `HR7` entry with severity `ERROR`, and
   `docs/quality/rule-count-claims.yaml` is reconciled to the new live count
   (SC-005).

## Author a real declaration for a future incremental load (guidance, not built here)

When a table genuinely outgrows a full nightly rebuild, an author facing HR7's
ERROR Finding has two ways to clear it:

- Add a single-line `-- reload-strategy: <key1>, <key2>` comment to the migration's
  own header, naming the dedup/overwrite key the load uses; or
- Create (or append to) `warehouse/load-policy.md`, naming the migration filename,
  the target table, and the same `reload-strategy:` marker.

Neither action is performed by this feature -- `warehouse/load-policy.md` does not
exist on the current tree and is not created here (see research.md's Landing
analysis). Whether moving a table to an incremental strategy itself needs a
named-human sign-off is the OPEN Q-APPROVAL-SEAM question (FR-013); an author facing
that question stops and raises it rather than deciding it alone.

## What HR7 never does

- Never executes a reload, opens a database connection, or depends on a DSN or the
  `db` extra (Principle VIII, FR-007/FR-010).
- Never proves a rerun is actually duplicate-free -- only that a key is declared and
  structurally plausible (FR-008/FR-009).
- Never re-decides a table's grain or primary key (FR-011; that is Mapping Ready's/
  HR1's territory).
- Never emits a numeric confidence/health/idempotency score or an "N of M"
  completeness count (hard rule #9, FR-012).
- Never accepts or requires a `source-map.yaml` key for the declaration
  (collision-avoidance allocation, FR-004).
- Never self-grants a Gold Ready `pass`, and never rules on the OPEN Q-APPROVAL-SEAM
  question (FR-013) on an owner's behalf.
