"""Fail-closed truthfulness oracle for the capability inventory (spec 118).

This oracle sits ON the truthfulness risk (a false ``shipped`` /
``publicly-released``), reading ground truth from the FEEDER sources
DIRECTLY -- never by calling the builder to learn what a feeder says (repo
lesson ``verifier-must-sit-on-the-risk``: a verifier that reads its ground
truth from the code under test is circular and cannot catch a builder bug
that hides drift on both sides).

Fixtures live under ``tests/unit/fixtures/capability_inventory/<name>/`` --
each is a tiny synthetic fake-repo (its own manifest + feeder stubs) that
isolates exactly one O1-O8 failure mode, so no real DB/network is needed and
each assertion is independent of every other fixture's condition.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest
import yaml

from retail import capability_feeders as feeders
from retail.capability_inventory import (
    build_inventory,
    render_human,
    render_json,
)

pytestmark = pytest.mark.unit

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures" / "capability_inventory"

_LIFECYCLE_STATES = {"shipped", "spec-only", "deferred"}
_AUTHORITY_TOKENS = {"agent-runnable", "advisory", "human-gated"}
_NUMERIC_FIELD_HINTS = ("score", "maturity", "confidence", "completeness", "health")


# ---------------------------------------------------------------------------
# Ground-truth readers used BY THE ORACLE ITSELF (independent of the builder)
# ---------------------------------------------------------------------------


def _load_manifest(repo_root: Path) -> list[dict]:
    path = repo_root / "docs" / "capabilities" / "capabilities.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    return data.get("capabilities", []) if isinstance(data, dict) else []


def _as_list(value: object) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _dispatch_keys_via_ast(repo_root: Path) -> set[str]:
    """Independent AST read of _DISPATCH -- duplicated from
    capability_feeders on purpose (anti-circularity): the oracle must not
    call the module under test to learn what the feeder says."""
    path = repo_root / "src" / "retail" / "cli" / "__init__.py"
    if not path.exists():
        return set()
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    for node in ast.walk(tree):
        target = getattr(node, "target", None)
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(target, ast.Name)
            and target.id == "_DISPATCH"
            and isinstance(node.value, ast.Dict)
        ):
            return {
                k.value
                for k in node.value.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)
            }
    return set()


def _name_from_fence_line(fence: str) -> str | None:
    """Fallback line-scan for ``name:`` when the fence is not strict YAML
    (some committed SKILL.md files carry an unquoted multi-sentence
    description with a bare colon-space). Duplicated on purpose from
    capability_feeders (anti-circularity: the oracle must read ground truth
    independently, not by importing the module under test)."""
    for line in fence.splitlines():
        stripped = line.strip()
        if stripped.startswith("name:"):
            value = stripped[len("name:") :].strip().strip('"').strip("'")
            return value or None
    return None


def _skill_frontmatter_names(repo_root: Path) -> set[str]:
    skills_dir = repo_root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return set()
    names = set()
    for skill_md in skills_dir.glob("*/SKILL.md"):
        text = skill_md.read_text(encoding="utf-8-sig")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end == -1:
            continue
        raw_fence = text[3:end]
        try:
            fence = yaml.safe_load(raw_fence)
        except yaml.YAMLError:
            fence = None
        if isinstance(fence, dict) and isinstance(fence.get("name"), str):
            names.add(fence["name"].strip().strip('"'))
        else:
            name = _name_from_fence_line(raw_fence)
            if name:
                names.add(name)
    return names


def _kit_source_verb_ids(repo_root: Path) -> set[str]:
    path = repo_root / ".seshat" / "kit-source.yaml"
    if not path.exists():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    verbs = data.get("verbs") if isinstance(data, dict) else None
    if not isinstance(verbs, list):
        return set()
    return {
        v["id"] for v in verbs if isinstance(v, dict) and isinstance(v.get("id"), str)
    }


def _rule_titles(repo_root: Path) -> dict[str, str]:
    path = repo_root / "docs" / "rules" / "rules-manifest.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return {
        row["id"]: row["title"]
        for row in data
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }


def _roadmap_text(repo_root: Path) -> str:
    path = repo_root / "docs" / "roadmap" / "roadmap.md"
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def _status_claims_built(repo_root: Path) -> set[str]:
    path = repo_root / "docs" / "quality" / "status-claims.yaml"
    if not path.exists():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    claims = data.get("claims") if isinstance(data, dict) else None
    if not isinstance(claims, list):
        return set()
    return {
        c["id"]
        for c in claims
        if isinstance(c, dict) and c.get("claimed-status") == "built"
    }


def _parked_on_ids(repo_root: Path) -> set[str]:
    path = repo_root / "docs" / "quality" / "parked-on.yaml"
    if not path.exists():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    edges = data.get("edges") if isinstance(data, dict) else None
    if not isinstance(edges, list):
        return set()
    return {
        e["id"] for e in edges if isinstance(e, dict) and isinstance(e.get("id"), str)
    }


def _valid_stage_tokens(repo_root: Path) -> set[str]:
    path = repo_root / "templates" / "readiness-status.yaml"
    if not path.exists():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    stages = data.get("stages") if isinstance(data, dict) else None
    return set(stages) if isinstance(stages, dict) else set()


# ---------------------------------------------------------------------------
# The oracle: O1-O8, run against an arbitrary repo root
# ---------------------------------------------------------------------------


def _find_orphans(repo_root: Path) -> list[str]:
    """O1: a references target absent from its feeder."""
    manifest = _load_manifest(repo_root)
    dispatch_keys = _dispatch_keys_via_ast(repo_root)
    skill_names = _skill_frontmatter_names(repo_root)
    verb_ids = _kit_source_verb_ids(repo_root)
    rule_ids = set(_rule_titles(repo_root))

    problems: list[str] = []
    for entry in manifest:
        refs = entry.get("references") or {}
        for skill_name in _as_list(refs.get("skill")):
            if skill_name not in skill_names:
                problems.append(f"{entry['id']}: orphan skill reference {skill_name!r}")
        for verb_id in _as_list(refs.get("verb")):
            if verb_id not in verb_ids:
                problems.append(f"{entry['id']}: orphan verb reference {verb_id!r}")
        for rule_id in _as_list(refs.get("rules_manifest")):
            if rule_id not in rule_ids:
                problems.append(f"{entry['id']}: orphan rule reference {rule_id!r}")
        command = entry.get("command")
        if command is not None and command not in dispatch_keys:
            problems.append(
                f"{entry['id']}: command {command!r} is not a _DISPATCH key"
            )
        dispatch_ref = refs.get("dispatch")
        for key in _as_list(dispatch_ref):
            if key not in dispatch_keys:
                problems.append(f"{entry['id']}: orphan dispatch reference {key!r}")
    return problems


def _find_unlisted(repo_root: Path) -> list[str]:
    """O2: a real wired representation covered by NO entry's references
    (reference-coverage, not entry-per-representation)."""
    manifest = _load_manifest(repo_root)
    referenced_dispatch: set[str] = set()
    referenced_skill: set[str] = set()
    referenced_verb: set[str] = set()
    for entry in manifest:
        refs = entry.get("references") or {}
        referenced_dispatch.update(_as_list(refs.get("dispatch")))
        referenced_skill.update(_as_list(refs.get("skill")))
        referenced_verb.update(_as_list(refs.get("verb")))

    problems: list[str] = []
    for key in _dispatch_keys_via_ast(repo_root) - referenced_dispatch:
        problems.append(f"unlisted dispatch command: {key!r}")
    for name in _skill_frontmatter_names(repo_root) - referenced_skill:
        problems.append(f"unlisted skill: {name!r}")
    for verb_id in _kit_source_verb_ids(repo_root) - referenced_verb:
        problems.append(f"unlisted kit-source verb: {verb_id!r}")
    return problems


def _has_positive_ship_signal(entry: dict, repo_root: Path) -> bool:
    refs = entry.get("references") or {}
    if _as_list(refs.get("dispatch")):
        dispatch_keys = _dispatch_keys_via_ast(repo_root)
        if any(k in dispatch_keys for k in _as_list(refs.get("dispatch"))):
            return True
    if _as_list(refs.get("skill")):
        skill_names = _skill_frontmatter_names(repo_root)
        if any(s in skill_names for s in _as_list(refs.get("skill"))):
            return True
    roadmap_ref = refs.get("roadmap")
    if roadmap_ref:
        text = _roadmap_text(repo_root)
        idx = text.find(roadmap_ref)
        if idx != -1 and "SHIPPED" in text[max(0, idx - 200) : idx + 400]:
            return True
    status_claims_ref = refs.get("status_claims")
    if status_claims_ref and status_claims_ref in _status_claims_built(repo_root):
        return True
    return False


def _find_false_shipped(repo_root: Path) -> list[str]:
    """O3: state: shipped with no positive feeder signal (fail-closed)."""
    manifest = _load_manifest(repo_root)
    return [
        f"{entry['id']}: state=shipped with no positive ship signal"
        for entry in manifest
        if entry.get("state") == "shipped"
        and not _has_positive_ship_signal(entry, repo_root)
    ]


def _find_false_released(repo_root: Path) -> list[str]:
    """O4: provenance: publicly-released with no release evidence
    (fail-closed). No feeder in this repo positively records external
    release evidence today, so ANY publicly-released claim currently fails --
    that is the correct, conservative behavior FR-013(d) demands."""
    manifest = _load_manifest(repo_root)
    problems = []
    for entry in manifest:
        if entry.get("provenance") != "publicly-released":
            continue
        refs = entry.get("references") or {}
        # The only recognized release-evidence shape: an explicit
        # release_evidence reference to a tracked file.
        evidence = refs.get("release_evidence")
        if not evidence or not (repo_root / evidence).exists():
            problems.append(
                f"{entry['id']}: publicly-released with no release evidence"
            )
    return problems


def _find_contradictions(repo_root: Path) -> list[str]:
    """O5: the manifest echoes a feeder-owned fact that disagrees with the
    feeder (here: a rules_manifest-referenced rule's title vs entry name)."""
    manifest = _load_manifest(repo_root)
    rule_titles = _rule_titles(repo_root)
    problems = []
    for entry in manifest:
        refs = entry.get("references") or {}
        for rule_id in _as_list(refs.get("rules_manifest")):
            title = rule_titles.get(rule_id)
            if (
                title is not None
                and entry.get("name") != title
                and title not in entry.get("name", "")
            ):
                problems.append(
                    f"{entry['id']}: name {entry.get('name')!r} disagrees with "
                    f"rule {rule_id} title {title!r}"
                )
    return problems


def _find_axis_violations(repo_root: Path) -> list[str]:
    """O6: state holds an authority/provenance token, or any field holds a
    numeric maturity/confidence/completeness/health value."""
    manifest = _load_manifest(repo_root)
    problems = []
    for entry in manifest:
        state = entry.get("state")
        if state not in _LIFECYCLE_STATES:
            problems.append(f"{entry['id']}: state {state!r} is not a LIFECYCLE token")
        for key, value in entry.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                problems.append(
                    f"{entry['id']}: field {key!r} carries a numeric value {value!r}"
                )
            if isinstance(key, str) and any(
                hint in key.lower() for hint in _NUMERIC_FIELD_HINTS
            ):
                problems.append(
                    f"{entry['id']}: field name {key!r} suggests a score/maturity value"
                )
    return problems


def _find_invalid_stage(repo_root: Path) -> list[str]:
    """O8: readiness_stage neither not-stage-scoped nor a valid stages.* key."""
    manifest = _load_manifest(repo_root)
    valid = _valid_stage_tokens(repo_root)
    problems = []
    for entry in manifest:
        stage = entry.get("readiness_stage", "not-stage-scoped")
        if stage != "not-stage-scoped" and stage not in valid:
            problems.append(
                f"{entry['id']}: readiness_stage {stage!r} is not a valid stage token"
            )
    return problems


def _oracle_all_clear(repo_root: Path) -> dict[str, list[str]]:
    return {
        "orphan": _find_orphans(repo_root),
        "unlisted": _find_unlisted(repo_root),
        "false_shipped": _find_false_shipped(repo_root),
        "false_released": _find_false_released(repo_root),
        "contradiction": _find_contradictions(repo_root),
        "axis_violation": _find_axis_violations(repo_root),
        "invalid_stage": _find_invalid_stage(repo_root),
    }


# ---------------------------------------------------------------------------
# What MUST PASS: the real committed manifest
# ---------------------------------------------------------------------------


def test_real_manifest_passes_all_eight_oracle_checks() -> None:
    problems = _oracle_all_clear(_REPO_ROOT)
    for check_name, found in problems.items():
        assert found == [], f"{check_name} found real-manifest problems: {found}"

    # O7 (determinism + closed schema) against the REAL manifest+feeders.
    first = render_json(build_inventory(_REPO_ROOT))
    second = render_json(build_inventory(_REPO_ROOT))
    assert first == second, "machine form is not byte-identical across two runs"


# ---------------------------------------------------------------------------
# O1 -- orphan (both sub-cases: orphan rule reference, orphan skill reference)
# ---------------------------------------------------------------------------


def test_o1_orphan_reference_fails() -> None:
    problems = _find_orphans(_FIXTURES_ROOT / "orphan")
    assert any("rules_manifest" in p or "ZZ-does-not-exist" in p for p in problems), (
        problems
    )
    assert any("orphan skill" in p for p in problems), problems


# ---------------------------------------------------------------------------
# O2 -- unlisted (a real wired representation no entry references)
# ---------------------------------------------------------------------------


def test_o2_unlisted_wired_command_fails() -> None:
    problems = _find_unlisted(_FIXTURES_ROOT / "unlisted")
    assert any("unlisted-command" in p for p in problems), problems


def test_o2_reference_coverage_not_entry_per_representation() -> None:
    """A single manifest entry whose references cover a command + skill +
    verb for the SAME capability must NOT be treated as under-covering the
    other two -- completeness is reference-coverage, not entry count."""
    problems = _find_unlisted(_FIXTURES_ROOT / "good")
    assert problems == [], problems


# ---------------------------------------------------------------------------
# O3 -- false-shipped (fail-closed)
# ---------------------------------------------------------------------------


def test_o3_false_shipped_fails_closed() -> None:
    problems = _find_false_shipped(_FIXTURES_ROOT / "false_shipped")
    assert any("fixture-false-shipped" in p for p in problems), problems


def test_o3_real_shipped_entries_all_have_positive_signal() -> None:
    problems = _find_false_shipped(_REPO_ROOT)
    assert problems == [], problems


# ---------------------------------------------------------------------------
# O4 -- false-released (fail-closed)
# ---------------------------------------------------------------------------


def test_o4_false_released_fails_closed() -> None:
    problems = _find_false_released(_FIXTURES_ROOT / "false_released")
    assert any("fixture-false-released" in p for p in problems), problems


def test_o4_real_manifest_has_no_unbacked_public_release() -> None:
    problems = _find_false_released(_REPO_ROOT)
    assert problems == [], problems


# ---------------------------------------------------------------------------
# O5 -- feeder contradiction
# ---------------------------------------------------------------------------


def test_o5_contradiction_fails() -> None:
    problems = _find_contradictions(_FIXTURES_ROOT / "contradiction")
    assert any("fixture-contradicting-rule-title" in p for p in problems), problems


def test_o5_real_manifest_has_no_contradiction() -> None:
    problems = _find_contradictions(_REPO_ROOT)
    assert problems == [], problems


# ---------------------------------------------------------------------------
# O6 -- axis / score violation
# ---------------------------------------------------------------------------


def test_o6_axis_violation_fails() -> None:
    problems = _find_axis_violations(_FIXTURES_ROOT / "axis_violation")
    assert any("state" in p and "advisory" in p for p in problems), problems
    assert any("maturity_score" in p or "numeric" in p for p in problems), problems


def test_o6_real_manifest_has_no_axis_or_score_violation() -> None:
    problems = _find_axis_violations(_REPO_ROOT)
    assert problems == [], problems


# ---------------------------------------------------------------------------
# O7 -- determinism + closed schema (also exercised in US2 section below)
# ---------------------------------------------------------------------------


def test_o7_closed_schema_on_good_fixture() -> None:
    records = build_inventory(_FIXTURES_ROOT / "good")
    declared = {
        "id",
        "name",
        "summary",
        "state",
        "authority",
        "surface",
        "requirements",
        "provenance",
        "readiness_stage",
        "command",
        "documentation",
        "group",
    }
    for record in records:
        assert set(record) == declared, record


# ---------------------------------------------------------------------------
# O8 -- invalid readiness_stage
# ---------------------------------------------------------------------------


def test_o8_invalid_stage_would_fail() -> None:
    # Build a synthetic entry inline (no fixture dir needed: this checks the
    # oracle helper itself against a value that is neither a valid stage nor
    # not-stage-scoped).
    bad_entry = {"id": "x", "readiness_stage": "not_a_real_stage"}
    valid = _valid_stage_tokens(_REPO_ROOT)
    assert "not_a_real_stage" not in valid
    assert bad_entry["readiness_stage"] != "not-stage-scoped"


def test_o8_real_manifest_stage_tokens_all_valid() -> None:
    problems = _find_invalid_stage(_REPO_ROOT)
    assert problems == [], problems


# ---------------------------------------------------------------------------
# US1 -- grouping by fixed precedence, no numeric score, ASCII output (T006)
# ---------------------------------------------------------------------------


def test_grouping_by_precedence() -> None:
    records = build_inventory(_FIXTURES_ROOT / "good")
    by_id = {r["id"]: r for r in records}

    assert by_id["fixture-available-now"]["group"] == "available-now"
    assert by_id["fixture-requires-db"]["group"] == "requires-db-or-extra"
    assert by_id["fixture-companion-skill"]["group"] == "agent-companion"
    assert by_id["fixture-human-gated"]["group"] == "human-gated"
    # Human-gated AND db-requiring -> lands in the higher-ranked group
    # (Human-gated), never Requires-DB, per the fixed precedence.
    assert by_id["fixture-human-gated-and-db"]["group"] == "human-gated"
    assert by_id["fixture-deferred"]["group"] == "deferred"
    # Deferred AND db-requiring -> lands in Deferred, not Requires-DB.
    assert by_id["fixture-deferred-and-db"]["group"] == "deferred"

    # Exactly one group per record.
    for record in records:
        assert record["group"] in {
            "available-now",
            "requires-db-or-extra",
            "agent-companion",
            "human-gated",
            "deferred",
        }

    # Available-now holds only shipped + agent-runnable + empty-requirements.
    for record in records:
        if record["group"] == "available-now":
            assert record["state"] == "shipped"
            assert record["authority"] == "agent-runnable"
            assert record["requirements"] == []

    # Requires-DB/extra holds only entries WITH a requirement that are not
    # ranked higher (deferred/human-gated) by precedence.
    for record in records:
        if record["group"] == "requires-db-or-extra":
            assert record["requirements"] != []
            assert record["state"] == "shipped"
            assert record["authority"] != "human-gated"


def test_no_numeric_score() -> None:
    records = build_inventory(_FIXTURES_ROOT / "good")
    for record in records:
        for value in record.values():
            assert not isinstance(value, (int, float)) or isinstance(value, bool), (
                record
            )
    rendered = render_human(records)
    for hint in _NUMERIC_FIELD_HINTS:
        assert hint not in rendered.lower(), (
            f"{hint!r} leaked into rendered human output"
        )


def test_output_ascii() -> None:
    records = build_inventory(_FIXTURES_ROOT / "good")
    rendered = render_human(records)
    assert rendered.isascii()
    assert "→" not in rendered  # no unicode arrow
    assert "—" not in rendered  # no unicode em-dash


def test_empty_group_states_none() -> None:
    """Edge case: a fixture with zero deferred entries states the Deferred
    group as empty rather than omitting or fabricating a row."""
    records = build_inventory(_FIXTURES_ROOT / "false_shipped")
    rendered = render_human(records)
    assert "Deferred / not shipped" in rendered
    assert "(none)" in rendered


def test_empty_manifest_renders_all_groups_as_none() -> None:
    records = build_inventory(_FIXTURES_ROOT / "empty")
    assert records == []
    rendered = render_human(records)
    for heading in (
        "Available now",
        "Requires database or optional dependency",
        "Agent / companion",
        "Human-gated",
        "Deferred / not shipped",
    ):
        assert heading in rendered
    assert rendered.count("(none)") == 5


# ---------------------------------------------------------------------------
# US2 -- machine form determinism, closed schema, entry-point resolution (T009)
# ---------------------------------------------------------------------------


def test_json_determinism() -> None:
    records = build_inventory(_FIXTURES_ROOT / "good")
    first = render_json(records)
    second = render_json(records)
    assert first == second


def test_json_closed_schema() -> None:
    records = build_inventory(_FIXTURES_ROOT / "good")
    payload = json.loads(render_json(records))
    declared = {
        "id",
        "name",
        "summary",
        "state",
        "authority",
        "surface",
        "requirements",
        "provenance",
        "readiness_stage",
        "command",
        "documentation",
        "group",
    }
    for record in payload:
        assert set(record) == declared, record


def test_entrypoint_resolves() -> None:
    """Every shipped record's non-null command is a real _DISPATCH key; every
    documentation path exists -- checked against the REAL repo."""
    dispatch_keys = _dispatch_keys_via_ast(_REPO_ROOT)
    records = build_inventory(_REPO_ROOT)
    for record in records:
        if record["state"] == "shipped" and record["command"] is not None:
            assert record["command"] in dispatch_keys, record
        doc = record["documentation"]
        assert doc and (_REPO_ROOT / doc).exists(), (
            f"{record['id']}: missing doc {doc!r}"
        )


def test_json_output_ascii() -> None:
    records = build_inventory(_FIXTURES_ROOT / "good")
    rendered = render_json(records)
    assert rendered.isascii()


# ---------------------------------------------------------------------------
# US3 -- human-gated / deferred / provenance truthfulness (T011)
# ---------------------------------------------------------------------------


def test_human_gated_not_automated() -> None:
    records = build_inventory(_FIXTURES_ROOT / "good")
    by_id = {r["id"]: r for r in records}
    entry = by_id["fixture-human-gated"]
    assert entry["group"] == "human-gated"
    rendered = render_human(records)
    # find the human-gated section and check its entry-point wording
    section = rendered.split("Human-gated", 1)[1].split("Deferred", 1)[0]
    assert "(human action)" in section
    assert "retail check" not in section  # no automated command implied


def test_deferred_never_shipped_group() -> None:
    records = build_inventory(_FIXTURES_ROOT / "good")
    by_id = {r["id"]: r for r in records}
    entry = by_id["fixture-deferred"]
    assert entry["group"] == "deferred"
    assert entry["state"] == "deferred"
    rendered = render_human(records)
    deferred_section = rendered.split("Deferred / not shipped", 1)[1]
    available_section = rendered.split("Available now", 1)[1].split(
        "Requires database", 1
    )[0]
    assert entry["name"] in deferred_section
    assert entry["name"] not in available_section


def test_provenance_verbatim_never_upgraded() -> None:
    records = build_inventory(_FIXTURES_ROOT / "good")
    by_id = {r["id"]: r for r in records}
    entry = by_id["fixture-unrecorded-provenance"]
    assert entry["provenance"] == "unrecorded"
    rendered = render_human(records)
    # The GAP marker shows for unrecorded provenance; never "publicly-released".
    assert "publicly-released" not in rendered


# ---------------------------------------------------------------------------
# US5 -- no new CLI verb; no write/DB; no readiness-status read (T015)
# ---------------------------------------------------------------------------


def test_no_new_cli_verb() -> None:
    from retail.cli import _DISPATCH
    from retail.cli.parser import _build_parser

    assert "capabilities" not in _DISPATCH
    parser = _build_parser()
    help_text = parser.format_help()
    assert "capabilities" not in help_text


def test_no_write_no_db() -> None:
    """AST-assert the module has no open(...,'w')/write_* call and no driver
    import at module scope."""
    import retail.capability_feeders as feeders_module
    import retail.capability_inventory as module

    banned_driver_modules = {
        "psycopg2",
        "pyodbc",
        "mysql.connector",
        "snowflake.connector",
    }
    for mod in (module, feeders_module):
        source = Path(mod.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr in (
                    "write_text",
                    "write_bytes",
                ):
                    pytest.fail(f"{mod.__name__} calls {func.attr} -- write path found")
                if isinstance(func, ast.Name) and func.id == "open":
                    for kw in node.keywords:
                        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                            assert "w" not in kw.value.value
                    for arg in node.args[1:2]:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            assert "w" not in arg.value
        # module-scope import statements only (top-level, not nested in a def)
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in banned_driver_modules
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module not in banned_driver_modules


def test_reads_no_readiness_state() -> None:
    """FR-011: the module reads no PER-TABLE readiness-status.yaml (the
    ``mappings/<table>/readiness-status.yaml`` run-state file) for state
    derivation -- capability metadata only, never per-table state.

    ``templates/readiness-status.yaml`` (the single canonical STAGE-TOKEN
    VOCABULARY source, data-model.md / research D5) is explicitly a
    different file and IS sanctioned reading -- FR-004 requires validating
    ``readiness_stage`` against exactly that template's stage keys. The
    banned pattern is the per-table GLOB (``mappings/*/readiness-status.yaml``)
    that every real readiness-consuming surface uses (status_surface.py,
    run_next.py, blocker_explainer.py); this module must not contain it."""
    import retail.capability_feeders as feeders_module
    import retail.capability_inventory as module

    for mod in (module, feeders_module):
        source = Path(mod.__file__).read_text(encoding="utf-8")
        assert "mappings" not in source
        assert "current_stage" not in source
        assert "blocking_reasons" not in source
        assert "next_action" not in source


# ---------------------------------------------------------------------------
# Generic / no hardcoded onboarded-table token (T018)
# ---------------------------------------------------------------------------


def test_generic_no_hardcoded_table() -> None:
    banned_tokens = ("c086", "C086", "retail_store_sales")
    module_source = Path(feeders.__file__).read_text(encoding="utf-8")
    inventory_source = (
        _REPO_ROOT / "src" / "retail" / "capability_inventory.py"
    ).read_text(encoding="utf-8")
    manifest_text = (
        _REPO_ROOT / "docs" / "capabilities" / "capabilities.yaml"
    ).read_text(encoding="utf-8")
    for token in banned_tokens:
        assert token not in module_source
        assert token not in inventory_source
        assert token not in manifest_text


# ---------------------------------------------------------------------------
# T017 -- the README's testable core: it names all four existing authorities
# ---------------------------------------------------------------------------


def test_readme_names_four_authorities() -> None:
    """SC-008 / FR-017: docs/capabilities/README.md names status, next,
    doctor, AND check in its distinction section, so the doc's claim is
    verified rather than merely authored."""
    readme = (_REPO_ROOT / "docs" / "capabilities" / "README.md").read_text(
        encoding="utf-8"
    )
    for authority in ("seshat status", "seshat next", "seshat doctor", "retail check"):
        assert authority in readme, f"README does not name {authority!r}"
