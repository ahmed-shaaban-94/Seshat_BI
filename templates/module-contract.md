<!--
=============================================================================
 module-contract.md  --  the copy-me authority declaration every Product Module fills
=============================================================================
 Tower BI Agent Kit  -  feature F024 (Companion Tools Architecture).
 See: docs/architecture/product-modules.md (the normative reference -- the five
      categories, the authority matrix, the two sub-vocabularies),
      docs/architecture/core-vs-modules-and-adapters.md (the prose narrative + seam),
      docs/decisions/0008-core-authority-vs-product-modules.md (the decision record).

 WHAT THIS IS
   A GENERIC, copy-me declaration. A Product Module is a focused tool that consumes
   Core Authority and presents, summarizes, or derives from it -- it never creates
   truth. Every Module fills one copy of this contract to declare, up front and
   reviewably: its capability level, the Core Authority it reads, the derived
   evidence it writes, and the operations the authority matrix forbids it.

 THE BOUNDARY  (verbatim from product-modules.md -- do not drift)
   A Product Module MUST NOT create truth: it cannot define business meaning,
   approve a metric or mapping, or move a readiness stage to `pass`. Those are Core
   Authority operations owned by a named human (Principle V). A Module reads,
   summarizes, visualizes, MAY write derived evidence (if `artifact-writing` or
   `execution-capable`), and MAY execute an approved step against the LOCAL committed
   working set (if `execution-capable`). If it would connect to a DB / external
   service or publish, it is an Execution Adapter, not a Module -- use
   templates/adapter-contract.md instead (see the module-vs-adapter seam).

 HOW TO USE
   Copy this file next to the module it declares (or under the module's own dir),
   fill every <ANGLE-BRACKET> field, delete this comment banner, and keep it
   committed alongside the tool. Generic -- no C086 / retail_store_sales values.
=============================================================================
-->

# Module Contract -- <MODULE NAME>

- **Authority category:** Product Module
- **Capability level:** `<read-only | artifact-writing | execution-capable>`  *(exactly one)*
- **Product layer:** `<1-6>`  *(the functional axis -- see docs/roadmap/roadmap.md; orthogonal to category)*
- **Roadmap feature:** `<Fxxx>`  **On-disk spec:** `<specs/0NN-...>`
- **Owner:** `<named human or role>`
- **Status:** `<Planned | Authored | Shipped>`

## What it does (one line)

> `<one sentence: what this module consumes from Core Authority and what it presents/derives>`

## Core Authority it READS

List the committed truth artifacts this module reads. It reads; it never writes these.

- `<e.g. mappings/<table>/readiness-status.yaml -- current_stage, per-stage status, approvals[], blocking_reasons[]>`
- `<e.g. source-map.yaml -- declared grain, PK, PII, placement>`
- `<...>`

## Derived evidence it WRITES

Only if capability is `artifact-writing` or `execution-capable`. A `read-only` module
writes NOTHING -- state "none" and leave the list empty. Derived evidence is composed
FROM committed evidence; it is never a new approval, metric definition, or stage change.

- `<e.g. templates/<derived-report>.md -- a composed summary, no new truth>`
- `<... or: none (read-only)>`

## Approved step it EXECUTES

Only if capability is `execution-capable`. The step MUST already be approved in Core
Authority, and it MUST touch only the LOCAL committed working set (no DB, no publish --
that would make it an Adapter). A `read-only` or `artifact-writing` module states "none".

- `<e.g. rewrites a committed local index from approved evidence>`
- `<... or: none>`

## Forbidden operations (the matrix says NO)

These hold for EVERY Product Module regardless of capability level:

- MUST NOT create truth: no defining business meaning, no approving a metric/mapping.
- MUST NOT grant approval or move a readiness stage to `pass` (named-human / Core Authority only).
- MUST NOT connect to a DB or external service, and MUST NOT publish a Power BI artifact
  (those are Execution Adapter capabilities -- reclassify if needed).
- MUST NOT emit a numeric / maturity / confidence score (hard rule #9).
- A `read-only` module additionally MUST NOT write any derived evidence or execute any step.

## How it handles a missing input

When a required Core Authority input is absent or a stage is not yet `pass`, the module
SURFACES it as a blocker and stops -- it never fabricates the input, self-approves, or
proceeds past the missing gate (Principle V; stop-and-ask).

- `<e.g. missing approval -> reported as a blocker, not auto-resolved>`

## See also

- The normative reference: `docs/architecture/product-modules.md`.
- The seam (Module vs Adapter): `docs/architecture/core-vs-modules-and-adapters.md`.
- The adapter contract (if this is actually an Adapter): `templates/adapter-contract.md`.
