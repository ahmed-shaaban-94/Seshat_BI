# Adversarial Plan-Review: Date-Spine Completeness Static Gate (HR8)

**Feature**: `094-date-spine-completeness` | **Date**: 2026-07-04
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports findings,
edits nothing). Artifacts reviewed: spec.md, plan.md, tasks.md, plus research.md,
data-model.md, quickstart.md (present in the feature directory).

**Precondition check**: spec.md, plan.md, tasks.md are present. **`analysis.md`
does NOT exist in this feature directory** -- `speckit-analyze` has not been run
for 094, so there is no cross-artifact analyze verdict to cite. This is recorded
as a non-blocking N-note, not a BLOCKED precondition (matching the 087/HR1
precedent for the same absence): this review substitutes direct ground-truth
verification against the live worktree in its place.

**Ground truth verified directly against the worktree** (not merely the plan's
self-report):

- Live rule count is **55** in **21** families
  (`docs/quality/rule-count-claims.yaml` `claimed-count: 55`;
  `docs/rules/rules-manifest.json` has 55 entries; `docs/glossary.md`'s anchor
  reads "Currently 55 rules in 21 families") -- matches spec/plan/tasks' stated
  baseline exactly.
- No `"HR1"` or `"HR8"` string and no `"HR` family-letter row exist anywhere in
  `src/`, `docs/`, or `tests/` -- 087/HR1 has NOT landed yet in this worktree,
  confirming HR8's reserved id and the "HR" family-letter slot are both
  genuinely free as of this review, and confirming plan.md's own
  Parallel-landing serialization warning is live, not hypothetical.
- `s7_contiguous_date_dim` (`src/retail/rules/sql.py:503-544`) verified to do
  exactly what the spec's Boundary section claims: it checks
  `has_distinct and not has_genseries` only -- it never inspects
  `generate_series`'s own arguments. HR8's target gap is real, not invented.
- `tokenize_sql` (`src/retail/sql.py:81-87`) docstring confirms it "collapse[s]
  \[string literals\] to an empty-text placeholder token"; `strip_sql_comments`
  (`src/retail/sql.py:135-143`) docstring confirms it "keeps `'...'` literals
  ... intact." The Clarifications' Q1 default (two utilities for two sub-steps)
  is verified correct against the actual source, not asserted on faith.
- The shipped worked-example migration
  (`warehouse/migrations/0004_create_gold_retail_store_sales_star.sql:107`)
  verified to read exactly
  `generate_series(DATE '2022-01-01', DATE '2025-01-18', INTERVAL '1 day')` --
  daily step, chronological literal bounds. SC-001's "stays green" claim is
  checked against the real byte content, not a paraphrase.
- Both alternate date-literal spellings the Clarifications' Q2 default names
  are independently confirmed live in the tree: `'...'::date` at
  `0003_create_silver_retail_store_sales.sql:58` and
  `order_date::date` at `0005_create_silver_demo_sample_orders.sql:39`.
- **`Severity.INFO` genuinely exists** (`src/retail/core.py:18-21`:
  `ERROR = "error"  # fails the build (non-zero exit)`;
  `WARNING = "warning"  # reported, does NOT fail the build`;
  `INFO = "info"  # informational only`) and is already emitted by one shipped
  rule (`src/retail/rules/git_meta.py:168`) -- FR-007 does not invent a new
  severity tier.
- **The gate's exit-code aggregation keys strictly on `Severity.ERROR`**
  (`src/retail/cli.py:713` and `:995`: `if any(f.severity is Severity.ERROR for
  f in findings):`). This is the load-bearing fact for SC-001: FR-007's INFO
  record fires on EVERY clean `generate_series` call, including the shipped
  migration's -- but because INFO never participates in the exit-code check,
  the shipped tree's `retail check` exit code stays 0 even after HR8 lands.
  SC-001's careful wording ("ZERO HR8 ERROR findings", not "zero findings") is
  exactly right and matches the actual gate mechanics, not just a hopeful
  paraphrase.

## Axis 1 -- hidden-principle-violation

Probe: does HR8 secretly self-grant an approval, decide a Principle-V judgment
call, or advise-instead-of-block?

- The core mechanism is read-only and fail-closed by construction: HR8 reads
  only committed migration text, emits `Finding` objects, and never writes a
  migration, a `source-map.yaml` key, or a readiness-status entry anywhere
  (FR-009, verified: no such write exists in the described design). No
  approval, `approvals[]` entry, or readiness-stage transition is recorded by
  a clean HR8 run.
- **The load-bearing question an adversarial reviewer must not wave past**:
  spec.md's entire Principle-V defense for hard-fixing the grain at daily
  rests on the claim that "every shipped date-dimension surface in this repo
  already presupposes a one-row-per-day calendar" (Assumptions), so enforcing
  it is "not a new business rule." Traced against the actual cited evidence:
  `docs/readiness/gold-ready.md:27` names S7's contribution as "date dim built
  via `generate_series` (contiguous)" -- it says **contiguous**, not
  **daily**; the doc itself never states a daily grain requirement in those
  words. S7's code (verified above) checks builder choice only, never the
  step. The strongest DIRECT evidence for "daily is already settled" is
  narrower than the spec's blanket phrasing: (a) the one shipped worked
  example happens to use `INTERVAL '1 day'`, and (b) V-RC15's live coverage
  check would only pass against a daily-stepped calendar if the fact table's
  own transaction dates are daily-grained (which they are, by the same
  worked example) -- neither is a repo-wide declared policy statement that a
  non-daily-grain date dimension is forbidden. HR8 is the FIRST artifact in
  this repo to elevate "daily step" from an incidental worked-example fact
  into a hard, fail-closed, repo-wide gate that ERRORs any weekly/monthly
  reporting-mart date dimension a future table might legitimately need. This
  is a genuine (if narrow) new business rule being minted, not merely an
  existing rule being enforced -- the spec's own "no Principle-V ruling is
  needed" argument is weaker than stated, because the premise (daily grain is
  already a declared, repo-wide convention) is not fully supported by the two
  citations available to check it against.
  - Mitigating factors, weighed honestly: the spec explicitly flags this
    exact tension itself (Clarifications: "The two candidate ambiguities
    considered ... both resolve against already-settled repo conventions ...
    If a future reviewer disagrees that either is fully settled, it should be
    raised at `/speckit-clarify` time rather than defaulted here") -- so this
    is not a silent, undisclosed self-grant; the spec pre-registers the
    disagreement path. The Assumptions section also explicitly scopes a
    future non-daily-grain date dimension as "OUT OF SCOPE (YAGNI) and would
    need its own future spec, not a widening of HR8" -- meaning HR8 does not
    itself forbid ever building a non-daily calendar, it just fails a
    migration that does so TODAY without that future spec's ruling. That is
    a materially softer claim than "daily grain is a settled fact," and the
    plan should say so.
  - Net effect: HR8's fail-closed behavior is technically sound engineering
    (every shipped instance today IS daily; catching a divergence early is
    valuable), but the CONSTITUTIONAL framing overstates how settled the
    convention is. This is a real, if narrow, judgment call about future
    reporting-mart shapes being pre-empted by a static rule, not a pure
    convention-enforcement action.
- No other Principle-V question (grain of an actual table, PII, business
  rollup, product identity) is answered anywhere in this feature; the daily-
  step question above is the only place the "convention vs. new rule"
  boundary is genuinely thin.

Verdict: **RISK**. The mechanism is read-only, fail-closed, and self-grants
nothing (the general shape is correct). But the spec's justification for
skipping a Principle-V ruling on "daily grain" leans on a "settled convention"
claim that is thinner than stated once traced against the actual cited
evidence (`gold-ready.md` says "contiguous," not "daily"; S7 never checks
step). This is not a fabricated citation and the spec explicitly invites a
future reviewer to challenge it -- but as the adversarial reviewer taking that
invitation up, the honest reading is that HR8 is minting a new, narrow,
fail-closed business rule about calendar grain, not purely enforcing an
already-declared one. Recommend the plan soften the "already-settled, no
Principle-V ruling needed" language to something like "the only shipped
instance is daily; HR8 fixes daily as the enforced default per Principle VI
(Defaults-Then-Deviations), and a future non-daily reporting mart would need
its own spec to carry a deviation" -- which is the true and still-safe shape
of the claim, without overclaiming existing repo-wide consensus that the
citations do not fully support. This does not block the design (the behavior
itself is defensible under Principle VI as a default), but the framing should
be corrected before or during ratification.

## Axis 2 -- assumes-deferred-capability

Probe: does any artifact assume F016, a live DB, or a running adapter exists?

- HR8 is 100% static: it reads only `ctx.tracked_files` / `iter_sql_files(ctx)`
  content (already the S1-S8 universe), opens no database connection, and
  invokes no execution adapter (FR-001, FR-006; verified no `validate.py`
  import is described anywhere in plan.md's file footprint).
- F016 (Power BI execution adapter) is never invoked or assumed; no Power
  BI/PBIP surface is read.
- Live row-level coverage is explicitly and repeatedly named as OUT of scope
  and deferred to `V-RC15`/`retail validate` (FR-006, FR-007, Boundary
  section, Assumptions) -- the FR-007 INFO record is the correct Principle
  VIII posture (author static structure, mark live PENDING) rather than
  silently assuming a live surface will eventually run.
- **The `Severity.INFO` mechanism itself is verified to actually exist and
  actually be non-blocking** (see Ground truth above) -- this is not a case
  of the spec assuming an unshipped severity tier or an unverified gate
  behavior; both are checked live in `core.py` and `cli.py`.
- One precision correction to the plan's own citation: plan.md's Project
  Structure note justifies the `["error", "info"]` severity-posture entry by
  analogy to "the existing 'S4b' precedent" (a rule that "also emits two
  severities"). Verified: S4b emits `Severity.ERROR` AND `Severity.WARNING`
  (`severity_posture.py:104-106`), not ERROR+INFO. S4b is valid precedent for
  "a rule can emit two severity classes from one registered id" (the general
  multi-class mechanism HR8 needs), but it is NOT precedent for INFO
  specifically being an accepted static-rule output class -- that precedent is
  `git_meta.py`'s existing (different, unrelated) rule, which the plan does
  not cite. This is a citation-precision gap, not a capability gap (INFO does
  exist and does work as intended), so it does not change this axis's PASS,
  but the plan/tasks should cite the correct precedent for the specific claim
  being made.

Verdict: **PASS**. No deferred capability (F016, live DB, running adapter) is
assumed anywhere; the one severity-mechanism claim that could have been an
unverified assumption (`Severity.INFO` working as a non-blocking gate output)
is independently confirmed against `core.py` and `cli.py`. The S4b-as-INFO-
precedent citation is imprecise but does not point to an actual capability gap.

## Axis 3 -- c086-leak

Probe: does any template/label bake in domain-specific values instead of
staying generic (Principle VII)?

- HR8's matching logic keys only on the existing generic `dim_date`-prefix
  convention S7 already relies on (FR-002, FR-014) -- no table/column name
  (`retail_store_sales`, `demo_sample_orders`, `dim_date_rss`) is required in
  the rule's matching or classification code for it to fire correctly on an
  arbitrary `warehouse/migrations/*.sql` path (FR-014; SC-007).
  `gold.dim_date_rss` (the shipped migration's actual dim name) still matches
  the generic "starts with `dim_date`" test S7 already uses -- verified this
  is the same precondition, not a new hardcoded name.
- The real worked-example names (`retail_store_sales`, `0004_create_gold_...`)
  appear only where the spec/plan CITE the actual committed file for
  mutation-verification purposes (SC-001, US1 Acceptance Scenario 3) -- the
  correct citation-vs-inlining distinction the 087/059 reviews both applied.
  T035 is a dedicated grep task confirming no domain-specific identifier
  leaks into the rule's matching logic or fixtures as a REQUIRED literal.
- No new manifest/template file is introduced at all (FR-010) -- there is no
  new authoring-comment surface (unlike 087/HR1's `conformed-dimension-map.yaml`
  scaffold) where a copy-pasted real name could leak into a committed
  template. This shrinks the leak surface relative to the 087 precedent, not
  merely holds it steady.

Verdict: **PASS**. No c086/worked-example specifics are baked into the rule's
matching logic; the only real names present are citations of the actual
committed migration for verification purposes, and the feature introduces no
new template file where a leak could occur.

## Axis 4 -- fabricated-confidence

Probe: does any artifact emit a numeric score/health/maturity/completeness
count?

- HR8's `Finding` objects reuse the existing, unchanged `Finding` dataclass
  (`rule_id`/`severity`/`message`/`locator`) -- no new numeric field is
  introduced anywhere (FR-008; data-model.md "HR8 Finding").
- FR-007 and FR-008 explicitly forbid coverage-proof language ("covers",
  "complete", "gap-free") in the INFO record and explicitly forbid any
  numeric confidence/health/maturity/completeness score or "N of M" / "%
  covered" tally -- and this is backed by TWO dedicated mechanical
  verification tasks, not just a docstring promise: T027 (text-content
  assertion scanning every HR8 INFO message for the forbidden substrings)
  and T034 (source-inspection test asserting no percentage/ratio/"N of M"
  formatting appears in any emitted message string, plus no DB-connection
  call, no `validate.py` import). This mirrors 087/HR1's T043/T044 mechanical-
  verification posture, which the 087 review specifically credited as
  "a stronger verification posture than a docstring promise."
  This feature has BOTH the message-content check (T027) AND the source-
  inspection check (T034), matching but not exceeding the 087 precedent.
- The one integer touched by this feature -- the rule count (55 -> 56, per
  `EXPECTED_RULE_IDS`/`docs/rules/rules-manifest.json`) -- is not a
  conformance/confidence score; it is the same `len()`-based mechanism SC2
  already reconciles, verified live at 55 before this feature lands, and
  plan.md explicitly hedges "re-verify the live count and family list against
  the actual committed files at implement time rather than trusting the
  numbers above" given the 19-parallel-feature landing race. This is the
  correct non-fabrication posture for a count that is genuinely volatile at
  authoring time.
- No maturity/health label anywhere; Findings remain categorical
  (ERROR/INFO) only.

Verdict: **PASS**. No fabricated or invented number anywhere; the rule-count
integer is an authoritative, explicitly re-verify-at-implement-time `len()`,
not a score; the no-coverage-proof-language and no-numeric-score guarantees
are each backed by a dedicated mechanical test, not just review discipline.

## Axis 5 -- over-scope

Probe: does the plan do more than its one readiness-stage job, or cross into
another feature's territory?

- Deliverables are unusually tight even by this repo's rule-adding precedent:
  ONE new `@register`ed function added inside an ALREADY-EXISTING module
  (`src/retail/rules/sql.py`), NO new rule module, NO new manifest/declaration
  file, NO new `source-map.yaml` key, NO new readiness stage. This is
  explicitly lighter-footprint than 087/HR1 (which added a new module AND a
  new manifest file) -- the plan states this comparison itself and it checks
  out against the file footprint described.
- The plan explicitly and repeatedly refuses to touch S7's or V-RC15's body,
  severity, or message text (FR-010; Boundary section) even though a
  shared-helper refactor touching S7 might have felt tidier -- T015/T016
  deliberately RE-DERIVE the statement-discovery span independently rather
  than factoring a shared helper that would edit `s7_contiguous_date_dim`.
  This is a genuine scope-discipline choice (accepting minor duplication to
  avoid touching a sibling rule's surface), consistent with FR-010's
  no-shared-schema-addition collision-avoidance allocation.
- It does not attempt live row-level coverage (V-RC15's job, explicitly
  deferred per FR-006) even though "just also check the live span" might
  have felt like a natural extension once the static structure exists --
  the spec/plan hold this line consistently across every artifact (Overview,
  Boundary, Assumptions, FR-006, US3).
- It does not touch 087/HR1's cross-star conformed-dimension territory; the
  spec's own Boundary section explicitly distinguishes HR8 (per-star,
  single-migration, step/bounds) from HR1 (cross-star, multi-fact,
  grain/key/type agreement) and states neither rule inspects the other's
  subject matter. Verified: 087/HR1 has not landed yet in this worktree, so
  this boundary claim cannot yet be checked against HR1's actual committed
  code, but the textual boundary described is coherent and non-overlapping
  on its face.
- The one place scope arguably nudges outward is the Axis-1 daily-grain
  question above: by hard-failing any non-daily step, HR8 is implicitly
  taking a small policy stance on what calendar shapes this repo will ever
  accept at Gold Ready, which is one increment more prescriptive than "a
  pure mechanical structure check" might suggest. This is the same tension
  as Axis 1, not a separate over-scope defect -- recorded here for
  completeness, not as an additional blocking finding.

Verdict: **PASS**. Scope is disciplined and, notably, the lightest-footprint
rule-adding feature reviewed in this batch (no new module, no new manifest
file, no shared-schema addition) -- it declines predictable scope-creep paths
(a shared S7 helper touching S7's body, live coverage, cross-star
conformance) rather than merely avoiding them by omission.

## Notes / carry-forward (non-blocking)

- **`analysis.md` is absent for this feature.** `speckit-analyze` has not been
  run. This review substituted direct ground-truth verification (rule count,
  manifest/glossary anchor text, S7 code inspection, `Severity.INFO`
  existence, CLI exit-code gate logic, the shipped migration's literal text,
  both date-literal spellings) for the missing cross-artifact analyze pass.
  Recommend running `speckit-analyze` before or during implementation.
- **Soften the "already-settled convention" framing for daily grain (Axis 1
  detail).** `docs/readiness/gold-ready.md` says "contiguous," not "daily,"
  and S7 never inspects step. The honest framing is "the one shipped instance
  is daily; HR8 fixes daily as the Principle-VI DEFAULT," not "every shipped
  surface already presupposes daily grain, so no default is even being set."
  This does not block the design -- Defaults-Then-Deviations explicitly
  permits fixing a default without a Principle-V ruling -- but the spec's
  Clarifications and Assumptions prose should be adjusted to the narrower,
  fully-supportable claim before ratification, since it is the one place this
  feature's Principle-V-avoidance argument is thinner than stated.
- **Cite the correct severity precedent.** Plan.md's Project Structure note
  cites "S4b" as precedent for the `["error", "info"]` two-severity shape.
  S4b emits ERROR+WARNING, not ERROR+INFO; the actually-relevant precedent for
  "a static rule may emit INFO and it does not block the gate" is
  `git_meta.py`'s existing INFO-emitting rule (verified: `Severity.INFO` used
  at `src/retail/rules/git_meta.py:168`), not S4b. Recommend correcting the
  citation in plan.md/tasks.md (T007's comment) before/during implementation;
  this is a documentation-precision item, not a capability gap, since INFO
  genuinely exists and is genuinely non-blocking (independently verified
  against `core.py` and `cli.py` in this review).
- **Real-tree bite is currently prospective for the ERROR paths, active for
  the INFO path.** Only one migration in this tree
  (`0004_create_gold_retail_store_sales_star.sql`) has a `dim_date
  generate_series` build, and it already passes both the step and
  bounds-order checks cleanly. HR8's two ERROR-producing checks (US1, US2)
  are therefore fixture-proven, not yet real-tree-active, against today's
  committed tree (matching 087/HR1's own "prospective enforcement" note) --
  but the FR-007 INFO record WILL fire against the real, committed 0004
  migration the moment HR8 lands (verified: its `generate_series` call is
  daily-step with chronological literal bounds, so it clears both checks and
  gets the INFO marker), so this feature's non-ERROR output is immediately
  live against real content, unlike a rule whose only fixture is synthetic.
- **SC-001's precise wording is load-bearing and correctly chosen.** "Zero
  HR8 ERROR findings" (not "zero findings") is exactly right given FR-007
  fires an INFO on every clean call including 0004's -- confirmed the CLI's
  exit-code gate keys strictly on `Severity.ERROR`
  (`src/retail/cli.py:713`, `:995`), so this wording is not just careful
  writing, it is the correct description of what actually keeps the gate
  green. Implementers should preserve this exact distinction in test
  assertions (T013 already does: "assert ZERO HR8 ERROR findings," separate
  from T026's later "assert exactly one Severity.INFO record").
- **The rule-count/family-letter claim is a live serialization point**,
  correctly hedged by plan.md/tasks.md (T002) given 087/HR1 is an in-flight
  sibling also claiming the "HR" family letter. Verified free (55/21, no "HR"
  anywhere) as of this review; no action needed beyond honoring the plan's
  own re-verify-at-implement-time instruction.

## Verdict

**Verdict**: PASS-WITH-NOTES

Four of five axes clear cleanly on direct ground-truth verification (not
merely the plan's self-report): the mechanism is static-only, fail-closed,
self-grants nothing structural, stays generic, fabricates no score, and is the
lightest-footprint rule-adding feature in this review batch (no new module, no
new manifest file). Axis 1 is marked RISK rather than PASS because the spec's
"daily grain is an already-settled repo-wide convention, so no Principle-V
ruling is needed" argument, when traced against its own cited evidence
(`gold-ready.md` says "contiguous" not "daily"; S7 never checks step), is
thinner than stated -- HR8 is the first artifact to hard-fail a non-daily
calendar, which is a narrow but real new fail-closed policy, best justified
under Principle VI (fixing a default from the one shipped instance) rather
than as pure enforcement of an already-declared, repo-wide rule. This does not
block the design's behavior (which is sound engineering and stays inside
Defaults-Then-Deviations) but the framing should be corrected before
ratification. Non-blocking carry-forwards: the missing `analysis.md`, a
citation-precision fix (S4b is not INFO precedent; `git_meta.py` is), and the
note that HR8's ERROR paths are currently fixture-proven against this tree
while its INFO path is immediately real-tree-active. No CRITICAL or FAIL
finding on any axis.
