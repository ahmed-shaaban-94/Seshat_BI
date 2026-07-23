"""Offline PBIR binding-resolution validator (#454).

Walks every JSON document under a report's ``definition/`` tree for bound field
references -- ``Column``/``Measure`` wrappers carrying an ``Expression ->
SourceRef`` and a ``Property`` (queryState projections, filters, sorts alike;
one recursive walker, no bucket enumeration) -- and resolves each
``Entity``+``Property`` pair against a symbol table built from the semantic
model's TMDL. Every unresolved binding is exactly one Power BI Desktop
"Something's wrong with one or more fields" error card caught BEFORE a human
opens Desktop.

WHY THIS IS A READ-ONLY CLI VERB (same precedent as ``pbir-validate-blueprint``)
--------------------------------------------------------------------------------
The delivery default for new capabilities is a SKILL, not a CLI verb (ratified
Option-B, ``docs/roadmap/decisions/cli-verbs-vs-skill-driven.md``). This module
is a CHECK SURFACE that POLICES what writers already produced -- the US7
compiler, pbi-cli scaffolding, or a human Desktop build -- exactly the narrow
exception R1/R2 and ``pbir-validate-blueprint`` established. Unlike that
validator it needs NO blueprint or binding map: the reported real-world case
(a Desktop-owned report over a Get-Data model) has neither, only the report
and model trees themselves.

READ-ONLY, GRANTS NO APPROVAL
--------------------------------------------------------------------------------
Opens nothing for write, never mutates the Decision Store, never sets a
readiness stage. ``BindingValidationResult.grants_approval`` is always False
and the shape carries no member that could ever flip it. Status vocabulary is
the shipped four-status subset (``pass`` / ``warning`` / ``blocked``), never a
numeric score.

RESOLUTION SEMANTICS
--------------------------------------------------------------------------------
- Case-insensitive: Power BI object names are case-insensitive; exact-case
  comparison would fabricate error cards Desktop never shows.
- ``SourceRef`` resolves directly (``{"Entity": e}``) or through the
  document-wide alias table collected from ``"From": [{"Name": n, "Entity": e}]``
  lists; an unresolvable alias is SKIPPED, never invented into a finding.
- Wrappers other than ``Column``/``Measure`` (``HierarchyLevel``, variations,
  conditional-formatting expressions) are out of scope for this increment.
- A model column bound under a ``Measure`` wrapper (or vice versa) resolves --
  Desktop renders it "by luck" -- but is reported as a ``projection_kind``
  WARNING: the detection side of #456; the authoring fix lives in the
  generator, so the validator warns without blocking.

FAIL-CLOSED (the #453 lesson: never a silent "0 findings" pass over nothing)
--------------------------------------------------------------------------------
Zero visuals under the report, zero TMDL tables under the model, or ANY
unreadable/unparseable definition file is a ``blocked`` finding naming the
path -- not a skip. A validator that silently validates nothing gives false
comfort, which is the exact failure mode it exists to remove.

TMDL NOTE: a single ``model.tmdl`` may carry SEVERAL table blocks (Desktop
sometimes writes this). ``tmdl.parse_tmdl`` attributes every block in a file to
the FIRST table header, so this module splits column-0 ``table`` headers into
segments first and delegates each segment to ``parse_tmdl`` -- the shipped
parser is reused, never reimplemented.

No pbi-cli, no live Power BI, no network -- stdlib ``json``/``pathlib``/``re``/
``difflib`` plus the shipped TMDL parser.
"""

from __future__ import annotations

import difflib
import json
import re
from pathlib import Path
from typing import Any, Iterator, NamedTuple

from .tmdl import parse_tmdl


class BindingFinding(NamedTuple):
    """One binding defect: evidence only, grants nothing."""

    dimension: str  # "unknown_entity" | "unresolved_field" | "projection_kind"
    #                 | "unparseable_json" | "unreadable_source"
    locator: str  # where (report-relative-ish path, or the offending dir)
    message: str  # human-readable statement naming entity/property/cause


class BindingValidationResult(NamedTuple):
    """The validator's verdict. Read-only evidence, never an approval grant --
    ``grants_approval`` is ALWAYS False; no member on this shape can flip it."""

    status: str  # "pass" | "warning" | "blocked"; worst finding rolls up
    unresolved: tuple[BindingFinding, ...]  # blocked-class findings
    kind_mismatches: tuple[BindingFinding, ...]  # warning-class (#456 shape)
    evidence: tuple[str, ...]
    grants_approval: bool = False


# --------------------------------------------------------------------------- #
# Model side: TMDL -> symbol table
# --------------------------------------------------------------------------- #


class _ModelTable(NamedTuple):
    name: str  # exact-case, for messages
    columns: dict[str, str]  # casefold -> exact-case
    measures: dict[str, str]


_TABLE_HEADER = re.compile(r"table\s+\S")


def _split_table_segments(text: str) -> list[str]:
    """Split one TMDL file into per-table texts at column-0 ``table`` headers.

    ``parse_tmdl`` reads a SINGLE-table file: on a multi-table ``model.tmdl``
    it would attribute every measure/column block to the first header. Files
    with no table header (``relationships.tmdl``, ``expressions.tmdl``) yield
    no segments.
    """
    lines = text.lstrip("﻿").splitlines()
    starts = [
        i
        for i, line in enumerate(lines)
        if line[:1] not in (" ", "\t") and _TABLE_HEADER.match(line.strip())
    ]
    return [
        "\n".join(lines[start : starts[idx + 1] if idx + 1 < len(starts) else None])
        for idx, start in enumerate(starts)
    ]


def _model_symbol_table(
    model_dir: Path,
) -> tuple[dict[str, _ModelTable], list[BindingFinding]]:
    """``{casefold(table): _ModelTable}`` from every ``definition/**/*.tmdl``.

    An UNREADABLE tmdl file is a blocker, not a skip: silently shrinking the
    symbol table would turn every binding into that file's tables into a false
    ``unknown_entity`` -- a validator must fail closed, never guess smaller.
    """
    tables: dict[str, _ModelTable] = {}
    blockers: list[BindingFinding] = []
    definition = model_dir / "definition"
    if not definition.is_dir():
        return tables, blockers
    for tmdl_path in sorted(definition.rglob("*.tmdl")):
        try:
            text = tmdl_path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            blockers.append(
                BindingFinding(
                    dimension="unreadable_source",
                    locator=str(tmdl_path),
                    message=(
                        f"model definition file {tmdl_path.name} is unreadable -- "
                        f"validation blocked (fail closed): an unread table file "
                        f"would misreport its bindings as unknown entities"
                    ),
                )
            )
            continue
        for segment in _split_table_segments(text):
            parsed = parse_tmdl(segment)
            if parsed is None:
                continue
            tables[parsed.name.casefold()] = _ModelTable(
                name=parsed.name,
                columns={c.name.casefold(): c.name for c in parsed.columns},
                measures={m.name.casefold(): m.name for m in parsed.measures},
            )
    return tables, blockers


# --------------------------------------------------------------------------- #
# Report side: definition JSON -> bound field references
# --------------------------------------------------------------------------- #


class _FieldRef(NamedTuple):
    path: Path
    kind: str  # "Column" | "Measure" (the wrapper key)
    entity: str  # resolved entity name (direct or via From-alias)
    prop: str


def _iter_dicts(node: Any) -> Iterator[dict[str, Any]]:
    """Every dict anywhere in a parsed JSON document, depth-first."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _iter_dicts(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_dicts(item)


def _collect_aliases(doc: Any) -> dict[str, str]:
    """Document-wide ``{alias: entity}`` from every ``"From"`` declaration list."""
    aliases: dict[str, str] = {}
    for node in _iter_dicts(doc):
        entries = node.get("From")
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if (
                isinstance(entry, dict)
                and isinstance(entry.get("Name"), str)
                and isinstance(entry.get("Entity"), str)
            ):
                aliases[entry["Name"]] = entry["Entity"]
    return aliases


def _wrapped_ref(node: dict[str, Any], kind: str) -> tuple[str | None, str] | None:
    """The ``(entity_or_None, property)`` of a ``Column``/``Measure`` wrapper on
    this node, with the entity still unresolved when referenced by alias --
    returned as ``(None, prop)`` only when no direct Entity is present (the
    caller resolves the alias). ``None`` when the node carries no such wrapper."""
    inner = node.get(kind)
    if not isinstance(inner, dict):
        return None
    prop = inner.get("Property")
    expression = inner.get("Expression")
    if not isinstance(prop, str) or not isinstance(expression, dict):
        return None
    source_ref = expression.get("SourceRef")
    if not isinstance(source_ref, dict):
        return None
    entity = source_ref.get("Entity")
    if isinstance(entity, str):
        return entity, prop
    if isinstance(source_ref.get("Source"), str):
        return None, prop  # alias resolved by the caller via _collect_aliases
    return None


def _refs_in_doc(doc: Any, path: Path) -> list[_FieldRef]:
    """Every alias-resolved ``Column``/``Measure`` field reference in one
    document. An unresolvable alias is skipped -- never invented into a
    finding (the walker only reports what it can actually ground)."""
    aliases = _collect_aliases(doc)
    refs: list[_FieldRef] = []
    for node in _iter_dicts(doc):
        for kind in ("Column", "Measure"):
            wrapped = _wrapped_ref(node, kind)
            if wrapped is None:
                continue
            entity, prop = wrapped
            if entity is None:
                inner = node[kind]
                alias = inner["Expression"]["SourceRef"].get("Source")
                entity = aliases.get(alias) if isinstance(alias, str) else None
                if entity is None:
                    continue  # unresolvable alias: skip, don't fabricate
            refs.append(_FieldRef(path=path, kind=kind, entity=entity, prop=prop))
    return refs


def _rel_locator(base_dir: Path, path: Path) -> str:
    try:
        return str(path.relative_to(base_dir.parent))
    except ValueError:
        return str(path)


def _walk_report(
    report_dir: Path,
) -> tuple[list[_FieldRef], list[BindingFinding]]:
    """All field references + fail-closed blockers across ``definition/**/*.json``.

    A corrupt or unreadable definition JSON is a blocker, not a skip: a broken
    ``visual.json`` is itself an error-card source, and silently skipping it
    would be the #453 fail-open pattern all over again.
    """
    refs: list[_FieldRef] = []
    blockers: list[BindingFinding] = []
    definition = report_dir / "definition"
    if not definition.is_dir():
        return refs, blockers
    for json_path in sorted(definition.rglob("*.json")):
        locator = _rel_locator(report_dir, json_path)
        try:
            text = json_path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            blockers.append(
                BindingFinding(
                    dimension="unreadable_source",
                    locator=locator,
                    message=(
                        "report definition file is unreadable -- "
                        "validation blocked (fail closed)"
                    ),
                )
            )
            continue
        try:
            doc = json.loads(text)
        except json.JSONDecodeError as exc:
            blockers.append(
                BindingFinding(
                    dimension="unparseable_json",
                    locator=locator,
                    message=(
                        f"report definition file is not valid JSON ({exc.msg}, "
                        f"line {exc.lineno}) -- a corrupt definition is itself "
                        f"an error-card source; validation blocked (fail closed)"
                    ),
                )
            )
            continue
        refs.extend(_refs_in_doc(doc, json_path))
    return refs, blockers


# --------------------------------------------------------------------------- #
# Resolution
# --------------------------------------------------------------------------- #


def _dedupe(refs: list[_FieldRef]) -> list[_FieldRef]:
    seen: set[tuple[Path, str, str, str]] = set()
    out: list[_FieldRef] = []
    for ref in refs:
        key = (ref.path, ref.kind, ref.entity.casefold(), ref.prop.casefold())
        if key in seen:
            continue
        seen.add(key)
        out.append(ref)
    return out


def _unresolved_field_finding(
    ref: _FieldRef, table: _ModelTable, locator: str
) -> BindingFinding:
    """The blocked finding for a property missing from its entity, naming the
    nearest model field: a governed rename / PII mask (the ex-2 defect --
    ``person_name`` vs the gold model's ``staff_name_masked``) is the common
    cause, and the near-match makes it visible without opening Desktop."""
    candidates = [*table.columns.values(), *table.measures.values()]
    near = difflib.get_close_matches(ref.prop, candidates, n=1)
    hint = f"; nearest model field: {near[0]!r}" if near else ""
    return BindingFinding(
        dimension="unresolved_field",
        locator=locator,
        message=(
            f"{ref.entity}[{ref.prop}] is bound in the report but {ref.prop!r} "
            f"is not a column or measure on model table {table.name!r}{hint} "
            f"-- a governed rename or PII mask is the common cause"
        ),
    )


def _kind_mismatch_finding(
    ref: _FieldRef, table: _ModelTable, locator: str
) -> BindingFinding:
    actual = "COLUMN" if ref.kind == "Measure" else "MEASURE"
    wanted = "Column" if ref.kind == "Measure" else "Measure"
    return BindingFinding(
        dimension="projection_kind",
        locator=locator,
        message=(
            f"{ref.entity}[{ref.prop}] is bound as a {ref.kind} projection but "
            f"is a model {actual} on {table.name!r} -- emit a {wanted} "
            f"projection instead (renders by luck; semantically wrong, #456)"
        ),
    )


def _resolve_ref(
    ref: _FieldRef,
    tables: dict[str, _ModelTable],
    report_dir: Path,
) -> tuple[BindingFinding | None, BindingFinding | None]:
    """``(blocked_finding, warning_finding)`` for one reference; both ``None``
    when the binding resolves cleanly with the right projection kind."""
    locator = _rel_locator(report_dir, ref.path)
    table = tables.get(ref.entity.casefold())
    if table is None:
        return (
            BindingFinding(
                dimension="unknown_entity",
                locator=locator,
                message=(
                    f"field reference {ref.entity}[{ref.prop}] names entity "
                    f"{ref.entity!r}, which is not a table in the model"
                ),
            ),
            None,
        )
    prop_key = ref.prop.casefold()
    is_column = prop_key in table.columns
    is_measure = prop_key in table.measures
    if not is_column and not is_measure:
        return _unresolved_field_finding(ref, table, locator), None
    if (ref.kind == "Measure" and is_column and not is_measure) or (
        ref.kind == "Column" and is_measure and not is_column
    ):
        return None, _kind_mismatch_finding(ref, table, locator)
    return None, None


# --------------------------------------------------------------------------- #
# Entry points
# --------------------------------------------------------------------------- #


def _fail_closed_blockers(
    report_dir: Path,
    model_dir: Path,
    tables: dict[str, _ModelTable],
) -> list[BindingFinding]:
    """The "nothing to validate" blockers: zero visuals or zero model tables is
    an ERROR naming the path, never a vacuous pass (the #453 lesson)."""
    blockers: list[BindingFinding] = []
    visuals = sorted(
        (report_dir / "definition" / "pages").glob("*/visuals/*/visual.json")
    )
    if not visuals:
        blockers.append(
            BindingFinding(
                dimension="unreadable_source",
                locator=str(report_dir),
                message=(
                    f"no visuals found under {report_dir}/definition/pages -- "
                    f"nothing to validate (fail closed); check the --report path"
                ),
            )
        )
    if not tables:
        blockers.append(
            BindingFinding(
                dimension="unreadable_source",
                locator=str(model_dir),
                message=(
                    f"no TMDL table definitions found under {model_dir}/definition "
                    f"-- nothing to resolve against (fail closed); check the "
                    f"--model path"
                ),
            )
        )
    return blockers


def validate_bindings(*, report_dir: Path, model_dir: Path) -> BindingValidationResult:
    """Resolve every bound field reference in the report against the model.

    READ-ONLY: opens nothing for write, never mutates the Decision Store,
    never sets a readiness stage. Returns evidence + findings only --
    ``grants_approval`` is always False.
    """
    report_dir = Path(report_dir)
    model_dir = Path(model_dir)

    tables, model_blockers = _model_symbol_table(model_dir)
    refs, report_blockers = _walk_report(report_dir)
    blockers = [
        *_fail_closed_blockers(report_dir, model_dir, tables),
        *model_blockers,
        *report_blockers,
    ]

    unresolved: list[BindingFinding] = list(blockers)
    kind_mismatches: list[BindingFinding] = []
    deduped = _dedupe(refs)
    if tables:  # an empty model already blocked; don't cascade unknown_entity
        for ref in deduped:
            blocked, warned = _resolve_ref(ref, tables, report_dir)
            if blocked is not None:
                unresolved.append(blocked)
            if warned is not None:
                kind_mismatches.append(warned)

    evidence = (
        f"PBIR report dir: {report_dir}",
        f"semantic model dir: {model_dir}",
        f"{len(deduped)} field reference(s) checked against "
        f"{len(tables)} model table(s)",
    )
    if unresolved:
        status = "blocked"
    elif kind_mismatches:
        status = "warning"
    else:
        status = "pass"
    return BindingValidationResult(
        status=status,
        unresolved=tuple(unresolved),
        kind_mismatches=tuple(kind_mismatches),
        evidence=evidence,
        grants_approval=False,
    )


def pbir_validate_bindings_main(args: object) -> int:
    """CLI entry: ``seshat pbir-validate-bindings``. Read-only: prints the
    resolution report to stdout and exits non-zero on any blocked finding --
    it never writes a file and never grants any readiness stage."""
    result = validate_bindings(
        report_dir=Path(args.report),  # type: ignore[attr-defined]
        model_dir=Path(args.model),  # type: ignore[attr-defined]
    )
    print(f"status: {result.status}")
    for finding in result.unresolved:
        print(
            f"[unresolved] {finding.dimension}: {finding.message} ({finding.locator})"
        )
    for finding in result.kind_mismatches:
        print(f"[kind] {finding.dimension}: {finding.message} ({finding.locator})")
    for line in result.evidence:
        print(f"evidence: {line}")
    print(
        "note: this is a read-only validation report; it grants no approval "
        "and never sets a readiness stage."
    )
    return 1 if result.status == "blocked" else 0
