"""Pure constructors for externally observed and authenticated terminals."""
from __future__ import annotations

from typing import Any

from evaluation.canonical import ContractError, canonical_sha256, exact
from evaluation.policy import SCHEMA_VERSION
from evaluation.records import build_attestation, build_release_receipt
from evaluation.verify import assess_provider_report

class HostConstructionError(ContractError):
    pass

def _binding(statement: dict[str, Any], binding: dict[str, Any]) -> dict[str, Any]:
    exact(binding, {"authenticator_id", "evidence_sha256", "signature"}, "evidence binding")
    if binding["evidence_sha256"] != canonical_sha256(statement):
        raise HostConstructionError("evidence binding does not cover the statement")
    return binding

def construct_attestation(
    statement: dict[str, Any], binding: dict[str, Any], *,
    response_schema: dict[str, Any], oracle: dict[str, Any] | None,
    provider_input: dict[str, Any],
) -> dict[str, Any]:
    """Seal one external provider terminal without authenticating its signature."""
    fields = {
        "kind", "schema_version", "spec_sha256", "spec_subject_sha256",
        "product_artifact_sha256", "unit_id", "stage", "provider_input_sha256",
        "invocation_sha256", "effect_subject_sha256", "attempt",
        "attempt_identity_sha256", "evaluation_authority_request_sha256",
        "authority_identity", "authority_sha256", "report", "observation",
        "effect_outcome",
    }
    exact(statement, fields, "provider terminal statement")
    if statement["kind"] != "provider_terminal" or statement["schema_version"] != SCHEMA_VERSION:
        raise HostConstructionError("provider terminal statement header differs")
    assessment = assess_provider_report(
        statement["report"], stage=statement["stage"], response_schema=response_schema,
        oracle=oracle, provider_input=provider_input,
    )
    values = {key: statement[key] for key in fields - {"kind", "schema_version", "report"}}
    return build_attestation(
        **values, claim={
            "report": statement["report"],
            "report_sha256": canonical_sha256(statement["report"]),
        }, evidence_binding=_binding(statement, binding), assessment=assessment,
    )

def construct_release_receipt(
    statement: dict[str, Any], binding: dict[str, Any],
) -> dict[str, Any]:
    """Seal one external release terminal without authenticating its signature."""
    fields = {
        "kind", "schema_version", "product_artifact_sha256", "eval_spec_sha256",
        "spec_subject_sha256", "prerequisite_attestation_sha256s",
        "exact_final_attestation_sha256", "holdout_result_sha256",
        "release_authority_request_sha256", "release_authority_identity",
        "release_authority_sha256", "release_effect_subject_sha256", "attempt",
        "attempt_identity_sha256", "destination", "target_identity",
        "rollback_identity", "installed_projection", "observation", "outcome",
    }
    exact(statement, fields, "release terminal statement")
    if statement["kind"] != "release_terminal" or statement["schema_version"] != SCHEMA_VERSION:
        raise HostConstructionError("release terminal statement header differs")
    values = {key: statement[key] for key in fields - {"kind", "schema_version"}}
    return build_release_receipt(**values, evidence_binding=_binding(statement, binding))

def external_boundary_notice() -> str:
    return (
        "These constructors cannot create authority, authenticate evidence, invoke an effect, "
        "enforce one-shot behavior, supply trusted time, decide recovery, or prove readback."
    )

__all__ = (
    "HostConstructionError", "construct_attestation", "construct_release_receipt",
    "external_boundary_notice",
)
