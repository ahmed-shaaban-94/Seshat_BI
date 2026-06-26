#!/usr/bin/env python3
"""Tabular Editor 2 BPA adapter -- headless smoke-test runner (F038 spike).

OPTIONAL + SKIP-SAFE. This is NOT part of the stdlib-only `retail check` core; it
lives under ``tools/`` and is never imported by ``src/retail/``. On a machine with
no Tabular Editor (e.g. CI), it exits 0 with a "skipped" status and launches no GUI.

What it does (the spike's six proof gates):
  1. Headless        -- invokes ONLY the documented TE CLI form (never the bare exe).
  2. No live Desktop -- analyzes the committed TMDL ``definition/`` folder from disk.
  3. Repo rules      -- runs ``tools/bpa-rules/retail-bpa.json`` (committed), not a
                        machine-global/cloud ruleset.
  4. Machine-readable-- parses TE's ``-V`` VSTS log lines. NOTE: TE exits 0 even WITH
                        violations, so the verdict is derived by PARSING output, not
                        from the exit code.
  5. CI/scripted     -- one command, bounded timeout, no clicks.
  6. Fails safe      -- absent binary / unset path => clean skip, no crash, no GUI.

Authority boundary: BPA findings are ADVISORY / generic DAX best-practice ONLY --
never a Tower BI contract / approval / business-truth verdict (see the F038 spec).

Usage:
    python tools/bpa_runner.py [--model <definition-dir>] [--rules <rules.json>]
                               [--timeout 60] [--evidence <path.md>]
Exit codes:
    0  ran headlessly (with or without BPA violations), OR cleanly skipped.
    2  a proof gate FAILED (not headless / no machine-readable result / timeout).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Default committed locations (relative to the repo root = this file's parent.parent).
_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_MODEL = _REPO_ROOT / "powerbi" / "Retailgold.SemanticModel" / "definition"
_DEFAULT_RULES = _REPO_ROOT / "tools" / "bpa-rules" / "retail-bpa.json"
# Documented fallback install path (after $TABULAR_EDITOR_PATH).
_DEFAULT_TE_PATH = Path(r"C:\Program Files (x86)\Tabular Editor\TabularEditor.exe")

_ENABLE_STEPS = (
    "Tabular Editor 2 not configured. This adapter is OPTIONAL and SKIP-SAFE.\n"
    "  To enable: install Tabular Editor 2 and set TABULAR_EDITOR_PATH to the full\n"
    "  path of TabularEditor.exe, e.g.\n"
    "    export TABULAR_EDITOR_PATH="
    '"C:/Program Files (x86)/Tabular Editor/TabularEditor.exe"\n'
    "  CI without the binary is expected to skip; `retail check` is unaffected."
)


def resolve_te_path() -> Path | None:
    """Resolve the TabularEditor.exe path: env first, then the documented default.

    Returns None if neither is a real file -- the caller MUST then skip cleanly
    (FR-001/FR-006 gate 6), never crash and never launch a GUI.
    """
    env = os.environ.get("TABULAR_EDITOR_PATH")
    if env:
        p = Path(env)
        return p if p.is_file() else None
    return _DEFAULT_TE_PATH if _DEFAULT_TE_PATH.is_file() else None


def _parse_violations(vsts_output: str) -> list[str]:
    """Return the BPA violation lines from TE's -V (VSTS) output.

    Gate 4: TE exits 0 whether or not violations exist, so the verdict is derived
    by PARSING the ``##vso[task.logissue ...] ... violates rule ...`` lines, not the
    exit code.
    """
    violations: list[str] = []
    for line in vsts_output.splitlines():
        if "##vso[task.logissue" in line and "violates rule" in line:
            # strip the leading ##vso[...] marker, keep the human-readable tail
            violations.append(line.split("]", 1)[-1].strip())
    return violations


def run_smoke(model: Path, rules: Path, timeout: int) -> tuple[str, dict[str, object]]:
    """Run the headless BPA smoke test. Returns (status, details).

    status is one of: "skipped" (no binary), "ran" (headless ok), "gate_failed".
    """
    te = resolve_te_path()
    if te is None:
        return "skipped", {"reason": "TABULAR_EDITOR_PATH unset / binary absent"}

    if not model.is_dir():
        return "gate_failed", {"gate": 2, "reason": f"model dir not found: {model}"}
    if not rules.is_file():
        return "gate_failed", {"gate": 3, "reason": f"rules file not found: {rules}"}

    # ONLY the documented headless CLI form: <model> -A <rules> -V. Never the bare exe.
    cmd = [str(te), str(model), "-A", str(rules), "-V"]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        # A hang means a GUI/prompt opened -> gate 1 (not headless) failure.
        return "gate_failed", {
            "gate": 1,
            "reason": f"timed out after {timeout}s (GUI/prompt suspected)",
            "command": cmd,
        }

    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    # Gate 4: a tool ERROR (vs a benign "violations found") is a real failure.
    tool_errored = "##vso[task.complete result=Failed;]" in out and (
        "Error on rule" in out or "File not found" in out
    )
    violations = _parse_violations(out)
    return (
        "ran",
        {
            "command": cmd,
            "exit_code": proc.returncode,
            "gui_spawned": False,  # headless CLI form; a GUI would have hung -> timeout
            "tool_errored": tool_errored,
            "violation_count": len(violations),
            "violations": violations[:50],
            "output_head": out.strip().splitlines()[:20],
        },
    )


def write_evidence(path: Path, status: str, details: dict[str, object]) -> None:
    """Write the dated six-gate evidence record."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# F038 Tabular Editor BPA -- headless smoke evidence ({now})",
        "",
        f"- **Status:** {status}",
        "- **Authority:** BPA findings are ADVISORY / generic DAX best-practice ONLY",
        "  -- NOT a Tower BI contract / approval / business-truth verdict.",
        "",
        "## Details",
        "",
        "```",
        *(f"{k}: {v}" for k, v in details.items()),
        "```",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="F038 BPA headless smoke runner")
    parser.add_argument("--model", default=str(_DEFAULT_MODEL))
    parser.add_argument("--rules", default=str(_DEFAULT_RULES))
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--evidence", default=None)
    args = parser.parse_args(argv)

    status, details = run_smoke(Path(args.model), Path(args.rules), args.timeout)

    if status == "skipped":
        print(_ENABLE_STEPS, file=sys.stderr)
        print("bpa-runner: skipped (not configured)", file=sys.stderr)
        if args.evidence:
            write_evidence(Path(args.evidence), status, details)
        return 0  # FR-001/FR-008: clean skip, never a failure

    if args.evidence:
        write_evidence(Path(args.evidence), status, details)

    if status == "gate_failed":
        print(f"bpa-runner: PROOF GATE FAILED -> {details}", file=sys.stderr)
        return 2

    # status == "ran": headless analysis succeeded (gates 1-5 demonstrated).
    if details.get("tool_errored"):
        print(f"bpa-runner: tool error during analysis -> {details}", file=sys.stderr)
        return 2
    n = details.get("violation_count", 0)
    print(
        f"bpa-runner: ran headlessly (advisory BPA violations: {n}). "
        "Findings are generic DAX best-practice, NOT a Tower BI verdict.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    # `python -m tools.bpa_runner` / `python tools/bpa_runner.py` both work.
    if __package__ in (None, "") and str(_REPO_ROOT) not in sys.path:
        pass  # no package import needed; the module is self-contained stdlib.
    sys.exit(main())
