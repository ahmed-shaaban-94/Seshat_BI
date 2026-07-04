# Second-Pass Adversarial Review (Opus): Date-Spine Completeness Static Gate (HR8)

**Feature**: `094-date-spine-completeness` (gap #17) | **Date**: 2026-07-05
**Reviewer stance**: INDEPENDENT senior external reviewer, second pass, default-adverse,
READ-ONLY. This is the stronger second opinion over the Sonnet stage-6 `plan-review.md`
(which returned PASS-WITH-NOTES). Artifacts read in full: spec.md, plan.md, tasks.md,
research.md, data-model.md, quickstart.md, plan-review.md. **`analysis.md` does NOT exist**
in this feature directory (`speckit-analyze` was not run for 094) -- recorded as a
non-blocking note, matching the 087/HR1 precedent; direct ground-truth verification is
substituted below.

## Ground truth I re-verified myself (not trusting the plan's or Sonnet's self-report)

- **S7 does exactly what the Boundary claims.** `s7_contiguous_date_dim`
  (`src/retail/rules/sql.py:503-544`) checks `has_distinct and not has_genseries` only
  (`:531`); it never reads the `generate_series` call's arguments. Severity WARNING
  (`:535`). HR8's target gap is real, not invented.
- **`Severity.INFO` exists and is non-blocking.** `src/retail/core.py:21`
  (`INFO = "info"  # informational only`); one shipped rule already emits it
  (`src/retail/rules/git_meta.py:168`). FR-007 invents no new tier.
- **The two-utility split (Clarifications Q1) is correct against source.** `tokenize_sql`
  collapses string literals to an empty placeholder (`src/retail/sql.py:113`,
  `SqlToken("", line)`); `strip_sql_comments` "keeps `'...'` literals ... intact"
  (`src/retail/sql.py:135-152`). So `tokenize_sql` genuinely cannot supply the step/bounds
  literal text FR-003/FR-005 classify, and `strip_sql_comments` genuinely can. The split is
  a real feasibility constraint, correctly resolved.
- **The shipped worked-example migration is clean under HR8.**
  `warehouse/migrations/0004_create_gold_retail_store_sales_star.sql:107` reads exactly
  `generate_series(DATE '2022-01-01', DATE '2025-01-18', INTERVAL '1 day')` -- daily step,
  chronological literal bounds. It is the ONLY committed migration with a
  `dim_date` + `generate_series` build (grep across `warehouse/migrations/` confirms).
- **S4b emits ERROR+WARNING, NOT ERROR+INFO** (`src/retail/severity_posture.py:6, 104-106,
  228`). So plan.md's "S4b precedent" for the `["error","info"]` shape is imprecise, as
  Sonnet flagged.
- **The severity-posture harness observes by forcing each rule over synthetic input**
  (`severity_posture.py:1-16`), so an unhandled id records a no-finding marker -- T007's
  "add a real `elif rule_id == "HR8":` branch, not just JSON regen" is correct.

### The one fact BOTH the plan AND the Sonnet review got the citation wrong for (I re-derived it)

SC-001/SC-006 assert the shipped tree stays green after HR8 lands even though FR-007 fires
an INFO on 0004. Sonnet cited `src/retail/cli.py:713` and `:995` as proof the "gate keys
strictly on `Severity.ERROR`." **Those two lines are the LIVE paths**: `:713` is inside
`_run_validate` (705-716: "pip install 'retail[db]'", "all live checks passed"); `:995` is
inside `_run_value_check` (960-1002: "L4 value checks"). Neither is the static `retail
check` path. The static `check` command delegates to `run(all_rules(), ctx)`
(`cli.py:333`), whose exit code is computed in `src/retail/runner.py`:

- `_exit_code` (`runner.py:79-81`): `"1 if any ERROR finding is present, else 0
  (WARNING/INFO never fail)."`
- `run` (`runner.py:84-98`): prints every finding via `_format`, sets `exit_code = 1` only
  `if finding.severity is Severity.ERROR` (`:96-97`).

**Conclusion is the same as Sonnet's (INFO never fails the static gate, SC-001 holds), but
the load-bearing evidence Sonnet cited was on the wrong subcommand.** A second pass earns
its keep here: the correct SC-001 citation is `runner.py:79-98`, not `cli.py:713/995`.
This is a note, not a blocker -- the actual static gate genuinely exits ERROR-only.

---

## Axis 1 -- hidden-principle-violation: **RISK** (framing accuracy only; NOT a hidden violation)

Probe: does HR8 secretly self-grant an approval, decide a Principle-V judgment call
(grain/PII/business-policy/who-approves), or advise-instead-of-block?

- **No self-grant, no advise-instead-of-block.** HR8 reads only committed migration text,
  emits `Finding` objects, writes no migration / `source-map.yaml` key / readiness-status
  entry (FR-009), records no `approvals[]`, moves no stage. Every proven-defect branch
  (FR-003 non-daily step, FR-004 unclassifiable step, FR-005 reversed literal bounds) is
  `Severity.ERROR` -> non-zero static exit (verified `runner.py:96-97`). There is no
  warn-only escape hatch on any of the three defect cases, so Principle I (fail CLOSED) is
  satisfied, not violated.
- **The daily-grain question, adjudicated head-on.** The spec's Principle-V-avoidance rests
  on "every shipped date-dimension surface in this repo already presupposes a
  one-row-per-day calendar ... so no Principle-V ruling is needed" (Assumptions;
  Clarifications). Traced against its own citations: `docs/readiness/gold-ready.md` says the
  date dim must be "contiguous" via `generate_series`, NOT "daily"; S7's code checks builder
  choice only, never step. So the strongest direct evidence for "daily is already settled"
  is narrower than the blanket prose: the single shipped worked example happens to use
  `INTERVAL '1 day'`, and daily is the near-universal date-dimension default the toolchain
  (S7, V-RC15, marked-date-table validation per S8) presupposes. HR8 is the first artifact
  to elevate "daily step" into a hard fail-closed gate.

**Where I DISAGREE with Sonnet (emphasis, not conclusion).** Sonnet framed this as "HR8 is
minting a new, narrow, fail-closed BUSINESS RULE about calendar grain ... the spec's
Principle-V avoidance is thinner than stated." I think that overstates it in the wrong
direction for *this axis*. This axis is *hidden*-principle-violation, and the daily-grain
move is (a) NOT hidden -- the spec surfaces the tension in Clarifications and pre-registers
the challenge path ("If a future reviewer disagrees ... raise it at `/speckit-clarify`
time"); (b) NOT a self-grant; (c) explicitly authorized by Principle VI
(Defaults-Then-Deviations), which permits fixing a default without a Principle-V ruling;
(d) fail-closed, which Principle I *requires*. Date-dimension daily grain is not a
fact-table grain / PII / business-rollup / who-approves judgment in the Principle-V sense --
it is a modeling default the whole existing surface already assumes. So no Principle-V
judgment call is secretly being made.

The genuine defect is narrower than either "hidden violation" or "minting a business rule":
the spec's PROSE OVERCLAIMS. "Enforcing an existing convention, not inventing a new one" and
"no default is even being set" are inaccurate -- a default *is* being set (daily), and the
one shipped instance is the only direct evidence for it. The honest, fully-supportable
framing is: *"daily is the enforced default under Principle VI; the one shipped instance is
daily; a future non-daily reporting mart would carry a deviation via its own spec."* The
behavior is sound; only the wording overreaches.

**Verdict: RISK on framing accuracy. Explicitly NOT a hidden-principle violation and NOT a
blocker.** Recommend softening the Assumptions/Clarifications prose to the Principle-VI
default-setting framing above before ratification.

## Axis 2 -- assumes-deferred-capability: **PASS**

- HR8 is 100% static: reads only `iter_sql_files(ctx)` / `ctx.tracked_files` (the S1-S8
  universe), opens no DB, invokes no execution adapter (FR-001, FR-006). No `validate.py`
  import appears anywhere in the described footprint; T034 is a source-inspection test that
  mechanically forbids it.
- F016 (Power BI execution adapter) is never invoked or assumed; no live Power BI/PBIP
  surface is read. Research.md's "Deferred capabilities NOT assumed" section names F016,
  live DB/V-RC15, non-daily grain, and auto-fix as explicitly out of scope.
- Live row-level coverage is deferred to V-RC15 with an explicit `Severity.INFO` PENDING
  marker (FR-007) -- the correct Principle VIII posture (author static, mark live PENDING),
  not a silent assumption that a live run will happen.
- `Severity.INFO` working as a non-blocking output is verified live (`core.py:21`,
  `runner.py:80-81`), so FR-007 assumes no unshipped mechanism.

No deferred capability is assumed. PASS -- I concur with Sonnet.

## Axis 3 -- c086-leak: **PASS**

- HR8 keys only on the generic `dim_date`-prefix convention S7 already uses (FR-002,
  FR-014); no worked-example table/column name is a required literal in matching or
  classification logic (SC-007). `gold.dim_date_rss` (the real dim name) still matches the
  generic `startswith("dim_date")` test -- same precondition, no new hardcoding.
- Real names (`retail_store_sales`, `0004_create_gold_...`) appear only as CITATIONS of the
  committed file for mutation-verification (SC-001, US1 AS-3), never inlined into rule logic.
  T035 is a dedicated grep guard.
- No new manifest/template/declaration file is introduced (FR-010), so there is no new
  authoring surface for a copy-pasted real name to leak into -- a smaller leak surface than
  087/HR1's `conformed-dimension-map.yaml` scaffold.

PASS -- I concur with Sonnet.

## Axis 4 -- fabricated-confidence: **PASS**

- HR8 reuses the unchanged `Finding(rule_id, severity, message, locator)` dataclass
  (`core.py:24-29`) -- no numeric field added. FR-008 forbids any score / "N of M" /
  "% covered" tally; FR-007 forbids coverage-proof language ("covers", "complete",
  "gap-free").
- Two DEDICATED mechanical verification tasks back this, not just a docstring: T027
  (text-content scan of every INFO message for forbidden substrings) and T034
  (source-inspection: no percentage/ratio formatting, no DB call, no `validate.py` import).
- The one integer touched (rule count 55 -> 56) is a `len()`-based authoritative count, not
  a confidence score, and is explicitly re-verify-at-implement-time hedged given the
  19-feature parallel landing race. Correct non-fabrication posture.

PASS -- I concur with Sonnet.

## Axis 5 -- over-scope: **PASS**

- Deliverables are the lightest-footprint rule-add I can construct for this repo: ONE
  `@register`ed function inside the EXISTING `src/retail/rules/sql.py` (no new module, so no
  `__init__.py` edit), NO new manifest/declaration file, NO new `source-map.yaml` key, NO
  new readiness stage. Lighter than 087/HR1 (new module + new manifest), and the plan states
  and defends this comparison correctly.
- FR-010 refuses to touch S7's/V-RC15's body, severity, or message even where a shared-helper
  refactor touching S7 would be tidier; T015/T016 deliberately RE-DERIVE the discovery span
  independently. Genuine scope discipline (minor duplication accepted to avoid a sibling
  rule's surface).
- Does not attempt live coverage (V-RC15's job, FR-006) and does not touch 087/HR1's
  cross-star territory. HR1 has not landed in this worktree (confirmed: no "HR" id in
  `tests/unit/test_rules_wiring.py`), so the cross-boundary claim cannot be checked against
  HR1's real code, but the textual boundary is coherent and non-overlapping. The reserved
  "HR" family letter + id HR8 is the only collision-avoidance allocation, correctly hedged
  for landing order.
- The daily-grain policy nudge (Axis 1) is the sole outward creep, and it is a framing issue
  already homed under Axis 1, not a separate over-scope defect.

PASS -- I concur with Sonnet.

## Axis 6 -- internal-consistency: **RISK** (one real inconsistency neither review named + one citation fix)

Probe: do spec/plan/tasks/data-model cohere -- every FR covered by a task, SCs testable, no
contradiction the analyze pass would have caught (there was no analyze pass)?

**FR -> task coverage is complete.** tasks.md's own "Requirement Coverage Check"
(FR-001..FR-014) maps each FR to >=1 task; I spot-checked FR-003 (T016/T017/T011/T012),
FR-005 (T016/T023/T024/T020-22), FR-007 (T029/T026-28), FR-011 (T005-T010a/T037a/T039) and
they hold. SC-001..SC-007 are each testable and wired (T013/T019, T002/T007/T037a for the
count/severity-posture lockstep, T027/T034 for no-fabrication, T035 for generic). The
severity-posture RED-then-GREEN choreography (T010a intentionally RED at Phase 2, regenerated
GREEN at T037a) is coherent and correctly ordered.

**Inconsistency #1 (NEW -- neither review named it; non-blocking).** The spec applied
anti-fork rigor to the BOUNDS check (Clarifications Q2 deliberately widened literal-date
recognition to TWO spellings, `DATE '...'` AND `'...'::date`, because "an implementer who
recognizes only one creates a behavioral fork" -- a fail-*open* risk it correctly closed).
But the STEP check (FR-003/FR-004) recognizes daily ONLY as `INTERVAL '1 day'`. A perfectly
valid daily step written in the OTHER PostgreSQL cast idiom -- `'1 day'::interval` -- is not
a literal `INTERVAL` expression by FR-003's text, so it falls into FR-004 "unclassifiable"
and gets a **fail-closed ERROR on correct input**. The spec's own Q2 reasoning ("recognize
the spellings already present in this repo, or you fork behavior") was applied to bounds but
not to the symmetric step case. This is a genuine internal inconsistency between Q2's
principle and FR-003's implementation. It is **non-blocking**: (a) no committed migration
uses cast-form step (0004 uses `INTERVAL '1 day'`), so SC-001 is unaffected; (b) the failure
mode is fail-CLOSED on valid input (a false ERROR an author can rewrite), not the fail-OPEN
hole Q2 fixed for bounds, so it is safe under Principle I. Recommend either (i) FR-003 also
recognize `'1 day'::interval` for symmetry with Q2, or (ii) the spec explicitly state that
step must be written in the `INTERVAL '...'` form and cast-form step is deliberately an
FR-004 ERROR (an authoring convention). Either resolves the inconsistency; today the spec is
silent on the asymmetry.

**Inconsistency #2 (citation, non-blocking).** plan.md's Project Structure note and T007's
comment cite "S4b" as precedent for the `["error","info"]` two-severity shape. S4b emits
ERROR+**WARNING** (`severity_posture.py:104-106`), not ERROR+INFO. S4b is valid precedent for
"one rule id emits two severity classes," but the precedent for "INFO is an accepted,
non-blocking static-rule output" is `git_meta.py:168`, which the plan does not cite. Sonnet
already flagged this; I confirm it and additionally note the Sonnet SC-001 exit-code citation
error above (`cli.py:713/995` are live paths; the static gate is `runner.py:79-98`).

**Verdict: RISK.** The artifact set is internally coherent on FR/SC coverage and the
severity-posture choreography, but the STEP-vs-BOUNDS spelling asymmetry (Inconsistency #1)
is a real self-inconsistency the spec's own Q2 rigor should have caught, and two citations
(S4b, and Sonnet's own SC-001 line refs) point at the wrong place. None blocks -- all are
authoring/framing corrections -- but they are exactly the class of thing a second pass exists
to surface.

---

## Where I disagree with the Sonnet stage-6 plan-review.md

1. **Axis 1 emphasis.** Sonnet: "HR8 is minting a new, narrow, fail-closed BUSINESS RULE ...
   Principle-V avoidance is thinner than stated." Me: it is NOT a Principle-V grain decision
   (daily is a modeling default the whole toolchain presupposes, not a fact-grain/PII/policy
   judgment), NOT hidden, and squarely authorized by Principle VI. The defect is narrower and
   different in kind: the spec's PROSE inaccurately claims "no default is being set" when one
   is. Same RISK rating, sharper and more accurate diagnosis -- the fix is a wording
   correction under Principle VI, not a Principle-V ruling.

2. **Sonnet's SC-001 exit-code evidence is cited on the wrong subcommand.** Sonnet leaned on
   `cli.py:713` and `:995` as proof the gate keys strictly on ERROR. Both are LIVE paths
   (`_run_validate`, `_run_value_check`). The static `retail check` exit code is in
   `runner.py:79-98` ("WARNING/INFO never fail"). Conclusion identical (SC-001 holds), but a
   reviewer relying on Sonnet's citation would be looking at the wrong code. Corrected here.

3. **Sonnet's Axis 6 was folded into a clean PASS with no internal-consistency finding.**
   Sonnet ran its six probes but did not surface the STEP-vs-BOUNDS spelling asymmetry
   (Inconsistency #1). I raise Axis 6 to RISK on that ground. It remains non-blocking, but it
   is a substantive coherence gap, not a non-issue.

I do NOT disagree with any of Sonnet's PASS ratings on Axes 2/3/4/5 -- verified independently
and concur. I do not find Sonnet over-flagged anything: its Axis 1 RISK and its two
carry-forwards (missing analysis.md, S4b citation) are all real.

## Verdict

**PASS-WITH-NOTES.**

Five axes clear on direct ground-truth verification (static-only, fail-closed, self-grants
nothing, stays generic, fabricates no score, lightest-footprint rule-add in the batch). Axis
1 is RISK on FRAMING ACCURACY only -- a Principle-VI default is being set and the prose
should say so instead of claiming no default exists; it is disclosed, fail-closed, and NOT a
hidden Principle-V violation. Axis 6 is RISK on a real, previously-unnamed internal
inconsistency: the STEP check recognizes only `INTERVAL '1 day'` while Q2's own anti-fork
logic widened the BOUNDS check to two spellings, so a valid `'1 day'::interval` step would
fail-closed on correct input (safe, but self-inconsistent). Non-blocking carry-forwards:
missing `analysis.md`; the S4b-vs-`git_meta` severity-precedent citation; and the correction
that the SC-001 exit-code proof lives in `runner.py:79-98`, not the live-path lines
`cli.py:713/995` Sonnet cited. No CRITICAL or FAIL finding on any axis; the design's behavior
is sound and ratifiable once the two RISK framing/consistency items are corrected.
