from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evaluation.identity import evaluator_components
from evaluation.policy import EXACT_FINAL_ROLE_ID, HOLDOUT_ROLE_ID, MODEL_ROLE_IDS
from evaluation.provider import provider_projection
from evaluation.records import (
    RecordError,
    build_eval_spec,
    canonical_sha256,
    validate_product_artifact,
)


MANIFEST_FILE = "manifest-v1.json"


class ManifestError(ValueError):
    pass


def _validate_structural_schema(node: Any) -> None:
    if type(node) is not dict or "type" not in node:
        raise ManifestError("response schema node lacks a structural type")
    allowed = {"type", "required", "properties", "items"}
    if set(node) - allowed:
        raise ManifestError("response schema contains a non-structural keyword")
    schema_type = node["type"]
    if schema_type not in {"object", "array", "boolean", "string"}:
        raise ManifestError("response schema type is outside the closed subset")
    if schema_type == "object":
        properties = node.get("properties", {})
        required = node.get("required", [])
        if type(properties) is not dict or type(required) is not list or not all(type(item) is str for item in required):
            raise ManifestError("response schema object shape is malformed")
        if len(required) != len(set(required)) or not set(required).issubset(properties):
            raise ManifestError("response schema required fields differ from properties")
        if "items" in node:
            raise ManifestError("response schema object cannot contain items")
        for child in properties.values():
            _validate_structural_schema(child)
    elif schema_type == "array":
        if set(node) != {"type", "items"}:
            raise ManifestError("response schema array shape is malformed")
        _validate_structural_schema(node["items"])
    elif set(node) != {"type"}:
        raise ManifestError("response schema scalar contains non-structural fields")


def _schema_covers(schema: dict[str, Any], path: str, expected: Any) -> bool:
    node: Any = schema
    for part in path.split("."):
        if type(node) is not dict or node.get("type") != "object" or part not in node.get("required", []) or part not in node.get("properties", {}):
            return False
        node = node["properties"][part]
    expected_type = {bool: "boolean", str: "string", int: "integer"}.get(type(expected))
    return expected_type is None or node.get("type") == expected_type


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read production evaluator input: {path.name}") from exc
    if type(value) is not dict:
        raise ManifestError(f"production evaluator input is not an object: {path.name}")
    return value


def load_production_inputs(root: Path) -> dict[str, Any]:
    evaluation = root.resolve() / "evaluation"
    manifest = _read(evaluation / MANIFEST_FILE)
    if set(manifest) != {"schema_version", "manifest_id", "provider_fixtures", "hidden_oracles", "response_schemas", "core_roles", "holdout_samples", "exact_final"} or manifest["schema_version"] != 1:
        raise ManifestError("production manifest fields differ")
    if tuple(manifest["core_roles"]) != MODEL_ROLE_IDS:
        raise ManifestError("production core role inventory differs")
    if type(manifest["holdout_samples"]) is not list or len(manifest["holdout_samples"]) != 3 or manifest["holdout_samples"] != sorted(set(manifest["holdout_samples"])):
        raise ManifestError("production manifest requires three fixed samples")
    if manifest["exact_final"].get("role_id") != EXACT_FINAL_ROLE_ID or type(manifest["exact_final"].get("brief_template")) is not str:
        raise ManifestError("production exact-final template differs")
    fixtures = _read(evaluation / manifest["provider_fixtures"])
    oracles = _read(evaluation / manifest["hidden_oracles"])
    schemas = _read(evaluation / manifest["response_schemas"])
    if set(fixtures) != {"schema_version", "core", "holdouts"} or fixtures["schema_version"] != 1:
        raise ManifestError("provider fixture fields differ")
    if set(oracles) != {"schema_version", "core", "holdouts", "exact_final"} or oracles["schema_version"] != 1:
        raise ManifestError("hidden oracle fields differ")
    if set(schemas) != {"schema_version", "core", "holdout", "exact_final"} or schemas["schema_version"] != 1:
        raise ManifestError("response schema fields differ")
    if set(fixtures["core"]) != set(MODEL_ROLE_IDS) or set(oracles["core"]) != set(MODEL_ROLE_IDS):
        raise ManifestError("core fixture/oracle inventory differs")
    if set(schemas["core"]) != set(MODEL_ROLE_IDS):
        raise ManifestError("core response schema inventory differs")
    for schema in [*schemas["core"].values(), schemas["holdout"], schemas["exact_final"]]:
        _validate_structural_schema(schema)
    samples = set(manifest["holdout_samples"])
    if set(fixtures["holdouts"]) != samples or set(oracles["holdouts"]) != samples:
        raise ManifestError("holdout fixture/oracle inventory differs")
    schema_oracles = [
        *( (schemas["core"][role], oracles["core"][role]) for role in MODEL_ROLE_IDS ),
        *( (schemas["holdout"], oracles["holdouts"][sample]) for sample in samples ),
        (schemas["exact_final"], oracles["exact_final"]),
    ]
    for schema, oracle in schema_oracles:
        fields = {**oracle.get("fatal", {}), **oracle.get("diagnostic", {}), **oracle.get("quality", {})}
        if not all(_schema_covers(schema, path, expected) for path, expected in fields.items()):
            raise ManifestError("public response schema cannot represent hidden oracle fields")
    if not _schema_covers(schemas["exact_final"], "decision", oracles["exact_final"]["passing_decision"]):
        raise ManifestError("exact-final response schema lacks decision field")
    return {
        "manifest": manifest, "fixtures": fixtures, "oracles": oracles,
        "schemas": schemas,
        "manifest_sha256": canonical_sha256(manifest),
        "fixtures_sha256": canonical_sha256(fixtures),
        "oracles_sha256": canonical_sha256(oracles),
        "response_schemas_sha256": canonical_sha256(schemas),
    }


def neutral_review_brief(
    inputs: dict[str, Any], product: dict[str, Any], brief: dict[str, Any],
) -> str:
    required = {"request", "obligations", "checks", "exclusions"}
    if set(brief) != required:
        raise ManifestError("neutral review brief fields differ")
    return inputs["manifest"]["exact_final"]["brief_template"].format(
        artifact_sha256=product["package_artifact_sha256"],
        request=brief["request"],
        obligations=json.dumps(brief["obligations"], sort_keys=True),
        checks=json.dumps(brief["checks"], sort_keys=True),
        exclusions=json.dumps(brief["exclusions"], sort_keys=True),
    )


def _unit(
    *, unit_id: str, role_id: str, sample_id: str | None, stage: str,
    arm_product: dict[str, Any], case: dict[str, Any], profile: dict[str, Any],
    oracle_sha256: str, harness_sha256: str, review_brief_sha256: str | None,
    host_contract_sha256: str,
) -> dict[str, Any]:
    projection = provider_projection(
        case={"role_id": role_id, "sample_id": sample_id, **case},
        product_semantic_sha256=arm_product["package_semantic_sha256"],
        external_role_config_sha256=arm_product["external_role_config_sha256"],
        profile=profile,
    )
    invocation = {
        "unit_id": unit_id, "stage": stage,
        "product_semantic_sha256": arm_product["package_semantic_sha256"],
        "external_role_config_sha256": arm_product["external_role_config_sha256"],
        "host_contract_sha256": host_contract_sha256,
        "provider_input": projection, "model": profile["model"],
        "effort": profile["effort"], "tools": profile["tools"],
        "timeout_seconds": profile["timeout_seconds"],
        "claim_key": canonical_sha256(
            {
                "unit_id": unit_id, "stage": stage,
                "product": arm_product["package_semantic_sha256"],
                "role_config": arm_product["external_role_config_sha256"],
                "host_contract": host_contract_sha256,
                "provider_input": projection,
            }
        ),
    }
    return {
        "unit_id": unit_id, "kind": "exact_final" if stage == "exact_final" else "behavior",
        "role_id": role_id, "sample_id": sample_id, "stage": stage,
        "order": {"behavior": 1, "holdout": 2, "exact_final": 3}[stage],
        "product_semantic_sha256": arm_product["package_semantic_sha256"],
        "external_role_config_sha256": arm_product["external_role_config_sha256"],
        "provider_input_sha256": canonical_sha256(projection),
        "oracle_sha256": oracle_sha256, "harness_sha256": harness_sha256,
        "invocation": invocation, "invocation_sha256": canonical_sha256(invocation),
        "review_brief_sha256": review_brief_sha256,
    }


def materialize_eval_spec(
    *, root: Path, candidate: dict[str, Any], previous: dict[str, Any],
    profile: dict[str, Any], total_cap: dict[str, int],
    holdout_mapping: dict[str, dict[str, str]], review_brief: dict[str, Any],
    host_contract: dict[str, Any],
) -> dict[str, Any]:
    validate_product_artifact(candidate)
    validate_product_artifact(previous)
    inputs = load_production_inputs(root)
    runtime = (root.resolve() / "skills" / "happycodex" / "SKILL.md").read_text(encoding="utf-8")
    brief_text = neutral_review_brief(inputs, candidate, review_brief)
    brief_sha = canonical_sha256(brief_text)
    host_contract_sha = canonical_sha256(host_contract)
    harness_sha = canonical_sha256({"raw_stream": "jsonl-v1", "proof": "external-host-v1"})
    units: list[dict[str, Any]] = []
    for role_id in MODEL_ROLE_IDS:
        fixture = inputs["fixtures"]["core"][role_id]
        units.append(
            _unit(
                unit_id=role_id, role_id=role_id, sample_id=None, stage="behavior",
                arm_product=candidate,
                case={**fixture, "runtime": runtime, "response_schema": inputs["schemas"]["core"][role_id]}, profile=profile,
                oracle_sha256=canonical_sha256(inputs["oracles"]["core"][role_id]),
                harness_sha256=harness_sha, review_brief_sha256=None,
                host_contract_sha256=host_contract_sha,
            )
        )
    holdouts = []
    for sample_id in inputs["manifest"]["holdout_samples"]:
        pair_id = sample_id
        unit_ids = sorted([f"{pair_id}-arm-a", f"{pair_id}-arm-b"])
        mapping = holdout_mapping.get(pair_id)
        if type(mapping) is not dict or set(mapping) != set(unit_ids) or sorted(mapping.values()) != ["baseline", "candidate"]:
            raise ManifestError("external holdout mapping differs from fixed pair")
        holdouts.append(
            {"pair_id": pair_id, "sample_id": sample_id, "unit_ids": unit_ids, "mapping_sha256": canonical_sha256(mapping)}
        )
        fixture = inputs["fixtures"]["holdouts"][sample_id]
        for unit_id in unit_ids:
            arm_product = candidate if mapping[unit_id] == "candidate" else previous
            units.append(
                _unit(
                    unit_id=unit_id, role_id=HOLDOUT_ROLE_ID, sample_id=sample_id,
                    stage="holdout", arm_product=arm_product,
                    case={**fixture, "runtime": runtime, "response_schema": inputs["schemas"]["holdout"]}, profile=profile,
                    oracle_sha256=canonical_sha256(inputs["oracles"]["holdouts"][sample_id]),
                    harness_sha256=harness_sha, review_brief_sha256=None,
                    host_contract_sha256=host_contract_sha,
                )
            )
    units.append(
        _unit(
            unit_id=EXACT_FINAL_ROLE_ID, role_id=EXACT_FINAL_ROLE_ID,
            sample_id=None, stage="exact_final", arm_product=candidate,
            case={
                "prompt": "Perform the neutral exact-final review.",
                "fixture": {"artifact_sha256": candidate["package_artifact_sha256"]},
                "workspace": {"brief_sha256": brief_sha}, "runtime": runtime,
                "neutral_review_brief": brief_text,
                "response_schema": inputs["schemas"]["exact_final"],
            },
            profile=profile,
            oracle_sha256=canonical_sha256(inputs["oracles"]["exact_final"]),
            harness_sha256=harness_sha, review_brief_sha256=brief_sha,
            host_contract_sha256=host_contract_sha,
        )
    )
    units.sort(key=lambda item: (item["order"], item["unit_id"]))
    if total_cap.get("model_calls", -1) < len(units):
        raise ManifestError("total cap cannot cover the finite invocation plan")
    components = evaluator_components(root)
    return build_eval_spec(
        product_semantic_sha256=candidate["package_semantic_sha256"],
        external_role_config_sha256=candidate["external_role_config_sha256"],
        previous_product_record_sha256=previous["record_sha256"],
        profile=profile, units=units, holdouts=holdouts, total_cap=total_cap,
        neutral_review_brief_sha256=brief_sha,
        manifest_sha256=inputs["manifest_sha256"],
        fixtures_sha256=inputs["fixtures_sha256"],
        oracles_sha256=inputs["oracles_sha256"],
        response_schemas_sha256=inputs["response_schemas_sha256"],
        host_contract=host_contract, host_contract_sha256=host_contract_sha,
        **components,
    )
