"""Dagster run evidence: raw records, finalization, validation, rendering.

ONE implementation for both environments (research D3/D4): the orchestration
package's assets append records through :class:`EvidenceWriter`; the parent
``seshat dagster`` CLI finalizes a run and renders the committed markdown --
neither side imports dagster here (stdlib + PyYAML only).

The code validator mirrors ``schemas/dagster-run-evidence.schema.json`` (the
machine-readable contract) so an invalid record set is REFUSED, never rendered.
DERIVED EVIDENCE ONLY: outcomes are execution words, never the readiness token
``pass``; no numeric score key is accepted anywhere (hard rule #9); every
string passes redaction before it is written (Principle IX).
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from . import ASSET_ORDER, OUTCOMES
from .redaction import redact_payload

_HALTED = {"failed", "skipped", "blocked", "deferred"}
_TRIGGERS = {"schedule", "sensor", "manual-CI"}
_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
_SUMMARY_KEYS = {
    "run_id",
    "commit_sha",
    "started",
    "finished",
    "trigger",
    "tables",
    "run_status",
}
_RECORD_KEYS = {
    "run_id",
    "asset",
    "table",
    "gate_command",
    "exit_code",
    "measured",
    "outcome",
    "blocking_reason",
    "owner",
    "ts",
}

_HUMAN_SEAM_ASSETS = {"source_map", "semantic_model", "publish_execution_evidence"}


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_dir(root: Path, run_id: str) -> Path:
    return Path(root) / ".seshat" / "dagster" / "runs" / run_id


def evidence_out_path(root: Path, run_id: str) -> Path:
    return Path(root) / "orchestration" / "dagster" / "run-evidence" / f"{run_id}.md"


def commit_sha(root: Path) -> str:
    """The repo state the run executed against; '0000000' when git is absent
    (a fixture repo) -- recorded honestly, never fabricated as a real sha."""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
        )
        sha = proc.stdout.strip()
        if proc.returncode == 0 and sha:
            return sha
    except OSError:
        pass
    return "0000000"


class EvidenceWriter:
    """Append-only writer for one run's raw records (git-ignored area)."""

    def __init__(self, root: Path, run_id: str) -> None:
        self.root = Path(root)
        self.run_id = run_id
        self.directory = run_dir(self.root, run_id)
        self.directory.mkdir(parents=True, exist_ok=True)

    @property
    def records_path(self) -> Path:
        return self.directory / "records.jsonl"

    def record(
        self,
        *,
        asset: str,
        table: str,
        gate_command: str,
        exit_code: int | None,
        measured: dict,
        outcome: str,
        blocking_reason: str | None = None,
        owner: str | None = None,
    ) -> dict:
        if asset not in ASSET_ORDER:
            raise ValueError(f"unknown asset name: {asset}")
        if outcome not in OUTCOMES:
            raise ValueError(f"outcome must be an execution word, got: {outcome}")
        if outcome in _HALTED and not (blocking_reason and owner):
            raise ValueError(f"halted outcome {outcome} requires blocking_reason + owner")
        row = redact_payload(
            {
                "run_id": self.run_id,
                "asset": asset,
                "table": table,
                "gate_command": gate_command,
                "exit_code": exit_code,
                "measured": measured,
                "outcome": outcome,
                "blocking_reason": blocking_reason,
                "owner": owner,
                "ts": _utc_now(),
            }
        )
        with self.records_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        return row

    def records(self) -> list[dict]:
        if not self.records_path.is_file():
            return []
        return [
            json.loads(line)
            for line in self.records_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]


def finalize_run(
    root: Path,
    run_id: str,
    tables: list[str],
    *,
    started: str,
    trigger: str = "manual-CI",
) -> dict:
    """Back-fill ``skipped`` records for never-ran assets and write summary.json.

    A STOP edge means downstream assets never execute, so they cannot record
    themselves; the back-fill cites the first halted upstream asset (concrete
    reason + its named owner) -- exactly what the committed evidence table must
    show (US1/US3). Computes ``run_status``: failed when anything failed or
    blocked (the CI signal), else succeeded.
    """
    writer = EvidenceWriter(root, run_id)
    by_table: dict[str, dict[str, dict]] = {}
    for row in writer.records():
        by_table.setdefault(row["table"], {})[row["asset"]] = row

    for table in tables:
        rows = by_table.get(table, {})
        halted_upstream: dict | None = None
        for asset in ASSET_ORDER:
            row = rows.get(asset)
            if row is not None:
                if row["outcome"] in {"failed", "blocked"}:
                    halted_upstream = halted_upstream or row
                continue
            if halted_upstream is None:
                reason = "not selected / run ended before this asset"
                owner = "orchestration owner"
            else:
                reason = (
                    f"upstream STOP edge: {halted_upstream['asset']} "
                    f"{halted_upstream['outcome']} -- {halted_upstream['blocking_reason']}"
                )
                owner = halted_upstream["owner"] or "orchestration owner"
            writer.record(
                asset=asset,
                table=table,
                gate_command="n/a -- did not run",
                exit_code=None,
                measured={},
                outcome="skipped",
                blocking_reason=reason,
                owner=owner,
            )

    final_records = writer.records()
    run_status = (
        "failed"
        if any(row["outcome"] in {"failed", "blocked"} for row in final_records)
        else "succeeded"
    )
    summary = {
        "run_id": run_id,
        "commit_sha": commit_sha(root),
        "started": started,
        "finished": _utc_now(),
        "trigger": trigger,
        "tables": sorted(tables),
        "run_status": run_status,
    }
    (writer.directory / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def _score_keys(payload: object) -> list[str]:
    found: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if "score" in str(key).lower():
                found.append(str(key))
            found.extend(_score_keys(value))
    elif isinstance(payload, list):
        for item in payload:
            found.extend(_score_keys(item))
    return found


def validate_records(summary: dict, records: list[dict]) -> list[str]:
    """Errors that make a record set unrenderable. Mirrors the JSON schema."""
    errors: list[str] = []
    for key in sorted(_SUMMARY_KEYS - set(summary)):
        errors.append(f"summary: missing key {key}")
    for key in sorted(set(summary) - _SUMMARY_KEYS):
        errors.append(f"summary: unknown key {key}")
    if summary.get("run_status") not in {"succeeded", "failed"}:
        errors.append(f"summary: run_status must be succeeded|failed, got {summary.get('run_status')!r}")
    if summary.get("trigger") not in _TRIGGERS:
        errors.append(f"summary: trigger must be one of {sorted(_TRIGGERS)}")
    if not _SHA_RE.match(str(summary.get("commit_sha", ""))):
        errors.append("summary: commit_sha must be a 7-40 char hex sha")
    if not records:
        errors.append("records: empty")
    for index, row in enumerate(records):
        label = f"records[{index}]"
        for key in sorted(_RECORD_KEYS - set(row)):
            errors.append(f"{label}: missing key {key}")
        for key in sorted(set(row) - _RECORD_KEYS):
            errors.append(f"{label}: unknown key {key}")
        if row.get("asset") not in ASSET_ORDER:
            errors.append(f"{label}: asset must be one of the spec-024 graph names")
        if row.get("outcome") not in OUTCOMES:
            errors.append(
                f"{label}: outcome must be an execution word "
                f"({'|'.join(sorted(OUTCOMES))}), got {row.get('outcome')!r}"
            )
        if row.get("outcome") in _HALTED:
            if not row.get("blocking_reason") or not row.get("owner"):
                errors.append(f"{label}: halted outcome requires blocking_reason + owner")
        for key in _score_keys(row):
            errors.append(f"{label}: score-like key forbidden (hard rule #9): {key}")
    return errors


def load_run(root: Path, run_id: str) -> tuple[dict, list[dict]]:
    directory = run_dir(root, run_id)
    summary_path = directory / "summary.json"
    records_path = directory / "records.jsonl"
    if not summary_path.is_file() or not records_path.is_file():
        raise FileNotFoundError(f"run {run_id} has no summary.json/records.jsonl under .seshat/dagster/runs/")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return summary, records


def list_runs(root: Path) -> list[dict]:
    runs_root = Path(root) / ".seshat" / "dagster" / "runs"
    if not runs_root.is_dir():
        return []
    out: list[dict] = []
    for directory in sorted(runs_root.iterdir()):
        summary_path = directory / "summary.json"
        if summary_path.is_file():
            out.append(json.loads(summary_path.read_text(encoding="utf-8")))
    return out


def _measured_cell(measured: dict) -> str:
    if not measured:
        return "-"
    parts = [f"{key}: {value}" for key, value in sorted(measured.items())]
    return "; ".join(str(part) for part in parts)


def render_markdown(summary: dict, records: list[dict]) -> str:
    """Deterministic committed evidence per templates/dagster-run-evidence.md."""
    lines: list[str] = []
    run_id = summary["run_id"]
    lines.append(f"# Dagster Run Evidence -- `{run_id}`")
    lines.append("")
    lines.append(
        "> DERIVED EVIDENCE about one orchestrated run (template: "
        "`templates/dagster-run-evidence.md`; spec 024 / F030). Outcomes are "
        "execution words, never the readiness token `pass`; this record writes "
        "no readiness `status`, no `Gate status`, no `approvals[]`, and no "
        "numeric score."
    )
    lines.append("")
    lines.append("## Run header")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append(f"| Run id | `{run_id}` |")
    lines.append(f"| Commit sha | `{summary['commit_sha']}` |")
    lines.append(f"| Started | `{summary['started']}` |")
    lines.append(f"| Finished | `{summary['finished']}` |")
    lines.append(f"| Triggered by | `{summary['trigger']}` |")
    lines.append(f"| Table(s) in scope | `{', '.join(summary['tables'])}` |")
    lines.append(
        "| Connection | READ-ONLY for validation steps; credentials from the "
        "git-ignored `.env` only (never recorded here). |"
    )
    lines.append(f"| Run status | `{summary['run_status']}` |")
    lines.append("")
    lines.append("## Per-asset results")
    lines.append("")
    lines.append("| # | Table | Asset | Gate command | Exit code | Measured | Outcome |")
    lines.append("|---|-------|-------|--------------|-----------|----------|---------|")
    ordered = sorted(
        records,
        key=lambda row: (row["table"], ASSET_ORDER.index(row["asset"])),
    )
    for number, row in enumerate(ordered, start=1):
        seam = " (HUMAN SEAM)" if row["asset"] in _HUMAN_SEAM_ASSETS else ""
        exit_cell = "n/a" if row["exit_code"] is None else str(row["exit_code"])
        lines.append(
            f"| {number} | `{row['table']}` | `{row['asset']}`{seam} "
            f"| `{row['gate_command']}` | {exit_cell} "
            f"| {_measured_cell(row['measured'])} | `{row['outcome']}` |"
        )
    lines.append("")
    halted = [row for row in ordered if row["outcome"] in _HALTED]
    lines.append("## Blocked / skipped assets")
    lines.append("")
    if halted:
        lines.append("| Table | Asset | Blocking reason | Named owner who can clear it |")
        lines.append("|-------|-------|-----------------|------------------------------|")
        for row in halted:
            lines.append(
                f"| `{row['table']}` | `{row['asset']}` | {row['blocking_reason']} "
                f"| {row['owner']} |"
            )
    else:
        lines.append("None -- every reached asset materialized.")
    lines.append("")
    lines.append("## What this run did NOT write (the no-authored-truth attestation)")
    lines.append("")
    lines.append("- [x] No `readiness-status.yaml` stage `status` was changed by this run.")
    lines.append("- [x] No `Gate status: CLEARED` was written by this run.")
    lines.append("- [x] No `approvals[]` entry was added by this run.")
    lines.append(
        "- [x] No metric / mapping / grain / rollup / segment / PII disposition "
        "was defined by this run."
    )
    lines.append(
        "- [x] No Power BI model was published and no Power BI connection was "
        "opened by this run (the terminal asset only TRIGGERS F016 when "
        "`publish_ready = pass`, and FAILS CLOSED while F016 is absent)."
    )
    lines.append(
        "- [x] No numeric health / confidence / maturity value appears anywhere "
        "in this record."
    )
    lines.append("")
    return "\n".join(lines)


def write_run_evidence(root: Path, run_id: str) -> Path:
    """Validate the raw records and render the committed markdown. REFUSES an
    invalid record set (never renders around a contract violation)."""
    summary, records = load_run(root, run_id)
    errors = validate_records(summary, records)
    if errors:
        detail = "; ".join(errors[:10])
        raise ValueError(f"invalid run evidence for {run_id}: {detail}")
    out_path = evidence_out_path(root, run_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_markdown(summary, records), encoding="utf-8", newline="\n")
    return out_path
