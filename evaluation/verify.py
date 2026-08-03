from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from evaluation.holdout import judge_fixed_holdouts
from evaluation.manifest import load_production_inputs
from evaluation.oracle import hidden_oracle_for, score_hidden
from evaluation.provider import ReleaseCapability, release_authority_request, sanitize_events
from evaluation.records import (
    RecordError,
    build_attestation,
    build_release_receipt,
    canonical_sha256,
    validate_attestation,
    validate_eval_spec,
    validate_product_artifact,
    validate_release_receipt,
)


class HostEvidenceError(ValueError):
    pass


_USAGE_FIELDS = {
    "input_tokens", "cached_input_tokens", "cache_write_input_tokens",
    "output_tokens", "reasoning_output_tokens",
}


def _exact_native(value: dict[str, Any], fields: set[str], label: str) -> None:
    if type(value) is not dict or set(value) != fields:
        raise HostEvidenceError(f"{label} fields differ")


def _usage(value: Any) -> dict[str, int]:
    if type(value) is not dict or set(value) != _USAGE_FIELDS:
        raise HostEvidenceError("native usage fields differ")
    if not all(type(value[field]) is int and value[field] >= 0 for field in _USAGE_FIELDS):
        raise HostEvidenceError("native usage values are invalid")
    return value


def parse_raw_stream(raw: bytes) -> dict[str, Any]:
    if type(raw) is not bytes:
        raise HostEvidenceError("raw stream must be bytes")
    try:
        lines = raw.decode().splitlines()
        if any(not line for line in lines):
            raise HostEvidenceError("raw stream contains an empty JSONL event")
        events = [json.loads(line) for line in lines]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HostEvidenceError("raw stream is not JSONL") from exc
    if not all(type(event) is dict for event in events):
        raise HostEvidenceError("raw stream event is invalid")
    thread_id = None; turn_started = turn_completed = turn_failed = False
    failure_message = None; open_items = {}; completed_items = set()
    item_facts = []; report = usage = None
    for index, event in enumerate(events):
        kind = event.get("type")
        if kind == "thread.started":
            _exact_native(event, {"type", "thread_id"}, "thread.started")
            if index or thread_id is not None or type(event["thread_id"]) is not str or not event["thread_id"]:
                raise HostEvidenceError("native thread start is invalid or duplicated")
            thread_id = event["thread_id"]
        elif kind == "turn.started":
            _exact_native(event, {"type"}, "turn.started")
            if thread_id is None or turn_started or turn_completed:
                raise HostEvidenceError("native turn start is invalid or duplicated")
            turn_started = True
        elif kind in {"item.started", "item.completed"}:
            _exact_native(event, {"type", "item"}, kind); item = event["item"]
            if type(item) is not dict or type(item.get("id")) is not str or not item["id"] or type(item.get("type")) is not str or not item["type"]:
                raise HostEvidenceError("native item identity is invalid")
            if not turn_started or turn_completed:
                raise HostEvidenceError("native item is outside the single unfinished turn")
            item_id, item_type = item["id"], item["type"]
            if item_type == "agent_message":
                if kind != "item.completed" or set(item) != {"id", "type", "text"} or item_id in completed_items or open_items or type(item["text"]) is not str:
                    raise HostEvidenceError("native final agent message is invalid or duplicated")
                try: value = json.loads(item["text"])
                except json.JSONDecodeError as exc: raise HostEvidenceError("native final agent message is not JSON") from exc
                if type(value) is not dict: raise HostEvidenceError("native final agent message is not an object")
                report = value; completed_items.add(item_id)
            elif report is not None:
                raise HostEvidenceError("native non-agent item follows an agent report")
            elif kind == "item.started":
                if item_id in open_items or item_id in completed_items: raise HostEvidenceError("native item start is duplicated")
                open_items[item_id] = item_type
            else:
                if open_items.get(item_id) != item_type: raise HostEvidenceError("native item completion lacks a matching start")
                del open_items[item_id]; completed_items.add(item_id)
            item_facts.append({"event": kind, "id": item_id, "type": item_type})
        elif kind == "error":
            _exact_native(event, {"type", "message"}, "error")
            if not turn_started or turn_completed or turn_failed or report is not None or failure_message is not None or type(event["message"]) is not str or not event["message"]:
                raise HostEvidenceError("native error event is invalid")
            failure_message = event["message"]
        elif kind == "turn.failed":
            _exact_native(event, {"type", "error"}, "turn.failed"); error = event["error"]
            if index != len(events)-1 or not turn_started or turn_completed or turn_failed or report is not None or open_items or type(error) is not dict or set(error) != {"message"} or error.get("message") != failure_message:
                raise HostEvidenceError("native failed terminal is invalid")
            turn_failed = True
        elif kind == "turn.completed":
            _exact_native(event, {"type", "usage"}, "turn.completed")
            if index != len(events)-1 or not turn_started or turn_completed or open_items or report is None:
                raise HostEvidenceError("native turn terminal is invalid or not last")
            usage = _usage(event["usage"]); turn_completed = True
        else:
            raise HostEvidenceError("native stream event type is forbidden")
    if events and thread_id is None: raise HostEvidenceError("native stream lacks a thread start")
    if failure_message is not None and not turn_failed: raise HostEvidenceError("native error lacks its exact failed terminal")
    return {
        "events": events, "thread_id": thread_id, "turn_started": turn_started,
        "turn_completed": turn_completed, "turn_failed": turn_failed,
        "item_facts": item_facts, "report": report, "usage": usage,
        "failure_message_sha256": hashlib.sha256(failure_message.encode()).hexdigest() if failure_message is not None else None,
        "raw_events_sha256": hashlib.sha256(raw).hexdigest(),
    }


def _host_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    _exact_native(metadata, {"started_at", "frozen_at", "exit_code", "timed_out"}, "host metadata")
    if type(metadata["exit_code"]) is not int or type(metadata["timed_out"]) is not bool:
        raise HostEvidenceError("host exit metadata is invalid")
    try:
        started = datetime.fromisoformat(metadata["started_at"].replace("Z", "+00:00")); frozen = datetime.fromisoformat(metadata["frozen_at"].replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc: raise HostEvidenceError("host timestamps are invalid") from exc
    if started.tzinfo is None or frozen.tzinfo is None or frozen < started:
        raise HostEvidenceError("host timestamps lack timezone or run backwards")
    return {**metadata, "wall_milliseconds": int((frozen.astimezone(timezone.utc)-started.astimezone(timezone.utc)).total_seconds()*1000)}


def _terminal(parsed: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    host = _host_metadata(metadata); usage = parsed["usage"] or {field: 0 for field in _USAGE_FIELDS}
    if parsed["turn_completed"] and host["exit_code"] == 0 and not host["timed_out"]: classification, complete = "success", True
    elif host["exit_code"] != 0 and not host["timed_out"] and not parsed["turn_started"] and not parsed["turn_completed"] and parsed["report"] is None: classification, complete = "infrastructure_no_effect", False
    else: classification, complete = "ambiguous_or_partial", False
    return {"classification":classification,"provider_reached":parsed["turn_started"],"complete":complete,"model_calls":1 if parsed["turn_started"] else 0,"input_tokens":usage["input_tokens"],"output_tokens":usage["output_tokens"],"wall_milliseconds":host["wall_milliseconds"]}


def _sanitized(parsed: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    return {"schema_version":1,"thread_id":parsed["thread_id"],"turn_started":parsed["turn_started"],"turn_completed":parsed["turn_completed"],"turn_failed":parsed["turn_failed"],"failure_message_sha256":parsed["failure_message_sha256"],"items":parsed["item_facts"],"agent_report":report if parsed["report"] is not None else None,"usage":parsed["usage"]}


def attestation_from_raw(*, root: Path, product: dict[str, Any], spec: dict[str, Any], unit_id: str, raw: bytes, host_metadata: dict[str, Any], authority_sha256: str, secrets: list[str] | None = None) -> dict[str, Any]:
    validate_product_artifact(product); validate_eval_spec(spec)
    unit = next((item for item in spec["units"] if item["unit_id"] == unit_id), None)
    if unit is None: raise HostEvidenceError("unit is absent from EvalSpec")
    if product["package_semantic_sha256"] != unit["product_semantic_sha256"] or product["external_role_config_sha256"] != unit["external_role_config_sha256"]: raise HostEvidenceError("host product differs from planned unit")
    parsed = parse_raw_stream(raw); metadata = _host_metadata(host_metadata); terminal = _terminal(parsed, host_metadata)
    report = sanitize_events([parsed["report"]], secrets=secrets or [])[0] if parsed["report"] is not None else {}
    inputs = load_production_inputs(root); assessment = score_hidden(report, hidden_oracle_for(inputs, unit), stage=unit["stage"])
    observation = {
        "raw_events_sha256":parsed["raw_events_sha256"],"raw_report_sha256":canonical_sha256(parsed["report"]),"sanitized_event_sha256":canonical_sha256(_sanitized(parsed,report)),"terminal_sha256":canonical_sha256(terminal),"report":report,"report_sha256":canonical_sha256(report),
        "provenance":{"provider":"fixed-host-runner","model":unit["invocation"]["model"],"effort":unit["invocation"]["effort"],"tools":unit["invocation"]["tools"],"timeout_seconds":unit["invocation"]["timeout_seconds"]},"parent_attestation_sha256":None,
        "started_at":metadata["started_at"],"frozen_at":metadata["frozen_at"],"exit_code":metadata["exit_code"],"timed_out":metadata["timed_out"],
    }
    verdict = "pass" if assessment["passed"] and terminal["classification"] == "success" else "fail"
    diagnostics = [*(f"fatal:{path}" for path in assessment["fatal"]), *(f"diagnostic:{path}" for path in assessment["diagnostics"])]
    return build_attestation(kind=unit["kind"],unit_id=unit_id,product_semantic_sha256=unit["product_semantic_sha256"],product_artifact_sha256=product["package_artifact_sha256"] if unit["stage"]=="exact_final" else None,external_role_config_sha256=unit["external_role_config_sha256"],provider_input_sha256=unit["provider_input_sha256"],oracle_sha256=unit["oracle_sha256"],harness_sha256=unit["harness_sha256"],invocation_sha256=unit["invocation_sha256"],authority_sha256=authority_sha256,host_claim_key=unit["invocation"]["claim_key"],observation=observation,terminal=terminal,verdict=verdict,diagnostics=diagnostics)


def verify_host_evidence(*, record: dict[str, Any], unit: dict[str, Any], spec: dict[str, Any], raw: bytes) -> dict[str, Any]:
    validate_attestation(record); validate_eval_spec(spec); parsed = parse_raw_stream(raw); observation = record["observation"]
    if observation["raw_events_sha256"] != parsed["raw_events_sha256"]: raise HostEvidenceError("raw stream digest differs from Attestation")
    metadata = {key:observation[key] for key in ("started_at","frozen_at","exit_code","timed_out")}; terminal = _terminal(parsed,metadata)
    if observation["raw_report_sha256"] != canonical_sha256(parsed["report"]): raise HostEvidenceError("raw report digest differs from Attestation")
    if record["terminal"] != terminal or observation["terminal_sha256"] != canonical_sha256(terminal): raise HostEvidenceError("raw terminal differs from Attestation")
    if record["unit_id"] != unit["unit_id"] or record["invocation_sha256"] != unit["invocation_sha256"]: raise HostEvidenceError("fixed-host invocation differs from EvalSpec")
    if record["host_claim_key"] != unit["invocation"]["claim_key"] or unit["invocation"]["host_contract_sha256"] != spec["host_contract_sha256"]: raise HostEvidenceError("fixed-host claim or contract differs")
    if observation["sanitized_event_sha256"] != canonical_sha256(_sanitized(parsed,observation["report"])): raise HostEvidenceError("sanitized projection digest differs from Attestation")
    return {**parsed,"terminal":terminal,"started_at":observation["started_at"],"frozen_at":observation["frozen_at"]}


class VerificationError(ValueError):
    pass


def _unit_map(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {unit["unit_id"]: unit for unit in spec["units"]}


def invalidation(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, list[str]]:
    """Return the minimum work implied by component identity changes."""
    validate_eval_spec(previous)
    validate_eval_spec(current)
    old = _unit_map(previous)
    new = _unit_map(current)
    model: set[str] = set()
    replay: set[str] = set()
    offline: set[str] = set()
    global_provider_change = any(
        previous[field] != current[field]
        for field in ("product_semantic_sha256", "external_role_config_sha256", "provider_component_sha256", "host_contract_sha256")
    )
    global_oracle_change = previous["oracle_component_sha256"] != current["oracle_component_sha256"]
    for unit_id, unit in new.items():
        prior = old.get(unit_id)
        if global_provider_change or prior is None or prior["provider_input_sha256"] != unit["provider_input_sha256"]:
            model.add(unit_id)
        elif global_oracle_change:
            (model if unit["stage"] == "exact_final" else replay).add(unit_id)
        elif prior["oracle_sha256"] != unit["oracle_sha256"]:
            (model if unit["stage"] == "exact_final" else replay).add(unit_id)
        elif prior["harness_sha256"] != unit["harness_sha256"]:
            offline.add(unit_id)
    removed = set(old) - set(new)
    if removed or previous["harness_component_sha256"] != current["harness_component_sha256"]:
        offline.add("__bundle__")
    if previous["manifest_sha256"] != current["manifest_sha256"]:
        offline.add("__manifest__")
    if previous["fixtures_sha256"] != current["fixtures_sha256"] and not model:
        offline.add("__fixtures__")
    if previous["response_schemas_sha256"] != current["response_schemas_sha256"] and not model:
        offline.add("__response_schemas__")
    return {
        "model_units": sorted(model),
        "replay_units": sorted(replay - model),
        "offline_units": sorted(offline - model - replay),
    }


def _lookup(report: dict[str, Any], path: str) -> Any:
    value: Any = report
    for part in path.split("."):
        if type(value) is not dict or part not in value:
            return None
        value = value[part]
    return value


def evaluate_runtime_decision(
    report: dict[str, Any], oracle: dict[str, dict[str, Any]],
) -> tuple[bool, list[str]]:
    """Only invariant mismatches are fatal; conservative action labels diagnose."""
    if type(report) is not dict or set(oracle) != {"fatal", "diagnostic"}:
        raise VerificationError("runtime oracle is not typed")
    failures = [path for path, expected in oracle["fatal"].items() if _lookup(report, path) != expected]
    diagnostics = [
        f"equivalent-action:{path}:expected={expected!r}:actual={_lookup(report, path)!r}"
        for path, expected in oracle["diagnostic"].items()
        if _lookup(report, path) != expected
    ]
    return not failures, [*(f"fatal:{path}" for path in failures), *diagnostics]


def replay_attestation(
    *, parent: dict[str, Any], spec: dict[str, Any],
    oracle: Callable[[dict[str, Any]], tuple[bool, list[str]]],
) -> dict[str, Any]:
    validate_attestation(parent)
    validate_eval_spec(spec)
    if parent["kind"] not in {"behavior", "replay"}:
        raise VerificationError("only behavior observations can replay")
    unit = _unit_map(spec).get(parent["unit_id"])
    if unit is None or unit["kind"] != "behavior":
        raise VerificationError("replay unit is absent from EvalSpec")
    if parent["provider_input_sha256"] != unit["provider_input_sha256"]:
        raise VerificationError("provider input changed; replay is forbidden")
    if parent["external_role_config_sha256"] != unit["external_role_config_sha256"]:
        raise VerificationError("external role config changed; replay is forbidden")
    passed, diagnostics = oracle(parent["observation"]["report"])
    observation = {
        **parent["observation"],
        "parent_attestation_sha256": parent["record_sha256"],
    }
    return build_attestation(
        kind="replay", unit_id=unit["unit_id"],
        product_semantic_sha256=parent["product_semantic_sha256"],
        product_artifact_sha256=None,
        external_role_config_sha256=unit["external_role_config_sha256"],
        provider_input_sha256=unit["provider_input_sha256"],
        oracle_sha256=unit["oracle_sha256"], harness_sha256=unit["harness_sha256"],
        invocation_sha256=unit["invocation_sha256"],
        authority_sha256=parent["authority_sha256"],
        host_claim_key=parent["host_claim_key"],
        observation=observation,
        terminal=parent["terminal"], verdict="pass" if passed else "fail",
        diagnostics=diagnostics,
    )


def append_attestation(
    existing: list[dict[str, Any]], new: dict[str, Any],
) -> list[dict[str, Any]]:
    validate_attestation(new)
    for record in existing:
        validate_attestation(record)
        if record["unit_id"] == new["unit_id"]:
            if record["kind"] == "exact_final" and record["product_artifact_sha256"] == new["product_artifact_sha256"]:
                if record["verdict"] == "fail":
                    raise VerificationError("adverse exact-final is durable for unchanged artifact")
                raise VerificationError("exact-final invocation is one-shot for unchanged artifact")
            raise VerificationError("attestation unit already exists")
    return [*existing, new]


def _time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise VerificationError("evidence timestamp is invalid") from exc
    if parsed.tzinfo is None:
        raise VerificationError("evidence timestamp lacks timezone")
    return parsed.astimezone(timezone.utc)


def verify_evaluation(
    *, root: Path, product: dict[str, Any], spec: dict[str, Any],
    attestations: list[dict[str, Any]], raw_streams: dict[str, bytes],
    previous_product: dict[str, Any] | None = None,
    holdout_mapping: dict[str, dict[str, str]] | None = None,
    mapping_revealed_at: str | None = None,
) -> dict[str, Any]:
    validate_product_artifact(product)
    validate_eval_spec(spec)
    if product["package_semantic_sha256"] != spec["product_semantic_sha256"] or product["external_role_config_sha256"] != spec["external_role_config_sha256"]:
        raise VerificationError("ProductArtifact does not match EvalSpec")
    inputs = load_production_inputs(root)
    for field in ("manifest_sha256", "fixtures_sha256", "oracles_sha256", "response_schemas_sha256"):
        if spec[field] != inputs[field]:
            raise VerificationError(f"EvalSpec {field} differs from production input")
    planned = _unit_map(spec)
    by_unit: dict[str, dict[str, Any]] = {}
    assessments: dict[str, dict[str, Any]] = {}
    authority: str | None = None
    totals = {"model_calls": 0, "input_tokens": 0, "output_tokens": 0, "wall_milliseconds": 0}
    for record in attestations:
        validate_attestation(record)
        unit = planned.get(record["unit_id"])
        if unit is None or record["unit_id"] in by_unit:
            raise VerificationError("unknown or duplicate attestation unit")
        for field in ("external_role_config_sha256", "provider_input_sha256", "oracle_sha256", "harness_sha256", "invocation_sha256"):
            if record[field] != unit[field]:
                raise VerificationError(f"attestation {field} mismatch")
        if record["host_claim_key"] != unit["invocation"]["claim_key"]:
            raise VerificationError("attestation host claim mismatch")
        if record["product_semantic_sha256"] != unit["product_semantic_sha256"]:
            raise VerificationError("attestation product semantic mismatch")
        if unit["kind"] == "exact_final":
            if record["kind"] != "exact_final" or record["product_artifact_sha256"] != product["package_artifact_sha256"]:
                raise VerificationError("exact-final does not bind exact artifact")
        elif record["kind"] not in {"behavior", "replay"}:
            raise VerificationError("behavior unit has wrong attestation kind")
        authority = authority or record["authority_sha256"]
        if record["authority_sha256"] != authority:
            raise VerificationError("more than one evaluation authority bundle was used")
        if record["unit_id"] not in raw_streams:
            raise VerificationError("attestation lacks fixed-host raw evidence")
        try:
            parsed = verify_host_evidence(
                record=record, unit=unit, spec=spec,
                raw=raw_streams[record["unit_id"]],
            )
        except HostEvidenceError as exc:
            raise VerificationError(str(exc)) from exc
        observation = record["observation"]
        if _time(observation["started_at"]) > _time(observation["frozen_at"]):
            raise VerificationError("Attestation timestamps run backwards")
        if (
            parsed["terminal"] != record["terminal"]
            or parsed["started_at"] != observation["started_at"]
            or parsed["frozen_at"] != observation["frozen_at"]
        ):
            raise VerificationError("Attestation does not reproduce from raw evidence")
        provenance = observation["provenance"]
        if provenance["provider"] != "fixed-host-runner" or any(
            provenance[field] != unit["invocation"][field]
            for field in ("model", "effort", "tools", "timeout_seconds")
        ):
            raise VerificationError("Attestation provenance differs from invocation")
        assessment = score_hidden(
            observation["report"], hidden_oracle_for(inputs, unit), stage=unit["stage"]
        )
        expected_verdict = (
            "pass" if assessment["passed"] and parsed["terminal"]["classification"] == "success"
            else "fail"
        )
        if record["verdict"] != expected_verdict:
            raise VerificationError("Attestation verdict differs from hidden oracle recomputation")
        expected_diagnostics = [f"fatal:{path}" for path in assessment["fatal"]]
        expected_diagnostics.extend(f"diagnostic:{path}" for path in assessment["diagnostics"])
        if record["diagnostics"] != expected_diagnostics:
            raise VerificationError("Attestation diagnostics differ from hidden oracle recomputation")
        assessments[record["unit_id"]] = assessment
        for field in totals:
            totals[field] += parsed["terminal"][field]
            if totals[field] > spec["total_cap"][field]:
                raise VerificationError(f"evaluation exceeds total cap: {field}")
        by_unit[record["unit_id"]] = record
    if set(raw_streams) != set(by_unit):
        raise VerificationError("fixed-host raw inventory differs from attestations")
    failures = [
        {"unit_id": unit_id, "classification": record["terminal"]["classification"], "verdict": record["verdict"]}
        for unit_id, record in by_unit.items()
        if record["terminal"]["classification"] != "success"
        or (planned[unit_id]["stage"] != "holdout" and record["verdict"] != "pass")
    ]
    stage_units = {
        stage: {unit["unit_id"] for unit in planned.values() if unit["stage"] == stage}
        for stage in ("behavior", "holdout", "exact_final")
    }
    supplied = set(by_unit)
    if supplied & stage_units["holdout"] and not stage_units["behavior"].issubset(supplied):
        raise VerificationError("holdout started before behavior froze")
    if supplied & stage_units["holdout"]:
        behavior_frozen = max(_time(by_unit[unit_id]["observation"]["frozen_at"]) for unit_id in stage_units["behavior"])
        holdout_started = min(_time(by_unit[unit_id]["observation"]["started_at"]) for unit_id in supplied & stage_units["holdout"])
        if holdout_started <= behavior_frozen:
            raise VerificationError("holdout started before all behavior froze")
    if supplied & stage_units["exact_final"] and not (
        stage_units["behavior"] | stage_units["holdout"]
    ).issubset(supplied):
        raise VerificationError("exact-final started before behavior and holdout froze")
    if failures:
        failed_order = min(planned[item["unit_id"]]["order"] for item in failures)
        if any(planned[unit_id]["order"] > failed_order for unit_id in supplied):
            raise VerificationError("calls continued after a terminal failure")
        cutoff = min(_time(by_unit[item["unit_id"]]["observation"]["frozen_at"]) for item in failures)
        earliest = {
            item["unit_id"] for item in failures
            if _time(by_unit[item["unit_id"]]["observation"]["frozen_at"]) == cutoff
        }
        if any(
            unit_id not in earliest
            and _time(record["observation"]["started_at"]) >= cutoff
            for unit_id, record in by_unit.items()
        ):
            raise VerificationError("calls continued after a known terminal failure")
    exact_final = by_unit.get("exact-final")
    if exact_final is not None:
        prior = stage_units["behavior"] | stage_units["holdout"]
        prior_frozen = max(_time(by_unit[unit_id]["observation"]["frozen_at"]) for unit_id in prior)
        if _time(exact_final["observation"]["started_at"]) <= prior_frozen:
            raise VerificationError("exact-final started before prior stages froze")
    holdout = None
    full_success = not failures and supplied == set(planned)
    if full_success and (holdout_mapping is None or mapping_revealed_at is None):
        raise VerificationError("successful evaluation requires holdout mapping and reveal")
    if holdout_mapping is not None or mapping_revealed_at is not None:
        if holdout_mapping is None or mapping_revealed_at is None or previous_product is None:
            raise VerificationError("holdout mapping and reveal time are inseparable")
        validate_product_artifact(previous_product)
        if previous_product["record_sha256"] != spec["previous_product_record_sha256"]:
            raise VerificationError("holdout baseline is not the previous released product")
        holdout_units = {unit for pair in spec["holdouts"] for unit in pair["unit_ids"]}
        if not holdout_units.issubset(supplied):
            raise VerificationError("holdout mapping was supplied before all outputs froze")
        holdout = judge_fixed_holdouts(
            spec=spec, attestations=[by_unit[unit] for unit in sorted(holdout_units)],
            assessments={unit: assessments[unit] for unit in holdout_units},
            mapping=holdout_mapping, revealed_at=mapping_revealed_at,
            candidate_product=product, previous_product=previous_product,
        )
        if not holdout["passed"]:
            if exact_final is not None:
                raise VerificationError("calls continued after fixed-holdout failure")
            failures.append({"unit_id": "fixed-holdouts", "classification": "quality_failure", "verdict": "fail"})
        if exact_final is not None and _time(mapping_revealed_at) >= _time(exact_final["observation"]["started_at"]):
            raise VerificationError("exact-final started before holdout mapping reveal")
    if not failures and supplied != set(planned):
        raise VerificationError("successful evaluation lacks planned attestations")
    return {
        "verified": not failures, "failures": failures,
        "product_record_sha256": product["record_sha256"],
        "eval_spec_sha256": spec["record_sha256"],
        "attestation_sha256s": sorted(record["record_sha256"] for record in attestations),
        "exact_final_attestation_sha256": exact_final["record_sha256"] if exact_final else None,
        "authority_sha256": authority, "usage": totals, "holdout": holdout,
    }


def create_release_receipt(
    *, product: dict[str, Any], evaluation: dict[str, Any],
    isolated_install: dict[str, Any], destination: dict[str, Any],
    rollback: dict[str, Any], capability: ReleaseCapability,
) -> dict[str, Any]:
    validate_product_artifact(product)
    if evaluation.get("verified") is not True or evaluation.get("holdout", {}).get("passed") is not True:
        raise VerificationError("release requires a fully verified evaluation")
    request = release_authority_request(
        product_record_sha256=product["record_sha256"],
        attestation_sha256s=evaluation["attestation_sha256s"],
        destination_sha256=canonical_sha256(destination),
        rollback_sha256=canonical_sha256(rollback),
    )
    if capability.request_sha256 != request:
        raise VerificationError("release capability does not bind this effect")
    if capability.authority_sha256 == evaluation["authority_sha256"]:
        raise VerificationError("evaluation authority cannot authorize release")
    return build_release_receipt(
        product_record_sha256=product["record_sha256"],
        product_artifact_sha256=product["package_artifact_sha256"],
        attestation_sha256s=evaluation["attestation_sha256s"],
        exact_final_attestation_sha256=evaluation["exact_final_attestation_sha256"],
        isolated_install=isolated_install, destination=destination,
        rollback=rollback, release_authority_sha256=capability.authority_sha256,
    )


def verify_release(
    *, product: dict[str, Any], evaluation: dict[str, Any],
    receipt: dict[str, Any], destination: dict[str, Any], rollback: dict[str, Any],
) -> dict[str, Any]:
    validate_product_artifact(product)
    validate_release_receipt(receipt)
    if not evaluation.get("verified") or not evaluation.get("holdout", {}).get("passed"):
        raise VerificationError("release evaluation is not qualifying")
    checks = {
        "product": receipt["product_record_sha256"] == product["record_sha256"],
        "artifact": receipt["product_artifact_sha256"] == product["package_artifact_sha256"] == receipt["isolated_install"]["artifact_sha256"],
        "attestations": receipt["attestation_sha256s"] == evaluation["attestation_sha256s"],
        "exact_final": receipt["exact_final_attestation_sha256"] == evaluation["exact_final_attestation_sha256"],
        "destination": receipt["destination"] == destination,
        "rollback": receipt["rollback"] == rollback,
        "authority_separate": receipt["release_authority_sha256"] != evaluation["authority_sha256"],
    }
    if not all(checks.values()):
        raise VerificationError("ReleaseReceipt identity/effect mismatch")
    return {"verified": True, "checks": checks, "release_receipt_sha256": receipt["record_sha256"]}
