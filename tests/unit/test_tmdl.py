import json
from pathlib import Path

import pytest

from retail.tmdl import top_level_blocks

GOLDEN_PBIP_ROOT = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "golden_pbip"
_MODEL = GOLDEN_PBIP_ROOT / "RetailGold.SemanticModel" / "definition" / "model.tmdl"
_RELS = GOLDEN_PBIP_ROOT / "RetailGold.SemanticModel" / "definition" / "relationships.tmdl"
_PBIR = GOLDEN_PBIP_ROOT / "RetailGold.Report" / "definition.pbir"


@pytest.mark.unit
def test_parser_reads_model_top_level_blocks() -> None:
    text = _MODEL.read_text(encoding="utf-8")
    blocks = top_level_blocks(text)
    assert "table Sales" in blocks
    assert "table Date" in blocks


@pytest.mark.unit
def test_model_pins_measure_and_displayfolder_and_no_slash() -> None:
    text = _MODEL.read_text(encoding="utf-8")
    assert "measure 'TotalSales' = SUM(Sales[Amount])" in text
    assert "displayFolder: Sales" in text
    assert "summarizeBy: sum" in text  # D5 warning anchor
    # D4 anchor: the measure body uses SUM, not a "/" division operator.
    assert "/" not in "measure 'TotalSales' = SUM(Sales[Amount])"


@pytest.mark.unit
def test_model_pins_gold_schema_and_parameterized_source() -> None:
    text = _MODEL.read_text(encoding="utf-8")
    assert 'Schema="gold"' in text  # D8 anchor
    assert "PostgreSQL.Database(Server, Database)" in text  # C1 anchor (identifiers)


@pytest.mark.unit
def test_model_pins_provisional_date_table_marker() -> None:
    # PROVISIONAL marker (spec §5.2 D7 / §13). Re-verify against the real PBIP from
    # Task M0.3 before M4 builds D7; if the real literal differs, update fixture + assert.
    text = _MODEL.read_text(encoding="utf-8")
    assert "annotation PBI_DateTable = true" in text


@pytest.mark.unit
def test_relationships_pins_bothdirections() -> None:
    # Intentional D6 VIOLATION used as the crossFilteringBehavior anchor.
    text = _RELS.read_text(encoding="utf-8")
    assert "crossFilteringBehavior: bothDirections" in text


@pytest.mark.unit
def test_pbir_is_bom_tolerant_and_uses_relative_bypath() -> None:
    # Contract: PBIR opened encoding="utf-8-sig" (BOM-tolerant). R1 anchor: byPath relative.
    data = json.loads(_PBIR.read_text(encoding="utf-8-sig"))
    path = data["datasetReference"]["byPath"]["path"]
    assert path == "../RetailGold.SemanticModel"
    assert not path[:1].isalpha() or path[1:2] != ":"  # not absolute "C:\..."
