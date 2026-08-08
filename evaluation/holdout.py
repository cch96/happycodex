"""Blind judging for the fixed three holdout pairs."""
from __future__ import annotations
from datetime import datetime, timezone
import json
from typing import Any
from evaluation.canonical import ContractError, canonical_sha256, canonical_text, exact
from evaluation.records import validate_eval_spec

class HoldoutError(ContractError):
    pass

_TERMINAL = object()

class VerifiedEffectTerminal:
    """Opaque value produced only after an authenticated sequence verifies."""
    __slots__ = ("_json", "attempt_sha256s")
    def __init__(self, record: dict[str, Any], attempts: list[dict[str, Any]], token: object):
        if token is not _TERMINAL:
            raise HoldoutError("VerifiedEffectTerminal is verifier-owned")
        self._json = canonical_text(record)
        self.attempt_sha256s = tuple(item["record_sha256"] for item in attempts)
    @property
    def record(self) -> dict[str, Any]:
        return json.loads(self._json)

def _verified_terminal(record: dict[str, Any], attempts: list[dict[str, Any]]) -> VerifiedEffectTerminal:
    return VerifiedEffectTerminal(record, attempts, _TERMINAL)

def _records(terminals: list[VerifiedEffectTerminal]) -> list[dict[str, Any]]:
    if not all(isinstance(item, VerifiedEffectTerminal) for item in terminals):
        raise HoldoutError("effect terminals are not verified")
    return [item.record for item in terminals]

def _six(spec: dict[str, Any], terminals: list[VerifiedEffectTerminal]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    validate_eval_spec(spec)
    records = _records(terminals)
    required = {unit["unit_id"] for unit in spec["units"] if unit["stage"] == "holdout"}
    by_unit = {record["unit_id"]: record for record in records}
    planned = {unit["unit_id"]: unit for unit in spec["units"] if unit["stage"] == "holdout"}
    if (
        len(records) != 6 or len(by_unit) != 6 or set(by_unit) != required
        or any(record["effect_outcome"] != "landed" for record in records)
        or any(
            record["spec_sha256"] != spec["spec_sha256"]
            or record["effect_subject_sha256"] != planned[record["unit_id"]]["effect_subject_sha256"]
            for record in records
        )
    ):
        raise HoldoutError("all six fixed holdout terminals must land before scoring")
    return records, by_unit

def _time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise HoldoutError("authenticated holdout timestamp is invalid") from exc
    if parsed.tzinfo is None:
        raise HoldoutError("authenticated holdout timestamp lacks timezone")
    return parsed.astimezone(timezone.utc)

def _ratio(candidate: int, baseline: int) -> bool:
    return candidate == 0 if baseline == 0 else candidate * 1000 <= baseline * 1250

def judge_fixed_holdouts(
    *, spec: dict[str, Any], terminals: list[VerifiedEffectTerminal],
    mappings: dict[str, dict[str, str]],
) -> dict[str, Any]:
    """Judge only after exactly six authenticated landed outputs are present."""
    records, by_unit = _six(spec, terminals)
    if type(mappings) is not dict or set(mappings) != {
        pair["pair_id"] for pair in spec["holdout_pairs"]
    }:
        raise HoldoutError("holdout mapping set differs")
    totals = {key: 0 for key in (
        "candidate_tokens", "baseline_tokens", "candidate_wall_milliseconds",
        "baseline_wall_milliseconds",
    )}
    results = []
    for pair in spec["holdout_pairs"]:
        mapping = mappings[pair["pair_id"]]
        if (
            type(mapping) is not dict or set(mapping) != set(pair["unit_ids"])
            or sorted(mapping.values()) != ["baseline", "candidate"]
            or canonical_sha256(mapping) != pair["mapping_commitment_sha256"]
        ):
            raise HoldoutError("holdout mapping differs from its commitment")
        labelled = {label: by_unit[unit_id] for unit_id, label in mapping.items()}
        candidate, baseline = labelled["candidate"], labelled["baseline"]
        if max(_time(item["observation"]["started_at"]) for item in labelled.values()) >= min(
            _time(item["observation"]["finished_at"]) for item in labelled.values()
        ):
            raise HoldoutError("holdout pair arms were not concurrent")
        if (
            candidate["product_artifact_sha256"] != spec["product_artifact_sha256"]
            or baseline["product_artifact_sha256"] != spec["previous_product_artifact_sha256"]
        ):
            raise HoldoutError("holdout product arms differ")
        candidate_score, baseline_score = (
            candidate["assessment"]["score"], baseline["assessment"]["score"],
        )
        results.append({
            "pair_id": pair["pair_id"], "candidate_unit_id": candidate["unit_id"],
            "baseline_unit_id": baseline["unit_id"], "candidate_score": candidate_score,
            "baseline_score": baseline_score,
            "passed": candidate["assessment"]["passed"] and candidate_score >= baseline_score,
        })
        for label, record in (("candidate", candidate), ("baseline", baseline)):
            observation = record["observation"]
            totals[f"{label}_tokens"] += observation["input_tokens"] + observation["output_tokens"]
            totals[f"{label}_wall_milliseconds"] += observation["effect_cumulative_wall_milliseconds"]
    aggregate = {
        **totals,
        "token_ratio_within_1_25": _ratio(totals["candidate_tokens"], totals["baseline_tokens"]),
        "wall_ratio_within_1_25_diagnostic": _ratio(
            totals["candidate_wall_milliseconds"], totals["baseline_wall_milliseconds"],
        ),
    }
    body = {
        "spec_sha256": spec["spec_sha256"],
        "terminal_attestation_sha256s": sorted(record["record_sha256"] for record in records),
        "pairs": results, "aggregate": aggregate,
        "passed": all(pair["passed"] for pair in results) and aggregate["token_ratio_within_1_25"],
    }
    return {**body, "result_sha256": canonical_sha256(body)}

def validate_holdout_result(
    result: dict[str, Any], *, spec: dict[str, Any], terminals: list[VerifiedEffectTerminal],
) -> dict[str, Any]:
    """Recompute a caller-supplied result from its authenticated terminals."""
    _six(spec, terminals)  # Mapping data is intentionally unread before this gate.
    exact(result, {
        "spec_sha256", "terminal_attestation_sha256s", "pairs", "aggregate",
        "passed", "result_sha256",
    }, "holdout result")
    if type(result["pairs"]) is not list or len(result["pairs"]) != 3:
        raise HoldoutError("holdout result pair count differs")
    mappings = {}
    for planned, observed in zip(spec["holdout_pairs"], result["pairs"]):
        exact(observed, {
            "pair_id", "candidate_unit_id", "baseline_unit_id", "candidate_score",
            "baseline_score", "passed",
        }, "holdout pair result")
        if observed["pair_id"] != planned["pair_id"]:
            raise HoldoutError("holdout result pair differs")
        mappings[planned["pair_id"]] = {
            observed["candidate_unit_id"]: "candidate",
            observed["baseline_unit_id"]: "baseline",
        }
    if result != judge_fixed_holdouts(spec=spec, terminals=terminals, mappings=mappings):
        raise HoldoutError("holdout result was not recomputed")
    return result

__all__ = (
    "HoldoutError", "VerifiedEffectTerminal", "judge_fixed_holdouts",
    "validate_holdout_result",
)
