# Implementation Plan: Theme JSON Purity Linter

**Branch**: `060-theme-json-purity-linter` | **Date**: 2026-07-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/060-theme-json-purity-linter/spec.md`

## Summary

Add one static governance rule to the retail rule registry that scans committed
theme JSON files and enforces the surface-3 purity contract from
`docs/powerbi/theme-json.md`: a theme file carries styling defaults only and MUST
NOT carry business-logic keys (DAX, measures, calculated columns/tables, metric
definitions, semantic-model relationships, source mapping, sentiment
thresholds/rules, data validation). A forbidden key in a theme file is an ERROR
finding with a file-plus-pointer locator; a clean styling-only file produces no
findings. The rule is stdlib-only over committed text, generic (globs theme files,
never hardcodes tenant/example keys), and wired into the five governance records.
The exact literal forbidden-key vocabulary and any required-key assertion are a
Principle-V boundary judgment reserved for a human ruling (spec ## Clarifications
OPEN items); this plan defines the seam that consumes that vocabulary without
freezing the literal list.

## Technical Context

**Language/Version**: Python 3.13 (CI); 3.12 local also supported. Stdlib only.

**Primary Dependencies**: None beyond the standard library and the existing
in-repo retail governance framework (`src/retail/registry.py`, `src/retail/core`).
No third-party package is added.

**Storage**: N/A -- the rule reads committed text files; it persists nothing.

**Testing**: pytest, `-m unit`. Fixture-based unit tests under `tests/unit/`,
using the `is_test_path` exemption so fixtures may carry forbidden keys.

**Target Platform**: CI (Linux) and local Windows; runs as part of the `retail
check` governance gate.

**Project Type**: Single project -- a library rule module inside an existing
package, invoked by the existing rule runner.

**Performance Goals**: Negligible -- the committed theme corpus is small (order of
tens of files at most); a single pass parse + key walk per file is sufficient.

**Constraints**: stdlib-only; no network, no Power BI Desktop, no live service
(Principle VIII). ASCII, UTF-8 without BOM, short paths (Principle IX). Generic
vocabulary only (Principle VII). Fails closed on violation (Principle I). No
adjudication of borderline business-meaning (Principle V).

**Scale/Scope**: One new rule module (~1 file), five golden-record wiring touches,
one fixture set + unit tests. No new subsystem.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Agent-First, Gate-Enforced)**: PASS -- a purity violation is an
  ERROR that drives a non-zero exit; the rule enforces, it does not advise.
- **Principle V (Agent Stops at Judgment Calls)**: PASS -- the rule performs only a
  categorical present/absent key scan; the borderline vocabulary boundary is
  RECORDED as an OPEN human ruling, not auto-resolved. Deriving the literal list is
  gated on that ruling before wiring freezes it.
- **Principle VII (C086 Is An Example, Not The Schema)**: PASS -- the rule globs
  theme files generically and derives its vocabulary from the generic contract; no
  tenant/pharmacy/brand key or palette value appears in the rule.
- **Principle VIII (Static-First Governance)**: PASS -- stdlib-only over committed
  text, CI-able, no live dependency. Squarely static-core.
- **Principle IX (Secrets/Reproducibility)**: PASS -- reads styling source that
  carries no secrets; all authored artifacts are ASCII / UTF-8-no-BOM / short-path.
- **Ratified 044 (severity observed, not declared)**: PASS -- the rule declares one
  id; severity is observed per branch from emitted findings. No governed per-rule
  severity table is introduced.
- **YAGNI / scope discipline**: PASS -- adds the seam (a MUST-NOT purity scan), not
  the unbuilt token-to-theme fidelity rule and not a required-key assertion the
  human has not yet defined.

No violations. Complexity Tracking table omitted (nothing to justify).

## Project Structure

### Documentation (this feature)

```text
specs/060-theme-json-purity-linter/
|-- plan.md              # This file
|-- research.md          # Phase 0 output
|-- data-model.md        # Phase 1 output
|-- quickstart.md        # Phase 1 output
|-- contracts/
|   `-- rule-contract.md  # Phase 1 output (the rule's behavioral contract)
|-- checklists/
|   `-- requirements.md   # Spec quality checklist (Stage 2)
`-- tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
src/retail/
|-- registry.py                 # existing: @register decorator + all_rules() (unchanged)
|-- core/                       # existing: Finding, RuleContext, Severity, is_test_path (unchanged)
`-- rules/
    |-- __init__.py             # MODIFIED: add design_theme to import tuple + __all__
    |-- pbir.py                 # existing: structural precedent (JSON scan + pointer locator + is_test_path)
    `-- design_theme.py         # NEW: the @register purity rule

docs/rules/
|-- rules-manifest.json         # REGENERATED: adds the new rule id + title
`-- severity-posture.json       # REGENERATED: adds the new rule id's observed severity

tests/unit/
|-- test_rules_wiring.py        # MODIFIED: add new rule id to EXPECTED_RULE_IDS
`-- test_design_theme.py        # NEW: fixture-based unit tests for the rule
    (+ fixture theme files under the test-exemption path)
```

**Structure Decision**: Single-project library rule. The rule module joins the
existing `src/retail/rules/` package and is discovered by the existing runner via
the side-effecting import in `__init__.py`. This mirrors every existing rule
(pbir.py is the closest JSON-scanning precedent) and requires no new subsystem,
directory, or dependency.

## Phase 0 -- Research

See [research.md](./research.md). Key decisions:
- Reuse the `pbir.py` structural pattern (json.load, Finding with a
  `file#/pointer` locator, `is_test_path` exemption).
- Discover theme files generically from the committed file set by a theme-file
  naming pattern (never an enumerated list).
- The forbidden-key vocabulary is a module-level constant DERIVED FROM the generic
  contract categories; its exact literal members are the OPEN human ruling and are
  represented as a clearly-marked seam pending that ruling.

## Phase 1 -- Design

See [data-model.md](./data-model.md), [contracts/rule-contract.md](./contracts/rule-contract.md),
and [quickstart.md](./quickstart.md).

**Constitution re-check after design**: no new violations introduced. The design
keeps the vocabulary as a single generic constant, keeps the scan categorical, and
keeps the human-ruling boundary as a documented seam -- consistent with Principles
V, VII, VIII and ratified 044.

## Phase 2 -- Tasks

Generated by `/speckit-tasks` into [tasks.md](./tasks.md). Task ordering follows
TDD (fixtures + failing tests first, then the rule, then the five-place wiring,
then regenerate the golden records, then the full wiring/gate check).

## Complexity Tracking

Not applicable -- Constitution Check has no violations.
