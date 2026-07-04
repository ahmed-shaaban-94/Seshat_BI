# Adversarial Plan-Review: Actuals-vs-Target (Budget) Fact + Variance Readiness

**Feature**: `095-actuals-vs-target-budget-fact` | **Date**: 2026-07-04
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports findings,
edits nothing). Artifacts reviewed: spec.md, plan.md, tasks.md, research.md,
data-model.md, quickstart.md.

**Precondition check**: spec.md, plan.md, tasks.md are present.
**`analysis.md` does NOT exist in this feature directory** -- `speckit-analyze`
has not been run for 095, so there is no cross-artifact analyze verdict to
cite. This review does not fabricate that precondition; it proceeds on spec +
plan + tasks + research.md + data-model.md + quickstart.md only, and performs
its own ground-truth verification in place of an analyze pass (see below).
This absence is recorded as a non-blocking N-note, not a BLOCKED precondition,
because the six artifacts present are internally consistent and independently
verifiable against the live tree (matches the precedent set by the
`087-conformed-dimension-readiness` review under the same absence).

**Ground truth verified directly against the worktree** (not merely the
plan's self-report):

- `templates/metric-contract.yaml` exists; its field set matches what
  research.md Sec 1/data-model.md claim verbatim (`name`, `grain`,
  `formula_intent`, `owner`, `binds_to.{gold_table, columns, pii_sensitive}`,
  `readiness.{status, evidence, blocking_reasons}`, `ambiguities[]` with
  `id/decision_status/ruling/evidence/number_moving`), plus an OPTIONAL
  `definition` block (F-DAXGEN) not mentioned in the shape's field-set claim --
  see Axis 3 note.
- `skills/retail-kpi-knowledge/domains/targets-and-budgets.md` exists; its
  content matches what FR-003/FR-005/research.md cite: the KPI
  ("Net Sales vs Target %"), its `Planned (needs target fact)` status, the
  four named ambiguities, and the non-additive-percentage note. **This file
  contains non-ASCII bytes** (an em-dash, `\xe2\x80\x94`, in its KPI table and
  decision-question table rows) -- confirmed by direct byte-level decode. This
  is a pre-existing condition in a file this feature only cites and never
  edits (FR-015); it is not introduced by this feature. See Axis 3/Notes for
  the live tension it creates with FR-017 (ASCII-only in the NEW artifacts).
- `docs/worked-examples/retail-store-sales.md` exists (cited, not edited).
- `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` exists;
  the fact table name (`gold.fct_sales_rss`) and all five conformed dimension
  names (`gold.dim_customer_rss`, `gold.dim_product_rss`,
  `gold.dim_payment_method_rss`, `gold.dim_location_rss`, `gold.dim_date_rss`)
  are confirmed present verbatim via `CREATE TABLE`/`DROP TABLE` statements --
  matches spec.md Acceptance Scenario 1 (US3), FR-011, SC-006 exactly.
- `docs/decisions/0002-retail-cleaning-defaults.md` exists (RC14 citation
  source, not independently re-verified word-for-word here but the file is
  present and is a standing repo artifact other shipped features already cite
  the same way).
- None of the three target deliverable files exist yet
  (`docs/patterns/target-budget-fact.md`,
  `templates/metric-contract-shape.variance-vs-target.yaml`,
  `docs/worked-examples/target-budget-pattern-retail-store-sales.md`) --
  matches plan.md/research.md's "additive only, no overwrite" claim. The
  `docs/patterns/` directory does not exist yet either (T002 correctly notes
  it "may not exist yet").
- No existing file anywhere in `docs/`, `templates/`, or `skills/` references
  `variance-vs-target` or `target-budget-fact` outside this feature's own
  `specs/095-*` chain -- the two new paths are genuinely free, no collision
  with the other in-flight features as of this read.
- `docs/rules/rules-manifest.json` currently has 55 rule ids -- consistent
  with FR-014's claim that this feature adds none (the count this feature
  should leave unchanged).

## Axis 1 -- hidden-principle-violation

Probe: does the plan secretly self-grant an approval, decide a Principle-V
judgment call, or advise-instead-of-block?

- The three Principle-V judgment calls the domain doc's own ambiguities and
  this feature's Clarifications session surface (target-fact grain, RAG
  thresholds, versioning/reforecast handling) are each explicitly left
  **OPEN** in spec.md's Clarifications section, each stamped "OPEN owner
  ruling -- Principle V, business-policy/grain judgment call; NOT answered
  here." No default value, no plausible placeholder number, and no
  resolved-by-fiat grain is substituted for any of the three.
- `readiness.status: blocked` (T022) with two REQUIRED
  `readiness.blocking_reasons[]` entries (missing-target case, missing RAG
  threshold) is the correct fail-CLOSED shape for the contract SHAPE
  artifact -- there is no path in the plan where a filled instance of this
  shape could reach `pass` without a named owner's `evidence[]` entry (the
  template's own existing discipline, reused unmodified).
- FR-016/T035 constrain the second worked example's readiness framing to the
  four explicit statuses, used honestly as `not_started` for
  `retail_store_sales`'s (nonexistent) target fact -- never a status implying
  progress that has not happened. No `approvals[]` entry and no
  readiness-status.yaml write is authored anywhere in this feature (FR-018;
  plan.md "Files/dirs a FUTURE build would touch" section lists this as
  explicitly NOT created here).
- The plan does not advise-instead-of-block anywhere it has the fail-closed
  option available: FR-009/T024 REFUSE to supply a default RAG threshold
  (explicitly distinguished from RC14's safe additive default, since "RAG
  bands have no safe generic default"), and FR-002/T010 refuse to assert a
  default grain even though a plausible one (e.g. "month x store x category")
  is named as an EXAMPLE in prose -- it is never planted as the actual value
  the marker resolves to.
- One load-bearing question an adversarial reviewer must not wave past: does
  citing the domain doc's ALREADY-established non-additive-variance and
  missing-target rules as "resolved structural defaults" (FR-019,
  data-model.md's ledger) quietly promote a Principle-V call to a "safe
  default" that was never actually ratified as a kit-wide default? Traced
  through: no -- these two are not judgment calls this feature is making;
  they are VERBATIM citations of prose the domain doc ALREADY carries (T004
  pins this verbatim; FR-003/FR-005 require citation, not restatement). The
  plan does not invent a new default the domain doc did not already state; it
  reuses an existing citable fact. This is the same "resolved defaults vs.
  open items" ledger discipline the constitution's Principle VI already
  applies elsewhere, not a fresh, unratified default this feature manufactures
  on its own authority.

Verdict: **PASS**. No hidden self-grant; every genuine judgment call
(grain, RAG, versioning) stays an explicit, unresolved `[NEEDS
CLARIFICATION]` marker, and the two "resolved defaults" the ledger claims are
traceable citations of already-published domain-doc text, not new invented
policy.

## Axis 2 -- assumes-deferred-capability

Probe: does any artifact assume F016, a live DB, or a running adapter exists?

- The plan is 100% static by its own repeated framing (Constitution Check row
  VIII; research.md Sec 4 "Deferred capabilities NOT assumed"): zero SQL,
  zero migration, zero live DB connection, zero `retail validate` run is
  authored or assumed reachable anywhere in the three deliverables.
- F016 (Power BI execution adapter) is explicitly named as not existing and
  not invoked; RAG *visualization* is explicitly deferred to a later,
  separate dashboard-design concern this feature does not address (spec.md
  Assumptions; research.md Sec 4).
- The plan is careful to distinguish a live-data `[PENDING LIVE PROFILE]`
  deferral (which does not appear anywhere, because no live surface is
  touched at all) from a Principle-V `[NEEDS CLARIFICATION]` business-policy
  deferral (grain, RAG, versioning) -- research.md Sec 4 states this
  distinction explicitly rather than conflating the two marker types, which
  is the correct discipline (mirrors the same care the 087 review credited
  its sibling feature for on the grain-limb deferral).
- Quickstart.md Step 5 explicitly frames the real per-table build
  (`source-mapping` -> `retail-build-warehouse` -> `retail-validate`) as a
  SEPARATE, LATER, unscheduled feature this plan does not execute any part
  of -- it names the sequence for orientation only, never claims to have run
  a step of it.

Verdict: **PASS**. No deferred capability (F016, live DB, adapter) is assumed
reachable anywhere; the plan's only deferred markers are Principle-V business-
policy markers, correctly distinguished from a live-data deferral.

## Axis 3 -- c086-leak

Probe: does any template/label bake in domain-specific values instead of
staying generic (Principle VII)?

- Two different surfaces call for two different rules here, and the plan
  gets the distinction right:
  - The **contract shape** (`templates/metric-contract-shape.variance-vs-
    target.yaml`) is the generic-template surface. T017 mandates a
    placeholder `name` (`<VarianceMetricName>`) and placeholder `owner`
    matching the existing template's OWN placeholder convention; T020 fills
    `binds_to.gold_table` with a PRIMARY-actuals PLACEHOLDER, not a real
    table name; research.md Sec 5 states `formula_intent` names the second
    table generically as `gold.<actuals_fact>` / `gold.<target_fact>`, not a
    real `_rss` name. No task in Phase 4 instructs filling this file with
    `gold.fct_sales_rss` or any other real committed name.
  - The **second worked example** (`docs/worked-examples/target-budget-
    pattern-retail-store-sales.md`) is SUPPOSED to be concrete -- it is
    Principle VII's own required SECOND data point, and real `_rss` names
    are the correct, sanctioned content there (FR-011, SC-006, T027).
    Concrete naming in this one file is not a leak; it is the deliverable.
  - Because the plan's tasks mandate the safe (placeholder) form for the
    generic surface and reserve concrete names for the sanctioned narrative
    surface, this axis is an earned PASS on the PLAN as written, not a
    rubber stamp -- the deviation risk (an implementer accidentally pasting
    `gold.fct_sales_rss` into the contract-shape TEMPLATE file instead of
    into the worked-example file) is a genuine, named risk, carried below as
    a non-blocking N-note (mirroring 087's T044 grep-verification note for
    the same class of risk).
- T030 (Polish) is a dedicated grep-verification task for fabricated VALUES
  (numeric target/variance/RAG), which is adjacent to but not identical to a
  c086-leak check (a leak here would be a real TABLE/COLUMN name landing in
  the generic template, not a numeric value) -- T031's field-set diff would
  likely catch a structural leak (an extra field), but a same-shaped field
  filled with a real name instead of a placeholder is NOT mechanically
  caught by any task in Phase 6. This is a real gap in the polish-phase
  task list, carried below as a non-blocking N-note.
- FR-006/SC-005's "0 new/renamed fields" bar is satisfied by the template's
  field set as confirmed by direct read; the one nuance is that
  `metric-contract.yaml` also carries an OPTIONAL `definition` block
  (F-DAXGEN) that the shape's claimed field-set list (research.md Sec 1,
  data-model.md) does not enumerate. Omitting an OPTIONAL block is not a
  "new/renamed field" violation -- SC-005's own bar is about additions/
  renames, not about mandatory inclusion of every optional block -- so this
  is a non-blocking clarification, not a defect.

Verdict: **PASS**. The plan correctly keeps the generic-template surface
placeholder-only and reserves real `_rss` names for the one sanctioned
narrative surface; the residual risk is an implementer-discipline concern
flagged as an N-note, not a plan-level defect.

## Axis 4 -- fabricated-confidence

Probe: does any artifact emit a numeric score/health/maturity/completeness
count?

- FR-010/FR-016 (hard rule #9) are stated as explicit prohibitions covering
  every one of the three deliverables, and T030/T035 are dedicated,
  independently-run grep/inspection tasks (not merely a docstring promise)
  that check for numeric target values, variance percentages, RAG colors,
  AND any numeric confidence/health/maturity/completeness score across all
  three files.
- The readiness vocabulary used anywhere in this feature's artifacts is
  constrained to the existing four-status set (`not_started | blocked |
  warning | pass`) already defined by the constitution and
  `templates/metric-contract.yaml` -- no new status word, no percentage-based
  status, and no numeric field is introduced by any FR or task.
- `readiness.status: blocked` (T022) is a categorical state, not a score; the
  two blocking_reasons entries it requires are text, not numbers.
- SC-007's "locate every `[NEEDS CLARIFICATION]` marker in under one pass" is
  a locatability check, not a maturity/completeness percentage -- it does not
  introduce a "% resolved" tally, which would have been an easy but
  prohibited shortcut to reach for here.

Verdict: **PASS**. No numeric score, health indicator, maturity label, or
completeness count is proposed anywhere in spec/plan/tasks/research/data-
model/quickstart; the four-status vocabulary is used honestly and the
verification tasks are mechanical, not self-reported.

## Axis 5 -- over-scope

Probe: does the plan do more than its one readiness-stage job, or cross into
another feature's territory?

- Deliverables are tightly bounded to exactly the three files the spec's
  Clarifications session already fixed a path for: one pattern doc, one
  contract-shape YAML instance, one worked-example narrative. No task
  authors a fourth file, and T002 explicitly confirms none of the three
  collide with anything already committed.
- The plan actively REFUSES two plausible scope-expansion temptations rather
  than merely avoiding them by omission:
  1. It does not add a second `gold_table` key or fork `binds_to` into a list
     to "solve" the two-table tension cleanly -- FR-007/T020/research.md Sec
     5 explicitly flag this as an OPEN NOTE for human/F009-owner review,
     leaving the actual template-mechanism decision to a future F009
     amendment this feature does not make.
  2. It does not flip `targets-and-budgets.md`'s `Planned` marker to
     anything else, and does not edit `retail-store-sales.md` or
     `metric-contract.yaml` at all (FR-015; T033 is a dedicated `git diff`
     zero-diff check on exactly these three files) -- these are explicitly
     called out as reserved for whoever ships the first REAL target-fact
     table, out of scope here.
- No new readiness stage, four-status gate, or `retail check` rule ID is
  added (FR-014; T034 confirms by inspection; ground-truth confirms the live
  manifest is unaffected at 55 ids). No `mappings/<table>/` directory, no
  migration SQL, no PBIP/semantic-model edit is authored (FR-018; the plan's
  own "Files/dirs a FUTURE build would touch" section explicitly lists these
  as NOT created here, for orientation only).
- Dashboard-design consequences (how a specific table's dashboard visualizes
  a missing-target flag or a RAG color) are explicitly and repeatedly named
  as out of scope (Edge Cases, FR-005, data-model.md Missing-Target-Case
  entity) rather than quietly addressed in passing.
- The plan does not attempt to retrofit a live-validation check, a
  `retail check` rule, or a readiness-status write for `retail_store_sales`'s
  nonexistent target fact -- T028/FR-012 keep the second worked example
  honestly a narrative-only artifact, and the Edge Cases section explicitly
  states it "MUST NOT be treated as evidence of any readiness stage."

Verdict: **PASS**. Scope stays inside the sanctioned three-file allocation;
the plan visibly resists two realistic scope-creep paths (a `binds_to` schema
fork, a `Planned`-marker flip) rather than merely not doing them by accident.

## Notes / carry-forward (non-blocking)

- **`analysis.md` is absent for this feature.** `speckit-analyze` has not
  been run. This review substituted direct ground-truth verification
  (metric-contract.yaml field set, migration table/dimension names, rule
  count, path-collision check, ASCII-byte check) for the missing
  cross-artifact analyze pass. Recommend running `speckit-analyze` before or
  during implementation so a genuine 0-critical/0-high verdict exists in the
  chain.
- **c086-leak vector for the implementer, not the plan.** The one realistic
  leak this feature could introduce is an implementer pasting a real,
  committed name (`gold.fct_sales_rss`, `dim_product_rss`, etc.) into the
  GENERIC contract-shape template (`templates/metric-contract-shape.variance-
  vs-target.yaml`) instead of keeping it placeholder-only, while reserving
  real names for the worked-example file where they belong. No task in
  Phase 6 mechanically greps the contract-shape file for real `_rss`/table
  names the way T030 greps for numeric values -- recommend adding this check
  (a same-name grep against the shape file, expecting zero matches) alongside
  T031's field-set diff when this feature reaches Polish, mirroring the 087
  review's T044 note for the analogous risk.
- **ASCII-vs-verbatim-citation tension.** `skills/retail-kpi-knowledge/
  domains/targets-and-budgets.md` (cited but never edited by this feature)
  contains an em-dash (non-ASCII byte, confirmed by direct decode) in its KPI
  and decision-question tables. T004 requires recording that doc's content
  "verbatim," and FR-003/FR-005 require CITING it rather than restating it as
  independently-invented guidance. If an implementer interprets "cite
  verbatim" as "byte-copy the table row," the em-dash would land in the new
  pattern document and violate FR-017/T036's ASCII-only requirement for the
  NEW artifacts. The plan does not mandate byte-copying (citation, not
  transcription, is what FR-003/FR-005 actually require), and T036 would
  catch the violation if it occurred -- so this is a genuine but non-blocking
  tension the implementer should resolve by paraphrasing/citing-by-reference
  (e.g., "see targets-and-budgets.md's Notes section") rather than pasting
  the table row's exact bytes.
- **FR-003/FR-005's citation discipline is only build-time verifiable.** The
  plan states the intent clearly (cite, don't restate as invented guidance)
  but nothing in Phase 6 mechanically distinguishes a citation from a
  restatement -- this is inherently a prose-quality judgment call for
  whoever authors T011/T013, not something a grep can verify. Not a plan
  defect (no realistic mechanical check exists for this), but worth the
  implementer's attention.
- **The two-table `binds_to` tension must stay an explicitly OPEN note.**
  FR-007 is correctly framed as "flag... for human/F009-owner review," not
  "resolve." Any FUTURE edit to this feature's contract shape (or a
  follow-up feature) that quietly adds a second `gold_table` key, forks
  `binds_to` into a list, or otherwise resolves this tension without a named
  F009-owner ruling would flip Axis 1 (hidden self-grant of a template-design
  decision) and Axis 5 (over-scope into F009's own territory) from PASS to a
  violation. This review's PASS verdict is conditioned on the tension
  staying open exactly as FR-007 currently states it.
- **SC-005's field-set bar should read as "0 new/renamed required fields,"
  not "must reproduce every optional block."** `metric-contract.yaml` also
  carries an OPTIONAL `definition` (F-DAXGEN) block not enumerated in
  research.md/data-model.md's field-set citation. Omitting an optional block
  is not a violation of SC-005's own stated bar (0 new/renamed fields), but a
  future reviewer diffing the two files naively could misread the omission as
  a mismatch -- worth a one-line clarification in the contract shape's own
  header comment if convenient, not a blocking requirement.
- **Minor environmental note, not a governance finding**: the actual worktree
  branch is `worktree-HERA`, not `095-actuals-vs-target-budget-fact` as T001
  assumes it will read from `git branch --show-current`. This is the same
  environmental worktree-naming pitfall already documented in this project's
  own memory notes (worktree-cwd mismatch) and does not affect any of the
  five governance axes -- flagged here only so T001's execution does not
  stall on an unexpected branch name.

## Verdict

**Verdict**: PASS-WITH-NOTES

All five axes clear on direct ground-truth verification against the live
worktree, not merely on the plan's self-report: the `metric-contract.yaml`
field set, the `0004_*.sql` migration's fact/dimension names, the 55-rule
manifest count, the free (non-colliding) target file paths, and a byte-level
ASCII check of the cited domain doc were all independently confirmed. The
plan is uniformly defensive in shape -- almost every functional requirement
is a MUST-NOT or a cite-don't-invent instruction -- and it visibly resists
two realistic scope-creep paths (forking `binds_to` to resolve the two-table
tension, flipping the domain doc's `Planned` marker) rather than merely
avoiding them by accident. No CRITICAL or HIGH finding; no axis is RISK or
FAIL. The carry-forward notes are non-blocking: the missing `analysis.md`,
a c086-leak vector that depends on implementer discipline in the contract-
shape file (with a recommended additional Polish-phase grep), a genuine
ASCII-vs-verbatim-citation tension against the cited domain doc's em-dash,
the inherently non-mechanical nature of the "cite, don't restate" discipline,
the requirement that the two-table `binds_to` tension stay open (not
resolved) through implementation, and a minor SC-005 optional-block
clarification.
