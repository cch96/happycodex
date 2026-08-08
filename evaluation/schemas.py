"""Closed recursive JSON schemas used by the thin verifier."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evaluation.canonical import ContractError, exact
from evaluation.policy import SCHEMA_VERSION

ALLOWED_TYPES = {"object", "array", "string", "boolean", "integer", "null"}
ALLOWED_KEYS = {
    "type",
    "properties",
    "required",
    "additionalProperties",
    "items",
    "enum",
}


class SchemaError(ContractError):
    pass


def validate_schema(schema: Any, label: str = "schema") -> dict[str, Any]:
    if type(schema) is not dict or set(schema) - ALLOWED_KEYS:
        raise SchemaError(f"{label} has unsupported schema fields")
    kind = schema.get("type")
    if kind not in ALLOWED_TYPES:
        raise SchemaError(f"{label} has unsupported type")
    if kind == "object":
        exact(
            schema,
            {"type", "properties", "required", "additionalProperties"},
            label,
        )
        properties = schema["properties"]
        required = schema["required"]
        if type(properties) is not dict or type(required) is not list:
            raise SchemaError(f"{label} object shape differs")
        if schema["additionalProperties"] is not False:
            raise SchemaError(f"{label} must be closed")
        if required != list(properties) or len(required) != len(set(required)):
            raise SchemaError(
                f"{label} required order differs from properties"
            )
        for name, child in properties.items():
            if type(name) is not str or not name:
                raise SchemaError(f"{label} property name is invalid")
            validate_schema(child, f"{label}.{name}")
    elif kind == "array":
        exact(schema, {"type", "items"}, label)
        validate_schema(schema["items"], f"{label}[]")
    elif "enum" in schema:
        exact(schema, {"type", "enum"}, label)
        values = schema["enum"]
        if type(values) is not list or not values:
            raise SchemaError(f"{label} enum differs")
        encoded = [json.dumps(item, sort_keys=True) for item in values]
        if len(encoded) != len(set(encoded)):
            raise SchemaError(f"{label} enum differs")
        for item in values:
            _validate_scalar(kind, item, label)
    else:
        exact(schema, {"type"}, label)
    return schema


def _validate_scalar(kind: str, value: Any, label: str) -> None:
    expected = {
        "string": str,
        "boolean": bool,
        "integer": int,
        "null": type(None),
    }[kind]
    if type(value) is not expected:
        raise SchemaError(f"{label} type differs")


def validate_instance(
    schema: dict[str, Any], value: Any, label: str = "value"
) -> Any:
    validate_schema(schema)
    kind = schema["type"]
    if kind == "object":
        if type(value) is not dict or set(value) != set(schema["required"]):
            raise SchemaError(f"{label} fields differ")
        for name, child in schema["properties"].items():
            validate_instance(child, value[name], f"{label}.{name}")
    elif kind == "array":
        if type(value) is not list:
            raise SchemaError(f"{label} is not an array")
        for index, item in enumerate(value):
            validate_instance(schema["items"], item, f"{label}[{index}]")
    else:
        _validate_scalar(kind, value, label)
        if "enum" in schema and value not in schema["enum"]:
            raise SchemaError(f"{label} is outside enum")
    return value


def load_closed_json(
    path: Path, *, required_fields: tuple[str, ...]
) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SchemaError(f"cannot load {path.name}") from exc
    if type(value) is not dict or tuple(value) != required_fields:
        raise SchemaError(f"{path.name} top-level fields differ")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise SchemaError(f"{path.name} schema version differs")
    return value


def object_schema(properties: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


__all__ = (
    "SchemaError",
    "load_closed_json",
    "object_schema",
    "validate_instance",
    "validate_schema",
)
