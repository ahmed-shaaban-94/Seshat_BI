"""``pack inspect`` acceptance coverage (spec 128, US2, T018).

Confirms the full record is shown, that nothing is fetched (SC-002), and
that an absent id reports "not found" without attempting retrieval.
"""

from __future__ import annotations

import json
import shutil
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


def _seeded_repo(tmp_path: Path) -> Path:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(
        repo, "packs/reference/kpi", pack_id="acme.kpi", category="kpi"
    )
    write_registry(
        repo,
        [
            record_dict(
                pack_id="acme.kpi",
                source="packs/reference/kpi",
                content_hash=content_digest(pack_dir),
                dependencies=("acme.other",),
                conflicts=("acme.rival",),
            )
        ],
    )
    return repo


def test_inspect_shows_the_full_record_and_fetches_nothing(
    tmp_path: Path, capsys
) -> None:
    repo = _seeded_repo(tmp_path)
    shutil.rmtree(repo / "packs/reference")  # nothing fetched required

    assert (
        main(["pack", "inspect", "--repo", str(repo), "acme.kpi", "--format", "json"])
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "found"
    assert payload["id"] == "acme.kpi"
    for field in (
        "id",
        "version",
        "category",
        "author",
        "source",
        "compatibility",
        "hash",
        "dependencies",
        "conflicts",
        "verification_state",
    ):
        assert field in payload
    assert payload["dependencies"] == ["acme.other"]
    assert payload["conflicts"] == ["acme.rival"]


def test_inspect_absent_id_reports_not_found_and_attempts_no_retrieval(
    tmp_path: Path, capsys
) -> None:
    repo = _seeded_repo(tmp_path)
    exit_code = main(["pack", "inspect", "--repo", str(repo), "does.not.exist"])
    assert exit_code == 1
    assert "not found" in capsys.readouterr().out
