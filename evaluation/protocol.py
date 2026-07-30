from __future__ import annotations

import hashlib
import json
import re
from typing import Any


_RESULT_FIELDS = frozenset(
    {
        "blocker_classifications",
        "decision",
        "evidence",
        "execplan_condition",
        "finding_classifications",
        "open_gates",
        "protocol_may_complete",
        "protocol_may_product_write",
        "protocol_review_mode",
        "qualifies",
        "reason",
        "recovery_state",
    }
)
_FINDING_FIELDS = frozenset({"anchors", "domain", "identity", "state"})
_BLOCKER_FIELDS = frozenset({"blocking", "class", "identity", "reason"})
_RECOVERY_FIELDS = frozenset(
    {
        "baseline_revision",
        "baseline_tree",
        "current_revision",
        "current_tree",
        "live_agents",
        "marker_ids",
        "milestone_phase",
        "next_action",
        "pending_gates",
        "tests",
        "worktree",
        "writer",
    }
)
_TEST_FIELDS = frozenset({"accepted_failures", "failed", "marker_ids", "passed"})
_AGENT_FIELDS = frozenset({"id", "receipt_reproduced", "status"})
_DECISIONS = frozenset({"continue", "stop_for_user", "complete", "incomplete"})
_EXECPLAN_CONDITIONS = frozenset(
    {"not_required", "missing", "usable", "needs_amendment"}
)
_REVIEW_MODES = frozenset({"none", "exact_final"})
_FINDING_DOMAINS = frozenset(
    {"secret", "baseline_failure", "receipt", "other"}
)
_FINDING_STATES = frozenset(
    {"baseline_unchanged", "resolved", "candidate_new", "unknown"}
)
_BLOCKER_CLASSES = frozenset(
    {
        "exhaustive_claim",
        "frozen_acceptance",
        "original_goal",
        "production_condition",
        "safety_data_integrity",
    }
)
_GATES = (
    "user_selection",
    "contract_freeze",
    "red_oracle",
    "product_edit",
    "checks",
    "reconciliation",
    "candidate_freeze",
    "exact_final_review",
    "release",
)
_MILESTONE_PHASES = frozenset(
    {
        "working",
        "candidate_frozen",
        "exact_final",
        "closed",
    }
)
_RECOVERY_ACTIONS = frozenset(
    {
        "ask_user",
        "create_execplan",
        "complete_boundary_union",
        "create_contract_freeze_revision",
        "observe_red",
        "implement",
        "run_checks",
        "reconciliation",
        "freeze_candidate",
        "exact_final_review",
        "release",
        "none",
        "unknown",
    }
)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_GIT_OBJECT = re.compile(r"^[0-9a-f]{40}$")
_PROJECTION_FIELDS = frozenset(
    {
        "accepted_baseline_sha256",
        "blocker_identities_sha256",
        "decision",
        "execplan_condition",
        "finding_identities_sha256",
        "invocation_profile_sha256",
        "open_gates",
        "protocol_may_complete",
        "protocol_may_product_write",
        "protocol_review_mode",
        "qualifies",
        "raw_result_sha256",
        "recovery_state_sha256",
        "schema_generation",
    }
)


def _canonical_sha256(value: Any) -> str:
    data = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
    return hashlib.sha256(data).hexdigest()


def _object(value: Any, fields: frozenset[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or any(type(key) is not str for key in value):
        raise ValueError(f"{label} must be an object")
    actual = set(value)
    if actual != fields:
        raise ValueError(
            f"{label} fields mismatch: "
            f"missing={sorted(fields - actual)}, unknown={sorted(actual - fields)}"
        )
    return value


def _enum(value: Any, allowed: frozenset[str], label: str) -> str:
    if type(value) is not str or value not in allowed:
        raise ValueError(f"{label} is invalid")
    return value


def _text(value: Any, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{label} must be nonblank exact text")
    return value


def _bool(value: Any, label: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{label} must be boolean")
    return value


def _nonnegative_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be a nonnegative integer")
    return value


def _exact_texts(
    value: Any,
    *,
    label: str,
    allowed: frozenset[str] | None = None,
) -> tuple[str, ...]:
    if type(value) is not list:
        raise ValueError(f"{label} must be an array")
    result = tuple(_text(item, label) for item in value)
    if len(result) != len(set(result)):
        singular = label[:-1] if label.endswith("s") else label
        raise ValueError(f"duplicate {singular} identity")
    if allowed is not None and any(item not in allowed for item in result):
        raise ValueError(f"{label} contains an invalid value")
    return result


def _validate_recovery(value: Any) -> str | None:
    if value is None:
        return None
    recovery = _object(value, _RECOVERY_FIELDS, "recovery_state")
    for field in (
        "baseline_revision",
        "baseline_tree",
        "current_revision",
        "current_tree",
    ):
        item = recovery[field]
        if type(item) is not str or _GIT_OBJECT.fullmatch(item) is None:
            raise ValueError(f"recovery_state.{field} is invalid")
    if recovery["writer"] != "Root":
        raise ValueError("recovery_state.writer must be Root")
    if recovery["worktree"] not in {"clean", "dirty"}:
        raise ValueError("recovery_state.worktree is invalid")
    _enum(
        recovery["milestone_phase"],
        _MILESTONE_PHASES,
        "recovery_state.milestone_phase",
    )
    _enum(recovery["next_action"], _RECOVERY_ACTIONS, "recovery_state.next_action")
    _exact_texts(
        recovery["pending_gates"],
        label="recovery pending gates",
        allowed=frozenset(_GATES),
    )
    _exact_texts(recovery["marker_ids"], label="recovery marker ids")
    tests = _object(recovery["tests"], _TEST_FIELDS, "recovery_state.tests")
    _nonnegative_int(tests["passed"], "recovery_state.tests.passed")
    failed = _nonnegative_int(tests["failed"], "recovery_state.tests.failed")
    accepted = _nonnegative_int(
        tests["accepted_failures"],
        "recovery_state.tests.accepted_failures",
    )
    if failed != accepted:
        raise ValueError("recovery_state has unaccepted test failures")
    _exact_texts(tests["marker_ids"], label="recovery test marker ids")
    if type(recovery["live_agents"]) is not list:
        raise ValueError("recovery_state.live_agents must be an array")
    agent_ids: set[str] = set()
    for raw_agent in recovery["live_agents"]:
        agent = _object(raw_agent, _AGENT_FIELDS, "recovery_state.live_agent")
        identity = _text(agent["id"], "recovery_state.live_agent.id")
        if identity in agent_ids:
            raise ValueError("duplicate recovery live agent identity")
        agent_ids.add(identity)
        if agent["status"] != "terminal" or agent["receipt_reproduced"] is not True:
            raise ValueError("recovery_state live agent is not terminal and reproduced")
    return _canonical_sha256(recovery)


def _expected_assertions(
    result: dict[str, Any],
    *,
    accepted_baseline_failures: tuple[str, ...],
) -> tuple[str, bool, str, bool]:
    accepted = set(accepted_baseline_failures)
    unresolved_findings = any(
        item["state"] in {"candidate_new", "unknown"}
        or (
            item["state"] == "baseline_unchanged"
            and item["identity"] not in accepted
        )
        for item in result["finding_classifications"]
    )
    blocking = any(item["blocking"] for item in result["blocker_classifications"])
    unresolved = unresolved_findings or blocking
    execplan_blocked = result["execplan_condition"] in {"missing", "needs_amendment"}
    gates = set(result["open_gates"])
    selected = next((gate for gate in _GATES if gate in gates), None)

    if selected == "user_selection":
        return ("stop_for_user", False, "none", False)
    if selected == "reconciliation":
        return ("incomplete", False, "none", False)
    if selected is not None:
        if execplan_blocked and selected in {
            "product_edit",
            "candidate_freeze",
            "exact_final_review",
        }:
            return ("incomplete", False, "none", False)
        if unresolved and selected in {
            "candidate_freeze",
            "exact_final_review",
        }:
            return ("continue", True, "none", False)
        return {
            "contract_freeze": ("continue", False, "none", False),
            "red_oracle": ("continue", False, "none", False),
            "product_edit": ("continue", True, "none", False),
            "checks": ("continue", False, "none", False),
            "candidate_freeze": ("continue", False, "none", False),
            "exact_final_review": ("continue", False, "exact_final", False),
            "release": ("continue", False, "none", False),
        }[selected]
    if execplan_blocked:
        return ("incomplete", False, "none", False)
    if unresolved:
        return ("continue", True, "none", False)
    return ("complete", False, "none", True)


def validate_result(value: Any) -> dict[str, Any]:
    result = _object(value, _RESULT_FIELDS, "result")
    _enum(result["decision"], _DECISIONS, "result.decision")
    _bool(result["qualifies"], "result.qualifies")
    _enum(
        result["execplan_condition"],
        _EXECPLAN_CONDITIONS,
        "result.execplan_condition",
    )
    _bool(
        result["protocol_may_product_write"],
        "result.protocol_may_product_write",
    )
    _enum(
        result["protocol_review_mode"],
        _REVIEW_MODES,
        "result.protocol_review_mode",
    )
    _bool(result["protocol_may_complete"], "result.protocol_may_complete")
    _text(result["reason"], "result.reason")
    _exact_texts(result["evidence"], label="evidence")
    _exact_texts(
        result["open_gates"],
        label="open gates",
        allowed=frozenset(_GATES),
    )

    if type(result["finding_classifications"]) is not list:
        raise ValueError("finding_classifications must be an array")
    finding_ids: set[str] = set()
    findings: dict[str, dict[str, Any]] = {}
    for raw_finding in result["finding_classifications"]:
        finding = _object(raw_finding, _FINDING_FIELDS, "finding")
        identity = _text(finding["identity"], "finding.identity")
        if identity in finding_ids:
            raise ValueError("duplicate finding identity in finding identities")
        finding_ids.add(identity)
        _enum(finding["domain"], _FINDING_DOMAINS, "finding.domain")
        _enum(finding["state"], _FINDING_STATES, "finding.state")
        _exact_texts(finding["anchors"], label="finding anchors")
        findings[identity] = finding

    if type(result["blocker_classifications"]) is not list:
        raise ValueError("blocker_classifications must be an array")
    blocker_ids: set[str] = set()
    for raw_blocker in result["blocker_classifications"]:
        blocker = _object(raw_blocker, _BLOCKER_FIELDS, "blocker")
        identity = _text(blocker["identity"], "blocker.identity")
        if identity in blocker_ids:
            raise ValueError("duplicate blocker identity in blocker identities")
        blocker_ids.add(identity)
        _enum(blocker["class"], _BLOCKER_CLASSES, "blocker.class")
        _bool(blocker["blocking"], "blocker.blocking")
        _text(blocker["reason"], "blocker.reason")
        finding = findings.get(identity)
        if finding is None:
            raise ValueError("blocker identity lacks an exact finding")
        if blocker["blocking"] and finding["state"] == "resolved":
            raise ValueError("contradictory resolved finding and blocking blocker")

    _validate_recovery(result["recovery_state"])
    return result


def project_result(
    value: Any,
    *,
    invocation_profile_sha256: str,
    accepted_baseline_failures: list[str],
) -> dict[str, Any]:
    result = validate_result(value)
    if (
        type(invocation_profile_sha256) is not str
        or _SHA256.fullmatch(invocation_profile_sha256) is None
    ):
        raise ValueError("invocation profile digest is invalid")
    accepted = _exact_texts(
        accepted_baseline_failures,
        label="accepted baseline identities",
    )
    if list(accepted) != sorted(accepted):
        raise ValueError("accepted baseline identities must be sorted")
    assertions = (
        result["decision"],
        result["protocol_may_product_write"],
        result["protocol_review_mode"],
        result["protocol_may_complete"],
    )
    if assertions != _expected_assertions(
        result,
        accepted_baseline_failures=accepted,
    ):
        raise ValueError("raw protocol assertions diverge from direct result state")
    return {
        "schema_generation": 6,
        "raw_result_sha256": _canonical_sha256(result),
        "invocation_profile_sha256": invocation_profile_sha256,
        "accepted_baseline_sha256": _canonical_sha256(list(accepted)),
        "decision": result["decision"],
        "qualifies": result["qualifies"],
        "execplan_condition": result["execplan_condition"],
        "protocol_may_product_write": result["protocol_may_product_write"],
        "protocol_review_mode": result["protocol_review_mode"],
        "protocol_may_complete": result["protocol_may_complete"],
        "finding_identities_sha256": _canonical_sha256(
            [item["identity"] for item in result["finding_classifications"]]
        ),
        "blocker_identities_sha256": _canonical_sha256(
            [item["identity"] for item in result["blocker_classifications"]]
        ),
        "open_gates": list(result["open_gates"]),
        "recovery_state_sha256": _validate_recovery(result["recovery_state"]),
    }


def replay_projection(
    value: Any,
    *,
    raw_result: Any,
    invocation_profile_sha256: str,
    accepted_baseline_failures: list[str],
) -> dict[str, Any]:
    projection = _object(value, _PROJECTION_FIELDS, "protocol projection")
    expected = project_result(
        raw_result,
        invocation_profile_sha256=invocation_profile_sha256,
        accepted_baseline_failures=accepted_baseline_failures,
    )
    if projection != expected:
        raise ValueError("protocol projection does not replay")
    return projection


__all__ = ("project_result", "replay_projection", "validate_result")
