# Tasks: Publish Approval Receipt (record-and-STOP token)

**Input**: Design documents from `specs/041-publish-approval-receipt-record-and/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: No automated test code is added (the spec requests none; this is a docs/templates
authoring slice). Verification is by `retail check` exit 0 (rule count UNCHANGED) + reading the
committed artifacts against Success Criteria SC-001..SC-009.

**Organization**: Tasks are grouped by user story. Ruling B (owner, 2026-06-29): the record-and-STOP
semantics FOLD INTO the EXISTING "Publish approval" section of `templates/handoff/bi-handoff-pack.md`
(line 87) -- NO new standalone artifact is created. The single edited target is that one section; each
user story's behavior is then VERIFIED against the already-present fields, so the stories share one
section by design -- the per-story tasks are the verification slices, not separate files.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths are included.

## Path Conventions

Docs/templates authoring slice. No `src/` or `tests/`. The committed text lives in
`templates/handoff/` and `docs/readiness/`. The one edited file is
`templates/handoff/bi-handoff-pack.md`; the one annotated file is `docs/readiness/publish-ready.md`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the home and the exact edit target before authoring.

- [ ] T001 Confirm `templates/handoff/` holds the two siblings `bi-handoff-pack.md` and `handoff-review-checklist.md`, and LOCATE the existing "Publish approval (the one non-inherited thing the pack adds)" section in `templates/handoff/bi-handoff-pack.md` (line 87) -- this is the one edited target. No new file is created (read-only check, no change).
- [ ] T002 Re-read the four ground-truth seams so the edit cites them exactly: `docs/readiness/publish-ready.md` (record-and-STOP prose in "Next allowed action" + the data-owner / governance owner), `templates/readiness-status.yaml` (`approvals[]` / stage `publish_ready` / "agent cannot self-grant"), `templates/handoff/bi-handoff-pack.md` (the EXISTING "Publish approval" section, lines 87-101, whose `approvals[]` / un-fillable-owner / never-self-grant / blocked-not-pass fields ALREADY EXIST and STAY VERBATIM), and the F016-absent / F027-shipped facts (read-only).

---

## Phase 2: Foundational (Blocking Prerequisite)

**Purpose**: Apply the ONE edit that adds the record-and-STOP framing to the existing pack section.
Every user story verifies against the edited section, so the edit MUST be complete before any
user-story verification.

**CRITICAL**: No user-story verification can begin until the edit is applied.

- [ ] T003 EDIT the existing `templates/handoff/bi-handoff-pack.md` "Publish approval" section (line 87) to ADD exactly TWO things, and ONLY these two -- everything else in the section STAYS VERBATIM: (a) a record-and-STOP LABEL/framing stating this section IS the terminal publish-authorization record (the record-and-STOP token), and (b) one explicit line: "No automated publish today; F016 (the official Power BI MCP / connection adapter; `pbi-cli` no longer preferred) is the deferred, gated, execution-only owner and is verified ABSENT -- this section records authorization and STOPS." Do NOT re-author the `approvals[]` `{stage, owner, at}` shape (lines 93-98), the un-fillable `<data_owner | governance>` owner placeholder, the never-self-grant gate ("the agent CANNOT self-grant it (Principle V) -- it STOPS", lines 90-91), or the blocked-not-pass rule ("Absent approval -> `publish_ready` is `blocked` ... does NOT become `pass`", lines 100-101); all are ALREADY THERE and unchanged. The added words cite Principle V (NOT Principle IV), add NO number, and name NO person. ASCII, UTF-8 no BOM (FR-001, FR-007; cites Principle V per FR-010).

**Checkpoint**: The pack's "Publish approval" section now carries the record-and-STOP label + F016-absent line; the three user-story behaviors can now be verified against it.

---

## Phase 3: User Story 1 - Record a terminal authorization that cites the approval and STOPS (Priority: P1) [MVP]

**Goal**: The edited "Publish approval" section, when filled for a table with a recorded
`publish_ready` approval, records the terminal state and reads `pass` -- with the sign-off CITED in
the already-present `approvals[]` block, not authored.

**Independent Test**: fill the pack's "Publish approval" section for a fixture table at Publish Ready
with a recorded `publish_ready` approval; confirm the cited `approvals[]` owner line is populated by
the named human (the agent authors nothing), the added no-executor line is present, and the pack's
existing "Readiness verdict" reads `pass` with `evidence[]` citing the pack + approval.

- [ ] T004 [US1] In `templates/handoff/bi-handoff-pack.md`, VERIFY (read-only, do not re-author) that the "Publish approval" section already QUOTES the `publish_ready` `approvals[]` entry shape `{stage, owner, at}` (lines 93-98) and shows the owner as the placeholder `<data_owner | governance>` the agent verifies-but-does-not-author; confirm the T003 record-and-STOP label frames this as cited-then-STOP, composing with F027 (FR-002, FR-003).
- [ ] T005 [US1] In the same file, VERIFY (read-only) that the existing "Readiness verdict for this pack" section (lines 103-114) already uses the readiness four-status set + `evidence[]`-citing `pass` criterion, that `pass` requires the recorded `publish_ready` approval, and that it carries NO numeric confidence/health field ("NO numeric confidence/health score is emitted (roadmap rule #9)", line 114) (FR-004, FR-005).
- [ ] T006 [US1] In the same file, VERIFY (read-only) that the existing "See also" section (lines 116-125) already links the checklist (`handoff-review-checklist.md`), the stage authority (`../../docs/readiness/publish-ready.md`), the deferred F016 adapter + Principle V, and cites the C086 worked instance by reference only; confirm the T003 edit added no subject-area specific to it (FR-009).

**Checkpoint**: US1 behavior (record + cite + STOP, `pass` on recorded approval) is satisfiable from the edited section.

---

## Phase 4: User Story 2 - Refuse to self-grant; leave the sign-off un-filled and STOP (Priority: P1)

**Goal**: The pack's "Publish approval" section makes the never-self-grant gate explicit: absent a
recorded approval the sign-off stays UN-FILLED and the status is `blocked`. This is ALREADY in the
section; US2 verifies the T003 label did not weaken it.

**Independent Test**: for a fixture with no recorded `publish_ready` approval (and one whose prior
stages are not all `pass`), the section's sign-off is un-filled, the verdict is `blocked` with the
matching blocking reason, the authority class stays the placeholder `<data_owner | governance>`, and
0 self-granted approvals.

- [ ] T007 [US2] In `templates/handoff/bi-handoff-pack.md`, VERIFY (read-only) that the existing Header "Prior-stage gate" row + note (lines 37-41) already restate (cite, never re-decide) that stages 1-6 must each be `pass`, and that a not-pass prior stage keeps `publish_ready` `blocked`; confirm T003 added no override (FR-012).
- [ ] T008 [US2] In the same file, VERIFY (read-only) that the existing never-self-grant guardrail is intact and UNWEAKENED after T003: "the agent CANNOT self-grant it (Principle V) -- it STOPS and requests the named owner" (lines 90-91), the owner stays the un-filled placeholder `<data_owner | governance>`, and "Absent approval -> `publish_ready` is `blocked` ('no recorded publish approval'); it does NOT become `pass`" (lines 100-101). Confirm the seam cites Principle V, NOT Principle IV (FR-002, FR-011; cites Principle V per FR-010).

**Checkpoint**: US2 behavior (refuse-to-self-grant, `blocked` with un-filled sign-off) is satisfiable and the T003 edit did not weaken it.

---

## Phase 5: User Story 3 - Stay strictly inside the record-and-STOP boundary; no executor (Priority: P1)

**Goal**: The edited section records authorization and STOPS; it never implies an executor, never
publishes. The T003 F016-absent line carries this explicitly.

**Independent Test**: across requests "publish" / "run the adapter" / "deploy to Fabric", 0
publish/executor output, F016 named, 0 commands / DB connections; the section states "no automated
publish today (F016 absent)".

- [ ] T009 [US3] In `templates/handoff/bi-handoff-pack.md`, VERIFY the T003-added no-executor line is present and exact in the "Publish approval" section: "No automated publish today; F016 (the official Power BI MCP / connection adapter; `pbi-cli` no longer preferred) is the deferred, gated, execution-only owner and is verified ABSENT -- this section records authorization and STOPS." Confirm it composes with the existing "No publishing here" banner (lines 16-19) and the existing "See also" F016 pointer (lines 123-125), neither of which is re-authored (FR-007).
- [ ] T010 [US3] VERIFY (read-only self-check) the edited `templates/handoff/bi-handoff-pack.md` NOWHERE implies an executor exists and that the T003 edit introduced 0 pbi-cli/MCP commands, 0 publish/deploy steps, 0 DB connection references, 0 new `retail check` rule mentions (against SC-004, SC-005).

**Checkpoint**: US3 boundary (record-and-STOP, no executor) holds in the edited section.

---

## Phase 6: Doc note + cross-cutting verification

**Purpose**: The one non-gating doc note + the slice-wide guardrail checks over the two touched files.

- [ ] T011 Add a ONE-LINE, NON-GATING `evidence[]`-style note to `docs/readiness/publish-ready.md` (e.g. in the "See also" section, lines 85-92, or on the `pass` evidence line, 52) pointing at the `templates/handoff/bi-handoff-pack.md` "Publish approval" section as the concrete record of the record-and-STOP action. It MUST add NO new gate, blocking reason, status, or required artifact; the stage's existing gates (lines 35-43, 54-60) stay verbatim (FR-006, SC-005).
- [ ] T012 [P] ASCII + UTF-8-no-BOM scan over both touched files (`templates/handoff/bi-handoff-pack.md`, `docs/readiness/publish-ready.md`): only `--` and `->`, no glyphs; repo-relative paths `<= 200` chars; no real host/secret; confirm the T003 + T011 edits introduced none (FR-013, SC-009).
- [ ] T013 [P] Generic-only scan: 0 C086/pharmacy or other subject-area specifics introduced by the T003 edit or the T011 note in either file; the worked example stays cited by reference only (FR-009, SC-007).
- [ ] T014 [P] No-fake-confidence scan: confirm the T003 edit added 0 numeric confidence/readiness/health fields to `templates/handoff/bi-handoff-pack.md`; the existing rule-#9 line (line 114) stands (FR-005, SC-006).
- [ ] T015 Run `retail check` over the repo; confirm exit 0 with the rule count UNCHANGED (no new rule was added) (FR-008, SC-005).
- [ ] T016 Principle V citation scan: every reference to the never-self-grant seam in `templates/handoff/bi-handoff-pack.md` (the existing lines + the T003 additions) cites Principle V (Agent Stops at Judgment Calls); 0 references mislabel it "Principle IV" (FR-010, SC-008).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies -- read-only confirmation of the edit target.
- **Foundational (Phase 2)**: depends on Setup -- BLOCKS all user stories (the T003 edit must be applied).
- **User Stories (Phases 3-5)**: all depend on the T003 edit. They VERIFY DIFFERENT existing fields of the one "Publish approval" section (plus its sibling sections), so they are sequenced (same-file reads/verification), not parallel.
- **Doc note + verification (Phase 6)**: T011 depends on the T003 edit existing; T012-T014, T016 are read-only scans that can run in parallel [P]; T015 (`retail check`) runs after both files are committed.

### Within Each User Story

- The pack section is edited once (T003); each story verifies its own slice of the existing/edited section.
- No test-first cycle (no test code is added).

### Parallel Opportunities

- T012, T013, T014, T016 are independent read-only scans -- runnable in parallel.
- The single edit (T003) and the per-story verification tasks (T004-T010) touch the SAME file and must be sequenced.

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1 Setup -> Phase 2 Foundational (apply the T003 edit to the existing pack section).
2. Phase 3 US1 (record + cite + STOP; `pass` on recorded approval).
3. STOP and VALIDATE US1 independently against its Independent Test.

### Incremental Delivery

1. Edit applied -> US1 (record/cite) -> US2 (refuse-to-self-grant) -> US3 (no-executor boundary).
2. Add the non-gating doc note (Phase 6) and run the cross-cutting guardrail scans + `retail check`.
3. Each story verifies the same edited section without changing the prior behavior.

---

## Notes

- [P] tasks = different files / independent read-only scans, no dependencies.
- The three user stories verify ONE edited section by design (Ruling B: fold into the existing pack
  "Publish approval" section, do not create a third presentation of the sign-off facts) -- the
  per-story tasks confirm distinct existing fields, so they are sequenced rather than parallel.
- The per-table filled instance is the EXISTING per-table pack copy
  (`mappings/<table>/handoff/bi-handoff-pack.md`, first `retail_store_sales` / C086) -- there is no
  separate per-table receipt; the "Publish approval" section of that copy IS the record. This is a
  downstream copy-and-fill, NOT part of this generic-authoring slice's required output.
- The three Principle V judgment calls (authority class -> data-owner OR governance; roadmap
  promotion / F-number -> stay spec-only, no F-number; receipt-vs-pack boundary -> Ruling B, fold
  into the pack section) were the human owner's to make and were RULED at ratification
  (Ahmed Shaaban, 2026-06-29); they are recorded in spec Clarifications -> Owner judgment calls and
  MUST NOT be self-answered.
