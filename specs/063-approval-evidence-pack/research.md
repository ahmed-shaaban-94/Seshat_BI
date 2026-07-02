# Research: Approval Evidence Pack for the Named-Human Stage Gate

Phase 0 -- precedent survey and input-source confirmation. All reads were of committed
artifacts in this worktree.

## Precedents (what to reuse, what to stay distinct from)

- **F028 evidence-pack-generator** (`.claude/skills/evidence-pack-generator/SKILL.md`, spec
  022). SHIPPED Product Module / `artifact-writing`. REUSE: its surface-never-assert table,
  its "composes never invents", its empty-approvals discipline, and its missing-source ->
  blocker rule (verbatim in spirit). STAY DISTINCT: F028 is a late-stage (Semantic ->
  Dashboard -> Publish) per-table 10-section pack; this feature is a PRE-approval, generic
  across all seven stages (stage param), scoped to one gate. Do NOT edit F028.
- **F027 Approval Console** (`templates/approval-request.md`, `templates/approval-decision.md`,
  spec 021). SHIPPED. `approval-request.md` packages ONE raised judgment call; the console
  TRANSCRIBES a human's answer back into committed artifacts. STAY DISTINCT: this feature
  packages a WHOLE-GATE readiness picture and WRITES NOTHING BACK. They COMPOSE: the pack is
  the evidence a human reads; the Approval Console records their signature afterward.
- **Readiness spine** (`docs/readiness/readiness-model.md` + the seven per-stage docs).
  Confirms: four statuses (`not_started | blocked | warning | pass`); four stages carry a
  named-human approval (Mapping / Semantic Model / Dashboard / Publish Ready); Silver + Gold
  are mechanical gates (no stage approval); a stage is entered only when the prior is `pass`.
  This is the authority for FR-003, FR-004, FR-015, FR-020.

## Input-source confirmation (the five reads)

| Input | Confirmed on-disk source | Notes |
|-------|--------------------------|-------|
| Gate requirements | `docs/readiness/<stage>-ready.md` (7 present) | stage-key -> doc mapping is 1:1 |
| Readiness state | `mappings/<table>/readiness-status.yaml` (template at `templates/readiness-status.yaml`) | per-stage status + evidence[] + blocking_reasons[] + approvals[] |
| Assumption signal | AL1 rule `src/retail/rules/assumptions.py` (spec 059) reading `mappings/<table>/metrics/*.yaml` | surface the recorded contradiction per contract; do NOT re-run/re-implement AL1 |
| Parked-on edges | `docs/quality/parked-on.yaml` (DF1, spec 051) | each edge: id/blocked/parked_on/doc/anchor/evidence |
| Pending contracts | UNCONFIRMED single artifact | FR-008 -- Principle-V OPEN; closest real seam is `mappings/<table>/metrics/*.yaml` with `readiness.status != pass` |

## Open (Principle-V, not resolved here)

- **Pending contracts (FR-008)**: no single confirmed artifact. Carried OPEN for a human.
- **Business-rule / PII summarisation boundary (FR-013)**: whether summarising a committed
  grain/rollup/segment/PII ruling risks republishing a human-owned judgment. Carried OPEN.

## Decisions carried from clarify (Session 2026-07-02)

- C1 output path: `mappings/<table>/approval-evidence-pack-<stage>.md`.
- C2 shape: skill + template; no executor; no retail rule.
- C3 stage window: selected stage + all prior; never later stages.
- C4 assumption granularity: per offending metric contract.

## Deferred capabilities NOT assumed

F016 Power BI execution adapter and F031-F033 spec-only runtimes are DEFERRED; FR-002 forbids
reading any of them. No live DB / PBIP read anywhere.
