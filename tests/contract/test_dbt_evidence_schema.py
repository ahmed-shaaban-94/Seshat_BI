"""Contract tests for normalized dbt run evidence."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
FEATURE_SCHEMA = (
    ROOT / "specs/133-activate-dbt-mvp/contracts/dbt-run-evidence.schema.json"
)
RUNTIME_SCHEMA = ROOT / "schemas/dbt-run-evidence.schema.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_runtime_evidence_schema_matches_the_approved_contract() -> None:
    assert _load(RUNTIME_SCHEMA) == _load(FEATURE_SCHEMA)


def test_evidence_schema_is_closed_and_authority_is_fixed() -> None:
    schema = _load(RUNTIME_SCHEMA)

    assert schema["additionalProperties"] is False
    assert schema["properties"]["authority"]["const"] == "derived-evidence-only"
    assert schema["properties"]["outcome"]["enum"] == [
        "pass",
        "blocked",
        "failed",
        "unavailable",
    ]
    assert schema["properties"]["seshat_exit_code"] == {
        "type": "integer",
        "minimum": 0,
        "maximum": 4,
    }
    assert set(schema["required"]) >= {
        "mapping_path",
        "mapping_revision",
        "elapsed_seconds",
        "plan_digest",
        "project_fingerprint",
        "parity",
        "artifacts",
        "readiness_effect",
    }
