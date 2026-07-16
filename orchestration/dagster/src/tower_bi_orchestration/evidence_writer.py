"""Thin re-export: the ONE evidence implementation lives in the main package
(``seshat.dagster_adapter.evidence``, research D3/D4) so the parent CLI (no
dagster) and this orchestration package (its own venv, seshat installed
editable) share writer, finalize, validation, and rendering."""

from __future__ import annotations

from seshat.dagster_adapter.evidence import (  # noqa: F401
    EvidenceWriter,
    commit_sha,
    finalize_run,
    run_dir,
)

__all__ = ["EvidenceWriter", "commit_sha", "finalize_run", "run_dir"]
