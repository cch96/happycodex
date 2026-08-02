from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
from typing import Any, Callable

from evaluation.manifest import load_production_inputs
from evaluation.oracle import hidden_oracle_for, score_hidden
from evaluation.provider import sanitize_events
from evaluation.records import (
    build_attestation,
    canonical_json,
    canonical_sha256,
    validate_attestation,
    validate_eval_spec,
    validate_product_artifact,
)


class HostEvidenceError(ValueError):
    pass


def parse_raw_stream(raw: bytes) -> dict[str, Any]:
    if type(raw) is not bytes or not raw:
        raise HostEvidenceError("raw stream is empty")
    try:
        events = [json.loads(line) for line in raw.decode().splitlines() if line]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HostEvidenceError("raw stream is not JSONL") from exc
    if not events or not all(type(event) is dict for event in events):
        raise HostEvidenceError("raw stream event is invalid")
    kinds = [event.get("type") for event in events]
    if kinds != ["started", "report", "usage", "terminal"]:
        raise HostEvidenceError("raw stream event sequence differs")
    started, report_event, usage, finished = events
    if set(started) != {"type", "at"} or set(report_event) != {"type", "report"}:
        raise HostEvidenceError("raw start/report event fields differ")
    if set(usage) != {"type", "model_calls", "input_tokens", "output_tokens", "wall_milliseconds"}:
        raise HostEvidenceError("raw usage event fields differ")
    if set(finished) != {"type", "classification", "provider_reached", "complete", "at"}:
        raise HostEvidenceError("raw terminal event fields differ")
    terminal = {
        "classification": finished["classification"],
        "provider_reached": finished["provider_reached"],
        "complete": finished["complete"],
        "model_calls": usage["model_calls"], "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "wall_milliseconds": usage["wall_milliseconds"],
    }
    return {
        "events": events, "report": report_event["report"], "terminal": terminal,
        "started_at": started["at"], "frozen_at": finished["at"],
        "raw_events_sha256": hashlib.sha256(raw).hexdigest(),
    }


def attestation_from_raw(
    *, root: Path, product: dict[str, Any], spec: dict[str, Any], unit_id: str,
    raw: bytes, authority_sha256: str, host_proof: dict[str, Any],
    secrets: list[str] | None = None,
) -> dict[str, Any]:
    validate_product_artifact(product)
    validate_eval_spec(spec)
    unit = next((item for item in spec["units"] if item["unit_id"] == unit_id), None)
    if unit is None:
        raise HostEvidenceError("unit is absent from EvalSpec")
    if product["package_semantic_sha256"] != unit["product_semantic_sha256"] or product["external_role_config_sha256"] != unit["external_role_config_sha256"]:
        raise HostEvidenceError("host product differs from planned unit")
    parsed = parse_raw_stream(raw)
    sanitized = sanitize_events(parsed["events"], secrets=secrets or [])
    report = next(event["report"] for event in sanitized if event["type"] == "report")
    inputs = load_production_inputs(root)
    assessment = score_hidden(report, hidden_oracle_for(inputs, unit), stage=unit["stage"])
    observation = {
        "raw_events_sha256": parsed["raw_events_sha256"],
        "sanitized_event_sha256": canonical_sha256(sanitized),
        "terminal_sha256": canonical_sha256(parsed["terminal"]),
        "report": report, "report_sha256": canonical_sha256(report),
        "provenance": {
            "provider": "external-host", "model": unit["invocation"]["model"],
            "effort": unit["invocation"]["effort"],
            "tools": unit["invocation"]["tools"],
            "timeout_seconds": unit["invocation"]["timeout_seconds"],
        },
        "parent_attestation_sha256": None,
        "started_at": parsed["started_at"], "frozen_at": parsed["frozen_at"],
    }
    verdict = "pass" if assessment["passed"] and parsed["terminal"]["classification"] == "success" else "fail"
    return build_attestation(
        kind=unit["kind"], unit_id=unit_id,
        product_semantic_sha256=unit["product_semantic_sha256"],
        product_artifact_sha256=product["package_artifact_sha256"] if unit["stage"] == "exact_final" else None,
        external_role_config_sha256=unit["external_role_config_sha256"],
        provider_input_sha256=unit["provider_input_sha256"],
        oracle_sha256=unit["oracle_sha256"], harness_sha256=unit["harness_sha256"],
        invocation_sha256=unit["invocation_sha256"],
        authority_sha256=authority_sha256,
        host_claim_key=unit["invocation"]["claim_key"],
        host_proof_sha256=canonical_sha256(host_proof),
        observation=observation, terminal=parsed["terminal"], verdict=verdict,
        diagnostics=[f"diagnostic:{path}" for path in assessment["diagnostics"]],
    )


def verify_host_evidence(
    *, record: dict[str, Any], raw: bytes, proof: dict[str, Any],
    external_verifier: Callable[[dict[str, Any], dict[str, Any]], bool],
) -> dict[str, Any]:
    parsed = parse_raw_stream(raw)
    if record["observation"]["raw_events_sha256"] != parsed["raw_events_sha256"]:
        raise HostEvidenceError("raw stream digest differs from Attestation")
    if record["host_proof_sha256"] != canonical_sha256(proof):
        raise HostEvidenceError("external host proof digest differs")
    challenge = {
        "unit_id": record["unit_id"], "claim_key": record["host_claim_key"],
        "invocation_sha256": record["invocation_sha256"],
        "raw_events_sha256": parsed["raw_events_sha256"],
        "terminal_sha256": canonical_sha256(parsed["terminal"]),
    }
    if not external_verifier(proof, challenge):
        raise HostEvidenceError("external host proof was rejected")
    return parsed


def _safe_claim_root(root: Path) -> Path:
    root = root.absolute()
    if root.is_symlink() or not root.is_dir() or stat.S_IMODE(root.stat().st_mode) != 0o700:
        raise HostEvidenceError("claim root must be a real mode-0700 directory")
    return root


def reserve_claim(
    *, root: Path, claim_key: str, invocation_sha256: str,
    recovery_index: int = 0, recovery_cap: int = 0,
    previous_raw: bytes | None = None,
    previous_attestation: dict[str, Any] | None = None,
    previous_proof: dict[str, Any] | None = None,
    proof_verifier: Callable[[dict[str, Any], dict[str, Any]], bool] | None = None,
) -> dict[str, Any]:
    root = _safe_claim_root(root)
    if recovery_index:
        if (
            previous_raw is None or previous_attestation is None
            or previous_proof is None or proof_verifier is None
            or recovery_index > recovery_cap
        ):
            raise HostEvidenceError("recovery is outside the preauthorized cap")
        validate_attestation(previous_attestation)
        previous = verify_host_evidence(
            record=previous_attestation, raw=previous_raw,
            proof=previous_proof, external_verifier=proof_verifier,
        )["terminal"]
        if (
            previous_attestation["host_claim_key"] != claim_key
            or previous_attestation["invocation_sha256"] != invocation_sha256
        ):
            raise HostEvidenceError("recovery evidence binds another invocation")
        if not (
            previous["classification"] == "infrastructure_no_effect"
            and previous["provider_reached"] is False
            and previous["model_calls"] == 0
        ):
            raise HostEvidenceError("only proven pre-provider no-effect may recover")
    effective = canonical_sha256(
        {"claim_key": claim_key, "recovery_index": recovery_index}
    )
    path = root / f"{effective}.json"
    payload = {
        "schema_version": 1, "claim_key": claim_key,
        "effective_claim_key": effective, "invocation_sha256": invocation_sha256,
        "recovery_index": recovery_index,
    }
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise HostEvidenceError("provider claim is already reserved") from exc
    try:
        os.write(descriptor, (canonical_json(payload) + "\n").encode())
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    directory = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return {**payload, "path": str(path), "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
