# Implementation Plan: Live-Surface Import Boundary Guard (B3)

**Branch**: `048-live-surface-import-boundary-guard` | **Date**: 2026-06-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/048-live-surface-import-boundary-guard/spec.md`

## Summary

Add ONE static rule that fails closed (ERROR) on a module-scope import of a
connection-capable library in any of the live-surface modules
(`validate.py`, `value_proxy.py`, `semantic.py`, `dax_gen.py`). The rule reuses
the EXISTING `module_scope_violations` AST helper and forbidden-root sets from
`src/retail/rules/never_execute.py` UNCHANGED -- the only difference from B1 is
the module set scanned (a live-surface set, disjoint from B1's static-core set).
It parses source text with stdlib `ast` and never imports or executes the scanned
modules. Registering the rule also updates the wiring test's expected id set and
regenerates `docs/rules/rules-manifest.json`, and a test exercises the rule
firing on a known-bad fixture (closing the prior wiring-latent-gap). It is the
static import-boundary sibling of the shipped runtime test in
`specs/044-live-surface-protocol/`.

## Technical Context

**Language/Version**: Python 3.11+ (matches the existing `src/retail` package and
`tests/unit` suite).

**Primary Dependencies**: standard library only (`ast`). No new runtime or test
dependency. The rule imports `retail.core` (`Finding`, `RuleContext`,
`Severity`), `retail.registry` (`register`), and the already-present
`module_scope_violations` / forbidden-root sets from
`retail.rules.never_execute`.

**Storage**: N/A. The rule reads tracked source files as text via the existing
`RuleContext` (`repo_root`, `tracked_files`); it opens no database and holds no
connection.

**Testing**: pytest, marked `pytest.mark.unit`. New unit tests for the rule plus
the existing rule-registry snapshot / wiring tests
(`tests/unit/test_rules_wiring.py`), run with psycopg2 absent.

**Target Platform**: Local dev + CI (Windows-first per repo `CLAUDE.md`;
platform-agnostic Python).

**Project Type**: Single project (library + CLI under `src/retail`, tests under
`tests/`).

**Performance Goals**: N/A (a handful of `ast.parse` calls over a fixed, small
module set during the static gate).

**Constraints**: stdlib-only, opens no network connection, imports no DB driver,
requires no credentials. ASCII / UTF-8 without BOM. Generic module paths and
synthetic source fixtures only -- no domain-specific schema artifact.

**Scale/Scope**: One rule registration + one explicit live-surface module-set
constant + the wiring-test id-set update + the regenerated manifest + new unit
tests. No production behavior of the scanned modules changes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle II (Depend, Never Fork)**: PASS. The rule reuses the existing
  `module_scope_violations` helper and forbidden-root / forbidden-dotted sets
  unchanged; it does NOT fork a parallel parser or forbidden-library list.
- **Principle VIII (Static-First Governance, Live Deferred)**: PASS. The guard is
  part of the stdlib-only, CI-able static core; it parses-not-imports and never
  executes a scanned module. It enforces the principle's own stated invariant
  (the live surface's driver imports stay lazy) structurally.
- **Severity asymmetry (constitution lines 401-403)**: PASS with a recorded
  judgment. The rule emits ERROR (clarified 2026-06-30), matching sibling B1: a
  module-scope driver import in a driver-free module is a proven invariant breach
  with no legitimate "override when" case, not a suspect pattern. It adds no new
  `Severity` tier.
- **Principle VII (C086 is an example, not the schema)**: PASS. The live-surface
  set is generic module paths; the forbidden roots are libraries; every fixture
  is a synthetic source snippet -- no table / column / KPI is referenced.
- **Anti-fabricated-confidence (constitution line 462)**: PASS. The rule emits
  Findings only; it produces no readiness/confidence number and moves no stage.
- **Principle IX (Reproducibility / Windows-safe)**: PASS. Pure-Python,
  deterministic, ASCII / UTF-8 no BOM, short paths.
- **Rule-registry integrity (043 snapshot + wiring test)**: PASS. Adding the rule
  updates `EXPECTED_RULE_IDS` AND regenerates the manifest in the same change; a
  test exercises the rule firing, not merely its registration (per the recorded
  wiring-latent-gap caveat). No numeric baseline count is hard-coded.
- **No executor / no deferred capability**: PASS. Pure static text rule; depends
  on no Power BI execution adapter (F016) or spec-only runtimes (F031-F033) and
  on no live database.

No violations. Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/048-live-surface-import-boundary-guard/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── rule-contract.md # Phase 1 output (the checkable rule contract)
├── checklists/
│   └── requirements.md  # Spec quality checklist (from /speckit-specify)
├── spec.md              # Feature specification
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
src/retail/
├── core.py              # Finding, RuleContext, Severity   (READ ONLY -- imported)
├── registry.py          # register decorator               (READ ONLY -- used)
├── validate.py          # live surface                      (READ ONLY -- scanned)
├── value_proxy.py       # live surface                      (READ ONLY -- scanned)
├── semantic.py          # live surface                      (READ ONLY -- scanned)
├── dax_gen.py           # live surface                      (READ ONLY -- scanned)
└── rules/
    ├── never_execute.py # B1 + module_scope_violations helper + forbidden sets
    │                     #   (the helper/sets are IMPORTED and reused unchanged;
    │                     #    whether the new rule lives here or in a sibling
    │                     #    module is a Phase-0 decision)
    └── live_surface_boundary.py   # CANDIDATE new sibling module for the rule
                                    #   (alternative: add the rule into
                                    #    never_execute.py next to B1)

docs/rules/
└── rules-manifest.json  # regenerated via `retail manifest`

tests/unit/
├── test_rules_wiring.py # EXPECTED_RULE_IDS updated with the new id
└── test_live_surface_boundary.py  # NEW -- direct firing tests for the rule
```

**Structure Decision**: Single-project layout. The feature adds exactly one
registered rule plus its tests, updates the wiring-test id set, and regenerates
the manifest. It changes NO behavior of the four scanned modules. The choice of
WHERE the rule lives (a new `live_surface_boundary.py` sibling vs. an added
`@register` function inside `never_execute.py`) is resolved in research.md; both
import the same shared helper, so neither forks the parser.

## Phase 0 -- Research (research.md)

Resolve and record (all grounded against the repo; no open technical unknowns):

1. The exact reusable surface of `never_execute.py`: `module_scope_violations`,
   `_FORBIDDEN_ROOTS`, `_FORBIDDEN_DOTTED`, `_is_forbidden`, and the
   SyntaxError-to-Finding pattern -- confirm they are importable and behave as
   B1 uses them.
2. Module placement decision: new sibling module vs. second `@register` in
   `never_execute.py` (decision + rationale + rejected alternative).
3. The registration / wiring contract: how `EXPECTED_RULE_IDS` keys off its own
   length (never a literal count), and how `retail manifest` regenerates
   `docs/rules/rules-manifest.json` guarded by the 043 snapshot test.
4. The recorded wiring-latent-gap: the new rule must be exercised firing on a
   known-bad fixture, not merely listed -- record the test obligation.
5. The live-surface module set: an explicit constant of repo-relative POSIX
   paths, disjoint from B1's `_GOVERNED_MODULES` / `_GOVERNED_PREFIX`.

## Phase 1 -- Design

- **data-model.md**: Describe the live-surface module-set constant (entity), the
  reused forbidden-root sets (referenced, not redefined), the registration record
  (id + title), and the Finding shape emitted per violation.
- **contracts/rule-contract.md**: Restate the asserted rule contract as a
  checkable list -- (a) module-scope forbidden import in a live-surface module ->
  exactly one ERROR Finding per offending name with that module's locator; (b)
  lazy / `TYPE_CHECKING` import -> no Finding; (c) module-scope `try`/`if`
  forbidden import -> flagged; (d) unparseable module -> ERROR Finding (fail
  loud); (e) `urllib.parse` -> never flagged; (f) registry id set + regenerated
  manifest + a firing test all agree; (g) no new `Severity`; (h) no
  domain-specific artifact anywhere.
- **quickstart.md**: How to run the rule's tests and the snapshot/wiring tests,
  what each proves, and how to regenerate the manifest.

### Post-Design Constitution Re-Check

Unchanged from above -- the design adds one rule, its tests, the id-set update,
and the regenerated manifest; it reuses the shared AST helper and introduces no
new violation, dependency, executor, or severity tier.

## Complexity Tracking

No constitution violations. Section intentionally empty.
