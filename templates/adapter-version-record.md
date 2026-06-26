<!--
=============================================================================
 adapter-version-record.md  --  the copy-me record of ONE adapter's verified version
=============================================================================
 Seshat BI Agent Kit  -  on-disk spec 026 / roadmap feature F032
                          (Adapter Compatibility Matrix).
 Authority category: Maintenance Automation (per docs/architecture/product-modules.md;
   the five-category contract is F024 / on-disk spec 018). Sub-axis: none (--).
   Maintenance Automation runs WITHOUT a per-invocation human trigger and emits ONLY
   derived evidence; it never creates truth and never self-approves. A version record
   carries no Module capability level and no Adapter connectivity level -- those
   sub-vocabularies belong to the Product Module / Execution Adapter categories, not
   to this one.
 See: docs/operations/adapter-compatibility-matrix.md (the matrix this record is a row of),
      docs/architecture/product-modules.md (the normative category reference),
      docs/readiness/readiness-model.md (the four-status vocabulary + no-fake-confidence).

 WHAT THIS IS
   A GENERIC, copy-me record. It is the atomic unit of the adapter compatibility
   matrix: the verified-compatible facts for ONE adapter/dependency the kit pins --
   its supported version RANGE, its named required SMOKE TEST, that test's last
   result + date, and the NAMED OWNER who attested it. A future dependency-update PR
   fills/updates one of these per adapter it moves. It is a RECORD, never an
   enforcement rule and never adapter code.

 THE RECORD / POLICY BOUNDARY  (verbatim across all F032 artifacts -- do not drift)
   F032 is the RECORD: what is verified-compatible (supported ranges + smoke-test
   status + last-verified dates + owners). F031 (Adapter Maintenance Policy) is the
   POLICY: what a dependency-update PR must DO about a violation, when to re-verify,
   and what to block. This record carries NO PR gate, NO CI fail condition, NO merge
   block, NO enforcement logic. It states the truth; F031 decides what to do about it.

 THE RECORD / BUILD BOUNDARY  (verbatim across all F032 artifacts -- do not drift)
   F032 RECORDS the supported versions of the F029 dbt adapter, the F030 Dagster
   adapter, and the F016 Power BI execution adapter. It MUST NOT author, modify, or
   execute any of those adapters' runtime code, connection logic, or transformations.
   It NAMES the required smoke test and records its last result; it does NOT author
   or run the smoke test, nor wire it into CI -- that is the adapter features' and a
   later automation slice's runtime work.

 NO FAKE CONFIDENCE  (hard rule #9 / Principle IX / readiness-model.md)
   Status is recorded with EXACTLY the four readiness statuses
   (not_started | blocked | warning | pass) PLUS `unknown` for the compatibility
   sense (an untested version/range/adapter). An UNKNOWN version is NEVER recorded as
   supported, NEVER `pass`, NEVER inferred from "it probably works". There is NO
   numeric / maturity / confidence score field anywhere, and a filled copy MUST NOT
   add one. The only path to a supported status is a named owner attesting a PASSED
   smoke test, recorded as evidence (owner + run date). `parked` is NOT a status
   value -- it is a NOTE in blocking_reasons explaining WHY a row is `unknown`.

 GENERIC  (Principle VII)
   No worked-example specifics. C086 / retail_store_sales is a filled instance cited
   as a reference, never inlined. Concrete version strings in a real filled record are
   environment facts; the values below are deliberately obvious placeholders. No
   secrets, DSNs, tokens, or local machine paths (Principle IX).

 HOW TO USE
   Copy this file (or this block, as one matrix row) per adapter/dependency the kit
   pins, fill every <ANGLE-BRACKET> field, delete this comment banner, and keep it
   committed. The agent FILLS the record from attested evidence; it never self-attests
   as owner and never self-promotes a cell to supported (Principle V posture).
=============================================================================
-->

# Adapter Version Record -- `<adapter / dependency name>`

- **Authority category:** Maintenance Automation  *(sub-axis: none / `--`)*
- **Roadmap feature:** F032  **On-disk spec:** `specs/026-adapter-compatibility-matrix`
- **Part of:** `docs/operations/adapter-compatibility-matrix.md` (one row of the matrix)
- **Readiness stage affected:** none directly (a Maintenance Automation durability record, not a spine gate)

## What this records (one line)

> `<one sentence: which adapter/dependency this pins, the version range verified-compatible with the kit, and the smoke test that proves it>`

## The record (the fields a filled copy carries)

| Field | Value | Notes |
|-------|-------|-------|
| `adapter` | `<adapter / dependency name>` | e.g. the transformation adapter, the orchestration adapter, a runtime, a database. NAMED, never blank. |
| `range` | `<floor + tested ceiling, e.g. >=X,<Y>` | A version RANGE, not a single bare pinned point. A floor is required; an untested ceiling is `unknown` (see below), never assumed. |
| `smoke_test` | `<named smoke test>` | The NAMED check whose PASS is the evidence a version is supported. F032 names it + records its last result; it does NOT author or run it. A row with no smoke test is a defect. |
| `status` | `<not_started | blocked | warning | pass | unknown>` | One of the four readiness statuses PLUS `unknown`. NO sixth value. `parked` is a note, not a status. |
| `last_verified` | `<YYYY-MM-DD | unknown>` | The date the smoke test last ran against this range. Point-in-time evidence; staleness is shown honestly, never hidden. `unknown` if never run. |
| `owner` | `<named human / role | UNASSIGNED>` | The named human who ATTESTED a passed smoke test. The agent never self-attests. A supported row with no owner reads `UNASSIGNED` and is flagged. |
| `evidence[]` | `<see below>` | For a `pass`: the passed smoke test + its run date + the attesting owner. A `pass` with no evidence is a defect. |
| `blocking_reasons[]` | `<see below>` | Required whenever status is `blocked` or `unknown`; the concrete missing-evidence reason. |

### `evidence[]`

For a SUPPORTED (`pass`) row, evidence MUST cite the passed smoke test, its run date,
and the named attesting owner -- never a number, never an adjective.

- `<e.g. "smoke test <name> passed against <range> on <YYYY-MM-DD>, attested by <named owner>">`

### `blocking_reasons[]`

Required when status is `blocked` or `unknown`. One concrete missing-evidence reason
per entry. This is where `parked` is recorded as a NOTE.

- `<e.g. "smoke test not run against this version -> unknown">`
- `<e.g. "upper bound untested -> ceiling unknown, not assumed compatible">`
- `<e.g. "adapter parked, not yet exercised -> unknown (parked is a note, not a status)">`

## The promotion rule (the only path to supported)

A row reaches a SUPPORTED status (`pass`) ONLY when a NAMED OWNER attests a PASSED
smoke test, recorded as evidence (the smoke-test result + its run date + the owner).

- The agent RECOMMENDS and RECORDS; the named owner DECIDES and ATTESTS.
- The agent MUST NOT self-promote a cell to supported and MUST NOT self-attest as owner.
- A named-but-unrun smoke test does NOT make a version supported -- it is `unknown`
  ("named, not yet run") until the test actually runs and passes.

## The stop-and-ask (UNKNOWN is never assumed compatible)

When a version, range, or adapter has NOT been verified by its smoke test, the record
marks it `unknown` and STOPS -- it never infers "compatible" from a version being
"close enough" or "probably fine" (Principle V posture: surface the uncertainty, never
bury it under a guessed status).

- If asked to "just mark it compatible" for an untested version: DECLINE, record
  `unknown`, cite readiness-model "No fake confidence", and record the missing
  smoke-test run as the `blocking_reasons[]` entry.
- If asked for a single numeric compatibility / confidence score: DECLINE, cite hard
  rule #9 / Principle IX, and record explicit status + evidence instead.
- The classic data judgment calls (grain / PII / business rollup) are N/A for a
  version record -- do NOT fake-fit them. The only judgment call here is "is this
  version verified by a passed smoke test?".

## Forbidden operations (the boundaries the matrix says NO to)

These hold for EVERY adapter version record:

- MUST NOT record any untested version/range/adapter as supported, `pass`, or
  compatible by inference -- it is `unknown` until a passed smoke test attests it.
- MUST NOT emit a numeric / maturity / confidence score (hard rule #9 / Principle IX).
- MUST NOT add a PR gate, a CI fail condition, a merge block, or any enforcement logic
  (that is the F031 policy -- the record/policy boundary).
- MUST NOT author, modify, or execute any adapter's runtime code, connection logic, or
  transformations, and MUST NOT author or run the smoke test (the record/build boundary).
- MUST NOT self-attest (the agent as owner) or self-promote a cell to supported
  (Principle V posture).
- MUST NOT inline C086 / retail_store_sales specifics, secrets, DSNs, tokens, or local
  machine paths (Principles VII / IX).

## Generic example (placeholders only -- zero C086)

> Shape only; every value is an obvious placeholder. Delete or replace when filling.

| Field | Example value |
|-------|---------------|
| `adapter` | the transformation adapter (against `<tool>`) |
| `range` | `<tool> >=X.0,<Y.0` (floor `X.0` tested; ceiling `Y.0` untested) |
| `smoke_test` | `<named smoke test, e.g. transform-smoke>` |
| `status` | `unknown` |
| `last_verified` | `unknown` |
| `owner` | `UNASSIGNED` |
| `evidence[]` | (none yet -- no passed smoke-test run) |
| `blocking_reasons[]` | `["smoke test <name> not yet run against <tool> >=X.0 -> unknown", "ceiling <Y.0> untested -> upper bound unknown"]` |

## See also

- The matrix this record is a row of: `docs/operations/adapter-compatibility-matrix.md`.
- The policy half of the pair (enforces against this record): F031 Adapter Maintenance
  Policy, `specs/025-adapter-maintenance-policy/`.
- The category home (Maintenance Automation): F024 Companion Tools Architecture,
  `docs/architecture/product-modules.md`, `specs/018-companion-tools-architecture/`.
- The four-status vocabulary + no-fake-confidence rule: `docs/readiness/readiness-model.md`.
- The tracked adapters (recorded here, NOT built here): F029 (dbt), F030 (Dagster),
  F016 (Power BI execution adapter).
- The roadmap row + hard rules 7/8/9: `docs/roadmap/roadmap.md` (F032).
- The spec: `specs/026-adapter-compatibility-matrix/spec.md`.
