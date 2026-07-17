"""Contract tests for the optional governed dbt runtime package surface."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]


def test_dbt_extra_is_an_exact_tested_pair() -> None:
    payload = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert payload["project"]["optional-dependencies"]["dbt"] == [
        "dbt-core==1.12.0",
        "dbt-postgres==1.11.0",
    ]


def test_dbt_local_outputs_are_ignored() -> None:
    lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    for line in (
        "/profiles.yml",
        "/.user.yml",
        "/dbt/target/",
        "/dbt/logs/",
        "/.seshat/dbt/",
    ):
        assert line in lines


def test_example_profile_uses_environment_references_only() -> None:
    text = (ROOT / "profiles.example.yml").read_text(encoding="utf-8")

    for key in (
        "SESHAT_DBT_HOST",
        "SESHAT_DBT_PORT",
        "SESHAT_DBT_USER",
        "SESHAT_DBT_PASSWORD",
        "SESHAT_DBT_DBNAME",
        "SESHAT_DBT_SCHEMA",
        "SESHAT_DBT_SSLMODE",
    ):
        assert f"env_var('{key}'" in text
    assert "<your-postgres-host>" not in text
    assert "<your-db-user>" not in text
    assert "<your-database-name>" not in text


def test_local_profile_is_actually_ignored_by_git() -> None:
    import subprocess

    result = subprocess.run(
        ["git", "check-ignore", "--quiet", "profiles.yml"],
        cwd=ROOT,
        check=False,
        shell=False,
    )

    assert result.returncode == 0
