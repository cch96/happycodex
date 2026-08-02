from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from evaluation.records import canonical_sha256, validate_attestation, validate_eval_spec


class HoldoutError(ValueError):
    pass


def _time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise HoldoutError("holdout timestamp is invalid") from exc
    if parsed.tzinfo is None:
        raise HoldoutError("holdout timestamp lacks timezone")
    return parsed.astimezone(timezone.utc)


def _ratio_ok(candidate: int, baseline: int) -> bool:
    return candidate == 0 if baseline == 0 else candidate * 100 <= baseline * 125


def judge_fixed_holdouts(
    *, spec: dict[str, Any], attestations: list[dict[str, Any]],
    mapping: dict[str, dict[str, str]], revealed_at: str,
    candidate_product: dict[str, Any], previous_product: dict[str, Any],
) -> dict[str, Any]:
    """Reveal and judge exactly three frozen, concurrent two-arm pairs."""
    validate_eval_spec(spec)
    if set(mapping) != {pair["pair_id"] for pair in spec["holdouts"]}:
        raise HoldoutError("holdout mapping set differs from the fixed plan")
    by_unit: dict[str, dict[str, Any]] = {}
    for attestation in attestations:
        validate_attestation(attestation)
        unit_id = attestation["unit_id"]
        if unit_id in by_unit:
            raise HoldoutError("duplicate holdout output")
        by_unit[unit_id] = attestation
    required = {unit for pair in spec["holdouts"] for unit in pair["unit_ids"]}
    if set(by_unit) != required or len(required) != 6:
        raise HoldoutError("all six fixed holdout outputs must freeze before reveal")
    reveal = _time(revealed_at)
    candidate_tokens = baseline_tokens = 0
    candidate_wall = baseline_wall = 0
    pair_results: list[dict[str, Any]] = []
    for pair in spec["holdouts"]:
        pair_mapping = mapping[pair["pair_id"]]
        if canonical_sha256(pair_mapping) != pair["mapping_sha256"]:
            raise HoldoutError("revealed mapping does not match its commitment")
        if set(pair_mapping) != set(pair["unit_ids"]) or sorted(pair_mapping.values()) != ["baseline", "candidate"]:
            raise HoldoutError("each holdout mapping needs one candidate and one baseline")
        arms = [by_unit[unit_id] for unit_id in pair["unit_ids"]]
        starts = [_time(item["observation"]["started_at"]) for item in arms]
        freezes = [_time(item["observation"]["frozen_at"]) for item in arms]
        if not all(frozen < reveal for frozen in freezes):
            raise HoldoutError("mapping was revealed before every output froze")
        if max(starts) >= min(freezes):
            raise HoldoutError("holdout pair arms did not run concurrently")
        labelled = {pair_mapping[item["unit_id"]]: item for item in arms}
        candidate = labelled["candidate"]
        baseline = labelled["baseline"]
        if candidate["product_semantic_sha256"] != candidate_product["package_semantic_sha256"]:
            raise HoldoutError("candidate arm does not bind candidate product")
        if baseline["product_semantic_sha256"] != previous_product["package_semantic_sha256"]:
            raise HoldoutError("baseline arm does not bind previous released product")
        for label, item in labelled.items():
            report = item["observation"]["report"]
            if type(report.get("quality_score")) is not int or type(report.get("fatal_invariants")) is not list:
                raise HoldoutError(f"{label} holdout report is not typed")
            if item["verdict"] != "pass" or report["fatal_invariants"]:
                raise HoldoutError(f"{label} holdout has a fatal quality failure")
        candidate_score = candidate["observation"]["report"]["quality_score"]
        baseline_score = baseline["observation"]["report"]["quality_score"]
        pair_passed = candidate_score >= baseline_score
        candidate_tokens += candidate["terminal"]["input_tokens"] + candidate["terminal"]["output_tokens"]
        baseline_tokens += baseline["terminal"]["input_tokens"] + baseline["terminal"]["output_tokens"]
        candidate_wall += candidate["terminal"]["wall_milliseconds"]
        baseline_wall += baseline["terminal"]["wall_milliseconds"]
        pair_results.append(
            {
                "pair_id": pair["pair_id"], "candidate_score": candidate_score,
                "baseline_score": baseline_score, "passed": pair_passed,
            }
        )
    token_ratio_ok = _ratio_ok(candidate_tokens, baseline_tokens)
    wall_ratio_ok = _ratio_ok(candidate_wall, baseline_wall)
    return {
        "passed": all(item["passed"] for item in pair_results) and token_ratio_ok and wall_ratio_ok,
        "pairs": pair_results,
        "aggregate": {
            "candidate_tokens": candidate_tokens, "baseline_tokens": baseline_tokens,
            "candidate_wall_milliseconds": candidate_wall,
            "baseline_wall_milliseconds": baseline_wall,
            "token_ratio_within_1_25": token_ratio_ok,
            "wall_ratio_within_1_25": wall_ratio_ok,
        },
        "revealed_mapping_sha256": canonical_sha256(mapping),
        "previous_product_record_sha256": spec["previous_product_record_sha256"],
    }
