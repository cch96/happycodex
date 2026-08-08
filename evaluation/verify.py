"""Stateless verification over authenticated caller-supplied records."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Protocol

from evaluation.canonical import (
    ContractError, canonical_json, canonical_sha256, canonical_text, exact,
)
from evaluation.holdout import (
    VerifiedEffectTerminal, _verified_terminal, validate_holdout_result,
)
from evaluation.oracle import score_hidden
from evaluation.policy import FINDING_TYPES, UNIT_TOPOLOGY
from evaluation.provider import (
    exact_final_effect_subject, release_authority_request_payload,
    release_effect_subject,
)
from evaluation.records import (
    validate_attestation, validate_eval_spec, validate_product_artifact,
    validate_release_receipt,
)
from evaluation.schemas import validate_instance

class VerifyError(ContractError):
    pass

class ExternalAuthenticator(Protocol):
    authenticator_id: str
    def verify(self, statement: bytes, signature: str) -> bool: ...

class ExternalAuthorityValidator(Protocol):
    def validate(self, request_sha256: str, authority: dict[str, Any]) -> bool: ...

def _time(value: str) -> datetime:
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise VerifyError("authenticated timestamp is invalid") from exc
    if result.tzinfo is None:
        raise VerifyError("authenticated timestamp lacks timezone")
    return result.astimezone(timezone.utc)

def _unit(spec: dict[str, Any], unit_id: str) -> dict[str, Any]:
    matches = [unit for unit in spec["units"] if unit["unit_id"] == unit_id]
    if len(matches) != 1:
        raise VerifyError("unit differs from EvalSpec")
    return matches[0]

def _evaluation_request(spec: dict[str, Any]) -> dict[str, Any]:
    body = {
        "purpose": "happycodex-evaluation-v3",
        "schema_version": spec["schema_version"],
        "spec_sha256": spec["spec_sha256"],
        "spec_subject_sha256": spec["spec_subject_sha256"],
        "product_artifact_sha256": spec["product_artifact_sha256"],
        "previous_product_artifact_sha256": spec["previous_product_artifact_sha256"],
        "review_contract_sha256": spec["review_contract_sha256"],
        "effect_subjects": [unit["effect_subject_sha256"] for unit in spec["units"]],
        "caps_sha256": canonical_sha256(spec["caps"]),
    }
    return {**body, "request_sha256": canonical_sha256(body)}

def _authority(
    authority: dict[str, Any], *, request_sha256: str,
    validator: ExternalAuthorityValidator,
) -> tuple[str, str]:
    exact(authority, {
        "authority_identity", "request_sha256", "signature", "authority_sha256",
    }, "external authority")
    body = {key: authority[key] for key in (
        "authority_identity", "request_sha256", "signature",
    )}
    if (
        authority["request_sha256"] != request_sha256
        or authority["authority_sha256"] != canonical_sha256(body)
        or validator.validate(request_sha256, authority) is not True
    ):
        raise VerifyError("external authority is invalid")
    return authority["authority_identity"], authority["authority_sha256"]

def _authenticate(
    statement: dict[str, Any], binding: dict[str, Any],
    authenticator: ExternalAuthenticator,
) -> None:
    if (
        binding["authenticator_id"] != getattr(authenticator, "authenticator_id", None)
        or binding["evidence_sha256"] != canonical_sha256(statement)
        or authenticator.verify(canonical_json(statement), binding["signature"]) is not True
    ):
        raise VerifyError("external evidence authentication failed")

def attestation_evidence_statement(attestation: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "spec_sha256", "spec_subject_sha256", "product_artifact_sha256", "unit_id",
        "stage", "provider_input_sha256", "invocation_sha256", "effect_subject_sha256",
        "attempt", "attempt_identity_sha256", "evaluation_authority_request_sha256",
        "authority_identity", "authority_sha256",
    )
    return {
        "kind": "provider_terminal", "schema_version": attestation["schema_version"],
        **{field: attestation[field] for field in fields},
        "report": attestation["claim"]["report"],
        "observation": attestation["observation"],
        "effect_outcome": attestation["effect_outcome"],
    }

def release_evidence_statement(receipt: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "product_artifact_sha256", "eval_spec_sha256", "spec_subject_sha256",
        "prerequisite_attestation_sha256s", "exact_final_attestation_sha256",
        "holdout_result_sha256", "release_authority_request_sha256",
        "release_authority_identity", "release_authority_sha256",
        "release_effect_subject_sha256", "attempt", "attempt_identity_sha256",
        "destination", "target_identity", "rollback_identity", "installed_projection",
    )
    return {
        "kind": "release_terminal", "schema_version": receipt["schema_version"],
        **{field: receipt[field] for field in fields},
        "observation": receipt["observation"], "outcome": receipt["outcome"],
    }

def assess_provider_report(
    report: dict[str, Any], *, stage: str, response_schema: dict[str, Any],
    oracle: dict[str, Any] | None, provider_input: dict[str, Any],
) -> dict[str, Any]:
    if provider_input.get("response_schema") != canonical_text(response_schema):
        raise VerifyError("response schema differs from provider input")
    try:
        validate_instance(response_schema, report, "provider_report")
    except ContractError:
        return {"passed": False, "score": 0, "fatal": ["malformed_report"], "diagnostics": []}
    if stage != "exact_final":
        if oracle is None:
            raise VerifyError("hidden oracle is missing")
        return score_hidden(report, oracle)
    reviewed = {
        "candidate_product_artifact_sha256": provider_input["candidate_product_artifact_sha256"],
        "review_policy_sha256": provider_input["review_policy_sha256"],
        "review_projection_sha256": provider_input["review_projection_sha256"],
    }
    fatal: list[str] = []
    if report["neutral"] is not True:
        fatal.append("exact_final_non_neutral")
    if report["reviewed"] != reviewed:
        fatal.append("exact_final_reviewed_identity")
    for finding in report["findings"]:
        if (
            finding["classification"] not in FINDING_TYPES
            or not all(finding[key] for key in ("reproduction", "evidence", "materiality", "summary"))
            or (
                finding["classification"] == "candidate_new_material_regression"
                and finding["candidate_new"] is not True
            )
        ):
            fatal.append("exact_final_finding_semantics")
            break
    complete = report["coverage"]["complete"] and not report["coverage"]["unverified"]
    if report["decision"] == "GO" and (not complete or report["findings"]):
        fatal.append("exact_final_invalid_go")
    if report["decision"] == "NOT_YET" and complete and not report["findings"]:
        fatal.append("exact_final_unsupported_not_yet")
    if fatal:
        return {"passed": False, "score": 0, "fatal": fatal, "diagnostics": []}
    passed = report["decision"] == "GO"
    return {
        "passed": passed, "score": int(passed),
        "fatal": [] if passed else ["exact_final_adverse"], "diagnostics": [],
    }

_ATTESTATION, _EVALUATION, _RELEASE = object(), object(), object()

class _Verified:
    __slots__ = ("_json",)
    _factory_token: object
    def __init__(self, value: dict[str, Any], token: object):
        if token is not self._factory_token:
            raise VerifyError(f"{type(self).__name__} is verifier-owned")
        self._json = canonical_text(value)
    def _value(self) -> dict[str, Any]:
        return json.loads(self._json)

class VerifiedAttestation(_Verified):
    __slots__ = ("authenticator_id",)
    _factory_token = _ATTESTATION
    def __init__(self, value: dict[str, Any], authenticator_id: str, token: object):
        super().__init__(value, token)
        self.authenticator_id = authenticator_id
    @property
    def record(self) -> dict[str, Any]:
        return self._value()

class VerifiedEvaluation(_Verified):
    __slots__ = ()
    _factory_token = _EVALUATION
    @property
    def result(self) -> dict[str, Any]:
        return self._value()

class VerifiedRelease(_Verified):
    __slots__ = ()
    _factory_token = _RELEASE
    @property
    def receipt(self) -> dict[str, Any]:
        return self._value()

def authenticate_attestation(
    attestation: dict[str, Any], *, spec: dict[str, Any],
    provider_input: dict[str, Any], response_schema: dict[str, Any],
    oracle: dict[str, Any] | None, authenticator: ExternalAuthenticator,
    evaluation_authority_request: dict[str, Any],
    evaluation_authority: dict[str, Any],
    authority_validator: ExternalAuthorityValidator,
) -> VerifiedAttestation:
    validate_attestation(attestation)
    validate_eval_spec(spec)
    unit = _unit(spec, attestation["unit_id"])
    if any(attestation[field] != unit[field] for field in (
        "stage", "provider_input_sha256", "invocation_sha256", "effect_subject_sha256",
    )) or attestation["spec_sha256"] != spec["spec_sha256"] or (
        attestation["spec_subject_sha256"] != spec["spec_subject_sha256"]
    ):
        raise VerifyError("attestation relationship differs")
    if canonical_sha256(provider_input) != unit["provider_input_sha256"]:
        raise VerifyError("provider input differs from EvalSpec")
    allowed_products = (
        {spec["product_artifact_sha256"], spec["previous_product_artifact_sha256"]}
        if unit["stage"] == "holdout" else {spec["product_artifact_sha256"]}
    )
    if attestation["product_artifact_sha256"] not in allowed_products:
        raise VerifyError("attestation product differs")
    expected_oracle = (
        {
            "review_contract_sha256": spec["review_contract_sha256"],
            "response_schema_sha256": canonical_sha256(response_schema),
        }
        if unit["stage"] == "exact_final" else oracle
    )
    if (
        (unit["stage"] == "exact_final" and oracle is not None)
        or expected_oracle is None
        or canonical_sha256(expected_oracle) != unit["oracle_sha256"]
    ):
        raise VerifyError("oracle identity differs from EvalSpec")
    expected_request = _evaluation_request(spec)
    if evaluation_authority_request != expected_request or (
        attestation["evaluation_authority_request_sha256"] != expected_request["request_sha256"]
    ):
        raise VerifyError("evaluation authority request differs")
    authority_identity, authority_sha = _authority(
        evaluation_authority, request_sha256=expected_request["request_sha256"],
        validator=authority_validator,
    )
    if (
        attestation["authority_identity"] != authority_identity
        or attestation["authority_sha256"] != authority_sha
    ):
        raise VerifyError("attestation authority binding differs")
    _authenticate(attestation_evidence_statement(attestation), attestation["evidence_binding"], authenticator)
    observation = attestation["observation"]
    if _time(observation["started_at"]) > _time(observation["finished_at"]):
        raise VerifyError("authenticated observation time is reversed")
    assessment = assess_provider_report(
        attestation["claim"]["report"], stage=attestation["stage"],
        response_schema=response_schema, oracle=oracle, provider_input=provider_input,
    )
    if attestation["assessment"] != assessment:
        raise VerifyError("attestation assessment was not recomputed")
    return VerifiedAttestation(attestation, authenticator.authenticator_id, _ATTESTATION)

def verify_effect_sequence(
    attempts: list[VerifiedAttestation], *, spec: dict[str, Any], unit_id: str,
) -> VerifiedEffectTerminal:
    validate_eval_spec(spec)
    if not attempts or not all(isinstance(item, VerifiedAttestation) for item in attempts):
        raise VerifyError("effect attempts are not authenticated")
    records, unit = [item.record for item in attempts], _unit(spec, unit_id)
    if [record["attempt"] for record in records] != list(range(len(records))):
        raise VerifyError("effect attempts are not contiguous from zero")
    if records[-1]["attempt"] > spec["caps"]["recovery_attempts"]:
        raise VerifyError("effect recovery cap exceeded")
    stable = (
        "spec_sha256", "spec_subject_sha256", "product_artifact_sha256", "unit_id",
        "stage", "provider_input_sha256", "invocation_sha256", "effect_subject_sha256",
        "evaluation_authority_request_sha256", "authority_identity", "authority_sha256",
    )
    expected = tuple(records[0][field] for field in stable)
    cumulative, history, previous_finish = 0, [], None
    for index, record in enumerate(records):
        observation = record["observation"]
        cumulative += observation["attempt_wall_milliseconds"]
        start, finish = _time(observation["started_at"]), _time(observation["finished_at"])
        if (
            tuple(record[field] for field in stable) != expected
            or record["spec_sha256"] != spec["spec_sha256"]
            or record["spec_subject_sha256"] != spec["spec_subject_sha256"]
            or record["unit_id"] != unit_id
            or record["stage"] != unit["stage"]
            or record["provider_input_sha256"] != unit["provider_input_sha256"]
            or record["invocation_sha256"] != unit["invocation_sha256"]
            or record["effect_subject_sha256"] != unit["effect_subject_sha256"]
            or observation["effect_cumulative_wall_milliseconds"] != cumulative
            or observation["recovery_history_sha256"] != canonical_sha256(history)
            or (previous_finish is not None and start < previous_finish)
        ):
            raise VerifyError("effect sequence relationship, wall, history, or time differs")
        if index < len(records) - 1 and record["effect_outcome"] != "not_landed":
            raise VerifyError("landed or unknown terminal has a later attempt")
        history.append(record["record_sha256"])
        previous_finish = finish
    if cumulative > spec["caps"]["unit_wall_milliseconds"]:
        raise VerifyError("unit cumulative wall cap exceeded")
    return _verified_terminal(records[-1], records)

def verify_evaluation(
    *, spec: dict[str, Any], terminals: list[VerifiedEffectTerminal],
    holdout_result: dict[str, Any],
) -> VerifiedEvaluation:
    validate_eval_spec(spec)
    if not all(isinstance(item, VerifiedEffectTerminal) for item in terminals):
        raise VerifyError("evaluation terminals are not verified")
    records = [item.record for item in terminals]
    by_unit = {record["unit_id"]: record for record in records}
    required = [unit.unit_id for unit in UNIT_TOPOLOGY]
    if len(records) != len(required) or set(by_unit) != set(required):
        raise VerifyError("evaluation requires all canonical terminals")
    if any(
        record["spec_sha256"] != spec["spec_sha256"] or record["effect_outcome"] != "landed"
        for record in records
    ):
        raise VerifyError("evaluation terminal is adverse or from another spec")
    for unit in spec["units"]:
        record = by_unit[unit["unit_id"]]
        if record["effect_subject_sha256"] != unit["effect_subject_sha256"]:
            raise VerifyError("evaluation effect identity differs")
        if unit["stage"] == "behavior" and not record["assessment"]["passed"]:
            raise VerifyError("behavior prerequisite is adverse")
    holdout_terminals = [
        item for item in terminals if item.record["stage"] == "holdout"
    ]
    validate_holdout_result(
        holdout_result, spec=spec, terminals=holdout_terminals,
    )
    if not holdout_result["passed"]:
        raise VerifyError("holdout prerequisite is adverse")
    exact_final = by_unit["exact-final"]
    if not exact_final["assessment"]["passed"] or exact_final["claim"]["report"].get("decision") != "GO":
        raise VerifyError("exact-final prerequisite is adverse")
    exact_unit = _unit(spec, "exact-final")
    expected_effect = exact_final_effect_subject(
        candidate_product_artifact_sha256=spec["product_artifact_sha256"],
        review_contract_sha256_value=spec["review_contract_sha256"],
    )
    if exact_unit["effect_subject_sha256"] != expected_effect:
        raise VerifyError("exact-final effect identity differs")
    others = [record for record in records if record["unit_id"] != "exact-final"]
    if _time(exact_final["observation"]["started_at"]) <= max(
        _time(record["observation"]["finished_at"]) for record in others
    ):
        raise VerifyError("exact-final began before prior terminals froze")
    cumulative_wall = sum(
        record["observation"]["effect_cumulative_wall_milliseconds"] for record in records
    )
    if cumulative_wall > spec["caps"]["absolute_wall_milliseconds"]:
        raise VerifyError("absolute cumulative wall cap exceeded")
    result = {
        "product_artifact_sha256": spec["product_artifact_sha256"],
        "eval_spec_sha256": spec["spec_sha256"],
        "spec_subject_sha256": spec["spec_subject_sha256"],
        "prerequisite_attestation_sha256s": sorted(record["record_sha256"] for record in records),
        "exact_final_attestation_sha256": exact_final["record_sha256"],
        "holdout_result_sha256": holdout_result["result_sha256"],
        "cumulative_effect_wall_milliseconds": cumulative_wall,
        "evaluation_authority_identities": sorted({record["authority_identity"] for record in records}),
    }
    return VerifiedEvaluation(result, _EVALUATION)

def verify_release(
    receipt: dict[str, Any], *, evaluation: VerifiedEvaluation,
    product: dict[str, Any], spec: dict[str, Any],
    authenticator: ExternalAuthenticator, release_authority: dict[str, Any],
    authority_validator: ExternalAuthorityValidator,
) -> VerifiedRelease:
    validate_release_receipt(receipt)
    validate_product_artifact(product)
    validate_eval_spec(spec)
    if not isinstance(evaluation, VerifiedEvaluation):
        raise VerifyError("release evaluation is not verified")
    evaluated = evaluation.result
    fixed = {
        "product_artifact_sha256": evaluated["product_artifact_sha256"],
        "eval_spec_sha256": evaluated["eval_spec_sha256"],
        "spec_subject_sha256": evaluated["spec_subject_sha256"],
        "prerequisite_attestation_sha256s": evaluated["prerequisite_attestation_sha256s"],
        "exact_final_attestation_sha256": evaluated["exact_final_attestation_sha256"],
        "holdout_result_sha256": evaluated["holdout_result_sha256"],
    }
    if any(receipt[key] != value for key, value in fixed.items()):
        raise VerifyError("release prerequisites differ")
    if product["artifact_sha256"] != spec["product_artifact_sha256"] or (
        receipt["installed_projection"] != product["projections"]["plugin_runtime"]
    ):
        raise VerifyError("release product projection differs")
    effect = release_effect_subject(
        product_artifact_sha256=product["artifact_sha256"], destination=receipt["destination"],
        target_identity=receipt["target_identity"], rollback_identity=receipt["rollback_identity"],
        installed_projection_sha256=receipt["installed_projection"]["projection_sha256"],
    )
    if receipt["release_effect_subject_sha256"] != effect:
        raise VerifyError("release effect subject differs")
    request = release_authority_request_payload(
        product_artifact_sha256=product["artifact_sha256"], eval_spec_sha256=spec["spec_sha256"],
        prerequisite_attestation_sha256s=evaluated["prerequisite_attestation_sha256s"],
        exact_final_attestation_sha256=evaluated["exact_final_attestation_sha256"],
        holdout_result_sha256=evaluated["holdout_result_sha256"],
        release_effect_subject_sha256=effect,
    )
    if receipt["release_authority_request_sha256"] != request["request_sha256"]:
        raise VerifyError("release authority request differs")
    authority_identity, authority_sha = _authority(
        release_authority, request_sha256=request["request_sha256"], validator=authority_validator,
    )
    if (
        authority_identity in evaluated["evaluation_authority_identities"]
        or receipt["release_authority_identity"] != authority_identity
        or receipt["release_authority_sha256"] != authority_sha
    ):
        raise VerifyError("release authority is not separate or differs")
    _authenticate(release_evidence_statement(receipt), receipt["evidence_binding"], authenticator)
    if receipt["attempt"] != 0 or receipt["outcome"] != "landed":
        raise VerifyError("release is not a one-shot landed terminal")
    observed = receipt["observation"]
    readback = {
        "observed_destination": receipt["destination"],
        "observed_product_artifact_sha256": receipt["product_artifact_sha256"],
        "observed_target_identity": receipt["target_identity"],
        "observed_rollback_identity": receipt["rollback_identity"],
        "observed_installed_projection_sha256": receipt["installed_projection"]["projection_sha256"],
    }
    if any(observed[key] != value for key, value in readback.items()):
        raise VerifyError("release readback differs")
    if _time(observed["started_at"]) > _time(observed["finished_at"]):
        raise VerifyError("release observation time is reversed")
    return VerifiedRelease(receipt, _RELEASE)

def external_trust_notice() -> str:
    return (
        "Repository verification is stateless. Authority, authentication, one-shot "
        "history, trusted time, provider effects, and release readback remain external facts."
    )

__all__ = (
    "ExternalAuthenticator", "ExternalAuthorityValidator", "VerifiedAttestation",
    "VerifiedEffectTerminal", "VerifiedEvaluation", "VerifiedRelease", "VerifyError",
    "assess_provider_report", "attestation_evidence_statement", "authenticate_attestation",
    "external_trust_notice", "release_evidence_statement", "verify_effect_sequence",
    "verify_evaluation", "verify_release",
)
