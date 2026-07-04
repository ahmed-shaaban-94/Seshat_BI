# Adversarial Plan-Review: Promotion/Markdown Fact and Factless-Fact Coverage Pattern (097)

**Feature**: `097-promotion-markdown-factless` | **Date**: 2026-07-04
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports findings,
edits nothing). Artifacts reviewed: spec.md, plan.md, tasks.md, research.md,
data-model.md, quickstart.md.

**Precondition check**: spec.md, plan.md, tasks.md are present. `analysis.md`
is **absent** -- confirmed by directory listing, not merely "not read." Unlike
sibling reviews in this repo (e.g. 099, which inherited a `speckit-analyze`
FR/SC-coverage pass and then re-derived its own axes anyway), this review has
no analyze-stage output to cross-check or lean on at all; every finding below
is derived from direct inspection of the five present artifacts plus ground
truth against the live worktree, with no analyze-stage self-report to inherit
or diverge from. This is recorded as a process gap (see Notes), not treated as
a blocking defect of the plan itself -- the plan's own content is independently
reviewable without it.

**Ground truth verified directly against the worktree** (not merely the plan's
self-report):

- `git status --short` at the worktree root shows only new, untracked
  `specs/0NN-*/` directories (087 through 105); nothing under `src/`,
  `mappings/`, `templates/`, `docs/`, or `warehouse/` is modified or newly
  created outside the spec-chain folders. Confirms this feature has touched
  zero repo surface beyond its own `specs/097-.../` folder -- exactly what a
  plan-stage review should find (the two deliverables are authored at
  implement stage, not this one).
- `docs/patterns/` does not exist as a subdirectory (Glob: no match) and
  `templates/factless-fact.yaml` does not exist (Glob: no match) -- confirms
  research.md Sec 2's and tasks.md T002's claim that both target paths are
  genuinely unclaimed, not already partially built ahead of this review.
- `skills/retail-kpi-knowledge/domains/discounts-and-promotions.md` read in
  full: Discount Amount and Discount Rate % are marked Seeded with contract
  paths; Promotion Uplift % is marked "Planned (needs promotion dimension +
  baseline rule)" verbatim. This matches the spec's Overview and FR-010's
  characterization exactly -- the spec does not embellish or misstate the gap
  it is responding to.
- `specs/087-conformed-dimension-readiness/spec.md` read (Overview + Boundary
  sections): Status is `Draft`, rule id `HR1` is `RESERVED`, not implemented.
  `grep -rn "HR1" src/` returns zero hits -- confirms HR1 does not exist as
  code anywhere in the tree today, matching FR-006's framing of 087 as a
  "pending, not-yet-ratified" mechanism this feature cites but does not
  depend on or implement.
- `templates/source-map.yaml` read (header + authoring-notes convention,
  lines 1-60+): confirms the `gold_star.fact` / `gold_star.dimensions` /
  `derived_columns` shape and the "WHAT THIS IS / WHICH PLAYBOOK PHASES /
  WHICH ADR-0002 DEFAULTS / C086 IS A FILLED INSTANCE / SISTER ARTIFACTS"
  header convention that data-model.md Entity 4 and tasks.md T007 claim the
  new `templates/factless-fact.yaml` will mirror. The convention exists
  exactly as described; the plan is not inventing a convention that isn't
  there.
- Grep for the feature's own locked generic placeholder vocabulary
  (`coverage_fact`, `promotion_fact`, `markdown_amount`, `promoted_units`)
  across the full worktree: the only hits are this feature's own five
  spec-chain files (spec.md, plan.md, research.md, data-model.md, tasks.md,
  quickstart.md). Zero collision with any committed repo artifact (migration
  SQL, TMDL, mapping YAML, KPI contract). The placeholder vocabulary is
  genuinely unclaimed and generic, not an accidental alias for something real.
- Grep for the real committed dimension/fact names this feature must not
  collide with or restate (`dim_product_rss`, `dim_store_rss`, `dim_date_rss`,
  `fct_sales_rss`): these exist only in the real `retail_store_sales` mapping
  artifacts, the worked example, the PBIP model, and unrelated test fixtures
  -- never inside `specs/097-.../`. The plan's own citation of
  `docs/worked-examples/retail-store-sales.md` (research.md Sec 1, Sec 5) is
  the only place 097's artifacts come near this name family, and it is
  explicitly a "see" pointer, never a restatement with the real `_rss`
  suffix names substituted into 097's own illustrations.

## Axis 1 -- hidden-principle-violation

Probe: does the design secretly self-grant an approval, decide a Principle-V
judgment call, or advise-instead-of-block?

- Every Principle-V-shaped decision the spec touches -- grain, primary key,
  PII, promo mechanics (discount-type taxonomy, funding source, hierarchy),
  the dimension-mismatch precondition for the anti-join, partial-day/
  overlapping-promotion grain ambiguity, and the Promotion Uplift % baseline
  rule -- is explicitly named as an adopting-table/owner decision routed
  through the UNCHANGED source-mapping gate, never resolved here (FR-008,
  FR-009, Edge Cases, plan.md Constitution Check Principle V row). The
  Clarifications section is explicit and self-aware about this: "No
  Principle-V judgment calls... were surfaced as open by this clarification
  pass... every such call the spec touches is, by design, already delegated
  to an adopting table's own analyst/data-owner" -- this is a correct
  characterization, not a rhetorical dodge, because nothing in FR-001 through
  FR-016 actually answers one of those calls; each is stated as a name-and-
  flag, not a decision.
- No approval of any kind is recorded by this feature. There is no
  `readiness-status.yaml` write, no `approvals[]` entry, no gate transition
  anywhere in the plan or tasks -- confirmed by the Project Structure section
  ("Any `mappings/<table>/readiness-status.yaml` -- no new key, no new
  stage") and independently by the fact that no task in tasks.md opens or
  edits any file under `mappings/`.
- The three Clarifications (Q1 file paths, Q2 `measures: []` vs a degenerate
  marker column, Q3 illustrative-SQL-vs-prose) are all correctly categorized
  as non-Principle-V naming/authoring-convention calls (Principle VI
  "Defaults Then Deviations" territory), not disguised judgment calls. None
  of the three decides a grain, a PII classification, a business rollup, or a
  product/promotion identity -- they decide where a file lives and how a
  template's empty-measures convention is spelled, which is squarely inside
  this feature's own authoring latitude.
- No task advises against a MUST-NOT rather than blocking it. FR-007, FR-009,
  FR-010, FR-011 are all phrased as hard MUSTs/MUST-NOTs, and tasks.md's
  Phase 6 guard tasks (T022-T026) are verification tasks that CONFIRM the
  MUST-NOTs held, not advisory suggestions layered on top of a softer design.

Verdict: **PASS**. No hidden self-grant of approval or gate transition exists
anywhere in the plan or tasks; every genuine Principle-V-shaped call is
correctly named and left to the adopting table's own gate, never resolved by
implication.

## Axis 2 -- assumes-deferred-capability

Probe: does any artifact assume F016 / a live DB / a running adapter exists?

- F016 is referenced exactly as a deferral: FR-011 states this feature "MUST
  NOT... invoke any deferred execution adapter (F016)," and no other mention
  of F016 appears anywhere in the five artifacts in a "call it" or "assume it
  responds" framing.
- No live database connection is assumed, proposed, or deferred-with-a-
  PENDING-marker -- research.md Sec 4 is explicit that this feature has "NO
  live surface to defer at all... there is nothing to mark pending because
  nothing here connects to, queries, or assumes a database exists," which
  this review's own read of plan.md's Testing section and tasks.md's T028
  (a read-only `retail check` run, not a `retail validate` run) confirms:
  nothing in this feature's task list opens a DB connection.
- The one SQL artifact (the anti-join sketch, Entity 3 / T012) is explicitly
  and repeatedly labeled non-executable ("ILLUSTRATION ONLY -- not a proposed
  or runnable migration," data-model.md line 110), consistent with
  Clarification Q3's resolution. This is the correct treatment of the one
  place a live-adjacent artifact type (SQL) appears in an otherwise fully
  static feature.
- **The one place this axis has real teeth**: FR-006 and the pattern doc's
  planned content state that a promotion/factless star's shared dimensions
  "MUST be conformed" with the sales star's, and cite spec 087 / HR1 as "the
  mechanism that would eventually verify that conformance." Ground truth
  confirms HR1 is Draft and unimplemented (`grep -rn "HR1" src/` = zero
  hits). The CURRENT wording in FR-006 and research.md Sec 1/4 already frames
  this correctly as pending/not-yet-ratified, not as a live check -- so there
  is no live defect in the artifacts reviewed here. But this is a real
  implement-stage risk: if the pattern doc's prose (authored later, per
  plan.md's "authored at implement stage" framing) drifts even slightly
  toward "conformance is verified by HR1" rather than "conformance is a
  MUST-follow convention with no enforcement mechanism today," a reader could
  come away believing a live gate exists when it does not. Recorded as **N1**.

Verdict: **PASS**. No artifact in the current spec/plan/tasks/research/
data-model set assumes F016, a live DB, or a running HR1 rule exists or is
reachable; the SQL sketch is correctly labeled non-executable. One
implement-stage wording discipline (N1) should be enforced when the pattern
doc's actual prose is authored, so the 087/HR1 citation cannot be
misread as an existing live gate.

## Axis 3 -- c086-leak

Probe: does any template/label bake in domain-specific values instead of
staying generic (Principle VII)?

- Direct grep confirms the feature's own generic placeholder vocabulary
  (`coverage_fact`, `promotion_fact`, `markdown_amount`, `promoted_units`,
  plus `sales_fact`, `dim_product`, `dim_store`, `dim_date`, `promotion_id`
  per research.md Sec 5's locked list) appears ONLY inside this feature's own
  spec-chain files -- zero collision with any real committed table, column,
  or dimension name anywhere else in the repository.
- `retail_store_sales` / `fct_sales_rss` are cited, by design, exactly once
  per artifact as an external "see" pointer (research.md Sec 1 and Sec 5,
  spec.md Boundary section, data-model.md Entity 3's Relationships) -- never
  restated with an invented promotion column or a fabricated worked number
  attached to that real table. This is the correct, narrower distinction
  099's own review had to draw (a cited filled instance is fine; inlining a
  domain-specific name into a GENERIC shape's fixed field/label is not) --
  and 097 does not cross it: no fixed field name, section header, or
  required key in Entity 1/2/4's shape borrows a real domain term the way
  099's `net_sales_consistency_note` did. Every field name in the illustrated
  `gold_star.fact` / `gold_star.dimensions` blocks (`grain`, `measures`,
  `name`, `dimensions`, `degenerate_dimensions`) is a structural YAML key
  already present in `templates/source-map.yaml`'s own shape, not a new
  domain-specific label.
- Unlike 099's flagged case, there is no analogous "borrowed KPI name baked
  into a fixed field label" here: `markdown_amount` and `promoted_units` are
  the feature's own SUBJECT (a promotion/markdown fact's measures), not an
  incidental borrowing from an unrelated worked example the way "Net Sales"
  was borrowed into a lineage-trace field name in 099. Promotion vocabulary
  appearing in a promotion-pattern doc is not a leak; it would only be a leak
  if a real adopting table's specific promotion name, product name, or
  discount-type value were inlined, and none is (confirmed by the grep above
  and by FR-008's explicit bar on inventing promotion mechanics beyond
  generic placeholders).
- T020's own verification grep-list (`retail_store_sales`, `fct_sales_rss`,
  `C086`, `pharmacy`, `el ezaby`/`El Ezaby`, "or any other worked-example or
  real-table-specific noun") is reasonably targeted but relies on a
  catch-all clause for the exact-suffix-confusable names (`dim_product_rss`,
  `dim_store_rss`, `dim_date_rss`) rather than naming them explicitly the way
  it names `fct_sales_rss`. This is a minor enforcement-precision gap, not an
  existing leak (the current five artifacts contain no `_rss`-suffixed name
  at all, confirmed by grep). Recorded as **N2**.

Verdict: **PASS**. No worked-example- or table-specific name is baked into
any fixed template field, section label, or required key anywhere in the
current spec/plan/tasks/research/data-model artifacts; the feature's own
placeholder vocabulary is confirmed collision-free against the full
committed tree. One enforcement-precision tightening (N2) is worth making to
T020's grep-token list before it runs at implement stage, but nothing to fix
in the plan's own content today.

## Axis 4 -- fabricated-confidence

Probe: does any artifact emit a numeric score/health/maturity/completeness
count?

- FR-014 states plainly: "This feature MUST NOT emit, and the pattern
  doc/template MUST NOT contain, any numeric confidence/health/maturity
  score or completeness count (hard rule #9)." SC-005 restates this as a
  measurable, inspectable outcome ("Zero numeric confidence/health/maturity
  scores or completeness counts appear in any artifact this feature
  produces"). Tasks.md T025 is a dedicated Phase 6 guard task that confirms
  this by inspection at implement-stage completion.
- Numerals that DO appear throughout the artifact set (16 FRs, 6 SCs, 3
  Clarifications, 4 named edge cases, 30 tasks) are ordinary requirement/
  task-count bookkeeping, not a readiness score, health metric, or
  completeness percentage attached to the feature's own maturity or to any
  table's readiness -- this review does not conflate the two, matching hard
  rule #9's actual target (a fabricated confidence/health/maturity/
  completeness assertion about READINESS), not any numeral whatsoever.
- Neither the promotion/markdown fact shape (Entity 1) nor the factless
  coverage fact shape (Entity 2) proposes a numeric field of any kind in
  their illustrated `gold_star` blocks -- every field is a name, a grain
  description, or a measures/dimensions list, never a score.
- No task, success criterion, or plan section proposes a "pattern adoption
  score," a "genericity score," or any other invented metric to characterize
  how well this feature succeeded -- SC-001 through SC-006 are all binary/
  qualitative inspection checks (does the doc name X; is `measures[]` empty;
  do zero real names appear; are zero rule ids added; are zero scores
  present; are the KPI files byte-identical), never a numeric tally
  presented as a maturity indicator.

Verdict: **PASS**. No fabricated or disguised numeric confidence/health/
maturity/completeness value exists anywhere in the plan, tasks, research, or
data-model; the only numerals present are ordinary requirement/task
bookkeeping, and a dedicated guard task (T025) exists to confirm this holds
in the two authored deliverables at implement stage.

## Axis 5 -- over-scope

Probe: does the plan do more than its one readiness-stage job, or cross into
another feature's territory?

- The spec's own "Boundary against neighbouring shipped work" section draws
  four specific, falsifiable lines against its closest neighbors
  (discounts-and-promotions domain doc, `templates/source-map.yaml`, the
  `retail-store-sales` worked example, spec 087/HR1) and every FR this review
  cross-checked holds up against direct reading: FR-010 (no KPI status flip,
  confirmed byte-identical claim in SC-006), FR-002 (no edit to
  `source-map.yaml`, confirmed by `git status` showing no modification to
  any existing `templates/` file), FR-012 (no edit to the worked example,
  same `git status` confirmation), FR-006 (087/HR1 cited, not implemented,
  confirmed by the zero-hit `grep -rn "HR1" src/`).
- Deliverables are tightly bounded to exactly two new files (`docs/patterns/
  promotion-markdown-factless.md`, `templates/factless-fact.yaml`) plus the
  new `docs/patterns/` directory -- confirmed both do not yet exist (Glob:
  no match for either), so this plan has not quietly gotten ahead of itself
  by partially authoring content before the review gate.
- FR-007 and SC-004 explicitly bar touching `src/retail/rules/__init__.py`,
  `EXPECTED_RULE_IDS`, the glossary rules table,
  `docs/rules/rules-manifest.json`, the severity-posture record, or any
  `readiness-status.yaml` key -- and `git status --short` confirms nothing
  under `src/` or `mappings/` is touched by this feature's current state.
  This matches the collision-avoidance allocation stated in the task framing
  ("Adds NO static rule... touches no shared schema") exactly.
- The plan explicitly declines to advance any readiness stage for any real
  table (plan.md Constitution Check, Readiness System row: "None directly...
  a cross-cutting kit-vocabulary addition... orthogonal to the seven-stage
  per-table spine"), consistent with the collision-avoidance allocation given
  in this task's own framing. No task creates a `mappings/<table>/`
  directory, edits a migration, or touches a PBIP model (tasks.md's repeated
  "Hard boundary" callout, and the Phase 6 guard tasks T022-T024 verify this
  at completion).
- The feature does not silently absorb spec 087's job: it cites HR1 as the
  future enforcement mechanism but explicitly states it adds "NO static rule,
  reserved rule id, or wiring to enforce that" (spec.md Boundary section) --
  confirmed structurally correct since HR1 remains unimplemented in `src/`
  and this feature's tasks.md contains no rule-authoring task of any kind.
- One scope-adjacent observation worth naming precisely: the "Serves: Stages
  2-6" framing given in this task's own header, and plan.md's "Readiness
  System (spine)" row, both correctly land on "advances no stage for any real
  table" as the operative answer -- the "Stages 2-6" language describes which
  future per-table stages a pattern ADOPTER would eventually walk through,
  not a claim that this feature itself advances any of them. This is
  consistent phrasing across spec/plan and not a scope overreach, but it is
  a phrase a less careful reader could misparse; not worth a blocking finding
  since the plan's own Constitution Check table already disambiguates it
  correctly in the artifact that matters most.

Verdict: **PASS**. Scope is disciplined and matches its stated
collision-avoidance allocation (two new files, no rule, no schema touch, no
stage advance for any real table); every boundary claim against a named
neighbor holds up under direct `git status` / grep verification, not merely
the plan's own self-report.

## Notes / carry-forward (non-blocking)

- **N1** (Axis 2, low-medium): when the pattern doc's actual prose is
  authored at implement stage, the spec 087/HR1 citation must stay framed as
  "a pending, unratified convention with no enforcement mechanism today," not
  drift toward language that could be read as "conformance is checked" or
  "conformance is enforced." FR-006's current wording in the spec already
  gets this right ("cite spec 087... as the existing/pending mechanism that
  would verify that conformance... without this feature adding, wiring, or
  duplicating that mechanism itself") -- this note is a guard against drift
  during T016's actual authoring, not a defect in the spec/plan as written.
- **N2** (Axis 3, low): tighten T020's grep-token list to explicitly name
  `dim_product_rss`, `dim_store_rss`, `dim_date_rss` alongside the already-
  named `fct_sales_rss`, closing the one-suffix-away confusability gap with
  this feature's own generic `dim_product`/`dim_store`/`dim_date`
  placeholders, rather than relying solely on the catch-all "or any other
  real-table-specific noun" clause.
- **N3** (process, non-blocking): `analysis.md` is absent for this feature,
  unlike sibling reviews in this repo that had a `speckit-analyze` pass to
  independently cross-check FR/SC coverage before this adversarial review
  ran. This review derived all five axes from direct inspection with no
  analyze-stage self-report to lean on or diverge from; it does not block
  this review's own conclusions (the plan's content is independently
  verifiable without it), but the build should not assume an analyze-stage
  FR-to-artifact coverage sweep already happened -- tasks.md's own T029 (an
  FR-to-task coverage sweep) is the closest existing substitute and should be
  executed as specified.

## Verdict

**Verdict**: PASS-WITH-NOTES

All five axes clear cleanly on direct inspection and ground-truth
verification against the live worktree (no analyze-stage output was
available to inherit or lean on -- see N3). No hidden Principle-V self-grant
exists; every genuine judgment call (grain, PII, promo mechanics, the
baseline rule, the dimension-mismatch precondition) is correctly named and
left to the adopting table's own source-mapping gate. No artifact assumes
F016, a live database, or an implemented HR1 rule; the one SQL sketch is
correctly labeled non-executable. No worked-example- or table-specific name
is baked into any fixed template field or label -- the feature's own generic
placeholder vocabulary is confirmed collision-free against the entire
committed tree by direct grep, and its promotion/markdown vocabulary is the
feature's legitimate subject, not a borrowed leak. No numeric confidence/
health/maturity score or completeness count appears anywhere; only ordinary
requirement/task bookkeeping numerals are present. Scope is disciplined to
exactly two new files with no rule, no schema touch, and no stage advance for
any real table, verified against `git status` rather than the plan's own
self-report. Two non-blocking implement-stage notes (N1: keep the 087/HR1
citation framed as pending/unenforced when the pattern doc's prose is
actually authored; N2: tighten T020's grep-token list with the `_rss`-
suffixed dimension names) and one process note (N3: no analysis.md existed
for this review to cross-check against) should be honored during
implementation but require no change to spec.md, plan.md, or tasks.md as
currently written. Nothing here blocks proceeding to the implement stage.
