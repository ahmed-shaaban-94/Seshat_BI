# Cross-Artifact Analysis: 092-rls-access-readiness

**Date**: 2026-07-04 | **Scope**: spec.md, plan.md, tasks.md, research.md,
data-model.md, quickstart.md vs the Seshat BI constitution
(`.specify/memory/constitution.md`, v1.7.0) and the live repo tree. Read-only;
no source artifact under review was edited to produce this report.

## Method

Read all six artifacts in full. Verified every cited repo path and precedent
against the actual worktree: `src/retail/rules/{g6,readiness_status,sql}.py`,
`src/retail/core.py` (`Severity` enum), `templates/metric-contract.yaml`,
`mappings/retail_store_sales/metrics/`, `docs/readiness/semantic-model-ready.md`,
`.claude/skills/retail-semantic-check/SKILL.md`, and confirmed **HR6 is an
unused rule id** (`grep -rn "HR6" src/ docs/` returns nothing pre-existing).

## Requirement-coverage table

| FR | Requirement (summary) | Covering task/artifact | Status |
|----|------------------------|-------------------------|--------|
| FR-001 | New template `templates/rls-role-contract.yaml`, mirrors metric-contract shape | T004; data-model.md Entity 1 | OK |
| FR-002 | Contract is a SEPARATE file; no key added to metric-contract.yaml/kpi-pack.yaml | T004, T030 | OK |
| FR-003 | Binding MUST reference `gold` schema only | T004, T019, T021 | OK |
| FR-004 | Exactly one new static rule, id HR6 | T006, T008, T028 | OK |
| FR-005 | HR6 fails on missing/empty/blank filter column (+ fact-table hard-fail, C1) | T003, T010, T013, T015, T017, T018, T029 | OK |
| FR-006 | HR6 fails when filter column doesn't exist on referenced gold table | T002, T003, T007, T011, T016, T018 | OK |
| FR-007 | HR6 fails on silver/bronze binding or absent gold table | T002, T003, T007, T012, T016, T018 | OK |
| FR-008 | HR6 fails on `status: pass` with empty `evidence[]` | T003, T022, T024, T025, T027 | OK |
| FR-009 | HR6 fails on duplicate role `name` | T003, T023, T026, T027 | OK |
| FR-010 | Record Q-ZERO-ROLES as OPEN; MUST NOT resolve it | T005, T009, T034 | OK (correctly left open, not "resolved") |
| FR-011 | HR6 finding(s) surface in `blocking_reasons[]` the same way D1-D11/G6 already do | T014, T018 | GAP (partial) -- see F1/F2 |
| FR-012 | HR6 MUST NOT execute/connect live; structure-only | T006, T007, T024, T034 | OK |
| FR-013 | Feature MUST NOT decide who-sees-what | T004 (placeholders only; no task resolves it) | OK |
| FR-014 | No numeric confidence/health/maturity score anywhere | T004, T020, T032 | OK |
| FR-015 | Template/rule stay generic; no C086 token | T002, T004, T031 | OK |
| FR-016 | ASCII/UTF-8-no-BOM; Windows 260-char path budget | T004, T033b | OK |
| FR-017 | `semantic-model-ready.md` lists HR6 in Required checks + Blocking reasons | T005, T033 | OK (doc only -- see F2 for the adjacent skill-file gap) |
| FR-018 | No live-DB-backed check introduced; live verification deferred | T034 | OK |

17 of 18 FRs are fully covered by name-matched tasks. FR-011 is partially
covered: T014/T018 confirm the generic wiring contract (an ERROR-severity
`Finding` blocks the stage via `retail check`'s existing non-zero-exit path),
but no task updates the one artifact that actually enumerates which rule
ids get cited into `blocking_reasons[]` by name -- see F2.

## Success-criteria testability

| SC | Criterion | Testable? | Task-mapped? |
|----|-----------|-----------|---------------|
| SC-001 | 100% of contracts with empty/missing filter-column produce an HR6 finding | Yes -- binary, automatable (T010) | Yes |
| SC-002 | 100% of contracts whose filter column doesn't exist on the gold table produce an HR6 finding | Yes -- binary, automatable (T011) | Yes |
| SC-003 | 0 well-formed contracts produce an HR6 finding | Yes -- binary, automatable (T019) | Yes |
| SC-004 | 0 findings/contracts/rule source contain a numeric score or "N of M" count | Yes -- grep-testable (T020, T032) | Yes |
| SC-005 | 0 keys added to metric-contract.yaml/kpi-pack.yaml | Yes -- `git diff --stat` testable (T030) | Yes |
| SC-006 | semantic-model-ready.md lists HR6 in both required tables | Yes -- doc-diff testable (T033) | Yes |
| SC-007 | 0 generic artifacts contain a C086-specific token | Yes -- grep-testable (T031) | Yes |

All 7 success criteria are quantified (100%/0, not vague adjectives) and each
maps to at least one concrete, automatable verification task. No SC relies on
a subjective judgment ("fast", "robust", "intuitive") without a measurable
proxy. None require live-DB infrastructure to test (consistent with Principle
VIII/FR-018).

## Terminology consistency

- "RLS role contract" / "role contract": used consistently across spec,
  plan, research, data-model, quickstart, and tasks. No drift.
- "Filter binding" / `filter: {gold_table, column}`: consistent field
  names across spec (Key Entities), data-model (Entity 1/2 shape), and tasks
  (T004, T015-T017 all say `filter.column`/`filter.gold_table`).
- "HR6": consistent id across all six artifacts; matches the reserved
  allocation in the task instructions and is confirmed unused in the live
  rule registry.
- "Q-ZERO-ROLES": consistent label for the same open question across spec
  (Clarifications), plan (Constitution Check), data-model (Entity 3 note),
  and tasks (FR Coverage Map). No renaming drift.
- Severity terminology: "fail closed" / `Severity.ERROR` used
  consistently; spec Clarification C1, plan's Constraints section, and
  data-model's Entity 3 table all agree HR6 is ERROR-only, never WARNING.
  Matches the live `Severity` enum in `src/retail/core.py`.
- Minor: spec/plan/quickstart alternate between "gold dimension table" and
  "gold.dim_* table" -- same referent, informal vs. literal-prefix phrasing.
  Not a defect (data-model.md's Field Notes table makes the literal form
  explicit: `^gold\.\w+$` + `dim_` prefix), but noted for terminology
  precision (see F4).

## Constitution alignment

Checked against all nine Core Principles plus hard rule #9 (no fabricated
score) and the F016 boundary.

| Principle | Alignment |
|---|---|
| I. Agent-First, Gate-Enforced | HR6 is a registered `retail check` rule returning `Finding(severity=Severity.ERROR, ...)` -- fails closed via non-zero exit, never advisory. Compliant. |
| II. Depend, Never Fork | Not engaged by this feature (no execution-adapter surface touched). N/A, no conflict. |
| III. Medallion, Gold-Only | FR-003/006/007 restrict bindings to `gold.*`; a `silver`/`bronze` binding is a hard failure. Compliant. |
| IV. Source-Mapping-Before-Silver | Not engaged -- HR6 operates at Stage 5, post-Gold-Ready; no `silver.*` SQL is authored or implied. Compliant (N/A). |
| V. Agent-Stops-at-Judgment | FR-013 explicitly refuses to decide who-sees-what; FR-010/Q-ZERO-ROLES is recorded OPEN, not resolved, and the plan's non-negotiable constraint ("no version of this feature may ship code that treats zero contracts as either a hard block or a clean pass") is the correct enforcement shape. Compliant. |
| VI. Defaults-Then-Deviations | Clarifications C1/C3/C4 record reversible, constitution-safe defaults with stated reasoning, mirroring shipped precedent (F009 shape, G6 rule shape) rather than inventing new mechanisms. Compliant. |
| VII. C086-is-an-example | FR-015/SC-007 forbid any C086/retail_store_sales token in the template or rule source; data-model.md's shapes use only placeholders. Compliant. |
| VIII. Static-First/Live-Deferred | FR-006/FR-012/FR-018 restrict HR6 to reading committed YAML + committed migration SQL; no live DB, no live PBIP read. Research's "Deferred capabilities NOT assumed" section and quickstart's guardrails both explicitly disclaim F016 and live-DB. Compliant. |
| IX. Secrets/Reproducibility | FR-016 requires ASCII/UTF-8-no-BOM and Windows-260-char-safe paths; no host/DSN/secret is introduced anywhere in the six artifacts. Compliant. |
| Hard rule #9 (no fabricated score) | FR-014/SC-004 forbid any numeric confidence/health/maturity field or "N of M" count in the template, the rule's findings, or its own source; the readiness block uses exactly the four explicit statuses. Compliant. |
| F016 boundary | Plan's Constitution Check row and quickstart's "What this feature does NOT let you do" both explicitly assume F016 does not exist and never simulate/preview a role filter. Compliant. |

No constitution violation found. The one Principle-V-adjacent item
(Q-ZERO-ROLES) is correctly modeled as an open question, not a resolved
one -- leaving it open is the compliant posture; the violation would be if any
artifact silently encoded a "pass" or "block" default for the zero-contract
case. No artifact does this (spec FR-010, plan's Constitution Check, and
data-model's Entity 3 all say the same thing three times, consistently).

## Contradiction / duplication / ambiguity scan

- F1 (MEDIUM) -- Spec vs. plan/data-model/tasks disagree on what HR6 does
  for the zero-contract case (spec.md FR-010 vs. plan.md "Zero-contract
  handling" vs. data-model.md Entity 3 vs. tasks.md T009).
  Spec FR-010's "PENDING DEFAULT" text says: "HR6 records the
  zero-contract state as an explicit, visible fact (not a fabricated pass)."
  This reads as HR6 taking an active recording action for the absence case.
  Plan.md's "Zero-contract handling" section and data-model.md's Entity 3
  both say the opposite in the current slice: "this slice's shipped HR6
  behavior... does not synthesize any finding for that absence -- HR6
  evaluates declared contracts only," with any future INFO-tier surfacing
  left to "a future slice." tasks.md's T009 smoke test then mechanically
  ratifies the plan's reading, asserting `check_rls_role_bindings` returns
  `[]` for zero contracts. Both readings stay Principle-V-safe (neither
  encodes "pass" nor "block"), so this is not a constitution violation --
  but the spec's own wording ("HR6... records the zero-contract state") is
  not what this slice actually builds; only a downstream artifact's
  narrower reading is implemented. A reader of spec.md alone would expect
  HR6 to emit some visible artifact for the zero-contract case; a reader
  of plan.md/data-model.md/tasks.md would correctly expect it to emit
  nothing. Recommend reconciling FR-010's prose to explicitly say this
  slice's HR6 emits no finding for the absence case, and that "recording the
  zero-contract state as an explicit fact" is deferred to a possible future
  slice (matching plan.md's own framing) -- the spec's own downstream
  artifacts already made this narrowing decision; the spec text should say
  so plainly rather than reading as if HR6 does something it does not do.

- F2 (HIGH) -- FR-011's "surfaces in blocking_reasons[]" promise names
  only the stage doc, not the skill that actually performs the
  citing (spec.md FR-011 / tasks.md T005 vs.
  `.claude/skills/retail-semantic-check/SKILL.md`).
  Verified in the live repo: the mechanism by which a `retail check`
  finding becomes a named entry in a table's
  `semantic_model_ready.blocking_reasons[]` is not automatic data-plumbing --
  it is `retail-semantic-check`'s own step-2 interpretive table, which
  currently reads: "Any `D1`-`D8`..., `C1`..., `R1`..., or `G6`... finding is
  a distinct `blocking_reason` (cite the id + locator)." This is a
  hand-enumerated list of rule ids inside the skill's own SKILL.md, separate
  from `docs/readiness/semantic-model-ready.md`'s "Required checks" table
  (which T005 does update). No task in tasks.md, and no file in plan.md's
  Project Structure list, updates
  `.claude/skills/retail-semantic-check/SKILL.md`'s step-2 enumeration to
  add HR6 alongside D1-D8/C1/R1/G6. Mechanically, an HR6 `Severity.ERROR`
  finding still makes `retail check` exit non-zero (so the stage cannot
  silently reach `pass` -- the hard-fail-closed guarantee holds), but the
  skill's own documented citation table would not explicitly name HR6 when
  a human or agent runs `retail-semantic-check` and reads its interpretation
  of why the stage is blocked, until that skill file is also updated.
  This is a real, if narrower-than-total, gap in FR-011's "the same way an
  existing D1-D11/G6 finding already blocks that stage" claim: G6 is
  named in that skill's table; HR6, as scoped by the current task list,
  would not be. Recommend adding a task (parallel to T005) to update
  `.claude/skills/retail-semantic-check/SKILL.md`'s step-2 table to cite
  HR6 alongside D1-D8/C1/R1/G6, or explicitly noting in tasks.md that this
  is deliberately deferred/out of scope if that is the intended reading.

- F3 (LOW) -- tasks.md T014 is marked [P] but its own prose says it is
  not parallel (tasks.md lines 191, 202-204). T014 carries the [P]
  marker in its task-id line, but the task's own parenthetical note
  immediately says: "(Note: not [P] in practice once sequenced after
  T010-T013 in the same file; marked here only to flag it as conceptually
  independent...)". The Dependencies & Execution Order section elsewhere
  correctly says no task inside `hr6.py`/`test_hr6.py` is ever genuinely
  [P] with another task touching the same file. The [P] marker on T014
  is therefore self-contradicting shorthand -- cosmetic, since the task's own
  prose overrides it and the Execution Order section is unambiguous, but it
  invites a naive parallel-runner (or a human skimming only the task-id
  line) to schedule T014 concurrently with T010-T013 against the same file.
  Recommend dropping the [P] marker from T014's id line since the note
  already says it is not one.

- F4 (LOW) -- informal "gold dimension table" phrasing vs. literal
  `gold.dim_*` regex in spec/plan/quickstart prose (spec.md Overview,
  User Story 1-2 prose, quickstart.md Step 1-3) vs. data-model.md's precise
  `^gold\.\w+$` + prefix-check Field Notes table. Not a substantive
  contradiction -- every artifact agrees on the underlying rule (must be a
  `dim_`-prefixed gold table) -- but the informal prose repeatedly says "a
  real gold dimension column" or "gold dimension table" without the literal
  prefix-match detail, which only data-model.md and research.md (P6) spell
  out precisely. A reader of spec.md alone could wonder whether "dimension"
  is a semantic judgment call (Principle V territory) rather than a
  mechanical `dim_`-prefix check. Clarification C3 in spec.md does resolve
  this precisely, so the ambiguity is fully closed within the same
  document -- flagged only as a readability nit, not a defect requiring a
  fix.

- No duplication detected: no two functional requirements restate the same
  rule in materially different words -- each FR-005 through FR-009 covers a
  distinct, non-overlapping HR6 finding trigger, and Entity 3's six-row
  table in data-model.md maps 1:1 to them with no double-counting.
- No unresolved placeholders (TODO, TKTK, ???, unfilled `<placeholder>`
  tokens meant to be resolved by this stage) were found in spec.md, plan.md,
  tasks.md, research.md, data-model.md, or quickstart.md. The
  `<RoleName>`/`<dim_table>`/`<column>` placeholders in data-model.md are
  intentional generic-template placeholders (Principle VII), not unresolved
  authoring gaps.
- No task ordering contradiction beyond F3: Setup -> Foundational -> US1 ->
  US2 -> US3 -> Polish is a strict, correctly-declared dependency chain: the
  "Dependencies & Execution Order" section explicitly overrides the
  template's default parallel-story assumption and states why (shared
  `hr6.py`/`test_hr6.py`), which is internally consistent with every
  individual task's Story/file annotations.

## Deferred-capability leakage scan

Checked whether any artifact assumes F016 (Power BI execution adapter) or a
live database surface exists, is stubbed, or is silently required.

- F016: research.md's "Deferred capabilities NOT assumed" section
  explicitly states HR6 "never opens a PBIP file, never connects to Power BI
  Desktop or the Power BI service, never evaluates or previews a role filter
  ('view as role')." Plan.md's Constitution Check table has a dedicated
  "F016 boundary" row making the same assertion. Quickstart.md's "What this
  feature does NOT let you do" section states "No live preview... HR6 never
  evaluates a filter against data." No task in tasks.md references a PBIP
  read, a Power BI connection, or a "view as role" action. Clean -- no
  leakage.
- Live database: FR-006/FR-012/FR-018 all explicitly restrict HR6 to
  reading committed `warehouse/migrations/*.sql` text via the same
  regex-family mechanism S6/S8 already use (research P5) -- never a live
  Postgres/`information_schema` query. Plan.md's Technical Context
  ("Storage: N/A at runtime") and Constraints section both restate this. No
  task imports a DB driver or references a DSN/connection string. T034
  explicitly confirms the zero-contract `retail check` run "does NOT itself
  fail the build" without touching a live DB. Clean -- no leakage.
- New readiness stage: research.md and the spec's Assumptions both
  state explicitly that the seven stages are unchanged and no new `retail
  check` subcommand is added. Confirmed against the live
  `semantic-model-ready.md` (Stage 5 unchanged in name/number). Clean.
- No live validate-surface entanglement: `retail validate` (the live
  surface per constitution Principle VIII) is never referenced as a
  dependency or extension point by any of the six artifacts. Clean.

No artifact in this chain assumes, stubs, or partially builds a capability
this feature's Scope Guard defers. The deferred-capability boundary is
consistently and explicitly restated in research.md, plan.md, and
quickstart.md (redundant across three artifacts, which is a strength
here, not the F1-style duplication flagged above, since all three restate
the identical boundary rather than disagreeing on it).

## Collision-avoidance allocation -- verified held

- HR6 unused: confirmed via repo-wide grep -- no existing rule module,
  manifest entry, or doc references `HR6` before this feature.
- Separate file: `templates/rls-role-contract.yaml` does not exist yet
  (to be created by T004); `templates/metric-contract.yaml` is untouched by
  any task in tasks.md (T030 adds an explicit grep-verification step for
  this).
- No metric-contract.yaml/kpi-pack.yaml key additions: no task edits
  either file; SC-005 and T030 both test for this.

## Metrics

- Total Functional Requirements: 18 (FR-001..FR-018)
- Total Success Criteria: 7 (SC-001..SC-007)
- Total Tasks: 39 (T001-T034, including T033b; T014 counted once)
- FR Coverage: 18/18 map to >=1 task (100%); 17/18 fully covered, 1 partially
  covered (FR-011 -- see F1/F2)
- SC Coverage: 7/7 map to >=1 task (100%)
- Ambiguity count: 1 (F4, LOW, self-resolved within the same document)
- Duplication count: 0
- Contradiction count: 1 (F1, MEDIUM -- spec prose vs. shipped-slice behavior)
- Gap count: 1 (F2, HIGH -- skill-file enumeration not updated for HR6)
- Constitution violations: 0
- Critical issues: 0

## Open Principle-V items (for a named human, not resolved by this analysis)

- Q-ZERO-ROLES (FR-010): whether a table with zero committed
  `rls-role-contract.yaml` files should block, warn, or pass Semantic Model
  Ready is explicitly recorded as OPEN across spec.md, plan.md, and
  data-model.md. This analysis confirms the artifacts correctly leave it
  open (no silent default encoded) and does not attempt to resolve it.

## Verdict

scope_ok = true. No constitution principle is violated by this artifact
chain. The Scope Guard (no who-sees-what decision, no execution, static
bind-check only) is honored consistently across all six documents, and the
collision-avoidance allocation (HR6 reserved+unused, separate template file,
zero metric-contract.yaml/kpi-pack.yaml key additions) holds. Two findings
warrant attention before/alongside implementation:

1. F2 (HIGH): add a task to update
   `.claude/skills/retail-semantic-check/SKILL.md`'s step-2 rule-citation
   table to name HR6 alongside D1-D8/C1/R1/G6, so FR-011's "the same way an
   existing D1-D11/G6 finding already blocks that stage" claim is fully,
   not just mechanically, true.
2. F1 (MEDIUM): reconcile spec.md FR-010's "HR6 records the
   zero-contract state as an explicit, visible fact" wording with the
   narrower behavior plan.md/data-model.md/tasks.md actually specify and
   build (no finding synthesized for the absence case in this slice).

F3 and F4 are LOW-severity, non-blocking wording/marker nits. No CRITICAL
issues were found; nothing here need block proceeding to
`/speckit-implement`, but F1/F2 should be resolved first for artifact
honesty (F1) and gate-doc completeness (F2).
