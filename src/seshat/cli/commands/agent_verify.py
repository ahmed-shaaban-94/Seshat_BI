"""`seshat agent verify --target claude|codex` handler (spec 129).

Produces categorical PASS/BLOCKED/UNAVAILABLE evidence that a shipped agent
integration installs correctly and ships the governance contract intact --
never a score, rank, pass-rate, grade, or rolled-up "certified"/"verified"
result (FR-003). Static-first: inspects the installed bundle and the
committed governance contract; never launches a live agent, never opens a
database, never reaches the network, never requires a running IDE
(FR-006/FR-007/FR-008). Grants no approval and advances no readiness stage
(FR-004).

Exit codes (stable):
  0  every required check is PASS
  1  at least one required check is BLOCKED
  2  input defect: unknown --target, or an uncontained --output/publish path
  3  at least one required check is UNAVAILABLE and none is BLOCKED (a
     truthful "not fully verifiable" result -- distinct from 0 so an
     UNAVAILABLE-only run never reads as a pass)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from seshat.agent_verify.model import PerCheckResult


def _print_evidence_lines(items: Sequence[str]) -> None:
    for item in items:
        print(f"    evidence: {item}")


def _print_blocked_lines(reasons: Sequence[str]) -> None:
    for reason in reasons:
        print(f"    blocked: {reason}")


def _print_check(result: PerCheckResult) -> None:
    print(f"[{result.verdict}] {result.check_id} ({result.evidence_class})")
    if result.verdict == "PASS":
        _print_evidence_lines(result.evidence)
    elif result.verdict == "BLOCKED":
        _print_blocked_lines(result.blocking_reasons)
    else:
        print(f"    unavailable: {result.unavailable_reason}")


def _summary_line(blocked: list[str], unavailable: list[str]) -> str:
    if not blocked and not unavailable:
        return "every required check is PASS (evidence only; grants no approval)"
    parts = []
    if blocked:
        parts.append(f"BLOCKED: {', '.join(blocked)}")
    if unavailable:
        parts.append(f"UNAVAILABLE: {', '.join(unavailable)}")
    return "; ".join(parts)


def _print_report(target: str, results: Sequence[PerCheckResult]) -> None:
    print(f"agent verify --target {target}")
    for result in results:
        _print_check(result)
    blocked = [item.check_id for item in results if item.verdict == "BLOCKED"]
    unavailable = [item.check_id for item in results if item.verdict == "UNAVAILABLE"]
    print(f"summary: {_summary_line(blocked, unavailable)}")


def _resolve_target_or_error(target_name: str):
    from seshat.agent_verify.targets import UnknownVerifyTargetError, resolve_target

    try:
        return resolve_target(target_name), None
    except UnknownVerifyTargetError as exc:
        print(f"error: {exc}")
        return None, 2


def _write_record_or_error(record, *, repo_root: Path, output):
    from seshat.agent_verify.record import write_record

    try:
        return write_record(record, repo_root=repo_root, output=output), None
    except ValueError as exc:
        print(f"error: {exc}")
        return None, 2


def _maybe_publish(record, *, requested: bool) -> int | None:
    if not requested:
        return None
    from seshat.agent_verify.record import publish_record

    try:
        outcome = publish_record(record, requested=True)
    except ValueError as exc:
        print(f"publish refused: {exc}")
        return 2
    disclosure_status = outcome["disclosure"]["status"]
    print(f"publish: {outcome['status']} (disclosure={disclosure_status})")
    return None


def _exit_code_for(results: Sequence[PerCheckResult]) -> int:
    if any(item.verdict == "BLOCKED" for item in results):
        return 1
    if any(item.verdict == "UNAVAILABLE" for item in results):
        return 3
    return 0


def _run_verify(args: argparse.Namespace) -> int:
    from seshat.agent_verify.checks import run_all_checks
    from seshat.agent_verify.record import build_record

    repo_root = Path(args.repo).resolve()
    target_spec, error_code = _resolve_target_or_error(args.target)
    if error_code is not None:
        return error_code

    results = run_all_checks(target_spec, repo_root)
    record = build_record(args.target, results, repo_root=repo_root)

    written, error_code = _write_record_or_error(
        record, repo_root=repo_root, output=args.output
    )
    if error_code is not None:
        return error_code

    written_relative = written.relative_to(repo_root).as_posix()
    if args.output_format == "json":
        # The written path is folded INTO the JSON object (never appended as
        # a trailing text line) so `--format json` output stays one valid,
        # pipeable JSON document on stdout.
        print(
            json.dumps({**record.to_document(), "written": written_relative}, indent=2)
        )
    else:
        _print_report(args.target, results)
        print(f"written: {written_relative}")

    publish_error_code = _maybe_publish(record, requested=args.publish)
    if publish_error_code is not None:
        return publish_error_code

    return _exit_code_for(results)


def agent_verify_main(args: argparse.Namespace) -> int:
    if args.agent_command == "verify":
        return _run_verify(args)
    print(f"error: unsupported agent subcommand {args.agent_command!r}")
    return 2
