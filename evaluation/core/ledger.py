from __future__ import annotations

import json
import math
from pathlib import Path
import re
from typing import Any

from evaluation.core.identity import (
    BLOCKER_CLASSES,
    CONVERGENCE_PHASES,
    FILESYSTEM_ISOLATION_POLICY,
    PERMISSION_FIELDS,
    RECOVERY_ACTIONS,
    RECOVERY_GATE_FIELDS,
    RECOVERY_PENDING_GATES,
    canonical_sha256,
    case_semantic_sha256,
    classification_identity_failures,
    classifications_share_identity,
    sha256_bytes,
    validate_invocation_profile,
)
from evaluation.core.impact import (
    impact_token,
    validate_impact,
    validate_snapshot,
)
from evaluation.holdout.blind import completed_quality
from evaluation.holdout.compare import (
    adaptive_next,
    aggregate_quality,
    cost_gate,
    sum_metrics,
)
from evaluation.semantic import SemanticError, make_attempt_key, replay_report


LEDGER_FIELDS = {
    "schema_version",
    "engine_generation",
    "state",
    "snapshot",
    "pending",
    "authorities",
    "calibration_history",
    "accepted_evidence",
    "receipt_head",
    "certification",
}
PENDING_FIELDS = {"gates", "corpus_cases", "holdout_pairs"}
PENDING_GATES = (
    "corpus",
    "executor_pilot",
    "holdout",
    "isolated_install",
    "receipt",
    "review",
)
AUTHORITY_SLOTS = {"executor", "corpus", "holdout"}
COVERAGE_FIELDS = {"corpus", "holdout"}
CORPUS_SUMMARY_FIELDS = {
    "schema_version",
    "engine_generation",
    "impact_token",
    "gate_authority_sha256",
    "arm",
    "model",
    "effort",
    "timeout_seconds",
    "passed",
    "total",
    "uncached_input_tokens",
    "telemetry_complete",
    "output_tokens",
    "elapsed_seconds",
    "cases",
}
CASE_RECEIPT_FIELDS = {
    "schema_version",
    "engine_generation",
    "id",
    "metadata_sha256",
    "installation",
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
    "result",
    "semantic_result",
    "fresh_recovery_result",
    "fresh_recovery_semantic_result",
    "terminal_projections",
    "oracle_failures",
    "native_compaction",
    "thread_id_sha256",
    "resume_thread_id_sha256",
    "fresh_recovery_thread_id_sha256",
    "filesystem_isolation",
}
HOLDOUT_RUN_FIELDS = {
    "schema_version",
    "engine_generation",
    "impact_token",
    "gate_authority_sha256",
    "manifest_sha256",
    "identities",
    "model",
    "effort",
    "timeout_seconds",
    "pair_ids",
    "case_sha256",
}
PAIR_RECEIPT_FIELDS = {
    "schema_version",
    "engine_generation",
    "id",
    "case_id",
    "case_sha256",
    "outside_diff_boundary",
    "oracle_kind",
    "mapping_commitment_file_sha256",
    "pre_reveal_decision_file_sha256",
    "mapping_reveal_file_sha256",
    "pre_reveal_decision_sha256",
    "mapping_commitment_sha256",
    "outcome",
    "metrics",
    "arms",
}
HOLDOUT_SUMMARY_FIELDS = {
    "schema_version",
    "engine_generation",
    "run_receipt_sha256",
    "adaptive_history",
    "adaptive_terminal_action",
    "pairs_run",
    "pair_receipts",
    "cost_gate",
}
OFFLINE_GATES = frozenset({"receipt", "isolated_install"})
OFFLINE_SUMMARY_FIELDS = {
    "schema_version",
    "engine_generation",
    "source_commit",
    "source_ledger_sha256",
    "snapshot_sha256",
    "engine_manifest_sha256",
    "gates",
    "receipt_artifact_sha256",
    "isolated_installation",
}

INSTALLATION_RECEIPT_FIELDS = {
    "source_skill_sha256",
    "installed_skill_sha256",
    "source_package_manifest_sha256",
    "installed_package_manifest_sha256",
    "plugin_sha256",
}
FILESYSTEM_RECEIPT_FIELDS = {
    "mechanism",
    "profile",
    "default_access",
    "workspace",
    "nonworkspace",
    "native_tools",
    "network",
    "selection",
    "policy_sha256",
}
RESULT_RECEIPT_FIELDS = {
    "result_sha256",
    *PERMISSION_FIELDS,
    "finding_classifications",
    "blocker_classifications",
    "open_gates_count",
    "open_gates_sha256",
    "goal_pause_handoff_present",
    "evidence_count",
    "evidence_sha256",
    "reason_sha256",
    "recovery_state",
}
FINDING_RECEIPT_FIELDS = {
    "identity_sha256",
    "identity_nonblank",
    "domain",
    "state",
    "anchors_count",
    "anchors_sha256",
    "anchor_sha256s",
}
BLOCKER_RECEIPT_FIELDS = {
    "identity_sha256",
    "identity_nonblank",
    "class",
    "blocking",
    "reason_sha256",
}
TERMINAL_PROJECTION_FIELDS = {
    "provenance",
    "provider",
    "session_id",
    "thread_id",
    "turn_id",
    "action_id",
    "attempt_key",
    "result_id",
    "result_sha256",
    "stream_sha256",
    "terminal_ordinal",
}
RECOVERY_RECEIPT_FIELDS = {
    "recovery_state_sha256",
    "baseline_revision",
    "baseline_tree",
    "current_revision",
    "current_tree",
    "writer",
    "milestone_phase",
    "next_action",
    "pending_gates",
    "tests",
    "worktree",
    "live_agents",
    "marker_ids_count",
    "marker_ids_sha256",
    "recovery_manifest_count",
    "recovery_manifest_sha256",
    "summary_consistent",
}
RECOVERY_TEST_FIELDS = {
    "passed",
    "failed",
    "accepted_failures",
    "marker_ids_count",
    "marker_ids_sha256",
}
RECOVERY_AGENT_FIELDS = {"id_sha256", "status", "receipt_reproduced"}
COMPACTION_PHASE_FIELDS = {
    "phase_sha256",
    "rollout_path_sha256",
    "rollout_sha256",
    "rollout_byte_count",
    "rollout_prefix_sha256",
    "compaction_event_count",
    "context_compacted_marker_count",
    "event_types",
    "rollout_match_count",
}
NATIVE_COMPACTION_FIELDS = {
    "native_compaction_sha256",
    "auto_compact_token_limit",
    "compaction_event_count",
    "resumed_same_thread",
    "before_resume",
    "after_resume",
    "post_compaction_transition_sha256",
    "fresh_control",
}
FRESH_CONTROL_FIELDS = {
    "fresh_control_sha256",
    "thread_id_sha256",
    "distinct_from_resumed_task",
    "no_resume_handle",
    "no_conversation_summary",
    "prompt_sha256",
    "equivalent_gate_fields",
    "allowed_label_differences_sha256",
}
RECOVERY_WRITERS = {"Root", "unknown"}
RECOVERY_PHASES = set(CONVERGENCE_PHASES)
RECOVERY_WORKTREE_STATES = {"clean", "dirty", "unknown"}
RECOVERY_AGENT_STATES = {"pending", "terminal", "missing"}
COMPACTION_EVENT_TYPES = {"compacted", "context_compacted"}


def _require_digest(value: Any, *, length: int, label: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(rf"[0-9a-f]{{{length}}}", value):
        raise ValueError(f"invalid {label}")


def _validate_coverage(
    coverage: Any,
    *,
    snapshot: dict[str, Any],
    impact: dict[str, Any],
    corpus_holdout_waived: bool,
) -> set[str]:
    if not isinstance(coverage, dict) or set(coverage) != COVERAGE_FIELDS:
        raise ValueError("invalid certification coverage manifest")
    refreshed: dict[str, set[str]] = {}
    required_disposition = "waived" if corpus_holdout_waived else "refreshed"
    for label, available in (
        ("corpus", set(snapshot["corpus"]["cases"])),
        ("holdout", set(snapshot["holdout"]["pairs"])),
    ):
        values = coverage.get(label)
        if (
            not isinstance(values, dict)
            or set(values) != available
            or any(value != required_disposition for value in values.values())
        ):
            raise ValueError(f"invalid certification {label} coverage")
        refreshed[label] = {
            name for name, disposition in values.items() if disposition == "refreshed"
        }
    if refreshed["corpus"] != set(impact["corpus_cases"]):
        raise ValueError("certification corpus coverage does not match impact")
    if refreshed["holdout"] != set(impact["holdout_pairs"]):
        raise ValueError("certification holdout coverage does not match impact")
    evidence_fields: set[str] = set()
    if refreshed["corpus"]:
        evidence_fields.add("corpus_summary")
    if refreshed["holdout"]:
        evidence_fields.update({"holdout_run", "holdout_summary"})
    return evidence_fields


def _offline_gates(impact: dict[str, Any]) -> set[str]:
    return set(impact["gates"]) & OFFLINE_GATES


def _validate_offline_summary(
    payload: Any,
    *,
    snapshot: dict[str, Any],
    source_commit: str,
    source_ledger_sha256: str,
    gates: set[str],
) -> None:
    if not isinstance(payload, dict) or set(payload) != OFFLINE_SUMMARY_FIELDS:
        raise ValueError("invalid offline certification evidence")
    expected_gates = sorted(gates)
    if (
        not gates
        or not gates.issubset(OFFLINE_GATES)
        or payload.get("schema_version") != 1
        or payload.get("engine_generation") != "0.6"
        or payload.get("source_commit") != source_commit
        or payload.get("source_ledger_sha256") != source_ledger_sha256
        or payload.get("snapshot_sha256") != canonical_sha256(snapshot)
        or payload.get("engine_manifest_sha256")
        != snapshot["engine"]["manifest_sha256"]
        or payload.get("gates") != expected_gates
    ):
        raise ValueError("offline certification evidence identity mismatch")
    expected_receipt = (
        snapshot["engine"]["categories"]["artifact"] if "receipt" in gates else None
    )
    if payload.get("receipt_artifact_sha256") != expected_receipt:
        raise ValueError("offline receipt evidence mismatch")
    installation = payload.get("isolated_installation")
    if "isolated_install" in gates:
        _validate_installation_receipt(
            installation,
            package=snapshot["package"],
            case_id="offline certification",
        )
    elif installation is not None:
        raise ValueError("unexpected offline installation evidence")


def _nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _identity_sha256(value: Any) -> str:
    return sha256_bytes(str(value).encode())


def _validate_digest_list(value: Any, *, label: str, required: bool) -> None:
    if (
        not isinstance(value, list)
        or (required and not value)
        or value != sorted(set(value))
    ):
        raise ValueError(f"invalid {label} digest list")
    for item in value:
        _require_digest(item, length=64, label=label)


def _matches_canonical_list_digest(value: Any, expected: list[Any]) -> bool:
    return value == canonical_sha256(sorted(expected))


def _validate_recovery_oracle_receipt(
    value: dict[str, Any], *, oracle: dict[str, Any], label: str
) -> None:
    for field in (
        "baseline_revision",
        "baseline_tree",
        "current_revision",
        "current_tree",
    ):
        if field in oracle and value[field] != oracle[field]:
            raise ValueError(f"invalid {label} recovery oracle receipt: {field}")
    for field in (
        "writer",
        "milestone_phase",
        "next_action",
        "pending_gates",
        "worktree",
    ):
        if value[field] != oracle[field]:
            raise ValueError(f"invalid {label} recovery oracle receipt: {field}")
    tests = value["tests"]
    expected_tests = oracle["tests"]
    for field in ("passed", "failed", "accepted_failures"):
        if tests[field] != expected_tests[field]:
            raise ValueError(f"invalid {label} recovery oracle tests: {field}")
    expected_test_markers = expected_tests["marker_ids"]
    if tests["marker_ids_count"] != len(
        expected_test_markers
    ) or not _matches_canonical_list_digest(
        tests["marker_ids_sha256"], expected_test_markers
    ):
        raise ValueError(f"invalid {label} recovery oracle test markers")
    expected_agents = [
        {
            "id_sha256": sha256_bytes(str(agent["id"]).encode()),
            "status": agent["status"],
            "receipt_reproduced": agent["receipt_reproduced"],
        }
        for agent in oracle["live_agents"]
    ]
    if sorted(value["live_agents"], key=canonical_sha256) != sorted(
        expected_agents, key=canonical_sha256
    ):
        raise ValueError(f"invalid {label} recovery oracle agents")
    expected_markers = oracle["marker_ids"]
    if value["marker_ids_count"] != len(
        expected_markers
    ) or not _matches_canonical_list_digest(
        value["marker_ids_sha256"], expected_markers
    ):
        raise ValueError(f"invalid {label} recovery oracle markers")


def _validate_case_oracle_receipt(
    value: dict[str, Any], *, case: dict[str, Any], label: str
) -> None:
    oracle = case["oracle"]
    findings = value["finding_classifications"]
    blockers = value["blocker_classifications"]
    from evaluation.corpus.engine import fixture_requires_goal_pause_handoff

    if (
        fixture_requires_goal_pause_handoff(case["fixture"])
        and value["decision"] == "stop_for_user"
        and value["goal_pause_handoff_present"] is not True
    ):
        raise ValueError(f"missing {label} oracle Goal-pause handoff receipt")
    for required in oracle.get("required_classifications", []):
        states = required["state"]
        allowed_states = states if isinstance(states, list) else [states]
        identity = _identity_sha256(required["identity"])
        if not any(
            identity == finding["identity_sha256"]
            and finding["domain"] == required["domain"]
            and finding["state"] in allowed_states
            for finding in findings
        ):
            raise ValueError(f"missing {label} oracle classification receipt")
    for required_class in oracle.get("required_blocker_classes", []):
        if not any(
            blocker["class"] == required_class and blocker["blocking"] is True
            for blocker in blockers
        ):
            raise ValueError(f"missing {label} oracle blocker-class receipt")
    for required in oracle.get("required_blocker_classifications", []):
        identity = _identity_sha256(required["identity"])
        if not any(
            identity == blocker["identity_sha256"]
            and blocker["class"] == required["class"]
            and blocker["blocking"] is True
            for blocker in blockers
        ):
            raise ValueError(f"missing {label} oracle blocker receipt")
    anchored_blocker_matches: list[list[frozenset[str]]] = []
    for required in oracle.get("required_anchored_blockers", []):
        anchor = _identity_sha256(required["anchor"])
        classes = required["class"]
        allowed_classes = classes if isinstance(classes, list) else [classes]
        anchored = [
            finding for finding in findings if anchor in finding["anchor_sha256s"]
        ]
        matches = [
            frozenset({finding["identity_sha256"]})
            for finding in anchored
            for blocker in blockers
            if classifications_share_identity(finding, blocker)
            and blocker["class"] in allowed_classes
            and blocker["blocking"] is True
        ]
        anchored_blocker_matches.append(matches)
        if not matches:
            raise ValueError(f"missing {label} oracle anchored blocker receipt")
    if anchored_blocker_matches and (
        any(len(matches) != 1 for matches in anchored_blocker_matches)
        or len({next(iter(matches[0])) for matches in anchored_blocker_matches})
        != len(anchored_blocker_matches)
    ):
        raise ValueError(f"distinct anchored blocker receipt required for {label}")
    anchored_classification_matches: list[list[frozenset[str]]] = []
    for required in oracle.get("required_anchored_classifications", []):
        anchor = _identity_sha256(required["anchor"])
        states = required["state"]
        allowed_states = states if isinstance(states, list) else [states]
        matches = [
            frozenset({finding["identity_sha256"]})
            for finding in findings
            if anchor in finding["anchor_sha256s"]
            and finding["domain"] == required["domain"]
            and finding["state"] in allowed_states
        ]
        anchored_classification_matches.append(matches)
        if not matches:
            raise ValueError(f"missing {label} oracle anchored classification receipt")
    if anchored_classification_matches and (
        any(len(matches) != 1 for matches in anchored_classification_matches)
        or len({next(iter(matches[0])) for matches in anchored_classification_matches})
        != len(anchored_classification_matches)
    ):
        raise ValueError(
            f"distinct anchored classification receipt required for {label}"
        )
    if value["decision"] == "complete" or value["protocol_may_complete"] is True:
        accepted = [
            (identity, _identity_sha256(identity))
            for identity in oracle.get("accepted_baseline_failures", [])
        ]
        for finding in findings:
            if (
                finding["domain"] == "baseline_failure"
                and finding["state"] == "baseline_unchanged"
                and sum(
                    identity_sha256 == finding["identity_sha256"]
                    for _, identity_sha256 in accepted
                )
                != 1
            ):
                raise ValueError(
                    f"invalid {label} accepted baseline classification receipt"
                )


SEMANTIC_RESULT_PROJECTION_FIELDS = {
    "schema_generation",
    "raw_result_sha256",
    "invocation_profile_sha256",
    "accepted_baseline_sha256",
    "report",
    "attempt_key",
}


def _validate_semantic_result_projection(
    value: Any,
    *,
    raw_result: dict[str, Any] | None = None,
    raw_result_sha256: str | None = None,
    invocation_profile: dict[str, Any],
    accepted_baseline_failures: list[str],
) -> dict[str, Any]:
    if (
        not isinstance(value, dict)
        or set(value) != SEMANTIC_RESULT_PROJECTION_FIELDS
        or value.get("schema_generation") != 6
    ):
        raise ValueError("invalid generation-6 result projection")
    expected_raw_sha256 = (
        canonical_sha256(raw_result)
        if raw_result is not None
        else raw_result_sha256
    )
    if value.get("raw_result_sha256") != expected_raw_sha256:
        raise ValueError("semantic projection raw result mismatch")
    if value.get("invocation_profile_sha256") != canonical_sha256(
        invocation_profile
    ):
        raise ValueError("semantic projection invocation_profile mismatch")
    if value.get("accepted_baseline_sha256") != canonical_sha256(
        accepted_baseline_failures
    ):
        raise ValueError("semantic projection accepted baseline mismatch")
    try:
        report = replay_report(value.get("report"))
        attempt_key = make_attempt_key(report).value
    except SemanticError as error:
        raise ValueError(str(error)) from error
    if value.get("attempt_key") != attempt_key:
        raise ValueError("semantic projection AttemptKey mismatch")

    if raw_result is not None:
        report_wire = report.to_wire()
        binding = report_wire["facts"]["task_binding"]
        from evaluation.corpus.engine import semantic_result_projection

        expected = semantic_result_projection(
            raw_result,
            context={
                **binding,
                "invocation_profile": invocation_profile,
                "accepted_baseline_failures": accepted_baseline_failures,
            },
        )
        if value != expected:
            raise ValueError("semantic projection does not match raw result")
    return value


def _validate_terminal_projections(
    value: Any,
    *,
    invocation_profile: dict[str, Any],
    result_sha256: str,
    fresh_result_sha256: str | None,
    native: bool,
) -> None:
    expected_count = 3 if native else 1
    if not isinstance(value, list) or len(value) != expected_count:
        raise ValueError("invalid terminal projection count")
    for projection in value:
        if (
            not isinstance(projection, dict)
            or set(projection) != TERMINAL_PROJECTION_FIELDS
            or projection.get("provenance")
            != "validated_invocation+native_stream"
            or projection.get("provider") != invocation_profile["provider"]
            or any(
                type(projection.get(field)) is not str or not projection[field]
                for field in (
                    "session_id",
                    "thread_id",
                    "turn_id",
                    "action_id",
                    "attempt_key",
                    "result_id",
                    "result_sha256",
                    "stream_sha256",
                )
            )
            or type(projection.get("terminal_ordinal")) is not int
            or projection["terminal_ordinal"] < 2
        ):
            raise ValueError("invalid terminal projection")
        for field in (
            "session_id",
            "turn_id",
            "attempt_key",
            "result_sha256",
            "stream_sha256",
        ):
            _require_digest(
                projection[field], length=64, label=f"terminal projection {field}"
            )
    if len({item["action_id"] for item in value}) != expected_count:
        raise ValueError("terminal action identities are not exact-unique")
    if len({item["turn_id"] for item in value}) != expected_count:
        raise ValueError("terminal turn identities are not exact-unique")
    if not native:
        if value[0]["result_sha256"] != result_sha256:
            raise ValueError("terminal result binding mismatch")
        return
    if (
        value[0]["session_id"] != value[1]["session_id"]
        or value[0]["thread_id"] != value[1]["thread_id"]
        or value[2]["session_id"] == value[1]["session_id"]
        or value[2]["thread_id"] == value[1]["thread_id"]
        or value[1]["result_sha256"] != result_sha256
        or fresh_result_sha256 is None
        or value[2]["result_sha256"] != fresh_result_sha256
    ):
        raise ValueError("native terminal lineage binding mismatch")


def _validate_recovery_receipt(value: Any, *, label: str) -> None:
    if not isinstance(value, dict) or set(value) != RECOVERY_RECEIPT_FIELDS:
        raise ValueError(f"invalid {label} recovery receipt")
    _require_digest(
        value.get("recovery_state_sha256"), length=64, label=f"{label} recovery"
    )
    for field in (
        "baseline_revision",
        "baseline_tree",
        "current_revision",
        "current_tree",
    ):
        _require_digest(value.get(field), length=40, label=f"{label} recovery {field}")
    pending_gates = value.get("pending_gates")
    if (
        value.get("writer") not in RECOVERY_WRITERS
        or value.get("milestone_phase") not in RECOVERY_PHASES
        or value.get("next_action") not in RECOVERY_ACTIONS
        or value.get("worktree") not in RECOVERY_WORKTREE_STATES
        or not isinstance(pending_gates, list)
        or any(gate not in RECOVERY_PENDING_GATES for gate in pending_gates)
    ):
        raise ValueError(f"invalid {label} recovery receipt")
    tests = value.get("tests")
    if not isinstance(tests, dict) or set(tests) != RECOVERY_TEST_FIELDS:
        raise ValueError(f"invalid {label} recovery tests receipt")
    if any(
        not _nonnegative_int(tests.get(field))
        for field in ("passed", "failed", "accepted_failures", "marker_ids_count")
    ):
        raise ValueError(f"invalid {label} recovery tests receipt")
    _require_digest(
        tests.get("marker_ids_sha256"),
        length=64,
        label=f"{label} recovery test markers",
    )
    agents = value.get("live_agents")
    if not isinstance(agents, list):
        raise ValueError(f"invalid {label} recovery agents receipt")
    for agent in agents:
        if (
            not isinstance(agent, dict)
            or set(agent) != RECOVERY_AGENT_FIELDS
            or agent.get("status") not in RECOVERY_AGENT_STATES
            or not isinstance(agent.get("receipt_reproduced"), bool)
        ):
            raise ValueError(f"invalid {label} recovery agent receipt")
        _require_digest(
            agent.get("id_sha256"), length=64, label=f"{label} recovery agent"
        )
    if not _nonnegative_int(value.get("marker_ids_count")):
        raise ValueError(f"invalid {label} recovery marker receipt")
    _require_digest(
        value.get("marker_ids_sha256"),
        length=64,
        label=f"{label} recovery markers",
    )
    if (
        value.get("recovery_manifest_count") != 1
        or value.get("summary_consistent") is not True
    ):
        raise ValueError(f"invalid {label} Recovery Manifest receipt")
    _require_digest(
        value.get("recovery_manifest_sha256"),
        length=64,
        label=f"{label} Recovery Manifest",
    )


def _validate_result_receipt(
    value: Any,
    *,
    label: str,
    required: bool,
    recovery_required: bool | None,
    expected_permissions: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if value is None:
        if required:
            raise ValueError(f"missing {label} result receipt")
        return None
    if not isinstance(value, dict) or set(value) != RESULT_RECEIPT_FIELDS:
        raise ValueError(f"invalid {label} result receipt")
    for field in (
        "result_sha256",
        "open_gates_sha256",
        "evidence_sha256",
        "reason_sha256",
    ):
        _require_digest(value.get(field), length=64, label=f"{label} result {field}")
    if (
        value.get("decision")
        not in {"continue", "stop_for_user", "complete", "incomplete"}
        or not isinstance(value.get("qualifies"), bool)
        or value.get("execplan_condition")
        not in {"not_required", "missing", "usable", "needs_amendment"}
        or any(
            not isinstance(value.get(field), bool)
            for field in (
                "protocol_may_product_write",
                "protocol_may_complete",
            )
        )
        or value.get("protocol_review_mode")
        not in {"none", "focused_hardening", "exact_final"}
        or not _nonnegative_int(value.get("open_gates_count"))
        or not _nonnegative_int(value.get("evidence_count"))
        or not isinstance(value.get("goal_pause_handoff_present"), bool)
    ):
        raise ValueError(f"invalid {label} result receipt")
    findings = value.get("finding_classifications")
    blockers = value.get("blocker_classifications")
    if not isinstance(findings, list) or not isinstance(blockers, list):
        raise ValueError(f"invalid {label} result classifications")
    identity_failures = [
        *classification_identity_failures(findings, label="finding"),
        *classification_identity_failures(blockers, label="blocker"),
    ]
    if identity_failures:
        raise ValueError(f"invalid {label} " + "; ".join(identity_failures))
    for finding in findings:
        if (
            not isinstance(finding, dict)
            or set(finding) != FINDING_RECEIPT_FIELDS
            or finding.get("domain")
            not in {"secret", "baseline_failure", "receipt", "other"}
            or finding.get("state")
            not in {"baseline_unchanged", "resolved", "candidate_new", "unknown"}
            or not isinstance(finding.get("identity_nonblank"), bool)
            or not _nonnegative_int(finding.get("anchors_count"))
        ):
            raise ValueError(f"invalid {label} result finding receipt")
        for field in ("identity_sha256", "anchors_sha256"):
            _require_digest(
                finding.get(field), length=64, label=f"{label} finding {field}"
            )
        if finding["identity_nonblank"] is not True:
            raise ValueError(f"invalid {label} blank finding identity")
        _validate_digest_list(
            finding.get("anchor_sha256s"),
            label=f"{label} finding anchors",
            required=finding["anchors_count"] > 0,
        )
        if finding["anchors_count"] == 0 and finding["anchor_sha256s"]:
            raise ValueError(f"invalid {label} result finding anchors")
    for blocker in blockers:
        if (
            not isinstance(blocker, dict)
            or set(blocker) != BLOCKER_RECEIPT_FIELDS
            or blocker.get("class") not in BLOCKER_CLASSES
            or not isinstance(blocker.get("blocking"), bool)
            or not isinstance(blocker.get("identity_nonblank"), bool)
        ):
            raise ValueError(f"invalid {label} result blocker receipt")
        for field in ("identity_sha256", "reason_sha256"):
            _require_digest(
                blocker.get(field), length=64, label=f"{label} blocker {field}"
            )
        if blocker["identity_nonblank"] is not True:
            raise ValueError(f"invalid {label} blank blocker identity")
    if expected_permissions is not None:
        for field in PERMISSION_FIELDS:
            allowed = expected_permissions.get(field)
            allowed = allowed if isinstance(allowed, list) else [allowed]
            if value.get(field) not in allowed:
                raise ValueError(f"invalid {label} oracle permission receipt")
    recovery = value.get("recovery_state")
    if recovery_required is True:
        _validate_recovery_receipt(recovery, label=label)
    elif recovery_required is False:
        if recovery is not None:
            raise ValueError(f"unexpected {label} recovery receipt")
    elif recovery is not None:
        _validate_recovery_receipt(recovery, label=label)
    return value


def _validate_compaction_phase(value: Any, *, label: str) -> None:
    if not isinstance(value, dict) or set(value) != COMPACTION_PHASE_FIELDS:
        raise ValueError(f"invalid native compaction {label} receipt")
    for field in ("phase_sha256", "rollout_path_sha256", "rollout_sha256"):
        _require_digest(value.get(field), length=64, label=f"native {label} {field}")
    prefix_sha256 = value.get("rollout_prefix_sha256")
    if prefix_sha256 is not None:
        _require_digest(
            prefix_sha256,
            length=64,
            label=f"native {label} rollout_prefix_sha256",
        )
    event_types = value.get("event_types")
    if (
        any(
            not _nonnegative_int(value.get(field))
            for field in (
                "compaction_event_count",
                "context_compacted_marker_count",
                "rollout_byte_count",
                "rollout_match_count",
            )
        )
        or not isinstance(event_types, list)
        or any(event not in COMPACTION_EVENT_TYPES for event in event_types)
        or value["compaction_event_count"] != event_types.count("compacted")
        or value["context_compacted_marker_count"]
        != event_types.count("context_compacted")
        or value["rollout_match_count"] != 1
        or value["compaction_event_count"] < 1
    ):
        raise ValueError(f"invalid native compaction {label} receipt")


def _validate_native_compaction(
    value: Any,
    *,
    case: dict[str, Any],
    receipt: dict[str, Any],
    result: dict[str, Any] | None,
    fresh_result: dict[str, Any] | None,
    native_evidence_oracle: dict[str, Any] | None,
) -> None:
    native = case["fixture"].get("native_compaction_resume")
    if native is None:
        if value is not None:
            raise ValueError("unexpected native compaction receipt")
        return
    if not isinstance(value, dict) or set(value) != NATIVE_COMPACTION_FIELDS:
        raise ValueError("missing or invalid native compaction receipt")
    if not isinstance(native_evidence_oracle, dict) or set(native_evidence_oracle) != {
        "recovery_state",
        "post_compaction_transition_sha256",
    }:
        raise ValueError("missing native evidence oracle")
    for field in (
        "native_compaction_sha256",
        "post_compaction_transition_sha256",
    ):
        _require_digest(value.get(field), length=64, label=f"native {field}")
    if (
        value["post_compaction_transition_sha256"]
        != native_evidence_oracle["post_compaction_transition_sha256"]
    ):
        raise ValueError("invalid native post-compaction transition receipt")
    if (
        value.get("auto_compact_token_limit") != native["auto_compact_token_limit"]
        or not _nonnegative_int(value.get("compaction_event_count"))
        or value["compaction_event_count"] < 1
        or value.get("resumed_same_thread") is not True
    ):
        raise ValueError("invalid native compaction receipt")
    _validate_compaction_phase(value.get("before_resume"), label="before-resume")
    _validate_compaction_phase(value.get("after_resume"), label="after-resume")
    before = value["before_resume"]
    after = value["after_resume"]
    if (
        value["compaction_event_count"] != before["compaction_event_count"]
        or after["rollout_path_sha256"] != before["rollout_path_sha256"]
        or after["rollout_sha256"] == before["rollout_sha256"]
        or before["rollout_prefix_sha256"] is not None
        or after["rollout_prefix_sha256"] != before["rollout_sha256"]
        or after["rollout_byte_count"] <= before["rollout_byte_count"]
        or after["event_types"][: len(before["event_types"])] != before["event_types"]
    ):
        raise ValueError("invalid native compaction rollout relationship")
    fresh = value.get("fresh_control")
    if not isinstance(fresh, dict) or set(fresh) != FRESH_CONTROL_FIELDS:
        raise ValueError("missing or invalid native fresh-control receipt")
    for field in (
        "fresh_control_sha256",
        "thread_id_sha256",
        "prompt_sha256",
        "allowed_label_differences_sha256",
    ):
        _require_digest(value=fresh.get(field), length=64, label=f"native {field}")
    if (
        fresh.get("distinct_from_resumed_task") is not True
        or fresh.get("no_resume_handle") is not True
        or fresh.get("no_conversation_summary") is not True
        or fresh.get("equivalent_gate_fields")
        != [*sorted(RECOVERY_GATE_FIELDS), "recovery_state"]
    ):
        raise ValueError("invalid native fresh-control receipt")
    primary_thread = receipt["thread_id_sha256"]
    resume_thread = receipt["resume_thread_id_sha256"]
    fresh_thread = receipt["fresh_recovery_thread_id_sha256"]
    missing_thread = sha256_bytes(b"None")
    if (
        primary_thread == missing_thread
        or resume_thread != primary_thread
        or fresh_thread == missing_thread
        or fresh_thread == primary_thread
        or fresh["thread_id_sha256"] != fresh_thread
    ):
        raise ValueError("invalid native thread-control receipt")
    if (
        result is None
        or fresh_result is None
        or any(result[field] != fresh_result[field] for field in RECOVERY_GATE_FIELDS)
    ):
        raise ValueError("invalid native recovery-control receipt")
    allowed_differences = {
        field: [result[field], fresh_result[field]]
        for field in ("decision", "execplan_condition")
        if result[field] != fresh_result[field]
    }
    if fresh["allowed_label_differences_sha256"] != canonical_sha256(
        allowed_differences
    ):
        raise ValueError("invalid native recovery-control labels receipt")
    recovery = result["recovery_state"]
    fresh_recovery = fresh_result["recovery_state"]
    if not isinstance(recovery, dict) or not isinstance(fresh_recovery, dict):
        raise ValueError("invalid native recovery-control state receipt")
    recovery_oracle = native_evidence_oracle["recovery_state"]
    _validate_recovery_oracle_receipt(recovery, oracle=recovery_oracle, label="primary")
    _validate_recovery_oracle_receipt(
        fresh_recovery, oracle=recovery_oracle, label="fresh"
    )
    for field in (
        "baseline_revision",
        "baseline_tree",
        "current_revision",
        "current_tree",
    ):
        if recovery[field] != fresh_recovery[field]:
            raise ValueError(f"invalid native recovery-control state: {field}")


def _validate_installation_receipt(
    value: Any, *, package: dict[str, str], case_id: str
) -> None:
    if not isinstance(value, dict) or set(value) != INSTALLATION_RECEIPT_FIELDS:
        raise ValueError(f"invalid corpus evidence installation: {case_id}")
    for field in INSTALLATION_RECEIPT_FIELDS:
        _require_digest(value.get(field), length=64, label=f"case installation {field}")
    if (
        value["source_skill_sha256"] != value["installed_skill_sha256"]
        or value["source_package_manifest_sha256"] != package["artifact_sha256"]
        or value["installed_package_manifest_sha256"] != package["artifact_sha256"]
    ):
        raise ValueError(f"corpus evidence installation mismatch: {case_id}")


def _validate_isolation_receipt(value: Any, *, case_id: str) -> None:
    if not isinstance(value, dict) or set(value) != FILESYSTEM_RECEIPT_FIELDS:
        raise ValueError(f"invalid corpus evidence isolation: {case_id}")
    expected = {
        field: FILESYSTEM_ISOLATION_POLICY[field]
        for field in FILESYSTEM_RECEIPT_FIELDS - {"policy_sha256"}
    }
    if any(value.get(field) != expected[field] for field in expected):
        raise ValueError(f"corpus evidence isolation mismatch: {case_id}")
    expected_policy_sha256 = canonical_sha256(
        {
            **FILESYSTEM_ISOLATION_POLICY,
            "workspace_root": "<case-temp>/repo",
            "native_tool_root": "<case-temp>/bin",
        }
    )
    if value.get("policy_sha256") != expected_policy_sha256:
        raise ValueError(f"corpus evidence isolation policy mismatch: {case_id}")


def _validate_case_identity(
    receipt: Any,
    snapshot: dict[str, Any],
    case_id: str,
    *,
    case: dict[str, Any],
    native_evidence_oracle: dict[str, Any] | None,
    expected_passed: bool = True,
    semantic_sha256: str,
    package: dict[str, str],
    engine: dict[str, Any],
    expected_profile_arm: str = "candidate",
) -> None:
    settings = snapshot["settings"]
    if (
        not isinstance(receipt, dict)
        or set(receipt) != CASE_RECEIPT_FIELDS
        or receipt.get("schema_version") != 1
        or receipt.get("engine_generation") != "0.6"
        or receipt.get("id") != case_id
        or not isinstance(case, dict)
        or case.get("id") != case_id
    ):
        raise ValueError("invalid corpus evidence case")
    passed = receipt.get("passed")
    timed_out = receipt.get("timed_out")
    if (
        not isinstance(passed, bool)
        or not isinstance(timed_out, bool)
        or receipt.get("model") != settings["model"]
        or receipt.get("effort") != settings["effort"]
        or receipt.get("timeout_seconds") != settings["timeout_seconds"]
    ):
        raise ValueError(f"corpus evidence case did not pass: {case_id}")
    if receipt.get("semantic_input_sha256") != semantic_sha256:
        raise ValueError(f"corpus evidence semantic identity mismatch: {case_id}")
    profile = validate_invocation_profile(
        receipt.get("invocation_profile"),
        require_bound_binary=True,
    )
    if (
        profile["model"] != settings["model"]
        or profile["effort"] != settings["effort"]
        or profile["timeout_seconds"] != settings["timeout_seconds"]
        or profile["arm"] != expected_profile_arm
        or profile["binary"]["identity_sha256"]
        != canonical_sha256(settings["toolchain"]["codex"])
    ):
        raise ValueError(f"corpus evidence invocation profile mismatch: {case_id}")
    identities = receipt.get("identities")
    if not isinstance(identities, dict) or set(identities) != {
        "engine",
        "package",
        "toolchain",
    }:
        raise ValueError(f"corpus evidence identities missing: {case_id}")
    if identities.get("engine") != engine:
        raise ValueError(f"corpus evidence engine mismatch: {case_id}")
    if identities.get("package") != package:
        raise ValueError(f"corpus evidence package mismatch: {case_id}")
    if identities.get("toolchain") != snapshot["settings"]["toolchain"]:
        raise ValueError(f"corpus evidence toolchain mismatch: {case_id}")
    for field in (
        "metadata_sha256",
        "events_sha256",
        "stderr_sha256",
        "thread_id_sha256",
        "resume_thread_id_sha256",
        "fresh_recovery_thread_id_sha256",
    ):
        _require_digest(receipt.get(field), length=64, label=f"case {field}")
    _validate_installation_receipt(
        receipt.get("installation"), package=package, case_id=case_id
    )
    failures = receipt.get("oracle_failures")
    if expected_passed:
        if failures != {"count": 0, "sha256": canonical_sha256([])}:
            raise ValueError(f"corpus evidence oracle failed: {case_id}")
    elif (
        not isinstance(failures, dict)
        or set(failures) != {"count", "sha256"}
        or not isinstance(failures.get("count"), int)
        or isinstance(failures.get("count"), bool)
        or failures["count"] <= 0
        or failures.get("sha256") == canonical_sha256([])
    ):
        raise ValueError(f"invalid failed-arm oracle evidence: {case_id}")
    else:
        _require_digest(
            failures.get("sha256"), length=64, label="failed-arm oracle failures"
        )
    quality = completed_quality(
        passed=passed,
        timed_out=timed_out,
        exit_code=receipt.get("exit_code"),
        oracle_failures_count=failures["count"],
    )
    if (quality == "pass") is not expected_passed:
        raise ValueError(f"corpus evidence case outcome mismatch: {case_id}")
    elapsed = receipt.get("elapsed_seconds")
    uncached = receipt.get("uncached_input_tokens")
    usage = receipt.get("usage")
    phases = receipt.get("usage_phases")
    required_usage = {"input_tokens", "cached_input_tokens", "output_tokens"}
    native = case["fixture"].get("native_compaction_resume") is not None
    expected_phases = 3 if native else 1
    if (
        not isinstance(usage, dict)
        or not isinstance(phases, list)
        or len(phases) != expected_phases
        or any(
            not isinstance(phase, dict)
            or not required_usage.issubset(phase)
            or any(
                not isinstance(key, str)
                or not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
                for key, value in phase.items()
            )
            for phase in phases
        )
    ):
        raise ValueError(f"invalid corpus evidence telemetry: {case_id}")
    combined_usage = {
        key: sum(phase.get(key, 0) for phase in phases)
        for key in sorted({key for phase in phases for key in phase})
    }
    if (
        usage != combined_usage
        or usage["cached_input_tokens"] > usage["input_tokens"]
        or uncached != usage["input_tokens"] - usage["cached_input_tokens"]
    ):
        raise ValueError(f"invalid corpus evidence telemetry: {case_id}")
    expected_permissions = case["oracle"]["expected"] if expected_passed else None
    result_receipt = _validate_result_receipt(
        receipt.get("result"),
        label=f"case {case_id}",
        required=True,
        recovery_required=True if native and expected_passed else None,
        expected_permissions=expected_permissions,
    )
    if expected_passed:
        _validate_case_oracle_receipt(
            result_receipt, case=case, label=f"case {case_id}"
        )
    accepted_baseline = sorted(
        case["oracle"].get("accepted_baseline_failures", [])
    )
    semantic_result = _validate_semantic_result_projection(
        receipt.get("semantic_result"),
        raw_result_sha256=result_receipt["result_sha256"],
        invocation_profile=profile,
        accepted_baseline_failures=accepted_baseline,
    )
    if (
        semantic_result["report"]["facts"]["task_binding"]["lineage_digest"]
        != semantic_sha256
    ):
        raise ValueError(f"corpus semantic lineage mismatch: {case_id}")
    fresh_result_receipt = None
    if native:
        fresh_result_receipt = _validate_result_receipt(
            receipt.get("fresh_recovery_result"),
            label=f"case {case_id} fresh recovery",
            required=expected_passed,
            recovery_required=True if expected_passed else None,
            expected_permissions=expected_permissions,
        )
        if expected_passed:
            _validate_case_oracle_receipt(
                fresh_result_receipt,
                case=case,
                label=f"case {case_id} fresh recovery",
            )
        _validate_semantic_result_projection(
            receipt.get("fresh_recovery_semantic_result"),
            raw_result_sha256=fresh_result_receipt["result_sha256"],
            invocation_profile=profile,
            accepted_baseline_failures=accepted_baseline,
        )
    elif receipt.get("fresh_recovery_result") is not None:
        raise ValueError(f"unexpected fresh recovery result receipt: {case_id}")
    elif receipt.get("fresh_recovery_semantic_result") is not None:
        raise ValueError(f"unexpected fresh recovery semantic result: {case_id}")
    _validate_terminal_projections(
        receipt.get("terminal_projections"),
        invocation_profile=profile,
        result_sha256=result_receipt["result_sha256"],
        fresh_result_sha256=(
            fresh_result_receipt["result_sha256"]
            if fresh_result_receipt is not None
            else None
        ),
        native=native,
    )
    _validate_native_compaction(
        receipt.get("native_compaction"),
        case=case,
        receipt=receipt,
        result=result_receipt,
        fresh_result=fresh_result_receipt,
        native_evidence_oracle=native_evidence_oracle,
    )
    _validate_isolation_receipt(receipt.get("filesystem_isolation"), case_id=case_id)
    if (
        not isinstance(receipt.get("exit_code"), int)
        or isinstance(receipt.get("exit_code"), bool)
        or not isinstance(elapsed, (int, float))
        or isinstance(elapsed, bool)
        or not math.isfinite(elapsed)
        or elapsed < 0
        or not isinstance(uncached, int)
        or isinstance(uncached, bool)
        or uncached < 0
    ):
        raise ValueError(f"invalid corpus evidence telemetry: {case_id}")


def _validate_corpus_summary(
    payload: dict[str, Any],
    snapshot: dict[str, Any],
    source: dict[str, Any],
    *,
    gate_authority_sha256: str,
    impact: dict[str, Any],
) -> None:
    validate_impact(impact, snapshot)
    _require_digest(
        gate_authority_sha256,
        length=64,
        label="gate authority digest",
    )
    settings = snapshot["settings"]
    cases = payload.get("cases")
    if (
        set(payload) != CORPUS_SUMMARY_FIELDS
        or payload.get("schema_version") != 1
        or payload.get("engine_generation") != "0.6"
        or payload.get("impact_token") != impact_token(snapshot, impact)
        or payload.get("gate_authority_sha256") != gate_authority_sha256
        or payload.get("arm") != "candidate"
        or payload.get("model") != settings["model"]
        or payload.get("effort") != settings["effort"]
        or payload.get("timeout_seconds") != settings["timeout_seconds"]
        or payload.get("telemetry_complete") is not True
        or not isinstance(cases, list)
    ):
        raise ValueError("invalid corpus certification evidence")
    by_id = {
        item.get("id"): item
        for item in cases
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    expected = set(impact["corpus_cases"])
    if not expected:
        raise ValueError("corpus certification evidence has no authorized scope")
    if set(by_id) != expected or len(by_id) != len(cases):
        raise ValueError("corpus certification evidence is incomplete")
    if payload.get("total") != len(expected) or payload.get("passed") != len(expected):
        raise ValueError("corpus certification evidence is not all-pass")
    for case_id in sorted(expected):
        _validate_case_identity(
            by_id[case_id],
            snapshot,
            case_id,
            case=source.get("corpus_cases", {}).get(case_id),
            native_evidence_oracle=source.get("native_evidence_oracles", {}).get(
                case_id
            ),
            semantic_sha256=snapshot["corpus"]["cases"][case_id],
            package=snapshot["package"],
            engine=source["engine"],
        )
    if (
        payload.get("uncached_input_tokens")
        != sum(item["uncached_input_tokens"] for item in cases)
        or payload.get("output_tokens")
        != sum(item["usage"]["output_tokens"] for item in cases)
        or payload.get("elapsed_seconds")
        != round(sum(item["elapsed_seconds"] for item in cases), 3)
    ):
        raise ValueError("corpus certification evidence telemetry mismatch")


def _validate_arm_identity(
    receipt: Any,
    snapshot: dict[str, Any],
    *,
    arm: str,
    expected_passed: bool,
    descriptor: dict[str, Any],
    package: dict[str, str],
    source: dict[str, Any],
) -> None:
    settings = snapshot["settings"]
    semantic_sha256 = case_semantic_sha256(
        descriptor["case"],
        shared_semantic_sha256=source["holdout_case_semantic_sha256"],
        package_semantic_sha256=package["semantic_sha256"],
        model=settings["model"],
        effort=settings["effort"],
        timeout=settings["timeout_seconds"],
        arm=arm,
    )
    _validate_case_identity(
        receipt,
        snapshot,
        descriptor["case"]["id"],
        case=descriptor["case"],
        native_evidence_oracle=source.get("native_evidence_oracles", {}).get(
            descriptor["case"]["id"]
        ),
        expected_passed=expected_passed,
        semantic_sha256=semantic_sha256,
        package=package,
        engine=source["engine"],
        expected_profile_arm="blinded-pair",
    )


def _validate_holdout_summary(
    payload: dict[str, Any],
    snapshot: dict[str, Any],
    *,
    run_pair_ids: list[str],
    run_sha256: str,
    public_package: dict[str, str],
    source: dict[str, Any],
) -> None:
    receipts = payload.get("pair_receipts")
    if (
        set(payload) != HOLDOUT_SUMMARY_FIELDS
        or payload.get("schema_version") != 1
        or payload.get("engine_generation") != "0.6"
        or payload.get("run_receipt_sha256") != run_sha256
        or not isinstance(receipts, list)
        or payload.get("pairs_run") != len(receipts)
        or not receipts
    ):
        raise ValueError("invalid holdout summary certification evidence")
    pair_ids = [item.get("id") for item in receipts if isinstance(item, dict)]
    if pair_ids != run_pair_ids[: len(pair_ids)] or len(pair_ids) != len(receipts):
        raise ValueError("holdout summary pair ordering mismatch")
    outcomes = [item.get("outcome") for item in receipts]
    if not all(isinstance(outcome, str) for outcome in outcomes):
        raise ValueError("invalid holdout outcome evidence")
    terminal_action = adaptive_next(outcomes)
    if (
        payload.get("adaptive_history") != outcomes
        or payload.get("adaptive_terminal_action") != terminal_action
    ):
        raise ValueError("holdout adaptive evidence mismatch")
    if terminal_action not in {"stop", "reject"}:
        raise ValueError("holdout adaptive evidence is not terminal")
    for receipt in receipts:
        if not isinstance(receipt, dict) or set(receipt) != PAIR_RECEIPT_FIELDS:
            raise ValueError("invalid holdout pair evidence")
        descriptor = source["holdout_descriptors"].get(receipt["id"])
        if (
            receipt.get("schema_version") != 1
            or receipt.get("engine_generation") != "0.6"
            or not isinstance(descriptor, dict)
            or receipt.get("case_id") != descriptor["case"]["id"]
            or receipt.get("case_sha256") != descriptor["case_sha256"]
            or receipt.get("outside_diff_boundary")
            is not descriptor["outside_diff_boundary"]
            or receipt.get("oracle_kind") != descriptor["oracle_kind"]
        ):
            raise ValueError("holdout pair does not match source descriptor")
        for field in (
            "mapping_commitment_file_sha256",
            "pre_reveal_decision_file_sha256",
            "mapping_reveal_file_sha256",
            "pre_reveal_decision_sha256",
            "mapping_commitment_sha256",
        ):
            _require_digest(
                receipt.get(field), length=64, label=f"holdout pair {field}"
            )
        arms = receipt.get("arms") if isinstance(receipt, dict) else None
        if not isinstance(arms, dict) or set(arms) != {"candidate", "public-0.4.0"}:
            raise ValueError("invalid holdout arm evidence")
        candidate_passed = (
            arms["candidate"].get("passed")
            if isinstance(arms["candidate"], dict)
            else None
        )
        public_passed = (
            arms["public-0.4.0"].get("passed")
            if isinstance(arms["public-0.4.0"], dict)
            else None
        )
        if not isinstance(candidate_passed, bool) or not isinstance(
            public_passed, bool
        ):
            raise ValueError("invalid holdout arm outcome evidence")
        derived_outcome = (
            "regression"
            if not candidate_passed
            else "better"
            if not public_passed
            else "equal"
        )
        if receipt.get("outcome") != derived_outcome:
            raise ValueError("holdout outcome mismatch")
        _validate_arm_identity(
            arms["candidate"],
            snapshot,
            arm="candidate",
            expected_passed=candidate_passed,
            descriptor=descriptor,
            package=snapshot["package"],
            source=source,
        )
        _validate_arm_identity(
            arms["public-0.4.0"],
            snapshot,
            arm="public-0.4.0",
            expected_passed=public_passed,
            descriptor=descriptor,
            package=public_package,
            source=source,
        )
        expected_metrics = {
            arm: {
                "uncached_input_tokens": arms[arm]["uncached_input_tokens"],
                "output_tokens": arms[arm]["usage"]["output_tokens"],
                "elapsed_seconds": arms[arm]["elapsed_seconds"],
            }
            for arm in ("candidate", "public-0.4.0")
        }
        if receipt.get("metrics") != expected_metrics:
            raise ValueError("holdout arm metrics mismatch")
    quality = aggregate_quality(outcomes)
    aggregate = {
        arm: sum_metrics([receipt["metrics"][arm] for receipt in receipts])
        for arm in ("candidate", "public-0.4.0")
    }
    expected_gate = cost_gate(
        aggregate["candidate"], aggregate["public-0.4.0"], quality=quality
    )
    if (
        payload.get("cost_gate") != expected_gate
        or not expected_gate["release_permitted"]
    ):
        raise ValueError("holdout cost/quality evidence does not permit certification")


def validate_ledger(ledger: dict[str, Any], *, repo: Path | None = None) -> None:
    del repo
    if (
        set(ledger) != LEDGER_FIELDS
        or ledger.get("schema_version") != 1
        or ledger.get("engine_generation") != "0.6"
    ):
        raise ValueError("invalid certification ledger envelope")
    if ledger.get("state") != "refresh_required":
        raise ValueError("invalid certification ledger state")
    snapshot = ledger.get("snapshot")
    if not isinstance(snapshot, dict):
        raise ValueError("invalid certification snapshot")
    validate_snapshot(snapshot)
    pending = ledger.get("pending")
    if not isinstance(pending, dict) or set(pending) != PENDING_FIELDS:
        raise ValueError("invalid pending refresh envelope")
    gates = pending["gates"]
    if gates != list(PENDING_GATES):
        raise ValueError("invalid generation-6 pending gates")
    for field in ("corpus_cases", "holdout_pairs"):
        value = pending[field]
        if (
            not isinstance(value, list)
            or not all(isinstance(item, str) and item for item in value)
            or value != sorted(set(value))
        ):
            raise ValueError(f"invalid pending scope: {field}")
    if pending["corpus_cases"] != sorted(snapshot["corpus"]["cases"]):
        raise ValueError("generation-6 genesis requires all corpus cases")
    if pending["holdout_pairs"] != sorted(snapshot["holdout"]["pairs"]):
        raise ValueError("generation-6 genesis requires all holdout pairs")
    if len(pending["corpus_cases"]) != 17 or len(pending["holdout_pairs"]) != 3:
        raise ValueError("invalid generation-6 genesis cardinality")
    authorities = ledger.get("authorities")
    if (
        not isinstance(authorities, dict)
        or set(authorities) != AUTHORITY_SLOTS
        or any(value is not None for value in authorities.values())
    ):
        raise ValueError("generation-6 genesis authorities must be null")
    if ledger.get("calibration_history") != []:
        raise ValueError("generation-6 genesis calibration history must be empty")
    if ledger.get("accepted_evidence") != []:
        raise ValueError("generation-6 genesis accepted evidence must be empty")
    if ledger.get("receipt_head") is not None:
        raise ValueError("generation-6 genesis receipt head must be null")
    if ledger.get("certification") is not None:
        raise ValueError("refresh-required ledger cannot carry certification")


def load_ledger(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("certification ledger must be an object")
    repo = path.resolve().parents[2]
    validate_ledger(value, repo=repo)
    return value


def ledger_sha256(ledger: dict[str, Any], *, repo: Path | None = None) -> str:
    validate_ledger(ledger, repo=repo)
    return canonical_sha256(ledger)
