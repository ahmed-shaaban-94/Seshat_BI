# 0008 -- Core Authority owns truth; the five-category authority taxonomy is orthogonal to the six layers

- **Date:** 2026-06-25
- **Status:** Accepted (F024; the normative reference + narrative are authored as
  `docs/architecture/product-modules.md` and `docs/architecture/core-vs-modules-and-adapters.md`;
  the two copy-me contracts as `templates/module-contract.md` and
  `templates/adapter-contract.md`. No runtime code, no `retail check` rule, no stage.)
- **Roadmap feature:** F024 (on-disk spec `018-companion-tools-architecture`). When the
  spec-dir number and the F-number disagree, the roadmap F-number wins.
- **Context:** The kit grew a dozen surfaces -- a conductor (`retail-orchestrate`), gate
  verbs (`retail-validate`, `retail-govern`, `retail-semantic-check`), read-only viewers
  (the control room, the grain reviewer), artifact-writing helpers (the BI handoff pack,
  dashboard design), and one deferred publish adapter (F016). The roadmap describes these
  through its **Six product layers** table, whose "What it is" column gestures at what each
  surface may do. But that table is a FUNCTIONAL cut (which part of the pipeline a surface
  touches); it never states, normatively, **what each surface may do to TRUTH** -- create
  it, approve it, or only read and summarize it. Features F025-F033 add nine more tools (a
  PR-readiness reviewer, a readiness viewer, an approval console, an evidence-pack
  generator, a dbt adapter, a Dagster adapter, a maintenance policy, a compatibility
  matrix, a release-maturity manager). Without a normative category contract, each new tool
  re-litigates the same question -- "can this thing approve a stage / define a metric /
  publish?" -- and the architectural rule binding all of them (only Core Authority owns
  truth) stays implicit and unenforceable. This ADR records the decision to make it
  explicit.

## Decision

### 1. The authority axis is ORTHOGONAL to the six layers; it does not replace them

The Six product layers answer "which part of the pipeline does this surface touch?" (a
functional axis) and remain authoritative for that. F024 adds a NEW, orthogonal authority
axis: "what may this surface do to truth?" Every tool therefore carries TWO coordinates --
its product LAYER and its authority CATEGORY. The control room is LAYER 4 AND CATEGORY
"Product Module / `read-only`"; F016 is LAYER 6 AND CATEGORY "Execution Adapter /
`publish-capable`". This is "formalize, do not reinvent": the layers are cited, never
renumbered or merged. Reading the change as "6 layers became 5 categories" is a misread.

### 2. Five closed categories, each with a one-paragraph normative definition

Every tool declares EXACTLY ONE of: **Core Authority**, **Official Workflow Skill**,
**Product Module**, **Execution Adapter**, **Maintenance Automation**. The set is closed
-- a sixth category requires its own spec, never a silent addition (Principle VI). The
full definitions live in `docs/architecture/product-modules.md`.

### 3. Only Core Authority creates truth or grants approval (the authority matrix)

The authority matrix (categories x {read, summarize, derive, execute, connect, publish,
create-truth, grant-approval}) gives `yes` on the create-truth and grant-approval rows to
**Core Authority alone** -- and grant-approval is always a named-human action. Every other
category reads, summarizes, visualizes, MAY write derived evidence, and MAY execute an
already-approved step, but MUST NOT create truth (define business meaning, approve a
metric/mapping) or move a stage to `pass`. This is not new authority; it makes the
existing "Core Authority owns truth" rule (Principles I, V; woven through F005-F016)
concrete and row-by-row checkable.

### 4. Two closed sub-vocabularies pin a Module's and an Adapter's declaration

A Product Module declares one capability level from `{ read-only, artifact-writing,
execution-capable }`. An Execution Adapter declares one connectivity level from
`{ local-only, DB-connected, external-service-connected, publish-capable }`. The other
three categories carry no parallel sub-axis -- their boundary is prose, and inventing one
would over-formalize.

### 5. The module-vs-adapter seam is the external trust/connectivity boundary

"Executes a step" alone does not make a tool an adapter; an `execution-capable` Module also
executes. The discriminator is whether the tool crosses an EXTERNAL trust/connectivity
boundary. DB-connected / external-service / publish -> Execution Adapter. Local committed
working set only -> `execution-capable` Module. The two categories are disjoint by
construction. This was the single biggest latent ambiguity; pinning it is what makes the
taxonomy normative rather than suggestive.

### 6. Maintenance Automation is its own category, distinguished by "no per-run human trigger"

A tool that runs on a schedule / in CI without a per-invocation human trigger is
Maintenance Automation, NOT a Module. It emits only derived evidence and never creates
truth or self-approves. The absence of a per-run trigger is the discriminator ONLY -- it
does NOT relax Principle V: such a tool operates exclusively on already-committed or
already-named-human-approved evidence, and the schedule itself (plus the evidence it runs
on) is a prior named-human action. This category is what lets F031 and F033 declare
themselves correctly instead of mis-declaring as Modules.

### 7. Docs-first; enforcement is enumerated and deferred

Consistent with hard rule #8 and Principle VIII, F024 ships as documentation + templates.
It adds no runtime code, no `retail check` rule (the static gate is unchanged), no CLI
verb, and no readiness stage. The conformance check that would assert "every tool declares
a category" is ENUMERATED as a future deliverable's job, not built here. A tool with no
declared category is a review finding today, not a runtime error.

## Consequences

- F025-F033 each open by declaring their category against `docs/architecture/product-modules.md`
  and filling `templates/module-contract.md` or `templates/adapter-contract.md` -- the
  same shared vocabulary, quoted, with no per-feature paraphrase or drift.
- The "can this tool approve / define / publish?" question is answered once, by the matrix,
  instead of re-litigated per feature.
- The static `retail check` gate is untouched (it stays at its existing rule count and
  exit 0); no governance hole is opened by adding an eagerly-imported rule.
- A maturity/score concept is explicitly parked to F033; this contract emits names only,
  never a number (hard rule #9).
- The six layers stay authoritative for the functional axis; nothing downstream may treat
  the categories as a renumbering of them.

## Alternatives considered

- **Extend the Six product layers to carry authority semantics.** Rejected: it would
  conflate a functional axis with an authority axis and force a renumbering. Orthogonal
  axes keep both clean.
- **Ship a conformance checker now (a `retail check` rule that asserts every tool declares
  a category).** Rejected for this slice: docs-first (rule #8), and a rule that
  eagerly imports config risks the same governance hole ADR-0007 documents. Enumerated as
  a future deliverable instead.
- **A numeric maturity score per tool.** Rejected: hard rule #9 (no fake confidence).
  Deferred to F033, which gates a maturity LADDER on evidence, not a score.

## See also

- The normative reference: `docs/architecture/product-modules.md`.
- The prose narrative + the seam worked through: `docs/architecture/core-vs-modules-and-adapters.md`.
- The copy-me declarations: `templates/module-contract.md`, `templates/adapter-contract.md`.
- The functional axis: `docs/roadmap/roadmap.md` (Six product layers).
- The authority rule it makes concrete: `.specify/memory/constitution.md` (Principles I, V).
- The spec: `specs/018-companion-tools-architecture/spec.md`.
- The append-only ADR allotment for this tier: 0008 (F024, this), 0009 (F029), 0010
  (F030), 0011 (F031). Shipped ADRs 0001-0007 and 0012 are never reused.
