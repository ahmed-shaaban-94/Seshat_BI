# Clarifications -- 088-drill-nav-periods

### Session 2026-07-04

Recommended answers recorded. **[OWNER SEAM]** items are Principle-V / structural
judgment calls carried to the ratify ledger -- the agent recommends, never
self-clears.

---

### C1 -- #5 scope: growth-contract STRUCTURE only, or seal the definition? **[OWNER SEAM, BLOCKING]**

**Ambiguity**: the gap report's shippable-form said "seal the growth contracts,
*resolving the baseline ambiguity and partial-period normalization*." But the
baseline (same-period-last-year vs prior-period) is UN-CODED (A3 is the date-axis ambiguity, not this), and
"comparable store" is **A11** -- both on the metric-contract stop-and-ask list.
Sealing the DEFINITION means the agent writes what "same-store" and "the baseline
period" mean -- a named human judgment call.

**Options**:
- **A (RECOMMENDED) -- structure only; comparison-baseline (uncoded) + A11 owner-ruled.** Author the growth
  contracts' SHAPE (business question, Non-additive additivity, base-over-base
  derivation, required fields, validation) and FLAG the comparison-baseline (uncoded) (+A11 for same-store) as
  OPEN owner decisions with a recommended option. The agent writes NO baseline /
  comparable-store definition. `Status` = honest open (Planned / structure-only).
- **B -- seal the definition now.** The agent picks the baseline + comparable-store
  rule. REJECTED as framed: it resolves the comparison-baseline (uncoded) + A11, violating Principle V / the
  stop-and-ask list -- the exact cardinal sin the session's rules guard against.

**Recommended answer: A (structure only).** Mirrors 087's FR-011 (backfilling
business values = owner work) and the metric-contract ambiguity-ledger model. The
owner rules them later; the contract structurally cannot go `Seeded` until they
do. Owner confirms A.

---

### C2 -- report-composition: absent-by-GAP or absent-by-DESIGN? **[OWNER SEAM]**

**Ambiguity**: the repo is emphatically one-page-per-blueprint ("one file = one
page"). A report-level, multi-page nav artifact adds a PARENT above the page that
does not exist today. Is that absent because it is a genuine gap, or a deliberate
omission (like F016 execution) that a new hierarchy layer would collide with?

**Options**:
- **A (RECOMMENDED) -- add `report-composition.yaml` as a NEW intent layer.** The
  footer_status "link to the DQ control room" and cross-page nav are REFERENCED by
  the page vocabulary but specifiable nowhere -- that is absent-by-gap, not by
  design. A composition artifact that REFERENCES pages (never inlines them)
  respects one-file-one-page while giving the report a parent.
- **B -- defer report-composition; ship only #4's drill fields.** If the owner
  considers multi-page composition a deliberate F016-adjacent omission, US2 is
  dropped from this spec and #4 ships as visual-spec drill fields only.

**Recommended answer: A**, because the page vocabulary already REFERENCES
inter-page links it cannot specify (a real dangling gap, like #5's placeholder).
The new artifact only references pages, so it does not violate one-file-one-page.
Owner confirms A vs B (defer).

---

### C3 -- #4 drill/nav: is the intent/execution line drawn correctly?

**Ambiguity**: drill-through/drill-down are partly RUNTIME behaviors (F016). Which
part is as-code intent vs deferred execution?

**Recommended answer**: capture only INTENT -- which visual OFFERS a drill-through,
to which target page, carrying which named filter; the drill-down hierarchy AXIS
(dimension levels). The RENDERED behavior (the click, the runtime filter transfer,
focus/keyboard) is F016. This line is stated in FR-003 + the template comments,
mirroring 087's no-score line. Not an owner seam; the adversarial reviewer confirms
no field crosses into execution.

---

### C4 -- combined ratification across two feature areas with two risk stories

**Ambiguity**: #4 is F011A (interaction, execution-boundary risk); #5 is F009
(business definition, Principle-V risk). Less thematically unified than 087's trio.

**Recommended answer**: proceed combined (owner's chosen pairing), and the ratify
ledger EXPLICITLY separates the two risk stories so the owner knowingly signs both.
No feature-boundary guard crossed (verified as for 087). Confirmed at ratify.

---

## Carried to the ratify ledger (owner confirms)

- **C1 [BLOCKING]** -- #5 structure-only (A), comparison-baseline (uncoded) + A11 owner-ruled. The agent writes
  no baseline/comparable-store definition.
- **C2** -- report-composition as a new intent layer (A) vs defer (B).
- **C4** -- combined ratification spans F011A (#4) + F009 (#5), two risk stories.
