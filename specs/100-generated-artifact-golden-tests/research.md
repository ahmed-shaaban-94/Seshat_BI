# Phase 0 Research: Golden/Regression Tests for Generated DAX & SQL

**Feature**: `100-generated-artifact-golden-tests` | **Date**: 2026-07-04

## Precedent survey (what SHIPPED to reuse; what to stay distinct from)

This feature is a THIRD instance of a pattern the repo has shipped twice already:
"compare committed text against a live/derived value; fail closed on any drift."
Both precedents are cited directly, and neither is edited.

### Precedent 1 -- `tests/unit/test_rules_manifest_snapshot.py` (feature 043)

`docs/rules/rules-manifest.json` is generated from the LIVE rule registry
(`registry.all_rules()`), and `test_rules_manifest_snapshot.py` asserts the
committed manifest matches a freshly built one, failing closed on any missing,
unexpected, or retitled entry. This is the closest architectural sibling:

- Same shape of claim: "a committed artifact must match what the live code
  would produce for it, today."
- Same fail-closed posture: a mismatch is a `pytest.fail` with a diff-shaped
  message (missing / unexpected / retitled), never a skip.
- Same "regenerate and commit" fix instruction embedded in the failure message
  (`retail manifest`).
- DIFFERENCE this feature must preserve: 043's comparison is over PARSED JSON,
  which is line-ending agnostic by construction (`json.loads` does not care
  about `\r\n` vs `\n`). This feature's subjects (DAX, TMDL, SQL) are RAW TEXT
  with no such built-in immunity, so explicit normalization (FR-006) is
  required where 043 needed none. This is a real, spec-called-out difference,
  not an oversight to copy over.
- DIFFERENCE this feature must preserve: 043 ships a generator CLI subcommand
  (`retail manifest`) that PRODUCES the committed artifact as part of the
  product surface. This feature ships NO CLI subcommand -- FR-008's optional
  regeneration helper is a standalone, non-CI, human-invoked script, never
  wired into `retail`'s argparse surface, because the SCOPE GUARD (no new
  runtime authority) forbids adding to `retail`'s command surface for a
  test-support concern.

### Precedent 2 -- `tests/unit/test_severity_posture.py` (feature 046, `docs/rules/severity-posture.json`)

A second golden-file lock, same family as Precedent 1: a committed JSON
snapshot of the checker's severity table, compared against the live registry,
failing closed on drift. Confirms the "committed-golden-vs-live" pattern is
an established, repeated idiom in this codebase (not a one-off), and confirms
that when this codebase adds a golden-file test it does NOT touch
`rules-manifest.json` or `severity-posture.json` themselves -- those are their
own closed loop. This feature adds a THIRD, independent golden-file surface;
it does not extend either existing one.

### Precedent 3 -- `tests/unit/test_dax_gen.py` (existing, this feature's direct neighbour)

Already exercises `generate_measure` / `load_contract` from `src/retail/dax_gen.py`
against the SAME three fixture contracts this feature reuses
(`tests/fixtures/contracts/base_revenue.yaml`, `ratio_disc.yaml`,
`refuse_no_column.yaml`). Its `test_generate_roundtrips_to_pass` already proves,
today, that `generate_measure(BASE_REVENUE, name=..., doc_intent=...)` is
deterministic enough to round-trip through `check_measure_drift` and land on
`status == "pass"` for a fixed input on every run. That existing, PASSING test
is the input-source confirmation this feature's golden tests rely on:
`generate_measure` is already proven to be a pure function of its arguments
for this exact fixture set; this feature does not need to newly establish
determinism, only PIN what the deterministic output actually IS. Its
`test_cli_generate_success_stdout_tmdl` / `test_cli_generate_json_format` /
`test_cli_generate_refusal_stdout_empty_stderr_reason` tests also already
exercise the CLI path this feature's FR-002 call-shape must mirror.

### Precedent 4 -- `tests/unit/test_sql.py` + `tests/fixtures/sql/*.sql` (existing)

Confirms the repo's existing `tests/fixtures/<category>/` convention
(`contracts/`, `sql/` already exist as siblings) and the "stage a fixture into
`tmp_path`, run the rule/check, assert on findings" pattern. This feature's
`tests/fixtures/golden/` subtree follows that same sibling-directory
convention (`golden/dax/`, `golden/sql/`), but this feature's tests do NOT
stage fixtures into `tmp_path` and do NOT invoke any `retail check` rule --
they call `generate_measure` directly (Story 1) or read two already-committed
files and compare their text (Story 2). `test_sql.py` remains a "does the
RULE correctly judge SQL" test; this feature is "does the WAREHOUSE BUILDER'S
OWN committed output stay the same," a materially different assertion, per
the spec's own boundary section.

### Precedent 5 -- `.claude/skills/retail-build-warehouse/SKILL.md` + the two exemplar migrations (shipped)

`warehouse/migrations/0003_create_silver_retail_store_sales.sql` and
`0004_create_gold_retail_store_sales_star.sql` are the already-committed,
already-approved output of that skill for the `retail_store_sales` (C086)
source-map. They are read-only INPUT to this feature (the SQL regression
lock's subject), never edited by it. The skill itself has no callable Python
entry point (confirmed: no `build_warehouse(source_map)` function exists in
`src/retail/`), so User Story 2 is architecturally a REGRESSION LOCK on
committed text, not a "regenerate from source-map and compare" golden test --
this asymmetry is inherent to the two generators' different natures (code vs.
agent-authored skill), not a shortcut this feature is taking.

## Input-source confirmation

- `src/retail/dax_gen.py` exports `generate_measure`, `load_contract`,
  `GenResult` -- confirmed present, confirmed already imported directly by
  `tests/unit/test_dax_gen.py` (this feature's tests import the same way; no
  new import surface).
- The exact call shape this feature's golden tests MUST use is confirmed by
  reading `src/retail/cli.py::_run_generate` directly (not inferred):
  ```python
  result = generate_measure(
      contract.get("definition") or {},
      name=name,                                  # name = contract.get("name")
      doc_intent=contract.get("formula_intent"),
  )
  ```
  No `format_string` or `display_folder` override. The golden tests reproduce
  this exact call (per the spec's Clarifications), so the golden reflects what
  `retail generate` (the CLI a human/agent actually runs) emits, not an
  ad-hoc test-only shape such as `test_dax_gen.py`'s own
  `doc_intent="meaning of the measure"` literal.
- The golden test compares only `result.dax` and `result.tmdl_block` (and, for
  the refusal fixture, `result.reason`) -- NOT `result.warnings`. `warnings`
  is a `tuple[str, ...]` assembled from D-rule WARNING findings inside
  `_run_d_rules`; pinning it is unnecessary for this feature's stated goal
  (catch a change to the EMITTED dax/tmdl/reason text) and would risk an
  unrelated source of flakiness if a future D-rule's warning wording changes
  for reasons orthogonal to this feature.
- The three existing contract fixtures under `tests/fixtures/contracts/` were
  read directly and their `definition` blocks confirmed:
  `base_revenue.yaml` is `kind: base` / `aggregation: sum` over
  `gold.fct_sales_rss.total_spent` (no filter); `ratio_disc.yaml` is
  `kind: ratio` with `count_rows` numerator/denominator over
  `gold.fct_sales_rss`, filtered on `discount_applied` (`is_true` /
  `is_not_null`); `refuse_no_column.yaml` is `kind: base` /
  `aggregation: sum` with a `source` that omits `column` (the refusal case,
  since `_emit_base` requires `column` for any aggregation other than
  `count_rows`). This is sufficient to cover FR-002 (success x2, one `base`
  and one `ratio`) and FR-003 (refusal x1) with the FIXED corpus the spec's
  Assumptions section names.
- The two exemplar migration files were read directly and confirmed present
  at the paths FR-004 names; both are ASCII, UTF-8, and already committed.

## Line-ending handling: a conscious choice, not an omission

Precedent 1 (043) additionally pinned `docs/rules/rules-manifest.json` as
`text eol=lf` in `.gitattributes`, but that pin was defense-in-depth on top of
a comparison that was ALREADY line-ending agnostic (parsed JSON). This
feature's subjects -- raw DAX strings, TMDL text blocks, and SQL file bodies --
have no such parser-level immunity, so FR-006 makes normalization the
comparison's OWN job, explicit and testable, rather than leaning on a
`.gitattributes` pin as the safety net. This feature therefore adds NO
`.gitattributes` entry: the normalization algorithm in FR-006 (`\r\n` -> `\n`,
strip at most one trailing `\n`, then compare) is the sole, sufficient
mechanism, applied identically in every golden/regression test this feature
adds. This keeps the mechanism visible in the test code (auditable per
Principle I) rather than split across a test file and a `.gitattributes` line.

## Deferred capabilities NOT assumed (explicitly out of reach for this feature)

- **F016 (Power BI execution adapter)**: NOT assumed, NOT invoked, NOT
  imported. This feature never opens Power BI Desktop, a `.pbix`/PBIP model,
  or any MCP/connection surface. Confirmed absent from every test this
  feature adds (FR-005).
- **Live database (Postgres or any `Dialect` engine)**: NOT assumed. Every
  test added by this feature reads only already-committed repository files
  (contract YAML fixtures, golden text files, the two exemplar migration
  `.sql` files) and calls a pure Python function
  (`generate_measure`/`load_contract`). No `psycopg2`, no DSN, no
  `ANALYTICS_DB_ENGINE`, no `retail validate` surface is touched. SC-003 (all
  tests pass with no DB connection available and no environment variable set)
  is a direct restatement of this.
- **F031-F033 (spec-only runtimes)**: NOT assumed; these do not exist as
  callable code as of this feature and are not referenced.
- **The `retail-build-warehouse` skill's execution**: NOT invoked. User Story
  2's regression test never runs the skill's instructions; it reads the
  skill's PAST, already-committed output (the two migration files) and
  compares that text to a golden copy. The skill itself, and its Markdown
  instructions, are untouched (FR-009).
- **A `build_warehouse(source_map)` callable**: does not exist in this repo
  and this feature does not add one; the Assumptions section of the spec
  records this as the reason User Story 2 is a regression LOCK rather than a
  symmetric golden test like User Story 1.

## Alternatives considered and rejected

- **Add the SQL regression check as a new `retail check` rule** (e.g. an
  "S8-style" rule that hashes the migration file and compares to a constant).
  Rejected: the spec's collision-avoidance allocation explicitly forbids a new
  rule-id for this feature, and a `retail check` rule would need registry
  wiring, a manifest entry, and a severity-posture entry -- all of which SC-005
  requires to stay byte-identical before/after this feature. A plain pytest
  test achieves the same fail-closed guarantee without touching the gate
  surface.
- **Combine `dax`, `tmdl_block`, and `reason` into one golden file per
  fixture** (e.g. a single JSON or YAML per contract). Rejected per the
  spec's own Clarifications: separate small text files per output
  (`<stem>.dax.txt`, `<stem>.tmdl.txt`, `<stem>.reason.txt`) make a failing
  diff unambiguous about which specific output changed, at negligible cost
  (a handful of small files).
- **Make the regeneration helper (FR-008) a `retail` CLI subcommand** (mirroring
  043's `retail manifest`). Rejected: 043's manifest is a PRODUCT artifact the
  CLI is expected to (re)produce as part of normal operation; this feature's
  golden fixtures are TEST-ONLY support files with no product-facing meaning,
  so adding them to `retail`'s subcommand surface would be new runtime
  authority the SCOPE GUARD forbids. A standalone script under
  `tests/fixtures/golden/` keeps the helper entirely off that surface.
