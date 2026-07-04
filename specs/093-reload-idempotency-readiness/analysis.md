# Specification Analysis Report: Reload / Idempotency Readiness (Anti-Double-Count)

**Feature**: `093-reload-idempotency-readiness` (gap #16, rule id HR7) | **Date**: 2026-07-04 | **Stage**: ANALYZE (read-only)

**Scope**: cross-artifact consistency pass over `spec.md`, `plan.md`, `tasks.md`, `research.md`,
`data-model.md`, `quickstart.md`. No file other than this one was modified. Facts below were
cross-checked against the live tree (`src/retail/sql.py`, `src/retail/rules/__init__.py`,
`warehouse/migrations/*.sql`, `docs/rules/rules-manifest.json`, `docs/glossary.md`,
`docs/readiness/gold-ready.md`, `src/retail/validate.py`), not merely trusted from the artifacts'
own prose.

## Requirement-coverage table

| FR | Covering task/artifact | Status |
|----|------------------------|--------|
| FR-001 (register HR7; gold-schema signal, never filename) | T005, T017 | OK |
| FR-002 (classify FULL_DROP_AND_REBUILD vs DEVIATION, incl. whole-table TRUNCATE/DELETE) | T018, T019, T033, T016b | OK |
| FR-003 (default passes free, no declaration required) | T015, T019 | OK |
| FR-004 (two allowed declaration locations; reload-strategy marker shape; never source-map.yaml) | T004, T022, T023, T029-T032, T041 | OK |
| FR-005 (fail CLOSED with ERROR Finding on undeclared deviation) | T021, T033 | OK |
| FR-006 (in-SQL key satisfies requirement without redundant marker) | T025, T026, T029, T032 | OK |
| FR-007 (static-only: read committed files, no DB) | T005, T035 | OK |
| FR-008 (bare structural/readability check; key presence AND syntactic plausibility; never semantic/live verification) | T030 (parse only), T035 (no-DB-import check) | **OK with caveat -- see F1** |
| FR-009 (never claim/imply a pass proves live idempotency; RC2/RC16 remain the live proof) | T003, T036, T037, T038, T039 | OK |
| FR-010 (no execution, no DB connection, no db extra/DSN dependency) | T005, T024, T035, T039 | OK |
| FR-011 (never re-decide grain/PK; not HR1's territory) | T041 | OK |
| FR-012 (no numeric score, no "N of M" tally) | T036, T040 | OK |
| FR-013 (OPEN Principle-V question -- approval seam for full-rebuild-to-incremental transition) | T044 (checklist confirmation only; not answered) | OK (correctly left open, not a gap) |
| FR-014 (warehouse/load-policy.md optional, new, distinct from source-map.yaml) | T002, T004, T023, T024, T031 | OK |
| FR-015 (generic; no baked-in table/column/C086 name in rule logic) | T042 | OK |
| FR-016 (ASCII, UTF-8 no BOM, short repo-relative paths) | T045 | OK |
| FR-017 (additive; no change to S6/S7/HR1/RC-series Finding text or outcome) | T043, T046, T047 | OK |

Coverage: 17/17 FRs have at least one covering task, independently re-verified above rather than
trusting tasks.md's own "Requirement Coverage Check" section at face value (that section's map
was used as a starting index, then checked line-by-line against tasks.md's actual task bodies).
0 requirements are orphaned. FR-013 is intentionally left un-resolved (Principle V) and is
correctly represented as a checklist-only task (T044), not a build task -- this is compliant
scoping, not a coverage gap.

**Success-criteria testability**:

| SC | Testability | Covering task(s) |
|----|-------------|-------------------|
| SC-001 (100% of committed gold migrations pass with zero Findings, no edits required) | Testable (binary: run against real tree) | T016, T020, T046 |
| SC-002 (bare-append-no-key -> exactly one ERROR; declaring a key clears it, no other change) | Testable (binary: Finding count before/after) | T021, T022, T023, T034 |
| SC-003 (0 Findings/pass messages contain a numeric score or "N of M" count) | Testable (grep/regex-able) | T036, T040 |
| SC-004 (0 evaluations open a DB connection / depend on DSN or db extra) | Testable (source-inspection, grep-able) | T035, T039 |
| SC-005 (wiring/rule-count lockstep stays green; only HR7 added) | Testable (existing meta-gate test suite) | T012, T043, T046, T047 |
| SC-006 (0 HR7 artifacts contain a domain-specific name outside a labeled illustrative example) | Testable (grep-able) | T042 |

All 6 Success Criteria are objectively testable (binary/grep-able), consistent with hard rule #9
-- none smuggles in an implicit numeric health/confidence/maturity metric. No SC is a restated
goal; all six read as hard, mechanically checkable thresholds.

## User-story -> task coverage

- **US1** (drop-and-rebuild passes free, P1) -> Phase 3 (T013-T020). Acceptance Scenarios 1-3 all
  covered (T014/T015 for scenarios 1-2, T016 for scenario 3 against the real committed set).
  COVERED.
- **US2** (undeclared deviation fails closed, P1) -> Phase 4 (T021-T034). Acceptance Scenarios 1-3
  covered (T021 for scenario 1, T022/T023 for scenario 2's two limbs, T025/T026 for scenario 3's
  two limbs). COVERED.
- **US3** (static-only, no live-proof claim, P2) -> Phase 5 (T035-T040). Independent Test and both
  Acceptance Scenarios covered (T035 for the no-DB-driver check, T036/T037 for the no-live-proof-
  claim check, T039 for the blocked-deferred non-interference check). COVERED.

No user story lacks a task; no task is orphaned from a story or requirement (Phase 6 Polish tasks
map to cross-cutting FRs: FR-011/FR-015/FR-016/FR-017, plus FR-013's checklist confirmation).

## Terminology consistency

- **ReloadStrategy** (FULL_DROP_AND_REBUILD | DEVIATION) is used identically across spec.md
  (FR-002, Key Entities), data-model.md (the enum definition), and tasks.md (T018's docstring,
  T019/T033). No drift.
- **reload-strategy: key1[, key2...]** marker shape is stated identically in spec.md
  (FR-004, Clarifications "Q-DECL-SHAPE"), data-model.md ("The reload-strategy marker" section),
  research.md ("Declaration marker" row), and quickstart.md ("Confirm a declaration clears the
  Finding"). No drift.
- **"Declaration" vs "key"**: spec.md, data-model.md, and tasks.md consistently distinguish "a
  declared key exists" (structural, FR-008) from "the key is correct" (semantic, out of scope) --
  the same distinction is preserved verbatim in plan.md's Constraints and quickstart.md's "What
  HR7 never does." Consistent.
- **HR1 vs HR7 boundary language** ("Boundary against neighbouring shipped work") is repeated
  near-verbatim across spec.md's boundary section and research.md's "HR-series static Gold-Ready
  rule precedent" bullet -- both correctly state HR1 = cross-star dimension shape, HR7 = single-
  table reload safety, reading disjoint artifacts. Consistent; not duplication (deliberate
  cross-referencing to prevent scope bleed between two parallel HR-series features).
- **Rule id HR7** is fixed and used consistently everywhere (never referred to by a placeholder
  or a different id in any of the six artifacts).

## Constitution alignment

Checked against the nine numbered Principles plus hard rule #9, per plan.md's own per-principle
walk, independently re-verified against spec.md/data-model.md/tasks.md rather than trusting
plan.md's PASS labels at face value.

- **Principle I (Agent-First, Gate-Enforced)**: PASS. FR-005 requires HR7 to fail CLOSED with an
  ERROR Finding on an undeclared deviation -- it never merely warns on the case the feature exists
  to catch (contrast with S6/S7's WARNING "override-when" posture, correctly distinguished in
  research.md). Compliance is demonstrable by running `retail check` (verified: HR7 registers into
  the same registry S1-S8/G6 already use).
- **Principle II (Depend, Never Fork)**: N/A, not addressed in plan.md's Constitution Check as its
  own line. Not a violation -- this feature has zero Power BI execution-adapter surface (no F016
  interaction whatsoever). Its omission from the explicit per-principle walk is a minor
  completeness gap in plan.md's own document, not a compliance failure (see F4, LOW).
- **Principle III (Medallion/Gold-Only)**: PASS. HR7 reads only `warehouse/migrations/` SQL text
  and, if present, `warehouse/load-policy.md`; it does not touch bronze/silver data, does not open
  a Power BI surface, and does not alter the gold Kimball star shape S6/S7/S8 already enforce.
- **Principle IV (Source-Mapping-Before-Silver)**: PASS (non-interaction). HR7 is a Gold-Ready
  check that runs strictly after silver SQL exists; it does not read or write `source-map.yaml`
  at all (verified: FR-004's collision-avoidance allocation is honored across spec/plan/data-model
  /tasks -- T041 is a dedicated source-inspection test for exactly this).
- **Principle V (Agent-Stops-at-Judgment)**: PASS. HR7 never decides whether a table should move to
  an incremental load, never picks a dedup key, and never self-grants a Gold Ready `pass`. FR-013 /
  Q-APPROVAL-SEAM is the one genuine judgment call this feature surfaces -- spec.md's
  Clarifications section, plan.md's Constitution Check, and tasks.md's T044 all agree: ship the
  PENDING mechanical default, leave the ruling open, never decide it unilaterally. This is
  compliant Principle-V behavior (raise-and-stop), not a violation.
- **Principle VI (Defaults-Then-Deviations)**: PASS -- this is the feature's design center. Full
  drop-and-rebuild is the default and costs nothing (FR-003, SC-001, independently confirmed
  against the real `0004` migration during this analysis: it is genuinely `DROP TABLE IF EXISTS`
  + clean `INSERT...SELECT` with no `ON CONFLICT`, no bare append, no partition overwrite). Only a
  deviation must declare anything.
- **Principle VII (C086-Is-An-Example-Not-The-Schema)**: PASS. FR-015/SC-006/T042 keep rule logic
  and doc updates free of a baked-in table/column name; the worked example
  (`retail_store_sales`/`0004_...sql`) is cited only illustratively.
- **Principle VIII (Static-First/Live-Deferred)**: PASS. HR7 reads only committed files, never
  connects to a database, never executes or simulates a reload (FR-007/FR-010, SC-004,
  independently confirmed: `src/retail/rules/sql.py`'s S1-S8 precedent this feature reuses
  contains no DB driver import, and no artifact instructs HR7 to add one). See also the
  deferred-capability leakage scan below -- no leakage found.
- **Principle IX (Secrets/Reproducibility)**: PASS. No host/DSN/secret is read or written anywhere.
  FR-016 mandates ASCII, UTF-8 no BOM, short repo-relative paths; plan.md's Constraints additionally
  require `warehouse/load-policy.md` to be read gated on `ctx.tracked_files` membership (never the
  raw working tree) -- T024 is a dedicated test for exactly this untracked-copy-must-not-count case.
- **Hard rule #9 (No Fabricated Confidence)**: PASS. HR7's only outcomes are "no Finding" or an
  ERROR Finding naming the missing declaration (FR-012); no numeric score, health/maturity band, or
  "N of M" tally is ever emitted (SC-003, T036/T040).
- **F016 (Power BI execution adapter)**: N/A / not assumed to exist. HR7 never invokes it, directly
  or indirectly -- confirmed by review of every artifact; no mention of F016 exists outside
  plan.md's own "N/A" disposition line.

**No CRITICAL or HIGH constitution violation found. scope_ok = true.** FR-013 (Q-APPROVAL-SEAM)
is surfaced in `open_principle_v` below as the one genuinely open Principle-V judgment call this
feature correctly raises and does not resolve -- that is compliant behavior per Principle V
("agent stops at judgment"), not a violation of it.

## Deferred-capability leakage scan

Searched all six artifacts for assumptions that F016 (Power BI execution adapter) or a live DB
surface already exists:

- spec.md's Boundary section, User Story 3, and Assumptions section; plan.md's Technical Context,
  Constitution Check, and Complexity Tracking; research.md's "Deferred capabilities NOT assumed"
  section; tasks.md's T035/T039 -- all mention the live surface (RC2/RC16, `retail validate`, `db`
  extra, DSN) exclusively in a "stays deferred / HR7 does not touch this / remains PENDING" framing.
- No artifact assumes F016 is reachable or callable; the one explicit mention (plan.md "F016...
  N/A / not assumed to exist") is a correct negative disposition, not an assumption of existence.
- No artifact assumes a live DB connection is available at build or CI time; quickstart.md's
  "Confirm HR7 stays static-only" step explicitly instructs inspecting the module for the absence
  of a DB driver import rather than assuming one could safely be added later.
- `warehouse/load-policy.md` (the one new artifact this feature's shape touches) is explicitly
  documented as NOT created by this feature and its absence is explicitly required to be a
  non-ERROR condition (data-model.md, Edge Cases) -- consistent with Principle VIII's "author
  static structure, mark live PENDING" posture, correctly applied here to a static (not live)
  optional file rather than to a DB surface.

**No deferred-capability leakage found.**

## Contradiction / duplication / ambiguity scan

### F1 -- FR-008's "syntactically plausible column identifier" sub-clause is untasked and untested (MEDIUM)

- **Category**: Test-coverage gap / underspecification
- **Severity**: MEDIUM
- **Location(s)**: spec.md:257-265 (FR-008), data-model.md:73-74 (ReloadStrategyDeclaration.keys:
  "Each key MUST look like a syntactically plausible column identifier"), tasks.md T030/T032/T035
- **Summary**: FR-008 has two sub-requirements: (a) confirm a key is *named* (presence), and (b)
  confirm the named key(s) are *syntactically plausible column identifiers* (a shape/readability
  check on the key text itself, distinct from a live-schema existence check). Tasks.md's
  Requirement Coverage Check maps FR-008 to T030 alone, annotated "structural marker parse only, no
  live-schema check -- implicit in _scan_reload_strategy_markers/_has_declaration never
  querying a DB." That annotation only defends the "never live-verify" half of FR-008. T030's own
  description ("Returns the parsed, comma-separated key list") is a bare parse/split, not a
  plausibility check on each resulting token -- nothing in T030, T032, T014-T027, or T035-T037
  asserts what happens for a key value that fails the plausibility test (e.g. a marker with no key
  text at all, `reload-strategy:` with an empty list; a key containing whitespace or SQL-punctuation
  that could never be a column identifier; a marker with malformed syntax). No fixture in Phase 3-5
  exercises this negative path.
- **Recommendation**: Not a blocker for this stage (ANALYZE is read-only), but before Phase 4/US2
  implementation lands, add one task (or extend T030/T032) that defines what "syntactically
  plausible" mechanically means (e.g. a regex over identifier-shaped tokens) and one test asserting
  a malformed/empty key list is treated as "no valid declaration" (contributing to FR-005's ERROR
  Finding, not silently accepted as a pass). Without this, an author could satisfy HR7 with a
  marker like `reload-strategy:` (no keys) or a garbage-text key and the rule's behavior in that
  case is currently unspecified by any task.

### F2 -- research.md groups reused SQL helpers under a `src/retail/rules/sql.py` heading, but their actual definitions live in `src/retail/sql.py` (LOW)

- **Category**: Minor inaccuracy (attribution), non-blocking
- **Severity**: LOW
- **Location(s)**: research.md:9 ("The static SQL-rule family (src/retail/rules/sql.py: S1-S8...)"),
  research.md:45 (same file cited again) vs. plan.md:41-44 (correctly: "Reuses src/retail/sql.py's
  existing tokenize_sql, schema_zone, iter_sql_files")
- **Summary**: Verified against the live tree: `tokenize_sql`, `schema_zone`, and `iter_sql_files`
  are defined in `src/retail/sql.py` (confirmed by direct grep for their `def` statements);
  `is_test_path` is defined in `src/retail/core.py`. `src/retail/rules/sql.py` imports these names
  and hosts the S1-S8 rule *implementations* -- the "static SQL-rule family" framing in research.md
  is itself accurate (S1-S8 do live in `src/retail/rules/sql.py`), but the same heading also lists
  the reusable helper functions as if they too live there, which is imprecise. plan.md's Primary
  Dependencies line already states the correct attribution. This is a soft, self-resolving
  imprecision (the correct file is stated elsewhere in the same feature's own plan.md), not a
  genuine cross-artifact contradiction that would mislead an implementer, since T005 (the task that
  actually writes the import) will fail fast against the real module layout if it imports from the
  wrong path.
- **Recommendation**: No spec/plan edit required for this stage. If research.md is ever revised,
  correct lines 9 and 45 to cite `src/retail/sql.py` for the helper functions specifically (keeping
  the `src/retail/rules/sql.py` citation for the S1-S8 rule-family precedent, which is correct as
  written).

### F3 -- Glossary's family-count anchor will need a new "HR" family entry, not just a number bump, and no existing lockstep test catches this (LOW)

- **Category**: Latent inconsistency / gate gap (order-dependent)
- **Severity**: LOW
- **Location(s)**: docs/glossary.md:101 (live tree: "Currently 55 rules in 21 families (S, D, C,
  R, RS, G, P, A, B, PP, SC, DF, SL, AL, AD, AQ, DL, CT, DR, AP, SF)" -- confirmed zero HR entries
  present) vs. tasks.md T010 ("update the rule-count anchor text to the new live total")
- **Summary**: Confirmed against the live tree that `src/retail/rules/**/HR1*` does not exist yet
  (087/HR1 is not merged) and `docs/rules/rules-manifest.json` has zero entries starting with HR.
  If this feature (093/HR7) lands before 087/HR1, HR7 becomes the FIRST rule in a brand-new HR
  family -- meaning T010's edit needs to bump BOTH the rule count (55->56) AND the family count
  (21->22) AND add HR to the parenthetical prefix list. T010's own wording only names "the
  rule-count anchor text to the new live total," which reads as the integer count alone; it does
  not explicitly call out the family-list edit. This gap would NOT be caught by the automated
  lockstep: test_glossary_rule_table.py checks id-bijection (every live rule id appears
  backtick-quoted in the glossary table), and rule-count-claims.yaml/SC2 checks only the integer
  count claim -- neither validates the "21 families" / prefix-list prose, so a stale family count
  would silently pass CI. This is the same class of order-dependent race risk other cross-artifact
  analyses in this repo have flagged when two features contend for a shared ledger/anchor -- here,
  093 (HR7) versus 087 (HR1) for which one first claims the "HR" family slot.
- **Recommendation**: Not a blocker for this stage. When T010 is executed, the implementer should
  read the live family-prefix list at that time (not copy the "21 families... S, D, C... SF" string
  verbatim) and add HR explicitly if HR7 lands first, exactly the same "read live, never hardcode"
  discipline research.md already applies to the rule count itself.

### F4 -- Constitution Check omits Principle II without an explicit "N/A" disposition (LOW)

- **Category**: Underspecification (documentation completeness)
- **Severity**: LOW
- **Location(s)**: plan.md:88-142 (Constitution Check section)
- **Summary**: The Constitution Check walks Principles I, III, IV, V, VI, VII, VIII, IX plus hard
  rule #9 and the F016 assumption, labeling each PASS/N/A. Principle II (Depend, Never Fork) has no
  explicit line. This is not a compliance failure -- Principle II binds the Power BI execution-
  adapter relationship, and this feature has zero adapter/engine surface -- but for audit
  completeness the other "not fully applicable" items (F016) do get an explicit disposition while
  Principle II is silently absent.
- **Recommendation**: Optional polish; a one-line "Principle II: N/A -- this feature touches no
  execution adapter" would remove any appearance of an overlooked principle. Does not block.

## Duplication detection

No near-duplicate Functional Requirements were found. FR-004 and FR-006 both touch "what
satisfies the declaration requirement," but this is deliberate complementary scoping (FR-004
defines the two allowed OUT-OF-BAND declaration locations; FR-006 defines the IN-SQL alternative
that needs no separate marker) rather than a restatement of the same rule from two angles that
should be merged. FR-002 and its Clarifications "Q-TRUNCATE-CLASS" entry restate the same
whole-table-TRUNCATE default across spec.md's Requirements and Clarifications sections, but this
is the documented pattern this repo already uses everywhere (spec.md Clarifications record the
session ruling; the FR encodes the resulting rule) -- not accidental duplication.

## Metrics

- Total Functional Requirements: 17 (FR-001..FR-017)
- Total Success Criteria (buildable/testable): 6 (SC-001..SC-006)
- Total Tasks: 48 (T001-T047, plus T016b)
- Requirement coverage: 17/17 = 100% (one, FR-008, OK-with-caveat per F1)
- Success-criteria coverage: 6/6 = 100%
- Ambiguity findings: 1 (F2, LOW)
- Duplication findings: 0
- Inconsistency / gap findings: 3 (F1 MEDIUM, F3 LOW, F4 LOW)
- Critical issues: 0
- Constitution violations: 0

## Next actions

- No CRITICAL or HIGH issues exist; this feature is not blocked from proceeding to implementation.
- Recommended before or during Phase 4 (US2) implementation: resolve F1 -- define and test the
  "syntactically plausible column identifier" negative path (an empty or malformed key list) so
  FR-008's full text, not just its no-live-verification half, is mechanically enforced.
- F2/F3/F4 are LOW severity and non-blocking: F2 is a one-line attribution fix in research.md if
  ever revised; F3 is a reminder for whoever executes T010 to check the live family-prefix list
  (not copy the current string verbatim) if HR7 lands before HR1; F4 is optional Constitution Check
  completeness polish.
- FR-013 (Q-APPROVAL-SEAM) is the one genuinely open Principle-V judgment call this feature
  correctly raises and does not resolve; it is surfaced in `open_principle_v` below, not treated as
  a violation.

## Remediation offer

This report is READ-ONLY per the ANALYZE stage's operating constraint -- no file besides this
analysis.md was modified. If a remediation pass is wanted for F1 (the one MEDIUM finding), it
would be a targeted addition to tasks.md Phase 4 (one new task defining the plausibility check plus
one new test asserting the malformed/empty-key negative path) -- but that edit is explicitly out of
scope for this stage and is not applied here.

