"""Report Intent metric-reference resolution (spec 123, US1/FR-003/FR-004).

A committed Report Intent's ``outcome_metrics`` / ``driver_metrics`` /
``guardrail_metrics`` entries REFERENCE approved metric contracts by name --
never define them (FR-003). This module is the small, honest reader that
resolves each reference against the real metric-contract store and reports the
result: every metric that resolves to an approved (``readiness.status: pass``)
contract, and every metric that does NOT (a gap that routes upstream to
metric-contract definition, per FR-004) -- it never invents a metric contract
to make a reference resolve.

This is the SAME committed-evidence shape ``gap_detector.py`` already reads
(``mappings/<table>/metrics/*.yaml`` + ``readiness.status``), scoped down to
just the resolve-by-name question a Report Intent needs. The US2 coordinator
(spec 123) reuses this same resolution at design time (FR-007); DL9 (the static
shape rule) deliberately does NOT do this resolution -- it is a runtime state
check, not a presence-only shape check (data-model.md D5).

Read-only: no execution, no DB, no Power BI, no approval grant, no writes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, NamedTuple


def _load_yaml_mapping(path: Path) -> dict[str, Any] | None:
    """Load a YAML mapping; None on any read/parse failure (shipped-surface idiom)."""
    import yaml

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return None
    if not isinstance(data, dict):
        return None
    return data


class MetricReference(NamedTuple):
    """One ``*_metrics[]`` entry as declared in a committed report-intent.yaml."""

    name: str
    store_ref: str


class MetricGap(NamedTuple):
    """A metric reference that does NOT resolve to an approved contract."""

    name: str
    store_ref: str
    reason: str


class ResolutionResult(NamedTuple):
    """The outcome of resolving one intent's metric references."""

    resolved: tuple[str, ...]  # names that resolve to an approved (pass) contract
    gaps: tuple[MetricGap, ...]  # names that do not; never invented


def _norm_refs(entries: object) -> list[MetricReference]:
    if not isinstance(entries, list):
        return []
    out: list[MetricReference] = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        name = str(e.get("name", "")).strip()
        store_ref = str(e.get("store_ref", "")).strip()
        if name:
            out.append(MetricReference(name=name, store_ref=store_ref))
    return out


def metric_references(intent: dict[str, Any]) -> list[MetricReference]:
    """The de-duplicated (by name) metric references across all three roles."""
    refs: dict[str, MetricReference] = {}
    for role in ("outcome_metrics", "driver_metrics", "guardrail_metrics"):
        for ref in _norm_refs(intent.get(role)):
            refs.setdefault(ref.name, ref)
    return list(refs.values())


def _contract_status(repo_root: Path, store_ref: str) -> str | None:
    """The ``readiness.status`` of the contract at ``store_ref``, or None if the
    file is absent/unreadable -- never fabricated."""
    if not store_ref:
        return None
    path = repo_root / store_ref
    if not path.is_file():
        return None
    data = _load_yaml_mapping(path)
    if data is None:
        return None
    readiness = data.get("readiness")
    if not isinstance(readiness, dict):
        return None
    status = readiness.get("status")
    return str(status).strip() if isinstance(status, str) else None


def resolve_metric_references(
    intent: dict[str, Any], repo_root: Path
) -> ResolutionResult:
    """Resolve every metric reference in ``intent`` against the real contract
    store rooted at ``repo_root``.

    A reference resolves only when its ``store_ref`` file exists, parses, and
    declares ``readiness.status: pass`` (FR-003). Everything else -- a missing
    file, an unreadable file, or a non-``pass`` status -- is a GAP: it is
    reported, never invented (FR-004). The caller (the interview / the US2
    coordinator) records the gap and routes it upstream to metric-contract
    definition; this function performs no write and grants no approval.
    """
    resolved: list[str] = []
    gaps: list[MetricGap] = []
    for ref in metric_references(intent):
        status = _contract_status(repo_root, ref.store_ref)
        if status == "pass":
            resolved.append(ref.name)
            continue
        if status is None:
            reason = f"no approved metric contract found at {ref.store_ref!r}"
        else:
            reason = f"metric contract at {ref.store_ref!r} is {status!r}, not 'pass'"
        gaps.append(MetricGap(name=ref.name, store_ref=ref.store_ref, reason=reason))
    return ResolutionResult(resolved=tuple(resolved), gaps=tuple(gaps))
