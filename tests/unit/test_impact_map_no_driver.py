from __future__ import annotations

import inspect

import pytest

import seshat.impact_map as impact_map

pytestmark = pytest.mark.unit


def test_composer_module_imports_no_database_driver() -> None:
    source = inspect.getsource(impact_map).lower()
    forbidden = ("import psycopg", "import sqlalchemy", ".connect(", "dsn")
    assert not any(token in source for token in forbidden)
