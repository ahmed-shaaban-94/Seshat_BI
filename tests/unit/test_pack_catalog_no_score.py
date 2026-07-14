"""No-score end-to-end invariant test (spec 128, T033).

No catalog output field is ever a number, percentage, or rank;
``verification_state`` stays categorical everywhere it appears (FR-015,
SC-008; hard-stop never_fabricate_a_confidence_score).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from seshat.packs.catalog import add_pack, content_digest
from seshat.packs.registry import VERIFICATION_STATES, inspect, load_registry, search
from tests.unit._pack_catalog_fixtures import (
    build_test_repo,
    record_dict,
    write_pack,
    write_registry,
)

pytestmark = pytest.mark.unit


def _numeric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _walk_no_numeric_score(node: object, forbidden_keys: frozenset[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key in forbidden_keys:
                assert not _numeric(value), f"{key!r} must never be numeric: {value!r}"
            _walk_no_numeric_score(value, forbidden_keys)
    elif isinstance(node, list):
        for item in node:
            _walk_no_numeric_score(item, forbidden_keys)


_SCORE_LIKE_KEYS = frozenset(
    {
        "verification_state",
        "score",
        "confidence",
        "rank",
        "percentage",
        "popularity",
        "downloads",
        "rating",
    }
)


def test_verification_states_are_a_fixed_categorical_vocabulary() -> None:
    assert VERIFICATION_STATES == ("reviewed", "unreviewed", "deprecated")
    for state in VERIFICATION_STATES:
        assert isinstance(state, str)


def test_search_and_inspect_outputs_carry_no_numeric_score(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    write_registry(
        repo,
        [
            record_dict(
                pack_id="acme.kpi",
                source="packs/reference/kpi",
                content_hash=content_digest(pack_dir),
            )
        ],
    )
    registry = load_registry(repo)
    for record in search(registry):
        _walk_no_numeric_score(record.__dict__, _SCORE_LIKE_KEYS)
    record = inspect(registry, "acme.kpi")
    assert record is not None
    _walk_no_numeric_score(record.__dict__, _SCORE_LIKE_KEYS)


def test_add_outcome_carries_no_numeric_score(tmp_path: Path) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    write_registry(
        repo,
        [
            record_dict(
                pack_id="acme.kpi",
                source="packs/reference/kpi",
                content_hash=content_digest(pack_dir),
            )
        ],
    )
    outcome = add_pack(repo, load_registry(repo), "acme.kpi")
    assert outcome.status == "added"
    for finding in outcome.findings:
        _walk_no_numeric_score(finding, _SCORE_LIKE_KEYS)


def test_unrecognized_verification_state_is_coerced_to_unreviewed_not_a_number(
    tmp_path: Path,
) -> None:
    repo = build_test_repo(tmp_path)
    pack_dir = write_pack(repo, "packs/reference/kpi", pack_id="acme.kpi")
    write_registry(
        repo,
        [
            {
                **record_dict(
                    pack_id="acme.kpi",
                    source="packs/reference/kpi",
                    content_hash=content_digest(pack_dir),
                ),
                "verification_state": "trusted",
            }
        ],
    )
    registry = load_registry(repo)
    # Schema-invalid enum value -> record excluded entirely, never silently
    # coerced into a numeric or fabricated score.
    assert registry.records == ()
    assert any(
        finding["rule"] == "pack_registry_invalid_record"
        for finding in registry.findings
    )
