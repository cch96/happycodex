from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any

from evaluation.core.identity import (
    canonical_json_bytes,
    canonical_sha256,
    sha256_bytes,
)
from evaluation.core.impact import validate_snapshot
from evaluation.corpus.contract import PERMISSION_FIELDS


LEDGER_FIELDS = {
    "schema_version",
    "state",
    "snapshot",
    "prior_evidence",
    "pending",
    "historical_cost",
    "live_authority",
    "certification",
}
PENDING_FIELDS = {"reasons", "corpus_cases", "holdout_pairs", "review"}
AUTHORITY_FIELDS = {
    "schema_version",
    "source",
    "source_sha256",
    "impact_sha256",
    "invocations",
}
CORPUS_INVOCATION_FIELDS = {
    "command",
    "package_semantic_sha256",
    "package_artifact_sha256",
    "model",
    "effort",
    "timeout_seconds",
    "arm",
    "cases",
}
HOLDOUT_INVOCATION_FIELDS = {
    "command",
    "candidate_semantic_sha256",
    "candidate_artifact_sha256",
    "public_semantic_sha256",
    "public_artifact_sha256",
    "model",
    "effort",
    "timeout_seconds",
    "pairs",
}
CERTIFICATION_FIELDS = {
    "schema_version",
    "successor_source_commit",
    "successor_source_tree",
    "snapshot_sha256",
    "engine_manifest_sha256",
    "corpus_receipt_sha256",
    "holdout_receipt_sha256",
    "review_receipt_sha256",
    "live_authority_sha256",
}


def _require_digest(value: Any, *, length: int, label: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(rf"[0-9a-f]{{{length}}}", value):
        raise ValueError(f"invalid {label}")


def _validate_ordered_names(value: Any, *, label: str) -> None:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item for item in value)
        or value != sorted(set(value))
    ):
        raise ValueError(f"invalid authorized {label}")


def _validate_invocation(invocation: Any) -> None:
    if not isinstance(invocation, dict):
        raise ValueError("invalid authorized invocation")
    command = invocation.get("command")
    fields = {
        "corpus": CORPUS_INVOCATION_FIELDS,
        "holdout": HOLDOUT_INVOCATION_FIELDS,
    }.get(command)
    if fields is None or set(invocation) != fields:
        raise ValueError("invalid authorized invocation envelope")
    for field in ("model", "effort"):
        if not isinstance(invocation[field], str) or not invocation[field]:
            raise ValueError(f"invalid authorized invocation field: {field}")
    timeout = invocation["timeout_seconds"]
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("invalid authorized invocation field: timeout_seconds")
    if command == "corpus":
        digest_fields = ("package_semantic_sha256", "package_artifact_sha256")
        if invocation["arm"] != "candidate":
            raise ValueError("authorized corpus invocation must use candidate arm")
        _validate_ordered_names(invocation["cases"], label="corpus cases")
    else:
        digest_fields = (
            "candidate_semantic_sha256",
            "candidate_artifact_sha256",
            "public_semantic_sha256",
            "public_artifact_sha256",
        )
        _validate_ordered_names(invocation["pairs"], label="holdout pairs")
    for field in digest_fields:
        _require_digest(invocation[field], length=64, label=field)


def validate_live_authority(authority: Any) -> None:
    if not isinstance(authority, dict) or set(authority) != AUTHORITY_FIELDS:
        raise ValueError("live authority is not persisted")
    if authority.get("schema_version") != 1:
        raise ValueError("invalid live authority schema")
    if not isinstance(authority.get("source"), str) or not re.fullmatch(
        r"current-task/user/[a-z0-9][a-z0-9._/-]*", authority["source"]
    ):
        raise ValueError("invalid live authority source")
    _require_digest(authority.get("source_sha256"), length=64, label="authority source")
    _require_digest(authority.get("impact_sha256"), length=64, label="authority impact")
    invocations = authority.get("invocations")
    if not isinstance(invocations, list) or not invocations:
        raise ValueError("live authority requires exact invocations")
    for invocation in invocations:
        _validate_invocation(invocation)
    invocation_digests = [
        sha256_bytes(canonical_json_bytes(invocation)) for invocation in invocations
    ]
    if len(set(invocation_digests)) != len(invocation_digests):
        raise ValueError("live authority contains duplicate invocations")


def require_authorized_invocation(
    authority: Any, *, impact_sha256: str, invocation: dict[str, Any]
) -> None:
    validate_live_authority(authority)
    if authority["impact_sha256"] != impact_sha256:
        raise ValueError("live authority does not match current impact")
    _validate_invocation(invocation)
    requested = sha256_bytes(canonical_json_bytes(invocation))
    authorized = {
        sha256_bytes(canonical_json_bytes(item)) for item in authority["invocations"]
    }
    if requested not in authorized:
        raise ValueError("invocation is not authorized")


def _validate_certification_receipt(
    certification: Any,
    *,
    snapshot: dict[str, Any],
    live_authority: dict[str, Any] | None,
) -> None:
    if (
        not isinstance(certification, dict)
        or set(certification) != CERTIFICATION_FIELDS
    ):
        raise ValueError("invalid certification receipt")
    if certification.get("schema_version") != 1:
        raise ValueError("invalid certification receipt schema")
    for field in ("successor_source_commit", "successor_source_tree"):
        _require_digest(certification.get(field), length=40, label=field)
    for field in CERTIFICATION_FIELDS - {
        "schema_version",
        "successor_source_commit",
        "successor_source_tree",
    }:
        _require_digest(certification.get(field), length=64, label=field)
    snapshot_sha256 = sha256_bytes(canonical_json_bytes(snapshot))
    if certification["snapshot_sha256"] != snapshot_sha256:
        raise ValueError("certification receipt snapshot mismatch")
    engine = snapshot.get("engine")
    if not isinstance(engine, dict) or certification[
        "engine_manifest_sha256"
    ] != engine.get("manifest_sha256"):
        raise ValueError("certification receipt engine manifest mismatch")
    if live_authority is None:
        raise ValueError("certification receipt requires live authority")
    authority_sha256 = sha256_bytes(canonical_json_bytes(live_authority))
    if certification["live_authority_sha256"] != authority_sha256:
        raise ValueError("certification receipt authority mismatch")
    settings = snapshot.get("settings")
    package = snapshot.get("package")
    if not isinstance(settings, dict) or not isinstance(package, dict):
        raise ValueError("certification receipt has invalid snapshot identities")
    for invocation in live_authority["invocations"]:
        if (
            invocation["model"] != settings.get("model")
            or invocation["effort"] != settings.get("effort")
            or invocation["timeout_seconds"] != settings.get("timeout_seconds")
        ):
            raise ValueError("certification authority settings mismatch")
        if invocation["command"] == "corpus":
            candidate = {
                "semantic_sha256": invocation["package_semantic_sha256"],
                "artifact_sha256": invocation["package_artifact_sha256"],
            }
        else:
            candidate = {
                "semantic_sha256": invocation["candidate_semantic_sha256"],
                "artifact_sha256": invocation["candidate_artifact_sha256"],
            }
        if candidate != package:
            raise ValueError("certification authority package mismatch")


def validate_ledger(ledger: dict[str, Any]) -> None:
    if set(ledger) != LEDGER_FIELDS or ledger.get("schema_version") != 1:
        raise ValueError("invalid certification ledger envelope")
    state = ledger.get("state")
    if state not in {"refresh_required", "certified"}:
        raise ValueError("invalid certification ledger state")
    snapshot = ledger.get("snapshot")
    if not isinstance(snapshot, dict) or snapshot.get("schema_version") != 1:
        raise ValueError("invalid certification snapshot")
    validate_snapshot(snapshot)
    prior = ledger.get("prior_evidence")
    if not isinstance(prior, dict):
        raise ValueError("invalid prior evidence")
    for field in ("source_commit", "source_path", "sha256"):
        if not isinstance(prior.get(field), str):
            raise ValueError(f"invalid prior evidence field: {field}")
    if not re.fullmatch(r"[0-9a-f]{40}", prior["source_commit"]):
        raise ValueError("invalid prior evidence commit")
    if not re.fullmatch(r"[0-9a-f]{64}", prior["sha256"]):
        raise ValueError("invalid prior evidence digest")
    pending = ledger.get("pending")
    if not isinstance(pending, dict) or set(pending) != PENDING_FIELDS:
        raise ValueError("invalid pending refresh envelope")
    if not isinstance(pending["reasons"], list) or not all(
        isinstance(item, str) and item for item in pending["reasons"]
    ):
        raise ValueError("invalid pending reasons")
    for field in ("corpus_cases", "holdout_pairs"):
        value = pending[field]
        if (
            not isinstance(value, list)
            or not all(isinstance(item, str) and item for item in value)
            or value != sorted(set(value))
        ):
            raise ValueError(f"invalid pending scope: {field}")
    if not isinstance(pending["review"], bool):
        raise ValueError("invalid pending review gate")
    if not isinstance(ledger.get("historical_cost"), dict):
        raise ValueError("invalid historical cost receipt")
    live_authority = ledger.get("live_authority")
    if live_authority is not None:
        validate_live_authority(live_authority)
    certification = ledger.get("certification")
    if state == "refresh_required":
        if certification is not None:
            raise ValueError("refresh-required ledger cannot carry certification")
        if not (
            pending["reasons"]
            or pending["corpus_cases"]
            or pending["holdout_pairs"]
            or pending["review"]
        ):
            raise ValueError("refresh-required ledger must name a pending gate")
    else:
        if (
            pending["reasons"]
            or pending["corpus_cases"]
            or pending["holdout_pairs"]
            or pending["review"]
        ):
            raise ValueError("certified ledger cannot retain pending gates")
        _validate_certification_receipt(
            certification,
            snapshot=snapshot,
            live_authority=live_authority,
        )


def text_sha256(value: Any) -> str:
    return sha256_bytes(str(value).encode())


def sanitized_recovery_receipt(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    receipt: dict[str, Any] = {"recovery_state_sha256": canonical_sha256(value)}
    for field in (
        "baseline_revision",
        "baseline_tree",
        "current_revision",
        "current_tree",
    ):
        item = value.get(field)
        receipt[field] = (
            item
            if isinstance(item, str) and re.fullmatch(r"[0-9a-f]{40}", item)
            else None
        )
    for field in ("writer", "milestone_phase", "next_action", "worktree"):
        receipt[field] = value.get(field)
    pending = value.get("pending_gates", [])
    receipt["pending_gates"] = pending if isinstance(pending, list) else []
    tests = value.get("tests", {})
    markers = tests.get("marker_ids", []) if isinstance(tests, dict) else []
    receipt["tests"] = {
        key: tests.get(key) if isinstance(tests, dict) else None
        for key in ("passed", "failed", "accepted_failures")
    }
    receipt["tests"].update(
        {
            "marker_ids_count": len(markers) if isinstance(markers, list) else 0,
            "marker_ids_sha256": canonical_sha256(markers),
        }
    )
    agents = value.get("live_agents", [])
    receipt["live_agents"] = (
        [
            {
                "id_sha256": text_sha256(agent.get("id", "")),
                "status": agent.get("status"),
                "receipt_reproduced": agent.get("receipt_reproduced"),
            }
            for agent in agents
            if isinstance(agent, dict)
        ]
        if isinstance(agents, list)
        else []
    )
    marker_ids = value.get("marker_ids", [])
    receipt["marker_ids_count"] = len(marker_ids) if isinstance(marker_ids, list) else 0
    receipt["marker_ids_sha256"] = canonical_sha256(marker_ids)
    return receipt


def sanitized_result_receipt(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        return {"result_sha256": canonical_sha256(value)}
    receipt: dict[str, Any] = {"result_sha256": canonical_sha256(value)}
    for field in sorted(PERMISSION_FIELDS):
        receipt[field] = value.get(field)
    findings = value.get("finding_classifications", [])
    receipt["finding_classifications"] = (
        [
            {
                "identity_sha256": text_sha256(item.get("identity", "")),
                "domain": item.get("domain"),
                "state": item.get("state"),
                "anchors_count": len(item.get("anchors", []))
                if isinstance(item.get("anchors", []), list)
                else 0,
                "anchors_sha256": canonical_sha256(item.get("anchors", [])),
            }
            for item in findings
            if isinstance(item, dict)
        ]
        if isinstance(findings, list)
        else []
    )
    blockers = value.get("blocker_classifications", [])
    receipt["blocker_classifications"] = (
        [
            {
                "identity_sha256": text_sha256(item.get("identity", "")),
                "class": item.get("class"),
                "blocking": item.get("blocking"),
                "reason_sha256": text_sha256(item.get("reason", "")),
            }
            for item in blockers
            if isinstance(item, dict)
        ]
        if isinstance(blockers, list)
        else []
    )
    for field in ("open_gates", "evidence"):
        items = value.get(field, [])
        receipt[f"{field}_count"] = len(items) if isinstance(items, list) else 0
        receipt[f"{field}_sha256"] = canonical_sha256(items)
    receipt["reason_sha256"] = text_sha256(value.get("reason", ""))
    receipt["recovery_state"] = sanitized_recovery_receipt(value.get("recovery_state"))
    return receipt


def sanitized_compaction_phase(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    return {
        "phase_sha256": canonical_sha256(value),
        "rollout_path_sha256": text_sha256(value.get("rollout_path", "")),
        "rollout_sha256": value.get("rollout_sha256"),
        "compaction_event_count": value.get("compaction_event_count"),
        "context_compacted_marker_count": value.get("context_compacted_marker_count"),
        "event_types": value.get("event_types", []),
        "rollout_match_count": value.get("rollout_match_count"),
    }


def sanitized_native_compaction_receipt(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    receipt = {
        "native_compaction_sha256": canonical_sha256(value),
        "auto_compact_token_limit": value.get("auto_compact_token_limit"),
        "compaction_event_count": value.get("compaction_event_count"),
        "resumed_same_thread": value.get("resumed_same_thread"),
        "before_resume": sanitized_compaction_phase(value.get("before_resume")),
        "after_resume": sanitized_compaction_phase(value.get("after_resume")),
    }
    if "post_compaction_transition" in value:
        receipt["post_compaction_transition_sha256"] = canonical_sha256(
            value["post_compaction_transition"]
        )
    fresh = value.get("fresh_control")
    if isinstance(fresh, dict):
        receipt["fresh_control"] = {
            "fresh_control_sha256": canonical_sha256(fresh),
            "thread_id_sha256": text_sha256(fresh.get("thread_id", "")),
            "distinct_from_resumed_task": fresh.get("distinct_from_resumed_task"),
            "no_resume_handle": fresh.get("no_resume_handle"),
            "no_conversation_summary": fresh.get("no_conversation_summary"),
            "prompt_sha256": fresh.get("prompt_sha256"),
            "equivalent_gate_fields": fresh.get("equivalent_gate_fields", []),
            "allowed_label_differences_sha256": canonical_sha256(
                fresh.get("allowed_label_differences", {})
            ),
        }
    return receipt


def sanitized_case_receipt(
    result: dict[str, Any], *, metadata_sha256: str
) -> dict[str, Any]:
    installation = result.get("installation", {})
    safe_installation = {
        key: installation.get(key)
        for key in (
            "source_skill_sha256",
            "installed_skill_sha256",
            "source_package_manifest_sha256",
            "installed_package_manifest_sha256",
        )
    }
    plugin = installation.get("plugin", {})
    if plugin:
        safe_installation["plugin_sha256"] = canonical_sha256(plugin)
    receipt = {
        "schema_version": 1,
        "engine_generation": "0.4",
        "id": result["case"],
        "metadata_sha256": metadata_sha256,
        "installation": safe_installation,
        **{
            key: result.get(key)
            for key in (
                "model",
                "effort",
                "timeout_seconds",
                "timed_out",
                "elapsed_seconds",
                "exit_code",
                "semantic_input_sha256",
                "identities",
                "events_sha256",
                "stderr_sha256",
                "usage",
                "usage_phases",
                "uncached_input_tokens",
                "passed",
            )
        },
        "result": sanitized_result_receipt(result.get("result")),
        "fresh_recovery_result": sanitized_result_receipt(
            result.get("fresh_recovery_result")
        ),
        "oracle_failures": {
            "count": len(result.get("oracle_failures", [])),
            "sha256": canonical_sha256(result.get("oracle_failures", [])),
        },
        "native_compaction": sanitized_native_compaction_receipt(
            result.get("native_compaction")
        ),
    }
    for field in ("thread_id", "resume_thread_id", "fresh_recovery_thread_id"):
        receipt[f"{field}_sha256"] = text_sha256(result.get(field, ""))
    isolation = result.get("filesystem_isolation", {})
    receipt["filesystem_isolation"] = {
        key: isolation.get(key)
        for key in (
            "mechanism",
            "profile",
            "default_access",
            "workspace",
            "nonworkspace",
            "native_tools",
            "network",
            "selection",
        )
    }
    receipt["filesystem_isolation"]["policy_sha256"] = canonical_sha256(isolation)
    return receipt


def load_ledger(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("certification ledger must be an object")
    validate_ledger(value)
    return value


def ledger_sha256(ledger: dict[str, Any]) -> str:
    validate_ledger(ledger)
    return sha256_bytes(canonical_json_bytes(ledger))


def write_new_json(path: Path, value: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode()
    with path.open("xb") as output:
        output.write(encoded)
        output.flush()
        os.fsync(output.fileno())
    return sha256_bytes(encoded)
