# Data Model: Approver Decision Surface

Phase 1. The composer's in-memory model. All fields are READ from two committed
files; none is authored, none is written.

## Inputs (read-only)

- `mappings/<table>/readiness-status.yaml`:
  - `current_stage` (str)
  - `stages{}` -- per stage: `status` (`not_started`|`blocked`|`warning`|`pass`),
    `evidence[]`, `blocking_reasons[]`.
  - `approvals[]` -- each `{stage, owner, at}` (validity via the shipped
    `readiness_status` owner check).
  - top-level `blocking_reasons[]` (status-level).
- `mappings/<table>/unresolved-questions.md`:
  - the Open-questions table rows -- each with `ID`, `Question`, `Who must
    answer`, `Status`, `Resolution`. OPEN = `Status` not `answered`.

## Shared classifier (extracted, D1/D2)

`src/retail/readiness_classify.py`: `classify(reason) -> (category, explanation,
next_surface)` over the fixed `_CATEGORY_RULES` enum (approval > grain >
live_validation > artifact > readiness) + `_DEFAULT_CATEGORY`. Moved verbatim
from `blocker_explainer.py`; both modules import it.

## Entities

### RefutationItem

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `table` | str | readiness-status `table`/dir | |
| `source` | str | which file + stage/row | cited location |
| `category` | enum | `classify()` (blockers) OR owner-map (questions) | fixed rank; never computed |
| `rank` | int | index of `category` in the fixed enum order | a LOOKUP, not a score |
| `reason` | str | verbatim `blocking_reasons[]` entry / question text | never paraphrased |
| `owner` | str \| None | `unresolved-questions` `Who must answer` | questions only |
| `kind` | enum | `blocked_stage`\|`warning_stage`\|`unmet_approval`\|`open_question` | |

**Refusal-eligibility (D4):** an item is refusal-eligible iff its stage status is
`blocked` or `warning`, OR it is an approval-requiring stage with no valid
`approvals[]` entry, OR it is an OPEN `unresolved-questions.md` row. Question
category by `Who must answer`: governance/data-owner -> `approval`; analyst ->
`classify(question_text)` restricted to grain/readiness; unknown -> `readiness`.

### ReassuranceItem

| Field | Type | Source |
|-------|------|--------|
| `kind` | enum: `pass_stage`\|`valid_approval`\|`answered_question` | |
| `detail` | str | verbatim (stage name / approval {stage,owner,at} / answered Q id) |
| `source` | str | cited location |

### ApproverView (output model)

| Field | Type | Notes |
|-------|------|-------|
| `table` | str | |
| `refusal_case[]` | RefutationItem | ordered by `rank` asc, then the shipped lexical tie-break (stable) |
| `reassurance[]` | ReassuranceItem | shown last; never scored |
| `missing_inputs[]` | str | named missing/unreadable input paths (FR-010) |
| `read_only_proof` | bool (always true) | mirrors blocker_explainer |

## State transitions

None -- pure compose. Reads current committed files each run; writes nothing by
default (D5).

## Validation rules (enforced by the verifier tests, D3)

- V1 (refusal completeness -- SAFETY): every refusal-eligible source item
  (blocked/warning reason, unmet approval, open question) appears exactly once in
  `refusal_case[]`. NONE is dropped (FR-001, SC-001/SC-005).
- V2 (correct side): no refusal-eligible item appears in `reassurance[]`, and no
  `pass`/valid-approval/`answered` item appears in `refusal_case[]` (D3/D4).
- V3 (fixed-rank order): `refusal_case[]` is ordered by the enum rank
  (approval > grain > live_validation > artifact > readiness), ties broken
  lexically (stable, deterministic); no `rank` is a computed value (FR-002/FR-012).
- V4 (verbatim + cite): every item reproduces its committed reason/question text
  verbatim and cites its source location (FR-005, SC-004).
- V5 (no score): output contains no numeric score/count/percentage (FR-008, SC-002).
- V6 (no write): `approver_view` contains no file-write call; a default run
  changes no tracked file (FR-006, SC-003) -- grep- + git-status-verifiable.
- V7 (input absence): a missing input is named in `missing_inputs[]`, never
  silently treated as "nothing to refuse" (FR-010).
- V8 (generic): same composer over two distinct tables, no per-table branch
  (FR-011, SC-006).
- V9 (regression lock): `blocker_explainer`'s output is byte-identical after the
  classifier extraction (D2).
