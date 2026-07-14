"""Shared build helpers for the spec 128 pack-catalog test suite.

Builds a throwaway, minimal repo tree (schemas + packs) so catalog/registry
tests never touch the real ``packs/registry/`` registry or the real
``packs/reference/`` packs. Mirrors the pattern of ``tests/unit/_gitfix.py``.
"""

from __future__ import annotations

from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EXTENSION_SCHEMA = _REPO_ROOT / "schemas/seshat-extension-pack.schema.json"


def build_test_repo(tmp_path: Path) -> Path:
    """A minimal repo root with only the shipped extension-pack schema."""
    repo = tmp_path / "repo"
    schemas = repo / "schemas"
    schemas.mkdir(parents=True)
    (schemas / "seshat-extension-pack.schema.json").write_bytes(
        _EXTENSION_SCHEMA.read_bytes()
    )
    return repo


def write_pack(repo: Path, relative_dir: str, **overrides: object) -> Path:
    """Write one minimal, schema-valid declarative pack under ``repo``.

    Returns the pack's directory (repo-relative parts already joined under
    ``repo``). Accepts the same keyword overrides callers always used
    (``pack_id`` required; ``category``/``owner``/``requires``/``conflicts``/
    ``extra_artifact_text`` optional) via ``**overrides`` so the declared
    parameter count stays low; every existing call site is unaffected since
    Python resolves keyword arguments into ``overrides`` transparently. An
    optional artifact carries ``extra_artifact_text`` verbatim (used to
    inject secret-shaped or oversized content for a specific test).
    """
    pack_id = overrides["pack_id"]
    category = overrides.get("category", "kpi")
    owner = overrides.get("owner", "Test Owner")
    requires: tuple[str, ...] = overrides.get("requires", ())
    conflicts: tuple[str, ...] = overrides.get("conflicts", ())
    extra_artifact_text = overrides.get("extra_artifact_text")

    pack_dir = repo / relative_dir
    (pack_dir / "artifacts").mkdir(parents=True)
    (pack_dir / "fixtures").mkdir(parents=True)
    artifact_body = extra_artifact_text or "note: a generic declarative artifact.\n"
    (pack_dir / "artifacts/note.yaml").write_text(artifact_body, encoding="utf-8")
    (pack_dir / "fixtures/synthetic.csv").write_text(
        "example_key,example_value\nsynthetic-1,10\n", encoding="utf-8"
    )
    manifest = {
        "schema_version": "1.0",
        "pack_id": pack_id,
        "version": "1.0.0",
        "category": category,
        "owner": owner,
        "description": "Synthetic test pack; not a real distribution.",
        "core_compatibility": "1.x",
        "provides": [pack_id.split(".")[-1]],
        "requires": list(requires),
        "conflicts": list(conflicts),
        "artifacts": [{"path": "artifacts/note.yaml", "purpose": "test artifact"}],
        "human_decisions": ["A named human owner reviews this synthetic content."],
        "fixtures": ["fixtures/synthetic.csv"],
        "verification": ["retail pack validate --repo . --pack " + relative_dir],
        "non_goals": ["Does not represent real distribution content."],
    }
    (pack_dir / "seshat-pack.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
    )
    return pack_dir


def record_dict(**overrides: object) -> dict:
    """Build one registry-record dict. ``pack_id``, ``source``, and
    ``content_hash`` are required; the rest have the same defaults as
    before. Collapsed to ``**overrides`` (from individually named keyword
    args) purely to keep the declared parameter count low -- every existing
    call site is unaffected since Python resolves keyword arguments into
    ``overrides`` transparently.
    """
    return {
        "id": overrides["pack_id"],
        "version": overrides.get("version", "1.0.0"),
        "category": overrides.get("category", "kpi"),
        "author": overrides.get("author", "Test Author"),
        "source": overrides["source"],
        "compatibility": overrides.get("compatibility", "1.x"),
        "hash": overrides["content_hash"],
        "dependencies": list(overrides.get("dependencies", ())),
        "conflicts": list(overrides.get("conflicts", ())),
        "verification_state": overrides.get("verification_state", "reviewed"),
    }


def write_registry(repo: Path, records: list[dict]) -> Path:
    registry_dir = repo / "packs/registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    index_path = registry_dir / "index.yaml"
    index_path.write_text(
        yaml.safe_dump({"schema_version": "1.0", "records": records}, sort_keys=False),
        encoding="utf-8",
    )
    return index_path
