"""#404/#405: the CSV source path is byte-identical to the pre-feature adapter.

The refactor swaps a SOURCE ADAPTER behind the same two asset names; it must
not change one byte of a CSV-mode run's evidence. This test pins the exact
pre-feature record shapes for ``raw_source_file`` and ``bronze_table`` (the two
assets the source seam touches) and proves the CSV-mode ``measured`` dict is
EXACTLY ``{"rows_loaded": N}`` -- no ``source_mode`` key leaks in.

``green_repo`` sets no ``SESHAT_DAGSTER_SOURCE_MODE``, so this run resolves the
default CSV path exactly as an existing customer run does.
"""

from __future__ import annotations

from conftest import TABLE, stub_green_db
from dagster import materialize
from tower_bi_orchestration.assets import build_table_assets
from tower_bi_orchestration.evidence_writer import EvidenceWriter
from tower_bi_orchestration.jobs import THROUGH_GOLD_ASSETS

RUN_ID = "testrun-001"


def _through_gold(root):
    return [
        a
        for a in build_table_assets(TABLE, root)
        if a.key.path[-1] in THROUGH_GOLD_ASSETS
    ]


def test_csv_mode_ingest_records_are_the_prefeature_shape(green_repo, monkeypatch):
    # No source mode env set -> default CSV path (the existing customer run).
    monkeypatch.delenv("SESHAT_DAGSTER_SOURCE_MODE", raising=False)
    stub_green_db(monkeypatch)  # load_csv returns 2 rows

    result = materialize(_through_gold(green_repo))
    assert result.success is True

    records = {r["asset"]: r for r in EvidenceWriter(green_repo, RUN_ID).records()}

    raw = records["raw_source_file"]
    assert raw["outcome"] == "materialized"
    assert raw["gate_command"] == "n/a -- landing input"
    assert set(raw["measured"]) == {"bytes"}  # unchanged: only the byte count

    bronze = records["bronze_table"]
    assert bronze["outcome"] == "materialized"
    assert bronze["exit_code"] == 0
    assert bronze["gate_command"] == "load bronze (psycopg2 COPY)"
    # THE byte-identity assertion: EXACTLY the pre-feature measured dict.
    assert bronze["measured"] == {"rows_loaded": 2}
    assert "source_mode" not in bronze["measured"]
