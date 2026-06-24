# Cross-Artifact Analysis: 012-dashboard-design-skill

**Date**: 2026-06-24 | **Scope**: spec.md, plan.md, tasks.md vs the constitution,
the roadmap hard rules, and the readiness spine. Read-only consistency pass
(speckit-analyze). No code; docs-only feature.

## Inputs analyzed

- `specs/012-dashboard-design-skill/spec.md`
- `specs/012-dashboard-design-skill/plan.md`
- `specs/012-dashboard-design-skill/tasks.md`
- Authoritative references: `docs/readiness/dashboard-ready.md`,
  `docs/readiness/semantic-model-ready.md`, `docs/readiness/readiness-model.md`,
  `docs/roadmap/roadmap.md`, `.specify/memory/constitution.md`.

## A. Requirement -> task coverage

All 12 FRs (FR-001..FR-012) map to at least one task; no orphan FR.

| FR | Covered by |
|----|------------|
| FR-001 (gate: pass before design) | T003, T005 |
| FR-002 (every visual -> one approved contract) | T006, T009 |
| FR-003 (no invented metric) | T009, T010 |
| FR-004 (author-only, no publish/pbi-cli) | T004, T012 |
| FR-005 (R1 relative ref exit 0) | T008 |
| FR-006 (status + evidence + blockers, no score) | T006, T009 |
| FR-007 (no self-granted pass) | T011 |
| FR-008 (stop at judgment calls) | T005, T012, T013 |
| FR-009 (generic, no C086) | T007, T014 |
| FR-010 (record next action) | T006 |
| FR-011 (record dropped contracts) | T013 |
| FR-012 (ASCII/UTF-8 no BOM, no host/secret) | T007, T014 |

SC coverage: SC-001/004/006/007 cited inline at a task; SC-002/003/005 swept by
the umbrella verification task T015 ("Verify ... every Success Criterion
SC-001..SC-007"). Acceptable for a single-file docs feature (not a defect).

## B. User-story -> task coverage

- US1 (design from contracts, P1): T005-T008. OK.
- US2 (refuse when gate not pass, P1): T003 (foundational gate) + T009-T010. OK.
- US3 (stop at review + publish boundary, P2): T004 (foundational boundary) +
  T011-T013. OK.
- MVP = Setup + Foundational + US1 + US2 (both P1: the gate AND the binding).
  Stated consistently in spec, plan, and tasks.

## C. Consistency with the readiness spine and roadmap

- Hard gate (rule 5): spec FR-001, plan Constitution-Check, tasks T003 all encode
  "no design before semantic_model_ready: pass." Matches dashboard-ready.md and
  readiness-pipeline.md. OK.
- Author/publish boundary (rule 6, F016 last): spec FR-004 + User Story 3, plan
  Principle II, tasks T004/T012 keep pbi-cli/PBIP authoring automation OUT and
  name F016 as its owner. Matches dashboard-ready.md. OK.
- Status model (no fake confidence): FR-006/FR-007 use the four statuses +
  evidence + blockers, forbid a fabricated score and a self-granted pass; the
  skill records at most `warning`, the reviewer's approvals[] entry enables
  `pass`. Matches readiness-model.md. OK.
- R1 reuse (no new gate): all three artifacts rely on existing retail check rule
  R1 for the relative model reference; no new rule proposed. OK.
- Generic (rule 7): FR-009 + T014 + the plan's template-scaffold decision keep the
  skill + any template free of C086/pharmacy values. OK.
- Docs/skill-first (rule 8): ships a SKILL.md (+ optional generic templates), no
  code, no codegen engine, no CLI -- matches the all-skills verb architecture. OK.

## D. Feature-number note (by design, not a defect)

The roadmap lists this as F011 ("Power BI Dashboard Design Skill"). It is drafted
under spec directory 012-dashboard-design-skill per the launch instruction
(explicit Number 012, to avoid parallel-worktree numbering collisions). The spec
records both (title cites "Roadmap F011"; directory/branch are 012). Renaming
012 -> 011 later is a cheap, reversible follow-up if the team prefers alignment.

## E. Duplication / contradiction scan

- No contradictory requirements across the three artifacts.
- No duplicate FR/SC ids (FR-001..012, SC-001..007 each defined once).
- "warning, not pass" stated once per artifact (spec FR-007, plan Constraints,
  tasks T011) with consistent wording. No drift.
- The author/publish boundary stated consistently in spec, plan, tasks. No drift.

## F. Open items for a human (Principle V -- NOT auto-answered)

1. PII / publish-safety of the dashboard surface -- whether any approved contract
   a visual binds to exposes a PII-derived field on a shared page is a
   publish-safety call for the data/BI owner.
2. Business-rollup / segment shown on the page -- which rollups/segments a visual
   aggregates to (the analytical story) is a business decision.
3. Product/entity identity used as a drill key -- which identity column keys a
   dimension/drill is reserved; the skill follows the model's declared keys.

## G. Auto-resolved decisions (recommended defaults)

1. Skill path/name = .claude/skills/dashboard-design/SKILL.md (matches existing
   verb dirs; short for the Windows 260-char limit). Reversible: easy.
2. No codegen engine / no report template / no `retail design` CLI -- pure skill
   (Principle II, rule 8, YAGNI). Reversible: easy.
3. Optional generic templates/* scaffolds vs inline-in-skill left as a tasks-level
   call (T007 optional). Reversible: easy.
4. Highest status the skill writes = `warning` (never self-granted `pass`).
   Reversible: easy, but changing it weakens the gate -- not recommended.
5. No new retail check rule -- reuse R1. Reversible: easy.

## Verdict

CONSISTENT / ready to draft the skill. All FRs have tasks; all user stories have
tasks; rules 5/6/7/8 are encoded uniformly across spec, plan, tasks and agree
with dashboard-ready.md, readiness-model.md, and the roadmap. The only items left
open are the four Principle V human judgment calls in Section F.
