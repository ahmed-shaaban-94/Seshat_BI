"""SL1 -- coverage-scorecard linter.

A committed per-table KPI coverage scorecard
(``mappings/<table>/<...>coverage-scorecard.md``) is the F8 artifact that answers, for
one source table, which KPIs can be served today -- as an explicit **status + named
blocker**, never a number (hard rule #9). Today nothing structurally enforces that a
FILLED scorecard is well-formed; SL1 makes four structural defects an ERROR.

SL1 validates STRUCTURE only. It NEVER adjudicates whether a stated "Covered" is
truly covered (that needs the table's real fields + the contract's real status -- a
Principle-V judgment). It checks, per row of the anchored status table:

  C1  the Coverage-status cell is one of the five closed enum values;
  C2  a ``Blocked -- ...`` row names a specific blocker (the Blocker cell is filled);
  C3  a ``Covered`` row's ``contracts/<file>.md`` path resolves to a tracked file
      (the contract-path-resolves invariant applies to Covered rows ONLY; Planned /
      Out of scope legitimately carry ``--``);
  C4  no ``<number>%`` token appears anywhere (the no-percentage / no-score law).

It is a pure static text read (parse committed markdown), never executes, opens no
connection, and modifies no scorecard/template file.

Ratified decisions (spec 056 ## Clarifications):
  - rule id ``SL1``; severity ERROR;
  - scan tracked ``mappings/**/*coverage-scorecard.md`` instances only -- the generic
    template file is excluded by explicit path (it is placeholders + an illustrative
    worked example by design), and ``tests/`` fixtures are excluded via is_test_path;
  - only rows in the anchored ``> Table:`` status table are parsed (a stray four-column
    table elsewhere contributes no rows);
  - no committed instance -> silent pass (mirrors PP1/G6); advances no readiness stage;
  - a tracked-but-unreadable instance fails loud (an ERROR), never crashes the gate.
"""

from __future__ import annotations

import re
from typing import Iterable

from ..core import Finding, RuleContext, Severity, is_test_path
from ..registry import register

# Per-table scorecard instances end with this suffix; the generic template is excluded
# by its explicit path (it is placeholders + an illustrative example by design).
_INSTANCE_SUFFIX = "coverage-scorecard.md"
_TEMPLATE_PATH = (
    "skills/retail-kpi-knowledge/references/kpi-coverage-scorecard-template.md"
)

# The five closed coverage statuses (F8 vocabulary). Compared after dash-normalization
# so an ASCII "--" and a unicode em-dash "—" both match.
_ENUM: frozenset[str] = frozenset(
    {
        "covered",
        "blocked -- missing field",
        "blocked -- needs business definition",
        "planned",
        "out of scope",
    }
)

# The status table is anchored by its per-table caption so only THIS table's rows are
# parsed; a stray four-column table in another section cannot contribute rows.
_TABLE_ANCHOR_RE = re.compile(r"^>\s*Table:", re.IGNORECASE)
_NEXT_HEADING_RE = re.compile(r"^##\s+")

# A status-table data row, matched POSITIONALLY:
# | KPI | Contract | Coverage status | Blocker |
# The separator row (|---|---|) and the header row are filtered out separately.
_ROW_RE = re.compile(
    r"^\|\s*(?P<kpi>[^|]*?)\s*\|\s*(?P<contract>[^|]*?)\s*\|\s*(?P<status>[^|]*?)\s*\|\s*(?P<blocker>[^|]*?)\s*\|"
)
_SEP_RE = re.compile(r"^\|[\s:|-]+\|$")
# contracts/<file>.md inside an inline-code span or bare.
_CONTRACT_RE = re.compile(r"contracts/[^\s`|]+\.md")
# A number immediately followed by a percent sign -- the forbidden score token. A bare
# "%" with no adjacent digit (e.g. inside a KPI name) does not match.
_PERCENT_RE = re.compile(r"\d\s*%")


def _iter_scorecards(ctx: RuleContext) -> list[str]:
    return [
        p
        for p in ctx.tracked_files
        if p.endswith(_INSTANCE_SUFFIX)
        and p != _TEMPLATE_PATH
        and not is_test_path(p)
    ]


def _norm(cell: str) -> str:
    """Lower-case, strip backticks, and normalize dashes for the enum compare."""
    s = cell.strip().strip("`").strip().lower()
    s = s.replace("—", "--").replace("–", "--")  # em/en dash -> --
    s = re.sub(r"\s*--\s*", " -- ", s)  # collapse spacing around --
    return re.sub(r"\s+", " ", s).strip()


def _is_dash(cell: str) -> bool:
    s = cell.strip().strip("`").strip().replace("—", "--").replace("–", "--")
    return s in ("", "--")


def _status_table_rows(text: str) -> list[re.Match]:
    """The data rows of ONLY the anchored '> Table:' status table."""
    lines = text.splitlines()
    out: list[re.Match] = []
    in_section = False
    header_seen = False
    for line in lines:
        if _TABLE_ANCHOR_RE.match(line):
            in_section = True
            header_seen = False
            continue
        if not in_section:
            continue
        if _NEXT_HEADING_RE.match(line):
            break  # a new ## section ends the anchored table region
        if _SEP_RE.match(line):
            header_seen = True
            continue
        m = _ROW_RE.match(line)
        if not m:
            continue
        # Skip the header row (the one before the separator) -- its status cell is the
        # literal column label, not a data value.
        if not header_seen:
            continue
        out.append(m)
    return out


@register("SL1", "Committed KPI coverage scorecard is structurally well-formed")
def check_coverage_scorecard(ctx: RuleContext) -> Iterable[Finding]:
    findings: list[Finding] = []
    tracked = set(ctx.tracked_files)
    for rel in sorted(_iter_scorecards(ctx)):
        try:
            text = (ctx.repo_root / rel).read_text(encoding="utf-8-sig")
        except OSError as exc:
            findings.append(
                Finding(
                    rule_id="SL1",
                    severity=Severity.ERROR,
                    message=f"could not read coverage scorecard: {exc}",
                    locator=rel,
                )
            )
            continue

        for m in _status_table_rows(text):
            kpi = m.group("kpi").strip()
            contract = m.group("contract")
            status_raw = m.group("status")
            blocker = m.group("blocker")
            status = _norm(status_raw)

            # C4: no <number>% token anywhere in the row.
            if _PERCENT_RE.search(m.group(0)):
                findings.append(
                    Finding(
                        rule_id="SL1",
                        severity=Severity.ERROR,
                        message=(
                            f"coverage scorecard row '{kpi}' contains a percentage/"
                            "score token; coverage is status + named blocker, never a "
                            "number (rule #9)"
                        ),
                        locator=rel,
                    )
                )

            # C1: status must be in the closed enum.
            if status not in _ENUM:
                findings.append(
                    Finding(
                        rule_id="SL1",
                        severity=Severity.ERROR,
                        message=(
                            f"coverage scorecard row '{kpi}' has status "
                            f"'{status_raw.strip()}' outside the allowed set "
                            "(Covered / Blocked -- missing field / Blocked -- needs "
                            "business definition / Planned / Out of scope)"
                        ),
                        locator=rel,
                    )
                )
                # enum unknown -> the status-conditional checks below don't apply
                continue

            # C2: a Blocked -- ... row must name a specific blocker.
            if status.startswith("blocked") and _is_dash(blocker):
                findings.append(
                    Finding(
                        rule_id="SL1",
                        severity=Severity.ERROR,
                        message=(
                            f"coverage scorecard row '{kpi}' is Blocked but names no "
                            "specific blocker (missing field or undecided policy)"
                        ),
                        locator=rel,
                    )
                )

            # C3: a Covered row's contract path must resolve to a tracked file.
            if status == "covered":
                cm = _CONTRACT_RE.search(contract)
                if not cm or cm.group(0) not in tracked:
                    findings.append(
                        Finding(
                            rule_id="SL1",
                            severity=Severity.ERROR,
                            message=(
                                f"coverage scorecard row '{kpi}' is Covered but its "
                                "contract path does not resolve to a tracked "
                                "contracts/<file>.md"
                            ),
                            locator=rel,
                        )
                    )
    return findings
