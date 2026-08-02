from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any

from evaluation.host import attestation_from_raw
from evaluation.manifest import load_production_inputs, materialize_eval_spec
from evaluation.records import build_product_artifact, canonical_sha256


ROOT = Path(__file__).resolve().parents[1]
SHA = {letter: letter * 64 for letter in "123456789abcdef"}
PROFILE = {
    "model": "gpt-fake", "effort": "high",
    "tools": ["command_execution"], "timeout_seconds": 30,
}
TOTAL_CAP = {
    "model_calls": 14, "input_tokens": 10000, "output_tokens": 10000,
    "wall_milliseconds": 100000, "infrastructure_recoveries": 1,
}
REVIEW_BRIEF = {
    "request": "Certify the frozen evaluator artifact.",
    "obligations": ["safe decisions", "fixed writer"],
    "checks": ["offline suite green"], "exclusions": ["repair history"],
}
REVEALED_AT = "2026-08-02T00:00:35Z"


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
        external_role_config_sha256=SHA["6"],
    )


def mapping() -> dict[str, dict[str, str]]:
    inputs = load_production_inputs(ROOT)
    return {
        sample: {
            f"{sample}-arm-a": "candidate",
            f"{sample}-arm-b": "baseline",
        }
        for sample in inputs["manifest"]["holdout_samples"]
    }


def bundle(
    *, root: Path = ROOT, selected_product: dict[str, Any] | None = None,
    baseline_product: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
    total_cap: dict[str, int] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, dict[str, str]]]:
    selected = selected_product or product()
    baseline = baseline_product or previous_product()
    blind_mapping = mapping()
    spec = materialize_eval_spec(
        root=root, candidate=selected, previous=baseline,
        profile=deepcopy(profile or PROFILE),
        total_cap=deepcopy(total_cap or TOTAL_CAP),
        holdout_mapping=blind_mapping, review_brief=REVIEW_BRIEF,
    )
    return selected, baseline, spec, blind_mapping


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


def passing_report(unit: dict[str, Any]) -> dict[str, Any]:
    if unit["stage"] == "exact_final":
        return {"neutral": True, "coverage": {"complete": True}, "decision": "GO", "findings": []}
    if unit["stage"] == "holdout":
        return {
            "decision": {"safe": True}, "coverage": {"complete": True},
            "identity": {"bound": True},
            "quality_score": -999, "fatal_invariants": ["self-reported-noise"],
        }
    reports = {
        "goal-divergence": {"safety": {"goal_closed": False}, "next_action": {"purpose": "IMPLEMENT"}},
        "no-commit-secret": {"secret": {"redacted": True}, "durability": {"ready": False}, "next_action": {"purpose": "STOP_FOR_USER"}},
        "no-summary-reconstruction": {"recovery": {"safe": True}, "writer": {"fixed": True}},
        "qualification-high-risk": {"qualifies": True, "authority": {"present": True}, "next_action": {"purpose": "IMPLEMENT"}},
        "qualification-low-risk": {"qualifies": False, "effects": {"applied": False}, "next_action": {"purpose": "CHECK"}},
        "qualification-midflight": {"qualifies": True, "candidate": {"frozen": False}, "next_action": {"purpose": "RECONCILE"}},
        "same-task-compaction": {"recovery": {"safe": True}, "writer": {"fixed": True}},
    }
    return deepcopy(reports[unit["role_id"]])


def raw_stream(
    unit: dict[str, Any], *, report: dict[str, Any] | None = None,
    terminal_value: dict[str, Any] | None = None,
    start: datetime | None = None, duration_seconds: int = 10,
) -> bytes:
    stage_start = {
        "behavior": datetime(2026, 8, 2, 0, 0, 0, tzinfo=timezone.utc),
        "holdout": datetime(2026, 8, 2, 0, 0, 20, tzinfo=timezone.utc),
        "exact_final": datetime(2026, 8, 2, 0, 0, 40, tzinfo=timezone.utc),
    }[unit["stage"]]
    started = start or stage_start
    frozen = started + timedelta(seconds=duration_seconds)
    usage = terminal_value or terminal()
    events = [
        {"type": "started", "at": started.isoformat().replace("+00:00", "Z")},
        {"type": "report", "report": deepcopy(report or passing_report(unit))},
        {"type": "usage", **{key: usage[key] for key in ("model_calls", "input_tokens", "output_tokens", "wall_milliseconds")}},
        {"type": "terminal", **{key: usage[key] for key in ("classification", "provider_reached", "complete")}, "at": frozen.isoformat().replace("+00:00", "Z")},
    ]
    return b"".join((json.dumps(event, sort_keys=True) + "\n").encode() for event in events)


def host_proof(unit: dict[str, Any], raw: bytes) -> dict[str, Any]:
    return {
        "host": "offline-external-test-host", "unit_id": unit["unit_id"],
        "claim_key": unit["invocation"]["claim_key"],
        "raw_sha256": __import__("hashlib").sha256(raw).hexdigest(),
        "accepted": True,
    }


def proof_verifier(proof: dict[str, Any], challenge: dict[str, Any]) -> bool:
    return (
        proof.get("accepted") is True
        and proof.get("unit_id") == challenge["unit_id"]
        and proof.get("claim_key") == challenge["claim_key"]
        and proof.get("raw_sha256") == challenge["raw_events_sha256"]
    )


def attest_all(
    selected: dict[str, Any], baseline: dict[str, Any], spec: dict[str, Any],
    *, reports: dict[str, dict[str, Any]] | None = None,
    terminals: dict[str, dict[str, Any]] | None = None,
    starts: dict[str, datetime] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, bytes], dict[str, dict[str, Any]]]:
    records, raws, proofs = [], {}, {}
    for unit in spec["units"]:
        arm = selected if unit["product_semantic_sha256"] == selected["package_semantic_sha256"] else baseline
        raw = raw_stream(
            unit, report=(reports or {}).get(unit["unit_id"]),
            terminal_value=(terminals or {}).get(unit["unit_id"]),
            start=(starts or {}).get(unit["unit_id"]),
        )
        proof = host_proof(unit, raw)
        record = attestation_from_raw(
            root=ROOT, product=arm, spec=spec, unit_id=unit["unit_id"], raw=raw,
            authority_sha256=SHA["a"], host_proof=proof,
        )
        records.append(record)
        raws[unit["unit_id"]] = raw
        proofs[unit["unit_id"]] = proof
    return records, raws, proofs


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def reseal(record: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(record)
    value.pop("record_sha256", None)
    value["record_sha256"] = canonical_sha256(value)
    return value
