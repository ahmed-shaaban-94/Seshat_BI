from __future__ import annotations

import ast
from pathlib import Path

import pytest

import seshat.impact_map as impact_map

pytestmark = pytest.mark.unit


def test_composer_imports_every_existing_authority() -> None:
    root = Path(__file__).resolve().parents[2]
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            root / "src/seshat/impact_map.py",
            root / "src/seshat/impact_map_graph.py",
            root / "src/seshat/impact_map_walk.py",
        )
    )
    required_uses = {
        "decision_store.load_store",
        "decision_store.scope_keys",
        "decision_store.is_critical",
        "decision_store.active_scope_conflicts",
        "artifact_identity.artifact_identity",
        "readiness_projection.build_readiness_projection",
        "readiness_classify.classify",
        "readiness_classify.CATEGORY_RANK",
        "explorer_build._lineage",
        "evidence_stale",
        "disclosure",
        "guards",
    }
    assert required_uses <= {token for token in required_uses if token in source}

    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "seshat"
        for alias in node.names
    }
    assert {
        "artifact_identity",
        "decision_store",
        "disclosure",
        "readiness_classify",
        "readiness_projection",
    } <= imports


def test_feature_adds_only_the_declared_projection_and_thin_surface() -> None:
    root = Path(__file__).resolve().parents[2]
    source_files = {
        path.relative_to(root).as_posix()
        for path in (root / "src/seshat").rglob("*impact_map*.py")
    }
    assert source_files == {
        "src/seshat/impact_map.py",
        "src/seshat/impact_map_graph.py",
        "src/seshat/impact_map_walk.py",
        "src/seshat/cli/commands/impact_map.py",
    }
    forbidden_public_types = {
        "DecisionStore",
        "ReadinessEngine",
        "LineageAuthority",
        "ApprovalSystem",
        "StatusModel",
    }
    assert forbidden_public_types.isdisjoint(vars(impact_map))


def test_graph_reuses_explorer_and_artifact_identity_node_vocabularies() -> None:
    root = Path(__file__).resolve().parents[2]
    source = (root / "src/seshat/impact_map_graph.py").read_text(encoding="utf-8")
    assert "explorer_build._lineage" in source
    assert 'f"warehouse:{gold_table}"' in source
    assert 'identity["artifact_id"]' in source
    assert "graph database" not in source.lower()
