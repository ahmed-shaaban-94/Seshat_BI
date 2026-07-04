# Analysis: 088-drill-nav-periods -- cross-artifact consistency

## Coverage (every FR -> a task)

FR-001->T101 · FR-002->T102 · FR-003->T103 · FR-004->T301 · FR-005->T201/202/203 ·
FR-006->T201/202/203/T402 · FR-007->T201/202/203/T403 · FR-007b->T202 (+T201/203) ·
FR-008->T204 · FR-009->T404 · FR-010->T405/T502 · FR-011->T501. SC-001->T101/T403 ·
SC-002->T301 · SC-003->T402/T403 · SC-004->T204 · SC-005->T402/T405. No orphan.

## Adversarial review result (2026-07-04, code-reviewer skeptic): NEEDS-FIX -> RESOLVED

- **[CRITICAL -> FIXED] A3 miscitation.** The spec built FR-007 (its flagship
  Principle-V safeguard) on "A3 = baseline ambiguity" -- but canonically A3 = "Sale
  date vs posting date vs return date"; the comparison-baseline (SPLY vs prior
  period) is UN-CODED in `kpi-ambiguities.md` (a separate un-coded bullet in
  `domains/time-intelligence.md`). Stamping `(A3)` would have been a false
  cross-reference into the canonical ledger -- exactly where the spec claimed most
  rigor. FIXED: all baseline references now cite the comparison-baseline as PROSE
  ("uncoded; see time-intelligence.md"), never `(A3)`; A11 (same-store) retained
  correctly. Chose prose over registering a new A12 to avoid rippling the
  `metric-contract.yaml` closed-range citation ("A1..A11 -- not A1..A10", 3 places)
  -- lower blast radius, and AL2 does not parse the A-code set as closed.
- **[LOW -> FIXED] structure-only authorship hazard.** Following the existing
  contract format could force the agent to fill Business-definition/Formula with a
  de-facto same-store/baseline definition. FIXED: FR-007b requires those sections
  left owner-pending ("vs the owner-ruled comparison baseline"), never an
  agent-authored definition.

Verified TRUE (non-issues, per the reviewer):
- **AD1 passes trivially**: AD1 only ERRORs on a literal `sum of <Cap>`/`SUM(<Cap>)`
  of a non-additive parent in the `**Derives from**` first paragraph, un-suppressed
  by a `<Cap>/<Cap>` ratio. The base-over-base derivation (`(NS[p]-NS[base])/NS[base]`)
  has no `sum` token -> zero findings by construction. Requirement for the author:
  `**Additivity**` opens with the single word `Non-additive`; `**Derives from**`
  first paragraph contains no `sum of X` string.
- **Ground truth confirmed**: drill fields absent, no report-composition, unbound
  `<period-comparison-contract>`, exactly 10 existing contracts (no growth ones).
- **No other rule breaks on +3 contracts**: AL1/AL2 key on `mappings/*/metrics/`
  (disjoint path); C3/scorecard checks cited-path resolution only; no
  contract-count/coverage anchor exists.
- **#4 intent/execution line clean**: no drill/nav field specifies runtime.
- **report-composition self-aware** (reference-only, gated on C2).

Note (owner awareness, not a 088 defect): the reviewer found AD1 is effectively a
no-op on natural-language contracts (its regexes match single-token identifiers +
an em-dash title format the real contracts don't use). Pre-existing AD1 weakness;
088 doesn't create it. Flag for a possible future AD1 hardening -- out of scope here.

## Boundary compliance

DEFINE-only (no rule/DAX/SQL/PBIR) · #4 intent-not-execution · #5 Principle-V
(baseline + A11 owner-ruled, agent writes no definition; prose citation, no false
A-code) · AD1-legal growth contracts · no numeric score · reference-by-name ·
generic placeholders. ALL PASS.

## Verdict

**CONSISTENT after the CRITICAL + LOW fixes.** 0 remaining critical/high. Owner
seams (C1 structure-only, C2 report-composition, C4 combined) carried to the ratify
ledger.
