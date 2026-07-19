"""`seshat scaffold-source <table>` self-sufficiency (issue #339).

A bare workspace (no dev repo) must obtain the three Stage-1 blank templates
from bundled package data, written non-destructively into mappings/<table>/.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_STAGE1_FILES = (
    "source-profile.md",
    "readiness-status.yaml",
    "source-map.yaml",
)


def test_scaffold_source_writes_the_three_stage1_files(tmp_path: Path) -> None:
    from seshat.stage1_scaffold import scaffold_source

    report = scaffold_source(tmp_path, "sales_c086")

    for name in _STAGE1_FILES:
        target = tmp_path / "mappings" / "sales_c086" / name
        assert target.is_file()
        assert f"mappings/sales_c086/{name}" in report.written
    assert report.kept == ()


def test_scaffold_source_neutralizes_the_broken_adr_link(tmp_path: Path) -> None:
    from seshat.stage1_scaffold import scaffold_source

    scaffold_source(tmp_path, "foo")
    profile = (tmp_path / "mappings" / "foo" / "source-profile.md").read_text(
        encoding="utf-8"
    )
    assert "../docs/decisions/0003-mapping-artifact-location.md" not in profile
    assert "ADR 0003 (mapping-artifact-location)" in profile


def test_scaffold_source_is_non_destructive_and_idempotent(tmp_path: Path) -> None:
    from seshat.stage1_scaffold import scaffold_source

    scaffold_source(tmp_path, "foo")
    edited = tmp_path / "mappings" / "foo" / "source-map.yaml"
    edited.write_text("# hand-edited\n", encoding="utf-8")

    second = scaffold_source(tmp_path, "foo")

    assert "mappings/foo/source-map.yaml" in second.kept
    assert second.written == ()
    assert edited.read_text(encoding="utf-8") == "# hand-edited\n"


def test_scaffold_source_creates_mappings_dir_when_absent(tmp_path: Path) -> None:
    from seshat.stage1_scaffold import scaffold_source

    assert not (tmp_path / "mappings").exists()
    scaffold_source(tmp_path, "foo")
    assert (tmp_path / "mappings" / "foo").is_dir()


@pytest.mark.parametrize("bad", ["../evil", "a/b", "", ".", "..", "/abs"])
def test_scaffold_source_rejects_unsafe_table_segment(tmp_path: Path, bad: str) -> None:
    from seshat.stage1_scaffold import Stage1ScaffoldError, scaffold_source

    with pytest.raises(Stage1ScaffoldError):
        scaffold_source(tmp_path, bad)


def test_scaffold_source_dev_checkout_fallback_resolves(tmp_path: Path) -> None:
    """No wheel data needed in the dev suite: the _SOURCE_ROOT fallback must
    find the repo-root templates/ so the three files still materialize."""
    from seshat.stage1_scaffold import scaffold_source

    report = scaffold_source(tmp_path, "foo")
    assert len(report.written) == 3


def test_scaffolded_readiness_degrades_to_unstarted_not_malformed(
    tmp_path: Path,
) -> None:
    """The scaffolded blank readiness-status.yaml must read as an UNSTARTED
    Source-Ready journey (outcome=next_action, stage=source_ready), never an
    input_defect / malformed-repair path (issue #339, degrade contract)."""
    from seshat.run_next import build_run_next_response
    from seshat.stage1_scaffold import scaffold_source

    scaffold_source(tmp_path, "foo")
    resp = build_run_next_response(str(tmp_path), "foo")

    assert resp["outcome"] == "next_action"
    assert resp["stage"] == "source_ready"
    assert resp["read_only_proof"] is True


@pytest.mark.parametrize(
    "reserved",
    ["con", "CON", "aux", "nul", "com1", "lpt1", "prn", "Com9", "a:b", "a*b", "a?b"],
)
def test_scaffold_source_rejects_windows_reserved_and_invalid_names(
    tmp_path: Path, reserved: str
) -> None:
    """P2 (#342): names that match the charset but cannot be created as
    directories on Windows (reserved device names, invalid filename chars) must
    raise Stage1ScaffoldError -- the documented refusal -- not an uncaught
    filesystem OSError / traceback."""
    from seshat.stage1_scaffold import Stage1ScaffoldError, scaffold_source

    with pytest.raises(Stage1ScaffoldError):
        scaffold_source(tmp_path, reserved)


def test_scaffold_source_refuses_symlinked_mappings_escape(tmp_path: Path) -> None:
    """P2 (#342): if `mappings/` is a symlink pointing outside --repo, writing
    into mappings/<table>/ would escape the repo. Refuse rather than follow the
    symlink out of the requested tree."""
    import os

    from seshat.stage1_scaffold import Stage1ScaffoldError, scaffold_source

    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        os.symlink(outside, repo / "mappings", target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted in this environment")

    with pytest.raises(Stage1ScaffoldError):
        scaffold_source(repo, "foo")

    # nothing was written outside the repo
    assert not (outside / "foo").exists()


def test_scaffold_source_wraps_oserror_as_stage1_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P2 backstop (#342): any residual filesystem OSError during the write
    (e.g. the Windows 260-char path limit) surfaces as Stage1ScaffoldError, so
    the CLI returns its refusal status instead of a traceback."""
    import seshat.stage1_scaffold as mod
    from seshat.stage1_scaffold import Stage1ScaffoldError, scaffold_source

    def _boom(target, data):
        raise OSError("simulated filesystem failure")

    monkeypatch.setattr(mod, "_write_if_absent", _boom)

    with pytest.raises(Stage1ScaffoldError):
        scaffold_source(tmp_path, "foo")
