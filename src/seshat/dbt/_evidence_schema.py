"""Minimal JSON Schema validation for governed dbt evidence payloads."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Callable
from datetime import datetime
from typing import Any

from seshat.dbt.artifacts import ArtifactIntegrityError


def _schema_reference_parts(reference: str) -> list[str]:
    if not reference.startswith("#/"):
        raise ArtifactIntegrityError("evidence schema has an unsupported reference")
    return reference[2:].split("/")


def _schema_reference_child(value: Any, part: str) -> Any:
    if not isinstance(value, dict) or part not in value:
        raise ArtifactIntegrityError("evidence schema reference is unresolved")
    return value[part]


def _schema_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ArtifactIntegrityError("evidence schema reference is invalid")
    return value


def _schema_ref(root: dict[str, Any], reference: str) -> dict[str, Any]:
    value: Any = root
    for part in _schema_reference_parts(reference):
        value = _schema_reference_child(value, part)
    return _schema_mapping(value)


def _is_object(value: Any) -> bool:
    return isinstance(value, dict)


def _is_array(value: Any) -> bool:
    return isinstance(value, list)


def _is_string(value: Any) -> bool:
    return isinstance(value, str)


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _is_boolean(value: Any) -> bool:
    return isinstance(value, bool)


def _never_matches(_: Any) -> bool:
    return False


_SCHEMA_TYPE_CHECKS: dict[str, Callable[[Any], bool]] = {
    "object": _is_object,
    "array": _is_array,
    "string": _is_string,
    "integer": _is_integer,
    "number": _is_number,
    "boolean": _is_boolean,
}


def _schema_type(value: Any, expected: str) -> bool:
    return _SCHEMA_TYPE_CHECKS.get(expected, _never_matches)(value)


def _validate_const(value: Any, schema: dict[str, Any], path: str) -> None:
    if "const" in schema and value != schema["const"]:
        raise ArtifactIntegrityError(f"evidence JSON Schema const failed at {path}")


def _validate_enum(value: Any, schema: dict[str, Any], path: str) -> None:
    if "enum" in schema and value not in schema["enum"]:
        raise ArtifactIntegrityError(f"evidence JSON Schema enum failed at {path}")


def _validate_schema_type(value: Any, schema: dict[str, Any], path: str) -> None:
    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not _schema_type(value, expected_type):
        raise ArtifactIntegrityError(f"evidence JSON Schema type failed at {path}")


def _validate_literal_constraints(
    value: Any, schema: dict[str, Any], path: str
) -> None:
    _validate_const(value, schema, path)
    _validate_enum(value, schema, path)
    _validate_schema_type(value, schema, path)


def _validate_required_properties(
    value: dict[str, Any], schema: dict[str, Any], path: str
) -> None:
    missing = set(schema.get("required", [])) - set(value)
    if missing:
        raise ArtifactIntegrityError(
            f"evidence JSON Schema missing property at {path}: "
            + ", ".join(sorted(missing))
        )


def _validate_property_name(
    key: str, schema: dict[str, Any], root: dict[str, Any], path: str
) -> None:
    property_names = schema.get("propertyNames")
    if isinstance(property_names, dict):
        _validate_value(key, property_names, root, f"{path}.<key>")


def _property_schema(
    key: str, schema: dict[str, Any], path: str
) -> dict[str, Any] | None:
    properties = schema.get("properties", {})
    if key in properties:
        return properties[key]
    additional = schema.get("additionalProperties", True)
    if additional is False:
        raise ArtifactIntegrityError(
            f"evidence JSON Schema additional property at {path}: {key}"
        )
    return additional if isinstance(additional, dict) else None


def _validate_object(
    value: dict[str, Any],
    schema: dict[str, Any],
    root: dict[str, Any],
    path: str,
) -> None:
    _validate_required_properties(value, schema, path)
    for key, item in value.items():
        _validate_property_name(key, schema, root, path)
        item_schema = _property_schema(key, schema, path)
        if item_schema is not None:
            _validate_value(item, item_schema, root, f"{path}.{key}")


def _validate_unique_items(value: list[Any], schema: dict[str, Any], path: str) -> None:
    if not schema.get("uniqueItems"):
        return
    normalized = [
        json.dumps(item, sort_keys=True, separators=(",", ":")) for item in value
    ]
    if len(normalized) != len(set(normalized)):
        raise ArtifactIntegrityError(
            f"evidence JSON Schema uniqueItems failed at {path}"
        )


def _validate_array_items(
    value: list[Any],
    schema: dict[str, Any],
    root: dict[str, Any],
    path: str,
) -> None:
    item_schema = schema.get("items")
    if not isinstance(item_schema, dict):
        return
    for index, item in enumerate(value):
        _validate_value(item, item_schema, root, f"{path}[{index}]")


def _validate_array(
    value: list[Any],
    schema: dict[str, Any],
    root: dict[str, Any],
    path: str,
) -> None:
    _validate_unique_items(value, schema, path)
    _validate_array_items(value, schema, root, path)


def _validate_string_pattern(value: str, schema: dict[str, Any], path: str) -> None:
    if "pattern" in schema and re.search(schema["pattern"], value) is None:
        raise ArtifactIntegrityError(f"evidence JSON Schema pattern failed at {path}")


def _validate_string_length(value: str, schema: dict[str, Any], path: str) -> None:
    if len(value) < schema.get("minLength", 0) or len(value) > schema.get(
        "maxLength", math.inf
    ):
        raise ArtifactIntegrityError(f"evidence JSON Schema length failed at {path}")


def _validate_date_time(value: str, schema: dict[str, Any], path: str) -> None:
    if schema.get("format") != "date-time":
        return
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ArtifactIntegrityError(
            f"evidence JSON Schema date-time failed at {path}"
        ) from exc


def _validate_string(
    value: str,
    schema: dict[str, Any],
    root: dict[str, Any],
    path: str,
) -> None:
    del root
    _validate_string_pattern(value, schema, path)
    _validate_string_length(value, schema, path)
    _validate_date_time(value, schema, path)


def _validate_number(
    value: int | float,
    schema: dict[str, Any],
    root: dict[str, Any],
    path: str,
) -> None:
    del root
    if value < schema.get("minimum", -math.inf) or value > schema.get(
        "maximum", math.inf
    ):
        raise ArtifactIntegrityError(f"evidence JSON Schema range failed at {path}")


_ValueValidator = Callable[[Any, dict[str, Any], dict[str, Any], str], None]
_VALUE_VALIDATORS: tuple[tuple[Callable[[Any], bool], _ValueValidator], ...] = (
    (_is_object, _validate_object),
    (_is_array, _validate_array),
    (_is_string, _validate_string),
    (_is_integer, _validate_number),
    (_is_number, _validate_number),
)


def _value_validator(value: Any) -> _ValueValidator | None:
    return next(
        (validator for predicate, validator in _VALUE_VALIDATORS if predicate(value)),
        None,
    )


def _validate_value(
    value: Any,
    schema: dict[str, Any],
    root: dict[str, Any],
    path: str,
) -> None:
    if "$ref" in schema:
        _validate_value(value, _schema_ref(root, schema["$ref"]), root, path)
        return
    _validate_literal_constraints(value, schema, path)
    validator = _value_validator(value)
    if validator is not None:
        validator(value, schema, root, path)


def validate_evidence_payload(payload: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate evidence against the checked-in JSON Schema vocabulary."""

    _validate_value(payload, schema, schema, "$")
