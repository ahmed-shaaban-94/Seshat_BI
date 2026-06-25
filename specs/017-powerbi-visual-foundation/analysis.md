# Cross-Artifact Analysis: Power BI Visual Foundation (F011A / 017)

**Date**: 2026-06-25 | **Scope**: spec.md, plan.md, tasks.md, checklists/requirements.md for feature 017-powerbi-visual-foundation
**Method**: `/speckit-analyze` detection passes (read-only). The Spec-Kit prerequisite script
(`check-prerequisites.ps1`) was NOT used: it enforces a feature-branch name and reads
`.specify/feature.json` (which still points at `004-retail-validate`), but this repo's
documented convention is to work on `main` and locate the feature by its `specs/0NN-*`
directory. This analysis therefore runs directly against the four committed artifacts, the
same way siblings 007-016 carry hand-authored `analysis.md` files.

## Verdict

**PASS -- no CRITICAL or HIGH findings.** The four artifacts are internally consistent. All
9 Success Criteria and 13 of 14 Functional Requirements are explicitly task-tagged; the one
untagged FR (FR-003) is covered in substance. The collision risk with the already-existing
F011 (on-disk `012-dashboard-design-skill`) is handled correctly (foundation vs. verb; no new
gate; no divergent source of truth). Two MEDIUM and three LOW findings below are improvements,
not blockers. Safe to proceed to `/speckit-implement`.

## Deterministic checks

| Check | Result |
|-------|--------|
| All four artifacts present (spec/plan/tasks/checklist) | PASS |
| ASCII-only, UTF-8 no BOM (all 4 files) | PASS (verified) |
| Spec-dir slot free when allocated (017 = next after 016) | PASS |
| FR ids contiguous FR-001..FR-014 | PASS (14) |
| SC ids contiguous SC-001..SC-009 | PASS (9) |
| Task ids contiguous T001..T039 (+ T017a, T031a) | PASS (41 tasks) |
| Unresolved placeholders (TODO/TKTK/???/`<placeholder>`) | NONE (the one judgment call is recorded as O-1, not a marker) |
| plan.md deliverable manifest == tasks.md authored files | PASS (5 docs/powerbi, 8 workflows, 5 templates, design/themes/reports, 2 edits) |

## Requirement -> task traceability (spot map)

| Requirement | Has Task? | Task IDs | Notes |
|-------------|-----------|----------|-------|
| FR-001 (route to one surface) | Yes | T003, T008 | the core router behavior |
| FR-002 (visual -> contract + mapped field) | Yes | T009, T018, T021, T023, T030 | |
| FR-003 (never invent/alter a metric) | Substance only | T008 ("metrics from contracts only"), T018 ("metric with NO contract" anti-pattern), T030 ("invents NO metric") | LOW: no explicit `[FR-003]` tag -- see C1 |
| FR-004 (inherit gate; no new gate / no divergent SoT) | Yes | T004, T008, T031 | |
| FR-005 (background = structure, not data) | Yes | T005, T011, T015, T024, T027, T028 | |
| FR-006 (theme = defaults, not meaning) | Yes | T005, T012, T016, T025, T029 | |
| FR-007 (no PBIP/PBIR/DAX/SQL/semantic/pbi-cli) | Yes | T006, T020, T036 | |
| FR-008 (generic, not C086) | Yes | T021, T023-T026, T030, T035 | |
| FR-009 (stop at Principle-V judgment) | Yes | T007, T019 | |
| FR-010 (readiness status, no score, no self-pass) | Yes | T004, T007 | |
| FR-011 (router distinguishes 4 surfaces in its text) | Yes | T003, T008 | |
| FR-012 (design principles committed) | Yes | T009, T010, T013, T014, T017, T026, T030 | |
| FR-013 (QA anti-pattern + screenshot critique) | Yes | T018, T019, T022, T017a | |
| FR-014 (ASCII/no-BOM/short paths/no secret) | Yes | T038 | |
| SC-001..SC-009 | Yes | T032-T039 | every SC has a Phase-6 verification task |

**Coverage**: 14/14 FR have task coverage (13 explicit-tagged + FR-003 substance-covered);
9/9 SC have a verification task. **Coverage = 100% (substance); 96% (explicit FR tag).**

## Consistency findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Coverage / traceability | LOW | tasks.md T008/T018/T030 | FR-003 (never invent a metric) is covered in substance but carries no explicit `[FR-003]` tag on any task. | Add `[FR-003]` to T008 (the HARD RULES task) during implementation; cosmetic, does not change work. |
| C2 | Underspecification | MEDIUM | tasks.md T031a; plan.md | T031a registers F011A in `docs/roadmap/roadmap.md` but the exact roadmap row placement/section ("Then" vs a new sub-row under F011) is left to the implementer. | Acceptable as a Principle-V-style human placement call; implementer should mirror the existing numbering-note style. No spec change needed. |
| C3 | Inconsistency (env) | MEDIUM | .specify/feature.json | `feature.json` points at `004-retail-validate`, stale for every feature 007-017; speckit scripts resolve the wrong feature. | Out of THIS feature's scope (a repo-wide env drift). Flag for a follow-up housekeeping patch; does not block 017. |
| C4 | Terminology | LOW | spec.md / plan.md | "F011A" (roadmap F-number) vs "017" (spec dir) used throughout. | Intentional and documented (header states both, per the roadmap numbering note). No action. |
| C5 | Duplication (by design) | LOW | docs/powerbi/visual-qa.md + workflows/dashboard-qa.md | The QA anti-pattern list lives in two places (prose doc + procedure workflow). | Intentional doc/skill split (plan.md Structure Decision #4); T017a notes "keep the two in sync." Acceptable; flagged so reviewers know it is deliberate, not accidental duplication. |

## Constitution / hard-rule alignment

| Principle / rule | Alignment |
|------------------|-----------|
| I Agent-First, Gate-Enforced | PASS -- a router skill; gate owned by stage doc + F011/012; no self-granted pass |
| II Depend, Never Fork | PASS -- no codegen/engine/CLI; pbi-cli stays F016 |
| III Gold-Only | PASS -- describes design against the gold-bound model; no read surface added |
| IV Source Mapping Before Silver | PASS -- unaffected; reinforced by analogy |
| V Agent Stops at Judgment | PASS -- FR-009; ambiguous surface / business question / design review surfaced |
| VI Defaults Then Deviations | PASS -- conservative tokens default; deviations recorded as warnings |
| VII C086 Is An Example | PASS -- FR-008/SC-007; generic-leakage grep T035 |
| VIII Static-First, Live Deferred | PASS -- docs/templates/skill-first; no new rule; publish deferred |
| IX Secrets & Reproducibility | PASS -- FR-014; no secret/host; ASCII no-BOM; short paths |
| Spine: no new gate / no divergent SoT | PASS -- FR-004; explicit "Relationship to F011/012" section; inherits rule 5/6 verbatim |
| Roadmap rule 5 (no design before contracts) | PASS -- FR-002/FR-004/US2 |
| Roadmap rule 6 (no pbi-cli/PBIP early) | PASS -- FR-007/handoff workflow |
| Roadmap rule 7 (generic) | PASS -- FR-008 |
| Roadmap rule 8 (docs/templates first) | PASS -- the whole foundation shape |
| Roadmap rule 9 (no fake confidence) | PASS -- FR-010 |

**No constitution conflicts.** No CRITICAL findings.

## Open for human (Principle V -- NOT auto-answered)

- **O-1**: does the `powerbi-dashboard-design` router sit ALONGSIDE the F011/012
  `dashboard-design` verb (recommended reversible default: yes, it routes TO it), or eventually
  absorb it? Recorded in spec.md + checklist; a merge would be a later, separate decision.
- The four-surface classification of an AMBIGUOUS request, the business question each page
  answers, and the design-review sign-off are deliberately stop-and-ask (FR-009).

## Auto-decisions made during drafting (recommended defaults)

- Skill at `.claude/skills/powerbi-dashboard-design/` (not top-level `skills/`) -- loadability;
  recorded in plan.md Structure Decision + spec Assumptions.
- Checklist at `checklists/requirements.md` (house convention).
- New top-level dirs `design/`, `themes/`, `reports/` -- justified in plan.md Complexity Tracking.
- Starter theme JSON treated as schema-uncertain, validate-in-Desktop (T029).

## Metrics

- Total Functional Requirements: **14**
- Total Success Criteria: **9**
- Total Tasks: **41** (T001-T039 + T017a + T031a)
- Coverage (requirements with >= 1 task): **100%** (substance) / **96%** (explicit FR tag)
- Coverage (success criteria with a verification task): **100%**
- Ambiguity count: **0** unresolved markers (1 recorded open decision O-1)
- Duplication count: **1** (intentional doc/skill QA split, C5)
- Critical issues: **0** | High: **0** | Medium: **2** (C2 placement, C3 env drift) | Low: **3**

## Recommendation

**Proceed to `/speckit-implement`.** No CRITICAL/HIGH findings. The two MEDIUM items are an
implementer placement call (C2) and a repo-wide env drift outside this feature's scope (C3);
the three LOW items are cosmetic. Optional pre-implementation tidy: add the `[FR-003]` tag to
T008 (C1). The stale `.specify/feature.json` (C3) is worth a separate housekeeping fix so the
speckit scripts work for features 007+, but it does not block 017.
