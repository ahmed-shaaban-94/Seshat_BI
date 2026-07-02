# Adversarial Plan-Review: Approval Evidence Pack (063)

A single default-adverse skeptic over spec.md, plan.md, tasks.md (READ-ONLY: I report fixes,
I do not edit). Five axes: hidden-principle-violation, assumes-deferred-capability, c086-leak,
fabricated-confidence, over-scope.

## Axis 1 -- hidden-principle-violation

- The module emits an EMPTY approvals[] and is declared structurally incapable of writing it
  (FR-009/FR-010, plan Constitution Check). The two genuine Principle-V rulings (pending-
  contracts FR-008; business-rule/PII summarisation FR-013) are carried OPEN, not answered.
  PASS.
- SUBTLE RISK (medium): FR-013 lets the pack "summarise" a committed grain/rollup/segment/PII
  ruling. A careless implementer could paraphrase a PII or grain ruling in a way that reads as
  a fresh judgment -- re-publishing a human-owned decision. The spec correctly flags this OPEN
  and forbids re-stating (FR-013), but the SKILL.md must operationalize "link + quote-verbatim,
  never paraphrase" so the boundary is enforced, not just aspirational. Recorded as N1 (the
  human ruling governs; the build must default to verbatim-quote-or-link, never paraphrase).
- Source Ready: readiness-model.md says Source Ready needs a data-owner confirm of semantics/
  PII but is NOT one of the four highlighted approvals[] stages. data-model.md handles this
  (surface recorded state + any confirm) but the SKILL.md must not manufacture an approvals[]
  slot for source_ready. Recorded as N2 (low).

## Axis 2 -- assumes-deferred-capability

- FR-002 + research + plan explicitly forbid F016 and F031-F033 and any live DB/PBIP read.
  The AL1 signal (FR-006) is surfaced from committed metric-contract YAML, not by executing a
  live rule run -- consistent with "composes results other tools recorded". PASS. No deferred
  capability is assumed to exist.

## Axis 3 -- c086-leak

- FR-014 + SC-006 + T011 require generic-only template/labels with C086 cited, never inlined,
  resolving a generic mappings/<table>/ path. The grounding's stated c086 risk (section labels
  / grain keys leaking into a hardcoded section list) is directly mitigated by T011 and by the
  data-model section list being generic (header / gate req / states / blockers / assumptions /
  parked-on / pending / slot -- no domain nouns). PASS, provided T011 is actually executed as a
  guard (it is a task, not just prose). Recorded as N3 (low): the build should verify zero
  domain nouns in the shipped template, not just intend to.

## Axis 4 -- fabricated-confidence

- FR-012 forbids any numeric confidence/health/maturity score AND any completeness/"N of M"
  count; readiness is only the four statuses + evidence + blockers. data-model explicitly
  states no field is a score or count. This matches hard rule #9 and F028's own boundary.
  PASS. Strong.

## Axis 5 -- over-scope

- Scope is pinned to the GENERIC multi-gate generator; the dashboard-specific variant is
  explicitly deferred to idea C1 (spec Assumptions, plan Scope discipline). Deliverable is
  docs/skill/template only, no runtime code, no new rule (FR-019). This is minimal-seam,
  YAGNI-compliant. PASS.
- One watch item (low): the feature ships a template + skill but no filled instance and no
  test module. That is correct for a docs/skill Product Module (F028 precedent), but the
  implement stage's CI gate is only "retail check green + rule count unchanged" -- there is no
  automated test that the generated pack obeys the read-only / no-score invariants. That is
  inherent to an agent-is-runtime module and is acceptable, but reviewers signing the eventual
  pack should know the invariants are convention-enforced, not test-enforced. Recorded as N4.

## Draft completeness

- spec.md, plan.md, tasks.md, research.md, data-model.md, quickstart.md, analysis.md all
  present and committed. analyze verdict: clean (0 critical / 0 high). Not an auto-BLOCK.

## Findings summary

| ID | Axis | Severity | Finding | Fix |
|----|------|----------|---------|-----|
| N1 | hidden-principle-violation | medium | FR-013 "summarise" could paraphrase a PII/grain ruling into a fresh judgment. | SKILL.md must default to link + verbatim quote, never paraphrase, until the human rules the FR-013 boundary. |
| N2 | hidden-principle-violation | low | source_ready is not an approvals[] stage; a slot must not be manufactured for it. | SKILL.md: only the 4 highlighted stages get an empty approvals[] slot; source_ready surfaces recorded state only. |
| N3 | c086-leak | low | Generic-only guard (T011) is intent; must be verified on the shipped template. | Implement: assert zero domain nouns in templates/approval-evidence-pack.md. |
| N4 | over-scope (integrity) | low | Invariants are convention-enforced, not test-enforced (agent-is-runtime). | None required; note it in the module contract so signers know. |

No critical findings. No high findings. All four are addressable at implement time within the
existing spec (no spec rewrite needed).

## Verdict

PASS-WITH-NOTES

The spec/plan/tasks are internally consistent, principle-aligned, generic, score-free, and
scope-disciplined. Four non-blocking notes (one medium, three low) should be honored by the
implementer; none require re-specification. The two Principle-V questions remain correctly
OPEN for a human and MUST be ruled on before or during implement, not by the agent.

**Verdict**: PASS-WITH-NOTES
