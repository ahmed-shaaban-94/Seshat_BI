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

## Verify

- `retail check` stays green and the rule count is unchanged (this feature adds no rule).
- A generated pack (against a table with committed artifacts) has every evidence line
  resolving to a committed path, an empty-or-recorded approval slot, and no score/count.
