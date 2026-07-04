---

description: "Task list for feature 091-semi-additive-snapshot-grain"
---

# Tasks: Semi-Additive (Snapshot) Grain in the Metric Contract

**Input**: Design documents from `specs/091-semi-additive-snapshot-grain/`
(spec.md, plan.md, research.md, data-model.md, quickstart.md)

**Tests**: The spec's Independent Tests / Acceptance Scenarios / Edge Cases
are explicit and the plan's Testing section names concrete test files
(`tests/unit/test_snapshot_time_additivity.py`,
`tests/unit/test_rules_wiring.py`). Test tasks are INCLUDED.

**Closed file set** (plan.md "Project Structure" -- no file outside this list
is required or permitted for this feature):

1. `templates/metric-contract.yaml` (EDIT)
2. `src/retail/rules/snapshot_time_additivity.py` (NEW)
3. `src/retail/rules/__init__.py` (EDIT)
4. `tests/unit/test_rules_wiring.py` (EDIT)
5. `docs/rules/rules-manifest.json` (REGENERATE via `retail manifest`, never
   hand-edit)
6. `docs/rules/severity-posture.json` (REGENERATE + golden fixture)
7. `tests/unit/test_snapshot_time_additivity.py` (NEW)

Docs-first ordering (hard rule #8): the template field (Phase 2, doc/schema
layer) is authored before the rule module, and the rule module before the
wiring/manifest tasks (Phase 6).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an
  unfinished task in this list)
- **[Story]**: US1 | US2 | US3 | (blank for Setup/Foundational/Polish)
- FR-xxx / SC-xxx citations are the analyze-stage coverage trace -- every
  functional requirement in spec.md maps to at least one task below.

---

## Phase 1: Setup

**Purpose**: Confirm the ground this feature builds on, with no code change
yet.

- [ ] T001 Confirm `PyYAML` is already an installed repo dependency (no new
      dependency is introduced by this feature -- plan.md "Primary
      Dependencies"). Check `pyproject.toml` / `requirements*.txt` for an
      existing `pyyaml` entry; if absent, STOP and escalate (this feature's
      plan assumes it is already present via AL1/AL2).
- [ ] T002 [P] Run `pytest tests/unit/test_rules_wiring.py -m unit` and
      record the current green baseline (rule count BEFORE this feature) so
      the Phase 6 wiring change can be diffed against a known-good state.
- [ ] T003 [P] Read `src/retail/rules/assumptions.py` (AL1) end-to-end as the
      clone source named in plan.md and research.md: lazy `import yaml`
      inside the registered function, the `mappings/[^/]+/metrics/[^/]+\.ya?ml`
      glob regex, the `_TEMPLATE_PATH` + `is_test_path(...)` exemption, the
      fail-loud `except (OSError, UnicodeDecodeError, yaml.YAMLError)`
      pattern, and the `@register("<ID>", "<title>")` decorator shape. No
      file changes in this task -- orientation only.

**Checkpoint**: Ground confirmed; no source or doc file has been modified
yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The schema field (docs-first) and the rule module's shared
skeleton that BOTH User Story 1 and User Story 2 branches extend. Nothing in
Phase 3+ can be written until this phase is done, because US1 and US2 add
`if`-branches to the same function in the same new file.

**CRITICAL**: No user-story task may begin until this phase is complete.

- [ ] T004 [P] Add the new, OPTIONAL top-level scalar field
      `time_additivity` to `templates/metric-contract.yaml`, positioned
      alongside the existing `grain` and `readiness` fields, with a comment
      block matching the file's existing documentation style: states the
      closed vocabulary (`fully | semi | non`), that it classifies additivity
      specifically over the DATE axis, and cites
      `skills/retail-kpi-knowledge/knowledge/kpi-additivity-and-grain.md`.
      The comment MUST NOT restate or redefine what "semi-additive" means in
      business terms (cite only) and MUST NOT inline any C086 /
      retail_store_sales / pharmacy-specific value. Touches ONLY this one new
      key -- no rename/restructure of any existing top-level key (collision
      avoidance vs. parallel adders 092/103).
      **Satisfies**: FR-001, FR-002, FR-002a, FR-003, FR-015, FR-016.
- [ ] T005 [P] Create `src/retail/rules/snapshot_time_additivity.py`
      with the HR5 module skeleton, cloned from `assumptions.py`'s scaffold:
      module docstring stating HR5's purpose and its boundary against AD1
      (does not read `skills/retail-kpi-knowledge/contracts/*.md` or AD1's
      composition-legality table -- FR-008); the same
      `_METRICS_RE = re.compile(r"^mappings/[^/]+/metrics/[^/]+\.ya?ml$")` and
      `_TEMPLATE_PATH` constants (or import/reuse the shared pattern);
      an `_iter_contracts(ctx)` helper applying the metrics-glob + template +
      `is_test_path(...)` exemption; the `@register("HR5", "<title>")`
      decorator on a `check_snapshot_time_additivity(ctx: RuleContext) ->
      Iterable[Finding]` function with a LAZY `import yaml` inside the
      function body (module stays stdlib-only at import scope); a
      `try/except (OSError, UnicodeDecodeError, yaml.YAMLError)` block per
      contract that appends a fail-loud `Finding(rule_id="HR5",
      severity=Severity.ERROR, message="could not read/parse metric
      contract: <exc>", locator=rel)` on an unreadable file (decision-table
      row 1) and otherwise `continue`s past a non-dict parse result. No
      A10/vocabulary branching logic yet -- that is US1/US2.
      **Satisfies**: FR-004 (glob + exemption scaffold), FR-008, FR-010,
      FR-014, FR-017.

**Checkpoint**: The schema field exists and is documented; the rule module
exists, registers under id `HR5`, scans the right corpus, and fails loud on
an unreadable file. No A10 or vocabulary logic exists yet -- `retail check`
would currently emit zero HR5 findings on every readable contract.

---

## Phase 3: User Story 1 - A snapshot-flagged contract must declare its date-axis additivity (Priority: P1) 🎯 MVP

**Goal**: HR5 detects an A10-flagged contract and ERRORs when its
`time_additivity` is absent or illegally `fully`; clears when `semi`/`non`.

**Independent Test** (spec.md): Author a fixture contract carrying
`ambiguities: [{id: A10, ...}]` and no `time_additivity`; run the rule and
confirm exactly one HR5 ERROR. Add `time_additivity: semi` and confirm the
finding clears. Set `time_additivity: fully` on the same fixture and confirm
HR5 still ERRORs.

### Tests for User Story 1

- [ ] T006 [US1] Add fixture-based unit tests to
      `tests/unit/test_snapshot_time_additivity.py` (new file -- first tasks
      to populate it) covering decision-table rows 5/6/7/8 from
      data-model.md: (a) A10 entry present + `time_additivity` absent ->
      exactly one HR5 ERROR whose message states a missing date-axis
      declaration (FR-004); (b) same fixture + `time_additivity: fully` ->
      still exactly one HR5 ERROR, with a message text DISTINCT from (a)
      (FR-005); (c) same fixture + `time_additivity: semi` -> zero findings;
      (d) same fixture + `time_additivity: non` -> zero findings. Mirror
      `tests/unit/test_assumptions.py`'s `_ctx(tmp_path, files)` fixture
      helper and `RuleContext(repo_root=..., tracked_files=...)` shape.
      Confirm these tests FAIL before Phase 3 implementation (only the
      fail-loud/skeleton branch from Phase 2 exists).
      **Satisfies**: FR-004, FR-005 (test evidence); SC-002, SC-003.

### Implementation for User Story 1

- [ ] T007 [US1] In `src/retail/rules/snapshot_time_additivity.py`, add an
      `_has_a10_entry(contract: dict) -> bool` helper: iterate
      `contract.get("ambiguities") or []` (a list of mappings) and return
      `True` iff any entry has `entry.get("id") == "A10"` using EXACT,
      case-sensitive string equality (no case-fold, no substring/prefix
      match) -- a near-miss token such as `a10` or `A10-inventory` does NOT
      count. Read ONLY the `id` field; do not gate on `decision_status`
      (an A10 entry with `decision_status: decided` still counts).
      Depends on T005 (module skeleton).
      **Satisfies**: FR-004a; Edge Case "ambiguities[] id-match casing";
      Edge Case "A10 entry is decision_status: decided".
- [ ] T008 [US1] In the same module, extend
      `check_snapshot_time_additivity` (depends on T007): when
      `_has_a10_entry(contract)` is `True` and `time_additivity` is ABSENT
      (see T009's normalization for the null/empty collapse), append a
      `Finding(rule_id="HR5", severity=Severity.ERROR, message="missing
      time_additivity declaration on an A10-flagged (snapshot) contract",
      locator=rel)`. When `_has_a10_entry(contract)` is `True` and the
      normalized value equals `"fully"`, append a SEPARATE, textually
      distinct `Finding(..., message="an A10-flagged contract cannot
      declare time_additivity: fully", locator=rel)`. When the normalized
      value is `"semi"` or `"non"`, emit no finding for that contract.
      **Satisfies**: FR-004, FR-005, FR-009 (ERROR-only, no score), FR-011
      (off-spine: no readiness stage/approval touched).

**Checkpoint**: User Story 1 is independently functional -- an A10-flagged
contract with a missing or `fully` declaration ERRORs; `semi`/`non` clears.
US2's vocabulary/no-trigger branches are not yet implemented.

---

## Phase 4: User Story 2 - Absent or out-of-vocabulary values are refused, never inferred (Priority: P1)

**Goal**: HR5 ERRORs on any contract (A10-flagged or not) whose
`time_additivity` value is outside the closed three-word vocabulary, treats
null/empty as absent (not out-of-vocabulary), handles a non-scalar value
without crashing, and stays silent on a contract with no A10 entry and no
field (or a volunteered valid field).

**Independent Test** (spec.md): Author an A10-flagged fixture with
`time_additivity: "sometimes"`; confirm HR5 ERRORs distinctly from the
missing-field message. Author a second fixture with no A10 entry and no
`time_additivity` field; confirm zero findings.

### Tests for User Story 2

- [ ] T009 [US2] Add fixture-based unit tests to
      `tests/unit/test_snapshot_time_additivity.py` covering decision-table
      rows 2/3/4/9 and the Q3/Q3b/Q2 edge cases from data-model.md /
      Clarifications: (a) no A10 entry + no `time_additivity` field -> zero
      findings (FR-007); (b) no A10 entry + a valid `time_additivity` value
      present anyway -> zero findings, validated-only (Edge Case /
      Acceptance Scenario 3 of US2); (c) no A10 entry + an out-of-vocabulary
      value (e.g. `"sometimes"`) -> exactly one HR5 ERROR regardless of A10
      absence (FR-006); (d) A10-flagged + a case/whitespace variant
      (`"Fully"`, `"SEMI"`, `"non "`) -> out-of-vocabulary ERROR, never
      silently normalized (FR-002a); (e) A10-flagged + `time_additivity:`
      with YAML null, and a second case with `time_additivity: ""` -> both
      produce the FR-004 missing-field message, NOT the out-of-vocabulary
      message (FR-004b); (f) A10-flagged + a non-scalar `time_additivity`
      (a YAML list, e.g. `["a", "b"]`) -> out-of-vocabulary ERROR with no
      unhandled exception raised (FR-006a); (g) confirm the out-of-vocabulary
      message text from (c)/(d)/(f) is DISTINCT from the missing-field
      message text from Phase 3's T006 (SC-004). Confirm these tests FAIL
      before Phase 4 implementation. Depends on T006 existing (same file).
      **Satisfies**: FR-002a, FR-004b, FR-006, FR-006a, FR-007 (test
      evidence); SC-004.

### Implementation for User Story 2

- [ ] T010 [US2] In `src/retail/rules/snapshot_time_additivity.py`, add a
      `_normalize_time_additivity(contract: dict) -> str` (or equivalent)
      helper returning one of `"ABSENT"`, `"FULLY"`, `"SEMI"`, `"NON"`, or
      `"OUT_OF_VOCAB"` per data-model.md's normalization table: key entirely
      absent -> `ABSENT`; YAML null or empty string -> `ABSENT` (FR-004b);
      exact case-sensitive match to `"fully"`/`"semi"`/`"non"` (untrimmed,
      FR-002a) -> `FULLY`/`SEMI`/`NON` respectively; any other string
      (including case/whitespace variants) -> `OUT_OF_VOCAB` (FR-002a,
      FR-006); a non-scalar YAML node (list or mapping) -> `OUT_OF_VOCAB`
      without raising (use an `isinstance(value, str)` guard before any
      string method -- FR-006a). Depends on T007/T008 (same module,
      sequential -- not parallelizable with US1's implementation task).
- [ ] T011 [US2] Wire `_normalize_time_additivity` into
      `check_snapshot_time_additivity` (depends on T010), replacing the
      ad-hoc missing/fully checks from T008 with the full decision table:
      `OUT_OF_VOCAB` -> ERROR with the message "unrecognized time_additivity
      value" (fires regardless of `_has_a10_entry`, per FR-006); `ABSENT` +
      no A10 -> no finding (FR-007); `FULLY`/`SEMI`/`NON` + no A10 -> no
      finding (validated-only). Confirm the three message classes stay
      textually distinct (unreadable-file / missing-declaration /
      illegal-fully / unrecognized-value) per SC-004 and the plan's decision
      table.
      **Satisfies**: FR-002a, FR-004b, FR-006, FR-006a, FR-007, FR-009,
      FR-010, FR-013 (empty/no-A10 corpus emits zero findings), FR-015.
      **Also documents FR-018's decided half**: the trigger checked here is
      the existing A10 id ONLY -- no other ambiguities-ledger id or
      measure-name heuristic is read (the OPEN half of FR-018/Clarifications
      Q4 is NOT implemented and is out of scope for this task).

**Checkpoint**: User Stories 1 AND 2 both work independently and together --
the full decision table (rows 1-9) is implemented and covered by tests.

---

## Phase 5: User Story 3 - The rule is wired in and counted like every other rule (Priority: P2)

**Goal**: HR5 is discoverable via `retail.rules` import, appears in the
expected-rule-id set, and both authoritative manifests (rule count,
severity-posture) reflect it -- the wiring meta-gate and rule-count
reconciler agree the count advanced by exactly one.

**Independent Test** (spec.md): Run the rule-wiring unit test and confirm
the actual registered rule ids equal the expected set (now including `HR5`)
and the manifest count matches.

### Implementation for User Story 3

- [ ] T012 [US3] Edit `src/retail/rules/__init__.py`: add
      `snapshot_time_additivity` to the side-effecting import tuple (alpha
      order -- between `scorecard` and `sql`... actually alphabetically
      after `sql`/`status_claims` per `s < s` comparison: place it in
      correct alpha order among the existing entries) and to `__all__` in
      the same alphabetical position in both lists. Depends on T005 (module
      must exist to be imported).
      **Satisfies**: FR-012 (wiring points 1 and 2 of 5: registry module
      import block + `__all__` export list).
- [ ] T013 [US3] Edit `tests/unit/test_rules_wiring.py`: add the literal
      string `"HR5"` to the `EXPECTED_RULE_IDS` frozenset (with a short
      inline comment matching the style of neighboring entries, e.g.
      `"HR5",  # snapshot time-additivity: A10-flagged contract must
      declare non-fully time_additivity`). Do NOT hardcode a count anywhere
      -- the existing `len(EXPECTED_RULE_IDS)` assertions derive it.
      Depends on T012 (module must be registered for the test to pass).
      **Satisfies**: FR-012 (wiring point 3 of 5: expected-rule-id set).
- [ ] T014 [US3] Run `pytest tests/unit/test_rules_wiring.py -m unit` and
      confirm `test_registered_rule_ids_match_expected_set` and
      `test_all_rules_returns_a_tuple` both pass with `HR5` present and no
      `rule-id drift` mismatch reported. Depends on T012, T013.
- [ ] T015 [US3] Regenerate `docs/rules/rules-manifest.json` via the
      repo's `retail manifest` command (never hand-edit): confirm it adds an
      alpha-sorted `{"id": "HR5", "title": "<the @register title from
      T005>"}` entry and the authoritative count advances by exactly one
      over the T002 baseline. Depends on T012 (rule must be registered to be
      picked up by the generator).
      **Satisfies**: FR-012 (wiring point 4 of 5: authoritative rules
      manifest).
- [ ] T016 [US3] Regenerate `docs/rules/severity-posture.json` (and its
      golden fixture, per the repo's existing regeneration command) so it
      adds a `"HR5": [...]` entry under `"registered"`; on the current
      committed corpus (zero A10 entries anywhere, per research.md Section
      1.6 / SC-001) the expected finding list for HR5 is empty (matching
      AD1's shape on the same corpus). Depends on T011 (full rule logic must
      exist for the golden run to reflect real behavior), T015.
      **Satisfies**: FR-012 (wiring point 5 of 5: severity-posture manifest
      + golden fixture), completing all five points (1-2: T012; 3: T013;
      4: T015; 5: T016).

**Checkpoint**: All three user stories are independently functional; the
rule is fully wired per the five-point checklist; `test_rules_wiring.py`
passes with the count advanced by exactly one.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Whole-feature verification that spans more than one user story;
confirms the constitution/scope guarantees that don't belong to a single FR
branch.

- [ ] T017 [P] Run `retail check` over the actual committed corpus and
      confirm zero HR5 findings (SC-001) -- the current corpus carries no
      A10 entry anywhere, so this is a genuine clean baseline, not a
      suppressed one. Depends on Phase 5 complete.
- [ ] T018 [P] Inspect `src/retail/rules/snapshot_time_additivity.py` and
      confirm: (a) no module-scope `import yaml` (lazy-only, matching AL1 --
      SC-006); (b) every emitted `Finding` uses `Severity.ERROR` only, no
      `Severity.WARNING`, no numeric/graded field anywhere in a message
      (hard rule #9, FR-009); (c) no DAX execution, no DB/network call, no
      PBIP/visual read anywhere in the module (FR-010); (d) the module does
      not import or read `skills/retail-kpi-knowledge/contracts/*.md` or
      reference AD1's composition-legality table (FR-008); (e) no readiness
      stage or approval field is written anywhere (FR-011).
- [ ] T019 [P] Grep `templates/metric-contract.yaml`'s new comment block and
      `src/retail/rules/snapshot_time_additivity.py` (source + docstrings)
      for any C086 / retail_store_sales / pharmacy-specific token (table
      name, column name, billing/insurance term); confirm zero hits (FR-016,
      SC-007).
- [ ] T020 [P] Confirm every new/edited file from the closed file set (T004,
      T005, T012, T013, and the regenerated T015/T016 outputs) is ASCII,
      UTF-8 without BOM, using only `--`/`->` for dashes/arrows (no
      non-ASCII glyphs), per Principle IX / FR-017.
- [ ] T021 Confirm `specs/091-semi-additive-snapshot-grain/spec.md`'s FR-018
      `[NEEDS CLARIFICATION -- resolved to OPEN owner ruling]` marker is
      UNCHANGED and still present -- this build implements only FR-018's
      decided half (A10-only trigger, covered by T011); the OPEN half
      (whether the trigger should ever widen beyond A10) is explicitly NOT
      answered, NOT pre-built for, and NOT removed from the spec by any task
      in this list.
- [ ] T022 Walk `specs/091-semi-additive-snapshot-grain/quickstart.md`
      end-to-end against the finished implementation (author a throwaway
      fixture per its Section 3, run `retail check`, confirm each of the
      7 numbered scenarios matches actual output) and fix any drift between
      the quickstart's described behavior and the shipped rule.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies -- can start immediately.
- **Foundational (Phase 2)**: Depends on Setup (T001-T003) completion --
  BLOCKS all user stories. T004 (template) and T005 (module skeleton) touch
  different files and MAY run in parallel with each other, but both must
  finish before any Phase 3+ task starts.
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion (needs the
  module skeleton from T005 to extend).
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion. T009/T010/T011
  edit the SAME module file and test file that US1's T006-T008 already
  edited -- run Phase 4 AFTER Phase 3, sequentially, not in parallel, even
  though both are P1 priority.
- **User Story 3 (Phase 5)**: Depends on Phase 2 (module must exist) and, in
  practice, on Phase 3 + Phase 4 being complete (T016's golden-fixture
  regeneration needs the FULL decision-table logic in place to reflect real
  behavior, and T014's wiring test should validate the finished rule, not a
  half-built one).
- **Polish (Phase 6)**: Depends on Phases 3, 4, and 5 all complete.

### Within-Phase Notes

- T004 and T005 are the only legitimate `[P]` pair before a user-story
  phase: different files, no shared state.
- T006 (US1 tests) MUST be written and confirmed FAILING before T007/T008
  (US1 implementation).
- T009 (US2 tests) MUST be written and confirmed FAILING before T010/T011
  (US2 implementation), and MUST be added to the same
  `tests/unit/test_snapshot_time_additivity.py` file T006 created --
  sequential with T006, not parallel.
- T007->T008->T010->T011 is a single sequential chain (same function, same
  file) even though T007/T008 belong to US1 and T010/T011 belong to US2.
- T012->T013->T014->T015->T016 is a single sequential wiring chain (each
  step depends on the previous being in place for its own verification to
  mean anything).
- T017-T020 in Phase 6 are mutually independent read-only checks over the
  finished artifacts and MAY run in parallel with each other; T021 and T022
  are likewise independent of T017-T020 but read the finished spec/
  quickstart rather than source, so they are listed without `[P]` only
  because they are better run last as a final sanity pass, not because of a
  file conflict.

### Parallel Example: Foundational Phase

```bash
# T004 and T005 touch different files and can run together:
Task: "Add time_additivity field to templates/metric-contract.yaml"
Task: "Create src/retail/rules/snapshot_time_additivity.py skeleton"
```

### Parallel Example: Polish Phase

```bash
# T017-T020 are independent read-only verification passes:
Task: "Run retail check over committed corpus, confirm zero HR5 findings"
Task: "Inspect module for lazy-import / ERROR-only / never-execute invariants"
Task: "Grep for C086/pharmacy-specific tokens in new artifacts"
Task: "Confirm ASCII/UTF-8-no-BOM on every new/edited file"
```

---

## FR / SC Coverage Trace (for the analyze stage)

| Requirement | Task(s) |
|---|---|
| FR-001 | T004 |
| FR-002 | T004 |
| FR-002a | T004, T006... (T009 negative), T010, T011 |
| FR-003 | T004 |
| FR-004 | T005 (scaffold), T006 (test), T008, T011 |
| FR-004a | T007 |
| FR-004b | T009 (test), T010, T011 |
| FR-005 | T006 (test), T008 |
| FR-006 | T009 (test), T010, T011 |
| FR-006a | T009 (test), T010 |
| FR-007 | T009 (test), T011 |
| FR-008 | T005, T018 |
| FR-009 | T008, T011, T018 |
| FR-010 | T005, T018 |
| FR-011 | T008, T018 |
| FR-012 | T012, T013, T014, T015, T016 |
| FR-013 | T011 |
| FR-014 | T005 |
| FR-015 | T004, T011 |
| FR-016 | T004, T005, T019 |
| FR-017 | T004, T005, T012, T013, T020 |
| FR-018 (decided half only; OPEN half explicitly not implemented) | T011 (decided half), T021 (OPEN half stays open) |
| SC-001 | T017 |
| SC-002 | T006 |
| SC-003 | T006 |
| SC-004 | T009 |
| SC-005 | T014, T015 |
| SC-006 | T018 |
| SC-007 | T019 |

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational (template field + module skeleton).
3. Complete Phase 3: User Story 1 (A10 + missing/fully/semi/non).
4. **STOP and VALIDATE**: run the new tests independently; `retail check`
   on a hand-authored fixture shows the expected ERROR/clear behavior.

### Incremental Delivery

1. Setup + Foundational -> schema field exists, module registers and reads
   the right corpus, fails loud on unreadable files.
2. Add User Story 1 -> A10-trigger branch complete and tested.
3. Add User Story 2 -> vocabulary/no-trigger branch complete and tested;
   full decision table now implemented.
4. Add User Story 3 -> wiring complete; manifests regenerated; rule count
   reconciled.
5. Polish -> whole-corpus clean-baseline check, invariant audit, genericness
   audit, ASCII/BOM audit, spec/quickstart drift check.
