# Adversarial Plan-Review: Returns/Refunds Fact Worked Example (Negative-Quantity Additivity)

**Feature**: `096-returns-refunds-fact-example` | **Date**: 2026-07-04
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports findings,
edits nothing). Artifacts reviewed: spec.md, plan.md, tasks.md, analysis.md, plus
research.md, data-model.md, quickstart.md (present in the feature directory).

**Precondition check**: spec.md, plan.md, tasks.md are present. **`analysis.md` IS
present** for this feature (unlike several recent siblings, e.g. 094/095, where it
was absent) -- `speckit-analyze` has already been run and reports 0 CRITICAL/HIGH
findings, 2 MEDIUM (F1, F2), 1 LOW (F3), 16/16 FR coverage, 7/7 SC coverage, 0
constitution violations. This review does NOT take that verdict on faith: every
load-bearing factual claim analysis.md relies on was independently re-verified
against the live worktree below, and F1/F2/F3 are each re-derived from source, not
merely cited.

**Ground truth verified directly against the worktree** (not merely the plan's or
analysis.md's self-report):

- `docs/readiness/readiness-model.md` lines 33-39 confirm the seven stages are:
  1 Source Ready, 2 Mapping Ready, 3 Silver Ready, 4 Gold Ready, **5 Semantic Model
  Ready**, **6 Dashboard Ready**, 7 Publish Ready. spec.md line 263 (FR-002) and
  plan.md's Summary both read "Stages 2 through 6 ... Mapping Ready through
  **Semantic Model Ready**" -- Semantic Model Ready is Stage 5, not Stage 6.
  Independently confirms analysis.md's F1 exactly: the numeric range (2-6) is
  right, the trailing NAME is off by one stage.
- `src/retail/rules/additivity_consistency.py` line 49:
  `_CORPUS_RE = re.compile(r"^skills/retail-kpi-knowledge/contracts/[^/]+\.md$")` --
  confirmed AD1's static-check surface is exactly and only
  `skills/retail-kpi-knowledge/contracts/*.md`. `mappings/<rr>/metrics/*.yaml` (this
  feature's two new contract files) is categorically outside that glob. SC-002's
  "AD1 emits zero new ERROR findings" is therefore true by construction, regardless
  of whether the two new contracts are actually AD1-legal -- confirms analysis.md's
  F3 exactly.
- `templates/metric-contract.yaml` grepped for `additivity`/`Additivity`: zero
  matches. Confirms the plan/data-model's repeated claim that the template has no
  additivity field and this feature must not add one (FR-005).
- `docs/decisions/0002-retail-cleaning-defaults.md` lines 56-59 confirm RC8's exact
  text: "Keep returns, and derive an `is_return` boolean from the authoritative
  column (billing/transaction type), never from the measure sign." Matches
  research.md's citation verbatim.
- `specs/087-conformed-dimension-readiness/` currently contains spec.md, plan.md,
  tasks.md, data-model.md, quickstart.md, research.md, AND plan-review.md --
  confirmed research.md Sec 2 row 4's claim ("087 is spec-only") is stale, matching
  analysis.md's F2. However, `grep -r "HR1" src/` returns zero matches and
  `docs/quality/conformed-dimension-map.yaml` does not exist on disk -- the
  load-bearing conclusion this feature's FR-012 design actually depends on (the
  gate is not implemented, so this feature cannot invoke it) is independently
  re-confirmed true. F2 is a stale citation about a sibling spec's paperwork stage,
  not a broken design dependency.
- `specs/084-worked-example-factory/contracts/worked-example-completeness.md`
  exists on disk with the Tier-1 section structure (A-H) the plan/tasks cite
  (Domain selection, Source Ready, Mapping Ready, Silver/Gold Ready, Semantic Model
  Ready, Dashboard Ready, Publish Ready, cross-cutting) -- FR-016's citation target
  is real, not a forward reference to a file that doesn't exist.
- `mappings/retail_store_sales/` exists with all seven named artifacts
  (source-profile.md, source-map.yaml, assumptions.md, unresolved-questions.md,
  reconciliation-report.md, reconciliation-bronze-to-gold.md,
  readiness-status.yaml) plus `metrics/`/`design/`/`handoff/` subdirectories (per
  the worked-example doc) -- the precedent this feature's Project Structure mirrors
  is real and matches the shape claimed.
- `mappings/retail_store_sales/` holds **no raw data file** -- its
  `source-profile.md` line 16/21 states the source is "Kaggle 'retail store sales
  (dirty)' -- single CSV export," but that CSV is not committed under
  `mappings/retail_store_sales/` itself. This is a real (minor) mismatch with
  FR-003/research.md Sec 3's claim that 096's committed synthetic dataset will be
  "in the same posture `retail_store_sales` used for its own source" -- see Notes.
- `docs/worked-examples/` contains exactly `README.md` and `retail-store-sales.md`
  -- confirms no second worked example exists yet and this feature is genuinely
  first-of-its-kind, not a restatement.

## Axis 1 -- hidden-principle-violation

Probe: does the plan secretly self-grant an approval, decide a Principle-V
judgment call, or advise-instead-of-block?

- Every genuine business-policy judgment call the domain doc's own ambiguities
  raise is explicitly routed to OPEN-owner-ruling status, never silently answered:
  VAT/tax treatment of refunds (FR-008, Clarification Q2, SCOPE GUARD-cited by
  name) and the operative reporting date axis (FR-013, Clarification Q1b, KPI
  ambiguity A3) both stay `open` in `unresolved-questions.md` per T011/T027, with
  no default value substituted for either.
- FR-013 is the sharpest Principle-V/VI boundary in this spec and it is drawn
  correctly: a Principle-VI REVERSIBLE default (return date = the fact's own
  transaction date) governs ONLY the example's own synthetic worked-figure
  arithmetic, and the spec's own bracketed text plus tasks.md's dedicated
  "Principle-V carve-out" section plus T027 all explicitly bar that default from
  being cited as having resolved which axis is the business's actual operative
  reporting axis. This is a real, load-bearing distinction (a worked example needs
  SOME axis to compute a demo figure; adopting one reversibly is not the same as
  ruling on it), not a rhetorical hedge -- and three independent artifacts (spec,
  tasks, and the carve-out section) all repeat the same boundary consistently.
- FR-010/T013/T022/T025 design every named-human approval seam (minimum Mapping
  Ready, Semantic Model Ready) to start and STAY with an empty `approvals[]` entry;
  T025 explicitly sweeps ALL SEVEN stages to confirm no seam is filled by the
  authoring agent. No task anywhere sets a stage to `pass` on the strength of the
  artifacts alone -- T016 explicitly requires `blocked` for `silver_ready`/
  `gold_ready` specifically BECAUSE no live DB exists to back a `pass`, which is
  the correct fail-closed posture, not an advisory warning stapled onto a `pass`.
- One load-bearing question an adversarial reviewer must not wave past: does
  citing RC8 as "the applied default, not a deviation" (Assumptions;
  T008/T010) quietly promote a Principle-V judgment (should THIS table's returns
  be classified from a transaction-type column) into a rubber-stamped default the
  agent applies without real profiling? Traced through: no -- RC8 is an
  ALREADY-ratified, shipped kit-wide default (`docs/decisions/0002-retail-cleaning-
  defaults.md` line 56, independently confirmed above), not a new policy this
  feature invents. Applying an existing default to a new table is exactly
  Principle VI's designed behavior, and the genuine judgment call this table's own
  build will face (grain, PK, exact column names) is explicitly left to "a
  Mapping-Ready Stage-2 judgment made during this example's own build" (spec.md Key
  Entities) -- not fixed in this spec/plan. This is not a hidden self-grant.
- The exchange-handling Default-adopted resolution (Clarification Q3) is narrowly
  scoped to SCOPE only ("out of scope for this instance if no exchange row
  exists"), and the spec/tasks are explicit that this is distinct from answering
  the underlying return-vs-netted policy question, which remains genuinely OPEN
  regardless of whether a source exchange case is later found. This is the correct
  disposition (decline to fabricate a scenario is a safe default; it does not
  resolve the policy), not a disguised ruling.

Verdict: **PASS**. No hidden self-grant of an approval or a business-policy
judgment call; every genuine Principle-V question (VAT, date axis, exchange
policy, cross-star conformance, named-human approvals) is correctly routed to
OPEN/empty rather than answered, and the one place a "default" is applied (RC8)
is an already-ratified kit-wide default, not a new invented policy.

## Axis 2 -- assumes-deferred-capability

Probe: does any artifact assume F016, a live DB, or a running adapter exists?

- FR-009/T016/T022/T025/T026 all explicitly require `blocked` (never `pass`) with
  a named `blocking_reasons[]` entry for every live-gated check (Gold Ready's live
  PK/grain/orphan-FK/penny-exact reconciliation; any live semantic-model
  connection) when no live DB or F016 is available -- and research.md Sec 4 and
  quickstart.md both name F016 and live-DB non-availability explicitly as a
  precondition of the whole design, not an afterthought.
- T019 explicitly states the governed TMDL model is "NOT opened in Power BI
  Desktop, NOT connected live -- authored and statically checkable only (F016
  deferred)." No task anywhere invokes `retail validate` (the live-DB command), no
  task opens Power BI Desktop, and no task assumes a DSN/host is reachable.
  T014/T015 (SQL migrations) are explicitly "authored," never "applied" or
  "executed" -- the plan's own Technical Context reiterates the migrations are
  Stage 3-4 SQL TEXT, matching the same dialect as the shipped spine, not a
  connection.
- T028's `retail check` run is the one genuinely-executed command this feature's
  Polish phase requires, and it is a static, stdlib-only, no-DB-connection gate
  (confirmed by this repo's own architecture; every other reviewed sibling feature
  in this batch makes the identical claim about the same gate) -- it is not a
  disguised live-DB assumption.
- One place worth tracing explicitly: T029 asks a human/agent to perform a "manual
  composition-legality review against the AD1 legality table" because AD1's
  automated corpus glob does not reach `mappings/*/metrics/*.yaml` (confirmed
  above). This is not an assumption that a deferred CAPABILITY exists -- it is an
  honest acknowledgment that the automated gate is vacuous here and a human
  judgment substitutes for it, which is the correct disclosure rather than a
  silent gap.

Verdict: **PASS**. No deferred capability (F016, live DB, running adapter) is
assumed reachable anywhere; every live-gated stage is explicitly designed to
report `blocked`, and the one automated-check gap (AD1's glob) is disclosed and
compensated with an explicit manual-review task rather than silently assumed away.

## Axis 3 -- c086-leak

Probe: does any template/label bake in domain-specific values instead of staying
generic (Principle VII)?

- data-model.md Sec 3/4's two contract shapes use exclusively placeholder tokens
  (`<returns_fact_or_view>`, `<return_value_column>`, `<net_sales_column>`, `<named
  metric owner>`) -- no filled client fact, billing code, or C086-archived specific
  appears in either shape sketch.
- FR-014/SC-007 explicitly forbid any C086/client-specific token anywhere in this
  feature's artifacts, and T031 is a dedicated grep-verification task (Polish
  phase) scoped to exactly the new file set (`mappings/<rr>/`,
  `docs/worked-examples/<rr>.md`) checking for C086/client-specific tokens outside
  a clearly-marked citation to `skills/retail-kpi-knowledge/*`.
- The synthetic dataset itself (T005) is explicitly required to be
  "hand-authored GENERIC," with the row shapes (data-model.md Sec 6) described only
  as abstract categories (normal sale / same-period return / cross-period return /
  discrepancy row), not concrete client-identifiable values -- the spec's own
  Assumptions and FR-014 repeatedly anchor this as a hard requirement, not a
  suggestion.
- The one place real names DO appear (correctly) is citation: `retail_store_sales`,
  `demo_sample_orders`, `RC8`, and specific file paths are named throughout
  spec.md/plan.md/tasks.md purely to establish BOUNDARIES (what this feature must
  NOT touch or reuse) -- this is the sanctioned citation-vs-inlining pattern this
  repo's other reviewed siblings (087, 094, 095) also use correctly, not a leak
  into a generic template surface.
- T032/FR-015 additionally require ASCII/UTF-8-without-BOM for all new artifacts,
  which is a related but distinct genericity/reproducibility discipline (no
  glyphs), also independently verified as a Polish-phase task, not merely asserted.

Verdict: **PASS**. Every contract/template shape sketched in the plan stays
placeholder-only; the two new metric contracts and the synthetic dataset are
required to be generic by FR-014/SC-007, backed by a dedicated grep task; real
names appear only as citations establishing scope boundaries, the correct pattern.

## Axis 4 -- fabricated-confidence

Probe: does any artifact emit a numeric score/health/maturity/completeness count?

- FR-011/SC-005 state the prohibition explicitly and repeatedly: no numeric
  confidence/health/maturity score and no "N of M"/percentage completeness tally
  anywhere in this feature's artifacts. T006 seeds `readiness-status.yaml` with
  the four-status vocabulary only (`not_started`/`blocked`/`warning`/`pass`) plus
  `evidence[]`/`blocking_reasons[]`/`approvals[]` -- no numeric field. T026/T030
  are dedicated, independently-run grep/inspection tasks (Polish and US3 phases
  respectively) scanning every new file for `score`, `confidence`, `health`,
  `maturity`, and N-of-M/percentage patterns, not merely a docstring promise.
- The one place this feature DOES produce numbers is the worked reconciliation
  figures (FR-007/SC-003/T020): a P1/P2 period-total arithmetic example and a
  gross-minus-returns-equals-net figure, both sourced from the committed synthetic
  dataset. This is categorically distinct from a hard-rule-#9 violation: these are
  EVIDENCE figures (concrete transaction amounts proving a reconciliation
  property holds), not a confidence/health/maturity SCORE or a completeness
  percentage. `readiness-status.yaml`'s own `evidence[]` field is explicitly
  designed to hold exactly this kind of cited factual evidence (matching
  `retail_store_sales`'s own shipped precedent, which cites transaction counts and
  dollar reconciliation figures in its evidence lines without those counting as
  "scores"). No task blurs this distinction by attaching a percentage or
  confidence label to either worked figure.
- `templates/metric-contract.yaml`'s `readiness.status` field is the same
  categorical (non-numeric) vocabulary every other reviewed sibling feature in
  this repo uses; this feature introduces no new field and no new severity/score
  tier.

Verdict: **PASS**. No numeric confidence/health/maturity score or completeness
tally is designed anywhere; the worked reconciliation figures the feature DOES
require are evidentiary transaction arithmetic, not a score, and two independent
Polish/US3-phase tasks mechanically scan for the forbidden patterns rather than
relying on review discipline alone.

## Axis 5 -- over-scope

Probe: does the plan do more than its one readiness-stage job, or cross into
another feature's territory?

- The Boundary section (spec.md) and the tasks.md Scope-guard section both name
  four specific neighbours (`retail-store-sales.md`/`mappings/retail_store_sales/`,
  spec 084, spec 068/AD1, spec 087/HR1) and state precisely what this feature must
  NOT do to each -- and T033 is a dedicated `git diff` boundary-scan task
  confirming zero modification to any of those paths. This is a stronger
  discipline than a prose promise: it is a mechanically-checked boundary.
- FR-002/tasks.md repeatedly and explicitly refuse three plausible scope-expansion
  paths rather than merely omitting them: (a) no new `retail check` rule file
  under `src/retail/rules/`; (b) no new RC default entry in
  `docs/decisions/0002-retail-cleaning-defaults.md`; (c) no new readiness-stage key
  in `docs/readiness/readiness-model.md`. T028 confirms the rule count stays
  UNCHANGED after this feature lands, which is a mechanical, not merely asserted,
  verification.
- FR-012 explicitly declines to resolve the cross-star conformed-dimension
  question even though this feature's own dimensions may collide by name with
  `retail_store_sales`'s or `demo_sample_orders`'s -- it notes the question in
  prose and explicitly never authors/edits `docs/quality/conformed-dimension-
  map.yaml` (confirmed not to exist on disk), which is spec 087/HR1's declared
  human-judgment mechanism, not a worked-example authoring step.
- One footprint precision worth surfacing (not a violation): plan.md's Summary and
  spec.md's Overview both frame this feature's scope as "Stages 2-6," but T023/T024
  (Phase 5/US3) author `design/` AND `handoff/` -- the Dashboard Ready (Stage 6)
  AND Publish Ready (Stage 7) artifact sets respectively, per spec 084's own
  Tier-1 completeness contract (sections F and G), which FR-016 requires this
  feature to satisfy in full. Tracing this: authoring the `handoff/` pack is
  REQUIRED compliance with the completeness contract this feature explicitly binds
  itself to (FR-016), not scope creep -- the 084 contract's own Tier-1 bar spans
  through Publish Ready's PACK artifacts (approval itself is Tier 2, deferred).
  The mismatch is that the "Stages 2-6" framing in the Overview/plan Summary
  undersells the actual artifact footprint by one stage's worth of pack content,
  the same imprecision family as analysis.md's F1 (stage-range/name mismatch), not
  a second, unrelated over-scope defect. It does not flip this axis to RISK: the
  extra artifact is licensed by the feature's own binding completeness-contract
  citation, not an unlicensed expansion.
- No task anywhere authors `src/retail/rules/additivity_consistency.py`, connects
  to a live database, opens Power BI Desktop, or writes to
  `docs/quality/conformed-dimension-map.yaml` -- all four of the collision-
  avoidance allocation's named prohibitions are independently upheld by task
  design, not merely stated as intent.

Verdict: **PASS**. Scope stays inside the sanctioned worked-example allocation;
the plan mechanically checks its own boundary (T033's `git diff` scan, T028's
rule-count check) rather than relying on prose discipline alone. The one
footprint-precision gap found (the "Stages 2-6" label undercounting the
Publish-Ready pack artifacts FR-016 itself requires) is the same label-precision
family as F1, not a genuine scope violation, and is carried forward as a
non-blocking note.

## Notes / carry-forward (non-blocking)

- **F1 (from analysis.md, independently re-confirmed here)**: spec.md FR-002
  (line ~263) and plan.md's Summary both read "Stages 2 through 6 ... Mapping
  Ready through Semantic Model Ready." Per `docs/readiness/readiness-model.md`
  lines 33-39 (independently verified above), Stage 5 is Semantic Model Ready and
  Stage 6 is Dashboard Ready -- the numeric range is correct, the trailing stage
  NAME is off by one. Recommend a one-line fix in both locations
  ("Mapping Ready through Dashboard Ready") before/during implementation; no task
  or FR needs renumbering since the underlying artifact scope (design artifacts
  through Dashboard Ready, per T023) is already correct.
- **F2 (from analysis.md, independently re-confirmed here)**: research.md Sec 2
  row 4 and Sec 5 both state spec 087 "is spec-only (spec.md plus research.md
  only, no plan/tasks/contracts)." Independently confirmed stale: 087's directory
  now also contains plan.md, tasks.md, data-model.md, quickstart.md, and
  plan-review.md. The load-bearing conclusion this feature's FR-012 design
  actually depends on -- that HR1's rule is absent from `src/retail/rules/` and
  `docs/quality/conformed-dimension-map.yaml` does not exist on disk -- was
  independently re-verified true in this review (zero `HR1` matches under `src/`,
  the map file absent). FR-012's design (note the question in prose, never author
  the map file) is not broken; only research.md's supporting citation about 087's
  own spec-kit paperwork stage is stale and should be corrected to describe the
  operative fact (rule/file absence) rather than a specific spec-kit stage for a
  sibling feature this feature does not own.
- **F3 (from analysis.md, independently re-confirmed here)**: SC-002 names
  `retail check`'s AD1 rule as the test for "zero new ERROR findings," but AD1's
  `_CORPUS_RE` (confirmed above) never reads `mappings/*/metrics/*.yaml` -- the
  automated check is vacuously satisfied regardless of the two new contracts'
  actual composition legality. T029 correctly substitutes a manual
  composition-legality review, but SC-002's own wording does not disclose that the
  automated half of its claim is vacuous. Recommend rewording SC-002 to state the
  zero-new-ERROR guarantee holds by construction (AD1 does not read this path) and
  that the substantive check is T029's manual review.
- **Footprint-precision gap (Axis 5 detail, new in this review, same family as
  F1)**: the "Stages 2-6" scope framing in spec.md's Overview and plan.md's
  Summary undercounts the actual required artifact set once FR-016's binding
  citation to spec 084's completeness contract is traced through -- T023/T024
  author Dashboard Ready (Stage 6) design artifacts AND Publish Ready (Stage 7)
  handoff-pack artifacts, both required by the completeness contract's Tier-1
  sections F/G. This is licensed, required compliance (not scope creep), but the
  "Stages 2-6" language should be read as "artifacts through Stage 6, plus the
  Stage-7 pack content the completeness contract requires, with Stage-7 APPROVAL
  itself out of scope" -- worth a one-line clarification alongside the F1 fix
  since both are the same kind of stage-label imprecision.
- **Minor precision note (new in this review, not in analysis.md, non-blocking)**:
  FR-003 and research.md Sec 3 state the committed synthetic dataset will be "in
  the same posture `retail_store_sales` used for its own source." Independently
  checked: `mappings/retail_store_sales/` holds no raw data file -- its
  `source-profile.md` documents an external Kaggle CSV export that is not
  committed under that directory. This feature's posture (committing the actual
  dataset file under `mappings/<rr>/`) is arguably a STRONGER reproducibility
  posture than `retail_store_sales`'s own precedent, not a weaker or mismatched
  one -- but the "same posture" phrasing is not literally accurate. This does not
  block anything (a hand-authored generic dataset committed to the repo is squarely
  within Principle IX/FR-003's actual intent) and is flagged only for wording
  precision, not correctness of the underlying plan.
- **AD1 legality is a build-time manual review, not a mechanical gate (re-surfaced
  from Axis 2/F3 for visibility)**: T029's manual composition-legality review
  against the AD1 legality table is real, necessary work given the automated
  gate's blind spot, but it depends entirely on the good-faith rigor of whoever
  executes T029 at build time -- no task mechanically re-derives the legality
  table's rules and checks the two new contracts' YAML against them
  programmatically. This is not a plan defect (no such mechanical check exists
  anywhere else in this repo for contracts outside AD1's corpus glob either), but
  it is worth the implementer's attention that "zero new AD1 ERROR findings" as
  literally measured by `retail check` will be true regardless of build-time care,
  so SC-002's real teeth come entirely from T029's manual diligence.

## Verdict

**Verdict**: PASS-WITH-NOTES

All five axes clear on direct ground-truth verification against the live
worktree, not merely on the plan's or analysis.md's self-report: the
readiness-model stage names, AD1's `_CORPUS_RE` glob, RC8's exact shipped text,
087/HR1's real on-disk absence (despite its paperwork having advanced), the
084 completeness contract's real existence, and `retail_store_sales`'s actual
committed artifact set were all independently re-confirmed rather than assumed
correct. Every genuine Principle-V judgment call (VAT/tax treatment, the
operative reporting date axis, cross-star conformed-dimension declaration,
named-human approvals) is correctly left OPEN/empty, never silently resolved;
no deferred capability (F016, live DB) is assumed reachable anywhere; every
contract/template shape stays generic with a dedicated grep-verification task;
no numeric confidence/health/maturity/completeness score is proposed anywhere,
and the feature's own worked reconciliation figures are correctly evidentiary
arithmetic, not a score; and scope stays inside the sanctioned allocation with
two mechanical boundary checks (T028's rule-count check, T033's `git diff`
scan). No CRITICAL or HIGH finding; no axis is RISK or FAIL. The carry-forward
notes are non-blocking: analysis.md's own F1 (Stage-6 mislabel) and F2 (stale
087-paperwork-stage citation, operative conclusion still correct) and F3
(SC-002's automated-check-is-vacuous wording) are all independently
re-confirmed here; a new same-family footprint-precision note observes that the
"Stages 2-6" framing undercounts the Publish-Ready pack artifacts FR-016's own
completeness-contract citation requires (licensed compliance, not scope creep);
and two minor wording-precision notes (the "same posture as retail_store_sales"
claim; T029's manual-review dependency) round out the non-blocking list.
