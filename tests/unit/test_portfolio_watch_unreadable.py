"""US3 tests: 'unreadable' truthful degradation (spec 131, T026, FR-016/FR-022).

An evidence artifact declaring an unknown schema version -> ``unreadable``
(naming the version); excluded from any pass/clean claim. A per-scope read
error (malformed JSON) degrades that dimension to ``unreadable``, never a
fabricated pass.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat import portfolio_watch as pw
from tests.fixtures.portfolio_watch.builders import write_readiness_status

pytestmark = pytest.mark.unit


def _write_raw(root: Path, scope_dir: str, filename: str, text: str) -> None:
    path = root / "mappings" / scope_dir / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_unknown_schema_version_is_unreadable_and_names_the_version(
    tmp_path: Path,
) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")
    _write_raw(
        tmp_path,
        "scope_alpha",
        "review-result.json",
        '{"schema_version": "7.3", "class": "ok"}',
    )

    summary = pw.build_portfolio_watch_summary(tmp_path)
    finding = next(
        d for d in summary["scopes"][0]["dimensions"] if d["dimension"] == "review"
    )

    assert finding["state"] == pw.STATE_UNREADABLE
    assert "7.3" in finding["measured"]


def test_malformed_json_is_unreadable_never_a_fabricated_pass(tmp_path: Path) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")
    _write_raw(tmp_path, "scope_alpha", "review-result.json", "{not valid json at all")

    summary = pw.build_portfolio_watch_summary(tmp_path)
    finding = next(
        d for d in summary["scopes"][0]["dimensions"] if d["dimension"] == "review"
    )

    assert finding["state"] == pw.STATE_UNREADABLE
    assert finding["state"] != pw.STATE_COVERED


def test_artifact_missing_a_class_field_is_unreadable(tmp_path: Path) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")
    _write_raw(
        tmp_path,
        "scope_alpha",
        "review-result.json",
        '{"schema_version": "1.0", "captured_at_revision": null}',
    )

    summary = pw.build_portfolio_watch_summary(tmp_path)
    finding = next(
        d for d in summary["scopes"][0]["dimensions"] if d["dimension"] == "review"
    )

    assert finding["state"] == pw.STATE_UNREADABLE


def test_readiness_dimension_unreadable_when_readiness_status_is_malformed(
    tmp_path: Path,
) -> None:
    path = tmp_path / "mappings" / "scope_alpha" / "readiness-status.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{this is not valid: yaml: [", encoding="utf-8")

    summary = pw.build_portfolio_watch_summary(tmp_path)

    # The scope is still listed (never silently dropped, FR-022/FR-017)...
    assert summary["scopes"][0]["scope_id"] == "scope_alpha"
    readiness_finding = next(
        d for d in summary["scopes"][0]["dimensions"] if d["dimension"] == "readiness"
    )
    assert readiness_finding["state"] == pw.STATE_UNREADABLE
