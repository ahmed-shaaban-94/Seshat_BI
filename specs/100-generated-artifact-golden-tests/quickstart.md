# Quickstart: Golden/Regression Tests for Generated DAX & SQL

**Feature**: `100-generated-artifact-golden-tests` | **Date**: 2026-07-04

This walks through exercising the feature once built: running the golden tests, reading a
failure, and refreshing a golden fixture after an intentional change. No database, no network,
no Power BI surface is required for any step below (Principle VIII; SC-003).

## 1. Run the golden/regression tests

```bash
pytest -m unit tests/unit/test_dax_golden.py tests/unit/test_warehouse_sql_golden.py -v
```

Expected on a clean checkout: all tests PASS. This establishes the baseline (User Story 1 and 2's
"Independent Test" starting point).

To run everything this feature touches alongside the neighbouring, UNCHANGED tests it must not
break:

```bash
pytest -m unit tests/unit/test_dax_gen.py tests/unit/test_sql.py tests/unit/test_dax.py \
  tests/unit/test_dax_golden.py tests/unit/test_warehouse_sql_golden.py -v
```

## 2. Confirm the DAX generator's stability is actually pinned (User Story 1)

Make a LOCAL, UNCOMMITTED one-character edit to `src/retail/dax_gen.py`'s emission logic (for
example, change the separator in `_emit_ratio`'s `DIVIDE(...)` join from `", "` to `","`), then:

```bash
pytest -m unit tests/unit/test_dax_golden.py -v
```

Expected: the golden test for the affected fixture FAILS with a diff showing the changed
character, naming which golden file (`<stem>.dax.txt` or `<stem>.tmdl.txt`) no longer matches.
Meanwhile:

```bash
pytest -m unit tests/unit/test_dax_gen.py -v
```

still PASSES (`test_generate_roundtrips_to_pass` only checks that the output re-verifies as
`pass`, which a whitespace/separator change does not break) -- demonstrating SC-001: a change
invisible to the existing round-trip test is caught here. Revert the local edit afterward
(`git checkout -- src/retail/dax_gen.py`) since it was never meant to be committed.

## 3. Confirm the SQL regression lock actually fires (User Story 2)

Make a LOCAL, UNCOMMITTED one-line edit to either exemplar migration, e.g.:

```bash
# (illustrative; do not commit this)
# add a stray comment line to warehouse/migrations/0003_create_silver_retail_store_sales.sql
```

Then:

```bash
pytest -m unit tests/unit/test_warehouse_sql_golden.py -v
```

Expected: the test FAILS, naming the migration file and the differing line(s) against
`tests/fixtures/golden/sql/0003_create_silver_retail_store_sales.sql` -- demonstrating SC-002.
Revert the local edit afterward.

## 4. Confirm a missing golden fails closed, never skips (FR-007)

```bash
# illustrative -- do not do this on a real checkout you intend to keep
mv tests/fixtures/golden/dax/base_revenue.dax.txt /tmp/base_revenue.dax.txt.bak
pytest -m unit tests/unit/test_dax_golden.py -v
# restore it immediately:
mv /tmp/base_revenue.dax.txt.bak tests/fixtures/golden/dax/base_revenue.dax.txt
```

Expected: an explicit test FAILURE naming the missing path (e.g. "golden file not found:
tests/fixtures/golden/dax/base_revenue.dax.txt") -- never a `pytest.skip`, never a silent pass.

## 5. Refresh the DAX/TMDL goldens after an INTENTIONAL emission change (User Story 3)

After landing a deliberate, reviewed change to `dax_gen.py`'s emission format (a real commit,
not the throwaway edits above):

```bash
python tests/fixtures/golden/regenerate_dax_golden.py
git diff tests/fixtures/golden/dax/
```

Review the diff -- it should show exactly the expected textual change and nothing else (no
contract fixture, no source file, no unrelated golden file touched). Then re-run the golden
tests to confirm they pass again with the refreshed fixtures:

```bash
pytest -m unit tests/unit/test_dax_golden.py -v
```

Stage and commit the refreshed golden files yourself; the regeneration script never commits on
your behalf, never runs inside `pytest`, and is never invoked by CI (FR-008).

There is no equivalent script for the SQL golden fixtures. If a migration file changes
intentionally, hand-copy its new text into the paired file under `tests/fixtures/golden/sql/` in
the SAME commit, then re-run step 1 to confirm the lock is green again.

## 6. Confirm this feature added no `retail check` rule (SC-005)

```bash
retail manifest --help >/dev/null 2>&1 || true   # (if such a flag exists; else just re-generate)
retail manifest
git diff docs/rules/rules-manifest.json docs/rules/severity-posture.json
```

Expected: no diff. This feature registers no `@register` rule and touches neither generated
file.

## 7. Confirm no live surface is required (Principle VIII / SC-003)

```bash
# Unset every DB-related env var this repo recognizes, then re-run:
env -u ANALYTICS_DB_ENGINE -u DATABASE_URL -u POSTGRES_DSN \
  pytest -m unit tests/unit/test_dax_golden.py tests/unit/test_warehouse_sql_golden.py -v
```

Expected: identical PASS result to step 1 -- these tests never read an environment variable and
never attempt a connection.
