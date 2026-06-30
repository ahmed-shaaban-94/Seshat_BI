# Implementation Plan: Stale-Marker Sweep / Status-Claim Reconciler (SC1)

**Branch**: `050-stale-marker-sweep` | **Date**: 2026-06-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/050-stale-marker-sweep/spec.md`

## Summary

Add a static governance rule SC1 to the `retail check` core that reconciles prose
STATUS CLAIMS against committed evidence. A new human-curated manifest
`docs/quality/status-claims.yaml` declares each claim as `{id, doc, anchor,
claimed-artifact, claimed-status}`. SC1 is a pure (context -> findings) function in
the existing rule contract, a clean lift of the shipped A1 resolver
(`src/retail/rules/routes.py`): lazy `import yaml`, manifest-in-tracked_files guard,
fail-loud on missing/malformed input, per-entry resolution of `claimed-artifact`
against the tracked-files set with ERROR on a contradiction --
`built`+absent (false built) or `planned`+present (stale marker). SC1 adds one step
A1 does not have: it reads the claiming doc's committed text and confirms the
`anchor` snippet is still present (an absent anchor is itself an ERROR). The
expected rule-id set moves 35 -> 36 in the same change so the wiring drift guard
stays honest. The change also seeds the manifest with the one confirmed generic
defect and corrects that defect's stale prose in the same change, so SC1 ships
GREEN on the feature branch.

## Technical Context

**Language/Version**: Python 3.12+ (matches the existing `src/retail/` core; CI runs 3.13).

**Primary Dependencies**: Standard library only in the core import path. The
manifest parse uses a LAZY `import yaml` inside the handler (the exact pattern A1
uses) -- `PyYAML` is a dev/optional dependency, NOT a core import-path dependency.
No markdown parser, no new dependency: the anchor check is a stdlib substring test
against the claiming doc's text.

**Storage**: N/A -- reads tracked text files (the manifest, plus each claiming
`doc`) and the tracked-files set; writes nothing at runtime.

**Testing**: pytest, `@pytest.mark.unit`. New `tests/unit/test_status_claims.py`
mirrors `test_routes.py`: a `_stage` helper writes a synthetic manifest + synthetic
claiming docs + synthetic artifacts under `tmp_path` and returns a real
`RuleContext`; plus one live-manifest-vs-real-repo guard (shells `git ls-files`,
builds a real `RuleContext`, asserts zero findings after the seed prose is fixed).

**Target Platform**: CI (Linux/Windows) under `retail check`; no DB, no network.

**Project Type**: Single project -- a governance rule submodule in `src/retail/rules/`.

**Performance Goals**: Negligible -- one small-manifest read plus, per entry, one
membership test against the tracked set and one substring scan of one claiming doc.
No measurable impact on `retail check` runtime.

**Constraints**: stdlib-only core import path (Principle VIII); pure read-only, no
execution / no connection (Principle VIII, never-execute invariant -- B1 itself
would flag a module-scope DB/network import); fail-loud on missing/malformed input
(never vacuously green); strictly categorical -- no numeric confidence/readiness
value emitted (Hard rule 9); generic-only schema + messages, no C086/pharmacy
specifics in rule or seed (Principle VII). ASCII + UTF-8-no-BOM in all authored
text (Principle IX).

**Scale/Scope**: One new rule module (`src/retail/rules/status_claims.py`), one new
manifest (`docs/quality/status-claims.yaml`), one new test file
(`tests/unit/test_status_claims.py`), the `EXPECTED_RULE_IDS` 35->36 update, the
rule-package wiring edit (`src/retail/rules/__init__.py`), a one-line prose
correction in the seeded doc, and a roadmap ledger row. The live set holds 35 ids
today (S1-S8, D1-D11, R1, A1, A3, B1, B3, C1, C2, G1-G6, P1, P2, PP1).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Agent-First, Gate-Enforced)**: PASS. SC1 is an enforced
  non-zero-exit static rule under `retail check`; a contradicted status claim fails
  closed (ERROR). It advises nothing -- the gate disposes.
- **Principle V (Agent Stops at Judgment Calls)**: HONORED / N/A carve-out. SC1
  surfaces NO grain/uniqueness, PII publish-safety, business rollup/segment, or
  product-identity question -- it reconciles prose claims against file existence and
  committed text. The three build-relevant ambiguities (seed-fix sequencing,
  completeness drift gap, readiness-spine placement) were resolved by the advisor on
  reversible defaults in spec ## Clarifications; none is a Principle-V ruling, so
  none is withheld for a human.
- **Principle VII (C086 Is An Example, Not The Schema)**: PASS. The manifest schema
  and the rule are generic prose-claim machinery; no pharmacy / C086 doc path,
  artifact, value, segment, or PII token is hardcoded in the rule or seeded as a
  kit-level entry. Test fixtures use synthetic doc/artifact paths and anchors. The
  one seed entry references a generic capability-state governance doc + a
  readiness-trace doc -- repo-infrastructure paths, not a worked-example value.
- **Principle VIII (Static-First Governance, Live Deferred)**: PASS. SC1 is a pure
  static read of committed text + the tracked-files set. Core import path stays
  stdlib-only (lazy `import yaml`, stdlib substring anchor check, no markdown dep, no
  network, no DB). It fails loud on missing/malformed/absent-anchor input, never
  vacuously green. It opens no connection and executes nothing.
- **Hard rule 9 (No fake confidence)**: PASS. SC1 is strictly categorical: a claim
  matches the evidence or it does not. No numeric confidence score, readiness
  percentage, or graded value is computed or emitted -- findings are yes/no
  statements only.
- **Principle IX (Secrets and Reproducibility)**: PASS. No secrets; all authored
  text is ASCII + UTF-8-no-BOM (`--` and `->`, no glyphs); paths stay short.
- **Wiring symmetry (roadmap discipline)**: PASS. `EXPECTED_RULE_IDS` is updated
  35->36 in the SAME change as the rule and its package wiring -- the wiring test is
  the guard.
- **Ship-green discipline**: PASS. The seed defect's stale prose is corrected in the
  same change, so an enforced ERROR rule does not land RED on main.

**Result**: No violations. No entries in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/050-stale-marker-sweep/
|-- plan.md              # This file
|-- spec.md              # Feature spec (stages 2-3)
|-- research.md          # Phase 0 output
|-- data-model.md        # Phase 1 output
|-- quickstart.md        # Phase 1 output
|-- contracts/
|   `-- sc1-rule-contract.md  # Phase 1 output (the rule's input/output contract)
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
`-- rules/
    |-- __init__.py          # EDIT: add status_claims to import tuple + __all__
    |-- routes.py            # A1 sibling (UNCHANGED, read as the shape to mirror)
    `-- status_claims.py     # NEW: the SC1 rule

tests/
`-- unit/
    |-- test_rules_wiring.py     # EDIT: add "SC1" to EXPECTED_RULE_IDS (35 -> 36)
    |-- test_routes.py           # A1 tests (UNCHANGED, read as the shape to mirror)
    `-- test_status_claims.py    # NEW: TDD for SC1 incl. live manifest-vs-real-repo guard

docs/
|-- quality/status-claims.yaml             # NEW: the human-curated status-claim manifest (seeded)
|-- quality/post-idea-bank-capability-state.md  # EDIT: correct the seeded stale "(planned)" prose
`-- roadmap/roadmap.md                     # EDIT: ledger row recording SC1 + 35->36 note
```

**Structure Decision**: Single project; SC1 ships as a NEW submodule
`src/retail/rules/status_claims.py` (rather than folding into `routes.py`) to keep
each rule module focused and because SC1 reads a different manifest + additionally
reads claiming-doc text. The new submodule MUST be added to
`src/retail/rules/__init__.py` (import tuple + `__all__`) to be discovered --
`test_all_submodules_importable` derives the list via `pkgutil`, so an unimported
new module is caught; `__init__.py` is the single wiring step for discovery.

## Complexity Tracking

> No Constitution Check violations. This section is intentionally empty.
