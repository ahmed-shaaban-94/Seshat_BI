# Feature Specification: Golden/Regression Tests for Generated DAX & SQL

**Feature Branch**: `100-generated-artifact-golden-tests`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "gap #12. Golden/regression tests for generated DAX & SQL --
Snapshot/golden tests that `retail generate` emits the SAME verified measure for a fixed
metric contract, and the warehouse builder emits stable SQL for a fixed source-map. Fixtures
test the rules today, not the generators' output stability."

## Overview

Seshat BI has two artifact generators, but they are architecturally asymmetric:

- `retail generate` (`src/retail/dax_gen.py`, `generate_measure` / `load_contract`) is
  DETERMINISTIC CODE. Given a metric-contract YAML it emits DAX + a TMDL block through a
  fail-closed verify pipeline (emit -> `check_measure_drift` -> D-rule form check), or it
  REFUSES with a reason. It is a pure function of its input: same contract in, same output
  (or same refusal) out.
- The silver/gold warehouse builder (`.claude/skills/retail-build-warehouse/SKILL.md`) is an
  AGENT-AUTHORED SKILL, not a callable function. There is no `build_warehouse(source_map)`
  entry point to invoke and diff; the agent reads an approved `source-map.yaml` and writes
  migration `.sql` files under `warehouse/migrations/` by following the skill's instructions.

Today's test suite (`tests/unit/test_dax_gen.py`, `tests/unit/test_sql.py`,
`tests/unit/test_dax.py`) exercises the RULES: it checks that `generate_measure` round-trips
through the verifier (emits something that re-verifies as `pass`), and that the S1-S4b / D
rules correctly accept or reject hand-written fixture SQL. None of these tests pin the
GENERATORS' OWN OUTPUT to a committed byte-for-byte expectation. A change to `dax_gen.py`'s
emission logic that still produces syntactically-valid, rule-passing DAX -- but different DAX
than before -- passes every existing test silently. The same is true, in spirit, for the two
committed exemplar migrations (`warehouse/migrations/0003_create_silver_retail_store_sales.sql`,
`0004_create_gold_retail_store_sales_star.sql`): nothing fails closed if their committed text
drifts from what the source-map that produced them implies. This feature closes that gap for
the deterministic generator with a true golden test, and closes it for the agent-authored
builder with a regression lock on the committed exemplar artifact, using the same "compare
against a committed fixture" pattern the codebase already uses for its rule-registry and
severity-posture snapshots.

## Boundary against neighbouring shipped work (read first)

This feature adds a NEW test layer; it must stay distinct from tests and artifacts that
already exist and already look adjacent:

- **`tests/unit/test_dax_gen.py`** (existing) asserts the DAX GENERATOR'S ROUND-TRIP PROPERTY:
  emitted DAX re-verifies as `pass` under `check_measure_drift`, and malformed contracts are
  refused. It does NOT assert what the emitted DAX text actually IS. This feature ADDS a
  byte-level comparison against a committed golden DAX/TMDL file for a fixed set of contract
  fixtures -- it does not replace or edit `test_dax_gen.py`, and it does not change
  `dax_gen.py`'s emission logic.
- **`tests/unit/test_sql.py`** + **`tests/fixtures/sql/*.sql`** (existing) assert that the
  S1-S4b static SQL rules correctly PASS or FAIL hand-authored fixture SQL files -- this is
  "does the checker correctly judge SQL," the RULES side of the gap sentence. This feature
  is the other half: "does the SQL the warehouse builder actually wrote stay the same," a
  regression lock on committed migration files, not a rule-correctness test.
- **`src/retail/metric_drift.py` (`check_measure_drift`)** is the CHECKER: "does this DAX
  match this contract." `dax_gen.py` is its inverse: "emit DAX that matches this contract."
  This feature is neither -- it is "does the generator's own emission for a FIXED contract
  stay textually identical run over run," a stability lock layered on top of both.
- **`test_rules_manifest_snapshot.py`** / `docs/rules/rules-manifest.json` and
  **`test_severity_posture.py`** / `docs/rules/severity-posture.json` (both shipped) are
  golden-file locks on the RULE REGISTRY and SEVERITY TABLE -- static governance metadata.
  This feature applies the same committed-golden pattern to a different subject: generated
  DAX/SQL artifacts, not rule metadata. It reuses the pattern; it does not touch those files
  or their tests.
- **`.claude/skills/retail-build-warehouse/SKILL.md`** (shipped) is the skill that AUTHORS
  migration SQL from an approved source-map and stops before executing it. This feature adds
  NO change to that skill and adds NO callable warehouse-builder function; it locks the SQL
  the skill has ALREADY produced and committed, so a future silent edit to that committed SQL
  (by hand or by a future automation) is caught.
- This feature adds NO `retail check` rule and NO rule-id (collision-avoidance allocation):
  it is pytest tests over committed fixtures, not a new gate rule. `retail check`'s rule count
  and manifest are UNCHANGED by this feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The DAX generator's output is pinned for a fixed contract (Priority: P1)

A contributor changes `dax_gen.py` -- refactoring `_emit_base`, tweaking whitespace in the
TMDL block, or adjusting how a filter clause is rendered. Before this feature, as long as the
new output still re-verifies as `pass`, nothing tells them the actual DAX text changed. With
this feature, running the test suite against a fixed, already-committed metric-contract
fixture (e.g. `tests/fixtures/contracts/base_revenue.yaml`) compares the freshly generated
DAX and TMDL block against a committed golden file. Any difference -- intended or not -- fails
the test with a visible diff, forcing an explicit, reviewable golden-file update rather than a
silent drift.

**Why this priority**: This is the deterministic half of the gap and the one with a real
callable function to test; it delivers the core value (catch silent generator drift) with the
least architectural risk.

**Independent Test**: Run the golden test suite unchanged against the current `dax_gen.py`;
it passes today (establishing the baseline). Then hand-edit one character of the emitted DAX
logic (a local, uncommitted experiment) and re-run; the golden test fails with a diff against
the committed golden file, while `test_dax_gen.py`'s existing round-trip test still passes.

**Acceptance Scenarios**:

1. **Given** a committed metric-contract fixture and its committed golden DAX + TMDL output,
   **When** the golden test runs `generate_measure(load_contract(fixture))` and compares the
   result to the golden file, **Then** the test passes when the generator's output is
   byte-identical (after newline normalization, see Edge Cases) to the golden file.
2. **Given** the same fixture, **When** the generator's emission logic changes such that its
   output text differs from the golden file (even if the new output still verifies as
   `pass`), **Then** the golden test fails and reports a diff between actual and expected
   output.
3. **Given** a REFUSAL fixture (a contract `generate_measure` is expected to reject, e.g.
   `tests/fixtures/contracts/refuse_no_column.yaml`), **When** the golden test runs it,
   **Then** the test asserts the refusal's `reason` string matches a committed golden reason
   string, so a silently-changed refusal message is also caught.

---

### User Story 2 - The committed exemplar warehouse SQL is locked against silent drift (Priority: P2)

A contributor (human or agent) touches `warehouse/migrations/0003_create_silver_retail_store_sales.sql`
or `0004_create_gold_retail_store_sales_star.sql` -- directly, or indirectly by re-running the
`retail-build-warehouse` skill against the same committed source-map and overwriting the file.
Before this feature, nothing in the test suite notices unless the edit happens to trip an
S1-S4b static rule. With this feature, a regression test reads the two committed migration
files and compares them against a committed copy held as a golden fixture; any difference
fails the test with a diff, so the change is visible and must be a deliberate, reviewed commit
rather than a silent rewrite.

**Why this priority**: The warehouse builder has no callable function to invoke, so this
story is a regression LOCK on an already-committed artifact, not a true "regenerate and
compare" golden test (see Assumptions). It is P2 because it is a narrower, artifact-only
safety net rather than the full generate-and-verify loop User Story 1 provides.

**Independent Test**: Run the regression test suite unchanged against the current
`warehouse/migrations/000{3,4}_*.sql`; it passes today. Hand-edit one line of either committed
migration file (a local, uncommitted experiment) and re-run; the test fails and reports which
file and which lines differ from the golden fixture.

**Acceptance Scenarios**:

1. **Given** a golden fixture copy of `warehouse/migrations/0003_create_silver_retail_store_sales.sql`
   under `tests/fixtures/`, **When** the regression test runs, **Then** it passes if the
   committed migration file is byte-identical (after newline normalization) to the golden
   fixture.
2. **Given** the same setup for `0004_create_gold_retail_store_sales_star.sql`, **When** the
   file's committed text changes, **Then** the regression test fails and names the file and
   the differing content.
3. **Given** the regression test suite, **When** it runs, **Then** it opens no database
   connection and invokes no `retail-build-warehouse` skill step -- it only reads already
   committed files (Principle VIII; SCOPE GUARD).

---

### User Story 3 - Golden fixtures are refreshed through one explicit, reviewable command (Priority: P3)

A contributor makes an intentional change to `dax_gen.py`'s emission format (e.g. a formatting
improvement everyone agrees on) and needs to update the golden files to match, without hand-
editing DAX text and risking a typo. They run a single regeneration command that overwrites
only the golden fixture files with fresh generator output, then review the resulting `git
diff` before committing -- the regeneration step itself never asserts pass/fail and never runs
in CI.

**Why this priority**: This is a workflow convenience for maintaining the golden suite over
time; the tests are fully valuable without it (a contributor could hand-edit the golden file),
so it is the lowest priority slice.

**Independent Test**: Run the regeneration command after an intentional `dax_gen.py` change;
confirm the golden fixture files are rewritten and `git diff` shows exactly the expected
textual change; then confirm the golden tests (User Story 1) pass again with the refreshed
fixtures.

**Acceptance Scenarios**:

1. **Given** an intentional change to `dax_gen.py`, **When** the regeneration command is run,
   **Then** only the golden DAX/TMDL fixture files are overwritten -- no source file, contract
   fixture, or rule file is touched.
2. **Given** the regeneration command exists, **When** it is invoked, **Then** it never
   silently commits, never runs as part of `pytest` or `retail check`, and requires the
   contributor to review and commit the resulting diff themselves.

---

### Edge Cases

- What happens on Windows CRLF vs LF newline differences between a freshly generated string
  and a committed golden file checked out under `core.autocrlf=true`? The comparison MUST
  normalize line endings (and, if applicable, a single trailing-newline difference) before
  comparing, so the golden tests do not flake across platforms or checkout configurations
  (see FR-006).
- What happens when a metric-contract fixture used by an existing test
  (`tests/fixtures/contracts/*.yaml`) is modified for an unrelated reason and a golden test
  for it now fails? The failure is a correct, intended signal (the generator's input changed,
  so its output is expected to change) -- the contributor updates the golden fixture via User
  Story 3 and reviews the diff; the test is not weakened to ignore this case.
- What happens when a new metric-contract `kind` is added to `dax_gen.py` in the future (the
  module's own docstring calls itself "Phase 1")? This feature's fixture set is a FIXED,
  finite corpus as of this spec (see Assumptions); adding golden coverage for a new `kind` is
  a follow-on addition to the fixture set, not a requirement this feature must anticipate.
- What happens if a golden fixture file is missing or unreadable when the test runs? The test
  MUST fail closed (an explicit test failure naming the missing path), never skip silently and
  never treat a missing golden as an automatic pass.
- What happens when the committed exemplar migration SQL (User Story 2) is intentionally
  changed as part of unrelated warehouse work (e.g. someone edits
  `0003_create_silver_retail_store_sales.sql` on purpose)? The regression test fails exactly
  as designed; the contributor updates the golden copy under `tests/fixtures/` in the same
  commit as the intentional SQL change, so the two never drift apart across commits.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST add golden/regression tests under `tests/unit/` (pytest,
  `@pytest.mark.unit`) and golden fixture files under `tests/fixtures/`. It MUST NOT add a
  `retail check` rule, a rule-id, or any entry to `docs/rules/rules-manifest.json` or
  `docs/rules/severity-posture.json` (collision-avoidance allocation).
- **FR-002**: For a fixed, committed set of metric-contract fixtures under
  `tests/fixtures/contracts/`, the test suite MUST call `generate_measure(...)` using the SAME
  argument mapping as the `retail generate` CLI path (`src/retail/cli.py::_run_generate`):
  `generate_measure(contract["definition"], name=contract["name"],
  doc_intent=contract.get("formula_intent"))`, with no `format_string` or `display_folder`
  override, so the golden reflects what `retail generate` actually emits for that contract
  file, not an ad-hoc test-only call shape. The test MUST assert the resulting `dax` and
  `tmdl_block` strings are identical (after the normalization in FR-006) to a committed golden
  file for that fixture. Golden files live under `tests/fixtures/golden/dax/`, one file per
  contract fixture named `<fixture-stem>.dax.txt` (the `dax` string) and
  `<fixture-stem>.tmdl.txt` (the `tmdl_block` string) -- two small text files per fixture
  rather than one combined file, so a diff on either output is unambiguous about which string
  changed.
- **FR-003**: For at least one contract fixture that `generate_measure` is expected to refuse
  (e.g. `refuse_no_column.yaml`), the test suite MUST assert the resulting `GenResult.reason`
  string is identical to a committed golden reason string, so a silent change to a refusal
  message is also caught. The golden reason file lives at
  `tests/fixtures/golden/dax/<fixture-stem>.reason.txt`, alongside the success-case golden
  files, using the same per-fixture-stem naming and the same FR-006 normalization.
- **FR-004**: The test suite MUST add a regression test comparing the current committed text
  of the two exemplar warehouse migration files
  (`warehouse/migrations/0003_create_silver_retail_store_sales.sql`,
  `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`) against a committed
  golden copy held under `tests/fixtures/golden/sql/`, one golden file per migration file
  using the SAME filename as the migration it locks (e.g.
  `tests/fixtures/golden/sql/0003_create_silver_retail_store_sales.sql`). This test MUST NOT
  invoke the `retail-build-warehouse` skill, open a database connection, or execute any SQL
  (Principle VIII; SCOPE GUARD: no live DB).
- **FR-005**: All golden/regression tests added by this feature MUST read only already-
  committed repository files. They MUST NOT connect to a database, invoke a live Power BI/PBIP
  surface, or call any deferred execution adapter (F016) or spec-only runtime (F031-F033).
- **FR-006**: All golden/regression text comparisons MUST normalize line endings (treat CRLF
  and LF as equivalent) and MUST NOT fail solely due to a single trailing-newline difference,
  so the tests are stable under `core.autocrlf=true` checkouts on Windows and other platforms.
  The normalization method is: read both the freshly generated/actual text and the committed
  golden text, replace every `\r\n` with `\n`, then strip at most one trailing `\n` from each
  side before comparing for exact equality. This mirrors why
  `test_rules_manifest_snapshot.py`'s JSON golden needs no such step (JSON parsing is already
  line-ending agnostic) -- raw DAX/TMDL/SQL text has no such built-in immunity, so this
  feature's tests MUST apply the normalization explicitly rather than relying on a parser.
- **FR-007**: When a golden fixture file referenced by a test is missing or unreadable, the
  test MUST fail with an explicit message naming the missing/unreadable path. It MUST NOT skip
  the test silently and MUST NOT treat the absence of a golden file as a passing result.
- **FR-008**: The feature MAY add one regeneration helper: a standalone Python script (e.g.
  `tests/fixtures/golden/regenerate_dax_golden.py`), invoked manually by a contributor
  (`python tests/fixtures/golden/regenerate_dax_golden.py`), that overwrites ONLY the golden
  fixture files under `tests/fixtures/golden/` with fresh generator output for review via `git
  diff`. It is not a `retail` CLI subcommand and not a pytest fixture/test. This helper MUST
  NOT run as part of `pytest`, MUST NOT run as part of `retail check`, MUST NOT be invoked by
  any CI workflow, and MUST NOT commit on the contributor's behalf.
- **FR-009**: This feature MUST NOT modify `src/retail/dax_gen.py`, `src/retail/metric_drift.py`,
  the `.claude/skills/retail-build-warehouse/SKILL.md` skill, or any existing test file
  (`test_dax_gen.py`, `test_sql.py`, `test_dax.py`) -- it is additive-only (SCOPE GUARD: no
  new runtime authority).
- **FR-010**: The golden DAX/TMDL/SQL fixture corpus MAY reuse the existing `retail_store_sales`
  (C086) worked-example contracts and migrations as its committed exemplar instances, consistent
  with Principle VII (a cited filled instance, not a template default); no new synthetic-only
  domain is required for this feature's fixture corpus.
- **FR-011**: All files authored by this feature MUST be ASCII, UTF-8 without BOM (`--` and
  `->`, no glyphs), and MUST use short repo-relative paths (Windows 260-char budget) (rule IX).
- **FR-012**: This feature MUST NOT emit, assert, or reference any numeric confidence / health /
  maturity score or any "N of M" completeness tally in its tests, fixtures, or documentation
  (hard rule #9). A golden test's result is binary (pass/fail with a diff), never a score.

### Key Entities

- **Golden DAX/TMDL fixture**: a committed file pairing a metric-contract fixture with the
  exact `dax` and `tmdl_block` text `generate_measure` is expected to emit for it; the basis
  of comparison for User Story 1.
- **Golden refusal fixture**: a committed expected `reason` string for a metric-contract
  fixture `generate_measure` is expected to refuse.
- **Golden SQL fixture**: a committed copy of an exemplar warehouse migration file, held under
  `tests/fixtures/`, used as the comparison baseline for the regression lock in User Story 2.
- **Regeneration helper**: the optional, non-CI, human-invoked command (FR-008) that refreshes
  golden fixture files from current generator output for review, never for automatic
  acceptance.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A one-character change to `dax_gen.py`'s emission logic that still passes
  `test_dax_gen.py`'s existing round-trip assertions is caught (test failure with a diff) by
  at least one golden test added by this feature.
- **SC-002**: A one-line hand-edit to either committed exemplar warehouse migration file is
  caught (test failure with a diff) by the regression test added for User Story 2.
- **SC-003**: 100% of the golden/regression tests added by this feature pass on a clean
  checkout with no database connection available and no environment variable set (Principle
  VIII: fully static, offline-runnable).
- **SC-004**: 0 golden/regression tests added by this feature flake between a CRLF checkout
  and an LF checkout of the same commit (FR-006 normalization holds in both directions).
- **SC-005**: `retail check`'s rule count and `docs/rules/rules-manifest.json` /
  `docs/rules/severity-posture.json` are byte-identical before and after this feature lands
  (0 new rule-ids; collision-avoidance allocation honored).
- **SC-006**: 0 numeric confidence/health/maturity scores or completeness tallies appear in
  any test, fixture, or doc this feature adds (hard rule #9).

## Assumptions

- `src/retail/dax_gen.py` (`generate_measure`, `load_contract`, `GenResult`) is stable public
  surface for this feature's tests to import directly, as `tests/unit/test_dax_gen.py` already
  does; this feature adds no new import surface to that module.
- The warehouse builder (`.claude/skills/retail-build-warehouse/SKILL.md`) has no callable
  Python entry point and is not expected to gain one for this feature; User Story 2 is
  therefore scoped to a REGRESSION LOCK on already-committed migration SQL, not a true
  "regenerate from source-map and compare" golden test. A future feature that gives the
  warehouse builder a deterministic, callable code path could upgrade this to a symmetric
  golden test; that upgrade is out of scope here.
- The fixture corpus for this feature is fixed at what already exists on disk as of this spec:
  `tests/fixtures/contracts/{base_revenue,ratio_disc,refuse_no_column}.yaml` for DAX, and
  `warehouse/migrations/0003_create_silver_retail_store_sales.sql` +
  `0004_create_gold_retail_store_sales_star.sql` for SQL. Expanding the corpus to new
  contract `kind`s or new tables is a follow-on addition, not a requirement of this feature.
- The regeneration helper in FR-008 is a convenience, not a load-bearing requirement; the
  feature is complete and independently valuable (User Stories 1 and 2) without it, so it is
  scoped as P3 / MAY rather than MUST.
- No new `retail check` rule, rule-id, or manifest/severity-posture entry is introduced; the
  collision-avoidance allocation for this feature is fully satisfied by adding pytest tests
  and fixtures only, touching no shared schema.
- This feature requires no named-human approval and raises no Principle-V judgment call: it
  locks already-approved, already-committed generator output and artifacts against silent
  drift; it does not decide grain, PII, business policy, or any new readiness state.

## Clarifications

### Session 2026-07-04

- **Q: FR-002 says the golden test must call `generate_measure(load_contract(...))`, but
  `generate_measure` requires a `name` keyword argument (and accepts optional `format_string`,
  `display_folder`, `doc_intent`) that are not part of the contract `definition` block --
  where do these come from, and what is the golden test actually pinning?**
  Resolution: Default adopted. The golden test mirrors the `retail generate` CLI's own
  argument mapping exactly (`src/retail/cli.py::_run_generate`):
  `generate_measure(contract["definition"], name=contract["name"],
  doc_intent=contract.get("formula_intent"))`, no `format_string`/`display_folder` override.
  This is the defensible default rather than an arbitrary one: the feature exists to pin what
  `retail generate` emits, so the golden must reproduce that CLI invocation path (already
  exercised and passing today in `test_cli_generate_success_stdout_tmdl` /
  `test_cli_generate_json_format`), not a test-only ad-hoc call shape such as
  `test_dax_gen.py`'s literal `doc_intent="meaning of the measure"`.
  Touched: FR-002.

- **Q: FR-002 and FR-004 both say a golden file is "committed" / "held under
  `tests/fixtures/`" but neither specifies the subdirectory, the per-fixture naming scheme, or
  whether the `dax` and `tmdl_block` outputs (plus, per FR-003, the refusal `reason`) share one
  file or live in separate files -- an implementer at plan/tasks stage cannot lay out the
  fixture tree from the spec text alone.**
  Resolution: Default adopted, following the repo's existing `tests/fixtures/<category>/`
  convention (`contracts/`, `sql/` already exist as siblings). DAX/TMDL/refusal goldens live
  under `tests/fixtures/golden/dax/`, one file per output per fixture, named by fixture stem:
  `<fixture-stem>.dax.txt`, `<fixture-stem>.tmdl.txt`, `<fixture-stem>.reason.txt` (refusal
  fixtures only). SQL regression goldens live under `tests/fixtures/golden/sql/`, one file per
  migration, using the migration's own filename unchanged. Separate small files (rather than
  one combined file per fixture) were chosen so a failing diff names exactly which output
  (dax vs tmdl vs reason) changed, without a contributor having to parse a combined diff.
  Touched: FR-002, FR-003, FR-004.

- **Q: FR-006 requires CRLF/LF and trailing-newline normalization but does not state the
  normalization algorithm; the nearest committed precedent
  (`test_rules_manifest_snapshot.py`) sidesteps the question entirely because it compares
  parsed JSON, not raw text, so that precedent does not transfer directly.**
  Resolution: Default adopted. Normalize by replacing every `\r\n` with `\n` in both the
  actual and the golden text, then stripping at most one trailing `\n` from each side, before
  an exact string-equality comparison. This is stated explicitly in FR-006 now rather than
  left to each test's own ad-hoc implementation, so all golden tests in this feature use one
  normalization behavior.
  Touched: FR-006.

- **Q: FR-008 permits an optional regeneration helper described only as "a script or a
  documented command" -- underspecified enough that an implementer could reach for a new
  `retail` CLI subcommand, which would then need `retail check` / manifest wiring this feature
  explicitly must not add.**
  Resolution: Default adopted. The helper, if added, is a standalone Python script under
  `tests/fixtures/golden/` (e.g. `regenerate_dax_golden.py`), run manually
  (`python tests/fixtures/golden/regenerate_dax_golden.py`) -- never a `retail` CLI
  subcommand, never a pytest test/fixture, never invoked by CI. This keeps FR-008's helper
  fully outside the `retail check` surface and the collision-avoidance allocation intact.
  Touched: FR-008.

No Principle-V judgment call (grain, PII, business-policy, or approval-authority question) was
found in this spec; none is recorded as OPEN. The spec's own Assumptions section already
states this feature decides no new readiness state and requires no named-human approval --
locking already-approved, already-committed generator output against silent drift is
mechanical, not a judgment call, and that assessment holds after this clarification pass.
