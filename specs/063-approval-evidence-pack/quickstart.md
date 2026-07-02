# Quickstart: Approval Evidence Pack for the Named-Human Stage Gate

## What this is

A generic Product Module (skill + template) that composes a PRE-approval decision packet for
ONE stage gate of ONE table, so a named human can decide a stage approval from one legible,
fully-traceable document. It reads committed artifacts only and writes nothing back -- the
pack ends with an EMPTY approval slot only the named human fills.

## How a human requests a pack

1. Pick the table and the stage gate about to be approved (one of the seven readiness stages).
2. Ask the agent to generate the approval evidence pack for that (table, stage).
3. The agent reads: the per-stage readiness doc (what the gate requires), the table's
   `readiness-status.yaml` (state + blockers for the selected + prior stages), the AL1
   assumption signal from the table's metric contracts, the parked-on map, and the pending
   contracts.
4. The agent writes `mappings/<table>/approval-evidence-pack-<stage>.md` and STOPS.

## How to read it

- Section 1 -- what this gate requires (linked to the readiness doc).
- Section 2 -- recorded four-status state for this stage and every stage before it. If any is
  not `pass`, the path is not clear.
- Sections 3-6 -- open blockers, unresolved assumptions (per contract), blocking parked-on
  edges, pending contracts.
- Section 7 -- the approval slot. If it is empty, YOU (the named owner) sign it. If it shows a
  recorded approval, it is already signed. If it says "no stage-approval applies", this is a
  mechanical gate (Silver/Gold).

## What it will never do

- It never fills the approval slot, never appends to `approvals[]`, never moves a stage to
  `pass`, never defines or approves business meaning.
- It never invents a status: a missing source is a recorded blocker.
- It never emits a confidence/health/maturity number or a completeness count.
- It never reads a live DB or Power BI surface.

## Two things a human must still rule on (Principle V -- OPEN)

- What "pending contracts" resolves to on disk (FR-008).
- The safe boundary for summarising a committed grain/rollup/segment/PII ruling (FR-013).

Until a human rules on these, a generated pack surfaces them as OPEN, not as answered.

## Worked walk-through (generic placeholders -- SC-001)

A named `<metric owner>` is asked to approve the `semantic_model_ready` gate for
`<schema.table>`. They ask for the approval evidence pack for that (table, stage).
The agent, following `.claude/skills/approval-evidence-pack/SKILL.md`, produces
`mappings/<table>/approval-evidence-pack-semantic_model_ready.md` with the template
sections in order:

1. **(H) Header** -- table, stage `semantic_model_ready`, generated-at, and the four
   sources it read.
2. **(1) What this gate requires** -- linked from
   `docs/readiness/semantic-model-ready.md` (not re-authored).
3. **(2) Readiness state** -- `source_ready` .. `semantic_model_ready` only (the
   selected stage plus every prior stage), each status verbatim; never a later
   stage (FR-020). Say `semantic_model_ready` is `blocked` with two recorded
   `blocking_reasons[]` -> the pack shows `blocked` and lists both reasons verbatim.
4. **(3) Open blockers** -- every `blocking_reasons[]` entry, each traceable to
   `mappings/<table>/readiness-status.yaml`.
5. **(4) Unresolved assumptions** -- one line per offending
   `mappings/<table>/metrics/<Metric>.yaml`, the recorded contradiction (never
   resolved).
6. **(5) Blocking parked-on edges** -- any `docs/quality/parked-on.yaml` edge that
   blocks this table's stage.
7. **(6) Pending contracts** -- the metric contracts whose `readiness.status` is
   not `pass` (link-and-cite only; FR-008/FR-013).
8. **(7) Approval slot** -- Form A: an EMPTY slot the metric owner fills. The
   module cannot fill it; no score, no count anywhere.

The reader confirms this order matches `templates/approval-evidence-pack.md` and
that every evidence line resolves to a committed path (SC-001, SC-002).

## Verify

- `retail check` stays green and the rule count is unchanged (this feature adds no rule).
- A generated pack (against a table with committed artifacts) has every evidence line
  resolving to a committed path, an empty-or-recorded approval slot, and no score/count.
