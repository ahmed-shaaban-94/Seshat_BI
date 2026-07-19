"""Hardened read-only git state probes (issue #334) -- all probes fail CLOSED."""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.gitstate import committed_text, is_tracked_and_clean
from tests.unit._gitfix import commit_all, make_git_repo

pytestmark = pytest.mark.unit


def test_committed_clean_file_is_trusted(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    (repo / "artifact.md").write_text("committed truth\n", encoding="utf-8")
    commit_all(repo, "record artifact")

    assert is_tracked_and_clean(repo, "artifact.md") is True
    assert committed_text(repo, "artifact.md") == "committed truth\n"


def test_untracked_file_fails_closed(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    (repo / "keep.md").write_text("x\n", encoding="utf-8")
    commit_all(repo, "seed")
    (repo / "artifact.md").write_text("worktree only\n", encoding="utf-8")

    assert is_tracked_and_clean(repo, "artifact.md") is False
    assert committed_text(repo, "artifact.md") is None


def test_dirty_tracked_file_fails_closed(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    (repo / "artifact.md").write_text("committed truth\n", encoding="utf-8")
    commit_all(repo, "record artifact")
    (repo / "artifact.md").write_text("uncommitted edit\n", encoding="utf-8")

    assert is_tracked_and_clean(repo, "artifact.md") is False
    assert committed_text(repo, "artifact.md") is None


def test_outside_any_repository_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "bare").mkdir()
    (tmp_path / "bare" / "artifact.md").write_text("x\n", encoding="utf-8")

    assert is_tracked_and_clean(tmp_path / "bare", "artifact.md") is False
    assert committed_text(tmp_path / "bare", "artifact.md") is None
