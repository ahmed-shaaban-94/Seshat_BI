# 0010 -- Dagster is an orchestration adapter: it RUNS approved steps and DECIDES no stage

- **Date:** 2026-06-26
- **Status:** Accepted (F030; the adapter integration doc, the run-evidence template, and the
  adapter skill are authored as `docs/integrations/dagster-adapter.md`,
  `templates/dagster-run-evidence.md`, and `.claude/skills/dagster-orchestration-adapter/SKILL.md`.
  NO Dagster runtime code, NO `retail check` rule, NO readiness stage this slice -- docs-first,
  Principle VIII / roadmap rule #8. The concrete Dagster project is a later implementation slice.)
- **Roadmap feature:** F030 (on-disk spec `024-dagster-orchestration-adapter`). When the
  spec-dir number and the F-number disagree, the roadmap F-number wins.
- **Context:** The kit already has a conductor that sequences the medallion stages:
  `retail-orchestrate` (F005), the agent-conversational Layer-D verb. That conductor is
  INTERACTIVE -- a human is in the loop, the agent reads readiness state, runs the gate, and
  HARD-STOPS at the two human seams (mapping approval, Principle-V judgment calls). What the
  kit lacks is the UNATTENDED / CI sibling: a way to run the SAME approved sequence on a
  schedule or in a pipeline -- load bronze, profile, build silver/gold, run `retail check` /
  `retail validate`, run the semantic check, generate the handoff pack -- without a human
  re-typing each step, while still respecting every gate and every human seam the conductor
  respects. As surfaces multiplied (F024 named the five authority categories), the risk this
  ADR exists to close is concrete: an unattended runtime that conflates "my asset succeeded"
  with "the stage passed" silently becomes Core Authority -- the single thing every feature in
  the kit forbids. This ADR records the decision that fixes the orchestrator's authority.

## Decision

### 1. Dagster is an Execution Adapter / `DB-connected` -- exactly one category, one connectivity level

Per F024 (`docs/architecture/product-modules.md`) every tool declares EXACTLY ONE of the five
authority categories. Dagster declares **Execution Adapter** -- "a tool that crosses an
external trust/connectivity boundary to MATERIALIZE or PUBLISH an already-approved artifact ...
It is execution-only and gated; it never defines metrics, mappings, semantic logic, or
dashboard design." Its connectivity level is **`DB-connected`** -- the STRONGEST boundary it
itself crosses (it loads bronze, runs migrations, runs `retail validate` against a live
Postgres). It is NOT `publish-capable`: Dagster TRIGGERS the parked F016 Power BI Execution
Adapter and never opens a Power BI connection itself, so the publish boundary is F016's, not
Dagster's. The frozen F024 enumeration pins this exact declaration (F030 = Execution Adapter /
`DB-connected`); this ADR does not invent a category, it records the one the parent already
assigned.

### 2. Dagster sequences ALL seven readiness stages and DECIDES none

Dagster sequences Source -> Mapping -> Silver -> Gold -> Semantic Model -> Dashboard ->
Publish. The authority that a stage is `pass` is the gate exit code (mechanical stages) or a
named-human approval (judgment-call stages), recorded in Core Authority's
`readiness-status.yaml`. Dagster never writes that `pass`. A Dagster asset's success means
"the command ran and returned this exit" -- never "the stage is now `pass`." This is the
constitutional guardrail (Principle I -- the agent proposes, the gate disposes), applied to the
unattended runtime.

### 3. The derived-evidence vs authored-truth boundary (the line this feature lives or dies on)

The single biggest design risk is conflating "Dagster writes evidence back" with "Dagster
authors truth." They are different writes and this ADR keeps them apart:

- **DERIVED RUN-EVIDENCE (allowed).** When Dagster runs a step it records WHAT HAPPENED:
  "ran `retail check`, exit 0, 0 violations, `<timestamp>`"; "ran `retail validate`, exit 0,
  PK unique, 0 orphan FKs, penny-exact reconcile"; "generated handoff pack at `<path>`". This is
  a `templates/dagster-run-evidence.md` record -- a measured, timestamped, reproducible log of
  an execution. It is the SAME category as a `reconciliation-report.md` being FILLED by a live
  run: evidence ABOUT a step, not a ruling.
- **AUTHORED TRUTH (forbidden).** Flipping a readiness stage to `pass`, writing an approval,
  writing `Gate status: CLEARED`, defining what a metric means, choosing a grain or a PII
  disposition -- these are RULINGS. Dagster MUST NOT write any of them.
- **How the two reconcile (the one sentence the reviewer is looking for).** For mechanical
  stages (Silver Ready, Gold Ready) Dagster writes the CHECK evidence (the `retail check` /
  `retail validate` exit + numbers); whether that evidence MARKS the stage `pass` is Core
  Authority's record, written by Core Authority's process, not by Dagster's asset. For
  human-approval stages (Mapping Ready, Semantic Model publish-safety, Publish Ready) Dagster
  READS the committed approval (the `Gate status: CLEARED` field, the `approvals[]` owner+date
  in `readiness-status.yaml`) and HALTS if it is absent -- it never writes the approval and
  never writes a `pass` that depends on one.

This is exactly the posture `retail-orchestrate` already takes ("you may READ `Gate status`;
you may not write `CLEARED` yourself"). Dagster is the unattended runtime of that same contract.

### 4. The run-evidence record lives next to the run; it surfaces as evidence, never as a pass write

The per-run record is written under the planned project's run-output area
`orchestration/dagster/run-evidence/<run-id>.md` (a filled copy of
`templates/dagster-run-evidence.md`). Its measured per-asset results + blocking reasons are
ALSO surfaced as `evidence[]` / `blocking_reasons[]` entries on the affected table's
`readiness-status.yaml` -- the existing spine convention. Whether that evidence MARKS any stage
`pass` is Core Authority's record, never Dagster's write. Run evidence is append/record-only
and never overwrites a human-authored gate field.

### 5. Fail-closed propagates downstream; a halted run also fails the Dagster run status (the CI signal)

A failed gate asset fails closed and HALTS all downstream assets (a STOP edge); no downstream
asset is run around. Beyond writing the run-evidence record, a halted or fail-closed run MUST
itself terminate with a non-zero / failed Dagster run status so an unattended scheduler surfaces
the blocker rather than exiting silently. That failed run status is DERIVED evidence ABOUT the
execution -- it is NOT a readiness `pass`/fail write into Core Authority and flips no stage.

### 6. The terminal publish asset only TRIGGERS F016, gated on `publish_ready = pass`, and fails closed when F016 is absent

Even when `publish_ready` is `pass`, Dagster's terminal `publish_execution_evidence` asset only
TRIGGERS the F016 Power BI Execution Adapter (parked, execution-only, the only feature allowed
to publish a Power BI model); Dagster itself opens no Power BI connection and publishes nothing.
When `publish_ready` is `pass` but F016 is parked / not yet built at run time, the publish asset
FAILS CLOSED: it HALTS, records `blocking_reason` "F016 publish adapter not available" with the
named owner, terminates the run with a failed status, and NEVER publishes itself as a fallback.
The publish wall holds even when the only authorized publisher is absent (Principle II).

### 7. F005 reconciliation: same sequence, same authority, two runtimes

`retail-orchestrate` (F005) is the agent-conversational / interactive conductor -- a human is
present, the agent sequences the verb-skills in-context, self-heals against the gate, and stops
to ask. Dagster is the unattended / CI sibling: the SAME medallion sequence, the SAME gate-exit
authority, the SAME two human seams (mapping gate, Principle V), but driven by a scheduler /
pipeline instead of a conversation. Two runtimes, one sequence, one authority; neither
self-approves. Where the conductor says "I will pause and ask," Dagster says "I will halt this
asset and surface the open blocker." This ADR cites `specs/005-layer-d-orchestration/spec.md` as
the source of the sequence; it does not redefine it.

### 8. Auto-update posture: pin Dagster and dagster-dbt TOGETHER; the shared policy is deferred

The planned project is a SEPARATE, upgradeable external dependency (Principle II -- depend,
never fork): the kit depends on `dagster` + `dagster-dbt`, pinned TOGETHER (no independent
bumps); updates via PR only; a definitions-load smoke test as the minimum CI gate; a small
orchestration smoke once an implementation exists; and NO automerge for Dagster MAJOR versions.
The SHARED cross-adapter update/maturity policy is owned by F031 (spec 025,
adapter-maintenance-policy) and F033 (spec 027, release-maturity); this ADR states only
Dagster's adapter-specific needs and DEFERS the rest.

## Consequences

- The "my asset succeeded" vs "the stage passed" conflation is closed in the design: no asset in
  the planned graph has the capability to write a `readiness-status.yaml` stage `pass`, a
  `Gate status: CLEARED`, an `approvals[]` entry, a metric/mapping definition, or a Power BI
  publish. Run evidence carries statuses + measured numbers only.
- The static `retail check` gate is untouched -- this slice adds no rule, no CLI verb, no
  readiness stage. The orchestrator reuses the existing gate commands; it adds none.
- An unattended run becomes AUDITABLE: the run-evidence record (and the failed run status on a
  halt) is the artifact a human or the Control Room (F012) reads to see what the scheduler did.
- A numeric run-health / confidence score is explicitly NOT introduced (hard rule #9 / Principle
  IX); run evidence is the four-status vocabulary + measured numbers, deferred until scoring
  rules exist.
- F016 stays the deliberately-last, bottom-of-stack execution-only publisher; F030 is an
  OPTIONAL companion engine, never a precursor to or substitute for F016.

## Alternatives considered

- **Declare Dagster as Maintenance Automation (the "scheduled / no per-run human trigger"
  category).** Rejected: although Dagster runs unattended on a schedule, Maintenance Automation
  "declares NO connectivity level" and (per the F024 matrix) does not connect out -- "if it must
  connect out, the seam makes it an Adapter." Dagster crosses a live DB boundary (loads bronze,
  runs `retail validate`) and triggers the publish-capable F016, so the seam makes it an
  Execution Adapter. The unattended / CI flavor is real and is recorded in prose and in the
  adapter doc, but the CATEGORY is Execution Adapter, not Maintenance Automation -- a tool
  declares exactly one (Principle VI; the closed set).
- **Declare `publish-capable` connectivity (because the terminal asset reaches publish).**
  Rejected: Dagster TRIGGERS F016 and never publishes itself; the strongest boundary Dagster
  ITSELF crosses is the DB. `publish-capable` is F016's declaration, not Dagster's. The
  DB+publish tie-break does not apply because Dagster never publishes.
- **Let the orchestrator write the `pass` after a green gate (it has the exit code anyway).**
  Rejected: that is precisely the conflation this ADR forbids. The exit code is evidence; Core
  Authority's process records the stage status from the evidence. An orchestrator that wrote the
  `pass` would silently become Core Authority (Principle I, V).
- **Emit a numeric run-health score on each run.** Rejected: hard rule #9 (no fake confidence).
  Deferred until readiness scoring rules exist; run evidence stays statuses + measured numbers.
- **Build the Dagster project now (definitions / assets / jobs / sensors / schedules).**
  Rejected for this slice: docs-first (roadmap rule #8 / Principle VIII). The project shape is
  ENUMERATED in `docs/integrations/dagster-adapter.md`; the code is a later implementation slice.

## See also

- The adapter integration doc (allowed/forbidden ops, the human seams, the enumerated project
  shape + asset graph): `docs/integrations/dagster-adapter.md`.
- The derived run-evidence record shape: `templates/dagster-run-evidence.md`.
- The agent-side companion skill (when/how to invoke; the gate-read posture):
  `.claude/skills/dagster-orchestration-adapter/SKILL.md`.
- The category parent (the five authority categories + the matrix + the two sub-vocabularies):
  `docs/architecture/product-modules.md`; the decision record `docs/decisions/0008-core-authority-vs-product-modules.md`.
- The copy-me adapter declaration: `templates/adapter-contract.md`.
- The conductor sibling: `.claude/skills/retail-orchestrate/SKILL.md`;
  `specs/005-layer-d-orchestration/spec.md` (the sequence Dagster reuses).
- The transformation adapter it orchestrates via `dagster-dbt`: `specs/023-dbt-transformation-adapter/` (F029).
- The parked publish adapter it triggers: roadmap F016 (Power BI Execution Adapter).
- The maintenance / maturity siblings it references: `specs/025-adapter-maintenance-policy/`
  (F031), `specs/027-release-maturity-management/` (F033).
- The spec: `specs/024-dagster-orchestration-adapter/spec.md`. The constitution it instantiates:
  `.specify/memory/constitution.md` (Principles I, II, IV, V, VII, VIII, IX).
- The append-only ADR allotment for this tier: 0008 (F024), 0009 (F029), 0010 (F030, this),
  0011 (F031). Shipped ADRs 0001-0007 and 0012 are never reused.
