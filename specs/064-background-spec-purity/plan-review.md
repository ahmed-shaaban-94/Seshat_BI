# Adversarial Plan-Review: Background-Spec Forbidden-Dynamic-Content Assertion Rule

**Feature**: 064-background-spec-purity
**Date**: 2026-07-02
**Reviewer stance**: single default-adverse skeptic, READ-ONLY over spec.md,
plan.md, tasks.md (+ research/data-model/contracts/quickstart). Reports fixes;
edits nothing. Five axes: hidden-principle-violation, assumes-deferred-capability,
c086-leak, fabricated-confidence, over-scope.

## Precondition check (auto-BLOCKED if missing)

- spec.md: present. plan.md: present. tasks.md: present (T001-T023).
- analysis.md: present, verdict clean (0 critical / 0 high).
- All stages ran. Precondition satisfied -- not auto-BLOCKED.

## Axis 1 -- Hidden principle violation

- **Principle V (stops at judgment calls)**: The rule asserts a categorical
  boolean + reason-PRESENCE check; it computes no score, self-grants no readiness,
  advances no stage (FR-015, Clarifications Q5). The one genuine judgment call --
  the filled-spec file-discovery CONVENTION -- is correctly RECORDED OPEN for the
  owner and NOT answered by the advisor, with the recommended default clearly
  labeled "recommended, pending the human ruling". The advisor DID resolve Q1-Q4
  (placeholder handling, vocabulary freeze, parse contract, severity); these are
  vocabulary/posture calls of the same class DL1 resolved under the delegated
  override, not grain/PII/rollup/identity carve-outs. CLEAN, with one NOTE below.
- **Principle I (fail closed)**: violation -> ERROR -> non-zero. Consistent.
- **Ratified 044 (severity observed)**: severity observed, not a governed table.
  Consistent.
- No hidden violation found.

NOTE (not a finding): the qa "recorded reason" detection (FR-005/Q3) is a thin
line -- the rule detects reason PRESENCE, never adequacy. The spec states this
explicitly and repeatedly, so it is not a hidden Principle-V overreach; an
implementer who starts grading reason quality would violate it, so the contract
doc must keep the "presence only" invariant loud. Flagged as R1 (LOW) for build
vigilance, not a plan defect.

## Axis 2 -- Assumes deferred capability

- No artifact assumes F016 (Power BI Execution Adapter) or F031-F033. The rule is
  stdlib-only over committed text; YAML is a lazy in-function import (existing
  sanctioned pattern), not a new runtime. Image verification is explicitly named
  OUT OF SCOPE (Assumptions + research Decision 4), not assumed. CLEAN.

## Axis 3 -- C086 / tenant leak

- Discovery is a generic suffix convention; vocabulary is frozen verbatim from
  the generic template `templates/background-spec.yaml`, not from any tenant
  example. No c086/pharmacy/brand path or key appears in any artifact. The
  recommended default suffix `*.background.yaml` is generic (no tenant token).
  is_test_path exemption reused. CLEAN. C13 + T023 guard this at build time.

## Axis 4 -- Fabricated confidence

- No numeric confidence/readiness score anywhere (rule 9 respected). No hardcoded
  rule count -- every reference to the registry says "reconcile against the TRUE
  live set at wiring time" (T001, research live-registry note). The local-41 vs
  main-40 drift is surfaced honestly as F2 (LOW) with an owning task, not papered
  over. Status stays Draft; no self-granted Ratified. CLEAN.

## Axis 5 -- Over-scope (YAGNI)

- Scope is one rule + fixtures + five-place wiring. No image binary verifier, no
  required-key invention beyond the template's declared blocks, no unbuilt
  fidelity rule, no discovery convention frozen ahead of the owner. The rule is
  inert on an empty corpus (FR-011) -- it adds the seam, not speculative behavior.
  CLEAN.

## Findings (fixes, not edits)

| ID | Axis | Severity | Finding | Recommended fix |
|----|------|----------|---------|-----------------|
| R1 | hidden-principle-violation | LOW | qa "reason" check is presence-only; an implementer could drift into grading reason adequacy (Principle V). | Keep the "presence only, never adequacy" invariant explicit in contracts/rule-contract.md and the rule's docstring at build time. Already stated in spec FR-005 + Clarifications Q3; no plan change. |
| R2 | fabricated-confidence | LOW | Local EXPECTED_RULE_IDS shows 41 (incl DL1) vs memory's 40 on main; a hardcoded assumption could go stale. | Already mitigated: T001 reconciles against the live registry; no literal id/count is frozen in the plan. No change. |
| R3 | over-scope | LOW | data-model leaves the exact YAML shape of a qa "reason" (sibling key vs mapping) unfrozen. | Acceptable build-time detail; resolve in contracts/rule-contract.md during implement. Not a plan defect. |

**Critical**: 0. **High**: 0. All three findings are LOW and each is already
owned by an existing task or an existing explicit spec invariant.

## Verdict

Verdict: PASS-WITH-NOTES

The plan is coherent, generic, static-first, fails closed, and stops correctly at
the one genuine Principle-V judgment (the discovery convention) by recording it
OPEN for the owner and keeping the rule inert until ruled. The three LOW notes are
build-time vigilance items, not planning gaps. No BLOCKED finding. The spec
front-matter correctly remains Status: Draft -- ratification is a human edit this
workflow does not make.
