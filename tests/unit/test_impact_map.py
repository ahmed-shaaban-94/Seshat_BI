from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from seshat import impact_map as impact_module
from seshat.impact_map import build_impact_map

pytestmark = pytest.mark.unit

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "impact_map"
_GENERATED_AT = "2026-07-15T00:00:00Z"


def _fixture(tmp_path: Path, family: str) -> Path:
    shutil.copytree(_FIXTURES / "_base", tmp_path, dirs_exist_ok=True)
    shutil.copytree(_FIXTURES / family, tmp_path, dirs_exist_ok=True)
    return tmp_path


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".seshat-output" not in path.parts
    }


def _build(root: Path, *, preview: bool = False) -> dict[str, object]:
    return build_impact_map(
        root,
        "naming.metric_alpha",
        preview=preview,
        generated_at=_GENERATED_AT,
    )


def test_direct_impact_superseded(tmp_path: Path) -> None:
    root = _fixture(tmp_path, "direct")
    projection = _build(root)

    direct = [
        item for item in projection["affected"] if item["kind"] == "metric_contract"
    ]
    assert len(direct) == 1
    assert direct[0]["relation"] == "direct"
    assert direct[0]["evidence_paths"]
    assert all((root / path).is_file() for path in direct[0]["evidence_paths"])
    assert direct[0]["affected_stages"] == ["semantic_model_ready"]
    assert direct[0]["next_actions"][0]["category"] == "approval"


def test_evidence_stale_trigger(tmp_path: Path) -> None:
    projection = _build(_fixture(tmp_path, "stale_evidence"))
    assert projection["subject"]["trigger"] == "evidence_stale"
    assert any(item["relation"] == "direct" for item in projection["affected"])


def test_no_state_written(tmp_path: Path) -> None:
    root = _fixture(tmp_path, "direct")
    before = _snapshot(root)
    _build(root)
    assert _snapshot(root) == before


def test_non_approved_subject_reported(tmp_path: Path) -> None:
    projection = _build(_fixture(tmp_path, "non_approved_subject"))
    assert projection["subject"] is None
    assert projection["blocking_condition"]["kind"] == "invalid_subject"
    assert projection["affected"] == []


def test_transitive_impact_with_edge_chain(tmp_path: Path) -> None:
    root = _fixture(tmp_path, "transitive")
    projection = _build(root)
    dashboard = [
        item for item in projection["affected"] if item["kind"] == "dashboard_binding"
    ]
    assert len(dashboard) == 1
    assert dashboard[0]["relation"] == "transitive"
    assert dashboard[0]["evidence_paths"][0].endswith("MetricAlpha.yaml")
    assert dashboard[0]["evidence_paths"][-1].endswith("visual-contract-binding-map.md")
    assert len(dashboard[0]["evidence_paths"]) >= 3


def test_unresolved_scope_tag_warns(tmp_path: Path) -> None:
    projection = _build(_fixture(tmp_path, "missing_ref"))
    warnings = projection["incomplete_lineage"]
    assert any(item["kind"] == "unresolved_scope_tag" for item in warnings)
    assert "unaffected" not in str(projection).lower()


def test_unfollowable_edge_warns(tmp_path: Path) -> None:
    projection = _build(_fixture(tmp_path, "missing_ref"))
    warnings = projection["incomplete_lineage"]
    assert any(item["kind"] == "unfollowable_edge" for item in warnings)
    assert not any(item["kind"] == "warehouse_table" for item in projection["affected"])


def test_affected_and_incomplete_disjoint(tmp_path: Path) -> None:
    projection = _build(_fixture(tmp_path, "incomplete_lineage"))
    affected = projection["affected"]
    warnings = projection["incomplete_lineage"]
    assert affected and warnings
    assert {item["artifact_id"] for item in affected}.isdisjoint(
        {item["locator"] for item in warnings}
    )
    metric = [item for item in affected if item["kind"] == "metric_contract"]
    assert len(metric) == 1
    assert metric[0]["relation"] == "direct"


def _cycle_graph(root: Path) -> impact_module._ImpactGraph:
    document = yaml.safe_load(
        (_FIXTURES / "cycle" / "graph.yaml").read_text(encoding="utf-8")
    )
    nodes = {
        item["node_id"]: impact_module._new_node(
            root,
            impact_module._NodeSpec(
                relative=item["evidence"],
                kind=item["kind"],
                node_id=item["node_id"],
                table="catalog",
                tokens=frozenset({item["node_id"].split(":")[-1]}),
            ),
        )
        for item in document["nodes"]
    }
    edges = tuple(
        impact_module._GraphEdge(item["from"], item["to"], item["evidence"])
        for item in document["edges"]
    )
    return impact_module._ImpactGraph(nodes=nodes, edges=edges)


def test_cycle_terminates_and_is_recorded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _fixture(tmp_path, "transitive")
    graph = _cycle_graph(root)
    monkeypatch.setattr(impact_module, "_build_graph", lambda _root: graph)
    projection = _build(root)
    assert projection["cycles"]
    assert projection["cycles"][0]["detail"] == "dependency cycle detected"
    assert len(projection["affected"]) <= len(graph.nodes)


def test_reference_matching_requires_boundaries() -> None:
    assert impact_module._text_references("gold.fact", "gold.fact")
    assert not impact_module._text_references("gold.fact_catalog", "gold.fact")
    assert not impact_module._text_references("net_sales", "sales")


def test_cycle_reached_through_a_visited_sibling_path_is_recorded(
    tmp_path: Path,
) -> None:
    root = _fixture(tmp_path, "transitive")
    metric = "metric:catalog:metric_alpha"
    warehouse = "warehouse:gold.fact_catalog"
    dashboard = "dashboard:mappings/catalog/design/visual-contract-binding-map.md"
    nodes = {
        metric: impact_module._new_node(
            root,
            impact_module._NodeSpec(
                relative="mappings/catalog/metrics/MetricAlpha.yaml",
                kind="metric_contract",
                node_id=metric,
            ),
        ),
        warehouse: impact_module._new_node(
            root,
            impact_module._NodeSpec(
                relative="warehouse/migrations/0001_create_gold_catalog.sql",
                kind="warehouse_table",
                node_id=warehouse,
            ),
        ),
        dashboard: impact_module._new_node(
            root,
            impact_module._NodeSpec(
                relative="mappings/catalog/design/visual-contract-binding-map.md",
                kind="dashboard_binding",
                node_id=dashboard,
            ),
        ),
    }
    graph = impact_module._ImpactGraph(
        nodes=nodes,
        edges=(
            impact_module._GraphEdge(
                metric, warehouse, nodes[warehouse].evidence_paths[0]
            ),
            impact_module._GraphEdge(
                metric, dashboard, nodes[dashboard].evidence_paths[0]
            ),
            impact_module._GraphEdge(
                warehouse, dashboard, nodes[dashboard].evidence_paths[0]
            ),
            impact_module._GraphEdge(
                dashboard, warehouse, nodes[warehouse].evidence_paths[0]
            ),
        ),
    )

    _paths, _warnings, cycles = impact_module._walk_graph(root, graph, {metric})

    assert {
        "nodes": [warehouse, dashboard, warehouse],
        "detail": "dependency cycle detected",
    } in cycles


def test_preview_no_mutation(tmp_path: Path) -> None:
    root = _fixture(tmp_path, "preview")
    before = _snapshot(root)
    projection = _build(root, preview=True)
    assert projection["subject"]["trigger"] == "preview"
    assert projection["subject"]["is_preview"] is True
    assert projection["affected"]
    assert _snapshot(root) == before


def test_supersession_chain_in_order(tmp_path: Path) -> None:
    projection = _build(_fixture(tmp_path, "dangling_pointer"))
    assert projection["supersession_chain"] == [
        {
            "decision_id": "naming.metric_alpha.v1",
            "relation": "supersedes",
            "resolved": True,
        },
        {
            "decision_id": "naming.metric_alpha.missing",
            "relation": "superseded_by",
            "resolved": False,
        },
    ]


def test_dangling_pointer_warns(tmp_path: Path) -> None:
    projection = _build(_fixture(tmp_path, "dangling_pointer"))
    warning = next(
        item
        for item in projection["incomplete_lineage"]
        if item["kind"] == "dangling_supersession_pointer"
    )
    assert warning["locator"] == "naming.metric_alpha.missing"


def test_absent_store_blocks(tmp_path: Path) -> None:
    projection = _build(_fixture(tmp_path, "absent_store"))
    assert projection["subject"] is None
    assert projection["blocking_condition"]["kind"] == "absent_store"
    assert projection["affected"] == []


def test_malformed_store_fails_closed(tmp_path: Path) -> None:
    root = _fixture(tmp_path, "malformed_store")
    before = _snapshot(root)
    projection = _build(root)
    assert projection["subject"] is None
    assert projection["blocking_condition"]["kind"] == "malformed_store"
    assert _snapshot(root) == before


def test_active_scope_conflict_surfaced(tmp_path: Path) -> None:
    projection = _build(_fixture(tmp_path, "conflict"), preview=True)
    assert projection["subject"] is None
    assert projection["blocking_condition"]["kind"] == "active_scope_conflict"


def test_missing_cited_evidence_warns(tmp_path: Path) -> None:
    root = _fixture(tmp_path, "stale_evidence")
    (root / "evidence/decision.md").unlink()
    projection = _build(root)
    assert any(
        item["kind"] == "missing_cited_evidence"
        for item in projection["incomplete_lineage"]
    )
    assert all(
        "evidence/decision.md" not in item["evidence_paths"]
        for item in projection["affected"]
    )
