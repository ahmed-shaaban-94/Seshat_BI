# Specification Quality Checklist: Power BI Visual Foundation (F011A)

**Purpose**: Validate specification completeness and quality before proceeding to implementation
**Created**: 2026-06-25
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) -- docs/templates/skill shapes
      are the artifact this feature delivers, not application code
- [x] Focused on user value and business needs (the agent reasons about design correctly and safely)
- [x] Written for non-technical stakeholders (the four-surface distinction is the throughline)
- [x] All mandatory sections completed (User Scenarios, Requirements, Success Criteria, Assumptions)

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain (the one judgment call -- router alongside vs.
      absorb 012 -- is recorded as open decision O-1 with a reversible default, not a blocker)
- [x] Requirements are testable and unambiguous (FR-001..FR-014 each map to an SC and a task)
- [x] Success criteria are measurable (SC-001..SC-009; counts, percentages, exit codes)
- [x] Success criteria are technology-agnostic (about routing/gating/separation behavior, not tooling)
- [x] All acceptance scenarios are defined (3 P1 user stories, each with scenarios + an independent test)
- [x] Edge cases are identified (spanning surfaces, critique-implies-wrong-metric, dark dense
      page, theme-encoding-a-rule, no-contracts-yet, "just build it")
- [x] Scope is clearly bounded (docs/templates/skill only; out-of-scope = data edits, PBIP/PBIR,
      pbi-cli, DAX, SQL, semantic-model, codegen, CLI, new gate)
- [x] Dependencies and assumptions identified (F009/F010 upstream; F011/012 consumer; F016 deferred)

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria (FR -> SC -> task traceability)
- [x] User scenarios cover primary flows (route / gate / separate -- the three loads)
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## F011A-Specific Risk Checks (the things this feature could get wrong)

- [x] **No divergent source of truth.** The spec's "Relationship to F011/012" section states
      F011A is the FOUNDATION and F011/012 is the VERB; F011A adds no new gate and reuses
      Dashboard Ready's rule-5/rule-6 gating verbatim (FR-004). [Constitution Governance clause 4]
- [x] **Four surfaces never blended.** Routing into exactly one of {visuals, background/canvas,
      theme JSON, handoff} is the core behavior (FR-001/FR-011, US1, SC-001).
- [x] **Background is structure, not data.** Forbidden-dynamic-content rule is explicit
      (FR-005, SC-005); the background template carries the section.
- [x] **Theme JSON is defaults, not meaning.** The must-NOT-control list is explicit
      (FR-006, SC-006); the theme spec carries both sides.
- [x] **No metric invented / no unmapped field.** Every data-bound visual references one
      approved contract + a mapped field (FR-002/FR-003, SC-004).
- [x] **No data edits in this slice.** 0 PBIP/PBIR/DAX/SQL/semantic-model/pbi-cli edits
      (FR-007, SC-003); handoff stops at notes, F016 owns execution.
- [x] **Generic, not C086.** No pharmacy specifics in any artifact (FR-008, SC-007); C086 is
      an example, not the schema (Principle VII).
- [x] **Skill loadability.** The skill is planned at `.claude/skills/powerbi-dashboard-design/`,
      not the input's top-level `skills/`, because this repo discovers skills only under
      `.claude/skills/` (deviation recorded in plan.md Structure Decision + spec Assumptions).
- [x] **No fabricated confidence / no self-granted pass.** Four statuses + evidence + blockers,
      never a score; `dashboard_ready: pass` is the verb's design-review, not this foundation's
      (FR-010, SC-009).

## Notes

- This spec is a docs/templates/skill-only slice (Principle VIII, roadmap rule 8): it adds no
  runtime code, so "implementation details" here means the skill/doc/template/token/theme/
  blueprint shapes, which ARE the artifact this feature delivers.
- Open decision O-1 (router `powerbi-dashboard-design` alongside vs. eventually absorbing the
  012 `dashboard-design` verb) is recorded with a recommended, reversible default (alongside;
  the router ROUTES to the verb), per the spec's defaults-then-deviations posture -- the same
  way 010 handled its storage-path O-1.
- Principle V judgment calls (which surface an ambiguous request is, which business question a
  page answers, whether a readability/grain deviation is acceptable, the design-review
  sign-off) are deliberately surfaced as stop-and-ask requirements (FR-009), not auto-answered.
- The starter theme JSON schema is treated as UNCERTAIN: `themes/tower-retail.theme.json` is a
  minimal conservative starter that must be validated in Power BI Desktop (recorded in spec
  Assumptions + planned in task T029).
