"""Canonical JSON and strict scalar helpers for the thin verifier."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable


class ContractError(ValueError):
    """A closed evaluator contract was not satisfied."""


def canonical_json(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ContractError("value is not canonical JSON") from exc


def canonical_text(value: Any) -> str:
    return canonical_json(value).decode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def exact(value: Any, fields: Iterable[str], label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != set(fields):
        raise ContractError(f"{label} fields differ")
    return value


def text(value: Any, label: str, *, allow_empty: bool = False) -> str:
    if type(value) is not str or (not value and not allow_empty) or "\x00" in value:
        raise ContractError(f"{label} is not valid text")
    return value


def integer(value: Any, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ContractError(f"{label} is not an integer >= {minimum}")
    return value


def boolean(value: Any, label: str) -> bool:
    if type(value) is not bool:
        raise ContractError(f"{label} is not boolean")
    return value


def sha256(value: Any, label: str) -> str:
    if type(value) is not str or len(value) != 64:
        raise ContractError(f"{label} is not sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ContractError(f"{label} is not sha256") from exc
    return value


def string_list(value: Any, label: str, *, unique: bool = True) -> list[str]:
    if type(value) is not list:
        raise ContractError(f"{label} is not a list")
    for index, item in enumerate(value):
        text(item, f"{label}[{index}]")
    if unique and len(value) != len(set(value)):
        raise ContractError(f"{label} contains duplicates")
    return value


def sealed(record: dict[str, Any]) -> dict[str, Any]:
    if "record_sha256" in record:
        raise ContractError("record is already sealed")
    return {**record, "record_sha256": canonical_sha256(record)}


def validate_seal(record: dict[str, Any]) -> None:
    sha256(record.get("record_sha256"), "record_sha256")
    body = {key: value for key, value in record.items() if key != "record_sha256"}
    if canonical_sha256(body) != record["record_sha256"]:
        raise ContractError("record seal differs")


__all__ = (
    "ContractError",
    "boolean",
    "canonical_json",
    "canonical_sha256",
    "canonical_text",
    "exact",
    "integer",
    "sealed",
    "sha256",
    "string_list",
    "text",
    "validate_seal",
)
