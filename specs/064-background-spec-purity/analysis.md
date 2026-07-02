# Cross-Artifact Analysis: Background-Spec Forbidden-Dynamic-Content Assertion Rule

**Feature**: 064-background-spec-purity
**Date**: 2026-07-02
**Scope**: Read-only consistency pass over spec.md, plan.md, tasks.md (with
research.md, data-model.md, contracts/rule-contract.md, quickstart.md as support).

## Method

Cross-checked: (1) every FR has coverage in a task and, where behavioral, a
contract row; (2) every user story maps to a task phase; (3) every success
criterion maps to a checkable test; (4) terminology is consistent across
artifacts; (5) constitution gate is evaluated; (6) no duplicate or conflicting
requirements; (7) no artifact assumes a deferred capability.

## Requirements coverage (spec FR -> contract row -> task)

| FR | Contract row(s) | Task(s) | Status |
|----|-----------------|---------|--------|
| FR-001 assert declared boolean contract | C5, C10 | T003, T008, T012 | covered |
| FR-002 generic discovery + template exempt | C1, C2 | T003, T016 | covered |
| FR-003 ERROR + file/pointer locator | C5 | T007, T008 | covered |
| FR-004 one finding per violation | C6 | T005, T007, T008 | covered |
| FR-005 categorical, no image, no adequacy judging | C7, C11 | T012, T016 | covered |
| FR-006 compliant/reasoned -> zero | C7, C11 | T009, T010, T011, T012 | covered |
| FR-007 generic vocabulary, no tenant literal | C13 | T003, T023 | covered |
| FR-008 fail closed on violation | C5 | T008, T022 | covered |
| FR-009 unparseable YAML -> finding, no crash | C12 | T014, T015, T016 | covered |
| FR-010 fixture exemption | C3 | T002, T015, T016 | covered |
| FR-011 inert on empty corpus | C4 | T015, T016, T022 | covered |
| FR-012 no execution; lazy in-function yaml import | (invariant) | T008, T023 | covered |
| FR-013 fresh non-colliding id, observed severity | (registration) | T001, T018, T020 | covered |
| FR-014 five-place wiring, drift fails closed | (registration) | T017-T020, T021 | covered |
| FR-015 no score, no self-granted readiness, no stage | (invariant) | T012, T016, T023 | covered |
| FR-016 vocabulary/parse/convention/severity settled | C8, C9, C11, C13 | T003, Phase 6 GATE | covered (convention literal OPEN by design) |

All non-deferred FRs are covered. The only OPEN item is the filled-spec
file-discovery CONVENTION literal (a Principle-V owner ruling), correctly
reflected as a wiring gate (Phase 6), not a planning-time gap. FR-016 is otherwise
fully settled in Clarifications Q1-Q4.

## User story coverage

- US1 (P1) -> Phase 3 (T004-T008). Covered; independently testable MVP.
- US2 (P1) -> Phase 4 (T009-T012). Covered.
- US3 (P2) -> Phase 5 (T013-T016). Covered.

## Success criteria coverage

| SC | Verified by |
|----|-------------|
| SC-001 true forbidden key -> ERROR + fail closed | C5 / T007-T008, T022 |
| SC-002 compliant filled spec -> zero false positives | C7, C11 / T011-T012 |
| SC-003 no filled spec on disk -> zero (green build) | C4 / T015-T016, T022 |
| SC-004 two true keys -> exactly two findings | C6 / T005, T007-T008 |
| SC-005 false+reason passes, false+no-reason fails | C10, C11 / T011-T012 |
| SC-006 new filled spec scanned, no code change; template never flagged | C1, C2, C13 / T014-T016 |
| SC-007 id in registry + goldens, wiring test passes | (registration) / T017-T021 |

All seven success criteria map to a checkable test.

## Terminology consistency

Consistent across artifacts: "filled background spec", "declared boolean
contract", "forbidden_dynamic_content" / "qa_checklist", "true-or-reason",
"file#/pointer locator", "discovery convention (suffix)", "lazy in-function yaml
import", "observed (not declared) severity", "test-fixture exemption path",
"inert on an empty corpus". No divergent synonyms that would confuse an
implementer. Rule id is deliberately referred to as "fresh design-lint-namespaced
id, finalized against the live registry at wiring time" everywhere (never a
hardcoded literal), which is correct.

## Constitution / gate

plan.md evaluates Principles I, II, V, VII, VIII, IX and ratified 044 with an
explicit PASS and rationale for each; no Complexity Tracking entries (no
violations). tasks.md carries a matching Principle-V gating note on Phase 6 for
the discovery convention. Consistent.

## Deferred-capability check

No artifact assumes F016 (Power BI Execution Adapter) or F031-F033 (spec-only
runtimes). The rule is stdlib-only over committed text (yaml lazily imported); it
explicitly does NOT open/render the image binary (image verification named OUT OF
SCOPE, not assumed present). Clean.

## Duplication / conflict check

No duplicate FRs. No conflicting requirements. Two tensions worth naming, neither
a contradiction:
- "the rule is plan-complete" vs "wiring MUST NOT be committed until the owner
  convention ruling" -- wiring is an implement-time step gated on the ruling; the
  planning artifacts are complete without it. Spec front-matter correctly stays
  Status: Draft.
- "inert on empty corpus (FR-011)" vs "asserts the declared contract (FR-001)" --
  not a conflict: with zero discovered filled specs there is nothing to assert, so
  zero findings is the correct behavior of the same rule; FR-011 defines the
  empty-set boundary of FR-001.

## Findings

| ID | Severity | Location | Finding | Recommended action |
|----|----------|----------|---------|--------------------|
| F1 | LOW | spec ## Clarifications OPEN item | The filled-spec file-discovery convention literal is OPEN (owner ruling). | INTENTIONAL Principle-V deferral, recorded OPEN and reflected as the Phase 6 wiring gate; the rule is inert until ruled. No action; do not auto-resolve. |
| F2 | LOW | T001 / research live-registry note | Possible EXPECTED_RULE_IDS vs decorator count drift on this branch (local 41 incl DL1 vs memory's 40 on main). | Reconcile against the TRUE live registry at wiring time (already an explicit task, T001). No spec change needed. |
| F3 | LOW | data-model.md reason-shape | The exact YAML shape carrying a qa "reason" (sibling key vs mapping value) is left to the rule contract, not frozen in the spec. | Acceptable: an implementation detail resolved in contracts/rule-contract.md at build time; the parse contract (reason PRESENCE, not adequacy) is fixed. No action. |

**Critical findings**: 0
**High findings**: 0
**Verdict**: clean (0 critical, 0 high). The three LOW items are by-design; each
is either an intentional Principle-V deferral with an owning gate/task or a
build-time detail, not a planning gap.
