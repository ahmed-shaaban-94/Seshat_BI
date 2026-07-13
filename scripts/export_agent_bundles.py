"""Deterministically export reviewed Seshat knowledge for Claude Code and Codex."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

import yaml

EXPORTER_VERSION = "1.0"
TARGET_ROOTS = {
    "claude": Path("integrations/claude-code/seshat-bi"),
    "codex": Path("integrations/codex/seshat-bi"),
}
CANONICAL_ROOTS = frozenset(
    {
        "skills/bi-sql-knowledge/SKILL.md",
        "skills/bi-dax-knowledge/SKILL.md",
        "skills/bi-python-knowledge/SKILL.md",
        "skills/bi-bigdata-knowledge/SKILL.md",
        "skills/retail-kpi-knowledge/SKILL.md",
    }
)
ALLOWED_MEDIA_TYPES = {
    "application/json",
    "application/yaml",
    "text/markdown",
    "text/plain",
}
ALLOWED_TRANSFORMS = {"copy-normalized-v1", "template-substitute-version-v1"}
_REFERENCE_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "credential-bearing URL": re.compile(
        r"\b[a-z][a-z0-9+.-]*://[^\s/:]+:[^\s/@]+@", re.IGNORECASE
    ),
    "Windows user path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\"),
    "macOS user path": re.compile(r"/Users/[^/\s]+/"),
    "client-confidential marker": re.compile(r"\bCLIENT[ _-]CONFIDENTIAL\b", re.I),
}


class ExportError(ValueError):
    """An allowlist or generated bundle violates the public export contract."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _normalize_text(data: bytes) -> bytes:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ExportError("allowlisted public files must be UTF-8 text") from exc
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"
    return normalized.encode("utf-8")


def _safe_relative_path(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ExportError(f"{label} must be a non-empty repository-relative path")
    if "\\" in value or any(char in value for char in "*?"):
        raise ExportError(f"{label} must be a literal POSIX path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ExportError(f"{label} escapes its allowed root: {value!r}")
    if path.parts and ":" in path.parts[0]:
        raise ExportError(f"{label} contains a drive prefix: {value!r}")
    return value


def _git_paths(repo_root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return {part.decode("utf-8") for part in result.stdout.split(b"\0") if part}


def _git_revision(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _project_version(repo_root: Path) -> str:
    document = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    return str(document["project"]["version"])


def load_allowlist(repo_root: Path, path: Path | None = None) -> dict[str, Any]:
    source = path or repo_root / "distribution" / "public-knowledge-allowlist.yaml"
    document = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ExportError("public knowledge allowlist must be a YAML object")
    return document


def _all_entries(document: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    entries: list[Mapping[str, Any]] = []
    for section in ("entries", "template_entries"):
        value = document.get(section)
        if not isinstance(value, list):
            raise ExportError(f"{section} must be a list")
        for entry in value:
            if not isinstance(entry, Mapping):
                raise ExportError(f"{section} entries must be objects")
            entries.append(entry)
    return entries


def validate_allowlist(
    repo_root: Path,
    document: Mapping[str, Any],
    *,
    tracked_paths: set[str] | None = None,
    allow_untracked_inputs: bool = False,
) -> list[Mapping[str, Any]]:
    """Validate and return the stable list of reviewed allowlist entries."""

    if document.get("schema_version") != 1:
        raise ExportError("allowlist schema_version must be 1")
    if document.get("canonical_repository") != "ahmed-shaaban-94/Seshat_BI":
        raise ExportError("allowlist canonical_repository is not Seshat_BI")
    roots = document.get("canonical_roots")
    if not isinstance(roots, list) or len(roots) != 5:
        raise ExportError("allowlist must declare the five canonical entrypoints")
    root_set = {_safe_relative_path(item, label="canonical root") for item in roots}
    if root_set != CANONICAL_ROOTS:
        raise ExportError("allowlist canonical_roots must match the five Seshat skills")
    tracked = tracked_paths if tracked_paths is not None else _git_paths(repo_root)
    entries = _all_entries(document)
    seen_ids: set[str] = set()
    seen_sources: set[str] = set()
    destinations: dict[str, set[str]] = {target: set() for target in TARGET_ROOTS}
    for entry in entries:
        entry_id = entry.get("entry_id", entry.get("template_id"))
        if not isinstance(entry_id, str) or not entry_id or entry_id in seen_ids:
            raise ExportError("every allowlist/template entry needs a unique stable ID")
        seen_ids.add(entry_id)
        source = _safe_relative_path(entry.get("source"), label=f"{entry_id} source")
        source_path = repo_root / Path(source)
        if source in seen_sources:
            raise ExportError(f"duplicate allowlisted source: {source}")
        seen_sources.add(source)
        if not source_path.exists() or not source_path.is_file():
            raise ExportError(f"allowlisted source is missing or not a file: {source}")
        cursor = repo_root
        source_has_symlink = False
        for part in PurePosixPath(source).parts:
            cursor /= part
            if cursor.is_symlink():
                source_has_symlink = True
                break
        if source_has_symlink:
            raise ExportError(f"allowlisted symlinks are prohibited: {source}")
        if source not in tracked and not allow_untracked_inputs:
            raise ExportError(f"allowlisted source is not tracked by Git: {source}")
        if entry.get("classification") not in {
            "generated_wrapper",
            "public_knowledge",
            "public_license",
        }:
            raise ExportError(f"{entry_id} has an unreviewed classification")
        if entry.get("media_type") not in ALLOWED_MEDIA_TYPES:
            raise ExportError(f"{entry_id} has a prohibited media type")
        if entry.get("transform") not in ALLOWED_TRANSFORMS:
            raise ExportError(f"{entry_id} has an unknown transform")
        if entry.get("required") is not True:
            raise ExportError(f"{entry_id} must explicitly be required")
        if (
            not isinstance(entry.get("review_reason"), str)
            or not str(entry.get("review_reason")).strip()
        ):
            raise ExportError(f"{entry_id} requires a public review reason")
        targets = entry.get("targets")
        if not isinstance(targets, Mapping) or not targets:
            raise ExportError(f"{entry_id} requires at least one target")
        for target, destination_value in targets.items():
            if target not in TARGET_ROOTS:
                raise ExportError(f"{entry_id} names unsupported target {target!r}")
            destination = _safe_relative_path(
                destination_value, label=f"{entry_id} {target} destination"
            )
            if destination in destinations[target]:
                raise ExportError(f"two sources collide at {target}/{destination}")
            destinations[target].add(destination)
    if not root_set.issubset(seen_sources):
        missing = sorted(root_set - seen_sources)
        raise ExportError(f"canonical entrypoints are not allowlisted: {missing}")
    return sorted(
        entries, key=lambda item: str(item.get("entry_id", item.get("template_id")))
    )


def _scan_public_content(source: str, data: bytes) -> None:
    text = data.decode("utf-8")
    for label, pattern in _SECRET_PATTERNS.items():
        if pattern.search(text):
            raise ExportError(f"{source} contains prohibited {label} content")


def _render_entry(
    repo_root: Path, entry: Mapping[str, Any], *, version: str
) -> tuple[bytes, str]:
    source = str(entry["source"])
    raw = (repo_root / Path(source)).read_bytes()
    normalized = _normalize_text(raw)
    _scan_public_content(source, normalized)
    transform = str(entry["transform"])
    if transform == "template-substitute-version-v1":
        normalized = normalized.replace(b"{{VERSION}}", version.encode("utf-8"))
        if b"{{" in normalized or b"}}" in normalized:
            raise ExportError(f"unresolved template marker in {source}")
    return normalized, _sha256(raw)


def _validate_links(bundle_root: Path) -> None:
    for path in bundle_root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for match in _REFERENCE_RE.finditer(text):
            reference = match.group(1).split("#", 1)[0].strip()
            if not reference or reference.startswith(
                ("#", "http://", "https://", "mailto:")
            ):
                continue
            if reference.startswith("/") or "\\" in reference:
                raise ExportError(f"unsafe Markdown reference in {path}: {reference}")
            resolved = (path.parent / reference).resolve()
            try:
                resolved.relative_to(bundle_root.resolve())
            except ValueError as exc:
                raise ExportError(
                    "Markdown reference escapes generated bundle in "
                    f"{path}: {reference}"
                ) from exc
            if not resolved.exists():
                raise ExportError(
                    f"unlisted or missing transitive reference in {path}: {reference}"
                )


def build_bundle(
    repo_root: Path,
    target: str,
    output_root: Path,
    *,
    source_revision: str | None = None,
    allow_untracked_inputs: bool = False,
) -> dict[str, Any]:
    """Build one target bundle and return its deterministic manifest."""

    if target not in TARGET_ROOTS:
        raise ExportError(f"unsupported target: {target}")
    document = load_allowlist(repo_root)
    entries = validate_allowlist(
        repo_root, document, allow_untracked_inputs=allow_untracked_inputs
    )
    version = _project_version(repo_root)
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)
    manifest_entries: list[dict[str, str]] = []
    for entry in entries:
        targets = entry["targets"]
        if target not in targets:
            continue
        destination = str(targets[target])
        data, source_digest = _render_entry(repo_root, entry, version=version)
        output = output_root / Path(destination)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        manifest_entries.append(
            {
                "classification": str(entry["classification"]),
                "destination": destination,
                "output_sha256": _sha256(data),
                "source": str(entry["source"]),
                "source_id": str(entry.get("entry_id", entry.get("template_id"))),
                "source_sha256": source_digest,
                "transform": str(entry["transform"]),
            }
        )
    _validate_links(output_root)
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "exporter_version": EXPORTER_VERSION,
        "target": target,
        "plugin": "seshat-bi",
        "version": version,
        "source_revision": source_revision or _git_revision(repo_root),
        "entries": sorted(manifest_entries, key=lambda item: item["destination"]),
    }
    payload["manifest_digest"] = _sha256(_canonical_json(payload))
    (output_root / "bundle-manifest.json").write_bytes(
        json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    )
    return payload


def _tree_bytes(root: Path) -> dict[str, bytes]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def compare_bundle_trees(
    expected_root: Path, actual_root: Path, *, target: str
) -> None:
    """Fail with stable details for missing, unexpected, or hand-edited files."""

    expected = _tree_bytes(expected_root)
    actual = _tree_bytes(actual_root)
    if expected == actual:
        return
    missing = sorted(set(expected) - set(actual))
    unexpected = sorted(set(actual) - set(expected))
    changed = sorted(
        path for path in set(expected) & set(actual) if expected[path] != actual[path]
    )
    raise ExportError(
        "generated bundle drift for "
        f"{target}: missing={missing}, unexpected={unexpected}, changed={changed}"
    )


def compare_shared_provenance(
    claude_manifest: Mapping[str, Any], codex_manifest: Mapping[str, Any]
) -> None:
    """Require identical canonical digests across both platform projections."""

    def canonical(manifest: Mapping[str, Any]) -> dict[str, tuple[str, str]]:
        result: dict[str, tuple[str, str]] = {}
        for entry in manifest.get("entries", []):
            if entry.get("classification") in {"public_knowledge", "public_license"}:
                result[str(entry["source"])] = (
                    str(entry["source_sha256"]),
                    str(entry["output_sha256"]),
                )
        return result

    if canonical(claude_manifest) != canonical(codex_manifest):
        raise ExportError("Claude and Codex canonical provenance differs")


def export_all(repo_root: Path, *, allow_untracked_inputs: bool = False) -> None:
    """Regenerate both committed platform bundles from reviewed inputs."""

    manifests: dict[str, Mapping[str, Any]] = {}
    for target, relative_root in TARGET_ROOTS.items():
        manifests[target] = build_bundle(
            repo_root,
            target,
            repo_root / relative_root,
            allow_untracked_inputs=allow_untracked_inputs,
        )
    compare_shared_provenance(manifests["claude"], manifests["codex"])


def check_all(repo_root: Path, *, allow_untracked_inputs: bool = False) -> None:
    """Fail if a clean regeneration differs from either committed bundle."""

    manifests: dict[str, Mapping[str, Any]] = {}
    with tempfile.TemporaryDirectory(prefix="seshat-bundle-check-") as temp:
        temp_root = Path(temp)
        for target, relative_root in TARGET_ROOTS.items():
            existing_root = repo_root / relative_root
            existing_manifest_path = existing_root / "bundle-manifest.json"
            source_revision = None
            if existing_manifest_path.exists():
                existing_manifest = json.loads(
                    existing_manifest_path.read_text(encoding="utf-8")
                )
                source_revision = existing_manifest.get("source_revision")
            generated_root = temp_root / target
            manifests[target] = build_bundle(
                repo_root,
                target,
                generated_root,
                source_revision=source_revision,
                allow_untracked_inputs=allow_untracked_inputs,
            )
            compare_bundle_trees(generated_root, existing_root, target=target)
        compare_shared_provenance(manifests["claude"], manifests["codex"])


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--allow-untracked-inputs",
        action="store_true",
        help="development-only: permit newly authored inputs before their first commit",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = args.repo.resolve()
    try:
        if args.check:
            check_all(repo_root, allow_untracked_inputs=args.allow_untracked_inputs)
        else:
            export_all(repo_root, allow_untracked_inputs=args.allow_untracked_inputs)
    except (ExportError, OSError, subprocess.CalledProcessError, KeyError) as exc:
        print(f"BLOCKED: {exc}")
        return 1
    print("PASS: generated Claude and Codex bundles match reviewed inputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
