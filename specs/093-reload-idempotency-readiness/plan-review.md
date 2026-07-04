# Adversarial Plan-Review: Reload / Idempotency Readiness -- Anti-Double-Count (HR7)

**Feature**: `093-reload-idempotency-readiness` | **Date**: 2026-07-04
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports findings,
edits nothing). Artifacts reviewed: spec.md, plan.md, tasks.md, analysis.md,
research.md, data-model.md, quickstart.md.

**Precondition check**: spec.md, plan.md, tasks.md, and analysis.md are all
present. `speckit-analyze` has already run for this feature and reports 0
CRITICAL / 0 HIGH, 17/17 FR coverage, 6/6 SC coverage, one MEDIUM (F1) and two
LOW (F3, F4) findings, all non-blocking. This review does not take that verdict
on faith -- ground truth below was independently re-verified against the live
worktree rather than trusting either plan.md's self-report or analysis.md's
citations.

**Ground truth verified directly against the worktree**:

- Live rule count is **55** (`docs/quality/rule-count-claims.yaml`
  `claimed-count: 55`; `grep -c '"id"' docs/rules/rules-manifest.json` = 55) --
  matches plan.md's "55 -> 56" claim.
- `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` is, read
  in full, genuinely textbook full drop-and-rebuild: `DROP TABLE IF EXISTS` for
  the fact then every dim (FK order), a clean `INSERT ... SELECT` per table, no
  `ON CONFLICT` anywhere, no bare append, no partition/date-range clear. `0003`
  and `0005` are silver (no `gold.*` target). This confirms SC-001's "100% of
  currently committed gold migrations pass HR7 with zero Findings" is checking a
  real, not hypothetical, baseline.
- `tokenize_sql`, `iter_sql_files`, `schema_zone` are defined in `src/retail/sql.py`
  (not `src/retail/rules/sql.py`, which hosts the S1-S8 rule bodies that import
  them); `is_test_path` is in `src/retail/core.py`. plan.md's Primary Dependencies
  line cites the correct module; research.md's precedent-survey heading is looser
  (flagged as analysis.md's own F2, LOW, non-blocking).
- `warehouse/load-policy.md` does **not** exist on disk -- matches the spec's
  Assumptions and research.md's "Landing analysis" claim that this feature
  creates no new file.
- No `HR1` or `HR7` string exists anywhere under `src/`, `docs/`, or `tests/`
  (outside `specs/*`) -- the id and the HR family letter are genuinely free in
  the committed tree today.
- **087/HR1's actual status differs from how the spec's "Boundary against
  neighbouring shipped work" section frames it.** `specs/087-conformed-dimension-readiness/`
  is untracked (`git status` shows it as `??`, part of the same batch of 18
  sibling spec directories as this feature) -- it has never been committed.
  Separately, the feature-number `087` was already consumed on `main` by an
  unrelated, already-merged feature (`087-decision-aid-layer`, commit `4d21861`,
  "decision-aid layer template fields" -- a DEFINE-only template-schema feature
  with **no retail-check rule at all**, confirmed by its own commit message:
  "no retail check rule, no DAX/SQL/PBIR"). So HR1 is not an established,
  shipped sibling the way spec.md's boundary section reads ("087
  conformed-dimension-readiness (rule id HR1)... HR1 is also a Gold-Ready,
  HR-series, static check") -- it is itself an unmerged, in-flight spec sharing
  this batch's numbering scheme, and the merged feature that actually holds
  number 087 is unrelated. This does not affect HR7's correctness (HR7 has zero
  functional dependency on HR1 -- verified: HR7 reads only `warehouse/migrations/*.sql`
  and optional `load-policy.md`; HR1 reads `source-map.yaml` and a separate
  `conformed-dimension-map.yaml`), and both plan.md (T008) and analysis.md (F3)
  already anticipate either landing order without incident. Recorded as a
  carry-forward N-note, not a blocking finding -- see Axis 5 and Notes below.

## Axis 1 -- hidden-principle-violation

Probe: does HR7 secretly self-grant an approval, decide a Principle-V judgment
call, or advise-instead-of-block?

- The core mechanism is fail-closed by construction on the case that matters:
  FR-005 requires an `ERROR` Finding (never a `WARNING`) on an undeclared
  deviation -- HR7 does not merely advise on the exact failure mode the feature
  exists to catch (contrast correctly drawn against S6/S7's WARNING
  "override-when" posture in research.md).
- **The load-bearing question an adversarial reviewer must not wave past**: does
  the MVP's "lands GREEN with zero Findings and creates no new file" (US1,
  T001/T002) constitute a disguised self-grant, the same shape of question the
  087/HR1 review had to trace through for its empty-scaffold green? Traced
  through here: no, and for a stronger reason than HR1's case. HR1's green was
  earned because the two committed stars happen to share zero dimension names
  today (a fact that could change). HR7's green is earned because the ONLY
  committed gold migration is independently, directly verified (this review's
  own read of `0004_create_gold_retail_store_sales_star.sql`, not just the
  spec's assertion) to be genuinely full drop-and-rebuild -- there is no
  deviation anywhere on the tree to declare, so there is nothing being silently
  waved through. FR-016 additionally guarantees HR7 records no model-level
  Gold-Ready "pass" of its own (Findings only) -- a clean HR7 run does not
  itself grant or contribute a self-authored readiness verdict beyond what
  every other mechanical S6/S7/S8 check already contributes today.
- FR-013 / Q-APPROVAL-SEAM (does the full-rebuild -> incremental transition
  itself need a named-human approval) is correctly left OPEN, not silently
  answered. The spec records a PENDING mechanical default an owner may later
  ratify, by direct precedent with Gold Ready's existing "Required owner /
  approval: None -- mechanical" posture (verified: `docs/readiness/gold-ready.md`
  line 52-55 states exactly this for the stage's existing S6/S7/RC2/RC16
  checks) -- HR7 is not inventing a new mechanical-by-default posture out of
  nothing, it is matching the stage's own documented precedent. tasks.md T044 is
  explicitly a "do not answer" checklist confirmation, not a resolution task.
- No grain/PII/business-rollup/product-identity call is answered anywhere.
  FR-011 explicitly forbids HR7 from re-deciding a table's grain/PK, and a
  dedicated source-inspection task (T041) verifies the rule module never
  references `source-map.yaml` or re-derives a grain/PK.

Verdict: **PASS**. No hidden self-grant; the zero-Findings landing state is
earned against a directly-verified real migration, not merely asserted, and the
one genuine judgment call (FR-013) is correctly raised and left open rather
than silently resolved.

## Axis 2 -- assumes-deferred-capability

Probe: does any artifact assume F016, a live DB, or a running adapter exists?

- HR7 is designed as 100% static: reads `warehouse/migrations/*.sql` (tracked
  files only, via `iter_sql_files(ctx)`) and, if present and tracked,
  `warehouse/load-policy.md`; no database connection, no Power BI/PBIP surface,
  no `db` extra or DSN dependency anywhere in FR-007/FR-010/plan.md's
  Constraints/Constitution-Check row VIII.
- F016 (Power BI execution adapter) is explicitly disposed as "N/A / not assumed
  to exist" in plan.md's Constitution Check, and no other artifact mentions it
  outside that negative disposition.
- Every mention of the live surface (RC2 grain/PK uniqueness, RC16 penny-exact
  reconciliation, `retail validate`) across spec.md (Boundary section, US3),
  plan.md (Summary, Constitution Check row VIII), research.md ("Gold Ready"
  precedent bullet), and quickstart.md ("Confirm HR7 stays static-only") is
  framed exclusively as "stays deferred / HR7 does not touch this / remains
  PENDING when no DSN is configured" -- never as an assumption that a live
  connection is reachable now or will become a silent prerequisite later. US3
  Acceptance Scenario 1 is a dedicated non-interaction guarantee: HR7 passing
  must never be used to mask RC2/RC16's own blocked-deferred state.
- `warehouse/load-policy.md`, the one new artifact this feature's shape touches,
  is explicitly NOT created here and its total absence is explicitly required
  to be a non-ERROR condition (Edge Cases, data-model.md) -- the correct
  Principle VIII posture (author static structure/shape, do not fake the
  capability into existing).

Verdict: **PASS**. No deferred capability is assumed reachable; every live-
surface reference is consistently framed as deferred, and the rule's own
scope guard (no DB connection, no reload execution) is verified both by
declaration (FR-007/FR-010) and by a dedicated source-inspection test (T035).

## Axis 3 -- c086-leak

Probe: does any template/label bake in domain-specific values instead of
staying generic (Principle VII)?

- The `ReloadStrategy` enum, `MigrationTableLoad`/`ReloadStrategyDeclaration`
  data shapes, and the `warehouse/load-policy.md` illustrative shape in
  data-model.md use only generic placeholders (`<migration-filename>.sql`,
  `gold.<table>`, `<key1>, <key2>`) -- confirmed by direct read of
  data-model.md's "Illustrative shape" block, which is explicitly labeled
  generic and states "no worked-example name used as a live requirement."
- FR-015 explicitly forbids baking a specific table/column name or the
  C086/retail_store_sales worked example into rule logic or doc updates; T042
  is a dedicated grep-verification task across the rule module and every
  Phase 1/2 doc edit for exactly this.
- The one place real names appear at all is research.md's own precedent-survey
  prose, which cites the actual committed migration filenames
  (`0004_create_gold_retail_store_sales_star.sql`) and table names
  (`gold.dim_product_rss`, `gold.fct_sales_rss`, verified present in the real
  file by this review's own read) to establish the landing-precondition claim.
  This is citation of the existing tree in a research/analysis artifact, not
  a domain-specific literal baked into the rule module or the `load-policy.md`
  template T004 will author -- consistent with how the 087/HR1 review treated
  an identical citation pattern as acceptable.
- Watch item for the implementer (carried forward as a note, not a spec
  defect): T004's `load-policy.md`-shape documentation and any illustrative
  fixture in T014/T016b/T021-T027 must keep using placeholder names
  (`<table>`, `<key1>`) and never literally copy `fct_sales_rss`'s or
  `dim_product_rss`'s real column names into a generic template comment --
  T042's grep is positioned to catch exactly this if it slips in during
  implementation.

Verdict: **PASS**. No c086/retail_store_sales specifics are baked into rule
logic or the `load-policy.md` shape; the real-name citations that do exist live
in research.md's precedent-survey prose, the correct place for them.

## Axis 4 -- fabricated-confidence

Probe: does any artifact emit a numeric score/health/maturity/completeness
count?

- HR7's Finding uses the existing `Finding` dataclass unchanged
  (`rule_id`/`severity`/`message`/`locator`, per data-model.md's "HR7 Finding"
  section) -- no new numeric field anywhere. The rule's only two outcomes are
  "no Finding" (pass-eligible) or a categorical `Severity.ERROR` Finding
  (FR-012).
- FR-012 explicitly forbids a numeric confidence/health/idempotency score and
  an "N of M" completeness tally; T036 is a dedicated mechanical test asserting
  no emitted Finding message contains a numeric percentage/ratio/"N of M"
  pattern -- a stronger verification posture than a docstring promise, and it
  runs against both the undeclared-deviation and the drop-and-rebuild fixtures
  (i.e. it checks both the failing and the passing path, not just one).
- Confirmed by direct read of quickstart.md and data-model.md's "Invariants"
  section: every framing of HR7's outcome is "Finding or no Finding," with an
  explicit "No score, ever" invariant line.
- The one integer anywhere in this feature -- the rule count (55 -> 56) -- is
  not a conformance/health score; it is the same `len(rules-manifest.json)`
  mechanism SC2 already reconciles for every rule addition, verified live at 55
  by this review, and plan.md/tasks.md both correctly instruct re-reading the
  live count at implement time rather than hardcoding a stale number (a
  discipline made concretely necessary here, not just theoretically, by
  analysis.md's F3: whichever of 093/HR7 or the still-unmerged
  087-conformed-dimension-readiness/HR1 lands first determines whether the
  count bump is also a NEW-family bump, and both plan.md T008 and tasks.md T010
  already hedge for either order).

Verdict: **PASS**. No fabricated or invented number anywhere; the rule count is
an authoritative `len()` read live, not a score, and the only test that
inspects Finding-message text explicitly asserts the absence of any numeric
framing on both the pass and fail paths.

## Axis 5 -- over-scope

Probe: does the plan do more than its one readiness-stage job, or cross into
another feature's territory?

- Deliverables are tightly bounded: one new rule module
  (`src/retail/rules/reload_idempotency.py`), the seven-surface wiring lockstep
  every new rule already requires, a new unit-test module, and one
  `docs/readiness/gold-ready.md` doc edit. `warehouse/load-policy.md`'s SHAPE is
  documented but the file itself is explicitly NOT created (T002, T004) --
  confirmed correct against the live tree (the file does not exist and nothing
  on the current committed migration set needs it).
- The plan explicitly REFUSES the one scope-expansion path that would have been
  easy to fold in: adding the dedup/overwrite key as a new `source-map.yaml`
  key, even though that file already carries related mapping metadata --
  because `source-map.yaml` is a SHARED surface with four other features
  already reading/extending it, and this feature's own collision-avoidance
  allocation forbids adding a fifth (FR-004, spec's Boundary section). This is
  the same discipline the 087/HR1 review credited HR1 for showing with its own
  refused `source-map.yaml` edit -- the pattern repeats correctly here rather
  than eroding on a second application.
- It does not touch HR1's territory (`conformed-dimension-map.yaml`,
  cross-star dimension shape agreement) at all -- verified: neither artifact
  set references the other's file, and the spec's Boundary section states the
  non-interaction explicitly and correctly (independently confirmed this
  review: HR1, wherever/whenever it lands, reads `source-map.yaml` +
  `conformed-dimension-map.yaml`; HR7 reads `warehouse/migrations/*.sql` +
  optional `load-policy.md` -- disjoint inputs, disjoint concerns).
- It does not touch Gold Ready's existing S6/S7 static checks or the RC2/RC16
  live checks' Finding text or outcome (FR-017); a dedicated additivity test
  (T043) runs the full rule registry before/after HR7's registration and
  asserts identical output for every non-HR7 rule id.
- It adds no new readiness stage and does not change Gold Ready's four-status
  model (`not_started | blocked | warning | pass`) -- confirmed against
  `docs/readiness/gold-ready.md`'s existing "Required checks" table, which HR7
  is designed to be added to as a third static row alongside S6/S7, not to
  replace or restructure.
- It does not re-decide any table's own grain/PK (FR-011; Mapping Ready's/HR1's
  territory) and does not open or extend the live `retail validate` composition
  at all (T039 is a dedicated structural confirmation of this non-interaction).

Verdict: **PASS**. Scope is disciplined and mirrors the 087/HR1 precedent's
correct refusal of a `source-map.yaml` shortcut; the one loose end this axis
surfaces is bookkeeping, not scope creep -- see Notes below.

## Notes / carry-forward (non-blocking)

- **The spec's "Boundary against neighbouring shipped work" section overstates
  HR1's current status.** It reads as though 087-conformed-dimension-readiness/
  HR1 is an established, shipped sibling ("087 conformed-dimension-readiness
  (rule id HR1): HR1 is also a Gold-Ready, HR-series, static check"). In fact,
  as of this review, `specs/087-conformed-dimension-readiness/` is itself
  untracked (part of the same unmerged 18-feature spec batch this feature
  belongs to), and the feature-number 087 that IS merged on `main`
  (`087-decision-aid-layer`) is a wholly different, unrelated DEFINE-only
  feature with no retail-check rule at all. research.md is honest about this
  elsewhere ("NOT YET MERGED... confirmed by an empty
  `src/retail/rules/**/HR1*` glob") -- the inconsistency is only in spec.md's
  own boundary-section prose reading more confidently than the facts support.
  This does not change any verdict: HR7 has zero functional dependency on HR1
  (disjoint input files, disjoint concerns, independently confirmed above), and
  both plan.md (T008) and analysis.md (F3) already correctly handle either
  landing order. Recommend a small wording softening in spec.md's Boundary
  section on a future revision ("087/HR1, if and when it lands, is..." rather
  than presenting it as already-shipped) so a future reader does not need to
  re-derive this from research.md's more careful phrasing.
- **FR-008's "syntactically plausible column identifier" sub-clause is
  untested** (analysis.md's own F1, MEDIUM, carried forward here as still
  live). FR-008 requires HR7 to check both that a key is *named* (presence)
  and that it is *syntactically plausible* (shape). Every task mapped to
  FR-008 (T030/T032/T035) verifies presence and the never-live-verify half;
  none defines what "syntactically plausible" mechanically means or tests the
  negative path (an empty `reload-strategy:` marker with no keys, or a
  malformed/garbage key list). Recommend resolving this before Phase 4 (US2)
  implementation closes, not merely before ship -- an author could otherwise
  satisfy HR7 with a marker carrying no real key and the rule's behavior in
  that case is currently unspecified by any task.
- **The rule-count and HR-family-prefix bump is a live, order-dependent
  serialization point**, sharpened (not newly created) by this review's
  confirmation that 087/HR1 is still unmerged: whichever of HR7 or HR1 lands
  first in `docs/glossary.md` must add the "HR" prefix to the family list, not
  just bump the integer count -- T010's current wording only names "the
  rule-count anchor text," which reads as the integer alone (analysis.md's F3).
  No automated lockstep test currently catches a stale family-prefix list
  (`test_glossary_rule_table.py` checks id-bijection only). Not a blocker; a
  reminder for whoever executes T010 to read the live family-prefix list at
  that time rather than copy today's "21 families... S, D, C... SF" string
  verbatim.
- **FR-013 (Q-APPROVAL-SEAM) stays genuinely open.** No task in tasks.md
  answers it; T044 is explicitly a "do not answer" checklist confirmation. This
  is correct and should remain so through implementation -- any future edit
  that adds an `approvals[]` shape for the reload-strategy tier without an
  owner ruling would flip Axis 1 to a violation.
- **Keep illustrative fixtures illustrative.** The only realistic c086-leak
  vector this feature could introduce during implementation is a test fixture
  or `load-policy.md`-shape example that copies `fct_sales_rss`'s or
  `dim_product_rss`'s real column names instead of a placeholder. T042's grep
  is positioned to catch this; keep it as a hard gate through implementation,
  not a courtesy check.

## Verdict

**Verdict**: PASS-WITH-NOTES

All five axes clear on direct ground-truth verification against the live
worktree, not merely on the plan's self-report: the migration this feature's
MVP zero-Findings claim depends on was read in full and confirmed genuinely
full drop-and-rebuild; the rule/family id-freedom claim was independently
re-checked and found to need one nuance the spec's own boundary section
understates (HR1 is unmerged, and the merged feature holding number 087 is
unrelated) without changing any functional dependency or verdict; the
collision-avoidance refusal of a `source-map.yaml` shortcut is real and
mirrors the 087/HR1 precedent's own discipline; and no numeric score or
fabricated confidence value appears anywhere, checked on both the passing and
failing Finding paths. The carry-forward notes are non-blocking: a wording
softening for the HR1 boundary-section framing, FR-008's untested plausibility
sub-clause (the one substantive gap, already flagged MEDIUM by analysis.md and
not newly discovered here), the rule-count/family-prefix serialization
reminder, the standing FR-013 open-question guard, and the illustrative-
fixture watch item. No CRITICAL or HIGH finding; no axis is RISK or FAIL.
