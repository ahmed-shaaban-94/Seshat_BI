# Contract: `.seshat/compass.yaml` (kit router)

The machine-readable, harness-neutral router. This contract defines what a
CONSUMER (Claude Code, Codex, any agent) can rely on and what the PRODUCER
(`init` / the projection generator) must guarantee.

## Shape (illustrative)

```yaml
kit: seshat-bi
version: 0.2.0

orient:
  question_first: "What readiness stage am I serving?"
  state_lives_in: "readiness-status.yaml (per TABLE, recomputed)"
  recompute_from: [committed artifacts, "Gate status", migration presence]
  # NO current_stage field — that would be the forbidden run-state engine.

verbs:
  - id: retail-orchestrate
    purpose: conductor — sequence the medallion verbs, self-heal against the gate
  - id: first-hour-compass
    purpose: first-arrival worked-example offer + single-source seam list + single-table orientation card
  - id: retail-onboard-table
    purpose: Source→Mapping front door; owns the Stage-1 read-only DB-backed profile (grain candidates, column types)
  - id: source-mapping
    purpose: the mapping gate — produces source-map.yaml
  - id: retail-build-warehouse
    purpose: author silver/gold SQL; stop before executing
  - id: retail-validate
    purpose: live checks; needs db extra + DSN, else [PENDING LIVE PROFILE]
  - id: retail-govern
    purpose: static check (retail check)

hard_stops:
  - never_self_grant_approval
  - no_silver_before_mapping_cleared
  - no_dashboard_before_metric_contracts
  - never_fabricate_a_confidence_score

integrations: [claude, codex]
```

## Producer guarantees (MUST)

- **P1**: `compass.yaml` is a byte-exact projection of `.seshat/kit-source.yaml`
  (`verbs`, `hard_stops`, `integrations`, `orient` copied verbatim). A drift check
  MUST pass.
- **P2**: NO `current_stage` and no per-table data appear anywhere in the file.
- **P3**: The file is valid YAML, ASCII, UTF-8 no BOM, `\n` line endings.
- **P4**: `verbs[].id` values resolve to real skills present in the kit -- including
  `retail-onboard-table`, the profiling front door, so an agent reading only
  `compass.yaml` (C1) can discover where the first profile comes from.

> NOTE (verb-set delta vs design source): `distribution-ideas.md`'s sketch listed 5
> verbs and omitted `first-hour-compass` / `retail-onboard-table`. The contract adds
> both because they are the actual first-arrival + profiling front doors an agent
> must discover; this delta is recorded in research R1. The source/projection split
> earns its keep primarily via the PROSE projections (`AGENTS.md`/`CLAUDE.md`), not
> the near-identical YAML twin (research R1, MINOR-7).

## Consumer guarantees (MAY rely on)

- **C1**: Reading ONLY this file, an agent can enumerate the verbs it may drive and
  the hard-stops it must respect (SC-007).
- **C2**: The hard-stops are ORIENTATION. This file DECLARES them; it does not
  ENFORCE them. Enforcement lives in the lint rules + `G6`/`C2` gate guards. A
  consumer MUST NOT treat presence in this file as "the gate passed".
- **C3**: For work-state, the consumer MUST recompute from the per-table
  `readiness-status.yaml` named in `orient.state_lives_in` — never from this file.

## Anti-requirements (MUST NOT)

- MUST NOT store, cache, or imply a repo-level readiness stage.
- MUST NOT be a second source of truth for the verb list or hard-stops (that is
  `kit-source.yaml`).
- MUST NOT contain secrets, hosts, or DSNs.
