# Cross-Artifact Analysis: Cross-Star Conformed-Dimension Readiness Gate (087)

**Feature**: `087-conformed-dimension-readiness` | **Date**: 2026-07-04
**Stage**: ANALYZE (read-only). Scope: `spec.md`, `plan.md`, `tasks.md`,
`research.md`, `data-model.md`, `quickstart.md` in this feature directory.
No file other than this one was edited to produce this report.

**Precondition**: spec.md, plan.md, tasks.md are all present (Draft status;
not ratified, not implemented -- `docs/quality/conformed-dimension-map.yaml`
and `src/retail/rules/rule_hr1.py` both confirmed absent from the live tree
at analysis time). An adversarial `plan-review.md` already exists for this
feature (verdict PASS-WITH-NOTES) and is treated as a companion artifact, not
a substitute for this analyze pass -- its five-axis adversarial shape is
different from the coverage/consistency shape below, and it explicitly notes
`analysis.md` did not yet exist. Ground-truth facts it verified (live rule
count 55, both committed stars' `gold_star` shapes, HR/HR1 freedom from
collision) were independently re-verified against the live tree during this
pass and are consistent.

---

## A. Requirement Coverage

Every functional requirement and success criterion mapped to its covering
task(s)/artifact(s). Status legend: **OK** = covered by 1+ concrete task or
artifact; **DEFERRED** = requirement's own text authorizes a partial/pending
implementation and the deferral is itself tracked; **GAP** = no covering
task/artifact found.

### Functional Requirements

| FR | Requirement (summary) | Covering task/artifact | Status |
|---|---|---|---|
| FR-001 | Model-level tier orthogonal to 7-stage spine; no 8th stage; no readiness-status.yaml key | T004 (confirm no-edit); plan.md Project Structure | OK |
| FR-002 | New human-authored conformed-dimension-map.yaml; mirrors SF1 shape; rule never writes it | T003 (author scaffold); T020 (read-only load); data-model.md ConformedDeclaration | OK |
| FR-003 | Exactly one @register-ed static rule, id HR1, reads only committed files, no DB/live/adapter | T001, T005 (stub check_hr1) | OK |
| FR-004 | Discover lookup dims via dimensions[] + date_dimension block (both forms); exclude degenerate_dimensions[]; no new source-map.yaml key | T017, T018, T019 | OK |
| FR-005 | Conformed-dim comparison: grain (natural key), key (surrogate_key), type (shared-attribute silver type); divergence -> ERROR | T021 (key+type); T022 (grain marked PENDING SCHEMA PREREQUISITE); T013/T014/T016 tests | **DEFERRED** (grain limb; see finding F1) |
| FR-006 | Undeclared same-name collision across 2+ stars -> ERROR | T032; T024 fixture/test | OK |
| FR-007 | Zero/one star -> no-op, no declaration demanded | T030 (2+-star gate), T037 (short-circuit); T034/T035 tests | OK |
| FR-008 | distinct declaration permits divergence, no ERROR | T032; T026 fixture/test | OK |
| FR-009 | Stale entry (fewer than 2 surviving stars, or named star lacking the dim) -> WARNING; moot-distinct -> WARNING | T041; T039/T040 fixtures/tests | OK (see finding F2 on the moot-distinct definition under graceful degradation) |
| FR-010 | Missing/unparseable manifest (2+ stars) -> ERROR; malformed entry (bad enum, unresolvable star) -> ERROR | T030 (missing/unparseable), T031 (malformed entry); T027/T028 fixtures | OK |
| FR-011 | No auto-merge/rewrite of dims or source-map.yaml; no authoring/editing the manifest by the rule; no self-grant of model-level pass | T043 (mechanical no-write source-inspection test); FR-002/FR-003 design | OK |
| FR-012 | No numeric confidence/health/maturity/conformance score; no completeness count or N-of-M/percent tally | T043 (mechanical grep for numeric formatting in messages) | OK |
| FR-013 | Rule + template stay generic; dim_product/dim_store/dim_date illustrative only; no C086/worked-example specifics baked in | T003 (illustrative scaffold), T044 (grep verification) | OK |
| FR-014 | Six-surface wiring lockstep in the same commit | T006-T012 | OK |
| FR-015 | ASCII, UTF-8 no BOM, short repo-relative paths | T003 (explicit); applies to every new file per tasks.md note | OK |
| FR-016 | OPEN -- Q-APPROVAL-SEAM (owner ruling required); PENDING DEFAULT = mechanical, no approvals[] shape invented | T048 (record OPEN, explicitly "do not answer") | OK (correctly left open -- see Constitution section, Principle V) |

### Success Criteria

| SC | Outcome | Covering task/artifact | Status |
|---|---|---|---|
| SC-001 | Human-authored map covering every shared name, all genuinely agreeing -> zero ERROR Findings | T046 (full local gate run) | OK |
| SC-002 | Second star with divergent shared dim (grain/key/type) -> ERROR, mutation-verified | T023 (mutation-verify re-run) | **PARTIAL** re: grain (grain limb not implemented this feature; key+type are mutation-verified per T023) -- see F1 |
| SC-003 | Same-named dim without declaration -> ERROR; declaring distinct clears it | T033 (mutation-verify: remove distinct, confirm ERROR reappears) | OK |
| SC-004 | Zero/one star -> no Finding regardless of map contents | T038 | OK |
| SC-005 | No numeric score; no write to any source-map.yaml/manifest/dimension | T043 | OK |
| SC-006 | Zero C086/pharmacy-specific names in generic artifacts | T044 | OK |
| SC-007 | Wiring + rule-count lockstep stays green | T012, T047 | OK |

**Coverage summary**: 16/16 FRs and 7/7 SCs have an identified covering
task or artifact. One requirement (FR-005's grain limb, propagating to
SC-002) is explicitly and consistently marked DEFERRED across every
artifact that touches it (spec Clarifications C3, plan.md Summary,
research.md, data-model.md Finding taxonomy row, tasks.md T022) rather than
silently dropped -- this is a coherence strength, not a hidden gap, but it
is recorded here as a partial-coverage item per the letter of FR-005/SC-002.

---

## B. Success-Criteria Testability

| SC | Testable as written? | Notes |
|---|---|---|
| SC-001 | Yes | "zero ERROR Findings" is a mechanically countable assertion against a concrete gate run (T046). |
| SC-002 | Yes, for key/type; N/A for grain | Mutation-verify (flip value, confirm Finding appears/disappears) is mechanical and already the repo's SF1/AP1 discipline. The grain clause of SC-002's own text ("diverges ... on grain, key, or a shared attribute's type") is not exercisable this feature since the grain limb does not exist yet -- the criterion's wording was not narrowed to match FR-005's deferral (see F1). |
| SC-003 | Yes | Same mutation-verify pattern (T033), mechanical. |
| SC-004 | Yes | Boolean count assertion across two concrete fixture states (T038). |
| SC-005 | Yes | Mechanically verified by source-inspection/grep (T043), stronger than a review-only claim. |
| SC-006 | Yes | Mechanically verified by grep (T044). |
| SC-007 | Yes | Mechanical: existing wiring-meta-gate + rule-count-claims tests (T012, T047) already assert this shape for every other rule addition. |

All seven success criteria are measurable and testable as written; none
depend on a subjective judgment call at verification time. The one
wording gap is SC-002 still naming "grain" as one of three divergence
axes it claims to mutation-verify, while FR-005/T022 defer the grain axis
entirely -- see Finding F1.

---

## C. Terminology Consistency

- "Star", "conformed", "distinct", "GoldDimension", "ConformedDeclaration",
  "ConformanceFinding" are used identically across spec.md, data-model.md,
  research.md, and tasks.md -- no synonym drift detected.
- Rule id "HR1" and artifact path docs/quality/conformed-dimension-map.yaml
  are stable across all six files and match the collision-avoidance
  allocation given in the task prompt verbatim.
- "Grain" is used consistently to mean "the natural-key attribute" of a
  dimension (spec FR-005, research.md C3, data-model.md), not conflated with
  a fact table's grain -- worth a reader's care but not an artifact-internal
  inconsistency.
- Severity posture ("ERROR" for proven breaches, "WARNING" for
  stale/moot) is stated once in spec.md Assumptions and then applied
  identically in data-model.md's Finding taxonomy table and tasks.md's
  fixture/test tasks -- no contradictory severity assignment found for any
  of the 12 taxonomy rows.
- Minor terminology gap (see F3): "identity string" for a star is
  defined in data-model.md as either meta.table_id or source_id
  depending on form, but no artifact states which literal string a human
  author must write into the manifest's stars: list for a rich-form vs.
  compact-form table.

---

## D. Constitution Alignment

| Principle | Alignment check | Verdict |
|---|---|---|
| **I. Agent-First, Gate-Enforced** | HR1 fails CLOSED (non-zero exit) on divergence/undeclared-collision/missing-manifest; no advisory-only mode for these three cases (FR-005/006/010; plan.md Constitution Check row I). Compliance demonstrable by running `retail check` (quickstart.md steps 1, 3, 5). | Satisfied |
| **III. Medallion/Gold-Only** | HR1 is the first enforced gate for Principle III's "conformed" clause; reads only the committed gold_star block, never Postgres or Power BI (plan.md row III). | Satisfied |
| **IV. Source-Mapping-Before-Silver** | HR1 writes no silver.* SQL and does not gate it; reads source-map.yaml strictly as a downstream consumer after that table's own Mapping Ready review (plan.md row IV, spec Assumptions). | Satisfied |
| **V. Agent-Stops-at-Judgment** | The conformed vs. distinct ruling is explicitly human-authored (FR-002, FR-011); an undeclared collision is never inferred conformed-by-default (FR-006) -- it is a fail-closed ERROR demanding a human ruling. FR-016 (Q-APPROVAL-SEAM) is correctly left OPEN rather than silently answered; T048 explicitly instructs "do not answer." This is the one place a reviewer must check closely for a disguised self-grant: T002/T003 have the agent author an EMPTY dimensions: {} scaffold that is what lands `retail check` green under FR-010. Traced through research.md's "Landing precondition" and independently re-verified in this pass (direct grep of both committed source-map.yaml files): the two committed stars share zero dimension names today (dim_product vs. gold.dim_product_rss), so there is genuinely nothing to adjudicate and no Principle-V ruling is bypassed by the scaffold. The green is earned, not manufactured. | Satisfied (verified, not merely asserted) |
| **VI. Defaults-Then-Deviations** | Clarify-session defaults C1/C2/C4 are recorded as reversible, constitution-safe defaults per Principle VI; C3 (grain signal) is correctly NOT defaulted because no safe default exists in the schema (deferred, not decided) -- research.md explicitly tested and rejected two heuristics before deferring. | Satisfied |
| **VII. C086-is-an-example** | dim_product/dim_store/dim_date are illustrative only in the rule design and the manifest template (FR-013); T044 is a dedicated grep-verification task. research.md's own prose cites the real gold.dim_product_rss / dim_product names as part of its precedent-survey analysis, not baked into rule logic or the template. | Satisfied |
| **VIII. Static-First/Live-Deferred** | HR1 reads only ctx.tracked_files; yaml is imported lazily to stay out of the stdlib-only static-core chain (mirrors SF1); live cross-star data reconciliation is explicitly named OUT of scope and deferred to a future `retail validate` surface. The grain limb is authored PENDING (T022 code comment) rather than silently dropped or faked with an unenforced heuristic. | Satisfied |
| **IX. Secrets/Reproducibility** | No connection string or credential touched anywhere; all new artifacts specified as ASCII, UTF-8 no BOM, short repo-relative paths (FR-015; plan.md row IX). | Satisfied |
| **Hard rule #9** | No numeric confidence/health/maturity/conformance score anywhere in the ConformanceFinding usage; FR-012 explicit; T043 is a MECHANICAL grep test (not just a docstring promise) for percentage/ratio/N-of-M formatting in emitted messages. The one integer in the whole feature (rule count 55->56) is the same len() mechanism every other rule addition uses, not a conformance score. | Satisfied |

**SCOPE GUARD verification** (task-prompt non-negotiables, independent of
the Constitution table above):

- MUST NOT auto-merge dims -- confirmed absent from every artifact; FR-011
  is explicit and T043 mechanically tests for the absence of any write.
- MUST NOT self-grant the model-level pass -- confirmed; FR-011, FR-016,
  and T048 all reinforce that HR1 emits Findings only and records no
  model-level pass anywhere (no approvals[] shape, no new
  readiness-status.yaml key).
- MUST NOT emit a numeric conformance score (hard rule #9) -- confirmed;
  see table row above.
- Static-only (Principle VIII) -- confirmed; see table row above.

All four SCOPE GUARD items hold across every artifact read. **No
constitution violation found.**

**Open Principle-V item (not a violation -- a correctly-raised judgment
call)**: FR-016 / Q-APPROVAL-SEAM remains genuinely OPEN for a named-human
owner ruling on whether the model-level conformed tier needs its own
approval seam. The spec, plan, research, and tasks all treat this
consistently as unanswered-by-design. This is reported under
open_principle_v in the structured output, not as a scope violation.

---

## E. Contradiction / Duplication / Ambiguity Scan

No direct contradictions were found between any two artifacts. The
following findings are genuine gaps or ambiguities, ranked by severity.

### F1 -- SC-002 wording not narrowed to match FR-005's grain deferral (LOW)

**Where**: spec.md SC-002 ("Introducing a second star whose shared
dimension diverges from the first on grain, key, or a shared attribute's
type causes HR1 to ERROR (mutation-verified)...") vs. spec.md FR-005's own
DEFERRED-TO-PLAN clause and plan.md/research.md/tasks.md T022, all of
which mark the grain limb PENDING SCHEMA PREREQUISITE and explicitly
scope this feature to key + type only.

**Impact**: A reader of SC-002 alone would expect grain-divergence
mutation-testing to be part of this feature's acceptance bar. Tasks.md
correctly does NOT attempt to satisfy the grain clause (T022 is a marker
comment, not an implementation), so there is no functional gap -- but
SC-002's literal text still promises a three-axis mutation-verified
outcome that only two axes (key, type) actually ship.

**Severity**: LOW. Recommend narrowing SC-002's wording to name only key
and type, or adding a parenthetical pointing to C3.

### F2 -- "Moot distinct" undefined under graceful degradation for a mixed rich/compact pair (LOW)

**Where**: data-model.md Finding taxonomy ("Moot distinct entry ... a
distinct entry whose stars have become identical in shape") vs.
data-model.md's own "Graceful degradation rule" (compare only fields
present on BOTH sides of a pair; an absent field is excluded from
comparison, never a divergence).

**Impact**: For a distinct-declared pair spanning one rich-form star and
one compact-form star, the only field genuinely comparable on both sides
is the dimension name itself. No artifact states whether "identical in
shape" for the moot-WARNING trigger means (a) all comparable fields
happen to agree (vacuously true whenever nothing is comparable), or (b)
requires at least one limb was actually comparable and agreed.

**Severity**: LOW. Affects only the WARNING-level moot-distinct case;
not live on the current tree. Recommend the implementer resolve it
explicitly in rule_hr1.py and record the choice in a code comment.

### F3 -- Star "identity string" convention for the manifest's stars: list is underspecified (LOW-MEDIUM)

**Where**: data-model.md Star entity ("Identity: meta.table_id (rich
form) or source_id (compact form) -- either serves as the star's
identity string ... for the manifest's stars: list.") vs. the
illustrative manifest examples elsewhere.

**Impact**: The two committed source-map.yaml instances use two
DIFFERENT identity conventions (retail_store_sales is rich-form;
demo_sample_orders is compact-form, identified by its directory name). A
human authoring a real conformed-dimension-map.yaml entry has no
documented rule for which literal string to write for a given table, and
no artifact specifies whether HR1's matching logic normalizes both forms
to a single canonical identity. This could produce a confusing FR-010
false-positive/false-negative at authoring time.

**Severity**: LOW-MEDIUM. Does not violate any constitution principle
and does not affect the current empty-manifest landing. Recommend
pinning down a single canonical identity-resolution rule and stating it
once in data-model.md.

### No duplication found

No two artifacts restate the same requirement with materially different
wording that could drift out of sync. No overlapping rule ids, artifact
paths, or wiring-surface edits were found between this feature's file
footprint and any neighboring shipped feature (SF1, Gold Ready,
source-mapping gate).

---

## F. Deferred-Capability Leakage Scan

Checked every artifact for an assumption that F016 (Power BI execution
adapter) or a live database surface already exists.

| Artifact | F016 assumed? | Live DB assumed? | Notes |
|---|---|---|---|
| spec.md | No | No | Explicitly static-only; live cross-star data reconciliation named as future/deferred scope. |
| plan.md | No | No | Technical Context: "Storage: N/A -- no database, no live connection." |
| tasks.md | No | No | Every task reads/writes committed text files or runs pytest/`retail check`/`retail kit-lint`. |
| research.md | No | No | "Deferred capabilities NOT assumed" section explicitly names F016 and live `retail validate` reconciliation. |
| data-model.md | No | No | "Non-goals" section: "No live/materialized-data shape." |
| quickstart.md | No | No | Step 8 is an explicit walkthrough assertion that no DB connection, Power BI Desktop session, or network access is required. |

**Verdict**: No leakage found. Every artifact that touches the
live/deferred boundary does so by explicitly naming what is deferred and
why, not by silently assuming a capability that does not yet exist. The
grain limb (C3) is marked PENDING SCHEMA PREREQUISITE in both prose and
code-comment form and deferred as a cross-feature prerequisite -- the
correct posture, not a leak.

---

## Summary

- **Requirement coverage**: 16/16 FRs, 7/7 SCs mapped to covering
  task/artifact; one requirement (FR-005 grain limb / SC-002) is
  explicitly and consistently DEFERRED rather than silently gapped.
- **Success-criteria testability**: all seven are mechanically testable as
  written; one (SC-002) has wording not narrowed to its own feature's
  scope reduction (F1, LOW).
- **Terminology**: consistent across all six artifacts; one underspecified
  convention (star identity string for manifest authoring, F3, LOW-MEDIUM).
- **Constitution alignment**: Principles I, III, IV, V, VI, VII, VIII, IX
  and hard rule #9 all satisfied; the one Principle-V item (FR-016) is
  correctly left OPEN, not silently resolved.
- **Contradictions/duplication**: none found. **Ambiguities**: three (F1,
  F2, F3), all LOW or LOW-MEDIUM, none blocking, none touching the SCOPE
  GUARD or hard rule #9.
- **Deferred-capability leakage**: none. F016 and live DB are consistently
  named as NOT existing and NOT invoked across every artifact.

**Findings ranked by severity**: F3 (LOW-MEDIUM) > F1 (LOW) = F2 (LOW).
No CRITICAL or HIGH finding. No constitution violation. This feature's
artifact set is internally consistent and ready to proceed to
implementation planning review, subject to the non-blocking
recommendations in F1-F3 and the standing OPEN owner ruling on FR-016.