"""Attribution invariant unit tests (spec 128, T034).

``author`` (the registry contributor) is present and unaltered through
search/inspect/add, and is never conflated with the pack manifest's own
``owner`` field (FR-017, SC-007).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.packs.catalog import add_pack, content_digest
from seshat.packs.registry import inspect, load_registry, search
from seshat.packs.validator import validate_pack
from tests.unit._pack_catalog_fixtures import (
    build_test_repo,
    record_dict,
    write_pack,
    write_registry,
)

pytestmark = pytest.mark.unit

_REGISTRY_AUTHOR = "Registry Contributor Jordan"
_MANIFEST_OWNER = "Manifest Content Owner Casey"


def _seed(repo: Path) -> Path:
    pack_dir = write_pack(
        repo, "packs/reference/kpi", pack_id="acme.kpi", owner=_MANIFEST_OWNER
    )
    write_registry(
        repo,
        [
            record_dict(
                pack_id="acme.kpi",
                author=_REGISTRY_AUTHOR,
                source="packs/reference/kpi",
                content_hash=content_digest(pack_dir),
            )
        ],
    )
    return pack_dir


def test_author_and_owner_are_deliberately_different_values(tmp_path: Path) -> None:
    # Sanity check the fixture itself carries two distinct identities.
    assert _REGISTRY_AUTHOR != _MANIFEST_OWNER


def test_search_preserves_author_without_touching_manifest_owner(
    tmp_path: Path,
) -> None:
    repo = build_test_repo(tmp_path)
    _seed(repo)
    matches = search(load_registry(repo))
    assert len(matches) == 1
    assert matches[0].author == _REGISTRY_AUTHOR


def test_inspect_preserves_author_distinct_from_manifest_owner(
    tmp_path: Path,
) -> None:
    repo = build_test_repo(tmp_path)
    _seed(repo)
    record = inspect(load_registry(repo), "acme.kpi")
    assert record is not None
    assert record.author == _REGISTRY_AUTHOR
    # RegistryRecord has no "owner" attribute at all -- it cannot conflate
    # the two identities because there is nowhere for "owner" to leak into.
    assert not hasattr(record, "owner")


def test_add_does_not_alter_the_manifest_owner_field(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    _seed(repo)
    outcome = add_pack(repo, load_registry(repo), "acme.kpi")
    assert outcome.status == "added"
    added_manifest = repo / "packs/added/kpi/seshat-pack.yaml"
    manifest, findings = validate_pack(repo, str(added_manifest.relative_to(repo)))
    assert findings == []
    assert manifest is not None
    assert manifest.owner == _MANIFEST_OWNER  # untouched by the catalog


def test_registry_author_survives_unchanged_across_the_whole_journey(
    tmp_path: Path,
) -> None:
    repo = build_test_repo(tmp_path)
    _seed(repo)
    registry = load_registry(repo)
    searched = search(registry)[0].author
    inspected = inspect(registry, "acme.kpi").author
    assert searched == inspected == _REGISTRY_AUTHOR
