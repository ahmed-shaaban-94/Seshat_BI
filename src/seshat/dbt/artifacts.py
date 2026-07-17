"""Strict, allowlisted dbt artifact readers and execution cross-checks."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any

from seshat.dbt import DBT_CORE_VERSION
from seshat.dbt.contracts import (
    ExecutionPlan,
    ManifestNode,
    ManifestSummary,
    NodeResult,
    RunResultsSummary,
)

MANIFEST_V12 = "https://schemas.getdbt.com/dbt/manifest/v12.json"
RUN_RESULTS_V6 = "https://schemas.getdbt.com/dbt/run-results/v6.json"
_RUN_COMMANDS = frozenset({"build", "test", "show"})
_STATUSES = frozenset(
    {"success", "error", "fail", "skipped", "pass", "warn", "partial_success"}
)


class ArtifactIntegrityError(ValueError):
    """A dbt artifact cannot prove the governed execution facts."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ArtifactIntegrityError(f"artifact has duplicate JSON key {key}")
        result[key] = value
    return result


def _load_json(path: Path) -> tuple[dict[str, Any], str]:
    raw = _read_artifact(path)
    payload = _decode_artifact(raw, path.name)
    return _artifact_root(payload), hashlib.sha256(raw).hexdigest()


def _read_artifact(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ArtifactIntegrityError(f"artifact is unavailable: {path.name}") from exc


def _decode_artifact(raw: bytes, name: str) -> object:
    try:
        return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_object)
    except ArtifactIntegrityError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ArtifactIntegrityError(f"artifact is not valid JSON: {name}") from exc


def _artifact_root(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ArtifactIntegrityError("artifact root must be a JSON object")
    return payload


def _metadata(payload: dict[str, Any], schema: str, label: str) -> str:
    metadata = _metadata_object(payload, label)
    _require_artifact_schema(metadata, schema, label)
    return _require_dbt_version(metadata, label)


def _metadata_object(payload: dict[str, Any], label: str) -> dict[str, Any]:
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        raise ArtifactIntegrityError(f"{label} metadata is missing")
    return metadata


def _require_artifact_schema(metadata: dict[str, Any], schema: str, label: str) -> None:
    if metadata.get("dbt_schema_version") != schema:
        raise ArtifactIntegrityError(f"unsupported {label} schema")


def _require_dbt_version(metadata: dict[str, Any], label: str) -> str:
    version = metadata.get("dbt_version")
    if version != DBT_CORE_VERSION:
        raise ArtifactIntegrityError(f"{label} dbt version must be {DBT_CORE_VERSION}")
    return version


def _strings(value: Any, label: str) -> tuple[str, ...]:
    values = _string_list(value, label)
    _require_string_items(values, label)
    return tuple(values)


def _string_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ArtifactIntegrityError(f"manifest {label} must be a string array")
    return value


def _require_string_items(values: list[Any], label: str) -> None:
    if not all(isinstance(item, str) for item in values):
        raise ArtifactIntegrityError(f"manifest {label} must be a string array")


def _relative_source_path(value: Any) -> str:
    source_path = _source_path_string(value)
    path = PurePosixPath(source_path.replace("\\", "/"))
    _require_relative_source_path(path)
    return path.as_posix()


def _source_path_string(value: Any) -> str:
    if not isinstance(value, str):
        raise ArtifactIntegrityError("manifest original_file_path is invalid")
    if not value:
        raise ArtifactIntegrityError("manifest original_file_path is invalid")
    return value


def _require_relative_source_path(path: PurePosixPath) -> None:
    if path.is_absolute():
        raise ArtifactIntegrityError("manifest original_file_path must be relative")
    if ".." in path.parts:
        raise ArtifactIntegrityError("manifest original_file_path must be relative")


def _manifest_node(key: str, raw: Any) -> ManifestNode:
    node = _manifest_node_object(key, raw)
    _require_manifest_unique_id(key, node)
    fields = _manifest_string_fields(key, node)
    return ManifestNode(
        unique_id=key,
        resource_type=fields["resource_type"],
        name=fields["name"],
        package_name=fields["package_name"],
        original_file_path=_relative_source_path(node.get("original_file_path")),
        depends_on_nodes=_strings(_dependency_nodes(node), f"node {key} dependencies"),
        tags=_strings(node.get("tags", []), f"node {key} tags"),
        schema=fields["schema"],
        database=_optional_node_string(key, node, "database"),
        alias=_optional_node_string(key, node, "alias"),
        relation_name=_optional_node_string(key, node, "relation_name"),
        materialized=_node_materialization(key, node),
        meta=_manifest_meta(key, node),
    )


def _manifest_node_object(key: str, raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ArtifactIntegrityError(f"manifest node {key} is not an object")
    return raw


def _require_manifest_unique_id(key: str, node: dict[str, Any]) -> None:
    if node.get("unique_id") != key:
        raise ArtifactIntegrityError(
            f"manifest node dictionary key does not match unique_id for {key}"
        )


def _manifest_string_fields(key: str, node: dict[str, Any]) -> dict[str, str]:
    fields = {
        field: node.get(field)
        for field in ("resource_type", "name", "package_name", "schema")
    }
    if not all(isinstance(value, str) and value for value in fields.values()):
        raise ArtifactIntegrityError(f"manifest node {key} has invalid string fields")
    return fields


def _dependency_nodes(node: dict[str, Any]) -> Any:
    depends_on = node.get("depends_on")
    if isinstance(depends_on, dict):
        return depends_on.get("nodes")
    return None


def _optional_node_string(key: str, node: dict[str, Any], field: str) -> str | None:
    value = node.get(field)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ArtifactIntegrityError(f"manifest node {key} {field} is invalid")
    return value


def _node_materialization(key: str, node: dict[str, Any]) -> str | None:
    config = node.get("config")
    if config is None:
        return None
    if not isinstance(config, dict):
        raise ArtifactIntegrityError(f"manifest node {key} config is invalid")
    materialized = config.get("materialized")
    if not isinstance(materialized, str) or not materialized:
        raise ArtifactIntegrityError(f"manifest node {key} materialization is invalid")
    return materialized


def _manifest_meta(key: str, node: dict[str, Any]) -> dict[str, Any]:
    meta = node.get("meta", {})
    if not isinstance(meta, dict):
        raise ArtifactIntegrityError(f"manifest node {key} meta must be an object")
    return dict(meta)


def _manifest_nodes(raw_nodes: Any) -> dict[str, ManifestNode]:
    if not isinstance(raw_nodes, dict):
        raise ArtifactIntegrityError("manifest nodes must be an object")
    if not all(isinstance(key, str) for key in raw_nodes):
        raise ArtifactIntegrityError("manifest node keys must be strings")
    return {key: _manifest_node(key, value) for key, value in raw_nodes.items()}


def _semantic_manifest_digest(version: str, nodes: dict[str, ManifestNode]) -> str:
    semantic_payload = {
        "schema_uri": MANIFEST_V12,
        "dbt_version": version,
        "nodes": {
            key: {
                **asdict(nodes[key]),
                "depends_on_nodes": sorted(nodes[key].depends_on_nodes),
                "tags": sorted(nodes[key].tags),
            }
            for key in sorted(nodes)
        },
    }
    canonical = json.dumps(
        semantic_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def load_manifest(path: Path) -> ManifestSummary:
    """Load exact manifest v12 and discard all non-allowlisted fields."""

    payload, digest = _load_json(path)
    version = _metadata(payload, MANIFEST_V12, "manifest")
    nodes = _manifest_nodes(payload.get("nodes"))
    return ManifestSummary(
        schema_uri=MANIFEST_V12,
        dbt_version=version,
        sha256=digest,
        semantic_sha256=_semantic_manifest_digest(version, nodes),
        nodes=nodes,
        selected_unique_ids=tuple(sorted(nodes)),
    )


def _node_result(raw: Any) -> NodeResult:
    result = _result_object(raw)
    unique_id = _result_unique_id(result)
    return NodeResult(
        unique_id=unique_id,
        status=_result_status(result, unique_id),
        failures=_result_failures(result, unique_id),
        execution_seconds=_result_seconds(result, unique_id),
    )


def _result_object(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ArtifactIntegrityError("run-results entry must be an object")
    return raw


def _result_unique_id(result: dict[str, Any]) -> str:
    unique_id = result.get("unique_id")
    if not isinstance(unique_id, str):
        raise ArtifactIntegrityError("run-results unique_id is invalid")
    if not unique_id:
        raise ArtifactIntegrityError("run-results unique_id is invalid")
    return unique_id


def _result_status(result: dict[str, Any], unique_id: str) -> str:
    status = result.get("status")
    if not isinstance(status, str):
        raise ArtifactIntegrityError(f"run-results status is invalid for {unique_id}")
    normalized = status.lower()
    if normalized not in _STATUSES:
        raise ArtifactIntegrityError(f"run-results status is invalid for {unique_id}")
    return normalized


def _result_failures(result: dict[str, Any], unique_id: str) -> int | None:
    failures = result.get("failures")
    if failures is None:
        return None
    if isinstance(failures, bool):
        raise ArtifactIntegrityError(f"run-results failures is invalid for {unique_id}")
    if not isinstance(failures, int):
        raise ArtifactIntegrityError(f"run-results failures is invalid for {unique_id}")
    return failures


def _result_seconds(result: dict[str, Any], unique_id: str) -> Decimal:
    try:
        seconds = Decimal(str(result.get("execution_time")))
    except (InvalidOperation, ValueError) as exc:
        raise ArtifactIntegrityError(
            f"run-results execution time is invalid for {unique_id}"
        ) from exc
    if not seconds.is_finite():
        raise ArtifactIntegrityError(
            f"run-results execution time is invalid for {unique_id}"
        )
    if seconds < 0:
        raise ArtifactIntegrityError(
            f"run-results execution time is invalid for {unique_id}"
        )
    return seconds


def _run_command(payload: dict[str, Any]) -> str:
    args = payload.get("args")
    which = args.get("which") if isinstance(args, dict) else None
    if which not in _RUN_COMMANDS:
        raise ArtifactIntegrityError("run-results args.which is unsupported")
    return which


def _run_results(payload: dict[str, Any]) -> tuple[NodeResult, ...]:
    raw_results = payload.get("results")
    if not isinstance(raw_results, list):
        raise ArtifactIntegrityError("run-results results must be an array")
    return tuple(_node_result(raw) for raw in raw_results)


def _require_unique_results(results: tuple[NodeResult, ...]) -> None:
    ids = tuple(result.unique_id for result in results)
    if len(ids) != len(set(ids)):
        raise ArtifactIntegrityError("run-results contains duplicate unique IDs")


def load_run_results(path: Path) -> RunResultsSummary:
    """Load exact run-results v6 and drop messages and compiled content."""

    payload, digest = _load_json(path)
    version = _metadata(payload, RUN_RESULTS_V6, "run-results")
    which = _run_command(payload)
    results = _run_results(payload)
    _require_unique_results(results)
    return RunResultsSummary(
        schema_uri=RUN_RESULTS_V6,
        dbt_version=version,
        which=which,
        sha256=digest,
        results=results,
    )


def _require_no_outside_nodes(outside: set[str]) -> None:
    if outside:
        raise ArtifactIntegrityError(
            "run-results contains nodes outside accepted plan: "
            + ", ".join(sorted(outside))
        )


def _required_execution_ids(selected: set[str], command: str) -> set[str]:
    required = {
        "build": selected,
        "test": {item for item in selected if item.startswith("test.")},
    }
    return required.get(command, set())


def _require_no_missing_nodes(missing: set[str]) -> None:
    if missing:
        raise ArtifactIntegrityError(
            "run-results is missing planned nodes: " + ", ".join(sorted(missing))
        )


def cross_check_execution(plan: ExecutionPlan, results: RunResultsSummary) -> None:
    """Prove that result nodes are exactly allowed by the accepted plan."""

    selected = set(plan.selected_unique_ids)
    actual = {result.unique_id for result in results.results}
    _require_no_outside_nodes(actual - selected)
    _require_no_missing_nodes(_required_execution_ids(selected, results.which) - actual)
