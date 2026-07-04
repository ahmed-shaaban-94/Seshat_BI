---

description: "Task list for 093-reload-idempotency-readiness (Reload / Idempotency Readiness -- Anti-Double-Count, rule id HR7)"
---

# Tasks: Reload / Idempotency Readiness (Anti-Double-Count)

**Input**: Design documents from `specs/093-reload-idempotency-readiness/`
(spec.md, plan.md, research.md, data-model.md, quickstart.md)

**Tests**: Included -- plan.md's Testing section requires rule-behavior tests
over fixtures (drop-and-rebuild -> zero Findings; bare-append-no-declaration
-> one ERROR; declared-deviation -> zero Findings; in-SQL-key-only -> zero
Findings; mixed-pattern -> per-table classification); this is a fail-closed
governance rule, not optional coverage.

**Status carried from plan.md**: the Constitution Check passed with no
Complexity Tracking entries. One genuine Principle-V question --
Q-APPROVAL-SEAM (FR-013) -- stays OPEN with a recorded PENDING mechanical
default; no task below rules on it.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3), or
  `SETUP`/`FOUND`/`POLISH` for cross-cutting phases
- Every task names an exact repo-relative file path

## Path Conventions

Single project (`src/retail/`, `tests/`, `docs/`, `warehouse/`) at repository
root, per plan.md "Structure Decision". No new project/service/top-level
directory. Module and test file names below follow plan.md's Project
Structure exactly: `src/retail/rules/reload_idempotency.py` and
`tests/unit/test_reload_idempotency.py` (NOT the `rule_hr7.py` naming some
older rule modules use -- plan.md is the binding path for this feature).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Docs-first per hard rule #8 -- confirm the landing precondition
and author/update the human-readable declaration contract BEFORE any
static-rule wiring or code exists. Unlike 087/HR1 (which landed RED and
needed an owner-authorized empty scaffold), HR7 lands GREEN on the current
tree with zero Findings and creates NO new file at Setup time (research.md
"Landing analysis" -- `warehouse/load-policy.md` stays undocumented-on-disk
because zero migrations are deviations today).

- [ ] **T001** `[SETUP]` Confirm the landing precondition (research.md
  "Landing analysis"): read `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`
  and confirm it is full drop-and-rebuild (`DROP TABLE IF EXISTS` for every
  fact/dim, then a clean `INSERT ... SELECT`, no `ON CONFLICT`, no bare
  append, no partition overwrite) and that `0003`/`0005` are silver (no
  `gold.*` target) and therefore out of HR7's scope. Plain confirmation
  against the real tree, not an owner ruling. _Satisfies: spec.md SC-001,
  research.md Landing analysis._
- [ ] **T002** `[SETUP]` Confirm `warehouse/load-policy.md` does NOT exist on
  the current tree (glob check) and record that this feature does NOT create
  it (research.md Corollary; plan.md Project Structure: "NOT created by this
  feature"). No file is written by this task. _Satisfies: FR-014, Edge Cases
  "load-policy.md does not exist at all"._
- [ ] **T003** `[SETUP]` Edit `docs/readiness/gold-ready.md`: add HR7 to the
  "Required checks" static row (alongside S6/S7/S8), and add one sentence
  stating a passing HR7 does NOT prove a live rerun is duplicate-free -- that
  proof stays with RC2 (grain/PK uniqueness) and RC16 (penny-exact
  reconciliation) under `retail validate`, unaltered by this feature.
  _Satisfies: FR-009, US3 Independent Test, plan.md Project Structure doc
  edit._
- [ ] **T004** `[SETUP]` Author the `warehouse/load-policy.md` SHAPE as a
  documentation note (data-model.md "warehouse/load-policy.md" section) --
  place it in `docs/readiness/gold-ready.md` (T003) or as a short comment
  block cross-referenced from there, describing: the file is optional, its
  absence is never an ERROR while zero migrations are deviations, and its
  minimal entry shape (migration filename, target table, a
  `reload-strategy: <key1>[, <key2>...]` marker). Do NOT create
  `warehouse/load-policy.md` itself (T002). ASCII, UTF-8 no BOM (Principle
  IX). _Satisfies: FR-004, FR-014, data-model.md "shape documented, not
  created"._

**Checkpoint**: the declaration contract (where a deviation load declares its
key, and that a static pass is not live proof) is documented for a human
reader before any rule code or wiring exists, and the landing precondition is
confirmed against the real tree.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Reserve the rule id across every wiring surface and produce a
stub module, mirroring the SF1/AP1/HR1 seven-surface wiring discipline
(research.md "Wiring points and target count"). **No Finding-emitting logic
is implemented yet in this phase** -- only the scaffold that makes
`@register("HR7", ...)` compile and be discoverable.

**CRITICAL**: No user story (Phase 3+) can be implemented until this phase is
complete, because HR7 must exist as a registered (even if empty-bodied) rule
before its Finding logic can be tested via `retail check`.

- [ ] **T005** `[FOUND]` Create the stub rule module
  `src/retail/rules/reload_idempotency.py` with `RULE_ID = "HR7"`, a module
  docstring (mirrors `rule_ap1.py`/`sql.py`'s shape: what HR7 does, what it
  never does -- static-only, no DB, no grain re-derivation, no numeric
  score), and a `@register(RULE_ID, "reload-strategy declaration for gold
  loads")`-decorated `check_hr7(ctx: RuleContext) -> Iterable[Finding]` that
  returns `[]` (stub body; Phase 3+ fills it in). Import `tokenize_sql`,
  `schema_zone`, `iter_sql_files`, `is_test_path` per plan.md's Primary
  Dependencies (stdlib + existing `sql.py` helpers only -- no third-party
  parser). _Satisfies: FR-001, FR-007, FR-010._
- [ ] **T006** `[FOUND]` Edit `src/retail/rules/__init__.py`: add
  `reload_idempotency` to the side-effecting import tuple (alphabetical slot,
  after `readiness_status`, before `routes`) AND to `__all__` in the same
  commit -- the ONLY discovery step (no autodiscovery). _Satisfies: research.md
  wiring surface 2._
- [ ] **T007** `[P]` `[FOUND]` Edit `tests/unit/test_rules_wiring.py`: add
  `"HR7"` to `EXPECTED_RULE_IDS`. _Satisfies: research.md wiring surface 3._
- [ ] **T008** `[P]` `[FOUND]` Edit `docs/rules/rules-manifest.json`: add
  `{"id": "HR7", "title": "reload-strategy declaration for gold loads"}` in
  id order (after any existing `HR`-family or numerically-adjacent entry; if
  087/HR1 has not yet landed in this tree, insert HR7 in the natural id-sort
  position). Read the LIVE entry count first -- do not hardcode a stale
  count. _Satisfies: research.md wiring surface 4._
- [ ] **T009** `[P]` `[FOUND]` Edit `docs/rules/severity-posture.json`: add
  `"HR7": ["error"]` under the registered section (HR7 emits only
  `Severity.ERROR`, per data-model.md's Finding taxonomy -- fail-closed only,
  no WARNING posture). _Satisfies: research.md wiring surface 5, FR-005._
- [ ] **T010** `[FOUND]` Edit `docs/glossary.md`: add an `HR7` row to the
  "Static check rules" table describing the reload-strategy-declaration
  fail-closed posture in the same style as the `HR`/`S`-family rows; update
  the rule-count anchor text to the new live total (read the live count,
  do not hardcode a number from research.md's research-time snapshot).
  _Satisfies: research.md wiring surface 6._
- [ ] **T011** `[FOUND]` Edit `docs/quality/rule-count-claims.yaml`: bump the
  `claimed-count` entry to match T010's updated anchor text (byte-consistent
  reconciliation). _Satisfies: research.md wiring surface 7, SC-005._
- [ ] **T012** `[FOUND]` Run `pytest -m unit tests/unit/test_wiring_meta_gate.py
  tests/unit/test_rules_wiring.py tests/unit/test_glossary_rule_table.py` and
  confirm all green with the HR7 stub registered. _Satisfies: SC-005 (wiring
  + rule-count lockstep stays green)._

**Checkpoint**: `HR7` is a real, registered, discoverable rule (currently a
no-op) and every meta-gate lockstep is green. User story implementation can
now begin.

---

## Phase 3: User Story 1 - A drop-and-rebuild migration passes with no extra declaration (Priority: P1) MVP

**Goal**: Given a gold migration that drops every fact/dim with
`DROP TABLE IF EXISTS` and recreates via a clean `INSERT ... SELECT` with no
append/upsert logic, HR7 classifies it `FULL_DROP_AND_REBUILD` and emits no
Finding, requiring no declaration in either allowed location.

**Independent Test**: run `retail check` against the committed
`0004_create_gold_retail_store_sales_star.sql`; HR7 emits no Finding.

### Tests for User Story 1

> Write these tests FIRST; they exercise the Phase 2 stub (trivially GREEN,
> since the stub always returns `[]`) then must stay GREEN once Phase 3
> implementation lands the real classification logic.

- [ ] **T013** `[P]` `[US1]` In `tests/unit/test_reload_idempotency.py`: add a
  `tmp_path`-based helper (mirrors `test_sql.py`'s `RuleContext(repo_root=
  tmp_path, tracked_files=...)` pattern) that writes an inline SQL fixture
  string to a `warehouse/migrations/NNNN_*.sql` path under `tmp_path` and
  returns a `RuleContext`. _Satisfies: US1 Independent Test scaffolding,
  plan.md Testing section._
- [ ] **T014** `[P]` `[US1]` Using T013's helper, write
  `test_hr7_full_drop_and_rebuild_passes_with_no_finding` asserting
  `check_hr7(ctx)` returns zero Findings for a fixture SQL text shaped like
  the real `0004` migration (`CREATE SCHEMA IF NOT EXISTS gold`,
  `DROP TABLE IF EXISTS gold.<fact>` and `gold.<dim>`, then
  `INSERT INTO gold.<table> SELECT ...`, no `ON CONFLICT`, no bare append, no
  declaration marker anywhere). _Satisfies: US1 Acceptance Scenario 1, SC-001._
- [ ] **T015** `[P]` `[US1]` Extend the same test module with
  `test_hr7_full_drop_and_rebuild_requires_no_declaration` -- the same
  fixture as T014, explicitly confirmed to carry NO `reload-strategy:` marker
  in its header comment and no `warehouse/load-policy.md` in
  `ctx.tracked_files` -- still zero Findings. _Satisfies: US1 Acceptance
  Scenario 2, FR-003._
- [ ] **T016** `[P]` `[US1]` Add
  `test_hr7_passes_against_the_real_committed_migration_set` that runs
  `check_hr7` against a `RuleContext` built from the ACTUAL repo (reading
  `warehouse/migrations/0003_create_silver_retail_store_sales.sql`,
  `0004_create_gold_retail_store_sales_star.sql`,
  `0005_create_silver_demo_sample_orders.sql` from the real repo root) and
  asserts zero Findings -- the direct SC-001/US1-Acceptance-Scenario-3 proof
  against the real tree, not just a synthetic fixture. _Satisfies: US1
  Acceptance Scenario 3, SC-001._
- [ ] **T016b** `[P]` `[US1]` Extend the same test module with
  `test_hr7_whole_table_truncate_then_insert_passes_with_no_finding` --
  a fixture SQL text using a WHOLE-TABLE, UNQUALIFIED
  `TRUNCATE gold.<table>` (no `WHERE`, no named partition/date-range) or
  unqualified `DELETE FROM gold.<table>` immediately followed by a clean
  `INSERT ... SELECT`, and no declaration anywhere; assert zero Findings.
  Also add a sibling assertion (or a second test function) that a
  `DELETE FROM gold.<table> WHERE <date-range>` (a PARTIAL, boundary-named
  clear) with the same no-declaration setup still classifies as `DEVIATION`
  and produces an ERROR, to pin the whole-table-vs-partial boundary. _Satisfies:
  FR-002, Q-TRUNCATE-CLASS (spec.md Clarifications "Session 2026-07-04"), Edge
  Cases distinguishing whole-table clear from FR-006's partition/date-range
  overwrite._

### Implementation for User Story 1

- [ ] **T017** `[US1]` In `reload_idempotency.py`: implement
  `_is_gold_migration(toks) -> bool` -- `True` only if the tokenized SQL
  contains `CREATE SCHEMA IF NOT EXISTS gold` or a DDL/DML statement
  qualifying a `gold.<table>` target, via `schema_zone()` (never filename
  pattern-matching). Depends on T005. _Satisfies: FR-001, data-model.md
  GoldMigrationSignal._
- [ ] **T018** `[US1]` In `reload_idempotency.py`: implement
  `_classify_table_load(toks, target_table) -> ReloadStrategy` -- for a given
  `gold.<table>` target within one migration's tokens, classify as
  `FULL_DROP_AND_REBUILD` when EITHER (a) a `DROP TABLE IF EXISTS <target>` is
  followed later by a clean `INSERT ... SELECT` into the same target with no
  `ON CONFLICT` and no partial clear, OR (b) a WHOLE-TABLE, UNQUALIFIED
  `TRUNCATE <target>` or unqualified `DELETE FROM <target>` (no `WHERE`
  clause, no named partition/date-range boundary) is followed later by the
  same clean `INSERT ... SELECT` -- per Q-TRUNCATE-CLASS's resolved default
  (spec.md Clarifications), a whole-table clear is idempotency-equivalent to
  `DROP TABLE` and requires no declaration. Anything else -- a bare append
  `INSERT` with no prior drop/whole-table-clear, an `ON CONFLICT` upsert, or a
  `TRUNCATE`/`DELETE ... WHERE <date-range>`/named-partition boundary before
  insert -- classifies as `DEVIATION`. Depends on T017. _Satisfies: FR-002,
  Q-TRUNCATE-CLASS, data-model.md ReloadStrategy + MigrationTableLoad._
- [ ] **T019** `[US1]` In `reload_idempotency.py`: implement `check_hr7`'s
  main loop -- for each file in `iter_sql_files(ctx)` skipping
  `is_test_path(rel)`, tokenize via `tokenize_sql`, skip if
  `_is_gold_migration` is `False`, else resolve every `gold.<table>` target
  in the file and classify each via `_classify_table_load`; for now (US1
  scope) simply confirm `FULL_DROP_AND_REBUILD` targets contribute no
  Finding (DEVIATION handling lands in US2). Depends on T017, T018. Replaces
  the T005 stub body. _Satisfies: FR-002, FR-003._
- [ ] **T020** `[US1]` Run `tests/unit/test_reload_idempotency.py`
  (T014-T016, T016b) against the Phase 3 implementation and confirm GREEN,
  including against the real committed migration set (T016) and the
  whole-table-TRUNCATE-passes-free case (T016b). _Satisfies: US1 Independent
  Test, SC-001, Q-TRUNCATE-CLASS._

**Checkpoint**: HR7 correctly classifies full drop-and-rebuild and passes
with zero Findings on 100% of the current committed migration set. This is
the MVP slice -- independently testable and deployable, and it is the
default path the feature must never tax (Principle VI).

---

## Phase 4: User Story 2 - An incremental/append load with no declared key fails closed (Priority: P1)

**Goal**: A gold migration whose load is a DEVIATION (bare append `INSERT`
with no prior drop, an `ON CONFLICT` upsert, or a partition/date-range
overwrite) with no declared dedup/overwrite key in either allowed location
produces exactly one `Finding(HR7, ERROR, ...)` naming the migration file (and
table, for a per-table deviation in a mixed migration). An in-SQL key
(`ON CONFLICT`, or an explicit partition/date-range boundary) or a
`reload-strategy:` marker (header comment or `warehouse/load-policy.md`)
clears the Finding.

**Independent Test**: author (test-fixture only, never executed) a bare
append `INSERT INTO gold.<table>` migration with no drop/merge/declaration ->
one ERROR Finding naming the file; add a declaration -> Finding clears.

### Tests for User Story 2

> Write these tests FIRST; they FAIL against the Phase 3 implementation
> (which has no DEVIATION/declaration-reading branches yet), then PASS once
> Phase 4 implementation lands.

- [ ] **T021** `[P]` `[US2]` In `tests/unit/test_reload_idempotency.py`: add
  `test_hr7_bare_append_with_no_declaration_fails_closed` -- a fixture SQL
  text with `CREATE SCHEMA IF NOT EXISTS gold` and a bare
  `INSERT INTO gold.<table> SELECT ...` with NO `DROP TABLE`, NO
  `ON CONFLICT`, NO `TRUNCATE`, and NO `reload-strategy:` marker anywhere;
  assert exactly one `Severity.ERROR` Finding naming the migration file and
  stating the declaration is required and absent. _Satisfies: US2 Acceptance
  Scenario 1, FR-005, SC-002._
- [ ] **T022** `[P]` `[US2]` Extend with
  `test_hr7_bare_append_with_header_comment_declaration_clears_finding` --
  the same fixture as T021 plus a single-line
  `-- reload-strategy: <key1>, <key2>` marker in the migration's header
  comment; assert zero Findings. _Satisfies: US2 Acceptance Scenario 2 (header
  comment limb), FR-004, SC-002._
- [ ] **T023** `[P]` `[US2]` Extend with
  `test_hr7_bare_append_with_load_policy_declaration_clears_finding` -- the
  T021 fixture with NO header-comment marker, plus a `warehouse/load-policy.md`
  file (added to `ctx.tracked_files`) naming the migration filename, the
  target table, and the `reload-strategy: <key(s)>` marker; assert zero
  Findings. _Satisfies: US2 Acceptance Scenario 2 (load-policy.md limb),
  FR-004, FR-014._
- [ ] **T024** `[P]` `[US2]` Extend with
  `test_hr7_load_policy_file_ignored_when_untracked` -- the T021 fixture plus
  a `warehouse/load-policy.md` written to `tmp_path`'s disk but NOT included
  in `ctx.tracked_files`; assert the ERROR Finding STILL fires (the untracked
  copy must not satisfy the declaration). _Satisfies: plan.md Constraints
  ("gated on `ctx.tracked_files` membership"), Principle IX reproducibility._
- [ ] **T025** `[P]` `[US2]` Extend with
  `test_hr7_on_conflict_upsert_satisfies_declaration_without_marker` -- a
  fixture whose load uses `INSERT INTO gold.<table> ... ON CONFLICT (<key>)
  DO UPDATE ...` with NO separate `reload-strategy:` marker anywhere; assert
  zero Findings. _Satisfies: US2 Acceptance Scenario 3 (upsert limb), FR-006._
- [ ] **T026** `[P]` `[US2]` Extend with
  `test_hr7_partition_overwrite_satisfies_declaration_without_marker` -- a
  fixture whose load does a `DELETE FROM gold.<table> WHERE <date-range>` (or
  `TRUNCATE PARTITION`-style boundary) immediately before an `INSERT`, naming
  the boundary, with NO separate marker; assert zero Findings. _Satisfies: US2
  Acceptance Scenario 3 (partition-overwrite limb), FR-006._
- [ ] **T027** `[P]` `[US2]` Extend with
  `test_hr7_mixed_migration_classifies_per_table` -- a single fixture
  migration that drops-and-rebuilds one target table (e.g. a dimension) AND
  bare-appends into a second target table (e.g. a fact) with no declaration
  for the second; assert EXACTLY one ERROR Finding naming the SECOND table
  only -- the drop-and-rebuilt table contributes no Finding. _Satisfies: Edge
  Cases "mixes patterns", data-model.md MigrationTableLoad per-table scope._
- [ ] **T028** `[US2]` Run `tests/unit/test_reload_idempotency.py`
  (T021-T027) against the Phase 3 implementation and confirm they FAIL (no
  DEVIATION/declaration branch exists yet) before starting implementation
  below. _Satisfies: TDD RED-before-GREEN discipline._

### Implementation for User Story 2

- [ ] **T029** `[US2]` In `reload_idempotency.py`: implement
  `_in_sql_key(toks, target_table) -> str | None` -- extract the key list from
  an `ON CONFLICT (<key1>, <key2>...) DO UPDATE` clause targeting
  `target_table`, OR the boundary named in a `DELETE ... WHERE`/`TRUNCATE`
  immediately preceding an `INSERT` into `target_table`; `None` if neither is
  present. Depends on T018. _Satisfies: FR-006, data-model.md
  MigrationTableLoad.in_sql_key._
- [ ] **T030** `[US2]` In `reload_idempotency.py`: implement
  `_scan_reload_strategy_markers(raw_text) -> list[str]` -- a line-oriented,
  RAW-text (non-tokenized, non-comment-stripped) scan for a single-line
  `reload-strategy: <key1>[, <key2>...]` marker inside a `--` comment,
  per research.md's "Read-path subtlety" (mirrors S6/S8's `_strip_sql_noise`
  precedent for reading a comment-preserved literal `tokenize_sql` would
  otherwise discard). Returns the parsed, comma-separated key list. Depends
  on T005. _Satisfies: FR-004, research.md Read-path subtlety._
- [ ] **T031** `[US2]` In `reload_idempotency.py`: implement
  `_load_policy_entries(ctx) -> list[LoadPolicyEntry]` -- if
  `"warehouse/load-policy.md"` is a member of `ctx.tracked_files`, read it via
  the same tracked-files-gated read path `iter_sql_files` uses (never the raw
  working tree) and parse each entry for its migration filename, target
  table, and `reload-strategy:` marker (per data-model.md's
  `warehouse/load-policy.md` shape); return `[]` if the file is absent or not
  tracked -- absence is never an ERROR. Depends on T005. _Satisfies: FR-004,
  FR-014, Edge Cases "load-policy.md does not exist", Principle IX
  (tracked-files-gated read)._
- [ ] **T032** `[US2]` In `reload_idempotency.py`: implement
  `_has_declaration(ctx, migration_path, target_table, header_raw_text,
  in_sql_key, load_policy_entries) -> bool` -- `True` if `in_sql_key` is
  present, OR a `reload-strategy:` marker is found in the migration's own
  header comment (T030 applied to `header_raw_text`), OR a matching
  `LoadPolicyEntry` (same migration filename + same target table) carries a
  `reload-strategy:` marker (T031). Depends on T029, T030, T031. _Satisfies:
  FR-004, FR-006._
- [ ] **T033** `[US2]` In `reload_idempotency.py`: extend `check_hr7`'s main
  loop (from T019) -- for each `DEVIATION`-classified table load, call
  `_has_declaration`; if `False`, emit
  `Finding(HR7, Severity.ERROR, message naming the migration file (and table,
  for a per-table deviation), locator=migration_path)` stating a
  reload-strategy declaration is required and absent; if `True`, emit no
  Finding for that table. Depends on T018, T032. _Satisfies: FR-005, FR-002
  (per-table), Edge Cases "mixes patterns", US2 all three Acceptance
  Scenarios._
- [ ] **T034** `[US2]` Run `tests/unit/test_reload_idempotency.py`
  (T021-T027) against T029-T033 and confirm GREEN, including the
  mutation-verify direction (remove a fixture's declaration and confirm the
  ERROR reappears; add it back and confirm it clears). _Satisfies: US2
  Independent Test, SC-002._

**Checkpoint**: HR7 now fails closed on an undeclared deviation load, per
table within a mixed migration, and correctly recognizes an in-SQL key or
either declaration location as clearing the Finding. This is the feature's
"whole point" story (spec.md US2 rationale) and is co-equal in priority with
US1.

---

## Phase 5: User Story 3 - HR7 stays static-only; live proof remains deferred (Priority: P2)

**Goal**: HR7 never opens a database connection, never executes or simulates
a reload, and its Finding/pass messaging plus the Gold Ready doc never claim
or imply that a static pass proves a live rerun is duplicate-free -- that
proof stays with RC2/RC16 under `retail validate`, unaltered by this feature.

**Independent Test**: inspect HR7's Finding/pass message text and the
`docs/readiness/gold-ready.md` update; confirm neither states or implies live
proof; confirm the module imports no DB driver and opens no connection.

### Tests for User Story 3

- [ ] **T035** `[P]` `[US3]` In `tests/unit/test_reload_idempotency.py`: add a
  source-inspection test `test_hr7_module_imports_no_database_driver` that
  reads `src/retail/rules/reload_idempotency.py`'s source text and asserts it
  contains no `import psycopg`/`import sqlalchemy`/`.connect(`/DSN-shaped
  string, and does not import or reference the `db` extra. _Satisfies: FR-007,
  FR-010, SC-004._
- [ ] **T036** `[P]` `[US3]` Extend with
  `test_hr7_messages_contain_no_numeric_score_or_live_proof_claim` -- run
  `check_hr7` against T021's (undeclared-deviation) and T014's
  (drop-and-rebuild) fixtures and assert no emitted Finding message contains
  a numeric percentage/ratio/"N of M" pattern, and no message contains
  language implying a passing declaration proves a live rerun is
  duplicate-free (e.g. assert absence of phrases like "proves" / "guaranteed
  duplicate-free" adjacent to "HR7" or "declared"). _Satisfies: FR-009,
  FR-012, SC-003._
- [ ] **T037** `[P]` `[US3]` Add a doc-inspection test (or manual-confirm
  checklist item if no existing doc-assertion test pattern exists in this
  repo -- check `tests/unit/` for a precedent first) reading
  `docs/readiness/gold-ready.md`'s HR7-related sentence (T003) and asserting
  it does not claim or imply a static HR7 pass proves live idempotency, and
  that RC2/RC16 are still named as the live proof. _Satisfies: US3 Independent
  Test, FR-009._

### Implementation for User Story 3

- [ ] **T038** `[US3]` Review `reload_idempotency.py`'s Finding message
  strings (from T033) and `docs/readiness/gold-ready.md`'s T003 sentence;
  edit either if T036/T037 surface any implied live-proof language or any
  numeric formatting, until both tests pass. Depends on T033, T003. _Satisfies:
  FR-009, FR-012._
- [ ] **T039** `[US3]` Confirm (checklist, no file edit) that HR7's Gold Ready
  composition does not substitute for or mask RC2/RC16's blocked-deferred
  state when no DSN/`db` extra is configured -- HR7 is a static rule read by
  `retail check`, entirely separate from `retail validate`'s live composition,
  so this is a structural confirmation that HR7 adds no code path touching
  the live composition at all. _Satisfies: US3 Acceptance Scenario 1, FR-010._
- [ ] **T040** `[US3]` Run `tests/unit/test_reload_idempotency.py`
  (T035-T037) and confirm GREEN. _Satisfies: US3 Independent Test, SC-003,
  SC-004._

**Checkpoint**: All three user stories are independently functional. HR7 is
static-only, fails closed on undeclared deviations, passes free on the
default, and makes no claim beyond "a key is declared."

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: The remaining requirements that cut across US1/US2/US3 --
grain/PK non-interference (FR-011), generic-naming verification (FR-015),
additivity (FR-017), the OPEN Principle-V seam (FR-013), encoding (FR-016),
and final gate/documentation sign-off.

- [ ] **T041** `[P]` `[POLISH]` Add
  `test_hr7_never_reads_or_writes_source_map_yaml` to
  `tests/unit/test_reload_idempotency.py` -- source-inspection test asserting
  `reload_idempotency.py` contains no reference to `source-map.yaml` and does
  not re-derive or compare a table's grain/primary key. _Satisfies: FR-004
  (collision-avoidance), FR-011, SC-006 (mechanically verified)._
- [ ] **T042** `[P]` `[POLISH]` Grep
  `src/retail/rules/reload_idempotency.py` and every doc edit from Phase 1/2
  (T003, T004, T008, T010) for any C086/`retail_store_sales`/domain-specific
  table or column name outside an explicitly labeled illustrative example;
  confirm any such name appears only in illustrative comments, never as a
  required literal in rule logic. _Satisfies: FR-015, SC-006._
- [ ] **T043** `[P]` `[POLISH]` Add
  `test_hr7_does_not_alter_existing_sql_rule_findings` to
  `tests/unit/test_reload_idempotency.py` (or extend `tests/unit/test_sql.py`
  if that is the more natural home) -- run the full rule registry (or S6/S7/S8
  specifically) against the same fixtures used in `test_sql.py` before and
  after HR7's registration and assert identical Finding output for every
  non-HR7 rule id. _Satisfies: FR-017, SC-005 (additivity, mechanically
  verified)._
- [ ] **T044** `[POLISH]` [OWNER SEAM -- OPEN, do not answer] Record
  Q-APPROVAL-SEAM (FR-013) as still OPEN in the feature's closing state -- no
  `approvals[]` shape is added, no `readiness-status.yaml` key is touched, and
  HR7 records no model-level pass anywhere beyond what a clean static check
  already contributes (same as S6/S7/S8/HR1). This task is a checklist
  confirmation, not a resolution. _Satisfies: FR-013 PENDING DEFAULT posture,
  Principle V guard._
- [ ] **T045** `[POLISH]` Confirm every authored/edited artifact this feature
  touches (`reload_idempotency.py`, `test_reload_idempotency.py`, the four
  Phase 1/2 doc edits) is ASCII, UTF-8 without BOM, using short repo-relative
  paths well inside the Windows 260-char budget. _Satisfies: FR-016,
  Principle IX._
- [ ] **T046** `[POLISH]` Run the full local gate:
  `ruff format --check src/ tests/`, `ruff check src/ tests/`,
  `pytest -m unit -x -q`, then `retail check` -- confirm GREEN on the current
  tree (T001's confirmed drop-and-rebuild migration passes HR7 with zero
  Findings; no existing migration requires an edit). _Satisfies: SC-001,
  SC-004, SC-005, plan.md local-verification requirement._
- [ ] **T047** `[POLISH]` Confirm `tests/unit/test_wiring_meta_gate.py`,
  `tests/unit/test_rules_wiring.py`, and `tests/unit/test_glossary_rule_table.py`
  all still pass with `HR7` present in `all_rules()`, `EXPECTED_RULE_IDS`,
  `rules-manifest.json`, `severity-posture.json`, and `docs/glossary.md`'s
  rule table. _Satisfies: SC-005._

**Checkpoint**: Feature complete, gate green, no numeric score anywhere, no
domain-specific name baked into generic artifacts, wiring lockstep intact,
existing rules unaltered, and the one genuinely open governance question
(FR-013) is left open rather than silently decided.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies; can start immediately. T003 and T004
  may proceed in parallel with each other but both belong to Setup because
  they are documentation, authored before any code (hard rule #8, docs before
  automation).
- **Foundational (Phase 2)**: depends on Setup only loosely (the doc edits in
  T003/T004 are not a hard input to the stub module) but is sequenced after
  Setup per hard rule #8's docs-before-wiring ordering. T006 depends on T005;
  T007-T009 are parallel edits once T005 exists; T010 depends on T005 (needs
  the final rule title); T011 depends on T010 (count must match anchor); T012
  depends on T006-T011 all landing. BLOCKS all user stories.
- **User Stories (Phase 3-5)**: all depend on Foundational (Phase 2)
  completion (HR7 must be a registered, importable rule before its body can
  be tested). US1 (Phase 3) has no dependency on US2/US3. US2 (Phase 4) reuses
  US1's `_is_gold_migration`/`_classify_table_load` helpers (T017/T018) but
  adds its own declaration-reading branches -- implemented after US1 lands so
  those helpers exist. US3 (Phase 5) depends on US2's T033 (the Finding
  messages it inspects) and T003 (the doc sentence it inspects).
- **Polish (Phase 6)**: depends on US1 + US2 + US3 all landing (T043's
  additivity check and T046's full gate run need the complete rule body).

### Within Each User Story

- Tests written first (RED where the behavior does not yet exist -- US2/US3);
  implementation follows; GREEN re-run task closes each story.
- `_is_gold_migration` / `_classify_table_load` (T017-T018) are shared
  read-only helpers built once in Phase 3 and reused (not reimplemented) by
  Phase 4.
- `_in_sql_key` / `_scan_reload_strategy_markers` / `_load_policy_entries` /
  `_has_declaration` (T029-T032) are shared helpers built once in Phase 4 and
  reused by Phase 5's inspection tests (T035-T037 read the same module).

### Parallel Opportunities

- T007, T008, T009 (three different wiring-surface files) can run in parallel
  once T005/T006 exist.
- T013-T016, T016b (US1 fixtures/tests, all in the same new test module but
  independent test functions) can be drafted in parallel before T017-T019
  implementation.
- T021-T027 (US2 fixtures/tests, independent test functions in the same
  module) can be drafted in parallel before T029-T033 implementation.
- T035-T037 (US3 inspection tests) can run in parallel with each other.
- T041-T043 (Polish verification tests) touch the same test module as
  sibling functions and can be drafted in parallel, though they should be
  added as separate test functions to avoid merge conflicts within one file.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational) -- HR7 registered as a
   no-op, wiring green.
2. Complete Phase 3 (US1) -- full drop-and-rebuild classifies correctly and
   passes free on 100% of the current committed migration set.
3. **STOP and VALIDATE**: run T020's tests independently, including against
   the real repo (T016).
4. This is the MVP: the default path the feature must never tax (Principle
   VI) is proven safe before the fail-closed case is added.

### Incremental Delivery

1. Setup + Foundational -> HR7 registered, no-op, gate green, declaration
   contract documented.
2. Add US1 -> the default (drop-and-rebuild) path stays free -- zero
   regression risk to the current committed tree.
3. Add US2 -> the fail-closed anti-double-count gate itself (the feature's
   stated "whole point," spec.md US2 rationale).
4. Add US3 -> the static-only / no-live-proof-claim guardrail (P2, a
   guardrail on the feature's own claims rather than new capability).
5. Polish -> additivity, generic-naming, encoding, and the OPEN
   Q-APPROVAL-SEAM checklist confirmation.

### Requirement Coverage Check (every FR maps to >=1 task)

- FR-001 -> T005, T017
- FR-002 -> T018, T019, T033, T016b (Q-TRUNCATE-CLASS whole-table-clear default)
- FR-003 -> T015, T019
- FR-004 -> T004, T022, T023, T029, T030, T031, T032, T041
- FR-005 -> T021, T033
- FR-006 -> T025, T026, T029, T032
- FR-007 -> T005, T035
- FR-008 -> T030 (structural marker parse only, no live-schema check --
  implicit in `_scan_reload_strategy_markers`/`_has_declaration` never
  querying a DB)
- FR-009 -> T003, T036, T037, T038, T039
- FR-010 -> T005, T024, T035, T039
- FR-011 -> T041
- FR-012 -> T036, T040
- FR-013 -> T044
- FR-014 -> T002, T004, T023, T024, T031
- FR-015 -> T042
- FR-016 -> T045
- FR-017 -> T043, T046, T047
