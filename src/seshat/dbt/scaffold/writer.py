"""Materialize a scaffold plan to disk: per-file models + idempotent merges.

Per-table model files (``<layer>/<table>/*.sql`` + ``_models.yml``) are written
with the shared hardened non-destructive writer (``safe_write.write_if_absent``):
an existing file is always kept. ``selectors.yml`` and the shared
``models/sources/_sources.yml`` are instead MERGED idempotently -- ``dbt init``
already created ``selectors.yml`` with a bootstrap row, and ``_sources.yml`` is
shared across tables, so a blind write-if-absent would either skip the new table
or clobber another's rows. Both merges add only what is missing.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from seshat.safe_write import write_if_absent

from .model_plan import ModelSpec, ScaffoldPlan

_SELECTORS = "dbt/selectors.yml"
_SOURCES = "dbt/models/sources/_sources.yml"


def _yaml_bytes(document: dict) -> bytes:
    text = yaml.safe_dump(document, sort_keys=False, default_flow_style=False)
    return text.encode("utf-8")


def _load_document(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError):
        return {}
    return document if isinstance(document, dict) else {}


def _selector_row(selector: str) -> dict:
    return {
        "name": selector,
        "description": f"Governed shadow graph for the {selector} approved map.",
        "definition": {"method": "tag", "value": selector},
    }


def merge_selector(root: Path, selector: str) -> bool:
    """Add the ``seshat_table_<id>`` tag selector if absent; True when changed."""
    path = root / _SELECTORS
    document = _load_document(path)
    rows = document.get("selectors")
    rows = rows if isinstance(rows, list) else []
    if any(isinstance(row, dict) and row.get("name") == selector for row in rows):
        return False
    document["selectors"] = [*rows, _selector_row(selector)]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _yaml_bytes(document).decode("utf-8"), encoding="utf-8", newline="\n"
    )
    return True


def _source_entry(name: str, schema: str, tables: list[str]) -> dict:
    return {"name": name, "schema": schema, "tables": [{"name": t} for t in tables]}


def _gold_tables(plan: ScaffoldPlan) -> list[str]:
    dims = [dim.name for dim in plan.dimensions]
    return [plan.fact.name, *dims]


def merge_sources(root: Path, plan: ScaffoldPlan) -> bool:
    """Add the bronze landing source and the migration_gold oracle if absent."""
    path = root / _SOURCES
    document = _load_document(path)
    rows = document.get("sources")
    rows = rows if isinstance(rows, list) else []
    by_name = {row.get("name"): row for row in rows if isinstance(row, dict)}
    desired = {
        "bronze": _source_entry("bronze", "bronze", [plan.source_table]),
        "migration_gold": _source_entry("migration_gold", "gold", _gold_tables(plan)),
    }
    changed = False
    for name, entry in desired.items():
        if name not in by_name:
            rows = [*rows, entry]
            changed = True
    if not changed:
        return False
    document.setdefault("version", 2)
    document["sources"] = rows
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _yaml_bytes(document).decode("utf-8"), encoding="utf-8", newline="\n"
    )
    return True


def _model_dir(plan: ScaffoldPlan, model: ModelSpec) -> str:
    return f"dbt/models/{model.layer}/{plan.table_id}"


def write_model_file(root: Path, relative: str, text: str) -> bool:
    """Write one model artifact non-destructively; True when written."""
    return write_if_absent(root, relative, text.encode("utf-8"))
