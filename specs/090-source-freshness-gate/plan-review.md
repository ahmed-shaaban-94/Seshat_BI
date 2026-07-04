# Adversarial Plan-Review: Source Freshness / Staleness Declaration and Static Presence Check (HR4)

**Feature**: `090-source-freshness-gate` | **Date**: 2026-07-04
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports findings,
edits nothing). Artifacts reviewed: spec.md, plan.md, tasks.md, research.md,
data-model.md, quickstart.md.

**Precondition check**: spec.md, plan.md, tasks.md are present. **`analysis.md`
does NOT exist in this feature directory** -- `speckit-analyze` has not been run
for 090, so there is no cross-artifact analyze verdict to cite. This review does
not fabricate that precondition; it proceeds on spec + plan + tasks + research.md
+ data-model.md + quickstart.md, and performs its own ground-truth verification
in place of an analyze pass (see below). This absence is a non-blocking N-note,
matching the same gap the sibling 087 review recorded for the same reason.

**Ground truth verified directly against the worktree** (not merely the plan's
self-report):

- Live registered-rule count is **55** (`docs/rules/rules-manifest.json` has 55
  `"id"` entries, confirmed via `json.load`) -- matches plan.md's "HR4 lands as
  rule 56" claim, appropriately hedged as re-verify-at-implement-time.
- **No `HR4` string and no `HR1` string exist anywhere** in `src/`, `docs/`, or
  `tests/` outside `specs/087-*` / `specs/090-*` -- both the id and the sibling
  087/HR1 feature are genuinely unlanded as code; there is no collision today and
  090 does not (and per its own text, must not) assume HR1 has landed.
- `templates/source-map.yaml`'s `meta:` block currently has `table_id`,
  `source_system`, `profiled_from`, `grain`, `primary_key`, `reviewed_by`,
  `reviewed_on` -- no `freshness` key yet, confirming T004's edit target is
  accurately described.
- `mappings/retail_store_sales/source-map.yaml` carries **no** `freshness` key
  today (grep returned zero matches) -- confirms the "landing precondition"
  claim that HR4 fires on zero real tables at present is not merely asserted,
  it is independently verifiable.
- `mappings/` contains exactly two filled instances (`retail_store_sales`,
  `demo_sample_orders`) -- matches plan.md's Project Structure list; no third
  filled map exists that the plan's footprint omits.
- `docs/readiness/source-drift.md` already uses the exact
  `[PENDING LIVE RE-PROFILE]` + non-`pass` convention this spec's FR-006
  explicitly reuses by name (`[PENDING LIVE FRESHNESS CHECK]`) -- the precedent
  cited in research.md is real, not invented.
- `src/retail/core.py` defines `is_test_path` (fixture-exemption helper) as
  claimed, confirming the plan's reuse of the existing mechanism is accurate
  rather than aspirational.

## Axis 1 -- hidden-principle-violation

Probe: does HR4 secretly self-grant an approval, decide a Principle-V judgment
call, or advise-instead-of-block?

The adversarial objection worth stating plainly before rebutting it: **a "gate"
that only fires on a present-but-malformed optional field, and never on the
field's outright absence, is advise-instead-of-block dressed up as a
fail-closed rule.** If a table can simply never add `meta.freshness` and incur
zero consequence, in what sense does `retail check` "gate" freshness at all?

Tracing this against the artifacts: the presence-gated design does not HIDE the
mandatory-ness decision, it HONESTLY DEFERS it, and the deferral is visibly
authored rather than silently absent:

- Spec FR-004 itself frames the ERROR condition as conditional on a table being
  "IN SCOPE for the freshness requirement," and FR-014 explicitly carves the
  scope-determination question out as OPEN, owner-only (Q-FR014-SCOPE). FR-004's
  clause (a) ("no `meta.freshness` block at all") is not silently dropped by the
  plan -- it is correctly read as vacuously unsatisfiable until FR-014 names an
  in-scope set, and the spec's own text says as much ("This spec does NOT assert
  that any specific already-committed `source-map.yaml`... is in scope or in
  violation"). Tasks T029-T031 implement clause (b) (present-but-malformed);
  T032 implements the clause-(a) short-circuit explicitly, with a code-comment
  requirement citing Q-FR014-SCOPE "so the deferred ruling is visibly authored,
  not silently absent" -- this is the correct Principle-V shape, not a
  workaround of it.
- research.md's "Landing precondition" section names the mechanism by its
  actual effect ("presence-gating can be trivially bypassed by never adding the
  block at all... This is NOT a loophole this feature quietly accepts as a
  permanent design; it is the explicit, visible seam where FR-014's ruling
  plugs in") -- an adversarial reviewer's objection is pre-empted in the
  artifact's own text, not evaded by omission.
- The two things that WOULD constitute a hidden self-grant -- (1) auto-filling
  a plausible `expected_cadence`/`max_staleness` on an existing table to make
  it "pass," or (2) writing an `approvals[]`/`readiness-status.yaml` entry --
  are both explicitly forbidden (FR-008) and mechanically tested for
  (T034 greps for write calls against those paths; T005/T032 are checklist
  confirmations that neither committed map is touched). Neither occurs anywhere
  in the design.
- Distinguishing the mechanical grammar (C1/C2, "which tokens count as
  well-formed") from the governance-shape question (FR-014, "which tables must
  supply the block") is itself a Principle-VI-correct move: the former is fixed
  now because it is not a business/SLA judgment (data-model.md "Why this
  shape"), the latter is left open because it is exactly a business-SLA /
  rollout judgment only a named human can make.

Verdict: **PASS**. The presence-gated shape is a disclosed, cited, and
mechanically-enforced DEFERRAL of a real Principle-V question, not a
concealment of one. See the Notes section below for the load-bearing caveat
this PASS depends on: the deferral must stay visibly open, and any future
change that quietly makes absence an ERROR (or invents an approval shape)
without an owner ruling would flip this axis.

## Axis 2 -- assumes-deferred-capability

Probe: does any artifact assume F016, a live DB, or a running adapter exists?

- HR4 is 100% static: `ctx.tracked_files` reads only, a LAZY `import yaml` kept
  out of the static-core chain (plan.md Technical Context, mirroring the
  HR1/SF1 precedent), no database connection, no Power BI/PBIP surface read
  (Constitution Check row VIII; FR-003, FR-006).
- F016 (Power BI execution adapter) is explicitly named as assumed NOT to exist
  and never invoked (research.md "Deferred capabilities NOT assumed"; spec
  Overview boundary section).
- The live arrival-time comparison (`MAX(<date column>)` vs. declared
  `max_staleness`) is explicitly named as the deferred half and is not
  computed, simulated, or approximated anywhere -- data-model.md's "Non-goals"
  states "No live/measured arrival-time field anywhere," and T034 is a
  dedicated source-inspection test asserting no DB/network API call and no
  elapsed-time computation exists in `rule_hr4.py`'s source, a mechanical
  check rather than a docstring promise.
- HR1 (087, the sibling `HR*` feature) is correctly NOT assumed to have landed
  -- research.md states this explicitly and the ground-truth check above
  confirms neither exists in the tree yet, so the "does not assume HR1 landed"
  claim is not merely aspirational.
- FR-006's `[PENDING LIVE FRESHNESS CHECK]` marker is recorded as a FUTURE
  surface's contract (most likely `retail validate`, spec 082) and Clarification
  C4 explicitly confirms this feature introduces no live-reporting surface of
  its own and never emits the marker itself -- the deferred capability is named
  without being assumed to exist or partially built.

Verdict: **PASS**. No deferred capability (F016, live DB, running adapter) is
assumed anywhere; the one live-adjacent artifact (the marker string) is
recorded as a contract for a not-yet-built surface, never invoked.

## Axis 3 -- c086-leak

Probe: does any template/label bake in domain-specific values instead of
staying generic (Principle VII)?

- The token grammar (data-model.md) uses only generic calendar vocabulary
  (`daily|weekly|monthly|quarterly|annual|one_time/static`, and a
  magnitude+calendar-unit duration regex) -- no C086/`retail_store_sales`/
  pharmacy-specific cadence value appears in the grammar itself.
- FR-011 explicitly forbids inlining any C086/`retail_store_sales` cadence
  value, column name, or table name into the schema template or rule logic,
  and T038 is a dedicated grep-verification task (rule module, template's new
  block, fixture authoring comments) at build time -- a mechanical check, not
  merely a stated intent.
- The template edit's placeholder text (T004,
  `"<cadence: daily|weekly|monthly|quarterly|annual|one_time>"`) is illustrative
  schema documentation, matching the existing convention already used by the
  template's other `meta` fields (`"<TABLE_ID>"`, `"<source_system>"`).
- `retail_store_sales` is cited ONLY as a fact ("carries no `meta.freshness`
  block today," verified true by this review's own grep) never as a source of
  a copied cadence/duration value -- the plan explicitly leaves both committed
  filled maps UNCHANGED and READ-ONLY (plan.md Project Structure, T005), so
  there is no file where a real value could leak into a generic artifact via
  copy-paste.
- Watch item for the implementer (carried forward, not a spec defect): T004's
  authoring comment and the fixture corpus under `tests/fixtures/source_freshness/`
  must stay illustrative and never literally copy a real value from either
  committed instance -- the same class of leak vector the 087 review flagged
  for its own manifest-scaffold comments. T038's grep is positioned to catch
  this if it happens.

Verdict: **PASS**. No c086/pharmacy specifics are baked into the rule logic,
the schema template edit, or the grammar; the one real-table citation
(`retail_store_sales` has no block today) is an honest fact about the tree,
not a copied value.

## Axis 4 -- fabricated-confidence

Probe: does any artifact emit a numeric score/health/maturity/completeness
count?

- HR4 emits the existing `Finding` dataclass unchanged (`rule_id`/`severity`/
  `message`/`locator`) -- no new numeric field is introduced anywhere
  (data-model.md "FreshnessFinding," FR-007).
- FR-007 explicitly forbids a numeric confidence/health/maturity/freshness
  score AND an "N of M" / completeness tally, and explicitly clarifies the one
  place a number legitimately appears: a human-DECLARED `max_staleness` value
  (e.g. `"3 days"`) is a declared SLA input, not a computed/rolled-up rating --
  this distinction is drawn correctly and consistently across spec (FR-007),
  plan (Constitution Check hard-rule-#9 row), and data-model.md ("Why this
  shape").
- T034 mechanically greps `rule_hr4.py`'s source for percentage/ratio/"N of M"
  formatting in any emitted message string, in addition to the DB/network
  checks -- again a build-time mechanical test, not a review-only claim.
- The one integer anywhere in this feature's own footprint is the rule COUNT
  (55 -> 56), which is the same `len(rules-manifest.json)` mechanism every
  other rule addition already uses (SC2's reconciliation) -- not a
  conformance/freshness score, and correctly hedged in plan.md/tasks.md as
  "re-verify at implement time" given the number of parallel in-flight
  rule-adding features (verified live at 55 by this review, matching the
  plan's stated baseline).
- No maturity/health label of any kind is introduced; `Severity` stays the
  existing `ERROR`/`WARNING` enum, and data-model.md explicitly notes HR4 has
  no WARNING branch at all (every triggering case is ERROR).

Verdict: **PASS**. No fabricated or invented number anywhere; the declared SLA
string is correctly distinguished from a forbidden score, and the rule-count
integer is the same authoritative `len()` every sibling rule-adding feature
already uses.

## Axis 5 -- over-scope

Probe: does the plan do more than its one readiness-stage job, or cross into
another feature's territory?

- Deliverables are tightly bounded: one new schema key (`meta.freshness`, two
  sub-keys, no new file), one new rule module (`rule_hr4.py`), the same
  six-surface wiring lockstep every new rule already requires, and one new
  fixture corpus. No new manifest file is introduced (correctly distinguished
  from HR1's `conformed-dimension-map.yaml` in research.md's "stay distinct"
  section -- HR4 evaluates one table's own file, not a cross-table shape).
- The plan explicitly REFUSES three scope-expansion temptations that would
  have been easy to fold in: (a) it does not extend `retail validate` or open
  a database connection to compute an actual arrival-time comparison, even
  though that would "complete" the freshness story (FR-006, Assumptions --
  named as a future seam, not built here); (b) it does not fold staleness
  together with missing-segment/date-spine completeness detection even though
  PB-SQL-09 as documented bundles the two (FR-010, explicitly out of scope,
  left to a future spec); (c) it does not touch `docs/readiness/source-drift.md`'s
  taxonomy or templates even though source-drift is the nearest-sounding
  neighbour (FR-009, and this review's grep confirms the file's existing
  `[PENDING LIVE RE-PROFILE]` convention is only CITED by name, never edited).
- It adds no eighth readiness stage, no fifth status value, and no
  `readiness-status.yaml`/`approvals[]` key (Assumptions, FR-008) -- confirmed
  by this review's reading of the plan's file footprint, which lists
  `source-ready.md` as REFERENCE ONLY, unedited.
- It does not touch `rule_hr1.py`, `conformed-dimension-map.yaml`, or
  `rule_sf1.py`/`shared-spine.yaml` -- research.md's "stay distinct" sections
  are explicit about non-overlap with both sibling `HR*`/`SF1` precedents, and
  the ground-truth check confirms neither HR1 nor SF1's manifest is read or
  written by this feature's described file footprint.
- The one place scope discipline is genuinely tested, not just claimed: FR-014
  (the mandatory-vs-going-forward ruling) is the single most tempting place to
  silently over-decide, because deciding it either way would make the feature
  "feel more finished." The plan declines on both directions (does not make
  absence an ERROR everywhere; does not explicitly grandfather-and-close the
  question either) and leaves it open for the owner (T043 "OWNER SEAM -- OPEN,
  do not answer"). This is the correct discipline, mirroring 087's refusal to
  invent an `approvals[]` shape for its own open question (FR-016 there,
  FR-014 here).

Verdict: **PASS**. Scope is disciplined; the plan actively resists the three
most plausible scope-creep paths (live comparison, missing-segment folding,
source-drift touch) rather than merely avoiding them by omission, and the one
governance question genuinely tempting to over-decide (FR-014) is left open
rather than silently resolved either direction.

## Notes / carry-forward (non-blocking)

- **Headline note -- this feature's real-tree enforcement is currently 100%
  prospective, more so than the 087/HR1 precedent it borrows its shape from.**
  In 087, the conformed-name check had real (if form-split-dormant) bite and
  only the grain LIMB was deferred pending a schema prerequisite. Here,
  presence-gating means the ENTIRE Finding-emitting path is gated behind
  FR-014, not one limb of it: on the current tree (verified above -- neither
  `retail_store_sales` nor `demo_sample_orders` carries a `freshness` block)
  HR4 fires on **zero real tables**. Its only exercised path today is via test
  fixtures (T014-T027); a data owner who never adds the block incurs zero
  consequence, by design, until the owner rules Q-FR014-SCOPE. This is not a
  defect -- it is the explicit, honestly-disclosed shape of "declare + check
  presence, defer the live/mandatory question" (Principle VIII/V) -- but
  implementers and future reviewers should not describe HR4 as "actively
  protecting against PB-SQL-09" until FR-014 is ruled and at least one table's
  scope is settled. Overclaiming this feature's current bite in a status
  report or a PR description would itself be close to a fabricated-confidence
  problem in spirit (Axis 4), even though no artifact here makes that
  overclaim -- quickstart.md and research.md are both explicit and honest
  about the presence-gated inertness.
- **The FR-004(a)/(b) split is real and correctly resolved, but easy to
  misread on a first pass.** Spec FR-004 states HR4 "MUST fail closed... when
  that table's `source-map.yaml` exists and either: (a) carries no
  `meta.freshness` block at all, or (b) carries a... block missing, blank, or
  unparseable." Read naively, the plan/tasks under-implement FR-004 by only
  building clause (b). The resolution (present in the artifacts, but worth
  stating explicitly for the record since an adversarial pass exists to
  surface exactly this kind of apparent contradiction): clause (a) is
  conditional on "IN SCOPE," FR-014 leaves the in-scope set undetermined, so
  clause (a) is vacuously satisfied (fires on nothing) until FR-014 names a
  scope -- consistent across spec (FR-004's own caveat sentence), research.md
  ("Landing precondition"), and tasks.md (T032's explicit short-circuit +
  citation). This is not a spec/plan mismatch; it is a spec clause whose
  antecedent is not yet true. Recommend the eventual implementation PR
  description say this plainly, since a code reviewer unfamiliar with FR-014
  will otherwise flag it as a missed requirement.
- **FR-014 must stay genuinely open through implementation.** No task answers
  Q-FR014-SCOPE; T043 is an explicit "do not answer" checklist confirmation.
  Any future change that (i) makes outright absence of `meta.freshness` an
  ERROR for some or all tables, (ii) auto-fills a plausible SLA value on an
  existing table, or (iii) invents an `approvals[]`/`readiness-status.yaml`
  shape for this concern -- without a named-human ruling recorded first --
  would flip Axis 1 from PASS to a violation. This is the single highest-risk
  regression path for this feature.
- **c086-leak watch item, mechanical not structural.** Keep T038's grep as a
  hard gate (not a courtesy check) against the template's new placeholder
  block and the fixture corpus's authoring comments -- the only realistic leak
  vector is an implementer copy-pasting a real value from
  `retail_store_sales`/`demo_sample_orders` into a "helpful" example comment
  instead of using an illustrative placeholder.
- **Rule-count and family-list serialization point (55 -> 56, family `HR`).**
  Verified 55 as of this review, matching plan.md/research.md's stated
  baseline; both already correctly hedge that a concurrently-landing sibling
  (087/HR1) may claim 56 and the `HR` family first, in which case 090 becomes
  57 without duplicating the family token. No action needed beyond honoring
  the plan's own re-verify-at-implement-time instruction.
- **`analysis.md` is absent for this feature.** `speckit-analyze` has not been
  run. This review substituted direct ground-truth verification (rule count,
  HR1/HR4 absence, template/filled-map state, source-drift marker precedent)
  for the missing cross-artifact analyze pass, matching the same substitution
  the 087 review made. Recommend running `speckit-analyze` before or during
  implementation.
- **Optional, non-blocking grammar note.** The closed cadence enum and strict
  duration regex will false-positive some legitimate real-world phrasings not
  in the vocabulary (e.g. "fortnightly," "2 business days," "twice weekly").
  Given the enforcement is currently inert on the real tree (see headline
  note), this costs nothing today, but whoever eventually extends the grammar
  under a ratified FR-014 should expect early false-positive reports from a
  data owner phrasing a real SLA in a way the closed enum does not recognize.
  Not a spec defect -- C1 explicitly prioritizes a well-defined fail-closed
  test over exhaustive phrasing coverage, which is the right tradeoff for a
  small, generic vocabulary Principle VII requires.

## Verdict

**Verdict**: PASS-WITH-NOTES

All five axes clear on direct ground-truth verification (rule count, HR1/HR4
absence, template and filled-map current state, and the source-drift marker
precedent were independently checked against the live tree, not taken on the
plan's word). The design correctly distinguishes a mechanical vocabulary
choice (fixed now, C1/C2) from a genuine governance-shape judgment (FR-014,
left open for the owner), and it actively refuses three plausible
scope-expansion paths (live comparison, missing-segment folding, source-drift
edit) rather than merely avoiding them by omission. The headline caveat is
that this discipline comes at a real cost: the feature's enforcement value is
currently 100% prospective (fires on zero real tables today, exercised only by
fixtures) until FR-014 is ruled -- this is an honest, disclosed tradeoff, not a
concealment, and is why the verdict is PASS-WITH-NOTES rather than a bare PASS.
No CRITICAL or HIGH finding; no axis is RISK or FAIL; blocking_findings is
empty.
