"""Offline unit tests for the co-resolution gate + freshness reporter (spec 136).

Every test here is deterministic and OFFLINE (FR-017): the resolve subprocess and
the PyPI JSON index are STUBBED, never contacted. The live resolve runs only in
the new co-resolution CI job, never in this unit path.

Fixtures below carry pip/PyPI output SHAPES captured from real invocations
(a real ResolutionImpossible stderr; a real `pip install --dry-run --report`
JSON envelope; the PyPI JSON `releases`/`info` shape with per-file `yanked`).
"""

from __future__ import annotations

import json

import pytest

pytestmark = pytest.mark.unit


# --------------------------------------------------------------------------- #
# Captured pip / PyPI output shapes (used by the stubs).
# --------------------------------------------------------------------------- #

# A real `pip install --dry-run --report -` JSON envelope (trimmed): the keys
# the parser reads are `install` (list) and each entry's `metadata.name/version`.
REPORT_PASS_JSON = json.dumps(
    {
        "version": "1",
        "pip_version": "26.0.1",
        "install": [
            {"metadata": {"name": "dbt-core", "version": "1.12.0"}},
            {"metadata": {"name": "sqlparse", "version": "0.5.5"}},
        ],
        "environment": {},
    }
)

# A real pip ResolutionImpossible stderr (captured from the spec-133/spec-134
# dbt-core==1.12.0 + dagster-dbt==0.29.14 conflict).
RESOLUTION_STDERR = (
    "ERROR: Cannot install dagster-dbt==0.29.14 and dbt-core==1.12.0 because "
    "these package versions have conflicting dependencies.\n\n"
    "The conflict is caused by:\n"
    "    The user requested dbt-core==1.12.0\n"
    "    dagster-dbt 0.29.14 depends on dbt-core<1.12 and >=1.7\n\n"
    "ERROR: ResolutionImpossible: for help visit "
    "https://pip.pypa.io/en/latest/topics/dependency-resolution/\n"
)

# A real network/index failure stderr (connection error signature).
INFRA_STDERR = (
    "WARNING: Retrying (Retry(total=4, connect=None, read=None, redirect=None, "
    "status=None)) after connection broken by 'NewConnectionError(...: Failed to "
    "establish a new connection: [Errno -3] Temporary failure in name "
    "resolution')': /simple/dbt-core/\n"
    "ERROR: Could not find a version that satisfies the requirement dbt-core\n"
    "ERROR: Network is unreachable\n"
)


def _pypi_json(name: str, versions_files: dict[str, list[dict]], info: dict) -> str:
    """Build a PyPI JSON API response body.

    ``versions_files`` maps each version string to its per-file list (each file
    is a dict that may carry a ``yanked`` flag). A release is yanked ONLY when
    ALL its files are yanked (plan-review D5, PER-FILE semantics).
    """
    return json.dumps({"info": {"name": name, **info}, "releases": versions_files})


# --------------------------------------------------------------------------- #
# Stub fixtures (the resolve subprocess + the PyPI index).
# --------------------------------------------------------------------------- #


@pytest.fixture
def stub_resolve(monkeypatch):
    """Patch dep_coresolve's resolve-subprocess seam.

    Yields a setter: call ``set(returncode=..., stdout=..., stderr=...)`` to
    program the next stubbed `pip install --dry-run --report` invocation. The
    stub NEVER launches a real subprocess, so no venv is created and nothing is
    installed into the test interpreter (SC-002).
    """
    import scripts.dep_coresolve as dc

    state = {"returncode": 0, "stdout": REPORT_PASS_JSON, "stderr": "", "calls": []}

    def fake_run_resolve(requirements, report_path):
        state["calls"].append(list(requirements))
        return dc.ResolveRun(
            returncode=state["returncode"],
            stdout=state["stdout"],
            stderr=state["stderr"],
            report_json=state["stdout"] if state["returncode"] == 0 else None,
        )

    monkeypatch.setattr(dc, "_run_resolve", fake_run_resolve)

    def _set(**kw):
        state.update(kw)

    _set.state = state  # expose recorded calls to the test
    yield _set


@pytest.fixture
def stub_pypi(monkeypatch):
    """Patch dep_coresolve's PyPI-fetch seam. Call ``set(dist, body)`` to
    program the JSON body returned for a distribution; the stub never hits the
    network (FR-017)."""
    import scripts.dep_coresolve as dc

    bodies: dict[str, str] = {}

    def fake_fetch(dist):
        if dist not in bodies:
            raise dc.InfraError(f"stub has no body for {dist}")
        return json.loads(bodies[dist])

    monkeypatch.setattr(dc, "_fetch_pypi_json", fake_fetch)

    def _set(dist, body):
        bodies[dist] = body

    yield _set


# --------------------------------------------------------------------------- #
# T003 [US1] Manifest loader + CONFIG classification.
# --------------------------------------------------------------------------- #


def test_valid_manifest_parses_into_typed_records(tmp_path):
    import scripts.dep_coresolve as dc

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = []\n'
        "[project.optional-dependencies]\ndev = []\ndbt = []\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "dependency-environments.yaml"
    manifest.write_text(
        "version: 1\n"
        "environments:\n"
        "  - id: root-dev\n"
        "    pyproject: pyproject.toml\n"
        "    extras: [dev]\n"
        "    local: true\n"
        '    path: "."\n'
        "cross_products:\n"
        "  - id: cp\n"
        "    combine: [root-dev]\n"
        "governed_pins:\n"
        "  - dist: dbt-core\n",
        encoding="utf-8",
    )

    loaded = dc.load_manifest(manifest)

    assert [e.id for e in loaded.environments] == ["root-dev"]
    env = loaded.environments[0]
    assert env.extras == ("dev",)
    assert env.local is True
    assert [cp.id for cp in loaded.cross_products] == ["cp"]
    assert loaded.cross_products[0].combine == ("root-dev",)
    assert [p.dist for p in loaded.governed_pins] == ["dbt-core"]


def test_manifest_missing_pyproject_is_config_outcome(tmp_path):
    import scripts.dep_coresolve as dc

    manifest = tmp_path / "dependency-environments.yaml"
    manifest.write_text(
        "version: 1\n"
        "environments:\n"
        "  - id: gone\n"
        "    pyproject: does-not-exist.toml\n"
        "    extras: [dev]\n"
        "    local: true\n"
        '    path: "."\n',
        encoding="utf-8",
    )

    loaded = dc.load_manifest(manifest)
    result = dc.resolve_environment(loaded, loaded.environments[0])

    assert result.outcome is dc.ResolveOutcome.CONFIG
    assert "does-not-exist.toml" in result.detail


def test_manifest_undefined_extra_is_config_outcome(tmp_path):
    import scripts.dep_coresolve as dc

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = []\n'
        "[project.optional-dependencies]\ndev = []\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "dependency-environments.yaml"
    manifest.write_text(
        "version: 1\n"
        "environments:\n"
        "  - id: bad\n"
        "    pyproject: pyproject.toml\n"
        "    extras: [nope]\n"
        "    local: true\n"
        '    path: "."\n',
        encoding="utf-8",
    )

    loaded = dc.load_manifest(manifest)
    result = dc.resolve_environment(loaded, loaded.environments[0])

    assert result.outcome is dc.ResolveOutcome.CONFIG
    assert "nope" in result.detail


# --------------------------------------------------------------------------- #
# T004 [US1] Local-path assembly (plan-review D1) + old-pip CONFIG (D5) +
# classification defaults (D2).
# --------------------------------------------------------------------------- #


def test_local_members_assemble_as_paths_never_dist_names(tmp_path):
    """plan-review D1: a repository-local member is assembled as a LOCAL PATH
    requirement, never by distribution name. The oracle sits on the assembled
    requirement strings themselves."""
    import scripts.dep_coresolve as dc

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "seshat-bi"\ndependencies = []\n'
        "[project.optional-dependencies]\ndbt = []\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "dependency-environments.yaml"
    manifest.write_text(
        "version: 1\n"
        "environments:\n"
        "  - id: root-dbt\n"
        "    pyproject: pyproject.toml\n"
        "    extras: [dbt]\n"
        "    local: true\n"
        '    path: "."\n',
        encoding="utf-8",
    )

    loaded = dc.load_manifest(manifest)
    reqs = dc.assemble_requirements(loaded, loaded.environments[0])

    joined = " ".join(reqs)
    # The assembled requirement is a local PATH carrying the extras...
    assert any(r.endswith("[dbt]") for r in reqs)
    assert any(("/" in r or r.startswith(".")) for r in reqs)
    # ...and the seshat-bi DISTRIBUTION NAME never appears as a requirement.
    assert "seshat-bi[dbt]" not in joined
    assert not any(r == "seshat-bi" or r.startswith("seshat-bi") for r in reqs)


def test_ambiguous_resolver_error_defaults_to_resolution(tmp_path):
    """plan-review D2: an unrecognized non-zero resolve fails CLOSED as
    RESOLUTION, never excused as INFRA."""
    import scripts.dep_coresolve as dc

    outcome = dc.classify_resolve(
        returncode=1,
        stderr="ERROR: some unexpected message the classifier does not recognize\n",
    )
    assert outcome is dc.ResolveOutcome.RESOLUTION


def test_explicit_network_signature_is_infra(tmp_path):
    """plan-review D2: INFRA only on an explicit, fixture-tested network
    signature."""
    import scripts.dep_coresolve as dc

    outcome = dc.classify_resolve(returncode=1, stderr=INFRA_STDERR)
    assert outcome is dc.ResolveOutcome.INFRA


def test_resolution_signature_is_resolution(tmp_path):
    import scripts.dep_coresolve as dc

    outcome = dc.classify_resolve(returncode=1, stderr=RESOLUTION_STDERR)
    assert outcome is dc.ResolveOutcome.RESOLUTION


def test_venv_pip_too_old_is_config(tmp_path):
    """plan-review D5: an ephemeral-venv pip too old for --report yields CONFIG,
    not a crash."""
    import scripts.dep_coresolve as dc

    assert dc.pip_supports_report("22.2") is True
    assert dc.pip_supports_report("22.1.2") is False
    assert dc.pip_supports_report("21.3") is False


# --------------------------------------------------------------------------- #
# T005 [US1] Redaction of a surfaced resolver error via the C2 shapes.
# --------------------------------------------------------------------------- #


def test_redaction_masks_credential_shaped_token():
    """FR-016: a resolver error carrying a C2 connection-string shape is masked
    before it is surfaced. Reuses the repo's C2 secret-shape posture."""
    import scripts.dep_coresolve as dc

    dirty = (
        "ERROR: Could not install from "
        "postgres://admin:s3cr3t@prod-host:5432/warehouse -- ResolutionImpossible"
    )
    cleaned = dc.redact(dirty)
    assert "s3cr3t" not in cleaned
    assert "postgres://admin:s3cr3t@" not in cleaned
    assert "[REDACTED]" in cleaned


def test_redaction_masks_digitalocean_endpoint():
    import scripts.dep_coresolve as dc

    dirty = "ERROR: host db-postgresql-fra1-12345.db.ondigitalocean.com refused"
    cleaned = dc.redact(dirty)
    assert "db.ondigitalocean.com" not in cleaned
    assert "[REDACTED]" in cleaned


def test_redaction_passes_clean_conflict_message_unchanged():
    """A clean resolver conflict (no secret shape) is passed through verbatim."""
    import scripts.dep_coresolve as dc

    assert dc.redact(RESOLUTION_STDERR) == RESOLUTION_STDERR


# --------------------------------------------------------------------------- #
# T007-T010 [US1] Per-environment resolve classification + cross-product union.
# --------------------------------------------------------------------------- #


def _one_env_manifest(tmp_path, extras=("dbt",)):
    """A one-local-environment manifest whose pyproject defines the extras."""
    opt = "\n".join(f"{x} = []" for x in extras)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "seshat-bi"\ndependencies = []\n'
        f"[project.optional-dependencies]\n{opt}\n",
        encoding="utf-8",
    )
    extras_yaml = ", ".join(extras)
    manifest = tmp_path / "dependency-environments.yaml"
    manifest.write_text(
        "version: 1\n"
        "environments:\n"
        "  - id: root-dbt\n"
        "    pyproject: pyproject.toml\n"
        f"    extras: [{extras_yaml}]\n"
        "    local: true\n"
        '    path: "."\n',
        encoding="utf-8",
    )
    return manifest


def test_resolution_impossible_classifies_and_redacts(stub_resolve, tmp_path):
    """FR-003: a stubbed ResolutionImpossible resolve -> RESOLUTION, capturing
    the (redacted) resolver text."""
    import scripts.dep_coresolve as dc

    stub_resolve(returncode=1, stdout="", stderr=RESOLUTION_STDERR)
    manifest = dc.load_manifest(_one_env_manifest(tmp_path))
    result = dc.resolve_environment(manifest, manifest.environments[0])

    assert result.outcome is dc.ResolveOutcome.RESOLUTION
    assert "ResolutionImpossible" in result.detail
    assert "dbt-core" in result.detail


def test_successful_dry_run_report_classifies_pass_no_local_install(
    stub_resolve, tmp_path
):
    """FR-002/SC-002: a stubbed successful --dry-run --report -> PASS, and the
    resolve NEVER installs into the current interpreter (the stubbed
    ephemeral-venv seam is the only path; no real subprocess runs)."""
    import scripts.dep_coresolve as dc

    stub_resolve(returncode=0, stdout=REPORT_PASS_JSON, stderr="")
    manifest = dc.load_manifest(_one_env_manifest(tmp_path))
    result = dc.resolve_environment(manifest, manifest.environments[0])

    assert result.outcome is dc.ResolveOutcome.PASS
    # The stub recorded exactly one resolve call routed through the venv seam;
    # nothing touched this interpreter's site-packages.
    assert len(stub_resolve.state["calls"]) == 1
    # The requirement handed to the resolve seam is the LOCAL PATH (D1).
    reqs = stub_resolve.state["calls"][0]
    assert any(r.endswith("[dbt]") for r in reqs)
    assert not any(r.startswith("seshat-bi") for r in reqs)


def test_network_failure_classifies_infra_distinct_exit(stub_resolve, tmp_path):
    """FR-004/SC-004: a stubbed network failure -> INFRA, with a distinct exit
    code from RESOLUTION."""
    import scripts.dep_coresolve as dc

    stub_resolve(returncode=1, stdout="", stderr=INFRA_STDERR)
    manifest = dc.load_manifest(_one_env_manifest(tmp_path))
    result = dc.resolve_environment(manifest, manifest.environments[0])

    assert result.outcome is dc.ResolveOutcome.INFRA
    assert dc.EXIT_INFRA != dc.EXIT_RESOLUTION


def test_cross_product_unions_members_and_resolves_as_one(stub_resolve, tmp_path):
    """FR-002/T010: a cross-product unions its members' requirement sets and
    resolves them together; the historical dbt-core vs dagster-dbt shape ->
    RESOLUTION."""
    import scripts.dep_coresolve as dc

    # Two local members: root (dbt extra) + orchestration.
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "seshat-bi"\ndependencies = []\n'
        "[project.optional-dependencies]\ndbt = []\n",
        encoding="utf-8",
    )
    orch = tmp_path / "orchestration" / "dagster"
    orch.mkdir(parents=True)
    (orch / "pyproject.toml").write_text(
        '[project]\nname = "tower-bi-orchestration"\ndependencies = []\n'
        "[project.optional-dependencies]\ndev = []\n",
        encoding="utf-8",
    )
    manifest_path = tmp_path / "dependency-environments.yaml"
    manifest_path.write_text(
        "version: 1\n"
        "environments:\n"
        "  - id: root-dbt\n"
        "    pyproject: pyproject.toml\n"
        "    extras: [dbt]\n"
        "    local: true\n"
        '    path: "."\n'
        "  - id: orchestration\n"
        "    pyproject: orchestration/dagster/pyproject.toml\n"
        "    extras: [dev]\n"
        "    local: true\n"
        '    path: "orchestration/dagster"\n'
        "cross_products:\n"
        "  - id: root-dbt-plus-orchestration\n"
        "    combine: [root-dbt, orchestration]\n",
        encoding="utf-8",
    )
    manifest = dc.load_manifest(manifest_path)

    # Assembly unions BOTH members' local-path requirements.
    reqs = dc.assemble_cross_product(manifest, manifest.cross_products[0])
    assert len(reqs) == 2
    assert any(r.endswith("[dbt]") for r in reqs)

    # The historical conflict resolves to RESOLUTION.
    stub_resolve(returncode=1, stdout="", stderr=RESOLUTION_STDERR)
    result = dc.resolve_cross_product(manifest, manifest.cross_products[0])
    assert result.outcome is dc.ResolveOutcome.RESOLUTION
    assert len(stub_resolve.state["calls"][0]) == 2


# --------------------------------------------------------------------------- #
# T013 [US1] The --check entry mode (fail-closed exit codes + PASS lines).
# --------------------------------------------------------------------------- #


def test_check_all_pass_exits_zero(stub_resolve, tmp_path, capsys):
    """FR-006: all environments resolve -> exit 0, one PASS line per env."""
    import scripts.dep_coresolve as dc

    stub_resolve(returncode=0, stdout=REPORT_PASS_JSON, stderr="")
    code = dc.run_check(_one_env_manifest(tmp_path))
    out = capsys.readouterr().out

    assert code == dc.EXIT_OK
    assert "PASS" in out
    assert "root-dbt" in out


def test_check_resolution_conflict_exits_nonzero_with_text(
    stub_resolve, tmp_path, capsys
):
    """FR-003: a RESOLUTION conflict -> non-zero exit, redacted resolver text
    printed naming the failing environment."""
    import scripts.dep_coresolve as dc

    stub_resolve(returncode=1, stdout="", stderr=RESOLUTION_STDERR)
    code = dc.run_check(_one_env_manifest(tmp_path))
    out = capsys.readouterr().out

    assert code == dc.EXIT_RESOLUTION
    assert "root-dbt" in out
    assert "ResolutionImpossible" in out


def test_check_infra_only_exits_distinct_infra_code(stub_resolve, tmp_path, capsys):
    """FR-004/SC-004: when ONLY INFRA occurred, exit with the distinct INFRA
    code, not the RESOLUTION code."""
    import scripts.dep_coresolve as dc

    stub_resolve(returncode=1, stdout="", stderr=INFRA_STDERR)
    code = dc.run_check(_one_env_manifest(tmp_path))

    assert code == dc.EXIT_INFRA


def test_check_config_error_exits_nonzero(tmp_path, capsys):
    """FR-005: a bad manifest entry (missing pyproject) -> non-zero exit."""
    import scripts.dep_coresolve as dc

    manifest = tmp_path / "dependency-environments.yaml"
    manifest.write_text(
        "version: 1\n"
        "environments:\n"
        "  - id: gone\n"
        "    pyproject: nope.toml\n"
        "    extras: [dev]\n"
        "    local: true\n"
        '    path: "."\n',
        encoding="utf-8",
    )
    code = dc.run_check(manifest)
    out = capsys.readouterr().out

    assert code == dc.EXIT_RESOLUTION
    assert "nope.toml" in out


def test_check_resolution_wins_over_infra(monkeypatch, tmp_path):
    """A real RESOLUTION anywhere fails closed even if an INFRA also occurred
    (a conflict is never excused by a co-occurring network blip)."""
    import scripts.dep_coresolve as dc

    # Two envs: first RESOLUTION, second INFRA.
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = []\n'
        "[project.optional-dependencies]\ndev = []\ndbt = []\n",
        encoding="utf-8",
    )
    manifest_path = tmp_path / "dependency-environments.yaml"
    manifest_path.write_text(
        "version: 1\n"
        "environments:\n"
        "  - id: a\n"
        "    pyproject: pyproject.toml\n"
        "    extras: [dev]\n"
        "    local: true\n"
        '    path: "."\n'
        "  - id: b\n"
        "    pyproject: pyproject.toml\n"
        "    extras: [dbt]\n"
        "    local: true\n"
        '    path: "."\n',
        encoding="utf-8",
    )

    # Program per-call stderr: first RESOLUTION, then INFRA.
    seq = [RESOLUTION_STDERR, INFRA_STDERR]

    def fake_run_resolve(requirements, report_path):
        stderr = seq.pop(0)
        return dc.ResolveRun(returncode=1, stdout="", stderr=stderr, report_json=None)

    monkeypatch.setattr(dc, "_run_resolve", fake_run_resolve)
    code = dc.run_check(manifest_path)
    assert code == dc.EXIT_RESOLUTION
