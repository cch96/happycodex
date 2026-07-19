from __future__ import annotations

from dataclasses import dataclass, field
import math
import re
import secrets
from typing import Any

from evaluation.core.identity import canonical_sha256


ALIASES = ("arm-a", "arm-b")
ACTUAL_ARMS = ("candidate", "public-0.2")
BLIND_FIELDS = frozenset(
    {
        "passed",
        "timed_out",
        "exit_code",
        "oracle_failures_count",
        "uncached_input_tokens",
        "output_tokens",
        "elapsed_seconds",
    }
)


def blind_view(metadata: dict[str, Any]) -> dict[str, Any]:
    failures = metadata.get("oracle_failures")
    usage = metadata.get("usage")
    if not isinstance(failures, list) or not isinstance(usage, dict):
        raise ValueError("raw result lacks oracle or usage telemetry")
    view = {
        "passed": metadata.get("passed"),
        "timed_out": metadata.get("timed_out"),
        "exit_code": metadata.get("exit_code"),
        "oracle_failures_count": len(failures),
        "uncached_input_tokens": metadata.get("uncached_input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "elapsed_seconds": metadata.get("elapsed_seconds"),
    }
    validate_blind_view(view)
    return view


def validate_blind_view(view: dict[str, Any]) -> None:
    if set(view) != BLIND_FIELDS:
        raise ValueError("unexpected blind receipt fields")
    if not isinstance(view["passed"], bool) or not isinstance(view["timed_out"], bool):
        raise ValueError("invalid blind receipt status")
    if not isinstance(view["exit_code"], int) or isinstance(view["exit_code"], bool):
        raise ValueError("invalid blind receipt exit code")
    for field_name in (
        "oracle_failures_count",
        "uncached_input_tokens",
        "output_tokens",
    ):
        value = view[field_name]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"invalid blind receipt metric: {field_name}")
    elapsed = view["elapsed_seconds"]
    if (
        not isinstance(elapsed, (int, float))
        or isinstance(elapsed, bool)
        or not math.isfinite(elapsed)
        or elapsed < 0
    ):
        raise ValueError("invalid blind receipt elapsed time")


def freeze_blind_decision(views: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if set(views) != set(ALIASES):
        raise ValueError("blind decision requires exactly arm-a and arm-b")
    aliases = []
    for alias in ALIASES:
        view = views[alias]
        validate_blind_view(view)
        passed = (
            view["passed"]
            and not view["timed_out"]
            and view["exit_code"] == 0
            and view["oracle_failures_count"] == 0
        )
        aliases.append(
            {
                "alias": alias,
                "blind_view_sha256": canonical_sha256(view),
                "quality": "pass" if passed else "fail",
                "metrics": {
                    "uncached_input_tokens": view["uncached_input_tokens"],
                    "output_tokens": view["output_tokens"],
                    "elapsed_seconds": view["elapsed_seconds"],
                },
            }
        )
    return {"schema_version": 1, "aliases": aliases}


@dataclass(frozen=True)
class SealedMapping:
    pair_id: str
    mapping_commitment_sha256: str
    _mapping: dict[str, str] = field(repr=False)
    _nonce: str = field(repr=False)

    def public_receipt(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "pair_id": self.pair_id,
            "mapping_commitment_sha256": self.mapping_commitment_sha256,
        }


def seal_mapping(
    pair_id: str, *, candidate_alias: str | None = None, nonce: str | None = None
) -> SealedMapping:
    if not re.fullmatch(r"[a-z0-9-]+", pair_id):
        raise ValueError("invalid pair id")
    candidate_alias = candidate_alias or ALIASES[secrets.randbelow(len(ALIASES))]
    if candidate_alias not in ALIASES:
        raise ValueError("candidate alias must be arm-a or arm-b")
    public_alias = next(alias for alias in ALIASES if alias != candidate_alias)
    nonce = nonce or secrets.token_hex(32)
    if not isinstance(nonce, str) or len(nonce) < 16:
        raise ValueError("mapping nonce is too short")
    mapping = {"candidate": candidate_alias, "public-0.2": public_alias}
    payload = {
        "schema_version": 1,
        "pair_id": pair_id,
        "mapping": mapping,
        "nonce": nonce,
    }
    return SealedMapping(pair_id, canonical_sha256(payload), mapping, nonce)


def reveal_mapping(
    sealed: SealedMapping, *, pre_reveal_decision_sha256: str
) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{64}", pre_reveal_decision_sha256):
        raise ValueError("invalid pre-reveal decision digest")
    return {
        "schema_version": 1,
        "pair_id": sealed.pair_id,
        "mapping_commitment_sha256": sealed.mapping_commitment_sha256,
        "mapping": dict(sealed._mapping),
        "nonce": sealed._nonce,
        "pre_reveal_decision_sha256": pre_reveal_decision_sha256,
    }


def validate_reveal(reveal: dict[str, Any], decision: dict[str, Any]) -> None:
    expected_fields = {
        "schema_version",
        "pair_id",
        "mapping_commitment_sha256",
        "mapping",
        "nonce",
        "pre_reveal_decision_sha256",
    }
    if set(reveal) != expected_fields or reveal["schema_version"] != 1:
        raise ValueError("invalid reveal envelope")
    mapping = reveal["mapping"]
    payload = {
        "schema_version": 1,
        "pair_id": reveal["pair_id"],
        "mapping": mapping,
        "nonce": reveal["nonce"],
    }
    if canonical_sha256(payload) != reveal["mapping_commitment_sha256"]:
        raise ValueError("mapping commitment mismatch")
    if (
        not isinstance(mapping, dict)
        or set(mapping) != set(ACTUAL_ARMS)
        or set(mapping.values()) != set(ALIASES)
    ):
        raise ValueError("invalid revealed mapping")
    if canonical_sha256(decision) != reveal["pre_reveal_decision_sha256"]:
        raise ValueError("pre-reveal decision digest mismatch")
