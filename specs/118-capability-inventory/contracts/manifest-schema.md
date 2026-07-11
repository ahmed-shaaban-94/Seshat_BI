# Contract: Capability Manifest (`docs/capabilities/capabilities.yaml`)

The single committed, hand-authored authority for capability CLASSIFICATION. Closed enums;
no run-state; no numeric scores. Owns only gap fields; references feeder facts.

## Shape

```yaml
# docs/capabilities/capabilities.yaml
version: 1
capabilities:
  - id: retail-check                      # stable kebab-case slug; sort key
    name: "retail check"
    summary: "Static governance gate over committed TMDL/PBIR/SQL/git text."
    state: shipped                        # shipped | spec-only | deferred
    authority: agent-runnable             # agent-runnable | advisory | human-gated
    surface: cli                          # cli | skill | execution-adapter | plugin | docs | human-artifact
    requirements: []                      # [] | [database] | [optional-dependency] | [database, optional-dependency]
    provenance: publicly-released         # locally-verified | publicly-released | unrecorded
    readiness_stage: not-stage-scoped     # a stage name | not-stage-scoped
    command: "retail check"               # a wired _DISPATCH key, or null
    documentation: "docs/rules/README.md" # existing repo-relative path
    references:                           # feeder pointers the oracle reconciles
      dispatch: "check"                   # => positive shipped signal (wired command)

  - id: dbt-transformation-adapter
    name: "dbt advisory adapter"
    summary: "Advisory dbt transformation adapter (not connected)."
    state: shipped
    authority: advisory
    surface: execution-adapter
    requirements: []
    provenance: locally-verified
    readiness_stage: not-stage-scoped
    command: null
    documentation: ".claude/skills/dbt-transformation-adapter/SKILL.md"
    references:
      roadmap: "F029"                     # => positive shipped signal (roadmap SHIPPED)
      skill: "dbt-transformation-adapter" # frontmatter'd SKILL.md

  - id: f016-powerbi-execution-adapter
    name: "F016 Power BI execution adapter"
    summary: "Materialize/publish an approved model to Power BI."
    state: deferred
    authority: agent-runnable
    surface: execution-adapter
    requirements: [optional-dependency]
    provenance: unrecorded
    readiness_stage: not-stage-scoped
    command: null
    documentation: "docs/quality/parked-on.yaml"   # its parked/deferred record
    references:
      parked_on: "F016"
```

## Field rules (the closed contract)

- **`id`**: required, unique, kebab-case. Determinism sort key.
- **`state`**: LIFECYCLE only -- `shipped` | `spec-only` | `deferred`. Authority values
  (advisory/human-gated) and provenance values NEVER go here (FR-005).
- **`authority`**: `agent-runnable` | `advisory` | `human-gated`.
- **`surface`**: `cli` | `skill` | `execution-adapter` | `plugin` | `docs` | `human-artifact`.
- **`requirements`**: list, possibly empty, of `database` | `optional-dependency`.
- **`provenance`**: `locally-verified` | `publicly-released` | `unrecorded`. Default
  `unrecorded`. `publicly-released` requires a committed release-evidence reference.
- **`readiness_stage`**: a valid snake_case stage token -- one of the `stages.*` keys of
  `templates/readiness-status.yaml` (the single canonical source: `source_ready` ...
  `publish_ready`) -- or `not-stage-scoped` (default).
- **`command`**: a wired `_DISPATCH` key or `null`.
- **`documentation`**: an existing repo-relative path (checked).
- **`references`**: optional map of feeder -> key that the oracle reconciles. Recognized
  feeders: `dispatch`, `skill`, `rules_manifest`, `verb` (kit-source), `roadmap`,
  `status_claims`, `parked_on`.

## Invariants (fail-closed)

1. `state: shipped` REQUIRES a `references` entry that resolves to a positive ship signal.
   No positive signal => INVALID (a spec-dir existing is NOT a signal).
2. `provenance: publicly-released` REQUIRES a committed release-evidence reference.
3. No field may be a number expressing maturity/confidence/completeness/health.
4. The manifest stores NO `current_stage` / per-table run-state (it is not a readiness file).
