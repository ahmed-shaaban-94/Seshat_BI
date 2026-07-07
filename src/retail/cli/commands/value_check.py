"""`retail value-check` handler: L4 value proxy (live recompute vs approved value).

Extracted verbatim from the former ``retail/cli.py`` (CodeScene hotspot split).
Calls the shared seams (``_ensure_driver``, ``_make_runner``, ``_current_engine``,
``_safe_target_label``) via ``from retail import cli`` -- NOT a by-value import --
so the test suite's ``monkeypatch.setattr("retail.cli._make_runner", ...)`` still
lands on the exact attribute this handler reads at call time.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path


def _filter_to_sql(filters: object, quote: Callable[..., str]) -> str | None:
    """Translate an L3 ``filter`` list into a SQL WHERE predicate (AND-joined).

    Reuses the L3 recognized-op vocabulary (``is_not_null`` / ``is_true``); each
    column is quoted via the hardened identifier helper. Returns None for an
    unrecognized op or a malformed entry (the caller fails the check closed).
    Empty/None filter list => "TRUE" (count all rows).
    """
    if not filters:
        return "TRUE"
    if not isinstance(filters, list):
        return None
    parts: list[str] = []
    for f in filters:
        if not isinstance(f, dict):
            return None
        col, op = f.get("column"), f.get("op")
        if not col:
            return None
        qcol = quote(col, context="L4 ratio filter column")
        if op == "is_not_null":
            parts.append(f"{qcol} IS NOT NULL")
        elif op == "is_true":
            parts.append(f"{qcol} = TRUE")
        else:
            return None
    return " AND ".join(parts)


def run_value_check(args: argparse.Namespace) -> int:
    """Run the L4 value proxy: recompute each contract's approved value live.

    Lazy psycopg2 (via ``_ensure_driver`` / ``_make_runner``, reused from the
    validate path) so the stdlib-only `retail check` chain never imports a driver.
    Discovers metric contracts under --metrics-dir (confined to the repo, like
    semantic-check), parses each ``definition.expected_value`` block, recomputes the
    aggregate/ratio against the live gold table, and reports a V-L4 ERROR for any
    value outside tolerance. A contract with no expected_value block is skipped; a
    malformed block is a fail-closed ERROR, never a silent skip.
    """
    import dataclasses
    import os

    from retail import cli
    from retail.core import Severity
    from retail.dialect import get_dialect
    from retail.metric_drift import load_definition
    from retail.runner import _format
    from retail.validate import resolve_dsn
    from retail.value_proxy import check_expected_value, parse_expected_value

    repo = Path(args.repo)
    engine = cli._current_engine()
    dialect = get_dialect(engine)

    # Confine --metrics-dir to the repo tree (same guard as semantic-check, #26).
    repo_resolved = repo.resolve()
    metrics_root = (repo / args.metrics_dir).resolve()
    if metrics_root != repo_resolved and not metrics_root.is_relative_to(repo_resolved):
        print(
            f"error: --metrics-dir {args.metrics_dir!r} escapes the repo root; "
            "it must resolve to a path inside --repo.",
            file=sys.stderr,
        )
        return 1

    # 1. Resolve the engine's config. Postgres: --dsn wins; else env (UNCHANGED
    #    behavior). Other engines: --dsn is not applicable; resolve from env only.
    if engine == "postgres":
        env = dict(os.environ)
        if args.dsn:
            env = {**env, "DATABASE_URL": args.dsn}
        config = resolve_dsn(env)
    else:
        config = dialect.resolve_config(dict(os.environ))
    if config is None:
        print(
            "error: no database connection configured.\n"
            "       pass --dsn (a postgresql:// connection string), or set\n"
            "       DATABASE_URL, or the ANALYTICS_DB_* vars (in your gitignored\n"
            "       .env). Never commit a real DSN.",
            file=sys.stderr,
        )
        return 1

    # 2. The DB driver is optional + lazy: only needed for a real run.
    if not cli._ensure_driver():
        print(
            "error: `retail value-check` needs the optional DB driver.\n"
            "       install it with:  pip install 'retail[db]'\n"
            "       (the static `retail check` core stays dependency-free).",
            file=sys.stderr,
        )
        return 1

    # 3. Discover contracts and parse each expected_value block (fail-closed).
    expectations: list[tuple[str, object]] = []  # (measure_name, ExpectedValue)
    if metrics_root.is_dir():
        for contract_path in sorted(metrics_root.glob("*/metrics/*.yaml")):
            name = contract_path.stem
            try:
                definition = load_definition(str(contract_path))
            except (OSError, ValueError) as exc:
                print(
                    f"error: could not load contract {contract_path}: {exc}",
                    file=sys.stderr,
                )
                return 1
            # binds_to lives at the contract top level, not under `definition`.
            try:
                import yaml

                doc = yaml.safe_load(contract_path.read_text(encoding="utf-8")) or {}
            except (OSError, ValueError) as exc:
                print(
                    f"error: could not load contract {contract_path}: {exc}",
                    file=sys.stderr,
                )
                return 1
            binds_to = doc.get("binds_to") or {}
            try:
                expected = parse_expected_value(definition, binds_to)
            except ValueError as exc:
                print(
                    f"error: contract {name}: malformed expected_value ({exc})",
                    file=sys.stderr,
                )
                return 1
            if expected is None:
                continue  # no expected_value block -> skip
            # For a ratio, translate the L3 numerator/denominator filters into SQL.
            if expected.aggregation == "ratio":
                num_sql = _filter_to_sql(
                    (definition or {}).get("numerator", {}).get("filter"),
                    dialect.quote_ident,
                )
                den_sql = _filter_to_sql(
                    (definition or {}).get("denominator", {}).get("filter"),
                    dialect.quote_ident,
                )
                if num_sql is None or den_sql is None:
                    print(
                        f"error: contract {name}: ratio numerator/denominator filter "
                        "uses an unrecognized op (L4 cannot recompute it)",
                        file=sys.stderr,
                    )
                    return 1
                expected = dataclasses.replace(
                    expected,
                    numerator_count_sql_filter=num_sql,
                    denominator_count_sql_filter=den_sql,
                )
            expectations.append((name, expected))

    if not expectations:
        print(
            "retail value-check: no contract carries a `definition.expected_value` "
            "block -- nothing to verify.",
            file=sys.stderr,
        )
        return 0

    # 4. Connect and run each check. No real DB is touched in tests (fake runner).
    safe_host = cli._safe_target_label(engine, config)
    print(
        f"retail value-check: running L4 value checks against {safe_host}",
        file=sys.stderr,
    )
    try:
        runner = cli._make_runner(config)
        findings = []
        for name, expected in expectations:
            findings.extend(
                check_expected_value(runner, name, expected, dialect=dialect)
            )
    except ValueError as exc:
        # an unsafe identifier in a contract -> clean message, no traceback
        print(
            f"error: value-check rejected an unsafe contract identifier: {exc}",
            file=sys.stderr,
        )
        return 1
    except Exception as exc:
        print(
            "error: live value-check failed at the DB boundary "
            f"({exc.__class__.__name__}): {dialect.redact(exc, config)}",
            file=sys.stderr,
        )
        return 1

    for finding in findings:
        print(_format(finding))
    if any(f.severity is Severity.ERROR for f in findings):
        return 1
    print(
        "retail value-check: all live values match the approved contracts "
        "(0 findings).",
        file=sys.stderr,
    )
    return 0
