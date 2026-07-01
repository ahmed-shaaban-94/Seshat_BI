# Quickstart: Wiring Meta-Gate

## Run it

```bash
pytest -m unit tests/unit/test_wiring_meta_gate.py
```

It runs in the same unit lane as the existing wiring/snapshot tests. No
arguments, no environment setup, no database/network.

## What it proves

In one lockstep pass it proves the five rule-registry wiring places agree with
the live registry (the ground truth) and closes the one un-guarded seam:

1. package import list == public export list == on-disk submodule set;
2. live registry ids == expected-rule-id set (catches the G6 omission-symmetry class);
3. golden manifest `{id,title}` == live registry;
4. every live rule id appears in the golden posture record;
5. every non-registered posture surface is on the explicit ADR-0007 exemption list.

Plus vacuity and duplicate-id guards.

## Reproduce each fail-closed case (for reviewers)

Each of these should turn the test RED; revert to return it GREEN.

- **Package symmetry (C1)**: remove one name from the package export list while
  leaving it in the import list -> fails naming the export-list omission.
- **Orphan submodule (C1)**: drop a new empty submodule file into the rules
  package without wiring it -> fails naming the orphan.
- **G6 class (C2)**: remove one id from the expected-rule-id set -> fails with
  `missing=` naming that id.
- **Stale manifest (C3)**: hand-edit the golden manifest to drop or retitle a rule
  -> fails naming the manifest place and the id.
- **Stale posture (C4)**: hand-edit the golden posture record to drop a registered
  rule -> fails naming the posture place and the id.
- **New non-registered surface (C5)**: add a non-registered surface key to the
  posture golden not on the exemption list -> fails naming the un-exempted key.

## Known-good state

With the repo unmodified (40 registered ids, 16 on-disk submodules, one
ADR-0007 non-registered surface), the meta-gate PASSES with zero false failures.
