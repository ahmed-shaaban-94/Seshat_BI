"""US3 fail-closed disclosure coverage (spec 127): the scan runs over the
FULL composed bundle body -- not merely the base readiness projection -- so
a sensitive value hiding in enriched lineage, an approval receipt, or a
supplied before/after snapshot still blocks generation (FR-009/FR-010,
INV-4, SC-005). Also exercises the documented write-path guard
(resolve_local_output / disclosure gate) the skill procedure follows."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from seshat.cli.guards import resolve_local_output
from seshat.showcase.build import build_showcase_bundle, render_showcase_html

pytestmark = pytest.mark.integration

_DSN = "postgresql://user:pw@example.internal/warehouse"


def _base_table(
    root: Path, *, blocking_reason: str = "grain needs owner approval"
) -> None:
    table_dir = root / "mappings/orders"
    table_dir.mkdir(parents=True)
    (table_dir / "source-profile.md").write_text("profile\n", encoding="utf-8")
    (table_dir / "readiness-status.yaml").write_text(
        f"""\
table: orders
current_stage: mapping_ready
stages:
  source_ready:
    status: pass
    evidence: [mappings/orders/source-profile.md]
    blocking_reasons: []
  mapping_ready:
    status: blocked
    evidence: []
    blocking_reasons: ["{blocking_reason}"]
blocking_reasons: ["{blocking_reason}"]
approvals: []
next_action: Resolve grain with the data owner.
""",
        encoding="utf-8",
    )


def _write_output(
    tmp_path: Path, bundle: dict, *, output: str = ".seshat-output/showcase/index.html"
) -> Path:
    target = resolve_local_output(tmp_path, output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_showcase_html(bundle, repo=tmp_path), encoding="utf-8")
    return target


def test_secret_in_base_blocking_reason_blocks_generation(tmp_path: Path) -> None:
    _base_table(tmp_path, blocking_reason=f"dsn {_DSN} is unreachable")
    bundle = build_showcase_bundle(tmp_path)
    assert bundle["disclosure"]["status"] == "blocked"
    assert not (tmp_path / ".seshat-output").exists()


def test_secret_reachable_only_via_approval_receipt_blocks_generation(
    tmp_path: Path,
) -> None:
    """The base Explorer projection's own disclosure scan runs BEFORE
    approval receipts are attached (they are added afterward by
    build_explorer_projection), so a secret living ONLY in an approval
    receipt is a value the base scan never saw. The showcase's full-body
    scan must still catch it."""
    _base_table(tmp_path)
    status = tmp_path / "mappings/orders/readiness-status.yaml"
    replacement = (
        "approvals:\n"
        "  - stage: source_ready\n"
        f'    owner: "{_DSN}"\n'
        '    at: "2026-07-01"'
    )
    status.write_text(
        status.read_text(encoding="utf-8").replace("approvals: []", replacement),
        encoding="utf-8",
    )
    bundle = build_showcase_bundle(tmp_path)
    assert bundle["disclosure"]["status"] == "blocked"
    findings = bundle["disclosure"]["findings"]
    assert any(finding["rule"] == "connection_string" for finding in findings)


def test_secret_reachable_only_via_lineage_label_blocks_generation(
    tmp_path: Path,
) -> None:
    """A metric contract's ``name`` becomes a lineage node label, which the
    base projection never scans (it seeds ``lineage`` as empty and Explorer
    fills it in only after the base scan ran)."""
    _base_table(tmp_path)
    metrics = tmp_path / "mappings/orders/metrics"
    metrics.mkdir()
    (metrics / "Leaky.yaml").write_text(f'name: "{_DSN}"\n', encoding="utf-8")
    bundle = build_showcase_bundle(tmp_path)
    assert bundle["disclosure"]["status"] == "blocked"
    findings = bundle["disclosure"]["findings"]
    assert any(finding["rule"] == "connection_string" for finding in findings)


def test_secret_reachable_only_via_supplied_snapshot_blocks_generation(
    tmp_path: Path,
) -> None:
    """A DSN embedded ONLY in a supplied before/after Passport snapshot's
    artifact path must still be caught by the full-body scan, since it never
    appears anywhere in the base readiness projection."""
    _base_table(tmp_path)

    def _snapshot(revision: str, artifact_path: str) -> dict:
        return {
            "schema_version": "1.0",
            "source_revision": revision,
            "scope": ["orders"],
            "readiness": [],
            "artifacts": [{"path": artifact_path, "sha256": None}],
            "approvals": [],
            "validation_boundary": {
                "static": "x",
                "live": "unavailable",
                "unavailable_checks": [],
            },
            "authority_disclaimer": "test",
            "passport_id": "passport-a",
            "generated_at": "2026-07-01T00:00:00+00:00",
        }

    before_path = tmp_path / "before.json"
    after_path = tmp_path / "after.json"
    before_path.write_text(
        json.dumps(_snapshot("1111111111111111111111111111111111111111", "clean.md")),
        encoding="utf-8",
    )
    after_path.write_text(
        json.dumps(_snapshot("2222222222222222222222222222222222222222", _DSN)),
        encoding="utf-8",
    )
    bundle = build_showcase_bundle(tmp_path, snapshots=(before_path, after_path))
    assert bundle["comparison"]["comparable"] is True
    assert bundle["disclosure"]["status"] == "blocked"
    findings = bundle["disclosure"]["findings"]
    assert any(finding["rule"] == "connection_string" for finding in findings)


def test_residual_absolute_path_outside_shared_scanner_prefixes_still_blocks(
    tmp_path: Path,
) -> None:
    """A machine-local absolute path outside the workspace root, under a root
    the shared scan_disclosure scanner's own narrow prefix list (home/Users/
    var/etc/opt/tmp) does NOT cover, must still block generation via the
    composer's own residual-absolute-path invariant."""
    _base_table(tmp_path)

    def _snapshot(revision: str, artifact_path: str) -> dict:
        return {
            "schema_version": "1.0",
            "source_revision": revision,
            "scope": ["orders"],
            "readiness": [],
            "artifacts": [
                {
                    "artifact_id": "evidence:leak",
                    "path": artifact_path,
                    "sha256": "e" * 64,
                }
            ],
            "approvals": [],
            "validation_boundary": {
                "static": "x",
                "live": "unavailable",
                "unavailable_checks": [],
            },
            "authority_disclaimer": "test",
            "passport_id": "passport-a",
            "generated_at": "2026-07-01T00:00:00+00:00",
        }

    before_path = tmp_path / "before.json"
    after_path = tmp_path / "after.json"
    before_path.write_text(
        json.dumps(_snapshot("1111111111111111111111111111111111111111", "clean.md")),
        encoding="utf-8",
    )
    after_path.write_text(
        json.dumps(
            _snapshot(
                "2222222222222222222222222222222222222222",
                "/workspace/client/export.csv",
            )
        ),
        encoding="utf-8",
    )
    bundle = build_showcase_bundle(tmp_path, snapshots=(before_path, after_path))
    assert bundle["comparison"]["comparable"] is True
    assert bundle["disclosure"]["status"] == "blocked"
    findings = bundle["disclosure"]["findings"]
    assert any(finding["rule"] == "residual_absolute_path" for finding in findings)


def test_pass_without_evidence_invariant_is_carried_and_blocks(tmp_path: Path) -> None:
    _base_table(tmp_path)
    status = tmp_path / "mappings/orders/readiness-status.yaml"
    status.write_text(
        status.read_text(encoding="utf-8").replace(
            "  mapping_ready:\n    status: blocked\n    evidence: []\n"
            '    blocking_reasons: ["grain needs owner approval"]',
            "  mapping_ready:\n    status: pass\n    evidence: []\n"
            "    blocking_reasons: []",
        ),
        encoding="utf-8",
    )
    bundle = build_showcase_bundle(tmp_path)
    assert bundle["disclosure"]["status"] == "blocked"
    assert any(
        finding["rule"] == "projection_pass_without_evidence"
        for finding in bundle["disclosure"]["findings"]
    )


def test_uncontained_output_path_is_refused_and_writes_nothing(tmp_path: Path) -> None:
    _base_table(tmp_path)
    bundle = build_showcase_bundle(tmp_path)
    assert bundle["disclosure"]["status"] == "pass"
    with pytest.raises(ValueError):
        _write_output(tmp_path, bundle, output="docs/showcase.html")
    assert not (tmp_path / "docs/showcase.html").exists()


def test_clean_bundle_writes_only_under_contained_output_root(tmp_path: Path) -> None:
    _base_table(tmp_path)
    bundle = build_showcase_bundle(tmp_path)
    assert bundle["disclosure"]["status"] == "pass"
    written = _write_output(tmp_path, bundle)
    assert written.is_relative_to(tmp_path / ".seshat-output")
    assert written.read_text(encoding="utf-8").startswith("<!doctype html>")
