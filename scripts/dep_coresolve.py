"""Governed dependency freshness and co-resolution (spec 136).

A plain script (NO new `seshat` CLI verb, ratified Option B). Two modes:

  * ``--check``     -- the fail-closed co-resolution gate. Resolves every
                       declared install environment and every declared
                       cross-product in an EPHEMERAL throwaway venv via
                       ``pip install --dry-run --report``; nothing is installed
                       into the caller's interpreter (SC-002). Exits non-zero on
                       any RESOLUTION or CONFIG outcome, printing the (redacted)
                       resolver text; exits with a DISTINCT code if only INFRA
                       occurred so a flaky network is never read as a conflict.
  * ``--freshness`` -- the advisory reporter. For each governed pin, reports the
                       latest STABLE version on PyPI and, when a newer stable
                       exists, PROPOSES a bump carrying a solve-proof. It changes
                       NO pin value and opens NO PR (FR-008/FR-012).

The declared environments live as committed DATA in ``dependency-environments.yaml``
(FR-001); this script hardcodes no pin list (FR-015).

Import boundary: this is a CI script, not part of the offline stdlib-only
``seshat check`` core, so it may import ``yaml`` and (for redaction) the repo's
C2 secret-shape regexes. It bootstraps ``<repo>/src`` onto ``sys.path`` so it
runs WITHOUT ``seshat`` being installed (the co-resolution CI job installs no
optional extra into its interpreter).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tomllib
import venv
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tempfile import mkdtemp
from urllib.error import URLError
from urllib.request import urlopen

# --- path bootstrap: reach the repo's src/ so redaction can reuse the C2 shapes
# without seshat being pip-installed (SC-002: nothing installed in the job
# interpreter). Computed from this file's location, not the cwd.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import yaml  # noqa: E402  (after the path bootstrap; a CI-script dep, not core)

# --------------------------------------------------------------------------- #
# Outcome model.
# --------------------------------------------------------------------------- #


class ResolveOutcome(Enum):
    """The classified result of one resolve attempt (spec Key Entities)."""

    PASS = "pass"
    RESOLUTION = "resolution"
    INFRA = "infra"
    CONFIG = "config"


# Distinct process exit codes so CI can tell the outcomes apart from the code
# alone (FR-004, SC-004).
EXIT_OK = 0
EXIT_RESOLUTION = 1  # a real conflict OR a bad manifest -- fail closed
EXIT_INFRA = 3  # network/index only -- distinct so a flake is not a conflict

# pip >= 22.2 introduced `--report` (plan-review D5).
_MIN_PIP_FOR_REPORT = (22, 2)


class InfraError(Exception):
    """Raised by the PyPI fetch seam on a network/index failure."""


# --------------------------------------------------------------------------- #
# Manifest records.
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Environment:
    id: str
    pyproject: str
    extras: tuple[str, ...]
    local: bool
    path: str | None


@dataclass(frozen=True)
class CrossProduct:
    id: str
    combine: tuple[str, ...]


@dataclass(frozen=True)
class GovernedPin:
    dist: str


@dataclass(frozen=True)
class Manifest:
    root: Path
    environments: tuple[Environment, ...]
    cross_products: tuple[CrossProduct, ...]
    governed_pins: tuple[GovernedPin, ...]

    def by_id(self, env_id: str) -> Environment | None:
        return next((e for e in self.environments if e.id == env_id), None)


@dataclass(frozen=True)
class ResolveResult:
    """One resolve attempt's classified outcome plus a (redacted) detail line."""

    target_id: str
    outcome: ResolveOutcome
    detail: str


@dataclass(frozen=True)
class ResolveRun:
    """The raw result of one `pip install --dry-run --report` subprocess."""

    returncode: int
    stdout: str
    stderr: str
    report_json: str | None


def load_manifest(path: Path) -> Manifest:
    """Parse the committed environments manifest into typed records (FR-001).

    Structural problems that are not resolvable per-environment (a non-mapping
    document) raise; a per-environment problem (missing pyproject, undefined
    extra) is deferred to ``resolve_environment`` so it classifies as CONFIG.
    """
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError(f"manifest is not a mapping: {path}")
    environments = tuple(
        Environment(
            id=str(e["id"]),
            pyproject=str(e["pyproject"]),
            extras=tuple(str(x) for x in (e.get("extras") or [])),
            local=bool(e.get("local", False)),
            path=(str(e["path"]) if e.get("path") is not None else None),
        )
        for e in (doc.get("environments") or [])
    )
    cross_products = tuple(
        CrossProduct(
            id=str(c["id"]),
            combine=tuple(str(m) for m in (c.get("combine") or [])),
        )
        for c in (doc.get("cross_products") or [])
    )
    governed_pins = tuple(
        GovernedPin(dist=str(p["dist"])) for p in (doc.get("governed_pins") or [])
    )
    return Manifest(
        root=path.resolve().parent,
        environments=environments,
        cross_products=cross_products,
        governed_pins=governed_pins,
    )


# --------------------------------------------------------------------------- #
# Requirement assembly (plan-review D1: local members as LOCAL PATHS).
# --------------------------------------------------------------------------- #


class ConfigError(Exception):
    """A manifest points at a missing pyproject or an undefined extra (FR-005)."""


def _read_pyproject_extras(project_path: Path) -> set[str]:
    data = tomllib.loads(project_path.read_text(encoding="utf-8"))
    optional = data.get("project", {}).get("optional-dependencies", {})
    return set(optional.keys())


def _assemble_member(manifest: Manifest, env: Environment) -> str:
    """Assemble ONE declared environment's install requirement.

    A repository-local project (``local: true``) is assembled as a LOCAL PATH
    requirement (``<path>[extras]``), NEVER by distribution name (plan-review
    D1) -- so the gate proves the PR's working tree resolves, not PyPI's
    published copy. The pyproject is read only to VALIDATE the declared extras
    exist (FR-005); the version pins are resolved by pip from that same tree.
    """
    project_path = manifest.root / env.pyproject
    if not project_path.is_file():
        raise ConfigError(
            f"environment {env.id!r}: pyproject not found: {env.pyproject}"
        )
    defined = _read_pyproject_extras(project_path)
    unknown = [x for x in env.extras if x not in defined]
    if unknown:
        raise ConfigError(
            f"environment {env.id!r}: undefined extra(s) {unknown} "
            f"(defined: {sorted(defined)})"
        )
    if not env.local or env.path is None:
        raise ConfigError(
            f"environment {env.id!r}: only repository-local projects are "
            "supported; mark 'local: true' with a 'path'"
        )
    local_dir = (manifest.root / env.path).resolve()
    extras_suffix = f"[{','.join(env.extras)}]" if env.extras else ""
    return f"{local_dir.as_posix()}{extras_suffix}"


def assemble_requirements(manifest: Manifest, env: Environment) -> list[str]:
    """Requirements for one declared environment (a single local-path member)."""
    return [_assemble_member(manifest, env)]


def assemble_cross_product(manifest: Manifest, cp: CrossProduct) -> list[str]:
    """Union the requirement sets of a cross-product's members (T012)."""
    reqs: list[str] = []
    for member_id in cp.combine:
        env = manifest.by_id(member_id)
        if env is None:
            raise ConfigError(f"cross-product {cp.id!r}: unknown member {member_id!r}")
        for req in assemble_requirements(manifest, env):
            if req not in reqs:
                reqs.append(req)
    return reqs


# --------------------------------------------------------------------------- #
# Classification (plan-review D2: default RESOLUTION; INFRA on signatures only).
# --------------------------------------------------------------------------- #

# Explicit, fixture-tested network signatures. INFRA is claimed ONLY on one of
# these; anything else on a non-zero exit defaults to RESOLUTION (fail-closed).
_INFRA_SIGNATURES = (
    "temporary failure in name resolution",
    "failed to establish a new connection",
    "network is unreachable",
    "connection broken by",
    "connection refused",
    "connection reset",
    "connection timed out",
    "read timed out",
    "max retries exceeded",
    "name or service not known",
    "proxyerror",
    "503 server error",
    "502 server error",
    "504 server error",
)


def classify_resolve(returncode: int, stderr: str) -> ResolveOutcome:
    """Classify a resolve subprocess result (FR-003/FR-004).

    Defaults to RESOLUTION on any non-zero exit (fail-closed, plan-review D2);
    returns INFRA only when stderr carries an explicit network signature.
    """
    if returncode == 0:
        return ResolveOutcome.PASS
    low = stderr.lower()
    if any(sig in low for sig in _INFRA_SIGNATURES):
        return ResolveOutcome.INFRA
    return ResolveOutcome.RESOLUTION


def pip_supports_report(version: str) -> bool:
    """True if a pip version string is >= 22.2 (supports --report; D5)."""
    parts: list[int] = []
    for token in version.split("."):
        digits = "".join(ch for ch in token if ch.isdigit())
        parts.append(int(digits) if digits else 0)
        if len(parts) == 2:
            break
    while len(parts) < 2:
        parts.append(0)
    return (parts[0], parts[1]) >= _MIN_PIP_FOR_REPORT


# --------------------------------------------------------------------------- #
# Redaction: reuse the repo's C2 connection-string shapes (FR-016).
# --------------------------------------------------------------------------- #

# The C2 DETECTION regexes live in seshat.rules.git_meta (they return findings,
# not masked text). We borrow pr_summary's masking POSTURE (iterate patterns,
# .sub a fixed token) but apply it over the C2 CONNECTION-STRING shapes -- not
# pr_summary's PII shapes, which by their own docstring do NOT cover a DSN URL.
from seshat.rules.git_meta import (  # noqa: E402
    CONN_URI_RE,
    DO_CLUSTER_SLUG_RE,
    DO_ENDPOINT_RE,
    MYSQL_URI_RE,
    ODBC_SECRET_RE,
)

_REDACT_TOKEN = "[REDACTED]"

# The URI/endpoint/ODBC/cluster-slug C2 shapes are safe to apply as a plain
# substitution. CONN_URI_RE / MYSQL_URI_RE match up to and including the `@`, so
# the credential (userinfo) is what gets masked; extend the URI masking a little
# past the `@` to also drop the host so a full DSN never survives.
_CONN_URI_FULL = re.compile(r"postgres(?:ql)?://[^\s]+")
_MYSQL_URI_FULL = re.compile(r"mysql://[^\s]+")


def redact(text: str) -> str:
    """Mask any C2 connection-string / secret shape in ``text`` before it is
    surfaced (FR-016). A clean conflict message is returned unchanged.

    Reuses the repository's C2 secret-shape posture: the same detection regexes
    ``seshat check``'s C2 rule uses, applied by substitution (mirroring the
    masking style in ``seshat.pr_summary.mask``). Idempotent -- the replacement
    token matches none of the shapes.
    """
    out = text
    # Full-DSN forms first (so the trailing host is dropped too, not just the
    # userinfo the bare C2 detection regex stops at).
    out = _CONN_URI_FULL.sub(_REDACT_TOKEN, out)
    out = _MYSQL_URI_FULL.sub(_REDACT_TOKEN, out)
    # Then the exact C2 detection shapes (belt-and-suspenders; also covers any
    # userinfo-only match the full forms missed).
    for pattern in (CONN_URI_RE, MYSQL_URI_RE, DO_ENDPOINT_RE, ODBC_SECRET_RE):
        out = pattern.sub(_REDACT_TOKEN, out)
    out = DO_CLUSTER_SLUG_RE.sub(_REDACT_TOKEN, out)
    return out


# --------------------------------------------------------------------------- #
# Ephemeral-venv resolve (implemented in Phase 3; the seam the stubs patch).
# --------------------------------------------------------------------------- #


def _venv_python(venv_dir: Path) -> Path:
    """The interpreter inside an ephemeral venv (cross-platform)."""
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _run_resolve(requirements: list[str], report_path: Path) -> ResolveRun:
    """Resolve ``requirements`` in a throwaway venv via ``pip install --dry-run
    --report`` -- WITHOUT installing anything into this interpreter (FR-002).

    This is the seam unit tests stub; it is exercised for real only by the live
    CI job and the local smoke.
    """
    venv_dir = Path(mkdtemp(prefix="dep_coresolve_"))
    try:
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        py = _venv_python(venv_dir)
        version = subprocess.run(
            [str(py), "-m", "pip", "--version"],
            capture_output=True,
            text=True,
        )
        pip_ver = version.stdout.split()[1] if version.stdout.split() else "0"
        if not pip_supports_report(pip_ver):
            return ResolveRun(
                returncode=2,
                stdout="",
                stderr=(
                    f"CONFIG: ephemeral venv pip {pip_ver} is older than "
                    "22.2 and does not support --report"
                ),
                report_json=None,
            )
        proc = subprocess.run(
            [
                str(py),
                "-m",
                "pip",
                "install",
                "--dry-run",
                "--report",
                str(report_path),
                *requirements,
            ],
            capture_output=True,
            text=True,
        )
        report_json = (
            report_path.read_text(encoding="utf-8")
            if proc.returncode == 0 and report_path.is_file()
            else None
        )
        return ResolveRun(
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            report_json=report_json,
        )
    finally:
        shutil.rmtree(venv_dir, ignore_errors=True)


def _resolve_reqs(target_id: str, requirements: list[str]) -> ResolveResult:
    """Run a resolve for an already-assembled requirement set and classify it."""
    report_path = Path(mkdtemp(prefix="dep_report_")) / "report.json"
    try:
        run = _run_resolve(requirements, report_path)
    finally:
        shutil.rmtree(report_path.parent, ignore_errors=True)
    # An explicit old-pip CONFIG signal from _run_resolve (D5).
    if run.returncode == 2 and run.stderr.startswith("CONFIG:"):
        return ResolveResult(target_id, ResolveOutcome.CONFIG, redact(run.stderr))
    outcome = classify_resolve(run.returncode, run.stderr)
    if outcome is ResolveOutcome.PASS:
        installed = _summarize_report(run.report_json)
        return ResolveResult(target_id, outcome, installed)
    return ResolveResult(target_id, outcome, redact(run.stderr.strip()))


def _summarize_report(report_json: str | None) -> str:
    if not report_json:
        return "resolved (empty install set)"
    try:
        doc = json.loads(report_json)
    except json.JSONDecodeError:
        return "resolved"
    names = [
        entry.get("metadata", {}).get("name", "?") for entry in doc.get("install", [])
    ]
    return f"resolved {len(names)} distribution(s)"


def resolve_environment(manifest: Manifest, env: Environment) -> ResolveResult:
    """Resolve one declared environment; a bad manifest entry -> CONFIG (FR-005)."""
    try:
        requirements = assemble_requirements(manifest, env)
    except ConfigError as exc:
        return ResolveResult(env.id, ResolveOutcome.CONFIG, str(exc))
    return _resolve_reqs(env.id, requirements)


def resolve_cross_product(manifest: Manifest, cp: CrossProduct) -> ResolveResult:
    """Resolve one declared cross-product (union of its members)."""
    try:
        requirements = assemble_cross_product(manifest, cp)
    except ConfigError as exc:
        return ResolveResult(cp.id, ResolveOutcome.CONFIG, str(exc))
    return _resolve_reqs(cp.id, requirements)


# --------------------------------------------------------------------------- #
# PyPI fetch seam (freshness; stubbed in unit tests).
# --------------------------------------------------------------------------- #

_PYPI_JSON_URL = "https://pypi.org/pypi/{dist}/json"


def _fetch_pypi_json(dist: str) -> dict:
    """Fetch the PyPI JSON API body for ``dist`` (network; stubbed in tests)."""
    url = _PYPI_JSON_URL.format(dist=dist)
    try:
        with urlopen(url, timeout=30) as resp:  # noqa: S310 (https literal)
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, OSError, json.JSONDecodeError) as exc:
        raise InfraError(f"PyPI fetch failed for {dist}: {exc}") from exc


def _print_result(result: ResolveResult) -> None:
    if result.outcome is ResolveOutcome.PASS:
        print(f"[PASS] {result.target_id}: {result.detail}")
    else:
        label = result.outcome.value.upper()
        print(f"[{label}] {result.target_id}: {result.detail}")


def _exit_code_for(results: list[ResolveResult]) -> int:
    """Fail closed: any RESOLUTION or CONFIG -> EXIT_RESOLUTION; else if any
    INFRA -> the distinct EXIT_INFRA; else EXIT_OK (FR-003/FR-004/SC-004)."""
    outcomes = {r.outcome for r in results}
    if ResolveOutcome.RESOLUTION in outcomes or ResolveOutcome.CONFIG in outcomes:
        return EXIT_RESOLUTION
    if ResolveOutcome.INFRA in outcomes:
        return EXIT_INFRA
    return EXIT_OK


def run_check(manifest_path: Path) -> int:
    """The fail-closed co-resolution gate (T013, FR-006).

    Loads the manifest, resolves every declared environment and cross-product
    in an ephemeral venv, prints one line per target, and returns a distinct
    exit code by the worst outcome seen (a real conflict is never masked by a
    co-occurring network blip).
    """
    manifest = load_manifest(manifest_path)
    results: list[ResolveResult] = []
    for env in manifest.environments:
        result = resolve_environment(manifest, env)
        results.append(result)
        _print_result(result)
    for cp in manifest.cross_products:
        result = resolve_cross_product(manifest, cp)
        results.append(result)
        _print_result(result)
    code = _exit_code_for(results)
    summary = (
        "ok"
        if code == EXIT_OK
        else "infra-only"
        if code == EXIT_INFRA
        else "conflict/config"
    )
    print(f"\n{len(results)} target(s) resolved; exit {code} ({summary})")
    return code


def run_freshness(manifest_path: Path, out: str | None) -> int:  # implemented in T022
    raise NotImplementedError


def _main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="run the gate")
    parser.add_argument("--freshness", action="store_true", help="run the reporter")
    parser.add_argument(
        "--manifest", default=str(_REPO_ROOT / "dependency-environments.yaml")
    )
    parser.add_argument("--out", default=None, help="freshness report output path")
    args = parser.parse_args(argv)
    if args.check:
        return run_check(Path(args.manifest))
    if args.freshness:
        return run_freshness(Path(args.manifest), args.out)
    parser.error("one of --check or --freshness is required")
    return EXIT_RESOLUTION


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main(sys.argv[1:]))
