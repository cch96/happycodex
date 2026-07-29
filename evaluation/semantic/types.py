from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
import re
from types import MappingProxyType
from typing import Any

class SemanticError(ValueError):
    """An input is malformed, ambiguous, or outside generation 6."""

class CapacityError(SemanticError):
    def __init__(self, limit: int, actual: int) -> None:
        super().__init__(f"capacity exceeded: limit={limit}, actual={actual}")
        self.limit = limit
        self.actual = actual

class ActionKind(str, Enum):
    DISCOVER = "DISCOVER"
    RECONCILE = "RECONCILE"
    IMPLEMENT_BATCH = "IMPLEMENT_BATCH"
    VERIFY = "VERIFY"
    FOCUSED_REVIEW = "FOCUSED_REVIEW"
    EXACT_FINAL = "EXACT_FINAL"
    ASK_USER = "ASK_USER"
    FREEZE_CANDIDATE = "FREEZE_CANDIDATE"
    CLOSE = "CLOSE"
    REFUSE = "REFUSE"

class EffectDecision(str, Enum):
    ALLOW = "ALLOW"
    ASK_USER = "ASK_USER"
    REFUSE = "REFUSE"

class _ProvenanceKind(str, Enum):
    DIRECT = "DIRECT"
    CROSS_TASK = "CROSS_TASK"

class InfraKind(str, Enum):
    REPLACED = "REPLACED"

_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/=+@-]*")
_TAG_PATTERN = re.compile(r"[a-z][a-z0-9_]*")
_DIGEST_TAGS = frozenset(
    {
        "attempt_key",
        "content",
        "lineage",
        "outcome",
        "progress_key",
        "repository",
        "role_config",
    }
)
_STABLE_DOMAINS = (
    "checks",
    "claims",
    "families",
    "findings",
    "gates",
    "markers",
    "paths",
    "replacements",
)
_ADMIN_DOMAINS = (
    "authority_receipts",
    "consumptions",
    "cursors",
    "receipts",
    "resource_claims",
    "timestamps",
)
_DOMAIN_ID_TAGS = MappingProxyType(
    {
        "checks": "check_id",
        "claims": "claim_id",
        "families": "family_id",
        "findings": "finding_id",
        "gates": "gate_id",
        "markers": "marker_id",
        "paths": "path_id",
        "replacements": "infrastructure_id",
        "authority_receipts": "authority_receipt_id",
        "consumptions": "consumption_id",
        "cursors": "cursor_id",
        "receipts": "receipt_id",
        "resource_claims": "resource_claim_id",
        "timestamps": "timestamp_id",
    }
)
_FACTS_SEAL = object()
_AUTHORITY_SEAL = object()
_REPORT_SEAL = object()

@dataclass(frozen=True, order=True)
class Id:
    tag: str
    value: str

    def __post_init__(self) -> None:
        if type(self.tag) is not str or _TAG_PATTERN.fullmatch(self.tag) is None:
            raise SemanticError("Id tag is invalid")
        if type(self.value) is not str or _ID_PATTERN.fullmatch(self.value) is None:
            raise SemanticError(f"{self.tag} identity is invalid")
        if self.tag in _DIGEST_TAGS and re.fullmatch(r"[0-9a-f]{64}", self.value) is None:
            raise SemanticError(f"{self.tag} must be lowercase 64-hex")

def _require_id(value: object, tag: str, field_name: str) -> None:
    if type(value) is not Id or value.tag != tag:
        raise SemanticError(f"{field_name} requires Id tag {tag}")

@dataclass(frozen=True)
class TaskBinding:
    task: Id
    root_task: Id
    executor_task: Id
    owner: Id
    destination: Id
    lineage: Id
    role_config: Id
    repository: Id
    outcome: Id

    def __post_init__(self) -> None:
        for name, tag in (
            ("task", "task"),
            ("root_task", "root_task"),
            ("executor_task", "executor_task"),
            ("owner", "owner"),
            ("destination", "destination"),
            ("lineage", "lineage"),
            ("role_config", "role_config"),
            ("repository", "repository"),
            ("outcome", "outcome"),
        ):
            _require_id(getattr(self, name), tag, name)

    def to_value(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "task_id": self.task.value,
                "root_task_id": self.root_task.value,
                "executor_task_id": self.executor_task.value,
                "owner_label": self.owner.value,
                "destination_id": self.destination.value,
                "lineage_digest": self.lineage.value,
                "role_config_digest": self.role_config.value,
                "repository_digest": self.repository.value,
                "outcome_digest": self.outcome.value,
            }
        )

def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        if any(type(key) is not str for key in value):
            raise SemanticError("mapping keys must be strings")
        return MappingProxyType({key: _freeze(value[key]) for key in sorted(value)})
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (list, set, frozenset, bytearray)):
        raise SemanticError("mutable or unordered semantic value")
    if type(value) is Id:
        return value
    if value is None or type(value) in (str, int, bool):
        return value
    raise SemanticError(f"unsupported fact value: {type(value).__name__}")

def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(value[key]) for key in value}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    if type(value) is Id:
        return value.value
    return value

@dataclass(frozen=True)
class _Record:
    primary_key: Id
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        if type(self.primary_key) is not Id:
            raise SemanticError("record primary key must be tagged")
        if not isinstance(self.payload, Mapping) or "id" in self.payload:
            raise SemanticError("record payload cannot contain id")
        object.__setattr__(self, "payload", _freeze(self.payload))

    def to_value(self) -> Mapping[str, object]:
        return MappingProxyType(
            {"id": self.primary_key.value, **{key: self.payload[key] for key in self.payload}}
        )

    def to_wire(self) -> dict[str, object]:
        return _thaw(self.to_value())

@dataclass(frozen=True, init=False)
class Facts:
    schema_generation: int
    task: TaskBinding
    stable: Mapping[str, tuple[_Record, ...]]
    administration: Mapping[str, tuple[_Record, ...]]
    _seal: object = field(repr=False, compare=False)

    def __init__(self) -> None:
        raise SemanticError("Facts are parser-issued; use parse_facts")

    def stable_value(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "schema_generation": self.schema_generation,
                "facts": MappingProxyType(
                    {
                        domain: tuple(record.to_value() for record in records)
                        for domain, records in self.stable.items()
                    }
                ),
            }
        )

    def to_wire(self) -> dict[str, object]:
        return {
            "schema_generation": self.schema_generation,
            "task_binding": _thaw(self.task.to_value()),
            "facts": {
                domain: [record.to_wire() for record in records]
                for domain, records in self.stable.items()
            },
            "administration": {
                domain: [record.to_wire() for record in records]
                for domain, records in self.administration.items()
            },
        }

def _normalize_domains(
    source: object,
    expected: tuple[str, ...],
    name: str,
) -> Mapping[str, tuple[_Record, ...]]:
    if not isinstance(source, Mapping) or any(type(key) is not str for key in source):
        raise SemanticError(f"Facts.{name} must be a mapping")
    if set(source) != set(expected):
        raise SemanticError(f"Facts.{name} domains are invalid")
    members: dict[str, tuple[_Record, ...]] = {}
    for domain in expected:
        records = source[domain]
        if type(records) is not tuple:
            raise SemanticError(f"Facts.{name}.{domain} must be immutable records")
        seen: set[str] = set()
        copied: list[_Record] = []
        for record in records:
            if type(record) is not _Record:
                raise SemanticError(f"Facts.{name}.{domain} has invalid record type")
            _require_id(record.primary_key, _DOMAIN_ID_TAGS[domain], f"{domain}.id")
            if record.primary_key.value in seen:
                raise SemanticError(
                    f"duplicate primary key in {domain}: {record.primary_key.value}"
                )
            seen.add(record.primary_key.value)
            copied.append(_Record(record.primary_key, record.payload))
        members[domain] = tuple(
            sorted(copied, key=lambda item: item.primary_key.value)
        )
    return MappingProxyType(members)

def _make_facts(
    *,
    schema_generation: object,
    task: object,
    stable: object,
    administration: object,
) -> Facts:
    if type(schema_generation) is not int or schema_generation != 6:
        raise SemanticError("schema_generation must equal 6")
    if type(task) is not TaskBinding:
        raise SemanticError("Facts.task must be TaskBinding")
    result = object.__new__(Facts)
    object.__setattr__(result, "schema_generation", schema_generation)
    object.__setattr__(result, "task", task)
    object.__setattr__(
        result, "stable", _normalize_domains(stable, _STABLE_DOMAINS, "stable")
    )
    object.__setattr__(
        result,
        "administration",
        _normalize_domains(administration, _ADMIN_DOMAINS, "administration"),
    )
    object.__setattr__(result, "_seal", _FACTS_SEAL)
    return result

def _is_parsed_facts(value: object) -> bool:
    return type(value) is Facts and getattr(value, "_seal", None) is _FACTS_SEAL

def _validate_authority(
    channel: object,
    root_task: object,
    source_task: object,
    target_task: object,
    executor_task: object,
    destination: object,
    lineage: object,
    message_id: object,
    turn_id: object,
    content_digest: object,
    target: object,
    scope: object,
) -> _ProvenanceKind:
    if type(channel) is not str or channel not in {
        "current_task_user",
        "cross_task_user_delegation",
    }:
        raise SemanticError("authority channel is invalid")
    for name, value, tag in (
        ("root_task", root_task, "root_task"),
        ("source_task", source_task, "task"),
        ("target_task", target_task, "task"),
        ("executor_task", executor_task, "executor_task"),
        ("destination", destination, "destination"),
        ("lineage", lineage, "lineage"),
        ("message_id", message_id, "message"),
        ("turn_id", turn_id, "turn"),
        ("content_digest", content_digest, "content"),
        ("target", target, "action_target"),
        ("scope", scope, "action_scope"),
    ):
        _require_id(value, tag, name)
    if channel == "current_task_user":
        if source_task != target_task:
            raise SemanticError("direct authority requires source task equal target task")
        return _ProvenanceKind.DIRECT
    if source_task == target_task:
        raise SemanticError("cross-task authority requires distinct source task")
    return _ProvenanceKind.CROSS_TASK

@dataclass(frozen=True, init=False)
class AuthorityProvenance:
    kind: _ProvenanceKind
    channel: str
    root_task: Id
    source_task: Id
    target_task: Id
    executor_task: Id
    destination: Id
    lineage: Id
    message_id: Id
    turn_id: Id
    content_digest: Id
    target: Id
    scope: Id
    _seal: object = field(repr=False, compare=False)

    def __init__(self) -> None:
        raise SemanticError("AuthorityProvenance is adapter-issued")

def _issue_authority(
    *,
    channel: str,
    root_task: Id,
    source_task: Id,
    target_task: Id,
    executor_task: Id,
    destination: Id,
    lineage: Id,
    message_id: Id,
    turn_id: Id,
    content_digest: Id,
    target: Id,
    scope: Id,
) -> AuthorityProvenance:
    kind = _validate_authority(
        channel,
        root_task,
        source_task,
        target_task,
        executor_task,
        destination,
        lineage,
        message_id,
        turn_id,
        content_digest,
        target,
        scope,
    )
    result = object.__new__(AuthorityProvenance)
    for name, value in (
        ("kind", kind),
        ("channel", channel),
        ("root_task", root_task),
        ("source_task", source_task),
        ("target_task", target_task),
        ("executor_task", executor_task),
        ("destination", destination),
        ("lineage", lineage),
        ("message_id", message_id),
        ("turn_id", turn_id),
        ("content_digest", content_digest),
        ("target", target),
        ("scope", scope),
    ):
        object.__setattr__(result, name, value)
    object.__setattr__(result, "_seal", _AUTHORITY_SEAL)
    return result

def _is_issued_authority(value: object) -> bool:
    return (
        type(value) is AuthorityProvenance
        and getattr(value, "_seal", None) is _AUTHORITY_SEAL
    )

@dataclass(frozen=True)
class NextAction:
    kind: ActionKind
    target: Id
    scope: Id
    family: Id
    falsifier: Id
    evidence_source: Id

    def __post_init__(self) -> None:
        if type(self.kind) is not ActionKind:
            raise SemanticError("action kind is invalid")
        for name, tag in (
            ("target", "action_target"),
            ("scope", "action_scope"),
            ("family", "family_id"),
            ("falsifier", "falsifier"),
            ("evidence_source", "evidence_source"),
        ):
            _require_id(getattr(self, name), tag, name)

    def to_wire(self) -> dict[str, str]:
        return {
            "kind": self.kind.value,
            "target": self.target.value,
            "scope": self.scope.value,
            "family_id": self.family.value,
            "falsifier_id": self.falsifier.value,
            "evidence_source_id": self.evidence_source.value,
        }

@dataclass(frozen=True)
class EffectGate:
    decision: EffectDecision
    target: Id
    scope: Id
    reason: str

    def __post_init__(self) -> None:
        if type(self.decision) is not EffectDecision:
            raise SemanticError("effect decision is invalid")
        _require_id(self.target, "action_target", "target")
        _require_id(self.scope, "action_scope", "scope")
        if type(self.reason) is not str or not self.reason:
            raise SemanticError("effect reason is invalid")

@dataclass(frozen=True, init=False)
class ProgressReport:
    facts: Facts
    progress_key: Id
    next_action: NextAction
    _seal: object = field(repr=False, compare=False)

    def __init__(self) -> None:
        raise SemanticError("ProgressReport is reducer-issued")

    def to_wire(self) -> dict[str, object]:
        return {
            "facts": self.facts.to_wire(),
            "progress_key": self.progress_key.value,
            "next_action": self.next_action.to_wire(),
        }

def _make_report(
    *,
    facts: Facts,
    progress_key: Id,
    next_action: NextAction,
) -> ProgressReport:
    if not _is_parsed_facts(facts):
        raise SemanticError("reducer report requires parsed Facts")
    _require_id(progress_key, "progress_key", "progress_key")
    if type(next_action) is not NextAction:
        raise SemanticError("reducer report requires NextAction")
    result = object.__new__(ProgressReport)
    object.__setattr__(result, "facts", facts)
    object.__setattr__(result, "progress_key", progress_key)
    object.__setattr__(result, "next_action", next_action)
    object.__setattr__(result, "_seal", _REPORT_SEAL)
    return result

def _is_reducer_report(value: object) -> bool:
    return (
        type(value) is ProgressReport
        and getattr(value, "_seal", None) is _REPORT_SEAL
        and _is_parsed_facts(value.facts)
        and type(value.next_action) is NextAction
    )

__all__ = (
    "ActionKind",
    "AuthorityProvenance",
    "CapacityError",
    "EffectDecision",
    "EffectGate",
    "Facts",
    "Id",
    "InfraKind",
    "NextAction",
    "ProgressReport",
    "SemanticError",
    "TaskBinding",
)
