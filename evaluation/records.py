from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Callable

from evaluation.policy import EXACT_FINAL_ROLE_ID, HOLDOUT_ROLE_ID, MODEL_ROLE_IDS


RECORD_TYPES = frozenset(
    {"ProductArtifact", "EvalSpec", "Attestation", "ReleaseReceipt"}
)
ATTESTATION_KINDS = frozenset({"behavior", "replay", "exact_final"})
TERMINAL_CLASSES = frozenset(
    {
        "success",
        "quality_failure",
        "resource_failure",
        "infrastructure_no_effect",
        "ambiguous_or_partial",
        "diagnostic",
    }
)
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class RecordError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise RecordError("record is not canonical JSON") from exc


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RecordError(message)


def _exact(value: dict[str, Any], keys: set[str], label: str) -> None:
    _require(type(value) is dict, f"{label} must be an object")
    missing = keys - set(value)
    extra = set(value) - keys
    _require(not missing and not extra, f"{label} fields differ: missing={sorted(missing)} extra={sorted(extra)}")


def _text(value: Any, label: str) -> str:
    _require(type(value) is str and bool(value), f"{label} must be non-empty text")
    return value


def _sha(value: Any, label: str) -> str:
    _require(type(value) is str and _HEX64.fullmatch(value) is not None, f"{label} must be sha256")
    return value


def _git(value: Any, label: str) -> str:
    _require(type(value) is str and _HEX40.fullmatch(value) is not None, f"{label} must be a Git object id")
    return value


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    _require(type(value) is int and value >= minimum, f"{label} must be an integer >= {minimum}")
    return value


def _string_list(value: Any, label: str, *, sorted_unique: bool = False) -> list[str]:
    _require(type(value) is list and all(type(item) is str and item for item in value), f"{label} must be a text list")
    if sorted_unique:
        _require(value == sorted(set(value)), f"{label} must be sorted and unique")
    return value


def _sealed(payload: dict[str, Any]) -> dict[str, Any]:
    _require("record_sha256" not in payload, "payload is already sealed")
    return {**payload, "record_sha256": canonical_sha256(payload)}


def record_sha256(record: dict[str, Any]) -> str:
    _require(type(record) is dict and "record_sha256" in record, "record is unsealed")
    return canonical_sha256({key: value for key, value in record.items() if key != "record_sha256"})


def _validate_seal(record: dict[str, Any]) -> None:
    _sha(record.get("record_sha256"), "record_sha256")
    _require(record["record_sha256"] == record_sha256(record), "record digest mismatch")


def build_product_artifact(
    *,
    source_commit: str,
    source_tree: str,
    package_tree: str,
    package_artifact_sha256: str,
    package_semantic_sha256: str,
    external_role_config_sha256: str,
) -> dict[str, Any]:
    record = _sealed(
        {
            "record_type": "ProductArtifact",
            "schema_version": 1,
            "source_commit": source_commit,
            "source_tree": source_tree,
            "package_tree": package_tree,
            "package_artifact_sha256": package_artifact_sha256,
            "package_semantic_sha256": package_semantic_sha256,
            "external_role_config_sha256": external_role_config_sha256,
        }
    )
    return validate_product_artifact(record)


def validate_product_artifact(record: dict[str, Any]) -> dict[str, Any]:
    _exact(
        record,
        {
            "record_type", "schema_version", "source_commit", "source_tree",
            "package_tree", "package_artifact_sha256", "package_semantic_sha256",
            "external_role_config_sha256", "record_sha256",
        },
        "ProductArtifact",
    )
    _require(record["record_type"] == "ProductArtifact" and record["schema_version"] == 1, "invalid ProductArtifact header")
    _git(record["source_commit"], "source_commit")
    _git(record["source_tree"], "source_tree")
    _git(record["package_tree"], "package_tree")
    for field in ("package_artifact_sha256", "package_semantic_sha256", "external_role_config_sha256"):
        _sha(record[field], field)
    _validate_seal(record)
    return record


def _validate_profile(profile: dict[str, Any]) -> None:
    _exact(profile, {"model", "effort", "tools", "timeout_seconds"}, "profile")
    _text(profile["model"], "profile.model")
    _text(profile["effort"], "profile.effort")
    _string_list(profile["tools"], "profile.tools", sorted_unique=True)
    _integer(profile["timeout_seconds"], "profile.timeout_seconds", minimum=1)


def _validate_profiles(profiles: dict[str, Any]) -> None:
    _exact(profiles, {"behavior", "exact_final"}, "profiles")
    _validate_profile(profiles["behavior"])
    _validate_profile(profiles["exact_final"])


def _validate_cap(cap: dict[str, Any]) -> None:
    _exact(cap, {"model_calls", "input_tokens", "output_tokens", "wall_milliseconds", "infrastructure_recoveries"}, "total_cap")
    for field in cap:
        _integer(cap[field], f"total_cap.{field}")


def _validate_host_contract(contract: dict[str, Any]) -> None:
    _exact(
        contract,
        {"schema_version", "trust_domain", "proof_verifier_sha256", "provider_binary_sha256", "tool_config_sha256", "permission_profile_sha256", "workspace_policy_sha256"},
        "host_contract",
    )
    _require(contract["schema_version"] == 1, "host contract schema differs")
    _text(contract["trust_domain"], "host_contract.trust_domain")
    for field in set(contract) - {"schema_version", "trust_domain"}:
        _sha(contract[field], f"host_contract.{field}")


def _validate_unit(unit: dict[str, Any]) -> None:
    _exact(
        unit,
        {"unit_id", "kind", "role_id", "sample_id", "stage", "order", "product_semantic_sha256", "external_role_config_sha256", "provider_input_sha256", "oracle_sha256", "harness_sha256", "invocation", "invocation_sha256", "review_brief_sha256"},
        "unit",
    )
    _text(unit["unit_id"], "unit.unit_id")
    _require(unit["kind"] in {"behavior", "exact_final"}, "unit kind is invalid")
    _text(unit["role_id"], "unit.role_id")
    _require(unit["sample_id"] is None or (type(unit["sample_id"]) is str and unit["sample_id"]), "unit.sample_id is invalid")
    _require(unit["stage"] in {"behavior", "holdout", "exact_final"}, "unit stage is invalid")
    _require(unit["order"] == {"behavior": 1, "holdout": 2, "exact_final": 3}[unit["stage"]], "unit stage order is invalid")
    for field in ("product_semantic_sha256", "external_role_config_sha256", "provider_input_sha256", "oracle_sha256", "harness_sha256", "invocation_sha256"):
        _sha(unit[field], f"unit.{field}")
    _exact(unit["invocation"], {"unit_id", "stage", "product_semantic_sha256", "external_role_config_sha256", "host_contract_sha256", "provider_input", "model", "effort", "tools", "timeout_seconds", "claim_key"}, "unit.invocation")
    for field in ("unit_id", "stage", "product_semantic_sha256", "external_role_config_sha256"):
        _require(unit["invocation"][field] == unit[field], f"invocation {field} drift")
    _require(type(unit["invocation"]["provider_input"]) is dict, "invocation provider input must be an object")
    _sha(unit["invocation"]["host_contract_sha256"], "invocation.host_contract_sha256")
    _require(canonical_sha256(unit["invocation"]["provider_input"]) == unit["provider_input_sha256"], "provider input digest mismatch")
    invocation_profile = {
        key: unit["invocation"][key]
        for key in ("model", "effort", "tools", "timeout_seconds")
    }
    _validate_profile(invocation_profile)
    _require(
        unit["invocation"]["provider_input"].get("profile") == invocation_profile,
        "provider input profile differs from invocation",
    )
    _sha(unit["invocation"]["claim_key"], "invocation.claim_key")
    _require(canonical_sha256(unit["invocation"]) == unit["invocation_sha256"], "invocation digest mismatch")
    if unit["stage"] == "exact_final":
        _sha(unit["review_brief_sha256"], "unit.review_brief_sha256")
    else:
        _require(unit["review_brief_sha256"] is None, "non-review unit has review brief")


def _validate_holdout(pair: dict[str, Any]) -> None:
    _exact(pair, {"pair_id", "sample_id", "unit_ids", "mapping_sha256"}, "holdout pair")
    _text(pair["pair_id"], "holdout.pair_id")
    _text(pair["sample_id"], "holdout.sample_id")
    _require(type(pair["unit_ids"]) is list and len(pair["unit_ids"]) == 2 and len(set(pair["unit_ids"])) == 2, "holdout pair needs two distinct unit ids")
    _string_list(pair["unit_ids"], "holdout.unit_ids", sorted_unique=True)
    _sha(pair["mapping_sha256"], "holdout.mapping_sha256")


def evaluation_authority_request_payload(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "scope": "evaluation",
        "product_semantic_sha256": spec["product_semantic_sha256"],
        "external_role_config_sha256": spec["external_role_config_sha256"],
        "evaluator_bundle_sha256": spec["evaluator_bundle_sha256"],
        "host_contract": spec["host_contract"],
        "host_contract_sha256": spec["host_contract_sha256"],
        "profiles": spec["profiles"],
        "invocations": [
            {"unit_id": unit["unit_id"], "stage": unit["stage"], "invocation": unit["invocation"], "invocation_sha256": unit["invocation_sha256"]}
            for unit in spec["units"]
        ],
        "total_cap": spec["total_cap"],
        "previous_product_record_sha256": spec["previous_product_record_sha256"],
    }


def build_eval_spec(
    *,
    product_semantic_sha256: str,
    external_role_config_sha256: str,
    evaluator_bundle_sha256: str,
    provider_component_sha256: str,
    oracle_component_sha256: str,
    harness_component_sha256: str,
    manifest_sha256: str,
    fixtures_sha256: str,
    oracles_sha256: str,
    response_schemas_sha256: str,
    host_contract: dict[str, Any],
    host_contract_sha256: str,
    neutral_review_brief_sha256: str,
    profiles: dict[str, Any],
    units: list[dict[str, Any]],
    holdouts: list[dict[str, Any]],
    total_cap: dict[str, int],
    previous_product_record_sha256: str,
) -> dict[str, Any]:
    base = {
        "record_type": "EvalSpec",
        "schema_version": 1,
        "product_semantic_sha256": product_semantic_sha256,
        "external_role_config_sha256": external_role_config_sha256,
        "evaluator_bundle_sha256": evaluator_bundle_sha256,
        "provider_component_sha256": provider_component_sha256,
        "oracle_component_sha256": oracle_component_sha256,
        "harness_component_sha256": harness_component_sha256,
        "manifest_sha256": manifest_sha256,
        "fixtures_sha256": fixtures_sha256,
        "oracles_sha256": oracles_sha256,
        "response_schemas_sha256": response_schemas_sha256,
        "host_contract": host_contract,
        "host_contract_sha256": host_contract_sha256,
        "neutral_review_brief_sha256": neutral_review_brief_sha256,
        "profiles": profiles,
        "units": units,
        "holdouts": holdouts,
        "total_cap": total_cap,
        "previous_product_record_sha256": previous_product_record_sha256,
    }
    request = canonical_sha256(evaluation_authority_request_payload(base))
    return validate_eval_spec(_sealed({**base, "authority_request_sha256": request}))


def validate_eval_spec(record: dict[str, Any]) -> dict[str, Any]:
    _exact(
        record,
        {
            "record_type", "schema_version", "product_semantic_sha256",
            "external_role_config_sha256", "evaluator_bundle_sha256",
            "provider_component_sha256", "oracle_component_sha256",
            "harness_component_sha256", "manifest_sha256", "fixtures_sha256",
            "oracles_sha256", "response_schemas_sha256", "host_contract",
            "host_contract_sha256", "neutral_review_brief_sha256", "profiles", "units", "holdouts",
            "total_cap", "previous_product_record_sha256",
            "authority_request_sha256", "record_sha256",
        },
        "EvalSpec",
    )
    _require(record["record_type"] == "EvalSpec" and record["schema_version"] == 1, "invalid EvalSpec header")
    for field in (
        "product_semantic_sha256", "external_role_config_sha256",
        "evaluator_bundle_sha256", "provider_component_sha256",
        "oracle_component_sha256", "harness_component_sha256",
        "manifest_sha256", "fixtures_sha256", "oracles_sha256",
        "response_schemas_sha256", "host_contract_sha256", "neutral_review_brief_sha256",
        "previous_product_record_sha256", "authority_request_sha256",
    ):
        _sha(record[field], field)
    _validate_host_contract(record["host_contract"])
    _require(record["host_contract_sha256"] == canonical_sha256(record["host_contract"]), "host contract digest mismatch")
    _validate_profiles(record["profiles"])
    _validate_cap(record["total_cap"])
    _require(type(record["units"]) is list and bool(record["units"]), "EvalSpec units must be non-empty")
    for unit in record["units"]:
        _validate_unit(unit)
        _require(unit["invocation"]["host_contract_sha256"] == record["host_contract_sha256"], "unit host contract differs")
        expected_profile = record["profiles"]["exact_final" if unit["stage"] == "exact_final" else "behavior"]
        actual_profile = {
            key: unit["invocation"][key]
            for key in ("model", "effort", "tools", "timeout_seconds")
        }
        _require(actual_profile == expected_profile, "unit stage profile differs")
    unit_ids = [unit["unit_id"] for unit in record["units"]]
    expected_order = [
        unit["unit_id"]
        for unit in sorted(record["units"], key=lambda item: (item["order"], item["unit_id"]))
    ]
    _require(len(unit_ids) == len(set(unit_ids)) and unit_ids == expected_order, "EvalSpec units must be stage ordered and unique")
    exact_final = [unit for unit in record["units"] if unit["kind"] == "exact_final"]
    _require(len(exact_final) == 1, "EvalSpec requires exactly one exact-final unit")
    _require(exact_final[0]["role_id"] == EXACT_FINAL_ROLE_ID, "exact-final role differs from production policy")
    _require(exact_final[0]["stage"] == "exact_final" and exact_final[0]["review_brief_sha256"] == record["neutral_review_brief_sha256"], "exact-final stage or brief differs")
    _require(type(record["holdouts"]) is list and len(record["holdouts"]) == 3, "EvalSpec requires exactly three fixed holdout pairs")
    for pair in record["holdouts"]:
        _validate_holdout(pair)
    pair_ids = [pair["pair_id"] for pair in record["holdouts"]]
    _require(pair_ids == sorted(set(pair_ids)), "holdout pairs must be sorted and unique")
    holdout_units = [unit for pair in record["holdouts"] for unit in pair["unit_ids"]]
    _require(len(holdout_units) == 6 and len(set(holdout_units)) == 6, "fixed holdouts require six unique units")
    _require(set(holdout_units).issubset(unit_ids), "holdout unit is absent from EvalSpec")
    units_by_id = {unit["unit_id"]: unit for unit in record["units"]}
    behavior_roles = sorted(
        unit["role_id"] for unit_id, unit in units_by_id.items()
        if unit_id not in holdout_units and unit["kind"] == "behavior"
    )
    _require(behavior_roles == sorted(MODEL_ROLE_IDS), "behavior role inventory differs from production policy")
    for unit_id, unit in units_by_id.items():
        if unit_id not in holdout_units:
            _require(unit["product_semantic_sha256"] == record["product_semantic_sha256"], "non-holdout unit does not bind candidate product")
            if unit["kind"] == "behavior":
                _require(unit["stage"] == "behavior", "core behavior unit stage differs")
    for pair in record["holdouts"]:
        _require(
            all(
                units_by_id[unit_id]["role_id"] == HOLDOUT_ROLE_ID
                and units_by_id[unit_id]["stage"] == "holdout"
                and units_by_id[unit_id]["sample_id"] == pair["sample_id"]
                and units_by_id[unit_id]["kind"] == "behavior"
                for unit_id in pair["unit_ids"]
            ),
            "holdout unit differs from fixed production policy",
        )
        semantics = {units_by_id[unit_id]["product_semantic_sha256"] for unit_id in pair["unit_ids"]}
        _require(len(semantics) == 2 and record["product_semantic_sha256"] in semantics, "holdout pair must blind candidate and one distinct baseline")
    expected_request = canonical_sha256(evaluation_authority_request_payload(record))
    _require(record["authority_request_sha256"] == expected_request, "authority request digest mismatch")
    _validate_seal(record)
    return record


def _validate_terminal(terminal: dict[str, Any]) -> None:
    _exact(terminal, {"classification", "provider_reached", "complete", "model_calls", "input_tokens", "output_tokens", "wall_milliseconds"}, "terminal")
    _require(terminal["classification"] in TERMINAL_CLASSES, "terminal classification is invalid")
    _require(type(terminal["provider_reached"]) is bool and type(terminal["complete"]) is bool, "terminal booleans are invalid")
    for field in ("model_calls", "input_tokens", "output_tokens", "wall_milliseconds"):
        _integer(terminal[field], f"terminal.{field}")
    if terminal["classification"] == "success":
        _require(terminal["provider_reached"] and terminal["complete"] and terminal["model_calls"] == 1, "success terminal must be one complete provider call")
    if terminal["classification"] == "quality_failure":
        _require(terminal["provider_reached"] and terminal["complete"] and terminal["model_calls"] == 1, "quality_failure must bind one complete provider call")
    if terminal["classification"] == "infrastructure_no_effect":
        _require(not terminal["provider_reached"] and terminal["model_calls"] == 0, "infrastructure_no_effect reached provider")
    if terminal["classification"] == "ambiguous_or_partial":
        _require(not terminal["complete"], "ambiguous_or_partial cannot be complete")


def _validate_observation(observation: dict[str, Any], kind: str) -> None:
    _exact(
        observation,
        {"raw_events_sha256", "sanitized_event_sha256", "terminal_sha256", "report", "report_sha256", "provenance", "parent_attestation_sha256", "started_at", "frozen_at"},
        "observation",
    )
    for field in ("raw_events_sha256", "sanitized_event_sha256", "terminal_sha256", "report_sha256"):
        _sha(observation[field], f"observation.{field}")
    _require(type(observation["report"]) is dict, "observation.report must be an object")
    _require(observation["report_sha256"] == canonical_sha256(observation["report"]), "report digest mismatch")
    _exact(observation["provenance"], {"provider", "model", "effort", "tools", "timeout_seconds"}, "observation.provenance")
    _text(observation["provenance"]["provider"], "provenance.provider")
    _validate_profile({key: observation["provenance"][key] for key in ("model", "effort", "tools", "timeout_seconds")})
    _text(observation["started_at"], "observation.started_at")
    _text(observation["frozen_at"], "observation.frozen_at")
    if kind == "replay":
        _sha(observation["parent_attestation_sha256"], "parent_attestation_sha256")
    else:
        _require(observation["parent_attestation_sha256"] is None, "non-replay attestation has replay parent")


def build_attestation(
    *, kind: str, unit_id: str, product_semantic_sha256: str,
    product_artifact_sha256: str | None, external_role_config_sha256: str,
    provider_input_sha256: str, oracle_sha256: str, harness_sha256: str,
    invocation_sha256: str, authority_sha256: str, host_claim_key: str,
    host_proof_sha256: str, observation: dict[str, Any],
    terminal: dict[str, Any], verdict: str, diagnostics: list[str],
) -> dict[str, Any]:
    return validate_attestation(
        _sealed(
            {
                "record_type": "Attestation", "schema_version": 1,
                "kind": kind, "unit_id": unit_id,
                "product_semantic_sha256": product_semantic_sha256,
                "product_artifact_sha256": product_artifact_sha256,
                "external_role_config_sha256": external_role_config_sha256,
                "provider_input_sha256": provider_input_sha256,
                "oracle_sha256": oracle_sha256, "harness_sha256": harness_sha256,
                "invocation_sha256": invocation_sha256,
                "authority_sha256": authority_sha256, "observation": observation,
                "host_claim_key": host_claim_key, "host_proof_sha256": host_proof_sha256,
                "terminal": terminal, "verdict": verdict,
                "diagnostics": diagnostics,
            }
        )
    )


def validate_attestation(record: dict[str, Any]) -> dict[str, Any]:
    _exact(
        record,
        {
            "record_type", "schema_version", "kind", "unit_id",
            "product_semantic_sha256", "product_artifact_sha256",
            "external_role_config_sha256",
            "provider_input_sha256", "oracle_sha256",
            "harness_sha256", "invocation_sha256", "authority_sha256",
            "host_claim_key", "host_proof_sha256", "observation", "terminal", "verdict", "diagnostics", "record_sha256",
        },
        "Attestation",
    )
    _require(record["record_type"] == "Attestation" and record["schema_version"] == 1, "invalid Attestation header")
    _require(record["kind"] in ATTESTATION_KINDS, "attestation kind is invalid")
    _text(record["unit_id"], "unit_id")
    for field in ("product_semantic_sha256", "external_role_config_sha256", "provider_input_sha256", "oracle_sha256", "harness_sha256", "invocation_sha256", "authority_sha256", "host_claim_key", "host_proof_sha256"):
        _sha(record[field], field)
    _require(record["product_artifact_sha256"] is None or _HEX64.fullmatch(record["product_artifact_sha256"]) is not None, "product_artifact_sha256 is invalid")
    _validate_terminal(record["terminal"])
    _validate_observation(record["observation"], record["kind"])
    _require(record["observation"]["terminal_sha256"] == canonical_sha256(record["terminal"]), "terminal digest mismatch")
    _require(record["verdict"] in {"pass", "fail", "diagnostic"}, "attestation verdict is invalid")
    _string_list(record["diagnostics"], "diagnostics")
    if record["kind"] == "exact_final":
        _sha(record["product_artifact_sha256"], "exact-final product artifact")
        report = record["observation"]["report"]
        _require(report.get("neutral") is True and report.get("decision") in {"GO", "NOT_YET"}, "exact-final report is not neutral and typed")
        _require((report["decision"] == "GO") == (record["verdict"] == "pass"), "exact-final decision and verdict differ")
    _validate_seal(record)
    return record


def build_release_receipt(
    *, product_record_sha256: str, product_artifact_sha256: str,
    attestation_sha256s: list[str], exact_final_attestation_sha256: str,
    isolated_install: dict[str, Any], destination: dict[str, Any],
    rollback: dict[str, Any], release_authority_sha256: str,
) -> dict[str, Any]:
    return validate_release_receipt(
        _sealed(
            {
                "record_type": "ReleaseReceipt", "schema_version": 1,
                "product_record_sha256": product_record_sha256,
                "product_artifact_sha256": product_artifact_sha256,
                "attestation_sha256s": attestation_sha256s,
                "exact_final_attestation_sha256": exact_final_attestation_sha256,
                "isolated_install": isolated_install, "destination": destination,
                "rollback": rollback,
                "release_authority_sha256": release_authority_sha256,
            }
        )
    )


def validate_release_receipt(record: dict[str, Any]) -> dict[str, Any]:
    _exact(
        record,
        {"record_type", "schema_version", "product_record_sha256", "product_artifact_sha256", "attestation_sha256s", "exact_final_attestation_sha256", "isolated_install", "destination", "rollback", "release_authority_sha256", "record_sha256"},
        "ReleaseReceipt",
    )
    _require(record["record_type"] == "ReleaseReceipt" and record["schema_version"] == 1, "invalid ReleaseReceipt header")
    for field in ("product_record_sha256", "product_artifact_sha256", "exact_final_attestation_sha256", "release_authority_sha256"):
        _sha(record[field], field)
    _string_list(record["attestation_sha256s"], "attestation_sha256s", sorted_unique=True)
    _require(record["exact_final_attestation_sha256"] in record["attestation_sha256s"], "exact-final is absent from release attestations")
    _exact(record["isolated_install"], {"artifact_sha256", "install_sha256", "invocation_sha256", "status"}, "isolated_install")
    for field in ("artifact_sha256", "install_sha256", "invocation_sha256"):
        _sha(record["isolated_install"][field], f"isolated_install.{field}")
    _require(record["isolated_install"]["status"] == "success", "isolated install did not succeed")
    _require(record["isolated_install"]["artifact_sha256"] == record["product_artifact_sha256"], "isolated install artifact differs from product")
    _exact(record["destination"], {"kind", "identity_sha256"}, "destination")
    _text(record["destination"]["kind"], "destination.kind")
    _sha(record["destination"]["identity_sha256"], "destination.identity_sha256")
    _exact(record["rollback"], {"artifact_sha256", "config_sha256", "ready"}, "rollback")
    _sha(record["rollback"]["artifact_sha256"], "rollback.artifact_sha256")
    _sha(record["rollback"]["config_sha256"], "rollback.config_sha256")
    _require(record["rollback"]["ready"] is True, "rollback is not ready")
    _validate_seal(record)
    return record


VALIDATORS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "ProductArtifact": validate_product_artifact,
    "EvalSpec": validate_eval_spec,
    "Attestation": validate_attestation,
    "ReleaseReceipt": validate_release_receipt,
}


def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    _require(type(record) is dict, "record must be an object")
    record_type = record.get("record_type")
    _require(record_type in RECORD_TYPES, "unknown durable record type")
    return VALIDATORS[record_type](record)
