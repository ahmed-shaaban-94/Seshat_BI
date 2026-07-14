"""``search`` unit tests (spec 128, US1, T009).

Keyword match, category filter, empty-result "no matches", and that
unreviewed/deprecated verification state is shown plainly (never hidden or
upgraded) -- US1 acceptance scenarios 1-4.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.packs.catalog import content_digest
from seshat.packs.registry import load_registry, search
from tests.unit._pack_catalog_fixtures import (
    build_test_repo,
    record_dict,
    write_pack,
    write_registry,
)

pytestmark = pytest.mark.unit


def _seeded_repo(tmp_path: Path) -> Path:
    repo = build_test_repo(tmp_path)
    kpi_dir = write_pack(
        repo, "packs/reference/kpi-basic", pack_id="acme.kpi-basic", category="kpi"
    )
    vocab_dir = write_pack(
        repo,
        "packs/reference/vocab-basic",
        pack_id="acme.vocab-basic",
        category="source_vocabulary",
    )
    deprecated_dir = write_pack(
        repo,
        "packs/reference/legacy-kpi",
        pack_id="acme.legacy-kpi",
        category="kpi",
    )
    write_registry(
        repo,
        [
            record_dict(
                pack_id="acme.kpi-basic",
                source="packs/reference/kpi-basic",
                content_hash=content_digest(kpi_dir),
                verification_state="reviewed",
            ),
            record_dict(
                pack_id="acme.vocab-basic",
                category="source_vocabulary",
                source="packs/reference/vocab-basic",
                content_hash=content_digest(vocab_dir),
                verification_state="unreviewed",
            ),
            record_dict(
                pack_id="acme.legacy-kpi",
                source="packs/reference/legacy-kpi",
                content_hash=content_digest(deprecated_dir),
                verification_state="deprecated",
            ),
        ],
    )
    return repo


def test_keyword_match_returns_expected_fields(tmp_path: Path) -> None:
    registry = load_registry(_seeded_repo(tmp_path))
    matches = search(registry, keyword="kpi-basic")
    assert [record.id for record in matches] == ["acme.kpi-basic"]
    record = matches[0]
    assert record.version and record.category and record.author
    assert record.compatibility and record.verification_state


def test_category_filter_restricts_results(tmp_path: Path) -> None:
    registry = load_registry(_seeded_repo(tmp_path))
    matches = search(registry, category="source_vocabulary")
    assert [record.id for record in matches] == ["acme.vocab-basic"]


def test_no_match_returns_empty_without_error(tmp_path: Path) -> None:
    registry = load_registry(_seeded_repo(tmp_path))
    matches = search(registry, keyword="nothing-matches-this-keyword")
    assert matches == ()


def test_unreviewed_and_deprecated_states_shown_plainly(tmp_path: Path) -> None:
    registry = load_registry(_seeded_repo(tmp_path))
    matches = {record.id: record for record in search(registry)}
    assert matches["acme.vocab-basic"].verification_state == "unreviewed"
    assert matches["acme.legacy-kpi"].verification_state == "deprecated"
    # Never silently upgraded to reviewed.
    assert matches["acme.vocab-basic"].reviewed is False
    assert matches["acme.legacy-kpi"].reviewed is False


def test_search_reads_only_registry_metadata(tmp_path: Path, monkeypatch) -> None:
    """Search never opens the pack SOURCE directory -- only registry
    metadata is read (FR-004)."""
    repo = _seeded_repo(tmp_path)
    registry = load_registry(repo)
    import shutil

    # Delete every pack source directory; search must still work because it
    # never fetches content.
    shutil.rmtree(repo / "packs/reference")
    matches = search(registry, keyword="kpi")
    assert {record.id for record in matches} == {"acme.kpi-basic", "acme.legacy-kpi"}
