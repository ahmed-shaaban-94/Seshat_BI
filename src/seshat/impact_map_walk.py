"""Cycle-safe traversal of committed impact-map graph edges."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from seshat.explorer import build as explorer_build
from seshat.impact_map_graph import GraphEdge, ImpactGraph


@dataclass(frozen=True)
class _Traversal:
    source: str
    evidence_chain: tuple[str, ...]
    node_chain: tuple[str, ...]


@dataclass(frozen=True)
class _EdgeResult:
    traversal: _Traversal | None = None
    warning: dict[str, str] | None = None
    cycle: tuple[str, ...] | None = None


@dataclass
class _WalkState:
    paths: dict[str, list[str]]
    queue: list[_Traversal]
    expanded: set[tuple[str, tuple[str, ...]]]
    warnings: list[dict[str, str]]
    cycles: list[dict[str, Any]]
    cycle_keys: set[tuple[str, ...]]


def _ordered_unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _outgoing_edges(graph: ImpactGraph) -> dict[str, list[GraphEdge]]:
    outgoing: dict[str, list[GraphEdge]] = {}
    for edge in graph.edges:
        outgoing.setdefault(edge.source, []).append(edge)
    for edges in outgoing.values():
        edges.sort(key=lambda edge: (edge.target, edge.evidence))
    return outgoing


def _cycle_for(edge: GraphEdge, current: _Traversal) -> tuple[str, ...] | None:
    if edge.target not in current.node_chain:
        return None
    start = current.node_chain.index(edge.target)
    return (*current.node_chain[start:], edge.target)


def _unfollowable(edge: GraphEdge) -> dict[str, str]:
    return {
        "kind": "unfollowable_edge",
        "locator": f"{edge.source}->{edge.target}",
        "detail": "the committed lineage edge target or evidence is unavailable",
    }


def _inspect_edge(
    root: Path,
    graph: ImpactGraph,
    edge: GraphEdge,
    current: _Traversal,
) -> _EdgeResult:
    cycle = _cycle_for(edge, current)
    if cycle is not None:
        return _EdgeResult(cycle=cycle)
    target = graph.nodes.get(edge.target)
    if (
        target is None
        or explorer_build._evidence_state(root, edge.evidence) != "available"
    ):
        return _EdgeResult(warning=_unfollowable(edge))
    chain = _ordered_unique(
        [*current.evidence_chain, edge.evidence, *target.evidence_paths]
    )
    return _EdgeResult(
        traversal=_Traversal(
            source=edge.target,
            evidence_chain=tuple(chain),
            node_chain=(*current.node_chain, edge.target),
        )
    )


def _record_cycle(
    cycle: tuple[str, ...],
    cycle_keys: set[tuple[str, ...]],
    cycles: list[dict[str, Any]],
) -> None:
    if cycle in cycle_keys:
        return
    cycle_keys.add(cycle)
    cycles.append({"nodes": list(cycle), "detail": "dependency cycle detected"})


def _apply_result(state: _WalkState, result: _EdgeResult) -> None:
    if result.cycle is not None:
        _record_cycle(result.cycle, state.cycle_keys, state.cycles)
        return
    if result.warning is not None:
        state.warnings.append(result.warning)
        return
    assert result.traversal is not None
    next_item = result.traversal
    state.paths.setdefault(next_item.source, list(next_item.evidence_chain))
    key = (next_item.source, next_item.node_chain)
    if key in state.expanded:
        return
    state.expanded.add(key)
    state.queue.append(next_item)


def walk_graph(
    root: Path,
    graph: ImpactGraph,
    direct: set[str],
) -> tuple[dict[str, list[str]], list[dict[str, str]], list[dict[str, Any]]]:
    """Walk existing edges only, recording gaps and stopping cyclic branches."""

    paths: dict[str, list[str]] = {
        node_id: list(graph.nodes[node_id].evidence_paths) for node_id in sorted(direct)
    }
    queue = [
        _Traversal(node_id, tuple(paths[node_id]), (node_id,))
        for node_id in sorted(direct)
    ]
    state = _WalkState(
        paths=paths,
        queue=queue,
        expanded={(item.source, item.node_chain) for item in queue},
        warnings=[],
        cycles=[],
        cycle_keys=set(),
    )
    outgoing = _outgoing_edges(graph)

    while state.queue:
        current = state.queue.pop(0)
        for edge in outgoing.get(current.source, []):
            result = _inspect_edge(root, graph, edge, current)
            _apply_result(state, result)

    state.cycles.sort(key=lambda item: tuple(item["nodes"]))
    return state.paths, state.warnings, state.cycles
