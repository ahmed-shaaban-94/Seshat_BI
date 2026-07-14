"""Registry-index schema contract tests (spec 128, T005).

Exercises the NEW registry-index contract directly, the same way
``test_ecosystem_schemas.py`` exercises the other ecosystem contracts: via
the shipped ``validate_json_contract`` utility (RR-005), never a second
validator.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from seshat.ecosystem_contracts import validate_json_contract

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads(
    (ROOT / "schemas/seshat-pack-registry.schema.json").read_text(encoding="utf-8")
)

_VALID_RECORD = {
    "id": "example.sales-kpis",
    "version": "1.0.0",
    "category": "kpi",
    "author": "Example Author",
    "source": "packs/reference/kpi-basic",
    "compatibility": "1.x",
    "hash": "0" * 64,
    "dependencies": [],
    "conflicts": [],
    "verification_state": "reviewed",
}


def _document(*records: dict) -> dict:
    return {"schema_version": "1.0", "records": list(records)}


def test_valid_reference_record_passes() -> None:
    assert validate_json_contract(_document(_VALID_RECORD), SCHEMA) == []


def test_specs_and_published_schema_are_identical() -> None:
    published = json.loads(
        (ROOT / "schemas/seshat-pack-registry.schema.json").read_text(encoding="utf-8")
    )
    authored = json.loads(
        (
            ROOT / "specs/128-pack-catalog/contracts/seshat-pack-registry.schema.json"
        ).read_text(encoding="utf-8")
    )
    assert published == authored


@pytest.mark.parametrize(
    "missing_field",
    [
        "id",
        "version",
        "category",
        "author",
        "source",
        "compatibility",
        "hash",
        "dependencies",
        "conflicts",
        "verification_state",
    ],
)
def test_record_missing_any_required_field_fails(missing_field: str) -> None:
    record = {k: v for k, v in _VALID_RECORD.items() if k != missing_field}
    assert validate_json_contract(_document(record), SCHEMA)


def test_numeric_verification_state_fails() -> None:
    record = {**_VALID_RECORD, "verification_state": 100}
    assert validate_json_contract(_document(record), SCHEMA)


def test_unrecognized_verification_state_fails() -> None:
    record = {**_VALID_RECORD, "verification_state": "trusted"}
    assert validate_json_contract(_document(record), SCHEMA)


def test_unknown_field_is_rejected() -> None:
    record = {**_VALID_RECORD, "popularity_rank": 1}
    assert validate_json_contract(_document(record), SCHEMA)


def test_duplicate_id_and_version_is_schema_legal_but_flagged_by_registry_py() -> None:
    # The SCHEMA itself does not forbid two records sharing id+version -- that
    # is a registry-level (cross-record) defect, detected by
    # ``seshat.packs.registry.load_registry`` (T008), not the shape contract.
    duplicate = _document(_VALID_RECORD, dict(_VALID_RECORD))
    assert validate_json_contract(duplicate, SCHEMA) == []
