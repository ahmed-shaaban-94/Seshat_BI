# Quickstart: building SC1 (TDD order)

This pins the RED -> GREEN order for implementation. Mirrors how A1
(`test_routes.py`) and A3 (`test_routes_coverage.py`) were built.

## Prerequisites

- Branch `050-stale-marker-sweep` checked out.
- Read `src/retail/rules/routes.py` (A1) and `tests/unit/test_routes.py` as the
  shape to mirror.
- Confirm `tests/unit/test_rules_wiring.py::EXPECTED_RULE_IDS` holds 35 ids and
  "SC1" is absent.

## Step 1 -- RED: write the unit tests first

In NEW `tests/unit/test_status_claims.py`, add a `_stage(tmp_path, claims, docs,
artifacts)` helper that writes a synthetic `docs/quality/status-claims.yaml`, the
named claiming docs (with their anchor text), and the named artifact files under
`tmp_path`, then returns a real `RuleContext(repo_root=tmp_path,
tracked_files=tuple(...))`. Use only GENERIC synthetic paths/anchors (e.g.
`docs/x.md`, anchor "feature X is planned", artifact `src/x.py`). Then add cases:

- `test_honest_built_yields_no_findings` -- built + artifact tracked + anchor present -> `[]`.
- `test_false_built_fails` -- built + artifact NOT tracked + anchor present -> 1 ERROR.
- `test_honest_planned_yields_no_findings` -- planned + artifact NOT tracked + anchor present -> `[]`.
- `test_stale_planned_marker_fails` -- planned + artifact tracked + anchor present -> 1 ERROR (the seed-defect shape).
- `test_absent_anchor_fails_loud` -- anchor NOT in doc text -> 1 ERROR.
- `test_missing_manifest_fails_loud` -- manifest untracked -> 1 ERROR.
- `test_malformed_yaml_fails_loud` -- manifest text is not valid YAML -> 1 ERROR.
- `test_wrong_shape_fails_loud` -- manifest has no `claims` list -> 1 ERROR.
- `test_invalid_status_fails` -- `claimed-status: shipped` -> 1 ERROR.
- `test_missing_field_fails` -- entry missing `claimed-artifact` -> 1 ERROR.
- `test_untracked_doc_fails` -- `doc` not in tracked set -> 1 ERROR.

Run `pytest -m unit tests/unit/test_status_claims.py` -> all FAIL (module absent). RED.

## Step 2 -- GREEN: implement the rule

Create `src/retail/rules/status_claims.py` per `contracts/sc1-rule-contract.md`:
module docstring (names A1 as the sibling; states stdlib-only / read-only /
fail-loud / categorical-only), `_MANIFEST` constant, `_VALID_STATUS = frozenset({"built","planned"})`,
`_finding(message, locator)` helper emitting `Finding(rule_id="SC1",
severity=Severity.ERROR, ...)`, and `@register("SC1", "...")` on
`check_status_claims(ctx)`. Implement the ordered behavioral contract (manifest
guard -> lazy parse -> shape guard -> per-entry: shape, required fields, status
enum, doc-tracked, anchor-present, artifact resolution).

Run the unit tests -> all PASS. GREEN.

## Step 3 -- wire + count

- Edit `src/retail/rules/__init__.py`: add `status_claims` to the side-effecting
  import tuple and to `__all__` (keep grouping/ordering consistent).
- Edit `tests/unit/test_rules_wiring.py`: add `"SC1"` to `EXPECTED_RULE_IDS` with a
  short comment. Count moves 35 -> 36.
- Run `pytest -m unit tests/unit/test_rules_wiring.py` -> `test_registered_rule_ids_match_expected_set` passes (SC1 present, count 36).

## Step 4 -- seed the manifest AND fix the seeded prose (same change)

- Author `docs/quality/status-claims.yaml` with the one confirmed seed entry: the
  capability-state doc's "(planned)" claim about the shipped Net Sales trace
  (`claimed-status: planned`, `claimed-artifact` = the trace doc). As written this
  entry FAILS (planned + present = stale marker) -- that is the defect SC1 catches.
- Correct the stale wording in `docs/quality/post-idea-bank-capability-state.md`
  so the claim no longer calls the shipped trace "(planned)". Decide whether the
  seed entry then flips to `built` (the trace now correctly described as shipped)
  or the entry is removed -- the manifest must end GREEN. Recommended: flip the
  entry to `built` so SC1 keeps guarding that the trace stays shipped, and the
  anchor is updated to the corrected wording.

## Step 5 -- live guard + full gate

- Add `test_live_manifest_resolves_against_real_repo` mirroring
  `test_routes.py::test_live_manifest_resolves_against_real_repo`:
  `@pytest.mark.skipif(shutil.which("git") is None)`, shell `git ls-files`, build a
  real `RuleContext` over the repo root, run `check_status_claims`, assert `[]`.
  This is the production guard proving the shipped manifest + corrected prose
  reconcile clean.
- Add a roadmap ledger row recording SC1 shipped and 35 -> 36.
- Run the full gate green: `ruff check .`, `pytest -m unit`, `retail check`
  (exit 0, 36 rules), `retail semantic-check`.
- Generic-leak sweep: grep the new rule + test + manifest for any
  pharmacy/C086/billing/segment/PII token; confirm all paths/anchors are generic
  repo-infrastructure paths.
