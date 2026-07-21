"""Derive the governed dbt star from an approved source map (pure, no I/O).

Everything here is derivable from the committed ``source-map.yaml`` alone:
the fact + dimensions from ``gold_star`` (issue #331 tags supply the fact's
grain key and money measures the built graph cannot enumerate), the staging
columns from the kept ``columns[]`` rows, and the exact parity-assertion set
``evidence._validate_parity_set`` requires. Names are normalized the same way
``fact_semantics._fact_name`` does -- a ``gold.``-qualified map name maps to the
bare dbt MODEL name -- so the generated models match what the manifest knows.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from seshat.dbt.contracts import FactBinding, GovernanceError

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class ColumnSpec:
    """One model output column: either cited to source columns or derived."""

    name: str
    source_columns: tuple[str, ...] = ()
    derivation: str | None = None
    data_type: str = "text"


@dataclass(frozen=True, slots=True)
class ModelSpec:
    """One governed dbt model (staging, dimension, fact, or the parity audit)."""

    name: str
    layer: str
    grain: str
    business_key: tuple[str, ...]
    columns: tuple[ColumnSpec, ...]


@dataclass(frozen=True, slots=True)
class ParityRow:
    """One governed parity assertion the audit model emits."""

    assertion_id: str
    assertion_class: str
    subject: str
    tolerance: str


@dataclass(frozen=True, slots=True)
class MapSource:
    """The committed source map an approved scaffold is derived from.

    Bundles the parsed ``document`` with its repo-relative path and committed git
    blob revision so the derivation takes one cohesive input, not three loose
    positional arguments.
    """

    document: dict
    source_map: str
    source_map_revision: str


@dataclass(frozen=True, slots=True)
class ScaffoldPlan:
    """The complete derived model set for one governed table."""

    table_id: str
    source_table: str
    source_map: str
    source_map_revision: str
    fact: FactBinding
    staging: ModelSpec
    dimensions: tuple[ModelSpec, ...]
    fact_model: ModelSpec
    audit: ModelSpec
    parity: tuple[ParityRow, ...]


class ScaffoldError(GovernanceError):
    """A committed source map cannot be turned into a governed model set."""

    def __init__(self, message: str) -> None:
        super().__init__("DBT_SCAFFOLD_INVALID", message)


def _normalized_name(value: object, label: str) -> str:
    """The bare dbt MODEL name for a (possibly schema-qualified) map relation."""
    normalized = value.rsplit(".", 1)[-1] if isinstance(value, str) else None
    if not isinstance(normalized, str) or not _IDENTIFIER.fullmatch(normalized):
        raise ScaffoldError(f"{label} is not a lowercase relation identifier")
    return normalized


def _require_identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ScaffoldError(f"{label} is not a lowercase identifier")
    return value


def _string_list(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list):
        return tuple(item for item in value if isinstance(item, str))
    return ()


@dataclass(frozen=True, slots=True)
class _PlanInputs:
    """Resolved identity + the raw ``gold_star`` section for one table."""

    table_id: str
    source_table: str
    source_map: str
    source_map_revision: str
    fact: FactBinding
    fact_grain: str
    gold_star: dict


def _kept_columns(document: dict) -> tuple[dict, ...]:
    """The ``keep``/``derive`` column rows a staging model must reproduce."""
    rows = document.get("columns")
    if not isinstance(rows, list):
        return ()
    return tuple(
        row
        for row in rows
        if isinstance(row, dict) and row.get("decision") in {"keep", "derive"}
    )


def _staging_column(row: dict, source_table: str) -> ColumnSpec | None:
    """A staging column ALWAYS cites its bronze source; a row without a usable
    ``source_name``/``rename_to`` is skipped (it cannot be a valid citation)."""
    source = row.get("source_name")
    if not isinstance(source, str) or not source:
        return None
    rename = row.get("rename_to")
    name = rename if isinstance(rename, str) and rename else source
    if not _IDENTIFIER.fullmatch(name):
        return None
    silver_type = row.get("silver_type")
    return ColumnSpec(
        name=name,
        source_columns=(f"bronze.{source_table}.{source}",),
        derivation=None,
        data_type=silver_type
        if isinstance(silver_type, str) and silver_type
        else "text",
    )


def _staging_model(inputs: _PlanInputs, document: dict) -> ModelSpec:
    columns = tuple(
        spec
        for row in _kept_columns(document)
        if (spec := _staging_column(row, inputs.source_table)) is not None
    )
    if not columns:
        raise ScaffoldError("no kept source columns to stage; the map keeps nothing")
    return ModelSpec(
        name=f"stg_{inputs.table_id}",
        layer="staging",
        grain=inputs.fact_grain,
        business_key=inputs.fact.business_key,
        columns=columns,
    )


def _dimension_model(raw: dict, inputs: _PlanInputs) -> ModelSpec:
    name = _normalized_name(raw.get("name"), "gold_star.dimensions[].name")
    surrogate = _require_identifier(raw.get("surrogate_key"), f"{name} surrogate_key")
    attributes = _string_list(raw.get("attributes"))
    natural_key = attributes[0] if attributes else surrogate
    columns = [ColumnSpec(name=surrogate, derivation="surrogate_key")]
    columns.extend(
        ColumnSpec(
            name=attr,
            source_columns=(f"bronze.{inputs.source_table}.{attr}",),
        )
        for attr in attributes
    )
    return ModelSpec(
        name=name,
        layer="marts",
        grain=f"one row per governed {natural_key} member",
        business_key=(attributes[0],) if attributes else (surrogate,),
        columns=tuple(columns),
    )


_DATE_COLUMNS = ("full_date", "year", "quarter", "month", "day", "iso_week")


def _date_dimension(inputs: _PlanInputs) -> ModelSpec | None:
    raw = inputs.gold_star.get("date_dimension")
    if not isinstance(raw, dict):
        return None
    name = _normalized_name(raw.get("name"), "gold_star.date_dimension.name")
    surrogate = _require_identifier(raw.get("surrogate_key"), f"{name} surrogate_key")
    columns = tuple(
        ColumnSpec(name=column, derivation="date_spine")
        for column in (surrogate, *_DATE_COLUMNS)
    )
    return ModelSpec(
        name=name,
        layer="marts",
        grain="one row per calendar date in the approved span",
        business_key=(_DATE_COLUMNS[0],),
        columns=columns,
    )


def _dimensions(inputs: _PlanInputs) -> tuple[ModelSpec, ...]:
    raw = inputs.gold_star.get("dimensions")
    entities = [
        _dimension_model(row, inputs)
        for row in (raw if isinstance(raw, list) else [])
        if isinstance(row, dict)
    ]
    date_dim = _date_dimension(inputs)
    if date_dim is not None:
        entities.append(date_dim)
    if not entities:
        raise ScaffoldError("gold_star declares no dimensions to build")
    return tuple(entities)


def _fact_columns(
    inputs: _PlanInputs, dimensions: tuple[ModelSpec, ...]
) -> tuple[ColumnSpec, ...]:
    """A synthetic surrogate key, the grain/business key, one FK per dimension,
    and every declared money measure -- each cited to the staging source."""
    table = inputs.source_table
    columns = [ColumnSpec(name=f"{inputs.fact.name}_sk", derivation="surrogate_key")]
    columns.extend(
        ColumnSpec(name=key, source_columns=(f"bronze.{table}.{key}",))
        for key in inputs.fact.business_key
    )
    columns.extend(
        ColumnSpec(
            name=dim.columns[0].name,
            source_columns=(f"bronze.{table}.{dim.business_key[0]}",),
        )
        for dim in dimensions
    )
    columns.extend(
        ColumnSpec(name=measure, source_columns=(f"bronze.{table}.{measure}",))
        for measure in inputs.fact.additive_money_measures
    )
    return tuple(_dedupe_columns(columns))


def _dedupe_columns(columns: list[ColumnSpec]) -> list[ColumnSpec]:
    seen: set[str] = set()
    unique: list[ColumnSpec] = []
    for column in columns:
        if column.name in seen:
            continue
        seen.add(column.name)
        unique.append(column)
    return unique


def _fact_model(inputs: _PlanInputs, dimensions: tuple[ModelSpec, ...]) -> ModelSpec:
    return ModelSpec(
        name=inputs.fact.name,
        layer="marts",
        grain=inputs.fact_grain,
        business_key=inputs.fact.business_key,
        columns=_fact_columns(inputs, dimensions),
    )


_AUDIT_COLUMNS = (
    "assertion_id",
    "assertion_class",
    "subject",
    "expected",
    "actual",
    "delta",
    "tolerance",
    "passed",
)


def _audit_model(table_id: str) -> ModelSpec:
    return ModelSpec(
        name=f"audit_{table_id}_parity",
        layer="audit",
        grain="one row per required migration-versus-shadow parity assertion",
        business_key=("assertion_id",),
        columns=tuple(
            ColumnSpec(name=name, derivation="parity_measure")
            for name in _AUDIT_COLUMNS
        ),
    )


def _parity_rows(
    inputs: _PlanInputs, dimensions: tuple[ModelSpec, ...]
) -> tuple[ParityRow, ...]:
    """The exact assertion set ``evidence._validate_parity_set`` requires."""
    fact = inputs.fact.name
    rows = [
        ParityRow("fact_row_count", "fact_row_count", fact, "0"),
        ParityRow(
            f"fact_distinct_{'_'.join(inputs.fact.business_key)}",
            "business_key_count",
            f"{fact}.{'.'.join(inputs.fact.business_key)}",
            "0",
        ),
    ]
    rows.extend(
        ParityRow(
            f"fact_{measure}_sum",
            "additive_money_total",
            f"{fact}.{measure}",
            "0.01",
        )
        for measure in inputs.fact.additive_money_measures
    )
    rows.extend(
        ParityRow(
            f"{dim.name}_member_count",
            "dimension_member_count",
            dim.name,
            "0",
        )
        for dim in dimensions
    )
    return tuple(rows)


def build_scaffold_plan(
    source: MapSource,
    table_id: str,
    fact: FactBinding,
) -> ScaffoldPlan:
    """Derive the complete governed model set from an approved source map.

    ``fact`` is the already-validated :class:`FactBinding`
    (``fact_semantics.load_fact_semantics``); this never re-parses the fact
    section, only the star's dimensions and the staging columns.
    """
    document = source.document
    gold_star = document.get("gold_star")
    if not isinstance(gold_star, dict):
        raise ScaffoldError("source map has no gold_star section to scaffold")
    meta = document.get("meta")
    grain = meta.get("grain") if isinstance(meta, dict) else None
    inputs = _PlanInputs(
        table_id=table_id,
        source_table=table_id,
        source_map=source.source_map,
        source_map_revision=source.source_map_revision,
        fact=fact,
        fact_grain=grain if isinstance(grain, str) and grain.strip() else "one row",
        gold_star=gold_star,
    )
    dimensions = _dimensions(inputs)
    return ScaffoldPlan(
        table_id=table_id,
        source_table=table_id,
        source_map=source.source_map,
        source_map_revision=source.source_map_revision,
        fact=fact,
        staging=_staging_model(inputs, document),
        dimensions=dimensions,
        fact_model=_fact_model(inputs, dimensions),
        audit=_audit_model(table_id),
        parity=_parity_rows(inputs, dimensions),
    )
