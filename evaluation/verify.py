from __future__ import annotations

from typing import Any, Callable

from evaluation.holdout import judge_fixed_holdouts
from evaluation.provider import ReleaseCapability, release_authority_request
from evaluation.records import (
    RecordError,
    build_attestation,
    build_release_receipt,
    canonical_sha256,
    validate_attestation,
    validate_eval_spec,
    validate_product_artifact,
    validate_release_receipt,
)


class VerificationError(ValueError):
    pass


def _unit_map(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {unit["unit_id"]: unit for unit in spec["units"]}


def invalidation(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, list[str]]:
    """Return the minimum work implied by component identity changes."""
    validate_eval_spec(previous)
    validate_eval_spec(current)
    old = _unit_map(previous)
    new = _unit_map(current)
    model: set[str] = set()
    replay: set[str] = set()
    offline: set[str] = set()
    global_provider_change = any(
        previous[field] != current[field]
        for field in ("product_semantic_sha256", "external_role_config_sha256", "provider_component_sha256")
    ) or previous["profile"] != current["profile"]
    for unit_id, unit in new.items():
        prior = old.get(unit_id)
        if global_provider_change or prior is None or prior["provider_input_sha256"] != unit["provider_input_sha256"]:
            model.add(unit_id)
        elif prior["oracle_sha256"] != unit["oracle_sha256"]:
            replay.add(unit_id)
        elif prior["harness_sha256"] != unit["harness_sha256"]:
            offline.add(unit_id)
    removed = set(old) - set(new)
    if removed or previous["harness_component_sha256"] != current["harness_component_sha256"]:
        offline.add("__bundle__")
    if previous["oracle_component_sha256"] != current["oracle_component_sha256"] and not replay:
        offline.add("__oracle__")
    return {
        "model_units": sorted(model),
        "replay_units": sorted(replay - model),
        "offline_units": sorted(offline - model - replay),
    }


def _lookup(report: dict[str, Any], path: str) -> Any:
    value: Any = report
    for part in path.split("."):
        if type(value) is not dict or part not in value:
            return None
        value = value[part]
    return value


def evaluate_runtime_decision(
    report: dict[str, Any], oracle: dict[str, dict[str, Any]],
) -> tuple[bool, list[str]]:
    """Only invariant mismatches are fatal; conservative action labels diagnose."""
    if type(report) is not dict or set(oracle) != {"fatal", "diagnostic"}:
        raise VerificationError("runtime oracle is not typed")
    failures = [path for path, expected in oracle["fatal"].items() if _lookup(report, path) != expected]
    diagnostics = [
        f"equivalent-action:{path}:expected={expected!r}:actual={_lookup(report, path)!r}"
        for path, expected in oracle["diagnostic"].items()
        if _lookup(report, path) != expected
    ]
    return not failures, [*(f"fatal:{path}" for path in failures), *diagnostics]


def replay_attestation(
    *, parent: dict[str, Any], spec: dict[str, Any],
    oracle: Callable[[dict[str, Any]], tuple[bool, list[str]]],
) -> dict[str, Any]:
    validate_attestation(parent)
    validate_eval_spec(spec)
    if parent["kind"] not in {"behavior", "replay"}:
        raise VerificationError("only behavior observations can replay")
    unit = _unit_map(spec).get(parent["unit_id"])
    if unit is None or unit["kind"] != "behavior":
        raise VerificationError("replay unit is absent from EvalSpec")
    if parent["provider_input_sha256"] != unit["provider_input_sha256"]:
        raise VerificationError("provider input changed; replay is forbidden")
    passed, diagnostics = oracle(parent["observation"]["report"])
    terminal = {
        "classification": "diagnostic", "provider_reached": False,
        "complete": True, "model_calls": 0, "input_tokens": 0,
        "output_tokens": 0, "wall_milliseconds": 0,
    }
    observation = {
        **parent["observation"],
        "terminal_sha256": canonical_sha256(terminal),
        "parent_attestation_sha256": parent["record_sha256"],
    }
    return build_attestation(
        kind="replay", unit_id=unit["unit_id"],
        product_semantic_sha256=parent["product_semantic_sha256"],
        product_artifact_sha256=None,
        provider_input_sha256=unit["provider_input_sha256"],
        oracle_sha256=unit["oracle_sha256"], harness_sha256=unit["harness_sha256"],
        invocation_sha256=unit["invocation_sha256"],
        authority_sha256=parent["authority_sha256"], observation=observation,
        terminal=terminal, verdict="pass" if passed else "fail",
        diagnostics=diagnostics,
    )


def append_attestation(
    existing: list[dict[str, Any]], new: dict[str, Any],
) -> list[dict[str, Any]]:
    validate_attestation(new)
    for record in existing:
        validate_attestation(record)
        if record["unit_id"] == new["unit_id"]:
            if record["kind"] == "exact_final" and record["product_artifact_sha256"] == new["product_artifact_sha256"]:
                if record["verdict"] == "fail":
                    raise VerificationError("adverse exact-final is durable for unchanged artifact")
                raise VerificationError("exact-final invocation is one-shot for unchanged artifact")
            raise VerificationError("attestation unit already exists")
    return [*existing, new]


def verify_evaluation(
    *, product: dict[str, Any], spec: dict[str, Any],
    attestations: list[dict[str, Any]], previous_product: dict[str, Any] | None = None,
    holdout_mapping: dict[str, dict[str, str]] | None = None,
    mapping_revealed_at: str | None = None,
) -> dict[str, Any]:
    validate_product_artifact(product)
    validate_eval_spec(spec)
    if product["package_semantic_sha256"] != spec["product_semantic_sha256"] or product["external_role_config_sha256"] != spec["external_role_config_sha256"]:
        raise VerificationError("ProductArtifact does not match EvalSpec")
    planned = _unit_map(spec)
    by_unit: dict[str, dict[str, Any]] = {}
    authority: str | None = None
    totals = {"model_calls": 0, "input_tokens": 0, "output_tokens": 0, "wall_milliseconds": 0}
    for record in attestations:
        validate_attestation(record)
        unit = planned.get(record["unit_id"])
        if unit is None or record["unit_id"] in by_unit:
            raise VerificationError("unknown or duplicate attestation unit")
        for field in ("provider_input_sha256", "oracle_sha256", "harness_sha256", "invocation_sha256"):
            if record[field] != unit[field]:
                raise VerificationError(f"attestation {field} mismatch")
        if record["product_semantic_sha256"] != unit["product_semantic_sha256"]:
            raise VerificationError("attestation product semantic mismatch")
        if unit["kind"] == "exact_final":
            if record["kind"] != "exact_final" or record["product_artifact_sha256"] != product["package_artifact_sha256"]:
                raise VerificationError("exact-final does not bind exact artifact")
        elif record["kind"] not in {"behavior", "replay"}:
            raise VerificationError("behavior unit has wrong attestation kind")
        authority = authority or record["authority_sha256"]
        if record["authority_sha256"] != authority:
            raise VerificationError("more than one evaluation authority bundle was used")
        for field in totals:
            totals[field] += record["terminal"][field]
            if totals[field] > spec["total_cap"][field]:
                raise VerificationError(f"evaluation exceeds total cap: {field}")
        by_unit[record["unit_id"]] = record
    if set(by_unit) != set(planned):
        raise VerificationError("caller did not supply exactly one attestation per planned unit")
    failures = [
        {"unit_id": unit_id, "classification": record["terminal"]["classification"], "verdict": record["verdict"]}
        for unit_id, record in by_unit.items()
        if record["verdict"] != "pass" or record["terminal"]["classification"] != "success"
        and record["kind"] != "replay"
    ]
    exact_final = next(record for record in by_unit.values() if record["kind"] == "exact_final")
    if exact_final["observation"]["report"]["decision"] != "GO":
        failures.append({"unit_id": exact_final["unit_id"], "classification": "quality_failure", "verdict": "fail"})
    holdout = None
    if holdout_mapping is not None or mapping_revealed_at is not None:
        if holdout_mapping is None or mapping_revealed_at is None or previous_product is None:
            raise VerificationError("holdout mapping and reveal time are inseparable")
        validate_product_artifact(previous_product)
        if previous_product["record_sha256"] != spec["previous_product_record_sha256"]:
            raise VerificationError("holdout baseline is not the previous released product")
        holdout_units = {unit for pair in spec["holdouts"] for unit in pair["unit_ids"]}
        holdout = judge_fixed_holdouts(
            spec=spec, attestations=[by_unit[unit] for unit in sorted(holdout_units)],
            mapping=holdout_mapping, revealed_at=mapping_revealed_at,
            candidate_product=product, previous_product=previous_product,
        )
        if not holdout["passed"]:
            failures.append({"unit_id": "fixed-holdouts", "classification": "quality_failure", "verdict": "fail"})
    return {
        "verified": not failures, "failures": failures,
        "product_record_sha256": product["record_sha256"],
        "eval_spec_sha256": spec["record_sha256"],
        "attestation_sha256s": sorted(record["record_sha256"] for record in attestations),
        "exact_final_attestation_sha256": exact_final["record_sha256"],
        "authority_sha256": authority, "usage": totals, "holdout": holdout,
    }


def create_release_receipt(
    *, product: dict[str, Any], evaluation: dict[str, Any],
    isolated_install: dict[str, Any], destination: dict[str, Any],
    rollback: dict[str, Any], capability: ReleaseCapability,
) -> dict[str, Any]:
    validate_product_artifact(product)
    if evaluation.get("verified") is not True or evaluation.get("holdout", {}).get("passed") is not True:
        raise VerificationError("release requires a fully verified evaluation")
    request = release_authority_request(
        product_record_sha256=product["record_sha256"],
        attestation_sha256s=evaluation["attestation_sha256s"],
        destination_sha256=canonical_sha256(destination),
        rollback_sha256=canonical_sha256(rollback),
    )
    if capability.request_sha256 != request:
        raise VerificationError("release capability does not bind this effect")
    if capability.authority_sha256 == evaluation["authority_sha256"]:
        raise VerificationError("evaluation authority cannot authorize release")
    return build_release_receipt(
        product_record_sha256=product["record_sha256"],
        product_artifact_sha256=product["package_artifact_sha256"],
        attestation_sha256s=evaluation["attestation_sha256s"],
        exact_final_attestation_sha256=evaluation["exact_final_attestation_sha256"],
        isolated_install=isolated_install, destination=destination,
        rollback=rollback, release_authority_sha256=capability.authority_sha256,
    )


def verify_release(
    *, product: dict[str, Any], evaluation: dict[str, Any],
    receipt: dict[str, Any], destination: dict[str, Any], rollback: dict[str, Any],
) -> dict[str, Any]:
    validate_product_artifact(product)
    validate_release_receipt(receipt)
    if not evaluation.get("verified") or not evaluation.get("holdout", {}).get("passed"):
        raise VerificationError("release evaluation is not qualifying")
    checks = {
        "product": receipt["product_record_sha256"] == product["record_sha256"],
        "artifact": receipt["product_artifact_sha256"] == product["package_artifact_sha256"] == receipt["isolated_install"]["artifact_sha256"],
        "attestations": receipt["attestation_sha256s"] == evaluation["attestation_sha256s"],
        "exact_final": receipt["exact_final_attestation_sha256"] == evaluation["exact_final_attestation_sha256"],
        "destination": receipt["destination"] == destination,
        "rollback": receipt["rollback"] == rollback,
        "authority_separate": receipt["release_authority_sha256"] != evaluation["authority_sha256"],
    }
    if not all(checks.values()):
        raise VerificationError("ReleaseReceipt identity/effect mismatch")
    return {"verified": True, "checks": checks, "release_receipt_sha256": receipt["record_sha256"]}
