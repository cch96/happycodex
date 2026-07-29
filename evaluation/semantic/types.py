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


class ProvenanceKind(str, Enum):
    DIRECT = "DIRECT"
    DELEGATED = "DELEGATED"


class InfraKind(str, Enum):
    REPLACED = "REPLACED"


_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/=+@-]*")
_TAG_PATTERN = re.compile(r"[a-z][a-z0-9_]*")
_DIGEST_TAGS = {"lineage", "role_config", "progress_key", "attempt_key", "source_event"}


@dataclass(frozen=True, order=True)
class Id:
    tag: str
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.tag, str) or _TAG_PATTERN.fullmatch(self.tag) is None:
            raise SemanticError("Id tag is invalid")
        if not isinstance(self.value, str) or _ID_PATTERN.fullmatch(self.value) is None:
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

    def __post_init__(self) -> None:
        for name, tag in (
            ("task", "task"),
            ("root_task", "root_task"),
            ("executor_task", "executor_task"),
            ("owner", "owner"),
            ("destination", "destination"),
            ("lineage", "lineage"),
            ("role_config", "role_config"),
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
            }
        )


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise SemanticError("mapping keys must be strings")
        return MappingProxyType({key: _freeze(value[key]) for key in sorted(value)})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, bytearray)):
        raise SemanticError("mutable or unordered semantic value")
    if value is None or type(value) in (str, int, bool):
        return value
    raise SemanticError(f"unsupported fact value: {type(value).__name__}")


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(value[key]) for key in value}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class _Record:
    primary_key: Id
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        if type(self.primary_key) is not Id:
            raise SemanticError("record primary key must be tagged")
        object.__setattr__(self, "payload", _freeze(self.payload))

    def to_value(self) -> Mapping[str, object]:
        return MappingProxyType(
            {"id": self.primary_key.value, **{key: self.payload[key] for key in self.payload}}
        )

    def to_wire(self) -> dict[str, object]:
        return _thaw(self.to_value())


@dataclass(frozen=True)
class Facts:
    schema_generation: int
    task: TaskBinding
    stable: Mapping[str, tuple[_Record, ...]]
    administration: Mapping[str, tuple[_Record, ...]]

    def __post_init__(self) -> None:
        if type(self.schema_generation) is not int or self.schema_generation != 6:
            raise SemanticError("schema_generation must equal 6")
        if type(self.task) is not TaskBinding:
            raise SemanticError("Facts.task must be TaskBinding")
        normalized: list[Mapping[str, tuple[_Record, ...]]] = []
        for name, source in (
            ("stable", self.stable),
            ("administration", self.administration),
        ):
            if not isinstance(source, Mapping):
                raise SemanticError(f"Facts.{name} must be a mapping")
            members: dict[str, tuple[_Record, ...]] = {}
            for domain in sorted(source):
                records = source[domain]
                if not isinstance(records, tuple) or any(
                    type(record) is not _Record for record in records
                ):
                    raise SemanticError(f"Facts.{name}.{domain} must be immutable records")
                members[domain] = records
            normalized.append(MappingProxyType(members))
        object.__setattr__(self, "stable", normalized[0])
        object.__setattr__(self, "administration", normalized[1])

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


@dataclass(frozen=True)
class AuthorityProvenance:
    kind: ProvenanceKind
    issuer: Id
    destination: Id
    lineage: Id
    source_event: Id
    target: Id
    scope: Id
    _adapter_issued: bool = field(default=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ProvenanceKind):
            raise SemanticError("provenance kind is invalid")
        for name, tag in (
            ("issuer", "root_task"),
            ("destination", "destination"),
            ("lineage", "lineage"),
            ("source_event", "source_event"),
            ("target", "action_target"),
            ("scope", "action_scope"),
        ):
            _require_id(getattr(self, name), tag, name)
        if type(self._adapter_issued) is not bool:
            raise SemanticError("adapter issuance marker is invalid")

    @classmethod
    def from_adapter(
        cls,
        *,
        kind: ProvenanceKind,
        issuer: Id,
        destination: Id,
        lineage: Id,
        source_event: Id,
        target: Id,
        scope: Id,
    ) -> AuthorityProvenance:
        return cls(kind, issuer, destination, lineage, source_event, target, scope, True)


@dataclass(frozen=True)
class NextAction:
    kind: ActionKind
    target: Id
    scope: Id
    falsifier: Id
    evidence_source: Id

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ActionKind):
            raise SemanticError("action kind is invalid")
        for name, tag in (
            ("target", "action_target"),
            ("scope", "action_scope"),
            ("falsifier", "falsifier"),
            ("evidence_source", "evidence_source"),
        ):
            _require_id(getattr(self, name), tag, name)

    def to_wire(self) -> dict[str, str]:
        return {
            "kind": self.kind.value,
            "target": self.target.value,
            "scope": self.scope.value,
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
        if not isinstance(self.decision, EffectDecision):
            raise SemanticError("effect decision is invalid")
        _require_id(self.target, "action_target", "target")
        _require_id(self.scope, "action_scope", "scope")
        if not isinstance(self.reason, str) or not self.reason:
            raise SemanticError("effect reason is invalid")


@dataclass(frozen=True)
class ProgressReport:
    facts: Facts
    progress_key: Id
    next_action: NextAction

    def __post_init__(self) -> None:
        _require_id(self.progress_key, "progress_key", "progress_key")

    def to_wire(self) -> dict[str, object]:
        return {
            "facts": self.facts.to_wire(),
            "progress_key": self.progress_key.value,
            "next_action": self.next_action.to_wire(),
        }


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
    "ProvenanceKind",
    "SemanticError",
    "TaskBinding",
)
