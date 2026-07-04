# Specification Analysis Report: Returns/Refunds Fact Worked Example (096)

**Analyzed**: 2026-07-04 | **Artifacts**: spec.md, plan.md, tasks.md, research.md,
data-model.md, quickstart.md | **Mode**: read-only

Cross-artifact consistency + constitution-alignment analysis run after task generation.
This analysis modified no chain artifact (spec/plan/tasks/research/data-model/quickstart);
findings are recorded here as the analyze-stage output. Ground-truth claims in
research.md and data-model.md were independently re-verified against the current
worktree state (src/retail/rules/additivity_consistency.py, templates/metric-contract.yaml,
docs/decisions/0002-retail-cleaning-defaults.md, docs/readiness/readiness-model.md,
docs/worked-examples/retail-store-sales.md, specs/084-.../contracts/worked-example-completeness.md,
specs/087-conformed-dimension-readiness/), not merely assumed correct.

## Requirement Coverage

| FR | Covering task/artifact | Status |
|----|------------------------|--------|
| FR-001 (second worked example, new narrative + mapping dir) | T004, T020, T021 | OK |
| FR-002 (walk Stages 2-6, same gates/templates/RC defaults, no new rule/default/stage) | T008-T010, T014-T015, T019, T028 | OK (see F1 stage-range naming) |
| FR-003 (source data includes a real signed return row; synthetic dataset default) | T005 | OK |
| FR-004 (is_return from authoritative column, never sign; discrepancy surfaced) | T005d, T008, T010, T011 | OK |
| FR-005 (Return Value additive / Return Rate percent non-additive contracts, closed vocabulary) | T017, T018 | OK |
| FR-006 (rate not composed by direct SUM; AD1 legality) | T018, T029 | OK (see F3 SC-002 testability) |
| FR-007 (state primary date axis; cross-period worked figure) | T020 | OK |
| FR-008 (no invented VAT/exchange/period-close policy; OPEN or Assumption-with-citation) | T011, T020, T027 | OK |
| FR-009 (live-gated checks blocked with blocking_reasons, never fabricated pass) | T012, T016, T022, T025, T026 | OK |
| FR-010 (approval seams start/stay empty; no self-grant) | T013, T022, T025 | OK |
| FR-011 (no numeric score or N-of-M tally anywhere) | T006, T026, T030 | OK |
| FR-012 (note cross-star conformance question; never touch conformed-dimension-map.yaml) | T020, T033 | OK |
| FR-013 (reversible date-axis default for worked figures only; A3 stays OPEN) | T011, T020, T027 | OK |
| FR-014 (generic; no C086/client-specific fact) | T005, T010, T031 | OK |
| FR-015 (ASCII/UTF-8-no-BOM; Windows 260-char path budget) | T005, T032 | OK |
| FR-016 (satisfy 084 completeness contract, cited by path) | T034 | OK |

All 16 FRs have at least one covering task; all seven Key Entities (spec.md) have a
corresponding data-model.md section (Sec 1-7). No FR is an orphan. Reverse direction also
checked: no task in tasks.md introduces work traceable to zero FR (T035 itself is the
traceability self-check task, correctly citing "traceability gate" rather than an FR).

Success-criteria coverage: SC-001 to T017/T018 (contract statements); SC-002 to T028/T029;
SC-003 to T020; SC-004 to T008 (source-map); SC-005 to T026; SC-006 to T025/T026;
SC-007 to T031/T033. All seven SCs have at least one verification task.

## Success-Criteria Testability

| SC | Testable as written? | Note |
|----|----------------------|------|
| SC-001 | Yes | Direct side-by-side text read of two YAML files against returns-rate-value.md. |
| SC-002 | Weakly, see F3 | The stated check (retail check's AD1 rule produces zero new ERROR findings) is true by construction and non-discriminating: research.md Sec 1 row 7 and quickstart.md Step 3 both confirm AD1's corpus regex reads only skills/retail-kpi-knowledge/contracts/*.md, never mappings/*/metrics/*.yaml. Running retail check cannot fail this SC regardless of whether the two new contracts are AD1-legal. T029 already concedes this and substitutes a manual composition-legality review, but SC-002's own wording still names the automated rule as the test. |
| SC-003 | Yes | At least one worked reconciliation figure sourced from committed data is a concrete, gradeable artifact check (T020). |
| SC-004 | Yes | Direct read of source-map.yaml's classification-column derivation. |
| SC-005 | Yes | Direct read of readiness-status.yaml; binary per-stage check. |
| SC-006 | Yes | Direct read of approvals list; binary. |
| SC-007 | Yes | Grep-based (C086 token; conformed-dimension-map.yaml diff). |

## Terminology Consistency

- Table-name placeholder: the returns-example token (spec.md/plan.md/data-model.md/quickstart.md)
  vs. rr (tasks.md) vs. ReturnsExample (PascalCase, for the PBIP model dir). All three
  are declared as the same placeholder resolved to one fixed name at build time (tasks.md
  "Table-name placeholder" section, plan.md Project Structure). Consistent by design, not a
  drift; flagged only so a build-time reader does not mistake them for three different
  entities.
- "Worked example" vs. mapped-but-undocumented table: demo_sample_orders is cited
  (spec.md FR-012, Edge Cases; research.md Sec 2) only as a table whose dimension names
  might collide; it is a real committed mappings/demo_sample_orders/ directory but has no
  narrative doc and no docs/worked-examples/README.md row, unlike retail_store_sales.
  The spec never calls it a worked example, so this is accurate as written, not a defect;
  noted here only because the two neighbouring tables (retail_store_sales,
  demo_sample_orders) are easy to conflate as "the two other worked examples" on a fast
  read.
- Stage-range naming: see F1 below (the one real terminology inconsistency found).

## Constitution Alignment

- Principle I (Agent-First/Gate-Enforced): satisfied. No task weakens or bypasses
  retail check; T028 requires an actual exit-0 run with an unchanged rule count, not an
  assumed pass.
- Principle III (Medallion/Gold-Only): satisfied. T017/T018's binds_to.gold_table
  points only at the new gold star (T015); no contract binds to silver/bronze.
- Principle IV (Source-Mapping-Before-Silver): satisfied and explicitly enforced as a
  cross-phase ordering constraint (tasks.md Scope guard + Dependencies section): Phase 3
  (US2, source-map) is a hard prerequisite for Phase 4 (US1, silver/gold migrations),
  overriding the spec's narrative US1/US2 numbering. This is the correct precedence and is
  stated clearly enough that an implementer cannot miss it.
- Principle V (Agent-Stops-at-Judgment): satisfied, and unusually well-covered for a
  worked-example feature. Four distinct judgment calls are correctly left open rather than
  resolved by the agent: (a) VAT/tax treatment of refunds (FR-008/Q2), no default,
  explicit OPEN owner ruling, SCOPE GUARD-cited; (b) the operative reporting date axis,
  sale-date vs. return-date, KPI ambiguity A3 (FR-013/Q1b), explicitly split from the
  Principle-VI default that governs only the example's own synthetic arithmetic
  (see below); (c) cross-star conformed-dimension declaration (FR-012, spec 087/HR1),
  noted in prose only, conformed-dimension-map.yaml never touched; (d) named-human
  approvals at Mapping Ready and Semantic Model Ready (FR-010), approvals list designed to
  start and stay empty, never self-granted. All four are the correct disposition (raise and
  stop), not a silently invented answer.
- Principle V/VI boundary on FR-013 specifically: this is the sharpest judgment-call
  line in the spec and it is drawn correctly. FR-013 adopts a Principle-VI reversible
  default (return date equals the fact's own transaction date) for the worked figures only,
  and the spec's own bracketed text plus tasks.md's "Principle-V carve-out" section and T027
  both explicitly bar that default from being cited as having resolved A3 (the business's
  actual operative reporting axis). This is a default-then-deviation move (Principle VI)
  layered correctly on top of a genuine open ruling (Principle V), not a conflation of
  the two, and not a violation.
- Principle VII (C086-is-an-example-not-the-schema): satisfied. FR-014/SC-007 and T031
  require a generic-token scan; data-model.md's shapes contain no filled client content.
- Principle VIII (Static-First/Live-Deferred): satisfied. FR-009, T016, T022, T025,
  T026 all require blocked plus blocking_reasons for every live-gated check; research.md
  Sec 4 and quickstart.md both state no live DB and no F016 is assumed anywhere.
- Principle IX (Secrets/Reproducibility): satisfied. FR-015/T032 requires ASCII,
  UTF-8-without-BOM, short paths; T019 requires a parameterized Power BI connection, no
  baked-in host/DSN.
- Hard rule number 9 (no fabricated confidence/health/maturity score): satisfied. FR-011,
  T006, T026, T030 all require zero score/confidence/health/maturity/N-of-M fields;
  data-model.md Sec 8 explicitly states readiness is expressed only via the four-status
  model plus evidence plus blocking_reasons.
- No violation found. All nine Principles and hard rule number 9 are addressed with a
  concrete task, not merely asserted in prose.

## Contradiction / Duplication / Ambiguity Scan

- F1 (MEDIUM, Inconsistency): spec.md FR-002 ("The example MUST walk readiness
  Stages 2 through 6, Mapping Ready through Semantic Model Ready") and plan.md Summary
  ("Stages 2-6, Mapping Ready through Semantic Model Ready") both misname the Stage-6
  endpoint. Per docs/readiness/readiness-model.md lines 33-39, the seven stages are
  numbered: 1 Source Ready, 2 Mapping Ready, 3 Silver Ready, 4 Gold Ready, 5 Semantic
  Model Ready, 6 Dashboard Ready, 7 Publish Ready. Stage 6 is Dashboard Ready, not
  Semantic Model Ready (Stage 5). The numeric range "2-6" is consistent with the feature's
  actual scope (Phase 5/US3 and T023 do author Dashboard Ready's design/ artifacts, and
  the Overview lists design among Stages 2-6), but the parenthetical NAME attached to the
  range's end is off by one stage. tasks.md's own Phase 4 heading ("User Story 1, through
  Stages 2-6") repeats the numeric range without the wrong name, so tasks.md is not
  contradicted; only spec.md FR-002 and plan.md's Summary carry the mismatched label.
  Recommendation: change "Mapping Ready through Semantic Model Ready" to "Mapping Ready
  through Dashboard Ready" in both locations; no task or FR needs renumbering since the
  underlying scope (design artifacts through Dashboard Ready) is already correct.
- F2 (MEDIUM, Factual/documentation accuracy, not a design defect): research.md Sec 2
  row 4 and Sec 5 both state spec 087 "is spec-only (spec.md plus research.md only, no
  plan/tasks/contracts)." As of this analysis, specs/087-conformed-dimension-readiness/
  actually contains plan.md, data-model.md, quickstart.md, tasks.md, and
  plan-review.md in addition to spec.md/research.md; 087 has advanced past
  spec-only in this worktree. The load-bearing conclusion this feature's FR-012 design
  depends on (that the HR1 rule is not implemented in src/retail/rules/ and that
  docs/quality/conformed-dimension-map.yaml does not exist on disk) was independently
  re-verified in this analysis pass and is still true, so FR-012's design (note the
  question in prose, never author the map file) is not broken by this. The defect is
  research.md's supporting citation being stale about 087's spec-kit stage, not
  the operative constitution-facing conclusion. Recommendation: correct research.md Sec 2
  row 4 and Sec 5 to say that 087's rule (HR1) is not yet implemented in
  src/retail/rules/ and docs/quality/conformed-dimension-map.yaml does not exist,
  regardless of 087's own spec-kit stage, rather than asserting a specific (and here,
  wrong) spec-kit stage for a sibling feature this feature does not own.
- F3 (LOW, Success-criteria testability, see table above): SC-002 names retail
  check's AD1 rule as the test, but the same research.md/quickstart.md that grounds this
  feature's design already establish that AD1's read glob excludes
  mappings/*/metrics/*.yaml entirely, making the automated check vacuously pass regardless
  of the two new contracts' actual legality. T029 correctly compensates by requiring a
  manual composition-legality review, but SC-002 itself is not amended to say so. Not a
  contradiction (T029's manual review is real work, not skipped), but a reader could believe
  SC-002 is machine-verified when it is not. Recommendation: reword SC-002 to state
  explicitly that the zero-new-ERROR-findings guarantee holds by
  construction because AD1 does not read this path, and that the substantive check is
  T029's manual review against the AD1 legality table.
- No duplication found between spec.md/plan.md/data-model.md's descriptions of the two
  metric contracts (Sec 3/4 of data-model.md and FR-005/FR-006 of spec.md are
  complementary, not restated redundantly; data-model.md gives the YAML shape, spec.md
  gives the acceptance-testable behavior).
- No unresolved placeholder (TODO, TKTK, question marks) found in any of the six artifacts;
  every placeholder-style token is an intentional build-time fill-in, consistently
  flagged as such (e.g. data-model.md Sec 3-4, tasks.md T001's rr note).
- No conflicting requirement found (e.g. no FR contradicts another FR's scope
  boundary); the Boundary section (spec.md) and the tasks.md Scope-guard section restate
  the same four boundaries (084, 068/AD1, 087/HR1, retail-store-sales.md) consistently
  across both files.

## Deferred-Capability Leakage Scan (F016 / live DB)

Checked every artifact for an assumption that F016 (Power BI execution adapter) or a live
DB connection already exists or will be invoked during this feature's own authoring:

- spec.md US3, FR-009, Edge Cases: explicitly states F016 does not exist and every
  live-gated check must show blocked. No leakage.
- plan.md Technical Context / Constitution Check (Principle VIII row): explicitly states
  no live DB and no F016 are assumed available. No leakage.
- research.md Sec 4 (Deferred capabilities NOT assumed): explicitly enumerates F016 and
  live-DB non-availability. No leakage.
- data-model.md Sec 8: readiness-status shape requires blocked for any live-gated stage.
  No leakage.
- quickstart.md: every one of its 8 steps is prefixed with a statement that no live database
  connection or F016 is required, and Step 3/6 explicitly re-state this. No leakage.
- tasks.md: T016, T019, T022, T025, T026 all explicitly assign blocked (never pass) to
  every live-gated stage and explicitly state the TMDL model (T019) is not opened in Power
  BI Desktop, not connected live. No task invokes retail validate (the live-DB command)
  or references opening Power BI Desktop as something this feature's authoring performs.

Result: no leakage found. All six artifacts consistently treat F016 and live-DB access
as unavailable and require blocked or PENDING LIVE PROFILE rather than a fabricated
pass, matching Principle VIII and FR-009/FR-011.

## Findings Summary

| ID | Category | Severity | Location(s) | Summary |
|----|----------|----------|-------------|---------|
| F1 | Inconsistency | MEDIUM | spec.md FR-002 (line approx 262); plan.md Summary (line approx 16) | Stages 2-6, Mapping Ready through Semantic Model Ready, misnames the Stage-6 endpoint; per docs/readiness/readiness-model.md, Stage 5 is Semantic Model Ready and Stage 6 is Dashboard Ready. The numeric range is correct; the name is off by one stage. |
| F2 | Documentation accuracy | MEDIUM | research.md Sec 2 row 4, Sec 5 | Claims spec 087 is spec-only (spec.md plus research.md only); the worktree's specs/087-conformed-dimension-readiness/ actually also has plan.md/tasks.md/data-model.md/quickstart.md/plan-review.md. The operative conclusion this feature relies on (HR1 rule and map file absent from the codebase) was independently re-verified and still holds, so FR-012's design is not broken; only the supporting citation about 087's own spec-kit progress is stale. |
| F3 | Success-criteria testability | LOW | spec.md SC-002 | Names retail check's AD1 rule as the test, but AD1's corpus regex never reads mappings/*/metrics/*.yaml (confirmed in src/retail/rules/additivity_consistency.py), so the automated check is vacuously satisfied regardless of the contracts' actual legality. T029 substitutes a manual review, but SC-002's own wording does not disclose this. |

Critical/High findings: 0. Constitution violations: 0.

## Metrics

- Total functional requirements: 16 (FR-001 to FR-016), 16/16 covered (100 percent)
- Total success criteria: 7 (SC-001 to SC-007), 7/7 covered (100 percent); 6/7 cleanly
  testable, 1/7 (SC-002) testable-but-vacuous as worded (F3)
- Total tasks: 35 (T001 to T035)
- Findings: 3 total (0 CRITICAL, 0 HIGH, 2 MEDIUM, 1 LOW)
- Constitution violations: 0
- Deferred-capability (F016/live-DB) leakage instances: 0

## Next Actions

No CRITICAL or HIGH findings; no constitution violation. The spec/plan/tasks/research/
data-model/quickstart set is internally consistent and fully covered. The feature may
proceed to implementation as written. The two MEDIUM findings (F1, F2) are both
documentation-precision issues discoverable by a one-line edit each (F1: fix the Stage-6
label in spec.md FR-002 and plan.md Summary; F2: fix research.md's claim about 087's
spec-kit stage) and neither blocks a correct build, since the underlying scope (F1) and
underlying operative fact (F2) are both already right. The LOW finding (F3) is a
clarity-only reword of SC-002's wording; T029 already performs the correct substantive
check.

## Open Principle-V Items Carried Forward (not resolved by this analysis; compliance, not a gap)

The following are correctly left OPEN by spec.md/tasks.md and are re-confirmed, not
newly raised, by this analyze pass:

- VAT/tax treatment of a refund whose original sale carried tax (FR-008, Clarification Q2),
  OPEN owner ruling; SCOPE GUARD explicitly names this as owner-only.
- The operative reporting date axis, sale-date vs. return-date, KPI ambiguity A3
  (FR-013, Clarification Q1b), OPEN owner ruling, distinct from the Principle-VI
  reversible default used for the example's own synthetic worked figures.
- Cross-star conformed-dimension declaration if this example's dimensions share a name
  with retail_store_sales or demo_sample_orders (FR-012, spec 087/HR1), deferred
  to a named human via 087's not-yet-implemented mechanism; this feature only notes the
  question in prose.
- Named-human approvals at, at minimum, Mapping Ready and Semantic Model Ready (FR-010):
  the approvals list is designed to start and stay empty until a real named human signs;
  the authoring agent never self-grants.
