"""Unit tests for DL7 (formatting-plan ledger well-formedness)."""

from __future__ import annotations

from pathlib import Path

import pytest

from retail.core import RuleContext, Severity
from retail.rules.formatting_plan import RULE_ID, check_formatting_plan

pytestmark = pytest.mark.unit

FIXTURES = Path(__file__).parent.parent / "fixtures" / "formatting_plan"


def _ctx(stem: str) -> RuleContext:
    # DL7 discovers files by the ``formatting-plan.md`` suffix, so every fixture
    # is named ``<stem>-formatting-plan.md``; the test refers to it by stem.
    return RuleContext(
        repo_root=FIXTURES, tracked_files=(f"{stem}-formatting-plan.md",)
    )


def test_clean_ledger_passes() -> None:
    assert list(check_formatting_plan(_ctx("clean"))) == []


def test_missing_principle_fails() -> None:
    f = list(check_formatting_plan(_ctx("bad_missing_principle")))
    assert any(x.rule_id == RULE_ID for x in f)
    assert any("principle" in x.message.lower() for x in f)


def test_unresolvable_principle_fails() -> None:
    f = list(check_formatting_plan(_ctx("bad_unresolvable_principle")))
    assert any("#99" in x.message or "resolve" in x.message.lower() for x in f)


def test_render_only_cited_as_resolved_fails() -> None:
    f = list(check_formatting_plan(_ctx("bad_render_only_resolved")))
    assert any("render-only" in x.message.lower() for x in f)


def test_score_field_fails() -> None:
    f = list(check_formatting_plan(_ctx("bad_has_score")))
    assert any("score" in x.message.lower() for x in f)


def test_agent_ratified_fails() -> None:
    f = list(check_formatting_plan(_ctx("bad_agent_ratified")))
    assert any("ratif" in x.message.lower() for x in f)


def test_out_of_allowlist_container_fails() -> None:
    f = list(check_formatting_plan(_ctx("bad_out_of_allowlist")))
    assert any("allow-list" in x.message.lower() for x in f)


def test_severity_is_error() -> None:
    f = list(check_formatting_plan(_ctx("bad_has_score")))
    assert all(x.severity is Severity.ERROR for x in f)


def test_test_fixtures_are_exempt_when_under_tests_path() -> None:
    ctx = RuleContext(
        repo_root=FIXTURES,
        tracked_files=(
            "tests/fixtures/formatting_plan/bad_has_score-formatting-plan.md",
        ),
    )
    assert list(check_formatting_plan(ctx)) == []
