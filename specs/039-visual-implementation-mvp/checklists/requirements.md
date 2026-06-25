# Specification Quality Checklist: Visual Implementation MVP (F034)

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-06-25
**Feature**: F034 (roadmap F-number, authoritative) | Spec directory `039-visual-implementation-mvp` (next free on-disk slot; script numbers from max 038) | [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) -- this is a docs/templates/skill
      authoring slice (roadmap rule 8); the workflow, trace template, and Dashboard Ready doc edit
      ARE the artifact, not application code. The only PBIR change is a human Desktop save.
- [x] Focused on user value and business needs (an analyst gets the dashboard they approved, as a
      real page reviewed in git -- closing the unspecced blueprint -> page seam)
- [x] Written for non-technical stakeholders (the build / refuse / boundary throughline and the
      "design approved vs page implemented" distinction are stated in plain terms)
- [x] All mandatory sections completed (User Scenarios, Requirements, Key Entities, Success
      Criteria, Assumptions all present)

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain (the one judgment call -- workflow-alongside vs
      standalone verb skill -- is recorded as open decision O-1 with a reversible default
      "alongside", not a blocker; same posture 010/017 used)
- [x] Requirements are testable and unambiguous (FR-001..FR-014; each is a MUST/MUST NOT that maps
      to an SC and an acceptance scenario)
- [x] Success criteria are measurable (SC-001..SC-009; counts, percentages, exit codes, 0/100%
      thresholds)
- [x] Success criteria are technology-agnostic (about build/trace/gate/boundary BEHAVIOR and
      counts, not about specific tooling internals)
- [x] All acceptance scenarios are defined (3 P1 user stories -- build, refuse, stay-inside-boundary
      -- each with numbered Given/When/Then scenarios and an Independent Test)
- [x] Edge cases are identified (design changes after build; Desktop owns report.json /
      diagramLayout.json; Windows path/encoding limits; slicer-is-not-a-trace-row;
      discount-rate trap; dashboard_ready already pass on design alone)
- [x] Scope is clearly bounded (no PBIR generator, no pbi-cli/MCP, no publish, no DAX/SQL/
      semantic-model edits, no new gate/stage/status/rule; F016 named as owner of automation)
- [x] Dependencies and assumptions identified (F011/012 + F011A upstream SHIPPED; F016 deferred
      boundary; Dashboard Ready gate/owner unchanged; build is a human Desktop action; first
      worked example retail_store_sales)

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria (FR -> SC -> user-story-scenario
      traceability: e.g. FR-003 -> SC-002 -> US1.2/US2.3/US2.4; FR-008 -> SC-004 -> US3)
- [x] User scenarios cover primary flows (build the page; refuse when design unapproved; stay
      inside the manual/no-publish boundary -- the three loads)
- [x] Feature meets measurable outcomes defined in Success Criteria (each SC ties to at least one FR)
- [x] No implementation details leak into specification

## F034-Specific Risk Checks (the things this feature could get wrong)

- [x] **Independent of F016, not blocked by it.** The "Relationship to F016" section states F034 is
      a HUMAN MANUAL BUILD reviewed in git, F016 is EXECUTION AUTOMATION; rule 6 gates the
      automation, not the manual build (FR-008, SC-004, US3). The boundary is stated explicitly.
- [x] **No new gate / stage / status / rule.** FR-005 records the result ONLY as an EVIDENCE ITEM
      under the existing Dashboard Ready owner; SC-005 asserts 0 new stages/statuses/rules and
      `retail check` rule count UNCHANGED. No divergent source of truth (constitution Governance).
- [x] **Hard gate inherited verbatim.** FR-006 / US2 / SC-003: no implemented-page evidence before
      `semantic_model_ready: pass` AND the design-review sign-off (rule 5); agent STOPS otherwise.
- [x] **Consumes, never re-designs.** FR-004 forbids inventing/altering a metric and re-design/
      re-binding; F009 owns metric definition, F011/012 owns design/binding. F011A handoff notes
      are the input contract, restated not duplicated (FR-001).
- [x] **1:1 trace, no orphans, no unmapped fields.** FR-003 / SC-002: every measure-bearing visual
      maps to exactly one approved contract by name + a mapped semantic-model field; orphan or
      unmapped field forces trace `blocked`.
- [x] **Manual/no-publish boundary holds.** FR-008 / FR-009 / SC-004: 0 generated PBIR, 0 pbi-cli/
      MCP, 0 publish, 0 DAX/SQL/semantic-model edits; the only PBIR change is the human Desktop
      save; hand-editing Desktop-owned files is forbidden.
- [x] **Generic, not C086/pharmacy.** FR-010 / SC-006: 0 subject-area specifics in any generic
      artifact (rule 7, Principle VII); worked values live only in the retail_store_sales instance.
- [x] **Discount-rate honesty.** FR-013 / SC-007: the worked-example discount visual and trace row
      show the approved DiscountedTransactionRate = 50.37% with caveats (33.39% unknown excluded;
      33.55% floor); 0 occurrences of the retracted/stale rate.
- [x] **No fabricated confidence / no self-granted pass.** FR-011 / FR-012 / SC-008: four statuses
      + evidence + blockers, never a numeric score (rule 9); `dashboard_ready: pass` stays the BI
      owner's recorded design-review action; Principle V judgment calls are stop-and-ask.
- [x] **Plain-text PBIR / git-diff reviewable.** FR-002 / SC-001: the report is saved as
      plain-text PBIR (PBIP) so the page is a git diff a reviewer reads like code; 0 opaque
      `.pbix` committed.
- [x] **R1 / relative model path.** FR-007 / SC-001: PBIR references the governed model by a
      relative path (the constraint `retail check` R1 enforces) -- never an absolute/remote ref.
- [x] **ASCII + UTF-8 no BOM + path limits.** FR-014 / SC-009: all committed files ASCII, UTF-8 no
      BOM, repo-relative paths <= 200 chars, under the Windows 260-char PBIR limit; 0 real
      hosts/secrets (Principle IX + G6).

## Notes

- This spec is a docs/templates/skill-only authoring slice (Principle VIII, roadmap rule 8): it
  adds no runtime code, so "implementation details" here means the workflow/template/doc shapes,
  which ARE the artifact this feature delivers -- not application code. The one PBIR change is a
  human Desktop save committed as reviewable plain text, not an agent-authored file.
- Open decision O-1 (the implementation-verification workflow lives alongside `powerbi-handoff.md`
  vs as a standalone verb skill) is recorded with a recommended, reversible default (alongside),
  per the spec's defaults-then-deviations posture -- the same way 010 and 017 handled their O-1s.
- The F016-independence and no-new-gate claims are stated explicitly: the "Relationship to F016"
  section and FR-005/FR-008/SC-004/SC-005 carry them; F034 reuses Dashboard Ready's rule-5 gate
  verbatim and adds only an evidence item under the existing owner.
- Principle V judgment calls (whether a built page faithfully realizes the approved design,
  whether a layout deviation found during the build is acceptable, whether the sign-off covers the
  built page) are deliberately surfaced as stop-and-ask requirements (FR-011), not auto-answered.
- The dashboard_ready-already-pass-on-design edge case is handled non-destructively: building ADDS
  the implemented-page evidence; a discovered divergence is a new warning/blocked finding on the
  page, not a retraction of the design approval.
