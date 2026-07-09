# Contract: Approver Decision Surface composer + CLI verb

## Shared classifier (extracted first -- D1/D2)

`src/retail/readiness_classify.py`

```
def classify(reason: str) -> tuple[str, str, str]   # (category, explanation, next_surface)
```

- Holds `_CATEGORY_RULES` + `_DEFAULT_CATEGORY` moved verbatim from
  `blocker_explainer.py`. `blocker_explainer` imports `classify` (and the rules
  tuple if it needs the rank) instead of its own module-private copy.
- Behavior-preserving: `test_blocker_explainer.py` MUST stay green with output
  byte-identical (V9).

## Python API

`src/retail/approver_view.py`

```
def build_approver_view(repo_root: Path | str, table: str) -> dict
```

- **Reads**: `<repo>/mappings/<table>/readiness-status.yaml` and
  `<repo>/mappings/<table>/unresolved-questions.md` ONLY (via the shipped
  `_load_yaml_mapping` idiom for the YAML; a small committed-markdown-table
  parser for the Open-questions table).
- **Returns** the ApproverView dict (data-model.md):
  ```
  {
    "table": str,
    "refusal_case": [ {kind, category, rank, reason, source, owner?}, ... ],  # rank-ordered
    "reassurance": [ {kind, detail, source}, ... ],
    "missing_inputs": [str, ...],
    "read_only_proof": True,
  }
  ```
- **Writes**: NOTHING. `render_view(view) -> str` produces the ASCII reading
  view; the default CLI path PRINTS it. NO file-write call exists in the module
  (FR-006, V6).
- **Never**: opens a DB/network/PBIP connection; imports a driver at module load;
  mutates any artifact; grants an approval; moves a stage; emits a score.

## Rendered view shape (ASCII, UTF-8 no BOM)

```
# Approver Decision Surface -- <table>

Read this before you sign. It re-orders committed readiness evidence:
what would make you REFUSE first, reassurance last. It records nothing,
grants no approval, and moves no stage.

## What would make you refuse (top = weigh first)

1. [approval] <stage> -- no valid recorded approval for this stage
   (mappings/<table>/readiness-status.yaml stages.<stage> / approvals[]).
2. [approval] OPEN question <ID> (owner: governance) -- "<question text>"
   (mappings/<table>/unresolved-questions.md).
3. [grain] <stage> blocked -- "<blocking_reason verbatim>"
   (mappings/<table>/readiness-status.yaml stages.<stage>.blocking_reasons).
4. [readiness] <stage> warning -- "<reason verbatim>" (...).

<or, when the refusal case is empty:>
## What would make you refuse

Nothing in the refusal case: no blocked or warning stage, no unmet approval,
no open question was found in the committed evidence.

## Reassurance (recorded positives)

- <stage> pass (evidence recorded).
- Approval recorded: <stage> by <owner> at <at>.
- Question <ID> answered.

<if an input was missing:>
## Inputs not available

- mappings/<table>/unresolved-questions.md not found -- open questions could
  NOT be read (this is NOT the same as "no open questions").
```

Rules: order by fixed enum rank then lexical tie-break; every line quotes its
committed source verbatim + cites location; NO numeric token anywhere; ASCII
`--`/`->`.

## CLI verb

`src/retail/cli/commands/approver_view.py` (mirrors `commands/blockers.py`):

```
retail approver-view --table <table> [--format text|json]
```

- Default `--format text` prints the rendered view; `--format json` prints the
  `build_approver_view` dict.
- No `--write` in the MVP (D5); default is a pure read. Returns exit `0` always
  (not a gate; FR-007). A missing input yields a `missing_inputs[]` note, not a
  non-zero exit.
- Registered in `cli/parser.py` and the CLI dispatch table, mirroring the shipped
  `blockers`/`next` wiring.

## Non-gating verifier (tests, D3)

`tests/unit/test_approver_view.py` -- asserts V1-V9 (data-model.md), centered on
REFUSAL-CASE COMPLETENESS (V1/V2), not just ordering. NO `@register` retail check
rule; NO rules-manifest change (FR-007).
