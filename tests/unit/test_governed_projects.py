"""`seshat dbt init` / `seshat dagster init` self-sufficiency (issue #325).

A bare workspace (no development repository) must gain the full governed
dbt / Dagster capability surface from bundled templates. Only table-neutral
content is materialized (constitution VII), nothing existing is ever
overwritten, and the results satisfy the exact same doctor checks that
previously demanded the dev repo.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_EXAMPLE_TOKENS = ("retail_store_sales", "c086", "pharmacy")


def test_dbt_init_materializes_the_doctor_required_paths(tmp_path: Path) -> None:
    from seshat.cli.commands.dbt import _verify_ignore_rules, _verify_required_paths
    from seshat.governed_projects import dbt_init

    report = dbt_init(tmp_path)

    _verify_required_paths(tmp_path)  # no raise: doctor's exact path set
    _verify_ignore_rules(tmp_path)  # no raise: doctor's exact ignore rules
    assert "dbt/dbt_project.yml" in report.written
    assert "dbt/selectors.yml" in report.written
    assert any("profiles.example.yml" in note for note in report.notes)


def test_dbt_init_never_overwrites_and_is_idempotent(tmp_path: Path) -> None:
    from seshat.governed_projects import dbt_init

    dbt_init(tmp_path)
    marker = tmp_path / "dbt" / "selectors.yml"
    marker.write_text("selectors: [] # hand-edited\n", encoding="utf-8")

    second = dbt_init(tmp_path)

    assert second.written == ()
    assert "dbt/selectors.yml" in second.kept
    assert marker.read_text(encoding="utf-8") == "selectors: [] # hand-edited\n"


def test_dbt_init_appends_only_missing_ignore_rules(tmp_path: Path) -> None:
    from seshat.governed_projects import dbt_init

    (tmp_path / ".gitignore").write_text("/profiles.yml\nuser-line\n", encoding="utf-8")

    dbt_init(tmp_path)

    lines = (tmp_path / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "user-line" in lines
    assert lines.count("/profiles.yml") == 1
    for required in ("/.user.yml", "/dbt/target/", "/dbt/logs/", "/.seshat/dbt/"):
        assert required in lines


def test_dagster_init_clears_the_project_absent_blocker(tmp_path: Path) -> None:
    from seshat.dagster_adapter import doctor
    from seshat.governed_projects import dagster_init

    report = dagster_init(tmp_path)

    findings = {finding.id for finding in doctor.run_doctor(tmp_path)}
    assert "orchestration/dagster/pyproject.toml" in report.written
    assert any(path.startswith("orchestration/dagster/src/") for path in report.written)
    assert "DAG-PROJ-01" not in findings
    assert "DAG-PAIR-01" not in findings
    # The venv is inherently user-created; init points at the remedy instead.
    assert "DAG-VENV-01" in findings
    assert any("uv venv" in note for note in report.notes)


def test_dagster_init_never_overwrites(tmp_path: Path) -> None:
    from seshat.governed_projects import dagster_init

    dagster_init(tmp_path)
    marker = tmp_path / "orchestration" / "dagster" / "pyproject.toml"
    marker.write_text("# hand-edited\n", encoding="utf-8")

    second = dagster_init(tmp_path)

    assert second.written == ()
    assert marker.read_text(encoding="utf-8") == "# hand-edited\n"


def test_bundled_templates_carry_no_worked_table_answers(tmp_path: Path) -> None:
    """Constitution VII: everything either init materializes is table-neutral
    -- no worked-example table name may reach a fresh workspace."""
    from seshat.governed_projects import dagster_init, dbt_init

    dbt_init(tmp_path)
    dagster_init(tmp_path)

    for path in tmp_path.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_bytes().decode("utf-8", errors="ignore").lower()
        for token in _EXAMPLE_TOKENS:
            assert token not in text, (path, token)


def test_cli_init_verbs_run_end_to_end(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from seshat.cli import main

    dbt_exit = main(["dbt", "init", "--repo", str(tmp_path)])
    dagster_exit = main(["dagster", "init", "--repo", str(tmp_path)])

    out = capsys.readouterr().out
    assert dbt_exit == 0
    assert dagster_exit == 0
    assert "materialized" in out
    assert (tmp_path / "dbt" / "dbt_project.yml").is_file()
    assert (tmp_path / "orchestration" / "dagster" / "pyproject.toml").is_file()
