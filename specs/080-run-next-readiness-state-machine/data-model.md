# Phase 1 Data Model: Run-Next Readiness State Machine

This feature introduces **no new persisted schema**. It reads two existing
artifact shapes and produces one ephemeral, non-persisted response shape. This
document names each entity's fields as THIS feature consumes/produces them --
it is a consumption map, not a schema owner.

## Entity 1: Readiness Status (existing, read-only input)

**Owner**: `templates/readiness-status.yaml` (ADR 0004). This feature does not
own, version, or modify this schema.

**Source instance location**: `mappings/<table>/readiness-status.yaml`.

| Field | Type | Used by this feature for |
|-------|------|---------------------------|
| `table` | string | identifying which table the response is about (echoed back, never altered) |
| `current_stage` | one of 7 stage keys | cross-check ONLY (FR-002); never the computation source |
| `stages.<stage_key>.status` | one of `not_started`/`blocked`/`warning`/`pass` | the stage-order walk (FR-002..FR-005) |
| `stages.<stage_key>.evidence[]` | list of strings | pass-without-evidence flag (FR-009) |
| `stages.<stage_key>.blocking_reasons[]` | list of strings | verbatim STOP text (FR-004) |
| `approvals[]` (each: `{stage, owner, at}`) | list of objects | approval-shape check (FR-005, FR-015), citing RS1's rule |
| `next_action` | string | disagreement check against the freshly computed action (FR-010) |

**Stage-key order this feature fixes** (FR-002; matches
`docs/readiness/readiness-pipeline.md` and RS1's `_STAGE_ORDER`):

1. `source_ready`
2. `mapping_ready`
3. `silver_ready`
4. `gold_ready`
5. `semantic_model_ready`
6. `dashboard_ready`
7. `publish_ready`

**Approval-required subset** (FR-005; matches RS1's `_APPROVAL_REQUIRED` plus
its file-source special case):

- `mapping_ready` (always)
- `semantic_model_ready` (always)
- `dashboard_ready` (always)
- `publish_ready` (always)
- `source_ready` (only when that stage's block declares a file
  `source_kind` in `{csv, tsv, excel}` per RS1's `_FILE_SOURCE_KINDS`/alias
  table)

**Validity rules this feature checks before trusting the file** (FR-012):

- File exists and is parseable UTF-8-sig YAML.
- Top-level is a mapping.
- `stages` key exists and is a mapping.
- Each present stage block is itself a mapping with a `status` in the
  recognized four-value set.

A file failing any of these does not raise an unhandled error; it produces a
"readiness file incomplete/unparseable" response (see Entity 3) naming the
specific defect.

## Entity 2: Stage Doc (existing, read-only reference input)

**Owner**: `docs/readiness/<stage>-ready.md`, one file per stage (7 total).

| Field (informal section) | Used by this feature for |
|---------------------------|---------------------------|
| "Next allowed action" | phrasing the forward-action text this feature returns for a `not_started`/`warning` stage |
| "Required owner / approval" | confirming WHICH stages require a named-human approval, and what authority class is expected (analyst/governance/data_owner/metric_owner) |

This feature reads these docs as fixed reference vocabulary; it does not
parse them programmatically in this slice (a future Python helper, if built,
could hardcode the mapping the same way RS1 hardcodes `_APPROVAL_REQUIRED`
rather than re-parsing Markdown at call time -- see plan.md R6 / research.md).

## Entity 3: Run-Next Response (this feature's sole output; NOT persisted)

This is the shape this feature produces. It is never written to disk by this
feature; it is returned to whatever invoked it (an agent turn, a future
caller). See `contracts/run-next-response.md` for the full field-by-field
contract and worked examples.

| Field | Type | Always present? | Notes |
|-------|------|------------------|-------|
| `table` | string | yes | echoed from the input file, or the requested table id if the file is missing |
| `outcome` | enum: `next_action` \| `stop_blocked` \| `approval_required` \| `terminal_pass` \| `input_defect` | yes | exactly one; mutually exclusive |
| `stage` | one of the 7 stage keys, or `null` | yes | the stage the outcome concerns; `null` only for `terminal_pass` |
| `action_text` | string, or `null` | only for `outcome=next_action` | drawn from that stage's "Next allowed action" doc text |
| `blocking_reasons` | list of strings | only for `outcome=stop_blocked` | copied verbatim from the source file |
| `required_authority` | one of the four RS1 authority classes, or `null` | only for `outcome=approval_required` | which class of named human must sign off |
| `caveats[]` | list of caveat objects (`{kind, detail}`) | always (may be empty) | `kind` in `{pass_without_evidence, next_action_disagreement, warning_carried_forward, dual_blocked}` |
| `read_only_proof` | boolean | yes | always `true`; asserts this invocation wrote nothing (see Safety Constraints in spec.md) |

## Relationships

```text
mappings/<table>/readiness-status.yaml  (Entity 1, read)
        |
        |  stage-order walk (fixed order, FR-002)
        v
   [earliest non-pass stage found]
        |
        |  cross-referenced against
        v
docs/readiness/<stage>-ready.md          (Entity 2, read, reference vocabulary)
        |
        |  produces
        v
   Run-Next Response                     (Entity 3, ephemeral output)
```

No entity in this feature is created, updated, or deleted on disk. Entities 1
and 2 are Core Authority artifacts owned elsewhere; Entity 3 exists only for
the duration of one invocation's response.

## State Transitions (conceptual only -- NOT a persisted state machine)

This is the "state machine" the feature name refers to: a pure function from
(Entity 1 snapshot) to (Entity 3 response), re-evaluated fresh every time,
with no memory of prior invocations.

```text
for stage in [source_ready, mapping_ready, silver_ready, gold_ready,
              semantic_model_ready, dashboard_ready, publish_ready]:
    if stage.status is invalid:
        return input_defect(stage)
    if stage.status == "blocked":
        return stop_blocked(stage, stage.blocking_reasons)
    if stage.status in ("not_started", "warning"):
        if stage requires an approval FOR THIS stage to be entered
           (i.e. the PRIOR stage's approval, if prior stage is approval-required)
           and that approval is missing/shape-invalid:
            return approval_required(prior_stage)
        return next_action(stage, caveats=[warning_carried_forward if applicable])
    # status == "pass":
    if stage.evidence is empty:
        record caveat pass_without_evidence(stage)
    if stage in APPROVAL_REQUIRED and no shape-valid approval:
        return approval_required(stage)
    # else: continue to next stage in the loop
# loop completed without returning => every stage is pass
return terminal_pass(caveats=accumulated)
```

This pseudocode is illustrative for the data model only; it is NOT a
committed implementation in this slice (Non-Goal: no code this slice). A
future implementation slice (Python helper or pure agent-procedure) must
preserve this exact walk order and these exact stop conditions, matching
spec.md FR-002 through FR-012.
