# Cross-Artifact Analysis: Currency / Unit-of-Measure Contract

**Feature**: 103-currency-unit-contract | **Date**: 2026-07-04 | **Stage**: ANALYZE (read-only)

**Scope**: Non-destructive consistency check across `spec.md`, `plan.md`,
`tasks.md`, `research.md`, `data-model.md`, `quickstart.md`. No other file was
modified to produce this report.

## Requirement-coverage table

Built independently from spec.md/plan.md/data-model.md against tasks.md's own
task bodies (not transcribed from tasks.md's self-reported "FR Coverage Map",
which is itself one of the artifacts under audit).

| FR | Requirement (short) | Covering task(s) | Status |
|---|---|---|---|
| FR-001 | source-map gains columns[].unit/columns[].currency, optional, default null | T002 (fixture), T005 (template edit) | OK |
| FR-002 | metric-contract gains top-level unit only, no currency | T006 | OK |
| FR-003 | new static rule HR11 registered | T008, T010 | OK |
| FR-004 | resolve every bound column to source-map entry, read unit/currency | T009, T018 | OK |
| FR-005 | fail on 2+ resolved columns w/ different non-null unit | T012, T019 | OK |
| FR-006 | fail on 2+ resolved columns w/ different non-null currency, independent of FR-005 | T026, T028, T029 | OK |
| FR-007 | exact case-sensitive comparison, no alias/fuzzy match | T019 (unit), T029 (currency) -- no dedicated negative test for case-sensitivity (e.g. "kg" vs "Kg" asserted as a mismatch) | GAP (partial) -- see F4 |
| FR-008 | no conversion rate/factor/converted value in any finding | T013, T027, T034 | OK |
| FR-009 | no DAX/SQL execution, no DB/network, no live PBIP read | T008, T009 (lazy import, read-only) | OK |
| FR-010 | unresolved bound column or missing/unreadable source-map -> blocking finding | T014, T015, T018 | OK |
| FR-011 | HR11 must not fire on <2 bound columns | T017 (skip), T023 (negative test) | OK |
| FR-012 | HR11 finding surfaces in semantic_model_ready.blocking_reasons[] | T016 -- asserts the wiring but adds no code, and no task touches the artifact that actually enumerates which rule ids block that stage | GAP -- see F1 |
| FR-013 | detection-scope ("is this a sum") left OPEN, not defaulted | T008 (docstring), T037 (grep-verify) -- but see F2: T017-T019's actual instructions contain no definition.aggregation gate at all | Contradiction -- see F2 |
| FR-014 | undeclared-value enforcement posture left OPEN, not defaulted | T008, T037, T039 | OK (recorded-open, not resolved, consistent) |
| FR-015 | no numeric confidence/health/maturity score anywhere | T024, T036 | OK |
| FR-016 | templates/rule stay generic, no C086-specific token | T002 (fixture uses generic names), T035 | OK |
| FR-017 | ASCII/UTF-8-no-BOM, Windows path budget | T005, T006 (asserted, not independently tested) | OK |
| FR-018 | semantic-model-ready.md lists HR11 in Required checks + Blocking reasons | T007, T038 | OK |
| FR-019 | no live-DB-backed check introduced | T039 ("verified by absence" -- no positive test exists because there is nothing to test) | OK (coverage is structural, not a test) |
| FR-020 | agent never auto-fills unit/currency; declaration is human-authored | T039 ("no code path... writes to either template" -- again coverage by absence/code-reading, not a runtime test) | OK (coverage is structural, not a test) |

18 of 20 FRs have clean covering tasks. FR-012 has a real gap (F1) and FR-013 has
an internal contradiction between the stated open-question policy and the literal
implementation instructions (F2). FR-019/FR-020 are legitimately covered "by
absence" (there is no code to positively test), which is appropriate for a
MUST-NOT requirement but is worth naming explicitly rather than treating as
equivalent to an executed test.

## Success-criteria testability

| SC | Testable as written? |
|---|---|
| SC-001 | Yes -- T012/T020 exercise the exact scenario (100% of a specific fixture family caught) |
| SC-002 | Yes -- T026/T030 |
| SC-003 | Yes -- T013, T027, T034 (grep for rate/factor/convert substrings) |
| SC-004 | Yes -- T021, T022, T025 |
| SC-005 | Yes -- T024, T036 |
| SC-006 | Yes -- T033, T035 |

All six Success Criteria are stated as falsifiable, mechanically checkable
conditions (finding counts, grep results) rather than subjective judgments,
and each has at least one task that exercises it. No SC references a
fabricated score, consistent with hard rule #9.

## Terminology consistency

- "columns[].unit" / "columns[].currency" / metric-contract top-level "unit"
  are used identically across spec.md, plan.md, data-model.md, quickstart.md,
  and tasks.md -- no drift, no competing name (uom, unit_of_measure,
  measure_unit never appear as adopted terms; they appear only as
  explicitly-forbidden names in the Scope Guard and in T033's grep list).
- "HR11" is used consistently as the rule id across all six artifacts; no
  other artifact silently renames or renumbers it.
- "documentary only" (metric-level unit, Clarification Q3) is stated
  identically in spec.md, plan.md, research.md (P2), data-model.md
  (Entity 2), and quickstart.md (Step 2 comment) -- no artifact re-opens or
  contradicts this.
- One soft inconsistency: spec.md's Key Entities section calls the
  source-map field the "Unit declaration" / "Currency declaration" while
  data-model.md calls the same thing "Entity 1 -- Unit declaration
  (columns[].unit, source-map)" and folds currency into the same entity's
  field-notes table rather than giving currency its own numbered entity.
  This is a documentation-organization difference, not a semantic
  contradiction (the field-notes table in data-model.md does cover
  columns[].currency fully) -- noted as trivial, no action needed.
- "Semantic Model Ready" vs "Stage 5" vs "semantic_model_ready" (YAML key)
  are used interchangeably but correctly across artifacts, matching the
  repo's existing convention (each artifact uses the form appropriate to
  its register -- prose vs YAML key).

No terminology finding rises above cosmetic.

## Constitution alignment

Checked against the nine Principles plus hard rule #9, as bound by this
task's instructions.

| Principle | Alignment |
|---|---|
| I. Agent-First, Gate-Enforced | HR11 is specified as Severity.ERROR only (never WARNING) across spec (FR-005/006), plan (Constitution Check), data-model (Entity 3 -- "all four triggers are Severity.ERROR"), and tasks (T032 asserts posture snapshot never records WARNING). Fails closed, consistent throughout. |
| III. Medallion, Gold-Only | Not engaged directly by this feature (HR11 reads already-gold-bound binds_to.columns[], per spec Boundary section); plan.md correctly scopes this as "enforced upstream." No artifact claims HR11 reads bronze/silver. |
| IV. Source-Mapping-Before-Silver | Correctly respected: FR-001's two new source-map keys are additive/optional and plan.md explicitly states "no silver.* SQL is authored, edited, or implied by this plan." No artifact proposes writing SQL. |
| V. Agent-Stops-at-Judgment | FR-013 and FR-014 are both explicitly carried as OPEN in spec.md Clarifications, plan.md's "Two open questions carried forward," research.md's "Deferred capabilities," and tasks.md's repeated "stay OPEN" framing (T037). FR-020 explicitly forbids the agent auto-filling unit/currency. This is the single most load-bearing principle for this feature and it is consistently honored in the documentation layer across all six artifacts -- see F2 below for where the task-body implementation instructions (not the stated policy) risk silently resolving FR-013 in one direction. |
| VI. Defaults-Then-Deviations | Q3 (metric-level unit documentary-only) and Q4 (join key = rename_to) are both recorded as adopted defaults with an explicit "why this is safe to default" rationale, consistent everywhere they are cited (spec Clarifications, plan Constitution Check, research P2/P6, data-model Entity 2/4). |
| VII. C086-is-an-example | data-model.md's own header states every example is a placeholder; FR-016 requires genericity; T002/T035 verify it via fixture-naming and grep. No artifact inlines a retail_store_sales/C086-specific value into a generic template. |
| VIII. Static-First/Live-Deferred | FR-009/FR-019 and research.md's "Deferred capabilities" section explicitly disclaim any live DB or PBIP read; quickstart.md's Step 3/5 use only the existing static retail check / retail-semantic-check surfaces. No artifact assumes a live surface exists (see Deferred-capability leakage scan below). |
| IX. Secrets/Reproducibility | FR-017 requires ASCII/UTF-8-no-BOM and Windows path budget; no artifact introduces a host/DSN/secret. Consistent. |
| Hard rule #9 (no fabricated score) | FR-015/SC-005 explicitly forbid a numeric confidence/health/maturity score or "N of M" completeness count; T024/T036 verify by grep. No artifact in this set introduces one. |
| F016 boundary | plan.md's Constitution Check explicitly states "this design assumes F016 does NOT exist" and HR11 never opens a PBIP/DAX/Power BI surface. Consistent (see Deferred-capability leakage scan). |

## Contradiction / duplication / ambiguity scan

### F1 -- FR-012's "zero new code" claim is not substantiated against the actual wiring mechanism (Severity: HIGH)

spec.md (FR-012), plan.md (Summary, "no change to F010/retail-semantic-check's
own logic"), and tasks.md (T016's description: "this test documents/confirms
the WIRING contract... it does NOT add new computation") all assert that an
HR11 Severity.ERROR finding automatically surfaces in
semantic_model_ready.blocking_reasons[] purely by virtue of being an
ERROR-severity retail check finding -- "the same way an existing
D1-D11/G6/HR-family finding already blocks that stage."

This claim is not true of the actual mechanism as committed in this repo.
`.claude/skills/retail-semantic-check/SKILL.md` (the skill that computes the
Semantic Model Ready verdict) states its mechanical gate step explicitly as a
NAMED, CLOSED LIST: "Any D1-D8 (TMDL/DAX), C1 (connection params), R1
(relative reference), or G6 (no real host) finding is a distinct
blocking_reason" -- not "any Severity.ERROR finding." HR11 is not, and cannot
be, in that list unless a task edits SKILL.md to add it. No task in tasks.md
(T001-T039) touches `.claude/skills/retail-semantic-check/SKILL.md`. T007/T038
only touch `docs/readiness/semantic-model-ready.md` (the stage-authority doc),
which is a different file from the skill implementation that actually
performs the "any D1-D8/C1/R1/G6 finding blocks" enumeration.

Without a task adding HR11 to that named list, running retail-semantic-check
per its own documented procedure would not surface an HR11 finding in
blocking_reasons[] even though retail check's raw exit code would be
non-zero -- an inconsistency between "mechanically failing" and "the skill's
own interpreted verdict," which is exactly the gap the skill's own "central
property" section implies should not happen.

**Mitigating context**: this is not unique to 103 -- a check of
specs/092-rls-access-readiness/tasks.md shows the identical gap for HR6 (the
sibling this feature explicitly mirrors); 092 also never touches SKILL.md's
named list. This suggests either (a) the repo's actual practice is that
SKILL.md's step-2 list is meant to be read as illustrative/non-exhaustive
rather than literally closed, or (b) both 092 and 103 share a genuine,
un-flagged wiring gap. Given FR-012's literal wording ("the same way an
existing D1-D11/G6/HR-family finding already blocks that stage"), and given
SKILL.md's own literal text names an explicit id list, this is flagged as a
coverage gap for FR-012 rather than assumed benign.

**Recommendation** (not applied -- read-only stage): a task should either
(a) add HR11 to SKILL.md's step-2 enumerated list, or (b) if the list is
intended to be read as open-ended/illustrative, an explicit repo-level
clarification (outside this feature's scope) should say so, and this
feature's FR-012/T016 language should say "any ERROR-severity finding blocks
per existing precedent" rather than implying a mechanism it cannot verify
from the committed skill text.

### F2 -- T017-T019's literal implementation instructions do not gate on definition.aggregation, which operationally is the "any 2+-column bind" extreme that plan.md and research.md forbid adopting (Severity: HIGH)

plan.md's Constitution Check states, as a "non-negotiable constraint carried
into tasks.md": "no version of this feature may ship code that silently
adopts either extreme as if it were already settled by this plan" --
referring to FR-013's two candidate readings (scope to
definition.aggregation: sum only, vs. scope to any 2+-column bind regardless
of definition). research.md's "Deferred capabilities" section repeats this
explicitly.

tasks.md's own preamble (lines 36-46) acknowledges the tension and states the
fixtures are deliberately authored with an explicit
definition.aggregation: sum block "so the unit/currency comparison can be
tested without the tasks silently resolving FR-013."

However, the actual IMPLEMENTATION TASK BODIES -- T017 ("skip any contract
whose binds_to.columns[] lists fewer than two entries"), T018 (resolve bound
columns via _read_source_map_columns), and T019 ("compare, pairwise, the
resolved unit value of every bound column that DOES resolve... emit exactly
one ERROR finding per metric when two or more of them declare a different,
non-null unit value") -- contain NO INSTRUCTION ANYWHERE to read, check, or
gate on definition.aggregation at all. As literally written,
check_unit_currency_agreement() fires on every metric contract with 2+
resolvable bound columns, full stop -- which is precisely the "any
2+-column bind, definition or not" extreme that plan.md's non-negotiable
constraint says must not ship.

T037 (a Polish-phase, post-hoc grep/read-verify task) asks someone to
"confirm src/retail/rules/hr11.py contains no logic that... unconditionally
treat[s] any 2+-column bind as a sum with no definition.aggregation gate at
all being asserted as 'settled'" -- but T037 only checks whether the code
ASSERTS this is settled (e.g., in a comment or docstring), not whether the
code's ACTUAL RUNTIME BEHAVIOR still fires unconditionally on any 2+-column
bind. A rule module that fires on every 2+-column bind while its docstring
says "this is not the settled answer to FR-013" would satisfy T037's literal
wording while still shipping exactly the behavior the Constitution Check
forbids "as if it were already settled."

This is read as a genuine contradiction between the stated Principle-V
policy (FR-013 stays open, no extreme ships) and the literal step-by-step
build instructions that, followed as written, ship one of the two forbidden
extremes as the running behavior -- not merely an underspecified predicate.
THIS IS THE BASIS FOR scope_ok=false (see below): the artifact set, taken as
instructions to build from, would produce code that silently resolves a
Principle-V-routed open question in one direction, contradicting FR-013 and
the plan's own non-negotiable constraint.

### F3 -- Q2a: an Acceptance Scenario presupposes an answer to an explicitly-open question, and this is self-flagged but not removed (Severity: MEDIUM, self-managed)

spec.md's User Story 3 Acceptance Scenario 3 states that a
currency-declared-vs-currency-undeclared pairing "is not treated as matches
anything" -- i.e., it presupposes the STRICT answer to FR-014 (open,
owner-ruling-required). But FR-006, the functional requirement that scenario
is supposed to be testing, literally fires only on "two or more of a
metric's resolved bound columns declare a different, non-null" currency
value -- a null-vs-non-null pairing is outside that literal condition.

This is explicitly flagged by the spec itself (the "Q2a" note immediately
following the Acceptance Scenario, and again in the Clarifications section)
as an unresolved internal-consistency issue, and is carried consistently
through plan.md, research.md, and data-model.md (Entity 3's "Explicitly NOT
(yet) a finding trigger" section) without any artifact silently picking a
side. tasks.md correctly excludes this shape from its fixture set (T002's
undeclared-unit/currency column is stated as "NOT wired into any FR-014
pass/fail assertion").

Because this is self-documented consistently across every artifact and no
artifact resolves it in either direction, this is recorded as a real but
ALREADY-MANAGED inconsistency -- a genuine defect in the requirements-as-
written (an acceptance scenario not actually backed by its governing FR
until FR-014 is ruled), but not a case of one artifact silently
contradicting another's settled position. Severity MEDIUM because it does
represent an acceptance criterion that cannot currently be verified as
written, but it does not risk shipping unauthorized behavior (unlike F2).

### F4 -- FR-007's case-sensitivity requirement lacks a dedicated positive test (Severity: LOW)

FR-007 requires "an exact, case-sensitive string comparison" and explicitly
calls out "kg" vs "Kg" vs "kilogram" as an edge case that must be reported as
a mismatch, not reconciled. T019/T029 implement the comparison "using the
SAME exact-string-equality mechanism," but no task in tasks.md authors a
fixture or test asserting that two case-different values (e.g., "kg" vs
"Kg") are actually flagged as a mismatch rather than silently treated as
equal by an accidental case-insensitive comparison. T012/T026 test
genuinely-different tokens (kg vs each, EGP vs USD), which does not exercise
the case-sensitivity boundary at all. This is a minor test-coverage gap
against an explicit FR, not a design contradiction.

### No other contradiction, duplication, or ambiguity found

- The Scope Guard's forbidden-key list (uom, unit_of_measure, measure_unit,
  binds_to.currency, metric.currency) is stated identically in spec.md and
  enforced identically by T033/T035 -- no drift.
- The 092/HR6 boundary section (spec.md) and research.md's P1/P4/P9
  sections agree on what is reused (pattern) vs. not reused (092's "new
  file" structural choice) -- no contradiction.
- tasks.md's claim that "092's Polish check confirms 0 lines changed" vs.
  this feature's "confirms the diffs LANDED" is consistent with
  research.md's P1 finding and is not a duplication -- it is an
  explicitly-flagged structural difference, correctly not treated as a
  template to blindly copy.
- No duplicate rule-id or duplicate key-name allocation was found between
  this spec and the two named neighboring specs (088, 091) it must avoid
  colliding with, based on the keys this spec actually claims
  (columns[].unit, columns[].currency, metric-contract unit, rule id
  HR11) -- spec.md's own Scope Guard states the collision-avoidance
  allocation explicitly and no other artifact in this set introduces a
  different key for the same purpose.

## Deferred-capability leakage scan (F016 / live DB)

Checked spec.md, plan.md, research.md, data-model.md, quickstart.md, and
tasks.md for any assumption that F016 (Power BI execution adapter) or a live
database surface already exists.

- F016: plan.md's Constitution Check has an explicit "F016 boundary" row
  stating the design assumes F016 does NOT exist; research.md's "Deferred
  capabilities NOT assumed" repeats this ("No F016... F016 does not exist in
  this repo and this feature does not assume any interface from it"). No
  artifact's quickstart or task instructs opening a PBIP file, connecting to
  Power BI Desktop/service, or evaluating a DAX measure. Clean.
- Live DB: FR-009/FR-019 explicitly forbid any DB/network connection or
  live-data sampling; research.md states the live check is "deferred to a
  future retail validate extension, not this feature"; quickstart.md's every
  step uses only retail check / retail-semantic-check (both existing static
  surfaces) or retail manifest (also static, code-registry-driven). T039's
  verification step explicitly confirms no fabricated finding results from
  running against the live repo tree's currently-all-undeclared mappings --
  this is a static-tree check, not a live-DB connection. Clean.
- All six artifacts consistently reference ctx.tracked_files /
  Path.read_text() as the sole I/O mechanism for HR11 -- no artifact
  introduces a database driver import, a connection string, or a network
  call.

No deferred-capability leakage found.

## Summary of findings

| ID | Severity | One-line summary |
|---|---|---|
| F1 | HIGH | FR-012's "surfaces automatically in blocking_reasons[]" claim is not backed by any task touching the skill file (SKILL.md) that actually enumerates which rule ids block Stage 5 by a named, closed list -- a coverage gap shared with the HR6 sibling this feature mirrors. |
| F2 | HIGH | T017-T019's literal implementation instructions contain no definition.aggregation gate, operationally shipping the "any 2+-column bind" extreme that plan.md's own non-negotiable constraint (Principle V/FR-013) forbids adopting as settled; T037's post-hoc grep does not actually verify the runtime behavior differs from that extreme. |
| F3 | MEDIUM | US3 Acceptance Scenario 3 presupposes the strict (unruled) answer to FR-014/Q2a; self-flagged consistently across all artifacts and not resolved in either direction, but the acceptance criterion is currently unverifiable as written. |
| F4 | LOW | FR-007's case-sensitivity requirement ("kg" vs "Kg" must mismatch) has no dedicated fixture/test exercising that exact boundary. |

## scope_ok verdict

**scope_ok = false.**

Rationale: F2 is judged a real Principle-V violation risk, not merely a
documentation gap. The spec, plan, and research artifacts are unanimous and
explicit that FR-013's detection-scope question must not be resolved by this
feature and that shipping either candidate extreme "as if it were already
settled" is forbidden. But tasks.md's actual step-by-step build instructions
(T017-T019) -- the artifact an implementer would mechanically follow --
describe a check_unit_currency_agreement() with no conditional on
definition.aggregation anywhere, which is operationally indistinguishable
from adopting the "any 2+-column bind" extreme as the running behavior. The
Polish-phase T037 checks the code's self-description, not its behavior, so
it would not catch this at verification time either. This is exactly the
class of thing this ANALYZE stage exists to catch before implementation
begins: an artifact set that talks a fully Principle-V-compliant policy
while its own build instructions would, if executed literally, ship a
settled answer to a question its own plan forbids settling.

F1 is a substantive coverage gap (FR-012) but is judged a
documentation/wiring omission rather than a constitution violation in
itself -- no artifact claims authority it doesn't have, and the same gap
exists in the already-in-flight HR6 sibling, suggesting it may be an
accepted (if under-examined) repo-wide pattern rather than a 103-specific
defect. It is listed under open_principle_v for visibility but does not by
itself flip scope_ok.

## open_principle_v (judgment calls left OPEN for a human)

- **FR-014 (+ Q2a)**: whether an undeclared (null/absent) unit/currency on
  one side of a multi-column bind is a blocking finding, a warning, or a
  silent no-op. This is the genuine Principle-V/VI owner-ruling item -- a
  governance-policy call about retroactive enforcement strictness that no
  artifact in this set attempts to resolve. Correctly left open throughout.
- **FR-013 (detection scope)**: whether HR11 scopes itself to
  definition.aggregation: sum specifically or to any 2+-column bind. The
  spec itself (Clarifications Q1) is explicit that this is NOT a Principle-V
  human-values ruling but a design-detection-scope decision routed to
  implementation planning -- it should not be mischaracterized as an
  owner-approval item. It is listed here because F2 shows the current
  artifact set's task-level instructions risk resolving it as a side effect
  of how hr11.py is literally specified to be built, which is exactly the
  kind of silent default Principle V/VI exists to prevent regardless of
  which sub-flavor of judgment call it is.
- **FR-012 wiring (F1)**: not a Principle-V human-values judgment call, but a
  genuine open technical question (does SKILL.md's enumerated id list need a
  literal edit, or is it meant as illustrative) that determines whether this
  feature's stated behavior is achievable without an additional task.
  Recorded here for visibility since it affects whether the feature as
  specified can actually deliver on FR-012 as literally worded.
