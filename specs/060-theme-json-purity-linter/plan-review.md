# Adversarial Plan-Review: Theme JSON Purity Linter

**Feature**: 060-theme-json-purity-linter
**Date**: 2026-07-01
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports fixes,
does not edit spec/plan/tasks).
**Artifacts present**: spec.md, plan.md, tasks.md, analysis.md, research.md,
data-model.md, contracts/rule-contract.md, quickstart.md. (Nothing missing -- not
an automatic BLOCKED.)

## Axis 1 -- Hidden principle violation

Checked whether any principle is quietly violated behind agreeable prose.

- Ratified 044 (severity observed, not declared): research R6 has the rule emit
  `Severity.ERROR` findings. This is NOT a declared per-rule severity table -- every
  rule emits a severity on its findings; the governed posture is still OBSERVED per
  branch in severity-posture.json. No violation.
- Principle V (agent stops at judgment calls): the literal forbidden-key vocabulary
  and required-key scope are correctly RECORDED as an OPEN human ruling and gated
  out of the wiring phase, not auto-resolved. Honored.
- Principle I (fail closed): violation is ERROR -> non-zero exit. Honored.
- Principle VIII (static-first): stdlib-only over committed text. Honored.

Verdict: PASS. No hidden violation.

## Axis 2 -- Assumes a deferred capability

Searched for any reliance on F016 (Power BI Execution Adapter) or F031-F033
(spec-only runtimes) or any live/Desktop/network path. Found none -- the rule is a
static scan over committed JSON using the existing registry + core. The
token-to-theme FIDELITY rule (which WOULD need the token cross-walk) is explicitly
OUT OF SCOPE, not assumed built.

Verdict: PASS.

## Axis 3 -- C086 / tenant leak

The artifacts name `themes/tower-retail.theme.json` in the C6 "starter theme stays
green" check. This is the GENERIC committed starter theme, not a c086/pharmacy or
per-tenant palette; naming it for a live-corpus green-build assertion is legitimate
and does not hardcode any tenant key or brand value into the rule. The rule's
vocabulary is derived from the generic contract and FR-007 + T024 explicitly forbid
tenant/example literals. No pharmacy/c086 key appears anywhere.

Verdict: PASS. NOTE: implementers must keep the "tower-retail" reference confined to
the green-build TEST assertion; it must never migrate into the rule's vocabulary or
discovery list.

## Axis 4 -- Fabricated confidence

No readiness score, no percentage of doneness, no self-granted pass. Spec
front-matter stays "Status: Draft". The analyze verdict "clean" is substantiated by
an FR->test coverage table, not asserted. No fake confidence.

Verdict: PASS.

## Axis 5 -- Over-scope

The plan builds exactly the first-step seam: one rule module, fixtures, unit tests,
and the five-place wiring. It excludes (a) the token-to-theme fidelity rule and
(b) any required-key assertion the human has not defined. Golden-record regeneration
(T020/T021) is the necessary wiring, correctly gated behind the human ruling.

Verdict: PASS. No gold-plating.

## Notes / carried-forward gates (for the human + implement stage)

1. **Principle-V wiring gate (standing).** Phase 6 (T018-T021) FREEZES the golden
   records against the literal forbidden-key vocabulary. It MUST NOT be committed
   until a human records the literal vocabulary (and required-key scope) ruling in
   spec ## Clarifications. This planning workflow deliberately did NOT answer it.
2. **Live-registry reconciliation (LOW).** Backlog reviewers flagged a possible
   EXPECTED_RULE_IDS-vs-decorator-count drift on this branch. T001 owns reconciling
   the fresh id against the TRUE registered set before wiring; do not trust a count
   claim.
3. **Rule-id naming (costly-reversible).** The fresh, design/theme-namespaced id is
   frozen into five golden records once wired; settle it (against the live registry)
   before wiring, not after.

## Verdict

PASS-WITH-NOTES

The draft is internally consistent, principle-clean, correctly scoped, and free of
fabricated confidence or deferred-capability assumptions. It is ratifiable AS A
DRAFT. The one substantive open item is the Principle-V forbidden-key vocabulary
ruling, which is a human decision by design (recorded, not a defect) and gates only
the implement-time wiring freeze -- not this plan's completeness.
