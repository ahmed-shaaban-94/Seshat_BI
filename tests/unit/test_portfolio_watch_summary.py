"""US1 tests: the recurring portfolio summary (spec 131, T008).

Summary lists every fixture scope; each covered dimension finding carries a
committed ``evidence`` citation + ``source_surface`` (INV-2); NO numeric
health/confidence/priority score appears anywhere (INV-1, FR-020).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from seshat import portfolio_watch as pw
from tests.fixtures.portfolio_watch.builders import (
    DEFAULT_STAGES,
    drift_artifact,
    write_json_artifact,
    write_readiness_status,
    write_source_profile,
)

pytestmark = pytest.mark.unit

_FORBIDDEN_SCORE_KEYS = (
    "score",
    "confidence",
    "health",
    "priority_score",
    "quality_score",
    "rank_score",
)


def _walk(value: Any) -> list[Any]:
    if isinstance(value, dict):
        out = []
        for key, child in value.items():
            assert not any(bad in str(key).lower() for bad in _FORBIDDEN_SCORE_KEYS), (
                f"forbidden score-shaped key found: {key}"
            )
            out.append(child)
        return out
    if isinstance(value, list):
        return list(value)
    return []


def _assert_no_score(document: Any) -> None:
    stack = [document]
    while stack:
        current = stack.pop()
        assert not isinstance(current, float), f"a bare float value appeared: {current}"
        stack.extend(_walk(current))


def _build_multi_scope_repo(root: Path) -> None:
    write_readiness_status(
        root,
        "scope_alpha",
        current_stage="publish_ready",
        stage_status={s: "pass" for s in DEFAULT_STAGES},
        next_action="All seven readiness stages pass for scope_alpha.",
    )
    write_readiness_status(
        root,
        "scope_beta",
        current_stage="mapping_ready",
        stage_status={"source_ready": "pass", "mapping_ready": "blocked"},
        stage_blocking_reasons={
            "mapping_ready": ["mapping_ready approval is missing"],
        },
        top_blocking_reasons=["mapping_ready approval is missing"],
        next_action="obtain the mapping_ready approval",
    )
    write_source_profile(root, "scope_beta")
    write_json_artifact(
        root,
        "scope_beta",
        "drift-findings.json",
        drift_artifact(class_="column_added", measured="1 finding"),
    )


def test_summary_lists_every_fixture_scope(tmp_path: Path) -> None:
    _build_multi_scope_repo(tmp_path)

    summary = pw.build_portfolio_watch_summary(tmp_path)

    scope_ids = {scope["scope_id"] for scope in summary["scopes"]}
    assert scope_ids == {"scope_alpha", "scope_beta"}
    assert summary["portfolio"]["scope_count"] == 2


def test_every_covered_finding_cites_evidence_and_source_surface(
    tmp_path: Path,
) -> None:
    _build_multi_scope_repo(tmp_path)

    summary = pw.build_portfolio_watch_summary(tmp_path)

    for scope in summary["scopes"]:
        for dim in scope["dimensions"]:
            if dim["state"] == "covered":
                assert dim["evidence"], f"covered finding with no evidence: {dim}"
                assert dim["source_surface"], (
                    f"covered finding with no source_surface: {dim}"
                )


def test_no_numeric_score_anywhere_in_the_summary(tmp_path: Path) -> None:
    _build_multi_scope_repo(tmp_path)

    summary = pw.build_portfolio_watch_summary(tmp_path)

    _assert_no_score(summary)
    # round-trip through JSON too, since the CLI surface emits JSON verbatim
    _assert_no_score(json.loads(json.dumps(summary)))


def test_summary_assembly_writes_no_per_scope_artifact(tmp_path: Path) -> None:
    """SC-008: summary assembly changes no committed per-scope artifact."""
    _build_multi_scope_repo(tmp_path)
    subprocess.run(
        ["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "t@example.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    pw.build_portfolio_watch_summary(tmp_path)

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert status.stdout.strip() == ""
