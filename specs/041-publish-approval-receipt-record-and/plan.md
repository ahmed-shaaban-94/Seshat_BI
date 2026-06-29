# Implementation Plan: Publish Approval Receipt (record-and-STOP token)

**Branch**: `041-publish-approval-receipt-record-and` | **Date**: 2026-06-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/041-publish-approval-receipt-record-and/spec.md`

## Summary

Make the record-and-STOP semantics already in prose at `docs/readiness/publish-ready.md` a
concrete, copy-me artifact: a GENERIC template `templates/handoff/publish-receipt.md` that records
the terminal publish-authorization state of a table (the table, the pack it terminalizes by path,
the CITED `publish_ready` `approvals[]` entry, a deliberately-empty sign-off / owner line, an
explicit "no automated publish today (F016 absent)" statement, and a four-status verdict +
`evidence[]` + `blocking_reasons[]`) and STOPS. Plus a one-line, NON-GATING note in
`docs/readiness/publish-ready.md` pointing at the receipt. The technical approach is pure
docs/templates authoring -- no code, no `retail check` rule, no CLI verb, no DB connection, no
executor. The load-bearing constraint is Principle V: the agent verifies the `approvals[]` slot
EXISTS and is recorded by a named human and CITES it; it never populates the sign-off. The empty
field IS the gate.

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

**Scale/Scope**: Two committed artifacts -- one new generic template + one one-line non-gating
doc note. The first filled instance (`retail_store_sales`, C086) is a per-table copy, not part of
this generic-authoring slice's required deliverable.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | How this plan satisfies it |
|-----------|--------|----------------------------|
| I. Agent-First, Gate-Enforced | PASS | Adds NO new gate; the existing `retail check` exit code stays the authority. The agent proposes the receipt; a human disposes the sign-off. |
| II. Depend, Never Fork | PASS | No executor adapter is vendored, forked, or invoked. F016 is named as the deferred owner of any publish; the receipt records-and-STOPs. |
| III. Medallion, Postgres-First, Gold-Only | PASS (N/A) | No schema, no DB read/write. Nothing reads silver/bronze. |
| IV. Source Mapping Before Silver | PASS (N/A) | No silver SQL is written. (Note: the idea text mislabels the seam "Principle IV"; the never-self-grant seam is Principle V -- corrected in spec FR-010.) |
| V. Agent Stops at Judgment Calls | PASS -- load-bearing | The receipt's sign-off / owner line is deliberately UN-FILLABLE by the agent (FR-002). Three judgment calls (authority class; roadmap promotion / F-number; receipt-vs-pack boundary) are REFUSED and recorded in spec Clarifications -> Open for human. |
| VI. Defaults Then Deviations | PASS (N/A) | No cleaning/modeling defaults are touched. |
| VII. C086 Is An Example, Not The Schema | PASS | The template is generic placeholders only; C086 (`retail_store_sales`) is cited by reference, never inlined (FR-009, SC-007). |
| VIII. Static-First Governance, Live Deferred | PASS | Docs/templates only; no new rule, no CLI verb, no Python, no DB/live validator. `retail check` exits 0, rule count UNCHANGED (FR-008, SC-005). |
| IX. Secrets and Reproducibility | PASS | ASCII + UTF-8 no BOM, short repo-relative paths, no real host/secret baked in (FR-013, SC-009). |
| Readiness System clause | PASS | Reuses the four-status set verbatim; adds NO new stage, status, blocking reason, or required artifact; the doc note is non-gating (FR-004, FR-006, SC-005). No fabricated confidence number (FR-005). |

**Verdict**: No violations. No Complexity Tracking entries required.

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
(the receipt cites existing entities defined elsewhere), and no contract/endpoint (no code).

### Source Code (repository root)

No source code is added or changed. The authored/edited committed text is:

```text
templates/handoff/
|-- bi-handoff-pack.md          # EXISTING sibling (not changed; the pack the receipt terminalizes)
|-- handoff-review-checklist.md # EXISTING sibling (not changed)
`-- publish-receipt.md          # NEW -- the generic record-and-STOP receipt template (this slice)

docs/readiness/
`-- publish-ready.md            # EDIT -- add one non-gating evidence-style note pointing at the receipt

# (Per-table filled instance -- NOT part of this generic-authoring slice's required output:)
mappings/<table>/handoff/publish-receipt.md   # a future copy-and-fill, cites the recorded approval
```

**Structure Decision**: A docs/templates authoring slice. The new template lands in
`templates/handoff/` beside its two existing siblings (the copy-per-table convention is already
established there and in `mappings/<table>/handoff/`). The only existing-file edit is a one-line
non-gating note in the stage-authority doc. No `src/`, no `tests/`, no `warehouse/`, no CLI.

## Phase 0 -- Research (no open technical unknowns)

All seams were verified read-only against the live repo during grounding:
`docs/readiness/publish-ready.md` (the record-and-STOP prose + the data-owner/governance owner),
`templates/readiness-status.yaml` (`approvals[]` shape, stage `publish_ready`, "the agent cannot
self-grant"), `templates/handoff/bi-handoff-pack.md` (the existing "Publish approval" section in
the identical shape), `templates/handoff/handoff-review-checklist.md` (the sibling gate), F027
(approval-console, SHIPPED, writes `approvals[]`), and F016 (verified ABSENT from `src/`). The
only OPEN items are the three Principle V judgment calls, which are human rulings, not research.

## Phase 1 -- Design

The receipt template's sections (all generic placeholders):

1. **Header** -- table identity, source family, the pack it terminalizes (relative path),
   assembled-on / assembled-by.
2. **Prior-stage gate** -- a restated check that stages 1-6 are each `pass` (cited from
   `readiness-status.yaml`), never re-decided here.
3. **Cited publish approval (READ-ONLY)** -- a quote/pointer to the `publish_ready` `approvals[]`
   entry with the owner line shown as a placeholder the agent does NOT fill; an explicit note that
   the agent verifies-the-slot-exists and STOPS (Principle V; composes with F027).
4. **No-executor statement** -- explicit "no automated publish today; F016 is the deferred,
   gated, execution-only owner and is not built" (rule 6, Principle II).
5. **Terminal verdict** -- the four-status set + `evidence[]` + `blocking_reasons[]`; `pass` only
   when a named-human approval is recorded; no numeric score (rule 9).
6. **See also** -- the pack, the checklist, the stage authority, F016/F027, and the C086 cited
   instance (by reference).

Re-check after design: the Constitution Check above still holds -- the design adds no gate, no
status, no rule, no executor, and keeps the sign-off agent-un-fillable.

## Complexity Tracking

No Constitution Check violations -- this table is intentionally empty.
