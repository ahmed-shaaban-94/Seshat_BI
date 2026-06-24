# Source Ready

Planning (docs/templates; no runtime code).

Stage 1 of the readiness spine. A profiled, understood source exists before any
mapping work begins. Maps to medallion-playbook Phase 1.

## Purpose

Establish that the raw `<schema>.<table>` source has been measured and proposed
for understanding -- BEFORE a single source-map decision is made. "Ready" here
means the mechanical numbers are recorded and the semantic profile rows are
PROPOSED for human confirmation, never invented. This is the floor every later
stage stands on: no mapping, no silver, no judgment calls yet.

## Required artifacts

| Artifact | What it must contain |
|----------|----------------------|
| `mappings/<table>/source-profile.md` | row count, column count; per-column missingness measured as `'' OR NULL` (not `IS NULL` alone); candidate-key uniqueness proof; returns-column population; PROPOSED semantics |

The profile is the ONLY required artifact at this stage. The other four mapping
artifacts (`source-map.yaml`, `assumptions.md`, `unresolved-questions.md`,
`reconciliation-report.md`) belong to Stage 2 (Mapping Ready) and MUST NOT be
authored here.

## Required checks

| Check | Gate |
|-------|------|
| Profile review | The numbers are recorded AND the semantic rows are PROPOSED (not invented), flagged for human confirmation |

This stage has no `retail check` / `retail validate` gate. The gate is a review:
confirm the mechanical numbers came from `profile.py` over a read-only
connection, and confirm each semantic proposal is marked as a proposal awaiting
sign-off, not stated as fact.

## Statuses

| Status | Meaning HERE |
|--------|--------------|
| `not_started` | no `source-profile.md` for `<table>` yet |
| `blocked` | a required number is missing/unmeasurable, or semantics were INVENTED instead of proposed -- see Blocking reasons |
| `warning` | profile recorded but with a noted caveat (e.g. `[PENDING LIVE PROFILE]` rows in deferred-boundary mode) -- does not auto-promote |
| `pass` | every required number recorded from `profile.py`; semantics PROPOSED + flagged; evidence cites `mappings/<table>/source-profile.md` |

## Blocking reasons

- `mappings/<table>/source-profile.md` does not exist.
- Missingness measured with `IS NULL` alone (the `'' OR NULL` trap, RC5) instead
  of `'' OR NULL`.
- Candidate-key uniqueness not tested, or `is_unique` not recorded.
- Returns-column population not recorded.
- Semantic meaning INVENTED (business rollup, PII ruling, or returns column
  asserted) rather than PROPOSED for confirmation.
- Numbers fabricated because the live boundary was unavailable, instead of
  marking them `[PENDING LIVE PROFILE]`.

## Required owner / approval

Analyst confirms the proposed semantics. The mechanical numbers are
self-evidencing (recorded from `profile.py`); the SEMANTIC rows are PROPOSALS and
require the analyst to confirm meaning before this stage can read `pass`.

## Next allowed action

Begin mapping -- Stage 2 (Mapping Ready). Hand the confirmed profile to the
source-mapping workflow to author the source-map decisions.

## What the agent must NOT do

- Write ANY source-map decisions (`source-map.yaml` or sibling artifacts).
- Invent semantic meaning -- no business rollups, no PII rulings, no
  authoritative returns column asserted as fact.
- Touch silver: no `silver.*` SQL, no migrations.
- Emit a confidence number in place of the four explicit statuses.
- Fabricate profile numbers when the DSN / `db` extra is absent -- mark
  `[PENDING LIVE PROFILE]` and record a `warning` instead.

## See also

- `readiness-model.md` -- the four-status state model and the no-fake-confidence rule.
- `readiness-pipeline.md` -- the seven-stage sequence; this is stage 1 of 7.
- `mapping-ready.md` -- the next stage (the source-mapping gate).
- `../../.claude/skills/source-mapping/SKILL.md` -- the skill that runs this stage; calls `profile.py` as the mechanical profiler.
- `../../src/retail/profile.py` -- the mechanical profiler (row/col counts, `'' OR NULL` missingness, candidate-PK proof).
- `../medallion-playbook.md` -- Phase 1, which this stage maps to.
- C086 is the first worked example -- a filled instance, not the schema: `../worked-examples/c086-pharmacy.md`.
