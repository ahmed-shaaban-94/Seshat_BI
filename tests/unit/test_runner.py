from pathlib import Path

import pytest

from retail.core import Finding, RegisteredRule, RuleContext, Severity
from retail.runner import build_context, run


def _ctx() -> RuleContext:
    return RuleContext(repo_root=Path("."), tracked_files=())


@pytest.mark.unit
def test_run_exits_1_when_any_error_finding(capsys):
    def bad(ctx: RuleContext):
        return [Finding("E1", Severity.ERROR, "boom", "f.sql:1")]

    rules = (RegisteredRule(id="E1", rule=bad, title="bad"),)
    code = run(rules, _ctx())
    assert code == 1
    out = capsys.readouterr().out
    assert "[error] E1 boom (f.sql:1)" in out


@pytest.mark.unit
def test_run_exits_0_when_no_error_findings(capsys):
    def warn(ctx: RuleContext):
        return [Finding("W1", Severity.WARNING, "heads up", "f.sql:2")]

    def clean(ctx: RuleContext):
        return ()

    rules = (
        RegisteredRule(id="W1", rule=warn, title="warn"),
        RegisteredRule(id="C0", rule=clean, title="clean"),
    )
    code = run(rules, _ctx())
    assert code == 0
    out = capsys.readouterr().out
    assert "[warning] W1 heads up (f.sql:2)" in out


@pytest.mark.unit
def test_run_exits_0_when_no_findings_at_all(capsys):
    def clean(ctx: RuleContext):
        return ()

    rules = (RegisteredRule(id="C0", rule=clean, title="clean"),)
    assert run(rules, _ctx()) == 0


@pytest.mark.unit
def test_build_context_uses_git_ls_files(tmp_path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "a.sql").write_text("select 1\n", encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.tmdl").write_text("table T\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)

    ctx = build_context(tmp_path)
    assert ctx.repo_root == tmp_path
    # POSIX-separated, repo-relative, regardless of OS.
    assert "a.sql" in ctx.tracked_files
    assert "sub/b.tmdl" in ctx.tracked_files
