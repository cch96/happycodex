"""Offline hidden scoring; oracle bytes never enter provider inputs."""
from __future__ import annotations

from typing import Any

from evaluation.canonical import ContractError, exact

class OracleError(ContractError):
    pass

def hidden_oracle_for(
    inputs: dict[str, Any], *, stage: str, role_id: str,
    sample_id: str | None = None,
) -> dict[str, Any]:
    exact(inputs, {"manifest", "cases", "oracles", "schemas"}, "production inputs")
    if stage == "behavior" and role_id in inputs["oracles"]["core"]:
        return inputs["oracles"]["core"][role_id]
    if stage == "holdout" and sample_id in inputs["oracles"]["holdouts"]:
        return inputs["oracles"]["holdouts"][sample_id]
    raise OracleError("hidden oracle routing differs")

def score_hidden(report: dict[str, Any], oracle: dict[str, Any]) -> dict[str, Any]:
    if type(report) is not dict or type(oracle) is not dict:
        raise OracleError("report or oracle is not an object")
    fatal_expected = oracle.get("fatal")
    quality_expected = oracle.get("quality")
    if type(fatal_expected) is not dict or type(quality_expected) is not dict:
        raise OracleError("hidden oracle shape differs")
    fatal = [field for field, expected in fatal_expected.items() if report.get(field) != expected]
    diagnostics = [
        field for field, expected in quality_expected.items() if report.get(field) != expected
    ]
    return {
        "passed": not fatal,
        "score": sum(report.get(field) == expected for field, expected in quality_expected.items()),
        "fatal": fatal,
        "diagnostics": diagnostics,
    }

__all__ = ("OracleError", "hidden_oracle_for", "score_hidden")
