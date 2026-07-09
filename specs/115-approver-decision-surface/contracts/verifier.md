# Contract: the Approver-view verifier (test-only, non-gating)

The mechanical guarantee. It lives in the test suite, NOT in `retail check`
(FR-007 forbids a gating rule). Centered on refusal-case COMPLETENESS -- the real
risk -- not merely deterministic ordering.

## `assert_refusal_case_complete(view: dict, status_yaml: dict, questions_rows: list) -> None`

Given a composed view and the parsed committed inputs, raises `AssertionError`
unless ALL hold:

- **V1 completeness (SAFETY)**: every refusal-eligible source item is present in
  `view["refusal_case"]` exactly once -- i.e. every `blocked` stage reason, every
  `warning` stage reason, every approval-requiring stage with no valid
  `approvals[]` entry, and every OPEN (`Status != answered`) question row. None
  dropped.
- **V2 correct-side**: no refusal-eligible item appears in
  `view["reassurance"]`; and no `pass` stage / valid approval / `answered`
  question appears in `view["refusal_case"]`. (This is the trap from spec 114:
  the danger is a refusal item silently reading as reassurance, so the assertion
  sits ON that boundary.)
- **V3 fixed-rank order**: `refusal_case` is sorted by the fixed enum rank
  (approval=0 > grain=1 > live_validation=2 > artifact=3 > readiness=4), ties
  broken by the shipped lexical key; each item's `rank` equals the enum index
  (a LOOKUP), never a computed value.
- **V4 verbatim + cite**: each item's `reason` is a verbatim substring of a
  committed source field and carries a source path (FR-005).
- **V5 no-score**: no numeric score/count/percentage token in the rendered view.

## Standalone assertions

- **V6 no-write**: `grep` shows no `write_text`/`open(...,'w')`/YAML-dump in
  `approver_view.py`; a default run changes no tracked file (git-status).
- **V7 input-absence**: a missing `readiness-status.yaml` OR
  `unresolved-questions.md` is named in `missing_inputs[]`; the surface never
  presents a missing questions file as "no open questions".
- **V8 generic**: same composer over two distinct tables, no per-table branch.
- **V9 regression-lock**: `build_blocker_explanations` output is byte-identical
  before/after the `readiness_classify` extraction (protects the shipped #229
  behavior).

## Fixtures

| Fixture | Shape | Expected |
|---------|-------|----------|
| full-refusal | blocked stage + warning stage + approval-required stage w/ no approval + OPEN governance question | all four in refusal_case, rank-ordered (approval items top); nothing misfiled |
| all-pass (reassurance) | every stage pass, valid approvals, all questions answered (the retail_store_sales shape) | empty refusal_case + explicit "nothing to refuse"; approvals/answered in reassurance |
| questions-only | open analyst + open governance rows | both in refusal_case; governance ranked above analyst |
| missing-status | no readiness-status.yaml | missing_inputs names it; no fabricated refusal |
| missing-questions | status present, no unresolved-questions.md | refusal_case from status; missing_inputs notes questions unavailable (NOT "no open questions") |
| second-table | a distinct conformant table | correct view, same code (V8) |
