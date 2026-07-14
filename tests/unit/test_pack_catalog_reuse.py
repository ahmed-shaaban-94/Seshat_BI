"""Reuse-boundary unit tests (spec 128, US3, T021).

Asserts the catalog CALLS the shipped ``validate_pack`` / ``validate_selection``
for content verdicts and the shipped ``scan_disclosure`` / ``resolve_within``
for secrets/containment -- it never re-implements them (RR-001..RR-004,
SC-005).
"""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from seshat.packs import catalog
from seshat.packs.catalog import add_pack, content_digest
from seshat.packs.registry import Registry, load_registry
from tests.unit._pack_catalog_fixtures import (
    build_test_repo,
    record_dict,
    write_pack,
    write_registry,
)

pytestmark = pytest.mark.unit


def _seeded_registry(repo: Path, pack_dir: Path, pack_id: str) -> Registry:
    write_registry(
        repo,
        [
            record_dict(
                pack_id=pack_id,
                source=str(pack_dir.relative_to(repo)),
                content_hash=content_digest(pack_dir),
            )
        ],
    )
    return load_registry(repo)


def test_add_calls_the_shipped_validate_pack(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    registry = _seeded_registry(repo, pack_dir, "acme.kpi")
    with mock.patch.object(
        catalog, "validate_pack", wraps=catalog.validate_pack
    ) as spy:
        outcome = add_pack(repo, registry, "acme.kpi")
    assert outcome.status == "added"
    spy.assert_called_once()


def test_add_calls_the_shipped_validate_selection(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    registry = _seeded_registry(repo, pack_dir, "acme.kpi")
    with mock.patch.object(
        catalog, "validate_selection", wraps=catalog.validate_selection
    ) as spy:
        outcome = add_pack(repo, registry, "acme.kpi")
    assert outcome.status == "added"
    spy.assert_called_once()


def test_add_calls_the_shipped_scan_disclosure(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    registry = _seeded_registry(repo, pack_dir, "acme.kpi")
    with mock.patch.object(
        catalog, "scan_disclosure", wraps=catalog.scan_disclosure
    ) as spy:
        outcome = add_pack(repo, registry, "acme.kpi")
    assert outcome.status == "added"
    assert spy.call_count >= 1


def test_add_calls_the_shipped_resolve_within(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    registry = _seeded_registry(repo, pack_dir, "acme.kpi")
    with mock.patch.object(
        catalog, "resolve_within", wraps=catalog.resolve_within
    ) as spy:
        outcome = add_pack(repo, registry, "acme.kpi")
    assert outcome.status == "added"
    assert spy.call_count >= 1


def test_a_pack_that_would_fail_existing_validation_is_refused_by_that_validator(
    tmp_path: Path,
) -> None:
    """SC-005: no separate validator produces the verdict. The universal-
    schema claim is a string leaf inside the MANIFEST itself, which
    ``validate_pack``'s existing content walk inspects."""
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(
        repo, "packs/reference/universal-claim", pack_id="acme.universal-claim"
    )
    manifest_path = pack_dir / "seshat-pack.yaml"
    manifest_path.write_text(
        manifest_path.read_text(encoding="utf-8").replace(
            "Synthetic test pack; not a real distribution.",
            "Synthetic test pack that works for all client schemas.",
        ),
        encoding="utf-8",
    )
    registry = _seeded_registry(repo, pack_dir, "acme.universal-claim")
    outcome = add_pack(repo, registry, "acme.universal-claim")
    assert outcome.status == "refused"
    assert any(f["rule"] == "pack_universal_claim" for f in outcome.findings)
