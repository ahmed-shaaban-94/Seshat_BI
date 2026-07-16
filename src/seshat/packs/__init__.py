"""Governed local extension packs (spec 120, US5).

Packs are declarative, explicitly selected local YAML manifests plus content
artifacts. They extend supported knowledge categories (KPI templates, source
vocabularies, warehouse compatibility notes, regional policies, accessibility
guidance, dashboard blueprints) without executing code, changing stage order,
or acquiring any approval authority. The core product operates with zero
packs installed (FR-031); a validated selection is an input to one
projection, never hidden global state.
"""

from __future__ import annotations

from pathlib import Path


def resolve_schema_path(filename: str) -> Path:
    """Resolve a bundled JSON-schema file across install layouts.

    The canonical schemas live in the repo-root ``schemas/`` directory. The
    wheel force-includes them under this package (``seshat/packs/schemas/``)
    so a clean, non-editable install can still read them; an editable/source
    checkout has no packaged copy and falls back to the repo-root tree.

    ``pack validate`` and ``pack search``/``inspect``/``add`` all read a
    schema at runtime. Resolving against ``__file__``'s ``parents[3]`` alone
    (the previous approach) only worked in an editable install -- in a wheel
    install that path points at ``site-packages/..`` where no ``schemas/``
    directory exists, so the ``pack`` family crashed with ``FileNotFoundError``.
    """
    packaged = Path(__file__).with_name("schemas") / filename
    if packaged.is_file():
        return packaged
    source_tree = Path(__file__).resolve().parents[3] / "schemas" / filename
    if source_tree.is_file():
        return source_tree
    raise FileNotFoundError(
        f"packaged schema {filename!r} is missing from both the installed "
        f"package ({packaged}) and the source tree ({source_tree}); the wheel "
        f"force-include for schemas/ is broken -- reinstall or rebuild the package"
    )
