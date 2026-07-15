"""Thin read-only surface for the offline decision-change impact projection.

The command writes only disclosure-safe review artifacts under the contained
local output root. It never mutates governed state and emits no impact score.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def _print_disclosure_block(disclosure: dict[str, object]) -> None:
    print("error: impact-map output is blocked by disclosure findings:")
    for finding in disclosure["findings"]:
        print(f"  [{finding['rule']}] {finding['locator']}: {finding['message']}")


def impact_map_main(args: argparse.Namespace) -> int:
    from seshat.cli.guards import resolve_local_output
    from seshat.disclosure import scan_disclosure
    from seshat.impact_map import (
        build_impact_map,
        render_impact_map,
        serialize_impact_map,
    )

    root = Path(args.repo).resolve()
    projection = build_impact_map(root, args.decision, preview=args.preview)
    blocking = projection["blocking_condition"]
    if blocking is not None:
        print(f"error: [{blocking['kind']}] {blocking['detail']}")
        return 1

    disclosure = scan_disclosure(projection)
    if disclosure["status"] != "pass":
        _print_disclosure_block(disclosure)
        return 1

    machine = serialize_impact_map(projection)
    human = render_impact_map(projection)
    human_disclosure = scan_disclosure(human)
    if human_disclosure["status"] != "pass":
        _print_disclosure_block(human_disclosure)
        return 1

    try:
        machine_target = resolve_local_output(root, args.output)
        human_target = resolve_local_output(root, args.human_output)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    machine_target.parent.mkdir(parents=True, exist_ok=True)
    human_target.parent.mkdir(parents=True, exist_ok=True)
    machine_target.write_text(machine, encoding="utf-8")
    human_target.write_text(human, encoding="utf-8")
    print(f"written_machine: {machine_target.relative_to(root).as_posix()}")
    print(f"written_human: {human_target.relative_to(root).as_posix()}")
    print("The impact map is read-only and grants no approval.")
    return 0
