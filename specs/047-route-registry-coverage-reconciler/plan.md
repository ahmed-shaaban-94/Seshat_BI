# Implementation Plan: Route-Registry Coverage Reconciler (A3)

**Branch**: `047-route-registry-coverage-reconciler` | **Date**: 2026-06-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/047-route-registry-coverage-reconciler/spec.md`

## Summary

Add a static governance rule A3 to the `retail check` core that reconciles the
knowledge map's "Route by task" id set against the routing manifest's id set as a
bijection: any id present on one side but not the other fails the gate (ERROR).
The rule is a pure (context -> findings) function in the existing rule contract,
mirroring the shipped A1 sibling. It adds a hand-rolled standard-library extractor
for the map's "Route by task" table (no new markdown dependency) and reuses the
existing lazy manifest parse. The expected rule-id set moves 33 -> 34 in the same
change so the wiring drift guard stays honest. The bijection already holds on main,
so A3 ships clean (zero findings) and locks the previously-unguarded invariant.

## Technical Context

**Language/Version**: Python 3.12+ (matches the existing `src/retail/` core; CI runs 3.13).

**Primary Dependencies**: Standard library only in the core import path. The
manifest parse uses a LAZY `import yaml` inside the handler (the same pattern A1
uses) -- `PyYAML` is a dev/optional dependency, NOT a core import-path dependency.
The map-table extractor is hand-rolled stdlib (no markdown-parsing library).

**Storage**: N/A -- reads two tracked text files (`docs/knowledge-map.md`,
`docs/routing/routes.yaml`); writes nothing.

**Testing**: pytest, `@pytest.mark.unit`. New `tests/unit/test_routes_coverage.py`
mirrors `test_routes.py`: synthetic-context cases plus one live-manifest-vs-real-map
guard (shells `git ls-files`, builds a real RuleContext, asserts zero findings).

**Target Platform**: CI (Linux/Windows) under `retail check`; no DB, no network.

**Project Type**: Single project -- a governance rule submodule in `src/retail/rules/`.

**Performance Goals**: Negligible -- two small-file reads + two set comparisons per
gate run. No measurable impact on `retail check` runtime.

**Constraints**: stdlib-only core import path (Principle VIII); pure read-only, no
execution / no connection (Principle VIII, never-execute invariant); fail-loud on
missing/malformed input (never vacuously green); generic-only messages (Principle
VII). ASCII + UTF-8-no-BOM in all authored text (Principle IX).

**Scale/Scope**: One new rule (~one small module), one new test file, the
EXPECTED_RULE_IDS 33->34 update, the rule-package wiring edit, and a roadmap ledger
row. The current id set on both sides is 26 ids ({1-22, 12a/b/c, 17a-d}).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Agent-First, Gate-Enforced)**: PASS. A3 is an enforced non-zero-exit
  static rule under `retail check`; a bijection difference fails closed. It advises
  nothing -- the gate disposes.
- **Principle VII (C086 Is An Example, Not The Schema)**: PASS. The rule and every
  finding reference only abstract route ids and document structure; no pharmacy /
  C086 route value, table name, code, segment, or PII column is read or emitted. The
  test fixtures use synthetic ids (e.g. "1", "2", "99"), never example route values.
- **Principle VIII (Static-First Governance, Live Deferred)**: PASS. A3 is a pure
  static read of two committed text files. Core import path stays stdlib-only (lazy
  `import yaml`, hand-rolled stdlib table parse, no markdown dep, no network, no DB).
  It fails loud on missing/malformed input, never vacuously green. It opens no
  connection and executes nothing (never-execute invariant; B1 would itself flag a
  module-scope DB/network import).
- **Principle V (Agent Stops at Judgment Calls)**: HONORED. The three governance-posture
  questions (roadmap stage, bijection scope, severity posture) are recorded as open
  `[NEEDS CLARIFICATION]` markers in the spec for human ratification; the plan
  proceeds on the advisor's reversible defaults and does not self-grant the ruling.
- **Principle IX (Secrets and Reproducibility)**: PASS. No secrets; all authored text
  is ASCII + UTF-8-no-BOM; paths stay short.
- **Wiring symmetry (roadmap discipline)**: PASS. EXPECTED_RULE_IDS is updated 33->34
  in the SAME change as the rule and its package wiring -- the wiring test is the guard.

**Result**: No violations. No entries in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/047-route-registry-coverage-reconciler/
|-- plan.md              # This file
|-- spec.md              # Feature spec (stages 2-3)
|-- research.md          # Phase 0 output
|-- data-model.md        # Phase 1 output
|-- quickstart.md        # Phase 1 output
|-- contracts/
|   `-- a3-rule-contract.md   # Phase 1 output (the rule's input/output contract)
|-- checklists/
|   `-- requirements.md  # spec quality checklist
`-- tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
src/retail/
|-- core.py                  # Finding / Severity / RuleContext (UNCHANGED, reused)
|-- registry.py              # @register decorator + all_rules() (UNCHANGED, reused)
`-- rules/
    |-- __init__.py          # EDIT: add routes_coverage to import tuple + __all__
    |-- routes.py            # A1 sibling (UNCHANGED, read as the shape to mirror)
    `-- routes_coverage.py   # NEW: the A3 rule

tests/
`-- unit/
    |-- test_rules_wiring.py     # EDIT: add "A3" to EXPECTED_RULE_IDS (33 -> 34)
    |-- test_routes.py           # A1 tests (UNCHANGED, read as the shape to mirror)
    `-- test_routes_coverage.py  # NEW: TDD for A3 incl. live map-vs-manifest guard

docs/
|-- knowledge-map.md         # READ-ONLY source of the map id set ("Route by task")
|-- routing/routes.yaml      # READ-ONLY source of the manifest id set
`-- roadmap/roadmap.md       # EDIT: ledger row recording A3 + 33->34 note
```

**Structure Decision**: Single project; A3 ships as a NEW submodule
`src/retail/rules/routes_coverage.py` (rather than folding into `routes.py`) to keep
each rule module focused and because A3 reads a different source (the map) than A1.
The new submodule MUST be added to `src/retail/rules/__init__.py` (import tuple +
`__all__`) to be discovered -- `test_all_submodules_importable` derives the list via
`pkgutil`, so an unimported new module is caught.

## Complexity Tracking

> No Constitution Check violations. This section is intentionally empty.
