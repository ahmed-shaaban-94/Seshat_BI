# Quickstart: Public Extension-Pack Catalog

How an agent or developer exercises `pack search` / `inspect` / `add` once
implemented. This is a walkthrough of the INTENDED usage, not an
implementation guide -- it assumes the shipped extension-pack system (spec
120, US5: `src/seshat/packs/model.py`, `loader.py`, `validator.py`,
`scaffold.py`) and this feature's registry (`packs/registry/index.yaml`,
`src/seshat/packs/registry.py`, `src/seshat/packs/catalog.py`) already exist.
All pack ids below are the generic, synthetic reference packs seeded in
`packs/registry/index.yaml` (Principle VII: no client-specific content).

## 0. Preconditions

- The reviewed static registry `packs/registry/index.yaml` is tracked
  repository text; no database, network, or hosted service is required.
- The pack `scaffold` and `validate` subcommands are unchanged (RR-006); this
  quickstart only exercises the three NEW subcommands.

## 1. Search the reviewed registry

```
retail pack search --repo . --query kpi
retail pack search --repo . --category dashboard_blueprint
```

- Every match shows id, version, category, author, compatibility, and
  verification state (FR-005). No content is fetched (SC-001) -- deleting
  every pack source directory would not change a `search` result at all.
- `retail pack search --repo . --query no-such-keyword` returns an empty
  result set with a plain "no matches" line and exit code `0`: an empty
  result is a normal outcome, never a failure (US1 scenario 3).
- `seshat.registry.dashboard-starter-basic` is seeded `unreviewed` on
  purpose: its verification state is shown plainly, never presented as
  reviewed (FR-016, US1 scenario 4).

## 2. Inspect one record before deciding to fetch anything

```
retail pack inspect --repo . seshat.reference.kpi-basic
```

- Shows the complete record: id, version, category, author, source,
  compatibility, hash, dependencies, conflicts, and verification state
  (FR-006). Still fetches nothing.
- `retail pack inspect --repo . does.not.exist` reports `not found` and
  exits `1` -- it does not attempt any retrieval (US2 scenario 4).

## 3. Add a clean, reviewed pack

```
retail pack add --repo . seshat.reference.kpi-basic
```

- The catalog fetches the pack directory named by the registry record's
  `source`, confirms the computed SHA-256 digest matches the
  registry-recorded `hash`, confirms the content is schema-valid against the
  UNCHANGED `schemas/seshat-extension-pack.schema.json`, runs the EXISTING
  `validate_pack` + `validate_selection` (RR-001/RR-002), and -- only on
  all-pass -- writes the verified pack under `packs/added/kpi-basic/` as new,
  reviewable file content (a plain `git status` shows it as untracked/new).
- Nothing is activated: no readiness stage advanced, no approval was
  granted, and no hidden "installed packs" state exists anywhere in the repo
  (FR-011..FR-013, SC-006). The added pack is inert until an operator
  explicitly selects it for a projection, exactly like a scaffolded pack.
- Running `retail pack validate --repo . --pack packs/added/kpi-basic/seshat-pack.yaml`
  afterward confirms the added content still passes the SAME validation that
  gated the add -- no second verdict-producing engine exists.

## 4. Tamper refusal

Mutate any file inside a pack's source directory (for example append a line
to `packs/reference/kpi-basic/artifacts/net-sales-template.yaml`) so the
computed digest no longer matches the registry-recorded `hash`, then re-run:

```
retail pack add --repo . seshat.reference.kpi-basic
```

- The catalog refuses, reports a `pack_catalog_tamper` finding naming the
  pack, and adds nothing to the workspace (SC-003, US3 scenario 2). Restore
  the file afterward -- this step is illustrative, not a permanent edit.

## 5. Incompatible-core refusal

A registry record whose `compatibility` does not match this core's
supported contract line (`CORE_CONTRACT_MAJOR`, currently `1.x`) is refused
the same way, before any content validation runs:

```
retail pack add --repo . <a pack id whose registry record declares compatibility: "9.x">
```

- The catalog refuses with a `pack_incompatible_core` finding and adds
  nothing (SC-004, US3 scenario 3).

## 6. Confirm no live surface is touched

None of the steps above require a database connection, a Power BI Desktop
session, or network access. `pack search`, `pack inspect`, and `pack add`
all run deterministically from committed repository text alone (Principle
VIII, FR-001, SC-009) -- directly observable by disabling networking and
re-running every command above.

## 7. Confirm the categorical-only output (hard rule #9)

At every step above, `verification_state` is always one of `reviewed` /
`unreviewed` / `deprecated` -- never a number, percentage, or rank anywhere
in `search`, `inspect`, or `add` output (SC-008). The registry's `author`
field is shown alongside the pack's own manifest `owner` field without ever
being conflated with it (FR-017, SC-007).

## 8. What this quickstart does NOT cover (explicitly deferred)

- **A hosted marketplace or dynamic index.** v1 is a static, reviewed git
  registry only (Out of Scope; Principle VIII).
- **Automatic dependency resolution.** `add` surfaces a declared dependency
  via the existing selection validation and refuses until the dependency is
  added first, explicitly, by the operator -- it never silently fetches a
  transitive pack (Out of Scope, US3 scenario 7).
- **Any activation/enablement lifecycle.** There is no "installed packs"
  state to inspect because none is ever written (Out of Scope).
