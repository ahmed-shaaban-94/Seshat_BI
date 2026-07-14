"""Unit tests for the `ide_surface` and `governance_contract_presence` checks
(spec 129, FR-020 / FR-012a / SC-005).

Split out of the former monolithic ``test_agent_verify_checks.py`` to keep
each test module single-purpose (CodeScene Low Cohesion).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.agent_verify import checks
from seshat.agent_verify.targets import resolve_target
from tests.unit._agent_verify_fixtures import (
    INTACT_CONTRACT,
    REPO,
    target_spec,
    write_json,
)

pytestmark = pytest.mark.unit


# --- IDE surface (FR-020) ---------------------------------------------------


@pytest.mark.parametrize(
    "case",
    [
        pytest.param(
            {
                "ide_surface_flag": False,
                "manifest_data": None,
                "expected_verdict": "UNAVAILABLE",
                "expected_substring": "no IDE surface",
            },
            id="declares_none",
        ),
        pytest.param(
            {
                "ide_surface_flag": False,
                "manifest_data": {
                    "name": "seshat-bi",
                    "interface": {"displayName": "Seshat BI"},
                },
                "expected_verdict": "UNAVAILABLE",
                "expected_substring": None,
            },
            id="declares_none_even_with_interface_present",
        ),
        pytest.param(
            {
                "ide_surface_flag": True,
                "manifest_data": {
                    "name": "seshat-bi",
                    "interface": {"displayName": "Seshat BI"},
                },
                "expected_verdict": "PASS",
                "expected_substring": "Seshat BI",
            },
            id="declared_and_interface_present",
        ),
        pytest.param(
            {
                "ide_surface_flag": True,
                "manifest_data": {"name": "seshat-bi"},
                "expected_verdict": "BLOCKED",
                "expected_substring": None,
            },
            id="declared_but_interface_missing",
        ),
    ],
)
def test_ide_surface_verdict_matches_declaration_and_manifest(
    tmp_path: Path, case: dict
) -> None:
    ide_surface_flag = case["ide_surface_flag"]
    name = "codex" if ide_surface_flag else "claude"
    spec = target_spec(tmp_path, name=name, ide_surface=ide_surface_flag)
    manifest_data = case["manifest_data"]
    if manifest_data is not None:
        write_json(tmp_path / spec.manifest_path, manifest_data)

    result = checks.ide_surface_check(spec, tmp_path)

    assert result.verdict == case["expected_verdict"]
    expected_substring = case["expected_substring"]
    if expected_substring is not None:
        text = result.unavailable_reason or (
            result.evidence[0] if result.evidence else ""
        )
        assert expected_substring in text


# --- per-target governance-contract presence (FR-012a; SC-005) -------------


def test_governance_contract_presence_pass_when_every_hard_stop_line_present(
    tmp_path: Path,
) -> None:
    spec = target_spec(tmp_path)
    (tmp_path / spec.operating_contract).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / spec.operating_contract).write_text(INTACT_CONTRACT, encoding="utf-8")
    result = checks.governance_contract_presence_check(spec, tmp_path)
    assert result.verdict == "PASS"
    assert result.evidence_class == "per_target"


def test_governance_contract_presence_tolerates_manual_line_wrapping(
    tmp_path: Path,
) -> None:
    """The real shipped file hard-wraps long bullets across two physical
    lines; the check must not false-BLOCK on that alone."""
    spec = target_spec(tmp_path)
    wrapped = INTACT_CONTRACT.replace(
        "Never self-grant an approval; grain, ",
        "Never self-grant an approval;\n  grain, ",
    )
    (tmp_path / spec.operating_contract).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / spec.operating_contract).write_text(wrapped, encoding="utf-8")
    result = checks.governance_contract_presence_check(spec, tmp_path)
    assert result.verdict == "PASS"


def test_governance_contract_presence_blocked_naming_dropped_hard_stop(
    tmp_path: Path,
) -> None:
    spec = target_spec(tmp_path)
    dropped_line = checks.GOVERNANCE_HARD_STOP_LINES[0][1]
    mutated = INTACT_CONTRACT.replace(dropped_line, "")
    (tmp_path / spec.operating_contract).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / spec.operating_contract).write_text(mutated, encoding="utf-8")
    result = checks.governance_contract_presence_check(spec, tmp_path)
    assert result.verdict == "BLOCKED"
    assert any(
        checks.GOVERNANCE_HARD_STOP_LINES[0][0] in reason
        for reason in result.blocking_reasons
    )


def test_governance_contract_presence_blocked_when_file_missing(tmp_path: Path) -> None:
    spec = target_spec(tmp_path)
    result = checks.governance_contract_presence_check(spec, tmp_path)
    assert result.verdict == "BLOCKED"


def test_governance_contract_presence_is_genuinely_per_target(tmp_path: Path) -> None:
    """SC-005: one target's own bundle can drop a hard stop while the other
    target's bundle stays intact -- the verdict is not vacuously identical."""
    claude_spec = target_spec(tmp_path, name="claude")
    codex_spec = target_spec(tmp_path, name="codex")
    (tmp_path / claude_spec.operating_contract).parent.mkdir(
        parents=True, exist_ok=True
    )
    (tmp_path / claude_spec.operating_contract).write_text(
        INTACT_CONTRACT, encoding="utf-8"
    )
    (tmp_path / codex_spec.operating_contract).parent.mkdir(parents=True, exist_ok=True)
    dropped_line = checks.GOVERNANCE_HARD_STOP_LINES[1][1]
    (tmp_path / codex_spec.operating_contract).write_text(
        INTACT_CONTRACT.replace(dropped_line, ""), encoding="utf-8"
    )

    claude_result = checks.governance_contract_presence_check(claude_spec, tmp_path)
    codex_result = checks.governance_contract_presence_check(codex_spec, tmp_path)

    assert claude_result.verdict == "PASS"
    assert codex_result.verdict == "BLOCKED"


def test_real_shipped_contracts_pass_for_both_targets() -> None:
    """Grounding check against the real committed bundles."""
    for name in ("claude", "codex"):
        result = checks.governance_contract_presence_check(resolve_target(name), REPO)
        assert result.verdict == "PASS", result.blocking_reasons
