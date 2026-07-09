# Ratify Ledger -- Approver Decision Surface (spec 115)

**Status: AWAITING HUMAN RATIFICATION.** The stop point of the idea-to-spec
chain. DEFINED and CHECKED; NOT approved, implemented, or merged. Ratification is
a named-human action the agent is structurally forbidden to self-grant (Principle
V). Spec + plan + tasks only; no runtime code written.

## What was produced

Branch `115-approver-decision-surface`, dir `specs/115-approver-decision-surface/`:

- `spec.md` -- 2 clarifications resolved, 13 FR + 6 SC, 3 user stories, scope wall.
- `plan.md` -- Constitution Check PASS (9/9 + hard rule #9); standalone-module
  structure decision.
- `research.md` -- 5 decisions (D1 structure, D2 extraction, D3 completeness
  verifier, D4 refusal-scope/question-mapping, D5 output vehicle).
- `data-model.md`, `contracts/view.md`, `contracts/verifier.md`, `quickstart.md`.
- `tasks.md` -- 18 TDD-ordered tasks, 6 phases; MVP = US1.
- `checklists/requirements.md`.

## Provenance

Idea #2 from the 2026-07-08 idea bank ("Approver Decision Surface"), CONSIDER,
V6/F7. Adversarially verified net-new + eligible vs `main` @ 84d05c8 on
2026-07-09 (all 6 skeptic verdicts refuted=false): no shipped surface reorders
refutation-first and none reads `unresolved-questions.md`. Companion to F027
approval-console (which OWNS the write-back); this surface only re-orders and
writes nothing.

## Key decisions the ratifier is signing off on

1. **Structure: STANDALONE `src/retail/approver_view.py`**, NOT folded into
   `blocker_explainer`. The clarify answers (surfaces `warning` stages, reads a
   2nd file, adds a reassurance grouping) made the delta a SECOND
   RESPONSIBILITY, not a sort mode -- folding would overload a single-purpose
   shipped module and balloon CodeScene-policed complexity. Reuse is achieved by
   EXTRACTING the shared classifier into `readiness_classify.py` (behavior-
   preserving, regression-locked). (Rejected option on record: fold as a sort-
   mode.)
2. **Enforcement: a non-gating unit-test verifier**, NOT a `@register` retail
   check rule (FR-007 forbids a gate). Centered on REFUSAL-CASE COMPLETENESS
   (V1/V2): every blocked/warning/unmet-approval/open-question item present in
   the refusal case, none misfiled as reassurance -- because the danger is a
   refusal reason the signer never sees, not ordering flake. (This carries over
   the failure-class from spec 114's join defect: put the guarantee ON the risk.)
3. **Refusal scope (Clarification Q1)**: `blocked` + `warning` stages + unmet
   approvals + OPEN questions. **Question mapping (Q2)**: by the committed
   `Who must answer` column, not by scoring free-text prose (keeps rule #9 clean).
4. **Output: a READ VIEW** (printed text/JSON), no write path in the MVP
   (Principle-V no-write proof is trivial); a `--write` companion is a deferred
   optional extension (research D5).

## Open item flagged for the ratifier

- **OPEN-1 -- Structure confirmation.** The standalone-vs-fold call (decision 1
  above) was the load-bearing plan decision the verification flagged. It is
  advisor-validated as standalone, but is recorded here for owner confirmation
  since it touches a shipped module (`blocker_explainer` via the classifier
  extraction). Confirm standalone + extraction, or direct the fold.

## Analyze outcome

0 CRITICAL, 0 HIGH. 100% semantic requirement coverage; every verifier assertion
V1-V9 is task-referenced. 0 constitution violations. LOW nits only (id-tag
traceability; the Open-questions parser column shape -- pinned by the fixture).

## Branch note (cross-spec)

This branch was created off `114-pii-touch-notice` (the prior chain's branch),
so #114's two spec commits are in #115's ancestry. Both are SPEC-ONLY and
independent; when merging, treat each spec on its own (or rebase #115 onto main
after #114 lands) so they don't tangle. Neither is ratified yet.

## Ratification

- [x] **RATIFIED** by: Ahmed Shaaban (repo owner) on 2026-07-09.
- Ratifying means: spec/plan/tasks approved to proceed to `/speckit-implement`
  (or the equivalent build) on this branch.
- Until this box is checked by a named human, no implementation begins.

### Owner ruling (2026-07-09)

- **OPEN-1 (structure): STANDALONE + extract classifier.** New
  `src/retail/approver_view.py`; reuse `blocker_explainer`'s rank by EXTRACTING
  `_CATEGORY_RULES`/`_classify` into a shared `readiness_classify.py`
  (behavior-preserving, regression-locked so `blocker_explainer`'s output stays
  byte-identical). Fold-into-`blocker_explainer` REJECTED: the clarify answers
  (warning stages + `unresolved-questions.md` ingestion + a reassurance
  grouping) make it a second responsibility, not a sort mode.

### Branch note update (2026-07-09)

Branch `115` was REBASED onto the implemented `114-pii-touch-notice` tip after
#114 was ratified + built, so #114's ratification + implementation are now in
#115's ancestry. When landing: #114 first, then #115 (rebase onto main after
#114 merges).
