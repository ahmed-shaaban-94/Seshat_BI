"""Committed-artifact graph construction for decision impact maps."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from seshat import artifact_identity
from seshat.explorer import build as explorer_build


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    artifact_id: str
    kind: str
    evidence_paths: tuple[str, ...]
    table: str | None
    tokens: frozenset[str]


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    evidence: str


@dataclass(frozen=True)
class ImpactGraph:
    nodes: dict[str, GraphNode]
    edges: tuple[GraphEdge, ...]
    problems: tuple[str, ...] = ()


@dataclass(frozen=True)
class NodeSpec:
    relative: str
    kind: str
    node_id: str | None = None
    table: str | None = None
    tokens: frozenset[str] = frozenset()


@dataclass(frozen=True)
class _MetricMetadata:
    name: str
    gold_table: str | None
    columns: tuple[str, ...]


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return None


def _read_yaml(path: Path) -> dict[str, Any] | None:
    text = _read_text(path)
    if text is None:
        return None
    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    return document if isinstance(document, dict) else None


def _norm(value: object) -> str:
    return re.sub(r"[^a-z0-9_.:/-]+", "_", str(value).strip().lower())


def _value_tokens(value: object) -> set[str]:
    tokens: set[str] = set()
    pending = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            pending.extend(current.values())
            continue
        if isinstance(current, list):
            pending.extend(current)
            continue
        if not isinstance(current, str):
            continue
        tokens.add(_norm(current))
        tokens.update(_norm(part) for part in re.split(r"[.:/\\]", current) if part)
    return {token for token in tokens if token}


def _path_table(relative: str) -> str | None:
    parts = Path(relative).parts
    if len(parts) >= 2 and parts[0] == "mappings":
        return parts[1]
    if len(parts) >= 2 and parts[0] == "powerbi":
        model = parts[1]
        if model.endswith(".SemanticModel"):
            return model.removesuffix(".SemanticModel").lower()
    return None


def new_node(root: Path, spec: NodeSpec) -> GraphNode:
    identity = artifact_identity.artifact_identity(root, spec.relative, kind=spec.kind)
    return GraphNode(
        node_id=spec.node_id or identity["artifact_id"],
        artifact_id=identity["artifact_id"],
        kind=spec.kind,
        evidence_paths=(spec.relative,),
        table=spec.table or _path_table(spec.relative),
        tokens=spec.tokens,
    )


def text_references(text: str, token: str) -> bool:
    reference_parts = re.findall(r"[a-z0-9_]+", token.lower())
    if not reference_parts:
        return False
    text_parts = re.findall(r"[a-z0-9_]+", text.lower())
    width = len(reference_parts)
    return any(
        text_parts[index : index + width] == reference_parts
        for index in range(len(text_parts) - width + 1)
    )


def _migration_for_table(root: Path, gold_table: str) -> str | None:
    for path in sorted(root.glob("warehouse/migrations/*.sql")):
        text = _read_text(path)
        if text is not None and text_references(text, gold_table):
            return path.relative_to(root).as_posix()
    return None


def _binding_metadata(document: dict[str, Any], raw: dict[str, Any]) -> _MetricMetadata:
    binds_to = document.get("binds_to")
    binding = binds_to if isinstance(binds_to, dict) else {}
    columns = binding.get("columns")
    return _MetricMetadata(
        name=str(document.get("name") or raw.get("label") or ""),
        gold_table=(str(binding["gold_table"]) if binding.get("gold_table") else None),
        columns=(
            tuple(str(value) for value in columns) if isinstance(columns, list) else ()
        ),
    )


def _metric_node(
    root: Path, raw: dict[str, Any]
) -> tuple[GraphNode | None, _MetricMetadata | None, str | None]:
    if raw.get("kind") == "input_defect":
        return None, None, str(raw.get("evidence") or raw.get("node_id"))
    if raw.get("kind") != "metric_contract":
        return None, None, None
    relative = str(raw["evidence"])
    document = _read_yaml(root / relative)
    if document is None:
        return None, None, relative
    node_id = str(raw["node_id"])
    table = node_id.split(":", 2)[1] if node_id.count(":") >= 2 else None
    tokens = _value_tokens(document)
    tokens.add(_norm(raw.get("label", "")))
    node = new_node(
        root,
        NodeSpec(
            relative=relative,
            kind="metric_contract",
            node_id=node_id,
            table=table,
            tokens=frozenset(tokens),
        ),
    )
    return node, _binding_metadata(document, raw), None


def _metric_nodes(
    root: Path, lineage: dict[str, list[dict[str, Any]]]
) -> tuple[dict[str, GraphNode], dict[str, _MetricMetadata], list[str]]:
    nodes: dict[str, GraphNode] = {}
    metadata: dict[str, _MetricMetadata] = {}
    problems: list[str] = []
    for raw in lineage["nodes"]:
        node, details, problem = _metric_node(root, raw)
        if problem is not None:
            problems.append(problem)
        if node is not None and details is not None:
            nodes[node.node_id] = node
            metadata[node.node_id] = details
    return nodes, metadata, problems


def _file_node(root: Path, path: Path, kind: str) -> GraphNode:
    relative = path.relative_to(root).as_posix()
    document = _read_yaml(path) if path.suffix == ".yaml" else None
    text = _read_text(path) or ""
    tokens = _value_tokens(document) if document is not None else set()
    tokens.update(_norm(part) for part in re.findall(r"[A-Za-z0-9_.]+", text))
    return new_node(
        root,
        NodeSpec(relative=relative, kind=kind, tokens=frozenset(tokens)),
    )


def _file_nodes(root: Path) -> dict[str, GraphNode]:
    nodes: dict[str, GraphNode] = {}
    families = (
        ("mappings/*/source-map.yaml", "source_mapping"),
        ("warehouse/migrations/*.sql", "warehouse_migration"),
        ("powerbi/**/*.tmdl", "semantic_artifact"),
        ("mappings/*/design/visual-contract-binding-map.md", "dashboard_binding"),
        ("mappings/*/readiness-status.yaml", "readiness_evidence"),
    )
    for pattern, kind in families:
        for path in sorted(root.glob(pattern)):
            node = _file_node(root, path, kind)
            nodes[node.node_id] = node
    return nodes


def _source_table(lineage: dict[str, list[dict[str, Any]]], node_id: str) -> str | None:
    source = next(
        (str(edge["from"]) for edge in lineage["edges"] if edge.get("to") == node_id),
        "",
    )
    return source.split(":", 2)[1] if source.count(":") >= 2 else None


def _warehouse_node(
    root: Path,
    lineage: dict[str, list[dict[str, Any]]],
    raw: dict[str, Any],
) -> GraphNode | None:
    if raw.get("kind") != "warehouse_table":
        return None
    node_id = str(raw["node_id"])
    gold_table = node_id.split(":", 1)[-1]
    relative = _migration_for_table(root, gold_table)
    if relative is None:
        return None
    return new_node(
        root,
        NodeSpec(
            relative=relative,
            kind="warehouse_table",
            node_id=node_id,
            table=_source_table(lineage, node_id),
            tokens=frozenset(_value_tokens(gold_table)),
        ),
    )


def _warehouse_nodes(
    root: Path, lineage: dict[str, list[dict[str, Any]]]
) -> dict[str, GraphNode]:
    nodes: dict[str, GraphNode] = {}
    for raw in lineage["nodes"]:
        node = _warehouse_node(root, lineage, raw)
        if node is not None:
            nodes[node.node_id] = node
    return nodes


def _nodes_of_kind(nodes: dict[str, GraphNode], kind: str) -> list[GraphNode]:
    return [node for node in nodes.values() if node.kind == kind]


def _node_text(root: Path, node: GraphNode) -> str:
    return _read_text(root / node.evidence_paths[0]) or ""


def _bound_warehouse_id(
    nodes: dict[str, GraphNode], gold_table: str | None
) -> str | None:
    if gold_table is None:
        return None
    warehouse_id = f"warehouse:{gold_table}"
    return warehouse_id if warehouse_id in nodes else None


def _warehouse_semantic_edge(
    warehouse_id: str | None,
    target: GraphNode,
    text: str,
) -> list[GraphEdge]:
    if warehouse_id is None:
        return []
    gold_table = warehouse_id.partition(":")[2]
    if not text_references(text, gold_table):
        return []
    return [GraphEdge(warehouse_id, target.node_id, target.evidence_paths[0])]


def _metric_semantic_edges(
    root: Path,
    nodes: dict[str, GraphNode],
    metric_id: str,
    metadata: _MetricMetadata,
) -> list[GraphEdge]:
    edges: list[GraphEdge] = []
    warehouse_id = _bound_warehouse_id(nodes, metadata.gold_table)
    for target in _nodes_of_kind(nodes, "semantic_artifact"):
        text = _node_text(root, target)
        if text_references(text, metadata.name):
            edges.append(GraphEdge(metric_id, target.node_id, target.evidence_paths[0]))
        edges.extend(_warehouse_semantic_edge(warehouse_id, target, text))
    return edges


def _semantic_dashboard_edges(
    root: Path,
    nodes: dict[str, GraphNode],
    metadata: _MetricMetadata,
) -> list[GraphEdge]:
    semantic_sources = [
        node
        for node in _nodes_of_kind(nodes, "semantic_artifact")
        if text_references(_node_text(root, node), metadata.name)
    ]
    dashboard_targets = [
        node
        for node in _nodes_of_kind(nodes, "dashboard_binding")
        if text_references(_node_text(root, node), metadata.name)
    ]
    return [
        GraphEdge(source.node_id, target.node_id, target.evidence_paths[0])
        for source in semantic_sources
        for target in dashboard_targets
    ]


def _readiness_edges(root: Path, nodes: dict[str, GraphNode]) -> list[GraphEdge]:
    sources = [node for node in nodes.values() if node.kind != "readiness_evidence"]
    targets = _nodes_of_kind(nodes, "readiness_evidence")
    return [
        GraphEdge(source.node_id, target.node_id, target.evidence_paths[0])
        for source in sources
        for target in targets
        if any(path in _node_text(root, target) for path in source.evidence_paths)
    ]


def _additional_edges(
    root: Path,
    nodes: dict[str, GraphNode],
    metric_metadata: dict[str, _MetricMetadata],
) -> list[GraphEdge]:
    edges = _readiness_edges(root, nodes)
    for metric_id, metadata in metric_metadata.items():
        if metric_id in nodes:
            edges.extend(_metric_semantic_edges(root, nodes, metric_id, metadata))
            edges.extend(_semantic_dashboard_edges(root, nodes, metadata))
    return edges


def build_graph(root: Path) -> ImpactGraph:
    lineage = explorer_build._lineage(root)
    metric_nodes, metric_metadata, problems = _metric_nodes(root, lineage)
    nodes = {**_file_nodes(root), **metric_nodes}
    nodes.update(_warehouse_nodes(root, lineage))
    edges = [
        GraphEdge(str(edge["from"]), str(edge["to"]), str(edge["evidence"]))
        for edge in lineage["edges"]
    ]
    edges.extend(_additional_edges(root, nodes, metric_metadata))
    unique = {(edge.source, edge.target, edge.evidence): edge for edge in edges}
    return ImpactGraph(
        nodes=nodes,
        edges=tuple(unique[key] for key in sorted(unique)),
        problems=tuple(sorted(set(problems))),
    )
