# Adversarial Plan-Review: Readiness Decay -- Drift Raises a Stale-Pass Demotion Blocker (HR3)

**Feature**: `089-readiness-decay-demotion` | **Date**: 2026-07-04
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports findings, edits
nothing). Artifacts reviewed: spec.md, plan.md, tasks.md, analysis.md, research.md,
data-model.md.

**Precondition check**: spec.md, plan.md, tasks.md, and analysis.md are all present --
unlike the 087 review (no `analysis.md` existed for that feature at review time), this
chain already has a clean `speckit-analyze` verdict (`scope_ok = true`, no FR/SC gap, no
constitution violation, two LOW-severity informational notes). That precondition is
satisfied, but this review does not lean on analysis.md's verdict as a substitute for its
own verification -- every load-bearing factual claim below was independently re-checked
against the live worktree rather than trusted at face value, precisely because
analysis.md is glowing enough that rubber-stamping it would be the easy failure mode here.

**Ground truth verified directly against the worktree** (not merely the plan's or
analysis.md's self-report):

- Live rule count is **55** (`grep -c '"id"' docs/rules/rules-manifest.json` = 55;
  `docs/quality/rule-count-claims.yaml` `claimed-count: 55`) -- matches plan.md's claim.
- `src/retail/rules/` contains **no** `rule_hr1.py` or `rule_hr3.py` file today -- HR1
  (spec 087) has genuinely not landed yet and the HR3 id is free; the heavy "re-verify at
  implement time" hedging in tasks.md (T001, T006, T008, T010) is warranted, not
  decorative.
- `docs/readiness/source-drift.md:70-75` was read verbatim: the "Downstream-invalidation
  rule" section states exactly what spec.md's Overview quotes, word for word, including
  "The detector FLAGS this; it MUST NOT silently demote or auto-`pass` any downstream
  stage." The line-74 citation is accurate.
- `src/retail/rules/readiness_status.py` (RS1) was read in full: `_INSTANCE_RE`,
  `_STAGE_ORDER`, `_STATUS_VALUES`, `_APPROVAL_REQUIRED`, `_AUTHORITY_CLASSES`,
  `_OWNER_SHAPE_RE`, and `_owner_is_valid` all exist exactly as plan.md/research.md
  describe them, with the exact reuse surface the plan claims. RS1 never reads a
  git-commit date and never treats `source_ready.status` as an implication for other
  stages -- confirmed by inspection, not assumed.
- `src/retail/gitutil.py` was read in full: it has no `git_last_commit_date` (or any
  per-path history read) today -- the plan's claim that this is a genuinely new helper is
  accurate. `git_output`, `validate_commit_range`, and `git_log_subjects` all exist and
  are the precedent the new helper is meant to follow (subprocess via `git_output`,
  option-injection-safe `--` pathspec separator).
- `src/retail/rules/git_meta.py` (the existing git-metadata rule family: G1-G5, P1, P2,
  C2) was read in full: **none of its rules reads a per-path commit-date/history log**.
  `git_check_ignore` and `git_log_subjects` (a bounded revision-range subject list) are
  the only `gitutil` calls in use today. This means HR3's `git log -1 --format=%aI --
  <path>` call is the **first** per-file git-history read anywhere in `retail check` --
  see Note 1 below; this is not a capability the codebase already leans on elsewhere.
- `mappings/retail_store_sales/readiness-status.yaml` (the SC-006 canary) was read in
  full, and its cited evidence paths' git dates were independently re-pulled:
  `git log -1 --format=%aI -- mappings/retail_store_sales/source-map.yaml` /
  `assumptions.md` / `unresolved-questions.md` all return `2026-06-25T15:33:29+03:00`;
  `metrics/` returns `2026-06-26T13:31:14+03:00`; `design/` returns
  `2026-07-03T14:21:10+03:00`. All match research.md's canary table exactly. The
  `mapping_ready` approval (`2026-06-25`) and its one resolving-file citation
  (`source-map.yaml`, same calendar day) land on the confirmed "same-day is not stale"
  tie -- verified, not assumed.
- The canary's `publish_ready` stage is independently observed to already be `blocked`
  with blocking_reasons narrating a retracted prior approval ("the prior publish approval
  ... was given against a pack that framed DiscountedTransactionRate as 33.55% ... the
  prior approval is retracted as stale"). This is a real, already-lived instance of
  exactly the human-demotes/system-surfaces pattern HR3 formalizes -- it happened by a
  human manually noticing and writing prose into `blocking_reasons[]`, which is the
  precise blind spot HR3 exists to stop relying on.

## Axis 1 -- hidden-principle-violation

Probe: does HR3 secretly self-grant an approval, decide a Principle-V judgment call, or
advise-instead-of-block?

- HR3 is read-only by construction and fails CLOSED: both stale conditions (FR-002
  drift-triggered, FR-003 approval-lag) are `Severity.ERROR`, not advisory (FR-001,
  confirmed no `"warning"` entry planned for HR3 in `severity-posture.json`'s T009). There
  is no path in the design where a `stale_pass` condition is merely logged or warned.
- FR-005 is the load-bearing non-self-grant guarantee: HR3 never writes
  `readiness-status.yaml`, never sets a status, never appends `blocking_reasons[]` on its
  own (which the design correctly notes would itself manufacture a fresh RS1 violation,
  since RS1 rejects `blocking_reasons[]` on a non-`blocked` stage). T048 turns this into a
  mechanical source-inspection test (no write/open-for-write call anywhere in the module),
  not just a docstring promise -- the same discipline the 087 review praised HR1 for.
- The clearing path (`stale_review`, FR-006/FR-007) is the second load-bearing guarantee:
  FR-009 explicitly forbids the agent from supplying or inferring `reviewer`, and the
  design correctly locates this constraint at the AGENT-BEHAVIOR layer (T051) rather than
  pretending a static rule module can enforce what an interactive agent session does --
  the same honest layering the 087 review flagged as a positive signal for HR1's FR-016
  boundary. A static rule genuinely cannot observe or prevent an agent auto-filling a
  YAML field in a later, unrelated turn; putting the guard where it can actually bite
  (agent conduct, not rule code) is correct, not evasive.
- The genuinely interesting judgment call in this spec -- whether `stale_review` may also
  clear a drift-triggered (FR-002) finding -- is explicitly left OPEN rather than
  defaulted. Spec.md's Clarifications marks it "OPEN owner ruling"; plan.md's "Open item
  carried to implement-stage" and tasks.md's T052 both implement the narrower PENDING
  DEFAULT (FR-007-as-written: approval-lag only) without silently broadening it. This
  mirrors the discipline the 087 review credited HR1 for on its own open item
  (Q-APPROVAL-SEAM).
- **Axis-1 tripwire for the build stage (see Note 3, non-blocking):** because this
  question is correctly left open rather than answered, the axis-1 PASS below is
  conditional on it STAYING open through implementation. A future edit that lets
  `stale_review` clear an FR-002 finding without an explicit owner ruling would flip this
  axis to a violation -- it would be exactly the kind of judgment call (defining what the
  reaffirmation escape hatch is FOR) Principle V reserves for a human, made silently by
  whoever implements T046.

Verdict: **PASS**. No hidden self-grant; the one open judgment call is genuinely left
open, not quietly resolved; the unenforceable-by-a-static-rule constraint (FR-009) is
honestly located at the layer that can actually enforce it.

## Axis 2 -- assumes-deferred-capability

Probe: does any artifact assume F016 / a live DB / a running adapter exists?

- F016 (Power BI execution adapter) is explicitly named as not existing and never invoked
  anywhere in spec.md's Boundary section, plan.md's Constitution Check (Principle III
  row), and research.md's "Deferred capabilities NOT assumed" section. No task, fixture,
  or code-path description references a Power BI connection, `pbi-cli`, or the official
  Power BI MCP.
- No live DB / `retail validate` dependency: FR-010 explicitly forbids a live re-profile
  runtime or a `retail drift` CLI; Technical Context's Storage line states "N/A -- no
  database, no live connection." Independently confirmed: no `retail drift` CLI or
  comparator module exists anywhere under `src/retail/` in this worktree, and
  `docs/readiness/source-drift.md` is prose-only (confirmed by direct read) -- the design
  correctly treats it as a document, not a runtime.
- The one genuinely new mechanical capability -- a `git log -1 --format=%aI` subprocess
  read via a new `gitutil.git_last_commit_date` helper -- is a STATIC, already-committed-
  history read (Principle VIII), not a live surface, and is structurally identical to
  `git_output`'s existing subprocess pattern.
- **Note 1 (non-blocking, build-stage instruction, elevated from a soft note because of
  what this review independently confirmed): full git history is a real, unstated
  precondition this feature introduces for the first time, and the design's fail-closed
  handling of a `None` commit-date result creates a shallow-clone false-positive vector.**
  `gitutil.py`'s new helper returns `None` when `git log -1 --format=%aI -- <path>` yields
  no output (T022). HR3's design (T038) then treats that `None` the same as an FR-013
  unresolvable-citation ERROR. But `None` can occur for two structurally different
  reasons that the current design does not distinguish: (a) the evidence token never
  resolved to a tracked file at all (a real unresolvable citation -- correct to flag), and
  (b) the token DID resolve to a tracked file (case (a) of the extraction algorithm,
  `ctx.tracked_files` contains it) but `git log` still returns nothing because the clone
  is SHALLOW (`git clone --depth=1` / `actions/checkout@v4`'s default `fetch-depth: 1`).
  For (b), the file is genuinely tracked and committed -- it is not an unresolvable
  citation, the local clone simply lacks the history to see its commit date. Verified
  this is a live gap, not a hypothetical: I confirmed by inspection that no existing
  `retail check` rule in this repo reads per-path git-commit history today
  (`git_meta.py`'s G1/G2/G3/G4/G5/P1/P2/C2 use only `git_check_ignore` and
  `git_log_subjects`, a bounded revision-range read) -- so `retail check`'s current CI
  posture has never depended on full clone depth, and this feature is the first to
  introduce that dependency. The plan's own Assumptions section ("a shallow clone without
  full history is an environmental concern for the CI runner, not a new design constraint
  this feature introduces") is not quite accurate given this: it IS effectively a new
  constraint, because HR3's OWN fail-closed `None`-handling is what turns a shallow-clone
  environment into false ERROR findings against valid, unchanged, already-approved
  evidence -- directly threatening SC-006 ("0 new HR3 findings" against the canary) in any
  CI job that does not fetch full history. This does not rise to a FAIL on this axis (a
  shallow clone is an environment/CI-configuration matter, not an assumption that F016 or
  a live DB exists), but it is a real build-stage risk that plan.md's current wording
  under-names. Recommend the build stage either (i) distinguish "resolves to a tracked
  file but has no discoverable commit history" from "does not resolve at all" and treat
  the former as `[PENDING full history]` rather than an ERROR (consistent with Principle
  VIII's "mark pending, do not fabricate" posture), or (ii) explicitly document as a
  release/CI gate that `retail check` in this repo now requires `fetch-depth: 0` (full
  history) and verify that requirement is actually met in whatever CI config exists.
  Either resolution is an implement-stage decision, not a spec defect -- flagged as an
  N-note the build must honor, not a blocking finding.

Verdict: **PASS**. No deferred capability (F016 / live DB) is assumed to exist anywhere in
the design. The shallow-clone dependency noted above is a genuine environmental risk this
feature introduces, but it is a CI/Principle-VIII-posture concern, not an assumption that
a deferred adapter or live surface already exists -- it does not warrant RISK on this
specific axis, though it is carried forward as a build-stage note.

## Axis 3 -- c086-leak

Probe: does any template/label bake in domain-specific values instead of staying generic
(Principle VII)?

- data-model.md's schema shapes (`stale_pass` finding, `stale_review` entry) use only
  generic placeholders (`<stage_name>`, `<repo-relative-path>`, `<Person Name>
  (<authority_class>)`) -- no column, dimension, or metric name from any domain appears in
  a required field or a rule-logic literal.
- The one real-name citation in the whole chain is research.md's SC-006 canary table,
  which necessarily names `retail_store_sales` and its real evidence paths
  (`source-map.yaml`, `metrics/`, `design/`) because that is the literal file SC-006
  requires the design stay clean against -- this is the correct place for a real name to
  appear (a precedent/verification artifact), exactly as the 087 review treated a
  citation of real dimension names in its own research.md as acceptable. It is explicitly
  marked "illustrative only, not a requirement" wherever it recurs in data-model.md.
- T050 is a dedicated grep task confirming no C086/pharmacy/retail-domain-specific literal
  leaks into `rule_hr3.py`'s logic, the new `gitutil.py` helper, or
  `templates/readiness-status.yaml`'s new comment block -- a mechanical check, not a
  reviewed convention.
- Watch item for the implementer (non-blocking, mirrors the 087 review's equivalent
  note): T002's `templates/readiness-status.yaml` comment block for `stale_review` must
  stay illustrative and never literally copy the real `retail_store_sales` evidence
  strings verified above into the new file's example comments -- that would be the one
  realistic leak vector this feature could introduce, and T050's grep is positioned to
  catch it if it happens.

Verdict: **PASS**. No domain-specific literal is baked into rule logic or the template;
the one real-name citation lives in research.md's canary-verification prose, the correct
location for it.

## Axis 4 -- fabricated-confidence

Probe: does any artifact emit a numeric score/health/maturity/completeness count?

- Every `stale_pass`-family Finding reuses the existing, unchanged `Finding` dataclass
  (`rule_id`/`severity`/`message`/`locator`) -- no new numeric field is introduced
  anywhere in the five message shapes data-model.md enumerates (drift-triggered,
  approval-lag, unresolvable-citation, unparseable-date, invalid-reviewer-shape).
- FR-012 explicitly forbids a numeric decay/staleness/confidence score and any
  completeness or "N of M" count; FR-002 explicitly requires N stale stages to produce N
  separate findings, never one rolled-up finding with an implicit count -- this is a
  stronger anti-rollup discipline than most rules in this repo need, because staleness is
  exactly the kind of thing a lazier design would be tempted to summarize as "3/7 stages
  stale" or a percentage. T034a/T034b specifically pin the "two independent findings, no
  dedup" behavior for the double-condition case, closing the one place a rollup temptation
  would most plausibly sneak in.
- T048 makes this mechanically verified, not just reviewed: a dedicated test greps every
  emitted message string across all five shapes for percentage/ratio/decay/"N of M"
  formatting. This is the same class of stronger-than-docstring guarantee the 087 review
  credited HR1's T043 for.
- `stale_review` entries carry `stage`/`evidence`/`reviewer`/`at`/optional `note` only --
  no score field anywhere in the schema (data-model.md entity 2).

Verdict: **PASS**. No fabricated or invented number anywhere in the design; the anti-
rollup discipline (one finding per stale stage, one finding per changed evidence path) is
unusually well-pinned by dedicated fixtures (T034a, T034b) rather than left implicit.

## Axis 5 -- over-scope

Probe: does HR3 do more than its one readiness-stage job, or cross into another feature's
territory?

- Deliverables are tightly bounded: one new rule module (`rule_hr3.py`), one new
  `gitutil.py` helper, one new optional/additive `readiness-status.yaml` key
  (`stale_review`), the standard six-surface wiring lockstep every new rule already
  requires, and one new fixture corpus. This matches the RS1/SF1/AP1/HR1 sibling scope.
- The Boundary section (spec.md) is unusually explicit about five adjacent shipped
  surfaces it deliberately does NOT touch -- the Source Drift Detector design doc (stays
  reference-only, no drift taxonomy edit), RS1 itself (stays read-only reference, reused
  not modified), F027 Approval Console, F028/F035 evidence-pack generators, and the three
  read-only viewer/aggregator skills. T004 turns this into a checklist confirmation, not
  just prose. Cross-checked: `docs/readiness/source-drift.md` and
  `src/retail/rules/readiness_status.py` are both listed as REFERENCE ONLY / UNCHANGED in
  plan.md's Project Structure, and neither is edited by any task in tasks.md.
- The design actively refuses two plausible scope-expansion temptations rather than
  merely avoiding them: (a) it does not turn a directory-shaped evidence token into a
  citation by guessing which file inside it "is" the evidence, even though that would
  give FR-003 much broader real-world bite on the canary (see Note 2 below) -- because
  that would require exactly the kind of silent judgment call this feature's own
  discipline forbids, and would reintroduce the `D1-D8/C1/R1/G6`-class false positive
  research.md spent real effort ruling out; (b) it does not broaden `stale_review` to also
  clear FR-002 drift findings, leaving that OPEN for the owner (Axis 1). Both refusals
  shrink scope rather than expand it.
- FR-017 explicitly forbids a new readiness stage, a new `retail validate` live check, or
  any executor/adapter; T004 confirms no `.claude/skills/` file is in this feature's
  footprint.
- **Note 2 (non-blocking, honesty/overclaim risk to carry forward, not a scope
  violation)**: the feature's real-world bite on the canary it is verified against is
  narrower than the headline description suggests, and this is worth stating plainly
  rather than only in research.md's own "Honesty limitation" section. Of the canary's four
  approval-bearing `pass` stages, only `mapping_ready` receives any FR-003 coverage at
  all (its one resolving-file citation, `source-map.yaml`) -- `semantic_model_ready` and
  `dashboard_ready` cite ONLY directory-shaped tokens (`metrics/`, `design/`,
  `...SemanticModel`), all three of which independently verified above as postdating
  their shared `2026-06-25` approval by one to eight days, yet produce ZERO findings
  because a directory reference is correctly treated as prose, not a citation. And even
  `mapping_ready`'s one covered case passes only via the same-day tie rule (the commit and
  the approval land on the same calendar date). This is the CORRECT design decision (per
  Axis 5's refusal analysis above), not a defect -- but it means "a pass whose evidence
  changed after approval must show a re-review" is, on the one real table this repo has
  today, actively enforced for roughly one of four qualifying stages, and only barely at
  that. Spec.md's SC-002 and User Story 2 framing do not overstate this (they are phrased
  per-condition, not "all approval-bearing stages get full coverage"), but a future reader
  citing HR3 as a green light should not read a clean HR3 run as "no evidence has moved
  since approval" -- only as "no RESOLVING-FILE-cited evidence has moved since approval,"
  which is the same distinction the 087 review drew for HR1's prospective-not-yet-active
  enforcement value. T003/T017 already exist to record this at the design layer before
  code; this note asks that the distinction also survive into whatever human-facing
  description (glossary row, release notes) eventually describes HR3's guarantee.

Verdict: **PASS**. Scope is disciplined and actively resists genuine scope-creep
temptations (guessing directory contents, broadening the reaffirmation escape hatch)
rather than merely avoiding them by omission. The coverage-narrowness noted above is a
correct consequence of that discipline, not an over-reach, and is already partially
self-documented (T003) -- the ask is to keep it visible past the design stage.

## Notes / carry-forward (non-blocking)

1. **Shallow-clone false-positive vector (Axis 2, elevated).** HR3 is the first
   `retail check` rule to read per-path git-commit history (`git_meta.py`'s existing
   rules never do). Its `None`-commit-date handling collapses "token never resolved" and
   "resolved but history unavailable (shallow clone)" into the same FR-013
   unresolvable-citation ERROR. Recommend the build stage either distinguish the two
   (mark the shallow-clone case `[PENDING full history]`, not an ERROR) or explicitly
   require and verify `fetch-depth: 0` in whatever CI runs `retail check`. This is a
   real, previously-nonexistent CI precondition this feature introduces, not merely an
   "environmental concern" to wave past as plan.md's Assumptions section currently frames
   it.
2. **Coverage-narrowness overclaim risk (Axis 5).** On the one real committed table this
   repo has today, FR-003 approval-lag coverage is active for 1 of 4 qualifying
   approval-bearing `pass` stages (directory-cited evidence gets zero coverage by design).
   This is the correct, disciplined outcome (guessing inside a directory would be worse),
   but the glossary row / any human-facing description of HR3 should carry this
   distinction forward so a clean HR3 run is never read as "no evidence has moved" when it
   actually means "no resolving-file-cited evidence has moved."
3. **Axis-1 tripwire.** The `stale_review`-vs-drift-triggered-finding scope question must
   remain OPEN through implementation, exactly as plan.md's "Open item carried to
   implement-stage" and tasks.md's T052 currently hold it. A future change that lets
   `stale_review` clear an FR-002 finding without an explicit owner ruling would retroactively
   flip Axis 1 from PASS to a violation -- this is not a hypothetical for a different
   feature, it is the single most likely place this exact feature could regress after
   shipping.
4. **`git_last_commit_date`'s addition to `gitutil.py` is additive and low-collision.**
   Confirmed no existing function of that name exists and no other in-flight feature in
   this review's visibility claims that helper name; this is a one-line implementation
   note, not a scope or collision concern.

## Verdict

**Verdict**: PASS-WITH-NOTES

All five axes clear on direct, independent ground-truth verification (rule count, RS1's
exact reuse surface, `gitutil.py`'s current absence of any per-path history read,
`git_meta.py`'s confirmed lack of any per-file commit-date dependency today, and the
canary's git dates re-pulled and matched against research.md's table) -- not merely on
the plan's or analysis.md's self-report, despite analysis.md already being clean. The
design is notably disciplined: it correctly refuses to guess which file inside a cited
directory "is" the evidence (avoiding both a Principle-V overreach and the
`D1-D8/C1/R1/G6`-class false positive), correctly leaves the `stale_review`-vs-drift scope
question open rather than silently deciding it, and correctly locates the one
constraint a static rule cannot itself enforce (FR-009's no-auto-fill-reviewer) at the
agent-behavior layer instead of faking an in-code check. No CRITICAL or HIGH finding; no
axis is RISK or FAIL. Four non-blocking notes are carried forward: a shallow-clone
false-positive vector this feature is the first in the repo to introduce (build-stage
action needed), a coverage-narrowness point that should survive into human-facing
documentation, an axis-1 tripwire on the OPEN `stale_review`-vs-drift scope question, and
a low-risk implementation-naming note.
