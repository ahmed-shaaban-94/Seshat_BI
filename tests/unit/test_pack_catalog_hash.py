"""Hashing unit tests (spec 128, US3, T019).

``content_digest`` is SHA-256 over the whole pack directory (every file's
relative path + bytes, sorted); any byte change anywhere in the tree flips
the verdict (FR-008).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.packs.catalog import content_digest
from tests.unit._pack_catalog_fixtures import build_test_repo, write_pack

pytestmark = pytest.mark.unit


def test_digest_is_a_64_character_hex_string(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi-basic", pack_id="acme.kpi-basic")
    digest = content_digest(pack_dir)
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


def test_digest_is_deterministic_for_identical_content(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi-basic", pack_id="acme.kpi-basic")
    assert content_digest(pack_dir) == content_digest(pack_dir)


def test_any_byte_change_in_the_manifest_flips_the_digest(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi-basic", pack_id="acme.kpi-basic")
    before = content_digest(pack_dir)
    manifest = pack_dir / "seshat-pack.yaml"
    manifest.write_text(manifest.read_text(encoding="utf-8") + "\n# tampered\n")
    after = content_digest(pack_dir)
    assert before != after


def test_any_byte_change_in_a_declared_artifact_flips_the_digest(
    tmp_path: Path,
) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi-basic", pack_id="acme.kpi-basic")
    before = content_digest(pack_dir)
    artifact = pack_dir / "artifacts/note.yaml"
    artifact.write_text(artifact.read_text(encoding="utf-8") + "tampered: true\n")
    after = content_digest(pack_dir)
    assert before != after


def test_adding_a_stray_file_flips_the_digest(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi-basic", pack_id="acme.kpi-basic")
    before = content_digest(pack_dir)
    (pack_dir / "artifacts/extra.yaml").write_text("sneaky: true\n", encoding="utf-8")
    after = content_digest(pack_dir)
    assert before != after
