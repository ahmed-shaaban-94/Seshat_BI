"""Cross-cutting invariant tests (spec 131, T037).

(a) no numeric health/confidence/priority/quality score in any produced
artifact (INV-1, SC-003); (b) no DSN/secret/real-host string in the summary
or snapshot (SEC-002, SC-012); (c) no Principle-V ruling is originated --
every relayed seam names an owner (FR-021, SC-010); (d) summary assembly
changes no committed per-scope artifact (SC-008).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from seshat import portfolio_watch as pw
from tests.fixtures.portfolio_watch.builders import (
    drift_artifact,
    write_json_artifact,
    write_readiness_status,
    write_source_profile,
)

pytestmark = pytest.mark.unit

_SECRET_LIKE = ("postgresql://", "postgres://", "password=", "DATABASE_URL")


def _flatten_strings(document: Any) -> list[str]:
    if isinstance(document, str):
        return [document]
    if isinstance(document, dict):
        return [s for value in document.values() for s in _flatten_strings(value)]
    if isinstance(document, list):
        return [s for value in document for s in _flatten_strings(value)]
    return []


_FORBIDDEN_SCORE_KEY_HINTS = ("score", "confidence", "health", "quality_score")


def _assert_no_score_shaped_key(key: object) -> None:
    lowered = str(key).lower()
    assert not any(bad in lowered for bad in _FORBIDDEN_SCORE_KEY_HINTS), (
        f"score-shaped key found: {key}"
    )


def _check_dict_children(value: dict) -> None:
    for key, child in value.items():
        _assert_no_score_shaped_key(key)
        _assert_no_numeric_score(child)


def _check_list_children(value: list) -> None:
    for child in value:
        _assert_no_numeric_score(child)


def _assert_no_numeric_score(value: Any) -> None:
    if isinstance(value, float):
        raise AssertionError(f"bare float found: {value}")
    if isinstance(value, dict):
        _check_dict_children(value)
    if isinstance(value, list):
        _check_list_children(value)


def _build_repo(root: Path) -> None:
    write_readiness_status(
        root,
        "scope_alpha",
        current_stage="mapping_ready",
        stage_status={"source_ready": "pass", "mapping_ready": "blocked"},
        stage_blocking_reasons={"mapping_ready": ["mapping_ready approval is missing"]},
        top_blocking_reasons=["mapping_ready approval is missing"],
    )
    write_source_profile(root, "scope_alpha")
    write_json_artifact(
        root,
        "scope_alpha",
        "drift-findings.json",
        drift_artifact(
            class_="pii_surface_drift",
            owner="governance",
            items=[
                {
                    "class": "pii_surface_drift",
                    "subject_locator": "customer_email",
                    "owner": "governance",
                    "principle_v": True,
                }
            ],
        ),
    )


def test_no_numeric_score_anywhere(tmp_path: Path) -> None:
    _build_repo(tmp_path)
    result = pw.run_portfolio_watch(tmp_path)
    _assert_no_numeric_score(result)
    _assert_no_numeric_score(json.loads(json.dumps(result)))


def test_no_secret_or_dsn_like_string(tmp_path: Path) -> None:
    _build_repo(tmp_path)
    result = pw.run_portfolio_watch(tmp_path)

    snapshot_path = tmp_path / ".seshat" / "watch" / "snapshot.json"
    haystacks = _flatten_strings(result) + [snapshot_path.read_text(encoding="utf-8")]
    for text in haystacks:
        for bad in _SECRET_LIKE:
            assert bad not in text, f"secret-like string leaked: {bad!r} in {text!r}"


def test_every_relayed_seam_names_an_owner(tmp_path: Path) -> None:
    _build_repo(tmp_path)
    summary = pw.build_portfolio_watch_summary(tmp_path)

    for scope in summary["scopes"]:
        if scope["requires_human_attention"]:
            assert scope["owner"], f"attention flagged with no owner: {scope}"


def _init_repo_with_commit(root: Path) -> None:
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
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=root,
        check=True,
        capture_output=True,
    )


def _git_status_paths(root: Path) -> list[str]:
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.split()[-1] for line in status.stdout.splitlines()]


def test_summary_assembly_changes_no_committed_artifact(tmp_path: Path) -> None:
    _build_repo(tmp_path)
    _init_repo_with_commit(tmp_path)

    pw.build_portfolio_watch_summary(tmp_path)

    assert _git_status_paths(tmp_path) == []


def test_run_portfolio_watch_writes_only_the_snapshot(tmp_path: Path) -> None:
    """SC-008: the only write beyond the returned summary is the local
    snapshot under .seshat/watch/."""
    _build_repo(tmp_path)
    _init_repo_with_commit(tmp_path)

    pw.run_portfolio_watch(tmp_path)

    changed = _git_status_paths(tmp_path)
    assert all(path.startswith(".seshat/") for path in changed), changed
