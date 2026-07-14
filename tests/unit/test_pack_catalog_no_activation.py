"""No-side-effect unit tests (spec 128, US3, T022).

After a successful add: no readiness stage advanced, no approval granted,
no activation/toggle file written, and no database write / Power BI
modification / publish occurred. The only write is local workspace content;
added content is inert until explicitly selected (FR-011, FR-012, FR-013,
FR-018, SC-006).
"""

from __future__ import annotations

import socket
from pathlib import Path

import pytest

from seshat.packs.catalog import add_pack, content_digest
from seshat.packs.registry import load_registry
from tests.unit._pack_catalog_fixtures import (
    build_test_repo,
    record_dict,
    write_pack,
    write_registry,
)

pytestmark = pytest.mark.unit


def _seed(repo: Path, pack_id: str = "acme.kpi") -> Path:
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id=pack_id)
    write_registry(
        repo,
        [
            record_dict(
                pack_id=pack_id,
                source="packs/reference/kpi",
                content_hash=content_digest(pack_dir),
            )
        ],
    )
    return pack_dir


def test_no_readiness_status_file_is_touched(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    _seed(repo)
    readiness_files_before = set(repo.rglob("readiness-status.yaml"))
    outcome = add_pack(repo, load_registry(repo), "acme.kpi")
    assert outcome.status == "added"
    readiness_files_after = set(repo.rglob("readiness-status.yaml"))
    assert readiness_files_before == readiness_files_after == set()


def test_no_activation_or_toggle_file_is_written(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    _seed(repo)
    outcome = add_pack(repo, load_registry(repo), "acme.kpi")
    assert outcome.status == "added"
    all_paths = {p.name.lower() for p in repo.rglob("*") if p.is_file()}
    forbidden_names = {
        "activated.yaml",
        "activation.yaml",
        "installed.yaml",
        "enabled.yaml",
    }
    assert not (all_paths & forbidden_names)
    # Every written file is declarative content (mirrors validate_pack's own
    # declarative-suffix allow-list); nothing executable landed.
    for written in outcome.written:
        assert Path(written).suffix.lower() in {
            ".yaml",
            ".yml",
            ".md",
            ".csv",
            ".json",
            ".txt",
            ".svg",
        }


def test_added_content_is_inert_until_explicitly_selected(tmp_path: Path) -> None:
    """A successful add writes files; it does not itself constitute a
    'selection' the way ``pack validate --pack ...`` would. Nothing in the
    repo tree references the added pack as active."""
    repo = build_test_repo(tmp_path)
    _seed(repo)
    outcome = add_pack(repo, load_registry(repo), "acme.kpi")
    assert outcome.status == "added"
    manifest_text = (repo / "packs/added/kpi/seshat-pack.yaml").read_text(
        encoding="utf-8"
    )
    assert "active" not in manifest_text.lower()
    assert "enabled" not in manifest_text.lower()


def test_add_never_opens_a_network_socket(tmp_path: Path, monkeypatch) -> None:
    def _refuse_socket(*args, **kwargs):
        raise AssertionError("add_pack must never open a network socket")

    monkeypatch.setattr(socket, "socket", _refuse_socket)
    repo = build_test_repo(tmp_path)
    _seed(repo)
    outcome = add_pack(repo, load_registry(repo), "acme.kpi")
    assert outcome.status == "added"


def test_add_never_imports_a_database_driver(tmp_path: Path) -> None:
    import sys

    forbidden_modules = {"psycopg", "psycopg2", "sqlalchemy"}
    before = forbidden_modules & set(sys.modules)
    repo = build_test_repo(tmp_path)
    _seed(repo)
    add_pack(repo, load_registry(repo), "acme.kpi")
    after = forbidden_modules & set(sys.modules)
    assert after == before  # add_pack imported none of them itself


def test_only_write_is_under_the_destination_directory(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    _seed(repo)
    before = {p for p in repo.rglob("*") if p.is_file()}
    outcome = add_pack(repo, load_registry(repo), "acme.kpi")
    after = {p for p in repo.rglob("*") if p.is_file()}
    new_files = after - before
    assert new_files == {repo / p for p in outcome.written}
    for path in new_files:
        assert (repo / "packs/added") in path.parents
