from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from evaluation.records import (
    RecordError,
    build_attestation,
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
    required = {"role_id", "fixture_sha256", "prompt"}
    if not required.issubset(case):
        raise ProviderError("case lacks provider-visible inputs")
    projection = {
        "schema_version": 1,
        "role_id": case["role_id"],
        "sample_id": case.get("sample_id"),
        "product_semantic_sha256": product_semantic_sha256,
        "external_role_config_sha256": external_role_config_sha256,
        "fixture_sha256": case["fixture_sha256"],
        "prompt": case["prompt"],
        "runtime_sha256": case.get("runtime_sha256"),
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
            if key not in {"secret", "token", "credential", "raw_stdin"}
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


@dataclass
class InvocationJournal:
    """Ephemeral operational cache; never serialized or used as evidence."""

    used: set[str] = field(default_factory=set)
    usage: dict[str, int] = field(
        default_factory=lambda: {
            "model_calls": 0, "input_tokens": 0, "output_tokens": 0,
            "wall_milliseconds": 0, "infrastructure_recoveries": 0,
        }
    )

    def reserve(self, invocation_sha256: str) -> None:
        if invocation_sha256 in self.used:
            raise ProviderError("invocation is one-shot and already reserved")
        self.used.add(invocation_sha256)

    def account(self, terminal: dict[str, Any], cap: dict[str, int]) -> None:
        mapping = {
            "model_calls": "model_calls", "input_tokens": "input_tokens",
            "output_tokens": "output_tokens", "wall_milliseconds": "wall_milliseconds",
        }
        for target, source in mapping.items():
            self.usage[target] += terminal[source]
            if self.usage[target] > cap[target]:
                raise ProviderError(f"evaluation cap exceeded: {target}")


def may_recover_infrastructure(
    terminal: dict[str, Any], *, recoveries_used: int, recovery_cap: int,
) -> bool:
    return (
        terminal.get("classification") == "infrastructure_no_effect"
        and terminal.get("provider_reached") is False
        and terminal.get("model_calls") == 0
        and recoveries_used < recovery_cap
    )


def _find_unit(spec: dict[str, Any], unit_id: str) -> dict[str, Any]:
    matches = [unit for unit in spec["units"] if unit["unit_id"] == unit_id]
    if len(matches) != 1:
        raise ProviderError("unit is not uniquely planned")
    return matches[0]


def run_fake_provider(
    *, product: dict[str, Any], spec: dict[str, Any], unit_id: str,
    projection: dict[str, Any], capability: EvaluationCapability,
    journal: InvocationJournal,
    provider: Callable[[dict[str, Any]], dict[str, Any]],
    oracle: Callable[[dict[str, Any]], tuple[bool, list[str]]],
    secrets: list[str] | None = None,
    visible_surface: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Exercise the real transaction shape with an offline callable provider."""
    validate_product_artifact(product)
    validate_eval_spec(spec)
    if capability.spec_sha256 != spec["record_sha256"] or capability.request_sha256 != spec["authority_request_sha256"]:
        raise ProviderError("evaluation capability identity drift")
    unit = _find_unit(spec, unit_id)
    if product["package_semantic_sha256"] != unit["product_semantic_sha256"] or product["external_role_config_sha256"] != spec["external_role_config_sha256"]:
        raise ProviderError("product and planned unit differ")
    if canonical_sha256(projection) != unit["provider_input_sha256"]:
        raise ProviderError("provider projection drift")
    journal.reserve(unit["invocation_sha256"])
    result = provider(projection)
    if type(result) is not dict or set(result) != {"terminal", "report", "events", "started_at", "frozen_at"}:
        raise ProviderError("provider terminal envelope fields differ")
    terminal = result["terminal"]
    # The typed Attestation validator performs the complete terminal check.
    journal.account(terminal, spec["total_cap"])
    secret_values = secrets or []
    sanitized = sanitize_events(result["events"], secrets=secret_values)
    report = _redact(result["report"], secret_values)
    surface = visible_surface or {"workspace": {}, "argv": [], "stdin": "", "env": {}}
    assert_provider_blind(
        sentinels=secret_values, projection=projection,
        workspace=surface.get("workspace", {}), argv=surface.get("argv", []),
        stdin=surface.get("stdin", ""), env=surface.get("env", {}),
        sanitized_events=sanitized,
    )
    passed, diagnostics = oracle(report)
    verdict = "pass" if passed else "fail"
    if terminal["classification"] == "diagnostic":
        verdict = "diagnostic"
    elif terminal["classification"] != "success":
        verdict = "fail"
    observation = {
        "raw_events_sha256": canonical_sha256(result["events"]),
        "sanitized_event_sha256": canonical_sha256(sanitized),
        "terminal_sha256": canonical_sha256(terminal),
        "report": report, "report_sha256": canonical_sha256(report),
        "provenance": {
            "provider": "offline-fake-provider", "model": spec["profile"]["model"],
            "effort": spec["profile"]["effort"], "tools": spec["profile"]["tools"],
            "timeout_seconds": spec["profile"]["timeout_seconds"],
        },
        "parent_attestation_sha256": None,
        "started_at": result["started_at"], "frozen_at": result["frozen_at"],
    }
    return build_attestation(
        kind=unit["kind"], unit_id=unit_id,
        product_semantic_sha256=product["package_semantic_sha256"],
        product_artifact_sha256=(product["package_artifact_sha256"] if unit["kind"] == "exact_final" else None),
        provider_input_sha256=unit["provider_input_sha256"],
        oracle_sha256=unit["oracle_sha256"], harness_sha256=unit["harness_sha256"],
        invocation_sha256=unit["invocation_sha256"],
        authority_sha256=capability.authority_sha256,
        observation=observation, terminal=terminal, verdict=verdict,
        diagnostics=diagnostics,
    )
