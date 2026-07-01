# Contract: Wiring Meta-Gate

The meta-gate is a unit-test module. Its "contract" is the set of assertions it
makes and the shape of its fail-closed output. It exposes no public API and adds
no CLI surface, no registered rule, and no new golden file.

## Invocation

- Runs in the existing unit lane: `pytest -m unit tests/unit/test_wiring_meta_gate.py`.
- No arguments, no environment variables, no network/DB/subprocess.
- Reads: the in-process registry (after deterministic reload), the rules package
  object (`__all__` + imported submodules), and two committed golden JSON files.

## Assertions (all fail closed / non-zero on violation)

| ID | Assertion | Failure message MUST name |
|----|-----------|---------------------------|
| A-C1a | on-disk submodule set == package import-list names | the differing submodule(s) + which side |
| A-C1b | on-disk submodule set == `__all__` names | the differing name(s) + `__all__` vs import/on-disk |
| A-C2 | live registry ids == expected-rule-id set | `missing=` and `unexpected=` id sets |
| A-C3 | manifest golden `{id,title}` == live `{id,title}` | added/removed/retitled id(s) + `manifest` |
| A-C4 | every live id present in posture golden `registered` | absent id(s) + `posture` |
| A-C5 | every non-registered posture surface key is exempted | the un-exempted surface key |
| A-C6 | submodule count > 0 AND rule count > 0 | which count is zero (vacuity trap) |
| A-C7 | `len(all_rules()) == len({ids})` | the duplicated id(s) |

## Fail-closed guarantees

- No assertion is advisory: each is a hard `assert` / raised failure that makes
  the test (and thus the CI gate and pre-commit gate) exit non-zero. There is no
  warning-only mode (FR-007).
- A vacuous state (zero submodules or zero rules) FAILS; it never passes silently
  (FR-008, A-C6).
- Duplicate registration FAILS (FR-009, A-C7).

## Non-registered-surface exemption

- The exemption list is an explicit in-test constant. Today it contains exactly
  the one L3 verdict-to-finding surface key recorded in the posture golden (per
  ADR-0007).
- A-C5 passes iff every non-registered key in the posture golden is on this list.
- Adding a NEW non-registered surface REQUIRES a deliberate edit to the exemption
  constant; until then the gate fails closed (this is intended).

## Determinism & portability (Principle IX)

- All comparisons are on parsed/normalized content (sets, dicts), never raw bytes.
- Golden JSON is read as UTF-8 without BOM.
- Paths are derived from the package location relative to the repo root;
  MAX_PATH-safe, no hardcoded absolute paths.

## Explicit non-contract

- Does NOT register a rule; does NOT appear in the registry, the expected-rule-id
  set, the manifest, or the posture record.
- Does NOT re-generate or re-observe the golden files (reads them statically).
- Does NOT execute any query, DAX, agent, database, or network call.
- Does NOT delete or modify the existing per-place tests (ADD, not REPLACE).
- Carries zero example-domain identifiers.
