"""Produce a credential-free, non-authorizing public release candidate audit."""

from __future__ import annotations

import argparse
import json
import subprocess
import tomllib
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

try:
    from scripts.check_release_versions import audit_versions
    from scripts.export_agent_bundles import ExportError, check_all
except ModuleNotFoundError:  # direct `python scripts/release_candidate_audit.py`
    from check_release_versions import audit_versions
    from export_agent_bundles import ExportError, check_all

REGISTRY_PATH = Path("skills/retail-kpi-knowledge/registry.yaml")
_CONTRADICTORY_HISTORY_PHRASES = (
    "there is no prior git tag",
    "no prior git tag exists",
)


def audit_registry(
    repo_root: Path, registry_document: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Check registry uniqueness, contract resolution, and KPI-MC-15 projection."""

    if registry_document is None:
        path = repo_root / REGISTRY_PATH
        if not path.is_file():
            return {
                "status": "fail",
                "blocking_reasons": [
                    f"required KPI registry is missing: {REGISTRY_PATH}"
                ],
            }
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, Mapping):
            return {
                "status": "fail",
                "blocking_reasons": ["KPI registry must be a YAML object"],
            }
        registry_document = loaded
    entries = registry_document.get("entries")
    if not isinstance(entries, list):
        return {
            "status": "fail",
            "blocking_reasons": ["KPI registry entries must be a list"],
        }
    ids: list[str] = []
    blockers: list[str] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            blockers.append(f"registry entry {index} is not an object")
            continue
        identifier = entry.get("id")
        if not isinstance(identifier, str):
            blockers.append(f"registry entry {index} has no string id")
            continue
        ids.append(identifier)
        contract = entry.get("knowledge_contract_ref")
        if not isinstance(contract, str) or not (repo_root / contract).is_file():
            blockers.append(
                f"registry {identifier} contract does not resolve: {contract!r}"
            )
    duplicates = sorted({identifier for identifier in ids if ids.count(identifier) > 1})
    if duplicates:
        blockers.append(f"duplicate KPI registry IDs: {duplicates}")
    kpi_count = ids.count("KPI-MC-15")
    if kpi_count != 1:
        blockers.append(f"KPI-MC-15 must resolve exactly once; observed {kpi_count}")
    return {
        "status": "fail" if blockers else "pass",
        "entry_count": len(entries),
        "kpi_mc_15_count": kpi_count,
        "blocking_reasons": sorted(blockers),
    }


def _audit_package(repo_root: Path) -> dict[str, Any]:
    pyproject_path = repo_root / "pyproject.toml"
    blockers: list[str] = []
    version: str | None = None
    if not pyproject_path.is_file():
        blockers.append("pyproject.toml is missing")
    else:
        document = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        project = document.get("project", {})
        version = project.get("version")
        if project.get("name") != "seshat-bi":
            blockers.append("Python project name must be seshat-bi")
        scripts = project.get("scripts", {})
        if scripts.get("seshat") != "seshat.cli:main":
            blockers.append("seshat console script must resolve to seshat.cli:main")
        if scripts.get("retail") != "seshat.cli:main":
            blockers.append("retail console script must resolve to seshat.cli:main")
    return {
        "status": "fail" if blockers else "pass",
        "version": version,
        "blocking_reasons": blockers,
    }


def _audit_history_docs(repo_root: Path) -> dict[str, Any]:
    blockers: list[str] = []
    for relative in ("CHANGELOG.md", "docs/releases/v0.1.md"):
        path = repo_root / relative
        if not path.is_file():
            blockers.append(f"release history document is missing: {relative}")
            continue
        lowered = path.read_text(encoding="utf-8").casefold()
        for phrase in _CONTRADICTORY_HISTORY_PHRASES:
            if phrase in lowered:
                blockers.append(
                    f"{relative} contradicts the existing v0.1.0 tag: {phrase!r}"
                )
    return {
        "status": "fail" if blockers else "pass",
        "blocking_reasons": blockers,
    }


def audit_candidate(
    repo_root: Path,
    *,
    allow_untracked_inputs: bool = False,
    known_immutable_package_versions: set[str] | None = None,
) -> dict[str, Any]:
    """Audit repository readiness and enumerate release blockers without a score."""

    repository_checks: dict[str, Any] = {
        "package": _audit_package(repo_root),
        "registry": audit_registry(repo_root),
        "history_docs": _audit_history_docs(repo_root),
    }
    try:
        check_all(repo_root, allow_untracked_inputs=allow_untracked_inputs)
        repository_checks["generated_bundles"] = {
            "status": "pass",
            "blocking_reasons": [],
        }
    except ExportError as exc:
        repository_checks["generated_bundles"] = {
            "status": "fail",
            "blocking_reasons": [str(exc)],
        }
    version_report = audit_versions(repo_root)
    repository_blockers = sorted(
        blocker
        for check in repository_checks.values()
        for blocker in check["blocking_reasons"]
    )
    release_blockers = list(version_report["blocking_reasons"])
    immutable = known_immutable_package_versions or set()
    version = str(version_report["candidate_version"])
    if version in immutable:
        release_blockers.append(
            f"immutable package version {version} already exists; "
            "select a new owner-approved version"
        )
    all_blockers = sorted(repository_blockers + release_blockers)
    candidate_id = f"candidate-{version}-{version_report['source_revision'][:12]}"
    artifact_digests: dict[str, str] = {}
    for platform, relative in (
        ("claude", "integrations/claude-code/seshat-bi/bundle-manifest.json"),
        ("codex", "integrations/codex/seshat-bi/bundle-manifest.json"),
    ):
        path = repo_root / relative
        if path.is_file():
            manifest = json.loads(path.read_text(encoding="utf-8"))
            digest = manifest.get("manifest_digest")
            if isinstance(digest, str):
                artifact_digests[f"{platform}-bundle-manifest"] = digest
    surface_status = {
        "schema_version": "1.0",
        "surfaces": {
            "python_pypi": {
                "status": "unverified",
                "reason": "no clean public PyPI install evidence is attached",
            },
            "claude_repository": {
                "status": "unverified",
                "reason": (
                    "no external public GitHub marketplace acceptance is attached"
                ),
            },
            "codex_repository": {
                "status": "unverified",
                "reason": "no external public Codex CLI and IDE acceptance is attached",
            },
            "claude_public_catalog": {
                "status": "unavailable",
                "reason": "no owner-approved public catalog submission was performed",
            },
            "openai_public_plugin": {
                "status": "unavailable",
                "reason": "no owner-approved OpenAI plugin submission was performed",
            },
        },
        "coordinated_release_status": "blocked" if all_blockers else "unverified",
        "summary": (
            "Repository candidate evidence only; public surfaces remain unverified."
        ),
    }
    report = {
        "schema_version": "1.0",
        "candidate_id": candidate_id,
        "candidate_version": version,
        "source_revision": version_report["source_revision"],
        "status": "blocked" if all_blockers else "validated",
        "repository_status": "fail" if repository_blockers else "pass",
        "repository_checks": repository_checks,
        "version_sync": version_report,
        "blocking_reasons": all_blockers,
        "artifact_digests": artifact_digests,
        "surface_availability": surface_status,
        "approval": None,
        "authority_disclaimer": (
            "This audit records evidence only; it grants no version, tag, publication, "
            "catalog, submission, or rollback approval."
        ),
    }
    report["evidence_manifest"] = {
        "schema_version": "1.0",
        "candidate_id": candidate_id,
        "version": version,
        "source_revision": version_report["source_revision"],
        "artifact_digests": artifact_digests,
        "repository_check_statuses": {
            name: check["status"] for name, check in repository_checks.items()
        },
        "surface_availability": surface_status,
        "publication_approval": None,
        "authority_disclaimer": (
            "Sanitized evidence only; no version, configuration, publication, "
            "submission, tag, release, or rollback action is approved."
        ),
    }
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repository-check", action="store_true")
    parser.add_argument("--require-release-ready", action="store_true")
    parser.add_argument("--allow-untracked-inputs", action="store_true")
    parser.add_argument(
        "--known-immutable-package-version", action="append", default=[]
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = audit_candidate(
            args.repo.resolve(),
            allow_untracked_inputs=args.allow_untracked_inputs,
            known_immutable_package_versions=set(args.known_immutable_package_version),
        )
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(
            json.dumps({"status": "blocked", "blocking_reasons": [str(exc)]}, indent=2)
        )
        return 1
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if args.repository_check and report["repository_status"] != "pass":
        return 1
    if args.require_release_ready and report["status"] != "validated":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
