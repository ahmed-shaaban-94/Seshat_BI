# Implementation Plan: Rule-Count Claim Reconciler (SC2)

**Branch**: `065-rule-count-reconciler` | **Date**: 2026-07-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/065-rule-count-reconciler/spec.md`

## Summary

Add a static governance rule SC2 to the `retail check` core that reconciles
prose RULE-COUNT CLAIMS against the authoritative rule count. A new
human-curated manifest `docs/quality/rule-count-claims.yaml` declares each claim
as `{id, doc, anchor, claimed-count}`. SC2 is a pure (context -> findings)
function in the existing rule contract, a clean lift of the shipped SC1 resolver
(`src/retail/rules/status_claims.py`): lazy `import yaml`, manifest-in-tracked_files
guard, fail-loud on missing/malformed input, per-entry anchor-presence check, and
an integer comparison of the manifest's `claimed-count` against the authoritative
count with ERROR on any mismatch. SC2 differs from SC1 in exactly one substantive
place: instead of resolving a `claimed-artifact` path against the tracked-files
set, it derives ONE authoritative integer from the committed golden rule-count
manifest (`docs/rules/rules-manifest.json`) read with the standard-library JSON
reader, and compares each entry's declared `claimed-count` against it. It never
imports the rules package to obtain the count (that would breach the stdlib-only
core invariant), and it never re-parses the integer out of the doc text (the
anchor is a presence check only). The expected rule-id set grows by one in the
same change so the wiring drift guard stays honest; the golden rule-count manifest
and the severity-posture snapshot are regenerated. The change also seeds the
manifest with the one confirmed generic defect -- the glossary line asserting a
stale rule count -- and corrects that stale prose to the POST-SC2 count in the
same change, so SC2 ships GREEN on the feature branch.

## Technical Context

**Language/Version**: Python 3.12+ (matches the existing `src/retail/` core; CI runs 3.13).

**Primary Dependencies**: Standard library only in the core import path. The
manifest parse uses a LAZY `import yaml` inside the handler (the exact pattern SC1
uses) -- `PyYAML` is a dev/optional dependency, NOT a core import-path dependency.
The authoritative count source is read with the standard-library `json` module. No
markdown parser and no import of the rules package: the anchor check is a stdlib
substring test against the claiming doc's committed text, and the count comes from
parsing a committed JSON file, never from `registry.all_rules()`.

**Storage**: N/A -- reads tracked text files (the manifest, each claiming `doc`,
and the committed rule-count JSON) and the tracked-files set; writes nothing at
runtime.

**Testing**: pytest, `@pytest.mark.unit`. New `tests/unit/test_rule_count_claims.py`
mirrors `test_status_claims.py`: a `_stage` helper writes a synthetic manifest +
synthetic claiming docs + a synthetic count-source JSON under `tmp_path` and
returns a real `RuleContext`; plus one live-manifest-vs-real-repo guard (shells
`git ls-files`, builds a real `RuleContext`, asserts zero findings after the seed
prose is fixed).

**Target Platform**: CI (Linux/Windows) under `retail check`; no DB, no network.

**Project Type**: Single project -- a governance rule submodule in `src/retail/rules/`.

**Performance Goals**: Negligible -- one small-manifest read, one small JSON read,
and per entry one substring scan of one claiming doc plus an integer comparison.
No measurable impact on `retail check` runtime.

**Constraints**: stdlib-only core import path (Principle VIII) -- no module-scope
import of the rules package or any third-party dependency; pure read-only, no
execution / no connection (Principle VIII, never-execute invariant -- B1 itself
would flag a module-scope DB/network import); fail-loud on missing/malformed input
including an unreadable count source (never vacuously green); strictly categorical
-- no numeric confidence/readiness value emitted (Hard rule 9; the claimed and
authoritative integers named in a finding are the reconciled counts, not a
confidence measure); generic-only schema + messages, no C086/pharmacy specifics in
rule or seed (Principle VII); manifest scoped to LIVE-STATE claims only, dated
snapshots never listed (never free-scans prose). ASCII + UTF-8-no-BOM in all
authored text (Principle IX).

**Scale/Scope**: One new rule module (`src/retail/rules/rule_count_claims.py`), one
new manifest (`docs/quality/rule-count-claims.yaml`), one new test file
(`tests/unit/test_rule_count_claims.py`), the `EXPECTED_RULE_IDS` +1 update, the
rule-package wiring edit (`src/retail/rules/__init__.py`), a golden rule-count
manifest regen (`retail manifest`) and severity-posture regen (`retail
severity-posture`), a one-line prose correction in the seeded glossary doc, and a
roadmap ledger row. NOTE on the count: the live registry holds N ids at authoring
(N == the size of `EXPECTED_RULE_IDS` on the base branch); registering SC2 makes it
N+1. The seeded glossary claim and the seed manifest `claimed-count` MUST both be
N+1 (the count AFTER SC2 registers), so the gate is GREEN at merge. The plan and
tasks derive N+1 from the live count at implement time rather than hardcoding a
number (which is exactly the drift SC2 exists to catch).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Agent-First, Gate-Enforced)**: PASS. SC2 is an enforced
  non-zero-exit static rule under `retail check`; a contradicted count claim fails
  closed (ERROR). It advises nothing -- the gate disposes.
- **Principle V (Agent Stops at Judgment Calls)**: HONORED / N/A carve-out. SC2
  surfaces NO grain/uniqueness, PII publish-safety, business rollup/segment, or
  product-identity question -- it reconciles a prose integer against a committed
  count source. The five build-relevant ambiguities (count source, seed-fix
  sequencing + target value, family-count scope, completeness drift gap,
  readiness-spine placement) were resolved by the advisor on documented defaults in
  spec ## Clarifications; none is a Principle-V ruling, so none is withheld for a
  human. Two items the workflow refuses to self-assign (the roadmap readiness stage
  and the roadmap F-number/spec-number) are recorded for the human, not answered.
- **Principle VII (C086 Is An Example, Not The Schema)**: PASS. The manifest schema
  and the rule are generic count-claim machinery; no pharmacy / C086 doc path or
  value is hardcoded in the rule or seeded as a kit-level entry. Test fixtures use
  synthetic doc paths, anchors, and a synthetic count-source JSON. The one seed
  entry references a generic governance doc (the glossary) + the generic committed
  rule-count manifest -- repo-infrastructure paths, not a worked-example value.
- **Principle VIII (Static-First Governance, Live Deferred)**: PASS. SC2 is a pure
  static read of committed text + one committed JSON + the tracked-files set. Core
  import path stays stdlib-only (lazy `import yaml`, stdlib `json`, stdlib substring
  anchor check, NO import of the rules package, no markdown dep, no network, no DB).
  It fails loud on missing/malformed/absent-anchor/unreadable-count-source input,
  never vacuously green. It opens no connection and executes nothing. (The
  never-execute rule B1 would itself flag a module-scope DB/network import in SC2's
  module; the count source is a data file, not governed code.)
- **Hard rule 9 (No fake confidence)**: PASS. SC2 is strictly categorical: the
  claimed integer either equals the authoritative integer or it does not. No numeric
  confidence score, readiness percentage, or graded value is computed or emitted --
  findings are yes/no statements that name the two reconciled counts only.
- **Principle IX (Secrets and Reproducibility)**: PASS. No secrets; all authored
  text is ASCII + UTF-8-no-BOM (`--` and `->`, no glyphs); paths stay short.
- **Wiring symmetry (roadmap discipline)**: PASS. `EXPECTED_RULE_IDS` is updated by
  one in the SAME change as the rule and its package wiring, and the golden
  rule-count manifest + severity-posture snapshot are regenerated -- the wiring test
  and the two golden-snapshot tests are the guards.
- **Ship-green discipline**: PASS. The seed defect's stale glossary prose is
  corrected to the POST-SC2 count in the same change, so an enforced ERROR rule does
  not land RED on main.

**Result**: No violations. No entries in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/065-rule-count-reconciler/
|-- plan.md              # This file
|-- spec.md              # Feature spec (stages 2-3)
|-- research.md          # Phase 0 output
|-- data-model.md        # Phase 1 output
|-- quickstart.md        # Phase 1 output
|-- contracts/
|   `-- sc2-rule-contract.md  # Phase 1 output (the rule's input/output contract)
|-- checklists/
|   `-- requirements.md  # spec quality checklist
|-- analysis.md          # Stage 5 (/speckit-analyze) output
|-- plan-review.md       # Stage 6 adversarial review output
`-- tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
src/retail/
|-- core.py                  # Finding / Severity / RuleContext (UNCHANGED, reused)
|-- registry.py              # @register decorator + all_rules() (UNCHANGED, reused)
|-- runner.py                # build_context / _git_ls_files (UNCHANGED, reused)
|-- manifest.py              # rule-count golden manifest (UNCHANGED code; regenerated output)
`-- rules/
    |-- __init__.py          # EDIT: add rule_count_claims to import tuple + __all__
    |-- status_claims.py     # SC1 sibling (UNCHANGED, read as the shape to mirror)
    `-- rule_count_claims.py # NEW: the SC2 rule

tests/
`-- unit/
    |-- test_rules_wiring.py         # EDIT: add "SC2" to EXPECTED_RULE_IDS (N -> N+1)
    |-- test_rules_manifest_snapshot.py  # UNCHANGED code; passes after manifest regen
    |-- test_severity_posture.py     # UNCHANGED code; passes after posture regen
    |-- test_status_claims.py        # SC1 tests (UNCHANGED, read as the shape to mirror)
    `-- test_rule_count_claims.py    # NEW: TDD for SC2 incl. live manifest-vs-real-repo guard

docs/
|-- quality/rule-count-claims.yaml   # NEW: the human-curated rule-count-claim manifest (seeded)
|-- glossary.md                      # EDIT: correct the seeded stale rule-count prose to N+1
|-- rules/rules-manifest.json        # REGEN: `retail manifest` (now contains SC2; count N+1)
|-- rules/severity-posture.json      # REGEN: `retail severity-posture` (now contains SC2)
`-- roadmap/roadmap.md               # EDIT: ledger row recording SC2 + N->N+1 note
```

**Structure Decision**: Single project; SC2 ships as a NEW submodule
`src/retail/rules/rule_count_claims.py` (rather than folding into `status_claims.py`)
to keep each rule module focused, and because SC2 reads a different manifest and a
different evidence source (the committed rule-count JSON, not the tracked-files set
for artifact existence). The new submodule MUST be added to
`src/retail/rules/__init__.py` (import tuple + `__all__`) to be discovered --
`test_all_submodules_importable` derives the list via `pkgutil`, so an unimported
new module is caught; `__init__.py` is the single wiring step for discovery, and the
two golden snapshots plus `EXPECTED_RULE_IDS` are the count-drift guards.

## Complexity Tracking

> No Constitution Check violations. This section is intentionally empty.
