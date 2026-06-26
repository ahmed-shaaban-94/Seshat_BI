"""Skip-safety + parsing tests for the OPTIONAL F038 BPA runner (tools/bpa_runner.py).

The runner is NOT part of the stdlib-only `retail check` core; these tests prove it
SKIPS cleanly with no binary (the CI norm, SC-002), parses TE output correctly, and
never imports a .NET/Tabular dependency. They do NOT require Tabular Editor to be
installed -- the live smoke run is exercised separately by the runner's --evidence
mode on a configured dev machine.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

# Load tools/bpa_runner.py by path -- it lives OUTSIDE the importable `retail`
# package (FR-007: outside the core import chain), so we load it explicitly.
_RUNNER_PATH = Path(__file__).parent.parent.parent / "tools" / "bpa_runner.py"
_spec = importlib.util.spec_from_file_location("bpa_runner", _RUNNER_PATH)
assert _spec and _spec.loader
bpa_runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bpa_runner)


def test_resolve_te_path_unset_and_no_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """No env var AND no default binary => None (the runner must then skip)."""
    monkeypatch.delenv("TABULAR_EDITOR_PATH", raising=False)
    monkeypatch.setattr(bpa_runner, "_DEFAULT_TE_PATH", Path("/no/such/te.exe"))
    assert bpa_runner.resolve_te_path() is None


def test_resolve_te_path_env_pointing_at_missing_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A TABULAR_EDITOR_PATH pointing at a nonexistent file resolves to None."""
    monkeypatch.setenv("TABULAR_EDITOR_PATH", "/definitely/not/here/te.exe")
    assert bpa_runner.resolve_te_path() is None


def test_main_skips_clean_when_unconfigured(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """SC-002: with no binary, the runner exits 0 'skipped' -- never a crash, never a
    GUI, never a non-zero failure (so CI without Tabular Editor stays green)."""
    monkeypatch.delenv("TABULAR_EDITOR_PATH", raising=False)
    monkeypatch.setattr(bpa_runner, "_DEFAULT_TE_PATH", Path("/no/such/te.exe"))

    rc = bpa_runner.main([])

    assert rc == 0
    err = capsys.readouterr().err
    assert "skipped (not configured)" in err
    assert "TABULAR_EDITOR_PATH" in err  # prints the enable steps


def test_main_skip_does_not_invoke_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The skip path must not even attempt to launch the binary (no GUI risk)."""
    monkeypatch.delenv("TABULAR_EDITOR_PATH", raising=False)
    monkeypatch.setattr(bpa_runner, "_DEFAULT_TE_PATH", Path("/no/such/te.exe"))

    import subprocess

    def _boom(*a, **k):  # pragma: no cover - must never be called on the skip path
        raise AssertionError("subprocess.run must not be called when skipping")

    monkeypatch.setattr(subprocess, "run", _boom)
    assert bpa_runner.main([]) == 0


def test_parse_violations_reads_vsts_lines() -> None:
    """Gate 4: violations are derived by PARSING the -V output, not the exit code
    (TE exits 0 even with violations)."""
    out = (
        "Tabular Editor 2.25.0\n"
        '##vso[task.logissue type=warning;]Measure [TotalSales] violates rule "X"\n'
        '##vso[task.logissue type=warning;]Measure [NetSales] violates rule "X"\n'
        "##vso[task.complete result=Failed;]Done.\n"
    )
    violations = bpa_runner._parse_violations(out)
    assert len(violations) == 2
    assert all("violates rule" in v for v in violations)
    assert not any(v.startswith("##vso") for v in violations)  # marker stripped


def test_parse_violations_empty_when_clean() -> None:
    """A clean model (no violation lines) parses to zero violations."""
    out = (
        "Running Best Practice Analyzer...\n"
        "No objects in violation of Best Practices.\n"
    )
    assert bpa_runner._parse_violations(out) == []
