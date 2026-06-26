# 0011 -- Safe auto-updates: Lane A automerges only on green CI, below the readiness spine; Lane B human review; Lane C never automerges

- **Date:** 2026-06-26
- **Status:** Accepted (F031; the policy is authored as two operations docs --
  `docs/operations/dependency-update-policy.md` and
  `docs/operations/adapter-update-policy.md`. No runtime code, no CI/bot config,
  no `retail check` rule, no readiness stage added.)
- **Roadmap feature:** F031 (on-disk spec `025-adapter-maintenance-policy`). When the
  spec-dir number (025) and the F-number (F031) disagree, the roadmap F-number wins.
- **Authority category:** Maintenance Automation  *(sub-axis: none / `--`)* -- per
  `docs/architecture/product-modules.md` (the five-category contract, F024 / on-disk
  spec 018). Maintenance Automation runs WITHOUT a per-invocation human trigger
  (scheduled / CI / a bot PR), emits ONLY derived evidence (a lane label, recorded
  per-check results), never creates truth, and never self-approves. It carries no
  Module capability level and no Adapter connectivity level -- those sub-vocabularies
  belong to the Product Module / Execution Adapter categories, not to this one, and
  Maintenance Automation declares no connectivity level (only Adapters do).

## Context

Constitution Principle II ("Depend, Never Fork") is the kit's load-bearing posture:
the opinion lives in this repo, the engine is borrowed and independently upgradeable,
and there is no "fork tax". That principle is only true in practice if there is a
SAFE, repeatable way to take an upstream upgrade. Without a written policy, every
dependency bump is an ad-hoc judgment call -- a dev-tool patch, a major Postgres
driver change, and a Power BI execution-adapter upgrade all flow through the same
undisciplined door, and the easiest path ("merge it, tests are green") is exactly the
path that can silently regress a readiness gate, strand the repo on a snapshot, or
pull a transitive secret / local path into a tracked file.

The single biggest design tension is the apparent contradiction between "automerge"
and "no tool self-approves" (Principle V / Core Authority owns truth). A green CI run
is sufficient to merge a mechanical dev-tool bump but is NOT sufficient to prove an
adapter's contract with the readiness gates is intact, nor to approve a credential /
publish-capable change. This ADR records the decision that resolves that tension by
placing automerge strictly BELOW the readiness spine and encoding WHERE human judgment
is mandatory as three update lanes.

## Decision

### 1. Three update lanes, by blast radius

Every update PR is classified into EXACTLY ONE lane. The lane decides automerge
eligibility and whether a named human review is mandatory.

| Lane | Membership (examples, not exhaustive) | Automerge | Human review |
|------|----------------------------------------|-----------|--------------|
| **Lane A -- allowed-auto** | Ruff, Pytest, pre-commit / dev tools, GitHub Actions patch/minor, docs tooling | eligible ONLY if every required check is green | not required when checks are green |
| **Lane B -- human-review-required** | `dbt-core`, `dbt-postgres`, `dagster`, `dagster-dbt`, `psycopg2`, Postgres-driver changes, Power BI modeling utilities | forbidden | a NAMED human reviewer MUST approve |
| **Lane C -- never-automerge** | the official Power BI MCP / execution adapter, anything publish-capable, major DB-driver changes, anything touching credentials / auth, anything that changes semantic-model behavior | forbidden under any check state | a NAMED human reviewer MUST approve |

The package names above are LANE-MEMBERSHIP examples (Principle VII): they are the
borrowed-engine and toolchain names the policy governs, not worked-example specifics.
The full lane table and the transitive-escalation rule live in
`docs/operations/dependency-update-policy.md`.

### 2. Automerge is allowed for Lane A on green CI, and ONLY there

Automerging a low-risk dev-tool bump on green CI is a MECHANICAL change in the
dependency / CI plane only. It does NOT define business meaning, approve a metric or
mapping, publish a Power BI artifact, clear a blocker, or move any readiness stage to
`pass`. Lane B and Lane C MUST NEVER automerge: green checks are necessary but never
sufficient for them, because a green build does not prove an adapter's contract with
the gates is intact and a publish-capable / credential change needs a human.

### 3. The no-bypass invariant (load-bearing -- stated identically in both ops docs)

> No update in ANY lane may bypass a readiness gate or move any stage to `pass`;
> automerge lives entirely below the readiness spine.

An update that could regress a gate (`retail check`, `retail validate`, the
silver/gold build, the semantic-model checks) MUST re-pass that gate before merge. It
never auto-promotes a stage and never clears a blocker. This is what keeps automerge
inside the Constitution: the lanes encode where human judgment is mandatory (Lane B
always; Lane C always, never automerge) versus where green gates suffice (Lane A), and
NONE of the three may touch the readiness spine.

### 4. The compatibility verdict is the human's; the policy routes and records

A major-version bump (Lane B/C) or any adapter update triggers an explicit
compatibility review naming the gates it could regress, the named reviewer, and the
outcome. The policy ROUTES the trigger and RECORDS the evidence; the verdict is the
named reviewer's (Principle V). The durable compatibility record lives in F032's
matrix (`docs/operations/adapter-compatibility-matrix.md`), which is the version-truth
record this policy reads and enforces against. F032 RECORDS; F031 READS and ENFORCES.

### 5. No fake confidence

The policy emits NO health / maturity / confidence score for a dependency or adapter
(hard rule #9). An update's status is the explicit per-check pass/fail plus the lane
and (for B/C) the named reviewer -- never a fabricated number. Any maturity score is
DEFERRED (see F033 Release & Maturity Management).

## Consequences

- Principle II is operational: the borrowed engines (dbt, Dagster, the Power BI
  execution adapter, the Postgres driver, the dev toolchain) stay current and
  upgradeable with no fork tax and no stranding, while the readiness gates stay the
  sole authority over `pass`/`fail`.
- The static `retail check` gate is untouched: this feature adds no rule, no
  validator, and no CLI verb (the checker stays exit 0). The required-check runtime is
  the EXISTING CI plus a human reviewer; no new runtime is built.
- Principle V is honored: Lane B/C mandate a named reviewer; the compatibility verdict
  is the human's; no automerge ever moves a stage to `pass`.
- Principle IX is honored: the no-secrets / no-paths check is a hard merge blocker in
  every lane.
- The optional bot config (`.github/dependabot.yml` / `renovate.json`) is PLANNED, not
  created: if later added it ENCODES these lanes (Lane A auto-eligible, Lane B/C
  review-required) and is itself subject to this policy. The dependabot-vs-renovate
  choice is deferred to the implementation slice.

## Alternatives considered

- **No automerge at all (every bump waits for a human).** Rejected: it re-introduces a
  fork-tax-by-friction on every trivial dev-tool bump, which is the precise failure
  Principle II forbids. The friction would discourage taking upgrades and strand the
  repo on snapshots -- the opposite of "depend, never fork".
- **Automerge everything on green CI.** Rejected: a green build does NOT prove an
  adapter's contract with the readiness gates is intact, and a publish-capable or
  credential / auth change needs a named human regardless of green checks. This would
  let a Lane C effect ride in behind a green run.
- **The three-lane split (chosen).** Lane A automerges on green CI below the spine;
  Lane B requires a named human review; Lane C never automerges. This is the only
  option that keeps the safe upgrade path (Principle II) without letting any update
  touch the readiness spine (Principle V), and it is the encoding the optional bot
  config would later mechanize.

## Numbering note

ADR numbers 0001-0007 are shipped on disk and are never reused. The F024-F033
companion tier reserves the appended block 0008-0011: **0008** (F024, shipped on disk),
**0009** (F029, reserved -- not yet authored), **0010** (F030, reserved -- not yet
authored), and **0011** (F031, this ADR). ADR **0012** (the P2 commit-types decision)
was authored after this block and explicitly reserved 0008-0011 for this tier, so
authoring 0011 here is the expected fill of a reserved slot, not a collision. The
earlier "matrix double-booking" concern is resolved: the F032 compatibility matrix
(`docs/operations/adapter-compatibility-matrix.md`) claims NO ADR number -- it is an
operations record, not a decision record -- so the fixed allotment 0008/0009/0010/0011
stands with no double-booking.

## See also

- The policy this ADR governs: `docs/operations/dependency-update-policy.md` (the
  lanes + required checks for the toolchain + drivers) and
  `docs/operations/adapter-update-policy.md` (the adapter overlay + compatibility-review
  trigger).
- The version-truth record this policy reads and enforces against:
  `docs/operations/adapter-compatibility-matrix.md` (F032, on-disk spec 026).
- The category home (Maintenance Automation): F024 Companion Tools Architecture,
  `docs/architecture/product-modules.md`, ADR `0008-core-authority-vs-product-modules.md`.
- The governed adapters (recorded / governed here, NOT redefined): F029 (dbt)
  `specs/023-dbt-transformation-adapter/`, F030 (Dagster)
  `specs/024-dagster-orchestration-adapter/`, F016 (Power BI execution adapter, parked).
- The required-check runtime: `.github/workflows/ci.yml`; the `retail check` static
  surface and the `retail validate` live surface.
- The principles: `.specify/memory/constitution.md` (Principles II, V, VIII, IX); hard
  rule #9 (no fake confidence), `docs/roadmap/roadmap.md`.
- The worked-example reference (cited, never inlined): `docs/worked-examples/c086-pharmacy.md`.
- The spec: `specs/025-adapter-maintenance-policy/spec.md`.
