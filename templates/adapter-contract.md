<!--
=============================================================================
 adapter-contract.md  --  the copy-me authority declaration every Execution Adapter fills
=============================================================================
 Tower BI Agent Kit  -  feature F024 (Companion Tools Architecture).
 See: docs/architecture/product-modules.md (the normative reference -- the five
      categories, the authority matrix, the two sub-vocabularies),
      docs/architecture/core-vs-modules-and-adapters.md (the prose narrative + seam),
      docs/decisions/0008-core-authority-vs-product-modules.md (the decision record).

 WHAT THIS IS
   A GENERIC, copy-me declaration. An Execution Adapter is a tool that crosses an
   EXTERNAL trust/connectivity boundary to MATERIALIZE or PUBLISH an already-approved
   artifact. It is execution-only and gated. Every Adapter fills one copy of this
   contract to declare, up front and reviewably: its connectivity level, the gate it
   is downstream of, the approved artifact it materializes/publishes, and the
   operations the authority matrix forbids it.

 THE BOUNDARY  (verbatim from product-modules.md -- do not drift)
   An Execution Adapter is EXECUTION-ONLY. It MUST NOT define metrics, mappings,
   semantic logic, or dashboard design; the definition it executes MUST already exist
   in Core Authority. It MUST NOT create truth or grant approval (named-human / Core
   Authority only). It runs downstream of a gate and fails closed when its required
   approval/evidence is absent. If a tool executes only against the LOCAL committed
   working set (no DB, no external service, no publish), it is an `execution-capable`
   Product Module, NOT an Adapter -- use templates/module-contract.md instead (the
   module-vs-adapter seam).

 HOW TO USE
   Copy this file next to the adapter it declares (or under the adapter's own dir),
   fill every <ANGLE-BRACKET> field, delete this comment banner, and keep it
   committed alongside the tool. Generic -- no C086 / retail_store_sales values,
   no real hostnames / DSNs / credentials (Principle IX; secrets stay in git-ignored
   .env / .example files only).
=============================================================================
-->

# Adapter Contract -- <ADAPTER NAME>

- **Authority category:** Execution Adapter
- **Connectivity level:** `<local-only | DB-connected | external-service-connected | publish-capable>`  *(exactly one -- the STRONGEST it uses)*
- **Product layer:** `<1-6>`  *(the functional axis -- see docs/roadmap/roadmap.md; orthogonal to category)*
- **Roadmap feature:** `<Fxxx>`  **On-disk spec:** `<specs/0NN-...>`
- **Owner:** `<named human or role>`
- **Status:** `<Planned | Authored | Shipped>`

## What it does (one line)

> `<one sentence: which already-approved artifact this adapter materializes or publishes, and across which boundary>`

## Gate it is DOWNSTREAM of

An adapter only runs after a readiness gate has passed. Name the stage and the approval
it requires; the adapter fails closed if that approval/evidence is absent.

- **Gated on stage:** `<e.g. Semantic Model Ready = pass (for a publish-capable adapter)>`
- **Required approval / evidence:** `<e.g. named-human approval recorded in approvals[]>`
- **Fail-closed behavior:** `<what it does when the gate is not pass -- e.g. refuses to run, reports the missing approval as a blocker>`

## Boundaries it CROSSES (connectivity)

Enumerate EVERY external boundary this adapter touches. `publish-capable` implies the
publish gate applies. Record the strongest connectivity above; list all here.

- `<e.g. opens a connection to a live database (DB-connected)>`
- `<e.g. publishes a Power BI report (publish-capable)>`
- `<... or, for local-only: none beyond the local committed working set>`

## Approved artifact it MATERIALIZES / PUBLISHES

The definition MUST already exist in Core Authority. The adapter executes it; it does not
author it.

- `<e.g. materializes gold from an approved silver->gold transformation>`
- `<e.g. publishes an already-approved PBIP semantic model>`

## Derived run-evidence it WRITES

An adapter may write a RUN RECORD (what ran, when, with what result) as derived evidence.
This is never a new truth or approval.

- `<e.g. a run record / execution log committed as derived evidence>`

## Secrets handling (Principle IX)

- **Credentials:** `<names the git-ignored .env keys it reads -- e.g. DB_DSN; NEVER inline real values>`
- **Committed example only:** `<e.g. profiles.example.yml / .env.example with placeholder values>`

## Forbidden operations (the matrix says NO)

These hold for EVERY Execution Adapter regardless of connectivity level:

- MUST NOT define metrics, mappings, semantic logic, or dashboard design (execution-only).
- MUST NOT create truth or grant approval / move a stage to `pass` (named-human / Core Authority only).
- MUST NOT execute when its required approval/evidence is absent -- it fails closed.
- MUST NOT publish unless its connectivity level is `publish-capable`.
- MUST NOT emit a numeric / maturity / confidence score (hard rule #9).
- MUST NOT commit real hostnames / DSNs / credentials (Principle IX).

## How it handles a missing definition or approval

When the artifact it would execute is undefined, or the gate it is downstream of is not
`pass`, the adapter SURFACES it as a blocker and fails closed -- it never invents the
definition, self-approves, or executes past the missing gate (Principle V; stop-and-ask).

## See also

- The normative reference: `docs/architecture/product-modules.md`.
- The seam (Adapter vs Module): `docs/architecture/core-vs-modules-and-adapters.md`.
- The module contract (if this is actually a local-only Module): `templates/module-contract.md`.
- The canonical publish-capable adapter (parked): F016 Power BI execution adapter.
