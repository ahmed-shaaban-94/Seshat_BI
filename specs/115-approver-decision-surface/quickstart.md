# Quickstart: Approver Decision Surface

## What it does

Composes a refutation-first reading view for a human signer over one table's
committed readiness evidence: what would make you REFUSE first (blocked/warning
stages, unmet approvals, open questions -- ordered by the shipped category rank),
reassurance last. Read-only, no gate, no score. F027 approval-console still owns
the write-back.

## Run it

```
# read the refusal-first view for a table (writes nothing)
retail approver-view --table retail_store_sales

# machine-readable
retail approver-view --table retail_store_sales --format json
```

## Expected on the worked example

`retail_store_sales` is at `publish_ready` with all stages pass, recorded
approvals, and all four `unresolved-questions.md` rows `answered` (Gate CLEARED).
So the view shows an EMPTY refusal case ("nothing to refuse") and lists the
passed stages / recorded approvals / answered questions as reassurance -- with no
score. A table mid-pipeline with a blocked stage and an open governance question
would instead show those at the top of the refusal case.

## What it will NOT do

- Never grants an approval, moves a stage, or writes any file (default is a pure
  read; no write path exists in the module).
- Never computes a priority/urgency/confidence number to order by -- the order is
  the fixed shipped enum rank (approval > grain > live_validation > artifact >
  readiness), a committed lookup.
- Never emits a score, count, or percentage.
- Never adds a `retail check` rule or blocks a stage.
- Never presents a missing `unresolved-questions.md` as "no open questions" --
  it names the missing input.

## Verify

```
pytest tests/unit/test_approver_view.py tests/unit/test_blocker_explainer.py -q
```

The tests are the verifier: refusal-case COMPLETENESS (every blocked/warning/
unmet-approval/open-question item present in the refusal case, none misfiled as
reassurance), fixed-rank ordering, verbatim+cite, no-score, no-write, input-
absence honesty, generic over two tables -- PLUS a regression lock that
`blocker_explainer`'s output is byte-identical after the shared-classifier
extraction.
