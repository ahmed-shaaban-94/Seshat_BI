# Research: Approver Decision Surface

Phase 0 decisions. No NEEDS CLARIFICATION remained after `/speckit-clarify`; the
open items were the STRUCTURE (standalone vs fold) and the ENFORCEMENT shape,
resolved here.

## D1 -- Structure: STANDALONE module, reuse the rank by extraction (not by folding)

**Decision**: Build a standalone `src/retail/approver_view.py` + CLI verb. Reuse
`blocker_explainer`'s category rank by EXTRACTING its module-private
`_CATEGORY_RULES` / `_classify` into a shared importable `readiness_classify.py`
that both modules call. Do NOT fold the surface into `blocker_explainer.py`.

**Rationale**: The verification workflow and the initial advisor lean both said
"prefer fold", but that lean was premised on a THIN delta ("re-sort existing
items + one new input"). The two clarify answers broke that premise:
- Q1: the surface surfaces `warning` stages -- which `blocker_explainer`
  DELIBERATELY ignores (it acts only on `status == "blocked"` + missing
  approvals).
- The surface reads `unresolved-questions.md` -- a SECOND file `blocker_explainer`
  never touches.
- It introduces a REASSURANCE grouping `blocker_explainer` has no concept of.
That is a SECOND RESPONSIBILITY, not a sort mode. Folding would overload a
single-purpose shipped module and balloon the complexity the CodeScene
new-code-health gate polices. Crucially, "reuse the rank" does NOT require
"live in the same module": a standalone module IMPORTS the shared classifier.
So folding buys nothing on the reuse axis and only adds responsibility.

**Alternatives considered**:
- *Fold as a sort-mode on `blocker_explainer`* -- rejected: overloads the module,
  fails the thin-delta premise, and the reuse benefit is obtainable by extraction.
- *Copy-paste the classifier into the new module* -- rejected: duplicates the
  #229 rank (drift risk); extraction is the DRY-correct move.

## D2 -- The classifier extraction is behavior-preserving + regression-locked

**Decision**: Move `_CATEGORY_RULES`, `_DEFAULT_CATEGORY`, and `_classify` from
`blocker_explainer.py` into `src/retail/readiness_classify.py` with a public
`classify(reason) -> (category, ...)`; `blocker_explainer` imports them. Add/keep
a test asserting `blocker_explainer`'s output is BYTE-IDENTICAL before and after.

**Rationale**: A move-refactor of shipped code must not change `blocker_explainer`'s
behavior or its shipped tests. Labeling it behavior-preserving + regression-locking
it keeps the CodeScene health gate and the existing `test_blocker_explainer.py`
green, and keeps the extraction out of the "new complexity" column.

## D3 -- Enforcement: a non-gating verifier asserting REFUSAL-CASE COMPLETENESS

**Decision**: The verifier (unit tests, NOT a `@register` retail check rule --
FR-007 forbids a gate) asserts, beyond deterministic ordering, that EVERY
refusal-eligible item appears in the refusal case and NONE is misfiled as
reassurance or dropped: every `blocked`/`warning` stage reason, every
approval-requiring stage lacking a valid approval, and every OPEN
`unresolved-questions.md` row is present in the refusal section; every `pass`
stage / valid approval / `answered` question is in reassurance, never the reverse.

**Rationale**: Carries over the failure-class from spec 114's join defect -- there,
a verbatim-fidelity check sat OUTSIDE the real risk (mis-attribution). Here the
danger is not ordering flake; it is a refusal-eligible item (an unmet approval, an
open governance question, a blocked/warning stage) silently landing in
reassurance or dropped, so the signer never sees the reason to refuse. The
mechanical guarantee must sit ON that risk: assert completeness + correct
side-of-the-line, not just stable sort.

## D4 -- Refusal scope + question mapping (Clarifications Q1/Q2, confirmed)

**Decision**: Refusal case = `blocked` OR `warning` stage reasons + approval-
requiring stages with no valid `approvals[]` entry + OPEN
`unresolved-questions.md` rows (Status != answered). Open-question category by the
committed `Who must answer` column: governance/data-owner -> approval bucket;
analyst -> grain/readiness by the shipped keyword classifier; unrecognized ->
readiness default. Reassurance = pass stages + valid approvals + answered questions.

**Rationale**: Grounded in the committed `retail_store_sales` fixture -- its
`readiness-status.yaml` carries per-stage `status`/`blocking_reasons[]`/`approvals[]`
and its `unresolved-questions.md` Open-questions table carries the `Who must
answer` column (governance/analyst/data-owner) and `Status`. Mapping by the
structured owner column (not free-text prose) keeps every ordering input a
committed fact -- no synthesized category, hard rule #9 clean by construction.

## D5 -- Output vehicle (read view default; --write companion deferred)

**Decision**: Default is a READ VIEW (printed text / JSON), writing nothing --
this is the core, and keeps FR-006's structural no-write guarantee simple to
prove. A `--write` companion-file option (e.g. `approver-view.md`) is a MINOR
deferred sub-decision the plan flags but does not require for the MVP; if added,
it is the ONLY write and must not touch any upstream artifact.

**Rationale**: The signer reads the view at the approval moment; a printed view
is sufficient for the MVP and makes the no-write proof trivial. A written
companion is a convenience, not core, and is left as an explicit optional
extension so the default surface stays provably write-free.
