"""Offline-guarantee acceptance test (spec 128, T037).

The entire search -> inspect -> add flow runs against a checked-out static
registry with NO network access and NO database (no socket, no driver
import) -- FR-001, FR-018, SC-009.
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path

import pytest

from seshat.cli import main
from seshat.packs.catalog import content_digest
from tests.unit._pack_catalog_fixtures import (
    build_test_repo,
    record_dict,
    write_pack,
    write_registry,
)

pytestmark = pytest.mark.integration

_FORBIDDEN_DB_MODULES = ("psycopg", "psycopg2", "sqlalchemy", "pyodbc")


def _seeded_repo(tmp_path: Path) -> Path:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    write_registry(
        repo,
        [
            record_dict(
                pack_id="acme.kpi",
                source="packs/reference/kpi",
                content_hash=content_digest(pack_dir),
            )
        ],
    )
    return repo


def test_full_flow_runs_with_sockets_disabled(tmp_path: Path, monkeypatch) -> None:
    def _refuse_socket(*args, **kwargs):
        raise AssertionError(
            "the pack catalog must never open a network socket (Principle VIII)"
        )

    monkeypatch.setattr(socket, "socket", _refuse_socket)
    repo = _seeded_repo(tmp_path)

    assert main(["pack", "search", "--repo", str(repo)]) == 0
    assert main(["pack", "inspect", "--repo", str(repo), "acme.kpi"]) == 0
    assert main(["pack", "add", "--repo", str(repo), "acme.kpi"]) == 0


def test_full_flow_imports_no_database_driver(tmp_path: Path) -> None:
    before = set(sys.modules) & set(_FORBIDDEN_DB_MODULES)
    repo = _seeded_repo(tmp_path)

    main(["pack", "search", "--repo", str(repo)])
    main(["pack", "inspect", "--repo", str(repo), "acme.kpi"])
    main(["pack", "add", "--repo", str(repo), "acme.kpi"])

    after = set(sys.modules) & set(_FORBIDDEN_DB_MODULES)
    assert after == before
