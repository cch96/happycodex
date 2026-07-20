from __future__ import annotations

import math
from typing import Any

from evaluation.holdout.blind import ACTUAL_ARMS, ALIASES, validate_reveal


PAIR_OUTCOMES = frozenset({"better", "equal", "regression", "uncertain"})
QUALITY_OUTCOMES = frozenset(
    {"materially_better", "equal", "regression", "inconclusive"}
)


def compare_pair(decision: dict[str, Any], reveal: dict[str, Any]) -> str:
    validate_reveal(reveal, decision)
    rows = {row["alias"]: row for row in decision["aliases"]}
    if set(rows) != set(ALIASES):
        raise ValueError("decision aliases do not match reveal")
    candidate = rows[reveal["mapping"]["candidate"]]["quality"]
    public = rows[reveal["mapping"]["public-0.2"]]["quality"]
    if candidate == "fail":
        return "regression"
    return "better" if public == "fail" else "equal"


def adaptive_next(outcomes: list[str]) -> str:
    if len(outcomes) > 3 or any(outcome not in PAIR_OUTCOMES for outcome in outcomes):
        raise ValueError("invalid adaptive holdout history")
    if "regression" in outcomes:
        return "reject"
    if not outcomes:
        return "run_first"
    if len(outcomes) == 1:
        return "run_second"
    if len(outcomes) == 2 and ("uncertain" in outcomes or outcomes[0] != outcomes[1]):
        return "run_third"
    return "stop"


def aggregate_quality(outcomes: list[str]) -> str:
    if not outcomes or any(outcome not in PAIR_OUTCOMES for outcome in outcomes):
        raise ValueError("invalid holdout outcomes")
    if "regression" in outcomes:
        return "regression"
    conclusive = [outcome for outcome in outcomes if outcome != "uncertain"]
    if len(outcomes) < 3 and "uncertain" in outcomes:
        return "inconclusive"
    if len(outcomes) == 3:
        if len(conclusive) < 2:
            return "inconclusive"
        better = conclusive.count("better")
        equal = conclusive.count("equal")
        if better == equal:
            return "inconclusive"
        return "materially_better" if better > equal else "equal"
    if len(set(conclusive)) > 1:
        return "inconclusive"
    if "better" in conclusive:
        return "materially_better"
    return "equal"


def ratio(numerator: float, denominator: float) -> float | str:
    if denominator == 0:
        return 1.0 if numerator == 0 else "infinity"
    return numerator / denominator


def exceeds_threshold(value: float | str) -> bool:
    return value == "infinity" or (isinstance(value, float) and value > 1.25)


def validate_metrics(metrics: dict[str, Any]) -> None:
    if set(metrics) != {
        "uncached_input_tokens",
        "output_tokens",
        "elapsed_seconds",
    }:
        raise ValueError("invalid cost metrics envelope")
    for field_name in ("uncached_input_tokens", "output_tokens"):
        value = metrics[field_name]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"invalid cost metric: {field_name}")
    elapsed = metrics["elapsed_seconds"]
    if (
        not isinstance(elapsed, (int, float))
        or isinstance(elapsed, bool)
        or not math.isfinite(elapsed)
        or elapsed < 0
    ):
        raise ValueError("invalid cost metric: elapsed_seconds")


def cost_gate(
    candidate: dict[str, Any], public: dict[str, Any], *, quality: str
) -> dict[str, Any]:
    validate_metrics(candidate)
    validate_metrics(public)
    if quality not in QUALITY_OUTCOMES:
        raise ValueError("invalid aggregate quality")
    candidate_combined = candidate["uncached_input_tokens"] + candidate["output_tokens"]
    public_combined = public["uncached_input_tokens"] + public["output_tokens"]
    blocking = {
        "combined_tokens": ratio(candidate_combined, public_combined),
        "wall": ratio(candidate["elapsed_seconds"], public["elapsed_seconds"]),
    }
    diagnostics = {
        "uncached_input_tokens": ratio(
            candidate["uncached_input_tokens"], public["uncached_input_tokens"]
        ),
        "output_tokens": ratio(candidate["output_tokens"], public["output_tokens"]),
    }
    expensive = any(exceeds_threshold(value) for value in blocking.values())
    if quality in {"regression", "inconclusive"}:
        decision = "reject"
    elif expensive and quality == "equal":
        decision = "simplify_and_retest"
    else:
        decision = "pass"
    return {
        "quality": quality,
        "threshold": 1.25,
        "candidate": {**candidate, "combined_tokens": candidate_combined},
        "public_0_2": {**public, "combined_tokens": public_combined},
        "blocking_ratios": blocking,
        "diagnostic_ratios": diagnostics,
        "decision": decision,
        "release_permitted": decision == "pass",
    }


def decision_metrics(
    decision: dict[str, Any], reveal: dict[str, Any]
) -> dict[str, Any]:
    validate_reveal(reveal, decision)
    rows = {row["alias"]: row for row in decision["aliases"]}
    return {arm: dict(rows[reveal["mapping"][arm]]["metrics"]) for arm in ACTUAL_ARMS}


def sum_metrics(values: list[dict[str, Any]]) -> dict[str, Any]:
    if not values:
        raise ValueError("cannot aggregate empty metrics")
    for value in values:
        validate_metrics(value)
    return {
        "uncached_input_tokens": sum(
            value["uncached_input_tokens"] for value in values
        ),
        "output_tokens": sum(value["output_tokens"] for value in values),
        "elapsed_seconds": round(sum(value["elapsed_seconds"] for value in values), 3),
    }
