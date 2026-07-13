from __future__ import annotations

from pathlib import Path

import pytest

from scripts.install_smoke_test import _assert_commands_removed, _workspace_digest

pytestmark = pytest.mark.integration


def test_project_digest_is_stable_and_detects_user_file_change(tmp_path: Path) -> None:
    workspace = tmp_path / "project"
    workspace.mkdir()
    (workspace / "README.md").write_text("user project\n", encoding="utf-8")
    before = _workspace_digest(workspace)
    assert _workspace_digest(workspace) == before
    (workspace / "README.md").write_text("changed\n", encoding="utf-8")
    assert _workspace_digest(workspace) != before


def test_uninstall_contract_fails_if_either_command_remains(tmp_path: Path) -> None:
    _assert_commands_removed(tmp_path)
    command = tmp_path / "seshat.exe"
    command.write_text("shim", encoding="utf-8")
    with pytest.raises(SystemExit, match="remained after uninstall"):
        _assert_commands_removed(tmp_path)
