"""Unit tests for the `update_integrity` and `uninstall_integrity` checks
(spec 129, FR-018/FR-019).

Split out of the former monolithic ``test_agent_verify_checks.py`` to keep
each test module single-purpose (CodeScene Low Cohesion).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.agent_verify import checks
from tests.unit._agent_verify_fixtures import (
    sha,
    target_spec,
    write_bundle_with_manifest,
    write_json,
)

pytestmark = pytest.mark.unit


# --- update integrity (FR-018) ---------------------------------------------


def test_update_integrity_pass_when_hashes_match(tmp_path: Path) -> None:
    spec = target_spec(tmp_path)
    write_bundle_with_manifest(tmp_path, spec)
    result = checks.update_integrity_check(spec, tmp_path)
    assert result.verdict == "PASS"
    assert "match their recorded output_sha256" in result.evidence[0]


def test_update_integrity_blocked_on_seeded_drift_names_path_and_hashes(
    tmp_path: Path,
) -> None:
    spec = target_spec(tmp_path)
    bundle_root = write_bundle_with_manifest(tmp_path, spec)
    # Seed drift: mutate one generated file's content without touching the manifest.
    drifted_file = bundle_root / "README.md"
    drifted_file.write_bytes(b"MUTATED content that breaks provenance\n")

    result = checks.update_integrity_check(spec, tmp_path)

    assert result.verdict == "BLOCKED"
    assert any("README.md" in reason for reason in result.blocking_reasons)
    assert any(
        "expected sha256" in reason and "observed" in reason
        for reason in result.blocking_reasons
    )


def test_update_integrity_blocked_when_destination_escapes_bundle_root(
    tmp_path: Path,
) -> None:
    """A provenance entry whose destination is an absolute path outside
    bundle_root must be refused as a containment escape -- never resolved
    and hashed as if it proved the installed bundle's own contents are
    intact (which it would, trivially, for ANY matching outside file)."""
    spec = target_spec(tmp_path)
    outside_file = tmp_path / "outside-secret.txt"
    outside_file.write_bytes(b"arbitrary file outside the bundle\n")
    manifest = {
        "entries": [
            {
                "destination": str(outside_file),
                "output_sha256": sha(outside_file.read_bytes()),
            }
        ]
    }
    write_json(tmp_path / spec.provenance_manifest, manifest)

    result = checks.update_integrity_check(spec, tmp_path)

    assert result.verdict == "BLOCKED"
    assert any(
        "escapes the bundle root" in reason for reason in result.blocking_reasons
    )


def test_update_integrity_blocked_on_missing_generated_file(tmp_path: Path) -> None:
    spec = target_spec(tmp_path)
    bundle_root = write_bundle_with_manifest(tmp_path, spec)
    (bundle_root / "README.md").unlink()

    result = checks.update_integrity_check(spec, tmp_path)

    assert result.verdict == "BLOCKED"
    assert any(
        "README.md" in reason and "missing" in reason
        for reason in result.blocking_reasons
    )


# --- uninstall integrity (FR-019) ------------------------------------------


def test_uninstall_integrity_lists_declared_footprint(tmp_path: Path) -> None:
    spec = target_spec(tmp_path)
    write_bundle_with_manifest(tmp_path, spec)
    result = checks.uninstall_integrity_check(spec, tmp_path)
    assert result.verdict == "PASS"
    assert "commands/seshat-check.md" in result.evidence
    assert "README.md" in result.evidence


def test_uninstall_integrity_unavailable_when_footprint_unenumerable(
    tmp_path: Path,
) -> None:
    spec = target_spec(tmp_path)
    # No provenance manifest at all.
    result = checks.uninstall_integrity_check(spec, tmp_path)
    assert result.verdict == "UNAVAILABLE"
    assert result.unavailable_reason


def test_uninstall_integrity_unavailable_when_manifest_has_no_entries(
    tmp_path: Path,
) -> None:
    spec = target_spec(tmp_path)
    write_json(tmp_path / spec.provenance_manifest, {"entries": []})
    result = checks.uninstall_integrity_check(spec, tmp_path)
    assert result.verdict == "UNAVAILABLE"
