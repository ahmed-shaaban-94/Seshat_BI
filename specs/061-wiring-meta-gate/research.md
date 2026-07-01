# Phase 0 Research: Wiring Meta-Gate

## Decision 1: Ground truth = deterministically re-loaded live registry

- **Decision**: The meta-gate re-loads the rule registry with the same
  clear-and-reload technique the existing wiring test uses (clear the registry
  list, then reload every submodule via package introspection so each
  registration decorator fires once), and treats the resulting id+title set as the
  ground truth.
- **Rationale**: Sibling tests mutate global registry state (one clears the
  registry in an autouse fixture); reading `all_rules()` without a forced reload
  would make the meta-gate order-dependent and flaky. The existing
  `test_registered_rule_ids_match_expected_set` already proves this technique is
  correct and CI-stable.
- **Alternatives considered**: (a) read `all_rules()` as-is -- rejected, flaky
  under cross-test state; (b) subprocess a fresh interpreter -- rejected,
  introduces a process dependency for no benefit over an in-process reload.

## Decision 2: Static read of the two golden JSON files

- **Decision**: For the manifest and posture cross-checks, read the committed
  golden files (`docs/rules/rules-manifest.json`,
  `docs/rules/severity-posture.json`) statically and compare their ids against the
  live registry ids; do NOT re-generate or re-observe.
- **Rationale**: The existing snapshot tests already assert live == committed for
  each golden file, so re-generating here duplicates work. Re-observing posture
  shells out to a version-control subprocess over a throwaway temp directory;
  reading the committed file statically keeps the meta-gate purely static
  (Principle VIII) and cheap. The meta-gate's distinct job is cross-consistency
  between places, which static reads fully serve.
- **Alternatives considered**: (a) re-run `build_manifest(all_rules())` and
  re-observe posture inline -- rejected, inherits the subprocess dependency and
  duplicates the snapshot tests; (b) parse the golden files with a third-party
  schema lib -- rejected, stdlib `json` suffices and adds no dependency.

## Decision 3: The package-symmetry seam (the genuinely-new coverage)

- **Decision**: Assert three sets are exactly equal: the names in the package's
  side-effecting import list, the names in its public export list (`__all__`), and
  the on-disk submodule set discovered via package introspection (excluding the
  package initializer). Any name in one but not the others is a fail-closed with
  the symbol and the list it is missing from named.
- **Rationale**: This is the one place with no existing assertion. The existing
  wiring test iterates the on-disk submodules dynamically but never compares them
  to `__all__` or the import list, so the export list can rot independently.
  Reading the import list and `__all__` from the imported package object is
  stdlib-only (`__all__` is a plain attribute; the import list is discoverable by
  comparing imported submodule attributes against the on-disk set).
- **Alternatives considered**: (a) parse `__init__.py` source text with a regex --
  rejected, brittle and re-implements the import system; (b) compare only import
  list vs on-disk (skip `__all__`) -- rejected, leaves the export list unguarded,
  which is exactly the gap. Reading `__all__` as an attribute and the imported
  submodules as attributes of the package, both against the pkgutil on-disk set,
  is the robust stdlib approach.

## Decision 4: ADR-0007 non-registered-surface exemption is explicit

- **Decision**: Encode an explicit constant exemption set naming the one known
  non-registered governance surface (the L3 verdict-to-finding surface recorded in
  the posture golden). The posture cross-check must accept that surface without a
  rule id; any non-registered posture surface NOT on the exemption list is a
  fail-closed.
- **Rationale**: An implicit "ignore anything without a rule id" would let a new,
  un-vetted non-registered surface enter silently -- defeating the gate. A new
  non-registered surface is a deliberate governance decision and must force an
  explicit update to the exemption list (a fail-closed prompt to the author).
- **Alternatives considered**: (a) implicit ignore -- rejected as above; (b)
  require every posture surface to have a rule id -- rejected, produces a false
  failure on the known-good repo state (violates SC-003).

## Decision 5: ADD, not REPLACE

- **Decision**: Keep the three/four existing standalone wiring tests; the
  meta-gate is a new cross-referencing check that sits beside them.
- **Rationale**: Deleting working fail-closed guards in the same change that adds
  a new one increases risk and loses per-place failure locality. Consolidation, if
  ever wanted, is a separate follow-on and is explicitly out of scope here.
- **Alternatives considered**: REPLACE/subsume -- deferred; reversible later.

## Decision 6: Vacuous-state and duplicate-id guards

- **Decision**: Fail closed if zero submodules or zero rules are discovered, and
  fail closed if the registry tuple length differs from the unique-id count.
- **Rationale**: A green run over zero rules is the omission-symmetry trap in its
  purest form; duplicate registration is a real wiring error the count check
  catches cheaply.
- **Alternatives considered**: skip these guards -- rejected, they are the exact
  silent-pass failure modes the feature exists to prevent.

## Non-Goals (confirmed)

- No new registered rule, no new expected-rule-id, no new persisted golden file.
- No live/executing behavior of any kind.
- No dependency on any deferred capability (Power BI execution adapter or
  spec-only runtimes); the meta-gate is fully satisfiable with today's static
  seams.
