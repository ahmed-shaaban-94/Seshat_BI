"""Delivery-shape guard (spec 127, FR-005): the showcase feature ships as a
skill over a library function, adding NO new top-level CLI verb (ratified
Option B). Mirrors the B1/B3 lazy-import discipline: importing the package
adds no network/driver dependency."""

from __future__ import annotations

import sys

import pytest

pytestmark = pytest.mark.unit


def test_cli_dispatch_has_no_showcase_verb() -> None:
    from seshat.cli import _DISPATCH

    assert "showcase" not in _DISPATCH


def test_importing_showcase_package_adds_no_network_or_driver_import() -> None:
    for name in list(sys.modules):
        if name == "seshat.showcase" or name.startswith("seshat.showcase."):
            del sys.modules[name]

    before = set(sys.modules)
    import seshat.showcase  # noqa: F401

    after = set(sys.modules) - before
    forbidden_substrings = ("psycopg", "sqlalchemy", "requests", "urllib3", "httpx")
    for module_name in after:
        lowered = module_name.lower()
        assert not any(token in lowered for token in forbidden_substrings), module_name


def test_public_api_exports_build_and_render() -> None:
    from seshat.showcase import build_showcase_bundle, render_showcase_html

    assert callable(build_showcase_bundle)
    assert callable(render_showcase_html)
