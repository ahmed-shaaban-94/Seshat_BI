"""Regression tests for the `pack` family's runtime schema packaging.

`seshat pack validate|search|inspect|add` read two JSON schemas at call time.
Their canonical home is the repo-root `schemas/` directory (outside `src/`), so
a bare wheel would not ship them: the previous `Path(__file__).parents[3]`
resolution only worked in an editable/source install and crashed every clean
(wheel) install with `FileNotFoundError`. These tests lock BOTH halves of the
fix -- runtime resolution and the packaging declaration -- so neither can
silently regress.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from seshat.packs import resolve_schema_path

pytestmark = pytest.mark.unit

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PACK_SCHEMAS = (
    "seshat-extension-pack.schema.json",
    "seshat-pack-registry.schema.json",
)


@pytest.mark.parametrize("filename", _PACK_SCHEMAS)
def test_resolve_schema_path_points_at_an_existing_file(filename: str) -> None:
    resolved = resolve_schema_path(filename)
    assert resolved.is_file(), f"{filename} did not resolve to a readable file"


def test_resolve_schema_path_missing_file_raises_actionable_error() -> None:
    """A truly-absent schema must fail loud with an actionable message (naming
    both searched locations), never a bare downstream FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="force-include for schemas/ is broken"):
        resolve_schema_path("does-not-exist.schema.json")


def test_pyproject_ships_pack_schemas_into_the_package() -> None:
    """The wheel force-include (and sdist include) must carry both schemas under
    the package, so `resolve_schema_path` finds them in a non-editable install."""
    raw = (_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    document = tomllib.loads(raw)
    force_include = document["tool"]["hatch"]["build"]["targets"]["wheel"][
        "force-include"
    ]
    sdist_include = document["tool"]["hatch"]["build"]["targets"]["sdist"]["include"]
    for filename in _PACK_SCHEMAS:
        source = f"schemas/{filename}"
        destination = f"seshat/packs/schemas/{filename}"
        assert force_include.get(source) == destination, (
            f"{source} must force-include into the package as {destination}"
        )
        assert f"/{source}" in sdist_include, (
            f"{source} must be in the sdist include list so the wheel can "
            f"force-include it"
        )
