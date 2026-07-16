"""Regression guard for the `claude-code-plugin` capability classification.

The generated Claude Code plugin bundle is committed (manifest + repo-root
marketplace entry) and contract-tested, yet the capability manifest once
recorded it `spec-only` with the false summary "No plugin manifest is committed
on this branch". This test pins the corrected truth so it cannot silently
regress: the entry must be `shipped` with a real ship feeder, and it must not
re-assert the falsified "no manifest committed" claim while the manifest exists.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.capability_inventory import load_manifest
from tests.unit import _capability_oracle as oracle

pytestmark = pytest.mark.unit

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _plugin_entry() -> dict:
    entry = next(
        (e for e in load_manifest(_REPO_ROOT) if e.get("id") == "claude-code-plugin"),
        None,
    )
    assert entry is not None, "claude-code-plugin capability entry is missing"
    return entry


def test_claude_code_plugin_manifests_are_committed() -> None:
    for manifest in (
        ".claude-plugin/marketplace.json",
        "integrations/claude-code/seshat-bi/.claude-plugin/plugin.json",
    ):
        assert (_REPO_ROOT / manifest).is_file(), f"{manifest} must be committed"


def test_claude_code_plugin_is_recorded_shipped_with_a_real_ship_feeder() -> None:
    entry = _plugin_entry()
    assert entry["state"] == "shipped"
    # A bare shipped flip would fail the O3 oracle; the entry must carry a
    # positive ship signal recognized by the independent feeder reader.
    assert oracle.has_positive_ship_signal(entry, _REPO_ROOT), (
        "claude-code-plugin must reference a recognized ship feeder"
    )


def test_claude_code_plugin_summary_drops_the_false_no_manifest_claim() -> None:
    summary = _plugin_entry()["summary"].lower()
    assert "no plugin manifest is committed" not in summary
