# Implementation Plan: Publish Approval Receipt (record-and-STOP token)

**Branch**: `041-publish-approval-receipt-record-and` | **Date**: 2026-06-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/041-publish-approval-receipt-record-and/spec.md`

## Summary

Make the record-and-STOP semantics already in prose at `docs/readiness/publish-ready.md`
concrete by FOLDING them into the EXISTING "Publish approval" section of
`templates/handoff/bi-handoff-pack.md` (line 87) -- the one non-inherited thing the pack
already adds. Per the owner ruling (B, 2026-06-29), this is NOT a new standalone artifact:
that existing section already carries the `approvals[]` `{stage: publish_ready, owner, at}`
shape, the never-self-grant gate ("the agent CANNOT self-grant -- it STOPS"), the
blocked-not-pass rule, and the rule #9 no-number constraint. The slice only ADDS the two
missing words-on-the-page: (a) a record-and-STOP label framing that section as the TERMINAL
publish-authorization record, and (b) an explicit "no automated publish today; F016 (the
official Power BI MCP / connection adapter) is the deferred, gated, execution-only owner and
is verified ABSENT from `src/` -- this records authorization and STOPS" line. Plus a one-line,
NON-GATING note in `docs/readiness/publish-ready.md` pointing at that pack section (not at a
new file). The technical approach is pure docs/templates editing -- no code, no `retail check`
rule, no CLI verb, no DB connection, no executor. The load-bearing constraint is Principle V:
the section's owner line stays deliberately empty; the agent verifies the `approvals[]` slot
EXISTS and is recorded by a named human and CITES it; it never populates the sign-off. The
empty field IS the gate.

## Technical Context

**Language/Version**: N/A -- Markdown documentation/templates only. No code is written.

**Primary Dependencies**: None (no new runtime dependency). The static core (`src/retail/`)
remains stdlib-only and is NOT touched.

**Storage**: N/A -- committed repository text only. No database is read or written; no connection
is opened (Principle VIII; the live `retail validate` surface is not invoked).

**Testing**: No automated test code is added. Verification is (a) `retail check` exits 0 with its
rule count UNCHANGED over the committed text, and (b) the spec's Success Criteria SC-001..SC-009
are checked by reading the committed artifacts (placeholder-only scan, ASCII/UTF-8-no-BOM, no
fabricated number, Principle V un-fillable sign-off, no executor text).

**Target Platform**: Repository documentation. Windows-safe paths (260-char limit), ASCII +
UTF-8 no BOM (Principle IX).

**Project Type**: Docs/templates authoring slice within the Tower BI Agent Kit (rule 8:
docs/templates before automation).

**Performance Goals**: N/A (no runtime).

**Constraints**: ASCII + UTF-8 no BOM; repo-relative paths `<= 200` chars; no fabricated
confidence/health number (rule 9); no new gate / status / rule (no divergent source of truth);
no executor / publish / DB (rule 6, Principle II).

**Scale/Scope**: Two EDITS to existing committed artifacts -- ADD the record-and-STOP label +
the F016-absent line to the existing "Publish approval" section of
`templates/handoff/bi-handoff-pack.md`, and ADD one one-line non-gating note to
`docs/readiness/publish-ready.md`. No new file is created (ruling B). The first filled
instance (`retail_store_sales`, C086) is the EXISTING per-table pack copy
(`mappings/<table>/handoff/bi-handoff-pack.md`), not part of this generic-editing slice's
required deliverable.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | How this plan satisfies it |
|-----------|--------|----------------------------|
| I. Agent-First, Gate-Enforced | PASS | Adds NO new gate; the existing `retail check` exit code stays the authority. The agent proposes the recorded authorization in the pack section; a human disposes the sign-off. |
| II. Depend, Never Fork | PASS | No executor adapter is vendored, forked, or invoked. F016 is named as the deferred owner of any publish; the pack section records authorization and STOPs. |
| III. Medallion, Postgres-First, Gold-Only | PASS (N/A) | No schema, no DB read/write. Nothing reads silver/bronze. |
| IV. Source Mapping Before Silver | PASS (N/A) | No silver SQL is written. (Note: the idea text mislabels the seam "Principle IV"; the never-self-grant seam is Principle V -- corrected in spec FR-010.) |
| V. Agent Stops at Judgment Calls | PASS -- load-bearing | The pack section's sign-off / owner line is deliberately UN-FILLABLE by the agent (FR-002) and ALREADY states "the agent CANNOT self-grant -- it STOPS". Three judgment calls (authority class; roadmap promotion / F-number; receipt-vs-pack boundary) were REFUSED and ruled by the owner (Clarifications -> RESOLVED). |
| VI. Defaults Then Deviations | PASS (N/A) | No cleaning/modeling defaults are touched. |
| VII. C086 Is An Example, Not The Schema | PASS | The edited section is generic placeholders only; C086 (`retail_store_sales`) is cited by reference, never inlined (FR-009, SC-007). |
| VIII. Static-First Governance, Live Deferred | PASS | Docs/templates only; no new rule, no CLI verb, no Python, no DB/live validator. `retail check` exits 0, rule count UNCHANGED (FR-008, SC-005). |
| IX. Secrets and Reproducibility | PASS | ASCII + UTF-8 no BOM, short repo-relative paths, no real host/secret baked in (FR-013, SC-009). |
| Readiness System clause | PASS -- single-source | Reuses the four-status set verbatim; adds NO new stage, status, blocking reason, or required artifact; the doc note is non-gating (FR-004, FR-006, SC-005). No fabricated confidence number (FR-005). Ruling B is MORE single-source-compliant: by folding record-and-STOP into the one existing "Publish approval" section it avoids a third presentation of the sign-off facts, making drift structurally impossible. |

**Verdict**: No violations. No Complexity Tracking entries required. (Ruling B strengthens the
single-source posture relative to the earlier standalone-file design -- it keeps ONE source of
truth for publish sign-off.)

## Project Structure

### Documentation (this feature)

```text
specs/041-publish-approval-receipt-record-and/
|-- spec.md              # the feature specification (stage 2 + 3 done)
|-- plan.md              # this file (stage 4)
|-- tasks.md             # the task list (stage 4)
|-- analysis.md          # the /speckit-analyze cross-artifact report (stage 5)
|-- plan-review.md       # the adversarial plan-review (stage 6)
`-- checklists/
    `-- requirements.md  # the spec-quality checklist (stage 2)
```

No `research.md`, `data-model.md`, `quickstart.md`, or `contracts/` is produced: there is no
unknown to research (every seam is verified against the live repo in the grounding), no data model
(the pack section cites existing entities defined elsewhere), and no contract/endpoint (no code).

### Source Code (repository root)

No source code is added or changed. No new file is created (ruling B: no standalone
publish-receipt.md is ever authored). The edited committed text is:

```text
templates/handoff/
|-- bi-handoff-pack.md          # EDIT -- ADD the record-and-STOP label + the F016-absent line to
|                               #   its EXISTING "Publish approval" section (line 87); that section
|                               #   already holds the approvals[] {stage,owner,at} shape, the
|                               #   never-self-grant gate, blocked-not-pass, and rule #9 no-number
`-- handoff-review-checklist.md # EXISTING sibling (not changed)

docs/readiness/
`-- publish-ready.md            # EDIT -- ADD one non-gating evidence-style note pointing at the
                                #   pack's "Publish approval" section as the record-and-STOP record

# (Per-table filled instance -- the EXISTING per-table pack copy, NOT a separate file, and NOT
#  part of this generic-editing slice's required output:)
mappings/<table>/handoff/bi-handoff-pack.md   # the copy whose Publish approval section cites the
                                              #   recorded approval and records the STOP
```

**Structure Decision**: A docs/templates editing slice. There is NO new file (ruling B). The only
edits are (1) ADD the record-and-STOP label + the F016-absent line to the EXISTING "Publish
approval" section of `templates/handoff/bi-handoff-pack.md`, and (2) ADD one non-gating note in
the stage-authority doc pointing at that section. The per-table instance is the established
per-table copy of the pack (`mappings/<table>/handoff/bi-handoff-pack.md`); there is no separate
per-table file. No `src/`, no `tests/`, no `warehouse/`, no CLI.

## Phase 0 -- Research (no open technical unknowns)

All seams were verified read-only against the live repo during grounding:
`docs/readiness/publish-ready.md` (the record-and-STOP prose + the data-owner/governance owner),
`templates/readiness-status.yaml` (`approvals[]` shape, stage `publish_ready`, "the agent cannot
self-grant"), `templates/handoff/bi-handoff-pack.md` (the EXISTING "Publish approval" section at
line 87 -- already in the identical `approvals[]` shape, already stating the never-self-grant gate
and the blocked-not-pass / rule #9 constraints; this is the section the slice edits),
`templates/handoff/handoff-review-checklist.md` (the sibling gate), F027 (approval-console,
SHIPPED, writes `approvals[]`), and F016 (verified ABSENT from `src/`). The only OPEN items were
the three Principle V judgment calls; all three are now ruled by the owner (Clarifications ->
RESOLVED), including the receipt-vs-pack boundary, which the owner ruled FOLD-INTO-THE-PACK (B).

## Phase 1 -- Design

The design is "what to ADD to the EXISTING `Publish approval` section of
`templates/handoff/bi-handoff-pack.md`", not a new file. The section ALREADY carries the
structural pieces -- they are NOT re-authored:

ALREADY PRESENT (verified at line 87; unchanged by this slice):
- the `approvals[]` `{stage: "publish_ready", owner: "<data_owner | governance>", at}` shape,
  with the owner line as a placeholder the agent does NOT fill;
- the never-self-grant gate -- "the agent CANNOT self-grant it (Principle V) -- it STOPS and
  requests the named owner";
- the blocked-not-pass rule -- absent approval -> `publish_ready` is `blocked`, NOT `pass`;
- the four-status verdict + `evidence[]` carried by the pack's "Readiness verdict" section, with
  NO numeric confidence/health score (rule #9).

WHAT THIS SLICE ADDS to that section (the only two changes):
1. **Record-and-STOP label / framing** -- a short line framing this section as the TERMINAL
   publish-authorization RECORD: when a named human has recorded the `publish_ready` approval,
   this section IS the durable, reviewable record that the table reached publish authorization
   and the agent STOPPED here. It is reviewed in git like any handoff artifact; it triggers
   nothing.
2. **The F016-absent line** -- an explicit "no automated publish today; F016 (the official Power
   BI MCP / connection adapter) is the deferred, gated, execution-only owner of any publish and is
   verified ABSENT from `src/` -- this section records authorization and STOPS" statement (rule #6,
   Principle II). The section text must NEVER imply an executor exists.

The non-gating doc note (`docs/readiness/publish-ready.md`) is one `evidence[]`-style line
pointing at this pack section as the concrete record-and-STOP record -- it adds NO new gate, NO
new blocking reason, NO new status, and NO new required artifact.

Re-check after design: the Constitution Check above still holds -- the design adds no gate, no
status, no rule, no executor, no new file, and keeps the sign-off agent-un-fillable. By editing the
ONE existing section rather than creating a parallel artifact, ruling B is more single-source-
compliant than the earlier design (it removes the third-presentation duplication the repo rejects).

## Complexity Tracking

No Constitution Check violations -- this table is intentionally empty.
