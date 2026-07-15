from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from seshat import impact_map
from seshat.cli import main

pytestmark = pytest.mark.integration

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "impact_map"
_MACHINE = ".seshat-output/impact-map/impact-map.json"
_HUMAN = ".seshat-output/impact-map/impact-map.md"


def _fixture(tmp_path: Path, family: str) -> Path:
    shutil.copytree(_FIXTURES / "_base", tmp_path, dirs_exist_ok=True)
    shutil.copytree(_FIXTURES / family, tmp_path, dirs_exist_ok=True)
    return tmp_path


def _run(root: Path, *extra: str) -> int:
    return main(
        [
            "impact-map",
            "--repo",
            str(root),
            "--decision",
            "naming.metric_alpha",
            *extra,
        ]
    )


def _human_document(text: str) -> dict[str, object]:
    payload = text.split("```json\n", 1)[1].rsplit("\n```", 1)[0]
    return json.loads(payload)


def test_human_machine_parity(tmp_path: Path) -> None:
    root = _fixture(tmp_path, "transitive")
    assert _run(root) == 0
    machine = json.loads((root / _MACHINE).read_text(encoding="utf-8"))
    human = _human_document((root / _HUMAN).read_text(encoding="utf-8"))
    assert human == machine


def test_byte_determinism(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _fixture(tmp_path, "transitive")
    monkeypatch.setattr(
        impact_map, "_generated_at", lambda _value: "2026-07-15T00:00:00Z"
    )
    assert _run(root) == 0
    first = (root / _MACHINE).read_bytes()
    assert _run(root) == 0
    assert (root / _MACHINE).read_bytes() == first


def test_disclosure_blocks_write(tmp_path: Path) -> None:
    root = _fixture(tmp_path, "no_leak")
    assert _run(root) == 1
    assert not (root / _MACHINE).exists()
    assert not (root / _HUMAN).exists()


def test_contained_write(tmp_path: Path) -> None:
    root = _fixture(tmp_path, "direct")
    assert _run(root, "--output", "mappings/impact-map.json") == 2
    assert not (root / "mappings/impact-map.json").exists()
    assert not (root / _HUMAN).exists()
