# Phase 0 Research: Route-Registry Coverage Reconciler (A3)

All findings verified against the repository on branch HEAD before planning.

## R1: Does A1 already cover this? (materially-new check)

- **Decision**: A3 is materially new, not an A1 restatement.
- **Rationale**: `src/retail/rules/routes.py` (A1) reads ONLY
  `docs/routing/routes.yaml` and validates each route target against the tracked
  filesystem. It NEVER reads `docs/knowledge-map.md` (the map is mentioned in A1's
  docstring as prose only; no code touches it). The map<->manifest id-set bijection
  is therefore a genuinely unguarded boundary.
- **Alternatives considered**: Folding the check into A1 -- rejected: A1's contract
  is target-resolution; mixing a second source (the map) and a second comparison
  (set bijection) into one rule muddies both. A separate A3 keeps each rule focused.

## R2: Markdown table extraction (stdlib-only)

- **Decision**: Hand-roll a small standard-library extractor; add NO markdown
  dependency.
- **Rationale**: Principle VIII keeps the `retail check` core import path
  stdlib-only. The "Route by task" table is a simple GFM pipe table; the id is the
  leading token of column 1 of each data row. A line-scan that (a) finds the
  `## Route by task` heading, (b) reads pipe rows until the next `## ` heading, (c)
  skips the header row and the `|---|` separator row, and (d) takes the first cell's
  leading token (strip a trailing period) is sufficient and dependency-free.
- **Alternatives considered**: A markdown-parsing library (e.g. markdown-it,
  mistune) -- rejected: violates the stdlib-only core invariant and adds a parse
  surface far larger than needed. A generic "all pipe tables" scan -- rejected:
  the map has other pipe tables ("Route by symptom", supporting refs) whose rows
  would pollute the id set; the extractor MUST be section-delimited.

## R3: Id token shape

- **Decision**: The id token is the leading cell content with a trailing period
  stripped, preserving sub-letters. Verified set on main =
  `{1..22, 12a, 12b, 12c, 17a, 17b, 17c, 17d}` (26 ids).
- **Rationale**: Map rows read `| 1. Source onboarding | ... |`, `| 12a. KPI ... |`,
  `| 17d. Distributed ... |`. The id is `1`, `12a`, `17d` (period stripped, letters
  kept). The manifest declares the same tokens as quoted `id:` values ("1", "12a",
  "17d"). Both sides normalize to the same string set.
- **Alternatives considered**: Treating the whole first cell as the id -- rejected:
  would never match the manifest's bare id. Stripping letters (12a -> 12) -- rejected:
  collapses three distinct ids onto one and breaks the bijection.

## R4: Manifest parse reuse

- **Decision**: Reuse A1's lazy `import yaml` + safe_load + shape-guard approach for
  reading manifest ids; extract just the id set.
- **Rationale**: Identical source file and shape (`{routes: [ {id: ...}, ... ]}`).
  Lazy import keeps the core import path driver/dep-free. Malformed YAML or wrong
  shape must fail loud (ERROR), matching A1.
- **Alternatives considered**: A second YAML reader -- unnecessary; the pattern is
  proven in `routes.py`.

## R5: Fail-loud on unreadable inputs

- **Decision**: Emit an ERROR (never an empty-set vacuous pass) when (a) the manifest
  is missing/untracked/unparseable/wrong-shape, or (b) the map file is missing or its
  "Route by task" table cannot be located.
- **Rationale**: Principle VIII requires never-vacuously-green. An empty extracted set
  on one side would otherwise read as "all manifest ids are extra" or hide drift
  behind a parse failure. A1 already fails loud on a missing/malformed manifest; A3
  extends the same posture to the map source.
- **Alternatives considered**: Returning no findings on unreadable input -- rejected
  outright as a vacuous green.

## R6: Wiring symmetry (the G6-class trap)

- **Decision**: Add "A3" to `EXPECTED_RULE_IDS` in `tests/unit/test_rules_wiring.py`
  in the SAME change, and add `routes_coverage` to `src/retail/rules/__init__.py`
  (import tuple + `__all__`).
- **Rationale**: Verified `EXPECTED_RULE_IDS` currently holds 33 ids (A1 and B1
  present; A3 absent). The test keys its count to `len(EXPECTED_RULE_IDS)`, so adding
  A3 takes it to 34 and the count assertion follows automatically. `test_all_submodules_importable`
  derives the submodule list via `pkgutil`, so an unimported new module is caught --
  but registration only fires when the module is imported by the package, hence the
  `__init__.py` edit is mandatory.
- **Alternatives considered**: Trusting the synthesis text's "already 34" baseline --
  rejected: ground truth is 33; the synthesis is a known off-by-one.

## R7: Live guard

- **Decision**: Add a `test_live_*` guard mirroring
  `test_live_manifest_resolves_against_real_repo`: shell `git ls-files`, build a real
  RuleContext over the actual repo root, run A3, assert zero findings.
- **Rationale**: Proves the shipped map and manifest are in bijection end-to-end --
  the production guard, closest to how the rule runs under `retail check` in CI.
- **Alternatives considered**: Synthetic-only tests -- insufficient; would not catch a
  real future edit to the committed map or manifest.

## Open (deferred to human ratification -- see spec ## Clarifications)

These do NOT block the plan; the plan proceeds on reversible advisor defaults.

- Roadmap stage ownership (advisor default: outside the 7-stage spine, advances no
  stage, like A1/B1).
- Bijection scope: "Route by task" only vs also COMPASS (advisor default: "Route by
  task" only for v1).
- Severity posture: ERROR both directions vs one-direction WARNING (advisor default:
  ERROR both, matching A1).
