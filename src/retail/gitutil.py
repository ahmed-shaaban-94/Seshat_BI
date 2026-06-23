from __future__ import annotations

import subprocess
from pathlib import Path


def git_output(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({result.returncode}): {result.stderr}"
        )
    return result.stdout


def git_check_ignore(repo_root: Path, path: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "check-ignore", "-q", path],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise RuntimeError(f"git check-ignore error ({result.returncode}): {result.stderr}")


def git_log_subjects(repo_root: Path, base_ref: str) -> list[str]:
    out = git_output(
        repo_root, "log", "--no-merges", f"{base_ref}..HEAD", "--format=%s"
    )
    return [line for line in out.splitlines() if line]
