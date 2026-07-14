"""`retail pack` handler: scaffold + validate (spec 120, US5) and the public
extension-pack catalog's search/inspect/add (spec 128).

`scaffold` writes one new declarative pack skeleton at an explicit local
path. `validate` checks each named manifest and the cross-pack selection
graph, reporting every finding BEFORE any pack content could contribute to a
readiness output (FR-032). No global activation state exists: validating a
pack installs nothing.

`search` and `inspect` are read-only discovery over the reviewed static
registry (``packs/registry/index.yaml``); neither fetches or executes pack
content. `add` runs the full fail-closed fetch -> hash -> schema -> existing
pack validation chain and, only on all-pass, adds the verified pack as a
reviewable workspace change -- it creates no activation state and advances
no readiness stage (spec 128, US1-US3).

Exit codes (stable):
  scaffold  0 succeeded, 2 input defect
  validate  0 pass, 1 validation findings, 2 unreadable/schema-invalid manifest
  search    0 ran (matches may be empty), 2 unreadable/invalid registry
  inspect   0 found, 1 not found, 2 unreadable/invalid registry
  add       0 added, 1 refused on findings, 2 unreadable/invalid registry
"""

from __future__ import annotations

import argparse
import json


def _run_scaffold(args: argparse.Namespace) -> int:
    from seshat.packs.model import PackError, PackSpec
    from seshat.packs.scaffold import scaffold_pack

    spec = PackSpec(pack_id=args.pack_id, category=args.category, owner=args.owner)
    try:
        written = scaffold_pack(args.repo, spec, target_dir=args.dir)
    except PackError as exc:
        print(f"error: {exc}")
        return 2
    for path in written:
        print(f"written: {path}")
    print("next: fill in the starter content, then run the pack's verification.")
    return 0


def _validate_all(repo: str, manifest_paths: list[str]) -> tuple[list, list, bool]:
    from seshat.packs.validator import validate_pack, validate_selection

    manifests = []
    findings = []
    unreadable = False
    for manifest_path in manifest_paths:
        manifest, pack_findings = validate_pack(repo, manifest_path)
        findings.extend(pack_findings)
        if manifest is None:
            unreadable = True
        else:
            manifests.append(manifest)
    findings.extend(validate_selection(manifests))
    return manifests, findings, unreadable


def _print_validate_result(output_format: str, manifests: list, findings: list) -> None:
    if output_format == "json":
        print(
            json.dumps(
                {
                    "status": "blocked" if findings else "pass",
                    "packs": [manifest.pack_id for manifest in manifests],
                    "findings": findings,
                },
                indent=2,
            )
        )
        return
    for finding in findings:
        print(f"[{finding['rule']}] {finding['locator']}: {finding['message']}")
    label = ", ".join(m.pack_id for m in manifests) or "none readable"
    print(f"packs: {label}")
    print(f"result: {'blocked' if findings else 'pass'}")


def _run_validate(args: argparse.Namespace) -> int:
    manifests, findings, unreadable = _validate_all(args.repo, args.pack)
    _print_validate_result(args.output_format, manifests, findings)
    if unreadable:
        return 2
    return 1 if findings else 0


def _record_dict(record) -> dict:
    return {
        "id": record.id,
        "version": record.version,
        "category": record.category,
        "author": record.author,
        "compatibility": record.compatibility,
        "verification_state": record.verification_state,
    }


def _full_record_dict(record) -> dict:
    return {
        **_record_dict(record),
        "source": record.source,
        "hash": record.hash,
        "dependencies": list(record.dependencies),
        "conflicts": list(record.conflicts),
        "verification_evidence": list(record.verification_evidence),
    }


def _print_registry_findings_text(registry_findings) -> None:
    for finding in registry_findings:
        print(
            f"[registry defect] [{finding['rule']}] "
            f"{finding['locator']}: {finding['message']}"
        )


def _print_search_text(matches, registry_findings) -> None:
    if not matches:
        print("no matches")
    else:
        for record in matches:
            print(
                f"[{record.category}] {record.id} {record.version} "
                f"-- author: {record.author} -- compatibility: {record.compatibility} "
                f"-- verification: {record.verification_state}"
            )
        print(f"matches: {len(matches)}")
    _print_registry_findings_text(registry_findings)


def _run_search(args: argparse.Namespace) -> int:
    from seshat.packs.registry import RegistryError, load_registry, search

    try:
        registry = load_registry(args.repo, args.registry)
    except RegistryError as exc:
        print(f"error: {exc}")
        return 2
    matches = search(registry, keyword=args.query, category=args.category)
    if args.output_format == "json":
        print(
            json.dumps(
                {
                    "query": args.query,
                    "category": args.category,
                    "matches": [_record_dict(record) for record in matches],
                    # A schema-invalid or duplicate registry record is
                    # excluded from `matches` but never silently hidden --
                    # a caller must be able to see WHY the registry looks
                    # smaller/different than expected (RR-005/FR-020).
                    "registry_findings": list(registry.findings),
                },
                indent=2,
            )
        )
    else:
        _print_search_text(matches, registry.findings)
    return 0


def _print_inspect_text(record) -> None:
    print(f"id: {record.id}")
    print(f"version: {record.version}")
    print(f"category: {record.category}")
    print(f"author: {record.author}")
    print(f"source: {record.source}")
    print(f"compatibility: {record.compatibility}")
    print(f"hash: {record.hash}")
    print(f"dependencies: {', '.join(record.dependencies) or 'none'}")
    print(f"conflicts: {', '.join(record.conflicts) or 'none'}")
    print(f"verification_state: {record.verification_state}")
    for evidence in record.verification_evidence:
        print(f"verification_evidence: {evidence}")


def _run_inspect(args: argparse.Namespace) -> int:
    from seshat.packs.registry import RegistryError, inspect, load_registry

    try:
        registry = load_registry(args.repo, args.registry)
    except RegistryError as exc:
        print(f"error: {exc}")
        return 2
    record = inspect(registry, args.id)
    if record is None:
        if args.output_format == "json":
            print(
                json.dumps(
                    {
                        "status": "not_found",
                        "id": args.id,
                        # "Not found" could mean the id was never registered,
                        # OR that a matching record was excluded as a
                        # registry defect (schema-invalid, duplicate) -- both
                        # are surfaced, never conflated (RR-005/FR-020).
                        "registry_findings": list(registry.findings),
                    },
                    indent=2,
                )
            )
        else:
            print(f"not found: {args.id}")
            _print_registry_findings_text(registry.findings)
        return 1
    if args.output_format == "json":
        print(
            json.dumps(
                {
                    "status": "found",
                    **_full_record_dict(record),
                    "registry_findings": list(registry.findings),
                },
                indent=2,
            )
        )
    else:
        _print_inspect_text(record)
        _print_registry_findings_text(registry.findings)
    return 0


def _print_add_text(outcome) -> None:
    for path in outcome.written:
        print(f"written: {path}")
    for finding in outcome.findings:
        print(f"[{finding['rule']}] {finding['locator']}: {finding['message']}")
    print(f"pack: {outcome.pack_id}")
    if outcome.author is not None:
        print(f"author: {outcome.author}")
    if outcome.verification_state is not None:
        print(f"verification_state: {outcome.verification_state}")
    print(f"result: {outcome.status}")
    if outcome.added:
        print(
            "note: added content is inert until explicitly selected for a "
            "projection; no readiness stage advanced and no approval was granted."
        )


def _run_add(args: argparse.Namespace) -> int:
    from seshat.packs.catalog import add_pack
    from seshat.packs.registry import RegistryError, load_registry

    try:
        registry = load_registry(args.repo, args.registry)
    except RegistryError as exc:
        print(f"error: {exc}")
        return 2
    outcome = add_pack(args.repo, registry, args.id, dest=args.dest)
    if args.output_format == "json":
        print(
            json.dumps(
                {
                    "status": outcome.status,
                    "pack_id": outcome.pack_id,
                    "author": outcome.author,
                    "verification_state": outcome.verification_state,
                    "written": list(outcome.written),
                    "findings": list(outcome.findings),
                },
                indent=2,
            )
        )
    else:
        _print_add_text(outcome)
    return 0 if outcome.added else 1


def pack_main(args: argparse.Namespace) -> int:
    if args.pack_command == "scaffold":
        return _run_scaffold(args)
    if args.pack_command == "validate":
        return _run_validate(args)
    if args.pack_command == "search":
        return _run_search(args)
    if args.pack_command == "inspect":
        return _run_inspect(args)
    if args.pack_command == "add":
        return _run_add(args)
    raise AssertionError(f"unhandled pack subcommand: {args.pack_command!r}")
