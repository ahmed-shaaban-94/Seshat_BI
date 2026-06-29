# Tasks: Live-Surface Import Boundary Guard (B3)

**Feature**: `048-live-surface-import-boundary-guard`
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Contract**: [contracts/rule-contract.md](./contracts/rule-contract.md)

TDD is the repo default (RED -> GREEN -> refactor). Test tasks precede the
implementation they cover. All paths are repo-relative.

Scope guard (YAGNI / first step): add ONE registered static rule that reuses B1's
AST helper unchanged, an explicit live-surface module-set constant, the wiring-id
update, the regenerated manifest, and a firing test. Change NO behavior of the
four scanned modules. Add NO new dependency, executor, or severity tier. The
B-family registry id and the final module-set membership are placeholders pending
human ratification (spec ## Clarifications) -- pick a non-colliding working id at
build time and leave a note; do not invent a readiness stage.

## Phase 1: Setup

- [ ] T001 Confirm the reusable surface in `src/retail/rules/never_execute.py`
  (`module_scope_violations`, `_FORBIDDEN_ROOTS`, `_FORBIDDEN_DOTTED`,
  `_is_forbidden`) is importable and unchanged; record the chosen non-colliding
  B-family working rule id (pending human ratification per spec ## Clarifications)
  in a code comment at the top of the new rule module.

## Phase 2: Foundational (blocking prerequisites)

- [ ] T002 Read `tests/unit/test_rules_wiring.py` to confirm `EXPECTED_RULE_IDS`
  is a frozenset whose length drives the snapshot count (no literal baseline), and
  read `docs/rules/rules-manifest.json` + the `retail manifest` subcommand in
  `src/retail/cli.py` to confirm the regeneration path before adding an id.

## Phase 3: User Story 1 -- A regressed live-surface import fails the gate (P1)

**Goal**: A module-scope connection-capable import in a live-surface module
produces an ERROR Finding; the approved lazy / TYPE_CHECKING pattern does not.

**Independent test**: Invoke the rule against synthetic source strings (bad and
good) and assert Findings / no Findings per contract C1-C5.

- [ ] T003 [US1] Add `tests/unit/test_live_surface_boundary.py` with RED tests
  asserting contract C1 (module-scope `import psycopg2` in a live-surface module
  path -> one ERROR Finding naming the import, locator = that module) and C2
  (same import lazy inside a function, and under `if TYPE_CHECKING:` -> no
  Finding). Use synthetic source strings + a fake `RuleContext` (generic paths
  only; no domain artifact).
- [ ] T004 [US1] Extend `tests/unit/test_live_surface_boundary.py` with RED tests
  for contract C3 (module-scope `try: import psycopg2 except ImportError:` and a
  module-level `if`/`else` forbidden import -> flagged), C4 (unparseable source ->
  fail-loud ERROR Finding), and C5 (`from urllib.parse import quote` -> no
  Finding).
- [ ] T005 [US1] Create `src/retail/rules/live_surface_boundary.py`: import the
  shared helper + forbidden sets from `..rules.never_execute` (no fork), define
  the explicit `_LIVE_SURFACE` module-set constant (candidate
  `{validate, value_proxy, semantic, dax_gen}` as repo-relative POSIX paths,
  disjoint from B1's set), and implement the `@register`ed checker that scans only
  those tracked files, emits `Severity.ERROR` Findings per violation, and converts
  `SyntaxError` into a fail-loud ERROR Finding. Make T003/T004 GREEN.
- [ ] T006 [US1] Run `pytest -m unit tests/unit/test_live_surface_boundary.py` and
  `retail check`; confirm tests pass and `retail check` reports zero new Findings
  on the current tree (the four modules are already lazy -> the rule is green
  today, fires only on regression -- contract C10).

## Phase 4: User Story 2 -- The new rule is genuinely wired, not just listed (P1)

**Goal**: The id is in the registry, the regenerated manifest, and the wiring
expected set, AND the rule is exercised firing (close the wiring-latent-gap).

**Independent test**: The snapshot/wiring test passes with the new id; a direct
test observes the rule fire on a known-bad fixture.

- [ ] T007 [US2] Add the chosen working rule id to `EXPECTED_RULE_IDS` in
  `tests/unit/test_rules_wiring.py` (with a one-line comment), keeping the set the
  single source of truth; do NOT introduce any literal baseline count.
- [ ] T008 [US2] Regenerate `docs/rules/rules-manifest.json` via
  `retail manifest --repo .` so it contains the new id; verify it is the only
  intended diff.
- [ ] T009 [US2] Run `pytest -m unit tests/unit/test_rules_wiring.py`; confirm the
  live registry id set equals `EXPECTED_RULE_IDS`, `len(all_rules()) ==
  len(EXPECTED_RULE_IDS)`, and the rule submodule is auto-discovered by `pkgutil`.
- [ ] T010 [US2] Confirm `tests/unit/test_live_surface_boundary.py` includes at
  least one test that invokes the rule directly on a known-bad fixture and asserts
  a non-empty Finding set (the rule FIRES, not merely registers -- FR-009 /
  SC-004); add it if not already covered by T003.

## Phase 5: User Story 3 -- Explicit, closed, schema-agnostic set (P2)

**Goal**: The module set is one explicit named collection of generic paths,
disjoint from B1's set; nothing references a domain artifact.

**Independent test**: Inspect the set definition and all fixtures.

- [ ] T011 [US3] Add a test in `tests/unit/test_live_surface_boundary.py`
  asserting the `_LIVE_SURFACE` set is disjoint from `never_execute._GOVERNED_MODULES`
  and that no member matches `never_execute._GOVERNED_PREFIX` (no double-coverage).
- [ ] T012 [US3] Review the rule module and every fixture; assert (in a test or by
  inspection note) they contain only generic module paths and library names -- no
  table / column / KPI (contract C8 / SC-005).

## Phase 6: Polish & Cross-Cutting

- [ ] T013 [P] Run `ruff` and the full `pytest -m unit` suite; confirm ASCII /
  UTF-8 no BOM in all new files and that no new third-party dependency, network
  call, or DB access was introduced (SC-006).
- [ ] T014 [P] Confirm the spec's three `[HUMAN RATIFY]` items (final module-set
  membership, the official B-family registry id, the readiness-stage question)
  remain recorded and unanswered; do not self-assign a readiness stage or a
  ratified id.

## Dependencies

- T001, T002 (Setup/Foundational) before all story phases.
- US1 (T003-T006) is the MVP; US2 (T007-T010) depends on the rule existing
  (T005). US3 (T011-T012) depends on the set existing (T005).
- T003/T004 (RED) before T005 (GREEN). T007/T008 before T009.
- Polish (T013-T014) last.

## Parallel opportunities

- T013 and T014 are independent ([P]).
- Within US1, T003 and T004 edit the same test file -> run sequentially.

## MVP scope

User Story 1 (T001-T006) alone delivers the protective value: a regressed
live-surface import fails the gate. US2 and US3 harden wiring integrity and scope
clarity.
