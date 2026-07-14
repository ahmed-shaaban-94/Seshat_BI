"""US2 tests: the deterministic sorted set-diff classifier (spec 131, T016).

Given prior + current key sets: ``new = current - prior``,
``resolved = prior - current``, ``unchanged = current & prior``; deterministic
sorted output (FR-008, FR-012, SC-006).
"""

from __future__ import annotations

import pytest

from seshat import portfolio_watch as pw

pytestmark = pytest.mark.unit


def _key(scope: str, n: int) -> tuple[str, str, str, str]:
    return (scope, "readiness", f"class_{n}", f"locator_{n}")


def _prior(keys: frozenset) -> dict:
    return {
        "conditions": keys,
        "scopes": frozenset({"scope_a"}),
        "captured_at_revision": None,
    }


def test_new_resolved_unchanged_are_the_exact_set_arithmetic() -> None:
    prior_keys = frozenset({_key("scope_a", 1), _key("scope_a", 2)})
    current_keys = frozenset({_key("scope_a", 2), _key("scope_a", 3)})

    conditions, scope_changes = pw.classify_changes(
        current_keys, frozenset({"scope_a"}), _prior(prior_keys)
    )

    labels = {c.key: c.label for c in conditions}

    assert labels[_key("scope_a", 3)] == pw.LABEL_NEW
    assert labels[_key("scope_a", 1)] == pw.LABEL_RESOLVED
    assert labels[_key("scope_a", 2)] == pw.LABEL_UNCHANGED
    assert scope_changes == []


def test_diff_is_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    prior_keys = frozenset({_key("scope_a", 1), _key("scope_a", 2)})
    current_keys = frozenset({_key("scope_a", 2), _key("scope_a", 3)})
    prior = _prior(prior_keys)

    run_1 = pw.classify_changes(current_keys, frozenset({"scope_a"}), prior)
    run_2 = pw.classify_changes(current_keys, frozenset({"scope_a"}), prior)

    assert run_1 == run_2


def test_empty_current_and_prior_yields_no_conditions() -> None:
    prior = {
        "conditions": frozenset(),
        "scopes": frozenset(),
        "captured_at_revision": None,
    }
    conditions, scope_changes = pw.classify_changes(frozenset(), frozenset(), prior)
    assert conditions == []
    assert scope_changes == []
