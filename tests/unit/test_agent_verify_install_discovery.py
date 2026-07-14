"""Unit tests for the `install_discovery` check (spec 129, FR-009/FR-010).

Split out of the former monolithic ``test_agent_verify_checks.py`` to keep
each test module single-purpose (CodeScene Low Cohesion).
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath

import pytest

from seshat.agent_verify import checks
from seshat.agent_verify.targets import marketplace_path_for
from tests.unit._agent_verify_fixtures import (
    bundle_source,
    target_spec,
    write_install_fixture,
    write_json,
)

pytestmark = pytest.mark.unit


def test_install_discovery_pass_cites_manifest_marketplace_and_provenance(
    tmp_path: Path,
) -> None:
    spec = target_spec(tmp_path)
    write_install_fixture(tmp_path, spec)

    result = checks.install_discovery_check(spec, tmp_path)

    assert result.verdict == "PASS"
    assert result.evidence_class == "per_target"
    assert any("plugin manifest resolved" in item for item in result.evidence)
    assert any(
        "marketplace/discovery entry resolved" in item for item in result.evidence
    )
    assert any("provenance manifest resolved" in item for item in result.evidence)


def test_install_discovery_blocked_on_missing_manifest(tmp_path: Path) -> None:
    spec = target_spec(tmp_path)
    # Deliberately do not write the manifest.
    result = checks.install_discovery_check(spec, tmp_path)
    assert result.verdict == "BLOCKED"
    assert result.blocking_reasons
    assert spec.manifest_path in result.blocking_reasons[0]


@pytest.mark.parametrize(
    "plugins",
    [
        pytest.param([{"name": "other-plugin"}], id="wrong_name"),
        pytest.param([{"name": "seshat-bi"}], id="missing_source"),
        pytest.param(
            [{"name": "seshat-bi", "source": "./integrations/some-other-bundle"}],
            id="source_points_elsewhere",
        ),
    ],
)
def test_install_discovery_blocked_on_marketplace_entry_not_matching(
    tmp_path: Path, plugins: list[dict]
) -> None:
    """A marketplace entry must match the target's plugin BOTH by ``name``
    AND by a ``source`` path resolving to the target's own bundle
    directory -- a stale or misdirected entry with a matching name (or one
    missing ``source`` entirely) must never be accepted (Codex review
    finding)."""
    spec = target_spec(tmp_path)
    write_json(tmp_path / spec.manifest_path, {"name": "seshat-bi", "version": "0.2.0"})
    write_json(tmp_path / marketplace_path_for(spec.name), {"plugins": plugins})
    result = checks.install_discovery_check(spec, tmp_path)
    assert result.verdict == "BLOCKED"
    assert any(
        "marketplace entry does not list" in reason
        for reason in result.blocking_reasons
    )


def test_install_discovery_pass_with_dict_shaped_source(tmp_path: Path) -> None:
    """Codex's marketplace schema nests the path as ``source.path`` (a dict),
    unlike Claude's plain string ``source`` -- both shapes must resolve."""
    spec = target_spec(tmp_path, name="codex")
    write_json(tmp_path / spec.manifest_path, {"name": "seshat-bi", "version": "0.2.0"})
    bundle_dir = PurePosixPath(spec.manifest_path).parent.parent.as_posix()
    write_json(
        tmp_path / marketplace_path_for(spec.name),
        {
            "plugins": [
                {
                    "name": "seshat-bi",
                    "source": {"source": "local", "path": f"./{bundle_dir}"},
                }
            ]
        },
    )
    write_json(
        tmp_path / spec.provenance_manifest,
        {"target": "codex", "plugin": "seshat-bi", "entries": []},
    )
    result = checks.install_discovery_check(spec, tmp_path)
    assert result.verdict == "PASS"


def test_install_discovery_blocked_on_provenance_identity_mismatch(
    tmp_path: Path,
) -> None:
    spec = target_spec(tmp_path)
    write_json(tmp_path / spec.manifest_path, {"name": "seshat-bi", "version": "0.2.0"})
    write_json(
        tmp_path / marketplace_path_for(spec.name),
        {"plugins": [{"name": "seshat-bi", "source": bundle_source(spec)}]},
    )
    write_json(
        tmp_path / spec.provenance_manifest,
        {"target": "wrong-target", "plugin": "seshat-bi"},
    )
    result = checks.install_discovery_check(spec, tmp_path)
    assert result.verdict == "BLOCKED"
    assert any("identity mismatch" in reason for reason in result.blocking_reasons)
