"""Unit tests for the DAX Generator (src/retail/dax_gen.py).

Phase 1: kind:base + kind:ratio, generate -> verify -> refuse. The headline
property is the round-trip: every emitted measure re-verifies as `pass`.
"""

import pytest

from retail.dax_gen import GenResult

pytestmark = pytest.mark.unit


def test_genresult_success_populates_outputs_only():
    r = GenResult.success(dax="SUM(T[c])", tmdl_block="measure X = SUM(T[c])")
    assert r.ok is True
    assert r.dax == "SUM(T[c])"
    assert r.tmdl_block == "measure X = SUM(T[c])"
    assert r.reason is None


def test_genresult_refuse_has_none_outputs():
    r = GenResult.refuse("unsupported kind 'foo'")
    assert r.ok is False
    assert r.dax is None
    assert r.tmdl_block is None
    assert r.reason == "unsupported kind 'foo'"


def test_genresult_rejects_ok_without_dax():
    with pytest.raises(ValueError):
        GenResult(ok=True, dax=None, tmdl_block=None)


def test_genresult_rejects_refusal_with_dax():
    with pytest.raises(ValueError):
        GenResult(ok=False, dax="SUM(T[c])", reason="x")
