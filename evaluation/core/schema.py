import json
from pathlib import Path
import re

_USES = {
    "object": {"properties", "required", "additionalProperties"},
    "array": {"items", "minItems", "maxItems", "uniqueItems"},
    "string": {"pattern", "minLength", "maxLength"},
    "integer": {"minimum", "maximum"},
}
_KEYS = {"$ref", "type", "enum"}.union(*_USES.values())
_TYPES = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool, "null": type(None)}

def _require(condition, message):
    if not condition:
        raise ValueError(message)

def _walk(value, schema, definitions, refs=(), check=False):
    _require(isinstance(schema, dict) and not set(schema) - _KEYS, "invalid schema dialect")
    if "$ref" in schema:
        name = schema["$ref"]
        _require(set(schema) == {"$ref"} and name in definitions, "unknown schema reference")
        _require(name not in refs and len(refs) < 6, "cyclic schema reference or depth exceeded")
        return _walk(value, definitions[name], definitions, (*refs, name), check)
    kinds = schema.get("type")
    kinds = [kinds] if isinstance(kinds, str) else kinds
    _require(isinstance(kinds, list) and kinds and not set(kinds) - set(_TYPES), "invalid schema type")
    if check:
        applicable = {"type", "enum"}.union(*(_USES.get(kind, set()) for kind in kinds))
        _require(set(schema) <= applicable, "schema keyword has no effect")
        for child in [*schema.get("properties", {}).values(), *([schema["items"]] if "items" in schema else [])]:
            _walk(None, child, definitions, refs, True)
        return value
    valid_type = any(
        isinstance(value, _TYPES[kind])
        and not (kind == "integer" and isinstance(value, bool))
        for kind in kinds
    )
    _require(valid_type and ("enum" not in schema or value in schema["enum"]), "schema type or enum mismatch")
    if value is None:
        return value
    if isinstance(value, str):
        _require(schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", len(value))
                 and ("pattern" not in schema or re.fullmatch(schema["pattern"], value)), "schema string mismatch")
    if type(value) is int:
        _require(schema.get("minimum", value) <= value <= schema.get("maximum", value), "schema range mismatch")
    if isinstance(value, dict):
        props, required = schema.get("properties", {}), set(schema.get("required", []))
        exact = required <= set(value) and not (
            schema.get("additionalProperties") is False and set(value) - set(props)
        )
        _require(exact, "schema object mismatch")
        for key in set(value) & set(props):
            _walk(value[key], props[key], definitions, refs)
    if isinstance(value, list):
        unique = len({json.dumps(item, sort_keys=True) for item in value}) == len(value)
        bounded = schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", len(value))
        _require(bounded and (not schema.get("uniqueItems") or unique),
                 "schema array mismatch")
        for item in value:
            _walk(item, schema["items"], definitions, refs)
    return value

def load_contracts(path=Path(__file__).resolve().parents[1] / "contracts-v6.json"):
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict) and set(value) == {"schema_version", "schemas"}
             and value["schema_version"] == 1 and isinstance(value["schemas"], dict), "invalid schema contract envelope")
    for schema in value["schemas"].values():
        _walk(None, schema, value["schemas"], check=True)
    return value

def validate_structure(value, schema, definitions):
    _walk(None, schema, definitions, check=True)
    return _walk(value, schema, definitions)

def validate_named(contracts, name, value):
    _require(name in contracts.get("schemas", {}), "unknown named schema reference")
    return _walk(value, contracts["schemas"][name], contracts["schemas"])

CONTRACTS = load_contracts()
