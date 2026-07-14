# Tasks: Public Extension-Pack Catalog

**Input**: Design documents from `specs/128-pack-catalog/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Required. Every story has contract, unit, or integration tests because the specification defines independently testable safety boundaries (a fail-closed retrieval gate).

**Organization**: Tasks are grouped by user story. Each story is independently releasable; User Story 1 (`search`) is the MVP. `[P]` marks tasks with no ordering dependency on each other within their phase. TDD: each story's tests precede its implementation.

**Status**: All tasks unchecked -- this is a spec-only chain (specify -> plan -> tasks -> analyze). No implementation has run; `/speckit-implement` is owner-gated.

## Phase 1: Setup

**Purpose**: Establish the one new versioned contract and the tracked static registry scaffold without changing any shipped runtime behavior.

- [ ] T001 Author the NEW registry-index contract `specs/128-pack-catalog/contracts/seshat-pack-registry.schema.json` (metadata ABOUT packs: id, version, category, author, source, compatibility, hash, dependencies, conflicts, verification_state; `additionalProperties: false`; required fields per FR-002). Do NOT modify `schemas/seshat-extension-pack.schema.json`.
- [ ] T002 Publish the registry-index contract to `schemas/seshat-pack-registry.schema.json` (RR-005; validated via the existing `validate_json_contract`).
- [ ] T003 [P] Create the tracked static registry scaffold `packs/registry/index.yaml` (empty/`records: []` initial) and `packs/registry/reference/` for generic declarative reference packs (FR-001; generic only, no C086/pharmacy specifics).
- [ ] T004 [P] Confirm `.gitignore` does NOT ignore `packs/registry/` (the registry is tracked repository text) and does NOT ignore any `definition/` folders (repo hard rule); add no new ignore for catalog state, since there is no activation state to persist (FR-012).

---

## Phase 2: Foundational Registry Core (US1 + US2 substrate)

**Purpose**: Parse and schema-validate the static registry index and expose read-only search/inspect over its metadata. Read-only; fetches nothing.

**CRITICAL**: Complete before any US that returns records.

- [ ] T005 [P] Write registry-index schema contract tests (valid reference records pass; records missing any required field, with a numeric verification_state, or with a duplicate id+version fail) in `tests/contract/test_pack_registry_schema.py` (FR-002, FR-003, FR-015, FR-020).
- [ ] T006 [P] Write registry parse/read unit tests: unreadable / non-UTF-8 / non-mapping registry fail closed with disclosure-safe messages; empty/absent registry yields zero records (FR-019, FR-021; edge cases).
- [ ] T007 Implement `src/seshat/packs/registry.py`: load + `validate_json_contract` the index against `schemas/seshat-pack-registry.schema.json`; build frozen registry-record models; reuse `disclosure` for safe messages; NO fetch, NO execution (FR-001, FR-003, RR-005).
- [ ] T008 Implement duplicate-id+version detection as a registry-defect finding in `src/seshat/packs/registry.py` (FR-020); the catalog must not silently choose one.

**Checkpoint**: The index is parseable and schema-checked; no user-facing verb yet.

---

## Phase 3: User Story 1 - Discover a Relevant Pack (Priority: P1) MVP

**Goal**: `pack search` returns matches from the reviewed static registry by keyword and category, showing identity + attribution + compatibility + verification state, fetching nothing.

**Independent Test**: Point at a reviewed registry with several records across categories; run keyword and category searches; verify displayed fields and that no content is fetched or executed.

- [ ] T009 [P] [US1] Write search unit tests: keyword match, category filter, empty-result "no matches", and that `unreviewed`/`deprecated` state is shown plainly in `tests/unit/test_pack_registry_search.py` (FR-004, FR-005, US1 scenarios 1-4).
- [ ] T010 [US1] Implement `search(registry, keyword, category)` in `src/seshat/packs/registry.py` returning matches with id, version, category, author, compatibility, verification_state (FR-004, FR-005). Read-only.
- [ ] T011 [US1] Add the `search` subparser to the existing `pack` verb group in `src/seshat/cli/parser_ecosystem.py` (`--registry`, `--query`, `--category`, `--format text|json`); do NOT alter `scaffold`/`validate` (RR-006).
- [ ] T012 [US1] Implement the `search` handler in `src/seshat/cli/commands/pack.py` (route via `pack_command == "search"`), preserving `author` attribution in output (FR-017), with stable exit codes.
- [ ] T013 [P] [US1] Integration test: `pack search` over a fixture registry returns expected matches and fetches nothing in `tests/integration/test_pack_catalog_search.py` (SC-001).

**Checkpoint**: A user can discover packs; nothing is fetched or added.

---

## Phase 4: User Story 2 - Inspect Before Retrieving (Priority: P2)

**Goal**: `pack inspect <id>` shows one full record (all required fields + declared dependencies + conflicts), fetching nothing.

**Independent Test**: Inspect one known id; verify the complete metadata record and that declared dependencies/conflicts are listed and nothing is fetched; inspect an absent id -> "not found".

- [ ] T014 [P] [US2] Write inspect unit tests: full-record display, dependency/conflict listing, and "not found" for an absent id in `tests/unit/test_pack_registry_inspect.py` (FR-006, US2 scenarios 1-4).
- [ ] T015 [US2] Implement `inspect(registry, pack_id)` in `src/seshat/packs/registry.py` returning the complete record or a "not found" outcome; read-only, no fetch (FR-006).
- [ ] T016 [US2] Add the `inspect` subparser to the `pack` verb group (`--registry`, positional/`--id`, `--format`) in `src/seshat/cli/parser_ecosystem.py` (RR-006).
- [ ] T017 [US2] Implement the `inspect` handler in `src/seshat/cli/commands/pack.py`, showing id, version, category, author, source, compatibility, hash, dependencies, conflicts, verification_state (FR-006, FR-017).
- [ ] T018 [P] [US2] Integration test: `pack inspect` shows the full record and fetches nothing in `tests/integration/test_pack_catalog_inspect.py` (SC-002).

**Checkpoint**: A user can read a full record before any content crosses into the workspace.

---

## Phase 5: User Story 3 - Fetch, Verify, and Explicitly Add (Priority: P3)

**Goal**: `pack add <id>` runs the full fail-closed chain (fetch -> hash -> content schema -> existing validation) and, only on all-pass, adds a verified declarative pack as a reviewable workspace change -- with no activation and no readiness promotion.

**Independent Test**: Add a clean pack -> content lands as a reviewable change, existing validation ran/passed, no activation state written, no stage advanced. Corrupt the content -> hash mismatch -> refused, nothing added.

### Tests first (fail-closed chain)

- [ ] T019 [P] [US3] Write hashing unit tests: SHA-256 over declarative content matches recorded hash; any byte change flips the verdict in `tests/unit/test_pack_catalog_hash.py` (FR-008).
- [ ] T020 [P] [US3] Write catalog fail-closed unit tests, one refusal class each: unknown id, hash mismatch (tamper), schema-invalid record, schema-invalid content, incompatible core, missing/dangling source, containment escape, disclosure hit, existing-validation finding, workspace collision -- each adds NOTHING and returns a disclosure-safe finding in `tests/unit/test_pack_catalog_fail_closed.py` (FR-008, FR-009, FR-010, FR-014, FR-019, FR-022).
- [ ] T021 [P] [US3] Write reuse-boundary tests asserting the catalog calls the SHIPPED `validate_pack` / `validate_selection` for content verdicts and the SHIPPED `scan_disclosure` / `resolve_within` for secrets/containment (no re-implementation) in `tests/unit/test_pack_catalog_reuse.py` (RR-001..RR-004, SC-005).
- [ ] T022 [P] [US3] Write no-side-effect tests: after a successful add no readiness stage advanced, no approval granted, no activation/toggle file written; added content is inert until explicitly selected in `tests/unit/test_pack_catalog_no_activation.py` (FR-011, FR-012, FR-013, SC-006).

### Implementation

- [ ] T023 [US3] Implement `src/seshat/packs/catalog.py` -- `fetch(record)` resolves the record source via `artifact_identity.resolve_within` (containment; missing -> refusal) and returns fetched content WITHOUT adding it (FR-007, FR-010, RR-003).
- [ ] T024 [US3] Implement hash verification in `catalog.py`: compute SHA-256 over fetched declarative content, compare to `record.hash`; mismatch -> tamper refusal naming the pack (FR-008).
- [ ] T025 [US3] Implement the verify-then-validate handoff in `catalog.py`: schema-check content against `schemas/seshat-extension-pack.schema.json` and run `validate_pack` + `validate_selection`; ANY finding -> refuse; also run `scan_disclosure` on content (FR-009, FR-010, FR-014, RR-001, RR-002, RR-004).
- [ ] T026 [US3] Implement the explicit, reviewable add in `catalog.py`: only on all-pass, write verified content into the workspace as an inspectable change; refuse on existing-content collision (FR-011, FR-012, FR-022); write NO activation state and touch NO readiness state (FR-013).
- [ ] T027 [US3] Enforce that verification_state is never set/upgraded at runtime and absence == NOT reviewed in `catalog.py`/`registry.py` (FR-015, FR-016; hard-stops `never_self_grant_approval`, `never_fabricate_a_confidence_score`).
- [ ] T028 [US3] Add the `add` subparser to the `pack` verb group (`--registry`, positional/`--id`, `--repo`, `--dest`, `--format`) in `src/seshat/cli/parser_ecosystem.py` (RR-006).
- [ ] T029 [US3] Implement the `add` handler in `src/seshat/cli/commands/pack.py` orchestrating fetch -> hash -> schema -> existing validation -> add, with stable exit codes (0 added, 1 refused-on-findings, 2 input defect) mirroring the shipped `validate` handler's code discipline (FR-007, FR-010, FR-019).
- [ ] T030 [P] [US3] Integration test: full search -> inspect -> add happy path lands content as a reviewable change, existing validation passed, no stage advanced in `tests/integration/test_pack_catalog_add.py` (SC-003, SC-006).
- [ ] T031 [P] [US3] Integration test: tampered pack (mutated content) and incompatible pack are each refused with nothing added in `tests/integration/test_pack_catalog_add_refusals.py` (SC-003, SC-004).

**Checkpoint**: The full retrieval journey is fail-closed, reuses shipped validation, and creates no activation state or readiness change.

---

## Phase 6: Polish, Reference Data, and Cross-Artifact Verification

**Purpose**: Seed generic reference registry content, verify attribution/no-score invariants end to end, and keep the shipped gates green.

- [ ] T032 [P] Populate `packs/registry/index.yaml` with a few generic, reviewed reference records sourcing packs in `packs/registry/reference/` across categories (FR-001; generic only). Ensure recorded hashes match the reference content.
- [ ] T033 [P] Add an end-to-end invariant test asserting no catalog output field is a number/percentage/rank (verification_state stays categorical) in `tests/unit/test_pack_catalog_no_score.py` (FR-015, SC-008).
- [ ] T034 [P] Add an attribution invariant test: `author` is present and unaltered through search/inspect/add and never conflated with the manifest `owner` in `tests/unit/test_pack_catalog_attribution.py` (FR-017, SC-007).
- [ ] T035 Author `specs/128-pack-catalog/quickstart.md` acceptance walkthrough (clean search -> inspect -> add + tamper refusal + incompatible refusal) and confirm it matches the shipped behavior.
- [ ] T036 Run and record green `retail check`, `retail semantic-check`, `retail kit-lint`, `ruff format --check`, `ruff check`, and `pytest -m unit`; confirm the shipped `pack scaffold`/`validate` behavior is unchanged (RR-006).

---

## Dependencies & Parallel Guidance

- Phase 1 (contract + registry scaffold) precedes everything.
- Phase 2 (registry core) precedes US1/US2 (both read the parsed index).
- US1 (search) and US2 (inspect) are independent of each other once Phase 2 lands; either may ship first (US1 is MVP).
- US3 (add) depends on the registry core (Phase 2) and reuses the shipped pack validation; it is the highest-risk slice and ships last.
- `[P]` tasks within a phase touch distinct files and may run in parallel. Handler tasks in `commands/pack.py` and parser tasks in `parser_ecosystem.py` for different subcommands touch the SAME file and are therefore NOT `[P]` against each other.
- No task modifies `schemas/seshat-extension-pack.schema.json`, `src/seshat/packs/model.py`, `loader.py`, `validator.py`, or `scaffold.py` (anti-reinvent: content model/schema/validation are reused unchanged).
