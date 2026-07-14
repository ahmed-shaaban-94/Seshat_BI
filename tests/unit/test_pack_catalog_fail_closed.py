"""Fail-closed catalog unit tests (spec 128, US3, T020).

One refusal class per test: unknown id, hash mismatch (tamper),
schema-invalid record, schema-invalid content, incompatible core,
missing/dangling source, containment escape, disclosure hit,
existing-validation finding, workspace collision. Every case must add
NOTHING to the workspace and return a disclosure-safe finding (FR-008,
FR-009, FR-010, FR-014, FR-019, FR-022).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.packs.catalog import add_pack, content_digest
from seshat.packs.registry import Registry, RegistryRecord, load_registry
from tests.unit._pack_catalog_fixtures import build_test_repo, record_dict, write_pack

pytestmark = pytest.mark.unit


def _one_record_registry(*records: dict) -> Registry:
    built = tuple(
        RegistryRecord(
            id=r["id"],
            version=r["version"],
            category=r["category"],
            author=r["author"],
            source=r["source"],
            compatibility=r["compatibility"],
            hash=r["hash"],
            dependencies=tuple(r.get("dependencies", [])),
            conflicts=tuple(r.get("conflicts", [])),
            verification_state=r.get("verification_state", "unreviewed"),
        )
        for r in records
    )
    return Registry(records=built, findings=())


def _nothing_written(repo: Path) -> bool:
    added = repo / "packs/added"
    return not added.exists() or not any(added.rglob("*"))


def test_unknown_pack_id_is_refused(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    registry = load_registry(repo)
    outcome = add_pack(repo, registry, "does.not.exist")
    assert outcome.status == "refused"
    assert {f["rule"] for f in outcome.findings} == {"pack_catalog_unknown_id"}
    assert _nothing_written(repo)


def test_hash_mismatch_is_refused_as_tamper(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    registry = _one_record_registry(
        record_dict(
            pack_id="acme.kpi", source="packs/reference/kpi", content_hash="0" * 64
        )
    )
    outcome = add_pack(repo, registry, "acme.kpi")
    assert outcome.status == "refused"
    rules = {f["rule"] for f in outcome.findings}
    assert "pack_catalog_tamper" in rules
    assert any("acme.kpi" in f["message"] for f in outcome.findings)
    assert _nothing_written(repo)


def test_incompatible_core_is_refused(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    registry = _one_record_registry(
        record_dict(
            pack_id="acme.kpi",
            source="packs/reference/kpi",
            content_hash=content_digest(pack_dir),
            compatibility="99.x",
        )
    )
    outcome = add_pack(repo, registry, "acme.kpi")
    assert outcome.status == "refused"
    assert any(f["rule"] == "pack_incompatible_core" for f in outcome.findings)
    assert _nothing_written(repo)


@pytest.mark.parametrize(
    ("source", "expected_rule"),
    [
        ("packs/reference/absent", "pack_catalog_missing_content"),
        ("../outside-workspace", "pack_catalog_containment"),
    ],
    ids=["missing_dangling_source", "containment_escape"],
)
def test_unresolvable_source_is_refused(
    tmp_path: Path, source: str, expected_rule: str
) -> None:
    repo = build_test_repo(tmp_path)
    registry = _one_record_registry(
        record_dict(pack_id="acme.kpi", source=source, content_hash="0" * 64)
    )
    outcome = add_pack(repo, registry, "acme.kpi")
    assert outcome.status == "refused"
    assert {f["rule"] for f in outcome.findings} == {expected_rule}
    assert _nothing_written(repo)


def test_disclosure_hit_is_refused(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(
        repo,
        "packs/reference/leaky",
        pack_id="acme.leaky",
        extra_artifact_text="note: postgres://user:pass@host:5432/db\n",
    )
    registry = _one_record_registry(
        record_dict(
            pack_id="acme.leaky",
            source="packs/reference/leaky",
            content_hash=content_digest(pack_dir),
        )
    )
    outcome = add_pack(repo, registry, "acme.leaky")
    assert outcome.status == "refused"
    assert any(f["rule"] == "pack_catalog_disclosure" for f in outcome.findings)
    assert _nothing_written(repo)


def test_disclosure_hit_in_a_yaml_comment_is_refused(tmp_path: Path) -> None:
    """A secret hiding in a YAML COMMENT (which yaml.safe_load silently
    drops from the parsed mapping) must still be caught, since the
    ORIGINAL bytes -- comment included -- are what gets copied into the
    workspace on a successful add."""
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(
        repo,
        "packs/reference/commented",
        pack_id="acme.commented",
        extra_artifact_text=(
            "note: a generic declarative artifact.\n"
            "# see postgres://user:pass@host:5432/db for context\n"
        ),
    )
    registry = _one_record_registry(
        record_dict(
            pack_id="acme.commented",
            source="packs/reference/commented",
            content_hash=content_digest(pack_dir),
        )
    )
    outcome = add_pack(repo, registry, "acme.commented")
    assert outcome.status == "refused"
    assert any(f["rule"] == "pack_catalog_disclosure" for f in outcome.findings)
    assert _nothing_written(repo)


def test_schema_invalid_content_is_refused_via_existing_validation(
    tmp_path: Path,
) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = repo / "packs/reference/broken"
    pack_dir.mkdir(parents=True)
    (pack_dir / "seshat-pack.yaml").write_text(
        "schema_version: '1.0'\npack_id: acme.broken\n", encoding="utf-8"
    )  # missing every other required manifest field
    registry = _one_record_registry(
        record_dict(
            pack_id="acme.broken",
            source="packs/reference/broken",
            content_hash=content_digest(pack_dir),
        )
    )
    outcome = add_pack(repo, registry, "acme.broken")
    assert outcome.status == "refused"
    assert any(f["rule"] == "pack_schema" for f in outcome.findings)
    assert _nothing_written(repo)


def test_existing_validation_finding_blocks_add(tmp_path: Path) -> None:
    """A pack that declares executable wiring fails the SHIPPED validator
    (RR-001); the catalog does not re-implement that check (SC-005)."""
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/hooked", pack_id="acme.hooked")
    manifest_path = pack_dir / "seshat-pack.yaml"
    text = manifest_path.read_text(encoding="utf-8")
    manifest_path.write_text(text + "hooks:\n  - on_load: run.sh\n", encoding="utf-8")
    registry = _one_record_registry(
        record_dict(
            pack_id="acme.hooked",
            source="packs/reference/hooked",
            content_hash=content_digest(pack_dir),
        )
    )
    outcome = add_pack(repo, registry, "acme.hooked")
    assert outcome.status == "refused"
    assert any(f["rule"] == "pack_schema" for f in outcome.findings)
    assert _nothing_written(repo)


def test_workspace_collision_is_refused(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    registry = _one_record_registry(
        record_dict(
            pack_id="acme.kpi",
            source="packs/reference/kpi",
            content_hash=content_digest(pack_dir),
        )
    )
    dest = repo / "packs/added/kpi"
    dest.mkdir(parents=True)
    (dest / "stale.txt").write_text("pre-existing", encoding="utf-8")
    outcome = add_pack(repo, registry, "acme.kpi")
    assert outcome.status == "refused"
    assert {f["rule"] for f in outcome.findings} == {"pack_catalog_collision"}
    assert not (dest / "seshat-pack.yaml").exists()


def test_undeclared_file_is_refused(tmp_path: Path) -> None:
    """A pack source directory file the manifest never declares as an
    artifact or fixture (e.g. a stray script) must refuse the add -- a
    matching content hash over the whole directory does not make an
    undeclared file declarative."""
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/sneaky", pack_id="acme.sneaky")
    (pack_dir / "run.sh").write_text("#!/bin/sh\necho hi\n", encoding="utf-8")
    registry = _one_record_registry(
        record_dict(
            pack_id="acme.sneaky",
            source="packs/reference/sneaky",
            content_hash=content_digest(pack_dir),
        )
    )
    outcome = add_pack(repo, registry, "acme.sneaky")
    assert outcome.status == "refused"
    assert any(f["rule"] == "pack_catalog_undeclared_file" for f in outcome.findings)
    assert _nothing_written(repo)


def test_unreadable_declared_content_is_refused(tmp_path: Path) -> None:
    """A declared artifact file that cannot be read/parsed (malformed YAML
    or non-UTF-8 bytes) must fail closed, never be silently skipped by the
    disclosure pass -- otherwise a secret inside unparseable content would
    slip through untouched."""
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/binary", pack_id="acme.binary")
    (pack_dir / "artifacts/note.yaml").write_bytes(b"\xff\xfe\x00\x01not-utf8")
    registry = _one_record_registry(
        record_dict(
            pack_id="acme.binary",
            source="packs/reference/binary",
            content_hash=content_digest(pack_dir),
        )
    )
    outcome = add_pack(repo, registry, "acme.binary")
    assert outcome.status == "refused"
    assert any(f["rule"] == "pack_catalog_unreadable_content" for f in outcome.findings)
    assert _nothing_written(repo)


def test_dest_is_existing_file_is_refused_as_collision(tmp_path: Path) -> None:
    """``--dest`` naming an existing FILE (not a directory) must refuse as a
    collision, not crash with NotADirectoryError from a bare iterdir()."""
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    registry = _one_record_registry(
        record_dict(
            pack_id="acme.kpi",
            source="packs/reference/kpi",
            content_hash=content_digest(pack_dir),
        )
    )
    dest = repo / "packs/added/kpi-file"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("i am a file, not a directory", encoding="utf-8")
    outcome = add_pack(repo, registry, "acme.kpi", dest=str(dest))
    assert outcome.status == "refused"
    assert {f["rule"] for f in outcome.findings} == {"pack_catalog_collision"}
    assert dest.read_text(encoding="utf-8") == "i am a file, not a directory"


def test_custom_dest_outside_added_root_is_refused(tmp_path: Path) -> None:
    """A custom --dest outside packs/added/ must be refused, not silently
    allowed -- _existing_manifests only ever scans packs/added for later
    dependency/conflict checks, so a pack added elsewhere would become
    invisible to every subsequent add's selection validation."""
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    registry = _one_record_registry(
        record_dict(
            pack_id="acme.kpi",
            source="packs/reference/kpi",
            content_hash=content_digest(pack_dir),
        )
    )
    outside_dest = repo / "somewhere-else" / "kpi"
    outcome = add_pack(repo, registry, "acme.kpi", dest=str(outside_dest))
    assert outcome.status == "refused"
    assert {f["rule"] for f in outcome.findings} == {"pack_catalog_containment"}
    assert not outside_dest.exists()


def test_custom_dest_name_under_added_root_is_discoverable_later(
    tmp_path: Path,
) -> None:
    """A custom --dest that DOES stay nested under packs/added/ must still
    be discovered by a later add's dependency/conflict check."""
    repo = build_test_repo(tmp_path)
    base_dir = write_pack(repo, "packs/reference/base", pack_id="acme.base")
    base_registry = _one_record_registry(
        record_dict(
            pack_id="acme.base",
            source="packs/reference/base",
            content_hash=content_digest(base_dir),
        )
    )
    custom_dest = repo / "packs/added/custom-name"
    outcome = add_pack(repo, base_registry, "acme.base", dest=str(custom_dest))
    assert outcome.status == "added"
    assert (custom_dest / "seshat-pack.yaml").is_file()

    dependent_dir = write_pack(
        repo,
        "packs/reference/dependent",
        pack_id="acme.dependent",
        requires=("acme.base",),
    )
    dependent_registry = _one_record_registry(
        record_dict(
            pack_id="acme.dependent",
            source="packs/reference/dependent",
            content_hash=content_digest(dependent_dir),
        )
    )
    outcome2 = add_pack(repo, dependent_registry, "acme.dependent")
    assert outcome2.status == "added"
