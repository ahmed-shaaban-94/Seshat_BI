# Implementation Plan: Approver Decision Surface

**Branch**: `115-approver-decision-surface` | **Date**: 2026-07-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/115-approver-decision-surface/spec.md`

## Summary

Compose ONE read-only, refutation-first reading view for a human signer over ONE
table's committed readiness evidence: refusal-bearing items (blocked/warning
stages, unmet approvals, OPEN `unresolved-questions.md` rows) first, ordered by
the SHIPPED fixed category enum rank (approval > grain > live_validation >
artifact > readiness), reassurance (pass stages, valid approvals, answered
questions) last. Writes nothing, grants nothing, moves no stage; no score, no
gate.

**Technical approach**: a STANDALONE `src/retail/approver_view.py` + CLI verb.
The refutation rank is REUSED (not re-invented) by EXTRACTING the module-private
`_CATEGORY_RULES` / `_classify` from `blocker_explainer.py` into a shared
importable helper both modules call -- a behavior-preserving move-refactor of the
#229 code, so `blocker_explainer`'s output is byte-identical and its tests stay
green. Paired with a non-gating unit-test VERIFIER that asserts REFUSAL-CASE
COMPLETENESS (every blocked/warning/unmet-approval/open-question item appears in
the refusal case, none misfiled as reassurance or dropped) plus deterministic
ordering -- because the danger this surface guards is a refusal-eligible item
silently reading as reassurance, not mere ordering flake.

## Technical Context

**Language/Version**: Python 3.11+ (matches `src/retail/`; stdlib-only core).

**Primary Dependencies**: stdlib + the in-repo `yaml` reader already used by the
shipped readiness surfaces; no new dependency. Reuses the extracted classifier
helper.

**Storage**: reads two committed files per table
(`mappings/<table>/readiness-status.yaml`, `mappings/<table>/unresolved-questions.md`);
writes nothing by default (a `--write` companion-file option is a deferred plan
sub-decision, see below). No DB, no network.

**Testing**: pytest `@pytest.mark.unit`. Fixtures: a table with blocked+warning
stages + a missing approval + an open governance question (the full refusal
case); an all-pass table (reassurance only); a table with only
`unresolved-questions.md` open rows; and input-absence cases. Plus a
regression-lock test that `blocker_explainer`'s output is unchanged after the
classifier extraction.

**Target Platform**: CLI, ASCII output, UTF-8 no BOM.

**Project Type**: single-project CLI/library (extends `src/retail`).

**Performance Goals**: N/A -- static compose over two small files.

**Constraints**: driver-free import path (Principle VIII); NO write path in the
default read view (FR-006, structurally grep-verifiable); ASCII-only (Principle
IX); short paths (Windows MAX_PATH).

**Scale/Scope**: one table per invocation. Generic across tables (Principle VII).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Bearing | Verdict |
|-----------|---------|---------|
| I. Agent-First, Gate-Enforced | Adds NO gate; not a `retail check` rule; claims no rule-pass authority. | PASS |
| II. Depend, Never Fork | No execution adapter touched. | PASS (n/a) |
| III. Medallion, Postgres-First, Gold-Only | Reads committed readiness artifacts, not a warehouse layer; opens no DB. | PASS (n/a) |
| IV. Source Mapping Before Silver | Consumes committed readiness state; writes no silver; adds no mapping gate. | PASS |
| V. Agent Stops at Judgment Calls | LOAD-BEARING. The surface RE-ORDERS committed evidence for the signer; it grants no approval, moves no stage, writes nothing. F027 owns the write-back. It REINFORCES Principle V (helps the human refuse well) and never self-grants. | PASS (reinforces; structural no-write) |
| VI. Defaults Then Deviations | Reuses the committed category rank; makes no default/deviation ruling. | PASS |
| VII. C086 Is An Example | Generic, per-table; no hardcoded names/keys (FR-011, SC-006). | PASS |
| VIII. Static-First, Live Deferred | Static committed-text only; driver-free; no live surface. | PASS |
| IX. Secrets and Reproducibility | Reads committed text; ASCII, UTF-8 no BOM; writes nothing by default. | PASS |

**Hard rule #9 (no fabricated confidence/score)**: PASS -- FR-002/FR-008 forbid
any synthesized rank or score; ordering is a FIXED committed enum lookup, not a
computation. Verified by a test asserting no numeric token in output and that the
order matches the fixed enum rank.

**Gate result**: PASS. No violations; Complexity Tracking not required. The
classifier extraction is a behavior-preserving refactor (regression-locked), not
new complexity.

## Project Structure

### Documentation (this feature)

```text
specs/115-approver-decision-surface/
  plan.md
  research.md
  data-model.md
  quickstart.md
  contracts/
    view.md
    verifier.md
  checklists/
    requirements.md
  tasks.md
```

### Source Code (repository root)

```text
src/retail/
  readiness_classify.py         # NEW: shared classifier -- _CATEGORY_RULES + classify(),
                                 #      EXTRACTED from blocker_explainer.py (behavior-preserving)
  blocker_explainer.py          # EDIT: import from readiness_classify instead of module-private copy
                                 #      (output byte-identical; regression-locked)
  approver_view.py              # NEW: the refutation-first composer (read 2 files, order, render)
  cli/
    commands/
      approver_view.py          # NEW: CLI verb (mirrors cli/commands/blockers.py)
  cli/parser.py                 # EDIT: register the new subcommand
  cli/__init__.py               # EDIT: dispatch the new subcommand

docs/tools/
  approver-decision-surface.md  # NEW: tool doc (mirrors docs/tools/blocker-explainer.md)

tests/unit/
  test_approver_view.py         # NEW: refusal-case COMPLETENESS verifier + ordering + fixtures
  test_blocker_explainer.py     # EDIT/CONFIRM: regression-lock output unchanged after extraction
```

**Structure Decision**: STANDALONE `src/retail/approver_view.py`, NOT a mode
folded into `blocker_explainer.py`. Rationale (decided in research D1): the
clarify answers made the delta a SECOND RESPONSIBILITY, not a sort tweak -- the
surface (a) surfaces `warning` stages `blocker_explainer` deliberately ignores,
(b) reads a second file (`unresolved-questions.md`) it never touches, and (c)
introduces a reassurance grouping it has no concept of. Folding would overload a
single-purpose shipped module and balloon the exact complexity the CodeScene
new-code-health gate polices. Reuse is achieved WITHOUT co-location by extracting
the shared classifier into `readiness_classify.py` (a behavior-preserving
move-refactor), giving the DRY the fold promised without the bloat. The rejected
fold option and this decision are flagged as a ratify-ledger open item for owner
confirmation.

## Complexity Tracking

> Not required -- Constitution Check passed. The classifier extraction is a
> regression-locked behavior-preserving refactor, explicitly NOT new complexity.
