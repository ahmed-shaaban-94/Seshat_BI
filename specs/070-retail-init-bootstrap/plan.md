# Implementation Plan: `retail init` Bootstrap-to-First-Result (Compass-Driven Phase-1)

**Branch**: `070-retail-init-bootstrap` | **Date**: 2026-07-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/070-retail-init-bootstrap/spec.md`

## Summary

Add an agent-invokable `init` workflow SKILL that bootstraps a repo for the
Compass-Driven kit and ends the first-run flow on a VISIBLE result from the user's
own table WHEN A LIVE DB IS REACHABLE (or the orientation structure + `[PENDING LIVE
PROFILE]` otherwise). The AGENT performs the delegate/route/profile behavior (those
are prose skills, not importable functions); the SKILL DELEGATES the first-arrival
worked-example offer to the existing `first-hour-compass` (anti-fork) and ROUTES into
the existing `first-hour-compass` -> `retail-onboard-table` verbs (the onboarding
verb owns the Stage-1 DB-backed profile). The Python surface is substrate-writing
ONLY: it writes `.seshat/compass.yaml` (kit router), the fenced `SESHAT-KIT` regions
of `AGENTS.md` / `CLAUDE.md`, and the kit manifests -- it never profiles, opens a DB,
prompts, or shows a menu (a `retail init` CLI writes substrate + prints the next
agent step, the `scaffold.py` write/print precedent). It stores no run-state, writes
only inside a delimited fence, self-grants nothing, and fetches from no remote.
Technical approach: a docs-first **Official Workflow Skill** (SKILL.md) plus a thin
projection generator + drift checker (the `compass.yaml`/fence writers), mirroring
how `scaffold.py` / `manifest.py` / `severity_posture.py` sit outside the readiness
stage sequence. The projection module MAY import `pyyaml` lazily (like
`semantic-check` / `value-check`); only the `retail check` core stays stdlib-only.

## Technical Context

**Language/Version**: Python 3.13+ (matches `pyproject.toml`). The projection
generator MAY import `pyyaml` LAZILY to parse `kit-source.yaml` and run the drift
check (same pattern as `retail semantic-check` / `value-check`); `pyyaml` is already
in the `dev` extra. Only the `retail check` static core stays stdlib-only -- this
feature adds no rule to that core.

**Primary Dependencies**: No NEW dependency. The `init` SKILL.md is prose the AGENT
performs, composing existing skills (`first-hour-compass`, `retail-onboard-table`,
and, for later stages, `retail-orchestrate` / `source-mapping`). No DB driver in the
`init` module (profiling is agent-routed into the existing verbs, which own the `db`
extra boundary).

**Storage**: Files only. Writes `.seshat/compass.yaml`, `.seshat/manifest.yaml`,
`.seshat/integrations/*.json`, and the fenced regions of `AGENTS.md` / `CLAUDE.md`.
Reads the canonical kit source + per-table `readiness-status.yaml` (points at, never
duplicates). No database.

**Testing**: pytest (unit); the same gate CI runs (`retail check`). New unit tests
cover: fence idempotency (no duplicate fence, byte-identical outside-fence),
`compass.yaml` has no `current_stage`, projection-matches-source drift, and the
deferred-live-boundary path.

**Target Platform**: Cross-platform CLI + agent skill; Windows-safe (UTF-8 no BOM,
`\n`, 260-char path limit).

**Project Type**: CLI + agent workflow skill (single project; `src/retail/` +
`.claude/skills/`), matching the existing kit layout.

**Performance Goals**: N/A (bootstrap runs once; no hot path). Idempotent re-run is
O(files touched), trivial.

**Constraints**: MUST NOT store run-state; MUST write only inside the `SESHAT-KIT`
fence; MUST NOT touch constitution-owned regions; the `init` module MUST NOT open a
DB connection, profile, prompt, show a menu, or fetch from a remote; MUST NOT emit a
confidence score; MUST NOT fork the `first-hour-compass` worked-example offer or its
seam list. The visible profile result is agent-routed over a live DB, not produced
by the `init` module.

**Scale/Scope**: One new SKILL.md, one small generator module (+ its fence
writer/reader), one canonical source file, and the projected artifacts. No changes
to the readiness stage engine (there is none) and no new `retail check` rule in this
slice (a projection-drift linter is Phase-2 backstage, spec'd separately).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

- **Principle I (Agent-First, Gate-Enforced)**: PASS. `init` is a workflow SKILL the
  agent performs -- NOT a terminal wizard. The delegate/route/profile flow is the
  agent executing prose skills; the Python/CLI surface only writes substrate + prints
  the next step (never prompts, menus, or a profile), so it never becomes a
  terminal-first product. It declares hard-stops as orientation but ENFORCES nothing
  new -- enforcement stays with the existing `@register` lint rules + `G6`/`C2` guards
  + gate exit code (FR-001, FR-005, spec "DECLARES, does not ENFORCE").
- **Principle II (Depend, Never Fork / Execution Adapter last & gated)**: PASS. `init`
  does not fetch from any remote and does not auto-execute pulled content (FR-011);
  kit self-update (`sync`) and channel-driven fetch are later, gated slices. `init`
  touches only the local repo working set.
- **Principle IV (Mapping gate before silver)**: PASS. `init` routes into profiling
  (Source/Mapping front door) and never authors `silver.*` or clears the mapping
  gate; the hard-stop is declared, the existing verbs enforce it.
- **Principle V (Agent Stops at Judgment Calls)**: PASS. `init` self-grants no
  approval, writes no `approvals[]`, and surfaces the human seams up front as STOP
  points using `first-hour-compass`'s single-source list (FR-009, FR-010) -- it keeps
  no divergent seam list of its own. It delegates the worked-example judgment to
  `first-hour-compass`, which also stops at those seams.
- **Principle VII (C086 Is An Example, Not The Schema)**: PASS. The worked examples
  are presented (via `first-hour-compass`) as narrative patterns to steer by, never
  copied as file templates (FR-013); `init` bakes in no C086 specifics.
- **Principle VIII (Static-First Governance)**: PASS. The `init` module does no DB,
  no network, no execution. It MAY import `pyyaml` lazily to parse the canonical
  source + run the drift check (same pattern as `semantic-check` / `value-check`);
  the `retail check` static CORE stays stdlib-only and this feature adds no rule to
  it. Live profiling is DELEGATED to the existing verbs, which own the DB boundary and
  its deferred mode (FR-003, FR-012).
- **Principle IX (Secrets / Reproducibility / Windows-safe)**: PASS. Authored files
  are UTF-8 no BOM, `\n`, ASCII, short paths (FR-014). `init` never writes a real
  host/secret; the fence never captures `.env` content.
- **Hard rule #8 (templates/docs first, automate after artifacts prove useful)**:
  PASS. The orientation spine already exists in prose (`COMPASS.md`) and the verbs
  exist; `init` is a thin bootstrap/projection over a proven shape, and the
  distribution model was hand-authored + adversarially reviewed first
  (`distribution-ideas.md`).
- **Hard rule #9 (no fabricated confidence score)**: PASS. `init` emits no numeric
  health / confidence / percent-ready score (FR-010); orientation is verbs +
  hard-stops + the explicit statuses read from per-table state.
- **Constitution-amendment safety (AGENTS.md / CLAUDE.md are governed artifacts)**:
  PASS for outside-fence invariance -- `init` writes ONLY inside the `SESHAT-KIT`
  fence (FR-006) and every line outside is byte-identical (SC-002, FR-007). CAVEAT:
  `AGENTS.md` has NO fence today (only repo `CLAUDE.md` does), so first-run insertion
  of generated governance prose into a governed file is the normal path, not an edge
  case; the source-vs-constitution drift check that would make the in-fence content
  amendment-verified is deferred to the Phase-2 drift linter. Until then the fence
  BODY is human-reviewed at ratify. This does not route any change around the
  amendment procedure (only fenced content changes), but the "verified-safe" claim is
  scoped to outside-fence invariance, not the fence body's content.
- **Anti-fork discipline (one source of truth)**: PASS. `init` delegates the
  first-arrival offer to `first-hour-compass` (FR-002, SC-008) and points at
  per-table `readiness-status.yaml` for state (FR-005) rather than restating either.
  `compass.yaml` is a PROJECTION of one canonical source (FR-015).
- **Readiness spine**: PASS. Advances NO readiness stage (kit-bootstrap
  infrastructure) and introduces no readiness score, matching `scaffold.py` /
  `manifest.py` (spec Assumptions).

No violations. No complexity-tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/070-retail-init-bootstrap/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (the compass.yaml / fence / manifest shapes)
├── quickstart.md        # Phase 1 output (the init first-run walk-through)
├── contracts/           # Phase 1 output (compass.yaml schema; fence contract)
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
src/retail/
├── kit_init.py          # NEW: substrate-writing ONLY (calls compass_project + fence). NO profiling, NO DB, NO prompt/menu.
├── compass_project.py   # NEW: projection generator + drift check (kit-source.yaml -> compass.yaml + manifests; MAY import pyyaml lazily)
├── fence.py             # NEW: read/write the SESHAT-KIT fenced region (idempotent, outside-fence-safe)
└── cli.py               # MODIFIED: add `init` subcommand -- writes substrate + PRINTS next agent step (no wizard)

.claude/skills/
└── retail-init/
    └── SKILL.md         # NEW: the Official Workflow Skill (agent-facing; agent performs delegate -> route -> profile)

.seshat/                 # NEW (generated by init at bootstrap time, in the target repo)
├── kit-source.yaml      # canonical source: verbs + hard-stops + integrations + orient (R1)
├── compass.yaml         # kit router projection (verbs + hard-stops + orient protocol; NO stage)
├── manifest.yaml        # kit file inventory + checksums
└── integrations/
    ├── claude.json      # per-harness file+checksum manifest
    └── codex.json

tests/unit/
├── test_kit_init.py         # NEW: substrate written; module opens no DB; deferred-live path is agent-routed
├── test_compass_project.py  # NEW: projection-matches-source; no current_stage
└── test_fence.py            # NEW: idempotency; byte-identical outside fence
```

**Structure Decision**: Single-project layout, matching the existing kit. The
agent-facing surface is `.claude/skills/retail-init/SKILL.md` (an Official Workflow
Skill, the same category as `retail-orchestrate` / `retail-onboard-table`) and the
agent PERFORMS the delegate/route/profile flow; the mechanical writers live in
`src/retail/` as small modules mirroring `scaffold.py` (the projection module MAY
import `pyyaml` lazily). The generated `.seshat/` tree is an OUTPUT of `init` in a
target repo (this repo dogfoods it, so a committed `.seshat/` here is itself a
projection the drift checker validates). The canonical source is `.seshat/kit-source.yaml`
(resolved in Phase 0, R1).

## Complexity Tracking

> No Constitution Check violations. No entries required.
