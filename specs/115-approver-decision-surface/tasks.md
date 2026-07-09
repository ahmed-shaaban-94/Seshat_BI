---
description: "Task list for Approver Decision Surface implementation"
---

# Tasks: Approver Decision Surface

**Input**: Design documents from `specs/115-approver-decision-surface/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: INCLUDED. The refusal-case COMPLETENESS verifier is the feature's
mechanical guarantee (it sits ON the real risk -- a refusal item misfiled as
reassurance -- per research D3). Repo mandates TDD, so tests precede code.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable (different files, no incomplete-task dependency)
- **[Story]**: US1 / US2 / US3 (maps to spec.md user stories)
- Paths repo-relative; single-project layout (`src/retail`, `tests/unit`).

---

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 [P] Add fixtures under `tests/unit/fixtures/approver_view/`: `full_refusal/` (readiness-status.yaml with a `blocked` stage + a `warning` stage + an approval-required stage lacking a valid `approvals[]` entry, plus unresolved-questions.md with an OPEN governance row), `all_pass/` (all stages pass, valid approvals, all questions answered -- the retail_store_sales shape), `questions_only/` (open analyst + open governance rows), `awkward_questions/` (an OPEN row with an embedded `|`, alignment padding, and a near-miss status string -- the PARSER-UNDER-TEST fixture, with its expected open-row set hand-declared in the test), `missing_status/` (no readiness-status.yaml), `missing_questions/` (status present, no unresolved-questions.md), and a `second_table/` distinct conformant table. ASCII, UTF-8 no BOM.
- [x] T002 Create the composer skeleton `src/retail/approver_view.py` with `build_approver_view(repo_root, table) -> dict` and `render_view(view) -> str` (raise NotImplementedError), reusing the `_load_yaml_mapping` idiom and a small committed-markdown-table parser for the Open-questions table. No DB/driver import at module load; NO file-write call.

**Checkpoint**: fixtures exist, module imports.

---

## Phase 2: Foundational (Blocking Prerequisites)

CRITICAL: the shared classifier extraction + the completeness verifier gate every story.

- [x] T003 Extract the shared classifier: create `src/retail/readiness_classify.py` holding `_CATEGORY_RULES`, `_DEFAULT_CATEGORY`, and a public `classify(reason)`, MOVED verbatim from `blocker_explainer.py`; update `blocker_explainer.py` to import them. Behavior-preserving (research D2).
- [x] T004 [P] Regression-lock (V9): confirm/extend `tests/unit/test_blocker_explainer.py` asserts `build_blocker_explanations` output is BYTE-IDENTICAL after T003. Must be green before proceeding.
- [x] T005 [US-shared] Write the completeness verifier `assert_refusal_case_complete(view, status_yaml, questions_rows)` in `tests/unit/test_approver_view.py` implementing V1 completeness, V2 correct-side, V3 fixed-rank order, V4 verbatim+cite, V5 no-score (contracts/verifier.md). CRITICAL: the question-side `questions_rows` oracle MUST be the HAND-AUTHORED expected open-row set from the fixture-test, NEVER the production markdown parser's own output (else V1 is circular -- a parser bug drops the row from both sides and passes vacuously; spec 114's join-defect class). Include the `awkward_questions` parser-under-test fixture so a parse regression FAILS V1. TEST-only -- NO `@register` rule, NO manifest change (FR-007).
- [x] T006 Implement the classification + partition core in `src/retail/approver_view.py`: read both inputs; build RefutationItem/ReassuranceItem per data-model.md D4 (blocked/warning/unmet-approval + OPEN questions -> refusal; pass/valid-approval/answered -> reassurance); question category by the committed `Who must answer` column (governance/data-owner -> approval; analyst -> classify() grain/readiness; unknown -> readiness); assign `rank` = fixed enum index (a lookup). Return the ApproverView dict incl. `missing_inputs`, `read_only_proof: True`. `render_view` still stubbed.

**Checkpoint**: `build_approver_view` returns a correct, correctly-partitioned model for all fixtures; verifier importable.

---

## Phase 3: User Story 1 - Signer reads the refusal case first (Priority: P1) -- MVP

**Goal**: refutation-first ORDERED view -- refusal-bearing items (by fixed enum rank) before reassurance.

**Independent Test**: run against `full_refusal` -> approval-category items top, blocked/warning below, reassurance last; no synthesized priority number.

### Tests for User Story 1 (write first, must FAIL)

- [x] T007 [P] [US1] In `tests/unit/test_approver_view.py`, add `test_refusal_first_order` and `test_all_pass_nothing_to_refuse`: compose for `full_refusal` and `all_pass`, run `assert_refusal_case_complete`; assert rank order (V3) and that `all_pass` yields an empty refusal case + explicit "nothing to refuse" + reassurance list, no score. Assert FAIL before T008.

### Implementation for User Story 1

- [x] T008 [US1] Implement `render_view` for the ordered refusal case + reassurance + the "nothing to refuse" empty case, per contracts/view.md. ASCII `--`/`->`, no glyphs, no numeric token.
- [x] T009 [US1] Add the CLI verb `src/retail/cli/commands/approver_view.py` (`retail approver-view --table <t> [--format text|json]`) mirroring `commands/blockers.py`; no `--write` (D5); always exit 0 (FR-007).
- [x] T010 [US1] Register + dispatch the `approver-view` subcommand in `src/retail/cli/parser.py` and the CLI dispatch table (`src/retail/cli/__init__.py`).

**Checkpoint**: MVP -- `retail approver-view --table retail_store_sales` shows the reassurance-only view (all_pass); `full_refusal` fixture orders correctly; US1 tests green.

---

## Phase 4: User Story 2 - Open governance/PII questions in the refusal case (Priority: P1)

**Goal**: OPEN unresolved-questions.md rows appear in the refusal case, owner-mapped; answered rows never appear as open refusal items.

**Independent Test**: run against `questions_only` -> open governance row ranked above open analyst row; against `all_pass` -> no answered row in the refusal case.

### Tests for User Story 2 (write first, must FAIL)

- [x] T011 [P] [US2] In `tests/unit/test_approver_view.py`, add `test_open_questions_owner_mapped` (governance/data-owner -> approval bucket, ranked above analyst) and `test_answered_questions_not_refusal` (answered rows never open refusal items; V2). Assert FAIL before T012.

### Implementation for User Story 2

- [x] T012 [US2] Ensure the Open-questions parser + owner-mapping (from T006) render correctly in `render_view`: each open question line carries its `Who must answer` owner + verbatim question text + source cite; answered questions appear only under reassurance.

**Checkpoint**: open questions surface owner-mapped; answered ones stay reassurance; US1 + US2 green.

---

## Phase 5: User Story 3 - Missing/unreadable input surfaced, not fabricated (Priority: P2)

**Goal**: a missing input is named in `missing_inputs[]`; a missing questions file is never presented as "no open questions".

**Independent Test**: run against `missing_status` and `missing_questions` fixtures.

### Tests for User Story 3 (write first, must FAIL)

- [x] T013 [P] [US3] In `tests/unit/test_approver_view.py`, add `test_missing_status_named` and `test_missing_questions_not_no_questions` (V7). Assert FAIL before T014.

### Implementation for User Story 3

- [x] T014 [US3] Extend `build_approver_view`/`render_view` for input absence: populate `missing_inputs[]` and render the "Inputs not available" section distinguishing "questions file missing" from "no open questions". No fabricated items.

**Checkpoint**: input-absence honest; all three stories functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T015 [P] Add the tool doc `docs/tools/approver-decision-surface.md` mirroring `docs/tools/blocker-explainer.md` (what it is, run, the scope wall, F027 boundary, what it will NOT do).
- [x] T016 [P] [US-shared] Add the no-write proof test (V6, SC-003): grep the module for zero write calls; a default run changes no tracked file; `build_approver_view` triggers no DB/network import.
- [x] T017 [P] [US-shared] Add the generic proof test (V8, SC-006): run the SAME composer over `retail_store_sales` (via the all_pass fixture shape) and `second_table` with no per-table branch.
- [x] T018 Run `quickstart.md` end-to-end; confirm the retail_store_sales reassurance-only view and zero score. Run `ruff format --check src tests` + `ruff check src tests` + `pytest tests/unit/test_approver_view.py tests/unit/test_blocker_explainer.py -q`; confirm `retail check` still exits 0 and the rules-manifest count is UNCHANGED (no gate added, FR-007), and blocker_explainer output unchanged (V9).

---

## Dependencies & Execution Order

### Phase dependencies

- Setup (1) -> Foundational (2) -> User Stories (3-5) -> Polish (6).
- Phase 2 BLOCKS all stories: T003 extraction (+ T004 regression lock) and the
  T006 partition core + T005 verifier are shared.

### Story dependencies

- US1 (P1): after Phase 2. The MVP.
- US2 (P1): after Phase 2; T012 shares `render_view` with T008 -> sequence
  T008 -> T012 (same-file).
- US3 (P2): after Phase 2; T014 shares `render_view`/`build_*` -> sequence after
  T008/T012.

### Within each story

- Test first (must FAIL) -> implementation -> checkpoint.
- T003 extraction + T004 lock BEFORE T006 (the core imports the extracted
  classifier). T006 before any `render_view` task.

### Parallel opportunities

- T001 fixtures [P] with T005 verifier authoring.
- T004 regression-lock [P] once T003 lands.
- Per-story TEST tasks (T007, T011, T013) [P] with each other; each precedes its
  own implementation.
- Polish T015/T016/T017 [P]; T018 is the final serial gate.
- NOTE: T008, T012, T014 all edit `render_view` in one file -> NOT parallel; run
  in story order.

---

## Implementation Strategy

### MVP first (US1 only)

1. Phase 1 -> Phase 2 (incl. the T003 extraction + T004 lock) -> Phase 3 US1.
2. STOP and validate: `retail approver-view --table retail_store_sales` shows the
   correctly-ordered/empty-refusal view; US1 + regression-lock green.

### Incremental delivery

- +US2 (open-question ingestion) -> +US3 (input-absence honesty) -> Polish (doc,
  no-write + generic proofs, full gate run + manifest-unchanged confirmation).

---

## Notes

- [P] = different files, no incomplete-task dependency.
- The verifier (T005) is TEST-only -- no `@register` rule, no manifest change
  (FR-007 forbids a gate).
- T003 is a behavior-preserving MOVE-refactor of shipped #229 code, regression-
  locked by T004 -- keeps the CodeScene new-code-health gate green.
- The completeness verifier (V1/V2) sits ON the real risk (a refusal item misfiled
  as reassurance), per research D3 -- not just ordering determinism.
- ASCII only, UTF-8 no BOM in every authored file (Principle IX).
