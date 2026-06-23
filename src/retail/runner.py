from __future__ import annotations

import subprocess
from pathlib import Path

from .core import Finding, RegisteredRule, RuleContext, Severity


def _git_ls_files(repo_root: Path) -> tuple[str, ...]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    # git ls-files already emits forward slashes; split on newlines, drop blanks.
    return tuple(line for line in result.stdout.splitlines() if line)


def build_context(repo_root: Path) -> RuleContext:
    return RuleContext(repo_root=repo_root, tracked_files=_git_ls_files(repo_root))


def _format(finding: Finding) -> str:
    return (
        f"[{finding.severity.value}] {finding.rule_id} "
        f"{finding.message} ({finding.locator})"
    )


def run(rules: tuple[RegisteredRule, ...], ctx: RuleContext) -> int:
    exit_code = 0
    for registered in rules:
        for finding in registered.rule(ctx):
            print(_format(finding))
            if finding.severity is Severity.ERROR:
                exit_code = 1
    return exit_code
