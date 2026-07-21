"""The closed source-mode vocabulary for the ingest head (issues #404 / #405).

The medallion orchestration accepts more than one Bronze ORIGIN. The mode is
the seam that chooses which SOURCE ADAPTER satisfies the ingest head; the gated
tail (``source_profile -> source_map -> silver -> gold -> live_validate``) is
identical for every mode and is NEVER bypassed.

Two modes ship today (acceptance for #405: CSV + existing-Bronze with a
reusable extension point):

* ``csv`` -- the DEFAULT, unchanged: a raw ``<table>.csv`` lands, the loader
  owns and (re)creates ``bronze.<table>``.
* ``existing-bronze`` -- non-destructive DB-first: an already-loaded
  ``bronze.<table>`` is verified READ-ONLY as the satisfied upstream; nothing
  is dropped, truncated, recreated, reloaded, or otherwise mutated.

This module is stdlib-only and driver-free (no dagster, no psycopg2): it is the
one place the mode token is validated, so the CLI, the runner child env, and
the orchestration definitions all agree on the exact same closed set. Selection
travels as the ``SESHAT_DAGSTER_SOURCE_MODE`` environment variable -- the same
closed discovery seam ``SESHAT_DAGSTER_TABLES`` uses -- never as raw argv.
"""

from __future__ import annotations

CSV = "csv"
EXISTING_BRONZE = "existing-bronze"

# The DEFAULT mode. An absent / empty selection resolves here so existing runs
# stay byte-identical (no env var set => the pre-feature CSV path exactly).
DEFAULT_SOURCE_MODE = CSV

# The closed vocabulary the CLI and the child env may carry (mirrors
# ``ALLOWED_JOBS``: an unknown value is a hard usage error, never a silent
# fall-through to a destructive default).
SOURCE_MODES: frozenset[str] = frozenset({CSV, EXISTING_BRONZE})

# The env var carrying the selection to the orchestration child (parallels
# ``SESHAT_DAGSTER_TABLES``). Set ONLY when non-default so the CSV-path child
# environment is byte-identical to the pre-feature runner.
SOURCE_MODE_ENV = "SESHAT_DAGSTER_SOURCE_MODE"


def normalize_source_mode(value: str | None) -> str:
    """Resolve a raw selection to a member of :data:`SOURCE_MODES`.

    ``None`` or an empty/whitespace string resolves to :data:`DEFAULT_SOURCE_MODE`
    (the unchanged CSV path). Any other unrecognized value FAILS CLOSED with a
    ``ValueError`` naming the closed set -- an unknown mode must never silently
    become a destructive CSV reload.
    """
    if value is None or not value.strip():
        return DEFAULT_SOURCE_MODE
    candidate = value.strip()
    if candidate not in SOURCE_MODES:
        raise ValueError(
            f"source mode must be one of {sorted(SOURCE_MODES)}, got: {value!r}"
        )
    return candidate
