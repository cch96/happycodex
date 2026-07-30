from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any


class SemanticError(ValueError):
    """A generation-7 value is malformed, ambiguous, or non-canonical."""


@dataclass(frozen=True)
class FrozenMap(Mapping[str, Any]):
    _items: tuple[tuple[str, Any], ...]

    def __getitem__(self, key: str) -> Any:
        for item_key, value in self._items:
            if item_key == key:
                return value
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return (key for key, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __hash__(self) -> int:
        return hash(self._items)


@dataclass(frozen=True, order=True)
class Anchor:
    kind: str
    namespace: str
    value: str

    def semantic_value(self) -> dict[str, str]:
        if self.kind == "marker":
            return {"kind": self.kind, "value": self.value}
        field = {
            "path": "repository",
            "digest": "label",
        }[self.kind]
        return {"kind": self.kind, field: self.namespace, "value": self.value}


@dataclass(frozen=True)
class Finding:
    finding_id: str
    domain: str
    status: str
    anchors: tuple[Anchor, ...]
    blocker_class: str | None
    blocker_reason: str | None

    def semantic_value(self) -> dict[str, object]:
        return {
            "id": self.finding_id,
            "domain": self.domain,
            "status": self.status,
            "anchors": tuple(item.semantic_value() for item in self.anchors),
            "blocker_class": self.blocker_class,
        }


@dataclass(frozen=True)
class MachineFacts:
    schema_generation: int
    task_binding: FrozenMap
    accepted_baseline_failures: tuple[str, ...]
    infrastructure_generation: str

    @property
    def scope(self) -> str:
        return self.task_binding["destination_id"]

    def semantic_value(self) -> dict[str, object]:
        return {
            "schema_generation": self.schema_generation,
            "task_binding": self.task_binding,
            "accepted_baseline_failures": self.accepted_baseline_failures,
            "infrastructure_generation": self.infrastructure_generation,
        }


@dataclass(frozen=True)
class ModelObservation:
    qualifies: bool
    execplan_condition: str
    findings: tuple[Finding, ...]
    open_gates: tuple[str, ...]
    evidence: tuple[str, ...]
    reason: str
    recovery: FrozenMap | None


@dataclass(frozen=True)
class ControlBlocker:
    finding_id: str
    blocker_class: str
    anchors: tuple[Anchor, ...]

    def semantic_value(self) -> dict[str, object]:
        return {
            "finding_id": self.finding_id,
            "class": self.blocker_class,
            "anchors": tuple(item.semantic_value() for item in self.anchors),
        }


@dataclass(frozen=True)
class NextAction:
    kind: str
    target: str
    scope: str
    falsifier_id: str
    evidence_source_id: str

    def semantic_value(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "target": self.target,
            "scope": self.scope,
            "falsifier_id": self.falsifier_id,
            "evidence_source_id": self.evidence_source_id,
        }


@dataclass(frozen=True)
class CanonicalReport:
    facts: MachineFacts
    observation: ModelObservation
    findings: tuple[Finding, ...]
    blockers: tuple[ControlBlocker, ...]
    next_action: NextAction
    state_key: str
    action_key: str


@dataclass(frozen=True)
class Reduction:
    findings: tuple[Finding, ...]
    blockers: tuple[ControlBlocker, ...]
    next_action: NextAction


__all__ = (
    "Anchor",
    "CanonicalReport",
    "ControlBlocker",
    "Finding",
    "FrozenMap",
    "MachineFacts",
    "ModelObservation",
    "NextAction",
    "Reduction",
    "SemanticError",
)
