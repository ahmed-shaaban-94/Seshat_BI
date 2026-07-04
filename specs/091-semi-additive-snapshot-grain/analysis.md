## Cross-Artifact Analysis: Semi-Additive (Snapshot) Grain in the Metric Contract

Feature: 091-semi-additive-snapshot-grain | Date: 2026-07-04 | Stage: ANALYZE (read-only)

Scope: spec.md, plan.md, tasks.md, research.md, data-model.md, quickstart.md under
specs/091-semi-additive-snapshot-grain/. This document is the ONLY file written by this
stage. No other artifact was modified.

---

### 1. Requirement-Coverage Table

Every functional requirement and success criterion in spec.md, independently traced to its
covering task(s)/artifact(s) (derived directly from tasks.md content, not transcribed from its
own trace table).

| Requirement | Covering task/artifact | Status |
|---|---|---|
| FR-001 (new optional time_additivity field, documented) | T004 | OK |
| FR-002 (closed vocabulary fully/semi/non) | T004 (schema comment), T010/T011 (enforcement) | OK |
| FR-002a (exact case-sensitive, untrimmed match) | T004, T009 (test: Fully/SEMI/non-with-space), T010, T011 | OK |
| FR-003 (classification only, no DAX/SQL/business restatement) | T004, T019 (genericness grep) | OK |
| FR-004 (HR5 ERRORs on A10 + missing field) | T005 (scaffold), T006 (test), T008, T011 | OK |
| FR-004a (exact-string A10 id match, no near-miss) | T007 | OK |
| FR-004b (null/empty collapses to missing, not out-of-vocab) | T009 (test), T010, T011 | OK |
| FR-005 (ERROR on A10 + fully, distinct message) | T006 (test), T008 | OK |
| FR-006 (ERROR on out-of-vocabulary, never inferred) | T009 (test), T010, T011 | OK |
| FR-006a (non-scalar treated as out-of-vocab, no crash) | T009 (test), T010 | OK |
| FR-007 (no A10 + no field means not required, no finding) | T009 (test), T011 | OK |
| FR-008 (no read/alter of AD1 corpus or legality table) | T005, T018 | OK |
| FR-009 (ERROR-only, no numeric/graded output) | T008, T011, T018 | OK |
| FR-010 (no DAX/DB/network/visual execution) | T005, T018 | OK |
| FR-011 (off-spine: no stage advance, no approval) | T008, T018 | OK |
| FR-012 (five wiring points, count +1) | T012, T013, T014, T015, T016 | OK |
| FR-013 (clean corpus means zero findings) | T011, T017 (whole-corpus check) | OK |
| FR-014 (unreadable file fails loud, never silent skip) | T005 (implementation only) | GAP |
| FR-015 (field is human-authored; rule never infers/chooses) | T004, T011 | OK |
| FR-016 (no C086/retail_store_sales/pharmacy specifics) | T004, T005, T019 | OK |
| FR-017 (ASCII/UTF-8-no-BOM, short paths) | T004, T005, T012, T013, T020 | OK |
| FR-018 (A10-only trigger decided; widen-beyond-A10 OPEN) | T011 (decided half), T021 (OPEN half preserved) | OK (decided half); intentionally unimplemented (OPEN half) |
| SC-001 (clean corpus, zero findings) | T017 | OK |
| SC-002 (missing then ERROR then clears on semi/non) | T006 | OK |
| SC-003 (fully on A10 gives ERROR) | T006 | OK |
| SC-004 (out-of-vocab ERROR distinguishable from missing) | T009 | OK |
| SC-005 (rule-id set + manifest count agree) | T014, T015 | OK |
| SC-006 (no score/confidence; no execution; stdlib-only import) | T018 | OK |
| SC-007 (zero domain-specific tokens in generic artifacts) | T019 | OK |

#### Finding F1 (Medium) -- FR-014 has an implementation task but no dedicated test task

Severity: Medium (coverage gap, not a design defect).

plan.md's Testing section and Project Structure block both explicitly list
"unreadable-file-fail-loud" as one of the fixture cases tests/unit/test_snapshot_time_additivity.py
must cover. data-model.md's decision table frames every row, including row 1 (file unreadable), as
"independently testable per the spec's Acceptance Scenarios / Edge Cases / Independent Tests."

However, tasks.md's two test tasks do not cover row 1:
- T006 (US1 tests) covers decision-table rows 5/6/7/8 only.
- T009 (US2 tests) covers rows 2/3/4/9 only.
- No task exercises row 1 (file unreadable, fail-loud ERROR) with an actual fixture (e.g., an
  unreadable/undecodable file, or a mocked OSError/UnicodeDecodeError/yaml.YAMLError).

The FR/SC coverage trace at the bottom of tasks.md itself records "FR-014 | T005" -- implementation
only, no test task cited -- which is consistent with this gap being real rather than a citation
oversight. Every other FR that has a MUST enforcement behavior has at least one test task in its
trace; FR-014 is the only MUST-behavior requirement in the table above with implementation-only
coverage.

Recommendation (informational -- this stage is read-only and does not edit tasks.md): add one
fixture case to T006 or T009 (or a new sub-case) asserting that a tracked-but-unreadable contract
path produces the row-1 fail-loud ERROR with the exact message class named in the decision table,
mirroring AL1's own precedent test if one exists.

---

### 2. Success-Criteria Testability

All seven success criteria are phrased as objectively checkable pass/fail conditions (a specific
fixture leading to a specific count of ERROR findings, or a boolean property of the module/
artifacts). None relies on a subjective judgment, an estimate, or a numeric threshold.

| SC | Testable as stated? | Note |
|---|---|---|
| SC-001 | Yes | Deterministic: run retail check on the real committed corpus; count HR5 findings equals 0. Independently confirmed during this analysis: mappings/*/metrics/*.yaml currently has zero A10 hits (5 files total: AvgTransactionValue, DiscountedTransactionRate, TotalQuantity, TotalSales, TransactionCount), so this baseline is genuine, not assumed. |
| SC-002 | Yes | Fixture-based; exact-count assertion (exactly one ERROR, then zero). |
| SC-003 | Yes | Fixture-based; exact-count assertion. |
| SC-004 | Yes | Requires the two message strings be textually distinguishable -- testable by string inequality, not by exact wording (the spec does not lock exact message text, which is appropriate -- it locks distinguishability, an implementation-phase freedom correctly left open). |
| SC-005 | Yes | len(EXPECTED_RULE_IDS) equals manifest count is a mechanical equality already exercised by the existing test_rules_wiring.py pattern. |
| SC-006 | Partially mechanical / partially inspection-based | "no numeric score in any finding" and "no execution" are verified by code inspection (T018), not purely by an automated assertion in this build (no test grep-asserts the absence of a Severity.WARNING or a network import). This is consistent with how AD1/AL1 were verified per research.md, so it is not a new weakness introduced by this feature, but it is worth naming: SC-006's "verifiable by inspecting outputs" phrasing is honest about being inspection-based rather than fully automated. |
| SC-007 | Yes | A grep-based zero-hits check (T019) is fully mechanical and reproducible. |

No success criterion contains an unresolvable ambiguity, a numeric health/confidence figure, or a
non-reproducible judgment.

---

### 3. Terminology Consistency

Checked the following terms for consistent usage across all six artifacts:

- time_additivity -- used identically (name, casing, position "alongside grain and readiness") in
  spec.md, plan.md, tasks.md, research.md, data-model.md, and quickstart.md. No drift.
- HR5 -- consistently the reserved rule id across all artifacts; consistently described as
  ERROR-only, off-spine, never-resolves. No artifact assigns it a different id or a WARNING
  severity.
- A10 -- consistently "Inventory snapshot date," consistently cited from
  skills/retail-kpi-knowledge/knowledge/kpi-ambiguities.md. Independently confirmed: the file's
  lines 65-70 read "A10 -- Inventory snapshot date... Must never be summed across dates," matching
  every paraphrase in spec.md, research.md, and data-model.md. No artifact restates or redefines
  this text; all cite it, per FR-003/FR-015's own requirement.
- AD1 vs. HR5 boundary language -- spec.md's "Boundary against neighbouring shipped work," plan.md's
  Constitution Check (Principle V paragraph), and research.md's Section 1.2 all describe the same
  distinction (composition-legality vs. date-axis additivity) using consistent framing. No
  contradiction.
- "Five wiring points" -- see Finding F2 below; the enumeration differs in composition (not in
  outcome) between research.md and FR-012/tasks.md.
- Decision-table row numbering -- data-model.md's 9-row table is referenced by exact row number in
  tasks.md (T006 cites "rows 5/6/7/8," T009 cites "rows 2/3/4/9"). Cross-checked: rows 5-8 are the
  four A10-true outcomes (ABSENT/FULLY/SEMI/NON) and rows 2/3/4/9 are the remaining A10-false and
  out-of-vocab-with-A10 cases -- the citations match the table's actual content. No drift.
- "OPTIONAL" vs. "REQUIRED-in-effect" -- data-model.md's own phrase ("becomes REQUIRED-in-effect
  only on a contract that also carries an A10 entry") is used nowhere else verbatim, but the
  underlying behavior (optional globally, HR5-enforced conditionally) is stated consistently in
  spec.md FR-007 and quickstart.md Section 1. Not a contradiction -- a locally-scoped clarifying
  phrase, not a competing definition.

No terminology contradiction found.

---

### 4. Constitution Alignment

Re-derived independently against .specify/memory/constitution.md's named principles (not merely
transcribing plan.md's own Constitution Check table):

- Principle I (Agent-First, Gate-Enforced) -- PASS. HR5 fails CLOSED as a categorical ERROR via
  retail check's exit code (FR-004/FR-005/FR-006, SC-002/SC-003/SC-004). No artifact frames a
  finding as advisory-only.
- Principle III (Medallion, Gold-Only) -- PASS by non-engagement. HR5 reads only
  mappings/*/metrics/*.yaml text; it opens no database connection and does not touch
  binds_to.gold_table semantics. Confirmed no artifact adds a bronze/silver read path.
- Principle IV (Source-Mapping-Before-Silver) -- PASS by non-engagement. No artifact writes or
  reorders silver.* SQL or the source-mapping gate artifacts. Correctly out of this feature's layer
  (metric-contract, downstream of mapping).
- Principle V (Agent-Stops-at-Judgment) -- PASS, and the feature's central discipline. HR5 never
  supplies, infers, or defaults a time_additivity value (FR-002a, FR-004a, FR-006, FR-015); it only
  checks that a human-authored A10 flag is accompanied by a human-authored declaration.
  FR-018/Clarifications Q4 (whether the A10-only trigger should ever widen to other
  semi-additive-over-time shapes) is correctly left "NEEDS CLARIFICATION -- OPEN owner ruling"
  rather than answered by the agent -- this is compliance with Principle V, not a violation of it.
  See Section 8 (open_principle_v) below for why this stays open rather than blocking.
- Principle VI (Defaults-Then-Deviations) -- PASS. Three mechanical parsing forks (Q1 exact-id
  match, Q2 exact-vocabulary match, Q3/Q3b null/empty/non-scalar collapse) each record an adopted
  DEFAULT with a stated rationale in spec.md's Clarifications section, consistent with plan.md's
  restatement. The one non-mechanical fork (Q4) was correctly NOT defaulted.
- Principle VII (C086-is-an-example) -- PASS. Independently grepped: no artifact under this
  feature's own spec tree contains a retail_store_sales/C086/pharmacy-specific column, table, or
  metric name in a normative (non-citation) position. The template comment (FR-001) is required to
  cite the knowledge doc generically, and the plan/tasks/data-model all repeat this constraint
  (FR-016, SC-007, T019).
- Principle VIII (Static-First, Live-Deferred) -- PASS. research.md Section 3 and quickstart.md
  Section 5 both explicitly enumerate what is NOT assumed to exist (F016, live DB, DAX-gen
  extension) rather than silently omitting the topic. See Section 5 below for the full leakage scan.
- Principle IX (Secrets/Reproducibility) -- PASS. No credential, host, or DSN appears in any
  artifact. FR-017/T020 require ASCII/UTF-8-no-BOM and short repo-relative paths; spot-checked, the
  six artifacts read as ASCII with double-hyphen/arrow substitutions, no smart quotes or arrows.
- Hard rule #9 (No Fabricated Confidence) -- PASS. FR-009/SC-006 restrict HR5 to categorical
  ERROR-only findings; data-model.md's Finding shape carries no numeric field. No artifact
  introduces a score, health value, or completeness count anywhere in this feature's scope.

---

### 5. Deferred-Capability Leakage Scan

Checked every artifact for an assumption that F016 (Power BI execution adapter) or a live DB
connection already exists or is reachable by this feature's design.

- research.md Section 3 explicitly lists, as NOT assumed: F016, live database connection, a
  time_additivity-aware DAX generator/F-DAXGEN extension, a new readiness stage, and a widened
  detection trigger. Each bullet states the concrete non-action (e.g., "HR5 never opens a PBIP
  file, never calls the official Power BI MCP/connection, and never calls pbi-cli").
- quickstart.md Section 5 ("What this quickstart deliberately does NOT do") independently restates
  the same three non-assumptions in end-user-facing language (no Power BI Desktop, no DB connection,
  no deciding a real metric's value).
- plan.md Constraints and Technical Context state Storage: None, Target Platform: CI static check
  only, and the Constitution Check's Principle VIII paragraph states "No live surface is introduced,
  so none needs a PENDING marker" -- correctly distinguishing this feature's zero-live-surface case
  from a feature that would need a PENDING marker.
- data-model.md's optional definition block reference (inherited from the template, not authored
  by this feature) is explicitly called out as "unrelated to this feature and is not read, written,
  or extended" (research.md Section 1.3, echoed in Section 3's DAX-generator bullet) -- this is the
  one place a live-adjacent capability (retail generate, F-DAXGEN) is even mentioned, and it is
  mentioned only to disclaim engagement, not to assume it.
- tasks.md T017 exercises retail check (the existing static gate binary), not any live-DB or
  execution-adapter command. No task invokes retail validate (the live-check skill) or any Power BI
  connection tooling.

Result: clean. No artifact in this feature's tree assumes F016 or a live DB surface exists. This is
a genuine pass, not an absence of a check.

---

### 6. Contradiction / Duplication / Ambiguity Scan

- No direct contradiction found between spec.md, plan.md, tasks.md, research.md, data-model.md, or
  quickstart.md on any requirement's substance (vocabulary, trigger, message classes, wiring points,
  scope boundary vs. AD1/092/103).
- Finding F1 (Medium, coverage gap) -- see Section 1: FR-014 has an implementation task (T005) but
  no dedicated fixture-test task; plan.md and data-model.md both frame the unreadable-file case as
  one of the testable rows/cases, but tasks.md's two test tasks (T006, T009) do not cite row 1.
- Finding F2 (Low, terminology drift, non-blocking) -- research.md Section 1.5 enumerates the "five
  wiring points" as: (1) __init__.py import tuple, (2) test_rules_wiring.py EXPECTED_RULE_IDS, (3)
  rules-manifest.json, (4) severity-posture.json, (5) "the new rule module itself plus its
  behavior-test file." FR-012 and tasks.md T012-T016 instead count: (1) __init__.py import block,
  (2) __init__.py __all__ list, (3) EXPECTED_RULE_IDS, (4) manifest, (5) severity-posture --
  splitting the import-tuple/__all__ edit (research.md's single item 1) into two FR-012 points, and
  dropping "module + test file" as a distinct fifth point (folded elsewhere). Both arrive at "five,"
  but membership differs. This does not change what gets built (T012-T016 correctly implement
  FR-012's version) -- it is a documentation-only inconsistency between research.md's summary and
  the spec's own count. Non-blocking.
- Finding F3 (Low, informational, same-artifact miscount) -- data-model.md's decision table
  (Section "The decision table") lists 9 rows and states "Three distinct ERROR message classes
  exist (row 1 unreadable; rows 5 missing; row 6 illegal-fully; rows 4/9 unrecognized)" -- this
  sentence names four row-groups (1; 5; 6; 4/9) while asserting "three" message classes. The actual
  count of message classes (unreadable / missing / illegal-fully / unrecognized) is four, not
  three -- the lead-in word "Three" appears to be a stale edit (an earlier version likely had only
  unreadable/missing/unrecognized before FR-005's "illegal fully" distinct-message requirement was
  added). This is a same-artifact internal inconsistency (a miscount in a summary sentence), not a
  cross-artifact contradiction, but is reported because it could mislead an implementer into
  collapsing two message classes. Recommend correcting "Three" to "Four" in data-model.md in a
  future editing pass (not performed by this read-only stage).

No duplication of requirements was found (each FR/SC states a distinct, non-overlapping rule; the
overlap that exists -- FR-004 vs. FR-004a/FR-004b, FR-006 vs. FR-006a -- is intentional
base-rule-plus-edge-case structuring, not duplication).

No unresolved ambiguity was found beyond the one the spec itself correctly flags as OPEN (FR-018 /
Q4) -- see Section 8.

---

### 7. Findings Summary

| ID | Severity | Summary |
|---|---|---|
| F1 | Medium | FR-014 (unreadable-file fail-loud) has an implementation task (T005) but no dedicated fixture-test task in T006/T009; tasks.md's own FR/SC trace confirms FR-014 maps only to T005, the sole MUST-behavior requirement in the table with implementation-only coverage. |
| F2 | Low | research.md Section 1.5's "five wiring points" enumeration and FR-012/tasks.md's five wiring tasks (T012-T016) both total five but differ in what they count as each point (documentation-only drift; build output unaffected). |
| F3 | Low | data-model.md's decision-table summary sentence says "Three distinct ERROR message classes exist" while its own parenthetical lists four (unreadable / missing / illegal-fully / unrecognized) -- an internal miscount in a summary sentence, not a cross-artifact contradiction. |

No CRITICAL or HIGH severity findings. No constitution violation was found (see Section 8).

---

### 8. Result

- scope_ok: true. No artifact redefines a KPI's business meaning (the field and rule cite, never
  restate, the A10/semi-additive definition owned by skills/retail-kpi-knowledge/); the
  templates/metric-contract.yaml change is confined to the single reserved key time_additivity,
  with independently confirmed zero collision against 092 (separate file, confirmed in
  specs/092-rls-access-readiness/spec.md) and 103 (its own unit key, confirmed in
  specs/103-currency-unit-contract/spec.md); the reserved rule id HR5 is used consistently and is
  not yet present in EXPECTED_RULE_IDS (correct for a pre-implementation ANALYZE stage); no
  fabricated confidence/health/completeness score appears anywhere; and Principle V is honored by
  stopping at, not resolving, the one genuine judgment call (FR-018/Q4).
- open_principle_v (informational -- surfaced per Principle V, not a violation):
  - FR-018 / Clarifications Q4: whether HR5's snapshot-grain detection trigger should ever extend
    beyond the existing A10 ambiguities-ledger id to a non-inventory semi-additive-over-time shape
    (e.g., a cumulative/YTD balance) is explicitly left "NEEDS CLARIFICATION -- OPEN owner ruling".
    This is correctly a retail-kpi-knowledge ledger-scope business decision, not something this
    build or this analysis stage may resolve; it remains open for a named retail-kpi-knowledge
    owner at a future date.
