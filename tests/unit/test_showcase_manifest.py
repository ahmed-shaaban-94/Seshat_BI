"""Four-category disclosure manifest unit coverage (spec 127, US3)."""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.showcase.manifest import (
    build_manifest,
    find_residual_absolute_paths,
    normalize_portability,
)

pytestmark = pytest.mark.unit


def _mixed_tables() -> list[dict]:
    return [
        {
            "table_id": "orders",
            "source_path": "mappings/orders/readiness-status.yaml",
            "stages": {
                "source_ready": {
                    "status": "pass",
                    "evidence": [
                        {
                            "reference": "mappings/orders/source-profile.md",
                            "state": "available",
                        }
                    ],
                    "blocking_reasons": [],
                },
                "silver_ready": {
                    "status": "warning",
                    "evidence": [
                        {"reference": "[PENDING LIVE PROFILE]", "state": "deferred"}
                    ],
                    "blocking_reasons": [],
                },
                "gold_ready": {
                    "status": "blocked",
                    "evidence": [
                        {
                            "reference": "mappings/orders/missing.md",
                            "state": "missing",
                        }
                    ],
                    "blocking_reasons": ["reconciliation report not yet produced"],
                },
            },
        },
        {
            "table_id": "broken",
            "source_path": "mappings/broken/readiness-status.yaml",
            "input_defect": "readiness-status.yaml is not an interpretable mapping",
            "stages": {},
        },
    ]


def _lineage() -> dict:
    return {
        "nodes": [
            {
                "node_id": "metric:orders:NetSales",
                "kind": "metric_contract",
                "label": "NetSales",
                "evidence": "mappings/orders/metrics/NetSales.yaml",
            },
            {
                "node_id": "defect:mappings/orders/metrics/Broken.yaml",
                "kind": "input_defect",
                "label": "unreadable metric contract",
                "evidence": "mappings/orders/metrics/Broken.yaml",
            },
        ],
        "edges": [],
    }


def _table_references(table: dict) -> set[str]:
    if "input_defect" in table:
        return {table["source_path"]}
    return {
        f"{table['table_id']}#{stage}:{item['reference']}"
        for stage, block in table["stages"].items()
        for item in block["evidence"]
    }


def _all_references(tables: list[dict], lineage: dict) -> set[str]:
    references: set[str] = set()
    for table in tables:
        references |= _table_references(table)
    references |= {node["node_id"] for node in lineage["nodes"]}
    return references


def test_every_composed_item_appears_under_exactly_one_category() -> None:
    tables = _mixed_tables()
    lineage = _lineage()
    manifest = build_manifest(tables, lineage, redactions=[])
    expected = _all_references(tables, lineage)
    seen: dict[str, str] = {}
    for category in ("included", "unavailable", "omitted", "redacted"):
        for entry in manifest[category]:
            assert entry["locator"] not in seen, "locator appears in >1 category"
            seen[entry["locator"]] = category
    assert set(seen) == expected


def test_available_evidence_is_included() -> None:
    manifest = build_manifest(_mixed_tables(), _lineage(), redactions=[])
    locators = {entry["locator"] for entry in manifest["included"]}
    assert any("source-profile.md" in locator for locator in locators)


def test_deferred_evidence_is_unavailable() -> None:
    manifest = build_manifest(_mixed_tables(), _lineage(), redactions=[])
    locators = {entry["locator"] for entry in manifest["unavailable"]}
    assert any("PENDING LIVE PROFILE" in locator for locator in locators)


def test_missing_evidence_and_input_defect_are_omitted() -> None:
    manifest = build_manifest(_mixed_tables(), _lineage(), redactions=[])
    locators = {entry["locator"] for entry in manifest["omitted"]}
    assert any("missing.md" in locator for locator in locators)
    assert "mappings/broken/readiness-status.yaml" in locators


def test_unreadable_metric_contract_is_omitted() -> None:
    manifest = build_manifest(_mixed_tables(), _lineage(), redactions=[])
    locators = {entry["locator"] for entry in manifest["omitted"]}
    assert "defect:mappings/orders/metrics/Broken.yaml" in locators


def test_absolute_path_normalizes_to_repo_relative_and_is_redacted(
    tmp_path: Path,
) -> None:
    target = tmp_path / "mappings" / "orders" / "source-profile.md"
    target.parent.mkdir(parents=True)
    target.write_text("profile\n", encoding="utf-8")
    document = {"reference": str(target)}
    normalized, redactions = normalize_portability(tmp_path, document)
    assert normalized["reference"] == "mappings/orders/source-profile.md"
    assert len(redactions) == 1
    assert redactions[0]["category"] == "redacted"
    assert redactions[0]["original_class"] == "absolute_path"


def test_private_url_is_stripped_and_redacted(tmp_path: Path) -> None:
    document = {"note": "dashboard at http://reports.internal/dash for review"}
    normalized, redactions = normalize_portability(tmp_path, document)
    assert "reports.internal" not in normalized["note"]
    assert "[private URL removed]" in normalized["note"]
    assert redactions[0]["original_class"] == "private_url"


def test_foreign_absolute_path_outside_root_is_left_for_the_scanner(
    tmp_path: Path,
) -> None:
    """An absolute path that does not resolve inside the workspace root is
    NOT silently rewritten -- it survives so the disclosure scan can block it
    (FR-010/FR-019); normalization never invents a fake relative path."""
    document = {"reference": "/home/someone/outside/file.csv"}
    normalized, redactions = normalize_portability(tmp_path, document)
    assert normalized["reference"] == "/home/someone/outside/file.csv"
    assert redactions == []


def test_absolute_path_outside_the_fixed_prefix_whitelist_still_normalizes(
    tmp_path: Path,
) -> None:
    """A workspace mounted at a root not in the old home/Users/var/etc/opt/tmp
    whitelist (e.g. a container mount like /workspace/...) must still be
    detected as absolute and reduced to repo-relative when it resolves inside
    the workspace root -- any absolute path is disclosure-sensitive, not just
    a fixed prefix list."""
    root = tmp_path / "workspace" / "Seshat_BI"
    target = root / "mappings" / "orders" / "source-profile.md"
    target.parent.mkdir(parents=True)
    target.write_text("profile\n", encoding="utf-8")
    document = {"reference": str(target)}
    normalized, redactions = normalize_portability(root, document)
    assert normalized["reference"] == "mappings/orders/source-profile.md"
    assert len(redactions) == 1
    assert redactions[0]["original_class"] == "absolute_path"


def test_multiple_private_urls_in_one_value_are_all_stripped(
    tmp_path: Path,
) -> None:
    """A single value naming more than one private/internal URL must have
    every occurrence stripped, not just the first match -- otherwise a
    residual internal endpoint would leak into the rendered bundle."""
    document = {
        "note": (
            "primary at http://reports.internal/dash, "
            "mirror at http://10.0.0.5:8080/dash"
        )
    }
    normalized, redactions = normalize_portability(tmp_path, document)
    assert "reports.internal" not in normalized["note"]
    assert "10.0.0.5" not in normalized["note"]
    assert normalized["note"].count("[private URL removed]") == 2
    assert redactions[0]["original_class"] == "private_url"


def test_residual_absolute_path_outside_a_narrow_prefix_is_still_found(
    tmp_path: Path,
) -> None:
    """A residual absolute path outside the workspace root, under a root the
    shared scan_disclosure scanner's own narrow prefix list (home/Users/var/
    etc/opt/tmp) does NOT cover -- e.g. a container mount like
    /workspace/client/... -- must still be found by the composer's own
    invariant so generation still fails closed regardless of the shared
    scanner's coverage."""
    document = {"reference": "/workspace/client/export.csv"}
    normalized, _redactions = normalize_portability(tmp_path, document)
    # Outside tmp_path's root: left unchanged by normalization (as designed).
    assert normalized["reference"] == "/workspace/client/export.csv"

    findings = find_residual_absolute_paths(normalized)
    assert len(findings) == 1
    assert findings[0]["rule"] == "residual_absolute_path"
    assert findings[0]["locator"] == "$.reference"


def test_residual_absolute_path_under_the_narrow_prefix_is_also_found(
    tmp_path: Path,
) -> None:
    """Sanity check: a path under one of the shared scanner's own listed
    prefixes is found too (the composer's invariant is a superset, not a
    replacement, of the shared scanner's coverage)."""
    document = {"reference": "/home/someone/outside/file.csv"}
    normalized, _redactions = normalize_portability(tmp_path, document)
    findings = find_residual_absolute_paths(normalized)
    assert len(findings) == 1


def test_no_residual_finding_once_normalized_to_repo_relative(
    tmp_path: Path,
) -> None:
    """A path that normalization successfully rewrote to repo-relative form
    must NOT be re-flagged as residual."""
    target = tmp_path / "mappings" / "orders" / "source-profile.md"
    target.parent.mkdir(parents=True)
    target.write_text("profile\n", encoding="utf-8")
    document = {"reference": str(target)}
    normalized, _redactions = normalize_portability(tmp_path, document)
    assert find_residual_absolute_paths(normalized) == []


def test_embedded_absolute_path_mid_sentence_is_normalized(tmp_path: Path) -> None:
    """A path embedded after other text (a blocking reason like "see
    /workspace/.../foo for details") must be found and reduced, not only a
    value that IS a path in its entirety -- both the absolute-path rule and
    the residual-path walk were previously start-anchored and missed this."""
    target = tmp_path / "mappings" / "orders" / "source-profile.md"
    target.parent.mkdir(parents=True)
    target.write_text("profile\n", encoding="utf-8")
    document = {"note": f"see {target} for details"}
    normalized, redactions = normalize_portability(tmp_path, document)
    assert normalized["note"] == "see mappings/orders/source-profile.md for details"
    assert redactions[0]["original_class"] == "absolute_path"
    assert find_residual_absolute_paths(normalized) == []


def test_embedded_absolute_path_outside_root_is_still_found_residually(
    tmp_path: Path,
) -> None:
    """The same embedded-path case, but outside the workspace root: left
    unchanged by normalization, and still caught by the residual-path
    walk -- not only when the whole value is a path."""
    document = {"note": "see /workspace/client/export.csv for the raw file"}
    normalized, redactions = normalize_portability(tmp_path, document)
    assert normalized["note"] == document["note"]
    assert redactions == []
    findings = find_residual_absolute_paths(normalized)
    assert len(findings) == 1
    assert findings[0]["rule"] == "residual_absolute_path"


def test_private_urls_are_never_mistaken_for_absolute_paths(tmp_path: Path) -> None:
    """Guard against the embedded-path search over-matching: a private/
    internal URL's path component must not be treated as a filesystem path by
    the absolute-path rule (that is `_normalize_private_url`'s job)."""
    document = {
        "note": (
            "primary at http://reports.internal/dash, "
            "mirror at http://10.0.0.5:8080/dash"
        )
    }
    normalized, redactions = normalize_portability(tmp_path, document)
    assert "[private URL removed]" in normalized["note"]
    assert all(r["original_class"] != "absolute_path" for r in redactions)
    assert find_residual_absolute_paths(normalized) == []


def test_html_closing_tags_are_never_mistaken_for_absolute_paths(
    tmp_path: Path,
) -> None:
    """Regression: rendered SVG/HTML markup like "</text></svg>" must not be
    flagged as a residual absolute path -- a "/" immediately after "<" is a
    closing tag, never a filesystem path."""
    document = {
        "svg": (
            '<svg xmlns="http://www.w3.org/2000/svg"><text>Gold: blocked</text></svg>'
        )
    }
    normalized, redactions = normalize_portability(tmp_path, document)
    assert normalized == document
    assert redactions == []
    assert find_residual_absolute_paths(normalized) == []
