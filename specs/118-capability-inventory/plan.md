# Implementation Plan: Capability Inventory

**Branch**: `118-capability-inventory` | **Date**: 2026-07-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/118-capability-inventory/spec.md`

## Summary

Expose ONE read-only, truthful capability inventory of the Seshat BI kit as a
COMPANION SURFACE (a skill wrapping a pure builder), NOT a new top-level CLI verb --
honoring the ratified Option-B decision (`docs/roadmap/decisions/cli-verbs-vs-skill-driven.md`,
2026-07-07). It classifies every capability by four ORTHOGONAL axes (lifecycle `state`,
`authority`, `requirements`, provenance) and renders a grouped human read + a stable
machine form. It reads only committed metadata, invents no maturity/confidence/health
score, grants/changes no readiness, writes no files, opens no DB, runs no Power BI.

**Technical approach**: a NEW hand-authored YAML **capability manifest**
(`docs/capabilities/capabilities.yaml`) is the canonical authority for the categorical
CLASSIFICATION, owning ONLY the fields no existing source records (`state` finer
buckets, `authority`, `requirements`, provenance) and REFERENCING -- never copying --
facts owned by existing feeders (rule ids/titles from `docs/rules/rules-manifest.json`;
skill declarations from `.claude/skills/*/SKILL.md` frontmatter; orchestration verbs
from `.seshat/kit-source.yaml`; F-numbered ship status from `docs/roadmap/roadmap.md`;
doc-anchored built/planned claims from `docs/quality/status-claims.yaml`). A NEW pure
builder `src/retail/capability_inventory.py` joins `manifest ⋈ feeders` and renders BOTH
forms DETERMINISTICALLY (stable id sort, fixed serialization) -- NO rendered output is
committed (owner decision: render live; only the manifest + feeders are committed
inputs). A NEW `.claude/skills/capabilities/SKILL.md` is the Option-B surface that calls
the builder. Paired with a NON-GATING pytest VERIFIER that sits ON the truthfulness risk
(FR-013): FAIL-CLOSED reconciliation of `state: shipped` and `provenance:
publicly-released` against the feeders, plus orphan/unlisted/no-score/determinism checks
-- because the danger this surface guards is a FALSE "shipped"/"released", not a layout
flake.

## Technical Context

**Language/Version**: Python 3.11+ (matches `src/retail/`; stdlib-only core).

**Primary Dependencies**: stdlib + the in-repo `yaml` reader already used by the shipped
readiness surfaces (`status_surface.py`, `run_next.py`) and `json` (stdlib) for the
machine form. NO new dependency, NO DB driver, NO network, NO Power BI/PBIR.

**Storage**: reads committed files only -- the NEW `docs/capabilities/capabilities.yaml`
manifest plus the feeders listed above. Writes NOTHING (structurally grep-verifiable, no
`open(...,"w")` / `write_text` / `Path.write*` in the module). No committed rendered
output (render live).

**Testing**: pytest `@pytest.mark.unit`. Fixtures: a manifest with a mix of shipped /
spec-only / deferred / human-gated / advisory entries; a deliberately-STALE manifest
(orphan entry referencing a non-existent rule id / skill; a wired capability omitted;
a `state: shipped` with no positive feeder; a `provenance: publicly-released` with no
release evidence) to prove the oracle FAILS in each direction; and an empty/minimal
manifest for the drop-in edge case. Ground truth for the oracle is read from the FEEDER
sources, independent of the builder's rendering code (no circularity).

**Target Platform**: skill-invoked composer; ASCII output, UTF-8 no BOM.

**Project Type**: single-project library + skill (extends `src/retail`; adds one skill).
NO CLI verb added (Option-B ratified decision).

**Invocation seam (compliance-critical)**: the builder is exposed as a Python MODULE
entry point -- `python -m retail.capability_inventory [--format json]` (a `__main__` in
the module, thin arg parse for the format flag). The `SKILL.md` (agent-facing
instructions) tells the agent to RUN that module command. This is Option-B-compliant by
construction: a `python -m` module entry point is NOT a `_DISPATCH`/argparse subcommand
and does NOT appear in `seshat --help` / `retail --help`, so it grows no top-level CLI
verb surface (FR-001). It is the novel-for-this-repo seam that lets an OPERATIONAL skill
(one that renders output) exist without the verb every shipped `retail-*` skill currently
wraps. The module is import-safe (driver-free) and its `__main__` writes only to stdout.

**Performance Goals**: N/A -- static compose over a handful of small committed files.

**Constraints**: driver-free import path (Principle VIII); NO write path (FR-010,
structurally grep-verifiable); NO new argparse subcommand / `_DISPATCH` entry (FR-001);
NO `retail check` rule / gate (FR-012); NO numeric score (FR-009, hard rule #9); ASCII
only (Principle IX); short paths (Windows MAX_PATH).

**Scale/Scope**: whole-kit inventory, one compose per invocation. Generic (Principle
VII): no hardcoded onboarded-table names.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Bearing | Verdict |
|-----------|---------|---------|
| I. Agent-First, Gate-Enforced | Adds NO `retail check` rule and NO gate (FR-012); claims no rule-pass authority; its presence is never a gate requirement. The staleness/truthfulness oracle is a UNIT TEST that fails closed at CI -- a test failing CI is NOT a governance gate (no non-zero `retail check` exit, no registered rule, no `blocking_reasons[]`), so "no gate" and "fail-closed test" are not in tension. | PASS |
| II. Depend, Never Fork | No execution adapter touched; the inventory merely LISTS the dbt/Dagster/PBI adapters, classifying each from its committed feeder. | PASS (n/a) |
| III. Medallion, Postgres-First, Gold-Only | Reads committed metadata, not a warehouse layer; opens no DB; runs no Power BI. | PASS (n/a) |
| IV. Source Mapping Before Silver | Consumes committed metadata; writes no silver; adds no mapping gate. | PASS |
| V. Agent Stops at Judgment Calls | LOAD-BEARING. The surface RE-PRESENTS committed truth; it grants no approval, moves no stage, computes/changes no readiness (FR-011), writes nothing (FR-010). It never self-grants and defers readiness to `status`/`next`/`check`. | PASS (reinforces; structural no-write) |
| VI. Defaults Then Deviations | Reuses the committed `product-modules.md` category vocabulary; makes no default/deviation ruling. | PASS |
| VII. C086 Is An Example | Generic whole-kit inventory; no hardcoded onboarded-table names or client keys (FR-018). | PASS |
| VIII. Static-First, Live Deferred | Static committed-text only; driver-free import path; no live surface, no DB, no PBIR. | PASS |
| IX. Secrets and Reproducibility | Reads committed text; ASCII, UTF-8 no BOM; writes nothing; deterministic render (FR-007). No credentials touched. | PASS |

**Hard rule #9 (no fabricated confidence/score)**: PASS -- FR-009 forbids any numeric
maturity/confidence/completeness/health value and any ranking by a computed number.
Verified by a test asserting no numeric-score token in either output form and that
grouping is by fixed categorical field, not a computed order.

**Ratified-decision check (`cli-verbs-vs-skill-driven.md`, Option B, 2026-07-07)**:
PASS by construction -- FR-001 adds NO top-level CLI verb; the surface is a skill
wrapping a builder, and rendering is LIVE so no regeneration verb is needed. This is the
110-113 packaging precedent, not the rejected Option-A verb growth.

**Gate result**: PASS. No violations; Complexity Tracking not required. One new manifest
+ one builder + one skill + one test module is the minimal seam, not a subsystem.

## Project Structure

### Documentation (this feature)

```text
specs/118-capability-inventory/
  plan.md
  research.md
  data-model.md
  quickstart.md
  contracts/
    manifest-schema.md          # the capability-manifest field contract (categorical, closed)
    inventory-output.md         # the two rendered forms (grouped human + machine)
    staleness-oracle.md         # the fail-closed test contract (what fails, in which direction)
  checklists/
    requirements.md
  tasks.md
```

### Source Code (repository root)

```text
docs/capabilities/
  capabilities.yaml             # NEW: the hand-authored capability manifest (canonical
                                 #      authority for classification; owns state/authority/
                                 #      requirements/provenance; REFERENCES feeder facts)
  README.md                     # NEW: explains capabilities vs status/next/doctor/check
                                 #      (FR-017), and that the manifest supersedes the prose
                                 #      predecessors as the structured authority

src/retail/
  capability_inventory.py       # NEW: pure builder + `__main__` module entry point --
                                 #      load manifest, reconcile against feeders, render
                                 #      grouped-human + machine forms DETERMINISTICALLY to
                                 #      stdout; `python -m retail.capability_inventory
                                 #      [--format json]`; reads only, writes nothing, NOT a
                                 #      _DISPATCH verb (invisible to seshat/retail --help)

.claude/skills/capabilities/
  SKILL.md                      # NEW: the Option-B surface (frontmatter name+description);
                                 #      instructs the agent to RUN `python -m
                                 #      retail.capability_inventory`; adds no CLI verb

tests/unit/
  test_capability_inventory.py  # NEW: fail-closed truthfulness oracle (orphan / unlisted /
                                 #      false-shipped / false-released), determinism, no-score,
                                 #      grouping-by-categorical-field; ground truth from feeders
```

Explicitly UNCHANGED (no edit): `src/retail/cli/parser.py`, `src/retail/cli/__init__.py`
(`_DISPATCH`) -- FR-001/FR-016 forbid a new subcommand and require existing surfaces
byte-identical. The feeder files are READ, never modified.

**Structure Decision**: a SKILL wrapping a standalone builder module, NOT a CLI verb and
NOT a hand-authored inventory doc.

- *Why not a CLI verb*: the ratified Option-B decision rejected CLI-verb growth for
  discoverability; this is the load-bearing constraint (spec Clarifications, FR-001).
- *Why not a hand-authored inventory doc*: FR-007 + SC-003 require BYTE-IDENTICAL machine
  output (a hand doc drifts and isn't deterministic), and FR-003/FR-015 forbid
  RE-DECLARING feeder-owned facts (a hand doc copying rule titles is the exact
  duplication the feature exists to kill). Determinism + no-duplication force a pure
  sorted BUILDER over `manifest ⋈ feeders`.
- *Why no committed golden* (owner decision, Session 2026-07-11): the repo's golden-file
  pattern (`rules-manifest.json`, `severity-posture.json`) regenerates via a `_DISPATCH`
  CLI VERB -- which this feature cannot add. Rendering LIVE (manifest + feeders are the
  committed, reviewable inputs; the builder emits on demand) needs NO regeneration verb,
  so the ratified decision is honored by construction. Determinism is proved by test, not
  by a checked-in snapshot.
- *Manifest = YAML* (not JSON): hand-authored ledgers here are YAML (`shipped-ideas.yaml`,
  `status-claims.yaml`, `kit-source.yaml`); only GENERATED goldens are JSON. This manifest
  is hand-authored, so YAML matches convention.

## Complexity Tracking

> Not required -- Constitution Check passed. One manifest + one builder + one skill + one
> test module is the minimal seam. No golden-regeneration surface (live render), no CLI
> verb, no `retail check` rule, no readiness-stage refactor (FR-004 is satisfied by
> REFERENCING an existing committed stage-name source, not by consolidating the three
> duplicated tuples -- that consolidation is out of scope, CLAUDE.md YAGNI).
