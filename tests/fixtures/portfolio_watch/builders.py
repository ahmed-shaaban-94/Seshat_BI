"""Generic (Principle VII) test-fixture builders for Portfolio Watch (spec 131).

No worked-example specifics (billing codes, segments, PII column names, real
per-table grain keys) -- every scope/column/table name here is a generic
placeholder (``scope_alpha``, ``widget_id``, ...), never a C086/pharmacy
literal.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

DEFAULT_STAGES = (
    "source_ready",
    "mapping_ready",
    "silver_ready",
    "gold_ready",
    "semantic_model_ready",
    "dashboard_ready",
    "publish_ready",
)


def init_git_repo(root: Path) -> str:
    """Initialize a real git repo at ``root`` with one commit, so
    ``git rev-parse HEAD`` (the source_revision seam) succeeds. Returns the
    HEAD sha. ``root`` must already exist."""
    subprocess.run(
        ["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "t@example.com"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "commit.gpgsign", "false"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    (root / ".gitkeep").write_text("", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"], cwd=root, check=True, capture_output=True
    )
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def commit_all(root: Path, message: str = "update") -> None:
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", message], cwd=root, check=True, capture_output=True
    )


def write_readiness_status(
    root: Path,
    scope_dir: str,
    *,
    table: str | None = None,
    current_stage: str = "mapping_ready",
    stage_status: dict[str, str] | None = None,
    stage_blocking_reasons: dict[str, list[str]] | None = None,
    top_blocking_reasons: list[str] | None = None,
    next_action: str = "do the next thing",
    approvals: list[dict[str, str]] | None = None,
) -> Path:
    """Write a minimal, valid ``readiness-status.yaml`` for one scope. Every
    stage defaults to ``not_started`` with no evidence/blockers; override via
    ``stage_status`` / ``stage_blocking_reasons``."""
    stage_status = stage_status or {}
    stage_blocking_reasons = stage_blocking_reasons or {}
    top_blocking_reasons = top_blocking_reasons or []
    table_name = table or scope_dir

    lines = [f'table: "{table_name}"', f'current_stage: "{current_stage}"', "stages:"]
    for stage in DEFAULT_STAGES:
        status = stage_status.get(stage, "not_started")
        reasons = stage_blocking_reasons.get(stage, [])
        lines.append(f"  {stage}:")
        lines.append(f'    status: "{status}"')
        lines.append("    evidence: []")
        if reasons:
            lines.append("    blocking_reasons:")
            for reason in reasons:
                lines.append(f'      - "{reason}"')
        else:
            lines.append("    blocking_reasons: []")
    lines.append("evidence: []")
    if top_blocking_reasons:
        lines.append("blocking_reasons:")
        for reason in top_blocking_reasons:
            lines.append(f'  - "{reason}"')
    else:
        lines.append("blocking_reasons: []")
    if approvals:
        lines.append("approvals:")
        for entry in approvals:
            lines.append(f'  - stage: "{entry["stage"]}"')
            lines.append(f'    owner: "{entry["owner"]}"')
            lines.append(f'    at: "{entry.get("at", "2026-01-01")}"')
    else:
        lines.append("approvals: []")
    lines.append(f'next_action: "{next_action}"')

    path = root / "mappings" / scope_dir / "readiness-status.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_json_artifact(root: Path, scope_dir: str, filename: str, data: dict) -> Path:
    path = root / "mappings" / scope_dir / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def write_source_profile(root: Path, scope_dir: str) -> Path:
    path = root / "mappings" / scope_dir / "source-profile.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# baseline source profile\n", encoding="utf-8")
    return path


def drift_artifact(
    *,
    schema_version: str = "1.0",
    captured_at_revision: str | None = None,
    live_leg_available: bool = True,
    class_: str = "no_drift",
    measured: str = "0 findings",
    owner: str | None = None,
    items: list[dict] | None = None,
) -> dict:
    doc: dict = {
        "schema_version": schema_version,
        "captured_at_revision": captured_at_revision,
        "live_leg_available": live_leg_available,
        "class": class_,
        "measured": measured,
    }
    if owner is not None:
        doc["owner"] = owner
    if items is not None:
        doc["items"] = items
    return doc


def generic_artifact(
    *,
    schema_version: str = "1.0",
    captured_at_revision: str | None = None,
    class_: str = "pass",
    measured: str = "1 item checked",
    owner: str | None = None,
    items: list[dict] | None = None,
) -> dict:
    doc: dict = {
        "schema_version": schema_version,
        "captured_at_revision": captured_at_revision,
        "class": class_,
        "measured": measured,
    }
    if owner is not None:
        doc["owner"] = owner
    if items is not None:
        doc["items"] = items
    return doc
