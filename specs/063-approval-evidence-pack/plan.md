# Implementation Plan: Approval Evidence Pack for the Named-Human Stage Gate

**Branch**: `063-approval-evidence-pack` | **Date**: 2026-07-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/063-approval-evidence-pack/spec.md`

## Summary

Ship a NEW generic Product Module (authority category: Product Module, capability level
`artifact-writing`, per docs/architecture/product-modules.md) that composes a PRE-approval
decision packet for ONE selected stage gate of ONE table. Deliverable is docs/skill/template
only -- a skill under `.claude/skills/` plus a generic copy-me template under `templates/`,
plus the F024 module contract and a roadmap-ledger entry assigning the new F-number. It adds
NO runtime executor and NO `retail check` rule (the agent is the runtime; it adds no gate).
The pack READS committed artifacts only (the per-stage readiness doc, the table's
readiness-status.yaml, the AL1 assumption-ledger signal from metric contracts, the parked-on
map, and the pending-contract set) and WRITES only its own pack with an EMPTY `approvals[]`
slot; it surfaces state, never asserts it, and emits no score and no count.

## Technical Context

**Language/Version**: N/A -- no runtime code. Authored artifacts are Markdown + a YAML/MD
template. The runtime is the agent following the skill (F028 precedent).

**Primary Dependencies**: none new. The module reads existing committed artifacts only:
`docs/readiness/*.md`, `mappings/<table>/readiness-status.yaml`,
`mappings/<table>/metrics/*.yaml`, `docs/quality/parked-on.yaml`.

**Storage**: files only (committed repo artifacts). No DB, no PBIP, no network.

**Testing**: doc-level acceptance -- the F028 pattern. There is no Python module to unit-test;
verification is (a) `retail check` stays green and rule count unchanged (no new rule), and
(b) the acceptance scenarios in spec.md are demonstrable by generating a pack against a
committed table's artifacts. No new pytest module is added.

**Target Platform**: repo-local, Windows-first (260-char path budget); ASCII/UTF-8 no BOM.

**Project Type**: docs/skill/template Product Module (single repo).

**Performance Goals**: N/A (a human-in-the-loop authoring step).

**Constraints**: read-only apart from the pack it writes; structurally incapable of writing
`approvals[]` or moving a stage; no numeric score / completeness count (hard rule #9); generic
only (Principle VII); adds no gate (F024).

**Scale/Scope**: one (table, stage) pack per invocation; seven possible stages; generic across
all tables.

## Constitution Check

*GATE: Must pass before Phase 0. Re-checked after design.*

- **Principle V (Agent Stops at Judgment Calls)**: PASS by construction. The module emits an
  EMPTY `approvals[]` slot and is structurally incapable of populating it, granting an
  approval, or moving a stage to `pass` (FR-009, FR-010). The two Principle-V rulings
  (pending-contracts definition FR-008; business-rule/PII summarisation boundary FR-013) are
  carried OPEN for a human, not answered here.
- **Principle VII (C086 Is An Example)**: PASS. Template and fixed labels stay generic; C086
  is a cited filled instance only; the module resolves a generic `mappings/<table>/` path
  (FR-014, SC-006).
- **Principle VIII (Static-First, Live Deferred)**: PASS. No live DB / PBIP / F016 read
  (FR-002); composes committed artifacts only.
- **Principle IX (Secrets & Reproducibility)**: PASS. ASCII/UTF-8 no BOM; short repo-relative
  paths (FR-017); no secrets.
- **F024 Product Module boundary**: PASS. Exactly one capability level (`artifact-writing`);
  reads Core Authority, writes one derived artifact; adds no gate, defines no truth.
- **Hard rule #9 (no fabricated confidence)**: PASS. Four explicit statuses + evidence +
  blockers only; no numeric score, no "N of M" count (FR-012).

No violations -- Complexity Tracking omitted.

## Design overview

Three authored artifacts + one ledger edit (no source-tree code):

1. **Template** `templates/approval-evidence-pack.md` -- the generic copy-me shape of the
   pack. Ordered sections: (H) header (table, stage, generated-at, source list); (1) what
   this gate requires (from the per-stage readiness doc); (2) readiness state for the selected
   stage + all prior stages (four-status, verbatim); (3) open blockers (from
   `blocking_reasons[]`); (4) unresolved assumptions (per-contract AL1 signal); (5) blocking
   parked-on edges; (6) pending contracts (input per FR-008, definition OPEN); (7) the empty
   approval slot OR, for a mechanical gate, a "no stage-approval applies" statement + the
   mechanical result, OR, if already signed, the recorded approval read-only. Every section
   carries `evidence[]` / `blocking_reasons[]`; no score; no count. Placeholders only.
2. **Skill** `.claude/skills/approval-evidence-pack/SKILL.md` -- the composer instructions:
   the input contract (the five read sources), the stage-key -> readiness-doc mapping, the
   surface-never-assert + empty-approvals discipline reused verbatim from F028, the missing-
   source -> blocker rule, the mechanical-gate and already-signed branches, and the explicit
   forbidden-operations list. Declares the F024 module contract (Product Module /
   `artifact-writing`) and the new roadmap F-number.
3. **Module contract** -- a filled `templates/module-contract.md` declaration embedded in the
   SKILL.md (F028 precedent), naming Core Authority READ, derived artifact WRITTEN, EXECUTES
   none, and the forbidden operations.
4. **Roadmap ledger edit** -- assign the next Product Module F-number after F028 in
   `docs/roadmap/roadmap.md` and note the on-disk spec dir `063-approval-evidence-pack`
   (dir!=F-number is allowed; roadmap F-number wins on disagreement, per F028's own note).

Design artifacts for this feature dir: this plan.md, research.md (precedent + input-source
confirmation), data-model.md (the pack's section/entity shapes + the read-source field map),
quickstart.md (how a human requests a pack and reads it), and tasks.md (stage 4 tasks). No
`contracts/` API dir -- there is no programmatic API surface.

## Project Structure

### Documentation (this feature)

```text
specs/063-approval-evidence-pack/
|-- spec.md
|-- plan.md              # this file
|-- research.md          # precedent + input-source confirmation
|-- data-model.md        # pack sections / entities / read-source field map
|-- quickstart.md        # how to request + read a pack
|-- checklists/
|   `-- requirements.md
|-- analysis.md          # /speckit-analyze output (stage 5)
|-- plan-review.md       # adversarial review (stage 6)
`-- tasks.md             # /speckit-tasks output (stage 4)
```

### Authored artifacts (repository root)

```text
templates/approval-evidence-pack.md            # NEW generic copy-me template
.claude/skills/approval-evidence-pack/SKILL.md # NEW composer skill + F024 module contract
docs/roadmap/roadmap.md                        # EDIT: assign new F-number, note spec dir
```

No `src/` changes. No `tests/` module. No `mappings/` change (the filled pack lands under
`mappings/<table>/` only when a real table is packed -- out of scope for this feature, which
ships the generic kit).

**Structure Decision**: docs/skill/template Product Module in the F028 shape; no runtime code,
no new gate, no source tree.

## Scope discipline (YAGNI)

- Ship the generic multi-gate generator ONLY. The dashboard-specific variant is idea C1, out
  of scope (spec Assumptions).
- Do NOT resolve the two Principle-V questions; carry them OPEN.
- Do NOT assume any deferred capability exists (F016 Power BI execution adapter; F031-F033
  spec-only runtimes) -- FR-002 forbids reading them.
- Add the seam (the generic kit), not a filled C086 pack instance.
