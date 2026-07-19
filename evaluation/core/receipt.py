from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any

from evaluation.core.identity import canonical_sha256, sha256_bytes
from evaluation.corpus.contract import PERMISSION_FIELDS


def text_sha256(value: Any) -> str:
    return sha256_bytes(str(value).encode())


def casefold_text_sha256(value: Any) -> str:
    return sha256_bytes(str(value).casefold().encode())


def identity_match_sha256s(value: Any) -> list[str]:
    folded = str(value).casefold()
    candidates = {folded}
    candidates.update(
        folded[index + 1 :]
        for index, character in enumerate(folded)
        if character in {":", "/"} and folded[index + 1 :]
    )
    return sorted(casefold_text_sha256(candidate) for candidate in candidates)


def member_sha256s(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({casefold_text_sha256(item) for item in value})


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
                "identity_casefold_sha256": casefold_text_sha256(
                    item.get("identity", "")
                ),
                "identity_match_sha256s": identity_match_sha256s(
                    item.get("identity", "")
                ),
                "domain": item.get("domain"),
                "state": item.get("state"),
                "anchors_count": len(item.get("anchors", []))
                if isinstance(item.get("anchors", []), list)
                else 0,
                "anchors_sha256": canonical_sha256(item.get("anchors", [])),
                "anchor_sha256s": member_sha256s(item.get("anchors", [])),
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
                "identity_casefold_sha256": casefold_text_sha256(
                    item.get("identity", "")
                ),
                "identity_match_sha256s": identity_match_sha256s(
                    item.get("identity", "")
                ),
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
    open_gates = value.get("open_gates", [])
    receipt["goal_pause_handoff_present"] = isinstance(open_gates, list) and any(
        isinstance(gate, str) and "/goal pause" in gate for gate in open_gates
    )
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
        "rollout_byte_count": value.get("rollout_byte_count"),
        "rollout_prefix_sha256": value.get("rollout_prefix_sha256"),
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
