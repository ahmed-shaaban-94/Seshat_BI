"""Parity parsing and normalized, approval-neutral dbt run evidence."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from secrets import token_hex
from typing import Any

from seshat.dbt._evidence_schema import validate_evidence_payload
from seshat.dbt.artifacts import ArtifactIntegrityError, cross_check_execution
from seshat.dbt.contracts import (
    ArtifactSet,
    Blocker,
    ExecutionPlan,
    InvocationResult,
    Operation,
    ParityAssertion,
    RunEvidence,
    RunResultsSummary,
    TestSummary,
)
from seshat.dbt.planning import plan_digest
from seshat.dbt.redaction import (
    EnvironmentConfigError,
    load_child_environment,
    sanitize,
    secret_values,
)

_ASSERTION_CONTRACTS = {
    "fact_row_count": ("fact_row_count", "fct_sales_rss", Decimal("0")),
    "fact_distinct_transaction_id": (
        "business_key_count",
        "fct_sales_rss.transaction_id",
        Decimal("0"),
    ),
    "fact_total_spent_sum": (
        "additive_money_total",
        "fct_sales_rss.total_spent",
        Decimal("0.01"),
    ),
    "dim_customer_member_count": (
        "dimension_member_count",
        "dim_customer_rss",
        Decimal("0"),
    ),
    "dim_product_member_count": (
        "dimension_member_count",
        "dim_product_rss",
        Decimal("0"),
    ),
    "dim_payment_method_member_count": (
        "dimension_member_count",
        "dim_payment_method_rss",
        Decimal("0"),
    ),
    "dim_location_member_count": (
        "dimension_member_count",
        "dim_location_rss",
        Decimal("0"),
    ),
    "dim_date_member_count": (
        "dimension_member_count",
        "dim_date_rss",
        Decimal("0"),
    ),
}
REQUIRED_RETAIL_STORE_SALES_ASSERTIONS = frozenset(_ASSERTION_CONTRACTS)
_INVOCATION_ID = re.compile(r"^[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}$")
_TABLE_ID = re.compile(r"^[a-z][a-z0-9_]*$")
_TEST_STATUS_BUCKETS = {
    "pass": "passed",
    "success": "passed",
    "fail": "failed",
    "warn": "failed",
    "error": "errored",
    "skipped": "skipped",
}
_PRIMARY_RESULT_OPERATIONS = frozenset({Operation.BUILD.value, Operation.TEST.value})
_REPORTED_DECIMAL_ERRORS = {
    "delta": "reported delta does not match values for {assertion_id}",
    "tolerance": "reported tolerance is not governed for {assertion_id}",
}


def _is_parity_result(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(row, dict) and "assertion_id" in row for row in value)
    )


def _candidate_entry(key: str, value: Any) -> list[list[dict[str, Any]]]:
    if key == "rows" and _is_parity_result(value):
        return [value]
    return _candidate_rows(value)


def _mapping_candidate_rows(value: dict[str, Any]) -> list[list[dict[str, Any]]]:
    candidates: list[list[dict[str, Any]]] = []
    for key, nested in value.items():
        candidates.extend(_candidate_entry(key, nested))
    return candidates


def _sequence_candidate_rows(value: list[Any]) -> list[list[dict[str, Any]]]:
    candidates: list[list[dict[str, Any]]] = []
    for nested in value:
        candidates.extend(_candidate_rows(nested))
    return candidates


def _candidate_rows(value: Any) -> list[list[dict[str, Any]]]:
    if isinstance(value, dict):
        return _mapping_candidate_rows(value)
    if isinstance(value, list):
        return _sequence_candidate_rows(value)
    return []


def _decimal(value: Any, label: str) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise ArtifactIntegrityError(f"parity {label} is not numeric")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ArtifactIntegrityError(f"parity {label} is not numeric") from exc
    if not number.is_finite():
        raise ArtifactIntegrityError(f"parity {label} must be finite")
    return number


def _decimal_string(value: Decimal) -> str:
    if value == 0:
        return "0"
    text = format(value.normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _parity_contract(raw: dict[str, Any]) -> tuple[str, str, str, Decimal]:
    assertion_id = raw.get("assertion_id")
    if not isinstance(assertion_id, str) or assertion_id not in _ASSERTION_CONTRACTS:
        raise ArtifactIntegrityError(f"unknown parity assertion {assertion_id!r}")
    expected_class, expected_subject, tolerance = _ASSERTION_CONTRACTS[assertion_id]
    return assertion_id, expected_class, expected_subject, tolerance


def _validate_parity_identity(
    raw: dict[str, Any], assertion_id: str, expected_class: str, expected_subject: str
) -> None:
    expected_fields = (
        (
            "assertion_class",
            expected_class,
            f"parity assertion class is invalid for {assertion_id}",
        ),
        ("subject", expected_subject, f"parity subject is invalid for {assertion_id}"),
    )
    for field, expected, message in expected_fields:
        if raw.get(field) != expected:
            raise ArtifactIntegrityError(message)


def _validate_reported_decimal(
    raw: dict[str, Any], assertion_id: str, field: str, governed: Decimal
) -> None:
    reported = _decimal(raw.get(field), f"{field} for {assertion_id}")
    if reported != governed:
        raise ArtifactIntegrityError(
            _REPORTED_DECIMAL_ERRORS[field].format(assertion_id=assertion_id)
        )


def _parity_values(
    raw: dict[str, Any], assertion_id: str, tolerance: Decimal
) -> tuple[Decimal, Decimal, Decimal]:
    expected = _decimal(raw.get("expected"), f"expected for {assertion_id}")
    actual = _decimal(raw.get("actual"), f"actual for {assertion_id}")
    delta = abs(actual - expected)
    _validate_reported_decimal(
        raw,
        assertion_id,
        "delta",
        delta,
    )
    _validate_reported_decimal(
        raw,
        assertion_id,
        "tolerance",
        tolerance,
    )
    return expected, actual, delta


def _validate_reported_pass(
    raw: dict[str, Any], assertion_id: str, passed: bool
) -> None:
    if not isinstance(raw.get("passed"), bool) or raw["passed"] is not passed:
        raise ArtifactIntegrityError(
            f"reported passed boolean is incorrect for {assertion_id}"
        )


def _parity_row(raw: dict[str, Any]) -> ParityAssertion:
    assertion_id, expected_class, expected_subject, tolerance = _parity_contract(raw)
    _validate_parity_identity(raw, assertion_id, expected_class, expected_subject)
    expected, actual, delta = _parity_values(raw, assertion_id, tolerance)
    passed = delta <= tolerance
    _validate_reported_pass(raw, assertion_id, passed)
    return ParityAssertion(
        assertion_id=assertion_id,
        assertion_class=expected_class,
        subject=expected_subject,
        expected=_decimal_string(expected),
        actual=_decimal_string(actual),
        delta=_decimal_string(delta),
        tolerance=_decimal_string(tolerance),
        passed=passed,
    )


def _parse_show_line(line: str, number: int) -> Any | None:
    if not line.strip():
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError as exc:
        raise ArtifactIntegrityError(
            f"dbt show line {number} is not valid JSON"
        ) from exc


def _structured_parity_result(event: Any) -> list[dict[str, Any]] | None:
    candidates = _candidate_rows(event)
    if len(candidates) > 1:
        raise ArtifactIntegrityError(
            "dbt show event contains multiple structured parity results"
        )
    return candidates[0] if candidates else None


def _show_result_events(show_stdout: str) -> list[list[dict[str, Any]]]:
    result_events: list[list[dict[str, Any]]] = []
    for number, line in enumerate(show_stdout.splitlines(), start=1):
        event = _parse_show_line(line, number)
        if event is None:
            continue
        result = _structured_parity_result(event)
        if result is not None:
            result_events.append(result)
    return result_events


def _only_parity_result(
    result_events: list[list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    if len(result_events) != 1:
        raise ArtifactIntegrityError(
            "dbt show must contain exactly one structured parity result event"
        )
    return result_events[0]


def _normalized_parity_rows(
    raw_rows: list[dict[str, Any]],
) -> tuple[ParityAssertion, ...]:
    rows = tuple(_parity_row(row) for row in raw_rows)
    ids = tuple(row.assertion_id for row in rows)
    if len(ids) != len(set(ids)):
        raise ArtifactIntegrityError("dbt show contains duplicate parity assertion IDs")
    order = {name: index for index, name in enumerate(_ASSERTION_CONTRACTS)}
    return tuple(sorted(rows, key=lambda row: order[row.assertion_id]))


def parse_parity_rows(show_stdout: str) -> tuple[ParityAssertion, ...]:
    """Extract exactly one structured dbt show result and normalize its rows."""

    raw_rows = _only_parity_result(_show_result_events(show_stdout))
    return _normalized_parity_rows(raw_rows)


def _unique_test_results(artifacts: ArtifactSet) -> Iterator[Any]:
    seen: set[str] = set()
    for summary in artifacts.run_results:
        for result in summary.results:
            if not result.unique_id.startswith("test.") or result.unique_id in seen:
                continue
            seen.add(result.unique_id)
            yield result


def _test_summary(artifacts: ArtifactSet) -> TestSummary:
    counts = {"passed": 0, "failed": 0, "errored": 0, "skipped": 0}
    for result in _unique_test_results(artifacts):
        bucket = _TEST_STATUS_BUCKETS.get(result.status)
        if bucket is not None:
            counts[bucket] += 1
    return TestSummary(**counts)


def _artifact_hashes(artifacts: ArtifactSet) -> dict[str, str]:
    hashes = {"manifest.json": artifacts.manifest.sha256}
    for summary in artifacts.run_results:
        key = (
            "parity_run_results.json" if summary.which == "show" else "run_results.json"
        )
        if key in hashes and hashes[key] != summary.sha256:
            raise ArtifactIntegrityError(f"multiple conflicting {key} artifacts")
        hashes[key] = summary.sha256
    return hashes


def _elapsed(started_at: str, completed_at: str) -> float:
    try:
        start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        completed = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ArtifactIntegrityError("invocation timestamps are invalid") from exc
    elapsed = (completed - start).total_seconds()
    if elapsed < 0:
        raise ArtifactIntegrityError("invocation completed before it started")
    return elapsed


def _validate_artifacts(plan: ExecutionPlan, artifacts: ArtifactSet) -> None:
    if (
        artifacts.manifest.schema_uri != plan.manifest.schema_uri
        or artifacts.manifest.semantic_sha256 != plan.manifest.semantic_sha256
    ):
        raise ArtifactIntegrityError("manifest does not match the accepted plan")
    for results in artifacts.run_results:
        cross_check_execution(plan, results)


def _results_for_operations(
    artifacts: ArtifactSet, operations: frozenset[str]
) -> tuple[RunResultsSummary, ...]:
    return tuple(
        result for result in artifacts.run_results if result.which in operations
    )


def _single_result(
    results: tuple[RunResultsSummary, ...], label: str
) -> RunResultsSummary:
    if len(results) != 1:
        raise ArtifactIntegrityError(
            f"dbt evidence requires exactly one {label} run-results artifact"
        )
    return results[0]


def _validate_artifact_roles(
    invocation: InvocationResult, artifacts: ArtifactSet
) -> None:
    primary = _single_result(
        _results_for_operations(artifacts, _PRIMARY_RESULT_OPERATIONS), "primary"
    )
    _single_result(_results_for_operations(artifacts, frozenset({"show"})), "show")
    if primary.which != invocation.operation.value:
        raise ArtifactIntegrityError(
            "primary run-results operation does not match invocation operation"
        )
    if len(artifacts.run_results) != 2:
        raise ArtifactIntegrityError("dbt evidence contains unexpected run-results")


def _validate_parity_set(parity: tuple[ParityAssertion, ...]) -> None:
    parity_ids = {row.assertion_id for row in parity}
    missing = REQUIRED_RETAIL_STORE_SALES_ASSERTIONS - parity_ids
    extras = parity_ids - REQUIRED_RETAIL_STORE_SALES_ASSERTIONS
    if missing:
        raise ArtifactIntegrityError(
            "missing parity assertions: " + ", ".join(sorted(missing))
        )
    if extras or len(parity) != len(REQUIRED_RETAIL_STORE_SALES_ASSERTIONS):
        raise ArtifactIntegrityError("parity assertions are not the exact governed set")


def _execution_blocker(invocation: InvocationResult) -> Blocker | None:
    if invocation.return_code == 0:
        return None
    return Blocker("DBT_EXECUTION_FAILED", "dbt execution completed with failures")


def _test_blocker(tests: TestSummary) -> Blocker | None:
    if not tests.failed and not tests.errored:
        return None
    return Blocker("DBT_TESTS_FAILED", "one or more governed dbt tests failed")


def _parity_blockers(parity: tuple[ParityAssertion, ...]) -> tuple[Blocker, ...]:
    return tuple(
        Blocker(
            "DBT_PARITY_MISMATCH",
            f"{row.assertion_id} delta {row.delta} exceeds tolerance {row.tolerance}",
            assertion_id=row.assertion_id,
        )
        for row in parity
        if not row.passed
    )


def _first_blocker(*blockers: Blocker | None) -> Blocker | None:
    return next((blocker for blocker in blockers if blocker is not None), None)


def _evidence_outcome(
    invocation: InvocationResult,
    tests: TestSummary,
    parity: tuple[ParityAssertion, ...],
) -> tuple[str, int, tuple[Blocker, ...]]:
    fatal = _first_blocker(_execution_blocker(invocation), _test_blocker(tests))
    if fatal is not None:
        return "failed", 1, (fatal,)
    blockers = _parity_blockers(parity)
    if blockers:
        return "blocked", 1, blockers
    return "pass", 0, ()


def _executed_unique_ids(artifacts: ArtifactSet) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                result.unique_id
                for summary in artifacts.run_results
                for result in summary.results
            }
        )
    )


def build_evidence(
    plan: ExecutionPlan,
    invocation: InvocationResult,
    artifacts: ArtifactSet,
    parity: tuple[ParityAssertion, ...],
) -> RunEvidence:
    """Build complete derived evidence without carrying raw process output."""

    if invocation.operation not in {Operation.BUILD, Operation.TEST}:
        raise ArtifactIntegrityError("only build/test invocations produce run evidence")
    _validate_artifact_roles(invocation, artifacts)
    _validate_artifacts(plan, artifacts)
    _validate_parity_set(parity)
    tests = _test_summary(artifacts)
    outcome, exit_code, blockers = _evidence_outcome(invocation, tests, parity)
    return RunEvidence(
        schema_version=1,
        authority="derived-evidence-only",
        invocation_id=invocation.invocation_id,
        table_id=plan.table_id,
        command=invocation.operation.value,
        outcome=outcome,
        seshat_exit_code=exit_code,
        started_at=invocation.started_at,
        completed_at=invocation.completed_at,
        elapsed_seconds=_elapsed(invocation.started_at, invocation.completed_at),
        plan_digest=plan_digest(plan),
        project_fingerprint=plan.project.sha256,
        mapping_path=plan.mapping.path,
        mapping_revision=plan.mapping.git_blob,
        runtime={
            "dbt_core": plan.runtime.dbt_core,
            "dbt_adapter": plan.runtime.dbt_adapter,
            "dbt_adapter_version": plan.runtime.dbt_adapter_version,
        },
        target={"name": plan.runtime.target, "schemas": asdict(plan.schemas)},
        selected_unique_ids=plan.selected_unique_ids,
        executed_unique_ids=_executed_unique_ids(artifacts),
        tests=tests,
        parity=parity,
        artifacts=_artifact_hashes(artifacts),
        blocking_reasons=blockers,
        readiness_effect="none; named-human approval required",
    )


def evidence_to_dict(evidence: RunEvidence) -> dict[str, Any]:
    """Convert evidence to its exact closed JSON shape."""

    return {
        "schema_version": evidence.schema_version,
        "authority": evidence.authority,
        "invocation_id": evidence.invocation_id,
        "table_id": evidence.table_id,
        "command": evidence.command,
        "outcome": evidence.outcome,
        "seshat_exit_code": evidence.seshat_exit_code,
        "started_at": evidence.started_at,
        "completed_at": evidence.completed_at,
        "elapsed_seconds": evidence.elapsed_seconds,
        "plan_digest": evidence.plan_digest,
        "project_fingerprint": evidence.project_fingerprint,
        "mapping_path": evidence.mapping_path,
        "mapping_revision": evidence.mapping_revision,
        "runtime": dict(evidence.runtime),
        "target": dict(evidence.target),
        "selected_unique_ids": list(evidence.selected_unique_ids),
        "executed_unique_ids": list(evidence.executed_unique_ids),
        "tests": asdict(evidence.tests),
        "parity": [asdict(row) for row in evidence.parity],
        "artifacts": dict(evidence.artifacts),
        "blocking_reasons": [
            _blocker_to_dict(blocker) for blocker in evidence.blocking_reasons
        ],
        "readiness_effect": evidence.readiness_effect,
    }


def _blocker_to_dict(blocker: Blocker) -> dict[str, Any]:
    row = {"code": blocker.code, "message": blocker.message}
    if blocker.assertion_id is not None:
        row["assertion_id"] = blocker.assertion_id
    return row


def _validate_evidence_identity(evidence: RunEvidence) -> None:
    if not _TABLE_ID.fullmatch(evidence.table_id):
        raise ArtifactIntegrityError("evidence table_id is unsafe")
    if not _INVOCATION_ID.fullmatch(evidence.invocation_id):
        raise ArtifactIntegrityError("evidence invocation_id is unsafe")
    expected_map = f"mappings/{evidence.table_id}/source-map.yaml"
    if evidence.mapping_path != expected_map:
        raise ArtifactIntegrityError("evidence mapping path does not match table_id")


def _require_repository_path(path: Path, root: Path) -> None:
    try:
        path.resolve().relative_to(root)
    except ValueError as exc:
        raise ArtifactIntegrityError("evidence path escapes the repository") from exc


def _mapping_directory(root: Path, evidence: RunEvidence) -> Path:
    mapping_dir = root / "mappings" / evidence.table_id
    if not mapping_dir.is_dir():
        raise ArtifactIntegrityError("evidence mapping directory is missing")
    _require_repository_path(mapping_dir, root)
    return mapping_dir


def _load_evidence_schema(root: Path) -> dict[str, Any]:
    schema_path = root / "schemas" / "dbt-run-evidence.schema.json"
    try:
        return json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ArtifactIntegrityError("evidence JSON Schema is unavailable") from exc


def _sanitized_payload(root: Path, evidence: RunEvidence) -> dict[str, Any]:
    try:
        environment = load_child_environment(root)
    except EnvironmentConfigError as exc:
        raise ArtifactIntegrityError(
            "local environment could not be sanitized"
        ) from exc
    cleaned = sanitize(evidence_to_dict(evidence), secret_values(environment), root)
    if not isinstance(cleaned, dict):
        raise ArtifactIntegrityError("evidence payload could not be sanitized")
    return cleaned


def _evidence_directory(root: Path, mapping_dir: Path) -> Path:
    evidence_dir = mapping_dir / "dbt-evidence"
    if evidence_dir.exists():
        _require_repository_path(evidence_dir, root)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    return evidence_dir


def _serialized_payload(cleaned: dict[str, Any]) -> str:
    return json.dumps(cleaned, sort_keys=True, indent=2, ensure_ascii=True) + "\n"


def _atomic_write(path: Path, payload: str) -> None:
    temporary = path.with_name(f".{path.name}.{token_hex(8)}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
        temporary.replace(path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def write_evidence(repo_root: Path, evidence: RunEvidence) -> Path:
    """Sanitize, schema-check, and atomically write one evidence record."""

    root = Path(repo_root).resolve()
    _validate_evidence_identity(evidence)
    mapping_dir = _mapping_directory(root, evidence)
    schema = _load_evidence_schema(root)
    cleaned = _sanitized_payload(root, evidence)
    validate_evidence_payload(cleaned, schema)
    evidence_dir = _evidence_directory(root, mapping_dir)
    path = evidence_dir / f"{evidence.invocation_id}.json"
    _atomic_write(path, _serialized_payload(cleaned))
    return path
