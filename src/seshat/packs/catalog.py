"""Fetch -> verify -> existing validation -> explicit add (spec 128, US3).

The highest-risk slice of the catalog: the only place external pack content
crosses into the workspace. Every step is fail-closed -- on ANY finding
nothing is written and a disclosure-safe finding is returned (FR-010).

Flow (FR-007), each step reusing a shipped component, never re-implementing
one (RR-001..RR-004):

    unknown id            -> registry lookup (``registry.find``)
    incompatible registry  -> ``validator._compatibility_findings`` on the
                              REGISTRY-recorded ``compatibility`` (checked
                              before any content is fetched)
    containment / missing  -> ``artifact_identity.resolve_within``
    tamper (hash mismatch)  -> ``hashlib.sha256`` over the fetched directory
    schema-invalid content,
    incompatible core,
    declarative/authority/
    stage-order violations  -> ``validator.validate_pack`` (unchanged)
    disclosure (secrets)    -> ``disclosure.scan_disclosure`` (both inside
                              ``validate_pack`` AND explicitly over every
                              declared artifact/fixture file's content)
    dependency / conflict   -> ``validator.validate_selection`` against the
                              packs already added to the workspace
    workspace collision     -> destination existence check

A successful add's only effect is new, reviewable workspace content: no
activation state, no readiness promotion, no approval (FR-011..FR-013).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..artifact_identity import canonical_relative_path, resolve_within
from ..disclosure import scan_disclosure
from .model import PackManifest
from .registry import Registry, RegistryRecord, find
from .validator import _compatibility_findings, validate_pack, validate_selection

DEFAULT_ADDED_ROOT = "packs/added"
_MANIFEST_NAME = "seshat-pack.yaml"


def _finding(rule: str, locator: str, message: str) -> dict[str, str]:
    return {"rule": rule, "locator": locator, "message": message}


@dataclass(frozen=True)
class CatalogOutcome:
    """The result of one ``add`` attempt. ``status`` is either ``"added"`` or
    ``"refused"`` -- never partial: a refusal writes nothing (FR-010)."""

    status: str
    pack_id: str
    written: tuple[str, ...] = ()
    findings: tuple[dict[str, str], ...] = ()

    @property
    def added(self) -> bool:
        return self.status == "added"


def _refuse(pack_id: str, findings: list[dict[str, str]]) -> CatalogOutcome:
    return CatalogOutcome(status="refused", pack_id=pack_id, findings=tuple(findings))


def _iter_pack_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.rglob("*") if path.is_file())


def content_digest(directory: Path) -> str:
    """SHA-256 over every file in ``directory`` (relative path + bytes),
    sorted for a deterministic, order-independent digest. Any byte changed
    or any file added/removed/renamed inside the pack directory flips the
    digest (T019)."""
    digest = hashlib.sha256()
    for path in _iter_pack_files(directory):
        relative = path.relative_to(directory).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _resolve_pack_dir(
    root: Path, record: RegistryRecord
) -> tuple[Path | None, dict[str, str] | None]:
    try:
        pack_dir = resolve_within(root, record.source)
    except ValueError:
        return None, _finding(
            "pack_catalog_containment",
            f"registry:{record.id}",
            "pack source escapes the workspace or registry root",
        )
    if not pack_dir.is_dir() or not (pack_dir / _MANIFEST_NAME).is_file():
        return None, _finding(
            "pack_catalog_missing_content",
            f"registry:{record.id}",
            f"pack source is missing or dangling: {record.source}",
        )
    return pack_dir, None


def _text_document(path: Path) -> Any:
    """Best-effort structured read for the explicit disclosure pass: YAML
    files are parsed (so secret/PII keys are checked by name); anything else
    is wrapped as a single string value (so connection-string and
    absolute-path patterns are still checked)."""
    import yaml

    if path.suffix.lower() in (".yaml", ".yml"):
        try:
            parsed = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError):
            return None
        return parsed
    try:
        return {"content": path.read_text(encoding="utf-8-sig")}
    except (OSError, UnicodeDecodeError):
        return None


def _disclosure_findings(
    pack_dir: Path, manifest_relative: str
) -> list[dict[str, str]]:
    """Explicit disclosure pass over every file the pack directory contains
    (RR-004). ``validate_pack`` already scans the manifest MAPPING; this
    additionally scans declared artifact/fixture file CONTENT, which
    ``validate_pack`` does not read."""
    findings: list[dict[str, str]] = []
    for path in _iter_pack_files(pack_dir):
        relative = path.relative_to(pack_dir).as_posix()
        if relative == _MANIFEST_NAME:
            continue  # already scanned inside validate_pack
        document = _text_document(path)
        if document is None:
            continue
        result = scan_disclosure(document)
        findings.extend(
            _finding(
                "pack_catalog_disclosure",
                f"{manifest_relative}#{relative}:{item['locator']}",
                item["message"],
            )
            for item in result["findings"]
        )
    return findings


def _existing_manifests(root: Path, added_root: str) -> list[PackManifest]:
    added_dir = root / added_root
    if not added_dir.is_dir():
        return []
    manifests: list[PackManifest] = []
    for manifest_path in sorted(added_dir.rglob(_MANIFEST_NAME)):
        relative = canonical_relative_path(root, manifest_path)
        manifest, findings = validate_pack(root, relative)
        if manifest is not None and not findings:
            manifests.append(manifest)
    return manifests


def _selection_findings_for(
    new_manifest: PackManifest, existing: list[PackManifest]
) -> list[dict[str, str]]:
    all_findings = validate_selection([*existing, new_manifest])
    needle_id = new_manifest.pack_id
    needle_path = new_manifest.manifest_path
    return [
        finding
        for finding in all_findings
        if needle_path in finding["locator"] or needle_id in finding["message"]
    ]


def _dest_dir(
    root: Path, record: RegistryRecord, dest: Path | str | None
) -> Path | None:
    if dest is not None:
        try:
            return resolve_within(root, dest)
        except ValueError:
            return None
    short = record.id.rsplit(".", 1)[-1]
    try:
        return resolve_within(root, Path(DEFAULT_ADDED_ROOT) / short)
    except ValueError:
        return None


def _write_pack(pack_dir: Path, dest_dir: Path) -> list[str]:
    written: list[str] = []
    for path in _iter_pack_files(pack_dir):
        relative = path.relative_to(pack_dir)
        target = dest_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        written.append(str(target))
    return written


def add_pack(
    repo_root: Path | str,
    registry: Registry,
    pack_id: str,
    *,
    dest: Path | str | None = None,
    added_root: str = DEFAULT_ADDED_ROOT,
) -> CatalogOutcome:
    """Run the full fail-closed chain and, only on all-pass, add the
    verified declarative pack as a reviewable workspace change.

    Never creates activation state, never advances readiness, never grants
    approval (FR-011..FR-013): the only effect of ``status == "added"`` is
    new file content under the destination directory.
    """
    root = Path(repo_root).resolve()

    record = find(registry, pack_id)
    if record is None:
        return _refuse(
            pack_id,
            [
                _finding(
                    "pack_catalog_unknown_id",
                    pack_id,
                    "pack id is not in the registry",
                )
            ],
        )

    incompatible = _compatibility_findings(
        record.compatibility, f"registry:{record.id}"
    )
    if incompatible:
        return _refuse(pack_id, incompatible)

    pack_dir, missing_or_escaped = _resolve_pack_dir(root, record)
    if pack_dir is None:
        return _refuse(pack_id, [missing_or_escaped])  # type: ignore[list-item]

    computed_hash = content_digest(pack_dir)
    if computed_hash != record.hash:
        return _refuse(
            pack_id,
            [
                _finding(
                    "pack_catalog_tamper",
                    f"registry:{record.id}",
                    f"fetched content hash does not match the recorded hash "
                    f"for {record.id!r}",
                )
            ],
        )

    manifest_relative = canonical_relative_path(root, pack_dir / _MANIFEST_NAME)
    manifest, content_findings = validate_pack(root, manifest_relative)
    if manifest is None or content_findings:
        return _refuse(pack_id, content_findings)

    disclosure_findings = _disclosure_findings(pack_dir, manifest_relative)
    if disclosure_findings:
        return _refuse(pack_id, disclosure_findings)

    existing = _existing_manifests(root, added_root)
    selection_findings = _selection_findings_for(manifest, existing)
    if selection_findings:
        return _refuse(pack_id, selection_findings)

    dest_dir = _dest_dir(root, record, dest)
    if dest_dir is None:
        return _refuse(
            pack_id,
            [
                _finding(
                    "pack_catalog_containment",
                    pack_id,
                    "destination path escapes the workspace",
                )
            ],
        )
    if dest_dir.exists() and any(dest_dir.iterdir()):
        return _refuse(
            pack_id,
            [
                _finding(
                    "pack_catalog_collision",
                    canonical_relative_path(root, dest_dir),
                    "pack content already exists at the destination; "
                    "add refuses to overwrite it silently",
                )
            ],
        )

    written = _write_pack(pack_dir, dest_dir)
    relative_written = tuple(canonical_relative_path(root, path) for path in written)
    return CatalogOutcome(status="added", pack_id=pack_id, written=relative_written)
