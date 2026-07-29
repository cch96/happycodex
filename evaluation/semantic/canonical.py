from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any

from evaluation.semantic.types import (
    Facts,
    Id,
    ProgressReport,
    SemanticError,
    _is_parsed_facts,
    _is_reducer_report,
)


def _value(value: Any) -> Any:
    if value is None or type(value) in (str, int, bool):
        return value
    if isinstance(value, float):
        raise SemanticError("floating point is noncanonical")
    if isinstance(value, Enum):
        return {"tag": type(value).__name__, "value": value.value}
    if isinstance(value, Mapping):
        if any(type(key) is not str for key in value):
            raise SemanticError("canonical mapping keys must be strings")
        return {key: _value(value[key]) for key in sorted(value)}
    if isinstance(value, tuple):
        return [_value(item) for item in value]
    if isinstance(value, (list, set, frozenset, bytearray)):
        raise SemanticError("mutable or unordered canonical input")
    semantic_value = getattr(value, "stable_value", None)
    if callable(semantic_value):
        return _value(semantic_value())
    to_value = getattr(value, "to_value", None)
    if callable(to_value):
        return _value(to_value())
    if is_dataclass(value) and not isinstance(value, type):
        return {
            "tag": type(value).__name__,
            **{
                item.name: _value(getattr(value, item.name))
                for item in fields(value)
                if not item.name.startswith("_")
            },
        }
    raise SemanticError(f"unsupported canonical type: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _digest(domain: str, value: Any) -> str:
    if type(domain) is not str or not domain or "\x00" in domain:
        raise SemanticError("hash domain is invalid")
    return hashlib.sha256(
        domain.encode("utf-8") + b"\0" + canonical_bytes(value)
    ).hexdigest()


def make_progress_key(facts: Facts) -> Id:
    if not _is_parsed_facts(facts):
        raise SemanticError("ProgressKey requires parser-issued Facts")
    return Id(
        "progress_key",
        _digest(
            "happycodex/0.6/progress-key",
            {
                "task_binding": facts.task.to_value(),
                "stable_semantic_facts": facts.stable_value(),
            },
        ),
    )


def make_attempt_key(report: ProgressReport) -> Id:
    if not _is_reducer_report(report):
        raise SemanticError("AttemptKey requires a reducer report")
    if report.progress_key != make_progress_key(report.facts):
        raise SemanticError("reducer report progress key mismatch")
    action = report.next_action
    return Id(
        "attempt_key",
        _digest(
            "happycodex/0.6/attempt-key",
            {
                "progress_key": report.progress_key.value,
                "target": action.target,
                "scope": action.scope,
                "falsifier_id": action.falsifier,
                "evidence_source_id": action.evidence_source,
            },
        ),
    )


__all__ = ("canonical_bytes", "make_attempt_key", "make_progress_key")
