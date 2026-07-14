"""Optional before/after comparison over two Passport snapshots (US4).

Two Passport snapshots are comparable only when they share ``schema_version``
and ``scope`` and differ in ``source_revision`` (R5). When comparable, the
stage transitions and evidence verdicts are expressed in the Passport
verify vocabulary reused from ``seshat.passport``. When not comparable --
different scope, different schema, only one snapshot, or none -- the result
carries ``comparable: False`` and a truthful ``omitted_reason``; no delta is
ever fabricated (FR-020/FR-021, INV-5). Read-only: no snapshot or workspace
file is written.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..passport import verify_passport


def _empty(reason: str) -> dict[str, Any]:
    return {
        "comparable": False,
        "omitted_reason": reason,
        "before_revision": None,
        "after_revision": None,
        "stage_transitions": [],
        "evidence_verdicts": [],
    }


def _load_snapshot(path: Any) -> dict[str, Any] | None:
    try:
        text = Path(path).read_text(encoding="utf-8")
        document = json.loads(text)
    except (OSError, ValueError, TypeError):
        return None
    return document if isinstance(document, dict) else None


def _comparability_reason(before: dict[str, Any], after: dict[str, Any]) -> str | None:
    if before.get("schema_version") != after.get("schema_version"):
        return "snapshots have different schema_version"
    if before.get("scope") != after.get("scope"):
        return "snapshots have different scope"
    if before.get("source_revision") == after.get("source_revision"):
        return "snapshots record the same source_revision (nothing to compare)"
    return None


def _stage_transitions(
    before: dict[str, Any], after: dict[str, Any]
) -> list[dict[str, Any]]:
    before_tables = {
        entry.get("table_id"): entry
        for entry in (before.get("readiness") or [])
        if isinstance(entry, dict)
    }
    transitions: list[dict[str, Any]] = []
    for after_table in after.get("readiness") or []:
        if not isinstance(after_table, dict):
            continue
        table_id = after_table.get("table_id")
        before_table = before_tables.get(table_id)
        if not isinstance(before_table, dict):
            continue
        after_stages = after_table.get("stages", {})
        before_stages = before_table.get("stages", {})
        if not isinstance(after_stages, dict) or not isinstance(before_stages, dict):
            continue
        for stage, after_block in after_stages.items():
            before_block = before_stages.get(stage)
            if not isinstance(before_block, dict) or not isinstance(after_block, dict):
                continue
            before_status = before_block.get("status")
            after_status = after_block.get("status")
            if before_status != after_status:
                transitions.append(
                    {
                        "table_id": table_id,
                        "stage": stage,
                        "before_status": before_status,
                        "after_status": after_status,
                    }
                )
    return transitions


def build_comparison(
    repo_root: Path | str, snapshots: tuple[Any, Any] | None
) -> dict[str, Any]:
    """Always returns a dict (never ``None``) so absent/single/non-comparable
    inputs are each a truthful, testable outcome rather than a bare omission.
    ``build_showcase_bundle`` only stores this on the bundle when snapshots
    were actually supplied (see build.py); this function's own uniform
    return shape is what T024/T025 exercise directly.
    """
    if not snapshots:
        return _empty("no snapshots were supplied")
    if len(snapshots) != 2 or snapshots[0] is None or snapshots[1] is None:
        return _empty("only one snapshot was supplied")

    root = Path(repo_root).resolve()
    before_path, after_path = snapshots
    before = _load_snapshot(before_path)
    after = _load_snapshot(after_path)
    if before is None or after is None:
        return _empty("one or both supplied snapshot files could not be read")

    reason = _comparability_reason(before, after)
    if reason is None and (
        not isinstance(before.get("readiness", []), list)
        or not isinstance(after.get("readiness", []), list)
    ):
        reason = "one or both snapshots have a malformed 'readiness' member"
    if reason is not None:
        result = _empty(reason)
        result["before_revision"] = before.get("source_revision")
        result["after_revision"] = after.get("source_revision")
        return result

    verify_result = verify_passport(root, after)
    evidence_verdicts = [
        {"path": item.get("path"), "verdict": item.get("verification")}
        for item in verify_result.get("artifacts", [])
        if isinstance(item, dict)
    ]
    return {
        "comparable": True,
        "omitted_reason": None,
        "before_revision": before.get("source_revision"),
        "after_revision": after.get("source_revision"),
        "stage_transitions": _stage_transitions(before, after),
        "evidence_verdicts": evidence_verdicts,
    }
