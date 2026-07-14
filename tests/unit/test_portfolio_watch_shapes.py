"""Foundational shape tests for Portfolio Watch (spec 131, T007).

Asserts: the dataclasses are frozen; the degradation/label sets are exactly
the closed sets from data-model.md; the governed-scope enumerator lists every
fixture scope and opens no DB connection (no ``Dialect``/DSN import anywhere
on its import path).
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from seshat import portfolio_watch as pw
from tests.fixtures.portfolio_watch.builders import write_readiness_status

pytestmark = pytest.mark.unit

_MODULE_SOURCE = Path(pw.__file__).read_text(encoding="utf-8")


def test_degradation_states_are_the_closed_set() -> None:
    assert pw.DEGRADATION_STATES == frozenset(
        {
            "covered",
            "[PENDING LIVE]",
            "stale",
            "not_applicable_with_reason",
            "unreadable",
        }
    )


def test_change_labels_are_the_closed_set() -> None:
    assert pw.CHANGE_LABELS == frozenset(
        {"new", "resolved", "unchanged", "current_condition_no_baseline"}
    )


@pytest.mark.parametrize(
    "cls,kwargs",
    [
        (
            pw.DimensionItem,
            {"class_": "column_removed", "subject_locator": "widget_id"},
        ),
        (
            pw.CoveredDimensionFinding,
            {"dimension": "readiness", "state": "covered"},
        ),
        (
            pw.PrioritizedNextAction,
            {"category": "readiness", "action": "do the next thing"},
        ),
        (
            pw.ConditionChange,
            {
                "key": ("scope_alpha", "readiness", "blocked", "mapping_ready"),
                "label": "new",
            },
        ),
        (
            pw.GovernedScope,
            {
                "scope_id": "scope_alpha",
                "source_path": "mappings/scope_alpha/readiness-status.yaml",
                "current_stage": "mapping_ready",
            },
        ),
    ],
)
def test_dataclasses_are_frozen(cls: type, kwargs: dict) -> None:
    instance = cls(**kwargs)
    first_field = dataclasses.fields(cls)[0].name
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(instance, first_field, getattr(instance, first_field))


def test_covered_dimension_finding_rejects_an_invented_state() -> None:
    with pytest.raises(ValueError):
        pw.CoveredDimensionFinding(dimension="readiness", state="mostly_fine")


def test_condition_change_rejects_an_invented_label() -> None:
    with pytest.raises(ValueError):
        pw.ConditionChange(key=("a", "b", "c", "d"), label="kinda_new")


def test_enumerator_lists_every_fixture_scope(tmp_path: Path) -> None:
    write_readiness_status(tmp_path, "scope_alpha")
    write_readiness_status(tmp_path, "scope_beta")
    write_readiness_status(tmp_path, "scope_gamma")

    scopes = pw.enumerate_governed_scopes(tmp_path)

    assert {s.scope_id for s in scopes} == {"scope_alpha", "scope_beta", "scope_gamma"}
    assert all(
        s.source_path == f"mappings/{s.scope_id}/readiness-status.yaml" for s in scopes
    )


def test_enumerator_is_empty_on_a_repo_with_no_mappings(tmp_path: Path) -> None:
    assert pw.enumerate_governed_scopes(tmp_path) == ()


def test_module_never_imports_a_db_touching_seam() -> None:
    """Static grep-assert: no Dialect/DSN-touching module is IMPORTED anywhere
    on portfolio_watch.py's import path (SEC-001, research D6). Scoped to
    actual import statements (not prose) so the module's own docstring, which
    explains what it deliberately does NOT import, does not self-trigger."""
    import_lines = [
        line
        for line in _MODULE_SOURCE.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    ]
    forbidden = ("dialect", "portfolio_enumerate", "validate", "psycopg2")
    for line in import_lines:
        for token in forbidden:
            assert token not in line, f"forbidden import found: {line!r}"


def test_running_the_enumerator_never_loads_a_db_module(tmp_path: Path) -> None:
    """Subprocess isolation: another test module in the same pytest process may
    already have imported seshat.dialect, so the only reliable check is a
    fresh interpreter."""
    import os
    import subprocess
    import sys

    write_readiness_status(tmp_path, "scope_alpha")
    src_root = str(Path(pw.__file__).resolve().parents[1])
    env = dict(os.environ, PYTHONPATH=src_root)
    code = (
        "import sys\n"
        "from seshat import portfolio_watch as pw\n"
        f"pw.enumerate_governed_scopes({str(tmp_path)!r})\n"
        "print('seshat.dialect' in sys.modules)\n"
        "print('seshat.portfolio_enumerate' in sys.modules)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    dialect_loaded, enumerate_loaded = result.stdout.splitlines()
    assert dialect_loaded == "False"
    assert enumerate_loaded == "False"
