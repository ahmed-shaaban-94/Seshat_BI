"""Registry load/parse unit tests (spec 128, T006, T007, T008).

Covers the edge cases spec.md lists for the registry file itself: absent,
unreadable, non-UTF-8, not-a-mapping, and the duplicate id+version defect.
All failures are disclosure-safe (no absolute host path, no secret) and none
partially succeed -- see spec.md "Edge Cases".
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.packs.catalog import content_digest
from seshat.packs.registry import RegistryError, load_registry
from tests.unit._pack_catalog_fixtures import (
    build_test_repo,
    record_dict,
    write_pack,
    write_registry,
)

pytestmark = pytest.mark.unit


def test_absent_registry_yields_zero_records(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    registry = load_registry(repo)
    assert registry.records == ()
    assert registry.findings == ()


def test_unreadable_registry_fails_closed_disclosure_safe(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    registry_dir = repo / "packs/registry"
    registry_dir.mkdir(parents=True)
    (registry_dir / "index.yaml").write_bytes(b"\xff\xfe\x00\x01not-utf8")
    with pytest.raises(RegistryError) as excinfo:
        load_registry(repo)
    message = str(excinfo.value)
    assert "packs/registry" in message
    assert str(tmp_path) not in message


def test_non_mapping_registry_fails_closed(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    registry_dir = repo / "packs/registry"
    registry_dir.mkdir(parents=True)
    (registry_dir / "index.yaml").write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(RegistryError):
        load_registry(repo)


def test_registry_escaping_workspace_fails_closed(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    with pytest.raises(RegistryError):
        load_registry(repo, registry_path="../outside/index.yaml")


def test_registry_missing_records_key_fails_closed(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    registry_dir = repo / "packs/registry"
    registry_dir.mkdir(parents=True)
    (registry_dir / "index.yaml").write_text(
        "schema_version: '1.0'\n", encoding="utf-8"
    )
    with pytest.raises(RegistryError):
        load_registry(repo)


def test_duplicate_id_and_version_is_a_defect_and_not_silently_chosen(
    tmp_path: Path,
) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/dupe", pack_id="acme.dupe")
    digest = content_digest(pack_dir)
    write_registry(
        repo,
        [
            record_dict(
                pack_id="acme.dupe", source="packs/reference/dupe", content_hash=digest
            ),
            record_dict(
                pack_id="acme.dupe",
                source="packs/reference/dupe",
                content_hash=digest,
                author="A Different Author",
            ),
        ],
    )
    registry = load_registry(repo)
    assert registry.records == ()  # neither duplicate is silently chosen
    rules = {finding["rule"] for finding in registry.findings}
    assert "pack_registry_duplicate_record" in rules


def test_schema_invalid_record_is_excluded_but_others_still_usable(
    tmp_path: Path,
) -> None:
    repo = build_test_repo(tmp_path)
    good_dir = write_pack(repo, "packs/reference/good", pack_id="acme.good")
    good_hash = content_digest(good_dir)
    good_record = record_dict(
        pack_id="acme.good", source="packs/reference/good", content_hash=good_hash
    )
    bad_record = {
        "id": "acme.bad",
        "version": "1.0.0",
        "category": "kpi",
        "author": "Acme",
        "source": "packs/reference/bad",
        "compatibility": "1.x",
        # hash / dependencies / conflicts / verification_state omitted
    }
    write_registry(repo, [good_record, bad_record])
    registry = load_registry(repo)
    assert [record.id for record in registry.records] == ["acme.good"]
    assert any(
        finding["rule"] == "pack_registry_invalid_record"
        for finding in registry.findings
    )
