"""Read-only, offline decision-change impact projection.

This module composes committed evidence without mutating decisions, approvals,
supersession pointers, or readiness state. It emits no numeric impact score and
never connects to a live data source or Power BI process.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from seshat import (
    decision_store,
    disclosure,
    impact_map_graph,
    readiness_classify,
    readiness_projection,
)
from seshat.cli import guards
from seshat.decision_gate import _FLOW_TO_SPINE, evidence_stale
from seshat.explorer import build as explorer_build
from seshat.impact_map_walk import walk_graph as _walk_graph

_GraphEdge = impact_map_graph.GraphEdge
_GraphNode = impact_map_graph.GraphNode
_ImpactGraph = impact_map_graph.ImpactGraph
_NodeSpec = impact_map_graph.NodeSpec
_norm = impact_map_graph._norm
_build_graph = impact_map_graph.build_graph
_new_node = impact_map_graph.new_node
_text_references = impact_map_graph.text_references


@dataclass(frozen=True)
class LoadedSubject:
    """Fail-closed, read-only input bundle for one impact-map subject."""

    repo_root: Path
    store: decision_store.Store
    decisions: tuple[dict[str, Any], ...]
    subject: dict[str, Any] | None
    scope: tuple[str, ...] = ()
    trigger: str | tuple[str, ...] | None = None
    critical: bool = False
    stale_evidence: tuple[str, ...] = ()
    blocking_condition: dict[str, str] | None = None


# The modules below are the existing authorities this projection composes. The
# tuple is intentionally import-backed: it documents the no-duplicate boundary
# without copying any of their rules or vocabularies into this module.
_REUSED_AUTHORITIES = (
    readiness_projection,
    readiness_classify,
    explorer_build,
    disclosure,
    guards,
    _FLOW_TO_SPINE,
)


def _blocked(
    root: Path,
    store: decision_store.Store,
    decisions: tuple[dict[str, Any], ...],
    blocking_condition: dict[str, str],
) -> LoadedSubject:
    return LoadedSubject(
        repo_root=root,
        store=store,
        decisions=decisions,
        subject=None,
        blocking_condition=blocking_condition,
    )


def _condition(kind: str, detail: str) -> dict[str, str]:
    return {"kind": kind, "detail": detail}


def _store_paths(root: Path) -> tuple[str, ...]:
    return tuple(path for path in decision_store.STORE_PATHS if (root / path).is_file())


def _subject_conflicts(
    subject: dict[str, Any], decisions: tuple[dict[str, Any], ...]
) -> list[tuple[str, str, list[str]]]:
    subject_type = subject.get("decision_type")
    subject_scope = set(decision_store.scope_keys(subject.get("scope")))
    return [
        conflict
        for conflict in decision_store.active_scope_conflicts(list(decisions))
        if conflict[0] == subject_type and conflict[1] in subject_scope
    ]


def _store_condition(store: decision_store.Store) -> dict[str, str] | None:
    if not store.present:
        return _condition("absent_store", "the canonical Decision Store is absent")
    if not store.problems:
        return None
    detail = "; ".join(
        f"{problem.locator}: {problem.message}" for problem in store.problems
    )
    return _condition("malformed_store", detail)


def _subject_condition(
    root: Path,
    subject: dict[str, Any],
    decisions: tuple[dict[str, Any], ...],
    decision_id: str,
) -> dict[str, str] | None:
    authority = decision_store.load_authority_map(root)
    approval_valid, approval_reason = decision_store.approval_is_valid(
        subject, authority
    )
    valid_status = subject.get("status") in ("approved", "superseded")
    if not valid_status or not approval_valid:
        detail = approval_reason or (
            f"{decision_id!r} is not a valid approved impact-map subject"
        )
        return _condition("invalid_subject", detail)
    conflicts = _subject_conflicts(subject, decisions)
    if not conflicts:
        return None
    decision_type, scope_key, ids = conflicts[0]
    detail = f"conflicting active {decision_type} decisions on {scope_key}: {ids}"
    return _condition("active_scope_conflict", detail)


def _change_trigger(
    subject: dict[str, Any],
    decisions: tuple[dict[str, Any], ...],
    stale: tuple[str, ...],
    preview: bool,
) -> str | tuple[str, ...] | None:
    triggers: list[str] = []
    superseded = subject.get("status") == "superseded" or any(
        decision.get("supersedes") == subject.get("id") for decision in decisions
    )
    if superseded:
        triggers.append("superseded")
    if stale:
        triggers.append("evidence_stale")
    if triggers:
        return triggers[0] if len(triggers) == 1 else tuple(triggers)
    return "preview" if preview else None


def load_subject(
    repo_root: Path | str,
    decision_id: str,
    *,
    preview: bool = False,
) -> LoadedSubject:
    """Load one approved decision and its trigger, failing closed as data.

    The function reads only the canonical Decision Store files and cited
    evidence identities. It never changes the store or readiness state.
    """

    root = Path(repo_root).resolve()
    store = decision_store.load_store(root, _store_paths(root))
    decisions = tuple(store.decisions())
    blocking_condition = _store_condition(store)
    if blocking_condition is not None:
        return _blocked(root, store, decisions, blocking_condition)

    subject = next(
        (decision for decision in decisions if decision.get("id") == decision_id),
        None,
    )
    if subject is None:
        return _blocked(
            root,
            store,
            decisions,
            _condition(
                "invalid_subject",
                f"{decision_id!r} is not a valid approved impact-map subject",
            ),
        )

    blocking_condition = _subject_condition(root, subject, decisions, decision_id)
    if blocking_condition is not None:
        return _blocked(root, store, decisions, blocking_condition)

    approval = subject.get("approval")
    stale = tuple(evidence_stale(root, approval) if isinstance(approval, dict) else [])
    trigger = _change_trigger(subject, decisions, stale, preview)
    if trigger is None:
        return _blocked(
            root,
            store,
            decisions,
            _condition(
                "invalid_subject",
                (
                    "the approved decision has no committed change trigger; "
                    "request preview"
                ),
            ),
        )

    return LoadedSubject(
        repo_root=root,
        store=store,
        decisions=decisions,
        subject=subject,
        scope=tuple(decision_store.scope_keys(subject.get("scope"))),
        trigger=trigger,
        critical=decision_store.is_critical(subject.get("decision_type")),
        stale_evidence=stale,
    )


def _generated_at(value: str | None) -> str:
    if value is not None:
        return value
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _empty_projection(
    generated_at: str, blocking_condition: dict[str, str]
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "subject": None,
        "supersession_chain": [],
        "affected": [],
        "incomplete_lineage": [],
        "cycles": [],
        "blocking_condition": blocking_condition,
        "generated_at": generated_at,
    }


_SCOPE_NODE_KINDS = {
    "kpis": frozenset({"metric_contract"}),
    "tables": frozenset({"source_mapping", "metric_contract", "readiness_evidence"}),
    "columns": frozenset({"source_mapping", "metric_contract"}),
}


def _artifact_scope_match(node: _GraphNode, wanted: str) -> bool:
    identities = {
        _norm(node.node_id),
        _norm(node.artifact_id),
        *(_norm(path) for path in node.evidence_paths),
    }
    return wanted in identities


def _scope_match(node: _GraphNode, kind: str, value: str) -> bool:
    wanted = _norm(value)
    leaf = _norm(re.split(r"[.:/\\]", value)[-1])
    if kind == "artifacts":
        return _artifact_scope_match(node, wanted)
    allowed_kinds = _SCOPE_NODE_KINDS.get(kind, frozenset())
    table_match = kind == "tables" and node.table == value
    token_match = wanted in node.tokens or leaf in node.tokens
    return node.kind in allowed_kinds and (table_match or token_match)


def _direct_nodes(
    graph: _ImpactGraph, scope: tuple[str, ...]
) -> tuple[set[str], list[dict[str, str]]]:
    direct: set[str] = set()
    warnings: list[dict[str, str]] = []
    for scope_key in scope:
        kind, _, value = scope_key.partition(":")
        matches = {
            node.node_id
            for node in graph.nodes.values()
            if _scope_match(node, kind, value)
        }
        if matches:
            direct.update(matches)
        else:
            warnings.append(
                {
                    "kind": "unresolved_scope_tag",
                    "locator": scope_key,
                    "detail": (
                        "no committed downstream artifact explicitly resolves "
                        "this scope tag"
                    ),
                }
            )
    return direct, warnings


def _table_projection_for(
    readiness: dict[str, Any], node: _GraphNode
) -> dict[str, Any] | None:
    if node.table is not None:
        match = next(
            (table for table in readiness["tables"] if table["table_id"] == node.table),
            None,
        )
        if match is not None:
            return match
    return next(
        (
            table
            for table in readiness["tables"]
            if any(
                path in evidence
                for path in node.evidence_paths
                for stage in table["stages"].values()
                for evidence in stage["evidence"]
            )
        ),
        None,
    )


def _stage_and_actions(
    readiness: dict[str, Any], node: _GraphNode
) -> tuple[list[str], list[dict[str, str]]]:
    table = _table_projection_for(readiness, node)
    if table is None:
        return [], []
    current = str(table["current_stage"])
    stage = _FLOW_TO_SPINE.get(current, current)
    stages = [stage] if stage in table["stages"] else []
    reasons = [str(reason) for reason in table.get("blocking_reasons", [])]
    if not reasons:
        reasons = ["readiness review"]
    actions: dict[str, dict[str, str]] = {}
    for reason in reasons:
        category, explanation, next_surface = readiness_classify.classify(reason)
        actions.setdefault(
            category,
            {
                "category": category,
                "explanation": explanation,
                "next_surface": next_surface,
            },
        )
    ordered = sorted(
        actions.values(),
        key=lambda action: readiness_classify.CATEGORY_RANK.index(action["category"]),
    )
    return stages, ordered


def _affected_entry(
    readiness: dict[str, Any],
    node: _GraphNode,
    relation: str,
    evidence_paths: list[str] | None = None,
) -> dict[str, Any]:
    stages, actions = _stage_and_actions(readiness, node)
    return {
        "artifact_id": node.artifact_id,
        "kind": node.kind,
        "relation": relation,
        "evidence_paths": evidence_paths or list(node.evidence_paths),
        "affected_stages": stages,
        "next_actions": actions,
    }


def _missing_evidence_warnings(loaded: LoadedSubject) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    for reference in loaded.stale_evidence:
        if explorer_build._evidence_state(loaded.repo_root, reference) == "missing":
            warnings.append(
                {
                    "kind": "missing_cited_evidence",
                    "locator": reference,
                    "detail": "the decision's cited evidence is missing or unreadable",
                }
            )
    return warnings


def _supersession_chain(
    loaded: LoadedSubject,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    assert loaded.subject is not None
    by_id = {
        str(decision["id"]): decision
        for decision in loaded.decisions
        if isinstance(decision.get("id"), str)
    }
    entries: list[dict[str, Any]] = []
    warnings: list[dict[str, str]] = []
    for relation in ("supersedes", "superseded_by"):
        current = loaded.subject
        visited = {str(current["id"])}
        while isinstance(current.get(relation), str):
            pointer = str(current[relation])
            resolved = pointer in by_id
            entries.append(
                {
                    "decision_id": pointer,
                    "relation": relation,
                    "resolved": resolved,
                }
            )
            if not resolved:
                warnings.append(
                    {
                        "kind": "dangling_supersession_pointer",
                        "locator": pointer,
                        "detail": (
                            f"the {relation} pointer does not resolve in the "
                            "Decision Store"
                        ),
                    }
                )
                break
            if pointer in visited:
                break
            visited.add(pointer)
            current = by_id[pointer]
    return entries, warnings


def build_impact_map(
    repo_root: Path | str,
    decision_id: str,
    *,
    preview: bool = False,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Compose one deterministic, read-only decision-change impact map."""

    timestamp = _generated_at(generated_at)
    loaded = load_subject(repo_root, decision_id, preview=preview)
    if loaded.blocking_condition is not None:
        return _empty_projection(timestamp, loaded.blocking_condition)

    graph = _build_graph(loaded.repo_root)
    if graph.problems:
        return _empty_projection(
            timestamp,
            {
                "kind": "unreadable_lineage_input",
                "detail": "unreadable lineage input: " + ", ".join(graph.problems),
            },
        )

    direct, warnings = _direct_nodes(graph, loaded.scope)
    warnings.extend(_missing_evidence_warnings(loaded))
    chain, chain_warnings = _supersession_chain(loaded)
    warnings.extend(chain_warnings)
    paths, walk_warnings, cycles = _walk_graph(loaded.repo_root, graph, direct)
    warnings.extend(walk_warnings)
    readiness = readiness_projection.build_readiness_projection(loaded.repo_root)
    affected = [
        _affected_entry(
            readiness,
            graph.nodes[node_id],
            "direct" if node_id in direct else "transitive",
            paths[node_id],
        )
        for node_id in paths
    ]
    affected.sort(key=lambda item: (item["relation"] != "direct", item["artifact_id"]))
    warnings = list(
        {
            (item["kind"], item["locator"], item["detail"]): item for item in warnings
        }.values()
    )
    warnings.sort(key=lambda item: (item["kind"], item["locator"]))
    trigger: str | list[str] | None = loaded.trigger
    if isinstance(trigger, tuple):
        trigger = list(trigger)
    assert loaded.subject is not None
    return {
        "schema_version": "1.0",
        "subject": {
            "decision_id": str(loaded.subject["id"]),
            "decision_type": str(loaded.subject["decision_type"]),
            "trigger": trigger,
            "is_preview": trigger == "preview",
            "critical": loaded.critical,
        },
        "supersession_chain": chain,
        "affected": affected,
        "incomplete_lineage": warnings,
        "cycles": cycles,
        "blocking_condition": None,
        "generated_at": timestamp,
    }


def serialize_impact_map(projection: dict[str, Any]) -> str:
    """Return the deterministic machine-readable JSON form."""

    return json.dumps(projection, indent=2, ensure_ascii=True) + "\n"


def render_impact_map(projection: dict[str, Any]) -> str:
    """Render the identical projection content as reviewable Markdown."""

    return (
        "# Decision Change Impact Map\n\n"
        "This is a read-only projection over committed evidence.\n\n"
        "```json\n"
        f"{serialize_impact_map(projection).rstrip()}\n"
        "```\n"
    )
