# Specification Analysis Report: Cross-Table Column-Level Lineage / Impact Analysis

**Feature**: `099-cross-table-lineage-impact` | **Date**: 2026-07-04 | **Stage**: ANALYZE (read-only)

**Scope**: Cross-artifact consistency pass over `spec.md`, `plan.md`, `tasks.md`, `research.md`,
`data-model.md`, `quickstart.md`. No file other than this one was modified.

## Requirement-coverage table

| FR | Covering task/artifact | Status |
|----|------------------------|--------|
| FR-001 | T005 (input contract), T013 (metric-rooted entry) | OK |
| FR-002 | T005 (no DB/SQL/DAX/F016/F031-F033) | OK |
| FR-003 | T006 (fixed hop order), T013, T015 | OK |
| FR-004 | T007 (citation discipline), T015 | OK |
| FR-005 | T008 (evidence vocabulary, no invented edge), T015 | OK |
| FR-006 | T003 (forbidden-fields note), T004 (module contract), T022 (grep scan) | OK |
| FR-007 | T004, T018 (downstream_set no-obligation), T019 (closing note) | OK |
| FR-008 | T009 (missing/unreadable handling), T014 (US2 upstream gap) | OK |
| FR-009 | T004 (forbidden ops), T019, T020 (composes-only proof) | OK |
| FR-010 | T008, T013, T015 (fail-safe default only; explicitly NOT resolved) | OK (deliberately carved out, see Principle-V section) |
| FR-011 | T002 (generic placeholders only), T023 (generic-token scan) | OK |
| FR-012 | T002, T024 (encoding + path-budget sweep) | OK |
| FR-013 | T004, T021 (`retail check` unchanged rule count) | OK |
| FR-014 | T011 (column-rooted write path), T017 (metric-rooted write path) | OK |
| FR-015 | T010 (unresolved-starting-point branch) | OK |
| FR-016 | T008 (three-state vocabulary) | OK |

Coverage: 16/16 FRs have at least one covering task. 0 gaps. Tasks.md's own self-check (T026)
also asserts this; independently re-verified above by direct grep against tasks.md rather than
trusting the file's internal claim.

**Success-criteria coverage**:

| SC | Testability | Covering task |
|----|-------------|---------------|
| SC-001 | Testable (qualitative: "one artifact replaces manual search") | T012, T020 |
| SC-002 | Testable (100% of PROVEN hops cite a real path) | T007, T025 |
| SC-003 | Testable (0 score/count/health tokens) | T022 |
| SC-004 | Testable (0 obligation verbs on downstream items) | T018, T022 |
| SC-005 | Testable (git status shows exactly 1 new file, 0 modified) | T020 |
| SC-006 | Testable (generated Net-Sales hops do not contradict the hand-authored trace) | T016, quickstart Scenario B step 5 |
| SC-007 | Testable (0 worked-example domain tokens outside cited-instance paragraphs) | T023 |

All 7 Success Criteria are objectively testable (binary/grep-able), consistent with hard rule
#9's "no fabricated score" -- none of them smuggle in an implicit numeric health/confidence
metric.

## Terminology consistency

- The five-hop vocabulary (`source_map` / `migration_sql` / `metric_contract` / `tmdl_measure` /
  `dashboard_visual`) and the three evidence states (`proven` / `unresolved` / `gap`) are used
  identically across spec.md (FR-016, Key Entities), data-model.md (Entity 2), and tasks.md
  (T006, T008). No drift found.
- "Downstream set" (spec Key Entities) equals `downstream_set` (data-model.md Entity 4) equals
  the object T018/T019 constrain. Consistent.
- "Starting point" / `kind` (`column` | `metric`) is consistent across spec FR-001, data-model.md
  Entity 1, and tasks T005/T013.

## Constitution alignment

Checked against `.specify/memory/constitution.md`'s nine numbered principles plus hard rule #9.

- **Principle I (Agent-First, Gate-Enforced)**: Correctly scoped as non-binding in the "fails
  closed" sense -- this feature adds no `retail check` rule (FR-013), so there is no gate to fail
  open/closed. Plan.md's analog framing ("fail-safe module behavior" rather than "fail-closed
  gate") is an accurate, non-diluting substitution -- it does not weaken Principle I's actual
  binding surface. PASS.
- **Principle II (Depend, Never Fork)**: Not addressed in plan.md's Constitution Check (no
  section for it). This is not a violation -- Principle II binds the Power BI execution-adapter
  relationship, and this feature has zero adapter/engine surface (FR-002, FR-013). Its omission
  from the explicit per-principle walk is a minor completeness gap, not a compliance failure. See
  finding F3 (LOW).
- **Principle III (Medallion, Postgres-First, Gold-Only)**: The module only reads already-existing
  gold-referencing SQL/TMDL text; asserts no new schema. PASS.
- **Principle IV (Source Mapping Before Silver)**: No SQL of any kind is authored by this feature;
  an unapproved/missing source-map is recorded as a GAP/blocker (FR-015), never treated as
  implicitly `pass`. PASS.
- **Principle V (Agent Stops at Judgment Calls)**: This is the principle the feature is explicitly
  built around. FR-010 is a genuine, correctly-unresolved NEEDS CLARIFICATION item -- an OPEN
  owner ruling on whether any name-similarity matching method may ever promote a candidate link to
  proven. The spec's Clarifications section, the plan's Constitution Check, and tasks.md's
  "Principle-V carve-out" section all agree: ship the fail-safe default (candidate-only, never
  silently promoted) and leave the ruling open. This is compliant, not a violation -- Principle V
  requires raising and stopping, not resolving, and that is exactly what happened. PASS.
- **Principle VI (Defaults Then Deviations)**: FR-014's output-path convention
  (`mappings/<table>/lineage-column-<column>.md` / `lineage-metric-<Metric>.md`) is correctly
  classified as a reversible, non-Principle-V default (matches existing `mappings/<table>/`
  co-location precedent). PASS.
- **Principle VII (C086 Is An Example, Not The Schema)**: FR-011 and data-model.md's closing
  paragraph correctly confine `retail_store_sales` specifics to one cited-instance paragraph; the
  template (T002) and SKILL.md fixed section labels (T004-T019) use only generic placeholders.
  T023 provides the enforcing scan. PASS.
- **Principle VIII (Static-First Governance, Live Deferred)**: The module reads only committed
  repo text; FR-002 explicitly forbids DB/SQL/DAX/live-PBIP/F016/F031-F033. No live surface is
  even marked PENDING because none is needed. PASS. See also the deferred-capability leakage scan
  below -- no leakage found.
- **Principle IX (Secrets and Reproducibility)**: No host/DSN/secret is read or written anywhere
  in the five input families (schema/SQL/YAML/TMDL/Markdown only). FR-012 mandates ASCII, UTF-8
  no BOM, `--`/`->` glyph substitution, short repo-relative paths. PASS.
- **Hard rule #9 (no fabricated confidence/health/maturity/completeness score)**: FR-006 and
  data-model.md's "Forbidden fields" list explicitly bar `blast_radius_score`, `confidence`,
  `health`, `maturity`, `artifacts_affected_count`, `priority`, `risk_level`,
  `recommended_action`. T003 and T022 both enforce this at the template and scan level. PASS.

**No CRITICAL constitution violation found.** `scope_ok = true`. FR-010 is surfaced in
`open_principle_v` below as the one genuinely open Principle-V judgment call this feature
correctly raises and does not resolve -- that is compliant behavior, not a violation.

## Deferred-capability leakage scan

Searched all six artifacts for F016 (Power BI execution adapter) and F031-F033 (adapter
maintenance automation, spec-only/no-consumer) references:

- `spec.md:233`, `plan.md:58,135,153`, `research.md:131-134`, `tasks.md:38,98,121` all mention
  F016/F031-F033 exclusively in a "does NOT exist / MUST NOT invoke / is not invoked" framing.
- No artifact assumes F016 is reachable, callable, or that a live Power BI/PBIP surface exists.
- No artifact assumes a live DB connection; `retail validate` (DB-connected) is explicitly named
  as out-of-scope territory in quickstart.md's closing section.

**No deferred-capability leakage found.**

## Contradiction / duplication / ambiguity scan

### F1 -- Internal self-contradiction on F024 capability level (research.md)

- **Category**: Inconsistency
- **Severity**: HIGH
- **Location(s)**: `research.md:68` vs `research.md:82-84`
- **Summary**: Section 1.4 first states the capability level for this feature is `read-only`
  ("`artifact-writing` there [F035]; `read-only` here... see Clarification below on why
  `read-only` is still the correct capability level"), then two paragraphs later concludes the
  opposite for the same feature: "so per the F024 matrix it is `artifact-writing`, matching
  F027/F028/F035, not `read-only`." These two statements about the same feature's same field
  directly contradict each other within one document.
- **Recommendation**: Delete or rewrite the parenthetical at line 68 (the "`read-only` here...
  correct capability level" clause) since it is superseded by the corrected reasoning at
  lines 82-84. The rest of the design (plan.md line 184, tasks.md T004) already correctly lands
  on `artifact-writing`, so this is a self-inflicted contradiction isolated to research.md's
  first pass, not a disagreement that propagated into the design. Low-risk fix: strike the
  outdated clause, keep the corrected one.

### F2 -- Spec's own "read-only" framing is a term-of-art collision, not a defect, but is easy to
misread

- **Category**: Ambiguity
- **Severity**: LOW
- **Location(s)**: `spec.md:29,94,260,281,339` (feature framing, SCOPE GUARD, FR-013, FR-009) vs
  `plan.md:184-186`, `research.md:76-89` (F024 capability level = `artifact-writing`)
- **Summary**: The spec repeatedly calls this a "read-only Product Module" / "read-only skill" in
  its narrative framing (input discipline: reads only, invents no truth), while the F024
  three-level vocabulary this same repo defines (`read-only | artifact-writing |
  execution-capable`) reserves `read-only` for modules that write no artifact at all -- a category
  this feature does not belong to, since it writes one derived lineage file per run. Plan.md and
  research.md (once F1 above is fixed) correctly disambiguate this, but a reader who only reads
  spec.md could reasonably expect the F024 declared capability level to be `read-only`, which
  would be wrong.
- **Recommendation**: No spec.md edit is required (the task instructions for this stage are
  read-only), but flag this for a future spec revision: add one clarifying parenthetical in
  spec.md's Overview or scope-guard line (e.g. "read-only in the sense of never writing back to
  what it reads; the F024 capability-level field this module declares is artifact-writing, since
  it writes its own derived output") to pre-empt the same confusion research.md's first draft
  fell into (F1).

### F3 -- Constitution Check omits Principle II without saying so

- **Category**: Underspecification
- **Severity**: LOW
- **Location(s)**: `plan.md:68-161` (Constitution Check section)
- **Summary**: The Constitution Check walks Principles I, III, IV, V, VI, VII, VIII, IX plus hard
  rule #9 and the F016 assumption, explicitly labeling each PASS. Principle II (Depend, Never
  Fork) is silently absent -- there is no "Principle II: N/A because..." line the way other
  not-fully-applicable items get an explicit disposition elsewhere in the repo's plan-template
  convention.
- **Recommendation**: Not a compliance failure (Principle II genuinely does not bind a feature
  with zero adapter/engine surface), but for audit completeness a one-line "Principle II: N/A --
  this feature touches no execution adapter" would remove any appearance of an overlooked
  principle. Low priority; does not block anything.

### F4 -- "Every one of the six shipped Product Modules" count is unverified/possibly imprecise

- **Category**: Ambiguity / possible inaccuracy
- **Severity**: LOW
- **Location(s)**: `research.md:77` ("Every one of the six shipped Product Modules that writes
  anything (F027, F028, F035)...")
- **Summary**: The parenthetical names only three Product Modules (F027, F028, F035) as evidence
  for a claim about "six shipped Product Modules." The sentence is ambiguous: it could mean "six
  shipped Product Modules total, of which these three write something," or it could be a
  miscount. The roadmap excerpt retrieved during this analysis shows F025-F028, F035 explicitly
  tiered as Product Modules (F026/F027/F028/F035 confirmed artifact-writing or read-only
  entries), which is close to but not exactly reconciled against "six" in this file.
  Non-blocking, since the FR-level claims this sentence supports (that artifact-writing is the
  correct capability level) do not depend on the exact count being six vs. some other number.
- **Recommendation**: If research.md is ever revised, either name all six explicitly or drop the
  specific count and say "the shipped Product Modules that write anything."

### F5 -- SC-001's "replacing a manual multi-folder search" is a qualitative, not strictly
measurable, outcome

- **Category**: Ambiguity (mild)
- **Severity**: LOW
- **Location(s)**: `spec.md:329-331` (SC-001)
- **Summary**: Unlike SC-002 through SC-007 (all binary/grep-able), SC-001 is phrased as a
  qualitative capability statement ("a reader can obtain... one artifact... replacing a manual
  multi-folder search") rather than a hard measurable threshold. It is still testable in the
  narrow sense the Independent Test in User Story 1 supplies (an artifact is in fact produced
  with all committed hops), so this is not a genuine coverage gap, but it is the one Success
  Criterion that reads more like a restated goal than a measurable outcome.
- **Recommendation**: No action required for this stage; SC-001 is adequately anchored by User
  Story 1's Independent Test and by T012/T020. Could be tightened in a future revision to name
  the exact artifact-existence check, mirroring SC-002's precision.

### F6 -- research.md's F039 roadmap-number proposal depends on a race condition against a
sibling in-flight spec, correctly resolved but worth flagging as a fragile cross-file assumption

- **Category**: Inconsistency (latent, not manifest)
- **Severity**: LOW
- **Location(s)**: `plan.md:235-241`, `research.md:91-110` vs
  `specs/101-consumer-data-dictionary/plan.md:244-251` and
  `specs/101-consumer-data-dictionary/research.md:92-106`
- **Summary**: This feature's plan/research propose F039 as the next unclaimed Product Module
  roadmap slot. A parallel in-flight sibling feature (101-consumer-data-dictionary) independently
  greps for the same unclaimed slot and, finding F039 already proposed by 099, correctly steps
  aside to propose F040 instead. This is not a current contradiction (101 explicitly defers to
  099's claim), but it is a soft, order-dependent cross-file assumption: if 099's number is ever
  revised at integration time, 101's F040 proposal (and any other sibling that greps the same
  pattern) inherits a stale assumption. Both files already say the true reconciliation happens at
  integration time and neither self-assigns the ledger row, so this is correctly hedged, not a
  defect requiring a fix in 099 itself.
- **Recommendation**: No action needed within 099's own artifacts. Note for whoever performs the
  integration-time roadmap-ledger edit: confirm both 099 (F039) and 101 (F040) against the
  then-current ledger state before committing either row, since both plans were authored against
  the same July 2026 snapshot of docs/roadmap/roadmap.md.

## Duplication detection

No near-duplicate Functional Requirements were found. FR-005 and FR-010 both touch "unresolved
candidate link" language, but this is deliberate cross-referencing (FR-010 explicitly says "see
FR-010" from within FR-005 and vice versa), not duplication -- they describe the same fail-safe
default from two angles (general rule vs. the specific OPEN owner-ruling case) and are already
kept as one canonical concept, not two competing rewordings. No consolidation needed.

## Metrics

- Total Functional Requirements: 16 (FR-001..FR-016)
- Total Success Criteria (buildable/testable): 7 (SC-001..SC-007)
- Total Tasks: 26 (T001-T026)
- Requirement coverage: 16/16 = 100%
- Success-criteria coverage: 7/7 = 100%
- Ambiguity findings: 3 (F2, F4, F5 -- all LOW)
- Duplication findings: 0
- Inconsistency findings: 3 (F1 HIGH, F3 LOW, F6 LOW)
- Critical issues: 0
- Constitution violations: 0

## Next actions

- No CRITICAL issues exist; this feature is not blocked from proceeding.
- Recommended before merge: fix F1 (research.md's self-contradicting capability-level sentence
  at line 68) -- it is a HIGH-severity internal contradiction in a committed research artifact,
  cheap to correct (delete one outdated clause), and the kind of thing a future reader citing
  research.md in isolation could get wrong even though the rest of the design already landed
  correctly on artifact-writing.
- F2/F3/F4/F5/F6 are LOW severity; none block implementation. They are optional polish for a
  future spec/research revision, not required rework.
- FR-010 is the one genuinely open Principle-V judgment call this feature correctly raises and
  does not resolve; it is surfaced in the stage's open_principle_v output, not treated as a
  violation.

## Remediation offer

This report is READ-ONLY per the ANALYZE stage's operating constraint -- no file besides this
analysis.md was modified. If a remediation pass is wanted for F1 (the one HIGH finding), it
would be a single targeted edit to research.md lines 66-71 (strike the outdated "read-only
here... correct capability level" clause) -- but that edit is explicitly out of scope for this
stage and is not applied here.
