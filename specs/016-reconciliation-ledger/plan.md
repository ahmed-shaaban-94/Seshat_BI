# Implementation Plan: Reconciliation Ledger -- a durable history of cross-layer reconciliation results

**Branch**: `016-reconciliation-ledger` | **Date**: 2026-06-24 | **Spec**: `specs/016-reconciliation-ledger/spec.md`

**Input**: Feature specification from `specs/016-reconciliation-ledger/spec.md`

## Summary

Define a **reconciliation ledger**: a durable, append-only history of cross-layer reconciliation
**results** over time, one immutable entry per result (provenance + measured per-measure/row
deltas + `pass`/`fail` + evidence). It is a **history layer over** the existing `retail validate`
reconciliation check (RC16) -- it records that check's verdict so the proof survives the run; it
is **not** a new validator and adds **no new gate**. It advances readiness stage **Gold Ready** by
giving that stage durable, historical evidence instead of a single point-in-time snapshot.

**Technical approach (this slice): docs/templates only.** Per the "Later" tier and hard rule #8,
this slice ships a generic **entry template** plus **hand-filled example entries** (one `pass`,
one `fail`) and the design narrative that positions the ledger against `retail validate`,
`reconciliation-report.md`, and `gold-ready.md`. **No runtime, no storage, no DB writes, no CLI.**
The store, the auto-append wiring from `retail validate`, and a query/history surface are named,
deferred follow-ups.

## Technical Context

**Language/Version**: N/A this slice (docs/templates only). Markdown + a small YAML snippet for the
example readiness-status evidence citation. The eventual deferred runtime would target Python 3 /
the existing `src/retail/` stdlib-only core (no new dependency), but no code is written here.

**Primary Dependencies**: None added. The ledger **consumes** the output of the already-built
`retail validate` reconciliation check (feature 004); it introduces no new dependency and does not
import psycopg2 or anything else (the static core's `dependencies = []` invariant is untouched).

**Storage**: **Deferred.** No store is built this slice. The design names the *intended* placement
(per-table, under the `mappings/<table>/` convention, ADR 0003) and leaves the concrete
file/path/format as a recorded decision (see Structure Decision); a real store is a later spec.

**Testing**: No code -> no unit tests this slice. Verification is by inspection + `retail check`
staying green (the new template is committed text the static checker sees) + a deterministic
ASCII/UTF-8-no-BOM check on the new files. The hand-filled example entries ARE the test of the
template's shape (US1/US2/US3 independent tests).

**Target Platform**: Repo-tracked text (Windows-safe paths, UTF-8 no BOM). Same constraints as the
other templates.

**Project Type**: Single project (the kit). This slice touches `templates/` and `docs/` only.

**Performance Goals**: N/A (no runtime).

**Constraints**: ASCII + UTF-8 without BOM; generic (no worked-example specifics, #7); Windows
`MAX_PATH` (repo-relative paths short); no fabricated numbers anywhere (#9); append-only invariant
stated in the design.

**Scale/Scope**: One new generic template, two example entries, one design doc section (or a short
standalone design note), and cross-link updates. No change to any gate, validator, or `src/`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | This slice |
|-----------|------|------------|
| I. Agent-First, Gate-Enforced | adds no authority over a gate's pass | PASS -- the ledger records the `retail validate` verdict; the gate exit code remains the authority. No new gate. |
| II. Depend, Never Fork | no pbi-cli fork/vendor | PASS -- not touched. |
| III. Medallion, Postgres-First, Gold-Only | no new read surface; gold-only intact | PASS -- records reconciliation results; reads nothing new. Any future store is gold-side, named not built. |
| IV. Source Mapping Before Silver | mapping gate unchanged | PASS -- the ledger is downstream (Gold Ready), not a mapping-gate change. |
| V. Agent Stops at Judgment Calls | grain/identity reserved for humans | PASS -- the ledger **grain** (one-entry-per-run vs per-measure; one-ledger-per-table vs shared) is left **OPEN for human** (spec Deferred). Not auto-decided. |
| VI. Defaults Then Deviations | start from RC defaults | PASS -- records the RC16 reconciliation result; introduces no competing default. |
| VII. C086 Is An Example | generic templates | PASS -- template is placeholders only; worked example cited, never copied. |
| VIII. Static-First, Live Deferred | no new live validator; respects deferred boundary | PASS -- adds no validator; records the existing live check; **no entry** when validate did not run (no fabricated pass, #9). |
| IX. Secrets and Reproducibility | no secrets; UTF-8 no BOM; short paths | PASS -- docs only; no creds; ASCII/UTF-8-no-BOM; short repo-relative paths. |

**Readiness-spine check**: advances **Gold Ready** with durable evidence; changes no stage gate;
verdict vocabulary (`pass`/`fail`) consistent with the stage. No fabricated confidence (#9). PASS.

**Scope-discipline check (hard rule #8, CLAUDE.md YAGNI)**: design/template first; runtime
deferred. PASS -- the slice adds the seam (the entry contract), not the implementation.

**Result: no violations.** Complexity Tracking below is intentionally empty.

## Project Structure

### Documentation (this feature)

```text
specs/016-reconciliation-ledger/
|-- spec.md        # done (specify step)
|-- plan.md        # this file (plan step)
|-- tasks.md       # tasks step
`-- analysis.md    # analyze step (cross-artifact findings)
```

No `research.md` / `data-model.md` / `contracts/` are needed: the "design" is a single generic
template plus example entries (no API, no schema, no novel research). They are intentionally
omitted to respect scope discipline.

### Source Code (repository root)

This slice writes **no source code**. The concrete deliverables are docs/templates:

```text
templates/
`-- reconciliation-ledger-entry.md      # NEW (this slice) -- the generic entry template
                                        #   (filename to be confirmed at tasks; this is the
                                        #    recommended default, sibling of reconciliation-report.md)

docs/readiness/
`-- gold-ready.md                       # EDIT -- add the ledger as a durable-evidence option
                                        #   for gold_ready.evidence[] (no gate change)

# Example entries: the two hand-filled examples (one pass, one fail) live INLINE in the template
# as worked illustrations (placeholders/generic), OR as a short companion example block. Decided
# at tasks; default = inline examples within the template (keeps one file, generic, citable).
```

Explicitly **NOT** created this slice (deferred, named in spec): any `src/retail/` code, any
`warehouse/migrations/*` ledger table, any `retail` CLI subcommand, any auto-append writer, any
query/history surface.

**Structure Decision**: Single-project, docs/templates-only change. The new artifact is a generic
template under `templates/` (the kit's home for the five gate artifacts + readiness templates),
named as the temporal sibling of `reconciliation-report.md`. A table's *actual* ledger is intended
to live per-table under the `mappings/<table>/` convention (ADR 0003), but **the concrete
storage file/path/format is deferred** (spec FR-007 / Deferred) -- this slice fixes the entry
*shape*, not the store. The two example entries demonstrate the shape; they carry only generic
placeholders (#7).

## Phasing (within this docs/templates slice)

- **Phase 0 (research)**: none required. The inputs are all in-repo and already understood:
  `retail validate`'s reconciliation output shape (feature 004 / `validate.py`),
  `reconciliation-report.md`'s tables, `gold-ready.md`'s evidence/blocking model, and the
  readiness status vocabulary. No external research, no `research.md`.
- **Phase 1 (design = the deliverable)**: author the generic `reconciliation-ledger-entry.md`
  template (provenance block + per-measure result table + row-count line + overall verdict +
  evidence refs + the append-only/correction invariant), with two hand-filled example entries
  (one `pass` penny-exact, one `fail` with a measured non-zero delta). Add the temporal-complement
  framing and the Gold Ready evidence wiring (doc-level, no gate change). Update cross-links.
- **Phase 2 (tasks)**: produced by the tasks step (`tasks.md`), grouped by the three user stories.

## Risks & mitigations

- **Risk: scope creep into building the store.** Mitigation: FR-011 + this plan forbid runtime;
  the changed-file set is verified to be docs/templates only (SC-007).
- **Risk: the template implies a confidence number.** Mitigation: #9 is enforced -- every field is
  a measured value/difference; reviewer checks no score appears (SC-003); `fail` example shows a
  recorded cent.
- **Risk: it reads as a new gate.** Mitigation: the design states "no new validator, no new gate"
  (FR-008, SC-005); the ledger only records the `retail validate` verdict.
- **Risk: grain decided implicitly.** Mitigation: the grain is left OPEN for a human (Principle V);
  the plan adopts one-entry-per-run-per-table only as a *working default* the spec marks as not
  finalized.

## Complexity Tracking

> No Constitution Check violations. No entries.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | -- | -- |

## See also

- Spec: `specs/016-reconciliation-ledger/spec.md`.
- The check it records: `src/retail/validate.py`, `specs/004-retail-validate/spec.md` (RC16).
- The point-in-time complement: `templates/reconciliation-report.md`.
- The stage advanced: `docs/readiness/gold-ready.md`; spine `docs/readiness/readiness-model.md`.
- Governing rules: constitution Principle VIII + readiness-spine section; roadmap F015; hard rules
  #4, #7, #8, #9. ADR 0003 (`mappings/<table>/` placement). ADR 0002 RC16.
