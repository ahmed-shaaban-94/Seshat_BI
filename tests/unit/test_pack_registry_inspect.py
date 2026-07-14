"""``inspect`` unit tests (spec 128, US2, T014).

Full-record display, dependency/conflict listing, and "not found" for an
absent id -- US2 acceptance scenarios 1-4.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.packs.catalog import content_digest
from seshat.packs.registry import inspect, load_registry
from tests.unit._pack_catalog_fixtures import (
    build_test_repo,
    record_dict,
    write_pack,
    write_registry,
)

pytestmark = pytest.mark.unit


def test_inspect_shows_the_complete_record(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi-basic", pack_id="acme.kpi-basic")
    write_registry(
        repo,
        [
            record_dict(
                pack_id="acme.kpi-basic",
                source="packs/reference/kpi-basic",
                content_hash=content_digest(pack_dir),
                dependencies=("acme.other",),
                conflicts=("acme.rival",),
            )
        ],
    )
    registry = load_registry(repo)
    record = inspect(registry, "acme.kpi-basic")
    assert record is not None
    assert record.id == "acme.kpi-basic"
    assert record.version == "1.0.0"
    assert record.category == "kpi"
    assert record.author == "Test Author"
    assert record.source == "packs/reference/kpi-basic"
    assert record.compatibility == "1.x"
    assert len(record.hash) == 64
    assert record.dependencies == ("acme.other",)
    assert record.conflicts == ("acme.rival",)
    assert record.verification_state == "reviewed"


def test_inspect_lists_declared_dependencies(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/needs-dep", pack_id="acme.needs-dep")
    write_registry(
        repo,
        [
            record_dict(
                pack_id="acme.needs-dep",
                source="packs/reference/needs-dep",
                content_hash=content_digest(pack_dir),
                dependencies=("acme.foundation",),
            )
        ],
    )
    record = inspect(load_registry(repo), "acme.needs-dep")
    assert record is not None
    assert "acme.foundation" in record.dependencies


def test_inspect_lists_declared_conflicts(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/rival", pack_id="acme.rival-a")
    write_registry(
        repo,
        [
            record_dict(
                pack_id="acme.rival-a",
                source="packs/reference/rival",
                content_hash=content_digest(pack_dir),
                conflicts=("acme.rival-b",),
            )
        ],
    )
    record = inspect(load_registry(repo), "acme.rival-a")
    assert record is not None
    assert "acme.rival-b" in record.conflicts


def test_inspect_absent_id_reports_not_found(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    registry = load_registry(repo)
    assert inspect(registry, "does.not.exist") is None


def test_inspect_reads_only_registry_metadata(tmp_path: Path) -> None:
    """Inspect never opens the pack SOURCE directory (FR-006)."""
    import shutil

    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi-basic", pack_id="acme.kpi-basic")
    write_registry(
        repo,
        [
            record_dict(
                pack_id="acme.kpi-basic",
                source="packs/reference/kpi-basic",
                content_hash=content_digest(pack_dir),
            )
        ],
    )
    registry = load_registry(repo)
    shutil.rmtree(repo / "packs/reference")
    record = inspect(registry, "acme.kpi-basic")
    assert record is not None
    assert record.id == "acme.kpi-basic"
