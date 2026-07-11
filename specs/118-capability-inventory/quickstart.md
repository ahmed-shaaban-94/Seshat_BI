# Quickstart: Capability Inventory

A read-only, truthful inventory of what the Seshat BI kit can do -- grouped by state, with
a stable machine form. It is a SKILL (no CLI verb), grants no readiness, writes nothing,
opens no DB, runs no Power BI, and emits no score.

## Use it

Invoke the `capabilities` skill (the Option-B surface). It instructs the agent to run the
read-only builder's module entry point, which prints the grouped human inventory by
default, or the stable machine (JSON) form on request:

```text
# grouped human read (default)
python -m retail.capability_inventory
  -> Available now / Requires DB-or-extra / Agent-companion / Human-gated / Deferred

# machine form (agent routing)
python -m retail.capability_inventory --format json
  -> deterministic JSON array, one closed-field record per capability, each with its `group`
```

There is NO `seshat capabilities` / `retail capabilities` CLI verb -- that would reopen a
ratified decision (`docs/roadmap/decisions/cli-verbs-vs-skill-driven.md`). The builder is a
`python -m` MODULE entry point (invisible to `seshat --help`), not a `_DISPATCH` subcommand,
so it grows no CLI verb surface. Discoverability ships as a skill, matching specs 110-113.

## How to trust it

- Every listed capability is declared in the committed manifest `docs/capabilities/capabilities.yaml`
  and traces to a committed feeder for any referenced fact. A file merely existing on disk
  is NOT a capability.
- `state: shipped` is FAIL-CLOSED: a capability is `shipped` only when a committed feeder
  positively records it (roadmap SHIPPED / `status-claims` built / a wired command / a
  frontmatter'd `SKILL.md`). A spec-only item can never render as shipped.
- `provenance: publicly-released` is FAIL-CLOSED too: draft / locally-verified work is never
  shown as publicly released.
- The `tests/unit/test_capability_inventory.py` oracle fails CI if the manifest drifts
  (orphan entry, unlisted real capability, false-shipped, false-released, feeder
  disagreement) -- so a rename or removal cannot silently make the inventory stale.

## How it differs from the four authorities (FR-017)

| Surface | Question it answers |
|---------|--------------------|
| **capabilities** (this) | What can the KIT do -- shipped / advisory / human-gated / deferred, and how to reach each. |
| `retail check` | Does the committed text pass the governance gate? (non-zero exit is the contract) |
| `seshat status` | What is the readiness STATE of each onboarded table? |
| `seshat next` | What is the single next allowed ACTION for a table? |
| `seshat doctor` | Where has the repo DRIFTED from its own governance? |

`capabilities` is about the tool's feature surface; the others are about a table's readiness
or the repo's health. `capabilities` defers to all four for their questions and changes
none of their behavior.

## Verify (before merge)

```text
ruff format --check src tests
ruff check src tests
pytest -m unit -x -q tests/unit/test_capability_inventory.py
python -m retail.capability_inventory --format json   # renders; must be byte-identical on rerun
retail check          # unchanged: this feature adds NO rule and NO gate
seshat --help         # unchanged: NO `capabilities` verb appears
```
