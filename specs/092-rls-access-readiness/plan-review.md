# Adversarial Plan-Review: Row-Level Security as a Semantic-Model-Ready Dimension (HR6)

**Feature**: `092-rls-access-readiness` | **Date**: 2026-07-04
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports findings,
edits nothing). Artifacts reviewed: spec.md, plan.md, tasks.md, analysis.md, plus
research.md, data-model.md, quickstart.md (all present in the feature directory).

**Precondition check**: spec.md, plan.md, tasks.md, and **analysis.md are all
present** (unlike the 087/HR1 and 094/HR8 sibling reviews, where `speckit-analyze`
had not yet been run). analysis.md's own verdict: `scope_ok = true`, 0 constitution
violations, 0 critical issues, 18/18 FRs mapped, 1 MEDIUM contradiction (F1), 1 HIGH
gap (F2), 2 LOW nits (F3/F4). This review does not import that verdict blindly --
it independently re-verifies F1 and F2 against the live tree below (both confirmed
real) and applies its own five-axis adversarial lens on top, which is not the same
question `speckit-analyze` asks.

**Ground truth verified directly against the worktree** (not merely the plan's
self-report):

- Live rule count is **55** (`docs/rules/rules-manifest.json` has 55 `"id"`
  entries; `docs/quality/rule-count-claims.yaml` confirms SC2 reconciles against
  this count) -- consistent with plan.md/tasks.md's implicit "56th rule" framing.
- `grep -rn "HR6" src/ docs/ tests/` returns **nothing** -- HR6 is genuinely
  unused as of this review. However, the "HR" family letter is **not exclusively
  reserved by this feature**: `specs/087-conformed-dimension-readiness/` (HR1)
  and `specs/094-date-spine-completeness/` (HR8) are sibling in-flight specs also
  claiming the same family letter, and neither has landed in `src/` yet (confirmed:
  no `"HR` string anywhere in `docs/rules/rules-manifest.json`). This is a live
  three-way serialization point across parallel features, not a defect unique to
  092 -- but it means "HR6 id free" is a snapshot-in-time fact, not a settled
  allocation, and the plan should be read with that caveat.
- `templates/metric-contract.yaml` verified: its declare/bind/readiness shape
  (identity -> `binds_to: {gold_table, columns}` -> four-status `readiness` block
  with `evidence[]`/`blocking_reasons[]`) is exactly what data-model.md's Entity 1
  mirrors for the role contract (`filter: {gold_table, column}` in place of
  `binds_to`). The precedent citation is accurate, not aspirational.
- `src/retail/rules/g6.py` verified as the shape precedent tasks.md cites for
  `hr6.py`: a pure `RuleContext -> Iterable[Finding]` function,
  `@register("G6", ...)`, `Severity.ERROR` only, `locator=f"{rel}:{lineno}"`
  style, a private `_iter_*_files(ctx)` helper that filters `is_test_path()`.
  `src/retail/rules/readiness_status.py:174` confirmed to carry the exact lazy
  `import yaml  # lazy: keep retail check import path stdlib-light` comment
  tasks.md T006 says it mirrors -- both precedents are real, not invented.
- `docs/readiness/semantic-model-ready.md` verified: its "Required checks" table
  currently lists only `D1-D11, C1, R1, G6`; HR6 is genuinely absent today,
  confirming the gap FR-017/T005 target is real, not a strawman.
- **F2 (analysis.md, HIGH) independently reconfirmed**:
  `.claude/skills/retail-semantic-check/SKILL.md` line 104 reads verbatim "Any
  `D1`-`D8` ..., `C1` ..., `R1` ..., or `G6` ... finding is a distinct
  `blocking_reason`" -- a hand-maintained, hand-enumerated citation list separate
  from `semantic-model-ready.md`'s own table. No task in tasks.md (T001-T034,
  T033b) touches this file, and plan.md's Project Structure file-footprint list
  does not mention it either. Mechanically the gate still fails closed (an HR6
  `Severity.ERROR` finding makes `retail check` exit non-zero regardless of
  whether SKILL.md names it), so this is not a fail-closed defect -- but a human
  or agent running `retail-semantic-check` and reading its own step-2 interpret
  table would not see HR6 named alongside G6, contradicting FR-011's "the same
  way an existing D1-D11/G6 finding already blocks that stage" claim in its
  fullest sense. Confirmed real; see Axis 5 / Notes.
- **F1 (analysis.md, MEDIUM) independently reconfirmed**: spec.md FR-010's
  "PENDING DEFAULT" prose says "HR6 records the zero-contract state as an
  explicit, visible fact (not a fabricated pass)" -- present tense, describing
  action this slice takes. plan.md's "Zero-contract handling" section and
  data-model.md's Entity 3 both say the opposite for what ships now: "this
  slice's shipped HR6 behavior... does not synthesize any finding for that
  absence." tasks.md's T009 mechanically ratifies the narrower reading (smoke
  test asserts `[]` for zero contracts). Confirmed: the spec's own prose
  overclaims relative to what plan.md/data-model.md/tasks.md actually commit to
  building. See Axis 1.

## Axis 1 -- hidden-principle-violation

Probe: does HR6 secretly self-grant an approval, decide a Principle-V judgment
call, or advise-instead-of-block?

- The core mechanism is read-only and fail-closed by construction: a role
  contract is human-authored (FR-001, data-model.md "Human-authored; the agent
  never fills or self-approves one"); HR6 only reads it and never picks a role,
  a viewer mapping, or the "correct" security column (FR-013). A malformed
  contract is never inferred as valid-by-default -- it is a fail-closed ERROR
  (Entity 3's six-row trigger table, all `Severity.ERROR`, none `WARNING`).
  This is the correct Principle-V shape and matches the F009/G6 precedent this
  feature explicitly cites.
- **The load-bearing question an adversarial reviewer must not wave past**:
  does leaving Q-ZERO-ROLES open actually close the leak the feature's own
  Overview motivates, or does it leave the door open by construction? Traced
  through: a table with **zero** committed `rls-role-contract.yaml` files
  produces **zero** HR6 findings (data-model.md Entity 3, "Explicitly NOT a
  finding trigger"; tasks.md T009's smoke test). No other Stage-5 check
  (D1-D11, C1, R1, G6, the metric-contract binding check) looks for RLS
  presence at all. So a model with genuinely zero declared roles can still
  reach `semantic_model_ready: pass` today, after this feature ships, exactly
  as it could before -- the Overview's own opening claim ("a 'ready' model can
  leak every store's... numbers to every viewer, and nothing in the readiness
  spine records that risk as evidence") remains literally true for the
  zero-contract case even after HR6 lands. This is not a hidden violation --
  the spec is honest that this is deliberately NOT decided (Q-ZERO-ROLES,
  Principle V) rather than silently defaulting to "pass" -- but it means the
  feature closes only HALF of the leak its own motivating narrative describes
  (the malformed-declaration half), and a reader of the Overview alone could
  reasonably expect more closure than what ships.
- The specific overclaim: FR-010's "PENDING DEFAULT" prose states "HR6 records
  the zero-contract state as an explicit, visible fact" in the present tense,
  describing an action. Independently verified (see Ground truth, F1) that
  this slice's actual shipped behavior does the opposite: HR6 "does not
  synthesize any finding for that absence" (plan.md), and T009's own smoke
  test enforces exactly that non-behavior. Both readings are Principle-V-safe
  (neither encodes a silent "pass" nor a silent "block"), so this is NOT a
  hidden self-grant of approval -- but FR-010's prose describes a capability
  ("HR6 records...") that plan.md/data-model.md/tasks.md all agree is
  explicitly NOT built in this slice. An implementer following spec.md alone,
  without cross-reading plan.md's narrower "Zero-contract handling" carve-out,
  could reasonably attempt to build the recording behavior FR-010 describes --
  which would still be Principle-V-safe in outcome (an INFO-tier surfacing,
  per plan.md's own suggested shape) but would be scope the plan/tasks chain
  explicitly declined to commit to, creating exactly the kind of
  spec-says-X/plan-builds-Y drift a Principle-V carve-out must not have.
- No other Principle-V question (grain, PII, business rollup, product
  identity, WHO gets WHICH role) is answered anywhere in the six artifacts;
  FR-013 is respected everywhere else. The fact-table hard-fail (Clarification
  C1) is a rule-severity mechanics choice (`Severity.ERROR` already exists and
  is used elsewhere), not a who-sees-what ruling -- correctly distinguished
  from Q-ZERO-ROLES in the spec's own Clarifications.

Verdict: **RISK**. The mechanism itself is read-only, fail-closed, and
self-grants nothing -- the general shape is sound and matches the F009/G6
precedent. But two related issues keep this from a clean PASS: (1) the feature's
own Overview frames the problem as "a ready model can leak every store's numbers,"
yet the zero-contract case -- arguably the MOST common way a model reaches
`pass` with genuinely no RLS at all -- is left exactly as open after this
feature as before it, which is a legitimate and disclosed Principle-V
deferral, not a defect, but the Overview's framing oversells how much of the
leak this slice actually closes; and (2) FR-010's prose ("HR6 records the
zero-contract state as an explicit, visible fact") describes a capability
this slice's own plan.md/data-model.md/tasks.md all agree is NOT built,
which is an artifact-honesty gap a build could act on incorrectly if it reads
spec.md without also reading plan.md's narrower carve-out. Recommend: (a)
soften spec.md's Overview to note explicitly that the zero-contract case
remains open and is NOT newly closed by this feature (only the
malformed-declaration case is), and (b) reconcile FR-010's "HR6 records..."
present-tense claim with the "this slice emits no finding for absence"
behavior plan.md/data-model.md/tasks.md actually commit to, per analysis.md's
own F1 recommendation. Neither issue is a hidden self-grant; both are
disclosure/honesty gaps in an otherwise Principle-V-safe design. Does not
block proceeding, but should be fixed before or during ratification.

## Axis 2 -- assumes-deferred-capability

Probe: does any artifact assume F016, a live DB, or a running adapter exists?

- HR6 is 100% static: it reads only `ctx.tracked_files` (`mappings/*/roles/*.yaml`)
  and committed `warehouse/migrations/*.sql` text via the existing `sql.py`
  regex-family helpers (research P5, reused not reinvented) -- no database
  connection, no live PBIP/Power BI read anywhere (FR-006, FR-012, FR-018;
  plan.md Technical Context "Storage: N/A at runtime").
- F016 (Power BI execution adapter) is explicitly and repeatedly named as NOT
  existing and never invoked: plan.md's Constitution Check has a dedicated
  "F016 boundary" row; quickstart.md's "What this feature does NOT let you do"
  states "No live preview... HR6 never evaluates a filter against data"; the
  spec's Boundary section makes the same statement a third time. No task in
  tasks.md references a PBIP read, a Power BI connection, or a "view as role"
  action.
- Live cross-check that a role's filter ACTUALLY restricts rows at query time
  is explicitly deferred (FR-018) to a future, unbuilt live-validate surface --
  not stubbed, not TODO'd into `hr6.py`'s body, simply not written, matching
  the correct Principle VIII posture (author static structure, mark PENDING).
- The one place a live read could plausibly sneak in -- the "read gold schema"
  helper (T007, `_read_gold_schema`) -- is specified to reuse
  `iter_sql_files`/regex helpers already used by S6/S8, not a database
  driver or `information_schema` query; no task's file footprint imports a DB
  driver or references a DSN/connection string (T034 explicitly verifies the
  zero-contract `retail check` run does not itself fail the build, without
  touching a live DB).

Verdict: **PASS**. No deferred capability (F016, live DB, running adapter) is
assumed, stubbed, or partially built anywhere across the six artifacts.

## Axis 3 -- c086-leak

Probe: does any template/label bake in domain-specific values instead of
staying generic (Principle VII)?

- `templates/rls-role-contract.yaml`'s shape (data-model.md Entity 1) uses only
  illustrative placeholders (`<RoleName>`, `<dim_table>`, `<column>`) and
  illustrative comment examples (`RegionManager`, `gold.dim_store`, `store_id`)
  explicitly marked as generic examples, not required values -- consistent with
  `templates/metric-contract.yaml`'s own style (`<MetricName>`, "e.g.
  TotalNetSales").
- FR-015/SC-007 explicitly forbid any `retail_store_sales`/C086-specific role,
  column, or table name in the template or the HR6 rule's own source; T031 is
  a dedicated grep-verification task naming specific tokens to check for
  (`dim_location_rss`, `dim_customer_rss`, `fct_sales_rss`).
- T002's fixture gold migration is specified as "modeled on the shape of
  `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql` but with
  wholly generic names (no `_rss`/C086 tokens)" -- this is the one place a real
  worked-example file is cited as a structural template, and the task
  explicitly calls out avoiding the leak, matching the same watch item the
  087/HR1 review flagged for its own manifest-scaffold task.
- Carry-forward note (non-blocking, same pattern the 087 review flagged for
  its own sibling task): the actual leak risk is not in the spec text (which
  stays clean) but in what an implementer pastes into T002's fixture file at
  build time -- if the fixture's column/table names are copy-pasted from the
  real `_rss`-suffixed migration rather than genericized, T031's grep would
  need to catch it retroactively rather than the task having prevented it by
  construction. T031 is positioned as a hard gate, which is the right
  mitigation, but it is a build-time discipline item, not something this
  spec/plan/tasks chain can verify today (the fixture does not exist yet).

Verdict: **PASS**. No c086/retail_store_sales specifics are baked into any
template, rule-source description, or spec/plan/tasks prose; the one
real-file citation (T002's reference to `0004_...rss.sql`) is a structural
precedent citation with an explicit generic-only instruction, not an inlined
leak.

## Axis 4 -- fabricated-confidence

Probe: does any artifact emit a numeric score/health/maturity/completeness
count?

- The role contract's `readiness` block uses exactly the four explicit
  statuses (`not_started | blocked | warning | pass`) plus `evidence[]` and
  `blocking_reasons[]` -- verified identical in shape to
  `templates/metric-contract.yaml`'s own readiness block, which already
  carries no numeric field (FR-014; data-model.md Field Notes table).
- Entity 3's `Finding` reuses the existing, unchanged `Finding` dataclass
  (`rule_id`/`severity`/`message`/`locator`) -- no new numeric field is
  introduced anywhere (SC-004).
- FR-014/SC-004 explicitly forbid any numeric confidence/health/maturity score
  or "N of M" completeness count in the template, the rule's findings, or the
  rule's own source -- and this is backed by a dedicated mechanical
  verification task, not just review discipline: T020
  (`test_hr6_findings_never_carry_a_numeric_score`, grep-style substring
  assertions across every defect fixture's `Finding.message`) plus T032
  (Polish-phase grep across the template, `hr6.py`, and `test_hr6.py` for any
  numeric confidence/health/maturity field name or "N of M" phrasing).
- The one integer touched by this feature -- the rule count (55 -> 56, shared
  serialization point with HR1/HR8) -- is not a conformance/confidence score;
  it is the same `len()`-based reconciliation SC2 already performs against
  `docs/rules/rules-manifest.json`, verified live at 55 before this feature
  lands. Neither spec.md nor plan.md nor tasks.md asserts a specific final
  count as settled fact requiring no re-verification; T028 explicitly
  regenerates the manifest from the running rule set rather than hardcoding a
  target number.

Verdict: **PASS**. No fabricated or invented number anywhere in any of the six
artifacts; the readiness model stays strictly four-status; the one integer
present (rule count) is an authoritative `len()`-based reconciliation, not a
score, and is backed by two independent mechanical grep tests rather than a
docstring promise alone.

## Axis 5 -- over-scope

Probe: does the plan do more than its one readiness-stage job, or cross into
another feature's territory?

- Deliverables are tightly bounded and explicitly enumerated in plan.md's
  Project Structure: one new template file, one new rule module (`hr6.py`),
  one doc-listing edit (`semantic-model-ready.md`), one manifest
  regeneration, one test module, and a NEW-but-precedented subfolder
  convention (`mappings/<table>/roles/`, mirroring the already-shipped
  `mappings/<table>/metrics/` pattern per ADR 0003). No new readiness stage,
  no new top-level `retail check` subcommand (spec Assumptions, plan.md
  Summary, both confirmed against the live `semantic-model-ready.md`, which
  is Stage 5 unchanged in name/number).
- The feature's own "Boundary against neighbouring shipped work" section in
  spec.md is unusually explicit about NOT touching four adjacent surfaces:
  F009's `metric-contract.yaml` (separate file enforced by collision-avoidance
  allocation, T030 grep-verified), F010's `retail-semantic-check` measure-to-
  contract logic (not replaced or duplicated), `retail-govern`'s existing rule
  ids (HR6 is additive only, no renumbering), and RC4/medallion-playbook's
  PII-hiding guidance (not re-litigated, operates "one layer up"). Each
  boundary is traceable to a concrete non-task (no edit to those files in
  tasks.md's file list).
- **Confirmed real, and the one place scope discipline is genuinely
  incomplete rather than merely disclaimed** (independently reconfirmed, see
  Ground truth / F2 above): FR-011 claims HR6 findings surface in
  `blocking_reasons[]` "the same way an existing D1-D11/G6 finding already
  blocks that stage." Mechanically this is true (any `Severity.ERROR` finding
  makes `retail check` exit non-zero, which is the actual gate mechanism).
  But the ARTIFACT that a human or agent reads to interpret WHY the stage is
  blocked -- `.claude/skills/retail-semantic-check/SKILL.md`'s own step-2
  rule-citation table -- hand-enumerates "D1-D8, C1, R1, G6" and is not
  touched by any task in tasks.md or any file in plan.md's Project Structure
  list. This is not an over-scope problem in the sense of doing MORE than the
  feature should -- it is an under-wiring gap in the FR-011 completeness
  claim: the feature stops one file short of where its own "the same way G6
  already does" comparison requires it to reach, since G6 IS named in that
  skill's table and HR6, as currently task-scoped, would not be. This does
  not change the mechanical fail-closed guarantee (the build stays green/red
  correctly either way), but it is a real gap in "the same way" being fully,
  not just mechanically, true.
- No task touches `retail validate`, no task adds a live-database-backed
  check, no task invents a new `approvals[]` shape or readiness-status.yaml
  field beyond appending existing-shape `blocking_reasons[]` string entries
  (Entity 4, confirmed as "not a new schema").

Verdict: **PASS-WITH-NOTE**. The feature's footprint is disciplined and its
explicit "Boundary against neighbouring shipped work" section actively refuses
several plausible scope-creep paths (touching F009's file, re-implementing
F010's logic, re-litigating RC4) rather than merely avoiding them by omission.
The one confirmed gap (SKILL.md's step-2 table not updated) is a completeness
shortfall in an otherwise well-scoped design, not evidence of doing too much --
recorded as a blocking-for-honesty, non-blocking-for-mechanics finding below.

## Notes / carry-forward (non-blocking unless marked)

- **N1 (build MUST honor) -- Reconcile FR-010's "records...as an explicit,
  visible fact" prose with this slice's actual no-finding-for-absence
  behavior.** Independently confirmed (Ground truth, F1 above): spec.md's
  present-tense claim ("HR6 records the zero-contract state...") describes
  action plan.md/data-model.md/tasks.md all agree this slice does NOT take
  (T009's smoke test asserts `[]` findings for zero contracts, full stop).
  Both the "records" reading and the "emits nothing yet" reading are
  Principle-V-safe in outcome, but the spec and its downstream artifacts must
  say the same thing. Recommend editing spec.md's FR-010/Overview/Edge-Cases
  prose to state plainly that THIS slice's HR6 emits no finding for the
  absence case, and that "recording the zero-contract state as an explicit
  fact" (if ever built) is a possible FUTURE slice's INFO-tier addition, not
  this one's shipped behavior -- matching analysis.md's own F1 recommendation
  exactly. This is an artifact-honesty fix, not a behavior change.

- **N2 (build MUST honor) -- Add a task to update
  `.claude/skills/retail-semantic-check/SKILL.md`'s step-2 rule-citation
  table to name HR6 alongside D1-D8/C1/R1/G6**, so FR-011's "the same way an
  existing D1-D11/G6 finding already blocks that stage" claim is fully true,
  not just mechanically true via the shared non-zero-exit path. Confirmed:
  no task in the current tasks.md (T001-T034, T033b) touches this file.
  Matches analysis.md's F2 recommendation exactly; independently
  reconfirmed against the live file content in this review (line 104).

- **N3 -- Soften the Overview's framing of how much of the motivating leak
  this feature actually closes.** The Overview's "a 'ready' model can leak
  every store's... numbers... and nothing in the readiness spine records
  that risk as evidence" remains true for the zero-RLS-contract case even
  after this feature ships (see Axis 1). Recommend one sentence in the
  Overview or Assumptions section making explicit that this feature closes
  the MALFORMED-declaration half of the leak (a role that exists but is
  broken), while the NO-declaration-at-all half stays open pending
  Q-ZERO-ROLES -- so a reader does not come away believing the leak
  described in paragraph one is fully closed by paragraph forty.

- **N4 -- Keep T002's fixture migration genuinely generic at build time, not
  merely generic in the spec's description of it.** The only realistic
  c086-leak vector this feature could introduce is copy-pasting real
  `_rss`-suffixed table/column names from `0004_create_gold_retail_store_
  sales_star.sql` into the new fixture instead of genericizing them. T031's
  grep is correctly positioned to catch this, but only at Polish time --
  keep it as a hard gate through implementation, matching the same watch
  item the 087/HR1 review flagged for its own manifest-scaffold task.

- **N5 -- The "HR" family letter is a live three-way serialization point,
  not an HR6-specific settlement.** Confirmed: 087 (HR1) and 094 (HR8) are
  both in-flight sibling specs claiming the same family letter as of this
  review, and none of the three has landed in `src/` yet. This is disclosed
  correctly by none of the three plans assuming exclusive ownership of the
  letter, but the implementer should re-verify `HR6` (and the family list)
  against the live manifest immediately before registering the rule, since
  another sibling could land first.

- **F3/F4 (analysis.md, LOW, non-blocking, re-confirmed but not re-litigated
  here)**: T014's self-contradicting `[P]` marker (task-id says parallel, its
  own prose says it is not) and the informal "gold dimension table" phrasing
  vs. the literal `^gold\.\w+$` + `dim_`-prefix regex (fully resolved within
  data-model.md's Field Notes table, a readability nit only). Both are
  correctly rated LOW by analysis.md; this review does not find either to be
  understated.

## Verdict

**Verdict**: PASS-WITH-NOTES

Four of five axes clear cleanly on independent ground-truth verification, not
merely the plan's self-report: the mechanism is 100% static (Axis 2), stays
generic with no C086 leak (Axis 3), fabricates no score anywhere and backs
that guarantee with two mechanical grep tests (Axis 4), and is tightly scoped
with an unusually explicit self-imposed boundary against four adjacent shipped
features (Axis 5, PASS-WITH-NOTE for one confirmed under-wiring gap). Axis 1 is
marked RISK, not PASS, because tracing the feature's own motivating claim
against what it actually ships reveals the zero-RLS-contract case -- arguably
the single most common way a "ready" model carries no row-level security at
all -- is left exactly as open after this feature as before it (a legitimate,
disclosed Principle-V deferral, not a hidden default), while spec.md's FR-010
prose describes an active "recording" behavior for that case that
plan.md/data-model.md/tasks.md all agree is explicitly NOT built in this
slice. Neither issue is a hidden self-grant of approval or a silent
who-sees-what ruling -- the design is Principle-V-safe in outcome -- but the
spec's own framing overclaims what this slice closes, and its own FR-010 text
disagrees with its own downstream artifacts about what ships. This repeats
(and independently reconfirms) analysis.md's F1 finding, read here through the
adversarial axis lens rather than the cross-artifact-consistency lens.

Two build-must-honor notes carry forward, both independently reconfirmed
against the live tree in this review (not merely cited from analysis.md):
N1 (reconcile FR-010's "records...as an explicit fact" prose with the actual
no-finding-for-absence behavior this slice ships) and N2 (add a task to
update `.claude/skills/retail-semantic-check/SKILL.md`'s step-2 table to name
HR6, since G6 is named there and HR6, as currently task-scoped, is not).
Neither N1 nor N2 changes the mechanical fail-closed guarantee (an HR6 ERROR
finding already makes `retail check` exit non-zero regardless of either gap),
which is why this verdict is PASS-WITH-NOTES rather than FAIL -- but both
should be resolved before or during implementation for artifact honesty (N1)
and gate-interpretation completeness (N2). No axis reached FAIL; no CRITICAL
finding blocks proceeding to `/speckit-implement`.
