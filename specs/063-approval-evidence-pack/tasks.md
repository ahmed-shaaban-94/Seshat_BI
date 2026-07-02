---
description: "Task list for Approval Evidence Pack for the Named-Human Stage Gate"
---

# Tasks: Approval Evidence Pack for the Named-Human Stage Gate

**Input**: Design documents from `specs/063-approval-evidence-pack/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Deliverable shape**: docs/skill/template Product Module -- NO runtime code, NO `retail
check` rule (FR-019). Verification is `retail check` staying green with an unchanged rule
count, plus doc-level demonstration of the acceptance scenarios (F028 precedent). No pytest
module is added.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency)
- **[Story]**: US1 / US2 / US3 (from spec.md), or SETUP / POLISH

## Phase 1: Setup

- [ ] T001 [SETUP] Confirm the five read-source paths exist and are readable in the repo (the
  seven `docs/readiness/*-ready.md`, `templates/readiness-status.yaml`,
  `src/retail/rules/assumptions.py`, `docs/quality/parked-on.yaml`,
  `mappings/<table>/metrics/` shape). Record any absent source as a plan risk. (research.md)

## Phase 2: Foundational (blocking prerequisites)

- [ ] T002 [SETUP] Author the generic pack template `templates/approval-evidence-pack.md`
  with the ordered sections from data-model.md (header, gate requirements, readiness states
  [selected + prior only], open blockers, unresolved assumptions [per contract], blocking
  parked-on edges, pending contracts, approval slot). Placeholders only; ASCII/UTF-8 no BOM;
  short paths. NO score field, NO count field (FR-012, FR-017, FR-018, FR-020, FR-021).
- [ ] T003 [SETUP] Embed the F024 module contract in the template banner / to be reused by the
  skill: Product Module / `artifact-writing`; Core Authority READ list; derived artifact
  WRITTEN; EXECUTES none; forbidden operations (no approvals[] write, no stage->pass, no truth,
  no DB/PBIP, no score/count). (plan.md Design 3)

## Phase 3: User Story 1 -- one pack before signing (Priority: P1)

**Goal**: a named human gets one ordered, fully-traceable pack for one (table, stage).
**Independent test**: generate a pack for a table+stage with committed artifacts; every claim
resolves to a committed path; approval slot empty; no score/count.

- [ ] T004 [US1] Author `.claude/skills/approval-evidence-pack/SKILL.md`: purpose, the input
  contract (five reads), the stage-key -> readiness-doc 1:1 map (data-model.md), the ordered
  compose steps, and the surface-never-assert + empty-approvals discipline reused verbatim in
  spirit from F028. (FR-001, FR-003, FR-004, FR-005, FR-009)
- [ ] T005 [US1] In SKILL.md, specify the empty-approval-slot terminal section and the
  structural incapability to write `approvals[]` / move a stage / grant approval / define
  business meaning. (FR-009, FR-010)
- [ ] T006 [US1] In SKILL.md, specify the no-score / no-count rule and that readiness is only
  the four statuses + evidence + blockers. (FR-012)
- [ ] T007 [US1] Add to quickstart.md a worked walk-through (generic placeholders) of
  requesting and reading a pack; confirm it matches the template section order. (SC-001)

## Phase 4: User Story 2 -- missing source -> blocker (Priority: P1)

**Goal**: no fabrication; every missing/unreadable source is a recorded blocker.
**Independent test**: generate against a table with no readiness-status.yaml; top-level
blocker names the missing path; no invented status; slot empty.

- [ ] T008 [US2] In SKILL.md, specify the missing-source handling: a missing / unfilled /
  blank-template / unreadable source -> an explicit BLOCKER naming the path; never fabricate a
  status or content. Cover the three US2 acceptance cases (no status file; stage
  `not_started`; unreadable metric contract). (FR-011)
- [ ] T009 [US2] In SKILL.md, specify the "prior stage not `pass`" blocker branch and the
  "already-signed approval -> surface read-only, no fresh slot" branch. (FR-016, edge cases)

## Phase 5: User Story 3 -- generic across seven stages (Priority: P2)

**Goal**: same module serves any stage via the stage parameter, generically.
**Independent test**: generate for two stages of two tables; each cites the correct readiness
doc; no C086 specifics in template/labels.

- [ ] T010 [US3] In SKILL.md, specify the mechanical-gate branch (Silver/Gold Ready -> "no
  stage-approval applies" + surface the mechanical result). (FR-015)
- [ ] T011 [P] [US3] Add the generic-only guard to template + SKILL.md: no worked-example
  (C086/pharmacy) label/grain-key/column-name; C086 cited only; resolve a generic
  `mappings/<table>/` path. (FR-014, SC-006)

## Phase 6: Polish + roadmap wiring

- [ ] T012 [POLISH] Edit `docs/roadmap/roadmap.md`: assign the next Product Module F-number
  after F028 to this feature and note on-disk spec dir `063-approval-evidence-pack` (roadmap
  F-number wins on any dir!=number disagreement, per the F028 note). (plan.md Design 4)
- [ ] T013 [POLISH] Verify `retail check` passes and the rule count is UNCHANGED (this feature
  adds no rule); confirm no `src/` or `tests/` change was introduced. (FR-019)
- [ ] T014 [POLISH] ASCII/UTF-8-no-BOM + short-path sweep of the two new artifacts and the
  roadmap edit (`--`/`->`, no glyphs). (FR-017)

## Dependencies

- T002-T003 (template + module contract) block all of Phase 3-5 (the skill references them).
- US1 (T004-T007) is the MVP slice; US2 and US3 extend the same SKILL.md.
- T012-T014 are polish, run last.

## Principle-V carve-out (do NOT implement a resolution)

- FR-008 (pending-contracts definition) and FR-013 (business-rule/PII summarisation boundary)
  stay OPEN. Tasks reference them as inputs; NO task resolves them. The template surfaces
  pending contracts against whatever definition a human later rules -- it does not hardcode
  one.
