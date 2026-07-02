# Quickstart: Rule-Count Claim Reconciler (SC2)

A TDD-ordered path to build SC2, mirroring how SC1 shipped. RED first, then GREEN.

## Prerequisites

- Read `src/retail/rules/status_claims.py` (SC1) and
  `tests/unit/test_status_claims.py` -- SC2 is a near-clone with the
  artifact-resolution branch replaced by an integer comparison against a committed
  count source.
- Confirm the base rule count: `len(EXPECTED_RULE_IDS)` in
  `tests/unit/test_rules_wiring.py` (call it N). Registering SC2 takes it to N+1.
  Do NOT hardcode N in any authored doc -- read it live.

## Build order (RED -> GREEN)

1. **US1 tests (RED)**: in NEW `tests/unit/test_rule_count_claims.py`, add a
   `_stage(tmp_path, manifest_claims, docs, count_source_len)` helper that writes a
   synthetic `docs/quality/rule-count-claims.yaml`, the named claiming docs
   (containing their anchor text), and a synthetic `docs/rules/rules-manifest.json`
   with `count_source_len` entries, and returns a
   `RuleContext(repo_root=tmp_path, tracked_files=tuple(...))`. Add
   `test_stale_count_fails` (claimed != source, anchor present -> 1 ERROR naming
   both integers) and `test_accurate_count_yields_no_findings` (claimed == source,
   anchor present -> `[]`). Use only GENERIC synthetic paths/anchors.
2. **US1 impl (GREEN)**: create NEW `src/retail/rules/rule_count_claims.py`:
   docstring (names SC1 as the sibling; states stdlib-only / read-only / fail-loud /
   categorical-only / manifest-only / live-state-only); constants
   `_MANIFEST = "docs/quality/rule-count-claims.yaml"` and
   `_COUNT_SOURCE = "docs/rules/rules-manifest.json"`; an `_finding(message,
   locator)` helper emitting `Finding(rule_id="SC2", severity=Severity.ERROR, ...)`;
   and `@register("SC2", "Prose rule-count claims reconcile with the authoritative
   count")` on `check_rule_count_claims(ctx)`. Implement steps 1-3 of the contract
   (manifest guard, parse guard, count-source guard) plus the mismatch comparison
   (step 4e) and the accurate-count no-finding path.
3. **US2 tests (RED)**: add `test_absent_anchor_fails_loud`,
   `test_malformed_count_fails` (missing / non-integer / negative),
   `test_untracked_doc_fails`, and `test_missing_field_fails`.
4. **US2 impl (GREEN)**: complete the per-entry fail-loud branches (contract steps
   4a-4d) BEFORE the comparison. Never fall through to a vacuous empty result on bad
   input.
5. **US3 tests (RED)**: add `test_missing_manifest_fails_loud`,
   `test_malformed_yaml_fails_loud`, `test_wrong_shape_fails_loud`, and
   `test_missing_count_source_fails_loud` (count source untracked/unparseable -> 1
   ERROR).
6. **Wiring**: edit `src/retail/rules/__init__.py` (add `rule_count_claims` to the
   import tuple + `__all__`); add `"SC2"` to `EXPECTED_RULE_IDS` (N -> N+1).
7. **Seed + ship-green**: author `docs/quality/rule-count-claims.yaml` with the one
   glossary count-claim entry; correct the glossary count prose to the POST-SC2
   count (N+1); set the seed entry's `claimed-count` to N+1 so it reconciles clean.
8. **Regenerate goldens**: `retail manifest` (rules-manifest.json now N+1 with SC2)
   and `retail severity-posture` (severity-posture.json now includes SC2); commit
   both.
9. **Live guard test**: add `test_live_manifest_reconciles_against_real_repo`
   (`@pytest.mark.skipif(shutil.which("git") is None)`): shell `git ls-files`, build
   a real `RuleContext`, run `check_rule_count_claims`, assert `[]`.
10. **Roadmap ledger + full gate**: add a roadmap row recording SC2 + N -> N+1; run
    `ruff check .`, `pytest -m unit`, `retail check` (exit 0, N+1 rules), `retail
    semantic-check`.

## Expected end state

- `retail check` passes with exit 0 and N+1 registered rules.
- The wiring/drift test, the golden rule-count manifest snapshot, and the
  severity-posture snapshot all pass.
- The live-guard test confirms the shipped manifest + corrected glossary reconcile
  clean (the glossary claim, its manifest `claimed-count`, and the authoritative
  count are all N+1).
