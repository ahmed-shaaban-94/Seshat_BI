"""Read-only Dashboard Gap Detector (spec 117).

A PRE-DESIGN inventory: given a HUMAN-SUPPLIED page-intent for ONE subject area
(the business questions the page must answer, each naming its required metric(s)
and slicing dimension(s) -- the same Principle-V input ``dashboard-design``
requires), classify each required item against the target table's committed
evidence and emit, per item, ONE categorical status from SL1's closed five-value
vocabulary plus a NAMED blocker where the item blocks design. It answers, before
the first visual is placed: which required things already exist and are approved,
and which are missing, unapproved, or awaiting an owner decision.

Committed evidence read (never written):
- ``mappings/<table>/metrics/*.yaml``       -- metric contract + ``readiness.status``
- ``mappings/<table>/source-map.yaml``       -- the ``gold_star`` dimension inventory
- ``mappings/<table>/unresolved-questions.md`` -- open owner decisions (structured rows)

Scope wall (load-bearing):
- INVENTS nothing: the required set is the human page-intent; a required item with
  no committed backing is a GAP to REPORT, never a thing to synthesize.
- WRITES NOTHING, records no ``pass``, grants no approval, moves no stage. No
  file-write path exists here (structural, grep-verifiable).
- Emits a CATEGORICAL status from SL1's five, NEVER a numeric score/percentage/
  count (hard rule #9).
- Adds NO ``retail check`` rule and is NOT SL1's runtime -- it reuses SL1's status
  VOCABULARY only (``coverage_status``).
- Designs nothing, executes nothing; opens no DB/PBIP/network.
- Generic (Principle VII): table-parameterized; no hardcoded names/keys.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .coverage_status import (
    BLOCKED_MISSING_FIELD,
    BLOCKED_NEEDS_DEFINITION,
    COVERED,
    OUT_OF_SCOPE,
    PLANNED,
)

_ANSWERED = "answered"


def _load_yaml_mapping(path: Path) -> dict[str, Any] | None:
    """Load a YAML mapping; None on any read/parse failure (shipped-surface idiom)."""
    import yaml

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return None


# --------------------------------------------------------------------------- #
# page-intent (the human-supplied required set) -- read, never authored
# --------------------------------------------------------------------------- #
def _str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(v).strip() for v in value if str(v).strip()]


def _norm_metric(entry: object) -> dict[str, Any]:
    if isinstance(entry, dict):
        return {
            "name": str(entry.get("name", "")).strip(),
            "depends_on": _str_list(entry.get("depends_on")),
        }
    return {"name": str(entry).strip(), "depends_on": []}


def _question_items(q: dict[str, Any]) -> list[dict[str, Any]]:
    """The typed required items (metric / dimension) for ONE business question."""
    question = str(q.get("question", "")).strip()
    out_of_scope = bool(q.get("out_of_scope", False))
    metrics = [_norm_metric(e) for e in (q.get("metrics") or [])]
    items = [
        {"kind": "metric", "question": question, "out_of_scope": out_of_scope, **m}
        for m in metrics
        if m["name"]
    ]
    items += [
        {
            "kind": "dimension",
            "question": question,
            "out_of_scope": out_of_scope,
            "name": name,
            "depends_on": [],
        }
        for name in _str_list(q.get("dimensions"))
    ]
    return items


def _required_items(page_intent: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten the page-intent into typed required items (metric / dimension)."""
    questions = page_intent.get("questions")
    if not isinstance(questions, list):
        return []
    items: list[dict[str, Any]] = []
    for q in questions:
        if isinstance(q, dict):
            items.extend(_question_items(q))
    return items


# --------------------------------------------------------------------------- #
# committed evidence readers (None == input absent/unreadable)
# --------------------------------------------------------------------------- #
def _load_contracts(metrics_dir: Path) -> dict[str, dict[str, Any]] | None:
    if not metrics_dir.is_dir():
        return None
    contracts: dict[str, dict[str, Any]] = {}
    for path in sorted(metrics_dir.glob("*.yaml")):
        data = _load_yaml_mapping(path)
        if data is None:
            continue
        name = str(data.get("name", path.stem)).strip()
        readiness = data.get("readiness")
        status = ""
        if isinstance(readiness, dict):
            status = str(readiness.get("status", "")).strip()
        binds = data.get("binds_to")
        cols = _str_list(binds.get("columns")) if isinstance(binds, dict) else []
        contracts[name] = {"status": status, "columns": cols, "rel": path.name}
    return contracts


def _collect_gold(source_map: dict[str, Any]) -> tuple[set[str], set[str]]:
    """Return (dimension tokens, gold columns) from the committed gold_star.

    Dimension tokens = every attribute + degenerate dimension + each dimension
    table name (full + bare) + the date-dimension name (full + bare). Gold columns
    = fact measures + attributes + degenerate dimensions (the binds_to check set).
    """
    star = source_map.get("gold_star")
    dims: set[str] = set()
    cols: set[str] = set()
    if not isinstance(star, dict):
        return dims, cols
    fact = star.get("fact")
    if isinstance(fact, dict):
        cols.update(_str_list(fact.get("measures")))
    for dim in star.get("dimensions") or []:
        if not isinstance(dim, dict):
            continue
        attrs = _str_list(dim.get("attributes"))
        dims.update(attrs)
        cols.update(attrs)
        dims.update(_name_tokens(dim.get("name")))
    degenerate = _str_list(star.get("degenerate_dimensions"))
    dims.update(degenerate)
    cols.update(degenerate)
    date_dim = star.get("date_dimension")
    if isinstance(date_dim, dict):
        dims.update(_name_tokens(date_dim.get("name")))
    return dims, cols


def _name_tokens(name: object) -> set[str]:
    """A dimension table name as both its full and bare (post-``.``) forms."""
    if not isinstance(name, str) or not name.strip():
        return set()
    full = name.strip()
    return {full, full.split(".")[-1]}


def _open_decisions(text: str) -> dict[str, dict[str, str]]:
    """Parse unresolved-questions.md into {row_id: {owner, question, open}}.

    A row is OPEN when its structured ``Status`` cell is not ``answered`` AND the
    doc-level ``Gate status`` is not ``CLEARED``. Openness is read from the
    structured column only -- the free-text question prose is never scored.
    """
    gate_cleared = _gate_cleared(text)
    rows: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        cells = _table_cells(line)
        if cells is None or len(cells) < 6:
            continue
        row_id = cells[0]
        if row_id.lower() in ("id", "") or set(row_id) <= {"-", ":"}:
            continue
        status = cells[5].lower()
        rows[row_id] = {
            "owner": cells[3],
            "question": cells[1],
            "open": "" if (gate_cleared or status == _ANSWERED) else "open",
        }
    return rows


def _gate_cleared(text: str) -> bool:
    for line in text.splitlines():
        low = line.lower()
        if "gate status" in low and "cleared" in low:
            return True
    return False


def _table_cells(line: str) -> list[str] | None:
    if "|" not in line:
        return None
    raw = line.strip().strip("|").split("|")
    if len(raw) < 2:
        return None
    return [c.strip().strip("`").strip() for c in raw]


# --------------------------------------------------------------------------- #
# classification -- one status from SL1's five, plus a named blocker
# --------------------------------------------------------------------------- #
def _blocker(status: str, blocker: str, path: str) -> dict[str, str]:
    return {"status": status, "blocker": blocker, "evidence_path": path}


def _open_dep(
    item: dict[str, Any], decisions: dict[str, dict[str, str]] | None
) -> dict | None:
    """The first depended-on decision row that is OPEN, if any."""
    if decisions is None:
        return None
    for dep in item["depends_on"]:
        row = decisions.get(dep)
        if row and row["open"]:
            return {"id": dep, **row}
    return None


def _classify_metric(
    item: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, str]:
    metrics_rel = f"mappings/{ctx['table']}/metrics/"
    questions_rel = f"mappings/{ctx['table']}/unresolved-questions.md"
    if item["out_of_scope"]:
        return _blocker(OUT_OF_SCOPE, "human-declared outside this table's domain", "")
    if item["depends_on"] and ctx["decisions"] is None:
        return _blocker(
            BLOCKED_NEEDS_DEFINITION,
            "cannot verify owner decision -- file not found",
            questions_rel,
        )
    dep = _open_dep(item, ctx["decisions"])
    if dep is not None:
        return _blocker(
            BLOCKED_NEEDS_DEFINITION,
            f"open owner decision {dep['id']} -- {dep['owner']} must answer: "
            f'"{dep["question"]}"',
            questions_rel,
        )
    if ctx["contracts"] is None:
        return _blocker(
            BLOCKED_NEEDS_DEFINITION,
            "cannot verify metric contract -- metrics/ not found",
            metrics_rel,
        )
    contract = ctx["contracts"].get(item["name"])
    if contract is None:
        return _blocker(
            PLANNED,
            f"no metric contract drafted for '{item['name']}'",
            f"{metrics_rel}{item['name']}.yaml",
        )
    rel = f"{metrics_rel}{contract['rel']}"
    if contract["status"] != "pass":
        return _blocker(
            BLOCKED_NEEDS_DEFINITION,
            f"contract present but readiness.status='{contract['status']}' (not pass)",
            rel,
        )
    missing = _missing_bound_columns(contract, ctx)
    if missing:
        return _blocker(
            BLOCKED_MISSING_FIELD,
            f"contract is pass but binds_to column(s) {missing} absent from gold_star",
            rel,
        )
    return _blocker(COVERED, "", rel)


def _missing_bound_columns(contract: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    """binds_to columns not present in the committed gold_star (intra-artifact
    disagreement). Skipped when the gold star could not be read."""
    if ctx["gold_cols"] is None:
        return []
    return [c for c in contract["columns"] if c not in ctx["gold_cols"]]


def _classify_dimension(item: dict[str, Any], ctx: dict[str, Any]) -> dict[str, str]:
    source_rel = f"mappings/{ctx['table']}/source-map.yaml"
    if item["out_of_scope"]:
        return _blocker(OUT_OF_SCOPE, "human-declared outside this table's domain", "")
    if ctx["dim_tokens"] is None:
        return _blocker(
            BLOCKED_MISSING_FIELD,
            "cannot verify dimension -- source-map.yaml gold_star not found",
            source_rel,
        )
    if item["name"] in ctx["dim_tokens"]:
        return _blocker(COVERED, "", source_rel)
    return _blocker(
        BLOCKED_MISSING_FIELD,
        f"dimension '{item['name']}' absent from gold_star",
        source_rel,
    )


def _classify(item: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    verdict = (
        _classify_metric(item, ctx)
        if item["kind"] == "metric"
        else _classify_dimension(item, ctx)
    )
    return {
        "kind": item["kind"],
        "name": item["name"],
        "question": item["question"],
        **verdict,
    }


# --------------------------------------------------------------------------- #
# compose (read-only; writes nothing)
# --------------------------------------------------------------------------- #
def _document_gaps(
    tdir: Path, table: str, items: list[dict[str, Any]], ctx: dict[str, Any]
) -> list[str]:
    """Name each RELEVANT missing committed input (never presented as 'no gaps')."""
    gaps: list[str] = []
    has_metric = any(i["kind"] == "metric" for i in items)
    has_dimension = any(i["kind"] == "dimension" for i in items)
    has_dep = any(i["depends_on"] for i in items)
    if has_metric and ctx["contracts"] is None:
        gaps.append(f"mappings/{table}/metrics/ not found -- metric items unverifiable")
    if has_dimension and ctx["dim_tokens"] is None:
        gaps.append(
            f"mappings/{table}/source-map.yaml not found -- dimensions unverifiable"
        )
    if has_dep and ctx["decisions"] is None:
        gaps.append(
            f"mappings/{table}/unresolved-questions.md not found -- "
            "owner decisions unverifiable (NOT the same as 'no open decisions')"
        )
    return gaps


def build_gap_inventory(
    repo_root: Path | str, table: str, page_intent_path: Path | str | None
) -> dict[str, Any]:
    """Compose the read-only pre-design gap inventory for one table."""
    root = Path(repo_root)
    tdir = root / "mappings" / table
    intent_rel = str(page_intent_path) if page_intent_path else "(none supplied)"

    page_intent = (
        _load_yaml_mapping(Path(page_intent_path)) if page_intent_path else None
    )
    if page_intent is None:
        return {
            "table": table,
            "page_intent_path": intent_rel,
            "items": [],
            "document_gaps": [f"page-intent not found or unreadable at {intent_rel}"],
            "read_only": True,
        }

    contracts = _load_contracts(tdir / "metrics")
    source_map = _load_yaml_mapping(tdir / "source-map.yaml")
    q_text = _read_text(tdir / "unresolved-questions.md")
    dim_tokens, gold_cols = _collect_gold(source_map) if source_map else (None, None)
    ctx = {
        "table": table,
        "contracts": contracts,
        "dim_tokens": dim_tokens,
        "gold_cols": gold_cols,
        "decisions": _open_decisions(q_text) if q_text is not None else None,
    }

    items = _required_items(page_intent)
    classified = [_classify(item, ctx) for item in items]
    return {
        "table": table,
        "page_intent_path": intent_rel,
        "items": classified,
        "document_gaps": _document_gaps(tdir, table, items, ctx),
        "read_only": True,
    }


# --------------------------------------------------------------------------- #
# render (ASCII, no glyphs, no numeric token -- FR-011/FR-015)
# --------------------------------------------------------------------------- #
_HEADER = (
    "Before you design this page: which required things already exist and are\n"
    "approved, and which are missing, unapproved, or awaiting an owner decision?\n"
    "Read-only pre-design inventory -- it records nothing, grants no approval,\n"
    "moves no stage, and emits no score. A gap is a status + named blocker."
)


def _item_line(item: dict[str, Any]) -> str:
    tail = "" if item["status"] == COVERED else f" -- {item['blocker']}"
    cite = f" (`{item['evidence_path']}`)" if item["evidence_path"] and tail else ""
    return f"- [{item['status']}] {item['kind']} `{item['name']}`{tail}{cite}"


def _inventory_section(items: list[dict[str, Any]]) -> list[str]:
    lines = ["## Design-blocking gap inventory", ""]
    if not items:
        return lines + ["No required items were classified."]
    seen_q: list[str] = []
    for item in items:
        q = item["question"] or "(unattributed)"
        if q not in seen_q:
            seen_q.append(q)
            lines.append(f"### {q}")
        lines.append(_item_line(item))
    return lines


def _document_gap_section(gaps: list[str]) -> list[str]:
    if not gaps:
        return []
    return ["", "## Inputs not available", ""] + [f"- {g}" for g in gaps]


def _closing(view: dict[str, Any]) -> list[str]:
    blocked = [i for i in view["items"] if i["status"] != COVERED]
    if view["items"] and not blocked and not view["document_gaps"]:
        return ["", "Nothing blocks design: every required item is Covered."]
    return []


def render_view(view: dict[str, Any]) -> str:
    """Render the ASCII read-only inventory (UTF-8 no BOM). Writes nothing."""
    lines = [f"# Dashboard Gap Detector -- {view['table']}", "", _HEADER, ""]
    lines += [f"page-intent: `{view['page_intent_path']}`", ""]
    lines += _inventory_section(view["items"])
    lines += _document_gap_section(view["document_gaps"])
    lines += _closing(view)
    return "\n".join(lines) + "\n"
