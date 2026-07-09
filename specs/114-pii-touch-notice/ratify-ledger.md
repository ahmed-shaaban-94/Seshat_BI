# Ratify Ledger -- Personal-Data-Touch Notice (spec 114)

**Status: AWAITING HUMAN RATIFICATION.** This is the stop point of the
idea-to-spec chain. The chain DEFINED and CHECKED the feature; it did NOT
approve, implement, or merge. Ratification is a named-human action the agent is
structurally forbidden to self-grant (Principle V). No `silver.*`/runtime code
was written; this branch carries spec + plan + tasks only.

## What was produced

Branch `114-pii-touch-notice`, spec dir `specs/114-pii-touch-notice/`:

- `spec.md` -- feature spec, 2 clarifications resolved, 14 FR + 6 SC, 3 user
  stories, scope wall.
- `plan.md` -- Constitution Check PASS (9/9 + hard rule #9); Python-composer
  structure decision.
- `research.md` -- 5 decisions (D1 vehicle, D2 enforcement, D3 source, D4
  undecided-definition, D5 idioms).
- `data-model.md`, `contracts/composer.md`, `contracts/verifier.md`,
  `quickstart.md`.
- `tasks.md` -- 17 TDD-ordered tasks, 6 phases; MVP = US1.
- `checklists/requirements.md` -- specify-phase quality checklist (all pass).

## Provenance

Idea #3 from the 2026-07-08 idea bank ("Personal-Data-Touch Notice"), CONSIDER,
V5/F8. Adversarially verified net-new + principle-eligible against `main`
@ 84d05c8 on 2026-07-09 (12-agent workflow, all 6 skeptic verdicts
refuted=false). Fills F040 consumer-data-dictionary's own declared PII exclusion
(its FR-010) rather than competing with it. Grounded on the committed fixture:
`retail_store_sales/source-map.yaml` L69 `customer_id` `pii:true, decision:keep`
+ RC4 disposition, rendered by no shipped surface.

## Key decisions the ratifier is signing off on

1. **Vehicle: Python composer** (`src/retail/pii_notice.py` + CLI verb), NOT
   skill-only. Chosen because FR-011 needs a MECHANICAL guarantee a prose skill
   cannot give. (Alternative on record: skill + external verifier.)
2. **Enforcement: a decoupled unit-test verifier**, NOT a `@register` retail
   check rule -- adding a gate would violate the feature's own FR-007. The
   mechanical guarantee lives in the test suite.
3. **Disposition source: `source-map.yaml` only** (Clarification Q1);
   `unresolved-questions.md` not parsed. FR-010 is an intra-file check.
4. **Output: `mappings/<table>/pii-touch-notice.md`** (Clarification Q2),
   mirroring F040's co-located output.

## Open item flagged for the ratifier (from the plan/advisor)

- If the ratifier prefers to KEEP the feature skill-only (F040 posture), that
  consciously downgrades FR-011 from a mechanical guarantee to prose enforcement.
  The spec as written assumes the mechanical (Python) path. Confirm the Python
  vehicle, or direct the skill-only downgrade here.

## Analyze outcome

0 CRITICAL, 0 HIGH. 100% semantic requirement coverage. 0 constitution
violations. 4 LOW nits (optional id-tag traceability; denylist enumerated in
verifier.md not spec.md) -- none blocking.

## Ratification

- [ ] **RATIFIED** by: __________________ (named owner or explicitly-delegated
  authority) on ____-__-__.
- Ratifying means: the spec/plan/tasks are approved to proceed to
  `/speckit-implement` (or the equivalent build) on this branch.
- Until this box is checked by a named human, no implementation begins.
