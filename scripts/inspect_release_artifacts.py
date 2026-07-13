"""Strictly inspect Seshat BI wheel/sdist artifacts and rebuild from the sdist."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from email import message_from_bytes
from email.message import Message
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

_PROHIBITED_TOP_LEVEL = {
    ".github",
    ".specify",
    "integrations",
    "specs",
    "tests",
}
_PROHIBITED_PATH_PARTS = {
    ".coverage",
    ".env",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}
_FORBIDDEN_MANDATORY_DEPS = {
    "build",
    "mysql-connector-python",
    "openpyxl",
    "playwright",
    "psycopg2-binary",
    "pyodbc",
    "pytest",
    "ruff",
    "snowflake-connector-python",
    "testcontainers",
    "twine",
}
_CONTENT_PATTERNS = {
    "private key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "credential-bearing URL": re.compile(
        rb"\b[a-z][a-z0-9+.-]*://[^\s/:]+:[^\s/@]+@", re.IGNORECASE
    ),
    "Windows user path": re.compile(rb"[A-Za-z]:\\Users\\[^\\\s]+\\"),
    "macOS user path": re.compile(rb"/Users/[^/\s]+/"),
    "client-confidential marker": re.compile(rb"\bCLIENT[ _-]CONFIDENTIAL\b", re.I),
}


class ArtifactInspectionError(ValueError):
    """A release artifact is incomplete, unsafe, or inconsistent."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_archive_path(name: str) -> PurePosixPath:
    if "\\" in name:
        raise ArtifactInspectionError(f"archive path is not POSIX: {name}")
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ArtifactInspectionError(f"archive path escapes its root: {name}")
    return path


def scan_content(name: str, data: bytes) -> None:
    """Reject strong secret, client, credential, and machine-path markers."""

    lowered_parts = {part.casefold() for part in _safe_archive_path(name).parts}
    if lowered_parts & _PROHIBITED_PATH_PARTS:
        raise ArtifactInspectionError(f"prohibited archive path: {name}")
    for label, pattern in _CONTENT_PATTERNS.items():
        if pattern.search(data):
            raise ArtifactInspectionError(f"{name} contains prohibited {label}")


def validate_wheel_inventory(names: Iterable[str]) -> None:
    paths = [_safe_archive_path(name) for name in names]
    if not any(path.parts and path.parts[0] == "seshat" for path in paths):
        raise ArtifactInspectionError("wheel is missing the seshat package")
    if not any(path.parts and path.parts[0] == "retail" for path in paths):
        raise ArtifactInspectionError(
            "wheel is missing the retail compatibility package"
        )
    if any(path.parts and path.parts[0] in _PROHIBITED_TOP_LEVEL for path in paths):
        raise ArtifactInspectionError(
            "wheel contains a development-only top-level path"
        )
    if not any(name.endswith(".dist-info/entry_points.txt") for name in names):
        raise ArtifactInspectionError("wheel is missing console entry-point metadata")
    if not any(".dist-info/licenses/LICENSE" in name for name in names):
        raise ArtifactInspectionError("wheel is missing the Apache-2.0 license file")


def validate_sdist_inventory(names: Iterable[str]) -> None:
    paths = [_safe_archive_path(name) for name in names]
    stripped = [PurePosixPath(*path.parts[1:]) for path in paths if len(path.parts) > 1]
    required = {"LICENSE", "README.md", "pyproject.toml"}
    observed = {path.as_posix() for path in stripped}
    missing = sorted(required - observed)
    if missing:
        raise ArtifactInspectionError(f"sdist is missing required files: {missing}")
    for package in ("src/seshat", "src/retail"):
        if not any(path.as_posix().startswith(package + "/") for path in stripped):
            raise ArtifactInspectionError(f"sdist is missing {package}")
    allowed_test_resource = "tests/fixtures/demo/demo_sample_orders.csv"
    for path in stripped:
        if not path.parts:
            continue
        if path.parts[0] == "tests" and path.as_posix() == allowed_test_resource:
            continue
        if path.parts[0] in _PROHIBITED_TOP_LEVEL:
            raise ArtifactInspectionError(
                "sdist contains unrelated development/publication files"
            )


def _metadata_values(message: Message) -> dict[str, Any]:
    return {
        "name": message.get("Name"),
        "version": message.get("Version"),
        "summary": message.get("Summary"),
        "requires_python": message.get("Requires-Python"),
        "license_expression": message.get("License-Expression")
        or message.get("License"),
        "description_content_type": message.get("Description-Content-Type"),
        "requires_dist": sorted(message.get_all("Requires-Dist", [])),
        "project_urls": sorted(message.get_all("Project-URL", [])),
    }


def _validate_metadata(metadata: dict[str, Any]) -> None:
    expected = {
        "name": "seshat-bi",
        "license_expression": "Apache-2.0",
        "description_content_type": "text/markdown",
    }
    for field, value in expected.items():
        if str(metadata.get(field)).casefold() != value.casefold():
            raise ArtifactInspectionError(
                f"metadata {field} is {metadata.get(field)!r}; expected {value!r}"
            )
    for field in ("version", "summary", "requires_python"):
        if not metadata.get(field):
            raise ArtifactInspectionError(f"metadata field is missing: {field}")
    urls = "\n".join(metadata["project_urls"])
    for label in ("Changelog", "Documentation", "Homepage", "Issues", "Repository"):
        if f"{label}, " not in urls:
            raise ArtifactInspectionError(f"metadata is missing project URL: {label}")
    mandatory = []
    for requirement in metadata["requires_dist"]:
        if "extra ==" not in requirement and "extra ==" not in requirement.casefold():
            mandatory.append(
                re.split(r"[ <>=;\[]", requirement, maxsplit=1)[0].casefold()
            )
    forbidden = sorted(set(mandatory) & _FORBIDDEN_MANDATORY_DEPS)
    if forbidden:
        raise ArtifactInspectionError(
            f"optional/development dependencies became mandatory: {forbidden}"
        )
    if "pyyaml" not in mandatory:
        raise ArtifactInspectionError(
            "wheel metadata is missing the PyYAML runtime dependency"
        )


def _read_wheel(path: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        files: dict[str, bytes] = {}
        for info in archive.infolist():
            if info.is_dir():
                continue
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise ArtifactInspectionError(
                    f"wheel contains a symlink: {info.filename}"
                )
            data = archive.read(info)
            scan_content(info.filename, data)
            files[info.filename] = data
    validate_wheel_inventory(files)
    metadata_names = [name for name in files if name.endswith(".dist-info/METADATA")]
    if len(metadata_names) != 1:
        raise ArtifactInspectionError("wheel must contain exactly one METADATA file")
    metadata = _metadata_values(message_from_bytes(files[metadata_names[0]]))
    _validate_metadata(metadata)
    entry_points = next(
        data.decode("utf-8")
        for name, data in files.items()
        if name.endswith(".dist-info/entry_points.txt")
    )
    for command in ("retail = seshat.cli:main", "seshat = seshat.cli:main"):
        if command not in entry_points:
            raise ArtifactInspectionError(f"wheel entry points are missing {command!r}")
    return files, metadata


def _read_sdist(path: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    with tarfile.open(path, "r:gz") as archive:
        files: dict[str, bytes] = {}
        for member in archive.getmembers():
            _safe_archive_path(member.name)
            if member.issym() or member.islnk():
                raise ArtifactInspectionError(f"sdist contains a link: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise ArtifactInspectionError(
                    f"sdist contains a special file: {member.name}"
                )
            extracted = archive.extractfile(member)
            if extracted is None:
                raise ArtifactInspectionError(
                    f"cannot read sdist member: {member.name}"
                )
            data = extracted.read()
            scan_content(member.name, data)
            files[member.name] = data
    validate_sdist_inventory(files)
    metadata_names = [name for name in files if name.endswith("/PKG-INFO")]
    if len(metadata_names) != 1:
        raise ArtifactInspectionError("sdist must contain exactly one root PKG-INFO")
    metadata = _metadata_values(message_from_bytes(files[metadata_names[0]]))
    _validate_metadata(metadata)
    return files, metadata


def _compare_normalized_wheels(original: Path, rebuilt: Path) -> None:
    first, first_metadata = _read_wheel(original)
    second, second_metadata = _read_wheel(rebuilt)
    if first_metadata != second_metadata:
        raise ArtifactInspectionError("rebuilt wheel metadata differs from original")

    def normalized(files: dict[str, bytes]) -> dict[str, bytes]:
        return {
            name: data
            for name, data in files.items()
            if not name.endswith((".dist-info/RECORD", ".dist-info/WHEEL"))
        }

    if normalized(first) != normalized(second):
        raise ArtifactInspectionError(
            "rebuilt wheel governed contents differ from original"
        )


def inspect_release_artifacts(
    dist_dir: Path,
    *,
    run_twine: bool = True,
    rebuild_sdist: bool = True,
) -> dict[str, Any]:
    """Inspect exactly one wheel and sdist, returning sanitized evidence."""

    wheels = sorted(dist_dir.glob("*.whl"))
    sdists = sorted(dist_dir.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise ArtifactInspectionError("expected exactly one wheel and one sdist")
    wheel, sdist = wheels[0], sdists[0]
    if run_twine:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "twine",
                "check",
                "--strict",
                str(wheel),
                str(sdist),
            ],
            check=True,
        )
    _, wheel_metadata = _read_wheel(wheel)
    _, sdist_metadata = _read_sdist(sdist)
    if wheel_metadata != sdist_metadata:
        raise ArtifactInspectionError("wheel and sdist core metadata differ")
    rebuild_status = "not_requested"
    if rebuild_sdist:
        with tempfile.TemporaryDirectory(prefix="seshat-sdist-rebuild-") as temp:
            rebuilt_dir = Path(temp)
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "build",
                    "--wheel",
                    "--outdir",
                    str(rebuilt_dir),
                    str(sdist),
                ],
                check=True,
            )
            rebuilt = sorted(rebuilt_dir.glob("*.whl"))
            if len(rebuilt) != 1:
                raise ArtifactInspectionError(
                    "sdist rebuild did not produce exactly one wheel"
                )
            _compare_normalized_wheels(wheel, rebuilt[0])
            rebuild_status = "pass"
    return {
        "schema_version": "1.0",
        "status": "pass",
        "version": wheel_metadata["version"],
        "artifacts": [
            {"filename": wheel.name, "sha256": _sha256(wheel), "kind": "wheel"},
            {"filename": sdist.name, "sha256": _sha256(sdist), "kind": "sdist"},
        ],
        "twine_strict": "pass" if run_twine else "not_requested",
        "isolated_sdist_rebuild": rebuild_status,
        "authority_disclaimer": "Artifact validation does not authorize publication.",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, default=Path("dist"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--skip-twine", action="store_true")
    parser.add_argument("--skip-rebuild", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = inspect_release_artifacts(
            args.dist,
            run_twine=not args.skip_twine,
            rebuild_sdist=not args.skip_rebuild,
        )
    except (ArtifactInspectionError, OSError, subprocess.CalledProcessError) as exc:
        print(
            json.dumps({"status": "blocked", "blocking_reasons": [str(exc)]}, indent=2)
        )
        return 1
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
