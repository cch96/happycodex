"""Closed provider inputs and deterministic request identities only."""
from __future__ import annotations

import json
from typing import Any

from evaluation.canonical import (
    ContractError,
    canonical_sha256,
    canonical_text,
    exact,
    integer,
    sha256,
    text,
)
from evaluation.identity import validate_review_projection
from evaluation.policy import (
    EXACT_FINAL_ROLE_ID,
    HOLDOUT_ROLE_ID,
    SCHEMA_VERSION,
    UnitTopology,
    exact_final_review_policy,
)
from evaluation.records import (
    validate_eval_spec,
    validate_product_artifact,
)
from evaluation.schemas import validate_instance, validate_schema


class ProviderError(ContractError):
    pass


def _closed_schema_text(schema: dict[str, Any]) -> str:
    validate_schema(schema)
    return canonical_text(schema)


def materialize_provider_input(
    public_inputs: dict[str, Any],
    *,
    stage: str,
    role_id: str,
    guidance: str,
    sample_id: str | None = None,
) -> dict[str, Any]:
    """Build behavior/holdout input from cases and closed schemas only."""
    exact(public_inputs, {"cases", "schemas"}, "public provider inputs")
    cases = public_inputs["cases"]
    schemas = public_inputs["schemas"]
    text(guidance, "guidance")
    if stage == "behavior":
        if sample_id is not None or role_id not in cases["core"]:
            raise ProviderError("behavior provider routing differs")
        case = cases["core"][role_id]
        input_schema = schemas["provider_inputs"][role_id]
        output_schema = schemas["provider_outputs"][role_id]
    elif stage == "holdout":
        if role_id != HOLDOUT_ROLE_ID or sample_id not in cases["holdouts"]:
            raise ProviderError("holdout provider routing differs")
        case = cases["holdouts"][sample_id]
        input_schema = schemas["provider_inputs"]["holdout"]
        output_schema = schemas["provider_outputs"][sample_id]
    else:
        raise ProviderError("exact-final uses its fixed materializer")
    value = {
        "prompt": case["prompt"],
        "context": case["context"],
        "workspace": case["workspace"],
        "guidance": guidance,
        "response_schema": _closed_schema_text(output_schema),
    }
    try:
        return validate_instance(input_schema, value, "provider_input")
    except ContractError as exc:
        raise ProviderError(str(exc)) from exc


def review_contract_sha256(public_inputs: dict[str, Any]) -> str:
    exact(public_inputs, {"cases", "schemas"}, "public provider inputs")
    schemas = public_inputs["schemas"]
    input_schema = schemas["provider_inputs"]["exact-final"]
    output_schema = schemas["provider_outputs"]["exact_final"]
    validate_schema(input_schema, "exact-final input schema")
    validate_schema(output_schema, "exact-final output schema")
    return canonical_sha256(
        {
            "review_policy": exact_final_review_policy(),
            "input_schema": input_schema,
            "response_schema": output_schema,
        }
    )


def _snapshot_product_binding(
    product: dict[str, Any], snapshot: dict[str, Any], label: str
) -> None:
    entries = {entry["path"]: entry for entry in snapshot["entries"]}
    product_entries = {
        entry["path"]: entry
        for projection in product["projections"].values()
        for entry in projection["entries"]
    }
    for path, product_entry in product_entries.items():
        snapshot_entry = entries.get(path)
        if product_entry["state"] == "absent":
            if snapshot_entry is not None:
                raise ProviderError(f"{label} deleted product input is present")
            continue
        if snapshot_entry is None:
            raise ProviderError(f"{label} product input is absent from review")
        if (
            snapshot_entry["mode"] != product_entry["mode"]
            or snapshot_entry["sha256"] != product_entry["sha256"]
            or snapshot_entry["size_bytes"] != product_entry["size_bytes"]
        ):
            raise ProviderError(f"{label} product input identity differs")


def materialize_exact_final_input(
    public_inputs: dict[str, Any],
    *,
    previous_product: dict[str, Any],
    candidate_product: dict[str, Any],
    review_projection: dict[str, Any],
) -> dict[str, Any]:
    """Derive the only exact-final input; caller-authored briefs are impossible."""
    exact(public_inputs, {"cases", "schemas"}, "public provider inputs")
    validate_product_artifact(previous_product)
    validate_product_artifact(candidate_product)
    validate_review_projection(review_projection)
    _snapshot_product_binding(
        previous_product, review_projection["baseline"], "previous product"
    )
    _snapshot_product_binding(
        candidate_product, review_projection["candidate"], "candidate product"
    )
    schemas = public_inputs["schemas"]
    contract_sha = review_contract_sha256(public_inputs)
    value = {
        "review_policy": canonical_text(exact_final_review_policy()),
        "review_policy_sha256": contract_sha,
        "previous_product_artifact": canonical_text(previous_product),
        "previous_product_artifact_sha256": previous_product["artifact_sha256"],
        "candidate_product_artifact": canonical_text(candidate_product),
        "candidate_product_artifact_sha256": candidate_product["artifact_sha256"],
        "review_projection": canonical_text(review_projection),
        "review_projection_sha256": review_projection["projection_sha256"],
        "response_schema": _closed_schema_text(
            schemas["provider_outputs"]["exact_final"]
        ),
    }
    try:
        return validate_instance(
            schemas["provider_inputs"]["exact-final"],
            value,
            "exact_final_provider_input",
        )
    except ContractError as exc:
        raise ProviderError(str(exc)) from exc


def parse_provider_report(
    *, raw: bytes, schema: dict[str, Any]
) -> dict[str, Any]:
    validate_schema(schema)
    if type(raw) is not bytes:
        raise ProviderError("provider report is not bytes")
    try:
        report = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProviderError("provider report is not one UTF-8 JSON value") from exc
    try:
        return validate_instance(schema, report, "provider_report")
    except ContractError as exc:
        raise ProviderError(str(exc)) from exc


def provider_projection(public_inputs: dict[str, Any]) -> str:
    exact(public_inputs, {"cases", "schemas"}, "public provider inputs")
    return canonical_sha256(public_inputs)


def exact_final_effect_subject(
    *,
    candidate_product_artifact_sha256: str,
    review_contract_sha256_value: str,
) -> str:
    sha256(
        candidate_product_artifact_sha256,
        "candidate_product_artifact_sha256",
    )
    sha256(review_contract_sha256_value, "review_contract_sha256")
    return canonical_sha256(
        {
            "purpose": "happycodex-exact-final-effect-v3",
            "candidate_product_artifact_sha256":
                candidate_product_artifact_sha256,
            "review_contract_sha256": review_contract_sha256_value,
        }
    )


def derive_unit_identities(
    *,
    topology: UnitTopology,
    provider_input_sha256: str,
    provider_input_component_sha256: str,
    candidate_product_artifact_sha256: str,
    review_contract_sha256_value: str,
) -> tuple[str, str]:
    for value, label in (
        (provider_input_sha256, "provider_input_sha256"),
        (provider_input_component_sha256, "provider_input_component_sha256"),
    ):
        sha256(value, label)
    invocation = canonical_sha256(
        {
            "purpose": "happycodex-provider-invocation-v3",
            "unit": topology._asdict(),
            "provider_input_sha256": provider_input_sha256,
            "provider_input_component_sha256":
                provider_input_component_sha256,
        }
    )
    if topology.unit_id == EXACT_FINAL_ROLE_ID:
        effect = exact_final_effect_subject(
            candidate_product_artifact_sha256=
                candidate_product_artifact_sha256,
            review_contract_sha256_value=review_contract_sha256_value,
        )
    else:
        effect = canonical_sha256(
            {
                "purpose": "happycodex-provider-effect-v3",
                "invocation_sha256": invocation,
            }
        )
    return invocation, effect


def evaluation_authority_request_payload(
    spec: dict[str, Any],
    *,
    expected_component_identities: dict[str, str],
    product: dict[str, Any],
    previous_product: dict[str, Any],
) -> dict[str, Any]:
    """Build an unsigned request only after caller-supplied identities agree."""
    validate_eval_spec(spec)
    validate_product_artifact(product)
    validate_product_artifact(previous_product)
    exact(
        expected_component_identities,
        {"provider_input", "oracle", "harness"},
        "expected_component_identities",
    )
    for name, identity in expected_component_identities.items():
        sha256(identity, f"expected_component_identities.{name}")
    if spec["component_identities"] != expected_component_identities:
        raise ProviderError("evaluator source identity drifted")
    if (
        spec["product_artifact_sha256"] != product["artifact_sha256"]
        or spec["previous_product_artifact_sha256"]
        != previous_product["artifact_sha256"]
    ):
        raise ProviderError("authority product identity differs")
    body = {
        "purpose": "happycodex-evaluation-v3",
        "schema_version": SCHEMA_VERSION,
        "spec_sha256": spec["spec_sha256"],
        "spec_subject_sha256": spec["spec_subject_sha256"],
        "product_artifact_sha256": product["artifact_sha256"],
        "previous_product_artifact_sha256":
            previous_product["artifact_sha256"],
        "review_contract_sha256": spec["review_contract_sha256"],
        "effect_subjects": [
            unit["effect_subject_sha256"] for unit in spec["units"]
        ],
        "caps_sha256": canonical_sha256(spec["caps"]),
    }
    return {**body, "request_sha256": canonical_sha256(body)}


def unit_effect_request_payload(
    spec: dict[str, Any],
    *,
    unit_id: str,
    provider_input: dict[str, Any],
    product_artifact_sha256: str,
    evaluation_authority_request_sha256: str,
    authority_identity: str,
    authority_sha256: str,
    attempt: int,
    recovery_history_sha256: str,
) -> dict[str, Any]:
    """Construct one unsigned external-effect request without invoking it."""
    validate_eval_spec(spec)
    matches = [unit for unit in spec["units"] if unit["unit_id"] == unit_id]
    if len(matches) != 1:
        raise ProviderError("effect request unit differs")
    unit = matches[0]
    if canonical_sha256(provider_input) != unit["provider_input_sha256"]:
        raise ProviderError("effect request provider input differs")
    allowed_products = (
        {
            spec["product_artifact_sha256"],
            spec["previous_product_artifact_sha256"],
        }
        if unit["stage"] == "holdout"
        else {spec["product_artifact_sha256"]}
    )
    if product_artifact_sha256 not in allowed_products:
        raise ProviderError("effect request product differs")
    sha256(
        evaluation_authority_request_sha256,
        "evaluation_authority_request_sha256",
    )
    text(authority_identity, "authority_identity")
    sha256(authority_sha256, "authority_sha256")
    integer(attempt, "attempt")
    sha256(recovery_history_sha256, "recovery_history_sha256")
    body = {
        "schema_version": SCHEMA_VERSION,
        "spec_sha256": spec["spec_sha256"],
        "spec_subject_sha256": spec["spec_subject_sha256"],
        "product_artifact_sha256": product_artifact_sha256,
        "unit_id": unit_id,
        "stage": unit["stage"],
        "provider_input_sha256": unit["provider_input_sha256"],
        "invocation_sha256": unit["invocation_sha256"],
        "effect_subject_sha256": unit["effect_subject_sha256"],
        "attempt": attempt,
        "attempt_identity_sha256": canonical_sha256(
            {
                "effect_subject_sha256": unit["effect_subject_sha256"],
                "attempt": attempt,
            }
        ),
        "recovery_history_sha256": recovery_history_sha256,
        "evaluation_authority_request_sha256":
            evaluation_authority_request_sha256,
        "authority_identity": authority_identity,
        "authority_sha256": authority_sha256,
        "provider_input": provider_input,
    }
    return {**body, "request_sha256": canonical_sha256(body)}


def release_effect_subject(
    *,
    product_artifact_sha256: str,
    destination: str,
    target_identity: str,
    rollback_identity: str,
    installed_projection_sha256: str,
) -> str:
    for value, label in (
        (product_artifact_sha256, "product_artifact_sha256"),
        (installed_projection_sha256, "installed_projection_sha256"),
    ):
        sha256(value, label)
    for value, label in (
        (destination, "destination"),
        (target_identity, "target_identity"),
        (rollback_identity, "rollback_identity"),
    ):
        text(value, label)
    return canonical_sha256(
        {
            "purpose": "happycodex-release-effect-v3",
            "product_artifact_sha256": product_artifact_sha256,
            "destination": destination,
            "target_identity": target_identity,
            "rollback_identity": rollback_identity,
            "installed_projection_sha256": installed_projection_sha256,
        }
    )


def release_authority_request_payload(
    *,
    product_artifact_sha256: str,
    eval_spec_sha256: str,
    prerequisite_attestation_sha256s: list[str],
    exact_final_attestation_sha256: str,
    holdout_result_sha256: str,
    release_effect_subject_sha256: str,
) -> dict[str, Any]:
    for value, label in (
        (product_artifact_sha256, "product_artifact_sha256"),
        (eval_spec_sha256, "eval_spec_sha256"),
        (exact_final_attestation_sha256, "exact_final_attestation_sha256"),
        (holdout_result_sha256, "holdout_result_sha256"),
        (release_effect_subject_sha256, "release_effect_subject_sha256"),
    ):
        sha256(value, label)
    if (
        type(prerequisite_attestation_sha256s) is not list
        or prerequisite_attestation_sha256s
        != sorted(set(prerequisite_attestation_sha256s))
    ):
        raise ProviderError("release prerequisites are not sorted and unique")
    for identity in prerequisite_attestation_sha256s:
        sha256(identity, "prerequisite_attestation_sha256s[]")
    if exact_final_attestation_sha256 not in prerequisite_attestation_sha256s:
        raise ProviderError("exact-final is not a release prerequisite")
    body = {
        "purpose": "happycodex-release-v3",
        "schema_version": SCHEMA_VERSION,
        "product_artifact_sha256": product_artifact_sha256,
        "eval_spec_sha256": eval_spec_sha256,
        "prerequisite_attestation_sha256s":
            prerequisite_attestation_sha256s,
        "exact_final_attestation_sha256":
            exact_final_attestation_sha256,
        "holdout_result_sha256": holdout_result_sha256,
        "release_effect_subject_sha256": release_effect_subject_sha256,
    }
    return {**body, "request_sha256": canonical_sha256(body)}


__all__ = (
    "ProviderError",
    "derive_unit_identities",
    "evaluation_authority_request_payload",
    "exact_final_effect_subject",
    "materialize_exact_final_input",
    "materialize_provider_input",
    "parse_provider_report",
    "provider_projection",
    "release_authority_request_payload",
    "release_effect_subject",
    "review_contract_sha256",
    "unit_effect_request_payload",
)
