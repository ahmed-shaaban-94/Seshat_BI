"""Integration test: the `retail watch` CLI surface (spec 131, T032).

Asserts the surface is read-only, emits the summary shape, opens no DB, and
prints no score. Runs `retail watch` as a real subprocess (matching how a CI/
agent-less consumer invokes it) so the process-level "no DB module loaded"
guarantee is meaningful.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.fixtures.portfolio_watch.builders import write_readiness_status

pytestmark = pytest.mark.integration


def _run_cli(repo: Path, *args: str) -> subprocess.CompletedProcess:
    src_root = str(Path(__file__).resolve().parents[2] / "src")
    env = dict(os.environ, PYTHONPATH=src_root)
    return subprocess.run(
        [sys.executable, "-m", "seshat.cli", "watch", "--repo", str(repo), *args],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )


def test_watch_json_emits_the_summary_shape_and_no_score(tmp_path: Path) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")

    result = _run_cli(tmp_path, "--format", "json")

    payload = json.loads(result.stdout)
    assert "scopes" in payload
    assert "portfolio" in payload
    assert payload["scopes"][0]["scope_id"] == "scope_alpha"
    lowered = result.stdout.lower()
    for bad in ("score", "confidence", "health_index"):
        assert bad not in lowered


def test_watch_text_format_runs_clean(tmp_path: Path) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")

    result = _run_cli(tmp_path, "--format", "text")

    assert "scope_alpha" in result.stdout
    assert result.returncode == 0


def test_watch_writes_only_the_local_snapshot(tmp_path: Path) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")
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

    _run_cli(tmp_path, "--format", "json")

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    changed = [line.split()[-1] for line in status.stdout.splitlines()]
    assert all(path.startswith(".seshat/") for path in changed), changed


def test_watch_process_never_loads_a_db_module(tmp_path: Path) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")
    src_root = str(Path(__file__).resolve().parents[2] / "src")
    env = dict(os.environ, PYTHONPATH=src_root)
    code = (
        "import sys\n"
        "from seshat.cli import main\n"
        f"main(['watch', '--repo', {str(tmp_path)!r}, '--format', 'json'])\n"
        "print('DIALECT_LOADED=' + str('seshat.dialect' in sys.modules))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    assert "DIALECT_LOADED=False" in result.stdout
