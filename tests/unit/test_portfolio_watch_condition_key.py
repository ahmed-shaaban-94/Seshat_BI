"""US2 tests: the Condition Key is magnitude-free (spec 131, T015).

The Condition Key is the tuple ``(scope_id, dimension, class, subject_
locator)`` -- a magnitude wiggle on the same class produces the SAME key (no
diff-churn noise, research D3, SNAP-4, FR-010).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat import portfolio_watch as pw
from tests.fixtures.portfolio_watch.builders import (
    drift_artifact,
    write_json_artifact,
    write_readiness_status,
    write_source_profile,
)

pytestmark = pytest.mark.unit


def _build(tmp_path: Path, measured: str) -> dict:
    write_readiness_status(tmp_path, "scope_alpha", current_stage="source_ready")
    write_source_profile(tmp_path, "scope_alpha")
    write_json_artifact(
        tmp_path,
        "scope_alpha",
        "drift-findings.json",
        drift_artifact(
            class_="missingness_shift",
            measured="unused-aggregate",
            items=[
                {
                    "class": "missingness_shift",
                    "subject_locator": "widget_id",
                    "measured": measured,
                }
            ],
        ),
    )
    return pw.build_portfolio_watch_summary(tmp_path)


def test_a_magnitude_wiggle_on_the_same_class_does_not_change_the_key(
    tmp_path: Path,
) -> None:
    summary_1 = _build(tmp_path, "missing 3.1% -> 11.7%")

    # Overwrite the SAME artifact with only the magnitude changed.
    summary_2 = _build(tmp_path, "missing 3.1% -> 99.9%")

    keys_1 = pw.condition_keys_from_summary(summary_1)
    keys_2 = pw.condition_keys_from_summary(summary_2)

    assert keys_1 == keys_2
    assert keys_1 == frozenset(
        {("scope_alpha", "source_drift", "missingness_shift", "widget_id")}
    )


def test_a_different_class_or_locator_is_a_different_key(tmp_path: Path) -> None:
    summary = _build(tmp_path, "missing 3.1% -> 11.7%")
    keys = pw.condition_keys_from_summary(summary)

    assert ("scope_alpha", "source_drift", "column_removed", "widget_id") not in keys
    assert ("scope_alpha", "source_drift", "missingness_shift", "other_col") not in keys
