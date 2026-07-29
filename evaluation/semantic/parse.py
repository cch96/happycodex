from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from evaluation.semantic.types import (
    ActionKind,
    CapacityError,
    Facts,
    Id,
    InfraKind,
    SemanticError,
    TaskBinding,
    _ADMIN_DOMAINS,
    _DOMAIN_ID_TAGS,
    _Record,
    _STABLE_DOMAINS,
    _make_facts,
)


_BINDING_FIELDS = frozenset(
    {
        "task_id",
        "root_task_id",
        "executor_task_id",
        "owner_label",
        "destination_id",
        "lineage_digest",
        "role_config_digest",
    }
)
_RECORD_FIELDS = MappingProxyType(
    {
        **{
            domain: frozenset({"id", "state", "evidence"})
            for domain in ("checks", "claims", "families", "findings", "gates")
        },
        "pending": frozenset(
            {
                "id",
                "priority",
                "kind",
                "target",
                "scope",
                "falsifier_id",
                "evidence_source_id",
            }
        ),
        "replacements": frozenset(
            {"id", "kind", "prior", "current", "evidence"}
        ),
        "paths": frozenset({"id", "repository_id", "path"}),
        "markers": frozenset({"id", "value"}),
        **{
            domain: frozenset({"id", "value"})
            for domain in _ADMIN_DOMAINS
        },
    }
)
_STATE_VALUES = MappingProxyType(
    {
        "checks": frozenset({"PENDING", "PASS", "FAIL", "BASELINE_ACCEPTED"}),
        "claims": frozenset({"OPEN", "VERIFIED", "N/A"}),
        "families": frozenset({"OPEN", "BOUNDARY_REQUIRED", "CLOSED", "N/A"}),
        "findings": frozenset(
            {
                "OPEN",
                "BASELINE_UNCHANGED",
                "CANDIDATE_NEW",
                "UNKNOWN",
                "RESOLVED",
                "BASELINE_ACCEPTED",
            }
        ),
        "gates": frozenset({"OPEN", "BLOCKED", "SATISFIED", "WAIVED"}),
    }
)
_PENDING_ID_FIELDS = MappingProxyType(
    {
        "target": "action_target",
        "scope": "action_scope",
        "falsifier_id": "falsifier",
        "evidence_source_id": "evidence_source",
    }
)


def _mapping(value: object, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or any(type(key) is not str for key in value):
        raise SemanticError(f"{name} must be an object")
    return value


def _exact_fields(
    value: Mapping[str, Any],
    expected: frozenset[str] | set[str],
    name: str,
) -> None:
    actual = set(value)
    if actual != set(expected):
        unknown = sorted(actual - set(expected))
        missing = sorted(set(expected) - actual)
        raise SemanticError(
            f"{name} fields mismatch: missing={missing}, unknown={unknown}"
        )


def _text(value: object, name: str) -> str:
    if type(value) is not str or not value:
        raise SemanticError(f"{name} must be nonblank text")
    return value


def _string_tuple(value: object, name: str) -> tuple[str, ...]:
    if type(value) is not list:
        raise SemanticError(f"{name} must be an array of nonblank text")
    result: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = _text(item, name)
        if text in seen:
            raise SemanticError(f"duplicate value in {name}: {text}")
        seen.add(text)
        result.append(text)
    return tuple(sorted(result))


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


def _state_payload(
    record: Mapping[str, Any],
    domain: str,
) -> dict[str, object]:
    state = _text(record["state"], f"{domain}.state")
    if state not in _STATE_VALUES[domain]:
        raise SemanticError(f"{domain}.state is invalid")
    return {
        "state": state,
        "evidence": _string_tuple(record["evidence"], f"{domain}.evidence"),
    }


def _pending_payload(record: Mapping[str, Any]) -> dict[str, object]:
    if type(record["priority"]) is not int or record["priority"] < 0:
        raise SemanticError("pending.priority must be a nonnegative integer")
    kind = _text(record["kind"], "pending.kind")
    try:
        ActionKind(kind)
    except ValueError as error:
        raise SemanticError("pending.kind is invalid") from error
    payload: dict[str, object] = {
        "priority": record["priority"],
        "kind": kind,
    }
    for field, tag in _PENDING_ID_FIELDS.items():
        payload[field] = Id(tag, _text(record[field], f"pending.{field}"))
    return payload


def _replacement_payload(record: Mapping[str, Any]) -> dict[str, object]:
    kind = _text(record["kind"], "replacements.kind")
    if kind != InfraKind.REPLACED.value:
        raise SemanticError("unknown infrastructure transition")
    prior = _text(record["prior"], "replacements.prior")
    current = _text(record["current"], "replacements.current")
    evidence = _string_tuple(record["evidence"], "replacements.evidence")
    if not evidence:
        raise SemanticError("REPLACED requires nonempty evidence")
    if prior == current:
        raise SemanticError("REPLACED must change the infrastructure envelope")
    return {
        "kind": kind,
        "prior": prior,
        "current": current,
        "evidence": evidence,
    }


def _path_payload(record: Mapping[str, Any]) -> dict[str, object]:
    repository = _text(record["repository_id"], "paths.repository_id")
    path = _text(record["path"], "paths.path")
    if (
        path.startswith("/")
        or path.endswith("/")
        or "\\" in path
        or "//" in path
        or any(part in ("", ".", "..") for part in path.split("/"))
    ):
        raise SemanticError("path must be exact root-relative POSIX identity")
    return {"repository_id": repository, "path": path}


def _payload(record: Mapping[str, Any], domain: str) -> dict[str, object]:
    if domain in _STATE_VALUES:
        return _state_payload(record, domain)
    if domain == "pending":
        return _pending_payload(record)
    if domain == "replacements":
        return _replacement_payload(record)
    if domain == "paths":
        return _path_payload(record)
    if domain == "markers":
        return {"value": _text(record["value"], "markers.value")}
    if domain == "timestamps":
        value = record["value"]
        if type(value) is not int or value < 0:
            raise SemanticError("timestamps.value must be a nonnegative integer")
        return {"value": value}
    return {"value": _text(record["value"], f"{domain}.value")}


def _records(raw: object, domain: str) -> tuple[_Record, ...]:
    if type(raw) is not list:
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
        result.append(
            _Record(
                Id(_DOMAIN_ID_TAGS[domain], primary_key),
                _payload(record, domain),
            )
        )
    return tuple(sorted(result, key=lambda item: item.primary_key.value))


def parse_facts(raw: object) -> Facts:
    envelope = _mapping(raw, "facts envelope")
    _exact_fields(
        envelope,
        {"schema_generation", "task_binding", "facts", "administration"},
        "facts envelope",
    )
    stable_raw = _mapping(envelope["facts"], "facts")
    admin_raw = _mapping(envelope["administration"], "administration")
    _exact_fields(stable_raw, set(_STABLE_DOMAINS), "facts")
    _exact_fields(admin_raw, set(_ADMIN_DOMAINS), "administration")
    stable = {
        domain: _records(stable_raw[domain], domain) for domain in _STABLE_DOMAINS
    }
    administration = {
        domain: _records(admin_raw[domain], domain) for domain in _ADMIN_DOMAINS
    }
    return _make_facts(
        schema_generation=envelope["schema_generation"],
        task=_binding(envelope["task_binding"]),
        stable=stable,
        administration=administration,
    )


__all__ = ("parse_facts",)
