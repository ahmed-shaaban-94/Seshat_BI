"""Unit tests for the `version_compatibility` check (spec 129, FR-011).

Split out of the former monolithic ``test_agent_verify_checks.py`` to keep
each test module single-purpose (CodeScene Low Cohesion).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.agent_verify import checks
from tests.unit._agent_verify_fixtures import target_spec

pytestmark = pytest.mark.unit


def _patch_audit_versions(
    monkeypatch: pytest.MonkeyPatch, projections: list[dict]
) -> None:
    def _fake_audit_versions(repo_root):  # noqa: ANN001 - test double
        return {"projections": projections}

    monkeypatch.setattr(
        "scripts.check_release_versions.audit_versions", _fake_audit_versions
    )


def test_version_compatibility_pass_in_range(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = target_spec(tmp_path)
    _patch_audit_versions(
        monkeypatch,
        [
            {
                "surface": "claude_plugin",
                "observed": "0.2.0",
                "expected": "0.2.0",
                "status": "pass",
            }
        ],
    )
    result = checks.version_compatibility_check(spec, tmp_path)
    assert result.verdict == "PASS"
    assert "0.2.0" in result.evidence[0]


def test_version_compatibility_blocked_out_of_range_names_both_versions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = target_spec(tmp_path)
    _patch_audit_versions(
        monkeypatch,
        [
            {
                "surface": "claude_plugin",
                "observed": "0.1.0",
                "expected": "0.2.0",
                "status": "blocked",
                "blocking_reason": "claude_plugin version is '0.1.0'; expected '0.2.0'",
            }
        ],
    )
    result = checks.version_compatibility_check(spec, tmp_path)
    assert result.verdict == "BLOCKED"
    assert "0.1.0" in result.blocking_reasons[0]
    assert "0.2.0" in result.blocking_reasons[0]


def test_version_compatibility_blocked_when_declaration_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = target_spec(tmp_path)
    _patch_audit_versions(monkeypatch, [])  # no projection for this surface at all
    result = checks.version_compatibility_check(spec, tmp_path)
    assert result.verdict == "BLOCKED"
    assert "no version projection" in result.blocking_reasons[0]


def test_version_compatibility_never_passes_on_absent_declaration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = target_spec(tmp_path)
    _patch_audit_versions(
        monkeypatch,
        [
            {
                "surface": "claude_plugin",
                "observed": None,
                "expected": "0.2.0",
                "status": "blocked",
            }
        ],
    )
    result = checks.version_compatibility_check(spec, tmp_path)
    assert result.verdict != "PASS"
