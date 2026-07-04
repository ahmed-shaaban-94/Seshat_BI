# Adversarial Plan-Review: Consumer-Facing Generated Data Dictionary (101)

A single default-adverse skeptic over spec.md, plan.md, tasks.md (READ-ONLY: I report fixes,
I do not edit). Five axes: hidden-principle-violation, assumes-deferred-capability, c086-leak,
fabricated-confidence, over-scope.

## Axis 1 -- hidden-principle-violation

- The central Principle-V question -- may the module GENERATE a simplified paraphrase of a
  column's existing TECHNICAL source-map `reason`, or must it always verbatim-cite-or-gap
  (FR-008/Clarification Q1) -- stays genuinely OPEN across all three artifacts: spec.md carries
  it as an explicit OPEN owner ruling, plan.md's Constitution Check states it "does **not**
  resolve it and does not adopt a paraphrase-generation capability," and tasks.md's own
  "Principle-V carve-out" section states "NO task in this list resolves it." The fail-safe
  default (verbatim-cite-or-gap) ships regardless of the eventual ruling. This is the axis this
  feature is built around, and it holds. PASS.
- No self-granted approval anywhere: the module emits no `approvals[]` entry and no
  `blocking_reasons[]` entry (FR-012), and is declared structurally incapable of moving a
  readiness stage. PASS.
- SUBTLE RISK (medium): FR-005 requires citing a source-map `reason` "quoted or linked as
  recorded," and the verified source-map text (`mappings/retail_store_sales/source-map.yaml`
  line 45) shows some `reason` strings already embed a prior resolved human ruling inline (e.g.
  "...KEPT (Q1 resolved 2026-06-25, deviation from the RC4 auto-drop)."). FR-008/Q1 correctly
  keeps NEW paraphrase-generation OPEN, but the spec does not explicitly say what happens if an
  implementer is tempted to trim or summarize a long multi-clause `reason` for readability --
  trimming a ruling out of a verbatim quote would be a quiet re-editing of a human's recorded
  decision, not a new judgment, but the boundary between "quote verbatim" and "quote a
  convenient excerpt" is not spelled out. Recorded as N1 (the human ruling governs; the build
  must default to whole-field verbatim quote or a full link, never a trimmed excerpt).
- data-model.md Entity 3's `approved` field is a derived display boolean ("`true` when
  `readiness_status == "pass"`, else `false`"), explicitly documented as "never itself a
  numeric score" and never the module's own witnessed approval. Correctly scoped: it reflects
  the metric contract's OWN recorded status, not a decision this module makes. PASS, worth
  stating affirmatively since a careless read of "approved: true/false" could look like the
  module is granting something. Recorded as N4 (low) -- the build must keep this field a pure
  read-through of `readiness.status`, never settable by any other logic path.

## Axis 2 -- assumes-deferred-capability

- FR-002 + research.md section 3 explicitly forbid F016, any live DB connection, any live
  Power BI/PBIP read, and any F031-F033 spec-only runtime; the module reads only committed SQL
  and YAML text. PASS.
- The one live-adjacent surface (reconciling the dictionary's column list against the
  ACTUALLY-DEPLOYED database schema) is explicitly named and marked PENDING/out-of-scope in the
  spec's Assumptions and plan's Principle VIII check, never silently assumed reconciled just
  because the two static files (gold SQL, source-map.yaml) happen to agree. The STATIC
  disagreement between those two committed files (FR-019) is correctly kept in-scope since it
  needs no live surface. PASS -- this is a more careful treatment of the static/live boundary
  than a feature that simply declares "no live reads" without naming the adjacent deferred
  case.

## Axis 3 -- c086-leak

- FR-015 + SC-006 + T018/T019 require generic-only path resolution and section labels, with
  `retail_store_sales` appearing only as a cited, filled illustrative instance (confirmed
  real on disk: `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`,
  `mappings/retail_store_sales/source-map.yaml`, `mappings/retail_store_sales/metrics/*.yaml`,
  all five metric files present). data-model.md's field vocabulary (`table_id`, `column_name`,
  `gold_table`, `metric_name`, `reason_code` enum) carries no domain noun. PASS, provided T019
  is actually executed as a guard at implement time (it is a task -- an audit pass over the
  finished artifacts -- not a standing runtime check). Recorded as N2 (low): the build should
  verify zero domain nouns in the shipped `templates/consumer-data-dictionary.md` and
  `SKILL.md`, not just intend to, matching the 063 precedent's own N3.

## Axis 4 -- fabricated-confidence

- FR-013 explicitly forbids any numeric confidence/health/maturity score AND any completeness
  count or "N of M" tally; data-model.md's "What this data model deliberately does NOT
  include" section states no `confidence`, `health`, `maturity`, or `completeness_pct` field
  exists anywhere in the shape. Gap Marker (Entity 4) is a named, enum-coded record, never a
  percentage. This matches hard rule #9 exactly. PASS. Strong -- the data model's explicit
  negative-space section makes this harder to violate by accident than a spec that merely
  states the rule in prose.

## Axis 5 -- over-scope

- Scope is pinned to composing a MEANING reference (what a column/measure means) from exactly
  three read-only artifact families -- gold migration SQL, `source-map.yaml`, and metric
  contracts. Note: the feature's own framing (spec Overview, task grounding) names two input
  families ("gold columns + metric contracts"), and the spec/plan/research add a THIRD --
  `source-map.yaml`'s `reason` field -- as the source of a gold column's committed meaning
  (FR-005). This is disclosed and justified in the Overview's own opening paragraph (a gold
  column's meaning "lives as a mapping-decision `reason` string inside
  `mappings/<table>/source-map.yaml`") rather than smuggled in silently, and it does not expand
  the module's write surface or add a new gate -- it is a necessary read source, not scope
  creep. PASS.
- The Boundary section (spec) and research.md section 1.2 draw three explicit, checked lines
  against neighbours: F013's handoff-pack item (e) (a REQUIRED Publish Ready gate section,
  pre-publish, data-owner audience) stays untouched and un-duplicated (confirmed on disk,
  `templates/handoff/bi-handoff-pack.md` lines 51/77, distinct filename per FR-018); F028's
  evidence-pack generator (a readiness bundle, different subject and filename) stays distinct;
  the `power-bi-docs` skill family (live-connected) stays distinct via the Principle VIII
  static-only constraint. Deliverable is docs/skill/template only -- no runtime executor, no
  `retail check` rule, no rule-id (FR-017), matching the Collision-Avoidance Allocation. PASS.
- One watch item (low): like its 063 precedent, this ships a template + skill but no filled
  instance and no test module -- correct for a docs/skill Product Module, but the invariants
  (no-invention, single-write, no-score) are convention-enforced by the agent following
  SKILL.md's numbered steps, not test-enforced by any `pytest` module. Recorded as N3.

## Draft completeness

- spec.md, plan.md, tasks.md, research.md, data-model.md, quickstart.md are present and
  internally consistent (cross-checked: research.md's three artifact families match
  data-model.md's Entity 2/3 field shapes match tasks.md's compose-step tasks match
  quickstart.md's walkthrough steps). **analysis.md is NOT present in this feature's spec
  directory** (only the six files above exist on disk). This external plan-review is itself
  serving as the cross-artifact consistency pass in analysis.md's place for this stage; its
  absence is noted here rather than silently treated as reviewed, but does not itself block --
  no contradiction between spec/plan/tasks was found during this review that an `analyze` pass
  would have needed to catch independently. Recorded as N5 (informational, non-blocking).

## Findings summary

| ID | Axis | Severity | Finding | Fix |
|----|------|----------|---------|-----|
| N1 | hidden-principle-violation | medium | FR-005's "quoted or linked as recorded" does not say whether a long multi-clause `reason` (which may embed a prior resolved human ruling, e.g. a Q1 PII deviation) may be excerpted/trimmed for readability. | SKILL.md must default to whole-field verbatim quote or a full link to the source-map location, never a trimmed excerpt, until a human rules otherwise. |
| N2 | c086-leak | low | Generic-only guard (T018/T019) is intent; must be verified on the shipped template and SKILL.md. | Implement: assert zero domain nouns (no `retail_store_sales`, no `transaction_id`, no `TotalSales`) in fixed labels of `templates/consumer-data-dictionary.md` and `SKILL.md`. |
| N3 | over-scope (integrity) | low | Invariants (no-invention, single-write, no-score) are convention-enforced, not test-enforced (agent-is-runtime). | None required; state this plainly in the module contract so signers know. |
| N4 | hidden-principle-violation | low | Entity 3's `approved` boolean must stay a pure read-through of the contract's own `readiness.status`, never a value this module sets independently. | SKILL.md: derive `approved` only from `readiness_status == "pass"`; no other code path may set it. |
| N5 | draft-completeness | informational | analysis.md is absent from this feature's spec directory. | Non-blocking; this plan-review serves as the cross-artifact consistency check for this stage. Author analysis.md at the usual pipeline point if the chain requires it downstream. |

No critical findings. No high findings. All five are addressable at implement time within the
existing spec (no spec rewrite needed).

## Verdict

PASS-WITH-NOTES

The spec/plan/tasks are internally consistent, principle-aligned, generic, score-free, and
scope-disciplined -- if anything more careful than the 063 precedent on the static/live
boundary (the static-disagreement-in-scope vs. live-reconciliation-deferred split is drawn
explicitly) and on negative-space documentation (data-model.md's own "does NOT include"
section). Five non-blocking notes (one medium, three low, one informational) should be
honored by the implementer; none require re-specification. The single Principle-V question
(FR-008/Q1) remains correctly OPEN for a named human and MUST be ruled on before or during
implement, not by the agent.

**Verdict**: PASS-WITH-NOTES
