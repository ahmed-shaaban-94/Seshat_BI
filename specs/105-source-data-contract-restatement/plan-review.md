# Adversarial Plan-Review: Source Data-Contract -- Forward Schema + Arrival + Restatement Policy (HR12)

**Feature**: `105-source-data-contract-restatement` | **Date**: 2026-07-04
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports findings,
edits nothing). Artifacts reviewed: spec.md, plan.md, tasks.md, research.md,
data-model.md, quickstart.md.

**Precondition check**: spec.md, plan.md, tasks.md are present. **`analysis.md`
does NOT exist in this feature directory** -- `speckit-analyze` has not been run
for 105, so there is no cross-artifact analyze verdict to cite. This review does
not fabricate that precondition; it proceeds on spec + plan + tasks + research.md
+ data-model.md + quickstart.md, and performs its own ground-truth verification in
place of an analyze pass (see below). This mirrors the same substitution the 087
and 090 sibling reviews made for the identical reason.

**Ground truth verified directly against the worktree** (not merely the plan's
self-report):

- Live registered-rule count is **55** (`docs/rules/rules-manifest.json`, counted
  live) -- matches plan.md/research.md's stated baseline for "HR12 lands as rule
  56," appropriately hedged as re-verify-at-implement-time.
- **No `HR12` string exists anywhere** in `src/`, `docs/`, `tests/`, `templates/`,
  or `mappings/` outside `specs/105-*` -- the id is genuinely unclaimed today; no
  collision with a concurrently-merged draft.
- **`templates/source-data-contract.yaml` does not exist yet** -- confirmed by
  directory listing of `templates/`. This is purely a planned deliverable (FR-001,
  T004); the plan does not misrepresent it as already present.
- **Zero `mappings/**/source-data-contract.yaml` files exist** on the tree (both
  `mappings/retail_store_sales/` and `mappings/demo_sample_orders/` checked) --
  confirms the "opt-in, currently inert on real tables" landing claim in
  research.md is independently verifiable, not merely asserted.
- `templates/source-map.yaml`'s `meta:` block carries no `freshness` key today,
  and a repo-wide grep for `meta.freshness` / `meta["freshness"]` returns zero
  matches in `src/retail/` -- confirms 090/HR4 has not landed and there is no
  live collision surface for FR-004's "must not read/write `meta.freshness`"
  constraint to violate.
- `templates/source-map.yaml`'s own comment literally reads `# SISTER ARTIFACTS
  IN THE MAPPING GATE (a reviewer reads all 5 as a set)` -- confirms research.md's
  claim that the Mapping Ready gate's required-artifact list is exactly five, and
  that this feature's new file is correctly kept off that list (FR-010).
- `src/retail/rules/rule_sf1.py` contains `except (OSError, yaml.YAMLError) as
  exc:  # malformed/unreadable -> fail loud` -- the exact precedent research.md
  and data-model.md cite for HR12's malformed-YAML branch is real code, not an
  invented analogy.
- `src/retail/rules/assumption_coherence.py` contains a `_TEMPLATE_PATH` exclusion
  constant, an `is_test_path` import, and a lazy `import yaml  # lazy: keep the
  retail-check core stdlib-only at module scope` comment -- the AL2 read-path
  precedent research.md cites is real and matches the claimed shape exactly.
- `docs/readiness/source-ready.md` states plainly: `This stage has no retail
  check / retail validate gate. The gate is a review:` -- confirms HR12 would be
  the FIRST static `retail check` rule to attach evidence at Source Ready, exactly
  as research.md claims (see the Notes section below for why this is a
  surfaced-and-resolved apparent contradiction, not an oversight).
- `src/retail/rules/readiness_status.py` reads `blocking_reasons[]` as
  human-authored data on the stage-verdict object (`block.get("blocking_reasons")`)
  rather than computing it from arbitrary rule Findings -- confirms the mechanism
  research.md relies on to resolve FR-013's "evidence vs. stage-blocking" layering
  is real, not a hoped-for design.
- The three named sibling features (089, 090, 093) are all `**Status**: Draft` in
  their own spec.md files -- confirms they are correctly treated as reserved,
  unlanded neighbours rather than already-shipped tools this plan could quietly
  lean on.

## Axis 1 -- hidden-principle-violation

Probe: does HR12 secretly self-grant an approval, decide a Principle-V judgment
call, or advise-instead-of-block?

The sharpest objection worth stating plainly before rebutting it: **an opt-in
presence check, combined with FR-013's interim non-blocking default, is a rule
that (a) never fires on a table that simply never adds the file, and (b) even
when it DOES fire on a present-but-broken contract, does not block the stage
verdict by default -- that is advise-instead-of-block wearing a fail-closed
costume, twice over.**

Tracing this against the artifacts and the ground truth above:

- HR12 itself is genuinely fail-closed at the CHECK level, not merely worded that
  way: FR-002/FR-006 require an `ERROR` Finding naming the specific incomplete
  section whenever the file is present but incomplete, and User Story 2's three
  acceptance scenarios plus Clarifications Q3/Q6 extend this to a schema entry
  missing `type` and to an unparseable YAML file. Nothing in spec, plan, or tasks
  quietly downgrades an incomplete-but-present contract to a pass or a silent
  skip -- T011/T012 implement exactly this, and T013 re-confirms no regression.
- The absence-case (FR-002's opt-in posture) is not a hidden default -- it is an
  explicitly named, explicitly justified precedent match ("mirrors 090/HR4 and
  093/HR7's own declare-or-default posture"), consistent with Principle VI
  (defaults-then-deviations): a table incurs zero new burden until it opts in by
  creating the file.
- The genuinely open question -- whether a present-but-broken contract should
  also block the STAGE's `pass` verdict (FR-013) -- is not silently resolved
  either direction. It is recorded as `[OPEN -- owner ruling required,
  unresolved]` in the spec itself, with an explicitly-labeled "safe-default
  STANCE for implementation sequencing only, not a resolution." research.md's
  Q-ENFORCEMENT-STRENGTH section and tasks.md's Requirement Coverage Map both
  repeat that no task answers it and no task wires HR12's Finding into
  `blocking_reasons[]`.
- Critically, this deferral is MECHANICALLY DISCONNECTED, not merely
  documented-as-deferred: the ground-truth read of `readiness_status.py` above
  confirms `blocking_reasons[]` is read as separately-authored data on the
  stage-verdict object, never auto-computed by scanning rule Findings. This means
  HR12's own Finding (visible in `retail check` output) and a table's Source Ready
  stage verdict are structurally two different layers today -- there is no code
  path by which HR12 could accidentally "leak" into blocking a stage even if the
  authors wanted it to, absent someone deliberately wiring it in later. The
  deferral is therefore not just asserted in prose; it is currently true of the
  code it depends on.
- The two concrete actions that WOULD constitute a hidden self-grant -- (1)
  auto-filling a plausible schema/cadence/restatement value to make an existing
  table "pass," or (2) writing an `approvals[]`/`readiness-status.yaml` entry --
  are both explicitly forbidden (FR-005, FR-004) and are not performed anywhere
  in the design; research.md's "Landing analysis" explicitly refuses to fabricate
  a filled instance for either real table, citing Principle V by name.

Verdict: **PASS**. The presence-gated, currently-non-blocking shape is a
disclosed, cited, and (as verified above) mechanically-unwired deferral of a real
Principle-V question, not a concealment of one. See the Notes section for the
load-bearing caveat this PASS depends on: the deferral must stay visibly open,
and any future change that quietly wires HR12's Finding into `blocking_reasons[]`
without a named owner ruling would flip this axis.

## Axis 2 -- assumes-deferred-capability

Probe: does any artifact assume F016, a live DB, or a running adapter exists?

- HR12 is 100% static by design and by the code shape it borrows: `ctx.tracked_files`
  reads only, a LAZY `import yaml` kept out of the package-level import chain
  (mirroring the verified AL2 precedent), no database connection, no Power BI/PBIP
  surface read (Constitution Check row VIII; FR-003).
- F016 (Power BI execution adapter) is explicitly named as assumed NOT to exist
  and is never invoked anywhere in spec, plan, research, or data-model.
- The live arrival-time comparison (`MAX(<date column>)` vs. the declared
  cadence) and live restatement-event detection are explicitly named as the
  deferred half (FR-003, User Story 3) and are not computed, simulated, or
  approximated anywhere. T014 (DSN-absent identical-Findings test) and T015 (a
  dedicated source-inspection test asserting no DB-driver import and no DSN/
  connection-string reference in the rule module) turn this into a mechanical
  build-time guard, not just a docstring promise.
- The 089/090/093 sibling `HR*` rules are correctly NOT assumed to have landed --
  research.md states this explicitly and the ground-truth check above confirms
  all three remain Draft with zero registered-rule presence today, so "HR12 is
  the next free id" is not built on a false premise about a sibling already
  having claimed it.
- No PENDING-marker or live-surface convention (unlike 090/HR4's `[PENDING LIVE
  FRESHNESS CHECK]`) is introduced or assumed by this feature; research.md is
  explicit that HR12 introduces no live-reporting surface of its own.

Verdict: **PASS**. No deferred capability (F016, live DB, running adapter) is
assumed anywhere in the design.

## Axis 3 -- c086-leak

Probe: does any template/label bake in domain-specific values instead of staying
generic (Principle VII)?

- The template shape in data-model.md uses only generic sentinel tokens
  (`REPLACE_ME_COLUMN_NAME`, `REPLACE_ME_COLUMN_TYPE`, `REPLACE_ME_ARRIVAL_CADENCE`,
  `REPLACE_ME_RESTATEMENT_POLICY`) and generic illustrative prose ("daily by 6am",
  "weekly on Mondays") -- no `retail_store_sales`/`demo_sample_orders`/pharmacy-
  specific column name, cadence value, or restatement mechanism appears in the
  template shape as documented.
- FR-007 explicitly forbids inlining any C086/`retail_store_sales` schema,
  cadence, or restatement specific into the template or HR12's fixed messages,
  and T026 is a dedicated build-time grep task against both the template and the
  rule module's fixed strings -- a mechanical check, not merely a stated
  intent, mirroring 090's own T038 precedent.
- `retail_store_sales` and `demo_sample_orders` are cited in research.md/plan.md
  ONLY as facts about the tree ("carry no `source-data-contract.yaml` today,"
  independently confirmed true by this review's own directory check) -- never as
  a source of a copied schema/cadence/restatement value. The plan explicitly
  states no filled instance is authored for either real table (Principle V), so
  there is no file in this feature's own footprint where a real value could leak
  into the generic template via copy-paste.
- **Caveat, not yet checkable**: `templates/source-data-contract.yaml` does not
  exist on the tree yet (confirmed above) -- this axis's PASS rests on the plan's
  DESCRIPTION of the template's future content (data-model.md), not on a file this
  review could grep directly. The leak risk is therefore purely build-time, carried
  forward as a watch item (see Notes) with T026 as its designated gate, exactly
  the same posture 090's review recorded for its own not-yet-authored template
  edit.

Verdict: **PASS**. As designed, the template and rule carry no domain-specific
value; the residual risk is a build-time copy-paste risk common to every
sibling feature in this batch, correctly gated by a dedicated grep task rather
than left to reviewer vigilance alone.

## Axis 4 -- fabricated-confidence

Probe: does any artifact emit a numeric score/health/maturity/completeness count?

- HR12 emits the existing `Finding` dataclass unchanged (`rule_id`/`severity`/
  `message`/`locator`) -- no new numeric field is introduced anywhere in
  data-model.md's `HR12Finding` entity.
- FR-009 explicitly forbids a numeric confidence/health/maturity score AND an
  "N of M" / completeness tally; data-model.md's message shape requires naming
  EACH incomplete section individually ("schema fails closed... arrival fails
  closed... never a single undifferentiated message"), which is categorical
  list-form, not a count. A phrasing like "2 of 3 sections incomplete" would
  violate FR-009 -- the design as written avoids this by listing sections, not
  tallying them, and this distinction should be treated as load-bearing during
  implementation (see Notes).
- T025 is a dedicated build-time grep task across every artifact this feature
  authors or edits (template, rule module, manifest, severity-posture, glossary)
  for a numeric confidence/health/maturity pattern or an "N of M" completeness
  pattern -- a mechanical gate, not a review-only claim.
- The one integer anywhere in this feature's own footprint is the rule COUNT
  (55 -> 56 in `rules-manifest.json`), the same `len()`-based mechanism every
  sibling rule-adding feature in this repo already uses for its own count
  reconciliation -- not a conformance/confidence score, and correctly hedged in
  plan.md/tasks.md/research.md as "re-verify live at implement time" given that
  089/090/093 are parallel drafts also contending for a next id (independently
  confirmed at 55 by this review, matching the stated baseline).
- No maturity/health label of any kind is introduced; `Severity` stays the
  existing `ERROR` enum (data-model.md notes HR12 has no `WARNING` branch --
  every incomplete/malformed case is `ERROR`).

Verdict: **PASS**. No fabricated or invented number appears anywhere in the
design; the rule-count integer is the same authoritative `len()` mechanism every
sibling feature already relies on, and the message-shape requirement (list
sections by name, never tally them) is explicit enough to prevent an
implementation-time drift into a disguised completeness count.

## Axis 5 -- over-scope

Probe: does the plan do more than its one readiness-stage job, or cross into
another feature's territory?

- Deliverables are tightly bounded: one new template file
  (`templates/source-data-contract.yaml`), one new rule module
  (`source_data_contract.py`), the same seven-surface wiring lockstep every new
  rule already requires, one doc-row edit to `source-ready.md`, and a test
  fixture corpus. No new readiness stage, no new top-level directory, no new key
  added to any existing schema file.
- The plan explicitly refuses the three most plausible scope-expansion paths a
  feature this close to 090/089/093 could easily have folded in, and each refusal
  is independently verifiable against the tree:
  - It does not add a key to `source-map.yaml` (FR-008, the collision-avoidance
    allocation) -- confirmed above: the live `meta:` block has no `freshness` key
    and the plan's file footprint never touches `source-map.yaml` at all.
  - It does not read `readiness-status.yaml` or raise a `stale_pass` blocker
    (FR-004, 089/HR3's concern) -- confirmed by the `blocking_reasons[]`
    mechanism check above: HR12's Finding and any stage's blocking list are
    structurally disconnected today.
  - It does not restate or re-implement 093/HR7's load-idempotency check even
    where the restatement policy text is expected to cite it by reference
    (FR-012) -- it points to 093/HR7 by name rather than duplicating its logic.
- It does not add a sixth artifact to the Mapping Ready gate's required list
  (FR-010) -- independently confirmed above via the template's own "SISTER
  ARTIFACTS... all 5 as a set" comment, which the plan correctly leaves
  unmodified.
- It does not touch `docs/readiness/source-drift.md`'s taxonomy or any future
  `source-drift-report.md` template, and does not fold restatement into the
  nine-class drift taxonomy (spec Boundary section, Edge Cases) -- source-drift
  is cited only as the conceptual foil the Overview names, never edited.
- The sharpest same-sounding-but-distinct boundary in this batch -- 105's
  supplier-facing `arrival.cadence` free text vs. 090's internal
  `meta.freshness` staleness tolerance -- is drawn explicitly and mechanically
  enforced: HR12 reads only `mappings/<table>/source-data-contract.yaml`; HR4
  reads only `source-map.yaml`'s `meta.freshness` key; neither rule reads the
  other's file, and the two may disagree in value without either rule detecting
  or flagging it (spec Edge Cases, explicitly out of scope here). This review's
  grep confirms there is no collision on the tree today for this boundary to be
  tested against.
- The one governance question genuinely tempting to over-decide in this feature
  -- FR-013's enforcement-strength question -- is left open rather than silently
  resolved either direction, mirroring 090/FR-014 and 093's own analogous
  Q-APPROVAL-SEAM treatment in the same dated batch.

Verdict: **PASS**. Scope is disciplined; the plan actively resists the three most
plausible scope-expansion paths (source-map.yaml key, stale_pass blocker,
HR7 duplication) with mechanically-verifiable non-interaction rather than merely
avoiding them by omission, and the one genuinely tempting governance question
(FR-013) is left open rather than silently resolved.

## Notes / carry-forward (non-blocking)

- **Headline note -- this feature's real-tree enforcement is currently 100%
  prospective, and doubly so compared to most siblings.** Verified above: zero
  `source-data-contract.yaml` files exist anywhere on the tree today, so HR12
  fires on zero real tables at landing. Beyond that, even once a table DOES opt
  in and its contract later breaks, FR-013's interim default means the resulting
  ERROR Finding is visible in `retail check` output but is NOT, by itself, wired
  into that table's Source Ready `blocking_reasons[]` -- the stage verdict stays
  a human review either way, exactly as `source-ready.md`'s current text already
  states. This is not a defect; it is the explicit, honestly-disclosed shape of
  "declare + check presence/well-formedness, defer the mandatory/blocking
  question" (Principle VIII/V). Recommend that any future status report or PR
  description avoid describing HR12 as "gating Source Ready" until FR-013 is
  ruled -- overclaiming its current bite would itself brush against the
  fabricated-confidence spirit (Axis 4) even though no artifact here makes that
  overclaim; quickstart.md and research.md are both explicit and honest about
  the presence-gated, currently-non-blocking shape.
- **The "first retail check rule at a review-only stage" point is real and
  correctly resolved, but worth stating plainly for the record.** This review's
  own grep confirms `docs/readiness/source-ready.md` currently says "This stage
  has no `retail check` / `retail validate` gate. The gate is a review." Read
  naively, HR12 landing at this stage looks like a contradiction of that
  sentence. The resolution, present in the artifacts: HR12 adds an ADDITIONAL,
  OPT-IN EVIDENCE check that a human reviewer may cite -- it does not become the
  stage's gate, and the stage's actual pass/blocked/warning decision procedure
  (human review of the profile + proposed semantics) is unchanged (FR-010, the
  plan's T005 doc-edit description). This is not a spec/plan mismatch; it is a
  layering distinction (a rule Finding vs. the stage's own gate procedure) that
  an implementer unfamiliar with the distinction could otherwise flag as a
  missed requirement or, worse, "fix" by wiring HR12 into the stage gate
  unprompted. Recommend the eventual implementation PR description state this
  layering explicitly.
- **FR-013 must stay genuinely open through implementation.** No task in
  tasks.md answers Q-ENFORCEMENT-STRENGTH; the Requirement Coverage Map
  explicitly marks FR-013 as "intentionally NOT assigned an implementation
  task." Any future change that (a) wires HR12's Finding into a table's
  `readiness-status.yaml` `blocking_reasons[]`, (b) auto-fills a plausible
  schema/cadence/restatement value on an existing table to force a pass, or (c)
  makes the file's outright absence an ERROR for some or all tables -- without a
  named-human ruling recorded first via the approval-console workflow -- would
  flip Axis 1 from PASS to a violation. This is the single highest-risk
  regression path for this feature, identically shaped to 090/FR-014's own
  carried-forward warning.
- **c086-leak watch item, mechanical not structural.** `templates/source-data-
  contract.yaml` does not exist yet (confirmed above); this axis's PASS rests on
  the plan's description of its future content. Keep T026's grep as a hard gate
  (not a courtesy check) against the template file once authored and against the
  fixture corpus's authoring comments -- the only realistic leak vector is an
  implementer copy-pasting a real value from `retail_store_sales`/
  `demo_sample_orders` into a "helpful" example comment instead of using the
  sentinel/illustrative placeholder.
- **Message-shape watch item (Axis 4).** data-model.md correctly specifies that
  HR12 names each incomplete section individually rather than tallying them.
  Implementers should double-check the actual emitted message string at build
  time does not drift into an "N of 3 sections complete" or similar phrasing,
  which reads innocuous but would violate FR-009's completeness-count
  prohibition. T025's grep is the designated gate for this; keep it literal
  (checking for tally/ratio patterns), not just a keyword check for the word
  "score."
- **Rule-count and family-list serialization point (55 -> 56, family `HR`).**
  Verified 55 as of this review, matching plan.md/research.md's stated baseline.
  research.md and tasks.md (T001, T020) already correctly hedge that a
  concurrently-landing sibling (089/090/093) may claim 56 and the `HR` family
  token first, in which case 105/HR12 becomes 57 (or later) without duplicating
  the family token. No action needed beyond honoring the plan's own
  re-verify-at-implement-time instruction.
- **`analysis.md` is absent for this feature.** `speckit-analyze` has not been
  run. This review substituted direct ground-truth verification (rule count,
  HR12 absence, template/mapping-tree current state, sister-artifact comment,
  SF1/AL2 precedent code, `blocking_reasons[]` mechanism, sibling spec statuses)
  for the missing cross-artifact analyze pass, matching the same substitution
  the 087 and 090 reviews made. Recommend running `speckit-analyze` before or
  during implementation.
- **Boundary-drift watch item (090/HR4 vs. 105/HR12), non-blocking.** The spec's
  own Edge Cases correctly declines to reconcile a table that declares both
  `meta.freshness` and this feature's `arrival.cadence` with disagreeing values
  -- each rule stays silent about the other's content. This is the right call
  today (no collision exists on the tree, confirmed above), but it is worth
  flagging as a plausible future feature request ("why do these two disagree and
  nothing tells me") rather than a defect of this spec; the spec is explicit
  that reconciling the two is out of scope here and would be a future
  cross-artifact concern.

## Verdict

**Verdict**: PASS-WITH-NOTES

All five axes clear on direct ground-truth verification (rule count, HR12
absence, template/mapping-tree current state, the sister-artifact comment, the
SF1/AL2 precedent code, and the `blocking_reasons[]` mechanism were independently
checked against the live tree, not taken on the plan's word). The design
correctly separates a mechanical, purely-structural check (HR12 itself, fixed now)
from a genuine governance-shape judgment (FR-013, left open for the owner), and it
actively resists three plausible scope-expansion paths (a `source-map.yaml` key,
a `stale_pass` blocker, restating 093/HR7's idempotency check) with
mechanically-verifiable non-interaction rather than avoiding them by omission
alone. The headline caveat is that this discipline comes at a real, disclosed
cost: the feature's enforcement value is currently 100% prospective (fires on
zero real tables today) and, even once opted in, does not block the Source Ready
stage verdict under FR-013's interim default -- this is an honest tradeoff, not a
concealment, and is why the verdict is PASS-WITH-NOTES rather than a bare PASS.
No CRITICAL or HIGH finding; no axis is RISK or FAIL; blocking_findings is empty.
