# Adversarial Plan-Review: 042-customer-domain-kpi-contracts-missing

**Reviewer posture**: single default-adverse skeptic, READ-ONLY (records fixes; edits nothing).
**Date**: 2026-06-29 | **Artifacts reviewed**: spec.md, plan.md, tasks.md, analysis.md
**Axes**: hidden-principle-violation, assumes-deferred-capability, c086-leak, fabricated-confidence, over-scope

## Verdict: PASS-WITH-NOTES

The draft is complete (specify + clarify + plan + tasks + analyze all ran) and internally
consistent. Two real NOTES below survive scrutiny -- both are honesty/consistency gaps the
self-analyze missed because it checked the three artifacts against EACH OTHER, never against the
live repo files they describe. Neither blocks; both must be visible to the ratifier.

## Findings

### PR1 -- Stale meta-reference will contradict the new file (axis: hidden-principle-violation, severity: medium)

`skills/retail-kpi-knowledge/knowledge/retail-kpi-domains.md` line 41 reads: "**planned** -- no
domain file in this seed, summarised here." Once `domains/customer.md` exists, that sentence is
FALSE, and the knowledge layer contradicts itself -- the exact routing/honesty invariant this idea
exists to uphold. The grounding listed this meta-reference as a touch point, but the task plan only
creates `customer.md` and edits `INDEX.md` (two edits); task T002 merely RE-READS the meta-reference,
it does not correct it. Verified: line 41 still carries the stale text and no task touches it.

FIX (for the ratifier / a later edit -- not applied here, stage 6 is read-only): add a task to
update `retail-kpi-domains.md` line ~41 so the Customer meta-reference points at
`domains/customer.md` instead of asserting "no domain file in this seed", OR explicitly
scope-justify deferring it. Recommended: fold it in -- it is one line and prevents a self-contradiction.

### PR2 -- New-vs-Returning KPI must cite the segment-rollup stop, not just identity (axis: hidden-principle-violation, severity: low-medium)

FR-002 / T005 name "New-vs-Returning Customer split" as a Planned KPI AND tie every KPI's blocker to
"the unmade customer-identity ruling." But new-vs-returning is a business SEGMENT, and the spec
simultaneously holds "business-segment rollups (new-vs-returning, tier, cohort)" as an OPEN
Principle-V stop (the analyst must supply the value->group table; the agent must not invent it).
Listing it Planned is fine (siblings list aspirational Planned KPIs); the risk is that tying its
blocker only to identity implicitly normalizes a segment the agent is forbidden to define.

FIX (record only): the New-vs-Returning row in `customer.md` MUST cite the segment-rollup
Principle-V stop as its blocker (not merely the identity ruling), so the file does not normalize an
un-ruled segment. This is a wording requirement on the eventual file; no artifact edit now.

## Axis sweep (clean axes)

- **assumes-deferred-capability**: CLEAN. No F016 Power BI Execution Adapter, no F031-F033 runtime,
  no DB/executor/network assumed. plan.md "Primary Dependencies: None" and tasks scope-guard both
  forbid it. The only tool invoked (T013 `retail check`) is the shipped static gate -- verified
  present at `src/retail/cli.py` with `rules/routes.py`.
- **c086-leak**: CLEAN by construction. FR-006 + T014 require a generic-retail token scan (no
  patient/insurance/payer/prescription/dispense/NDC). The Owner ruling (FR-004a) names generic
  functions only. Residual risk acknowledged in spec Edge Cases; mitigation is explicit.
- **fabricated-confidence**: CLEAN. No numeric readiness/health/confidence score anywhere. The
  analyze "100% / 17-17 coverage" is standard speckit traceability output over a finite requirement
  set, not a fabricated readiness score (hard rule #9). Front-matter "Readiness stage advanced:
  none" is the honest, conservative ruling -- it grants nothing.
- **over-scope**: CLEAN. Scope held to one file + two INDEX edits. No contract authored (FR-005,
  T016). The PII-section precedent question was ruled customer-only (not retrofitting 11 siblings),
  which RESISTS scope creep. The idea title's "KPI Contracts" over-promise is explicitly contained.
- **hidden-principle-violation**: two NOTES above (PR1, PR2); otherwise the four Principle-V calls
  are correctly OPEN and the never-self-grant / no-executor invariants hold.

## Bottom line

PASS-WITH-NOTES. The four Principle-V judgment calls remaining OPEN is the required state, not a
defect. The human ratifier should (a) decide PR1 (fold the meta-reference edit in, recommended, or
scope-defer it) and (b) ensure PR2's wording requirement reaches the eventual `customer.md`. Neither
note blocks ratification of this draft as a draft.
