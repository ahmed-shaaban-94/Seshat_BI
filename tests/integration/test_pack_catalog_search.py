"""``pack search`` acceptance coverage (spec 128, US1, T013).

Runs `pack search` over a fixture registry through the real CLI entry point
and confirms the expected matches, and that nothing is fetched (SC-001):
the pack source directories are deleted before the search runs.
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
    kpi_dir = write_pack(
        repo, "packs/reference/kpi", pack_id="acme.kpi", category="kpi"
    )
    vocab_dir = write_pack(
        repo,
        "packs/reference/vocab",
        pack_id="acme.vocab",
        category="source_vocabulary",
    )
    write_registry(
        repo,
        [
            record_dict(
                pack_id="acme.kpi",
                source="packs/reference/kpi",
                content_hash=content_digest(kpi_dir),
            ),
            record_dict(
                pack_id="acme.vocab",
                category="source_vocabulary",
                source="packs/reference/vocab",
                content_hash=content_digest(vocab_dir),
                verification_state="unreviewed",
            ),
        ],
    )
    return repo


def test_search_over_fixture_registry_returns_expected_matches_and_fetches_nothing(
    tmp_path: Path, capsys
) -> None:
    repo = _seeded_repo(tmp_path)
    # Delete pack sources: search must succeed identically -- it reads only
    # registry metadata and fetches nothing.
    shutil.rmtree(repo / "packs/reference")

    assert (
        main(
            [
                "pack",
                "search",
                "--repo",
                str(repo),
                "--query",
                "kpi",
                "--format",
                "json",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert [m["id"] for m in payload["matches"]] == ["acme.kpi"]
    match = payload["matches"][0]
    assert set(match) >= {
        "id",
        "version",
        "category",
        "author",
        "compatibility",
        "verification_state",
    }


def test_search_with_no_match_returns_zero_with_no_matches_message(
    tmp_path: Path, capsys
) -> None:
    repo = _seeded_repo(tmp_path)
    assert (
        main(["pack", "search", "--repo", str(repo), "--query", "no-such-thing"]) == 0
    )
    assert "no matches" in capsys.readouterr().out


def test_search_category_filter_via_cli(tmp_path: Path, capsys) -> None:
    repo = _seeded_repo(tmp_path)
    assert (
        main(
            [
                "pack",
                "search",
                "--repo",
                str(repo),
                "--category",
                "source_vocabulary",
                "--format",
                "json",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert [m["id"] for m in payload["matches"]] == ["acme.vocab"]
