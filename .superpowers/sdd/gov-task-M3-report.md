# Milestone M3 — Implementation Report

**Date:** 2026-06-24
**Branch:** spec/pbi-governance-layer
**Status:** COMPLETE — all 5 SQL rules implemented, 19 new tests green, 90 total unit tests passing, ruff + black clean, all_rules() = 13.

---

## Per-rule files and tests

### M3.1 — SQL Lexer (`src/retail/sql.py`)

**Files created:**
- `src/retail/sql.py` — `SqlToken`, `tokenize_sql`, `iter_sql_files`, `stale_schema_tokens`
- `tests/unit/test_sql_lexer.py` — 6 tests

**Commit:** `6db02dc` — `feat: add SQL lexer and schema-position matcher for retail check`

**Tests (6):** `test_tokenize_tracks_line_numbers`, `test_tokenize_strips_line_comment`, `test_tokenize_strips_string_literal_contents`, `test_stale_schema_passes_snake_case_column`, `test_stale_schema_flags_create_schema_raw`, `test_stale_schema_flags_qualifier_and_from`

---

### M3.2 — S1 + S2 (`src/retail/rules/sql.py`)

**Files created/modified:**
- `src/retail/rules/sql.py` — added S1 + S2 (replacing the 2-line stub)
- `tests/unit/test_sql.py` — 5 tests
- `tests/fixtures/sql/pass_s1_s2.sql`
- `tests/fixtures/sql/fail_s1_quoted_caps.sql`
- `tests/fixtures/sql/fail_s2_create_schema_raw.sql`

**Commit:** `453c606` — `feat: add S1 snake_case and S2 medallion-schema SQL rules`

**Tests (5):** `test_s1_passes_snake_case`, `test_s1_flags_quoted_caps`, `test_s2_passes_raw_amount_column`, `test_s2_flags_create_schema_raw`, `test_s2_exempts_warehouse_readme`

---

### M3.3 — S3 (`src/retail/rules/sql.py`)

**Files created/modified:**
- `src/retail/rules/sql.py` — appended S3
- `tests/unit/test_sql.py` — 2 additional tests
- `tests/fixtures/sql/pass_s3_vw.sql`
- `tests/fixtures/sql/fail_s3_no_prefix.sql`

**Commit:** `4a8dcf9` — `feat: add S3 vw_ view-prefix SQL rule`

**Tests (2):** `test_s3_passes_prefixed_views`, `test_s3_flags_unprefixed_view`

---

### M3.4 — S4a (`src/retail/rules/sql.py`)

**Files modified:**
- `src/retail/rules/sql.py` — appended S4a
- `tests/unit/test_sql.py` — 4 additional tests

**Commit:** `9440370` — `feat: add S4a migration filename and numbering SQL rule`

**Tests (4):** `test_s4a_passes_contiguous_unique`, `test_s4a_flags_bad_name`, `test_s4a_flags_gap`, `test_s4a_flags_duplicate`

---

### M3.5 — S4b (`src/retail/rules/sql.py`)

**Files created/modified:**
- `src/retail/rules/sql.py` — appended S4b
- `tests/unit/test_sql.py` — 2 additional tests + import consolidation + ruff/black fixes
- `tests/unit/test_sql_lexer.py` — removed unused `SqlToken` import
- `tests/fixtures/sql/pass_s4b_guarded.sql`
- `tests/fixtures/sql/fail_s4b_bare.sql`

**Commit:** `3db9c92` — `feat: add S4b migration guard-form SQL warning rule`

**Tests (2):** `test_s4b_passes_guarded_forms`, `test_s4b_warns_on_bare_create_and_alter`

---

## Full suite output

```
90 passed in 3.74s
```

Coverage:
```
src/retail/rules/sql.py    94%  (6 missed: lines 47, 73, 78, 155-157 — guarded branches not exercised by SQL rule tests)
src/retail/sql.py          94%  (4 missed: lines 41-44 — block-comment newline counting)
```

---

## ruff + black output

```
ruff check src tests   → All checks passed!
black --check src tests → 24 files would be left unchanged.
```

**Ruff fixes applied (not in brief verbatim code, necessary for compliance):**
1. `E501` Line too long in `rules/sql.py` line 110 — the verbatim message string was split across two lines using raw string concatenation.
2. `E402` Module-level imports not at top — the brief appended imports mid-file per TDD step; consolidated all `from retail.rules.sql import ...` into a single import block at the top of `test_sql.py`.
3. `F401` Unused `SqlToken` import in `test_sql_lexer.py` — removed (the verbatim brief imported it but no test used it directly).

---

## all_rules() id list (13 total)

```
['G5', 'P1', 'G1', 'G2', 'P2', 'C2', 'G3', 'G4', 'S1', 'S2', 'S3', 'S4a', 'S4b']
```

8 git-meta (G1, G2, G3, G4, G5, P1, P2, C2) + 5 SQL (S1, S2, S3, S4a, S4b) = 13.

---

## `retail check --repo .` output

```
[error] P2 commit subject must match '<type>: <desc>' (feat|fix|refactor|docs|chore) (test: add hand-authored golden PBIP fixture and TMDL parser smoke test)
```

Exit code: 1 (1 grandfathered P2 error — expected, pre-existing). No S-rule violations fired. The `warehouse/` directory contains only `.gitkeep`, so no real SQL files are scanned by any S-rule.

---

## Commit SHAs (M3 only)

| Commit     | Description                                          |
|------------|------------------------------------------------------|
| `6db02dc`  | feat: add SQL lexer and schema-position matcher      |
| `453c606`  | feat: add S1 snake_case and S2 medallion-schema SQL rules |
| `4a8dcf9`  | feat: add S3 vw_ view-prefix SQL rule                |
| `9440370`  | feat: add S4a migration filename and numbering SQL rule |
| `3db9c92`  | feat: add S4b migration guard-form SQL warning rule  |

---

## tests/ exemption decision

**Decision: no additional skip added.**

The SQL rules all consume `iter_sql_files`, which is positively scoped to `warehouse/**/*.sql`. Real test fixtures live under `tests/fixtures/sql/` — they never start with `warehouse/`, so `iter_sql_files` never returns them. The exemption is already satisfied by construction. This is consistent with the brief's "if the brief already handles this, good" guidance.

The harness-staged copies written by tests into `tests/fixtures/sql/warehouse/` also start with `tests/`, not `warehouse/`, so they too are outside the scope of `iter_sql_files` when running against the real repo via `retail check`. No false positives in `retail check --repo .`.

---

## Concerns

1. **Test-harness writes into the real working tree.** Tests write staged fixture files into `tests/fixtures/sql/warehouse/` via `mkdir`/`write_text` (not `tmp_path`). These files appear as untracked after `pytest` runs. They are under `tests/` so are excluded from all rule scans, but they create noise in `git status`. This is the brief-mandated pattern; refactoring to `tmp_path` would diverge from verbatim code.

2. **Inter-test ordering dependency.** `test_s2_passes_raw_amount_column` relies on `test_s1_passes_snake_case` having already staged `pass_s1_s2.sql`. Works under pytest's default definition order + the file persisting on disk between tests. Not fragile in practice, but a smell.

3. **Black Python 3.14 parse warning.** Black emits `Warning: Python 3.13 cannot parse code formatted for Python 3.14` during `--check`. This is a black version mismatch warning, not an error; all files pass. Acceptable for current machine setup.

4. **`_is_guarded(toks: list, ...)` bare `list` annotation.** This is the verbatim brief code; ruff does not flag it under current config. Left as-is per instruction.
