# Tasks: Publish Approval Receipt (record-and-STOP token)

**Input**: Design documents from `specs/041-publish-approval-receipt-record-and/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: No automated test code is added (the spec requests none; this is a docs/templates
authoring slice). Verification is by `retail check` exit 0 (rule count UNCHANGED) + reading the
committed artifacts against Success Criteria SC-001..SC-009.

**Organization**: Tasks are grouped by user story. The single deliverable artifact (the generic
template) is authored once and then each user story's behavior is verified against it, so the
stories share one file by design -- the per-story tasks are the verification slices, not separate
files.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths are included.

## Path Conventions

Docs/templates authoring slice. No `src/` or `tests/`. The committed text lives in
`templates/handoff/` and `docs/readiness/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the home and the siblings before authoring.

- [ ] T001 Confirm `templates/handoff/` exists and holds the two siblings `bi-handoff-pack.md` and `handoff-review-checklist.md`; the new `publish-receipt.md` lands beside them (read-only check, no change).
- [ ] T002 Re-read the four ground-truth seams so the template cites them exactly: `docs/readiness/publish-ready.md` (record-and-STOP prose + owner), `templates/readiness-status.yaml` (`approvals[]` / stage `publish_ready` / "agent cannot self-grant"), `templates/handoff/bi-handoff-pack.md` (the existing "Publish approval" section), and the F016-absent / F027-shipped facts (read-only).

---

## Phase 2: Foundational (Blocking Prerequisite)

**Purpose**: Author the one generic template that all three user stories verify against. This is
the single load-bearing artifact -- it MUST be complete before any user-story verification.

**CRITICAL**: No user-story verification can begin until the template exists.

- [ ] T003 Author the GENERIC `templates/handoff/publish-receipt.md` per plan.md Phase 1 design: a copy-me blank with the six sections (Header; Prior-stage gate; Cited publish approval READ-ONLY; No-executor statement; Terminal verdict; See also). Placeholders only -- no C086/pharmacy specifics (FR-001, FR-009). The header banner MUST state: generic copy-me, composes-never-invents, no publishing here (F016 absent), no fake confidence number, ASCII/UTF-8-no-BOM, short paths (mirrors the sibling templates' banner conventions).

**Checkpoint**: The generic template exists; the three user-story behaviors can now be verified.

---

## Phase 3: User Story 1 - Record a terminal receipt that cites the approval and STOPS (Priority: P1) [MVP]

**Goal**: The template, when filled for a table with a recorded `publish_ready` approval, records
the terminal state and reads `pass` -- with the sign-off CITED, not authored.

**Independent Test**: fill the template for a fixture table at Publish Ready with a recorded
`publish_ready` approval; confirm every true field is populated, the sign-off line CITES the
recorded owner (agent authors nothing), the no-executor statement is present, status is `pass`
with `evidence[]` citing the pack + approval.

- [ ] T004 [US1] In `templates/handoff/publish-receipt.md`, author the "Cited publish approval (READ-ONLY)" section so it QUOTES/points at the `publish_ready` `approvals[]` entry shape `{stage, owner, at}` and shows the owner line as a placeholder the agent verifies-but-does-not-author; add the explicit "verify the slot exists, then STOP" instruction (FR-002, FR-003 -- composes with F027).
- [ ] T005 [US1] In the same file, author the "Terminal verdict" section using the readiness four-status set + `evidence[]` + `blocking_reasons[]`; state `pass` is admissible ONLY when a named-human `publish_ready` approval is already recorded; add NO numeric confidence/health field (FR-004, FR-005).
- [ ] T006 [US1] In the same file, author the "See also" section linking the pack (`bi-handoff-pack.md`), the checklist (`handoff-review-checklist.md`), the stage authority (`../../docs/readiness/publish-ready.md`), F016/F027, and the C086 cited instance by reference only (FR-009).

**Checkpoint**: US1 behavior (record + cite + STOP, `pass` on recorded approval) is satisfiable from the template.

---

## Phase 4: User Story 2 - Refuse to self-grant; leave the sign-off un-filled and STOP (Priority: P1)

**Goal**: The template makes the never-self-grant gate explicit: absent a recorded approval the
sign-off stays UN-FILLED and the status is `blocked`.

**Independent Test**: for a fixture with no recorded `publish_ready` approval (and one whose prior
stages are not all `pass`), the receipt's sign-off is un-filled, status `blocked` with the
matching blocking reason, authority class left as a placeholder, 0 self-granted approvals.

- [ ] T007 [US2] In `templates/handoff/publish-receipt.md`, author the "Prior-stage gate" section to restate (cite, never re-decide) that stages 1-6 must each be `pass`; a not-pass prior stage is a `blocked` blocking reason (FR-012).
- [ ] T008 [US2] In the same file, add the explicit never-self-grant guardrail: "absent a recorded `publish_ready` approval, the receipt is `blocked` ('no recorded publish approval'); the agent leaves the sign-off / owner line UN-FILLED, names the required authority class only as a placeholder `<data_owner | governance>`, points at the recorded-approval path (F027), and STOPS -- it never writes an owner or date" (FR-002, FR-011; cites Principle V, NOT Principle IV per FR-010).

**Checkpoint**: US2 behavior (refuse-to-self-grant, `blocked` with un-filled sign-off) is satisfiable.

---

## Phase 5: User Story 3 - Stay strictly inside the record-and-STOP boundary; no executor (Priority: P1)

**Goal**: The template records authorization and STOPS; it never implies an executor, never
publishes.

**Independent Test**: across requests "publish" / "run the adapter" / "deploy to Fabric", 0
publish/executor output, F016 named each time, 0 commands / DB connections; the receipt text
states "no automated publish today (F016 absent)".

- [ ] T009 [US3] In `templates/handoff/publish-receipt.md`, author the "No-executor statement" section: explicit "no automated publish today; F016 (official Power BI MCP / connection; pbi-cli no longer preferred) is the deferred, gated, execution-only owner and is verified ABSENT -- this receipt records authorization and STOPs, it triggers nothing, runs no command, opens no connection, deploys nothing to Fabric" (FR-007).
- [ ] T010 [US3] Verify the template text NOWHERE implies an executor exists and contains 0 pbi-cli/MCP commands, 0 publish/deploy steps, 0 DB connection references, 0 new `retail check` rule mentions (read-only self-check against SC-004, SC-005).

**Checkpoint**: US3 boundary (record-and-STOP, no executor) holds in the template.

---

## Phase 6: Doc note + cross-cutting verification

**Purpose**: The one non-gating doc note + the slice-wide guardrail checks.

- [ ] T011 Add a ONE-LINE, NON-GATING `evidence[]`-style note to `docs/readiness/publish-ready.md` pointing at `../../templates/handoff/publish-receipt.md` as the concrete artifact of the record-and-STOP action (e.g. under "See also" or the `pass` evidence line). It MUST add NO new gate, blocking reason, status, or required artifact; the stage's existing gates stay verbatim (FR-006, SC-005).
- [ ] T012 [P] ASCII + UTF-8-no-BOM scan over both committed files (`publish-receipt.md`, `publish-ready.md`): only `--` and `->`, no glyphs; repo-relative paths `<= 200` chars; no real host/secret (FR-013, SC-009).
- [ ] T013 [P] Generic-only scan: 0 C086/pharmacy or other subject-area specifics in either committed generic file; the worked example is cited by reference only (FR-009, SC-007).
- [ ] T014 [P] No-fake-confidence scan: 0 numeric confidence/readiness/health fields in the template (FR-005, SC-006).
- [ ] T015 Run `retail check` over the repo; confirm exit 0 with the rule count UNCHANGED (no new rule was added) (FR-008, SC-005).
- [ ] T016 Principle V citation scan: every reference to the never-self-grant seam in the template cites Principle V (Agent Stops at Judgment Calls), 0 references mislabel it "Principle IV" (FR-010, SC-008).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies -- read-only confirmation.
- **Foundational (Phase 2)**: depends on Setup -- BLOCKS all user stories (the template must exist).
- **User Stories (Phases 3-5)**: all depend on the template (T003). They author DIFFERENT SECTIONS of the one file, so they are sequenced (same-file edits), not parallel.
- **Doc note + verification (Phase 6)**: T011 depends on the template existing; T012-T014, T016 are read-only scans that can run in parallel [P]; T015 (`retail check`) runs after both files are committed.

### Within Each User Story

- The template is authored once (T003); each story authors/verifies its own section.
- No test-first cycle (no test code is added).

### Parallel Opportunities

- T012, T013, T014, T016 are independent read-only scans -- runnable in parallel.
- The section-authoring tasks (T004-T010) touch the SAME file and must be sequenced.

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1 Setup -> Phase 2 Foundational (author the template).
2. Phase 3 US1 (record + cite + STOP; `pass` on recorded approval).
3. STOP and VALIDATE US1 independently against its Independent Test.

### Incremental Delivery

1. Template authored -> US1 (record/cite) -> US2 (refuse-to-self-grant) -> US3 (no-executor boundary).
2. Add the non-gating doc note (Phase 6) and run the cross-cutting guardrail scans + `retail check`.
3. Each story strengthens the same template without breaking the prior behavior.

---

## Notes

- [P] tasks = different files / independent read-only scans, no dependencies.
- The three user stories share ONE file (the generic template) by design -- the per-story tasks
  author distinct sections, so they are sequenced rather than parallel.
- The per-table filled instance (`mappings/<table>/handoff/publish-receipt.md`, first
  `retail_store_sales` / C086) is a downstream copy-and-fill, NOT part of this generic-authoring
  slice's required output.
- The three Principle V judgment calls (authority class; roadmap promotion / F-number;
  receipt-vs-pack boundary) are NOT tasks -- they are human rulings recorded in spec
  Clarifications -> Open for human and MUST NOT be self-answered.
