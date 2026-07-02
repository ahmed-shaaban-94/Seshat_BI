# Phase 0 Research: Rule-Count Claim Reconciler (SC2)

All unknowns for SC2 are resolved by the shipped SC1 sibling and the existing
retail-check core; no external research was required. This file records the
decisions that shape the plan and the rationale/alternatives for each.

## Decision 1 -- Authoritative count source

**Decision**: Derive the authoritative rule count from the committed golden
rule-count manifest `docs/rules/rules-manifest.json`, read as committed text and
parsed with the standard-library `json` module. SC2 does NOT import the rules
package (`registry.all_rules()`) at module scope.

**Rationale**: The retail-check core import path is stdlib-only (Principle VIII).
SC1 keeps the core dependency-free, using only a lazy `import yaml` inside its
handler. The golden rule-count manifest is already golden-tested
(`tests/unit/test_rules_manifest_snapshot.py`) to equal `len(all_rules())`, so
reading it yields the same authoritative integer without pulling governed
application code into the gate core. `json` is stdlib, so no dependency is added
to the import path.

**Alternatives considered**:
- `len(registry.all_rules())` -- rejected: a module-scope import of the rules
  package breaches the stdlib-only core invariant and pulls governed code into the
  gate, exactly what SC1's discipline avoids. (A lazy import inside the handler
  would avoid the module-scope breach but still couples SC2 to the live registry
  object; the golden JSON is the cleaner, already-tested proxy.)
- `len(EXPECTED_RULE_IDS)` from the wiring test -- rejected: importing a test
  module from a rule is an inversion of the dependency direction; the wiring test
  is a consumer of the registry, not a source of truth SC2 should read.

**Reversibility**: costly. The count-source choice shapes the module's import
surface and the never-execute guarantee; changing it later is a design change, not
a text edit. Recorded as spec Clarifications Q1.

## Decision 2 -- Count comparison, not in-prose number extraction

**Decision**: SC2 compares the manifest's declared `claimed-count` field against
the authoritative integer. It does NOT extract an integer from the anchor sentence
text. The anchor is a substring-presence check only (is the claiming sentence still
in the doc).

**Rationale**: Re-parsing a number out of prose is brittle (multiple numbers in a
sentence, ranges, formatting) and would risk false positives -- the exact hazard
that kept SC1's count facet out of scope until a dedicated, manifest-declared
approach existed. Declaring the integer in the manifest makes the parse
unambiguous and keeps the doc-side check identical to SC1's proven anchor test.

**Alternatives considered**: a regex "N rules" scanner over the anchor -- rejected
as brittle and duplicative of the manifest's `claimed-count`.

## Decision 3 -- Seed defect and ship-green sequencing

**Decision**: Seed the manifest with the one confirmed generic defect (the glossary
line asserting a stale rule count) and correct that glossary prose to the POST-SC2
count in the SAME change. Both the corrected glossary number and the seed manifest
`claimed-count` equal the count AFTER SC2 registers (N+1, not the pre-SC2 N).

**Rationale**: An enforced ERROR rule that ships RED on main blocks every later
change until the prose is fixed; SC1 set the precedent of landing the seed defect
and its correction together. Because registering SC2 itself increments the registry
by one, the correct target is the post-SC2 count -- correcting to the pre-SC2 count
would make the gate red the moment SC2 is registered.

**Reversibility**: easy (a small text edit). Recorded as spec Clarifications Q2 and
success criterion SC-006.

## Decision 4 -- Dated-record immunity via manifest-only scope

**Decision**: The manifest lists only LIVE-STATE count claims. Dated as-of-then
snapshots (ADR/decision/audit records that recorded a count on a past date) are NOT
listed and are never touched, because SC2 is manifest-only and never free-scans the
repo for "N rules" strings.

**Rationale**: Dated snapshots were correct as-of-then; flagging them would be a
false positive. Manifest-only scope makes dated-record immunity structural, not a
special case in the matcher. Recorded as spec FR-017.

## Decision 5 -- Wiring surfaces and the count arithmetic

**Decision**: Registering SC2 requires the established five-place wiring: (1) the
new module, (2) `src/retail/rules/__init__.py` import tuple + `__all__`, (3)
`EXPECTED_RULE_IDS` in the wiring test, (4) regenerate the golden rule-count
manifest via `retail manifest`, (5) regenerate the severity-posture snapshot via
`retail severity-posture`. The rule count moves N -> N+1.

**Rationale**: The repo's new-rule wiring checklist (per project memory) touches
exactly these five surfaces; missing one fails a golden test. The count N is read
from the live registry / `EXPECTED_RULE_IDS` at implement time -- it is deliberately
NOT hardcoded in the spec/plan because a hardcoded number is itself the drift class
SC2 governs. Recorded as spec FR-015.

## Decision 6 -- Off-spine placement

**Decision**: SC2 maps to no roadmap F-number and advances no seven-stage readiness
stage; it is an idea-bank integrity rule, sibling to SC1/DF1, recorded outside the
Source -> ... -> Publish spine.

**Rationale**: SC2 is governance/observability-integrity machinery, structurally
identical to the SC1/DF1 rules already recorded off-spine. The roadmap readiness
stage and the F-number/spec-number are a human's to assign at ratify time; the
workflow records them for the human and does not self-assign them. Recorded as spec
Clarifications Q5 and the Principle-V deferral note.
