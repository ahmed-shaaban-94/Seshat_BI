# Phase 1 Data Model: `retail init`

The "entities" here are file shapes and the fence contract, not database tables
(`init` opens no DB). Each shape lists its fields, invariants, and the requirement
it serves.

## E1. Canonical kit source — `.seshat/kit-source.yaml`

The single source of truth all projections derive from. Downstream of the
constitution.

| Field | Type | Notes |
|-------|------|-------|
| `kit` | string | kit id, e.g. `seshat-bi` |
| `version` | string | kit version (semver); the projection stamps this into `compass.yaml` |
| `verbs[]` | list | each `{ id, purpose }` — the agent-driven helper skills |
| `hard_stops[]` | list | orientation-only flags the agent READS (never enforced by this file) |
| `integrations[]` | list | harness ids whose projections are generated (`claude`, `codex`) |
| `orient` | object | `{ question_first, state_lives_in, recompute_from[] }` |

**Invariants**:
- MUST NOT contain a `current_stage` or any per-table run-state (FR-005).
- `verbs[]` and `hard_stops[]` are the ONLY source; `compass.yaml` copies, never
  re-declares (FR-015, anti-fork).
- ASCII, UTF-8 no BOM, `\n` (FR-014).

## E2. Projection — `.seshat/compass.yaml` (kit router)

A generated projection of E1. Harness-neutral; buys Codex/Claude parity.

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `kit` | string | E1.kit | verbatim |
| `version` | string | E1.version | verbatim |
| `orient` | object | E1.orient | protocol only; POINTS AT `readiness-status.yaml` |
| `verbs[]` | list | E1.verbs | verbatim; MUST include `first-hour-compass` (first-arrival) + `retail-onboard-table` (profiling front door) so the agent can discover them (SC-007) |
| `hard_stops[]` | list | E1.hard_stops | verbatim; DECLARES, does not ENFORCE |
| `integrations[]` | list | E1.integrations | which projections exist |

**Invariants**:
- `compass.yaml == project(kit-source.yaml)` byte-for-byte (drift check, SC-004).
- No `current_stage` field (structural check, SC-004).
- An agent reading ONLY this file can enumerate verbs + hard-stops (SC-007).

## E3. Fenced generated region (in `AGENTS.md` / `CLAUDE.md`)

| Element | Value |
|---------|-------|
| Start marker | `<!-- SESHAT-KIT START -->` |
| End marker | `<!-- SESHAT-KIT END -->` |
| Body | a prose projection of E1 (verbs + hard-stops + the orient protocol) |
| Outside-fence | hand-authored / constitution-owned; NEVER touched |

**Invariants**:
- Exactly ONE fenced region per file (idempotent; no duplicate on re-run, FR-008).
- Every byte OUTSIDE the fence is identical before/after `init` (SC-002, FR-006).
- Distinct from the existing `SPECKIT` fence — never collides.
- If markers are absent, insert one fresh block safely or STOP (never rewrite the
  file). NOTE: `AGENTS.md` has NO fence today, so first-run insertion there is the
  normal path (not an edge case); the fence body is human-reviewed at ratify until
  the Phase-2 source-vs-constitution drift check lands (MINOR-5).
- The fence-body drift check is a PROSE render-and-compare
  (`fenced_body == render_prose(kit-source.yaml)`), NOT a byte-vs-YAML compare — a
  DIFFERENT mechanism from E2's byte-exact YAML projection (MINOR-6).

## E4. Kit manifest — `.seshat/manifest.yaml` + `.seshat/integrations/*.json`

| Field | Type | Notes |
|-------|------|-------|
| `files[]` | list | `{ path, checksum }` for each kit file (integrity receipt) |
| `integrations/<harness>.json` | file | per-harness `{ files[], checksum }` — speckit's good part |

**Invariants**:
- Derived evidence only (Maintenance Automation); creates no truth, self-approves
  nothing.
- Checksums recompute deterministically from committed content.

## E5. Per-table readiness state — `readiness-status.yaml` (EXISTING, referenced)

`init` READS/POINTS AT this; it writes nothing here and duplicates no field. It is
the authoritative per-table work-state (`current_stage`, per-stage `status`,
`evidence[]`, `blocking_reasons[]`, `approvals[]`). Listed so the model is complete;
owned by the existing readiness system, not this feature.

## State transitions

`init` itself is (near-)stateless per run:

```text
[no .seshat/]        --init-->  [bootstrapped: substrate written, fence present]
[bootstrapped]       --init-->  [bootstrapped: fenced regions re-projected; "already bootstrapped"]
[partial bootstrap]  --init-->  [reconciled: missing pieces completed, or STOP if unsafe]
```

No transition writes a readiness stage or an approval. The visible first-run RESULT
(grain candidates + column types) is produced by the delegated verbs, not stored by
`init`.
