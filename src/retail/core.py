from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Iterable


class Severity(str, Enum):
    ERROR = "error"  # fails the build (non-zero exit)
    WARNING = "warning"  # reported, does NOT fail the build
    INFO = "info"  # informational only


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: Severity
    message: str
    locator: str


@dataclass(frozen=True)
class RuleContext:
    repo_root: Path
    tracked_files: tuple[str, ...]
    commit_range: str | None = None
    commit_message: str | None = None


# A rule is a pure function: context in, findings out. No side effects.
Rule = Callable[[RuleContext], Iterable[Finding]]


@dataclass(frozen=True)
class RegisteredRule:
    id: str
    rule: Rule
    title: str
