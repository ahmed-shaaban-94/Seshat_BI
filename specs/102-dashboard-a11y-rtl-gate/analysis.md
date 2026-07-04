# Cross-Artifact Analysis: Dashboard Accessibility + RTL/Arabic Readiness Checklist

**Feature**: `102-dashboard-a11y-rtl-gate` | **Date**: 2026-07-04 | **Stage**: ANALYZE (read-only)

**Scope**: `spec.md`, `plan.md`, `tasks.md`, `research.md`, `data-model.md`, `quickstart.md`
in this feature directory. No other file was edited to produce this report.

---

## 1. Requirement coverage table

| Req | Covering task(s) / artifact | Status |
|-----|------------------------------|--------|
| FR-001 (generic template, 3 dimensions) | T003, T007 | OK |
| FR-002 (static; no render/open/publish/connect) | T007, T008 | OK |
| FR-003 (contrast cites CT1, never re-derives) | T012, T013, T014, T020 | GAP -- see F1 |
| FR-004 (open CT1 error/parse-failure -> blocked) | T012, T020 | OK |
| FR-005 (colorblind-safe fixed generic criteria) | T015, T017, T021 | OK |
| FR-006 (RTL/Arabic fixed generic criteria) | T016, T018, T021 | OK |
| FR-007 (checklist required in evidence[]; absent/unfilled = blocker) | T007, T010 | OK |
| FR-008 (no new status/stage/rule id; additive only) | T010, T011, T026 | OK |
| FR-009 (generic; no C086 specifics; per-page path) | T005, T015, T016, T023 | OK |
| FR-010 (staleness = review-discipline, not mechanical) | T019 | OK |
| FR-011 (defect -> warning/blocked + proposed alternative) | T011, T017, T018 | OK |
| FR-012 (no numeric score/confidence/health/completeness) | T007, T022, T025 | OK |
| FR-013 (ASCII/UTF-8-no-BOM; no literal Arabic; short paths) | T016, T024, T028 | OK |
| FR-014 (two OPEN Principle-V questions carried forward) | T009, T011, T018, T029 | OK |
| FR-015 (token-file resolution via existing co-location convention) | T013, T020 | GAP -- see F1 |

13 of 15 FRs are cleanly covered by their mapped tasks with no contradiction found on
independent verification. FR-003 and FR-015 are marked GAP because the resolution
mechanic both requirements depend on (verified below, F1) does not match the actual
repo layout or the cited precedent file, which means T013/T020 as currently specified
will produce a worked instance that cannot execute the fill procedure exactly as written.

---

## 2. Success-criteria testability

| SC | Testable as stated? | Notes |
|----|----------------------|-------|
| SC-001 | Yes | Requires a future-state audit across all pages recording `dashboard_ready: pass`; not verifiable from this feature's four artifacts alone, but the *mechanism* (FR-007's blocker) is checkable now. |
| SC-002 | Yes | Directly checkable: grep filled checklists' `disposition: reviewed-clean` co-occurring with `ct1_result` != `clean`. Deterministic. |
| SC-003 | Yes | Deterministic grep (T025), already specified with the exact field names to search. |
| SC-004 | Yes | Deterministic grep (T023), exact target files named. |
| SC-005 | Yes | Deterministic diff of `retail check` rule-id set before/after (T002, T026). Precisely falsifiable. |
| SC-006 | Yes | Requires manual trace of each citation to a real path (T027); the paths named in plan.md/data-model.md are independently confirmed to exist on disk (Section 5 below) with one exception (the token-file co-location path, F1). |

All six success criteria are measurable/testable as written. None is vague or relies on
a subjective judgment beyond the documented dimension criteria. No fabricated
score/percentage appears in any SC (consistent with hard rule #9).

---

## 3. Terminology consistency

- **"disposition" vs "status"**: data-model.md consistently uses `disposition` for the
  per-dimension field and `overall_status` for the roll-up field; spec.md, plan.md,
  tasks.md, and quickstart.md all use the same two terms consistently. No drift found.
- **"reviewed-clean" / "not-applicable-with-reason" / "blocked"**: identical three-value
  enum used verbatim across spec.md (Key Entities, FR-005/006/007), data-model.md, and
  tasks.md (T007, T017, T018). Consistent.
- **"CT1"**: spec.md, plan.md, research.md, data-model.md, quickstart.md, and tasks.md
  all refer to the same rule id and the same file (`src/retail/rules/design_contrast.py`).
  Consistent, and independently confirmed to be the correct RULE_ID in the source file.
- **`ct1_result` vocabulary**: data-model.md defines the enum as `clean | open-error: <text>
  | parse-failure: <text> | file-not-found`. Quickstart step 2 and tasks T012/T020 reuse
  this vocabulary consistently across artifacts -- but the vocabulary itself does not
  match CT1's actual output surface (see F2 below). This is an internal-consistency
  pass (the artifacts agree with each other); it is not a consistency-with-ground-truth
  pass, which is covered under Contradictions below.
- **"co-location convention"**: spec.md (C1), research.md (R5), data-model.md, and
  quickstart.md all describe the same claimed mechanic in matching language ("the SAME
  co-location convention `visual-implementation-trace.md` already uses"). The wording is
  internally consistent across all five artifacts -- the defect is that the convention
  described does not exist in the cited file and does not match the repo's actual
  directory layout (F1). Terminology is uniform; the referent is wrong.
- **F-number**: research.md tags this feature "F039 (TENTATIVE)" and explicitly declines
  to edit `docs/roadmap/roadmap.md`. spec.md and plan.md do not independently assert a
  different F-number, so there is no cross-artifact F-number contradiction. F038 is
  confirmed as the current highest allocated F-number in `docs/roadmap/roadmap.md`
  (`F038 Tabular Editor BPA spike`), so "F039 tentative, next-free" is accurate at the
  time of writing.

No terminology contradiction found beyond the F1 referent problem noted above.

---

## 4. Constitution alignment

| Principle | Alignment finding |
|-----------|--------------------|
| I. Agent-First, Gate-Enforced | plan.md's Constitution Check correctly identifies that enforcement is via the EXISTING human design-review sign-off, not a new mechanical rule -- and this is consistent with the SCOPE GUARD's "no rule-id" default. Fails-closed property is preserved in spec language (FR-007) even though no `retail check` code enforces it. No violation. |
| III. Medallion / Gold-Only | Feature touches no schema, no SQL, no bronze/silver/gold table. Confirmed: all four target paths (template, two doc edits, one worked instance) are docs/Markdown only. No violation. |
| IV. Source-Mapping-Before-Silver | Not implicated; feature does not touch `silver.*` or the mapping gate. No violation. |
| V. Agent-Stops-at-Judgment | Two genuine business-policy questions (Q-FR014-SCOPE, Q-FR014-SEVERITY) are correctly raised as OPEN and are not defaulted or silently resolved anywhere across spec.md, plan.md, tasks.md, or quickstart.md. quickstart.md step 4 explicitly instructs "STOP before marking this dimension not-applicable-with-reason" absent an explicit human ruling -- correct Principle-V posture. This is compliance, not a violation. |
| VI. Defaults-Then-Deviations | Three non-Principle-V defaults (C1, C2, C3) are recorded with stated reasoning and reversibility in spec.md's Clarifications, consistent with plan.md's Constitution Check row VI. Correctly distinguished from the two OPEN Principle-V items. However, C1's stated default (see F1) is a default that does not actually correspond to a real, reusable existing mechanism -- it defaults into a resolution mechanic that has to be freshly invented at task time, which weakens (without invalidating) the "reuse, don't invent" reasoning given for adopting it. |
| VII. C086-is-an-example | Confirmed: FR-009, FR-013, and the worked-instance separation (generic template vs. `mappings/retail_store_sales/design/` filled copy) are consistent across all six artifacts. T023/T024 give concrete deterministic greps to verify this holds post-authoring. No violation. |
| VIII. Static-First/Live-Deferred | Confirmed via research.md R7's explicit deferred-capability inventory (F016, live DB, CVD-simulation engine, new rule, new stage, automated staleness detector, roadmap edit) -- all correctly named as NOT assumed to exist. See Section 6 for independent verification. No violation. |
| IX. Secrets/Reproducibility | No host/DSN/secret literal appears in any of the six artifacts (confirmed by reading). ASCII/UTF-8-no-BOM is stated as a requirement (FR-013) and a verification task (T028) exists. No violation observed in the planning artifacts themselves (the produced deliverables have not yet been authored at this ANALYZE stage). |
| Hard rule #9 (no fabricated score) | No numeric confidence/health/maturity/completeness field appears anywhere in spec.md, plan.md, tasks.md, research.md, data-model.md, or quickstart.md. All six use only the four-value status vocabulary + evidence[] + blocking_reasons[]. Confirmed by direct read plus a targeted grep (Section 6). No violation. |

**Overall**: no Principle is violated by the planning artifacts under review. The two
Principle-V carve-outs are handled correctly (raised, not resolved). `scope_ok = true`.

---

## 5. Contradiction / duplication / ambiguity scan

### F1 -- GAP (medium): token-file co-location convention does not match the repo or its own cited precedent

**Where**: spec.md (Clarifications C1, FR-003, FR-009, FR-015), research.md (R5),
plan.md (Structure Decision item 2/4, Phasing), data-model.md (`contrast.token_file`),
tasks.md (T013, T020), quickstart.md (step 2).

**Claim made (consistently, across all six artifacts)**: the contrast dimension resolves
its cited `*-design-tokens.yaml` file "by following the SAME co-location convention
`templates/visual-implementation-trace.md` already uses -- the token file already
associated with the page's design mapping under `mappings/<subject>/design/`."

**Verified against the actual repo**:
- `templates/visual-implementation-trace.md` contains **zero** occurrences of the word
  "token" -- it establishes no token-file co-location convention of any kind to reuse.
- The only `*-design-tokens.yaml` file in the repository is at the repo-root path
  `design/tokens/tower-retail-design-tokens.yaml`.
- `mappings/retail_store_sales/design/` (the directory the convention claims the token
  file lives under) contains exactly three files: `dashboard-layout.md`,
  `visual-contract-binding-map.md`, `visual-list.md` -- no token file.
- `src/retail/rules/design_contrast.py`'s `_iter_tokens_files()` finds token files by a
  global suffix scan over `ctx.tracked_files` (any tracked path ending in
  `-design-tokens.yaml`), not by any per-subject-area or per-page co-location lookup.
  There is no "association" mechanism in the shipped code for the plan to reuse.

**Impact**: T013 ("document the token_file resolution mechanic: the SAME co-location
convention `visual-implementation-trace.md` already uses") cannot be completed as
written, because the cited source establishes no such convention, and the actual worked
example (T020) will have to cite the real repo-root path
(`design/tokens/tower-retail-design-tokens.yaml`), not a `mappings/retail_store_sales/
design/`-nested path, contradicting the mechanic FR-015/C1/R5 describe. This is a
same-directory naming collision: two different things are both called "the design/
location" -- the per-subject-area `mappings/<subject>/design/` folder, and the
repo-root `design/tokens/` folder -- and the spec/plan/research conflate them.

**Recommendation** (informational only; this stage does not edit other files): at task
time, either (a) correct FR-015/C1 to state the actual resolution rule (a global
suffix-scan match, or an explicit one-token-file-per-repo assumption, consistent with
CT1's real behavior and the YAGNI reasoning research.md R5 already gives for rejecting a
new index file), or (b) if a true per-subject co-location is wanted, that is a NEW
mechanism this feature would be introducing, not a reuse of an existing one -- which
would need to be named honestly as new, not attributed to a precedent that does not
establish it.

### F2 -- GAP (low): `ct1_result: file-not-found` is not a real CT1 output category

**Where**: data-model.md (`contrast.ct1_result` enum), tasks.md (T012), quickstart.md
(step 2).

**Verified**: `design_contrast.py`'s only `Finding`-emission sites are: (1) an
unparseable/missing contrast floor, (2) an invalid hex value, (3) a below-floor ratio,
(4) a YAML parse failure. If a `*-design-tokens.yaml` file is simply absent or not
matched by `_iter_tokens_files()`, CT1 emits **no finding at all** for it (silently) --
CT1 has no "file not found" finding category to report.

**Impact**: the checklist's `ct1_result: file-not-found` value is not something CT1 can
ever actually assert; it is a checklist-invented category being presented as if it were
one of CT1's own outputs. This does not block authoring (the checklist can still record
"file not found" as its OWN determination, made by the checklist-filler when they cannot
locate the cited file), but as currently worded in data-model.md/quickstart.md it implies
CT1 itself would report this, which it structurally cannot. Low severity: a wording
fix (attribute "file-not-found" to the checklist author's own check, not to CT1),
not a functional defect.

### F3 -- Ambiguity (low): "H9" tag possibly reused across two unrelated gaps

**Where**: spec.md line 9 ("Input: User description: 'H9 (gap #14)...'").

**Observation**: an untracked file `mappings/retail_store_sales/approval-request-
H9-time-intel.md` exists per this session's git-status context, whose filename suggests
"H9" is already used to label a **time-intelligence** gap, not the accessibility/RTL gap
this feature addresses. That file was not found inside this worktree
(`.claude/worktrees/HERA`), so this analysis cannot confirm whether the two "H9" usages
are the same identifier accidentally reused across two different gap items, or an
artifact confined to a different, unrelated branch/worktree. Flagged as low-severity/
ambiguity for the owner to confirm the gap-numbering ledger has not double-assigned
"H9" -- this does not affect this feature's own internal correctness.

### F4 -- Observation (low, not a defect): severity asymmetry between "unfilled" and "filled-with-defect"

**Where**: FR-007 vs. Q-FR014-SEVERITY (spec.md), mirrored in T010/T011.

**Observation**: FR-007 makes an absent or partially-unfilled checklist dimension an
unconditional `blocking_reasons[]` entry (hard blocker), while Q-FR014-SEVERITY leaves
open whether a dimension that IS filled but records a genuine defect only downgrades the
page to `warning` (not `blocked`) pending the owner's ruling. As currently drafted, a
page that never reviewed RTL at all is guaranteed `blocked`, while a page that reviewed
RTL and found a real mirroring defect could end up merely `warning` if the owner rules
that way. This is not a contradiction (both rules are stated correctly per their own
scope, and the spec explicitly marks the second question OPEN pending a human ruling) --
it is an incentive question worth the named human's attention when they resolve
Q-FR014-SEVERITY, since the interim floor could reward not-reviewing over
reviewing-and-reporting a real problem. No artifact edit is warranted at this stage;
this is a note for the eventual owner ruling, not a spec defect.

**No other contradictions, duplications, or unresolved ambiguities were found.** In
particular:
- No duplication was found between this feature and CT1 / the theme-JSON purity linter
  (spec 060) / `design_theme_fidelity.py` / the retail-term dictionary / the
  mobile-layout workflow -- the "Boundary against neighbouring shipped work" section's
  claims were checked against each named file and hold up (CT1 computes a ratio and
  never reviews RTL/colorblind legibility; the purity linter scans forbidden keys, not
  legibility; `design_theme_fidelity.py` checks token-to-theme agreement, not
  readability; the term dictionary is Stage 1 term meaning, unrelated to Stage 6 layout).
- No duplicate FR numbering, no orphan task (a task with no FR tag), and no FR with zero
  covering tasks was found (Section 1).
- The two bare `[NEEDS CLARIFICATION]` markers appearing in spec.md's body text
  (Edge Cases, FR-006, FR-014) are each explicitly annotated as resolving to the two
  OPEN Q-FR014 items in the Clarifications section -- none is a dangling, unresolved
  marker left unaddressed.

---

## 6. Deferred-capability leakage scan (F016 / live DB)

Checked every one of the six artifacts for any assumption that F016 (the Power BI
execution adapter) or a live database connection exists or is callable:

- **spec.md**: FR-002 explicitly forbids render/open/publish/connect to Power BI
  Desktop, a live semantic model, or F016; names F016 as "gated and does not exist."
  No leakage.
- **plan.md**: Constraints section repeats the same prohibition; Constitution Check row
  VIII states the same; Technical Context states "No `pbi-cli`, no Power BI MCP, no
  network, no DB driver." No leakage.
- **tasks.md**: T007/T008 require a FORBIDDEN OPERATIONS section naming F016 explicitly;
  T002 runs only the existing static `retail check` (no `--db`/live-DSN flag anywhere in
  any task). No leakage.
- **research.md**: R7 is an explicit, itemized "deferred capabilities NOT assumed" list
  covering F016, live DB, a CVD-simulation engine, a new rule, a new stage, an automated
  staleness detector, and a roadmap-ledger edit -- each stated as not existing/not
  assumed. No leakage.
- **data-model.md**: the colorblind-safe dimension is explicitly stated as "a documented
  HUMAN/agent-read judgment against fixed criteria, NOT a numeric CVD-simulation score";
  no field or enum value implies a rendering or live-connection step. No leakage.
- **quickstart.md**: the "What this feature does NOT let you do" section restates the
  F016/live-DB/new-rule/new-status/self-granted-scope-ruling prohibitions verbatim, and
  every numbered fill-step operates on already-committed static text (YAML/JSON/
  Markdown) read from disk, never a running Power BI process. No leakage.

**Independently confirmed**: `retail check` (the only tool this feature's tasks invoke,
T002/T026) is a static, read-only checker -- CT1 (`design_contrast.py`) parses YAML from
disk and opens no database connection and renders no pixel (confirmed by reading the
rule's own docstring and code: "Read-only: parses committed YAML, renders no pixel,
opens no DB, writes nothing"). No artifact in this feature assumes F016 or a live DB
exists. **No deferred-capability leakage found.**

---

## Summary

| Severity | Count | IDs |
|----------|-------|-----|
| Medium | 1 | F1 |
| Low | 3 | F2, F3, F4 |
| Constitution violations | 0 | -- |

The planning artifacts are internally well-aligned (terminology, FR-to-task coverage,
success-criteria testability, and Constitution/hard-rule-#9 compliance all check out),
and the two Principle-V questions are correctly left open rather than defaulted. The one
substantive defect (F1) is a factual mismatch between the claimed token-file
co-location "reuse" mechanic and both (a) the actual shipped precedent file
(`visual-implementation-trace.md`, which says nothing about tokens) and (b) the real
repo layout (the only token file lives at repo-root `design/tokens/`, not under any
`mappings/<subject>/design/` directory). This should be corrected before or during
Phase 4/5 task execution (T013, T020) so the worked instance does not silently paper
over a resolution mechanic that does not exist as described. It is a planning-artifact
consistency defect, not a Constitution violation -- it does not touch grain, PII,
business policy, or self-granted approval, and it does not weaken any fail-closed
property, since CT1 itself still runs and still fails closed regardless of how the
checklist locates the file to cite.

