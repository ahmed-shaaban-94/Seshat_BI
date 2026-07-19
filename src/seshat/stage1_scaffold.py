"""Materialize the three Stage-1 blank templates into any workspace (#339).

The first governed action (Source Ready / Stage 1) requires a
template-conformant ``source-profile.md`` plus a ``readiness-status.yaml`` and
``source-map.yaml``. Those blank templates previously shipped only with the
development repository, so a bare ``pip install seshat-bi`` left a new user
with nothing to copy -- violating the portable operating contract's "Never
require the Seshat development repository for normal use".

``scaffold_source`` closes that gap by writing the three blanks into
``mappings/<table>/`` from bundled package data (wheel force-include; a
development checkout falls back to the repo ``templates/`` dir, mirroring
``seshat.governed_projects``). Only table-neutral blank templates ship
(constitution VII). Writes are per-file non-destructive: an existing file is
always kept, never overwritten. Pure stdlib -- no DB, no network.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

_SOURCE_ROOT = Path(__file__).resolve().parents[2]
_PACKAGED_ROOT = "stage1_templates"

# The three Stage-1 blank templates (issue #339). Exactly these -- the other
# ~60 templates stay dev-only (YAGNI + constitution VII).
_STAGE1_FILES: tuple[str, ...] = (
    "source-profile.md",
    "readiness-status.yaml",
    "source-map.yaml",
)

# source-profile.md carries one dev-repo relative link that dangles once the
# file is materialized under mappings/<table>/. Neutralize to bare text so the
# stub is self-contained. (Everything else is copied byte-for-byte.)
_BROKEN_LINK = "[ADR 0003](../docs/decisions/0003-mapping-artifact-location.md)"
_LINK_REPLACEMENT = "ADR 0003 (mapping-artifact-location)"


class Stage1ScaffoldError(ValueError):
    """Raised when ``table`` is not a safe single path segment."""


@dataclass(frozen=True)
class Stage1Report:
    """What one ``scaffold_source`` call did, per file, plus operator notes."""

    written: tuple[str, ...]
    kept: tuple[str, ...]
    notes: tuple[str, ...]


def _validate_table(table: str) -> str:
    """A safe single path segment: no separators, no traversal, non-trivial."""
    if not table or table in {".", ".."} or "/" in table or "\\" in table:
        raise Stage1ScaffoldError(
            f"unsafe table segment: {table!r} "
            "(must be a plain name, no path separators or traversal)"
        )
    return table


def _template_bytes(name: str) -> bytes:
    """One bundled template's bytes: wheel data first, dev checkout fallback."""
    packaged = files("seshat").joinpath(_PACKAGED_ROOT, name)
    if packaged.is_file():
        return packaged.read_bytes()
    source = _SOURCE_ROOT / "templates" / name
    if source.is_file():
        return source.read_bytes()
    raise FileNotFoundError(
        f"bundled Stage-1 template is missing: {name} "
        "(reinstall seshat-bi, or run from a development checkout)"
    )


def _materialized_bytes(name: str) -> bytes:
    """Template bytes with per-file materialization fixups applied."""
    data = _template_bytes(name)
    if name == "source-profile.md":
        return data.replace(
            _BROKEN_LINK.encode("utf-8"), _LINK_REPLACEMENT.encode("utf-8")
        )
    return data


def _write_if_absent(target: Path, data: bytes) -> bool:
    """Write one file; True when written, False when kept as-is."""
    if target.exists():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return True


def scaffold_source(repo_root: Path, table: str) -> Stage1Report:
    """Write the three Stage-1 blank templates into ``mappings/<table>/``.

    ``table`` must be a plain path segment (raises ``Stage1ScaffoldError``
    otherwise). Per-file non-destructive: an existing file is kept, never
    overwritten. Returns a ``Stage1Report`` of what was written vs kept.
    """
    table = _validate_table(table)
    root = Path(repo_root).resolve()
    dest_dir = root / "mappings" / table
    written: list[str] = []
    kept: list[str] = []
    for name in _STAGE1_FILES:
        rel = f"mappings/{table}/{name}"
        if _write_if_absent(dest_dir / name, _materialized_bytes(name)):
            written.append(rel)
        else:
            kept.append(rel)
    notes = (
        f"fill mappings/{table}/source-profile.md (Table id, Row count, the "
        "Per-column profile table, the PK proof), then run `seshat next`",
    )
    return Stage1Report(written=tuple(written), kept=tuple(kept), notes=notes)
