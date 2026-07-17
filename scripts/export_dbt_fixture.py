"""Export a review-safe, allowlisted fixture from a pinned dbt manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

MANIFEST_V12 = "https://schemas.getdbt.com/dbt/manifest/v12.json"
DBT_VERSION = "1.12.0"
ALLOWED_NODE_FIELDS = (
    "unique_id",
    "resource_type",
    "name",
    "package_name",
    "original_file_path",
    "tags",
    "schema",
    "meta",
    "database",
    "alias",
    "relation_name",
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--list-output", type=Path, required=True)
    return parser


def _sanitize_node(unique_id: str, raw: object) -> dict[str, object]:
    node = _manifest_node(unique_id, raw)
    _validate_node_scope(unique_id, node)
    result = {field: node.get(field) for field in ALLOWED_NODE_FIELDS}
    result["depends_on"] = {"nodes": _dependencies(unique_id, node)}
    result["config"] = {"materialized": _materialization(unique_id, node)}
    return result


def _manifest_node(unique_id: str, raw: object) -> dict[str, object]:
    if not isinstance(raw, dict) or raw.get("unique_id") != unique_id:
        raise ValueError(f"invalid manifest node: {unique_id}")
    return raw


def _validate_node_scope(unique_id: str, node: dict[str, object]) -> None:
    if node.get("resource_type") not in {"model", "test"}:
        raise ValueError(f"unsupported manifest resource: {unique_id}")
    if node.get("package_name") != "seshat_bi":
        raise ValueError(f"foreign manifest package: {unique_id}")


def _dependencies(unique_id: str, raw: dict[str, object]) -> list[str]:
    depends_on = raw.get("depends_on")
    nodes = depends_on.get("nodes") if isinstance(depends_on, dict) else None
    if not isinstance(nodes, list) or not all(isinstance(item, str) for item in nodes):
        raise ValueError(f"invalid node dependencies: {unique_id}")
    return sorted(nodes)


def _materialization(unique_id: str, raw: dict[str, object]) -> str:
    config = raw.get("config")
    materialized = config.get("materialized") if isinstance(config, dict) else None
    if not isinstance(materialized, str) or not materialized:
        raise ValueError(f"invalid node materialization: {unique_id}")
    return materialized


def _manifest_payload(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("manifest must be a JSON object")
    return payload


def _validate_metadata(payload: dict[str, object]) -> None:
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError("manifest metadata is missing")
    if metadata.get("dbt_schema_version") != MANIFEST_V12:
        raise ValueError("manifest schema is not v12")
    if metadata.get("dbt_version") != DBT_VERSION:
        raise ValueError("manifest was not produced by dbt 1.12.0")


def _manifest_nodes(payload: dict[str, object]) -> dict[str, object]:
    raw_nodes = payload.get("nodes")
    if not isinstance(raw_nodes, dict):
        raise ValueError("manifest nodes are missing")
    return raw_nodes


def _is_selected(unique_id: object, raw: object) -> bool:
    if not isinstance(unique_id, str) or not unique_id.startswith(
        ("model.seshat_bi.", "test.seshat_bi.")
    ):
        return False
    tags = raw.get("tags") if isinstance(raw, dict) else None
    return isinstance(tags, list) and "seshat_table_retail_store_sales" in tags


def _selected_nodes(
    raw_nodes: dict[str, object],
) -> dict[str, dict[str, object]]:
    selected: dict[str, dict[str, object]] = {}
    for unique_id, raw in sorted(raw_nodes.items()):
        if _is_selected(unique_id, raw):
            selected[unique_id] = _sanitize_node(unique_id, raw)
    return selected


def _verify_counts(selected: dict[str, dict[str, object]]) -> None:
    models = sum(node["resource_type"] == "model" for node in selected.values())
    tests = sum(node["resource_type"] == "test" for node in selected.values())
    if (models, tests) != (8, 24):
        raise ValueError(
            f"expected 8 governed models and 24 tests, got {models}/{tests}"
        )


def _fixture(selected: dict[str, dict[str, object]]) -> dict[str, object]:
    return {
        "metadata": {
            "dbt_schema_version": MANIFEST_V12,
            "dbt_version": DBT_VERSION,
            "fixture_kind": "sanitized-pinned-parse",
        },
        "nodes": selected,
    }


def _write_fixture(path: Path, fixture: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(fixture, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_list(path: Path, selected: dict[str, dict[str, object]]) -> None:
    lines = (
        json.dumps({"unique_id": unique_id}, sort_keys=True) + "\n"
        for unique_id in selected
    )
    path.write_text("".join(lines), encoding="utf-8", newline="\n")


def main() -> int:
    args = _parser().parse_args()
    payload = _manifest_payload(args.manifest)
    _validate_metadata(payload)
    selected = _selected_nodes(_manifest_nodes(payload))
    _verify_counts(selected)
    _write_fixture(args.output, _fixture(selected))
    _write_list(args.list_output, selected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
