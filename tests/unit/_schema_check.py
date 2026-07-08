"""A tiny stdlib-only JSON Schema validator (no `jsonschema` dependency).

Shared by test modules that need to assert a dict matches one of this repo's
schemas/*.schema.json contracts without taking a third-party dependency the
`dev` extra does not declare (CI installs `pip install -e ".[dev]"` on a clean
runner; `jsonschema` is not in that extra and must not be imported at test
collection/run time).

Covers exactly the constructs this repo's schemas use: object/array/string/
null/boolean/number/integer types, `required`, `properties`,
`additionalProperties` (both `false` and a schema), `items`, `enum`, and
`$ref` into `$defs` (resolved against the root schema at any recursion
depth). Not a general-purpose validator.
"""

from __future__ import annotations


def _resolve_ref(schema: dict, root: dict) -> dict:
    ref = schema.get("$ref")
    if ref is None:
        return schema
    assert ref.startswith("#/"), f"unsupported $ref: {ref}"
    node = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _check_type(value: object, types: object) -> bool:
    allowed = types if isinstance(types, list) else [types]
    checks = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "null": lambda v: v is None,
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
    }
    return any(checks[t](value) for t in allowed)


def _check_required(value: dict, schema: dict, path: str) -> list[str]:
    return [
        f"{path}: missing required key {key!r}"
        for key in schema.get("required", [])
        if key not in value
    ]


def _check_no_extra_keys(value: dict, schema: dict, path: str) -> list[str]:
    if schema.get("additionalProperties") is not False:
        return []
    allowed = set(schema.get("properties", {}))
    return [f"{path}: unexpected key {key!r}" for key in value if key not in allowed]


def _validate_named_props(
    value: dict, schema: dict, root: dict, path: str
) -> list[str]:
    props = schema.get("properties", {})
    return [
        e
        for key, subschema in props.items()
        if key in value
        for e in _validate(value[key], subschema, root, f"{path}.{key}")
    ]


def _validate_additional_props(
    value: dict, schema: dict, root: dict, path: str
) -> list[str]:
    additional = schema.get("additionalProperties")
    if not isinstance(additional, dict):
        return []
    props = schema.get("properties", {})
    return [
        e
        for key, val in value.items()
        if key not in props
        for e in _validate(val, additional, root, f"{path}.{key}")
    ]


def _validate_object(value: dict, schema: dict, root: dict, path: str) -> list[str]:
    return (
        _check_required(value, schema, path)
        + _check_no_extra_keys(value, schema, path)
        + _validate_named_props(value, schema, root, path)
        + _validate_additional_props(value, schema, root, path)
    )


def _validate_items(value: list, schema: dict, root: dict, path: str) -> list[str]:
    if "items" not in schema:
        return []
    return [
        e
        for i, item in enumerate(value)
        for e in _validate(item, schema["items"], root, f"{path}[{i}]")
    ]


def _validate_enum(value: object, schema: dict, path: str) -> list[str]:
    if "enum" in schema and value not in schema["enum"]:
        return [f"{path}: {value!r} not in enum {schema['enum']}"]
    return []


def _validate(value: object, schema: dict, root: dict, path: str = "$") -> list[str]:
    schema = _resolve_ref(schema, root)

    if "type" in schema and not _check_type(value, schema["type"]):
        got = type(value).__name__
        return [f"{path}: expected type {schema['type']}, got {got}"]

    errors = _validate_enum(value, schema, path)
    if isinstance(value, dict):
        errors += _validate_object(value, schema, root, path)
    elif isinstance(value, list):
        errors += _validate_items(value, schema, root, path)
    return errors


def assert_matches_schema(instance: dict, schema: dict) -> None:
    errors = _validate(instance, schema, schema)
    assert errors == [], f"schema violations: {errors}"
