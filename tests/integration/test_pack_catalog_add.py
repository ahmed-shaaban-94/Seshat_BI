"""``pack add`` happy-path acceptance coverage (spec 128, US3, T030).

Full search -> inspect -> add path: content lands as a reviewable change,
the existing validation ran and passed, and no readiness stage advanced
(SC-003, SC-006).
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


def test_full_search_inspect_add_happy_path(tmp_path: Path, capsys) -> None:
    repo = _seeded_repo(tmp_path)

    assert main(["pack", "search", "--repo", str(repo), "--query", "kpi"]) == 0
    capsys.readouterr()

    assert main(["pack", "inspect", "--repo", str(repo), "acme.kpi"]) == 0
    capsys.readouterr()

    readiness_before = set(repo.rglob("readiness-status.yaml"))
    assert (
        main(["pack", "add", "--repo", str(repo), "acme.kpi", "--format", "json"]) == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "added"
    assert payload["findings"] == []
    assert any(w.endswith("seshat-pack.yaml") for w in payload["written"])

    added_manifest = repo / "packs/added/kpi/seshat-pack.yaml"
    assert added_manifest.is_file()

    # The existing shipped validator confirms the added content still passes.
    assert (
        main(
            [
                "pack",
                "validate",
                "--repo",
                str(repo),
                "--pack",
                "packs/added/kpi/seshat-pack.yaml",
            ]
        )
        == 0
    )

    readiness_after = set(repo.rglob("readiness-status.yaml"))
    assert readiness_before == readiness_after == set()


def test_add_result_notes_content_is_inert(tmp_path: Path, capsys) -> None:
    repo = _seeded_repo(tmp_path)
    assert main(["pack", "add", "--repo", str(repo), "acme.kpi"]) == 0
    output = capsys.readouterr().out
    assert "result: added" in output
    assert "inert" in output


def test_add_result_carries_contributor_attribution(tmp_path: Path, capsys) -> None:
    """The add result must carry the registry record's author/
    verification_state through -- otherwise `add` would be the only catalog
    surface (unlike search/inspect) where a user cannot see who the added
    content is attributed to."""
    repo = _seeded_repo(tmp_path)
    assert (
        main(["pack", "add", "--repo", str(repo), "acme.kpi", "--format", "json"]) == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["author"] == "Test Author"
    assert payload["verification_state"] == "reviewed"

    repo2 = _seeded_repo(tmp_path / "second")
    assert main(["pack", "add", "--repo", str(repo2), "acme.kpi"]) == 0
    text_output = capsys.readouterr().out
    assert "author: Test Author" in text_output
    assert "verification_state: reviewed" in text_output


def test_add_surfaces_registry_defects_for_a_duplicated_id(
    tmp_path: Path, capsys
) -> None:
    """When the requested id only exists as records excluded by a registry
    defect (duplicate id+version), add must report the registry defect
    rather than letting a defective registry look like a simple missing
    pack (pack_catalog_unknown_id with no explanation)."""
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    dup = record_dict(
        pack_id="acme.kpi",
        source="packs/reference/kpi",
        content_hash=content_digest(pack_dir),
    )
    write_registry(repo, [dup, dict(dup)])

    assert (
        main(
            ["pack", "add", "--repo", str(repo), "acme.kpi", "--format", "json"],
        )
        == 1
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "refused"
    assert any(
        f["rule"] == "pack_registry_duplicate_record"
        for f in payload["registry_findings"]
    )
