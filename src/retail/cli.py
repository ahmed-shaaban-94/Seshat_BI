from __future__ import annotations

import argparse
import sys
from pathlib import Path

import retail.rules  # noqa: F401  (import for side effects: fires every @register)

from .registry import all_rules
from .runner import build_context, run


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Exposed (not inlined in ``main``) so flag->field mapping is unit-testable
    without executing any rules. The two commit-aware flags live UNDER the
    ``check`` subcommand alongside ``--repo``.
    """
    parser = argparse.ArgumentParser(
        prog="retail",
        description="Static governance checks for committed Power BI artifacts.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="run static governance checks")
    check.add_argument("--repo", default=".", help="repo root to check")
    check.add_argument(
        "--commit-range",
        dest="commit_range",
        default=None,
        metavar="ORIGIN..HEAD",
        help="CI mode: git commit range to scope commit-aware rules (P2).",
    )
    check.add_argument(
        "--commit-msg-file",
        dest="commit_msg_file",
        default=None,
        metavar="PATH",
        help="commit-msg-hook mode: file holding the incoming commit message (P2).",
    )

    # LIVE validators (feature 004). Needs a running DB + the optional `db` extra
    # (psycopg2). The driver is imported LAZILY in _run_validate, never here, so
    # `retail check` and CI (no driver installed) never import it.
    # Connection is host-agnostic: ANY Postgres (local / remote / DigitalOcean /
    # other) via a DSN -- from --dsn, or DATABASE_URL, or the ANALYTICS_DB_* parts.
    validate = sub.add_parser(
        "validate",
        help="run LIVE data checks against any Postgres DB (needs the 'db' extra)",
    )
    validate.add_argument(
        "--dsn",
        default=None,
        metavar="postgresql://...",
        help=(
            "Postgres connection string. Overrides env. If omitted, DATABASE_URL "
            "or the ANALYTICS_DB_* env vars are used. NEVER commit a real DSN."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _build_parser().parse_args(argv)
    except SystemExit as exc:
        # argparse exits 2 on bad/missing args (e.g. no subcommand); surface it
        # as a return code rather than letting it propagate.
        return int(exc.code or 0)

    if args.command == "check":
        commit_message: str | None = None
        if args.commit_msg_file is not None:
            try:
                raw = Path(args.commit_msg_file).read_text(encoding="utf-8")
            except FileNotFoundError:
                print(
                    f"error: commit message file not found: {args.commit_msg_file}",
                    file=sys.stderr,
                )
                sys.exit(1)
            # git's COMMIT_EDITMSG ends in a trailing newline (\r\n on Windows) —
            # strip it so the message passed to rules is the bare text.
            commit_message = raw.rstrip("\r\n")

        ctx = build_context(
            Path(args.repo),
            commit_range=args.commit_range,
            commit_message=commit_message,
        )
        return run(all_rules(), ctx)

    if args.command == "validate":
        return _run_validate(args)

    return 0


def _run_validate(args) -> int:
    """Run the LIVE validators against a real DB.

    The psycopg2 import is LAZY (here, not at module scope) so that `retail
    check` and CI -- which install no DB driver -- never import it. If the driver
    or a usable connection is missing, exit non-zero with an actionable message,
    never a raw traceback.

    Connection is host-agnostic (any Postgres: local / remote / DigitalOcean /
    other) via a DSN resolved from --dsn or env (DATABASE_URL / ANALYTICS_DB_*).

    NOTE (feature 004 scope): the surface is built and fixture-tested; the actual
    live run against a database (target wiring from source-map.yaml + executing
    the checks) is the deferred follow-up. This handler resolves the DSN, enforces
    the lazy-driver + clear-error contract, and reports the deferred state -- it
    does not yet execute checks against a live DB.
    """
    import os

    from .validate import resolve_dsn

    # 1. Resolve a DSN (host-agnostic). --dsn wins; else env. No DSN -> clear error.
    env = dict(os.environ)
    if args.dsn:
        env = {**env, "DATABASE_URL": args.dsn}
    dsn = resolve_dsn(env)
    if dsn is None:
        print(
            "error: no database connection configured.\n"
            "       pass --dsn (a postgresql:// connection string), or set\n"
            "       DATABASE_URL, or the ANALYTICS_DB_* vars (in your gitignored\n"
            "       .env). Never commit a real DSN.",
            file=sys.stderr,
        )
        return 1

    # 2. The DB driver is optional + lazy: only needed for a real run.
    try:
        import psycopg2  # noqa: F401  (lazy: only when validate actually connects)
    except ImportError:
        print(
            "error: `retail validate` needs the optional DB driver.\n"
            "       install it with:  pip install 'retail[db]'\n"
            "       (the static `retail check` core stays dependency-free).",
            file=sys.stderr,
        )
        return 1

    # 3. Live execution is the deferred step (004 builds + fixture-tests the
    #    surface; running it against a real DB is the follow-up). Be explicit
    #    rather than pretending to connect. The DSN is resolved and the driver is
    #    present -- only the check-execution + per-table target wiring remain.
    safe_host = dsn.split("@")[-1] if "@" in dsn else dsn  # never echo credentials
    print(
        "retail validate: the live-validator surface is built and fixture-tested; "
        "executing the checks against a live DB is the deferred follow-up.\n"
        f"resolved target (credentials hidden): {safe_host}\n"
        "See specs/004-retail-validate/spec.md (FR-009): live execution is the "
        "deferred step.",
        file=sys.stderr,
    )
    return 1
