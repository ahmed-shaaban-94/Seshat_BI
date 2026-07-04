# Opus Second-Pass Adversarial Review: Golden/Regression Tests for Generated DAX & SQL (100)

**Date**: 2026-07-05 | **Branch**: `100-generated-artifact-golden-tests`
**Reviewer stance**: independent senior external reviewer, default-adverse, READ-ONLY.
**Relation to first pass**: this is the SECOND opinion over the Sonnet stage-6 `plan-review.md`
(which returned **FAIL**). I read every artifact (spec/plan/tasks/research/data-model/quickstart),
ground-checked the load-bearing claims against source, and judge on SIX axes (the sixth,
internal-consistency, is the axis the Sonnet pass explicitly did NOT run).

**Headline**: I **DISAGREE with the Sonnet FAIL** and downgrade to **PASS-WITH-NOTES**. The
sole basis of Sonnet's FAIL -- a missing `analysis.md` -- is real but is NOT blocking under this
chain's own established practice for exactly-comparable features (see the Disagreement section).
Every content axis is a grounded PASS; the one axis Sonnet skipped (internal-consistency) I ran
myself and it is PASS with two minor map imprecisions.

---

## Grounding performed (not asserted -- verified against source in this worktree)

- **FR-002 call shape** matches `src/retail/cli.py::_run_generate` VERBATIM (read lines ~1035-1040):
  `generate_measure(contract.get("definition") or {}, name=name, doc_intent=contract.get("formula_intent"))`
  with `name = contract.get("name")`, no `format_string`/`display_folder` override. Spec, plan,
  data-model, and research all reproduce this accurately.
- **`GenResult`** (`src/retail/dax_gen.py:19-53`) is a frozen dataclass with fields
  `ok, dax, tmdl_block, reason, warnings` exactly as the spec/data-model describe; its
  `__post_init__` enforces the refusal invariants (`dax`/`tmdl_block` None on refusal) that
  data-model.md relies on for the refusal test. No live adapter, DB driver, or Power BI import
  anywhere in the module.
- **`generate_measure` signature** (`dax_gen.py:206-243`) matches: keyword-only `name` (required,
  raises on empty), optional `format_string`/`display_folder`/`doc_intent`.
- **Fixture corpus exists on disk** exactly as the Assumptions section fixes it:
  `tests/fixtures/contracts/{base_revenue,ratio_disc,refuse_no_column}.yaml`;
  `warehouse/migrations/{0003_create_silver_retail_store_sales,0004_create_gold_retail_store_sales_star}.sql`.
  `tests/fixtures/golden/` does NOT yet exist (correct -- this feature creates it; T005).
- **Refusal reason is stable/pinnable**: `refuse_no_column.yaml` (kind base, sum, source has no
  `column`) routes through `_emit_base` (`dax_gen.py:93-94`) which returns the deterministic string
  `aggregation 'sum' requires source.column`. A golden `reason.txt` over this is stable, not
  environment- or path-dependent. FR-003 is implementable as specified.
- **C086 data authorization**: fixture contents (`total_spent`, `gold.fct_sales_rss`,
  `discount_applied`) are C086 worked-example values. FR-010 explicitly cites them as a filled
  instance per Principle VII -- authorized, not leaked.

---

## Axis 1 -- hidden-principle-violation: **PASS**

No self-grant, no Principle-V resolution, no advise-instead-of-block.

- The spec raises no grain/PII/business-policy/approval question and then quietly answers it. There
  is no readiness-stage transition anywhere in this feature's surface: it writes no
  `readiness-status.yaml`, requests no approval, records no `unresolved-questions.md` entry. The
  Assumptions section ("requires no named-human approval and raises no Principle-V judgment call")
  is accurate -- locking already-approved, already-committed output against silent drift is
  mechanical.
- The tests fail CLOSED, consistent with Principle I: FR-007 (mirrored by T009/T014) requires an
  explicit failure naming the missing/unreadable golden path -- never a `pytest.skip`, never a
  pass-by-default. This is "block," not "advise."
- Critically, the plan does NOT overclaim gate coverage. Its Constitution Check states the scope
  precisely: "Demonstrability here means 'run `pytest -m unit`,' not 'run `retail check`.'" An
  over-reaching spec would have blurred this to claim `retail check` authority it (correctly, per
  FR-001) does not add. The precision is itself evidence against a hidden violation.

I do NOT treat the missing `analysis.md` as an axis-1 principle violation (Sonnet filed it under
axis 1). It is a process-artifact gap, addressed in the Disagreement section below, not a hidden
self-grant or judgment-call resolution in the text.

## Axis 2 -- assumes-deferred-capability: **PASS**

- FR-005 forbids any DB connection, live Power BI/PBIP surface, F016 (execution adapter), or
  F031-F033 (spec-only runtimes). SC-003 requires the full suite to pass with no DB connection and
  no environment variable set. research.md's "Deferred capabilities NOT assumed" section names
  F016, live Postgres, F031-F033, and the `retail-build-warehouse` skill EXECUTION explicitly and
  states each is untouched.
- Verified: `dax_gen.py` imports no adapter; the two migration `.sql` files are read as TEXT
  (T013), never executed, never connected to. User Story 2 is correctly framed as a REGRESSION
  LOCK on committed text (no `build_warehouse(source_map)` callable exists), not a symmetric
  regenerate-and-compare golden. That asymmetry is inherent to the two generators' natures, not a
  deferred-capability assumption. T015 asserts the SQL test opens no DB and invokes no skill/CLI.

## Axis 3 -- c086-leak: **PASS** (one honest residual, non-blocking)

- FR-010 invokes Principle VII's own mechanism correctly: the fixtures ARE the cited filled C086
  instance, not a genericity target. The two test MODULES are generic (iterate a fixture-stem list
  and a filename-pair list); nothing about "sales"/"discount"/"retail" is hardcoded into the
  comparison LOGIC, only into the fixture DATA and file names -- which is the citation FR-010
  authorizes.
- RESIDUAL (LOW, non-blocking): the golden `.txt`/`.sql` fixture CONTENTS unavoidably carry
  C086-specific identifiers, and no SC scans fixture contents for domain leakage the way SC-006
  scans for scores. This is correct and expected: FR-010 declares these the cited instance; the
  alternative (a synthetic non-C086 corpus) is explicitly rejected by the Assumptions section. Note,
  not finding -- same shape as the 046 review's own axis-3 residual.

## Axis 4 -- fabricated-confidence: **PASS**

- Every comparison is a binary string-equality (pass/fail with a text diff) -- never a score,
  percentage, or partial-credit value. FR-012 + SC-006 forbid any numeric confidence/health/
  maturity score or "N of M" tally; T025 is a dedicated grep-for-scores polish task.
- The numeric Success Criteria (SC-003 "100% pass," SC-004 "0 flake," SC-005 "byte-identical,"
  SC-006 "0 scores") are counts/binaries about the TEST SUITE's own behavior, not a fabricated
  readiness/maturity score about the feature or codebase. No `readiness-status.yaml` is touched.

## Axis 5 -- over-scope: **PASS**

- File footprint is exactly two new test modules (`tests/unit/test_dax_golden.py`,
  `test_warehouse_sql_golden.py`), a new `tests/fixtures/golden/` subtree, and one optional
  standalone script. No task edits `dax_gen.py`, `metric_drift.py`, the `retail-build-warehouse`
  skill, `rules-manifest.json`, `severity-posture.json`, `cli.py`, or any existing test file
  (FR-009; T022/T023/T024 verify byte-identity).
- No `retail check` rule, no rule-id, no manifest/severity-posture entry (FR-001; SC-005). This is
  the collision-avoidance allocation the brief demanded (pytest-over-fixtures only), honored.
- The one mutation vector (the optional regeneration script, FR-008/T019) is tightly bounded: T020
  confirms it is not pytest-collected, not wired into the `retail` CLI or `retail check`, not
  referenced by CI, and contains no `git add`/`git commit`. Correct shape for a human-reviewed
  convenience tool, not new runtime authority.
- research.md actively rejected two scope-expanding options (a new `retail check` rule for the SQL
  lock; a CLI subcommand for the regeneration helper) -- scope discipline exercised, not merely
  claimed.

## Axis 6 -- internal-consistency: **PASS** (this is the axis Sonnet did NOT run; I ran it)

Because `analysis.md` (the dedicated cross-artifact consistency artifact) is absent, I performed
the FR-to-task walk myself rather than trusting the self-authored FR Coverage Map at the foot of
tasks.md.

- **All 12 FRs are covered by at least one task.** FR-001->T005/T024; FR-002->T002/T007/T010/T012;
  FR-003->T008/T011/T012; FR-004->T004/T013/T016/T017/T018; FR-006->T006/T007/T008/T013;
  FR-007->T009/T014; FR-008->T019/T020/T021; FR-009->T001/T020/T022/T023; FR-010->T003;
  FR-011->T010/T011/T016/T017/T026; FR-012->T025. No orphan FR, no orphan task.
- **All 6 SCs are testable.** SC-001/SC-002 map to the two Independent Test procedures (quickstart
  steps 2-3); SC-003 to quickstart step 7 (env-unset run); SC-005 to T024/quickstart step 6;
  SC-006 to T025.
- **Spec/plan/tasks/research/data-model/quickstart cohere** -- no contradiction found across the
  set. The call shape, the fixture list, the golden directory layout, the FR-006 algorithm, and
  the P1/P2/P3 story split are stated identically in every document.

Two MAP imprecisions (both cosmetic; coverage itself is real -- NOTE, not FAIL):
- **FR-005 map imprecision**: the FR Coverage Map maps FR-005 -> **T015 only**, but T015 is
  US2-scoped (`test_warehouse_sql_golden.py`). The US1 DAX module's "no DB / no F016" guarantee
  actually rides on **SC-003 / T027** (quickstart step 7's env-unset run), not T015. Coverage
  exists; the map row is under-inclusive. Fix: add T027 to the FR-005 row.
- **SC-004 has no dedicated task**: "0 flake between CRLF and LF checkout" is satisfied BY
  CONSTRUCTION (the FR-006 `\r\n`->`\n` + single-trailing-`\n`-strip normalization in T006, applied
  in T007/T008/T013) and only exercised via the quickstart bundle in T027, not a standalone
  CRLF-vs-LF task. This is acceptable -- normalization makes a dedicated dual-checkout test
  redundant -- but it is "satisfied by construction," not "tested directly." Note it so a future
  reader does not mistake it for a gap.

---

## Where I DISAGREE with the Sonnet stage-6 plan-review.md

### Disagreement 1 (verdict-flipping): the missing `analysis.md` is NOT a blocking FAIL

Sonnet's verdict is **FAIL**, resting entirely on Finding R1: `analysis.md` is absent, therefore
the `/speckit-analyze` cross-artifact consistency stage was never run, therefore (citing the 046
review's "a draft missing analyze... would be automatic BLOCKED") the feature is blocked.

I disagree on the **precedent framing**, which is selective. Sonnet argues "every plan-reviewed
feature 041-068 carries an analysis.md" and treats 069/070/087/094/095 as a "later change in chain
practice" that does not count. But 094 and 095 are the NEAREST comparables to 100 by every relevant
measure: they carry the *identical* artifact set (spec + plan + tasks + research + data-model +
quickstart, and NO analysis.md), and I verified their verdicts directly:

- **094 plan-review.md**: overall **RISK** (not FAIL); the missing analyze is recorded as a note --
  "there is no cross-artifact analyze verdict to cite."
- **095 plan-review.md**: overall **PASS**; same note -- "analyze... has not been run for 095, so
  there is no cross-artifact analyze verdict to cite."

So the chain's OWN practice for exactly-shaped features is to record the missing analyze as a
non-blocking note and let content stand on its own -- not to auto-FAIL. Sonnet reached the opposite
conclusion by excluding the two nearest comparables and anchoring on 046 (a feature that DID have
analysis.md and is therefore silent on how to treat its absence). The 046 quote ("automatic
BLOCKED") describes 046's self-standard, not a chain-wide rule that survived to the 094/095 era.

The **substantive** purpose of analysis.md -- cross-artifact consistency -- is not left unchecked
here: it is precisely axis 6, which this second pass runs directly (above) and finds PASS. With the
consistency check actually performed and clean, blocking the feature for the missing *artifact*
would be blocking on a process formality whose content the review has already supplied. That is the
opposite of Principle I's "demonstrable, not asserted": the consistency IS demonstrated here.

**My resolution**: record the missing `analysis.md` as a NOTE (recommend running `/speckit-analyze`
and committing it for chain hygiene, matching 094/095), NOT as a blocker. Verdict downgrades from
FAIL to PASS-WITH-NOTES.

### Disagreement 2 (minor): Sonnet's clean content pass is correct but under-verified on axis 6

Sonnet reviewed five axes and explicitly did not run internal-consistency ("it reviews the same
three documents from a different angle (principles, not internal consistency)"). That is a
reasonable division of labor, but it means Sonnet's "content is clean" rests on the self-authored FR
Coverage Map it did not independently walk. I walked it (axis 6 above) and it holds -- but with the
two map imprecisions Sonnet's pass could not have surfaced. So I AGREE with Sonnet's content
conclusion while noting it was reached without the check that would have caught FR-005's map row.

### Agreements with Sonnet (I concur, no dispute)

- Axes 2-5 content: PASS, well-grounded. I re-verified independently and reached the same result.
- N1 (regeneration-script idempotency re-check at PR time if T010/T011 change): valid, carry it.
- N2 (two inline FR-006 normalization helpers must be verified byte-identical in behavior at review
  time -- a divergence would be a silent bug neither module's tests would catch): valid and worth
  emphasizing, carry it.

---

## Notes carried to implementation (non-blocking)

- **NB-1**: Missing `analysis.md`. Recommend running `/speckit-analyze` and committing it for chain
  hygiene, consistent with 094/095 practice. NON-BLOCKING (axis 6 performed here is clean).
- **NB-2** (from Sonnet N2): FR-006 normalization is implemented as a per-module inline helper
  (T006), not a shared utility. The two inline copies MUST be verified byte-identical in behavior at
  review time; a divergence is a subtle bug the suite itself would not catch.
- **NB-3**: FR Coverage Map row for FR-005 is under-inclusive (maps T015 only; add T027 for the US1
  DAX module's no-DB guarantee). Cosmetic -- coverage is real.
- **NB-4**: SC-004 (CRLF/LF no-flake) is satisfied by the FR-006 normalization construction and
  checked only via the T027 quickstart bundle, not a dedicated dual-checkout task. Acceptable;
  documented so it is not later mistaken for a gap.
- **NB-5** (from Sonnet N1): re-confirm the regeneration script's idempotency (T021) at PR time if
  the T010/T011 goldens are regenerated for any reason before merge.

## Verdict

**PASS-WITH-NOTES.**

All six axes are PASS (axis 3 with a non-blocking C086 residual explicitly authorized by FR-010;
axis 6 with two cosmetic map imprecisions). The feature stays strictly inside its
pytest-golden-tests-over-committed-fixtures allocation: no `retail check` rule, no rule-id, no
deferred-capability assumption, no fabricated score, no hidden self-grant or judgment-call
resolution, no shared-surface collision. I explicitly OVERTURN the Sonnet FAIL: the missing
`analysis.md` is a non-blocking note under this chain's own 094/095 practice for identically-shaped
features, and the consistency check that artifact would supply has been performed directly here and
is clean.
