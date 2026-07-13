"""Audit Seshat BI version projections without authorizing a release."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tomllib
from pathlib import Path
from typing import Any, Iterable, Mapping

_SEMVER = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)


class VersionAuditError(ValueError):
    """The version source itself is missing or invalid."""


def _json(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise VersionAuditError(f"{path} must contain a JSON object")
    return value


def _git_revision(repo_root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _tag_map(repo_root: Path) -> dict[str, str]:
    names = subprocess.run(
        ["git", "tag", "--list"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    revisions: dict[str, str] = {}
    for name in names:
        revision = subprocess.run(
            ["git", "rev-list", "-n", "1", name],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        revisions[name] = revision
    return revisions


def _projection(
    surface: str,
    path: str,
    observed: str | None,
    expected: str,
    *,
    status: str | None = None,
    blocker: str | None = None,
) -> dict[str, str | None]:
    resolved_status = status or ("pass" if observed == expected else "blocked")
    result: dict[str, str | None] = {
        "surface": surface,
        "path": path,
        "observed": observed,
        "expected": expected,
        "status": resolved_status,
    }
    if blocker:
        result["blocking_reason"] = blocker
    elif resolved_status == "blocked":
        result["blocking_reason"] = (
            f"{surface} version is {observed!r}; expected {expected!r}"
        )
    return result


def _json_version_projection(
    repo_root: Path,
    *,
    surface: str,
    relative_path: str,
    expected: str,
    value_path: tuple[object, ...],
    schema_optional: bool = False,
) -> dict[str, str | None]:
    path = repo_root / relative_path
    if not path.is_file():
        return _projection(
            surface,
            relative_path,
            None,
            expected,
            blocker=f"required governed version location is missing: {relative_path}",
        )
    try:
        value: object = _json(path)
        for key in value_path:
            if isinstance(key, int):
                if not isinstance(value, list):
                    raise KeyError(key)
                value = value[key]
            else:
                if not isinstance(value, Mapping):
                    raise KeyError(key)
                value = value[key]
    except (KeyError, IndexError, TypeError):
        if schema_optional:
            return _projection(
                surface,
                relative_path,
                None,
                expected,
                status="not_schema_supported",
            )
        return _projection(
            surface,
            relative_path,
            None,
            expected,
            blocker=f"governed version field is missing: {relative_path}",
        )
    return _projection(surface, relative_path, str(value), expected)


def audit_versions(
    repo_root: Path,
    *,
    source_revision: str | None = None,
    tags: Mapping[str, str] | None = None,
    github_release_tag: str | None = None,
) -> dict[str, Any]:
    """Return a deterministic, evidence-only version synchronization audit."""

    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.is_file():
        raise VersionAuditError("pyproject.toml is missing")
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    try:
        version = str(pyproject["project"]["version"])
    except KeyError as exc:
        raise VersionAuditError(
            "project.version is missing from pyproject.toml"
        ) from exc
    if _SEMVER.fullmatch(version) is None:
        raise VersionAuditError(f"project.version is not SemVer: {version!r}")
    revision = source_revision or _git_revision(repo_root)
    tag_map = dict(tags) if tags is not None else _tag_map(repo_root)
    projections: list[dict[str, str | None]] = [
        _projection("python_package", "pyproject.toml", version, version),
        _json_version_projection(
            repo_root,
            surface="claude_plugin",
            relative_path="integrations/claude-code/seshat-bi/.claude-plugin/plugin.json",
            expected=version,
            value_path=("version",),
        ),
        _json_version_projection(
            repo_root,
            surface="claude_marketplace",
            relative_path=".claude-plugin/marketplace.json",
            expected=version,
            value_path=("metadata", "version"),
        ),
        _json_version_projection(
            repo_root,
            surface="claude_bundle_manifest",
            relative_path="integrations/claude-code/seshat-bi/bundle-manifest.json",
            expected=version,
            value_path=("version",),
        ),
        _json_version_projection(
            repo_root,
            surface="codex_plugin",
            relative_path="integrations/codex/seshat-bi/.codex-plugin/plugin.json",
            expected=version,
            value_path=("version",),
        ),
        _json_version_projection(
            repo_root,
            surface="codex_catalog",
            relative_path=".agents/plugins/marketplace.json",
            expected=version,
            value_path=("plugins", 0, "version"),
            schema_optional=True,
        ),
        _json_version_projection(
            repo_root,
            surface="codex_bundle_manifest",
            relative_path="integrations/codex/seshat-bi/bundle-manifest.json",
            expected=version,
            value_path=("version",),
        ),
    ]
    changelog = repo_root / "CHANGELOG.md"
    changelog_match = False
    if changelog.is_file():
        changelog_match = (
            re.search(
                rf"^## \[{re.escape(version)}\](?:\s|$)",
                changelog.read_text(encoding="utf-8"),
                re.MULTILINE,
            )
            is not None
        )
    projections.append(
        _projection(
            "changelog",
            "CHANGELOG.md",
            version if changelog_match else None,
            version,
            blocker=None
            if changelog_match
            else f"CHANGELOG.md has no exact [{version}] release heading",
        )
    )
    major_minor = ".".join(version.split(".")[:2])
    note_path = f"docs/releases/v{major_minor}.md"
    release_note = repo_root / note_path
    note_match = False
    if release_note.is_file():
        note_match = (
            re.search(
                rf"^# .*\bv{re.escape(major_minor)}(?:\b|\.)",
                release_note.read_text(encoding="utf-8"),
                re.MULTILINE,
            )
            is not None
        )
    projections.append(
        _projection(
            "release_note",
            note_path,
            major_minor if note_match else None,
            major_minor,
            blocker=None
            if note_match
            else (
                f"release note is missing or has no v{major_minor} heading: {note_path}"
            ),
        )
    )
    tag = f"v{version}"
    tagged_revision = tag_map.get(tag)
    if tagged_revision is None:
        projections.append(
            _projection(
                "git_tag",
                tag,
                None,
                revision,
                status="pending_owner_action",
            )
        )
    else:
        projections.append(
            _projection(
                "git_tag",
                tag,
                tagged_revision,
                revision,
                blocker=None
                if tagged_revision == revision
                else (
                    f"existing immutable tag {tag} points to {tagged_revision}, "
                    f"not {revision}"
                ),
            )
        )
    projections.append(
        _projection(
            "github_release",
            tag,
            github_release_tag,
            tag,
            status="pending_owner_action" if github_release_tag is None else None,
        )
    )
    projections.sort(key=lambda item: (str(item["surface"]), str(item["path"])))
    blockers = sorted(
        str(item["blocking_reason"])
        for item in projections
        if item["status"] == "blocked"
    )
    return {
        "status": "blocked" if blockers else "pass",
        "candidate_version": version,
        "source_revision": revision,
        "projections": projections,
        "blocking_reasons": blockers,
        "authority_disclaimer": (
            "Version synchronization evidence does not authorize tagging or "
            "publication."
        ),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero when any governed projection is blocked",
    )
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = audit_versions(args.repo.resolve())
    except (
        VersionAuditError,
        OSError,
        ValueError,
        subprocess.CalledProcessError,
    ) as exc:
        print(
            json.dumps({"status": "blocked", "blocking_reasons": [str(exc)]}, indent=2)
        )
        return 1
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1 if args.check and report["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
