"""Fixtures + honest-skip precondition chain for the local live-validation suite.

Spec 082 (``specs/082-postgres-live-validation-suite/``); the precondition contract
is ``contracts/live-pass-contract.md``.

The single load-bearing rule (FR-009, hard "no hidden live pass"): a live check may
report a completed live outcome ONLY when ALL five preconditions hold. Any failure
collapses to ``pytest.skip(reason=<named reason>)`` -- never a pass, never a silent
omission, never a swallowed exception. The five named reasons are mutually distinct
so a reviewer can tell which precondition failed without reading source.

testcontainers is imported LAZILY inside ``_start_container`` (never at module
scope), and each live_db test module ``pytest.importorskip``s it, so pytest can
COLLECT this suite even when the ``livetest`` extra is not installed (e.g. in CI,
which installs only ``dev``). Collection-import failure would be a hard error, not a
skip -- the lazy import + importorskip is what keeps the honest-skip promise real.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass

import pytest

_SEEDS_DIR = pathlib.Path(__file__).parent / "seeds"

# The five named precondition-failure reasons (contracts/live-pass-contract.md).
# Kept as a module constant so the runtime chain and the US4 mock tests agree on the
# exact strings (a reviewer acts on these; genericness would defeat FR-014).
REASON_DOCKER = "docker not available"
REASON_DRIVER = "driver not installed"
REASON_CONTAINER = "container failed to start"
REASON_PORT = "port conflict"
REASON_SEED = "seed failed"


@dataclass(frozen=True)
class ContainerHandle:
    """A ready, seeded ephemeral Postgres container (data-model.md section 3).

    ``dsn`` is valid only for the container's lifetime; never logged unredacted.
    """

    dsn: str


def docker_available() -> tuple[bool, str | None]:
    """Pure, mockable Docker-availability probe.

    Returns ``(True, None)`` when a Docker client can be constructed and pinged,
    else ``(False, REASON_DOCKER)``. Imports the docker client lazily so this
    module collects without the ``livetest`` extra. Never raises: any failure is
    reported as unavailable, so the caller skips honestly rather than erroring.
    """
    try:
        import docker  # lazy: only when actually probing
    except Exception:
        return (False, REASON_DOCKER)
    try:
        client = docker.from_env()
        client.ping()
        return (True, None)
    except Exception:
        return (False, REASON_DOCKER)


def driver_available() -> tuple[bool, str | None]:
    """Pure, mockable psycopg2-availability probe (precondition #2).

    Distinct from Docker availability: the pytest environment may have Docker but
    not the ``db`` extra. Returns ``(True, None)`` or ``(False, REASON_DRIVER)``.
    """
    try:
        import psycopg2  # noqa: F401  -- import-presence probe only
    except Exception:
        return (False, REASON_DRIVER)
    return (True, None)


def _run_sql_file(dsn: str, sql_path: pathlib.Path) -> None:
    """Execute a .sql file against ``dsn`` via psycopg2 (precondition #4 helper).

    Raises on any SQL error so the fixture can map it to REASON_SEED. psycopg2 is
    imported lazily -- this helper is only reached after ``driver_available()`` held.
    """
    import psycopg2  # lazy

    conn = psycopg2.connect(dsn)
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(sql_path.read_text(encoding="utf-8"))
    finally:
        conn.close()


def seed_container(handle: ContainerHandle, scenario_file: str) -> None:
    """Run schema.sql then the named scenario .sql against the container.

    Raises on SQL error (the fixture maps that to a REASON_SEED skip). Kept as a
    standalone function so a US4 test can mock it to force the seed-failure path.
    """
    _run_sql_file(handle.dsn, _SEEDS_DIR / "schema.sql")
    _run_sql_file(handle.dsn, _SEEDS_DIR / scenario_file)


def _start_container():
    """Start an ephemeral Postgres container, returning (dsn, stop_callable).

    testcontainers is imported HERE, lazily -- never at module scope -- so this file
    collects without the ``livetest`` extra installed. Raises on start failure; the
    fixture maps a timeout/start error to REASON_CONTAINER and a bind error to
    REASON_PORT.
    """
    from testcontainers.postgres import PostgresContainer  # lazy

    container = PostgresContainer("postgres:16-alpine")
    container.start()
    dsn = container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql://"
    )
    return dsn, container.stop


@pytest.fixture
def live_db_container(request):
    """The single fixture every US1-US3 live test depends on.

    Walks the five preconditions in contract order; on the first failure it
    ``pytest.skip``s with that precondition's named reason. Only when all hold does
    it yield a ready, seeded ``ContainerHandle``. Teardown always stops the
    container, even on a mid-test failure.

    The scenario seed file is passed via ``@pytest.mark.seed("seed_clean.sql")`` on
    the test (or defaults to ``seed_clean.sql``).
    """
    marker = request.node.get_closest_marker("seed")
    scenario_file = marker.args[0] if marker else "seed_clean.sql"

    ok, reason = docker_available()
    if not ok:
        pytest.skip(reason)
    ok, reason = driver_available()
    if not ok:
        pytest.skip(reason)

    try:
        dsn, stop = _start_container()
    except Exception as exc:  # start/bind failure -> honest skip, never a pass
        text = str(exc).lower()
        if "port" in text or "address already in use" in text or "bind" in text:
            pytest.skip(REASON_PORT)
        pytest.skip(REASON_CONTAINER)
        return  # unreachable; keeps type-checkers happy

    handle = ContainerHandle(dsn=dsn)
    try:
        try:
            seed_container(handle, scenario_file)
        except Exception:
            pytest.skip(REASON_SEED)
        yield handle
    finally:
        stop()
