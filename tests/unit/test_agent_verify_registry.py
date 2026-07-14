"""Unit tests for the agent-verify target registry and required-check-id set
(spec 129). Split out of the former monolithic ``test_agent_verify_checks.py``
to keep each test module single-purpose (CodeScene Low Cohesion).
"""

from __future__ import annotations

import pytest

from seshat.agent_verify import checks
from seshat.agent_verify.targets import (
    UnknownVerifyTargetError,
    resolve_target,
    supported_targets,
)

pytestmark = pytest.mark.unit


def test_every_required_check_id_is_covered_once() -> None:
    assert len(checks.REQUIRED_CHECK_IDS) == 11
    assert len(set(checks.REQUIRED_CHECK_IDS)) == 11
    assert set(checks.PER_TARGET_CHECK_IDS) | set(
        checks.SHARED_BASELINE_CHECK_IDS
    ) == set(checks.REQUIRED_CHECK_IDS)


def test_resolve_target_supports_claude_and_codex() -> None:
    assert set(supported_targets()) == {"claude", "codex"}
    assert resolve_target("claude").name == "claude"
    assert resolve_target("codex").name == "codex"


def test_resolve_target_raises_typed_error_for_unknown_target() -> None:
    with pytest.raises(UnknownVerifyTargetError):
        resolve_target("gemini")
