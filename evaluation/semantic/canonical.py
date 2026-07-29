from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Iterable, TypeVar

from .types import (
    AttemptKey,
    AttemptScope,
    AttemptTarget,
    Decision,
    EvidenceSourceId,
    FalsifierId,
    MachineEnvelope,
    ReceiptLink,
    ReceiptLinkHash,
    SemanticValidationError,
    Sha256,
    StateKey,
    StateProjection,
)


def _canonical_value(value: Any) -> Any:
    semantic_value = getattr(value, "semantic_value", None)
    if callable(semantic_value):
        return _canonical_value(semantic_value())
    if value is None:
        return None
    if type(value) is bool:
        return value
    if type(value) is int:
        return value
    if isinstance(value, float):
        raise SemanticValidationError("floating point input is noncanonical")
    if isinstance(value, Enum):
        return {"tag": type(value).__name__, "value": value.value}
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise SemanticValidationError("canonical mapping keys must be strings")
        result: dict[str, Any] = {}
        for key in sorted(value):
            result[key] = _canonical_value(value[key])
        return result
    if isinstance(value, tuple):
        return [_canonical_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        encoded = sorted(canonical_bytes(item) for item in value)
        if len(encoded) != len(set(encoded)):
            raise SemanticValidationError("duplicate canonical set identity")
        return [json.loads(item.decode("utf-8")) for item in encoded]
    if is_dataclass(value) and not isinstance(value, type):
        result = {"tag": type(value).__name__}
        for item in fields(value):
            result[item.name] = _canonical_value(getattr(value, item.name))
        return result
    raise SemanticValidationError(f"unsupported canonical type: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            _canonical_value(value),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        if isinstance(error, SemanticValidationError):
            raise
        raise SemanticValidationError("value is not canonically encodable") from error


def _domain_bytes(domain: str) -> bytes:
    if not isinstance(domain, str) or not domain or "\x00" in domain:
        raise SemanticValidationError("canonical domain must be nonblank text without NUL")
    return domain.encode("utf-8") + b"\x00"


def canonical_sha256(domain: str, value: Any) -> Sha256:
    return Sha256(hashlib.sha256(_domain_bytes(domain) + canonical_bytes(value)).hexdigest())


T = TypeVar("T")


def canonical_set(values: Iterable[T], *, max_items: int | None = None) -> tuple[T, ...]:
    materialized = tuple(values)
    if max_items is not None:
        if type(max_items) is not int or max_items < 0:
            raise SemanticValidationError("max_items must be a nonnegative integer")
        if len(materialized) > max_items:
            from .types import CapacityError

            raise CapacityError(limit=max_items, actual=len(materialized))
    if any(isinstance(value, (Mapping, list, set, bytearray)) for value in materialized):
        raise SemanticValidationError("canonical_set members must be deeply immutable")
    keyed = sorted(
        ((canonical_bytes(value), value) for value in materialized),
        key=lambda item: item[0],
    )
    keys = tuple(key for key, _ in keyed)
    if len(keys) != len(set(keys)):
        raise SemanticValidationError("duplicate canonical identity")
    return tuple(value for _, value in keyed)


def make_state_key(value: StateProjection | MachineEnvelope) -> StateKey:
    projection = value.projection if isinstance(value, MachineEnvelope) else value
    if not isinstance(projection, StateProjection):
        raise SemanticValidationError("StateKey requires an exact StateProjection")
    digest = canonical_sha256("happycodex/0.6/state-key", projection.semantic_value())
    return StateKey(digest.value)


def make_attempt_key(
    state_key: StateKey,
    decision: Decision,
    target: AttemptTarget,
    scope: AttemptScope,
    falsifier_id: FalsifierId,
    evidence_source_id: EvidenceSourceId,
) -> AttemptKey:
    if not isinstance(state_key, StateKey):
        raise SemanticValidationError("AttemptKey requires a StateKey")
    if not isinstance(decision, Decision):
        raise SemanticValidationError("AttemptKey requires an exact Decision")
    if not isinstance(target, AttemptTarget) or not isinstance(scope, AttemptScope):
        raise SemanticValidationError("AttemptKey requires exact target and scope")
    if not isinstance(falsifier_id, FalsifierId) or not isinstance(evidence_source_id, EvidenceSourceId):
        raise SemanticValidationError("AttemptKey requires exact falsifier and evidence-source IDs")
    digest = canonical_sha256(
        "happycodex/0.6/attempt-key",
        {
            "state_key": state_key,
            "decision": decision,
            "target": target,
            "scope": scope,
            "falsifier_id": falsifier_id,
            "evidence_source_id": evidence_source_id,
        },
    )
    return AttemptKey(digest.value)


def make_receipt_link_hash(link: ReceiptLink) -> ReceiptLinkHash:
    if not isinstance(link, ReceiptLink):
        raise SemanticValidationError("receipt-link hash requires a ReceiptLink")
    digest = canonical_sha256("happycodex/0.6/receipt-link", link)
    return ReceiptLinkHash(digest.value)


__all__ = (
    "canonical_bytes",
    "canonical_set",
    "canonical_sha256",
    "make_attempt_key",
    "make_receipt_link_hash",
    "make_state_key",
)
