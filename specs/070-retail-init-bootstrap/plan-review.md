# Adversarial Plan Review — 070 retail init

Single adversarial skeptic (the final chain stage), run twice: an initial review that
returned **BLOCK**, then a re-review after reconciliation that returned
**PASS-WITH-NOTES**. This file records both rounds and the resolution, per the
`idea-to-spec` / speckit-finish-chain pattern (mirrors `specs/062-.../plan-review.md`).

## Round 1 — verdict: BLOCK

The skeptic verified load-bearing facts against the codebase (`profile.py`,
`retail-onboard-table` SKILL, `AGENTS.md`, the constitution) and found:

| # | Severity | Finding |
|---|----------|---------|
| BLOCKER-1 | BLOCKER | The P1 "aha" (grain candidates + column types on first run) was unreachable: the only profiler (`profile.py`) is DB/SQL-only; FR-003 forbade `init` from invoking it; the "delegated" verbs are agent-performed prose, not callable by the specified `kit_init.py` / `retail init` wizard; and the quickstart's CSV example had no implementation. Net: the feature would ship either an empty `[PENDING LIVE PROFILE]` or a terminal-first wizard forking the agent-first conductor (Principle I). |
| MAJOR-2 | MAJOR | Routing was internally inconsistent (`retail-orchestrate → source-mapping` vs `retail-onboard-table`), pointed upstream of where grain comes from, and `retail-onboard-table` (the real front door) was absent from the compass `verbs[]`. |
| MAJOR-3 | MAJOR | `init` hard-coded its own four-seam list that DIVERGED from the delegate `first-hour-compass` ("metric policy" vs "product identity") — a forked second source of truth, the exact anti-fork the spec claimed to avoid. |
| MAJOR-4 | MAJOR | "stdlib-only" invariant leaked: the drift check must parse YAML, so `compass_project` cannot be stdlib-only. |
| MINOR-5 | MINOR | Plan over-claimed "amendment-safe: PASS"; `AGENTS.md` has no fence, so writing governed prose there is the normal path and its source-vs-constitution check is deferred. |
| MINOR-6 | MINOR | The prose-fence "drift check" cannot be byte-compared to YAML — two different mechanisms were conflated. |
| MINOR-7 | MINOR | Verb set drifted from the design-source sketch; the source/projection YAML split is near-nominal. |

## Resolution (cross-propagated across all seven artifacts)

- **BLOCKER-1 (both prongs)** — `init` reframed as primarily an agent Workflow Skill;
  the Python module + `retail init` CLI are substrate-writing only (no profiling, no
  DB, no prompt/menu; writes substrate + prints the next agent step). SC-001 rewritten
  so the grain/column result is agent-executed over a LIVE DB, degrading honestly to
  `[PENDING LIVE PROFILE]` without one. Fabricated CSV example + interactive wizard
  session removed from quickstart; no CSV/Excel profiler in scope (YAGNI).
- **MAJOR-2** — single route `first-hour-compass → retail-onboard-table`; the verb
  added to the compass `verbs[]` (contract P4, data-model E2, SC-007).
- **MAJOR-3** — `init`'s divergent seam list dropped; seam wording deferred to
  `first-hour-compass` as single source (FR-009/SC-006/US3/T018/T020; R4).
- **MAJOR-4** — stdlib-only claim dropped for `compass_project` (MAY import `pyyaml`
  lazily, like `semantic-check`/`value-check`); only the `retail check` core stays
  stdlib-only.
- **MINOR-5** — amendment-safety claim scoped to outside-fence invariance; the
  `AGENTS.md`-has-no-fence caveat + Phase-2 deferral recorded.
- **MINOR-6** — drift check split into byte-exact YAML and prose render-and-compare.
- **MINOR-7** — verb-set delta + near-nominal YAML split recorded in R1 + contract.

## Round 2 — verdict: PASS-WITH-NOTES

Re-review confirmed BLOCKER-1 and all four MAJORs CLOSED with substantive,
cross-propagated edits. Three MINOR doc-consistency residuals were flagged:

| # | Location | Status |
|---|----------|--------|
| MINOR-8 | spec.md:135 stale wired-verb list | FIXED (now `first-hour-compass → retail-onboard-table`) |
| MINOR-9 | tasks.md:103 wizard-shorthand in Implementation strategy | FIXED (reworded to agent-performed) |
| NOTE | quickstart.md seam list restatement | LEFT — verbatim-identical + attributed to `first-hour-compass`; passes T020 (anti-fork targets sources of truth, not attributed illustrations). Optional future hardening: replace with a pointer. |

## Final state

- **Round-2 verdict:** PASS-WITH-NOTES.
- **BLOCKER + all MAJORs:** closed.
- **MINOR-8, MINOR-9:** fixed after round 2.
- **Remaining:** one optional NOTE (non-blocking).
- **`retail check`:** exit 0 on the worktree (pre-commit gate passed on each commit).
- **`speckit-analyze`:** 0 CRITICAL / 0 HIGH (coverage 21/23 full, 2 partial resolved).

Nothing gates implementation. This is a DEFINE-and-CHECK output: it stops at the
ratify ledger (`ratify-ledger.md`) for a named human. No implementation task has been
executed; nothing has merged to `main`.
