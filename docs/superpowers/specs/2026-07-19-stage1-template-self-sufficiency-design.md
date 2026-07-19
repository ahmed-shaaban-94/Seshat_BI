# Design: Stage-1 template self-sufficiency (issue #339)

**Date:** 2026-07-19
**Issue:** [#339](https://github.com/Kemetra/Seshat-BI/issues/339) — *Stage-1
onboarding templates ship only with the dev repo; pip users + init-project have
nothing to copy* (`enhancement`)
**Class:** Stage-1 instance of the #325 self-sufficiency class — the pip package
ships the engine/reader but not the blank artifacts it reads.

## Problem

A user who installs via `pipx install seshat-bi` — or scaffolds a workspace with
`retail init-project` — has **no `templates/` directory and no command to obtain
one**, yet the first governed action (Source Ready / Stage 1) requires authoring
a *template-conformant* `source-profile.md` and `readiness-status.yaml`.

The blank Stage-1 templates live only at `<dev-repo>/templates/*`. They are
absent from the pip wheel and from `init-project` output. This violates
`portable-operating-contract.md`: *"Never require the Seshat development
repository for normal use."*

Confirmed against v0.5.0:
- `seshat/source_profile_reader.py` parses a *template-conformant*
  `source-profile.md` (Header `Table id`, Shape `Row count`, a `Per-column
  profile` pipe table, a PK proof block).
- `seshat/capability_feeders.py` reads `templates/readiness-status.yaml`.
- Rules reference `templates/source-map.yaml` as the blank copy-me template.

## Settled mechanism (not an open question)

Issue #325 already established the exact pattern on `main`
(`src/seshat/governed_projects.py` + `pyproject.toml` force-include/sdist-mirror).
This design **mirrors it** for the three Stage-1 templates. The bundling
mechanism is not re-derived here.

## Scope (YAGNI)

Exactly the **three** templates the issue names:
- `templates/source-profile.md`
- `templates/readiness-status.yaml`
- `templates/source-map.yaml`

Not the other ~60 templates. No wizard, no stdin prompting (matches the
`init-project` / `retail init` non-interactive posture). Non-destructive only.

Table-neutrality (constitution VII) is satisfied: verified per-file that all
three are genuinely blank (35 / 16 / 49 placeholder markers respectively). Their
`C086` mentions are pedagogical comments that explicitly say *"C086 IS A FILLED
INSTANCE, NEVER THE SCHEMA"* — no filled worked-example rows are baked in.

## Architecture

Three moving parts, following `governed_projects.py`:

### 1. Bundle as wheel package data

Add to `[tool.hatch.build.targets.wheel.force-include]`:

```
"templates/source-profile.md"    = "seshat/stage1_templates/source-profile.md"
"templates/readiness-status.yaml"= "seshat/stage1_templates/readiness-status.yaml"
"templates/source-map.yaml"      = "seshat/stage1_templates/source-map.yaml"
```

Mirror the same three paths into `[tool.hatch.build.targets.sdist].include`
(the wheel is built from the sdist, so the sdist must carry them).

### 2. New module `src/seshat/stage1_scaffold.py`

Reuses the two-tier resolver idiom from `governed_projects.py`:
`importlib.resources.files("seshat").joinpath("stage1_templates", ...)` for the
wheel path, falling back to `_SOURCE_ROOT / "templates" / ...` for a development
checkout. Raises a clear `FileNotFoundError` ("reinstall seshat-bi, or run from a
development checkout") if neither resolves.

Public surface:

```python
def scaffold_source(repo_root: Path, table: str) -> InitReport
```

- Writes `mappings/<table>/source-profile.md`, `.../readiness-status.yaml`,
  `.../source-map.yaml`.
- **Non-destructive** per-file (`_write_if_absent` posture): an existing file is
  always kept, never overwritten.
- Returns a `written / kept / notes` report (reuse or mirror
  `governed_projects.InitReport`).
- Validates `table` as a safe path segment (no traversal, no separators) —
  reuses the `init-project` outside-CWD guard reasoning.

The `source-profile.md` bytes get the one broken relative link
(`../docs/decisions/0003-mapping-artifact-location.md` — dev-repo lore a user
workspace does not have) neutralized on materialization, so the stub is
self-contained.

### 3. New CLI verb `seshat scaffold-source <table>`

- Handler in `src/seshat/cli/commands/scaffold_source.py`, lazy-importing
  `seshat.stage1_scaffold` (keeps the stdlib-only `check` core import chain
  clean, B1).
- Parser wiring in `src/seshat/cli/parser.py` (positional `table`).
- Prints each written / kept path and a next-step pointer
  (*"fill the profile, then `seshat next`"*).

### 4. Pointer in `seshat next`

`agent_next.py`'s Source-Ready guidance mentions `scaffold-source` so a user who
runs `seshat next` on an empty workspace learns the command exists.

## Correctness constraints (BLOCKING)

1. **Release-gate coverage (closes the gap #325 left).** Add the three assets to
   `_REQUIRED_WHEEL_PACKAGE_DATA` in `scripts/inspect_release_artifacts.py`. If
   the force-include is ever dropped, the release gate fails loud with
   `ArtifactInspectionError` — instead of silently reintroducing #339's exact
   bug. #325 did **not** add its bundled files to this gate; this design closes
   that gap for the Stage-1 three.

2. **Degrade to "unstarted," not "malformed."** The scaffolded blank
   `readiness-status.yaml` MUST make `seshat next` read the table as an
   *unstarted Source-Ready journey* — it must not trip the "repair the malformed
   readiness-status.yaml" path (`agent_next.py` / `run_next.py`) and must not
   hard-fail `seshat check`. This is the same class of constraint `workspace_init`
   handles by deliberately not writing `.seshat/`. Verified end-to-end.

## Testing (TDD — tests first)

- `tests/unit/test_stage1_scaffold.py` (mirrors `test_governed_projects.py`):
  writes the three files; non-destructive re-run keeps existing; dev-checkout
  fallback resolves; bad `table` rejected; report is correct.
- Extend `tests/contract/test_release_artifact_contents.py`: the three assets
  are required wheel inventory; dropping one raises `ArtifactInspectionError`.
- `tests/unit/test_cli_scaffold_source.py`: the verb wires up, prints
  written/kept, and returns exit 0 / non-zero on refusal.
- **End-to-end degrade test:** `scaffold_source(root, "foo")` → `run_next` /
  `agent_next` yields Source-Ready guidance (not the malformed-repair path); a
  `seshat check` over the scaffolded workspace stays clean.

## Files touched

| File | Change |
|------|--------|
| `pyproject.toml` | +3 wheel force-include, +3 sdist include |
| `src/seshat/stage1_scaffold.py` | **new** — resolver + `scaffold_source` |
| `src/seshat/cli/commands/scaffold_source.py` | **new** — verb handler |
| `src/seshat/cli/parser.py` | wire `scaffold-source <table>` |
| `src/seshat/agent_next.py` | mention `scaffold-source` in Source-Ready guidance |
| `scripts/inspect_release_artifacts.py` | +3 to `_REQUIRED_WHEEL_PACKAGE_DATA` |
| `tests/unit/test_stage1_scaffold.py` | **new** |
| `tests/unit/test_cli_scaffold_source.py` | **new** |
| `tests/contract/test_release_artifact_contents.py` | +required-inventory case |
| `CHANGELOG.md` | unreleased entry |

## Non-goals

- Bundling all ~60 templates.
- An interactive wizard / stdin prompting.
- Overwriting existing user files.
- Any DB or network access (the scaffolder is pure `pathlib` + `importlib.resources`).
