# Quickstart: Decision Change Impact Map

**Feature**: `132-decision-change-impact-map` | **Date**: 2026-07-15

> Reviewer-facing walkthrough of the intended behavior. Describes how the feature would be used once
> implemented; this package implements nothing.

## When you reach for it

You are a reviewer or data owner and one of these is true for an **approved** decision:

- It has been **superseded** (a newer decision replaced it), or
- Its cited **evidence went stale** (a file it approved against no longer matches), or
- You are **about to supersede it** and want to see the reach first (a *preview*).

You want a truthful map of *what downstream analytical artifacts may now be wrong and what a human
should re-review* — without a fabricated risk number and without any change to state.

## What you run (conceptually)

The agent produces the Decision Change Impact Map for the subject decision, reusing the existing
disclosure-safe, contained-output pattern (same shape as the readiness explorer and passport):

1. It loads the Decision Store (read-only) and identifies the subject decision and its trigger
   (superseded / evidence-stale / preview).
2. It resolves the decision's scope to the concrete downstream artifacts derived from it and walks
   the existing lineage edges.
3. It produces **two forms of the same content**: a machine-readable projection and a human-readable
   rendering, written only under the contained output root after a disclosure scan.

## How to read the result

- **Subject** — the changed decision, its trigger, whether this is a preview, and whether it is a
  critical decision type.
- **Supersession chain** — what this decision replaced / what replaced it, read from the store's
  existing pointers, in order. A pointer that does not resolve appears as an incomplete-lineage
  warning, not invented history.
- **Affected artifacts** — split into:
  - **Direct** — artifacts that reference the decision's scope directly.
  - **Transitive** — artifacts reachable only through further dependency edges; each carries the full
    ordered chain of edge evidence paths.
  Each affected artifact names the affected **readiness stage(s)** and the **next human review
  action(s)** (drawn from the existing blocker-category authority — e.g. "re-confirm the approval",
  "re-run live validation").
- **Incomplete-lineage warnings** — the honest part. Any scope tag that resolved to *nothing*, any
  edge that could not be followed, and any dangling supersession pointer is listed here. **"No
  reference found" is never reported as "unaffected."** If you see an empty `affected[]` but
  non-empty `incomplete_lineage[]`, the correct reading is "could not determine," not "safe."
- **Cycles** — if the dependency graph loops, the cycle is named and the walk stops; a cycle is never
  presented as a completed transitive path.
- **Blocking condition** — if the store is absent/malformed or has an active-scope conflict, the map
  says so plainly and refuses a misleading clean result.

## What it will never do

- Never supersede, approve, invalidate, re-validate, publish, or change readiness state.
- Never write a decision record, an approval, a supersession pointer, or a `readiness-status.yaml`.
- Never emit a confidence / risk / trust / completeness / blast-radius number, percentage, or ranking.
- Never touch a live database or a Power BI connection.
- Never guess an edge to fill a gap, and never treat a missing reference as "unaffected."

## Verifying it works (fixtures)

The behavior is pinned by the fixture families in `contracts/fixtures/` — direct, transitive, cycle,
stale-evidence, missing-ref, active-scope conflict, incomplete-lineage, dangling supersession
pointer, absent/malformed store, preview, and a no-leak disclosure case — each with an expected
result in that README. Determinism is checked by producing the machine form twice and diffing bytes
(identical modulo the generated-at field).
