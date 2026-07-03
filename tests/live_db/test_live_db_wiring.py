"""US4 wiring guards for the live-DB suite (spec 082).

Static guards on top of the runtime honest-skip tests:
- every test in tests/live_db/ carries @pytest.mark.live_db (so `pytest -m unit`
  never accidentally runs a Docker-dependent test);
- no silent ``except ...: pass`` swallows a Docker/psycopg2 call (the forbidden
  shape from contracts/live-pass-contract.md -- a swallowed failure could hide a
  live pass).

Runnable on any machine (pure source scans; no Docker, no testcontainers).
"""

import ast
import pathlib

import pytest

pytestmark = pytest.mark.live_db

_LIVE_DB_DIR = pathlib.Path(__file__).parent
_THIS_FILE = pathlib.Path(__file__).name
_EXCLUDED = {"conftest.py", _THIS_FILE, "__init__.py"}


def _test_modules() -> list[pathlib.Path]:
    return [p for p in sorted(_LIVE_DB_DIR.glob("*.py")) if p.name not in _EXCLUDED]


def _has_live_db_marker(node: ast.FunctionDef) -> bool:
    for dec in node.decorator_list:
        # @pytest.mark.live_db  (Attribute) or @pytest.mark.live_db(...) (Call)
        target = dec.func if isinstance(dec, ast.Call) else dec
        if (
            isinstance(target, ast.Attribute)
            and target.attr == "live_db"
            and isinstance(target.value, ast.Attribute)
            and target.value.attr == "mark"
        ):
            return True
    return False


def _module_has_pytestmark_live_db(tree: ast.Module) -> bool:
    """True if the module sets ``pytestmark = pytest.mark.live_db`` at module scope."""
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "pytestmark":
                    src = ast.unparse(node.value)
                    if "live_db" in src:
                        return True
    return False


def test_every_live_db_test_is_marked():
    """T033: every test function in tests/live_db/ is marked live_db."""
    offenders: list[str] = []
    for path in _test_modules():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        module_marked = _module_has_pytestmark_live_db(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                if not (module_marked or _has_live_db_marker(node)):
                    offenders.append(f"{path.name}::{node.name}")
    assert not offenders, f"unmarked live_db tests: {offenders}"


def test_no_silent_exception_swallow_around_docker_calls():
    """T034: no bare ``except ...: pass`` anywhere in the live-DB suite source.

    A swallowed exception around a Docker/psycopg2 call is the forbidden shape that
    could hide a live pass. This scans all suite source (incl. conftest) for an
    ``except`` handler whose body is a lone ``pass``.
    """
    offenders: list[str] = []
    scan = [*_test_modules(), _LIVE_DB_DIR / "conftest.py"]
    for path in scan:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    offenders.append(f"{path.name}:{node.lineno}")
    assert not offenders, f"silent except-pass swallow(s): {offenders}"
