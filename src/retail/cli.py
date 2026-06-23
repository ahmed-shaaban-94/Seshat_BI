from __future__ import annotations

import argparse
from pathlib import Path

from .registry import all_rules
from .runner import build_context, run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="retail")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="run static governance checks")
    check.add_argument("--repo", default=".", help="repo root to check")

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # argparse exits 2 on bad/missing args; surface it as a return code.
        return int(exc.code or 0)

    if args.command == "check":
        ctx = build_context(Path(args.repo))
        return run(all_rules(), ctx)

    return 0
