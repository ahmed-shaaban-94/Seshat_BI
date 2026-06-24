---
description: "Task list for Reconciliation Ledger (016) -- docs/templates-only, Later tier"
---

# Tasks: Reconciliation Ledger -- a durable history of cross-layer reconciliation results

**Input**: Design documents from `specs/016-reconciliation-ledger/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: No automated tests this slice -- it ships docs/templates only (no `src/` code). The
"tests" are the per-story Independent Tests (hand-filled example entries + inspection) plus the
deterministic ASCII/UTF-8-no-BOM check and `retail check` staying green. This matches the spec
(FR-011) and the tasks-template note that test tasks are OPTIONAL unless code is requested.

**Organization**: grouped by the three user stories so each is independently verifiable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency)
- **[Story]**: US1 / US2 / US3 (or SETUP / POLISH)
- All paths are repo-relative from the repo root.

## Path Conventions

Single project (the kit). This slice touches `templates/` and `docs/` only. **No** `src/`,
**no** `warehouse/migrations/`, **no** CLI -- those are deferred (spec Deferred decisions).

---

## Phase 1: Setup (Shared)

**Purpose**: confirm the naming/placement decisions the template depends on, before authoring.

- [ ] T001 [SETUP] Confirm the new template filename + location: `templates/reconciliation-ledger-entry.md` (recommended default, sibling of `templates/reconciliation-report.md`). Record the choice at the top of the template. (Resolves spec FR-001 filename; plan Structure Decision.)
- [ ] T002 [SETUP] Confirm the example-entry placement decision: two hand-filled examples (one `pass`, one `fail`) INLINE within the template as generic worked illustrations (plan default). Note the decision in the template header.
- [ ] T003 [SETUP] Record the deferred storage-placement note to carry into the template: a table's actual ledger is INTENDED to live per-table under `mappings/<table>/` (ADR 0003); concrete file/path/format is DEFERRED (spec FR-007). This is a one-line note, not a built store.

**Checkpoint**: naming + placement + example-format decisions fixed; authoring can begin.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the skeleton every story writes into -- the template file with its sections.

**CRITICAL**: T004 blocks all user-story tasks (they fill sections of this file).

- [ ] T004 [FOUND] Create `templates/reconciliation-ledger-entry.md` skeleton: title + the GENERIC-TEMPLATE banner (placeholders only, no worked-example specifics, #7), and the section headers: (a) What this ledger is / is not, (b) Provenance block, (c) Per-measure result table, (d) Row-count line, (e) Overall verdict, (f) Evidence references, (g) Append-only + correction invariant, (h) Worked examples, (i) See also. ASCII + UTF-8 no BOM. (Spec FR-001/FR-002.)

**Checkpoint**: empty-but-structured template exists; stories fill it.

---

## Phase 3: User Story 1 - Durable, append-only entry shape (Priority: P1) -- MVP

**Goal**: define the entry so one reconciliation result is captured immutably, append-only, with
every number a measured value.

**Independent Test**: hand-fill one `pass` entry from a reconciliation result; confirm it carries
measured deltas + verdict + evidence + provenance, and that a second entry appends without
touching the first.

- [ ] T005 [US1] Author the **Provenance block** fields in `templates/reconciliation-ledger-entry.md`: table id, run timestamp (precise, to distinguish same-day runs), actor (`agent|analyst`), DB cluster/database identifiers, and an evidence reference to the source `retail validate` run and/or the `reconciliation-report.md`. (Spec FR-002.)
- [ ] T006 [US1] Author the **Per-measure result table** in the template: columns measure name, source / silver / gold / BI totals, measured delta, per-line match verdict. BI column may be `n/a`. Every cell is a measured value/difference -- no score (#9, FR-003). (Spec FR-002/FR-003.)
- [ ] T007 [US1] Author the **Row-count line** and the **Overall verdict** (`pass` | `fail`) sections; state penny-exact = `pass`, any non-zero delta = `fail`, no `warning`/score middle value for the number (FR-006).
- [ ] T008 [US1] Author the **Append-only + correction invariant** section: recording a result ADDS an entry, never mutates/deletes a prior one; corrections are supersede-by-append (a new entry referencing the superseded one), never edit-in-place. (Spec FR-004; SC-004.)
- [ ] T009 [P] [US1] Add a hand-filled **`pass` example entry** (generic placeholders) demonstrating penny-exact reconciliation: all deltas `0`, verdict `pass`, evidence ref present, full provenance. (Spec SC-002; US1 acceptance 1.)

**Checkpoint**: the entry shape is complete and demonstrated by a `pass` example; append-only is stated.

---

## Phase 4: User Story 2 - A FAIL is recorded with its measured drift (Priority: P1)

**Goal**: ensure a non-reconciling result is first-class history -- the measured non-zero delta,
the layer pair, and an overall `fail`, with nothing rounded away.

**Independent Test**: hand-fill a `fail` entry where one measure differs by a known amount; confirm
the measure, the exact delta, the layer pair, and overall `fail` are recorded.

- [ ] T010 [US2] Extend the per-measure result table guidance in the template to require, for a non-matching line: the **measured non-zero delta** (penny precision, signed), the **layer pair** where the gap appears (e.g. silver->gold), and a `fail` line verdict. A NULL total on a layer is recorded as a reconciliation defect (`fail` line), not omitted. (Spec FR-005; US2 acceptance 1-2.)
- [ ] T011 [P] [US2] Add a hand-filled **`fail` example entry** (generic placeholders): one measure with a measured delta (e.g. `+0.03` silver->gold), overall verdict `fail`, the cent recorded not rounded. Coexists with the `pass` example unchanged (demonstrates append-only). (Spec SC-002/SC-004; US2 acceptance 1.)
- [ ] T012 [US2] In the template, state the **deferred-mode rule**: when `retail validate` did not run (no DSN / no `db` extra -- the Gold Ready blocked-deferred boundary), there is **NO entry**; the ledger never fabricates a pass or a 0-delta for a run that did not happen. (Spec FR-012; #9; gold-ready.md.)

**Checkpoint**: failures and drift are auditable; deferred-mode absence is honest.

---

## Phase 5: User Story 3 - Durable, historical Gold Ready evidence (Priority: P2)

**Goal**: make a ledger entry citable as Gold Ready evidence (durable history), without changing
the Gold Ready gate.

**Independent Test**: cite the `pass` example entry in a `readiness-status.yaml`
`gold_ready.evidence[]`; show prior entries remain visible as history.

- [ ] T013 [US3] In the template's **Evidence references** section, document that a `pass` entry is a valid member of `gold_ready.evidence[]` and a `fail` entry is a `gold_ready` blocking reason (reconciliation not penny-exact) -- explicitly **without** changing the Gold Ready gate criteria. (Spec FR-010; US3 acceptance 1.)
- [ ] T014 [US3] Add a short **readiness-status citation snippet** (generic YAML) to the template showing a `gold_ready.evidence[]` entry pointing at a ledger entry, aligned to `templates/readiness-status.yaml` vocabulary. (Spec SC-006.)
- [ ] T015 [US3] Edit `docs/readiness/gold-ready.md`: under "Required artifacts" / evidence, add the reconciliation ledger as a DURABLE-HISTORY evidence option for `gold_ready` (complement to the point-in-time `reconciliation-report.md`), with NO change to the stage's gate/pass criteria. Add a "See also" link to the new template. (Spec FR-010; SC-005.)

**Checkpoint**: the readiness payoff is wired at the doc level; gate criteria untouched.

---

## Phase 6: Polish & Cross-Cutting

**Purpose**: framing, cross-links, and the generic/scope/encoding guarantees.

- [ ] T016 [P] [POLISH] Author the template's **"What this ledger is / is not"** framing: a history layer over the existing `retail validate` reconciliation check; adds NO new validator and NO new gate; the temporal complement to `reconciliation-report.md`. (Spec FR-008/FR-009; SC-005.)
- [ ] T017 [P] [POLISH] Author the template's **"See also"** section with working cross-links: `src/retail/validate.py` + `specs/004-retail-validate/spec.md` (the check, RC16), `templates/reconciliation-report.md` (snapshot complement), `docs/readiness/gold-ready.md` + `docs/readiness/readiness-model.md`, `docs/roadmap/roadmap.md` (F015), constitution Principle VIII, ADR 0002 (RC16), ADR 0003 (placement). (Spec FR-009.)
- [ ] T018 [POLISH] Cite the C086 worked example as the eventual FILLED-INSTANCE source -- referenced, never copied; confirm the template carries zero worked-example/pharmacy specifics (all placeholders, #7). (Spec SC-001; FR-001.)
- [ ] T019 [POLISH] Verify no fabricated numbers: scan template + both examples; every numeric field is a measured value or measured difference; no confidence/score anywhere (#9). (Spec SC-003.)
- [ ] T020 [P] [POLISH] Run the deterministic checks: ASCII + UTF-8-without-BOM on `templates/reconciliation-ledger-entry.md` and the `gold-ready.md` edit; confirm short repo-relative paths (Windows MAX_PATH). (Spec SC-001; constitution IX.)
- [ ] T021 [POLISH] Run `retail check` and confirm it stays green (no new violations from the added/edited text) and that the changed-file set is docs/templates ONLY -- no `src/`, no migration, no CLI (SC-007). (Spec SC-007/SC-008.)

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (T001-T003)**: no dependency -- start immediately.
- **Foundational (T004)**: depends on Setup -- BLOCKS all user-story tasks (they fill this file).
- **User stories (Phase 3-5)**: all depend on T004.
  - US1 (P1) and US2 (P1) edit the same template file -- sequence the section-authoring tasks
    (T005-T008, T010, T012) to avoid same-file conflicts; the two **example** tasks (T009, T011)
    are content-additive and marked [P].
  - US3 (P2) depends on the entry shape (US1) existing before it can be cited.
- **Polish (Phase 6)**: depends on the stories being authored.

### Story dependencies

- **US1 (P1)**: the MVP -- the entry shape. No dependency on other stories.
- **US2 (P1)**: extends the same template (fail-line guidance + fail example + deferred-mode). Best
  authored right after US1; the fail example is independently addable.
- **US3 (P2)**: depends on US1 (needs an entry to cite); touches `gold-ready.md` + a YAML snippet.

### Within the shared template file

Because T004-T013, T016-T019 edit the **same file** (`reconciliation-ledger-entry.md`), they are
**not** parallel with each other except where marked [P] (the two example-entry additions, and the
final-section authoring that touches distinct sections). Sequence same-section edits.

### Parallel opportunities

- Setup tasks T001-T003 are quick and effectively parallel.
- T009 (pass example) and T011 (fail example) are [P] -- distinct content blocks.
- T015 (`gold-ready.md`) and T014 (YAML snippet in the template) touch different files -> [P]-able.
- Polish T016, T017, T020 touch distinct sections/files -> [P] where noted.

---

## Implementation Strategy

### MVP first (US1 only)

1. Setup (T001-T003) + Foundational (T004).
2. US1 (T005-T009) -> the durable, append-only entry shape with a `pass` example.
3. **STOP and VALIDATE**: hand-fill the `pass` example; confirm measured deltas + verdict +
   evidence + provenance, and append-only. This alone is a usable, demonstrable ledger design.

### Incremental delivery

1. MVP (US1) -> the entry exists and is demonstrated.
2. US2 -> failures + drift + deferred-mode honesty are first-class.
3. US3 -> wired as durable Gold Ready evidence (gate unchanged).
4. Polish -> framing, cross-links, generic/encoding/scope guarantees verified.

---

## Notes

- This is a **"Later"-tier, docs/templates-only** slice (hard rule #8): the deliverable is the
  template + examples + design framing + the `gold-ready.md` evidence note. **No runtime is built.**
- Deferred (named, not built, per spec): the storage runtime/store, `retail validate` -> ledger
  auto-append wiring, and a query/history surface.
- **OPEN for human (Principle V):** the ledger **grain** (one-entry-per-run vs per-measure;
  one-ledger-per-table vs shared) is NOT finalized here -- the template adopts one-entry-per-run-
  per-table as a working default and flags the grain as a human decision. Do not auto-resolve it.
- Verify: no fabricated numbers (#9), generic only (#7), ASCII/UTF-8-no-BOM, `retail check` green,
  changed files docs/templates only.
