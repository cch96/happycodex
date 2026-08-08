"""Load fixed inputs and construct/qualify the canonical EvalSpec."""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from evaluation.canonical import (
    ContractError,
    canonical_sha256,
    exact,
)
from evaluation.identity import (
    evaluator_components,
    validate_product_against_tree,
    validate_review_projection,
    validate_review_projection_against_git,
)
from evaluation.policy import (
    BEHAVIOR_ROLE_IDS,
    EXACT_FINAL_ROLE_ID,
    HOLDOUT_PAIR_TOPOLOGY,
    HOLDOUT_SAMPLE_IDS,
    UNIT_TOPOLOGY,
)
from evaluation.provider import (
    derive_unit_identities,
    evaluation_authority_request_payload,
    materialize_exact_final_input,
    materialize_provider_input,
    review_contract_sha256,
)
from evaluation.records import (
    build_eval_spec,
    validate_eval_spec,
    validate_product_artifact,
)
from evaluation.schemas import load_closed_json, validate_schema

MANIFEST_FILE = "manifest-v1.json"

class ManifestError(ContractError):
    pass

def load_production_inputs(root: Path) -> dict[str, Any]:
    evaluation = root.resolve(strict=True) / "evaluation"
    try:
        manifest = load_closed_json(
            evaluation / MANIFEST_FILE,
            required_fields=(
                "schema_version",
                "manifest_id",
                "provider_fixtures",
                "hidden_oracles",
                "report_schemas",
                "behavior_roles",
                "holdout_samples",
                "exact_final_role",
            ),
        )
        if (
            manifest["manifest_id"] != "happycodex-thin-verifier-v3"
            or manifest["provider_fixtures"] != "provider-fixtures-v1.json"
            or manifest["hidden_oracles"] != "hidden-oracles-v1.json"
            or manifest["report_schemas"] != "report-schemas-v1.json"
            or tuple(manifest["behavior_roles"]) != BEHAVIOR_ROLE_IDS
            or tuple(manifest["holdout_samples"]) != HOLDOUT_SAMPLE_IDS
            or manifest["exact_final_role"] != EXACT_FINAL_ROLE_ID
        ):
            raise ManifestError("production manifest contract differs")
        cases = load_closed_json(
            evaluation / manifest["provider_fixtures"],
            required_fields=("schema_version", "core", "holdouts"),
        )
        oracles = load_closed_json(
            evaluation / manifest["hidden_oracles"],
            required_fields=("schema_version", "core", "holdouts"),
        )
        schemas = load_closed_json(
            evaluation / manifest["report_schemas"],
            required_fields=(
                "schema_version",
                "provider_inputs",
                "provider_outputs",
            ),
        )
    except ContractError as exc:
        raise ManifestError(str(exc)) from exc
    if (
        tuple(cases["core"]) != BEHAVIOR_ROLE_IDS
        or tuple(oracles["core"]) != BEHAVIOR_ROLE_IDS
        or tuple(cases["holdouts"]) != HOLDOUT_SAMPLE_IDS
        or tuple(oracles["holdouts"]) != HOLDOUT_SAMPLE_IDS
    ):
        raise ManifestError("case/oracle topology differs")
    required_inputs = (
        *BEHAVIOR_ROLE_IDS,
        "holdout",
        "exact-final",
    )
    required_outputs = (
        *BEHAVIOR_ROLE_IDS,
        *HOLDOUT_SAMPLE_IDS,
        "exact_final",
    )
    if (
        tuple(schemas["provider_inputs"]) != required_inputs
        or tuple(schemas["provider_outputs"]) != required_outputs
    ):
        raise ManifestError("provider schema topology differs")
    try:
        for group in ("provider_inputs", "provider_outputs"):
            for name, schema in schemas[group].items():
                validate_schema(schema, f"{group}.{name}")
    except ContractError as exc:
        raise ManifestError(str(exc)) from exc
    return {
        "manifest": manifest,
        "cases": cases,
        "oracles": oracles,
        "schemas": schemas,
    }

def public_provider_inputs(inputs: dict[str, Any]) -> dict[str, Any]:
    exact(inputs, {"manifest", "cases", "oracles", "schemas"}, "production inputs")
    value = {
        "cases": {
            "core": inputs["cases"]["core"],
            "holdouts": inputs["cases"]["holdouts"],
        },
        "schemas": {
            "provider_inputs": inputs["schemas"]["provider_inputs"],
            "provider_outputs": inputs["schemas"]["provider_outputs"],
        },
    }
    return copy.deepcopy(value)

def _guidance(root: Path) -> str:
    root = root.resolve(strict=True)
    paths = (
        root / "skills/happycodex/SKILL.md",
        root / "skills/happycodex/references/execplan.md",
    )
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise ManifestError("provider guidance is missing or redirected")
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)

def _mappings(
    mappings: dict[str, dict[str, str]],
) -> tuple[dict[str, dict[str, str]], list[dict[str, Any]]]:
    if type(mappings) is not dict:
        raise ManifestError("holdout mappings are not an object")
    expected_pairs = tuple(pair[0] for pair in HOLDOUT_PAIR_TOPOLOGY)
    if set(mappings) != set(expected_pairs):
        raise ManifestError("holdout mapping topology differs")
    normalized = {}
    pairs = []
    for pair_id, sample_id, unit_ids in HOLDOUT_PAIR_TOPOLOGY:
        mapping = mappings[pair_id]
        if (
            type(mapping) is not dict
            or set(mapping) != set(unit_ids)
            or sorted(mapping.values()) != ["baseline", "candidate"]
        ):
            raise ManifestError("holdout pair mapping differs")
        normalized[pair_id] = dict(mapping)
        pairs.append(
            {
                "pair_id": pair_id,
                "sample_id": sample_id,
                "unit_ids": list(unit_ids),
                "mapping_commitment_sha256": canonical_sha256(mapping),
            }
        )
    return normalized, pairs

def materialize_production_unit_inputs(
    *,
    root: Path,
    previous_root: Path,
    product: dict[str, Any],
    previous_product: dict[str, Any],
    review_projection: dict[str, Any],
    holdout_mappings: dict[str, dict[str, str]],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    validate_product_against_tree(root, product)
    validate_product_against_tree(previous_root, previous_product)
    validate_review_projection(review_projection)
    inputs = load_production_inputs(root)
    public = public_provider_inputs(inputs)
    mappings, _ = _mappings(holdout_mappings)
    guidance = _guidance(root)
    previous_guidance = _guidance(previous_root)
    exact_input = materialize_exact_final_input(
        public,
        previous_product=previous_product,
        candidate_product=product,
        review_projection=review_projection,
    )
    materialized = {}
    for topology in UNIT_TOPOLOGY:
        if topology.stage == "behavior":
            value = materialize_provider_input(
                public,
                stage="behavior",
                role_id=topology.role_id,
                guidance=guidance,
            )
        elif topology.stage == "holdout":
            mapping = mappings[f"holdout-{topology.sample_id}"]
            selected = mapping[topology.unit_id]
            value = materialize_provider_input(
                public,
                stage="holdout",
                role_id=topology.role_id,
                sample_id=topology.sample_id,
                guidance=(
                    guidance if selected == "candidate" else previous_guidance
                ),
            )
        else:
            value = exact_input
        materialized[topology.unit_id] = value
    return materialized, inputs

def build_production_spec(
    *,
    root: Path,
    previous_root: Path,
    product: dict[str, Any],
    previous_product: dict[str, Any],
    review_projection: dict[str, Any],
    holdout_mappings: dict[str, dict[str, str]],
    caps: dict[str, int],
) -> dict[str, Any]:
    validate_product_artifact(product)
    validate_product_artifact(previous_product)
    unit_inputs, inputs = materialize_production_unit_inputs(
        root=root,
        previous_root=previous_root,
        product=product,
        previous_product=previous_product,
        review_projection=review_projection,
        holdout_mappings=holdout_mappings,
    )
    components = evaluator_components(root)
    public = public_provider_inputs(inputs)
    contract_sha = review_contract_sha256(public)
    units = []
    for topology in UNIT_TOPOLOGY:
        provider_sha = canonical_sha256(unit_inputs[topology.unit_id])
        if topology.stage == "behavior":
            oracle = inputs["oracles"]["core"][topology.role_id]
        elif topology.stage == "holdout":
            oracle = inputs["oracles"]["holdouts"][topology.sample_id]
        else:
            oracle = {
                "review_contract_sha256": contract_sha,
                "response_schema_sha256": canonical_sha256(
                    inputs["schemas"]["provider_outputs"]["exact_final"]
                ),
            }
        invocation, effect = derive_unit_identities(
            topology=topology,
            provider_input_sha256=provider_sha,
            provider_input_component_sha256=components["provider_input"],
            candidate_product_artifact_sha256=product["artifact_sha256"],
            review_contract_sha256_value=contract_sha,
        )
        units.append(
            {
                **topology._asdict(),
                "provider_input_sha256": provider_sha,
                "oracle_sha256": canonical_sha256(oracle),
                "invocation_sha256": invocation,
                "effect_subject_sha256": effect,
            }
        )
    _, pairs = _mappings(holdout_mappings)
    return build_eval_spec(
        product_artifact_sha256=product["artifact_sha256"],
        previous_product_artifact_sha256=previous_product["artifact_sha256"],
        component_identities=components,
        review_contract_sha256=contract_sha,
        units=units,
        holdout_pairs=pairs,
        caps=caps,
    )

def qualify_production_spec(
    spec: dict[str, Any],
    **construction: Any,
) -> dict[str, Any]:
    validate_eval_spec(spec)
    try:
        validate_review_projection_against_git(
            construction["root"], construction["review_projection"]
        )
        expected = build_production_spec(**construction)
    except ContractError as exc:
        raise ManifestError(str(exc)) from exc
    if expected != spec:
        raise ManifestError(
            "EvalSpec differs from current product/evaluator source identities"
        )
    return spec

def qualified_evaluation_authority_request(
    spec: dict[str, Any],
    **construction: Any,
) -> dict[str, Any]:
    qualify_production_spec(spec, **construction)
    return evaluation_authority_request_payload(
        spec,
        expected_component_identities=evaluator_components(
            construction["root"]
        ),
        product=construction["product"],
        previous_product=construction["previous_product"],
    )

__all__ = (
    "MANIFEST_FILE",
    "ManifestError",
    "build_production_spec",
    "load_production_inputs",
    "materialize_production_unit_inputs",
    "public_provider_inputs",
    "qualified_evaluation_authority_request",
    "qualify_production_spec",
)
