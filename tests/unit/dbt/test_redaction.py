from __future__ import annotations

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def test_load_child_environment_allows_only_runtime_and_governed_dbt_keys(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from seshat.dbt.redaction import load_child_environment

    monkeypatch.setenv("PATH", "safe-path")
    monkeypatch.setenv("UNRELATED_API_TOKEN", "must-not-reach-dbt")
    monkeypatch.setenv("SESHAT_DBT_HOST", "parent-host")
    before = dict(os.environ)
    (tmp_path / ".env").write_text(
        "# local dbt connection\n"
        "SESHAT_DBT_HOST=private-host\n"
        "SESHAT_DBT_PASSWORD='private-pass'\n"
        "UNRELATED_DOTENV_TOKEN=must-not-reach-dbt\n",
        encoding="utf-8",
    )

    child = load_child_environment(tmp_path)

    assert child["PATH"] == "safe-path"
    assert child["SESHAT_DBT_HOST"] == "private-host"
    assert child["SESHAT_DBT_PASSWORD"] == "private-pass"
    assert "UNRELATED_API_TOKEN" not in child
    assert "UNRELATED_DOTENV_TOKEN" not in child
    assert dict(os.environ) == before


@pytest.mark.parametrize(
    "content",
    (
        "NOT AN ASSIGNMENT\n",
        "1INVALID=value\n",
        "DUPLICATE=first\nDUPLICATE=second\n",
        "UNCLOSED='value\n",
    ),
)
def test_load_child_environment_rejects_malformed_or_duplicate_lines(
    tmp_path: Path, content: str
) -> None:
    from seshat.dbt.redaction import EnvironmentConfigError, load_child_environment

    (tmp_path / ".env").write_text(content, encoding="utf-8")

    with pytest.raises(EnvironmentConfigError, match=r"\.env"):
        load_child_environment(tmp_path)


def test_component_redaction_removes_reformatted_uri_credentials(
    tmp_path: Path,
) -> None:
    from seshat.dbt.redaction import sanitize

    dsn = "postgresql://private-user:private%2Fpass@private-host:5432/private-db"
    text = (
        'connection to server at "private-host" failed for user "private-user" '
        "password private/pass database private-db"
    )

    clean = sanitize(text, (dsn,), tmp_path)

    assert isinstance(clean, str)
    for component in ("private-host", "private-user", "private/pass", "private-db"):
        assert component not in clean


def test_sanitize_recurses_and_replaces_repo_and_home_paths(tmp_path: Path) -> None:
    from seshat.dbt.redaction import sanitize

    repo_path = str(tmp_path / "dbt" / "target" / "manifest.json")
    home_path = str(Path.home() / ".dbt" / "profiles.yml")
    value = {
        "message": f"secret-long at {repo_path}",
        "nested": (f"home={home_path}", ["secret", 7]),
    }

    clean = sanitize(value, ("secret", "secret-long", ""), tmp_path)

    assert isinstance(clean, dict)
    assert clean["message"] == "<redacted> at <repo>/dbt/target/manifest.json"
    assert isinstance(clean["nested"], tuple)
    assert clean["nested"][0] == "home=<home>/.dbt/profiles.yml"
    assert clean["nested"][1] == ["<redacted>", 7]


def test_sanitize_redacts_mapping_keys_as_well_as_values(tmp_path: Path) -> None:
    from seshat.dbt.redaction import sanitize

    clean = sanitize({"private-user": "ok"}, ("private-user",), tmp_path)

    assert clean == {"<redacted>": "ok"}
