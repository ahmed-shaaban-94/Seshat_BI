# Milestone M2 Report — Git-Metadata Rules

**Date:** 2026-06-24
**Branch:** spec/pbi-governance-layer

---

## Summary

All 8 M2 rules implemented, tested, and committed. Full unit suite: **66 passed, 0 failed**.

---

## Files Created / Modified

| File | Action |
|---|---|
| `src/retail/gitutil.py` | Created — git subprocess helpers |
| `src/retail/rules/git_meta.py` | Replaced stub — all 8 rules |
| `tests/unit/_gitfix.py` | Created — shared git repo fixture helpers |
| `tests/unit/test_git_meta.py` | Created — 29 unit tests |

---

## Per-Rule Status

### M2.1 — gitutil helpers
- `git_output`, `git_check_ignore`, `git_log_subjects` implemented in `src/retail/gitutil.py`.
- Fixture helpers `make_git_repo`, `commit_all`, `context_for` in `tests/unit/_gitfix.py`.
- Test: `test_git_check_ignore_respects_gitignore` — PASSED.

### M2.2 — G5: Windows MAX_PATH discipline
- Rule: `rule_g5_path_length` — flags `tracked_files` paths > 200 chars.
- Tests: `test_g5_flags_long_path`, `test_g5_passes_short_paths` — PASSED.

### M2.3 — P1: Approach-A layout
- Rule: `rule_p1_layout` — checks required dirs, PBIP under `powerbi/`, SQL under `warehouse/`.
- Tests: `test_p1_accepts_good_layout`, `test_p1_flags_misplaced_sql_and_pbip`, `test_p1_flags_missing_required_dir` — PASSED.

### M2.4 — G1: .gitignore correctness
- Rule: `rule_g1_gitignore_correctness` — must-contain subset check + `git check-ignore` on definition probe paths.
- Tests: `test_g1_accepts_correct_gitignore`, `test_g1_flags_missing_required_entry`, `test_g1_flags_ignored_definition_path` — PASSED.

### M2.5 — G2: definition artifacts committed
- Rule: `rule_g2_definition_committed` — INFO when no PBIP present; ERROR for tracked `.pbi/cache.abf`.
- Tests: `test_g2_emits_info_when_no_pbip`, `test_g2_flags_tracked_cache_abf` — PASSED.

### M2.6 — P2: commit-message convention
- Rule: `rule_p2_commit_subjects` — three modes: commit_message, commit_range, fallback HEAD~20.
- Tests: `test_p2_flags_bad_subject`, `test_p2_validates_single_commit_message`, `test_p2_exempts_merge_commits` — PASSED.

### M2.7 — C2: no committed secrets
- Rule: `rule_c2_no_committed_secrets` — .env gitignored/untracked, .env.example keys, content scan.
- Tests (6): `test_c2_clean_repo_passes`, `test_c2_flags_real_endpoint_in_scanned_file`, `test_c2_ignores_angle_bracket_placeholder_in_scanned_file`, `test_c2_skips_docs_and_example_files`, `test_c2_flags_tracked_env`, `test_c2_flags_env_example_with_filled_secret` — ALL PASSED.
- Key behavior: angle-bracket placeholders `<your-db-host>.db.ondigitalocean.com` do NOT fire; `docs/` and `*.example` files excluded from content scan.

### M2.G3 — G3: UTF-8 without BOM
- Rule: `g3_no_bom` — reads first 3 bytes of `*.tmdl/*.pbir/*.json/*.pbism`; flags EF BB BF.
- Helper: `_read_leading_bytes(path, count=3)` — binary read, never decodes.
- Tests (5): `test_read_leading_bytes_returns_first_three_bytes`, `test_read_leading_bytes_short_file_returns_fewer`, `test_g3_flags_tmdl_with_bom`, `test_g3_passes_tmdl_without_bom`, `test_g3_ignores_non_target_extension_with_bom` — PASSED.

### M2.G4 — G4: .gitattributes EOL policy
- Rule: `check_gitattributes_eol` — subset check, exact first-token match, 10 required glob/attribute pairs.
- Tests (4): `test_g4_passes_when_all_required_mappings_present`, `test_g4_flags_missing_tmdl_crlf`, `test_g4_flags_contradicting_token_with_line_locator`, `test_g4_flags_all_when_file_absent` — PASSED.
- Note: Brief states 11 findings when file absent but lists 10 required globs. Implementation has 10 `_G4_REQUIRED` entries; test asserts 10 — consistent.

---

## Full pytest Output (unit suite)

```
66 passed in 4.51s

Name                           Stmts   Miss  Cover
--------------------------------------------------
src\retail\rules\git_meta.py     160      7    96%
src\retail\gitutil.py             18      2    89%
(total)                          288     10    97%
```

---

## ruff + black Output

```
ruff check src tests         -> All checks passed!
black --check src tests      -> 21 files would be left unchanged.
                               (Warning: Python 3.13 parsing Python 3.14 target — benign)
```

---

## `retail check --repo .` Output on This Repo

```
[error] P1 PBIP artifact must live under powerbi/ (tests/fixtures/golden_pbip/RetailGold.Report/definition.pbir)
[error] P1 PBIP artifact must live under powerbi/ (tests/fixtures/golden_pbip/RetailGold.SemanticModel/definition/model.tmdl)
[error] P1 PBIP artifact must live under powerbi/ (tests/fixtures/golden_pbip/RetailGold.SemanticModel/definition/relationships.tmdl)
[error] P1 PBIP artifact must live under powerbi/ (tests/fixtures/golden_pbip/RetailGold.pbip)
[error] P2 commit subject must match '<type>: <desc>' (feat|fix|refactor|docs|chore) (test: add hand-authored golden PBIP fixture and TMDL parser smoke test)
```

**Expected / legitimate findings:** The M0 golden fixture at `tests/fixtures/golden_pbip/` is intentionally placed outside `powerbi/` (it is a test fixture, not a live model). The P2 finding is a pre-M2 commit on the branch that used `test:` as a type (not in the allowed set). These will be reconciled in M8 per the brief.

---

## Commit SHAs

| SHA | Message |
|---|---|
| `f93332e` | feat: add git subprocess helper for git-metadata rules |
| `1999e54` | feat: add G5 path-length rule, P1 Approach-A layout rule |

(All 8 rules are in `1999e54`; gitutil/fixtures in `f93332e`.)

---

## Registry Verification

```python
>>> import retail.rules; from retail.registry import all_rules
>>> [r.id for r in all_rules()]
['G5', 'P1', 'G1', 'G2', 'P2', 'C2', 'G3', 'G4']
```

All 8 git-meta rule IDs present in `all_rules()`.

---

## Concerns / Notes

1. **G4 required-count discrepancy:** The brief prose says 11 findings for absent `.gitattributes`; the implementation code has 10 `_G4_REQUIRED` entries. Test asserts 10 (consistent with implementation). The brief's table has 10 rows — the "11" in the prose appears to be a typo.

2. **Black Python 3.14 warning:** `black --check` emits a warning about Python 3.13 vs. 3.14 target version. All files pass; this is a version-mismatch warning, not a failure.

3. **P2 fallback range:** `DEFAULT_BASE_REF = "HEAD~20"` — on a repo with fewer than 20 commits, git returns `fatal: bad revision 'HEAD~20..HEAD'` silently via the `git_log_subjects` function (git returns an empty list). This is safe — no crash — but the local fallback will silently no-op on shallow repos. Acceptable per spec.
