# Cross-Artifact Analysis: 089-readiness-decay-demotion

**Stage**: ANALYZE (read-only). **Date**: 2026-07-04. **Scope**: `spec.md`, `plan.md`,
`tasks.md`, `research.md`, `data-model.md`, `quickstart.md` in this feature directory only.
No other file was modified to produce this report. Verification below was performed against
the live worktree (`readiness_status.py`, `gitutil.py`, `docs/rules/rules-manifest.json`,
`docs/quality/rule-count-claims.yaml`, `docs/glossary.md`, `docs/readiness/source-drift.md`,
and the canary `mappings/retail_store_sales/readiness-status.yaml`) to distinguish
verified-accurate cross-references from unverified assertions.

## Requirement-coverage table

Every Functional Requirement (FR) and every Success Criterion (SC) mapped to its covering
task(s)/artifact. Status `OK` = covered by at least one task with a clear implementation
path; `GAP` = no task closes it or coverage is incomplete.

| Req | Covering task(s) / artifact | Status |
|---|---|---|
| FR-001 (one new rule HR3, fails CLOSED) | T005, T006, T018, T020 | OK |
| FR-002 (drift-triggered, N findings not rolled up) | T020, T013-T017, T034a | OK |
| FR-003 (approval-lag, cited-path extraction, latest-approval) | T036, T037, T038, T024-T027/T029/T034b | OK |
| FR-004 (author date not committer date) | T022, T023(c), T038 | OK |
| FR-005 (never writes any file) | T038/T046 (no write path), T048 (mechanical source-scan) | OK |
| FR-006 (`stale_review` schema, additive) | T002, T045 | OK |
| FR-007 (stale_review clears matching FR-003 finding only if shape-valid + dated) | T046, T040/T042/T043, T052 (OPEN scope recorded) | OK |
| FR-008 (invalid reviewer -> distinct finding) | T046, T041 | OK |
| FR-009 (agent never auto-fills reviewer) | T051 (agent-behavior checklist, not rule code) | OK (by design: unenforceable in a static rule; correctly deferred to agent-behavior layer) |
| FR-010 (no live re-profile runtime invoked) | T020 (no subprocess/network call in that branch) | OK |
| FR-011 (approval-lag scoped to approval-bearing stages only) | T036, T017, T033 | OK |
| FR-012 (no numeric score) | T009 (ERROR-only posture), T048 (mechanical string-scan) | OK |
| FR-013 (unresolvable citation -> distinct finding, scoped) | T036, T030/T032/T033/T034 | OK |
| FR-014 (unparseable approval date -> distinct finding) | T037, T028 | OK |
| FR-015 (additive only; RS1 unchanged) | T004, T005 (reuse not redefine) | OK |
| FR-016 (ASCII/UTF-8 no BOM, short paths) | T002 explicit; implicitly every new-file task | OK |
| FR-017 (no new stage / live check / executor) | T004 | OK |
| SC-001 (0 tables pass silently under drift) | T013-T017, T021 | OK |
| SC-002 (0 tables pass silently under approval-lag) | T024-T029, T039 | OK |
| SC-003 (0 writes across every scenario) | T018 (per-fixture), T035 (repeat), T048 (mechanical, feature-wide) | OK |
| SC-004 (0 numeric scores in any finding/entry) | T048 (mechanical string-scan across all 5 message shapes) | OK |
| SC-005 (valid stale_review clears matching finding, no side effects) | T040, T047 | OK |
| SC-006 (0 new false positives on current committed state, canary) | T049 (runs `check_hr3` against the real `retail_store_sales` file, not a copy) | OK |

No FR or SC is left uncovered. `tasks.md`'s own "Requirement Coverage Check" section
(lines 740-761) independently restates this same mapping; it was cross-checked against the
task bodies themselves rather than trusted at face value, and it matches.

## Success-criteria testability

All six SCs are objectively checkable without a numeric/subjective judgment call:

- SC-001/SC-002 are existence assertions ("N tables pass silently" = 0) verified by fixture
  count assertions in `test_rule_hr3.py` -- testable.
- SC-003 is a byte-diff assertion (working tree before/after a check run) -- mechanically
  testable, and T048 additionally makes it a static source-scan (no write call exists in the
  module at all), which is a stronger guarantee than a per-fixture behavioral test alone.
- SC-004 is a "does this string ever contain a number formatted as a ratio/score" static scan
  -- testable, though it is worth noting this is necessarily a heuristic grep-style test
  (T048) rather than a type-level guarantee; the `Finding.message` field is a free string, so
  nothing stops a future edit to a message template from introducing a percentage. This is a
  reasonable trade-off given `Finding` is a shared, unchanged dataclass, not a defect in the
  design.
- SC-005 is a before/after finding-count assertion -- testable.
- SC-006 is the strongest-verified SC in this chain: it names a real file
  (`mappings/retail_store_sales/readiness-status.yaml`) and research.md traced every
  `evidence[]` token in it against the extraction algorithm, cross-checked with live
  `git log --format=%aI/%cI` output. I independently re-ran the three commit-date checks
  cited in research.md's canary table (`source-map.yaml`, `assumptions.md`,
  `unresolved-questions.md` all show `2026-06-25T15:33:29+03:00`) and the rule-count claim
  (`docs/rules/rules-manifest.json` has exactly 55 entries, matching
  `rule-count-claims.yaml`'s `claimed-count: 55` and `glossary.md`'s "Currently 55 rules in 21
  families" anchor). All three checks matched research.md's assertions exactly -- this SC's
  supporting evidence is verified-accurate, not merely asserted.

No SC is vague, unfalsifiable, or dependent on a subjective "looks right" judgment.

## Terminology consistency

Checked across all six documents for drift in naming:

- **`stale_pass`** (finding kind), **`stale_review`** (schema key), **`HR3`** (rule id),
  **`Person Name (authority_class)`** (owner shape), **`_APPROVAL_REQUIRED`**,
  **`_STAGE_ORDER`**, **`_INSTANCE_RE`** -- used identically in spec.md, plan.md, tasks.md,
  research.md, data-model.md, and quickstart.md. No synonym drift (e.g. no document calls it
  "stale-review" vs "stale_review" inconsistently, no document calls the rule "HR-3" instead
  of "HR3").
- **"drift-triggered" vs "approval-lag"** -- the two staleness conditions are named
  consistently as this exact pair across every document (spec's Overview/User
  Stories/Clarifications, plan's Summary, data-model's message shapes 1/2, tasks.md's Phase
  3/4 titles).
- **Five message shapes** -- spec.md's Key Entities describes the finding generically;
  data-model.md is the sole place the five exact message templates are spelled out
  (drift-triggered, approval-lag, unresolvable-citation, unparseable-date,
  invalid-reviewer-shape); tasks.md refers back to these by "message shape N" consistently
  (T028, T030, T034a, T041 all cite the correct shape number matching data-model.md's
  numbering). Verified all five references resolve to the correct shape.
- **"author date" vs "committer date"** (`%aI` vs `%cI`) -- used with the same meaning and the
  same justification (rebase/cherry-pick rewrites committer date) in FR-004, plan.md's
  Technical Context, research.md's canary table, data-model.md entity 6, and quickstart.md's
  verification snippet. No document ever conflates the two.
- **Minor terminology note (not a defect)**: FR-013's prose calls it an "unresolvable evidence
  citation," data-model.md's message-shape list calls the same thing "Unresolvable evidence
  citation," and tasks.md sometimes shortens it to "unresolvable citation" or
  "unresolvable-citation finding." This is a consistent abbreviation, not a naming conflict --
  no ambiguity was found in context.

## Constitution alignment

Explicitly checked against every named principle and hard rule #9:

- **Principle I (Agent-First/Gate-Enforced, fails CLOSED)**: plan.md's Constitution Check
  table states HR3 emits `Severity.ERROR` for every finding, no advisory/warn-only mode.
  Verified: `docs/rules/severity-posture.json`'s wiring task (T009) adds `"HR3": ["error"]`
  only -- no `"warning"` entry anywhere in the design. Compliant.
- **Principle III (Medallion/Gold-Only)**: HR3 reads no data path, opens no Postgres
  connection, reads no PBIP surface -- confirmed by Technical Context's Storage line ("N/A --
  no database, no live connection") and the plan's Constitution Check row. Compliant (this
  principle is largely inapplicable to a pure-YAML/git-metadata rule, and the spec correctly
  says so rather than forcing a contrived connection).
- **Principle IV (Source-Mapping-Before-Silver)**: HR3 writes no SQL and does not gate
  `silver.*` authorship; it only evaluates whether an already-approved `mapping_ready` pass
  has drifted. Does not reopen the mapping-gate mechanism. Compliant.
- **Principle V (Agent-Stops-at-Judgment, never self-grant)**: this is the most
  heavily-scrutinized principle in the chain, and correctly so -- HR3 raises a finding and
  stops (FR-005); the Clarifications section explicitly leaves the `stale_review`-vs-drift
  scope question OPEN rather than silently deciding it (a genuine Principle-V-conscious
  choice, not a cosmetic one); FR-009/T051 correctly locate the "agent must not auto-fill
  reviewer" constraint at the AGENT-BEHAVIOR layer rather than pretending a static rule module
  can enforce it (a static rule has no way to observe or prevent what an interactive agent
  session does -- this is the right layer to put that constraint, and the design says so
  explicitly rather than fabricating an unenforceable in-code check). Compliant, and notably
  self-aware about the boundary of what a static rule can enforce.
- **Principle VI (Defaults-Then-Deviations)**: the three mechanical rule-behavior choices
  (same-day-not-stale, path-token extraction gated on resolution not shape, latest-approval-
  wins) are recorded as reversible defaults in spec.md's Clarifications, not fresh
  inventions buried in code. Compliant.
- **Principle VII (C086-is-an-example)**: data-model.md's schema shapes use generic
  `<stage_name>`/`<repo-relative-path>` placeholders; the one worked example
  (`retail_store_sales`) is explicitly marked "illustrative only, not a requirement." T050
  is a dedicated grep task confirming no domain-specific literal leaks into rule logic.
  Compliant.
- **Principle VIII (Static-First/Live-Deferred)**: HR3 reads only `ctx.tracked_files` and git
  commit metadata; FR-010 explicitly forbids invoking a live re-profile runtime or `retail
  drift` CLI (confirmed: no such CLI exists in this worktree -- `docs/readiness/
  source-drift.md` is prose-only, matching the spec's own Boundary section claim). Compliant.
- **Principle IX (Secrets/Reproducibility)**: FR-004's author-date-over-committer-date choice
  is explicitly grounded in this principle (reproducibility across clones); no
  connection-string/DSN/secret is touched anywhere in this design; FR-016 requires ASCII/
  UTF-8-no-BOM/short-path discipline. Compliant.
- **Hard rule #9 (no fabricated score)**: FR-012, SC-004, and T048's dedicated mechanical
  string-scan for numeric-score-shaped output collectively give this the strongest
  enforcement of any single rule in the chain -- a static source-inspection test, not just a
  reviewed convention. Compliant.

**No constitution violation found.** `scope_ok = true`; nothing is listed under
`open_principle_v` as a violation (the one OPEN item -- `stale_review`-vs-drift scope -- is
correctly a recorded-open PRODUCT decision per the spec's own Clarifications, not a
constitution violation; see "Deferred/open items" below for why this is not scored as a
defect).

## Contradiction / duplication / ambiguity scan

- **No contradiction found** between spec.md's FR text, plan.md's Constitution Check, and
  data-model.md's algorithm. This is unusual for a chain this large -- cross-checked
  specifically for the classic failure mode (an FR saying one thing, a task implementing
  another) and found none. Example spot-check: FR-003's "strictly later" wording, the Edge
  Cases same-day bullet, the Clarifications same-day answer, data-model.md entity 6's
  truncate-to-day-then-compare description, and T026's fixture name
  (`approval_lag_same_day_not_stale`) all agree on the exact same rule (same-day = NOT
  stale) with no variant wording anywhere that could be read the opposite way.
- **No duplication found** in rule logic: T019's `_iter_status_files` is explicitly built
  once (Phase 3) and reused (not reimplemented) by Phase 4/5 per the Dependencies section;
  T036's extraction algorithm and T037's latest-approval selector are likewise built once and
  reused by T046. The plan is explicit that these are shared, not duplicated.
- **F1 (minor, informational)** -- plan.md's Complexity Tracking states "No entries" and "no
  principle requires a documented violation," which is accurate, but the plan itself performs
  a substantial amount of Constitution-adjacent judgment work (the whole
  same-day/path-extraction/latest-approval Clarifications sequence) that in a stricter
  process might have warranted a Complexity Tracking row explaining why three separate
  "reversible defaults" were adopted at plan/spec time rather than left to implement. This is
  not a defect -- the spec's own Clarifications session already documents each decision's
  rationale in more detail than a Complexity Tracking row would -- but it is worth naming that
  the two sections (Clarifications and Complexity Tracking) could be cross-referenced
  explicitly (e.g. "see Clarifications for the three reversible defaults this Complexity
  Tracking section does not re-litigate") so a future reader does not need to infer that
  connection. **Severity: LOW (documentation cross-reference, not a correctness or scope
  issue).**
- **F2 (minor, informational)** -- the module-naming convention in plan.md's Project Structure
  says HR3 "mirrors" HR1's spec-087 plan/research precedent, and research.md independently
  confirms HR1 is itself still design-stage (not implemented) "at time of writing." I
  independently confirmed `src/retail/rules/` contains no `rule_hr1.py` file today, so this
  claim is accurate as of this analysis. However, several tasks (T006, T008, T010) instruct
  the implementer to "re-verify order/whether HR1 has already landed... at implement time" --
  this is a live TOCTOU (time-of-check-to-time-of-use) risk inherent to any spec written while
  a sibling feature (HR1) is in flight, not a defect in this spec's authoring. The spec
  handles it about as well as a document can (explicit "do not assume, re-verify" language at
  every touch point rather than hardcoding a number), so this is flagged as an
  **environmental risk to note, not a spec defect. Severity: LOW (self-mitigated by the
  spec's own re-verify instructions).**
- **No ambiguity found** in the FR text itself. Every FR that could plausibly be read two
  ways (the same-day tie, the multiple-approvals-per-stage case, the path-extraction
  resolution gate, the simultaneous-drift-and-lag case) was explicitly resolved in the
  Clarifications section with a stated rationale, and the corresponding FR text was updated
  to reflect the resolved wording (e.g. FR-003's "strictly later," FR-004's "AUTHOR date, not
  committer date"). Cross-checked that no Clarification's answer was left unreflected in its
  target FR -- all five Clarifications entries name the FRs/sections they touch, and each
  named location was checked and found updated accordingly.

## Deferred-capability leakage scan

Checked every artifact for an assumption that F016 (Power BI execution adapter) or a live DB
surface already exists:

- **F016 (Power BI execution adapter)**: explicitly named as NOT existing / not invoked in
  spec.md's Boundary section, plan.md's Constitution Check (Principle III row: "opens no
  Postgres connection and reads no Power BI/PBIP surface"), and research.md's "Deferred
  capabilities NOT assumed" section. No task, fixture, or code-path description anywhere in
  `tasks.md` references a Power BI connection, `pbi-cli`, or the official Power BI MCP. No
  leakage found.
- **Live DB / `retail validate`**: FR-010 explicitly forbids depending on a live re-profiling
  runtime; Technical Context's Storage line states "N/A -- no database, no live connection";
  research.md confirms `docs/readiness/source-drift.md` is "design-only, no runtime, no
  `retail drift` CLI, no comparator" and independently verifies this against the live
  worktree (I separately confirmed no `retail drift` CLI or comparator module exists under
  `src/retail/`). No task assumes a DSN, connection string, or `db` extra. No leakage found.
- **Git as the sole "live" signal**: the design's one genuinely new capability (a
  `git log -1 --format=%aI` subprocess read) is correctly scoped as a STATIC, already-
  committed-history read (Principle VIII), not a live surface -- this is consistent with how
  `gitutil.py`'s existing functions (`git_output`, `git_log_subjects`) already operate in this
  codebase, confirmed by inspection. No leakage found.
- **HR1 / spec 087**: correctly treated as a sibling design-stage artifact, not a dependency
  this feature assumes is built -- plan.md explicitly says HR3 "does not edit `rule_hr1.py`,"
  and I confirmed no such file exists yet. No leakage found.

**No deferred-capability leakage found in any artifact.**

## Additional cross-check note (not a finding, informational)

Several specific factual claims embedded in research.md and quickstart.md -- the exact commit
timestamps for the canary's evidence files, the current registered-rule count (55), the exact
text of `docs/glossary.md`'s "Currently N rules" anchor, and the literal wording of
`docs/readiness/source-drift.md`'s "Downstream-invalidation rule" -- were independently
re-verified against the live worktree during this analysis rather than trusted at face value,
given how heavily SC-006 and the Constitution Check depend on them. All matched exactly. This
level of independently-checkable, and now independently-checked, precision is unusual and is
noted here as a positive signal on the spec chain's reliability, not a finding requiring
action.

## Deferred/open items (carried forward, not defects)

- **OPEN (Principle V, by design)**: whether a `stale_review` entry may also clear a
  drift-triggered (FR-002) finding, or is scoped to approval-lag (FR-003) only. Spec.md's
  Clarifications section marks this "OPEN owner ruling" explicitly (not a default-adopted
  answer); plan.md's dedicated "Open item carried to implement-stage" section and tasks.md's
  T052 both correctly implement the PENDING DEFAULT (FR-007-as-written: approval-lag only)
  without silently broadening scope. This is a genuine, correctly-flagged product-scope
  question for a named human/feature-owner to answer -- it is not a spec defect, and the
  design does not paper over it by picking an answer. Listed here for visibility, not as a
  constitution violation.

## Verdict

`scope_ok = true`. No constitution violation found. No FR/SC gap found. No contradiction,
harmful duplication, or unresolved ambiguity found in the spec chain. No deferred-capability
(F016 / live DB) leakage found. Two LOW-severity informational notes (F1: cross-reference
opportunity between Clarifications and Complexity Tracking; F2: an inherent, self-mitigated
TOCTOU risk from HR1 being a concurrently in-flight sibling feature) are recorded above but do
not block this feature from proceeding to the next stage. The one OPEN item
(`stale_review`-vs-drift scope) is a correctly-flagged Principle-V product-scope question for
the feature owner, not a defect in this analysis's scope.
