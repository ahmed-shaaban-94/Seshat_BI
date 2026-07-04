# Data Model: Golden/Regression Tests for Generated DAX & SQL

**Feature**: `100-generated-artifact-golden-tests` | **Date**: 2026-07-04

This feature introduces no database table, no new Python class, and no `retail check` rule
entity. Its "data model" is entirely the shape of committed text/YAML fixture files and the
in-memory comparison each test performs over them. Every shape below is GENERIC (Principle VII):
none carries a hardcoded expectation of any DOMAIN beyond citing the C086 `retail_store_sales`
instance already committed elsewhere in the repo, per FR-010.

## Entity: Golden DAX/TMDL fixture pair

A committed pair of small text files pinning what `generate_measure` is expected to emit for
one SUCCESS-case metric-contract fixture.

| Field | Shape | Notes |
|---|---|---|
| Contract fixture stem | e.g. `base_revenue`, `ratio_disc` | Derived from the existing filename under `tests/fixtures/contracts/<stem>.yaml`; this feature does not rename or add a contract fixture. |
| DAX golden file | `tests/fixtures/golden/dax/<stem>.dax.txt` | Raw text: exactly the `GenResult.dax` string `generate_measure(...)` returns for this contract, newline-normalized per FR-006, with a single trailing newline. |
| TMDL golden file | `tests/fixtures/golden/dax/<stem>.tmdl.txt` | Raw text: exactly the `GenResult.tmdl_block` string, same normalization. |

**Comparison rule**: for each `<stem>` in the fixed corpus (`base_revenue`, `ratio_disc`), the
test:

1. Loads the contract via `load_contract("tests/fixtures/contracts/<stem>.yaml")`.
2. Calls `generate_measure(contract.get("definition") or {}, name=contract.get("name"),
   doc_intent=contract.get("formula_intent"))` -- the exact `_run_generate` call shape (no
   `format_string`/`display_folder` override).
3. Asserts `result.ok is True` (a precondition failure here is a distinct, clearer test failure
   than a golden-mismatch failure).
4. Reads the two golden files; if either is missing/unreadable, fails explicitly naming the path
   (FR-007) -- never a skip, never a pass-by-default.
5. Normalizes both the actual (`result.dax` / `result.tmdl_block`) and golden text per FR-006
   (`\r\n` -> `\n`, strip at most one trailing `\n` on each side) and asserts exact string
   equality, reporting a diff on mismatch.

## Entity: Golden refusal fixture

A committed single text file pinning the exact refusal `reason` string for one REFUSAL-case
metric-contract fixture.

| Field | Shape | Notes |
|---|---|---|
| Contract fixture stem | `refuse_no_column` (the fixed corpus's one refusal case) | Existing file, unmodified. |
| Reason golden file | `tests/fixtures/golden/dax/<stem>.reason.txt` | Raw text: exactly the `GenResult.reason` string, same FR-006 normalization, single trailing newline. |

**Comparison rule**: identical call shape as above; asserts `result.ok is False`, `result.dax is
None`, `result.tmdl_block is None` (mirroring the invariants `GenResult.__post_init__` already
enforces in `dax_gen.py`), then compares the normalized `result.reason` string to the normalized
golden file content, failing with a diff on mismatch and failing explicitly (never skipping) if
the golden file is missing.

**Explicitly out of this entity's scope**: `GenResult.warnings` (a `tuple[str, ...]`) is NOT
pinned by any golden fixture in this feature -- see research.md's rationale (unrelated source of
flakiness; not needed to satisfy SC-001/SC-002).

## Entity: Golden SQL fixture

A committed byte-for-byte (post-normalization) copy of one already-committed exemplar warehouse
migration file, used as the regression-lock baseline for User Story 2.

| Field | Shape | Notes |
|---|---|---|
| Source migration path | `warehouse/migrations/0003_create_silver_retail_store_sales.sql` or `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` | Existing files, read-only input; never edited by this feature. |
| Golden copy path | `tests/fixtures/golden/sql/<same filename>` | Same basename as the migration it locks -- e.g. `tests/fixtures/golden/sql/0003_create_silver_retail_store_sales.sql` -- so the pairing is obvious from the filename alone, no manifest needed. |

**Comparison rule**: for each of the two `(migration path, golden path)` pairs, the test reads
both files as UTF-8 text; if either is missing/unreadable, fails explicitly naming the path
(FR-007). It normalizes both per FR-006 and asserts exact string equality, reporting which file
and which normalized lines differ on mismatch. The test opens no database connection, invokes no
CLI, and calls no skill (FR-004's own text; SCOPE GUARD).

## Entity: Regeneration helper (optional, FR-008)

Not a data shape so much as a described SIDE EFFECT boundary -- included here because it is the
one place this feature COULD mutate a committed file, and its boundary must be exact.

| Property | Value |
|---|---|
| Location | `tests/fixtures/golden/regenerate_dax_golden.py` |
| Invocation | Manual only: `python tests/fixtures/golden/regenerate_dax_golden.py` |
| Reads | The same three contract fixtures under `tests/fixtures/contracts/` this feature's tests read. |
| Writes | ONLY the DAX/TMDL/reason golden files under `tests/fixtures/golden/dax/` this feature defines above -- never a contract fixture, never a golden SQL file, never any file under `src/` or `warehouse/`. |
| MUST NOT | Run as part of `pytest` collection or execution; run as part of `retail check`; be invoked by any CI workflow step; commit anything on the contributor's behalf. |
| Review mechanism | The contributor runs it locally, then inspects `git diff` before staging/committing -- the script itself asserts nothing and returns no pass/fail signal. |

There is no equivalent regeneration helper for the SQL golden fixtures in this feature: FR-008
scopes the (optional) helper to the DAX/TMDL/reason goldens only. A SQL golden is refreshed by a
contributor manually copying the (intentionally changed) migration file's new text into its
paired golden file, in the SAME commit as the intentional migration edit (per the spec's Edge
Cases section) -- no script is warranted for a two-file, rarely-changing pair.

## Relationships

```text
tests/fixtures/contracts/<stem>.yaml  --(generate_measure via CLI call shape)-->  GenResult
                                                                                     |
                                                          dax, tmdl_block, reason    |
                                                                                     v
tests/fixtures/golden/dax/<stem>.{dax,tmdl,reason}.txt  <--(FR-006 compare)--  (in-memory result)

warehouse/migrations/000{3,4}_*.sql  <--(FR-006 compare)-->  tests/fixtures/golden/sql/000{3,4}_*.sql
```

No entity in this feature has a lifecycle beyond "committed, read, compared." None is created,
updated, or deleted by any test at test-run time; the only writer of any golden file is a human
running the optional regeneration script (DAX/TMDL/reason) or hand-editing a golden SQL copy
(deliberately, in the same commit as an intentional migration change).
