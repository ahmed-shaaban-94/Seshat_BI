# Adversarial Plan-Review: Dimension History / SCD Policy Readiness (HR2)

**Feature**: `088-scd-dimension-history-policy` | **Date**: 2026-07-04
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports findings,
edits nothing). Artifacts reviewed: spec.md, plan.md, tasks.md, analysis.md,
research.md, data-model.md, quickstart.md.

**Precondition check**: spec.md, plan.md, tasks.md, and `analysis.md` are all
present -- unlike the 087/HR1 sibling review (which had no `speckit-analyze`
pass to cite), 088 already has a cross-artifact analyze verdict. analysis.md's
own verdict: `scope_ok = true`, no constitution violation, but two concrete
Medium-severity spec-to-task coverage gaps (F1, F2) and one Low informational
staleness item (F3). This review does not take analysis.md's verdict on
faith -- it independently re-derives F1/F2/F3 against tasks.md's actual task
bodies below and confirms all three hold.

**Ground truth verified directly against the worktree** (not merely the
plan's self-report): live rule count is **55** (`docs/quality/rule-count-claims.yaml`
`claimed-count: 55`; `docs/rules/rules-manifest.json` has 55 `"id"` entries) --
matches plan.md's "HR2 lands as rule 56" claim. No `HR1` string exists
anywhere in `src/`, `docs/`, or `tests/` -- confirms 087/HR1 has NOT landed in
this tree yet, matching both plan.md's and tasks.md's "verify live, HR1 may
land first" hedge. No `HR2` string exists anywhere outside `specs/088-*` --
the id is genuinely free, no collision. The one committed gold migration
(`warehouse/migrations/0004_create_gold_retail_store_sales_star.sql`) was
read directly: it confirms research.md's C5 claim -- six `DROP TABLE IF
EXISTS` batched at lines 22-27, non-adjacent to each dimension's later
`CREATE TABLE ... ; INSERT INTO ...` recreation, zero occurrences of
`CREATE TABLE ... AS SELECT` anywhere in the file. This is load-bearing: a
rule literally matching the as-first-drafted "adjacent CTAS" wording would
fail OPEN on this repo's actual gold output, and the spec's own C5
correction fixes exactly that.

## Axis 1 -- hidden-principle-violation

Probe: does HR2 secretly self-grant an approval, decide a Principle-V
judgment call, or advise-instead-of-block?

- The core mechanism is read-only by construction: `scd_type` is
  human-authored inside `source-map.yaml` (FR-003, FR-011); HR2 only reads
  it and never infers or defaults a value. A missing, empty, `null`, or
  `"tbd"` declaration is never treated as `type_1` by convenience -- it is a
  fail-closed Needs-decision ERROR naming the dimension (FR-005), explicitly
  reasoned in spec.md as "silently assuming Type-1 would reproduce the exact
  silent gap this feature exists to end, only one layer higher."
- **The load-bearing question an adversarial reviewer must not wave past**:
  does this feature land GREEN by having the agent quietly fill in a safe
  default, the way a lazier design might paper over the adoption cliff? Traced
  through: no -- and the artifacts go out of their way to foreclose this.
  research.md's "Landing precondition" section states explicitly that both
  committed maps (`retail_store_sales`, `demo_sample_orders`) have dimension
  entries with NO `scd_type` key today, that HR2 registering makes `retail
  check` go RED on the live tree with no grandfather clause, and that "this is
  NOT something the agent may fix by scaffolding a placeholder value: filling
  in `scd_type: type_1` on a human's behalf, even as a 'safe default,' is
  exactly the Principle-V violation FR-011/FR-005 forbid." tasks.md's T041
  (the final gate-run task) explicitly instructs: "Do **NOT** assert a clean
  full-repo `retail check` run ... that RED is the intended, deliberate
  outcome of this feature landing, not a defect to fix here." This is the
  OPPOSITE of a hidden self-grant -- it is a design that accepts its own
  adoption cost rather than manufacture a false green. Compare to 087/HR1,
  which lands green via a genuinely-empty scaffold with nothing to
  adjudicate; 088 cannot and does not claim that shortcut for itself.
- FR-017 (Q-APPROVAL-SEAM) is correctly left OPEN rather than silently
  settled -- the plan records a PENDING DEFAULT (folds into existing Mapping
  Ready approval) the owner may later overturn, and T044 is explicitly
  labeled `[OWNER SEAM -- OPEN, do not answer]`, a checklist confirmation,
  not a resolution. No grain/PII/business-rollup/product-identity call is
  answered anywhere in the artifact set.
- The C3 positive-signal deferral (research.md, spec.md Clarifications) is a
  schema/mechanics gap ("no construct exists yet to recognize"), correctly
  distinguished from a Principle-V judgment -- HR2 does not smuggle in a
  guessed heuristic for what a valid Type-2 migration looks like; it names
  the gap and marks it future scope (T029's `[FUTURE SCOPE]` code comment).

Verdict: **PASS**. No hidden self-grant; the design's landing story is
notably the opposite of a shortcut -- it deliberately accepts a RED landing
on the live tree rather than scaffold a value that would constitute a
disguised Principle-V ruling.

## Axis 2 -- assumes-deferred-capability

Probe: does any artifact assume F016, a live DB, or a running adapter exists?

- HR2 is 100% static: it reads `ctx.tracked_files` text only (source-map YAML
  and gold migration SQL), `yaml` imported LAZILY out of the static-core
  chain (plan.md Primary Dependencies, mirroring SF1/HR1's precedent). No SQL
  parser, no database connection, no Power BI/PBIP surface read anywhere
  (FR-004, FR-012, Constitution Check row VIII).
- F016 (Power BI execution adapter) is explicitly named as gated + LAST and
  assumed NOT to exist (research.md "Deferred capabilities NOT assumed";
  quickstart.md Step 7 explicitly confirms no DB connection, SQL execution,
  Power BI Desktop session, or network access is required by any step).
- Live SCD-2 row-level data-correctness auditing (duplicate current rows,
  `effective_to` gaps, `is_current` flags) is explicitly named as OUT of
  scope and deferred to "a future `retail validate` extension" (spec.md
  Assumptions, plan.md Principle VIII row, research.md) -- named-and-deferred,
  not silently assumed to already exist. T038 mechanically enforces the
  static boundary via a grep-style assertion against live-DB imports, a
  stronger posture than a docstring promise.
- The positive Type-2-construct-recognition signal (C3) is correctly deferred
  to "whichever future feature adds Type-2 authoring" rather than assumed
  buildable now with an untested heuristic -- and, unlike HR1's grain limb
  (which had NO usable MVP signal at all), 088's own MVP negative signal is
  confirmed implementable today against the one committed migration, so
  nothing load-bearing for THIS feature's P1 slice is deferred.

Verdict: **PASS**. No deferred capability is assumed to exist anywhere in the
artifact set; the one genuinely future-scoped limb (positive Type-2
recognition) is honestly marked pending, not faked.

## Axis 3 -- c086-leak

Probe: does any template/label bake in domain-specific values instead of
staying generic (Principle VII)?

- The rule logic, the `templates/source-map.yaml` edit, and the fixture
  corpus use only illustrative placeholders (`dim_<entity_a>`,
  `<entity_a>_sk`), explicitly marked as such (FR-015; data-model.md header:
  "Generic (Principle VII) ... ILLUSTRATIONS ONLY, never required names").
  T003's template edit is specified as adding exactly
  `scd_type: "type_1"` to the existing illustrative entry -- no new
  domain-specific name is introduced by that edit.
- **The one borderline call worth making explicit**: data-model.md and
  research.md both cite the REAL committed dimension name
  `gold.dim_customer_rss` (and `gold.dim_product_rss`) when explaining why
  the C4 schema-prefix-stripping rule and the C5 construct-shape correction
  are confirmed against actual evidence, not invented. Tracing where each
  real name lands: it appears only in evidentiary/precedent-survey PROSE
  (research.md's "committed gold migration confirms," data-model.md's
  property-table commentary) -- never inside the `templates/source-map.yaml`
  SHAPE block itself (which stays `dim_<entity_a>` throughout), never inside
  any task's fixture-authoring instruction (T021-T024 all specify
  "illustrative table/column names only"), and never inside any rule-logic
  description. This is the same pattern the 087/HR1 review accepted for its
  own citation of `dim_product_rss` in research.md prose -- a citation of the
  existing tree as evidence is not the same as baking a required literal
  into shipped generic infrastructure.
- FR-015 explicitly forbids inlining a C086/pharmacy-specific value as a
  REQUIRED value in the rule or template, and T039 is a dedicated
  grep-verification task at build time (grep the rule module, the template's
  new `scd_type` line, and every fixture file for any such name).

Verdict: **PASS**, with a carry-forward watch-item (see Notes below): T039's
grep must remain a hard gate at implementation time to keep the real
`dim_customer_rss`/`dim_product_rss` names confined to prose and out of the
shipped `rule_hr2.py` and `templates/source-map.yaml` edit.

## Axis 4 -- fabricated-confidence

Probe: does any artifact emit a numeric score/health/maturity/completeness
count?

- HR2 reuses the existing `Finding` dataclass unchanged
  (`rule_id`/`severity`/`message`/`locator`) -- no new numeric field anywhere
  (data-model.md "HR2 Finding" table; FR-013).
- FR-013 explicitly forbids a numeric confidence/health/maturity/completeness
  score and an "N of M" tally; output is categorical only (per finding: the
  dimension, the table, and what is wrong). T037 is a dedicated MECHANICAL
  test (grep `rule_hr2.py`'s source and every emitted message string for
  percentage/ratio/"N of M" formatting), not merely a review-time claim.
- The one integer anywhere in the feature -- the rule COUNT (55 -> 56) -- is
  not a conformance/confidence score; it is the same `len(rules-manifest.json)`
  mechanism every prior rule addition uses (SC2's existing reconciliation),
  independently confirmed live at 55 by this review. plan.md and tasks.md
  (T002) correctly hedge it as "re-verify at implement time," not assert it
  as a settled fact, given the 19-parallel-feature serialization risk (HR1
  may claim the slot first).
- No maturity/health label is introduced anywhere; every Finding remains
  `Severity.ERROR` categorical, matching the existing enum (data-model.md:
  "there is no WARNING-only HR2 case").

Verdict: **PASS**. No fabricated or invented number anywhere; the one integer
present (rule count) is an authoritative `len()`, explicitly flagged as
re-verify-at-implement-time rather than a score.

## Axis 5 -- over-scope

Probe: does HR2 do more than its one readiness-stage job, or cross into
another feature's territory?

- Deliverables are tightly bounded: one new rule module (`rule_hr2.py`), one
  new nested schema key (`gold_star.dimensions[].scd_type`), the six-surface
  wiring lockstep every new rule already requires, and one new fixture
  corpus (plan.md Project Structure). This matches the SF1/AP1/HR1 sibling
  scope exactly.
- The plan explicitly REFUSES several scope-expansion temptations that would
  have been easy to fold in: (a) it does not teach `retail-build-warehouse`
  to author Type-2 SQL, even though that would have made the feature feel
  more "complete" -- explicitly named as a substantial separate feature
  (Assumptions: "This feature does not teach `retail-build-warehouse` to
  author Type-2 SQL"); (b) it does not build a positive-recognition signal
  for a valid Type-2 construct, since none exists in the tree to recognize
  yet (C3); (c) it does not invent an `approvals[]` shape or a new
  `readiness-status.yaml` key to answer FR-017, leaving that open for the
  owner instead (same discipline as HR1's own FR-016); (d) it does not add a
  new readiness stage -- `scd_type` is declared inside the EXISTING Mapping
  Ready artifact and HR2 runs on the EXISTING Gold Ready static surface
  (spec.md Boundary section, plan.md Constitution Check row IV).
- The spec's own "Boundary against neighbouring shipped work" section is
  unusually explicit about staying off adjacent surfaces: it does not
  re-implement S6/S7 (Gold Ready's existing static checks), does not touch
  `retail validate`, does not re-decide any table's grain/PK/PII (Mapping
  Ready's already-settled judgments), does not edit HR1's separate
  `conformed-dimension-map.yaml` (orthogonal axis: HR1 is cross-star name
  agreement, HR2 is one dimension's own history policy), and does not edit
  SF1/AP1's rule modules despite reusing their wiring shape.
- The collision-avoidance allocation is honored in substance: HR2's entire
  schema footprint is the single nested key `gold_star.dimensions[].scd_type`
  -- verified directly against all three sibling in-flight
  `source-map.yaml`-touching features that DO already exist in this tree
  (090 adds `meta.freshness`, 103 adds `columns[].unit`/`columns[].currency`,
  105 adds a wholly separate template file) -- none collide with
  `gold_star.dimensions[]` (this review independently confirms analysis.md's
  F3 substance-check: the allocation holds even though the spec's prose
  claiming those directories "do not exist yet" is stale -- see Notes).

Verdict: **PASS**. Scope is disciplined and actively resists multiple
plausible scope-creep paths (Type-2 authoring, an invented approval shape, a
new readiness stage) rather than merely avoiding them by omission.

## Notes / carry-forward (non-blocking)

- **F1 (from analysis.md, independently re-confirmed) -- FR-008/C7
  multi-match migration handling has no covering task.** spec.md FR-008 and
  Clarification C7 require that if the `warehouse/migrations/*create_gold_
  <table>_star.sql` glob matches MORE than one file for a table, HR2 emits a
  single fail-closed ERROR naming the table and every matched filename.
  Tracing tasks.md directly: T027's declared helper signature
  (`_find_gold_migration(ctx, table_id) -> str | None`) has no return shape
  for "2+ matches"; T030 (the wiring task) branches only on `None` vs.
  present; T025 (the RED test task) asserts exactly three outcomes (ERROR
  for type_2+drop-rebuild, zero findings for type_1, zero findings for
  absent migration) with no multi-match assertion; no Phase 4 fixture
  creates two migration files matching the same glob. This is a genuine
  task-list under-implementation of an already-correct spec requirement --
  not a spec defect and not a fail-open outcome in the DESIGN (FR-008 itself
  correctly requires fail-closed), but if tasks.md is executed exactly as
  written, the 2+-match branch of FR-008 will not be built. No committed
  table today has more than one matching migration, so nothing fails open on
  the CURRENT tree, but this must be fixed before or during implementation --
  add a fixture pair (two migration files for one table id) and extend
  T027/T030's signatures and T025's assertions to cover it.
- **F2 (from analysis.md, independently re-confirmed) -- C6 placeholder
  routing (`""`/`null`/`"tbd"` -> FR-005, not FR-006) has no covering task and
  T018 as literally worded would misroute it.** spec.md Clarification C6
  requires an empty string, `null`, or case-insensitive `"tbd"` value to
  route to FR-005's Needs-decision finding (same remedy as a missing key),
  not FR-006's invalid-value finding. T018's stated condition ("for each
  dimension whose `scd_type` is present but not exactly `type_1` or
  `type_2`, emit `Finding(HR2, ERROR, ...)` naming the dimension and the
  literal value seen") contains no placeholder-exclusion clause -- as
  literally worded it is also true for `scd_type: ""`, `null`, and `"tbd"`,
  which would produce the exact confusing "invalid value: ''" message C6
  says to avoid. T034 is explicitly scoped to "no key at all" and does not
  cover the present-but-placeholder case; no fixture in T032 exercises it.
  Both outcomes remain `Severity.ERROR` regardless of which branch fires, so
  this does NOT fail open and does NOT violate Principle I -- it is a
  finding-message/routing-fidelity gap, not an enforcement gap. Fix before
  or during implementation: add a placeholder-exclusion clause to T018's
  condition (or an explicit placeholder-detection branch ahead of it feeding
  into T034's Needs-decision path) and extend T032/T033's fixtures/tests to
  cover `""`, `null`, and `"tbd"` explicitly.
- **F3 (from analysis.md, independently re-confirmed, Low/non-blocking) --
  spec.md's claim that sibling directories 090/103/105 "do not exist yet in
  this tree" is stale.** Direct check confirms all three already exist with
  full artifact sets (`specs/090-source-freshness-gate/`,
  `specs/103-currency-unit-contract/`,
  `specs/105-source-data-contract-restatement/`). The SUBSTANTIVE
  collision-avoidance claim still holds -- independently verified against
  each sibling's own FR-001, none touch `gold_star.dimensions[]` -- so this
  does not affect `scope_ok` or any axis verdict above. Cosmetic only; worth
  a one-line correction to spec.md's Overview/Boundary section during
  implementation so the prose does not read as factually wrong to a future
  reader, but not a build-blocking item.
- **Keep T039's grep a hard gate, not a courtesy check.** The only realistic
  c086-leak vector this feature could introduce is copying the real
  `gold.dim_customer_rss`/`gold.dim_product_rss` names from research.md's/
  data-model.md's evidentiary prose into the shipped `rule_hr2.py` docstring,
  a fixture's naming, or the `templates/source-map.yaml` edit itself. T039
  is positioned to catch this at build time -- keep it in the task list as a
  hard gate through Phase 6.
- **The rule-count claim (55 -> 56) is a live serialization point shared with
  HR1/087.** Verified 55 as of this review; both plan.md and tasks.md (T002)
  already correctly hedge that 087/HR1 may land the same slot first and
  change the number the implementer must target. No action needed beyond
  honoring the plan's own instruction to re-verify live at implement time.
- **FR-017 stays genuinely open.** No task in tasks.md answers
  Q-APPROVAL-SEAM; T044 is explicitly a "do not answer" checklist
  confirmation. This is correct and should stay this way through
  implementation -- any future edit that adds an `approvals[]` shape for
  `scd_type` without an owner ruling would flip Axis 1 to a violation.
- **The RED-landing precondition is a real, accepted cost, not a bug to
  "fix" during implementation.** T041 explicitly forbids asserting a clean
  full-repo `retail check` run after HR2 lands, and no task may add a real
  `scd_type` value to either committed map (tasks.md header warning). An
  implementer under schedule pressure could be tempted to "just fill in
  `type_1` everywhere" to make the gate green -- that would be exactly the
  Principle-V violation this feature exists to forbid. Flag this loudly in
  code review of the implementation PR.

## Verdict

**Verdict**: PASS-WITH-NOTES

All five axes clear on direct ground-truth verification (rule count, HR1
non-landed status, HR2 id freedom, and the committed gold migration's actual
shape were independently checked against the live tree, not merely taken from
the plan's self-report). The design is notably disciplined: it accepts a
deliberate RED landing on the live tree rather than manufacture a false green
by scaffolding a Principle-V ruling, and it actively refuses several plausible
scope-creep paths (Type-2 authoring, an invented approval shape, a new
readiness stage) rather than merely avoiding them by omission.

The carry-forward notes are non-blocking but material: F1 (FR-008/C7
multi-match migration handling has no covering task) and F2 (C6 placeholder
routing has no covering task and T018 as worded would misroute it) are two
concrete task-list under-implementations of already-correct spec text --
both already surfaced by analysis.md and independently re-confirmed here.
Neither fails open (both misrouted/unimplemented cases still land as
`Severity.ERROR` or, in F1's case, undefined-but-not-silently-passing
behavior on a case that does not exist on the current tree), so neither
constitutes an axis FAIL or a blocking finding -- but both must be fixed in
tasks.md (or caught during implementation) before this feature can honestly
claim FR-008 and FR-005/FR-006 are fully built. F3 is a one-line cosmetic
staleness fix. No CRITICAL or HIGH finding; no axis is RISK or FAIL.
