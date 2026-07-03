# idea-engine: review + expand the user's own ideas -- design

- **Status:** Approved design (2026-07-03)
- **File touched:** `.claude/workflows/idea-engine.js`
- **Depends on:** the `serves` / `strengthens_layer` rails already in the file.

## Problem

The `idea-engine` workflow only generates and reviews ideas it invents from the
repo map. A user who has an idea of their own -- often rough, half-formed, hard to
put into words -- has no way to (a) feed it in, (b) have it grown into a fully
shaped idea, or (c) get it reviewed through the same rigorous gate.

## Goal

Two new capabilities, both on the SAME pipeline (no parallel second engine):

1. **Expand** a user's tiny/rough words into ONE fully-shaped idea (strongest
   reading), surfacing the reading it chose and the readings it rejected so a
   misread is visible, not silent.
2. **Review** the user's idea(s) through the existing skeptic + 4-reviewer panel +
   eligibility gate, and present the verdict where the user can find it.

Input mode (user choice): **mine + its own** -- expand the user's idea(s) AND let
the six lenses generate their own; review everything in one bank.

Expansion mode (default, recommended): **one best reading** per user idea. Can be
upgraded later to a pick-from-readings interaction.

## The load-bearing risk this design solves

In "mixed bank" mode the user's idea is threatened by three existing mechanisms:

1. `synthesize:merge` has **no schema** -- it emits prose, so structured fields
   (incl. `source_lens`) do NOT survive synthesis as structure.
2. The synthesizer is told to **dedupe/merge** ("keep the strongest framing") -- a
   user idea resembling a machine idea gets absorbed and the machine wording wins.
3. Render groups by **verdict**, not origin -- the user's idea is one `###` heading
   among dozens, unfindable.

Net without a fix: the user pastes a rough idea, gets a wall of machine ideas, and
cannot locate their own. The feature defeats itself.

## Design (reuses two patterns already proven in this file)

### 1. Interpret stage (new; runs ONLY when user ideas are supplied)

- New arg: `args.ideas` (array of strings) or `args.seed` (single string). Absent
  -> the stage is skipped and the workflow behaves exactly as today.
- One `interpret:user-ideas` agent (Opus xhigh) reads the user's raw words + the
  repo map and returns, per idea: a fully-shaped idea (title, pitch, horizon,
  why_it_fits, rough_shape, strengthens_layer, serves) PLUS a `user_note` carrying
  the ORIGINAL words, the chosen reading, and the rejected alternative readings.
- These are injected into the candidate pool tagged `origin: user`. They flow
  through cross-pollinate/fill (lenses MAY build on them), synthesize, verify, and
  the panel -- the same gate the machine ideas get.

### 2. `origin` rail (`user` | `engine`)

Rides the exact rails `serves` already uses:
`IDEA_SCHEMA` -> `PANEL_REVIEWER_SCHEMA` -> `aggregatePanel` return ->
`review.scored_ideas` -> render. Every generated idea defaults `origin: engine`;
interpreter ideas are `origin: user`. Makes provenance first-class, not
prose-dependent.

### 3. Synthesis guard

The synthesizer prompt gains: **never merge-away or drop an `origin: user` idea.**
Keep it as its own row; if a machine idea converges with it, NOTE the convergence
(a strength signal) rather than absorbing it. Same spirit as the existing
"KEEP + tag shipped" instruction. It must preserve `origin` and `user_note` in its
prose output for the user rows.

### 4. "Your Ideas" render lane

Modeled exactly on the existing `designCohort` / Design Foundation lane:
`ideas.filter(i => i.origin === 'user')`, rendered as a distinct cohort near the
TOP of the backlog so the user finds their verdict instantly -- with the verdict,
V/F scores, eligibility, and the interpreter's `user_note` (original words +
chosen reading + rejected readings). Renders present-but-empty on a no-user-input
run (a run with user ideas always populates it). The verdict shows whatever it is:
an ADOPTED or a REJECTED user idea both appear here, so a rejected idea is never
hidden only in `## REJECT`. A rejected user idea still gets its Rescue note.

## Scope guard (what this does NOT do)

- No second/parallel pipeline. One interpreter stage + one rail + one synthesis
  instruction + one lane.
- The interpreter does not auto-approve, promote, or bypass any gate. A user idea
  is reviewed like any other -- it can be ruled INELIGIBLE or REJECT.
- No new `retail check` rule, no runtime code, no DB touch. Respects every hard
  principle (the interpreter is told them; ineligible expansions are flagged).
- Expansion stays "one best reading" for now; the pick-from-readings interaction is
  a deferred future option (the `user_note` already carries the rejected readings,
  so upgrading later is cheap).

## Survival guarantee (added after review -- the load-bearing hardening)

The `origin` schema field makes provenance first-class from the panel onward, but the
synthesizer is schema-less and told to merge, and the panel only echoes `origin`. Two
LLM hops could drop or mislabel a user idea, silently emptying the "Your Ideas" lane --
the one outcome this feature exists to prevent. We hold the ground truth (`userIdeas`),
so we ENFORCE with JS, not prose:

1. **Re-assert origin by normalized title match.** In `review.scored_ideas`, any idea
   whose normalized title (`normKey`, the same identity `aggregatePanel` groups on, now
   lifted to module scope) matches a known user idea is forced to `origin: 'user'`
   regardless of the echoed value. A flipped tag cannot empty the lane.
2. **Loud "lost user idea" guard.** After aggregation, any `userIdeas` title with no
   normalized match among the aggregated titles was dropped/reworded by synthesis -- a
   re-assert cannot recover a vanished row, so it raises a DEGRADED banner naming the
   idea (same idiom as `uncovered_by_skeptic` / `panel_failed`).
3. **Note lookup by normalized key.** The "Your words / Read as" lines look up by
   `normKey` so a reworded title still shows the interpreter's reading.

## Verification

- `node --check` passes AND the edits avoid the two documented loader traps
  (no backtick nested in `${...}` -- two introduced were de-nested; no `.filter()`
  chained on a multi-line wrapper; no apostrophe-in-single-quote breakage).
- Not run end-to-end here (all-Opus, expensive) -- a real run is the user's call.
