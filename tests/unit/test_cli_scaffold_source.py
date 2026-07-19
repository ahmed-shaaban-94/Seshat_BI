"""`seshat scaffold-source <table>` CLI wiring (issue #339)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def test_cli_scaffold_source_writes_files_and_reports(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from seshat.cli import main

    rc = main(["scaffold-source", "sales_c086", "--repo", str(tmp_path)])

    assert rc == 0
    out = capsys.readouterr().out
    assert "wrote" in out
    assert "mappings/sales_c086/source-profile.md" in out
    assert (tmp_path / "mappings" / "sales_c086" / "source-map.yaml").is_file()


def test_cli_scaffold_source_reports_kept_on_rerun(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from seshat.cli import main

    main(["scaffold-source", "foo", "--repo", str(tmp_path)])
    capsys.readouterr()
    rc = main(["scaffold-source", "foo", "--repo", str(tmp_path)])

    assert rc == 0
    out = capsys.readouterr().out
    assert "kept" in out


def test_cli_scaffold_source_rejects_unsafe_table(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from seshat.cli import main

    rc = main(["scaffold-source", "../evil", "--repo", str(tmp_path)])

    assert rc == 1
    assert "refused" in capsys.readouterr().err


def test_cli_scaffold_source_hint_carries_nondefault_repo(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """P2 round-6 (#342): with a non-cwd --repo, the printed follow-up must name
    `seshat next --repo <that repo>` so the user inspects the scaffolded
    workspace, not their cwd."""
    from seshat.cli import main

    rc = main(["scaffold-source", "foo", "--repo", str(tmp_path)])

    assert rc == 0
    out = capsys.readouterr().out
    assert f"--repo {tmp_path}" in out
    assert "seshat next" in out
