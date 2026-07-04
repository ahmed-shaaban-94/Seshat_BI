# Adversarial Plan-Review: Semi-Additive (Snapshot) Grain in the Metric Contract

Single default-adverse skeptic over spec.md, plan.md, tasks.md and the design artifacts
(research.md, data-model.md, quickstart.md, analysis.md). READ-ONLY: findings report fixes;
no artifact was edited by this review. Draft completeness: spec + plan + tasks + research +
data-model + quickstart + analysis ALL present (analyze already ran, found 1 Medium + 2 Low,
no CRITICAL/HIGH) -> not an automatic BLOCKED.

## Axis 1 -- Hidden principle violation

- Finding (none -- verified clean): the discriminating question for this feature is whether
  HR5 quietly decides the SEMI-vs-NON classification word on a metric owner's behalf, which
  would be a live Principle-V violation dressed up as a schema check. Read data-model.md's
  decision table directly (rows 7 and 8): an A10-flagged contract declaring `time_additivity:
  semi` OR `time_additivity: non` both resolve to CLEAN -- no finding either way. HR5 rejects
  ONLY `fully` (row 6), which is safe because A10's own committed text
  (`kpi-ambiguities.md` line 65: "Inventory is semi-additive... Must never be summed across
  dates") makes "not fully additive" a categorical, already-settled fact, not a judgment HR5
  is making fresh. Rejecting `fully` on an A10-flagged contract is TRANSCRIPTION of an
  existing human-authored ledger fact, not a new classification decision. VERDICT: not a
  violation as specified.
- Finding (LOW, note): HR5 rejects `fully` even when the A10 entry's `decision_status` is
  `decided` (Edge Case "A10 entry is decision_status: decided"; FR-004a's neighbor). This is
  safe only because A10's underlying meaning is categorical ("never fully additive") and the
  `decided` status answers a DIFFERENT question (business snapshot policy) per the spec's own
  framing. Guard for the build: do not generalize this hard-reject-on-`fully` pattern to any
  future ambiguities-ledger id whose underlying claim is not similarly categorical -- that
  would silently smuggle a business judgment into a "safe" transcription.
- Finding (LOW, note): FR-018/Clarifications Q4 (whether the A10-only trigger should ever
  widen to non-inventory semi-additive shapes) is correctly left `[NEEDS CLARIFICATION --
  OPEN owner ruling]` and is explicitly NOT implemented (T011's docstring, T021's guard). This
  is compliance with Principle V, not a gap -- the workflow does not attempt to resolve a
  retail-kpi-knowledge ledger-scope call.
- No self-grant of approval found anywhere: HR5 advances no readiness stage, writes no
  `readiness.status`, and grants no approval (FR-011, checked against T008/T018). Confirmed
  against `templates/metric-contract.yaml`'s own `readiness` block -- HR5's read surface does
  not touch it.

## Axis 2 -- Assumes a deferred capability

- No finding. HR5 is a pure static YAML text read (lazy `import yaml` inside the registered
  function only, matching the shipped `assumptions.py` scaffold verified directly). Confirmed
  against research.md Section 3 and quickstart.md Section 5, which both enumerate, as
  explicitly NOT assumed: F016 (Power BI execution adapter), a live database connection, a
  `time_additivity`-aware DAX-generator extension, and a widened detection trigger. No task in
  tasks.md invokes `retail validate` (the live-check skill) or any Power BI connection
  tooling; T017 exercises only the existing static `retail check` binary. CLEAN.

## Axis 3 -- C086 / worked-example leak

- Finding (none -- verified clean, but the sharpest axis so the check is spelled out): HR5's
  source hardcodes the literal string `"A10"`. That could look like a leaked domain specific
  at a glance, but A10 is generic KIT VOCABULARY already defined in the generic template
  itself (`templates/metric-contract.yaml`'s own authoring comment lists "A1..A11" as the
  full closed ambiguities-ledger range, confirmed by direct read) and in
  `skills/retail-kpi-knowledge/knowledge/kpi-ambiguities.md` -- it is not a
  C086/retail_store_sales/pharmacy-specific token. This is the same status as the shipped AL1
  hardcoding `readiness.status`/`blocking_reasons` -- a generic schema vocabulary word, not a
  worked-example leak. Independently confirmed: `mappings/retail_store_sales/metrics/*.yaml`
  (the only filled corpus on disk) carries zero A10 entries today, so the day-one glob target
  is not even the trigger case -- there is no worked-example value HR5 could be leaking
  through its trigger.
- Finding (LOW, note -- matches 068's precedent guard): the day-one glob corpus
  (`mappings/*/metrics/*.yaml`) is, on `main` today, exclusively the worked-example
  (retail_store_sales) corpus -- the only filled contracts that exist. This is not itself a
  leak (the same is true of shipped AL1/AL2), but the leak test is the RULE CODE and the
  template comment, not the corpus. T019's grep-for-C086-tokens check must stay teeth-in
  during build and CI, not merely asserted in the spec.
- Confirmed directly: `templates/metric-contract.yaml`'s existing authoring style uses
  placeholder angle-bracket values (`<MetricName>`, `<fact_or_dim>`) throughout; FR-001/FR-016
  require the new field's comment follow the same style and cite, not restate, the knowledge
  doc. No task authors a filled example inline in the template.

## Axis 4 -- Fabricated confidence

- No finding. FR-009/SC-006 restrict HR5 to categorical `Severity.ERROR` findings only; the
  data-model.md Finding shape carries no numeric field, and T018 explicitly checks for the
  absence of `Severity.WARNING` and any graded/numeric field. The four message classes (rows
  1, 5, 6, 4/9) are all string labels, never a score, health value, or threshold. CLEAN --
  same posture as the shipped AD1/AL1 precedent this feature clones.

## Axis 5 -- Over-scope

- No finding. The closed file set (plan.md "Project Structure," tasks.md "Closed file set")
  is exactly: one template field edit, one new rule module, its test file, and the five
  wiring points (`__init__.py`, `test_rules_wiring.py`, two regenerated manifests). No file
  outside this list is touched.
- Confirmed no collision with the two sibling metric-contract adders directly, not merely by
  citation: `specs/092-rls-access-readiness/spec.md` states explicitly it ships "a wholly
  separate file" and "does NOT add ... keys to `templates/metric-contract.yaml`"; while it
  does add a *reference* line to the template's own header comment naming its file, that is
  documentation cross-reference, not a competing key -- and it explicitly excludes adding any
  key to this template. `specs/103-currency-unit-contract/spec.md` states its own top-level
  addition is a differently-named key, `unit` (not `time_additivity`), and explicitly excludes
  `grain`/`formula_intent`/`binds_to.pii_sensitive`. No overlap with `time_additivity` in
  either sibling spec.
- Confirmed HR5 does not read or duplicate AD1's corpus: `additivity_consistency.py` (AD1)
  reads `skills/retail-kpi-knowledge/contracts/*.md` (define-layer prose) for a composition-
  legality question; HR5 reads only `mappings/*/metrics/*.yaml` for a date-axis question.
  FR-008 states this boundary and T018(d) checks it structurally.
- One scope guard worth naming (LOW, note): data-model.md's Key Entities/Entity-1 table states
  the field applies "on every filled copy under `mappings/<table>/metrics/*.yaml>`" -- read
  literally this could be misread as "back-fill the field onto the 5 existing committed
  contracts." The closed file set correctly does NOT include editing any of the 5 existing
  `mappings/retail_store_sales/metrics/*.yaml` files (confirmed: none carry an A10 entry, so
  the field stays optional and absent on all of them per FR-007). Guard for the build: do not
  retroactively add `time_additivity` to the 5 existing contracts as part of this feature --
  that is out of the closed file set and unnecessary (FR-007 makes it optional, not required,
  absent an A10 flag).
- Confirms the feature adds no new readiness stage (spec's own "Boundary against neighbouring
  shipped work" section, FR-011) -- it is off-spine, matching AD1/AL1/AL2.

## Carried-forward non-blocking finding (from analysis.md, not re-litigated here)

- F1 (Medium, coverage gap, not an axis violation): FR-014 (unreadable-file fail-loud) has an
  implementation task (T005) but tasks.md's two test tasks (T006 covers decision-table rows
  5-8; T009 covers rows 2-4/9) do not cover row 1 (the unreadable-file case) with an actual
  fixture. This is a test-coverage gap the build should close (e.g., add a mocked
  `OSError`/`UnicodeDecodeError`/`yaml.YAMLError` fixture case to T006 or T009), not a
  principle violation on any of the five axes above.

## Open items correctly deferred to human (Principle V)

- FR-018 / Clarifications Q4: whether HR5's trigger should ever extend beyond the existing A10
  ambiguities-ledger id to a non-inventory semi-additive-over-time shape (e.g. a cumulative/
  YTD balance) is explicitly left `NEEDS CLARIFICATION -- OPEN owner ruling`. This is a
  retail-kpi-knowledge ledger-scope business decision, not something this build or this review
  may resolve. It remains open for a named retail-kpi-knowledge owner at a future date and does
  not block this build, which correctly implements only the decided A10-only half.

## Verdict

Verdict: PASS-WITH-NOTES

Rationale: No CRITICAL or HIGH finding on any axis; no axis drops below PASS. The feature's
sharpest risk -- HR5 secretly deciding the semi-vs-non classification word, which would be a
live Principle-V violation -- is directly refuted by data-model.md's decision table (rows 7/8
both CLEAN): the rule rejects only the categorically-settled `fully`, never chooses between
`semi` and `non`. The A10-leak concern on Axis 3 is likewise refuted: A10 is generic kit
vocabulary already named in the generic template, not a C086 specific, and the day-one corpus
carries zero A10 entries. Four LOW notes (don't generalize the hard-reject-on-fully pattern to
non-categorical ambiguity ids; keep T019's C086-token grep teeth-in through CI; do not
back-fill `time_additivity` onto the 5 existing contracts; FR-014 needs a dedicated unreadable-
file test fixture) are guard-rails for the BUILD, not spec defects. The one genuine Principle-V
judgment call (FR-018/Q4) is correctly left OPEN rather than answered. The draft is ratifiable
as specified; the build should honor the four notes above and the human ratifier should be
aware FR-018/Q4 remains an open ledger-scope question for retail-kpi-knowledge, not a defect in
this build.
