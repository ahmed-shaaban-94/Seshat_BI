from __future__ import annotations

import subprocess
from pathlib import Path

from . import rules as _rules  # noqa: F401  (imported for the registration side effect)
from .core import Finding, RegisteredRule, RuleContext, Severity


def _git_ls_files(repo_root: Path) -> tuple[str, ...]:
    """Return repo-relative POSIX paths for every tracked file.

    Returns an empty tuple when ``repo_root`` is not a git repository (e.g.
    in unit tests that call ``build_context`` on a bare tmp dir) rather than
    raising ``CalledProcessError``.
    """
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ()
    # git ls-files already emits forward slashes; split on newlines, drop blanks.
    return tuple(line for line in result.stdout.splitlines() if line)


def build_context(
    repo_root: Path,
    commit_range: str | None = None,
    commit_message: str | None = None,
) -> RuleContext:
    """Build the read-only context every rule receives.

    ``commit_range`` and ``commit_message`` are the contract-v2 invocation
    fields: populated by the CLI flags ``--commit-range`` / ``--commit-msg-file``
    and consumed by P2. Both default to ``None`` (no commit context), which is
    the local ``retail check`` mode.
    """
    return RuleContext(
        repo_root=repo_root,
        tracked_files=_git_ls_files(repo_root),
        commit_range=commit_range,
        commit_message=commit_message,
    )


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
