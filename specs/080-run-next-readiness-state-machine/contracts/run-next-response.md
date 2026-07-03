# Contract: The Run-Next Response Shape

This is the one contract this feature exposes: given a single table's
committed `readiness-status.yaml` (or its absence), the response this feature
returns. There is no HTTP/RPC surface in this slice -- the "contract" is the
field shape an agent-facing skill (or a future thin Python helper) must
produce consistently, so any future caller (a human, `retail-orchestrate`, a
test fixture) can rely on it.

## Request (conceptual)

| Input | Type | Required | Notes |
|-------|------|----------|-------|
| `table` | string (e.g. `<schema>.<table>` id, matching the readiness-status `table` field) | yes | identifies which `mappings/<table>/readiness-status.yaml` to read |
| readiness-status file content | the file at `mappings/<table>/readiness-status.yaml`, if present | n/a (read from disk, not passed as a parameter) | absence is a valid, handled case (FR-011), not an error |

There is no other input. No DSN, no live query, no flags that change
behavior in a way that could produce a different answer for the same
committed file (determinism: same file in, same response out, every time).

## Response

```yaml
table: "<schema>.<table>"
outcome: "next_action"          # one of: next_action | stop_blocked | approval_required | terminal_pass | input_defect
stage: "<stage_key>"            # the stage this outcome concerns; null only for terminal_pass
action_text: "<string or null>" # populated only when outcome == next_action
blocking_reasons: []            # populated only when outcome == stop_blocked; verbatim from source
required_authority: null        # populated only when outcome == approval_required
caveats: []                     # zero or more {kind, detail} objects; always present, may be empty
read_only_proof: true           # always true; this invocation wrote nothing
```

### `outcome` values (mutually exclusive; exactly one per response)

| Value | When it applies | What else is populated |
|-------|------------------|--------------------------|
| `next_action` | earliest non-`pass` stage is `not_started` or `warning`, and any PRIOR approval-required stage's approval is present and shape-valid | `stage`, `action_text`, possibly a `warning_carried_forward` caveat |
| `stop_blocked` | earliest non-`pass` stage is `blocked` | `stage`, `blocking_reasons` (verbatim, non-empty) |
| `approval_required` | earliest non-`pass` stage (or the stage just walked past) is `pass` but its required `approvals[]` entry is missing or shape-invalid | `stage`, `required_authority` |
| `terminal_pass` | all seven stages are `pass` with all required approvals present and shape-valid | `stage: null`; `caveats[]` may still carry `pass_without_evidence` entries accumulated along the way |
| `input_defect` | the file is missing, malformed, or contains an unrecognized stage-status value that blocks determining stage order past that point | `stage` names the first stage where the defect was found (or `null` if the defect is file-level, e.g. missing file / unparseable YAML) |

### `caveats[]` entry shape

```yaml
- kind: "pass_without_evidence"       # | "next_action_disagreement" | "warning_carried_forward" | "dual_blocked"
  detail: "<human-readable explanation, citing the specific stage/field>"
```

| `kind` | Fires when | Corresponding requirement |
|--------|------------|-----------------------------|
| `pass_without_evidence` | any stage recorded `pass` has empty `evidence[]` | FR-009 |
| `next_action_disagreement` | the file's stored `next_action` string names a materially different stage/action than the one computed | FR-010 |
| `warning_carried_forward` | the earliest non-`pass` stage is `warning` (not blocking, but not silently dropped) | Edge case: "warning status on the current stage" |
| `dual_blocked` | more than one stage is `blocked`; only the earliest is the `stage` in the outcome, but this caveat names the later one(s) too | Edge case: "two stages both blocked" |

## Guarantees (the contract's non-negotiable properties)

1. **Read-only**: `read_only_proof` is always `true`, and it is true because
   the implementation performs zero writes -- not because the field is
   asserted without being backed by actual behavior. A future
   implementation's test suite MUST verify `git status --short` is empty
   after invocation (SC-003), not just that the field says so.
2. **No numeric score anywhere in the response** -- no field of type number
   represents confidence, health, or percent-ready (SC-004). `required_authority`
   and `outcome` are enums (strings), not scores.
3. **Determinism**: the same committed `readiness-status.yaml` content always
   produces the same response. No randomness, no time-of-day dependency (a
   caveat MAY mention a date found in the file, e.g. an `approvals[].at`
   value, but the OUTCOME never depends on the current wall-clock date).
4. **Exactly one `outcome`**: never zero, never more than one. When more than
   one stage is non-cleared (e.g. one stage is `blocked` AND another stage is a
   mislabeled `pass` missing its approval), the response is the outcome of the
   **EARLIEST such stage in walk order** -- position alone decides. Whichever
   stage the front-to-back walk reaches first determines the outcome: if that
   earliest stage is a mislabeled-`pass`, the outcome is `approval_required`; if
   it is `blocked`, the outcome is `stop_blocked`. Outcome TYPE never overrides
   walk position (there is NO rule that `stop_blocked` outranks `approval_required`
   regardless of position). This matches the "walk front-to-back, stop at the
   first wall" model in spec.md's edge cases and the data-model walk.
5. **Traceability**: every non-null field in the response can be traced to an
   exact field in the source `readiness-status.yaml` (or, for `action_text`,
   to the corresponding stage doc's "Next allowed action" text) -- never an
   invented value (FR-014).

## Worked examples

### Example A: forward action, no complications

Input (`mappings/example_table/readiness-status.yaml` excerpt):
```yaml
stages:
  source_ready: { status: pass, evidence: ["mappings/example_table/source-profile.md"] }
  mapping_ready: { status: not_started }
  ...
```

Response:
```yaml
table: "silver.example_table"
outcome: "next_action"
stage: "mapping_ready"
action_text: "Begin Mapping Ready (Stage 2) -- the source-mapping gate."
blocking_reasons: []
required_authority: null
caveats: []
read_only_proof: true
```

### Example B: blocked stage

Input excerpt:
```yaml
stages:
  mapping_ready: { status: blocked, blocking_reasons: ["grain not confirmed unique on data"] }
```

Response:
```yaml
table: "silver.example_table"
outcome: "stop_blocked"
stage: "mapping_ready"
action_text: null
blocking_reasons: ["grain not confirmed unique on data"]
required_authority: null
caveats: []
read_only_proof: true
```

### Example C: approval missing (shape-invalid owner)

Input excerpt:
```yaml
stages:
  semantic_model_ready: { status: pass, evidence: ["powerbi/model.tmdl"] }
approvals:
  - stage: "semantic_model_ready"
    owner: "metric_owner"     # bare role token -- fails RS1's shape check
    at: "2026-07-01"
```

Response:
```yaml
table: "silver.example_table"
outcome: "approval_required"
stage: "semantic_model_ready"
action_text: null
blocking_reasons: []
required_authority: "metric_owner"
caveats: []
read_only_proof: true
```

### Example D: terminal pass with a carried caveat

Input: all seven stages `pass`, all approvals shape-valid, but
`gold_ready.evidence` is `[]`.

Response:
```yaml
table: "silver.example_table"
outcome: "terminal_pass"
stage: null
action_text: null
blocking_reasons: []
required_authority: null
caveats:
  - kind: "pass_without_evidence"
    detail: "stage 'gold_ready' is pass but evidence[] is empty"
read_only_proof: true
```

### Example E: missing file

Input: `mappings/new_table/readiness-status.yaml` does not exist.

Response:
```yaml
table: "silver.new_table"
outcome: "next_action"
stage: "source_ready"
action_text: "No readiness file found; start onboarding at Source Ready."
blocking_reasons: []
required_authority: null
caveats: []
read_only_proof: true
```
