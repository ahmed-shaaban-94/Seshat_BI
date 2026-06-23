from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from retail import gitutil
from retail.core import RuleContext, Severity
from retail.rules.git_meta import (
    _read_leading_bytes,
    check_gitattributes_eol,
    rule_c2_no_committed_secrets,
    rule_g1_gitignore_correctness,
    rule_g2_definition_committed,
    rule_g3_no_bom,
    rule_g5_path_length,
    rule_p1_layout,
    rule_p2_commit_subjects,
)
from tests.unit._gitfix import commit_all, context_for, make_git_repo

# ---------------------------------------------------------------------------
# M2.1 — gitutil
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_git_check_ignore_respects_gitignore(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    (repo / ".gitignore").write_text(".env\n", encoding="utf-8")
    (repo / ".env").write_text("SECRET=x\n", encoding="utf-8")
    (repo / "keep.txt").write_text("ok\n", encoding="utf-8")
    assert gitutil.git_check_ignore(repo, ".env") is True
    assert gitutil.git_check_ignore(repo, "keep.txt") is False


# ---------------------------------------------------------------------------
# M2.2 — G5
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_g5_flags_long_path() -> None:
    long_path = "warehouse/migrations/" + ("x" * 201) + ".sql"
    assert len(long_path) > 200
    ctx = RuleContext(repo_root=Path("."), tracked_files=(long_path, "ok.sql"))
    findings = list(rule_g5_path_length(ctx))
    assert len(findings) == 1
    f = findings[0]
    assert f.rule_id == "G5"
    assert f.severity is Severity.ERROR
    assert f.locator == long_path


@pytest.mark.unit
def test_g5_passes_short_paths() -> None:
    ctx = RuleContext(repo_root=Path("."), tracked_files=("warehouse/x.sql",))
    assert list(rule_g5_path_length(ctx)) == []


# ---------------------------------------------------------------------------
# M2.3 — P1
# ---------------------------------------------------------------------------

GOOD_LAYOUT = (
    "README.md",
    "warehouse/README.md",
    "powerbi/README.md",
    "warehouse/migrations/0001_init.sql",
    "powerbi/Sales.pbip",
)


@pytest.mark.unit
def test_p1_accepts_good_layout() -> None:
    ctx = RuleContext(repo_root=Path("."), tracked_files=GOOD_LAYOUT)
    assert list(rule_p1_layout(ctx)) == []


@pytest.mark.unit
def test_p1_flags_misplaced_sql_and_pbip() -> None:
    tracked = GOOD_LAYOUT + ("scripts/adhoc.sql", "reports/Sales.pbip")
    ctx = RuleContext(repo_root=Path("."), tracked_files=tracked)
    ids = {f.locator for f in rule_p1_layout(ctx)}
    assert "scripts/adhoc.sql" in ids
    assert "reports/Sales.pbip" in ids


@pytest.mark.unit
def test_p1_flags_missing_required_dir() -> None:
    tracked = ("README.md", "warehouse/README.md")  # no powerbi/README.md
    ctx = RuleContext(repo_root=Path("."), tracked_files=tracked)
    findings = list(rule_p1_layout(ctx))
    assert any(f.locator == "powerbi/README.md" for f in findings)
    assert all(f.severity is Severity.ERROR for f in findings)


@pytest.mark.unit
def test_p1_exempts_pbip_under_tests() -> None:
    # A committed test fixture .pbip under tests/ is NOT the live model -> skipped.
    tracked = GOOD_LAYOUT + ("tests/fixtures/golden_pbip/RetailGold.pbip",)
    ctx = RuleContext(repo_root=Path("."), tracked_files=tracked)
    locators = {f.locator for f in rule_p1_layout(ctx)}
    assert "tests/fixtures/golden_pbip/RetailGold.pbip" not in locators


@pytest.mark.unit
def test_p1_still_flags_pbip_outside_powerbi_and_tests() -> None:
    # A .pbip outside both powerbi/ and tests/ IS still flagged.
    tracked = GOOD_LAYOUT + ("reports/Sales.pbip",)
    ctx = RuleContext(repo_root=Path("."), tracked_files=tracked)
    locators = {f.locator for f in rule_p1_layout(ctx)}
    assert "reports/Sales.pbip" in locators


@pytest.mark.unit
def test_p1_exempts_sql_under_tests() -> None:
    # A .sql under tests/ is NOT forced under warehouse/ -> skipped.
    tracked = GOOD_LAYOUT + ("tests/fixtures/seed.sql",)
    ctx = RuleContext(repo_root=Path("."), tracked_files=tracked)
    locators = {f.locator for f in rule_p1_layout(ctx)}
    assert "tests/fixtures/seed.sql" not in locators


@pytest.mark.unit
def test_p1_still_flags_sql_outside_warehouse_and_tests() -> None:
    # A .sql outside both warehouse/ and tests/ IS still flagged.
    tracked = GOOD_LAYOUT + ("scripts/adhoc.sql",)
    ctx = RuleContext(repo_root=Path("."), tracked_files=tracked)
    locators = {f.locator for f in rule_p1_layout(ctx)}
    assert "scripts/adhoc.sql" in locators


# ---------------------------------------------------------------------------
# M2.4 — G1
# ---------------------------------------------------------------------------

GOOD_GITIGNORE = (
    "**/.pbi/localSettings.json\n"
    "**/.pbi/cache.abf\n"
    ".env\n"
    "__pycache__/\n"  # extra entry — permitted
)


@pytest.mark.unit
def test_g1_accepts_correct_gitignore(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    (repo / ".gitignore").write_text(GOOD_GITIGNORE, encoding="utf-8")
    commit_all(repo, "chore: add gitignore")
    assert list(rule_g1_gitignore_correctness(context_for(repo))) == []


@pytest.mark.unit
def test_g1_flags_missing_required_entry(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    (repo / ".gitignore").write_text("**/.pbi/cache.abf\n.env\n", encoding="utf-8")
    commit_all(repo, "chore: add gitignore")
    findings = list(rule_g1_gitignore_correctness(context_for(repo)))
    assert any("localSettings.json" in f.message for f in findings)
    assert all(f.severity is Severity.ERROR for f in findings)


@pytest.mark.unit
def test_g1_flags_ignored_definition_path(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    (repo / ".gitignore").write_text(GOOD_GITIGNORE + "definition/\n", encoding="utf-8")
    commit_all(repo, "chore: add gitignore")
    findings = list(rule_g1_gitignore_correctness(context_for(repo)))
    assert any("definition" in f.locator for f in findings)


# ---------------------------------------------------------------------------
# M2.5 — G2
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_g2_emits_info_when_no_pbip(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    (repo / "README.md").write_text("hi\n", encoding="utf-8")
    commit_all(repo, "docs: readme")
    findings = list(rule_g2_definition_committed(context_for(repo)))
    assert len(findings) == 1
    assert findings[0].severity is Severity.INFO
    assert findings[0].message == "no PBIP project present"


@pytest.mark.unit
def test_g2_flags_tracked_cache_abf(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    pbip_dir = repo / "powerbi" / "Sales.SemanticModel" / "definition"
    pbip_dir.mkdir(parents=True)
    (pbip_dir / "model.tmdl").write_text("model\n", encoding="utf-8")
    (repo / "powerbi" / "Sales.pbip").write_text("{}\n", encoding="utf-8")
    pbi_dir = repo / "powerbi" / "Sales.SemanticModel" / ".pbi"
    pbi_dir.mkdir(parents=True)
    (pbi_dir / "cache.abf").write_text("x\n", encoding="utf-8")
    commit_all(repo, "feat: add pbip with stray cache")
    findings = list(rule_g2_definition_committed(context_for(repo)))
    assert any(
        "cache.abf" in f.locator and f.severity is Severity.ERROR for f in findings
    )


# ---------------------------------------------------------------------------
# M2.6 — P2
# ---------------------------------------------------------------------------


def _build_p2_history(repo: Path) -> str:
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "feat: base"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "fix: ok change"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "bad subject here"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    return base


@pytest.mark.unit
def test_p2_flags_bad_subject(tmp_path: Path) -> None:
    import dataclasses

    repo = make_git_repo(tmp_path)
    base = _build_p2_history(repo)
    # CI mode: scope P2 to a commit range via the contract field (no env var).
    ctx = dataclasses.replace(context_for(repo), commit_range=base)
    findings = list(rule_p2_commit_subjects(ctx))
    assert len(findings) == 1
    assert findings[0].rule_id == "P2"
    assert findings[0].locator == "bad subject here"
    assert findings[0].severity is Severity.ERROR


@pytest.mark.unit
def test_p2_validates_single_commit_message(tmp_path: Path) -> None:
    import dataclasses

    repo = make_git_repo(tmp_path)
    # commit-msg-hook mode: a single incoming subject via ctx.commit_message.
    ctx = dataclasses.replace(context_for(repo), commit_message="bad subject here")
    findings = list(rule_p2_commit_subjects(ctx))
    assert len(findings) == 1
    assert findings[0].locator == "bad subject here"
    # A conforming message yields no findings.
    ok = dataclasses.replace(context_for(repo), commit_message="feat: a thing")
    assert list(rule_p2_commit_subjects(ok)) == []


@pytest.mark.unit
def test_p2_exempts_merge_commits(tmp_path: Path) -> None:
    import dataclasses

    repo = make_git_repo(tmp_path)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "feat: base"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    subprocess.run(
        ["git", "checkout", "-b", "side"], cwd=repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "feat: side work"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "checkout", "main"], cwd=repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "merge", "--no-ff", "side", "-m", "Merge branch 'side'"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    ctx = dataclasses.replace(context_for(repo), commit_range=base)
    assert list(rule_p2_commit_subjects(ctx)) == []


# ---------------------------------------------------------------------------
# M2.7 — C2
# ---------------------------------------------------------------------------

GOOD_ENV_EXAMPLE = (
    "ANALYTICS_DB_HOST=\n"
    "ANALYTICS_DB_PORT=25060\n"
    "ANALYTICS_DB_NAME=\n"
    "ANALYTICS_DB_USER=\n"
    "ANALYTICS_DB_PASSWORD=\n"
    "ANALYTICS_DB_SSLMODE=require\n"
)


def _seed_c2_repo(repo: Path) -> None:
    (repo / ".gitignore").write_text(".env\n", encoding="utf-8")
    (repo / ".env.example").write_text(GOOD_ENV_EXAMPLE, encoding="utf-8")


@pytest.mark.unit
def test_c2_clean_repo_passes(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    _seed_c2_repo(repo)
    commit_all(repo, "chore: seed env example")
    assert list(rule_c2_no_committed_secrets(context_for(repo))) == []


@pytest.mark.unit
def test_c2_flags_real_endpoint_in_scanned_file(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    _seed_c2_repo(repo)
    (repo / "config.txt").write_text(
        "host = db-prod-01.db.ondigitalocean.com\n", encoding="utf-8"
    )
    commit_all(repo, "chore: add config")
    findings = list(rule_c2_no_committed_secrets(context_for(repo)))
    assert any(f.locator.startswith("config.txt:") for f in findings)


@pytest.mark.unit
def test_c2_ignores_angle_bracket_placeholder_in_scanned_file(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    _seed_c2_repo(repo)
    # ROOT-level scanned file (not docs/, not *.example) — exercises the REGEX
    # exclusion, not the path exclusion.
    (repo / "config.txt").write_text(
        "host = <your-db-host>.db.ondigitalocean.com\n", encoding="utf-8"
    )
    commit_all(repo, "chore: add placeholder config")
    assert list(rule_c2_no_committed_secrets(context_for(repo))) == []


@pytest.mark.unit
def test_c2_skips_docs_and_example_files(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    _seed_c2_repo(repo)
    docs = repo / "docs"
    docs.mkdir()
    (docs / "conn.md").write_text(
        "postgresql://user:pw@real-host.db.ondigitalocean.com:25060/db\n",
        encoding="utf-8",
    )
    (repo / "settings.example").write_text(
        "postgresql://user:pw@real-host.db.ondigitalocean.com/db\n",
        encoding="utf-8",
    )
    commit_all(repo, "docs: add connection placeholders")
    assert list(rule_c2_no_committed_secrets(context_for(repo))) == []


@pytest.mark.unit
def test_c2_flags_tracked_env(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    _seed_c2_repo(repo)
    (repo / ".env").write_text("ANALYTICS_DB_PASSWORD=hunter2\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "-f", ".env"], cwd=repo, check=True, capture_output=True
    )
    commit_all(repo, "chore: oops env")
    findings = list(rule_c2_no_committed_secrets(context_for(repo)))
    assert any(f.locator == ".env" for f in findings)


@pytest.mark.unit
def test_c2_flags_env_example_with_filled_secret(tmp_path: Path) -> None:
    repo = make_git_repo(tmp_path)
    (repo / ".gitignore").write_text(".env\n", encoding="utf-8")
    bad = GOOD_ENV_EXAMPLE.replace(
        "ANALYTICS_DB_PASSWORD=\n", "ANALYTICS_DB_PASSWORD=secret\n"
    )
    (repo / ".env.example").write_text(bad, encoding="utf-8")
    commit_all(repo, "chore: bad example")
    findings = list(rule_c2_no_committed_secrets(context_for(repo)))
    assert any("ANALYTICS_DB_PASSWORD" in f.message for f in findings)


# ---------------------------------------------------------------------------
# M2.G3 — G3 UTF-8 without BOM
# ---------------------------------------------------------------------------

BOM = b"\xef\xbb\xbf"


def _write(path: Path, prefix: bytes, text: str) -> None:
    path.write_bytes(prefix + text.encode("utf-8"))


@pytest.mark.unit
def test_read_leading_bytes_returns_first_three_bytes(tmp_path: Path) -> None:
    f = tmp_path / "x.tmdl"
    f.write_bytes(BOM + b"table Sales")
    assert _read_leading_bytes(f) == BOM


@pytest.mark.unit
def test_read_leading_bytes_short_file_returns_fewer(tmp_path: Path) -> None:
    f = tmp_path / "x.tmdl"
    f.write_bytes(b"ab")
    assert _read_leading_bytes(f) == b"ab"


@pytest.mark.unit
def test_g3_flags_tmdl_with_bom(tmp_path: Path) -> None:
    _write(tmp_path / "withbom.tmdl", BOM, "table Sales")
    ctx = RuleContext(repo_root=tmp_path, tracked_files=("withbom.tmdl",))
    findings = list(rule_g3_no_bom(ctx))
    assert len(findings) == 1
    f = findings[0]
    assert f.rule_id == "G3"
    assert f.severity is Severity.ERROR
    assert f.locator == "withbom.tmdl"


@pytest.mark.unit
def test_g3_passes_tmdl_without_bom(tmp_path: Path) -> None:
    _write(tmp_path / "clean.tmdl", b"", "table Sales")
    ctx = RuleContext(repo_root=tmp_path, tracked_files=("clean.tmdl",))
    assert list(rule_g3_no_bom(ctx)) == []


@pytest.mark.unit
def test_g3_ignores_non_target_extension_with_bom(tmp_path: Path) -> None:
    # A .sql file WITH a BOM must NOT be flagged: G3 only covers
    # *.tmdl/*.pbir/*.json/*.pbism. This keeps the extension filter load-bearing.
    _write(tmp_path / "ddl.sql", BOM, "select 1")
    ctx = RuleContext(repo_root=tmp_path, tracked_files=("ddl.sql",))
    assert list(rule_g3_no_bom(ctx)) == []


# ---------------------------------------------------------------------------
# M2.G4 — G4 .gitattributes EOL policy
# ---------------------------------------------------------------------------


def _ctx_g4(tmp_path: Path) -> RuleContext:
    return RuleContext(repo_root=tmp_path, tracked_files=(".gitattributes",))


_PASSING_GITATTRIBUTES = """\
# Normalize line endings; Power BI Desktop writes CRLF for PBIP text files.
* text=auto

*.tmdl   text eol=crlf
*.pbir   text eol=crlf
*.pbism  text eol=crlf
*.json   text eol=crlf
*.sql    text eol=lf
*.md     text eol=lf
*.py     text eol=lf

*.pbix   binary
*.abf    binary
*.png    binary
*.svg    text eol=lf
*.toml   text eol=lf
*.yml    text eol=lf
"""


@pytest.mark.unit
def test_g4_passes_when_all_required_mappings_present(tmp_path: Path) -> None:
    (tmp_path / ".gitattributes").write_text(_PASSING_GITATTRIBUTES, encoding="utf-8")
    findings = list(check_gitattributes_eol(_ctx_g4(tmp_path)))
    assert findings == []


@pytest.mark.unit
def test_g4_flags_missing_tmdl_crlf(tmp_path: Path) -> None:
    # Drop the *.tmdl line entirely -> required glob absent.
    content = _PASSING_GITATTRIBUTES.replace("*.tmdl   text eol=crlf\n", "")
    (tmp_path / ".gitattributes").write_text(content, encoding="utf-8")
    findings = list(check_gitattributes_eol(_ctx_g4(tmp_path)))
    assert len(findings) == 1
    f = findings[0]
    assert f.rule_id == "G4"
    assert f.severity is Severity.ERROR
    assert "*.tmdl" in f.message
    assert "eol=crlf" in f.message
    # Glob absent -> locator is the bare file, no line number.
    assert f.locator == ".gitattributes"


@pytest.mark.unit
def test_g4_flags_contradicting_token_with_line_locator(tmp_path: Path) -> None:
    # *.sql present but declared eol=crlf instead of required eol=lf.
    content = _PASSING_GITATTRIBUTES.replace(
        "*.sql    text eol=lf", "*.sql    text eol=crlf"
    )
    (tmp_path / ".gitattributes").write_text(content, encoding="utf-8")
    findings = list(check_gitattributes_eol(_ctx_g4(tmp_path)))
    assert len(findings) == 1
    f = findings[0]
    assert f.rule_id == "G4"
    assert f.severity is Severity.ERROR
    assert "*.sql" in f.message
    # Line exists -> most-specific locator carries the line number.
    assert f.locator.startswith(".gitattributes:")


@pytest.mark.unit
def test_g4_flags_all_when_file_absent(tmp_path: Path) -> None:
    # No .gitattributes at all -> every required glob missing, no silent pass.
    findings = list(check_gitattributes_eol(_ctx_g4(tmp_path)))
    assert len(findings) == 10
    assert all(f.severity is Severity.ERROR for f in findings)
    assert all(f.locator == ".gitattributes" for f in findings)
