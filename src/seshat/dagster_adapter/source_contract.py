"""Read-only source-map column contract reader (issue #405).

The existing-Bronze source adapter must fail closed when a pre-loaded
``bronze.<table>`` does NOT match the approved source contract. The minimal,
honest contract-match (the advisor's scope call) is:

    the live Bronze columns SUPERSET the source columns the map references.

If the committed ``source-map.yaml`` names a ``source_name`` the existing
Bronze relation does not carry, the downstream silver build would break, so
the ingest head halts with a named blocker rather than proceeding into a
guaranteed-broken run.

This reader parses ONLY the two keys it needs from the committed
``mappings/<table>/source-map.yaml`` -- the ``columns[].source_name`` list --
never a general source-map parser. It is stdlib + lazy-PyYAML only (no dagster,
no DB driver), mirroring the gate readers, so it is unit-testable in the parent
environment. A missing map or missing/empty ``columns`` list returns an empty
set: the existence + non-empty checks in the adapter still apply, and the
superset check degrades to "no referenced columns to require" rather than
fabricating a match.
"""

from __future__ import annotations

from pathlib import Path


def referenced_source_columns(repo_root: Path, table: str) -> frozenset[str]:
    """The set of ``columns[].source_name`` the committed source-map references.

    Returns an empty frozenset when the map is absent, unreadable, malformed,
    or carries no ``columns`` list -- never raises, so the caller's own
    existence / non-empty gate stays the fail-closed authority.
    """
    source_map = Path(repo_root) / "mappings" / table / "source-map.yaml"
    if not source_map.is_file():
        return frozenset()
    try:
        text = source_map.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return frozenset()
    import yaml  # lazy: keeps this module driver- and dependency-light

    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError:
        return frozenset()
    if not isinstance(document, dict):
        return frozenset()
    columns = document.get("columns")
    if not isinstance(columns, list):
        return frozenset()
    names: set[str] = set()
    for entry in columns:
        if isinstance(entry, dict):
            source_name = entry.get("source_name")
            if isinstance(source_name, str) and source_name.strip():
                names.add(source_name.strip())
    return frozenset(names)
