"""Unit tests for DL9 (Report Intent well-formedness / spec 123, US1).

DL9 is a verify-slot-only completeness gate over FILLED
``**/design/report-intent.yaml`` instances (excluding the generic
``templates/report-intent.yaml`` blank and committed test fixtures). It checks
presence-only structural shape:

  * ``audience``, ``supported_decision``, ``review_cadence`` are present and
    non-empty;
  * ``purpose`` is one of the five enum values (FR-002);
  * at least one ``business_questions`` entry with a non-empty ``text``
    (US1 AC#4);
  * ``owner`` is a well-formed "Person Name (class_token)" shape
    (decision_store.owner_shape_ok);
  * ``readiness.status: pass`` is never recorded with an empty ``evidence[]``.

DL9 grants no approval, never judges business content, and never reads/fills
the ``report_intent_approval`` Decision Store slot (a named human owns that
separately). Test pattern mirrors the other design-lint rule tests
(fixture-rooted RuleContext, mirrors DL4/DL6).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.core import RuleContext, Severity
from seshat.rules.report_intent import check_report_intent

pytestmark = pytest.mark.unit

FIXTURES = Path(__file__).parent.parent / "fixtures" / "report_intent_rule"
REPO_ROOT = Path(__file__).parent.parent.parent


def _ctx(*tracked: str, repo_root: Path = FIXTURES) -> RuleContext:
    return RuleContext(repo_root=repo_root, tracked_files=tracked)


# --- User Story 1: a well-formed instance is clean ---------------------------


def test_well_formed_instance_zero_findings() -> None:
    assert list(check_report_intent(_ctx("good/design/report-intent.yaml"))) == []


# --- User Story 2: required-field presence -----------------------------------


def test_missing_purpose_and_questions_errors() -> None:
    findings = list(
        check_report_intent(_ctx("missing_fields/design/report-intent.yaml"))
    )
    assert findings
    assert all(f.severity is Severity.ERROR for f in findings)
    messages = " ".join(f.message for f in findings)
    assert "purpose" in messages
    assert "business_questions" in messages


def test_purpose_outside_enum_errors() -> None:
    findings = list(check_report_intent(_ctx("bad_purpose/design/report-intent.yaml")))
    assert len(findings) == 1
    assert findings[0].severity is Severity.ERROR
    assert "purpose" in findings[0].message
    assert "vibes" in findings[0].message


def test_bad_owner_shape_errors() -> None:
    findings = list(check_report_intent(_ctx("bad_owner/design/report-intent.yaml")))
    assert len(findings) == 1
    assert findings[0].severity is Severity.ERROR
    assert "owner" in findings[0].message


# --- User Story 3: pass-with-empty-evidence never allowed --------------------


def test_pass_with_empty_evidence_errors() -> None:
    findings = list(
        check_report_intent(_ctx("pass_no_evidence/design/report-intent.yaml"))
    )
    assert len(findings) == 1
    assert findings[0].severity is Severity.ERROR
    assert "evidence" in findings[0].message


# --- User Story 4: template + fixture exclusion ------------------------------


def test_generic_template_is_excluded() -> None:
    """The templates/ blank has placeholder values by design; DL9 must never
    fire on it (mirrors the design-lint _TEMPLATE_PATH exclusion)."""
    ctx = _ctx("templates/report-intent.yaml", repo_root=REPO_ROOT)
    assert list(check_report_intent(ctx)) == []


def test_fixture_exemption_excludes_tests_paths() -> None:
    """A report-intent under tests/ is a committed fixture -> exempt
    (is_test_path), even though its content would otherwise error."""
    ctx = _ctx(
        "tests/fixtures/report_intent_rule/missing_fields/design/report-intent.yaml",
        repo_root=REPO_ROOT,
    )
    assert list(check_report_intent(ctx)) == []


def test_no_instances_zero_findings() -> None:
    assert list(check_report_intent(_ctx("warehouse/x.sql", "README.md"))) == []


# --- Live guard: DL9 must be <no-finding> on the real committed tree ---------


def test_no_tenant_or_example_literal_in_rule_source() -> None:
    from seshat.rules import report_intent

    src = Path(report_intent.__file__).read_text(encoding="utf-8")
    for banned in ("pharmacy", "c086", "ezaby"):
        assert banned not in src.lower()
