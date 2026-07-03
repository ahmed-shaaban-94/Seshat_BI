"""US4: honest pending/skipped reporting for every precondition failure (spec 082).

These tests mock each of the five preconditions in isolation and assert the fixture
chain raises ``pytest.skip`` with the correct NAMED reason -- never a raw exception,
never a silent pass, never a reported Finding. They deliberately do NOT require
Docker or the ``livetest`` extra (they mock before any real container/driver is
touched), so they run and are meaningful on ANY machine -- including CI. This is
the concrete proof of the "no hidden live pass" discipline (live-pass-contract.md).

Marked ``live_db`` (so ``pytest -m unit`` deselects them alongside the real live
tests), but unlike the real live tests they pass without Docker.
"""

import pytest

from tests.live_db import conftest

pytestmark = pytest.mark.live_db


def _drive_fixture(request):
    """Drive the live_db_container generator fixture to its first yield/skip.

    Returns the yielded handle, or re-raises the pytest.skip the chain raised.
    """
    gen = conftest.live_db_container.__wrapped__(request)
    return next(gen)


class _Req:
    """Minimal stand-in for a pytest request: no ``seed`` marker -> default seed."""

    class _Node:
        def get_closest_marker(self, name):
            return None

    node = _Node()


def test_docker_absent_skips_with_reason(monkeypatch):
    """T027: Docker absent -> skip 'docker not available', not an exception/pass."""
    monkeypatch.setattr(
        conftest, "docker_available", lambda: (False, conftest.REASON_DOCKER)
    )
    with pytest.raises(pytest.skip.Exception) as exc:
        _drive_fixture(_Req())
    assert conftest.REASON_DOCKER in str(exc.value)


def test_driver_missing_skips_with_reason(monkeypatch):
    """T028: driver absent -> skip 'driver not installed' (distinct from Docker)."""
    monkeypatch.setattr(conftest, "docker_available", lambda: (True, None))
    monkeypatch.setattr(
        conftest, "driver_available", lambda: (False, conftest.REASON_DRIVER)
    )
    with pytest.raises(pytest.skip.Exception) as exc:
        _drive_fixture(_Req())
    assert conftest.REASON_DRIVER in str(exc.value)


def test_container_start_timeout_skips_with_reason(monkeypatch):
    """T029: container start failure -> skip 'container failed to start'."""
    monkeypatch.setattr(conftest, "docker_available", lambda: (True, None))
    monkeypatch.setattr(conftest, "driver_available", lambda: (True, None))

    def _boom():
        raise RuntimeError("readiness wait exceeded timeout")

    monkeypatch.setattr(conftest, "_start_container", _boom)
    with pytest.raises(pytest.skip.Exception) as exc:
        _drive_fixture(_Req())
    assert conftest.REASON_CONTAINER in str(exc.value)


def test_port_conflict_skips_with_reason(monkeypatch):
    """T030: a port-bind failure -> skip 'port conflict' (distinct from timeout)."""
    monkeypatch.setattr(conftest, "docker_available", lambda: (True, None))
    monkeypatch.setattr(conftest, "driver_available", lambda: (True, None))

    def _boom():
        raise RuntimeError("bind: address already in use on host port")

    monkeypatch.setattr(conftest, "_start_container", _boom)
    with pytest.raises(pytest.skip.Exception) as exc:
        _drive_fixture(_Req())
    assert conftest.REASON_PORT in str(exc.value)


def test_seed_failure_skips_with_reason(monkeypatch):
    """T031: a seed SQL error -> skip 'seed failed', and NO Finding is reported."""
    monkeypatch.setattr(conftest, "docker_available", lambda: (True, None))
    monkeypatch.setattr(conftest, "driver_available", lambda: (True, None))
    monkeypatch.setattr(
        conftest, "_start_container", lambda: ("postgresql://x", lambda: None)
    )

    def _boom(handle, scenario_file):
        raise RuntimeError("relation does not exist")

    monkeypatch.setattr(conftest, "seed_container", _boom)
    with pytest.raises(pytest.skip.Exception) as exc:
        _drive_fixture(_Req())
    assert conftest.REASON_SEED in str(exc.value)


def test_all_five_reasons_are_distinct_strings():
    """T032: the five named precondition reasons are pairwise distinct."""
    reasons = [
        conftest.REASON_DOCKER,
        conftest.REASON_DRIVER,
        conftest.REASON_CONTAINER,
        conftest.REASON_PORT,
        conftest.REASON_SEED,
    ]
    assert len(set(reasons)) == len(reasons)
