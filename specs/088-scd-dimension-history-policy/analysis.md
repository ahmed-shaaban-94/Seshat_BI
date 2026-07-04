# Cross-Artifact Analysis: 088-scd-dimension-history-policy

**Stage**: ANALYZE (read-only). Scope: spec.md, plan.md, tasks.md, research.md,
data-model.md, quickstart.md in this feature directory only. No other file was
edited to produce this output.

**Verdict**: Two concrete coverage gaps found between spec.md's own
Clarifications (C6, C7) and tasks.md's task bodies. Neither is a constitution
violation -- both remain fail-closed in the design itself; tasks.md
under-implements two sub-limbs of already-correct FR text. `scope_ok = true`.
One item is correctly left OPEN for the owner (FR-017 / Q-APPROVAL-SEAM) and is
not a violation.

---

## 1. Requirement-coverage table

| FR | Requirement (short) | Covering task(s) | Status |
|----|----------------------|-------------------|--------|
| FR-001 | Exactly one new nested key `gold_star.dimensions[].scd_type`; no new top-level/sibling key | T001, T003 | OK |
| FR-002 | Permitted values exactly `type_1`/`type_2`; anything else invalid | T003, T013, T018 | OK |
| FR-003 | `scd_type` is human-authored at Mapping Ready, never inferred/defaulted | T003, T016 | OK |
| FR-004 | One `@register`ed rule HR2; reads only committed files; no DB/live/adapter | T005, T019, T027, T038 | OK |
| FR-005 | Missing key OR empty/`null`/`"tbd"` placeholder -> Needs-decision ERROR, no grandfather | T032, T033, T034, T035 | GAP -- see F2 |
| FR-006 | Invalid value (non-empty, non-placeholder, not type_1/type_2) -> ERROR naming value | T014, T015, T018 | GAP -- see F2 |
| FR-007 | Type-2 + drop-and-rebuild construct (either form, non-adjacent OK) -> ERROR | T021, T022, T024, T026, T027, T028, T029, T030 | OK |
| FR-008 | No migration -> no finding; 2+ migration matches -> single ambiguous-migration ERROR naming table + all filenames | T025, T027, T030 | GAP -- see F1 |
| FR-009 | `type_1` dimension never fires regardless of build shape | T023, T024, T030, T031 | OK |
| FR-010 | Never reads `degenerate_dimensions[]` or `date_dimension` | T017 | OK |
| FR-011 | HR2 never decides/defaults `scd_type` on a human's behalf | T037 | OK |
| FR-012 | No SQL execution, no DB connection, migrations read as text only | T037, T038 | OK |
| FR-013 | No numeric score / completeness count anywhere | T005, T035, T037 | OK |
| FR-014 | Six-surface wiring lockstep in the same commit | T006-T012 | OK |
| FR-015 | Generic-only artifacts, no C086/pharmacy specifics | T003, T039 | OK |
| FR-016 | ASCII, UTF-8 no BOM, short paths | T040 | OK |
| FR-017 | OPEN owner ruling (Q-APPROVAL-SEAM); not answered by any task | T044 (records OPEN, does not resolve) | OK (correctly left open) |

Coverage summary: 15 of 17 FRs fully covered; FR-005/FR-006 share one root gap
(C6 placeholder routing not implemented); FR-008 has a second, independent gap
(C7 multi-match not implemented). See Section 5.

---

## 2. Success-criteria testability

| SC | Text | Testable as written? |
|----|------|------------------------|
| SC-001 | Zero findings once every dimension validly declared and no type_2 migration matches the construct | Yes -- logical AND of already-tested branches (T020/T031/T036); no single task runs the composite, but it is derivable, not blocking. |
| SC-002 | Type-2 + drop-and-rebuild -> ERROR (mutation-verified) | Yes -- T025/T031 explicitly mutation-verify (flip type_2->type_1, re-confirm). |
| SC-003 | Missing `scd_type` -> one Needs-decision finding; adding a value clears it | Yes -- T033/T036 mutation-verify the missing-key case. SC-003's own wording covers only the missing-key case, so it is not itself contradicted by F2; FR-005's broader text is. |
| SC-004 | `type_1` never fires (0 false positives) | Yes -- T023/T031. |
| SC-005 | No finding when no migration exists (0 fabricated findings) | Yes -- T025 (b)/(c), zero-match limb only; SC-005 does not itself claim the 2+-match limb (see F1). |
| SC-006 | No numeric score; never writes any file | Yes -- T037 asserts both mechanically. |
| SC-007 | Zero worked-example names in generic artifacts | Yes -- T039 is a direct grep-and-confirm task. |
| SC-008 | Wiring + rule-count lockstep stays green | Yes -- T012, T041, T042. |

All 8 success criteria are stated in a falsifiable, mechanically-checkable form
(finding counts, construct presence/absence, grep-verifiable pattern absence).
No SC uses a numeric score, ratio, or "N of M" tally (hard rule #9 respected).

---

## 3. Terminology consistency

- `scd_type`, `type_1`, `type_2`: spelled identically (lowercase, underscore)
  across all six files. No variant spelling found.
- `HR2`: consistent rule id everywhere; no other id used for this feature.
- `gold_star.dimensions[].scd_type`: quoted identically (dot-and-bracket) in
  spec.md FR-001, plan.md Summary, data-model.md, tasks.md T001/T003.
- "drop-and-rebuild construct": consistent name for the FR-007 detection
  target across spec.md (Overview/US2/FR-007/C5), research.md, data-model.md,
  tasks.md (T021-T030). The C5 correction (non-adjacent, either CTAS or
  DDL+INSERT) propagated cleanly downstream -- quickstart.md Step 4 matches C5
  exactly; no leftover "adjacent CTAS-only" wording found anywhere.
- "Needs-decision": consistent term for the FR-005/US3 finding across spec.md,
  data-model.md, quickstart.md, tasks.md T033/T034. No competing term used.
- Minor non-blocking label variance: spec.md's Key Entities calls the second
  entity "Gold migration construct"; data-model.md titles its section "Gold
  migration construct (the drop-and-rebuild signal)" -- a superset title, same
  substance, not a contradiction.

No terminology contradiction found.

---

## 4. Constitution alignment

| Principle / Rule | Alignment check | Result |
|---|---|---|
| I. Agent-First, Gate-Enforced | Every HR2 finding (FR-005/006/007) is `Severity.ERROR`, never advisory; T041 explicitly does not attempt to green-wash a full-repo `retail check` run. | Satisfied |
| III. Medallion/Gold-Only | HR2 reads only `gold_star.dimensions[]` text and gold migration SQL text; no Postgres/Power BI touch. | Satisfied |
| IV. Source-Mapping-Before-Silver | HR2 adds a Mapping Ready field but does not gate/write `silver.*` SQL; it consumes an already-authored gold migration only as a downstream reader. | Satisfied |
| V. Agent-Stops-at-Judgment | `scd_type` is explicitly human-authored (FR-003/FR-011); research.md's landing-precondition section states explicitly the agent must not scaffold a real value even as a "safe default." FR-017 is correctly left OPEN; T044 only records it. | Satisfied -- this is the one item correctly recorded under open_principle_v, not a violation |
| VI. Defaults-Then-Deviations | C1/C2/C4/C6/C7 recorded as reasonable defaults with stated reasoning/reversibility; C5 explicitly labeled a correction, not a new default. | Satisfied |
| VII. C086-is-an-example | All names in spec.md/data-model.md/tasks.md/quickstart.md are generic (`dim_<entity_a>`, `dim_product`) except research.md's evidentiary quoting of the one real committed migration -- appropriate use as evidence, not as a required template value; T039 polices this at implementation time. | Satisfied |
| VIII. Static-First/Live-Deferred | HR2 is 100% static (FR-004/FR-012); live SCD-2 correctness auditing is named-and-deferred (not silently omitted); F016/live DB never assumed to exist anywhere (Section 6). | Satisfied |
| IX. Secrets/Reproducibility | No host/DSN/secret in any of the six files; FR-016 requires ASCII/UTF-8/no-BOM/short paths. | Satisfied |
| Hard rule #9 (no fabricated score) | FR-013, SC-006, data-model.md's Finding-usage table, and T037's mechanical test all forbid any percentage/ratio/"N of M" in HR2 output. | Satisfied |

No constitution violation found. `scope_ok = true`.

---

## 5. Contradiction / duplication / ambiguity scan

### F1 -- GAP (Medium): FR-008/C7 multi-match migration handling has no covering task

spec.md FR-008 and Clarification C7 require: if the migration glob matches
more than one file for a table, HR2 emits a single fail-closed ERROR naming
the table and every matched filename. data-model.md's Finding taxonomy table
lists this as its own row.

tasks.md's actual task bodies do not implement or test this branch:
- T027's declared signature, `_find_gold_migration(ctx, table_id) -> str |
  None`, can only represent "no match" or "one match" -- there is no return
  shape for "2+ matches."
- T030 (the wiring task) branches only on `None` (no finding) vs. present
  (inspect it) -- no third branch for "matched more than one."
- T025 (the RED test task for US2) asserts exactly three outcomes: ERROR for
  type_2+drop-rebuild, zero findings for type_1, zero findings when the
  migration file is absent. No assertion covers the multi-match ERROR.
- No fixture in Phase 4 (T021-T024) creates two migration files matching the
  same table's glob.
- tasks.md's own "Requirement Coverage Check" maps FR-008 to T025/T027/T030,
  which is true only for the zero-match limb, not the 2+-match limb.

Impact: if tasks.md is executed as literally written, HR2 will not correctly
implement the 2+-match branch of FR-008 (undefined behavior -- likely picking
or ignoring one file, or an unhandled case -- rather than the required single
ambiguous-migration ERROR). This is not a violation in the SPEC (which
correctly requires fail-closed) but is a genuine spec-to-task fidelity gap.
No committed table today has more than one matching migration, so nothing
fails open on the CURRENT tree -- but the task list as written would not
correctly implement FR-008 once a second migration file for the same table
appears.

Severity: Medium.

### F2 -- GAP + latent contradiction (Medium): C6 placeholder routing is not implemented by the tasks as written

spec.md Clarification C6 (and FR-005/FR-006 as amended by C6, and
data-model.md's Finding taxonomy table) require an empty string, `null`, or a
case-insensitive `"tbd"` value to route to FR-005's Needs-decision finding
(same message as a missing key), NOT to FR-006's invalid-value finding.

tasks.md's task bodies do not implement this routing:
- T018 ("for each dimension whose `scd_type` is present but not exactly
  `type_1` or `type_2`, emit `Finding(HR2, ERROR, ...)` naming the dimension
  and the literal value seen") has no placeholder-exclusion clause. As
  literally worded, T018's condition is also true for `scd_type: ""`,
  `scd_type: null`, and `scd_type: "tbd"` -- so a literal implementation would
  route all three placeholder forms to the invalid-value finding (e.g.
  "invalid value: ''"), the exact confusing outcome C6 says to avoid.
- T034 ("for each ... entry with NO `scd_type` key at all") is explicitly
  scoped to "no key at all" and does not cover "key present but holding a
  placeholder value."
- T032's fixture covers only "no `scd_type` key" variants; no fixture
  exercises `scd_type: ""`, `scd_type: null`, or `scd_type: "TBD"`.
- T033's RED tests correspondingly assert only the missing-key outcome, not
  the placeholder-routes-to-FR-005 outcome C6 requires.
- The "Requirement Coverage Check" maps FR-005 to T032/T033/T034/T035 and
  FR-006 to T014/T015/T018 -- correct for the non-placeholder sub-cases of
  each, but the mapping does not surface that the placeholder sub-case
  (explicitly named by C6 in both FRs) has no task.

Impact: both a coverage gap (no task/fixture exercises C6's placeholder
routing) and a latent contradiction (T018's condition as worded would
misroute all three placeholder forms). This does not fail open -- both
outcomes remain `Severity.ERROR` regardless of which branch fires, so
Principle I is not violated -- but a reviewer would see a confusing "invalid
value: ''" message instead of the "declare type_1 or type_2" remedy C6
intends.

Severity: Medium.

### F3 -- Minor factual staleness (Low, non-blocking): spec.md claims sibling directories "do not exist yet," but they do

spec.md's "Boundary against neighbouring shipped work" section states: "This
feature is coordinated, NOT collision-tested, against three OTHER in-flight
`source-map.yaml` adders ... None of those directories exist yet in this
tree." Direct check of this worktree shows all three already exist with a
full artifact set each: `specs/090-source-freshness-gate/`,
`specs/103-currency-unit-contract/`, `specs/105-source-data-contract-restatement/`.

Substance check (verified directly against each sibling's own FR-001): none
collide with 088's schema footprint.
- 090 (freshness) adds `meta.freshness` (nested under `meta:`, not `gold_star`).
- 103 (currency/unit) adds `columns[].unit` and `columns[].currency` (nested
  under `columns[]`, not `gold_star.dimensions[]`).
- 105 (data-contract) defines a wholly separate new template file,
  `templates/source-data-contract.yaml`, touching neither `gold_star` nor
  `columns[]` in `source-map.yaml`.

The collision-avoidance allocation HOLDS in substance -- only the prose claim
that the directories "do not exist yet" is stale. This does not affect
`scope_ok` and requires no code change; it is a cosmetic narrative
inaccuracy, not a blocking finding.

Severity: Low, non-blocking, informational only.

### No other contradictions, duplications, or ambiguities found

- No FR contradicts another FR within spec.md.
- No task in tasks.md contradicts a Clarification other than the T018/C6
  interaction already recorded as F2.
- data-model.md's Finding taxonomy table is fully consistent with spec.md's
  FR-005 through FR-010 and the Edge Cases section; the two gaps are
  tasks.md-level coverage gaps, not data-model contradictions (data-model.md
  itself correctly states both cases).
- plan.md's Constitution Check table and spec.md's principle-by-principle
  framing agree point-for-point.
- quickstart.md's walkthrough matches FR-005/FR-007/FR-008/FR-009's stated
  behavior at every numbered step it covers; it does not walk through the C6
  placeholder case or the C7 multi-match case either -- consistent with those
  being the same two gaps recorded above, not a separate finding.

---

## 6. Deferred-capability leakage scan (F016 / live DB)

- F016 (Power BI execution adapter): never invoked or assumed reachable in any
  of the six files. research.md's "Deferred capabilities NOT assumed" section
  names it explicitly as gated + LAST and assumed NOT to exist. Quickstart.md
  Step 7 explicitly confirms no database connection, SQL execution, Power BI
  Desktop session, or network access is required by any step.
- Live DB / `retail validate`: HR2 is scoped to reading committed TEXT only;
  no task, FR, or quickstart step opens a database connection or calls
  `retail validate`. Live SCD-2 row-level correctness auditing is explicitly
  named as out of scope and deferred to "a future `retail validate` extension"
  in spec.md Assumptions, plan.md's Principle VIII row, and research.md's
  deferred-capabilities section -- named-and-deferred, not silently assumed.
  T038 mechanically enforces this via a grep-style assertion against live-DB
  imports.
- A "PENDING LIVE ..." marker convention (used by sibling spec 090 for its
  live-reporting surface) is absent here -- correctly so, since 088/HR2 has no
  live-reporting limb at all to mark.
- Positive Type-2 construct recognition is correctly named as future scope
  (C3) rather than assumed implementable now; T029 authors a visible
  `[FUTURE SCOPE]` code comment rather than silently omitting the limb.

Result: CLEAN. No artifact in this feature assumes F016 or a live DB surface
exists. Every deferred capability is explicitly named, and the static/live
boundary is enforced both by design (FR-004/FR-012) and by a dedicated test
task (T038).

---

## Summary of findings

| ID | Severity | Summary |
|----|----------|---------|
| F1 | Medium | FR-008/C7 multi-match migration-file handling (2+ files -> single ambiguous-migration ERROR) has no covering task, no capable helper signature (T027), and no fixture. |
| F2 | Medium | C6's placeholder-routing rule (`""`/`null`/`"tbd"` -> FR-005 Needs-decision, not FR-006 invalid-value) has no covering task or fixture; T018 as literally worded would misroute all three placeholder forms to the invalid-value finding, contradicting C6's stated intent (though both outcomes remain ERROR, so this is not a fail-open defect). |
| F3 | Low (non-blocking) | spec.md's Overview claims sibling directories 090/103/105 "do not exist yet in this tree," but all three now exist with full artifact sets. The substantive collision-avoidance claim still holds (verified: none touch `gold_star.dimensions[]`) -- a stale narrative sentence, not a schema collision. |

Constitution violations found: none. `scope_ok = true`.

Correctly-open item (not a violation; not resolved here): FR-017 /
Q-APPROVAL-SEAM -- whether `scd_type` declaration needs its own named-human
approval seam or folds into the existing Mapping Ready `approvals[]` sign-off.
Left OPEN for the owner across all six artifacts, consistent with Principle V;
T044 records it as still open and is explicitly marked "[OWNER SEAM -- OPEN,
do not answer]."
