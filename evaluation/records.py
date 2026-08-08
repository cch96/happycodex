"""Closed schema-v3 validators for the four durable evaluator records."""
from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any, Callable

from evaluation.canonical import (
    ContractError,
    boolean,
    canonical_sha256,
    exact,
    integer,
    sealed,
    sha256,
    string_list,
    text,
    validate_seal,
)
from evaluation.policy import (
    EFFECT_OUTCOMES,
    HOLDOUT_PAIR_TOPOLOGY,
    PROJECTION_NAMES,
    RECORD_TYPES,
    SCHEMA_VERSION,
    STAGES,
    UNIT_TOPOLOGY,
)

class RecordError(ContractError):
    pass

def _guard(
    function: Callable[[dict[str, Any]], None],
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def wrapped(record: dict[str, Any]) -> dict[str, Any]:
        try:
            function(record)
            validate_seal(record)
        except ContractError as exc:
            raise RecordError(str(exc)) from exc
        return record

    return wrapped

def _header(record: dict[str, Any], record_type: str, fields: set[str]) -> None:
    exact(
        record,
        fields | {"record_type", "schema_version", "record_sha256"},
        record_type,
    )
    if (
        record["record_type"] != record_type
        or record["schema_version"] != SCHEMA_VERSION
    ):
        raise ContractError(f"invalid {record_type} header")

def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    if type(record) is not dict or record.get("record_type") not in RECORD_TYPES:
        raise RecordError("unknown durable record type")
    validator = {
        "ProductArtifact": validate_product_artifact,
        "EvalSpec": validate_eval_spec,
        "Attestation": validate_attestation,
        "ReleaseReceipt": validate_release_receipt,
    }[record["record_type"]]
    return validator(record)

def _path(value: Any, label: str) -> str:
    result = text(value, label)
    parsed = PurePosixPath(result)
    if (
        result.startswith("/")
        or "\\" in result
        or ".." in parsed.parts
        or result != parsed.as_posix()
    ):
        raise ContractError(f"{label} escapes its root")
    return result

def _entry(entry: dict[str, Any], label: str) -> None:
    exact(entry, {"path", "mode", "state", "sha256", "size_bytes"}, label)
    _path(entry["path"], f"{label}.path")
    if entry["mode"] not in ("100644", "100755", "000000"):
        raise ContractError(f"{label}.mode differs")
    if entry["state"] not in ("present", "absent"):
        raise ContractError(f"{label}.state differs")
    sha256(entry["sha256"], f"{label}.sha256")
    integer(entry["size_bytes"], f"{label}.size_bytes")
    if entry["state"] == "absent" and (
        entry["mode"] != "000000" or entry["size_bytes"] != 0
    ):
        raise ContractError(f"{label} absent identity differs")
    if entry["state"] == "present" and entry["mode"] == "000000":
        raise ContractError(f"{label} present mode differs")

def _projection(value: dict[str, Any], label: str) -> None:
    exact(value, {"entries", "projection_sha256"}, label)
    entries = value["entries"]
    if type(entries) is not list or not entries:
        raise ContractError(f"{label}.entries is empty")
    for index, entry in enumerate(entries):
        _entry(entry, f"{label}.entries[{index}]")
    paths = [entry["path"] for entry in entries]
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise ContractError(f"{label}.entries are not sorted and unique")
    sha256(value["projection_sha256"], f"{label}.projection_sha256")
    if value["projection_sha256"] != canonical_sha256(entries):
        raise ContractError(f"{label} projection seal differs")

def _validate_product(record: dict[str, Any]) -> None:
    _header(
        record,
        "ProductArtifact",
        {"source_provenance", "projections", "artifact_sha256"},
    )
    provenance = exact(
        record["source_provenance"],
        {"kind", "identity", "baseline_identity"},
        "source_provenance",
    )
    if provenance["kind"] not in ("git_tree", "content_snapshot"):
        raise ContractError("source provenance kind differs")
    text(provenance["identity"], "source_provenance.identity")
    text(provenance["baseline_identity"], "source_provenance.baseline_identity")
    projections = exact(record["projections"], PROJECTION_NAMES, "projections")
    for name in PROJECTION_NAMES:
        _projection(projections[name], f"projections.{name}")
    sha256(record["artifact_sha256"], "artifact_sha256")
    if record["artifact_sha256"] != canonical_sha256(projections):
        raise ContractError("ProductArtifact identity differs")

validate_product_artifact = _guard(_validate_product)

def build_product_artifact(
    *, source_provenance: dict[str, Any], projections: dict[str, Any]
) -> dict[str, Any]:
    return validate_product_artifact(
        sealed(
            {
                "record_type": "ProductArtifact",
                "schema_version": SCHEMA_VERSION,
                "source_provenance": source_provenance,
                "projections": projections,
                "artifact_sha256": canonical_sha256(projections),
            }
        )
    )

def _unit(value: dict[str, Any], index: int) -> None:
    fields = {
        "unit_id",
        "stage",
        "role_id",
        "sample_id",
        "arm",
        "provider_input_sha256",
        "oracle_sha256",
        "invocation_sha256",
        "effect_subject_sha256",
    }
    exact(value, fields, f"units[{index}]")
    text(value["unit_id"], f"units[{index}].unit_id")
    if value["stage"] not in STAGES:
        raise ContractError(f"units[{index}].stage differs")
    text(value["role_id"], f"units[{index}].role_id")
    for field in ("sample_id", "arm"):
        if value[field] is not None:
            text(value[field], f"units[{index}].{field}")
    for field in (
        "provider_input_sha256",
        "oracle_sha256",
        "invocation_sha256",
        "effect_subject_sha256",
    ):
        sha256(value[field], f"units[{index}].{field}")

def _caps(value: dict[str, Any]) -> None:
    exact(
        value,
        {
            "model_calls",
            "candidate_token_ratio_milli",
            "unit_wall_milliseconds",
            "absolute_wall_milliseconds",
            "recovery_attempts",
        },
        "caps",
    )
    if value["model_calls"] != len(UNIT_TOPOLOGY):
        raise ContractError("fixed model-call cap differs")
    if value["candidate_token_ratio_milli"] != 1250:
        raise ContractError("fixed candidate token ratio differs")
    integer(value["unit_wall_milliseconds"], "caps.unit_wall_milliseconds", minimum=1)
    integer(
        value["absolute_wall_milliseconds"],
        "caps.absolute_wall_milliseconds",
        minimum=1,
    )
    integer(value["recovery_attempts"], "caps.recovery_attempts")
    if value["absolute_wall_milliseconds"] < value["unit_wall_milliseconds"]:
        raise ContractError("absolute wall cap is below one unit cap")

def _validate_eval(record: dict[str, Any]) -> None:
    fields = {
        "product_artifact_sha256",
        "previous_product_artifact_sha256",
        "component_identities",
        "review_contract_sha256",
        "units",
        "holdout_pairs",
        "caps",
        "spec_subject_sha256",
        "spec_sha256",
    }
    _header(record, "EvalSpec", fields)
    for field in (
        "product_artifact_sha256",
        "previous_product_artifact_sha256",
        "review_contract_sha256",
    ):
        sha256(record[field], field)
    components = exact(
        record["component_identities"],
        {"provider_input", "oracle", "harness"},
        "component_identities",
    )
    for name, identity in components.items():
        sha256(identity, f"component_identities.{name}")
    units = record["units"]
    if type(units) is not list:
        raise ContractError("units is not a list")
    for index, unit in enumerate(units):
        _unit(unit, index)
    observed_topology = tuple(
        (
            unit["unit_id"],
            unit["stage"],
            unit["role_id"],
            unit["sample_id"],
            unit["arm"],
        )
        for unit in units
    )
    if observed_topology != tuple(tuple(unit) for unit in UNIT_TOPOLOGY):
        raise ContractError("canonical UNIT_TOPOLOGY differs")
    effects = [unit["effect_subject_sha256"] for unit in units]
    if len(effects) != len(set(effects)):
        raise ContractError("effect subjects are not unique")
    pairs = record["holdout_pairs"]
    if type(pairs) is not list:
        raise ContractError("holdout_pairs is not a list")
    observed_pairs = []
    for index, pair in enumerate(pairs):
        exact(
            pair,
            {"pair_id", "sample_id", "unit_ids", "mapping_commitment_sha256"},
            f"holdout_pairs[{index}]",
        )
        unit_ids = pair["unit_ids"]
        if type(unit_ids) is not list:
            raise ContractError("holdout pair unit_ids is not a list")
        sha256(
            pair["mapping_commitment_sha256"],
            f"holdout_pairs[{index}].mapping_commitment_sha256",
        )
        observed_pairs.append(
            (pair["pair_id"], pair["sample_id"], tuple(unit_ids))
        )
    if tuple(observed_pairs) != HOLDOUT_PAIR_TOPOLOGY:
        raise ContractError("canonical holdout pair topology differs")
    _caps(record["caps"])
    subject_fields = fields - {"spec_subject_sha256", "spec_sha256"}
    expected_subject = canonical_sha256(
        {key: record[key] for key in subject_fields}
    )
    if record["spec_subject_sha256"] != expected_subject:
        raise ContractError("EvalSpec subject differs")
    expected_spec = canonical_sha256(
        {key: record[key] for key in fields if key != "spec_sha256"}
    )
    if record["spec_sha256"] != expected_spec:
        raise ContractError("EvalSpec identity differs")

validate_eval_spec = _guard(_validate_eval)

def build_eval_spec(**values: Any) -> dict[str, Any]:
    values = dict(values)
    values["spec_subject_sha256"] = canonical_sha256(values)
    values["spec_sha256"] = canonical_sha256(values)
    return validate_eval_spec(
        sealed(
            {
                "record_type": "EvalSpec",
                "schema_version": SCHEMA_VERSION,
                **values,
            }
        )
    )

def _observation(value: dict[str, Any], *, release: bool = False) -> None:
    common = {
        "started_at",
        "finished_at",
        "attempt_wall_milliseconds",
        "effect_cumulative_wall_milliseconds",
        "recovery_history_sha256",
        "raw_sha256",
    }
    provider = {
        "provider_reached",
        "response_complete",
        "model_calls",
        "input_tokens",
        "output_tokens",
    }
    release_fields = {
        "effect_reached",
        "readback_complete",
        "observed_destination",
        "observed_product_artifact_sha256",
        "observed_target_identity",
        "observed_rollback_identity",
        "observed_installed_projection_sha256",
    }
    exact(value, common | (release_fields if release else provider), "observation")
    text(value["started_at"], "observation.started_at")
    text(value["finished_at"], "observation.finished_at")
    for field in (
        "attempt_wall_milliseconds",
        "effect_cumulative_wall_milliseconds",
    ):
        integer(value[field], f"observation.{field}")
    if (
        value["effect_cumulative_wall_milliseconds"]
        < value["attempt_wall_milliseconds"]
    ):
        raise ContractError("effect cumulative wall omits the current attempt")
    sha256(value["recovery_history_sha256"], "observation.recovery_history_sha256")
    sha256(value["raw_sha256"], "observation.raw_sha256")
    if release:
        boolean(value["effect_reached"], "observation.effect_reached")
        boolean(value["readback_complete"], "observation.readback_complete")
        for field in release_fields - {"effect_reached", "readback_complete"}:
            if value[field] is not None:
                if field.endswith("sha256"):
                    sha256(value[field], f"observation.{field}")
                else:
                    text(value[field], f"observation.{field}")
    else:
        boolean(value["provider_reached"], "observation.provider_reached")
        boolean(value["response_complete"], "observation.response_complete")
        for field in ("model_calls", "input_tokens", "output_tokens"):
            integer(value[field], f"observation.{field}")

def _binding(value: dict[str, Any]) -> None:
    exact(
        value,
        {"authenticator_id", "evidence_sha256", "signature"},
        "evidence_binding",
    )
    text(value["authenticator_id"], "evidence_binding.authenticator_id")
    sha256(value["evidence_sha256"], "evidence_binding.evidence_sha256")
    text(value["signature"], "evidence_binding.signature")

def _attempt_rules(
    *, attempt: int, outcome: str, observation: dict[str, Any], release: bool
) -> None:
    if outcome not in EFFECT_OUTCOMES:
        raise ContractError("effect outcome differs")
    empty_history = canonical_sha256([])
    if attempt == 0:
        if observation["recovery_history_sha256"] != empty_history:
            raise ContractError("first attempt has recovery history")
        if (
            observation["effect_cumulative_wall_milliseconds"]
            != observation["attempt_wall_milliseconds"]
        ):
            raise ContractError("first attempt cumulative wall differs")
    elif observation["recovery_history_sha256"] == empty_history:
        raise ContractError("recovered attempt lacks history identity")
    reached = "effect_reached" if release else "provider_reached"
    complete = "readback_complete" if release else "response_complete"
    if outcome == "not_landed":
        if observation[reached] or observation[complete]:
            raise ContractError("not_landed is not a pre-effect terminal")
        if not release and any(
            observation[field]
            for field in ("model_calls", "input_tokens", "output_tokens")
        ):
            raise ContractError("not_landed provider usage is nonzero")
    if outcome == "landed":
        if not observation[reached] or not observation[complete]:
            raise ContractError("landed terminal is incomplete")
        if not release and observation["model_calls"] != 1:
            raise ContractError("landed provider model-call count differs")

def _validate_attestation_record(record: dict[str, Any]) -> None:
    fields = {
        "spec_sha256",
        "spec_subject_sha256",
        "product_artifact_sha256",
        "unit_id",
        "stage",
        "provider_input_sha256",
        "invocation_sha256",
        "effect_subject_sha256",
        "attempt",
        "attempt_identity_sha256",
        "evaluation_authority_request_sha256",
        "authority_identity",
        "authority_sha256",
        "claim",
        "observation",
        "evidence_binding",
        "assessment",
        "effect_outcome",
    }
    _header(record, "Attestation", fields)
    for field in (
        "spec_sha256",
        "spec_subject_sha256",
        "product_artifact_sha256",
        "provider_input_sha256",
        "invocation_sha256",
        "effect_subject_sha256",
        "attempt_identity_sha256",
        "evaluation_authority_request_sha256",
        "authority_sha256",
    ):
        sha256(record[field], field)
    text(record["unit_id"], "unit_id")
    if record["stage"] not in STAGES:
        raise ContractError("attestation stage differs")
    if not any(
        unit.unit_id == record["unit_id"] and unit.stage == record["stage"]
        for unit in UNIT_TOPOLOGY
    ):
        raise ContractError("attestation unit is outside UNIT_TOPOLOGY")
    attempt = integer(record["attempt"], "attempt")
    expected_attempt = canonical_sha256(
        {
            "effect_subject_sha256": record["effect_subject_sha256"],
            "attempt": attempt,
        }
    )
    if record["attempt_identity_sha256"] != expected_attempt:
        raise ContractError("attempt identity differs")
    text(record["authority_identity"], "authority_identity")
    claim = exact(record["claim"], {"report", "report_sha256"}, "claim")
    if type(claim["report"]) is not dict:
        raise ContractError("claim.report is not an object")
    if claim["report_sha256"] != canonical_sha256(claim["report"]):
        raise ContractError("claim report identity differs")
    _observation(record["observation"])
    _binding(record["evidence_binding"])
    assessment = exact(
        record["assessment"],
        {"passed", "score", "fatal", "diagnostics"},
        "assessment",
    )
    boolean(assessment["passed"], "assessment.passed")
    integer(assessment["score"], "assessment.score")
    string_list(assessment["fatal"], "assessment.fatal")
    string_list(assessment["diagnostics"], "assessment.diagnostics")
    _attempt_rules(
        attempt=attempt,
        outcome=record["effect_outcome"],
        observation=record["observation"],
        release=False,
    )

validate_attestation = _guard(_validate_attestation_record)

def build_attestation(**values: Any) -> dict[str, Any]:
    return validate_attestation(
        sealed(
            {
                "record_type": "Attestation",
                "schema_version": SCHEMA_VERSION,
                **values,
            }
        )
    )

def _validate_release(record: dict[str, Any]) -> None:
    fields = {
        "product_artifact_sha256",
        "eval_spec_sha256",
        "spec_subject_sha256",
        "prerequisite_attestation_sha256s",
        "exact_final_attestation_sha256",
        "holdout_result_sha256",
        "release_authority_request_sha256",
        "release_authority_identity",
        "release_authority_sha256",
        "release_effect_subject_sha256",
        "attempt",
        "attempt_identity_sha256",
        "destination",
        "target_identity",
        "rollback_identity",
        "installed_projection",
        "observation",
        "evidence_binding",
        "outcome",
    }
    _header(record, "ReleaseReceipt", fields)
    for field in (
        "product_artifact_sha256",
        "eval_spec_sha256",
        "spec_subject_sha256",
        "exact_final_attestation_sha256",
        "holdout_result_sha256",
        "release_authority_request_sha256",
        "release_authority_sha256",
        "release_effect_subject_sha256",
        "attempt_identity_sha256",
    ):
        sha256(record[field], field)
    prerequisites = string_list(
        record["prerequisite_attestation_sha256s"],
        "prerequisite_attestation_sha256s",
    )
    for identity in prerequisites:
        sha256(identity, "prerequisite_attestation_sha256s[]")
    if prerequisites != sorted(prerequisites):
        raise ContractError("release prerequisites are not sorted")
    if record["exact_final_attestation_sha256"] not in prerequisites:
        raise ContractError("exact-final is not a release prerequisite")
    text(record["release_authority_identity"], "release_authority_identity")
    for field in ("destination", "target_identity", "rollback_identity"):
        text(record[field], field)
    attempt = integer(record["attempt"], "attempt")
    expected_attempt = canonical_sha256(
        {
            "effect_subject_sha256": record["release_effect_subject_sha256"],
            "attempt": attempt,
        }
    )
    if record["attempt_identity_sha256"] != expected_attempt:
        raise ContractError("release attempt identity differs")
    _projection(record["installed_projection"], "installed_projection")
    _observation(record["observation"], release=True)
    _binding(record["evidence_binding"])
    _attempt_rules(
        attempt=attempt,
        outcome=record["outcome"],
        observation=record["observation"],
        release=True,
    )
    observed = (
        "observed_destination",
        "observed_product_artifact_sha256",
        "observed_target_identity",
        "observed_rollback_identity",
        "observed_installed_projection_sha256",
    )
    if record["outcome"] == "landed" and any(
        record["observation"][field] is None for field in observed
    ):
        raise ContractError("landed release readback is incomplete")
    if record["outcome"] == "not_landed" and any(
        record["observation"][field] is not None for field in observed
    ):
        raise ContractError("not_landed release has readback values")

validate_release_receipt = _guard(_validate_release)

def build_release_receipt(**values: Any) -> dict[str, Any]:
    return validate_release_receipt(
        sealed(
            {
                "record_type": "ReleaseReceipt",
                "schema_version": SCHEMA_VERSION,
                **values,
            }
        )
    )


__all__ = (
    "RecordError",
    "build_attestation",
    "build_eval_spec",
    "build_product_artifact",
    "build_release_receipt",
    "validate_attestation",
    "validate_eval_spec",
    "validate_product_artifact",
    "validate_record",
    "validate_release_receipt",
)
