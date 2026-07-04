# Adversarial Plan-Review: Dashboard Accessibility + RTL/Arabic Readiness Checklist (102)

A single default-adverse skeptic over spec.md, plan.md, tasks.md, and their supporting
research.md/data-model.md/quickstart.md/analysis.md (READ-ONLY: I report fixes, I do not
edit). Five axes: hidden-principle-violation, assumes-deferred-capability, c086-leak,
fabricated-confidence, over-scope. analysis.md (already on disk, an internal consistency
pass) is treated as an input to verify, not a substitute for this adversarial pass; its
findings are independently re-checked against the actual repo below, not transcribed.

## Axis 1 -- hidden-principle-violation

- **Does the enforcement mechanism secretly resolve Q-FR014-SEVERITY toward `blocked`?
  RISK.** FR-011 / T011 / data-model.md's "interim severity floor" states an open finding
  in any dimension is recorded as AT LEAST a `warning`-class finding "cited in
  `blocking_reasons[]` **or** an equivalent warning-evidence entry." But `blocking_reasons[]`
  is not a neutral list in this repo's own readiness vocabulary: `docs/readiness/
  readiness-model.md` line 90 defines `blocked` as "a required artifact, check, or approval
  is missing -- see `blocking_reasons`," and line 103 defines `blocking_reasons[]` as "lists
  the concrete reasons a stage is `blocked`." If the eventual template/workflow takes the
  literal "cited in `blocking_reasons[]`" branch for a merely-`warning`-worthy finding, that
  entry becomes the DEFINITIONAL marker of `blocked` in this repo's own model -- which is
  precisely the Q-FR014-SEVERITY question the spec declares OPEN and forbidden to the agent
  (FR-014b). The "or an equivalent warning-evidence entry" clause is the compliant escape
  hatch, and data-model.md does hedge elsewhere ("any dimension `blocked` -> overall
  `blocked` (or `warning`, pending Q-FR014-SEVERITY)"), so the spec-level artifacts do not
  themselves commit to the pre-empting branch -- but the wording is loose enough that an
  implementer filling in `templates/a11y-rtl-readiness-checklist.md` at task time could
  wire the "at least warning" floor straight into `blocking_reasons[]`, silently manufacturing
  a `blocked` status for every dimension defect before the owner rules on severity. This does
  not FAIL the axis (no artifact currently asserts the pre-empting reading; both branches are
  literally present in the text), but it is a live risk the build must close explicitly.
  Recorded as N1 (must-fix at task/template-authoring time, not at spec time).
- **Advise-instead-of-block objection, engaged and cleared.** FR-008 forbids a new `retail
  check` rule; enforcement of "the checklist must be filled" runs entirely through the
  EXISTING human design-review sign-off on `dashboard_ready`, not through any mechanical
  gate this feature adds. An adversarial read must ask whether this is Principle I's
  "advise, don't block" failure mode in disguise. It is not, for three independently
  sufficient reasons, all confirmed on disk: (a) this is the identical mechanism F034's own
  "design approved vs page implemented" evidence item already uses on the same file
  (`docs/readiness/dashboard-ready.md` lines 54-79, confirmed present) -- the precedent this
  feature explicitly mirrors, not a new leniency; (b) the underlying gate itself (`pass`
  requires the design-review sign-off recorded in `approvals[]`) still fails closed --
  nothing here weakens that gate, it only adds a required INPUT to the same sign-off; (c)
  colorblind-safe and RTL/Arabic legibility are independently confirmed NOT mechanically
  verifiable from committed static text without rendering the report (Principle VIII; F016
  is gated and does not exist), so a `retail check` rule is structurally unavailable for two
  of the three dimensions regardless of preference -- the SCOPE GUARD's "evidence item, not
  a rule" default is the only Principle-VIII-compliant shape available, not a softening.
  The "teeth" here are convention/sign-off-enforced, not test-enforced -- worth stating
  plainly (mirrors 101's N3) so a signer does not mistake this for a mechanical gate.
  PASS, with the caveat recorded as N2 (low, informational).
- **No self-granted approval anywhere.** The checklist itself never sets `dashboard_ready:
  pass` (FR-007's own text, the data-model.md "Invariants" section, and quickstart.md step 5
  all state this explicitly); it produces evidence FOR the existing BI/report-owner sign-off.
  Confirmed against the actual `dashboard-ready.md` "Required owner / approval" section
  (unedited by this feature). PASS.
- **Both genuine Principle-V questions (Q-FR014-SCOPE, Q-FR014-SEVERITY) stay OPEN, not
  defaulted.** Verified across all six artifacts: spec.md's Clarifications section states
  both as "OPEN owner ruling" with an explicit PENDING-DEFAULT / floor that a human must
  ratify, never a silent resolution; data-model.md's `scope_ruling_citation` field makes an
  assumed default an INVALID citation (not merely discouraged); quickstart.md step 4
  instructs "STOP before marking this dimension not-applicable-with-reason" absent an
  explicit human ruling. This is correct Principle-V posture -- raised, not answered. PASS.

## Axis 2 -- assumes-deferred-capability

- FR-002, the Constraints section of plan.md, and quickstart.md's "What this feature does
  NOT let you do" section all independently forbid render/open/publish/connect to Power BI
  Desktop, a live semantic model, or F016; F016 is named explicitly as "gated and does not
  exist." No task, template field, or worked-instance step calls a live surface. PASS.
- Independently verified against the actual `src/retail/rules/design_contrast.py` (CT1)
  source: its own docstring states "Read-only: parses committed YAML, renders no pixel,
  opens no DB, writes nothing," and the code confirms this (`_iter_tokens_files` reads
  `ctx.tracked_files`, `_load_yaml` opens a local `Path`, no network/DB import anywhere in
  the module). The only tool this feature's tasks invoke (`retail check`, T002/T026) is
  confirmed static and read-only. No deferred-capability leakage. PASS.
- The colorblind-safe dimension is explicitly a "documented HUMAN/agent-read judgment
  against fixed criteria, NOT a numeric CVD-simulation score" (data-model.md, spec
  Assumptions) -- a future CVD-simulation engine is named as a SEPARATE, not-yet-specified
  feature this one does not build or presuppose. PASS.

## Axis 3 -- c086-leak

- FR-009 and FR-013 require the generic template and the criteria-doc extension to carry no
  C086/pharmacy/retail_store_sales domain noun, color literal, or grain key, AND no literal
  Arabic string in the GENERIC artifacts (a real Arabic example, if any, is confined to the
  ONE filled worked instance under `mappings/retail_store_sales/design/`). This is the
  sharpest c086 risk in this specific feature (unlike most docs/template features, this one's
  subject matter -- RTL/Arabic readiness -- makes it unusually tempting to embed an actual
  Arabic string "for illustration" directly in the generic template). T024 exists
  specifically as a non-ASCII-byte grep against the generic template file to catch exactly
  this. PASS, contingent on T024/T023 actually being executed as a build-time guard (not
  merely declared as intent) -- recorded as N3 (mirrors 101's own N2 pattern: intent is not
  enforcement until the grep is actually run and its output checked).
- The worked instance is correctly scoped as the ONE place real `retail_store_sales` values
  appear (`mappings/retail_store_sales/design/a11y-rtl-readiness-checklist.md`), cited from
  the generic template by pointer, never inlined into it -- consistent with FR-009 and the
  F034 precedent's own real-values-only-in-the-instance discipline. PASS.
- The two new criteria subsections planned for `docs/powerbi/visual-design-system.md`
  (T015/T016) are specified with generic example language only ("do not rely on hue alone,"
  "avoid red/green as the only distinguishing pair," "Arabic numeral/date formatting
  expectations" as a category, not a worked value) -- no C086 color literal or domain noun
  appears in the planned text. PASS.

## Axis 4 -- fabricated-confidence

- FR-012 explicitly forbids any numeric confidence/health/maturity score or completeness
  count; data-model.md states "No `score`, `confidence`, `health`, `maturity`, or
  `completeness_count` field exists anywhere in this shape" as an explicit negative-space
  section (stronger than a bare prose rule, matching 101's own strong pattern -- harder to
  violate by accident than a spec that only states the rule once). Every dimension and the
  overall roll-up use the four-value readiness vocabulary (`not_started`/`blocked`/
  `warning`/`pass` at the checklist level; `reviewed-clean`/`not-applicable-with-reason`/
  `blocked` per dimension) -- never a number. T025 is a deterministic grep across all four
  target files for `score`/`confidence`/`health`/`maturity`/`completeness` used as a numeric
  field. PASS.
- SC-003 makes this independently falsifiable (0 generated/filled checklists contain a
  numeric field) and SC-005 makes the no-new-rule guarantee independently falsifiable (rule
  count/id-set diff before/after). Both are mechanically checkable, not self-attested. PASS.

## Axis 5 -- over-scope

- **Scope is pinned correctly**: one generic template (`templates/`), one additive
  prose-section extension to an EXISTING doc (`docs/powerbi/visual-design-system.md`), one
  additive evidence-item edit to an EXISTING stage doc (`docs/readiness/dashboard-ready.md`),
  and one worked instance. No new top-level directory, no `src/` change, no new `retail
  check` rule, no rule-registry wiring, no CLI, no MCP call -- confirmed via the tasks.md
  SCOPE GUARD (naming the four exact out-of-scope surfaces: `src/retail/rules/`,
  `docs/rules/rules-manifest.json`, `tests/unit/test_rules_wiring.py`,
  `docs/roadmap/roadmap.md`) and independently confirmed no task in tasks.md touches any of
  those four paths. PASS.
- **The Collision-Avoidance allocation is honored, and the reasoning for declining HR10 is
  sound.** The spec explicitly declined the offered HR10 rule-id reservation, reasoning that
  a second rule recomputing CT1's contrast math over a different file would be the
  duplicate-surface problem the guard exists to prevent. Independently verified against
  CT1's actual code: CT1 already does a global suffix-scan for every `*-design-tokens.yaml`
  file in `ctx.tracked_files`, so a second rule targeting the same file class would indeed be
  pure duplication, not new coverage. Declining HR10 is the correct call. PASS.
- **F1 (from analysis.md, independently re-verified): the "reuse the same co-location
  convention `visual-implementation-trace.md` already uses" claim (FR-003/FR-009/FR-015,
  Clarifications C1, research.md R5) is factually wrong about its own cited precedent, but
  this is a wording defect, not scope creep -- confirmed by direct read of the actual repo:**
  - `templates/visual-implementation-trace.md` contains zero occurrences of the word
    "token" anywhere in the file (confirmed by full read above) -- it establishes no
    token-file co-location convention to reuse.
  - `mappings/retail_store_sales/design/` (confirmed via glob) contains exactly
    `dashboard-layout.md`, `visual-contract-binding-map.md`, `visual-list.md` -- no token
    file lives there.
  - The only `*-design-tokens.yaml` file in the repo is the repo-root
    `design/tokens/tower-retail-design-tokens.yaml` (confirmed via glob: single match).
  - CT1's own `_iter_tokens_files()` (confirmed by reading the source) resolves token files
    by a GLOBAL suffix scan over `ctx.tracked_files` -- there is no per-subject-area lookup
    mechanism in the shipped code to "reuse."
  - **Why this stays a note, not a FAIL on this axis**: the actual resolution needed is
    trivial (there is exactly one token file in the corpus today; CT1 already finds it via
    a global scan) -- the defect is mis-describing an existing, already-correct outcome as
    "reuse of a co-location convention" that does not exist, not a proposal to build new
    machinery. The trap to flag for the build: do NOT "fix" this by constructing a NEW
    per-subject-area token-to-page lookup/index/manifest -- that would be actual new scope
    (an index this feature's own Assumptions and research.md R5 correctly reject as
    speculative YAGNI when discussing an alternative). The correct fix is narrower: reword
    FR-015/C1/R5 to state the real mechanic (CT1's global suffix-scan finds the one token
    file already; the checklist cites that file directly, or -- if the corpus later gains
    multiple token files -- the checklist cites whichever one is co-located under the page's
    OWN `mappings/<subject>/design/` directory as a NEW, honestly-labeled convention at that
    future point, not attributed to a precedent that never established it). Recorded as N4
    (medium; task-time fix, does not require a spec rewrite, does not change any FR's
    intent or the worked instance's actual citation target).
  - **F2 (from analysis.md, re-verified): `ct1_result: file-not-found` is not a real CT1
    output category.** Confirmed by reading `design_contrast.py`: its only four
    `Finding`-emission sites are an unparseable/missing floor, an invalid hex, a below-floor
    ratio, and a YAML parse failure. A token file that CT1's scan simply does not match
    produces NO finding at all (silent), not a "file not found" finding. This does not
    block authoring -- the checklist can still record "file not found" as the CHECKLIST
    AUTHOR's own determination when they cannot locate the cited file -- but data-model.md
    and quickstart.md currently phrase it as if CT1 itself asserts this category, which it
    structurally cannot. Recorded as N5 (low; a wording fix attributing "file-not-found" to
    the checklist filler's own check, not to CT1's enum).
- **No duplication found with neighbouring shipped work.** Independently checked each of the
  five "Boundary against neighbouring shipped work" claims against the actual files: CT1
  computes a ratio and reviews no RTL/colorblind legibility (confirmed by reading the code);
  the theme-JSON purity linter (spec 060) scans forbidden KEYS, not legibility (matches
  spec's own description, and 060 is a `src/retail/rules/*.py` module + registry-wiring
  shape this feature's SCOPE GUARD explicitly does not follow); `design_theme_fidelity.py`
  checks token-to-theme agreement, not readability (name and stated purpose are consistent
  with the boundary claim, not independently re-read line-by-line here since it is cited only
  as a negative-boundary, non-load-bearing claim); the retail-term dictionary is Stage 1 term
  meaning, a different stage; the mobile-layout workflow is the cited non-rule precedent for
  a layout concern as a design-workflow output, matching this feature's own checklist shape.
  PASS.
- **Low collision note on the shared `dashboard-ready.md` file.** `specs/
  104-rename-impact-refactor-guard/plan.md` also edits `docs/readiness/dashboard-ready.md`,
  but at a different location (its own "Blocking reasons" table, adding an HR9 line scoped to
  a binding-map-orphan case) versus this feature's new evidence-item subsection appended
  after the existing F034 block. Both edits are additive-only to the same file at different,
  non-overlapping insertion points -- within this feature's own allocation, not a collision
  requiring resolution here, but worth flagging for whoever lands both features close in time
  to sequence the two diffs cleanly. Recorded as N6 (low, informational).

## Findings summary

| ID | Axis | Severity | Finding | Fix |
|----|------|----------|---------|-----|
| N1 | hidden-principle-violation | medium | The interim severity floor's "cited in `blocking_reasons[]` or an equivalent warning-evidence entry" wording risks the template/workflow taking the `blocking_reasons[]` branch for a merely-`warning`-worthy finding -- which, under this repo's own `readiness-model.md` definitions, IS the marker of `blocked`, silently pre-empting the OPEN Q-FR014-SEVERITY ruling. | At template/workflow-authoring time (T011, T017, T018), make the non-pre-empting branch the ONLY implemented path until the owner rules: record an open finding as a distinct warning-evidence entry (e.g. an `evidence[]`-adjacent note or a dedicated `open_findings[]` field) that does NOT populate `blocking_reasons[]` and does NOT set `overall_status: blocked`, until Q-FR014-SEVERITY is resolved. |
| N2 | hidden-principle-violation | low (informational) | Enforcement is convention/sign-off-enforced (the existing human design-review gate), not test-enforced by any mechanical `retail check` rule. | State this plainly in the template/workflow so a signer does not mistake the checklist requirement for a mechanical gate; no spec change needed -- this is the correct, Principle-VIII-consistent shape given colorblind/RTL are not mechanically checkable without F016. |
| N3 | c086-leak | low | Genericity/no-Arabic-string guards (T023/T024) are declared intent; must be actually executed and their output checked at authoring time, not merely planned. | Implement: run the greps and record zero-match output as part of the Polish phase's completion evidence, not just as a task checkbox. |
| N4 | over-scope | medium | FR-003/FR-009/FR-015/C1/R5's claimed "reuse the same co-location convention `visual-implementation-trace.md` already uses" for token-file resolution does not exist in the cited file, and the actual token file lives at repo-root `design/tokens/`, not under any `mappings/<subject>/design/` directory; CT1 itself resolves token files via a global suffix-scan, not a per-subject lookup. | Reword FR-015/C1/R5 at task time to describe the REAL mechanic (CT1's global scan already finds the corpus's one token file; the checklist cites that file directly). Do NOT build a new per-subject token-to-page index/manifest to make the false "convention" true -- that would be actual new scope this feature's own YAGNI reasoning already rejects. |
| N5 | over-scope (precision) | low | `ct1_result: file-not-found` is presented as if it were one of CT1's own output categories; CT1 has no such finding -- an unmatched file produces silence, not a finding. | Attribute "file-not-found" to the checklist filler's OWN determination (made when they cannot locate the cited file), not to CT1's finding vocabulary, in data-model.md/quickstart.md wording at task time. |
| N6 | over-scope (collision) | low (informational) | `104-rename-impact-refactor-guard` also additively edits `docs/readiness/dashboard-ready.md`, at a different (non-overlapping) location. | No action required now; sequence the two diffs if both land close in time. |

No finding rises to CRITICAL or blocks the spec as currently written. All six are
addressable at task/authoring time within the existing spec shape; none requires a spec
rewrite or invalidates an FR's intent.

## Verdict

**PASS-WITH-NOTES**

The spec/plan/tasks are internally consistent, keep both genuine Principle-V questions
correctly OPEN (never defaulted), assume no deferred capability (F016/live-DB/CVD-engine
all correctly named as absent and unused), stay generic with a real and non-trivial
Arabic-string leak risk correctly guarded by a dedicated task (T024), and emit no numeric
score anywhere in six independently-checked artifacts. The scope stays disciplined: no new
`retail check` rule, no new stage, no new status, no `src/` change -- confirmed against the
actual CT1 source and the actual repo layout, not just the spec's own claims.

One medium finding (N1) is a real, if currently-latent, risk that the build could
accidentally pre-resolve Q-FR014-SEVERITY through a literal reading of "cite in
`blocking_reasons[]`" against this repo's own readiness-status vocabulary -- this must be
closed explicitly at template-authoring time, not left to the wording as currently drafted.
One medium finding (N4, carried forward from analysis.md's F1 and independently
re-verified against the actual `design_contrast.py` source and the actual
`mappings/retail_store_sales/design/` directory contents) is a factual mismatch between the
claimed "reuse" mechanic and both the cited precedent file and the real repo layout --
addressable by a wording correction, with an explicit warning against "fixing" it by
building new lookup machinery that would itself become scope creep. Three low notes (N2,
N3, N5) and one informational note (N6) round out the record. None of these six findings
meets the bar for FAIL: no self-granted approval, no assumed deferred capability, no
fabricated score, and no confirmed C086/domain leak in the artifacts as drafted.

**Verdict**: PASS-WITH-NOTES
