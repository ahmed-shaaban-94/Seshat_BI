# Implementation Plan: Customer Domain KPI Overview (domains/customer.md)

**Branch**: `042-customer-domain-kpi-contracts-missing` | **Date**: 2026-06-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/042-customer-domain-kpi-contracts-missing/spec.md`

## Summary

Author exactly ONE generic-retail committed-text file -- `skills/retail-kpi-knowledge/domains/customer.md`
-- mirroring the 11 sibling domain files, with all KPIs marked Planned (no customer metric contract
exists), a decision-questions table routing only to seeded contracts or honest Planned markers, and a
new PII/identity owner-ruling section that carries the constitution Principle-V stop-and-ask verbatim
and decides none of it. Then make two `INDEX.md` edits: resolve the Customer route from `[planned]` to
the new file, and bump the file-map domain count 11 -> 12. No contracts authored, no executor, no live
data, no readiness self-grant.

Technical approach: pure markdown authoring + two surgical edits to an existing markdown router. The
closest template precedent is `domains/inventory.md` (an all-Planned domain deferred on an unmade
prerequisite -- here the prerequisite is the human customer-identity ruling).

## Technical Context

**Language/Version**: N/A -- committed Markdown text only (no code).

**Primary Dependencies**: None. No executor, no DB, no pbi-cli, no network (Principle VIII static-first).

**Storage**: N/A -- the deliverable is a git-tracked `.md` file plus edits to a git-tracked `.md` router.

**Testing**: The repo static gate `retail check` over the changed text (must exit 0); a generic-retail
token scan (no C086/pharmacy specifics); a structural-mirror check against the 11 siblings; an
"all-Planned, zero fabricated contract/formula" scan; a "four Principle-V stops remain unanswered" check.
No unit/integration/E2E software tests apply (no code).

**Target Platform**: The retail-kpi-knowledge skill (agent-read documentation layer).

**Project Type**: Documentation / reasoning-layer content (layer-5 KPI knowledge). Not an application.

**Performance Goals**: N/A (static text).

**Constraints**: ASCII + UTF-8 no BOM (`--`, `->`, no glyphs; constitution rule IX). Windows 260-char
path limit (names already short). Generic-only (Principle VII). No fabricated readiness/confidence
score (hard rule #9). Advances no readiness stage (Principle I).

**Scale/Scope**: One new file (~40-60 lines, sibling-sized) + 2 line edits in `INDEX.md`.

## Constitution Check

*GATE: Must pass before authoring. Re-checked after design.*

- **Principle I (Agent-First, Gate-Enforced)**: PASS -- reasoning-layer content; grants no readiness,
  ends a `[planned]` route on an honest seeded-overview note. No gate is self-disposed.
- **Principle V (Agent Stops at Judgment Calls)**: PASS -- the four judgment calls (identity/grain, PII
  publish-safety default-drop, business-segment rollup, product identity) are carried as explicit
  stop-and-ask markers in the file and recorded as OPEN in the spec; the agent answers none.
- **Principle VII (C086 Is An Example, Not The Schema)**: PASS -- file stays generic retail; no
  patient/insurance/prescription-loyalty token may appear (enforced by token scan in tasks).
- **Principle VIII (Static-First, Live Deferred)**: PASS -- committed text only; no executor, no live
  data, no fabricated number; KPIs stay categorical Planned markers.
- **Hard rule #9 (no fabricated confidence/readiness score)**: PASS -- the file emits none.

No violations -> Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/042-customer-domain-kpi-contracts-missing/
|-- spec.md            # /speckit-specify output (with Clarifications)
|-- plan.md            # this file (/speckit-plan output)
|-- tasks.md           # /speckit-tasks output
|-- analysis.md        # /speckit-analyze output (repo convention)
|-- plan-review.md     # adversarial plan-review output (repo convention)
`-- checklists/
    `-- requirements.md # spec quality checklist
```

No `research.md`, `data-model.md`, `quickstart.md`, or `contracts/` are produced: there is nothing to
research (template precedent already established), no data model (no data), no quickstart (no runnable
artifact), and -- critically -- NO contracts (authoring a customer contract is explicitly out of scope;
each would need the F009 contract process + a confirmed PII ruling).

### Source Code (repository root)

The "implementation" (executed later by a human-approved run, NOT by this planning workflow) touches
exactly these committed-text paths:

```text
skills/retail-kpi-knowledge/
|-- domains/
|   `-- customer.md     # NEW -- the single deliverable file
`-- INDEX.md            # EDIT -- line ~59 Customer route; file-map "(11 files)" -> "(12 files)"
```

**Structure Decision**: Documentation-content feature. No `src/` or `tests/` tree is created. The unit
of work is one new domain-overview markdown file plus two surgical edits to the existing router. The
verification surface is the static `retail check` gate plus the content scans listed under Testing --
there is no compiled or executed code.

## Complexity Tracking

No constitution violations. Section intentionally empty.
