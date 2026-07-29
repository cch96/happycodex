from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from evaluation.semantic.types import (
    CapacityError,
    Facts,
    Id,
    InfraKind,
    SemanticError,
    TaskBinding,
    _Record,
)


_STABLE = (
    "checks",
    "claims",
    "families",
    "findings",
    "gates",
    "markers",
    "paths",
    "pending",
    "replacements",
)
_ADMIN = (
    "authority_receipts",
    "consumptions",
    "cursors",
    "receipts",
    "resource_claims",
    "timestamps",
)
_BINDING_FIELDS = {
    "task_id",
    "root_task_id",
    "executor_task_id",
    "owner_label",
    "destination_id",
    "lineage_digest",
    "role_config_digest",
}
_RECORD_FIELDS = {
    **{
        domain: {"id", "state", "evidence"}
        for domain in ("checks", "claims", "families", "findings", "gates")
    },
    "pending": {
        "id",
        "priority",
        "kind",
        "target",
        "scope",
        "falsifier_id",
        "evidence_source_id",
    },
    "replacements": {"id", "kind", "prior", "current", "evidence"},
    "paths": {"id", "repository_id", "path"},
    "markers": {"id", "value"},
    **{domain: {"id", "value"} for domain in _ADMIN},
}
_ID_TAGS = {
    "checks": "check_id",
    "claims": "claim_id",
    "families": "family_id",
    "findings": "finding_id",
    "gates": "gate_id",
    "markers": "marker_id",
    "paths": "path_id",
    "pending": "pending_id",
    "replacements": "infrastructure_id",
    "authority_receipts": "authority_receipt_id",
    "consumptions": "consumption_id",
    "cursors": "cursor_id",
    "receipts": "receipt_id",
    "resource_claims": "resource_claim_id",
    "timestamps": "timestamp_id",
}


def _mapping(value: object, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        raise SemanticError(f"{name} must be an object")
    return value


def _exact_fields(value: Mapping[str, Any], expected: set[str], name: str) -> None:
    actual = set(value)
    if actual != expected:
        unknown = sorted(actual - expected)
        missing = sorted(expected - actual)
        raise SemanticError(f"{name} fields mismatch: missing={missing}, unknown={unknown}")


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise SemanticError(f"{name} must be nonblank text")
    return value


def _string_list(value: object, name: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise SemanticError(f"{name} must be an array of nonblank text")
    return value


def _binding(raw: object) -> TaskBinding:
    value = _mapping(raw, "task_binding")
    _exact_fields(value, _BINDING_FIELDS, "task_binding")
    return TaskBinding(
        task=Id("task", _text(value["task_id"], "task_id")),
        root_task=Id("root_task", _text(value["root_task_id"], "root_task_id")),
        executor_task=Id(
            "executor_task", _text(value["executor_task_id"], "executor_task_id")
        ),
        owner=Id("owner", _text(value["owner_label"], "owner_label")),
        destination=Id(
            "destination", _text(value["destination_id"], "destination_id")
        ),
        lineage=Id("lineage", _text(value["lineage_digest"], "lineage_digest")),
        role_config=Id(
            "role_config", _text(value["role_config_digest"], "role_config_digest")
        ),
    )


def _records(raw: object, domain: str) -> tuple[_Record, ...]:
    if not isinstance(raw, list):
        raise SemanticError(f"{domain} must be an array")
    if domain == "markers" and len(raw) > 64:
        raise CapacityError(64, len(raw))
    result: list[_Record] = []
    primary_keys: set[str] = set()
    for item in raw:
        record = _mapping(item, domain)
        _exact_fields(record, _RECORD_FIELDS[domain], domain)
        primary_key = _text(record["id"], f"{domain}.id")
        if primary_key in primary_keys:
            raise SemanticError(f"duplicate primary key in {domain}: {primary_key}")
        primary_keys.add(primary_key)
        if "evidence" in record:
            evidence = _string_list(record["evidence"], f"{domain}.evidence")
            if (
                domain == "replacements"
                and record["kind"] == InfraKind.REPLACED.value
                and not evidence
            ):
                raise SemanticError("REPLACED requires nonempty evidence")
        if domain == "replacements":
            if record["kind"] != InfraKind.REPLACED.value:
                raise SemanticError("unknown infrastructure transition")
            if record["prior"] == record["current"]:
                raise SemanticError("REPLACED must change the infrastructure envelope")
        if domain == "pending":
            if type(record["priority"]) is not int or record["priority"] < 0:
                raise SemanticError("pending.priority must be a nonnegative integer")
            try:
                from evaluation.semantic.types import ActionKind

                ActionKind(record["kind"])
            except ValueError as error:
                raise SemanticError("pending.kind is invalid") from error
        if domain == "paths":
            _text(record["repository_id"], "paths.repository_id")
            path = _text(record["path"], "paths.path")
            if (
                path.startswith("/")
                or path.endswith("/")
                or "\\" in path
                or "//" in path
                or any(part in ("", ".", "..") for part in path.split("/"))
            ):
                raise SemanticError("path must be exact root-relative POSIX identity")
        result.append(
            _Record(
                Id(_ID_TAGS[domain], primary_key),
                {key: record[key] for key in record if key != "id"},
            )
        )
    return tuple(sorted(result, key=lambda item: item.primary_key))


def parse_facts(raw: object) -> Facts:
    envelope = _mapping(raw, "facts envelope")
    _exact_fields(
        envelope,
        {"schema_generation", "task_binding", "facts", "administration"},
        "facts envelope",
    )
    stable_raw = _mapping(envelope["facts"], "facts")
    admin_raw = _mapping(envelope["administration"], "administration")
    _exact_fields(stable_raw, set(_STABLE), "facts")
    _exact_fields(admin_raw, set(_ADMIN), "administration")
    stable = {domain: _records(stable_raw[domain], domain) for domain in _STABLE}
    administration = {domain: _records(admin_raw[domain], domain) for domain in _ADMIN}
    return Facts(
        envelope["schema_generation"],
        _binding(envelope["task_binding"]),
        stable,
        administration,
    )


__all__ = ("parse_facts",)
