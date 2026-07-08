"""`retail next` handler for the run-next readiness surface."""

from __future__ import annotations

import argparse
import json


def _render_text(response: dict) -> str:
    lines = [
        f"table: {response['table']}",
        f"outcome: {response['outcome']}",
        f"stage: {response['stage']}",
    ]
    if response.get("action_text"):
        lines.append(f"action: {response['action_text']}")
    for reason in response.get("blocking_reasons", []):
        lines.append(f"blocking_reason: {reason}")
    if response.get("required_authority"):
        lines.append(f"required_authority: {response['required_authority']}")
    for caveat in response.get("caveats", []):
        lines.append(f"caveat: {caveat.get('kind')}: {caveat.get('detail')}")
    lines.append("read_only_proof: true")
    return "\n".join(lines)


def next_main(args: argparse.Namespace) -> int:
    from retail.run_next import build_run_next_response

    response = build_run_next_response(args.repo, args.table)
    if getattr(args, "output_format", "text") == "json":
        print(json.dumps(response, indent=2))
    else:
        print(_render_text(response))
    return 0
