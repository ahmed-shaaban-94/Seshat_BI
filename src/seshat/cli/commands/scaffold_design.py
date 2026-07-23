"""`seshat scaffold-design` handler (issues #440, #441): write the six
Stage-6/7 design + handoff blank templates into the workspace so a pip-only
user can produce Dashboard-Ready / Publish-Ready artifacts without the
development repository.

Lazy-imports ``seshat.design_scaffold`` (mirrors the other command handlers)
to keep the stdlib-only ``check`` core import chain unaffected (B1).
"""

from __future__ import annotations

import argparse
import sys


def scaffold_design_main(args: argparse.Namespace) -> int:
    """Materialize the Stage-6/7 design blanks; per-file non-destructive.

    Returns 0 on success (including an all-kept re-run), 1 if the bundled
    template data is missing or the destination is unsafe to write into.
    """
    from pathlib import Path

    from seshat import cli
    from seshat.design_scaffold import scaffold_design
    from seshat.safe_write import SafeWriteError

    prog = cli._prog(args)  # brand the client typed (`seshat`/`retail`), #402
    try:
        report = scaffold_design(Path(args.repo))
    except (FileNotFoundError, SafeWriteError) as exc:
        print(f"{prog} scaffold-design: [refused] {exc}", file=sys.stderr)
        return 1

    for rel in report.written:
        print(f"wrote {rel}")
    for rel in report.kept:
        print(f"kept {rel} (already present; not overwritten)")
    print(
        f"\nnext: fill the materialized templates under templates/ and "
        f"design/grids/ for the table's Dashboard-Ready / Publish-Ready "
        f"artifacts, then run `{prog} next`"
    )
    return 0
