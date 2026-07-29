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
    if (
        type(view["passed"]) is not bool
        or type(view["timed_out"]) is not bool
        or type(view["exit_code"]) is not int
        or type(view["oracle_failures_count"]) is not int
        or view["oracle_failures_count"] < 0
    ):
        raise ValueError("invalid execution status")
    for field_name in ("uncached_input_tokens", "output_tokens"):
        value = view[field_name]
        if type(value) is not int or value < 0:
            raise ValueError(f"invalid blind receipt metric: {field_name}")
    elapsed = view["elapsed_seconds"]
    if (
        type(elapsed) not in (int, float)
        or not math.isfinite(elapsed)
        or elapsed < 0
    ):
        raise ValueError("invalid blind receipt elapsed time")
    if view["timed_out"] or view["exit_code"] != 0:
        raise ValueError("quality evidence requires a completed execution")
    if view["passed"] is not (view["oracle_failures_count"] == 0):
        raise ValueError("pass status does not match oracle failures")


def freeze_blind_decision(views: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if set(views) != set(ALIASES):
        raise ValueError("blind decision requires exactly arm-a and arm-b")
    aliases = []
    for alias in ALIASES:
        view = views[alias]
        validate_blind_view(view)
        aliases.append(
            {
                "alias": alias,
                "blind_view_sha256": canonical_sha256(view),
                "quality": "pass" if view["passed"] else "fail",
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
    aliases = decision.get("aliases") if isinstance(decision, dict) else None
    if set(decision) != {"schema_version", "aliases"} or (
        decision["schema_version"] != 1
        or not isinstance(aliases, list)
        or len(aliases) != len(ALIASES)
    ):
        raise ValueError("invalid blind decision envelope")
    for alias, row in zip(ALIASES, aliases, strict=True):
        if (
            not isinstance(row, dict)
            or set(row) != {"alias", "blind_view_sha256", "quality", "metrics"}
            or row["alias"] != alias
            or re.fullmatch(r"[0-9a-f]{64}", row["blind_view_sha256"]) is None
            or row["quality"] not in {"pass", "fail"}
            or not isinstance(row["metrics"], dict)
            or set(row["metrics"]) != {
                "uncached_input_tokens", "output_tokens", "elapsed_seconds"
            }
        ):
            raise ValueError("invalid blind decision row")
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
