# Implementation Plan: Golden/Regression Tests for Generated DAX & SQL

**Branch**: `100-generated-artifact-golden-tests` | **Date**: 2026-07-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/100-generated-artifact-golden-tests/spec.md`

## Summary

Add pytest golden/regression tests -- and only golden/regression tests -- that pin the
STABILITY of two already-shipped generators' output, closing gap #12. For the deterministic
DAX generator (`generate_measure`/`load_contract` in `src/retail/dax_gen.py`), a new test
module calls `generate_measure` using the SAME argument mapping `retail generate`'s CLI path
(`src/retail/cli.py::_run_generate`) already uses, for the three existing contract fixtures
under `tests/fixtures/contracts/`, and compares the resulting `dax` / `tmdl_block` (and, for
the one refusal fixture, `reason`) strings against small committed golden text files under
`tests/fixtures/golden/dax/`. For the agent-authored warehouse builder (no callable Python
entry point exists), a second new test module reads the two committed exemplar migration files
(`warehouse/migrations/0003_*.sql`, `0004_*.sql`) and compares their text, byte-for-byte after
normalization, against golden copies under `tests/fixtures/golden/sql/`. Both comparisons apply
one explicit CRLF/LF + single-trailing-newline normalization (FR-006) so they never flake across
`core.autocrlf=true` checkouts. An optional, non-CI, human-run regeneration script may refresh
the DAX/TMDL goldens for review via `git diff`. This is a THIRD instance of the repo's existing
"committed golden vs. live/derived value, fail closed on drift" pattern (Precedents: feature 043
`rules-manifest.json`, feature 046 `severity-posture.json`) applied to a new subject (generated
DAX/SQL artifact text, not rule/severity metadata). It adds NO `retail check` rule, NO rule-id,
and NO change to `docs/rules/rules-manifest.json` or `docs/rules/severity-posture.json` --
purely additive pytest tests and fixtures, touching no shared schema, no source generator, and
no skill.

## Technical Context

**Language/Version**: Python 3.13 (repo interpreter); stdlib-only for the tests and the
optional regeneration helper (`pathlib`, `dataclasses` via the imported `dax_gen` module).

**Primary Dependencies**: NONE new. Reuses `retail.dax_gen.generate_measure`,
`retail.dax_gen.load_contract`, and `retail.dax_gen.GenResult` exactly as
`tests/unit/test_dax_gen.py` already imports them. Test framework is `pytest` (already a repo
dependency). No new third-party package.

**Storage**: Committed text artifacts only -- golden `.txt` files under
`tests/fixtures/golden/dax/` and golden `.sql` copies under `tests/fixtures/golden/sql/`. No
database, no live connection of any kind.

**Testing**: `pytest`, marked `@pytest.mark.unit` (matches every sibling test file this feature
is adjacent to: `test_dax_gen.py`, `test_sql.py`, `test_rules_manifest_snapshot.py`).

**Target Platform**: CI + local dev on Windows (`core.autocrlf=true`) and Linux/CI runners.
Must be byte-stable across both via the FR-006 normalization (no `.gitattributes` pin is added
for this feature -- see research.md's "conscious choice" note).

**Project Type**: Single project (existing `src/retail` package + `tests/unit` + `tests/fixtures`).

**Performance Goals**: N/A -- three DAX-generation calls plus two small-file text comparisons;
runs in well under a second.

**Constraints**: No database connection, no network call, no Power BI/PBIP surface, no import of
any live-execution adapter (Principle VIII; SCOPE GUARD). No modification to `dax_gen.py`,
`metric_drift.py`, the `retail-build-warehouse` skill, or any existing test file (FR-009,
additive-only). No new `retail` CLI subcommand, no registry/manifest/severity-posture entry
(collision-avoidance allocation; SC-005). ASCII / UTF-8 no-BOM for every authored file (FR-011).

**Scale/Scope**: Two new pytest test modules, up to nine small golden text files (three
contracts x up to three outputs each: `.dax.txt`, `.tmdl.txt`, and `.reason.txt` for the one
refusal fixture only), two golden SQL copies, and one optional standalone regeneration script.
No more.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design below.*

Each principle is addressed at the altitude this feature actually touches. Several principles
are correctly **not engaged** by a pytest-golden-tests-over-committed-fixtures feature; those
are stated as such rather than stretched into a false "satisfies" claim.

- **Principle I (Agent-First, Gate-Enforced)** -- ENGAGED, narrowly. This feature's tests are
  themselves fail-closed (a diff, not an advisory warning, on any mismatch; FR-007 forbids a
  silent skip on a missing golden). But they are explicitly **NOT** a `retail check` rule and
  add **NO** rule-id (collision-avoidance allocation; FR-001). Demonstrability here means
  "run `pytest -m unit`," not "run `retail check`" -- the generator-stability guarantee this
  feature adds lives in the test suite, not the gate. PASS, with that scope named precisely.
- **Principle III (Medallion, Postgres-First, Gold-Only)** -- NOT ENGAGED. This feature opens no
  database connection and reads no `gold`/`silver`/`bronze` schema live; it reads two already-
  committed `.sql` FILES as text. No compliance claim is made under this principle because none
  is applicable.
- **Principle IV (Source Mapping Before Silver)** -- NOT ENGAGED. This feature authors no
  `silver.*` SQL and maps no new table. It locks the TEXT of migration files that were already
  written under an ALREADY-approved source-map (`mappings/retail_store_sales/`, gate cleared
  2026-06-25); it does not touch the mapping gate itself.
- **Principle V (Agent Stops at Judgment Calls)** -- NOT ENGAGED. This feature raises no grain,
  PII, business-rollup, or approval question and records no `unresolved-questions.md` entry;
  none exists to raise. The spec's own Assumptions section confirms this and it is re-confirmed
  here: the tests lock ALREADY-approved, ALREADY-committed output against silent drift; they
  decide nothing new.
- **Principle VI (Defaults Then Deviations)** -- NOT ENGAGED. No new cleaning/modeling default is
  adopted or deviated from; no `assumptions.md` entry is added or implied.
- **Principle VII (C086 Is An Example, Not The Schema)** -- ENGAGED. Per FR-010, the fixture
  corpus reuses the existing `retail_store_sales` (C086) contracts and migrations as the cited
  FILLED INSTANCE -- exactly the role Principle VII assigns C086 -- rather than inventing a new
  synthetic-only domain. Nothing table-specific (billing codes, business segments, PII columns)
  is baked into any generic test/plan/template; the two new test MODULES are themselves fully
  generic (they would work unchanged against any future contract/migration fixture set). PASS.
- **Principle VIII (Static-First Governance, Live Deferred)** -- ENGAGED, centrally. Every test
  this feature adds is stdlib-only at import, reads only committed files, opens no DB connection,
  and calls no live Power BI/adapter surface (SC-003: passes with no DB connection available and
  no environment variable set). This is squarely the "static core, CI-able, no network" posture
  the principle requires. PASS.
- **Principle IX (Secrets and Reproducibility)** -- ENGAGED. No secret, host, or DSN is
  introduced (there is nothing to connect to). All files this feature authors are ASCII /
  UTF-8 without BOM (FR-011), and every path stays well under the Windows `MAX_PATH` budget
  (longest new path is `tests/fixtures/golden/dax/refuse_no_column.reason.txt`, ~50 repo-relative
  characters). PASS.
- **Hard rule #9 (no fabricated confidence/health/maturity score)** -- ENGAGED and structurally
  guaranteed: every test this feature adds is a binary pytest pass/fail with a text diff on
  failure. No score, percentage, or "N of M" tally is emitted, asserted, or referenced anywhere
  (FR-012, SC-006). PASS.

No violations identified against any engaged principle -> **Complexity Tracking is empty.**

*Post-design re-check (after Phase 1 data-model/quickstart below): unchanged.* The data model
introduces no new runtime authority and the quickstart invokes only `pytest` and an optional
manual script; the gate list above still holds.

## Project Structure

### Documentation (this feature)

```text
specs/100-generated-artifact-golden-tests/
|-- spec.md              # Stage 2 output (already clarified)
|-- research.md           # Phase 0 output (this plan's sibling)
|-- plan.md               # This file
|-- data-model.md         # Phase 1 output
|-- quickstart.md         # Phase 1 output
`-- tasks.md               # Stage 4 output (/speckit-tasks -- NOT created by /speckit-plan)
```

No `contracts/` subdirectory: this is not an API-shaped feature (no request/response contract
to specify); the closest precedent (043, also a golden-file-test feature) omits it too.

### Source Code (repository root)

```text
tests/
|-- unit/
|   |-- test_dax_golden.py            # NEW -- User Story 1 + 3 (DAX/TMDL/reason goldens)
|   `-- test_warehouse_sql_golden.py  # NEW -- User Story 2 (SQL regression lock)
`-- fixtures/
    |-- contracts/                     # UNCHANGED (existing: base_revenue, ratio_disc,
    |                                  #   refuse_no_column) -- read-only input, not edited
    `-- golden/                        # NEW subtree, this feature's own fixture footprint
        |-- dax/
        |   |-- base_revenue.dax.txt
        |   |-- base_revenue.tmdl.txt
        |   |-- ratio_disc.dax.txt
        |   |-- ratio_disc.tmdl.txt
        |   `-- refuse_no_column.reason.txt
        |-- sql/
        |   |-- 0003_create_silver_retail_store_sales.sql
        |   `-- 0004_create_gold_retail_store_sales_star.sql
        `-- regenerate_dax_golden.py   # OPTIONAL (FR-008) -- standalone, human-run, not CI

warehouse/migrations/                  # UNCHANGED -- read-only input (0003, 0004 already exist)
src/retail/                            # UNCHANGED -- no edit to dax_gen.py, metric_drift.py,
                                        #   cli.py, or any rule module
.claude/skills/retail-build-warehouse/ # UNCHANGED -- SKILL.md not touched
docs/rules/                            # UNCHANGED -- rules-manifest.json, severity-posture.json
                                        #   both untouched (SC-005)
```

**Structure Decision**: Single-project layout, purely additive under `tests/`. Two new test
modules live in `tests/unit/` (sibling to, never editing, `test_dax_gen.py` / `test_sql.py`).
A new `tests/fixtures/golden/` directory holds every golden file this feature introduces,
mirroring the repo's existing `tests/fixtures/<category>/` sibling convention (`contracts/`,
`sql/` already exist next to it). No file outside `tests/` is created or edited by this
feature; `warehouse/migrations/000{3,4}_*.sql` and `tests/fixtures/contracts/*.yaml` are read as
existing, unmodified INPUT. No `src/retail/rules/` module, no `docs/readiness/` artifact, and no
`.claude/skills/` file is added or changed -- this feature has no rule surface and no skill
surface at all.

## Complexity Tracking

*Empty -- the Constitution Check above identified no violation on any engaged principle.*
