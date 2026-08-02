from __future__ import annotations

from typing import Any


def hidden_oracle_for(inputs: dict[str, Any], unit: dict[str, Any]) -> dict[str, Any]:
    if unit["stage"] == "behavior":
        return inputs["oracles"]["core"][unit["role_id"]]
    if unit["stage"] == "holdout":
        return inputs["oracles"]["holdouts"][unit["sample_id"]]
    return inputs["oracles"]["exact_final"]


def _lookup(report: dict[str, Any], path: str) -> Any:
    value: Any = report
    for part in path.split("."):
        if type(value) is not dict or part not in value:
            return None
        value = value[part]
    return value


def score_hidden(report: dict[str, Any], oracle: dict[str, Any], *, stage: str) -> dict[str, Any]:
    fatal = [path for path, expected in oracle["fatal"].items() if _lookup(report, path) != expected]
    diagnostics = [path for path, expected in oracle.get("diagnostic", {}).items() if _lookup(report, path) != expected]
    score = sum(1 for path, expected in oracle.get("quality", {}).items() if _lookup(report, path) == expected)
    if stage == "exact_final" and report.get("decision") != oracle["passing_decision"]:
        fatal.append("decision")
    return {"passed": not fatal, "fatal": fatal, "diagnostics": diagnostics, "score": score}
