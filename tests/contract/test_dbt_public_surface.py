"""Contract for the public dbt skill and thin Claude command wrappers."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SURFACE = ROOT / "distribution" / "public-command-surface.yaml"
ALLOWLIST = ROOT / "distribution" / "public-knowledge-allowlist.yaml"
TEMPLATES = ROOT / "distribution" / "bundle-templates"
COMMANDS = ("dbt-doctor", "dbt-plan", "dbt-build", "dbt-review")


def _yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_public_surface_declares_dbt_skill_and_commands() -> None:
    surface = _yaml(SURFACE)
    commands = {
        item["name"]: item
        for item in surface["commands"]
        if item["status"] == "shipped"
    }

    assert set(COMMANDS) <= set(commands)
    assert commands["dbt-doctor"]["mode"] == "read-only"
    assert commands["dbt-plan"]["gates"] == ["mapping-approval"]
    assert commands["dbt-build"]["gates"] == [
        "mapping-approval",
        "accepted-plan",
    ]
    assert commands["dbt-review"]["gates"] == ["named-human-approval"]
    assert all(commands[name]["skill"] == "dbt-workflows" for name in COMMANDS)
    assert all(commands[name]["cli_verbs"] == ["dbt"] for name in COMMANDS)

    skill = next(item for item in surface["skills"] if item["name"] == "dbt-workflows")
    assert skill["platforms"] == ["claude", "codex"]
    assert skill["status"] == "shipped"


def test_dbt_wrappers_are_thin_governed_routes() -> None:
    requirements = {
        "dbt-doctor": ("seshat dbt doctor", "read-only"),
        "dbt-plan": ("seshat dbt plan", "digest"),
        "dbt-build": ("seshat dbt build", "--accept-plan"),
        "dbt-review": ("seshat dbt inspect-run", "named human"),
    }
    for name, phrases in requirements.items():
        path = TEMPLATES / "claude" / "commands" / f"{name}.md"
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert "Load the `dbt-workflows` skill" in text
        assert ".claude/skills/" not in text
        for phrase in phrases:
            assert phrase.casefold() in text.casefold(), name
        assert not re.search(
            r"(?<!seshat )\bdbt (?:parse|ls|build|test|show)\b", text
        ), name


def test_dbt_skill_encodes_fixed_workflow_and_human_stops() -> None:
    path = TEMPLATES / "shared" / "skills" / "dbt-workflows" / "SKILL.md"
    text = path.read_text(encoding="utf-8")

    assert text.startswith("---\nname: dbt-workflows\n")
    for command in (
        "seshat dbt doctor",
        "seshat dbt validate",
        "seshat dbt plan",
        "seshat dbt build",
        "seshat dbt test",
        "seshat dbt inspect-run",
    ):
        assert command in text
    for contract in (
        "[PENDING LIVE PROFILE]",
        "--accept-plan",
        "derived evidence",
        "named human",
        "migrations remain",
        "exit 4",
    ):
        assert contract.casefold() in text.casefold()
    assert ".claude/skills/" not in text


def test_dbt_templates_are_allowlisted_for_their_platforms() -> None:
    document = _yaml(ALLOWLIST)
    entries = {item["source"]: item for item in document["template_entries"]}
    skill_source = "distribution/bundle-templates/shared/skills/dbt-workflows/SKILL.md"
    assert entries[skill_source]["targets"] == {
        "claude": "skills/dbt-workflows/SKILL.md",
        "codex": "skills/dbt-workflows/SKILL.md",
    }
    for name in COMMANDS:
        source = f"distribution/bundle-templates/claude/commands/{name}.md"
        assert entries[source]["targets"] == {"claude": f"commands/{name}.md"}


def test_generated_dbt_skill_and_commands_equal_templates() -> None:
    skill = TEMPLATES / "shared" / "skills" / "dbt-workflows" / "SKILL.md"
    for platform, bundle in (
        ("claude", ROOT / "integrations" / "claude-code" / "seshat-bi"),
        ("codex", ROOT / "integrations" / "codex" / "seshat-bi"),
    ):
        generated = bundle / "skills" / "dbt-workflows" / "SKILL.md"
        assert generated.read_bytes() == skill.read_bytes(), platform
    for name in COMMANDS:
        template = TEMPLATES / "claude" / "commands" / f"{name}.md"
        generated = (
            ROOT
            / "integrations"
            / "claude-code"
            / "seshat-bi"
            / "commands"
            / f"{name}.md"
        )
        assert generated.read_bytes() == template.read_bytes(), name
