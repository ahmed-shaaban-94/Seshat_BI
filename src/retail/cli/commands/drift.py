"""`retail drift` handler (F014 source-drift detector runtime).

Two-mode, mirroring `validate`: without a --dsn (no observed re-profile) it
reports the deferred [PENDING LIVE RE-PROFILE] state and returns 1 -- it NEVER
fabricates a comparison (Principle VIII). A non-conformant baseline is reported
as uncomparable rather than guessed at, and a missing --baseline path is a clean
error, never a raw traceback. The live leg (build a QueryRunner, call
retail.profile.profile, diff) is wired through the cli seams so tests patch it
without touching a real DB.
"""

from __future__ import annotations

import argparse
import json
import sys


def run_drift(args: argparse.Namespace) -> int:
    from retail.source_profile_reader import read_source_profile

    # A missing/unreadable --baseline path is a distinct failure from a
    # non-conformant one; surface it as a clean message (never a traceback),
    # matching run_validate's "actionable message, not a stack trace" posture.
    try:
        parsed = read_source_profile(args.baseline)
    except OSError as exc:
        print(
            f"retail drift: cannot read baseline {args.baseline!r}: {exc}",
            file=sys.stderr,
        )
        return 1

    if parsed.uncomparable is not None:
        print(f"retail drift: {parsed.uncomparable}", file=sys.stderr)
        return 1

    if not args.dsn:
        # Deferred-live: emit a schema-valid pending document; never a fake diff.
        from retail.drift import to_findings_dict

        doc = to_findings_dict(
            baseline=parsed.profile,
            observed=None,
            baseline_ref=str(args.baseline),
            evidence=[str(args.baseline)],
        )
        if getattr(args, "output_format", "text") == "json":
            print(json.dumps(doc, indent=2))
        print(
            "retail drift: [PENDING LIVE RE-PROFILE] -- no --dsn given, so no "
            "observed re-profile was taken. status=pending_live_reprofile + "
            "warning; no comparison fabricated. Pass --dsn to run the live leg.",
            file=sys.stderr,
        )
        return 1

    # Live leg: build the read-only runner via the cli seam (patched in tests),
    # re-profile the SAME table, diff, emit.
    #
    # Mirrors run_validate's DB-boundary discipline: resolve the engine config,
    # gate on the lazy driver, and scrub every DB-boundary exception through
    # dialect.redact(exc, config) so a DSN (user/host/password) NEVER leaks in a
    # traceback. The observed re-profile runs on the PK the baseline STATES
    # (parsed.pk_columns) -- NOT a guessed column -- so baseline.pk and
    # observed.pk describe the same key and grain_pk_drift can't be fabricated.
    import os

    from retail import cli
    from retail.dialect import get_dialect
    from retail.drift import to_findings_dict
    from retail.profile import profile as run_profile
    from retail.validate import resolve_dsn

    engine = cli._current_engine()
    dialect = get_dialect(engine)
    if engine == "postgres":
        env = {**os.environ, "DATABASE_URL": args.dsn}
        config = resolve_dsn(env)
    else:
        config = dialect.resolve_config(dict(os.environ))
    if config is None:
        print(
            "retail drift: no database connection configured for the live "
            "re-profile. Pass --dsn (postgresql://...) or set the ANALYTICS_DB_* "
            "vars in your gitignored .env. Never commit a real DSN.",
            file=sys.stderr,
        )
        return 1

    if not cli._ensure_driver():
        print(
            "retail drift: the live re-profile needs the optional DB driver.\n"
            "       install it with:  pip install 'retail[db]'\n"
            "       (the deferred [PENDING LIVE RE-PROFILE] mode needs no driver).",
            file=sys.stderr,
        )
        return 1

    if not parsed.pk_columns:
        print(
            "retail drift: baseline states no candidate PK column set, so the "
            "live re-profile cannot re-prove grain on the same key. Treated as "
            "uncomparable rather than guessing a key.",
            file=sys.stderr,
        )
        return 1

    try:
        runner = cli._make_runner(config)
        observed = run_profile(runner, parsed.profile.table, parsed.pk_columns)
    except Exception as exc:
        print(
            "retail drift: live re-profile failed at the DB boundary "
            f"({exc.__class__.__name__}): {dialect.redact(exc, config)}",
            file=sys.stderr,
        )
        return 1

    doc = to_findings_dict(
        baseline=parsed.profile,
        observed=observed,
        baseline_ref=str(args.baseline),
        evidence=[str(args.baseline)],
        reprofiled_by="agent (retail.profile, read-only session)",
    )
    if getattr(args, "output_format", "text") == "json":
        print(json.dumps(doc, indent=2))
    else:
        n = len(doc["findings"])
        print(f"retail drift: status={doc['status']}; {n} finding(s)")
        for r in doc["blocking_reasons"]:
            print(f"  blocking_reason: {r}")
    return 0 if doc["status"] in ("pass", "warning") else 1
