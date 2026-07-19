# Stage-1 Template Self-Sufficiency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the three Stage-1 blank templates as wheel package data and add a `seshat scaffold-source <table>` verb, so a pip-only user can produce the first required Source-Ready artifact without the dev repo (issue #339).

**Architecture:** Mirror the settled #325 pattern (`src/seshat/governed_projects.py` + `pyproject.toml` force-include / sdist-mirror). A new `src/seshat/stage1_scaffold.py` reuses the two-tier resource resolver (wheel `importlib.resources` first, dev-checkout fallback) to write `mappings/<table>/{source-profile.md, readiness-status.yaml, source-map.yaml}` non-destructively. A new CLI verb wires it in; `agent_next.py` mentions the verb; the release-artifact gate requires the three assets in the wheel.

**Tech Stack:** Python 3.13, stdlib only (`pathlib`, `importlib.resources`, `argparse`), hatchling build backend, pytest.

## Global Constraints

- **Python floor:** `>=3.13` (pyproject). Use `from __future__ import annotations`.
- **Stdlib-only core (B1/B3):** no third-party import at module scope in `stage1_scaffold.py` or the command handler; the CLI handler lazy-imports `seshat.stage1_scaffold` at call time (mirror every other `commands/*.py`).
- **Constitution VII (table-neutral only):** bundle ONLY the three named blank templates. Never bundle filled worked-example content.
- **Non-destructive:** an existing target file is always kept, never overwritten (mirror `governed_projects._write_if_absent`).
- **Line endings:** write files UTF-8 without BOM. Template bytes are copied verbatim (they are `.md`/`.yaml` text already committed with the repo's `.gitattributes` eol rules); do not re-encode.
- **No DB, no network, no stdin prompt** (matches `init-project` posture).
- **Scope:** exactly `source-profile.md`, `readiness-status.yaml`, `source-map.yaml`. Not the other ~60 templates. No wizard.

---

### Task 1: The scaffolder module (`stage1_scaffold.py`)

**Files:**
- Create: `src/seshat/stage1_scaffold.py`
- Test: `tests/unit/test_stage1_scaffold.py`

**Interfaces:**
- Consumes: nothing (leaf module).
- Produces:
  - `Stage1Report` — a frozen dataclass with `written: tuple[str, ...]`, `kept: tuple[str, ...]`, `notes: tuple[str, ...]`.
  - `scaffold_source(repo_root: Path, table: str) -> Stage1Report`.
  - `class Stage1ScaffoldError(ValueError)` — raised for an unsafe `table` segment.

**Design facts (verified against the repo):**
- The three blank templates live at repo-root `templates/{source-profile.md,readiness-status.yaml,source-map.yaml}` and are bundled (Task 4) at `seshat/stage1_templates/<name>`.
- Resolver mirrors `governed_projects.py`: `files("seshat").joinpath("stage1_templates", name)` first, then `_SOURCE_ROOT / "templates" / name` (dev checkout), where `_SOURCE_ROOT = Path(__file__).resolve().parents[2]`.
- `source-profile.md` line 4 contains a dev-repo relative link `[ADR 0003](../docs/decisions/0003-mapping-artifact-location.md)` that breaks when materialized under `mappings/<table>/`. Neutralize it: replace the markdown link `[ADR 0003](../docs/decisions/0003-mapping-artifact-location.md)` with the bare text `ADR 0003 (mapping-artifact-location)`. Only that substring; leave everything else byte-identical.
- Empirically verified: the blank `readiness-status.yaml` parses as a valid YAML mapping and `run_next` treats the scaffolded table as an unstarted Source-Ready journey (no input defect). So NO stub surgery is needed on the YAML — copy it verbatim.

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_stage1_scaffold.py
"""`seshat scaffold-source <table>` self-sufficiency (issue #339).

A bare workspace (no dev repo) must obtain the three Stage-1 blank templates
from bundled package data, written non-destructively into mappings/<table>/.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_STAGE1_FILES = (
    "source-profile.md",
    "readiness-status.yaml",
    "source-map.yaml",
)


def test_scaffold_source_writes_the_three_stage1_files(tmp_path: Path) -> None:
    from seshat.stage1_scaffold import scaffold_source

    report = scaffold_source(tmp_path, "sales_c086")

    for name in _STAGE1_FILES:
        target = tmp_path / "mappings" / "sales_c086" / name
        assert target.is_file()
        assert f"mappings/sales_c086/{name}" in report.written
    assert report.kept == ()


def test_scaffold_source_neutralizes_the_broken_adr_link(tmp_path: Path) -> None:
    from seshat.stage1_scaffold import scaffold_source

    scaffold_source(tmp_path, "foo")
    profile = (tmp_path / "mappings" / "foo" / "source-profile.md").read_text(
        encoding="utf-8"
    )
    assert "../docs/decisions/0003-mapping-artifact-location.md" not in profile
    assert "ADR 0003 (mapping-artifact-location)" in profile


def test_scaffold_source_is_non_destructive_and_idempotent(tmp_path: Path) -> None:
    from seshat.stage1_scaffold import scaffold_source

    scaffold_source(tmp_path, "foo")
    edited = tmp_path / "mappings" / "foo" / "source-map.yaml"
    edited.write_text("# hand-edited\n", encoding="utf-8")

    second = scaffold_source(tmp_path, "foo")

    assert "mappings/foo/source-map.yaml" in second.kept
    assert second.written == ()
    assert edited.read_text(encoding="utf-8") == "# hand-edited\n"


def test_scaffold_source_creates_mappings_dir_when_absent(tmp_path: Path) -> None:
    from seshat.stage1_scaffold import scaffold_source

    assert not (tmp_path / "mappings").exists()
    scaffold_source(tmp_path, "foo")
    assert (tmp_path / "mappings" / "foo").is_dir()


@pytest.mark.parametrize("bad", ["../evil", "a/b", "", ".", "..", "/abs"])
def test_scaffold_source_rejects_unsafe_table_segment(
    tmp_path: Path, bad: str
) -> None:
    from seshat.stage1_scaffold import Stage1ScaffoldError, scaffold_source

    with pytest.raises(Stage1ScaffoldError):
        scaffold_source(tmp_path, bad)


def test_scaffold_source_dev_checkout_fallback_resolves(tmp_path: Path) -> None:
    """No wheel data needed in the dev suite: the _SOURCE_ROOT fallback must
    find the repo-root templates/ so the three files still materialize."""
    from seshat.stage1_scaffold import scaffold_source

    report = scaffold_source(tmp_path, "foo")
    assert len(report.written) == 3
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/unit/test_stage1_scaffold.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'seshat.stage1_scaffold'`.

- [ ] **Step 3: Write the module**

```python
# src/seshat/stage1_scaffold.py
"""Materialize the three Stage-1 blank templates into any workspace (#339).

The first governed action (Source Ready / Stage 1) requires a
template-conformant ``source-profile.md`` plus a ``readiness-status.yaml`` and
``source-map.yaml``. Those blank templates previously shipped only with the
development repository, so a bare ``pip install seshat-bi`` left a new user
with nothing to copy -- violating the portable operating contract's "Never
require the Seshat development repository for normal use".

``scaffold_source`` closes that gap by writing the three blanks into
``mappings/<table>/`` from bundled package data (wheel force-include; a
development checkout falls back to the repo ``templates/`` dir, mirroring
``seshat.governed_projects``). Only table-neutral blank templates ship
(constitution VII). Writes are per-file non-destructive: an existing file is
always kept, never overwritten. Pure stdlib -- no DB, no network.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

_SOURCE_ROOT = Path(__file__).resolve().parents[2]
_PACKAGED_ROOT = "stage1_templates"

# The three Stage-1 blank templates (issue #339). Exactly these -- the other
# ~60 templates stay dev-only (YAGNI + constitution VII).
_STAGE1_FILES: tuple[str, ...] = (
    "source-profile.md",
    "readiness-status.yaml",
    "source-map.yaml",
)

# source-profile.md carries one dev-repo relative link that dangles once the
# file is materialized under mappings/<table>/. Neutralize to bare text so the
# stub is self-contained. (Everything else is copied byte-for-byte.)
_BROKEN_LINK = "[ADR 0003](../docs/decisions/0003-mapping-artifact-location.md)"
_LINK_REPLACEMENT = "ADR 0003 (mapping-artifact-location)"


class Stage1ScaffoldError(ValueError):
    """Raised when ``table`` is not a safe single path segment."""


@dataclass(frozen=True)
class Stage1Report:
    """What one ``scaffold_source`` call did, per file, plus operator notes."""

    written: tuple[str, ...]
    kept: tuple[str, ...]
    notes: tuple[str, ...]


def _validate_table(table: str) -> str:
    """A safe single path segment: no separators, no traversal, non-trivial."""
    if not table or table in {".", ".."} or "/" in table or "\\" in table:
        raise Stage1ScaffoldError(
            f"unsafe table segment: {table!r} "
            "(must be a plain name, no path separators or traversal)"
        )
    return table


def _template_bytes(name: str) -> bytes:
    """One bundled template's bytes: wheel data first, dev checkout fallback."""
    packaged = files("seshat").joinpath(_PACKAGED_ROOT, name)
    if packaged.is_file():
        return packaged.read_bytes()
    source = _SOURCE_ROOT / "templates" / name
    if source.is_file():
        return source.read_bytes()
    raise FileNotFoundError(
        f"bundled Stage-1 template is missing: {name} "
        "(reinstall seshat-bi, or run from a development checkout)"
    )


def _materialized_bytes(name: str) -> bytes:
    """Template bytes with per-file materialization fixups applied."""
    data = _template_bytes(name)
    if name == "source-profile.md":
        return data.replace(
            _BROKEN_LINK.encode("utf-8"), _LINK_REPLACEMENT.encode("utf-8")
        )
    return data


def _write_if_absent(target: Path, data: bytes) -> bool:
    """Write one file; True when written, False when kept as-is."""
    if target.exists():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return True


def scaffold_source(repo_root: Path, table: str) -> Stage1Report:
    """Write the three Stage-1 blank templates into ``mappings/<table>/``.

    ``table`` must be a plain path segment (raises ``Stage1ScaffoldError``
    otherwise). Per-file non-destructive: an existing file is kept, never
    overwritten. Returns a ``Stage1Report`` of what was written vs kept.
    """
    table = _validate_table(table)
    root = Path(repo_root).resolve()
    dest_dir = root / "mappings" / table
    written: list[str] = []
    kept: list[str] = []
    for name in _STAGE1_FILES:
        rel = f"mappings/{table}/{name}"
        if _write_if_absent(dest_dir / name, _materialized_bytes(name)):
            written.append(rel)
        else:
            kept.append(rel)
    notes = (
        f"fill mappings/{table}/source-profile.md (Table id, Row count, the "
        "Per-column profile table, the PK proof), then run `seshat next`",
    )
    return Stage1Report(written=tuple(written), kept=tuple(kept), notes=notes)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/unit/test_stage1_scaffold.py -v`
Expected: PASS (all 8 cases, incl. the 6 parametrized `bad` values).

- [ ] **Step 5: Commit**

```bash
git add src/seshat/stage1_scaffold.py tests/unit/test_stage1_scaffold.py
git commit -m "feat: stage1_scaffold materializes the three Source-Ready blanks (#339)"
```

---

### Task 2: The `scaffold-source` CLI verb

**Files:**
- Create: `src/seshat/cli/commands/scaffold_source.py`
- Modify: `src/seshat/cli/parser.py` (add `_add_scaffold_source_parser` + call it in `_build_parser` after `_add_init_project_parser(sub)`)
- Modify: `src/seshat/cli/__init__.py` (add one `_DISPATCH` entry)
- Test: `tests/unit/test_cli_scaffold_source.py`

**Interfaces:**
- Consumes: `seshat.stage1_scaffold.scaffold_source`, `Stage1ScaffoldError` (Task 1).
- Produces: `scaffold_source_main(args: argparse.Namespace) -> int` (dispatch handler; `args.table` and `args.repo`).

**Design facts:**
- Handlers are registered in `_DISPATCH` (`src/seshat/cli/__init__.py`, ~line 142) via `_lazy(".commands.<mod>", "<func>")` so the module imports at CALL time only.
- Parsers are added by `_add_*_parser(sub)` helpers, each called in order inside `_build_parser` (`src/seshat/cli/parser.py`, ~line 1070). Mirror `_add_init_project_parser` exactly.
- `main` looks up `_DISPATCH.get(args.command)` and calls `handler(args)`.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_cli_scaffold_source.py
"""`seshat scaffold-source <table>` CLI wiring (issue #339)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def test_cli_scaffold_source_writes_files_and_reports(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from seshat.cli import main

    rc = main(["scaffold-source", "sales_c086", "--repo", str(tmp_path)])

    assert rc == 0
    out = capsys.readouterr().out
    assert "wrote" in out
    assert "mappings/sales_c086/source-profile.md" in out
    assert (tmp_path / "mappings" / "sales_c086" / "source-map.yaml").is_file()


def test_cli_scaffold_source_reports_kept_on_rerun(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from seshat.cli import main

    main(["scaffold-source", "foo", "--repo", str(tmp_path)])
    capsys.readouterr()
    rc = main(["scaffold-source", "foo", "--repo", str(tmp_path)])

    assert rc == 0
    out = capsys.readouterr().out
    assert "kept" in out


def test_cli_scaffold_source_rejects_unsafe_table(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from seshat.cli import main

    rc = main(["scaffold-source", "../evil", "--repo", str(tmp_path)])

    assert rc == 1
    assert "refused" in capsys.readouterr().err
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/test_cli_scaffold_source.py -v`
Expected: FAIL — argparse exits with code 2 ("invalid choice: 'scaffold-source'") since the verb is unregistered.

- [ ] **Step 3: Write the handler**

```python
# src/seshat/cli/commands/scaffold_source.py
"""`seshat scaffold-source <table>` handler (issue #339): write the three
Stage-1 blank templates into ``mappings/<table>/`` so a pip-only user can
produce the first Source-Ready artifact without the development repository.

Lazy-imports ``seshat.stage1_scaffold`` (mirrors the other command handlers) to
keep the stdlib-only ``check`` core import chain unaffected (B1).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def scaffold_source_main(args: argparse.Namespace) -> int:
    """Materialize the Stage-1 blanks; per-file non-destructive.

    Returns 0 on success (including an all-kept re-run), 1 on an unsafe table
    segment (writes nothing).
    """
    from seshat.stage1_scaffold import Stage1ScaffoldError, scaffold_source

    try:
        report = scaffold_source(Path(args.repo), args.table)
    except Stage1ScaffoldError as exc:
        print(f"[refused] {exc}", file=sys.stderr)
        return 1

    for rel in report.written:
        print(f"wrote {rel}")
    for rel in report.kept:
        print(f"kept {rel} (already present; not overwritten)")
    for note in report.notes:
        print(f"\nnext: {note}")
    return 0
```

- [ ] **Step 4: Register the parser** — in `src/seshat/cli/parser.py`, add this helper immediately after `_add_init_project_parser` (ends ~line 62):

```python
def _add_scaffold_source_parser(sub: argparse._SubParsersAction) -> None:
    """`scaffold-source <table>` (issue #339): write the three Stage-1 blank
    templates (source-profile.md, readiness-status.yaml, source-map.yaml) into
    mappings/<table>/ from bundled package data, so a pip-only user has the
    Source-Ready artifacts to fill. Per-file non-destructive; no wizard.
    Extracted (mirrors `_add_init_project_parser`) to keep `_build_parser` from
    growing (CodeScene large-method guard)."""
    p = sub.add_parser(
        "scaffold-source",
        help=(
            "write the three Stage-1 blank templates (source-profile.md, "
            "readiness-status.yaml, source-map.yaml) into mappings/<table>/ "
            "so a fresh workspace has the Source-Ready artifacts to fill"
        ),
    )
    p.add_argument(
        "table",
        metavar="TABLE",
        help="table id / mapping folder name to scaffold under mappings/",
    )
    p.add_argument("--repo", default=".", help="repo root to scaffold into")
```

Then, in `_build_parser` (~line 1070), add the call immediately after `_add_init_project_parser(sub)`:

```python
    _add_init_project_parser(sub)
    _add_scaffold_source_parser(sub)
```

- [ ] **Step 5: Register the dispatch entry** — in `src/seshat/cli/__init__.py`, add to the `_DISPATCH` dict immediately after the `"init-project"` line:

```python
    "init-project": _lazy(".commands.init_project", "init_project_main"),
    "scaffold-source": _lazy(".commands.scaffold_source", "scaffold_source_main"),
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `python -m pytest tests/unit/test_cli_scaffold_source.py -v`
Expected: PASS (all 3 cases).

- [ ] **Step 7: Commit**

```bash
git add src/seshat/cli/commands/scaffold_source.py src/seshat/cli/parser.py src/seshat/cli/__init__.py tests/unit/test_cli_scaffold_source.py
git commit -m "feat: add `seshat scaffold-source <table>` verb (#339)"
```

---

### Task 3: End-to-end degrade contract (scaffold -> next -> unstarted)

**Files:**
- Test: `tests/unit/test_stage1_scaffold.py` (append to the file from Task 1)

**Interfaces:**
- Consumes: `seshat.stage1_scaffold.scaffold_source`, `seshat.run_next.build_run_next_response`.
- Produces: nothing (pure test).

**Design fact (empirically verified):** with the blank `readiness-status.yaml` in `mappings/<table>/`, `build_run_next_response(root, table)` returns `outcome == "next_action"`, `stage == "source_ready"` — an unstarted journey, NOT `input_defect`. This test locks that contract so a future template edit can't silently break it (the advisor's BLOCKING constraint #2).

- [ ] **Step 1: Write the failing test**

```python
# append to tests/unit/test_stage1_scaffold.py

def test_scaffolded_readiness_degrades_to_unstarted_not_malformed(
    tmp_path: Path,
) -> None:
    """The scaffolded blank readiness-status.yaml must read as an UNSTARTED
    Source-Ready journey (outcome=next_action, stage=source_ready), never an
    input_defect / malformed-repair path (issue #339, degrade contract)."""
    from seshat.run_next import build_run_next_response
    from seshat.stage1_scaffold import scaffold_source

    scaffold_source(tmp_path, "foo")
    resp = build_run_next_response(str(tmp_path), "foo")

    assert resp["outcome"] == "next_action"
    assert resp["stage"] == "source_ready"
    assert resp["read_only_proof"] is True
```

- [ ] **Step 2: Run test to verify it fails, then passes**

Run: `python -m pytest tests/unit/test_stage1_scaffold.py::test_scaffolded_readiness_degrades_to_unstarted_not_malformed -v`
Expected: PASS immediately (the scaffolder from Task 1 already produces this). If it FAILS with `input_defect`, the template copy is being mutated — stop and fix `stage1_scaffold` (the YAML must be copied verbatim).

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_stage1_scaffold.py
git commit -m "test: lock scaffold-source -> next unstarted degrade contract (#339)"
```

---

### Task 4: Bundle the three templates as wheel/sdist package data

**Files:**
- Modify: `pyproject.toml` — `[tool.hatch.build.targets.wheel.force-include]` (~line 128-153) and `[tool.hatch.build.targets.sdist].include` (~line 155-181)

**Interfaces:**
- Consumes: nothing.
- Produces: wheel entries `seshat/stage1_templates/{source-profile.md,readiness-status.yaml,source-map.yaml}` that `stage1_scaffold._template_bytes` resolves at runtime; sdist entries so the wheel (built from the sdist) can carry them.

**Design fact:** the dev-checkout test suite hits the `_SOURCE_ROOT` fallback, so Tasks 1-3 pass WITHOUT this bundling. This task + Task 5 are what make the WHEEL carry the files — the actual #339 fix. Verify via Task 5's gate, not the unit suite.

- [ ] **Step 1: Add the wheel force-include entries** — in `pyproject.toml`, inside `[tool.hatch.build.targets.wheel.force-include]`, append after the last `orchestration/dagster/src` line (~line 153):

```toml
# `seshat scaffold-source <table>` (issue #339) materializes the three Stage-1
# blank templates from these bundled copies so a pip-only workspace can produce
# the first Source-Ready artifact without the development repository. Only the
# table-neutral blank templates ship (constitution VII).
"templates/source-profile.md" = "seshat/stage1_templates/source-profile.md"
"templates/readiness-status.yaml" = "seshat/stage1_templates/readiness-status.yaml"
"templates/source-map.yaml" = "seshat/stage1_templates/source-map.yaml"
```

- [ ] **Step 2: Add the sdist include entries** — in `pyproject.toml`, inside `[tool.hatch.build.targets.sdist].include`, append after the last `/orchestration/dagster/src` line (~line 177):

```toml
    # Stage-1 blank templates the scaffold-source verb bundles (issue #339);
    # the wheel is built from the sdist, so the sdist must carry them.
    "/templates/source-profile.md",
    "/templates/readiness-status.yaml",
    "/templates/source-map.yaml",
```

- [ ] **Step 3: Verify the wheel actually carries them (build + introspect)**

Run:
```bash
python -m pip install --quiet build 2>/dev/null; python -m build --wheel --outdir dist/_stage1check . 2>&1 | tail -3
python -c "import zipfile,glob; w=sorted(glob.glob('dist/_stage1check/*.whl'))[-1]; names=zipfile.ZipFile(w).namelist(); [print('OK', n) for n in names if 'stage1_templates' in n] or None; assert sum('stage1_templates' in n for n in names)==3, 'expected 3 stage1_templates entries'; print('WHEEL CARRIES ALL 3')"
```
Expected: three `OK seshat/stage1_templates/...` lines, then `WHEEL CARRIES ALL 3`.
Cleanup: `rm -rf dist/_stage1check`

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "build: bundle the three Stage-1 templates as package data (#339)"
```

---

### Task 5: Release-gate coverage (fail loud if the bundle is dropped)

**Files:**
- Modify: `scripts/inspect_release_artifacts.py` — `_REQUIRED_WHEEL_PACKAGE_DATA` (~line 119)
- Modify: `tests/contract/test_release_artifact_contents.py` — add a required-inventory case

**Interfaces:**
- Consumes: `scripts.inspect_release_artifacts.validate_wheel_inventory`, `ArtifactInspectionError`.
- Produces: nothing (test + constant only).

**Design fact:** `_REQUIRED_WHEEL_PACKAGE_DATA` is the loud-failure gate for force-included runtime data. #325 did NOT add its bundled files here; this task closes that gap for the Stage-1 three, so a dropped force-include fails the release gate instead of silently reintroducing #339 (the advisor's BLOCKING constraint #1).

- [ ] **Step 1: Write the failing test** — append to `tests/contract/test_release_artifact_contents.py`:

```python
def test_wheel_inventory_requires_stage1_templates() -> None:
    """The three Stage-1 blank templates reach the wheel only via force-include
    (issue #339). A dropped entry must fail the artifact gate rather than
    silently reintroduce the pip-user 'nothing to copy' bug."""
    base = [
        "seshat/__init__.py",
        "retail/__init__.py",
        "seshat/packs/schemas/seshat-extension-pack.schema.json",
        "seshat/packs/schemas/seshat-pack-registry.schema.json",
        "seshat/stage1_templates/source-profile.md",
        "seshat/stage1_templates/readiness-status.yaml",
        "seshat/stage1_templates/source-map.yaml",
        "seshat_bi-0.2.0.dist-info/entry_points.txt",
        "seshat_bi-0.2.0.dist-info/licenses/LICENSE",
    ]
    validate_wheel_inventory(base)
    without_profile = [n for n in base if "source-profile.md" not in n]
    with pytest.raises(ArtifactInspectionError, match="required package data"):
        validate_wheel_inventory(without_profile)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest "tests/contract/test_release_artifact_contents.py::test_wheel_inventory_requires_stage1_templates" -v`
Expected: FAIL — `validate_wheel_inventory(base)` raises because the three assets are not yet required, so the "does NOT raise for a valid inventory" line fails (or the negative branch doesn't fire). Either way, red.

- [ ] **Step 3: Add the three assets to the required constant** — in `scripts/inspect_release_artifacts.py`, extend `_REQUIRED_WHEEL_PACKAGE_DATA`:

```python
_REQUIRED_WHEEL_PACKAGE_DATA = (
    "seshat/packs/schemas/seshat-extension-pack.schema.json",
    "seshat/packs/schemas/seshat-pack-registry.schema.json",
    # Stage-1 blank templates `scaffold-source` reads at call time; they reach
    # the wheel ONLY via force-include (issue #339). A dropped entry would
    # silently strand a pip-only user with nothing to copy -- fail loud here.
    "seshat/stage1_templates/source-profile.md",
    "seshat/stage1_templates/readiness-status.yaml",
    "seshat/stage1_templates/source-map.yaml",
)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/contract/test_release_artifact_contents.py -v`
Expected: PASS (existing cases + the new one).

- [ ] **Step 5: Commit**

```bash
git add scripts/inspect_release_artifacts.py tests/contract/test_release_artifact_contents.py
git commit -m "test: require Stage-1 templates in the wheel release gate (#339)"
```

---

### Task 6: Point `seshat next` at the scaffold verb

**Files:**
- Modify: `src/seshat/agent_next.py` — `_FRESH_NEXT_ACTION` (~line 137-142)
- Test: `tests/unit/test_agent_next_source_ready_pointer.py` (create)

**Interfaces:**
- Consumes: `seshat.agent_next._FRESH_NEXT_ACTION`.
- Produces: nothing (string edit + guard test).

**Design fact:** `_FRESH_NEXT_ACTION` is the guidance a fresh (no-evidence) workspace gets from the agent-facing `next`. Adding the verb name there is the "pointer" half of the fix — cheap, closes the discovery loop. Keep it one sentence appended; do not restructure.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_agent_next_source_ready_pointer.py
"""The fresh-workspace next-action guidance names `scaffold-source` (#339)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_fresh_next_action_mentions_scaffold_source() -> None:
    from seshat.agent_next import _FRESH_NEXT_ACTION

    assert "scaffold-source" in _FRESH_NEXT_ACTION
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/test_agent_next_source_ready_pointer.py -v`
Expected: FAIL — `assert "scaffold-source" in ...` is False.

- [ ] **Step 3: Edit the guidance** — in `src/seshat/agent_next.py`, change `_FRESH_NEXT_ACTION`:

```python
_FRESH_NEXT_ACTION = (
    "No readiness evidence found under mappings/. Begin at Source Ready: "
    "run `seshat scaffold-source <table>` to write the blank source profile "
    "and readiness-status.yaml, then fill the source profile and record "
    "mappings/<table>/readiness-status.yaml before any warehouse or "
    "dashboard work."
)
```

- [ ] **Step 4: Run the test AND the existing agent_next tests to verify none asserted the old exact string**

Run: `python -m pytest tests/unit/test_agent_next_source_ready_pointer.py tests/unit -k "agent_next or fresh or next" -v`
Expected: PASS. If any existing test asserted the OLD `_FRESH_NEXT_ACTION` verbatim, update that assertion to match the new text (it is guidance copy, not a contract).

- [ ] **Step 5: Commit**

```bash
git add src/seshat/agent_next.py tests/unit/test_agent_next_source_ready_pointer.py
git commit -m "feat: point fresh-workspace next guidance at scaffold-source (#339)"
```

---

### Task 7: Changelog + full-suite + governance gate

**Files:**
- Modify: `CHANGELOG.md` (Unreleased section)

**Interfaces:** none.

- [ ] **Step 1: Add the changelog entry** — under the `## [Unreleased]` heading (top of `CHANGELOG.md`), add under an `### Added` subsection (create it if absent, following the file's existing style):

```markdown
- `seshat scaffold-source <table>` writes the three Stage-1 blank templates
  (`source-profile.md`, `readiness-status.yaml`, `source-map.yaml`) into
  `mappings/<table>/` from bundled package data, so a pip-only workspace can
  produce the first Source-Ready artifact without the development repository
  (#339). The three templates now ship as wheel package data and are required
  by the release-artifact gate.
```

- [ ] **Step 2: Run the full unit suite**

Run: `python -m pytest -m unit -q`
Expected: PASS, no regressions. (Note: the pre-existing PBIP-redaction failure on `main` is a known flake — if it appears, confirm it is unrelated to these changes; do not fix it here.)

- [ ] **Step 3: Run ruff format check + lint (CI parity)**

Run: `python -m ruff format --check src/seshat/stage1_scaffold.py src/seshat/cli/commands/scaffold_source.py tests/unit/test_stage1_scaffold.py tests/unit/test_cli_scaffold_source.py && python -m ruff check src tests`
Expected: no diffs, no lint errors. If format check fails, run `python -m ruff format <files>` and re-commit.

- [ ] **Step 4: Run the CodeScene change-set delta gate (CI parity)**

Use the `mcp__plugin_codescene_codescene__analyze_change_set` tool on the branch, or run the repo's local wrapper if present. Expected: no health decline below threshold on the new/edited files. New files are small and focused; if a Large-Method or complexity flag appears, address it before PR.

- [ ] **Step 5: Run the static governance gate**

Run: `python -m seshat.cli check` (or `retail check` if the console script is installed)
Expected: clean (no new violations). This is the same gate the issue's repro invoked.

- [ ] **Step 6: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: changelog for scaffold-source Stage-1 self-sufficiency (#339)"
```

---

## Self-Review

**Spec coverage:**
- Bundle three templates as package data → Task 4 (wheel+sdist).
- New `stage1_scaffold.py` with two-tier resolver + non-destructive writes → Task 1.
- New `scaffold-source <table>` verb → Task 2.
- `seshat next` mentions the verb → Task 6.
- Release-gate coverage (BLOCKING #1) → Task 5.
- Degrade-to-unstarted contract (BLOCKING #2) → Task 3 (empirically pre-verified).
- Constitution VII table-neutrality → enforced by scope (only the three blanks) + Global Constraints; the templates were verified blank during design.
- Broken ADR link neutralized → Task 1 (`_materialized_bytes`).
- Changelog → Task 7. Full suite + ruff + CodeScene + `check` → Task 7.
- All 10 files in the design's "Files touched" table are covered.

**Placeholder scan:** No TBD/TODO/"handle edge cases" — every code step shows complete code; every command shows expected output.

**Type consistency:** `scaffold_source(repo_root, table) -> Stage1Report` and `Stage1ScaffoldError` are defined in Task 1 and consumed with the same names/signatures in Tasks 2, 3, 6. `scaffold_source_main` defined in Task 2, referenced in the `_DISPATCH` string. `_REQUIRED_WHEEL_PACKAGE_DATA` extended in Task 5 matches the wheel paths produced in Task 4. `_FRESH_NEXT_ACTION` edited in Task 6 matches the constant read in its test. All aligned.
