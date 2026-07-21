"""The shell-free, closed-argv child-process runner (spec 134 US4, FR-008).

``seshat dagster run`` never imports dagster: it launches the orchestration
environment's interpreter with EXACTLY the argv below -- no shell, no raw
pass-through arguments, no selectors. Table scoping travels via the
``SESHAT_DAGSTER_TABLES`` environment variable (the definitions module's
closed discovery seam), never via argv.
"""

from __future__ import annotations

import os
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from . import ALLOWED_JOBS
from .doctor import orchestration_python
from .redaction import redact_text

_TAIL_CHARS = 4000
_RUN_TIMEOUT_SECONDS = 7200


class RunnerError(RuntimeError):
    """A preflight-shaped runner failure (missing environment, bad job)."""


@dataclass(frozen=True)
class RunResult:
    run_id: str
    exit_code: int
    output: str


def new_run_id() -> str:
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + uuid.uuid4().hex[:8]


def build_run_argv(python: Path, job: str) -> list[str]:
    if job not in ALLOWED_JOBS:
        raise ValueError(f"job must be one of {sorted(ALLOWED_JOBS)}, got: {job!r}")
    return [
        str(python),
        "-m",
        "dagster",
        "job",
        "execute",
        "-m",
        "tower_bi_orchestration.definitions",
        "-j",
        job,
    ]


def execute_run(root: Path, job: str, table: str | None = None) -> RunResult:
    """Run one job in the orchestration environment; return the redacted result.

    The child's evidence lands under ``.seshat/dagster/runs/<run_id>/`` because
    the run id is injected via ``SESHAT_DAGSTER_RUN_ID`` -- the parent then
    finalizes and renders it (evidence.py)."""
    root = Path(root)
    python = orchestration_python(root)
    if python is None:
        raise RunnerError(
            "orchestration environment absent -- run `seshat dagster doctor` "
            "for the install remedy"
        )
    argv = build_run_argv(python, job)
    run_id = new_run_id()
    env = dict(os.environ)
    env["SESHAT_DAGSTER_RUN_ID"] = run_id
    env["SESHAT_REPO_ROOT"] = str(root)
    # Force the CHILD to EMIT UTF-8, not just decode it in the parent (#404).
    # The `python -m dagster` child does not run seshat's stdio reconfig, so on
    # Windows it would otherwise write via the legacy code page (cp1252) and
    # UnicodeEncodeError on non-Latin-1 governed values (e.g. Arabic). Pairing
    # the child's UTF-8 output with the parent's UTF-8 decode also stops
    # `errors="replace"` from silently corrupting cp1252-encoded chars like `é`.
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    if table:
        env["SESHAT_DAGSTER_TABLES"] = table
    else:
        env.pop("SESHAT_DAGSTER_TABLES", None)
    try:
        proc = subprocess.run(
            argv,
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            # Decode the child's stdout/stderr as UTF-8, NOT the platform default
            # (cp1252 on Windows). The Dagster child ingests governed data whose
            # values can be non-Latin-1 (e.g. Arabic `billing_type`); with
            # `text=True` alone the reader thread decodes via
            # locale.getpreferredencoding() and raises UnicodeDecodeError mid-run
            # on Windows (#404). `errors="replace"` keeps a stray byte from
            # crashing the capture. Same class as the #322 stdio fix, one layer
            # down at the subprocess-read boundary.
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=_RUN_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        # Fail closed: a hung child is a FAILED run, never an exception the
        # caller might swallow into a green result (review finding).
        return RunResult(
            run_id=run_id,
            exit_code=124,
            output=f"child run timed out after {_RUN_TIMEOUT_SECONDS}s (killed)",
        )
    combined = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    # Redact BEFORE truncating (#362 leak #2): slicing first can cut a DSN's
    # `scheme://` into the discarded front, leaving a schemeless credential
    # remainder that every redaction pass then misses. Redacting the full string
    # first, then trimming to the tail, closes that.
    return RunResult(
        run_id=run_id,
        exit_code=proc.returncode,
        output=redact_text(combined).strip()[-_TAIL_CHARS:],
    )
