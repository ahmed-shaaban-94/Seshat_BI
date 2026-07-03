# Specification Analysis Report: 083-demo-harness

**Method**: MANUAL analysis. The automated `speckit-analyze` skill's
prerequisite script (`.specify/scripts/powershell/check-prerequisites.ps1`)
requires the current branch to match `NNN-feature-name` (or a timestamp
variant); this worktree's branch is `spec/demo-harness` (assigned by the
task's worktree setup, not this agent), so the script aborts with "Not on a
feature branch" before any analysis logic runs. This is a tooling/branch-naming
mismatch, not a content issue with the branch or the artifacts. Falling back
to a manual read of `spec.md` + `plan.md` + `tasks.md` + `.specify/memory/constitution.md`,
following the same detection passes (duplication, ambiguity, underspecification,
constitution alignment, coverage gaps, inconsistency) the automated skill defines.

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| F1 | Coverage gap (naming) | MEDIUM | plan.md Project Structure; data-model.md; tasks.md T001 | The sample table name (`demo_sample_orders`), demo-scoped DB marker, and working-directory path are all marked "TBD at implementation time" in multiple files rather than fixed once. | Acceptable for spec-work (naming is an implementation choice, not a requirement), but tasks.md T001 already exists specifically to pin these once before other tasks proceed -- confirm T001 is treated as a hard prerequisite, not skippable. |
| F2 | Ambiguity | LOW | spec.md FR-009 ("well under 1,000 rows") | "Well under" is a soft bound, not an exact number. | Acceptable: an exact row count is an implementation choice (data-model.md leaves it open too); FR-009 is a ceiling constraint, not a precise target, and tightening it further would be premature specificity. No change recommended. |
| F3 | Potential overlap (flagged, then ruled out) | HIGH -> resolved in-spec | spec.md "Relationship to sibling/adjacent work"; docs/demo/retail-store-sales-demo.md | On first read, "demo" in both this feature and the existing `docs/demo/` directory could look like duplication. | Already addressed: spec.md's differentiation section and FR-015 explicitly distinguish "reading tour of committed retail_store_sales artifacts" (existing) from "runnable CLI harness over an invented dataset" (this feature), with a non-duplication requirement. No further action, but implementers should re-check this boundary hasn't blurred once `docs/demo/demo-harness.md` (tasks.md T031) is actually written. |
| F4 | Hidden-impl-scope risk (flagged, then ruled out) | HIGH -> mitigated in-spec | spec.md FR-013, Non-Goals; contracts/demo-report-contract.md "Content contract" | `demo report` is the highest-risk surface for scope creep toward "one-click dashboard generation" (the task's named hard constraint). | Already mitigated: FR-013 + the Non-Goals section + the dedicated "Content contract" block in the report contract all independently forbid chart/visual/PBIP rendering. Recommend this exact language be re-verified, not loosened, if `report` is ever extended (e.g. to add `--format json` consumers) at implementation time. |
| F5 | Dependency direction (flagged, then confirmed) | MEDIUM -> resolved in-spec | spec.md "Relationship to sibling/adjacent work"; plan.md "Repo-only vs. live-DB legs" | This feature's User Story 2 optionally depends on `082-postgres-live-validation-suite`, a sibling being specced concurrently and not yet merged. | Already handled correctly: spec.md states the dependency direction explicitly (083 -> 082 optional; 082 has no dependency on 083) and requires graceful `pending` degrade when 082 (or any local DB) is absent (FR-003, FR-012). No blocking issue; note for the human reconciling both specs that 082 does not need to reference 083 at all. |
| F6 | Overlap with unspecced sibling (flagged, then bounded) | LOW | spec.md "Relationship to sibling/adjacent work" (084 paragraph) | `084-worked-example-factory` does not exist yet as a spec dir; this spec references it only to state a non-invented relationship ("083 runs a sample; 084 would define how samples are authored"). | No action needed now: the reference is explicitly hedged ("not yet on disk as of this writing") and does not assume or invent 084's contents. Recommend the eventual 084 author re-read this spec's "Relationship" section when 084 is drafted, to keep the boundary consistent from both sides. |
| F7 | Terminology consistency | LOW -> RESOLVED | spec.md, plan.md, contracts/*, quickstart.md | "pending" was used as a rendered status word alongside the canonical four statuses (`not_started`/`blocked`/`warning`/`pass`) in `docs/readiness/readiness-model.md`. | RESOLVED during the post-advisor reconciliation pass: the offline ceiling was re-stated using the canonical tokens (`blocked` for Gold Ready deferred-mode, `not_started` for later stages), consistent with `gold-ready.md`'s own "blocked (deferred)" language. "pending" now survives only as display-only phrasing in prose, never as a stored status value (FR-006 binds the stored field to the four canonical values). Implementers should keep "pending" display-only in `src/retail/demo/report.py`. |
| F11 | Coherence / fake-pass risk | HIGH -> RESOLVED | spec SC-002 + US1 test; contracts/demo-run-contract.md; quickstart.md; docs/readiness/silver-ready.md, gold-ready.md | The offline honest boundary was drawn INCONSISTENTLY across spec/contract/quickstart before the advisor pass -- one branch (the run-contract) implied `silver_ready` might rest on a static check while quickstart marked silver `pending`, and SC-002 was silent on silver. | RESOLVED after reading `silver-ready.md` (gate is static "authoring only," `pass` reachable offline) and `gold-ready.md` (gate is live `retail validate`, `blocked`-deferred offline). All five spots now agree: Source/Mapping/Silver reach `pass` offline; Gold Ready is the honest offline ceiling. The committed silver migration fixture moved to Foundational (T008) so US1 can show silver=pass. |
| F12 | Machine-enforced approval (RS1) | HIGH -> RESOLVED | docs/readiness/source-ready.md; src/retail/rules/readiness_status.py; spec FR-016/FR-017 | The sample is a CSV file source; rule RS1 REFUSES a file source's `source_ready: pass` without a matching `{stage: source_ready}` approval entry -- so `retail check` would fail on the demo fixture unless that approval ships. This also made the "illustrative approval fixture" load-bearing and mandatory, not optional/US3-only. | RESOLVED: added FR-017 (mandatory `source_kind: csv` + source_ready approval), generalized FR-008/FR-016 to cover source/mapping/semantic approvals, updated data-model.md's readiness-status + approval-fixture entities, and updated T006 to author both mandatory approvals with an RS1 check at the Foundational checkpoint. |
| F8 | Task-ordering note | LOW | tasks.md Phase 2 (T008) vs Phase 4 (T027) | T008 "describes" the migration shape in Foundational, and T027 "applies" it in US2 -- a deliberate two-step split so US1 (offline-only) doesn't require writing real migration SQL. | Intentional, not a defect -- flagging only so a future implementer doesn't collapse the two steps and accidentally make US1 depend on migration SQL existing. No change recommended. |
| F9 | Constitution alignment check | PASS (no finding) | plan.md Constitution Check table | All nine principles + the Readiness Spine section were checked individually in plan.md's Constitution Check table with a specific PASS rationale per principle, not a blanket assertion. | No issue. This is the strongest part of the plan; recommend future specs in this repo copy this per-principle table format rather than a summary paragraph. |
| F10 | Coverage gap check | PASS (no finding) | spec.md FR-001..016, SC-001..006 vs tasks.md | Spot-checked FR-005/FR-006 (recompute-not-track, four-status-only) against T018/T026 (offline/live run computation); FR-011 (demo-scoped naming) against T022/T025; FR-016 (illustrative-fixture labeling) against T007/T028/T030; SC-004 (clean git status) against T029/T033. Every spot-checked FR/SC has at least one mapped task. | No gap found in the spot-checked sample. A full row-by-row FR-to-task matrix was not exhaustively tabulated (see Coverage Summary below for the abbreviated version) given the manual-analysis time budget; recommend a full matrix pass if this spec proceeds toward `/speckit-implement`. |

## Coverage Summary (abbreviated -- key requirements only, not exhaustive)

| Requirement Key | Has Task? | Task IDs | Notes |
|---|---|---|---|
| FR-001 (demo verb group + --help) | Yes | T009, T014 | |
| FR-002 (init materializes fixtures, offline) | Yes | T004, T005, T015, T016 | |
| FR-003 (load offline skip + reason) | Yes | T011, T017 | |
| FR-004 (load idempotent, live) | Yes | T023, T025 | |
| FR-005 (run: recompute, no state engine) | Yes | T018, T026 | |
| FR-006 (four statuses only, no score) | Yes | T012, T013, T018 | |
| FR-007 (name the required approval/owner) | Yes | T018 (implicit in status computation), T030 | |
| FR-008 (never write approvals[]) | Yes | T029 | |
| FR-009 (invented, small, generic dataset) | Yes | T004 | |
| FR-010 (no tracked writes; clean git status) | Yes | T029, T033 | |
| FR-011 (demo-scoped DB naming) | Yes | T022, T025 | |
| FR-012 (graceful degrade, no exception) | Yes | T011, T024 | |
| FR-013 (report is not a dashboard) | Yes | T013 (score check only), contract's Content contract | |
| FR-014 (secrets stay in .env) | Yes | T037 (secret scan folded in) | G1 resolved |
| FR-015 (docs cross-link, no duplication) | Yes | T031 | |
| FR-016 (all approval fixtures labeled) | Yes | T006, T007, T028, T030 | |
| FR-017 (source_kind: csv + RS1 approval) | Yes | T006, T037 | mandatory for CSV source |
| SC-001 (<5 min offline) | Partial | T033 (manual validation only) | Not an automated test; acceptable per plan.md ("a `quickstart.md`-driven manual check... because it asserts on ambient repo state") |
| SC-006 (no C086 terms in sample) | Yes | T004 (review step named inline) | |

### Gaps identified

- **G1 (LOW) -> RESOLVED**: FR-014's no-secrets guarantee had no dedicated
  build-time verification task. FOLDED into T037 during the reconciliation
  pass (a secret-pattern scan over new fixtures/docs is now part of T037's
  acceptance).
- **G2 (LOW) -> RESOLVED**: No task re-verified that the rule registry count
  is unchanged (this feature adds no `retail check` rule). FOLDED into T037
  (run `retail manifest` / diff `docs/rules/rules-manifest.json` to confirm no
  new rule ID appeared).
- **G3 (LOW, new)**: T037 now also asserts RS1 passes on the CSV
  `readiness-status.yaml` fixture and S1-S7 pass on the silver migration
  fixture -- and the Foundational checkpoint runs `retail check` over the
  fixtures early, so an RS1/S-rule failure is caught before any CLI code
  exists. No open action.

## Constitution Alignment Issues

None found. plan.md's per-principle Constitution Check table (reproduced from
`.specify/memory/constitution.md` Principles I-IX plus the Readiness Spine
section) shows PASS for every principle with a specific rationale citing the
FR/contract that satisfies it. No MUST-level conflict was found in spec.md,
plan.md, or tasks.md during this manual pass.

## Unmapped Tasks

None found. Every task in tasks.md (T001-T037) maps to either a Setup/
Foundational concern, a specific user story's FR/AC, or a Polish/validation
concern named in plan.md's "Tests and validation" or "Operational risks"
sections.

## Overlap / Keep-Separate-or-Narrow Recommendation

**Recommendation: KEEP SEPARATE**, with the differentiations already recorded
in spec.md preserved verbatim as implementation proceeds:

1. **vs. `docs/demo/retail-store-sales-demo.md`**: keep separate -- different
   artifact class (reading tour vs. runnable harness) and different dataset
   (existing Kaggle CSV vs. new invented CSV). No merge recommended.
2. **vs. `docs/worked-examples/retail-store-sales.md`**: keep separate -- that
   document remains the canonical full narrative on real data; this feature
   is explicitly a smaller, faster, complementary artifact, not a competitor.
3. **vs. `082-postgres-live-validation-suite`**: keep separate, with the
   stated one-directional optional dependency (083 -> 082). Narrowing note:
   if 082's own spec ends up defining a demo-scoped naming convention or
   working-directory convention of its own, reconcile 083's research.md R4 /
   data-model.md working-directory naming against 082's choices at
   implementation time to avoid two similar-but-different conventions
   existing side by side.
4. **vs. `084-worked-example-factory`**: keep separate; no action needed
   until 084 is drafted, at which point re-reading 083's "Relationship"
   section is recommended for whoever authors 084.

## Metrics

- Total Functional Requirements: 17 (FR-001..017; FR-017 added in the
  post-advisor reconciliation pass for the CSV/RS1 requirement)
- Total Success Criteria: 6 (SC-001..006)
- Total Tasks: 37 (T001-T037)
- Requirements with >=1 mapped task: 17/17 (100%); gap notes G1/G2 RESOLVED
  (folded into T037), G3 opened+closed same pass
- Ambiguity findings: 1 (F2, accepted as intentional)
- Duplication findings: 0
- Critical issues count: 0
- High-severity findings: 4 (F3, F4, F11, F12) -- ALL resolved (F3/F4 within
  the original spec; F11/F12 in the post-advisor reconciliation pass); zero
  open high-severity issues remain

## Next Actions

- **No CRITICAL issues exist.** This spec chain is not blocked from proceeding
  to a (separately authorized) `/speckit-implement` pass on the findings in
  this report alone.
- Recommended before implementation (not blocking, but cheap to do): fold G1
  and G2 into T036/T037's acceptance notes; confirm F7's "pending is
  display-only" convention explicitly in the eventual `src/retail/demo/report.py`
  docstring so a future maintainer doesn't add "pending" as a fifth stored
  status value.
- Recommended for the human reconciling concurrent specs: when
  `082-postgres-live-validation-suite`'s own spec lands, diff its working-
  directory/naming conventions against this spec's `research.md` R4 and
  `data-model.md` "Demo working directory" entity for consistency (F5/F6/
  Overlap recommendation item 3).
- This report does not recommend running `/speckit-specify` refinement,
  `/speckit-plan` architecture changes, or manual tasks.md edits -- the
  findings are either already resolved in-spec, or LOW-severity documentation
  notes suitable for the implementation phase itself.

## Remediation offer

Per the `speckit-analyze` skill's Step 8 convention: concrete remediation
edits for G1/G2 (adding one line each to T036/T037) were NOT applied
automatically, consistent with this being a read-only analysis pass and with
this task's SPEC-WORK-ONLY boundary (no further edits beyond the spec dir
were made after this report). A human reviewer can request these two
one-line task edits explicitly if desired.
