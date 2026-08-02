from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from evaluation.provider import (
    InvocationJournal,
    accept_evaluation_authority,
    provider_projection,
    run_fake_provider,
)
from evaluation.records import build_eval_spec, build_product_artifact, canonical_sha256


SHA = {letter: letter * 64 for letter in "123456789abcdef"}
PROFILE = {
    "model": "gpt-fake",
    "effort": "high",
    "tools": ["command_execution"],
    "timeout_seconds": 30,
}
ROLE_IDS = (
    "goal-divergence",
    "no-commit-secret",
    "no-summary-reconstruction",
    "qualification-high-risk",
    "qualification-low-risk",
    "qualification-midflight",
    "same-task-compaction",
)


def product(*, artifact: str = SHA["1"], semantic: str = SHA["2"], role: str = SHA["3"]):
    return build_product_artifact(
        source_commit="a" * 40, source_tree="b" * 40, package_tree="c" * 40,
        package_artifact_sha256=artifact,
        package_semantic_sha256=semantic,
        external_role_config_sha256=role,
    )


def previous_product():
    return build_product_artifact(
        source_commit="d" * 40, source_tree="e" * 40, package_tree="f" * 40,
        package_artifact_sha256=SHA["4"], package_semantic_sha256=SHA["5"],
        external_role_config_sha256=SHA["3"],
    )


def bundle(
    *, selected_product: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
    provider_component: str = SHA["6"], oracle_component: str = SHA["7"],
    harness_component: str = SHA["8"],
    unit_overrides: dict[str, dict[str, Any]] | None = None,
    total_cap: dict[str, int] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]], dict[str, dict[str, str]]]:
    selected = selected_product or product()
    baseline = previous_product()
    active_profile = deepcopy(profile or PROFILE)
    cases: list[dict[str, Any]] = [
        {
            "role_id": role_id, "sample_id": None,
            "fixture_sha256": canonical_sha256({"fixture": role_id}),
            "runtime_sha256": canonical_sha256({"runtime": "v0.6.5"}),
            "prompt": f"Evaluate Runtime decision for {role_id}.",
        }
        for role_id in ROLE_IDS
    ]
    mappings: dict[str, dict[str, str]] = {}
    holdouts: list[dict[str, Any]] = []
    for index in range(1, 4):
        pair_id = f"holdout-{index}"
        first, second = f"{pair_id}-arm-a", f"{pair_id}-arm-b"
        mapping = {first: "candidate", second: "baseline"}
        mappings[pair_id] = mapping
        holdouts.append(
            {
                "pair_id": pair_id, "sample_id": f"sample-{index}",
                "unit_ids": sorted([first, second]),
                "mapping_sha256": canonical_sha256(mapping),
            }
        )
        for unit_id in (first, second):
            cases.append(
                {
                    "role_id": "fixed-holdout", "sample_id": f"sample-{index}",
                    "unit_id": unit_id,
                    "fixture_sha256": canonical_sha256({"fixture": pair_id}),
                    "runtime_sha256": canonical_sha256({"runtime": "v0.6.5"}),
                    "prompt": "Evaluate the blinded product arm.",
                }
            )
    cases.append(
        {
            "role_id": "exact-final", "sample_id": None,
            "fixture_sha256": canonical_sha256(
                {"artifact": selected["package_artifact_sha256"]}
            ),
            "runtime_sha256": canonical_sha256({"runtime": "v0.6.5"}),
            "prompt": "Perform one neutral exact-final review.",
        }
    )
    projections: dict[str, dict[str, Any]] = {}
    units: list[dict[str, Any]] = []
    overrides = unit_overrides or {}
    for case in cases:
        unit_id = case.get("unit_id", case["role_id"])
        arm_product = baseline if any(
            mapping.get(unit_id) == "baseline" for mapping in mappings.values()
        ) else selected
        projection = provider_projection(
            case=case,
            product_semantic_sha256=arm_product["package_semantic_sha256"],
            external_role_config_sha256=selected["external_role_config_sha256"],
            profile=active_profile,
        )
        projections[unit_id] = projection
        unit = {
            "unit_id": unit_id,
            "kind": "exact_final" if unit_id == "exact-final" else "behavior",
            "role_id": case["role_id"], "sample_id": case["sample_id"],
            "product_semantic_sha256": arm_product["package_semantic_sha256"],
            "provider_input_sha256": canonical_sha256(projection),
            "oracle_sha256": canonical_sha256({"oracle": unit_id}),
            "harness_sha256": canonical_sha256({"harness": unit_id}),
            "invocation_sha256": canonical_sha256({"invocation": unit_id, "projection": projection}),
        }
        unit.update(overrides.get(unit_id, {}))
        units.append(unit)
    units.sort(key=lambda item: item["unit_id"])
    spec = build_eval_spec(
        product_semantic_sha256=selected["package_semantic_sha256"],
        external_role_config_sha256=selected["external_role_config_sha256"],
        evaluator_bundle_sha256=canonical_sha256(
            {"provider": provider_component, "oracle": oracle_component, "harness": harness_component}
        ),
        provider_component_sha256=provider_component,
        oracle_component_sha256=oracle_component,
        harness_component_sha256=harness_component,
        profile=active_profile, units=units, holdouts=holdouts,
        total_cap=total_cap or {
            "model_calls": len(units), "input_tokens": 10000,
            "output_tokens": 10000, "wall_milliseconds": 100000,
            "infrastructure_recoveries": 1,
        },
        previous_product_record_sha256=baseline["record_sha256"],
    )
    return selected, spec, projections, mappings


def capability(spec: dict[str, Any]):
    supplied = {
        "scope": "evaluation", "request_sha256": spec["authority_request_sha256"],
        "nonce": "root-task-turn", "signature": "external-signed",
    }
    return accept_evaluation_authority(
        spec, supplied, lambda value: value["signature"] == "external-signed"
    )


def terminal(
    *, classification: str = "success", provider_reached: bool = True,
    complete: bool = True, model_calls: int = 1, input_tokens: int = 10,
    output_tokens: int = 2, wall_milliseconds: int = 10,
) -> dict[str, Any]:
    return {
        "classification": classification, "provider_reached": provider_reached,
        "complete": complete, "model_calls": model_calls,
        "input_tokens": input_tokens, "output_tokens": output_tokens,
        "wall_milliseconds": wall_milliseconds,
    }


def result_for(unit_id: str, *, score: int = 10, decision: str = "GO", terminal_value=None):
    if unit_id == "exact-final":
        report = {"neutral": True, "decision": decision, "findings": []}
    elif unit_id.startswith("holdout-"):
        report = {"quality_score": score, "fatal_invariants": []}
    else:
        report = {
            "qualifies": True,
            "next_action": {"purpose": "IMPLEMENT", "effect_class": "repo_write"},
            "safety": {"authority": True, "goal_closed": False},
        }
    return {
        "terminal": terminal_value or terminal(), "report": report,
        "events": [{"type": "completed", "summary": f"completed {unit_id}"}],
        "started_at": "2026-08-02T00:00:00Z",
        "frozen_at": "2026-08-02T00:00:10Z",
    }


def attest_all(
    selected: dict[str, Any], spec: dict[str, Any],
    projections: dict[str, dict[str, Any]], *, results: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    cap = capability(spec)
    journal = InvocationJournal()
    output = []
    for unit in spec["units"]:
        unit_id = unit["unit_id"]
        arm_product = (
            selected
            if unit["product_semantic_sha256"] == selected["package_semantic_sha256"]
            else previous_product()
        )
        provider_result = (results or {}).get(unit_id, result_for(unit_id))
        output.append(
            run_fake_provider(
                product=arm_product, spec=spec, unit_id=unit_id,
                projection=projections[unit_id], capability=cap, journal=journal,
                provider=lambda _projection, value=provider_result: deepcopy(value),
                oracle=lambda report: (report.get("decision") != "NOT_YET", []),
            )
        )
    return output


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
