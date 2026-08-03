from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from evaluation.host import ExternalProofVerifier, HostEvidenceError, verify_host_evidence
from evaluation.holdout import judge_fixed_holdouts
from evaluation.manifest import load_production_inputs
from evaluation.oracle import hidden_oracle_for, score_hidden
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
        for field in ("product_semantic_sha256", "external_role_config_sha256", "provider_component_sha256", "host_contract_sha256")
    )
    global_oracle_change = previous["oracle_component_sha256"] != current["oracle_component_sha256"]
    for unit_id, unit in new.items():
        prior = old.get(unit_id)
        if global_provider_change or prior is None or prior["provider_input_sha256"] != unit["provider_input_sha256"]:
            model.add(unit_id)
        elif global_oracle_change:
            (model if unit["stage"] == "exact_final" else replay).add(unit_id)
        elif prior["oracle_sha256"] != unit["oracle_sha256"]:
            (model if unit["stage"] == "exact_final" else replay).add(unit_id)
        elif prior["harness_sha256"] != unit["harness_sha256"]:
            offline.add(unit_id)
    removed = set(old) - set(new)
    if removed or previous["harness_component_sha256"] != current["harness_component_sha256"]:
        offline.add("__bundle__")
    if previous["manifest_sha256"] != current["manifest_sha256"]:
        offline.add("__manifest__")
    if previous["fixtures_sha256"] != current["fixtures_sha256"] and not model:
        offline.add("__fixtures__")
    if previous["response_schemas_sha256"] != current["response_schemas_sha256"] and not model:
        offline.add("__response_schemas__")
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
    host_proof: dict[str, Any],
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
    if parent["external_role_config_sha256"] != unit["external_role_config_sha256"]:
        raise VerificationError("external role config changed; replay is forbidden")
    passed, diagnostics = oracle(parent["observation"]["report"])
    observation = {
        **parent["observation"],
        "parent_attestation_sha256": parent["record_sha256"],
    }
    return build_attestation(
        kind="replay", unit_id=unit["unit_id"],
        product_semantic_sha256=parent["product_semantic_sha256"],
        product_artifact_sha256=None,
        external_role_config_sha256=unit["external_role_config_sha256"],
        provider_input_sha256=unit["provider_input_sha256"],
        oracle_sha256=unit["oracle_sha256"], harness_sha256=unit["harness_sha256"],
        invocation_sha256=unit["invocation_sha256"],
        authority_sha256=parent["authority_sha256"],
        host_claim_key=parent["host_claim_key"],
        host_proof_sha256=canonical_sha256(host_proof), observation=observation,
        terminal=parent["terminal"], verdict="pass" if passed else "fail",
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


def _time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise VerificationError("evidence timestamp is invalid") from exc
    if parsed.tzinfo is None:
        raise VerificationError("evidence timestamp lacks timezone")
    return parsed.astimezone(timezone.utc)


def verify_evaluation(
    *, root: Path, product: dict[str, Any], spec: dict[str, Any],
    attestations: list[dict[str, Any]], raw_streams: dict[str, bytes],
    host_proofs: dict[str, dict[str, Any]],
    proof_verifier: ExternalProofVerifier,
    previous_product: dict[str, Any] | None = None,
    holdout_mapping: dict[str, dict[str, str]] | None = None,
    mapping_revealed_at: str | None = None,
) -> dict[str, Any]:
    validate_product_artifact(product)
    validate_eval_spec(spec)
    if product["package_semantic_sha256"] != spec["product_semantic_sha256"] or product["external_role_config_sha256"] != spec["external_role_config_sha256"]:
        raise VerificationError("ProductArtifact does not match EvalSpec")
    inputs = load_production_inputs(root)
    for field in ("manifest_sha256", "fixtures_sha256", "oracles_sha256", "response_schemas_sha256"):
        if spec[field] != inputs[field]:
            raise VerificationError(f"EvalSpec {field} differs from production input")
    planned = _unit_map(spec)
    by_unit: dict[str, dict[str, Any]] = {}
    assessments: dict[str, dict[str, Any]] = {}
    authority: str | None = None
    totals = {"model_calls": 0, "input_tokens": 0, "output_tokens": 0, "wall_milliseconds": 0}
    for record in attestations:
        validate_attestation(record)
        unit = planned.get(record["unit_id"])
        if unit is None or record["unit_id"] in by_unit:
            raise VerificationError("unknown or duplicate attestation unit")
        for field in ("external_role_config_sha256", "provider_input_sha256", "oracle_sha256", "harness_sha256", "invocation_sha256"):
            if record[field] != unit[field]:
                raise VerificationError(f"attestation {field} mismatch")
        if record["host_claim_key"] != unit["invocation"]["claim_key"]:
            raise VerificationError("attestation host claim mismatch")
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
        if record["unit_id"] not in raw_streams or record["unit_id"] not in host_proofs:
            raise VerificationError("attestation lacks external raw/proof evidence")
        try:
            parsed = verify_host_evidence(
                record=record, unit=unit, spec=spec,
                raw=raw_streams[record["unit_id"]],
                proof=host_proofs[record["unit_id"]],
                external_verifier=proof_verifier,
            )
        except HostEvidenceError as exc:
            raise VerificationError(str(exc)) from exc
        observation = record["observation"]
        if _time(observation["started_at"]) > _time(observation["frozen_at"]):
            raise VerificationError("Attestation timestamps run backwards")
        if (
            parsed["terminal"] != record["terminal"]
            or parsed["started_at"] != observation["started_at"]
            or parsed["frozen_at"] != observation["frozen_at"]
        ):
            raise VerificationError("Attestation does not reproduce from raw evidence")
        provenance = observation["provenance"]
        if provenance["provider"] != "external-host" or any(
            provenance[field] != unit["invocation"][field]
            for field in ("model", "effort", "tools", "timeout_seconds")
        ):
            raise VerificationError("Attestation provenance differs from invocation")
        assessment = score_hidden(
            observation["report"], hidden_oracle_for(inputs, unit), stage=unit["stage"]
        )
        expected_verdict = (
            "pass" if assessment["passed"] and parsed["terminal"]["classification"] == "success"
            else "fail"
        )
        if record["verdict"] != expected_verdict:
            raise VerificationError("Attestation verdict differs from hidden oracle recomputation")
        expected_diagnostics = [f"fatal:{path}" for path in assessment["fatal"]]
        expected_diagnostics.extend(f"diagnostic:{path}" for path in assessment["diagnostics"])
        if record["diagnostics"] != expected_diagnostics:
            raise VerificationError("Attestation diagnostics differ from hidden oracle recomputation")
        assessments[record["unit_id"]] = assessment
        for field in totals:
            totals[field] += parsed["terminal"][field]
            if totals[field] > spec["total_cap"][field]:
                raise VerificationError(f"evaluation exceeds total cap: {field}")
        by_unit[record["unit_id"]] = record
    if set(raw_streams) != set(by_unit) or set(host_proofs) != set(by_unit):
        raise VerificationError("external raw/proof inventory differs from attestations")
    failures = [
        {"unit_id": unit_id, "classification": record["terminal"]["classification"], "verdict": record["verdict"]}
        for unit_id, record in by_unit.items()
        if record["verdict"] != "pass" or record["terminal"]["classification"] != "success"
    ]
    stage_units = {
        stage: {unit["unit_id"] for unit in planned.values() if unit["stage"] == stage}
        for stage in ("behavior", "holdout", "exact_final")
    }
    supplied = set(by_unit)
    if supplied & stage_units["holdout"] and not stage_units["behavior"].issubset(supplied):
        raise VerificationError("holdout started before behavior froze")
    if supplied & stage_units["holdout"]:
        behavior_frozen = max(_time(by_unit[unit_id]["observation"]["frozen_at"]) for unit_id in stage_units["behavior"])
        holdout_started = min(_time(by_unit[unit_id]["observation"]["started_at"]) for unit_id in supplied & stage_units["holdout"])
        if holdout_started <= behavior_frozen:
            raise VerificationError("holdout started before all behavior froze")
    if supplied & stage_units["exact_final"] and not (
        stage_units["behavior"] | stage_units["holdout"]
    ).issubset(supplied):
        raise VerificationError("exact-final started before behavior and holdout froze")
    if failures:
        failed_order = min(planned[item["unit_id"]]["order"] for item in failures)
        if any(planned[unit_id]["order"] > failed_order for unit_id in supplied):
            raise VerificationError("calls continued after a terminal failure")
        cutoff = min(_time(by_unit[item["unit_id"]]["observation"]["frozen_at"]) for item in failures)
        earliest = {
            item["unit_id"] for item in failures
            if _time(by_unit[item["unit_id"]]["observation"]["frozen_at"]) == cutoff
        }
        if any(
            unit_id not in earliest
            and _time(record["observation"]["started_at"]) >= cutoff
            for unit_id, record in by_unit.items()
        ):
            raise VerificationError("calls continued after a known terminal failure")
    exact_final = by_unit.get("exact-final")
    if exact_final is not None:
        prior = stage_units["behavior"] | stage_units["holdout"]
        prior_frozen = max(_time(by_unit[unit_id]["observation"]["frozen_at"]) for unit_id in prior)
        if _time(exact_final["observation"]["started_at"]) <= prior_frozen:
            raise VerificationError("exact-final started before prior stages froze")
    holdout = None
    full_success = not failures and supplied == set(planned)
    if full_success and (holdout_mapping is None or mapping_revealed_at is None):
        raise VerificationError("successful evaluation requires holdout mapping and reveal")
    if holdout_mapping is not None or mapping_revealed_at is not None:
        if holdout_mapping is None or mapping_revealed_at is None or previous_product is None:
            raise VerificationError("holdout mapping and reveal time are inseparable")
        validate_product_artifact(previous_product)
        if previous_product["record_sha256"] != spec["previous_product_record_sha256"]:
            raise VerificationError("holdout baseline is not the previous released product")
        holdout_units = {unit for pair in spec["holdouts"] for unit in pair["unit_ids"]}
        if not holdout_units.issubset(supplied):
            raise VerificationError("holdout mapping was supplied before all outputs froze")
        holdout = judge_fixed_holdouts(
            spec=spec, attestations=[by_unit[unit] for unit in sorted(holdout_units)],
            assessments={unit: assessments[unit] for unit in holdout_units},
            mapping=holdout_mapping, revealed_at=mapping_revealed_at,
            candidate_product=product, previous_product=previous_product,
        )
        if not holdout["passed"]:
            if exact_final is not None:
                raise VerificationError("calls continued after fixed-holdout failure")
            failures.append({"unit_id": "fixed-holdouts", "classification": "quality_failure", "verdict": "fail"})
        if exact_final is not None and _time(mapping_revealed_at) >= _time(exact_final["observation"]["started_at"]):
            raise VerificationError("exact-final started before holdout mapping reveal")
    if not failures and supplied != set(planned):
        raise VerificationError("successful evaluation lacks planned attestations")
    return {
        "verified": not failures, "failures": failures,
        "product_record_sha256": product["record_sha256"],
        "eval_spec_sha256": spec["record_sha256"],
        "attestation_sha256s": sorted(record["record_sha256"] for record in attestations),
        "exact_final_attestation_sha256": exact_final["record_sha256"] if exact_final else None,
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
