from __future__ import annotations

from typing import Any, Callable

from evaluation.records import (
    canonical_json,
    canonical_sha256,
    validate_eval_spec,
    validate_product_artifact,
)


FORBIDDEN_PROVIDER_FIELDS = frozenset(
    {
        "expected_boundary", "expected_answer", "expected", "oracle",
        "matcher", "mapping", "verdict", "history", "findings_history",
        "preferred_verdict", "acceptable_alternatives",
    }
)
_CAPABILITY_KEY = object()


class ProviderError(ValueError):
    pass


def provider_projection(
    *, case: dict[str, Any], product_semantic_sha256: str,
    external_role_config_sha256: str, profile: dict[str, Any],
) -> dict[str, Any]:
    """Construct provider input from a closed allowlist, never by redaction."""
    required = {"role_id", "prompt"}
    if not required.issubset(case):
        raise ProviderError("case lacks provider-visible inputs")
    if any(field not in case for field in ("fixture", "workspace", "runtime", "response_schema")):
        raise ProviderError("case lacks materialized fixture, workspace, Runtime, or response schema")
    projection = {
        "schema_version": 1,
        "role_id": case["role_id"],
        "sample_id": case.get("sample_id"),
        "product_semantic_sha256": product_semantic_sha256,
        "external_role_config_sha256": external_role_config_sha256,
        "fixture": case["fixture"],
        "workspace": case["workspace"],
        "prompt": case["prompt"],
        "runtime": case["runtime"],
        "response_schema": case["response_schema"],
        "neutral_review_brief": case.get("neutral_review_brief"),
        "profile": {
            "model": profile["model"],
            "effort": profile["effort"],
            "tools": sorted(profile["tools"]),
            "timeout_seconds": profile["timeout_seconds"],
        },
    }
    serialized = canonical_json(projection)
    for field in FORBIDDEN_PROVIDER_FIELDS:
        if f'"{field}"' in serialized:
            raise ProviderError(f"forbidden provider field: {field}")
    return projection


def assert_provider_blind(
    *, sentinels: list[str], projection: dict[str, Any], workspace: Any,
    argv: list[str], stdin: str, env: dict[str, str], sanitized_events: Any,
) -> None:
    surface = canonical_json(
        {
            "projection": projection, "workspace": workspace, "argv": argv,
            "stdin": stdin, "env": env, "sanitized_events": sanitized_events,
        }
    )
    for sentinel in sentinels:
        if not sentinel or sentinel in surface:
            raise ProviderError("hidden sentinel reached a provider-visible surface")


def _redact(value: Any, secrets: list[str]) -> Any:
    if type(value) is str:
        result = value
        for secret in secrets:
            if secret:
                result = result.replace(secret, "<redacted>")
        return result
    if type(value) is list:
        return [_redact(item, secrets) for item in value]
    if type(value) is dict:
        return {
            key: _redact(item, secrets)
            for key, item in value.items()
            if key not in {"token", "credential", "raw_stdin"}
        }
    return value


def sanitize_events(events: list[dict[str, Any]], *, secrets: list[str]) -> list[dict[str, Any]]:
    if type(events) is not list or not all(type(item) is dict for item in events):
        raise ProviderError("raw events must be an object list")
    sanitized = [_redact(event, secrets) for event in events]
    visible = canonical_json(sanitized)
    if any(secret and secret in visible for secret in secrets):
        raise ProviderError("secret remained in sanitized events")
    return sanitized


class EvaluationCapability:
    __slots__ = ("request_sha256", "authority_sha256", "spec_sha256")

    def __init__(self, key: object, request: str, authority: str, spec: str):
        if key is not _CAPABILITY_KEY:
            raise ProviderError("evaluation capability is host-minted only")
        self.request_sha256 = request
        self.authority_sha256 = authority
        self.spec_sha256 = spec

    def __reduce__(self):
        raise TypeError("evaluation capability is process-local")


class ReleaseCapability:
    __slots__ = ("request_sha256", "authority_sha256")

    def __init__(self, key: object, request: str, authority: str):
        if key is not _CAPABILITY_KEY:
            raise ProviderError("release capability is host-minted only")
        self.request_sha256 = request
        self.authority_sha256 = authority

    def __reduce__(self):
        raise TypeError("release capability is process-local")


def _validate_supplied_authority(value: dict[str, Any], scope: str, request: str) -> None:
    if type(value) is not dict or set(value) != {"scope", "request_sha256", "nonce", "signature"}:
        raise ProviderError("external authority fields differ")
    if value["scope"] != scope or value["request_sha256"] != request:
        raise ProviderError("external authority does not bind the request")
    if not all(type(value[field]) is str and value[field] for field in ("nonce", "signature")):
        raise ProviderError("external authority proof is empty")


def accept_evaluation_authority(
    spec: dict[str, Any], supplied: dict[str, Any],
    external_verifier: Callable[[dict[str, Any]], bool],
) -> EvaluationCapability:
    validate_eval_spec(spec)
    _validate_supplied_authority(supplied, "evaluation", spec["authority_request_sha256"])
    if not external_verifier(supplied):
        raise ProviderError("external verifier rejected evaluation authority")
    return EvaluationCapability(
        _CAPABILITY_KEY, supplied["request_sha256"],
        canonical_sha256(supplied), spec["record_sha256"],
    )


def release_authority_request(
    *, product_record_sha256: str, attestation_sha256s: list[str],
    destination_sha256: str, rollback_sha256: str,
) -> str:
    return canonical_sha256(
        {
            "scope": "release", "product_record_sha256": product_record_sha256,
            "attestation_sha256s": sorted(attestation_sha256s),
            "destination_sha256": destination_sha256,
            "rollback_sha256": rollback_sha256,
        }
    )


def accept_release_authority(
    request_sha256: str, supplied: dict[str, Any],
    external_verifier: Callable[[dict[str, Any]], bool],
) -> ReleaseCapability:
    _validate_supplied_authority(supplied, "release", request_sha256)
    if not external_verifier(supplied):
        raise ProviderError("external verifier rejected release authority")
    return ReleaseCapability(_CAPABILITY_KEY, request_sha256, canonical_sha256(supplied))
