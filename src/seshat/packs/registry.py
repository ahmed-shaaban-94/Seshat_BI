"""Static registry-index parsing and read-only search/inspect (spec 128).

Loads the tracked, reviewed registry index (``packs/registry/index.yaml`` by
default), schema-validates it against the NEW registry-INDEX contract
(``schemas/seshat-pack-registry.schema.json``), and builds frozen
registry-record models describing pack METADATA -- distinct from the pack's
own manifest (``seshat.packs.model.PackManifest``), which this module never
constructs or mutates.

This module never fetches pack content and never executes anything: it is
the read-only substrate for ``pack search`` and ``pack inspect`` (US1/US2).
Fetching, hash verification, and the existing pack validation live in
``seshat.packs.catalog`` (US3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..artifact_identity import canonical_relative_path, resolve_within
from ..ecosystem_contracts import validate_json_contract
from . import resolve_schema_path

# Categorical vocabulary only -- never a numeric score, rank, or percentage
# (hard-stop never_fabricate_a_confidence_score; FR-015).
VERIFICATION_STATES = ("reviewed", "unreviewed", "deprecated")

DEFAULT_REGISTRY_PATH = "packs/registry/index.yaml"

_SCHEMA_PATH = resolve_schema_path("seshat-pack-registry.schema.json")


class RegistryError(ValueError):
    """The registry index cannot be read or interpreted safely."""


def _finding(rule: str, locator: str, message: str) -> dict[str, str]:
    return {"rule": rule, "locator": locator, "message": message}


@dataclass(frozen=True)
class RegistryRecord:
    """One immutable metadata record ABOUT a pack (FR-002).

    Distinct from ``PackManifest``: this describes what the registry claims
    about a pack (identity, provenance, and a human-authored verification
    state); it is never the pack's own declarative content.
    """

    id: str
    version: str
    category: str
    author: str
    source: str
    compatibility: str
    hash: str
    dependencies: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    verification_state: str = "unreviewed"
    verification_evidence: tuple[str, ...] = ()

    @property
    def reviewed(self) -> bool:
        """True only when a named human reviewer committed ``reviewed``.

        Absence or an unrecognized value is NEVER treated as reviewed
        (FR-016; hard-stop never_self_grant_approval).
        """
        return self.verification_state == "reviewed"


@dataclass(frozen=True)
class Registry:
    """A parsed, schema-checked registry index.

    ``records`` holds only schema-valid, non-duplicated entries -- the
    catalog never silently prefers one of a duplicate id+version pair
    (FR-020), so both are excluded from ``records`` and reported in
    ``findings`` instead.
    """

    records: tuple[RegistryRecord, ...] = ()
    findings: tuple[dict[str, str], ...] = field(default_factory=tuple)


def _full_schema() -> dict[str, Any]:
    import json

    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def _record_schema() -> dict[str, Any]:
    return _full_schema()["properties"]["records"]["items"]


def _envelope_schema() -> dict[str, Any]:
    """The top-level shape only (``schema_version``, ``additionalProperties:
    false``, ``records`` as an array) -- NOT each record's item schema,
    which is validated per-record so one schema-invalid record is excluded
    and reported rather than failing the whole load (FR-002/FR-020)."""
    full = _full_schema()
    return {
        **full,
        "properties": {**full["properties"], "records": {"type": "array"}},
    }


def _read_index_text(resolved: Path, relative: str) -> str:
    try:
        return resolved.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise RegistryError(f"registry index is unreadable: {relative}") from exc
    except UnicodeDecodeError as exc:
        raise RegistryError(f"registry index is not valid UTF-8: {relative}") from exc


def _parse_index(raw: str, relative: str) -> dict[str, Any]:
    import yaml  # lazy: keep module import stdlib-light, matching packs.loader

    try:
        document = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise RegistryError(f"registry index is not valid YAML: {relative}") from exc
    if document is None:
        return {"schema_version": "1.0", "records": []}
    if not isinstance(document, dict):
        raise RegistryError(f"registry index is not a mapping: {relative}")
    return document


def _record_from_raw(raw: dict[str, Any]) -> RegistryRecord:
    return RegistryRecord(
        id=raw["id"],
        version=raw["version"],
        category=raw["category"],
        author=raw["author"],
        source=raw["source"],
        compatibility=raw["compatibility"],
        hash=raw["hash"],
        dependencies=tuple(raw.get("dependencies", [])),
        conflicts=tuple(raw.get("conflicts", [])),
        verification_state=(
            raw["verification_state"]
            if raw.get("verification_state") in VERIFICATION_STATES
            else "unreviewed"
        ),
        verification_evidence=tuple(raw.get("verification_evidence", [])),
    )


def _valid_records_and_findings(
    raw_records: list[Any],
) -> tuple[list[RegistryRecord], list[dict[str, str]]]:
    schema = _record_schema()
    valid: list[RegistryRecord] = []
    findings: list[dict[str, str]] = []
    for index, raw in enumerate(raw_records):
        locator = f"$.records[{index}]"
        if not isinstance(raw, dict):
            findings.append(
                _finding(
                    "pack_registry_invalid_record",
                    locator,
                    "registry record is not a mapping",
                )
            )
            continue
        errors = validate_json_contract(raw, schema, locator)
        if errors:
            findings.extend(
                _finding("pack_registry_invalid_record", locator, error)
                for error in errors
            )
            continue
        valid.append(_record_from_raw(raw))
    return valid, findings


def _partition_duplicates(
    records: list[RegistryRecord],
) -> tuple[list[RegistryRecord], list[dict[str, str]]]:
    """Split out id+version duplicates as a registry defect (FR-020).

    The catalog MUST NOT silently pick one of a duplicate pair, so BOTH
    copies are excluded from the usable set; only the defect is reported.
    """
    by_key: dict[tuple[str, str], list[RegistryRecord]] = {}
    for record in records:
        by_key.setdefault((record.id, record.version), []).append(record)

    usable: list[RegistryRecord] = []
    findings: list[dict[str, str]] = []
    for (pack_id, version), group in by_key.items():
        if len(group) > 1:
            findings.append(
                _finding(
                    "pack_registry_duplicate_record",
                    f"registry:{pack_id}@{version}",
                    f"duplicate registry record for {pack_id!r} at version "
                    f"{version!r}; the catalog will not silently choose one",
                )
            )
            continue
        usable.append(group[0])
    return usable, findings


def _resolve_registry_path(root: Path, registry_path: Path | str) -> Path | None:
    """Resolve the registry path within the workspace root. Returns ``None``
    for an absent file (FR-021's "empty registry" case); raises
    :class:`RegistryError` for a containment escape or a non-file path."""
    try:
        resolved = resolve_within(root, registry_path)
    except ValueError as exc:
        raise RegistryError("registry path resolves outside the workspace") from exc
    if not resolved.exists():
        return None
    if not resolved.is_file():
        raise RegistryError("registry path is not a file")
    return resolved


def _load_index_document(root: Path, resolved: Path) -> dict:
    relative = canonical_relative_path(root, resolved)
    document = _parse_index(_read_index_text(resolved, relative), relative)
    envelope_errors = validate_json_contract(document, _envelope_schema(), relative)
    if envelope_errors:
        # An incompatible/malformed ENVELOPE (wrong schema_version, an
        # unexpected top-level field, "records" not an array) fails the
        # whole load closed -- unlike a single bad record, which is excluded
        # and reported instead (RR-005; reuses the shared JSON-contract
        # validator, never a second schema check).
        raise RegistryError(
            f"registry index envelope is invalid: {relative}: {envelope_errors[0]}"
        )
    return document


def load_registry(
    repo_root: Path | str, registry_path: Path | str = DEFAULT_REGISTRY_PATH
) -> Registry:
    """Load and schema-check the static registry index.

    An absent registry file is FR-021's "empty registry" case: zero records,
    no error. A containment escape, an unreadable/non-UTF-8/non-mapping file,
    or invalid top-level shape fails closed with a disclosure-safe
    :class:`RegistryError`. A per-record schema failure or a duplicate
    id+version pair does NOT fail the whole load: the offending record(s)
    are excluded from ``records`` and reported in ``findings`` (FR-002,
    FR-020) so the rest of the registry stays usable.
    """
    root = Path(repo_root).resolve()
    resolved = _resolve_registry_path(root, registry_path)
    if resolved is None:
        return Registry()

    document = _load_index_document(root, resolved)
    valid_records, invalid_findings = _valid_records_and_findings(document["records"])
    usable_records, duplicate_findings = _partition_duplicates(valid_records)
    return Registry(
        records=tuple(usable_records),
        findings=tuple(invalid_findings) + tuple(duplicate_findings),
    )


def _matches_keyword(record: RegistryRecord, keyword: str) -> bool:
    needle = keyword.strip().lower()
    if not needle:
        return True
    haystacks = (record.id, record.category, record.author, record.compatibility)
    return any(needle in haystack.lower() for haystack in haystacks)


def search(
    registry: Registry, keyword: str | None = None, category: str | None = None
) -> tuple[RegistryRecord, ...]:
    """Keyword + category search over registry metadata only (FR-004, FR-005).

    Reads nothing but the already-parsed ``registry``; fetches and executes
    no pack content. An empty result is a normal, non-error outcome
    (FR-021, US1 scenario 3).
    """
    matches = [
        record
        for record in registry.records
        if _matches_keyword(record, keyword or "")
        and (category is None or record.category == category)
    ]
    return tuple(sorted(matches, key=lambda record: (record.id, record.version)))


def _version_key(version: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in version.split("."))
    except ValueError:
        return (0,)


def find(registry: Registry, pack_id: str) -> RegistryRecord | None:
    """Look up one pack id's usable registry record.

    Only records that passed schema validation and were not part of a
    duplicate id+version pair are considered (they are simply absent from
    ``registry.records``). When more than one version of the same id is
    present, the highest version is returned; this is a scope decision, not
    a semantic one -- the registry is expected to carry one active version
    per id (see plan.md assumptions).
    """
    matches = [record for record in registry.records if record.id == pack_id]
    if not matches:
        return None
    return max(matches, key=lambda record: _version_key(record.version))


def inspect(registry: Registry, pack_id: str) -> RegistryRecord | None:
    """Full metadata record for one pack id, or ``None`` for "not found"
    (FR-006). Reads only registry metadata; fetches no content."""
    return find(registry, pack_id)
