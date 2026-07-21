"""Ingest assets: raw_source_file -> bronze_table -> source_profile.

The ingest HEAD is pluggable by SOURCE MODE (issues #404 / #405): the same two
asset names serve every mode, with the SOURCE ADAPTER swapped behind them, so
``ASSET_ORDER`` / the job graph / the gate tail are frozen. The DEFAULT (CSV)
path is byte-identical to the pre-feature adapter.

* CSV mode (default): ``raw_source_file`` checks the landing file exists;
  ``bronze_table`` OWNS and (re)creates ``bronze.<table>`` from it.
* existing-bronze mode: there is no landing file by design, so
  ``raw_source_file`` records ``deferred`` (not ``failed`` -- it does NOT
  STOP-edge downstream, mirroring ``live_validate``'s deferred boundary), and
  ``bronze_table`` verifies the pre-loaded relation READ-ONLY. Zero Bronze
  writes.

The gated tail (``source_profile -> source_map -> silver -> ...``) is identical
for every mode and is NEVER bypassed.
"""

from __future__ import annotations

import os
from pathlib import Path

from dagster import AssetKey, asset

from ..evidence_writer import AssetOutcome
from . import halt, writer_for
from .sources import (
    CsvLandingAdapter,
    ExistingBronzeAdapter,
    resolve_source_mode,
)


def _landing_path(root: Path, table: str) -> Path:
    landing = os.environ.get("SESHAT_RAW_LANDING_DIR")
    base = Path(landing) if landing else root / "data" / "raw"
    return base / f"{table}.csv"


def _raw_source_file_asset(table: str, root: Path):
    @asset(name="raw_source_file", key_prefix=[table], group_name=table)
    def raw_source_file(context) -> None:
        writer = writer_for(context, root)
        base = dict(
            asset="raw_source_file",
            table=table,
            gate_command="n/a -- landing input",
            exit_code=None,
        )
        mode = resolve_source_mode()
        if mode != "csv":
            # existing-bronze (and any future non-CSV origin): no landing file
            # by design. `deferred` is honest -- it is NOT `failed`, so it does
            # not STOP-edge bronze_table (which reads the DB directly). Same
            # deferred-boundary pattern live_validate uses without creds.
            writer.record(
                AssetOutcome(
                    **base,
                    measured={"source_mode": mode},
                    outcome="deferred",
                    blocking_reason=(
                        f"{mode} mode: no raw landing file by design -- "
                        "bronze_table verifies the existing relation read-only"
                    ),
                    owner="data owner",
                )
            )
            return
        path = _landing_path(root, table)
        if not path.is_file():
            halt(
                writer,
                AssetOutcome(
                    **base,
                    measured={},
                    outcome="failed",
                    blocking_reason=(
                        f"raw landing file not found: {path.name} "
                        "(landing dir absent or empty)"
                    ),
                    owner="data owner",
                ),
            )
        writer.record(
            AssetOutcome(
                **base, measured={"bytes": path.stat().st_size}, outcome="materialized"
            )
        )

    return raw_source_file


def _bronze_asset(table: str, root: Path):
    @asset(
        name="bronze_table",
        key_prefix=[table],
        group_name=table,
        deps=[AssetKey([table, "raw_source_file"])],
    )
    def bronze_table(context) -> None:
        writer = writer_for(context, root)
        mode = resolve_source_mode()
        gate_command = (
            "load bronze (psycopg2 COPY)"
            if mode == "csv"
            else "verify existing bronze (read-only)"
        )
        base = dict(asset="bronze_table", table=table, gate_command=gate_command)

        def _halt_blocked(reason: str) -> None:
            halt(
                writer,
                AssetOutcome(
                    **base,
                    exit_code=None,
                    measured={},
                    outcome="blocked",
                    blocking_reason=reason,
                    owner="platform owner",
                ),
            )

        def _halt_failed(reason: str) -> None:
            halt(
                writer,
                AssetOutcome(
                    **base,
                    exit_code=None,
                    measured={},
                    outcome="failed",
                    blocking_reason=reason,
                    owner="table onboarder",
                ),
            )

        if mode == "csv":
            adapter = CsvLandingAdapter(root, _landing_path(root, table), _halt_blocked)
        else:
            adapter = ExistingBronzeAdapter(root, _halt_blocked, _halt_failed)
        prepared = adapter.prepare_bronze(table)
        writer.record(
            AssetOutcome(
                **base,
                # Byte-identity: CSV mode's exit_code stays 0 and measured stays
                # EXACTLY {"rows_loaded": rows}. existing-bronze uses exit_code
                # None (no command executed) with its own read-only measured.
                exit_code=0 if mode == "csv" else None,
                measured=prepared.measured,
                outcome=prepared.outcome,
            )
        )

    return bronze_table


def _source_profile_asset(table: str, root: Path):
    @asset(
        name="source_profile",
        key_prefix=[table],
        group_name=table,
        deps=[AssetKey([table, "bronze_table"])],
    )
    def source_profile(context) -> None:
        writer = writer_for(context, root)
        profile = root / "mappings" / table / "source-profile.md"
        base = dict(
            asset="source_profile",
            table=table,
            gate_command="n/a -- reads the committed source profile",
            exit_code=None,
        )
        if not profile.is_file():
            halt(
                writer,
                AssetOutcome(
                    **base,
                    measured={},
                    outcome="blocked",
                    blocking_reason=(
                        "committed source profile absent: "
                        f"mappings/{table}/source-profile.md "
                        "(Stage-1 onboarding not done)"
                    ),
                    owner="table onboarder",
                ),
            )
        writer.record(
            AssetOutcome(
                **base,
                measured={"profile": f"mappings/{table}/source-profile.md"},
                outcome="materialized",
            )
        )

    return source_profile


def build_ingest_assets(table: str, root: Path) -> list:
    return [
        _raw_source_file_asset(table, root),
        _bronze_asset(table, root),
        _source_profile_asset(table, root),
    ]
