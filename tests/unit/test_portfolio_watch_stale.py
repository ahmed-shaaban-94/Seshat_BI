"""US3 tests: 'stale' truthful degradation (spec 131, T024, FR-014).

Evidence captured at a revision older than the current HEAD/source_revision
-> ``stale``, citing captured-at vs current; not presented as a current
condition.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat import portfolio_watch as pw
from tests.fixtures.portfolio_watch.builders import (
    commit_all,
    drift_artifact,
    init_git_repo,
    write_json_artifact,
    write_readiness_status,
    write_source_profile,
)

pytestmark = pytest.mark.unit


def test_evidence_captured_at_an_older_revision_is_stale(tmp_path: Path) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")
    write_source_profile(tmp_path, "scope_alpha")
    old_sha = init_git_repo(tmp_path)

    write_json_artifact(
        tmp_path,
        "scope_alpha",
        "drift-findings.json",
        drift_artifact(captured_at_revision=old_sha, class_="column_added"),
    )
    # Move HEAD forward with a new commit, so the artifact's captured_at
    # revision now predates the current HEAD.
    (tmp_path / "unrelated.txt").write_text("change\n", encoding="utf-8")
    commit_all(tmp_path, "advance head")

    summary = pw.build_portfolio_watch_summary(tmp_path)
    finding = next(
        d
        for d in summary["scopes"][0]["dimensions"]
        if d["dimension"] == "source_drift"
    )

    assert finding["state"] == pw.STATE_STALE
    assert old_sha in finding["measured"]
    assert summary["generated_at_revision"] in finding["measured"]


def test_evidence_captured_at_the_current_revision_is_not_stale(tmp_path: Path) -> None:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")
    write_source_profile(tmp_path, "scope_alpha")
    init_git_repo(tmp_path)

    from seshat.portfolio_watch import _source_revision

    current = _source_revision(tmp_path)
    write_json_artifact(
        tmp_path,
        "scope_alpha",
        "drift-findings.json",
        drift_artifact(captured_at_revision=current, class_="column_added"),
    )

    summary = pw.build_portfolio_watch_summary(tmp_path)
    finding = next(
        d
        for d in summary["scopes"][0]["dimensions"]
        if d["dimension"] == "source_drift"
    )

    assert finding["state"] == pw.STATE_COVERED
