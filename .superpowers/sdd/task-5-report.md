## Task 5 Report — generate_measure pipeline + TMDL builder + round-trip property

### What was done

Implemented the three functions specified in the brief, with two deviations from the verbatim spec that were required for correctness:

**Files changed:**
- `src/retail/dax_gen.py` — added `_default_format`, `_build_tmdl_block`, `_run_d_rules`, `generate_measure`
- `tests/unit/test_dax_gen.py` — added 6 new tests (round-trip x2, D-rule cleanliness, refusals x2, doc_intent isolation)

**Deviation 1: `RATIO_DISC` in tests gets `"additive": False`**
The brief's verbatim `RATIO_DISC` omits `additive`. `check_measure_drift` for a non-base kind falls to the legacy ratio path, which at line 335 does `if definition.get("additive") is not False: return Verdict("escalate", ...)`. With `additive` absent, `None is not False` triggers escalate, making the ratio round-trip fail. Adding `"additive": False` allows the denominator filter-set comparison to proceed and return `pass`. This is the only way the headline property can hold without modifying metric_drift.

**Deviation 2: `_run_d_rules` drops the `measure stub = 0` wrapper**
The brief's template wraps the generated block in `table T\n\tmeasure stub = 0\n\n{_indent_measure(tmdl_block)}`. "stub" is lowercase, triggering a D1 ERROR; it also lacks a displayFolder, triggering D2 ERROR. Both cause every `generate_measure` call to refuse. The fix: `table_text = f"table T\n{tmdl_block}"` — `parse_tmdl` finds a measure at indent-1 without a stub.

**TMDL structure adjustment:**
`_build_tmdl_block` emits lines already indented with one tab (indent-1), so `table T\n{tmdl_block}` produces the correct nesting without an `_indent_measure` call. The `///` doc comment at indent-1 is immediately above the `measure Name = ...` line at indent-1, and `formatString`/`displayFolder` are at indent-2 — matching what `parse_tmdl` and D11 expect (as confirmed by `clean_with_doc.tmdl`).

### Test results

**Targeted tests (`-k "generate or doc_intent"`):**
```
6 passed in 0.34s
```
- test_generate_roundtrips_to_pass[TotalRevenue-defn0] PASSED
- test_generate_roundtrips_to_pass[DiscountedRate-defn1] PASSED
- test_generated_tmdl_passes_d_rules PASSED
- test_generate_refuses_unknown_kind PASSED
- test_generate_refuses_bad_pascalcase_name PASSED
- test_doc_intent_isolation_same_dax_diff_comment PASSED

**Full suite (`-m unit`):**
```
378 passed in 9.39s
```
Zero regressions.

### Commit hash
`28cb702`

### Concerns
None. The two deviations from the verbatim brief were forced by the immutable verifier's existing behaviour; both are the minimal correct fixes. The headline round-trip property holds for both base and ratio measures.

---

## Task 5 Spec-Gap Fix — kind:ratio implies non-additive

### What was done

Closed the spec-compliance gap identified in review: `kind: ratio` now implies `additive: false` in `check_measure_drift`, so callers need not restate it.

**Files changed:**
- `src/retail/metric_drift.py` — added a shallow-copy normalization in `check_measure_drift` immediately after the `kind == "base"` dispatch: if the definition has `kind: ratio` and `additive` is absent, `definition` is replaced with `{**definition, "additive": False}`. The caller's dict is never mutated. Explicit `additive: true` is still respected (escalates as before).
- `tests/unit/test_dax_gen.py` — removed `"additive": False` from the `RATIO_DISC` fixture so the round-trip test now proves the canonical ratio shape (kind:ratio WITHOUT additive).
- `tests/unit/test_metric_drift.py` — added two focused tests: `test_kind_ratio_without_additive_treated_nonadditive` (kind:ratio without `additive` returns `pass`) and `test_kind_ratio_explicit_additive_true_still_escalates` (explicit `additive: true` still escalates).

### Covering-test command and full output

Command: `python -m pytest tests/unit/test_metric_drift.py tests/unit/test_dax_gen.py -v`

```
============================= test session starts =============================
platform win32 -- Python 3.13.12, pytest-8.4.2, pluggy-1.6.0
collected 52 items

tests/unit/test_metric_drift.py::test_shipped_discounted_rate_passes PASSED
tests/unit/test_metric_drift.py::test_shipped_avg_transaction_value_passes PASSED
tests/unit/test_metric_drift.py::test_all_transactions_denominator_is_drift PASSED
tests/unit/test_metric_drift.py::test_wrong_column_denominator_is_drift PASSED
tests/unit/test_metric_drift.py::test_empty_calculate_wrapper_normalizes_to_drift PASSED
tests/unit/test_metric_drift.py::test_unrecognized_predicate_escalates PASSED
tests/unit/test_metric_drift.py::test_is_not_null_via_ne_blank_passes PASSED
tests/unit/test_metric_drift.py::test_is_not_null_via_isblank_eq_false_passes PASSED
tests/unit/test_metric_drift.py::test_is_true_via_true_eq_col_passes PASSED
tests/unit/test_metric_drift.py::test_is_true_via_ne_false_passes PASSED
tests/unit/test_metric_drift.py::test_non_divide_measure_escalates PASSED
tests/unit/test_metric_drift.py::test_unparseable_unbalanced_parens_escalates PASSED
tests/unit/test_metric_drift.py::test_additive_measure_escalates PASSED
tests/unit/test_metric_drift.py::test_missing_additive_flag_escalates PASSED
tests/unit/test_metric_drift.py::test_contract_without_definition_block_skips PASSED
tests/unit/test_metric_drift.py::test_verdict_has_status_and_detail PASSED
tests/unit/test_metric_drift.py::test_metric_drift_module_does_not_import_yaml_at_top_level PASSED
tests/unit/test_metric_drift.py::test_importing_retail_rules_does_not_pull_metric_drift PASSED
tests/unit/test_metric_drift.py::test_three_arg_divide_is_checked_not_escalated PASSED
tests/unit/test_metric_drift.py::test_three_arg_divide_still_detects_drift PASSED
tests/unit/test_metric_drift.py::test_four_arg_divide_still_escalates PASSED
tests/unit/test_metric_drift.py::test_base_pass_matches_contract PASSED
tests/unit/test_metric_drift.py::test_base_pass_with_filter PASSED
tests/unit/test_metric_drift.py::test_base_drift_wrong_filter_column PASSED
tests/unit/test_metric_drift.py::test_base_drift_missing_filter PASSED
tests/unit/test_metric_drift.py::test_base_drift_wrong_aggregation PASSED
tests/unit/test_metric_drift.py::test_base_escalate_unrecognized_shape PASSED
tests/unit/test_metric_drift.py::test_base_escalate_unknown_predicate PASSED
tests/unit/test_metric_drift.py::test_kind_absent_ratio_path_unchanged PASSED
tests/unit/test_metric_drift.py::test_aggregation_unread_on_kind_absent_path PASSED
tests/unit/test_metric_drift.py::test_kind_ratio_without_additive_treated_nonadditive PASSED
tests/unit/test_metric_drift.py::test_kind_ratio_explicit_additive_true_still_escalates PASSED
tests/unit/test_dax_gen.py::test_genresult_success_populates_outputs_only PASSED
tests/unit/test_dax_gen.py::test_genresult_refuse_has_none_outputs PASSED
tests/unit/test_dax_gen.py::test_genresult_rejects_ok_without_dax PASSED
tests/unit/test_dax_gen.py::test_genresult_rejects_refusal_with_dax PASSED
tests/unit/test_dax_gen.py::test_emit_base_sum_no_filter PASSED
tests/unit/test_dax_gen.py::test_emit_base_count_rows_no_column PASSED
tests/unit/test_dax_gen.py::test_emit_base_with_filter_wraps_calculate PASSED
tests/unit/test_dax_gen.py::test_emit_base_sum_without_column_refuses PASSED
tests/unit/test_dax_gen.py::test_emit_base_count_rows_with_column_refuses PASSED
tests/unit/test_dax_gen.py::test_emit_base_non_gold_table_refuses PASSED
tests/unit/test_dax_gen.py::test_emit_base_unknown_aggregation_refuses PASSED
tests/unit/test_dax_gen.py::test_emit_base_unknown_filter_op_refuses PASSED
tests/unit/test_dax_gen.py::test_generate_roundtrips_to_pass[TotalRevenue-defn0] PASSED
tests/unit/test_dax_gen.py::test_generate_roundtrips_to_pass[DiscountedRate-defn1] PASSED
tests/unit/test_dax_gen.py::test_generated_tmdl_passes_d_rules PASSED
tests/unit/test_dax_gen.py::test_generate_refuses_unknown_kind PASSED
tests/unit/test_dax_gen.py::test_generate_refuses_bad_pascalcase_name PASSED
tests/unit/test_dax_gen.py::test_doc_intent_isolation_same_dax_diff_comment PASSED
tests/unit/test_dax_gen.py::test_emit_ratio_inline_count_rows PASSED
tests/unit/test_dax_gen.py::test_emit_ratio_refuses_bad_side PASSED

52 passed in 0.78s
```

Full suite command: `python -m pytest -m unit -q`

```
380 passed in 9.98s
```

(378 existing + 2 new tests; zero regressions)

Kind-absent regression tests: `test_kind_absent_ratio_path_unchanged` and `test_aggregation_unread_on_kind_absent_path` both PASSED.

### Commit hash
`0cfcff2`

---

## Task 5 Report — CLI handler + parser + dispatch wiring (`retail dashboard` verb)

NOTE: This section documents a DIFFERENT "Task 5" (per `.superpowers/sdd/task-5-brief.md`,
dashboard CLI wiring), unrelated to the dax_gen work recorded above. The two
tasks happen to share the file name `task-5-report.md` in this scratch
directory; this section was appended rather than overwriting prior history.

### Status: DONE

### Commit
`36951df94631b19edbc71feb566a333f1024891a` — "feat: retail dashboard CLI verb (write + auto-open static HTML)"

### What was implemented

Followed the brief's 5 steps exactly (TDD: RED -> GREEN -> commit):

1. **Test file** `tests/unit/test_dashboard_cli.py` — written verbatim from the
   brief's Step 1, with ONE deliberate deviation per the known plan slip #1:
   all imports placed FIRST, then `pytestmark = pytest.mark.unit` AFTER the
   imports (repo convention / ruff E402 compliance), instead of the
   mid-import placement shown in the brief's code block.

2. **RED confirmed**: `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_cli.py -v`
   failed with `ModuleNotFoundError: No module named 'seshat.cli.commands.dashboard'`
   as expected.

3. **Implementation** (Step 3, verbatim from brief):
   - Created `src/seshat/cli/commands/dashboard.py` — `dashboard_main(args)`:
     lazily imports `generate` from `seshat.dashboard.generate` and (only on
     the open-browser branch) lazily imports `webbrowser`. No module-scope
     import of `generate` or `webbrowser`. Catches `OSError` from `generate`,
     prints an ASCII-only error, returns 1; otherwise prints the written path
     and returns 0.
   - Modified `src/seshat/cli/parser.py`: added `_add_dashboard_parser(sub)`
     immediately after `_add_status_parser` (registers `--repo`, `--out`,
     `--no-open`/`dest="no_open"`), and added the call
     `_add_dashboard_parser(sub)` in `_build_parser` immediately after
     `_add_status_parser(sub)` (was line 1097; now followed by the new call).
   - Modified `src/seshat/cli/__init__.py`: added
     `"dashboard": _lazy(".commands.dashboard", "dashboard_main"),` to
     `_DISPATCH`, immediately after the `"status"` row, matching the existing
     `_lazy(...)` style exactly.

4. **GREEN confirmed**: `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_cli.py -v`
   -> 4 passed (parser registration, write+return-0, OSError->1, dispatch row
   present).

5. **Committed** the 4 files listed in the brief's Step 5 (test file, new
   handler, parser.py, cli/__init__.py).

### Verification gates

- **pytest**: `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_cli.py -v`
  -> **4 passed**.
- **ruff**: `ruff check src tests scripts` -> **All checks passed!** (no new
  ignores added; no line-length reflow was needed — all new lines were
  already <=88 chars).
- **retail check (B1 gate)**: `PYTHONPATH=src python -m seshat.cli check --repo . --format json`
  -> `{"findings": [], "exit_code": 0}` — **no B1 finding** on
  `src/seshat/cli/commands/dashboard.py` or any other file.

#### B1 scan-coverage negative control (extra verification, not in the brief)

The advisor flagged a real gap: B1's rule (`check_no_module_scope_execution_imports`
in `src/seshat/rules/never_execute.py`) iterates `ctx.tracked_files`, which is
populated by `git ls-files` (`src/seshat/runner.py::_git_ls_files`) — i.e. the
git index, NOT a filesystem walk. Immediately after creating `dashboard.py` it
was untracked, so an initial "0 findings" run would have been a **file-not-
scanned** false negative, not a true confirmation.

To close that gap:
1. Staged all 4 files (`git add ...`) so `dashboard.py` entered the git index
   and `git ls-files` (confirmed directly) listed
   `src/seshat/cli/commands/dashboard.py`.
2. **Negative control**: temporarily added `import socket` at module scope in
   `dashboard.py`, re-staged, and re-ran `retail check --repo . --format
   json`. Result: **B1 fired** —
   `{"rule_id": "B1", "message": "module-scope import of 'socket' ...",
   "locator": "src/seshat/cli/commands/dashboard.py"}`, exit code 1. This
   proves the gate genuinely parses and evaluates this file.
3. Reverted the temporary `import socket` line, re-staged, and re-ran all
   three gates (retail check, ruff, pytest) — all clean/passing (see above).
4. Committed the clean state.

This makes the "no B1 finding" claim a verified true negative, not an
artifact of the scanner skipping an untracked file.

### Concerns

None. The only deviation from the brief's literal code (test-file import
ordering) was an explicitly pre-authorized "known plan slip" (#1 in the task
instructions), applied without asking as instructed.

---

### Fix note — review Minor: cover the webbrowser branch (B1-critical behavior)

Review passed (Spec, quality Approved) with one Minor: no test exercised the
`webbrowser.open` branch, so a future edit that un-gated the lazy import to
module scope would pass silently (no test would catch it going module-scope
or being called when it shouldn't be).

**What was added** to `tests/unit/test_dashboard_cli.py` (imports stayed at
top, `pytestmark` stayed last — unchanged from before):

1. `test_no_open_does_not_open_browser` — `monkeypatch.setattr("webbrowser.open", ...)`
   with a spy appending to a `calls` list; calls `dashboard_main` with
   `no_open=True`; asserts `rc == 0`, the output file exists, and `calls == []`
   (browser never invoked).
2. `test_open_branch_opens_file_uri` — same spy pattern; calls `dashboard_main`
   with `no_open=False`; asserts `rc == 0`, the spy was called exactly once,
   and the argument starts with `"file:"` (the `.as_uri()` of the written
   path). Hermetic — no real browser launches since `webbrowser.open` is
   mocked.

**How the monkeypatch resolved the lazy import:** `monkeypatch.setattr(
"webbrowser.open", spy)` patches the `open` attribute directly on the
`webbrowser` module object in `sys.modules`. The handler's lazy
`import webbrowser` inside `dashboard_main` does not create a new module — it
binds the SAME cached module object from `sys.modules` (Python only executes
a module's top-level code once, on first import; every subsequent `import
webbrowser` anywhere, including inside a function body, returns that same
object). So `webbrowser.open(...)` called inside the handler resolves to the
already-patched attribute. Verified empirically: both new tests passed on the
first run with no alternate patch target needed — no workaround was
required.

**Verification:**
- `PYTHONPATH=src python -m pytest tests/unit/test_dashboard_cli.py -v` ->
  **6 passed** (previous 4 + the 2 new monkeypatch tests; all PASSED
  individually: `test_parser_registers_dashboard_with_flags`,
  `test_dashboard_main_writes_and_returns_zero`,
  `test_dashboard_main_oserror_returns_one`,
  `test_no_open_does_not_open_browser`, `test_open_branch_opens_file_uri`,
  `test_dispatch_has_dashboard_row`).
- `ruff check src tests scripts` -> **All checks passed!**

**Commit:** (recorded below once created).
