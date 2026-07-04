# Cross-Artifact Analysis: Rename/Impact Refactor-Safety Static Rule (HR9)

**Feature**: `104-rename-impact-refactor-guard` | **Date**: 2026-07-04 | **Stage**: ANALYZE

**Scope**: Read-only cross-artifact consistency pass over `spec.md`, `plan.md`,
`tasks.md`, `research.md`, `data-model.md`, `quickstart.md`. No other file was
edited to produce this document. Verified against the live repo tree (not
just the artifacts' own claims) where a claim was checkable: `src/retail/rules/`
contents, `HR1`/`HR6`/`HR9` grep across `src/`, `docs/`, `specs/`, the worked
`retail_store_sales` metric contract / TMDL / binding-map files, the gate docs,
and the six wiring-surface files named in Phase 2.

---

## 1. Requirement-Coverage Table

Every Functional Requirement against its covering task(s)/artifact(s).

| FR | Requirement (short) | Covering task(s) | Status |
|---|---|---|---|
| FR-001 | Register new rule id HR9, engage on every table with >=1 TMDL file | T004 | OK |
| FR-002 | Derive truth set from committed TMDL, no manifest | T004, T011 | OK |
| FR-003 | Resolve contract `binds_to.columns` against truth set | T019, T020, T021 | OK |
| FR-004 | Resolve DAX measure-to-measure / measure-to-column tokens | T030, T031 | OK |
| FR-005 | Resolve binding-map `semantic_model_field(s)` bracket tokens | T032, T033 | OK |
| FR-006 | Table-qualified = own table only; unqualified measure = model-folder union | T012, T020, T031, T033 | OK |
| FR-007 | No TMDL for a table -> zero findings (no premature engagement) | T037, T038 | GAP (see F1) |
| FR-008 | Check regardless of contract `readiness.status` | T017, T019 | OK |
| FR-009 | Never decide/auto-correct/suggest a name; name-and-stop only | T021 | OK |
| FR-010 | No DAX execution, no live DB/PBIP surface | T004, T039 | OK |
| FR-011 | Surface HR9 in `blocking_reasons[]` (Semantic Model Ready / Dashboard Ready) | T002, T003, T046 | OK |
| FR-012 | No numeric score; binary clean/blocked | T008, T021, T040 | OK |
| FR-013 | No worked-example (C086/pharmacy/retail_store_sales) hardcode in rule source | T004, T041, T042 | OK |
| FR-014 | Gate docs list HR9 in Blocking-reasons | T002, T003, T046 | OK (see F5 terminology nit) |
| FR-015 | Rule-count lockstep across wiring surfaces | T005, T006, T007, T008, T009, T010 | OK (tasks exceed FR text -- see F4) |
| FR-016 | Q-APPROVAL-SEAM stays OPEN, not self-decided | T045 | OK |

**Summary**: 15/16 FRs have unambiguous, non-contradictory task coverage. FR-007
is marked GAP not because no task addresses it, but because the task that is
supposed to guarantee it (T037) is internally ambiguous in a way that could
make the guarantee false under one reading -- see Finding F1 below, the
substantive result of this analysis pass.

---

## 2. Success-Criteria Testability

| SC | Text | Testable as written? |
|---|---|---|
| SC-001 | Orphaned `binds_to.columns` entry produces a finding | Yes -- binary, fixture-checkable (T015/T018) |
| SC-002 | Orphaned DAX measure/column token produces a finding | Yes -- binary, fixture-checkable (T023/T024/T029) |
| SC-003 | Orphaned binding-map bracket token produces a finding | Yes -- binary, fixture-checkable (T026/T029) |
| SC-004 | "0 HR9 findings, or the HR9 rule's own source, contain a worked-example domain specific" | Testable but the wording is inverted/ambiguous on first read (see F6) -- the intended and actually-implemented test (T041/T042: grep the rule source and fixtures for zero worked-example literals) is unambiguous; only the SC's own prose is momentarily confusing. |
| SC-005 | 0 findings for a table with contracts but no TMDL | Testable in isolation (T035/T036/T038) but its truth depends on T037's ambiguous no-op condition -- see F1. |
| SC-006 | HR9 never writes/renames/modifies a committed artifact | Yes -- source-inspection test (T039), plus the quickstart's git-status-diff check |
| SC-007 | Both gate docs list HR9 in their Blocking-reasons section | Yes, but see F5 -- the two docs use different structural shapes (table vs. bullet list), and SC-007 says "tables" for both |
| SC-008 | Wiring/rule-count meta-gates stay green | Yes -- T014, T044 exercise exactly this; both referenced test files (`test_wiring_meta_gate.py`, `test_rule_count_claims.py`) exist in the tree today |

All 8 SCs are measurable outcomes, not vague aspirations, and none smuggles in
a numeric confidence/health score (hard rule #9 compliant). SC-004's prose
construction ("0 HR9 findings, or the rule's own source, contain...") reads
oddly as a single sentence but the intent -- and T041/T042's actual
implementation of it -- is unambiguous: two independent zero-conditions (no
worked-example-triggered findings, and no worked-example literal in the source
itself).

---

## 3. Terminology Consistency

- **"HR9" / "rename/impact refactor-safety" / "reconcile-and-fail-closed"** are
  used consistently across all six artifacts with the same meaning.
- **Rule module filename convention drifts from the SF1 precedent's own naming**:
  `rule_sf1.py` (the actual committed SF1 module name, confirmed by `ls
  src/retail/rules/`) uses the `rule_<id>.py` pattern, while HR9's planned
  module is `rename_impact_guard.py` (plan.md, tasks.md T004) -- a
  descriptive-name pattern instead, closer to `status_claims.py`/`parked_on.py`.
  Both patterns already coexist in the codebase (`status_claims.py` is SC1,
  `rule_sf1.py` is SF1, `rule_ap1.py` is AP1), so this is not a genuine defect,
  just worth flagging as a naming-convention footnote -- no artifact asserts a
  single mandatory file-naming rule, so there is no contradiction, only
  precedent inconsistency already present before this feature.
- **"Blocking reasons" is called a "table" in SC-007 and T002/T003/T046, but
  only `semantic-model-ready.md` actually uses a Markdown table for that
  section** -- `dashboard-ready.md`'s "Blocking reasons" section (confirmed by
  direct read) is a bullet list, not a table. See Finding F5.
- **"Truth set" / "Reference set" / "Orphaned reference"** (spec Key Entities,
  data-model.md Entities 1-3) are used identically across spec.md, plan.md,
  research.md, data-model.md, quickstart.md -- no drift.
- **"Manifest-less"** is asserted consistently in spec.md, plan.md, research.md
  Sec 2.1, and tasks.md's preamble -- all agree HR9 introduces no new
  `docs/quality/*.yaml` manifest, which is independently verifiable: `ls
  docs/quality/` shows no HR9-related file is proposed anywhere in the task
  list.
- **HR6 is cited as an established "precedent" in spec.md FR-014** ("mirrors
  the HR6 FR-017 precedent"), but research.md Sec 2 explicitly finds "HR6 has
  no rule source and no HR6 text outside specs 092/103/105" (themselves
  in-flight, unshipped specs) and instructs the reader to treat it as "a NAMING
  CONVENTION... not a file to open or depend on." This is self-corrected within
  the artifact set (research.md catches what spec.md's FR-014 phrasing implies)
  rather than a live contradiction, but it is worth surfacing verbatim -- see
  Finding F7 (LOW).

---

## 4. Constitution Alignment

| Principle | Alignment check | Verdict |
|---|---|---|
| I. Agent-First, Gate-Enforced | HR9 findings are `Severity.ERROR` only (data-model.md Entity 5) -- no WARNING tier, so a finding always fails the gate's exit code; compliance is demonstrable by running `retail check`. plan.md's Constitution Check table states this explicitly. | PASS |
| III. Medallion/Gold-Only | HR9 reads only the gold-schema TMDL surface and artifacts that reference gold (metric contracts bound to `gold_table`, binding-map cells naming gold measures/dim columns); it does not read silver/bronze and adds no new fact/dimension shape. | PASS |
| IV. Source-Mapping-Before-Silver | HR9 writes no `silver.*` SQL and operates strictly downstream of an already-approved map (Semantic Model Ready / Dashboard Ready territory). Not implicated. | PASS (not implicated) |
| V. Agent-Stops-at-Judgment | The mechanical resolution question ("does this reference resolve") is not a judgment call and may be computed directly (matches SC1/DF1 precedent). The one genuine Principle-V question -- Q-APPROVAL-SEAM (does a clean HR9 run need its own approval seam) -- is explicitly left OPEN in spec.md's Clarifications, plan.md's Constitution Check, and tasks.md T045 (marked "OWNER SEAM -- OPEN, do not answer"). No artifact self-grants an answer. | PASS |
| VI. Defaults-Then-Deviations | Q-CASE-SENSITIVITY and Q-BINDING-CELL-PARSE are recorded as reasonable, reversible, constitution-safe defaults under a dated session subsection, distinct from the Q-APPROVAL-SEAM Principle-V carve-out. Q-MEASURE-SCOPE is also correctly classified as "a Principle-VI mechanical default... not a Principle-V judgment call" since it matches externally-verifiable Power BI engine semantics rather than inventing a business rule. | PASS |
| VII. C086-Is-An-Example | FR-013/SC-004 require zero worked-example-specific literals in the rule's own source; `retail_store_sales` is used only as a cited, inspected example in research.md/plan.md/data-model.md to confirm concrete artifact shapes, never as a hardcoded value the rule logic depends on. T041/T042 verify this by grep. | PASS |
| VIII. Static-First/Live-Deferred | HR9 never opens a DB connection, never executes DAX, never opens a live Power BI/PBIP surface (FR-010). All six artifacts agree there is no "live half" of HR9 to mark PENDING -- unlike `retail validate`, referential-integrity-against-committed-text has no live analogue by design. | PASS |
| IX. Secrets/Reproducibility | No connection string, DSN, or credential is introduced anywhere in the design. | PASS |
| Hard rule #9 (no fabricated score) | HR9's output is strictly binary (ERROR finding present or absent) -- no confidence/health/maturity/completeness number is computed or stored anywhere in spec.md, data-model.md Entity 5, or the wiring in `docs/rules/severity-posture.json` (T008 explicitly rejects HR1's two-tier `["error","warning"]` shape in favor of `["error"]` only). | PASS |

**Overall constitution verdict**: PASS on every principle and on hard rule #9.
No principle requires a justified deviation; plan.md's Complexity Tracking is
correctly empty.

---

## 5. Contradiction / Duplication / Ambiguity Scan

### F1 -- FR-007/US3/SC-005 no-op guarantee is ambiguously scoped in T037 (MEDIUM-HIGH)

**Where**: `tasks.md` T037, read against `data-model.md` Entity 3 step 2 and
`spec.md` FR-007/US3/SC-005.

**The conflict**: Entity 3 step 2 says that when a contract's `gold_table`
qualifier resolves to no TMDL table at all, "the qualifier itself is
unresolved -> orphan (naming the qualifier, not a column)" -- i.e., HR9 fires.
But FR-007/US3/SC-005 require that a table with metric contracts and no
committed TMDL file produces zero findings -- i.e., HR9 must be silent.
Statically, "a contract's `gold_table` resolves to no TMDL table anywhere"
is the exact same detectable condition in both cases: there is no way from
committed text alone to distinguish "this table simply hasn't reached Semantic
Model Ready yet" (US3, must be silent) from "this table's gold_table was
renamed/typo'd and now dangles" (a genuine orphan, should fire) -- the two are
the same string-lookup miss.

T037's own text tries to reconcile this but gives the no-op condition two
different scopes in the same sentence:

> "a contract-column reference whose `gold_table` does not resolve to ANY TMDL
> table anywhere in the tree is reported as an unresolved QUALIFIER orphan
> only if TMDL model surfaces exist elsewhere in the tree... when the table
> has genuinely no TMDL file anywhere, no Reference... is resolved and no
> Finding is produced"

Read literally ("anywhere in the tree" / "anywhere"), this makes the no-op
condition tree-global: a table's own missing TMDL only stays silent if no
other table in the whole repo has a TMDL file. Since `retail_store_sales`
already has a fully committed TMDL model (`powerbi/RetailStoreSales.
SemanticModel/`, confirmed present in the current tree), any other newly
onboarded table with contracts-but-no-TMDL would, under this literal reading,
have its contract-column references treated as genuine orphans (because "TMDL
model surfaces exist elsewhere in the tree" is trivially true today) -- the
exact opposite of what US3/FR-007/SC-005 require, and a regression against the
"HR1 zero/one-star no-op precedent" the spec explicitly invokes as the bar to
clear.

A folder-scoped reading ("no TMDL surface at all for that table's own model
folder") would resolve the contradiction correctly and matches the rest of the
design's folder-scoping discipline (Entity 1's `*.SemanticModel/` folder
scope, Entity 3 step 0's "locate the governing model first," FR-006's
cross-model isolation) -- but T037's own sentence does not commit to that
reading; it explicitly says "in the tree" / "anywhere," which is tree-global
language, not folder-scoped language.

**Impact**: If implemented per the literal (tree-global) reading, US3's
Acceptance Scenario 1, FR-007, and SC-005 all break the first time a second
table's TMDL exists in the repo -- which is already true today. This would
also silently violate SC-005's "0 HR9 findings... for a table that has metric
contracts but no committed TMDL model file" the moment HR9 ships, since
`retail_store_sales` already provides the "TMDL exists elsewhere" trigger
condition for every other onboarded-but-not-yet-modeled table.

**Recommendation** (for the BUILD stage, not this ANALYZE stage): T037 should
be rewritten to unambiguously key the no-op condition on "does the referenced
table's own model folder have at least one committed TMDL file," never on
tree-global TMDL existence. This does not require a spec/plan change -- FR-007's
own text ("A table with metric contracts but no TMDL model surface yet") is
already correctly table-scoped; only T037's task-authoring language needs
tightening before implementation.

### F2 -- DAX unqualified-bracket-token disambiguation is a documented but unenforced assumption (LOW-MEDIUM)

**Where**: `data-model.md` Entity 2b.

Entity 2b states as a design assumption that every unqualified bracket token
in a DAX expression is treated as a candidate MEASURE reference and every
qualified token as a candidate COLUMN reference, because "DAX has no such
form in practice on this model" (an unqualified column reference). The
document is commendably honest that this is "a known, explicitly documented
limitation" that could misclassify a future unqualified-column DAX form as a
measure lookup and false-positive. This is not a contradiction between
artifacts -- plan.md, research.md, and tasks.md do not claim otherwise -- but it
is a load-bearing correctness assumption resting on an informal survey of the
one worked instance, not on a DAX-language guarantee. No task in Phase 3/4
tests the failure mode this limitation describes (an unqualified column
reference triggering a false orphan). This is a legitimate, disclosed gap, not
a defect to fix at this stage, but it should not be silently forgotten once
implementation begins.

### F3 -- No collision-avoidance ledger file exists in the tree to independently verify the HR9 reservation (LOW, informational)

**Where**: spec.md header, tasks.md T001.

Both the feature description and spec.md assert HR9 is a "reserved static-rule
id" allocated under a "collision-avoidance ledger," and T001 tasks a
confirmation grep against `src/retail/rules/__init__.py` and
`docs/rules/rules-manifest.json`. A repo-wide grep for HR9 found matches only
inside this feature's own six spec files -- no other in-flight spec directory,
no rule source, and no manifest currently claims HR9, which is consistent with
a clean reservation. However, no single "collision-avoidance ledger" file was
found anywhere in the tree to independently corroborate that the allocation
process itself (as opposed to the current absence of collisions) is tracked
anywhere durable. This is not a defect in the six artifacts under review -- T001
correctly scopes itself to a live grep, not a ledger-file read -- but it means
the ledger's existence is asserted, not independently verifiable from this
repo's committed state.

### F4 -- FR-015 under-enumerates the wiring surfaces tasks.md actually discovers (LOW, coverage note, not a defect)

**Where**: spec.md FR-015 vs. tasks.md T005-T010.

FR-015's text names three wiring surfaces explicitly (`src/retail/rules/
__init__.py`'s import/`__all__`, `docs/rules/rules-manifest.json`, `tests/
unit/test_rules_wiring.py`'s expected-id set). tasks.md's Foundational phase
discovers and tasks six wiring surfaces (adding `docs/rules/
severity-posture.json`, `docs/glossary.md`, and `docs/quality/
rule-count-claims.yaml`), all of which were confirmed to exist in the current
tree. This is tasks.md being more complete than the FR's own enumeration, not
a contradiction -- the FR's normative claim ("the rule-count lockstep MUST stay
intact... the count itself is never hardcoded") is general enough to cover all
six, and the Requirement Coverage Check at the bottom of tasks.md correctly
maps FR-015 to all six task ids (T005-T010). Recorded as a coverage note only:
a future reader of spec.md alone would not learn that six surfaces exist, only
three.

### F5 -- SC-007/T002/T003/T046 call both gate docs' "Blocking reasons" sections a "table," but only one is (LOW)

**Where**: spec.md SC-007, tasks.md T002/T003/T046, vs. the actual files.

Direct read of `docs/readiness/semantic-model-ready.md` confirms its
"Blocking reasons" content is presented as a bullet list under that heading
(not a Markdown table in the strict sense, though T002 itself hedges with
"section/table"). Direct read of `docs/readiness/dashboard-ready.md` confirms
its "Blocking reasons" section is unambiguously a bullet list, not a table.
SC-007 says both docs' "Blocking reasons tables" list HR9 -- a minor
terminology looseness (both are bulleted sections, not tables) that does not
change the substantive requirement (HR9 must appear in both docs' Blocking
Reasons content) but could cause an implementer to look for a Markdown table
syntax that is not there in either file.

### F6 -- SC-004's sentence construction is momentarily ambiguous on first read (LOW, cosmetic)

**Where**: spec.md SC-004.

"0 HR9 findings, or the HR9 rule's own source, contain a worked-example...
domain specific" reads, grammatically, as if it could mean "(0 HR9 findings)
OR (the HR9 rule's own source) contain[s]..." -- an odd construction pairing a
count with a source file under one shared verb. The clearly intended meaning
(confirmed by T041/T042's actual implementation: two independent zero
conditions -- no findings caused by worked-example names, AND no worked-example
literal in the rule's source) is unambiguous once cross-referenced against the
tasks, but the SC's own prose is momentarily confusing standing alone.

### F7 -- FR-014's "HR6 FR-017 precedent" citation is self-corrected by research.md but not by spec.md itself (LOW)

**Where**: spec.md FR-014 vs. research.md Sec 2.

Already noted under Terminology Consistency (Section 3) above: FR-014 cites
"the HR6 FR-017 precedent" as an existing pattern to mirror, but research.md's
own survey found HR6 has no shipped rule source anywhere in the tree -- only
references inside other in-flight, unshipped specs (092/103/105). research.md
correctly reframes this as "a NAMING CONVENTION the spec author is pointing
at... not a file to open or depend on," which prevents any actual
implementation risk (no task tries to read or depend on HR6 code). Listed here
because it is a real internal inconsistency between what FR-014's own wording
implies (an established precedent) and what research.md's own fact-check
found (no such shipped precedent exists) -- resolved in practice, but not
tidied up in spec.md's own text.

**No other contradictions, duplications, or unresolved ambiguities were found.**
The three genuine Clarifications (Q-CASE-SENSITIVITY, Q-BINDING-CELL-PARSE,
Q-MEASURE-SCOPE) are each resolved with a stated default, a stated reasoning,
and a stated reversibility, and are consistently referenced by the same names
across all six artifacts with no drift in what was decided.

---

## 6. Deferred-Capability Leakage Scan

Checked every mention of F016 (Power BI execution adapter) and "live"/"database"
surfaces across all six artifacts.

| Artifact | F016 / live-DB mentions | Posture |
|---|---|---|
| spec.md | Assumptions: "Live cross-check... is OUT OF SCOPE... deferred to the Power BI execution adapter (F016)" | Correctly deferred |
| plan.md | Constitution Check (Principle VIII row): "F016... is correctly treated as non-existent; HR9 does not call it, wait on it, or reference its API" | Correctly deferred |
| research.md | Sec 4 "Deferred capabilities NOT assumed": "F016... does not exist and is not assumed... never opens a live Power BI/PBIP connection" | Correctly deferred |
| data-model.md | No F016/live mention (N/A -- HR9 has no live entity) | Clean (no leakage) |
| tasks.md | T043 runs `retail check`/`retail kit-lint` on the committed tree (static only); no task opens a DB/PBIP connection or calls an adapter | Clean |
| quickstart.md | Sec 7 "What this quickstart does NOT cover": "It does not exercise F016 (the Power BI execution adapter) -- HR9 has no live/execution path to demonstrate" | Correctly deferred |

**Verdict**: CLEAN. No artifact assumes F016 exists, is callable, or will ship
before HR9. No artifact assumes a live database connection is available or
required. HR9 is consistently described, across all six documents, as having
"no live half to defer" by design (a referential-integrity-against-committed-text
check has no live analogue, unlike `retail validate`'s PK-uniqueness-on-
materialized-rows checks) -- this is a stated design property, not an omission,
and is accurate: no task, requirement, or scenario in this feature set requires
F016 or a live DB surface to exist for HR9 to be implemented or to function.

---

## 7. Overall Verdict

- **Requirement coverage**: 15/16 FRs cleanly covered; FR-007 flagged GAP due
  to F1 (T037's ambiguous no-op scoping), not due to missing task coverage.
- **Success criteria**: all 8 measurable and testable; SC-005's truth depends
  on F1 being resolved correctly at implementation time; SC-004's prose is
  cosmetically awkward but unambiguous once cross-referenced with T041/T042.
- **Terminology**: consistent throughout, with two LOW cosmetic nits (F5, F7)
  and one naming-convention footnote (module-file pattern) that is not a defect.
- **Constitution alignment**: PASS on Principles I, III, IV, V, VI, VII, VIII,
  IX, and hard rule #9. No violation found. The one open Principle-V item
  (Q-APPROVAL-SEAM) is correctly left OPEN rather than self-decided -- this is
  compliant behavior, not a defect.
- **Contradiction scan**: one MEDIUM-HIGH finding (F1) that, if carried
  literally into implementation, would break the feature's own P2 user story
  and SC-005 the moment it ships (since a TMDL model already exists elsewhere
  in the repo today); two LOW-MEDIUM/LOW findings (F2, F3) that are disclosed
  limitations, not contradictions; three cosmetic LOW findings (F4, F5, F6, F7).
- **Deferred-capability leakage**: CLEAN. No artifact assumes F016 or a live DB
  surface exists.

### scope_ok

true. No artifact violates the SCOPE GUARD (static cross-artifact reconcile
only; no auto-rename; no execution; no score) or any binding constitution
principle. F1-F7 are internal-consistency/task-authoring findings for the
BUILD stage to address, not constitution or scope-guard violations -- none of
them causes HR9 to execute code, open a live surface, decide a name, or emit a
score.

### open_principle_v

- Q-APPROVAL-SEAM (FR-016): genuinely open Principle-V question (does a
  clean HR9 run need its own named-human approval seam beyond existing
  Semantic Model Ready / Dashboard Ready sign-offs). Correctly left OPEN by
  spec.md, plan.md, and tasks.md T045 -- no artifact self-grants an answer.
  Flagged here per this stage's instructions as the one item requiring a human
  owner ruling; its being open is compliant, not a defect.
