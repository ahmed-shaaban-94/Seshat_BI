"""``pack add`` refusal acceptance coverage (spec 128, US3, T031).

A tampered pack and an incompatible pack are each refused with nothing
added (SC-003, SC-004), exercised through the real CLI entry point.
"""

from __future__ import annotations

import json
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


def test_tampered_pack_is_refused_with_nothing_added(tmp_path: Path, capsys) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    correct_hash = content_digest(pack_dir)
    write_registry(
        repo,
        [
            record_dict(
                pack_id="acme.kpi",
                source="packs/reference/kpi",
                content_hash=correct_hash,
            )
        ],
    )
    # Tamper AFTER the hash was recorded.
    (pack_dir / "artifacts/note.yaml").write_text("tampered: true\n", encoding="utf-8")

    exit_code = main(
        ["pack", "add", "--repo", str(repo), "acme.kpi", "--format", "json"]
    )
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert payload["status"] == "refused"
    assert any(f["rule"] == "pack_catalog_tamper" for f in payload["findings"])
    assert not (repo / "packs/added").exists()


def test_incompatible_pack_is_refused_with_nothing_added(
    tmp_path: Path, capsys
) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    write_registry(
        repo,
        [
            record_dict(
                pack_id="acme.kpi",
                source="packs/reference/kpi",
                content_hash=content_digest(pack_dir),
                compatibility="7.x",
            )
        ],
    )

    exit_code = main(
        ["pack", "add", "--repo", str(repo), "acme.kpi", "--format", "json"]
    )
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert payload["status"] == "refused"
    assert any(f["rule"] == "pack_incompatible_core" for f in payload["findings"])
    assert not (repo / "packs/added").exists()


def test_unknown_pack_id_is_refused_via_cli(tmp_path: Path, capsys) -> None:
    repo = build_test_repo(tmp_path)
    exit_code = main(["pack", "add", "--repo", str(repo), "does.not.exist"])
    assert exit_code == 1
    assert not (repo / "packs/added").exists()
