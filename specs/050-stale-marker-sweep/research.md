# Phase 0 Research: SC1 Status-Claim Reconciler

## Decision 1 -- Lift the A1 resolver pattern, do not invent a new one

**Decision**: SC1 reuses the A1 (`src/retail/rules/routes.py`) shape verbatim where
it overlaps: lazy `import yaml` inside the handler, manifest-must-be-in-tracked_files
guard, fail-loud on malformed YAML / wrong shape, per-entry resolution of a
repo-relative POSIX path against `set(ctx.tracked_files)`, `Severity.ERROR` on a
contradiction in either direction, a small `_finding(message, locator)` helper.

**Rationale**: A1 is shipped, reviewed, and already enforces exactly the
"built target missing / planned target exists" pair SC1 needs. Lifting it minimizes
new surface and inherits A1's fail-closed posture. The runner's `tracked_files`
(populated from `git ls-files`, repo-relative POSIX) is the same evidence source
A1 resolves against, so artifact-existence resolution behaves identically.

**Alternatives rejected**:
- A bespoke resolver -- rejected: duplicates A1 logic and risks divergent posture.
- Folding SC1 into `routes.py` -- rejected: different manifest, different second
  step (anchor scan); keep modules focused (one rule group per file, repo convention).

## Decision 2 -- The anchor check is a stdlib substring presence test

**Decision**: SC1 reads the claiming `doc`'s committed text via
`(ctx.repo_root / doc).read_text(encoding="utf-8")` and tests whether the `anchor`
string is a substring (`anchor in text`). Presence, not position: no line number,
no offset, no regex. Absent anchor -> ERROR.

**Rationale**: This is the single step beyond A1, and it is the main design risk the
reviewers flagged (a prose matcher can false-positive). A literal substring presence
test is the narrowest possible matcher: it asks only "is the exact claim text the
manifest pins still in the doc". It does NOT parse the doc, infer status from prose,
or scan for free-form status words. The manifest author supplies the verbatim
snippet; SC1 verifies it is still there (so a manifest entry cannot silently point
at a claim that was deleted or reworded). No markdown dependency is introduced.

**Alternatives rejected**:
- Detecting a status WORD ("(planned)" / "NOT BUILT") by scanning prose -- REJECTED:
  this is the false-positive trap (legitimate forward-looking "planned" prose would
  trip it) and is materially more than A1 does. The manifest's `anchor` IS the pinned
  status text; SC1 checks the artifact's real state, not a free-form word scan.
- Regex / line-anchored matching -- rejected: brittle (line moves break it) for no
  gain over substring presence.

## Decision 3 -- claimed-status enum is {built, planned}, mirroring A1

**Decision**: `claimed-status` is one of `built` | `planned`, the same two-value
enum A1 uses for route status. `built` -> claimed-artifact MUST be tracked.
`planned` -> claimed-artifact MUST NOT be tracked. Any other value -> ERROR.

**Rationale**: SC1 reconciles a binary readiness claim against a binary evidence
fact (file exists or not). Two values cover both honest cases and both contradiction
cases. Reusing A1's vocabulary keeps the kit coherent.

**Alternatives rejected**: a richer status ladder (e.g. "in-progress") -- rejected:
there is no committed evidence to reconcile an intermediate state against; it would
reintroduce the graded-confidence smell Hard rule 9 forbids.

## Decision 4 -- Manifest top-level key is `claims`

**Decision**: The manifest is a mapping with a top-level `claims` list (A1 uses
`routes`). Each list item is a mapping with `id`, `doc`, `anchor`,
`claimed-artifact`, `claimed-status`.

**Rationale**: Parallels A1's `{routes: [...]}` shape so the shape-guard code is a
near-copy. `claims` names the domain (status claims) clearly.

**Alternatives rejected**: reusing the literal `routes` key -- rejected: misleading;
these are claims, not routes.

## Decision 5 -- Seed with one generic defect AND fix its prose in the same change

**Decision**: Seed the manifest with exactly one entry: the capability-state
governance doc that calls the shipped Net Sales end-to-end trace "(planned)" while
the trace is a tracked, shipped artifact (`planned` + present = stale marker). In
the SAME change, correct that doc's stale wording so the seeded entry resolves clean
and SC1 ships GREEN.

**Rationale**: Confirmed real (the trace doc is tracked; roadmap records it shipped
at stage 2 / PR #72). An enforced ERROR rule that landed RED would block every later
change. Fixing the wording is a tracked-document text correction, not a re-decision.
The constitution rule-count facet is explicitly OUT (delegated to sibling idea T5.5):
seeding it would force a prose matcher SC1 is deliberately not building.

**Alternatives rejected**:
- Seed both defects (incl. rule-count) -- rejected: out of scope, needs a word-scan
  matcher (false-positive risk), delegated to T5.5.
- Register the claim but defer the prose fix -- rejected: ships the gate RED on main.

## Decision 6 -- Accept the manifest-completeness drift gap (no coverage rule now)

**Decision**: SC1 checks only the claims listed in the manifest. Nothing verifies
the manifest is complete. Record the gap; do not build a coverage check.

**Rationale**: A1 shipped route resolution before its A3 coverage/bijection sibling;
the same staged path applies. A coverage rule is a separate future idea (YAGNI now).

**Alternatives rejected**: pairing SC1 with a coverage rule now -- rejected: scope
creep; A3-style coverage is independently addable later without changing SC1.

## Open items carried to ratification

None requiring a human Principle-V ruling. The three resolved ambiguities are
recorded in spec ## Clarifications on reversible advisor defaults; a human may flip
any of them at ratify with a localized change (seed-fix sequencing, completeness
gap, spine placement).
