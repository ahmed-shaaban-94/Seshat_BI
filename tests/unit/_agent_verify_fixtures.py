"""Shared synthetic-fixture helpers for the `seshat agent verify` check tests
(spec 129), split across ``test_agent_verify_*.py`` by responsibility so each
module stays small and single-purpose.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

from seshat.agent_verify import checks
from seshat.agent_verify.model import VerifyTargetSpec
from seshat.agent_verify.targets import marketplace_path_for

REPO = Path(__file__).parents[2]

INTACT_CONTRACT = "\n".join(
    ["Hard stops:", ""] + [line for _, line in checks.GOVERNANCE_HARD_STOP_LINES]
)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def target_spec(
    tmp_path: Path, *, name: str = "claude", ide_surface: bool = False
) -> VerifyTargetSpec:
    manifest_rel = (
        f"integrations/{name}/seshat-bi/.claude-plugin/plugin.json"
        if name == "claude"
        else f"integrations/{name}/seshat-bi/.codex-plugin/plugin.json"
    )
    provenance_rel = f"integrations/{name}/seshat-bi/bundle-manifest.json"
    contract_rel = f"integrations/{name}/seshat-bi/portable-operating-contract.md"
    return VerifyTargetSpec(
        name=name,
        manifest_path=manifest_rel,
        provenance_manifest=provenance_rel,
        version_source=f"{name}_plugin",
        footprint_source=provenance_rel,
        operating_contract=contract_rel,
        ide_surface=ide_surface,
    )


def bundle_source(spec: VerifyTargetSpec) -> str:
    bundle_dir = PurePosixPath(spec.manifest_path).parent.parent
    return f"./{bundle_dir.as_posix()}"


def write_install_fixture(tmp_path: Path, spec: VerifyTargetSpec) -> None:
    write_json(tmp_path / spec.manifest_path, {"name": "seshat-bi", "version": "0.2.0"})
    marketplace_rel = marketplace_path_for(spec.name)
    write_json(
        tmp_path / marketplace_rel,
        {"plugins": [{"name": "seshat-bi", "source": bundle_source(spec)}]},
    )
    write_json(
        tmp_path / spec.provenance_manifest,
        {"target": spec.name, "plugin": "seshat-bi", "entries": []},
    )


def write_bundle_with_manifest(tmp_path: Path, spec: VerifyTargetSpec) -> Path:
    bundle_root = (tmp_path / spec.provenance_manifest).parent
    file_a = bundle_root / "commands" / "seshat-check.md"
    file_a.parent.mkdir(parents=True, exist_ok=True)
    file_a.write_bytes(b"check command content\n")
    file_b = bundle_root / "README.md"
    file_b.write_bytes(b"readme content\n")
    manifest = {
        "entries": [
            {
                "destination": "commands/seshat-check.md",
                "output_sha256": sha(file_a.read_bytes()),
            },
            {"destination": "README.md", "output_sha256": sha(file_b.read_bytes())},
        ]
    }
    write_json(tmp_path / spec.provenance_manifest, manifest)
    return bundle_root
