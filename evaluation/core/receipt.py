from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any

from evaluation.core.identity import (
    canonical_sha256,
    recovery_manifest_projection,
    recovery_summary_consistent,
    sha256_bytes,
)
from evaluation.semantic import (
    parse_model_observation,
    parse_report,
    report_to_raw,
)


def text_sha256(value: Any) -> str:
    return sha256_bytes(str(value).encode())


def canonical_members_sha256(value: Any) -> str:
    members = value if isinstance(value, list) else []
    return canonical_sha256(
        sorted(
            members,
            key=lambda item: json.dumps(
                item,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
    )


def sanitized_recovery_receipt(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    commits = {}
    for field in (
        "baseline_revision",
        "baseline_tree",
        "current_revision",
        "current_tree",
    ):
        item = value.get(field)
        commits[field] = (
            item if type(item) is str and re.fullmatch(r"[0-9a-f]{40}", item) else None
        )
    tests = value.get("tests", {})
    agents = value.get("live_agents", [])
    markers = value.get("marker_ids", [])
    return {
        "recovery_state_sha256": canonical_sha256(value),
        **commits,
        **{
            field: value.get(field)
            for field in ("writer", "milestone_phase", "next_action", "worktree")
        },
        "pending_gates": value.get("pending_gates", []),
        "tests_sha256": canonical_sha256(tests),
        "live_agents_sha256": canonical_sha256(agents),
        "marker_ids_count": len(markers) if isinstance(markers, list) else 0,
        "marker_ids_sha256": canonical_members_sha256(markers),
        **recovery_manifest_projection(value),
        "summary_consistent": recovery_summary_consistent(value),
    }


def sanitized_result_receipt(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        return {"result_sha256": canonical_sha256(value)}
    observation = parse_model_observation(value)
    findings = value["findings"]
    open_gates = value.get("open_gates", [])
    evidence = value.get("evidence", [])
    return {
        "result_sha256": canonical_sha256(value),
        "qualifies": observation.qualifies,
        "execplan_condition": observation.execplan_condition,
        "findings": [
            {
                "id_sha256": text_sha256(item.get("id", "")),
                "domain": item.get("domain"),
                "status": item.get("status"),
                "anchors_sha256": canonical_members_sha256(item.get("anchors", [])),
                "blocker": (
                    None
                    if item.get("blocker") is None
                    else {
                        "class": item["blocker"].get("class"),
                        "reason_sha256": text_sha256(
                            item["blocker"].get("reason", "")
                        ),
                    }
                ),
            }
            for item in findings
            if isinstance(item, dict)
        ],
        "open_gates_count": len(open_gates) if isinstance(open_gates, list) else 0,
        "open_gates_sha256": canonical_members_sha256(open_gates),
        "goal_pause_handoff_present": (
            isinstance(open_gates, list) and "user_selection" in open_gates
        ),
        "evidence_count": len(evidence) if isinstance(evidence, list) else 0,
        "evidence_sha256": canonical_members_sha256(evidence),
        "reason_sha256": text_sha256(value.get("reason", "")),
        "recovery": sanitized_recovery_receipt(value.get("recovery")),
    }


def sanitized_report_receipt(value: Any) -> dict[str, Any]:
    report = parse_report(value)
    raw = report_to_raw(report)
    return {
        "schema_generation": 7,
        "report_sha256": canonical_sha256(raw),
        "task_binding_sha256": canonical_sha256(raw["facts"]["task_binding"]),
        "accepted_baseline_sha256": canonical_members_sha256(
            raw["facts"]["accepted_baseline_failures"]
        ),
        "infrastructure_generation": raw["facts"][
            "infrastructure_generation"
        ],
        "state_key": report.state_key,
        "action_key": report.action_key,
        "next_action": raw["next_action"],
        "findings_sha256": canonical_sha256(raw["findings"]),
        "blockers_sha256": canonical_sha256(raw["blockers"]),
        "observation": sanitized_result_receipt(raw["observation"]),
    }


def sanitized_compaction_phase(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    return {
        "phase_sha256": canonical_sha256(value),
        "rollout_path_sha256": text_sha256(value.get("rollout_path", "")),
        **{
            field: value.get(field)
            for field in (
                "rollout_sha256",
                "rollout_byte_count",
                "rollout_prefix_sha256",
                "compaction_event_count",
                "context_compacted_marker_count",
                "event_types",
                "rollout_match_count",
            )
        },
    }


def sanitized_native_compaction_receipt(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    fresh = value.get("fresh_control")
    return {
        "native_compaction_sha256": canonical_sha256(value),
        "auto_compact_token_limit": value.get("auto_compact_token_limit"),
        "compaction_event_count": value.get("compaction_event_count"),
        "resumed_same_thread": value.get("resumed_same_thread"),
        "before_resume": sanitized_compaction_phase(value.get("before_resume")),
        "after_resume": sanitized_compaction_phase(value.get("after_resume")),
        "fresh_control_sha256": (
            canonical_sha256(fresh) if isinstance(fresh, dict) else None
        ),
    }


def _validated_report(
    value: Any,
    *,
    raw: Any,
    profile: Any,
    accepted: Any,
) -> dict[str, Any]:
    report = parse_report(value)
    if report.observation != parse_model_observation(raw):
        raise ValueError("canonical report does not bind raw observation")
    if (
        report.facts.task_binding["invocation_profile_digest"]
        != canonical_sha256(profile)
        or list(report.facts.accepted_baseline_failures) != accepted
    ):
        raise ValueError("canonical report context binding mismatch")
    return report_to_raw(report)


def sanitized_case_receipt(
    result: dict[str, Any], *, metadata_sha256: str
) -> dict[str, Any]:
    profile = result.get("invocation_profile")
    accepted = result.get("accepted_baseline_failures", [])
    report = _validated_report(
        result.get("canonical_report"),
        raw=result.get("result"),
        profile=profile,
        accepted=accepted,
    )
    fresh_raw = result.get("fresh_recovery_result")
    fresh = result.get("fresh_recovery_canonical_report")
    if fresh_raw is not None:
        fresh = _validated_report(
            fresh, raw=fresh_raw, profile=profile, accepted=accepted
        )
    elif fresh is not None:
        raise ValueError("unexpected fresh recovery projection")
    installation = result.get("installation", {})
    return {
        "schema_version": 1,
        "engine_generation": "0.6.5",
        "id": result["case"],
        "metadata_sha256": metadata_sha256,
        "installation": {
            key: installation.get(key)
            for key in (
                "source_skill_sha256",
                "installed_skill_sha256",
                "source_package_manifest_sha256",
                "installed_package_manifest_sha256",
            )
        },
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
                "invocation_profile",
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
        "canonical_report": sanitized_report_receipt(report),
        "fresh_recovery_result": sanitized_result_receipt(fresh_raw),
        "fresh_recovery_canonical_report": (
            sanitized_report_receipt(fresh) if fresh is not None else None
        ),
        "terminal_projections": result.get("terminal_projections", []),
        "oracle_failures_sha256": canonical_sha256(result.get("oracle_failures", [])),
        "native_compaction": sanitized_native_compaction_receipt(
            result.get("native_compaction")
        ),
        "thread_id_sha256": text_sha256(result.get("thread_id", "")),
        "resume_thread_id_sha256": text_sha256(
            result.get("resume_thread_id", "")
        ),
        "fresh_recovery_thread_id_sha256": text_sha256(
            result.get("fresh_recovery_thread_id", "")
        ),
        "filesystem_isolation": result.get("filesystem_isolation"),
    }


def write_new_json(path: Path, payload: Any) -> str:
    data = (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2).encode()
        + b"\n"
    )
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, data)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return sha256_bytes(data)
