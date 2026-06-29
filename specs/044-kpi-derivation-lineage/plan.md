# Implementation Plan: KPI Derivation-Lineage Contract (base-vs-derived dependency graph)

**Branch**: `044-kpi-derivation-lineage` | **Date**: 2026-06-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/044-kpi-derivation-lineage/spec.md`

## Summary

Add a DEFINE-layer base-vs-derived dependency graph over the 10 existing KPI-MC metric contracts,
using committed-text only:

1. Add a `**Derives from**` body section (not YAML front-matter) to
   `references/metric-contract-template.md` with generic placeholder guidance (list base-KPI
   dependencies by stable KPI-MC ID, or "none -- base KPI"; reference IDs never filenames).
2. Add a filled `**Derives from**` section to two exemplar contracts -- `contracts/net-sales.md`
   (KPI-MC-02, a base KPI: "none -- base KPI") and `contracts/average-transaction-value.md`
   (KPI-MC-05, a derived KPI: KPI-MC-02 + KPI-MC-04) -- each transcribed from that contract's own
   committed prose.
3. Author one new file `references/kpi-derivation-lineage.md` rendering the full 10-node graph
   (4 base + 6 derived), every edge transcribed from committed contract prose and citing its source.
4. If `INDEX.md` should route to the new doc, add a routing-table row and append it to the
   references prose summary (line ~85); no count is claimed by INDEX so no count bump is needed.

Technical approach: pure markdown authoring + surgical edits to existing markdown files. The edge
set is READ from the contracts, not invented (Principle V). The closest precedent is the F009
Metric Contract Store's "DEFINES, does not CHECK" boundary and the 042 domains/customer.md
docs-content feature.

## Technical Context

**Language/Version**: N/A -- committed Markdown text only (no code).

**Primary Dependencies**: None. No executor, no DB, no pbi-cli, no network, no generator
(Principle VIII static-first; hard-rule #8 docs-first defers any renderer).

**Storage**: N/A -- the deliverable is git-tracked `.md` files plus edits to git-tracked `.md`
files (one template, two contracts, optionally the INDEX router).

**Testing**: The repo static gate `retail check` over the changed text (must exit 0); a
generic-retail token scan (no C086/pharmacy specifics); an edge-provenance check (every edge in the
lineage doc traces to committed contract prose -- zero invented edges, zero edges to a non-contract
node such as growth / sales per sqm / vs-target / COGS / Return Value); an ASCII/UTF-8-no-BOM scan
over the NEW text; a "no fabricated readiness/confidence score" scan. No unit/integration/E2E
software tests apply (no code).

**Target Platform**: The retail-kpi-knowledge skill (agent-read documentation layer).

**Project Type**: Documentation / DEFINE-layer reasoning content (layer-5 KPI knowledge). Not an
application.

**Performance Goals**: N/A (static text).

**Constraints**: ASCII + UTF-8 no BOM in NEW text (`-`, `/`, `*`, `->`; no Unicode glyphs;
constitution Principle IX). Existing contract-body glyphs MUST NOT be altered (out of scope).
Windows 260-char path limit (names already short). Generic-only (Principle VII). No fabricated
readiness/confidence score (hard rule #9). Advances no readiness stage (Principle I). No invented
edge (Principle V).

**Scale/Scope**: One new file (`kpi-derivation-lineage.md`, ~50-90 lines) + a `**Derives from**`
section added to 3 existing files (1 template + 2 contracts) + an optional INDEX routing row.

## Constitution Check

*GATE: Must pass before authoring. Re-checked after design.*

- **Principle I (Agent-First, Gate-Enforced)**: PASS -- DEFINE/reasoning-layer content; grants no
  readiness, self-disposes no gate. Compliance is demonstrable by `retail check` exit 0 over the
  changed text.
- **Principle V (Agent Stops at Judgment Calls)**: PASS -- every edge is transcribed from committed
  contract prose and cites its source; declaring a NEW edge not in committed prose is carried as an
  explicit stop-and-ask the agent does not cross (recorded OPEN in spec ## Clarifications).
- **Principle VII (C086 Is An Example, Not The Schema)**: PASS -- template, exemplar contracts, and
  lineage doc use only the 10 generic KPI-MC contracts; no pharmacy KPI/billing-code/payer segment
  may appear (enforced by token scan in tasks).
- **Principle VIII (Static-First, Live Deferred)**: PASS -- committed text only; no executor, no
  live data, no generator, no fabricated number; the graph is a categorical relationship map.
- **Hard rule #8 (docs/templates first, automate later)**: PASS -- lineage doc is hand-authored; no
  generator is built.
- **Hard rule #9 (no fabricated confidence/readiness score)**: PASS -- the artifacts emit none.

No violations -> Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/044-kpi-derivation-lineage/
|-- spec.md            # /speckit-specify output (with Clarifications)
|-- plan.md            # this file (/speckit-plan output)
|-- tasks.md           # /speckit-tasks output
|-- analysis.md        # /speckit-analyze output (repo convention)
|-- plan-review.md     # adversarial plan-review output (repo convention)
`-- checklists/
    `-- requirements.md # spec quality checklist
```

No `research.md`, `data-model.md`, `quickstart.md`, or `contracts/` (Spec-Kit interface contracts)
are produced: the edge set is already established by reading the committed KPI-MC contracts (nothing
to research), there is no data model (no data -- the "entities" are markdown sections), no quickstart
(no runnable artifact), and no Spec-Kit interface contract (this is documentation, not an exposed
API). NOTE: "contracts" here means the EXISTING KPI metric contracts under
`skills/retail-kpi-knowledge/contracts/`, NOT a Spec-Kit `/contracts/` interface dir.

### Source Code (repository root)

The "implementation" (executed later by a human-approved run, NOT by this planning workflow) touches
exactly these committed-text paths:

```text
skills/retail-kpi-knowledge/
|-- references/
|   |-- metric-contract-template.md   # EDIT -- add a "**Derives from**" body section (placeholder)
|   `-- kpi-derivation-lineage.md     # NEW -- the full 10-node lineage graph
|-- contracts/
|   |-- net-sales.md                  # EDIT -- add "**Derives from**": none -- base KPI (KPI-MC-02)
|   `-- average-transaction-value.md  # EDIT -- add "**Derives from**": KPI-MC-02, KPI-MC-04 (KPI-MC-05)
`-- INDEX.md                          # OPTIONAL EDIT -- routing row to the new doc + append to the
                                      #   references prose summary (line ~85). No count is claimed by
                                      #   INDEX, so no count bump is needed.
```

**Structure Decision**: Documentation-content feature. No `src/` or `tests/` tree is created. The
unit of work is one new reference doc + a `**Derives from**` section in three existing files +
optionally one INDEX routing row. The verification surface is the static `retail check` gate plus
the content/provenance scans listed under Testing -- there is no compiled or executed code.

### Router-consistency finding (the 042 lesson, verified against the live repo)

`/speckit-analyze` cross-checks the three spec artifacts, NOT the live repo, so a stale router
pointer is invisible to it. Verified: `INDEX.md` does NOT enumerate the `references/` dir as a
counted file list -- it references specific reference files contextually in a routing table (lines
20-26) and a prose summary (line 85: "template, field requirements, id conventions, source map,
research notes"). Therefore FR-010 resolves as: there is NO file-count to bump; the only consistency
action is the OPTIONAL addition of a routing row + a prose-summary mention so a reader can find the
new lineage doc. This is captured as a task and explicitly recorded so the ratifier sees it was
considered, not missed.

## Complexity Tracking

No constitution violations. Section intentionally empty.
