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


# A safe ``table`` is a single path segment: non-empty, not a traversal token,
# and free of any path separator. Kept as a data-driven predicate set so the
# guard stays a flat ``any(...)`` rather than a multi-branch boolean.
_UNSAFE_TABLE_TOKENS = frozenset({"", ".", ".."})
_PATH_SEPARATORS = ("/", "\\")

# Characters that are invalid in a Windows filename (and a portable red flag on
# any OS). A name containing one cannot be created as a directory, so it must be
# refused as a documented Stage1ScaffoldError rather than crash at mkdir.
_INVALID_FILENAME_CHARS = frozenset(':*?"<>|')

# Windows reserved DEVICE names: these match the identifier charset yet fail at
# directory creation on Windows (case-insensitively, with or without an
# extension). Compared on the pre-extension stem, lowercased.
_WINDOWS_RESERVED_NAMES = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"com{i}" for i in range(1, 10)}
    | {f"lpt{i}" for i in range(1, 10)}
)


def _is_unsafe_table(table: str) -> bool:
    """True when ``table`` is not a safe, portably-createable path segment."""
    if table in _UNSAFE_TABLE_TOKENS:
        return True
    if any(sep in table for sep in _PATH_SEPARATORS):
        return True
    if any(char in _INVALID_FILENAME_CHARS for char in table):
        return True
    stem = table.split(".", 1)[0].lower()
    return stem in _WINDOWS_RESERVED_NAMES


def _validate_table(table: str) -> str:
    """Return ``table`` if it is a safe single path segment, else raise.

    Rejects traversal tokens, path separators, characters invalid in a filename,
    and Windows reserved device names -- all of which match the identifier
    charset but cannot be created as a directory, so they would otherwise crash
    at mkdir with an uncaught OSError instead of the documented refusal.
    """
    if _is_unsafe_table(table):
        raise Stage1ScaffoldError(
            f"unsafe table segment: {table!r} (must be a plain name -- no path "
            "separators, traversal, invalid filename characters, or Windows "
            "reserved device names)"
        )
    return table


def _guard_destination_within_root(root: Path, dest_dir: Path) -> None:
    """Refuse a destination that resolves outside ``root`` (symlink escape).

    If ``mappings`` or ``mappings/<table>`` is a directory symlink out of the
    repo, ``_write_if_absent`` would follow it and write outside ``--repo``.
    Resolve the destination and require it stay under ``root`` (mirrors
    ``workspace_init._validate_target``'s outside-root guard).
    """
    resolved = dest_dir.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        raise Stage1ScaffoldError(
            f"refusing to scaffold outside the repository: {dest_dir} resolves "
            f"to {resolved}, which is not under {root} (a symlinked mappings/ "
            "path component would escape --repo)"
        ) from None


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
    _guard_destination_within_root(root, dest_dir)
    written: list[str] = []
    kept: list[str] = []
    try:
        for name in _STAGE1_FILES:
            rel = f"mappings/{table}/{name}"
            if _write_if_absent(dest_dir / name, _materialized_bytes(name)):
                written.append(rel)
            else:
                kept.append(rel)
    except OSError as exc:
        # Backstop for any residual filesystem failure the name/destination
        # guards can't foresee (e.g. the Windows 260-char path limit): surface
        # the documented refusal, never an uncaught traceback.
        raise Stage1ScaffoldError(
            f"could not scaffold mappings/{table}/: {exc}"
        ) from exc
    notes = (
        f"fill mappings/{table}/source-profile.md (Table id, Row count, the "
        "Per-column profile table, the PK proof), then run `seshat next`",
    )
    return Stage1Report(written=tuple(written), kept=tuple(kept), notes=notes)
