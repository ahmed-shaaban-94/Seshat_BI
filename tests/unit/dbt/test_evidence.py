from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "dbt_artifacts"


@dataclass(frozen=True)
class ArtifactRoleCase:
    primary_count: int
    show_count: int
    primary_operation: str
    expected_error: str


def _sample_plan():
    from seshat.dbt.artifacts import load_manifest
    from seshat.dbt.contracts import (
        ExecutionPlan,
        ManifestBinding,
        MappingBinding,
        ProjectBinding,
        RuntimeBinding,
        ShadowSchemas,
    )

    return ExecutionPlan(
        schema_version=1,
        table_id="retail_store_sales",
        mapping=MappingBinding(
            path="mappings/retail_store_sales/source-map.yaml",
            git_blob="b" * 40,
            sha256="c" * 64,
            readiness_sha256="d" * 64,
            unresolved_questions_sha256="e" * 64,
            approval_id="approval-1",
        ),
        project=ProjectBinding(path="dbt", sha256="f" * 64),
        runtime=RuntimeBinding(
            dbt_core="1.12.0",
            dbt_adapter="dbt-postgres",
            dbt_adapter_version="1.10.2",
            profile="seshat_bi_warehouse",
            target="shadow",
            selector="seshat_table_retail_store_sales",
        ),
        schemas=ShadowSchemas(
            silver="seshat_dbt_shadow_silver",
            gold="seshat_dbt_shadow_gold",
            audit="seshat_dbt_shadow_audit",
        ),
        manifest=ManifestBinding(
            schema_uri="https://schemas.getdbt.com/dbt/manifest/v12.json",
            semantic_sha256=load_manifest(
                FIXTURES / "manifest-v12.json"
            ).semantic_sha256,
        ),
        selected_unique_ids=(
            "model.seshat_bi.fact_retail_store_sales",
            "model.seshat_bi.stg_retail_store_sales",
            "test.seshat_bi.not_null_fact_transaction_id.abc123",
        ),
    )


def _invocation(return_code: int = 0):
    from seshat.dbt.contracts import InvocationResult, Operation

    return InvocationResult(
        invocation_id="20260716T120000Z-a1b2c3d4",
        operation=Operation.BUILD,
        argv_summary=("build", "--select", "selector:seshat_table_retail_store_sales"),
        return_code=return_code,
        started_at="2026-07-16T12:00:00Z",
        completed_at="2026-07-16T12:01:00Z",
        stdout="",
        stderr="private-host private-pass",
        target_dir=Path("ignored-target"),
        log_dir=Path("ignored-logs"),
    )


def _artifacts():
    from seshat.dbt.artifacts import load_manifest, load_run_results
    from seshat.dbt.contracts import ArtifactSet

    primary = load_run_results(FIXTURES / "run-results-v6.json")
    parity = replace(primary, which="show", sha256="a" * 64, results=())
    return ArtifactSet(
        manifest=load_manifest(FIXTURES / "manifest-v12.json"),
        run_results=(primary, parity),
    )


def _stdout(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_complete_parity_passes_and_money_delta_at_tolerance_passes() -> None:
    from seshat.dbt.evidence import (
        REQUIRED_RETAIL_STORE_SALES_ASSERTIONS,
        parse_parity_rows,
    )

    rows = parse_parity_rows(_stdout("show-parity-pass.jsonl"))

    assert {row.assertion_id for row in rows} == (
        REQUIRED_RETAIL_STORE_SALES_ASSERTIONS
    )
    assert all(row.passed for row in rows)
    money = next(row for row in rows if row.assertion_id == "fact_total_spent_sum")
    assert money.delta == "0.01"
    assert money.tolerance == "0.01"


def test_money_delta_above_tolerance_fails_with_concrete_blocker() -> None:
    from seshat.dbt.evidence import build_evidence, parse_parity_rows

    rows = parse_parity_rows(_stdout("show-parity-fail.jsonl"))
    evidence = build_evidence(_sample_plan(), _invocation(), _artifacts(), rows)

    money = next(row for row in rows if row.assertion_id == "fact_total_spent_sum")
    assert money.delta == "0.0101"
    assert money.passed is False
    assert evidence.outcome == "blocked"
    assert evidence.seshat_exit_code == 1
    assert evidence.blocking_reasons[0].assertion_id == "fact_total_spent_sum"
    assert "0.0101" in evidence.blocking_reasons[0].message


def test_missing_parity_row_blocks_even_with_green_tests() -> None:
    from seshat.dbt.artifacts import ArtifactIntegrityError
    from seshat.dbt.evidence import build_evidence, parse_parity_rows

    rows = parse_parity_rows(_stdout("show-parity-missing.jsonl"))

    with pytest.raises(ArtifactIntegrityError, match="missing parity assertions"):
        build_evidence(_sample_plan(), _invocation(), _artifacts(), rows)


@pytest.mark.parametrize(
    "case",
    (
        ArtifactRoleCase(0, 1, "build", "exactly one primary"),
        ArtifactRoleCase(2, 1, "build", "exactly one primary"),
        ArtifactRoleCase(1, 0, "build", "exactly one show"),
        ArtifactRoleCase(1, 2, "build", "exactly one show"),
        ArtifactRoleCase(1, 1, "test", "does not match invocation"),
    ),
)
def test_build_evidence_enforces_artifact_roles(case: ArtifactRoleCase) -> None:
    from seshat.dbt.artifacts import ArtifactIntegrityError
    from seshat.dbt.evidence import build_evidence, parse_parity_rows

    artifacts = _artifacts()
    primary, show = artifacts.run_results
    changed = replace(
        artifacts,
        run_results=(replace(primary, which=case.primary_operation),)
        * case.primary_count
        + (show,) * case.show_count,
    )

    with pytest.raises(ArtifactIntegrityError, match=case.expected_error):
        build_evidence(
            _sample_plan(),
            _invocation(),
            changed,
            parse_parity_rows(_stdout("show-parity-pass.jsonl")),
        )


def test_duplicate_parity_ids_are_rejected() -> None:
    from seshat.dbt.artifacts import ArtifactIntegrityError
    from seshat.dbt.evidence import parse_parity_rows

    stdout = _stdout("show-parity-pass.jsonl")
    events = [json.loads(line) for line in stdout.splitlines()]
    rows = events[-1]["data"]["preview"]["rows"]
    rows.append(rows[0])
    changed = "\n".join(json.dumps(event) for event in events)

    with pytest.raises(ArtifactIntegrityError, match="duplicate parity"):
        parse_parity_rows(changed)


def test_incorrect_reported_passed_boolean_is_rejected() -> None:
    from seshat.dbt.artifacts import ArtifactIntegrityError
    from seshat.dbt.evidence import parse_parity_rows

    event = json.loads(_stdout("show-parity-fail.jsonl"))
    event["data"]["preview"]["rows"][2]["passed"] = True

    with pytest.raises(ArtifactIntegrityError, match="reported passed"):
        parse_parity_rows(json.dumps(event))


@pytest.mark.parametrize("count", (0, 2))
def test_show_requires_exactly_one_structured_result_event(count: int) -> None:
    from seshat.dbt.artifacts import ArtifactIntegrityError
    from seshat.dbt.evidence import parse_parity_rows

    event = _stdout("show-parity-pass.jsonl").splitlines()[-1]
    stdout = "\n".join([event] * count)

    with pytest.raises(ArtifactIntegrityError, match="exactly one"):
        parse_parity_rows(stdout)


def test_evidence_never_changes_readiness_authority() -> None:
    from seshat.dbt.evidence import (
        build_evidence,
        evidence_to_dict,
        parse_parity_rows,
    )

    evidence = build_evidence(
        _sample_plan(),
        _invocation(),
        _artifacts(),
        parse_parity_rows(_stdout("show-parity-pass.jsonl")),
    )
    payload = evidence_to_dict(evidence)

    assert payload["authority"] == "derived-evidence-only"
    assert payload["readiness_effect"] == "none; named-human approval required"
    assert "readiness_status" not in payload
    assert payload["outcome"] == "pass"
    assert payload["tests"] == {
        "passed": 1,
        "failed": 0,
        "errored": 0,
        "skipped": 0,
    }


def test_failed_invocation_emits_failed_outcome_without_raw_error() -> None:
    from seshat.dbt.evidence import build_evidence, evidence_to_dict, parse_parity_rows

    evidence = build_evidence(
        _sample_plan(),
        _invocation(return_code=1),
        _artifacts(),
        parse_parity_rows(_stdout("show-parity-pass.jsonl")),
    )
    payload = evidence_to_dict(evidence)

    assert payload["outcome"] == "failed"
    assert payload["seshat_exit_code"] == 1
    assert "private-host" not in json.dumps(payload)
    assert payload["blocking_reasons"][0]["code"] == "DBT_EXECUTION_FAILED"


def test_write_evidence_is_atomic_schema_valid_stable_and_readiness_safe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import seshat.dbt.evidence as module

    mapping_dir = tmp_path / "mappings" / "retail_store_sales"
    mapping_dir.mkdir(parents=True)
    readiness = mapping_dir / "readiness-status.yaml"
    readiness.write_text("stages: unchanged\n", encoding="utf-8")
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    runtime_schema = (
        Path(__file__).resolve().parents[3] / "schemas" / "dbt-run-evidence.schema.json"
    )
    schema_dir.joinpath("dbt-run-evidence.schema.json").write_bytes(
        runtime_schema.read_bytes()
    )
    monkeypatch.setattr(
        module,
        "load_child_environment",
        lambda root: {
            "SESHAT_DBT_HOST": "private-host",
            "SESHAT_DBT_PASSWORD": "private-pass",
        },
    )
    evidence = module.build_evidence(
        _sample_plan(),
        _invocation(),
        _artifacts(),
        module.parse_parity_rows(_stdout("show-parity-pass.jsonl")),
    )
    before = readiness.read_bytes()

    path = module.write_evidence(tmp_path, evidence)
    first = path.read_bytes()
    second_path = module.write_evidence(tmp_path, evidence)

    assert path == (mapping_dir / "dbt-evidence" / "20260716T120000Z-a1b2c3d4.json")
    assert second_path == path
    assert second_path.read_bytes() == first
    assert readiness.read_bytes() == before
    assert b"private-host" not in first and b"private-pass" not in first
    assert str(tmp_path).encode() not in first
    assert list(json.loads(first)) == sorted(json.loads(first))
    assert not list(path.parent.glob("*.tmp"))


def test_evidence_schema_rejects_additional_fields() -> None:
    from seshat.dbt.artifacts import ArtifactIntegrityError
    from seshat.dbt.evidence import (
        build_evidence,
        evidence_to_dict,
        parse_parity_rows,
        validate_evidence_payload,
    )

    evidence = build_evidence(
        _sample_plan(),
        _invocation(),
        _artifacts(),
        parse_parity_rows(_stdout("show-parity-pass.jsonl")),
    )
    payload = evidence_to_dict(evidence)
    payload["readiness_status"] = "pass"
    runtime_schema = (
        Path(__file__).resolve().parents[3] / "schemas" / "dbt-run-evidence.schema.json"
    )
    schema = json.loads(runtime_schema.read_text(encoding="utf-8"))

    with pytest.raises(ArtifactIntegrityError, match="additional property"):
        validate_evidence_payload(payload, schema)


def test_write_evidence_rejects_table_path_escape(tmp_path: Path) -> None:
    from seshat.dbt.artifacts import ArtifactIntegrityError
    from seshat.dbt.evidence import build_evidence, parse_parity_rows, write_evidence

    evidence = build_evidence(
        _sample_plan(),
        _invocation(),
        _artifacts(),
        parse_parity_rows(_stdout("show-parity-pass.jsonl")),
    )
    evidence = replace(evidence, table_id="../outside")

    with pytest.raises(ArtifactIntegrityError, match="evidence table_id"):
        write_evidence(tmp_path, evidence)
