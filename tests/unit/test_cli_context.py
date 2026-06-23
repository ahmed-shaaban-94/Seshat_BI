"""M1.7: mode-aware build_context + the two new CLI flags."""

from pathlib import Path

import pytest

from retail.cli import _build_parser
from retail.runner import build_context

pytestmark = pytest.mark.unit


def test_build_context_defaults_both_none(tmp_path: Path) -> None:
    ctx = build_context(tmp_path)
    # Only the two v2 fields are asserted here — tracked_files behavior on a
    # tmp dir is out of scope for this test.
    assert ctx.commit_range is None
    assert ctx.commit_message is None


def test_build_context_populates_v2_fields(tmp_path: Path) -> None:
    ctx = build_context(
        tmp_path,
        commit_range="origin/main..HEAD",
        commit_message="feat: a thing",
    )
    assert ctx.commit_range == "origin/main..HEAD"
    assert ctx.commit_message == "feat: a thing"


def test_parser_default_flags_are_none() -> None:
    # The commit-aware flags live under the `check` subcommand.
    ns = _build_parser().parse_args(["check"])
    assert ns.commit_range is None
    assert ns.commit_msg_file is None
    assert ns.repo == "."  # M1.5's --repo is retained with its default


def test_parser_commit_range_flag() -> None:
    ns = _build_parser().parse_args(["check", "--commit-range", "origin/main..HEAD"])
    assert ns.commit_range == "origin/main..HEAD"


def test_parser_commit_msg_file_flag() -> None:
    ns = _build_parser().parse_args(["check", "--commit-msg-file", "/tmp/MSG"])
    assert ns.commit_msg_file == "/tmp/MSG"


def test_main_commit_msg_file_is_read_and_stripped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # git writes COMMIT_EDITMSG with a trailing newline; main must strip it.
    msg_file = tmp_path / "COMMIT_EDITMSG"
    msg_file.write_text("feat: real message\n", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_build_context(repo_root, commit_range=None, commit_message=None):
        captured["commit_range"] = commit_range
        captured["commit_message"] = commit_message
        from retail.core import RuleContext

        return RuleContext(
            repo_root=repo_root,
            tracked_files=(),
            commit_range=commit_range,
            commit_message=commit_message,
        )

    # Patch where cli looks it up, and stub run so no rules execute.
    monkeypatch.setattr("retail.cli.build_context", fake_build_context)
    monkeypatch.setattr("retail.cli.run", lambda rules, ctx: 0)

    rc = main_under_test(["check", "--commit-msg-file", str(msg_file)])

    assert rc == 0
    assert captured["commit_message"] == "feat: real message"
    assert captured["commit_range"] is None


def test_main_commit_range_flag_threads_through(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_build_context(repo_root, commit_range=None, commit_message=None):
        captured["commit_range"] = commit_range
        captured["commit_message"] = commit_message
        from retail.core import RuleContext

        return RuleContext(repo_root=repo_root, tracked_files=())

    monkeypatch.setattr("retail.cli.build_context", fake_build_context)
    monkeypatch.setattr("retail.cli.run", lambda rules, ctx: 0)

    rc = main_under_test(["check", "--commit-range", "origin/main..HEAD"])

    assert rc == 0
    assert captured["commit_range"] == "origin/main..HEAD"
    assert captured["commit_message"] is None


# Imported at module scope after monkeypatch targets above are defined; aliased
# so the patch sites (retail.cli.build_context / retail.cli.run) are the ones
# main() actually calls.
from retail.cli import main as main_under_test  # noqa: E402
