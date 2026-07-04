# Adversarial Plan-Review: Cross-Table Column-Level Lineage / Impact Analysis (099)

**Feature**: `099-cross-table-lineage-impact` | **Date**: 2026-07-04
**Reviewer stance**: single default-adverse skeptic, READ-ONLY (reports findings,
edits nothing). Artifacts reviewed: spec.md, plan.md, tasks.md, analysis.md,
research.md, data-model.md, quickstart.md.

**Precondition check**: spec.md, plan.md, tasks.md, analysis.md all present and
committed. `speckit-analyze` has already run and reports 0 critical / 0 high
constitution violations, 16/16 FR coverage, 7/7 SC coverage, one HIGH-severity
internal contradiction confined to research.md (F1), and three LOW findings
(F2-F6). This review does not inherit analysis.md's conclusions as its own --
analysis.md is a consistency pass, not an adversarial one, and its own
"Constitution alignment" section marks every axis PASS from the artifacts'
self-report. This review instead re-derives each of its five axes from direct
inspection and, where possible, ground truth against the live tree, and found
one load-bearing issue analysis.md's non-adversarial pass did not surface (see
Axis 3).

**Ground truth verified directly against the worktree** (not merely the plan's
self-report):

- `templates/visual-contract-binding-map.md` exists and is the path the
  dashboard-design skill's own SKILL.md cites (line 217) -- confirms
  research.md section 1.2's fifth-artifact-family claim and the FR-014
  Clarification's default.
- `.claude/skills/` does NOT yet contain a `cross-table-lineage/` directory --
  confirms this is genuinely pre-build (design stage), not already partially
  implemented ahead of review.
- `grep -n "F036\|F037\|F039\|F040" docs/roadmap/roadmap.md` returns zero hits
  -- confirms research.md section 1.5's claim that F039 is unclaimed as of this
  research.
- The sibling in-flight feature `specs/101-consumer-data-dictionary/` does
  exist, and its own plan.md/research.md independently grep the same pattern,
  find F039 already proposed by 099, and correctly step aside to propose F040
  instead (`plan.md:256-262`, `research.md:92-106`) -- confirms analysis.md's
  F6 is accurately described as a correctly-hedged soft dependency, not a
  live collision.
- `src/retail/rules/publish_pack.py` and `scorecard.py` are the only two rule
  modules that glob filenames under `mappings/<table>/` -- both restrict to
  narrow, specific suffixes (`bi-handoff-pack.md`,
  `^mappings/[^/]+/.*coverage-scorecard\.md$`), neither of which would
  incidentally match `lineage-column-*.md` or `lineage-metric-*.md`. The
  "composes-only, no gate side-effect" invariant this feature's SC-005 rests on
  is not silently undermined by an existing rule reading its output.
- `data-model.md:81` and `tasks.md:79,192` confirm `net_sales_consistency_note`
  is a literal, fixed field name in the GENERIC entity shape (Entity 4) that
  `templates/lineage-trace.md` (T002) is instructed to carry as a placeholder
  slot -- this is the basis for Axis 3 below.
- `tasks.md:249-252` (T023's Generic-token scan) lists its grep tokens as
  "patient, insurance, payer, prescription, dispense, NDC, billing-code" plus
  "retail_store_sales-specific column/table names" -- it does **not** include
  "net_sales" / "Net Sales" / "net sales" anywhere in its token list, confirming
  the enforcement gap identified in Axis 3.

## Axis 1 -- hidden-principle-violation

Probe: does the design secretly self-grant an approval, decide a Principle-V
judgment call, or advise-instead-of-block?

- The core safety property is that a hop is marked `proven` only when a
  committed artifact contains an "EXPLICIT, machine-readable reference"
  (data-model.md Entity 2) -- never an inferred or interpreted match. Traced
  hop-by-hop: hop 1->2 (source-map column -> migration SQL) and hop 3->4
  (contract -> TMDL measure) are exactly the two hops FR-010 already flags as
  the genuine risk surface (no explicit cross-reference field exists today),
  and the spec/plan/tasks are unanimous and explicit that these stay
  `unresolved`/candidate, never silently promoted, until a named human rules
  on FR-010 (spec Clarifications; plan Constitution Check Principle V; tasks.md
  "Principle-V carve-out" section, referenced by T008/T013/T015). No task
  authorizes, sketches, or leaves room for a name-similarity heuristic to slip
  in as an implementation detail -- T008 requires the `note` field to
  explicitly explain why a link was NOT promoted, which is a stronger guard
  than silence would be.
- FR-009 / FR-007 / the module contract (T004) jointly forbid moving a
  readiness stage, granting an approval, defining business meaning, or writing
  back to any artifact the module reads. The artifact is structurally
  single-output (one generated file per run), so there is no code path by
  which a stage transition or approval record could be emitted even
  accidentally -- unlike modules that touch `readiness-status.yaml`, this one
  never opens that file for writing (Project Structure "WRITES" list in
  plan.md names only the two `lineage-*.md` patterns).
- FR-010 itself is correctly left OPEN, not silently closed. This is the
  principle the feature is explicitly built around, and the spec's own
  Clarifications section states the fail-safe default ships regardless of the
  eventual ruling, which is the correct "raise and stop," not "raise and
  proceed," posture.
- One residual soft spot, mirroring the 063 review's N1: "explicit
  machine-readable reference" is not yet given an operational test in SKILL.md
  (SKILL.md does not exist yet -- this is plan-stage prose only). The line
  between "the migration SQL's `SELECT` clause literally names the source-map's
  column" (mechanical, safe) and "the migration SQL's `SELECT` clause names a
  column that is semantically the same field under a different alias"
  (interpretive, risky) is not yet drawn precisely anywhere in tasks.md. T007's
  citation discipline says a hop "MUST cite the exact committed repo-relative
  path... it was read from," which constrains the OUTPUT shape but does not
  yet constrain the MATCHING method used to decide a hop is `proven` in the
  first place. This is not a violation today (nothing in the current design
  performs an interpretive match and calls it proven), but it is exactly the
  gap where an implementer under schedule pressure could quietly widen
  "proven" to include a fuzzy match. Recorded as **N1**.

Verdict: **PASS**. No hidden self-grant; the design's one genuine Principle-V
line (FR-010) is correctly raised and left open rather than resolved by
implication. One operational-precision gap (N1) is non-blocking but should be
closed in SKILL.md before or during build.

## Axis 2 -- assumes-deferred-capability

Probe: does any artifact assume F016, a live DB, or a running adapter exists?

- FR-002 explicitly forbids DB connection, SQL execution, DAX execution, any
  live Power BI/PBIP surface, and any F016/F031-F033 invocation. Every one of
  the five read-source artifact families (source-map YAML, migration SQL text,
  metric-contract YAML, committed TMDL text, binding-map Markdown) is static
  repository text, never a live query result.
- research.md section 3 ("Deferred capabilities NOT assumed") is an explicit,
  itemized non-goals list covering F016, F031-F033, live DB, graphical
  rendering, and reverse lineage -- and section 1 of analysis.md's own
  deferred-capability leakage scan independently confirms every F016/F031-F033
  mention across all six artifacts is in a "does NOT exist / MUST NOT invoke"
  framing, never an "assumes reachable" framing. This review's own reading of
  the same six artifacts agrees with that finding.
- The one place a live-adjacent capability is even named is `retail validate`
  (DB-connected), and quickstart.md's closing section explicitly places it
  OUT OF SCOPE ("It will not connect to a database or run SQL/DAX... that is
  `retail validate`... territory").

Verdict: **PASS**. No deferred capability is assumed reachable anywhere in the
design; the design is structurally 100% static, with no code path that could
accidentally reach toward F016 or a live DB even by omission.

## Axis 3 -- c086-leak

Probe: does any template/label bake in domain-specific values instead of
staying generic (Principle VII)?

- **FINDING (load-bearing, missed by analysis.md's non-adversarial pass):**
  `data-model.md` Entity 4 names a literal field `net_sales_consistency_note`
  as part of the GENERIC artifact shape every generated lineage document
  carries (data-model.md:81; also T002's own template-authoring instruction,
  tasks.md:79, and T016's SKILL.md-behavior instruction, tasks.md:192-197).
  "Net Sales" is the C086/worked-example KPI name from
  `docs/demo/net-sales-end-to-end-readiness-trace.md` -- it is domain-specific
  to the retail_store_sales worked example, not a generic concept. Baking a
  worked-example KPI's name into a FIXED FIELD LABEL of the generic entity
  shape (not merely citing it in illustrative prose, which Principle VII
  explicitly permits) is exactly the C086-leak pattern SC-007 and FR-011 exist
  to forbid: "the worked example... may appear only as a cited filled
  instance, never inlined into the template or a fixed section label" (spec
  FR-011, emphasis matches the spec's own words).
- The severity is sharpened, not softened, by the enforcement gap: T023's own
  Generic-token scan -- the task tasks.md and analysis.md both cite as the
  mechanism that would catch a C086 leak -- lists its grep tokens as
  "patient, insurance, payer, prescription, dispense, NDC, billing-code" (the
  pharmacy/C086 vocabulary) plus "retail_store_sales-specific column/table
  names." It does **not** include "net_sales," "Net Sales," or "net sales"
  anywhere in its token list (verified directly, tasks.md:249-252). As
  specified, T023 would NOT catch this leak even if executed exactly as
  written -- the guard has a hole precisely where the leak sits.
- This is distinguishable from the acceptable, spec-sanctioned use of "Net
  Sales" elsewhere in the design: SC-006, the Net-Sales Independent Test in
  User Story 2, and quickstart.md Scenario B step 5 all cite Net Sales as an
  ILLUSTRATIVE CONSISTENCY CHECK against an already-shipped hand-authored
  trace -- that is a cited filled instance, exactly what Principle VII
  permits, and this review does not flag those uses. The distinct, flagged
  problem is narrower and sharper: the FIELD NAME ITSELF in the generic
  template/data-model shape is domain-specific, not merely an example
  populating a generic field.
- Why this is not FAIL: the leak is a naming/labeling defect, not a
  functional one -- the field's BEHAVIOR (an optional consistency note,
  populated only when the starting point happens to resolve to a Net-Sales-
  equivalent contract) is itself generic and spec-compliant; only its LABEL
  hardcodes the domain instance. It is also a single, isolated field in an
  otherwise clean generic shape (every other field in Entity 1/2/3/4 uses
  fully generic names: `hop_name`, `evidence_state`, `citation`,
  `downstream_set`, `boundary_footer`), and it is caught before any code
  exists (SKILL.md and the template are both not yet authored) -- this is
  exactly the class of finding an adversarial plan-review exists to catch
  before it ships, not evidence the design is broadly undisciplined.
- Recorded as **N2 (build-blocking within this feature's own Phase 2/6, not
  spec-blocking)**: rename the field to a generic name before or during T002
  (e.g. `reference_trace_consistency_note` or
  `worked_example_consistency_note`), citing Net Sales only in the field's
  prose DESCRIPTION as the illustrative instance (matching how every other
  cited-instance reference in this design set already works), and add
  "net_sales" / "Net Sales" / "net sales" to T023's grep token list so the
  scan would actually catch a regression of this exact pattern in the future.
  T016's SKILL.md-behavior task must be updated to reference the renamed
  field. This is a data-model.md + tasks.md correction, not a spec.md
  correction (FR-011/SC-006 are already correctly worded; the shape derived
  from them drifted).

Verdict: **RISK**. One concrete, verified C086/worked-example leak into a
fixed generic-shape field label exists in the current design (data-model.md
Entity 4, propagated into tasks T002/T016). It is narrow, isolated, caught
pre-implementation, and trivially fixable without touching spec.md, but it is
real and would ship into the generic template/data-model as currently
specified if not corrected -- and the task designed to catch exactly this
class of defect (T023) does not have the token coverage to catch it. Not FAIL:
no runtime/behavioral consequence, single-field scope, cheap fix, spec-level
requirements already correct.

## Axis 4 -- fabricated-confidence

Probe: does any artifact emit a numeric score/health/maturity/completeness
count?

- FR-006 and data-model.md's "Forbidden fields" list (Entity 4) explicitly bar
  `blast_radius_score`, `confidence`, `health`, `maturity`,
  `artifacts_affected_count`, `priority`, `risk_level`, `recommended_action`.
  T003 requires the template to carry this exact forbidden-fields note as a
  standing guard against silent reintroduction in a future filled copy; T022
  is a dedicated grep-verification task at build time covering the same
  token set.
- Every field in Entity 1-4's shape is categorical or textual
  (`evidence_state: proven|unresolved|gap`, `resolved: boolean`, string
  citations/notes) -- no numeric field of any kind is proposed anywhere in the
  data model. The "downstream set" (User Story 3's whole subject) is
  explicitly a NAMED SET with citations, never a count of that set's size
  (FR-006: "Impact is expressed only as the named SET... " -- not "the number
  of items in the set").
- SC-003 and SC-004 are both binary/grep-able negative checks (0 score tokens,
  0 obligation verbs), consistent with hard rule #9's discipline; neither
  smuggles in an implicit numeric health/confidence metric under a different
  name.
- The one place a number appears anywhere near this feature's artifacts is
  the roadmap F-number proposal (F039) -- an identifier, not a score, and
  explicitly deferred to integration time rather than asserted as a settled
  fact in this stage's own deliverables.

Verdict: **PASS**. No fabricated or disguised numeric confidence/health/
maturity/completeness value exists anywhere in the design; the forbidden-
fields list is both stated and has a dedicated build-time enforcement task
(T022) with an accurate token list (unlike T023's incomplete list for Axis 3).

## Axis 5 -- over-scope

Probe: does the plan do more than its one readiness-stage job, or cross into
another feature's territory?

- The spec's own "Boundary against neighbouring shipped work" section
  distinguishes this feature from four close neighbours (spec 044 KPI
  Derivation-Lineage, F014 Source Drift Detector, F012 Data Quality Control
  Room, the Net-Sales trace) with a specific, falsifiable claim for each
  ("this feature does not touch contract prose," "this feature does not
  detect drift," "this feature aggregates LINEAGE EDGES, not DQ findings").
  Spot-checked against the actual FR text: FR-002 (no drift detection, no
  comparison logic), the Overview (this feature never edits/re-derives a
  spec-044 `Derives from` edge), and the Assumptions (Control Room's
  independence is preserved) all hold up under direct reading -- none of the
  four boundary claims is contradicted elsewhere in the FR list.
- Deliverables are tightly bounded per tasks.md's own "Scope guard": ONE skill
  file, ONE generic template, nothing else. The scope guard explicitly forbids
  (and this review confirms none of T001-T026 violates): a roadmap-ledger
  edit, a `src/retail/rules/` entry, a Python module, a `tests/` file, a DB
  connection, an F016/F031-F033 invocation, and inlining C086 specifics into
  the template body (Axis 3's finding is the one place this last guard's
  companion enforcement task under-delivers, not a violation of the guard's
  own intent).
- **The metric-rooted "backward trace" is the one place scope-creep risk is
  real, not merely theoretical.** T013 instructs the module to "trace backward
  only far enough to cite the contract's own required-field origin against
  the source-map/migration-SQL side," while spec Assumptions declare reverse
  (upstream-only) lineage queries explicitly OUT OF SCOPE. Read literally,
  "only far enough to cite... origin" is bounded to a SINGLE backward
  citation (does the contract's required field trace to an explicit
  source-map/SQL reference, yes/no/unresolved) -- not a recursive upstream
  walk. Data-model.md's illustrative section (line 112-114) confirms this
  reading: the metric-rooted example still produces hop 1 and hop 2 as
  ordinary forward-order entries, just entered from a different starting
  point, not a separate reverse-traversal algorithm. So the CURRENT wording
  is defensible as "one bounded backward-citation check," but the phrase
  "only far enough" is loose enough that an implementer could read it as
  license to keep walking backward indefinitely (e.g., from the source-map
  entry further back to a raw bronze table, or across multiple source-map
  rows) which WOULD reintroduce the excluded reverse-lineage query by
  increments. Recorded as **N3**: SKILL.md must state explicitly that the
  metric-rooted backward step is bounded to exactly hop 2 -> hop 1 (a single
  citation check against the contract's own required-field origin), and MUST
  NOT recurse further upstream than the source-map entry under any
  circumstance.
- The feature adds no new readiness stage, no new `retail check` rule-id
  (confirmed: FR-013, and no `src/retail/rules/` entry appears anywhere in
  plan.md's "ADDS" file list), and does not touch `readiness-status.yaml`
  (plan.md's WRITES list names only the two `lineage-*.md` patterns). It does
  not touch the roadmap-ledger file in this stage (research.md 1.5, tasks.md
  scope guard) -- correctly deferred to integration time to avoid the
  19-parallel-features collision this repo's own collision-avoidance
  allocation exists to prevent (independently confirmed against the real
  sibling 101 above).

Verdict: **PASS**. Scope is disciplined and matches its stated collision-
avoidance allocation (Product Module, no rule-id, no schema touch). One
wording looseness (N3, the metric-rooted backward-trace bound) is a real but
narrow risk of scope-creep-by-increment and should be tightened in SKILL.md
before implementation, not a present violation.

## Notes / carry-forward (non-blocking)

- **N1** (Axis 1, low): "Explicit machine-readable reference" (the test for
  `proven`) is not yet given an operational definition in any task. SKILL.md
  must state precisely what counts as machine-readable (e.g., literal
  identifier match in a `SELECT`/YAML key/TMDL object name) versus what does
  not (paraphrase, business-friendly name, semantic similarity) before build,
  so "proven" cannot silently drift toward interpretation.
- **N2** (Axis 3, medium -- the one finding this review adds beyond
  analysis.md's own pass): rename `net_sales_consistency_note` to a generic
  field name in data-model.md Entity 4 and tasks.md T002/T016 before or during
  implementation; add "net_sales"/"Net Sales"/"net sales" to T023's grep
  token list. This is the one concrete, verified C086-leak this review found
  that analysis.md's consistency-only pass did not surface (analysis.md's own
  F1-F6 do not mention this field at all).
- **N3** (Axis 5, low-medium): tighten T013's "trace backward only far enough"
  language in SKILL.md to an explicit single-hop bound (hop 2 -> hop 1 only,
  never recursing past the source-map entry), so the metric-rooted entry
  point cannot incrementally reintroduce the explicitly-out-of-scope reverse-
  lineage query.
- **N4** (carried from analysis.md F1, low): research.md:66-71 contains a
  self-contradicting sentence about the F024 capability level (first says
  `read-only`, two paragraphs later correctly concludes `artifact-writing`).
  This does not map cleanly to any of the five axes (it is a documentation
  internal-consistency defect, not a hidden judgment call, deferred
  capability, C086 leak, fabricated score, or scope violation) and does not
  propagate into plan.md or tasks.md, which already land correctly on
  `artifact-writing`. Non-blocking; cheap fix (strike the outdated clause) if
  research.md is ever revised.
- **N5** (low): analysis.md's F3 (Constitution Check omits an explicit
  "Principle II: N/A" line) and F5 (SC-001 is qualitative rather than a hard
  threshold) are both accurate, both genuinely low severity, and this review
  independently agrees neither blocks anything. No new action beyond what
  analysis.md already recommends.
- **Ground-truth-clean item worth recording explicitly**: the "composes-only"
  invariant (SC-005) that every prior Product Module review in this repo has
  had to check is independently verified clean here -- no existing
  `retail check` rule globs a pattern that would incidentally pick up
  `lineage-column-*.md` or `lineage-metric-*.md` (only `publish_pack.py` and
  `scorecard.py` glob anything under `mappings/<table>/`, both with narrow,
  specific suffixes unrelated to this feature's output). This feature's own
  generated artifact will not accidentally trip a gate.

## Verdict

**Verdict**: PASS-WITH-NOTES

Four of five axes clear cleanly (hidden-principle-violation, assumes-deferred-
capability, fabricated-confidence, over-scope all PASS, each independently
re-derived and ground-truth-checked rather than inherited from analysis.md's
self-report). One axis is RISK, not PASS: the generic data-model shape bakes
the worked-example KPI name "Net Sales" into a fixed field label
(`net_sales_consistency_note`), a genuine Principle VII / SC-007 leak that
analysis.md's non-adversarial consistency pass did not surface, and whose own
designated enforcement task (T023) currently lacks the token coverage to catch
it. This is narrow, isolated to one field, caught before any code exists, and
cheaply fixed by renaming the field and extending T023's grep list -- it does
not require a spec.md rewrite (FR-011/SC-006 are already correctly worded) and
does not block proceeding to implementation, provided the fix lands in
data-model.md/tasks.md first. Three additional non-blocking N-notes (N1
operational precision for "proven," N3 the metric-rooted backward-trace
bound, N4/N5 carried from analysis.md) should be honored during implementation
but do not require re-specification. FR-010 remains correctly OPEN as the
feature's one genuine Principle-V judgment call and must not be resolved by
the agent at any later stage.
